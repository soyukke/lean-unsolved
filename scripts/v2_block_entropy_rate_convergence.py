#!/usr/bin/env python3
"""
v2列ブロックエントロピー率 H_k/k の k->infinity 収束先特定

目標:
1. v2(3*T^i(n)+1) の列のブロックエントロピー H_k を k=1..20 で計算
2. エントロピー率 h = lim H_k/k の数値的特定
3. 独立幾何分布のエントロピー H_indep = 2 bits/step との乖離を定量化
4. 条件付きエントロピー h(k) = H(k) - H(k-1) の収束を検証
5. h_top(T) = log2(4/3) = 0.4150 との関係を探る

理論:
- v2(3n+1) ~ Geom(1/2), P(v2=j) = 1/2^j for j >= 1
- 独立なら H(1) = sum j/2^j = 2 bits
- 軌道上の v2 列には微小な相関があるため H_k/k < 2
- h = lim_{k->inf} (H(k) - H(k-1)) = lim_{k->inf} H(k)/k
"""

import math
import json
import time
from collections import Counter, defaultdict
from itertools import product as iproduct

# ========================================
# 基本関数
# ========================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse map T(n) = (3n+1)/2^{v2(3n+1)}"""
    val = 3 * n + 1
    return val >> v2(val)

def get_v2_sequence(n, length=2000):
    """Generate v2 sequence from odd number n"""
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

# ========================================
# データ集約 (大規模)
# ========================================

def aggregate_v2_data(n_start, n_end, step=2, max_len=2000):
    """大量のv2列を集約"""
    all_seq = []
    count = 0
    for n in range(n_start, n_end + 1, step):
        if n % 2 == 0:
            continue
        seq = get_v2_sequence(n, max_len)
        if len(seq) >= 20:
            all_seq.extend(seq)
            count += 1
    return all_seq, count

# ========================================
# エントロピー計算
# ========================================

def compute_block_entropy(seq, L):
    """長さLブロックのShannon entropy H(L)"""
    if L > len(seq):
        return None
    counter = Counter()
    for i in range(len(seq) - L + 1):
        block = tuple(seq[i:i+L])
        counter[block] += 1
    total = sum(counter.values())
    H = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            H -= p * math.log2(p)
    return H, len(counter), total

# ========================================
# 理論値
# ========================================

def theoretical_independent_entropy_per_symbol():
    """独立幾何分布 P(v2=j) = 1/2^j のエントロピー
    H = sum_{j=1}^{inf} (1/2^j) * log2(2^j) = sum j/2^j = 2 bits"""
    return 2.0

def theoretical_block_entropy_independent(L):
    """独立なら H(L) = L * H(1)"""
    return L * 2.0

# ========================================
# Markov次数別エントロピー率推定
# ========================================

def estimate_markov_entropy_rate(seq, order):
    """order次マルコフモデルのエントロピー率を推定

    h_markov(order) = H(order+1) - H(order)

    これはorder次マルコフ過程の定常エントロピー率
    """
    H_k, _, _ = compute_block_entropy(seq, order + 1)
    H_k_minus_1, _, _ = compute_block_entropy(seq, order)
    return H_k - H_k_minus_1

# ========================================
# メイン計算
# ========================================

print("=" * 80)
print("v2列ブロックエントロピー率 H_k/k の収束解析")
print("=" * 80)

# Phase 1: 小規模データで k=1..20
print("\n--- Phase 1: 中規模データ (n=3..99999) ---")
t0 = time.time()
seq_mid, count_mid = aggregate_v2_data(3, 99999, step=2, max_len=1000)
print(f"データ集約完了: {len(seq_mid)} symbols from {count_mid} odd numbers ({time.time()-t0:.1f}s)")

# k=1..20のブロックエントロピー
max_k = 20
results_mid = {}

print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)=H(k)-H(k-1)':>20} "
      f"{'H_ind(k)/k':>12} {'gap':>10} {'#blocks':>10} {'#distinct':>10}")
print("-" * 110)

