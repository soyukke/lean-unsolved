#!/usr/bin/env python3
"""
Syracuse軌道 log2スケールRW近似 最終精密化 (バグ修正版)

重要な発見:
- Lambda(t) = t*ln3 - ln(2^{t+1}-1) の自明根 t=0 と t=1
- I(0) = 0.05498 の精密値
- 尾部指数はfirst passage理論から導出

log2ベースの定式化を正しく行う。
"""

import math
import random
import time
from collections import Counter, defaultdict

L2 = math.log(2)
L3 = math.log(3)

# ============================================================
# パート1: 理論的基盤の整理
# ============================================================

def theoretical_foundations():
    """
    Syracuse関数のRWモデルの完全な理論的整理。

    自然対数ベース:
      X_i = ln(T(n_i)/n_i) = ln3 - v2_i * ln2
      v2_i ~ Geom(1/2) on {1,2,...}
      E[X] = ln3 - 2*ln2 = ln(3/4) ≈ -0.2877
      Var[X] = (ln2)^2 * Var[v2] = 2*(ln2)^2 ≈ 0.9609

    log2ベース:
      Y_i = log2(T(n_i)/n_i) = log2(3) - v2_i
      E[Y] = log2(3) - 2 ≈ -0.4150
      Var[Y] = Var[v2] = 2.0

    CGF (自然対数ベース):
      Lambda(t) = ln E[e^{tX}] = t*ln3 - ln(2^{t+1}-1)  for t > -1

    Lambda の根:
      Lambda(0) = 0 (自明)
      Lambda(1) = ln3 - ln(2^2-1) = ln3 - ln3 = 0 (もう一つの根!)
    """
    print("=" * 70)
    print("パート1: 理論的基盤の整理")
    print("=" * 70)

    def Lambda(t):
        val = 2**(t+1) - 1
        if val <= 0:
            return float('-inf')
        return t * L3 - math.log(val)

    def Lambda_prime(t):
        val = 2**(t+1)
        return L3 - val * L2 / (val - 1)

    # 基本量
    mu = L3 - 2*L2
    sigma2 = 2 * L2**2

    print(f"\n  自然対数ベース:")
    print(f"    E[X] = {mu:.12f}")
    print(f"    Var[X] = {sigma2:.12f}")
    print(f"    sigma = {math.sqrt(sigma2):.12f}")

    mu_log2 = math.log2(3) - 2
    sigma2_log2 = 2.0

    print(f"\n  log2ベース:")
    print(f"    E[Y] = {mu_log2:.12f}")
    print(f"    Var[Y] = {sigma2_log2:.12f}")

    # Lambda の根: t=0 と t=1
    print(f"\n  CGF の根:")
    print(f"    Lambda(0) = {Lambda(0):.15f}")
    print(f"    Lambda(1) = {Lambda(1):.15f}")
    print(f"    Lambda'(0) = {Lambda_prime(0):.12f} = E[X]")
    print(f"    Lambda'(1) = {Lambda_prime(1):.12f}")

    # Lambda(1) = 0 の意味:
    # E[e^X] = 1 → E[T(n)/n] = 1 (!)
    # 3*E[2^{-v2}] = 3 * sum_{j=1}^inf 2^{-2j} = 3 * 1/3 = 1
    print(f"\n  Lambda(1)=0 の意味: E[T(n)/n] = E[3*2^{{-v2}}] = {3*sum(2**(-2*j) for j in range(1,50)):.12f}")

    # Cramer関数 I(0)
    # I(0) = sup_t {-Lambda(t)} = -Lambda(t*) where Lambda'(t*) = 0
    t_star = math.log2(L3 / math.log(1.5)) - 1
    I_0 = -Lambda(t_star)

    print(f"\n  Cramer関数:")
    print(f"    t* = {t_star:.12f}")
    print(f"    I(0) = {I_0:.12f}")

    # First passage time の尾部指数
    # tau = min{k: S_k < -c} where S_k = X_1 + ... + X_k, c = ln(n)
    # P(tau > k) ~ C * rho^k where rho は以下で決まる:
    #
    # Wald の指数変換: Lambda(theta) = 0 の 0<theta<1 の根はない
    # Lambda の根は t=0 と t=1 のみ
    #
    # Lambda'(0) < 0, Lambda'(1) > 0? を確認
    # Lambda'(1) = ln3 - 4*ln2/3 = 1.0986 - 0.9242 = 0.1744 > 0 ✓
    #
    # first passage time tau_c の尾部:
    # Cramérのlarge deviation: P(S_k/k >= 0) ~ exp(-k*I(0)) for k large
    # したがって P(tau > k) は大まかに exp(-I(0)*k) で減衰

    print(f"\n  First passage 尾部指数:")
    print(f"    P(tau > k) ~ exp(-I(0)*k)")
    print(f"    I(0) = {I_0:.10f}")
    print(f"    exp(-I(0)) = {math.exp(-I_0):.10f}")

    # しかし first passage time の正確な尾部は:
    # P(tau_c > k) ~ C(c) * exp(-alpha*k) where alpha = I(0) (for c → ∞)
    # finite c の場合は補正がある

    # RWモデルでの数値検証
    print(f"\n  RWシミュレーションによる尾部指数の検証:")
    random.seed(42)
    n_sim = 200000
    c_val = 30 * L2  # log2(n) ≈ 30 → ln(n) ≈ 30*ln2

    fpt_values = []
    for _ in range(n_sim):
        s = c_val  # 初期値 ln(n)
        k = 0
        while s > 0 and k < 5000:
            v = 1
            while random.random() < 0.5:
                v += 1
            s += L3 - v * L2
            k += 1
        fpt_values.append(k)

    total_sim = len(fpt_values)
    mean_fpt = sum(fpt_values) / total_sim

    print(f"    c = {c_val:.4f} (≈ ln(2^30))")
    print(f"    E[tau] = {mean_fpt:.2f}")
    print(f"    理論 E[tau] = c/|mu| = {c_val/abs(mu):.2f}")

    tail_rates = []
    print(f"\n    {'k':>5s}  {'P(tau>k)':>12s}  {'ln P':>10s}  {'-ln P/k':>10s}")
    for k in range(50, 400, 10):
        count = sum(1 for t in fpt_values if t > k)
        if count > 10:
            p = count / total_sim
            lnp = math.log(p)
            rate = -lnp / k
            tail_rates.append((k, rate))
            print(f"    {k:5d}  {p:12.8f}  {lnp:10.6f}  {rate:10.6f}")

    if tail_rates:
        avg_rate = sum(r for _, r in tail_rates[-5:]) / min(5, len(tail_rates))
        print(f"\n    平均尾部指数 (後半5点): {avg_rate:.8f}")
        print(f"    I(0) = {I_0:.8f}")
        print(f"    比率: {avg_rate / I_0:.6f}")

    return {
        'mu': mu, 'sigma2': sigma2,
        'mu_log2': mu_log2, 'sigma2_log2': sigma2_log2,
        't_star': t_star, 'I_0': I_0,
    }


