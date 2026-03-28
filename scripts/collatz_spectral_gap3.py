#!/usr/bin/env python3
"""
追加解析3:
1. 巡回長 >= L の巡回のみでの min mean_v₂ の解析
2. 固定点（巡回長1）の正体の解明
3. 短巡回の比率と長巡回の平均 v₂ の収束
4. E[v₂] の奇偶パターンの解明
"""

import time
import math
from fractions import Fraction

def v2(n):
    if n == 0:
        return 999
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def build_permutation(k):
    mod = 2**k
    odds = list(range(1, mod, 2))
    N = len(odds)
    odd_to_idx = {o: i for i, o in enumerate(odds)}
    perm = [0] * N
    v2_vals = [0] * N
    for i, n_res in enumerate(odds):
        val = 3 * n_res + 1
        vv = v2(val)
        target = (val >> vv) % mod
        v2_vals[i] = vv
        if target in odd_to_idx:
            perm[i] = odd_to_idx[target]
    return perm, odds, v2_vals

def cycle_decomposition(perm, v2_vals):
    N = len(perm)
    visited = [False] * N
    cycles = []
    for i in range(N):
        if not visited[i]:
            cycle = []
            j = i
            while not visited[j]:
                visited[j] = True
                cycle.append(j)
                j = perm[j]
            mean_v2 = sum(v2_vals[ii] for ii in cycle) / len(cycle)
            cycles.append((cycle, mean_v2))
    return cycles

# Part A: 固定点の正体
print("=" * 80)
print("Part A: 固定点（巡回長=1）の正体")
print("=" * 80)

for k in range(3, 16):
    perm, odds, v2_vals = build_permutation(k)
    cycles = cycle_decomposition(perm, v2_vals)
    fixed_points = [(odds[c[0]], v2_vals[c[0]]) for c, m in cycles if len(c) == 1]
    if k <= 10:
        print(f"k={k:2d}: 固定点 = {fixed_points}")
    else:
        print(f"k={k:2d}: 固定点数 = {len(fixed_points)}, v₂値 = {set(fp[1] for fp in fixed_points)}")

# T(n) ≡ n mod 2^k の解析
print("\n固定点の条件: T(n) ≡ n mod 2^k")
print("つまり (3n+1)/2^{v₂(3n+1)} ≡ n mod 2^k")
for k in [5, 7, 9]:
    mod = 2**k
    print(f"\nk={k}:")
    for n in range(1, mod, 2):
        t = syracuse(n)
        if t % mod == n:
            vv = v2(3*n+1)
            print(f"  n={n}: T(n)={t}, v₂={vv}, (3n+1)={3*n+1}, T(n)mod{mod}={t%mod}")

# Part B: 巡回長別の mean_v₂
print("\n" + "=" * 80)
print("Part B: 巡回長別の mean_v₂ 分布")
print("=" * 80)

log2_3 = math.log2(3)

for k in [7, 9, 11, 13, 15, 17, 19]:
    perm, odds, v2_vals = build_permutation(k)
    cycles = cycle_decomposition(perm, v2_vals)

    # 巡回長でグループ化
    by_len = {}
    for cycle, mean in cycles:
        L = len(cycle)
        if L not in by_len:
            by_len[L] = []
        by_len[L].append(mean)

    print(f"\nk={k} (N={2**(k-1)}, 巡回数={len(cycles)}):")
    print(f"  {'巡回長':>8s}  {'個数':>5s}  {'mean_v₂ min':>12s}  {'mean_v₂ avg':>12s}  {'> log₂3':>8s}")

    total_below = 0
    total_count = 0
    for L in sorted(by_len.keys()):
        means = by_len[L]
        min_m = min(means)
        avg_m = sum(means) / len(means)
        above = sum(1 for m in means if m > log2_3)
        total_below += len(means) - above
        total_count += len(means)
        if L <= 20 or min_m <= log2_3:
            print(f"  {L:8d}  {len(means):5d}  {min_m:12.6f}  {avg_m:12.6f}  {above}/{len(means)}")

    below = total_count - sum(1 for c, m in cycles if m > log2_3)
    print(f"  合計: {below}/{total_count} 巡回が mean_v₂ <= log₂(3)")

# Part C: 長巡回のみでの min mean_v₂
print("\n" + "=" * 80)
print("Part C: 巡回長 >= L の巡回での min mean_v₂")
print("=" * 80)

