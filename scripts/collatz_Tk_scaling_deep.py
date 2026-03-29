"""
深掘り分析: 分散のスケーリング則と正規収束の速度
"""

import math
import random
import json
import time

random.seed(42)

def collatz_step(n):
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def collatz_iterate(n, k):
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
    return sum(((x - m)/s)**3 for x in arr) / len(arr)

def kurtosis_excess(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0:
        return 0.0
    return sum(((x - m)/s)**4 for x in arr) / len(arr) - 3.0

def ks_test_normal(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0:
        return 1.0, 0.0
    standardized = sorted([(x - m) / s for x in arr])
    n = len(standardized)
    max_d = 0.0
    for i, x in enumerate(standardized):
        cdf_val = 0.5 * (1 + math.erf(x / math.sqrt(2)))
        ecdf_val = (i + 1) / n
        ecdf_val_prev = i / n
        d = max(abs(ecdf_val - cdf_val), abs(ecdf_val_prev - cdf_val))
        if d > max_d:
            max_d = d
    sqrt_n = math.sqrt(n)
    lambda_val = (sqrt_n + 0.12 + 0.11/sqrt_n) * max_d
    if lambda_val <= 0:
        p_val = 1.0
    else:
        p_val = 2 * sum((-1)**(j-1) * math.exp(-2 * j**2 * lambda_val**2) for j in range(1, 101))
        p_val = max(0.0, min(1.0, p_val))
    return max_d, p_val

# =====================================================
# 分析1: 分散の k 依存性 (Var ~ C * k なのか?)
# =====================================================
def variance_scaling_analysis():
    """
    Var[log2(T^k(n)/n)] を k=1..40 で計算し、
    k に対する線形性 (独立な場合の予測) を検証。
    """
    print("=== 分散のスケーリング分析 (k=1..40) ===")
    N = 8000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000

    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    results = []

    # 逐次的に T^k を計算
    current_values = {n: n for n in odd_numbers}
    log2_n_arr = {n: log2(n) for n in odd_numbers}

    for k in range(1, 41):
        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        # log2(T^k(n)/n) = log2(T^k(n)) - log2(n)
        log_ratios = [log2(current_values[n]) - log2_n_arr[n] for n in odd_numbers]

        m = mean(log_ratios)
        v = variance(log_ratios, m)
        s = std(log_ratios, m)
        sk = skewness(log_ratios)
        ku = kurtosis_excess(log_ratios)

        # 理論予測: var ~ 2.0 * k (独立近似)
        predicted_var = 2.0 * k

        results.append({
            'k': k,
            'mean_log_ratio': m,
            'var_log_ratio': v,
            'predicted_var_independent': predicted_var,
            'ratio_var_to_k': v / k,
            'skewness': sk,
            'kurtosis_excess': ku,
        })

        if k in [1, 2, 5, 10, 15, 20, 25, 30, 35, 40]:
            print(f"  k={k:2d}: mean={m:.4f}, var={v:.4f}, var/k={v/k:.4f}, pred={predicted_var:.1f}, skew={sk:.4f}, kurt={ku:.4f}")

    return results

# =====================================================
# 分析2: ステップ間相関
# =====================================================
def step_correlation_analysis():
    """
    連続するステップの log 変化間の相関を測定。
    独立なら相関 = 0。
    """
    print("\n=== ステップ間相関分析 ===")
    N = 10000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000

    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    # 各ステップでの log 変化を記録
    K_MAX = 20
    step_changes = {n: [] for n in odd_numbers}

    current_values = {n: n for n in odd_numbers}

    for k in range(1, K_MAX + 1):
        for n in odd_numbers:
            old_val = current_values[n]
            new_val = collatz_step(old_val)
            change = log2(new_val) - log2(old_val)
            step_changes[n].append(change)
            current_values[n] = new_val

    # lag-1 相関
    results = {}
    for lag in [1, 2, 3, 5]:
        correlations = []
        for step in range(K_MAX - lag):
            x_vals = [step_changes[n][step] for n in odd_numbers]
            y_vals = [step_changes[n][step + lag] for n in odd_numbers]

            mx = mean(x_vals)
            my = mean(y_vals)
            sx = std(x_vals, mx)
            sy = std(y_vals, my)

            if sx > 0 and sy > 0:
                cov = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals)) / len(x_vals)
                corr = cov / (sx * sy)
            else:
                corr = 0.0
            correlations.append(corr)

        avg_corr = mean(correlations)
        results[lag] = {
            'average_correlation': avg_corr,
            'correlations_by_step': [round(c, 6) for c in correlations],
        }
        print(f"  lag-{lag} 平均相関: {avg_corr:.6f}")

    return results

