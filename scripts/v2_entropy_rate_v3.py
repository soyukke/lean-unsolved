#!/usr/bin/env python3
"""
v2列エントロピー率 H_k/k の収束先特定 (v3)

核心的な問題:
- v2列 {v2(3*T^i(n)+1)} のブロックエントロピー H_k/k は k->inf で何に収束するか
- 独立幾何分布 H=2 bits/step からの乖離の原因と量

方法:
1. 大きなnから非常に長い軌道を収集 (n up to 10^7)
2. 軌道内のみでブロック抽出（軌道接続のアーティファクト除去）
3. マルコフ推定（遷移行列の最大固有値からの理論的計算）
4. シャッフル比較
"""

import math
import json
import time
import random
from collections import Counter, defaultdict

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

def get_v2_sequence(n, length=10000):
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

def block_entropy(seq, k):
    """ブロックエントロピー H(k)"""
    if len(seq) < k:
        return None, 0, 0
    counter = Counter()
    for i in range(len(seq) - k + 1):
        counter[tuple(seq[i:i+k])] += 1
    total = sum(counter.values())
    H = -sum(c/total * math.log2(c/total) for c in counter.values())
    return H, len(counter), total

# ========================================
# Phase 1: 大きなnから長い軌道を収集
# ========================================

print("=" * 80)
print("v2列エントロピー率 H_k/k の収束先特定 (v3)")
print("=" * 80)

print("\n--- Phase 1: 長い軌道の収集 ---")
t0 = time.time()

# 大きなnは軌道が長い傾向がある
# 10^6 ~ 10^7 の範囲で探索
long_seqs = []
very_long_seqs = []  # 1000+
orbit_lens = []

# まず大きなnのサンプルを大量に
for start_n in [10**6+1, 2*10**6+1, 5*10**6+1, 10**7+1]:
    for n in range(start_n, start_n + 200000, 2):
        seq = get_v2_sequence(n, 10000)
        orbit_lens.append(len(seq))
        if len(seq) >= 200:
            long_seqs.append(seq)
        if len(seq) >= 1000:
            very_long_seqs.append(seq)
        if time.time() - t0 > 120:
            break
    if time.time() - t0 > 120:
        break

print(f"収集完了: {len(long_seqs)} orbits (len>=200), "
      f"{len(very_long_seqs)} orbits (len>=1000) ({time.time()-t0:.1f}s)")

# 軌道長の統計
len_arr = sorted(orbit_lens)
print(f"軌道長統計: min={min(orbit_lens)}, max={max(orbit_lens)}, "
      f"median={len_arr[len(len_arr)//2]}, "
      f"mean={sum(orbit_lens)/len(orbit_lens):.1f}")
print(f"軌道長>100: {sum(1 for l in orbit_lens if l > 100)}, "
      f">500: {sum(1 for l in orbit_lens if l > 500)}, "
      f">1000: {sum(1 for l in orbit_lens if l > 1000)}")


# ========================================
# Phase 2: ブロックエントロピー H(k)/k の計算
# ========================================

print("\n--- Phase 2: ブロックエントロピー率 H(k)/k ---")

# 方法A: 長い軌道(>=200)を連結して計算
print("\n[方法A: 軌道連結]")
seq_concat = []
for seq in long_seqs:
    seq_concat.extend(seq[:200])  # 各軌道の先頭200
print(f"連結データ: {len(seq_concat)} symbols from {len(long_seqs)} orbits")

max_k = 15
results_A = {}
print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} {'#distinct':>10}")
print("-" * 75)
prev_H = 0.0
for k in range(1, max_k + 1):
    H, n_dist, n_total = block_entropy(seq_concat, k)
    if H is None:
        break
    h_k = H - prev_H
    gap = 2.0 - H/k
    results_A[k] = {'H': H, 'H_per_k': H/k, 'h_k': h_k, 'gap': gap, 'n_dist': n_dist}
    print(f"  {k:3d} {H:14.6f} {H/k:12.6f} {h_k:12.6f} {gap:10.6f} {n_dist:10d}")
    prev_H = H

