"""
Syracuse mod 2^k 深層解析

前回の実験から発見された重要パターン:
1. 像の多重度分布に明確な規則性がある（3のべき乗が出現）
2. v2層別解析で全ての層が完全単射
3. k=9まで唯一のサイクルは不動点{1}、k=10で初めて長さ26のサイクル出現
4. サイクル外要素が圧倒的多数

この深層解析では:
(A) 多重度分布のパターンを数学的に解析
(B) k=10で出現するサイクルの構造を詳細に調査
(C) 関数グラフの木構造（テール）を解析
(D) v2層別全単射の証明的理解
"""

from collections import Counter, defaultdict
from math import gcd
from functools import reduce

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

def find_cycles_in_functional_graph(func_map):
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
            idx = path.index(node)
            cycle = path[idx:]
            cycles.append(cycle)
        visited.update(path)
    return cycles

# ==============================================================
# A: 多重度分布の数学的パターン解析
# ==============================================================
print("=" * 70)
print("A: 多重度分布の数学的パターン")
print("=" * 70)

print("\n奇数kでの多重度分布:")
for k in range(3, 16):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())

    # 多重度m を持つ像の数
    mult_counts = {}
    for m in sorted(md.keys()):
        mult_counts[m] = md[m]

    print(f"  k={k:2d}: {mult_counts}")

# パターン検証: 多重度mの像の数は 3^{m-1} か？
print("\n\n多重度パターンの検証 (多重度m の像の数 / 3^{m-1}):")
for k in range(5, 16):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    image_counter = Counter(func_map.values())
    md = Counter(image_counter.values())

    ratios = {}
    for m in sorted(md.keys()):
        if m >= 2:
            ratios[m] = md[m] / (3**(m-1))
    print(f"  k={k:2d}: {ratios}")

# ==============================================================
# B: k=10,11,12 の非自明サイクルの詳細
# ==============================================================
print("\n\n" + "=" * 70)
print("B: 非自明サイクルの詳細解析")
print("=" * 70)

for k in range(10, 16):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod

    cycles = find_cycles_in_functional_graph(func_map)
    nontrivial = [c for c in cycles if len(c) > 1]

    if nontrivial:
        print(f"\nk={k} (mod {mod}):")
        for i, cycle in enumerate(nontrivial):
            print(f"  サイクル {i+1}: 長さ={len(cycle)}")
            # サイクルの要素のmod小さいべきでの残基
            if len(cycle) <= 30:
                # 遷移を表示
                for j, node in enumerate(cycle):
                    next_node = func_map[node]
                    v = v2(3*node + 1)
                    print(f"    {node:6d} --[v2={v}]--> {next_node:6d}  "
                          f"(mod8={node%8}, mod16={node%16})")

            # v2パターン
            v2_seq = [v2(3*node + 1) for node in cycle]
            v2_counts = Counter(v2_seq)
            print(f"  v2パターン: {v2_seq}")
            print(f"  v2分布: {dict(v2_counts)}")
            print(f"  v2合計: {sum(v2_seq)}")
            # 3^a / 2^b 比率
            a = len(cycle)  # 3倍の回数
            b = sum(v2_seq)  # 2除算の合計回数
            print(f"  3^{a} vs 2^{b}: 3^{a}={3**a}, 2^{b}={2**b}, "
                  f"ratio={3**a / 2**b:.10f}")

            # このサイクルが実数コラッツの軌道に対応するか？
            # サイクル上の元が実際にコラッツでサイクルを形成するかチェック
            start = min(cycle)
            n = start
            real_orbit = [n]
            for _ in range(200):
                n = syracuse(n)
                if n == start:
                    print(f"  *** 実コラッツでもサイクル（長さ{len(real_orbit)}）***")
                    break
                if n < start or n > 10**15:
                    print(f"  実コラッツでは1に収束（サイクルではない）")
                    break
                real_orbit.append(n)

# ==============================================================
# C: 関数グラフのテール構造解析
# ==============================================================
print("\n\n" + "=" * 70)
print("C: テール（非サイクル部分）の構造")
print("=" * 70)