# =====================================================
# 分析3: k=30,40,50 での分布形状
# =====================================================
def large_k_distribution():
    """k が大きい場合の分布"""
    print("\n=== 大きなk での分布 (k=30,40,50) ===")
    N = 8000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000

    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    mu_est = -0.420  # Phase0で計測した値
    sigma2_est = 2.05

    results = {}
    current_values = {n: n for n in odd_numbers}
    log2_n_arr = {n: log2(n) for n in odd_numbers}

    k_targets = [30, 40, 50]

    for k in range(1, max(k_targets) + 1):
        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        if k in k_targets:
            # CLT スケーリング
            Z_values = []
            for n in odd_numbers:
                Tk_n = current_values[n]
                log_ratio = log2(Tk_n) - log2_n_arr[n]
                Z = (log_ratio - k * mu_est) / math.sqrt(sigma2_est * k)
                Z_values.append(Z)

            m = mean(Z_values)
            s = std(Z_values, m)
            sk = skewness(Z_values)
            ku = kurtosis_excess(Z_values)
            ks_stat, ks_pval = ks_test_normal(Z_values)

            print(f"  k={k}: mean={m:.6f}, std={s:.6f}, skew={sk:.6f}, kurt={ku:.6f}, KS={ks_stat:.6f}")

            results[k] = {
                'mean': m,
                'std': s,
                'skewness': sk,
                'kurtosis_excess': ku,
                'ks_statistic': ks_stat,
                'ks_pvalue': ks_pval,
            }

    return results

# =====================================================
# 分析4: alpha_k = (3/4)^k vs 実測最適指数の系統比較
# =====================================================
def scaling_exponent_comparison():
    """
    (3/4)^k スケーリングの意味を吟味:
    log2(T(n)/n) の平均が -0.415 => 各ステップで n が n^{2^{-0.415}} 倍
    => k ステップで n^{(1-0.415/log2(e))^k} ... ではない。

    正しくは: E[log2(T^k(n))] ~ log2(n) + k * E[log2(T/n)]
    => T^k(n) ~ n * 2^{k * (-0.415)}
    => T^k(n) / n ~ 2^{-0.415k}

    (3/4)^k = 2^{k * log2(3/4)} = 2^{-0.415k}
    log2(3/4) = log2(3) - 1 = 1.585 - 2 = -0.415  !!!

    これが alpha_k = (3/4)^k の由来!
    """
    print("\n=== スケーリング指数の理論的整合性 ===")
    print(f"  log2(3/4)        = {math.log2(3/4):.10f}")
    print(f"  既知 E[log2(T/n)] = -0.415")
    print(f"  実測 E[log2(T/n)] = -0.420237")
    print(f"  差分              = {math.log2(3/4) - (-0.415):.10f}")
    print()
    print("  解釈: alpha_k = (3/4)^k は T^k(n)/n のスケーリングに対応。")
    print("  Y_k(n) = log2(T^k(n)) - alpha_k * log2(n)")
    print("         = log2(T^k(n)) - (3/4)^k * log2(n)")
    print()
    print("  しかし正しいスケーリングは:")
    print("  log2(T^k(n)) ~ log2(n) + k * log2(3/4)")
    print("  => log2(T^k(n)) - log2(n) ~ k * log2(3/4) = -0.415 * k")
    print()
    print("  alpha_k = (3/4)^k ではなく、正しくは:")
    print("  log2(T^k(n)) ~ log2(n) + k * log2(3/4)")
    print("  つまり T^k(n) ~ n * (3/4)^k ではなく、T^k(n)/n ~ (3/4)^k (!) ")
    print()

    # 別スケーリング: T^k(n) / (n * (3/4)^k) の分布
    print("  検証: W_k(n) = log2(T^k(n)/n) - k*log2(3/4) = log2(T^k(n)/n) + 0.415*k")

    N = 10000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000
    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    results = {}
    current_values = {n: n for n in odd_numbers}
    log2_n_arr = {n: log2(n) for n in odd_numbers}

    for k in range(1, 21):
        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        W_values = []
        for n in odd_numbers:
            Tk_n = current_values[n]
            W = log2(Tk_n) - log2_n_arr[n] - k * math.log2(3/4)
            W_values.append(W)

        m = mean(W_values)
        s = std(W_values, m)
        sk = skewness(W_values)
        ku = kurtosis_excess(W_values)

        if k in [1, 5, 10, 15, 20]:
            ks_stat, ks_pval = ks_test_normal(W_values)
            print(f"  k={k:2d}: mean(W)={m:.4f}, std(W)={s:.4f}, std/sqrt(k)={s/math.sqrt(k):.4f}, skew={sk:.4f}, kurt={ku:.4f}, KS={ks_stat:.4f}")
            results[k] = {
                'mean': m,
                'std': s,
                'std_over_sqrt_k': s / math.sqrt(k),
                'skewness': sk,
                'kurtosis_excess': ku,
                'ks_statistic': ks_stat,
                'ks_pvalue': ks_pval,
            }

    return results


