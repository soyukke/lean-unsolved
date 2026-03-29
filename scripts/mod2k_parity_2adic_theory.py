"""
mod 2^k 非排除残基の偶奇振動パターンの2-adic理論的解析

目的:
1. N(k) の偶奇パターンを精密に調べる
2. 偶奇振動の2-adic valuation的な説明を探る
3. N(k) mod 2, mod 4, mod 8 の振る舞いを解析
4. 漸化式的構造（N(k+1) と N(k) の関係）を調べる
"""

import json
import math
from collections import Counter, defaultdict

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)}"""
    m = 3 * n + 1
    return m >> v2(m)

def steps_to_descend(n, mod):
    """
    Given odd residue n mod 2^k, compute Syracuse iterates mod 2^k.
    Return number of steps until value < n (deterministic descent).
    Returns None if no descent within max_steps.
    """
    current = n
    for step in range(1, 100):
        m = 3 * current + 1
        v = v2(m)
        if v >= mod.bit_length() - 1:
            # Cannot determine next step mod 2^k
            return None
        current = (m >> v) % mod
        if current == 0:
            current = mod  # wrap
        if current < n:
            return step
    return None

def compute_non_excluded(k, max_steps=None):
    """
    Compute non-excluded odd residues mod 2^k.
    A residue r is 'excluded' if Syracuse iteration deterministically
    brings it below r within a bounded number of steps (determined mod 2^k).

    More precisely: r is excluded if T^s(r) mod 2^k < r for some s <= threshold,
    AND this is deterministic (v2 values at each step are < k).
    """
    if max_steps is None:
        max_steps = k  # Use k steps as threshold

    mod = 1 << k
    non_excluded = []

    for r in range(1, mod, 2):  # odd residues
        current = r
        excluded = False
        for step in range(1, max_steps + 1):
            m = 3 * current + 1
            v = v2(m)
            if v >= k:
                # v2 >= k means we lose all info mod 2^k: non-deterministic
                break
            current = (m >> v) % mod
            if current < r:
                excluded = True
                break
        if not excluded:
            non_excluded.append(r)

    return non_excluded

print("=" * 70)
print("Part 1: N(k) 系列の精密計算と偶奇振動")
print("=" * 70)

nk_data = {}
for k in range(2, 22):
    residues = compute_non_excluded(k)
    n = len(residues)
    nk_data[k] = {
        'count': n,
        'parity': n % 2,
        'mod4': n % 4,
        'mod8': n % 8,
        'v2_nk': v2(n) if n > 0 else 'inf',
        'residues': residues if k <= 10 else None
    }
    parity_str = "even" if n % 2 == 0 else "odd"
    print(f"k={k:2d}: N(k)={n:6d}  ({parity_str})  mod4={n%4}  mod8={n%8}  v2(N(k))={v2(n) if n > 0 else 'inf'}")

print("\n" + "=" * 70)
print("Part 2: 偶奇振動パターンの解析")
print("=" * 70)

# Extract parity sequence
parities = [nk_data[k]['parity'] for k in range(2, 22)]
counts = [nk_data[k]['count'] for k in range(2, 22)]
ks = list(range(2, 22))

print(f"\nk values:    {ks}")
print(f"N(k) values: {counts}")
print(f"Parities:    {parities}")

# Check for periodic patterns
print("\nParity sequence (E=even, O=odd):")
seq = ''.join(['E' if p == 0 else 'O' for p in parities])
print(f"  {seq}")

# Check period-2, period-3, period-4 patterns
for period in range(2, 8):
    is_periodic = True
    for i in range(period, len(parities)):
        if parities[i] != parities[i % period]:
            is_periodic = False
            break
    if is_periodic:
        print(f"  Period-{period} detected!")

# Look at differences and ratios
print("\n" + "=" * 70)
print("Part 3: N(k+1) / N(k) 比と N(k+1) - 2*N(k) の解析")
print("=" * 70)

for k in range(3, min(22, max(nk_data.keys()))):
    if k-1 in nk_data and k in nk_data:
        nk = nk_data[k]['count']
        nk_prev = nk_data[k-1]['count']
        ratio = nk / nk_prev if nk_prev > 0 else 'inf'
        diff = nk - 2 * nk_prev
        excess = nk - 2 * nk_prev  # How many more/fewer than doubling
        print(f"k={k:2d}: N(k)={nk:6d}, N(k-1)={nk_prev:5d}, "
              f"ratio={ratio:.4f}, N(k)-2*N(k-1)={diff:6d}, "
              f"v2(|diff|)={v2(abs(diff)) if diff != 0 else 'inf'}")

print("\n" + "=" * 70)
print("Part 4: 2-adic構造 -- trailing 1s の分布と排除メカニズム")
print("=" * 70)

# For each k, analyze how residues get excluded going from k to k+1
for k in range(4, min(17, max(nk_data.keys()))):
    res_k = set(compute_non_excluded(k))
    res_k1 = set(compute_non_excluded(k + 1))
    mod_k = 1 << k
    mod_k1 = 1 << (k + 1)

    # Each residue r mod 2^k lifts to r and r + 2^k mod 2^{k+1}
    # Count: how many lifts survive vs get excluded
    survived_both = 0
    survived_low = 0  # only r survives
    survived_high = 0  # only r + 2^k survives
    excluded_both = 0

    for r in range(1, mod_k, 2):
        low_in = r in res_k1
        high_in = (r + mod_k) in res_k1

        if r in res_k:
            if low_in and high_in:
                survived_both += 1
            elif low_in:
                survived_low += 1
            elif high_in:
                survived_high += 1
            else:
                excluded_both += 1
        # Note: if r not in res_k, both lifts should not be in res_k1

    nk = len(res_k)
    nk1 = len(res_k1)
    print(f"k={k:2d}->k+1: N(k)={nk:4d}, N(k+1)={nk1:5d}  "
          f"both_survive={survived_both:4d}, low_only={survived_low:3d}, "
          f"high_only={survived_high:3d}, both_excl={excluded_both:3d}  "
          f"[expected: 2*{nk}-{nk1}={2*nk-nk1} newly excluded]")

print("\n" + "=" * 70)
print("Part 5: N(k) の v2 値パターンと2-adic理論")
print("=" * 70)

# v2(N(k)) pattern
v2_pattern = [(k, nk_data[k]['count'], v2(nk_data[k]['count'])) for k in range(2, 22)]
print("\nk | N(k) | v2(N(k)) | N(k)/2^{v2(N(k))}")
for k, n, v in v2_pattern:
    odd_part = n >> v if v < 30 else n
    print(f"{k:2d} | {n:6d} | {v:3d}      | {odd_part}")

print("\n" + "=" * 70)
print("Part 6: 3x+1 の 2-adic 写像としての分析")
print("=" * 70)

# In Z_2 (2-adic integers), the map n -> (3n+1)/2 is a contraction?
# For odd n in Z_2: T_1(n) = (3n+1)/2
# This is a 2-adic isometry? |T_1(n) - T_1(m)|_2 = |3(n-m)|_2/2 = |n-m|_2 / 2
# (since |3|_2 = 1)
# So the map T_1: n -> (3n+1)/2 contracts 2-adic distances by 1/2

# But Syracuse map T(n) = (3n+1)/2^{v2(3n+1)} is more complex
# v2(3n+1) depends on n mod 2^k for various k

# Key insight: for n odd, 3n+1 is even.
# v2(3n+1) = v2(3n+1)
# n = ...b_k b_{k-1} ... b_1 b_0 in binary (b_0 = 1 since n is odd)
# 3n + 1 = 2n + n + 1
# Trailing 1s of n determine v2(3n+1)

# If n = ...0 1^m (m trailing ones), then
# 3n + 1 in binary: carrying through the trailing 1s

# Let's verify: n with t trailing 1s -> v2(3n+1) = ?
print("Trailing 1s -> v2(3n+1) relationship:")
for t in range(1, 16):
    # n with exactly t trailing 1s: n = 2^t * q + (2^t - 1), q even (so bit t is 0)
    # Simplest: n = 2^{t+1} + 2^t - 1 = 3*2^t - 1
    # But we need n odd, so take n = 2^t - 1 (all 1s) for t >= 1
    # Actually: n = 2^t - 1 has t trailing 1s
    # But if t is even, that makes n odd? yes if t >= 1 since LSB = 1

    # Better: test several examples
    v2_vals = set()
    for n in range(1, 2000, 2):
        # Count trailing 1s of n
        trailing = 0
        tmp = n
        while tmp & 1:
            trailing += 1
            tmp >>= 1
        if trailing == t:
            v2_vals.add(v2(3 * n + 1))
            if len(v2_vals) > 3:
                break

    if v2_vals:
        print(f"  t={t:2d} trailing 1s: v2(3n+1) values = {sorted(v2_vals)}")

print("\n" + "=" * 70)
print("Part 7: 厳密な解析 - trailing 1s と v2(3n+1) の関係")
print("=" * 70)

# Theorem attempt: if n has exactly t trailing 1s (n = 2^t * m + 2^t - 1, m even)
# then v2(3n+1) = ?
#
# n = 2^t * m + (2^t - 1), where m is even (bit position t is 0)
# 3n + 1 = 3 * 2^t * m + 3(2^t - 1) + 1 = 3 * 2^t * m + 3*2^t - 2
#         = 3 * 2^t * m + 2(3*2^{t-1} - 1)
#
# Hmm, let's compute more carefully.
# n = 2^t * m + (2^t - 1), m = 2q (even)
# 3n + 1 = 3 * 2^t * 2q + 3*(2^t - 1) + 1
#         = 6q * 2^t + 3*2^t - 2
#         = 2^t(6q + 3) - 2
#         = 2(2^{t-1}(6q+3) - 1)
#
# Now 2^{t-1}(6q+3) is always odd * 2^{t-1} since 6q+3 is odd.
# If t-1 >= 1, then 2^{t-1}(6q+3) is even, so 2^{t-1}(6q+3) - 1 is odd.
# So v2(3n+1) = 1 when t >= 2.
#
# If t = 1: n = 2m + 1, m even, so n = 4q + 1 (since m = 2q)
# 3n + 1 = 12q + 4 = 4(3q + 1)
# v2 = 2 + v2(3q + 1)
# If q is even: v2(3q+1) = v2(1) = 0 when q=0, or generally v2(3*2r + 1) = v2(6r+1) which is 0
# Wait, that's not right. Let me just verify.

print("n with exactly t trailing 1s -> v2(3n+1):")
for t in range(1, 20):
    # Sample many n with exactly t trailing 1s
    v2_counts = Counter()
    count = 0
    for n in range(1, 100000, 2):
        trailing = 0
        tmp = n
        while tmp & 1:
            trailing += 1
            tmp >>= 1
        if trailing == t:
            v2_counts[v2(3 * n + 1)] += 1
            count += 1
            if count >= 1000:
                break
    if v2_counts:
        dominant = v2_counts.most_common(1)[0]
        total = sum(v2_counts.values())
        top5 = dict(sorted(v2_counts.items())[:5])
        print(f"  t={t:2d}: v2 distribution = {top5}  "
              f"(dominant: v2={dominant[0]} at {dominant[1]/total*100:.1f}%)")

print("\n" + "=" * 70)
print("Part 8: 偶奇振動の代数的メカニズム")
print("=" * 70)

# The key question: why does N(k) oscillate between even and odd?
# Recall from Part 4: going from k to k+1, each residue r lifts to r and r+2^k.
# N(k+1) = 2*N(k) - (newly excluded) + (newly appeared, which shouldn't happen)
# Actually, newly appeared can happen: a residue that was excluded mod 2^k
# might become non-excluded mod 2^{k+1} because the finer resolution
# breaks the deterministic descent.

# Let's track this more carefully
print("Detailed lift analysis:")
for k in range(4, min(19, max(nk_data.keys()))):
    res_k = set(compute_non_excluded(k))
    res_k1 = set(compute_non_excluded(k + 1))
    mod_k = 1 << k

    # Classify all odd residues mod 2^{k+1}
    from_nonexcl_survive = 0
    from_nonexcl_newexcl = 0
    from_excl_reappear = 0
    from_excl_stay_excl = 0

    for r in range(1, 1 << (k + 1), 2):
        r_mod_k = r % mod_k
        was_nonexcl = r_mod_k in res_k
        is_nonexcl = r in res_k1

        if was_nonexcl and is_nonexcl:
            from_nonexcl_survive += 1
        elif was_nonexcl and not is_nonexcl:
            from_nonexcl_newexcl += 1
        elif not was_nonexcl and is_nonexcl:
            from_excl_reappear += 1
        else:
            from_excl_stay_excl += 1

    nk = len(res_k)
    nk1 = len(res_k1)
    # N(k+1) = from_nonexcl_survive + from_excl_reappear
    # = (2*N(k) - from_nonexcl_newexcl) + from_excl_reappear
    delta = nk1 - 2 * nk
    print(f"k={k:2d}: N(k)={nk:5d} N(k+1)={nk1:5d} "
          f"survive={from_nonexcl_survive:5d} new_excl={from_nonexcl_newexcl:4d} "
          f"reappear={from_excl_reappear:4d} delta={delta:5d} "
          f"v2(delta)={v2(abs(delta)) if delta !=0 else 'inf'}")

print("\n" + "=" * 70)
print("Part 9: 偶奇振動の2-adic解釈")
print("=" * 70)

# N(k+1) = 2*N(k) - E(k) + R(k)
# where E(k) = newly excluded, R(k) = reappeared
# N(k+1) mod 2 = (2*N(k) - E(k) + R(k)) mod 2 = (-E(k) + R(k)) mod 2 = (E(k) + R(k)) mod 2

# So parity of N(k+1) is determined by E(k) + R(k) mod 2
# Let's check this

print("E(k) and R(k) parity analysis:")
e_values = []
r_values = []
for k in range(4, min(19, max(nk_data.keys()))):
    res_k = set(compute_non_excluded(k))
    res_k1 = set(compute_non_excluded(k + 1))
    mod_k = 1 << k

    E_k = 0  # newly excluded
    R_k = 0  # reappeared

    for r in range(1, 1 << (k + 1), 2):
        r_mod_k = r % mod_k
        was_nonexcl = r_mod_k in res_k
        is_nonexcl = r in res_k1

        if was_nonexcl and not is_nonexcl:
            E_k += 1
        elif not was_nonexcl and is_nonexcl:
            R_k += 1

    nk1 = nk_data[k + 1]['count']
    nk = nk_data[k]['count']
    delta = nk1 - 2 * nk
    check = -E_k + R_k

    e_values.append(E_k)
    r_values.append(R_k)

    print(f"k={k:2d}: E(k)={E_k:4d} R(k)={R_k:4d}  E+R mod2={((E_k+R_k)%2)}  "
          f"N(k+1) mod2={nk1%2}  match={((E_k+R_k)%2) == (nk1%2)}")

print("\n" + "=" * 70)
print("Part 10: v2(3r+1) の分布と排除の深層構造")
print("=" * 70)

# For non-excluded residues, analyze the 2-adic properties of the Syracuse orbit
for k in [8, 10, 12, 14, 16]:
    if k > max(nk_data.keys()):
        break
    residues = compute_non_excluded(k)

    # For each non-excluded residue, compute the sequence of v2 values
    v2_sequences = []
    for r in residues[:50]:  # Sample first 50
        seq = []
        current = r
        for step in range(min(k, 10)):
            m = 3 * current + 1
            v = v2(m)
            seq.append(v)
            if v >= k:
                break
            current = (m >> v) % (1 << k)
        v2_sequences.append(seq)

    # Analyze v2 value at each step
    print(f"\nk={k}: Non-excluded residues v2 sequence analysis (first {min(50, len(residues))} of {len(residues)}):")
    max_len = max(len(s) for s in v2_sequences) if v2_sequences else 0
    for step in range(min(max_len, 8)):
        vals = [s[step] for s in v2_sequences if len(s) > step]
        ctr = Counter(vals)
        avg = sum(vals) / len(vals) if vals else 0
        print(f"  Step {step}: avg_v2={avg:.3f}, dist={dict(sorted(ctr.items())[:6])}")

# Part 11: 2-adic explanation of oscillation
print("\n" + "=" * 70)
print("Part 11: 偶奇振動の理論的説明の仮説")
print("=" * 70)

# Hypothesis: The parity of N(k) is related to some 2-adic property
# Let's check N(k) mod 2 against various k-dependent quantities

print("\nN(k) mod 2 vs various predictors:")
print(f"{'k':>3} {'N(k)':>7} {'N%2':>4} {'k%2':>4} {'k%3':>4} {'k%4':>4} {'v2(k)':>5}")
for k in range(2, 22):
    n = nk_data[k]['count']
    print(f"{k:3d} {n:7d} {n%2:4d} {k%2:4d} {k%3:4d} {k%4:4d} {v2(k):5d}")

# Check if N(k) mod 2 follows a simple rule based on k
parity_seq = [nk_data[k]['count'] % 2 for k in range(2, 22)]
k_mod2_seq = [k % 2 for k in range(2, 22)]
print(f"\nN(k) mod 2: {parity_seq}")
print(f"k mod 2:    {k_mod2_seq}")
match = sum(1 for a, b in zip(parity_seq, k_mod2_seq) if a == b)
print(f"Match rate (N(k)%2 == k%2): {match}/{len(parity_seq)}")

# Check offset patterns
for offset in range(4):
    shifted = [(k + offset) % 2 for k in range(2, 22)]
    match = sum(1 for a, b in zip(parity_seq, shifted) if a == b)
    print(f"Match rate (N(k)%2 == (k+{offset})%2): {match}/{len(parity_seq)}")

print("\n" + "=" * 70)
print("Part 12: Consecutive ratio と振動の精密モデル")
print("=" * 70)

# Model: N(k) ~ C * alpha^k * (1 + epsilon * (-1)^k)
# Fit this more carefully

from math import log

counts_list = [(k, nk_data[k]['count']) for k in range(6, 22)]
log_counts = [(k, log(n)) for k, n in counts_list]

# Simple linear fit of log(N(k)) = a + b*k
n_pts = len(log_counts)
sum_k = sum(k for k, _ in log_counts)
sum_ln = sum(ln for _, ln in log_counts)
sum_k2 = sum(k*k for k, _ in log_counts)
sum_kln = sum(k*ln for k, ln in log_counts)

b = (n_pts * sum_kln - sum_k * sum_ln) / (n_pts * sum_k2 - sum_k**2)
a = (sum_ln - b * sum_k) / n_pts

alpha = math.exp(b)
C = math.exp(a)

print(f"Exponential fit (k=6..21): N(k) ~ {C:.4f} * {alpha:.6f}^k")
print(f"Growth rate per step: {alpha:.6f}")
print(f"log2(alpha) = {b/log(2):.6f}")

# Residuals from exponential model
print(f"\nResiduals from exponential model:")
for k in range(2, 22):
    n = nk_data[k]['count']
    predicted = C * alpha**k
    residual = n - predicted
    rel_residual = residual / predicted if predicted > 0 else 0
    sign = '+' if rel_residual > 0 else '-'
    print(f"k={k:2d}: N(k)={n:6d}, pred={predicted:9.1f}, residual={residual:8.1f}, "
          f"rel={rel_residual:+.4f}  {'<-- odd k' if k%2==1 else '    even k'}")

# Check if residuals oscillate with (-1)^k
print("\nAlternating sign pattern in residuals:")
residuals = []
for k in range(6, 22):
    n = nk_data[k]['count']
    predicted = C * alpha**k
    residuals.append((k, n - predicted, (-1)**k))

for k, res, sign in residuals:
    pos = res > 0
    expected_pos = sign > 0
    match = "MATCH" if pos == expected_pos else "MISMATCH"
    print(f"  k={k}: residual={res:+10.1f}, (-1)^k={sign:+d}, {match}")

# Summary statistics
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
N(k) 系列 (k=2..21):
{[nk_data[k]['count'] for k in range(2, 22)]}

偶奇パターン (0=even, 1=odd):
{[nk_data[k]['count'] % 2 for k in range(2, 22)]}

v2(N(k)) パターン:
{[v2(nk_data[k]['count']) for k in range(2, 22)]}

主要な発見:
1. N(k) mod 2 パターンは明確な周期を持たない（周期2でも3でもない）
2. 成長率 alpha = {alpha:.6f} (各ステップ約{alpha:.3f}倍)
3. 指数モデルからの残差は (-1)^k パターンとは完全には一致しない
""")

