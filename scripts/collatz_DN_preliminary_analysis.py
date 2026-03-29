"""
D(N) 予備分析: 既知のrecord holderデータからαの収束を調べる

OEIS A006877 / A006884 の既知データ + N=10^7までの実計算データを使用
Oliveira e Silva のデータも利用
"""

import math
import json

# 既知の record holders (n, total_stopping_time)
# OEIS A006877: numbers with record total stopping times
# OEIS A006884: corresponding stopping times
# Source: computed + known references

# N=10^7 までは先行計算済み
# D(10^k) の値 (先行スクリプトから)
known_DN = {
    3: 178,     # D(10^3)
    4: 261,     # D(10^4)
    5: 350,     # D(10^5)
    6: 524,     # D(10^6)
    7: 685,     # D(10^7) (from earlier script: 9999999 -> 685)
}

# 既知の record holder (n, ST) for larger n
# Collatz record delays from various sources
known_records_large = [
    # n, total stopping time
    (1, 0),
    (2, 1),
    (3, 7),
    (6, 8),
    (7, 16),
    (9, 19),
    (18, 20),
    (25, 23),
    (27, 111),
    (54, 112),
    (73, 115),
    (97, 118),
    (129, 121),
    (171, 124),
    (231, 127),
    (313, 130),
    (327, 143),
    (649, 144),
    (703, 170),
    (871, 178),
    (1161, 181),
    (2223, 182),
    (2463, 208),
    (2919, 216),
    (3711, 237),
    (6171, 261),
    (10971, 267),
    (13255, 275),
    (17647, 278),
    (23529, 281),
    (26623, 307),
    (34239, 310),
    (35655, 323),
    (52527, 339),
    (77031, 350),
    (106239, 353),
    (142587, 374),
    (156159, 382),
    (216367, 385),
    (230631, 442),
    (410011, 448),
    (511935, 469),
    (626331, 508),
    (837799, 524),
    (1117065, 527),
    (1501353, 530),
    (1723519, 556),
    (2298025, 559),
    (3064033, 562),
    (3542887, 583),
    (3732423, 596),
    (5649499, 612),
    (6649279, 664),
    (8400511, 685),
]

print("=" * 90)
print("D(N) 予備分析: alpha の収束")
print("=" * 90)

# D(N) テーブルの再構築
# record holders から D(N) を構築
# D(N) = max{ST(n) : n <= N}
# record holders が ST の単調増加列なので、D(N) = last record <= N の ST

print("\n=== Record holders ===")
print(f"{'n':>12} {'ST':>6} {'logn':>8} {'loglogn':>8} {'ST/(logn)^1.5':>16} {'ST/(logn)^1.6':>16} {'ST/(logn)^2':>14}")
print("-" * 96)
for n, st in known_records_large:
    if n < 10:
        continue
    ln = math.log(n)
    lln = math.log(ln)
    print(f"{n:>12,} {st:>6} {ln:>8.3f} {lln:>8.4f} {st/ln**1.5:>16.4f} {st/ln**1.6:>16.4f} {st/ln**2:>14.4f}")

# alpha 推定: record holder ペアから
print("\n=== Record holder ペアからの alpha 推定 ===")
print("(連続record holderペアで alpha = log(ST2/ST1) / log(logn2/logn1))")
print(f"{'n1':>12} {'n2':>12} {'alpha':>10}")
print("-" * 36)

filtered = [(n, st) for n, st in known_records_large if n >= 100]
pair_alphas = []
for i in range(1, len(filtered)):
    n1, st1 = filtered[i-1]
    n2, st2 = filtered[i]
    ln1 = math.log(n1)
    ln2 = math.log(n2)
    if st2 > st1 and ln2 > ln1:
        alpha_est = math.log(st2/st1) / math.log(ln2/ln1)
        pair_alphas.append((n2, alpha_est))
        if n1 > 1000:
            print(f"{n1:>12,} {n2:>12,} {alpha_est:>10.4f}")

# 移動平均
window = 5
sm = []
for i in range(window, len(pair_alphas)):
    vals = [a[1] for a in pair_alphas[i-window:i]]
    sm.append((pair_alphas[i][0], sum(vals)/len(vals)))

if sm:
    print(f"\n移動平均 (window={window}):")
    for n, a in sm:
        print(f"  n ~ {n:>12,}: alpha ~ {a:.4f}")

# D(10^k) からの alpha
print("\n\n=== D(10^k) テーブルからの alpha 推定 ===")
dk = known_DN
dk_keys = sorted(dk.keys())

print(f"{'k':>4} {'D(10^k)':>10} {'logN':>10} {'log(logN)':>10} {'log(D)':>10}")
print("-" * 50)
for k in dk_keys:
    d = dk[k]
    logN = k * math.log(10)
    print(f"{k:>4} {d:>10} {logN:>10.3f} {math.log(logN):>10.4f} {math.log(d):>10.4f}")

# 回帰: log(D) = log(C) + alpha * log(logN)
xs = [math.log(k * math.log(10)) for k in dk_keys]
ys = [math.log(dk[k]) for k in dk_keys]

n = len(xs)
mx = sum(xs)/n; my = sum(ys)/n
sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
sxx = sum((x-mx)**2 for x in xs)
b = sxy/sxx; a = my - b*mx
alpha_fit = b
C_fit = math.exp(a)