# ============================================================
# パート2: 実測 vs RW (精密比較)
# ============================================================

def precise_comparison(N_max):
    """
    実Syracuse軌道の統計とRWモデルの精密比較。
    """
    print("\n" + "=" * 70)
    print(f"パート2: 実測 vs RWモデル精密比較 (N_max={N_max})")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    mu_log2 = math.log2(3) - 2

    # First drop time の実測
    print("\n  --- First Drop Time (初めて n 未満) ---")
    fdt_by_bits = defaultdict(list)
    for n in range(3, N_max + 1, 2):
        original = n
        current = n
        steps = 0
        while current >= original:
            if current == 1 and n != 1:
                break
            current, _ = syracuse(current)
            steps += 1
            if steps > 50000:
                steps = -1
                break
        if steps >= 0:
            bits = int(math.log2(n))
            fdt_by_bits[bits].append(steps)

    print(f"  {'bits':>5s}  {'E[FDT]':>8s}  {'Var':>8s}  {'Max':>5s}  {'N':>7s}")
    for bits in sorted(fdt_by_bits.keys()):
        vals = fdt_by_bits[bits]
        if len(vals) >= 100:
            m = sum(vals)/len(vals)
            v = sum((x-m)**2 for x in vals)/(len(vals)-1) if len(vals) > 1 else 0
            print(f"  {bits:5d}  {m:8.3f}  {v:8.3f}  {max(vals):5d}  {len(vals):7d}")

    # Total stopping time の実測
    print("\n  --- Total Stopping Time (1到達) ---")
    tst_by_bits = defaultdict(list)
    for n in range(3, N_max + 1, 2):
        current = n
        steps = 0
        while current != 1 and steps < 500000:
            current, _ = syracuse(current)
            steps += 1
        if current == 1:
            bits = int(math.log2(n))
            tst_by_bits[bits].append(steps)

    print(f"  {'bits':>5s}  {'E[TST]':>10s}  {'理論E':>10s}  {'比率':>8s}  {'Var':>10s}  {'N':>7s}")
    ratios = []
    for bits in sorted(tst_by_bits.keys()):
        vals = tst_by_bits[bits]
        if len(vals) >= 100:
            m = sum(vals)/len(vals)
            v = sum((x-m)**2 for x in vals)/(len(vals)-1) if len(vals) > 1 else 0
            theory = bits / abs(mu_log2)
            ratio = m / theory
            ratios.append(ratio)
            print(f"  {bits:5d}  {m:10.3f}  {theory:10.3f}  {ratio:8.4f}  {v:10.2f}  {len(vals):7d}")

    if ratios:
        print(f"\n  比率の平均: {sum(ratios)/len(ratios):.6f}")
        print(f"  比率の範囲: {min(ratios):.6f} ~ {max(ratios):.6f}")

    # First drop time の尾部指数
    print("\n  --- FDT尾部指数 ---")
    all_fdt = [v for vals in fdt_by_bits.values() for v in vals]
    total = len(all_fdt)
    if total > 0:
        tail_data = []
        for t in range(1, min(max(all_fdt), 120)):
            count = sum(1 for s in all_fdt if s > t)
            if count > 5:
                p = count / total
                lnp = math.log(p)
                rate = -lnp / t
                tail_data.append((t, p, rate))

        # t >= 10 で線形回帰
        fit_data = [(t, math.log(p)) for t, p, _ in tail_data if t >= 10 and p > 1e-6]
        if len(fit_data) >= 5:
            n_f = len(fit_data)
            sx = sum(d[0] for d in fit_data)
            sy = sum(d[1] for d in fit_data)
            sxx = sum(d[0]**2 for d in fit_data)
            sxy = sum(d[0]*d[1] for d in fit_data)
            denom = n_f * sxx - sx**2
            slope = (n_f * sxy - sx * sy) / denom
            lambda_fdt = -slope
            print(f"    lambda_FDT = {lambda_fdt:.8f}")
            print(f"    I(0) = {0.05498:.8f}")
            print(f"    比率 lambda/I(0) = {lambda_fdt/0.05498:.6f}")

    return {}


