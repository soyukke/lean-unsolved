#!/usr/bin/env python3
"""
コラッツ予想 探索42: 大規模 d/u 最小値の精密計算

n = 1..10^7 の奇数で d/u の最小値を追跡し、
メルセンヌ数、2進表現の特徴、途中の累積 d/u を分析する。
"""

import math
import heapq
import time
from collections import defaultdict

LOG2_3 = math.log2(3)  # ≈ 1.58496...

# ===========================================================
# ユーティリティ
# ===========================================================

def collatz_du(n):
    """n の軌道で d(偶数ステップ=÷2回数), u(奇数ステップ=3n+1回数) を返す"""
    d, u = 0, 0
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
            d += 1
        else:
            x = 3 * x + 1
            u += 1
    return d, u


def collatz_du_with_interim_min(n):
    """
    n の軌道で:
    - 最終 d, u
    - 途中の累積 d/u の最小値 (min_interim_ratio)
    - 途中で累積 d/u < log2(3) になる瞬間があるか (has_below)
    を返す。サイクル単位で計算。
    """
    d, u = 0, 0
    x = n
    min_ratio = float('inf')
    has_below = False

    while x != 1:
        # 奇数フェーズ
        while x != 1 and x % 2 == 1:
            x = 3 * x + 1
            u += 1
            x //= 2
            d += 1
        # 追加偶数フェーズ
        while x != 1 and x % 2 == 0:
            x //= 2
            d += 1
        # サイクル完了時に ratio チェック
        if u > 0:
            ratio = d / u
            if ratio < min_ratio:
                min_ratio = ratio
            if ratio < LOG2_3:
                has_below = True

    return d, u, min_ratio, has_below


def bit_density(n):
    """n の2進表現における1の密度"""
    b = bin(n)[2:]
    return b.count('1') / len(b)


# ===========================================================
# 1. n=1..10^7 奇数で d/u の最小値を追跡
# ===========================================================
print("=" * 70)
print("探索42: 大規模 d/u 最小値の精密計算")
print("=" * 70)

N_MAX = 10_000_000
TOP_K = 100

print(f"\n1. n=3..{N_MAX} の奇数で d/u の最小値を追跡 (上位{TOP_K}個)")
print(f"   log₂(3) = {LOG2_3:.15f}")

# ヒープで上位TOP_K個を管理（最大ヒープ = 負のratioで最小ヒープ）
# heap stores: (-ratio, n, d, u)
top_heap = []  # max-heap of size TOP_K (smallest d/u values)
global_min_ratio = float('inf')
global_min_n = 3
count_below_log23 = 0
count_total = 0

# 10^k ごとの最小値記録
power_milestones = {}
next_power = 10
next_power_exp = 1

# 途中の累積d/u < log2(3) の統計
count_interim_below = 0

t_start = time.time()
t_last_report = t_start

