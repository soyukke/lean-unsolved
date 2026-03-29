#!/usr/bin/env python3
"""
連続上昇の深い分析:
1. max_k = floor(log2(N)) の厳密性を確認
2. メルセンヌ軌道の段階的下降パターンの数学的構造
3. 2*3^{m-1}-1 が常に ≡1 (mod 4) である理由
4. メルセンヌ数軌道の "waterfall" 構造の定量化
"""

import math
from collections import Counter

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def consecutive_ascents(n):
    if n % 2 == 0:
        return 0
    count = 0
    current = n
    while True:
        val = 3 * current + 1
        if v2(val) != 1:
            break
        count += 1
        current = val // 2
    return count

# ============================================================
# Analysis 1: max_k = floor(log2(N)) の正確性
# ============================================================

def analyze_max_k_exact():
    """
    max_k(N) = k回連続上昇する最小の奇数が N 以下 ⟺ 2^{k+1}-1 <= N
    つまり max_k(N) = floor(log2(N+1)) - 1

    正確な公式を導出・検証
    """
    print("=== Analysis 1: max_k(N) の正確な公式 ===")
    print()
    print("k回連続上昇する最小の奇数 = 2^{k+1} - 1")
    print("max_k(N) = max{k : 2^{k+1}-1 <= N} = floor(log2(N+1)) - 1")
    print()

    print(f"{'N':>15} | {'実測max_k':>9} | {'公式':>5} | 一致?")
    print("-" * 50)

    max_k = 0
    for N in [10, 100, 1000, 10000, 100000, 1000000, 10000000]:
        # 実測: 最大のk
        for n in range(1, N + 1, 2):
            k = consecutive_ascents(n)
            if k > max_k:
                max_k = k

        formula = math.floor(math.log2(N + 1)) - 1
        match = "Yes" if max_k == formula else "NO"
        print(f"{N:>15,} | {max_k:>9} | {formula:>5} | {match}")

    print()
    print("結論: max_k(N) = floor(log2(N+1)) - 1 が厳密に成立")
    print("これは max_k(N) ~ log2(N) を意味し、成長率は log(N)/ln(2) ~ 1.4427*ln(N)")


# ============================================================
# Analysis 2: メルセンヌ軌道の "Waterfall" 構造
# ============================================================

def analyze_waterfall():
    """
    2^p - 1 の軌道で、初期 p-1 ステップは全て上昇(v2=1)。
    T^{k}(2^p-1) のステップごとの値を追跡。

    T^k(2^p-1) = ? の閉じた公式:
    初期のm-1ステップでは各ステップで T(n) = (3n+1)/2
    T^1(2^m-1) = (3(2^m-1)+1)/2 = (3*2^m - 2)/2 = 3*2^{m-1} - 1
    T^2(3*2^{m-1}-1) = (3(3*2^{m-1}-1)+1)/2 = (9*2^{m-1}-2)/2 = 9*2^{m-2}-1 = 3^2*2^{m-2}-1
    一般: T^k(2^m-1) = 3^k * 2^{m-k} - 1 (k=0,...,m-1)
    """
    print("\n=== Analysis 2: メルセンヌ軌道の Waterfall 構造 ===")
    print()
    print("仮説: T^k(2^m - 1) = 3^k * 2^{m-k} - 1 (k = 0, ..., m-1)")
    print()

    # 検証
    print(f"{'m':>3} | {'k':>3} | {'T^k(2^m-1)':>20} | {'3^k*2^{m-k}-1':>20} | 一致?")
    print("-" * 75)

    for m in [5, 7, 11, 13]:
        start = (1 << m) - 1
        current = start
        all_match = True
        for k in range(m):
            expected = (3**k) * (2**(m - k)) - 1
            match = current == expected
            if not match:
                all_match = False
            if k <= 3 or k == m - 1:
                print(f"{m:>3} | {k:>3} | {current:>20,} | {expected:>20,} | {'Yes' if match else 'NO'}")
            elif k == 4:
                print(f"{'':>3} | {'...':>3} | {'...':>20} | {'...':>20} |")
            current = syracuse(current)

        if all_match:
            print(f"  -> m={m}: 全ステップ一致!")
        print()

    # 数学的証明
    print("--- 数学的証明 ---")
    print("帰納法: T^k(2^m-1) = 3^k * 2^{m-k} - 1 (k=0,...,m-1)")
    print("基底: k=0: T^0(2^m-1) = 2^m - 1 = 3^0 * 2^m - 1. OK")
    print("帰納: T^k = 3^k * 2^{m-k} - 1 と仮定 (k < m-1)")
    print("  この値は奇数? 3^k * 2^{m-k} は偶数(m-k >= 1), 偶数-1は奇数. OK")
    print("  v2(3 * (3^k * 2^{m-k} - 1) + 1) = v2(3^{k+1} * 2^{m-k} - 2)")
    print("    = v2(2 * (3^{k+1} * 2^{m-k-1} - 1))")
    print("    = 1 + v2(3^{k+1} * 2^{m-k-1} - 1)")
    print("  m-k-1 >= 1 のとき(k <= m-2): 3^{k+1} * 2^{m-k-1} は偶数, -1で奇数")
    print("    よって v2(3^{k+1} * 2^{m-k-1} - 1) = 0")
    print("    全体で v2 = 1")
    print("  T^{k+1} = (3 * (3^k * 2^{m-k} - 1) + 1) / 2")
    print("          = (3^{k+1} * 2^{m-k} - 2) / 2")
    print("          = 3^{k+1} * 2^{m-k-1} - 1")
    print("  QED")
    print()
    print("特に k=m-1 のとき: T^{m-1}(2^m-1) = 3^{m-1} * 2^1 - 1 = 2*3^{m-1} - 1")
    print("これが既知の帰着公式 T^{m-1}(2^m-1) = 2*3^{m-1} - 1 の導出!")


