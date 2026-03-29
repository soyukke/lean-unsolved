#!/usr/bin/env python3
"""
v2列エントロピー率の最終解析

方針の整理:
- 軌道長は n の大きさに依存する。n~10^6 では平均軌道長 ~50 steps
- 長い軌道を得るには中程度のn (数千~数万)が有利
- ブロックエントロピー H(k)/k の信頼性には total/distinct >> 1 が必要
- k が大きいと必要なデータ量が指数的に増える

戦略:
1. 大量の軌道を集約（n=3..200000の全奇数）
2. 軌道接続をまたがないブロック抽出
3. k=1..12 程度で確実な計算
4. マルコフ推定で外挿
"""

import math
import json
import time
import random
from collections import Counter, defaultdict

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def get_v2_sequence(n, length=5000):
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

print("=" * 80)
print("v2列エントロピー率の最終解析")
print("=" * 80)

# ========================================
# データ収集
# ========================================

print("\n--- データ収集 ---")
t0 = time.time()

all_orbits = []  # (n, seq) のリスト
orbit_lengths = []

for n in range(3, 500001, 2):
    seq = get_v2_sequence(n, 5000)
    if len(seq) >= 20:
        all_orbits.append(seq)
        orbit_lengths.append(len(seq))

print(f"収集完了: {len(all_orbits)} orbits ({time.time()-t0:.1f}s)")
print(f"軌道長統計: min={min(orbit_lengths)}, max={max(orbit_lengths)}, "
      f"mean={sum(orbit_lengths)/len(orbit_lengths):.1f}, "
      f"median={sorted(orbit_lengths)[len(orbit_lengths)//2]}")

# 軌道長分布
for thresh in [20, 50, 100, 200, 500]:
    cnt = sum(1 for l in orbit_lengths if l >= thresh)
    print(f"  長さ>={thresh}: {cnt}")

total_symbols = sum(len(s) for s in all_orbits)
print(f"総シンボル数: {total_symbols}")


# ========================================
# Part 1: 軌道内ブロック抽出によるエントロピー (正確な方法)
# ========================================

print("\n\n--- Part 1: 軌道内ブロック抽出 (接続アーティファクトなし) ---")

def compute_entropy_within_orbits(orbits, k, max_orbit_prefix=None):
    """各軌道内でのみk-ブロックを抽出してエントロピーを計算"""
    counter = Counter()
    for seq in orbits:
        s = seq[:max_orbit_prefix] if max_orbit_prefix else seq
        for j in range(len(s) - k + 1):
            counter[tuple(s[j:j+k])] += 1
    total = sum(counter.values())
    if total == 0:
        return None, 0, 0
    H = -sum(c/total * math.log2(c/total) for c in counter.values())
    return H, len(counter), total

# 全軌道を使用
print(f"\n[全軌道使用 ({len(all_orbits)} orbits)]")
print(f"\n{'k':>3} {'H(k)':>14} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} "
      f"{'#distinct':>10} {'#total':>10} {'t/d ratio':>10}")
print("-" * 95)

prev_H = 0.0
results_all = {}
for k in range(1, 16):
    t1 = time.time()
    H, n_dist, n_total = compute_entropy_within_orbits(all_orbits, k)
    if H is None:
        break
    h_k = H - prev_H
    gap = 2.0 - H/k
    td_ratio = n_total / n_dist if n_dist > 0 else 0
    results_all[k] = {
        'H': H, 'H_per_k': H/k, 'h_k': h_k, 'gap': gap,
        'n_dist': n_dist, 'n_total': n_total, 'td_ratio': td_ratio
    }
    reliable = "OK" if td_ratio > 20 else "ok" if td_ratio > 5 else "LOW"
    print(f"  {k:3d} {H:14.6f} {H/k:12.6f} {h_k:12.6f} {gap:10.6f} "
          f"{n_dist:10d} {n_total:10d} {td_ratio:10.1f} {reliable}")
    prev_H = H

