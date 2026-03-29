#!/usr/bin/env python3
"""
collatzResidue の Lean 4 実装設計

数学的分析結果:
- c(0) = 0
- c(n+1) = if n%2=0 then 4*c(n)+1 else c(n)
- c(2m) = (4^m - 1)/3
- c(2m+1) = (4^(m+1) - 1)/3
- 核心等式（加法形式）: 3*c(k) + 1 = 4^{ceil(k/2)} (k >= 0)
  - k=0: 3*0+1 = 1 = 4^0 ✓
  - k奇数 2m+1: 3*c(2m+1)+1 = 4^(m+1) ✓
  - k偶数 2m (m>=1): 3*c(2m)+1 = 4^m ✓

Lean設計戦略:
1. 定義は自然数 -> 自然数の再帰関数
2. 除算を含む閉じた形の代わりに加法形式の等式を核心定理とする
3. 帰納法は「偶数ステップと奇数ステップの交互」で証明
"""

lean_code = r'''
import Mathlib

-- ============================================================
-- Part 1: collatzResidue の定義
-- ============================================================

/-- collatzResidue: コラッツ残余関数
    c(0) = 0
    c(n+1) = if n % 2 = 0 then 4 * c(n) + 1 else c(n)

    偶数インデックスのステップで値が4倍+1され、
    奇数インデックスのステップでは不変。
    連続上昇公式の定数項と密接に関連する。-/
def collatzResidue : ℕ → ℕ
  | 0 => 0
  | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
             else collatzResidue n

-- ============================================================
-- Part 2: 展開補題
-- ============================================================

/-- collatzResidue 0 = 0 -/
@[simp] theorem collatzResidue_zero : collatzResidue 0 = 0 := rfl

/-- 偶数ステップでの展開: c(n+1) = 4*c(n)+1 when n is even -/
theorem collatzResidue_even_step (n : ℕ) (h : n % 2 = 0) :
    collatzResidue (n + 1) = 4 * collatzResidue n + 1 := by
  simp [collatzResidue, h]

/-- 奇数ステップでの展開: c(n+1) = c(n) when n is odd -/
theorem collatzResidue_odd_step (n : ℕ) (h : n % 2 ≠ 0) :
    collatzResidue (n + 1) = collatzResidue n := by
  simp [collatzResidue, h]

-- 数値検証
example : collatzResidue 0 = 0 := rfl
example : collatzResidue 1 = 1 := rfl
example : collatzResidue 2 = 1 := rfl
example : collatzResidue 3 = 5 := rfl
example : collatzResidue 4 = 5 := rfl
example : collatzResidue 5 = 21 := rfl

-- ============================================================
-- Part 3: 偶奇分解補題
-- ============================================================

/-- c(2m+1) = 4*c(2m) + 1 (偶数→奇数ステップ)
    2m は偶数なので even_step が適用される -/
theorem collatzResidue_two_mul_succ (m : ℕ) :
    collatzResidue (2 * m + 1) = 4 * collatzResidue (2 * m) + 1 := by
  -- 2*m+1 = (2*m) + 1 で、2*m は偶数
  exact collatzResidue_even_step (2 * m) (by omega)

/-- c(2m+2) = c(2m+1) (奇数→偶数ステップ)
    2m+1 は奇数なので odd_step が適用される -/
theorem collatzResidue_two_mul_succ_succ (m : ℕ) :
    collatzResidue (2 * m + 2) = collatzResidue (2 * m + 1) := by
  -- 2*m+2 = (2*m+1) + 1 で、2*m+1 は奇数
  exact collatzResidue_odd_step (2 * m + 1) (by omega)

/-- c(2(m+1)) = c(2m+1) = 4*c(2m)+1 の組み合わせ -/
theorem collatzResidue_double_step (m : ℕ) :
    collatzResidue (2 * (m + 1)) = 4 * collatzResidue (2 * m) + 1 := by
  -- 2*(m+1) = 2*m+2
  have h1 : 2 * (m + 1) = 2 * m + 2 := by ring
  rw [h1, collatzResidue_two_mul_succ_succ, collatzResidue_two_mul_succ]

-- ============================================================
-- Part 4: 核心等式（加法形式、除算回避）
-- ============================================================

/-- 核心等式A（偶数インデックス）:
    3 * collatzResidue (2*m) + 1 = 4^m

    帰納法で証明。
    base: 3*c(0)+1 = 1 = 4^0
    step: 3*c(2*(m+1))+1 = 3*(4*c(2*m)+1)+1 = 12*c(2*m)+4
                         = 4*(3*c(2*m)+1) = 4*4^m = 4^(m+1) -/
theorem collatzResidue_even_core (m : ℕ) :
    3 * collatzResidue (2 * m) + 1 = 4 ^ m := by
  induction m with
  | zero => simp [collatzResidue]
  | succ m ih =>
    rw [collatzResidue_double_step]
    -- 目標: 3 * (4 * collatzResidue (2 * m) + 1) + 1 = 4 ^ (m + 1)
    -- ih: 3 * collatzResidue (2 * m) + 1 = 4 ^ m
    -- 左辺 = 12 * collatzResidue(2*m) + 4 = 4 * (3 * collatzResidue(2*m) + 1)
    -- = 4 * 4^m = 4^(m+1)
    have key : 3 * (4 * collatzResidue (2 * m) + 1) + 1
             = 4 * (3 * collatzResidue (2 * m) + 1) := by ring
    rw [key, ih]
    ring

/-- 核心等式B（奇数インデックス）:
    3 * collatzResidue (2*m+1) + 1 = 4^(m+1)

    c(2m+1) = 4*c(2m)+1 を使い、核心等式Aに帰着 -/
theorem collatzResidue_odd_core (m : ℕ) :
    3 * collatzResidue (2 * m + 1) + 1 = 4 ^ (m + 1) := by
  rw [collatzResidue_two_mul_succ]
  -- 目標: 3 * (4 * collatzResidue (2 * m) + 1) + 1 = 4 ^ (m + 1)
  have key : 3 * (4 * collatzResidue (2 * m) + 1) + 1
           = 4 * (3 * collatzResidue (2 * m) + 1) := by ring
  rw [key, collatzResidue_even_core]
  ring

-- ============================================================
-- Part 5: 閉じた形（系）
-- ============================================================

/-- 偶数インデックスの閉じた形: c(2m) = (4^m - 1)/3
    核心等式から自然数引き算で導出 -/
theorem collatzResidue_even_closed (m : ℕ) :
    collatzResidue (2 * m) = (4 ^ m - 1) / 3 := by
  have h := collatzResidue_even_core m
  -- h: 3 * c(2m) + 1 = 4^m
  -- → c(2m) = (4^m - 1) / 3
  -- 4^m >= 1 は明らか
  have h4 : 4 ^ m ≥ 1 := Nat.one_le_pow m 4 (by omega)
  omega

/-- 奇数インデックスの閉じた形: c(2m+1) = (4^(m+1) - 1)/3 -/
theorem collatzResidue_odd_closed (m : ℕ) :
    collatzResidue (2 * m + 1) = (4 ^ (m + 1) - 1) / 3 := by
  have h := collatzResidue_odd_core m
  have h4 : 4 ^ (m + 1) ≥ 1 := Nat.one_le_pow (m+1) 4 (by omega)
  omega

-- ============================================================
-- Part 6: ascentConst との関係
-- ============================================================

-- ascentConst k = 3^k - 2^k (既存の定理)
-- collatzResidue (2m) = (4^m - 1)/3
-- これらは異なる漸化式から同じ種類の定数を生成する

/-- collatzResidue と ascentConst の関係（m=1 の場合の数値確認）
    ascentConst(1) = 1 = collatzResidue(1) -/

-- ============================================================
-- Part 7: 連続上昇公式への応用
-- ============================================================

/-- 連続上昇 k 回後の乗法形式を collatzResidue で表現:
    偶数ステップでの定数項は collatzResidue に対応

    ascentConst の漸化式: a(k+1) = 3*a(k) + 2^k
    collatzResidue の漸化式: c(2m+1) = 4*c(2m) + 1

    関係: a(k) = sum_{i=0}^{k-1} 3^(k-1-i) * 2^i
          c(2m) = sum_{i=0}^{m-1} 4^i = (4^m-1)/3

    これらは異なる基底での幾何級数の和。-/
'''

