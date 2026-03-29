"""
Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の mod 2^k 上の置換群 <T> の構造分析

核心的な問題:
  T は mod 2^k の奇数残基上で (一般には) well-defined な置換にならない。
  v2(3n+1) が k 以上になりうるため。

  方針:
  1. まず naive に T(n) mod 2^k を計算して、奇数 mod 2^k 上の写像とする
  2. 全単射性を確認し、全単射なら置換群 <T> を計算
  3. 全単射でない場合は、T^m の合成を調べる

  群 <T> = {T, T^2, T^3, ...} の位数は置換 T の位数に等しい。

  追加: <T> を対称群 S_{2^{k-1}} の部分群として構造を調べる:
  - 巡回群か？
  - アーベルか？（巡回群なら自明にアーベル）
  - 位数の素因数分解とkの関係

k = 3..14 で計算する。
"""

from math import gcd, log2
from functools import reduce
from collections import Counter
import json
import time

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse: T(n) = (3n+1) / 2^{v2(3n+1)}"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def get_odd_residues(k):
    """mod 2^k の奇数残基"""
    mod = 2**k
    return list(range(1, mod, 2))

def compute_map(k):
    """T(n) mod 2^k の写像を計算（奇数→奇数）"""
    mod = 2**k
    odds = get_odd_residues(k)
    mapping = {}
    for n in odds:
        img = syracuse(n) % mod
        mapping[n] = img
    return mapping

def is_bijection(mapping, odds):
    image = set(mapping.values())
    return image == set(odds)

def cycle_decomposition(perm):
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
        if cycle:
            cycles.append(tuple(cycle))
    return cycles

def perm_order_from_cycles(cycles):
    """置換の位数 = 巡回長のLCM"""
    lengths = [len(c) for c in cycles]
    if not lengths:
        return 1
    result = lengths[0]
    for l in lengths[1:]:
        result = result * l // gcd(result, l)
    return result

def perm_sign(cycles):
    sign = 1
    for c in cycles:
        if len(c) % 2 == 0:
            sign *= -1
    return sign

def compose_perm(p1, p2):
    """p1 o p2 = p1(p2(x))"""
    return {x: p1[p2[x]] for x in p2}

