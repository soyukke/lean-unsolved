"""
Tao 2019 密度1結果の精密化:
f(n) = log(n)^C (C=2,3,5) での Col_min(n) < f(n) の到達率を計算
N = 10^7 まで検証し、理論予測との一致度を検証する。

Col_min(n) = min of Collatz orbit from n
T(n) = (3n+1) / 2^{v2(3n+1)} for odd n

We compute:
1. Col_min(n) for each odd n up to N
2. Fraction of n <= N with Col_min(n) < f(n) for various f
3. Logarithmic density version
4. Exception set mod structure analysis
"""

import math
from collections import defaultdict
import time
import sys

def col_min_fast(n, max_steps=10000):
    """Fast Col_min using standard 3n+1 map"""
    current = n
    min_val = n
    for _ in range(max_steps):
        if current == 1:
            return 1
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        if current < min_val:
            min_val = current
    return min_val

def linear_regression(xs, ys):
    """Simple linear regression y = a*x + b"""
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x*x for x in xs)
    sxy = sum(x*y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-15:
        return 0, 0
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return a, b

def percentile(sorted_data, p):
    """Compute p-th percentile from sorted data"""
    n = len(sorted_data)
    k = (n - 1) * p / 100.0
    f = int(k)
    c = f + 1
    if c >= n:
        return sorted_data[-1]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1

def main():
    # Parameters
    N_values = [10**4, 10**5, 10**6, 10**7]
    C_values = [2, 3, 5]

    print("=" * 80)
    print("Tao 2019 密度1結果の精密化")
    print("f(n) = log(n)^C での Col_min(n) < f(n) 到達率")
    print("=" * 80)

    for N in N_values:
        t0 = time.time()
        print(f"\n{'='*60}")
        print(f"N = {N:,}")
        print(f"{'='*60}")

        odd_count = 0
        reach_counts = {C: 0 for C in C_values}
        reach_counts_logdensity = {C: 0.0 for C in C_values}
        total_log_weight = 0.0

        # Also track exceptions for mod analysis (only for smaller N)
        exceptions = {C: [] for C in C_values}

        # f(n) = n^theta comparison (Korec bound)
        theta_korec = math.log(3) / math.log(4)  # ~0.7924
        korec_count = 0
        sqrt_count = 0
        reached_1_count = 0

        for n in range(3, N + 1, 2):
            cmin = col_min_fast(n)
            odd_count += 1
            log_weight = 1.0 / n
            total_log_weight += log_weight

            if cmin == 1:
                reached_1_count += 1

            for C in C_values:
                threshold = math.log(n) ** C if n > 1 else 1.0
                if cmin < threshold:
                    reach_counts[C] += 1
                    reach_counts_logdensity[C] += log_weight
                else:
                    if N <= 10**6 and len(exceptions[C]) < 50000:
                        exceptions[C].append(n)

            if cmin < n ** theta_korec:
                korec_count += 1
            if cmin < math.sqrt(n):
                sqrt_count += 1

        elapsed = time.time() - t0
        print(f"計算時間: {elapsed:.1f}s, 奇数個数: {odd_count:,}")
        print(f"Col_min=1 到達: {reached_1_count}/{odd_count} = {reached_1_count/odd_count:.6f}")

        # Natural density results
        print(f"\n--- 自然密度 (奇数のみ) ---")
        print(f"{'f(n)':>20} | {'到達数':>10} | {'到達率':>10} | {'例外数':>10} | {'例外率':>12}")
        print("-" * 78)

        for C in C_values:
            rate = reach_counts[C] / odd_count
            exc = odd_count - reach_counts[C]
            exc_rate = exc / odd_count
            print(f"  log(n)^{C:<11} | {reach_counts[C]:>10,} | {rate:>10.6f} | {exc:>10,} | {exc_rate:>12.8f}")

        korec_rate = korec_count / odd_count
        sqrt_rate = sqrt_count / odd_count
        print(f"  n^{theta_korec:.4f} (Korec) | {korec_count:>10,} | {korec_rate:>10.6f} |")
        print(f"  sqrt(n)            | {sqrt_count:>10,} | {sqrt_rate:>10.6f} |")

        # Logarithmic density
        print(f"\n--- 対数密度 ---")
        for C in C_values:
            log_rate = reach_counts_logdensity[C] / total_log_weight
            print(f"  log(n)^{C}: 対数密度 = {log_rate:.8f}")

        # Exception mod analysis (only for smaller N)
        if N <= 10**6:
            print(f"\n--- 例外集合の mod 構造解析 ---")
            for C in C_values:
                exc_set = exceptions[C]
                if len(exc_set) == 0:
                    print(f"  log(n)^{C}: 例外なし")
                    continue

                print(f"\n  log(n)^{C}: 例外 {len(exc_set)} 個")
                if len(exc_set) <= 30:
                    print(f"    例外値: {exc_set}")
                else:
                    print(f"    最初の20個: {exc_set[:20]}")
                    print(f"    最後の10個: {exc_set[-10:]}")

                # Mod analysis
                for M in [3, 4, 6, 8, 12, 16, 24, 48]:
                    mod_counts = defaultdict(int)
                    for e in exc_set:
                        mod_counts[e % M] += 1
                    sorted_mods = sorted(mod_counts.items(), key=lambda x: -x[1])
                    expected = len(exc_set) / M
                    if expected > 0:
                        chi2 = sum((c - expected)**2 / expected for _, c in mod_counts.items())
                    else:
                        chi2 = 0
                    if chi2 > 2 * M:  # Only report significant deviation
                        top3 = sorted_mods[:3]
                        top3_str = ", ".join(f"{r}:{c}" for r, c in top3)
                        print(f"    mod {M}: chi2={chi2:.1f}, top=[{top3_str}]")

        sys.stdout.flush()

    # Phase 2: Exception scaling analysis
    print("\n" + "=" * 80)
    print("Phase 2: 例外数のスケーリング解析")
    print("=" * 80)

    scales = [10**3, 3*10**3, 10**4, 3*10**4, 10**5, 3*10**5, 10**6]
    exception_data = {C: [] for C in C_values}

    for N in scales:
        exc_count = {C: 0 for C in C_values}
        odd_count = 0
        for n in range(3, N + 1, 2):
            cmin = col_min_fast(n)
            odd_count += 1
            for C in C_values:
                threshold = math.log(n) ** C if n > 1 else 1.0
                if cmin >= threshold:
                    exc_count[C] += 1
        for C in C_values:
            exception_data[C].append((N, odd_count, exc_count[C]))

    print(f"\n{'N':>10} | ", end="")
    for C in C_values:
        print(f" exc(C={C})/total  |", end="")
    print()
    print("-" * 78)

    for i, N in enumerate(scales):
        print(f"{N:>10,} | ", end="")
        for C in C_values:
            _, total, exc = exception_data[C][i]
            rate = exc / total if total > 0 else 0
            print(f"  {exc:>6}/{total:>6} ({rate:.4f}) |", end="")
        print()

    # Fit power law: exc_rate ~ N^(-alpha)
    print(f"\n--- スケーリング指数の推定 (例外率 ~ N^(-alpha)) ---")
    for C in C_values:
        log_N = []
        log_rate = []
        for N, total, exc in exception_data[C]:
            rate = exc / total if total > 0 else 0
            if rate > 0:
                log_N.append(math.log(N))
                log_rate.append(math.log(rate))

        if len(log_N) >= 2:
            slope, intercept = linear_regression(log_N, log_rate)
            print(f"  C={C}: alpha = {-slope:.4f} (例外率 ~ N^({slope:.4f}))")
        else:
            print(f"  C={C}: 例外なし（全てが閾値以下）")

    # Phase 3: Col_min distribution
    print("\n" + "=" * 80)
    print("Phase 3: Col_min / n の分布と log(n)^C 閾値")
    print("=" * 80)

    N = 10**5
    ratios = []
    for n in range(3, N + 1, 2):
        cmin = col_min_fast(n)
        if cmin > 0 and n > 1:
            ratios.append(math.log(cmin) / math.log(n))

    ratios.sort()
    mean_r = sum(ratios) / len(ratios)
    median_r = ratios[len(ratios)//2]
    variance = sum((r - mean_r)**2 for r in ratios) / len(ratios)
    std_r = math.sqrt(variance)

    print(f"  log(Col_min) / log(n) の統計量 (N={N:,}, 奇数のみ):")
    print(f"    平均: {mean_r:.6f}")
    print(f"    中央値: {median_r:.6f}")
    print(f"    標準偏差: {std_r:.6f}")
    print(f"    最大値: {ratios[-1]:.6f}")

    frac_1 = sum(1 for r in ratios if r == 0) / len(ratios)
    print(f"    Col_min=1 (ratio=0) の割合: {frac_1:.6f}")

    for p in [90, 95, 99, 99.9]:
        val = percentile(ratios, p)
        print(f"    {p}パーセンタイル: {val:.6f}")

    # Phase 4: Structure of exceptions
    print("\n" + "=" * 80)
    print("Phase 4: 例外nの構造的特徴（Col_min(n)が大きいn）")
    print("=" * 80)

    N = 10**6
    top_entries = []
    for n in range(3, N + 1, 2):
        cmin = col_min_fast(n)
        top_entries.append((cmin, n))

    top_entries.sort(reverse=True)
    top100 = top_entries[:100]

    print(f"\n  Col_min が最大の20個 (N={N:,}):")
    print(f"  {'n':>12} | {'Col_min':>12} | {'Col_min/n':>10} | {'n mod 6':>8} | {'n mod 12':>8}")
    print("  " + "-" * 60)
    for cmin, n in top100[:20]:
        print(f"  {n:>12,} | {cmin:>12,} | {cmin/n:>10.4f} | {n%6:>8} | {n%12:>8}")

    # Mod structure of top exceptions
    print(f"\n  Top-100 例外の mod 分布:")
    for M in [3, 6, 8, 12, 16, 24]:
        mod_dist = defaultdict(int)
        for _, n in top100:
            mod_dist[n % M] += 1
        sorted_mods = sorted(mod_dist.items(), key=lambda x: -x[1])
        top5 = dict(sorted_mods[:5])
        print(f"    mod {M}: {top5}")

    # Binary structure
    print(f"\n  Top-20 のバイナリ構造:")
    for cmin, n in top100[:20]:
        binary = bin(n)[2:]
        ones = binary.count('1')
        print(f"    n={n:>10}, bin_len={len(binary):>3}, ones={ones:>3}, density={ones/len(binary):.3f}, Col_min={cmin}")

    # Phase 5: 対数密度の収束挙動
    print("\n" + "=" * 80)
    print("Phase 5: 対数密度の収束挙動")
    print("=" * 80)

    C_target = 2  # Focus on C=2 as it's the hardest threshold
    checkpoints = [100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000]
    print(f"\n  f(n) = log(n)^{C_target} の対数密度の収束 (1 - density):")
    print(f"  {'N':>10} | {'1-logdensity':>14} | {'1-natdensity':>14}")
    print("  " + "-" * 45)

    reach_ld = 0.0
    total_ld = 0.0
    reach_nd = 0
    total_nd = 0

    cp_idx = 0
    for n in range(3, max(checkpoints) + 1, 2):
        cmin = col_min_fast(n)
        lw = 1.0 / n
        total_ld += lw
        total_nd += 1
        threshold = math.log(n) ** C_target
        if cmin < threshold:
            reach_ld += lw
            reach_nd += 1

        if cp_idx < len(checkpoints) and n >= checkpoints[cp_idx]:
            ld = reach_ld / total_ld
            nd = reach_nd / total_nd
            print(f"  {n:>10,} | {1-ld:>14.8f} | {1-nd:>14.8f}")
            cp_idx += 1

    print("\nDone.")

if __name__ == "__main__":
    main()
