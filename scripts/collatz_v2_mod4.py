"""
探索: v₂(3n+1) の mod 4 依存性

n % 4 = 1 のとき v₂(3n+1) の分布
n % 4 = 3 のとき v₂(3n+1) = 1 (常に)
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def main():
    print("=== v₂(3n+1) の mod 4 依存性 ===\n")

    for mod4 in [1, 3]:
        vals = []
        for n in range(mod4, 10001, 4):
            if n % 2 == 1:  # 奇数のみ
                vals.append(v2(3 * n + 1))

        from collections import Counter
        dist = Counter(vals)
        total = len(vals)
        print(f"n ≡ {mod4} (mod 4):")
        for k in sorted(dist.keys()):
            print(f"  v₂(3n+1) = {k}: {dist[k]} ({100*dist[k]/total:.1f}%)")
        print()

    # mod 8 analysis
    print("=== v₂(3n+1) の mod 8 依存性 ===\n")
    for mod8 in [1, 3, 5, 7]:
        vals = []
        for n in range(mod8, 10001, 8):
            vals.append(v2(3 * n + 1))
        from collections import Counter
        dist = Counter(vals)
        total = len(vals)
        print(f"n ≡ {mod8} (mod 8): v₂ 分布 = {dict(sorted(dist.items()))}")

if __name__ == "__main__":
    main()