def perm_power(p, n):
    """p^n を高速べき乗で計算"""
    if n == 0:
        return {x: x for x in p}  # identity
    if n == 1:
        return dict(p)
    if n % 2 == 0:
        half = perm_power(p, n // 2)
        return compose_perm(half, half)
    else:
        return compose_perm(p, perm_power(p, n - 1))

def factorize(n):
    """素因数分解"""
    if n <= 1:
        return {}
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

def format_factorization(n):
    facs = factorize(n)
    if not facs:
        return str(n)
    parts = []
    for p, e in sorted(facs.items()):
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " * ".join(parts)

# ==========================================================
# メイン計算
# ==========================================================
print("=" * 70)
print("Syracuse T mod 2^k 上の置換群 <T> の構造")
print("=" * 70)

results = []
order_data = []

for k in range(3, 15):
    t_start = time.time()
    mod = 2**k
    odds = get_odd_residues(k)
    n_odds = len(odds)  # = 2^{k-1}

    mapping = compute_map(k)
    bij = is_bijection(mapping, odds)

    print(f"\n--- k={k}, mod={mod}, |domain|={n_odds} ---")
    print(f"  全単射: {'YES' if bij else 'NO'}")

    entry = {
        'k': k,
        'mod': mod,
        'n_odds': n_odds,
        'is_bijection': bij
    }

    if bij:
        cycles = cycle_decomposition(mapping)
        order = perm_order_from_cycles(cycles)
        sign = perm_sign(cycles)
        n_cycles = len(cycles)
        n_fixed = sum(1 for c in cycles if len(c) == 1)
        cycle_len_counts = Counter(len(c) for c in cycles)

        entry['order'] = order
        entry['order_factored'] = format_factorization(order)
        entry['sign'] = 'even' if sign == 1 else 'odd'
        entry['n_cycles'] = n_cycles
        entry['n_fixed_points'] = n_fixed
        entry['cycle_length_counts'] = dict(sorted(cycle_len_counts.items()))
        entry['max_cycle_length'] = max(len(c) for c in cycles)

        print(f"  位数 |<T>| = {order} = {format_factorization(order)}")
        print(f"  符号: {entry['sign']}")
        print(f"  巡回数: {n_cycles}, 不動点: {n_fixed}")
        print(f"  巡回長分布: {dict(sorted(cycle_len_counts.items()))}")
        print(f"  最大巡回長: {entry['max_cycle_length']}")

        # 位数の2-adic valuation
        order_v2 = v2(order) if order > 0 else 0
        entry['order_v2'] = order_v2
        print(f"  v2(|<T>|) = {order_v2}")

        # log2(order) と k の関係
        if order > 0:
            entry['log2_order'] = log2(order) if order > 0 else 0
            print(f"  log2(|<T>|) = {entry['log2_order']:.4f}")

        order_data.append((k, order))

        # 不動点の一覧（少数なら）
        if n_fixed <= 10:
            fixed_pts = [c[0] for c in cycles if len(c) == 1]
            entry['fixed_points'] = fixed_pts
            print(f"  不動点: {fixed_pts}")

        # 周期2点
        period2 = [c for c in cycles if len(c) == 2]
        if period2 and len(period2) <= 10:
            entry['period2_cycles'] = [list(c) for c in period2]
            print(f"  周期2サイクル: {[list(c) for c in period2]}")
    else:
        # 非全単射の分析
        image = set(mapping.values())
        missing = set(odds) - image
        img_counts = Counter(mapping.values())
        multi = {v: c for v, c in img_counts.items() if c > 1}

        entry['image_size'] = len(image)
        entry['missing_count'] = len(missing)
        print(f"  像のサイズ: {len(image)}/{n_odds}")
        print(f"  欠損: {len(missing)}個")

        # それでも T の反復を調べる
        # T^m が最初に恒等写像に戻る最小 m を探す
        current = dict(mapping)
        for m in range(2, min(n_odds * 2, 10000)):
            current = {x: mapping[current[x]] if current[x] in mapping else None
                       for x in odds}
            if any(v is None for v in current.values()):
                break

    elapsed = time.time() - t_start
    entry['compute_time'] = round(elapsed, 4)
    results.append(entry)

# ==========================================================
# 成長率分析
# ==========================================================
print("\n" + "=" * 70)
print("位数の成長率分析")
print("=" * 70)

print("\n--- 位数の表 ---")
print(f"{'k':>4} {'|<T>|':>20} {'素因数分解':>30} {'log2(|<T>|)':>14} {'log2(|<T>|)/k':>16}")
for entry in results:
    if entry['is_bijection']:
        k = entry['k']
        order = entry['order']
        l2 = log2(order) if order > 1 else 0
        ratio = l2 / k if k > 0 else 0
        print(f"{k:>4} {order:>20} {entry['order_factored']:>30} {l2:>14.4f} {ratio:>16.4f}")

# 連続する k での位数比
print("\n--- 位数の増加比 |<T>|_{k+1} / |<T>|_k ---")
for i in range(len(order_data) - 1):
    k1, o1 = order_data[i]
    k2, o2 = order_data[i+1]
    if o1 > 0:
        ratio = o2 / o1
        print(f"  k={k1}→{k2}: {o2}/{o1} = {ratio:.4f} (log2 ratio = {log2(ratio):.4f})")

# k間の位数のGCD/LCM関係
print("\n--- 位数間の整除関係 ---")
for i in range(len(order_data) - 1):
    k1, o1 = order_data[i]
    k2, o2 = order_data[i+1]
    g = gcd(o1, o2)
    divides = (o2 % o1 == 0)
    print(f"  |<T>|_{k1}={o1}, |<T>|_{k2}={o2}: gcd={g}, {o1}|{o2}? {'YES' if divides else 'NO'}")

# ==========================================================
# 巡回群かどうかの検証
# ==========================================================
print("\n" + "=" * 70)
print("<T> は巡回群か？（<T> = {T^0, T^1, ..., T^{ord-1}} で位数 = ord なら巡回群）")
print("=" * 70)
print("  <T> は定義上 T が生成する巡回群なので、常に巡回群。")
print("  位数 = T の置換としての位数。")
print("  より興味深い問題: <T> が対称群 S_n のどの部分に埋め込まれるか。")

# ==========================================================
# 具体的な巡回構造の深掘り
# ==========================================================
print("\n" + "=" * 70)
print("巡回長の最大値と素因数の分析")
print("=" * 70)

for entry in results:
    if not entry['is_bijection']:
        continue
    k = entry['k']
    clc = entry['cycle_length_counts']
    print(f"\n  k={k}:")
    distinct_lengths = sorted(clc.keys())
    print(f"    巡回長の種類: {distinct_lengths}")
    for length in distinct_lengths:
        print(f"      長さ {length}: {clc[length]}個 (合計 {length * clc[length]} 要素) {format_factorization(length)}")

# ==========================================================
# 位数の 2^k 依存の規則性
# ==========================================================
print("\n" + "=" * 70)
print("位数の規則性: v2(order), v3(order), etc.")
print("=" * 70)

for k, order in order_data:
    facs = factorize(order)
    v2_val = facs.get(2, 0)
    v3_val = facs.get(3, 0)
    print(f"  k={k}: order={order}, v2={v2_val}, v3={v3_val}, 奇数部={order // (2**v2_val)}")

# ==========================================================
# 位数は 2^{k-1}! を割り切るか (当然)
# 位数は 2^{k-1} (= n_odds) を割り切るか
# ==========================================================
print("\n--- 位数と n_odds=2^{k-1} の関係 ---")
for k, order in order_data:
    n = 2**(k-1)
    print(f"  k={k}: order={order}, 2^{k-1}={n}, order | 2^{k-1}? {n % order == 0 if order > 0 else '?'}")
    # n! / order (対称群内での指数)
    # order | phi(2^{k-1})? (where phi is Euler's)

# ==========================================================
# 追加: k >= 12 で非全単射の場合の軌道構造
# ==========================================================
print("\n" + "=" * 70)
print("非全単射の場合の構造（もしあれば）")
print("=" * 70)

for entry in results:
    if not entry['is_bijection']:
        print(f"  k={entry['k']}: 全単射でない。像サイズ={entry.get('image_size','?')}")

# ==========================================================
# JSON出力
# ==========================================================
output = {
    'title': 'Syracuse T mod 2^k permutation group structure',
    'results': []
}

for entry in results:
    # cycles は大きいのでJSON出力から省略
    safe_entry = {key: val for key, val in entry.items()
                  if key not in ('cycles',)}
    output['results'].append(safe_entry)

# 成長率サマリ
if len(order_data) >= 2:
    ratios = []
    for i in range(len(order_data) - 1):
        k1, o1 = order_data[i]
        k2, o2 = order_data[i+1]
        if o1 > 0:
            ratios.append(o2/o1)
    output['growth_ratios'] = ratios
    output['avg_growth_ratio'] = sum(ratios) / len(ratios) if ratios else None
    output['growth_log2_avg'] = sum(log2(r) for r in ratios) / len(ratios) if ratios else None

with open('/Users/soyukke/study/lean-unsolved/results/syracuse_permgroup.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("\n\nJSON結果を results/syracuse_permgroup.json に保存しました。")
