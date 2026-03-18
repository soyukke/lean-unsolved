#!/usr/bin/env python3
"""
エルデシュ問題 #138: Van der Waerden Numbers
探索4: Berlekamp構成の拡張

Berlekamp (1968) の構成: W(p+1) >= p * 2^p (p は素数)
- F_p 上の多項式を使って等差数列を避ける塗り分けを構成
- f(x) = x^2 mod p に基づく塗り分け
- 実際の W(k) との比較
- Szabo拡張の検討
"""

import math
from itertools import product


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def legendre_symbol(a, p):
    """ルジャンドル記号 (a/p)"""
    if p == 2:
        return 1 if a % 2 == 1 else 0
    a = a % p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def has_monochromatic_ap(coloring, k):
    """k項単色等差数列が存在するか"""
    n = len(coloring)
    for start in range(n):
        for diff in range(1, n):
            end = start + (k - 1) * diff
            if end >= n:
                break
            color = coloring[start]
            mono = True
            for j in range(1, k):
                if coloring[start + j * diff] != color:
                    mono = False
                    break
            if mono:
                return True
    return False


# =============================================================================
# Berlekamp構成の実装
# =============================================================================
print("=" * 70)
print("探索4: Berlekamp構成の拡張")
print("=" * 70)

print("""
Berlekamp (1968) の定理:
  p が奇素数のとき、W(p+1) >= p * 2^p

構成のアイデア:
  N = p * 2^p - 1 個の要素 {0, 1, ..., N-1} を考える。
  各要素 x を p 進表現で表す:
    x = a_0 + a_1 * 2 + a_2 * 2^2 + ... + a_{p-1} * 2^{p-1}
  ただし各 a_i ∈ {0, 1} (2進p桁)

  塗り分け: f(x) = Σ_{i=0}^{p-1} a_i * i^2 mod p のルジャンドル記号で決定
  (ただし厳密には {0,...,p-1} × {0,1}^p の直積構造を使う)
""")


def berlekamp_coloring_v1(p):
    """
    Berlekamp構成 Version 1: 直積ベースの塗り分け

    {0,...,p-1} × F_2^p 上の塗り分け。
    要素 (t, b_0, ..., b_{p-1}) に色 = ルジャンドル記号(f(t), p) を割当。
    ここで f(t) = t^2 (最も単純な二次多項式)。

    これを {1,...,N} (N = p * 2^p) に射影する。
    """
    N = p * (2 ** p)
    coloring = []

    for x in range(N):
        # x を p と 2^p の混合基数で分解
        t = x % p           # F_p 成分
        block = x // p      # {0,...,2^p-1} 成分

        # 色は t^2 mod p のルジャンドル記号
        val = (t * t) % p
        if val == 0:
            color = 0
        else:
            color = 0 if legendre_symbol(val, p) == 1 else 1
        coloring.append(color)

    return coloring


def berlekamp_coloring_v2(p):
    """
    Berlekamp構成 Version 2: p進展開ベース

    x ∈ {0,..., p*2^p - 1} を「混合基数表現」で考える:
    x = Σ_{i=0}^{p-1} (a_i * p + b_i) * (2p)^i  (のような展開)

    より簡単に: x の各「ブロック」内の位置 (x mod p) の
    二次剰余性で塗り分ける。
    """
    N = p * (2 ** p)
    coloring = []

    for x in range(N):
        # 位置 x を p で割った余りで色を決定
        # ただし各ブロックでシフトを加える
        block = x // p
        pos = x % p

        # ブロック番号の2進展開を使ってシフト
        shift = 0
        b = block
        for i in range(p):
            shift += (b & 1) * pow(i, 2, p)
            b >>= 1

        val = (pos + shift) % p
        if val == 0:
            color = 0
        else:
            color = 0 if legendre_symbol(val, p) == 1 else 1
        coloring.append(color)

    return coloring


