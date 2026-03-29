#!/usr/bin/env python3
"""
T^{-k}(1) の分岐過程モデルと閉公式の導出

核心的アイデア:
  逆BFS木では、各ノード m が以下の子を持つ:
  (1) m mod 3 != 0 なら「根逆像」r(m) を1つ持つ
  (2) さらに、それに 4n+1 鎖を適用した無限の子を持つ

  しかし、BFS木で有限の上界 N を設定すると:
  各ノード m の子の数は floor(log_4(N / r(m))) + 1

  根逆像の2/3が「肥沃」(mod 3 != 0)で、1/3が「不毛」(mod 3 = 0)。

  |T^{-k}(1) ∩ [1,N]| に閉公式があるか調べる。
"""

import math
from collections import defaultdict
import json

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

def root_preimage(m):
    """The root (minimal) preimage of m under Syracuse"""
    if m % 3 == 0:
        return None
    if m % 6 == 1:
        n = (4 * m - 1) // 3
        return n
    elif m % 6 == 5:
        n = (2 * m - 1) // 3
        return n
    else:
        return None

# ================================================================
# Part 1: BFS tree with EXACT counting (bounded by N)
# ================================================================
def bfs_bounded(start, max_depth, N_bound):
    """BFS the inverse tree from start, up to depth max_depth, with preimages <= N_bound"""
    levels = {0: {start}}
    all_seen = {start}

    for k in range(1, max_depth + 1):
        new_level = set()
        for m in levels[k-1]:
            j = 1
            while True:
                num = m * (1 << j) - 1
                if num % 3 == 0:
                    n = num // 3
                    if n > N_bound:
                        break
                    if n % 2 == 1 and n >= 1 and n not in all_seen:
                        new_level.add(n)
                j += 1
                if m * (1 << j) > 3 * N_bound + 1:
                    break
        levels[k] = new_level
        all_seen.update(new_level)
    return levels

# Compare BFS sizes for different bounds N
print("Part 1: Bound dependence of |T^{-k}(1) ∩ [1,N]|")
print("=" * 70)

bounds = [10**4, 10**5, 10**6, 10**7, 10**8]
max_k = 20

results_by_bound = {}
for N in bounds:
    levels = bfs_bounded(1, max_k, N)
    sizes = [len(levels[k]) for k in range(max_k + 1)]
    results_by_bound[N] = sizes
    print(f"\n  N = {N:.0e}:")
    for k in range(min(max_k + 1, len(sizes))):
        print(f"    k={k:2d}: {sizes[k]:>10,}")

# ================================================================
# Part 2: For large N, level sizes should be N-independent for small k
# ================================================================
print("\n\nPart 2: N-independence test (level sizes stabilize as N grows)")
print("=" * 70)

for k in range(min(15, max_k + 1)):
    sizes_at_k = [results_by_bound[N][k] for N in bounds]
    print(f"  k={k:2d}: {sizes_at_k}")
    if len(set(sizes_at_k[-2:])) == 1:
        print(f"         -> Stabilized at {sizes_at_k[-1]}")

# ================================================================
# Part 3: Mod 18 refinement (mod 6 × mod 3 transitions)
# ================================================================
print("\n\nPart 3: Mod 18 transition analysis")
print("=" * 70)

# The mod 6 transition only tells us the probability of fertility.
# Mod 18 = mod 6 × mod 3 gives a finer Markov chain.

N = 10**8
levels = bfs_bounded(1, 20, N)

for k in range(min(12, 21)):
    if len(levels[k]) == 0:
        continue
    mod18 = defaultdict(int)
    for n in levels[k]:
        mod18[n % 18] += 1
    total = len(levels[k])
    dist_str = ", ".join(f"{r}:{c}" for r, c in sorted(mod18.items()) if c > 0)
    print(f"  k={k:2d}: total={total:>8,}, mod18 = {{{dist_str}}}")

# ================================================================
# Part 4: Exact closed formula analysis
# ================================================================
print("\n\nPart 4: Exact sequence analysis")
print("=" * 70)

# Use the largest bound
N = 10**8
levels = bfs_bounded(1, 20, N)
sizes = [len(levels[k]) for k in range(21)]

print("  Exact level sizes:")
for k, s in enumerate(sizes):
    print(f"    a({k}) = {s}")

