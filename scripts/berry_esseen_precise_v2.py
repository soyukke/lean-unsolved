#!/usr/bin/env python3
"""
Berry-Esseen精密定数の導出 (numpy不要版)

コラッツ加速Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の増分
  X = log2(T(n)/n) = log2(3) - v2(3n+1)

V = v2(3n+1) ~ Geom(1/2) (starting at 1) が完全離散であることを利用し、
全モーメント・キュムラントを閉公式で導出。

Berry-Esseen定数 C_BE と Edgeworth展開係数の閉公式を確立する。
"""

import math
import random
import time
import json
from collections import Counter

LOG2_3 = math.log2(3)
MU = LOG2_3 - 2

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


# ============================================================
# Part 1: 閉公式モーメント・キュムラント・rho
# ============================================================

def exact_closed_forms():
    """全量を解析的に導出"""
    print("=" * 70)
    print("Part 1: 完全離散増分の閉公式モーメント・キュムラント")
    print("=" * 70)

    # V ~ Geom(1/2) starting at 1: P(V=j) = 2^{-j}
    # E[V^k] = sum_{j>=1} j^k * 2^{-j}
    # 母関数 sum j^k x^j の x=1/2 での値

    # 数値的に高精度計算 (解析値と一致を確認)
    max_j = 200
    EV = {}
    for k in range(1, 7):
        EV[k] = sum(j**k * 2.0**(-j) for j in range(1, max_j + 1))

    # 解析的な値 (母関数から導出)
    # E[V^1] = 2
    # E[V^2] = 6
    # E[V^3] = 26
    # E[V^4] = 150
    # E[V^5] = 1082
    # E[V^6] = 9366
    analytic = {1: 2, 2: 6, 3: 26, 4: 150, 5: 1082, 6: 9366}

    print("\n  生のモーメント E[V^k]:")
    for k in range(1, 7):
        print(f"    E[V^{k}] = {EV[k]:.1f} (解析: {analytic[k]})")

    # 中心モーメント mu_k(V) = E[(V-2)^k]
    # 二項展開で計算
    mu_V = EV[1]  # = 2
    cm_V = {}
    # mu_2(V) = E[V^2] - 2*2*E[V] + 4 = 6 - 8 + 4 = 2
    cm_V[2] = EV[2] - 2*mu_V*EV[1] + mu_V**2
    # mu_3(V)
    cm_V[3] = EV[3] - 3*mu_V*EV[2] + 3*mu_V**2*EV[1] - mu_V**3
    # mu_4(V)
    cm_V[4] = (EV[4] - 4*mu_V*EV[3] + 6*mu_V**2*EV[2]
               - 4*mu_V**3*EV[1] + mu_V**4)
    # mu_5(V)
    cm_V[5] = (EV[5] - 5*mu_V*EV[4] + 10*mu_V**2*EV[3]
               - 10*mu_V**3*EV[2] + 5*mu_V**4*EV[1] - mu_V**5)
    # mu_6(V)
    cm_V[6] = (EV[6] - 6*mu_V*EV[5] + 15*mu_V**2*EV[4]
               - 20*mu_V**3*EV[3] + 15*mu_V**4*EV[2]
               - 6*mu_V**5*EV[1] + mu_V**6)

    print("\n  中心モーメント mu_k(V) = E[(V-2)^k]:")
    cm_V_analytic = {2: 2, 3: 6, 4: 38, 5: 270, 6: 2342}
    for k in range(2, 7):
        print(f"    mu_{k}(V) = {cm_V[k]:.1f} (解析: {cm_V_analytic[k]})")

    # X - E[X] = -(V - 2) なので mu_k(X) = (-1)^k * mu_k(V)
    cm_X = {k: (-1)**k * cm_V[k] for k in range(2, 7)}
    sigma = math.sqrt(cm_X[2])
    sigma3 = sigma**3

    print(f"\n  X = log2(3) - V の中心モーメント:")
    for k in range(2, 7):
        print(f"    mu_{k}(X) = {cm_X[k]:.1f}")

    print(f"\n  sigma = sqrt(Var) = sqrt(2) = {sigma:.10f}")
    print(f"  sigma^3 = 2*sqrt(2) = {sigma3:.10f}")

    # キュムラント
    kappa = {}
    kappa[1] = MU
    kappa[2] = cm_X[2]   # = 2
    kappa[3] = cm_X[3]   # = -6
    kappa[4] = cm_X[4] - 3*cm_X[2]**2  # = 38 - 12 = 26
    kappa[5] = cm_X[5] - 10*cm_X[3]*cm_X[2]  # = -270 - 10*(-6)*2 = -270+120 = -150
    kappa[6] = (cm_X[6] - 15*cm_X[4]*cm_X[2]
                - 10*cm_X[3]**2 + 30*cm_X[2]**3)
    # = 2342 - 15*38*2 - 10*36 + 30*8 = 2342 - 1140 - 360 + 240 = 1082

    print(f"\n  キュムラント kappa_k:")
    kappa_analytic = {1: MU, 2: 2, 3: -6, 4: 26, 5: -150, 6: 1082}
    for k in range(1, 7):
        print(f"    kappa_{k} = {kappa[k]:.6f} (解析: {kappa_analytic[k]})")

    # 標準化キュムラント gamma_k = kappa_k / sigma^k
    gamma = {}
    for k in range(3, 7):
        gamma[k] = kappa[k] / sigma**k

    gamma3_exact = -3*math.sqrt(2)/2  # = -6/(2*sqrt(2))
    gamma4_exact = 13.0/2.0           # = 26/4

    print(f"\n  標準化キュムラント gamma_k = kappa_k/sigma^k:")
    print(f"    gamma_3 = {gamma[3]:.10f} = -3*sqrt(2)/2 = {gamma3_exact:.10f}")
    print(f"    gamma_4 = {gamma[4]:.10f} = 13/2 = {gamma4_exact:.10f}")
    print(f"    gamma_5 = {gamma[5]:.10f}")
    print(f"    gamma_6 = {gamma[6]:.10f}")

    # rho = E[|X - mu|^3] = E[|V - 2|^3]
    rho = sum(abs(j - 2)**3 * 2.0**(-j) for j in range(1, max_j + 1))
    # 解析: j=1 => 1*1/2, j=2 => 0, j>=3 => sum (j-2)^3 * 2^{-j}
    # = 1/2 + (1/4) * sum_{m>=1} m^3 * 2^{-m} = 1/2 + 26/4 = 7
    rho_analytic = 7.0

    print(f"\n  Berry-Esseen のrho:")
    print(f"    rho = E[|X-mu|^3] = {rho:.10f} (解析: {rho_analytic})")
    print(f"    rho/sigma^3 = 7/(2*sqrt(2)) = 7*sqrt(2)/4 = {rho/sigma3:.10f}")

    return {
        "kappa": kappa,
        "gamma": gamma,
        "sigma": sigma,
        "sigma3": sigma3,
        "rho": rho_analytic,
        "rho_over_sigma3": rho_analytic / sigma3,
        "cm_X": cm_X,
    }