# 軌道長フィルタ: 長い軌道のみ
for min_len in [50, 100]:
    filtered = [s for s in all_orbits if len(s) >= min_len]
    if len(filtered) < 100:
        continue
    print(f"\n[軌道長>={min_len}のみ ({len(filtered)} orbits)]")
    print(f"  {'k':>3} {'H(k)/k':>12} {'h(k)':>12} {'gap':>10} {'t/d':>8}")
    print("  " + "-" * 50)
    prev_H = 0.0
    for k in range(1, min(16, min_len//3)):
        H, n_dist, n_total = compute_entropy_within_orbits(filtered, k, max_orbit_prefix=min_len)
        if H is None:
            break
        h_k = H - prev_H
        gap = 2.0 - H/k
        td = n_total / n_dist if n_dist > 0 else 0
        print(f"  {k:3d} {H/k:12.6f} {h_k:12.6f} {gap:10.6f} {td:8.1f}")
        prev_H = H


# ========================================
# Part 2: マルコフ推定 (大規模データ)
# ========================================

print("\n\n--- Part 2: マルコフ推定 (大規模データ) ---")

# 全データを連結（マルコフ推定のため）
# ただし軌道接続点は除外
all_pairs = []  # (v_i, v_{i+1}) within orbits
all_triples = []  # (v_i, v_{i+1}, v_{i+2}) within orbits
all_quads = []

for seq in all_orbits:
    for j in range(len(seq) - 1):
        all_pairs.append((seq[j], seq[j+1]))
    for j in range(len(seq) - 2):
        all_triples.append((seq[j], seq[j+1], seq[j+2]))
    for j in range(len(seq) - 3):
        all_quads.append((seq[j], seq[j+1], seq[j+2], seq[j+3]))

# 0次: 辺際分布のエントロピー
all_v2_values = []
for seq in all_orbits:
    all_v2_values.extend(seq)

marginal = Counter(all_v2_values)
total_v2 = len(all_v2_values)
H0 = -sum(c/total_v2 * math.log2(c/total_v2) for c in marginal.values())

print(f"\n  0次 (辺際分布): H(1) = {H0:.8f}")
print(f"  理論 (幾何分布): H_indep = 2.000000")
print(f"  分布偏差: {2.0 - H0:.8f}")

# v2分布
print(f"\n  v2値分布:")
for v in sorted(marginal.keys())[:15]:
    p = marginal[v] / total_v2
    theo = 1.0 / (2**v)
    print(f"    v2={v:2d}: p={p:.6f}, theo(1/2^v)={theo:.6f}, ratio={p/theo:.4f}")

# 1次マルコフ
print(f"\n  1次マルコフ:")
trans1 = defaultdict(lambda: defaultdict(int))
for a, b in all_pairs:
    trans1[a][b] += 1

h1 = 0.0
for s, transitions in trans1.items():
    total_s = sum(transitions.values())
    pi_s = marginal[s] / total_v2
    H_cond = -sum(c/total_s * math.log2(c/total_s) for c in transitions.values() if c > 0)
    h1 += pi_s * H_cond

print(f"    エントロピー率: {h1:.8f}")
print(f"    1次相関量: {H0 - h1:.8f}")

# 遷移行列の表示 (上位状態のみ)
print("\n  遷移確率 P(v_t+1|v_t) [上位5状態]:")
print("    " + "v_t\\v_t+1".rjust(12), end="")
for j in range(1, 6):
    print(f"  v={j:d}  ", end="")
print(f"  {'total':>8}")
for i in range(1, 6):
    total_i = sum(trans1[i].values())
    print(f"    v={i:d}         ", end="")
    for j in range(1, 6):
        p = trans1[i][j] / total_i if total_i > 0 else 0
        print(f" {p:.4f}", end="")
    print(f"  {total_i:8d}")
print(f"    理論(独立):   ", end="")
for j in range(1, 6):
    print(f" {1/(2**j):.4f}", end="")
print()

# 2次マルコフ
print(f"\n  2次マルコフ:")
trans2 = defaultdict(lambda: defaultdict(int))
pair_cnt = Counter()
for a, b, c in all_triples:
    trans2[(a,b)][c] += 1
    pair_cnt[(a,b)] += 1

total_pairs_cnt = sum(pair_cnt.values())
h2 = 0.0
for pair, cnt in pair_cnt.items():
    pi_pair = cnt / total_pairs_cnt
    total_from = sum(trans2[pair].values())
    H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans2[pair].values() if c > 0)
    h2 += pi_pair * H_cond

print(f"    エントロピー率: {h2:.8f}")
print(f"    2次相関量: {h1 - h2:.8f}")

# 3次マルコフ
print(f"\n  3次マルコフ:")
trans3 = defaultdict(lambda: defaultdict(int))
triple_cnt = Counter()
for a, b, c, d in all_quads:
    trans3[(a,b,c)][d] += 1
    triple_cnt[(a,b,c)] += 1

total_triples_cnt = sum(triple_cnt.values())
h3 = 0.0
for triple, cnt in triple_cnt.items():
    pi_triple = cnt / total_triples_cnt
    total_from = sum(trans3[triple].values())
    if total_from >= 3:
        H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans3[triple].values() if c > 0)
        h3 += pi_triple * H_cond

