"""
Syracuse写像 T mod 2^k の置換群構造 - 第3弾

発見された核心的パターンの深掘り:
1. 逆像サイズ分布に明確な規則性がある (1, 2, 3, ... の個数が完全平方列?)
2. k=10,11,12 で出現する非自明サイクルの構造
3. v2層間衝突の数値的パターン
4. 像の収縮率 (T^m の像サイズ) の理論的予測

新しいアプローチ:
A. 逆像サイズ分布の閉公式の導出
B. k=10-20 での非自明不変サイクルの網羅的探索
C. v2層を跨ぐ写像の半群構造
"""

from math import gcd, log2, log
from collections import Counter
import json
import time

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

def factorize(n):
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def format_fac(n):
    facs = factorize(n)
    if not facs:
        return str(n)
    return " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facs.items()))

# ==========================================================
print("=" * 70)
print("A. 逆像サイズ分布の閉公式")
print("=" * 70)

print("\n逆像サイズ = m の残基の個数 N(m, k):")
print()

# preimage sizes from earlier:
# k=3: {1: 2, 2: 1}
# k=4: {1: 1, 2: 2, 3: 1}
# k=5: {1: 9, 2: 2, 3: 1}  -- 0: 4個 (missing)
# k=6: {1: 8, 2: 7, 3: 2, 4: 1}
# k=7: {1: 36, 2: 9, 3: 2, 4: 1}
# k=8: {1: 36, 2: 26, 3: 9, 4: 2, 5: 1}
# k=9: {1: 144, 2: 36, 3: 9, 4: 2, 5: 1}
# k=10: {1: 148, 2: 102, 3: 36, 4: 9, 5: 2, 6: 1}
# k=11: {1: 576, 2: 144, 3: 36, 4: 9, 5: 2, 6: 1}
# k=12: {1: 596, 2: 406, 3: 144, 4: 36, 5: 9, 6: 2, 7: 1}
# k=13: {1: 2304, 2: 576, 3: 144, 4: 36, 5: 9, 6: 2, 7: 1}

# パターンの仮説:
# k奇: N(1, k) = (3/4) * 2^{k-1}?  k=7: (3/4)*64=48... 実際は36. 違う。
# k奇のN(m, k) for m>=2: 見ると k=7で {2:9, 3:2, 4:1}、k=9で {2:36, 3:9, 4:2, 5:1}
# k=7: 9 = 3^2, 2, 1  → 3^2, 2, 1
# k=9: 36 = 6^2? No. 36=4*9. 9 = 3^2, 2, 1
# k=11: 144=12^2? 144, 36, 9, 2, 1
# k=13: 576, 144, 36, 9, 2, 1

# k奇(>=7): N(2)=36 for k=7, N(2)=36 for k=9???  No, k=9: N(2)=36, k=11:N(2)=144
# Let me recompute more carefully

for k in range(3, 18):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}

    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())

    # n=0 (not in image) count
    n_missing = len(set(odds) - set(mapping.values()))
    size_dist[0] = n_missing

    print(f"  k={k} (k{'odd' if k%2==1 else 'even'}):", end="")
    for m in sorted(size_dist.keys()):
        if size_dist[m] > 0:
            print(f"  N({m})={size_dist[m]}", end="")
    print()

# ==========================================================
print("\n" + "=" * 70)
print("A2. 逆像サイズ N(m,k) を k偶・k奇で分離して分析")
print("=" * 70)

print("\n--- k奇 ---")
for k in range(3, 18, 2):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}

    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())
    n_missing = len(set(odds) - set(mapping.values()))
    size_dist[0] = n_missing

    # m >= 2 の部分を抽出
    higher = {m: size_dist[m] for m in sorted(size_dist.keys()) if m >= 2}
    print(f"  k={k}: N(0)={size_dist[0]}, N(1)={size_dist.get(1,0)}, higher={higher}")

    # higher の値列: 見ると k=7: {2:9, 3:2, 4:1}, k=9: {2:36, 3:9, 4:2, 5:1}
    # k=11: {2:144, 3:36, 4:9, 5:2, 6:1}
    # k=13: {2:576, 3:144, 4:36, 5:9, 6:2, 7:1}
    # パターン: N(m) = N(m+1,k-2) for m >= 2, and N(2,k) = 4 * N(2,k-2)
    # k=7: N(2)=9, k=9: N(2)=36 = 4*9, k=11: N(2)=144=4*36, k=13: N(2)=576=4*144
    # So N(2, k_odd) = 9 * 4^{(k-7)/2} for k >= 7