# ============================================================
# Analysis 3: 2*3^{m-1}-1 ≡ 1 (mod 4) の証明
# ============================================================

def analyze_post_mersenne_mod():
    """2*3^{m-1} - 1 mod 4 の分析"""
    print("\n=== Analysis 3: 2*3^{m-1}-1 mod 4 の分析 ===")
    print()
    print("3^k mod 4: 3^1=3, 3^2=1, 3^3=3, 3^4=1, ... 周期2")
    print("  3^k ≡ 3 (mod 4) if k odd, 3^k ≡ 1 (mod 4) if k even")
    print()
    print("2*3^{m-1} mod 4:")
    print("  m-1 odd (m even): 2*3 = 6 ≡ 2 (mod 4) → 2*3^{m-1}-1 ≡ 1 (mod 4)")
    print("  m-1 even (m odd): 2*1 = 2 ≡ 2 (mod 4) → 2*3^{m-1}-1 ≡ 1 (mod 4)")
    print()
    print("いずれの場合も 2*3^{m-1} ≡ 2 (mod 4)")
    print("よって 2*3^{m-1} - 1 ≡ 1 (mod 4)")
    print("つまり帰着後の値は常に ≡ 1 (mod 4) → 連続上昇 0回")
    print("→ 次のステップでは v2(3n+1) >= 2 → 下降が保証される")
    print()

    # v2(3(2*3^{m-1}-1)+1) の分析
    print("--- 帰着後の v2 分析 ---")
    print(f"{'m':>3} | {'2*3^(m-1)-1':>20} | v2(3n+1) | T(n)")
    print("-" * 60)
    for m in range(2, 25):
        val = 2 * (3 ** (m - 1)) - 1
        next_val = 3 * val + 1
        v = v2(next_val)
        t = next_val // (2 ** v)
        print(f"{m:>3} | {val:>20,} | {v:>8} | {t:,}")

    # v2 の分布分析
    print("\n--- v2(6*3^{m-1} - 2) の分析 ---")
    print("3n+1 = 3(2*3^{m-1}-1)+1 = 6*3^{m-1} - 2 = 2*(3^m - 1)")
    print("v2(2*(3^m-1)) = 1 + v2(3^m - 1)")
    print()
    print(f"{'m':>3} | {'3^m mod 2^k':>15} | v2(3^m - 1) | v2(3n+1)")
    print("-" * 55)
    for m in range(1, 30):
        val = 3**m - 1
        v = v2(val)
        print(f"{m:>3} | {'':>15} | {v:>11} | {v+1:>8}")


# ============================================================
# Analysis 4: v2(3^m - 1) の系統的分析
# ============================================================

