#!/usr/bin/env python3
"""
Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の逆像分岐分析 (v2: 高速版)

T^{-k}(1) のk番目の層を構築し、成長率・分布を解析する。
逆写像には上限を設けず、木構造を直接追跡する。
"""

import math
from collections import defaultdict, Counter
import time
import sys

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse_bounded(m, max_n):
    """T(n) = m となる奇数 n で n <= max_n のものを全て返す"""
    if m % 3 == 0:
        return []
    results = []
    if m % 3 == 1:
        start_a, step = 2, 2
    else:
        start_a, step = 1, 2
    a = start_a
    while True:
        val = m * (1 << a) - 1
        if val // 3 > max_n:
            break
        if val % 3 == 0:
            n = val // 3
            if n > 0 and n % 2 == 1:
                results.append((n, a))
        a += step
    return results

# ============================================================
# 構築: T^{-k}(1) for k=0..MAX_DEPTH
# ============================================================
MAX_DEPTH = 35
# 上限は十分大きくするが、計算可能な範囲に制限
# 各層の最大値は指数的に増えるので、適応的に上限を設定
INITIAL_MAX = 10**12

print("=" * 70)
print(f"Syracuse逆像木 T^{{-k}}(1) の構築と解析 (k=0..{MAX_DEPTH})")
print("=" * 70)

layers = [set() for _ in range(MAX_DEPTH + 1)]
layers[0] = {1}
all_visited = {1: 0}

start_time = time.time()

for k in range(1, MAX_DEPTH + 1):
    t0 = time.time()
    new_layer = set()

    # 適応的上限: 前の層の最大値の100倍程度
    if layers[k-1]:
        adaptive_max = max(layers[k-1]) * 200
        adaptive_max = max(adaptive_max, 10**8)
    else:
        adaptive_max = INITIAL_MAX

    for m in layers[k-1]:
        preimages = inverse_syracuse_bounded(m, adaptive_max)
        for n, a in preimages:
            if n not in all_visited:
                new_layer.add(n)
                all_visited[n] = k

    layers[k] = new_layer
    t1 = time.time()

    if len(new_layer) > 0:
        sys.stdout.write(f"  k={k:>3}: |T^{{-k}}| = {len(new_layer):>12,}  "
                        f"(min={min(new_layer)}, max={max(new_layer)})  "
                        f"[{t1-t0:.2f}s]\n")
    else:
        sys.stdout.write(f"  k={k:>3}: |T^{{-k}}| = 0  [{t1-t0:.2f}s]\n")
    sys.stdout.flush()

    # タイムアウト防止
    if time.time() - start_time > 300:
        print(f"\n[WARNING] タイムアウト: k={k}で打ち切り")
        MAX_DEPTH = k
        break

total_time = time.time() - start_time
print(f"\n構築完了: {total_time:.2f}秒, 総ノード数: {len(all_visited):,}")

# ============================================================
# 分析1: サイズと成長率
# ============================================================
print("\n" + "=" * 70)
print("分析1: |T^{-k}(1)| のサイズと成長率")
print("=" * 70)

layer_sizes = [len(layers[k]) for k in range(MAX_DEPTH + 1)]
growth_rates = []
cumulative = 0

print(f"\n{'k':>4} {'|T^{-k}(1)|':>15} {'成長率':>12} {'累積':>15}")
print("-" * 50)

for k in range(MAX_DEPTH + 1):
    size = layer_sizes[k]
    cumulative += size
    if k > 0 and layer_sizes[k-1] > 0:
        rate = size / layer_sizes[k-1]
    else:
        rate = float('nan')
    growth_rates.append(rate)
    print(f"{k:>4} {size:>15,} {rate:>12.6f} {cumulative:>15,}")

# ============================================================
# 分析2: 成長率の漸近フィット
# ============================================================
print("\n" + "=" * 70)
print("分析2: 成長率の漸近解析")
print("=" * 70)

valid_rates = [(k, r) for k, r in enumerate(growth_rates) if not math.isnan(r) and r > 0]

if len(valid_rates) > 10:
    recent = valid_rates[-15:]
    avg_rate = sum(r for _, r in recent) / len(recent)
    print(f"直近15層の平均成長率: {avg_rate:.6f}")
    print(f"理論値 4/3 = {4/3:.6f}")
    print(f"差: {avg_rate - 4/3:.6f}")

