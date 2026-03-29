"""
D(N) = max_{n <= N} stopping_time(n) のスケーリング則分析
N = 10^3 .. 10^9 に拡張

高速化:
  - メモ化 + ルックアップテーブル (n < CACHE_SIZE)
  - Syracuse形式 T(n) = (3n+1) / 2^{v2(3n+1)} で奇数のみ追跡

目標:
  - D(N) ~ C * (log N)^alpha のalphaの収束を調べる
  - alpha ~ 1.623 の検証と精密化
"""

import math
import time
import json
import sys

# ===== 高速 stopping time (メモ化) =====
CACHE_SIZE = 10_000_000  # 10M のキャッシュ
cache = [0] * CACHE_SIZE
cache[1] = 0

def stopping_time_memo(n):
    """メモ化つき stopping time"""
    orig_n = n
    steps = 0
    path = []

    while n != 1:
        if n < CACHE_SIZE and cache[n] > 0:
            steps += cache[n]
            break
        path.append((n, steps))
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1

    # キャッシュに書き戻す
    for prev_n, prev_steps in path:
        if prev_n < CACHE_SIZE:
            cache[prev_n] = steps - prev_steps

    return steps

# ===== まずキャッシュを温める =====
print("キャッシュのウォームアップ中...", flush=True)
t0 = time.time()
for i in range(2, min(CACHE_SIZE, 10_000_001)):
    stopping_time_memo(i)
t1 = time.time()
print(f"ウォームアップ完了: {t1 - t0:.1f}秒", flush=True)

# ===== D(N) の計算 =====
# チェックポイント: 対数的に等間隔
checkpoints = []
# 10^3 から 10^9 まで
for k in range(30, 91):  # 10^(k/10)
    val = int(round(10**(k / 10.0)))
    checkpoints.append(val)

# 10^k ぴったりも追加
for k in range(3, 10):
    checkpoints.append(10**k)

checkpoints = sorted(set(checkpoints))
N_max = max(checkpoints)

print(f"\nN_max = {N_max:,}", flush=True)
print(f"チェックポイント数: {len(checkpoints)}", flush=True)

# D(N)の漸進計算
print("\nD(N) 計算開始...", flush=True)

DN_results = {}
record_holders = []  # (n, ST) で D(N) が更新された時
current_max_st = 0
cp_idx = 0
t_start = time.time()

# 進捗報告の間隔
report_intervals = [10**k for k in range(6, 10)]

for n in range(1, N_max + 1):
    st = stopping_time_memo(n)
    if st > current_max_st:
        current_max_st = st
        record_holders.append((n, st))

    # チェックポイントチェック
    while cp_idx < len(checkpoints) and checkpoints[cp_idx] == n:
        DN_results[n] = current_max_st
        cp_idx += 1

    # 進捗報告
    if n in report_intervals:
        elapsed = time.time() - t_start
        rate = n / elapsed if elapsed > 0 else 0
        print(f"  N={n:>14,}: D(N)={current_max_st:>6}, "
              f"elapsed={elapsed:>7.1f}s, rate={rate:,.0f}/s", flush=True)

t_end = time.time()
total_time = t_end - t_start
print(f"\n計算完了: {total_time:.1f}秒", flush=True)
print(f"総数 = {N_max:,}", flush=True)

# ===== 結果テーブル =====
print("\n" + "=" * 90)
print("D(N) のテーブル")
print("=" * 90)
Ns = sorted(DN_results.keys())
DNs = [DN_results[n] for n in Ns]
logNs = [math.log(n) for n in Ns]
logDNs = [math.log(d) for d in DNs]
loglogNs = [math.log(ln) for ln in logNs]

print(f"{'N':>16} {'D(N)':>8} {'logN':>8} {'loglogN':>8} "
      f"{'D/(logN)^1.5':>14} {'D/(logN)^1.6':>14} {'D/(logN)^2':>14}")
print("-" * 100)
for i in range(len(Ns)):
    n = Ns[i]
    d = DNs[i]
    ln = logNs[i]
    lln = loglogNs[i]
    print(f"{n:>16,} {d:>8} {ln:>8.3f} {lln:>8.4f} "
          f"{d/ln**1.5:>14.4f} {d/ln**1.6:>14.4f} {d/ln**2:>14.4f}")

