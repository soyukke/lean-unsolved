"""
T(n) mod 2^k の像サイズ公式: k偶数での 7/12 への収束速度の解析

既知:
  k奇数: |Im| = 3 * 2^{k-3}  => 占有率 = 3/4 (正確)
  k偶数: |Im| = (7 * 2^{k-3} - 2) / 3  => 占有率 → 7/12

このスクリプトでは:
1. k偶数の占有率の7/12への収束速度を解析
2. 補正項の構造を特定
3. k奇数 vs k偶数の振動パターンを理解
4. k→∞での一般的漸近展開
"""

from fractions import Fraction
import math

print("=" * 70)
print("Part 1: k偶数の像サイズと占有率の正確な値")
print("=" * 70)

# k偶数の像サイズ: |Im| = (7 * 2^{k-3} - 2) / 3
# 定義域サイズ: 2^{k-1} (奇数残基の数)
# 占有率 = |Im| / 2^{k-1} = (7 * 2^{k-3} - 2) / (3 * 2^{k-1})
#         = (7 * 2^{k-3} - 2) / (3 * 2^{k-1})
#         = 7 / (3 * 4) - 2 / (3 * 2^{k-1})
#         = 7/12 - 2/(3 * 2^{k-1})

print("\n占有率 = |Im| / 2^{k-1} の正確な有理数値:")
print(f"{'k':>4} {'|Im|':>12} {'2^(k-1)':>12} {'占有率(Fraction)':>25} {'占有率(float)':>15} {'7/12との差':>20}")

for k in range(4, 42, 2):
    im_size = Fraction(7 * 2**(k-3) - 2, 3)
    domain_size = Fraction(2**(k-1))
    ratio = im_size / domain_size
    diff_from_712 = ratio - Fraction(7, 12)

    if k <= 20:
        print(f"{k:4d} {int(im_size):12d} {int(domain_size):12d} {str(ratio):>25s} {float(ratio):15.12f} {float(diff_from_712):>20.2e}")
    else:
        print(f"{k:4d} {'...':>12} {'...':>12} {'see formula':>25s} {float(ratio):15.12f} {float(diff_from_712):>20.2e}")

print("\n" + "=" * 70)
print("Part 2: 占有率の正確な公式の導出")
print("=" * 70)

# 占有率 r(k) = |Im(k)| / 2^{k-1}
# k偶数: r(k) = (7 * 2^{k-3} - 2) / (3 * 2^{k-1})
#             = (7 * 2^{k-3}) / (3 * 2^{k-1}) - 2 / (3 * 2^{k-1})
#             = 7 / (3 * 4) - 2 / (3 * 2^{k-1})
#             = 7/12 - 1/(3 * 2^{k-2})
# k奇数: r(k) = 3 * 2^{k-3} / 2^{k-1} = 3/4

print("""
占有率の正確な公式:
  k奇数: r(k) = 3/4  (定数、k依存なし)
  k偶数: r(k) = 7/12 - 1/(3 * 2^{k-2})

差分 (7/12からのずれ):
  delta(k) = r(k) - 7/12 = -1/(3 * 2^{k-2})

収束速度:
  |delta(k)| = 1/(3 * 2^{k-2})
  => 指数的収束、各kの増加(+2)で4倍速く収束
""")

# 検証
print("公式の検証:")
for k in range(4, 22, 2):
    im_exact = Fraction(7 * 2**(k-3) - 2, 3)
    domain = Fraction(2**(k-1))
    ratio_exact = im_exact / domain

    formula_ratio = Fraction(7, 12) - Fraction(1, 3 * 2**(k-2))

    check = "OK" if ratio_exact == formula_ratio else "NG"
    print(f"  k={k:2d}: exact = {ratio_exact}, formula = {formula_ratio}, {check}")


print("\n" + "=" * 70)
print("Part 3: k奇数 vs k偶数の振動解析")
print("=" * 70)

print("""
k奇数: r(k) = 3/4 = 9/12
k偶数: r(k) = 7/12 - 1/(3*2^{k-2})

振動幅 = r(k_odd) - r(k_even)
       = 3/4 - (7/12 - 1/(3*2^{k-2}))
       = 9/12 - 7/12 + 1/(3*2^{k-2})
       = 2/12 + 1/(3*2^{k-2})
       = 1/6 + 1/(3*2^{k-2})

k→∞ での振動幅 → 1/6 = 0.166...
""")

print(f"{'k':>4} {'r(k)(奇)':>12} {'r(k+1)(偶)':>15} {'振動幅':>15} {'振動幅-1/6':>15}")