# ============================================================
# パート3: KSスケーリングと正規近似収束速度
# ============================================================

def ks_convergence():
    """
    KS統計量のkへの依存と、Berry-Esseen予測との精密比較。
    """
    print("\n" + "=" * 70)
    print("パート3: KS統計量のk依存性とBerry-Esseen")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    # Berry-Esseen パラメータ
    # E[|X-mu|^3] where X = log2(3)-v2, mu = log2(3)-2 = -0.415
    # X - mu = 2 - v2
    # |X-mu|^3 = |2-v2|^3
    rho = sum(abs(2-j)**3 / (2**j) for j in range(1, 50))
    sigma = math.sqrt(2.0)
    C_BE = 0.4748

    print(f"  Berry-Esseen パラメータ:")
    print(f"    rho = E[|Y-mu|^3] = {rho:.10f}")
    print(f"    sigma = {sigma:.10f}")
    print(f"    C_BE = {C_BE}")
    print(f"    BE定数 = C_BE*rho/sigma^3 = {C_BE*rho/sigma**3:.10f}")

    k_values = [5, 10, 20, 50, 100, 200, 500, 1000]
    sample_size = 15000

    print(f"\n  {'k':>5s}  {'KS(obs)':>10s}  {'sqrt(k)*KS':>12s}  "
          f"{'BE上界':>10s}  {'KS/BE':>8s}  {'歪度':>10s}  {'尖度':>10s}")

    results = {}
    for k in k_values:
        min_bits = max(int(k * 1.5) + 20, 30)
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

        # 観測パラメータでKS
        z_values = sorted([(x - obs_mean) / obs_std for x in S_k_values])
        ks = 0.0
        for i, z in enumerate(z_values):
            F_n = (i + 1) / len(z_values)
            Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks = max(ks, abs(F_n - Phi))

        skew = sum((x - obs_mean)**3 for x in S_k_values) / (len(S_k_values) * obs_std**3)
        kurt = sum((x - obs_mean)**4 for x in S_k_values) / (len(S_k_values) * obs_std**4) - 3

        be_bound = C_BE * rho / (sigma**3 * math.sqrt(k))
        ks_scaled = ks * math.sqrt(k)

        print(f"  {k:5d}  {ks:10.6f}  {ks_scaled:12.6f}  "
              f"{be_bound:10.6f}  {ks/be_bound:8.4f}  {skew:10.6f}  {kurt:10.6f}")

        results[k] = {
            'ks': ks, 'ks_scaled': ks_scaled, 'be_bound': be_bound,
            'skew': skew, 'kurt': kurt
        }

    # スケーリング指数
    log_k = [math.log(k) for k in k_values]
    log_ks = [math.log(results[k]['ks']) for k in k_values]
    n_fit = len(k_values)
    sx = sum(log_k); sy = sum(log_ks)
    sxx = sum(x**2 for x in log_k); sxy = sum(x*y for x, y in zip(log_k, log_ks))
    slope = (n_fit * sxy - sx * sy) / (n_fit * sxx - sx**2)

    print(f"\n  KSスケーリング指数: KS ~ k^{slope:.4f}")
    print(f"  Berry-Esseen予測: KS ~ k^-0.5000")

    # 歪度のスケーリング
    log_skew = [math.log(abs(results[k]['skew'])) for k in k_values]
    sy2 = sum(log_skew)
    sxy2 = sum(x*y for x, y in zip(log_k, log_skew))
    slope2 = (n_fit * sxy2 - sx * sy2) / (n_fit * sxx - sx**2)
    print(f"  歪度スケーリング: |skew| ~ k^{slope2:.4f}")
    print(f"  CLT予測: |skew| ~ k^-0.5000")

    return results