prev_H = 0.0
for k in range(1, max_k + 1):
    t1 = time.time()
    result = compute_block_entropy(seq_mid, k)
    if result is None:
        break
    H_k, n_distinct, n_total = result
    H_per_k = H_k / k
    h_k = H_k - prev_H  # conditional entropy
    H_ind = k * 2.0
    gap = 2.0 - H_per_k  # gap from independent

    results_mid[k] = {
        'H_k': H_k,
        'H_per_k': H_per_k,
        'h_k': h_k,
        'gap_from_independent': gap,
        'n_distinct': n_distinct,
        'n_total': n_total,
        'time': time.time() - t1,
    }

    print(f"  {k:3d} {H_k:14.6f} {H_per_k:12.6f} {h_k:20.6f} "
          f"{2.0:12.6f} {gap:10.6f} {n_total:10d} {n_distinct:10d}")
    prev_H = H_k

    # k >= 15 でブロック数が少なすぎたら警告
    if n_total < n_distinct * 5:
        print(f"    WARNING: too few samples (total/distinct = {n_total/n_distinct:.1f})")

    # タイムアウト防止
    if time.time() - t0 > 300:  # 5分制限
        print(f"    TIME LIMIT: stopping at k={k}")
        break

# Phase 2: h(k) = H(k) - H(k-1) の収束分析
print("\n\n--- Phase 2: 条件付きエントロピー h(k) の収束分析 ---")
print(f"\n{'k':>3} {'h(k)':>12} {'h(k)-h(k-1)':>14} {'h(k)/h(k-1)':>14}")
print("-" * 55)

h_values = []
for k in range(1, max_k + 1):
    if k not in results_mid:
        break
    h_k = results_mid[k]['h_k']
    h_values.append(h_k)

    if k >= 2:
        h_prev = results_mid[k-1]['h_k']
        delta = h_k - h_prev
        ratio = h_k / h_prev if h_prev > 0 else float('inf')
        print(f"  {k:3d} {h_k:12.6f} {delta:14.6f} {ratio:14.6f}")
    else:
        print(f"  {k:3d} {h_k:12.6f}")

# Phase 3: エントロピー率の外挿推定
print("\n\n--- Phase 3: エントロピー率の外挿推定 ---")

# Method 1: H(k)/k の最後の数値
valid_ks = sorted(results_mid.keys())
if len(valid_ks) >= 5:
    last_5 = valid_ks[-5:]
    h_per_k_last5 = [results_mid[k]['H_per_k'] for k in last_5]
    avg_last5 = sum(h_per_k_last5) / len(h_per_k_last5)
    print(f"\n  Method 1: H(k)/k の最後5点の平均 = {avg_last5:.8f}")

# Method 2: h(k) = H(k) - H(k-1) の最後の値
if len(valid_ks) >= 2:
    last_h = results_mid[valid_ks[-1]]['h_k']
    print(f"  Method 2: h(k_max) = H({valid_ks[-1]}) - H({valid_ks[-2]}) = {last_h:.8f}")

# Method 3: Richardson extrapolation on H(k)/k
if len(valid_ks) >= 3:
    k1, k2, k3 = valid_ks[-3], valid_ks[-2], valid_ks[-1]
    a1 = results_mid[k1]['H_per_k']
    a2 = results_mid[k2]['H_per_k']
    a3 = results_mid[k3]['H_per_k']
    # Aitken's delta-squared
    denom = (a3 - a2) - (a2 - a1)
    if abs(denom) > 1e-15:
        aitken = a3 - (a3 - a2)**2 / denom
        print(f"  Method 3: Aitken extrapolation = {aitken:.8f}")

