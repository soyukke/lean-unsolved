#!/usr/bin/env python3
"""
Collatz delay records analysis.
- Delay record: n where stopping time exceeds all previous values
- Growth rates, binary structure, Mersenne relationships, mod patterns
- Glide records: n where steps to reach max value is largest so far
"""

import math
from collections import defaultdict

N_MAX = 10_000_000

def stopping_time(n):
    """Steps to reach 1 from n."""
    steps = 0
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        steps += 1
    return steps

def glide_info(n):
    """Return (steps_to_max, max_value) for the trajectory of n."""
    x = n
    mx = n
    step_at_max = 0
    steps = 0
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        steps += 1
        if x > mx:
            mx = x
            step_at_max = steps
    return step_at_max, mx

def main():
    print("=" * 70)
    print("Collatz Delay Records Analysis (n = 1..10^7)")
    print("=" * 70)

    # --- Phase 1: Compute delay records ---
    print("\n[Phase 1] Computing delay records...")
    delay_records = []  # (n, stopping_time)
    max_st = -1

    for n in range(1, N_MAX + 1):
        st = stopping_time(n)
        if st > max_st:
            max_st = st
            delay_records.append((n, st))

    print(f"Found {len(delay_records)} delay records up to {N_MAX}")

    # Print delay records
    print(f"\n{'k':>4} {'n':>12} {'stop_time':>10} {'n ratio':>10} {'st ratio':>10} {'bin(n)':>30}")
    print("-" * 80)
    for i, (n, st) in enumerate(delay_records):
        if i == 0 or delay_records[i - 1][1] == 0:
            n_ratio = "-"
            st_ratio = "-"
        else:
            prev_n, prev_st = delay_records[i - 1]
            n_ratio = f"{n / prev_n:.4f}"
            st_ratio = f"{st / prev_st:.4f}"
        bstr = bin(n)[2:]
        if len(bstr) > 28:
            bstr = bstr[:14] + ".." + bstr[-14:]
        print(f"{i:>4} {n:>12} {st:>10} {n_ratio:>10} {st_ratio:>10} {bstr:>30}")

    # --- Phase 2: Growth rate analysis ---
    print("\n" + "=" * 70)
    print("[Phase 2] Growth rate analysis")
    print("=" * 70)

    # Ratio r_{k+1}/r_k statistics
    n_ratios = []
    st_ratios = []
    for i in range(1, len(delay_records)):
        if delay_records[i - 1][0] > 0 and delay_records[i - 1][1] > 0:
            n_ratios.append(delay_records[i][0] / delay_records[i - 1][0])
            st_ratios.append(delay_records[i][1] / delay_records[i - 1][1])

    print(f"\nn-ratio (r_{{k+1}}/r_k): mean={sum(n_ratios)/len(n_ratios):.4f}, "
          f"median={sorted(n_ratios)[len(n_ratios)//2]:.4f}, "
          f"min={min(n_ratios):.4f}, max={max(n_ratios):.4f}")
    print(f"st-ratio (s_{{k+1}}/s_k): mean={sum(st_ratios)/len(st_ratios):.4f}, "
          f"median={sorted(st_ratios)[len(st_ratios)//2]:.4f}, "
          f"min={min(st_ratios):.4f}, max={max(st_ratios):.4f}")

    # Fit r_k ~ C * alpha^k
    print("\n--- Exponential fit: r_k ~ C * alpha^k ---")
    log_ns = [math.log(n) for n, _ in delay_records if n > 0]
    ks = list(range(len(log_ns)))
    # Linear regression: log(r_k) = log(C) + k * log(alpha)
    n_pts = len(ks)
    sum_k = sum(ks)
    sum_logn = sum(log_ns)
    sum_k2 = sum(k * k for k in ks)
    sum_k_logn = sum(k * ln for k, ln in zip(ks, log_ns))
    denom = n_pts * sum_k2 - sum_k * sum_k
    log_alpha = (n_pts * sum_k_logn - sum_k * sum_logn) / denom
    log_C = (sum_logn - log_alpha * sum_k) / n_pts
    alpha = math.exp(log_alpha)
    C = math.exp(log_C)
    print(f"  r_k ≈ {C:.4f} * {alpha:.6f}^k")
    print(f"  alpha = {alpha:.6f} (compare: 2^(1/1) = 2.0, 3^(1/2) = {3**0.5:.6f})")

    # --- Phase 3: Binary representation features ---
    print("\n" + "=" * 70)
    print("[Phase 3] Binary representation features")
    print("=" * 70)

    print(f"\n{'k':>4} {'n':>12} {'bits':>6} {'1-bits':>7} {'1-density':>10} {'trailing 1s':>12} {'form':>20}")
    print("-" * 80)
    for i, (n, st) in enumerate(delay_records):
        bits = n.bit_length()
        ones = bin(n).count('1')
        density = ones / bits if bits > 0 else 0
        # Trailing 1s
        t1 = 0
        x = n
        while x & 1:
            t1 += 1
            x >>= 1
        # Check specific forms
        form = ""
        if n == (1 << bits) - 1:
            form = f"2^{bits}-1 (Mersenne)"
        elif n & (n + 1) == 0:
            form = f"2^{bits}-1 (all 1s)"
        elif bin(n).count('1') <= 3:
            form = f"sparse ({ones} ones)"
        print(f"{i:>4} {n:>12} {bits:>6} {ones:>7} {density:>10.4f} {t1:>12} {form:>20}")

    # --- Phase 4: Mersenne number relationship ---
    print("\n" + "=" * 70)
    print("[Phase 4] Mersenne number relationship")
    print("=" * 70)

    mersenne = [(k, (1 << k) - 1) for k in range(1, 25)]
    delay_set = set(n for n, _ in delay_records)

    print("\nMersenne numbers that are delay records:")
    for k, m in mersenne:
        if m in delay_set:
            st = stopping_time(m)
            print(f"  2^{k}-1 = {m}, stopping time = {st}")

    print("\nDelay records near Mersenne numbers (|n - 2^k+1| <= 5):")
    for n, st in delay_records:
        bits = n.bit_length()
        mersenne_val = (1 << bits) - 1
        diff = n - mersenne_val
        if abs(diff) <= 5 and diff != 0:
            print(f"  n={n}, 2^{bits}-1={mersenne_val}, diff={diff}, stop_time={st}")

    # Fraction of delay records that are 2^k-1
    mersenne_count = sum(1 for n, _ in delay_records if n & (n + 1) == 0)
    print(f"\nDelay records that are Mersenne-form (2^k-1): {mersenne_count}/{len(delay_records)} "
          f"({100*mersenne_count/len(delay_records):.1f}%)")

    # --- Phase 5: Mod patterns ---
    print("\n" + "=" * 70)
    print("[Phase 5] Mod patterns of delay records")
    print("=" * 70)

    for mod in [2, 3, 4, 6, 8, 9, 12, 16]:
        counts = defaultdict(int)
        for n, _ in delay_records:
            counts[n % mod] += 1
        total = len(delay_records)
        dist = ", ".join(f"{r}:{c}({100*c/total:.0f}%)" for r, c in sorted(counts.items()))
        print(f"  mod {mod:>2}: {dist}")

    # --- Phase 6: Glide records ---
    print("\n" + "=" * 70)
    print("[Phase 6] Glide records (steps to max)")
    print("=" * 70)
    print("Computing glide records (may take a while)...")

    glide_records = []
    max_glide = -1
    # Only compute for a smaller range for glide (more expensive)
    GLIDE_MAX = 1_000_000
    for n in range(2, GLIDE_MAX + 1):
        g, mx = glide_info(n)
        if g > max_glide:
            max_glide = g
            glide_records.append((n, g, mx))

    print(f"Found {len(glide_records)} glide records up to {GLIDE_MAX}")
    print(f"\n{'k':>4} {'n':>12} {'glide_steps':>12} {'max_value':>20} {'n ratio':>10}")
    print("-" * 65)
    for i, (n, g, mx) in enumerate(glide_records):
        if i == 0:
            n_ratio = "-"
        else:
            n_ratio = f"{n / glide_records[i-1][0]:.4f}"
        print(f"{i:>4} {n:>12} {g:>12} {mx:>20} {n_ratio:>10}")

    # Overlap between delay and glide records
    delay_ns = set(n for n, _ in delay_records)
    glide_ns = set(n for n, _, _ in glide_records)
    overlap = delay_ns & glide_ns
    print(f"\nOverlap (delay ∩ glide records up to {GLIDE_MAX}): {len(overlap)} numbers")
    if overlap:
        print(f"  Overlapping: {sorted(overlap)[:30]}...")

    # --- Phase 7: Stopping time vs log(n) ---
    print("\n" + "=" * 70)
    print("[Phase 7] Stopping time scaling: s_k vs log(r_k)")
    print("=" * 70)

    print(f"\n{'k':>4} {'n':>12} {'stop_time':>10} {'log2(n)':>10} {'st/log2(n)':>12}")
    print("-" * 55)
    for i, (n, st) in enumerate(delay_records):
        if n <= 1:
            continue
        l2 = math.log2(n)
        ratio = st / l2
        print(f"{i:>4} {n:>12} {st:>10} {l2:>10.3f} {ratio:>12.4f}")

    # Average ratio
    ratios_log = [st / math.log2(n) for n, st in delay_records if n > 1]
    print(f"\nMean(st/log2(n)) = {sum(ratios_log)/len(ratios_log):.4f}")
    print(f"Trend: last 20 values mean = {sum(ratios_log[-20:])/20:.4f}")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total delay records (1..10^7): {len(delay_records)}")
    print(f"Largest delay record: n={delay_records[-1][0]}, stopping time={delay_records[-1][1]}")
    print(f"Growth fit: r_k ≈ {C:.3f} * {alpha:.4f}^k")
    print(f"Mersenne-form delay records: {mersenne_count}/{len(delay_records)}")
    print(f"Mean st/log2(n) ratio: {sum(ratios_log)/len(ratios_log):.4f}")
    print(f"Glide records (1..10^6): {len(glide_records)}")

if __name__ == "__main__":
    main()