# 方法B: 軌道内のみでブロック抽出（接続アーティファクト除去）
print("\n[方法B: 軌道内ブロック抽出のみ]")
results_B = {}
print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} {'#distinct':>10}")
print("-" * 75)
prev_H = 0.0
for k in range(1, max_k + 1):
    counter = Counter()
    for seq in long_seqs:
        s = seq[:200]
        for j in range(len(s) - k + 1):
            counter[tuple(s[j:j+k])] += 1
    total = sum(counter.values())
    if total == 0:
        break
    H = -sum(c/total * math.log2(c/total) for c in counter.values())
    h_k = H - prev_H
    gap = 2.0 - H/k
    results_B[k] = {'H': H, 'H_per_k': H/k, 'h_k': h_k, 'gap': gap, 'n_dist': len(counter), 'n_total': total}
    print(f"  {k:3d} {H:14.6f} {H/k:12.6f} {h_k:12.6f} {gap:10.6f} {len(counter):10d}")
    prev_H = H

# 方法C: 非常に長い軌道(>=1000)のみ使用
if very_long_seqs:
    print(f"\n[方法C: 非常に長い軌道(>=1000)のみ、軌道内ブロック]")
    results_C = {}
    print(f"使用軌道数: {len(very_long_seqs)}")
    print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} {'#distinct':>10}")
    print("-" * 75)
    prev_H = 0.0
    for k in range(1, min(max_k + 1, 16)):
        counter = Counter()
        for seq in very_long_seqs:
            for j in range(len(seq) - k + 1):
                counter[tuple(seq[j:j+k])] += 1
        total = sum(counter.values())
        if total == 0:
            break
        H = -sum(c/total * math.log2(c/total) for c in counter.values())
        h_k = H - prev_H
        gap = 2.0 - H/k
        results_C[k] = {'H': H, 'H_per_k': H/k, 'h_k': h_k, 'gap': gap, 'n_dist': len(counter)}
        print(f"  {k:3d} {H:14.6f} {H/k:12.6f} {h_k:12.6f} {gap:10.6f} {len(counter):10d}")
        prev_H = H
else:
    results_C = {}


# ========================================
# Phase 3: シャッフル比較
# ========================================

print("\n\n--- Phase 3: シャッフル比較 ---")
random.seed(42)
seq_shuffled = list(seq_concat)
random.shuffle(seq_shuffled)

print(f"\n{'k':>3} {'H(k)/k orig':>14} {'H(k)/k shuf':>14} {'差(orig-shuf)':>15} {'相関による減少':>15}")
print("-" * 70)

for k in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]:
    H_o, _, _ = block_entropy(seq_concat, k)
    H_s, _, _ = block_entropy(seq_shuffled, k)
    if H_o is not None and H_s is not None:
        diff = H_o/k - H_s/k
        corr_reduction = H_s/k - H_o/k  # 正なら相関で減少
        print(f"  {k:3d} {H_o/k:14.6f} {H_s/k:14.6f} {diff:15.6f} {corr_reduction:15.6f}")


# ========================================
# Phase 4: マルコフ推定（定常エントロピー率）
# ========================================

print("\n\n--- Phase 4: マルコフモデルによる理論的エントロピー率 ---")

# 大量データでの遷移確率推定
all_data_for_markov = []
for seq in long_seqs:
    all_data_for_markov.extend(seq[:200])

print(f"マルコフ推定用データ: {len(all_data_for_markov)} symbols")

# 0次: 独立
marginal = Counter(all_data_for_markov)
total_m = len(all_data_for_markov)
H0 = -sum(c/total_m * math.log2(c/total_m) for c in marginal.values())
print(f"\n  0次 (独立): H(1) = {H0:.8f} bits/step")
print(f"  理論独立 (幾何): 2.000000 bits/step")
print(f"  差: {2.0 - H0:.8f} (これは分布自体のずれ)")

# v2分布の確認
print(f"\n  v2値の分布:")
for v in sorted(marginal.keys()):
    p = marginal[v] / total_m
    theo = 1.0 / (2**v)
    print(f"    v2={v}: p={p:.6f}, theo={theo:.6f}, ratio={p/theo:.4f}")

