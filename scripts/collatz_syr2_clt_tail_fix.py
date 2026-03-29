#!/usr/bin/env python3
"""
尾部分布の問題修正と追加分析

前回の問題:
  - 右裾が0になっていた → log2(T/n) = log2(3) - v2 であり、v2 >= 1 なので
    log2(T/n) <= log2(3) - 1 ≈ 0.585
    これが mu + sigma ≈ -0.415 + 1.414 ≈ 0.999 より小さい
    つまり右裾の閾値を超えるサンプルが存在しない（分布の上限が制約的）

  この分布は正規分布と根本的に異なる:
  - 上限: log2(3) - 1 ≈ 0.585 （v2=1の場合）
  - 離散的な値: log2(3) - k (k=1,2,3,...) + 微小補正
  - 左に重い裾（v2が大きいケース）
  - 非対称で右に打ち切られた分布

追加分析:
  1. 正しいkステップでの分布形状
  2. v2の分布に基づく理論的な増分分布の導出
  3. kが増えた時のCLT収束の構造的理由
"""

import math
import random
import time
import json
from collections import Counter

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
    return {"mean": mu, "var": var, "std": sigma, "skewness": skew, "kurtosis": kurt}

# ============================================================
# Part 1: 正確な1ステップ分布の構造
# ============================================================

def exact_1step_structure(N_samples=1000000):
    """
    log2(T(n)/n) の正確な分布構造

    T(n) = (3n+1)/2^v で v = v2(3n+1)
    log2(T(n)/n) = log2(3n+1) - log2(n) - v
                 = log2(3 + 1/n) - v
                 ≈ log2(3) - v + (1/(n*ln2)) * (correction)

    大きなnでは log2(T/n) ≈ log2(3) - v2(3n+1)
    """
    print("  1ステップ分布の構造解析...")

    # v2ごとの増分の分布
    v2_increments = {}  # v2 -> list of increments
    all_increments = []

    for _ in range(N_samples):
        n = random.randint(10**9, 10**10)
        if n % 2 == 0:
            n += 1
        tn = syracuse(n)
        inc = math.log2(tn / n)
        v = v2(3 * n + 1)
        all_increments.append(inc)
        if v not in v2_increments:
            v2_increments[v] = []
        v2_increments[v].append(inc)

    results = {
        "overall_stats": compute_stats(all_increments),
        "distribution_support": {
            "upper_bound": math.log2(3) - 1,
            "description": "log2(T/n) <= log2(3) - 1 ≈ 0.585 (v2=1 case)",
        }
    }

    # v2ごとの統計
    v2_details = {}
    for v_val in sorted(v2_increments.keys()):
        incs = v2_increments[v_val]
        if len(incs) >= 10:
            theoretical_center = math.log2(3) - v_val
            actual_mean = sum(incs) / len(incs)
            actual_var = sum((x - actual_mean)**2 for x in incs) / len(incs)
            v2_details[str(v_val)] = {
                "count": len(incs),
                "fraction": len(incs) / N_samples,
                "theoretical_center": theoretical_center,
                "actual_mean": actual_mean,
                "deviation_from_center": actual_mean - theoretical_center,
                "variance_within_v2": actual_var,
            }

    results["v2_conditioned"] = v2_details

    # 分布の形状: 離散的な塊の集合
    # 各v2値での集中度
    total_var = results["overall_stats"]["var"]
    between_group_var = sum(
        (len(v2_increments.get(v, [])) / N_samples) *
        (math.log2(3) - v - results["overall_stats"]["mean"])**2
        for v in v2_increments.keys()
    )
    within_group_var = sum(
        (len(v2_increments.get(v, [])) / N_samples) *
        (sum((x - (sum(v2_increments[v]) / len(v2_increments[v])))**2
             for x in v2_increments[v]) / len(v2_increments[v])
         if len(v2_increments[v]) > 0 else 0)
        for v in v2_increments.keys()
    )
    results["variance_decomposition"] = {
        "total_variance": total_var,
        "between_v2_groups": between_group_var,
        "within_v2_groups": within_group_var,
        "between_fraction": between_group_var / total_var if total_var > 0 else 0,
    }

    return results

# ============================================================
# Part 2: kステップ和の分布がなぜCLTに収束するか
# ============================================================

