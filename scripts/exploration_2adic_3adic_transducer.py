"""
Exploration: 2-adic -> 3-adic Finite State Transducer for Collatz/Syracuse map

Goal: Construct an explicit finite state transducer (FST) that reads the
v2 sequence (j_1, j_2, ..., j_k) and outputs the 3-adic digits of T^k(n) mod 3^k.

Key known results:
- T^k(n) mod 3^k = C_k(j_1,...,j_k) * (2^{S_k})^{-1} mod 3^k
- C_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i}, S_0=0, S_i = j_1+...+j_i
- This depends ONLY on the v2 sequence, not on n

The transducer:
- Input alphabet: positive integers (v2 values, typically 1,2,3,...)
- Output alphabet: {1, 2} (3-adic digits, never 0 by mod 3 nonzero theorem)
- State: carries information to compute the next 3-adic digit

We construct this step by step.
"""

import json
import sys
from collections import defaultdict
from itertools import product

def syracuse(n):
    """Syracuse map T(n) = (3n+1)/2^{v2(3n+1)} for odd n."""
    if n % 2 == 0:
        raise ValueError(f"n must be odd, got {n}")
    x = 3 * n + 1
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return x, v

def v2(n):
    """2-adic valuation of n."""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def syracuse_iter(n, k):
    """Compute T^k(n) and the v2 sequence."""
    v2_seq = []
    current = n
    for _ in range(k):
        current, v = syracuse(current)
        v2_seq.append(v)
    return current, v2_seq

def compute_Ck_mod3k(v2_seq):
    """
    Compute C_k mod 3^k from v2 sequence.
    C_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i}
    where S_0=0, S_i = j_1+...+j_i
    """
    k = len(v2_seq)
    if k == 0:
        return 0
    mod = 3**k
    S = [0]  # S_0 = 0
    for j in v2_seq:
        S.append(S[-1] + j)

    Ck = 0
    for i in range(k):
        Ck = (Ck + pow(3, k-1-i, mod) * pow(2, S[i], mod)) % mod
    return Ck

def compute_Tk_mod3k(v2_seq):
    """
    Compute T^k(n) mod 3^k from v2 sequence.
    T^k(n) = C_k * (2^{S_k})^{-1} mod 3^k
    """
    k = len(v2_seq)
    if k == 0:
        return None  # undefined
    mod = 3**k
    Ck = compute_Ck_mod3k(v2_seq)
    Sk = sum(v2_seq)
    inv_2Sk = pow(2, -Sk, mod)  # modular inverse since gcd(2,3)=1
    return (Ck * inv_2Sk) % mod

def extract_3adic_digits(value, k):
    """Extract k base-3 digits of value (least significant first)."""
    digits = []
    v = value
    for _ in range(k):
        digits.append(v % 3)
        v //= 3
    return digits

# ============================================================
# Part 1: Verify the transducer concept
# After reading j_1, ..., j_i, we should be able to output digit d_i
# where d_i is the i-th 3-adic digit of T^k(n) mod 3^k
#
# Key question: Can the i-th digit be determined after reading only j_1,...,j_i?
# Or do we need all k values?
# ============================================================

print("=" * 70)
print("PART 1: Can 3-adic digits be read sequentially?")
print("=" * 70)

# Check if digit_i of T^k(n) mod 3^k depends only on j_1,...,j_i
# (independent of j_{i+1},...,j_k and independent of k)

# Test: for various k, check if digit_i is the same regardless of
# what j_{i+1},...,j_k are
print("\nTest: Is the i-th 3-adic digit stable as k increases?")

test_results = {}
for test_prefix in [(1,), (2,), (1,1), (1,2), (2,1), (1,1,1), (2,1,1)]:
    digit_sets = defaultdict(set)
    prefix_len = len(test_prefix)

    # Try many different suffixes
    for suffix_len in range(0, 5):
        if suffix_len == 0:
            seq = list(test_prefix)
            k = len(seq)
            val = compute_Tk_mod3k(seq)
            digits = extract_3adic_digits(val, k)
            for i in range(prefix_len):
                if i < len(digits):
                    digit_sets[i].add(digits[i])
        else:
            for suffix in product([1, 2, 3], repeat=suffix_len):
                seq = list(test_prefix) + list(suffix)
                k = len(seq)
                val = compute_Tk_mod3k(seq)
                digits = extract_3adic_digits(val, k)
                for i in range(prefix_len):
                    if i < len(digits):
                        digit_sets[i].add(digits[i])

    stable = all(len(digit_sets[i]) == 1 for i in range(prefix_len))
    digit_vals = {i: list(digit_sets[i]) for i in sorted(digit_sets.keys())}
    test_results[str(test_prefix)] = {
        "stable": stable,
        "digits": digit_vals
    }
    print(f"  prefix {test_prefix}: stable={stable}, digits={digit_vals}")

