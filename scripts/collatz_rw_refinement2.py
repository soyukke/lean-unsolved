#!/usr/bin/env python3
"""
Syracuse軌道のlog2スケールRW近似 精密化 (修正版)

修正点:
1. KS検定: survivor biasを除去。kステップ後にまだ1に未到達かつ初期値以上の軌道のみで比較するのではなく、
   全軌道のS_kを使って正規近似を検証する。ただし有限バッファ効果を考慮。
2. ST定義: total stopping time (1に到達するまで) を使用。
3. 自己相関: v2(3n+1)の値の系列について測定（log変化量ではなく直接）。
4. 条件付きドリフト: n mod 2^k は最初のステップのv2を完全に決定する → 2次以上の相関を測定。
"""

import math
import random
import time
from collections import Counter, defaultdict

# ============================================================
# 基本関数
# ============================================================

def syracuse(n):
    """Syracuse関数。戻り値: (T(n), v2(3n+1))"""
    m = 3 * n + 1
    v = 0
    while m % 2 == 0:
        m //= 2
        v += 1
    return m, v

def total_stopping_time(n):
    """1に到達するまでのSyracuseステップ数"""
    steps = 0
    current = n
    while current != 1:
        current, _ = syracuse(current)
        steps += 1
        if steps > 500000:
            return -1
    return steps

def first_drop_time(n):
    """初めて n 未満になるまでのステップ数"""
    original = n
    steps = 0
    current = n
    while current >= original:
        if current == 1 and n != 1:
            return steps
        current, _ = syracuse(current)
        steps += 1
        if steps > 50000:
            return -1
    return steps

# ============================================================
# パートA: v2系列の精密統計（連続相関構造）
# ============================================================

def analyze_v2_series(N_max, traj_length=200, n_traj=5000):
    """
    Syracuse軌道上の v2(3*n_k+1) 系列の統計的性質を精密に測定。
    特に:
    - 各ステップでのv2の条件付き分布
    - 連続するv2値間の相互情報量の近似
    - v2ペアの同時分布
    """
    print("=" * 70)
    print("パートA: v2系列の精密統計")
    print("=" * 70)

    random.seed(42)
    starts = [random.randrange(3, N_max, 2) for _ in range(n_traj)]

    # v2 系列を収集
    all_v2_series = []
    for n in starts:
        current = n
        series = []
        for _ in range(traj_length):
            if current == 1:
                break
            current, v = syracuse(current)
            series.append(v)
        if len(series) >= 50:
            all_v2_series.append(series)

    print(f"  有効軌道数: {len(all_v2_series)}")

    # v2の全体統計
    all_v2 = [v for s in all_v2_series for v in s[10:]]  # 最初10を捨てる
    n_total = len(all_v2)
    mean_v2 = sum(all_v2) / n_total
    var_v2 = sum((v - mean_v2)**2 for v in all_v2) / (n_total - 1)

    print(f"\n  全体統計 (最初10ステップ除外後):")
    print(f"    サンプル数: {n_total}")
    print(f"    E[v2]  = {mean_v2:.8f}  (理論: 2.0)")
    print(f"    Var[v2] = {var_v2:.8f}  (理論: 2.0)")

    # v2 の分布
    v2_counter = Counter(all_v2)
    print(f"\n  v2分布:")
    print(f"    {'v':>3s}  {'P(v2=v)観測':>12s}  {'P(v2=v)幾何':>12s}  {'比率':>8s}")
    for v in range(1, 16):
        obs = v2_counter.get(v, 0) / n_total
        geo = 1.0 / (2**v)
        ratio = obs / geo if geo > 0 else 0
        print(f"    {v:3d}  {obs:12.8f}  {geo:12.8f}  {ratio:8.5f}")

    # v2ペアの同時分布: P(v2_{k+1}=j | v2_k=i)
    pair_counts = defaultdict(lambda: defaultdict(int))
    single_counts = defaultdict(int)

    for series in all_v2_series:
        for i in range(10, len(series)-1):
            pair_counts[series[i]][series[i+1]] += 1
            single_counts[series[i]] += 1

    print(f"\n  条件付き分布 P(v2_{{k+1}}=j | v2_k=i):")
    print(f"    {'i\\j':>5s}", end="")
    for j in range(1, 8):
        print(f"  {f'j={j}':>8s}", end="")
    print(f"  {'E[j|i]':>8s}  {'N':>8s}")

    for i in range(1, 8):
        total_i = single_counts[i]
        if total_i < 100:
            continue
        print(f"    i={i:2d}", end="")
        cond_mean = 0
        for j in range(1, 8):
            p_cond = pair_counts[i].get(j, 0) / total_i
            cond_mean += j * p_cond
            print(f"  {p_cond:8.4f}", end="")
        # j>=8の寄与を加える
        for j in range(8, 30):
            p_cond = pair_counts[i].get(j, 0) / total_i
            cond_mean += j * p_cond
        print(f"  {cond_mean:8.4f}  {total_i:8d}")

    # 条件付き平均のばらつきを定量化
    cond_means = {}
    for i in range(1, 10):
        if single_counts[i] >= 100:
            total_i = single_counts[i]
            cm = sum(j * pair_counts[i].get(j, 0) for j in range(1, 50)) / total_i
            cond_means[i] = cm

    if cond_means:
        cm_vals = list(cond_means.values())
        cm_spread = max(cm_vals) - min(cm_vals)
        print(f"\n  E[v2_{{k+1}} | v2_k=i] のスプレッド: {cm_spread:.6f}")
        print(f"  → i.i.d.なら全て2.0になるはず")
        print(f"  → 最大偏差: {max(abs(v-2.0) for v in cm_vals):.6f}")

    return {
        'mean_v2': mean_v2, 'var_v2': var_v2,
        'cond_means': cond_means
    }


