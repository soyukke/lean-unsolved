"""
ランダムSyracuseモデルでの到達時間の大偏差解析（純Python版）

モデル:
  Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} で v2 を i.i.d. 幾何分布とみなす。
  各ステップの log 変化量: X_i = log(3) - v2_i * log(2)
  S_k = X_1 + ... + X_k = k*log(3) - (v2_1+...+v2_k)*log(2)
  log(T^k(n)) ≈ log(n) + S_k
"""

from math import log, exp, sqrt, pi
import random

L2 = log(2)
L3 = log(3)
L5 = log(5)
EX = L3 - 2 * L2  # = log(3/4)

# ===== パート1: 理論的なCramér関数の導出 =====
print("=" * 70)
print("パート1: 基本量の導出")
print("=" * 70)

print(f"v2 ~ Geom(1/2) on {{1,2,...}}: P(v2=j) = 1/2^j")
print(f"X = log(3) - v2*log(2)")
print(f"E[X] = log(3) - 2*log(2) = log(3/4) = {EX:.10f}")
print(f"  → 各ステップで平均 {EX:.6f} ずつ log(n) が減少")
print(f"  → 縮小率 3/4 = {exp(EX):.6f}")
print(f"Var[X] = 2*(log2)^2 = {2*L2**2:.10f}")

# ===== MGF =====
print("\n" + "=" * 70)
print("パート2: モーメント母関数")
print("=" * 70)

print("""
M_X(t) = E[exp(t*X)] = 3^t * Σ_{j=1}^∞ 2^{-j} * 2^{-tj}
       = 3^t * Σ_{j=1}^∞ 2^{-j(t+1)}
       = 3^t / (2^{t+1} - 1)    for t > -1

Λ(t) = log M_X(t) = t*log(3) - log(2^{t+1} - 1)

Λ'(t) = log(3) - 2^{t+1}*log(2) / (2^{t+1} - 1)

Λ''(t) = 2^{t+1}*(log2)^2 / (2^{t+1} - 1)^2
""")

def mgf(t):
    return 3**t / (2**(t+1) - 1)

def log_mgf(t):
    return t * L3 - log(2**(t+1) - 1)

def log_mgf_deriv(t):
    u = 2**(t+1)
    return L3 - u * L2 / (u - 1)

def log_mgf_deriv2(t):
    u = 2**(t+1)
    return u * L2**2 / (u - 1)**2

print(f"検証:")
print(f"  M_X(0) = {mgf(0):.6f} (should be 1)")
print(f"  Λ(0) = {log_mgf(0):.10f} (should be 0)")
print(f"  Λ'(0) = {log_mgf_deriv(0):.10f} = E[X] = {EX:.10f} ✓")
print(f"  Λ''(0) = {log_mgf_deriv2(0):.10f} = 2*(log2)^2 = {2*L2**2:.10f} ✓")

# ===== Λ'(t) の範囲 =====
print(f"\nΛ'(t) の漸近挙動:")
print(f"  t→-1+: Λ'(t) → -∞")
print(f"  t→+∞:  Λ'(t) → log(3) - log(2) = log(3/2) = {L3-L2:.10f}")
print(f"  値域: (-∞, log(3/2))")
print(f"  log(3/2) = {L3-L2:.6f} > 0 → x=0 での Cramér関数は有限!")

# ===== I(0): 発散のレート =====
print("\n" + "=" * 70)
print("パート3: 発散確率 P(S_k > 0) の指数減衰レート")
print("=" * 70)

# Λ'(t*) = 0 を解く
# log(3) = 2^{t*+1} * log(2) / (2^{t*+1} - 1)
# w = 2^{t*+1} とおく: log(3) = w*log(2)/(w-1)
# w*(log(3)-log(2)) = log(3) → w = log(3)/log(3/2)

w_star = L3 / (L3 - L2)
t_star = log(w_star) / L2 - 1
I_0 = -(t_star * L3 - log(2**(t_star + 1) - 1))

print(f"  Λ'(t*) = 0 の解:")
print(f"  w* = log(3)/log(3/2) = {w_star:.10f}")
print(f"  t* = log₂(w*) - 1 = {t_star:.10f}")
print(f"  Λ(t*) = {log_mgf(t_star):.10f}")
print(f"  Λ'(t*) = {log_mgf_deriv(t_star):.2e} (≈ 0 ✓)")
print(f"\n  ★ I(0) = {I_0:.10f}")
print(f"  ★ exp(-I(0)) = {exp(-I_0):.10f}")

# ===== Cramér関数の閉形式 =====
print("\n" + "=" * 70)
print("パート4: Cramér関数 I(x) の閉形式")
print("=" * 70)

