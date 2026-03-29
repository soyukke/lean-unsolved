"""
Syracuse軌道のprefix共有分析

T^k(n1) = T^k(n2) となる最小k（合流時間）がLのペア(n1,n2)で、
|n1-n2|が最小のものの構造を解析する。

逆像からの構成:
- Syracuse逆関数 T^{-1}(m) = {(2^a * m - 1)/3 : 2^a * m ≡ 1 (mod 3)}
- 合流点mからL段の逆像木を展開し、合流時間が正確にLとなるペアを列挙

目標:
1. 各合流時間Lに対し、最小距離ペアを発見
2. 最小距離の増加パターン（Lとの関係）を特定
3. 逆像木の分岐構造と最小距離の関係を解明
"""

import math
import json
import time
from collections import defaultdict, Counter
from itertools import combinations

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=500):
    """nからのSyracuse軌道（奇数列）"""
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    traj = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        traj.append(current)
    return traj

def syracuse_preimages(m, max_a=30):
    """
    Syracuse逆関数: T^{-1}(m) の全ての逆像を返す
    n = (2^a * m - 1)/3 が奇数の正整数になるもの
    """
    results = []
    for a in range(1, max_a + 1):
        num = (2**a) * m - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1 and n != m:  # 奇数で正で自分自身でない
                results.append((n, a))
    return results

def inverse_tree(root, depth, max_a=25):
    """
    rootからdepth段の逆像木を構築
    返り値: {depth_level: set of nodes}
    """
    layers = {0: {root}}
    current_layer = {root}

    for d in range(1, depth + 1):
        next_layer = set()
        for m in current_layer:
            for n, a in syracuse_preimages(m, max_a):
                # nが既に浅い層にいないことを確認（合流時間が正確にdとなるように）
                already_seen = False
                for dd in range(d):
                    if n in layers[dd]:
                        already_seen = True
                        break
                if not already_seen:
                    next_layer.add(n)
        layers[d] = next_layer
        current_layer = next_layer
    return layers


# ===== Phase 1: 各合流時間Lでの最小距離ペア（直接探索） =====
print("=" * 70)
print("Phase 1: 各合流時間Lでの最小距離ペア（直接全探索）")
print("=" * 70)

def find_confluence_time(n1, n2, max_steps=300):
    """n1, n2の合流時間（T^k(n1)=T^k(n2)となる最小k）を返す"""
    o1 = orbit(n1, max_steps)
    o2 = orbit(n2, max_steps)
    min_len = min(len(o1), len(o2))
    for k in range(min_len):
        if o1[k] == o2[k]:
            return k  # k=0はn1=n2の場合
    return None

N_LIMIT = 2000  # 奇数の探索範囲
odd_numbers = [n for n in range(1, N_LIMIT, 2)]

# 合流時間ごとの最小距離を記録
min_distance_by_L = {}  # L -> (min_dist, n1, n2, meeting_point)
all_pairs_by_L = defaultdict(list)

t0 = time.time()
for i, n1 in enumerate(odd_numbers):
    if time.time() - t0 > 30:  # 30秒制限
        print(f"  [時間制限で停止: {i}/{len(odd_numbers)}]")
        break
    for n2 in odd_numbers[i+1:]:
        if n2 - n1 > 500:  # 距離が大きすぎるペアはスキップ
            break
        L = find_confluence_time(n1, n2)
        if L is not None and L > 0:
            dist = n2 - n1
            if L not in min_distance_by_L or dist < min_distance_by_L[L][0]:
                # 合流点を特定
                o1 = orbit(n1, 300)
                meeting = o1[L] if L < len(o1) else None
                min_distance_by_L[L] = (dist, n1, n2, meeting)
            all_pairs_by_L[L].append((dist, n1, n2))

print(f"\n合流時間L | 最小距離 | ペア(n1,n2) | 合流点")
print("-" * 60)
for L in sorted(min_distance_by_L.keys()):
    dist, n1, n2, mp = min_distance_by_L[L]
    print(f"  L={L:3d}  | dist={dist:6d} | ({n1}, {n2}) | meet={mp}")


