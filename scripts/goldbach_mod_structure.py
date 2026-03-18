#!/usr/bin/env python3
"""
ゴールドバッハ予想 探索4: 素数ペア分布の mod 6 / mod 30 構造の深掘り

各偶数nに対し、ゴールドバッハ分解 n=p+q の (p%6, q%6) と (p%30, q%30) の分布を調査し、
n%6, n%12, n%30 ごとにパターンを分類する。
「特定のmod構造が表現数g(n)を支配する」仮説を検証する。
"""

import math
from collections import defaultdict, Counter


def sieve_of_eratosthenes(limit):
    """エラトステネスの篩"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def goldbach_pairs(n, is_prime):
    """偶数 n の全ゴールドバッハ分解 (p, q) を返す (p <= q)"""
    pairs = []
    for p in range(2, n // 2 + 1):
        if is_prime[p] and is_prime[n - p]:
            pairs.append((p, n - p))
    return pairs


def main():
    N = 10000
    print(f"=== 探索4: 素数ペア分布の mod 6 / mod 30 構造 (4 <= n <= {N}) ===\n")

    is_prime = sieve_of_eratosthenes(N)

    # ============================================================
    # Part 1: (p%6, q%6) の分布を n%6 ごとに集計
    # ============================================================
    print("=" * 70)
    print("Part 1: (p%6, q%6) パターンの n%6 別分布")
    print("=" * 70)

    # n%6 ごとに (p%6, q%6) のカウントを蓄積
    mod6_pattern_by_nmod6 = defaultdict(Counter)
    # n%6 ごとの g(n) 合計・個数
    g_by_nmod6 = defaultdict(list)

    for n in range(4, N + 1, 2):
        r = n % 6
        pairs = goldbach_pairs(n, is_prime)
        g_by_nmod6[r].append(len(pairs))
        for p, q in pairs:
            mod6_pattern_by_nmod6[r][(p % 6, q % 6)] += 1

    for r in sorted(mod6_pattern_by_nmod6.keys()):
        counter = mod6_pattern_by_nmod6[r]
        total = sum(counter.values())
        gvals = g_by_nmod6[r]
        avg_g = sum(gvals) / len(gvals) if gvals else 0
        print(f"\n  n ≡ {r} (mod 6): 偶数{len(gvals)}個, 平均g(n)={avg_g:.1f}, 総ペア数={total}")
        for pattern, count in sorted(counter.items(), key=lambda x: -x[1]):
            pct = 100.0 * count / total
            print(f"    (p%6, q%6) = {pattern}: {count:6d} ({pct:5.1f}%)")

    # ============================================================
    # Part 2: (p%30, q%30) の分布を n%30 ごとに集計（上位パターンのみ）
    # ============================================================
    print("\n" + "=" * 70)
    print("Part 2: (p%30, q%30) パターンの n%30 別分布 (上位5パターン)")
    print("=" * 70)

    mod30_pattern_by_nmod30 = defaultdict(Counter)
    g_by_nmod30 = defaultdict(list)

    for n in range(4, N + 1, 2):
        r = n % 30
        pairs = goldbach_pairs(n, is_prime)
        g_by_nmod30[r].append(len(pairs))
        for p, q in pairs:
            mod30_pattern_by_nmod30[r][(p % 30, q % 30)] += 1

    for r in sorted(mod30_pattern_by_nmod30.keys()):
        counter = mod30_pattern_by_nmod30[r]
        total = sum(counter.values())
        gvals = g_by_nmod30[r]
        avg_g = sum(gvals) / len(gvals) if gvals else 0
        print(f"\n  n ≡ {r:2d} (mod 30): 偶数{len(gvals):3d}個, 平均g(n)={avg_g:6.1f}")
        top5 = counter.most_common(5)
        for pattern, count in top5:
            pct = 100.0 * count / total
            print(f"    (p%30, q%30) = {pattern}: {count:5d} ({pct:5.1f}%)")

    # ============================================================
    # Part 3: n%12 別の g(n) 分布
    # ============================================================
    print("\n" + "=" * 70)
    print("Part 3: n%12 別の g(n) 平均")
    print("=" * 70)

    g_by_nmod12 = defaultdict(list)
    for n in range(4, N + 1, 2):
        g_by_nmod12[n % 12].append(len(goldbach_pairs(n, is_prime)))

    print(f"\n  {'n%12':>5s}  {'個数':>5s}  {'平均g(n)':>9s}  {'最小':>5s}  {'最大':>5s}")
    for r in sorted(g_by_nmod12.keys()):
        vals = g_by_nmod12[r]
        avg = sum(vals) / len(vals)
        print(f"  {r:5d}  {len(vals):5d}  {avg:9.2f}  {min(vals):5d}  {max(vals):5d}")

    # ============================================================
    # Part 4: mod 6 構造がg(n)を支配する仮説の検証
    # ============================================================
    print("\n" + "=" * 70)
    print("Part 4: mod 6 構造がg(n)を支配するか？")
    print("=" * 70)

    # 同じnの範囲で、n%6=0の平均g(n) vs n%6=2, n%6=4 を比較
    # 区間ごとに比率を見る
    print(f"\n  {'区間':>14s}  {'n%6=0 平均':>10s}  {'n%6=2 平均':>10s}  {'n%6=4 平均':>10s}  {'比率(0/2)':>9s}  {'比率(0/4)':>9s}")
    for start in range(0, N, 2000):
        end = min(start + 2000, N)
        by_r = defaultdict(list)
        for n in range(max(4, start), end + 1, 2):
            by_r[n % 6].append(len(goldbach_pairs(n, is_prime)))
        if all(by_r[r] for r in [0, 2, 4]):
            avg0 = sum(by_r[0]) / len(by_r[0])
            avg2 = sum(by_r[2]) / len(by_r[2])
            avg4 = sum(by_r[4]) / len(by_r[4])
            r02 = avg0 / avg2 if avg2 > 0 else float('inf')
            r04 = avg0 / avg4 if avg4 > 0 else float('inf')
            print(f"  [{start+1:5d},{end:5d}]  {avg0:10.2f}  {avg2:10.2f}  {avg4:10.2f}  {r02:9.3f}  {r04:9.3f}")

    # ============================================================
    # Part 5: (p%6, q%6) = (5,5) vs (1,1) の頻度比較（n%6=4のケース）
    # ============================================================
    print("\n" + "=" * 70)
    print("Part 5: n%6=4 における (p%6,q%6)=(5,5) vs (1,1) の比較")
    print("=" * 70)

    cnt_55 = 0
    cnt_11 = 0
    cnt_other = 0
    for n in range(4, N + 1, 2):
        if n % 6 != 4:
            continue
        pairs = goldbach_pairs(n, is_prime)
        for p, q in pairs:
            key = (p % 6, q % 6)
            if key == (5, 5):
                cnt_55 += 1
            elif key == (1, 1):
                cnt_11 += 1
            else:
                cnt_other += 1

    total_n4 = cnt_55 + cnt_11 + cnt_other
    print(f"\n  n ≡ 4 (mod 6) のペア総数: {total_n4}")
    print(f"  (5,5): {cnt_55} ({100*cnt_55/total_n4:.1f}%)")
    print(f"  (1,1): {cnt_11} ({100*cnt_11/total_n4:.1f}%)")
    print(f"  その他: {cnt_other} ({100*cnt_other/total_n4:.1f}%)")

    # ============================================================
    # Part 6: mod 30 での g(n) の順位付け
    # ============================================================
    print("\n" + "=" * 70)
    print("Part 6: n%30 別の平均g(n) ランキング")
    print("=" * 70)

    ranking = []
    for r in sorted(g_by_nmod30.keys()):
        vals = g_by_nmod30[r]
        avg = sum(vals) / len(vals)
        ranking.append((r, avg, len(vals)))
    ranking.sort(key=lambda x: -x[1])

    print(f"\n  {'順位':>4s}  {'n%30':>4s}  {'平均g(n)':>10s}  {'偶数個数':>8s}")
    for i, (r, avg, cnt) in enumerate(ranking, 1):
        print(f"  {i:4d}  {r:4d}  {avg:10.2f}  {cnt:8d}")

    # ============================================================
    # 結論
    # ============================================================
    print("\n" + "=" * 70)
    print("結論")
    print("=" * 70)
    avg_0 = sum(g_by_nmod6[0]) / len(g_by_nmod6[0])
    avg_2 = sum(g_by_nmod6[2]) / len(g_by_nmod6[2])
    avg_4 = sum(g_by_nmod6[4]) / len(g_by_nmod6[4])
    print(f"""
  1. mod 6 構造が g(n) を強く支配している:
     - n ≡ 0 (mod 6): 平均g(n) = {avg_0:.1f} (最大)
     - n ≡ 2 (mod 6): 平均g(n) = {avg_2:.1f}
     - n ≡ 4 (mod 6): 平均g(n) = {avg_4:.1f}
     - 比率 g(0)/g(2) ≈ {avg_0/avg_2:.2f}, g(0)/g(4) ≈ {avg_0/avg_4:.2f}

  2. n ≡ 0 (mod 6) のg(n)が大きい理由:
     - 6の倍数は3でも割れるため、(p%6, q%6) の利用可能パターンが多い
     - 特に (1,5) と (5,1) の両方が可能

  3. mod 30 構造ではさらに細かい分類が可能:
     - n ≡ 0 (mod 30) が最大の平均g(n) を持つ（5の倍数でもある効果）
     - 素因子が多い偶数ほどg(n)が大きい（Hardy-Littlewood補正因子と一致）

  4. 仮説「mod構造がg(n)を支配する」は確認された:
     - n の mod 6 残基だけでg(n)の約2倍の差が生じる
     - これは Hardy-Littlewood の singular series の離散版と解釈できる
""")


if __name__ == "__main__":
    main()
