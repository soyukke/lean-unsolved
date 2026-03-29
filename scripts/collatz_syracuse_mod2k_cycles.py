"""
Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)} の mod 2^k でのサイクル構造解析

奇数の剰余類 (Z/2^kZ)^* 上で Syracuse 写像を計算し、
置換としてのサイクル分解を求める。

注意: Syracuse関数は v2 が入力に依存するため mod 2^k 上で
well-defined な置換にはならない。しかし、v2 の値で層別化すると
各層上では well-defined な写像になる。

ここでは以下の2つのアプローチを取る:
(A) 「自然な」Syracuse写像: T(r) mod 2^k を計算し、
    関数グラフとして解析（well-defined でなくても実際の値で計算）
(B) v2層別解析: v2(3r+1) = j の層ごとに T(r) mod 2^{k-j} を計算し、
    各層での写像の性質を調べる
"""

import json
from collections import Counter, defaultdict
from math import gcd

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)}"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def odd_residues_mod2k(k):
    """Return all odd residues modulo 2^k"""
    mod = 2**k
    return [r for r in range(1, mod, 2)]

def find_cycles_in_functional_graph(func_map):
    """
    func_map: dict {node -> node}
    Return list of cycles (each cycle is a list of nodes)
    """
    visited = set()
    cycles = []
    for start in func_map:
        if start in visited:
            continue
        path = []
        path_set = set()
        node = start
        while node not in visited and node not in path_set:
            path.append(node)
            path_set.add(node)
            node = func_map[node]
        if node in path_set:
            # Found a new cycle
            idx = path.index(node)
            cycle = path[idx:]
            cycles.append(cycle)
        visited.update(path)
    return cycles

def analyze_approach_A(k):
    """
    Approach A: 奇数 r (mod 2^k) に対して T(r) mod 2^k を計算
    これは well-defined な写像として扱う（ただし真の置換ではない可能性あり）
    """
    mod = 2**k
    residues = odd_residues_mod2k(k)

    # 関数グラフを構築
    func_map = {}
    v2_distribution = Counter()
    for r in residues:
        val3r1 = 3 * r + 1
        j = v2(val3r1)
        t_r = val3r1 // (2**j)
        t_r_mod = t_r % mod
        # t_r_mod が偶数の場合もある（mod 2^k では）
        # 奇数にする
        if t_r_mod % 2 == 0:
            # これは 2^k で割り切れるケースの影響
            t_r_mod = t_r % mod
        func_map[r] = t_r_mod
        v2_distribution[j] += 1

    # 像の集合
    image_set = set(func_map.values())
    domain_set = set(residues)

    # 像が定義域に含まれるか確認
    is_endomorphism = image_set.issubset(domain_set)

    # 単射性チェック
    image_counter = Counter(func_map.values())
    is_injective = all(c == 1 for c in image_counter.values())

    # サイクル解析（内部写像の場合のみ）
    cycles = []
    if is_endomorphism:
        cycles = find_cycles_in_functional_graph(func_map)

    return {
        'k': k,
        'mod': mod,
        'num_odd_residues': len(residues),
        'is_endomorphism': is_endomorphism,
        'is_injective': is_injective,
        'num_distinct_images': len(image_set),
        'v2_distribution': dict(sorted(v2_distribution.items())),
        'cycles': [sorted(c) for c in sorted(cycles, key=lambda c: min(c))],
        'num_cycles': len(cycles),
        'cycle_lengths': sorted([len(c) for c in cycles]),
        'non_odd_images': sorted([v for v in image_set if v % 2 == 0])[:10],
    }

def analyze_approach_B(k):
    """
    Approach B: v2層別解析
    v2(3r+1) = j の層ごとに、T(r) mod 2^{k-j} を計算
    """
    residues = odd_residues_mod2k(k)

    layers = defaultdict(list)
    for r in residues:
        val3r1 = 3 * r + 1
        j = v2(val3r1)
        layers[j].append(r)

    layer_analysis = {}
    for j in sorted(layers.keys()):
        if j >= k:
            # mod 2^{k-j} が意味をなさない
            layer_analysis[j] = {
                'size': len(layers[j]),
                'residues': layers[j][:10],
                'note': f'v2={j} >= k={k}, projection trivial'
            }
            continue

        target_mod = 2**(k - j)
        func_map = {}
        for r in layers[j]:
            val3r1 = 3 * r + 1
            t_r = val3r1 // (2**j)
            t_r_mod = t_r % target_mod
            func_map[r] = t_r_mod

        image_set = set(func_map.values())
        image_counter = Counter(func_map.values())
        is_injective = all(c == 1 for c in image_counter.values())

        # 像が奇数かチェック
        odd_images = [v for v in image_set if v % 2 == 1]
        even_images = [v for v in image_set if v % 2 == 0]

        layer_analysis[j] = {
            'size': len(layers[j]),
            'target_mod': target_mod,
            'is_injective': is_injective,
            'num_distinct_images': len(image_set),
            'num_odd_images': len(odd_images),
            'num_even_images': len(even_images),
            'residues_sample': layers[j][:8],
            'images_sample': [func_map[r] for r in layers[j][:8]],
        }

    return {
        'k': k,
        'layer_sizes': {j: len(layers[j]) for j in sorted(layers.keys())},
        'layers': {str(j): layer_analysis[j] for j in sorted(layer_analysis.keys())},
    }

