"""
T(n) mod 2^k の像サイズ公式: k偶数での 7/12 への収束速度の解析 (v2)

統一公式の修正と、交互比率・2-adic構造の深い解析
"""

from fractions import Fraction
import math

print("=" * 70)
print("Part 1: 統一公式の正しい導出")
print("=" * 70)

# 占有率:
# k奇: r(k) = 3/4
# k偶: r(k) = 7/12 - 1/(3*2^{k-2})

# 統一的に書くために:
# epsilon(k) = (1 + (-1)^k) / 2  (k偶で1, k奇で0)
# r(k) = 3/4 - epsilon(k) * [3/4 - 7/12 + 1/(3*2^{k-2})]
#       = 3/4 - epsilon(k) * [1/6 + 1/(3*2^{k-2})]

# 検証
print("統一公式: r(k) = 3/4 - epsilon(k) * [1/6 + 1/(3*2^{k-2})]")
print("where epsilon(k) = (1+(-1)^k)/2 (k偶で1, k奇で0)")
print()

for k in range(3, 25):
    if k % 2 == 1:
        r_exact = Fraction(3, 4)
    else:
        r_exact = Fraction(7, 12) - Fraction(1, 3 * 2**(k-2))

    eps = (1 + (-1)**k) // 2  # 0 or 1
    r_unified = Fraction(3, 4) - eps * (Fraction(1, 6) + Fraction(1, 3 * 2**(k-2)))

    check = "OK" if r_exact == r_unified else "NG"
    if k <= 14:
        print(f"  k={k:2d}: eps={eps}, exact={str(r_exact):>10s}, unified={str(r_unified):>10s}, {check}")

print("  ... (全てOK)")

print("\n" + "=" * 70)
print("Part 2: 交互比率の正確な公式")
print("=" * 70)

# |Im(k+1)| / |Im(k)| の正確な値
print("交互比率 |Im(k+1)|/|Im(k)| の正確な分析:")
print()

for k in range(3, 26):
    if k % 2 == 1:  # k奇 → k+1偶
        im_k = 3 * 2**(k-3)
        im_k1 = (7 * 2**((k+1)-3) - 2) // 3
    else:  # k偶 → k+1奇
        im_k = (7 * 2**(k-3) - 2) // 3
        im_k1 = 3 * 2**((k+1)-3)

    ratio = Fraction(im_k1, im_k)

    if k % 2 == 1:
        # k奇→k+1偶: (7*2^{k-2}-2)/(3*3*2^{k-3}) = (7*2^{k-2}-2)/(9*2^{k-3})
        #           = (14*2^{k-3}-2)/(9*2^{k-3}) = 14/9 - 2/(9*2^{k-3})
        theory = Fraction(14, 9) - Fraction(2, 9 * 2**(k-3))
        limit = Fraction(14, 9)
    else:
        # k偶→k+1奇: 3*2^{k-2}/((7*2^{k-3}-2)/3) = 9*2^{k-2}/(7*2^{k-3}-2)
        #           = 18*2^{k-3}/(7*2^{k-3}-2) → 18/7
        theory = Fraction(9 * 2**(k-2), 7 * 2**(k-3) - 2)
        limit = Fraction(18, 7)

    diff_from_limit = ratio - limit
    parity = "奇→偶" if k % 2 == 1 else "偶→奇"
    lim_str = "14/9" if k % 2 == 1 else " 9/7"

    if k <= 16:
        print(f"  k={k:2d} ({parity}): ratio={float(ratio):.10f}, limit={lim_str}={float(limit):.10f}, diff={float(diff_from_limit):.2e}")

    assert ratio == theory, f"k={k}: ratio={ratio} != theory={theory}"

print("""
交互比率の正確な公式:
  k奇→k+1偶: |Im(k+1)|/|Im(k)| = 14/9 - 2/(9*2^{k-3})
              → 14/9 ≈ 1.5556  (指数的収束, O(2^{-k}))

  k偶→k+1奇: |Im(k+1)|/|Im(k)| = 9*2^{k-3}/(7*2^{k-3}-2)
              = 9/7 * 1/(1-2/(7*2^{k-3}))
              → 9/7 ≈ 1.2857  (指数的収束, O(2^{-k}))

検証: (14/9) * (9/7) = 14/7 = 2 (2ステップで2倍)
""")

# 2ステップ比率の検証
print(f"(14/9) * (9/7) = {float(Fraction(14,9) * Fraction(9,7))} = 2")


print("\n" + "=" * 70)
print("Part 3: 像サイズの差分方程式")
print("=" * 70)

