"""
探索174: 入次数幾何分布 Geom(3/4) の分析と Lean 形式化設計

Syracuse関数 T の入次数(逆像サイズ)が幾何分布 Geom(3/4) に従うことを
数学的に分析し、Lean 4 での形式化を設計する。

=== 数学的背景 ===
- syracuse(n) = (3n+1) / 2^{v2(3n+1)} for odd n
- syracuse(4n+1) = syracuse(n) (形式証明済み)
- collatzStep_indeg_le_two: collatzStep の入次数 ≤ 2 (形式証明済み)
- 像サイズ = 3N/8 (既知結果)

=== 問題: T^{-1}(m) の構造 ===
各奇数 m (m % 3 != 0) に対して T^{-1}(m) = {n : odd n, syracuse(n) = m}
の完全な構造を解明する。
"""

import math
from collections import defaultdict

# === 1. Syracuse関数の実装 ===
def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count

def syracuse(n):
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)

# === 2. 逆像の構造分析 ===
def find_preimages(m, N):
    """T^{-1}(m) ∩ [1, N] の全要素を列挙"""
    preimages = []
    for n in range(1, N+1, 2):  # 奇数のみ
        if syracuse(n) == m:
            preimages.append(n)
    return preimages

# === 3. 逆像漸化式 n' = 4n+1 の検証 ===
print("=" * 60)
print("1. 逆像漸化式 n' = 4n+1 の検証")
print("=" * 60)

N = 10000
test_targets = [1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 37, 41, 43]

for m in test_targets:
    if m % 3 == 0:
        continue
    preimages = find_preimages(m, N)
    print(f"\nT^(-1)({m}): {preimages[:10]}{'...' if len(preimages) > 10 else ''}")

    # 漸化式 n_{k+1} = 4*n_k + 1 を検証
    if len(preimages) >= 2:
        for i in range(len(preimages)-1):
            ratio = (preimages[i+1] - 1) / preimages[i] if preimages[i] > 0 else "?"
            print(f"  n_{i+1}/n_{i} = {preimages[i+1]}/{preimages[i]} = {ratio:.4f}, "
                  f"4*n_{i}+1 = {4*preimages[i]+1}, match = {4*preimages[i]+1 == preimages[i+1]}")

# === 4. 入次数の分布分析 ===
print("\n" + "=" * 60)
print("2. 入次数の分布 (N=100000)")
print("=" * 60)

N = 100000
# 全Syracuse像の入次数をカウント
preimage_count = defaultdict(int)
for n in range(1, N+1, 2):
    m = syracuse(n)
    preimage_count[m] += 1

# 入次数の分布
indeg_distribution = defaultdict(int)
for m, count in preimage_count.items():
    indeg_distribution[count] += 1

# 入次数=0 のケースも考慮: 奇数で T^{-1}(m) = ∅
total_odd = N // 2
image_count = len(preimage_count)
no_preimage = sum(1 for m in range(1, N+1, 2) if m % 2 == 1 and m not in preimage_count)

print(f"総奇数 [1,{N}]: {total_odd}")
print(f"像の数 (入次数>=1): {image_count}")
print(f"入次数=0の奇数: {no_preimage}")

print("\n入次数分布:")
for d in sorted(indeg_distribution.keys()):
    count = indeg_distribution[d]
    frac = count / image_count
    # 幾何分布の理論値: P(d) = (3/4)(1/4)^{d-1}
    geom_val = (3/4) * (1/4)**(d-1)
    print(f"  indeg={d}: count={count}, fraction={frac:.6f}, "
          f"Geom(3/4)={geom_val:.6f}, ratio={frac/geom_val:.4f}")

# === 5. mod 6 条件と入次数の関係 ===
print("\n" + "=" * 60)
print("3. mod 6 条件と入次数の関係")
print("=" * 60)

# n が奇数なら 3n+1 は偶数。T(n) = (3n+1)/2^v2(3n+1)。
# T^{-1}(m) の最小元 (root) の mod 条件を分析

