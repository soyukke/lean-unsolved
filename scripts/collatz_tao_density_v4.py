"""
Tao 2019 精密化 v4: 核心発見のまとめと追加検証

Key discoveries so far:
1. k_min(N, C) ~ alpha * log(N) のスケーリング (Fで発見)
2. 停止時間記録保持者の mod 構造に明確なバイアス (Bで発見)
   - mod 4: r=3 が r=1 の約2倍
   - mod 16: r=15 が圧倒的
3. TST tail decay lambda ~ 0.083 > 理論 0.0735
4. 8-bit pattern 01010101 (=85) が最低TST

追加検証:
- k_min(N, C) のスケーリング精密測定
- mod 4 ≡ 3 のバイアスの理論的説明
- 高1-bit密度と高TSTの相関の定量化
"""

import math
from collections import defaultdict
import time

def main():
    # =========================================================================
    # G. k_min(N, C) のスケーリング法則の精密測定
    # =========================================================================
    print("=" * 70)
    print("G. k_min(N, C) のスケーリング法則")
    print("全 n<=N で Col_min_k(n) < log(n)^C を満たす最小の k")
    print("=" * 70)

    C_values = [2, 3, 5]

    # Use the worst-case n at each N (the one requiring the most steps)
    N_test = [100, 300, 1000, 3000, 10000, 30000, 100000]

    for C in C_values:
        print(f"\n  f(n) = log(n)^{C}:")
        print(f"  {'N':>10} | {'k_min':>6} | {'worst_n':>10} | {'TST(worst)':>10} | {'k/log(N)':>10}")
        print("  " + "-" * 60)

        for N in N_test:
            worst_n = -1
            worst_k = 0

            for n in range(3, N + 1, 2):
                threshold = math.log(n) ** C

                current = n
                min_so_far = n
                steps_needed = -1

                for s in range(1, 500):
                    if current == 1:
                        min_so_far = 1
                        if min_so_far < threshold:
                            steps_needed = s
                            break
                        break
                    val = 3 * current + 1
                    while val % 2 == 0:
                        val //= 2
                    current = val
                    if current < min_so_far:
                        min_so_far = current
                    if min_so_far < threshold:
                        steps_needed = s
                        break

                if steps_needed == -1:
                    steps_needed = 500  # fallback

                if steps_needed > worst_k:
                    worst_k = steps_needed
                    worst_n = n

            # Also compute TST of worst_n
            if worst_n > 0:
                current = worst_n
                tst = 0
                while current != 1 and tst < 10000:
                    val = 3 * current + 1
                    while val % 2 == 0:
                        val //= 2
                    current = val
                    tst += 1

                ratio = worst_k / math.log(N) if N > 1 else 0
                print(f"  {N:>10,} | {worst_k:>6} | {worst_n:>10,} | {tst:>10} | {ratio:>10.4f}")

    # =========================================================================
    # H. mod 4 ≡ 3 バイアスの理論的説明
    # =========================================================================
    print("\n" + "=" * 70)
    print("H. mod 4 ≡ 3 のバイアスの理論的説明")
    print("n ≡ 3 (mod 4) => T(n) = (3n+1)/2 (v2=1のみ)")
    print("n ≡ 1 (mod 4) => T(n) = (3n+1)/4 (v2>=2)")
    print("=> n ≡ 3 は1ステップでの降下が小さい => 高TST")
    print("=" * 70)

    N = 500000

    # Verify: average TST by mod 4
    tst_by_mod4 = {1: [], 3: []}
    for n in range(3, N + 1, 2):
        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1
        tst_by_mod4[n % 4].append(st)

    for r in [1, 3]:
        sts = tst_by_mod4[r]
        mean = sum(sts) / len(sts)
        print(f"  n ≡ {r} (mod 4): count={len(sts):,}, mean TST = {mean:.2f}")

    # First step behavior
    print(f"\n  1ステップ降下率 by mod 4:")
    for r in [1, 3]:
        ratios = []
        for n in range(r, min(N, 100000) + 1, 4):
            if n < 3:
                continue
            val = 3 * n + 1
            v2 = 0
            while val % 2 == 0:
                val //= 2
                v2 += 1
            tn = val
            ratios.append(math.log2(tn / n))
        mean_r = sum(ratios) / len(ratios) if ratios else 0
        print(f"  n ≡ {r} (mod 4): E[log2(T/n)] = {mean_r:.6f}")

    # Verify: mod 8 decomposition
    print(f"\n  1ステップ降下率 by mod 8:")
    for r in [1, 3, 5, 7]:
        ratios = []
        for n in range(r, min(N, 100000) + 1, 8):
            if n < 3:
                continue
            val = 3 * n + 1
            v2 = 0
            while val % 2 == 0:
                val //= 2
                v2 += 1
            tn = val
            ratios.append(math.log2(tn / n))
        mean_r = sum(ratios) / len(ratios) if ratios else 0
        # Exact: n ≡ r (mod 8), 3n+1 mod 8
        residue_3n1 = (3 * r + 1) % 8
        v2_exact = 0
        tmp = 3 * r + 1
        while tmp % 2 == 0:
            tmp //= 2
            v2_exact += 1
        print(f"  n ≡ {r} (mod 8): E[log2(T/n)] = {mean_r:.6f}, v2(3r+1)={v2_exact}, 3r+1={3*r+1}")

    # =========================================================================
    # I. 1-bit density vs TST の相関
    # =========================================================================
    print("\n" + "=" * 70)
    print("I. 2進表現の1密度 vs 全停止時間の相関")
    print("=" * 70)

    N = 200000
    density_tst_pairs = []

    for n in range(3, N + 1, 2):
        bits = bin(n)[2:]
        density = bits.count('1') / len(bits)

        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1

        density_tst_pairs.append((density, st))

    # Group by density bins
    bins = defaultdict(list)
    for d, st in density_tst_pairs:
        b = round(d * 20) / 20  # bin to nearest 0.05
        bins[b].append(st)

    print(f"\n  1-bit density (binned) vs mean TST:")
    print(f"  {'density':>8} | {'count':>8} | {'mean TST':>10} | {'std TST':>10}")
    print("  " + "-" * 45)

    for d in sorted(bins.keys()):
        sts = bins[d]
        if len(sts) >= 10:
            mean_st = sum(sts) / len(sts)
            var_st = sum((s - mean_st)**2 for s in sts) / len(sts)
            std_st = math.sqrt(var_st)
            print(f"  {d:>8.2f} | {len(sts):>8} | {mean_st:>10.2f} | {std_st:>10.2f}")

    # Correlation coefficient
    mean_d = sum(d for d, _ in density_tst_pairs) / len(density_tst_pairs)
    mean_st = sum(st for _, st in density_tst_pairs) / len(density_tst_pairs)
    cov = sum((d - mean_d) * (st - mean_st) for d, st in density_tst_pairs) / len(density_tst_pairs)
    var_d = sum((d - mean_d)**2 for d, _ in density_tst_pairs) / len(density_tst_pairs)
    var_st = sum((st - mean_st)**2 for _, st in density_tst_pairs) / len(density_tst_pairs)
    corr = cov / math.sqrt(var_d * var_st) if var_d > 0 and var_st > 0 else 0

    print(f"\n  相関係数 r(1-bit density, TST) = {corr:.6f}")

    # =========================================================================
    # J. 連続1のパターンと TST の関係
    # =========================================================================
    print("\n" + "=" * 70)
    print("J. 末尾連続1の数 vs 全停止時間")
    print("末尾が111...1 のnは3n+1で大きく増加 => 高TST?")
    print("=" * 70)

    N = 200000
    trailing_ones_tst = defaultdict(list)

    for n in range(3, N + 1, 2):
        # Count trailing 1s
        tmp = n
        trailing = 0
        while tmp & 1:
            trailing += 1
            tmp >>= 1

        current = n
        st = 0
        while current != 1 and st < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            st += 1

        trailing_ones_tst[trailing].append(st)

    print(f"\n  {'trailing 1s':>12} | {'count':>8} | {'mean TST':>10} | {'std TST':>10}")
    print("  " + "-" * 50)
    for t in sorted(trailing_ones_tst.keys()):
        sts = trailing_ones_tst[t]
        mean_st = sum(sts) / len(sts)
        var_st = sum((s - mean_st)**2 for s in sts) / len(sts)
        std_st = math.sqrt(var_st)
        print(f"  {t:>12} | {len(sts):>8} | {mean_st:>10.2f} | {std_st:>10.2f}")

    # =========================================================================
    # K. 理論的予測: Taoの密度の定量的下界
    # =========================================================================
    print("\n" + "=" * 70)
    print("K. Tao密度の定量的下界推定")
    print("P(Col_min(n) < f(n)) >= 1 - g(N) の g(N) の推定")
    print("=" * 70)

    # From Analysis D (v3), k-step到達率 at fixed k=10, f=log(n)^2
    # 到達率 decreases as N increases (because log(n)^2 grows slower than typical descent)
    # But with unlimited steps (total stopping), rate = 1 for all tested N

    # Key insight: the fraction of n in [1,N] whose TST > T
    # gives P(TST > T), and if T is large enough that n -> f(n) in T steps,
    # we get the density

    # Estimate: what fraction of n <= N reach log(n)^C within T steps?
    print(f"\n  f(n)=log(n)^2 到達に必要な最大ステップ数の分布 (N=100,000):")

    N = 100000
    steps_to_reach = []
    for n in range(3, N + 1, 2):
        threshold = math.log(n) ** 2
        current = n
        min_so_far = n
        steps = 0

        while min_so_far >= threshold and steps < 1000:
            if current == 1:
                min_so_far = 1
                break
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            if current < min_so_far:
                min_so_far = current
            steps += 1

        steps_to_reach.append(steps)

    steps_to_reach.sort()
    n_total = len(steps_to_reach)
    mean_steps = sum(steps_to_reach) / n_total
    max_steps = steps_to_reach[-1]

    print(f"  平均ステップ: {mean_steps:.2f}")
    print(f"  最大ステップ: {max_steps}")
    print(f"  中央値: {steps_to_reach[n_total//2]}")

    print(f"\n  ステップ数の累積分布:")
    print(f"  {'k':>6} | {'P(steps<=k)':>14}")
    print("  " + "-" * 25)
    for k in [1, 2, 5, 10, 20, 50, 100, 150, 200]:
        count = sum(1 for s in steps_to_reach if s <= k)
        frac = count / n_total
        print(f"  {k:>6} | {frac:>14.6f}")

    # Compare with TST distribution
    print(f"\n  到達ステップ vs TST の比較:")
    print(f"  到達ステップ = min k such that min(T^0,...,T^k) < log(n)^2")
    print(f"  TST = steps to reach 1")
    print(f"  到達ステップ / TST の平均比率:")

    N = 50000
    ratio_sum = 0
    count = 0
    for n in range(3, N + 1, 2):
        threshold = math.log(n) ** 2
        current = n
        min_so_far = n
        reach_step = 0

        for s in range(1, 1000):
            if current == 1:
                min_so_far = 1
                break
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            if current < min_so_far:
                min_so_far = current
            if min_so_far < threshold and reach_step == 0:
                reach_step = s

        # TST
        current = n
        tst = 0
        while current != 1 and tst < 10000:
            val = 3 * current + 1
            while val % 2 == 0:
                val //= 2
            current = val
            tst += 1

        if tst > 0 and reach_step > 0:
            ratio_sum += reach_step / tst
            count += 1

    if count > 0:
        print(f"  平均(到達ステップ/TST) = {ratio_sum/count:.4f}")

    print("\n完了")

if __name__ == "__main__":
    main()
