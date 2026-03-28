#!/usr/bin/env python3
"""
探索095: v2列初期5ステップからのST条件付き期待値の精密計算

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} の停止時間(ST)を
v2列の初期5ステップパターン(j1,...,j5)で条件付けて分析する。

N=10^6の奇数について統計を取り、E[ST|j1,...,j5]の精密モデルを構築。
"""

import json
import time
import math
from collections import defaultdict

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^{v2(3n+1)}"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def stopping_time(n):
    """Total stopping time: number of Syracuse steps until reaching 1"""
    steps = 0
    while n != 1 and steps < 100000:
        n = syracuse(n)
        steps += 1
    if steps >= 100000:
        return -1  # didn't stop
    return steps

def v2_sequence(n, k=5):
    """Return first k values of v2(3*n_i + 1) along the Syracuse orbit"""
    seq = []
    for _ in range(k):
        val = v2(3 * n + 1)
        seq.append(val)
        n = syracuse(n)
    return tuple(seq)

def main():
    t0 = time.time()

    N_MAX = 10**6
    # All odd numbers from 3 to N_MAX
    odds = range(3, N_MAX + 1, 2)

    # Collect data: v2 initial 5-step pattern -> list of stopping times
    pattern_data = defaultdict(list)

    # Also collect by sum of initial 5 v2 values
    sum_data = defaultdict(list)

    total_count = 0
    st_values = []

    for n in odds:
        st = stopping_time(n)
        if st < 0:
            continue
        v2seq = v2_sequence(n, k=5)
        v2sum = sum(v2seq)

        pattern_data[v2seq].append(st)
        sum_data[v2sum].append(st)
        st_values.append(st)
        total_count += 1

    elapsed_collect = time.time() - t0

    # ---- Analysis ----

    # 1. Global statistics
    global_mean_st = sum(st_values) / len(st_values)
    global_median_st = sorted(st_values)[len(st_values) // 2]

    # Mean log(n) for normalization
    log_values = [math.log(n) for n in range(3, N_MAX + 1, 2)]
    mean_log_n = sum(log_values) / len(log_values)
    st_over_log_ratio = global_mean_st / mean_log_n

    # 2. E[ST | v2_sum] analysis
    sum_analysis = {}
    for s in sorted(sum_data.keys()):
        vals = sum_data[s]
        if len(vals) < 10:
            continue
        mean_st = sum(vals) / len(vals)
        std_st = (sum((x - mean_st)**2 for x in vals) / len(vals)) ** 0.5
        sum_analysis[s] = {
            "count": len(vals),
            "mean_st": round(mean_st, 3),
            "std_st": round(std_st, 3),
            "median_st": sorted(vals)[len(vals) // 2],
        }

    # 3. Top patterns by frequency and by mean ST
    pattern_stats = {}
    for pat, vals in pattern_data.items():
        if len(vals) < 5:
            continue
        mean_st = sum(vals) / len(vals)
        std_st = (sum((x - mean_st)**2 for x in vals) / len(vals)) ** 0.5
        pattern_stats[pat] = {
            "count": len(vals),
            "mean_st": round(mean_st, 3),
            "std_st": round(std_st, 3),
            "v2_sum": sum(pat),
        }

    # Top 20 most frequent patterns
    top_freq = sorted(pattern_stats.items(), key=lambda x: -x[1]["count"])[:20]

    # Top 20 highest mean ST (min count >= 20)
    top_high_st = sorted(
        [(k, v) for k, v in pattern_stats.items() if v["count"] >= 20],
        key=lambda x: -x[1]["mean_st"]
    )[:20]

    # Top 20 lowest mean ST (min count >= 20)
    top_low_st = sorted(
        [(k, v) for k, v in pattern_stats.items() if v["count"] >= 20],
        key=lambda x: x[1]["mean_st"]
    )[:20]

    # 4. Linear regression: ST ~ a * v2_sum + b
    # Using patterns with count >= 20
    regression_points = []
    for pat, stats in pattern_stats.items():
        if stats["count"] >= 20:
            regression_points.append((stats["v2_sum"], stats["mean_st"], stats["count"]))

    if regression_points:
        # Weighted least squares
        sw = sum(c for _, _, c in regression_points)
        sx = sum(x * c for x, _, c in regression_points)
        sy = sum(y * c for _, y, c in regression_points)
        sxx = sum(x * x * c for x, _, c in regression_points)
        sxy = sum(x * y * c for x, y, c in regression_points)

        denom = sw * sxx - sx * sx
        if denom != 0:
            slope = (sw * sxy - sx * sy) / denom
            intercept = (sy * sxx - sx * sxy) / denom
        else:
            slope = 0
            intercept = global_mean_st

        # R^2
        y_mean = sy / sw
        ss_tot = sum(c * (y - y_mean)**2 for _, y, c in regression_points)
        ss_res = sum(c * (y - (slope * x + intercept))**2 for x, y, c in regression_points)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        regression = {
            "model": "E[ST] = a * v2_sum + b",
            "slope_a": round(slope, 4),
            "intercept_b": round(intercept, 4),
            "r_squared": round(r_squared, 6),
            "n_patterns": len(regression_points),
        }
    else:
        regression = {"error": "insufficient data"}

    # 5. Per-step v2 marginal effect
    # For each position i in {0..4}, compute E[ST | j_i = k] for various k
    step_marginal = {}
    for pos in range(5):
        step_data = defaultdict(list)
        for pat, vals in pattern_data.items():
            step_data[pat[pos]].extend(vals)

        step_analysis = {}
        for k in sorted(step_data.keys()):
            vals = step_data[k]
            if len(vals) < 50:
                continue
            mean_st = sum(vals) / len(vals)
            step_analysis[k] = {
                "count": len(vals),
                "mean_st": round(mean_st, 3),
            }
        step_marginal[f"step_{pos+1}"] = step_analysis

    # 6. Multi-step regression: ST ~ a1*j1 + a2*j2 + ... + a5*j5 + b
    # Weighted by pattern count
    # Using numpy-free approach: normal equations
    # X = [j1, j2, j3, j4, j5, 1], y = mean_st, weight = count
    patterns_for_reg = [(pat, stats) for pat, stats in pattern_stats.items() if stats["count"] >= 10]

    if len(patterns_for_reg) >= 10:
        dim = 6  # 5 features + intercept
        # Build normal equations A^T W A x = A^T W y
        ATA = [[0.0] * dim for _ in range(dim)]
        ATy = [0.0] * dim

        for pat, stats in patterns_for_reg:
            w = stats["count"]
            features = list(pat) + [1.0]
            y = stats["mean_st"]
            for i in range(dim):
                for j in range(dim):
                    ATA[i][j] += w * features[i] * features[j]
                ATy[i] += w * features[i] * y

        # Solve using Gaussian elimination
        aug = [ATA[i][:] + [ATy[i]] for i in range(dim)]
        for col in range(dim):
            # Pivot
            max_row = max(range(col, dim), key=lambda r: abs(aug[r][col]))
            aug[col], aug[max_row] = aug[max_row], aug[col]
            pivot = aug[col][col]
            if abs(pivot) < 1e-12:
                continue
            for j in range(col, dim + 1):
                aug[col][j] /= pivot
            for row in range(dim):
                if row == col:
                    continue
                factor = aug[row][col]
                for j in range(col, dim + 1):
                    aug[row][j] -= factor * aug[col][j]

        coeffs = [aug[i][dim] for i in range(dim)]

        # R^2 for multi-step model
        sw = sum(s["count"] for _, s in patterns_for_reg)
        y_mean = sum(s["count"] * s["mean_st"] for _, s in patterns_for_reg) / sw
        ss_tot = sum(s["count"] * (s["mean_st"] - y_mean)**2 for _, s in patterns_for_reg)
        ss_res = 0
        for pat, stats in patterns_for_reg:
            pred = sum(c * j for c, j in zip(coeffs[:5], pat)) + coeffs[5]
            ss_res += stats["count"] * (stats["mean_st"] - pred)**2
        r2_multi = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        multi_regression = {
            "model": "E[ST] = a1*j1 + a2*j2 + a3*j3 + a4*j4 + a5*j5 + b",
            "coefficients": {
                "a1_step1": round(coeffs[0], 4),
                "a2_step2": round(coeffs[1], 4),
                "a3_step3": round(coeffs[2], 4),
                "a4_step4": round(coeffs[3], 4),
                "a5_step5": round(coeffs[4], 4),
                "b_intercept": round(coeffs[5], 4),
            },
            "r_squared": round(r2_multi, 6),
            "n_patterns": len(patterns_for_reg),
        }
    else:
        multi_regression = {"error": "insufficient data"}

    # 7. Theoretical probability of each v2 sum
    # P(sum = s) for 5 geometric(1/2) random variables
    # Each v2 ~ Geometric with P(v2=j) = 1/2^j for j>=1
    # Sum of 5 such variables: min=5, distribution via convolution
    theoretical_prob = {}
    # Compute via dynamic programming
    dp = {0: 1.0}
    for step in range(5):
        new_dp = defaultdict(float)
        for s, p in dp.items():
            for j in range(1, 40):  # truncate at 40
                new_dp[s + j] += p * (0.5 ** j)
        dp = new_dp
    for s in sorted(dp.keys()):
        if dp[s] > 1e-8:
            theoretical_prob[s] = round(dp[s], 8)

    elapsed_total = time.time() - t0

    # ---- Build result ----
    result = {
        "exploration_id": "095",
        "title": "v2列初期5ステップからのST条件付き期待値の精密計算",
        "method": "v2_initial_5step_conditional_expected_ST",
        "parameters": {
            "N_max": N_MAX,
            "n_odd_numbers": total_count,
            "v2_steps": 5,
        },
        "global_statistics": {
            "mean_ST": round(global_mean_st, 3),
            "median_ST": global_median_st,
            "mean_log_n": round(mean_log_n, 4),
            "ST_over_log_ratio": round(st_over_log_ratio, 4),
        },
        "v2_sum_conditional_ST": sum_analysis,
        "linear_regression_sum": regression,
        "multi_step_regression": multi_regression,
        "step_marginal_effects": step_marginal,
        "top_20_most_frequent_patterns": [
            {"pattern": list(k), "v2_sum": sum(k), **v}
            for k, v in top_freq
        ],
        "top_20_highest_mean_ST": [
            {"pattern": list(k), "v2_sum": sum(k), **v}
            for k, v in top_high_st
        ],
        "top_20_lowest_mean_ST": [
            {"pattern": list(k), "v2_sum": sum(k), **v}
            for k, v in top_low_st
        ],
        "theoretical_v2sum_probabilities": theoretical_prob,
        "unique_patterns_observed": len(pattern_stats),
        "timing": {
            "data_collection_sec": round(elapsed_collect, 2),
            "total_sec": round(elapsed_total, 2),
        },
    }

    # Save
    with open("/Users/soyukke/study/lean-unsolved/results/exploration_095.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