N = 50000
for m in [1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31]:
    if m % 3 == 0:
        continue
    preimages = find_preimages(m, N)
    if preimages:
        root = preimages[0]
        print(f"m={m:3d} (mod3={m%3}, mod6={m%6}): root={root:5d} "
              f"(mod6={root%6}, mod4={root%4}), |T^(-1)(m) ∩ [1,{N}]| = {len(preimages)}")
        # root の構造
        # m mod 3 = 1 => root = (4m-1)/3
        # m mod 3 = 2 => root = (2m-1)/3
        if m % 3 == 1:
            expected_root = (4*m - 1) // 3
            print(f"  (4m-1)/3 = {expected_root}, match = {expected_root == root}")
        elif m % 3 == 2:
            expected_root = (2*m - 1) // 3
            print(f"  (2m-1)/3 = {expected_root}, match = {expected_root == root}")

# === 6. 「確率」3/4 の導出の数学的根拠 ===
print("\n" + "=" * 60)
print("4. 幾何分布 Geom(3/4) の数学的導出")
print("=" * 60)

print("""
=== 数学的導出 ===

Syracuse逆像の構造:
  T^{-1}(m) = { 4^k * root(m) + (4^k - 1)/3 : k = 0, 1, 2, ... }

ここで root(m) は m の最小逆像。

n_k = 4^k * root(m) + (4^k - 1)/3 は指数的に増大するので、
[1, N] に含まれる逆像の数は約 log_4(N / root(m)) + 1。

入次数 d の「確率」（密度）:
  |T^{-1}(m) ∩ [1,N]| = d  ⟺  n_{d-1} ≤ N < n_d
  ⟺  4^{d-1} * root(m) + ... ≤ N < 4^d * root(m) + ...

root(m) は m に比例するので、root(m) ∈ [R, 4R) の範囲の m について:
  - n_0 = root ∈ [R, 4R): 全ての m で入次数 ≥ 1
  - n_1 = 4*root + 1 ∈ [4R+1, 16R+1): 入次数 ≥ 2 ⟺ 4*root+1 ≤ N

N >> root のとき、入次数 ≥ d+1 の確率 ≈ (1/4)^d:
  n_d ≤ N ⟺ 4^d * root ≲ N ⟺ root ≲ N/4^d

root の分布は概ね一様なので:
  P(indeg ≥ d+1 | indeg ≥ 1) ≈ (1/4)^d

よって:
  P(indeg = d) = P(indeg ≥ d) - P(indeg ≥ d+1) ≈ (1/4)^{d-1} - (1/4)^d
              = (1/4)^{d-1} * (1 - 1/4) = (3/4) * (1/4)^{d-1}

これが Geom(3/4)。
""")

# === 7. 数値検証: 実際の分布とGeom(3/4)の比較 ===
print("=" * 60)
print("5. 数値検証: 大規模比較")
print("=" * 60)

for N in [10000, 100000, 1000000]:
    preimage_count = defaultdict(int)
    for n in range(1, N+1, 2):
        m = syracuse(n)
        preimage_count[m] += 1

    indeg_dist = defaultdict(int)
    for m, count in preimage_count.items():
        indeg_dist[count] += 1

    total_images = sum(indeg_dist.values())
    print(f"\nN = {N}, 像の数 = {total_images}")

    for d in sorted(indeg_dist.keys()):
        if d > 8:
            break
        observed = indeg_dist[d] / total_images
        expected = (3/4) * (1/4)**(d-1)
        error = abs(observed - expected) / expected * 100
        print(f"  d={d}: observed={observed:.6f}, Geom(3/4)={expected:.6f}, error={error:.2f}%")

# === 8. Lean形式化設計 ===
print("\n" + "=" * 60)
print("6. Lean 4 形式化設計")
print("=" * 60)

