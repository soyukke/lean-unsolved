"""
Syracuse写像の mod 2^k 上の置換構造の分析

奇数 mod 2^k 上で Syracuse写像 T がどのような置換を誘導するかを k=3..12 で調べる。
- 置換の巡回分解（巡回型）
- 位数
- 符号（偶置換/奇置換）
- 全射性・全単射性
- k依存性の分析
"""

from math import gcd
from functools import reduce
from collections import Counter
import json

def syracuse(n):
    """Syracuse関数: T(n) = (3n+1) / 2^v2(3n+1)"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def syracuse_mod(n, mod):
    """Syracuse関数を mod 上で計算"""
    return syracuse(n) % mod

def get_odd_residues(k):
    """mod 2^k の奇数残基類のリスト"""
    mod = 2**k
    return [i for i in range(1, mod, 2)]

def compute_permutation(k):
    """k に対して、奇数 mod 2^k 上の Syracuse写像による置換を計算"""
    mod = 2**k
    odds = get_odd_residues(k)
    odd_set = set(odds)

    perm = {}
    for n in odds:
        img = syracuse_mod(n, mod)
        perm[n] = img

    return perm

def check_bijection(perm, odds):
    """置換が全単射かチェック"""
    image = set(perm.values())
    domain = set(odds)
    is_surjective = image == domain
    is_injective = len(image) == len(domain)
    return is_surjective and is_injective, is_surjective, is_injective

def cycle_decomposition(perm):
    """置換の巡回分解"""
    visited = set()
    cycles = []

    for start in sorted(perm.keys()):
        if start in visited:
            continue
        cycle = []
        current = start
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = perm[current]
        if len(cycle) > 0:
            cycles.append(tuple(cycle))

    return cycles

def cycle_type(cycles):
    """巡回型（各巡回の長さのソート済みリスト）"""
    lengths = sorted([len(c) for c in cycles], reverse=True)
    return tuple(lengths)

def permutation_order(cycles):
    """置換の位数（巡回長のLCM）"""
    lengths = [len(c) for c in cycles]
    if not lengths:
        return 1
    result = lengths[0]
    for l in lengths[1:]:
        result = result * l // gcd(result, l)
    return result

def permutation_sign(cycles):
    """置換の符号: +1 = 偶置換, -1 = 奇置換"""
    # 各 m-巡回は (m-1) 個の互換に分解 → 符号は (-1)^(m-1)
    sign = 1
    for c in cycles:
        if len(c) % 2 == 0:  # 偶数長の巡回は奇置換
            sign *= -1
    return sign

def analyze_k(k):
    """k に対する完全な分析"""
    mod = 2**k
    odds = get_odd_residues(k)
    n_odds = len(odds)  # = 2^(k-1)

    perm = compute_permutation(k)
    is_bij, is_surj, is_inj = check_bijection(perm, odds)

    if is_bij:
        cycles = cycle_decomposition(perm)
        ct = cycle_type(cycles)
        order = permutation_order(cycles)
        sign = permutation_sign(cycles)
        n_cycles = len(cycles)
        n_fixed = sum(1 for c in cycles if len(c) == 1)

        # 巡回長のカウント
        length_counts = Counter(len(c) for c in cycles)

        return {
            'k': k,
            'mod': mod,
            'n_odds': n_odds,
            'is_bijection': True,
            'n_cycles': n_cycles,
            'n_fixed_points': n_fixed,
            'cycle_type': ct,
            'cycle_length_counts': dict(length_counts),
            'order': order,
            'sign': sign,
            'sign_str': 'even' if sign == 1 else 'odd',
            'cycles': cycles
        }
    else:
        # 全単射でない場合の分析
        image = set(perm.values())
        missing = set(odds) - image
        # 各像の出現回数
        img_counts = Counter(perm.values())
        multi = {v: c for v, c in img_counts.items() if c > 1}

        return {
            'k': k,
            'mod': mod,
            'n_odds': n_odds,
            'is_bijection': False,
            'is_surjective': is_surj,
            'is_injective': is_inj,
            'missing_from_image': sorted(missing),
            'multiple_preimages': multi
        }

# ============================================================
# メイン分析
# ============================================================
print("=" * 70)
print("Syracuse写像の mod 2^k 上の置換構造分析")
print("=" * 70)

results = []
for k in range(3, 13):
    print(f"\n--- k = {k}, mod = {2**k} ---")
    res = analyze_k(k)
    results.append(res)

    if res['is_bijection']:
        print(f"  全単射: YES")
        print(f"  奇数の数: {res['n_odds']}")
        print(f"  巡回の数: {res['n_cycles']}")
        print(f"  不動点の数: {res['n_fixed_points']}")
        print(f"  置換の位数: {res['order']}")
        print(f"  符号: {res['sign_str']} ({'+1' if res['sign']==1 else '-1'})")
        print(f"  巡回長分布: {res['cycle_length_counts']}")

        if k <= 6:
            # 小さい k では巡回を表示
            for i, c in enumerate(res['cycles']):
                if len(c) <= 20:
                    print(f"    巡回 {i+1} (長さ {len(c)}): {c}")
                else:
                    print(f"    巡回 {i+1} (長さ {len(c)}): ({c[0]}, {c[1]}, ..., {c[-1]})")
    else:
        print(f"  全単射: NO")
        print(f"  全射: {res['is_surjective']}, 単射: {res['is_injective']}")

# ============================================================
# パターン分析
# ============================================================
print("\n" + "=" * 70)
print("パターン分析")
print("=" * 70)

# 不動点の分析
print("\n--- 不動点の分析 ---")
for res in results:
    if res['is_bijection']:
        fixed = [c[0] for c in res['cycles'] if len(c) == 1]
        print(f"  k={res['k']}: 不動点 = {fixed}")

# 符号パターン
print("\n--- 符号パターン ---")
for res in results:
    if res['is_bijection']:
        print(f"  k={res['k']}: 符号 = {res['sign_str']}, 位数 = {res['order']}")

# 巡回数の成長
print("\n--- 巡回数と不動点の成長 ---")
for res in results:
    if res['is_bijection']:
        print(f"  k={res['k']}: n_odds={res['n_odds']}, n_cycles={res['n_cycles']}, n_fixed={res['n_fixed_points']}, ratio={res['n_cycles']/res['n_odds']:.4f}")

# 巡回型の最大巡回長
print("\n--- 最大巡回長 ---")
for res in results:
    if res['is_bijection']:
        max_len = max(len(c) for c in res['cycles'])
        print(f"  k={res['k']}: 最大巡回長 = {max_len}, 最大/n_odds = {max_len/res['n_odds']:.4f}")

# 位数の素因数分解
print("\n--- 位数の素因数分解 ---")
def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

for res in results:
    if res['is_bijection']:
        facs = factorize(res['order'])
        fac_str = ' * '.join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facs.items()))
        print(f"  k={res['k']}: 位数 = {res['order']} = {fac_str}")
