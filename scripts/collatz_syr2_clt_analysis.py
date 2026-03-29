#!/usr/bin/env python3
"""
加速Syracuse Syr^2 のランダムウォーク表現と中心極限定理(CLT)近似精度評価

目的:
  1. T^2(n) = T(T(n)) の対数増分 log2(T^2(n)/n) の分布を実軌道から収集
  2. 理論的なE, Varの計算と実データとの比較
  3. CLT近似(正規分布)の精度をKS検定・KL divergenceで定量化
  4. Berry-Esseen的な収束速度の実測
  5. 2ステップ相関の影響評価

理論:
  log2(T(n)/n) ≈ log2(3) - v2(3n+1) （奇数nに対して）
  E[log2(T(n)/n)] = log2(3) - E[v2] ≈ 1.585 - 2 = -0.415
  T^2(n) = T(T(n)) なので log2(T^2(n)/n) = log2(T(T(n))/T(n)) + log2(T(n)/n)
  = 2ステップの対数増分の和

  CLT: S_k = sum of log increments → Normal(k*mu, k*sigma^2) as k→∞
  ここで mu = E[log2(T/n)], sigma^2 = Var[log2(T/n)]
"""

import math
import random
import time
import json
from collections import Counter, defaultdict

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse map for odd n: Syr(n) = (3n+1)/2^{v2(3n+1)}"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def syracuse2(n):
    """2-step Syracuse: T^2(n) = T(T(n)) for odd n"""
    return syracuse(syracuse(n))

# ============================================================
# Part 1: 1ステップ対数増分の分布収集
# ============================================================

def collect_1step_increments(N_samples, max_val=10**7):
    """奇数nに対するlog2(T(n)/n)を収集"""
    increments = []
    v2_vals = []
    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        tn = syracuse(n)
        inc = math.log2(tn / n)
        increments.append(inc)
        v2_vals.append(v2(3 * n + 1))
    return increments, v2_vals

# ============================================================
# Part 2: 2ステップ対数増分の分布収集
# ============================================================

def collect_2step_increments(N_samples, max_val=10**7):
    """奇数nに対するlog2(T^2(n)/n)を収集"""
    increments_2step = []
    inc1_list = []
    inc2_list = []
    v2_1_list = []
    v2_2_list = []

    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t2 = syracuse(t1)

        inc1 = math.log2(t1 / n)
        inc2 = math.log2(t2 / t1)
        inc_total = math.log2(t2 / n)

        increments_2step.append(inc_total)
        inc1_list.append(inc1)
        inc2_list.append(inc2)
        v2_1_list.append(v2(3 * n + 1))
        v2_2_list.append(v2(3 * t1 + 1))

    return increments_2step, inc1_list, inc2_list, v2_1_list, v2_2_list

# ============================================================
# Part 3: 統計量計算
# ============================================================

def compute_stats(data):
    """平均、分散、歪度、尖度を計算"""
    n = len(data)
    mu = sum(data) / n
    var = sum((x - mu)**2 for x in data) / n
    sigma = math.sqrt(var) if var > 0 else 1e-15
    skew = sum(((x - mu) / sigma)**3 for x in data) / n
    kurt = sum(((x - mu) / sigma)**4 for x in data) / n - 3  # excess kurtosis
    return {"mean": mu, "var": var, "std": sigma, "skewness": skew, "kurtosis": kurt}

def correlation(x, y):
    """ピアソン相関"""
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n)) / n
    sx = math.sqrt(sum((xi - mx)**2 for xi in x) / n)
    sy = math.sqrt(sum((yi - my)**2 for yi in y) / n)
    if sx == 0 or sy == 0:
        return 0
    return cov / (sx * sy)

# ============================================================
# Part 4: CLT近似精度 - KS統計量
# ============================================================

def ks_test_normal(data):
    """正規分布とのKolmogorov-Smirnov統計量"""
    n = len(data)
    stats = compute_stats(data)
    mu, sigma = stats["mean"], stats["std"]

    sorted_data = sorted(data)
    ks_stat = 0
    for i, x in enumerate(sorted_data):
        z = (x - mu) / sigma
        # Phi(z) via erf
        cdf_val = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        ecdf_val = (i + 1) / n
        ecdf_val_prev = i / n
        ks_stat = max(ks_stat, abs(ecdf_val - cdf_val), abs(ecdf_val_prev - cdf_val))

    return ks_stat

