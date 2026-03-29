#!/usr/bin/env python3
"""
連続上昇回数の分布と極値統計: メルセンヌ数との関連

目的:
1. N=10^7まで奇数の連続上昇回数分布を計算
2. 最大連続上昇回数の成長率を log(N) と比較
3. メルセンヌ数 2^p - 1 (p素数) の軌道における連続上昇を調査
4. n ≡ 2^{k+1}-1 (mod 2^{k+1}) が k回連続上昇の必要十分条件を数値検証
"""

import math
import time
from collections import defaultdict, Counter

# ============================================================
# ユーティリティ関数
# ============================================================

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def consecutive_ascents(n):
    """
    連続上昇回数を計算。
    v2(3n+1) = 1 が続く回数を数える。
    v2=1 なら T(n) = (3n+1)/2 (上昇ステップ)。
    """
    if n % 2 == 0:
        return 0
    count = 0
    current = n
    while True:
        val = 3 * current + 1
        if v2(val) != 1:
            break
        count += 1
        current = val // 2  # 次の奇数(v2=1なので /2 で奇数)
    return count

def consecutive_ascents_in_trajectory(n, max_steps=10000):
    """
    軌道全体での最大連続上昇回数と、各連続上昇ブロックのリストを返す。
    """
    if n % 2 == 0:
        n = n // (2 ** v2(n))  # 奇数に変換
    if n <= 0:
        return 0, []

    ascent_blocks = []
    current = n
    max_ascent = 0
    steps = 0

    while current != 1 and steps < max_steps:
        asc = consecutive_ascents(current)
        if asc > 0:
            ascent_blocks.append(asc)
            max_ascent = max(max_ascent, asc)
        # 次のステップへ
        current = syracuse(current)
        steps += 1

    return max_ascent, ascent_blocks


def is_prime(n):
    """素数判定"""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# ============================================================
# Part 1: 連続上昇回数の分布 (N=10^7)
# ============================================================

def compute_ascent_distribution(N):
    """奇数 1,3,5,...,N の連続上昇回数の分布"""
    print(f"=== Part 1: 連続上昇回数の分布 (N={N:,}) ===")
    t0 = time.time()

    dist = Counter()
    max_k = 0
    max_k_n = 1

    for n in range(1, N + 1, 2):  # 奇数のみ
        k = consecutive_ascents(n)
        dist[k] += 1
        if k > max_k:
            max_k = k
            max_k_n = n

    elapsed = time.time() - t0
    total = sum(dist.values())

    print(f"計算時間: {elapsed:.2f}秒")
    print(f"総奇数数: {total:,}")
    print(f"最大連続上昇回数: {max_k} (n={max_k_n})")
    print()

    print("k | 個数 | 割合 | 理論値(1/2^k - 1/2^{k+1}) | 比")
    print("-" * 70)
    for k in sorted(dist.keys()):
        count = dist[k]
        ratio = count / total
        # k=0: 確率 1/2 (n ≡ 1 mod 4)
        # k≥1: 確率 1/2^{k+1} (ちょうどk回)
        if k == 0:
            theory = 1/2
        else:
            theory = 1 / (2 ** (k + 1))
        print(f"{k:2d} | {count:>10,} | {ratio:.6f} | {theory:.6f} | {ratio/theory:.4f}")

    return dist, max_k, max_k_n


# ============================================================
# Part 2: 最大連続上昇回数の成長率
# ============================================================

def compute_max_ascent_growth():
    """Nが増加するときの最大連続上昇回数の成長"""
    print(f"\n=== Part 2: 最大連続上昇回数の成長率 ===")
    t0 = time.time()

    # 各閾値での最大連続上昇回数を記録
    thresholds = [10**i for i in range(1, 8)]
    thresholds += [j * 10**i for i in range(2, 7) for j in [2, 5]]
    thresholds = sorted(set(thresholds))

    max_k = 0
    max_k_n = 1
    results = []
    threshold_idx = 0

    for n in range(1, 10**7 + 1, 2):
        k = consecutive_ascents(n)
        if k > max_k:
            max_k = k
            max_k_n = n

        while threshold_idx < len(thresholds) and n >= thresholds[threshold_idx]:
            N = thresholds[threshold_idx]
            log2N = math.log2(N)
            logN = math.log(N)
            results.append((N, max_k, max_k_n, log2N, logN))
            threshold_idx += 1

    # 最後の閾値を処理
    while threshold_idx < len(thresholds):
        N = thresholds[threshold_idx]
        if N <= 10**7:
            log2N = math.log2(N)
            logN = math.log(N)
            results.append((N, max_k, max_k_n, log2N, logN))
        threshold_idx += 1

    elapsed = time.time() - t0
    print(f"計算時間: {elapsed:.2f}秒")
    print()

    print(f"{'N':>12} | max_k | {'n':>12} | log2(N) | max_k/log2(N) | ln(N) | max_k/ln(N)")
    print("-" * 95)
    for N, mk, mkn, l2, lnN in results:
        r2 = mk / l2 if l2 > 0 else 0
        rln = mk / lnN if lnN > 0 else 0
        print(f"{N:>12,} | {mk:>5} | {mkn:>12,} | {l2:>7.2f} | {r2:>13.4f} | {lnN:>5.2f} | {rln:>10.4f}")

    return results