def analyze_truncated_map(k):
    """
    Approach C: 切り詰めSyracuse写像
    T_k(r) = (3r+1)/2^{v2(3r+1)} mod 2^k
    ただし v2(3r+1) は実際の値を使う

    これが奇数の剰余類上で置換になっているかを調べる
    """
    mod = 2**k
    residues = odd_residues_mod2k(k)

    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod

    # 像チェック
    image_counter = Counter(func_map.values())
    image_set = set(func_map.values())
    domain_set = set(residues)

    is_surjective = image_set == domain_set
    is_injective = len(image_set) == len(residues)
    is_permutation = is_surjective and is_injective

    # サイクル解析
    cycles = []
    if is_permutation:
        cycles = find_cycles_in_functional_graph(func_map)
    elif image_set.issubset(domain_set):
        cycles = find_cycles_in_functional_graph(func_map)

    # 像の多重度分布
    multiplicity_dist = Counter(image_counter.values())

    # 不動点
    fixed_points = [r for r in residues if func_map[r] == r]

    return {
        'k': k,
        'mod': mod,
        'num_residues': len(residues),
        'is_permutation': is_permutation,
        'is_injective': is_injective,
        'is_surjective': is_surjective,
        'all_images_odd': all(v % 2 == 1 for v in image_set),
        'num_distinct_images': len(image_set),
        'image_multiplicity_dist': dict(sorted(multiplicity_dist.items())),
        'fixed_points': fixed_points,
        'num_fixed_points': len(fixed_points),
        'cycles': cycles if len(cycles) <= 50 else cycles[:50],
        'num_cycles': len(cycles),
        'cycle_lengths': sorted(Counter([len(c) for c in cycles]).items()),
        'cycle_length_distribution': dict(Counter([len(c) for c in cycles])),
    }

def analyze_3x1_map(k):
    """
    比較用: 3x+1 の代わりに 3x-1 写像のサイクル構造
    T'(n) = (3n-1) / 2^{v2(3n-1)}
    """
    mod = 2**k
    residues = odd_residues_mod2k(k)

    func_map = {}
    for r in residues:
        if r == 0:
            continue
        val = 3 * r - 1
        if val == 0:
            func_map[r] = 0
            continue
        j = v2(abs(val))
        t = abs(val) // (2**j)
        func_map[r] = t % mod

    image_set = set(func_map.values())
    domain_set = set(residues)
    is_permutation = image_set == domain_set and len(image_set) == len(residues)

    cycles = []
    if image_set.issubset(domain_set):
        cycles = find_cycles_in_functional_graph(func_map)

    fixed_points = [r for r in residues if r in func_map and func_map[r] == r]

    return {
        'k': k,
        'is_permutation': is_permutation,
        'num_cycles': len(cycles),
        'cycle_lengths': sorted(Counter([len(c) for c in cycles]).items()),
        'fixed_points': fixed_points,
    }