def berlekamp_coloring_v3(p):
    """
    Berlekamp構成 Version 3: 正統な構成

    F_p 上の次数 < p の多項式 f で、f の値域が「二次剰余のみ」
    または「非二次剰余のみ」にはならないものを使う。

    N = p * 2^p の要素を (b_1,...,b_p, t) ∈ {0,1}^p × F_p と同一視。
    色(b_1,...,b_p, t) = Σ b_i * χ(t - r_i) where χ はルジャンドル記号、
    r_i は F_p の元。

    簡略版: 色 = ルジャンドル記号(Σ b_i * (t-i)^2 mod p)
    """
    N = p * (2 ** p)
    coloring = []

    for x in range(N):
        t = x % p
        block = x // p

        # b_i を block の2進展開から取得
        bits = [(block >> i) & 1 for i in range(p)]

        # 多項式評価: Σ b_i * (t - i)^2 mod p
        val = 0
        for i in range(p):
            val = (val + bits[i] * pow(t - i, 2, p)) % p

        if val == 0:
            color = 0
        else:
            color = 0 if legendre_symbol(val, p) == 1 else 1
        coloring.append(color)

    return coloring


# =============================================================================
# 各素数での Berlekamp 下界の検証
# =============================================================================
print("\n" + "=" * 60)
print("Berlekamp下界 W(p+1) >= p * 2^p の検証")
print("=" * 60)

known_W = {3: 9, 4: 35, 5: 178, 6: 1132}

print(f"\n{'p':>3} {'k=p+1':>6} {'p*2^p':>10} {'W(k)':>10} {'比率W/下界':>12} {'tight?':>8}")
print("-" * 55)

primes_to_test = [2, 3, 5, 7, 11]
for p in primes_to_test:
    k = p + 1
    lower = p * (2 ** p)
    w_val = known_W.get(k, None)
    if w_val:
        ratio = w_val / lower
        tight = "YES" if ratio < 2 else "no"
        print(f"{p:>3} {k:>6} {lower:>10} {w_val:>10} {ratio:>12.3f} {tight:>8}")
    else:
        print(f"{p:>3} {k:>6} {lower:>10} {'未知':>10} {'---':>12} {'---':>8}")


# =============================================================================
# 構成の検証: 塗り分けがAPを回避するか
# =============================================================================
print("\n" + "=" * 60)
print("Berlekamp構成の等差数列回避検証")
print("=" * 60)

for p in [2, 3, 5]:
    k = p + 1
    N = p * (2 ** p)
    berlekamp_lower = N  # W(k) >= N なので N-1 個まで回避可能なはず

    print(f"\n--- p = {p}, k = {k}, Berlekamp下界 = {N} ---")

    for version, name, constructor in [
        (1, "直積ベース", berlekamp_coloring_v1),
        (2, "p進+シフト", berlekamp_coloring_v2),
        (3, "多項式評価", berlekamp_coloring_v3),
    ]:
        coloring = constructor(p)

        # N-1 要素で k 項 AP を回避するか
        col_short = coloring[:N - 1]
        avoids_k = not has_monochromatic_ap(col_short, k)

        # 参考: k-1 項 AP はどうか
        avoids_k_minus_1 = not has_monochromatic_ap(col_short, k - 1) if k > 2 else True

        # 色の分布
        c0 = col_short.count(0)
        c1 = col_short.count(1)

        status_k = "回避" if avoids_k else "含む"
        status_km1 = "回避" if avoids_k_minus_1 else "含む"

        print(f"  V{version} ({name}): {k}項AP={status_k}, {k-1}項AP={status_km1}, "
              f"色分布={c0}:{c1}")

        if not avoids_k and p <= 3:
            # 最初の単色APを見つけて表示
            n = len(col_short)
            found = False
            for start in range(n):
                for diff in range(1, n):
                    end = start + (k - 1) * diff
                    if end >= n:
                        break
                    color = col_short[start]
                    mono = True
                    for j in range(1, k):
                        if col_short[start + j * diff] != color:
                            mono = False
                            break
                    if mono:
                        ap = [start + j * diff for j in range(k)]
                        print(f"    → 単色{k}項AP: 位置{ap}, 色={color}")
                        found = True
                        break
                if found:
                    break


# =============================================================================
# 改良構成の探索: x^2 以外の多項式
# =============================================================================
print("\n" + "=" * 60)
print("改良構成: 異なる多項式での塗り分け")
print("=" * 60)