def cramer_I(x):
    """Cramér関数の閉形式"""
    a = L3 - x
    b = L3 - L2 - x  # = log(3/2) - x
    if b <= 0:
        return float('inf')
    w = a / b
    t_s = log(w) / L2 - 1
    return t_s * x - (t_s * L3 - log(w - 1))

print("""
■ 閉形式:
  a(x) = log(3) - x
  b(x) = log(3/2) - x
  w(x) = a(x)/b(x)
  t*(x) = log₂(w(x)) - 1
  I(x) = t*(x)·x - t*(x)·log(3) + log(w(x) - 1)

  定義域: x < log(3/2) ≈ 0.4055
  最小値: I(log(3/4)) = 0 (平均点)
""")

# 重要な点でのI(x)
print("重要な点でのCramér関数:")
key_points = [
    ("E[X]=log(3/4)", EX),
    ("x=-1.0", -1.0),
    ("x=-0.5", -0.5),
    ("x=-0.1", -0.1),
    ("x=0 (発散境界)", 0.0),
    ("x=0.1", 0.1),
    ("x=0.2", 0.2),
    ("x=0.3", 0.3),
    ("x=0.4", 0.4),
]

for name, x in key_points:
    I_val = cramer_I(x)
    if I_val < 1e15:
        print(f"  I({x:8.4f}) = {I_val:.10f}   [{name}]")
    else:
        print(f"  I({x:8.4f}) = +∞              [{name}]")

# ===== 発散確率の定量評価 =====
print("\n" + "=" * 70)
print("パート5: 発散確率の定量評価")
print("=" * 70)

print(f"\n大偏差原理: P(S_k/k ≥ 0) ≲ exp(-k·I(0))")
print(f"  I(0) = {I_0:.10f}")
print(f"\n各kでの発散確率上界:")
print(f"{'k':>6} | {'exp(-k·I(0))':>16} | {'解釈':>30}")
print("-" * 60)
for k in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
    prob_bound = exp(-k * I_0)
    if prob_bound > 1e-10:
        interpretation = f"約 1/{1/prob_bound:.0f}"
    else:
        interpretation = "事実上ゼロ"
    print(f"{k:6d} | {prob_bound:16.6e} | {interpretation:>30}")

# ===== モンテカルロ検証 =====
print("\n" + "=" * 70)
print("パート6: モンテカルロシミュレーション検証")
print("=" * 70)

random.seed(42)
N_samples = 500000

def geom_sample():
    """Geom(1/2) on {1,2,...}"""
    j = 1
    while random.random() < 0.5:
        j += 1
    return j

k_values = [1, 2, 3, 5, 10, 15, 20, 30, 50, 100]
print(f"\nシミュレーション (N={N_samples:,} サンプル):")
print(f"{'k':>5} | {'P(S_k>0) sim':>14} | {'exp(-k·I(0))':>14} | {'実効ﾚｰﾄ':>12} | {'I(0)':>10}")
print("-" * 70)

sim_results = []
for k in k_values:
    count_diverge = 0
    for _ in range(N_samples):
        v2_sum = sum(geom_sample() for _ in range(k))
        S_k = k * L3 - v2_sum * L2
        if S_k > 0:
            count_diverge += 1

    prob_diverge = count_diverge / N_samples
    bound = exp(-k * I_0)

    if prob_diverge > 0:
        empirical_rate = -log(prob_diverge) / k
    else:
        empirical_rate = float('inf')

    sim_results.append((k, prob_diverge, empirical_rate))

    if empirical_rate < 1e10:
        print(f"{k:5d} | {prob_diverge:14.6e} | {bound:14.6e} | {empirical_rate:12.6f} | {I_0:10.6f}")
    else:
        print(f"{k:5d} | {prob_diverge:14.6e} | {bound:14.6e} | {'∞':>12} | {I_0:10.6f}")

# ===== 実際のコラッツ軌道との比較 =====
print("\n" + "=" * 70)
print("パート7: 実際のコラッツ軌道との比較")
print("=" * 70)

def syracuse(n):
    """Syracuse関数 T(n)。奇数nに対して (3n+1)/2^v2 を返す"""
    m = 3 * n + 1
    v2 = 0
    while m % 2 == 0:
        m //= 2
        v2 += 1
    return m, v2

all_v2 = []
all_log_changes = []
odd_numbers = range(1, 20001, 2)

for n in odd_numbers:
    current = n
    for _ in range(10000):
        if current <= 1:
            break
        if current % 2 == 0:
            current //= 2
            continue
        new_val, v2 = syracuse(current)
        all_v2.append(v2)
        all_log_changes.append(log(3) - v2 * log(2))
        current = new_val

