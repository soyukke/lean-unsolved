"""
k偶数の N(2,k) の正確な公式を導出する。

N(2,k偶): 2, 7, 26, 102, 406, 1622, 6486, 25942
漸化式: N(2,4)=2, N(2,6)=7, N(2,k+2) = 4*N(2,k) - 2 (k>=6)

4*2-2=6 NG(7), 4*7-2=26 OK
つまり k=6 が特殊。

修正漸化式: N(2,k+2) = 4*N(2,k) - 2  for k >= 6
N(2,6)=7 を初期値として:
  N(2,8) = 4*7-2 = 26 OK
  N(2,10) = 4*26-2 = 102 OK
  ...

閉じた公式: a_n = 4*a_{n-1} - 2, a_0 = 7 (n = (k-6)/2)
特殊解 c: c=4c-2 => c=2/3
一般解: a_n - 2/3 = (7-2/3)*4^n = (19/3)*4^n
a_n = (19/3)*4^n + 2/3 = (19*4^n + 2)/3

検証: n=0 (k=6): (19+2)/3=21/3=7 OK
n=1 (k=8): (19*4+2)/3=78/3=26 OK
n=2 (k=10): (19*16+2)/3=306/3=102 OK

4^n = 4^{(k-6)/2} = 2^{k-6}

N(2, k偶) = (19*2^{k-6} + 2) / 3  for k >= 6
N(2, 4) = 2 (特殊)
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
for k in range(3, 22):
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

# N(2, k偶) の公式検証
print("N(2, k偶) = (19*2^{k-6} + 2) / 3  for k >= 6")
print("N(2, 4) = 2")
for k in range(4, 22, 2):
    actual = Ndict.get((2, k))
    if k == 4:
        predicted = 2
    elif k >= 6:
        predicted = (19 * 2**(k-6) + 2) // 3
    else:
        predicted = "N/A"
    match = "OK" if actual == predicted else "NG"
    print(f"  k={k}: N(2,k)={actual}, predicted={predicted}, {match}")

# N(1, k偶) の公式も再検証
print("\nN(1, k偶) = (7*2^{k-4} - 4) / 3")
for k in range(4, 22, 2):
    actual = Ndict.get((1, k))
    predicted = (7 * 2**(k-4) - 4) // 3
    match = "OK" if actual == predicted else "NG"
    print(f"  k={k}: N(1,k)={actual}, predicted={predicted}, {match}")


# ==============================================================
# 完全な公式
# ==============================================================
def N_formula(m, k):
    """多重度 m の像の数の正確な公式"""
    if k % 2 == 1:  # k 奇数
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
                return 0
            return (7 * 2**(k-4) - 4) // 3
        elif m == 2:
            if k == 4:
                return 2
            if k >= 6:
                return (19 * 2**(k-6) + 2) // 3
            return 0
        else:
            # m >= 3: N(m, k偶) = N(m-2, k-3)
            return N_formula(m-2, k-3)
    return 0

print("\n\n" + "=" * 70)
print("完全検証 (k=3..21)")
print("=" * 70)

errors = 0
for k in range(3, 22):
    mod = 2**k
    residues = [r for r in range(1, mod, 2)]
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())

    for m_actual in sorted(md.keys()):
        actual = md[m_actual]
        predicted = N_formula(m_actual, k)
        match = "OK" if actual == predicted else "NG"
        if match == "NG":
            print(f"  k={k:2d}, m={m_actual:2d}: actual={actual:7d}, predicted={predicted:7d}, {match}")
            errors += 1

    # 公式が0だが実データにない m のチェック
    max_m = max(md.keys())
    for m_check in range(max_m + 1, max_m + 3):
        pred = N_formula(m_check, k)
        if pred > 0:
            print(f"  k={k:2d}, m={m_check:2d}: 公式は{pred}だが実データなし")
            errors += 1

if errors == 0:
    print("  全て OK!")
else:
    print(f"  エラー {errors}件")

# 整合性検証
print("\n\n整合性検証 1: sum_m m * N(m,k) = 2^{k-1}")
for k in range(3, 22):
    total = 0
    for m in range(1, k+1):
        n = N_formula(m, k)
        total += m * n
    expected = 2**(k-1)
    match = "OK" if total == expected else f"NG (sum={total}, exp={expected})"
    print(f"  k={k:2d}: {match}")

print("\n整合性検証 2: sum_m N(m,k) = |Im|")
for k in range(3, 22):
    total = 0
    for m in range(1, k+1):
        n = N_formula(m, k)
        total += n
    if k % 2 == 1:
        expected = 3 * 2**(k-3)
    else:
        expected = (7 * 2**(k-3) - 2) // 3
    match = "OK" if total == expected else f"NG (sum={total}, exp={expected})"
    print(f"  k={k:2d}: {match}")

# ==============================================================
# 最終まとめ
# ==============================================================
print("\n\n" + "=" * 70)
print("最終定理")
print("=" * 70)
print("""
定理 (Syracuse写像 mod 2^k の像の多重度分布):

T: (Z/2^kZ)^* -> (Z/2^kZ)^* を T(r) = (3r+1)/2^{v2(3r+1)} mod 2^k とし、
N(m,k) = |{t in Im(T) : |T^{-1}(t)| = m}| とする。

【k奇数の場合】
  再帰: N(m, k) = N(m-1, k-2)     (m >= 2)
  基底: N(1, 3) = 2
         N(1, k) = 9 * 2^{k-5}     (k >= 5)
  最大多重度: (k-1)/2
  像の総数: |Im(T)| = 3 * 2^{k-3}  (= 3/4 の占有率)

【k偶数の場合】
  N(1, k) = (7 * 2^{k-4} - 4) / 3  (k >= 4)
  N(2, 4) = 2
  N(2, k) = (19 * 2^{k-6} + 2) / 3  (k >= 6)
  N(m, k) = N(m-2, k-3)             (m >= 3)
  最大多重度: k/2
  像の総数: |Im(T)| = (7 * 2^{k-3} - 2) / 3  (-> 7/12 に収束)

【補助定理】
  v2層別全単射: v2(3r+1)=j のとき、
  r -> (3r+1)/2^j mod 2^{k-j} は奇数残基 mod 2^{k-j} への全単射。

【コラッツ予想への示唆】
  唯一の不動点は r=1。
  k<=9 で非自明サイクルなし。k=10,11,12 で mod 2^k のみの偽サイクル出現
  (実際のコラッツでは1に収束)。
  k=13-17 で再び非自明サイクルなし。
  テール要素が全体の 97%+ を占め、全ての残基が1に向かう流れを反映。
""")
