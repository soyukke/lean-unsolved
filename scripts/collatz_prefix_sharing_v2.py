"""
Syracuse軌道のprefix共有分析 v2 (軽量版)
合流時間Lのペアで|n1-n2|が最小のものの構造を解析
"""
import math
import time
import json
from collections import defaultdict, Counter

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=300):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    traj = [n]
    c = n
    for _ in range(max_steps):
        if c == 1:
            break
        c = syracuse(c)
        traj.append(c)
    return traj

# ===== Part 1: 隣接奇数ペア(距離2)の合流時間 =====
print("Part 1: 隣接奇数ペア(距離2)の合流時間")
t0 = time.time()

dist2_results = {}  # L -> [(n1, n2, meeting_point)]
L_counts = Counter()

for n in range(1, 8001, 2):
    n2 = n + 2
    o1 = orbit(n)
    o2 = orbit(n2)
    mlen = min(len(o1), len(o2))
    L = None
    for k in range(mlen):
        if o1[k] == o2[k]:
            L = k
            break
    if L is not None and L > 0:
        L_counts[L] += 1
        mp = o1[L]
        if L not in dist2_results:
            dist2_results[L] = []
        if len(dist2_results[L]) < 5:
            dist2_results[L].append((n, n2, mp))

print(f"  計算時間: {time.time()-t0:.1f}s")
total = sum(L_counts.values())
mean_L = sum(L*c for L,c in L_counts.items()) / total if total > 0 else 0
print(f"  ペア数: {total}, 平均合流時間: {mean_L:.3f}")

print(f"\n  L | count | 割合   | 例")
print("  " + "-"*60)
for L in sorted(L_counts.keys()):
    ex = dist2_results.get(L, [('?','?','?')])[0]
    pct = 100*L_counts[L]/total
    print(f"  {L:2d} | {L_counts[L]:5d} | {pct:5.1f}% | ({ex[0]}, {ex[1]}) -> {ex[2]}")

# ===== Part 2: 各合流時間Lでの最小距離（小範囲探索） =====
print(f"\nPart 2: 合流時間Lでの最小距離ペア")
t1 = time.time()

N_MAX = 800
odds = list(range(1, N_MAX, 2))
# 事前に全軌道を計算
orbits = {}
for n in odds:
    orbits[n] = orbit(n)

min_dist_by_L = {}  # L -> (dist, n1, n2, meeting)

# 距離の小さいペアから優先的にチェック
for gap in range(2, 200, 2):  # 距離2,4,6,...,198
    for n1 in range(1, N_MAX - gap, 2):
        n2 = n1 + gap
        if n2 >= N_MAX:
            break
        o1 = orbits[n1]
        o2 = orbits[n2]
        mlen = min(len(o1), len(o2))
        for k in range(mlen):
            if o1[k] == o2[k]:
                L = k
                if L > 0:
                    if L not in min_dist_by_L or gap < min_dist_by_L[L][0]:
                        min_dist_by_L[L] = (gap, n1, n2, o1[L])
                break

print(f"  計算時間: {time.time()-t1:.1f}s")
print(f"\n  L | min_dist | pair(n1,n2) | meeting | log2(dist) | dist/L")
print("  " + "-"*70)
for L in sorted(min_dist_by_L.keys()):
    d, n1, n2, mp = min_dist_by_L[L]
    log_d = math.log2(d) if d > 0 else 0
    print(f"  {L:2d} | {d:8d} | ({n1:5d},{n2:5d}) | {mp:6d} | {log_d:6.2f} | {d/L:.2f}")

# ===== Part 3: 逆像からの合流構成 =====
print(f"\nPart 3: 逆像からの合流ペア構成")

def preimages(m, max_a=22):
    """Syracuse逆像: (2^a * m - 1)/3 が奇数正整数"""
    res = []
    for a in range(1, max_a+1):
        num = (1 << a) * m - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1:
                res.append((n, a))
    return res

def build_inverse_tree(root, depth, max_a=20):
    """逆像木を構築。層ごとにノード集合を返す"""
    layers = [set([root])]
    all_seen = set([root])
    for d in range(depth):
        nxt = set()
        for m in layers[-1]:
            for n, a in preimages(m, max_a):
                if n not in all_seen:
                    nxt.add(n)
                    all_seen.add(n)
        layers.append(nxt)
    return layers

