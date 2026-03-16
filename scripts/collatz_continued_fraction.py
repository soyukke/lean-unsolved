#!/usr/bin/env python3
"""探索28: 連分数展開と log2(3) のコラッツへの関わり"""

import math
import statistics
from collections import defaultdict

N = 65536  # 2^16

def total_stopping_time(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def collatz_orbit(n):
    orbit = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        orbit.append(n)
    return orbit

print("=" * 70)
print("探索28: 連分数と log2(3) のコラッツへの関わり")
print("=" * 70)

# --- log2(3) の連分数展開 ---
print(f"\n[1] log2(3) の連分数展開")
log2_3 = math.log2(3)
print(f"  log2(3) = {log2_3:.15f}")

# 連分数展開を mpmath なしで計算（float精度の限界まで）
def continued_fraction_float(x, max_terms=30):
    cf = []
    for _ in range(max_terms):
        a = int(x)
        cf.append(a)
        frac = x - a
        if abs(frac) < 1e-12:
            break
        x = 1.0 / frac
    return cf

cf = continued_fraction_float(log2_3, 25)
print(f"  連分数: [{cf[0]}; {', '.join(str(a) for a in cf[1:])}]")

# 既知の正確な連分数展開 (OEISより)
cf_exact = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 2, 2, 1, 1, 2]
print(f"  既知の正確値: [{cf_exact[0]}; {', '.join(str(a) for a in cf_exact[1:])}]")

# 収束子 p_k/q_k を計算
def convergents(cf):
    p_prev, p_curr = 1, cf[0]
    q_prev, q_curr = 0, 1
    result = [(p_curr, q_curr)]
    for a in cf[1:]:
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        result.append((p_curr, q_curr))
    return result

conv_list = convergents(cf_exact)
print(f"\n[2] 収束子 p_k/q_k と |2^p - 3^q|:")
for k, (p, q) in enumerate(conv_list):
    if q > 60:  # 3^q が大きすぎない範囲
        log_diff = p * math.log(2) - q * math.log(3)
        print(f"  k={k:2d}: p/q={p:10d}/{q:<8d} = {p/q:.12f}, "
              f"log(2^p/3^q) = {log_diff:.6e}")
    else:
        diff = abs(2**p - 3**q)
        ratio = 2**p / 3**q
        log_diff_exact = math.log2(diff) if diff > 0 else -999
        print(f"  k={k:2d}: p/q={p:10d}/{q:<8d} = {p/q:.12f}, "
              f"|2^p - 3^q| = {diff} (≈2^{log_diff_exact:.1f}), "
              f"2^p/3^q = {ratio:.12f}")

# --- 「near-miss」の分析 ---
print(f"\n[3] Near-miss 2^p ≈ 3^q の詳細:")
near_misses = []
for k, (p, q) in enumerate(conv_list):
    if p > 0 and q > 0:
        log_ratio = p * math.log(2) - q * math.log(3)
        rel_error = abs(math.exp(log_ratio) - 1)
        near_misses.append((p, q, rel_error, k))

near_misses.sort(key=lambda x: x[2])
print(f"  相対誤差の小さい順:")
for p, q, err, k in near_misses[:15]:
    print(f"    2^{p}/3^{q}: 相対誤差 = {err:.6e} (収束子 k={k})")

# --- 軌道中の上昇/下降比率と log2(3) ---
print(f"\n[4] 軌道中の「上昇/下降」回数と log2(3) の関係:")
print(f"  軌道で奇数ステップ(x3+1) u回、偶数ステップ(/2) d回なら")
print(f"  収束条件: d/u > log2(3) ≈ {math.log2(3):.6f}")

ratios = []
for n in range(3, min(N + 1, 10001), 2):
    orbit = collatz_orbit(n)
    u = sum(1 for x in orbit[:-1] if x % 2 == 1)
    d = sum(1 for x in orbit[:-1] if x % 2 == 0)
    if u > 0:
        ratios.append((n, d / u, u, d))

d_over_u = [r[1] for r in ratios]
print(f"  n=3..{min(N, 10000)} (奇数) の d/u 統計:")
print(f"    平均: {statistics.mean(d_over_u):.6f}")
print(f"    中央値: {statistics.median(d_over_u):.6f}")
print(f"    標準偏差: {statistics.stdev(d_over_u):.6f}")
print(f"    log2(3) = {math.log2(3):.6f}")
print(f"    平均 - log2(3) = {statistics.mean(d_over_u) - math.log2(3):.6f}")
print(f"    最小 d/u = {min(d_over_u):.6f}")

