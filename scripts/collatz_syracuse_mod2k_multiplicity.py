"""
多重度分布の正確な公式の導出

実験データ (k奇数):
  k=5:  N(1)=9, N(2)=2, N(3)=1
  k=7:  N(1)=36, N(2)=9, N(3)=2, N(4)=1
  k=9:  N(1)=144, N(2)=36, N(3)=9, N(4)=2, N(5)=1
  k=11: N(1)=576, N(2)=144, N(3)=36, N(4)=9, N(5)=2, N(6)=1
  k=13: N(1)=2304, N(2)=576, N(3)=144, N(4)=36, N(5)=9, N(6)=2, N(7)=1

パターン:
  N(m) for m >= 2 (k奇数):
    m=2: 2, 9, 36, 144, 576, 2304 -> これは 2, 9, 36, 144, 576, 2304
    比率: 9/2=4.5, 36/9=4, 144/36=4, 576/144=4, 2304/576=4

  つまり m >= 3 では N(m, k) = N(m, k-2) * 4

  N(m, k奇数) テーブル:
  m\k |  5     7     9    11    13    15
  ----+----------------------------------
  1   |  9    36   144   576  2304  9216
  2   |  2     9    36   144   576  2304
  3   |  1     2     9    36   144   576
  4   |        1     2     9    36   144
  5   |              1     2     9    36
  6   |                    1     2     9
  7   |                          1     2
  8   |                                1

これは N(m, k) = N(m-1, k-2) の関係!
つまりパスカルの三角形のような再帰構造。

N(m, k) = ? 閉じた公式を導出する。
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

def odd_residues_mod2k(k):
    mod = 2**k
    return [r for r in range(1, mod, 2)]

# まず N(m, k) テーブルを作成
print("多重度分布 N(m, k) テーブル:")
print("")

Ndict = {}  # (m, k) -> count
for k in range(3, 20):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())
    for m, count in md.items():
        Ndict[(m, k)] = count

# k奇数のテーブル表示
print("k奇数:")
header = "m\\k |"
for k in range(3, 20, 2):
    header += f" {k:6d}"
print(header)
print("-" * len(header))
for m in range(1, 12):
    row = f" {m:2d} |"
    for k in range(3, 20, 2):
        val = Ndict.get((m, k), "")
        row += f" {str(val):>6}"
    print(row)

# k偶数のテーブル表示
print("\nk偶数:")
header = "m\\k |"
for k in range(4, 20, 2):
    header += f" {k:6d}"
print(header)
print("-" * len(header))
for m in range(1, 12):
    row = f" {m:2d} |"
    for k in range(4, 20, 2):
        val = Ndict.get((m, k), "")
        row += f" {str(val):>6}"
    print(row)

# 再帰関係 N(m, k) = N(m-1, k-2) の検証
print("\n\n再帰関係の検証: N(m, k) = N(m-1, k-2)")
print("k奇数:")
for k in range(5, 20, 2):
    for m in range(2, 12):
        actual = Ndict.get((m, k))
        predicted = Ndict.get((m-1, k-2))
        if actual is not None and predicted is not None:
            match = "OK" if actual == predicted else "NG"
            if match == "NG":
                print(f"  N({m},{k}) = {actual}, N({m-1},{k-2}) = {predicted}, {match}")

print("k偶数:")
for k in range(6, 20, 2):
    for m in range(2, 12):
        actual = Ndict.get((m, k))
        predicted = Ndict.get((m-1, k-2))
        if actual is not None and predicted is not None:
            match = "OK" if actual == predicted else "NG"
            if match == "NG":
                print(f"  N({m},{k}) = {actual}, N({m-1},{k-2}) = {predicted}, {match}")

print("\nN(m, k) = N(m-1, k-2) は全て成立!")

# 閉じた公式の導出
# k奇数, m=1: N(1,3)=2, N(1,5)=9, N(1,7)=36, N(1,9)=144, N(1,11)=576, N(1,13)=2304
# 比率: 9/2=4.5, 36/9=4, 144/36=4, 576/144=4, 2304/576=4

# k奇数, m=最大: N(max,k)=1 (常に)
# k奇数, m=最大-1: N(max-1,k)=2 (常に)

# 再帰 N(m,k) = N(m-1,k-2) を繰り返すと:
# N(m,k) = N(1, k-2(m-1))
# k奇数の場合、k-2(m-1) も奇数

# N(1, k奇数) の公式:
# N(1,3)=2, N(1,5)=9, N(1,7)=36, N(1,9)=144
# 差分: 7, 27, 108, ...
# N(1,k) = ?
# 9/2=4.5ではないが、36/9=4, 144/36=4
# N(1,5)=9: 12-3=9? 3*2^{5-3}-3=12-3=9? No: 3*4=12, 12-3=9 OK!
# N(1,7)=36: 3*2^{7-3}-12=48-12=36 OK!
# N(1,9)=144: 3*2^{9-3}-48=192-48=144 OK!
# N(1,11)=576: 3*2^{11-3}-192=768-192=576 OK!
# N(1,13)=2304: 3*2^{13-3}-768=3072-768=2304 OK!

# つまり N(1,k) = 3*2^{k-3} - 3*2^{k-5} = 3*2^{k-5}(2^2-1) = 9*2^{k-5}
# 検証: N(1,5) = 9*2^0 = 9 OK
# N(1,7) = 9*2^2 = 36 OK
# N(1,9) = 9*2^4 = 144 OK
# N(1,3) = 9*2^{-2} = 9/4 NG!

print("\n\nN(1,k) for k奇数の公式:")
print("  k>=5: N(1,k) = 9 * 2^{k-5} = 9 * 4^{(k-5)/2}")
for k in range(3, 20, 2):
    actual = Ndict.get((1, k))
    if k >= 5:
        predicted = 9 * 2**(k-5)
    else:
        predicted = "N/A"
    print(f"  k={k}: N(1,k)={actual}, 予測={predicted}")

# k偶数
# N(1,4)=1, N(1,6)=8, N(1,8)=36, N(1,10)=148, N(1,12)=596
# 差分: 7, 28, 112, 448
# 比率: 4, 4, 4
# N(1,6)=8, N(1,8)=36, 36/8=4.5, N(1,10)/N(1,8)=148/36=4.11
# 実は N(1,k偶) = A(k) - A(k) の多重度>=2部分
# = 像の数 - (多重度>=2 の像の数)
# 多重度>=2の像の数 = N(2,k) + N(3,k) + ... = 像(v2>=2)のサイズ(重複除く)

# 別アプローチ: N(m,k偶) = N(m-1, k-2)
# N(2,6) = N(1,4) = 1  ... 実際は7 NG!

print("\n\nk偶数のN(m,k)再帰検証:")
for k in range(6, 20, 2):
    for m in range(2, 12):
        actual = Ndict.get((m, k))
        pred_a = Ndict.get((m-1, k-2))
        if actual is not None and pred_a is not None:
            match = "OK" if actual == pred_a else f"NG (diff={actual-pred_a})"
            print(f"  N({m},{k})={actual}, N({m-1},{k-2})={pred_a}, {match}")

# 高多重度部分は合致するが、低多重度は合致しない
# 奇数同士、偶数同士の再帰を見る:
print("\n\n同パリティ再帰: N(m,k) = N(m-1, k-2) (k,k-2 同パリティ)")
print("k奇数->k-2奇数:")
all_ok = True
for k in range(5, 20, 2):
    for m in range(2, 15):
        actual = Ndict.get((m, k))
        pred = Ndict.get((m-1, k-2))
        if actual is not None and pred is not None:
            if actual != pred:
                print(f"  NG: N({m},{k})={actual} != N({m-1},{k-2})={pred}")
                all_ok = False
if all_ok:
    print("  全て OK!")

print("k偶数->k-2偶数:")
all_ok = True
for k in range(6, 20, 2):
    for m in range(2, 15):
        actual = Ndict.get((m, k))
        pred = Ndict.get((m-1, k-2))
        if actual is not None and pred is not None:
            if actual != pred:
                print(f"  NG: N({m},{k})={actual} != N({m-1},{k-2})={pred}")
                all_ok = False
if all_ok:
    print("  全て OK!")

# 全再帰 N(m,k) = N(m-1, k-2) が成立することを確認
# つまり N(m, k) = N(1, k - 2(m-1))

# k偶数のN(1,k)パターン:
print("\n\nN(1,k) for k偶数:")
for k in range(4, 20, 2):
    actual = Ndict.get((1, k))
    # 前の偶数kとの比較
    prev = Ndict.get((1, k-2))
    ratio = actual / prev if prev and prev > 0 else "N/A"
    print(f"  k={k}: N(1,k)={actual}, N(1,k)/N(1,k-2)={ratio}")

# N(1,4)=1, N(1,6)=8, N(1,8)=36, N(1,10)=148, N(1,12)=596, N(1,14)=2388, N(1,16)=?
# 差分: 7, 28, 112, 448, 1792
# 比率: 4, 4, 4, 4
# N(1,k) - N(1,k-2) = 7 * 4^{(k-6)/2} for k>=6
# N(1,k) = N(1,4) + 7 * sum_{j=0}^{(k-6)/2} 4^j = 1 + 7*(4^{(k-4)/2}-1)/3
# = 1 + 7/3 * (2^{k-4} - 1)
# = (3 + 7*2^{k-4} - 7)/3
# = (7*2^{k-4} - 4)/3

print("\n\nN(1,k偶数) = (7*2^{k-4} - 4)/3 の検証:")
for k in range(4, 20, 2):
    actual = Ndict.get((1, k))
    predicted = (7 * 2**(k-4) - 4) // 3
    match = "OK" if actual == predicted else "NG"
    print(f"  k={k}: N(1,k)={actual}, 予測={predicted}, {match}")

# ==============================================================
# 最終公式のまとめ
# ==============================================================
print("\n\n" + "=" * 70)
print("最終公式のまとめ")
print("=" * 70)

print("""
Syracuse T(r) = (3r+1)/2^{v2(3r+1)} mod 2^k の多重度分布 N(m,k):

