#!/usr/bin/env python3
"""
T^{-k}(1) の逆像ツリーの理論的分析

理論的背景:
  Syracuse関数 T(n) = (3n+1) / 2^{v2(3n+1)} の逆像は
  n = (m * 2^j - 1) / 3  (j = 1, 2, 3, ...)

  mod 6 分類:
  - m ≡ 1 (mod 6) => 有効な j は偶数 (j=2,4,6,...)
  - m ≡ 5 (mod 6) => 有効な j は奇数 (j=1,3,5,...)
  - m ≡ 3 (mod 6) => 逆像なし

  逆像鎖: n_0 が T(n_0) = m の根ならば
  n_k = 4^k * n_0 + (4^k - 1) / 3 も T(n_k) = m を満たす

核心的問題:
  |T^{-k}(1)| の閉公式は存在するか?
  逆BFS成長率は何に収束するか?
"""

import math
from collections import defaultdict

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

# ============================================================
# Part A: Small-depth exact analysis
# ============================================================
print("Part A: Exact T^{-k}(1) for small k with full mod6 classification")
print("=" * 70)

def get_preimages(m):
    """Get all preimages of m under Syracuse, with their j-values"""
    if m % 3 == 0:
        return []
    results = []
    j = 1
    while j <= 100:  # j up to 100 covers very large preimages
        num = m * (1 << j) - 1
        if num % 3 == 0:
            n = num // 3
            if n % 2 == 1 and n >= 1:
                results.append((n, j))
        j += 1
    return results

# The root preimages (minimal j) for each m
def root_preimage(m):
    """The minimal preimage of m"""
    if m % 3 == 0:
        return None
    if m % 6 == 1:
        # j_min = 2: n = (4m-1)/3
        n = (4 * m - 1) // 3
        assert (4 * m - 1) % 3 == 0
        assert n % 2 == 1
        return n, 2
    elif m % 6 == 5:
        # j_min = 1: n = (2m-1)/3
        n = (2 * m - 1) // 3
        assert (2 * m - 1) % 3 == 0
        assert n % 2 == 1
        return n, 1
    else:
        return None

# Enumerate T^{-k}(1) exactly for small k
levels = {0: {1}}
for k in range(1, 25):
    new_level = set()
    for m in levels[k-1]:
        rp = root_preimage(m)
        if rp is not None:
            n0, j_min = rp
            # All preimages: n_i = 4^i * n0 + (4^i - 1)/3 for i = 0, 1, 2, ...
            for i in range(100):
                n_i = (4**i) * n0 + ((4**i) - 1) // 3
                if n_i > 10**18:
                    break
                new_level.add(n_i)
    levels[k] = new_level

print(f"\n  {'k':>3} | {'|T^{-k}(1)|':>15} | {'ratio':>12} | {'mod6 dist':>40}")
print("  " + "-" * 80)

prev_size = 1
for k in range(25):
    size = len(levels[k])
    ratio = size / prev_size if prev_size > 0 else 0
    mod6 = defaultdict(int)
    for n in levels[k]:
        mod6[n % 6] += 1
    mod6_str = ", ".join(f"{r}:{c}" for r, c in sorted(mod6.items()))
    print(f"  {k:3d} | {size:15,} | {ratio:12.6f} | {mod6_str}")
    prev_size = size

# ============================================================
# Part B: Branching structure analysis
# ============================================================
print("\n\nPart B: Branching structure of the inverse tree")
print("=" * 70)

# For each node m at depth k, the number of children is:
# - 0 if m ≡ 0 (mod 3)
# - infinite in principle (all 4^i * root + offset)
# But for finite depth, each node contributes exactly 1 new root + all extensions from previous roots.

# Actually, the key insight: at each level, a node m with mod6=1 or mod6=5
# has EXACTLY ONE root preimage, plus EACH previous-level preimage n of m
# generates a 4n+1 extension.

# More precisely: the BFS tree has the property that each node at level k
# branches into its root preimage at level k+1.
# But the 4n+1 chain means: if n is at level k, then 4n+1 is ALSO at level k+1
# (since T(4n+1) = T(n), so 4n+1 is a preimage of T(n) which was at level k-1)

# Wait, this needs careful thought. Let me re-examine.
# T(n) = m means n is a preimage of m.
# T(4n+1) = T(n) = m, so 4n+1 is ALSO a preimage of m.
# So if n ∈ T^{-1}(m), then 4n+1 ∈ T^{-1}(m) as well.