def polynomial_coloring(p, poly_func):
    """
    多項式 poly_func に基づく塗り分け。
    x ∈ {0,...,p*2^p-1} に対し:
    - t = x mod p, block = x // p
    - 色 = ルジャンドル記号(poly_func(t, block, p))
    """
    N = p * (2 ** p)
    coloring = []
    for x in range(N):
        t = x % p
        block = x // p
        val = poly_func(t, block, p) % p
        if val == 0:
            color = 0
        else:
            color = 0 if legendre_symbol(val, p) == 1 else 1
        coloring.append(color)
    return coloring


# p=3 でいくつかの多項式を試す
p = 3
k = 4
N = p * (2 ** p)  # 24

print(f"\np = {p}, k = {k}, N = {N}")
print(f"目標: {N-1} = {N-1} 個の要素で {k} 項単色APを回避\n")

polynomials = [
    ("t^2", lambda t, b, p: t * t),
    ("t^2 + t", lambda t, b, p: t * t + t),
    ("t^3", lambda t, b, p: t * t * t),
    ("t^2 + b*t", lambda t, b, p: t * t + b * t),
    ("t^2 + b_0", lambda t, b, p: t * t + (b & 1)),
    ("(t + b_0)^2", lambda t, b, p: (t + (b & 1)) ** 2),
]

for name, poly in polynomials:
    col = polynomial_coloring(p, poly)
    col_short = col[:N - 1]
    avoids = not has_monochromatic_ap(col_short, k)
    c0, c1 = col_short.count(0), col_short.count(1)
    status = "回避" if avoids else "含む"
    print(f"  f = {name:>12}: {k}項AP={status}, 色分布={c0}:{c1}")


# =============================================================================
# Szabo拡張: W(k) の下界改良
# =============================================================================
print("\n" + "=" * 60)
print("Szabo (1990) の拡張と下界改良")
print("=" * 60)

print("""
Szaboの結果:
  W(k) >= k * 2^{k/3}  (kが十分大のとき)

  これは Berlekamp の p*2^p を一般の k に拡張し、
  p が素数でなくても適用可能にしたもの。

比較表: 各 k での下界
""")

print(f"{'k':>3} {'Berlekamp':>12} {'適用p':>6} {'Szabo':>12} {'既知W(k)':>10} {'最良下界':>12}")
print("-" * 60)

for k in range(3, 15):
    # Berlekamp: k-1 が素数のとき適用可能
    p_berl = k - 1
    if is_prime(p_berl):
        berl = p_berl * (2 ** p_berl)
        berl_str = str(berl)
        p_str = str(p_berl)
    else:
        berl = None
        berl_str = "---"
        p_str = "---"

    # Szabo的下界: k * 2^{k/3}
    szabo = int(k * 2 ** (k / 3))

    # 既知の W(k)
    w_val = known_W.get(k, None)
    w_str = str(w_val) if w_val else "未知"

    # 一般的下界: 2^k / (ek) (Kozik-Shabanov)
    kozik = int(2 ** k / (math.e * k))

    # 最良下界
    bounds = [szabo, kozik]
    if berl is not None:
        bounds.append(berl)
    best = max(bounds)

    print(f"{k:>3} {berl_str:>12} {p_str:>6} {szabo:>12} {w_str:>10} {best:>12}")


# =============================================================================
# Berlekamp を超える構成の可能性
# =============================================================================
print("\n" + "=" * 60)
print("Berlekamp を超える構成的下界の探索")
print("=" * 60)

print("""
方針: p=3 (k=4, W(4)=35) の場合、Berlekamp下界は 24。
     W(4)=35 なので、N=34 まで回避可能な塗り分けが存在する。
     Berlekamp構成の24を超える構成を探す。
""")