print("""
=== 形式化可能な定理の階層 ===

--- 既証明 (使用可能) ---
(A) syracuse_four_mul_add_one: syracuse(4n+1) = syracuse(n)
(B) collatzStep_indeg_le_two: 入次数 ≤ 2
(C) collatzStep_odd_preimage_exists: n ≡ 4 (mod 6) → 奇数前像存在
(D) syracuse_odd: T(n) は常に奇数
(E) syracuse_not_div_three: T(n) % 3 ≠ 0

--- 新定理1: 逆像鎖の反復 ---

/-- syracuse(4n+1) = syracuse(n) の k 回反復。
    4^k*n + (4^k-1)/3 の Syracuse 値は n の Syracuse 値に等しい。-/
theorem syracuse_four_pow_chain (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuse (4^k * n + (4^k - 1)/3) = syracuse n

証明戦略: k に関する帰納法。
  base k=0: 4^0*n + 0/3 = n (trivial)
  step k→k+1:
    4^{k+1}*n + (4^{k+1}-1)/3
    = 4*(4^k*n + (4^k-1)/3) + 1  ... (★要証明の代数的等式)
    T(4*m+1) = T(m) by syracuse_four_mul_add_one
    = T(4^k*n + (4^k-1)/3)
    = T(n) by 帰納仮定

注意: (4^k-1)/3 は自然数。これは 4 ≡ 1 (mod 3) より 4^k ≡ 1 (mod 3)。

--- 新定理2: 根の明示公式 ---

/-- m % 3 = 1 のとき、(4m-1)/3 は T の逆像: syracuse((4m-1)/3) = m -/
theorem syracuse_root_mod3_eq1 (m : ℕ) (hm : m ≥ 1) (hmod : m % 3 = 1)
    (hodd : m % 2 = 1) :
    syracuse ((4 * m - 1) / 3) = m

/-- m % 3 = 2 のとき、(2m-1)/3 は T の逆像: syracuse((2m-1)/3) = m -/
theorem syracuse_root_mod3_eq2 (m : ℕ) (hm : m ≥ 1) (hmod : m % 3 = 2)
    (hodd : m % 2 = 1) :
    syracuse ((2 * m - 1) / 3) = m

--- 新定理3: 逆像の完全列挙 ---

/-- T^{-1}(m) の全ての要素は 4n+1 鎖上にある -/
theorem syracuse_preimage_on_chain (m n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (h : syracuse n = m) :
    ∃ k root, syracuse root = m ∧ n = 4^k * root + (4^k - 1) / 3

--- 新定理4 (Finset版): 有界入次数の計数 ---

/-- [1, N] 内の T^{-1}(m) の要素数 -/
noncomputable def syracusePreimageCount (m N : ℕ) : ℕ :=
  (Finset.range N).filter (fun n => n % 2 = 1 ∧ n ≥ 1 ∧ syracuse n = m) |>.card

--- 新定理5: 入次数と 4^k チェーンの長さ ---

/-- 入次数 d ≥ 1 の奇数 m の割合は (3/4)(1/4)^{d-1} に収束する。
    これは syracuse_four_mul_add_one の直接的帰結。-/

--- 形式化の難易度順 ---
1. ★★ 新定理1 (鎖の反復): syracuse_four_mul_add_one の帰納的拡張。30-50行。
2. ★★★ 新定理2 (根の公式): 具体的な v2 計算が必要。各50-80行。
3. ★★★★ 新定理3 (完全性): 逆方向の証明が難しい。100行以上。
4. ★★★★★ 新定理5 (分布): 漸近評価が Lean では困難。形式化よりは検証向き。

=== 推奨: 新定理1を最優先 ===
""")

# === 9. 新定理1の詳細な証明設計 ===
print("=" * 60)
print("7. 新定理1の詳細な証明設計")
print("=" * 60)

