"""
探索193: 差分方程式 a(k+2) = 4*a(k) + 2 のLean形式化設計

mod 2^k 像サイズの差分方程式:
  - k偶: a(k+2) = 4*a(k) + 2
  - k奇: a(k+2) = 4*a(k)

閉公式:
  - k偶: a(k) = (7*2^{k-3} - 2) / 3
  - k奇: a(k) = 3 * 2^{k-3}

目標: 閉公式から差分方程式を直接代数的に導出し、Lean形式化の青写真を設計する。
"""

from fractions import Fraction

# =============================================
# Part 1: 閉公式の検証 (k=3..21)
# =============================================
print("=" * 60)
print("Part 1: 閉公式の数値検証")
print("=" * 60)

def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)}"""
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def image_size_mod2k(k):
    """mod 2^k での Syracuse 写像の像サイズ（奇数->奇数）"""
    mod = 2**k
    odds = [n for n in range(1, mod, 2)]
    images = set()
    for n in odds:
        images.add(syracuse(n) % mod)
    return len(images)

def closed_form_even(k):
    """k偶数のときの閉公式: (7*2^{k-3} - 2) / 3"""
    assert k >= 4 and k % 2 == 0
    return (7 * 2**(k-3) - 2) // 3

def closed_form_odd(k):
    """k奇数のときの閉公式: 3 * 2^{k-3}"""
    assert k >= 3 and k % 2 == 1
    return 3 * 2**(k-3)

def closed_form(k):
    if k % 2 == 0:
        return closed_form_even(k)
    else:
        return closed_form_odd(k)

# 直接計算との照合
print(f"{'k':>3} {'parity':>6} {'computed':>10} {'formula':>10} {'match':>6}")
for k in range(3, 22):
    comp = image_size_mod2k(k)
    form = closed_form(k)
    match = "OK" if comp == form else "FAIL"
    parity = "odd" if k % 2 == 1 else "even"
    print(f"{k:>3} {parity:>6} {comp:>10} {form:>10} {match:>6}")

# =============================================
# Part 2: 差分方程式の代数的導出
# =============================================
print("\n" + "=" * 60)
print("Part 2: 差分方程式の代数的導出")
print("=" * 60)

# k偶数: a(k) = (7*2^{k-3} - 2) / 3
# a(k+2) = (7*2^{k-1} - 2) / 3
# 4*a(k) + 2 = 4*(7*2^{k-3} - 2)/3 + 2
#            = (28*2^{k-3} - 8)/3 + 6/3
#            = (28*2^{k-3} - 8 + 6)/3
#            = (28*2^{k-3} - 2)/3
#            = (7*4*2^{k-3} - 2)/3
#            = (7*2^{k-1} - 2)/3
#            = a(k+2)  [QED]

print("\n--- k偶数: a(k+2) = 4*a(k) + 2 ---")
print("代数的証明:")
print("  a(k) = (7*2^{k-3} - 2) / 3  [k偶, k>=4]")
print("  a(k+2) = (7*2^{k-1} - 2) / 3")
print("  4*a(k) + 2 = 4*(7*2^{k-3} - 2)/3 + 2")
print("             = (28*2^{k-3} - 8 + 6)/3")
print("             = (7*2^2 * 2^{k-3} - 2)/3")
print("             = (7*2^{k-1} - 2)/3")
print("             = a(k+2)  [QED]")

# 数値検証
print("\nk偶数の検証:")
for k in range(4, 20, 2):
    ak = closed_form_even(k)
    ak2 = closed_form_even(k+2)
    rhs = 4 * ak + 2
    print(f"  k={k}: a(k)={ak}, a(k+2)={ak2}, 4*a(k)+2={rhs}, match={ak2==rhs}")

# k奇数: a(k) = 3*2^{k-3}
# a(k+2) = 3*2^{k-1}
# 4*a(k) = 4 * 3*2^{k-3} = 3*4*2^{k-3} = 3*2^{k-1}
# = a(k+2) [QED]

print("\n--- k奇数: a(k+2) = 4*a(k) ---")
print("代数的証明:")
print("  a(k) = 3*2^{k-3}  [k奇, k>=3]")
print("  a(k+2) = 3*2^{k-1}")
print("  4*a(k) = 4 * 3*2^{k-3} = 3*2^2*2^{k-3} = 3*2^{k-1}")
print("         = a(k+2)  [QED]")

print("\nk奇数の検証:")
for k in range(3, 20, 2):
    ak = closed_form_odd(k)
    ak2 = closed_form_odd(k+2)
    rhs = 4 * ak
    print(f"  k={k}: a(k)={ak}, a(k+2)={ak2}, 4*a(k)={rhs}, match={ak2==rhs}")

# =============================================
# Part 3: Lean形式化に向けた自然数算術の整理
# =============================================
print("\n" + "=" * 60)
print("Part 3: Lean形式化の自然数算術")
print("=" * 60)

# Lean4では自然数の除算が面倒なので、除算を避ける形を検討。
#
# 方針1: 3倍して除算を避ける
#   k偶: 3*a(k) = 7*2^{k-3} - 2
#   k偶: 3*a(k+2) = 7*2^{k-1} - 2
#   3*(4*a(k)+2) = 12*a(k) + 6
#   しかし 3*a(k+2) = 12*a(k) + 6 を証明すれば
#   3*a(k+2) = 3*(4*a(k)+2) なので a(k+2)=4*a(k)+2 が従う
#
#   3*a(k+2) = 7*2^{k-1} - 2
#   12*a(k) + 6 = 12*(7*2^{k-3}-2)/3 + 6 ... 結局除算が残る
#
# 方針2: 乗法形式で定式化
#   k偶: 3*a(k) + 2 = 7*2^{k-3}
#   → a(k) を直接使わず b(k) = 3*a(k) + 2 を使う
#   b(k) = 7*2^{k-3}   (k偶)
#   b(k+2) = 7*2^{k-1} = 4*7*2^{k-3} = 4*b(k)
#   つまり b(k+2) = 4*b(k) (k偶)
#
#   元の差分方程式との関係:
#   b(k+2) = 3*a(k+2) + 2
#           = 3*(4*a(k)+2) + 2
#           = 12*a(k) + 8
#   4*b(k) = 4*(3*a(k)+2)
#          = 12*a(k) + 8
#   OK!

print("\n方針2: b(k) = 3*a(k) + 2 の乗法形式")
print("  k偶: b(k) = 7*2^{k-3}")
print("  b(k+2) = 4*b(k)  [除算なし!]")
print()

for k in range(4, 22, 2):
    ak = closed_form_even(k)
    bk = 3*ak + 2
    expected = 7 * 2**(k-3)
    print(f"  k={k}: a(k)={ak}, b(k)=3*{ak}+2={bk}, 7*2^{k-3}={expected}, match={bk==expected}")

# k奇数は除算なし: a(k) = 3*2^{k-3}
print("\nk奇数は除算不要:")
for k in range(3, 22, 2):
    ak = closed_form_odd(k)
    expected = 3 * 2**(k-3)
    print(f"  k={k}: a(k)={ak}, 3*2^{k-3}={expected}, match={ak==expected}")

# =============================================
# Part 4: 初期値と帰納法の構造
# =============================================
print("\n" + "=" * 60)
print("Part 4: 帰納法の構造")
print("=" * 60)

# k偶数列: k=4, 6, 8, 10, ...
# a(4), a(6), a(8), ...
# 初期値: a(4) = (7*2 - 2)/3 = 12/3 = 4
# 差分方程式: a(k+2) = 4*a(k) + 2
#
# k=4をインデックス0とすると j = (k-4)/2
# a(4+2j) = 4*a(4+2(j-1)) + 2 = 4*a(2+2j) + 2
#
# 別の見方: m = k-4 (m偶数, m>=0)
# a(m+4) = 4*a(m+2) + 2 (m偶数)
# a(m+4) = 4*a(m+2) (m奇数)
# ただしここでは m+4 の偶奇 = m の偶奇

# 方針: Lean では k に対する strong induction を使う
# base: k=3 (奇数), k=4 (偶数)
# step: k >= 3 に対して k+2 を k から導出

print("帰納法の基底と帰納ステップ:")
print()
print("k偶数列:")
print(f"  base: a(4) = {closed_form_even(4)}")
for k in range(4, 16, 2):
    print(f"  step: a({k+2}) = 4*a({k}) + 2 = 4*{closed_form_even(k)} + 2 = {4*closed_form_even(k)+2}")

print()
print("k奇数列:")
print(f"  base: a(3) = {closed_form_odd(3)}")
for k in range(3, 16, 2):
    print(f"  step: a({k+2}) = 4*a({k}) = 4*{closed_form_odd(k)} = {4*closed_form_odd(k)}")


# =============================================
# Part 5: Lean 4 コード設計
# =============================================
print("\n" + "=" * 60)
print("Part 5: Lean 4 コード設計")
print("=" * 60)

lean_design = """
/-!
# 差分方程式 a(k+2) = 4*a(k) + 2 の形式化