# ============================================================
# Part 2: Derive the recurrence for 3-adic digits
# ============================================================

print("\n" + "=" * 70)
print("PART 2: Recurrence structure for 3-adic digit extraction")
print("=" * 70)

# T^k(n) mod 3^k = C_k * (2^{S_k})^{-1} mod 3^k
# C_k recurrence: C_{k+1} = 3*C_k + 2^{S_k}
# S_{k+1} = S_k + j_{k+1}
#
# Let R_k = T^k(n) mod 3^k = C_k * 2^{-S_k} mod 3^k
# Then R_{k+1} mod 3^{k+1}:
#   C_{k+1} * 2^{-S_{k+1}} = (3*C_k + 2^{S_k}) * 2^{-(S_k + j_{k+1})}
#   = 3*C_k*2^{-S_k}*2^{-j_{k+1}} + 2^{S_k}*2^{-S_k}*2^{-j_{k+1}}
#   = 3*R_k*2^{-j_{k+1}} + 2^{-j_{k+1}}  (mod 3^{k+1})
#   = (3*R_k + 1) * 2^{-j_{k+1}} (mod 3^{k+1})
#
# This is the KEY RECURRENCE:
#   R_{k+1} = (3*R_k + 1) * 2^{-j_{k+1}} mod 3^{k+1}
# with R_0 interpreted suitably (R_1 = 2^{-j_1} mod 3)

print("\nKey recurrence: R_{k+1} = (3*R_k + 1) * 2^{-j_{k+1}} mod 3^{k+1}")
print("where R_k = T^k(n) mod 3^k")

# Verify the recurrence
print("\nVerification of recurrence:")
for n_test in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]:
    current = n_test
    R_prev = 0  # R_0 conceptually
    v2_list = []
    all_ok = True
    for step in range(1, 7):
        current_val, v_val = syracuse(current)
        v2_list.append(v_val)

        # Direct computation
        Tk_mod = compute_Tk_mod3k(v2_list)

        # Recurrence computation
        mod = 3**step
        inv2j = pow(2, -v_val, mod)
        if step == 1:
            R_recur = (1 * inv2j) % mod  # R_0 = 0, so (3*0+1)*2^{-j_1}
        else:
            # lift R_prev to mod 3^step
            R_recur = ((3 * R_prev + 1) * inv2j) % mod

        if Tk_mod != R_recur:
            all_ok = False
            print(f"  MISMATCH n={n_test}, step={step}: direct={Tk_mod}, recur={R_recur}")

        R_prev = R_recur
        current = current_val

    if all_ok:
        print(f"  n={n_test}: recurrence matches for all 6 steps")

# ============================================================
# Part 3: Extract digit-by-digit output rule
# ============================================================

print("\n" + "=" * 70)
print("PART 3: Digit extraction - the transducer output function")
print("=" * 70)

# R_k = value mod 3^k, with 3-adic expansion d_1 + d_2*3 + ... + d_k*3^{k-1}
# The k-th digit is: d_k = (R_k - R_{k-1}) / 3^{k-1}
# Since R_k mod 3^{k-1} = R_{k-1} (consistency), this is well-defined
#
# From R_{k+1} = (3*R_k + 1) * 2^{-j_{k+1}} mod 3^{k+1}:
# d_{k+1} = floor(R_{k+1} / 3^k) mod 3

# The STATE of the transducer needs to track enough to compute d_{k+1}
# What info do we need?
# R_{k+1} mod 3^{k+1} = (3*R_k + 1) * 2^{-j_{k+1}} mod 3^{k+1}
# d_{k+1} = (R_{k+1} // 3^k) % 3
# We need R_k mod 3^{k+1} to compute this... but R_k is only defined mod 3^k!
#
# Actually: (3*R_k + 1) * 2^{-j_{k+1}} mod 3^{k+1}
# 3*R_k mod 3^{k+1}: since R_k is mod 3^k, 3*R_k is mod 3^{k+1}, fine
# So we need: R_k mod 3^k (which gives 3*R_k mod 3^{k+1})
# BUT for the NEXT step we need R_{k+1} mod 3^{k+1}, which requires
# full precision at each level.
#
# This means the state space grows: at step k, the state is R_k mod 3^k
# That's 2*3^{k-1} possible states (since R_k is coprime to 3)
#
# For a FIXED number of digits, we can build a finite transducer.
# But for arbitrary k, the state space is infinite.
#
# HOWEVER: there might be a finite-state representation if we track
# only a "carry" or similar bounded information.

