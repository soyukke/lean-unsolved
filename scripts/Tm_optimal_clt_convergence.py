"""
T^m 最適基本マップ: m=1,2,3,4,5,6 での CLT 収束速度比較

目標:
1. T^m の1回適用のモーメント（歪度、尖度）をm毎に理論的に計算
2. Berry-Esseen 定数 rho_m / sigma_m^3 をm毎に計算
3. KS距離のm依存性を数値実験で測定
4. 同じ「計算コスト」（= 元のT適用回数 = m*k）での最適mを決定

核心的トレードオフ:
- m増加 -> 歪度 ~ gamma_3 / sqrt(m) 減少（CLT収束改善）
- m増加 -> 1ステップのコストがm倍（同じコストでkが1/m倍に）
- 同コスト比較: KS(T^m, k=N/m) vs KS(T, k=N)

既知:
- X = log2(3) - V, V ~ Geom(1/2)
- E[X] = log2(3) - 2, Var[X] = 2, Skew[X] = -3*sqrt(2)/2, Kurt[X] = 6.5
- rho = 7, Berry-Esseen: KS ~ 0.28 * k^{-0.514}
"""

import numpy as np
from scipy import stats
from collections import Counter
import json
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Part 1: 理論的モーメント計算 (T^m の m-step 合成分布)
# ============================================================

def theoretical_moments_Tm(m):
    """
    T^m = T composed m times の対数増分のモーメントを理論計算。

    独立近似: X_1 + X_2 + ... + X_m where X_i = log2(3) - V_i, V_i ~ Geom(1/2)

    S_m = sum X_i:
    E[S_m] = m * E[X] = m * (log2(3) - 2)
    Var[S_m] = m * Var[X] = 2m
    Skew[S_m] = Skew[X] / sqrt(m)
    Kurt[S_m] = Kurt[X] / m
    rho_m = E[|S_m - E[S_m]|^3]
    """
    mu_X = np.log2(3) - 2  # -0.41504
    var_X = 2.0
    sigma_X = np.sqrt(2)
    skew_X = -3 * np.sqrt(2) / 2  # -2.1213
    kurt_X = 6.5
    rho_X = 7.0  # exact

    mu_Sm = m * mu_X
    var_Sm = m * var_X
    sigma_Sm = np.sqrt(var_Sm)
    skew_Sm = skew_X / np.sqrt(m)
    kurt_Sm = kurt_X / m

    # rho_m = E[|S_m - E[S_m]|^3] の計算
    # 独立和のrho: 厳密にはrho_m != m * rho だが、
    # 標準化3次絶対モーメントは rho_m / sigma_m^3
    # 理論: rho_m / sigma_m^3 = rho_X / (sigma_X^3 * sqrt(m)) for i.i.d. sum
    # (Berry-Esseen の分子がsqrt(m)で小さくなる)
    rho_over_sigma3 = rho_X / (sigma_X**3 * np.sqrt(m))

    return {
        'm': m,
        'mu': mu_Sm,
        'var': var_Sm,
        'sigma': sigma_Sm,
        'skewness': skew_Sm,
        'kurtosis_excess': kurt_Sm,
        'rho_over_sigma3': rho_over_sigma3,
        'BE_rate_per_step': rho_over_sigma3,  # BE bound ~ C * this / sqrt(k)
    }


def compute_Tm_numerical_rho(m, n_samples=200000):
    """
    T^m の増分 S_m の数値的 rho/sigma^3 を計算。
    独立 Geom(1/2) の和からシミュレーション。
    """
    # V_i ~ Geom(1/2), i=1..m を m 個独立に生成
    V = np.random.geometric(0.5, size=(n_samples, m))
    S = m * np.log2(3) - np.sum(V, axis=1)

    mu = np.mean(S)
    sigma = np.std(S)

    centered = S - mu
    rho = np.mean(np.abs(centered)**3)
    rho_over_sigma3 = rho / sigma**3
    skew = np.mean(centered**3) / sigma**3
    kurt = np.mean(centered**4) / sigma**4 - 3

    return {
        'm': m,
        'mu_num': mu,
        'sigma_num': sigma,
        'skew_num': skew,
        'kurt_num': kurt,
        'rho_over_sigma3_num': rho_over_sigma3,
    }


