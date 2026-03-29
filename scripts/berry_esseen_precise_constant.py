#!/usr/bin/env python3
"""
Berry-Esseen精密定数の導出

コラッツ加速Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の増分
  X = log2(T(n)/n) = log2(3) - v2(3n+1)

既知: v2(3n+1) ~ Geom(1/2) (starting at 1)
  => X = log2(3) - V, V ~ Geom(1/2)
  => P(X = log2(3) - j) = 2^{-j}, j = 1, 2, 3, ...

完全離散分布からの閉公式導出:
  E[X] = log2(3) - E[V] = log2(3) - 2
  Var[X] = Var[V] = 2
  sigma = sqrt(2)

Berry-Esseen定理: sup|F_k(x) - Phi(x)| <= C * rho / (sigma^3 * sqrt(k))
  where rho = E[|X - E[X]|^3]

この rho を閉形式で計算し、実際の定数 C を数値的に推定する。
"""

import math
import random
import time
import json
from collections import Counter

# ============================================================
# 定数
# ============================================================
LOG2_3 = math.log2(3)  # 1.58496...
MU = LOG2_3 - 2        # -0.41504...

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

# ============================================================
# Part 1: 完全離散増分の閉公式モーメント導出
# ============================================================

def exact_moments():
    """
    X = log2(3) - V where V ~ Geom(1/2), P(V=j) = 2^{-j}, j >= 1

    E[V] = 2
    E[V^2] = 6
    E[V^3] = 26
    E[V^4] = 150
    E[V^5] = 1082
    E[V^6] = 9366

    一般に E[V^n] = Li_{-n}(1/2) where Li は多重対数関数
    ただし Geom(1/2) starting at 1 では:
    E[V^k] = sum_{j=1}^{inf} j^k * 2^{-j}
    """
    print("=" * 70)
    print("Part 1: 完全離散増分の閉公式モーメント")
    print("=" * 70)

    # 数値的にモーメントを高精度計算
    # sum_{j=1}^{inf} j^k * 2^{-j} を十分大きな j まで
    max_j = 200

    raw_moments_V = {}
    for k in range(1, 7):
        s = sum(j**k * 2**(-j) for j in range(1, max_j + 1))
        raw_moments_V[k] = s
        print(f"  E[V^{k}] = {s}")

    # X = log2(3) - V のモーメント
    # E[X] = log2(3) - E[V]
    mu_X = LOG2_3 - raw_moments_V[1]
    print(f"\n  E[X] = log2(3) - 2 = {mu_X:.15f}")
    print(f"  log2(3) = {LOG2_3:.15f}")

    # 中心モーメント mu_k = E[(X - E[X])^k]
    # X - E[X] = -(V - E[V]) = -(V - 2)
    # => mu_k(X) = (-1)^k * mu_k(V)
    mu_V = raw_moments_V[1]  # = 2

    central_moments_V = {}
    # mu_2(V) = E[(V-2)^2] = E[V^2] - 4E[V] + 4 = 6 - 8 + 4 = 2
    central_moments_V[2] = raw_moments_V[2] - 2 * mu_V * raw_moments_V[1] + mu_V**2
    # mu_3(V) = E[(V-2)^3] = E[V^3] - 3*2*E[V^2] + 3*4*E[V] - 8
    central_moments_V[3] = (raw_moments_V[3] - 3 * mu_V * raw_moments_V[2]
                           + 3 * mu_V**2 * raw_moments_V[1] - mu_V**3)
    # mu_4(V) = E[(V-2)^4]
    central_moments_V[4] = (raw_moments_V[4] - 4 * mu_V * raw_moments_V[3]
                           + 6 * mu_V**2 * raw_moments_V[2]
                           - 4 * mu_V**3 * raw_moments_V[1] + mu_V**4)
    # mu_5(V)
    central_moments_V[5] = (raw_moments_V[5] - 5 * mu_V * raw_moments_V[4]
                           + 10 * mu_V**2 * raw_moments_V[3]
                           - 10 * mu_V**3 * raw_moments_V[2]
                           + 5 * mu_V**4 * raw_moments_V[1] - mu_V**5)
    # mu_6(V)
    central_moments_V[6] = (raw_moments_V[6] - 6 * mu_V * raw_moments_V[5]
                           + 15 * mu_V**2 * raw_moments_V[4]
                           - 20 * mu_V**3 * raw_moments_V[3]
                           + 15 * mu_V**4 * raw_moments_V[2]
                           - 6 * mu_V**5 * raw_moments_V[1] + mu_V**6)

    # X - E[X] = -(V - 2) だから
    # mu_k(X) = (-1)^k * mu_k(V)
    central_moments_X = {}
    for k in range(2, 7):
        central_moments_X[k] = (-1)**k * central_moments_V[k]

    sigma_X = math.sqrt(central_moments_X[2])

    # 標準化モーメント
    standardized_X = {}
    for k in range(2, 7):
        standardized_X[k] = central_moments_X[k] / sigma_X**k

    print(f"\n  中心モーメント (X = log2(3) - V):")
    for k in range(2, 7):
        print(f"    mu_{k}(X) = {central_moments_X[k]:.10f}")

    print(f"\n  sigma(X) = sqrt({central_moments_X[2]:.10f}) = {sigma_X:.10f}")

    print(f"\n  標準化モーメント:")
    for k in range(2, 7):
        print(f"    gamma_{k} = mu_{k}/sigma^{k} = {standardized_X[k]:.10f}")

    # キュムラント
    kappa = {}
    kappa[1] = mu_X
    kappa[2] = central_moments_X[2]  # = sigma^2 = 2
    kappa[3] = central_moments_X[3]  # = mu_3 (第3キュムラント = 第3中心モーメント)
    kappa[4] = central_moments_X[4] - 3 * central_moments_X[2]**2  # 第4キュムラント
    # kappa_5 = mu_5 - 10*mu_3*mu_2
    kappa[5] = central_moments_X[5] - 10 * central_moments_X[3] * central_moments_X[2]
    # kappa_6 = mu_6 - 15*mu_4*mu_2 - 10*mu_3^2 + 30*mu_2^3
    kappa[6] = (central_moments_X[6] - 15 * central_moments_X[4] * central_moments_X[2]
                - 10 * central_moments_X[3]**2 + 30 * central_moments_X[2]**3)

    print(f"\n  キュムラント:")
    for k in range(1, 7):
        print(f"    kappa_{k} = {kappa[k]:.10f}")

    # Berry-Esseen定数に必要な量
    # rho = E[|X - E[X]|^3]
    # X - E[X] = -(V - 2) = 2 - V
    # |X - E[X]|^3 = |V - 2|^3
    rho = sum(abs(j - 2)**3 * 2**(-j) for j in range(1, max_j + 1))

    print(f"\n  Berry-Esseen パラメータ:")
    print(f"    rho = E[|X - mu|^3] = E[|V - 2|^3] = {rho:.10f}")
    print(f"    sigma^3 = ({sigma_X:.10f})^3 = {sigma_X**3:.10f}")
    print(f"    rho / sigma^3 = {rho / sigma_X**3:.10f}")

    # 各項の寄与を分解
    print(f"\n  rho の各項の寄与:")
    total_rho = 0
    for j in range(1, 15):
        contrib = abs(j - 2)**3 * 2**(-j)
        total_rho += contrib
        print(f"    j={j}: |{j}-2|^3 * 2^{{-{j}}} = {abs(j-2)**3} * {2**(-j):.10f} = {contrib:.10f} (累積: {total_rho:.10f})")

    # 解析的な rho の導出
    # rho = sum_{j=1}^{inf} |j-2|^3 * 2^{-j}
    # = |1-2|^3 * 2^{-1} + |2-2|^3 * 2^{-2} + sum_{j=3}^{inf} (j-2)^3 * 2^{-j}
    # = 1 * 1/2 + 0 + sum_{m=1}^{inf} m^3 * 2^{-(m+2)}
    # = 1/2 + (1/4) * sum_{m=1}^{inf} m^3 * 2^{-m}
    # = 1/2 + (1/4) * E[V^3 for Geom(1/2)]... ただしこれは j=1 の V^3
    # E_geom[V^3] = 26 だから
    # = 1/2 + 26/4 = 1/2 + 13/2 = 14/2 = 7
    #
    # 待って。計算し直す
    # sum_{j=3}^{inf} (j-2)^3 * 2^{-j} = sum_{m=1}^{inf} m^3 * 2^{-(m+2)} = (1/4) * sum_{m=1}^{inf} m^3 * 2^{-m}
    # sum_{m=1}^{inf} m^3 * 2^{-m} = 26
    # => = 26/4 = 13/2
    #
    # rho = 1/2 + 0 + 13/2 = 14/2 = 7

    rho_analytical = 0.5 + 0 + 26.0 / 4.0
    print(f"\n  解析的 rho:")
    print(f"    rho = 1/2 + 0 + 26/4 = {rho_analytical}")
    print(f"    数値計算との差: {abs(rho - rho_analytical):.15e}")

    # sigma^3 = (sqrt(2))^3 = 2*sqrt(2)
    sigma3 = 2 * math.sqrt(2)
    print(f"    sigma^3 = 2*sqrt(2) = {sigma3:.10f}")
    print(f"    rho / sigma^3 = 7 / (2*sqrt(2)) = {7.0 / sigma3:.10f}")
    print(f"    = 7*sqrt(2)/4 = {7 * math.sqrt(2) / 4:.10f}")

    return {
        "raw_moments_V": raw_moments_V,
        "central_moments_X": central_moments_X,
        "standardized_moments_X": standardized_X,
        "cumulants": kappa,
        "sigma": sigma_X,
        "rho": rho,
        "rho_analytical": rho_analytical,
        "sigma_cubed": sigma3,
        "rho_over_sigma3": rho / sigma3,
        "rho_over_sigma3_exact": "7*sqrt(2)/4",
    }


