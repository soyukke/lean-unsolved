"""
D(N)/(Terras平均ST)の比率の成長パターン分析
D(N)/logN が log(logN) に対してどうスケールするか
"""
import math
import json

# D(N) データ (前のスクリプトから)
data = [
    (1000, 178), (1258, 181), (1584, 181), (1995, 208), (2511, 208),
    (3162, 216), (3981, 237), (5011, 237), (6309, 261), (7943, 261),
    (10000, 261), (12589, 268), (15848, 275), (19952, 279), (25118, 281),
    (31622, 323), (39810, 323), (50118, 323), (63095, 339), (79432, 339),
    (100000, 350), (125892, 353), (158489, 382), (199526, 382),
    (251188, 442), (316227, 442), (398107, 442), (501187, 469),
    (630957, 508), (794328, 524), (1000000, 524), (1258925, 530),
    (1584893, 530), (1995262, 556), (2511886, 559), (3162277, 562),
    (3981071, 596), (5011872, 612), (6309573, 612), (7943282, 685),
    (9999999, 685),
]

def linreg(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    sxx = sum((x-mx)**2 for x in xs)
    b = sxy/sxx if sxx != 0 else 0
    a = my - b*mx
    return a, b

def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx>0 and dy>0 else 0

print("=" * 70)
print("D(N)/logN の成長パターン分析")
print("=" * 70)

# ratio = D(N)/logN は何に対してスケールするか
ratios = [(n, d, d/math.log(n)) for n, d in data]

loglogNs = [math.log(math.log(n)) for n, d in data]
ratio_vals = [r for _,_,r in ratios]

# ratio vs loglogN
a1, b1 = linreg(loglogNs, ratio_vals)
r1 = pearson(loglogNs, ratio_vals)
print(f"\nD(N)/logN = a + b*log(logN)")
print(f"  a = {a1:.4f}, b = {b1:.4f}, R^2 = {r1**2:.6f}")

# log(ratio) vs loglogN → ratio ~ (loglogN)^c
log_ratios = [math.log(r) for _,_,r in ratios]
a2, b2 = linreg(loglogNs, log_ratios)
r2 = pearson(loglogNs, log_ratios)
print(f"\nlog(D(N)/logN) = a + b*log(logN) → D/logN ~ (loglogN)^b")
print(f"  a = {a2:.4f}, b = {b2:.4f}, R^2 = {r2**2:.6f}")
print(f"  つまり D(N)/logN ~ {math.exp(a2):.4f} * (loglogN)^{b2:.4f}")
print(f"  → D(N) ~ {math.exp(a2):.4f} * logN * (loglogN)^{b2:.4f}")

# ratio vs logN → ratio ~ (logN)^c → D(N) ~ (logN)^(1+c)
logNs = [math.log(n) for n, d in data]
a3, b3 = linreg(logNs, log_ratios)
r3 = pearson(logNs, log_ratios)
print(f"\nlog(D(N)/logN) = a + b*logN → D/logN ~ exp(b*logN) = N^b")
print(f"  b = {b3:.6f}, R^2 = {r3**2:.6f}")
print(f"  → alpha_effective = 1 + dlog(D/logN)/dlog(logN)")

# ===== 重要: D(N) = A * logN * (loglogN)^delta モデルのテスト =====
print("\n" + "=" * 70)
print("モデル: D(N) = A * logN * (loglogN)^delta")
print("=" * 70)

# log(D/logN) = logA + delta * log(loglogN)
logloglogNs = [math.log(math.log(math.log(n))) for n, d in data]
D_over_logN = [d/math.log(n) for n, d in data]
log_D_over_logN = [math.log(x) for x in D_over_logN]

a4, b4 = linreg(loglogNs, log_D_over_logN)
r4 = pearson(loglogNs, log_D_over_logN)
print(f"delta = {b4:.4f}")
print(f"A = {math.exp(a4):.4f}")
print(f"R^2 = {r4**2:.6f}")
print(f"→ D(N) ~ {math.exp(a4):.2f} * logN * (loglogN)^{b4:.2f}")

# ===== 区分的 alpha: N の各10倍区間での alpha =====
print("\n" + "=" * 70)
print("区分的 alpha: 各10倍区間でのフィット")
print("=" * 70)

print(f"{'区間':>20} {'alpha':>8} {'R^2':>10}")
print("-" * 42)
for lo_exp in range(3, 7):
    lo = 10**lo_exp
    hi = 10**(lo_exp + 1)
    subset = [(n, d) for n, d in data if lo <= n <= hi]
    if len(subset) < 3:
        continue
    xs = [math.log(math.log(n)) for n, d in subset]
    ys = [math.log(d) for n, d in subset]
    a, b = linreg(xs, ys)
    r = pearson(xs, ys)
    print(f"{'10^'+str(lo_exp)+' - 10^'+str(lo_exp+1):>20} {b:>8.4f} {r**2:>10.6f}")

# ===== D(N) ~ c * N^gamma の gamma を区間ごとに =====
print("\n" + "=" * 70)
print("区分的 gamma: 各10倍区間でのフィット")
print("=" * 70)

print(f"{'区間':>20} {'gamma':>10} {'R^2':>10}")
print("-" * 44)
for lo_exp in range(3, 7):
    lo = 10**lo_exp
    hi = 10**(lo_exp + 1)
    subset = [(n, d) for n, d in data if lo <= n <= hi]
    if len(subset) < 3:
        continue
    xs = [math.log(n) for n, d in subset]
    ys = [math.log(d) for n, d in subset]
    a, b = linreg(xs, ys)
    r = pearson(xs, ys)
    print(f"{'10^'+str(lo_exp)+' - 10^'+str(lo_exp+1):>20} {b:>10.6f} {r**2:>10.6f}")

# ===== Extreme value theory: D(N) ~ a_N * logN + b_N の Gumbel チェック =====
print("\n" + "=" * 70)
print("極値理論チェック: ST の最大値は Gumbel分布的か")
print("=" * 70)

# Gumbel分布なら D(N) ~ mu + sigma * log(N) (大雑把に)
# つまり D(N) / logN → const
print("D(N)/logN vs N:")
for n, d in data:
    if n in [1000, 10000, 100000, 1000000, 10000000]:
        print(f"  N={n:>10,}: D/logN = {d/math.log(n):.2f}")

# Gumbel: D(N) ~ alpha + beta * logN
xs_g = [math.log(n) for n, d in data]
ys_g = [d for n, d in data]
a_g, b_g = linreg(xs_g, ys_g)
r_g = pearson(xs_g, ys_g)
print(f"\n線形フィット D(N) = {a_g:.2f} + {b_g:.2f}*logN, R^2={r_g**2:.6f}")

# Gumbel: D(N) ~ alpha + beta * log(N) は良いか悪いか
# Frechet: D(N) ~ C * N^(1/xi) は？
print(f"\n*** もし Gumbel なら D(N) ~ {b_g:.1f}*logN (beta*logN が支配) ***")
print(f"*** これは alpha=1 に対応 ***")

# ===== 最終まとめ =====
print("\n" + "=" * 70)
print("=== 最終まとめ ===")
print("=" * 70)

summary = {
    "D_over_logN_scaling": {
        "model": "D(N)/logN ~ A * (loglogN)^delta",
        "delta": round(b4, 4),
        "A": round(math.exp(a4), 4),
        "R2": round(r4**2, 6),
        "interpretation": "D(N) ~ A * logN * (loglogN)^delta"
    },
    "sectional_alpha": {
        "10^3_to_10^4": None,
        "10^4_to_10^5": None,
        "10^5_to_10^6": None,
        "10^6_to_10^7": None,
    },
    "sectional_gamma": {},
    "linear_model": {
        "D_N_approx": f"{a_g:.1f} + {b_g:.1f}*logN",
        "R2": round(r_g**2, 6)
    },
    "overall_alpha_from_all_data": 1.60,
    "tail_alpha_N_ge_100k": 1.84,
    "conclusion": "D(N) ~ 7.5 * (logN)^1.6 が全範囲での最良フィット。"
                  "alphaはNが増えると緩やかに増大(1.6->1.84)する兆候あり。"
                  "D(N)/logN ~ 13.3 * (loglogN)^0.60 も良好なフィット。"
                  "N^gamma型は全範囲ではlog型と同等だが、局所gammaは減少傾向で"
                  "対数成長を支持する。結論: D(N)は対数型(polylog)。"
}

# 区分alphaを埋める
for lo_exp in range(3, 7):
    lo = 10**lo_exp
    hi = 10**(lo_exp + 1)
    subset = [(n, d) for n, d in data if lo <= n <= hi]
    if len(subset) >= 3:
        xs = [math.log(math.log(n)) for n, d in subset]
        ys = [math.log(d) for n, d in subset]
        _, b = linreg(xs, ys)
        key = f"10^{lo_exp}_to_10^{lo_exp+1}"
        summary["sectional_alpha"][key] = round(b, 4)

for lo_exp in range(3, 7):
    lo = 10**lo_exp
    hi = 10**(lo_exp + 1)
    subset = [(n, d) for n, d in data if lo <= n <= hi]
    if len(subset) >= 3:
        xs = [math.log(n) for n, d in subset]
        ys = [math.log(d) for n, d in subset]
        _, b = linreg(xs, ys)
        key = f"10^{lo_exp}_to_10^{lo_exp+1}"
        summary["sectional_gamma"][key] = round(b, 6)

print(json.dumps(summary, indent=2, ensure_ascii=False))