# ============================================================
# Part 5: CLT近似精度 - ヒストグラム比較
# ============================================================

def histogram_comparison(data, n_bins=100):
    """正規分布との比較ヒストグラム"""
    stats = compute_stats(data)
    mu, sigma = stats["mean"], stats["std"]
    n = len(data)

    lo = mu - 4 * sigma
    hi = mu + 4 * sigma
    bin_width = (hi - lo) / n_bins

    # 実データヒストグラム
    hist = [0] * n_bins
    for x in data:
        idx = int((x - lo) / bin_width)
        if 0 <= idx < n_bins:
            hist[idx] += 1

    # 正規分布理論値
    kl_div = 0
    total_deviation = 0
    max_deviation = 0

    for i in range(n_bins):
        x_center = lo + (i + 0.5) * bin_width
        z = (x_center - mu) / sigma
        p_normal = math.exp(-0.5 * z**2) / (sigma * math.sqrt(2 * math.pi)) * bin_width
        p_empirical = hist[i] / n

        deviation = abs(p_empirical - p_normal)
        total_deviation += deviation
        max_deviation = max(max_deviation, deviation)

        if p_empirical > 0 and p_normal > 0:
            kl_div += p_empirical * math.log(p_empirical / p_normal)

    return {
        "kl_divergence": kl_div,
        "total_variation": total_deviation / 2,
        "max_bin_deviation": max_deviation,
    }

# ============================================================
# Part 6: k-ステップ和のCLT収束速度
# ============================================================

def kstep_clt_convergence(max_k=20, N_per_k=50000, max_val=10**6):
    """
    S_k = sum_{i=1}^{k} log2(T(n_i)/n_i) の分布がCLTに収束する速度を測定
    実際の軌道上での和を使う
    """
    results = []

    for k in [1, 2, 3, 4, 5, 8, 10, 15, 20]:
        sums = []
        for _ in range(N_per_k):
            n = random.randint(1, max_val)
            if n % 2 == 0:
                n += 1
            s = 0
            valid = True
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
                if n <= 1:
                    valid = False
                    break
            if valid:
                sums.append(s)

        if len(sums) < 100:
            continue

        stats = compute_stats(sums)
        ks = ks_test_normal(sums)
        hist_comp = histogram_comparison(sums, n_bins=80)

        results.append({
            "k": k,
            "n_samples": len(sums),
            "mean": stats["mean"],
            "expected_mean": k * (math.log2(3) - 2),
            "var": stats["var"],
            "std": stats["std"],
            "skewness": stats["skewness"],
            "kurtosis": stats["kurtosis"],
            "ks_statistic": ks,
            "kl_divergence": hist_comp["kl_divergence"],
            "total_variation": hist_comp["total_variation"],
        })

    return results

# ============================================================
# Part 7: 連続2ステップの相関分析
# ============================================================

