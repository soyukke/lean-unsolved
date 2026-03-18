#!/usr/bin/env python3
"""
探索050: コラッツ軌道のビットエントロピーの単調減少性を検証

各数 n のビット表現に関するエントロピー指標を定義し、
Syracuse軌道上での推移を追跡する。

指標:
1. ビット長 L(n) = floor(log2(n)) + 1
2. Shannon entropy H(n) = -p*log2(p) - (1-p)*log2(1-p) where p = popcount(n)/L(n)
3. 圧縮率 C(n) = zlib圧縮後サイズ / 元サイズ
"""

import math
import zlib
import statistics
from collections import Counter, defaultdict


def syracuse(n):
    """Syracuse写像 T(n)"""
    if n % 2 == 0:
        return n // 2
    else:
        return (3 * n + 1) // 2


def syracuse_orbit(n, max_steps=10000):
    """Syracuse軌道を返す（1に到達するまで）"""
    orbit = [n]
    seen = {n}
    current = n
    for _ in range(max_steps):
        current = syracuse(current)
        orbit.append(current)
        if current == 1:
            break
        if current in seen:
            break
        seen.add(current)
    return orbit


def bit_length(n):
    """ビット長"""
    if n <= 0:
        return 0
    return n.bit_length()


def popcount(n):
    """1ビットの数"""
    return bin(n).count('1')


def shannon_entropy(n):
    """ビット列のShannon entropy (正規化: 0-1)"""
    L = bit_length(n)
    if L <= 1:
        return 0.0
    p = popcount(n) / L
    if p == 0 or p == 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def compression_ratio(n):
    """zlib圧縮率"""
    if n <= 0:
        return 0.0
    bits = bin(n)[2:]  # '0b'を除去
    data = bits.encode('ascii')
    if len(data) == 0:
        return 0.0
    compressed = zlib.compress(data, 9)
    return len(compressed) / len(data)


def bit_density(n):
    """1ビットの密度 = popcount / bit_length"""
    L = bit_length(n)
    if L == 0:
        return 0.0
    return popcount(n) / L


# =============================================================
# 解析1: 軌道上のビット長・エントロピーの推移
# =============================================================
def analyze_orbit_entropy(n):
    """1つの軌道について各指標の推移を返す"""
    orbit = syracuse_orbit(n)
    lengths = [bit_length(x) for x in orbit]
    entropies = [shannon_entropy(x) for x in orbit]
    densities = [bit_density(x) for x in orbit]
    return orbit, lengths, entropies, densities


def count_monotone_violations(seq):
    """単調減少に反するステップの数を数える"""
    violations = 0
    for i in range(1, len(seq)):
        if seq[i] > seq[i - 1]:
            violations += 1
    return violations


print("=" * 70)
print("探索050: コラッツ軌道のビットエントロピーの単調減少性")
print("=" * 70)

# =============================================================
# Part 1: 具体例での軌道推移
# =============================================================
print("\n" + "=" * 70)
print("Part 1: 具体例での軌道推移")
print("=" * 70)

example_ns = [27, 97, 127, 255, 703, 871, 6171, 77031]
for n in example_ns:
    orbit, lengths, entropies, densities = analyze_orbit_entropy(n)
    steps = len(orbit) - 1
    bl_violations = count_monotone_violations(lengths)
    ent_violations = count_monotone_violations(entropies)
    print(f"\nn = {n} (ビット長={bit_length(n)}, 軌道長={steps})")
    print(f"  ビット長の単調減少違反: {bl_violations}/{steps} "
          f"({100*bl_violations/max(steps,1):.1f}%)")
    print(f"  Shannon entropy の単調減少違反: {ent_violations}/{steps} "
          f"({100*ent_violations/max(steps,1):.1f}%)")
    # 最初の20ステップを表示
    show = min(20, len(orbit))
    print(f"  最初{show}ステップ:")
    print(f"    {'step':>4} {'value':>12} {'bits':>5} {'H(n)':>6} {'density':>7}")
    for i in range(show):
        print(f"    {i:4d} {orbit[i]:12d} {lengths[i]:5d} "
              f"{entropies[i]:6.4f} {densities[i]:7.4f}")


# =============================================================
# Part 2: 大量のnでの統計
# =============================================================
print("\n" + "=" * 70)
print("Part 2: 大量のnでの統計（n=3,5,7,...,19999 奇数のみ）")
print("=" * 70)

bl_violation_rates = []
ent_violation_rates = []
orbit_lengths = []
max_bl_steps = []  # ビット長が最大になるステップ
max_bl_ratios = []  # 最大ビット長 / 初期ビット長

