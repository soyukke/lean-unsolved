#!/usr/bin/env python3
"""
collatzResidue: Step 1-3 設計
- Step 1: collatzResidue の再帰定義と数値テーブル
- Step 2: rfl による数値検証（小さな値）の確認
- Step 3: 核心等式 3 * collatzResidue(k) + 1 = 4^{ceil(k/2)} の帰納法設計

定義:
  collatzResidue(0) = 0
  collatzResidue(n+1) = if n is even then 4 * collatzResidue(n) + 1
                         else collatzResidue(n)

注意: "n%2=0" は引数 n の偶奇 (collatzResidue(n+1) の定義で n を見る)
"""

import math

def collatzResidue(n):
    """collatzResidue の再帰定義"""
    if n == 0:
        return 0
    # collatzResidue(n) = f(n-1, collatzResidue(n-1))
    prev = collatzResidue(n - 1)
    m = n - 1  # 引数 n+1 のときの n に対応
    if m % 2 == 0:  # n-1 が偶数 <=> n が奇数
        return 4 * prev + 1
    else:           # n-1 が奇数 <=> n が偶数
        return prev

print("=" * 60)
print("Step 1: collatzResidue テーブル")
print("=" * 60)
print(f"{'k':>4} {'c(k)':>12} {'3*c(k)+1':>12} {'4^ceil(k/2)':>12} {'一致?':>6}")
print("-" * 50)

for k in range(16):
    ck = collatzResidue(k)
    lhs = 3 * ck + 1
    ck_half = math.ceil(k / 2)
    rhs = 4 ** ck_half
    match = "OK" if lhs == rhs else "NG"
    print(f"{k:>4} {ck:>12} {lhs:>12} {rhs:>12} {match:>6}")

print()
print("=" * 60)
print("Step 2: 再帰展開の確認")
print("=" * 60)

# 各ステップの再帰展開を明示
print("c(0) = 0")
print(f"c(1) = 4*c(0)+1 = 4*0+1 = 1        [n=0 is even]")
print(f"c(2) = c(1) = 1                      [n=1 is odd]")
print(f"c(3) = 4*c(2)+1 = 4*1+1 = 5         [n=2 is even]")
print(f"c(4) = c(3) = 5                      [n=3 is odd]")
print(f"c(5) = 4*c(4)+1 = 4*5+1 = 21        [n=4 is even]")
print(f"c(6) = c(5) = 21                     [n=5 is odd]")
print(f"c(7) = 4*c(6)+1 = 4*21+1 = 85       [n=6 is even]")
print(f"c(8) = c(7) = 85                     [n=7 is odd]")

print()
# c(k) の閉じた形を探す
print("=" * 60)
print("閉じた形の分析")
print("=" * 60)

# パターン: c(2j+1) = c(2j) = (4^j - 1) / 3
# c(0) = 0 = (4^0 - 1)/3 = 0  ... OK
# c(1) = 1 = (4^1 - 1)/3 = 1  ... OK
# c(2) = 1 = (4^1 - 1)/3 = 1  ... OK
# c(3) = 5 = (4^2 - 1)/3 = 5  ... OK
# c(4) = 5 = (4^2 - 1)/3 = 5  ... OK
# c(5) = 21 = (4^3 - 1)/3 = 21 ... OK

print(f"{'k':>4} {'c(k)':>12} {'(4^ceil(k/2)-1)/3':>20} {'一致?':>6}")
print("-" * 50)

for k in range(16):
    ck = collatzResidue(k)
    ck_half = math.ceil(k / 2)
    closed = (4 ** ck_half - 1) // 3
    match = "OK" if ck == closed else "NG"
    print(f"{k:>4} {ck:>12} {closed:>20} {match:>6}")

print()
print("核心等式の検証:")
print("  3 * c(k) + 1 = 4^{ceil(k/2)}")
print("  <=> 3 * (4^{ceil(k/2)} - 1)/3 + 1 = 4^{ceil(k/2)}")
print("  <=> 4^{ceil(k/2)} - 1 + 1 = 4^{ceil(k/2)}")
print("  <=> 4^{ceil(k/2)} = 4^{ceil(k/2)}  ... 自明")
print()
print("つまり c(k) = (4^{ceil(k/2)} - 1) / 3 が成り立つなら核心等式は自明。")
print("帰納法で c(k) = (4^{ceil(k/2)} - 1) / 3 を直接示すのが正攻法。")

print()
print("=" * 60)
print("Step 3: 帰納法の設計")
print("=" * 60)