print("\n--- k偶 ---")
for k in range(4, 18, 2):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}

    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())
    n_missing = len(set(odds) - set(mapping.values()))
    size_dist[0] = n_missing

    higher = {m: size_dist[m] for m in sorted(size_dist.keys()) if m >= 2}
    print(f"  k={k}: N(0)={size_dist[0]}, N(1)={size_dist.get(1,0)}, higher={higher}")
    # k=6: {2:7, 3:2, 4:1}, k=8: {2:26, 3:9, 4:2, 5:1}
    # k=10: {2:102, 3:36, 4:9, 5:2, 6:1}
    # k=12: {2:406, 3:144, 4:36, 5:9, 6:2, 7:1}
    # k=14: ...
    # N(3,k_even) = 9 * 4^{(k-8)/2} for k >= 8
    # N(2,k_even) = ?  k=6: 7, k=8: 26, k=10: 102, k=12: 406
    # 7, 26, 102, 406: ratio: 26/7=3.71, 102/26=3.92, 406/102=3.98 → approaching 4
    # 26 = 4*7 - 2, 102 = 4*26 - 2, 406 = 4*102 - 2
    # a_n = 4*a_{n-1} - 2, a_0 = 7
    # a_n = (7 - 2/3) * 4^n + 2/3 = (19/3) * 4^n + 2/3

# ==========================================================
print("\n" + "=" * 70)
print("A3. N(m,k) の閉公式検証")
print("=" * 70)

print("\nN(m,k_odd) for m>=2, k>=7:")
print("  仮説: N(m, k_odd) = N(m-1, k_odd - 2)")
print("  すなわち、高次の逆像は2段階前のkの値をシフトして再現")
print()

for k in range(7, 18, 2):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())

    # k-2 の値
    if k >= 9:
        mod2 = 2**(k-2)
        odds2 = list(range(1, mod2, 2))
        mapping2 = {n: syracuse(n) % mod2 for n in odds2}
        preimage_count2 = Counter(mapping2.values())
        size_dist2 = Counter(preimage_count2.values())

        print(f"  k={k}:")
        for m in sorted(set(list(size_dist.keys()) + list(size_dist2.keys()))):
            if m >= 2:
                val_k = size_dist.get(m, 0)
                val_km2 = size_dist2.get(m-1, 0)
                match = "OK" if val_k == val_km2 else f"MISMATCH ({val_km2})"
                print(f"    N({m},{k}) = {val_k}, N({m-1},{k-2}) = {val_km2}: {match}")

print("\nN(m,k_even) for m>=3, k>=8:")
for k in range(8, 18, 2):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())

    if k >= 10:
        mod2 = 2**(k-2)
        odds2 = list(range(1, mod2, 2))
        mapping2 = {n: syracuse(n) % mod2 for n in odds2}
        preimage_count2 = Counter(mapping2.values())
        size_dist2 = Counter(preimage_count2.values())

        print(f"  k={k}:")
        for m in sorted(set(list(size_dist.keys()) + list(size_dist2.keys()))):
            if m >= 3:
                val_k = size_dist.get(m, 0)
                val_km2 = size_dist2.get(m-1, 0)
                match = "OK" if val_k == val_km2 else f"MISMATCH ({val_km2})"
                print(f"    N({m},{k}) = {val_k}, N({m-1},{k-2}) = {val_km2}: {match}")

# ==========================================================
print("\n" + "=" * 70)
print("B. k=10..20 での非自明不変サイクル探索")
print("=" * 70)

