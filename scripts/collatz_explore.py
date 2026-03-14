"""
Collatz conjecture exploration script.
Computes stopping times, Syracuse function, pattern analysis, and visualizations.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

# ============================================================
# 1. Standard Collatz stopping time
# ============================================================

def collatz_stopping_time(n):
    """Return (stopping_time, trajectory_max) for the standard Collatz sequence."""
    steps = 0
    traj_max = n
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        traj_max = max(traj_max, x)
        steps += 1
    return steps, traj_max


def v2(n):
    """2-adic valuation of n (largest k such that 2^k divides n)."""
    if n == 0:
        return float("inf")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


# ============================================================
# 2. Syracuse function stopping time (odd-only tracking)
# ============================================================

def syracuse_step(n):
    """T(n) = (3n+1) / 2^v2(3n+1) for odd n."""
    val = 3 * n + 1
    return val >> v2(val)


def syracuse_stopping_time(n):
    """Stopping time using only odd iterates via the Syracuse function."""
    if n == 1:
        return 0
    steps = 0
    x = n
    while x != 1:
        x = syracuse_step(x)
        steps += 1
    return steps


# ============================================================
# Compute data for n = 1..1000
# ============================================================

N = 1000

stopping_times = {}
traj_maxima = {}
for n in range(1, N + 1):
    st, tm = collatz_stopping_time(n)
    stopping_times[n] = st
    traj_maxima[n] = tm

syracuse_times = {}
for n in range(1, N + 1, 2):  # odd only
    syracuse_times[n] = syracuse_stopping_time(n)

# ============================================================
# 3. Pattern analysis
# ============================================================

print("=" * 60)
print("COLLATZ EXPLORATION  n = 1 .. 1000")
print("=" * 60)

# --- Top 10 stopping times ---
top_st = sorted(stopping_times.items(), key=lambda x: -x[1])[:10]
print("\n[1] Top 10 stopping times (standard Collatz):")
for rank, (n, st) in enumerate(top_st, 1):
    print(f"  {rank:2d}. n={n:4d}  stopping_time={st}")

# --- Top 10 Syracuse stopping times ---
top_syr = sorted(syracuse_times.items(), key=lambda x: -x[1])[:10]
print("\n[2] Top 10 Syracuse stopping times (odd-only):")
for rank, (n, st) in enumerate(top_syr, 1):
    print(f"  {rank:2d}. n={n:4d}  syracuse_stopping_time={st}")

# --- Top 10 trajectory maxima ---
top_tm = sorted(traj_maxima.items(), key=lambda x: -x[1])[:10]
print("\n[3] Top 10 trajectory maxima:")
for rank, (n, tm) in enumerate(top_tm, 1):
    print(f"  {rank:2d}. n={n:4d}  trajectory_max={tm}")

# --- Mod analysis ---
print("\n[4] Average stopping time by residue class:")
for mod in [2, 3, 6, 12]:
    buckets = defaultdict(list)
    for n in range(1, N + 1):
        buckets[n % mod].append(stopping_times[n])
    print(f"\n  mod {mod}:")
    for r in sorted(buckets):
        vals = buckets[r]
        avg = sum(vals) / len(vals)
        print(f"    r={r:2d}  count={len(vals):4d}  avg_stopping_time={avg:.2f}  max={max(vals)}")

# --- v2(3n+1) distribution for odd n ---
v2_counts = defaultdict(int)
v2_values = []
odd_ns = list(range(1, N + 1, 2))
for n in odd_ns:
    val = v2(3 * n + 1)
    v2_counts[val] += 1
    v2_values.append(val)

print("\n[5] Distribution of v2(3n+1) for odd n in [1, 999]:")
for k in sorted(v2_counts):
    cnt = v2_counts[k]
    frac = cnt / len(odd_ns)
    expected = 1 / (2 ** k) if k < 10 else "~0"
    print(f"    v2={k:2d}  count={cnt:4d}  freq={frac:.4f}  (expected ~{expected})")

# ============================================================
# 4. Visualization
# ============================================================

# --- Scatter: n vs stopping time ---
ns = list(range(1, N + 1))
sts = [stopping_times[n] for n in ns]

fig, ax = plt.subplots(figsize=(12, 5))
ax.scatter(ns, sts, s=2, alpha=0.6, color="steelblue")
ax.set_xlabel("n")
ax.set_ylabel("Stopping time")
ax.set_title("Collatz stopping time for n = 1..1000")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("/Users/soyukke/study/lean-unsolved/scripts/collatz_stopping_time.png", dpi=150)
print("\nSaved: collatz_stopping_time.png")

# --- Histogram: v2(3n+1) ---
fig2, ax2 = plt.subplots(figsize=(8, 5))
max_v2 = max(v2_values)
ax2.bar(range(1, max_v2 + 1),
        [v2_counts.get(k, 0) for k in range(1, max_v2 + 1)],
        color="coral", edgecolor="darkred", alpha=0.8)
ax2.set_xlabel("v2(3n+1)")
ax2.set_ylabel("Count")
ax2.set_title("Distribution of v2(3n+1) for odd n in [1, 999]")
ax2.grid(True, alpha=0.3, axis="y")
fig2.tight_layout()
fig2.savefig("/Users/soyukke/study/lean-unsolved/scripts/v2_distribution.png", dpi=150)
print("Saved: v2_distribution.png")

print("\nDone.")
