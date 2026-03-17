#!/usr/bin/env python3
"""
双子素数予想 探索1-2: 数値実験
- 双子素数の分布（100万まで）
- 密度 π₂(x)/x の変化
- Brunの定数 B₂ の近似値
- 素数ギャップの分布
- mod 6, mod 30 での分布パターン
"""

import math
from collections import Counter

def sieve_of_eratosthenes(limit):
    """エラトステネスの篩"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return is_prime

def main():
    LIMIT = 1_000_000
    print(f"=== 双子素数の探索 (上限: {LIMIT:,}) ===\n")

    # 篩の実行
    is_prime = sieve_of_eratosthenes(LIMIT)
    primes = [i for i in range(2, LIMIT + 1) if is_prime[i]]
    print(f"素数の個数 π({LIMIT:,}) = {len(primes):,}")

    # 双子素数の収集
    twin_primes = []
    for i in range(len(primes) - 1):
        if primes[i + 1] - primes[i] == 2:
            twin_primes.append((primes[i], primes[i + 1]))

    print(f"双子素数の組数 π₂({LIMIT:,}) = {len(twin_primes):,}")
    print(f"\n最初の20組: {twin_primes[:20]}")
    print(f"最後の5組: {twin_primes[-5:]}")

    # === 密度の変化 ===
    print("\n=== 密度 π₂(x)/x の変化 ===")
    print(f"{'x':>12} {'π₂(x)':>8} {'π₂(x)/x':>12} {'π₂(x)/(x/ln²x)':>16}")
    checkpoints = [100, 1000, 10000, 50000, 100000, 500000, 1000000]
    idx = 0
    for cp in checkpoints:
        while idx < len(twin_primes) and twin_primes[idx][0] <= cp:
            idx += 1
        count = idx
        density = count / cp
        # Hardy-Littlewood 予想: π₂(x) ~ 2 C₂ x / ln²(x)
        # C₂ ≈ 0.6601618...
        hl_ratio = count / (cp / (math.log(cp) ** 2)) if cp > 1 else 0
        print(f"{cp:>12,} {count:>8,} {density:>12.8f} {hl_ratio:>16.6f}")

    # Hardy-Littlewood 定数 C₂ の推定
    # π₂(x) ~ 2 C₂ ∫₂ˣ dt/ln²(t)  → π₂(x) / (x/ln²(x)) → 2 C₂
    x = LIMIT
    estimated_2C2 = len(twin_primes) / (x / (math.log(x) ** 2))
    print(f"\n推定 2C₂ = {estimated_2C2:.6f} (理論値 ≈ 1.3203)")

    # === Brunの定数 B₂ ===
    print("\n=== Brunの定数 B₂ の近似 ===")
    print("B₂ = Σ (1/p + 1/(p+2)) for twin primes (p, p+2)")
    brun_sum = 0.0
    brun_checkpoints = [100, 1000, 10000, 100000, len(twin_primes)]
    for i, (p, q) in enumerate(twin_primes):
        brun_sum += 1.0 / p + 1.0 / q
        if i + 1 in brun_checkpoints:
            print(f"  最初の {i+1:>6,} 組まで: B₂ ≈ {brun_sum:.10f}")
    print(f"  (理論値 B₂ ≈ 1.9021605831...)")

    # === 素数ギャップの分布 ===
    print("\n=== 素数ギャップの分布 ===")
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    gap_counter = Counter(gaps)
    print(f"{'ギャップ':>8} {'出現回数':>10} {'割合(%)':>10}")
    for gap in sorted(gap_counter.keys())[:20]:
        count = gap_counter[gap]
        pct = 100.0 * count / len(gaps)
        print(f"{gap:>8} {count:>10,} {pct:>10.4f}")

    # === mod 6 パターン ===
    print("\n=== 双子素数の小さい方の mod 6 分布 ===")
    mod6_counter = Counter()
    for p, q in twin_primes:
        mod6_counter[p % 6] += 1
    for r in sorted(mod6_counter.keys()):
        count = mod6_counter[r]
        pct = 100.0 * count / len(twin_primes) if twin_primes else 0
        print(f"  p ≡ {r} (mod 6): {count:>6,} 組 ({pct:.2f}%)")

    # 注: p=3 の場合のみ p ≡ 3 (mod 6) で、それ以外は全て p ≡ 5 (mod 6)
    # なぜなら p > 3 で p が素数なら p ≡ 1 or 5 (mod 6)
    # p ≡ 1 (mod 6) なら p+2 ≡ 3 (mod 6) で3の倍数なので素数でない
    # よって p > 3 の双子素数では必ず p ≡ 5 (mod 6)

    # === mod 30 パターン ===
    print("\n=== 双子素数の小さい方の mod 30 分布 (p > 5) ===")
    mod30_counter = Counter()
    for p, q in twin_primes:
        if p > 5:
            mod30_counter[p % 30] += 1
    for r in sorted(mod30_counter.keys()):
        count = mod30_counter[r]
        pct = 100.0 * count / sum(mod30_counter.values()) if mod30_counter else 0
        print(f"  p ≡ {r:>2} (mod 30): {count:>6,} 組 ({pct:.2f}%)")

    # === 連続する双子素数間の距離 ===
    print("\n=== 連続する双子素数間の距離（小さい方の差）===")
    if len(twin_primes) > 1:
        diffs = [twin_primes[i + 1][0] - twin_primes[i][0] for i in range(len(twin_primes) - 1)]
        diff_counter = Counter(diffs)
        print(f"{'距離':>8} {'出現回数':>10} {'割合(%)':>10}")
        for d in sorted(diff_counter.keys())[:15]:
            count = diff_counter[d]
            pct = 100.0 * count / len(diffs)
            print(f"{d:>8} {count:>10,} {pct:>10.4f}")

    # === まとめ ===
    print("\n=== まとめ ===")
    print(f"1. 双子素数は {LIMIT:,} まで {len(twin_primes):,} 組存在")
    print(f"2. 密度は緩やかに減少（Hardy-Littlewood 予想と整合）")
    print(f"3. Brunの定数 B₂ ≈ {brun_sum:.8f} (理論値 ≈ 1.9022)")
    print(f"4. p > 3 の双子素数は全て p ≡ 5 (mod 6) — Leanで証明可能")
    print(f"5. mod 30 では 11, 17, 29 の3つの剰余類に集中")

if __name__ == "__main__":
    main()