# Let's investigate the carry structure
print("\nAnalyzing the carry structure of digit computation:")
print("R_{k+1} = (3*R_k + 1) * 2^{-j} mod 3^{k+1}")
print("Write R_k = d_1 + d_2*3 + ... + d_k*3^{k-1}")
print("Then 3*R_k + 1 = 1 + d_1*3 + d_2*9 + ... + d_k*3^k")
print("Need to multiply by 2^{-j} mod 3^{k+1} and extract digit k+1")

# Key insight: 2^{-j} mod 3^{k+1} depends on j mod ord_{3^{k+1}}(2) = 2*3^k
# For the DIGIT at position k+1, only a finite amount of information matters.

# Let's try a different approach: track the "carry" from the multiplication
# by 2^{-j}.

# Alternative: work in the 3-adic integers directly.
# In Z_3, the sequence R_1, R_2, ... converges to a 3-adic integer R
# whose digits are d_1, d_2, ...
# R = lim_{k->inf} R_k = lim (C_k * 2^{-S_k}) in Z_3

# For the transducer, we need to compute d_k given d_1,...,d_{k-1} and j_k.
# The recurrence in Z_3: if we define r = ...d_2 d_1 (3-adic integer built so far)
# then the next coefficient d_{k+1} depends on r mod 3^k and j_{k+1}.

# Since the state space at step k is Z/3^k Z (coprime part), it grows.
# But let's check: maybe only the LAST few digits matter?

print("\nChecking if d_{k+1} depends on bounded recent history:")

# For each step k, check if d_{k+1} depends on all of d_1,...,d_k or only recent ones
dependency_test = {}
for k_test in range(2, 8):
    # Generate many v2 sequences of length k_test
    # Check if d_{k_test} (the last digit) depends on d_1 or only on recent digits
    digit_by_config = defaultdict(set)

    # Use actual Syracuse orbits
    for n in range(1, 2000, 2):  # odd numbers
        _, v2_seq = syracuse_iter(n, k_test)
        val = compute_Tk_mod3k(v2_seq)
        digits = extract_3adic_digits(val, k_test)

        # Key: does digit[k_test-1] depend on digit[0]?
        # Group by (j_k, d_{k-1}) and see if d_k varies
        key_recent = (v2_seq[-1], digits[-2] if k_test > 1 else None)
        key_full = tuple(v2_seq)

        digit_by_config[key_recent].add(digits[-1])

    # Check how many keys have multiple digit values
    multi_count = sum(1 for v in digit_by_config.values() if len(v) > 1)
    total_keys = len(digit_by_config)

    dependency_test[k_test] = {
        "total_keys": total_keys,
        "multi_valued": multi_count,
        "fraction_determined_by_recent": 1 - multi_count/total_keys if total_keys > 0 else 0
    }
    print(f"  k={k_test}: {total_keys} distinct (j_k, d_{{k-1}}) pairs, "
          f"{multi_count} have multiple d_k values, "
          f"frac_determined={1 - multi_count/total_keys:.3f}")

# ============================================================
# Part 4: Construct the actual transducer for small moduli
# ============================================================

print("\n" + "=" * 70)
print("PART 4: Explicit transducer for mod 3, mod 9, mod 27")
print("=" * 70)

# For mod 3^K (fixed K), build the transducer:
# State = R_k mod 3^K (the accumulated value so far, lifted)
# Input = j (v2 value)
# Output = new digit at position k+1 (if k < K)
# Transition = R_{k+1} mod 3^K

# But we need R_k mod 3^{k+1} for the digit, and R_k is defined mod 3^k
# The trick: work always mod 3^K for a fixed K

