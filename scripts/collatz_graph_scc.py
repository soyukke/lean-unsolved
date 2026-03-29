"""
コラッツグラフの到達可能性と強連結成分(SCC)分析

n -> T(n) の有向グラフ（Syracuse関数）を構築し:
1. 強連結成分(SCC)の数・サイズ分布
2. 頂点1からの逆方向到達距離分布
3. 最長パスの特定
4. グラフ理論的特徴量の計算
を行う。
"""

import time
import sys
from collections import defaultdict, deque

def syracuse(n):
    """Syracuse関数: T(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    if n % 2 == 0:
        raise ValueError("Syracuse function is defined for odd n only")
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def collatz_step(n):
    """Standard Collatz: even -> n/2, odd -> 3n+1"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def collatz_to_one(n, max_steps=10000):
    """nから1への到達ステップ数を返す"""
    steps = 0
    while n != 1 and steps < max_steps:
        n = collatz_step(n)
        steps += 1
    return steps if n == 1 else -1

# ===== Part 1: Syracuse グラフ構築と SCC 分析 =====
print("=" * 70)
print("Part 1: Syracuse グラフ (奇数のみ) の SCC 分析")
print("=" * 70)

N_values = [1000, 10000, 50000, 100000]

for N in N_values:
    t0 = time.time()

    # 奇数ノードのみ
    odd_nodes = set(range(1, N + 1, 2))

    # Syracuse グラフ: n -> T(n) の辺
    # T(n) が N を超える場合は辺を追加しない（外部ノード扱い）
    graph = {}      # 順方向: n -> T(n)
    rev_graph = defaultdict(list)  # 逆方向: T(n) -> [n]

    for n in odd_nodes:
        t = syracuse(n)
        graph[n] = t
        if t in odd_nodes:
            rev_graph[t].append(n)

    # Tarjan の SCC アルゴリズム（スタックベース反復版）
    index_counter = [0]
    stack = []
    on_stack = set()
    index_map = {}
    lowlink = {}
    sccs = []

    def strongconnect_iterative(v):
        """反復版 Tarjan"""
        work_stack = [(v, 0)]  # (node, neighbor_index)
        call_stack = []

        while work_stack:
            node, ni = work_stack.pop()

            if ni == 0:
                # 初回訪問
                index_map[node] = index_counter[0]
                lowlink[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)

            # node の後続ノード
            succ = graph.get(node)
            neighbors = [succ] if (succ is not None and succ in odd_nodes) else []

            if ni < len(neighbors):
                w = neighbors[ni]
                work_stack.append((node, ni + 1))

                if w not in index_map:
                    work_stack.append((w, 0))
                elif w in on_stack:
                    lowlink[node] = min(lowlink[node], index_map[w])
            else:
                # 全ての隣接ノードを処理済み
                if lowlink[node] == index_map[node]:
                    scc = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        scc.append(w)
                        if w == node:
                            break
                    sccs.append(scc)

                # 呼び出し元の lowlink を更新
                if work_stack:
                    parent = work_stack[-1][0]
                    if parent in lowlink and node in lowlink:
                        lowlink[parent] = min(lowlink[parent], lowlink[node])

    # 全奇数ノードに対して SCC 計算
    sys.setrecursionlimit(max(10000, N + 100))
    for n in sorted(odd_nodes):
        if n not in index_map:
            strongconnect_iterative(n)

    # SCC 分析
    scc_sizes = sorted([len(s) for s in sccs], reverse=True)
    num_sccs = len(sccs)
    trivial_sccs = sum(1 for s in scc_sizes if s == 1)  # サイズ1
    nontrivial_sccs = sum(1 for s in scc_sizes if s > 1)

    # 1を含むSCCを特定
    scc_containing_1 = None
    for scc in sccs:
        if 1 in scc:
            scc_containing_1 = sorted(scc)
            break

    elapsed = time.time() - t0

    print(f"\n--- N = {N} (奇数ノード数: {len(odd_nodes)}) ---")
    print(f"  SCC 総数: {num_sccs}")
    print(f"  自明SCC (サイズ1): {trivial_sccs}")
    print(f"  非自明SCC (サイズ>1): {nontrivial_sccs}")
    if nontrivial_sccs > 0:
        print(f"  非自明SCCのサイズ: {[s for s in scc_sizes if s > 1]}")
    print(f"  1を含むSCC: サイズ={len(scc_containing_1) if scc_containing_1 else 0}")
    if scc_containing_1 and len(scc_containing_1) <= 10:
        print(f"    要素: {scc_containing_1}")
    print(f"  計算時間: {elapsed:.2f}秒")


