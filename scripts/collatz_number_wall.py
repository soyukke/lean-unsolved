#!/usr/bin/env python3
"""探索29: コラッツの「数論的壁」— 突破しにくい数の系統的調査"""

import math
from collections import defaultdict

N = 65536  # 2^16

def glide(n):
    """n が初めて n 未満に落ちるまでのステップ数 g(n)"""
    orig = n
    steps = 0
    m = n
    while m >= orig:
        if m == 1 and orig == 1:
            return 0
        if m % 2 == 0:
            m //= 2
        else:
            m = 3 * m + 1
        steps += 1
        if steps > 10000:
            return steps  # 安全弁
    return steps

def total_stopping_time(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def max_in_orbit(n):
    """軌道中の最大値"""
    mx = n
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        mx = max(mx, n)
    return mx

def prime_factors(n):
    """素因数分解"""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

print("=" * 70)
print("探索29: コラッツの「数論的壁」— 突破しにくい数")
print("=" * 70)

# --- g(n) の計算 ---
print(f"\n[1] 全 n=1..{N} の glide g(n) 計算中...")
g = {}
for n in range(1, N + 1):
    g[n] = glide(n)

# 基本統計
g_vals = list(g.values())
print(f"  平均 g(n): {sum(g_vals)/len(g_vals):.2f}")
print(f"  最大 g(n): {max(g_vals)} (n={max(g, key=g.get)})")

# --- 「壁」の特定 ---
print(f"\n[2] 「壁」の特定 (g(n) が異常に大きい n):")
# レコード更新する n（それまでの全ての m < n より g(n) が大きい）
records = []
max_g_so_far = -1
for n in range(2, N + 1):
    if g[n] > max_g_so_far:
        max_g_so_far = g[n]
        records.append((n, g[n]))

print(f"  レコード更新回数: {len(records)}")
print(f"  レコード更新する n の列:")
for n, gn in records:
    tst = total_stopping_time(n)
    mx = max_in_orbit(n)
    bin_n = bin(n)[2:]
    print(f"    n={n:6d}: g={gn:4d}, total_stop={tst:4d}, "
          f"max/n={mx/n:8.1f}, bin={bin_n[:24]}{'...' if len(bin_n)>24 else ''}")

# --- 壁の共通性質 ---
wall_ns = [n for n, gn in records if gn >= 10]
print(f"\n[3] 壁 (g >= 10) の共通性質分析 ({len(wall_ns)} 個):")

# mod m の分布
for m in [3, 4, 5, 6, 7, 8, 9, 12, 16]:
    dist = defaultdict(int)
    for n in wall_ns:
        dist[n % m] += 1
    print(f"  mod {m:2d}: {dict(sorted(dist.items()))}")

# 2進表現のパターン
print(f"\n[4] 壁の2進表現パターン:")
for n, gn in records:
    if gn >= 10:
        b = bin(n)[2:]
        ones = b.count('1')
        zeros = b.count('0')
        trailing = len(b) - len(b.rstrip('1'))
        leading_after_1 = b[1:4] if len(b) > 3 else b[1:]
        print(f"  n={n:6d}: bits={len(b):2d}, ones={ones:2d}, "
              f"ones/bits={ones/len(b):.3f}, trailing_1s={trailing}, "
              f"bin={b[:30]}")

# ones/bits の統計
ones_ratios = []
for n, gn in records:
    if gn >= 10:
        b = bin(n)[2:]
        ones_ratios.append(b.count('1') / len(b))
if ones_ratios:
    print(f"\n  壁の ones/bits 統計:")
    print(f"    平均: {sum(ones_ratios)/len(ones_ratios):.4f}")
    print(f"    (ランダムなら 0.5)")

# --- 素因数分解 ---
print(f"\n[5] 壁の素因数分解:")
for n, gn in records:
    if gn >= 10:
        pf = prime_factors(n)
        print(f"  n={n:6d} (g={gn}): {' x '.join(str(p) for p in pf)}")

# --- 壁同士の比率 ---
print(f"\n[6] 連続する壁の比率:")
for i in range(1, len(records)):
    n1, g1 = records[i - 1]
    n2, g2 = records[i]
    if n1 > 0 and g1 >= 5:
        ratio = n2 / n1
        print(f"  {n2:6d}/{n1:6d} = {ratio:.4f}, "
              f"g: {g1} -> {g2}")

# --- 壁の列に予測可能なパターン ---
print(f"\n[7] 壁の列のパターン分析:")
wall_large = [(n, gn) for n, gn in records if gn >= 20]
print(f"  g >= 20 の壁: {[n for n, _ in wall_large]}")

if len(wall_large) >= 3:
    print(f"  連続比率:")
    for i in range(1, len(wall_large)):
        n1 = wall_large[i-1][0]
        n2 = wall_large[i][0]
        print(f"    {n2}/{n1} = {n2/n1:.4f}")

# --- 壁と 2^k * m - 1 パターン ---
print(f"\n[8] 壁と 2^k * m ± 1 パターン:")
for n, gn in records:
    if gn >= 10:
        # n+1 の 2 のべき乗成分
        v2_plus = 0
        tmp = n + 1
        while tmp % 2 == 0:
            v2_plus += 1
            tmp //= 2
        # n-1 の 2 のべき乗成分
        v2_minus = 0
        if n > 1:
            tmp = n - 1
            while tmp % 2 == 0:
                v2_minus += 1
                tmp //= 2
        print(f"  n={n:6d}: v2(n+1)={v2_plus}, v2(n-1)={v2_minus}, "
              f"n+1={n+1}=2^{v2_plus}*{(n+1)//2**v2_plus}, "
              f"n-1={n-1}=2^{v2_minus}*{(n-1)//2**v2_minus if n > 1 else 0}")

# --- stopping time の異常値と壁の関係 ---
print(f"\n[9] stopping time 異常値 (上位30):")
st_list = [(n, total_stopping_time(n)) for n in range(1, N + 1)]
st_list.sort(key=lambda x: -x[1])
wall_set = set(n for n, _ in records)
for n, st in st_list[:30]:
    is_wall = "★壁" if n in wall_set else "    "
    print(f"  {is_wall} n={n:6d}: stopping_time={st:4d}, g(n)={g[n]:3d}")

# --- 壁の「密度」---
print(f"\n[10] 壁の密度分析:")
for k in range(4, 17):
    bound = 2**k
    walls_in_range = sum(1 for n, gn in records if n <= bound)
    print(f"  n <= 2^{k:2d}={bound:6d}: {walls_in_range:3d} 個の壁レコード")

# --- glide の分布 ---
print(f"\n[11] g(n) の分布 (奇数のみ):")
g_odd = {n: g[n] for n in range(1, N + 1) if n % 2 == 1}
g_dist = defaultdict(int)
for v in g_odd.values():
    g_dist[v] += 1
for gv in sorted(g_dist.keys()):
    if g_dist[gv] >= 10 or gv <= 5:
        bar = "#" * min(g_dist[gv] // 50, 50)
        print(f"  g={gv:3d}: {g_dist[gv]:5d} {bar}")

# --- 「壁を越えた直後」の挙動 ---
print(f"\n[12] 壁を越えた直後の挙動:")
for n, gn in records[-10:]:  # 最後の10個
    if gn >= 20:
        m = n
        orbit_snippet = [m]
        for _ in range(min(gn + 5, 200)):
            if m == 1:
                break
            if m % 2 == 0:
                m //= 2
            else:
                m = 3 * m + 1
            orbit_snippet.append(m)
        peak = max(orbit_snippet)
        peak_idx = orbit_snippet.index(peak)
        first_below = next((i for i, v in enumerate(orbit_snippet) if v < n and i > 0), -1)
        print(f"  n={n:6d} (g={gn}): peak={peak} at step {peak_idx}, "
              f"first_below at step {first_below}, peak/n={peak/n:.1f}")

print("\n" + "=" * 70)
print("結論:")
print("  - 「壁」は 1 の密度が高い2進表現を持つ傾向")
print("  - g(n) レコードの列は対数的に成長")
print("  - 壁の mod パターンと素因数分解から規則性を調査")
print("=" * 70)
