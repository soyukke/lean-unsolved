#!/usr/bin/env python3
"""
加速Syracuse Syr^2 CLT近似精度の深掘り分析

前回の発見:
  - 連続ステップ相関 ≈ 0.001 （ほぼ独立）
  - 分散比 2step/2*1step ≈ 1.0006 （独立和に非常に近い）
  - 1ステップ: 歪度=-2.12, 尖度=6.48 （正規分布からの大きな逸脱）
  - k=20でKS≈0.054, kの増加でCLT収束は確認

本分析:
  1. 大きなnのみ使用（軌道の1到達問題を回避）
  2. 尾部分布の精密解析（裾の重さの定量化）
  3. 独立和モデル vs 実データの尾部比較
  4. Edgeworth展開による補正項の計算
  5. T^2のドリフト定数の精密推定
"""

import math
import random
import time
import json
from collections import Counter, defaultdict

def v2(n):
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def compute_stats(data):
    n = len(data)
    mu = sum(data) / n
    var = sum((x - mu)**2 for x in data) / n
    sigma = math.sqrt(var) if var > 0 else 1e-15
    skew = sum(((x - mu) / sigma)**3 for x in data) / n
    kurt = sum(((x - mu) / sigma)**4 for x in data) / n - 3
    m5 = sum(((x - mu) / sigma)**5 for x in data) / n
    m6 = sum(((x - mu) / sigma)**6 for x in data) / n
    return {"mean": mu, "var": var, "std": sigma, "skewness": skew,
            "kurtosis": kurt, "5th_moment": m5, "6th_moment": m6}

# ============================================================
# Part 1: 大きなnでの高精度1ステップ分布
# ============================================================

def precise_1step_distribution(N_samples=1000000):
    """
    大きな奇数 n ~ [10^9, 10^10] での1ステップ増分分布
    小さなnでの異常を避ける
    """
    print("  大きなnでの1ステップ分布収集...")
    increments = []
    v2_vals = []

    for _ in range(N_samples):
        n = random.randint(10**9, 10**10)
        if n % 2 == 0:
            n += 1
        tn = syracuse(n)
        increments.append(math.log2(tn / n))
        v2_vals.append(v2(3 * n + 1))

    stats = compute_stats(increments)
    v2s = compute_stats([float(v) for v in v2_vals])

    # v2の分布
    v2_counter = Counter(v2_vals)
    v2_dist = {}
    total = len(v2_vals)
    for k in sorted(v2_counter.keys()):
        if k <= 15:
            empirical = v2_counter[k] / total
            theoretical = 2**(-k)  # Geom(1/2) starting at 1
            v2_dist[str(k)] = {
                "empirical": empirical,
                "theoretical": theoretical,
                "ratio": empirical / theoretical if theoretical > 0 else None,
            }

    return {
        "increment_stats": stats,
        "v2_stats": v2s,
        "v2_distribution": v2_dist,
        "theoretical_mean": math.log2(3) - 2,
        "mean_deviation": stats["mean"] - (math.log2(3) - 2),
    }

# ============================================================
# Part 2: Edgeworth展開によるCLT補正
# ============================================================

