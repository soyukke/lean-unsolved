"""
Tao 2019 密度1結果の精密化 v2:

問題: n <= 10^7 では全て Col_min(n) = 1 なので、Col_min は trivial。
代わりに、「最初にf(n)以下に到達するまでのステップ数」と
「Col_min_partial(n, k): k ステップ以内の最小値」を調べる。

具体的に:
1. 固定ステップ数 k でのCol_min_k(n) = min(T^0(n),...,T^k(n))
   k=10,20,50,100 で Col_min_k(n) < f(n) の率を測定
2. 「最初にf(n)以下に落ちるステップ数」の分布
3. 軌道の最大値 Col_max(n) と f(n) の比較
4. Stopping time (n より小さくなるまでの時間) の分布と理論予測の比較
"""

import math
from collections import defaultdict
import time
import sys

def collatz_orbit_stats(n, max_steps=10000):
    """
    Compute various statistics of the Collatz orbit starting from n.
    Returns: (col_min, col_max, total_stopping_time, first_drop_below)
    first_drop_below[threshold] = step count to first go below threshold
    """
    current = n
    min_val = n
    max_val = n
    step = 0

    # Track first time below various thresholds
    # We'll compute these afterwards
    orbit_values = [n]

    for step in range(1, max_steps + 1):
        if current == 1:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        orbit_values.append(current)
        if current < min_val:
            min_val = current
        if current > max_val:
            max_val = current

    total_steps = len(orbit_values) - 1
    return orbit_values, min_val, max_val, total_steps

def syracuse_orbit_stats(n, max_steps=10000):
    """
    Syracuse map T: odd -> odd, T(n) = (3n+1)/2^{v_2(3n+1)}
    Only tracks odd values in the orbit.
    """
    current = n
    min_val = n
    max_val = n
    orbit = [n]

    for step in range(1, max_steps + 1):
        if current == 1:
            break
        val = 3 * current + 1
        while val % 2 == 0:
            val //= 2
        current = val
        orbit.append(current)
        if current < min_val:
            min_val = current
        if current > max_val:
            max_val = current

    return orbit, min_val, max_val