# ============================================================
# パートB: 正規近似のKS検定（修正版）
# ============================================================

def ks_test_corrected(N_max, step_counts=[5, 10, 20, 50]):
    """
    修正版KS検定:
    大きな開始値からスタートして、kステップ後の log2(T^k(n)) - log2(n) の分布を
    N(k*mu, k*sigma^2) と比較。開始値をlog2(n) >> kなら1に到達しない。
    """
    print("\n" + "=" * 70)
    print("パートB: 正規近似のKS検定（修正版: 大初期値使用）")
    print("=" * 70)

    mu = math.log2(3) - 2  # ≈ -0.41504
    sigma2 = 2.0

    results = {}

    for k in step_counts:
        # 十分大きな奇数を使って survivorship bias を回避
        # k*|mu| << log2(n) を保証
        min_start = 2**(int(k * 3) + 10)  # log2(n) >> k*|mu|
        max_start = min_start * 10

        sample_size = 30000
        random.seed(42 + k)

        S_k_values = []
        for _ in range(sample_size):
            n = random.randrange(min_start + 1, max_start, 2)  # 奇数
            s = 0.0
            current = n
            for step in range(k):
                next_val, v = syracuse(current)
                s += math.log2(next_val) - math.log2(current)
                current = next_val
            S_k_values.append(s)

        n_z = len(S_k_values)
        expected_mean = k * mu
        expected_std = math.sqrt(k * sigma2)

        obs_mean = sum(S_k_values) / n_z
        obs_var = sum((x - obs_mean)**2 for x in S_k_values) / (n_z - 1)
        obs_std = math.sqrt(obs_var)

        # KS検定: S_k を理論N(k*mu, k*sigma^2)と比較
        z_values = sorted([(x - expected_mean) / expected_std for x in S_k_values])

        ks_stat = 0.0
        for i, z in enumerate(z_values):
            F_n = (i + 1) / n_z
            F_n_minus = i / n_z
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks_stat = max(ks_stat, abs(F_n - Phi), abs(F_n_minus - Phi))

        ks_critical_005 = 1.36 / math.sqrt(n_z)
        ks_critical_001 = 1.63 / math.sqrt(n_z)

        # 観測平均を使って再標準化したKS検定
        z_values2 = sorted([(x - obs_mean) / obs_std for x in S_k_values])
        ks_stat2 = 0.0
        for i, z in enumerate(z_values2):
            F_n = (i + 1) / n_z
            F_n_minus = i / n_z
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks_stat2 = max(ks_stat2, abs(F_n - Phi), abs(F_n_minus - Phi))

        reject_005 = "棄却" if ks_stat > ks_critical_005 else "受容"
        reject2_005 = "棄却" if ks_stat2 > ks_critical_005 else "受容"

        # S_kの歪度と尖度
        skew = sum((x - obs_mean)**3 for x in S_k_values) / (n_z * obs_std**3)
        kurt = sum((x - obs_mean)**4 for x in S_k_values) / (n_z * obs_std**4) - 3

        print(f"\n  k={k} ステップ (n: [{math.log2(min_start):.0f},{math.log2(max_start):.0f}]bit)")
        print(f"    サンプル数: {n_z}")
        print(f"    観測平均: {obs_mean:.6f}, 理論平均: {expected_mean:.6f}")
        print(f"    観測std:  {obs_std:.6f},  理論std:  {expected_std:.6f}")
        print(f"    平均比:   {obs_mean/expected_mean:.6f}, std比: {obs_std/expected_std:.6f}")
        print(f"    歪度: {skew:.6f}, 尖度: {kurt:.6f}")
        print(f"    KS(理論パラメータ): {ks_stat:.6f}, 臨界(5%): {ks_critical_005:.6f} → {reject_005}")
        print(f"    KS(観測パラメータ): {ks_stat2:.6f}, 臨界(5%): {ks_critical_005:.6f} → {reject2_005}")

        results[k] = {
            'n_samples': n_z,
            'obs_mean': obs_mean, 'theory_mean': expected_mean,
            'obs_std': obs_std, 'theory_std': expected_std,
            'skewness': skew, 'kurtosis': kurt,
            'ks_theory': ks_stat, 'ks_observed': ks_stat2,
            'ks_critical_005': ks_critical_005,
            'reject_theory': reject_005, 'reject_observed': reject2_005,
        }

    return results


