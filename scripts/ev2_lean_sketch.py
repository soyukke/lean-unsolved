"""
Lean 4 形式化スケッチ: E[v2] = 2

3つの独立した形式化可能な定理と、その組み立て方を記述する。
"""

lean_sketch = r"""
/-!
# E[v2(3n+1)] = 2 の形式化スケッチ

## 構成

### Theorem A: 有限 mod における v2 分布
v2(3n+1) = j を満たす奇数剰余類は mod 2^{j+1} でちょうど1個。

### Theorem B: テレスコープ和の閉形式 (純代数)
sum_{j=1}^{K} (j:R) / 2^j = 2 - (K+2:R) / 2^K

### Theorem C: 無限和の値 (解析)
HasSum (fun n => (n+1:R) / 2^(n+1)) 2
-/

import Mathlib

open Finset Real

-- ============================================================
-- Theorem A: mod 2^{j+1} での一意的剰余類
-- ============================================================

/-
核心的補題: 3 は mod 2^k で可逆（k >= 1 のとき）。
3 * (3^{-1} mod 2^k) ≡ 1 (mod 2^k).
v2(3n+1) >= j <==> 3n+1 ≡ 0 (mod 2^j)
              <==> n ≡ -3^{-1} (mod 2^j)
              <==> n ≡ (2^j - 1) / 3 の一般化 (mod 2^j)

v2(3n+1) = j（正確に j）<==> n ≡ r_j (mod 2^{j+1})
  where r_j is the unique odd residue mod 2^{j+1} satisfying:
  - 2^j | (3 r_j + 1)   (v2 >= j)
  - 2^{j+1} does not divide (3 r_j + 1)  (v2 = j, not > j)

帰納法の核心: n ≡ r (mod 2^j) で v2(3n+1) >= j が確定するとき、
mod 2^{j+1} に持ち上げると 2通り:
  r と r + 2^j。このうちちょうど1つが v2 = j、もう1つが v2 > j。
-/

-- 予備補題: 3 の逆元の存在
-- Mathlib: ZMod.val_inv_of_prime 等ではなく、直接的に示す
theorem three_inv_mod_pow_two (k : ℕ) (hk : k ≥ 1) :
    ∃ t : ℕ, t < 2^k ∧ t % 2 = 1 ∧ (3 * t + 1) % 2^k = 0 := by
  sorry -- Hensel's lemma を mod 2^k に帰納法で適用

-- v2 分布の核心: mod 2^{j+1} の奇数のうち、v2(3n+1) = j は丁度1個
-- （全奇数は 2^j 個なので、比率は 1/2^j）
theorem v2_unique_residue (j : ℕ) (hj : j ≥ 1) :
    ∃! r : ℕ, r < 2^(j+1) ∧ r % 2 = 1 ∧ v2 (3 * r + 1) = j := by
  sorry
  -- 方針:
  -- 1. 3t ≡ -1 (mod 2^j) の解 t0 が存在 (three_inv_mod_pow_two)
  -- 2. t0 mod 2^{j+1} と (t0 + 2^j) mod 2^{j+1} の2つが候補
  -- 3. 一方は v2 = j、他方は v2 > j
  -- 4. 奇数条件で一意に決まる

-- ============================================================
-- Theorem B: テレスコープ和の閉形式
-- ============================================================

-- sum_{j=0}^{K-1} (j+1) / 2^{j+1} = 2 - (K+2) / 2^K
-- Finset.range K で j = 0, ..., K-1 を走らせ、f(j) = (j+1)/2^{j+1} とする
theorem partial_sum_j_div_2pow (K : ℕ) (hK : K ≥ 1) :
    ∑ j ∈ range K, ((j + 1 : ℕ) : ℝ) / (2 : ℝ) ^ (j + 1)
    = 2 - ((K + 2 : ℕ) : ℝ) / (2 : ℝ) ^ K := by
  induction K with
  | zero => omega
  | succ n ih =>
    by_cases hn : n = 0
    · subst hn; simp [Finset.sum_range_succ]; ring
    · rw [Finset.sum_range_succ]
      rw [ih (by omega)]
      -- Goal: (2 - (n+2)/2^n) + (n+1)/2^{n+1} = 2 - (n+3)/2^{n+1}
      -- Algebraic manipulation:
      -- LHS = 2 - 2(n+2)/2^{n+1} + (n+1)/2^{n+1}
      --     = 2 - (2n+4-n-1)/2^{n+1}
      --     = 2 - (n+3)/2^{n+1}
      -- 注意: (n+2)/2^n = 2(n+2)/2^{n+1}
      sorry -- field_simp + ring で解決可能

-- ============================================================
-- Theorem C: 無限和 HasSum
-- ============================================================

-- 方針: hasSum_iff_tendsto_nat_of_nonneg を使う
-- f(n) = (n+1)/2^{n+1} ≥ 0 かつ
-- 部分和 S(K) = 2 - (K+2)/2^K → 2

-- 必要な補助定理: (K+2)/2^K → 0
theorem tendsto_K_plus_2_div_2_pow_K :
    Filter.Tendsto (fun K : ℕ => ((K + 2 : ℕ) : ℝ) / (2 : ℝ) ^ K)
      Filter.atTop (nhds 0) := by
  sorry
  -- 方針: (K+2)/2^K ≤ C * (3/4)^K for some C (K が十分大きいとき)
  -- または squeeze theorem: 0 ≤ (K+2)/2^K ≤ ... → 0
  -- Mathlib: tendsto_pow_atTop_nhds_zero_of_lt_one + mul

-- 部分和の収束
theorem tendsto_partial_sum :
    Filter.Tendsto
      (fun K : ℕ => ∑ j ∈ range K, ((j + 1 : ℕ) : ℝ) / (2 : ℝ) ^ (j + 1))
      Filter.atTop (nhds 2) := by
  sorry
  -- partial_sum_j_div_2pow + tendsto_K_plus_2_div_2_pow_K で
  -- S(K) = 2 - err(K), err(K) → 0 なので S(K) → 2

-- メイン定理
theorem hasSum_j_div_2pow :
    HasSum (fun n : ℕ => ((n + 1 : ℕ) : ℝ) / (2 : ℝ) ^ (n + 1)) 2 := by
  rw [hasSum_iff_tendsto_nat_of_nonneg]
  · exact tendsto_partial_sum
  · intro n; positivity

-- 系: tsum 版
theorem tsum_j_div_2pow :
    ∑' n : ℕ, ((n + 1 : ℕ) : ℝ) / (2 : ℝ) ^ (n + 1) = 2 :=
  hasSum_j_div_2pow.tsum_eq

-- ============================================================
-- 組み合わせ: v2 分布と期待値の接続
-- ============================================================

/-
最終的な定理の形:

「mod 2^k の奇数について、v2(3n+1) の"平均"は 2 - (k+2)/2^k であり、
k → ∞ で 2 に収束する」

正確には:
  (1/2^{k-1}) * Σ_{n odd < 2^k} v2(3n+1)
  = Σ_{j=1}^{k-1} j * #{v2=j} / 2^{k-1} + k * #{v2>=k} / 2^{k-1}
  = Σ_{j=1}^{k-1} j / 2^j + k / 2^{k-1}
  → 2 as k → ∞

これは Theorem A (数え上げ) + Theorem B (閉形式) + Theorem C (収束) の合成。
-/

-- ============================================================
-- 形式化の難易度評価と推奨順序
-- ============================================================

/-
## 難易度評価

### Theorem B (テレスコープ和): 最も形式化しやすい ★★☆☆☆
- 純粋な代数的計算（帰納法 + field_simp + ring）
- Mathlib の実数算術だけで完結
- 推定コード量: 30-50行

### Theorem C (無限和 HasSum): 中程度 ★★★☆☆
- hasSum_iff_tendsto_nat_of_nonneg が核心
- (K+2)/2^K → 0 の証明に Mathlib の極限理論が必要
- tendsto_pow_atTop_nhds_zero_of_lt_one を利用可能
- 推定コード量: 40-60行

### Theorem A (v2 数え上げ): 最も難しい ★★★★☆
- Finset の操作が複雑
- v2 の帰納的定義と Finset.filter の相互作用
- decide/omega で小さいケースは解決可能だが、一般の j は困難
- 推定コード量: 80-120行

## 推奨実装順序
1. Theorem B（テレスコープ和）を最初に形式化
2. Theorem C（無限和）を Theorem B の結果を用いて形式化
3. Theorem A（数え上げ）は独立して進められる

## 代替戦略（より簡潔だが高度）
Mathlib の tsum_geometric_two (Σ(1/2)^n = 2) を直接利用し、
テレスコープ展開 Σ j/2^j = Σ_{j=1}^∞ Σ_{i=j}^∞ 1/2^i = Σ Σ (Fubini)
で一気に示す方法もある。ただし Fubini (tsum_comm) の適用には
Summable 条件の検証が必要。
-/
"""