def consecutive_step_correlation(N_samples=200000, max_val=10**7):
    """連続するステップ間のlog増分の相関"""
    inc_pairs = []

    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t2 = syracuse(t1)

        if t1 > 0 and t2 > 0:
            inc1 = math.log2(t1 / n)
            inc2 = math.log2(t2 / t1)
            inc_pairs.append((inc1, inc2))

    inc1_list = [p[0] for p in inc_pairs]
    inc2_list = [p[1] for p in inc_pairs]

    corr = correlation(inc1_list, inc2_list)

    # 条件付き分布: inc1の値で分けた時のinc2の統計
    # inc1を四分位で分割
    sorted_inc1 = sorted(inc1_list)
    q1 = sorted_inc1[len(sorted_inc1) // 4]
    q2 = sorted_inc1[len(sorted_inc1) // 2]
    q3 = sorted_inc1[3 * len(sorted_inc1) // 4]

    conditional_stats = {}
    for label, lo, hi in [("Q1", -999, q1), ("Q2", q1, q2), ("Q3", q2, q3), ("Q4", q3, 999)]:
        subset = [inc2_list[i] for i in range(len(inc1_list)) if lo <= inc1_list[i] < hi]
        if len(subset) > 10:
            conditional_stats[label] = compute_stats(subset)

    return {
        "correlation_inc1_inc2": corr,
        "n_samples": len(inc_pairs),
        "inc1_stats": compute_stats(inc1_list),
        "inc2_stats": compute_stats(inc2_list),
        "conditional_inc2_given_inc1": conditional_stats,
    }

# ============================================================
# Part 8: v2連続値の条件付き分布
# ============================================================

def v2_conditional_distribution(N_samples=500000, max_val=10**7):
    """v2(3*T(n)+1) の v2(3n+1) への条件付き依存"""
    pairs = defaultdict(list)

    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        v1 = v2(3 * n + 1)
        v2_val = v2(3 * t1 + 1)
        pairs[v1].append(v2_val)

    result = {}
    for k in sorted(pairs.keys()):
        if len(pairs[k]) >= 50:
            vals = pairs[k]
            mean_v2 = sum(vals) / len(vals)
            var_v2 = sum((x - mean_v2)**2 for x in vals) / len(vals)
            counter = Counter(vals)
            dist = {str(v): c / len(vals) for v, c in sorted(counter.items())[:10]}
            result[str(k)] = {
                "count": len(vals),
                "mean_v2_next": mean_v2,
                "var_v2_next": var_v2,
                "distribution": dist,
            }

    return result

# ============================================================
# Part 9: Berry-Esseen bound 実測
# ============================================================

def berry_esseen_analysis(N_samples=200000, max_val=10**7):
    """
    Berry-Esseen定理: |F_n(x) - Phi(x)| <= C * rho / (sigma^3 * sqrt(n))
    ここで rho = E[|X - mu|^3]

    kステップ和 S_k について実際の最大偏差を測定し、
    理論的Berry-Esseen上界と比較
    """
    # まず1ステップ増分の3次絶対モーメントを計算
    increments = []
    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        tn = syracuse(n)
        increments.append(math.log2(tn / n))

    stats = compute_stats(increments)
    mu = stats["mean"]
    sigma = stats["std"]
    rho = sum(abs(x - mu)**3 for x in increments) / len(increments)  # E[|X-mu|^3]

    # C_BE ≈ 0.4748 (Shevtsova 2011 の最良定数)
    C_BE = 0.4748

    # 各kでの実際のsup偏差
    be_results = []
    for k in [2, 3, 5, 8, 10, 15, 20, 30, 50]:
        sums = []
        for _ in range(min(N_samples, 100000)):
            n = random.randint(1, max_val)
            if n % 2 == 0:
                n += 1
            s = 0
            valid = True
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
                if n <= 1:
                    valid = False
                    break
            if valid:
                sums.append(s)

        if len(sums) < 100:
            continue

        # 標準化
        expected_mean = k * mu
        expected_std = sigma * math.sqrt(k)
        standardized = [(s - expected_mean) / expected_std for s in sums]

        # KS統計量（標準正規との比較）
        sorted_z = sorted(standardized)
        n_z = len(sorted_z)
        ks_actual = 0
        for i, z in enumerate(sorted_z):
            cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ecdf = (i + 1) / n_z
            ecdf_prev = i / n_z
            ks_actual = max(ks_actual, abs(ecdf - cdf), abs(ecdf_prev - cdf))

        be_bound = C_BE * rho / (sigma**3 * math.sqrt(k))

        be_results.append({
            "k": k,
            "n_samples": len(sums),
            "ks_actual": ks_actual,
            "berry_esseen_bound": be_bound,
            "ratio_actual_to_bound": ks_actual / be_bound if be_bound > 0 else None,
            "mean_deviation": abs(sum(sums) / len(sums) - expected_mean),
            "std_deviation": abs(math.sqrt(sum((s - sum(sums)/len(sums))**2 for s in sums)/len(sums)) - expected_std),
        })

    return {
        "one_step_stats": {
            "mean": mu,
            "std": sigma,
            "rho_third_abs_moment": rho,
            "skewness": stats["skewness"],
            "kurtosis": stats["kurtosis"],
        },
        "berry_esseen_results": be_results,
    }

# ============================================================
# Part 10: T^2の直接的分布解析
# ============================================================

def t2_direct_analysis(N_samples=300000, max_val=10**7):
    """T^2(n)の対数増分を直接解析し、2*muとの偏差、独立和モデルとの比較"""
    t2_incs = []
    v2_sum_list = []

    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t2 = syracuse(t1)

        inc = math.log2(t2 / n)
        t2_incs.append(inc)
        v2_sum_list.append(v2(3 * n + 1) + v2(3 * t1 + 1))

    stats_t2 = compute_stats(t2_incs)

    # 理論値（独立仮定）
    mu1 = math.log2(3) - 2
    var1_theoretical = 2  # Var[v2] = 2 for geometric(1/2) starting at 1

    expected_mean_2step = 2 * mu1
    # 独立仮定のvar: 2 * var1
    # 実際のvar1を使う

    # v2の和の分布
    v2_sum_stats = compute_stats([float(v) for v in v2_sum_list])

    # KS検定
    ks = ks_test_normal(t2_incs)
    hist_comp = histogram_comparison(t2_incs)

    # 独立仮定との比較: 実際の分散 vs 2*Var[1step]
    # 1ステップ増分も集めて比較
    inc1_list_for_var = []
    for _ in range(N_samples):
        n = random.randint(1, max_val)
        if n % 2 == 0:
            n += 1
        inc1_list_for_var.append(math.log2(syracuse(n) / n))

    var_1step = compute_stats(inc1_list_for_var)["var"]

    return {
        "t2_increment_stats": stats_t2,
        "theoretical_mean_indep": expected_mean_2step,
        "mean_deviation_from_theory": stats_t2["mean"] - expected_mean_2step,
        "var_1step_empirical": var_1step,
        "var_2step_empirical": stats_t2["var"],
        "var_ratio_2step_to_2x1step": stats_t2["var"] / (2 * var_1step) if var_1step > 0 else None,
        "v2_sum_stats": v2_sum_stats,
        "ks_statistic": ks,
        "kl_divergence": hist_comp["kl_divergence"],
        "total_variation": hist_comp["total_variation"],
    }

# ============================================================
# メイン実行
# ============================================================

def main():
    start_time = time.time()
    results = {}

    print("=" * 70)
    print("加速Syracuse Syr^2 のランダムウォーク表現とCLT近似精度評価")
    print("=" * 70)

    # --- Part A: 1ステップ分布 ---
    print("\n[Part A] 1ステップ対数増分の分布...")
    inc1, v2_1 = collect_1step_increments(500000)
    stats1 = compute_stats(inc1)
    ks1 = ks_test_normal(inc1)
    hist1 = histogram_comparison(inc1)
    v2_stats = compute_stats([float(v) for v in v2_1])

    results["1step"] = {
        "stats": stats1,
        "ks_statistic": ks1,
        "histogram_comparison": hist1,
        "v2_stats": v2_stats,
        "theoretical_mean": math.log2(3) - 2,
        "theoretical_v2_mean": 2.0,
        "theoretical_v2_var": 2.0,
    }
    print(f"  E[log2(T/n)] = {stats1['mean']:.6f} (theory: {math.log2(3)-2:.6f})")
    print(f"  Var = {stats1['var']:.6f}, Std = {stats1['std']:.6f}")
    print(f"  Skewness = {stats1['skewness']:.6f}, Kurtosis = {stats1['kurtosis']:.6f}")
    print(f"  E[v2] = {v2_stats['mean']:.6f} (theory: 2.0)")
    print(f"  KS statistic = {ks1:.6f}")

    # --- Part B: 2ステップ分布 ---
    print("\n[Part B] 2ステップ対数増分 T^2 の分布...")
    t2_result = t2_direct_analysis(300000)
    results["2step_direct"] = t2_result

    s = t2_result["t2_increment_stats"]
    print(f"  E[log2(T^2/n)] = {s['mean']:.6f} (theory indep: {t2_result['theoretical_mean_indep']:.6f})")
    print(f"  Var[2step] = {s['var']:.6f}")
    print(f"  2*Var[1step] = {2*t2_result['var_1step_empirical']:.6f}")
    print(f"  Var ratio (2step / 2*1step) = {t2_result['var_ratio_2step_to_2x1step']:.6f}")
    print(f"  Skewness = {s['skewness']:.6f}, Kurtosis = {s['kurtosis']:.6f}")
    print(f"  KS statistic = {t2_result['ks_statistic']:.6f}")
    print(f"  KL divergence = {t2_result['kl_divergence']:.6f}")

    # --- Part C: 連続ステップ相関 ---
    print("\n[Part C] 連続ステップ間の相関...")
    corr_result = consecutive_step_correlation(200000)
    results["step_correlation"] = corr_result

    print(f"  Corr(inc1, inc2) = {corr_result['correlation_inc1_inc2']:.6f}")
    print("  Conditional E[inc2 | inc1 quartile]:")
    for q, st in corr_result["conditional_inc2_given_inc1"].items():
        print(f"    {q}: E = {st['mean']:.6f}, Var = {st['var']:.6f}")

    # --- Part D: v2条件付き分布 ---
    print("\n[Part D] v2 条件付き分布...")
    v2_cond = v2_conditional_distribution(300000)
    results["v2_conditional"] = v2_cond

    for k, info in sorted(v2_cond.items(), key=lambda x: int(x[0])):
        if int(k) <= 6:
            print(f"  v2_prev={k}: E[v2_next]={info['mean_v2_next']:.4f} (theory indep: 2.0), count={info['count']}")

    # --- Part E: CLT収束速度 ---
    print("\n[Part E] k-ステップ和のCLT収束速度...")
    clt_results = kstep_clt_convergence(max_k=20, N_per_k=80000)
    results["clt_convergence"] = clt_results

    print(f"  {'k':>3} {'KS stat':>10} {'Skew':>10} {'Kurt':>10} {'KL div':>10}")
    for r in clt_results:
        print(f"  {r['k']:>3} {r['ks_statistic']:>10.6f} {r['skewness']:>10.6f} {r['kurtosis']:>10.6f} {r['kl_divergence']:>10.6f}")

    # --- Part F: Berry-Esseen分析 ---
    print("\n[Part F] Berry-Esseen bound 実測...")
    be_result = berry_esseen_analysis(100000)
    results["berry_esseen"] = be_result

    print(f"  3rd abs moment (rho) = {be_result['one_step_stats']['rho_third_abs_moment']:.6f}")
    print(f"  {'k':>3} {'KS actual':>12} {'BE bound':>12} {'ratio':>10}")
    for r in be_result["berry_esseen_results"]:
        ratio_str = f"{r['ratio_actual_to_bound']:.4f}" if r['ratio_actual_to_bound'] else "N/A"
        print(f"  {r['k']:>3} {r['ks_actual']:>12.6f} {r['berry_esseen_bound']:>12.6f} {ratio_str:>10}")

    # --- 総括 ---
    elapsed = time.time() - start_time
    print(f"\n総実行時間: {elapsed:.1f}秒")

    # 主要な発見のまとめ
    summary = {
        "drift_per_step": stats1["mean"],
        "drift_per_2step": t2_result["t2_increment_stats"]["mean"],
        "var_ratio_2step": t2_result["var_ratio_2step_to_2x1step"],
        "step_correlation": corr_result["correlation_inc1_inc2"],
        "clt_ks_at_k2": next((r["ks_statistic"] for r in clt_results if r["k"] == 2), None),
        "clt_ks_at_k10": next((r["ks_statistic"] for r in clt_results if r["k"] == 10), None),
        "clt_ks_at_k20": next((r["ks_statistic"] for r in clt_results if r["k"] == 20), None),
        "skewness_1step": stats1["skewness"],
        "kurtosis_1step": stats1["kurtosis"],
        "be_ratio_at_k10": next((r["ratio_actual_to_bound"] for r in be_result["berry_esseen_results"] if r["k"] == 10), None),
    }
    results["summary"] = summary

    print("\n" + "=" * 70)
    print("主要結果サマリー")
    print("=" * 70)
    print(f"  1ステップドリフト: {summary['drift_per_step']:.6f} (theory: {math.log2(3)-2:.6f})")
    print(f"  2ステップドリフト: {summary['drift_per_2step']:.6f} (theory: {2*(math.log2(3)-2):.6f})")
    print(f"  分散比(2step/2*1step): {summary['var_ratio_2step']:.6f}")
    print(f"  連続ステップ相関: {summary['step_correlation']:.6f}")
    print(f"  CLT KS at k=2: {summary['clt_ks_at_k2']}")
    print(f"  CLT KS at k=10: {summary['clt_ks_at_k10']}")
    print(f"  CLT KS at k=20: {summary['clt_ks_at_k20']}")
    print(f"  1ステップ歪度: {summary['skewness_1step']:.6f}")
    print(f"  1ステップ尖度: {summary['kurtosis_1step']:.6f}")

    # JSON保存
    # floatをシリアライズ可能に変換
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

    results_ser = make_serializable(results)

    with open("/Users/soyukke/study/lean-unsolved/results/syr2_clt_analysis.json", "w") as f:
        json.dump(results_ser, f, indent=2)
    print("\n結果を results/syr2_clt_analysis.json に保存しました")

if __name__ == "__main__":
    main()
