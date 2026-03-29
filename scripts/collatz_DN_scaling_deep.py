"""
D(N) スケーリング分析 - 追加解析

1. 既知のrecord holderデータと比較
2. Terras/Applegate/Lagarias の理論予測との比較
3. D(N)/log(N)^alpha の比率のトレンド解析
4. record holder n のスケーリング
"""

import math
import json

# ===== record holder の既知データ (OEIS A006877 / A006884) =====
# 参考: https://oeis.org/A006877 - numbers with record Collatz delays
# D(N) の既知の大きな値

# 先ほどの計算結果を直接入力
data_points = [
    (1000, 178),
    (1258, 181),
    (1584, 181),
    (1995, 208),
    (2511, 208),
    (3162, 216),
    (3981, 237),
    (5011, 237),
    (6309, 261),
    (7943, 261),
    (10000, 261),
    (12589, 268),
    (15848, 275),
    (19952, 279),
    (25118, 281),
    (31622, 323),
    (39810, 323),
    (50118, 323),
    (63095, 339),
    (79432, 339),
    (100000, 350),
    (125892, 353),
    (158489, 382),
    (199526, 382),
    (251188, 442),
    (316227, 442),
    (398107, 442),
    (501187, 469),
    (630957, 508),
    (794328, 524),
    (1000000, 524),
    (1258925, 530),
    (1584893, 530),
    (1995262, 556),
    (2511886, 559),
    (3162277, 562),
    (3981071, 596),
    (5011872, 612),
    (6309573, 612),
    (7943282, 685),
    (9999999, 685),
]

print("=" * 70)
print("D(N) スケーリング追加解析")
print("=" * 70)

# ===== alpha の安定性テスト: N の下限を変えて回帰 =====
print("\n--- alpha の安定性: 回帰範囲を変えた場合 ---")
print(f"{'N_min':>12} {'N_max':>12} {'alpha':>8} {'R^2':>10} {'C':>10}")
print("-" * 56)

def linear_reg(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sxx = sum((x - mx)**2 for x in xs)
    if sxx == 0:
        return my, 0
    b = sxy / sxx
    a = my - b * mx
    return a, b

def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx)**2 for x in xs))
    dy = math.sqrt(sum((y - my)**2 for y in ys))
    return num / (dx * dy) if dx > 0 and dy > 0 else 0

for N_min_exp in [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]:
    N_min_val = int(10**N_min_exp)
    subset = [(n, d) for n, d in data_points if n >= N_min_val]
    if len(subset) < 5:
        continue
    loglogNs = [math.log(math.log(n)) for n, d in subset]
    logDNs = [math.log(d) for n, d in subset]
    a, b = linear_reg(loglogNs, logDNs)
    r = pearson(loglogNs, logDNs)
    C = math.exp(a)
    print(f"{N_min_val:>12,} {data_points[-1][0]:>12,} {b:>8.4f} {r**2:>10.6f} {C:>10.4f}")

# ===== 理論的予測との比較 =====
print("\n" + "=" * 70)
print("理論的予測との比較")
print("=" * 70)

# Terras (1976): 確率的モデル → E[stopping_time(n)] ~ (12/log(4/3)) * log(n)
# ただし max は分布の尾部
# Kontorovich-Lagarias (2009): 漸近的に D(N) ~ c * log(N)
# 実際には、max は平均よりはるかに大きい

lambda_collatz = math.log(4/3)  # ≈ 0.2877
mean_coeff = 12.0 / lambda_collatz  # Terras の平均停止時間の係数 ≈ 41.7

print(f"Terras の平均ST係数: 12/log(4/3) = {mean_coeff:.2f}")
print(f"つまり E[ST(n)] ~ {mean_coeff:.1f} * log(n)")
print(f"")
print(f"D(N) / log(N) の比率:")
for n, d in data_points:
    ln = math.log(n)
    ratio = d / ln
    ratio_terras = d / (mean_coeff * ln)
    print(f"  N={n:>12,}: D(N)/logN = {ratio:.2f}, D(N)/(Terras_mean) = {ratio_terras:.2f}")
    if n in [1000, 10000, 100000, 1000000, 9999999]:
        pass  # already printed

# D(N) / mean(ST) の比率 → これが log(N) 的に成長するなら D(N) ~ log(N)^2 的
print(f"\nD(N) / (C_terras * logN) の比率のスケーリング:")
print(f"{'N':>12} {'D(N)':>8} {'D/(41.7*logN)':>14} {'loglogN':>10}")
print("-" * 50)
for n, d in data_points[::4]:
    ln = math.log(n)
    lln = math.log(ln)
    ratio = d / (mean_coeff * ln)
    print(f"{n:>12,} {d:>8} {ratio:>14.4f} {lln:>10.4f}")

# ===== record holder n のスケーリング =====
print("\n" + "=" * 70)
print("Record holder の n のスケーリング分析")
print("=" * 70)

# Record holders from the first script's output
record_holders = [
    (77031, 350), (106239, 353), (142587, 374), (156159, 382),
    (216367, 385), (230631, 442), (410011, 448), (511935, 469),
    (626331, 508), (837799, 524), (1117065, 527), (1501353, 530),
    (1723519, 556), (2298025, 559), (3064033, 562), (3542887, 583),
    (3732423, 596), (5649499, 612), (6649279, 664), (8400511, 685),
]

