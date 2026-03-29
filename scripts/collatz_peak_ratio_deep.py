"""
ピーク/n比の深堀解析
- record holderのMersenne的構造 (2^k - 1 型)
- trailing onesと peak ratio の精密な関係
- 対数テールの累積分布（指数関数的減衰 vs べき的減衰）
- ブロック最大値の複数ブロックサイズ比較
"""

import math
import time
import json
from collections import defaultdict, Counter

def syracuse(n):
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def collatz_peak(n):
    peak = n
    current = n
    steps = 0
    while current != 1 and steps < 100000:
        current = syracuse(current)
        if current > peak:
            peak = current
        steps += 1
    return peak

def trailing_ones(n):
    c = 0
    while n & 1:
        n >>= 1
        c += 1
    return c

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def std(lst):
    if len(lst) < 2:
        return 0.0
    m = mean(lst)
    return math.sqrt(sum((x - m)**2 for x in lst) / len(lst))

def median_val(lst):
    s = sorted(lst)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0

# ========================================
# Analysis A: Mersenne型 n = 2^k - 1 の peak/n
# ========================================
def analysis_mersenne():
    print("=== Analysis A: Mersenne型 n=2^k-1 の peak ratio ===")
    results = []
    for k in range(2, 30):
        n = (1 << k) - 1  # 2^k - 1
        pk = collatz_peak(n)
        r = pk / n
        to = trailing_ones(n)
        log2r = math.log2(r) if r > 0 else 0
        results.append({
            "k": k,
            "n": n,
            "peak": pk,
            "ratio": float(r),
            "log2_ratio": float(log2r),
            "trailing_ones": to,
            "log2r_per_trailing": log2r / to if to > 0 else 0,
        })
        print(f"  2^{k}-1 = {n}: peak={pk}, ratio={r:.2f}, log2={log2r:.4f}, "
              f"trail1s={to}, log2r/trail1s={log2r/to:.4f}" if to > 0 else f"  k={k}: trail1s=0")

    # log2(ratio) vs k (= trailing_ones) の回帰
    ks = [r["k"] for r in results]
    log2s = [r["log2_ratio"] for r in results]
    mk, ml = mean(ks), mean(log2s)
    cov = sum((x-mk)*(y-ml) for x,y in zip(ks, log2s)) / len(ks)
    varx = sum((x-mk)**2 for x in ks) / len(ks)
    slope = cov / varx if varx > 0 else 0
    intercept = ml - slope * mk
    print(f"\n  回帰: log2(peak/n) ~ {slope:.4f} * k + {intercept:.4f}")
    print(f"  つまり peak(2^k-1) / (2^k-1) ~ 2^({slope:.4f}*k + {intercept:.4f})")
    print(f"  1 trailing_oneあたり ~ {slope:.4f} bits の log2(peak/n) 増加")

    return results, slope, intercept

# ========================================
# Analysis B: 一般のtrailing ones固定での peak/n分布
# ========================================
def analysis_trailing_ones_fixed(N_max=500000):
    print(f"\n=== Analysis B: trailing_ones固定でのpeak/n分布 (N<{N_max}) ===")

    trail_data = defaultdict(list)

    for n in range(1, N_max + 1, 2):
        to = trailing_ones(n)
        pk = collatz_peak(n)
        r = pk / n
        log_r = math.log2(max(r, 1e-300))
        trail_data[to].append(log_r)

    results = {}
    print(f"\n  {'TO':>4} | {'count':>8} | {'mean_log2':>10} | {'std_log2':>8} | {'max_log2':>8} | {'median':>8}")
    print(f"  {'-'*65}")
    for to in sorted(trail_data.keys()):
        data = trail_data[to]
        if len(data) < 10:
            continue
        m = mean(data)
        s = std(data)
        mx = max(data)
        med = median_val(data)
        results[to] = {
            "count": len(data),
            "mean_log2_ratio": m,
            "std_log2_ratio": s,
            "max_log2_ratio": mx,
            "median_log2_ratio": med,
        }
        print(f"  {to:>4} | {len(data):>8} | {m:>10.4f} | {s:>8.4f} | {mx:>8.4f} | {med:>8.4f}")

    # trailing_ones vs mean_log2_ratio の回帰
    valid = [(to, info["mean_log2_ratio"]) for to, info in results.items() if info["count"] >= 100]
    if len(valid) >= 3:
        xs = [v[0] for v in valid]
        ys = [v[1] for v in valid]
        mx_r, my_r = mean(xs), mean(ys)
        cov = sum((x-mx_r)*(y-my_r) for x,y in zip(xs, ys)) / len(xs)
        varx = sum((x-mx_r)**2 for x in xs) / len(xs)
        slope = cov / varx if varx > 0 else 0
        intercept = my_r - slope * mx_r
        print(f"\n  回帰: mean_log2(peak/n) ~ {slope:.4f} * trailing_ones + {intercept:.4f}")
        print(f"  既知値 (E[log2(T/n)] +2.4/bit) と比較: {slope:.4f} vs 2.4")
    else:
        slope, intercept = None, None

    return results, slope

