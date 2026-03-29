#!/usr/bin/env python3
"""
尾部指数の精密解析:

理論: I(0) = 0.05498 だが、RWシミュレーションの尾部指数がこの値に収束しない。
原因: first passage time の尾部は P(tau>k) ~ C(c) * exp(-I(0)*k) で
c (= log初期値) に依存し、有限cでは前指数因子が重要。

ここではcを大きくした時の収束を確認する。
"""

import math
import random

L2 = math.log(2)
L3 = math.log(3)
I0 = 0.054979472811  # Cramer I(0)

def rw_first_passage(c, n_sim=100000):
    """RWモデルで first passage time を n_sim 回シミュレーション"""
    fpt_list = []
    for _ in range(n_sim):
        s = c
        k = 0
        while s > 0 and k < 100000:
            v = 1
            while random.random() < 0.5:
                v += 1
            s += L3 - v * L2
            k += 1
        fpt_list.append(k)
    return fpt_list

print("=" * 70)
print("尾部指数の c 依存性と I(0) への収束")
print("=" * 70)

random.seed(42)

# 異なるc（= ln(n)に対応）で尾部指数を測定
c_values = [5, 10, 20, 50, 100, 200]

print(f"\n{'c':>6s}  {'E[tau]':>10s}  {'理論E':>10s}  {'尾部指数':>10s}  {'I(0)':>10s}  {'比率':>8s}")

