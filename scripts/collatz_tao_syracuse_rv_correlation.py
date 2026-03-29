#!/usr/bin/env python3
"""
Tao 2019 Syracuse Random Variable モデルの相関構造精密化

目的:
  1. Tao流のSyracuse RVモデルでのv2系列の相関関数を精密計算
  2. 実軌道との乖離の定量化
  3. 高次統計量(3次/4次キュムラント)での乖離検出

Taoモデル:
  Syracuse map: Syr(n) = (3n+1)/2^{v2(3n+1)} for odd n
  v2(3n+1) はTaoモデルでは Geom(1/2) (独立幾何分布) と近似
  理論的 E[v2] = 2, Var[v2] = 2
  ドリフト: E[log2(T/n)] = E[log2(3) - v2] = log2(3) - 2 = -0.41503...

本スクリプト:
  - 実軌道での v2 系列を大規模に収集
  - 自己相関関数 (ACF) を lag=0..20 で計算
  - 相互情報量 (MI) を lag=1..10 で計算
  - 高次キュムラント比較
  - 条件付き分布の偏差計測
  - 乖離の定量化指標を導出
"""

import math
from collections import defaultdict, Counter
import time
import random

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse map: Syr(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2_of_3n1(n):
    """v2(3n+1) for odd n"""
    return v2(3 * n + 1)

def get_v2_sequence(n, length):
    """奇数 n から length 回の Syracuse ステップの v2 系列を取得"""
    seq = []
    current = n
    for _ in range(length):
        if current <= 0:
            break
        val = v2_of_3n1(current)
        seq.append(val)
        current = syracuse(current)
        if current == 1:
            break
    return seq

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def variance(lst):
    if len(lst) < 2:
        return 0.0
    m = mean(lst)
    return sum((x - m)**2 for x in lst) / len(lst)

def std(lst):
    return math.sqrt(variance(lst))

# ============================================================
# Part 1: 大規模 v2 系列の収集
# ============================================================

def collect_v2_data(N_max, seq_len):
    """多数の奇数初期値からv2系列を収集"""
    all_sequences = []
    all_v2_values = []
    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, seq_len)
        if len(seq) >= seq_len:
            all_sequences.append(seq)
            all_v2_values.extend(seq)
    return all_sequences, all_v2_values

# ============================================================
# Part 2: 自己相関関数 (ACF) の計算
# ============================================================

def compute_acf(sequences, max_lag=20):
    """v2系列の自己相関関数を計算"""
    # 各lag位置でのペアを集める
    acf = {}
    global_mean = 0.0
    global_var = 0.0
    count = 0

    # まず全体の平均と分散
    all_vals = []
    for seq in sequences:
        all_vals.extend(seq)
    mu = mean(all_vals)
    var = variance(all_vals)

    for lag in range(max_lag + 1):
        cov_sum = 0.0
        pair_count = 0
        for seq in sequences:
            for i in range(len(seq) - lag):
                cov_sum += (seq[i] - mu) * (seq[i + lag] - mu)
                pair_count += 1
        if pair_count > 0 and var > 0:
            acf[lag] = (cov_sum / pair_count) / var
        else:
            acf[lag] = 0.0
    return acf, mu, var

# ============================================================
# Part 3: 相互情報量 (MI) の計算
# ============================================================