def find_cycles_in_map(mapping, odds):
    """写像の中で周期軌道を全て見つける（全単射でなくても動作）"""
    cycles_found = []
    visited_global = set()

    for start in odds:
        if start in visited_global:
            continue

        # Floyd's cycle detection
        path = [start]
        visited = {start}
        current = start

        for _ in range(len(odds) + 10):
            nxt = mapping.get(current)
            if nxt is None or nxt not in mapping:
                break
            if nxt in visited:
                # サイクルの開始点を見つけた
                cycle_start = nxt
                cycle = []
                pos = nxt
                while True:
                    cycle.append(pos)
                    pos = mapping[pos]
                    if pos == cycle_start:
                        break
                if len(cycle) > 0:
                    # 正規化（最小元から開始）
                    min_idx = cycle.index(min(cycle))
                    cycle = cycle[min_idx:] + cycle[:min_idx]
                    cycle_key = tuple(cycle)
                    if cycle_key not in [tuple(c) for c in cycles_found]:
                        cycles_found.append(list(cycle))
                for elem in cycle:
                    visited_global.add(elem)
                break
            visited.add(nxt)
            path.append(nxt)
            current = nxt

        visited_global.update(path)

    return cycles_found

for k in range(3, 21):
    t0 = time.time()
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}

    cycles = find_cycles_in_map(mapping, odds)

    # 長さ > 1 のサイクルのみ
    nontrivial = [c for c in cycles if len(c) > 1]
    fixed = [c for c in cycles if len(c) == 1]

    elapsed = time.time() - t0

    if nontrivial:
        print(f"  k={k}: 不動点={len(fixed)}, 非自明サイクル={len(nontrivial)} ({elapsed:.2f}s)")
        for c in nontrivial:
            if len(c) <= 30:
                print(f"    長さ {len(c)}: {c}")
            else:
                print(f"    長さ {len(c)}: [{c[0]}, {c[1]}, ..., {c[-1]}]")
            # サイクルの位数パターン
            total_v2 = sum(v2(3*n+1) for n in c)
            total_bits = total_v2
            print(f"      合計v2={total_v2}, 合計3n+1=log(prod(3c_i+1))=...skip, "
                  f"平均v2={total_v2/len(c):.4f}")
    else:
        if k <= 12:
            print(f"  k={k}: 不動点={len(fixed)}, 非自明サイクル=0 ({elapsed:.2f}s)")

# ==========================================================
print("\n" + "=" * 70)
print("C. 像収縮率の理論予測 vs 実測")
print("   |Image(T^m mod 2^k)| / 2^{k-1} ~ (3/4)^m のはず")
print("=" * 70)

for k in [9, 11, 13]:
    mod = 2**k
    odds = list(range(1, mod, 2))
    n_odds = len(odds)

    current_map = {n: syracuse(n) % mod for n in odds}

    print(f"\n  k={k}:")
    print(f"  {'m':>4} {'|Image|':>10} {'ratio':>10} {'(3/4)^m':>10} {'ratio/(3/4)^m':>14}")

    for m in range(1, 30):
        image = set(current_map.values()) & set(odds)
        ratio = len(image) / n_odds
        predicted = (3/4)**m
        rel = ratio / predicted if predicted > 0 else 0

        print(f"  {m:>4} {len(image):>10} {ratio:>10.6f} {predicted:>10.6f} {rel:>14.6f}")

        # 次ステップ
        next_map = {}
        for n in odds:
            val = current_map[n]
            next_map[n] = syracuse(val) % mod
        current_map = next_map

        if len(image) <= 1:
            break

# ==========================================================
print("\n" + "=" * 70)
print("D. 逆像サイズ分布の完全な閉公式")
print("=" * 70)

# k奇: N(0,k) は missing count
# k奇で N(0)を計算
print("\n--- N(0,k) = missing count ---")
for k in range(3, 18):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    n_missing = len(set(odds) - set(mapping.values()))
    n_odds = len(odds)
    ratio = n_missing / n_odds
    print(f"  k={k} ({'odd' if k%2==1 else 'even'}): N(0)={n_missing}, "
          f"N(0)/n_odds={ratio:.6f}, "
          f"N(0)/2^k={n_missing/mod:.6f}")