for c in c_values:
    n_sim = max(50000, int(200000 / (c/10)))
    fpt = rw_first_passage(c, n_sim=n_sim)
    mean_fpt = sum(fpt) / len(fpt)
    theory_mean = c / abs(L3 - 2*L2)

    # 尾部指数: P(tau > t) の指数部分を推定
    # t > E[tau] の範囲で線形回帰
    max_t = max(fpt)
    t_start = int(mean_fpt * 1.5)
    t_end = int(mean_fpt * 4)
    fit_data = []
    for t in range(t_start, min(t_end, max_t), max(1, (t_end-t_start)//50)):
        count = sum(1 for f in fpt if f > t)
        if count >= 20:
            fit_data.append((t, math.log(count / len(fpt))))

    if len(fit_data) >= 5:
        n_f = len(fit_data)
        sx = sum(d[0] for d in fit_data)
        sy = sum(d[1] for d in fit_data)
        sxx = sum(d[0]**2 for d in fit_data)
        sxy = sum(d[0]*d[1] for d in fit_data)
        denom = n_f * sxx - sx**2
        slope = (n_f * sxy - sx * sy) / denom
        lambda_est = -slope
        ratio = lambda_est / I0
        print(f"{c:6.0f}  {mean_fpt:10.2f}  {theory_mean:10.2f}  {lambda_est:10.6f}  {I0:10.6f}  {ratio:8.4f}")
    else:
        print(f"{c:6.0f}  {mean_fpt:10.2f}  {theory_mean:10.2f}  データ不足")


# ============================================================
# 実Syracuse first drop time との比較
# ============================================================
print("\n" + "=" * 70)
print("実Syracuse FDT の尾部指数のビット数別推定")
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
    current = n
    steps = 0
    while current >= original:
        if current == 1 and n != 1:
            return steps
        current, _ = syracuse(current)
        steps += 1
        if steps > 50000:
            return -1
    return steps

# bits別にFDTの尾部を測定
for target_bits in [14, 16, 18, 20]:
    n_start = 2**(target_bits-1) + 1
    n_end = 2**target_bits - 1
    fdt_list = []
    for n in range(n_start, n_end + 1, 2):
        f = first_drop_time(n)
        if f >= 0:
            fdt_list.append(f)

    if not fdt_list:
        continue

    total = len(fdt_list)
    mean_fdt = sum(fdt_list) / total
    max_fdt = max(fdt_list)

    # 尾部回帰
    t_start = max(5, int(mean_fdt * 2))
    fit_data = []
    for t in range(t_start, min(max_fdt, 200)):
        count = sum(1 for f in fdt_list if f > t)
        if count >= 10:
            fit_data.append((t, math.log(count/total)))

    if len(fit_data) >= 5:
        n_f = len(fit_data)
        sx = sum(d[0] for d in fit_data)
        sy = sum(d[1] for d in fit_data)
        sxx = sum(d[0]**2 for d in fit_data)
        sxy = sum(d[0]*d[1] for d in fit_data)
        denom = n_f * sxx - sx**2
        slope = (n_f * sxy - sx * sy) / denom
        lambda_est = -slope

        print(f"\n  bits={target_bits} (n: {n_start}~{n_end})")
        print(f"    サンプル数: {total}")
        print(f"    E[FDT] = {mean_fdt:.3f}")
        print(f"    max FDT = {max_fdt}")
        print(f"    尾部指数 lambda = {lambda_est:.6f}")
        print(f"    I(0) = {I0:.6f}")
        print(f"    lambda/I(0) = {lambda_est/I0:.4f}")


# ============================================================
# 理論的考察: Overshoot 効果
# ============================================================
print("\n" + "=" * 70)
print("理論的考察: Overshoot効果")
print("=" * 70)

print("""
First passage time tau_c = min{k: S_k < -c} の尾部:

Cramérの定理より:
  P(S_k >= 0) ~ exp(-k * I(0)) for k >> 1

しかし P(tau_c > k) は P(min_{j<=k} S_j > -c) であり、
tau_c > k は全ての j <= k で S_j > -c を要求する。

正確な漸近:
  P(tau_c > k) ~ C(c) * exp(-I(0) * k)  as k → ∞

ここで C(c) は c に依存する前指数因子で、
  C(c) ~ exp(-theta^* * c) * (定数)
where theta^* は Lambda(theta*)=0 の正根 (ここでは theta*=1)。

つまり:
  P(tau_c > k) ~ A * exp(-c) * exp(-I(0)*k)

I(0) 自体は c に依存しないが、前指数因子が exp(-c) なので
有限サンプルでは尾部の観測が困難。

重要: theta* = 1 (Lambda(1)=0) は以下を意味する:
  E[e^X] = 1 (X = ln(T(n)/n))
  つまり E[T(n)/n] = 1

これは Kac の巡回定理やエルゴード理論の文脈で
コラッツ予想の確率論的議論の核心部分。
""")

# Lambda(theta) = 0 の theta=1 について
# P(S_k >= 0 for all k) = 0 (since E[X]<0, S_k → -inf a.s.)
# しかし renewal theory により:
# P(max_k S_k >= c) ~ exp(-theta* * c) for c → inf
# ここで theta* は Lambda(theta*)=0 の正根、つまり theta*=1

# よって:
# P(max_k S_k >= c) ~ exp(-c) = 1/e^c

print("Renewal理論による結果:")
print(f"  P(max_k S_k >= c) ~ exp(-theta* * c) = exp(-c)")
print(f"  theta* = 1 (Lambda(1) = 0)")
print(f"  これは: P(軌道が高さ c 以上に到達) ~ exp(-c)")
print(f"  ln ベースなので: P(T^k(n) >= e^c * n for some k) ~ exp(-c)")
print(f"  つまり: P(max_k T^k(n) >= M*n) ~ 1/M")

# 数値検証
print(f"\n数値検証: P(max trajectory / n >= M)")
random.seed(42)
for n_bits in [16, 18, 20]:
    n_start = 2**(n_bits-1) + 1
    n_end = min(2**n_bits - 1, n_start + 100000)

    max_ratios = []
    for n in range(n_start, n_end + 1, 2):
        current = n
        max_val = n
        for _ in range(1000):
            if current == 1:
                break
            current, _ = syracuse(current)
            if current > max_val:
                max_val = current
        max_ratios.append(math.log(max_val / n))

    total = len(max_ratios)
    print(f"\n  bits={n_bits}: ", end="")
    for c_ln in [1, 2, 3, 5, 8]:
        count = sum(1 for r in max_ratios if r >= c_ln)
        p_obs = count / total
        p_theory = math.exp(-c_ln)
        ratio = p_obs / p_theory if p_theory > 0 else 0
        print(f"P(ln(max/n)>={c_ln})={p_obs:.4f}(th:{p_theory:.4f},r:{ratio:.2f}) ", end="")
    print()