# First differences
diffs = [sizes[k+1] - sizes[k] for k in range(len(sizes)-1)]
print("\n  First differences a(k+1) - a(k):")
for k, d in enumerate(diffs):
    print(f"    k={k}: {d}")

# Second differences
diffs2 = [diffs[k+1] - diffs[k] for k in range(len(diffs)-1)]
print("\n  Second differences:")
for k, d in enumerate(diffs2):
    print(f"    k={k}: {d}")

# Ratios
print("\n  Ratios a(k+1)/a(k):")
for k in range(len(sizes)-1):
    if sizes[k] > 0:
        print(f"    k={k}: {sizes[k+1]/sizes[k]:.10f}")

# ================================================================
# Part 5: Mod 6 population dynamics
# ================================================================
print("\n\nPart 5: Mod 6 population dynamics")
print("=" * 70)

# Track (mod6=1 count, mod6=5 count, mod6=3 count) at each level
for k in range(min(20, 21)):
    if len(levels[k]) == 0:
        continue
    c1 = sum(1 for n in levels[k] if n % 6 == 1)
    c5 = sum(1 for n in levels[k] if n % 6 == 5)
    c3 = sum(1 for n in levels[k] if n % 6 == 3)  # These are dead ends
    total = c1 + c5 + c3
    print(f"  k={k:2d}: mod6=1: {c1:>8,} ({100*c1/total:5.1f}%), "
          f"mod6=5: {c5:>8,} ({100*c5/total:5.1f}%), "
          f"mod6=3: {c3:>8,} ({100*c3/total:5.1f}%)")

# ================================================================
# Part 6: Transition matrix for (mod 6 → mod 6) via root preimage
# ================================================================
print("\n\nPart 6: Root preimage mod6 transition matrix")
print("=" * 70)

# For m ≡ 1 (mod 6): root = (4m-1)/3
# m = 18q + r where r ∈ {1, 7, 13} (these are m ≡ 1 mod 6)
# m = 18q + 1: root = (4(18q+1)-1)/3 = (72q+3)/3 = 24q+1, mod6 = 1
# m = 18q + 7: root = (4(18q+7)-1)/3 = (72q+27)/3 = 24q+9, mod6 = 3
# m = 18q + 13: root = (4(18q+13)-1)/3 = (72q+51)/3 = 24q+17, mod6 = 5

print("  m ≡ 1 (mod 18): root = 24q+1 ≡ 1 (mod 6)  [fertile]")
print("  m ≡ 7 (mod 18): root = 24q+9 ≡ 3 (mod 6)  [DEAD]")
print("  m ≡ 13 (mod 18): root = 24q+17 ≡ 5 (mod 6)  [fertile]")

# For m ≡ 5 (mod 6): root = (2m-1)/3
# m = 18q + r where r ∈ {5, 11, 17}
# m = 18q + 5: root = (2(18q+5)-1)/3 = (36q+9)/3 = 12q+3, mod6 = 3
# m = 18q + 11: root = (2(18q+11)-1)/3 = (36q+21)/3 = 12q+7, mod6 = 1
# m = 18q + 17: root = (2(18q+17)-1)/3 = (36q+33)/3 = 12q+11, mod6 = 5

print("\n  m ≡ 5 (mod 18): root = 12q+3 ≡ 3 (mod 6)  [DEAD]")
print("  m ≡ 11 (mod 18): root = 12q+7 ≡ 1 (mod 6)  [fertile]")
print("  m ≡ 17 (mod 18): root = 12q+11 ≡ 5 (mod 6)  [fertile]")

# For m ≡ 3 (mod 6): NO preimage. So mod6=3 nodes are dead ends.

print("\n  Summary transition matrix (root preimage, mod6):")
print("  m mod 6 | root mod 6 | probability | fertility")
print("  --------|-----------|-------------|----------")
print("  1       | 1         | 1/3         | fertile")
print("  1       | 3         | 1/3         | DEAD")
print("  1       | 5         | 1/3         | fertile")
print("  5       | 3         | 1/3         | DEAD")
print("  5       | 1         | 1/3         | fertile")
print("  5       | 5         | 1/3         | fertile")
print("  3       | (none)    | 1           | (no preimage)")