def analyze_v2_power3():
    """v2(3^m - 1) のパターン"""
    print("\n=== Analysis 4: v2(3^m - 1) のパターン ===")
    print()
    print("Lifting the Exponent Lemma (LTE):")
    print("v2(3^m - 1) = v2(3 - 1) + v2(3 + 1) + v2(m) - 1")
    print("            = 1 + 2 + v2(m) - 1 = 2 + v2(m)   (m even)")
    print("v2(3^m - 1) = v2(3 - 1) = 1                    (m odd)")
    print()

    print(f"{'m':>4} | v2(3^m-1) | LTE予測 | 一致? | 全体v2(帰着後)")
    print("-" * 60)
    for m in range(1, 40):
        actual = v2(3**m - 1)
        if m % 2 == 0:
            lte = 2 + v2(m)
        else:
            lte = 1
        match = "Yes" if actual == lte else "NO"
        full_v2 = actual + 1  # v2(2*(3^m-1)) = 1 + v2(3^m-1)
        print(f"{m:>4} | {actual:>9} | {lte:>7} | {match:>5} | {full_v2:>14}")

    print()
    print("結論:")
    print("  m奇数: v2(帰着後) = 2 → T = (3n+1)/4 (穏やかな下降)")
    print("  m偶数: v2(帰着後) = 3 + v2(m) → v2(m)が大きいほど急降下")
    print("  m = 2^k * (odd): v2(帰着後) = 3 + k")


# ============================================================
# Analysis 5: メルセンヌ数の軌道長と比率分析
# ============================================================

def analyze_mersenne_trajectory_length():
    """メルセンヌ数の総軌道長 vs 初期上昇"""
    print("\n=== Analysis 5: メルセンヌ軌道 - 初期上昇後の比率 ===")
    print()

    print(f"{'p':>3} | 初期上昇 | 総軌道長 | 上昇/軌道 | 3^p/2^p (成長因子)")
    print("-" * 70)

    for p in range(2, 50):
        if not all(p % i != 0 for i in range(2, int(p**0.5) + 1)) and p > 1:
            continue  # 素数のみ

        m = (1 << p) - 1
        if m > 10**15:
            break

        init_k = p - 1

        # 軌道長
        current = m
        steps = 0
        while current != 1 and steps < 200000:
            current = syracuse(current)
            steps += 1

        ratio = init_k / steps if steps > 0 else 0
        growth = (3**p) / (2**p)

        print(f"{p:>3} | {init_k:>8} | {steps:>8} | {ratio:>9.4f} | {growth:>18.4f}")


# ============================================================
# Analysis 6: 全ビット1でない数の大連続上昇
# ============================================================

def analyze_non_allones_ascent(N=10**7):
    """2^k-1 以外で大きな連続上昇を持つ数"""
    print(f"\n=== Analysis 6: 2^k-1 以外の大連続上昇 (N={N:,}) ===")
    print()
    print("k回連続上昇する数は n ≡ 2^{k+1}-1 (mod 2^{k+1})")
    print("最小は 2^{k+1}-1 だが、それ以外にも多数存在")
    print()

    # k=10以上で 2^{k+1}-1 でない最初の数
    print(f"{'k':>3} | 最小n = 2^(k+1)-1 | 2番目に小さいn | 差")
    print("-" * 60)

    for k in range(1, 23):
        min_n = (1 << (k + 1)) - 1
        # 2番目: min_n + 2^{k+1}
        second_n = min_n + (1 << (k + 1))
        if second_n <= N or k <= 22:
            diff = second_n - min_n
            print(f"{k:>3} | {min_n:>18,} | {second_n:>15,} | {diff:>10,}")

    print()
    print("n ≡ 2^{k+1}-1 (mod 2^{k+1}) を満たす数の密度: 1/2^{k+1}")
    print(f"N={N:,}内でk=20の数の個数: {N // (1 << 21)}")


if __name__ == "__main__":
    print("=" * 80)
    print("連続上昇の深い分析")
    print("=" * 80)

    analyze_max_k_exact()
    analyze_waterfall()
    analyze_post_mersenne_mod()
    analyze_v2_power3()
    analyze_mersenne_trajectory_length()
    analyze_non_allones_ascent()

    print("\n" + "=" * 80)
    print("深い分析完了")
    print("=" * 80)
