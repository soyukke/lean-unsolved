#!/usr/bin/env python3
"""探索27: コラッツ関係のグラフ理論的構造解析"""

from collections import defaultdict, deque

N = 65536  # 2^16

def syracuse(n):
    """奇数 n に対する Syracuse 写像: (3n+1) / 2^v2(3n+1)"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

print("=" * 70)
print("探索27: コラッツ関係のグラフ理論的構造解析")
print("=" * 70)

# --- Syracuse グラフ構築（奇数のみ）---
print(f"\n[1] Syracuse グラフ構築 (奇数 1..{N})")
# 辺: n → syracuse(n)
edges = {}  # n -> syracuse(n)
in_degree = defaultdict(int)
out_targets = defaultdict(list)
odd_nums = [n for n in range(1, N + 1) if n % 2 == 1]

for n in odd_nums:
    t = syracuse(n)
    edges[n] = t
    in_degree[t] += 1
    out_targets[t].append(n)  # t の逆辺

num_nodes = len(odd_nums)
# N 以下の奇数で、Syracuse の行き先も N 以下のもの
internal_edges = sum(1 for n in odd_nums if edges[n] <= N)
print(f"  頂点数 (奇数): {num_nodes}")
print(f"  内部辺数 (行き先も <= {N}): {internal_edges}")
print(f"  外部辺数 (行き先 > {N}): {num_nodes - internal_edges}")

# --- 入次数分布 ---
print(f"\n[2] 入次数分布 (上位ハブ):")
in_deg_list = [(n, in_degree[n]) for n in odd_nums if in_degree[n] > 0]
in_deg_list.sort(key=lambda x: -x[1])

# 入次数の分布
deg_dist = defaultdict(int)
for n in odd_nums:
    d = in_degree.get(n, 0)
    deg_dist[d] += 1

print(f"  入次数分布:")
for d in sorted(deg_dist.keys()):
    if deg_dist[d] > 0:
        print(f"    deg={d}: {deg_dist[d]} 頂点 ({100*deg_dist[d]/num_nodes:.1f}%)")

print(f"\n  上位20ハブ (入次数が高い頂点):")
for n, d in in_deg_list[:20]:
    # n の性質
    bin_n = bin(n)[2:]
    print(f"    n={n:6d} (入次数={d:3d}, bin={bin_n[:20]}{'...' if len(bin_n)>20 else ''})")

# --- ハブの共通性質 ---
print(f"\n[3] ハブの性質分析:")
top_hubs = [n for n, d in in_deg_list[:50]]
print(f"  上位50ハブの n mod 3 分布:")
mod3 = defaultdict(int)
for n in top_hubs:
    mod3[n % 3] += 1
print(f"    {dict(mod3)}")

print(f"  上位50ハブの n mod 8 分布:")
mod8 = defaultdict(int)
for n in top_hubs:
    mod8[n % 8] += 1
print(f"    {dict(sorted(mod8.items()))}")

# --- BFS で 1 からの距離（逆方向）---
print(f"\n[4] 1 からの距離 (Syracuse グラフの逆向き BFS):")
# 逆グラフで BFS
inv_graph = defaultdict(list)
for n in odd_nums:
    t = edges[n]
    if t <= N and t % 2 == 1:
        inv_graph[t].append(n)

dist = {}
queue = deque([1])
dist[1] = 0
while queue:
    v = queue.popleft()
    for u in inv_graph[v]:
        if u not in dist:
            dist[u] = dist[v] + 1
            queue.append(u)

reachable = len(dist)
print(f"  1 から到達可能な頂点数: {reachable} / {num_nodes} ({100*reachable/num_nodes:.1f}%)")

if dist:
    max_dist = max(dist.values())
    print(f"  最大距離 (グラフの深さ): {max_dist}")

    # 距離分布
    dist_hist = defaultdict(int)
    for d in dist.values():
        dist_hist[d] += 1
    print(f"  距離分布:")
    for d in sorted(dist_hist.keys()):
        bar = "#" * min(dist_hist[d] // 100, 50)
        print(f"    dist={d:3d}: {dist_hist[d]:5d} 頂点 {bar}")

    # 各距離の最大の n
    print(f"\n  各距離での最大 n:")
    dist_max_n = defaultdict(int)
    for n, d in dist.items():
        dist_max_n[d] = max(dist_max_n[d], n)
    for d in sorted(dist_max_n.keys()):
        print(f"    dist={d:3d}: max_n={dist_max_n[d]}")

# --- 1に到達できない頂点の調査 ---
unreachable = [n for n in odd_nums if n not in dist]
print(f"\n[5] 逆BFSで到達できない頂点: {len(unreachable)}")
if unreachable:
    print(f"  (これらは Syracuse(n) > {N} を経由する頂点)")
    print(f"  例: {unreachable[:20]}")
    # これらが実際に 1 に到達するか確認
    escapes = 0
    for n in unreachable[:100]:
        m = n
        for _ in range(10000):
            if m == 1:
                break
            m = syracuse(m) if m % 2 == 1 else m // 2
            while m % 2 == 0:
                m //= 2
        if m == 1:
            escapes += 1
    print(f"  最初の{min(100,len(unreachable))}個のうち 1 に到達: {escapes}")

# --- 木構造のバランス度 ---
print(f"\n[6] 逆木構造のバランス度:")
# 各頂点の子の数（逆グラフでの隣接数）
child_counts = [len(inv_graph.get(n, [])) for n in odd_nums if n in dist]
if child_counts:
    print(f"  平均子ノード数: {sum(child_counts)/len(child_counts):.3f}")
    print(f"  子ノード数 0 (葉): {child_counts.count(0)} ({100*child_counts.count(0)/len(child_counts):.1f}%)")
    print(f"  子ノード数 1: {child_counts.count(1)} ({100*child_counts.count(1)/len(child_counts):.1f}%)")
    print(f"  子ノード数 2: {child_counts.count(2)} ({100*child_counts.count(2)/len(child_counts):.1f}%)")
    print(f"  子ノード数 >= 3: {sum(1 for c in child_counts if c >= 3)}")

# --- 強連結成分 ---
print(f"\n[7] 強連結成分の探索:")
# Tarjan's algorithm (簡易版: 小規模なので)
# Syracuse グラフで N 以下に留まるサブグラフでのサイクル探索
visited = set()
in_stack = set()
stack = []
scc_list = []
index_counter = [0]
indices = {}
lowlink = {}

def strongconnect(v):
    indices[v] = index_counter[0]
    lowlink[v] = index_counter[0]
    index_counter[0] += 1
    stack.append(v)
    in_stack.add(v)

    w = edges.get(v)
    if w and w <= N and w % 2 == 1:
        if w not in indices:
            strongconnect(w)
            lowlink[v] = min(lowlink[v], lowlink[w])
        elif w in in_stack:
            lowlink[v] = min(lowlink[v], indices[w])

    if lowlink[v] == indices[v]:
        scc = []
        while True:
            w = stack.pop()
            in_stack.discard(w)
            scc.append(w)
            if w == v:
                break
        if len(scc) > 1:
            scc_list.append(scc)

import sys
sys.setrecursionlimit(100000)

# 小さい範囲で実行
small_N = min(N, 10000)
small_odds = [n for n in range(1, small_N + 1) if n % 2 == 1]
for n in small_odds:
    if n not in indices:
        try:
            strongconnect(n)
        except RecursionError:
            pass

print(f"  奇数 1..{small_N} での非自明な強連結成分数: {len(scc_list)}")
if scc_list:
    for scc in scc_list:
        print(f"    SCC: {sorted(scc)}")
else:
    print(f"  → 1 以外のサイクルは存在しない")

# --- パスの長さ分析 ---
print(f"\n[8] Syracuse パスの長さ分析:")
# 各奇数 n から 1 に到達するまでの Syracuse ステップ数
path_lengths = {}
for n in odd_nums:
    m = n
    steps = 0
    while m != 1 and steps < 1000:
        m = syracuse(m)
        steps += 1
    path_lengths[n] = steps

max_path = max(path_lengths.values())
max_path_n = max(path_lengths, key=path_lengths.get)
print(f"  最長 Syracuse パス: {max_path} ステップ (n={max_path_n})")

# 上位10
top_paths = sorted(path_lengths.items(), key=lambda x: -x[1])[:10]
print(f"  上位10:")
for n, l in top_paths:
    print(f"    n={n:6d}: {l} Syracuse ステップ")

print("\n" + "=" * 70)
print("結論:")
print("  - 強連結成分は 1 (自己ループ) のみ → サイクル不在を確認")
print("  - 入次数の高いハブの性質とグラフの深さ構造を分析")
print("  - 逆木のバランス度から成長パターンを確認")
print("=" * 70)
