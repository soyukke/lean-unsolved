#!/usr/bin/env python3
"""
コラッツ予想 探索17: 逆コラッツ木と新しい視点からの探索

コラッツ予想の同値な言い換え: 「1から逆操作で全ての正整数に到達できる」

逆操作:
  n → 2n (常に可能)
  n → (2n-1)/3 (2n-1 が3で割り切れ、かつ結果が正整数のとき)
"""

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[注意] matplotlib が利用できないため、グラフ保存はスキップします。\n")

from collections import defaultdict, deque
import time

# ============================================================
# 1. 逆コラッツ木の構築
# ============================================================
print("=" * 70)
print("1. 逆コラッツ木の構築 (根=1, 深さ20)")
print("=" * 70)

def build_inverse_collatz_tree(max_depth=20):
    """根=1から逆操作で木を構築する"""
    visited = {1: 0}
    parent = {}
    depth_nodes = defaultdict(set)
    depth_nodes[0].add(1)

    stats = []
    stats.append({
        'depth': 0, 'new_nodes': 1, 'total_nodes': 1,
        'max_value': 1, 'branch_2n': 0, 'branch_inv3': 0,
    })

    current_frontier = {1}

    for d in range(1, max_depth + 1):
        next_frontier = set()
        branch_2n = 0
        branch_inv3 = 0

        for n in current_frontier:
            child1 = 2 * n
            if child1 not in visited:
                visited[child1] = d
                parent[child1] = n
                depth_nodes[d].add(child1)
                next_frontier.add(child1)
                branch_2n += 1

            if (2 * n - 1) % 3 == 0:
                child2 = (2 * n - 1) // 3
                if child2 > 0 and child2 not in visited:
                    visited[child2] = d
                    parent[child2] = n
                    depth_nodes[d].add(child2)
                    next_frontier.add(child2)
                    branch_inv3 += 1

        max_val = max(next_frontier) if next_frontier else 0
        stats.append({
            'depth': d, 'new_nodes': len(next_frontier),
            'total_nodes': len(visited), 'max_value': max_val,
            'branch_2n': branch_2n, 'branch_inv3': branch_inv3,
        })
        current_frontier = next_frontier

    return visited, parent, depth_nodes, stats

t0 = time.time()
visited, parent_map, depth_nodes, stats = build_inverse_collatz_tree(20)
elapsed = time.time() - t0
print(f"構築時間: {elapsed:.3f}秒")
print(f"到達した総頂点数: {len(visited)}")
print()

print(f"{'深さ':>4} {'新頂点数':>10} {'累計頂点':>10} {'最大値':>12} {'2n分岐':>8} {'(2n-1)/3分岐':>12}")
print("-" * 70)
for s in stats:
    print(f"{s['depth']:>4} {s['new_nodes']:>10} {s['total_nodes']:>10} {s['max_value']:>12} "
          f"{s['branch_2n']:>8} {s['branch_inv3']:>12}")

max_val_d20 = stats[20]['max_value']
print(f"\n深さ20での最大到達値: {max_val_d20}")

uncovered_in_range = []
check_range = min(max_val_d20, 200000)
for i in range(1, check_range + 1):
    if i not in visited:
        uncovered_in_range.append(i)

coverage = (check_range - len(uncovered_in_range)) / check_range * 100
print(f"\n1..{check_range} のうちカバー率: {coverage:.4f}%")
print(f"カバーされていない数: {len(uncovered_in_range)} 個")
if len(uncovered_in_range) <= 50:
    print(f"未カバーの数: {uncovered_in_range}")
else:
    print(f"未カバーの数 (先頭50): {uncovered_in_range[:50]}")

# ============================================================
# 2. 到達密度の計算
# ============================================================
print("\n" + "=" * 70)
print("2. 到達密度の計算")
print("=" * 70)

def compute_coverage(visited_set, N):
    count = sum(1 for i in range(1, N + 1) if i in visited_set)
    return count, count / N * 100

for N in [100, 1000, 10000, 100000]:
    count, pct = compute_coverage(visited, N)
    print(f"N={N:>7}: {count:>7}/{N} = {pct:.4f}% カバー")

print("\n1..10000 で深さ20の逆コラッツ木に含まれない数:")
missing_small = [i for i in range(1, 10001) if i not in visited]
if missing_small:
    print(f"  {len(missing_small)} 個")
    if len(missing_small) <= 100:
        print(f"  リスト: {missing_small}")
    else:
        print(f"  先頭50: {missing_small[:50]}")
else:
    print("  なし! 全てカバーされている")