# ============================================================
# Part 3: mod条件の検証
# ============================================================

def verify_mod_condition(N=100000):
    """n ≡ 2^{k+1}-1 (mod 2^{k+1}) ⟺ k回連続上昇 の検証"""
    print(f"\n=== Part 3: mod条件の検証 (N={N:,}) ===")
    t0 = time.time()

    violations = 0
    for n in range(1, N + 1, 2):
        k_actual = consecutive_ascents(n)

        # 理論: k回連続上昇 ⟺ n ≡ 2^{k+1}-1 (mod 2^{k+1}) かつ
        #        n ≢ 2^{k+2}-1 (mod 2^{k+2}) (ちょうどk回)

        # もっと単純に: 下位ビットが連続する1の個数 = k
        # n = ...0 1...1 (末尾k+1個の1)のとき n ≡ 2^{k+1}-1 (mod 2^{k+1})

        # 末尾の連続する1の個数を数える
        trailing_ones = 0
        temp = n
        while temp & 1:
            trailing_ones += 1
            temp >>= 1

        # 奇数なので trailing_ones >= 1
        # k回連続上昇: trailing_ones = k + 1 ?
        # k=0: trailing_ones=1, n≡1(mod2) だが n≢3(mod4)
        # k=1: trailing_ones=2, n≡3(mod4) だが n≢7(mod8)
        # k=2: trailing_ones=3, n≡7(mod8) だが n≢15(mod16)

        # 正しい対応: k = trailing_ones - 1
        k_predicted = trailing_ones - 1

        if k_actual != k_predicted:
            if violations < 10:
                print(f"  不一致! n={n}, actual={k_actual}, predicted={k_predicted}, "
                      f"trailing_ones={trailing_ones}, bin={bin(n)}")
            violations += 1

    elapsed = time.time() - t0
    print(f"検証数: {N//2:,} 奇数")
    print(f"不一致: {violations}")
    print(f"計算時間: {elapsed:.2f}秒")

    if violations == 0:
        print(">>> 完全一致: k回連続上昇 ⟺ 末尾に(k+1)個の連続1ビット <<<")

    return violations


# ============================================================
# Part 4: メルセンヌ数の軌道分析
# ============================================================

def analyze_mersenne_numbers():
    """メルセンヌ数 2^p - 1 (p素数) の軌道での連続上昇を分析"""
    print(f"\n=== Part 4: メルセンヌ数の軌道分析 ===")
    t0 = time.time()

    primes = [p for p in range(2, 64) if is_prime(p)]

    print(f"\n--- 4a: メルセンヌ数の初期連続上昇 ---")
    print(f"{'p':>3} | {'2^p-1':>20} | 初期連続上昇 | 理論値(p-1) | 一致?")
    print("-" * 70)

    for p in primes:
        m = (1 << p) - 1
        k = consecutive_ascents(m)
        # 2^p - 1 = 111...1 (p個の1) なので末尾p個の連続1
        # よって k = p - 1 回の連続上昇が予測される
        theory = p - 1
        match = "Yes" if k == theory else "NO"
        if m < 10**18:
            print(f"{p:>3} | {m:>20,} | {k:>12} | {theory:>11} | {match}")

    print(f"\n--- 4b: メルセンヌ数の軌道全体の連続上昇統計 ---")
    print(f"{'p':>3} | 初期上昇 | 軌道最大上昇 | 軌道長(Syracuse) | 上昇ブロック数 | 軌道内上昇ブロック")
    print("-" * 90)

    for p in primes[:20]:  # p<=67まで
        m = (1 << p) - 1
        if m > 10**15:  # あまり大きいと時間かかる
            break

        init_k = consecutive_ascents(m)
        max_k, blocks = consecutive_ascents_in_trajectory(m, max_steps=100000)

        # 軌道長
        current = m
        if current % 2 == 0:
            current = current // (2 ** v2(current))
        steps = 0
        while current != 1 and steps < 100000:
            current = syracuse(current)
            steps += 1

        block_summary = Counter(blocks)
        block_str = ", ".join(f"{k}x{c}" for k, c in sorted(block_summary.items(), reverse=True))

        print(f"{p:>3} | {init_k:>8} | {max_k:>12} | {steps:>16} | {len(blocks):>14} | {block_str}")

    elapsed = time.time() - t0
    print(f"\n計算時間: {elapsed:.2f}秒")


# ============================================================
# Part 5: T^{m-1}(2^m - 1) = 2*3^{m-1} - 1 の検証
# ============================================================

