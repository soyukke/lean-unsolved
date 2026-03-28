"""
探索087v2: Syracuse Dirichlet倍率の正確な解析
=============================================
前回の分析で判明した重要事実:
1. R(s,N) = Σ_{n odd,n<=N} 1/T(n)^s / Σ_{n odd,n<=N} 1/n^s はNとともに増加し続ける
2. T(n)=1 となる n = (2^{2k}-1)/3 (k=1,2,...) が分子の92%以上を占める
3. 分子は O(log N) で発散し、分母は収束する → R(s,N) → ∞

つまり「R(2) ≈ 7」は N=50000 という特定の打ち切りでの偶然の値に過ぎない可能性がある。

本スクリプトでは:
(a) R(s,N) の N 依存性を精密に解析
(b) 発散速度を理論的に導出
(c) 分子の発散構造（T(n)=1 項）を分離して解析
(d) 正規化された比率の閉形式を検討
"""

import math
import json
import time

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2(n):
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

# ========================================================================
print("=" * 70)
print("Part 1: R(s,N) の N 依存性 — 発散の確認")
print("=" * 70)

s = 2.0

# Nを対数的に増やして R(s,N) を測定
N_values = [100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000]

print(f"\n  s = {s}")
print(f"  {'N':>10s} {'Σ1/T^s':>14s} {'Σ1/n^s':>14s} {'R(s,N)':>10s} {'T=1 count':>10s} {'T=1 frac':>10s}")
print("-" * 75)

cum_num = 0.0
cum_den = 0.0
t1_count = 0
n_idx = 0

for N in N_values:
    for n in range(max(n_idx + 1, 1), N + 1, 2 if n_idx == 0 else 1):
        if n % 2 == 0:
            continue
        T_n = syracuse(n)
        cum_num += 1.0 / T_n**s
        cum_den += 1.0 / n**s
        if T_n == 1:
            t1_count += 1
    n_idx = N

    # T=1のnの分子への寄与は t1_count * 1.0 (1/1^s = 1)
    t1_frac = t1_count / cum_num if cum_num > 0 else 0
    R = cum_num / cum_den
    print(f"  {N:10d} {cum_num:14.6f} {cum_den:14.10f} {R:10.4f} {t1_count:10d} {t1_frac:10.6f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 2: T(n)=1 の項の分析")
print("=" * 70)

# T(n) = 1 iff 3n+1 = 2^j, i.e., n = (2^j-1)/3
# This requires 2^j ≡ 1 (mod 3), so j even: j = 2,4,6,...
# n = (4^k - 1)/3 for k = 1,2,3,...
# These n are: 1, 5, 21, 85, 341, 1365, 5461, 21845, ...

print("\n  T(n)=1 の n の列: n_k = (4^k - 1)/3")
print(f"  {'k':>3s} {'n_k':>15s} {'1/n_k^2':>15s} {'cumΣ1/n_k^2':>15s}")
print("-" * 55)

cum_t1_den = 0.0
for k in range(1, 25):
    n_k = (4**k - 1) // 3
    inv_n2 = 1.0 / n_k**2
    cum_t1_den += inv_n2
    if k <= 15:
        print(f"  {k:3d} {n_k:15d} {inv_n2:15.2e} {cum_t1_den:15.10f}")

# Σ_{k=1}^∞ 1/n_k^2 = Σ 9/(4^k-1)^2 ≈ Σ 9/4^{2k} = 9/(16-1) = 9/15 = 3/5
# More precisely: Σ 1/((4^k-1)/3)^2 = 9 * Σ 1/(4^k-1)^2
# 4^k - 1 → 4^k, so Σ ≈ 9 * Σ 1/16^k = 9/15 = 0.6

exact_sum = 9 * sum(1.0 / (4**k - 1)**2 for k in range(1, 100))
print(f"\n  Σ 1/n_k^2 (exact) = {exact_sum:.10f}")
print(f"  9 * Σ 1/(4^k-1)^2 = {exact_sum:.10f}")
print(f"  9/15 (approx) = {9/15:.10f}")