# ===== Phase 2: 逆像木からの構成 =====
print("\n" + "=" * 70)
print("Phase 2: 逆像木からの構成")
print("=" * 70)

# 主要合流ハブから逆像木を構築
hubs = [1, 5, 7, 11, 13, 17, 19, 21, 23]
max_depth = 10

for hub in hubs[:5]:  # 最初の5つ
    print(f"\n--- 合流ハブ: {hub} ---")
    layers = inverse_tree(hub, max_depth)

    for d in range(1, max_depth + 1):
        nodes = sorted(layers[d])
        if len(nodes) < 2:
            continue

        # 同じ層のノード間で最小距離を見つける
        min_dist = float('inf')
        best_pair = None
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                d_ij = abs(nodes[j] - nodes[i])
                if d_ij < min_dist:
                    min_dist = d_ij
                    best_pair = (nodes[i], nodes[j])

        if best_pair:
            # 検証: 合流時間が正確にdか
            actual_L = find_confluence_time(best_pair[0], best_pair[1])
            print(f"  depth={d}: |layer|={len(nodes):4d}, min_dist={min_dist:8d}, "
                  f"pair=({best_pair[0]}, {best_pair[1]}), actual_L={actual_L}")


# ===== Phase 3: 最小距離の増加パターン分析 =====
print("\n" + "=" * 70)
print("Phase 3: 最小距離のスケーリング分析")
print("=" * 70)