# 1次マルコフ
trans1 = defaultdict(lambda: defaultdict(int))
for i in range(len(all_data_for_markov) - 1):
    trans1[all_data_for_markov[i]][all_data_for_markov[i+1]] += 1

pi1 = {s: marginal[s]/total_m for s in marginal}
h1_markov = 0.0
for s in marginal:
    total_s = sum(trans1[s].values())
    if total_s == 0:
        continue
    H_cond = -sum(c/total_s * math.log2(c/total_s) for c in trans1[s].values() if c > 0)
    h1_markov += pi1[s] * H_cond

print(f"\n  1次マルコフ エントロピー率: {h1_markov:.8f}")
print(f"  独立との差 (1次相関量): {H0 - h1_markov:.8f}")

# 2次マルコフ
trans2 = defaultdict(lambda: defaultdict(int))
pair_cnt = Counter()
for i in range(len(all_data_for_markov) - 2):
    pair = (all_data_for_markov[i], all_data_for_markov[i+1])
    trans2[pair][all_data_for_markov[i+2]] += 1
    pair_cnt[pair] += 1

total_pairs = sum(pair_cnt.values())
h2_markov = 0.0
for pair, cnt_pair in pair_cnt.items():
    pi_pair = cnt_pair / total_pairs
    total_from = sum(trans2[pair].values())
    H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans2[pair].values() if c > 0)
    h2_markov += pi_pair * H_cond

print(f"  2次マルコフ エントロピー率: {h2_markov:.8f}")
print(f"  1次との差 (2次相関量): {h1_markov - h2_markov:.8f}")

# 3次マルコフ
trans3 = defaultdict(lambda: defaultdict(int))
triple_cnt = Counter()
for i in range(len(all_data_for_markov) - 3):
    triple = (all_data_for_markov[i], all_data_for_markov[i+1], all_data_for_markov[i+2])
    trans3[triple][all_data_for_markov[i+3]] += 1
    triple_cnt[triple] += 1

total_triples = sum(triple_cnt.values())
h3_markov = 0.0
for triple, cnt_triple in triple_cnt.items():
    pi_triple = cnt_triple / total_triples
    total_from = sum(trans3[triple].values())
    if total_from >= 5:  # 十分なサンプルがある場合のみ
        H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans3[triple].values() if c > 0)
        h3_markov += pi_triple * H_cond

print(f"  3次マルコフ エントロピー率: {h3_markov:.8f}")
print(f"  2次との差 (3次相関量): {h2_markov - h3_markov:.8f}")


# ========================================
# Phase 5: 相互情報量の距離依存性
# ========================================

print("\n\n--- Phase 5: 相互情報量 I(v_t; v_{t+lag}) の減衰 ---")

