"""
新探索: コラッツ stopping time s(n) の隠れた構造

s(n) = nが1に到達するまでのステップ数
既知: s(2^k) = k, s(1) = 0

疑問:
1. s(n) mod m にパターンはあるか？
2. s(n) = s(n+1) となる n の分布は？
3. s(n) の「レコード」（局所最大値）の構造は？
4. 特定の残差類で s(n) の公式はあるか？
"""

def collatz_stopping_time(n):
    """nが1に到達するまでのステップ数"""
    if n <= 0: return -1
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def main():
    print("=== コラッツ stopping time の隠れた構造 ===\n")

    # 基本データ
    N = 10000
    st = [collatz_stopping_time(n) for n in range(1, N+1)]

    # 1. s(n) mod 3 の分布
    print("--- s(n) mod 3 の分布 ---")
    from collections import Counter
    for m in [2, 3, 4, 5, 6]:
        dist = Counter(s % m for s in st)
        print(f"  mod {m}: {dict(sorted(dist.items()))}")

    # 2. s(n) = s(n+1) のパターン
    print("\n--- s(n) = s(n+1) となる n ---")
    equal_pairs = [(n, st[n-1]) for n in range(1, N) if st[n-1] == st[n]]
    print(f"  n=1..{N-1} で {len(equal_pairs)} 組")
    print(f"  最初の20個: {[(n, s) for n, s in equal_pairs[:20]]}")

    # mod パターン
    eq_mod2 = Counter(n % 2 for n, _ in equal_pairs)
    eq_mod4 = Counter(n % 4 for n, _ in equal_pairs)
    print(f"  n mod 2: {dict(sorted(eq_mod2.items()))}")
    print(f"  n mod 4: {dict(sorted(eq_mod4.items()))}")

    # 3. s(n) のレコード（s(n) > s(m) for all m < n）
    print("\n--- s(n) のレコード（局所最大値） ---")
    records = []
    max_so_far = -1
    for n in range(1, N+1):
        if st[n-1] > max_so_far:
            max_so_far = st[n-1]
            records.append((n, max_so_far))
    print(f"  最初の20レコード: {records[:20]}")

    # レコード値の比 s(n)/log(n)
    import math
    print(f"\n  レコード値の成長率:")
    for n, s in records[:20]:
        if n > 1:
            print(f"    n={n:6d}: s={s:4d}, s/log₂(n)={s/math.log2(n):.2f}")

    # 4. 残差類ごとの平均 s(n)
    print(f"\n--- 残差類ごとの平均 s(n) ---")
    for m in [2, 4, 8, 16]:
        avgs = {}
        for r in range(m):
            vals = [st[n-1] for n in range(max(1,r), N+1, m)]
            if vals:
                avgs[r] = sum(vals) / len(vals)
        print(f"  mod {m}: " + ", ".join(f"{r}:{avgs[r]:.1f}" for r in sorted(avgs)))

    # 5. ★ 新発見を探す: s(n) と n の2進表現の関係
    print(f"\n--- s(n) と n の2進表現 ---")
    print(f"  n, s(n), bin(n), popcount(n), len(bin(n))")
    for n in [1, 2, 3, 7, 15, 27, 31, 63, 127, 255, 511, 1023]:
        s = collatz_stopping_time(n)
        pc = bin(n).count('1')
        bl = n.bit_length()
        print(f"  {n:6d}: s={s:4d}, bin={bin(n):>12s}, popcount={pc}, bitlen={bl}")

    # 6. 2^k - 1 (メルセンヌ数) の stopping time
    print(f"\n--- 2^k - 1 の stopping time ---")
    for k in range(1, 21):
        n = 2**k - 1
        s = collatz_stopping_time(n)
        print(f"  2^{k:2d}-1 = {n:8d}: s = {s:4d}, s/k = {s/k:.2f}")

    # 7. 3^k の stopping time
    print(f"\n--- 3^k の stopping time ---")
    for k in range(1, 13):
        n = 3**k
        s = collatz_stopping_time(n)
        print(f"  3^{k:2d} = {n:8d}: s = {s:4d}, s/k = {s/k:.2f}")

    # 8. ★ s(2^k - 1) の公式を探す
    print(f"\n--- ★ s(2^k-1) / k の収束 ---")
    ratios = []
    for k in range(1, 25):
        n = 2**k - 1
        s = collatz_stopping_time(n)
        ratio = s / k
        ratios.append(ratio)
        if k >= 10:
            print(f"  k={k:2d}: s(2^k-1)/k = {ratio:.4f}")

    # 平均の収束
    if len(ratios) > 10:
        avg_last10 = sum(ratios[-10:]) / 10
        print(f"\n  最後10個の平均: {avg_last10:.4f}")
        print(f"  理論値 (もしあれば): ???")

if __name__ == "__main__":
    main()
