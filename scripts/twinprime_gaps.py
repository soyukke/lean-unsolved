"""
双子素数・いとこ素数・セクシー素数のギャップ解析
"""
from collections import Counter


def is_prime(n):
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


def primes_up_to(limit):
    """エラトステネスの篩"""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]


def analyze_prime_gaps(limit=100000):
    primes = primes_up_to(limit)
    gaps = {2: [], 4: [], 6: []}  # twin, cousin, sexy

    for i in range(len(primes) - 1):
        g = primes[i + 1] - primes[i]
        if g in gaps:
            gaps[g].append(primes[i])

    print(f"=== 素数ギャップ解析 (p < {limit}) ===")
    for g, name in [(2, "双子素数"), (4, "いとこ素数"), (6, "セクシー素数")]:
        pairs = gaps[g]
        print(f"\n{name} (ギャップ={g}):")
        print(f"  個数: {len(pairs)}")
        if pairs:
            print(f"  最大: ({pairs[-1]}, {pairs[-1]+g})")
            # mod 30 分布
            mod30 = Counter(p % 30 for p in pairs if p > g)
            print(f"  mod 30 分布: {dict(sorted(mod30.items()))}")


if __name__ == "__main__":
    analyze_prime_gaps()
