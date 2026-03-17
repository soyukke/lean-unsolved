#!/usr/bin/env python3
"""
ゴールドバッハ予想 探索1-2: 小さい偶数での網羅検証と分析

- 4から10000までの偶数でゴールドバッハ予想を検証
- 各偶数に対する素数ペアの数（ゴールドバッハ関数 g(n)）を計算
- g(n)の最小値を持つ偶数を特定
- g(n)の成長パターンを分析
"""

import math
from collections import defaultdict


def sieve_of_eratosthenes(limit):
    """エラトステネスの篩で limit 以下の素数を列挙"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime


def goldbach_pairs(n, is_prime):
    """偶数 n を2つの素数の和で表す全ペア (p, q) を返す (p <= q)"""
    pairs = []
    for p in range(2, n // 2 + 1):
        if is_prime[p] and is_prime[n - p]:
            pairs.append((p, n - p))
    return pairs


def main():
    N = 10000
    print(f"=== ゴールドバッハ予想の検証: 4 ≤ n ≤ {N} (偶数) ===\n")

    # 篩の計算
    is_prime = sieve_of_eratosthenes(N)
    primes = [p for p in range(2, N + 1) if is_prime[p]]
    print(f"素数の数 (≤ {N}): {len(primes)}")
    print(f"最大の素数: {primes[-1]}\n")

    # 全偶数の検証
    g_values = {}  # n -> g(n) = 素数ペア数
    min_pair_examples = {}  # n -> 最小の素数ペア
    counterexamples = []

    for n in range(4, N + 1, 2):
        pairs = goldbach_pairs(n, is_prime)
        g_values[n] = len(pairs)
        if pairs:
            min_pair_examples[n] = pairs[0]
        else:
            counterexamples.append(n)

    # 結果
    if counterexamples:
        print(f"⚠ 反例発見: {counterexamples}")
    else:
        print(f"✓ 4 ≤ n ≤ {N} の全偶数でゴールドバッハ予想が成立\n")

    # g(n) の最小値を持つ偶数
    print("=== g(n) が小さい偶数（素数ペアが少ない） ===")
    sorted_by_g = sorted(g_values.items(), key=lambda x: (x[1], x[0]))
    for n, g in sorted_by_g[:20]:
        pairs = goldbach_pairs(n, is_prime)
        pairs_str = ", ".join(f"({p}+{q})" for p, q in pairs[:5])
        print(f"  n={n:5d}: g(n)={g:2d}  ペア: {pairs_str}")

    # g(n) が大きい偶数
    print("\n=== g(n) が大きい偶数（素数ペアが多い） ===")
    sorted_by_g_desc = sorted(g_values.items(), key=lambda x: (-x[1], x[0]))
    for n, g in sorted_by_g_desc[:10]:
        print(f"  n={n:5d}: g(n)={g:3d}")

    # 特定の偶数での例（Lean検証用）
    print("\n=== Lean検証用: 特定の偶数での素数ペア ===")
    test_values = [4, 6, 8, 10, 12, 14, 16, 18, 20, 30, 50, 100, 200, 1000]
    for n in test_values:
        pairs = goldbach_pairs(n, is_prime)
        first = pairs[0] if pairs else None
        print(f"  n={n:4d}: g(n)={len(pairs):3d}  最小ペア: {first}")

    # g(n) の統計
    print("\n=== g(n) の統計 ===")
    g_list = list(g_values.values())
    print(f"  最小値: {min(g_list)}")
    print(f"  最大値: {max(g_list)}")
    print(f"  平均値: {sum(g_list)/len(g_list):.2f}")

    # 区間ごとの g(n) の平均
    print("\n=== 区間ごとの g(n) の平均 ===")
    for start in range(0, N, 1000):
        end = start + 1000
        vals = [g_values[n] for n in range(max(4, start), min(end, N) + 1, 2) if n in g_values]
        if vals:
            avg = sum(vals) / len(vals)
            min_v = min(vals)
            max_v = max(vals)
            print(f"  [{start+1:5d}, {end:5d}]: 平均={avg:6.2f}, 最小={min_v:3d}, 最大={max_v:3d}")

    # 6k, 6k+2, 6k+4 別の分析
    print("\n=== mod 6 別の g(n) 平均 ===")
    for r in [0, 2, 4]:
        vals = [g_values[n] for n in range(4, N + 1, 2) if n % 6 == r]
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  n ≡ {r} (mod 6): 平均={avg:.2f}, 最小={min(vals)}, 個数={len(vals)}")

    # g(n) = 1 の偶数（ほぼ素数ペアがない）
    print("\n=== g(n) = 1 の偶数（唯一の素数ペア） ===")
    g1 = [(n, goldbach_pairs(n, is_prime)[0]) for n in range(4, N + 1, 2) if g_values[n] == 1]
    for n, (p, q) in g1[:20]:
        print(f"  n={n:5d}: {p} + {q}")
    if len(g1) > 20:
        print(f"  ... 他 {len(g1)-20} 個")
    print(f"  合計: {len(g1)} 個")

    # Hardyの予想 C_2 * n / (ln n)^2 との比較
    print("\n=== Hardy-Littlewood 予想との比較 ===")
    print("  Hardy-Littlewood 予想: g(n) ~ C₂ * n / (ln n)² × 補正項")
    print("  C₂ (双子素数定数) ≈ 1.3203")
    C2 = 1.3203236316
    print(f"  n      g(n)   HL近似   比率")
    for n in [100, 200, 500, 1000, 2000, 5000, 10000]:
        if n in g_values:
            ln_n = math.log(n)
            # Hardy-Littlewood の近似公式
            hl_approx = C2 * n / (ln_n ** 2)
            # 奇素数の積補正
            ratio = g_values[n] / hl_approx if hl_approx > 0 else 0
            print(f"  {n:5d}  {g_values[n]:5d}  {hl_approx:7.1f}  {ratio:.3f}")


if __name__ == "__main__":
    main()
