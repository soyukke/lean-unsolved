#!/usr/bin/env python3
"""
探索194 Part 2: root(m) の詳細分析と Lean 証明設計
"""
from collections import defaultdict

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

# ========================================
# Part A: j=1逆像の正確な条件
# ========================================
print("=" * 70)
print("Part A: j=1 逆像 n=(2m-1)/3 の正確な条件")
print("=" * 70)

# m ≡ 2 (mod 3) のとき n = (2m-1)/3 が整数
# このとき 3n+1 = 3*(2m-1)/3 + 1 = 2m-1+1 = 2m
# v2(3n+1) = v2(2m) = 1 + v2(m)
# syracuse(n) = 2m / 2^(1+v2(m)) = m / 2^v2(m)
#
# これが m に等しいためには: m / 2^v2(m) = m
# つまり v2(m) = 0 ⟺ m は奇数!
#
# したがって: m が奇数かつ m ≡ 2 (mod 3) ⟺ m ≡ 5 (mod 6)
# のとき n = (2m-1)/3 は syracuse(n) = m を満たす

print("\n【核心】j=1逆像が正しくsyracuse(n)=mとなる条件:")
print("  m 奇数 かつ m ≡ 2 (mod 3)")
print("  ⟺ m ≡ 5 (mod 6)")
print()

# 検証
print("数値検証 (m ≡ 5 mod 6):")
for m in [5, 11, 17, 23, 29, 35, 41, 47, 53, 59]:
    if m % 6 == 5:
        n = (2*m - 1) // 3
        syr_n = syracuse(n)
        print(f"  m={m}: n=(2*{m}-1)/3={n}, syracuse({n})={syr_n}, correct={syr_n==m}")

# ========================================
# Part B: j=2逆像の正確な条件
# ========================================
print("\n" + "=" * 70)
print("Part B: j=2 逆像 n=(4m-1)/3 の正確な条件")
print("=" * 70)

# m ≡ 1 (mod 3) のとき n = (4m-1)/3 が整数
# 3n+1 = 3*(4m-1)/3 + 1 = 4m-1+1 = 4m
# v2(3n+1) = v2(4m) = 2 + v2(m)
# syracuse(n) = 4m / 2^(2+v2(m)) = m / 2^v2(m)
# 
# これが m に等しいためには: v2(m) = 0 ⟺ m は奇数!
# 
# したがって: m が奇数かつ m ≡ 1 (mod 3) ⟺ m ≡ 1 (mod 6)
# のとき n = (4m-1)/3 は syracuse(n) = m を満たす

print("\n【核心】j=2逆像が正しくsyracuse(n)=mとなる条件:")
print("  m 奇数 かつ m ≡ 1 (mod 3)")
print("  ⟺ m ≡ 1 (mod 6)")
print()

print("数値検証 (m ≡ 1 mod 6):")
for m in [1, 7, 13, 19, 25, 31, 37, 43, 49, 55]:
    if m % 6 == 1:
        n = (4*m - 1) // 3
        syr_n = syracuse(n)
        print(f"  m={m}: n=(4*{m}-1)/3={n}, syracuse({n})={syr_n}, correct={syr_n==m}")

# ========================================
# Part C: n の奇数性の検証
# ========================================
print("\n" + "=" * 70)
print("Part C: 逆像 n の奇数性検証")
print("=" * 70)

print("\nm ≡ 5 (mod 6), n = (2m-1)/3:")
for m in [5, 11, 17, 23, 29]:
    n = (2*m - 1) // 3
    print(f"  m={m} (m%6={m%6}): n={n}, n%2={n%2}, n%4={n%4}")

print("\nm ≡ 1 (mod 6), n = (4m-1)/3:")
for m in [1, 7, 13, 19, 25]:
    n = (4*m - 1) // 3
    print(f"  m={m} (m%6={m%6}): n={n}, n%2={n%2}, n%4={n%4}")

# ========================================
# Part D: v2(3n+1) の値の確認
# ========================================
print("\n" + "=" * 70)
print("Part D: v2(3n+1) の値の確認")
print("=" * 70)

print("\nm ≡ 5 (mod 6), n = (2m-1)/3:")
for m in [5, 11, 17, 23, 29]:
    n = (2*m - 1) // 3
    val = 3*n + 1
    print(f"  m={m}: n={n}, 3n+1={val}=2*{m}, v2(3n+1)={v2(val)}")

