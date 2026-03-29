"""
分散飽和の原因分析:
- k が大きいと T^k(n) が 1 付近に落ち込む軌道が増える
- これが分散を減少させ、正規分布からの逸脱を引き起こす
- 「まだ1に到達していない」軌道のみでフィルタして再分析
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

def log2(x):
    return math.log2(x) if x > 0 else 0.0

def mean(arr):
    return sum(arr) / len(arr) if arr else 0.0

def variance(arr, m=None):
    if not arr:
        return 0.0
    if m is None:
        m = mean(arr)
    return sum((x - m)**2 for x in arr) / len(arr)

def std(arr, m=None):
    return math.sqrt(variance(arr, m))

def skewness(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0 or len(arr) < 3:
        return 0.0
    return sum(((x - m)/s)**3 for x in arr) / len(arr)

def kurtosis_excess(arr):
    m = mean(arr)
    s = std(arr, m)
    if s == 0 or len(arr) < 4:
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


def analysis_with_filtering():
    """
    kステップ後にまだ「十分大きい」値を持つ軌道のみで分布を調べる。
    T^k(n) > threshold のもののみ使用。
    """
    print("=== フィルタリング分析: T^k(n) > 10 の軌道のみ ===")
    N = 10000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000
    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    mu = math.log2(3/4)  # = -0.4150...

    current_values = {n: n for n in odd_numbers}
    log2_n_arr = {n: log2(n) for n in odd_numbers}

    results = []

    for k in range(1, 51):
        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        # 全体のW
        W_all = []
        W_filtered = []
        n_at_1 = 0

        for n in odd_numbers:
            Tk_n = current_values[n]
            W = log2(Tk_n) - log2_n_arr[n] - k * mu
            W_all.append(W)
            if Tk_n <= 1:
                n_at_1 += 1
            else:
                W_filtered.append(W)

        frac_at_1 = n_at_1 / N

        # 全体統計
        m_all = mean(W_all)
        s_all = std(W_all, m_all)
        sk_all = skewness(W_all)
        ku_all = kurtosis_excess(W_all)

        # フィルタ後統計
        if len(W_filtered) > 10:
            m_filt = mean(W_filtered)
            s_filt = std(W_filtered, m_filt)
            sk_filt = skewness(W_filtered)
            ku_filt = kurtosis_excess(W_filtered)
        else:
            m_filt = s_filt = sk_filt = ku_filt = None

        r = {
            'k': k,
            'frac_reached_1': frac_at_1,
            'all_mean': m_all,
            'all_std': s_all,
            'all_var': s_all**2,
            'all_var_over_k': s_all**2 / k,
            'all_skew': sk_all,
            'all_kurt': ku_all,
        }
        if m_filt is not None:
            r.update({
                'filtered_n': len(W_filtered),
                'filtered_mean': m_filt,
                'filtered_std': s_filt,
                'filtered_var': s_filt**2,
                'filtered_var_over_k': s_filt**2 / k,
                'filtered_skew': sk_filt,
                'filtered_kurt': ku_filt,
            })
        results.append(r)

        if k in [1, 5, 10, 15, 20, 25, 30, 40, 50]:
            print(f"\n  k={k}: {frac_at_1*100:.1f}% at 1")
            print(f"    全体:      mean={m_all:.4f}, std={s_all:.4f}, var/k={s_all**2/k:.4f}, skew={sk_all:.4f}, kurt={ku_all:.4f}")
            if m_filt is not None:
                print(f"    フィルタ({len(W_filtered):5d}): mean={m_filt:.4f}, std={s_filt:.4f}, var/k={s_filt**2/k:.4f}, skew={sk_filt:.4f}, kurt={ku_filt:.4f}")

    return results


def large_n_analysis():
    """
    大きなnを使えば、k=20でもまだ1に到達していない軌道が多い。
    n ~ 10^9 で再テスト。
    """
    print("\n=== 大きな n での再テスト (n ~ 10^9) ===")
    N = 5000
    n_start = 10**9 + 1
    n_end = 10**9 + 100000
    odd_numbers = list(range(n_start if n_start % 2 == 1 else n_start + 1,
                             n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    mu = math.log2(3/4)
    sigma2_per_step = 2.05  # 計測値

    current_values = {n: n for n in odd_numbers}
    log2_n_arr = {n: log2(n) for n in odd_numbers}

    results = []

    for k in range(1, 41):
        new_values = {}
        for n_orig, val in current_values.items():
            new_values[n_orig] = collatz_step(val)
        current_values = new_values

        W_values = []
        Z_values = []
        n_at_1 = 0
        for n in odd_numbers:
            Tk_n = current_values[n]
            if Tk_n <= 1:
                n_at_1 += 1
            W = log2(Tk_n) - log2_n_arr[n] - k * mu
            W_values.append(W)
            Z = W / math.sqrt(sigma2_per_step * k)
            Z_values.append(Z)

        frac_1 = n_at_1 / N
        m_W = mean(W_values)
        s_W = std(W_values)
        m_Z = mean(Z_values)
        s_Z = std(Z_values)
        sk_Z = skewness(Z_values)
        ku_Z = kurtosis_excess(Z_values)

        if k in [5, 10, 15, 20, 25, 30, 35, 40]:
            ks_stat, ks_pval = ks_test_normal(Z_values)
            print(f"  k={k:2d}: {frac_1*100:.1f}% at 1, Z: mean={m_Z:.4f}, std={s_Z:.4f}, skew={sk_Z:.4f}, kurt={ku_Z:.4f}, KS={ks_stat:.4f}")
            results.append({
                'k': k,
                'frac_at_1': frac_1,
                'Z_mean': m_Z,
                'Z_std': s_Z,
                'Z_skew': sk_Z,
                'Z_kurt': ku_Z,
                'KS_stat': ks_stat,
                'W_mean': m_W,
                'W_std': s_W,
                'W_var_over_k': s_W**2 / k,
            })

    return results


def berry_esseen_rate():
    """
    CLT収束速度の定量評価。
    Berry-Esseen定理: |F_n(x) - Phi(x)| <= C * E[|X|^3] / (sigma^3 * sqrt(n))
    ここで n = k (ステップ数)
    """
    print("\n=== Berry-Esseen 収束速度の定量評価 ===")
    # 1ステップの3次モーメント
    N = 20000
    n_start = 10**6 + 1
    n_end = 10**6 + 200000
    odd_numbers = list(range(n_start, n_end + 1, 2))
    odd_numbers = random.sample(odd_numbers, N)

    mu = math.log2(3/4)
    log_ratios = []
    for n in odd_numbers:
        Tn = collatz_step(n)
        log_ratios.append(log2(Tn) - log2(n))

    m = mean(log_ratios)
    centered = [x - m for x in log_ratios]
    sigma2 = mean([x**2 for x in centered])
    sigma = math.sqrt(sigma2)
    rho = mean([abs(x)**3 for x in centered])  # E[|X-mu|^3]

    print(f"  sigma  = {sigma:.6f}")
    print(f"  sigma^3 = {sigma**3:.6f}")
    print(f"  E[|X-mu|^3] = {rho:.6f}")
    print(f"  rho / sigma^3 = {rho / sigma**3:.6f}")
    print()

    # Berry-Esseen上界: C_BE * rho / (sigma^3 * sqrt(k))
    C_BE = 0.4748  # 最良定数
    print(f"  Berry-Esseen定数 C = {C_BE}")
    print(f"  上界 = {C_BE} * {rho/sigma**3:.4f} / sqrt(k)")
    print()

    for k in [5, 10, 20, 30, 50, 100]:
        bound = C_BE * rho / (sigma**3 * math.sqrt(k))
        print(f"  k={k:3d}: BE上界 = {bound:.6f}")

    return {
        'sigma': sigma,
        'third_abs_moment': rho,
        'rho_over_sigma3': rho / sigma**3,
        'berry_esseen_const': C_BE,
    }


if __name__ == '__main__':
    print("=" * 60)
    print("分散飽和の原因分析と正規収束の条件")
    print("=" * 60)

    # 分析1: フィルタリング
    filter_results = analysis_with_filtering()

    # 分析2: 大きなn
    large_n_results = large_n_analysis()

    # 分析3: Berry-Esseen
    be_results = berry_esseen_rate()

    # 保存
    output = {
        'filtering_analysis': filter_results,
        'large_n_analysis': large_n_results,
        'berry_esseen': be_results,
    }

    with open('/Users/soyukke/study/lean-unsolved/results/Tk_saturation_analysis.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=lambda x: round(x, 6) if isinstance(x, float) else x)

    print("\n結果を results/Tk_saturation_analysis.json に保存しました。")
