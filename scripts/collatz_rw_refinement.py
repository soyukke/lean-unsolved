#!/usr/bin/env python3
"""
Syracuse軌道のlog2スケールでのランダムウォーク近似の精密化

X_k = log2(T^k(n)) の対数スケールランダムウォーク:
  - ドリフト mu = E[log2(T(n)/n)] の精密測定
  - 分散 sigma^2 の精密測定
  - 正規近似の適用範囲をKS検定で検証
  - 局所CLTによるST分布予測をN=10^6で検証

Syracuse関数: T(n) = (3n+1) / 2^{v2(3n+1)}  (nは奇数)
"""

import math
import random
import time
from collections import Counter, defaultdict

# ============================================================
# パート0: 基本関数
# ============================================================

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)}"""
    n = 3 * n + 1
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return n, v

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def stopping_time_syracuse(n):
    """n が n 未満の値に初めて到達するまでのSyracuseステップ数"""
    original = n
    steps = 0
    current = n
    while current >= original:
        if current == 1 and original != 1:
            return steps
        current, _ = syracuse(current)
        steps += 1
        if steps > 50000:
            return -1  # 未到達
    return steps

def total_stopping_time_syracuse(n):
    """n が 1 に到達するまでの総Syracuseステップ数"""
    steps = 0
    current = n
    while current != 1:
        current, _ = syracuse(current)
        steps += 1
        if steps > 500000:
            return -1
    return steps

# ============================================================
# パート1: ドリフトと分散の精密測定
# ============================================================

def measure_drift_variance(N_max, sample_size=None):
    """
    実際のSyracuse軌道から1ステップ変化量 log2(T(n)/n) の統計を測定
    奇数 n in [3, N_max] をサンプリング
    """
    print("=" * 70)
    print(f"パート1: ドリフトと分散の精密測定 (N_max={N_max})")
    print("=" * 70)

    # 理論値
    mu_theory = math.log2(3) - 2  # = log2(3/4) ≈ -0.41504
    # Var[log2(T(n)/n)] = Var[log2(3) - v2*log2(2)] = Var[v2] = 2.0 (幾何分布近似)
    # しかし実際はv2の分布が厳密に幾何分布ではないかもしれない

    odd_numbers = list(range(3, N_max + 1, 2))
    if sample_size and sample_size < len(odd_numbers):
        random.seed(42)
        odd_numbers = random.sample(odd_numbers, sample_size)

    log_ratios = []
    v2_values = []

    for n in odd_numbers:
        tn, v = syracuse(n)
        log_ratio = math.log2(tn) - math.log2(n)  # = log2(T(n)/n) = log2(3) - v*1
        log_ratios.append(log_ratio)
        v2_values.append(v)

    count = len(log_ratios)
    mu_obs = sum(log_ratios) / count
    var_obs = sum((x - mu_obs)**2 for x in log_ratios) / (count - 1)

    mu_v2 = sum(v2_values) / count
    var_v2 = sum((x - mu_v2)**2 for x in v2_values) / (count - 1)

    # v2の分布を集計
    v2_counter = Counter(v2_values)
    total_v2 = sum(v2_counter.values())

    print(f"\nサンプル数: {count}")
    print(f"\n--- log2(T(n)/n) の統計 ---")
    print(f"  観測平均 mu_obs  = {mu_obs:.10f}")
    print(f"  理論値   mu_th   = {mu_theory:.10f}")
    print(f"  差       |diff|  = {abs(mu_obs - mu_theory):.2e}")
    print(f"  観測分散 var_obs = {var_obs:.10f}")
    print(f"  理論分散(幾何)   = {2.0:.10f}")
    print(f"  差       |diff|  = {abs(var_obs - 2.0):.2e}")
    print(f"  観測標準偏差     = {math.sqrt(var_obs):.10f}")

    print(f"\n--- v2(3n+1) の統計 ---")
    print(f"  観測平均 E[v2]   = {mu_v2:.10f}")
    print(f"  理論値 (幾何)    = 2.0")
    print(f"  差               = {abs(mu_v2 - 2.0):.2e}")
    print(f"  観測分散 Var[v2] = {var_v2:.10f}")
    print(f"  理論値 (幾何)    = 2.0")
    print(f"  差               = {abs(var_v2 - 2.0):.2e}")

    print(f"\n--- v2 の分布 (観測 vs 幾何分布) ---")
    print(f"  {'v2':>4s}  {'観測頻度':>10s}  {'幾何分布':>10s}  {'比率':>8s}")
    for j in sorted(v2_counter.keys()):
        if j <= 15:
            obs_freq = v2_counter[j] / total_v2
            geom_freq = 1.0 / (2**j)
            ratio = obs_freq / geom_freq if geom_freq > 0 else float('inf')
            print(f"  {j:4d}  {obs_freq:10.6f}  {geom_freq:10.6f}  {ratio:8.4f}")

    # 3次以上のモーメント
    skew = sum((x - mu_obs)**3 for x in log_ratios) / (count * var_obs**1.5)
    kurt = sum((x - mu_obs)**4 for x in log_ratios) / (count * var_obs**2) - 3

    print(f"\n--- 高次モーメント ---")
    print(f"  歪度 (skewness)         = {skew:.6f}")
    print(f"  尖度 (excess kurtosis)  = {kurt:.6f}")
    print(f"  幾何分布の理論歪度      = {(2 - 0.5) / math.sqrt(0.5 * 0.5 / 0.25):.6f}")
    # Geom(p=1/2): skew = (2-p)/sqrt(q) where q=1-p
    # = (2-0.5)/sqrt(0.5) = 1.5/sqrt(0.5) ≈ 2.121

    return {
        'mu_obs': mu_obs, 'mu_theory': mu_theory,
        'var_obs': var_obs, 'var_theory': 2.0,
        'mu_v2': mu_v2, 'var_v2': var_v2,
        'skewness': skew, 'kurtosis': kurt,
        'count': count
    }


# ============================================================
# パート2: KS検定 - 正規近似の適用範囲
# ============================================================

def ks_test_normal_approx(N_max, step_counts=[5, 10, 20, 50, 100]):
    """
    k ステップ後の S_k = sum_{i=1}^{k} log2(T^i(n)/T^{i-1}(n)) の分布を、
    正規分布 N(k*mu, k*sigma^2) と比較してKS検定を行う。
    """
    print("\n" + "=" * 70)
    print(f"パート2: KS検定による正規近似の適用範囲 (N_max={N_max})")
    print("=" * 70)

    mu = math.log2(3) - 2
    sigma2 = 2.0

    results = {}

    for k in step_counts:
        # 奇数サンプルから k ステップの軌道和を計算
        sample_size = min(50000, N_max // 2)
        random.seed(42 + k)
        odd_numbers = [random.randrange(3, N_max + 1, 2) for _ in range(sample_size)]

        S_k_values = []
        for n in odd_numbers:
            s = 0.0
            current = n
            valid = True
            for step in range(k):
                next_val, v = syracuse(current)
                s += math.log2(next_val) - math.log2(current)
                current = next_val
                if current == 1:
                    # 1に到達した場合は除外（absorbing state）
                    valid = False
                    break
            if valid:
                S_k_values.append(s)

        if len(S_k_values) < 100:
            print(f"  k={k}: サンプル不足 ({len(S_k_values)})")
            continue

        # 標準化
        expected_mean = k * mu
        expected_std = math.sqrt(k * sigma2)

        obs_mean = sum(S_k_values) / len(S_k_values)
        obs_std = math.sqrt(sum((x - obs_mean)**2 for x in S_k_values) / (len(S_k_values) - 1))

        # 標準化してKS統計量を計算
        z_values = sorted([(x - expected_mean) / expected_std for x in S_k_values])
        n_z = len(z_values)

        # KS統計量 = max |F_n(x) - Phi(x)|
        ks_stat = 0.0
        for i, z in enumerate(z_values):
            F_n = (i + 1) / n_z
            F_n_minus = i / n_z
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks_stat = max(ks_stat, abs(F_n - Phi), abs(F_n_minus - Phi))

        # KS臨界値 (alpha=0.05): c(0.05) / sqrt(n) ≈ 1.36 / sqrt(n)
        ks_critical_005 = 1.36 / math.sqrt(n_z)
        ks_critical_001 = 1.63 / math.sqrt(n_z)

        reject_005 = "棄却" if ks_stat > ks_critical_005 else "受容"
        reject_001 = "棄却" if ks_stat > ks_critical_001 else "受容"

        print(f"\n  k={k} ステップ (有効サンプル: {n_z})")
        print(f"    観測平均: {obs_mean:.6f}, 理論平均: {expected_mean:.6f}, 差: {abs(obs_mean-expected_mean):.6f}")
        print(f"    観測std:  {obs_std:.6f}, 理論std:  {expected_std:.6f}, 比: {obs_std/expected_std:.6f}")
        print(f"    KS統計量: {ks_stat:.6f}")
        print(f"    KS臨界値(5%): {ks_critical_005:.6f} → {reject_005}")
        print(f"    KS臨界値(1%): {ks_critical_001:.6f} → {reject_001}")

        results[k] = {
            'n_samples': n_z,
            'obs_mean': obs_mean, 'theory_mean': expected_mean,
            'obs_std': obs_std, 'theory_std': expected_std,
            'ks_stat': ks_stat,
            'ks_critical_005': ks_critical_005,
            'reject_005': reject_005,
            'ks_critical_001': ks_critical_001,
            'reject_001': reject_001,
        }

    return results


# ============================================================
# パート3: 自己相関の測定 - i.i.d.仮定の検証
# ============================================================

def measure_autocorrelation(N_max, max_lag=10, sample_size=20000):
    """
    連続するSyracuseステップの log2変化量の自己相関を測定。
    i.i.d.仮定が成立するならラグ1以降の自己相関は0であるべき。
    """
    print("\n" + "=" * 70)
    print(f"パート3: 自己相関の測定 (i.i.d.仮定の検証)")
    print("=" * 70)

    trajectory_length = max_lag + 50
    random.seed(42)
    odd_numbers = [random.randrange(3, N_max + 1, 2) for _ in range(sample_size)]

    # 各軌道の変化量列を収集
    all_deltas = []  # (delta_0, delta_1, ..., delta_{L-1}) のリスト

    for n in odd_numbers:
        deltas = []
        current = n
        for _ in range(trajectory_length):
            next_val, v = syracuse(current)
            deltas.append(math.log2(next_val) - math.log2(current))
            current = next_val
            if current == 1:
                break
        if len(deltas) >= max_lag + 10:
            all_deltas.append(deltas)

    print(f"  有効軌道数: {len(all_deltas)}")

    # ラグ別自己相関を計算
    # 軌道の中間部分（最初10ステップを除外して定常状態に近づける）
    start_idx = 10
    flat_pairs = defaultdict(list)

    for deltas in all_deltas:
        for i in range(start_idx, len(deltas) - max_lag):
            for lag in range(max_lag + 1):
                flat_pairs[lag].append((deltas[i], deltas[i + lag]))

    mu = math.log2(3) - 2

    print(f"\n  {'ラグ':>4s}  {'自己相関':>12s}  {'95%信頼区間':>14s}  {'有意性':>8s}")

    autocorr_results = {}
    for lag in range(max_lag + 1):
        pairs = flat_pairs[lag]
        n_pairs = len(pairs)
        if n_pairs == 0:
            continue

        # 自己相関 = Cov(X_i, X_{i+lag}) / Var(X_i)
        mean_x = sum(p[0] for p in pairs) / n_pairs
        mean_y = sum(p[1] for p in pairs) / n_pairs
        var_x = sum((p[0] - mean_x)**2 for p in pairs) / n_pairs
        var_y = sum((p[1] - mean_y)**2 for p in pairs) / n_pairs
        cov_xy = sum((p[0] - mean_x) * (p[1] - mean_y) for p in pairs) / n_pairs

        if var_x > 0 and var_y > 0:
            corr = cov_xy / math.sqrt(var_x * var_y)
        else:
            corr = 0.0

        # 95%信頼区間: ±1.96/sqrt(n)
        ci = 1.96 / math.sqrt(n_pairs)
        significant = "***" if abs(corr) > ci else ""

        print(f"  {lag:4d}  {corr:12.8f}  +/- {ci:.8f}  {significant}")
        autocorr_results[lag] = {'corr': corr, 'ci': ci, 'n_pairs': n_pairs}

    return autocorr_results


# ============================================================
# パート4: 局所CLTによるStopping Time分布予測
# ============================================================

def stopping_time_distribution_vs_clt(N_max):
    """
    局所CLT予測:
    P(ST = k) ≈ log2(n) * phi((log2(n) + k*mu) / (sigma*sqrt(k))) / (sigma*sqrt(k))

    ここで phi は標準正規密度、mu = log2(3)-2, sigma^2 = 2

    大数の法則: ST ≈ log2(n) / |mu| = log2(n) / 0.41504

    N_max までの奇数について実測STと比較
    """
    print("\n" + "=" * 70)
    print(f"パート4: 局所CLTによるStopping Time分布予測 (N_max={N_max})")
    print("=" * 70)

    mu = math.log2(3) - 2  # ≈ -0.41504
    sigma2 = 2.0
    sigma = math.sqrt(sigma2)

    # 全奇数のSTを計算
    st_values = []
    for n in range(3, N_max + 1, 2):
        st = stopping_time_syracuse(n)
        if st >= 0:
            st_values.append((n, st))

    print(f"  サンプル数: {len(st_values)}")

    # ST の分布
    st_only = [s for _, s in st_values]
    st_counter = Counter(st_only)
    total = len(st_only)

    mean_st = sum(st_only) / total
    var_st = sum((x - mean_st)**2 for x in st_only) / (total - 1)
    max_st = max(st_only)

    # 理論的な平均ST: E[ST] ≈ (1/|mu|) * <log2(n)>_avg
    # log2(n) の平均は (1/(N/2)) * sum_{k=0}^{N/2-1} log2(2k+3) ≈ log2(N) - 1
    avg_log2n = sum(math.log2(n) for n, _ in st_values) / total
    theory_mean_st = avg_log2n / abs(mu)

    print(f"\n--- Stopping Time 統計 ---")
    print(f"  観測平均 E[ST]    = {mean_st:.4f}")
    print(f"  理論予測 E[ST]    = {theory_mean_st:.4f} (= <log2(n)>/|mu|)")
    print(f"  比率              = {mean_st / theory_mean_st:.6f}")
    print(f"  観測分散 Var[ST]  = {var_st:.4f}")
    print(f"  観測max ST        = {max_st}")
    print(f"  平均 log2(n)      = {avg_log2n:.4f}")

    # STの分布をビンに分けて理論値と比較
    # 理論: n が一様に [3, N_max] の奇数から選ばれるとき、
    # P(ST=k) = average over n of P(first passage at step k)

    # 単純なRWモデル: X_i iid, E[X]=-0.415, Var[X]=2
    # S_k = sum X_i, ST = min{k: log2(n)+S_k < 0} (log2(n)からのfirst passage to 0)

    # RWシミュレーションでのST分布
    print(f"\n--- RWモデルとの比較 ---")
    n_rw_samples = 100000
    random.seed(123)

    rw_st_values = []
    for _ in range(n_rw_samples):
        # n を [3, N_max] の奇数から一様サンプリングに近似
        log2n = random.uniform(math.log2(3), math.log2(N_max))

        # RWシミュレーション: 各ステップで v2 ~ Geom(1/2) on {1,2,...}
        s = log2n
        k = 0
        while s >= 0 and k < 10000:
            # v2 ~ Geom(1/2): P(v=j) = 1/2^j for j=1,2,...
            v = 1
            while random.random() < 0.5:
                v += 1
            s += math.log2(3) - v  # = log2(3) - v2
            k += 1
        rw_st_values.append(k)

    rw_mean = sum(rw_st_values) / len(rw_st_values)
    rw_var = sum((x - rw_mean)**2 for x in rw_st_values) / (len(rw_st_values) - 1)

    print(f"  RW平均 ST         = {rw_mean:.4f}")
    print(f"  実測平均 ST       = {mean_st:.4f}")
    print(f"  比率              = {mean_st / rw_mean:.6f}")
    print(f"  RW分散 ST         = {rw_var:.4f}")
    print(f"  実測分散 ST       = {var_st:.4f}")

    # ビン別比較
    bin_size = 5
    max_bin = min(max_st + bin_size, 200)

    print(f"\n  {'STビン':>10s}  {'実測頻度':>10s}  {'RW頻度':>10s}  {'比率':>8s}")

    bin_comparison = {}
    for b_start in range(0, max_bin, bin_size):
        b_end = b_start + bin_size
        obs_count = sum(1 for s in st_only if b_start <= s < b_end)
        rw_count = sum(1 for s in rw_st_values if b_start <= s < b_end)

        obs_freq = obs_count / total
        rw_freq = rw_count / len(rw_st_values)

        if rw_freq > 1e-6:
            ratio = obs_freq / rw_freq
        else:
            ratio = float('inf') if obs_freq > 0 else 0

        if obs_count > 10 or rw_count > 10:
            print(f"  [{b_start:3d},{b_end:3d})  {obs_freq:10.6f}  {rw_freq:10.6f}  {ratio:8.4f}")
            bin_comparison[f"[{b_start},{b_end})"] = {
                'obs_freq': obs_freq, 'rw_freq': rw_freq, 'ratio': ratio
            }

    return {
        'mean_st': mean_st, 'theory_mean_st': theory_mean_st,
        'var_st': var_st, 'rw_mean': rw_mean, 'rw_var': rw_var,
        'max_st': max_st, 'bin_comparison': bin_comparison
    }


# ============================================================
# パート5: 尾部指数の精密測定
# ============================================================

def tail_exponent_analysis(N_max):
    """
    P(ST > t) の尾部減衰率を精密に測定。
    既知: P(ST > t) ~ exp(-lambda * t) with lambda ≈ 0.0735
    Cramer関数 I(0) = 0.05498 との関係を検証。
    """
    print("\n" + "=" * 70)
    print(f"パート5: 尾部指数の精密測定 (N_max={N_max})")
    print("=" * 70)

    # STを計算
    st_values = []
    for n in range(3, N_max + 1, 2):
        st = stopping_time_syracuse(n)
        if st >= 0:
            st_values.append(st)

    total = len(st_values)

    # 累積分布の尾部
    max_st = max(st_values)

    # P(ST > t) for various t
    print(f"\n  {'t':>5s}  {'P(ST>t)':>12s}  {'log P(ST>t)':>14s}  {'-log/t':>10s}")

    tail_data = []
    for t in range(10, min(max_st, 200), 5):
        count_gt_t = sum(1 for s in st_values if s > t)
        if count_gt_t > 0:
            p = count_gt_t / total
            log_p = math.log(p)
            rate = -log_p / t
            print(f"  {t:5d}  {p:12.8f}  {log_p:14.6f}  {rate:10.6f}")
            tail_data.append((t, p, rate))

    # 線形回帰で lambda を推定 (t >= 20 の範囲)
    tail_fit_data = [(t, math.log(p)) for t, p, _ in tail_data if t >= 20 and p > 1e-7]
    if len(tail_fit_data) >= 3:
        n_fit = len(tail_fit_data)
        sum_t = sum(d[0] for d in tail_fit_data)
        sum_logp = sum(d[1] for d in tail_fit_data)
        sum_t2 = sum(d[0]**2 for d in tail_fit_data)
        sum_t_logp = sum(d[0]*d[1] for d in tail_fit_data)

        # slope = (n*sum_t_logp - sum_t*sum_logp) / (n*sum_t2 - sum_t^2)
        denom = n_fit * sum_t2 - sum_t**2
        if denom != 0:
            slope = (n_fit * sum_t_logp - sum_t * sum_logp) / denom
            intercept = (sum_logp - slope * sum_t) / n_fit
            lambda_est = -slope

            print(f"\n  尾部指数 lambda (線形回帰) = {lambda_est:.6f}")
            print(f"  既知値 lambda              = 0.0735")
            print(f"  Cramer I(0)               = 0.05498")
            print(f"  lambda / I(0)             = {lambda_est / 0.05498:.6f}")

            # 理論: lambda = I(0) for simple RW first passage
            # ここで I(0) は S_k/k = 0 に対する rate function
            # I(x) = sup_t (tx - Lambda(t)) where Lambda(t) = log E[e^{tX}]

            return {
                'lambda_est': lambda_est,
                'lambda_known': 0.0735,
                'cramer_I0': 0.05498,
                'tail_data': [(t, p) for t, p, _ in tail_data]
            }

    return {'tail_data': [(t, p) for t, p, _ in tail_data]}


# ============================================================
# パート6: 条件付き分布 - n mod 2^k 別の精密化
# ============================================================

def conditional_analysis(N_max, k_mod=6):
    """
    n mod 2^k 毎にドリフトを分解。
    2次マルコフ効果（gap≈0.82）の検証。
    """
    print("\n" + "=" * 70)
    print(f"パート6: 条件付き分布 (n mod {2**k_mod}, N_max={N_max})")
    print("=" * 70)

    modulus = 2**k_mod

    # n mod modulus 別に 1ステップの v2 分布を集計
    v2_by_class = defaultdict(list)

    for n in range(3, N_max + 1, 2):
        r = n % modulus
        _, v = syracuse(n)
        v2_by_class[r].append(v)

    print(f"\n  {'n mod':>6s}  {'E[v2]':>8s}  {'Var[v2]':>8s}  {'E[delta]':>10s}  {'サンプル':>8s}")

    mu_global = math.log2(3) - 2
    class_stats = {}

    for r in sorted(v2_by_class.keys()):
        vals = v2_by_class[r]
        if len(vals) < 10:
            continue
        mean_v = sum(vals) / len(vals)
        var_v = sum((x - mean_v)**2 for x in vals) / (len(vals) - 1) if len(vals) > 1 else 0
        mean_delta = math.log2(3) - mean_v

        print(f"  {r:6d}  {mean_v:8.4f}  {var_v:8.4f}  {mean_delta:10.6f}  {len(vals):8d}")
        class_stats[r] = {'mean_v2': mean_v, 'var_v2': var_v, 'mean_delta': mean_delta}

    # クラス別ドリフトのばらつき
    all_means = [class_stats[r]['mean_delta'] for r in class_stats]
    if all_means:
        drift_spread = max(all_means) - min(all_means)
        print(f"\n  ドリフト範囲: {min(all_means):.6f} ~ {max(all_means):.6f}")
        print(f"  スプレッド:   {drift_spread:.6f}")
        print(f"  全体平均との差の最大: {max(abs(m - mu_global) for m in all_means):.6f}")

    return class_stats


# ============================================================
# メイン実行
# ============================================================

if __name__ == '__main__':
    t_start = time.time()

    print("Syracuse軌道のlog2スケール ランダムウォーク近似の精密化")
    print("=" * 70)

    # パート1: ドリフトと分散 (N=10^6)
    drift_results = measure_drift_variance(10**6, sample_size=200000)

    # パート2: KS検定 (N=10^5 でメモリ節約)
    ks_results = ks_test_normal_approx(10**5, step_counts=[5, 10, 20, 50, 100])

    # パート3: 自己相関
    autocorr_results = measure_autocorrelation(10**5, max_lag=8, sample_size=10000)

    # パート4: ST分布 vs CLT予測 (N=10^6は重いのでN=5*10^5)
    st_results = stopping_time_distribution_vs_clt(500000)

    # パート5: 尾部指数 (N=10^6)
    tail_results = tail_exponent_analysis(10**6)

    # パート6: 条件付き分布 (N=10^5)
    cond_results = conditional_analysis(10**5, k_mod=4)

    elapsed = time.time() - t_start
    print(f"\n\n{'=' * 70}")
    print(f"総実行時間: {elapsed:.1f}秒")
    print("=" * 70)

    # サマリー
    print("\n\n===== 総合サマリー =====")
    print(f"1. ドリフト: mu={drift_results['mu_obs']:.10f} (理論: {drift_results['mu_theory']:.10f})")
    print(f"   分散: sigma^2={drift_results['var_obs']:.10f} (理論: 2.0)")
    print(f"   歪度: {drift_results['skewness']:.6f}, 尖度: {drift_results['kurtosis']:.6f}")

    print(f"2. KS検定:")
    for k, res in ks_results.items():
        print(f"   k={k}: KS={res['ks_stat']:.6f}, 5%{'棄却' if res['reject_005']=='棄却' else '受容'}")

    print(f"3. 自己相関:")
    for lag in range(1, min(6, len(autocorr_results))):
        if lag in autocorr_results:
            r = autocorr_results[lag]
            print(f"   lag={lag}: r={r['corr']:.8f} (CI: +/-{r['ci']:.8f})")

    print(f"4. ST分布: 実測平均={st_results['mean_st']:.2f}, "
          f"RW予測={st_results['rw_mean']:.2f}, "
          f"理論={st_results['theory_mean_st']:.2f}")

    if 'lambda_est' in tail_results:
        print(f"5. 尾部指数: lambda={tail_results['lambda_est']:.6f} (既知: 0.0735)")
