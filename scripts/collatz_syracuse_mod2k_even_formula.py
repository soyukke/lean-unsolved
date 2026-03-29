"""
k偶数の多重度分布の正確な公式

k偶数テーブル:
m\k |      4      6      8     10     12     14     16     18
  1 |      1      8     36    148    596   2388   9556  38228
  2 |      2      7     26    102    406   1622   6486  25942
  3 |      1      2      9     36    144    576   2304   9216
  4 |             1      2      9     36    144    576   2304
  5 |                    1      2      9     36    144    576
  6 |                           1      2      9     36    144
  7 |                                  1      2      9     36
  8 |                                         1      2      9

注目: m>=3 の部分は k奇数のテーブルと同じ!
つまり m>=3 で N(m, k偶) = N(m-2, k-4) (k奇のテーブル参照)
正確には N(m, k偶) = 9*2^{k-2m-3} (k-2m >= 4 のとき)

m=2 の列: 2, 7, 26, 102, 406, 1622, 6486, 25942
m=1 の列: 1, 8, 36, 148, 596, 2388, 9556, 38228

m=2 の差分列: 5, 19, 76, 304, 1216, 4864, 19456
比率: 19/5=3.8, 76/19=4, 304/76=4, 1216/304=4, 4864/1216=4
-> 7, 26, 102, 406, 1622 の隣接比:
  26/7=3.71, 102/26=3.92, 406/102=3.98, 1622/406=3.995 -> 4に収束

差分列: 7-2=5, 26-7=19, 102-26=76, 406-102=304
二次差分: 14, 57, 228 ...
"""

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

# N(m, k) テーブル構築
Ndict = {}
for k in range(3, 20):
    mod = 2**k
    residues = [r for r in range(1, mod, 2)]
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())
    for m, count in md.items():
        Ndict[(m, k)] = count

# k偶数, m=2 の列の公式を探す
print("k偶数, m=2 の分析:")
print("  k:  N(2,k)   N(2,k)-N(1,k-2奇)  関係")
for k in range(4, 20, 2):
    n2 = Ndict.get((2, k))
    n1_prev_odd = Ndict.get((1, k-1))  # k-1は奇数
    if n2 and n1_prev_odd:
        diff = n2 - n1_prev_odd
        print(f"  k={k}: N(2,{k})={n2}, N(1,{k-1})={n1_prev_odd}, 差={diff}")

# N(2,k偶) - N(1, k-1奇) の差:
# k=4: 2-2=0, k=6: 7-9=-2, k=8: 26-36=-10, k=10: 102-144=-42
# 差の差: -2, -8, -32 -> 比率4
# 差 = -2*(4^{j}-1)/3 ?

# 別のアプローチ: k偶数でのN(m,k)をN(m,k奇)との対応で理解
# k偶数のm>=3の部分はk奇数と同一の数列
# k偶数のm=1,2だけが特殊

# k偶数, m=2: 2, 7, 26, 102, 406, 1622, 6486, 25942
# これを a_j (j=0,1,2,...) とする (k=4+2j)
# a_0=2, a_1=7, a_2=26, a_3=102, a_4=406
# a_j = 4*a_{j-1} - a_{j-2} ?
# 4*2-1=7 OK, 4*7-2=26 OK, 4*26-2=102 OK NG(4*26-2=102)
# 4*7-2=26 OK
# 4*26-2=102 OK
# 4*102-2=406 OK
# 4*406-2=1622 OK
# 4*1622-2=6486 OK
# 4*6486-2=25942 OK!

print("\n\n漸化式チェック: N(2, k+2) = 4*N(2, k) - 2")
for k in range(6, 20, 2):
    actual = Ndict.get((2, k))
    predicted = 4 * Ndict.get((2, k-2)) - 2
    match = "OK" if actual == predicted else "NG"
    print(f"  k={k}: N(2,k)={actual}, 4*N(2,k-2)-2={predicted}, {match}")

# N(2,k) = 4*N(2,k-2) - 2
# 特殊解 c: c = 4c - 2 => c = 2/3
# 一般解: N(2,k) - 2/3 = C * 4^{(k-4)/2}
# N(2,4) - 2/3 = 2 - 2/3 = 4/3 => C = 4/3
# N(2,k) = 4/3 * 4^{(k-4)/2} + 2/3 = 4/3 * 2^{k-4} + 2/3 = (4*2^{k-4}+2)/3
# = (2^{k-2} + 2)/3

print("\n閉じた公式: N(2,k偶) = (2^{k-2} + 2) / 3")
for k in range(4, 20, 2):
    actual = Ndict.get((2, k))
    predicted = (2**(k-2) + 2) // 3
    match = "OK" if actual == predicted else "NG"
    print(f"  k={k}: N(2,k)={actual}, (2^{k-2}+2)/3={predicted}, {match}")

# k偶数, m=1 の公式（既に導出済み）
# N(1, k偶) = (7*2^{k-4} - 4) / 3

# k偶数, m=3: 1, 2, 9, 36, 144, 576, 2304, 9216
# これは k奇数の m=1: 2, 9, 36, 144, 576, 2304, 9216 の1つずれ
# つまり N(3, k偶) = N(1, k-3 奇) = N(1, k-3)
# 正確には: N(3,6)=2=N(1,3), N(3,8)=9=N(1,5), N(3,10)=36=N(1,7)
# つまり N(m, k偶) = N(m-2, k-3) for m >= 3?
# No: N(3,8)=9, N(1,5)=9 OK
# N(4,8)=2, N(2,5)=2 OK
# N(5,8)=1, N(3,5)=1 OK