# Phase 1の結果から、最小距離 vs L のスケーリングを分析
sorted_L = sorted(min_distance_by_L.keys())
if len(sorted_L) > 2:
    Ls = []
    dists = []
    for L in sorted_L:
        d = min_distance_by_L[L][0]
        Ls.append(L)
        dists.append(d)

    print(f"\nL vs min_distance:")
    for L, d in zip(Ls, dists):
        log_d = math.log2(d) if d > 0 else 0
        print(f"  L={L:3d}, min_dist={d:8d}, log2(dist)={log_d:.2f}, dist/2^L={d/2**L:.6f}")

    # 線形回帰 log(dist) vs L
    if len(Ls) > 3:
        n_pts = len(Ls)
        sum_x = sum(Ls)
        sum_y = sum(math.log2(d) if d > 0 else 0 for d in dists)
        sum_xy = sum(L * (math.log2(d) if d > 0 else 0) for L, d in zip(Ls, dists))
        sum_xx = sum(L**2 for L in Ls)

        slope = (n_pts * sum_xy - sum_x * sum_y) / (n_pts * sum_xx - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n_pts

        print(f"\nlog2(min_dist) ~ {slope:.4f} * L + {intercept:.4f}")
        print(f"=> min_dist ~ 2^({slope:.4f} * L)")
        print(f"=> 基底 = 2^{slope:.4f} = {2**slope:.4f}")


# ===== Phase 4: mod構造分析 =====
print("\n" + "=" * 70)
print("Phase 4: 最小距離ペアのmod構造")
print("=" * 70)

for L in sorted_L[:15]:
    dist, n1, n2, mp = min_distance_by_L[L]
    print(f"  L={L:2d}: ({n1:6d}, {n2:6d}), "
          f"n1 mod 4={n1%4}, n2 mod 4={n2%4}, "
          f"n1 mod 8={n1%8}, n2 mod 8={n2%8}, "
          f"dist={dist}, dist mod 4={dist%4}, dist mod 8={dist%8}")


# ===== Phase 5: 特定合流点からの逆像分岐パターン =====
print("\n" + "=" * 70)
print("Phase 5: 合流点からの逆像分岐 -- 2段分岐の構造")
print("=" * 70)

def detailed_preimages(m, max_a=20):
    """詳細な逆像情報"""
    results = []
    for a in range(1, max_a + 1):
        num = (2**a) * m - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1:
                results.append({'n': n, 'a': a, 'ratio': n/m if m > 0 else 0})
    return results

for m in [1, 5, 7, 11, 13]:
    pre = detailed_preimages(m, max_a=20)
    print(f"\nT^{{-1}}({m}):")
    for p in pre[:8]:
        n = p['n']
        # n の2段目逆像
        pre2 = detailed_preimages(n, max_a=15)
        n_pre2 = len(pre2)
        print(f"  n={n:8d} (a={p['a']:2d}, ratio={p['ratio']:.3f}): "
              f"|T^{{-1}}(n)|={n_pre2}")
        for p2 in pre2[:4]:
            print(f"    -> {p2['n']:10d} (a={p2['a']:2d})")


# ===== Phase 6: 距離2のペアの合流パターン =====
print("\n" + "=" * 70)
print("Phase 6: 距離2の隣接奇数ペアの合流時間分布")
print("=" * 70)

dist2_L_dist = Counter()
dist2_examples = {}

for n in range(1, 10001, 2):
    n2 = n + 2
    L = find_confluence_time(n, n2)
    if L is not None:
        dist2_L_dist[L] += 1
        if L not in dist2_examples:
            o1 = orbit(n, 300)
            mp = o1[L] if L < len(o1) else None
            dist2_examples[L] = (n, n2, mp)

print(f"\n合流時間L | 頻度 | 例")
print("-" * 60)
for L in sorted(dist2_L_dist.keys()):
    ex = dist2_examples.get(L, ('?', '?', '?'))
    print(f"  L={L:3d} | {dist2_L_dist[L]:5d} | ({ex[0]}, {ex[1]}) -> meet={ex[2]}")

# 統計
if dist2_L_dist:
    total = sum(dist2_L_dist.values())
    mean_L = sum(L * c for L, c in dist2_L_dist.items()) / total
    print(f"\n平均合流時間: {mean_L:.3f}")
    print(f"最頻合流時間: {dist2_L_dist.most_common(1)[0]}")


# ===== Phase 7: 合流時間が大きいペアの構造 =====
print("\n" + "=" * 70)
print("Phase 7: 大合流時間ペアの特殊構造")
print("=" * 70)

# 合流時間が大きい隣接奇数ペアの特徴
large_L_pairs = [(L, n, n+2) for n in range(1, 10001, 2)
                 for L_val in [find_confluence_time(n, n+2)]
                 if L_val is not None and L_val > 15]

# 上の内包が遅いので別のアプローチ
large_L_pairs = []
for n in range(1, 5001, 2):
    L = find_confluence_time(n, n+2)
    if L is not None and L > 12:
        large_L_pairs.append((L, n, n+2))

large_L_pairs.sort(reverse=True)
print(f"\n大合流時間ペア（top 20）:")
for L, n1, n2 in large_L_pairs[:20]:
    v2_n1 = 0
    tmp = n1 + 1
    while tmp % 2 == 0:
        v2_n1 += 1
        tmp //= 2
    print(f"  L={L:3d}: ({n1:6d}, {n2:6d}), "
          f"n1 mod 16={n1%16:2d}, v2(n1+1)={v2_n1}")


# ===== 最終集計 =====
print("\n" + "=" * 70)
print("最終集計")
print("=" * 70)

findings = []
hypotheses = []

# Finding 1: 最小距離のスケーリング
if len(sorted_L) > 5:
    findings.append(f"合流時間L={sorted_L[0]}~{sorted_L[-1]}の範囲で最小距離ペアを計算")

# Finding 2: 距離2ペアの合流時間
if dist2_L_dist:
    findings.append(f"隣接奇数ペア(距離2)の平均合流時間={mean_L:.3f}")
    mode_L = dist2_L_dist.most_common(1)[0]
    findings.append(f"最頻合流時間={mode_L[0]} (頻度={mode_L[1]})")

# Finding 3: 大合流時間
if large_L_pairs:
    max_L = large_L_pairs[0][0]
    findings.append(f"[1,5000]の隣接奇数ペアで最大合流時間={max_L}")

results = {
    "min_distance_by_L": {str(L): {"dist": d, "n1": n1, "n2": n2, "meeting": mp}
                          for L, (d, n1, n2, mp) in min_distance_by_L.items()},
    "dist2_L_distribution": {str(L): c for L, c in sorted(dist2_L_dist.items())},
    "large_L_pairs_top10": [(L, n1, n2) for L, n1, n2 in large_L_pairs[:10]],
    "findings": findings,
}

print(f"\n発見: {findings}")
print(f"\nDone. Total time: {time.time()-t0:.1f}s")