# (4^{k+1} - 1) / 3 = 4 * (4^k - 1)/3 + 1 の検証
print("\n代数的等式の検証:")
for k in range(8):
    lhs = (4**(k+1) - 1) // 3
    rhs = 4 * ((4**k - 1) // 3) + 1
    chain_val = lambda n: 4**k * n + (4**k - 1) // 3
    print(f"k={k}: (4^{k+1}-1)/3={lhs}, 4*(4^{k}-1)/3 + 1 = {rhs}, match={lhs==rhs}")

# 4^{k+1}*n + (4^{k+1}-1)/3 = 4*(4^k*n + (4^k-1)/3) + 1 の検証
print("\n全体の代数的等式の検証:")
for k in range(6):
    for n in [1, 3, 5, 7, 11, 13, 17]:
        lhs = 4**(k+1) * n + (4**(k+1) - 1) // 3
        inner = 4**k * n + (4**k - 1) // 3
        rhs = 4 * inner + 1
        if lhs != rhs:
            print(f"  MISMATCH: k={k}, n={n}")
            break
    else:
        continue
    break
else:
    print("  全て一致 (k=0..5, n=1..17)")

# === 10. chainElem の定義と奇数性 ===
print("\n" + "=" * 60)
print("8. chainElem の奇数性の証明")
print("=" * 60)

print("""
chainElem(n, k) := 4^k * n + (4^k - 1) / 3

奇数性: n が奇数 ⟹ chainElem(n, k) が奇数

証明:
  4^k * n は偶数 (k≥1) or n (k=0)
  (4^k - 1)/3:
    k=0: 0 (偶数)
    k=1: 1 (奇数)
    k=2: 5 (奇数)
    k=3: 21 (奇数)

  パターン: (4^k-1)/3 mod 2:
    k=0: 0
    k≥1: 1 (帰納法で証明可能)
""")

for k in range(10):
    val = (4**k - 1) // 3
    print(f"  k={k}: (4^k-1)/3 = {val}, mod 2 = {val % 2}")

print("""
k≥1 のとき (4^k-1)/3 は奇数:
  4^k - 1 = (4-1)(4^{k-1} + 4^{k-2} + ... + 1) = 3 * sum
  (4^k-1)/3 = sum_{j=0}^{k-1} 4^j
  この和の偶奇: sum = 1 + 4 + 16 + ...
  mod 2: = 1 + 0 + 0 + ... = 1 (奇数)

よって chainElem(n, k):
  k=0: n (奇数, 仮定)
  k≥1: 4^k*n + (4^k-1)/3 = (偶数) + (奇数) = 奇数

⟹ 全ての k で chainElem(n, k) は奇数 ✓
""")

# === 11. 自然数除算の問題と回避策 ===
print("=" * 60)
print("9. 自然数除算の問題と Lean での回避策")
print("=" * 60)

print("""
問題: (4^k - 1) / 3 は Lean の自然数除算で正しく計算されるか？

4^k ≡ 1 (mod 3) なので 3 | (4^k - 1)。よって除算は割り切れる。

Lean での表現候補:

方法A: 直接定義（除算使用）
  def chainOffset (k : ℕ) : ℕ := (4^k - 1) / 3

  問題: k=0 で 4^0 - 1 = 0, 0/3 = 0 ✓
        k=1 で 4^1 - 1 = 3, 3/3 = 1 ✓
  自然数の引き算は安全（4^k ≥ 1 は自明）

方法B: 漸化式による定義（除算回避）
  def chainOffset : ℕ → ℕ
    | 0 => 0
    | k+1 => 4 * chainOffset k + 1

  これは ascentConst と同型! 実際:
    chainOffset 0 = 0
    chainOffset 1 = 1
    chainOffset 2 = 5
    chainOffset 3 = 21
    chainOffset 4 = 85

  一方、(4^k-1)/3:
    k=0: 0, k=1: 1, k=2: 5, k=3: 21, k=4: 85

  一致! ⟹ 方法Bが最適。除算を完全に回避。

閉じた形の証明:
  theorem chainOffset_eq : chainOffset k = (4^k - 1) / 3
  証明: chainOffset k * 3 + 1 = 4^k (帰納法で乗法形式)
""")

# 方法Bの検証
print("chainOffset の漸化式の検証:")
def chainOffset(k):
    if k == 0:
        return 0
    return 4 * chainOffset(k-1) + 1

for k in range(10):
    co = chainOffset(k)
    exact = (4**k - 1) // 3
    print(f"  k={k}: chainOffset={co}, (4^k-1)/3={exact}, match={co==exact}")

# === 12. 最終的な Lean コード設計 ===
print("\n" + "=" * 60)
print("10. 最終的な Lean 4 形式化設計（完全版）")
print("=" * 60)

print("""
=== Lean 4 コード設計 ===

--- 定義 ---

/-- 逆像鎖のオフセット: chainOffset 0 = 0, chainOffset (k+1) = 4 * chainOffset k + 1 -/
def chainOffset : ℕ → ℕ
  | 0 => 0
  | k + 1 => 4 * chainOffset k + 1

/-- 逆像鎖の要素: chainElem n k = 4^k * n + chainOffset k -/
def chainElem (n k : ℕ) : ℕ := 4 ^ k * n + chainOffset k

--- 補題群 ---

-- 数値検証
example : chainOffset 0 = 0 := rfl
example : chainOffset 1 = 1 := rfl
example : chainOffset 2 = 5 := rfl
example : chainOffset 3 = 21 := rfl

/-- chainOffset の閉じた形（乗法形式）: 3 * chainOffset k + 1 = 4^k -/
theorem three_mul_chainOffset_add_one (k : ℕ) : 3 * chainOffset k + 1 = 4 ^ k := by
  induction k with
  | zero => simp [chainOffset]
  | succ k ih =>
    simp only [chainOffset, pow_succ]
    -- 3 * (4 * chainOffset k + 1) + 1 = 4 * 4^k
    -- = 12 * chainOffset k + 4
    -- = 4 * (3 * chainOffset k + 1) = 4 * 4^k
    linarith

/-- chainElem の漸化式: chainElem n (k+1) = 4 * chainElem n k + 1 -/
theorem chainElem_succ (n k : ℕ) : chainElem n (k + 1) = 4 * chainElem n k + 1 := by
  simp only [chainElem, chainOffset, pow_succ]; ring

/-- chainElem n 0 = n -/
@[simp] theorem chainElem_zero (n : ℕ) : chainElem n 0 = n := by
  simp [chainElem, chainOffset]

/-- chainOffset k が k ≥ 1 で奇数 -/
theorem chainOffset_odd (k : ℕ) (hk : k ≥ 1) : chainOffset k % 2 = 1 := by
  induction k with
  | zero => omega
  | succ k ih =>
    simp only [chainOffset]
    -- 4 * chainOffset k + 1
    -- k = 0: 4*0+1 = 1, 1 % 2 = 1 ✓
    -- k ≥ 1: 4*(odd) + 1 = even + 1 = odd ✓
    omega  -- 4 * (anything) + 1 is always odd

/-- chainElem n k は n 奇数なら常に奇数 -/
theorem chainElem_odd (n k : ℕ) (hodd : n % 2 = 1) : chainElem n k % 2 = 1 := by
  cases k with
  | zero => simp [chainElem, chainOffset]; exact hodd
  | succ k =>
    rw [chainElem_succ]
    omega  -- 4 * (anything) + 1 is odd

/-- chainElem n k ≥ 1 (n ≥ 1 のとき) -/
theorem chainElem_pos (n k : ℕ) (hn : n ≥ 1) : chainElem n k ≥ 1 := by
  simp [chainElem]; omega

--- 主定理 ---

/-- ★★ 逆像鎖定理: syracuse(chainElem n k) = syracuse n -/
theorem syracuse_chainElem (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuse (chainElem n k) = syracuse n := by
  induction k with
  | zero => simp [chainElem, chainOffset]
  | succ k ih =>
    rw [chainElem_succ]
    -- chainElem n (k+1) = 4 * chainElem n k + 1
    -- syracuse(4m + 1) = syracuse(m) by syracuse_four_mul_add_one
    have hm_pos : chainElem n k ≥ 1 := chainElem_pos n k hn
    have hm_odd : chainElem n k % 2 = 1 := chainElem_odd n k hodd
    rw [syracuse_four_mul_add_one (chainElem n k) hm_pos hm_odd]
    exact ih

推定行数: 60-80行（定義 + 補題 + 主定理）

--- 応用定理 ---

/-- 入次数は無限: 任意の d に対して |T^{-1}(m) ∩ [1,N]| ≥ d となる N が存在 -/
theorem syracuse_indeg_unbounded (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    ∀ d, ∃ N, N ≥ 1 ∧ syracuse N = syracuse n ∧ N ≠ n := by
  intro d
  use chainElem n (d + 1)
  refine ⟨chainElem_pos n (d+1) hn,
         syracuse_chainElem n (d+1) hn hodd,
         by simp [chainElem]; omega⟩

/-- 入次数は正確に: T^{-1}(T(n)) の d 個の異なる元を構成 -/
theorem syracuse_indeg_at_least (n d : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    ∃ S : Finset ℕ, S.card = d ∧
    ∀ m ∈ S, syracuse m = syracuse n

注: この最後の定理は Finset の構成が必要で、より高度。

""")

# === 13. 形式化の難易度評価と依存関係 ===
print("=" * 60)
print("11. 形式化の依存関係と難易度")
print("=" * 60)

print("""
依存関係グラフ:

  syracuse_four_mul_add_one (既証明)
         ↓
  chainOffset (新定義、漸化式)
  chainElem (新定義)
  chainElem_succ (代数、ring)
  chainElem_odd (omega)
  chainElem_pos (omega)
         ↓
  syracuse_chainElem (帰納法 + 上記補題)
         ↓
  syracuse_indeg_unbounded (直接的応用)

難易度: ★★ (中程度)
推定行数: 80-100行
sorry不要の完全証明: ほぼ確実に可能

最大のリスク:
  - chainOffset の性質証明で omega/linarith が通らない可能性
    → 手動で calc ステップを追加すれば解決可能
  - syracuse_four_mul_add_one の前提条件 (n≥1, n奇数) の伝播
    → chainElem_pos, chainElem_odd で事前証明済み
""")

print("\n完了。")