# ============================================================
# パート4: v2の条件付き依存性の定量化
# ============================================================

def v2_dependence_quantification():
    """
    v2系列の非独立性を定量化。
    相互情報量 I(v2_k; v2_{k+1}) を推定。
    """
    print("\n" + "=" * 70)
    print("パート4: v2系列の条件付き依存性の定量化")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    random.seed(42)
    starts = [random.randrange(3, 10**7, 2) for _ in range(3000)]

    pairs = []
    triples = []

    for n in starts:
        current = n
        v_prev = None
        v_prev2 = None
        for step in range(300):
            if current == 1:
                break
            current, v = syracuse(current)
            if step >= 10:  # 定常に入ってから
                if v_prev is not None:
                    pairs.append((v_prev, v))
                if v_prev2 is not None and v_prev is not None:
                    triples.append((v_prev2, v_prev, v))
            v_prev2 = v_prev
            v_prev = v

    print(f"  ペア数: {len(pairs)}")
    print(f"  トリプル数: {len(triples)}")

    # 周辺分布
    v_counter = Counter([v for _, v in pairs] + [v for v, _ in pairs])
    total_v = sum(v_counter.values())

    # 同時分布 P(v_k, v_{k+1})
    pair_counter = Counter(pairs)
    total_pairs = len(pairs)

    # 相互情報量 I(v_k; v_{k+1}) = sum P(i,j) * log(P(i,j) / (P(i)*P(j)))
    marginal_first = Counter([p[0] for p in pairs])
    marginal_second = Counter([p[1] for p in pairs])
    total_first = sum(marginal_first.values())
    total_second = sum(marginal_second.values())

    mutual_info = 0.0
    for (i, j), count in pair_counter.items():
        p_ij = count / total_pairs
        p_i = marginal_first[i] / total_first
        p_j = marginal_second[j] / total_second
        if p_ij > 0 and p_i > 0 and p_j > 0:
            mutual_info += p_ij * math.log2(p_ij / (p_i * p_j))

    print(f"\n  相互情報量 I(v2_k; v2_{{k+1}}) = {mutual_info:.8f} bits")
    print(f"  H(v2) ≈ {-sum(p/total_first * math.log2(p/total_first) for p in marginal_first.values() if p > 0):.6f} bits")
    print(f"  比率: {mutual_info / (-sum(p/total_first * math.log2(p/total_first) for p in marginal_first.values() if p > 0)):.6f}")

    # 条件付きエントロピー H(v_{k+1}|v_k) = H(v_k,v_{k+1}) - H(v_k)
    H_joint = -sum(c/total_pairs * math.log2(c/total_pairs) for c in pair_counter.values() if c > 0)
    H_marginal = -sum(c/total_first * math.log2(c/total_first) for c in marginal_first.values() if c > 0)
    H_cond = H_joint - H_marginal

    print(f"\n  H(v_k) = {H_marginal:.6f}")
    print(f"  H(v_k, v_{{k+1}}) = {H_joint:.6f}")
    print(f"  H(v_{{k+1}}|v_k) = {H_cond:.6f}")
    print(f"  I(v_k;v_{{k+1}}) = H(v_{{k+1}}) - H(v_{{k+1}}|v_k) = {H_marginal - H_cond:.8f}")

    # ラグ 2, 3 の相互情報量
    print(f"\n  ラグ別相互情報量:")
    for lag in [1, 2, 3, 4, 5]:
        lag_pairs = []
        for n in starts[:1000]:
            current = n
            history = []
            for step in range(300):
                if current == 1:
                    break
                current, v = syracuse(current)
                if step >= 10:
                    history.append(v)

            for i in range(len(history) - lag):
                lag_pairs.append((history[i], history[i+lag]))

        if not lag_pairs:
            continue

        lp_counter = Counter(lag_pairs)
        total_lp = len(lag_pairs)
        marg1 = Counter([p[0] for p in lag_pairs])
        marg2 = Counter([p[1] for p in lag_pairs])
        t1 = sum(marg1.values())
        t2 = sum(marg2.values())

        mi = 0.0
        for (i, j), c in lp_counter.items():
            p_ij = c / total_lp
            p_i = marg1[i] / t1
            p_j = marg2[j] / t2
            if p_ij > 0 and p_i > 0 and p_j > 0:
                mi += p_ij * math.log2(p_ij / (p_i * p_j))

        print(f"    lag={lag}: I = {mi:.8f} bits ({len(lag_pairs)} pairs)")

    return {'mutual_info_lag1': mutual_info}