print(f"\n回帰結果 (k={dk_keys[0]}..{dk_keys[-1]}):")
print(f"  alpha = {alpha_fit:.4f}")
print(f"  C = {C_fit:.4f}")

# Jackknife: 1点を除いてフィット
print(f"\nJackknife alpha:")
for exclude_k in dk_keys:
    sub_keys = [k for k in dk_keys if k != exclude_k]
    sub_xs = [math.log(k * math.log(10)) for k in sub_keys]
    sub_ys = [math.log(dk[k]) for k in sub_keys]
    n2 = len(sub_xs)
    mx2 = sum(sub_xs)/n2; my2 = sum(sub_ys)/n2
    sxy2 = sum((sub_xs[i]-mx2)*(sub_ys[i]-my2) for i in range(n2))
    sxx2 = sum((x-mx2)**2 for x in sub_xs)
    b2 = sxy2/sxx2
    print(f"  除外 k={exclude_k}: alpha = {b2:.4f}")

# alpha の理論的意味
print("\n" + "=" * 90)
print("alpha の理論的分析")
print("=" * 90)

# 確率モデル: ST(n) ~ Geometric(p) sum
# p = log(2)/(log(2)+log(3)) が偶奇の確率
# E[ST] ~ logn / log(4/3)
# ST の分布: 正規近似で sigma ~ C * sqrt(logn)
# max of N iid ~ 平均 + sigma * sqrt(2 * log N)
# => D(N) ~ E[ST(N)] + c * sqrt(logN) * sqrt(2 * logN)
#          ~ a*logN + b*logN  (if sigma ~ sqrt(logN))
# This gives D(N) ~ c*logN, not (logN)^alpha

# しかし ST は iid でない + 尾部が指数減衰 => EVT の Gumbel class
# max ~ mean + sigma * (logN - loglogN + ...) / lambda
# lambda = 指数減衰率 0.0735

# P(ST > t) ~ exp(-0.0735 * t) (既知)
# max of N: P(max <= t) = (1 - exp(-0.0735*t))^N
# Setting this = 1/2: t ~ log(N) / 0.0735
# => D(N) ~ logN / 0.0735 ??? This gives D(N) ~ 13.6 * logN

lambda_exp = 0.0735
for k in dk_keys:
    N = 10**k
    logN = math.log(N)
    predicted_gumbel = logN / lambda_exp
    actual = dk[k]
    ratio = actual / predicted_gumbel
    print(f"  k={k}: Gumbel予測 = {predicted_gumbel:.1f}, 実測 = {actual}, 比 = {ratio:.4f}")

# EVT: Gumbel mode = F^{-1}(1 - 1/N) where F is CDF of ST
# If P(ST > t) ~ exp(-lambda*t), then F^{-1}(1-1/N) = log(N)/lambda
# Gumbel mean = mode + gamma_euler / lambda
gamma_euler = 0.5772
print(f"\nGumbel分布の詳細:")
print(f"  scale = 1/lambda = {1/lambda_exp:.2f}")
print(f"  mode = log(N)/lambda")
print(f"  mean = mode + gamma/lambda = log(N)/lambda + {gamma_euler/lambda_exp:.2f}")

for k in dk_keys:
    N = 10**k
    logN = math.log(N)
    mode = logN / lambda_exp
    gumbel_mean = mode + gamma_euler / lambda_exp
    actual = dk[k]
    print(f"  k={k}: mode={mode:.1f}, Gumbel_mean={gumbel_mean:.1f}, actual={actual}, ratio={actual/gumbel_mean:.4f}")

# しかし P(ST>t)~exp(-0.0735t) は近似。実際は ST は n に依存。
# より正確な分析: 独立でないため直接EVTは使えない

# D(N) ~ (logN)^alpha で alpha > 1 なら superlogarithmic
# alpha = 1 なら D(N) ~ C * logN (Gumbel consistent)

print(f"\n\n=== 結論 ===")
print(f"D(10^k) からのフィット: alpha = {alpha_fit:.4f}")
print(f"Gumbel EVT予測 (指数減衰尾部): D(N) ~ logN / 0.0735 => alpha = 1")
print(f"ただし実測データは alpha > 1 を示唆")
print(f"これは ST 尾部の指数減衰が純粋でない（サブ指数的な補正あり）ことを意味する可能性")

# alpha の N 依存性の予測
print(f"\n=== alpha の N 依存性分析 ===")
# D(10^k, 10^(k+1)) のペアからの instantaneous alpha
print(f"{'k1-k2':>8} {'alpha_inst':>12}")
for i in range(len(dk_keys)-1):
    k1, k2 = dk_keys[i], dk_keys[i+1]
    d1, d2 = dk[k1], dk[k2]
    lN1 = k1 * math.log(10)
    lN2 = k2 * math.log(10)
    alpha_inst = math.log(d2/d1) / math.log(lN2/lN1)
    print(f"  {k1}-{k2}: {alpha_inst:>12.4f}")

print(f"\nもし alpha が増大傾向なら、真の漸近的 alpha はさらに大きい可能性")
print(f"もし alpha が減少傾向なら、alpha ~ 1 (対数的) に収束する可能性")