# ===== 統計ヘルパー =====
def mean(xs):
    return sum(xs) / len(xs) if xs else 0

def std(xs):
    if len(xs) < 2:
        return 0
    m = mean(xs)
    return math.sqrt(sum((x - m)**2 for x in xs) / len(xs))

def linear_regression(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sxx = sum((x - mx)**2 for x in xs)
    if sxx == 0:
        return my, 0.0
    b = sxy / sxx
    a = my - b * mx
    return a, b

def pearson_r(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx)**2 for x in xs))
    dy = math.sqrt(sum((y - my)**2 for y in ys))
    return num / (dx * dy) if dx > 0 and dy > 0 else 0

def rmse(xs, ys, a, b):
    n = len(xs)
    return math.sqrt(sum((ys[i] - (a + b * xs[i]))**2 for i in range(n)) / n)

# ===== モデル1: D(N) = C * (logN)^alpha =====
print("\n" + "=" * 90)
print("モデル1: D(N) = C * (logN)^alpha  [log D = log C + alpha * log(logN)]")
print("=" * 90)

a1, b1 = linear_regression(loglogNs, logDNs)
alpha1 = b1
C1 = math.exp(a1)
r1 = pearson_r(loglogNs, logDNs)
rmse1 = rmse(loglogNs, logDNs, a1, b1)

print(f"全データ: alpha = {alpha1:.4f}, C = {C1:.4f}, R^2 = {r1**2:.6f}, RMSE = {rmse1:.6f}")

# ===== 範囲を変えてフィット: alpha の安定性 =====
print("\n--- alpha の安定性: フィット範囲依存性 ---")
print(f"{'N_min':>16} {'N_max':>16} {'alpha':>8} {'C':>10} {'R^2':>10} {'data_pts':>10}")
print("-" * 80)