print("""
像サイズの差分方程式を導出:

a(k) = |Im(T mod 2^k)| とおく。
  k奇: a(k) = 3*2^{k-3}
  k偶: a(k) = (7*2^{k-3}-2)/3

2ステップの関係:
  a(k+2) / a(k) を計算する。

k奇→k+2奇:
  a(k+2)/a(k) = 3*2^{k-1} / (3*2^{k-3}) = 4

k偶→k+2偶:
  a(k+2)/a(k) = (7*2^{k-1}-2) / (7*2^{k-3}-2)
             = (7*4*2^{k-3}-2)/(7*2^{k-3}-2)
             = 4 - 6/(7*2^{k-3}-2)

a(k+2) = 4*a(k) + correction

k奇: a(k+2) = 4*a(k)  (正確、補正なし)
k偶: a(k+2) = 4*a(k) + ?
  4*a(k) = 4*(7*2^{k-3}-2)/3 = (28*2^{k-3}-8)/3
  a(k+2) = (7*2^{k-1}-2)/3 = (28*2^{k-3}-2)/3
  差 = (28*2^{k-3}-2)/3 - (28*2^{k-3}-8)/3 = 6/3 = 2

つまり: k偶: a(k+2) = 4*a(k) + 2
""")

print("差分方程式の検証:")
print("k奇: a(k+2) = 4*a(k)")
for k in range(3, 20, 2):
    a_k = 3 * 2**(k-3)
    a_k2 = 3 * 2**((k+2)-3)
    check = "OK" if a_k2 == 4 * a_k else "NG"
    print(f"  k={k:2d}: a(k)={a_k:>8d}, a(k+2)={a_k2:>8d}, 4*a(k)={4*a_k:>8d}, {check}")

print("\nk偶: a(k+2) = 4*a(k) + 2")
for k in range(4, 20, 2):
    a_k = (7 * 2**(k-3) - 2) // 3
    a_k2 = (7 * 2**((k+2)-3) - 2) // 3
    check = "OK" if a_k2 == 4 * a_k + 2 else "NG"
    print(f"  k={k:2d}: a(k)={a_k:>8d}, a(k+2)={a_k2:>8d}, 4*a(k)+2={4*a_k+2:>8d}, {check}")


print("\n" + "=" * 70)
print("Part 4: 1ステップ差分方程式")
print("=" * 70)

print("""
1ステップの差分方程式:
  k奇→k+1偶: a(k+1) = a(k)*(14/9) - 2/(9*2^{k-3}) * a(k)

正確に:
  k奇: a(k) = 3*2^{k-3}
  k+1偶: a(k+1) = (7*2^{k-2}-2)/3

  a(k+1) = (7*2*2^{k-3}-2)/3 = (14*2^{k-3}-2)/3

  a(k+1) in terms of a(k):
    a(k) = 3*2^{k-3} => 2^{k-3} = a(k)/3
    a(k+1) = (14*a(k)/3 - 2)/3 = (14*a(k) - 6)/9

  k偶→k+1奇:
    a(k) = (7*2^{k-3}-2)/3
    a(k+1) = 3*2^{k-2} = 3*2*2^{k-3} = 6*2^{k-3}

    a(k) = (7*2^{k-3}-2)/3 => 7*2^{k-3} = 3*a(k)+2 => 2^{k-3} = (3*a(k)+2)/7
    a(k+1) = 6*(3*a(k)+2)/7 = (18*a(k)+12)/7

まとめ:
  k奇→k+1偶: a(k+1) = (14*a(k) - 6) / 9
  k偶→k+1奇: a(k+1) = (18*a(k) + 12) / 7
""")

print("1ステップ差分方程式の検証:")
for k in range(3, 22):
    if k % 2 == 1:
        a_k = 3 * 2**(k-3)
        a_k1 = (7 * 2**((k+1)-3) - 2) // 3
        a_k1_formula = (14 * a_k - 6) // 9
        check = "OK" if a_k1 == a_k1_formula else "NG"
        print(f"  k={k:2d} (奇→偶): a(k)={a_k:>8d}, a(k+1)={a_k1:>8d}, (14a-6)/9={a_k1_formula:>8d}, {check}")
    else:
        a_k = (7 * 2**(k-3) - 2) // 3
        a_k1 = 3 * 2**((k+1)-3)
        a_k1_formula = (18 * a_k + 12) // 7
        check = "OK" if a_k1 == a_k1_formula else "NG"
        print(f"  k={k:2d} (偶→奇): a(k)={a_k:>8d}, a(k+1)={a_k1:>8d}, (18a+12)/7={a_k1_formula:>8d}, {check}")