# ================================================================
# Part 7: Full branching including 4n+1 chains
# ================================================================
print("\n\nPart 7: Full branching with 4n+1 chains")
print("=" * 70)

# Each fertile node m generates:
#   1. Root preimage r(m)
#   2. Chain: r(m), 4r(m)+1, 16r(m)+5, 64r(m)+21, ...
#
# In the BFS with bound N, the chain has length floor(log_4(N/r(m))) + 1
#
# The root r(m) ≈ m * (4/3 or 2/3).
# At level k, the typical node size m_k grows roughly as:
#   m_k ≈ c * (something)^k
#
# But the chain length = floor(log_4(N/r)) + 1 ≈ log_4(N) - log_4(m_k * const)
# As k increases, m_k grows, so chain lengths DECREASE.

# Let's verify: average chain length at each level
print("\n  Average chain length at each BFS level:")
for k in range(min(15, 21)):
    if len(levels[k]) == 0:
        continue
    chain_lengths = []
    for m in levels[k]:
        if m % 3 == 0:
            chain_lengths.append(0)
            continue
        r = root_preimage(m)
        if r is None:
            chain_lengths.append(0)
            continue
        # Chain length within [1, N]
        chain_len = 0
        n = r
        while n <= N and n >= 1:
            chain_len += 1
            n = 4 * n + 1
        chain_lengths.append(chain_len)
    avg_cl = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
    print(f"  k={k:2d}: avg_chain_length = {avg_cl:.2f}, total_children = {sum(chain_lengths)}, "
          f"nodes = {len(levels[k])}")

# ================================================================
# Part 8: Markov chain model and closed-form attempt
# ================================================================
print("\n\nPart 8: Markov chain model")
print("=" * 70)

# State: (mod6 class, approximate size range)
# But the key simplification: the mod6 transitions are UNIFORM.
# From mod6=1 or mod6=5, each generates with equal probability:
#   mod6=1 (1/3), mod6=3 (1/3), mod6=5 (1/3)
# mod6=3 is a dead end.

# So the "root-only" process has:
# fertile offspring per fertile node = 2/3
# This means the root-only tree SHRINKS: expected size -> 0

# But the 4n+1 chains provide additional nodes.
# The total size at level k (bounded by N) is:
# |T^{-k}(1) ∩ [1,N]| = sum over fertile nodes m at level k-1:
#     (chain_length of root(m) within N)

# The chain length for root r within [1,N] is:
# L(r) = floor(log_4(N/r)) + 1 if r <= N, else 0

# Since each chain step multiplies by ~4, the number of nodes at level k is:
# ~ (#fertile nodes at level k-1) * average_chain_length(k-1)

# Let f_k = #fertile nodes at level k (mod6 != 3)
# Let s_k = |T^{-k}(1) ∩ [1,N]| = total nodes at level k

# s_k = sum_{m fertile at level k-1} L(root(m))
# f_k = #{n in level k : n mod 3 != 0} ≈ (2/3) * s_k

# The average chain length at level k is approximately:
# <L>_k ≈ (1/2) * log_4(N) - (1/2) * <log_4(m)>_{level k-1}

# We need to track <log_4(m)>_k.
# The root of m has size:
#   root(m) ≈ (4/3)*m (if m mod6 = 1) or (2/3)*m (if m mod6 = 5)
# average: roughly m

# Each 4n+1 chain step gives n -> 4n+1 ≈ 4n.
# So the average log_4 of a chain element starting from r is:
# log_4(r), log_4(4r) = 1 + log_4(r), ..., up to L steps.
# Average over chain: log_4(r) + (L-1)/2

# This is getting complex. Let me try a direct numerical fit instead.

# ================================================================
# Part 9: Direct numerical fitting
# ================================================================
print("\n\nPart 9: Fitting |T^{-k}(1) ∩ [1,N]| = f(k, N)")
print("=" * 70)

# For fixed N, fit a(k) = C * lambda^k or a(k) = C * k * lambda^k

import numpy as np

# Use N = 10^8 data
sizes_arr = np.array(sizes, dtype=float)
ks = np.arange(len(sizes))

# Fit log(a(k)) = log(C) + k * log(lambda) for k >= 3
valid = sizes_arr > 0
log_sizes = np.log(sizes_arr[valid])
ks_valid = ks[valid]

