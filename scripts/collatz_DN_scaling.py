"""
D(N) = max_{n <= N} stopping_time(n) のスケーリング則分析
純Python版 (numpy/scipy不要)

目標:
  - N = 10^3 .. 10^7 で D(N) を計算
  - D(N) ~ C * (log N)^alpha 型 vs D(N) ~ C * N^gamma 型 のフィッティング
  - 最良の alpha を特定
  - 既知: ST尾部指数 0.0735, max(ST) ~ (log N)^1.623
"""

import math
import time
import json

# ===== コラッツ停止時間 =====
def stopping_time(n):
    """コラッツ停止時間: n が 1 に到達するまでのステップ数"""
    count = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        count += 1
    return count

# ===== 統計ヘルパー =====
def mean(xs):
    return sum(xs) / len(xs)

def std(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m)**2 for x in xs) / len(xs))

def pearson_r(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx)**2 for x in xs))
    dy = math.sqrt(sum((y - my)**2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)

def linear_regression(xs, ys):
    """y = a + b*x の最小二乗フィット。(a, b) を返す"""
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sxx = sum((x - mx)**2 for x in xs)
    if sxx == 0:
        return my, 0.0
    b = sxy / sxx
    a = my - b * mx
    return a, b

def rmse(xs, ys, a, b):
    """y = a + b*x の残差RMSE"""
    n = len(xs)
    return math.sqrt(sum((ys[i] - (a + b * xs[i]))**2 for i in range(n)) / n)

# ===== D(N) の計算 =====
def compute_DN(N_max, checkpoints):
    """D(N) を漸進的に計算"""
    results = {}
    current_max_st = 0
    cp_set = set(checkpoints)

    for n in range(1, N_max + 1):
        st = stopping_time(n)
        if st > current_max_st:
            current_max_st = st
        if n in cp_set:
            results[n] = current_max_st

    return results

# ===== メイン =====
print("=" * 70)
print("D(N) = max_{n <= N} stopping_time(n) のスケーリング則分析")
print("=" * 70)

# チェックポイント生成
N_values = []
exp = 3.0
while exp <= 7.01:
    N_values.append(int(10**exp))
    exp += 0.1
N_values = sorted(set(N_values))
N_max = max(N_values)

print(f"\nN_max = {N_max:,}")
print(f"チェックポイント数: {len(N_values)}")
print(f"計算開始...")

t0 = time.time()
DN_dict = compute_DN(N_max, N_values)
t1 = time.time()
print(f"計算完了: {t1 - t0:.1f}秒")

# 結果テーブル化
Ns = sorted(DN_dict.keys())
DNs = [DN_dict[n] for n in Ns]
logNs = [math.log(n) for n in Ns]
logDNs = [math.log(d) for d in DNs]
loglogNs = [math.log(ln) for ln in logNs]

print(f"\n{'N':>12} {'D(N)':>8} {'logN':>8} {'D/logN':>10} {'D/(logN)^2':>14}")
print("-" * 60)
step = max(1, len(Ns) // 15)
for i in range(0, len(Ns), step):
    n = Ns[i]
    d = DNs[i]
    ln = logNs[i]
    print(f"{n:>12,} {d:>8} {ln:>8.2f} {d/ln:>10.2f} {d/ln**2:>14.4f}")

# ===== モデル1: D(N) = C * (log N)^alpha =====
# log D = log C + alpha * log(log N)
print("\n" + "=" * 70)
print("モデル1: D(N) = C * (logN)^alpha")
print("=" * 70)

a1, b1 = linear_regression(loglogNs, logDNs)
alpha1 = b1
C1 = math.exp(a1)
r1 = pearson_r(loglogNs, logDNs)
rmse1 = rmse(loglogNs, logDNs, a1, b1)

print(f"alpha = {alpha1:.4f}")
print(f"C = {C1:.4f}")
print(f"R^2 = {r1**2:.6f}")
print(f"RMSE(log) = {rmse1:.6f}")

# ===== モデル2: D(N) = C * N^gamma =====
# log D = log C + gamma * log N
print("\n" + "=" * 70)
print("モデル2: D(N) = C * N^gamma")
print("=" * 70)

a2, b2 = linear_regression(logNs, logDNs)
gamma2 = b2
C2 = math.exp(a2)
r2 = pearson_r(logNs, logDNs)
rmse2 = rmse(logNs, logDNs, a2, b2)

print(f"gamma = {gamma2:.6f}")
print(f"C = {C2:.4f}")
print(f"R^2 = {r2**2:.6f}")
print(f"RMSE(log) = {rmse2:.6f}")

# ===== モデル3: 多重回帰 log D = a + b*log(logN) + c*log(log(logN)) =====
print("\n" + "=" * 70)
print("モデル3: D(N) = C * (logN)^alpha * (loglogN)^beta")
print("=" * 70)

# 手動2変数回帰
logloglogNs = [math.log(x) for x in loglogNs]
# log D = a + b * loglogN + c * logloglogN
# 正規方程式を解く
n = len(Ns)
x1 = loglogNs
x2 = logloglogNs
y = logDNs

sx1 = sum(x1)
sx2 = sum(x2)
sy = sum(y)
sx1x1 = sum(a*a for a in x1)
sx2x2 = sum(a*a for a in x2)
sx1x2 = sum(x1[i]*x2[i] for i in range(n))
sx1y = sum(x1[i]*y[i] for i in range(n))
sx2y = sum(x2[i]*y[i] for i in range(n))

# 正規方程式: [[n, sx1, sx2], [sx1, sx1x1, sx1x2], [sx2, sx1x2, sx2x2]] * [a,b,c] = [sy, sx1y, sx2y]
# ガウス消去法
A = [[n, sx1, sx2, sy],
     [sx1, sx1x1, sx1x2, sx1y],
     [sx2, sx1x2, sx2x2, sx2y]]

for col in range(3):
    # ピボット選択
    max_row = col
    for row in range(col + 1, 3):
        if abs(A[row][col]) > abs(A[max_row][col]):
            max_row = row
    A[col], A[max_row] = A[max_row], A[col]

    for row in range(col + 1, 3):
        if A[col][col] != 0:
            factor = A[row][col] / A[col][col]
            for j in range(4):
                A[row][j] -= factor * A[col][j]

# 後退代入
c3 = A[2][3] / A[2][2] if A[2][2] != 0 else 0
b3 = (A[1][3] - A[1][2] * c3) / A[1][1] if A[1][1] != 0 else 0
a3 = (A[0][3] - A[0][1] * b3 - A[0][2] * c3) / A[0][0] if A[0][0] != 0 else 0

alpha3 = b3
beta3 = c3
C3 = math.exp(a3)

residuals3 = [y[i] - (a3 + b3 * x1[i] + c3 * x2[i]) for i in range(n)]
rmse3 = math.sqrt(sum(r**2 for r in residuals3) / n)
predicted3 = [a3 + b3 * x1[i] + c3 * x2[i] for i in range(n)]
r3 = pearson_r(y, predicted3)

print(f"alpha = {alpha3:.4f}")
print(f"beta = {beta3:.4f}")
print(f"C = {C3:.4f}")
print(f"R^2 = {r3**2:.6f}")
print(f"RMSE(log) = {rmse3:.6f}")

# ===== 局所指数 alpha_local =====
print("\n" + "=" * 70)
print("局所指数 alpha_local(N) = d(logD)/d(loglogN)")
print("=" * 70)

local_alphas = []
for i in range(1, len(Ns)):
    d_logD = logDNs[i] - logDNs[i-1]
    d_loglogN = loglogNs[i] - loglogNs[i-1]
    if abs(d_loglogN) > 1e-10 and d_logD > 0:
        alpha_loc = d_logD / d_loglogN
        local_alphas.append((Ns[i], alpha_loc))

# 5点移動平均
window = 5
smoothed_a = []
if len(local_alphas) > window + 1:
    for i in range(window, len(local_alphas)):
        avg = mean([a[1] for a in local_alphas[i-window:i]])
        smoothed_a.append((local_alphas[i][0], avg))

    print(f"{'N':>12} {'alpha_local(smoothed)':>22}")
    print("-" * 36)
    step = max(1, len(smoothed_a) // 12)
    for i in range(0, len(smoothed_a), step):
        n_val, a_val = smoothed_a[i]
        print(f"{n_val:>12,} {a_val:>22.4f}")

    last10_a = [a[1] for a in smoothed_a[-10:]]
    mean_last_a = mean(last10_a)
    std_last_a = std(last10_a)
    print(f"\n最後の10点平均: alpha_local = {mean_last_a:.4f} +/- {std_last_a:.4f}")

# ===== 局所指数 gamma_local =====
print("\n" + "=" * 70)
print("局所指数 gamma_local(N) = d(logD)/d(logN)")
print("=" * 70)

local_gammas = []
for i in range(1, len(Ns)):
    d_logD = logDNs[i] - logDNs[i-1]
    d_logN = logNs[i] - logNs[i-1]
    if abs(d_logN) > 1e-10 and d_logD > 0:
        gamma_loc = d_logD / d_logN
        local_gammas.append((Ns[i], gamma_loc))

smoothed_g = []
if len(local_gammas) > window + 1:
    for i in range(window, len(local_gammas)):
        avg = mean([a[1] for a in local_gammas[i-window:i]])
        smoothed_g.append((local_gammas[i][0], avg))

    print(f"{'N':>12} {'gamma_local(smoothed)':>22}")
    print("-" * 36)
    step = max(1, len(smoothed_g) // 12)
    for i in range(0, len(smoothed_g), step):
        n_val, g_val = smoothed_g[i]
        print(f"{n_val:>12,} {g_val:>22.6f}")

    last10_g = [g[1] for g in smoothed_g[-10:]]
    mean_last_g = mean(last10_g)
    std_last_g = std(last10_g)
    print(f"\n最後の10点平均: gamma_local = {mean_last_g:.6f} +/- {std_last_g:.6f}")

# ===== 最適alpha探索: CV最小化 =====
print("\n" + "=" * 70)
print("最適alpha探索: D(N)/(logN)^alpha のCV最小化")
print("=" * 70)

def cv_ratio(alpha):
    ratios = [DNs[i] / logNs[i]**alpha for i in range(len(Ns))]
    m = mean(ratios)
    s = std(ratios)
    return s / m if m > 0 else float('inf')

# 粗いスキャン
print(f"{'alpha':>8} {'CV':>12} {'mean(ratio)':>14}")
print("-" * 38)
best_alpha = 1.0
best_cv = float('inf')
for alpha_test_x10 in range(10, 35):
    alpha_test = alpha_test_x10 / 10.0
    cv = cv_ratio(alpha_test)
    ratios = [DNs[i] / logNs[i]**alpha_test for i in range(len(Ns))]
    print(f"{alpha_test:>8.1f} {cv:>12.4f} {mean(ratios):>14.4f}")
    if cv < best_cv:
        best_cv = cv
        best_alpha = alpha_test

# 細かいスキャン
print(f"\n粗いスキャンの最良: alpha = {best_alpha:.1f}")
print(f"\n精密スキャン:")
best_alpha_fine = best_alpha
best_cv_fine = best_cv
for alpha_test_x100 in range(int((best_alpha - 0.5) * 100), int((best_alpha + 0.5) * 100) + 1):
    alpha_test = alpha_test_x100 / 100.0
    cv = cv_ratio(alpha_test)
    if cv < best_cv_fine:
        best_cv_fine = cv
        best_alpha_fine = alpha_test

print(f"最適 alpha (CV最小) = {best_alpha_fine:.2f}")
print(f"最小 CV = {best_cv_fine:.4f}")

# さらに精密
best_alpha_vfine = best_alpha_fine
best_cv_vfine = best_cv_fine
for alpha_test_x1000 in range(int((best_alpha_fine - 0.05) * 1000), int((best_alpha_fine + 0.05) * 1000) + 1):
    alpha_test = alpha_test_x1000 / 1000.0
    cv = cv_ratio(alpha_test)
    if cv < best_cv_vfine:
        best_cv_vfine = cv
        best_alpha_vfine = alpha_test

print(f"最適 alpha (精密) = {best_alpha_vfine:.3f}")
print(f"最小 CV (精密) = {best_cv_vfine:.4f}")

# ===== AIC比較 =====
print("\n" + "=" * 70)
print("モデル比較 (AIC/BIC)")
print("=" * 70)

for name, res_list, k in [("(logN)^alpha", [logDNs[i] - (a1 + b1 * loglogNs[i]) for i in range(n)], 2),
                            ("N^gamma", [logDNs[i] - (a2 + b2 * logNs[i]) for i in range(n)], 2),
                            ("(logN)^a*(loglogN)^b", residuals3, 3)]:
    rss = sum(r**2 for r in res_list)
    aic = n * math.log(rss / n) + 2 * k
    bic = n * math.log(rss / n) + k * math.log(n)
    rmse_val = math.sqrt(rss / n)
    print(f"{name:>25}: AIC={aic:>8.2f}, BIC={bic:>8.2f}, RMSE={rmse_val:.6f}")

# ===== Record holders =====
print("\n" + "=" * 70)
print("Record holders (D(N)が更新される n)")
print("=" * 70)

records = []
current_max = 0
for nn in range(1, N_max + 1):
    st = stopping_time(nn)
    if st > current_max:
        current_max = st
        records.append((nn, st))

print(f"record数: {len(records)}")
print(f"\n{'n':>12} {'ST':>8} {'logn':>8} {'ST/(logn)^1.6':>14} {'ST/(logn)^alpha':>16}")
print("-" * 66)
for nn, st in records[-20:]:
    ln = math.log(nn) if nn > 1 else 1
    print(f"{nn:>12,} {st:>8} {ln:>8.2f} {st/ln**1.6:>14.4f} {st/ln**alpha1:>16.4f}")

# ===== N=10^k での D(N) =====
print("\n" + "=" * 70)
print("N = 10^k での D(N)")
print("=" * 70)

key_Ns = [1000, 3162, 10000, 31623, 100000, 316228, 1000000, 3162278, 10000000]
print(f"{'N':>12} {'D(N)':>8} {'logN':>8} {'D/(logN)^1.5':>14} {'D/(logN)^{alpha1:.2f}':>16} {'D/(logN)^2':>14}")
print("-" * 82)
for nn in key_Ns:
    if nn in DN_dict:
        d = DN_dict[nn]
        ln = math.log(nn)
        print(f"{nn:>12,} {d:>8} {ln:>8.2f} {d/ln**1.5:>14.4f} {d/ln**alpha1:>16.4f} {d/ln**2:>14.4f}")

# ===== D(N) の漸近分析: 後半データでの alpha =====
print("\n" + "=" * 70)
print("後半データ (N >= 10^5) でのフィット")
print("=" * 70)

# N >= 10^5 のデータのみ
idx_start = 0
for i in range(len(Ns)):
    if Ns[i] >= 100000:
        idx_start = i
        break

loglogNs_tail = loglogNs[idx_start:]
logDNs_tail = logDNs[idx_start:]
logNs_tail = logNs[idx_start:]

a1t, b1t = linear_regression(loglogNs_tail, logDNs_tail)
alpha1t = b1t
r1t = pearson_r(loglogNs_tail, logDNs_tail)
print(f"(logN)^alpha: alpha = {alpha1t:.4f}, R^2 = {r1t**2:.6f}")

a2t, b2t = linear_regression(logNs_tail, logDNs_tail)
gamma2t = b2t
r2t = pearson_r(logNs_tail, logDNs_tail)
print(f"N^gamma: gamma = {gamma2t:.6f}, R^2 = {r2t**2:.6f}")

# ===== 最終結論 =====
print("\n" + "=" * 70)
print("=== 最終結論 ===")
print("=" * 70)

print(f"\n全データフィット:")
print(f"  D(N) = {C1:.2f} * (logN)^{alpha1:.4f}  [R^2={r1**2:.6f}, RMSE={rmse1:.6f}]")
print(f"  D(N) = {C2:.2f} * N^{gamma2:.6f}  [R^2={r2**2:.6f}, RMSE={rmse2:.6f}]")
print(f"  D(N) = {C3:.2f} * (logN)^{alpha3:.4f} * (loglogN)^{beta3:.4f}  [R^2={r3**2:.6f}, RMSE={rmse3:.6f}]")
print(f"\n後半データ (N>=10^5) フィット:")
print(f"  alpha = {alpha1t:.4f}, gamma = {gamma2t:.6f}")
print(f"\n最適alpha (CV最小化): {best_alpha_vfine:.3f}")
print(f"\n局所alpha (大N近傍): {mean_last_a:.4f} +/- {std_last_a:.4f}" if smoothed_a else "")
print(f"局所gamma (大N近傍): {mean_last_g:.6f} +/- {std_last_g:.6f}" if smoothed_g else "")

winner = "(logN)^alpha" if rmse1 < rmse2 else "N^gamma"
print(f"\n*** 勝者: {winner} 型 ***")
if rmse3 < rmse1:
    print(f"*** ただし3パラメータモデルがさらに良好 ***")

# gamma_local が 0 に向かっているかチェック
if smoothed_g:
    first10_g = [g[1] for g in smoothed_g[:10]]
    last10_g_vals = [g[1] for g in smoothed_g[-10:]]
    print(f"\ngamma_local の減少傾向: {mean(first10_g):.6f} -> {mean(last10_g_vals):.6f}")
    if mean(last10_g_vals) < mean(first10_g) * 0.8:
        print("  -> gamma が 0 に収束する傾向あり => 多項式成長でなく対数成長を支持")
    else:
        print("  -> gamma の減少は明確でない")

# ===== JSON =====
output = {
    "model1_log_power": {
        "type": "D(N) = C * (logN)^alpha",
        "alpha": round(alpha1, 4),
        "C": round(C1, 4),
        "R2": round(r1**2, 6),
        "RMSE_log": round(rmse1, 6)
    },
    "model2_power": {
        "type": "D(N) = C * N^gamma",
        "gamma": round(gamma2, 6),
        "C": round(C2, 4),
        "R2": round(r2**2, 6),
        "RMSE_log": round(rmse2, 6)
    },
    "model3_extended": {
        "type": "D(N) = C * (logN)^alpha * (loglogN)^beta",
        "alpha": round(alpha3, 4),
        "beta": round(beta3, 4),
        "C": round(C3, 4),
        "R2": round(r3**2, 6),
        "RMSE_log": round(rmse3, 6)
    },
    "tail_fit_N_ge_100k": {
        "alpha": round(alpha1t, 4),
        "gamma": round(gamma2t, 6)
    },
    "optimal_alpha_cv_minimization": round(best_alpha_vfine, 3),
    "min_cv": round(best_cv_vfine, 4),
    "local_alpha_last10": round(mean_last_a, 4) if smoothed_a else None,
    "local_gamma_last10": round(mean_last_g, 6) if smoothed_g else None,
    "n_records": len(records),
    "N_max": N_max,
    "D_Nmax": DNs[-1],
    "winner_model": winner,
    "key_DN_values": {str(nn): DN_dict[nn] for nn in key_Ns if nn in DN_dict}
}

print("\n" + "=" * 70)
print("JSON summary:")
print(json.dumps(output, indent=2))