print(f"    エントロピー率: {h3:.8f}")
print(f"    3次相関量: {h2 - h3:.8f}")

# 4次マルコフ
print(f"\n  4次マルコフ:")
trans4 = defaultdict(lambda: defaultdict(int))
quad_cnt = Counter()
for seq in all_orbits:
    for j in range(len(seq) - 4):
        q = tuple(seq[j:j+4])
        trans4[q][seq[j+4]] += 1
        quad_cnt[q] += 1

total_quads_cnt = sum(quad_cnt.values())
h4 = 0.0
for quad, cnt in quad_cnt.items():
    pi_quad = cnt / total_quads_cnt
    total_from = sum(trans4[quad].values())
    if total_from >= 3:
        H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans4[quad].values() if c > 0)
        h4 += pi_quad * H_cond

print(f"    エントロピー率: {h4:.8f}")
print(f"    4次相関量: {h3 - h4:.8f}")

# 5次マルコフ
print(f"\n  5次マルコフ:")
trans5 = defaultdict(lambda: defaultdict(int))
quint_cnt = Counter()
for seq in all_orbits:
    for j in range(len(seq) - 5):
        q = tuple(seq[j:j+5])
        trans5[q][seq[j+5]] += 1
        quint_cnt[q] += 1

total_quints_cnt = sum(quint_cnt.values())
h5 = 0.0
for quint, cnt in quint_cnt.items():
    pi_quint = cnt / total_quints_cnt
    total_from = sum(trans5[quint].values())
    if total_from >= 3:
        H_cond = -sum(c/total_from * math.log2(c/total_from) for c in trans5[quint].values() if c > 0)
        h5 += pi_quint * H_cond

print(f"    エントロピー率: {h5:.8f}")
print(f"    5次相関量: {h4 - h5:.8f}")


# ========================================
# Part 3: マルコフ推定の収束分析
# ========================================

print("\n\n--- Part 3: マルコフ推定の収束分析 ---")

h_markov = [H0, h1, h2, h3, h4, h5]
print(f"\n{'次数':>4} {'エントロピー率':>16} {'差分 d_k':>12} {'比率 d_k/d_{k-1}':>16}")
print("-" * 55)

for k in range(len(h_markov)):
    d = h_markov[k-1] - h_markov[k] if k > 0 else 0
    d_prev = h_markov[k-2] - h_markov[k-1] if k > 1 else 0
    ratio = d / d_prev if k > 1 and abs(d_prev) > 1e-12 else float('nan')
    print(f"  {k:4d} {h_markov[k]:16.8f} {d:12.8f} {ratio:16.6f}")

# 収束先の推定
d_vals = [h_markov[k-1] - h_markov[k] for k in range(1, len(h_markov))]
print(f"\n差分列: {[f'{d:.6f}' for d in d_vals]}")

# d_kが増加しているか減少しているか
if len(d_vals) >= 3:
    # d_k の比率がある値に収束していれば幾何級数外挿可能
    ratios = [d_vals[i+1]/d_vals[i] for i in range(len(d_vals)-1) if abs(d_vals[i]) > 1e-12]
    print(f"比率列: {[f'{r:.4f}' for r in ratios]}")

    if all(r < 1 for r in ratios[-2:]):
        # 減衰中 -> 収束
        avg_r = sum(ratios[-2:]) / 2
        remaining = d_vals[-1] * avg_r / (1 - avg_r) if avg_r < 1 else float('inf')
        h_limit = h_markov[-1] - remaining
        print(f"\n幾何級数外挿 (比率={avg_r:.4f}):")
        print(f"  残り補正: {remaining:.8f}")
        print(f"  推定 h_inf = {h_limit:.8f}")
    else:
        print(f"\n差分列がまだ増加中 -> 収束先の推定は困難")
        print(f"最良の下界: h >= {h_markov[-1]:.8f} (5次マルコフ)")