mod 2^k での Syracuse 写像の像サイズ a(k) に関する差分方程式。

## 閉公式
- k奇 (k>=3): a(k) = 3 * 2^{k-3}
- k偶 (k>=4): a(k) = (7 * 2^{k-3} - 2) / 3

## 差分方程式
- k奇: a(k+2) = 4 * a(k)
- k偶: a(k+2) = 4 * a(k) + 2

## 形式化戦略
除算回避のため乗法形式を使用:
- k偶: 3 * a(k) + 2 = 7 * 2^{k-3}  (除算不要)
- k奇: a(k) = 3 * 2^{k-3}          (除算不要)
-/

/-! ### 定義: 像サイズの閉公式 -/

/-- k奇数の像サイズ閉公式 -/
def imageSizeOdd (k : Nat) : Nat := 3 * 2 ^ k

/-- k偶数の像サイズ閉公式（乗法形式: 3*a + 2 = 7*2^m） -/
-- 実際の a(k) = (7*2^{k-3} - 2)/3 を避けて
-- b(k) := 3*a(k) + 2 = 7*2^{k-3} を定義
def imageSizeEvenTripled (k : Nat) : Nat := 7 * 2 ^ k

-- ここで注意: imageSizeOdd m = a(2m+3) = 3*2^{2m}
-- imageSizeEvenTripled m = 3*a(2m+4) + 2 = 7*2^{2m+1}
-- パラメータの対応関係を慎重に設計する必要がある

