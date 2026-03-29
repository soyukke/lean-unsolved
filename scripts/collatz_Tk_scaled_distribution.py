"""
コラッツ予想: T^k(n) / n^{alpha_k} の分布収束の探索
====================================================
alpha_k = (3/4)^k スケーリングで、k=5,10,20 での分布形状を調べる。
純粋 Python 実装 (numpy/scipy 不使用)
"""

import math
import random
import json
import time
import statistics

random.seed(42)

# --- コラッツ関数 (Syracuse形式: 奇数のみ追跡) ---
def collatz_step(n):
    """T(n): 奇数 n に対して (3n+1) を2で割れるだけ割った結果"""
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def collatz_iterate(n, k):
    """T^k(n): k回のSyracuse反復"""
    for _ in range(k):
        n = collatz_step(n)
    return n

def log2(x):
    return math.log2(x) if x > 0 else 0.0

def mean(arr):
    return sum(arr) / len(arr)

def variance(arr, m=None):
    if m is None:
        m = mean(arr)
    return sum((x - m)**2 for x in arr) / len(arr)

def std(arr, m=None):
    return math.sqrt(variance(arr, m))

def skewness(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0:
        return 0.0
    n = len(arr)
    return sum(((x - m)/s)**3 for x in arr) / n

def kurtosis_excess(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0:
        return 0.0
    n = len(arr)
    return sum(((x - m)/s)**4 for x in arr) / n - 3.0

def percentile(arr, p):
    """p は 0-100"""
    sorted_arr = sorted(arr)
    k = (len(sorted_arr) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_arr[int(k)]
    d0 = sorted_arr[int(f)] * (c - k)
    d1 = sorted_arr[int(c)] * (k - f)
    return d0 + d1

def histogram(arr, bins=50):
    """簡易ヒストグラム (密度正規化)"""
    mn = min(arr)
    mx = max(arr)
    if mn == mx:
        return [], []
    bin_width = (mx - mn) / bins
    counts = [0] * bins
    for x in arr:
        idx = int((x - mn) / bin_width)
        if idx >= bins:
            idx = bins - 1
        counts[idx] += 1
    # 密度正規化
    n = len(arr)
    density = [c / (n * bin_width) for c in counts]
    centers = [mn + (i + 0.5) * bin_width for i in range(bins)]
    return centers, density

def ks_test_normal(arr):
    """
    KS検定 (正規分布): 標準化したデータと標準正規分布の最大距離
    """
    m = mean(arr)
    s = std(arr, m)
    if s == 0:
        return 1.0, 0.0
    standardized = sorted([(x - m) / s for x in arr])
    n = len(standardized)
    max_d = 0.0
    for i, x in enumerate(standardized):
        # CDF of standard normal (近似)
        cdf_val = 0.5 * (1 + math.erf(x / math.sqrt(2)))
        ecdf_val = (i + 1) / n
        ecdf_val_prev = i / n
        d = max(abs(ecdf_val - cdf_val), abs(ecdf_val_prev - cdf_val))
        if d > max_d:
            max_d = d
    # p-value 近似 (Kolmogorov-Smirnov)
    sqrt_n = math.sqrt(n)
    lambda_val = (sqrt_n + 0.12 + 0.11/sqrt_n) * max_d
    # Kolmogorov 分布の近似
    if lambda_val <= 0:
        p_val = 1.0
    else:
        p_val = 2 * sum((-1)**(j-1) * math.exp(-2 * j**2 * lambda_val**2) for j in range(1, 101))
        p_val = max(0.0, min(1.0, p_val))
    return max_d, p_val

# --- メイン計算 ---
def compute_scaled_distribution(N_samples, k_values, n_range_start, n_range_end):
    """
    Y_k(n) = log2(T^k(n)) - alpha_k * log2(n) を計算
    alpha_k = (3/4)^k
    """
    results = {}

    # 奇数サンプルを生成
    odd_numbers = list(range(n_range_start if n_range_start % 2 == 1 else n_range_start + 1,
                             n_range_end + 1, 2))
    if len(odd_numbers) > N_samples:
        odd_numbers = random.sample(odd_numbers, N_samples)
        odd_numbers.sort()

    actual_N = len(odd_numbers)
    print(f"サンプル数: {actual_N}, 範囲: [{n_range_start}, {n_range_end}]")

    for k in k_values:
        alpha_k = (3/4) ** k
        print(f"\n--- k={k}, alpha_k={alpha_k:.10f} ---")
        t0 = time.time()

        Y_values = []

        for i, n in enumerate(odd_numbers):
            Tk_n = collatz_iterate(n, k)
            log2_Tk = log2(Tk_n)
            log2_n = log2(n)
            Y = log2_Tk - alpha_k * log2_n
            Y_values.append(Y)

            if (i+1) % 5000 == 0:
                print(f"  進捗: {i+1}/{actual_N}")

        elapsed = time.time() - t0

        # 統計量
        mean_Y = mean(Y_values)
        std_Y = std(Y_values, mean_Y)
        skew_Y = skewness(Y_values)
        kurt_Y = kurtosis_excess(Y_values)
        median_Y = statistics.median(Y_values)

        ks_stat, ks_pval = ks_test_normal(Y_values)

        results[k] = {
            'alpha_k': alpha_k,
            'mean': mean_Y,
            'std': std_Y,
            'variance': std_Y**2,
            'skewness': skew_Y,
            'kurtosis_excess': kurt_Y,
            'median': median_Y,
            'min': min(Y_values),
            'max': max(Y_values),
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval,
            'elapsed_sec': elapsed,
            'percentiles': {
                '1%': percentile(Y_values, 1),
                '5%': percentile(Y_values, 5),
                '25%': percentile(Y_values, 25),
                '75%': percentile(Y_values, 75),
                '95%': percentile(Y_values, 95),
                '99%': percentile(Y_values, 99),
            },
        }

        print(f"  計算時間: {elapsed:.2f}秒")
        print(f"  mean(Y) = {mean_Y:.6f}")
        print(f"  std(Y)  = {std_Y:.6f}")
        print(f"  var(Y)  = {std_Y**2:.6f}")
        print(f"  skew    = {skew_Y:.6f}")
        print(f"  kurtosis(excess) = {kurt_Y:.6f}")
        print(f"  median  = {median_Y:.6f}")
        print(f"  KS stat = {ks_stat:.6f}, p = {ks_pval:.6e}")

    return results

# --- 最適スケーリング ---
def explore_optimal_scaling(N_samples, k_values, n_range_start, n_range_end):
    """
    log2(T^k(n)) = beta_k * log2(n) + c_k + noise の線形回帰
    """
    odd_numbers = list(range(n_range_start if n_range_start % 2 == 1 else n_range_start + 1,
                             n_range_end + 1, 2))
    if len(odd_numbers) > N_samples:
        odd_numbers = random.sample(odd_numbers, N_samples)
        odd_numbers.sort()

    results = {}

    for k in k_values:
        alpha_k_theoretical = (3/4) ** k
        print(f"\n=== 最適スケーリング探索 k={k} ===")

        log2_n_arr = [log2(n) for n in odd_numbers]
        log2_Tk_arr = [log2(collatz_iterate(n, k)) for n in odd_numbers]

        # 線形回帰 (最小二乗法)
        n_pts = len(log2_n_arr)
        sum_x = sum(log2_n_arr)
        sum_y = sum(log2_Tk_arr)
        sum_xy = sum(x*y for x, y in zip(log2_n_arr, log2_Tk_arr))
        sum_x2 = sum(x*x for x in log2_n_arr)

        beta_fit = (n_pts * sum_xy - sum_x * sum_y) / (n_pts * sum_x2 - sum_x**2)
        c_fit = (sum_y - beta_fit * sum_x) / n_pts

        # 残差
        residuals = [y - (beta_fit * x + c_fit) for x, y in zip(log2_n_arr, log2_Tk_arr)]
        residual_std_val = std(residuals)

        print(f"  理論 alpha_k = {alpha_k_theoretical:.10f}")
        print(f"  回帰 beta_k  = {beta_fit:.10f}")
        print(f"  差分          = {beta_fit - alpha_k_theoretical:.10e}")
        print(f"  切片 c_k      = {c_fit:.6f}")
        print(f"  残差 std      = {residual_std_val:.6f}")

        results[k] = {
            'alpha_k_theoretical': alpha_k_theoretical,
            'beta_k_fitted': beta_fit,
            'difference': beta_fit - alpha_k_theoretical,
            'intercept': c_fit,
            'residual_std': residual_std_val,
        }

    return results

# --- n スケール依存性 ---
def convergence_with_n_scale(k, n_scales, samples_per_scale=3000):
    """n のスケールを変えた時の Y_k 分布の変化"""
    print(f"\n=== n スケール依存性 (k={k}) ===")
    results = []
    alpha_k = (3/4) ** k

    for scale in n_scales:
        n_start = scale
        n_end = scale * 2
        odd_numbers = list(range(n_start if n_start % 2 == 1 else n_start + 1,
                                 n_end + 1, 2))
        if len(odd_numbers) > samples_per_scale:
            odd_numbers = random.sample(odd_numbers, samples_per_scale)

        Y_values = []
        for n in odd_numbers:
            Tk_n = collatz_iterate(n, k)
            Y = log2(Tk_n) - alpha_k * log2(n)
            Y_values.append(Y)

        mean_Y = mean(Y_values)
        std_Y = std(Y_values, mean_Y)
        skew_Y = skewness(Y_values)
        kurt_Y = kurtosis_excess(Y_values)

        log_scale = int(math.log10(scale))
        print(f"  scale=10^{log_scale}: mean={mean_Y:.4f}, std={std_Y:.4f}, skew={skew_Y:.4f}, kurt={kurt_Y:.4f}")
        results.append({
            'scale': scale,
            'log10_scale': log_scale,
            'mean': mean_Y,
            'std': std_Y,
            'skewness': skew_Y,
            'kurtosis_excess': kurt_Y,
        })

    return results

# --- ステップごとの分布進化 ---
def step_by_step_evolution(N_samples, n_start, n_end):
    """k=1..20 でのY_k分布進化"""
    print("\n=== ステップごとの分布進化 ===")
    odd_numbers = list(range(n_start if n_start % 2 == 1 else n_start + 1,
                             n_end + 1, 2))
    if len(odd_numbers) > N_samples:
        odd_numbers = random.sample(odd_numbers, N_samples)
        odd_numbers.sort()

    results = []
    all_k = list(range(1, 21))

    current_values = {n: n for n in odd_numbers}
    log2_n_arr = [log2(n) for n in odd_numbers]

    for k in all_k:
        alpha_k = (3/4) ** k

        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        Y_values = []
        for i, n in enumerate(odd_numbers):
            Tk_n = current_values[n]
            Y = log2(Tk_n) - alpha_k * log2_n_arr[i]
            Y_values.append(Y)

        mean_Y = mean(Y_values)
        std_Y = std(Y_values, mean_Y)
        skew_Y = skewness(Y_values)
        kurt_Y = kurtosis_excess(Y_values)
        ks_stat, ks_pval = ks_test_normal(Y_values)

        results.append({
            'k': k,
            'alpha_k': alpha_k,
            'mean': mean_Y,
            'std': std_Y,
            'skewness': skew_Y,
            'kurtosis_excess': kurt_Y,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval,
        })

        if k in [1, 2, 3, 5, 10, 15, 20]:
            print(f"  k={k:2d}: mean={mean_Y:.4f}, std={std_Y:.4f}, skew={skew_Y:.4f}, kurt={kurt_Y:.4f}, KS={ks_stat:.4f} (p={ks_pval:.3e})")

    return results

# --- 別スケーリング: log2(T^k(n)/n) / sqrt(k) ---
def alternative_clt_scaling(N_samples, k_values, n_start, n_end):
    """
    CLT的スケーリング: Z_k(n) = [log2(T^k(n)) - n*mu_k] / (sigma * sqrt(k))
    ここで mu_k は1ステップあたりの平均 log 変化 = E[log2(T/n)] = -0.415
    sigma^2 = Var[log2(T/n)] = 2.0
    """
    print("\n=== 代替CLTスケーリング: [log2(T^k(n)/n) - k*mu] / (sigma*sqrt(k)) ===")
    mu = -0.415   # E[log2(T/n)] per step
    sigma2 = 2.0  # Var per step

    odd_numbers = list(range(n_start if n_start % 2 == 1 else n_start + 1,
                             n_end + 1, 2))
    if len(odd_numbers) > N_samples:
        odd_numbers = random.sample(odd_numbers, N_samples)
        odd_numbers.sort()

    results = {}

    for k in k_values:
        print(f"\n  k={k}:")
        Z_values = []
        for n in odd_numbers:
            Tk_n = collatz_iterate(n, k)
            # log2(T^k(n)) - log2(n) = log2(T^k(n)/n)
            log_ratio = log2(Tk_n) - log2(n)
            # CLT scaling
            Z = (log_ratio - k * mu) / math.sqrt(sigma2 * k)
            Z_values.append(Z)

        mean_Z = mean(Z_values)
        std_Z = std(Z_values, mean_Z)
        skew_Z = skewness(Z_values)
        kurt_Z = kurtosis_excess(Z_values)
        ks_stat, ks_pval = ks_test_normal(Z_values)

        print(f"    mean(Z) = {mean_Z:.6f} (理論: 0)")
        print(f"    std(Z)  = {std_Z:.6f} (理論: 1)")
        print(f"    skew    = {skew_Z:.6f} (理論: 0)")
        print(f"    kurt    = {kurt_Z:.6f} (理論: 0)")
        print(f"    KS stat = {ks_stat:.6f}, p = {ks_pval:.6e}")

        results[k] = {
            'mean': mean_Z,
            'std': std_Z,
            'skewness': skew_Z,
            'kurtosis_excess': kurt_Z,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval,
        }

    return results

# --- E[log2(T/n)] と Var[log2(T/n)] の直接計測 ---
def measure_single_step_statistics(N_samples, n_start, n_end):
    """1ステップの統計量を直接計測して既知値と比較"""
    print("\n=== 1ステップ統計量の直接計測 ===")
    odd_numbers = list(range(n_start if n_start % 2 == 1 else n_start + 1,
                             n_end + 1, 2))
    if len(odd_numbers) > N_samples:
        odd_numbers = random.sample(odd_numbers, N_samples)

    log_ratios = []
    for n in odd_numbers:
        Tn = collatz_step(n)
        log_ratios.append(log2(Tn) - log2(n))

    m = mean(log_ratios)
    v = variance(log_ratios, m)
    s = math.sqrt(v)
    sk = skewness(log_ratios)
    ku = kurtosis_excess(log_ratios)

    print(f"  E[log2(T/n)]   = {m:.6f} (既知値: -0.415)")
    print(f"  Var[log2(T/n)] = {v:.6f} (既知値: ~2.0)")
    print(f"  Std            = {s:.6f}")
    print(f"  Skewness       = {sk:.6f}")
    print(f"  Kurtosis(exc)  = {ku:.6f}")

    return {
        'mean': m,
        'variance': v,
        'std': s,
        'skewness': sk,
        'kurtosis_excess': ku,
    }


if __name__ == '__main__':
    print("=" * 60)
    print("コラッツ予想: T^k(n)/n^{alpha_k} の分布収束探索")
    print("=" * 60)

    N_SAMPLES = 15000
    K_VALUES = [5, 10, 20]
    N_START = 10**6 + 1
    N_END = 10**6 + 200000

    # 0. 1ステップ統計量の検証
    print("\n" + "=" * 60)
    print("Phase 0: 1ステップ統計量の直接計測")
    print("=" * 60)
    single_step = measure_single_step_statistics(N_SAMPLES, N_START, N_END)

    # 1. メイン分布計算
    print("\n" + "=" * 60)
    print("Phase 1: Y_k(n) = log2(T^k(n)) - alpha_k*log2(n) の分布")
    print("=" * 60)
    dist_results = compute_scaled_distribution(N_SAMPLES, K_VALUES, N_START, N_END)

    # 2. 最適スケーリング探索
    print("\n" + "=" * 60)
    print("Phase 2: 最適スケーリング beta_k の回帰推定")
    print("=" * 60)
    scaling_results = explore_optimal_scaling(N_SAMPLES, K_VALUES, N_START, N_END)

    # 3. n スケール依存性
    print("\n" + "=" * 60)
    print("Phase 3: n のスケール依存性")
    print("=" * 60)
    n_scales = [10**4, 10**5, 10**6, 10**7]
    scale_results_k5 = convergence_with_n_scale(5, n_scales, samples_per_scale=3000)
    scale_results_k10 = convergence_with_n_scale(10, n_scales, samples_per_scale=3000)

    # 4. ステップごとの分布進化
    print("\n" + "=" * 60)
    print("Phase 4: ステップごとの分布進化 (k=1..20)")
    print("=" * 60)
    evolution_results = step_by_step_evolution(N_SAMPLES, N_START, N_END)

    # 5. 代替CLTスケーリング
    print("\n" + "=" * 60)
    print("Phase 5: 代替CLTスケーリング Z_k = [log2(T^k/n) - k*mu] / (sigma*sqrt(k))")
    print("=" * 60)
    alt_clt = alternative_clt_scaling(N_SAMPLES, K_VALUES, N_START, N_END)

    # --- まとめ ---
    print("\n" + "=" * 60)
    print("まとめ")
    print("=" * 60)

    summary_dist = {}
    for k in K_VALUES:
        d = dist_results[k]
        summary_dist[str(k)] = {
            'alpha_k': d['alpha_k'],
            'mean': round(d['mean'], 6),
            'std': round(d['std'], 6),
            'variance': round(d['variance'], 6),
            'skewness': round(d['skewness'], 6),
            'kurtosis_excess': round(d['kurtosis_excess'], 6),
            'ks_statistic': round(d['ks_statistic'], 6),
            'ks_pvalue': d['ks_pvalue'],
            'percentiles': {k2: round(v, 4) for k2, v in d['percentiles'].items()},
        }

    evolution_summary = []
    for r in evolution_results:
        evolution_summary.append({
            'k': r['k'],
            'mean': round(r['mean'], 4),
            'std': round(r['std'], 4),
            'skewness': round(r['skewness'], 4),
            'kurtosis_excess': round(r['kurtosis_excess'], 4),
            'ks_statistic': round(r['ks_statistic'], 4),
            'ks_pvalue': r['ks_pvalue'],
        })

    output = {
        'single_step_statistics': {k: round(v, 6) for k, v in single_step.items()},
        'distribution_at_k5_k10_k20': summary_dist,
        'optimal_scaling': {str(k): {k2: round(v, 10) if isinstance(v, float) else v for k2, v in vv.items()} for k, vv in scaling_results.items()},
        'n_scale_dependence': {
            'k5': [{k2: round(v, 4) if isinstance(v, float) else v for k2, v in r.items()} for r in scale_results_k5],
            'k10': [{k2: round(v, 4) if isinstance(v, float) else v for k2, v in r.items()} for r in scale_results_k10],
        },
        'step_evolution_k1_to_k20': evolution_summary,
        'alternative_clt_scaling': {str(k): {k2: round(v, 6) for k2, v in vv.items()} for k, vv in alt_clt.items()},
    }

    with open('/Users/soyukke/study/lean-unsolved/results/Tk_scaled_distribution.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n結果を results/Tk_scaled_distribution.json に保存しました。")
    print("完了。")
