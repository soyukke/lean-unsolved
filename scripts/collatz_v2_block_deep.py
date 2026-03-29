#!/usr/bin/env python3
"""
v2列ブロック統計の深掘り分析

1. 冗長度の成長法則（線形 vs 超線形）
2. v2=4の過大表現の原因分析
3. 禁止パターンの閾値分析（理論頻度をもっと低くして）
4. 長距離相関の定量化
5. マルコフ近似の次数とエントロピー率の比較
"""

import math
from collections import Counter, defaultdict
from itertools import product
import json

# ========================================
# 基本関数
# ========================================

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

def get_v2_sequence(n, length=500):
    seq = []
    current = n
    for _ in range(length):
        if current == 1:
            break
        val = 3 * current + 1
        v = v2(val)
        seq.append(v)
        current = val >> v
    return seq

def aggregate_v2_sequences(n_start, n_end, step=2, max_orbit_len=500):
    all_seq = []
    count = 0
    for n in range(n_start, n_end + 1, step):
        if n % 2 == 0:
            continue
        seq = get_v2_sequence(n, max_orbit_len)
        if len(seq) >= 10:
            all_seq.extend(seq)
            count += 1
    return all_seq, count

def extract_blocks(seq, L):
    blocks = []
    for i in range(len(seq) - L + 1):
        block = tuple(seq[i:i+L])
        blocks.append(block)
    return blocks

def compute_block_frequencies(seq, L):
    blocks = extract_blocks(seq, L)
    counter = Counter(blocks)
    total = len(blocks)
    freqs = {block: count / total for block, count in counter.items()}
    return freqs, counter, total

def compute_block_entropy(freqs):
    H = 0.0
    for block, freq in freqs.items():
        if freq > 0:
            H -= freq * math.log2(freq)
    return H

def theoretical_independent_freq(block):
    prob = 1.0
    for v in block:
        prob *= 1.0 / (2 ** v)
    return prob

# ========================================
# メインデータ生成
# ========================================

print("=" * 70)
print("v2列ブロック統計の深掘り分析")
print("=" * 70)

print("\nデータ集約中...")
all_seq, n_count = aggregate_v2_sequences(3, 49999, step=2, max_orbit_len=500)
print(f"v2列総長: {len(all_seq)}, 奇数個数: {n_count}")

# ========================================
# Part 1: 冗長度の成長法則
# ========================================
print("\n" + "-" * 70)
print("Part 1: 冗長度の成長法則 (L=1..8)")
print("-" * 70)

H1 = compute_block_entropy(
    {v: c / len(all_seq) for v, c in Counter(all_seq).items()}
)

entropies = {1: H1}
redundancies = {}
kl_divs = {}

for L in range(2, 9):
    freqs, counter, total = compute_block_frequencies(all_seq, L)
    HL = compute_block_entropy(freqs)
    entropies[L] = HL
    redundancies[L] = L * H1 - HL

    # KL divergence
    kl = 0
    for block, freq in freqs.items():
        theo = theoretical_independent_freq(block)
        if freq > 0 and theo > 0:
            kl += freq * math.log2(freq / theo)
    kl_divs[L] = kl

print(f"\n{'L':>3} {'H(L)':>12} {'L*H(1)':>12} {'冗長度':>12} {'Delta冗長度':>12} "
      f"{'H(L)/L':>10} {'h(L)':>10} {'KL div':>10}")
prev_red = 0
prev_H = H1
for L in range(1, 9):
    HL = entropies[L]
    LH1 = L * H1
    red = L * H1 - HL if L > 1 else 0
    delta_red = red - prev_red
    hL = HL - prev_H if L > 1 else H1
    kl = kl_divs.get(L, 0)
    print(f"  {L:3d} {HL:12.6f} {LH1:12.6f} {red:12.6f} {delta_red:12.6f} "
          f"{HL/L:10.6f} {hL:10.6f} {kl:10.6f}")
    prev_red = red
    prev_H = HL

# 冗長度の成長が線形かの確認
print(f"\n冗長度の成長パターン分析:")
reds = [(L, redundancies[L]) for L in range(2, 9)]
for i in range(1, len(reds)):
    L, r = reds[i]
    L_prev, r_prev = reds[i-1]
    if r_prev > 0:
        ratio = r / r_prev
        print(f"  R({L})/R({L-1}) = {ratio:.4f}")