# For the BFS tree T^{-k}(1):
# T^{-1}(1) = {5, 21, 85, 341, ...} = {5 * 4^i + (4^i-1)/3 | i=0,1,...}
# Wait let me compute directly.

print("\n  Direct computation of T^{-1}(1):")
for j in range(1, 20):
    num = 1 * (1 << j) - 1
    if num % 3 == 0:
        n = num // 3
        if n % 2 == 1:
            print(f"    j={j}: n = (2^{j} - 1)/3 = {n}, mod6 = {n%6}")

# Root of 1: m=1, mod6=1, so root = (4-1)/3 = 1. But 1 is 1 itself!
# Actually wait: root of m=1 is (4*1-1)/3 = 1 which is a fixed point.
# But 1 ≡ 1 (mod 6), so j_min = 2, n = (4-1)/3 = 1.
# So T(1) = (3+1)/2^2 = 1. Self-loop!

# The NEXT preimage: j=4: n = (16-1)/3 = 5
# j=6: n = (64-1)/3 = 21
# j=8: n = (256-1)/3 = 85

# So T^{-1}(1) \ {1} = {5, 21, 85, 341, 1365, ...}
# n_i = (4^{i+2} - 1)/3 for i = 0, 1, 2, ...
# = (4^2 * 4^i - 1)/3

# Actually: n_i = 4^i * 5 + (4^i - 1)/3 for i >= 0
# n_0 = 5, n_1 = 4*5 + 1 = 21, n_2 = 16*5 + 5 = 85

print("\n  T^{-1}(1) chain: root=5 (excluding self-loop at 1)")
for i in range(10):
    n_i = (4**i) * 5 + ((4**i) - 1) // 3
    print(f"    i={i}: n = {n_i}, mod6 = {n_i % 6}, verify T(n) = {syracuse(n_i)}")

# ============================================================
# Part C: Non-overlapping tree structure
# ============================================================
print("\n\nPart C: Tree structure - checking if T^{-k}(1) form a tree (no cycles)")
print("=" * 70)

# The DISTINCT preimage tree:
# Level 0: {1}
# Level 1: all DISTINCT preimages of 1, excluding 1 itself
# Level 2: all DISTINCT preimages of Level 1 nodes, excluding nodes already seen
# etc.

# Let's compute this "true tree" without self-loops and duplicates
true_levels = {0: {1}}
all_seen = {1}

for k in range(1, 25):
    new_nodes = set()
    for m in true_levels[k-1]:
        for j in range(1, 100):
            num = m * (1 << j) - 1
            if num % 3 == 0:
                n = num // 3
                if n > 10**18:
                    break
                if n % 2 == 1 and n >= 1 and n not in all_seen:
                    new_nodes.add(n)
    true_levels[k] = new_nodes
    all_seen.update(new_nodes)
    ratio = len(new_nodes) / len(true_levels[k-1]) if len(true_levels[k-1]) > 0 else 0
    print(f"  depth {k:3d}: |new nodes| = {len(new_nodes):>12,}, ratio = {ratio:.6f}")

# ============================================================
# Part D: Generating function / recurrence for level sizes
# ============================================================
print("\n\nPart D: Analyzing the level-size sequence")
print("=" * 70)

# Level sizes of the true tree
true_sizes = [len(true_levels[k]) for k in range(min(25, len(true_levels)))]
print("  True tree level sizes:")
for k, s in enumerate(true_sizes):
    print(f"    k={k}: {s}")

# Check successive ratios
print("\n  Successive ratios:")
for k in range(1, len(true_sizes)):
    if true_sizes[k-1] > 0:
        r = true_sizes[k] / true_sizes[k-1]
        print(f"    a({k})/a({k-1}) = {r:.10f}")

# Try to find the pattern: each node at level k generates preimages at level k+1
# A node m has:
#   - If m mod 3 != 0: infinitely many preimages (but within bound, finitely many)
#   - If m mod 3 == 0: no preimages
# But in practice, most preimages are very large (exponentially growing)
# So the effective branching factor depends on the j-cutoff

# For the INFINITE tree (no bound):
# Each m ≡ 1 (mod 6) has one root preimage (j=2) plus one extension per existing preimage
# Each m ≡ 5 (mod 6) has one root preimage (j=1) plus extensions
# Each m ≡ 3 (mod 6) has NO preimages

# At depth k of the BFS tree,
# the number of nodes is exactly the number of distinct preimages paths of length k from 1