def edgeworth_expansion_analysis(N_samples=500000):
    """
    Edgeworth展開: P(S_k/sqrt(k) <= x) ≈ Phi(x) + corrections

    第1補正: -(kappa_3 / (6 * sqrt(k))) * (x^2 - 1) * phi(x)
    第2補正:
      (kappa_4 / (24*k)) * (x^3 - 3x) * phi(x)
      + (kappa_3^2 / (72*k)) * (x^5 - 10x^3 + 15x) * phi(x)

    ここで kappa_3 = skewness, kappa_4 = excess kurtosis
    """
    print("  1ステップ増分のキュムラントを精密計算...")
    increments = []
    for _ in range(N_samples):
        n = random.randint(10**8, 10**9)
        if n % 2 == 0:
            n += 1
        increments.append(math.log2(syracuse(n) / n))

    stats = compute_stats(increments)
    kappa3 = stats["skewness"]
    kappa4 = stats["kurtosis"]

    def phi(x):
        return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)

    def Phi(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def edgeworth_cdf(x, k, kappa3, kappa4):
        """k個の和の標準化されたCDF（Edgeworth展開付き）"""
        term0 = Phi(x)
        term1 = -(kappa3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi(x)
        term2_a = (kappa4 / (24 * k)) * (x**3 - 3*x) * phi(x)
        term2_b = (kappa3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi(x)
        return term0 + term1 + term2_a + term2_b

    # 各kでの精度比較
    results = []
    for k in [2, 3, 5, 10, 20, 50]:
        print(f"  k={k} のEdgeworth展開精度を評価...")
        sums = []
        for _ in range(min(N_samples, 200000)):
            n = random.randint(10**8, 10**9)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * stats["mean"]
        sigma_k = stats["std"] * math.sqrt(k)
        standardized = [(s - mu_k) / sigma_k for s in sums]
        sorted_z = sorted(standardized)
        n_z = len(sorted_z)

        # 通常CLTとEdgeworth展開のKS統計量
        ks_clt = 0
        ks_edge = 0
        max_edge_improve = 0

        for i, z in enumerate(sorted_z):
            ecdf = (i + 1) / n_z
            clt_cdf = Phi(z)
            edge_cdf = edgeworth_cdf(z, k, kappa3, kappa4)

            err_clt = abs(ecdf - clt_cdf)
            err_edge = abs(ecdf - edge_cdf)

            ks_clt = max(ks_clt, err_clt)
            ks_edge = max(ks_edge, err_edge)
            max_edge_improve = max(max_edge_improve, err_clt - err_edge)

        results.append({
            "k": k,
            "n_samples": n_z,
            "ks_clt": ks_clt,
            "ks_edgeworth": ks_edge,
            "improvement_factor": ks_clt / ks_edge if ks_edge > 0 else None,
            "max_edge_improvement": max_edge_improve,
        })

    return {
        "kappa3_skewness": kappa3,
        "kappa4_excess_kurtosis": kappa4,
        "results": results,
    }

# ============================================================
# Part 3: 尾部分布の精密解析
# ============================================================

def tail_distribution_analysis(N_samples=500000):
    """
    log2(T(n)/n) の尾部の重さを定量化
    正規分布 vs 実分布の裾の比較
    """
    print("  尾部分布の精密解析...")
    increments = []
    for _ in range(N_samples):
        n = random.randint(10**8, 10**9)
        if n % 2 == 0:
            n += 1
        increments.append(math.log2(syracuse(n) / n))

    stats = compute_stats(increments)
    mu = stats["mean"]
    sigma = stats["std"]

    # 尾部確率の実測と正規分布理論値の比較
    tail_results = []
    for threshold in [1, 1.5, 2, 2.5, 3, 3.5, 4, 5]:
        # 右裾: P(X > mu + t*sigma)
        right_count = sum(1 for x in increments if x > mu + threshold * sigma)
        right_prob = right_count / N_samples
        right_normal = 0.5 * math.erfc(threshold / math.sqrt(2))

        # 左裾: P(X < mu - t*sigma)
        left_count = sum(1 for x in increments if x < mu - threshold * sigma)
        left_prob = left_count / N_samples
        left_normal = 0.5 * math.erfc(threshold / math.sqrt(2))

        tail_results.append({
            "threshold_sigma": threshold,
            "right_tail_empirical": right_prob,
            "right_tail_normal": right_normal,
            "right_ratio": right_prob / right_normal if right_normal > 0 else None,
            "left_tail_empirical": left_prob,
            "left_tail_normal": left_normal,
            "left_ratio": left_prob / left_normal if left_normal > 0 else None,
        })

    # 2ステップでの尾部
    print("  2ステップ尾部分布...")
    inc2_list = []
    for _ in range(N_samples):
        n = random.randint(10**8, 10**9)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t2 = syracuse(t1)
        inc2_list.append(math.log2(t2 / n))

    stats2 = compute_stats(inc2_list)
    mu2 = stats2["mean"]
    sigma2 = stats2["std"]

    tail_results_2step = []
    for threshold in [1, 1.5, 2, 2.5, 3, 3.5, 4]:
        right_count = sum(1 for x in inc2_list if x > mu2 + threshold * sigma2)
        right_prob = right_count / N_samples
        right_normal = 0.5 * math.erfc(threshold / math.sqrt(2))

        left_count = sum(1 for x in inc2_list if x < mu2 - threshold * sigma2)
        left_prob = left_count / N_samples
        left_normal = 0.5 * math.erfc(threshold / math.sqrt(2))

        tail_results_2step.append({
            "threshold_sigma": threshold,
            "right_tail_empirical": right_prob,
            "right_tail_normal": right_normal,
            "right_ratio": right_prob / right_normal if right_normal > 0 else None,
            "left_tail_empirical": left_prob,
            "left_tail_normal": left_normal,
            "left_ratio": left_prob / left_normal if left_normal > 0 else None,
        })

    return {
        "1step_stats": stats,
        "1step_tails": tail_results,
        "2step_stats": stats2,
        "2step_tails": tail_results_2step,
    }

# ============================================================
# Part 4: T^2の分解表現
# ============================================================

def t2_decomposition(N_samples=500000):
    """
    T^2(n) = T(T(n)) の増分を詳しく分解

    log2(T^2(n)/n) = log2(3) - v2_1 + log2(3) - v2_2
                    = 2*log2(3) - (v2_1 + v2_2)

    ここで v2_1 = v2(3n+1), v2_2 = v2(3*T(n)+1)

    v2_1 + v2_2 の分布が 2個の独立 Geom(1/2) の和に近いか検証
    """
    print("  T^2 分解表現の解析...")
    v2_sums = []
    v2_1_list = []
    v2_2_list = []

    for _ in range(N_samples):
        n = random.randint(10**8, 10**9)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        v1 = v2(3 * n + 1)
        v2_val = v2(3 * t1 + 1)
        v2_sums.append(v1 + v2_val)
        v2_1_list.append(v1)
        v2_2_list.append(v2_val)

    # v2_1 + v2_2 の分布 vs 理論（独立幾何和）
    sum_counter = Counter(v2_sums)
    total = len(v2_sums)

    # 2個の独立Geom(1/2) (starting at 1) の和の理論分布
    # P(V1+V2 = s) = sum_{v1=1}^{s-1} P(V1=v1)*P(V2=s-v1)
    # = sum_{v1=1}^{s-1} 2^{-v1} * 2^{-(s-v1)} = (s-1) * 2^{-s}

    dist_comparison = {}
    chi2_stat = 0
    for s in range(2, 20):
        empirical = sum_counter.get(s, 0) / total
        theoretical = (s - 1) * 2**(-s)
        diff = empirical - theoretical
        if theoretical > 0:
            chi2_contrib = (empirical - theoretical)**2 / theoretical
            chi2_stat += chi2_contrib * total
        dist_comparison[str(s)] = {
            "empirical": empirical,
            "theoretical": theoretical,
            "difference": diff,
            "relative_diff": diff / theoretical if theoretical > 0 else None,
        }

    # ドリフト精密計算
    mean_v2_sum = sum(v2_sums) / total
    drift_t2 = 2 * math.log2(3) - mean_v2_sum

    # 独立性検定: 相関
    corr_v2 = (sum(v2_1_list[i] * v2_2_list[i] for i in range(total)) / total
               - (sum(v2_1_list) / total) * (sum(v2_2_list) / total))
    var_v2_1 = sum(v**2 for v in v2_1_list) / total - (sum(v2_1_list) / total)**2
    var_v2_2 = sum(v**2 for v in v2_2_list) / total - (sum(v2_2_list) / total)**2
    corr_coeff = corr_v2 / math.sqrt(var_v2_1 * var_v2_2) if var_v2_1 > 0 and var_v2_2 > 0 else 0

    return {
        "v2_sum_distribution": dist_comparison,
        "chi2_statistic": chi2_stat,
        "mean_v2_sum": mean_v2_sum,
        "theoretical_mean_v2_sum": 4.0,
        "drift_t2": drift_t2,
        "theoretical_drift_t2": 2 * math.log2(3) - 4,
        "v2_correlation_coefficient": corr_coeff,
        "v2_1_stats": compute_stats([float(v) for v in v2_1_list]),
        "v2_2_stats": compute_stats([float(v) for v in v2_2_list]),
    }

# ============================================================
# Part 5: 高次相関 (v2 mod 2, mod 3 の依存)
# ============================================================

def v2_modular_dependence(N_samples=500000):
    """
    v2(3n+1) mod m と v2(3*T(n)+1) mod m の依存関係
    独立なら均一分布になるはず
    """
    print("  v2のmodular依存性を解析...")
    results = {}

    for mod in [2, 3, 4]:
        joint_counter = Counter()
        for _ in range(N_samples):
            n = random.randint(10**8, 10**9)
            if n % 2 == 0:
                n += 1
            t1 = syracuse(n)
            v1 = v2(3 * n + 1)
            v2_val = v2(3 * t1 + 1)
            joint_counter[(v1 % mod, v2_val % mod)] += 1

        total = sum(joint_counter.values())

        # 周辺分布
        marginal1 = Counter()
        marginal2 = Counter()
        for (a, b), c in joint_counter.items():
            marginal1[a] += c
            marginal2[b] += c

        # 独立仮定との乖離
        max_deviation = 0
        chi2 = 0
        joint_dist = {}

        for a in range(mod):
            for b in range(mod):
                observed = joint_counter.get((a, b), 0) / total
                expected = (marginal1.get(a, 0) / total) * (marginal2.get(b, 0) / total)
                deviation = observed - expected
                max_deviation = max(max_deviation, abs(deviation))
                if expected > 0:
                    chi2 += (observed - expected)**2 / expected * total
                joint_dist[f"({a},{b})"] = {
                    "observed": observed,
                    "expected_indep": expected,
                    "deviation": deviation,
                }

        results[f"mod{mod}"] = {
            "chi2_statistic": chi2,
            "max_deviation": max_deviation,
            "joint_distribution": joint_dist,
        }

    return results

# ============================================================
# Part 6: k-ステップ和の高精度CLT収束
# ============================================================

def precise_clt_convergence(N_samples=200000):
    """
    大きなnを使い、軌道の1到達を避けたCLT収束速度の精密測定
    """
    print("  高精度CLT収束速度測定...")

    # まず1ステップのキュムラント
    inc_all = []
    for _ in range(N_samples):
        n = random.randint(10**10, 10**11)
        if n % 2 == 0:
            n += 1
        inc_all.append(math.log2(syracuse(n) / n))

    stats1 = compute_stats(inc_all)

    results = []
    for k in [1, 2, 3, 4, 5, 8, 10, 15, 20, 30]:
        print(f"    k={k}...")
        sums = []
        for _ in range(min(N_samples, 150000)):
            n = random.randint(10**10, 10**11)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * stats1["mean"]
        sigma_k = stats1["std"] * math.sqrt(k)
        standardized = [(s - mu_k) / sigma_k for s in sums]

        # 標準化データの統計量
        z_stats = compute_stats(standardized)

        # KS
        sorted_z = sorted(standardized)
        n_z = len(sorted_z)
        ks = 0
        for i, z in enumerate(sorted_z):
            cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ecdf = (i + 1) / n_z
            ks = max(ks, abs(ecdf - cdf), abs(i / n_z - cdf))

        # CLT理論: KS ~ C / sqrt(k) (Berry-Esseen)
        results.append({
            "k": k,
            "n_samples": len(sums),
            "ks_statistic": ks,
            "ks_times_sqrt_k": ks * math.sqrt(k),
            "standardized_mean": z_stats["mean"],
            "standardized_std": z_stats["std"],
            "standardized_skewness": z_stats["skewness"],
            "standardized_kurtosis": z_stats["kurtosis"],
            "actual_mean": sum(sums) / len(sums),
            "expected_mean": mu_k,
        })

    return {
        "one_step_cumulants": {
            "mean": stats1["mean"],
            "var": stats1["var"],
            "skewness": stats1["skewness"],
            "kurtosis": stats1["kurtosis"],
        },
        "convergence_data": results,
    }

# ============================================================
# メイン
# ============================================================

def main():
    start_time = time.time()
    all_results = {}

    print("=" * 70)
    print("Syr^2 CLT近似精度 深掘り分析")
    print("=" * 70)

    # Part 1
    print("\n[Part 1] 大きなnでの高精度1ステップ分布")
    p1 = precise_1step_distribution(500000)
    all_results["precise_1step"] = p1
    s = p1["increment_stats"]
    print(f"  E[log2(T/n)] = {s['mean']:.8f} (theory: {math.log2(3)-2:.8f})")
    print(f"  Var = {s['var']:.8f}, Skew = {s['skewness']:.6f}, Kurt = {s['kurtosis']:.6f}")
    print(f"  Mean deviation from theory: {p1['mean_deviation']:.8f}")
    print("  v2 distribution ratios (empirical/theoretical):")
    for k, info in sorted(p1["v2_distribution"].items(), key=lambda x: int(x[0])):
        if int(k) <= 8:
            print(f"    v2={k}: emp={info['empirical']:.6f}, th={info['theoretical']:.6f}, ratio={info['ratio']:.6f}")

    # Part 2
    print("\n[Part 2] Edgeworth展開によるCLT補正")
    p2 = edgeworth_expansion_analysis(300000)
    all_results["edgeworth"] = p2
    print(f"  kappa3 (skewness) = {p2['kappa3_skewness']:.6f}")
    print(f"  kappa4 (excess kurtosis) = {p2['kappa4_excess_kurtosis']:.6f}")
    print(f"  {'k':>3} {'KS CLT':>10} {'KS Edge':>10} {'Improve':>10}")
    for r in p2["results"]:
        imp = r["improvement_factor"]
        imp_str = f"{imp:.4f}" if imp else "N/A"
        print(f"  {r['k']:>3} {r['ks_clt']:>10.6f} {r['ks_edgeworth']:>10.6f} {imp_str:>10}")

    # Part 3
    print("\n[Part 3] 尾部分布の精密解析")
    p3 = tail_distribution_analysis(500000)
    all_results["tail_distribution"] = p3
    print("  1ステップ尾部比較:")
    print(f"  {'t*sigma':>7} {'Right emp':>12} {'Right norm':>12} {'R ratio':>10} {'Left emp':>12} {'Left norm':>12} {'L ratio':>10}")
    for t in p3["1step_tails"]:
        r_ratio = f"{t['right_ratio']:.4f}" if t['right_ratio'] else "N/A"
        l_ratio = f"{t['left_ratio']:.4f}" if t['left_ratio'] else "N/A"
        print(f"  {t['threshold_sigma']:>7.1f} {t['right_tail_empirical']:>12.6f} {t['right_tail_normal']:>12.6f} {r_ratio:>10} {t['left_tail_empirical']:>12.6f} {t['left_tail_normal']:>12.6f} {l_ratio:>10}")
    print("\n  2ステップ尾部比較:")
    for t in p3["2step_tails"]:
        r_ratio = f"{t['right_ratio']:.4f}" if t['right_ratio'] else "N/A"
        l_ratio = f"{t['left_ratio']:.4f}" if t['left_ratio'] else "N/A"
        print(f"  {t['threshold_sigma']:>7.1f} {t['right_tail_empirical']:>12.6f} {t['right_tail_normal']:>12.6f} {r_ratio:>10} {t['left_tail_empirical']:>12.6f} {t['left_tail_normal']:>12.6f} {l_ratio:>10}")

    # Part 4
    print("\n[Part 4] T^2の分解表現")
    p4 = t2_decomposition(500000)
    all_results["t2_decomposition"] = p4
    print(f"  E[v2_1+v2_2] = {p4['mean_v2_sum']:.6f} (theory: 4.0)")
    print(f"  drift_T2 = {p4['drift_t2']:.6f} (theory: {p4['theoretical_drift_t2']:.6f})")
    print(f"  Corr(v2_1, v2_2) = {p4['v2_correlation_coefficient']:.6f}")
    print(f"  Chi2 for v2_sum distribution = {p4['chi2_statistic']:.4f}")
    print("  v2_sum分布比較:")
    for s_val, info in sorted(p4["v2_sum_distribution"].items(), key=lambda x: int(x[0])):
        if int(s_val) <= 10:
            rd = f"{info['relative_diff']:.6f}" if info['relative_diff'] is not None else "N/A"
            print(f"    sum={s_val}: emp={info['empirical']:.6f}, th={info['theoretical']:.6f}, rel_diff={rd}")

    # Part 5
    print("\n[Part 5] v2のmodular依存性")
    p5 = v2_modular_dependence(300000)
    all_results["v2_modular"] = p5
    for mod_key, info in p5.items():
        print(f"  {mod_key}: chi2 = {info['chi2_statistic']:.4f}, max_dev = {info['max_deviation']:.6f}")

    # Part 6
    print("\n[Part 6] 高精度CLT収束速度")
    p6 = precise_clt_convergence(100000)
    all_results["precise_clt"] = p6
    print(f"  1ステップキュムラント: mu={p6['one_step_cumulants']['mean']:.8f}, var={p6['one_step_cumulants']['var']:.8f}")
    print(f"  {'k':>3} {'KS':>10} {'KS*sqrt(k)':>12} {'Skew':>10} {'Kurt':>10}")
    for r in p6["convergence_data"]:
        print(f"  {r['k']:>3} {r['ks_statistic']:>10.6f} {r['ks_times_sqrt_k']:>12.6f} {r['standardized_skewness']:>10.6f} {r['standardized_kurtosis']:>10.6f}")

    # 総括
    elapsed = time.time() - start_time
    print(f"\n総実行時間: {elapsed:.1f}秒")

    # 主要な発見
    key_findings = {
        "1step_drift_deviation": p1["mean_deviation"],
        "1step_skewness": p1["increment_stats"]["skewness"],
        "1step_kurtosis": p1["increment_stats"]["kurtosis"],
        "v2_correlation": p4["v2_correlation_coefficient"],
        "v2_sum_chi2": p4["chi2_statistic"],
        "edgeworth_improvement_k2": p2["results"][0]["improvement_factor"] if p2["results"] else None,
        "edgeworth_improvement_k10": next((r["improvement_factor"] for r in p2["results"] if r["k"] == 10), None),
        "clt_ks_sqrt_k_limit": [r["ks_times_sqrt_k"] for r in p6["convergence_data"]],
        "tail_heaviness_1step_3sigma_right": next((t["right_ratio"] for t in p3["1step_tails"] if t["threshold_sigma"] == 3), None),
        "tail_heaviness_1step_3sigma_left": next((t["left_ratio"] for t in p3["1step_tails"] if t["threshold_sigma"] == 3), None),
    }
    all_results["key_findings"] = key_findings

    print("\n" + "=" * 70)
    print("主要発見")
    print("=" * 70)
    for k, v in key_findings.items():
        print(f"  {k}: {v}")

    # JSON保存
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return str(obj)
            return round(obj, 10)
        return obj

    results_ser = make_serializable(all_results)
    with open("/Users/soyukke/study/lean-unsolved/results/syr2_clt_deep_analysis.json", "w") as f:
        json.dump(results_ser, f, indent=2)
    print("\n結果を results/syr2_clt_deep_analysis.json に保存しました")

if __name__ == "__main__":
    main()