for K in [1, 2, 3, 4]:
    mod = 3**K
    print(f"\n--- Transducer for mod 3^{K} = {mod} ---")

    # States: elements of (Z/3^K Z)* plus initial state
    # Initial state: 0 (before any step)
    # Transition: state R, input j -> new_state = (3*R + 1) * 2^{-j} mod 3^K
    # BUT: at step k, R is conceptually mod 3^k, and we need mod 3^{k+1}
    # For a fixed K, we just track everything mod 3^K

    # Actually the correct approach for a K-digit transducer:
    # State after reading (j_1,...,j_k) is R_k mod 3^K
    # Transition on reading j_{k+1}: R_{k+1} = (3*R_k + 1)*2^{-j_{k+1}} mod 3^K
    # Output: none during processing; at the end, read off all K digits from final state

    # For a STREAMING transducer that outputs digit by digit:
    # At step k, state = R_k mod 3^K (for some large enough K)
    # Output digit d_k = (R_k // 3^{k-1}) % 3
    # But this requires knowing k (the step count), which means the transducer
    # is not purely finite-state in the classical sense

    # Let's build the transition table
    transitions = {}
    max_j = 8  # typical v2 values are 1-8

    states = list(range(mod))
    for R in states:
        for j in range(1, max_j + 1):
            inv2j = pow(2, -j, mod)
            new_R = ((3 * R + 1) * inv2j) % mod
            transitions[(R, j)] = new_R

    # Count reachable states from initial state 0
    reachable = {0}
    frontier = {0}
    for step in range(K + 2):
        new_frontier = set()
        for R in frontier:
            for j in range(1, max_j + 1):
                nR = transitions[(R, j)]
                if nR not in reachable:
                    reachable.add(nR)
                    new_frontier.add(nR)
        frontier = new_frontier

    print(f"  Total states mod {mod}: {mod}")
    print(f"  Reachable from 0 (after {K+2} steps): {len(reachable)}")

    # Check: all reachable states are coprime to 3 (except initial 0)
    coprime_reachable = sum(1 for r in reachable if r % 3 != 0)
    print(f"  Coprime to 3: {coprime_reachable}, Not coprime: {len(reachable) - coprime_reachable}")

    # Verify transducer by comparing with direct computation
    verified = 0
    total_tests = 0
    for n in range(1, 200, 2):
        _, v2_seq = syracuse_iter(n, K)

        # Transducer simulation
        R = 0
        for j in v2_seq:
            j_eff = min(j, max_j)  # clip for table lookup
            inv2j = pow(2, -j, mod)
            R = ((3 * R + 1) * inv2j) % mod

        # Direct computation
        Tk_mod = compute_Tk_mod3k(v2_seq)

        total_tests += 1
        if R == Tk_mod:
            verified += 1

    print(f"  Verification: {verified}/{total_tests} match")

    if K <= 2:
        # Print small transition tables
        print(f"  Transition table (state, input -> new_state):")
        for R in sorted(reachable):
            for j in range(1, 4):
                nR = transitions[(R, j)]
                print(f"    ({R}, j={j}) -> {nR}")

# ============================================================
# Part 5: The "streaming" transducer - output digits one by one
# ============================================================

print("\n" + "=" * 70)
print("PART 5: Streaming digit output analysis")
print("=" * 70)

# Key question: Can we output d_k after reading j_k (online/streaming)?
#
# From the recurrence: R_k = (3*R_{k-1} + 1) * 2^{-j_k} mod 3^k
# d_k = (R_k // 3^{k-1}) % 3
#
# R_k mod 3 = d_1 (the first digit), always determined
# R_k mod 9 gives d_1 and d_2, etc.
#
# For streaming: when we read j_1, we can output d_1 = R_1 mod 3 = 2^{-j_1} mod 3
# When we read j_2, to output d_2 we need R_2 mod 9
# R_2 = (3*R_1 + 1)*2^{-j_2} mod 9, where R_1 = 2^{-j_1} mod 3
# But we need R_1 mod 9 (not just mod 3) to compute R_2 mod 9!
# R_1 = 2^{-j_1} mod 9 (NOT mod 3)
#
# So the state after step 1 is R_1 mod 9 (for 2-digit streaming)
# After step k, state is R_k mod 3^{K} for K-digit streaming

# The state must be R_k mod 3^K where K is the maximum number of digits desired.
# This is NOT a finite-state transducer for arbitrary K.

# HOWEVER: if we consider the 3-adic integer R = lim R_k in Z_3,
# and define the state as R_k (an element of Z_3 approximated to k digits),
# then we get an infinite-state transducer.

# Can we decompose it into a FINITE-state component?
#
# Alternative formulation: work mod 3 only (output one digit per step)
# State = some finite info, input = j, output = d in {1,2}
#
# Check: is d_k determined by j_k and some bounded state?

print("\nAnalyzing state needed for each digit output:")

# For the first digit d_1:
# R_1 = 2^{-j_1} mod 3 = (2 if j odd, 1 if j even)
# No state needed! Just j_1 determines d_1.
print("Digit 1: d_1 = 2^{-j_1} mod 3 = (1 if j_1 even, 2 if j_1 odd)")