# ============================================================
# Part 2: Hermite多項式*phi のsup (純粋Python)
# ============================================================

def hermite_phi_sup():
    """He_k(x)*phi(x) のsup を数値計算（numpy不要）"""
    print("\n" + "=" * 70)
    print("Part 2: Hermite多項式 * phi(x) のsup計算")
    print("=" * 70)

    # He_2(x) = x^2 - 1
    # He_3(x) = x^3 - 3x
    # He_5(x) = x^5 - 10x^3 + 15x

    N = 100000
    x_min, x_max = -10.0, 10.0
    dx = (x_max - x_min) / N

    sup_he2 = 0.0
    sup_he3 = 0.0
    sup_he5 = 0.0

    for i in range(N + 1):
        x = x_min + i * dx
        p = phi_std(x)
        he2 = (x**2 - 1) * p
        he3 = (x**3 - 3*x) * p
        he5 = (x**5 - 10*x**3 + 15*x) * p
        sup_he2 = max(sup_he2, abs(he2))
        sup_he3 = max(sup_he3, abs(he3))
        sup_he5 = max(sup_he5, abs(he5))

    # 解析的 sup|He_2*phi|: at x=0, |(0-1)*phi(0)| = 1/sqrt(2*pi)
    sup_he2_analytic = 1.0 / math.sqrt(2 * math.pi)

    print(f"  sup|He_2(x)*phi(x)| = {sup_he2:.10f} (解析: {sup_he2_analytic:.10f})")
    print(f"  sup|He_3(x)*phi(x)| = {sup_he3:.10f}")
    print(f"  sup|He_5(x)*phi(x)| = {sup_he5:.10f}")

    return {
        "sup_he2_phi": sup_he2,
        "sup_he3_phi": sup_he3,
        "sup_he5_phi": sup_he5,
    }


