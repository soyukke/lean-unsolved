#!/usr/bin/env python3
"""
Syracuse軌道 log2スケールRW近似 最終精密化

Cramer関数とtail exponentの正確な数値計算を含む。
"""

import math
import random
import time
from collections import Counter, defaultdict

L2 = math.log(2)
L3 = math.log(3)

# ============================================================
# パート1: MGFとCramer関数の正確な数値計算
# ============================================================

def compute_mgf_and_cramer():
    """
    X = ln(3) - v2 * ln(2)  where v2 ~ Geom(1/2) on {1,2,...}

    MGF: M(t) = E[e^{tX}] = e^{t*ln3} * sum_{j=1}^inf (e^{-t*ln2}/2)^j
             = e^{t*ln3} * (e^{-t*ln2}/2) / (1 - e^{-t*ln2}/2)
             = 3^t / (2^{t+1} - 1)     (for 2^{t+1} > 1, i.e., t > -1/ln2)

    CGF: Lambda(t) = ln M(t) = t*ln3 - ln(2^{t+1} - 1)
    """
    print("=" * 70)
    print("パート1: MGF/CGF/Cramer関数の正確な計算")
    print("=" * 70)

    def Lambda(t):
        """Cumulant generating function (natural log base)"""
        val = 2**(t+1) - 1
        if val <= 0:
            return float('-inf')
        return t * L3 - math.log(val)

    def Lambda_prime(t):
        """dLambda/dt"""
        val = 2**(t+1)
        return L3 - val * L2 / (val - 1)

    def Lambda_double_prime(t):
        """d^2 Lambda/dt^2"""
        val = 2**(t+1)
        return val * L2**2 / (val - 1)**2

    # 基本量の確認
    print(f"\n  Lambda(0) = {Lambda(0):.10f}  (should be 0)")
    print(f"  Lambda'(0) = {Lambda_prime(0):.10f}")
    print(f"  理論 E[X] = ln3-2*ln2 = {L3-2*L2:.10f}")
    print(f"  Lambda''(0) = {Lambda_double_prime(0):.10f}")
    print(f"  理論 Var[X] = 2*(ln2)^2 = {2*L2**2:.10f}")

    # --- Cramer関数 I(x) = sup_t {tx - Lambda(t)} ---
    # I(0) を計算: sup_t {-Lambda(t)} = -inf_t {Lambda(t)}
    # Lambda'(t*) = 0 を解く

    # Lambda'(t) = ln3 - 2^{t+1}*ln2/(2^{t+1}-1) = 0
    # → 2^{t+1}*ln2/(2^{t+1}-1) = ln3
    # → 2^{t+1} = ln3/(ln3-ln2) = ln3/ln(3/2)
    # → t+1 = log2(ln3/ln(3/2))
    # → t* = log2(ln3/ln(3/2)) - 1

    t_star_exact = math.log2(L3 / math.log(1.5)) - 1
    print(f"\n  t* (Lambda'=0の解):")
    print(f"    解析解: t* = log2(ln3/ln(3/2)) - 1 = {t_star_exact:.10f}")
    print(f"    検証 Lambda'(t*) = {Lambda_prime(t_star_exact):.2e}")
    print(f"    Lambda(t*) = {Lambda(t_star_exact):.10f}")

    I_0 = -Lambda(t_star_exact)
    print(f"    I(0) = -Lambda(t*) = {I_0:.10f}")
    print(f"    I(0)/ln2 (log2ベース) = {I_0/L2:.10f}")

    # 別の表現: I(0) = -t*ln3 + ln(2^{t*+1}-1)
    # = -(log2(ln3/ln(3/2))-1)*ln3 + ln(2^{log2(ln3/ln(3/2))}-1)
    # = -(log2(ln3/ln(3/2))-1)*ln3 + ln(ln3/ln(3/2) - 1)
    # = -(log2(ln3/ln(3/2))-1)*ln3 + ln(ln2/ln(3/2))

    alt_I0 = -(t_star_exact)*L3 + math.log(L3/math.log(1.5) - 1)
    print(f"    I(0) [別表現] = {alt_I0:.10f}")

    # --- 尾部指数: Lambda(theta) = 0 の正の根 ---
    # theta*ln3 - ln(2^{theta+1}-1) = 0
    # → 3^theta = 2^{theta+1} - 1
    # → 3^theta + 1 = 2^{theta+1} = 2*2^theta
    # → 3^theta + 1 = 2*2^theta

    # Newton法で解く
    def f(t):
        return Lambda(t)

    def f_prime(t):
        return Lambda_prime(t)

    # theta > 0 の範囲で Lambda(theta) = 0 を探す
    # Lambda(0) = 0 は自明な根
    # Lambda'(0) < 0 なので Lambda は0の直後で負
    # Lambda(t) → +inf as t → inf (3^t項が支配)
    # よって正の根が存在する

    # まず範囲を特定
    print(f"\n  Lambda の値:")
    for t in [0, 0.5, 1, 2, 3, 4, 5, 6, 7, 8]:
        print(f"    Lambda({t}) = {Lambda(t):.6f}")

    # Newton法 (t=5付近からスタート)
    t = 5.0
    for _ in range(50):
        lt = Lambda(t)
        lpt = Lambda_prime(t)
        if abs(lpt) < 1e-15:
            break
        t_new = t - lt / lpt
        if abs(t_new - t) < 1e-14:
            t = t_new
            break
        t = t_new

    theta_star = t
    print(f"\n  尾部指数 theta*:")
    print(f"    theta* = {theta_star:.15f}")
    print(f"    Lambda(theta*) = {Lambda(theta_star):.2e}")
    print(f"    検証: 3^theta = {3**theta_star:.6f}")
    print(f"    検証: 2^(theta+1)-1 = {2**(theta_star+1)-1:.6f}")

    # exp(-theta*) は各ステップの「生存確率の指数」
    # P(tau > k) ~ C * exp(-theta* * k) for large k
    # ただしこれはln(T(n)/n)のRWモデルでのfirst passage time

    # log2ベースでの尾部指数
    alpha_log2 = theta_star * L2  # ← 変換が必要か再考
    # 実際: S_k (lnベース) < -ln(n) の first passage
    # ステップ k でのtotal declining rate

    print(f"\n  P(tau > k) ~ exp(-theta* * k):")
    print(f"    theta* = {theta_star:.10f}")

    # これは ln ベースのRW X_i = ln3 - v2*ln2 に対する
    # Lambda(theta) = 0 の正の根
    # RWの first passage time tau = min{k: S_k < -c} の尾部は
    # P(tau > k) ~ C * phi(theta*) * exp(-theta* * k) (ただし phi は調整関数)

    # しかし theta* ≈ 5.97 は非常に大きい → 指数減衰率が速すぎないか?
    # exp(-5.97) ≈ 0.0025 → P(tau>k+1)/P(tau>k) ≈ 0.25%

    # 実測では P(ST>t) ~ exp(-0.07*t) 程度 → 指数 ≈ 0.07
    # これは log2 ベースの ST に対する値

    # 混乱を整理: Syracuse ST は log2 ステップ、X_i は各ステップの log2 変化
    # X_i (log2) = log2(3) - v2_i
    # E[X_i] = log2(3) - 2 ≈ -0.415
    # Lambda_{log2}(t) = t*log2(3) + ln(sum 2^{-j} * e^{-t*j}), j=1,...,inf

    # log2ベースMGF: M_{log2}(t) = E[e^{t*X_log2}] = E[e^{t*(log2(3)-v2)}]
    #   = e^{t*log2(3)} * E[e^{-t*v2}]
    #   = e^{t*log2(3)} * sum_{j=1}^inf 2^{-j} e^{-tj}
    #   = e^{t*log2(3)} * e^{-t}/(2-e^{-t}) for e^{-t} < 2

    def Lambda_log2(t):
        """CGF for X in log2 base"""
        exp_neg_t = math.exp(-t)
        if exp_neg_t >= 2:
            return float('inf')
        return t * math.log2(3) + math.log(exp_neg_t / (2 - exp_neg_t))

    def Lambda_log2_prime(t):
        exp_neg_t = math.exp(-t)
        # d/dt [t*log2(3)] = log2(3)
        # d/dt [ln(e^{-t}/(2-e^{-t}))] = -1 + e^{-t}/(2-e^{-t}) = -1 + exp_neg_t/(2-exp_neg_t)
        # = (-2+exp_neg_t+exp_neg_t)/(2-exp_neg_t) = (2*exp_neg_t-2)/(2-exp_neg_t)
        # = -2*(1-exp_neg_t)/(2-exp_neg_t)
        return math.log2(3) - 1 + exp_neg_t/(2 - exp_neg_t)
        # 展開すると log2(3) - 2/(2-e^{-t})

    print(f"\n  log2ベースCGF:")
    print(f"    Lambda_log2(0) = {Lambda_log2(0):.10f}")
    print(f"    Lambda_log2'(0) = {Lambda_log2_prime(0):.10f}")
    print(f"    理論 E[X_log2] = {math.log2(3)-2:.10f}")

    # Lambda_log2(theta) = 0 の正の根を求める
    for t_test in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]:
        print(f"    Lambda_log2({t_test}) = {Lambda_log2(t_test):.6f}")

    # Newton法
    t = 0.1
    for _ in range(100):
        lt = Lambda_log2(t)
        lpt = Lambda_log2_prime(t)
        if abs(lpt) < 1e-15:
            break
        t_new = t - lt / lpt
        if t_new < 0.001:
            t_new = 0.001
        if abs(t_new - t) < 1e-14:
            t = t_new
            break
        t = t_new

    theta_log2 = t
    print(f"\n  log2ベース尾部指数:")
    print(f"    theta_log2 = {theta_log2:.15f}")
    print(f"    Lambda_log2(theta_log2) = {Lambda_log2(theta_log2):.2e}")
    print(f"    exp(-theta_log2) = {math.exp(-theta_log2):.10f}")

    # I_log2(0) を計算
    # Lambda_log2'(t*) = 0 を解く
    t = 0.5
    for _ in range(100):
        lpt = Lambda_log2_prime(t)
        # 2次微分を数値で
        eps = 1e-8
        lppt = (Lambda_log2_prime(t+eps) - Lambda_log2_prime(t-eps)) / (2*eps)
        if abs(lppt) < 1e-15:
            break
        t_new = t - lpt / lppt
        if abs(t_new - t) < 1e-12:
            t = t_new
            break
        t = t_new

    t_star_log2 = t
    I_0_log2 = -Lambda_log2(t_star_log2)
    print(f"\n  I_log2(0) の計算:")
    print(f"    t* = {t_star_log2:.15f}")
    print(f"    Lambda_log2(t*) = {Lambda_log2(t_star_log2):.15f}")
    print(f"    I_log2(0) = {I_0_log2:.15f}")
    print(f"    既知値 0.05498 との比較: 差 = {abs(I_0_log2 - 0.05498):.6f}")

    return {
        't_star_ln': t_star_exact,
        'I_0_ln': I_0,
        'theta_star_ln': theta_star,
        'theta_star_log2': theta_log2,
        'I_0_log2': I_0_log2,
        't_star_log2': t_star_log2,
    }