# ========================================
# Analysis C: テール分布の精密解析
# ========================================
def analysis_tail_distribution(N_max=500000):
    print(f"\n=== Analysis C: テール分布精密解析 ===")

    log_ratios = []
    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        log_ratios.append(math.log2(max(r, 1e-300)))

    log_ratios.sort()
    n = len(log_ratios)

    # 累積分布の尾部: P(log2(peak/n) > x) の対数
    # 指数的減衰なら log P ~ -a*x (直線)
    # べき的減衰なら log P ~ -b*log(x)
    print(f"\n  log2(peak/n)の尾部生存確率:")
    thresholds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    tail_points = []
    print(f"  {'x':>5} | {'P(X>x)':>12} | {'log10(P)':>10} | count")
    print(f"  {'-'*45}")
    for x in thresholds:
        count = sum(1 for lr in log_ratios if lr > x)
        p = count / n
        if p > 0:
            log10p = math.log10(p)
            print(f"  {x:>5} | {p:>12.8f} | {log10p:>10.4f} | {count}")
            tail_points.append((x, log10p, count))
        else:
            print(f"  {x:>5} | {'0':>12} | {'-inf':>10} | 0")

    # 指数減衰回帰: log10(P) vs x
    if len(tail_points) >= 3:
        xs = [tp[0] for tp in tail_points]
        ys = [tp[1] for tp in tail_points]
        mx, my = mean(xs), mean(ys)
        cov = sum((x-mx)*(y-my) for x,y in zip(xs, ys)) / len(xs)
        varx = sum((x-mx)**2 for x in xs) / len(xs)
        slope = cov / varx if varx > 0 else 0
        intercept = my - slope * mx
        print(f"\n  指数減衰適合: log10(P(X>x)) ~ {slope:.4f} * x + {intercept:.4f}")
        print(f"  つまり P(X>x) ~ 10^{{{intercept:.2f}}} * 10^({slope:.4f}*x)")
        print(f"  指数減衰率 (nat): lambda = {-slope * math.log(10):.4f}")

        # 残差
        residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
        print(f"  残差: {['%.4f' % r for r in residuals]}")

        tail_result = {
            "decay_type": "exponential",
            "slope_log10": slope,
            "intercept_log10": intercept,
            "lambda_nat": -slope * math.log(10),
            "tail_points": tail_points,
            "residuals": residuals,
        }
    else:
        tail_result = {"tail_points": tail_points}

    return tail_result