# もっと正確に: k偶数のm>=3 は k奇数の m-2, k-3 に対応
# N(m, k偶) for m>=3 は N(m-2, k-3 奇) に等しい?
# N(3,6)=2, N(1,3)=2 OK
# N(3,8)=9, N(1,5)=9 OK
# N(4,8)=2, N(2,5)=2 OK
# N(3,10)=36, N(1,7)=36 OK
# N(4,10)=9, N(2,7)=9 OK

# 実は同じ数列が現れている
# k奇数: 末尾が ..., 9, 2, 1
# k偶数: m>=3 の部分は ..., 9, 2, 1 (同じ数列の再利用)

# 正確には:
# k偶数, m=3,4,... は k-3 が奇数 で m-2 = 1,2,... として
# N(m, k偶) = N(m-2, k-3)

# k=6, m=3: N(3,6)=2, N(1,3)=2 OK
# k=8, m=3: N(3,8)=9, N(1,5)=9 OK
# k=10, m=3: N(3,10)=36, N(1,7)=36 OK
# k=12, m=3: N(3,12)=144, N(1,9)=144 OK

print("\n\nN(m, k偶) = N(m-2, k-3) for m >= 3 の検証:")
all_ok = True
for k in range(6, 20, 2):
    for m in range(3, 15):
        actual = Ndict.get((m, k))
        predicted = Ndict.get((m-2, k-3))
        if actual is not None and predicted is not None:
            if actual != predicted:
                print(f"  NG: N({m},{k})={actual} != N({m-2},{k-3})={predicted}")
                all_ok = False
if all_ok:
    print("  全て OK!")

# ==============================================================
# 完全な公式のまとめと検証
# ==============================================================
print("\n\n" + "=" * 70)
print("完全な多重度公式")
print("=" * 70)

def N_formula(m, k):
    """多重度 m の像の数の公式"""
    if k % 2 == 1:  # k 奇数
        # N(m, k奇) = N(1, k-2(m-1))  where k-2(m-1) は奇数
        k_base = k - 2*(m-1)
        if k_base < 1:
            return 0
        if k_base == 1:
            return 1
        if k_base == 3:
            return 2
        if k_base >= 5:
            return 9 * 2**(k_base - 5)
    else:  # k 偶数
        if m == 1:
            if k < 4:
                return None
            return (7 * 2**(k-4) - 4) // 3
        elif m == 2:
            if k < 4:
                return None
            return (2**(k-2) + 2) // 3
        else:
            # m >= 3: N(m, k偶) = N(m-2, k-3) where k-3 は奇数
            return N_formula(m-2, k-3)
    return None

print("\n完全検証:")
errors = 0
for k in range(3, 20):
    mod = 2**k
    residues = [r for r in range(1, mod, 2)]
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())

    for m in sorted(md.keys()):
        actual = md[m]
        predicted = N_formula(m, k)
        if predicted is None:
            predicted = "N/A"
        match = "OK" if actual == predicted else "NG"
        if match == "NG":
            print(f"  k={k:2d}, m={m:2d}: actual={actual:6d}, predicted={predicted}, {match}")
            errors += 1

if errors == 0:
    print("  全て OK! 公式は k=3..19, 全ての多重度で完全一致")
else:
    print(f"  エラー {errors}件")

# ==============================================================
# 公式の数学的意味
# ==============================================================
print("\n\n" + "=" * 70)
print("数学的解釈")
print("=" * 70)

print("""
定理 (Syracuse mod 2^k の像の多重度分布):

T: Z_odd/2^kZ -> Z_odd/2^kZ を T(r) = (3r+1)/2^{v2(3r+1)} mod 2^k とする。
像 t in Im(T) に対して、多重度 mult(t) = |T^{-1}(t)| と定義する。
N(m, k) = |{t : mult(t) = m}| とするとき:

1) k 奇数の場合:
   再帰: N(m, k) = N(m-1, k-2)  (m >= 2)
   基底: N(1, k) = 9 * 2^{k-5}  (k >= 5), N(1, 3) = 2
   最大多重度: (k-1)/2

2) k 偶数の場合:
   N(1, k) = (7 * 2^{k-4} - 4) / 3  (k >= 4)
   N(2, k) = (2^{k-2} + 2) / 3       (k >= 4)
   N(m, k) = N(m-2, k-3)             (m >= 3)
   最大多重度: k/2

3) 像の総数:
   k奇数: |Im(T)| = 3 * 2^{k-3}
   k偶数: |Im(T)| = (7 * 2^{k-3} - 2) / 3

4) 整合性の検証:
   sum_m m * N(m,k) = 2^{k-1} (奇数残基の総数) が成立すべき
""")

# 整合性検証: sum_m m * N(m,k) = 2^{k-1}
print("整合性検証: sum_m m * N(m,k) = 2^{k-1}")
for k in range(3, 20):
    total = sum(m * N_formula(m, k) for m in range(1, k+1) if N_formula(m, k) and N_formula(m, k) > 0)
    expected = 2**(k-1)
    match = "OK" if total == expected else f"NG (got {total})"
    print(f"  k={k:2d}: sum = {total:6d}, 2^{k-1} = {expected:6d}, {match}")

# 別の整合性: sum_m N(m,k) = |Im(T)|
print("\n整合性検証: sum_m N(m,k) = |Im(T)|")
for k in range(3, 20):
    total_images = sum(N_formula(m, k) for m in range(1, k+1) if N_formula(m, k) and N_formula(m, k) > 0)
    if k % 2 == 1:
        expected = 3 * 2**(k-3)
    else:
        expected = (7 * 2**(k-3) - 2) // 3
    match = "OK" if total_images == expected else f"NG (got {total_images})"
    print(f"  k={k:2d}: sum = {total_images:6d}, |Im| = {expected:6d}, {match}")