# 線形フィット
from statistics import linear_regression
xs = [L for L in range(2, 9)]
ys = [redundancies[L] for L in range(2, 9)]
try:
    slope, intercept = linear_regression(xs, ys)
    print(f"\n線形フィット: 冗長度 = {slope:.6f} * L + ({intercept:.6f})")
    # 二次フィット（手動）
    # R(L) = a*L^2 + b*L + c の最小二乗
    n_pts = len(xs)
    sum_x = sum(xs)
    sum_x2 = sum(x**2 for x in xs)
    sum_x3 = sum(x**3 for x in xs)
    sum_x4 = sum(x**4 for x in xs)
    sum_y = sum(ys)
    sum_xy = sum(x*y for x, y in zip(xs, ys))
    sum_x2y = sum(x**2 * y for x, y in zip(xs, ys))

    print(f"\n  R(L)/L の推移:")
    for L in range(2, 9):
        print(f"    R({L})/L = {redundancies[L]/L:.6f}")
except Exception as e:
    print(f"  フィット失敗: {e}")


# ========================================
# Part 2: v2=4の過大表現の原因分析
# ========================================
print("\n" + "-" * 70)
print("Part 2: v2=4の過大表現の原因分析")
print("-" * 70)

# v2=4が出現する前後のコンテキスト
v4_before = Counter()
v4_after = Counter()
for i in range(1, len(all_seq) - 1):
    if all_seq[i] == 4:
        v4_before[all_seq[i-1]] += 1
        v4_after[all_seq[i+1]] += 1

total_v4 = sum(v4_before.values())
print(f"\nv2=4の出現数: {total_v4}")
print(f"\nv2=4の直前のv2値分布:")
for v in sorted(v4_before.keys()):
    p = v4_before[v] / total_v4
    print(f"  v2={v}: {p:.4f} (出現数={v4_before[v]})")

print(f"\nv2=4の直後のv2値分布:")
total_v4_after = sum(v4_after.values())
for v in sorted(v4_after.keys()):
    p = v4_after[v] / total_v4_after
    theo = 1.0 / (2 ** v)
    print(f"  v2={v}: {p:.4f} (理論={theo:.4f}, 比={p/theo:.4f})")

# (5,4) ペアの特別な頻度を分析
print(f"\n(5,4) ペアの後に続くv2値:")
triple_54 = defaultdict(int)
for i in range(len(all_seq) - 2):
    if all_seq[i] == 5 and all_seq[i+1] == 4:
        triple_54[all_seq[i+2]] += 1
total_54 = sum(triple_54.values())
if total_54 > 0:
    for v in sorted(triple_54.keys()):
        p = triple_54[v] / total_54
        print(f"  (5,4,{v}): {p:.4f} (出現数={triple_54[v]})")

# (1,5,4) の頻度が異常に高い理由を数論的に考察
print(f"\n数論的分析: v2(3n+1)=5 となるn mod 32:")
for r in range(32):
    n = 2 * r + 1  # 奇数
    val = 3 * n + 1
    if v2(val) == 5:
        print(f"  n = {n} mod 64: v2(3*{n}+1) = v2({val}) = {v2(val)}")
        # 次のステップ
        next_n = val >> v2(val)
        next_val = 3 * next_n + 1
        print(f"    T(n) = {next_n}, v2(3*{next_n}+1) = v2({next_val}) = {v2(next_val)}")

# v2=4が異常に多い理由: mod 16での構造
print(f"\nmod 16でのv2分布:")
for r in range(16):
    if r % 2 == 0:
        continue
    val = 3 * r + 1
    v = v2(val)
    print(f"  n = {r} mod 16: v2(3*{r}+1) = v2({val}) = {v}")


# ========================================
# Part 3: 連続v2=1のラン長分布
# ========================================
print("\n" + "-" * 70)
print("Part 3: 連続v2=1のラン長分布")
print("-" * 70)

runs_of_1 = []
current_run = 0
for v in all_seq:
    if v == 1:
        current_run += 1
    else:
        if current_run > 0:
            runs_of_1.append(current_run)
        current_run = 0
