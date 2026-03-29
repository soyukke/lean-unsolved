"""
探索163 Part 2: 「最初の合流点」確率の精密モデル

核心的洞察:
- P(orbit ∋ 5) = 94% だが P(mp=5) = 42.5%
- P(orbit ∋ 1) = 100% だが P(mp=1) = 9.8%
- つまり「通過する」と「最初に合流する」は全く違う
- mp=v ⟺ v は軌道の「最も早い共有点」

モデル:
P(mp=v) = P(both pass v) * P(v is first shared | both pass v)
        = P(pass_a ∋ v) * P(pass_b ∋ v) * P(first | both)

P(first | both) は「vより前に共有点がない」確率
→ 軌道の構造（vに到達するまでの経路の独立性）に依存
"""

import math
from collections import defaultdict, Counter

def syracuse(n):
    assert n % 2 == 1
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def odd_collatz_sequence(n):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    seq = [n]
    while n != 1:
        n = syracuse(n)
        seq.append(n)
    return seq

# === Part A: 軌道の階層構造 ===
# 1→...→5→...→1 の軌道: 5→16→8→4→2→1
# したがって5を通過するすべての軌道は1も通過する
# でもmp=5 > mp=1 ⟹ 多くのペアは5で「最初に」合流する（1に到達する前に）

print("=" * 70)
print("Part A: 軌道の階層構造と合流点の優先関係")
print("=" * 70)

# 5から1への経路
seq_5 = odd_collatz_sequence(5)
print(f"orbit(5) = {seq_5}")

# 11から1への経路
seq_11 = odd_collatz_sequence(11)
print(f"orbit(11) = {seq_11}")

# 23から1への経路
seq_23 = odd_collatz_sequence(23)
print(f"orbit(23) = {seq_23}")

# === Part B: 「5が最初の合流点」になる条件の分析 ===

print("\n" + "=" * 70)
print("Part B: 5が最初の合流点になる条件")
print("=" * 70)

# n=1,...,5000の奇数について、軌道のどの位置で5に到達するか
N = 5000
reach_5_step = {}  # n -> step where 5 is first reached
for n in range(1, N+1, 2):
    seq = odd_collatz_sequence(n)
    for i, x in enumerate(seq):
        if x == 5:
            reach_5_step[n] = i
            break

print(f"  5に到達する奇数の数: {len(reach_5_step)}/{N//2}")
if reach_5_step:
    steps = list(reach_5_step.values())
    print(f"  到達ステップ数: min={min(steps)}, max={max(steps)}, mean={sum(steps)/len(steps):.1f}")

# ステップ数の分布
step_dist = Counter(steps)
print(f"  ステップ数分布 (上位):")
for s in sorted(step_dist.keys())[:20]:
    print(f"    step={s:3d}: count={step_dist[s]:5d} ({step_dist[s]/len(steps)*100:.1f}%)")

# === Part C: 隣接ペアが5で合流する詳細条件 ===

print("\n" + "=" * 70)
print("Part C: 隣接ペアが5で合流する詳細メカニズム")
print("=" * 70)

# 隣接ペア(n, n+2)が5で合流 ⟺
# (1) both pass through 5
# (2) 5に到達するまでの軌道が完全に分離（共有点なし）

merge_at_5 = []
merge_at_other = []
both_pass_5 = 0
only_one_pass_5 = 0
neither_pass_5 = 0

for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)

    # 合流点を見つける
    set_n = set(seq_n)
    mp = None
    for x in seq_m:
        if x in set_n:
            mp = x
            break

    n_passes_5 = 5 in set_n
    m_passes_5 = 5 in set(seq_m)

    if n_passes_5 and m_passes_5:
        both_pass_5 += 1
        if mp == 5:
            merge_at_5.append((n, m))
        else:
            merge_at_other.append((n, m, mp))
    elif n_passes_5 or m_passes_5:
        only_one_pass_5 += 1
    else:
        neither_pass_5 += 1

total_adj = (N - 1) // 2
print(f"  隣接奇数ペア総数: {total_adj}")
print(f"  両方5を通過: {both_pass_5} ({both_pass_5/total_adj*100:.1f}%)")
print(f"  片方だけ5を通過: {only_one_pass_5} ({only_one_pass_5/total_adj*100:.1f}%)")
print(f"  どちらも通過しない: {neither_pass_5} ({neither_pass_5/total_adj*100:.1f}%)")
print(f"  両方通過 & mp=5: {len(merge_at_5)} ({len(merge_at_5)/total_adj*100:.1f}%)")
print(f"  両方通過 & mp≠5: {len(merge_at_other)} ({len(merge_at_other)/total_adj*100:.1f}%)")
print(f"  P(mp=5 | both pass 5) = {len(merge_at_5)/both_pass_5:.4f}")

# mp≠5 のとき、合流点は5の上流？下流？
print(f"\n  mp≠5の場合の合流点分布:")
other_mp_counter = Counter()
for n, m, mp in merge_at_other:
    other_mp_counter[mp] += 1
for v, c in other_mp_counter.most_common(10):
    # vは5の上流(5→...→v→...→1)か下流(v→...→5→...→1)?
    orbit_v = set(odd_collatz_sequence(v))
    relation = "5の下流(v→5)" if 5 in orbit_v else "5の上流(5→v) or 独立"
    print(f"    mp={v:6d}: count={c:4d}, {relation}")

# === Part D: 軌道分岐の構造的分析 ===

print("\n" + "=" * 70)
print("Part D: 隣接ペアの軌道分岐パターン")
print("=" * 70)