# ============================================================
# Part E: Theoretical growth rate
# ============================================================
print("\n\nPart E: Theoretical growth rate analysis")
print("=" * 70)

# The growth rate should be related to the average number of DISTINCT preimages
# For the Syracuse function:
# - fraction of odd numbers with m mod 3 != 0 is 2/3
# - each such m has one "root" preimage chain
# - the 4n+1 extension means infinite preimages, but bounded in practice

# For the BFS without upper bound:
# Level 0: {1}
# Level 1: root preimage of 1 = {5}, plus 4*1+1=5 (already counted!),
#           plus chain: {5, 21, 85, 341, ...}
# Wait, 4*1+1 = 5, and T(5) = T(1) = 1. But 5 is also the root preimage of 1.

# So |T^{-1}(1)| is INFINITE (unbounded).
# The question is really about the BFS tree WITH a bound N.

# Let's think about this differently.
# Each node m at level k has:
#   - One root preimage r(m) (if m mod 3 != 0)
#   - For each existing preimage n of m at level k+1, 4n+1 is ALSO a preimage of m
#     but it's at the SAME level k+1

# The number of preimages of m within [1, N] is approximately log_4(N / m) / 2
# (since each chain step multiplies by ~4)

# For the BFS tree:
# The number of DISTINCT elements at level k (with bound N) grows like
# the number of "root preimages" at each step.

# Root preimage generation:
# If m mod 3 != 0 (prob 2/3 among odd m), m has exactly 1 root preimage.
# That root preimage has mod6 distribution that we can compute.

# Let's compute the mod6 transition matrix
print("\n  Mod 6 transition matrix for root preimages:")
print("  (m mod 6 -> root_preimage(m) mod 6)")

for m_mod6 in [1, 5]:
    rp = root_preimage(m_mod6)
    if rp:
        n, j = rp
        # But we need to check all m with this mod6 value
        # Actually, let's compute for a range of m values
        trans = defaultdict(int)
        total = 0
        for m in range(1, 10000, 2):
            if m % 6 != m_mod6:
                continue
            if m % 3 == 0:
                continue
            rp = root_preimage(m)
            if rp:
                n, j = rp
                trans[n % 6] += 1
                total += 1
        print(f"  m ≡ {m_mod6} (mod 6): ", end="")
        for r in sorted(trans.keys()):
            print(f"{r}: {trans[r]}/{total} ({100*trans[r]/total:.1f}%), ", end="")
        print()

# Also need: what fraction of preimages have m mod 3 == 0 (i.e., childless)?
print("\n  Fraction of nodes with mod3 == 0 (childless) at each level:")
for k in range(min(15, len(true_levels))):
    childless = sum(1 for n in true_levels[k] if n % 3 == 0)
    total = len(true_levels[k])
    if total > 0:
        print(f"    k={k}: {childless}/{total} = {childless/total:.4f}")

# ============================================================
# Part F: Root-only tree (ignoring 4n+1 chains)
# ============================================================
print("\n\nPart F: Root-only tree (1 root preimage per node, no chain extensions)")
print("=" * 70)

root_levels = {0: {1}}
root_all_seen = {1}

for k in range(1, 30):
    new_nodes = set()
    for m in root_levels[k-1]:
        if m % 3 == 0:
            continue
        rp = root_preimage(m)
        if rp is not None:
            n, j = rp
            if n not in root_all_seen:
                new_nodes.add(n)
    root_levels[k] = new_nodes
    root_all_seen.update(new_nodes)
    ratio = len(new_nodes) / len(root_levels[k-1]) if len(root_levels[k-1]) > 0 else 0
    childless = sum(1 for n in new_nodes if n % 3 == 0)
    print(f"  k={k:3d}: |nodes| = {len(new_nodes):>10,}, ratio = {ratio:.6f}, "
          f"childless = {childless} ({100*childless/max(1,len(new_nodes)):.1f}%)")

root_sizes = [len(root_levels[k]) for k in range(min(30, len(root_levels)))]
print(f"\n  Root-only sizes: {root_sizes[:20]}")

# Theory: if m mod 3 != 0, root_preimage(m) exists.
# The root_preimage has mod3 != 0 iff ... let's check
print("\n  Root preimage mod 3 analysis:")
for m_mod in [1, 5]:
    vals = []
    for m in range(m_mod, 1000, 6):
        rp = root_preimage(m)
        if rp:
            vals.append(rp[0] % 3)
    from collections import Counter
    c = Counter(vals)
    total = len(vals)
    print(f"    m ≡ {m_mod} (mod 6): root mod 3 distribution = {dict(c)}, "
          f"fraction mod3!=0: {(c.get(1,0)+c.get(2,0))/total:.4f}")