# ============================================================
# Part 2: Edgeworth展開の高次項の閉公式
# ============================================================

def edgeworth_closed_form(moments_data):
    """
    S_k = X_1 + ... + X_k のEdgeworth展開
    W_k = (S_k - k*mu) / (sigma * sqrt(k))

    P(W_k <= x) = Phi(x) + c_1/sqrt(k) * p_1(x)*phi(x)
                         + c_2/k * p_2(x)*phi(x) + ...

    第1項: -(gamma_3 / 6) / sqrt(k) * (x^2 - 1) * phi(x)
    第2項: [ gamma_4/(24*k) * (x^3 - 3x) + gamma_3^2/(72*k) * (x^5 - 10x^3 + 15x) ] * phi(x)

    ここで gamma_3 = kappa_3/sigma^3 = skewness, gamma_4 = kappa_4/sigma^4 = excess kurtosis
    """
    print("\n" + "=" * 70)
    print("Part 2: Edgeworth展開の閉公式")
    print("=" * 70)

    kappa = moments_data["cumulants"]
    sigma = moments_data["sigma"]

    gamma3 = kappa[3] / sigma**3  # skewness
    gamma4 = kappa[4] / sigma**4  # excess kurtosis
    gamma5 = kappa[5] / sigma**5
    gamma6 = kappa[6] / sigma**6

    print(f"  標準化キュムラント:")
    print(f"    gamma_3 (skewness) = {gamma3:.10f}")
    print(f"    gamma_4 (excess kurtosis) = {gamma4:.10f}")
    print(f"    gamma_5 = {gamma5:.10f}")
    print(f"    gamma_6 = {gamma6:.10f}")

    # 解析的な gamma_3 の導出
    # kappa_3 = mu_3(X) = -mu_3(V)
    # mu_3(V) = E[(V-2)^3] = E[V^3] - 6E[V^2] + 12E[V] - 8
    #         = 26 - 36 + 24 - 8 = 6
    # => kappa_3 = -6
    # gamma_3 = -6 / (sqrt(2))^3 = -6 / (2*sqrt(2)) = -3/sqrt(2) = -3*sqrt(2)/2
    gamma3_exact = -3 * math.sqrt(2) / 2
    print(f"\n  解析的 gamma_3:")
    print(f"    mu_3(V) = 26 - 36 + 24 - 8 = 6")
    print(f"    kappa_3 = -6")
    print(f"    gamma_3 = -6/(2*sqrt(2)) = -3*sqrt(2)/2 = {gamma3_exact:.10f}")
    print(f"    数値との差: {abs(gamma3 - gamma3_exact):.15e}")

    # gamma_4 の導出
    # mu_4(V) = E[(V-2)^4] = E[V^4] - 8E[V^3] + 24E[V^2] - 32E[V] + 16
    #         = 150 - 208 + 144 - 64 + 16 = 38
    # mu_4(X) = mu_4(V) = 38 (偶数乗なので符号変わらず)
    # kappa_4 = mu_4 - 3*sigma^4 = 38 - 3*4 = 38 - 12 = 26
    # gamma_4 = 26/4 = 13/2 = 6.5
    gamma4_exact = 13.0 / 2.0
    print(f"\n  解析的 gamma_4:")
    print(f"    mu_4(V) = 150 - 208 + 144 - 64 + 16 = 38")
    print(f"    kappa_4 = 38 - 3*4 = 26")
    print(f"    gamma_4 = 26/4 = 13/2 = {gamma4_exact}")
    print(f"    数値との差: {abs(gamma4 - gamma4_exact):.15e}")

    # Edgeworth展開のCDF補正のsup計算
    # 第1項のsup: |gamma_3/6| * sup_x |(x^2-1)*phi(x)|
    # (x^2-1)*phi(x) のsup: d/dx[(x^2-1)*phi(x)] = 0
    # => (2x)*phi(x) + (x^2-1)*(-x*phi(x)) = phi(x)*(2x - x^3 + x) = phi(x)*(3x - x^3)
    # = phi(x)*x*(3 - x^2) = 0 => x = 0 or x = sqrt(3)
    # |x^2-1|*phi(x) at x=0: 1*phi(0) = 1/sqrt(2*pi) = 0.3989
    # at x=sqrt(3): 2*phi(sqrt(3)) = 2*exp(-3/2)/sqrt(2*pi) = 2*0.0893 = 0.1786
    # => sup = 1/sqrt(2*pi) (at x=0)

    sup_he2_phi = 1.0 / math.sqrt(2 * math.pi)

    # 第1項のsup寄与 (CDFへの)
    # -(gamma_3/6) * He_2(x) * phi(x) の積分としてのCDFへの寄与のsupは
    # |(gamma_3/6)| * |He_2(x)*phi(x)| を x 全体で sup
    # ただしCDFの場合は Phi(x) - F_k(x) の sup を見る

    # Berry-Esseen型の上界
    # Edgeworth第1項のKSへの寄与:
    # |gamma_3| / (6*sqrt(k)) * sup_x |He_2(x)*phi(x)|
    # = |gamma_3| / (6*sqrt(k)) * (1/sqrt(2*pi))

    c1_coeff = abs(gamma3) / 6 * sup_he2_phi
    print(f"\n  Edgeworth展開 KS寄与の上界:")
    print(f"    第1項: |gamma_3|/(6*sqrt(k)) * sup|He_2*phi| / sqrt(k)")
    print(f"          = {abs(gamma3):.6f}/6 * {sup_he2_phi:.6f} / sqrt(k)")
    print(f"          = {c1_coeff:.6f} / sqrt(k)")

    # 第2項の寄与
    # gamma_4/(24*k) * sup|(x^3-3x)*phi(x)| + gamma_3^2/(72*k) * sup|(x^5-10x^3+15x)*phi(x)|
    # (x^3-3x)*phi(x) = He_3(x)*phi(x) の sup を数値計算
    import numpy as np

    x_arr = np.linspace(-10, 10, 100000)
    phi_arr = np.exp(-0.5 * x_arr**2) / np.sqrt(2 * np.pi)

    he2 = x_arr**2 - 1
    he3 = x_arr**3 - 3*x_arr
    he5 = x_arr**5 - 10*x_arr**3 + 15*x_arr

    sup_he2_phi_num = np.max(np.abs(he2 * phi_arr))
    sup_he3_phi_num = np.max(np.abs(he3 * phi_arr))
    sup_he5_phi_num = np.max(np.abs(he5 * phi_arr))

    print(f"\n  Hermite多項式 * phi(x) のsup:")
    print(f"    sup|He_2*phi| = {sup_he2_phi_num:.10f} (解析: {sup_he2_phi:.10f})")
    print(f"    sup|He_3*phi| = {sup_he3_phi_num:.10f}")
    print(f"    sup|He_5*phi| = {sup_he5_phi_num:.10f}")

    c2a_coeff = abs(gamma4) / 24 * sup_he3_phi_num
    c2b_coeff = gamma3**2 / 72 * sup_he5_phi_num
    c2_coeff = c2a_coeff + c2b_coeff

    print(f"\n    第2項a: |gamma_4|/24 * sup|He_3*phi| = {c2a_coeff:.10f}")
    print(f"    第2項b: gamma_3^2/72 * sup|He_5*phi| = {c2b_coeff:.10f}")
    print(f"    第2項合計: {c2_coeff:.10f} / k")

    # 予測KS: c1/sqrt(k) + c2/k
    print(f"\n  予測 KS(k) = {c1_coeff:.6f}/sqrt(k) + {c2_coeff:.6f}/k + O(k^{{-3/2}})")

    for k in [1, 2, 3, 5, 10, 20, 50, 100]:
        ks_pred = c1_coeff / math.sqrt(k) + c2_coeff / k
        print(f"    k={k:3d}: KS_pred = {ks_pred:.6f}")

    return {
        "gamma3": gamma3,
        "gamma3_exact": "-3*sqrt(2)/2",
        "gamma3_exact_value": gamma3_exact,
        "gamma4": gamma4,
        "gamma4_exact": "13/2",
        "gamma4_exact_value": gamma4_exact,
        "gamma5": gamma5,
        "gamma6": gamma6,
        "c1_coeff": c1_coeff,
        "c2_coeff": c2_coeff,
        "sup_He2_phi": sup_he2_phi_num,
        "sup_He3_phi": sup_he3_phi_num,
        "sup_He5_phi": sup_he5_phi_num,
    }