def main():
    print("=" * 80)
    print("Tao 2019 精密化 v2: 有限ステップでの到達率と停止時間解析")
    print("=" * 80)

    # =========================================================================
    # Analysis 1: k-step partial minimum
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 1: k-step partial Col_min_k(n) < f(n) 到達率")
    print("Syracuse写像で k ステップ以内の最小値")
    print("=" * 70)

    N = 10**6
    k_values = [5, 10, 20, 50, 100]
    C_values = [1, 2, 3]

    # Also test f(n) = n^alpha for alpha < 1
    alpha_values = [0.5, 0.3, 0.1]

    t0 = time.time()

    # Collect data
    counts_logC = {(k, C): 0 for k in k_values for C in C_values}
    counts_alpha = {(k, a): 0 for k in k_values for a in alpha_values}
    total_odd = 0

    for n in range(3, N + 1, 2):
        total_odd += 1

        # Compute Syracuse orbit
        current = n
        min_by_step = [n]  # min_by_step[i] = min of first i+1 values

        for s in range(max(k_values)):
            if current == 1:
                # Stay at 1
                min_by_step.append(1)
                continue
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            prev_min = min_by_step[-1]
            min_by_step.append(min(prev_min, current))

        for k in k_values:
            col_min_k = min_by_step[min(k, len(min_by_step)-1)]

            for C in C_values:
                threshold = math.log(n) ** C
                if col_min_k < threshold:
                    counts_logC[(k, C)] += 1

            for a in alpha_values:
                threshold = n ** a
                if col_min_k < threshold:
                    counts_alpha[(k, a)] += 1

    elapsed = time.time() - t0
    print(f"N={N:,}, 計算時間: {elapsed:.1f}s")

    print(f"\n  f(n) = log(n)^C の場合:")
    print(f"  {'k':>5} | ", end="")
    for C in C_values:
        print(f" C={C} rate  |", end="")
    print()
    print("  " + "-" * 50)
    for k in k_values:
        print(f"  {k:>5} | ", end="")
        for C in C_values:
            rate = counts_logC[(k, C)] / total_odd
            print(f" {rate:.6f} |", end="")
        print()

    print(f"\n  f(n) = n^alpha の場合:")
    print(f"  {'k':>5} | ", end="")
    for a in alpha_values:
        print(f" a={a} rate  |", end="")
    print()
    print("  " + "-" * 50)
    for k in k_values:
        print(f"  {k:>5} | ", end="")
        for a in alpha_values:
            rate = counts_alpha[(k, a)] / total_odd
            print(f" {rate:.6f} |", end="")
        print()

    # =========================================================================
    # Analysis 2: Stopping time distribution
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 2: 停止時間 (n より小さくなるステップ数) の分布")
    print("理論予測: E[log2(T(n)/n)] = log2(3/4) ≈ -0.415")
    print("         => 期待停止時間 ~ log(n) / 0.415")
    print("=" * 70)

    N = 10**6
    t0 = time.time()

    stopping_times = []
    total_stopping_times = []

    for n in range(3, N + 1, 2):
        current = n
        st = 0
        total_st = 0

        # Stopping time (Syracuse steps to go below n)
        while current >= n:
            if current == 1 and n > 1:
                break
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1
            if st > 1000:
                break
        stopping_times.append(st)

        # Total stopping time (to reach 1)
        current = n
        while current != 1:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            total_st += 1
            if total_st > 10000:
                break
        total_stopping_times.append(total_st)

    elapsed = time.time() - t0
    print(f"N={N:,}, 計算時間: {elapsed:.1f}s")

    # Statistics
    stopping_times.sort()
    total_stopping_times.sort()

    n_st = len(stopping_times)
    mean_st = sum(stopping_times) / n_st
    median_st = stopping_times[n_st // 2]
    max_st = stopping_times[-1]

    mean_tst = sum(total_stopping_times) / len(total_stopping_times)
    median_tst = total_stopping_times[len(total_stopping_times) // 2]
    max_tst = total_stopping_times[-1]

    # Theoretical prediction for stopping time
    # E[steps to drop below n] ~ log(n) / |E[log(T(n)/n)]|
    # E[log2(T/n)] = log2(3/4) = -0.41504
    drift = 0.41504

    print(f"\n  停止時間 (Syracuse, n以下に到達):")
    print(f"    平均: {mean_st:.2f}")
    print(f"    中央値: {median_st}")
    print(f"    最大: {max_st}")

    # Compare with theory at different n ranges
    print(f"\n  停止時間 vs 理論予測 (理論: log2(n) / {drift:.5f}):")
    print(f"  {'n range':>15} | {'平均 ST':>10} | {'理論予測':>10} | {'比率':>8}")
    print("  " + "-" * 55)

    ranges = [(3, 100), (100, 1000), (1000, 10000), (10000, 100000), (100000, 1000000)]
    idx = 0
    for lo, hi in ranges:
        sts_in_range = []
        for n in range(max(lo, 3), hi + 1, 2):
            current = n
            st = 0
            while current >= n and st < 1000:
                val = 3 * current + 1
                while val % 2 == 0:
                    val //= 2
                current = val
                st += 1
            sts_in_range.append(st)

        if sts_in_range:
            mean_in_range = sum(sts_in_range) / len(sts_in_range)
            n_mid = (lo + hi) / 2
            theory = math.log2(n_mid) / drift
            ratio = mean_in_range / theory if theory > 0 else 0
            print(f"  {lo:>7}-{hi:<7} | {mean_in_range:>10.2f} | {theory:>10.2f} | {ratio:>8.4f}")

    print(f"\n  全停止時間 (Syracuse, 1に到達):")
    print(f"    平均: {mean_tst:.2f}")
    print(f"    中央値: {median_tst}")
    print(f"    最大: {max_tst}")

    # =========================================================================
    # Analysis 3: Stopping time tail distribution P(ST > t)
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 3: 停止時間の尾部分布 P(ST > t)")
    print("理論: P(ST > t) ~ exp(-lambda * t), lambda ≈ 0.0735")
    print("=" * 70)

    # Use total stopping times for tail analysis
    # Count P(TST > t)
    tst_sorted = sorted(total_stopping_times)
    n_total = len(tst_sorted)

    print(f"\n  P(全停止時間 > t):")
    print(f"  {'t':>6} | {'P(TST>t)':>12} | {'-log(P)/t':>12} | {'理論lambda':>12}")
    print("  " + "-" * 55)

    t_values = [10, 20, 30, 50, 70, 100, 150, 200, 300]
    for t in t_values:
        count_above = sum(1 for x in tst_sorted if x > t)
        p = count_above / n_total
        if p > 0:
            lam_est = -math.log(p) / t
            print(f"  {t:>6} | {p:>12.6f} | {lam_est:>12.6f} | {0.0735:>12.6f}")
        else:
            print(f"  {t:>6} | {0:>12.6f} | {'inf':>12} | {0.0735:>12.6f}")

    # =========================================================================
    # Analysis 4: 降下比率 T^k(n)/n の分布
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 4: k-step 降下比率の分布")
    print("理論: E[log2(T^k(n)/n)] ≈ k * (-0.41504)")
    print("=" * 70)

    N = 100000
    k_test = [5, 10, 20, 50]

    for k in k_test:
        log_ratios = []
        for n in range(3, N + 1, 2):
            current = n
            for _ in range(k):
                if current == 1:
                    break
                val = 3 * current + 1
                while val % 2 == 0:
                    val //= 2
                current = val
            if current > 0 and n > 0:
                lr = math.log2(current / n) if current > 0 else -100
                log_ratios.append(lr)

        mean_lr = sum(log_ratios) / len(log_ratios)
        theory_lr = k * (-0.41504)
        variance_lr = sum((x - mean_lr)**2 for x in log_ratios) / len(log_ratios)
        std_lr = math.sqrt(variance_lr)

        print(f"  k={k:>3}: E[log2(T^k/n)] = {mean_lr:>10.4f} (理論: {theory_lr:>10.4f}), std = {std_lr:.4f}")

    # =========================================================================
    # Analysis 5: f(n) = C * log(log(n)) (極めて遅い成長) での到達
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 5: 超低成長関数 f(n) = C * log(log(n)) での到達率")
    print("Taoの定理: 任意のf(n)->infinity で密度1")
    print("=" * 70)

    N = 10**6
    C_slow_values = [1, 2, 5, 10]

    # Here we test: is there any n such that Col_min(n) >= C * log(log(n))?
    # Since Col_min(n) = 1 for all tested n, we need to look at
    # intermediate steps instead.
    #
    # Better: look at Col_min_k(n) for SMALL k where the orbit hasn't
    # reached 1 yet

    print(f"\n  k-step minimum vs f(n) = C * log(log(n)):")
    print(f"  N = {N:,}")

    for k in [3, 5, 10]:
        print(f"\n  k = {k} Syracuse steps:")
        print(f"  {'C':>5} | {'f(n)=Clog(logn) 到達率':>25} | {'f(n)=logn^C 到達率':>25}")
        print("  " + "-" * 60)

        for C in [1, 2, 3, 5]:
            count_loglog = 0
            count_logpow = 0
            total = 0

            for n in range(11, N + 1, 2):  # start at 11 so log(log(n)) > 0
                total += 1
                current = n
                min_k = n

                for _ in range(k):
                    if current == 1:
                        min_k = 1
                        break
                    val = 3 * current + 1
                    while val % 2 == 0:
                        val //= 2
                    current = val
                    if current < min_k:
                        min_k = current

                thresh_loglog = C * math.log(math.log(n))
                thresh_logpow = math.log(n) ** C

                if min_k < thresh_loglog:
                    count_loglog += 1
                if min_k < thresh_logpow:
                    count_logpow += 1

            rate_ll = count_loglog / total
            rate_lp = count_logpow / total
            print(f"  {C:>5} | {rate_ll:>25.6f} | {rate_lp:>25.6f}")

    # =========================================================================
    # Analysis 6: Record high stopping times and their mod structure
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 6: 停止時間記録保持者の mod 構造")
    print("=" * 70)

    N = 10**6
    record_st = 0
    records = []

    for n in range(3, N + 1, 2):
        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1

        if st > record_st:
            record_st = st
            records.append((n, st))

    print(f"\n  停止時間の記録保持者 (N={N:,}):")
    print(f"  {'n':>12} | {'TST':>6} | {'n mod 3':>8} | {'n mod 6':>8} | {'n mod 12':>8} | {'n mod 16':>8}")
    print("  " + "-" * 65)
    for n, st in records[-20:]:
        print(f"  {n:>12,} | {st:>6} | {n%3:>8} | {n%6:>8} | {n%12:>8} | {n%16:>8}")

    # =========================================================================
    # Analysis 7: 精密な降下速度とバリアンスの比較
    # =========================================================================
    print("\n" + "=" * 70)
    print("Analysis 7: 1-step Syracuse 降下率の精密計算")
    print("理論: E[log2(T/n)] = -1 + sum_{j>=1} log2(1 + 2^{-j}/3) * 2^{-j}")
    print("=" * 70)

    N = 10**7
    t0 = time.time()

    sum_log_ratio = 0.0
    sum_log_ratio_sq = 0.0
    count = 0

    for n in range(3, N + 1, 2):
        val = 3 * n + 1
        v2 = 0
        tmp = val
        while tmp % 2 == 0:
            tmp //= 2
            v2 += 1
        tn = tmp  # T(n) = (3n+1)/2^v2

        lr = math.log2(tn / n) if tn > 0 else 0
        sum_log_ratio += lr
        sum_log_ratio_sq += lr * lr
        count += 1

    mean_lr = sum_log_ratio / count
    var_lr = sum_log_ratio_sq / count - mean_lr * mean_lr
    std_lr = math.sqrt(var_lr)

    # Theoretical value
    theory_mean = math.log2(3) - 2  # = log2(3/4) ≈ -0.41504

    elapsed = time.time() - t0
    print(f"  N = {N:,}, 計算時間: {elapsed:.1f}s")
    print(f"  数値計算:  E[log2(T/n)] = {mean_lr:.8f}")
    print(f"  理論値:    log2(3) - 2  = {theory_mean:.8f}")
    print(f"  差分:                     {mean_lr - theory_mean:.8f}")
    print(f"  標準偏差:  Std[log2(T/n)] = {std_lr:.6f}")

    # v2 distribution
    print(f"\n  v2(3n+1) の分布:")
    v2_counts = defaultdict(int)
    for n in range(3, min(N, 10**6) + 1, 2):
        val = 3 * n + 1
        v2 = 0
        while val % 2 == 0:
            val //= 2
            v2 += 1
        v2_counts[v2] += 1

    total_v2 = sum(v2_counts.values())
    print(f"  {'v2':>4} | {'count':>10} | {'freq':>10} | {'theory 2^-v2':>12}")
    print("  " + "-" * 45)
    for v2 in sorted(v2_counts.keys()):
        freq = v2_counts[v2] / total_v2
        theory = 2**(-v2)
        print(f"  {v2:>4} | {v2_counts[v2]:>10} | {freq:>10.6f} | {theory:>12.6f}")

    print("\n完了")

if __name__ == "__main__":
    main()