# ===== Part 2: 標準コラッツグラフ (全整数) の分析 =====
print("\n" + "=" * 70)
print("Part 2: 標準コラッツグラフ (n=1..N) の距離分析")
print("=" * 70)

N2 = 100000

# 1への到達ステップ数を計算
print(f"\nN = {N2} について1への到達ステップ数を計算中...")
t0 = time.time()

steps_to_one = {}
for n in range(1, N2 + 1):
    steps_to_one[n] = collatz_to_one(n)

elapsed = time.time() - t0
print(f"計算時間: {elapsed:.2f}秒")

# 統計量
max_steps = max(steps_to_one.values())
max_steps_n = max(steps_to_one, key=steps_to_one.get)
avg_steps = sum(steps_to_one.values()) / len(steps_to_one)

print(f"\n1への到達ステップ数の統計:")
print(f"  平均: {avg_steps:.2f}")
print(f"  最大: {max_steps} (n={max_steps_n})")
print(f"  到達失敗: {sum(1 for v in steps_to_one.values() if v == -1)}")

# ステップ数の分布
step_dist = defaultdict(int)
for s in steps_to_one.values():
    step_dist[s] += 1

print(f"\nステップ数分布 (上位20):")
for s in sorted(step_dist.keys(), key=lambda k: step_dist[k], reverse=True)[:20]:
    print(f"  ステップ {s}: {step_dist[s]} 個 ({100*step_dist[s]/N2:.2f}%)")


# ===== Part 3: 逆コラッツグラフ (1からの逆到達) の BFS 層構造 =====
print("\n" + "=" * 70)
print("Part 3: 逆コラッツグラフ - 1からの BFS 層構造")
print("=" * 70)

def collatz_predecessors(n, limit=10**7):
    """nの前駆ノード: n = m/2 -> m = 2n, n = 3m+1 -> m = (n-1)/3"""
    preds = []
    # n = m/2 のケース: m = 2n は常に前駆
    preds.append(2 * n)

    # n = 3m+1 のケース: m = (n-1)/3 が正整数で奇数
    if (n - 1) % 3 == 0 and n > 1:
        m = (n - 1) // 3
        if m > 0 and m % 2 == 1:  # mは奇数
            preds.append(m)

    return [p for p in preds if p <= limit]


N3 = 10**6
max_depth = 100

print(f"\n1からの逆方向BFS (ノード上限: {N3}, 深さ上限: {max_depth})")
t0 = time.time()

visited = {1}
current_layer = {1}
layer_sizes = [1]
layer_max = [1]
layer_min = [1]
covered_up_to = defaultdict(int)  # depth -> [1..N3]内のカバー数

depth = 0
while current_layer and depth < max_depth:
    depth += 1
    next_layer = set()
    for n in current_layer:
        for pred in collatz_predecessors(n, limit=N3):
            if pred not in visited:
                visited.add(pred)
                next_layer.add(pred)

    if not next_layer:
        break

    current_layer = next_layer
    layer_sizes.append(len(next_layer))
    layer_max.append(max(next_layer))
    layer_min.append(min(next_layer))

elapsed = time.time() - t0
total_visited = len(visited)

print(f"計算時間: {elapsed:.2f}秒")
print(f"到達深さ: {depth}")
print(f"訪問ノード総数: {total_visited}")
print(f"[1..{N3}]内カバー率: {sum(1 for v in visited if v <= N3)}/{N3} = {100*sum(1 for v in visited if v <= N3)/N3:.4f}%")

print(f"\n逆BFS層構造 (最初の30層):")
print(f"{'層':>4} {'ノード数':>10} {'最小値':>12} {'最大値':>12} {'成長率':>8}")
for i in range(min(30, len(layer_sizes))):
    growth = layer_sizes[i] / layer_sizes[i-1] if i > 0 and layer_sizes[i-1] > 0 else 0
    print(f"{i:>4} {layer_sizes[i]:>10} {layer_min[i]:>12} {layer_max[i]:>12} {growth:>8.3f}")

# 成長率の平均
if len(layer_sizes) > 5:
    growth_rates = [layer_sizes[i]/layer_sizes[i-1] for i in range(2, len(layer_sizes)) if layer_sizes[i-1] > 0]
    if growth_rates:
        print(f"\n平均成長率 (層2以降): {sum(growth_rates)/len(growth_rates):.4f}")
        print(f"中央値成長率: {sorted(growth_rates)[len(growth_rates)//2]:.4f}")


# ===== Part 4: Syracuse グラフの DAG 構造分析 =====
print("\n" + "=" * 70)
print("Part 4: Syracuse グラフの DAG 構造分析 (SCC縮約後)")
print("=" * 70)