print(lean_code)

# 証明戦略の詳細分析
print("=" * 60)
print("証明戦略の詳細分析")
print("=" * 60)

print("""
## 証明の依存関係グラフ

collatzResidue_zero (by rfl)
  |
collatzResidue_even_step (by simp)
collatzResidue_odd_step (by simp)
  |
  v
collatzResidue_two_mul_succ (even_step 適用)
collatzResidue_two_mul_succ_succ (odd_step 適用)
  |
  v
collatzResidue_double_step (上2つの組み合わせ)
  |
  v
collatzResidue_even_core (m に関する帰納法 + ring + double_step)
  |
  v
collatzResidue_odd_core (two_mul_succ + even_core + ring)
  |
  v
collatzResidue_even_closed (even_core + omega)
collatzResidue_odd_closed (odd_core + omega)

## 各証明の推定難易度

1. collatzResidue_zero: ★ (trivial, rfl)
2. collatzResidue_even_step: ★ (simp with定義展開)
3. collatzResidue_odd_step: ★ (simp with定義展開)
4. collatzResidue_two_mul_succ: ★ (even_step 直接適用)
5. collatzResidue_two_mul_succ_succ: ★ (odd_step 直接適用)
6. collatzResidue_double_step: ★★ (rewrite + 上2つの組み合わせ)
7. collatzResidue_even_core: ★★★ (帰納法 + ring + rw)
8. collatzResidue_odd_core: ★★ (rw + ring + even_core適用)
9. collatzResidue_even_closed: ★★ (omega, 但し Nat 除算注意)
10. collatzResidue_odd_closed: ★★ (omega, 同上)

## 潜在的リスク

1. simp [collatzResidue, h] が if-then-else を正しく簡約できるか
   → 代替: unfold collatzResidue; split; omega のようなパターン

2. omega が 3 * c(2m) + 1 = 4^m から c(2m) = (4^m-1)/3 を導けるか
   → omega は自然数の線形算術なので、4^m は定数ではない
   → 代替: Nat.div_eq_of_eq のような補題が必要かもしれない

3. ring が自然数上で正しく動くか
   → Nat 上の ring は問題ないはず

## Lean 4 での simp/unfold の注意点

- `if n % 2 = 0 then ... else ...` の簡約には
  仮定 `h : n % 2 = 0` または `h : n % 2 ≠ 0` が必要
- `simp [collatzResidue, h]` で展開 + 条件分岐の解決を同時に行う
- 失敗する場合は `unfold collatzResidue; simp [h]` に分ける
""")