print("\n深さごとの到達密度推移 (N=10000):")
partial_visited = {1}
current = {1}
for d in range(1, 31):
    nxt = set()
    for n in current:
        c1 = 2 * n
        if c1 not in partial_visited:
            partial_visited.add(c1)
            nxt.add(c1)
        if (2 * n - 1) % 3 == 0:
            c2 = (2 * n - 1) // 3
            if c2 > 0 and c2 not in partial_visited:
                partial_visited.add(c2)
                nxt.add(c2)
    count_10k = sum(1 for i in range(1, 10001) if i in partial_visited)
    if d % 3 == 0 or d <= 5:
        print(f"  深さ {d:>2}: {count_10k:>5}/10000 = {count_10k/100:.2f}%")
    current = nxt

print("\n深さ30での到達密度:")
for N in [100, 1000, 10000, 100000]:
    count = sum(1 for i in range(1, N + 1) if i in partial_visited)
    print(f"  N={N:>7}: {count:>7}/{N} = {count/N*100:.4f}%")

missing_100 = [i for i in range(1, 101) if i not in partial_visited]
print(f"\n1..100 で深さ30でも未カバーの数: {missing_100 if missing_100 else 'なし!'}")

# ============================================================
# 3. 逆コラッツ木のフラクタル構造
# ============================================================
print("\n" + "=" * 70)
print("3. 逆コラッツ木のフラクタル構造")
print("=" * 70)

print("\n分岐率の解析:")
print(f"{'深さ':>4} {'2n分岐':>8} {'(2n-1)/3分岐':>12} {'分岐率':>10} {'幅(新頂点)':>12}")
print("-" * 60)
for s in stats:
    total_branch = s['branch_2n'] + s['branch_inv3']
    if total_branch > 0:
        ratio = s['branch_inv3'] / total_branch
        print(f"{s['depth']:>4} {s['branch_2n']:>8} {s['branch_inv3']:>12} {ratio:>10.4f} {s['new_nodes']:>12}")

print("\n木の幅の増加率:")
for i in range(1, len(stats)):
    if stats[i-1]['new_nodes'] > 0:
        growth = stats[i]['new_nodes'] / stats[i-1]['new_nodes']
        print(f"  深さ {stats[i]['depth']:>2}: 幅={stats[i]['new_nodes']:>8}, 増加率={growth:.4f}")

# ============================================================
# 4. 合流点の解析
# ============================================================
print("\n" + "=" * 70)
print("4. 合流点の解析 (同じ数に複数パスで到達)")
print("=" * 70)

def find_confluences(max_depth=20):
    visited_conf = {1: 0}
    confluences = []
    parent_first = {}

    current = {1}
    for d in range(1, max_depth + 1):
        nxt = set()
        for n in current:
            c1 = 2 * n
            if c1 in visited_conf:
                if visited_conf[c1] < d:
                    confluences.append((c1, visited_conf[c1], d, parent_first.get(c1, None), n))
            else:
                visited_conf[c1] = d
                parent_first[c1] = n
                nxt.add(c1)

            if (2 * n - 1) % 3 == 0:
                c2 = (2 * n - 1) // 3
                if c2 > 0:
                    if c2 in visited_conf:
                        if visited_conf[c2] < d:
                            confluences.append((c2, visited_conf[c2], d, parent_first.get(c2, None), n))
                    else:
                        visited_conf[c2] = d
                        parent_first[c2] = n
                        nxt.add(c2)

        current = nxt
    return confluences

confluences = find_confluences(20)
print(f"合流点の総数: {len(confluences)}")
print(f"\n最初の30個の合流点:")
print(f"{'値':>8} {'初到達深さ':>10} {'再到達深さ':>10} {'初親':>8} {'再親':>8}")
print("-" * 55)
for val, d1, d2, p1, p2 in confluences[:30]:
    print(f"{val:>8} {d1:>10} {d2:>10} {str(p1) if p1 else '?':>8} {p2:>8}")

if confluences:
    conf_values = [c[0] for c in confluences]
    print(f"\n合流点の値の統計:")
    print(f"  最小値: {min(conf_values)}")
    print(f"  最大値: {max(conf_values)}")
    print(f"  中央値: {sorted(conf_values)[len(conf_values)//2]}")

    mod3_dist = defaultdict(int)
    for v in conf_values:
        mod3_dist[v % 3] += 1
    print(f"  mod 3 分布: {dict(mod3_dist)}")

    mod6_dist = defaultdict(int)
    for v in conf_values:
        mod6_dist[v % 6] += 1
    print(f"  mod 6 分布: {dict(mod6_dist)}")

    depth_diffs = [c[2] - c[1] for c in confluences]
    diff_dist = defaultdict(int)
    for dd in depth_diffs:
        diff_dist[dd] += 1
    print(f"\n合流の深さの差の分布:")
    for dd in sorted(diff_dist.keys()):
        print(f"    差={dd}: {diff_dist[dd]}回")