# Method 4: h(k)の差分列からの外挿
if len(h_values) >= 6:
    # h(k) の差分 delta_h(k) = h(k) - h(k-1) がどう減衰するか
    deltas = [h_values[i] - h_values[i-1] for i in range(1, len(h_values))]

    # delta_h(k) ~ a / k^alpha のフィッティング
    # log|delta_h(k)| = log(a) - alpha * log(k)
    log_k_vals = []
    log_delta_vals = []
    for i, d in enumerate(deltas):
        k_val = i + 2  # k starts from 2
        if abs(d) > 1e-12:
            log_k_vals.append(math.log(k_val))
            log_delta_vals.append(math.log(abs(d)))

    if len(log_k_vals) >= 3:
        n_pts = len(log_k_vals)
        mean_x = sum(log_k_vals) / n_pts
        mean_y = sum(log_delta_vals) / n_pts
        ssxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_k_vals, log_delta_vals))
        ssxx = sum((x - mean_x)**2 for x in log_k_vals)
        if abs(ssxx) > 1e-15:
            alpha = -ssxy / ssxx
            log_a = mean_y + alpha * mean_x
            print(f"  Method 4: delta_h(k) decay: |delta_h| ~ {math.exp(log_a):.6f} / k^{alpha:.4f}")

            # 残りの和を推定: sum_{k=k_max+1}^{inf} delta_h(k)
            # = sum a/k^alpha ~ integral from k_max to inf = a * k_max^(1-alpha) / (alpha-1)
            k_max = len(h_values)
            if alpha > 1:
                remaining = math.exp(log_a) * k_max**(1-alpha) / (alpha - 1)
                estimated_limit = h_values[-1] - remaining  # h(k) is decreasing toward limit
                print(f"    Estimated remaining correction: {remaining:.8f}")
                print(f"    Estimated limit h_inf: {h_values[-1]:.8f} + correction")


# Phase 4: 重要な理論量との比較
print("\n\n--- Phase 4: 理論量との比較 ---")

H_indep = 2.0
log2_43 = math.log2(4/3)
log2_e_times_2 = math.log2(math.e) * 2  # = 2/ln(2) ≈ 2.885
ln_2 = math.log(2)

print(f"\n  重要な定数:")
print(f"    H_indep = 2.000000 bits/step (独立幾何分布のエントロピー)")
print(f"    log2(4/3) = {log2_43:.6f} (位相的エントロピー)")
print(f"    log2(e)*2 = {log2_e_times_2:.6f} (幾何分布の微分エントロピー?)")
print(f"    2/ln(2) = {2/ln_2:.6f}")

if valid_ks:
    final_rate = results_mid[valid_ks[-1]]['H_per_k']
    final_h = results_mid[valid_ks[-1]]['h_k']

    print(f"\n  最終推定値:")
    print(f"    H(k)/k at k={valid_ks[-1]}: {final_rate:.8f}")
    print(f"    h(k) at k={valid_ks[-1]}:   {final_h:.8f}")

    gap = H_indep - final_rate
    print(f"\n  独立エントロピーからの乖離:")
    print(f"    H_indep - H(k)/k = {gap:.8f}")
    print(f"    相対乖離: {gap/H_indep * 100:.4f}%")

    # 乖離がlog2(4/3)に関係するか?
    print(f"\n  乖離と log2(4/3) の比較:")
    print(f"    gap = {gap:.8f}")
    print(f"    log2(4/3) = {log2_43:.8f}")
    print(f"    gap / log2(4/3) = {gap/log2_43:.8f}")

    # 他の可能な関係
    print(f"\n  乖離の可能な解釈:")
    print(f"    gap / H_indep = {gap/H_indep:.8f}")
    print(f"    gap * ln(2) = {gap * ln_2:.8f}")
    print(f"    2 - gap = {2 - gap:.8f}")
    print(f"    H_indep - log2(4/3) = {H_indep - log2_43:.8f}")


# Phase 5: 大規模データでの検証 (k=1..12)
print("\n\n--- Phase 5: 大規模データ (n=3..499999) での検証 ---")
t0_phase5 = time.time()
seq_large, count_large = aggregate_v2_data(3, 499999, step=2, max_len=500)
print(f"大規模データ集約完了: {len(seq_large)} symbols from {count_large} odd numbers ({time.time()-t0_phase5:.1f}s)")

max_k_large = 15
results_large = {}
print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} {'#distinct':>10}")
print("-" * 75)

