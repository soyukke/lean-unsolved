"""
Tao 2019 精密化 v3: 発見された異常の深堀り

Key findings from v2:
1. k-step降下比率がk>=20で理論から大きく乖離する
   k=50: 実測 -12.76 vs 理論 -20.75
   -> 軌道が1に到達すると降下が止まるため
2. 停止時間記録保持者に mod 3 = 0 が顕著
3. P(TST > t) の指数減衰率が理論値 0.0735 より小さい

深堀り:
A. 1に到達しない条件付きk-step降下比率（1に到達前のステップのみ）
B. 停止時間記録保持者の mod 構造の統計的検定
C. 例外集合密度の精密なスケーリング
D. Tao理論の定量化: stopping time分布のフィッティング
"""

import math
from collections import defaultdict
import time

def main():
    # =========================================================================
    # A. 条件付きk-step降下比率（1到達前のみ）
    # =========================================================================
    print("=" * 70)
    print("A. 条件付きk-step降下比率 (1に到達しない軌道のみ)")
    print("=" * 70)

    N = 200000
    k_test = [5, 10, 20, 50, 100]

    for k in k_test:
        log_ratios = []
        count_survived = 0
        count_reached_1 = 0

        for n in range(3, N + 1, 2):
            current = n
            survived = True
            for _ in range(k):
                if current == 1:
                    survived = False
                    break
                val = 3 * current + 1
                while val % 2 == 0:
                    val //= 2
                current = val

            if survived and current > 0:
                lr = math.log2(current / n)
                log_ratios.append(lr)
                count_survived += 1
            else:
                count_reached_1 += 1

        total = count_survived + count_reached_1
        frac_survived = count_survived / total

        if log_ratios:
            mean_lr = sum(log_ratios) / len(log_ratios)
            var_lr = sum((x - mean_lr)**2 for x in log_ratios) / len(log_ratios)
            std_lr = math.sqrt(var_lr)
            theory = k * (-0.41504)
            print(f"  k={k:>3}: survived={frac_survived:.4f}, E[log2]={mean_lr:>8.4f} (理論: {theory:>8.4f}), std={std_lr:.4f}")
        else:
            print(f"  k={k:>3}: 全て1に到達")

    # =========================================================================
    # B. 停止時間記録保持者の mod 構造の統計的検定
    # =========================================================================
    print("\n" + "=" * 70)
    print("B. 高停止時間 n の mod 構造解析 (上位1%, 5%, 10%)")
    print("=" * 70)

    N = 500000
    t0 = time.time()

    # Compute all total stopping times
    all_tst = []
    for n in range(3, N + 1, 2):
        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1
        all_tst.append((n, st))

    elapsed = time.time() - t0
    print(f"N={N:,}, 計算時間: {elapsed:.1f}s")

    # Sort by TST
    all_tst.sort(key=lambda x: -x[1])
    total_odd = len(all_tst)

    for pct in [1, 5, 10]:
        top_count = max(1, total_odd * pct // 100)
        top_set = all_tst[:top_count]

        print(f"\n  上位 {pct}% (TST >= {top_set[-1][1]}), {top_count} 個:")

        for M in [3, 4, 6, 8, 12, 16, 24, 48]:
            mod_dist = defaultdict(int)
            for n, _ in top_set:
                mod_dist[n % M] += 1

            # Compare with uniform expectation
            expected = top_count / M
            sorted_mods = sorted(mod_dist.items(), key=lambda x: -x[1])

            # Find significantly over/under-represented residues
            significant = []
            for r, c in sorted_mods:
                z = (c - expected) / math.sqrt(expected) if expected > 0 else 0
                if abs(z) > 3:  # > 3 sigma
                    significant.append((r, c, z))

            if significant:
                sig_str = ", ".join(f"r={r}: {c} (z={z:.1f})" for r, c, z in significant[:5])
                print(f"    mod {M:>2}: {sig_str}")

    # =========================================================================
    # C. TST分布の精密フィッティング
    # =========================================================================
    print("\n" + "=" * 70)
    print("C. 全停止時間の分布フィッティング")
    print("=" * 70)

    tst_values = [st for _, st in all_tst]
    tst_values.sort()

    # Histogram
    max_tst = tst_values[-1]
    bins = defaultdict(int)
    for st in tst_values:
        bins[st] += 1

    print(f"\n  TST 分布 (N={N:,}):")
    print(f"  {'TST':>6} | {'count':>8} | {'P(TST=t)':>12} | {'P(TST>t)':>12} | {'-ln(P>t)/t':>12}")
    print("  " + "-" * 60)

    cum_above = total_odd
    for t in range(0, max_tst + 1, 5):
        count_at = sum(bins.get(s, 0) for s in range(t, t+5))
        cum_above -= count_at
        p_above = cum_above / total_odd
        p_at = count_at / (5 * total_odd)
        if p_above > 0 and t > 0:
            lam = -math.log(p_above) / t
            print(f"  {t:>6} | {count_at:>8} | {p_at:>12.6f} | {p_above:>12.6f} | {lam:>12.6f}")
        elif t <= 30:
            print(f"  {t:>6} | {count_at:>8} | {p_at:>12.6f} | {p_above:>12.6f} |")

    # Fit exponential decay P(TST > t) ~ exp(-lambda * t) for t > 30
    print("\n  尾部指数減衰フィッティング (t > 30):")
    log_points = []
    cum_above = total_odd
    for t in range(max_tst + 1):
        if t in bins:
            cum_above -= bins[t]
        if t > 30 and cum_above > 10:  # Need enough data
            log_points.append((t, math.log(cum_above / total_odd)))

    if len(log_points) >= 2:
        xs = [p[0] for p in log_points]
        ys = [p[1] for p in log_points]
        n_pts = len(xs)
        sx = sum(xs)
        sy = sum(ys)
        sxx = sum(x*x for x in xs)
        sxy = sum(x*y for x, y in zip(xs, ys))
        denom = n_pts * sxx - sx * sx
        slope = (n_pts * sxy - sx * sy) / denom if denom != 0 else 0
        intercept = (sy - slope * sx) / n_pts

        lambda_fit = -slope
        print(f"  フィット lambda = {lambda_fit:.6f}")
        print(f"  理論値 lambda = 0.0735")
        print(f"  比率 = {lambda_fit / 0.0735:.4f}")

    # =========================================================================
    # D. k-step到達率のNスケーリング
    # =========================================================================
    print("\n" + "=" * 70)
    print("D. k-step到達率のNスケーリング (k固定, N増加)")
    print("f(n) = log(n)^2 で k=10 Syracuse steps")
    print("=" * 70)

    k = 10
    C = 2
    checkpoints = [1000, 3000, 10000, 30000, 100000, 300000, 1000000]

    print(f"\n  {'N':>10} | {'到達率':>12} | {'例外率':>12} | {'例外数':>8}")
    print("  " + "-" * 50)

    for N in checkpoints:
        total = 0
        reach = 0
        for n in range(3, N + 1, 2):
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
            threshold = math.log(n) ** C
            if min_k < threshold:
                reach += 1

        rate = reach / total
        exc = total - reach
        exc_rate = exc / total
        print(f"  {N:>10,} | {rate:>12.6f} | {exc_rate:>12.6f} | {exc:>8,}")

    # =========================================================================
    # E. 停止時間と初期値の2進構造の相関
    # =========================================================================
    print("\n" + "=" * 70)
    print("E. 停止時間と初期値の2進構造の相関")
    print("=" * 70)

    N = 200000
    # Group by trailing bits
    print(f"\n  最下位ビットパターン vs 平均停止時間 (N={N:,}):")
    print(f"  {'pattern':>10} | {'count':>8} | {'mean TST':>10} | {'std TST':>10}")
    print("  " + "-" * 50)

    bit_groups = defaultdict(list)
    for n in range(3, N + 1, 2):
        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1

        # Trailing 4 bits (n is odd, so LSB=1)
        pattern = n & 0xF  # lower 4 bits
        bit_groups[pattern].append(st)

    for pattern in sorted(bit_groups.keys()):
        if pattern % 2 == 0:
            continue  # only odd
        sts = bit_groups[pattern]
        mean_st = sum(sts) / len(sts)
        var_st = sum((s - mean_st)**2 for s in sts) / len(sts)
        std_st = math.sqrt(var_st)
        bits = bin(pattern)[2:].zfill(4)
        print(f"  {bits:>10} | {len(sts):>8} | {mean_st:>10.2f} | {std_st:>10.2f}")

    # 8-bit patterns
    print(f"\n  最下位8ビット vs 平均TST (top/bottom 10):")
    bit_groups8 = defaultdict(list)
    for n in range(3, N + 1, 2):
        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1

        pattern = n & 0xFF
        bit_groups8[pattern].append(st)

    mean_by_pattern = {}
    for pattern, sts in bit_groups8.items():
        if len(sts) >= 10:
            mean_by_pattern[pattern] = sum(sts) / len(sts)

    sorted_patterns = sorted(mean_by_pattern.items(), key=lambda x: -x[1])

    print(f"\n  高TST パターン:")
    for pattern, mean_st in sorted_patterns[:10]:
        bits = bin(pattern)[2:].zfill(8)
        count = len(bit_groups8[pattern])
        print(f"    {bits} ({pattern:>3}): mean TST = {mean_st:.2f}, count = {count}")

    print(f"\n  低TST パターン:")
    for pattern, mean_st in sorted_patterns[-10:]:
        bits = bin(pattern)[2:].zfill(8)
        count = len(bit_groups8[pattern])
        print(f"    {bits} ({pattern:>3}): mean TST = {mean_st:.2f}, count = {count}")

    # =========================================================================
    # F. 核心分析: Tao密度結果の定量的精密化
    # =========================================================================
    print("\n" + "=" * 70)
    print("F. Tao密度結果の定量的精密化")
    print("Col_min(n) < f(n) が「いつから」全てのnで成立するか")
    print("=" * 70)

    # For various f(n), find the largest n that fails
    # Since all n <= 10^7 reach 1, Col_min = 1 for all
    # So the question becomes: Col_min_k(n) < f(n) for finite k
    # What is the smallest k(N) such that ALL n <= N satisfy Col_min_k < f(n)?

    for C in [2, 3, 5]:
        print(f"\n  f(n) = log(n)^{C}:")
        for N in [1000, 10000, 100000, 1000000]:
            # Find minimum k such that ALL odd n in [3,N] have Col_min_k < log(n)^C
            for k_try in range(1, 500):
                all_pass = True
                for n in range(3, N + 1, 2):
                    current = n
                    min_k = n
                    for s in range(k_try):
                        if current == 1:
                            min_k = 1
                            break
                        val = 3 * current + 1
                        while val % 2 == 0:
                            val //= 2
                        current = val
                        if current < min_k:
                            min_k = current
                    threshold = math.log(n) ** C
                    if min_k >= threshold:
                        all_pass = False
                        break  # Found a failure

                if all_pass:
                    print(f"    N={N:>10,}: 最小 k = {k_try}")
                    break

                if k_try == 499:
                    print(f"    N={N:>10,}: k=500 でも不十分")

    print("\n完了")

if __name__ == "__main__":
    main()