# ============================================================
# パートC: Total Stopping Time分布 vs RWモデル
# ============================================================

def total_st_vs_rw(N_max):
    """
    Total stopping time (1到達まで) の分布を RW モデルと比較。
    """
    print("\n" + "=" * 70)
    print(f"パートC: Total Stopping Time分布 vs RWモデル (N_max={N_max})")
    print("=" * 70)

    mu = math.log2(3) - 2
    sigma2 = 2.0

    # 実測TST
    tst_values = []
    for n in range(3, N_max + 1, 2):
        tst = total_stopping_time(n)
        if tst >= 0:
            tst_values.append((n, tst))

    tst_only = [t for _, t in tst_values]
    total = len(tst_only)
    mean_tst = sum(tst_only) / total
    var_tst = sum((x - mean_tst)**2 for x in tst_only) / (total - 1)

    # 理論平均: E[TST(n)] ≈ log2(n) / |mu|
    avg_log2n = sum(math.log2(n) for n, _ in tst_values) / total
    theory_mean = avg_log2n / abs(mu)

    print(f"\n  サンプル数: {total}")
    print(f"  実測 E[TST]  = {mean_tst:.4f}")
    print(f"  理論 E[TST]  = {theory_mean:.4f}")
    print(f"  比率         = {mean_tst / theory_mean:.6f}")
    print(f"  実測 Var[TST] = {var_tst:.4f}")
    print(f"  実測 std[TST] = {math.sqrt(var_tst):.4f}")
    print(f"  max TST      = {max(tst_only)}")

    # RWシミュレーション
    n_rw = 100000
    random.seed(999)
    rw_tst = []
    for _ in range(n_rw):
        log2n = random.uniform(math.log2(3), math.log2(N_max))
        s = log2n
        k = 0
        while s > 0 and k < 50000:
            v = 1
            while random.random() < 0.5:
                v += 1
            s += math.log2(3) - v
            k += 1
        rw_tst.append(k)

    rw_mean = sum(rw_tst) / len(rw_tst)
    rw_var = sum((x - rw_mean)**2 for x in rw_tst) / (len(rw_tst) - 1)

    print(f"\n  RW E[TST]    = {rw_mean:.4f}")
    print(f"  RW Var[TST]  = {rw_var:.4f}")
    print(f"  実測/RW比     = {mean_tst / rw_mean:.6f}")

    # log2(n) で正規化した TST の分布
    # 正規化: TST(n) / log2(n) → 1/|mu| ≈ 2.41 に集中するはず
    normalized = [t / math.log2(n) for n, t in tst_values if math.log2(n) > 5]
    norm_mean = sum(normalized) / len(normalized)
    norm_var = sum((x - norm_mean)**2 for x in normalized) / (len(normalized) - 1)
    theory_ratio = 1.0 / abs(mu)

    print(f"\n  正規化 TST/log2(n):")
    print(f"    実測平均   = {norm_mean:.6f}")
    print(f"    理論値     = {theory_ratio:.6f}")
    print(f"    比率       = {norm_mean / theory_ratio:.6f}")
    print(f"    分散       = {norm_var:.6f}")

    # ビン別比較
    tst_counter = Counter(tst_only)
    bin_size = 10
    max_bin = min(max(tst_only) + bin_size, 300)
    rw_counter = Counter(rw_tst)

    print(f"\n  {'TSTビン':>12s}  {'実測':>10s}  {'RW':>10s}  {'比率':>8s}")
    for b_start in range(0, max_bin, bin_size):
        b_end = b_start + bin_size
        obs_f = sum(1 for s in tst_only if b_start <= s < b_end) / total
        rw_f = sum(1 for s in rw_tst if b_start <= s < b_end) / len(rw_tst)
        ratio = obs_f / rw_f if rw_f > 1e-6 else 0
        if obs_f > 1e-6 or rw_f > 1e-5:
            print(f"  [{b_start:3d},{b_end:3d})  {obs_f:10.6f}  {rw_f:10.6f}  {ratio:8.4f}")

    return {
        'mean_tst': mean_tst, 'theory_mean': theory_mean,
        'var_tst': var_tst, 'rw_mean': rw_mean, 'rw_var': rw_var,
        'norm_mean': norm_mean, 'theory_ratio': theory_ratio,
    }