# 帰納法: c(k) と ascentConst k の関係
# ascentConst k = 3^k - 2^k
# c(k) = (4^{ceil(k/2)} - 1) / 3 = (2^{2*ceil(k/2)} - 1) / 3

# 二つのアプローチ:
# (A) 直接帰納法: 3*c(k)+1 = 4^{ceil(k/2)} を帰納法で証明
# (B) 閉じた形: c(k) = (4^{ceil(k/2)} - 1)/3 を示し、核心等式を導出

print("アプローチ(A): 直接帰納法で 3*c(k)+1 = 4^{ceil(k/2)}")
print()
print("Base: k=0 => 3*0+1 = 1 = 4^0 ... OK")
print()
print("Step (偶数の場合): k+1 で n=k が偶数 (k=2j)")
print("  c(2j+1) = 4*c(2j) + 1")
print("  3*c(2j+1) + 1 = 3*(4*c(2j)+1) + 1 = 12*c(2j) + 4 = 4*(3*c(2j)+1)")
print("  IH: 3*c(2j)+1 = 4^{ceil(2j/2)} = 4^j")
print("  => 3*c(2j+1)+1 = 4*4^j = 4^{j+1} = 4^{ceil((2j+1)/2)}")
print("  ceil((2j+1)/2) = j+1 ... OK!")
print()
print("Step (奇数の場合): k+1 で n=k が奇数 (k=2j+1)")
print("  c(2j+2) = c(2j+1)")
print("  3*c(2j+2) + 1 = 3*c(2j+1) + 1")
print("  IH: 3*c(2j+1)+1 = 4^{ceil((2j+1)/2)} = 4^{j+1}")
print("  => 3*c(2j+2)+1 = 4^{j+1} = 4^{ceil((2j+2)/2)}")
print("  ceil((2j+2)/2) = j+1 ... OK!")
print()

# 帰納法の検証
print("帰納法の数値検証:")
for k in range(12):
    ck = collatzResidue(k)
    lhs = 3 * ck + 1
    ck_half = math.ceil(k / 2)
    rhs = 4 ** ck_half

    if k > 0:
        prev = collatzResidue(k - 1)
        n = k - 1
        if n % 2 == 0:
            # c(k) = 4*c(k-1)+1
            assert ck == 4 * prev + 1
            # 3*c(k)+1 = 3*(4*c(k-1)+1)+1 = 12*c(k-1)+4 = 4*(3*c(k-1)+1)
            prev_eq = 3 * prev + 1
            assert lhs == 4 * prev_eq, f"k={k}: {lhs} != 4 * {prev_eq}"
        else:
            # c(k) = c(k-1)
            assert ck == prev

    assert lhs == rhs, f"k={k}: {lhs} != {rhs}"
    print(f"  k={k:>2}: 3*c({k})+1 = {lhs:>8} = 4^{ck_half} = {rhs:>8} OK")

print()
print("=" * 60)
print("Lean 4 コード設計")
print("=" * 60)

print("""
-- Step 1: 定義
/-- コラッツ剰余関数:
    c(0) = 0
    c(n+1) = if n is even then 4 * c(n) + 1 else c(n) -/
def collatzResidue : Nat -> Nat
  | 0 => 0
  | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
              else collatzResidue n

-- Step 2: 数値検証 (native_decide or rfl)
example : collatzResidue 0 = 0 := rfl
example : collatzResidue 1 = 1 := rfl
example : collatzResidue 2 = 1 := rfl
example : collatzResidue 3 = 5 := rfl
example : collatzResidue 4 = 5 := rfl
example : collatzResidue 5 = 21 := rfl
example : collatzResidue 6 = 21 := rfl
example : collatzResidue 7 = 85 := rfl
example : collatzResidue 8 = 85 := rfl

-- Step 3: 核心等式の帰納法
-- 補助: ceil(k/2) を Lean の Nat.div で書く
-- Nat.ceil(k/2) は自然数では (k + 1) / 2

-- 核心等式: 3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2)
""")

# (k+1)/2 (自然数の切り上げ除算) の検証
print("ceil(k/2) vs (k+1)/2 (自然数除算):")
for k in range(12):
    ceil_val = math.ceil(k / 2)
    nat_div = (k + 1) // 2
    print(f"  k={k}: ceil(k/2)={ceil_val}, (k+1)/2={nat_div}, 一致={ceil_val == nat_div}")

print()
print("=" * 60)
print("Lean帰納法のケース分析")
print("=" * 60)