hubs = [1, 5, 7, 11, 13]
for hub in hubs:
    print(f"\n  --- 合流ハブ={hub}, 逆像木 ---")
    layers = build_inverse_tree(hub, depth=8, max_a=18)
    for d in range(1, len(layers)):
        nodes = sorted(layers[d])
        if len(nodes) < 2:
            if len(nodes) == 1:
                print(f"    depth={d}: |layer|={len(nodes)}, nodes={nodes}")
            else:
                print(f"    depth={d}: |layer|=0")
            continue
        # 最小距離
        min_gap = float('inf')
        best = None
        for i in range(len(nodes)-1):
            g = nodes[i+1] - nodes[i]
            if g < min_gap:
                min_gap = g
                best = (nodes[i], nodes[i+1])
        print(f"    depth={d}: |layer|={len(nodes):5d}, "
              f"min_gap={min_gap:10d}, pair={best}, "
              f"range=[{nodes[0]},{nodes[-1]}]")

# ===== Part 4: 距離のmod構造 =====
print(f"\nPart 4: 最小距離ペアのmod構造")
print(f"  L | dist | dist%3 | dist%4 | dist%6 | dist%8 | n1%3 | n2%3 | n1%8 | n2%8")
print("  " + "-"*80)
for L in sorted(min_dist_by_L.keys()):
    d, n1, n2, mp = min_dist_by_L[L]
    print(f"  {L:2d} | {d:5d} | {d%3:5d} | {d%4:5d} | {d%6:5d} | {d%8:5d} | "
          f"{n1%3:4d} | {n2%3:4d} | {n1%8:4d} | {n2%8:4d}")

# ===== Part 5: スケーリング分析 =====
print(f"\nPart 5: スケーリング分析")
Ls = sorted(min_dist_by_L.keys())
dists = [min_dist_by_L[L][0] for L in Ls]
log_dists = [math.log2(d) for d in dists]

# 線形回帰
if len(Ls) > 3:
    n_pts = len(Ls)
    sx = sum(Ls)
    sy = sum(log_dists)
    sxy = sum(L*ld for L,ld in zip(Ls, log_dists))
    sxx = sum(L**2 for L in Ls)

    slope = (n_pts * sxy - sx * sy) / (n_pts * sxx - sx**2)
    intercept = (sy - slope * sx) / n_pts

    # R^2
    y_pred = [slope * L + intercept for L in Ls]
    ss_res = sum((y - yp)**2 for y, yp in zip(log_dists, y_pred))
    ss_tot = sum((y - sy/n_pts)**2 for y in log_dists)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0

    print(f"  log2(min_dist) ~ {slope:.4f} * L + {intercept:.4f}")
    print(f"  R^2 = {r2:.4f}")
    print(f"  => min_dist ~ 2^({slope:.4f}*L) * 2^({intercept:.4f})")
    print(f"  => min_dist ~ {2**intercept:.4f} * {2**slope:.4f}^L")

    # log2(3/2) = 0.585 との比較
    print(f"  比較: log2(3/2) = {math.log2(1.5):.4f}")
    print(f"  比較: log2(2) = {math.log2(2):.4f}")

# ===== Part 6: 合流時間が同じペアの集合の構造 =====
print(f"\nPart 6: 同一合流時間L=1のペアの構造")
# T(n1) = T(n2) のペア → 逆像の全ペア
for m in [1, 5, 7]:
    pre = preimages(m, max_a=18)
    pre_nodes = sorted([n for n, a in pre])
    print(f"\n  T^{{-1}}({m}) = {pre_nodes[:15]} ...")
    print(f"  |T^{{-1}}({m})| = {len(pre_nodes)}")
    if len(pre_nodes) >= 2:
        gaps = [pre_nodes[i+1] - pre_nodes[i] for i in range(len(pre_nodes)-1)]
        print(f"  隣接ギャップ: {gaps[:15]} ...")
        # ギャップの比率
        if len(gaps) >= 2:
            ratios = [gaps[i+1]/gaps[i] for i in range(len(gaps)-1) if gaps[i] > 0]
            print(f"  ギャップ比率: {[f'{r:.3f}' for r in ratios[:10]]}")

# ===== JSON出力 =====
print(f"\n{'='*70}")
print("JSON Results")
print(f"{'='*70}")

result_json = {
    "dist2_L_distribution": {str(L): L_counts[L] for L in sorted(L_counts.keys())},
    "mean_confluence_time_dist2": round(mean_L, 3),
    "min_dist_by_L": {str(L): {"dist": d, "n1": n1, "n2": n2, "meeting": mp}
                      for L, (d, n1, n2, mp) in sorted(min_dist_by_L.items())},
    "scaling": {
        "slope": round(slope, 4) if len(Ls) > 3 else None,
        "intercept": round(intercept, 4) if len(Ls) > 3 else None,
        "r2": round(r2, 4) if len(Ls) > 3 else None,
    }
}
print(json.dumps(result_json, indent=2))
print(f"\nTotal time: {time.time()-t0:.1f}s")