# 隣接奇数 n, n+2 の軌道がどこで分岐してどこで合流するか
# 特に n → ... → 5 と n+2 → ... → 5 の経路の独立性

# n ≡ r (mod 6) による分類
mod6_stats = defaultdict(lambda: {'total': 0, 'mp5': 0})
for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)
    set_n = set(seq_n)
    mp = None
    for x in seq_m:
        if x in set_n:
            mp = x
            break

    r = n % 6
    mod6_stats[r]['total'] += 1
    if mp == 5:
        mod6_stats[r]['mp5'] += 1

print(f"\nmod 6 による合流点=5 の確率:")
for r in sorted(mod6_stats.keys()):
    s = mod6_stats[r]
    print(f"  n ≡ {r} (mod 6): P(mp=5) = {s['mp5']}/{s['total']} = {s['mp5']/s['total']:.4f}")

# mod 12 分類
mod12_stats = defaultdict(lambda: {'total': 0, 'mp5': 0})
for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)
    set_n = set(seq_n)
    mp = None
    for x in seq_m:
        if x in set_n:
            mp = x
            break

    r = n % 12
    mod12_stats[r]['total'] += 1
    if mp == 5:
        mod12_stats[r]['mp5'] += 1

print(f"\nmod 12 による合流点=5 の確率:")
for r in sorted(mod12_stats.keys()):
    s = mod12_stats[r]
    if s['total'] > 0:
        print(f"  n ≡ {r:2d} (mod 12): P(mp=5) = {s['mp5']:4d}/{s['total']:4d} = {s['mp5']/s['total']:.4f}")

# === Part E: 5に到達するステップ差の分析 ===

print("\n" + "=" * 70)
print("Part E: 隣接ペアの5到達ステップ差とmp=5の関係")
print("=" * 70)

step_diff_mp5 = []
step_diff_other = []
for n in range(1, N-1, 2):
    m = n + 2
    if n in reach_5_step and m in reach_5_step:
        diff = abs(reach_5_step[n] - reach_5_step[m])
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        set_n = set(seq_n)
        mp = None
        for x in seq_m:
            if x in set_n:
                mp = x
                break
        if mp == 5:
            step_diff_mp5.append(diff)
        else:
            step_diff_other.append(diff)

if step_diff_mp5:
    print(f"  mp=5のとき: avg |step_a - step_b| = {sum(step_diff_mp5)/len(step_diff_mp5):.2f}")
    print(f"    ステップ差分布: {Counter(step_diff_mp5).most_common(10)}")
if step_diff_other:
    print(f"  mp≠5のとき: avg |step_a - step_b| = {sum(step_diff_other)/len(step_diff_other):.2f}")
    print(f"    ステップ差分布: {Counter(step_diff_other).most_common(10)}")

# === Part F: 逆像木の「流域」による説明 ===

print("\n" + "=" * 70)
print("Part F: 逆像木の流域（Basin）モデル")
print("=" * 70)

# 各奇数nについて、「最初に到達する主要合流候補」を記録
# = 軌道上で最初に到達する {1, 5, 11} のどれか

first_major = Counter()
for n in range(1, N+1, 2):
    seq = odd_collatz_sequence(n)
    for x in seq:
        if x in {1, 5, 11}:
            first_major[x] += 1
            break

total_odd = N // 2
print(f"\n最初に到達する主要点の分布 ({1}, {5}, {11}):")
for v in [1, 5, 11]:
    print(f"  first_reach = {v}: {first_major[v]}/{total_odd} = {first_major[v]/total_odd:.4f}")

# さらに細かく: 5より前に11に到達するか
reach_order = Counter()  # (first of {5, 11}) -> count
for n in range(1, N+1, 2):
    seq = odd_collatz_sequence(n)
    for x in seq:
        if x == 5:
            reach_order['5 first'] += 1
            break
        elif x == 11:
            reach_order['11 first'] += 1
            break

print(f"\n5 vs 11 の到達順序:")
for k, v in reach_order.most_common():
    print(f"  {k}: {v}/{total_odd} = {v/total_odd:.4f}")

# === Part G: 逆像木の深さと合流確率の関係 ===

print("\n" + "=" * 70)
print("Part G: 逆BFSの深さごとの累積到達率と合流確率")
print("=" * 70)

def inverse_syracuse_all(m, N_max):
    preimages = []
    for j in range(1, 60):
        num = m * (1 << j) - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1 and n <= N_max:
                preimages.append(n)
            if n > N_max:
                break
    return preimages

def inverse_bfs_by_depth(root, max_depth, N_max):
    """各depth毎の到達数を記録"""
    current = {root}
    all_reached = {root}
    depth_counts = {0: 1}
    for d in range(1, max_depth + 1):
        next_level = set()
        for m in current:
            for pre in inverse_syracuse_all(m, N_max):
                if pre not in all_reached:
                    next_level.add(pre)
                    all_reached.add(pre)
        current = next_level
        depth_counts[d] = len(all_reached)
        if not current:
            break
    return depth_counts, all_reached

N_max = 5000
max_depth = 25

for v in [1, 5, 11, 23, 17]:
    dc, reached = inverse_bfs_by_depth(v, max_depth, N_max)
    total_odd_v = N_max // 2
    print(f"\n  v={v}: 逆BFS到達率 (N_max={N_max})")
    for d in range(0, max_depth + 1, 3):
        if d in dc:
            frac = dc[d] / total_odd_v
            print(f"    depth={d:2d}: reached={dc[d]:5d}, frac={frac:.4f}")