def compute_mutual_information(sequences, lag, v_max=10):
    """v2系列のlag距離での相互情報量を計算"""
    joint = defaultdict(int)
    marg_x = Counter()
    marg_y = Counter()
    total = 0

    for seq in sequences:
        for i in range(len(seq) - lag):
            x = min(seq[i], v_max)
            y = min(seq[i + lag], v_max)
            joint[(x, y)] += 1
            marg_x[x] += 1
            marg_y[y] += 1
            total += 1

    if total == 0:
        return 0.0

    mi = 0.0
    for (x, y), count in joint.items():
        p_xy = count / total
        p_x = marg_x[x] / total
        p_y = marg_y[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi

# ============================================================
# Part 4: 高次キュムラント
# ============================================================

def compute_cumulants(all_v2, max_v=15):
    """v2値の高次キュムラントを計算し理論値(Geom(1/2))と比較"""
    # Geom(1/2): P(X=k) = (1/2)^k for k=1,2,...
    # E[X] = 2, Var = 2, Skew = 6/sqrt(2) ~ 4.243, ExKurtosis = 6+12 = 18
    n = len(all_v2)
    mu = mean(all_v2)

    # 中心モーメント
    m2 = sum((x - mu)**2 for x in all_v2) / n
    m3 = sum((x - mu)**3 for x in all_v2) / n
    m4 = sum((x - mu)**4 for x in all_v2) / n

    # キュムラント
    k1 = mu
    k2 = m2
    k3 = m3  # 3次キュムラント = 3次中心モーメント
    k4 = m4 - 3 * m2**2  # 4次キュムラント

    # 正規化
    skewness = k3 / (k2 ** 1.5) if k2 > 0 else 0.0
    ex_kurtosis = k4 / (k2 ** 2) if k2 > 0 else 0.0

    # Geom(1/2)の理論値
    # E[X] = 2, Var = 2
    # Skewness = (1 + p) / sqrt(1 - p) = (1 + 1/2) / sqrt(1/2) = (3/2) / (1/sqrt(2)) = 3*sqrt(2)/2
    # Excess kurtosis = 6 + p^2/(1-p) = 6 + (1/4)/(1/2) = 6 + 1/2 = 6.5
    # (p=1/2 for Geom(1/2) starting at 1)

    # Geometric distribution with p=1/2, support {1,2,3,...}
    # E[X] = 1/p = 2
    # Var[X] = (1-p)/p^2 = (1/2)/(1/4) = 2
    # Third central moment: (2-p)(1-p)/p^3 = (3/2)(1/2)/(1/8) = 6
    # Skewness = 6 / (2^{3/2}) = 6/(2*sqrt(2)) = 3/sqrt(2) ~ 2.1213
    # Fourth central moment: (9p^2 - 9p + 2)(1-p) / p^4 + 3*(2/1)
    # ... let me compute numerically

    # Numerical computation of Geom(1/2) cumulants
    geom_probs = {}
    for k in range(1, 30):
        geom_probs[k] = 0.5 ** k
    geom_mu = sum(k * p for k, p in geom_probs.items())
    geom_m2 = sum((k - geom_mu)**2 * p for k, p in geom_probs.items())
    geom_m3 = sum((k - geom_mu)**3 * p for k, p in geom_probs.items())
    geom_m4 = sum((k - geom_mu)**4 * p for k, p in geom_probs.items())
    geom_skew = geom_m3 / (geom_m2 ** 1.5)
    geom_exkurt = (geom_m4 / (geom_m2 ** 2)) - 3

    return {
        'mean': (k1, geom_mu),
        'variance': (k2, geom_m2),
        'skewness': (skewness, geom_skew),
        'ex_kurtosis': (ex_kurtosis, geom_exkurt),
        'k3': (k3, geom_m3),
        'k4': (k4, geom_m4 - 3 * geom_m2**2)
    }

# ============================================================
# Part 5: 条件付き分布の分析
# ============================================================

def analyze_conditional_distributions(sequences, max_condition=6):
    """v2_i の値に条件付けた v2_{i+1} の分布を分析"""
    cond_data = defaultdict(list)
    for seq in sequences:
        for i in range(len(seq) - 1):
            if seq[i] <= max_condition:
                cond_data[seq[i]].append(seq[i + 1])

    results = {}
    for v_cond in sorted(cond_data.keys()):
        vals = cond_data[v_cond]
        n = len(vals)
        m = mean(vals)
        v = variance(vals)
        # v2の分布
        dist = Counter(vals)
        # KL divergence from Geom(1/2)
        kl = 0.0
        for k in range(1, 15):
            p_emp = dist.get(k, 0) / n
            p_geom = 0.5 ** k
            if p_emp > 0:
                kl += p_emp * math.log(p_emp / p_geom)
        results[v_cond] = {
            'count': n,
            'mean': m,
            'var': v,
            'kl_from_geom': kl,
            'dist_top5': dict(dist.most_common(5))
        }
    return results

# ============================================================
# Part 6: 位置依存性 (Syracuse step index による変化)
# ============================================================

def analyze_position_dependence(sequences, max_pos=20):
    """軌道中の位置 (step index) による v2 の統計量変化"""
    pos_data = defaultdict(list)
    for seq in sequences:
        for i, val in enumerate(seq):
            if i < max_pos:
                pos_data[i].append(val)

    results = {}
    for pos in range(max_pos):
        if pos in pos_data and len(pos_data[pos]) > 100:
            vals = pos_data[pos]
            results[pos] = {
                'mean': mean(vals),
                'var': variance(vals),
                'count': len(vals)
            }
    return results

# ============================================================
# Part 7: ドリフトの精密計算
# ============================================================

def compute_drift_statistics(sequences, N_max):
    """log2(Syr(n)/n) = log2(3) - v2(3n+1) のドリフト統計"""
    log2_3 = math.log2(3)
    drifts = []
    for seq in sequences:
        for v in seq:
            drift = log2_3 - v
            drifts.append(drift)

    # 理論値: E[drift] = log2(3) - E[v2] = log2(3) - 2
    theory_mean = log2_3 - 2.0  # -0.41503...

    # ステップペアでのドリフト相関
    drift_pairs = []
    for seq in sequences:
        for i in range(len(seq) - 1):
            d1 = log2_3 - seq[i]
            d2 = log2_3 - seq[i + 1]
            drift_pairs.append((d1, d2))

    if drift_pairs:
        d1_list = [p[0] for p in drift_pairs]
        d2_list = [p[1] for p in drift_pairs]
        mu1 = mean(d1_list)
        mu2 = mean(d2_list)
        cov = mean([(a - mu1) * (b - mu2) for a, b in drift_pairs])
        var1 = variance(d1_list)
        var2 = variance(d2_list)
        if var1 > 0 and var2 > 0:
            corr = cov / math.sqrt(var1 * var2)
        else:
            corr = 0.0
    else:
        corr = 0.0
        cov = 0.0

    return {
        'drift_mean': mean(drifts),
        'drift_var': variance(drifts),
        'theory_mean': theory_mean,
        'mean_deviation': mean(drifts) - theory_mean,
        'drift_pair_corr': corr,
        'drift_pair_cov': cov
    }

# ============================================================
# Part 8: 累積ドリフトの分散成長率
# ============================================================

def compute_cumulative_drift_variance(sequences, max_steps=20):
    """累積ドリフト S_k = sum_{i=1}^{k} (log2(3)-v2_i) の分散成長率
    独立ならVar[S_k] = k * Var[drift]
    相関があればずれる
    """
    log2_3 = math.log2(3)
    results = {}

    for k in range(1, max_steps + 1):
        cumulative = []
        for seq in sequences:
            if len(seq) >= k:
                s = sum(log2_3 - seq[i] for i in range(k))
                cumulative.append(s)
        if len(cumulative) > 100:
            m = mean(cumulative)
            v = variance(cumulative)
            results[k] = {
                'mean': m,
                'var': v,
                'count': len(cumulative)
            }

    return results

# ============================================================
# Part 9: 連続3ステップの高次相関
# ============================================================

def compute_three_point_correlation(sequences):
    """3点相関 <(v2_i - mu)(v2_{i+1} - mu)(v2_{i+2} - mu)> を計算"""
    all_v2 = []
    for seq in sequences:
        all_v2.extend(seq)
    mu = mean(all_v2)

    triple_sum = 0.0
    count = 0
    for seq in sequences:
        for i in range(len(seq) - 2):
            triple_sum += (seq[i] - mu) * (seq[i+1] - mu) * (seq[i+2] - mu)
            count += 1

    three_point = triple_sum / count if count > 0 else 0.0

    # 4点 connected correlation
    quad_sum = 0.0
    qcount = 0
    for seq in sequences:
        for i in range(len(seq) - 3):
            quad_sum += ((seq[i] - mu) * (seq[i+1] - mu) *
                        (seq[i+2] - mu) * (seq[i+3] - mu))
            qcount += 1
    four_point = quad_sum / qcount if qcount > 0 else 0.0

    return three_point, four_point

# ============================================================
# Part 10: mod 2^k での v2 偏差
# ============================================================

def analyze_v2_mod_structure(N_max, k_max=8):
    """n mod 2^k の値による v2(3n+1) の平均の変動を分析
    Taoモデルではnのmod構造がv2に影響しない（独立）はずだが、
    実際にはn mod 2^k がv2(3n+1)を完全に決定する局所構造がある"""
    results = {}
    for k in range(1, k_max + 1):
        mod = 2 ** k
        class_data = defaultdict(list)
        for n in range(1, min(N_max + 1, 200001), 2):
            r = n % mod
            val = v2_of_3n1(n)
            class_data[r].append(val)

        # 各剰余類でのv2の平均
        means_by_class = {}
        for r in sorted(class_data.keys()):
            if len(class_data[r]) >= 10:
                means_by_class[r] = mean(class_data[r])

        if means_by_class:
            vals = list(means_by_class.values())
            spread = max(vals) - min(vals)
            avg_mean = mean(vals)
            var_of_means = variance(vals)
        else:
            spread = 0
            avg_mean = 0
            var_of_means = 0

        results[k] = {
            'num_classes': len(means_by_class),
            'spread': spread,
            'avg_mean': avg_mean,
            'var_of_means': var_of_means
        }
    return results

# ============================================================
# Part 11: 2次マルコフモデルのフィッティング
# ============================================================

def fit_second_order_markov(sequences, max_v=6):
    """v2系列の2次マルコフモデル P(v2_{i+2} | v2_{i+1}, v2_i) をフィッティング"""
    # 遷移カウント
    triple_counts = defaultdict(lambda: defaultdict(int))
    pair_counts = defaultdict(int)

    for seq in sequences:
        for i in range(len(seq) - 2):
            a, b, c = min(seq[i], max_v), min(seq[i+1], max_v), min(seq[i+2], max_v)
            triple_counts[(a, b)][c] += 1
            pair_counts[(a, b)] += 1

    # 1次マルコフとの比較
    single_counts = defaultdict(lambda: defaultdict(int))
    single_totals = defaultdict(int)
    for seq in sequences:
        for i in range(len(seq) - 1):
            b, c = min(seq[i], max_v), min(seq[i+1], max_v)
            single_counts[b][c] += 1
            single_totals[b] += 1

    # 2次vs1次の差を測定
    max_diff = 0.0
    total_kl = 0.0
    kl_count = 0

    for (a, b), c_counts in triple_counts.items():
        total = pair_counts[(a, b)]
        if total < 50:
            continue
        for c in range(1, max_v + 1):
            p2 = c_counts.get(c, 0) / total  # 2次
            p1 = single_counts[b].get(c, 0) / single_totals[b] if single_totals[b] > 0 else 0
            diff = abs(p2 - p1)
            if diff > max_diff:
                max_diff = diff
                max_diff_config = (a, b, c, p2, p1)
            if p2 > 0 and p1 > 0:
                total_kl += p2 * math.log(p2 / p1)
                kl_count += 1

    avg_kl = total_kl / kl_count if kl_count > 0 else 0.0

    return {
        'max_diff': max_diff,
        'max_diff_config': max_diff_config if max_diff > 0 else None,
        'avg_kl_2nd_vs_1st': avg_kl,
        'num_transitions_analyzed': kl_count
    }

# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 80)
    print("Tao 2019 Syracuse RV モデル相関構造精密化")
    print("=" * 80)

    # パラメータ
    N_MAX = 200_000   # 奇数初期値の上限
    SEQ_LEN = 30      # 各軌道から取得するステップ数

    t0 = time.time()

    # データ収集
    print(f"\n[Phase 1] データ収集: 奇数 3..{N_MAX}, 各{SEQ_LEN}ステップ")
    sequences, all_v2 = collect_v2_data(N_MAX, SEQ_LEN)
    print(f"  軌道数: {len(sequences)}")
    print(f"  総v2値数: {len(all_v2)}")
    print(f"  収集時間: {time.time() - t0:.1f}秒")

    # Part 2: ACF
    print(f"\n[Phase 2] 自己相関関数 (ACF)")
    acf, mu, var = compute_acf(sequences, max_lag=20)
    print(f"  全体平均 E[v2] = {mu:.6f}  (理論: 2.0)")
    print(f"  全体分散 Var[v2] = {var:.6f}  (理論: 2.0)")
    print(f"\n  Lag | ACF(lag)     | 独立からの偏差")
    print(f"  " + "-" * 45)
    for lag in range(21):
        deviation = acf[lag] - (1.0 if lag == 0 else 0.0)
        star = " ***" if abs(deviation) > 0.01 and lag > 0 else ""
        print(f"  {lag:3d} | {acf[lag]:+.8f} | {deviation:+.8f}{star}")

    # Part 3: MI
    print(f"\n[Phase 3] 相互情報量 (MI)")
    print(f"  Lag | MI (bits)   | 意味")
    print(f"  " + "-" * 45)
    for lag in range(1, 11):
        mi = compute_mutual_information(sequences, lag)
        level = "強い依存" if mi > 0.05 else ("弱い依存" if mi > 0.01 else "ほぼ独立")
        print(f"  {lag:3d} | {mi:.6f}    | {level}")

    # Part 4: 高次キュムラント
    print(f"\n[Phase 4] 高次キュムラント比較")
    cumulants = compute_cumulants(all_v2)
    print(f"  {'統計量':15s} | {'実測値':>12s} | {'Geom(1/2)理論':>12s} | {'偏差':>12s} | {'相対偏差%':>10s}")
    print(f"  " + "-" * 75)
    for name, (emp, theo) in cumulants.items():
        rel_dev = (emp - theo) / abs(theo) * 100 if abs(theo) > 1e-10 else 0.0
        print(f"  {name:15s} | {emp:12.6f} | {theo:12.6f} | {emp - theo:+12.6f} | {rel_dev:+9.3f}%")

    # Part 5: 条件付き分布
    print(f"\n[Phase 5] 条件付き分布 P(v2_{'{i+1}'} | v2_i = k)")
    cond = analyze_conditional_distributions(sequences)
    print(f"  v2_i | E[v2_{{i+1}}] | Var       | KL(実測||Geom) | 観測数")
    print(f"  " + "-" * 65)
    for k, info in sorted(cond.items()):
        print(f"  {k:4d} | {info['mean']:10.6f} | {info['var']:9.4f} | {info['kl_from_geom']:.6f}       | {info['count']:,}")

    # Part 6: 位置依存性
    print(f"\n[Phase 6] 位置 (step index) 依存性")
    pos_dep = analyze_position_dependence(sequences)
    print(f"  Step | E[v2]     | Var[v2]    | 理論乖離")
    print(f"  " + "-" * 50)
    for pos in range(min(20, len(pos_dep))):
        if pos in pos_dep:
            d = pos_dep[pos]
            dev = d['mean'] - 2.0
            print(f"  {pos:4d} | {d['mean']:9.6f} | {d['var']:10.6f} | {dev:+.6f}")

    # Part 7: ドリフト統計
    print(f"\n[Phase 7] ドリフト統計")
    drift = compute_drift_statistics(sequences, N_MAX)
    print(f"  E[log2(T/n)] = {drift['drift_mean']:.8f}  (理論: {drift['theory_mean']:.8f})")
    print(f"  偏差 = {drift['mean_deviation']:.8f}")
    print(f"  Var[log2(T/n)] = {drift['drift_var']:.8f}")
    print(f"  連続ドリフト相関 = {drift['drift_pair_corr']:.8f}")
    print(f"  連続ドリフト共分散 = {drift['drift_pair_cov']:.8f}")

    # Part 8: 累積ドリフト分散
    print(f"\n[Phase 8] 累積ドリフト分散成長率")
    cum_drift = compute_cumulative_drift_variance(sequences, max_steps=20)
    single_var = drift['drift_var']
    print(f"  k  | Var[S_k]    | k*Var[d]    | 比率          | 乖離%")
    print(f"  " + "-" * 65)
    for k in range(1, 21):
        if k in cum_drift:
            d = cum_drift[k]
            expected = k * single_var
            ratio = d['var'] / expected if expected > 0 else 0
            dev_pct = (ratio - 1.0) * 100
            print(f"  {k:3d} | {d['var']:11.6f} | {expected:11.6f} | {ratio:12.6f}  | {dev_pct:+7.3f}%")

    # Part 9: 3点・4点相関
    print(f"\n[Phase 9] 高次相関関数")
    three_pt, four_pt = compute_three_point_correlation(sequences)
    print(f"  3点相関 <(v2_i-mu)(v2_{{i+1}}-mu)(v2_{{i+2}}-mu)> = {three_pt:.8f}")
    print(f"  4点相関 <(v2_i-mu)(v2_{{i+1}}-mu)(v2_{{i+2}}-mu)(v2_{{i+3}}-mu)> = {four_pt:.8f}")
    # 独立なら両方 0
    print(f"  (独立Geom(1/2)モデルでは両方 0 になるべき)")

    # Part 10: mod構造による偏差
    print(f"\n[Phase 10] n mod 2^k による v2(3n+1) の構造")
    mod_struct = analyze_v2_mod_structure(N_MAX)
    print(f"  k  | mod 2^k | classes | spread    | Var(means)")
    print(f"  " + "-" * 55)
    for k, info in sorted(mod_struct.items()):
        print(f"  {k:3d} | {2**k:>7d} | {info['num_classes']:>7d} | {info['spread']:9.4f} | {info['var_of_means']:.6f}")

    # Part 11: 2次マルコフ
    print(f"\n[Phase 11] 2次マルコフモデル vs 1次マルコフモデル")
    markov2 = fit_second_order_markov(sequences)
    print(f"  最大確率差: {markov2['max_diff']:.6f}")
    if markov2['max_diff_config']:
        a, b, c, p2, p1 = markov2['max_diff_config']
        print(f"    at (v2_i={a}, v2_{{i+1}}={b}) -> v2_{{i+2}}={c}")
        print(f"    P_2次={p2:.4f}, P_1次={p1:.4f}")
    print(f"  平均KL(2次||1次): {markov2['avg_kl_2nd_vs_1st']:.8f} nats")

    # 総合まとめ
    print(f"\n{'='*80}")
    print(f"総合まとめ: Tao RVモデルとの乖離定量化")
    print(f"{'='*80}")

    # 乖離指標のまとめ
    print(f"\n  1. 平均の乖離: E[v2] = {mu:.6f} (理論2.0, 偏差={mu-2.0:+.6f})")
    print(f"  2. 分散の乖離: Var[v2] = {var:.6f} (理論2.0, 偏差={var-2.0:+.6f})")
    print(f"  3. lag=1 ACF: {acf[1]:+.8f} (独立なら0)")
    mi_1 = compute_mutual_information(sequences, 1)
    mi_4 = compute_mutual_information(sequences, 4)
    print(f"  4. lag=1 MI: {mi_1:.6f} bits")
    print(f"  5. lag=4 MI: {mi_4:.6f} bits")
    print(f"  6. 3点相関: {three_pt:.8f}")
    print(f"  7. 累積分散 Var[S_20]/20Var[d] - 1: ", end="")
    if 20 in cum_drift:
        ratio20 = cum_drift[20]['var'] / (20 * single_var) if single_var > 0 else 0
        print(f"{ratio20 - 1.0:+.6f}")
    else:
        print("N/A")
    print(f"  8. 2次マルコフgap: {markov2['max_diff']:.6f}")
    print(f"  9. 連続ドリフト相関: {drift['drift_pair_corr']:.8f}")

    # 乖離の物理的意味
    print(f"\n  【解釈】")
    if abs(acf[1]) > 0.005:
        print(f"  - lag=1で有意なACF → v2値間に短距離相関が存在")
    if mi_1 > 0.02:
        print(f"  - MI(lag=1)={mi_1:.4f}bits → Taoの独立仮定は近似的")
    if abs(three_pt) > 0.01:
        print(f"  - 3点相関が非ゼロ → 高次の非線形依存が存在")
    if markov2['max_diff'] > 0.01:
        print(f"  - 2次マルコフgapが大きい → v2列は少なくとも2ステップ記憶を持つ")

    cum_dev = 0
    if 20 in cum_drift:
        cum_dev = cum_drift[20]['var'] / (20 * single_var) - 1.0 if single_var > 0 else 0
    if abs(cum_dev) > 0.01:
        sgn = "超拡散(正の相関)" if cum_dev > 0 else "亜拡散(負の相関)"
        print(f"  - 累積分散の乖離{cum_dev:+.4f} → {sgn}的効果")

    total_time = time.time() - t0
    print(f"\n  総実行時間: {total_time:.1f}秒")

if __name__ == "__main__":
    main()
