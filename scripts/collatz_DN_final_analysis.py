"""
D(N) alpha 収束: 最終分析
N=10^8 の D(N)=949 という新データを含む包括的分析

核心の問い: D(N) ~ (logN)^alpha の alpha は何に収束するのか?
"""

import math
import json

# D(10^k) データ
dk = {
    3: 178,     # D(10^3) = 178
    4: 261,     # D(10^4) = 261
    5: 350,     # D(10^5) = 350
    6: 524,     # D(10^6) = 524
    7: 685,     # D(10^7) = 685
    8: 949,     # D(10^8) = 949 [新データ]
}
# D(2*10^8) = 953 [新データ]

def mean(xs):
    return sum(xs)/len(xs) if xs else 0

def std(xs):
    if len(xs) < 2: return 0
    m = mean(xs)
    return math.sqrt(sum((x-m)**2 for x in xs)/len(xs))

def linreg(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    sxx = sum((x-mx)**2 for x in xs)
    if sxx == 0: return my, 0.0
    b = sxy/sxx; a = my - b*mx
    return a, b

def pearson(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    num = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx>0 and dy>0 else 0

print("=" * 90)
print("D(N) = max stopping time up to N: alpha の収束分析")
print("=" * 90)

# ====================================================================
# 1. 基本回帰: log(D) = logC + alpha * log(logN)
# ====================================================================
dk_keys = sorted(dk.keys())
xs = [math.log(k * math.log(10)) for k in dk_keys]
ys = [math.log(dk[k]) for k in dk_keys]

a, alpha = linreg(xs, ys)
C = math.exp(a)
r = pearson(xs, ys)

print(f"\n1. 基本回帰 (k=3..8):")
print(f"   D(N) = {C:.3f} * (logN)^{alpha:.4f}")
print(f"   R^2 = {r**2:.6f}")

# ====================================================================
# 2. 隣接ペア instantaneous alpha
# ====================================================================
print(f"\n2. 隣接ペアの instantaneous alpha:")
inst_alphas = []
for i in range(len(dk_keys)-1):
    k1, k2 = dk_keys[i], dk_keys[i+1]
    d1, d2 = dk[k1], dk[k2]
    lN1, lN2 = k1*math.log(10), k2*math.log(10)
    a_inst = math.log(d2/d1) / math.log(lN2/lN1)
    inst_alphas.append(a_inst)
    print(f"   k={k1}->{k2}: alpha_inst = {a_inst:.4f}")

print(f"\n   推移: {' -> '.join(f'{a:.2f}' for a in inst_alphas)}")

# 傾向分析
if len(inst_alphas) >= 3:
    first_half = mean(inst_alphas[:len(inst_alphas)//2])
    second_half = mean(inst_alphas[len(inst_alphas)//2:])
    print(f"   前半平均: {first_half:.4f}, 後半平均: {second_half:.4f}")
    if second_half > first_half * 1.1:
        print(f"   => alpha は増大傾向 (alpha -> infinity の可能性)")
    elif second_half < first_half * 0.9:
        print(f"   => alpha は減少傾向 (alpha -> 有限値 に収束)")
    else:
        print(f"   => alpha は概ね安定")

# ====================================================================
# 3. D(N)/(logN)^alpha のトレンド検出
# ====================================================================
print(f"\n3. D(N)/(logN)^alpha のトレンド検出:")
for a_test in [1.5, 1.6, 1.623, 1.7, 1.8, 2.0]:
    ratios = []
    for k in dk_keys:
        logN = k * math.log(10)
        r = dk[k] / logN**a_test
        ratios.append(r)

    # 線形トレンド: ratio vs k
    ks = list(range(len(dk_keys)))
    a_t, b_t = linreg(ks, ratios)
    # b_t > 0: 増加 (alpha小さすぎ), b_t < 0: 減少 (alpha大きすぎ), b_t~0: 適切
    trend = "増加(alpha小)" if b_t > 0.05 else ("減少(alpha大)" if b_t < -0.05 else "安定(alpha適切)")
    cv = std(ratios)/mean(ratios) if mean(ratios) > 0 else float('inf')
    print(f"   alpha={a_test:.3f}: ratios={[f'{r:.2f}' for r in ratios]}")
    print(f"              CV={cv:.4f}, trend_slope={b_t:.4f} => {trend}")

# ====================================================================
# 4. 精密なalpha推定: 最小CV
# ====================================================================
print(f"\n4. 精密な alpha 推定:")
best_a = 1.0; best_cv = float('inf')
for ax10000 in range(10000, 30000):
    a_test = ax10000 / 10000.0
    ratios = [dk[k] / (k*math.log(10))**a_test for k in dk_keys]
    m = mean(ratios); s = std(ratios)
    cv = s/m if m > 0 else float('inf')
    if cv < best_cv: best_cv = cv; best_a = a_test
print(f"   CV最小 alpha = {best_a:.4f} (CV = {best_cv:.6f})")

# k=5..8のみ
best_a58 = 1.0; best_cv58 = float('inf')
keys58 = [k for k in dk_keys if k >= 5]
for ax10000 in range(10000, 30000):
    a_test = ax10000 / 10000.0
    ratios = [dk[k] / (k*math.log(10))**a_test for k in keys58]
    m = mean(ratios); s = std(ratios)
    cv = s/m if m > 0 else float('inf')
    if cv < best_cv58: best_cv58 = cv; best_a58 = a_test
print(f"   CV最小 alpha (k>=5) = {best_a58:.4f} (CV = {best_cv58:.6f})")

# k=6..8のみ
best_a68 = 1.0; best_cv68 = float('inf')
keys68 = [k for k in dk_keys if k >= 6]
for ax10000 in range(10000, 30000):
    a_test = ax10000 / 10000.0
    ratios = [dk[k] / (k*math.log(10))**a_test for k in keys68]
    m = mean(ratios); s = std(ratios)
    cv = s/m if m > 0 else float('inf')
    if cv < best_cv68: best_cv68 = cv; best_a68 = a_test
print(f"   CV最小 alpha (k>=6) = {best_a68:.4f} (CV = {best_cv68:.6f})")

# ====================================================================
# 5. 対数微分分析: d(logD)/d(loglogN)
# ====================================================================
print(f"\n5. 対数微分 d(logD)/d(loglogN):")
for i in range(len(dk_keys)-1):
    k1, k2 = dk_keys[i], dk_keys[i+1]
    d_logD = math.log(dk[k2]) - math.log(dk[k1])
    d_loglogN = math.log(k2 * math.log(10)) - math.log(k1 * math.log(10))
    local_alpha = d_logD / d_loglogN
    print(f"   k={k1}->{k2}: d(logD)/d(loglogN) = {local_alpha:.4f}")

# ====================================================================
# 6. D(N) / logN の成長速度
# ====================================================================
print(f"\n6. D(N)/logN の成長:")
for k in dk_keys:
    logN = k * math.log(10)
    ratio = dk[k] / logN
    print(f"   k={k}: D/logN = {ratio:.2f}")

# D/logN ~ (logN)^(alpha-1) なので、log(D/logN) vs loglogN の傾き = alpha-1
ratios_dlogn = [dk[k]/(k*math.log(10)) for k in dk_keys]
log_ratios = [math.log(r) for r in ratios_dlogn]
loglogNs = [math.log(k*math.log(10)) for k in dk_keys]
a_r, b_r = linreg(loglogNs, log_ratios)
print(f"   回帰: alpha - 1 = {b_r:.4f} => alpha = {b_r+1:.4f}")

# ====================================================================
# 7. Gumbel EVT 比較
# ====================================================================
print(f"\n7. Gumbel EVT との比較:")
# もし ST(n) ~ iid with P(ST>t) ~ exp(-lambda*t)
# then D(N) ~ log(N)/lambda (Gumbel mode)
# 実測 D(N)/logN の増大は EVT からの乖離

lambda_tail = 0.0735  # 既知の尾部指数

print(f"   尾部指数 lambda = {lambda_tail}")
print(f"   Gumbel予測: D(N) ~ logN / lambda = {1/lambda_tail:.2f} * logN")
print(f"   実測との比 D_actual / D_gumbel:")
for k in dk_keys:
    logN = k * math.log(10)
    gumbel = logN / lambda_tail
    ratio = dk[k] / gumbel
    print(f"     k={k}: ratio = {ratio:.4f}")

print(f"\n   この比の増大は、stopping time が iid でないことの証拠")
print(f"   (高いSTを持つnが集中的に出現する)")

# ====================================================================
# 8. 総合判定
# ====================================================================
print(f"\n" + "=" * 90)
print("8. 総合判定")
print("=" * 90)

# 各手法のalpha推定値
estimates = {
    "全体回帰 (k=3..8)": alpha,
    "CV最小 (全k)": best_a,
    "CV最小 (k>=5)": best_a58,
    "CV最小 (k>=6)": best_a68,
    "D/logN 回帰 (alpha-1)": b_r + 1,
    "inst alpha 平均 (全)": mean(inst_alphas),
    "inst alpha 平均 (後半)": mean(inst_alphas[2:]),
}

print(f"\n各手法の alpha 推定値:")
for name, val in estimates.items():
    print(f"   {name:30s}: {val:.4f}")

all_est = list(estimates.values())
print(f"\n   全推定の中央値: {sorted(all_est)[len(all_est)//2]:.4f}")
print(f"   全推定の平均: {mean(all_est):.4f}")
print(f"   全推定の標準偏差: {std(all_est):.4f}")

# ====================================================================
# 9. D(10^8)=949 の意味
# ====================================================================
print(f"\n" + "=" * 90)
print("9. D(10^8)=949 の意味")
print("=" * 90)

print(f"\n   D(10^7) = 685, D(10^8) = 949")
print(f"   増加率: {949/685:.4f} (38.5%増)")
print(f"   logN の増加率: {8*math.log(10)/(7*math.log(10)):.4f} (14.3%増)")
print(f"   (logN)^1.6 の増加率: {(8*math.log(10))**1.6/(7*math.log(10))**1.6:.4f}")
print(f"   (logN)^1.7 の増加率: {(8*math.log(10))**1.7/(7*math.log(10))**1.7:.4f}")
print(f"   (logN)^2.0 の増加率: {(8*math.log(10))**2.0/(7*math.log(10))**2.0:.4f}")
print(f"   (logN)^2.4 の増加率: {(8*math.log(10))**2.4/(7*math.log(10))**2.4:.4f}")

# D(10^8)/D(10^7) = 949/685 = 1.385
# (logN8/logN7)^alpha = (8/7)^alpha * (log10)^0 = (8/7)^alpha
# 実は (log(10^8)/log(10^7))^alpha = (8*log10 / 7*log10)^alpha = (8/7)^alpha
# 1.385 = (8/7)^alpha => alpha = log(1.385)/log(8/7) = log(1.385)/log(1.1429)
alpha_78 = math.log(949/685) / math.log(8/7)
print(f"\n   D(10^8)/D(10^7) から: alpha = {alpha_78:.4f}")
print(f"   (logN が定数倍なので log(logN) の比から)")

# 正確には: log(D8/D7) / log(logN8/logN7)
alpha_78_exact = math.log(949/685) / math.log(math.log(10**8)/math.log(10**7))
print(f"   正確な alpha_inst(7->8) = {alpha_78_exact:.4f}")

# ====================================================================
# 10. 予測と検証可能な帰結
# ====================================================================
print(f"\n" + "=" * 90)
print("10. 予測と検証可能な帰結")
print("=" * 90)

# 各alphaでの D(10^9) 予測
print(f"\n   D(10^9) の予測:")
logN9 = 9 * math.log(10)
for a_pred in [1.6, 1.7, 1.8, 2.0, 2.4]:
    # Cを k=8 から逆算
    C_pred = dk[8] / (8*math.log(10))**a_pred
    D9_pred = C_pred * logN9**a_pred
    print(f"     alpha={a_pred:.1f}: D(10^9) ~ {D9_pred:.0f}")

# 全体回帰からの予測
D9_reg = C * logN9**alpha
print(f"     回帰 (alpha={alpha:.3f}): D(10^9) ~ {D9_reg:.0f}")

# ====================================================================
# 結論
# ====================================================================
print(f"\n" + "=" * 90)
print("結論")
print("=" * 90)

conclusion_text = f"""
D(N) = max_{{n<=N}} stopping_time(n) のスケーリング D(N) ~ C*(logN)^alpha

[既知] alpha ~ 1.623 (N=10^7 まで)
[新規] D(10^8) = 949 の発見

主要結果:
1. D(10^8)=949 を含めた全体回帰: alpha = {alpha:.4f}
   N=10^7 までの alpha=1.596 から増加 (+ 0.10)

2. 瞬間 alpha (k=7->8) = {alpha_78_exact:.4f}
   これは k=3->4 (1.33) や k=6->7 (1.74) より大きい

3. CV最小 alpha:
   全範囲: {best_a:.4f}
   k>=5: {best_a58:.4f}
   k>=6: {best_a68:.4f}
   大N ほど alpha が大きくなる

4. D(N)/(logN)^alpha のトレンド:
   alpha=1.6: わずかに増加傾向
   alpha=1.7: ほぼ安定
   alpha=1.8: わずかに減少傾向
   => 現時点での最良推定: alpha ~ 1.65-1.75

5. 瞬間 alpha の推移: 1.33 -> 1.31 -> 2.21 -> 1.74 -> 2.44
   不安定だが、全体的に増大傾向が見える
   alpha が漸近的に増大し続ける可能性を排除できない

6. Gumbel EVT 予測との乖離が N と共に増大
   => stopping time 間の相関が重要

D(10^9) 予測: {D9_reg:.0f} (回帰), 1050-1300 (alpha依存)
"""
print(conclusion_text)

# ===== JSON =====
output = {
    "title": "D(N)_alpha_convergence_final",
    "new_data": {"D_1e8": 949, "D_2e8": 953},
    "DN_table": dk,
    "regression_all": {
        "alpha": round(alpha, 4),
        "C": round(C, 4),
        "R2": round(r**2, 6)
    },
    "instantaneous_alpha": {
        f"{dk_keys[i]}-{dk_keys[i+1]}": round(inst_alphas[i], 4)
        for i in range(len(inst_alphas))
    },
    "cv_optimal_alpha": {
        "all_k": round(best_a, 4),
        "k_ge_5": round(best_a58, 4),
        "k_ge_6": round(best_a68, 4),
    },
    "DlogN_regression_alpha": round(b_r + 1, 4),
    "alpha_estimates_summary": {
        "median": round(sorted(all_est)[len(all_est)//2], 4),
        "mean": round(mean(all_est), 4),
        "std": round(std(all_est), 4),
    },
    "alpha_trend": "weakly_increasing_with_N",
    "best_estimate_alpha": "1.65-1.75 (with upward trend)",
    "D_1e9_prediction": {
        "regression": round(D9_reg, 0),
        "alpha_1.6": round(dk[8]/(8*math.log(10))**1.6 * (9*math.log(10))**1.6, 0),
        "alpha_1.7": round(dk[8]/(8*math.log(10))**1.7 * (9*math.log(10))**1.7, 0),
        "alpha_2.0": round(dk[8]/(8*math.log(10))**2.0 * (9*math.log(10))**2.0, 0),
    },
    "key_findings": [
        "D(10^8)=949 は alpha=1.6 モデルの予測(~870)を9%超過",
        "瞬間alpha(k=7->8)=2.44 は過去最高",
        "alphaは安定せず、Nと共に緩やかに増大する傾向",
        "D(N)/(logN)^1.7 がN=10^3..10^8で最も安定",
        "Gumbel EVTからの乖離が増大 => ST間の相関が重要",
    ]
}

json_path = "/Users/soyukke/study/lean-unsolved/results/DN_alpha_convergence_final.json"
with open(json_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"JSON保存: {json_path}")