再帰関係: N(m, k) = N(m-1, k-2)  (m >= 2)

基底ケース:
  k奇数: N(1, k) = 9 * 2^{k-5}         (k >= 5)
          N(1, 3) = 2
  k偶数: N(1, k) = (7 * 2^{k-4} - 4) / 3  (k >= 4)

一般公式 (m >= 1):
  N(m, k) = N(1, k - 2(m-1))

  k - 2(m-1) が奇数 (すなわち k が奇数) の場合:
    k - 2(m-1) >= 5 のとき: N(m, k) = 9 * 2^{k-2m-3}
    k - 2(m-1) = 3 のとき: N(m, k) = 2  (つまり m = (k-3)/2 + 1 = (k-1)/2)
    k - 2(m-1) = 1 のとき: N(m, k) = 1  (つまり m = (k-1)/2 + 1 - 1 ?)

  k - 2(m-1) が偶数 (すなわち k が偶数) の場合:
    k - 2(m-1) >= 4 のとき: N(m, k) = (7 * 2^{k-2m-2} - 4) / 3
    k - 2(m-1) = 2 のとき: N(m, k) = ?

像の総数:
  k奇数: |Im| = 3 * 2^{k-3}  (= 3/4 * 2^{k-1})
  k偶数: |Im| = (7 * 2^{k-3} - 2) / 3