# For the second digit d_2:
# R_2 mod 9 = (3*R_1 + 1)*2^{-j_2} mod 9
# Need R_1 mod 9 = 2^{-j_1} mod 9
# j_1 mod 6 determines 2^{-j_1} mod 9 (since ord_9(2) = 6)
# So state after reading j_1 = j_1 mod 6
# Then d_2 = (R_2 // 3) % 3

# For the k-th digit:
# Need R_{k-1} mod 3^k to compute R_k mod 3^k and extract d_k
# State = R_{k-1} mod 3^k, which grows with k

# Check: is there a BOUNDED carry that suffices?
# R_k = (3*R_{k-1} + 1) * 2^{-j_k} mod 3^k
# Write R_{k-1} = d_1 + d_2*3 + ... + d_{k-1}*3^{k-2} + c*3^{k-1} (with carry c)
# Then 3*R_{k-1} + 1 = 1 + d_1*3 + d_2*9 + ... + d_{k-1}*3^{k-1} + c*3^k
# mod 3^k: = 1 + d_1*3 + ... + d_{k-1}*3^{k-1}
# So the carry c drops out mod 3^k!

# This means: R_k mod 3^k = ((3*R_{k-1} + 1) * 2^{-j_k}) mod 3^k
# only depends on R_{k-1} mod 3^{k-1} (since 3*R_{k-1} mod 3^k uses R_{k-1} mod 3^{k-1})
# PLUS maybe some extra info for the multiplication by 2^{-j_k}

# Wait, let's be more precise:
# 3*R_{k-1} mod 3^k depends only on R_{k-1} mod 3^{k-1} -- YES
# (3*R_{k-1} + 1) mod 3^k depends only on R_{k-1} mod 3^{k-1} -- YES
# (3*R_{k-1} + 1) * 2^{-j_k} mod 3^k -- this is a multiplication mod 3^k
# which also only depends on R_{k-1} mod 3^{k-1} and j_k mod ord_{3^k}(2) = 2*3^{k-1}

# So the TOTAL information needed at step k is:
# (R_{k-1} mod 3^{k-1}, j_k mod 2*3^{k-1})
# State space: 3^{k-1} * 2*3^{k-1} = 2*3^{2(k-1)} -- still growing!

# BUT: let's check if there's a decomposition where only bounded info is needed
# for the INCREMENTAL digit computation.

# The digit d_k requires knowing:
# floor(R_k / 3^{k-1}) mod 3
# where R_k = (3*R_{k-1} + 1) * 2^{-j_k} mod 3^k

# Since 3*R_{k-1}+1 mod 3^k depends on R_{k-1} mod 3^{k-1},
# and R_{k-1} mod 3^{k-1} encodes digits d_1,...,d_{k-1},
# we need ALL previous digits plus j_k.

# THIS IS THE KEY NEGATIVE RESULT:
# A finite-state transducer cannot stream arbitrary digits,
# because the state must grow with k.

# However, for FIXED depth K, the transducer IS finite.
# And there's a beautiful structure to exploit.

print("\n--- Finite transducer for fixed depth K ---")
print("State space at each step = R mod 3^K")
print("For K=1: 2 states (coprime to 3)")
print("For K=2: 6 states")
print("For K=3: 18 states")
print("For K=4: 54 states")
print(f"General: 2*3^(K-1) states (= phi(3^K))")

# ============================================================
# Part 6: Alternative - Mealy machine with bounded lookahead
# ============================================================

print("\n" + "=" * 70)
print("PART 6: Mealy machine representation for digit d_k")
print("=" * 70)

# Even though streaming requires growing state, we can build a
# Mealy machine for each FIXED k that computes d_k from (j_1,...,j_k).
# This has the SAME transition structure for all k!
#
# The transition is: R -> (3*R + 1)*2^{-j} mod 3^K
# where K is chosen large enough.

# Actually, let's reconsider. There IS a finite representation:
# the "right-to-left" transducer.
#
# The 3-adic digits can be computed from RIGHT to LEFT:
# d_k depends on j_k and a carry from j_{k+1},...
# Wait, this is backwards.

# Let's try yet another approach:
# Separate the concerns of "which j values" from "which digits"

# For the least significant digit d_1:
# d_1 = 2^{-j_1} mod 3, depends on j_1 mod 2
# THIS is a 2-state transducer.

# For digit d_2 given d_1:
# Need R_1 mod 9, which is 2^{-j_1} mod 9
# This depends on j_1 mod 6
# Then d_2 = ((3 * R_1_mod9 + 1) * 2^{-j_2}) // 3 mod 3