def clt_mechanism_analysis(N_samples=300000):
    """
    S_k = sum of log2(T/n) の分布形状の変化

    1ステップは離散的な塊（v2の値ごと）
    kステップ和は異なるv2値の組み合わせで混合される
    → CLT収束は離散的モードの「畳み込みによる平滑化」
    """
    print("  kステップ和の分布形状変化を解析...")

    results = {}
    for k in [1, 2, 3, 5, 10, 20]:
        sums = []
        v2_sequences = []
        for _ in range(min(N_samples, 200000)):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            v2_seq = []
            for step in range(k):
                v = v2(3 * n + 1)
                tn = syracuse(n)
                s += math.log2(tn / n)
                v2_seq.append(v)
                n = tn
            sums.append(s)
            v2_sequences.append(tuple(v2_seq))

        stats = compute_stats(sums)

        # v2合計値の分布（離散的）
        v2_total = [sum(seq) for seq in v2_sequences]
        v2_total_counter = Counter(v2_total)
        v2_total_dist = {str(t): c / len(v2_total) for t, c in sorted(v2_total_counter.items())[:15]}

        # S_k = k*log2(3) - sum(v2) + corrections
        # 主要項は sum(v2) の分布で決まる
        # sum of k independent Geom(1/2) の分散 = k * 2

        # 離散モード数: sum(v2)が取りうる値の数
        n_modes = len(v2_total_counter)

        # 各モードの重み
        mode_weights = sorted(v2_total_counter.values(), reverse=True)
        top_5_weight = sum(mode_weights[:5]) / len(v2_total) if mode_weights else 0

        results[str(k)] = {
            "stats": stats,
            "n_modes_in_v2_sum": n_modes,
            "top_5_modes_weight": top_5_weight,
            "v2_sum_distribution": v2_total_dist,
            "v2_sum_mean": sum(v2_total) / len(v2_total),
            "v2_sum_var": compute_stats([float(v) for v in v2_total])["var"],
            "expected_v2_sum_mean": 2 * k,
            "expected_v2_sum_var": 2 * k,
        }

    return results

# ============================================================
# Part 3: Edgeworth展開の理論的係数
# ============================================================

def theoretical_edgeworth_coefficients():
    """
    v2 ~ Geom(1/2) starting at 1 のモーメントから理論的なEdgeworth係数を計算

    X = log2(3) - v2
    E[X] = log2(3) - 2
    Var[X] = Var[v2] = 2
    E[(X-mu)^3] = -E[(v2-2)^3] = -E[(v2-2)^3]

    Geom(1/2) starting at 1: P(v2=k) = 2^{-k}, k=1,2,...
    E[v2] = 2
    E[v2^2] = sum k^2 * 2^{-k} = 6
    Var[v2] = 6 - 4 = 2
    E[(v2-2)^3] = sum (k-2)^3 * 2^{-k}
    """
    print("  理論的Edgeworth係数の計算...")

    # 正確な計算
    max_k = 100
    moments = {}
    for p in range(1, 7):
        moments[p] = sum(k**p * 2**(-k) for k in range(1, max_k + 1))

    E_v2 = moments[1]
    E_v2_2 = moments[2]
    E_v2_3 = moments[3]
    E_v2_4 = moments[4]
    E_v2_5 = moments[5]
    E_v2_6 = moments[6]

    Var_v2 = E_v2_2 - E_v2**2

    # 中心モーメント
    mu3 = E_v2_3 - 3*E_v2*E_v2_2 + 2*E_v2**3
    mu4 = (E_v2_4 - 4*E_v2*E_v2_3 + 6*E_v2**2*E_v2_2 - 3*E_v2**4)
    mu5 = (E_v2_5 - 5*E_v2*E_v2_4 + 10*E_v2**2*E_v2_3
           - 10*E_v2**3*E_v2_2 + 4*E_v2**5)
    mu6 = (E_v2_6 - 6*E_v2*E_v2_5 + 15*E_v2**2*E_v2_4
           - 20*E_v2**3*E_v2_3 + 15*E_v2**4*E_v2_2 - 5*E_v2**6)

    sigma = math.sqrt(Var_v2)
    skewness = mu3 / sigma**3
    kurtosis = mu4 / sigma**4 - 3

    # X = log2(3) - v2 なので
    # (X - E[X]) = -(v2 - E[v2])
    # E[(X-mu)^3] = -mu3  (反転)
    # E[(X-mu)^4] = mu4
    # skewness(X) = -skewness(v2)
    # kurtosis(X) = kurtosis(v2)

    # Edgeworth展開のS_kに対する係数
    # S_k = sum of k iid copies of X
    # S_k has: skewness = skew(X)/sqrt(k), kurtosis = kurt(X)/k

    edgeworth_info = {
        "v2_moments": {
            "E[v2]": E_v2,
            "E[v2^2]": E_v2_2,
            "Var[v2]": Var_v2,
            "mu3": mu3,
            "mu4": mu4,
        },
        "X_cumulants": {
            "E[X]": math.log2(3) - E_v2,
            "Var[X]": Var_v2,
            "skewness": -skewness,  # X = log2(3) - v2
            "excess_kurtosis": kurtosis,
        },
        "edgeworth_corrections": {
            "description": "For S_k = sum of k X's, standardized Z_k = (S_k - k*mu)/(sigma*sqrt(k))",
            "term1_coefficient": -skewness,  # appears as skew(X)/(6*sqrt(k))
            "term2a_coefficient": kurtosis,   # appears as kurt(X)/(24*k)
            "term2b_coefficient": skewness**2,  # appears as skew(X)^2/(72*k)
        },
        "Berry_Esseen": {
            "rho": abs(mu3),
            "sigma": sigma,
            "BE_constant_ratio": abs(mu3) / sigma**3,
            "description": "KS(S_k) <= 0.4748 * rho / (sigma^3 * sqrt(k))",
        }
    }

    return edgeworth_info