/-! ### 方針A: k>=3 に対する直接的定式化 -/

-- a(k) を直接定義（decidable な定義）
-- 問題: 自然数の除算は (7*2^{k-3} - 2) / 3 で Nat.div が必要

-- 代替: 閉公式の代わりに漸化式で定義
/-- Syracuse 像サイズ（漸化式による定義） -/
def imageSize : Nat -> Nat
  | 3 => 3        -- a(3) = 3 (k=3, 奇数)
  | 4 => 4        -- a(4) = 4 (k=4, 偶数)
  | k + 5 => if k % 2 = 0 then 4 * imageSize (k + 3) + 2  -- k+5偶 <=> k偶
             else 4 * imageSize (k + 3)                      -- k+5奇 <=> k奇

/-! ### 方針B: 偶奇を分離した定義 -/

-- j >= 0 に対して:
-- oddSize j = a(2j+3) = 3 * 2^{2j}     (j=0,1,2,...)
-- evenSize j = a(2j+4) = (7*2^{2j+1}-2)/3  (j=0,1,2,...)

/-- k奇数の像サイズ: a(2j+3) -/
def oddSize (j : Nat) : Nat := 3 * 4 ^ j

/-- k偶数の像サイズ（乗法形式）: 3*a(2j+4)+2 -/
def evenSizeTripled (j : Nat) : Nat := 7 * 2 * 4 ^ j  -- = 14 * 4^j