# ============================================================
# パートD: 分散の精密理論値と高次補正
# ============================================================

def variance_refinement():
    """
    RWモデルの分散の理論値を高精度で導出し、実測と比較。

    v2 ~ Geom(1/2) on {1,2,...}: E[v2]=2, Var[v2]=2
    X = log2(3) - v2: E[X] = log2(3)-2, Var[X] = Var[v2] = 2

    しかし実際のv2は独立ではなく、mod構造に依存。
    2ステップの共分散 Cov(X_k, X_{k+1}) を理論的に評価。
    """
    print("\n" + "=" * 70)
    print("パートD: 分散の精密理論値と高次補正")
    print("=" * 70)

    L2 = math.log(2)
    L3 = math.log(3)

    # 基本量
    mu_ln = L3 - 2*L2  # 自然対数ベース
    mu_log2 = math.log2(3) - 2

    # MGF: M(t) = 3^t / (2^{t+1} - 1)
    # Lambda(t) = t*ln3 - ln(2^{t+1}-1)
    # Lambda'(0) = ln3 - 2*ln2*2/(2-1) = ln3 - 2*ln2 = mu_ln ✓
    # Lambda''(0) = 4*(ln2)^2*1 / (2-1)^2 = 4*(ln2)^2 ← 自然対数ベースの分散

    var_ln = 4 * L2**2  # NG: 再計算

    # 正しい計算:
    # E[v2] = sum_{j=1}^inf j/2^j = 2
    # E[v2^2] = sum_{j=1}^inf j^2/2^j = 6
    # Var[v2] = 6 - 4 = 2
    # X = log2(3) - v2
    # Var[X] = Var[v2] = 2 (log2ベース)

    # 自然対数ベース:
    # X_ln = ln(3) - v2*ln(2)
    # Var[X_ln] = (ln2)^2 * Var[v2] = 2*(ln2)^2

    var_log2 = 2.0  # Var[v2]
    var_nat = 2 * L2**2

    print(f"  基本パラメータ:")
    print(f"    mu (log2) = {mu_log2:.10f}")
    print(f"    mu (ln)   = {mu_ln:.10f}")
    print(f"    Var (log2) = {var_log2:.10f}")
    print(f"    Var (ln)   = {var_nat:.10f}")
    print(f"    sigma (log2) = {math.sqrt(var_log2):.10f}")

    # CLTによるTST(n)の分散の理論値
    # TST ≈ first passage time of S_k to level -log2(n)
    # Wald's identity: E[TST] = log2(n)/|mu|
    # Var[TST] ≈ sigma^2 * log2(n) / |mu|^3

    # より正確には、first passage time の分散:
    # For RW with drift mu<0, Var[tau_x] = sigma^2 * x / |mu|^3
    # where tau_x = first time S_k < -x

    print(f"\n  TST(n)の分散の理論予測:")
    print(f"    Var[TST(n)] ≈ sigma^2 * log2(n) / |mu|^3")
    print(f"    sigma^2/|mu|^3 = {var_log2 / abs(mu_log2)**3:.6f}")

    for bits in [10, 15, 20]:
        log2n = bits
        var_pred = var_log2 * log2n / abs(mu_log2)**3
        mean_pred = log2n / abs(mu_log2)
        cv_pred = math.sqrt(var_pred) / mean_pred
        print(f"    log2(n)={bits}: E[TST]≈{mean_pred:.1f}, Var[TST]≈{var_pred:.1f}, CV≈{cv_pred:.4f}")

    # Cramer関数の精密計算
    # I(x) = sup_t (t*x - Lambda(t))
    # Lambda(t) = t*log2(3) - log2(2^{t+1}-1)   ← log2ベース

    # I(0) を精密計算: I(0) = -Lambda(t*) where Lambda'(t*) = 0
    # Lambda'(t) = log2(3) - 2^{t+1}*ln2 / ((2^{t+1}-1)*ln2) = log2(3) - 2^{t+1}/(2^{t+1}-1)
    # ← 注意: log2ベースとlnベースの変換

    # lnベースで:
    # Lambda_ln(t) = t*ln3 - ln(2^{t+1}-1)
    # Lambda_ln'(t) = ln3 - 2^{t+1}*ln2/(2^{t+1}-1) = 0
    # → 2^{t+1}*ln2/(2^{t+1}-1) = ln3
    # → 2^{t+1} = ln3/(ln3-ln2) * (ただし近似解が必要)

    # 数値的に求める
    def Lambda_ln(t):
        if 2**(t+1) <= 1:
            return float('-inf')
        return t*L3 - math.log(2**(t+1) - 1)

    def Lambda_ln_prime(t):
        return L3 - 2**(t+1)*L2/(2**(t+1) - 1)

    # t* を二分法で求める
    lo, hi = -0.99, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if Lambda_ln_prime(mid) > 0:
            lo = mid
        else:
            hi = mid
    t_star = (lo + hi) / 2

    I_0 = -Lambda_ln(t_star)
    I_0_log2 = I_0 / L2  # log2ベースに変換

    print(f"\n  Cramer関数 I(0) の精密計算:")
    print(f"    t* = {t_star:.10f}")
    print(f"    Lambda(t*) = {Lambda_ln(t_star):.10f}")
    print(f"    I(0) [ln]  = {I_0:.10f}")
    print(f"    I(0) [log2] = {I_0_log2:.10f}")
    print(f"    既知値      = 0.05498")
    print(f"    差          = {abs(I_0_log2 - 0.05498):.2e}")

    # 尾部指数との関係
    # P(ST > t) ~ C * exp(-I(0) * t) for the RW model
    # ただし first passage の場合: lambda = I(0) ではなく、
    # lambda = (rate of exponential decay of P(max S_k >=0 for k>=t))
    # 正確には lambda は方程式 Lambda(t) = 0 の正の根に関係

    # Lambda_ln(theta) = 0 を解く（theta > 0）
    lo, hi = 0.001, 5.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if Lambda_ln(mid) > 0:
            lo = mid
        else:
            hi = mid
    theta_star = (lo + hi) / 2

    print(f"\n  尾部指数の理論:")
    print(f"    Lambda(theta)=0 の正根: theta = {theta_star:.10f}")
    print(f"    → P(ST > t) ~ exp(-theta * t) [lnベース]")
    print(f"    → lnベース減衰率: {theta_star:.6f}")
    print(f"    → P(ST > t) ~ exp(-theta/ln2 * t) [log2ベースステップ数]")
    print(f"    注: STのステップ数は離散、tは連続パラメータ")

    # First passage の正確な尾部指数:
    # P(tau > k) ~ C * r^k where r = inf{r>0: E[r^{-1} e^{theta X}]=1} 的な解析
    # 実際にはRenewal理論: P(tau>k) ~ C * exp(-alpha*k)
    # alpha = unique positive solution of E[exp(alpha*X)] = 1 (Xはステップの増分)
    # これはLambda(alpha) = 0 と同値

    print(f"\n  結論: 尾部指数 alpha (P(tau>k)~exp(-alpha*k)):")
    print(f"    alpha = theta_star = {theta_star:.8f}")
    print(f"    exp(-alpha) = {math.exp(-theta_star):.8f}")
    print(f"    既知値 0.0735 との比較: {theta_star:.6f} vs 0.0735")

    return {
        'mu_log2': mu_log2, 'var_log2': var_log2,
        't_star': t_star, 'I_0_ln': I_0, 'I_0_log2': I_0_log2,
        'theta_star': theta_star,
    }