for k in range(3, 31, 2):
    r_odd = Fraction(3, 4)
    r_even = Fraction(7, 12) - Fraction(1, 3 * 2**((k+1)-2))
    oscillation = r_odd - r_even
    osc_minus_16 = oscillation - Fraction(1, 6)
    print(f"{k:4d} {float(r_odd):12.8f} {float(r_even):15.12f} {float(oscillation):15.12f} {float(osc_minus_16):>15.2e}")


print("\n" + "=" * 70)
print("Part 4: 一般的な漸近展開と Cesaro 平均")
print("=" * 70)

# Cesaro平均: 連続するk奇・k偶の平均
# [r(2j+1) + r(2j+2)] / 2 = [3/4 + 7/12 - 1/(3*2^{2j})] / 2
# = [9/12 + 7/12 - 1/(3*4^j)] / 2
# = [16/12 - 1/(3*4^j)] / 2
# = 8/12 - 1/(6*4^j)
# = 2/3 - 1/(6*4^j)

print("""
Cesaro平均 (連続するk奇・k偶ペアの平均):
  C(j) = [r(2j+1) + r(2j+2)] / 2
       = 2/3 - 1/(6 * 4^j)

k→∞ での Cesaro 平均 → 2/3 = 0.666...

注: 2/3 は 3/4 と 7/12 の算術平均 (9/12 + 7/12)/2 = 16/24 = 2/3
""")

print(f"{'j':>4} {'k_odd':>6} {'k_even':>7} {'Cesaro(exact)':>20} {'Cesaro(float)':>15} {'2/3との差':>15}")

for j in range(1, 16):
    k_odd = 2*j + 1
    k_even = 2*j + 2
    r_odd = Fraction(3, 4)
    r_even = Fraction(7, 12) - Fraction(1, 3 * 2**(k_even - 2))
    cesaro = (r_odd + r_even) / 2
    formula_cesaro = Fraction(2, 3) - Fraction(1, 6 * 4**j)

    check = "OK" if cesaro == formula_cesaro else "NG"
    diff_from_23 = cesaro - Fraction(2, 3)

    print(f"{j:4d} {k_odd:6d} {k_even:7d} {str(cesaro):>20s} {float(cesaro):15.12f} {float(diff_from_23):>15.2e} {check}")


print("\n" + "=" * 70)
print("Part 5: 像サイズの漸近展開")
print("=" * 70)

print("""
像サイズの漸近展開:

k奇数: |Im(k)| = (3/4) * 2^{k-1}
                = 3 * 2^{k-3}

k偶数: |Im(k)| = (7/12) * 2^{k-1} - 2/3
                = (7/12) * 2^{k-1} [1 - 8/(7 * 2^{k-1})]

一般形: |Im(k)| = alpha_k * 2^{k-1} + beta_k

  k奇数: alpha = 3/4,  beta = 0
  k偶数: alpha = 7/12, beta = -2/3

差分方程式の視点:
  |Im(k+1)| / |Im(k)| の比率を見る
""")

print(f"{'k':>4} {'|Im(k)|':>12} {'|Im(k+1)|':>12} {'比率':>15} {'理論値':>15}")

for k in range(3, 25):
    if k % 2 == 1:  # k奇数
        im_k = 3 * 2**(k-3)
        im_k1 = (7 * 2**((k+1)-3) - 2) // 3
    else:  # k偶数
        im_k = (7 * 2**(k-3) - 2) // 3
        im_k1 = 3 * 2**((k+1)-3)

    ratio = Fraction(im_k1, im_k)

    # 理論比率:
    # k奇→k+1偶: (7*2^{k-2}-2)/(3*3*2^{k-3}) = (7*2^{k-2}-2)/(9*2^{k-3})
    #           = (14*2^{k-3}-2)/(9*2^{k-3}) = 14/9 - 2/(9*2^{k-3})
    # k偶→k+1奇: 3*2^{k-2}/((7*2^{k-3}-2)/3) = 9*2^{k-3}/(7*2^{k-3}-2)

    if k % 2 == 1:
        theory = "14/9 - O(2^{-k})"
        theory_exact = Fraction(14, 9) - Fraction(2, 9 * 2**(k-3))
    else:
        theory = "9/(7-2/2^{k-3})"
        theory_exact = Fraction(9 * 2**(k-3), 7 * 2**(k-3) - 2)

    diff = float(ratio - theory_exact)
    print(f"{k:4d} {im_k:12d} {im_k1:12d} {float(ratio):15.10f} {float(theory_exact):15.10f} (diff={diff:.2e})")