# ============================================================
# Part 3: Edgeworth展開係数の閉公式
# ============================================================

def edgeworth_coefficients(forms, sups):
    """Edgeworth展開の各次補正係数"""
    print("\n" + "=" * 70)
    print("Part 3: Edgeworth展開のKS上界係数 (閉公式)")
    print("=" * 70)

    gamma3 = forms["gamma"][3]
    gamma4 = forms["gamma"][4]

    # CDF補正の第1項:
    # Delta_1(x) = -(gamma_3/6) * He_2(x) * phi(x) / sqrt(k)
    # |Delta_1| <= |gamma_3|/6 * sup|He_2*phi| / sqrt(k)
    c1 = abs(gamma3) / 6.0 * sups["sup_he2_phi"]

    # 解析的: |gamma_3|/6 = (3*sqrt(2)/2)/6 = sqrt(2)/4
    # sup|He_2*phi| = 1/sqrt(2*pi)
    # c1 = sqrt(2)/(4*sqrt(2*pi)) = 1/(4*sqrt(pi)) = 1/(4*1.7725...) = 0.14105...
    c1_analytic = 1.0 / (4 * math.sqrt(math.pi))
    print(f"  第1項係数 c1:")
    print(f"    c1 = |gamma_3|/6 * sup|He_2*phi|")
    print(f"       = (3*sqrt(2)/2)/6 * 1/sqrt(2*pi)")
    print(f"       = sqrt(2)/(4*sqrt(2*pi))")
    print(f"       = 1/(4*sqrt(pi))")
    print(f"       = {c1:.10f} (解析: {c1_analytic:.10f})")

    # CDF補正の第2項:
    # Delta_2(x) = [gamma_4/24 * He_3(x) + gamma_3^2/72 * He_5(x)] * phi(x) / k
    # |Delta_2| <= [|gamma_4|/24 * sup|He_3*phi| + gamma_3^2/72 * sup|He_5*phi|] / k
    c2a = abs(gamma4) / 24.0 * sups["sup_he3_phi"]
    c2b = gamma3**2 / 72.0 * sups["sup_he5_phi"]
    c2 = c2a + c2b

    print(f"\n  第2項係数 c2 = c2a + c2b:")
    print(f"    c2a = |gamma_4|/24 * sup|He_3*phi| = (13/2)/24 * {sups['sup_he3_phi']:.8f}")
    print(f"         = {c2a:.10f}")
    print(f"    c2b = gamma_3^2/72 * sup|He_5*phi| = (9/2)/72 * {sups['sup_he5_phi']:.8f}")
    print(f"         = {c2b:.10f}")
    print(f"    c2  = {c2:.10f}")

    # KS予測: KS(k) ~ c1/sqrt(k) + c2/k
    print(f"\n  Edgeworth KS上界: KS(k) <= {c1:.6f}/sqrt(k) + {c2:.6f}/k + O(k^{{-3/2}})")
    print(f"\n  予測KS値:")
    for k in [1, 2, 3, 5, 10, 20, 50, 100]:
        ks_pred = c1 / math.sqrt(k) + c2 / k
        print(f"    k={k:3d}: KS_pred = {ks_pred:.6f}")

    return {
        "c1": c1,
        "c1_analytic": c1_analytic,
        "c1_exact_form": "1/(4*sqrt(pi))",
        "c2a": c2a,
        "c2b": c2b,
        "c2": c2,
    }


# ============================================================
# Part 4: 数値検証 (KS vs 理論)
# ============================================================

