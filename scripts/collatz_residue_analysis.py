#!/usr/bin/env python3
"""
collatzResidue の数学的分析

定義:
  collatzResidue(0) = 0
  collatzResidue(n+1) = if n % 2 == 0 then 4 * collatzResidue(n) + 1
                         else collatzResidue(n)

核心等式（仮説）: 3 * collatzResidue(k) + 1 = 4^{ceil(k/2)} もしくは類似の形

まず定義から数値を計算し、パターンを調べる。
"""

def collatz_residue(n):
    """再帰定義に従って計算"""
    if n == 0:
        return 0
    # c(n+1) = if n%2==0 then 4*c(n)+1 else c(n)
    # つまり c(k) は c(k-1) から計算: c(k) = if (k-1)%2==0 then 4*c(k-1)+1 else c(k-1)
    prev = collatz_residue(n - 1)
    if (n - 1) % 2 == 0:  # n-1 が偶数 → n は奇数
        return 4 * prev + 1
    else:  # n-1 が奇数 → n は偶数
        return prev

print("=== collatzResidue の値 ===")
for k in range(20):
    c = collatz_residue(k)
    print(f"c({k:2d}) = {c:10d}   (n-1={k-1} mod 2 = {(k-1)%2 if k>0 else 'N/A'})")

print("\n=== 3*c(k)+1 の値 ===")
for k in range(20):
    c = collatz_residue(k)
    val = 3 * c + 1
    # 4^m の候補を調べる
    if val > 0:
        import math
        log4 = math.log(val) / math.log(4)
        is_pow4 = abs(log4 - round(log4)) < 1e-10
    else:
        log4 = 0
        is_pow4 = (val == 1)
    print(f"3*c({k:2d})+1 = {val:10d}   4^? = {log4:.4f}   is_pow4={is_pow4}")

print("\n=== パターン解析 ===")
# c(k) の変化を調べる
# n=0: c(0)=0
# n=1: (n-1)=0 は偶数 → c(1) = 4*0+1 = 1
# n=2: (n-1)=1 は奇数 → c(2) = c(1) = 1
# n=3: (n-1)=2 は偶数 → c(3) = 4*1+1 = 5
# n=4: (n-1)=3 は奇数 → c(4) = c(3) = 5
# n=5: (n-1)=4 は偶数 → c(5) = 4*5+1 = 21

# つまり偶数ステップでのみ値が変化し、奇数ステップでは不変
# 実質的に c(2m+1) = 4*c(2m) + 1, c(2m+2) = c(2m+1)
# → c(2m+1) = c(2m+2) = 4*c(2m) + 1 = 4*c(2m-1) + 1

# 偶数インデックスのみ追跡: a(m) = c(2m)
# a(0) = c(0) = 0
# a(m+1) = c(2m+2) = c(2m+1) = 4*c(2m)+1 = 4*a(m)+1
# → a(m) = 4^m * a(0) + sum_{i=0}^{m-1} 4^i = (4^m - 1)/3

print("偶数インデックス a(m) = c(2m):")
for m in range(10):
    am = collatz_residue(2*m)
    formula = (4**m - 1) // 3
    print(f"  a({m}) = c({2*m}) = {am},  (4^{m}-1)/3 = {formula},  match = {am == formula}")

print("\n奇数インデックス b(m) = c(2m+1):")
for m in range(10):
    bm = collatz_residue(2*m+1)
    formula = (4**(m+1) - 1) // 3
    print(f"  b({m}) = c({2*m+1}) = {bm},  (4^{m+1}-1)/3 = {formula},  match = {bm == formula}")

print("\n=== 核心等式の検証 ===")
print("仮説 A: 3*c(k)+1 = 4^{ceil((k+1)/2)}")
for k in range(20):
    c = collatz_residue(k)
    lhs = 3 * c + 1
    # ceil((k+1)/2) = (k+2)//2
    exp = (k + 2) // 2
    rhs = 4 ** exp
    match = (lhs == rhs)
    print(f"  k={k:2d}: 3*c(k)+1 = {lhs:10d}, 4^{exp} = {rhs:10d}, match = {match}")

print("\n=== ascentConst との関係 ===")
def ascent_const(k):
    if k == 0:
        return 0
    return 3 * ascent_const(k-1) + 2**(k-1)

print("ascentConst と collatzResidue の比較:")
for k in range(15):
    ac = ascent_const(k)
    cr = collatz_residue(k)
    print(f"  k={k:2d}: ascentConst(k)={ac:8d}, collatzResidue(k)={cr:8d}, ratio={ac/cr if cr>0 else 'N/A'}")

print("\n=== 閉じた形の検証 ===")
print("c(2m) = (4^m - 1)/3 の検証:")
for m in range(12):
    actual = collatz_residue(2*m)
    expected = (4**m - 1) // 3
    assert actual == expected, f"Failed at m={m}"
print("  全て一致!")

print("\nc(2m+1) = (4^(m+1) - 1)/3 の検証:")
for m in range(12):
    actual = collatz_residue(2*m+1)
    expected = (4**(m+1) - 1) // 3
    assert actual == expected, f"Failed at m={m}"
print("  全て一致!")

print("\n核心等式の正確な形:")
print("  c(2m) = (4^m - 1)/3")
print("  c(2m+1) = (4^(m+1) - 1)/3")
print("  統一形: c(k) = (4^{ceil(k/2)} - 1)/3  ただし ceil は天井関数")
print("  等価: 3*c(k) + 1 = 4^{ceil(k/2)}  ただし k>=1 のとき")
print("  もしくは: 3*c(k) + 1 = 4^{(k+1)/2}  (切り上げ除算)")

print("\n=== 帰納法の構造 ===")
print("偶数→奇数ステップ:")
print("  c(2m+1) = 4*c(2m) + 1")
print("  3*c(2m+1) + 1 = 3*(4*c(2m)+1) + 1 = 12*c(2m) + 4 = 4*(3*c(2m)+1)")
print("  IH: 3*c(2m)+1 = 4^m ならば 3*c(2m+1)+1 = 4*4^m = 4^(m+1)")
print("")
print("奇数→偶数ステップ:")
print("  c(2m+2) = c(2m+1)")
print("  3*c(2m+2)+1 = 3*c(2m+1)+1 = 4^(m+1)")
print("  即座に成立")