for k in range(3, 13):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod

    # サイクル要素を特定
    cycles = find_cycles_in_functional_graph(func_map)
    cycle_elements = set()
    for c in cycles:
        cycle_elements.update(c)

    # テール要素のサイクルまでの距離
    def distance_to_cycle(start):
        node = start
        dist = 0
        visited = set()
        while node not in cycle_elements and node not in visited:
            visited.add(node)
            node = func_map[node]
            dist += 1
        if node in cycle_elements:
            return dist
        return -1  # 到達不能（理論的にはないはず）

    tail_elements = [r for r in residues if r not in cycle_elements]
    if tail_elements:
        distances = [distance_to_cycle(r) for r in tail_elements]
        dist_counter = Counter(distances)
        max_dist = max(distances) if distances else 0
        avg_dist = sum(distances) / len(distances) if distances else 0
        print(f"  k={k:2d}: テール要素数={len(tail_elements):5d}, "
              f"最大距離={max_dist:3d}, 平均距離={avg_dist:.2f}, "
              f"距離分布={dict(sorted(dist_counter.items()))}")

# ==============================================================
# D: 多重度パターンの理論的解析
# ==============================================================
print("\n\n" + "=" * 70)
print("D: 多重度パターンの理論的構造")
print("=" * 70)

print("\nv2値ごとの寄与の分析:")
for k in range(5, 13):
    mod = 2**k
    residues = odd_residues_mod2k(k)

    # v2別に、T(r) mod 2^k の像をグループ化
    v2_image_overlap = {}
    images_by_v2 = defaultdict(list)

    for r in residues:
        val = 3 * r + 1
        j = v2(val)
        t = val // (2**j)
        t_mod = t % mod
        images_by_v2[j].append(t_mod)

    print(f"\n  k={k}:")
    for j in sorted(images_by_v2.keys()):
        imgs = images_by_v2[j]
        img_counter = Counter(imgs)
        mult_dist = Counter(img_counter.values())
        print(f"    v2={j}: 入力{len(imgs)}個, 像{len(img_counter)}個, "
              f"多重度={dict(sorted(mult_dist.items()))}")

# ==============================================================
# E: 像の「重なり」の構造 - 同じ像を持つ入力の関係
# ==============================================================
print("\n\n" + "=" * 70)
print("E: 同じ像を持つ入力のペア解析")
print("=" * 70)

for k in [6, 8, 10]:
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    v2_map = {}
    for r in residues:
        val = 3 * r + 1
        j = v2(val)
        t = val // (2**j)
        func_map[r] = t % mod
        v2_map[r] = j

    # 像ごとにプリイメージをグループ化
    preimages = defaultdict(list)
    for r in residues:
        preimages[func_map[r]].append(r)

    # 多重像（複数のプリイメージを持つ像）
    multi = {img: pres for img, pres in preimages.items() if len(pres) >= 2}

    print(f"\nk={k} (mod {mod}):")
    count = 0
    for img in sorted(multi.keys())[:10]:
        pres = multi[img]
        v2_vals = [v2_map[r] for r in pres]
        diffs = [pres[i+1] - pres[i] for i in range(len(pres)-1)]
        print(f"  像 {img:5d} <- {pres} (v2={v2_vals}, 差={diffs})")
        count += 1

    # 差の統計
    all_diffs = []
    for img, pres in multi.items():
        for i in range(len(pres)):
            for j in range(i+1, len(pres)):
                all_diffs.append(pres[j] - pres[i])

    if all_diffs:
        diff_v2 = Counter([v2(d) for d in all_diffs])
        print(f"  プリイメージ差のv2分布: {dict(sorted(diff_v2.items()))}")
        diff_mod = Counter([d % 8 for d in all_diffs])
        print(f"  プリイメージ差のmod8分布: {dict(sorted(diff_mod.items()))}")

# ==============================================================
# F: v2層の単射性と 3x+1 の数論的性質
# ==============================================================
print("\n\n" + "=" * 70)
print("F: v2層別写像の代数的構造")
print("=" * 70)