print("\nm ≡ 1 (mod 6), n = (4m-1)/3:")
for m in [1, 7, 13, 19, 25]:
    n = (4*m - 1) // 3
    val = 3*n + 1
    print(f"  m={m}: n={n}, 3n+1={val}=4*{m}, v2(3n+1)={v2(val)}")

# ========================================
# Part E: 精密な Lean 証明設計
# ========================================
print("\n" + "=" * 70)
print("Part E: 精密な Lean 4 形式化設計")
print("=" * 70)

design = """
=== 精密 Lean 4 形式化設計 ===

【ファイル: Unsolved/Collatz/Fertile.lean (新規, 約80行)】

import Unsolved.Collatz.Structure

--- セクション1: 肥沃性の定義と基本性質 ---

/-- 奇数 m が「肥沃」(fertile) ⟺ Syracuse逆像を持つ ⟺ m%3 ≠ 0 -/
def syracuseFertile (m : Nat) : Prop := m % 3 ≠ 0

--- セクション2: 不肥沃性の証明 ---

/-- 3の倍数は Syracuse の像にならない(→方向) -/
theorem syracuse_image_not_div_three' (m : Nat) (hm : m ≥ 1) (hodd : m % 2 = 1)
    (n : Nat) (hn : n ≥ 1) (hodd_n : n % 2 = 1) (hsyr : syracuse n = m) :
    m % 3 ≠ 0 := by
  rw [<- hsyr]
  exact syracuse_not_div_three n hodd_n
  -- 既存の syracuse_not_div_three を利用

--- セクション3: 肥沃性の証明 (← 方向) ---

/-- ★ m ≡ 5 (mod 6) のとき (2m-1)/3 は正の奇数で syracuse((2m-1)/3) = m
    核心: 3n+1 = 3*(2m-1)/3 + 1 = 2m, v2(2m)=1 (m奇数), m/2^0=m -/
theorem syracuse_preimage_mod6_eq5 (m : Nat) (hm : m ≥ 5) (hmod : m % 6 = 5) :
    let n := (2 * m - 1) / 3
    n % 2 = 1 ∧ n ≥ 1 ∧ syracuse n = m := by
  constructor
  · -- n は奇数: m = 6k+5, n = (12k+9)/3 = 4k+3, 奇数
    omega
  constructor
  · -- n ≥ 1: m ≥ 5 → n ≥ 3
    omega
  · -- syracuse n = m:
    -- 3n + 1 = 3 * (2m-1)/3 + 1 = 2m (omega で処理可能)
    -- v2(2m) = 1 (m が奇数で m%6=5 → m%2=1)
    -- syracuse n = 2m / 2^1 = m
    simp only [syracuse]
    -- ここで omega だけでは v2 の評価ができないので、
    -- v2_two_mul を使う
    have h3n1 : 3 * ((2 * m - 1) / 3) + 1 = 2 * m := by omega
    rw [h3n1]
    -- v2(2*m) = 1 + v2(m), m 奇数 → v2(m)=0 → v2(2m)=1
    have hm_odd : m % 2 = 1 := by omega
    have hm_ne : m ≠ 0 := by omega
    rw [v2_two_mul m hm_ne, v2_odd m (by omega)]
    -- 2*m / 2^1 = m
    simp
    
/-- ★ m ≡ 1 (mod 6) のとき (4m-1)/3 は正の奇数で syracuse((4m-1)/3) = m
    核心: 3n+1 = 3*(4m-1)/3 + 1 = 4m, v2(4m)=2 (m奇数), m/2^0=m -/
theorem syracuse_preimage_mod6_eq1 (m : Nat) (hm : m ≥ 1) (hmod : m % 6 = 1) :
    let n := (4 * m - 1) / 3
    n % 2 = 1 ∧ n ≥ 1 ∧ syracuse n = m := by
  constructor
  · -- n は奇数: m = 6k+1, n = (24k+3)/3 = 8k+1, 奇数
    omega
  constructor
  · -- n ≥ 1
    omega
  · -- syracuse n = m:
    simp only [syracuse]
    have h3n1 : 3 * ((4 * m - 1) / 3) + 1 = 4 * m := by omega
    rw [h3n1]
    -- v2(4*m) = 2 + v2(m), m 奇数 → v2(m)=0 → v2(4m)=2
    have hm_ne : m ≠ 0 := by omega
    rw [show (4:Nat)*m = 2*(2*m) from by ring,
        v2_two_mul (2*m) (by omega),
        v2_two_mul m hm_ne,
        v2_odd m (by omega)]
    simp
    
--- セクション4: 肥沃 ⟺ 逆像存在 ---

/-- ★★ 肥沃性の同値条件 (mod 6 による6ケースsplit) -/
theorem fertile_iff (m : Nat) (hm : m ≥ 1) (hodd : m % 2 = 1) :
    (∃ n, n ≥ 1 ∧ n % 2 = 1 ∧ syracuse n = m) ↔ m % 3 ≠ 0 := by
  constructor
  · -- → 方向: 逆像存在 → 不肥沃でない
    rintro ⟨n, hn, hodd_n, hsyr⟩
    rw [<- hsyr]; exact syracuse_not_div_three n hodd_n
  · -- ← 方向: 肥沃 → 逆像構成
    intro hfertile
    -- m%6 = 1 or m%6 = 5 (m奇数かつm%3≠0)
    rcases odd_mod6_trichotomy m hodd with h1 | h3 | h5
    · -- m ≡ 1 (mod 6): n = (4m-1)/3
      exact ⟨(4*m-1)/3, by omega, by omega, 
             (syracuse_preimage_mod6_eq1 m hm h1).2.2⟩
    · -- m ≡ 3 (mod 6): 矛盾 (m%3=0)
      exfalso; apply hfertile; omega
    · -- m ≡ 5 (mod 6): n = (2m-1)/3
      exact ⟨(2*m-1)/3, by omega, by omega,
             (syracuse_preimage_mod6_eq5 m (by omega) h5).2.2⟩

--- セクション5: 肥沃率 2/3 ---

/-- 肥沃率: 奇数を mod 6 で分類すると {1,3,5} のうち {1,5} が肥沃 -/
theorem fertile_rate_two_of_three (m : Nat) (hodd : m % 2 = 1) :
    m % 6 = 1 ∨ m % 6 = 3 ∨ m % 6 = 5 := by omega
-- 3クラスのうち2つが肥沃 → 密度 2/3

=== 証明の鍵 ===
1. omega で 3n+1 = 2m (resp. 4m) の等式を処理
2. v2_two_mul + v2_odd で v2 を計算
3. simp で除算を簡約

=== 行数見積もり ===
- 定義・補助: 10行
- preimage_mod6_eq5: 15行  
- preimage_mod6_eq1: 15行
- fertile_iff: 15行
- 肥沃率関連: 10行
- 検証例: 15行
合計: 約80行

=== 依存関係 ===
- v2_two_mul (Defs.lean)
- v2_odd (Defs.lean)
- syracuse_not_div_three (Structure.lean)
- syracuse_four_mul_add_one (Structure.lean) ← 追加逆像の生成に使用可能
"""
print(design)

