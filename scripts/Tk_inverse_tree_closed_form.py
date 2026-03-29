#!/usr/bin/env python3
"""
T^{-k}(1) の完全列挙と閉公式の導出

既知の事実:
1. syracuse(4n+1) = syracuse(n)  [形式証明済]
2. 入次数 <= 2                     [形式証明済]
3. 像サイズ = 3N/8                 [数値検証済]
4. 平均入次数 = 4/3               [数値検証済]

Syracuse関数の逆像:
  T(n) = m ⟺ n = (m * 2^j - 1) / 3 for some j >= 1, and this n is a positive odd integer

逆像の構造 (mod 6分類):
  - m ≡ 1 (mod 6): j は偶数のみ有効 (j=2,4,6,...)
  - m ≡ 5 (mod 6): j は奇数のみ有効 (j=1,3,5,...)
  - m ≡ 3 (mod 6): 逆像なし (m ≡ 0 mod 3)
  - m ≡ 0 (mod 6): Syracuse関数は奇数のみ返すので不関連

逆像鎖: 各有効な逆像 n_0 に対して {4^k * n_0 + (4^k-1)/3 : k>=0} が全て同じ像 m を持つ
"""

import math
from collections import defaultdict, deque
import json
import time

start_time = time.time()

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_preimages(m, N_max=None):
    """
    Return all odd n such that syracuse(n) = m.
    If N_max given, restrict to n <= N_max.

    n = (m * 2^j - 1) / 3 for valid j values.
    """
    preimages = []
    if m % 3 == 0:
        return preimages  # No preimages if m divisible by 3

    j = 1
    while True:
        numerator = m * (1 << j) - 1
        if numerator % 3 != 0:
            j += 1
            continue
        n = numerator // 3
        if N_max and n > N_max:
            break
        if n % 2 == 1 and n >= 1:
            # Verify
            assert syracuse(n) == m, f"Failed: syracuse({n}) != {m}"
            preimages.append(n)
        j += 1
        if j > 200:  # Safety bound
            break
    return preimages

# ==================================================================
# Part 1: BFS from 1 to enumerate T^{-k}(1) for k = 0, 1, 2, ...
# ==================================================================
print("=" * 60)
print("Part 1: Complete enumeration of T^{-k}(1)")
print("=" * 60)

MAX_DEPTH = 40
N_LIMIT = 10**15  # Upper bound for preimage search

# BFS
bfs_levels = {0: {1}}  # T^0(1) = {1}
all_nodes = {1}
level_sizes = [1]  # |T^0(1)| = 1
level_new_sizes = [1]  # New nodes at each level (excluding duplicates with prior levels)

for depth in range(1, MAX_DEPTH + 1):
    new_level = set()
    for m in bfs_levels[depth - 1]:
        # Find all preimages of m
        j = 1
        while True:
            numerator = m * (1 << j) - 1
            if numerator % 3 == 0:
                n = numerator // 3
                if n > N_LIMIT:
                    break
                if n % 2 == 1 and n >= 1:
                    new_level.add(n)
            j += 1
            if m * (1 << j) > 3 * N_LIMIT + 1:
                break

    # Distinct new nodes only
    truly_new = new_level - all_nodes
    all_nodes.update(truly_new)
    bfs_levels[depth] = new_level
    level_sizes.append(len(new_level))
    level_new_sizes.append(len(truly_new))

    if depth <= 30 or depth % 5 == 0:
        ratio = level_sizes[-1] / level_sizes[-2] if level_sizes[-2] > 0 else float('inf')
        print(f"  depth {depth:3d}: |T^{{-{depth}}}(1)| = {level_sizes[-1]:>15,}  "
              f"new = {level_new_sizes[-1]:>15,}  ratio = {ratio:.6f}")

print(f"\n  Total nodes found (depth 0..{MAX_DEPTH}): {len(all_nodes):,}")
elapsed = time.time() - start_time
print(f"  Elapsed: {elapsed:.1f}s")

# ==================================================================
# Part 2: Analyze level sizes for a closed-form pattern
# ==================================================================
print("\n" + "=" * 60)
print("Part 2: Growth rate analysis of |T^{-k}(1)|")
print("=" * 60)