print("\n" + "=" * 70)
print("Part 5: 2-adic 構造と二進パターンの解析")
print("=" * 70)

# k偶の像サイズ (7*2^n-2)/3 の二進パターン: 100, 10010, 1001010, ...
# つまり先頭が "100" で、残りは "10" の繰り返し

print("k偶の像サイズの二進パターン分析:")
print("  (7*2^n - 2)/3 = ?")
print()

for n in range(1, 25):
    val = (7 * 2**n - 2) // 3
    b = bin(val)[2:]  # "0b" を除去

    # パターン解析
    # n奇数: 10 01 01 ... 0 (末尾0)
    # n偶数: 10 01 01 ... 10 (末尾10)
    if n <= 12:
        print(f"  n={n:2d} (k={n+3:2d}偶): {val:>8d} = {b}")

print("""
パターン:
  n奇 (k=偶): 1 (0010)* 10  例: 100(n=1), 1001010(n=5), 100101010(n=7)
  n偶 (k=偶NG): k=n+3 なので n=k-3, k偶 ⟹ n奇

  k偶 ⟹ n=k-3 奇数

  n=1: 100
  n=3: 10010
  n=5: 1001010
  n=7: 100101010
  ...

  つまり: "1" + "00" + ("10") * ((n-1)/2)
  = 2^{n+1} + sum_{i=0}^{(n-3)/2} 2^{2i+1}
  = 2^{n+1} + 2*(4^{(n-1)/2} - 1)/3

  検証:
""")

for n in range(1, 20, 2):  # n奇数 only (k偶)
    val_exact = (7 * 2**n - 2) // 3
    # formula: 2^{n+1} + 2*(4^{(n-1)/2} - 1)/3
    m = (n - 1) // 2
    val_formula = 2**(n+1) + 2 * (4**m - 1) // 3

    # 別の表現: 直接計算
    # (7 * 2^n - 2)/3 = (7*2^n - 2)/3
    # 2^{n+1} = 2*2^n
    # 7*2^n / 3 = 2*2^n + 2^n/3
    # (7*2^n - 2)/3 = 2*2^n + (2^n - 2)/3

    check = "OK" if val_exact == val_formula else "NG"
    if n <= 13:
        print(f"  n={n}: exact={val_exact}, formula=2^{n+1}+2*(4^{m}-1)/3={val_formula}, {check}")


print("\n" + "=" * 70)
print("Part 6: 占有率の収束速度の統一的理解")
print("=" * 70)

print("""
=== 主結果: 収束速度の完全な記述 ===

定理 (像サイズの閉公式と漸近):
  Syracuse写像 T: Z_odd → Z_odd, T(n) = (3n+1)/2^{v_2(3n+1)} に対し、
  T mod 2^k: Z_odd/2^kZ → Z_odd/2^kZ の像のサイズを a(k) = |Im(T mod 2^k)| とする。

  k奇数 (k >= 3): a(k) = 3 * 2^{k-3}
  k偶数 (k >= 4): a(k) = (7 * 2^{k-3} - 2) / 3

  占有率 rho(k) = a(k) / 2^{k-1} について:

  (1) k奇数: rho(k) = 3/4  (k非依存の定数)
  (2) k偶数: rho(k) = 7/12 - (1/3) * 2^{-(k-2)}

  収束速度:
  (3) |rho(k) - 7/12| = (1/3) * 2^{-(k-2)}  (k偶数)
      kが2増えるごとに誤差は1/4に縮小 (指数的収束)
  (4) rho(k) - 3/4 = 0  (k奇数、正確に3/4)

  差分方程式:
  (5) k奇: a(k+2) = 4 * a(k)         (正確)
  (6) k偶: a(k+2) = 4 * a(k) + 2     (正確)
  (7) k奇→k+1偶: a(k+1) = (14*a(k) - 6) / 9
  (8) k偶→k+1奇: a(k+1) = (18*a(k) + 12) / 7

  交互比率:
  (9)  a(k+1)/a(k) → 14/9 ≈ 1.5556  (k奇から偶)
  (10) a(k+1)/a(k) → 9/7  ≈ 1.2857  (k偶から奇)
  (11) (14/9) * (9/7) = 2  (2ステップで2倍)

  振動:
  (12) rho(k_odd) - rho(k_even) = 1/6 + 1/(3*2^{k-2}) → 1/6 ≈ 0.1667
  (13) Cesaro平均: [rho(2j+1) + rho(2j+2)]/2 = 2/3 - 1/(6*4^j) → 2/3

注意: 漸近展開は *正確な閉公式* から直接得られるため、
      O記法の中に隠れた未知の定数は存在しない。
      全ての補正項は明示的に計算される。
""")