# ============================================================
# Part 3: 数値検証 - KSスケーリング vs 理論予測
# ============================================================

def ks_scaling_verification(moments_data, edgeworth_data, N_samples=300000):
    """
    実際のKS統計量と理論予測の比較
    KS ~ c1/sqrt(k) + c2/k を検証
    """
    print("\n" + "=" * 70)
    print("Part 3: KS統計量の理論予測 vs 数値検証")
    print("=" * 70)

    import numpy as np

    sigma = moments_data["sigma"]
    mu = MU
    kappa3 = moments_data["cumulants"][3]
    kappa4 = moments_data["cumulants"][4]
    gamma3 = edgeworth_data["gamma3"]
    gamma4 = edgeworth_data["gamma4"]

    def phi(x):
        return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

    def Phi(x):
        return 0.5 * (1 + np.vectorize(math.erf)(x / np.sqrt(2)))

    def edgeworth_cdf(x, k):
        """Edgeworth展開によるCDF"""
        t0 = Phi(x)
        t1 = -(gamma3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi(x)
        t2a = (gamma4 / (24 * k)) * (x**3 - 3*x) * phi(x)
        t2b = (gamma3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi(x)
        return t0 + t1 + t2a + t2b

    results = []
    k_values = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 75, 100]

    for k in k_values:
        n_use = min(N_samples, max(50000, N_samples // max(1, k // 5)))
        print(f"  k={k:3d} (n={n_use})...")

        sums = []
        for _ in range(n_use):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * mu
        sigma_k = sigma * math.sqrt(k)
        standardized = np.array([(s - mu_k) / sigma_k for s in sums])
        sorted_z = np.sort(standardized)
        n_z = len(sorted_z)

        # KS vs CLT
        ecdf_vals = np.arange(1, n_z + 1) / n_z
        clt_cdf = Phi(sorted_z)
        ks_clt = np.max(np.abs(ecdf_vals - clt_cdf))

        # KS vs Edgeworth
        edge_cdf = edgeworth_cdf(sorted_z, k)
        ks_edge = np.max(np.abs(ecdf_vals - edge_cdf))

        # 理論予測
        c1 = edgeworth_data["c1_coeff"]
        c2 = edgeworth_data["c2_coeff"]
        ks_pred_1 = c1 / math.sqrt(k)
        ks_pred_12 = c1 / math.sqrt(k) + c2 / k

        results.append({
            "k": k,
            "n_samples": n_z,
            "ks_clt": float(ks_clt),
            "ks_edgeworth": float(ks_edge),
            "ks_pred_term1": ks_pred_1,
            "ks_pred_terms12": ks_pred_12,
            "ratio_clt_over_pred1": float(ks_clt / ks_pred_1) if ks_pred_1 > 0 else None,
            "ks_times_sqrt_k": float(ks_clt * math.sqrt(k)),
            "improvement_edge": float(ks_clt / ks_edge) if ks_edge > 0 else None,
        })

        print(f"    KS_clt={ks_clt:.6f}, KS_edge={ks_edge:.6f}, pred={ks_pred_12:.6f}, "
              f"ratio={ks_clt/ks_pred_1:.4f}")

    # KS * sqrt(k) の漸近値を推定
    ks_sqrt_k = [r["ks_times_sqrt_k"] for r in results if r["k"] >= 10]
    if ks_sqrt_k:
        print(f"\n  KS*sqrt(k) for k>=10: mean={np.mean(ks_sqrt_k):.6f}, std={np.std(ks_sqrt_k):.6f}")

    # フィッティング: KS = A * k^alpha
    from numpy.polynomial import polynomial as P
    log_k = np.array([np.log(r["k"]) for r in results if r["k"] >= 3])
    log_ks = np.array([np.log(r["ks_clt"]) for r in results if r["k"] >= 3])

    if len(log_k) >= 3:
        coeffs = np.polyfit(log_k, log_ks, 1)
        alpha_fit = coeffs[0]
        A_fit = np.exp(coeffs[1])
        print(f"\n  Power law fit KS = A * k^alpha:")
        print(f"    alpha = {alpha_fit:.6f} (理論: -0.5)")
        print(f"    A = {A_fit:.6f}")
        print(f"    理論 A = c1 = {edgeworth_data['c1_coeff']:.6f}")

    return {
        "results": results,
        "power_law_alpha": float(alpha_fit) if len(log_k) >= 3 else None,
        "power_law_A": float(A_fit) if len(log_k) >= 3 else None,
        "theoretical_c1": edgeworth_data["c1_coeff"],
    }


# ============================================================
# Part 4: 精密Edgeworth CDF vs 実データの直接比較
# ============================================================

def edgeworth_pointwise_analysis(moments_data, edgeworth_data, N_samples=200000):
    """
    特定のkで、CDFの各点でのEdgeworth近似誤差を分析
    最大誤差が生じる x の位置を特定
    """
    print("\n" + "=" * 70)
    print("Part 4: Edgeworth近似の精密点別分析")
    print("=" * 70)

    import numpy as np

    sigma = moments_data["sigma"]
    mu_val = MU
    gamma3 = edgeworth_data["gamma3"]
    gamma4 = edgeworth_data["gamma4"]

    def phi(x):
        return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

    def Phi(x):
        return 0.5 * (1 + np.vectorize(math.erf)(x / np.sqrt(2)))

    def edgeworth_cdf(x, k):
        t0 = Phi(x)
        t1 = -(gamma3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi(x)
        t2a = (gamma4 / (24 * k)) * (x**3 - 3*x) * phi(x)
        t2b = (gamma3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi(x)
        return t0 + t1 + t2a + t2b

    results = {}
    for k in [5, 10, 20]:
        print(f"\n  k={k}:")
        sums = []
        for _ in range(N_samples):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * mu_val
        sigma_k = sigma * math.sqrt(k)
        standardized = np.sort(np.array([(s - mu_k) / sigma_k for s in sums]))
        n_z = len(standardized)
        ecdf = np.arange(1, n_z + 1) / n_z

        clt_vals = Phi(standardized)
        edge_vals = edgeworth_cdf(standardized, k)

        err_clt = ecdf - clt_vals
        err_edge = ecdf - edge_vals

        # 最大正・負誤差の位置
        idx_max_pos_clt = np.argmax(err_clt)
        idx_max_neg_clt = np.argmin(err_clt)
        idx_max_pos_edge = np.argmax(err_edge)
        idx_max_neg_edge = np.argmin(err_edge)

        print(f"    CLT max+ error: {err_clt[idx_max_pos_clt]:.6f} at z={standardized[idx_max_pos_clt]:.4f}")
        print(f"    CLT max- error: {err_clt[idx_max_neg_clt]:.6f} at z={standardized[idx_max_neg_clt]:.4f}")
        print(f"    Edge max+ error: {err_edge[idx_max_pos_edge]:.6f} at z={standardized[idx_max_pos_edge]:.4f}")
        print(f"    Edge max- error: {err_edge[idx_max_neg_edge]:.6f} at z={standardized[idx_max_neg_edge]:.4f}")
        print(f"    KS_clt = {np.max(np.abs(err_clt)):.6f}, KS_edge = {np.max(np.abs(err_edge)):.6f}")

        # 第1項補正が最大となる理論的位置
        # -(gamma3/6)/sqrt(k) * (x^2-1)*phi(x) が最大: x=0 で (0-1)*phi(0) = -0.399
        # なので gamma3 < 0 => 補正は正 => x=0 近辺で ecdf > Phi が期待

        # Edgeworth第1項の寄与の符号分析
        x_grid = np.linspace(-4, 4, 1000)
        term1_vals = -(gamma3 / (6 * math.sqrt(k))) * (x_grid**2 - 1) * phi(x_grid)

        results[k] = {
            "ks_clt": float(np.max(np.abs(err_clt))),
            "ks_edge": float(np.max(np.abs(err_edge))),
            "max_pos_err_clt_z": float(standardized[idx_max_pos_clt]),
            "max_neg_err_clt_z": float(standardized[idx_max_neg_clt]),
            "max_pos_err_edge_z": float(standardized[idx_max_pos_edge]),
            "max_neg_err_edge_z": float(standardized[idx_max_neg_edge]),
            "term1_max_value": float(np.max(term1_vals)),
            "term1_max_position": float(x_grid[np.argmax(term1_vals)]),
        }

    return results


# ============================================================
# Part 5: C_BE定数の精密推定 (実効Berry-Esseen定数)
# ============================================================

def estimate_effective_BE_constant(moments_data, N_samples=200000):
    """
    Berry-Esseen定理: sup|F_k - Phi| <= C_BE * rho / (sigma^3 * sqrt(k))

    この C_BE を数値的に推定する:
    C_BE_eff(k) = sup|F_k - Phi| * sigma^3 * sqrt(k) / rho

    k -> inf で C_BE_eff(k) -> 実効定数
    (既知の最良上界: C_BE <= 0.4748)
    """
    print("\n" + "=" * 70)
    print("Part 5: 実効Berry-Esseen定数の推定")
    print("=" * 70)

    sigma = moments_data["sigma"]
    rho = moments_data["rho"]
    sigma3 = moments_data["sigma_cubed"]

    # BE定数の分母: rho / sigma^3
    be_denom = rho / sigma3
    print(f"  rho = {rho:.10f}")
    print(f"  sigma^3 = {sigma3:.10f}")
    print(f"  rho/sigma^3 = {be_denom:.10f}")
    print(f"  解析的: 7/(2*sqrt(2)) = 7*sqrt(2)/4 = {7*math.sqrt(2)/4:.10f}")

    results = []

    for k in [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 75, 100]:
        n_use = min(N_samples, max(30000, N_samples // max(1, k // 5)))
        print(f"  k={k:3d} (n={n_use})...", end="", flush=True)

        sums = []
        for _ in range(n_use):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * MU
        sigma_k = sigma * math.sqrt(k)
        standardized = sorted([(s - mu_k) / sigma_k for s in sums])
        n_z = len(standardized)

        ks = 0
        for i, z in enumerate(standardized):
            cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
            ecdf = (i + 1) / n_z
            ks = max(ks, abs(ecdf - cdf), abs(i / n_z - cdf))

        # C_BE_eff = KS * sqrt(k) / (rho/sigma^3)
        c_be_eff = ks * math.sqrt(k) / be_denom

        # Edgeworth第1項予測 KS ~ |gamma3|/(6) * sup|He2*phi| / sqrt(k)
        # => C_eff = |gamma3|/(6) * sup|He2*phi| / (rho/sigma^3)

        results.append({
            "k": k,
            "ks": ks,
            "ks_sqrt_k": ks * math.sqrt(k),
            "c_be_effective": c_be_eff,
        })
        print(f"  KS={ks:.6f}, C_BE_eff={c_be_eff:.6f}")

    # 漸近的なC_BEの推定
    large_k_results = [r for r in results if r["k"] >= 10]
    if large_k_results:
        c_be_values = [r["c_be_effective"] for r in large_k_results]
        mean_c_be = sum(c_be_values) / len(c_be_values)
        print(f"\n  大k (>=10) での C_BE 平均: {mean_c_be:.6f}")
        print(f"  理論上界 (Shevtsova 2011): 0.4748")
        print(f"  比率: {mean_c_be / 0.4748:.4f}")

    # 理論的Edgeworth第1項定数
    gamma3 = -3 * math.sqrt(2) / 2
    sup_he2_phi = 1.0 / math.sqrt(2 * math.pi)
    c1_theoretical = abs(gamma3) / 6 * sup_he2_phi
    c_be_from_edgeworth = c1_theoretical / be_denom

    print(f"\n  Edgeworth第1項からのC_BE推定:")
    print(f"    c1 = |gamma_3|/6 * sup|He_2*phi| = {c1_theoretical:.10f}")
    print(f"    C_BE_edgeworth = c1 / (rho/sigma^3) = {c_be_from_edgeworth:.10f}")

    return {
        "results": results,
        "rho": rho,
        "sigma_cubed": sigma3,
        "rho_over_sigma3": be_denom,
        "c_be_from_edgeworth": c_be_from_edgeworth,
        "c1_theoretical": c1_theoretical,
    }


# ============================================================
# Part 6: KS ~ 0.28 * k^{-0.514} の理論的根拠
# ============================================================

def ks_scaling_theory(moments_data, edgeworth_data):
    """
    KS ~ 0.28 * k^{-0.514} が観察されている場合の理論的説明

    純粋なBE定理なら KS ~ C/sqrt(k) だが、
    Edgeworth展開なら KS ~ c1/sqrt(k) + c2/k + ... でパワーが-0.5より急
    有限kではフィットで alpha < -0.5 に見える
    """
    print("\n" + "=" * 70)
    print("Part 6: KS ~ 0.28 * k^{-0.514} の理論的根拠")
    print("=" * 70)

    import numpy as np

    c1 = edgeworth_data["c1_coeff"]
    c2 = edgeworth_data["c2_coeff"]

    print(f"  Edgeworth予測: KS(k) = {c1:.6f}/sqrt(k) + {c2:.6f}/k")

    # この関数 f(k) = c1/sqrt(k) + c2/k を power law A*k^alpha にフィット
    k_range = np.arange(3, 101)
    ks_theory = c1 / np.sqrt(k_range) + c2 / k_range

    log_k = np.log(k_range)
    log_ks = np.log(ks_theory)

    # 線形フィット
    coeffs = np.polyfit(log_k, log_ks, 1)
    alpha = coeffs[0]
    A = np.exp(coeffs[1])

    print(f"\n  Edgeworth予測の power law fit (k=3..100):")
    print(f"    alpha = {alpha:.6f}")
    print(f"    A = {A:.6f}")

    # 部分区間でのフィット
    for k_min, k_max in [(3, 10), (5, 20), (10, 50), (20, 100), (3, 50)]:
        mask = (k_range >= k_min) & (k_range <= k_max)
        c = np.polyfit(log_k[mask], log_ks[mask], 1)
        print(f"    k={k_min:3d}-{k_max:3d}: alpha={c[0]:.6f}, A={np.exp(c[1]):.6f}")

    # KS = c1/sqrt(k) + c2/k の場合
    # d(log KS)/d(log k) = -1/2 * (1 + c2/(c1*sqrt(k))) / (1 + c2/(c1*sqrt(k)))
    # これは k が有限のとき -1/2 より小さい（負の補正がある場合）

    # 瞬間的な指数: d(log KS)/d(log k)
    print(f"\n  局所べき指数 d(log KS)/d(log k):")
    for k in [3, 5, 10, 20, 50, 100]:
        # 数値微分
        dk = 0.01
        f_plus = c1 / math.sqrt(k + dk) + c2 / (k + dk)
        f_minus = c1 / math.sqrt(k - dk) + c2 / (k - dk)
        local_alpha = (math.log(f_plus) - math.log(f_minus)) / (math.log(k + dk) - math.log(k - dk))
        print(f"    k={k:3d}: alpha_local = {local_alpha:.6f}")

    # c2/c1 の物理的意味
    print(f"\n  c2/c1 ratio = {c2/c1:.6f}")
    print(f"  c2/(c1) が正なら、有限kでの有効 alpha は -0.5 より大きい（遅い収束）")
    print(f"  c2/(c1) が負なら、有限kでの有効 alpha は -0.5 より小さい（速い収束に見える）")

    # 0.28 * k^{-0.514} と Edgeworth予測の比較
    print(f"\n  0.28 * k^{{-0.514}} vs Edgeworth予測:")
    print(f"  {'k':>5} {'0.28*k^-0.514':>15} {'Edgeworth':>12} {'ratio':>10}")
    for k in [2, 3, 5, 10, 20, 50, 100]:
        empirical_model = 0.28 * k**(-0.514)
        edge_pred = c1 / math.sqrt(k) + c2 / k
        print(f"  {k:5d} {empirical_model:15.6f} {edge_pred:12.6f} {empirical_model/edge_pred:10.4f}")

    return {
        "c1": c1,
        "c2": c2,
        "c2_over_c1": c2 / c1,
        "power_law_fit_alpha": float(alpha),
        "power_law_fit_A": float(A),
    }


# ============================================================
# Part 7: sigma^2 = 2 の純粋解析的証明
# ============================================================

def variance_analytical_proof():
    """
    sigma^2 = Var[X] = 2 の解析的証明

    X = log2(3) - V, V ~ Geom(1/2) starting at 1
    Var[X] = Var[V] (定数の引き算は分散不変)

    Var[V] = E[V^2] - (E[V])^2

    E[V] = sum_{j=1}^{inf} j * 2^{-j} = 2
    E[V^2] = sum_{j=1}^{inf} j^2 * 2^{-j} = 6

    Var[V] = 6 - 4 = 2
    """
    print("\n" + "=" * 70)
    print("Part 7: 分散 sigma^2 = 2 の解析的導出")
    print("=" * 70)

    # 解析的導出の詳細
    print("  V ~ Geom(1/2), P(V=j) = 2^{-j}, j=1,2,3,...")
    print()

    # E[V] の導出
    # sum_{j=1}^{inf} j*x^j = x/(1-x)^2 for |x| < 1
    # x = 1/2: sum = (1/2)/(1/2)^2 = (1/2)/(1/4) = 2
    print("  E[V] = sum_{j>=1} j * 2^{-j}")
    print("       = sum_{j>=1} j * (1/2)^j")
    print("       = (1/2) / (1 - 1/2)^2   [generating function identity]")
    print("       = (1/2) / (1/4) = 2")

    # E[V^2] の導出
    # sum_{j=1}^{inf} j^2 * x^j = x*(1+x)/(1-x)^3
    # x = 1/2: (1/2)*(3/2)/(1/2)^3 = (3/4)/(1/8) = 6
    print()
    print("  E[V^2] = sum_{j>=1} j^2 * 2^{-j}")
    print("         = sum_{j>=1} j^2 * (1/2)^j")
    print("         = (1/2)(1 + 1/2) / (1 - 1/2)^3")
    print("         = (1/2)(3/2) / (1/8) = (3/4)/(1/8) = 6")

    print()
    print("  Var[V] = E[V^2] - (E[V])^2 = 6 - 4 = 2")
    print("  sigma = sqrt(2)")
    print("  sigma^3 = 2*sqrt(2)")

    # E[V^3] の導出
    # sum_{j=1}^{inf} j^3 * x^j = x(1+4x+x^2)/(1-x)^4
    # x = 1/2: (1/2)(1 + 2 + 1/4)/(1/2)^4 = (1/2)(13/4)/(1/16) = (13/8)/(1/16) = 26
    print()
    print("  E[V^3] = sum_{j>=1} j^3 * (1/2)^j")
    print("         = (1/2)(1 + 4*1/2 + (1/2)^2) / (1/2)^4")
    print("         = (1/2)(13/4) / (1/16) = 26")
    print()
    print("  mu_3(V) = E[(V-2)^3] = E[V^3] - 6*E[V^2] + 12*E[V] - 8")
    print("          = 26 - 36 + 24 - 8 = 6")
    print("  mu_3(X) = (-1)^3 * mu_3(V) = -6")
    print("  skewness = mu_3 / sigma^3 = -6 / (2*sqrt(2)) = -3*sqrt(2)/2")
    print(f"           = {-3*math.sqrt(2)/2:.10f}")

    # E[V^4] の導出
    # sum_{j=1}^{inf} j^4 * x^j = x(1+11x+11x^2+x^3)/(1-x)^5
    # x=1/2: (1/2)(1 + 11/2 + 11/4 + 1/8)/(1/2)^5
    # 分子: 1 + 5.5 + 2.75 + 0.125 = 9.375 = 75/8
    # (1/2)(75/8)/(1/32) = (75/16)/(1/32) = 75*32/16 = 150
    print()
    print("  E[V^4] = 150")
    print("  mu_4(V) = 150 - 8*26 + 24*6 - 32*2 + 16 = 150 - 208 + 144 - 64 + 16 = 38")
    print("  kappa_4 = 38 - 3*(2)^2 = 38 - 12 = 26")
    print("  gamma_4 = 26/4 = 13/2 = 6.5")

    return {
        "EV": 2,
        "EV2": 6,
        "EV3": 26,
        "EV4": 150,
        "Var_V": 2,
        "mu3_V": 6,
        "mu4_V": 38,
        "kappa3": -6,
        "kappa4": 26,
        "gamma3": -3*math.sqrt(2)/2,
        "gamma4": 6.5,
    }


# ============================================================
# メイン
# ============================================================

def main():
    start = time.time()
    all_results = {}

    print("Berry-Esseen精密定数の導出")
    print("コラッツ加速Syracuse増分 X = log2(3) - Geom(1/2)")
    print()

    # Part 7 first (purely analytical)
    p7 = variance_analytical_proof()
    all_results["analytical_proof"] = p7

    # Part 1: 閉公式モーメント
    p1 = exact_moments()
    all_results["exact_moments"] = p1

    # Part 2: Edgeworth閉公式
    p2 = edgeworth_closed_form(p1)
    all_results["edgeworth_closed_form"] = p2

    # Part 6: スケーリング理論
    p6 = ks_scaling_theory(p1, p2)
    all_results["ks_scaling_theory"] = p6

    # Part 3: 数値検証
    p3 = ks_scaling_verification(p1, p2, N_samples=150000)
    all_results["ks_scaling_verification"] = p3

    # Part 4: 点別分析
    p4 = edgeworth_pointwise_analysis(p1, p2, N_samples=100000)
    all_results["edgeworth_pointwise"] = p4

    # Part 5: C_BE推定
    p5 = estimate_effective_BE_constant(p1, N_samples=100000)
    all_results["effective_BE_constant"] = p5

    # 総括
    elapsed = time.time() - start

    summary = {
        "exact_closed_forms": {
            "E[X]": f"log2(3) - 2 = {MU:.15f}",
            "Var[X]": "2 (exact)",
            "sigma": "sqrt(2)",
            "sigma_cubed": "2*sqrt(2)",
            "rho_E|X-mu|^3": "7 (exact: 1/2 + 26/4 = 7)",
            "skewness_gamma3": "-3*sqrt(2)/2",
            "excess_kurtosis_gamma4": "13/2 = 6.5",
            "kappa3": "-6",
            "kappa4": "26",
        },
        "berry_esseen_bound": {
            "formula": "sup|F_k - Phi| <= C * rho/(sigma^3 * sqrt(k))",
            "rho_over_sigma3": f"7/(2*sqrt(2)) = 7*sqrt(2)/4 = {7*math.sqrt(2)/4:.10f}",
            "best_known_C": 0.4748,
            "theoretical_KS_bound": f"{0.4748 * 7 * math.sqrt(2) / 4:.6f} / sqrt(k)",
        },
        "edgeworth_expansion": {
            "term1": f"-gamma3/(6*sqrt(k)) * He2(x)*phi(x), coeff = {p2['c1_coeff']:.10f}/sqrt(k)",
            "term2": f"[gamma4/24 * He3 + gamma3^2/72 * He5]*phi/k, coeff = {p2['c2_coeff']:.10f}/k",
            "total_KS_prediction": f"{p2['c1_coeff']:.6f}/sqrt(k) + {p2['c2_coeff']:.6f}/k",
        },
        "ks_scaling_explanation": {
            "observed": "KS ~ 0.28 * k^{-0.514}",
            "explanation": ("Edgeworth展開の2項 c1/sqrt(k)+c2/k で "
                          f"有限kのpower lawフィットは alpha={p6['power_law_fit_alpha']:.4f}。"
                          "c2>0のため有限kでは-0.5より急な減衰に見える。"),
            "c1": p2["c1_coeff"],
            "c2": p2["c2_coeff"],
        },
    }
    all_results["summary"] = summary
    all_results["elapsed_seconds"] = elapsed

    print(f"\n{'='*70}")
    print("総括")
    print(f"{'='*70}")
    for section, content in summary.items():
        print(f"\n  [{section}]")
        if isinstance(content, dict):
            for k, v in content.items():
                print(f"    {k}: {v}")
        else:
            print(f"    {content}")

    print(f"\n  実行時間: {elapsed:.1f}秒")

    # 保存
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return str(obj)
            return round(obj, 12)
        elif hasattr(obj, 'item'):  # numpy scalar
            return float(obj)
        return obj

    with open("/Users/soyukke/study/lean-unsolved/results/berry_esseen_precise.json", "w") as f:
        json.dump(make_serializable(all_results), f, indent=2)

    print("\n結果を results/berry_esseen_precise.json に保存")


if __name__ == "__main__":
    main()