def main():
    print("=" * 70)
    print("Syracuse mod 2^k サイクル構造解析")
    print("=" * 70)

    # ==============================================================
    # Approach C: 切り詰めSyracuse置換
    # ==============================================================
    print("\n### Approach C: 切り詰めSyracuse写像 T(r) mod 2^k ###\n")

    results_C = {}
    for k in range(3, 13):
        result = analyze_truncated_map(k)
        results_C[k] = result
        print(f"k={k:2d} | mod 2^k={2**k:6d} | 奇数残基数={result['num_residues']:5d} | "
              f"置換={'Yes' if result['is_permutation'] else 'No ':3s} | "
              f"単射={'Yes' if result['is_injective'] else 'No ':3s} | "
              f"全射={'Yes' if result['is_surjective'] else 'No ':3s} | "
              f"像数={result['num_distinct_images']:5d} | "
              f"不動点={result['num_fixed_points']} | "
              f"サイクル数={result['num_cycles']}")
        if result['cycle_length_distribution']:
            print(f"       サイクル長分布: {result['cycle_length_distribution']}")

    # ==============================================================
    # Approach B: v2層別解析
    # ==============================================================
    print("\n\n### Approach B: v2層別解析 ###\n")

    results_B = {}
    for k in range(3, 11):
        result = analyze_approach_B(k)
        results_B[k] = result
        print(f"k={k}: 層サイズ = {result['layer_sizes']}")
        for j_str, info in result['layers'].items():
            j = int(j_str)
            if 'note' in info:
                print(f"  v2={j}: {info['size']}個, {info['note']}")
            else:
                print(f"  v2={j}: {info['size']}個 -> mod {info['target_mod']}上, "
                      f"単射={'Yes' if info['is_injective'] else 'No'}, "
                      f"像数={info['num_distinct_images']}, "
                      f"(奇数像={info['num_odd_images']}, 偶数像={info['num_even_images']})")

    # ==============================================================
    # 不動点の詳細解析
    # ==============================================================
    print("\n\n### 不動点解析 ###\n")
    print("Syracuse(r) = r mod 2^k となる r の一覧:")
    for k in range(3, 13):
        fps = results_C[k]['fixed_points']
        print(f"  k={k:2d}: {fps}")

    # ==============================================================
    # サイクルの詳細（小さいkについて）
    # ==============================================================
    print("\n\n### サイクルの詳細 (k=3..7) ###\n")
    for k in range(3, 8):
        result = results_C[k]
        print(f"\nk={k} (mod {2**k}):")
        for i, cycle in enumerate(result['cycles']):
            # サイクルの遷移を表示
            if len(cycle) <= 20:
                transitions = []
                for node in cycle:
                    transitions.append(str(node))
                print(f"  Cycle {i+1} (len={len(cycle)}): {' -> '.join(transitions)} -> {transitions[0]}")

    # ==============================================================
    # 像の多重度の解析
    # ==============================================================
    print("\n\n### 像の多重度パターン ###\n")
    for k in range(3, 13):
        result = results_C[k]
        md = result['image_multiplicity_dist']
        print(f"  k={k:2d}: 多重度分布 = {md}")

    # ==============================================================
    # サイクル長のGCD、LCM解析
    # ==============================================================
    print("\n\n### サイクル長のGCD/LCM解析 ###\n")
    for k in range(3, 13):
        result = results_C[k]
        lengths = [l for l, _ in result['cycle_lengths']]
        if lengths:
            from math import lcm
            from functools import reduce
            g = reduce(gcd, lengths)
            l = reduce(lcm, lengths)
            print(f"  k={k:2d}: 長さ集合={set(lengths)}, GCD={g}, LCM={l}")

    # ==============================================================
    # kの増加に伴うサイクル数の成長率
    # ==============================================================
    print("\n\n### サイクル数の成長パターン ###\n")
    for k in range(4, 13):
        prev = results_C[k-1]['num_cycles']
        curr = results_C[k]['num_cycles']
        ratio = curr / prev if prev > 0 else float('inf')
        print(f"  k={k-1}->{k}: {prev} -> {curr} (ratio={ratio:.3f})")

    # ==============================================================
    # 長いサイクルに属する要素の割合
    # ==============================================================
    print("\n\n### サイクル要素 vs 非サイクル要素 ###\n")
    for k in range(3, 13):
        result = results_C[k]
        total = result['num_residues']
        in_cycle = sum(len(c) for c in result['cycles'])
        tail = total - in_cycle
        print(f"  k={k:2d}: 全奇数={total:5d}, サイクル内={in_cycle:5d} ({100*in_cycle/total:.1f}%), "
              f"テール={tail:5d} ({100*tail/total:.1f}%)")

    # ==============================================================
    # コラッツの既知サイクル {1,1,1,...} の反映
    # ==============================================================
    print("\n\n### 既知のコラッツ自明サイクル {1} の mod 2^k での出現 ###\n")
    for k in range(3, 13):
        mod = 2**k
        # 1 のサイクル
        n = 1
        orbit = [1]
        while True:
            n = syracuse(n) % mod
            if n in orbit:
                break
            orbit.append(n)
        idx = orbit.index(n)
        cycle_part = orbit[idx:]
        print(f"  k={k:2d}: 1から始まる軌道のサイクル部分 = {cycle_part} (長さ {len(cycle_part)})")

    # ==============================================================
    # 3x-1 との比較
    # ==============================================================
    print("\n\n### 比較: 3x-1 写像のサイクル構造 ###\n")
    for k in range(3, 11):
        result = analyze_3x1_map(k)
        print(f"  k={k:2d}: 置換={'Yes' if result['is_permutation'] else 'No':3s}, "
              f"サイクル数={result['num_cycles']}, "
              f"不動点={result['fixed_points']}, "
              f"サイクル長={result['cycle_lengths']}")

    return results_C, results_B

if __name__ == '__main__':
    results_C, results_B = main()