# ============================================================
# Part 4: T^2 vs T の CLT収束速度比較
# ============================================================

def t1_vs_t2_clt_comparison(N_samples=200000):
    """
    T^2を「1回の」マップとして扱った場合のCLT収束速度を
    Tの場合と比較

    T^2を使うと、1回のマップで log2(T^2/n) ≈ 2*log2(3) - (v2_1 + v2_2)
    分布がより対称的になる可能性がある → CLT収束が速い？
    """
    print("  T vs T^2 のCLT収束速度比較...")

    # T^2の1ステップ統計
    t2_incs = []
    for _ in range(N_samples):
        n = random.randint(10**9, 10**10)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t2 = syracuse(t1)
        t2_incs.append(math.log2(t2 / n))

    t2_stats = compute_stats(t2_incs)

    # T の1ステップ統計
    t1_incs = []
    for _ in range(N_samples):
        n = random.randint(10**9, 10**10)
        if n % 2 == 0:
            n += 1
        t1 = syracuse(n)
        t1_incs.append(math.log2(t1 / n))

    t1_stats = compute_stats(t1_incs)

    # kステップでのCLT精度比較
    comparison = []
    for k in [1, 2, 3, 5, 10]:
        # T^1 の kステップ
        t1_sums = []
        for _ in range(min(N_samples, 100000)):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            t1_sums.append(s)

        # T^2 の kステップ（= T^{2k}）
        t2_sums = []
        for _ in range(min(N_samples, 100000)):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                t1 = syracuse(n)
                t2 = syracuse(t1)
                s += math.log2(t2 / n)
                n = t2
            t2_sums.append(s)

        # KS統計量
        def ks_normal(data, mu, sigma):
            sorted_d = sorted((x - mu) / sigma for x in data)
            n = len(sorted_d)
            ks = 0
            for i, z in enumerate(sorted_d):
                cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
                ks = max(ks, abs((i+1)/n - cdf), abs(i/n - cdf))
            return ks

        mu_t1_k = k * t1_stats["mean"]
        sigma_t1_k = t1_stats["std"] * math.sqrt(k)
        ks_t1 = ks_normal(t1_sums, mu_t1_k, sigma_t1_k)

        mu_t2_k = k * t2_stats["mean"]
        sigma_t2_k = t2_stats["std"] * math.sqrt(k)
        ks_t2 = ks_normal(t2_sums, mu_t2_k, sigma_t2_k)

        comparison.append({
            "k": k,
            "equivalent_T_steps": {"T1": k, "T2": 2*k},
            "ks_T1_k_steps": ks_t1,
            "ks_T2_k_steps": ks_t2,
            "ks_ratio_T1_over_T2": ks_t1 / ks_t2 if ks_t2 > 0 else None,
        })

    return {
        "T1_1step_stats": t1_stats,
        "T2_1step_stats": t2_stats,
        "skewness_ratio": t2_stats["skewness"] / t1_stats["skewness"] if t1_stats["skewness"] != 0 else None,
        "kurtosis_ratio": t2_stats["kurtosis"] / t1_stats["kurtosis"] if t1_stats["kurtosis"] != 0 else None,
        "comparison": comparison,
    }