# N(0) = n_odds - |Image| = 2^{k-1} - |Image|
# k奇: |Image| = 3/4 * 2^{k-1} → N(0) = 1/4 * 2^{k-1} = 2^{k-3}
# k偶: |Image| → 7/12 * 2^{k-1} → N(0) → 5/12 * 2^{k-1}

print("\n--- 整数値でのN(0) ---")
for k in range(3, 18):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    n_missing = len(set(odds) - set(mapping.values()))

    if k % 2 == 1:
        expected = 2**(k-3)
        print(f"  k={k} (odd): N(0)={n_missing}, 2^{k-3}={expected}, match={n_missing==expected}")
    else:
        # 5/12 * 2^{k-1} は整数でないかも
        approx = 5 * 2**(k-1) / 12
        print(f"  k={k} (even): N(0)={n_missing}, 5/12*2^{k-1}={approx:.2f}")

# ==========================================================
print("\n" + "=" * 70)
print("E. N(2,k_even) の漸化式検証")
print("   N(2, k+2) = 4 * N(2, k) - 2 ?")
print("=" * 70)

n2_even = {}
for k in range(4, 18, 2):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())
    n2_even[k] = size_dist.get(2, 0)

print("  N(2, k_even):")
for k in sorted(n2_even.keys()):
    print(f"    k={k}: N(2)={n2_even[k]}")

print("\n  4*N(2,k)-2 vs N(2,k+2):")
for k in sorted(n2_even.keys()):
    if k+2 in n2_even:
        predicted = 4 * n2_even[k] - 2
        actual = n2_even[k+2]
        print(f"    k={k}: 4*{n2_even[k]}-2={predicted}, actual N(2,{k+2})={actual}, "
              f"{'OK' if predicted==actual else f'DIFF={actual-predicted}'}")

# もう一つの仮説: N(2, k_even) = (19*4^{(k-6)/2} + 2) / 3
print("\n  代替公式検証: N(2, k_even) = (19*4^{(k-6)/2} + 2) / 3")
for k in sorted(n2_even.keys()):
    exp = (k-6)//2
    if exp >= 0:
        predicted = (19 * 4**exp + 2) // 3
        print(f"    k={k}: predicted={predicted}, actual={n2_even[k]}, "
              f"{'OK' if predicted==n2_even[k] else 'MISMATCH'}")
    else:
        print(f"    k={k}: (k-6)/2 < 0, skip")

# ==========================================================
# JSON保存
# ==========================================================
print("\n\n結果を保存中...")

all_distributions = {}
for k in range(3, 18):
    mod = 2**k
    odds = list(range(1, mod, 2))
    mapping = {n: syracuse(n) % mod for n in odds}
    preimage_count = Counter(mapping.values())
    size_dist = Counter(preimage_count.values())
    n_missing = len(set(odds) - set(mapping.values()))
    size_dist[0] = n_missing
    all_distributions[k] = dict(sorted(size_dist.items()))

output = {
    'title': 'Syracuse T mod 2^k - preimage distribution and cycle structure',
    'preimage_distributions': {str(k): v for k, v in all_distributions.items()},
    'key_findings': [
        'T mod 2^k is NEVER a bijection on odd residues (all k>=3)',
        'Within each v2-layer, T is injection (0 intra-layer collisions)',
        'Image ratio: exactly 3/4 for k odd, converging to 7/12 for k even',
        'N(0,k_odd) = 2^{k-3} exactly',
        'Preimage size distribution shifts: N(m,k) = N(m-1,k-2) for m >= 2 (k odd), m >= 3 (k even)',
        'Nontrivial invariant cycles appear at k=10,11,12 but vanish for k=13,14',
        'For k_even: N(2,k+2) = 4*N(2,k) - 2 (recurrence)',
        'Maximal invariant bijective subset is trivially {1} for most k'
    ]
}

with open('/Users/soyukke/study/lean-unsolved/results/syracuse_permgroup_v3.json', 'w') as f:
    json.dump(output, f, indent=2)

print("結果を results/syracuse_permgroup_v3.json に保存しました。")