for n in range(3, 20000, 2):
    orbit, lengths, entropies, densities = analyze_orbit_entropy(n)
    steps = len(orbit) - 1
    if steps == 0:
        continue

    bl_v = count_monotone_violations(lengths) / steps
    ent_v = count_monotone_violations(entropies) / steps
    bl_violation_rates.append(bl_v)
    ent_violation_rates.append(ent_v)
    orbit_lengths.append(steps)

    max_bl = max(lengths)
    max_bl_idx = lengths.index(max_bl)
    max_bl_steps.append(max_bl_idx / steps if steps > 0 else 0)
    max_bl_ratios.append(max_bl / lengths[0] if lengths[0] > 0 else 0)

print(f"\n解析対象: {len(bl_violation_rates)} 個の奇数")
print(f"\nビット長の単調減少違反率:")
print(f"  平均: {statistics.mean(bl_violation_rates):.4f}")
print(f"  中央値: {statistics.median(bl_violation_rates):.4f}")
print(f"  最大: {max(bl_violation_rates):.4f}")
print(f"  最小: {min(bl_violation_rates):.4f}")
print(f"  標準偏差: {statistics.stdev(bl_violation_rates):.4f}")

print(f"\nShannon entropy の単調減少違反率:")
print(f"  平均: {statistics.mean(ent_violation_rates):.4f}")
print(f"  中央値: {statistics.median(ent_violation_rates):.4f}")
print(f"  最大: {max(ent_violation_rates):.4f}")
print(f"  最小: {min(ent_violation_rates):.4f}")
print(f"  標準偏差: {statistics.stdev(ent_violation_rates):.4f}")

print(f"\nビット長が最大になるステップ（軌道長に対する相対位置）:")
print(f"  平均: {statistics.mean(max_bl_steps):.4f}")
print(f"  中央値: {statistics.median(max_bl_steps):.4f}")

print(f"\n最大ビット長 / 初期ビット長:")
print(f"  平均: {statistics.mean(max_bl_ratios):.4f}")
print(f"  中央値: {statistics.median(max_bl_ratios):.4f}")
print(f"  最大: {max(max_bl_ratios):.4f}")


# =============================================================
# Part 3: ビット長の平均減少率とd/uの関係
# =============================================================
print("\n" + "=" * 70)
print("Part 3: ビット長の減少率とd/u比の関係")
print("=" * 70)

def compute_du_and_bl_rate(n):
    """軌道のd(偶数ステップ数), u(奇数ステップ数), ビット長変化率を計算"""
    orbit = syracuse_orbit(n)
    if len(orbit) <= 1:
        return None
    d_count = 0  # 偶数（÷2だけ）
    u_count = 0  # 奇数（3n+1→÷2）
    for x in orbit[:-1]:
        if x % 2 == 0:
            d_count += 1
        else:
            u_count += 1

    bl_start = bit_length(orbit[0])
    bl_end = bit_length(orbit[-1])  # 1なら1
    steps = len(orbit) - 1
    bl_rate = (bl_end - bl_start) / steps if steps > 0 else 0
    du_ratio = d_count / u_count if u_count > 0 else float('inf')
    return d_count, u_count, du_ratio, bl_rate, steps

# ビット長ごとにグループ化して分析
print(f"\n初期ビット長別の平均d/u比とビット長減少率:")
print(f"{'初期BL':>7} {'個数':>6} {'平均d/u':>8} {'平均BL減少率':>12} {'理論BL減少率':>12}")

bl_groups = defaultdict(list)
for n in range(3, 20000, 2):
    result = compute_du_and_bl_rate(n)
    if result is None:
        continue
    d, u, du, bl_rate, steps = result
    bl_groups[bit_length(n)].append((du, bl_rate))

for bl in sorted(bl_groups.keys()):
    items = bl_groups[bl]
    avg_du = statistics.mean([x[0] for x in items])
    avg_bl_rate = statistics.mean([x[1] for x in items])
    # 理論的なビット長減少率: 各ステップで偶数なら-1bit, 奇数なら+log2(3/2)≈+0.585 bit
    # 平均減少率 = (-d + u*log2(3/2)) / (d+u) = (-1 + (1/(du+1))*log2(3/2)) ...
    # 1ステップあたり: 偶数の割合 p = d/(d+u), 奇数の割合 1-p
    # 期待変化 = p*(-1) + (1-p)*(log2(3/2)) = -p + (1-p)*0.585
    p = avg_du / (avg_du + 1)
    theory_rate = -p + (1 - p) * math.log2(3 / 2)
    print(f"{bl:7d} {len(items):6d} {avg_du:8.4f} {avg_bl_rate:12.6f} {theory_rate:12.6f}")