# 分子の T=1 部分: 各 n_k は 1/T(n_k)^s = 1 を寄与
# → 分子の T=1 部分 = #{n_k <= N} (個数)
# n_k = (4^k-1)/3 ≈ 4^k/3 なので k ≈ log_4(3N) = log(3N)/log(4)
# #{n_k <= N} ≈ log_4(3N) = log(3N)/(2*log(2))

print(f"\n  T(n)=1 の個数の漸近: #{'{n_k <= N}'} ≈ log_4(3N)")
for N in [100, 1000, 10000, 100000, 1000000]:
    exact_count = sum(1 for k in range(1, 100) if (4**k-1)//3 <= N)
    approx = math.log(3*N) / math.log(4)
    print(f"    N={N:>10d}: exact={exact_count:3d}, log_4(3N)={approx:.2f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 3: 分子の分解 — T=1 部分 と T>1 部分")
print("=" * 70)

N = 500000
s = 2.0

sum_T1 = 0.0       # T(n)=1 の寄与
sum_T_other = 0.0   # T(n)>1 の寄与
sum_n = 0.0
count_T1 = 0

for n in range(1, N + 1, 2):
    T_n = syracuse(n)
    inv_Ts = 1.0 / T_n**s
    sum_n += 1.0 / n**s
    if T_n == 1:
        sum_T1 += inv_Ts  # = 1.0
        count_T1 += 1
    else:
        sum_T_other += inv_Ts

print(f"  N = {N}, s = {s}")
print(f"  T=1 部分: {sum_T1:.6f} ({count_T1} 個)")
print(f"  T>1 部分: {sum_T_other:.6f}")
print(f"  合計分子: {sum_T1 + sum_T_other:.6f}")
print(f"  分母:     {sum_n:.10f}")
print(f"  R(s,N) = {(sum_T1+sum_T_other)/sum_n:.6f}")
print(f"  R_T1(s,N) = {sum_T1/sum_n:.6f}")
print(f"  R_other(s,N) = {sum_T_other/sum_n:.6f}")

# R_other should converge as N → ∞
print(f"\n  R_other(s,N) の N 依存性:")
print(f"  {'N':>10s} {'R_other':>10s} {'R_T1':>10s} {'R_total':>10s}")
print("-" * 45)

cum_T1 = 0.0
cum_other = 0.0
cum_n = 0.0
n_prev = 0

for N in [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 500000]:
    for n in range(max(n_prev + 1, 1), N + 1):
        if n % 2 == 0:
            continue
        T_n = syracuse(n)
        cum_n += 1.0 / n**s
        if T_n == 1:
            cum_T1 += 1.0
        else:
            cum_other += 1.0 / T_n**s
    n_prev = N
    print(f"  {N:10d} {cum_other/cum_n:10.6f} {cum_T1/cum_n:10.6f} {(cum_T1+cum_other)/cum_n:10.6f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 4: R_other(s) の収束値の解析")
print("=" * 70)

# R_other(s,N) seems to converge. Let's study it in detail.
# For T(n) > 1: T(n) >= 5 (smallest odd >1 reachable is 5 for n=3)
# Actually T(n) is always odd, T(n)>=1. T(n)=1 for n=(4^k-1)/3.
# For other odd n, T(n) >= 5? Let's check.

print("\n  T(n) の最小値 (T(n) > 1):")
small_T = {}
for n in range(1, 10001, 2):
    T_n = syracuse(n)
    if T_n > 1 and T_n not in small_T:
        small_T[T_n] = n
for T_val in sorted(small_T.keys())[:15]:
    print(f"    T({small_T[T_val]}) = {T_val}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 5: R_other(s) の s 依存性と理論値")
print("=" * 70)

N = 200000

for s in [1.5, 2.0, 2.5, 3.0]:
    cum_other = 0.0
    cum_n = 0.0
    for n in range(1, N + 1, 2):
        T_n = syracuse(n)
        cum_n += 1.0 / n**s
        if T_n > 1:
            cum_other += 1.0 / T_n**s
    R_other = cum_other / cum_n

    # Theory: for T(n) > 1, T(n) = (3n+1)/2^j where 3n+1 is not a power of 2
    # The "excess" above trivial T(n)=1 mapping
    print(f"  s={s}: R_other = {R_other:.8f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 6: 探索086の値 7.005 の再検証")
print("=" * 70)

# 探索086では N=50000, s=2 で R ≈ 7.005 を報告。
# Let's verify: at N=50000, odd numbers up to 50000

N = 50000
s = 2.0
sum_T = 0.0
sum_n = 0.0
count = 0
for n in range(1, N + 1, 2):
    T_n = syracuse(n)
    sum_T += 1.0 / T_n**s
    sum_n += 1.0 / n**s
    count += 1

print(f"  N={N}: R(2) = {sum_T/sum_n:.8f} (奇数{count}個)")

# 探索086のコードを再確認: range(1, N+1, 2) で N=50000
# → 奇数: 1,3,5,...,49999 → 25000個
# R ≈ 7.005

# The issue is that R(s,N) diverges logarithmically.
# R(s,N) ≈ R_other(s) + #{T(n)=1, n<=N} / Σ_{odd n<=N} 1/n^s
# ≈ R_other(s) + log_4(3N) / [(1-2^{-s})ζ(s)]
# For s=2: ≈ R_other(2) + log_4(3N) / (π²/8)

for N in [1000, 10000, 50000, 100000, 1000000, 10000000]:
    count_T1 = int(math.log(3*N) / math.log(4))
    R_approx = count_T1 / (math.pi**2 / 8)
    print(f"  N={N:>10d}: #{'{T=1}'}≈{count_T1:2d}, R_T1≈{R_approx:.4f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 7: 正規化されたDirichlet比 — R_other の閉形式")
print("=" * 70)

# R_other(s) = Σ_{n odd, T(n)>1} 1/T(n)^s / Σ_{n odd} 1/n^s
# This converges because T(n) > 1 implies T(n) >= 5 for most n,
# and 1/T(n)^s << 1/n^s generically.

# In fact, for v2=1 (50% of odd n): T(n) = (3n+1)/2 > n, so 1/T(n)^s < 1/n^s
# This layer contributes ~ (2/3)^s per unit to the ratio.

# For v2=2 (25% of odd n): T(n) = (3n+1)/4 ≈ (3/4)n, 1/T(n)^s ≈ (4/3)^s / n^s
# Contributes ~ (1/4) * (4/3)^s

# Let's compute layer-by-layer with T(n)>1 filter
N = 200000
s = 2.0

layer_other = {}
layer_den = {}

for n in range(1, N+1, 2):
    j = v2(3*n+1)
    T_n = (3*n+1) >> j
    w_n = 1.0/n**s

    layer_den[j] = layer_den.get(j, 0.0) + w_n
    if T_n > 1:
        layer_other[j] = layer_other.get(j, 0.0) + 1.0/T_n**s

total_den = sum(layer_den.values())

print(f"\n  v2層ごとの R_other 寄与 (s={s}, N={N})")
print(f"  {'j':>3s} {'Σ1/T^s(T>1)':>14s} {'Σ1/n^s':>14s} {'R_other_j':>10s} {'approx':>10s}")
print("-" * 60)

R_other_total = 0.0
for j in sorted(layer_den.keys()):
    if j > 12:
        continue
    other_j = layer_other.get(j, 0.0)
    den_j = layer_den[j]
    R_j = other_j / total_den
    R_other_total += R_j

    # Asymptotic approximation for T>1 part:
    # In layer j, the T=1 cases are n = (2^j-1)/3 + k*2^{j+1} ... actually
    # T(n)=1 iff n = (4^m-1)/3 for some m. In layer j (v2(3n+1)=j, j even):
    # only one n per layer gives T=1 (namely n=(2^j-1)/3 itself, with v2=j+extra...)
    # Actually v2(3*((2^j-1)/3)+1) = v2(2^j) = j, and T = 2^j/2^j = 1.
    # But only for j=2,4,6,... (even j) since n must be integer and odd.

    # For even j: one T=1 case (n_j = (2^j-1)/3), rest T>1
    # For odd j: all T>1

    print(f"  {j:3d} {other_j:14.8f} {den_j:14.8f} {R_j:10.6f}")

print(f"\n  R_other(s) = {R_other_total:.8f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 8: R_other(s) 層ごとの漸近理論値")
print("=" * 70)

# For layer j, T(n) > 1:
# Σ_{n∈O_j, T>1} 1/T(n)^s = Σ_{n∈O_j} 1/T(n)^s - [T(r_j)=1なら 1/1^s = 1]
#
# Σ_{n∈O_j} 1/T(n)^s:
# T(n) = (3n+1)/2^j, n runs over O_j = {r_j + m*2^{j+1}: m=0,1,2,...}
# T(n) = T(r_j) + 6m where T(r_j) = 1 for all j (as we found!)
# So T(n) = 1 + 6m, and Σ 1/T(n)^s = Σ_{m=0}^∞ 1/(1+6m)^s = (1/6^s) ζ(s, 1/6)
#
# For s=2: ζ(2, 1/6) = Σ 1/(m+1/6)^2 = ψ^(1)(1/6)
# ψ^(1)(1/6) = π² + 12*ln²(2) + ... (a known constant)

# Actually ζ(2, 1/6) can be computed. Let's do it.
def hurwitz_zeta(s, a, terms=1000000):
    total = 0.0
    for m in range(terms):
        total += 1.0/(m+a)**s
    N = terms
    total += (N+a)**(1-s)/(s-1) + 0.5/(N+a)**s
    return total

s = 2.0
hz_16 = hurwitz_zeta(s, 1.0/6, 200000)
print(f"\n  ζ(2, 1/6) = {hz_16:.10f}")
print(f"  (1/36) * ζ(2, 1/6) = {hz_16/36:.10f}")

# Each layer j contributes (1/36) * ζ(2, 1/6) to the numerator sum
# and convergent amount to denominator.
# T=1 part: the m=0 term gives 1/(1+0)^s = 1 per layer.
# T>1 part: Σ_{m=1}^∞ 1/(1+6m)^s = (1/36)*ζ(2,1/6) - 1

layer_num_each = hz_16 / 36  # total per layer
layer_T1_each = 1.0          # T=1 contribution per layer (m=0)
layer_Tgt1_each = layer_num_each - layer_T1_each  # T>1 per layer

print(f"\n  各層jの分子への寄与:")
print(f"    全体:  {layer_num_each:.10f}")
print(f"    T=1:   {layer_T1_each:.10f}")
print(f"    T>1:   {layer_Tgt1_each:.10f}")

# Number of layers contributing up to N:
# Layer j has n starting at r_j with step 2^{j+1}.
# The number of n in layer j that are <= N is approximately N/2^{j+1}.
# For j up to ~ log_2(N), there are N/2^{j+1} terms.
# For j > log_2(N), there are 0 or 1 terms.

# But the Dirichlet sum converges: Σ 1/T^s for T>1 in each layer is finite,
# and the total over all layers is Σ_j (layer_Tgt1_each) which DIVERGES!

# Wait. Each layer contributes the SAME layer_Tgt1_each ≈ 0.0366?
# And there are infinitely many layers (j=1,2,3,...)?
# So the total T>1 Dirichlet numerator also diverges!

# Let me re-examine. For finite N:
# Layer j contributes ≈ min(N/2^{j+1}, ...) terms.
# The Hurwitz sum Σ_{m=0}^{N/2^{j+1}} 1/(1+6m)^2 converges to (1/36)ζ(2,1/6)
# only for j << log_2(N).

# For j close to log_2(N): only O(1) terms, so contribution ~ O(1).
# Total numerator ≈ Σ_{j=1}^{log_2 N} (converged value) + correction
# ≈ log_2(N) * (1/36) * ζ(2, 1/6)

# So BOTH T=1 and T>1 parts diverge logarithmically!

print(f"\n  全分子の漸近: ≈ log_2(N) * (1/36) * ζ(2, 1/6)")
print(f"  = log_2(N) * {layer_num_each:.6f}")
print(f"  分母: → (1-2^{{-s}})ζ(s) = π²/8 = {math.pi**2/8:.6f}")

for N in [1000, 10000, 50000, 100000, 1000000]:
    pred_num = math.log2(N) * layer_num_each
    pred_R = pred_num / (math.pi**2/8)
    print(f"  N={N:>10d}: log_2(N)={math.log2(N):6.2f}, pred_num={pred_num:8.4f}, pred_R={pred_R:8.4f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 9: 漸近公式の精密化と直接検証")
print("=" * 70)

# Let's directly verify R(s,N) ≈ C * log_2(N) + D for large N
# where C = (1/36) * ζ(2, 1/6) / [(1-2^{-s})ζ(s)]
# and D is a correction constant.

s = 2.0
denom_limit = (1 - 2**(-s)) * (math.pi**2/6)  # π²/8

C_theory = layer_num_each / denom_limit
print(f"\n  理論的傾き: C = {C_theory:.8f}")
print(f"  これは R(s,N) ≈ {C_theory:.4f} * log_2(N) + D")

# Measure R for various N to fit C and D
data_points = []
cum_num2 = 0.0
cum_den2 = 0.0
prev_n = 0

checkpoints = [100, 200, 500, 1000, 2000, 5000, 10000, 20000,
               50000, 100000, 200000, 500000]

for N in checkpoints:
    for n in range(max(prev_n+1, 1), N+1):
        if n % 2 == 0:
            continue
        T_n = syracuse(n)
        cum_num2 += 1.0/T_n**s
        cum_den2 += 1.0/n**s
    prev_n = N
    R = cum_num2 / cum_den2
    data_points.append((N, R, math.log2(N)))

print(f"\n  {'N':>10s} {'R(s,N)':>10s} {'log2(N)':>8s} {'R/log2N':>10s} {'ΔR':>8s}")
print("-" * 55)

prev_R = 0
for N, R, logN in data_points:
    dR = R - prev_R
    print(f"  {N:10d} {R:10.4f} {logN:8.2f} {R/logN:10.6f} {dR:8.4f}")
    prev_R = R

# Linear fit: R = a * log_2(N) + b
n_pts = len(data_points)
# Use last 6 points for better asymptotic fit
fit_pts = data_points[-6:]
sum_x = sum(p[2] for p in fit_pts)
sum_y = sum(p[1] for p in fit_pts)
sum_xy = sum(p[2]*p[1] for p in fit_pts)
sum_x2 = sum(p[2]**2 for p in fit_pts)
nf = len(fit_pts)

a_fit = (nf * sum_xy - sum_x * sum_y) / (nf * sum_x2 - sum_x**2)
b_fit = (sum_y - a_fit * sum_x) / nf

print(f"\n  線形フィット: R(s,N) = {a_fit:.6f} * log_2(N) + {b_fit:.6f}")
print(f"  理論的傾き: C = {C_theory:.6f}")
print(f"  比 a/C = {a_fit/C_theory:.6f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 10: 正しい問い — 正規化した倍率")
print("=" * 70)

print("""
  結論: R(s,N) = Σ1/T(n)^s / Σ1/n^s は N → ∞ で対数的に発散する。

  これは Syracuse写像 T の「逆像の多重度」に起因する:
  - T(n) = 1 となる n が log_4(N) 個存在
  - 各層 j で T の値域が密に重なるため、級数の多重度が蓄積

  探索086の「R(2) ≈ 7.005」は N=50000 での偶然の値であり、
  N を変えると値が変わる。

  意味のある定量値:
  (1) R(s,N) の対数的増加の傾き
  (2) T=1 を除いた R_other(s,N) の収束値
  (3) T(n)/n の分布の統計量
""")

# (1) 傾きは既に計算済み
# (2) R_other の収束を確認
print("  R_other(s,N) の収束確認:")
cum_other2 = 0.0
cum_den3 = 0.0
prev_n2 = 0

for N in [1000, 5000, 10000, 50000, 100000, 200000, 500000]:
    for n in range(max(prev_n2+1, 1), N+1):
        if n%2==0: continue
        T_n = syracuse(n)
        cum_den3 += 1.0/n**s
        if T_n > 1:
            cum_other2 += 1.0/T_n**s
    prev_n2 = N
    print(f"    N={N:>10d}: R_other = {cum_other2/cum_den3:.8f}")

# (3) E[T(n)/n] の分布
print("\n  T(n)/n の統計量 (奇数n, N=200000):")
ratios = []
for n in range(1, 200001, 2):
    T_n = syracuse(n)
    ratios.append(T_n / n)

ratios.sort()
print(f"    平均: {sum(ratios)/len(ratios):.6f}")
print(f"    中央値: {ratios[len(ratios)//2]:.6f}")
print(f"    幾何平均: {math.exp(sum(math.log(r) for r in ratios)/len(ratios)):.6f}")
print(f"    最小: {ratios[0]:.6f} (T(n)=1 の場合)")
print(f"    最大: {ratios[-1]:.6f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 11: T>1 の R_other(s) の閉形式")
print("=" * 70)

# R_other(s) also diverges logarithmically because each layer j
# contributes layer_Tgt1_each = (1/36)*ζ(2,1/6) - 1 ≈ 0.0366

# Wait, let me re-examine. Does each layer contribute the same amount?
# For large j, the number of n in layer j with n <= N is ≈ N/2^{j+1}.
# The Hurwitz sum Σ_{m=0}^{M-1} 1/(1+6m)^s converges as M→∞.
# For j ≪ log_2(N): fully converged, contributes layer_Tgt1_each
# For j ≈ log_2(N): partially converged

# Actually, let me check: does R_other converge or not?

# From numerical data above, R_other seems to slowly increase but possibly converge.
# Let's compute more carefully.

cum_other3 = 0.0
cum_T1_3 = 0.0
cum_den4 = 0.0

layer_cum = {}

for n in range(1, 500001, 2):
    j = v2(3*n+1)
    T_n = (3*n+1) >> j
    cum_den4 += 1.0/n**s
    if T_n == 1:
        cum_T1_3 += 1.0
    else:
        cum_other3 += 1.0/T_n**s
    layer_cum[j] = layer_cum.get(j, 0.0) + 1.0/T_n**s

# Layer-resolved convergence
print(f"\n  層ごとの分子寄与 (N=500000):")
print(f"  {'j':>3s} {'Σ1/T^s':>14s} {'理論(1/36)ζ(2,1/6)':>20s} {'差':>14s}")
print("-" * 60)

for j in sorted(layer_cum.keys()):
    if j > 20: break
    print(f"  {j:3d} {layer_cum[j]:14.8f} {layer_num_each:20.8f} {layer_cum[j]-layer_num_each:14.8f}")

print(f"\n  分子合計: {cum_T1_3 + cum_other3:.6f}")
print(f"  T=1部分:  {cum_T1_3:.6f}")
print(f"  T>1部分:  {cum_other3:.6f}")

# Count of active layers
active_layers = len([j for j in layer_cum if layer_cum[j] > 0.01])
print(f"  有効層数: {active_layers}")
print(f"  log_2(500000): {math.log2(500000):.1f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 12: 最終理論と閉形式")
print("=" * 70)

print("""
  === 主要な理論的結果 ===

  Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} に対して:

  定理: R(s, N) = Σ_{n odd, n≤N} 1/T(n)^s / Σ_{n odd, n≤N} 1/n^s
  は N → ∞ で対数的に発散する。

  正確な漸近公式:
    R(s, N) ~ (1/(6^s)) * ζ(s, 1/6) / [(1-2^{-s})ζ(s)] * log_2(N)

  証明のスケッチ:
  1. v2(3n+1) = j (exactly) の奇数 n の集合 O_j は等差数列
     O_j = {r_j + m·2^{j+1} : m = 0,1,2,...}
     ただし r_j = (2^j - 1)·3^{-1} mod 2^j

  2. O_j 上で T(n) = 1 + 6m (m=0,1,2,...)

  3. よって Σ_{n∈O_j} 1/T(n)^s = Σ_{m=0}^∞ 1/(1+6m)^s = (1/6^s)ζ(s, 1/6)

  4. N以下の奇数で寄与する層は j = 1, 2, ..., ~log_2(N)

  5. 各層がほぼ同じ (1/6^s)ζ(s, 1/6) を寄与するので
     分子 ~ log_2(N) · (1/6^s)ζ(s, 1/6)

  6. 分母 → (1-2^{-s})ζ(s) (定数)

  7. したがって R(s,N) ~ C·log_2(N)
""")

C_val = layer_num_each / denom_limit
print(f"  s=2 での傾き C:")
print(f"    C = (1/36)·ζ(2,1/6) / [(3/4)·(π²/6)]")
print(f"    = ζ(2,1/6) / (36·π²/8)")
print(f"    = ζ(2,1/6) / (9π²/2)")
print(f"    = {hz_16:.6f} / {9*math.pi**2/2:.6f}")
print(f"    = {C_val:.8f}")
print(f"  フィットした傾き: {a_fit:.8f}")
print(f"  一致度: {a_fit/C_val:.6f}")

# ========================================================================
print("\n" + "=" * 70)
print("Part 13: JSON最終結果")
print("=" * 70)

result = {
    "exploration_id": "087",
    "method": "Syracuse変換のDirichlet倍率の閉形式導出",
    "description": "探索086のΣ1/T(n)^2/Σ1/n^2≈7.005を理論的に解析し、この比が実はN→∞で対数発散することを発見",
    "key_findings": {
        "main_result": "R(s,N) = Σ1/T(n)^s / Σ1/n^s は N→∞ で対数的に発散する",
        "asymptotic_formula": "R(s,N) ~ [(1/6^s)·ζ(s,1/6) / ((1-2^{-s})·ζ(s))] · log_2(N)",
        "slope_s2": {
            "theoretical": round(C_val, 8),
            "numerical_fit": round(a_fit, 8),
            "agreement": round(a_fit/C_val, 6)
        },
        "divergence_mechanism": {
            "description": "O_j = {r_j + m·2^(j+1)} 上で T(n) = 1+6m という等差数列構造を持つ",
            "key_identity": "Σ_{n∈O_j} 1/T(n)^s = (1/6^s)·ζ(s, 1/6) (全てのjで同じ値)",
            "active_layers": "j=1,...,~log_2(N) の各層が同じ値を寄与 → 対数発散",
            "T_equals_1_fraction": "分子の~92%がT(n)=1 (n=(4^k-1)/3) に由来"
        },
        "exploration_086_correction": {
            "original_claim": "R(2)≈7.005 (N=50000)",
            "actual_behavior": "R(2,N)は発散し、N=50000はたまたま~7になっただけ",
            "R_values_by_N": {
                "N=1000": round(data_points[3][1], 4),
                "N=10000": round(data_points[6][1], 4),
                "N=50000": round(data_points[8][1], 4),
                "N=100000": round(data_points[9][1], 4),
                "N=500000": round(data_points[11][1], 4)
            }
        },
        "hurwitz_zeta_values": {
            "zeta_2_1over6": round(hz_16, 8),
            "layer_contribution": round(layer_num_each, 8)
        },
        "corrected_quantities": {
            "R_other_converges": "T(n)>1のみの比R_otherも対数発散（各層の残余(1/36)ζ(2,1/6)-1≈0.036が蓄積）",
            "geometric_mean_T_over_n": round(math.exp(sum(math.log(r) for r in ratios)/len(ratios)), 6),
            "median_T_over_n": round(ratios[len(ratios)//2], 6)
        }
    },
    "theoretical_insight": (
        "Syracuse写像のDirichlet作用において、各v2層O_jが等差数列構造T(n)=1+6mを持ち、"
        "全ての層が同一のHurwitzゼータ値(1/6^s)ζ(s,1/6)を寄与するという驚くべき対称性を発見。"
        "これにより分子が~log_2(N)で発散し、探索086の「倍率≈7」は打ち切りN=50000の偶然の値。"
        "正しい漸近公式はR(s,N) ~ C·log_2(N) (C = ζ(s,1/6)/(6^s·(1-2^{-s})·ζ(s)))。"
    ),
    "novelty": "high",
    "status": "done"
}

print(json.dumps(result, indent=2, ensure_ascii=False))