# ============================================================
# パートE: Berry-Esseen型の補正項
# ============================================================

def berry_esseen_correction(N_max, k_values=[10, 20, 50, 100]):
    """
    Berry-Esseen定理による正規近似の誤差上界を計算し、
    実測のKSずれと比較。

    |P(S_k <= x) - Phi(x)| <= C * rho / (sigma^3 * sqrt(k))
    where rho = E[|X-mu|^3]
    """
    print("\n" + "=" * 70)
    print("パートE: Berry-Esseen補正")
    print("=" * 70)

    mu = math.log2(3) - 2
    sigma2 = 2.0
    sigma = math.sqrt(sigma2)

    # E[|X-mu|^3] を計算
    # X = log2(3) - v2, mu = log2(3) - 2
    # X - mu = 2 - v2
    # |X-mu|^3 = |2-v2|^3
    # E[|2-v2|^3] = sum_{j=1}^inf |2-j|^3 / 2^j

    rho = 0
    for j in range(1, 50):
        rho += abs(2 - j)**3 / (2**j)

    print(f"  E[|X-mu|^3] = {rho:.10f}")
    print(f"  sigma^3 = {sigma**3:.10f}")
    print(f"  rho/sigma^3 = {rho/sigma**3:.10f}")

    # Berry-Esseen bound: C_BE * rho / (sigma^3 * sqrt(k))
    C_BE = 0.4748  # Shevtsova (2010) の最良定数

    print(f"  Berry-Esseen定数 C_BE = {C_BE}")

    for k in k_values:
        be_bound = C_BE * rho / (sigma**3 * math.sqrt(k))
        print(f"    k={k:3d}: BE上界 = {be_bound:.6f}")

    # 実測との比較（パートBと同様の実験）
    print(f"\n  実測KSとの比較 (N_max={N_max}):")
    results = {}
    for k in k_values:
        min_start = 2**(int(k * 3) + 10)
        max_start = min_start * 10
        sample_size = 20000
        random.seed(42 + k)

        S_k_values = []
        for _ in range(sample_size):
            n = random.randrange(min_start + 1, max_start, 2)
            s = 0.0
            current = n
            for step in range(k):
                next_val, v = syracuse(current)
                s += math.log2(next_val) - math.log2(current)
                current = next_val
            S_k_values.append(s)

        obs_mean = sum(S_k_values) / len(S_k_values)
        obs_std = math.sqrt(sum((x - obs_mean)**2 for x in S_k_values) / (len(S_k_values) - 1))

        # 観測パラメータでのKS
        z_values = sorted([(x - obs_mean) / obs_std for x in S_k_values])
        ks = 0.0
        for i, z in enumerate(z_values):
            F_n = (i + 1) / len(z_values)
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks = max(ks, abs(F_n - Phi))

        be_bound = C_BE * rho / (sigma**3 * math.sqrt(k))

        print(f"    k={k:3d}: KS実測={ks:.6f}, BE上界={be_bound:.6f}, "
              f"比率={ks/be_bound:.4f}")

        results[k] = {'ks': ks, 'be_bound': be_bound, 'ratio': ks/be_bound}

    return results