for k in [9, 11, 13, 15, 17]:
    perm, odds, v2_vals = build_permutation(k)
    cycles = cycle_decomposition(perm, v2_vals)

    print(f"\nk={k}:")
    for min_len in [1, 2, 3, 5, 10, 20, 30]:
        filtered = [(c, m) for c, m in cycles if len(c) >= min_len]
        if not filtered:
            break
        min_m = min(m for c, m in filtered)
        avg_m = sum(m * len(c) for c, m in filtered) / sum(len(c) for c, m in filtered)
        num = len(filtered)
        num_below = sum(1 for c, m in filtered if m <= log2_3)
        print(f"  L>={min_len:3d}: {num:5d}巡回, min={min_m:.6f}, "
              f"weighted_avg={avg_m:.6f}, below_log₂3: {num_below}")

# Part D: E[v₂] のパリティ依存パターンの証明
print("\n" + "=" * 80)
print("Part D: E[v₂] の k パリティ依存パターン")
print("  k奇数 → E[v₂] = 2 厳密")
print("  k偶数 → E[v₂] = (2^k - 1)/2^{k-1} = 2 - 1/2^{k-1}")
print("=" * 80)

print(f"{'k':>3s}  {'E[v₂] exact':>20s}  {'2-1/2^(k-1)':>20s}  {'match(even)':>12s}")
for k in range(3, 22):
    mod = 2**k
    total = 0
    count = 0
    for n in range(1, mod, 2):
        total += v2(3*n + 1)
        count += 1
    mean = Fraction(total, count)

    if k % 2 == 1:
        expected = Fraction(2)
        match = "yes" if mean == expected else "no"
        print(f"{k:3d}  {str(mean):>20s}  {'2':>20s}  {match:>12s}  (k odd)")
    else:
        expected = Fraction(2**k - 1, 2**(k-1))
        match = "yes" if mean == expected else "no"
        print(f"{k:3d}  {str(mean):>20s}  {str(expected):>20s}  {match:>12s}  (k even)")

# Part E: v₂ 分布の精密構造
print("\n" + "=" * 80)
print("Part E: v₂ 分布の精密構造")
print("  P(v₂=j) for j=1,...,k の正確な値")
print("=" * 80)

for k in [5, 8, 11, 14]:
    mod = 2**k
    N = 2**(k-1)
    dist = {}
    for n in range(1, mod, 2):
        vv = v2(3*n+1)
        dist[vv] = dist.get(vv, 0) + 1

    print(f"\nk={k}:")
    print(f"  {'j':>3s}  {'count':>8s}  {'P(v₂=j)':>20s}  {'1/2^j':>20s}  {'差':>20s}")
    for j in sorted(dist.keys()):
        p = Fraction(dist[j], N)
        geo = Fraction(1, 2**j)
        diff = p - geo
        print(f"  {j:3d}  {dist[j]:8d}  {str(p):>20s}  {str(geo):>20s}  {str(diff):>20s}")

# Part F: 確率的遷移行列のスペクトルギャップ（大サンプル）
print("\n" + "=" * 80)
print("Part F: 確率的遷移行列 — 大サンプルでの安定性検証")
print("=" * 80)

for k in [5, 7, 9]:
    mod = 2**k
    odds = list(range(1, mod, 2))
    N = len(odds)
    odd_to_idx = {o: i for i, o in enumerate(odds)}

    for num_samples in [64, 256, 1024, 4096]:
        # 遷移行列構成
        P = [[0.0]*N for _ in range(N)]
        for i, n_res in enumerate(odds):
            targets = {}
            for s in range(num_samples):
                n = n_res + s * mod
                if n == 0:
                    continue
                t = syracuse(n)
                t_mod = t % mod
                if t_mod in odd_to_idx:
                    j = odd_to_idx[t_mod]
                    targets[j] = targets.get(j, 0) + 1
            total = sum(targets.values())
            if total > 0:
                for j, count in targets.items():
                    P[i][j] = count / total

        # 冪乗法でλ₂推定
        import random
        random.seed(42)
        v = [random.gauss(0,1) for _ in range(N)]
        mean_v = sum(v)/N
        v = [x - mean_v for x in v]
        norm = math.sqrt(sum(x*x for x in v))
        if norm > 0:
            v = [x/norm for x in v]

        lambda2 = 0.0
        for _ in range(300):
            w = [0.0]*N
            for i in range(N):
                for j in range(N):
                    w[i] += P[i][j] * v[j]
            mean_w = sum(w)/N
            w = [x - mean_w for x in w]
            norm = math.sqrt(sum(x*x for x in w))
            if norm < 1e-15:
                lambda2 = 0.0
                break
            lambda2 = norm
            v_new = [x/norm for x in w]
            diff = math.sqrt(sum((v_new[i]-v[i])**2 for i in range(N)))
            v = v_new
            if diff < 1e-12:
                break

        gap = 1.0 - lambda2
        print(f"k={k:2d}, samples={num_samples:5d}: |λ₂|={lambda2:.6f}, gap={gap:.6f}")

