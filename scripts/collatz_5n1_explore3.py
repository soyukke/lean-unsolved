"""
探索3: 1に到達する奇数の完全分類

前回の発見: p·2^k で1に到達するかは奇数部分 p のみで決まる
目標: 1に到達する奇数 p の集合を特定し、パターンを発見する
"""

def step(n):
    return n // 2 if n % 2 == 0 else 5 * n + 1

def reaches_1(n, max_steps=100000):
    visited = set()
    for _ in range(max_steps):
        if n == 1:
            return True
        if n in visited:
            return False  # cycle
        visited.add(n)
        n = step(n)
    return False  # probably diverges

def syracuse_5(n):
    """5n+1 Syracuse: 奇数 n → (5n+1)/2^v2(5n+1) の奇数部分"""
    m = 5 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def main():
    print("=== 探索3: 1に到達する奇数の完全分類 ===\n")

    # 1に到達する奇数を列挙
    good_odds = []
    for n in range(1, 100001, 2):
        if reaches_1(n):
            good_odds.append(n)

    print(f"奇数 1..99999 で1に到達: {len(good_odds)} 個")
    print(f"最初の50個: {good_odds[:50]}")

    # 連続する差
    diffs = [good_odds[i+1] - good_odds[i] for i in range(min(50, len(good_odds)-1))]
    print(f"連続差: {diffs}")

    # mod 5 分析
    print(f"\n--- mod 5 分析 ---")
    mod5 = [n % 5 for n in good_odds]
    from collections import Counter
    print(f"  mod 5 分布: {dict(sorted(Counter(mod5).items()))}")

    # mod 10 分析
    mod10 = [n % 10 for n in good_odds]
    print(f"  mod 10 分布: {dict(sorted(Counter(mod10).items()))}")

    # 5進表現
    print(f"\n--- 5進表現 ---")
    def to_base5(n):
        if n == 0: return "0"
        digits = []
        while n > 0:
            digits.append(str(n % 5))
            n //= 5
        return "".join(reversed(digits))

    for n in good_odds[:30]:
        print(f"  {n:6d} = {to_base5(n):>10s} (base 5)  mod5={n%5}  mod3={n%3}")

    # Syracuse 5n+1 写像の軌道
    print(f"\n--- Syracuse 5n+1 写像（奇数→奇数） ---")
    for n in [1, 3, 15, 19, 51, 65, 97]:
        traj = [n]
        current = n
        for _ in range(20):
            if current == 1 and len(traj) > 1:
                break
            current = syracuse_5(current)
            traj.append(current)
            if current == 1:
                break
        print(f"  {n}: {' → '.join(map(str, traj))}")

    # 1に到達しない奇数の最小例
    print(f"\n--- 1に到達しない奇数 ---")
    bad_odds = []
    for n in range(1, 1001, 2):
        if not reaches_1(n):
            bad_odds.append(n)
    print(f"  最初の30個: {bad_odds[:30]}")
    mod5_bad = [n % 5 for n in bad_odds[:100]]
    print(f"  mod 5 分布: {dict(sorted(Counter(mod5_bad).items()))}")

    # 仮説検証: 1に到達する奇数は「5の倍数でない」?
    print(f"\n--- 仮説検証 ---")
    good_div5 = [n for n in good_odds if n % 5 == 0]
    print(f"  5の倍数で1に到達: {good_div5[:20]}")
    bad_not_div5 = [n for n in bad_odds[:100] if n % 5 != 0]
    print(f"  5の倍数でないが到達しない: {bad_not_div5[:20]}")

    # 3の倍数分析
    print(f"\n--- 3の倍数分析 ---")
    good_div3 = [n for n in good_odds if n % 3 == 0]
    print(f"  3の倍数で1に到達: {len(good_div3)} 個")
    print(f"  最初の20個: {good_div3[:20]}")

    # 再帰的構造: 1に到達する奇数 p に対し、(2p-1)/5 も到達するか?
    print(f"\n--- 逆写像の分析 ---")
    # Syracuse逆写像: 奇数 m が 5n+1 の奇数部分なら n = (m·2^k - 1)/5 for some k
    # つまり m·2^k ≡ 1 (mod 5)
    for m in [1, 3, 15, 19, 51]:
        print(f"  m={m}: ", end="")
        preimages = []
        for k in range(1, 20):
            val = m * (2**k) - 1
            if val % 5 == 0:
                n = val // 5
                if n > 0 and n % 2 == 1:
                    preimages.append((n, k))
        print(f"逆像(奇数): {preimages[:5]}")

if __name__ == "__main__":
    main()