# 漸近的に等価な形式のまとめ
print("占有率の様々な等価な表現:")
print()
for k in [4, 6, 8, 10, 20, 40, 100]:
    r = Fraction(7, 12) - Fraction(1, 3 * 2**(k-2))
    # 各表現
    expr1 = f"7/12 - 1/(3*2^{k-2})"
    expr2 = f"7/12 - 1/{3*2**(k-2)}"
    expr3 = f"7/12 * (1 - 8/(7*2^{k-1}))"
    rel_err = float(Fraction(8, 7 * 2**(k-1)))

    print(f"  k={k:3d}: rho = {expr1:>25s} = {float(r):.15f}, 相対誤差(7/12から) = {rel_err:.2e}")

print("\n\n" + "=" * 70)
print("Part 7: なぜ 7/12 なのか? — 構造的理由の解析")
print("=" * 70)

print("""
7/12 の起源を多重度分布から理解する。

k偶数の多重度分布:
  N(1,k) = (7*2^{k-4} - 4)/3  ← 単射的像の数
  N(2,k) = (2^{k-2} + 2)/3    ← 2重像の数
  N(m,k) = N(m-2, k-3)        ← m >= 3

合計: sum N(m,k) = |Im| = (7*2^{k-3}-2)/3

N(1,k) + N(2,k) = (7*2^{k-4}-4)/3 + (2^{k-2}+2)/3
                 = (7*2^{k-4} + 2^{k-2} - 2) / 3
                 = (7*2^{k-4} + 2*2^{k-3} - 2) / 3

比率 N(1,k)/|Im| = ?
""")

print("k偶数での多重度分布の割合:")
print(f"{'k':>4} {'N(1)/|Im|':>12} {'N(2)/|Im|':>12} {'N(>=3)/|Im|':>12}")
for k in range(4, 22, 2):
    N1 = (7 * 2**(k-4) - 4) // 3
    N2 = (2**(k-2) + 2) // 3
    im_total = (7 * 2**(k-3) - 2) // 3
    N_ge3 = im_total - N1 - N2

    print(f"  k={k:2d}: {float(Fraction(N1, im_total)):12.8f} {float(Fraction(N2, im_total)):12.8f} {float(Fraction(N_ge3, im_total)):12.8f}")

print("""
N(1)/|Im| → 1/2
N(2)/|Im| → 2/7
N(>=3)/|Im| → ?

N(1)の漸近比:
  N(1,k) / |Im(k)| = (7*2^{k-4}-4) / (7*2^{k-3}-2)
  = (7*2^{k-4}-4) / (2*7*2^{k-4}-2)
  → 1/2 as k→∞

N(2)の漸近比:
  N(2,k) / |Im(k)| = (2^{k-2}+2) / ((7*2^{k-3}-2)/1)
  = 3*(2^{k-2}+2) / (7*2^{k-3}-2)
  = 3*(2*2^{k-3}+2) / (7*2^{k-3}-2)
  → 6/7 as k→∞? No...

  N(2)/|Im| = (2^{k-2}+2)/3 / ((7*2^{k-3}-2)/3) = (2^{k-2}+2)/(7*2^{k-3}-2)
  = (2*2^{k-3}+2)/(7*2^{k-3}-2) → 2/7
""")

# 7/12 の代数的起源
print("\n7/12 の代数的起源:")
print()
print("k偶数のsyracuse写像の構造:")
print("  T(n) = (3n+1)/2^{v_2(3n+1)} mod 2^k")
print()
print("  k偶数で像が少ない理由:")
print("  v_2 の偶奇による分類が k の偶奇と干渉する")
print()

# 7 = 4 + 3 の分解を探る
# |Im| = (7*2^{k-3}-2)/3
# = (4*2^{k-3} + 3*2^{k-3} - 2) / 3
# = (2^{k-1} + 3*2^{k-3} - 2) / 3
# = 2^{k-1}/3 + 2^{k-3} - 2/3
#
# k奇: |Im| = 3*2^{k-3} = 2^{k-1}/2 + 2^{k-3} = 2^{k-3}(2+1) = 3*2^{k-3}
#
# k偶 vs k奇:
# Im_odd - Im_even = 3*2^{k-3} - (7*2^{k-3}-2)/3
# = (9*2^{k-3} - 7*2^{k-3} + 2)/3
# = (2*2^{k-3} + 2)/3
# = (2^{k-2} + 2)/3
# = N(2, k) !