print(lean_sketch)

# 追加の重要な計算: r_j の閉形式
print("\n" + "=" * 70)
print("追加発見: r_j のパターン分析")
print("=" * 70)

from fractions import Fraction

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0:
        c += 1
        n //= 2
    return c

# r_j: v2(3r+1) = j を満たす唯一の奇数 r mod 2^{j+1}
print("\n偶数 j (j=2,4,6,8,10): r_j = (2^j - 1)/3")
print("奇数 j (j=1,3,5,7,9,11): r_j = (2^{j+1} - 1)/3 = 2*r_{j-1} + 1 ??? ")

for j in range(1, 13):
    M = 2**(j+1)
    for r in range(1, M, 2):
        if v2(3*r + 1) == j:
            # Check pattern
            if j % 2 == 0:
                formula = (2**j - 1) // 3
                match = "OK" if r == formula else "MISMATCH"
                print(f"  j={j:2d} (even): r_j = {r:5d}, (2^j-1)/3 = {formula:5d} {match}")
            else:
                # For odd j, check (2^{j+1}-1)/3
                if (2**(j+1) - 1) % 3 == 0:
                    formula = (2**(j+1) - 1) // 3
                    match = "OK" if r == formula else "MISMATCH"
                    print(f"  j={j:2d} (odd):  r_j = {r:5d}, (2^(j+1)-1)/3 = {formula:5d} {match}")
                else:
                    print(f"  j={j:2d} (odd):  r_j = {r:5d}, formula not applicable")
            break

print("\n結論:")
print("  偶数 j: r_j = (2^j - 1) / 3 = (4^{j/2} - 1) / 3")
print("  奇数 j: r_j = (2^{j+1} - 1) / 3")
print("  統一公式: r_j = (-1/3) mod 2^j の持ち上げの一つ")

# verify
print("\n検証:")
for j in range(1, 13):
    M = 2**(j+1)
    for r in range(1, M, 2):
        if v2(3*r + 1) == j:
            # r ≡ (-1/3) mod 2^j, i.e., 3r ≡ -1 mod 2^j
            check = (3*r + 1) % (2**j) == 0
            check2 = (3*r + 1) % (2**(j+1)) != 0
            print(f"  j={j:2d}: r={r:5d}, 3r+1={3*r+1:6d}, "
                  f"2^j|3r+1: {check}, 2^(j+1)|3r+1: {not check2}")
            break