if __name__ == '__main__':
    print("=" * 60)
    print("深掘り分析: 分散スケーリングと正規収束")
    print("=" * 60)

    all_results = {}

    # 分析1
    print()
    var_scaling = variance_scaling_analysis()
    all_results['variance_scaling'] = var_scaling

    # 分析2
    step_corr = step_correlation_analysis()
    all_results['step_correlations'] = {str(k): v for k, v in step_corr.items()}

    # 分析3
    large_k = large_k_distribution()
    all_results['large_k_distribution'] = {str(k): {k2: round(v, 6) for k2, v in vv.items()} for k, vv in large_k.items()}

    # 分析4
    scaling_comp = scaling_exponent_comparison()
    all_results['correct_scaling_Wk'] = {str(k): {k2: round(v, 6) for k2, v in vv.items()} for k, vv in scaling_comp.items()}

    # 核心的な発見を出力
    print("\n" + "=" * 60)
    print("核心的発見")
    print("=" * 60)

    # 分散/k の収束
    print("\n1. Var[log2(T^k/n)] / k の推移:")
    for r in var_scaling:
        if r['k'] in [1, 5, 10, 20, 30, 40]:
            print(f"   k={r['k']:2d}: var/k = {r['ratio_var_to_k']:.6f}")

    # 相関
    print("\n2. ステップ間相関:")
    for lag, data in step_corr.items():
        print(f"   lag-{lag}: avg corr = {data['average_correlation']:.6f}")

    # CLT 収束
    print("\n3. 歪度・尖度の k 依存性:")
    for r in var_scaling:
        if r['k'] in [1, 5, 10, 20, 30, 40]:
            print(f"   k={r['k']:2d}: skew={r['skewness']:.4f}, kurt={r['kurtosis_excess']:.4f}")

    # Berry-Esseen 型の収束速度
    print("\n4. |skewness| の収束:")
    for r in var_scaling:
        if r['k'] in [1, 5, 10, 20, 30, 40]:
            abs_skew = abs(r['skewness'])
            predicted_rate = 1.0 / math.sqrt(r['k'])  # Berry-Esseen: O(1/sqrt(k))
            print(f"   k={r['k']:2d}: |skew|={abs_skew:.4f}, 1/sqrt(k)={predicted_rate:.4f}, ratio={abs_skew/predicted_rate:.4f}")

    with open('/Users/soyukke/study/lean-unsolved/results/Tk_scaling_deep.json', 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print("\n結果を results/Tk_scaling_deep.json に保存しました。")