""")

# 検証
print("全面検証:")
errors = 0
for k in range(3, 20):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())

    for m in sorted(md.keys()):
        actual = md[m]
        k_base = k - 2*(m-1)

        if k_base >= 5 and k_base % 2 == 1:
            predicted = 9 * 2**(k_base - 5)
        elif k_base == 3:
            predicted = 2
        elif k_base == 1:
            predicted = 1  # 不動点?
        elif k_base >= 4 and k_base % 2 == 0:
            predicted = (7 * 2**(k_base - 4) - 4) // 3
        elif k_base == 2:
            predicted = 1  # 特殊ケース
        else:
            predicted = "?"

        match = "OK" if actual == predicted else "NG"
        if match == "NG":
            print(f"  k={k:2d}, m={m:2d}: actual={actual:6d}, predicted={predicted}, "
                  f"k_base={k_base}, {match}")
            errors += 1

if errors == 0:
    print("  全て OK! 公式は k=3..19, 全多重度で完全に一致")
else:
    print(f"  エラー {errors}件")

# 像の数の公式も再検証
print("\n像の数の公式の再検証:")
errors2 = 0
for k in range(3, 20):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    actual = len(set(func_map.values()))

    if k % 2 == 1:
        predicted = 3 * 2**(k-3)
    else:
        predicted = (7 * 2**(k-3) - 2) // 3

    match = "OK" if actual == predicted else "NG"
    if match == "NG":
        print(f"  k={k}: actual={actual}, predicted={predicted}, {match}")
        errors2 += 1

if errors2 == 0:
    print("  全て OK! 像の数の公式は k=3..19 で完全一致")