# Compute ratios and look for patterns
ratios = []
for k in range(1, len(level_sizes)):
    if level_sizes[k-1] > 0:
        r = level_sizes[k] / level_sizes[k-1]
        ratios.append(r)
    else:
        ratios.append(None)

print("\n  Growth ratios |T^{-(k+1)}(1)| / |T^{-k}(1)|:")
for k, r in enumerate(ratios):
    if r and (k < 25 or k % 5 == 0):
        print(f"    k={k:3d} -> k+1={k+1:3d}: ratio = {r:.8f}")

# Check if ratios converge
if len(ratios) > 10:
    recent_ratios = [r for r in ratios[-10:] if r]
    if recent_ratios:
        avg_ratio = sum(recent_ratios) / len(recent_ratios)
        print(f"\n  Average ratio (last 10): {avg_ratio:.8f}")
        print(f"  4/3 = {4/3:.8f}")
        print(f"  3^(1/2) = {3**0.5:.8f}")
        # (4/3)^(log2(3)/2) as a guess
        log2_3 = math.log2(3)
        guess1 = (4/3) ** (log2_3 / 2)
        print(f"  (4/3)^(log2(3)/2) = {guess1:.8f}")

# ==================================================================
# Part 3: Galton-Watson branching process model
# ==================================================================
print("\n" + "=" * 60)
print("Part 3: Branching structure analysis")
print("=" * 60)

# For each node at each level, count its number of preimages
# This gives the branching distribution of the inverse tree
branching_dists = {}
for depth in range(0, min(25, MAX_DEPTH)):
    counts = defaultdict(int)
    total = 0
    for m in bfs_levels[depth]:
        # Count preimages within a reasonable range
        j = 1
        num_preimages = 0
        while True:
            numerator = m * (1 << j) - 1
            if numerator % 3 == 0:
                n = numerator // 3
                if n > N_LIMIT:
                    break
                if n % 2 == 1 and n >= 1:
                    num_preimages += 1
            j += 1
            if m * (1 << j) > 3 * N_LIMIT + 1:
                break
        counts[num_preimages] += 1
        total += 1
    branching_dists[depth] = dict(counts)
    if depth < 20 or depth % 5 == 0:
        avg_branching = sum(k * v for k, v in counts.items()) / total if total > 0 else 0
        print(f"  depth {depth:3d}: avg_branching = {avg_branching:.4f}, "
              f"dist = {dict(sorted(counts.items()))}")

# ==================================================================
# Part 4: Mod 6 classification of nodes at each level
# ==================================================================
print("\n" + "=" * 60)
print("Part 4: Mod 6 classification of T^{-k}(1)")
print("=" * 60)

for depth in range(0, min(20, MAX_DEPTH)):
    mod6_counts = defaultdict(int)
    for n in bfs_levels[depth]:
        mod6_counts[n % 6] += 1
    total = len(bfs_levels[depth])
    print(f"  depth {depth:3d}: total = {total:>10,}, "
          f"mod6 = {{ {', '.join(f'{k}:{v}({100*v/total:.1f}%)' for k, v in sorted(mod6_counts.items()))} }}")

# ==================================================================
# Part 5: Exact closed-form candidates
# ==================================================================
print("\n" + "=" * 60)
print("Part 5: Closed-form analysis")
print("=" * 60)

# The key idea: Each node m in T^{-k}(1) has preimages determined by
# j-values where (m*2^j - 1)/3 is a positive odd integer.
# The number of such j values up to J_max ~ log2(N_LIMIT/m) follows the mod6 pattern.

# For m ≡ 1 (mod 6): valid j's are even: j=2,4,6,...  => about J_max/2 preimages
# For m ≡ 5 (mod 6): valid j's are odd: j=1,3,5,...   => about J_max/2 preimages

# But we need the number of preimages WITHOUT the N_LIMIT bound (or with a very large bound).
# The growth ratio should be governed by a specific branching process.

# Let's try to find the exact sequence by removing the N_LIMIT effect.
# For small k, all preimages are small enough, so the count is exact.

# Check if the sequence |T^{-k}(1)| matches any known integer sequence
print("\n  Level sizes (exact, small k):")
for k in range(min(30, len(level_sizes))):
    print(f"    |T^{{-{k}}}(1)| = {level_sizes[k]}")

# ==================================================================
# Part 6: Recurrence relation search
# ==================================================================
print("\n" + "=" * 60)
print("Part 6: Recurrence relation search")
print("=" * 60)