# Save results
results = {
    "title": "mod 2^k非排除残基の偶奇振動の2-adic理論的解析",
    "nk_series": {str(k): nk_data[k]['count'] for k in range(2, 22)},
    "parity_pattern": {str(k): nk_data[k]['count'] % 2 for k in range(2, 22)},
    "v2_nk_pattern": {str(k): v2(nk_data[k]['count']) for k in range(2, 22)},
    "exponential_fit": {
        "C": round(C, 6),
        "alpha": round(alpha, 6),
        "range": "k=6..21"
    },
    "lift_analysis": {},
    "oscillation_mechanism": {}
}

# Redo lift analysis for saving
for k in range(4, min(19, max(nk_data.keys()))):
    res_k = set(compute_non_excluded(k))
    res_k1 = set(compute_non_excluded(k + 1))
    mod_k = 1 << k

    E_k = 0
    R_k = 0
    for r in range(1, 1 << (k + 1), 2):
        r_mod_k = r % mod_k
        if r_mod_k in res_k and r not in res_k1:
            E_k += 1
        elif r_mod_k not in res_k and r in res_k1:
            R_k += 1

    results["lift_analysis"][str(k)] = {
        "E_k": E_k,
        "R_k": R_k,
        "delta": nk_data[k+1]['count'] - 2*nk_data[k]['count'],
        "E_plus_R_mod2": (E_k + R_k) % 2
    }

with open("/Users/soyukke/study/lean-unsolved/results/mod2k_parity_2adic_theory.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nResults saved to results/mod2k_parity_2adic_theory.json")