# Lean では k に対する帰納法がシンプル
# k = 0: 3 * 0 + 1 = 1 = 4^0 = 1  OK
# k+1:
#   Case n % 2 = 0 (n = k):
#     collatzResidue (k+1) = 4 * collatzResidue k + 1
#     3 * (4 * c(k) + 1) + 1 = 12 * c(k) + 4 = 4 * (3 * c(k) + 1) = 4 * 4^((k+1)/2)
#     Need: 4^((k+2)/2) = 4 * 4^((k+1)/2)
#     k even => (k+1)/2 = k/2, (k+2)/2 = k/2 + 1  so 4^(k/2+1) = 4 * 4^(k/2) OK
#
#   Case n % 2 = 1 (n = k):
#     collatzResidue (k+1) = collatzResidue k
#     3 * c(k) + 1 = 4^((k+1)/2)  (IH)
#     Need: 4^((k+2)/2) = 4^((k+1)/2)
#     k odd => (k+1)/2 = (k+1)/2, (k+2)/2 = (k+1)/2  (since k+2 = 2j+3, (2j+3)/2 = j+1 = (2j+2)/2)
#     Wait, let me check: k=1 (odd), (k+1)/2=1, (k+2)/2=3/2=1 (Nat div)  OK

print("k偶奇と (k+1)/2, (k+2)/2 の関係:")
for k in range(12):
    k1_div2 = (k + 1) // 2
    k2_div2 = (k + 2) // 2
    parity = "even" if k % 2 == 0 else "odd"
    if k % 2 == 0:
        # k even: (k+2)/2 = (k+1)/2 + 1 ?
        # k=0: (2)/2=1, (1)/2=0, diff=1 YES
        # k=2: (4)/2=2, (3)/2=1, diff=1 YES
        relation = f"(k+2)/2 = {k2_div2} = (k+1)/2 + 1 = {k1_div2 + 1}"
        check = k2_div2 == k1_div2 + 1
    else:
        # k odd: (k+2)/2 = (k+1)/2
        # k=1: (3)/2=1, (2)/2=1, same YES
        # k=3: (5)/2=2, (4)/2=2, same YES
        relation = f"(k+2)/2 = {k2_div2} = (k+1)/2 = {k1_div2}"
        check = k2_div2 == k1_div2
    print(f"  k={k:>2} ({parity:>4}): {relation}  {'OK' if check else 'NG'}")

print()
print("=" * 60)
print("完全な Lean 4 コード設計案")
print("=" * 60)