print("\n  Key conclusion: What fraction of root preimages are 'fertile' (mod 3 != 0)?")
# m ≡ 1 (mod 6): root = (4m-1)/3
# If m = 6q+1, root = (24q+3)/3 = 8q+1
# 8q+1 mod 3: depends on q mod 3
#   q ≡ 0: 1 mod 3 (fertile)
#   q ≡ 1: 8+1 = 9 ≡ 0 mod 3 (infertile!)
#   q ≡ 2: 16+1 = 17 ≡ 2 mod 3 (fertile)

# m ≡ 5 (mod 6): root = (2m-1)/3
# If m = 6q+5, root = (12q+9)/3 = 4q+3
# 4q+3 mod 3:
#   q ≡ 0: 3 ≡ 0 mod 3 (infertile!)
#   q ≡ 1: 7 ≡ 1 mod 3 (fertile)
#   q ≡ 2: 11 ≡ 2 mod 3 (fertile)

print("""
  Theory:
  m ≡ 1 (mod 6): root = (4m-1)/3 = 8q+1 where m = 6q+1
    q ≡ 0 (mod 3) => root ≡ 1 (mod 3): fertile
    q ≡ 1 (mod 3) => root ≡ 0 (mod 3): INFERTILE
    q ≡ 2 (mod 3) => root ≡ 2 (mod 3): fertile
    => 2/3 fertile, 1/3 infertile

  m ≡ 5 (mod 6): root = (2m-1)/3 = 4q+3 where m = 6q+5
    q ≡ 0 (mod 3) => root ≡ 0 (mod 3): INFERTILE
    q ≡ 1 (mod 3) => root ≡ 1 (mod 3): fertile
    q ≡ 2 (mod 3) => root ≡ 2 (mod 3): fertile
    => 2/3 fertile, 1/3 infertile

  Both cases: exactly 2/3 of root preimages are fertile!
  => The root-only branching factor is 2/3.
  => The root-only tree should shrink (< 1), NOT grow.
""")

# But the FULL tree also has the 4n+1 chain contributions!
# Each existing preimage n generates 4n+1 as an additional preimage.
# So effective branching = root_branching + chain_extension_branching

# Let me think about this more carefully for the FULL BFS tree.
print("Part G: Full BFS effective branching")
print("=" * 70)

# In the full BFS tree (with all preimages, no upper bound):
# At level k, each node m has:
#   - 1 root preimage (if m mod 3 != 0), at level k+1
#   - For each n at level k+1 with T(n) = m, 4n+1 is ALSO at level k+1
#     But 4n+1 is an "extension" of n, not a new root.

# The total number of preimages of m within [1, N] is approximately:
# floor(log_4(3N/D(m))) + 1 ≈ log_4(N) / 2

# BUT for the BFS tree, we count each n exactly once (at the first level it appears).
# Since the 4n+1 chain produces n, 4n+1, 16n+5, 64n+21, ...,
# ALL of these are preimages of the SAME m.
# In a BFS from 1, these all appear at the SAME level.

# So at each BFS level:
# New root preimages + all their 4n+1 chain extensions up to bound N.

# The number of chain extensions of root r within [1,N] is approximately:
# floor(log_4(N/r))

# For the BFS tree with bound N:
# |T^{-k}(1) ∩ [1,N]| ≈ (# root preimages at level k) * average_chain_length(k)
# where average_chain_length depends on the typical size of roots at level k.

# What's the typical size of a root at level k?
# root(m) ≈ m * 2^{j_min} / 3 ≈ 4m/3 or 2m/3
# So root is roughly proportional to m.

# At level k, the typical node size is roughly ... let's compute

print("\n  Average and median of log2(n) for nodes at each BFS level:")
import statistics

for k in range(min(20, len(true_levels))):
    if len(true_levels[k]) > 0:
        log_vals = [math.log2(n) for n in true_levels[k] if n > 0]
        if log_vals:
            avg = statistics.mean(log_vals)
            med = statistics.median(log_vals)
            print(f"    k={k:3d}: avg_log2 = {avg:.2f}, median_log2 = {med:.2f}, "
                  f"min_log2 = {min(log_vals):.2f}, max_log2 = {max(log_vals):.2f}")