-- 方針Bの差分方程式:
-- oddSize (j+1) = 4 * oddSize j
-- evenSizeTripled (j+1) = 4 * evenSizeTripled j

-- これは自明! 4^{j+1} = 4 * 4^j

/-! ### 定理: 方針Bの差分方程式 -/

theorem oddSize_recurrence (j : Nat) : oddSize (j + 1) = 4 * oddSize j := by
  simp [oddSize, pow_succ]
  ring

theorem evenSizeTripled_recurrence (j : Nat) :
    evenSizeTripled (j + 1) = 4 * evenSizeTripled j := by
  simp [evenSizeTripled, pow_succ]
  ring

/-! ### 定理: 元の差分方程式との等価性 -/

-- evenSize j = (evenSizeTripled j - 2) / 3
-- a(k+2) = 4*a(k) + 2 は
-- 3*a(k+2) + 2 = 4*(3*a(k)+2) - 6 + 2 = 4*(3*a(k)+2) - 4
-- ... これは直接的ではない

-- より良い導出:
-- b(k+2) = 4*b(k) where b(k) = 3*a(k)+2
-- b(k+2) = 3*a(k+2)+2 = 3*(4*a(k)+2)+2 = 12*a(k)+8
-- 4*b(k) = 4*(3*a(k)+2) = 12*a(k)+8  [一致!]

/-- 3*a(k+2)+2 = 4*(3*a(k)+2) は a(k+2)=4*a(k)+2 と同値 -/
theorem recurrence_equiv (ak ak2 : Nat) :
    3 * ak2 + 2 = 4 * (3 * ak + 2) ↔ ak2 = 4 * ak + 2 := by
  omega

/-! ### 定理: 閉公式の直接的等式 -/

-- 方針C: Lean で (7*2^n - 2) を 3 で割れることを証明
-- 7*2^n ≡ 2 (mod 3) は n >= 0 で常に成立 (7≡1, 2^n≡2^n, 1*2^n mod 3 は 2,1,2,1,...)
-- 実は 7*2^n - 2 ≡ 1*2^n - 2 ≡ 2^n - 2 (mod 3)
-- n=0: 7-2=5 ≡ 2 mod 3  [3で割れない]
-- n=1: 14-2=12 ≡ 0 mod 3 [OK]
-- n=2: 28-2=26 ≡ 2 mod 3 [NG]
-- n=3: 56-2=54 ≡ 0 mod 3 [OK]
-- n奇数のときのみ 3 | (7*2^n - 2)

-- k偶数 (k>=4) なら k-3 は奇数 (k-3>=1)
-- つまり 3 | (7*2^{k-3} - 2) は k-3 が奇数のとき成立

/-- n が奇数のとき 3 | (7*2^n - 2) -/
-- 証明: n = 2m+1 とすると
-- 7*2^{2m+1} - 2 = 14*4^m - 2 = 2*(7*4^m - 1)
-- 7*4^m mod 3 = 1*1^m = 1 mod 3
-- 7*4^m - 1 ≡ 0 mod 3
-- よって 3 | (7*2^n - 2)

-- Lean での証明:
-- theorem seven_two_pow_sub_two_div3 (m : Nat) :
--     3 ∣ (7 * 2 ^ (2*m+1) - 2) := by ...

-- あるいは帰納法:
-- base: n=1: 7*2-2=12, 12/3=4 OK
-- step: 3 | (7*2^n-2) => 3 | (7*2^{n+2}-2)
-- 7*2^{n+2}-2 = 4*(7*2^n-2) + 4*2-2 = 4*(7*2^n-2) + 6
-- 3 | (7*2^n-2) かつ 3 | 6 なので 3 | (7*2^{n+2}-2)
-- ただし n は奇数ステップで n+2 も奇数