# ============================================================
# Part 5: KS*sqrt(k) の安定化とCLT収束の精密速度
# ============================================================

def precise_convergence_rate(N_samples=150000):
    """
    KS(S_k) * sqrt(k) の挙動を精密に追跡
    Berry-Esseen: KS * sqrt(k) → C（定数）
    実際には log(k) 補正がある可能性
    """
    print("  KS*sqrt(k) の安定化を精密測定...")

    # 1ステップの基礎統計
    inc_all = []
    for _ in range(N_samples):
        n = random.randint(10**9, 10**10)
        if n % 2 == 0:
            n += 1
        inc_all.append(math.log2(syracuse(n) / n))
    stats1 = compute_stats(inc_all)

    results = []
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30]:
        sums = []
        for _ in range(min(N_samples, 120000)):
            n = random.randint(10**9, 10**10)
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
        sorted_z = sorted((s - mu_k) / sigma_k for s in sums)
        n_z = len(sorted_z)

        ks = 0
        for i, z in enumerate(sorted_z):
            cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ks = max(ks, abs((i+1)/n_z - cdf), abs(i/n_z - cdf))

        results.append({
            "k": k,
            "ks": ks,
            "ks_sqrt_k": ks * math.sqrt(k),
            "ks_k_to_2_3": ks * k**(2/3),
            "log_ks": math.log(ks) if ks > 0 else None,
            "log_k": math.log(k),
        })

    # ks = C * k^(-alpha) のフィット
    # log(ks) = log(C) - alpha * log(k)
    valid = [(r["log_k"], r["log_ks"]) for r in results if r["log_ks"] is not None and r["k"] >= 2]
    if len(valid) >= 3:
        x = [v[0] for v in valid]
        y = [v[1] for v in valid]
        n = len(x)
        sx = sum(x)
        sy = sum(y)
        sxx = sum(xi**2 for xi in x)
        sxy = sum(x[i]*y[i] for i in range(n))
        alpha = -(n * sxy - sx * sy) / (n * sxx - sx**2)
        log_C = (sy + alpha * sx) / n
        C = math.exp(log_C)
        fitted = {"alpha": alpha, "C": C, "description": f"KS ≈ {C:.4f} * k^(-{alpha:.4f})"}
    else:
        fitted = None

    return {
        "one_step_stats": {"mean": stats1["mean"], "var": stats1["var"]},
        "convergence_data": results,
        "power_law_fit": fitted,
    }

# ============================================================
# メイン
# ============================================================