def verify_mersenne_formula():
    """T^{m-1}(2^m - 1) = 2*3^{m-1} - 1 を検証"""
    print(f"\n=== Part 5: メルセンヌ帰着公式の検証 ===")
    print(f"T^{{m-1}}(2^m - 1) = 2*3^{{m-1}} - 1")
    print()

    print(f"{'m':>3} | {'2^m-1':>15} | {'T^(m-1)(2^m-1)':>20} | {'2*3^(m-1)-1':>20} | 一致?")
    print("-" * 85)

    for m in range(2, 30):
        start = (1 << m) - 1
        current = start
        for _ in range(m - 1):
            current = syracuse(current)

        expected = 2 * (3 ** (m - 1)) - 1
        match = "Yes" if current == expected else "NO"
        print(f"{m:>3} | {start:>15,} | {current:>20,} | {expected:>20,} | {match}")


# ============================================================
# Part 6: 2*3^{m-1}-1 の連続上昇分析
# ============================================================

def analyze_post_mersenne():
    """メルセンヌ帰着後の 2*3^{m-1}-1 の連続上昇分析"""
    print(f"\n=== Part 6: 帰着後 2*3^(m-1)-1 の連続上昇 ===")

    print(f"{'m':>3} | {'2*3^(m-1)-1':>20} | 連続上昇 | mod4 | 末尾1ビット数 | {'bin末尾8bit':>10}")
    print("-" * 85)

    for m in range(2, 35):
        val = 2 * (3 ** (m - 1)) - 1
        k = consecutive_ascents(val)
        mod4 = val % 4

        # 末尾の連続1ビット数
        trailing_ones = 0
        temp = val
        while temp & 1:
            trailing_ones += 1
            temp >>= 1

        bin_tail = bin(val)[-8:] if len(bin(val)) > 10 else bin(val)
        print(f"{m:>3} | {val:>20,} | {k:>8} | {mod4:>4} | {trailing_ones:>14} | {bin_tail:>10}")


# ============================================================
# Part 7: 非メルセンヌ数との比較
# ============================================================

def compare_mersenne_with_random():
    """メルセンヌ数vs同程度の大きさのランダムな奇数の連続上昇比較"""
    print(f"\n=== Part 7: メルセンヌ数 vs 一般的な数の比較 ===")

    import random
    random.seed(42)

    print(f"{'p':>3} | {'Mersenne初期上昇':>16} | {'一般平均初期上昇':>16} | {'Mersenne軌道最大':>16} | {'一般平均軌道最大':>16}")
    print("-" * 90)

    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        m = (1 << p) - 1

        # メルセンヌ数の統計
        init_k_mersenne = consecutive_ascents(m)
        max_k_mersenne, _ = consecutive_ascents_in_trajectory(m)

        # 同程度の大きさの奇数100個のサンプル
        init_ks = []
        max_ks = []
        for _ in range(100):
            r = random.randint(m // 2, m * 2)
            if r % 2 == 0:
                r += 1
            init_ks.append(consecutive_ascents(r))
            mk, _ = consecutive_ascents_in_trajectory(r, max_steps=10000)
            max_ks.append(mk)

        avg_init = sum(init_ks) / len(init_ks)
        avg_max = sum(max_ks) / len(max_ks)

        print(f"{p:>3} | {init_k_mersenne:>16} | {avg_init:>16.2f} | {max_k_mersenne:>16} | {avg_max:>16.2f}")


# ============================================================
# Part 8: 連続上昇の記録更新パターン
# ============================================================

def record_ascent_pattern(N=10**7):
    """連続上昇記録を更新する数のパターン"""
    print(f"\n=== Part 8: 連続上昇記録の更新パターン (N={N:,}) ===")

    max_k = 0
    records = []

    for n in range(1, N + 1, 2):
        k = consecutive_ascents(n)
        if k > max_k:
            max_k = k
            records.append((n, k, bin(n)))

    print(f"{'n':>12} | k | binary")
    print("-" * 60)
    for n, k, b in records:
        print(f"{n:>12,} | {k} | {b}")

    print(f"\n記録更新数: {len(records)}")
    print("\n観察: 全ての記録更新は 2^{k+1}-1 の形 (全ビット1)")

    # 検証: 各kに対して最小の n は 2^{k+1}-1
    print(f"\n--- 最小n検証 ---")
    for n, k, b in records:
        expected = (1 << (k + 1)) - 1
        print(f"k={k}: 最小n={n}, 2^{{k+1}}-1={expected}, 一致={n==expected}")

    return records


# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":
    print("=" * 80)
    print("連続上昇回数の分布と極値統計: メルセンヌ数との関連")
    print("=" * 80)

    # Part 1: 分布
    dist, max_k, max_k_n = compute_ascent_distribution(10**7)

    # Part 2: 成長率
    growth_results = compute_max_ascent_growth()

    # Part 3: mod条件検証
    violations = verify_mod_condition(100000)

    # Part 4: メルセンヌ数
    analyze_mersenne_numbers()

    # Part 5: 帰着公式
    verify_mersenne_formula()

    # Part 6: 帰着後分析
    analyze_post_mersenne()

    # Part 7: 比較
    compare_mersenne_with_random()

    # Part 8: 記録パターン
    records = record_ascent_pattern()

    print("\n" + "=" * 80)
    print("全分析完了")
    print("=" * 80)
