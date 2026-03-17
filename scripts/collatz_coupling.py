#!/usr/bin/env python3
"""
探索34: 確率的カップリング — 2つのCollatz軌道の合流解析

全く新しいアイデア: 異なる初期値からの軌道が「合流」する現象を系統的に調べる。
コラッツ予想 ⟺ 任意の2軌道が有限時間で合流する。
"""

import math
from collections import Counter, defaultdict

# === Syracuse map ===
def syracuse(n):
    """奇数 n に対する Syracuse map: (3n+1) / 2^v2(3n+1)"""
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def syracuse_orbit(n, max_steps=1000):
    """奇数 n からの Syracuse 軌道（奇数列）"""
    orbit = [n]
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x = syracuse(x)
        orbit.append(x)
    return orbit

# ============================================================
# 1. カップリング時間の測定
# ============================================================
print("=" * 70)
print("探索34: 確率的カップリング — Collatz軌道の合流解析")
print("=" * 70)

print("\n### 1. カップリング時間の測定 ###\n")

def coupling_time(n, m, max_steps=2000):
    """
    奇数 n, m からの Syracuse 軌道が初めて合流するステップ数。
    合流 = 同じ奇数値に同時に到達（ステップは各自独立にカウント）。

    方法: 両方の軌道を生成し、集合の交差を見る。
    返り値: (coupling_step_n, coupling_step_m, meeting_point) or None
    """
    orb_n = syracuse_orbit(n, max_steps)
    orb_m = syracuse_orbit(m, max_steps)

    # 各値が最初に現れるステップを記録
    first_step_n = {}
    for i, v in enumerate(orb_n):
        if v not in first_step_n:
            first_step_n[v] = i

    first_step_m = {}
    for i, v in enumerate(orb_m):
        if v not in first_step_m:
            first_step_m[v] = i

    # 共通値を探す
    common = set(first_step_n.keys()) & set(first_step_m.keys())
    if not common:
        return None

    # 合計ステップ (step_n + step_m) が最小のものを選ぶ
    best = None
    for v in common:
        total = first_step_n[v] + first_step_m[v]
        if best is None or total < best[0]:
            best = (total, first_step_n[v], first_step_m[v], v)

    return (best[1], best[2], best[3])


# 小規模ペアで測定
print("(a) 奇数ペア (n,m) のカップリング時間 (n,m ∈ {3,5,...,199})")
odd_range = list(range(3, 200, 2))
coupling_times = {}
meeting_points = Counter()
no_coupling = 0

for i, n in enumerate(odd_range):
    for m in odd_range[i+1:]:
        result = coupling_time(n, m)
        if result is None:
            no_coupling += 1
        else:
            sn, sm, mp = result
            coupling_times[(n, m)] = sn + sm
            meeting_points[mp] += 1

total_pairs = len(odd_range) * (len(odd_range) - 1) // 2
times_list = list(coupling_times.values())

print(f"  総ペア数: {total_pairs}")
print(f"  合流成功: {len(times_list)}")
print(f"  合流失敗: {no_coupling}")
if times_list:
    print(f"  平均カップリング時間: {sum(times_list)/len(times_list):.2f}")
    print(f"  最大カップリング時間: {max(times_list)}")
    print(f"  中央値: {sorted(times_list)[len(times_list)//2]}")

# カップリング時間の分布
print("\n  カップリング時間の分布:")
time_dist = Counter()
for t in times_list:
    bucket = t // 5 * 5
    time_dist[bucket] += 1