# ============================================================
# パート2: 実測tail vs 理論
# ============================================================

def tail_comparison(N_max):
    """実測のTST尾部を理論指数と比較"""
    print("\n" + "=" * 70)
    print(f"パート2: 尾部指数の精密比較 (N_max={N_max})")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    def first_drop_time(n):
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

    def total_stopping_time(n):
        steps = 0
        current = n
        while current != 1:
            current, _ = syracuse(current)
            steps += 1
            if steps > 500000:
                return -1
        return steps

    # First drop time の分布
    print("\n--- First Drop Time (初めて n 未満になるまで) ---")
    fdt_values = []
    for n in range(3, N_max + 1, 2):
        fdt = first_drop_time(n)
        if fdt >= 0:
            fdt_values.append(fdt)

    total = len(fdt_values)
    fdt_counter = Counter(fdt_values)

    print(f"  サンプル数: {total}")
    print(f"  E[FDT] = {sum(fdt_values)/total:.4f}")
    print(f"  max FDT = {max(fdt_values)}")

    # 尾部 P(FDT > t)
    print(f"\n  {'t':>5s}  {'P(FDT>t)':>12s}  {'ln P':>10s}  {'-ln P/t':>10s}")
    tail_data = []
    for t in range(1, min(max(fdt_values), 120)):
        count = sum(1 for s in fdt_values if s > t)
        if count > 0:
            p = count / total
            lnp = math.log(p)
            rate = -lnp / t
            if t % 5 == 0 or t <= 10:
                print(f"  {t:5d}  {p:12.8f}  {lnp:10.6f}  {rate:10.6f}")
            tail_data.append((t, p, rate))

    # 線形回帰 (t >= 5)
    fit_data = [(t, math.log(p)) for t, p, _ in tail_data if t >= 5 and p > 1e-6]
    if len(fit_data) >= 5:
        n_f = len(fit_data)
        sx = sum(d[0] for d in fit_data)
        sy = sum(d[1] for d in fit_data)
        sxx = sum(d[0]**2 for d in fit_data)
        sxy = sum(d[0]*d[1] for d in fit_data)
        denom = n_f * sxx - sx**2
        slope = (n_f * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n_f
        lambda_fdt = -slope

        print(f"\n  尾部指数 (first drop time):")
        print(f"    lambda = {lambda_fdt:.8f}")
        print(f"    exp(-lambda) = {math.exp(-lambda_fdt):.8f}")
        print(f"    切片 = {intercept:.6f} → C = {math.exp(intercept):.6f}")

    # Total stopping time の分布
    print("\n\n--- Total Stopping Time (1到達まで) ---")
    tst_values = []
    for n in range(3, N_max + 1, 2):
        tst = total_stopping_time(n)
        if tst >= 0:
            tst_values.append(tst)

    total_tst = len(tst_values)
    print(f"  サンプル数: {total_tst}")
    print(f"  E[TST] = {sum(tst_values)/total_tst:.4f}")
    print(f"  max TST = {max(tst_values)}")

    # 正規化した尾部: P(TST/log2(n) > c) for fixed c
    avg_log2n = sum(math.log2(2*k+3) for k in range(total_tst)) / total_tst
    mu = abs(math.log2(3) - 2)

    print(f"\n  正規化 TST/log2(n):")
    print(f"  {'c':>6s}  {'P(TST/log2n > c)':>18s}")
    for c in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]:
        count = 0
        total_c = 0
        for k in range(total_tst):
            n = 2*k + 3
            log2n = math.log2(n)
            if tst_values[k] / log2n > c:
                count += 1
            total_c += 1
        p = count / total_c
        print(f"  {c:6.1f}  {p:18.8f}")

    return {
        'lambda_fdt': lambda_fdt if len(fit_data) >= 5 else None,
    }