"""

print(lean_design)

# =============================================
# Part 6: 最も簡潔な Lean 形式化の設計
# =============================================
print("\n" + "=" * 60)
print("Part 6: 最終的な Lean 形式化設計")
print("=" * 60)

# 最もクリーンなアプローチ:
# j をインデックスとして使う
# a_odd(j) := a(2j+3)  [k奇数]
# a_even(j) := a(2j+4) [k偶数]

# 定理1: a_odd(j+1) = 4 * a_odd(j)
#   証明: 3*2^{2(j+1)} = 4 * 3*2^{2j} = 3*2^{2j+2}  [tautology]

# 定理2: 3*a_even(j+1) + 2 = 4*(3*a_even(j) + 2)
#   証明: evenSizeTripled の漸化式から直接

# 定理3 (系): a_even(j+1) = 4*a_even(j) + 2
#   証明: 定理2 + omega

# 実は定理3は直接 Nat で困難（引き算）。
# 代替: 3を掛けた形 3*a_even(j) + 2 = 14*4^j を使って:
# a_even(j) = (14*4^j - 2) / 3 の代わりに
# 3*a_even(j) = 14*4^j - 2 を証明

# さらにシンプルに:
# b(j) = 14*4^j とすると b(j+1) = 4*b(j)
# a_even(j) = (b(j)-2)/3
# a_even(j+1) = (4*b(j)-2)/3 = (4*b(j)-8+6)/3 = (4*(b(j)-2)+6)/3
#             = 4*(b(j)-2)/3 + 2 = 4*a_even(j) + 2
# でもこの途中で除算が出る...

# Lean での除算回避の最終策:
# imageSize を漸化式で定義し、閉公式との一致を帰納法で証明
# 漸化式: imageSize 3 = 3, imageSize 4 = 4
#          imageSize (k+2) = 4*imageSize(k) + (if k even then 2 else 0)

print("最終設計: 漸化式定義 + 閉公式の帰納法証明")
print()

# imageSize の漸化式検証
def imageSize_rec(k):
    if k == 3:
        return 3
    elif k == 4:
        return 4
    else:
        prev = imageSize_rec(k-2)
        if (k-2) % 2 == 0:  # k-2 偶数 → k 偶数
            return 4 * prev + 2
        else:  # k-2 奇数 → k 奇数
            return 4 * prev

print(f"{'k':>3} {'parity':>6} {'rec':>10} {'closed':>10} {'match':>6}")
for k in range(3, 22):
    r = imageSize_rec(k)
    c = closed_form(k)
    parity = "odd" if k % 2 == 1 else "even"
    print(f"{k:>3} {parity:>6} {r:>10} {c:>10} {'OK' if r==c else 'FAIL':>6}")


# =============================================
# Part 7: 可除性の帰納法証明の検証
# =============================================
print("\n" + "=" * 60)
print("Part 7: 3 | (7*2^{2m+1} - 2) の帰納法検証")
print("=" * 60)

# base: m=0 → 7*2^1 - 2 = 12, 12/3=4 OK
# step: 7*2^{2(m+1)+1} - 2 = 7*2^{2m+3} - 2 = 4*(7*2^{2m+1}) - 2
#      = 4*(7*2^{2m+1}-2) + 4*2-2 = 4*(7*2^{2m+1}-2) + 6
#      3 | 4*(7*2^{2m+1}-2) [by IH] and 3 | 6
#      so 3 | 7*2^{2m+3} - 2

for m in range(20):
    val = 7 * 2**(2*m+1) - 2
    div3 = val // 3
    rem = val % 3
    print(f"  m={m:>2}: 7*2^{2*m+1} - 2 = {val:>15}, /3 = {div3:>10}, mod 3 = {rem}")

# =============================================
# Part 8: 可除性の別のアプローチ - mod 3 算術
# =============================================
print("\n" + "=" * 60)
print("Part 8: mod 3 算術による可除性証明")
print("=" * 60)

# 7 ≡ 1 (mod 3)
# 2^{2m+1} ≡ 2 * 4^m ≡ 2 * 1^m ≡ 2 (mod 3)
# 7*2^{2m+1} ≡ 1*2 ≡ 2 (mod 3)
# 7*2^{2m+1} - 2 ≡ 2 - 2 ≡ 0 (mod 3) [QED]

print("7 mod 3 = 1")
print("4 mod 3 = 1")
print("2^{2m+1} = 2*4^m ≡ 2*1 = 2 (mod 3)")
print("7*2^{2m+1} ≡ 1*2 = 2 (mod 3)")
print("7*2^{2m+1} - 2 ≡ 0 (mod 3)  [QED]")
print()
print("Lean 4 での証明方針:")
print("  (7 * 2^(2*m+1) - 2) % 3 = 0")
print("  = (7 * (2 * 4^m) - 2) % 3")
print("  帰納法 on m: Nat.mod の計算規則 + omega")


# =============================================
# Part 9: 完全な Lean 形式化の擬似コード
# =============================================
print("\n" + "=" * 60)
print("Part 9: 完全な Lean 形式化の擬似コード")
print("=" * 60)

lean_final = """
-- ============================================
-- Lean 4 形式化: 差分方程式 a(k+2) = 4a(k) + 2
-- ============================================