prev_H = 0.0
for k in range(1, max_k_large + 1):
    t1 = time.time()
    result = compute_block_entropy(seq_large, k)
    if result is None:
        break
    H_k, n_distinct, n_total = result
    H_per_k = H_k / k
    h_k = H_k - prev_H
    gap = 2.0 - H_per_k

    results_large[k] = {
        'H_k': H_k,
        'H_per_k': H_per_k,
        'h_k': h_k,
        'gap': gap,
        'n_distinct': n_distinct,
        'n_total': n_total,
    }

    print(f"  {k:3d} {H_k:14.6f} {H_per_k:12.6f} {h_k:12.6f} {gap:10.6f} {n_distinct:10d}")
    prev_H = H_k

    if time.time() - t0_phase5 > 300:
        print(f"    TIME LIMIT at k={k}")
        break


# Phase 6: 安定性チェック - 異なるデータ範囲で比較
print("\n\n--- Phase 6: 安定性チェック (異なるデータ範囲) ---")

ranges_to_test = [
    (3, 9999),
    (10001, 49999),
    (50001, 99999),
    (100001, 199999),
    (200001, 499999),
]

print(f"\n{'range':>20} {'H(1)/1':>10} {'H(5)/5':>10} {'H(10)/10':>10} {'h(5)':>10} {'h(10)':>10}")
print("-" * 80)

for n_start, n_end in ranges_to_test:
    t1 = time.time()
    seq_r, cnt_r = aggregate_v2_data(n_start, n_end, step=2, max_len=500)
    if len(seq_r) < 10000:
        continue

    H1_r = compute_block_entropy(seq_r, 1)[0]
    H5_r = compute_block_entropy(seq_r, 5)[0]

    # k=10はデータ量次第
    H10_result = compute_block_entropy(seq_r, 10)
    H10_r = H10_result[0] if H10_result else float('nan')

    H4_r = compute_block_entropy(seq_r, 4)[0]
    H9_r = compute_block_entropy(seq_r, 9)[0] if compute_block_entropy(seq_r, 9) else float('nan')

    h5 = H5_r - H4_r
    h10 = H10_r - H9_r if not math.isnan(H10_r) and not math.isnan(H9_r) else float('nan')

    print(f"  {n_start:>7d}-{n_end:<7d} {H1_r/1:10.6f} {H5_r/5:10.6f} "
          f"{H10_r/10:10.6f} {h5:10.6f} {h10:10.6f}")

    if time.time() - t0 > 600:
        print("    TOTAL TIME LIMIT")
        break


# Phase 7: 1次/2次マルコフ推定によるエントロピー率
print("\n\n--- Phase 7: マルコフモデルによるエントロピー率推定 ---")

# 1次マルコフ: 遷移行列から定常分布とエントロピー率を計算
transition_counts = defaultdict(lambda: defaultdict(int))
for i in range(len(seq_large) - 1):
    transition_counts[seq_large[i]][seq_large[i+1]] += 1

# 遷移確率行列
states = sorted(set(seq_large))
max_state = min(max(states), 12)  # 12までに制限
states_limited = [s for s in states if s <= max_state]

print(f"\n  1次マルコフモデル:")
print(f"  状態数: {len(states_limited)}")

# 定常分布（marginal frequencyで近似）
marginal = Counter(seq_large)
total_symbols = len(seq_large)
pi = {s: marginal[s]/total_symbols for s in states_limited}

# 条件付きエントロピー H(X_{n+1} | X_n) = sum_i pi(i) * H(X_{n+1} | X_n = i)
h_markov1 = 0.0
for s in states_limited:
    total_from_s = sum(transition_counts[s].values())
    if total_from_s == 0:
        continue
    H_cond = 0.0
    for s2 in states_limited:
        if transition_counts[s][s2] > 0:
            p = transition_counts[s][s2] / total_from_s
            H_cond -= p * math.log2(p)
    h_markov1 += pi[s] * H_cond

print(f"  1次マルコフ エントロピー率: {h_markov1:.8f}")
print(f"  独立との差: {2.0 - h_markov1:.8f}")

# 2次マルコフ: (X_n, X_{n+1}) -> X_{n+2}
transition2_counts = defaultdict(lambda: defaultdict(int))
for i in range(len(seq_large) - 2):
    pair = (seq_large[i], seq_large[i+1])
    transition2_counts[pair][seq_large[i+2]] += 1

pair_counts = Counter()
for i in range(len(seq_large) - 1):
    pair_counts[(seq_large[i], seq_large[i+1])] += 1