# ============================================================
# パート3: KS検定のkスケーリング
# ============================================================

def ks_scaling(k_values=[5, 10, 20, 50, 100, 200, 500]):
    """
    KS統計量の k 依存性を調べる。
    Berry-Esseen: KS ~ C/sqrt(k)
    実測がどの程度のkで正規近似が「良く」なるかを定量化。
    """
    print("\n" + "=" * 70)
    print("パート3: KS統計量のkスケーリング")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    mu = math.log2(3) - 2
    sigma2 = 2.0

    sample_size = 20000
    results = {}

    print(f"\n  {'k':>5s}  {'KS(obs.param)':>14s}  {'KS*sqrt(k)':>12s}  {'歪度':>10s}  {'尖度':>10s}")

    for k in k_values:
        # 十分大きな開始値
        min_bits = int(k * 3) + 20
        min_start = 2**min_bits
        max_start = min_start * 4

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

        z_values = sorted([(x - obs_mean) / obs_std for x in S_k_values])
        ks = 0.0
        for i, z in enumerate(z_values):
            F_n = (i + 1) / len(z_values)
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks = max(ks, abs(F_n - Phi))

        skew = sum((x - obs_mean)**3 for x in S_k_values) / (len(S_k_values) * obs_std**3)
        kurt = sum((x - obs_mean)**4 for x in S_k_values) / (len(S_k_values) * obs_std**4) - 3

        ks_scaled = ks * math.sqrt(k)
        print(f"  {k:5d}  {ks:14.8f}  {ks_scaled:12.6f}  {skew:10.6f}  {kurt:10.6f}")

        results[k] = {'ks': ks, 'ks_scaled': ks_scaled, 'skew': skew, 'kurt': kurt}

    # 理論: Berry-Esseen より KS ~ C/sqrt(k) → KS*sqrt(k) = const
    ks_scaled_vals = [results[k]['ks_scaled'] for k in k_values]
    print(f"\n  KS*sqrt(k) の範囲: {min(ks_scaled_vals):.6f} ~ {max(ks_scaled_vals):.6f}")
    print(f"  → 定数に収束するか? 比率(max/min) = {max(ks_scaled_vals)/min(ks_scaled_vals):.4f}")

    # log-log 回帰で実際のスケーリング指数を推定
    log_k = [math.log(k) for k in k_values]
    log_ks = [math.log(results[k]['ks']) for k in k_values]
    n_fit = len(k_values)
    sx = sum(log_k)
    sy = sum(log_ks)
    sxx = sum(x**2 for x in log_k)
    sxy = sum(x*y for x, y in zip(log_k, log_ks))
    denom = n_fit * sxx - sx**2
    slope = (n_fit * sxy - sx * sy) / denom

    print(f"  log-log 回帰: KS ~ k^{slope:.4f}")
    print(f"  Berry-Esseen予測: KS ~ k^{-0.5}")

    return results