# ========================================
# Part 4: シャッフル比較 (大規模)
# ========================================

print("\n\n--- Part 4: シャッフル比較 ---")
random.seed(42)

# 全データの連結
all_data = []
for seq in all_orbits:
    all_data.extend(seq)

shuffled = list(all_data)
random.shuffle(shuffled)

print(f"データ長: {len(all_data)}")
print(f"\n{'k':>3} {'H(k)/k orig':>14} {'H(k)/k shuf':>14} {'相関による減少':>15}")
print("-" * 55)

for k in [1, 2, 3, 4, 5, 8, 10]:
    # original
    co = Counter()
    for i in range(len(all_data) - k + 1):
        co[tuple(all_data[i:i+k])] += 1
    to = sum(co.values())
    Ho = -sum(c/to * math.log2(c/to) for c in co.values())

    # shuffled
    cs = Counter()
    for i in range(len(shuffled) - k + 1):
        cs[tuple(shuffled[i:i+k])] += 1
    ts = sum(cs.values())
    Hs = -sum(c/ts * math.log2(c/ts) for c in cs.values())

    print(f"  {k:3d} {Ho/k:14.6f} {Hs/k:14.6f} {Hs/k - Ho/k:15.6f}")


# ========================================
# Part 5: 相互情報量の減衰
# ========================================

print("\n\n--- Part 5: 相互情報量の減衰 ---")