# log-linear回帰
valid_log = [(k, math.log(s)) for k, s in enumerate(layer_sizes) if s > 0 and k >= 3]
if len(valid_log) >= 5:
    ks = [d[0] for d in valid_log]
    logs = [d[1] for d in valid_log]
    n_pts = len(valid_log)
    sk = sum(ks); sl = sum(logs); sk2 = sum(x**2 for x in ks); skl = sum(x*y for x, y in zip(ks, logs))
    slope = (n_pts * skl - sk * sl) / (n_pts * sk2 - sk**2)
    intercept = (sl - slope * sk) / n_pts
    growth_base = math.exp(slope)

    print(f"\nlog(|T^{{-k}}(1)|) = {slope:.6f} * k + {intercept:.6f}")
    print(f"|T^{{-k}}(1)| ~ {math.exp(intercept):.4f} * {growth_base:.6f}^k")
    print(f"実効成長率: {growth_base:.6f}")

    # R^2計算
    y_mean = sl / n_pts
    ss_tot = sum((y - y_mean)**2 for y in logs)
    ss_res = sum((y - (slope * x + intercept))**2 for x, y in zip(ks, logs))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    print(f"R^2 = {r_squared:.8f}")

# ============================================================
# 分析3: mod分布
# ============================================================
print("\n" + "=" * 70)
print("分析3: mod 6, 8, 16 分布")
print("=" * 70)

# mod 6 (入次数関連)
print("\n--- mod 6 分布 ---")
print(f"{'k':>4} {'≡1(6)':>8} {'≡3(6)':>8} {'≡5(6)':>8} {'|層|':>10}")
for k in range(MAX_DEPTH + 1):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    c1 = sum(1 for n in layers[k] if n % 6 == 1) / total
    c3 = sum(1 for n in layers[k] if n % 6 == 3) / total
    c5 = sum(1 for n in layers[k] if n % 6 == 5) / total
    print(f"{k:>4} {c1:>8.4f} {c3:>8.4f} {c5:>8.4f} {total:>10,}")

# mod 8
print("\n--- mod 8 分布 (奇数residue) ---")
print(f"{'k':>4} {'≡1(8)':>8} {'≡3(8)':>8} {'≡5(8)':>8} {'≡7(8)':>8}")
for k in range(MAX_DEPTH + 1):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    vals = []
    for r in [1, 3, 5, 7]:
        vals.append(sum(1 for n in layers[k] if n % 8 == r) / total)
    print(f"{k:>4} {vals[0]:>8.4f} {vals[1]:>8.4f} {vals[2]:>8.4f} {vals[3]:>8.4f}")

# ============================================================
# 分析4: 層間遷移（子の数分布）
# ============================================================
print("\n" + "=" * 70)
print("分析4: 各要素が次の層に生む子の数")
print("=" * 70)

print(f"{'k':>4} {'0子':>8} {'1子':>8} {'2子':>8} {'3子':>8} {'4+子':>8} {'平均':>8}")
for k in range(min(30, MAX_DEPTH)):
    if len(layers[k]) == 0 or k + 1 >= len(layers):
        continue

    # 適応的上限
    if layers[k]:
        check_max = max(layers[k]) * 200
    else:
        continue

    child_dist = Counter()
    total_children = 0

    for m in layers[k]:
        children_in_next = 0
        preimages = inverse_syracuse_bounded(m, check_max)
        for n, a in preimages:
            if n in layers[k + 1]:
                children_in_next += 1
        child_dist[children_in_next] += 1
        total_children += children_in_next

    total = len(layers[k])
    avg = total_children / total if total > 0 else 0
    c0 = child_dist.get(0, 0) / total * 100
    c1 = child_dist.get(1, 0) / total * 100
    c2 = child_dist.get(2, 0) / total * 100
    c3 = child_dist.get(3, 0) / total * 100
    c4p = sum(v for kk, v in child_dist.items() if kk >= 4) / total * 100
    print(f"{k:>4} {c0:>7.1f}% {c1:>7.1f}% {c2:>7.1f}% {c3:>7.1f}% {c4p:>7.1f}% {avg:>8.4f}")

# ============================================================
# 分析5: v2(3n+1) 分布
# ============================================================
print("\n" + "=" * 70)
print("分析5: 各層のv2(3n+1)分布")
print("=" * 70)

print(f"{'k':>4} {'v=1':>8} {'v=2':>8} {'v=3':>8} {'v=4':>8} {'v>=5':>8} {'平均':>8}")
for k in range(MAX_DEPTH + 1):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    v2_counts = Counter()
    v2_sum = 0
    for n in layers[k]:
        v = v2(3 * n + 1)
        v2_counts[v] += 1
        v2_sum += v
    avg = v2_sum / total
    vals = [v2_counts.get(i, 0) / total * 100 for i in range(1, 5)]
    v5p = sum(v for kk, v in v2_counts.items() if kk >= 5) / total * 100
    print(f"{k:>4} {vals[0]:>7.1f}% {vals[1]:>7.1f}% {vals[2]:>7.1f}% {vals[3]:>7.1f}% {v5p:>7.1f}% {avg:>8.4f}")

# ============================================================
# 分析6: 被覆密度
# ============================================================
print("\n" + "=" * 70)
print("分析6: 累積被覆密度")
print("=" * 70)