for bucket in sorted(time_dist.keys())[:15]:
    bar = '#' * min(time_dist[bucket] // 10, 60)
    print(f"    [{bucket:3d}-{bucket+4:3d}]: {time_dist[bucket]:5d} {bar}")

# ============================================================
# 2. 合流パターン
# ============================================================
print("\n### 2. 合流パターン ###\n")

print("(a) 最頻合流点 TOP 20:")
for mp, cnt in meeting_points.most_common(20):
    print(f"    値={mp:10d}: {cnt:5d} 回")

print("\n(b) 合流点の値の分布（対数スケール）:")
mp_log_dist = Counter()
for mp, cnt in meeting_points.items():
    bucket = int(math.log2(mp + 1))
    mp_log_dist[bucket] += cnt
for b in sorted(mp_log_dist.keys()):
    bar = '#' * min(mp_log_dist[b] // 20, 50)
    print(f"    log2 ∈ [{b:2d},{b+1:2d}): {mp_log_dist[b]:6d} {bar}")

# |n-m| とカップリング時間の関係
print("\n(c) |n-m| とカップリング時間の関係:")
diff_times = defaultdict(list)
for (n, m), t in coupling_times.items():
    diff = abs(n - m)
    diff_bucket = diff // 20 * 20
    diff_times[diff_bucket].append(t)

for d in sorted(diff_times.keys())[:10]:
    vals = diff_times[d]
    avg = sum(vals) / len(vals)
    print(f"    |n-m| ∈ [{d:3d},{d+19:3d}]: 平均={avg:.1f}, 最大={max(vals)}, 件数={len(vals)}")

# ============================================================
# 3. log₂距離の時間発展
# ============================================================
print("\n### 3. log₂距離の時間発展 ###\n")

print("具体例: 各ペアについて log₂|T^k(n) - T^k(m)| の推移")
example_pairs = [(3, 5), (7, 11), (27, 31), (97, 101), (127, 255)]

for n, m in example_pairs:
    orb_n = syracuse_orbit(n, 200)
    orb_m = syracuse_orbit(m, 200)
    min_len = min(len(orb_n), len(orb_m))

    print(f"\n  ペア ({n}, {m}):")
    print(f"    軌道長: {len(orb_n)}, {len(orb_m)}")

    distances = []
    for k in range(min_len):
        if orb_n[k] != orb_m[k]:
            d = abs(math.log2(orb_n[k]) - math.log2(orb_m[k]))
            distances.append((k, d))
        else:
            distances.append((k, 0.0))
            print(f"    → ステップ {k} で合流! 値={orb_n[k]}")
            break

    # 距離の推移をサンプル表示
    show_steps = [0, 1, 2, 3, 5, 10, 15, 20, 30, 50]
    for s in show_steps:
        if s < len(distances):
            k, d = distances[s]
            print(f"    step {k:3d}: log₂距離 = {d:.4f}")

# ============================================================
# 4. 隣接奇数のカップリング n と n+2
# ============================================================
print("\n### 4. 隣接奇数 n と n+2 のカップリング ###\n")

adj_coupling = []
for n in range(3, 10001, 2):
    result = coupling_time(n, n + 2, max_steps=500)
    if result:
        sn, sm, mp = result
        adj_coupling.append((n, sn + sm, mp))

print(f"  調査範囲: n = 3..9999 (奇数), ペア数={len(range(3,10001,2))}")
print(f"  合流成功: {len(adj_coupling)}")
if adj_coupling:
    times = [t for _, t, _ in adj_coupling]
    print(f"  平均カップリング時間: {sum(times)/len(times):.2f}")
    print(f"  最大カップリング時間: {max(times)}")

    # 最大カップリング時間のケース
    adj_coupling.sort(key=lambda x: x[1], reverse=True)
    print("\n  最もカップリングが遅いペア TOP 10:")
    for n, t, mp in adj_coupling[:10]:
        print(f"    n={n:6d}, n+2={n+2:6d}: 時間={t:4d}, 合流点={mp}")

# ============================================================
# 5. 吸引盆の構造
# ============================================================
print("\n### 5. 吸引盆（逆像集合）の構造 ###\n")

print("各奇数 m に対して、Syracuse 1ステップで m に到達する奇数の集合を構築")
print("(逆写像: m の前像)")

def syracuse_preimages(m, bound=100000):
    """
    Syracuse(n) = m となる奇数 n を列挙 (n <= bound)
    3n+1 = m * 2^k  →  n = (m * 2^k - 1) / 3
    n が正の奇数であること
    """
    preimages = []
    k = 1
    while True:
        val = m * (2 ** k) - 1
        if val > 3 * bound:
            break
        if val % 3 == 0:
            n = val // 3
            if n > 0 and n % 2 == 1 and n <= bound:
                # 検証: v2(3n+1) = k を確認
                check = 3 * n + 1
                v2 = 0
                while check % 2 == 0:
                    check //= 2
                    v2 += 1
                if v2 == k and check == m:
                    preimages.append(n)
        k += 1
    return preimages

# 小さい奇数の前像
print("\n(a) 各奇数 m の直接前像数 (bound=100000):")
preimage_counts = {}
for m in range(1, 102, 2):
    pre = syracuse_preimages(m, bound=100000)
    preimage_counts[m] = len(pre)
    if m <= 21 or len(pre) >= 10:
        print(f"    m={m:5d}: 前像数={len(pre):4d}  前像={pre[:10]}{'...' if len(pre)>10 else ''}")

# k-step 吸引盆のサイズ
print("\n(b) 1の k-step 吸引盆サイズ (k=1..8):")
basin = {1}
for k in range(1, 9):
    new_basin = set()
    for m in basin:
        if m % 2 == 1:
            pres = syracuse_preimages(m, bound=500000)
            new_basin.update(pres)
    basin.update(new_basin)
    odd_count = sum(1 for x in basin if x % 2 == 1)
    print(f"    k={k}: 盆サイズ(奇数のみ)={odd_count}, 新規追加={len(new_basin)}")

# ============================================================
# 6. 大規模統計: n=3..50001 のカップリング
# ============================================================
print("\n### 6. 大規模統計: 軌道の合流ネットワーク ###\n")

print("各奇数 n ∈ [3..50001] の軌道が 1 に合流するまでの時間")
stopping_times = {}
for n in range(3, 50002, 2):
    orb = syracuse_orbit(n, 2000)
    if orb[-1] == 1:
        stopping_times[n] = len(orb) - 1
    else:
        stopping_times[n] = -1

failed = sum(1 for v in stopping_times.values() if v < 0)
succeeded = sum(1 for v in stopping_times.values() if v >= 0)
print(f"  合流成功 (→1): {succeeded}")
print(f"  合流失敗: {failed}")

if succeeded > 0:
    valid_times = [v for v in stopping_times.values() if v >= 0]
    print(f"  平均停止時間: {sum(valid_times)/len(valid_times):.2f}")
    print(f"  最大停止時間: {max(valid_times)}")

# 軌道の「合流木」: 異なる n がどの値で初めて既知軌道と合流するか
print("\n  軌道合流木の分析:")
first_merge = Counter()  # 各値が「初めての合流点」になった回数

seen_global = set()
for n in range(3, 20002, 2):
    orb = syracuse_orbit(n, 500)
    for i, v in enumerate(orb):
        if v in seen_global:
            first_merge[v] += 1
            break
    seen_global.update(orb)

print("  最頻合流ノード TOP 20:")
for v, cnt in first_merge.most_common(20):
    print(f"    値={v:10d} (log₂={math.log2(v+1):.1f}): {cnt:5d} 回")

# ============================================================
# 7. カップリング的言い換えの検証
# ============================================================
print("\n### 7. カップリング的言い換えの検証 ###\n")

print("命題: 任意の2つの正奇数 n,m に対して、")
print("      Syracuse軌道が有限時間で合流する ⟺ コラッツ予想")
print()
print("検証: ランダムに選んだ1000ペアについてカップリング時間を測定")

import random
random.seed(42)

large_coupling = []
for _ in range(1000):
    n = random.randrange(3, 50001, 2)
    m = random.randrange(3, 50001, 2)
    if n == m:
        continue
    result = coupling_time(n, m, max_steps=500)
    if result:
        sn, sm, mp = result
        large_coupling.append((n, m, sn + sm, mp))

print(f"  テストペア数: {len(large_coupling)}")
if large_coupling:
    times = [t for _, _, t, _ in large_coupling]
    print(f"  全ペア合流: {'Yes' if len(large_coupling) >= 999 else 'No'}")
    print(f"  平均カップリング時間: {sum(times)/len(times):.2f}")
    print(f"  最大カップリング時間: {max(times)}")
    print(f"  標準偏差: {(sum((t-sum(times)/len(times))**2 for t in times)/len(times))**.5:.2f}")

    # カップリング時間 vs max(n,m)
    print("\n  max(n,m) の範囲別カップリング時間:")
    size_buckets = defaultdict(list)
    for n, m, t, mp in large_coupling:
        bucket = max(n, m) // 10000 * 10000
        size_buckets[bucket].append(t)
    for b in sorted(size_buckets.keys()):
        vals = size_buckets[b]
        print(f"    max ∈ [{b},{b+9999}]: 平均={sum(vals)/len(vals):.1f}, 件数={len(vals)}")

print("\n" + "=" * 70)
print("探索34 完了")
print("=" * 70)