# ============================================================
# パート4: 補正RWモデル（2ステップ相関含む）
# ============================================================

def corrected_rw_model(N_max):
    """
    v2の1ステップ自己相関を取り込んだ補正RWモデルでTSTを予測。
    """
    print("\n" + "=" * 70)
    print(f"パート4: 補正RWモデル (N_max={N_max})")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    # 遷移行列の推定: P(v2_{k+1}=j | v2_k=i)
    # まず十分な軌道データを収集
    random.seed(42)
    starts = [random.randrange(3, 10**7, 2) for _ in range(2000)]

    transitions = defaultdict(lambda: defaultdict(int))
    marginal = defaultdict(int)

    for n in starts:
        current = n
        prev_v = None
        for _ in range(200):
            if current == 1:
                break
            current, v = syracuse(current)
            if prev_v is not None:
                transitions[prev_v][v] += 1
                marginal[prev_v] += 1
            prev_v = v

    # 遷移確率
    trans_prob = {}
    for i in range(1, 10):
        if marginal[i] > 0:
            trans_prob[i] = {}
            for j in range(1, 20):
                if transitions[i][j] > 0:
                    trans_prob[i][j] = transitions[i][j] / marginal[i]

    # 定常分布の計算
    # π_i = P(v2=i) in stationary
    pi = defaultdict(float)
    # 初期: 幾何分布
    for i in range(1, 20):
        pi[i] = 1.0 / (2**i)

    # べき乗法で定常分布を求める
    for _ in range(100):
        pi_new = defaultdict(float)
        for i in range(1, 20):
            for j in range(1, 20):
                if i in trans_prob and j in trans_prob[i]:
                    pi_new[j] += pi[i] * trans_prob[i][j]
        # 正規化
        total = sum(pi_new.values())
        if total > 0:
            for j in pi_new:
                pi_new[j] /= total
        pi = pi_new

    print(f"  定常分布 (Markov):")
    for i in range(1, 10):
        geom = 1.0 / (2**i)
        print(f"    v2={i}: pi={pi.get(i,0):.6f}, Geom={geom:.6f}, "
              f"比率={pi.get(i,0)/geom:.4f}" if geom > 0 else "")

    # 補正ドリフト
    mu_corrected = sum((math.log2(3) - v) * pi.get(v, 0) for v in range(1, 20))
    mu_iid = math.log2(3) - 2

    print(f"\n  ドリフト:")
    print(f"    i.i.d.モデル: {mu_iid:.8f}")
    print(f"    Markov補正:   {mu_corrected:.8f}")
    print(f"    差:           {abs(mu_corrected - mu_iid):.8f}")

    # 補正分散 (Markovモデルの漸近分散)
    # sigma^2_eff = Var_pi[X] + 2*sum_{k=1}^inf Cov(X_0, X_k)
    var_pi = sum((math.log2(3) - v)**2 * pi.get(v, 0) for v in range(1, 20)) - mu_corrected**2

    # 1ステップ共分散を推定
    cov1 = 0
    for i in range(1, 15):
        for j in range(1, 15):
            if i in trans_prob and j in trans_prob[i]:
                cov1 += pi.get(i, 0) * trans_prob[i][j] * (math.log2(3)-i-mu_corrected) * (math.log2(3)-j-mu_corrected)

    sigma2_eff = var_pi + 2 * cov1  # 1次近似

    print(f"\n  有効分散:")
    print(f"    Var_pi[X] = {var_pi:.8f}")
    print(f"    Cov(X_0,X_1) = {cov1:.8f}")
    print(f"    sigma^2_eff ≈ {sigma2_eff:.8f}")
    print(f"    i.i.d.分散 = 2.0")
    print(f"    比率 sigma^2_eff/2 = {sigma2_eff/2:.6f}")

    # 補正TSTの予測
    # E[TST(n)] ≈ log2(n) / |mu_corrected|
    # Var[TST(n)] ≈ sigma^2_eff * log2(n) / |mu_corrected|^3

    print(f"\n  TST予測の比較 (log2(n)=17):")
    log2n = 17
    tst_iid = log2n / abs(mu_iid)
    tst_markov = log2n / abs(mu_corrected)
    print(f"    E[TST] i.i.d.:  {tst_iid:.2f}")
    print(f"    E[TST] Markov:  {tst_markov:.2f}")

    # 実測と比較
    print(f"\n  実測比較 (N_max={N_max}):")
    tst_by_bits = defaultdict(list)
    for n in range(3, N_max + 1, 2):
        current = n
        steps = 0
        while current != 1 and steps < 500000:
            current, _ = syracuse(current)
            steps += 1
        if current == 1:
            bits = int(math.log2(n)) + 1
            tst_by_bits[bits].append(steps)

    print(f"    {'bits':>5s}  {'E[TST]実測':>12s}  {'E[TST]iid':>12s}  {'E[TST]markov':>12s}  {'N':>8s}")
    for bits in sorted(tst_by_bits.keys()):
        if len(tst_by_bits[bits]) >= 50:
            mean_tst = sum(tst_by_bits[bits]) / len(tst_by_bits[bits])
            pred_iid = bits / abs(mu_iid)
            pred_markov = bits / abs(mu_corrected)
            print(f"    {bits:5d}  {mean_tst:12.2f}  {pred_iid:12.2f}  {pred_markov:12.2f}  {len(tst_by_bits[bits]):8d}")

    return {
        'mu_corrected': mu_corrected, 'mu_iid': mu_iid,
        'sigma2_eff': sigma2_eff,
    }