n_steps = len(all_log_changes)
mean_X = sum(all_log_changes) / n_steps
var_X = sum((x - mean_X)**2 for x in all_log_changes) / n_steps
mean_v2 = sum(all_v2) / len(all_v2)

print(f"  総ステップ数: {n_steps:,}")
print(f"  E[X] 実測: {mean_X:.10f}")
print(f"  E[X] 理論: {EX:.10f}")
print(f"  差: {abs(mean_X - EX):.2e}")
print(f"  Var[X] 実測: {var_X:.10f}")
print(f"  Var[X] 理論: {2*L2**2:.10f}")
print(f"  E[v2] 実測: {mean_v2:.10f}")
print(f"  E[v2] 理論: 2.0")

# v2の分布
print(f"\n  v2の分布:")
v2_counts = {}
for v in all_v2:
    v2_counts[v] = v2_counts.get(v, 0) + 1
for j in range(1, 8):
    empirical = v2_counts.get(j, 0) / len(all_v2)
    theory = 1.0 / 2**j
    ratio = empirical / theory if theory > 0 else 0
    print(f"    P(v2={j}): 実測={empirical:.6f}, 理論={theory:.6f}, 比={ratio:.4f}")

# 実際の軌道でS_k > 0となるステップの頻度
print(f"\n  実際の軌道での累積S_k > 0の統計:")
# いくつかの軌道でS_kの推移を調べる
test_starts = [27, 97, 871, 6171, 77031, 837799]
for n in test_starts:
    current = n
    S_k = 0.0
    steps = 0
    max_S = 0.0
    positive_steps = 0
    for _ in range(100000):
        if current <= 1:
            break
        if current % 2 == 0:
            current //= 2
            continue
        _, v2 = syracuse(current)
        current_new, _ = syracuse(current)
        S_k += log(3) - v2 * log(2)
        steps += 1
        if S_k > 0:
            positive_steps += 1
        max_S = max(max_S, S_k)
        current = current_new
    if steps > 0:
        print(f"    n={n:>8d}: {steps:>4d}ステップ, S_k>0: {positive_steps}/{steps} ({positive_steps/steps*100:.1f}%), max(S_k)={max_S:.4f}")

# ===== 有限時間到達確率 =====
print("\n" + "=" * 70)
print("パート8: 有限時間到達確率の下界")
print("=" * 70)

print(f"\n到達条件: S_k < -log(n) (log(T^k(n)) ≈ log(n) + S_k < 0)")
print(f"S_k/k ≈ E[X] = log(3/4) = {EX:.6f}")
print(f"k > log(n)/|E[X]| = {1/abs(EX):.4f} · log(n)")
print(f"\n  到達に必要なステップ数の見積もり:")
for bits in [10, 20, 32, 64, 128, 256, 1000]:
    log_n = bits * L2
    k_needed = log_n / abs(EX)
    print(f"    n ~ 2^{bits:>4d}: k ≈ {k_needed:.1f} ステップ")

# CLT による精密評価
print(f"\n  中心極限定理による到達確率:")
print(f"  P(S_k < -log(n)) = P((S_k - k·μ)/√(k·σ²) < (-log(n) - k·μ)/(√k·σ))")
print(f"  μ = {EX:.6f}, σ² = {2*L2**2:.6f}, σ = {sqrt(2)*L2:.6f}")
sigma = sqrt(2) * L2
for bits in [10, 32, 64, 128]:
    log_n = bits * L2
    k_est = int(log_n / abs(EX) * 1.5)  # 1.5倍のマージン
    z = (-log_n - k_est * EX) / (sqrt(k_est) * sigma)
    # Φ(z) ≈ 1 for z >> 0
    print(f"    n ~ 2^{bits}: k={k_est}, z = {z:.2f} → P ≈ Φ({z:.2f})")

# ===== 5n+1 との比較 =====
print("\n" + "=" * 70)
print("パート9: 3n+1 vs 5n+1 の比較")
print("=" * 70)

EX_5 = L5 - 2 * L2
# 5n+1: I(0)
w5 = L5 / (L5 - L2)
t5_star = log(w5) / L2 - 1
I5_0 = -(t5_star * L5 - log(2**(t5_star + 1) - 1))

print(f"  3n+1:")
print(f"    E[X] = log(3/4) = {EX:.6f} < 0 (縮小)")
print(f"    I(0) = {I_0:.6f}")
print(f"    P(発散) ≤ exp(-{I_0:.6f}·k) → 発散は指数的に不可能")