print("=" * 70)
print("Part 1: T^m の理論的モーメント (m=1..8)")
print("=" * 70)

theory_results = []
for m in range(1, 9):
    th = theoretical_moments_Tm(m)
    num = compute_Tm_numerical_rho(m)
    th['rho_over_sigma3_numerical'] = num['rho_over_sigma3_num']
    theory_results.append(th)
    print(f"  m={m}: skew={th['skewness']:.4f}, kurt={th['kurtosis_excess']:.4f}, "
          f"rho/sigma^3={th['rho_over_sigma3']:.4f} (num={num['rho_over_sigma3_num']:.4f})")

# ============================================================
# Part 2: 同コスト比較の理論的分析
# ============================================================

print("\n" + "=" * 70)
print("Part 2: 同コスト比較 (total T-applications = N)")
print("=" * 70)
print("  T^m を k = N/m 回適用 vs T を k=N 回適用")
print("  Berry-Esseen: KS_m(k) <= C_BE * (rho_m/sigma_m^3) / sqrt(k)")
print("  同コスト: k = N/m, so KS_m(N/m) <= C_BE * rho_m/sigma_m^3 / sqrt(N/m)")
print()

C_BE = 0.11  # 実効Berry-Esseen定数（実測値）
rho_base = 7.0
sigma3_base = 2 * np.sqrt(2)

for N in [10, 20, 50, 100]:
    print(f"  N = {N} (total T-applications):")
    for m in range(1, 9):
        k = N / m
        if k < 1:
            continue
        th = theoretical_moments_Tm(m)
        # KS 上界（理論）
        ks_upper = C_BE * th['rho_over_sigma3'] / np.sqrt(k)
        # 実効べき乗則 0.28 * k^{-0.514} で推定
        ks_empirical_est = 0.28 * k**(-0.514)
        print(f"    m={m}, k={k:.1f}: KS_BE_upper={ks_upper:.4f}, "
              f"KS_emp_est={ks_empirical_est:.4f}")
    print()

# ============================================================
# Part 3: 数値実験 - 実際の T^m の KS 距離測定
# ============================================================

print("=" * 70)
print("Part 3: 数値実験 - T^m の KS 距離測定")
print("=" * 70)

def collatz_T(n):
    """Syracuse map: T(n) = (3n+1) / 2^{v2(3n+1)} for odd n"""
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def collatz_Tm(n, m):
    """T^m: T composed m times"""
    x = n
    for _ in range(m):
        x = collatz_T(x)
        if x == 1:
            return None  # reached 1
    return x