print("\nv2=1層 (r = 3 or 7 mod 8) での写像 T_1(r) = (3r+1)/2 mod 2^{k-1}:")
for k in range(4, 12):
    target_mod = 2**(k-1)
    # v2=1 の奇数: r ≡ 3 or 7 (mod 8)
    inputs = [r for r in odd_residues_mod2k(k) if v2(3*r+1) == 1]
    func = {r: (3*r+1)//2 % target_mod for r in inputs}

    image_set = set(func.values())
    # 像が奇数の奇数残基 mod 2^{k-1} に一致するか
    odd_targets = set(r for r in range(1, target_mod, 2))
    covers_all_odd = image_set == odd_targets

    # 写像は本質的に r -> (3r+1)/2 mod 2^{k-1}
    # これは Z/2^{k-1}Z 上のアフィン写像
    # (3r+1)/2 = 3r/2 + 1/2
    # 2-adic で 1/2 は存在、3/2 も存在
    # つまり r -> (3/2)r + (1/2) mod 2^{k-1}

    print(f"  k={k}: 入力{len(inputs)}個, 像{len(image_set)}個, "
          f"全奇数カバー={'Yes' if covers_all_odd else 'No'}, "
          f"target_mod={target_mod}")

print("\nv2=2層 (r = 1 mod 8) での写像 T_2(r) = (3r+1)/4 mod 2^{k-2}:")
for k in range(4, 12):
    target_mod = 2**(k-2)
    inputs = [r for r in odd_residues_mod2k(k) if v2(3*r+1) == 2]
    func = {r: (3*r+1)//4 % target_mod for r in inputs}

    image_set = set(func.values())
    odd_targets = set(r for r in range(1, target_mod, 2))
    covers_all_odd = image_set == odd_targets

    print(f"  k={k}: 入力{len(inputs)}個, 像{len(image_set)}個, "
          f"全奇数カバー={'Yes' if covers_all_odd else 'No'}, "
          f"target_mod={target_mod}")

# ==============================================================
# G: 像の数の公式
# ==============================================================
print("\n\n" + "=" * 70)
print("G: 像の数の理論的予測")
print("=" * 70)

print("\nT(r) mod 2^k の像の数:")
print(f"{'k':>4} {'像数':>8} {'奇数残基数':>12} {'像/残基':>10} {'予測(3/4)^j和':>16}")
for k in range(3, 16):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    num_images = len(set(func_map.values()))
    num_residues = len(residues)
    ratio = num_images / num_residues

    # 理論予測: 像の数 = sum_{j=1}^{k-1} 2^{k-j-1} = 2^{k-1} - 1 ？
    # いや、各v2=j層のサイズは 2^{k-j-1}、像は奇数 mod 2^{k-j}
    # 層間で像が重複する可能性がある
    # 重複を無視した場合の和
    sum_layers = sum(2**(k-j-1) for j in range(1, k))
    # 予測: 像の和(重複なし) = 2^{k-1}-1
    pred = 2**(k-1) - 1

    print(f"{k:4d} {num_images:8d} {num_residues:12d} {ratio:10.4f} {pred:16d}")

# 像の数はどう計算されるべきか
print("\n像の数 vs 各種公式:")
for k in range(3, 16):
    mod = 2**k
    residues = odd_residues_mod2k(k)
    func_map = {}
    for r in residues:
        t = syracuse(r)
        func_map[r] = t % mod
    num_images = len(set(func_map.values()))

    # v2層の像をマージして重複を数える
    all_images = set()
    layer_images = {}
    for j in range(1, k+5):
        inputs_j = [r for r in residues if v2(3*r+1) == j]
        if not inputs_j:
            continue
        imgs_j = set()
        for r in inputs_j:
            val = 3 * r + 1
            t = val // (2**j)
            t_mod = t % mod
            imgs_j.add(t_mod)
        layer_images[j] = imgs_j
        all_images.update(imgs_j)

    # 層間の重複
    overlaps = {}
    layers_list = sorted(layer_images.keys())
    for i, j1 in enumerate(layers_list):
        for j2 in layers_list[i+1:]:
            overlap = layer_images[j1] & layer_images[j2]
            if overlap:
                overlaps[(j1,j2)] = len(overlap)

    if overlaps:
        print(f"  k={k:2d}: 像数={num_images}, 合計={len(all_images)}, "
              f"層間重複={overlaps}")
    else:
        print(f"  k={k:2d}: 像数={num_images}, 合計={len(all_images)}, 層間重複なし")