print("\n" + "=" * 70)
print("Part 6: 収束速度のまとめ")
print("=" * 70)

print("""
=== 収束速度の完全な結果 ===

1. k偶数の占有率:
   r(k) = 7/12 - 1/(3 * 2^{k-2})

   収束速度: 指数的 O(2^{-k})
   具体的: |r(k) - 7/12| = 1/(3 * 2^{k-2}) = (1/3) * 4^{-(k/2 - 1)}

   k=4:  |r-7/12| = 1/12 ≈ 0.0833
   k=6:  |r-7/12| = 1/48 ≈ 0.0208
   k=8:  |r-7/12| = 1/192 ≈ 0.0052
   k=10: |r-7/12| = 1/768 ≈ 0.0013
   k=12: |r-7/12| = 1/3072 ≈ 0.000326

   kが2増えるごとに誤差が1/4に減少

2. k奇数の占有率:
   r(k) = 3/4 (正確、補正項なし)

3. 全kでの平均占有率:
   Cesaro平均 C(j) = [r(2j+1) + r(2j+2)]/2 = 2/3 - 1/(6*4^j)
   C(j) → 2/3 (指数的収束)

4. 振動:
   k奇偶の振動幅 = 1/6 + O(2^{-k}) → 1/6

5. 像サイズの漸近展開:
   k偶: |Im(k)| = (7/12) * 2^{k-1} - 2/3
                 = (7 * 2^{k-3} - 2) / 3

   第1項: (7/12) * 2^{k-1}  (指数成長)
   第2項: -2/3  (定数補正)

   相対誤差: |(-2/3) / ((7/12)*2^{k-1})| = 8/(7*2^{k-1})

6. 交互比率:
   |Im(k+1)| / |Im(k)| → { 14/9 (k奇→偶), 9/7 (k偶→奇) }
   (14/9) * (9/7) = 2*9/(9*7)*7*2 → 14*9/(9*7) = 2 (正しい: 2ステップで2倍)
""")

# 交互比率の検証
print("交互比率の漸近値:")
print("  (14/9) * (9/7) =", float(Fraction(14, 9) * Fraction(9, 7)), "= 2 (正しい: 2ステップで定義域が4倍、像も≈4倍だが奇数のみなので2倍)")


print("\n" + "=" * 70)
print("Part 7: 数値検証 (直接計算との比較)")
print("=" * 70)

from collections import Counter

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

print(f"{'k':>4} {'|Im|(直接)':>12} {'|Im|(公式)':>12} {'check':>6} {'占有率':>12} {'公式占有率':>15} {'差':>12}")

for k in range(3, 22):
    mod = 2**k
    residues = [r for r in range(1, mod, 2)]
    image_set = set()
    for r in residues:
        t = syracuse(r)
        image_set.add(t % mod)

    im_direct = len(image_set)

    if k % 2 == 1:
        im_formula = 3 * 2**(k-3)
        ratio_formula = Fraction(3, 4)
    else:
        im_formula = (7 * 2**(k-3) - 2) // 3
        ratio_formula = Fraction(7, 12) - Fraction(1, 3 * 2**(k-2))

    domain_size = 2**(k-1)
    ratio_direct = Fraction(im_direct, domain_size)

    check = "OK" if im_direct == im_formula else "NG"
    diff = float(ratio_direct - Fraction(7, 12))

    parity = "奇" if k % 2 == 1 else "偶"
    print(f"{k:4d}({parity}) {im_direct:12d} {im_formula:12d} {check:>6s} {float(ratio_direct):12.8f} {float(ratio_formula):15.12f} {diff:>12.2e}")


print("\n" + "=" * 70)
print("Part 8: 二進展開の視点")
print("=" * 70)

print("""
像サイズを二進展開の視点で理解:

k奇数: |Im| = 3 * 2^{k-3} = 11_2 * 2^{k-3}
  二進表現: 11 followed by (k-3) zeros

k偶数: |Im| = (7 * 2^{k-3} - 2) / 3
  k=4:  |Im| = (7*2 - 2)/3 = 12/3 = 4
  k=6:  |Im| = (7*8 - 2)/3 = 54/3 = 18
  k=8:  |Im| = (7*32 - 2)/3 = 222/3 = 74
  k=10: |Im| = (7*128 - 2)/3 = 894/3 = 298
  k=12: |Im| = (7*512 - 2)/3 = 3582/3 = 1194
  k=14: |Im| = (7*2048 - 2)/3 = 14334/3 = 4778
  k=16: |Im| = (7*8192 - 2)/3 = 57342/3 = 19114
  k=18: |Im| = (7*32768 - 2)/3 = 229374/3 = 76458
""")