# Part G: 巡回の v₂ 系列と log₂(3) との比較
print("\n" + "=" * 80)
print("Part G: 「問題のある」巡回の詳細分析")
print("  mean_v₂ <= log₂(3) の巡回がどのような n を含むか")
print("=" * 80)

for k in [9, 11]:
    perm, odds, v2_vals = build_permutation(k)
    cycles = cycle_decomposition(perm, v2_vals)
    mod = 2**k

    bad_cycles = [(c, m) for c, m in cycles if m <= log2_3]
    print(f"\nk={k}: {len(bad_cycles)} 個の「問題巡回」")
    for idx, (cycle, mean) in enumerate(bad_cycles[:5]):
        ns = [odds[i] for i in cycle]
        vs = [v2_vals[i] for i in cycle]
        print(f"  巡回{idx+1} (長さ{len(cycle)}, mean_v₂={mean:.4f}):")
        print(f"    n mod {mod}: {ns[:10]}{'...' if len(ns)>10 else ''}")
        print(f"    v₂ 系列: {vs[:10]}{'...' if len(vs)>10 else ''}")
        # この巡回に沿った値の変化: n → 3n+1 → /2^v₂ → ...
        # log₂(n) の変化: +log₂(3) - v₂ per step
        # mean change = log₂(3) - mean_v₂
        change = math.log2(3) - mean
        print(f"    1ステップあたりの log₂(n) 変化 ≈ {change:+.4f} (>0 means growth)")

# Part H: 巡回平均 v₂ の分布の要約
print("\n" + "=" * 80)
print("Part H: 巡回平均 v₂ の分布要約（全 k）")
print("=" * 80)

print(f"{'k':>3s}  {'巡回数':>8s}  {'min':>8s}  {'q25':>8s}  {'median':>8s}  {'q75':>8s}  "
      f"{'max':>8s}  {'below%':>8s}  {'below(L>=5)%':>12s}")

for k in range(5, 20):
    perm, odds, v2_vals = build_permutation(k)
    cycles = cycle_decomposition(perm, v2_vals)
    means = sorted([m for c, m in cycles])
    N_cyc = len(means)

    q25 = means[N_cyc//4]
    median = means[N_cyc//2]
    q75 = means[3*N_cyc//4]

    below = sum(1 for m in means if m <= log2_3)
    below_pct = 100.0 * below / N_cyc

    # L >= 5 のみ
    long_means = [m for c, m in cycles if len(c) >= 5]
    if long_means:
        below_long = sum(1 for m in long_means if m <= log2_3)
        below_long_pct = 100.0 * below_long / len(long_means)
    else:
        below_long_pct = 0.0

    print(f"{k:3d}  {N_cyc:8d}  {means[0]:8.4f}  {q25:8.4f}  {median:8.4f}  {q75:8.4f}  "
          f"{means[-1]:8.4f}  {below_pct:7.1f}%  {below_long_pct:11.1f}%")

# Part I: 長巡回での min mean_v₂ の k 依存性
print("\n" + "=" * 80)
print("Part I: 巡回長 >= L の巡回での min mean_v₂ の k 推移")
print("=" * 80)

for min_L in [5, 10, 20]:
    print(f"\n巡回長 >= {min_L}:")
    print(f"  {'k':>3s}  {'#巡回':>7s}  {'min mean_v₂':>12s}  {'> log₂(3)?':>10s}  {'差':>10s}")
    for k in range(5, 20):
        perm, odds, v2_vals = build_permutation(k)
        cycles = cycle_decomposition(perm, v2_vals)
        filtered = [(c, m) for c, m in cycles if len(c) >= min_L]
        if filtered:
            min_m = min(m for c, m in filtered)
            ok = "YES" if min_m > log2_3 else "NO"
            diff = min_m - log2_3
            print(f"  {k:3d}  {len(filtered):7d}  {min_m:12.6f}  {ok:>10s}  {diff:+10.6f}")
        else:
            print(f"  {k:3d}  {'0':>7s}  {'N/A':>12s}")