-- 方針: 偶奇を分離し、j-indexed で定義

-- Part A: k奇数 (k = 2j+3, j >= 0)
-- 閉公式: a(2j+3) = 3 * 4^j

def oddImageSize (j : Nat) : Nat := 3 * 4 ^ j

-- 定理A1: 差分方程式 (自明)
theorem oddImageSize_recurrence (j : Nat) :
    oddImageSize (j + 1) = 4 * oddImageSize j := by
  simp [oddImageSize, pow_succ]
  ring

-- 定理A2: 初期値
theorem oddImageSize_zero : oddImageSize 0 = 3 := by
  simp [oddImageSize]

-- Part B: k偶数 (k = 2j+4, j >= 0)
-- 乗法形式: 3 * a(2j+4) + 2 = 14 * 4^j

-- 定義: 乗法形式
def evenImageSizeAux (j : Nat) : Nat := 14 * 4 ^ j

-- 定理B1: aux の漸化式 (自明)
theorem evenImageSizeAux_recurrence (j : Nat) :
    evenImageSizeAux (j + 1) = 4 * evenImageSizeAux j := by
  simp [evenImageSizeAux, pow_succ]
  ring

-- 定理B2: 3で割れること
theorem evenImageSizeAux_sub_two_div3 (j : Nat) :
    3 ∣ (evenImageSizeAux j - 2) := by
  -- 14*4^j - 2 = 2*(7*4^j - 1)
  -- 7*4^j ≡ 1*1 = 1 (mod 3)
  -- 7*4^j - 1 ≡ 0 (mod 3)
  induction j with
  | zero => simp [evenImageSizeAux]  -- 14-2=12, 3|12
  | succ n ih =>
    simp [evenImageSizeAux, pow_succ]
    -- 14*4^{n+1} - 2 = 56*4^n - 2 = 4*(14*4^n - 2) + 6
    -- 3 | (14*4^n - 2) by IH, 3 | 6
    omega  -- or: exact dvd_add (dvd_mul_of_dvd_right ih 4) (dvd_refl 3 |>.mul_right 2)

-- 定義: 実際の像サイズ
def evenImageSize (j : Nat) : Nat := (evenImageSizeAux j - 2) / 3

-- 定理B3: 差分方程式
-- 3*evenImageSize(j+1)+2 = 4*(3*evenImageSize(j)+2)
-- i.e., evenImageSizeAux(j+1) = 4*evenImageSizeAux(j)
-- これは B1 と同一!

-- 定理B4: 差分方程式(元の形)
-- evenImageSize(j+1) = 4*evenImageSize(j) + 2
theorem evenImageSize_recurrence (j : Nat) :
    evenImageSize (j + 1) = 4 * evenImageSize j + 2 := by
  -- evenImageSizeAux_recurrence から導出
  -- evenImageSizeAux (j+1) = 4 * evenImageSizeAux j
  -- (evenImageSizeAux(j+1) - 2)/3 = (4*evenImageSizeAux(j) - 2)/3
  -- = (4*(3*evenImageSize(j)+2) - 2)/3
  -- = (12*evenImageSize(j) + 6)/3
  -- = 4*evenImageSize(j) + 2
  sorry  -- omega or Nat.div 計算