# ========================================
# Analysis D: n mod 2^k の2Dマップ (k=1..8)
# ========================================
def analysis_mod_hierarchy(N_max=300000):
    print(f"\n=== Analysis D: mod 2^k階層の peak/n寄与分析 ===")

    # n mod 2^k で条件付き期待値 E[log2(peak/n) | n mod 2^k = r]
    # k=1,2,...,8
    results = {}
    all_log_ratios = {}

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        lr = math.log2(max(r, 1e-300))
        all_log_ratios[n] = lr

    for k in range(1, 9):
        mod_val = 1 << k
        group_data = defaultdict(list)
        for n, lr in all_log_ratios.items():
            group_data[n % mod_val].append(lr)

        # 各residueの条件付き期待値
        cond_means = {}
        for res in sorted(group_data.keys()):
            data = group_data[res]
            if len(data) >= 50:
                cond_means[res] = mean(data)

        if cond_means:
            max_res = max(cond_means, key=cond_means.get)
            min_res = min(cond_means, key=cond_means.get)
            spread = cond_means[max_res] - cond_means[min_res]
            results[k] = {
                "mod": mod_val,
                "n_residues": len(cond_means),
                "max_residue": max_res,
                "max_mean": cond_means[max_res],
                "min_residue": min_res,
                "min_mean": cond_means[min_res],
                "spread": spread,
            }
            print(f"  mod 2^{k}={mod_val}: spread={spread:.4f}, "
                  f"max_res={max_res}(bin={bin(max_res)}, mean={cond_means[max_res]:.4f}), "
                  f"min_res={min_res}(mean={cond_means[min_res]:.4f})")

    # spreadの成長パターン
    ks = sorted(results.keys())
    if len(ks) >= 3:
        spreads = [results[k]["spread"] for k in ks]
        print(f"\n  Spread成長: {['%.4f' % s for s in spreads]}")
        diffs = [spreads[i+1] - spreads[i] for i in range(len(spreads)-1)]
        print(f"  差分: {['%.4f' % d for d in diffs]}")

    return results

# ========================================
# Analysis E: n = a * 2^k - 1 型のpeak/n (一般化Mersenne)
# ========================================
def analysis_generalized_mersenne():
    print(f"\n=== Analysis E: n = a*2^k - 1 型のpeak/n ===")

    results = []
    for a in [1, 3, 5, 7, 9, 11, 13]:
        print(f"\n  a={a}:")
        for k in range(2, 22):
            n = a * (1 << k) - 1
            if n > 5000000:
                break
            pk = collatz_peak(n)
            r = pk / n
            to = trailing_ones(n)
            log2r = math.log2(r) if r > 0 else 0
            results.append({
                "a": a, "k": k, "n": n, "peak": pk,
                "ratio": float(r), "log2_ratio": float(log2r),
                "trailing_ones": to,
            })
            if k <= 15 or k % 3 == 0:
                print(f"    k={k}: n={n}, peak={pk}, log2(peak/n)={log2r:.4f}, trail1s={to}")

    # a=1 (pure Mersenne) の特別性を確認
    a1_data = [(r["k"], r["log2_ratio"]) for r in results if r["a"] == 1]
    if len(a1_data) >= 3:
        xs, ys = zip(*a1_data)
        mx, my = mean(xs), mean(ys)
        cov = sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / len(xs)
        varx = sum((x-mx)**2 for x in xs) / len(xs)
        slope = cov / varx if varx > 0 else 0
        print(f"\n  a=1 回帰: log2(peak/n) ~ {slope:.4f} * k")

    return results

# ========================================
# Main
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("コラッツ peak(n)/n 比 深堀解析")
    print("=" * 70)
    total_t0 = time.time()

    # A: Mersenne型
    mersenne_results, mersenne_slope, mersenne_intercept = analysis_mersenne()

    # B: trailing ones固定
    trail_results, trail_slope = analysis_trailing_ones_fixed(N_max=500000)

    # C: テール分布
    tail_result = analysis_tail_distribution(N_max=500000)

    # D: mod 2^k 階層
    mod_hierarchy = analysis_mod_hierarchy(N_max=300000)

    # E: 一般化Mersenne
    gen_mersenne = analysis_generalized_mersenne()

    total_elapsed = time.time() - total_t0
    print(f"\n{'='*70}")
    print(f"総計算時間: {total_elapsed:.1f}s")

    output = {
        "analysis_A_mersenne": {
            "data": mersenne_results,
            "slope_per_k": mersenne_slope,
            "intercept": mersenne_intercept,
        },
        "analysis_B_trailing_fixed": {
            "data": {str(k): v for k, v in trail_results.items()},
            "slope_per_trailing_one": trail_slope,
        },
        "analysis_C_tail": tail_result,
        "analysis_D_mod_hierarchy": {str(k): v for k, v in mod_hierarchy.items()},
        "analysis_E_gen_mersenne_summary": {
            "sample_size": len(gen_mersenne),
        },
    }

    with open("/Users/soyukke/study/lean-unsolved/results/peak_ratio_deep.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n結果を results/peak_ratio_deep.json に保存しました")