for N_min_exp in [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
    N_min_val = int(10**N_min_exp)
    subset_idx = [i for i in range(len(Ns)) if Ns[i] >= N_min_val]
    if len(subset_idx) < 4:
        continue
    sub_loglogNs = [loglogNs[i] for i in subset_idx]
    sub_logDNs = [logDNs[i] for i in subset_idx]
    a, b = linear_regression(sub_loglogNs, sub_logDNs)
    r = pearson_r(sub_loglogNs, sub_logDNs)
    C = math.exp(a)
    print(f"{N_min_val:>16,} {Ns[-1]:>16,} {b:>8.4f} {C:>10.4f} {r**2:>10.6f} {len(subset_idx):>10}")

# ===== モデル2: D(N) = C * N^gamma =====
print("\n" + "=" * 90)
print("モデル2: D(N) = C * N^gamma  [log D = log C + gamma * logN]")
print("=" * 90)

a2, b2 = linear_regression(logNs, logDNs)
gamma2 = b2
C2 = math.exp(a2)
r2 = pearson_r(logNs, logDNs)
rmse2 = rmse(logNs, logDNs, a2, b2)

print(f"全データ: gamma = {gamma2:.6f}, C = {C2:.4f}, R^2 = {r2**2:.6f}, RMSE = {rmse2:.6f}")

# 後半データ
for N_min_exp in [6.0, 7.0, 8.0]:
    N_min_val = int(10**N_min_exp)
    subset_idx = [i for i in range(len(Ns)) if Ns[i] >= N_min_val]
    if len(subset_idx) < 4:
        continue
    sub_logNs = [logNs[i] for i in subset_idx]
    sub_logDNs = [logDNs[i] for i in subset_idx]
    a, b = linear_regression(sub_logNs, sub_logDNs)
    r = pearson_r(sub_logNs, sub_logDNs)
    print(f"  N>={N_min_val:>12,}: gamma = {b:.6f}, R^2 = {r**2:.6f}")

# ===== 局所 alpha(N) =====
print("\n" + "=" * 90)
print("局所指数 alpha_local(N) = d(logD)/d(loglogN)")
print("=" * 90)

local_alphas = []
for i in range(1, len(Ns)):
    d_logD = logDNs[i] - logDNs[i-1]
    d_loglogN = loglogNs[i] - loglogNs[i-1]
    if abs(d_loglogN) > 1e-10 and d_logD > 0:
        alpha_loc = d_logD / d_loglogN
        local_alphas.append((Ns[i], alpha_loc))

# 移動平均
window = 5
smoothed_alphas = []
for i in range(window, len(local_alphas)):
    vals = [a[1] for a in local_alphas[i-window:i]]
    smoothed_alphas.append((local_alphas[i][0], mean(vals)))

print(f"{'N':>16} {'alpha_local (smoothed)':>24}")
print("-" * 42)
for n_val, a_val in smoothed_alphas:
    if n_val in [10**k for k in range(3, 10)] or n_val >= 10**8:
        print(f"{n_val:>16,} {a_val:>24.4f}")

# 大N近傍の alpha
if smoothed_alphas:
    last10 = [a[1] for a in smoothed_alphas[-10:]]
    print(f"\n最後の10点の alpha_local 平均: {mean(last10):.4f} +/- {std(last10):.4f}")

# ===== 局所 gamma(N) =====
print("\n" + "=" * 90)
print("局所指数 gamma_local(N) = d(logD)/d(logN)")
print("=" * 90)

local_gammas = []
for i in range(1, len(Ns)):
    d_logD = logDNs[i] - logDNs[i-1]
    d_logN = logNs[i] - logNs[i-1]
    if abs(d_logN) > 1e-10 and d_logD > 0:
        gamma_loc = d_logD / d_logN
        local_gammas.append((Ns[i], gamma_loc))

smoothed_gammas = []
for i in range(window, len(local_gammas)):
    vals = [g[1] for g in local_gammas[i-window:i]]
    smoothed_gammas.append((local_gammas[i][0], mean(vals)))

if smoothed_gammas:
    last10_g = [g[1] for g in smoothed_gammas[-10:]]
    first10_g = [g[1] for g in smoothed_gammas[:10]]
    print(f"gamma_local 推移: 初期 {mean(first10_g):.6f} -> 最終 {mean(last10_g):.6f}")
    if mean(last10_g) < mean(first10_g):
        print(f"  減少率: {mean(last10_g)/mean(first10_g):.3f} (1未満なら0へ収束傾向)")

# ===== CV最小化で最適 alpha =====
print("\n" + "=" * 90)
print("最適alpha探索: D(N)/(logN)^alpha のCV最小化")
print("=" * 90)

def cv_ratio(alpha):
    ratios = [DNs[i] / logNs[i]**alpha for i in range(len(Ns))]
    m = mean(ratios)
    s = std(ratios)
    return s / m if m > 0 else float('inf')

# 粗いスキャン
best_alpha = 1.0
best_cv = float('inf')
for alpha_x10 in range(10, 35):
    alpha_test = alpha_x10 / 10.0
    cv = cv_ratio(alpha_test)
    if cv < best_cv:
        best_cv = cv
        best_alpha = alpha_test

# 精密スキャン
for alpha_x100 in range(int((best_alpha - 0.5) * 100), int((best_alpha + 0.5) * 100) + 1):
    alpha_test = alpha_x100 / 100.0
    cv = cv_ratio(alpha_test)
    if cv < best_cv:
        best_cv = cv
        best_alpha = alpha_test

# 超精密
for alpha_x1000 in range(int((best_alpha - 0.05) * 1000), int((best_alpha + 0.05) * 1000) + 1):
    alpha_test = alpha_x1000 / 1000.0
    cv = cv_ratio(alpha_test)
    if cv < best_cv:
        best_cv = cv
        best_alpha = alpha_test

print(f"最適 alpha (CV最小) = {best_alpha:.3f}")
print(f"最小 CV = {best_cv:.4f}")

# 後半データのみでCV
subset_big = [i for i in range(len(Ns)) if Ns[i] >= 10**6]
def cv_ratio_subset(alpha):
    ratios = [DNs[i] / logNs[i]**alpha for i in subset_big]
    m = mean(ratios)
    s = std(ratios)
    return s / m if m > 0 else float('inf')

best_alpha_big = 1.0
best_cv_big = float('inf')
for alpha_x100 in range(100, 300):
    alpha_test = alpha_x100 / 100.0
    cv = cv_ratio_subset(alpha_test)
    if cv < best_cv_big:
        best_cv_big = cv
        best_alpha_big = alpha_test

for alpha_x1000 in range(int((best_alpha_big - 0.05) * 1000), int((best_alpha_big + 0.05) * 1000) + 1):
    alpha_test = alpha_x1000 / 1000.0
    cv = cv_ratio_subset(alpha_test)
    if cv < best_cv_big:
        best_cv_big = cv
        best_alpha_big = alpha_test

print(f"最適 alpha (N>=10^6, CV最小) = {best_alpha_big:.3f}")
print(f"最小 CV (N>=10^6) = {best_cv_big:.4f}")

# ===== Record holders 分析 =====
print("\n" + "=" * 90)
print(f"Record holders (最後の30件, 合計 {len(record_holders)} 件)")
print("=" * 90)

print(f"{'n':>16} {'ST':>8} {'logn':>8} {'ST/(logn)^1.6':>16} {'ST/(logn)^alpha':>18}")
print("-" * 80)
for nn, st in record_holders[-30:]:
    ln = math.log(nn) if nn > 1 else 1
    print(f"{nn:>16,} {st:>8} {ln:>8.3f} "
          f"{st/ln**1.6:>16.4f} {st/ln**alpha1:>18.4f}")

# ===== D(10^k) テーブル =====
print("\n" + "=" * 90)
print("D(10^k) の値")
print("=" * 90)

dk_values = {}
print(f"{'k':>4} {'N=10^k':>16} {'D(N)':>8} {'logN':>8} {'D/(logN)^1.5':>14} "
      f"{'D/(logN)^1.6':>14} {'D/(logN)^1.7':>14} {'D/(logN)^2':>14}")
print("-" * 106)
for k in range(3, 10):
    N = 10**k
    if N in DN_results:
        d = DN_results[N]
        ln = math.log(N)
        dk_values[k] = d
        print(f"{k:>4} {N:>16,} {d:>8} {ln:>8.3f} {d/ln**1.5:>14.4f} "
              f"{d/ln**1.6:>14.4f} {d/ln**1.7:>14.4f} {d/ln**2:>14.4f}")

# ===== D(10^k) からの alpha 推定 =====
print("\n--- D(10^k) ペアからの alpha 推定 ---")
print(f"{'k1':>4} {'k2':>4} {'alpha_est':>12}")
print("-" * 24)
dk_keys = sorted(dk_values.keys())
for i in range(len(dk_keys)):
    for j in range(i+1, len(dk_keys)):
        k1, k2 = dk_keys[i], dk_keys[j]
        d1, d2 = dk_values[k1], dk_values[k2]
        logN1 = math.log(10**k1)
        logN2 = math.log(10**k2)
        # D ~ C * (logN)^alpha  =>  log(D2/D1) = alpha * log(logN2/logN1)
        if logN2 > logN1 and d2 > d1:
            alpha_est = math.log(d2/d1) / math.log(logN2/logN1)
            print(f"{k1:>4} {k2:>4} {alpha_est:>12.4f}")

# ===== 3パラメータモデル =====
print("\n" + "=" * 90)
print("モデル3: D(N) = C * (logN)^alpha * (loglogN)^beta")
print("=" * 90)

logloglogNs = [math.log(x) for x in loglogNs]
n = len(Ns)
x1 = loglogNs
x2 = logloglogNs
y = logDNs

sx1 = sum(x1); sx2 = sum(x2); sy = sum(y)
sx1x1 = sum(a*a for a in x1); sx2x2 = sum(a*a for a in x2)
sx1x2 = sum(x1[i]*x2[i] for i in range(n))
sx1y = sum(x1[i]*y[i] for i in range(n))
sx2y = sum(x2[i]*y[i] for i in range(n))

A = [[n, sx1, sx2, sy],
     [sx1, sx1x1, sx1x2, sx1y],
     [sx2, sx1x2, sx2x2, sx2y]]

for col in range(3):
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

print(f"alpha = {alpha3:.4f}, beta = {beta3:.4f}, C = {C3:.4f}")
print(f"R^2 = {r3**2:.6f}, RMSE = {rmse3:.6f}")

# ===== AIC/BIC =====
print("\n" + "=" * 90)
print("モデル比較 (AIC/BIC)")
print("=" * 90)

models = [
    ("(logN)^alpha", [logDNs[i] - (a1 + b1*loglogNs[i]) for i in range(n)], 2),
    ("N^gamma", [logDNs[i] - (a2 + b2*logNs[i]) for i in range(n)], 2),
    ("(logN)^a*(loglogN)^b", residuals3, 3),
]

for name, res_list, k in models:
    rss = sum(r**2 for r in res_list)
    aic = n * math.log(rss / n) + 2 * k
    bic = n * math.log(rss / n) + k * math.log(n)
    rmse_val = math.sqrt(rss / n)
    print(f"  {name:>25}: AIC={aic:>8.2f}, BIC={bic:>8.2f}, RMSE={rmse_val:.6f}")

# ===== 外挿予測 =====
print("\n" + "=" * 90)
print("モデル外挿: N=10^10..10^15")
print("=" * 90)

print(f"{'N':>16} {'(logN)^{alpha1:.2f}':>16} {'(logN)^1.623':>16} {'N^{gamma2:.4f}':>16}")
print("-" * 70)
for exp in range(3, 16):
    N = 10**exp
    logN = math.log(N)
    pred1 = C1 * logN**alpha1
    pred_1623 = C1 * logN**1.623  # 既知alpha
    pred2 = C2 * N**gamma2
    marker = " <-- computed" if exp < 10 and 10**exp in DN_results else ""
    actual = f" [actual={DN_results[10**exp]}]" if 10**exp in DN_results else ""
    print(f"  10^{exp:>2}: {pred1:>14.1f} {pred_1623:>14.1f} {pred2:>14.1f}{actual}")

# ===== 最終まとめ =====
print("\n" + "=" * 90)
print("=== 最終結論 ===")
print("=" * 90)

print(f"""
計算範囲: N = 1 .. {N_max:,}
計算時間: {total_time:.1f}秒

モデル1 (全データ): D(N) = {C1:.2f} * (logN)^{alpha1:.4f}  [R^2={r1**2:.6f}]
モデル2 (全データ): D(N) = {C2:.2f} * N^{gamma2:.6f}  [R^2={r2**2:.6f}]
モデル3 (全データ): D(N) = {C3:.2f} * (logN)^{alpha3:.4f} * (loglogN)^{beta3:.4f}  [R^2={r3**2:.6f}]

最適 alpha (CV最小, 全データ): {best_alpha:.3f}
最適 alpha (CV最小, N>=10^6): {best_alpha_big:.3f}
""")

# ===== JSON 出力 =====
output = {
    "N_max": N_max,
    "computation_time_sec": round(total_time, 1),
    "num_checkpoints": len(checkpoints),
    "num_record_holders": len(record_holders),
    "DN_at_powers_of_10": dk_values,
    "model1_log_power_all": {
        "alpha": round(alpha1, 4),
        "C": round(C1, 4),
        "R2": round(r1**2, 6),
        "RMSE": round(rmse1, 6)
    },
    "model2_N_power_all": {
        "gamma": round(gamma2, 6),
        "C": round(C2, 4),
        "R2": round(r2**2, 6),
        "RMSE": round(rmse2, 6)
    },
    "model3_two_param": {
        "alpha": round(alpha3, 4),
        "beta": round(beta3, 4),
        "C": round(C3, 4),
        "R2": round(r3**2, 6),
        "RMSE": round(rmse3, 6)
    },
    "optimal_alpha_cv_all": round(best_alpha, 3),
    "optimal_alpha_cv_N_ge_1e6": round(best_alpha_big, 3),
    "alpha_stability": {},
    "local_alpha_last10_mean": round(mean(last10), 4) if smoothed_alphas else None,
    "local_alpha_last10_std": round(std(last10), 4) if smoothed_alphas else None,
    "last_record_holder": {"n": record_holders[-1][0], "ST": record_holders[-1][1]} if record_holders else None,
    "DN_table": {str(n): DN_results[n] for n in Ns},
}

# alpha stability
for N_min_exp in [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
    N_min_val = int(10**N_min_exp)
    subset_idx = [i for i in range(len(Ns)) if Ns[i] >= N_min_val]
    if len(subset_idx) < 4:
        continue
    sub_loglogNs = [loglogNs[i] for i in subset_idx]
    sub_logDNs = [logDNs[i] for i in subset_idx]
    a, b = linear_regression(sub_loglogNs, sub_logDNs)
    output["alpha_stability"][f"N_ge_{N_min_val}"] = round(b, 4)

json_path = "/Users/soyukke/study/lean-unsolved/results/DN_scaling_1e9.json"
with open(json_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nJSON保存: {json_path}")
print(json.dumps(output, indent=2))