N4 = 50000

# 奇数 Syracuse グラフ
odd_nodes_4 = list(range(1, N4 + 1, 2))
graph_4 = {}
for n in odd_nodes_4:
    t = syracuse(n)
    if t <= N4:
        graph_4[n] = t

# 1への最短パス(Syracuse)
print(f"\nSyracuse関数での1への到達ステップ数 (N={N4}, 奇数のみ)")
syr_steps = {}
for n in odd_nodes_4:
    curr = n
    steps = 0
    while curr != 1 and steps < 1000:
        curr = syracuse(curr)
        steps += 1
    syr_steps[n] = steps if curr == 1 else -1

max_syr = max(syr_steps.values())
max_syr_n = max(syr_steps, key=syr_steps.get)
avg_syr = sum(syr_steps.values()) / len(syr_steps)

print(f"  平均ステップ数: {avg_syr:.2f}")
print(f"  最大ステップ数: {max_syr} (n={max_syr_n})")

# Syracuse ステップ数 vs log(n) の関係
import math
print(f"\nSyracuse ステップ数 vs log2(n) の比率:")
for threshold in [100, 1000, 5000, 10000, 25000, 50000]:
    relevant = {n: s for n, s in syr_steps.items() if n <= threshold and n > 1}
    ratios = [s / math.log2(n) for n, s in relevant.items()]
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0
    print(f"  n <= {threshold:>6}: 平均比率 = {avg_ratio:.4f}")


# ===== Part 5: グラフの木構造度分析 =====
print("\n" + "=" * 70)
print("Part 5: グラフの木構造度分析")
print("=" * 70)

N5 = 100000

# 標準コラッツで逆グラフを構築 (1..N5)
# 各ノードの入次数(逆辺の数)を計算
in_degree = defaultdict(int)
out_node = {}

for n in range(1, N5 + 1):
    target = collatz_step(n)
    if target <= N5:
        in_degree[target] += 1
        out_node[n] = target

# 入次数分布
in_deg_dist = defaultdict(int)
for n in range(1, N5 + 1):
    in_deg_dist[in_degree[n]] += 1

print(f"\n入次数分布 (N={N5}):")
for d in sorted(in_deg_dist.keys()):
    print(f"  入次数 {d}: {in_deg_dist[d]} ノード ({100*in_deg_dist[d]/N5:.2f}%)")

# 葉ノード（前駆なし）の数
leaves = sum(1 for n in range(1, N5 + 1) if in_degree[n] == 0)
print(f"\n葉ノード数(入次数0): {leaves} ({100*leaves/N5:.2f}%)")

# 分岐ノード（入次数>=2）
branch_nodes = sum(1 for n in range(1, N5 + 1) if in_degree[n] >= 2)
print(f"分岐ノード数(入次数>=2): {branch_nodes} ({100*branch_nodes/N5:.2f}%)")

# 偶数/奇数別の入次数パターン
print(f"\n偶数ノードの入次数分布:")
even_in_deg = defaultdict(int)
for n in range(2, N5 + 1, 2):
    even_in_deg[in_degree[n]] += 1
for d in sorted(even_in_deg.keys()):
    print(f"  入次数 {d}: {even_in_deg[d]}")

print(f"\n奇数ノードの入次数分布:")
odd_in_deg = defaultdict(int)
for n in range(1, N5 + 1, 2):
    odd_in_deg[in_degree[n]] += 1
for d in sorted(odd_in_deg.keys()):
    print(f"  入次数 {d}: {odd_in_deg[d]}")


# ===== Part 6: 高度到達ノード（hub分析） =====
print("\n" + "=" * 70)
print("Part 6: 高入次数ノード (Hub) 分析")
print("=" * 70)

# 入次数の高い上位20ノード
top_hubs = sorted(range(1, N5 + 1), key=lambda n: in_degree[n], reverse=True)[:20]
print(f"\n入次数上位20ノード (N={N5}):")
print(f"{'ノード':>10} {'入次数':>8} {'偶奇':>4} {'2^k形':>8}")
for n in top_hubs:
    parity = "偶" if n % 2 == 0 else "奇"
    # 2の冪乗チェック
    is_pow2 = (n & (n - 1) == 0) if n > 0 else False
    pow2_str = f"2^{int(math.log2(n))}" if is_pow2 else "-"
    print(f"{n:>10} {in_degree[n]:>8} {parity:>4} {pow2_str:>8}")


print("\n" + "=" * 70)
print("分析完了")
print("=" * 70)