# ============================================================
# メイン
# ============================================================

if __name__ == '__main__':
    t_start = time.time()

    # パート1: MGFとCramer
    cramer = compute_mgf_and_cramer()

    # パート2: 尾部指数
    tail = tail_comparison(10**6)

    # パート3: KSスケーリング
    ks_scaling_results = ks_scaling([5, 10, 20, 50, 100, 200, 500])

    # パート4: 補正RWモデル
    corrected = corrected_rw_model(200000)

    elapsed = time.time() - t_start
    print(f"\n\n{'=' * 70}")
    print(f"総実行時間: {elapsed:.1f}秒")
    print("=" * 70)

    # 最終サマリー
    print("\n===== 最終サマリー =====")
    print(f"1. Cramer関数 I_log2(0) = {cramer['I_0_log2']:.10f}")
    print(f"   尾部指数 theta_log2 = {cramer['theta_star_log2']:.10f}")
    if tail.get('lambda_fdt'):
        print(f"   FDT尾部指数(実測) = {tail['lambda_fdt']:.8f}")
    print(f"2. KSスケーリング: KS ~ k^alpha")
    print(f"3. Markov補正: mu = {corrected['mu_corrected']:.8f} (vs iid: {corrected['mu_iid']:.8f})")
    print(f"   sigma^2_eff = {corrected['sigma2_eff']:.8f} (vs iid: 2.0)")