# State = (j_1 mod 6) -- 6 states, outputs (d_1, d_2)

# INSIGHT: We can build a SEQUENTIAL transducer that operates on
# (j_1, j_2, ..., j_k) and outputs (d_1, d_2, ..., d_k)
# with state = R mod 3^K and it works perfectly for depth K.
# The number of input symbols per transition is 1 (one j value),
# the number of output symbols is 1 (one d value).

# Build the explicit Mealy machine for K=3 (mod 27)
K = 3
mod = 3**K
max_j_val = 10

print(f"\nMealy machine for K={K} (mod {mod}):")
print(f"  States: 0, 1, 2, ..., {mod-1} (representing R mod {mod})")
print(f"  Initial state: 0")
print(f"  Input alphabet: positive integers (v2 values)")
print(f"  Output alphabet: {{1, 2}} (3-adic digits, never 0)")

# Build transition and output tables
mealy_transitions = {}
mealy_outputs = {}

for R in range(mod):
    for j in range(1, max_j_val + 1):
        inv2j = pow(2, -j, mod)
        new_R = ((3 * R + 1) * inv2j) % mod
        mealy_transitions[(R, j)] = new_R
        # Output: what's the new digit?
        # If state was R (representing R_{k-1} mod 3^K),
        # new state is R_k mod 3^K
        # But which digit to output depends on which step k we're at...
        # This is the problem: the output function depends on k.

# The issue is that digit extraction requires knowing the step number k.
# d_k = (R_k // 3^{k-1}) mod 3
# But the transducer doesn't inherently know k.

# SOLUTION: Use a different state encoding.
# Instead of R_k mod 3^K, track the "unextracted" part.
# After extracting digits d_1,...,d_{k-1}, the remaining info is
# R_k mod 3^K with the lower k-1 digits "consumed".
# Define Q_k = (R_k - (d_1 + d_2*3 + ... + d_{k-1}*3^{k-2})) / 3^{k-1}
# Wait, this is just d_k + d_{k+1}*3 + ... (the remaining higher digits)

# Actually, the simplest approach: state = R_k mod 3^K
# and output at step k = (R_k // 3^{k-1}) mod 3
# The step counter k is implicit (we count transitions).

# For a formal Mealy machine at FIXED K:
# - States: {0, 1, ..., 3^K - 1} x {0, 1, ..., K-1} (value + step counter)
# - But this is still finite for fixed K!

# Let's compute the full table
print(f"\n  Transition and output table (first few states):")
for R in [0, 1, 2, 4, 5, 7, 8]:
    for j in [1, 2, 3]:
        new_R = mealy_transitions[(R, j)]
        print(f"    delta({R}, {j}) = {new_R}")

# ============================================================
# Part 7: The RIGHT key insight -- 2-state automaton mod 3
# ============================================================

print("\n" + "=" * 70)
print("PART 7: The fundamental 2-state automaton (mod 3)")
print("=" * 70)

# The simplest non-trivial transducer: computes T^k(n) mod 3
# from the v2 sequence.
#
# Since T^k(n) mod 3 is in {1, 2}, we have 2 states.
# But actually, R_k mod 3 = 2^{-j_1-...-j_k} mod 3
# Wait no: R_k = C_k * 2^{-S_k} mod 3

# From the recurrence R_k = (3*R_{k-1}+1)*2^{-j_k} mod 3^k:
# R_k mod 3 = (0 + 1) * 2^{-j_k} mod 3 = 2^{-j_k} mod 3
# Wait, this says R_k mod 3 depends only on j_k, not on previous state!
# Because 3*R_{k-1} = 0 mod 3.

# So: d_1 (the first 3-adic digit) = R_k mod 3 = 2^{-j_k} mod 3
# This means: d_1 = 1 if j_k even, d_1 = 2 if j_k odd.

# WAIT: this is the FIRST digit, independent of k!
# That can't be right. Let me re-examine.

# R_1 = 2^{-j_1} mod 3. d_1 = R_1 mod 3 = 2^{-j_1} mod 3. Correct.
# R_2 = (3*R_1+1)*2^{-j_2} mod 9. d_1 = R_2 mod 3 = 2^{-j_2} mod 3.
# But also d_1 should = R_1 mod 3 = 2^{-j_1} mod 3!
# CONTRADICTION unless 2^{-j_1} = 2^{-j_2} mod 3 always, which is false.

