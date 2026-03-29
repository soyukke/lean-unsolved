#!/usr/bin/env python3
"""
Berry-Esseen大kでのKS検証 修正版

問題: k>=50で軌道が1に到達 -> 増分が異常値になる
解決: 十分大きなnを使い、1到達を検出して除外
"""

import math
import random
import time
import json

LOG2_3 = math.log2(3)
MU = LOG2_3 - 2
SIGMA = math.sqrt(2.0)

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

def phi_std(x):
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)

def Phi_std(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def ks_with_large_n(N_samples=50000):
    """
    十分大きな n を使って k ステップの和を計算。
    1到達を検出して除外する。
    """
    print("=" * 70)
    print("大kでの修正KS検証 (1到達除外、大きなn)")
    print("=" * 70)

    # Edgeworth展開の閉公式定数
    gamma3 = -3*math.sqrt(2)/2  # = -6/(2*sqrt(2))
    gamma4 = 13.0/2.0           # = 26/4
    c1 = 1.0 / (4 * math.sqrt(math.pi))  # = 0.141047...
    # c2 は上界なのでまた計算
    # sup|He_3*phi| と sup|He_5*phi| の厳密値
    # He_3(x)*phi(x): d/dx = 0 => x*(x^2-3)*(-x*phi) + (3x^2-3)*phi = 0
    # = phi * [3x^2 - 3 - x^4 + 3x^2] = phi * [-x^4 + 6x^2 - 3] = 0
    # => x^4 - 6x^2 + 3 = 0 => x^2 = (6 +/- sqrt(24))/2 = 3 +/- sqrt(6)
    # x^2 = 3+sqrt(6) => x = sqrt(3+sqrt(6)) ~ 2.334
    # He_3(x)*phi(x) at that x: (x^3-3x)*phi(x)
    x_he3 = math.sqrt(3 + math.sqrt(6))
    sup_he3 = abs((x_he3**3 - 3*x_he3) * phi_std(x_he3))

    # He_5 の sup を数値で
    sup_he5 = 0.0
    for i in range(200001):
        x = -10 + 20 * i / 200000
        val = abs((x**5 - 10*x**3 + 15*x) * phi_std(x))
        sup_he5 = max(sup_he5, val)

    c2a = abs(gamma4) / 24 * sup_he3
    c2b = gamma3**2 / 72 * sup_he5
    c2 = c2a + c2b
    rho_s3 = 7 * math.sqrt(2) / 4

    print(f"  閉公式定数:")
    print(f"    c1 = 1/(4*sqrt(pi)) = {c1:.10f}")
    print(f"    sup|He_3*phi| = {sup_he3:.10f}")
    print(f"    sup|He_5*phi| = {sup_he5:.10f}")
    print(f"    c2 = {c2:.10f}")
    print(f"    rho/sigma^3 = 7*sqrt(2)/4 = {rho_s3:.10f}")

    def edgeworth_cdf(x, k):
        t0 = Phi_std(x)
        t1 = -(gamma3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi_std(x)
        t2a = (gamma4 / (24 * k)) * (x**3 - 3*x) * phi_std(x)
        t2b = (gamma3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi_std(x)
        return t0 + t1 + t2a + t2b

    results = []

    for k in [1, 2, 3, 5, 10, 20, 30, 50, 75, 100]:
        # kが大きいほど大きなnが必要
        n_min = max(10**9, 10**(8 + k // 10))
        n_max = n_min * 10
        n_use = min(N_samples, max(20000, N_samples // max(1, k // 5)))

        print(f"\n  k={k:3d} (n={n_use}, range=[{n_min:.0e},{n_max:.0e}])...")

        sums = []
        rejected = 0
        attempts = 0

        while len(sums) < n_use and attempts < n_use * 5:
            attempts += 1
            n = random.randint(n_min, n_max)
            if n % 2 == 0:
                n += 1

            s = 0.0
            reached_1 = False
            for step in range(k):
                if n == 1:
                    reached_1 = True
                    break
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn

            if reached_1:
                rejected += 1
                continue
            sums.append(s)

        if len(sums) < 100:
            print(f"    サンプル不足: {len(sums)}個")
            continue

        mu_k = k * MU
        sigma_k = SIGMA * math.sqrt(k)
        standardized = sorted([(s - mu_k) / sigma_k for s in sums])
        n_z = len(standardized)

        ks_clt = 0.0
        ks_edge = 0.0
        for i, z in enumerate(standardized):
            ecdf = (i + 1) / n_z
            clt_val = Phi_std(z)
            edge_val = edgeworth_cdf(z, k)
            ks_clt = max(ks_clt, abs(ecdf - clt_val), abs(i/n_z - clt_val))
            ks_edge = max(ks_edge, abs(ecdf - edge_val), abs(i/n_z - edge_val))

        ks_pred = c1 / math.sqrt(k) + c2 / k
        c_be = ks_clt * math.sqrt(k) / rho_s3

        print(f"    samples={n_z}, rejected={rejected}, "
              f"KS_clt={ks_clt:.6f}, KS_edge={ks_edge:.6f}, pred={ks_pred:.6f}, "
              f"C_BE={c_be:.4f}")
        print(f"    KS*sqrt(k) = {ks_clt*math.sqrt(k):.6f}")

        results.append({
            "k": k,
            "n_samples": n_z,
            "n_rejected": rejected,
            "ks_clt": ks_clt,
            "ks_edgeworth": ks_edge,
            "ks_pred_edgeworth": ks_pred,
            "ks_times_sqrt_k": ks_clt * math.sqrt(k),
            "c_be_effective": c_be,
            "ratio_actual_to_pred": ks_clt / ks_pred if ks_pred > 0 else None,
            "improvement_edge_over_clt": ks_clt / ks_edge if ks_edge > 0 else None,
        })

    # Power law fit
    log_data = [(math.log(r["k"]), math.log(r["ks_clt"])) for r in results if r["k"] >= 3]
    n_fit = len(log_data)
    if n_fit >= 3:
        sx = sum(x for x, y in log_data)
        sy = sum(y for x, y in log_data)
        sxx = sum(x**2 for x, y in log_data)
        sxy = sum(x*y for x, y in log_data)
        alpha = (n_fit * sxy - sx * sy) / (n_fit * sxx - sx**2)
        b = (sy - alpha * sx) / n_fit
        A = math.exp(b)
        print(f"\n  Power law fit (k>=3): KS = {A:.4f} * k^{{{alpha:.4f}}}")
    else:
        alpha, A = None, None

    # C_BE の漸近推定
    large_k_cbe = [r["c_be_effective"] for r in results if r["k"] >= 10]
    if large_k_cbe:
        print(f"\n  C_BE (k>=10): values = {[f'{x:.4f}' for x in large_k_cbe]}")
        print(f"  C_BE mean = {sum(large_k_cbe)/len(large_k_cbe):.6f}")

    # KS * sqrt(k) のトレンド
    print(f"\n  KS * sqrt(k) トレンド:")
    for r in results:
        print(f"    k={r['k']:3d}: {r['ks_times_sqrt_k']:.6f}")

    return {
        "results": results,
        "closed_form": {
            "c1": c1,
            "c1_exact": "1/(4*sqrt(pi))",
            "c2": c2,
            "gamma3": gamma3,
            "gamma4": gamma4,
            "rho_over_sigma3": rho_s3,
        },
        "power_law": {"alpha": alpha, "A": A} if alpha else None,
    }


def main():
    start = time.time()

    result = ks_with_large_n(N_samples=50000)

    elapsed = time.time() - start
    result["elapsed_seconds"] = elapsed

    print(f"\n実行時間: {elapsed:.1f}秒")

    # save
    def ser(obj):
        if isinstance(obj, dict):
            return {str(k): ser(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ser(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return str(obj)
            return round(obj, 12)
        return obj

    with open("/Users/soyukke/study/lean-unsolved/results/berry_esseen_large_k.json", "w") as f:
        json.dump(ser(result), f, indent=2)
    print("保存: results/berry_esseen_large_k.json")


if __name__ == "__main__":
    main()
