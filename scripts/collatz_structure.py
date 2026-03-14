"""
Collatz Phase 3: Structure Discovery
Fiber decomposition, inverse Collatz tree, ascent/descent patterns, 2-adic structure.
Uses only Python standard library.
"""

from collections import defaultdict
import math

SCRIPT_DIR = "/Users/soyukke/study/lean-unsolved/scripts"

# ============================================================
# Helper functions
# ============================================================

def v2(n):
    """2-adic valuation of n."""
    if n == 0:
        return float("inf")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^v2(3n+1) for odd n."""
    val = 3 * n + 1
    return val >> v2(val)


def syracuse_sequence(n, max_steps=500):
    """Return Syracuse sequence starting from odd n, stopping at 1."""
    seq = [n]
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x = syracuse(x)
        seq.append(x)
    return seq


def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0


# ============================================================
# 1. Fiber Decomposition (mod m analysis)
# ============================================================

print("=" * 70)
print("PHASE 3: STRUCTURE DISCOVERY")
print("=" * 70)

print("\n" + "=" * 70)
print("1. FIBER DECOMPOSITION (mod m)")
print("=" * 70)

N = 10000

for mod in [4, 8, 16, 32]:
    print(f"\n--- Syracuse T(n) behavior for n mod {mod} (odd n in [1, {N}]) ---")
    residue_data = defaultdict(lambda: defaultdict(int))
    residue_counts = defaultdict(int)

    for n in range(1, N + 1, 2):
        r = n % mod
        t = syracuse(n)
        residue_data[r][t % mod] += 1
        residue_counts[r] += 1

    for r in sorted(residue_data.keys()):
        total = residue_counts[r]
        dist = residue_data[r]
        top = sorted(dist.items(), key=lambda x: -x[1])[:5]
        top_str = ", ".join(f"{val}:{cnt}/{total}" for val, cnt in top)
        print(f"  n={r:2d} (mod {mod}): T(n) mod {mod} -> [{top_str}]")

# --- mod 4 detailed: trajectory structure comparison ---
print(f"\n--- n = 1 (mod 4) vs n = 3 (mod 4): trajectory comparison ---")
for residue in [1, 3]:
    ns = [n for n in range(residue, 2001, 4)]
    avg_steps = []
    avg_first_drop = []
    for n in ns:
        seq = syracuse_sequence(n)
        avg_steps.append(len(seq) - 1)
        drop = 0
        for i, x in enumerate(seq[1:], 1):
            if x < n:
                drop = i
                break
        avg_first_drop.append(drop)

    print(f"  n = {residue} (mod 4): count={len(ns)}, "
          f"avg_syracuse_steps={mean(avg_steps):.2f}, "
          f"avg_first_drop_below_n={mean(avg_first_drop):.2f}")

# --- Deterministic v2 from residue class ---
print(f"\n--- v2(3n+1) is determined by n mod 2^k ---")
for bits in range(1, 7):
    mod = 2 ** bits
    v2_by_residue = defaultdict(set)
    for n in range(1, 10001, 2):
        r = n % mod
        v2_by_residue[r].add(v2(3 * n + 1))
    determined = sum(1 for r in v2_by_residue if len(v2_by_residue[r]) == 1)
    total = len(v2_by_residue)
    print(f"  mod {mod:4d}: {determined}/{total} residue classes have fixed v2 "
          f"({'YES all determined' if determined == total else 'partial'})")
    if bits <= 4:
        for r in sorted(v2_by_residue.keys()):
            vals = sorted(v2_by_residue[r])
            if len(vals) <= 3:
                print(f"    n={r} (mod {mod}): v2 = {vals}")
            else:
                print(f"    n={r} (mod {mod}): v2 in {vals[:5]}...")


# ============================================================
# 2. Inverse Collatz Tree
# ============================================================

print("\n" + "=" * 70)
print("2. INVERSE COLLATZ TREE (depth 10 from root=1)")
print("=" * 70)

def inverse_collatz_children(n):
    """Return all predecessors of n in the Collatz graph."""
    children = []
    # Even route: 2n always leads to n
    children.append(2 * n)
    # Odd route: m = (2^k * n - 1) / 3 for each k where result is integer and odd
    for k in range(1, 40):
        val = (2**k) * n - 1
        if val % 3 == 0:
            m = val // 3
            if m > 0 and m % 2 == 1 and m != n:
                children.append(m)
    return children

# BFS from 1
tree_levels = {0: {1}}
all_nodes = {1}
for depth in range(1, 11):
    new_nodes = set()
    for node in tree_levels[depth - 1]:
        for child in inverse_collatz_children(node):
            if child not in all_nodes and child <= 10**8:
                new_nodes.add(child)
                all_nodes.add(child)
    tree_levels[depth] = new_nodes

print(f"\n  {'Depth':>6}  {'Nodes at depth':>15}  {'Cumulative':>12}  {'Growth rate':>12}")
print(f"  {'-'*6}  {'-'*15}  {'-'*12}  {'-'*12}")
cumulative = 0
prev = 1
for d in range(0, 11):
    cnt = len(tree_levels[d])
    cumulative += cnt
    rate = cnt / prev if prev > 0 else 0
    print(f"  {d:6d}  {cnt:15d}  {cumulative:12d}  {rate:12.2f}")
    prev = cnt

# Sample nodes at each depth
print("\n  Sample nodes at each depth:")
for d in range(0, 11):
    sample = sorted(tree_levels[d])[:10]
    print(f"    depth {d:2d}: {sample}{'...' if len(tree_levels[d]) > 10 else ''}")


# ============================================================
# 3. Ascent / Descent Patterns
# ============================================================

print("\n" + "=" * 70)
print("3. SYRACUSE ASCENT / DESCENT PATTERNS")
print("=" * 70)

N_ANALYSIS = 10000
ascent_counts = []
descent_counts = []
max_consecutive_ascents = []
first_drop_steps = []
odd_ns = list(range(3, N_ANALYSIS + 1, 2))

for n in odd_ns:
    seq = syracuse_sequence(n)
    asc = 0
    desc = 0
    max_cons_asc = 0
    cur_cons_asc = 0
    first_drop = len(seq)

    for i in range(1, len(seq)):
        if seq[i] > seq[i - 1]:
            asc += 1
            cur_cons_asc += 1
            max_cons_asc = max(max_cons_asc, cur_cons_asc)
        else:
            desc += 1
            cur_cons_asc = 0

        if seq[i] < n and first_drop == len(seq):
            first_drop = i

    total = asc + desc
    ascent_counts.append(asc / total if total > 0 else 0)
    descent_counts.append(desc / total if total > 0 else 0)
    max_consecutive_ascents.append(max_cons_asc)
    first_drop_steps.append(first_drop)

print(f"\n  Analysis of odd n in [3, {N_ANALYSIS}]:")
print(f"  Average ascent fraction:        {mean(ascent_counts):.4f}")
print(f"  Average descent fraction:       {mean(descent_counts):.4f}")
print(f"  Average max consecutive ascent: {mean(max_consecutive_ascents):.2f}")
print(f"  Max of max consecutive ascent:  {max(max_consecutive_ascents)}")
print(f"  Average first-drop-below-n:     {mean(first_drop_steps):.2f}")
print(f"  Max first-drop-below-n:         {max(first_drop_steps)}")

# Top 10 hardest to drop below themselves
drop_data = list(zip(odd_ns, first_drop_steps))
drop_data.sort(key=lambda x: -x[1])
print(f"\n  Top 10 longest first-drop-below-n:")
for rank, (n, steps) in enumerate(drop_data[:10], 1):
    print(f"    {rank:2d}. n={n:6d}  steps_to_drop={steps}")

# Ascent fraction histogram (text-based)
print(f"\n  Ascent fraction distribution (binned):")
bins = [0, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 1.0]
hist = [0] * (len(bins) - 1)
for v in ascent_counts:
    for i in range(len(bins) - 1):
        if bins[i] <= v < bins[i + 1]:
            hist[i] += 1
            break
for i in range(len(bins) - 1):
    bar = "#" * (hist[i] // 20)
    print(f"    [{bins[i]:.2f}, {bins[i+1]:.2f}): {hist[i]:5d}  {bar}")


# ============================================================
# 4. 2-adic Structure
# ============================================================

print("\n" + "=" * 70)
print("4. 2-ADIC STRUCTURE")
print("=" * 70)

# --- Tail bit pattern vs v2(3n+1) ---
print("\n--- Tail bit patterns and v2(3n+1) ---")
print(f"  {'Tail bits':>12}  {'Pattern':>10}  {'v2(3n+1)':>10}  {'Verified':>10}")
print(f"  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*10}")

for num_bits in range(1, 8):
    for pattern in range(2**num_bits):
        if pattern % 2 == 0:
            continue  # only odd numbers
        # Check if this pattern determines v2
        v2_vals = set()
        for n in range(pattern, 10001, 2**num_bits):
            if n > 0:
                v2_vals.add(v2(3 * n + 1))
        if len(v2_vals) == 1:
            v2_val = v2_vals.pop()
            binary = format(pattern, f'0{num_bits}b')
            # Verify with a larger range
            verify_vals = set()
            for n in range(pattern, 50001, 2**num_bits):
                if n > 0:
                    verify_vals.add(v2(3 * n + 1))
            verified = "YES" if len(verify_vals) == 1 else "NO"
            if num_bits <= 5:
                print(f"  ...{binary:>8s}  {pattern:10d}  {v2_val:10d}  {verified:>10s}")

# --- Binary representation vs stopping time ---
print(f"\n--- Binary features vs stopping time ---")

def count_ones(n):
    return bin(n).count('1')

def trailing_ones(n):
    k = 0
    while n & 1:
        n >>= 1
        k += 1
    return k

odd_data = []
for n in range(1, N_ANALYSIS + 1, 2):
    seq = syracuse_sequence(n)
    st = len(seq) - 1
    ones = count_ones(n)
    bit_len = n.bit_length()
    trail = trailing_ones(n)
    odd_data.append((n, st, ones, bit_len, trail))

# Group by trailing ones
print(f"\n  Stopping time by number of trailing 1-bits:")
trail_groups = defaultdict(list)
for n, st, ones, bit_len, trail in odd_data:
    trail_groups[trail].append(st)

for t in sorted(trail_groups.keys()):
    vals = trail_groups[t]
    if len(vals) >= 5:
        print(f"    trailing 1s = {t}: count={len(vals):5d}, "
              f"avg_steps={mean(vals):8.2f}, max={max(vals):5d}")

# Group by bit density
print(f"\n  Stopping time by bit density (popcount / bit_length):")
density_groups = defaultdict(list)
for n, st, ones, bit_len, trail in odd_data:
    bucket = round(ones / bit_len, 1)
    density_groups[bucket].append(st)

for d in sorted(density_groups.keys()):
    vals = density_groups[d]
    if len(vals) >= 10:
        print(f"    density ~{d:.1f}: count={len(vals):5d}, "
              f"avg_steps={mean(vals):8.2f}, max={max(vals):5d}")

# --- v2 coverage table ---
print(f"\n--- Compact v2(3n+1) table: tail bits that deterministically fix v2 ---")
print(f"\n  {'Bits':>4}  {'# determined':>14}  {'# total odd':>12}  {'Coverage':>10}")
for num_bits in range(1, 9):
    mod = 2 ** num_bits
    determined = 0
    total_odd = 0
    for pattern in range(mod):
        if pattern % 2 == 0:
            continue
        total_odd += 1
        v2_vals = set()
        for n in range(pattern, 10001, mod):
            if n > 0:
                v2_vals.add(v2(3 * n + 1))
        if len(v2_vals) == 1:
            determined += 1
    coverage = determined / total_odd if total_odd > 0 else 0
    print(f"  {num_bits:4d}  {determined:14d}  {total_odd:12d}  {coverage:10.4f}")


# ============================================================
# 5. SVG Visualizations (no external dependencies)
# ============================================================

print("\n" + "=" * 70)
print("5. GENERATING SVG VISUALIZATIONS")
print("=" * 70)


def make_svg_scatter(filename, title, xs, ys, width=800, height=400,
                     xlabel="x", ylabel="y", color="steelblue", point_size=2):
    """Create a simple SVG scatter plot."""
    margin = 60
    pw = width - 2 * margin
    ph = height - 2 * margin

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_range = x_max - x_min or 1
    y_range = y_max - y_min or 1

    points = []
    # Sample if too many points
    step = max(1, len(xs) // 2000)
    for i in range(0, len(xs), step):
        px = margin + (xs[i] - x_min) / x_range * pw
        py = height - margin - (ys[i] - y_min) / y_range * ph
        points.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{point_size}" '
                      f'fill="{color}" opacity="0.4"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width//2}" y="20" text-anchor="middle" font-size="14" font-weight="bold">{title}</text>
  <text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="11">{xlabel}</text>
  <text x="12" y="{height//2}" text-anchor="middle" font-size="11" transform="rotate(-90,12,{height//2})">{ylabel}</text>
  <line x1="{margin}" y1="{height-margin}" x2="{margin+pw}" y2="{height-margin}" stroke="black"/>
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black"/>
  {"".join(points)}
</svg>'''

    with open(filename, 'w') as f:
        f.write(svg)


def make_svg_bar(filename, title, labels, values, width=600, height=400,
                 xlabel="x", ylabel="y", color="mediumpurple"):
    """Create a simple SVG bar chart."""
    margin = 60
    pw = width - 2 * margin
    ph = height - 2 * margin

    n = len(labels)
    if n == 0:
        return
    bar_w = pw / n * 0.8
    gap = pw / n * 0.2
    y_max = max(values) if values else 1

    bars = []
    for i, (label, val) in enumerate(zip(labels, values)):
        x = margin + i * (bar_w + gap)
        h = val / y_max * ph
        y = height - margin - h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
                    f'fill="{color}" stroke="black" stroke-width="0.5"/>')
        bars.append(f'<text x="{x + bar_w/2:.1f}" y="{height-margin+15}" '
                    f'text-anchor="middle" font-size="9">{label}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width//2}" y="20" text-anchor="middle" font-size="14" font-weight="bold">{title}</text>
  <text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="11">{xlabel}</text>
  <line x1="{margin}" y1="{height-margin}" x2="{margin+pw}" y2="{height-margin}" stroke="black"/>
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black"/>
  {"".join(bars)}
</svg>'''

    with open(filename, 'w') as f:
        f.write(svg)


# Fig 1: First-drop-below-n scatter
make_svg_scatter(
    f"{SCRIPT_DIR}/first_drop_scatter.svg",
    "Steps to first drop below n (Syracuse)",
    odd_ns, first_drop_steps,
    xlabel="n (odd)", ylabel="Steps to first drop below n",
    color="coral"
)
print("  Saved: first_drop_scatter.svg")

# Fig 2: Inverse tree growth
depths_list = list(range(0, 11))
counts_list = [len(tree_levels[d]) for d in depths_list]
make_svg_bar(
    f"{SCRIPT_DIR}/inverse_tree_growth.svg",
    "Inverse Collatz Tree: Nodes at Each Depth",
    [str(d) for d in depths_list], [math.log10(c + 1) for c in counts_list],
    xlabel="Depth", ylabel="log10(nodes)", color="royalblue"
)
print("  Saved: inverse_tree_growth.svg")

# Fig 3: Stopping time by trailing 1-bits
trail_keys_filtered = [t for t in sorted(trail_groups.keys()) if len(trail_groups[t]) >= 5]
trail_means = [mean(trail_groups[t]) for t in trail_keys_filtered]
make_svg_bar(
    f"{SCRIPT_DIR}/trailing_ones_vs_stopping.svg",
    "Avg Syracuse Stopping Time by Trailing 1-bits",
    [str(t) for t in trail_keys_filtered], trail_means,
    xlabel="Trailing 1-bits", ylabel="Avg stopping time", color="mediumpurple"
)
print("  Saved: trailing_ones_vs_stopping.svg")

# Fig 4: Max consecutive ascent scatter
make_svg_scatter(
    f"{SCRIPT_DIR}/max_consecutive_ascent.svg",
    "Max Consecutive Ascent in Syracuse Sequence",
    odd_ns, max_consecutive_ascents,
    xlabel="n (odd)", ylabel="Max consecutive ascents",
    color="forestgreen"
)
print("  Saved: max_consecutive_ascent.svg")

print("\n" + "=" * 70)
print("PHASE 3 COMPLETE")
print("=" * 70)