print("k偶数の像サイズの二進表現:")
for k in range(4, 32, 2):
    im = (7 * 2**(k-3) - 2) // 3
    print(f"  k={k:2d}: |Im| = {im:>12d} = {bin(im)}")

# パターン分析
print("\nパターン: (7 * 2^n - 2) / 3 の二進表現")
for n in range(1, 20):
    val = (7 * 2**n - 2) // 3
    print(f"  n={n:2d}: {val:>10d} = {bin(val):>25s}")


print("\n" + "=" * 70)
print("Part 9: 2-adic 視点")
print("=" * 70)

print("""
2-adic 的に:
  (7 * 2^{k-3} - 2) / 3 を mod 2^m で見ると:

  7 * 2^{k-3} ≡ 0 (mod 2^{k-3})
  -2/3 の 2-adic 表現: sum_{i>=0} 2^{2i+1} = ...10101010_2

  よって (7*2^{k-3} - 2)/3 は 2-adic で下位ビットが ...10101010 のパターン

これは像サイズの 7/12 への収束を 2-adic 的に説明:
  7/12 = 7/(4*3) の 2-adic 展開
  1/3 の 2-adic 展開: ...01010101_2 = sum 2^{2i} = 1/(1-4) = -1/3  (in 2-adic)
  2/3 の 2-adic 展開: ...10101010_2
  7/12 = 7/12 ...
""")


print("\n" + "=" * 70)
print("Part 10: 更に高次の補正項の解析")
print("=" * 70)

print("""
k偶数の占有率:
  r(k) = 7/12 - 1/(3 * 2^{k-2})

これは1次までの漸近展開で既に *正確* である。
つまり、高次補正項は存在しない！

理由: 公式 |Im| = (7 * 2^{k-3} - 2)/3 は閉公式であり、
  r(k) = (7 * 2^{k-3} - 2) / (3 * 2^{k-1})
       = 7/(3*4) - 2/(3*2^{k-1})
       = 7/12 - 1/(3 * 2^{k-2})

これ以上の項は存在しない。漸近展開は有限項(2項)で打ち切られる。

まとめ:
  r(k) = 7/12 - (1/3) * 2^{-(k-2)}  [正確、補正項なし]

同様に k奇数:
  r(k) = 3/4  [正確、補正項なし]

一般公式（k奇偶をまとめた形）:
  r(k) = (3/4 + 7/12)/2 + (-1)^k * (3/4 - 7/12)/2 + (correction)
       = 2/3 + (-1)^k * 1/12 + (correction for k even)

ただし (-1)^k の符号:
  k奇: (-1)^k = -1 → 2/3 - 1/12 = 7/12 NG

もっと正確に:
  k奇: r(k) = 3/4
  k偶: r(k) = 7/12 - 1/(3*2^{k-2})

統一公式を試す:
  r(k) = 2/3 + (1/12)*(-1)^{k+1} + f(k)

  k奇: 2/3 + 1/12 = 2/3 + 1/12 = 8/12 + 1/12 = 9/12 = 3/4 OK
  k偶: 2/3 - 1/12 = 8/12 - 1/12 = 7/12... + f(k) = -1/(3*2^{k-2})

  f(k) = { 0            if k odd
          { -1/(3*2^{k-2}) if k even
       = (1 - (-1)^k)/2 * (-1/(3*2^{k-2}))

統一公式:
  r(k) = 2/3 + (1/12)*(-1)^{k+1} - (1-(-1)^k)/(6*2^{k-2})
""")

# 統一公式の検証
print("統一公式の検証:")
for k in range(3, 25):
    if k % 2 == 1:
        r_exact = Fraction(3, 4)
    else:
        r_exact = Fraction(7, 12) - Fraction(1, 3 * 2**(k-2))

    # 統一公式
    term1 = Fraction(2, 3)
    term2 = Fraction((-1)**(k+1), 12)
    term3 = -Fraction(1 - (-1)**k, 6 * 2**(k-2))
    r_unified = term1 + term2 + term3

    check = "OK" if r_exact == r_unified else "NG"
    print(f"  k={k:2d}: exact={float(r_exact):.12f}, unified={float(r_unified):.12f}, {check}")