# 閉じた形の omega 適用可能性を検証
print("\n## omega の適用可能性の詳細分析")
print("""
omega は線形算術（変数の線形結合の等式/不等式）を解く。
3 * x + 1 = y から x = (y - 1) / 3 を導くには、y が 3 で割り切れる情報が必要。

実際の状況:
  仮定: 3 * collatzResidue(2*m) + 1 = 4^m
  目標: collatzResidue(2*m) = (4^m - 1) / 3

omega が扱える形:
  3 * x + 1 = y ∧ y ≥ 1 → x = (y - 1) / 3

omega は y / 3 を直接扱えないが、
Nat.div_eq_of_eq_mul_add を使えば:
  y = 3 * q + r ∧ r < 3 → y / 3 = q

ここで y = 4^m, q = collatzResidue(2*m), r = 1 の場合は r < 3 なので不適合。
正確には 4^m - 1 = 3 * collatzResidue(2*m) なので:
  (4^m - 1) / 3 = collatzResidue(2*m) は、
  3 | (4^m - 1) と 3 * collatzResidue(2*m) = 4^m - 1 から従う。

omega が直接解けるかは微妙。代替:

theorem collatzResidue_even_closed (m : ℕ) :
    collatzResidue (2 * m) = (4 ^ m - 1) / 3 := by
  have h := collatzResidue_even_core m
  have h4 : 4 ^ m ≥ 1 := Nat.one_le_pow m 4 (by omega)
  -- 3 * c(2m) + 1 = 4^m → 3 * c(2m) = 4^m - 1
  -- → c(2m) = (4^m - 1) / 3
  -- ここで 3 | (4^m - 1) は h から自明: 4^m - 1 = 3 * c(2m)
  have h3 : 4 ^ m - 1 = 3 * collatzResidue (2 * m) := by omega
  rw [h3, Nat.mul_div_cancel_left _ (by omega : 3 > 0)]
  -- もしくは omega で直接
""")