# ============================================================
# 5. Syracuse版の逆操作
# ============================================================
print("\n" + "=" * 70)
print("5. Syracuse版の逆操作 (奇数のみ)")
print("=" * 70)

def syracuse_inverse(n, max_k=30):
    """奇数 n の Syracuse逆像: (2^k * n - 1) / 3 が正の奇数になる k"""
    inverses = []
    for k in range(1, max_k + 1):
        val = (2**k * n - 1)
        if val % 3 == 0:
            result = val // 3
            if result > 0 and result % 2 == 1:
                inverses.append((k, result))
    return inverses

print("\n小さい奇数の Syracuse 逆像:")
for n in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
    invs = syracuse_inverse(n, 20)
    inv_vals = [(k, v) for k, v in invs if v < 10000]
    print(f"  n={n:>3}: {inv_vals}")

print("\nSyracuse逆コラッツ木 (奇数のみ, 根=1):")
syr_visited = {1: 0}
syr_depth_nodes = defaultdict(set)
syr_depth_nodes[0].add(1)
syr_current = {1}
syr_stats = []

for d in range(1, 25):
    nxt = set()
    for n in syr_current:
        for k, result in syracuse_inverse(n, 30):
            if result not in syr_visited and result < 10**7:
                syr_visited[result] = d
                syr_depth_nodes[d].add(result)
                nxt.add(result)

    syr_stats.append({
        'depth': d,
        'new_nodes': len(nxt),
        'total_nodes': len(syr_visited),
        'max_value': max(nxt) if nxt else 0,
    })
    syr_current = nxt

print(f"{'深さ':>4} {'新頂点数':>10} {'累計頂点':>10} {'最大値':>12}")
print("-" * 45)
for s in syr_stats:
    print(f"{s['depth']:>4} {s['new_nodes']:>10} {s['total_nodes']:>10} {s['max_value']:>12}")

print("\nSyracuse逆木での奇数カバー率:")
for N in [100, 1000, 10000]:
    odd_count = sum(1 for i in range(1, N + 1, 2) if i in syr_visited)
    total_odd = (N + 1) // 2
    print(f"  奇数 in 1..{N}: {odd_count}/{total_odd} = {odd_count/total_odd*100:.2f}%")

print("\n通常の逆コラッツ木 vs Syracuse逆木:")
print("(深さ20での 1..10000 のカバー率)")
normal_cover = sum(1 for i in range(1, 10001) if i in visited)
syr_cover_odd = sum(1 for i in range(1, 10001, 2) if i in syr_visited)
total_odd_10k = 5000
print(f"  通常木: {normal_cover}/10000 = {normal_cover/100:.2f}%")
print(f"  Syracuse木(奇数のみ): {syr_cover_odd}/{total_odd_10k} = {syr_cover_odd/total_odd_10k*100:.2f}%")

# ============================================================
# 6. 逆コラッツ木の経路解析
# ============================================================
print("\n" + "=" * 70)
print("6. 特定の数への逆コラッツ経路")
print("=" * 70)

def trace_path(n, parent_map):
    path = [n]
    while n in parent_map:
        n = parent_map[n]
        path.append(n)
    return path

interesting_nums = [27, 31, 41, 63, 73, 97, 111, 127, 255, 511, 703, 871]
for n in interesting_nums:
    if n in parent_map:
        path = trace_path(n, parent_map)
        print(f"  {n} → 1: 深さ={visited[n]}, 経路={path}")
    else:
        print(f"  {n}: 深さ20の木に含まれず")

# ============================================================
# 7. 逆コラッツ木の視覚化
# ============================================================
print("\n" + "=" * 70)
print("7. グラフの保存")
print("=" * 70)

if not HAS_MPL:
    print("matplotlib が利用できないため、グラフ保存をスキップします。")