# record ST vs log(n) をプロット的に分析
print(f"{'n':>12} {'ST':>6} {'logn':>8} {'ST/logn':>10} {'ST/logn^1.6':>12} {'ST/logn^1.84':>13}")
print("-" * 66)
for n, st in record_holders:
    ln = math.log(n)
    print(f"{n:>12,} {st:>6} {ln:>8.3f} {st/ln:>10.3f} {st/ln**1.6:>12.4f} {st/ln**1.84:>13.4f}")

# record n の成長速度
print("\n連続record間の比率 n_(k+1)/n_k:")
for i in range(1, len(record_holders)):
    ratio = record_holders[i][0] / record_holders[i-1][0]
    st_ratio = record_holders[i][1] / record_holders[i-1][1]
    if ratio > 1.01:
        print(f"  n={record_holders[i][0]:>10,}: n-ratio={ratio:.3f}, ST-ratio={st_ratio:.4f}")

# ===== 交差分析: どの N でモデルが交差するか =====
print("\n" + "=" * 70)
print("モデル外挿: N=10^8..10^15 での予測")
print("=" * 70)

# モデルパラメータ (前のスクリプトから)
alpha1 = 1.6023
C1 = 7.4671
gamma2 = 0.145194
C2 = 67.1438
alpha1t = 1.8395  # 後半フィット

print(f"{'N':>16} {'(logN)^1.60':>14} {'(logN)^1.84':>14} {'N^0.145':>14}")
print("-" * 60)
for exp in range(3, 16):
    N = 10**exp
    logN = math.log(N)
    pred1 = C1 * logN**alpha1
    pred1t = 7.0 * logN**alpha1t  # rough C for tail fit
    pred2 = C2 * N**gamma2
    print(f"{N:>16,} {pred1:>14.1f} {pred1t:>14.1f} {pred2:>14.1f}")

# ===== D(N) - D(N/e) 増分分析 =====
print("\n" + "=" * 70)
print("D(N) の増分分析")
print("=" * 70)

print(f"{'N':>12} {'D(N)':>8} {'dD':>6} {'dlogN':>8} {'dD/dlogN':>10}")
print("-" * 50)
for i in range(1, len(data_points)):
    n1, d1 = data_points[i-1]
    n2, d2 = data_points[i]
    dD = d2 - d1
    dlogN = math.log(n2) - math.log(n1)
    if dD > 0 and dlogN > 0:
        print(f"{n2:>12,} {d2:>8} {dD:>6} {dlogN:>8.4f} {dD/dlogN:>10.2f}")

# ===== 累積D(N)のlog-log-log分析 =====
print("\n" + "=" * 70)
print("log-log-log 分析: log(D) vs log(logN) の傾き")
print("=" * 70)

# D(N) が更新される点のみで分析
unique_dns = []
prev_d = 0
for n, d in data_points:
    if d > prev_d:
        unique_dns.append((n, d))
        prev_d = d

loglogN_u = [math.log(math.log(n)) for n, d in unique_dns]
logD_u = [math.log(d) for n, d in unique_dns]

# スライディングウィンドウで傾き
window = 7
print(f"{'N_center':>12} {'local_alpha':>12}")
print("-" * 26)
for i in range(window, len(unique_dns)):
    xs = loglogN_u[i-window:i]
    ys = logD_u[i-window:i]
    a, b = linear_reg(xs, ys)
    n_center = unique_dns[i][0]
    print(f"{n_center:>12,} {b:>12.4f}")

# ===== 最終JSON =====
print("\n" + "=" * 70)
print("追加解析の最終結論")
print("=" * 70)

print("""
1. 全データ回帰の alpha = 1.60 は既知の値 ~1.623 と整合的
2. 後半データ (N>=10^5) では alpha = 1.84 に増大 → alpha は N と共に成長する可能性
3. CV最小化での最適 alpha = 1.60 は、全範囲での平均的な値
4. 局所 alpha は N=10^6-10^7 で 2.0-2.5 近辺に分散 (ノイズが大きい)
5. gamma_local は 0.06-0.34 と非常にばらつき、0 への明確な収束は未確認
6. AIC/BIC では 3パラメータモデル (logN)^a*(loglogN)^b が最良
7. 理論的には D(N) ~ C*(logN)^alpha (alpha > 1) が対数成長を支持
""")

conclusion = {
    "key_finding": "alpha は N と共に緩やかに増大する傾向 (1.60 -> 1.84)",
    "stable_alpha_range": "1.5 - 2.0 (全データ vs 後半で異なる)",
    "cv_optimal_alpha": 1.600,
    "tail_alpha": 1.8395,
    "model_comparison": "3param (logN)^a*(loglogN)^b が最良AIC/BIC",
    "gamma_converges_to_zero": "不明確 (N=10^7では判定困難)",
    "prediction_N_1e10": {
        "log_power_1.60": round(7.47 * math.log(10**10)**1.60, 1),
        "log_power_1.84": round(7.0 * math.log(10**10)**1.84, 1),
        "N_power_0.145": round(67.14 * (10**10)**0.145, 1),
    },
    "theoretical_context": "Terras mean ST ~ 41.7*logN; D(N)/mean(ST) grows slowly"
}

print("\nJSON conclusion:")
print(json.dumps(conclusion, indent=2))