print(f"\n  5n+1:")
print(f"    E[X] = log(5/4) = {EX_5:.6f} > 0 (発散)")
print(f"    I(0) = {I5_0:.6f}")
print(f"    t* = {t5_star:.6f} (< 0: 正しい)")
print(f"    P(収束) ~ exp(-{abs(I5_0):.6f}·k) → 収束は指数的に不可能")

print(f"\n  ★ 3n+1と5n+1の根本的違い:")
print(f"    3n+1: log(3/4) < 0 → 典型軌道は縮小")
print(f"    5n+1: log(5/4) > 0 → 典型軌道は発散")
print(f"    境界は an+1 で a = 4 (log(4/4) = 0)")

# ===== パート10: I(0)のさらなる簡約 =====
print("\n" + "=" * 70)
print("パート10: I(0) の代数的表現")
print("=" * 70)

# I(0) = -Λ(t*) = -t*·log3 + log(2^{t*+1} - 1)
# 2^{t*+1} = w* = log3/log(3/2)
# t* = log_2(log3/log(3/2)) - 1
# I(0) = -(log_2(w*)-1)·log3 + log(w*-1)
# = -log_2(w*)·log3 + log3 + log(w*-1)
# = log3 - log(w*)·log3/log2 + log(w*-1)

# w* - 1 = log3/log(3/2) - 1 = (log3 - log(3/2))/log(3/2) = log2/log(3/2)

w_minus_1 = L2 / (L3 - L2)
log_w = log(w_star)

print(f"  w* = log(3)/log(3/2) = {w_star:.10f}")
print(f"  w* - 1 = log(2)/log(3/2) = {w_minus_1:.10f}")
print(f"  log(w*) = log(log3/log(3/2)) = {log_w:.10f}")

I_0_form = L3 - L3 * log_w / L2 + log(w_minus_1)
print(f"\n  I(0) = log(3) - log(3)·log(log3/log(3/2))/log(2) + log(log2/log(3/2))")
print(f"       = log(3)·(1 - log(log3/log(3/2))/log(2)) + log(log2/log(3/2))")
print(f"       = {I_0_form:.10f}")
print(f"  検証: I(0) = {I_0:.10f} ✓")

# 数値的にきれいな関係はないか
print(f"\n  I(0) の数値的特徴:")
print(f"    I(0) = {I_0:.10f}")
print(f"    1/I(0) = {1/I_0:.6f}")
print(f"    I(0)/log(2) = {I_0/L2:.10f}")
print(f"    I(0)/log(3) = {I_0/L3:.10f}")
print(f"    I(0)/(log3-log2) = {I_0/(L3-L2):.10f}")
print(f"    exp(I(0)) = {exp(I_0):.10f}")

# ===== 最終まとめ =====
print("\n" + "=" * 70)
print("★★★ 最終結果まとめ ★★★")
print("=" * 70)

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ ランダムSyracuseモデル
  X_i = log(3) - v2_i · log(2),  v2_i ~ Geom(1/2)
  S_k = X_1 + ... + X_k

■ 基本統計量
  E[X] = log(3/4) = {EX:.10f}
  Var[X] = 2·(log2)² = {2*L2**2:.10f}

■ 対数モーメント母関数 (閉形式)
  Λ(t) = t·log(3) - log(2^{{t+1}} - 1),  t > -1

■ Cramér関数 (閉形式)
  I(x) = t*(x)·x - Λ(t*(x))
  t*(x) = log₂((log3-x)/(log(3/2)-x)) - 1
  定義域: x < log(3/2) ≈ {L3-L2:.6f}

■ ★ 発散確率の指数減衰レート (核心結果)
  I(0) = log(3)·(1 - log(log3/log(3/2))/log(2)) + log(log2/log(3/2))
       = {I_0:.10f}

  P(S_k > 0) ≤ exp(-k · I(0)) = exp(-{I_0:.6f} · k)

  Chernoff最適パラメータ: t* = {t_star:.6f}
  M_X(t*) = exp(-I(0)) = {exp(-I_0):.6f}

■ ★ 定量評価
  k=10:  P(発散) ≤ {exp(-10*I_0):.6e}
  k=50:  P(発散) ≤ {exp(-50*I_0):.6e}
  k=100: P(発散) ≤ {exp(-100*I_0):.6e}

■ ★ 有限時間到達
  到達ステップ数 ~ {1/abs(EX):.2f} · log(n)
  例: n ~ 2^64 → 約 {64*L2/abs(EX):.0f} Syracuse ステップ

■ 3n+1 vs 5n+1
  3n+1: I(0) = {I_0:.6f} (発散確率が指数減衰)
  5n+1: I(0) = {abs(I5_0):.6f} (収束確率が指数減衰)
  境界: an+1, a=4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