# ============================================================
# メイン実行
# ============================================================

if __name__ == '__main__':
    t_start = time.time()
    print("Syracuse軌道 log2スケールRW近似 精密化 (修正版)")
    print("=" * 70)

    # パートA: v2系列の精密統計
    v2_results = analyze_v2_series(10**7, traj_length=200, n_traj=3000)

    # パートB: KS検定（修正版）
    ks_results = ks_test_corrected(10**6, step_counts=[5, 10, 20, 50, 100])

    # パートC: TST分布 vs RW
    tst_results = total_st_vs_rw(200000)

    # パートD: 分散の精密理論値
    var_results = variance_refinement()

    # パートE: Berry-Esseen
    be_results = berry_esseen_correction(10**6, k_values=[10, 20, 50, 100, 200])

    elapsed = time.time() - t_start
    print(f"\n\n{'=' * 70}")
    print(f"総実行時間: {elapsed:.1f}秒")

    # 総合サマリー
    print("\n\n" + "=" * 70)
    print("総合サマリー")
    print("=" * 70)
    print(f"\n1. v2の条件付き独立性:")
    if v2_results['cond_means']:
        max_dev = max(abs(v - 2.0) for v in v2_results['cond_means'].values())
        print(f"   E[v2_{{k+1}}|v2_k=i] の最大偏差: {max_dev:.6f}")
        print(f"   → {'有意な依存性あり' if max_dev > 0.05 else 'ほぼ独立'}")

    print(f"\n2. KS検定 (survivorship bias 除去後):")
    for k, res in ks_results.items():
        print(f"   k={k}: KS(理論)={res['ks_theory']:.6f}, "
              f"KS(観測)={res['ks_observed']:.6f}, "
              f"歪度={res['skewness']:.4f}, 尖度={res['kurtosis']:.4f} "
              f"→ {res['reject_theory']} / {res['reject_observed']}")

    print(f"\n3. TST分布:")
    print(f"   実測E[TST]={tst_results['mean_tst']:.2f}, "
          f"理論={tst_results['theory_mean']:.2f}, "
          f"比率={tst_results['mean_tst']/tst_results['theory_mean']:.4f}")
    print(f"   正規化平均 TST/log2(n) = {tst_results['norm_mean']:.6f} "
          f"(理論: {tst_results['theory_ratio']:.6f})")

    print(f"\n4. Cramer関数:")
    print(f"   I(0) = {var_results['I_0_log2']:.8f}")
    print(f"   尾部指数 theta* = {var_results['theta_star']:.8f}")

    print(f"\n5. Berry-Esseen:")
    for k, res in be_results.items():
        print(f"   k={k}: 実測/上界 = {res['ratio']:.4f}")