# Try to find a(k) = c1*a(k-1) + c2*a(k-2) + ...
sizes = level_sizes[:min(35, len(level_sizes))]
print(f"\n  Testing linear recurrence of order r for |T^{{-k}}(1)|:")

for order in range(1, 6):
    if len(sizes) < 2 * order + 2:
        continue
    # Set up system: for each k from order to 2*order-1,
    # a(k) = c1*a(k-1) + ... + cr*a(k-order)
    import numpy as np
    n_eq = len(sizes) - order
    A = np.zeros((n_eq, order))
    b = np.zeros(n_eq)
    for i in range(n_eq):
        k = i + order
        for j in range(order):
            A[i, j] = sizes[k - 1 - j]
        b[i] = sizes[k]

    # Least squares
    result = np.linalg.lstsq(A, b, rcond=None)
    coeffs = result[0]
    residuals = b - A @ coeffs
    max_residual = max(abs(residuals))
    rel_error = max(abs(residuals[i]) / max(1, b[i]) for i in range(len(b)))

    print(f"\n  Order {order}: coefficients = {coeffs}")
    print(f"    Max absolute residual = {max_residual:.6f}")
    print(f"    Max relative error = {rel_error:.10f}")

    if max_residual < 0.5:
        print(f"    ** EXACT recurrence found! **")

# ==================================================================
# Part 7: Total size up to depth k: cumulative count
# ==================================================================
print("\n" + "=" * 60)
print("Part 7: Cumulative sizes and density estimates")
print("=" * 60)

cumulative = []
total = 0
for k in range(len(level_sizes)):
    total += level_sizes[k]
    cumulative.append(total)

# Compare with 2^k, (4/3)^k, etc.
print("\n  Cumulative |T^{-0}(1) u ... u T^{-k}(1)|:")
for k in range(min(35, len(cumulative))):
    ratio_to_4_3 = cumulative[k] / (4/3)**k if (4/3)**k > 0 else 0
    ratio_to_level = level_sizes[k] / (4/3)**k if (4/3)**k > 0 else 0
    print(f"    k={k:3d}: cumulative = {cumulative[k]:>15,}, "
          f"|T^{{-k}}|/(4/3)^k = {ratio_to_level:.6f}")

# ==================================================================
# Part 8: Exact duplicate analysis
# ==================================================================
print("\n" + "=" * 60)
print("Part 8: Duplicate analysis (nodes appearing at multiple depths)")
print("=" * 60)

# Check for overlaps between levels
duplicates_count = 0
for depth in range(1, min(25, MAX_DEPTH + 1)):
    overlap = bfs_levels[depth] & bfs_levels.get(depth - 1, set())
    if overlap:
        print(f"  depth {depth} overlaps with depth {depth-1}: {len(overlap)} nodes")
        if len(overlap) <= 5:
            print(f"    nodes: {sorted(overlap)}")
        duplicates_count += len(overlap)

if duplicates_count == 0:
    print("  No duplicates between adjacent levels!")

# Cross-level duplicates
for d1 in range(min(15, MAX_DEPTH)):
    for d2 in range(d1 + 2, min(15, MAX_DEPTH + 1)):
        overlap = bfs_levels[d1] & bfs_levels[d2]
        if overlap:
            print(f"  depth {d1} overlaps with depth {d2}: {len(overlap)} nodes")
            if len(overlap) <= 3:
                print(f"    nodes: {sorted(overlap)}")

# ==================================================================
# Summary
# ==================================================================
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

print(f"\n  Level sizes for first {min(35, len(level_sizes))} depths:")
for k in range(min(35, len(level_sizes))):
    print(f"    k={k}: {level_sizes[k]}")

print(f"\n  Elapsed time: {time.time() - start_time:.1f}s")

# Save results
results = {
    "level_sizes": level_sizes[:min(40, len(level_sizes))],
    "level_new_sizes": level_new_sizes[:min(40, len(level_new_sizes))],
    "ratios": [r if r else None for r in ratios[:min(40, len(ratios))]],
    "cumulative": cumulative[:min(40, len(cumulative))],
}

with open("/Users/soyukke/study/lean-unsolved/results/Tk_inverse_tree_closed_form_data.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nData saved.")