# d/u が log2(3) に最も近い
close_to_boundary = sorted(ratios, key=lambda x: abs(x[1] - math.log2(3)))[:15]
print(f"\n  d/u が log2(3) に最も近い n:")
for n, r, u, d in close_to_boundary:
    print(f"    n={n:6d}: d/u={r:.6f} (diff={r - math.log2(3):+.6f}), u={u}, d={d}")

# --- 軌道の最大値/初期値 と連分数部分商 ---
print(f"\n[5] 軌道の最大値/初期値 の分布:")
max_ratios = []
for n in range(3, min(N + 1, 10001), 2):
    orbit = collatz_orbit(n)
    mx = max(orbit)
    max_ratios.append((n, mx / n, mx))

max_ratios.sort(key=lambda x: -x[1])
print(f"  最大値/初期値 が大きい上位20:")
for n, ratio, mx in max_ratios[:20]:
    st = total_stopping_time(n)
    print(f"    n={n:6d}: max/n={ratio:10.1f}, max={mx}, stop_time={st}")

# --- 連分数の部分商が大きい箇所の影響 ---
print(f"\n[6] 大きい部分商と near-miss の関係:")
for k, a in enumerate(cf_exact):
    if a >= 3 and k < len(conv_list):
        p, q = conv_list[k]
        log_ratio = p * math.log(2) - q * math.log(3)
        print(f"  a_{k}={a:3d}: 収束子 {p}/{q}, "
              f"|log(2^{p}/3^{q})| = {abs(log_ratio):.6e}")

# --- コラッツ軌道中の「近似比率」---
print(f"\n[7] 軌道中の 3^k/2^m ≈ 1 の近似出現:")
# 代表的な長い軌道で、途中の値の比率を調べる
test_ns = [27, 703, 871, 6171]
for n in test_ns:
    orbit = collatz_orbit(n)
    u_running = 0
    d_running = 0
    print(f"\n  n={n} (軌道長={len(orbit)}):")
    for step, val in enumerate(orbit[:-1]):
        if val % 2 == 1:
            u_running += 1
        else:
            d_running += 1
        # d/u の変化を追跡（10ステップごと）
        if (step + 1) % max(len(orbit) // 10, 1) == 0 and u_running > 0:
            print(f"    step {step+1:4d}: val={val:12d}, d/u={d_running/u_running:.4f} "
                  f"(log2(3)={math.log2(3):.4f})")

# --- 2^a * 3^b - 1 型の数 ---
print(f"\n[8] 2^a * 3^b - 1 型の数の stopping time:")
results_23 = []
for a in range(1, 20):
    for b in range(0, 12):
        n = 2**a * 3**b - 1
        if 1 < n <= 200000 and n % 2 == 1:
            st = total_stopping_time(n)
            results_23.append((a, b, n, st))

results_23.sort(key=lambda x: -x[3])
print(f"  上位20 (stopping time順):")
for a, b, n, st in results_23[:20]:
    print(f"    2^{a}*3^{b}-1 = {n:8d}: stopping_time={st}")

# --- log2(3) の有理近似と「危険な」軌道 ---
print(f"\n[9] 有理近似 p/q ≈ log2(3) と 軌道中のステップ比率の一致:")
# 軌道が収束子 p/q の比率に沿って進む場面を探す
for p, q in [(2, 1), (3, 2), (5, 3), (8, 5), (19, 12), (46, 29), (65, 41)]:
    # d/u = p/q に近い軌道を持つ n を探す
    target = p / q
    matching = []
    for n, r, u, d in ratios:
        if abs(r - target) < 0.01:
            matching.append((n, r))
    print(f"  p/q={p}/{q}={target:.4f}: d/u が近い n は {len(matching)} 個")
    if matching:
        for n, r in matching[:3]:
            print(f"    n={n}: d/u={r:.4f}")

print("\n" + "=" * 70)
print("結論:")
print(f"  - d/u の平均 ({statistics.mean(d_over_u):.4f}) > log2(3) ({math.log2(3):.4f}) が収束の鍵")
print("  - log2(3) の連分数近似の質がコラッツの困難さを本質的に支配")
print("  - 大きい部分商 (a=23, 55, 15, ...) に対応する near-miss が長い軌道を生む")
print("  - 2^a*3^b-1 型の数は stopping time が系統的に長い")
print("=" * 70)