def main():
    start_time = time.time()
    all_results = {}

    print("=" * 70)
    print("Syr^2 CLT 尾部・構造・収束率の深掘り分析")
    print("=" * 70)

    # Part 1
    print("\n[Part 1] 1ステップ分布の構造")
    p1 = exact_1step_structure(500000)
    all_results["1step_structure"] = p1
    s = p1["overall_stats"]
    vd = p1["variance_decomposition"]
    print(f"  全体: E={s['mean']:.6f}, Var={s['var']:.6f}, Skew={s['skewness']:.6f}, Kurt={s['kurtosis']:.6f}")
    print(f"  上限: {p1['distribution_support']['upper_bound']:.6f}")
    print(f"  分散分解: between={vd['between_v2_groups']:.6f} ({vd['between_fraction']:.4f}), within={vd['within_v2_groups']:.6f}")
    print("  v2別:")
    for v, info in sorted(p1["v2_conditioned"].items(), key=lambda x: int(x[0])):
        if int(v) <= 6:
            print(f"    v2={v}: center={info['theoretical_center']:.4f}, mean={info['actual_mean']:.6f}, "
                  f"dev={info['deviation_from_center']:.6f}, within_var={info['variance_within_v2']:.8f}")

    # Part 2
    print("\n[Part 2] kステップ和の分布形状変化")
    p2 = clt_mechanism_analysis(200000)
    all_results["clt_mechanism"] = p2
    for k_str, info in sorted(p2.items(), key=lambda x: int(x[0])):
        s = info["stats"]
        print(f"  k={k_str}: modes={info['n_modes_in_v2_sum']}, top5_weight={info['top_5_modes_weight']:.4f}, "
              f"skew={s['skewness']:.4f}, kurt={s['kurtosis']:.4f}")

    # Part 3
    print("\n[Part 3] 理論的Edgeworth係数")
    p3 = theoretical_edgeworth_coefficients()
    all_results["theoretical_edgeworth"] = p3
    print(f"  X = log2(3) - v2:")
    print(f"    E[X] = {p3['X_cumulants']['E[X]']:.8f}")
    print(f"    Var[X] = {p3['X_cumulants']['Var[X]']:.8f}")
    print(f"    Skewness(X) = {p3['X_cumulants']['skewness']:.8f}")
    print(f"    Kurtosis(X) = {p3['X_cumulants']['excess_kurtosis']:.8f}")
    print(f"  Berry-Esseen ratio rho/sigma^3 = {p3['Berry_Esseen']['BE_constant_ratio']:.8f}")

    # Part 4
    print("\n[Part 4] T vs T^2 CLT収束比較")
    p4 = t1_vs_t2_clt_comparison(100000)
    all_results["t1_vs_t2"] = p4
    print(f"  T1: skew={p4['T1_1step_stats']['skewness']:.4f}, kurt={p4['T1_1step_stats']['kurtosis']:.4f}")
    print(f"  T2: skew={p4['T2_1step_stats']['skewness']:.4f}, kurt={p4['T2_1step_stats']['kurtosis']:.4f}")
    print(f"  Skewness ratio (T2/T1): {p4['skewness_ratio']:.4f}")
    print(f"  Kurtosis ratio (T2/T1): {p4['kurtosis_ratio']:.4f}")
    for c in p4["comparison"]:
        print(f"    k={c['k']}: KS_T1={c['ks_T1_k_steps']:.6f}, KS_T2={c['ks_T2_k_steps']:.6f}, "
              f"ratio={c['ks_ratio_T1_over_T2']:.4f}")

    # Part 5
    print("\n[Part 5] 収束速度のべき乗則フィット")
    p5 = precise_convergence_rate(100000)
    all_results["convergence_rate"] = p5
    if p5["power_law_fit"]:
        print(f"  フィット: {p5['power_law_fit']['description']}")
    print(f"  {'k':>3} {'KS':>10} {'KS*sqrt(k)':>12} {'KS*k^(2/3)':>12}")
    for r in p5["convergence_data"]:
        print(f"  {r['k']:>3} {r['ks']:>10.6f} {r['ks_sqrt_k']:>12.6f} {r['ks_k_to_2_3']:>12.6f}")

    elapsed = time.time() - start_time
    print(f"\n総実行時間: {elapsed:.1f}秒")

    # 総合的な発見
    summary = {
        "key_insight_1": "1ステップ分布は上限bounded (log2(3)-1≈0.585)、左に重い裾を持つ",
        "key_insight_2": f"分散の{vd['between_fraction']*100:.1f}%はv2の値の違いで説明される（between-group）",
        "key_insight_3": f"v2ごとの条件付き分散は極めて小さい（within-group variance ≈ {list(p1['v2_conditioned'].values())[0]['variance_within_v2']:.6f}）",
        "key_insight_4": f"T^2の歪度はTの{abs(p4['skewness_ratio']):.2f}倍 → CLT収束が{1/abs(p4['skewness_ratio']):.2f}倍速い",
        "key_insight_5": f"収束べき指数: KS ≈ C * k^(-alpha) with alpha = {p5['power_law_fit']['alpha']:.4f}" if p5["power_law_fit"] else "fitting failed",
        "theoretical_skewness": p3["X_cumulants"]["skewness"],
        "theoretical_kurtosis": p3["X_cumulants"]["excess_kurtosis"],
        "berry_esseen_const": p3["Berry_Esseen"]["BE_constant_ratio"],
    }
    all_results["summary"] = summary

    print("\n" + "=" * 70)
    print("総合的な発見")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k}: {v}")

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

    with open("/Users/soyukke/study/lean-unsolved/results/syr2_clt_deep_analysis.json", "w") as f:
        json.dump(make_serializable(all_results), f, indent=2)
    print("\n結果を results/syr2_clt_deep_analysis.json に保存しました")

if __name__ == "__main__":
    main()