total_pairs = sum(pair_counts.values())

h_markov2 = 0.0
for pair, total_from_pair in pair_counts.items():
    if pair[0] > max_state or pair[1] > max_state:
        continue
    pi_pair = total_from_pair / total_pairs
    H_cond = 0.0
    for s2, cnt in transition2_counts[pair].items():
        p = cnt / total_from_pair
        H_cond -= p * math.log2(p)
    h_markov2 += pi_pair * H_cond

print(f"  2次マルコフ エントロピー率: {h_markov2:.8f}")
print(f"  独立との差: {2.0 - h_markov2:.8f}")
print(f"  1次 vs 2次の差: {h_markov1 - h_markov2:.8f}")


# Phase 8: 最終まとめ
print("\n\n" + "=" * 80)
print("最終まとめ")
print("=" * 80)

print(f"\n  データ規模:")
print(f"    中規模: {len(seq_mid)} symbols ({count_mid} odd numbers, n=3..99999)")
print(f"    大規模: {len(seq_large)} symbols ({count_large} odd numbers, n=3..499999)")

print(f"\n  ブロックエントロピー率 H(k)/k の収束:")
for k in [1, 2, 5, 10, 15]:
    if k in results_mid:
        val_mid = results_mid[k]['H_per_k']
        val_large = results_large.get(k, {}).get('H_per_k', float('nan'))
        print(f"    k={k:2d}: mid={val_mid:.8f}, large={val_large:.8f}")

print(f"\n  条件付きエントロピー h(k) = H(k) - H(k-1) の収束:")
for k in [1, 2, 5, 10, 15]:
    if k in results_mid:
        val_mid = results_mid[k]['h_k']
        val_large = results_large.get(k, {}).get('h_k', float('nan'))
        print(f"    k={k:2d}: mid={val_mid:.8f}, large={val_large:.8f}")

print(f"\n  マルコフモデル推定:")
print(f"    0次(独立): {2.0:.8f}")
print(f"    1次マルコフ: {h_markov1:.8f}")
print(f"    2次マルコフ: {h_markov2:.8f}")

# エントロピー率の最良推定
best_estimates = []
if valid_ks:
    best_estimates.append(("H(k_max)/k_max", results_mid[valid_ks[-1]]['H_per_k']))
    best_estimates.append(("h(k_max)", results_mid[valid_ks[-1]]['h_k']))
best_estimates.append(("1st Markov", h_markov1))
best_estimates.append(("2nd Markov", h_markov2))

print(f"\n  エントロピー率の最良推定:")
for name, val in best_estimates:
    print(f"    {name:20s}: {val:.8f}  (gap from 2.0: {2.0 - val:.8f})")

# JSON output
output = {
    "title": "v2列ブロックエントロピー率の収束解析",
    "data": {
        "mid_range": {"n_start": 3, "n_end": 99999, "n_symbols": len(seq_mid), "n_orbits": count_mid},
        "large_range": {"n_start": 3, "n_end": 499999, "n_symbols": len(seq_large), "n_orbits": count_large},
    },
    "block_entropy_mid": {str(k): {
        "H_k": results_mid[k]['H_k'],
        "H_per_k": results_mid[k]['H_per_k'],
        "h_k": results_mid[k]['h_k'],
        "gap": results_mid[k]['gap_from_independent'],
        "n_distinct": results_mid[k]['n_distinct'],
    } for k in sorted(results_mid.keys())},
    "block_entropy_large": {str(k): {
        "H_k": results_large[k]['H_k'],
        "H_per_k": results_large[k]['H_per_k'],
        "h_k": results_large[k]['h_k'],
        "gap": results_large[k]['gap'],
    } for k in sorted(results_large.keys())},
    "markov_estimates": {
        "order_0_independent": 2.0,
        "order_1": h_markov1,
        "order_2": h_markov2,
    },
    "theoretical_constants": {
        "H_independent": 2.0,
        "log2_4_over_3": log2_43,
        "log2_e_times_2": log2_e_times_2,
    },
}

with open("/Users/soyukke/study/lean-unsolved/results/v2_entropy_rate_convergence.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n結果を results/v2_entropy_rate_convergence.json に保存しました")