-- 定理B5: 初期値
theorem evenImageSize_zero : evenImageSize 0 = 4 := by
  simp [evenImageSize, evenImageSizeAux]  -- (14-2)/3 = 12/3 = 4

-- Part C: 統合定理

-- 統合定義
def collatzImageSize (k : Nat) (hk : k >= 3) : Nat :=
  if h : k % 2 = 1 then oddImageSize ((k - 3) / 2)
  else evenImageSize ((k - 4) / 2)

-- 統合差分方程式
-- theorem collatzImageSize_recurrence (k : Nat) (hk : k >= 3) :
--     collatzImageSize (k + 2) (by omega) =
--     if k % 2 = 0 then 4 * collatzImageSize k hk + 2
--     else 4 * collatzImageSize k hk := by ...
"""

print(lean_final)

# =============================================
# Part 10: 証明の難易度評価
# =============================================
print("\n" + "=" * 60)
print("Part 10: 証明の難易度評価")
print("=" * 60)

difficulties = [
    ("oddImageSize_recurrence", "自明", "ring で完了"),
    ("evenImageSizeAux_recurrence", "自明", "ring で完了"),
    ("evenImageSizeAux_sub_two_div3", "易", "帰納法 + omega"),
    ("evenImageSize_recurrence", "中", "Nat.div の扱い、Nat.div_add, div_mul 等が必要"),
    ("evenImageSize_zero", "易", "simp + decide"),
    ("collatzImageSize_recurrence", "中", "場合分け + 前定理の適用"),
]

for name, diff, note in difficulties:
    print(f"  {name:40s} [{diff:>3}] {note}")

print("\n最大の難所: evenImageSize_recurrence")
print("  Nat.div は整除性が保証されている場合でも扱いが面倒")
print("  方策1: Nat.div_eq_of_eq_mul_left を使う")
print("  方策2: 乗法形式 (evenImageSizeAux) で全て証明し、最後に割る")
print("  方策3: Int に移して証明し、Nat に戻す")
print()
print("推奨: 方策2 - 乗法形式を一貫して使い、除算は最終ステップのみ")

# =============================================
# Part 11: evenImageSize_recurrence の詳細証明
# =============================================
print("\n" + "=" * 60)
print("Part 11: evenImageSize_recurrence の詳細証明")
print("=" * 60)

# 核心: (14*4^{j+1} - 2)/3 = 4*(14*4^j - 2)/3 + 2
# LHS = (56*4^j - 2)/3
# RHS = (4*(14*4^j - 2) + 6)/3 = (56*4^j - 8 + 6)/3 = (56*4^j - 2)/3
# LHS = RHS [QED]

# Lean での証明:
# have h1 : evenImageSizeAux (j+1) = 4 * evenImageSizeAux j := evenImageSizeAux_recurrence j
# have h2 : 3 ∣ (evenImageSizeAux j - 2) := evenImageSizeAux_sub_two_div3 j
# have h3 : evenImageSizeAux j ≥ 2 := by simp [evenImageSizeAux]; omega (14*4^j >= 14 >= 2)
# -- evenImageSize (j+1) = (evenImageSizeAux(j+1) - 2)/3
# --                      = (4*evenImageSizeAux(j) - 2)/3
# -- 4*evenImageSize(j) + 2 = 4*(evenImageSizeAux(j)-2)/3 + 2
# --                        = (4*(evenImageSizeAux(j)-2) + 6)/3
# --                        = (4*evenImageSizeAux(j) - 8 + 6)/3
# --                        = (4*evenImageSizeAux(j) - 2)/3
#
# Key lemma: for a, b : Nat, 3 | (a - b) => (4*a - b)/3 = (4*(a-b) + 3*b)/3 = (4*(a-b))/3 + b
# Actually simpler:
#   (4*a - 2)/3 = (4*(a-2) + 6)/3 = (4*(a-2))/3 + 2
# If 3 | (a-2) then (4*(a-2))/3 = 4*((a-2)/3)
# So (4*a-2)/3 = 4*((a-2)/3) + 2 = 4*evenImageSize(j) + 2

print("証明の核心等式:")
print("  (4*A - 2)/3 = 4*((A-2)/3) + 2  where A = evenImageSizeAux j, 3|(A-2)")
print()

# 検証
for j in range(10):
    A = 14 * 4**j
    lhs = (4*A - 2) // 3
    rhs = 4 * ((A-2)//3) + 2
    print(f"  j={j}: A={A}, (4A-2)/3={lhs}, 4*((A-2)/3)+2={rhs}, match={lhs==rhs}")

print()
print("Lean 補題:")
print("  lemma nat_div_aux (a : Nat) (h1 : a >= 2) (h2 : 3 ∣ (a - 2)) :")
print("      (4 * a - 2) / 3 = 4 * ((a - 2) / 3) + 2")
print("  証明: Nat.div_eq_of_eq_mul_left + algebra")
print("  あるいは: obtain ⟨c, hc⟩ := h2; omega を使う")

# =============================================
# Part 12: 補題の Lean 証明スケッチ
# =============================================
print("\n" + "=" * 60)
print("Part 12: nat_div_aux の Lean 証明スケッチ")
print("=" * 60)

# obtain ⟨c, hc⟩ := h2  -- a - 2 = 3 * c  (hc : a - 2 = 3 * c)
# have ha : a = 3 * c + 2 := by omega
# rw [ha]
# -- Goal: (4 * (3*c+2) - 2) / 3 = 4 * ((3*c+2-2)/3) + 2
# -- = (12*c + 6) / 3 = 4 * (3*c/3) + 2 = 4*c + 2
# simp
# -- (12*c+6)/3 = 4*c+2
# -- 12*c+6 = 3*(4*c+2) → Nat.div_eq ... or omega

lean_proof = """
lemma nat_div3_aux (a : Nat) (h1 : a >= 2) (h2 : 3 ∣ (a - 2)) :
    (4 * a - 2) / 3 = 4 * ((a - 2) / 3) + 2 := by
  obtain ⟨c, hc⟩ := h2
  have ha : a = 3 * c + 2 := by omega
  subst ha  -- or: rw [ha]; clear h1
  -- Goal: (4*(3*c+2) - 2)/3 = 4*((3*c+2-2)/3) + 2
  -- = (12*c+6)/3 = 4*(3*c/3) + 2
  simp [Nat.add_mul_div_left]
  -- should reduce to (12*c+6)/3 = 4*c + 2
  omega  -- or: Nat.mul_div_cancel with appropriate form
"""
print(lean_proof)

# =============================================
# Part 13: 全体像のまとめ
# =============================================
print("\n" + "=" * 60)
print("Part 13: 全体像のまとめ")
print("=" * 60)

summary = """
形式化の全体構成 (推定 60-80行):

1. oddImageSize (j : Nat) : Nat := 3 * 4^j        [1行]
2. evenImageSizeAux (j : Nat) : Nat := 14 * 4^j    [1行]
3. evenImageSize (j : Nat) : Nat := (14*4^j - 2)/3 [1行]

4. oddImageSize_recurrence: ring で完了              [3行]
5. evenImageSizeAux_recurrence: ring で完了          [3行]
6. evenImageSizeAux_ge_two: omega で完了             [3行]
7. evenImageSizeAux_sub_two_div3: 帰納法+omega      [8行]
8. nat_div3_aux: 核心補題                           [8行]
9. evenImageSize_recurrence: 組み立て               [10行]
10. 初期値検証: decide/simp                         [4行]
11. 統合定義と統合定理                              [15行]

合計: 約60行 (sorry なし)
最難関: nat_div3_aux (Nat.div の操作)
"""
print(summary)