# The issue: R_k is T^k(n) mod 3^k, and the digits are of T^k(n), not T^1,...,T^k.
# So for a FIXED k, the 3-adic digits are those of a SINGLE value T^k(n).
# Different k gives different values and different digit sequences.

# This changes the nature of the transducer completely!
# The transducer reads (j_1,...,j_k) and outputs the 3-adic digits of T^k(n),
# NOT one digit per j value.

# Reframing: the transducer maps a SEQUENCE of v2 values to a SINGLE
# 3-adic integer (T^k(n) mod 3^k).

# For a streaming version, we want: after reading j_1,...,j_m,
# can we output the LAST digit of T^m(n) mod 3^m?
# But that's just d_m, the m-th digit.

# From R_m mod 3: (3*R_{m-1}+1)*2^{-j_m} mod 3 = 2^{-j_m} mod 3
# So the last digit (d_m, the most significant of the first m digits)
# depends only on j_m! That's the trivial mod 3 result.

# CORRECT FRAMEWORK:
# The transducer produces ALL digits of T^k(n) mod 3^k at once,
# after reading k inputs. The internal state carries the accumulated
# R value.

# Let me verify: R_1 mod 3 = 2^{-j_1} mod 3
# R_2 mod 3 = (3*R_1+1)*2^{-j_2} mod 3 = 2^{-j_2} mod 3
# These can be DIFFERENT from R_1 mod 3!
# So R_2 mod 3 != R_1 mod 3 in general.
# Digits of T^2(n) are NOT digits of T^1(n) extended.

print("CLARIFICATION: T^k(n) mod 3^k are NOT coherent as k increases.")
print("That is, T^{k+1}(n) mod 3^k != T^k(n) mod 3^k in general.")
print("Each T^k(n) is a DIFFERENT number.")

# Verify
for n in [1, 3, 5, 7, 9]:
    print(f"\n  n={n}:")
    current = n
    for k in range(1, 6):
        current, v = syracuse(current) if k > 0 else (current, 0)
        # Recompute from scratch
        Tk, _ = syracuse_iter(n, k)
        Tk_prev, _ = syracuse_iter(n, k-1) if k > 1 else (n, [])
        mod_k = 3**k
        mod_km1 = 3**(k-1) if k > 1 else 1
        print(f"    T^{k}(n)={Tk}, mod 3^{k}={Tk % mod_k}, mod 3^{k-1}={Tk % mod_km1}" +
              (f", T^{k-1}(n) mod 3^{k-1}={Tk_prev % mod_km1}" if k > 1 else ""))

# ============================================================
# Part 8: The correct transducer -- map v2_seq to C_k value
# ============================================================

print("\n" + "=" * 70)
print("PART 8: Correct transducer formulation")
print("=" * 70)

# The mathematically correct transducer reads (j_1,...,j_k) and produces
# the residue class T^k(n) mod 3^k, which depends only on the input.
#
# For FIXED K, the transducer is:
# - States: Z/3^K Z (integers mod 3^K)
# - Initial state: 0
# - Transition: delta(R, j) = (3*R + 1) * 2^{-j} mod 3^K
# - Final output: R_K after K steps, read as K base-3 digits
#
# This is a Deterministic Finite Automaton (DFA) / Mealy machine
# with 3^K states.
#
# But we can also think of it as a FAMILY of transducers indexed by K,
# with a natural projection: the K+1 transducer's state modulo 3^K
# gives the K transducer's state.
#
# This is precisely the PROFINITE structure of Z_3!

print("The 2-adic to 3-adic transducer is the profinite limit of")
print("Mealy machines M_K with 3^K states each.")
print()
print("M_K = (Q_K, Sigma, Delta_K, q0, lambda_K) where:")
print(f"  Q_K = Z/3^K Z = {{0, 1, ..., 3^K - 1}}")
print(f"  Sigma = Z_{{>0}} (positive integers, the v2 values)")
print(f"  q0 = 0 (initial state)")
print(f"  delta_K(R, j) = (3R + 1) * 2^{{-j}} mod 3^K")
print(f"  lambda_K(R) = base-3 digits of R (the 3-adic expansion truncated to K digits)")

# Verify the profinite consistency
print("\nProfinite consistency check:")
print("Does delta_{K+1}(R, j) mod 3^K = delta_K(R mod 3^K, j)?")