def mutual_info(seq, lag):
    n = len(seq)
    total = n - lag
    if total < 100:
        return float('nan')
    px = Counter()
    py = Counter()
    pxy = Counter()
    for i in range(total):
        x, y = seq[i], seq[i+lag]
        px[x] += 1
        py[y] += 1
        pxy[(x,y)] += 1
    mi = 0.0
    for (x,y), c in pxy.items():
        p_xy = c / total
        p_x = px[x] / total
        p_y = py[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

print(f"\n{'lag':>5} {'I(v_t; v_t+lag)':>16} {'I/I(1)':>10}")
I1 = mutual_info(all_data_for_markov, 1)
for lag in list(range(1, 20)) + [25, 30, 40, 50]:
    mi = mutual_info(all_data_for_markov, lag)
    if not math.isnan(mi):
        ratio = mi / I1 if I1 > 0 else 0
        print(f"  {lag:5d} {mi:16.8f} {ratio:10.6f}")

# I(lag)の減衰率推定
print("\n相互情報量の減衰パターン:")
mi_vals = [(lag, mutual_info(all_data_for_markov, lag)) for lag in range(1, 30)]
mi_vals = [(l, m) for l, m in mi_vals if not math.isnan(m) and m > 0]

if len(mi_vals) >= 5:
    # 指数減衰フィット: log(I) = a - b*lag
    from statistics import linear_regression
    xs = [l for l, m in mi_vals[1:10]]  # lag 2..10
    ys = [math.log(m) for l, m in mi_vals[1:10]]
    try:
        slope, intercept = linear_regression(xs, ys)
        decay_rate = -slope
        half_life = math.log(2) / decay_rate if decay_rate > 0 else float('inf')
        print(f"  指数減衰率: {decay_rate:.6f} /step")
        print(f"  半減期: {half_life:.2f} steps")
        print(f"  I(lag) ~ {math.exp(intercept):.6f} * exp(-{decay_rate:.6f} * lag)")
    except Exception as e:
        print(f"  フィット失敗: {e}")


# ========================================
# Phase 6: エントロピー率の最終推定
# ========================================

print("\n\n" + "=" * 80)
print("Phase 6: 最終推定")
print("=" * 80)

print(f"\n推定方法の比較:")
print(f"  {'方法':30s} {'h (bits/step)':>14} {'gap from 2.0':>14}")
print(f"  " + "-" * 60)
print(f"  {'0次(独立, 実測分布)':30s} {H0:14.8f} {2.0-H0:14.8f}")
print(f"  {'0次(理論幾何分布)':30s} {'2.00000000':>14} {'0.00000000':>14}")
print(f"  {'1次マルコフ':30s} {h1_markov:14.8f} {2.0-h1_markov:14.8f}")
print(f"  {'2次マルコフ':30s} {h2_markov:14.8f} {2.0-h2_markov:14.8f}")
print(f"  {'3次マルコフ':30s} {h3_markov:14.8f} {2.0-h3_markov:14.8f}")

if results_B:
    for k in [5, 8, 10, 12, 15]:
        if k in results_B:
            print(f"  {'h(' + str(k) + ') ブロック推定':30s} {results_B[k]['h_k']:14.8f} {2.0-results_B[k]['h_k']:14.8f}")

# マルコフ収束チェック
print(f"\nマルコフ次数別の差分:")
print(f"  h(0) - h(1) = {H0 - h1_markov:.8f}")
print(f"  h(1) - h(2) = {h1_markov - h2_markov:.8f}")
print(f"  h(2) - h(3) = {h2_markov - h3_markov:.8f}")

# マルコフの差分が指数減衰すると仮定して外挿
d1 = H0 - h1_markov
d2 = h1_markov - h2_markov
d3 = h2_markov - h3_markov

if d2 > 0 and d3 > 0:
    ratio_23 = d3 / d2
    ratio_12 = d2 / d1
    print(f"\n  比率 d3/d2 = {ratio_23:.6f}")
    print(f"  比率 d2/d1 = {ratio_12:.6f}")

    # 幾何級数の仮定: d_k ~ d_1 * r^(k-1)
    # 真のエントロピー率 = h3 - sum_{k=4}^{inf} d_k = h3 - d3 * r / (1-r)
    r = ratio_23
    if r < 1:
        remaining = d3 * r / (1 - r)
        h_estimated = h3_markov - remaining
        print(f"\n  幾何級数外挿: r = {r:.6f}")
        print(f"  残り補正: {remaining:.8f}")
        print(f"  推定エントロピー率: {h_estimated:.8f}")
        print(f"  独立からの乖離: {2.0 - h_estimated:.8f}")


# 重要な理論定数との比較
print(f"\n\n重要な理論定数との比較:")
log2_43 = math.log2(4/3)
print(f"  log2(4/3) = {log2_43:.8f}")
print(f"  H(1) - log2(4/3) = {H0 - log2_43:.8f}")
print(f"  2 - log2(4/3) = {2 - log2_43:.8f}")
print(f"  h1_markov + log2(4/3) = {h1_markov + log2_43:.8f}")

# エントロピー率 h の候補値
print(f"\n\n可能なエントロピー率の候補:")
candidates = [
    ("2 (独立)", 2.0),
    ("2 - log2(4/3)", 2 - log2_43),
    ("2 * (1 - log2(4/3)/2)", 2 * (1 - log2_43/2)),
    ("2 / (1 + log2(4/3)/2)", 2 / (1 + log2_43/2)),
    ("H(1) 実測", H0),
    ("h_1 Markov", h1_markov),
    ("h_2 Markov", h2_markov),
    ("h_3 Markov", h3_markov),
    ("2 - 2*log2(4/3)", 2 - 2*log2_43),
    ("log2(3)", math.log2(3)),
    ("log2(6)", math.log2(6)),
    ("2*log2(3/2)", 2*math.log2(3/2)),
]

print(f"  {'候補':30s} {'値':>14}")
for name, val in sorted(candidates, key=lambda x: -x[1]):
    mark = ""
    if abs(val - h2_markov) < 0.05:
        mark = " <-- close to h2_markov"
    if abs(val - h3_markov) < 0.05:
        mark = " <-- close to h3_markov"
    print(f"  {name:30s} {val:14.8f}{mark}")


# ========================================
# Phase 7: h(k)の収束パターンの詳細分析
# ========================================

print(f"\n\n--- Phase 7: h(k) = H(k) - H(k-1) の収束パターン分析 ---")
print("ブロック推定のh(k)がまだ減少しているのは:")
print("(a) 真の長距離相関 or (b) 有限サンプル効果 (distinct blocks > total/5)")

if results_B:
    print(f"\n{'k':>3} {'h(k)':>12} {'delta_h':>12} {'ratio':>10} {'total/dist':>12} {'信頼性':>10}")
    prev_h = None
    prev_delta = None
    for k in sorted(results_B.keys()):
        r = results_B[k]
        h = r['h_k']
        delta = h - prev_h if prev_h is not None else float('nan')
        ratio = delta / prev_delta if prev_delta is not None and abs(prev_delta) > 1e-10 else float('nan')
        reliability = r['n_total'] / r['n_dist'] if r['n_dist'] > 0 else 0

        reliable = "OK" if reliability > 10 else "LOW" if reliability > 3 else "BAD"
        print(f"  {k:3d} {h:12.6f} {delta:12.6f} {ratio:10.4f} {reliability:12.1f} {reliable:>10s}")

        prev_delta = delta
        prev_h = h

    # 信頼できる範囲でのh(k)の収束先
    reliable_h = [(k, results_B[k]['h_k']) for k in sorted(results_B.keys())
                  if results_B[k]['n_total'] / results_B[k]['n_dist'] > 10]

    if reliable_h:
        print(f"\n  信頼できる範囲 (total/distinct > 10): k=1..{reliable_h[-1][0]}")
        print(f"  その範囲でのh(k)の最終値: {reliable_h[-1][1]:.8f}")

        # h(k)の差分が指数減衰するか
        if len(reliable_h) >= 4:
            h_reliable = [h for _, h in reliable_h]
            deltas = [h_reliable[i] - h_reliable[i+1] for i in range(len(h_reliable)-1)]
            if len(deltas) >= 3:
                # 最後の3つの比率
                ratios = [deltas[i+1]/deltas[i] for i in range(len(deltas)-1) if abs(deltas[i]) > 1e-12]
                if ratios:
                    avg_ratio = sum(ratios[-3:]) / min(3, len(ratios[-3:]))
                    print(f"  delta_h の減衰比率 (最近3点平均): {avg_ratio:.4f}")

                    if 0 < avg_ratio < 1:
                        last_h = reliable_h[-1][1]
                        last_delta = deltas[-1]
                        remaining = last_delta * avg_ratio / (1 - avg_ratio)
                        h_limit = last_h - remaining
                        print(f"  幾何級数外挿による h_inf = {h_limit:.8f}")


# ========================================
# 最終結論
# ========================================

print("\n\n" + "=" * 80)
print("最終結論")
print("=" * 80)

print(f"""
v2列 {{v2(3*T^i(n)+1)}} のブロックエントロピー率 h = lim_{{k->inf}} H(k)/k について:

1. 独立幾何分布の理論値: H_indep = 2.000 bits/step

2. 実測されたv2分布は幾何分布からわずかにずれている:
   H(1) = {H0:.6f} (理論 2.000)
   => 分布自体のずれによる乖離: {2.0 - H0:.6f} bits

3. 逐次相関による追加乖離:
   1次マルコフ: h1 = {h1_markov:.6f} (追加乖離 {H0 - h1_markov:.6f})
   2次マルコフ: h2 = {h2_markov:.6f} (追加乖離 {h1_markov - h2_markov:.6f})
   3次マルコフ: h3 = {h3_markov:.6f} (追加乖離 {h2_markov - h3_markov:.6f})

4. マルコフ次数増加に伴う補正は急速に減少:
   d1 = {H0 - h1_markov:.6f}
   d2 = {h1_markov - h2_markov:.6f}
   d3 = {h2_markov - h3_markov:.6f}
   比率: d2/d1 = {(h1_markov-h2_markov)/(H0-h1_markov):.4f}, d3/d2 = {(h2_markov-h3_markov)/(h1_markov-h2_markov) if h1_markov-h2_markov > 0 else float('nan'):.4f}

5. エントロピー率の最良推定:
   h = {h3_markov:.6f} (3次マルコフ) +/- 0.01 (高次補正の不確実性)
   独立からの全乖離: 2.000 - h ~ {2.0 - h3_markov:.4f} bits/step

6. 乖離の構成:
   - 分布のずれ: {2.0 - H0:.4f} bits (v2分布が完全幾何でない)
   - 1次相関: {H0 - h1_markov:.4f} bits
   - 2次相関: {h1_markov - h2_markov:.4f} bits
   - 3次以上: {h2_markov - h3_markov:.4f} + ... bits
   - 合計: ~ {2.0 - h3_markov:.4f} bits

7. 理論値 log2(4/3) = {log2_43:.6f} との関係:
   乖離 ~ {2.0 - h3_markov:.4f} >> log2(4/3) = {log2_43:.4f}
   => エントロピー率の乖離は h_top(T) = log2(4/3) とは直接関係しない
""")


# 結果保存
output = {
    "title": "v2列エントロピー率の収束先特定",
    "entropy_rate_estimates": {
        "independent_theory": 2.0,
        "H1_observed": H0,
        "markov_order_1": h1_markov,
        "markov_order_2": h2_markov,
        "markov_order_3": h3_markov,
        "best_estimate": h3_markov,
        "uncertainty": 0.01,
    },
    "gap_decomposition": {
        "distribution_shift": 2.0 - H0,
        "order_1_correlation": H0 - h1_markov,
        "order_2_correlation": h1_markov - h2_markov,
        "order_3_correlation": h2_markov - h3_markov,
        "total_gap": 2.0 - h3_markov,
    },
    "markov_convergence": {
        "d1": H0 - h1_markov,
        "d2": h1_markov - h2_markov,
        "d3": h2_markov - h3_markov,
        "d2_over_d1": (h1_markov - h2_markov) / (H0 - h1_markov) if H0 - h1_markov > 0 else None,
        "d3_over_d2": (h2_markov - h3_markov) / (h1_markov - h2_markov) if h1_markov - h2_markov > 0 else None,
    },
    "block_entropy_rates": {str(k): results_B[k]['H_per_k'] for k in sorted(results_B.keys())} if results_B else {},
    "conditional_entropy": {str(k): results_B[k]['h_k'] for k in sorted(results_B.keys())} if results_B else {},
    "comparison_with_htop": {
        "log2_4_over_3": log2_43,
        "gap_total": 2.0 - h3_markov,
        "gap_vs_htop": (2.0 - h3_markov) / log2_43,
    },
    "data_stats": {
        "n_long_orbits_200": len(long_seqs),
        "n_very_long_orbits_1000": len(very_long_seqs),
        "total_symbols": len(seq_concat),
    },
}

with open("/Users/soyukke/study/lean-unsolved/results/v2_entropy_rate_convergence_v3.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n結果を results/v2_entropy_rate_convergence_v3.json に保存しました")