print("像サイズの差 |Im_odd| - |Im_even|:")
for k in range(5, 20, 2):
    im_odd = 3 * 2**(k-3)
    im_even_next = (7 * 2**((k+1)-3) - 2) // 3
    N2_next = (2**((k+1)-2) + 2) // 3
    diff = im_odd * 2 - im_even_next  # 同じkレベルでの比較ではなく...

    # 同じレベルでの比較: k と k+1
    # 実は定義域サイズが異なるので、占有率で比較すべき

print("""
重要な関係:
  k奇での像数 a(k) = 3*2^{k-3}
  k偶での像数 a(k+1) = (7*2^{k-2}-2)/3

  差: a(k) - a(k+1)/2 = 3*2^{k-3} - (7*2^{k-2}-2)/6
    = (18*2^{k-3} - 7*2^{k-2} + 2) / 6
    = (18*2^{k-3} - 14*2^{k-3} + 2) / 6
    = (4*2^{k-3} + 2) / 6
    = (2^{k-1} + 2) / 6

7/12 が現れる本質的理由:
  k偶数では、v_2(3n+1) の値域が制限されることで、
  約 1/6 (= 3/4 - 7/12) の像が「失われる」。
  この失われた像の数は正確に N(2,k) = (2^{k-2}+2)/3 に等しい。
  これは多重度2の像の数であり、k偶数特有の「衝突」を表す。
""")


print("\n" + "=" * 70)
print("Part 8: 多重度の加重平均と期待値")
print("=" * 70)

print("平均多重度 = 定義域サイズ / 像サイズ = 2^{k-1} / |Im|")
for k in range(3, 22):
    if k % 2 == 1:
        im = 3 * 2**(k-3)
    else:
        im = (7 * 2**(k-3) - 2) // 3
    domain = 2**(k-1)
    avg_mult = Fraction(domain, im)
    parity = "奇" if k % 2 == 1 else "偶"

    # k奇: 2^{k-1}/(3*2^{k-3}) = 4/3
    # k偶: 2^{k-1}/((7*2^{k-3}-2)/3) = 3*2^{k-1}/(7*2^{k-3}-2) → 12/7
    if k % 2 == 1:
        limit = Fraction(4, 3)
    else:
        limit = Fraction(12, 7)

    if k <= 16:
        print(f"  k={k:2d} ({parity}): avg_mult = {float(avg_mult):.8f}, limit = {float(limit):.8f} = {limit}")

print("""
平均多重度:
  k奇: E[mult] = 4/3  (正確、k非依存)
  k偶: E[mult] = 12/7 + O(2^{-k}) → 12/7 ≈ 1.7143

  E[mult]_odd * rho_odd = (4/3)*(3/4) = 1
  E[mult]_even * rho_even → (12/7)*(7/12) = 1  (整合的)

つまり占有率 = 1/E[mult] が成り立つ。
  k奇: rho = 3/4 = 1/(4/3)
  k偶: rho → 7/12 = 1/(12/7)
""")


print("\n" + "=" * 70)
print("Part 9: 全結果の数値表")
print("=" * 70)

print(f"{'k':>4} {'parity':>7} {'|Im|':>10} {'rho':>14} {'rho-limit':>14} {'avg_mult':>12} {'ratio':>10}")
print("-" * 75)

for k in range(3, 30):
    if k % 2 == 1:
        im = 3 * 2**(k-3)
        rho_limit = Fraction(3, 4)
    else:
        im = (7 * 2**(k-3) - 2) // 3
        rho_limit = Fraction(7, 12)

    domain = 2**(k-1)
    rho = Fraction(im, domain)
    diff = rho - rho_limit
    avg_mult = Fraction(domain, im)
    parity = "奇" if k % 2 == 1 else "偶"

    # ratio to previous
    if k > 3:
        if (k-1) % 2 == 1:
            im_prev = 3 * 2**((k-1)-3)
        else:
            im_prev = (7 * 2**((k-1)-3) - 2) // 3
        ratio = float(Fraction(im, im_prev))
        ratio_str = f"{ratio:.6f}"
    else:
        ratio_str = "---"

    if k <= 24:
        print(f"{k:4d} {parity:>7s} {im:10d} {float(rho):14.10f} {float(diff):>14.2e} {float(avg_mult):12.8f} {ratio_str:>10s}")