all_consistent = True
for K in range(1, 5):
    mod_K = 3**K
    mod_K1 = 3**(K+1)

    inconsistencies = 0
    tests = 0
    for R in range(mod_K1):
        for j in range(1, 8):
            inv2j_K = pow(2, -j, mod_K)
            inv2j_K1 = pow(2, -j, mod_K1)

            new_R_K1 = ((3 * R + 1) * inv2j_K1) % mod_K1
            new_R_K = ((3 * (R % mod_K) + 1) * inv2j_K) % mod_K

            tests += 1
            if new_R_K1 % mod_K != new_R_K:
                inconsistencies += 1
                all_consistent = False

    print(f"  K={K} -> K+1={K+1}: {tests} tests, {inconsistencies} inconsistencies")

if all_consistent:
    print("  ALL CONSISTENT - profinite structure confirmed!")

# ============================================================
# Part 9: Effective state reduction
# ============================================================

print("\n" + "=" * 70)
print("PART 9: State reduction analysis")
print("=" * 70)

# The state space Q_K = Z/3^K Z has 3^K elements.
# But not all states are reachable from q0=0.
# How many states are reachable after exactly k steps?

for K in [2, 3, 4, 5]:
    mod = 3**K

    reachable_at_step = [set() for _ in range(K + 3)]
    reachable_at_step[0] = {0}

    all_reachable = {0}
    for step in range(1, K + 3):
        for R in reachable_at_step[step - 1]:
            for j in range(1, 10):
                inv2j = pow(2, -j, mod)
                new_R = ((3 * R + 1) * inv2j) % mod
                reachable_at_step[step].add(new_R)
                all_reachable.add(new_R)

    sizes = [len(reachable_at_step[s]) for s in range(K + 3)]
    print(f"  K={K} (mod {mod}): reachable at step 0..{K+2}: {sizes}")
    print(f"    Total reachable: {len(all_reachable)} out of {mod}")

    # Check: are all coprime-to-3 states eventually reachable?
    coprime_states = {r for r in range(mod) if r % 3 != 0}
    coprime_reachable = all_reachable & coprime_states
    print(f"    Coprime states: {len(coprime_states)}, reachable: {len(coprime_reachable)}")

    # The 0 state (divisible by 3): is it reachable after step 0?
    zero_reachable_later = any(0 in reachable_at_step[s] for s in range(1, K + 3))
    mult3_reachable = {r for r in all_reachable if r % 3 == 0}
    print(f"    States divisible by 3 reachable: {mult3_reachable}")

# ============================================================
# Part 10: Summary of the transducer structure
# ============================================================

print("\n" + "=" * 70)
print("PART 10: Complete transducer characterization")
print("=" * 70)

# For each K, compute the transition table and verify digit-0 avoidance
for K in [1, 2, 3]:
    mod = 3**K
    print(f"\n--- K={K}, mod={mod} ---")

    # All reachable non-initial states
    reachable = set()
    frontier = {0}
    for _ in range(K + 2):
        new_frontier = set()
        for R in frontier:
            for j in range(1, 8):
                inv2j = pow(2, -j, mod)
                new_R = ((3 * R + 1) * inv2j) % mod
                if new_R not in reachable:
                    reachable.add(new_R)
                    new_frontier.add(new_R)
        frontier = new_frontier

    # Check: all reachable states (except initial 0) have d_1 != 0
    # i.e., state mod 3 != 0
    all_nonzero_d1 = all(r % 3 != 0 for r in reachable)
    print(f"  All reachable states have mod 3 != 0: {all_nonzero_d1}")

    # Extract the transition graph structure
    if K <= 2:
        print(f"  Full transition graph:")
        for R in sorted(reachable):
            targets = {}
            for j in range(1, 5):
                inv2j = pow(2, -j, mod)
                new_R = ((3 * R + 1) * inv2j) % mod
                targets[j] = new_R
            digits = extract_3adic_digits(R, K)
            digit_str = ''.join(str(d) for d in reversed(digits))
            print(f"    R={R} (3-adic: {digit_str}): " +
                  ", ".join(f"j={j}->{t}" for j, t in targets.items()))

# Compute number of distinct output classes for small K
print("\n\nDistinct outputs (T^K(n) mod 3^K) for various K:")
for K in range(1, 7):
    outputs = set()
    for n in range(1, 5000, 2):
        _, v2_seq = syracuse_iter(n, K)
        val = compute_Tk_mod3k(v2_seq)
        outputs.add(val)

    # Check which residues appear
    missing = set(range(1, 3**K)) - outputs - {r for r in range(3**K) if r % 3 == 0}
    print(f"  K={K}: {len(outputs)} distinct values out of {3**K}, "
          f"missing coprime: {len(missing)}, "
          f"all outputs coprime to 3: {all(o % 3 != 0 for o in outputs)}")

print("\n\nDone!")