for n in range(3, N_MAX + 1, 2):
    d, u, min_interim, has_below = collatz_du_with_interim_min(n)
    count_total += 1

    if has_below:
        count_interim_below += 1

    if u > 0:
        ratio = d / u

        if ratio < LOG2_3:
            count_below_log23 += 1

        # 最小値更新
        if ratio < global_min_ratio:
            global_min_ratio = ratio
            global_min_n = n

        # 上位TOP_K
        if len(top_heap) < TOP_K:
            heapq.heappush(top_heap, (-ratio, n, d, u))
        elif ratio < -top_heap[0][0]:
            heapq.heapreplace(top_heap, (-ratio, n, d, u))

    # 10^k milestone
    if n >= next_power - 1 and next_power_exp <= 7:
        power_milestones[next_power_exp] = (global_min_ratio, global_min_n)
        next_power *= 10
        next_power_exp += 1

    # 進捗表示
    now = time.time()
    if now - t_last_report > 15:
        elapsed = now - t_start
        pct = n / N_MAX * 100
        rate = count_total / elapsed
        eta = (N_MAX // 2 - count_total) / rate if rate > 0 else 0
        print(f"  ... n={n:>10,} ({pct:.1f}%) [{elapsed:.0f}s, {rate:.0f}/s, ETA {eta:.0f}s] min d/u={global_min_ratio:.10f} @ n={global_min_n}")
        t_last_report = now

# 最後のmilestone
if next_power_exp <= 7:
    power_milestones[next_power_exp] = (global_min_ratio, global_min_n)

t_end = time.time()
print(f"\n  完了: {count_total:,} 個の奇数を調査 ({t_end - t_start:.1f}秒)")

# ===========================================================
# 結果表示
# ===========================================================
print(f"\n--- d/u < log₂(3) の個数: {count_below_log23} ---")
if count_below_log23 > 0:
    print("  *** 最終的な d/u < log₂(3) となる n が存在！***")
else:
    print("  全ての n で d/u ≥ log₂(3) (最終値)")

print(f"\n--- 途中の累積 d/u < log₂(3) となる瞬間がある n の数: {count_interim_below} / {count_total} ({count_interim_below/count_total*100:.2f}%) ---")

# 上位TOP_K
results_sorted = sorted([(-r, n, d, u) for r, n, d, u in top_heap])
print(f"\n--- d/u が最小の上位{min(50, len(results_sorted))}個 ---")
print(f"{'Rank':>4} {'n':>12} {'d':>6} {'u':>6} {'d/u':>15} {'d/u - log₂3':>15} {'bit_density':>12}")
print("-" * 75)
for i, (ratio, n, d, u) in enumerate(results_sorted[:50]):
    diff = ratio - LOG2_3
    bd = bit_density(n)
    print(f"{i+1:>4} {n:>12} {d:>6} {u:>6} {ratio:>15.10f} {diff:>15.10f} {bd:>12.4f}")

# 10^k ごとの推移
print(f"\n--- 10^k ごとの最小 d/u の推移 ---")
print(f"{'Range':>15} {'min d/u':>15} {'n*':>12} {'d/u - log₂3':>15}")
print("-" * 60)
for exp in sorted(power_milestones.keys()):
    ratio, n = power_milestones[exp]
    diff = ratio - LOG2_3
    print(f"{'n ≤ 10^' + str(exp):>15} {ratio:>15.10f} {n:>12} {diff:>15.10f}")


# ===========================================================
# 2. メルセンヌ数 2^k - 1 の特別調査 (k=2..30)
# ===========================================================
print(f"\n{'=' * 70}")
print(f"2. メルセンヌ数 2^k - 1 の d/u (k=2..30)")
print(f"{'=' * 70}")

print(f"{'k':>4} {'n=2^k-1':>20} {'d':>8} {'u':>8} {'d/u':>15} {'d/u - log₂3':>15} {'interim_min':>15}")
print("-" * 90)

mersenne_results = []
for k in range(2, 31):
    n = (1 << k) - 1
    d, u, min_interim, has_below = collatz_du_with_interim_min(n)
    if u > 0:
        ratio = d / u
        diff = ratio - LOG2_3
        mersenne_results.append((k, n, d, u, ratio, min_interim, has_below))
        below_mark = " *** interim < log₂3" if has_below else ""
        print(f"{k:>4} {n:>20} {d:>8} {u:>8} {ratio:>15.10f} {diff:>15.10f} {min_interim:>15.10f}{below_mark}")


# ===========================================================
# 3. 最小 d/u を持つ n の2進表現の特徴分析
# ===========================================================
print(f"\n{'=' * 70}")
print(f"3. 最小 d/u を持つ n の2進表現の特徴")
print(f"{'=' * 70}")

# 上位100の分析
print(f"\n--- 上位20の2進表現 ---")
for i, (ratio, n, d, u) in enumerate(results_sorted[:20]):
    b = bin(n)[2:]
    ones = b.count('1')
    density = ones / len(b)
    # 連続1の最大長
    max_run = max(len(s) for s in b.split('0') if s)
    print(f"  #{i+1:>2} n={n:>12} = ...{b[-20:]:>20} len={len(b):>3} 1s={ones:>3} density={density:.4f} max1run={max_run}")

# 統計
densities = [bit_density(n) for _, n, _, _ in results_sorted]
all_densities_sample = []
import random
random.seed(42)
for _ in range(1000):
    rn = random.randrange(3, N_MAX, 2)
    all_densities_sample.append(bit_density(rn))

print(f"\n--- 1の密度の統計 ---")
print(f"  d/u最小上位100: mean={sum(densities)/len(densities):.4f}, min={min(densities):.4f}, max={max(densities):.4f}")
print(f"  ランダム1000個:  mean={sum(all_densities_sample)/len(all_densities_sample):.4f}")


# ===========================================================
# 4. d/u - log₂(3) の最小値がどう推移するか（詳細）
# ===========================================================
print(f"\n{'=' * 70}")
print(f"4. d/u - log₂(3) の最小差分の推移")
print(f"{'=' * 70}")

print(f"\n  全体の最小 d/u: {global_min_ratio:.15f} (n={global_min_n})")
print(f"  log₂(3):        {LOG2_3:.15f}")
print(f"  差分:            {global_min_ratio - LOG2_3:.15f}")

# 最小差分を持つnの詳細
d, u, min_int, has_b = collatz_du_with_interim_min(global_min_n)
print(f"\n  n={global_min_n} の詳細:")
print(f"    d={d}, u={u}, d/u={d/u:.15f}")
print(f"    途中の最小 d/u = {min_int:.15f}")
print(f"    途中で d/u < log₂(3): {'あり' if has_b else 'なし'}")
print(f"    2進表現: {bin(global_min_n)[2:]}")
print(f"    1の密度: {bit_density(global_min_n):.6f}")


# ===========================================================
# 5. 途中の累積 d/u が log₂(3) を下回る瞬間の統計
# ===========================================================
print(f"\n{'=' * 70}")
print(f"5. 途中の累積 d/u < log₂(3) の統計（サンプル詳細）")
print(f"{'=' * 70}")

# 代表的なケースを詳しく見る
print(f"\n  全体: {count_interim_below}/{count_total} ({count_interim_below/count_total*100:.2f}%) の n で途中 d/u < log₂(3)")

# 範囲ごとの割合
print(f"\n--- 範囲ごとの途中 d/u < log₂(3) の割合 ---")
for check_max in [100, 1000, 10000, 100000, 1000000]:
    cnt_below = 0
    cnt_all = 0
    for n in range(3, min(check_max + 1, N_MAX + 1), 2):
        _, _, _, has_b = collatz_du_with_interim_min(n)
        cnt_all += 1
        if has_b:
            cnt_below += 1
    print(f"  n ≤ {check_max:>10,}: {cnt_below}/{cnt_all} ({cnt_below/cnt_all*100:.2f}%)")

# 途中でlog₂(3)を下回るnの中で、最小interim ratioが最も低いもの
print(f"\n--- 途中の最小 d/u が最も低い n (上位20, n ≤ 100000) ---")
interim_results = []
for n in range(3, 100001, 2):
    d, u, min_int, has_b = collatz_du_with_interim_min(n)
    if u > 0:
        interim_results.append((min_int, n, d, u))

interim_results.sort()
print(f"{'Rank':>4} {'n':>10} {'d':>6} {'u':>6} {'final d/u':>15} {'interim min':>15} {'gap':>15}")
print("-" * 75)
for i, (min_int, n, d, u) in enumerate(interim_results[:20]):
    final_ratio = d / u
    gap = min_int - LOG2_3
    print(f"{i+1:>4} {n:>10} {d:>6} {u:>6} {final_ratio:>15.10f} {min_int:>15.10f} {gap:>15.10f}")


# ===========================================================
# 6. 収束速度の理論的分析
# ===========================================================
print(f"\n{'=' * 70}")
print(f"6. 理論的分析: d/u の下界")
print(f"{'=' * 70}")

print(f"""
■ 主要な発見

1. 最終 d/u < log₂(3) となる n: {count_below_log23} 個 (n ≤ {N_MAX})
2. 途中の累積 d/u < log₂(3) となる n の割合: {count_interim_below/count_total*100:.2f}%
3. 全体の最小 d/u: {global_min_ratio:.15f} (n={global_min_n})
4. d/u - log₂(3) の最小差: {global_min_ratio - LOG2_3:.15f}

■ メルセンヌ数の傾向
""")

for k, n, d, u, ratio, min_int, has_b in mersenne_results[-5:]:
    print(f"  2^{k}-1: d/u = {ratio:.10f}, diff = {ratio - LOG2_3:.10f}")

print(f"""
■ d/u > log₂(3) が成立する理由（仮説の強化）

コラッツ関数で n → 3n+1 の直後に必ず ÷2 が発生するため、
偶数ステップが構造的に優位になる。

  実効的な偶数ステップ確率 p > log₂(3)/(1+log₂(3)) ≈ 0.6131

が n ≤ {N_MAX} の全ての奇数で保持されている。

■ 10^k ごとの最小 d/u の差分推移
""")

prev_diff = None
for exp in sorted(power_milestones.keys()):
    ratio, n = power_milestones[exp]
    diff = ratio - LOG2_3
    trend = ""
    if prev_diff is not None:
        if diff < prev_diff:
            trend = f" (↓ {prev_diff/diff:.2f}x smaller gap)"
        else:
            trend = f" (→ gap stable/increased)"
    print(f"  10^{exp}: diff = {diff:.12f}{trend}")
    prev_diff = diff

print(f"""
差分が 10^k が大きくなるにつれて縮小するなら、
d/u > log₂(3) が常に成立するかは未確定。
差分が一定の正の値に収束するなら、
d/u > log₂(3) は全ての n で成立する可能性が高い。
""")

print("完了")