def numerical_ks_verification(forms, edge, N_samples=100000):
    """数値的にKSを計測して理論予測と比較"""
    print("\n" + "=" * 70)
    print("Part 4: KS統計量の数値検証")
    print("=" * 70)

    sigma = forms["sigma"]
    gamma3 = forms["gamma"][3]
    gamma4 = forms["gamma"][4]
    c1 = edge["c1"]
    c2 = edge["c2"]
    rho_s3 = forms["rho_over_sigma3"]

    def edgeworth_cdf(x, k):
        t0 = Phi_std(x)
        t1 = -(gamma3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi_std(x)
        t2a = (gamma4 / (24 * k)) * (x**3 - 3*x) * phi_std(x)
        t2b = (gamma3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi_std(x)
        return t0 + t1 + t2a + t2b

    results = []
    k_values = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100]

    for k in k_values:
        n_use = min(N_samples, max(30000, N_samples // max(1, k // 3)))
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

        ks_clt = 0.0
        ks_edge = 0.0
        for i, z in enumerate(standardized):
            ecdf = (i + 1) / n_z
            clt_val = Phi_std(z)
            edge_val = edgeworth_cdf(z, k)
            ks_clt = max(ks_clt, abs(ecdf - clt_val), abs(i/n_z - clt_val))
            ks_edge = max(ks_edge, abs(ecdf - edge_val), abs(i/n_z - edge_val))

        ks_pred = c1 / math.sqrt(k) + c2 / k
        c_be_eff = ks_clt * math.sqrt(k) / rho_s3

        results.append({
            "k": k,
            "n_samples": n_z,
            "ks_clt": ks_clt,
            "ks_edgeworth": ks_edge,
            "ks_pred": ks_pred,
            "ks_times_sqrt_k": ks_clt * math.sqrt(k),
            "c_be_effective": c_be_eff,
            "ratio_clt_to_pred": ks_clt / ks_pred if ks_pred > 0 else None,
            "improvement_edge": ks_clt / ks_edge if ks_edge > 0 else None,
        })
        print(f"  KS_clt={ks_clt:.6f}, KS_edge={ks_edge:.6f}, pred={ks_pred:.6f}, "
              f"C_BE={c_be_eff:.4f}")

    # Power law フィット (線形回帰 on log-log, 純粋Python)
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
        print(f"\n  Power law fit KS = A * k^alpha (k>=3):")
        print(f"    alpha = {alpha:.6f} (Berry-Esseen: -0.5)")
        print(f"    A = {A:.6f}")
    else:
        alpha = None
        A = None

    # C_BE のまとめ
    large_k = [r["c_be_effective"] for r in results if r["k"] >= 10]
    if large_k:
        print(f"\n  実効 C_BE (k>=10): mean={sum(large_k)/len(large_k):.6f}")
        print(f"  Shevtsova上界: 0.4748")

    return {
        "results": results,
        "power_law_alpha": alpha,
        "power_law_A": A,
        "c_be_mean_large_k": sum(large_k)/len(large_k) if large_k else None,
    }


# ============================================================
# Part 5: 局所べき指数の理論的説明
# ============================================================

def scaling_theory(edge):
    """KS ~ 0.28*k^{-0.514} の理論的根拠"""
    print("\n" + "=" * 70)
    print("Part 5: KS~0.28*k^{-0.514} の理論的根拠")
    print("=" * 70)

    c1 = edge["c1"]
    c2 = edge["c2"]

    print(f"  Edgeworth予測: KS(k) = {c1:.6f}/sqrt(k) + {c2:.6f}/k")
    print(f"  c2/c1 = {c2/c1:.6f}")

    # f(k) = c1/sqrt(k) + c2/k のpower lawフィット
    # 局所べき指数 d(ln f)/d(ln k)
    print(f"\n  局所べき指数 alpha_loc(k) = d(ln KS)/d(ln k):")
    for k in [2, 3, 5, 10, 20, 50, 100, 200]:
        dk = 0.001
        f_plus = c1 / math.sqrt(k + dk) + c2 / (k + dk)
        f_minus = c1 / math.sqrt(k - dk) + c2 / (k - dk)
        alpha_loc = (math.log(f_plus) - math.log(f_minus)) / (math.log(k+dk) - math.log(k-dk))
        print(f"    k={k:4d}: alpha_loc = {alpha_loc:.6f}")

    # 解析的な局所指数
    # f(k) = c1*k^{-1/2} + c2*k^{-1}
    # f'(k) = -(c1/2)*k^{-3/2} - c2*k^{-2}
    # alpha_loc = k*f'(k)/f(k)
    # = k * [-(c1/2)*k^{-3/2} - c2*k^{-2}] / [c1*k^{-1/2} + c2*k^{-1}]
    # = [-(c1/2)*k^{-1/2} - c2*k^{-1}] / [c1*k^{-1/2} + c2*k^{-1}]
    # let r = c2/(c1*sqrt(k)):
    # = [-(1/2) - r] / [1 + r]
    # = -(1/2 + r)/(1 + r)
    # as k -> inf: r -> 0, alpha -> -1/2
    # for finite k: if r > 0, alpha < -1/2 (steeper)

    print(f"\n  解析的な局所指数:")
    print(f"    alpha_loc = -(1/2 + r)/(1 + r) where r = c2/(c1*sqrt(k))")
    for k in [3, 5, 10, 20, 50, 100]:
        r = c2 / (c1 * math.sqrt(k))
        alpha_analytic = -(0.5 + r) / (1 + r)
        print(f"    k={k:4d}: r={r:.6f}, alpha={alpha_analytic:.6f}")

    # 0.28 * k^{-0.514} と比較
    print(f"\n  0.28*k^{{-0.514}} vs Edgeworth:")
    print(f"  {'k':>5} {'empirical':>12} {'Edgeworth':>12} {'ratio':>10}")
    for k in [2, 3, 5, 10, 20, 50, 100]:
        emp = 0.28 * k**(-0.514)
        edg = c1 / math.sqrt(k) + c2 / k
        print(f"  {k:5d} {emp:12.6f} {edg:12.6f} {emp/edg:10.4f}")

    # 有効 power law フィット (k=3..50 でのEdgeworth)
    log_pairs = []
    for k in range(3, 51):
        f = c1 / math.sqrt(k) + c2 / k
        log_pairs.append((math.log(k), math.log(f)))

    n_p = len(log_pairs)
    sx = sum(x for x, y in log_pairs)
    sy = sum(y for x, y in log_pairs)
    sxx = sum(x**2 for x, y in log_pairs)
    sxy = sum(x*y for x, y in log_pairs)
    alpha_fit = (n_p * sxy - sx * sy) / (n_p * sxx - sx**2)
    A_fit = math.exp((sy - alpha_fit * sx) / n_p)
    print(f"\n  Edgeworth予測の power law fit (k=3..50):")
    print(f"    alpha = {alpha_fit:.6f}")
    print(f"    A = {A_fit:.6f}")

    return {
        "c1": c1,
        "c2": c2,
        "c2_over_c1": c2 / c1,
        "effective_alpha_3_50": alpha_fit,
        "effective_A_3_50": A_fit,
    }


# ============================================================
# Part 6: Edgeworth CDF実関数との点別比較
# ============================================================

def edgeworth_pointwise_test(forms, edge, N_samples=80000):
    """特定のkでのEdgeworth近似の精度を点別に検証"""
    print("\n" + "=" * 70)
    print("Part 6: Edgeworth近似の点別精密テスト")
    print("=" * 70)

    sigma = forms["sigma"]
    gamma3 = forms["gamma"][3]
    gamma4 = forms["gamma"][4]

    def edgeworth_cdf(x, k):
        t0 = Phi_std(x)
        t1 = -(gamma3 / (6 * math.sqrt(k))) * (x**2 - 1) * phi_std(x)
        t2a = (gamma4 / (24 * k)) * (x**3 - 3*x) * phi_std(x)
        t2b = (gamma3**2 / (72 * k)) * (x**5 - 10*x**3 + 15*x) * phi_std(x)
        return t0 + t1 + t2a + t2b

    results = {}
    for k in [5, 10, 20]:
        print(f"\n  k={k}:")
        sums = []
        for _ in range(N_samples):
            n = random.randint(10**9, 10**10)
            if n % 2 == 0:
                n += 1
            s = 0.0
            for step in range(k):
                tn = syracuse(n)
                s += math.log2(tn / n)
                n = tn
            sums.append(s)

        mu_k = k * MU
        sigma_k = sigma * math.sqrt(k)
        standardized = sorted([(s - mu_k) / sigma_k for s in sums])
        n_z = len(standardized)

        max_pos_clt = (-1e10, 0)
        max_neg_clt = (1e10, 0)
        max_pos_edge = (-1e10, 0)
        max_neg_edge = (1e10, 0)

        for i, z in enumerate(standardized):
            ecdf = (i + 1) / n_z
            err_clt = ecdf - Phi_std(z)
            err_edge = ecdf - edgeworth_cdf(z, k)

            if err_clt > max_pos_clt[0]:
                max_pos_clt = (err_clt, z)
            if err_clt < max_neg_clt[0]:
                max_neg_clt = (err_clt, z)
            if err_edge > max_pos_edge[0]:
                max_pos_edge = (err_edge, z)
            if err_edge < max_neg_edge[0]:
                max_neg_edge = (err_edge, z)

        ks_clt = max(abs(max_pos_clt[0]), abs(max_neg_clt[0]))
        ks_edge = max(abs(max_pos_edge[0]), abs(max_neg_edge[0]))

        print(f"    CLT: max+={max_pos_clt[0]:.6f} at z={max_pos_clt[1]:.3f}, "
              f"max-={max_neg_clt[0]:.6f} at z={max_neg_clt[1]:.3f}")
        print(f"    Edge: max+={max_pos_edge[0]:.6f} at z={max_pos_edge[1]:.3f}, "
              f"max-={max_neg_edge[0]:.6f} at z={max_neg_edge[1]:.3f}")
        print(f"    KS_clt={ks_clt:.6f}, KS_edge={ks_edge:.6f}, improvement={ks_clt/ks_edge:.2f}x")

        # Edgeworth第1項の予測:
        # 誤差最大位置は He_2(x)*phi(x) が最大のところ、つまり x=0
        # gamma_3 < 0 なので -(gamma_3/6)/sqrt(k) * (-1)*phi(0) > 0
        # => 正の誤差が x=0 近辺で発生
        term1_at_0 = -(gamma3 / (6 * math.sqrt(k))) * (-1) * phi_std(0)
        print(f"    理論: Edgeworth第1項 at x=0 = {term1_at_0:.6f}")

        results[k] = {
            "ks_clt": ks_clt,
            "ks_edge": ks_edge,
            "improvement": ks_clt / ks_edge if ks_edge > 0 else None,
            "max_clt_error_position": max_pos_clt[1],
            "edgeworth_term1_at_0": term1_at_0,
        }

    return results


# ============================================================
# Part 7: rho=7 の解析的導出の完全な証明
# ============================================================

def rho_analytical_proof():
    """rho = E[|V-2|^3] = 7 の完全な証明"""
    print("\n" + "=" * 70)
    print("Part 7: rho = 7 の完全な解析的証明")
    print("=" * 70)

    print("""
  rho = E[|V-2|^3] where V ~ Geom(1/2), P(V=j) = 2^{-j}

  = sum_{j=1}^{inf} |j-2|^3 * 2^{-j}

  = |1-2|^3 * 2^{-1} + |2-2|^3 * 2^{-2} + sum_{j=3}^{inf} (j-2)^3 * 2^{-j}

  = 1 * (1/2) + 0 * (1/4) + sum_{m=1}^{inf} m^3 * 2^{-(m+2)}
                              [substitution m = j-2]

  = 1/2 + (1/4) * sum_{m=1}^{inf} m^3 * 2^{-m}

  Now, sum_{m=1}^{inf} m^3 * x^m = x(1+4x+x^2)/(1-x)^4 for |x|<1

  At x=1/2:
    (1/2)(1 + 2 + 1/4) / (1/2)^4
    = (1/2)(13/4) / (1/16)
    = (13/8) * 16
    = 26

  Therefore:
    rho = 1/2 + 26/4 = 1/2 + 13/2 = 14/2 = 7

  Also: sigma^3 = (sqrt(2))^3 = 2*sqrt(2)

  Berry-Esseen ratio:
    rho/sigma^3 = 7/(2*sqrt(2)) = 7*sqrt(2)/4
""")

    # 数値確認
    rho_num = sum(abs(j-2)**3 * 2.0**(-j) for j in range(1, 300))
    print(f"  数値確認: rho = {rho_num:.15f}")
    print(f"  解析値:   rho = 7.0")
    print(f"  差: {abs(rho_num - 7.0):.15e}")

    return {"rho": 7.0, "rho_over_sigma3": 7.0 / (2*math.sqrt(2))}


# ============================================================
# メイン
# ============================================================

def main():
    start = time.time()
    all_results = {}

    print("Berry-Esseen精密定数の導出")
    print("X = log2(3) - Geom(1/2): 完全離散増分からの閉公式")
    print()

    # Part 7: rho の証明
    p7 = rho_analytical_proof()
    all_results["rho_proof"] = p7

    # Part 1: 閉公式
    p1 = exact_closed_forms()
    all_results["exact_forms"] = {k: v for k, v in p1.items()
                                   if k not in ("kappa", "gamma", "cm_X")}
    all_results["exact_forms"]["kappa"] = {str(k): v for k, v in p1["kappa"].items()}
    all_results["exact_forms"]["gamma"] = {str(k): v for k, v in p1["gamma"].items()}

    # Part 2: Hermite sup
    p2 = hermite_phi_sup()
    all_results["hermite_sups"] = p2

    # Part 3: Edgeworth係数
    p3 = edgeworth_coefficients(p1, p2)
    all_results["edgeworth_coefficients"] = p3

    # Part 5: スケーリング理論
    p5 = scaling_theory(p3)
    all_results["scaling_theory"] = p5

    # Part 4: 数値検証
    p4 = numerical_ks_verification(p1, p3, N_samples=80000)
    all_results["numerical_verification"] = p4

    # Part 6: 点別テスト
    p6 = edgeworth_pointwise_test(p1, p3, N_samples=60000)
    all_results["pointwise_test"] = {str(k): v for k, v in p6.items()}

    elapsed = time.time() - start

    # 総括
    summary = {
        "closed_form_parameters": {
            "E[X]": f"log2(3) - 2 = {MU}",
            "Var[X]": "2 (exact: Var[Geom(1/2)] = 2)",
            "sigma": "sqrt(2)",
            "sigma_cubed": "2*sqrt(2)",
            "kappa_3": "-6",
            "kappa_4": "26",
            "kappa_5": "-150",
            "kappa_6": "1082",
            "gamma_3_skewness": "-3*sqrt(2)/2 = -2.12132...",
            "gamma_4_excess_kurtosis": "13/2 = 6.5",
            "rho_E_absX3": "7 (exact)",
            "rho_over_sigma3": "7*sqrt(2)/4 = 2.47487...",
        },
        "edgeworth_expansion": {
            "term1_coeff": f"c1 = 1/(4*sqrt(pi)) = {p3['c1']:.10f}",
            "term2_coeff": f"c2 = {p3['c2']:.10f}",
            "KS_formula": f"KS(k) ~ {p3['c1']:.6f}/sqrt(k) + {p3['c2']:.6f}/k",
        },
        "berry_esseen": {
            "BE_bound": f"sup|F_k-Phi| <= C * {p1['rho_over_sigma3']:.6f} / sqrt(k)",
            "effective_C_BE": p4.get("c_be_mean_large_k"),
            "Shevtsova_upper_bound": 0.4748,
        },
        "scaling_explanation": {
            "observed_pattern": "KS ~ 0.28 * k^{-0.514}",
            "theoretical_alpha_local": (
                "alpha_loc = -(1/2 + r)/(1+r) where r = c2/(c1*sqrt(k)), "
                f"effective alpha(k=3..50) = {p5['effective_alpha_3_50']:.4f}"
            ),
            "explanation": (
                "Edgeworth展開の第2項(1/k)が正のため、有限kでの有効指数は "
                "-0.5より急 (more negative)。k -> infでは -0.5 に収束。"
            ),
        },
        "elapsed_seconds": elapsed,
    }
    all_results["summary"] = summary

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
    def make_ser(obj):
        if isinstance(obj, dict):
            return {str(k): make_ser(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_ser(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return str(obj)
            return round(obj, 12)
        return obj

    with open("/Users/soyukke/study/lean-unsolved/results/berry_esseen_precise.json", "w") as f:
        json.dump(make_ser(all_results), f, indent=2)
    print("\n結果を results/berry_esseen_precise.json に保存")

if __name__ == "__main__":
    main()