if current_run > 0:
    runs_of_1.append(current_run)

run_counter = Counter(runs_of_1)
total_runs = len(runs_of_1)
print(f"v2=1のラン数: {total_runs}")
print(f"\n{'ラン長':>6} {'実測頻度':>10} {'理論(幾何)':>12} {'比率':>8} {'出現数':>8}")
# 独立仮定での幾何分布: P(run=k) = p^(k-1) * (1-p) where p = P(v2=1)
p1 = Counter(all_seq)[1] / len(all_seq)
for k in sorted(run_counter.keys()):
    if k > 20:
        break
    obs = run_counter[k] / total_runs
    theo = p1 ** (k - 1) * (1 - p1)
    print(f"  {k:6d} {obs:10.6f} {theo:12.6f} {obs/theo:8.4f} {run_counter[k]:8d}")

print(f"\n平均ラン長: {sum(runs_of_1) / len(runs_of_1):.4f}")
print(f"理論平均ラン長 (幾何): {1 / (1 - p1):.4f}")


# ========================================
# Part 4: マルコフ近似によるエントロピー率
# ========================================
print("\n" + "-" * 70)
print("Part 4: マルコフ近似の次数とエントロピー率")
print("-" * 70)

# k次マルコフモデルのエントロピー率 = H(k+1) - H(k)
print(f"\n{'次数k':>5} {'エントロピー率 h':>18} {'独立率との差':>14}")
for k in range(0, 8):
    if k == 0:
        h_rate = H1
    else:
        h_rate = entropies[k + 1] - entropies[k]
    diff = H1 - h_rate
    print(f"  {k:5d} {h_rate:18.6f} {diff:14.6f}")

# エントロピー率の収束速度
print(f"\nエントロピー率の差分（収束速度）:")
prev_rate = H1
for k in range(1, 8):
    rate = entropies[k + 1] - entropies[k]
    delta = prev_rate - rate
    print(f"  h({k}) - h({k+1}) = {delta:.6f}")
    prev_rate = rate


# ========================================
# Part 5: 特定パターンの数論的意味
# ========================================
print("\n" + "-" * 70)
print("Part 5: 高頻度パターンの数論的意味")
print("-" * 70)

# (4,2,2,4,3) が異常に高頻度
print(f"\nパターン (4,2,2,4,3) の分析:")
print(f"  理論頻度 = 1/(16*4*4*16*8) = {1/(16*4*4*16*8):.8f}")
# 実際の出現状況を追跡
pattern_instances = []
for n in range(3, 10001, 2):
    seq = get_v2_sequence(n, 500)
    for i in range(len(seq) - 4):
        if tuple(seq[i:i+5]) == (4, 2, 2, 4, 3):
            pattern_instances.append((n, i))
            break  # 1つだけ記録

print(f"  n=3..10000で出現するnの個数: {len(pattern_instances)}")
if len(pattern_instances) > 0:
    print(f"  出現するnの先頭10個:")
    for n, pos in pattern_instances[:10]:
        seq = get_v2_sequence(n, pos + 10)
        context = seq[max(0, pos-2):pos+7]
        print(f"    n={n}, 位置={pos}, コンテキスト: ...{context}...")

# パターン (1,5,4) の数論的説明
print(f"\nパターン (1,5,4) の数論的分析:")
print(f"  v2=1 -> n = 1 mod 4, T(n) = (3n+1)/2")
print(f"  v2=5 -> T(n) = 21 mod 32, T^2(n) = (3*T(n)+1)/32")
print(f"  v2=4 -> T^2(n) = 5 mod 16")

# 検証: (1,5)が起こる条件
count_15 = 0
count_154 = 0
for n in range(1, 1000, 4):  # n = 1 mod 4 -> v2(3n+1) >= 1
    if n % 2 == 0:
        continue
    val1 = 3 * n + 1
    if v2(val1) != 1:
        continue
    n2 = val1 >> 1
    val2 = 3 * n2 + 1
    if v2(val2) == 5:
        count_15 += 1
        n3 = val2 >> 5
        val3 = 3 * n3 + 1
        if v2(val3) == 4:
            count_154 += 1
            if count_154 <= 5:
                print(f"  n={n}: {n} -> {n2} (v2=1) -> {n3} (v2=5) -> {val3>>v2(val3)} (v2={v2(val3)})")