def mutual_info_from_orbits(orbits, lag):
    """軌道内のペアのみから相互情報量を計算"""
    px = Counter()
    py = Counter()
    pxy = Counter()
    total = 0
    for seq in orbits:
        for j in range(len(seq) - lag):
            x, y = seq[j], seq[j+lag]
            px[x] += 1
            py[y] += 1
            pxy[(x,y)] += 1
            total += 1
    if total == 0:
        return 0
    mi = 0.0
    for (x,y), c in pxy.items():
        p_xy = c / total
        p_x = px[x] / total
        p_y = py[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

print(f"\n{'lag':>5} {'I(v_t; v_{t+lag})':>18} {'I/I(1)':>10}")
I1 = mutual_info_from_orbits(all_orbits, 1)
mi_data = []
for lag in list(range(1, 31)) + [40, 50, 60, 80, 100]:
    mi = mutual_info_from_orbits(all_orbits, lag)
    ratio = mi / I1 if I1 > 0 else 0
    mi_data.append((lag, mi))
    if lag <= 20 or lag % 10 == 0:
        print(f"  {lag:5d} {mi:18.8f} {ratio:10.6f}")

# 減衰率の推定
print("\n減衰パターンのフィット:")
mi_for_fit = [(l, m) for l, m in mi_data if l >= 2 and l <= 20 and m > 0]
if len(mi_for_fit) >= 5:
    from statistics import linear_regression
    xs = [l for l, m in mi_for_fit]
    ys = [math.log(m) for l, m in mi_for_fit]
    try:
        slope, intercept = linear_regression(xs, ys)
        decay = -slope
        print(f"  I(lag) ~ {math.exp(intercept):.6f} * exp(-{decay:.4f} * lag)")
        print(f"  半減期: {math.log(2)/decay:.1f} steps")
        print(f"  相関長: {1/decay:.1f} steps")

        # エントロピー率への影響推定
        # 全相互情報量の和 = sum I(lag) ~ integral exp(-decay*lag) = 1/decay
        total_MI = sum(m for l, m in mi_data)
        print(f"\n  全相互情報量の和 (lag=1..100): {total_MI:.6f} bits")
        print(f"  理論全和 (指数減衰): {math.exp(intercept)/decay:.6f} bits")
    except:
        pass


# ========================================
# Part 6: 最終結論
# ========================================

print("\n\n" + "=" * 80)
print("最終結論")
print("=" * 80)

print(f"""
v2列 {{v2(3*T^i(n)+1)}} のブロックエントロピー率の解析結果:

データ: {len(all_orbits)} 軌道, 合計 {total_symbols} シンボル (n=3..500000の奇数)

[1] v2値の辺際分布
    H(1) = {H0:.6f} bits
    理論値 (幾何分布 P(v2=j)=1/2^j): 2.000 bits
    分布偏差: {2.0 - H0:.6f} bits
    主因: v2=1の出現頻度が理論(0.500)より高い(~{marginal[1]/total_v2:.3f})

[2] マルコフ推定によるエントロピー率
    次数0 (独立):   h = {H0:.6f}
    次数1:          h = {h1:.6f}  (差 {H0-h1:.6f})
    次数2:          h = {h2:.6f}  (差 {h1-h2:.6f})
    次数3:          h = {h3:.6f}  (差 {h2-h3:.6f})
    次数4:          h = {h4:.6f}  (差 {h3-h4:.6f})
    次数5:          h = {h5:.6f}  (差 {h4-h5:.6f})

[3] 収束状況
    マルコフ差分列: {', '.join(f'{d:.4f}' for d in d_vals)}
""")

# d_vals の振る舞いに基づく結論
if d_vals[-1] < d_vals[-2]:
    print(f"    差分は次数4->5で減少中 => 収束の兆候あり")
    if d_vals[-1] > 0:
        # 外挿
        r = d_vals[-1] / d_vals[-2]
        remaining = d_vals[-1] * r / (1-r) if r < 1 else float('inf')
        h_extrapolated = h_markov[-1] - remaining
        print(f"    外挿推定: h_inf ~ {h_extrapolated:.6f}")
else:
    print(f"    差分はまだ増加中 => 長距離相関が支配的")
    print(f"    5次マルコフ推定 h5 = {h5:.6f} は上界")

log2_43 = math.log2(4/3)
print(f"""
[4] 理論値との比較
    log2(4/3) = {log2_43:.6f}  (位相的エントロピー)
    log2(3) = {math.log2(3):.6f}  (= 2 - log2(4/3))
    2*log2(3/2) = {2*math.log2(3/2):.6f}

    注目: H(1) = {H0:.6f} ~ log2(3) = {math.log2(3):.6f}
    差: |H(1) - log2(3)| = {abs(H0 - math.log2(3)):.6f}

[5] エントロピー率の最良推定
    h ~ {h5:.4f} +/- {abs(d_vals[-1]):.4f} bits/step
    独立幾何分布からの乖離: {2.0 - h5:.4f} bits/step

[6] 乖離の主要因
    1. 分布偏差 (v2分布 != 幾何分布): {2.0 - H0:.4f} bits
    2. 相関効果 (1-5次マルコフ): {H0 - h5:.4f} bits
    3. 高次相関 (未推定): 小量
    合計: ~ {2.0 - h5:.4f} bits
""")


# JSON保存
output = {
    "title": "v2列ブロックエントロピー率の収束先特定",
    "data_stats": {
        "n_orbits": len(all_orbits),
        "total_symbols": total_symbols,
        "n_range": "3..500000",
    },
    "marginal_distribution": {
        "H1_observed": H0,
        "H1_theoretical": 2.0,
        "gap_distribution": 2.0 - H0,
        "v2_frequencies": {str(v): marginal[v]/total_v2 for v in sorted(marginal.keys())[:12]},
    },
    "markov_estimates": {
        "order_0": H0,
        "order_1": h1,
        "order_2": h2,
        "order_3": h3,
        "order_4": h4,
        "order_5": h5,
    },
    "markov_differences": {
        "d1": H0 - h1,
        "d2": h1 - h2,
        "d3": h2 - h3,
        "d4": h3 - h4,
        "d5": h4 - h5,
    },
    "block_entropy_rates": {str(k): results_all[k]['H_per_k'] for k in sorted(results_all.keys())},
    "conditional_entropy": {str(k): results_all[k]['h_k'] for k in sorted(results_all.keys())},
    "block_entropy_reliability": {str(k): results_all[k]['td_ratio'] for k in sorted(results_all.keys())},
    "best_estimate": {
        "h": h5,
        "uncertainty": abs(d_vals[-1]) if d_vals else 0,
        "gap_from_independent": 2.0 - h5,
    },
    "theoretical_constants": {
        "H_independent": 2.0,
        "log2_4_over_3": log2_43,
        "log2_3": math.log2(3),
        "2_log2_3_over_2": 2 * math.log2(3/2),
    },
    "mutual_info_decay": {
        "data": [(l, m) for l, m in mi_data[:20]],
    },
}

with open("/Users/soyukke/study/lean-unsolved/results/v2_entropy_rate_final.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n結果を results/v2_entropy_rate_final.json に保存しました")