thresholds = [10**i for i in range(2, 8)]
print(f"{'N':>12} {'被覆奇数':>12} {'奇数総数':>12} {'密度':>10}")
for N in thresholds:
    covered = sum(1 for v in all_visited if v <= N)
    total_odd = (N + 1) // 2
    density = covered / total_odd if total_odd > 0 else 0
    print(f"{N:>12,} {covered:>12,} {total_odd:>12,} {density:>10.6f}")

# ============================================================
# 分析7: ビット長の増加率
# ============================================================
print("\n" + "=" * 70)
print("分析7: 各層の平均ビット長と理論的増加")
print("=" * 70)

print(f"{'k':>4} {'平均bit':>10} {'理論bit':>10} {'差':>10}")
for k in range(MAX_DEPTH + 1):
    if len(layers[k]) == 0:
        continue
    avg_bits = sum(n.bit_length() for n in layers[k]) / len(layers[k])
    # 理論: 各ステップで log2(4/3) ≈ 0.415 ビット増加
    theoretical_bits = 1 + k * math.log2(4/3)
    print(f"{k:>4} {avg_bits:>10.2f} {theoretical_bits:>10.2f} {avg_bits - theoretical_bits:>10.2f}")

# ============================================================
# 分析8: 特殊な層の要素
# ============================================================
print("\n" + "=" * 70)
print("分析8: 各層の最小・最大要素と特記事項")
print("=" * 70)

for k in range(min(25, MAX_DEPTH + 1)):
    if len(layers[k]) == 0:
        continue
    s = sorted(layers[k])
    n_show = min(8, len(s))
    print(f"k={k:>3}: |{len(s):>8,}| 最小{n_show}個: {s[:n_show]}")

# ============================================================
# 分析9: 成長率の周期性・振動
# ============================================================
print("\n" + "=" * 70)
print("分析9: 成長率の振動パターン")
print("=" * 70)

valid_gr = [(k, r) for k, r in enumerate(growth_rates) if not math.isnan(r) and k >= 3]
if len(valid_gr) >= 10:
    rates_only = [r for _, r in valid_gr]
    mean_r = sum(rates_only) / len(rates_only)

    # 自己相関
    print(f"平均成長率: {mean_r:.6f}")
    print("\n成長率の自己相関:")
    for lag in range(1, min(10, len(rates_only) // 2)):
        n_ac = len(rates_only) - lag
        cov = sum((rates_only[i] - mean_r) * (rates_only[i + lag] - mean_r) for i in range(n_ac)) / n_ac
        var = sum((r - mean_r)**2 for r in rates_only) / len(rates_only)
        ac = cov / var if var > 0 else 0
        print(f"  lag={lag}: {ac:>8.4f}")

    # 連続する成長率の差
    diffs = [rates_only[i+1] - rates_only[i] for i in range(len(rates_only)-1)]
    print(f"\n成長率の変動:")
    print(f"  最大増加: {max(diffs):.6f}")
    print(f"  最大減少: {min(diffs):.6f}")
    print(f"  平均変動: {sum(abs(d) for d in diffs) / len(diffs):.6f}")

# ============================================================
# 分析10: mod 3 での入次数0ノードの密度
# ============================================================
print("\n" + "=" * 70)
print("分析10: 3の倍数(入次数0)ノードが逆木に出現しない確認")
print("=" * 70)

multiples_of_3 = [n for n in all_visited if n % 3 == 0]
print(f"逆木中の3の倍数の数: {len(multiples_of_3)}")
if multiples_of_3:
    print(f"例: {sorted(multiples_of_3)[:20]}")
    print("[注意] Syracuse写像は奇数のみ扱うので、3の倍数の奇数(=3,9,15,...)は")
    print("入次数0のため逆木に出現しないはず。出現していれば検証必要。")

# ============================================================
# 最終まとめ
# ============================================================
print("\n" + "=" * 70)
print("最終まとめ")
print("=" * 70)

print(f"\n逆像木の深さ: {MAX_DEPTH}")
print(f"総ノード数: {len(all_visited):,}")
print(f"最大層サイズ: {max(layer_sizes):,} (k={layer_sizes.index(max(layer_sizes))})")

if 'growth_base' in dir():
    print(f"実効成長率: {growth_base:.6f}")
    print(f"理論値(4/3): {4/3:.6f}")

# 主要な発見をまとめ
findings = []
if 'growth_base' in dir():
    if abs(growth_base - 4/3) < 0.05:
        findings.append(f"実効成長率 {growth_base:.4f} は理論値 4/3 に近い")
    else:
        findings.append(f"実効成長率 {growth_base:.4f} は理論値 4/3 から乖離")

print(f"\n発見:")
for f in findings:
    print(f"  - {f}")

print("\n完了。")