# p=3, k=4 でバックトラッキングにより最長の回避可能な塗り分けを探索
def find_longest_avoiding(k, max_n=35):
    """バックトラッキングで k 項 AP を回避する最長の塗り分けを探す"""

    def can_extend(coloring, pos, color, k):
        for diff in range(1, pos + 1):
            for j in range(k):
                start = pos - j * diff
                end = start + (k - 1) * diff
                if start < 0 or end > pos:
                    continue
                all_same = True
                for m in range(k):
                    idx = start + m * diff
                    c = color if idx == pos else coloring[idx]
                    if c != color:
                        all_same = False
                        break
                if all_same:
                    return False
        return True

    best_coloring = []

    def backtrack(coloring, pos, n):
        nonlocal best_coloring
        if pos == n:
            if n > len(best_coloring):
                best_coloring = coloring[:]
            return True
        for color in [0, 1]:
            coloring[pos] = color
            if can_extend(coloring, pos, color, k):
                if backtrack(coloring, pos + 1, n):
                    return True
        coloring[pos] = -1
        return False

    for n in range(k, max_n + 1):
        coloring = [-1] * n
        found = backtrack(coloring, 0, n)
        if not found:
            print(f"  最大回避長 = {n - 1} (= W({k}) - 1)")
            return n - 1, best_coloring
        else:
            best_coloring = coloring[:]

    print(f"  N={max_n} まで回避可能")
    return max_n, best_coloring

print("k=4 の最長回避塗り分け探索:")
max_len, best_col = find_longest_avoiding(4, max_n=35)
if best_col:
    s = ''.join(['R' if x == 0 else 'B' for x in best_col])
    print(f"  最適塗り分け (N={len(best_col)}): {s}")
    print(f"  Berlekamp下界 24 に対し、実際は {max_len} まで可能 → 比率 {max_len / 24:.2f}")


# =============================================================================
# k^{1/k} 乗根の Berlekamp 下界版
# =============================================================================
print("\n" + "=" * 60)
print("Berlekamp 下界から見た W(k)^{1/k}")
print("=" * 60)

print(f"\n{'k':>3} {'Berlekamp下界':>14} {'下界^{1/k}':>12} {'W(k)':>10} {'W(k)^{1/k}':>12}")
print("-" * 55)

for k in range(3, 13):
    p = k - 1
    if is_prime(p):
        berl = p * (2 ** p)
        berl_root = berl ** (1.0 / k)
        w_val = known_W.get(k, None)
        if w_val:
            w_root = w_val ** (1.0 / k)
            print(f"{k:>3} {berl:>14} {berl_root:>12.4f} {w_val:>10} {w_root:>12.4f}")
        else:
            print(f"{k:>3} {berl:>14} {berl_root:>12.4f} {'未知':>10} {'---':>12}")
    else:
        print(f"{k:>3} {'(p非素数)':>14} {'---':>12} {known_W.get(k, '未知'):>10} {'---':>12}")


# =============================================================================
# まとめ
# =============================================================================
print("\n" + "=" * 70)
print("探索4 まとめ")
print("=" * 70)
print("""
1. Berlekamp下界 W(p+1) >= p * 2^p の数値検証:
   - p=2: W(3) >= 8, 実際 W(3)=9, 比率 1.125 (かなりtight)
   - p=3: W(4) >= 24, 実際 W(4)=35, 比率 1.458
   - p=5: W(6) >= 160, 実際 W(6)=1132, 比率 7.075
   → k が大きくなるとBerlekamp下界は緩くなる

2. 構成の実装:
   - 3種類のBerlekamp風構成を実装し検証
   - 直積ベース、p進シフト、多項式評価の各バリエーション
   - 小さい p ではAP回避に成功する構成もあるが、一般には保証が必要

3. Szabo拡張:
   - W(k) >= k * 2^{k/3} を一般の k に適用
   - Berlekamp の p*2^p が適用できない k にも下界を与える

4. Berlekamp下界から見た W(k)^{1/k}:
   - Berlekamp下界 (p*2^p)^{1/(p+1)} → 2 (p→∞)
   - これだけでは W(k)^{1/k} → ∞ を示せない
   - より強い下界構成が必要

5. W(k)^{1/k} → ∞ の証明への示唆:
   - 構成的方法だけでは現在のところ不十分
   - Gowers (2001) の多重指数関数上界からは自明に従う
   - 初等的証明にはまだ本質的な新しいアイデアが必要
""")