# ========================================
# Part F: mod18 遷移行列の3パターンの発見
# ========================================
print("\n" + "=" * 70)
print("Part F: mod 18 遷移行列のパターン解析")
print("=" * 70)

# 遷移行列を見ると、mod 6 で同じクラスの行は同じパターン
# mod18=1 ≡ 1 (mod 6) と mod18=7 ≡ 1 (mod 6) と mod18=13 ≡ 1 (mod 6) → 同じ分布
# mod18=3 ≡ 3 (mod 6) と mod18=9 ≡ 3 (mod 6) と mod18=15 ≡ 3 (mod 6) → 同じ分布
# mod18=5 ≡ 5 (mod 6) と mod18=11 ≡ 5 (mod 6) と mod18=17 ≡ 5 (mod 6) → 同じ分布

print("\nmod 6 で同じクラスの行は同じ遷移パターンを持つか?")
transition_18 = defaultdict(lambda: defaultdict(int))
count_18 = defaultdict(int)
for n in range(1, 1000001, 2):
    r_from = n % 18
    s = syracuse(n)
    r_to = s % 18
    transition_18[r_from][r_to] += 1
    count_18[r_from] += 1

odd_res = [1, 3, 5, 7, 9, 11, 13, 15, 17]
non3_res = [1, 5, 7, 11, 13, 17]

# mod 6 で分類して比較
for mod6_class in [1, 3, 5]:
    members = [r for r in odd_res if r % 6 == mod6_class]
    print(f"\nmod 6 = {mod6_class} のクラス: {members}")
    for r_from in members:
        total = count_18[r_from]
        dist = {r: transition_18[r_from][r]/total*100 for r in non3_res if transition_18[r_from][r] > 0}
        sorted_dist = sorted(dist.items(), key=lambda x: -x[1])
        desc = ", ".join(f"{r}:{p:.1f}%" for r, p in sorted_dist[:6])
        print(f"  mod18={r_from}: {desc}")