# =============================================================
# Part 4: 圧縮率の推移
# =============================================================
print("\n" + "=" * 70)
print("Part 4: ビット列の圧縮率の軌道上推移（サンプル）")
print("=" * 70)

sample_ns = [27, 127, 703, 6171]
for n in sample_ns:
    orbit = syracuse_orbit(n)
    steps = len(orbit) - 1
    # 10点をサンプリング
    indices = [int(i * steps / 9) for i in range(10)] if steps >= 9 else list(range(len(orbit)))
    print(f"\nn = {n} (軌道長 = {steps})")
    print(f"  {'step':>5} {'value':>12} {'bits':>5} {'圧縮率':>7} {'H(n)':>6}")
    for idx in indices:
        v = orbit[idx]
        cr = compression_ratio(v) if v > 1 else 0.0
        h = shannon_entropy(v)
        print(f"  {idx:5d} {v:12d} {bit_length(v):5d} {cr:7.4f} {h:6.4f}")


# =============================================================
# Part 5: ビットエントロピーの「軌道平均」の振る舞い
# =============================================================
print("\n" + "=" * 70)
print("Part 5: 軌道上のShannon entropyの統計的振る舞い")
print("=" * 70)

# 軌道を前半・後半に分けてエントロピーの平均を比較
first_half_wins = 0
second_half_wins = 0
ties = 0

for n in range(3, 20000, 2):
    orbit = syracuse_orbit(n)
    if len(orbit) < 4:
        continue
    entropies = [shannon_entropy(x) for x in orbit]
    mid = len(entropies) // 2
    first_avg = statistics.mean(entropies[:mid])
    second_avg = statistics.mean(entropies[mid:])
    if first_avg > second_avg:
        first_half_wins += 1
    elif second_avg > first_avg:
        second_half_wins += 1
    else:
        ties += 1

total = first_half_wins + second_half_wins + ties
print(f"\n前半vs後半のShannon entropy平均比較 (n=3..19999の奇数):")
print(f"  前半 > 後半: {first_half_wins} ({100*first_half_wins/total:.1f}%)")
print(f"  後半 > 前半: {second_half_wins} ({100*second_half_wins/total:.1f}%)")
print(f"  同値: {ties} ({100*ties/total:.1f}%)")


# =============================================================
# Part 6: ビット密度と軌道の関係
# =============================================================
print("\n" + "=" * 70)
print("Part 6: 初期ビット密度と軌道長の関係")
print("=" * 70)

density_groups = defaultdict(list)
for n in range(3, 50000, 2):
    d = bit_density(n)
    orbit = syracuse_orbit(n)
    steps = len(orbit) - 1
    # 密度を0.1刻みでグループ化
    group = round(d, 1)
    density_groups[group].append(steps)

print(f"\n{'密度':>5} {'個数':>6} {'平均軌道長':>10} {'中央値':>8} {'最大':>8}")
for d in sorted(density_groups.keys()):
    items = density_groups[d]
    if len(items) < 10:
        continue
    avg = statistics.mean(items)
    med = statistics.median(items)
    mx = max(items)
    print(f"{d:5.1f} {len(items):6d} {avg:10.1f} {med:8.1f} {mx:8d}")


# =============================================================
# Part 7: 「ビット長増加イベント」の連続性
# =============================================================
print("\n" + "=" * 70)
print("Part 7: ビット長が連続して増加する最大区間")
print("=" * 70)

max_increase_runs = []
for n in range(3, 20000, 2):
    orbit = syracuse_orbit(n)
    lengths = [bit_length(x) for x in orbit]
    max_run = 0
    current_run = 0
    for i in range(1, len(lengths)):
        if lengths[i] > lengths[i - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    max_increase_runs.append((max_run, n))

max_increase_runs.sort(reverse=True)
print(f"\nビット長が連続増加する最大区間長 top10:")
for run, n in max_increase_runs[:10]:
    orbit = syracuse_orbit(n)
    print(f"  n={n:>6d}: 最大連続増加={run}, 軌道長={len(orbit)-1}, "
          f"初期BL={bit_length(n)}")

print(f"\n連続増加区間長の統計:")
runs_only = [r for r, _ in max_increase_runs]
print(f"  平均: {statistics.mean(runs_only):.2f}")
print(f"  中央値: {statistics.median(runs_only):.1f}")
print(f"  最大: {max(runs_only)}")

# 連続増加区間長の分布
run_dist = Counter(runs_only)
print(f"\n  連続増加区間長の分布:")
for k in sorted(run_dist.keys()):
    print(f"    {k:3d}: {run_dist[k]:6d} ({100*run_dist[k]/len(runs_only):.1f}%)")


print("\n" + "=" * 70)
print("解析完了")
print("=" * 70)