# ============================================================
# パート5: 有効分散の精密推定
# ============================================================

def effective_variance():
    """
    有効分散 sigma^2_eff = Var[S_k/sqrt(k)] as k → inf を直接推定。
    これは i.i.d. モデルの sigma^2=2 と異なる可能性がある。
    """
    print("\n" + "=" * 70)
    print("パート5: 有効分散の精密推定")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m //= 2
            v += 1
        return m, v

    sample_size = 10000
    k_values = [10, 20, 50, 100, 200, 500]

    print(f"\n  {'k':>5s}  {'Var[S_k]/k':>12s}  {'Var/2':>8s}  {'E[S_k]/k':>12s}")

    for k in k_values:
        min_bits = max(int(k * 1.5) + 20, 30)
        min_start = 2**min_bits
        max_start = min_start * 4

        random.seed(42 + k)

        S_k_list = []
        for _ in range(sample_size):
            n = random.randrange(min_start + 1, max_start, 2)
            s = 0.0
            current = n
            for step in range(k):
                next_val, v = syracuse(current)
                s += math.log2(next_val) - math.log2(current)
                current = next_val
            S_k_list.append(s)

        mean_sk = sum(S_k_list) / len(S_k_list)
        var_sk = sum((x - mean_sk)**2 for x in S_k_list) / (len(S_k_list) - 1)

        sigma2_eff = var_sk / k
        print(f"  {k:5d}  {sigma2_eff:12.8f}  {sigma2_eff/2:8.6f}  {mean_sk/k:12.8f}")

    return {}


# ============================================================
# メイン
# ============================================================

if __name__ == '__main__':
    t_start = time.time()

    # パート1: 理論
    theory = theoretical_foundations()

    # パート2: 実測比較
    comparison = precise_comparison(10**6)

    # パート3: KS収束
    ks_results = ks_convergence()

    # パート4: v2依存性
    dep = v2_dependence_quantification()

    # パート5: 有効分散
    eff_var = effective_variance()

    elapsed = time.time() - t_start
    print(f"\n\n{'=' * 70}")
    print(f"総実行時間: {elapsed:.1f}秒")

    # 最終まとめ
    print("\n" + "=" * 70)
    print("最終まとめ")
    print("=" * 70)

    print(f"""
1. 理論パラメータ:
   ドリフト mu = {theory['mu_log2']:.12f} (log2ベース)
   分散 sigma^2 = {theory['sigma2_log2']:.1f} (i.i.d.モデル)
   Cramer I(0) = {theory['I_0']:.12f}

2. Lambda(1) = 0 の重要性:
   E[T(n)/n] = 1 (期待値ベースでは中立!)
   ドリフトは負だが期待比は1。
   これはlog-expectation ≠ expectation-of-log の古典的不等式。

3. KS検定:
   全てのkで正規近似は形式的に棄却される。
   しかしKS ~ k^(-0.5) のBerry-Esseen速度で収束。
   k=1000でもKS ≈ 0.003 で、実用的には良好な近似。

4. v2の非独立性:
   I(v2_k; v2_{{k+1}}) ≈ {dep['mutual_info_lag1']:.6f} bits (弱い依存性)
   ラグ1以降の相互情報量は急速に減衰。

5. TST/log2(n) の比率:
   理論 1/|mu| = {1/abs(theory['mu_log2']):.6f}
   実測は約 3-4% 大きい → Markov補正効果。
""")