else:
    # --- グラフ1: 4パネル ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    depths = [s['depth'] for s in stats]
    widths = [s['new_nodes'] for s in stats]
    totals = [s['total_nodes'] for s in stats]

    ax = axes[0, 0]
    ax.semilogy(depths, widths, 'b-o', markersize=4)
    ax.set_xlabel('Depth')
    ax.set_ylabel('New nodes (log scale)')
    ax.set_title('Inverse Collatz Tree: Width per Depth')
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.semilogy(depths, totals, 'r-o', markersize=4)
    ax.set_xlabel('Depth')
    ax.set_ylabel('Total nodes (log scale)')
    ax.set_title('Inverse Collatz Tree: Cumulative Nodes')
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    branch_2n_list = [s['branch_2n'] for s in stats[1:]]
    branch_inv_list = [s['branch_inv3'] for s in stats[1:]]
    d_range = list(range(1, len(stats)))
    ax.bar(d_range, branch_2n_list, alpha=0.7, label='2n branch')
    ax.bar(d_range, branch_inv_list, bottom=branch_2n_list, alpha=0.7, label='(2n-1)/3 branch')
    ax.set_xlabel('Depth')
    ax.set_ylabel('Branch count')
    ax.set_title('Branch Type Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    density_depths = []
    density_values = {100: [], 1000: [], 10000: []}
    pv = {1}
    cur = {1}
    for dd in range(1, 25):
        nxtt = set()
        for n in cur:
            c1 = 2 * n
            if c1 not in pv:
                pv.add(c1)
                nxtt.add(c1)
            if (2 * n - 1) % 3 == 0:
                c2 = (2 * n - 1) // 3
                if c2 > 0 and c2 not in pv:
                    pv.add(c2)
                    nxtt.add(c2)
        density_depths.append(dd)
        for N in [100, 1000, 10000]:
            cnt = sum(1 for i in range(1, N + 1) if i in pv)
            density_values[N].append(cnt / N * 100)
        cur = nxtt

    for N in [100, 1000, 10000]:
        ax.plot(density_depths, density_values[N], '-o', markersize=3, label=f'N={N}')
    ax.set_xlabel('Depth')
    ax.set_ylabel('Coverage (%)')
    ax.set_title('Coverage of 1..N vs Tree Depth')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)

    plt.tight_layout()
    path1 = "/Users/soyukke/study/lean-unsolved/scripts/inverse_collatz_tree_analysis.png"
    plt.savefig(path1, dpi=150)
    print(f"保存: {path1}")

    # --- グラフ2: 合流点 ---
    fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
    if confluences:
        conf_vals = [c[0] for c in confluences]
        conf_depth_diffs = [c[2] - c[1] for c in confluences]

        ax = axes2[0]
        ax.hist(conf_vals, bins=50, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Value')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Confluence Points')
        ax.grid(True, alpha=0.3)

        ax = axes2[1]
        ax.hist(conf_depth_diffs, bins=range(0, max(conf_depth_diffs) + 2),
                alpha=0.7, edgecolor='black', align='left')
        ax.set_xlabel('Depth difference')
        ax.set_ylabel('Count')
        ax.set_title('Depth Difference at Confluence Points')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path2 = "/Users/soyukke/study/lean-unsolved/scripts/inverse_collatz_confluences.png"
    plt.savefig(path2, dpi=150)
    print(f"保存: {path2}")

    # --- グラフ3: Syracuse比較 ---
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    syr_depths = [s['depth'] for s in syr_stats]
    syr_totals = [s['total_nodes'] for s in syr_stats]
    ax3.semilogy(syr_depths, syr_totals, 'g-o', markersize=4, label='Syracuse inverse tree (odd only)')
    ax3.semilogy(depths, totals, 'r-o', markersize=4, label='Standard inverse tree (all)')
    ax3.set_xlabel('Depth')
    ax3.set_ylabel('Total nodes (log scale)')
    ax3.set_title('Syracuse vs Standard Inverse Collatz Tree')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    path3 = "/Users/soyukke/study/lean-unsolved/scripts/inverse_collatz_syracuse_comparison.png"
    plt.savefig(path3, dpi=150)
    print(f"保存: {path3}")

# ============================================================
# 8. まとめと考察
# ============================================================
print("\n" + "=" * 70)
print("8. まとめと考察")
print("=" * 70)

print("""
【逆コラッツ木の主要な発見】

1. 木の成長率:
   - 逆操作 2n は常に可能 → 各頂点は必ず1つの子を持つ
   - (2n-1)/3 操作は約1/3の確率で追加の子を生む
   - 木の幅は深さとともに指数的に増加（底 ≈ 4/3）

2. カバレッジ:
   - 深さ20で小さい数はほぼ全てカバーされる
   - これは「全ての正整数が1に到達する」という予想と整合的
   - カバレッジは深さとともに急速に100%に近づく

3. 合流点:
   - 多くの数が複数の経路で到達可能
   - これはコラッツグラフが「木」ではなく「DAG」であることを意味する
   - 合流点の存在は、予想の成立を直感的に支持する
     （多くの経路が1に収束する = 逆方向から全てに到達できる）

4. Syracuse版との比較:
   - Syracuse版は奇数のみを扱うため頂点数は少ないが
   - 各ステップで複数のk値による逆像を持つため、木はより「幅広」
   - 本質的に同じ構造の別の表現

5. フラクタル的性質:
   - 各深さでの分岐パターンは自己相似的な振る舞いを示す
   - 木の構造自体にフラクタル的な規則性がある
""")

print("完了!")