# Only use k >= 3 where the pattern stabilizes
mask = ks_valid >= 3
if sum(mask) >= 3:
    coeffs = np.polyfit(ks_valid[mask], log_sizes[mask], 1)
    lambda_fit = np.exp(coeffs[0])
    C_fit = np.exp(coeffs[1])
    print(f"  Exponential fit a(k) = {C_fit:.4f} * {lambda_fit:.8f}^k")
    print(f"  Lambda = {lambda_fit:.8f}")
    print(f"  4/3 = {4/3:.8f}")
    print(f"  log2(lambda) = {np.log2(lambda_fit):.8f}")
    print(f"  log2(4/3) = {np.log2(4/3):.8f}")

    # Check fit quality
    fitted = C_fit * lambda_fit ** ks
    print("\n  Fit quality:")
    for k in range(min(20, len(sizes))):
        if sizes[k] > 0:
            error = (fitted[k] - sizes[k]) / sizes[k]
            print(f"    k={k}: actual={sizes[k]:>10,}, fitted={fitted[k]:>10,.0f}, rel_error={error:+.4f}")

# Try polynomial correction: a(k) = C * lambda^k * (alpha + beta/k)
if sum(mask) >= 4:
    # Fit log(a(k)) - k*log(lambda) vs 1/k
    residuals = log_sizes[mask] - coeffs[0] * ks_valid[mask]
    inv_k = 1.0 / ks_valid[mask]
    coeffs2 = np.polyfit(inv_k, residuals, 1)
    print(f"\n  With 1/k correction: a(k) ≈ exp({coeffs2[1]:.4f} + {coeffs2[0]:.4f}/k) * {lambda_fit:.8f}^k")

# ================================================================
# Part 10: Comparison with different N values
# ================================================================
print("\n\nPart 10: Lambda as a function of N")
print("=" * 70)

for N_val, sizes_list in results_by_bound.items():
    sizes_arr = np.array(sizes_list, dtype=float)
    valid = sizes_arr > 0
    if sum(valid) < 5:
        continue
    ks_v = np.arange(len(sizes_list))[valid]
    log_s = np.log(sizes_arr[valid])
    mask = ks_v >= 3
    if sum(mask) >= 3:
        coeffs = np.polyfit(ks_v[mask], log_s[mask], 1)
        lam = np.exp(coeffs[0])
        print(f"  N = {N_val:.0e}: lambda = {lam:.8f}, log2(lambda) = {np.log2(lam):.8f}")

# The lambda should decrease with N (because chain lengths decrease for larger k).
# Or rather, for fixed N, as k increases, the preimages get larger and hit the N bound.

# Actually, for the UNBOUNDED case (N = infinity), |T^{-k}(1)| = infinity for all k >= 1!
# The interesting quantity is the bounded version.

# The growth rate for bounded case:
# As N -> infinity, the effective lambda should approach 4/3 (since each step adds 1/3 more)
# But the chain length decreases, so there's a competition.

# ================================================================
# Output results
# ================================================================
print("\n\nFinal Summary")
print("=" * 70)

# Core data
core_results = {
    "level_sizes_N1e8": sizes,
    "growth_ratios": [sizes[k+1]/sizes[k] if sizes[k] > 0 else None for k in range(len(sizes)-1)],
    "mod6_transition": {
        "from_mod6_1": {"to_1": "1/3", "to_3": "1/3 (dead)", "to_5": "1/3"},
        "from_mod6_5": {"to_1": "1/3", "to_3": "1/3 (dead)", "to_5": "1/3"},
        "from_mod6_3": "no preimage (dead end)"
    },
    "fertility_rate": "2/3 of root preimages are fertile (mod3 != 0)",
    "chain_property": "4n+1 generates additional preimages at same level"
}

print(f"  Level sizes for N=10^8: {sizes[:15]}")
print(f"  Growth ratios: {[f'{r:.4f}' for r in core_results['growth_ratios'][:15] if r]}")

with open("/Users/soyukke/study/lean-unsolved/results/Tk_inverse_tree_branching_data.json", "w") as f:
    json.dump(core_results, f, indent=2, default=str)

print("\nDone.")