print(f"  n=1..999でv2=(1,5)のペア数: {count_15}")
print(f"  n=1..999でv2=(1,5,4)のトリプル数: {count_154}")
if count_15 > 0:
    print(f"  P(v2_3=4 | v2_1=1, v2_2=5) の実測: {count_154/count_15:.4f}")
    print(f"  理論(独立): {1/16:.4f}")


# ========================================
# Part 6: 相互情報量のlag依存性
# ========================================
print("\n" + "-" * 70)
print("Part 6: 相互情報量 I(v2_k; v2_{k+lag}) のlag依存性")
print("-" * 70)

def mutual_info(seq, lag):
    """I(X_t; X_{t+lag})"""
    n = len(seq)
    if lag >= n:
        return 0

    # marginal
    marginal = Counter(seq)
    total = n - lag

    # joint
    joint = Counter()
    for i in range(n - lag):
        joint[(seq[i], seq[i + lag])] += 1

    mi = 0.0
    for (x, y), count in joint.items():
        p_xy = count / total
        p_x = sum(1 for i in range(total) if seq[i] == x) / total
        p_y = sum(1 for i in range(total) if seq[i + lag] == y) / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

# 効率的な実装
def mutual_info_fast(seq, lag):
    n = len(seq)
    total = n - lag

    # Count marginals and joint
    px_counts = Counter()
    py_counts = Counter()
    pxy_counts = Counter()

    for i in range(total):
        x = seq[i]
        y = seq[i + lag]
        px_counts[x] += 1
        py_counts[y] += 1
        pxy_counts[(x, y)] += 1

    mi = 0.0
    for (x, y), count in pxy_counts.items():
        p_xy = count / total
        p_x = px_counts[x] / total
        p_y = py_counts[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

print(f"\n{'lag':>5} {'I(v2_k; v2_{k+lag})':>20} {'bits':>8}")
for lag in range(1, 16):
    mi = mutual_info_fast(all_seq, lag)
    print(f"  {lag:5d} {mi:20.6f} bits")

# 周期性の検出
print(f"\n相互情報量のピーク分析:")
mis = [(lag, mutual_info_fast(all_seq, lag)) for lag in range(1, 30)]
mis_sorted = sorted(mis, key=lambda x: x[1], reverse=True)
print(f"  相互情報量 top 5:")
for lag, mi in mis_sorted[:5]:
    print(f"    lag={lag}: I={mi:.6f} bits")


# ========================================
# Part 7: 個別軌道 vs 集約のブロックエントロピー比較
# ========================================
print("\n" + "-" * 70)
print("Part 7: 個別軌道 vs 集約のブロックエントロピー比較")
print("-" * 70)

# 長い軌道を持つnを選んでそれぞれのブロックエントロピーを計算
long_orbit_ns = []
for n in range(3, 100000, 2):
    seq = get_v2_sequence(n, 2000)
    if len(seq) >= 200:
        long_orbit_ns.append((len(seq), n))

long_orbit_ns.sort(reverse=True)
print(f"\n軌道長 >= 200のnの個数: {len(long_orbit_ns)}")

print(f"\n個別軌道のL=3ブロックエントロピー (top 10 長い軌道):")
individual_H3s = []
for orbit_len, n in long_orbit_ns[:20]:
    seq = get_v2_sequence(n, 2000)
    freqs, _, total = compute_block_frequencies(seq, 3)
    H3 = compute_block_entropy(freqs)
    individual_H3s.append(H3)
    if len(individual_H3s) <= 10:
        print(f"  n={n:>7d} (軌道長={orbit_len:4d}): H(3)={H3:.4f}, H(3)/3={H3/3:.4f}")

if individual_H3s:
    avg_H3 = sum(individual_H3s) / len(individual_H3s)
    print(f"\n  個別軌道H(3)の平均: {avg_H3:.6f}")
    print(f"  集約H(3): {entropies[3]:.6f}")
    print(f"  差: {entropies[3] - avg_H3:.6f}")


print("\n" + "=" * 70)
print("深掘り分析完了")
print("=" * 70)