def measure_ks_for_Tm(m_val, k_steps, n_start_range=(10**7, 2*10**7), n_samples=50000):
    """
    T^m を k_steps 回適用した対数増分の和 S_k の CLT 収束を KS 距離で測定。
    """
    log2_3 = np.log2(3)
    increments = []

    # 奇数の初期値を大量生成
    starts = np.random.randint(n_start_range[0] // 2, n_start_range[1] // 2, size=n_samples * 2) * 2 + 1

    count = 0
    for n0 in starts:
        if count >= n_samples:
            break

        log_sum = 0.0
        valid = True
        x = int(n0)

        for step in range(k_steps):
            # m回のT適用を1ステップとする
            x_prev = x
            for _ in range(m_val):
                x_next = collatz_T(x)
                if x_next == 1:
                    valid = False
                    break
                x = x_next
            if not valid:
                break
            log_inc = np.log2(x / x_prev)
            log_sum += log_inc

        if valid:
            increments.append(log_sum)
            count += 1

    if len(increments) < 100:
        return None

    increments = np.array(increments)
    mu = np.mean(increments)
    sigma = np.std(increments)

    if sigma < 1e-10:
        return None

    standardized = (increments - mu) / sigma
    ks_stat, ks_pval = stats.kstest(standardized, 'norm')
    skew = stats.skew(increments)
    kurt = stats.kurtosis(increments)

    return {
        'm': m_val,
        'k': k_steps,
        'total_T_applications': m_val * k_steps,
        'n_valid': len(increments),
        'mean': float(mu),
        'std': float(sigma),
        'skewness': float(skew),
        'kurtosis_excess': float(kurt),
        'ks_statistic': float(ks_stat),
        'ks_sqrt_k': float(ks_stat * np.sqrt(k_steps)),
    }


# 小さなサンプルで各mとkの組み合わせを測定
np.random.seed(42)
numerical_results = []

# m=1,2,3,4,5,6 x k=1,2,3,5,8,10,15,20
m_values = [1, 2, 3, 4, 5, 6]
k_values = [1, 2, 3, 5, 8, 10, 15, 20]

start_time = time.time()
for m_val in m_values:
    for k_val in k_values:
        if time.time() - start_time > 300:  # 5分制限
            break
        result = measure_ks_for_Tm(m_val, k_val, n_samples=30000)
        if result is not None:
            numerical_results.append(result)
            print(f"  m={m_val}, k={k_val}: KS={result['ks_statistic']:.4f}, "
                  f"KS*sqrt(k)={result['ks_sqrt_k']:.4f}, "
                  f"skew={result['skewness']:.3f}, valid={result['n_valid']}")

# ============================================================
# Part 4: 同コスト比較の数値実験
# ============================================================

print("\n" + "=" * 70)
print("Part 4: 同コスト比較 (固定 total T-applications)")
print("=" * 70)

# 固定の total_cost = m * k での比較
equal_cost_results = {}
for total_cost in [10, 20, 30, 40, 50]:
    equal_cost_results[total_cost] = []
    for m_val in [1, 2, 5, 10]:
        k_val = total_cost // m_val
        if k_val < 1:
            continue
        result = measure_ks_for_Tm(m_val, k_val, n_samples=30000)
        if result is not None:
            equal_cost_results[total_cost].append(result)
            print(f"  total={total_cost}, m={m_val}, k={k_val}: "
                  f"KS={result['ks_statistic']:.4f}, skew={result['skewness']:.3f}")

# ============================================================
# Part 5: 最適m の理論的決定
# ============================================================

print("\n" + "=" * 70)
print("Part 5: 最適m の理論的分析")
print("=" * 70)

print("\n理論分析: Berry-Esseen的KS上界の同コスト比較")
print("  KS_m(N) <= C_BE * (rho_m / sigma_m^3) / sqrt(N/m)")
print("         = C_BE * (rho_1 / (sigma_1^3 * sqrt(m))) / sqrt(N/m)")
print("         = C_BE * (rho_1 / sigma_1^3) * (1/sqrt(m)) * sqrt(m/N)")
print("         = C_BE * (rho_1 / sigma_1^3) / sqrt(N)")
print("  -> m依存性が消える！BE的にはmによらず同じ！")
print()

# しかしEdgeworth展開の高次項で差が出る
print("Edgeworth展開からの補正:")
print("  F_k(x) = Phi(x) + phi(x) * [gamma3/(6*sqrt(k)) * He2(x) + ...]")
print("  T^m: gamma3_m = gamma3 / sqrt(m)")
print("  k_m = N/m steps")
print("  -> Edgeworth 1st term ~ gamma3_m / sqrt(k_m) = gamma3/sqrt(m) / sqrt(N/m) = gamma3/sqrt(N)")
print("  -> 1次Edgeworth項でもm依存性消滅！")
print()
print("  2次Edgeworth項: gamma4_m / k_m = (gamma4/m) / (N/m) = gamma4/N")
print("                 + gamma3_m^2 / k_m = (gamma3^2/m) / (N/m) = gamma3^2/N")
print("  -> 2次項でもm依存性消滅！")
print()
print("  結論: 独立近似が完全なら、T^m の最適m は存在しない（mによらず同等）")
print()

# ステップ間相関の効果
print("ただし、実際にはステップ間相関が存在する可能性がある。")
print("m大: 各T^mステップが長い分、ステップ間相関が減少する可能性")
print("     -> 独立近似の精度がm大で改善されるなら、m大が有利")
print()

# ============================================================
# Part 6: ステップ間相関のm依存性
# ============================================================

print("=" * 70)
print("Part 6: ステップ間相関のm依存性")
print("=" * 70)

def measure_correlation_Tm(m_val, n_samples=50000, n_steps=10):
    """T^m の連続ステップの増分間相関を測定"""
    log2_3 = np.log2(3)
    all_increments = [[] for _ in range(n_steps)]

    starts = np.random.randint(5*10**6, 10**7, size=n_samples * 3) * 2 + 1

    count = 0
    for n0 in starts:
        if count >= n_samples:
            break

        valid = True
        x = int(n0)
        incs = []

        for step in range(n_steps):
            x_prev = x
            for _ in range(m_val):
                x_next = collatz_T(x)
                if x_next == 1:
                    valid = False
                    break
                x = x_next
            if not valid:
                break
            incs.append(np.log2(x / x_prev))

        if valid and len(incs) == n_steps:
            for i, inc in enumerate(incs):
                all_increments[i].append(inc)
            count += 1

    if count < 100:
        return None

    # 各ステップの増分をnumpy配列に
    inc_arrays = [np.array(all_increments[i]) for i in range(n_steps)]

    # 隣接ステップ間の相関
    correlations_lag1 = []
    correlations_lag2 = []
    for i in range(n_steps - 1):
        corr = np.corrcoef(inc_arrays[i], inc_arrays[i+1])[0, 1]
        correlations_lag1.append(float(corr))
    for i in range(n_steps - 2):
        corr = np.corrcoef(inc_arrays[i], inc_arrays[i+2])[0, 1]
        correlations_lag2.append(float(corr))

    return {
        'm': m_val,
        'n_valid': count,
        'mean_corr_lag1': float(np.mean(correlations_lag1)),
        'std_corr_lag1': float(np.std(correlations_lag1)),
        'mean_corr_lag2': float(np.mean(correlations_lag2)),
        'std_corr_lag2': float(np.std(correlations_lag2)),
        'max_abs_corr_lag1': float(np.max(np.abs(correlations_lag1))),
    }

corr_results = []
for m_val in [1, 2, 3, 4, 5, 6, 8, 10]:
    if time.time() - start_time > 400:
        break
    cr = measure_correlation_Tm(m_val, n_samples=20000, n_steps=8)
    if cr is not None:
        corr_results.append(cr)
        print(f"  m={m_val}: mean_corr_lag1={cr['mean_corr_lag1']:.6f}, "
              f"max_|corr|={cr['max_abs_corr_lag1']:.6f}, "
              f"mean_corr_lag2={cr['mean_corr_lag2']:.6f}")

# ============================================================
# Part 7: KS の精密同コスト比較表
# ============================================================

print("\n" + "=" * 70)
print("Part 7: KS精密同コスト比較表")
print("=" * 70)

# 同コスト N (total T-applications) での KS を各 m で比較
precise_comparison = {}
for N in [12, 20, 30, 60]:
    precise_comparison[N] = {}
    print(f"\n  N = {N}:")
    for m_val in [1, 2, 3, 4, 5, 6]:
        k_val = N // m_val
        if k_val < 1:
            continue
        actual_N = m_val * k_val
        if actual_N != N:
            continue  # 割り切れない場合はスキップ

        result = measure_ks_for_Tm(m_val, k_val, n_samples=40000)
        if result is not None:
            precise_comparison[N][m_val] = result
            print(f"    m={m_val}, k={k_val}: KS={result['ks_statistic']:.5f}, "
                  f"skew={result['skewness']:.4f}, kurt={result['kurtosis_excess']:.4f}")

# ============================================================
# Part 8: 効率スコアの計算
# ============================================================

print("\n" + "=" * 70)
print("Part 8: 効率スコア (KS per unit cost)")
print("=" * 70)

# 固定k（ステップ数）でのKS比較：m増でKSがどう変わるか
print("\n固定ステップ数 k=10 での比較:")
fixed_k_results = {}
for m_val in [1, 2, 3, 4, 5, 6]:
    result = measure_ks_for_Tm(m_val, 10, n_samples=40000)
    if result is not None:
        fixed_k_results[m_val] = result
        print(f"  m={m_val}: KS={result['ks_statistic']:.5f}, cost={m_val*10}, "
              f"KS*cost={result['ks_statistic']*m_val*10:.4f}")

print("\n固定ステップ数 k=5 での比較:")
fixed_k5_results = {}
for m_val in [1, 2, 3, 4, 5, 6]:
    result = measure_ks_for_Tm(m_val, 5, n_samples=40000)
    if result is not None:
        fixed_k5_results[m_val] = result
        print(f"  m={m_val}: KS={result['ks_statistic']:.5f}, cost={m_val*5}, "
              f"KS*cost={result['ks_statistic']*m_val*5:.4f}")

# ============================================================
# Part 9: 結果の集約とJSON出力
# ============================================================

print("\n" + "=" * 70)
print("Part 9: 結果集約")
print("=" * 70)

# KS*sqrt(k) の m 依存性をまとめる
ks_sqrt_k_by_m = {}
for r in numerical_results:
    m = r['m']
    k = r['k']
    if m not in ks_sqrt_k_by_m:
        ks_sqrt_k_by_m[m] = []
    ks_sqrt_k_by_m[m].append({'k': k, 'ks_sqrt_k': r['ks_sqrt_k']})

print("\nKS*sqrt(k) の m 依存性:")
for m in sorted(ks_sqrt_k_by_m.keys()):
    vals = ks_sqrt_k_by_m[m]
    for v in sorted(vals, key=lambda x: x['k']):
        print(f"  m={m}, k={v['k']}: KS*sqrt(k) = {v['ks_sqrt_k']:.4f}")

# 理論的分析の要約
print("\n最終結論の理論分析:")
print("1. Berry-Esseen的に: 同コスト比較では m によらず KS ~ C/sqrt(N)")
print("2. Edgeworth展開でも: 同コスト比較では m 依存性が消滅")
print("3. 実質的にmを変えてもCLT収束速度は変わらない（独立近似が成立する限り）")
print("4. ステップ間相関の減少による微小改善の可能性はあるが、効果は限定的")

# 数値的に確認
if precise_comparison:
    print("\n数値的確認 (同コスト N=60):")
    if 60 in precise_comparison:
        for m, r in sorted(precise_comparison[60].items()):
            print(f"  m={m}, k={60//m}: KS={r['ks_statistic']:.5f}")

# JSON出力
output = {
    "title": "T^m最適基本マップ: CLT収束速度のm依存性分析",
    "approach": "T^m(m=1..6)の対数増分のモーメント・Berry-Esseen定数を理論計算し、同コスト(total T-applications = N)での KS距離を数値比較。Edgeworth展開による理論分析も実施。",
    "findings": [],
    "hypotheses": [],
    "dead_ends": [],
    "theory_moments": theory_results,
    "numerical_ks": numerical_results,
    "correlation_by_m": corr_results,
    "equal_cost_comparison": {str(k): v for k, v in equal_cost_results.items()},
    "precise_comparison": {str(k): {str(m): v for m, v in d.items()} for k, d in precise_comparison.items()},
    "fixed_k10": {str(m): v for m, v in fixed_k_results.items()},
    "fixed_k5": {str(m): v for m, v in fixed_k5_results.items()},
}

# findings, hypotheses, dead_ends は最後に追加
print("\n計算完了。JSON出力を生成中...")

with open('/Users/soyukke/study/lean-unsolved/results/Tm_optimal_clt_comparison.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("JSON saved.")