lean_code = r"""
import Mathlib

/-!
# collatzResidue: 再帰定義と核心等式

## 定義
collatzResidue(0) = 0
collatzResidue(n+1) = if n % 2 = 0 then 4 * collatzResidue(n) + 1
                       else collatzResidue(n)

## 核心等式
3 * collatzResidue(k) + 1 = 4 ^ ((k + 1) / 2)

## 閉じた形
collatzResidue(k) = (4 ^ ((k + 1) / 2) - 1) / 3

## ascentConst との関係
ascentConst k = 3^k - 2^k は "連続上昇"公式の定数。
collatzResidue k は "偶奇交互パターン" の累積残差。
両者は異なる再帰構造だが、コラッツ予想の解析に関連する。
-/

/-! ## Step 1: 定義 -/

/-- コラッツ剰余関数 -/
def collatzResidue : Nat -> Nat
  | 0 => 0
  | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
              else collatzResidue n

/-! ## Step 2: 数値検証 -/

example : collatzResidue 0 = 0 := rfl
example : collatzResidue 1 = 1 := rfl
example : collatzResidue 2 = 1 := rfl
example : collatzResidue 3 = 5 := rfl
example : collatzResidue 4 = 5 := rfl
example : collatzResidue 5 = 21 := rfl
example : collatzResidue 6 = 21 := rfl
example : collatzResidue 7 = 85 := rfl
example : collatzResidue 8 = 85 := rfl

/-! ## Step 2.5: 展開補題 -/

theorem collatzResidue_zero : collatzResidue 0 = 0 := rfl

theorem collatzResidue_succ_even (n : Nat) (h : n % 2 = 0) :
    collatzResidue (n + 1) = 4 * collatzResidue n + 1 := by
  simp [collatzResidue, h]

theorem collatzResidue_succ_odd (n : Nat) (h : n % 2 = 1) :
    collatzResidue (n + 1) = collatzResidue n := by
  simp [collatzResidue]
  omega

/-! ## Step 3: 核心等式 -/

/-- 核心等式: 3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2)

帰納法:
- Base: k = 0 => 3 * 0 + 1 = 1 = 4^0 ... trivial
- Step k -> k+1:
  - k % 2 = 0:
    c(k+1) = 4 * c(k) + 1
    3 * (4*c(k)+1) + 1 = 12*c(k) + 4 = 4 * (3*c(k)+1) = 4 * 4^((k+1)/2)
    Need: 4^((k+2)/2) = 4 * 4^((k+1)/2)
    k even => (k+2)/2 = (k+1)/2 + 1, so 4^((k+1)/2+1) = 4 * 4^((k+1)/2)  OK
  - k % 2 = 1:
    c(k+1) = c(k)
    3 * c(k) + 1 = 4^((k+1)/2) (IH)
    Need: 4^((k+2)/2) = 4^((k+1)/2)
    k odd => (k+2)/2 = (k+1)/2 (since k+2 is odd => truncation same)  OK
-/
theorem collatzResidue_core_eq (k : Nat) :
    3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2) := by
  induction k with
  | zero => simp [collatzResidue]
  | succ n ih =>
    by_cases hn : n % 2 = 0
    · -- n even: c(n+1) = 4 * c(n) + 1
      rw [collatzResidue_succ_even n hn]
      -- Goal: 3 * (4 * collatzResidue n + 1) + 1 = 4 ^ ((n + 2) / 2)
      -- ih: 3 * collatzResidue n + 1 = 4 ^ ((n + 1) / 2)
      -- LHS = 12 * c(n) + 4 = 4 * (3 * c(n) + 1) = 4 * 4^((n+1)/2)
      -- n even: (n+2)/2 = (n+1)/2 + 1 (since n=2j => (2j+2)/2=j+1, (2j+1)/2=j)
      have h_exp : (n + 2) / 2 = (n + 1) / 2 + 1 := by omega
      rw [h_exp, Nat.pow_succ]
      linarith
    · -- n odd: c(n+1) = c(n)
      have hn_odd : n % 2 = 1 := by omega
      rw [collatzResidue_succ_odd n hn_odd]
      -- Goal: 3 * collatzResidue n + 1 = 4 ^ ((n + 2) / 2)
      -- ih: 3 * collatzResidue n + 1 = 4 ^ ((n + 1) / 2)
      -- n odd: (n+2)/2 = (n+1)/2 (since n=2j+1 => (2j+3)/2=j+1, (2j+2)/2=j+1)
      have h_exp : (n + 2) / 2 = (n + 1) / 2 := by omega
      rw [h_exp]
      exact ih

/-! ## 系: 閉じた形 -/

/-- collatzResidue k = (4 ^ ((k + 1) / 2) - 1) / 3 -/
theorem collatzResidue_closed (k : Nat) :
    collatzResidue k = (4 ^ ((k + 1) / 2) - 1) / 3 := by
  have h := collatzResidue_core_eq k
  -- h: 3 * c(k) + 1 = 4^((k+1)/2)
  -- => c(k) = (4^((k+1)/2) - 1) / 3
  -- Need 3 | 4^m - 1 for all m (since 4 ≡ 1 mod 3)
  have h_mod3 : 4 ^ ((k + 1) / 2) % 3 = 1 := by
    have : 4 % 3 = 1 := by norm_num
    rw [Nat.pow_mod]
    simp [this]
  omega
"""

print(lean_code)

print()
print("=" * 60)
print("ascentConst との関係分析")
print("=" * 60)

# ascentConst k = 3^k - 2^k
def ascentConst(k):
    return 3**k - 2**k

print(f"{'k':>4} {'c(k)':>12} {'ascentConst(k)':>16} {'比率':>12}")
print("-" * 50)
for k in range(12):
    ck = collatzResidue(k)
    ak = ascentConst(k)
    ratio = f"{ck/ak:.4f}" if ak > 0 else "N/A"
    print(f"{k:>4} {ck:>12} {ak:>16} {ratio:>12}")

print()
print("collatzResidue(k) は 4^{ceil(k/2)} 系列の累積。")
print("ascentConst(k) は 3^k - 2^k 系列。")
print("両者は直接的な比例関係にないが、")
print("コラッツ予想の異なる側面を捉えている。")

print()
print("=" * 60)
print("Lean コンパイル可能性チェック: rfl で通る値")
print("=" * 60)

# rfl で通るかどうかは、Lean の kernel reduction で計算できるか
# collatzResidue は構造的再帰なので、具体的な値では reduce できるはず
for k in range(20):
    ck = collatzResidue(k)
    print(f"  collatzResidue {k:>2} = {ck:>10}  (rfl で検証可能)")
