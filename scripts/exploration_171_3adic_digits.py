"""
Exploration 171: 3-adic digit 0 non-appearance in Syracuse iterates
T^k(n) mod 3^k has all digits in {1,2} (no digit 0 in base 3)

Key question: Is it true that syracuseIter k n mod 3 != 0 for all k, all odd n >= 1?
More generally: Do all 3-adic digits of T^k(n) avoid 0?
"""

import sys

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
    """Syracuse function: (3n+1) / 2^v2(3n+1)"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

def base3_digits(n, num_digits):
    """Extract first num_digits base-3 digits (least significant first)"""
    digits = []
    for _ in range(num_digits):
        digits.append(n % 3)
        n //= 3
    return digits

# ============================================================
# Part 1: Verify T^k(n) % 3 != 0 for many n, k
# ============================================================
print("=" * 60)
print("Part 1: Verify T^k(n) mod 3 != 0 for odd n=1..999, k=1..30")
print("=" * 60)

violations_mod3 = []
for n in range(1, 1000, 2):  # odd numbers 1,3,5,...,999
    val = n
    for k in range(1, 31):
        val = syracuse(val)
        if val % 3 == 0:
            violations_mod3.append((n, k, val))

if violations_mod3:
    print(f"VIOLATIONS found: {len(violations_mod3)}")
    for v in violations_mod3[:10]:
        print(f"  n={v[0]}, k={v[1]}, T^k(n)={v[2]}")
else:
    print("No violations found! T^k(n) mod 3 != 0 holds for all tested cases.")

# ============================================================
# Part 2: Check 3-adic digits of T^k(n) mod 3^k
# ============================================================
print("\n" + "=" * 60)
print("Part 2: 3-adic digits of T^k(n): check digit 0 non-appearance")
print("=" * 60)

# For T^k(n), check if (T^k(n) mod 3^k) has any digit 0 in base 3
digit0_found = []
for n in range(1, 200, 2):
    val = n
    for k in range(1, 16):
        val = syracuse(val)
        residue = val % (3 ** k)
        digits = base3_digits(residue, k)
        if 0 in digits:
            digit0_found.append((n, k, val, residue, digits))

if digit0_found:
    print(f"Cases where digit 0 appears in T^k(n) mod 3^k: {len(digit0_found)}")
    for item in digit0_found[:20]:
        n, k, val, res, digs = item
        print(f"  n={n}, k={k}, T^k(n)={val}, mod 3^{k}={res}, digits(lsb)={digs}")
else:
    print("No digit-0 found! All 3-adic digits of T^k(n) mod 3^k are in {1,2}.")

# ============================================================
# Part 3: Deeper analysis of T^k(n) mod 3 pattern
# ============================================================
print("\n" + "=" * 60)
print("Part 3: T^k(n) mod 3 distribution for various n")
print("=" * 60)

for n in [1, 3, 5, 7, 9, 11, 13, 15, 27, 31, 127, 255]:
    mods = []
    val = n
    for k in range(1, 21):
        val = syracuse(val)
        mods.append(val % 3)
    print(f"  n={n:>4}: T^k mod 3 = {mods}")

# ============================================================
# Part 4: Proof of T^k(n) mod 3 != 0 by induction analysis
# ============================================================
print("\n" + "=" * 60)
print("Part 4: Analysis of why T(T^{k-1}(n)) mod 3 != 0")
print("=" * 60)

print("""
Key chain of reasoning:
1. syracuse_not_div_three: For odd n, syracuse(n) % 3 != 0 (PROVEN in Lean)
2. syracuse produces odd outputs (by definition: divides out all factors of 2)
3. Therefore by induction:
   - Base: n is odd, so syracuse(n) % 3 != 0, and syracuse(n) is odd
   - Step: If T^k(n) is odd and T^k(n) % 3 != 0, then:
     * T^{k+1}(n) = syracuse(T^k(n)) % 3 != 0 (by syracuse_not_div_three)
     * T^{k+1}(n) is odd (by definition of syracuse)
""")

# Verify syracuse always produces odd numbers
print("Verifying syracuse always produces odd outputs:")
all_odd = True
for n in range(1, 10000, 2):
    s = syracuse(n)
    if s % 2 != 1:
        print(f"  COUNTEREXAMPLE: n={n}, syracuse(n)={s} is even!")
        all_odd = False
        break
if all_odd:
    print("  Confirmed: syracuse(n) is always odd for odd n in [1, 9999]")

# ============================================================
# Part 5: Check what's needed for Lean formalization
# ============================================================
print("\n" + "=" * 60)
print("Part 5: Lean formalization requirements")
print("=" * 60)

# Check if syracuse_odd is already proven
print("""
Required lemmas for the inductive proof:

1. syracuse_odd (n : Nat) (hodd : n % 2 = 1) : syracuse n % 2 = 1
   Status: Need to check if this exists

2. syracuse_not_div_three (n : Nat) (hn : n % 2 = 1) : syracuse n % 3 != 0
   Status: PROVEN (in Structure.lean line 272)

3. New theorem (by induction on k):
   syracuseIter_not_div_three (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
     syracuseIter k n % 3 != 0

   Proof sketch:
   - k = 0: hodd implies n % 2 = 1, and we need n % 3 != 0...
     Wait, this is NOT true for n=3 (3 % 3 = 0)!

   Let me reconsider...
""")

# Re-check: is n % 3 != 0 for the input n?
print("Check: Does T^k(n) mod 3 != 0 hold even when n % 3 = 0?")
for n in [3, 9, 15, 21, 27, 33]:
    print(f"  n={n}: n%3={n%3}")
    val = n
    for k in range(1, 11):
        val = syracuse(val)
        print(f"    T^{k}({n}) = {val}, mod 3 = {val%3}")

# ============================================================
# Part 6: Refined statement analysis
# ============================================================
print("\n" + "=" * 60)
print("Part 6: Refined statement - T^k(n) % 3 != 0 for all k >= 1")
print("=" * 60)

print("""
IMPORTANT CORRECTION:
- The statement T^k(n) % 3 != 0 needs k >= 1, NOT k >= 0
- At k=0, T^0(n) = n, and n could be divisible by 3 (e.g., n=3)
- But syracuse(n) is never divisible by 3 (syracuse_not_div_three)
- And syracuse of odd number is odd (need to verify/prove)
- So for k >= 1: T^k(n) is odd AND T^k(n) % 3 != 0

Correct statement:
  For all odd n >= 1, for all k >= 1:
    syracuseIter k n % 3 != 0

Alternative equivalent:
  For all odd n >= 1, for all k >= 0:
    syracuse (syracuseIter k n) % 3 != 0
    = syracuseIter (k+1) n % 3 != 0
""")

# Final comprehensive check
print("Final comprehensive verification:")
max_violations = 0
for n in range(1, 2000, 2):
    val = n
    for k in range(1, 50):
        val = syracuse(val)
        if val % 3 == 0:
            max_violations += 1
            print(f"  VIOLATION at n={n}, k={k}: T^k(n) = {val}")

print(f"Total violations: {max_violations}")

# ============================================================
# Part 7: syracuse_odd lemma analysis
# ============================================================
print("\n" + "=" * 60)
print("Part 7: Why syracuse(n) is always odd")
print("=" * 60)

print("""
By definition:
  syracuse(n) = (3n+1) / 2^v2(3n+1)

Since v2(m) counts ALL factors of 2, after dividing by 2^v2(m),
the result is always odd (when m > 0).

This is a basic property of v2: m / 2^v2(m) is odd for m > 0.

We need:
  odd_div_pow_v2 (m : Nat) (hm : m > 0) : (m / 2^v2(m)) % 2 = 1
""")

# Verify
print("Verification: m / 2^v2(m) is always odd for m = 1..1000:")
all_good = True
for m in range(1, 1001):
    result = m >> v2(m)
    if result % 2 != 1:
        print(f"  FAIL at m={m}: {m}/2^{v2(m)} = {result}")
        all_good = False
if all_good:
    print("  All verified!")

# ============================================================
# Part 8: The stronger 3^k digit claim
# ============================================================
print("\n" + "=" * 60)
print("Part 8: Re-examining 3-adic digit claim with correction")
print("=" * 60)

print("Checking T^k(n) mod 3^j for various j <= k:")
for n in [1, 3, 5, 7, 11, 15, 27]:
    print(f"\n  n = {n}:")
    val = n
    for k in range(1, 8):
        val = syracuse(val)
        for j in range(1, k+1):
            residue = val % (3**j)
            digits = base3_digits(residue, j)
            has_zero = 0 in digits
            if has_zero:
                print(f"    k={k}, mod 3^{j}: digits={digits} ** HAS ZERO **")

print("\nT^k(n) itself in base 3:")
for n in [1, 3, 5, 7]:
    print(f"\n  n = {n}:")
    val = n
    for k in range(1, 10):
        val = syracuse(val)
        # Full base 3 representation
        tmp = val
        digits_full = []
        while tmp > 0:
            digits_full.append(tmp % 3)
            tmp //= 3
        digits_full.reverse()
        has_zero = 0 in digits_full
        print(f"    T^{k}(n)={val:>8}, base3={digits_full}, has_zero={has_zero}")

print("\n\nCounting how many T^k values have digit 0 in full base-3 representation:")
total = 0
with_zero = 0
for n in range(1, 500, 2):
    val = n
    for k in range(1, 30):
        val = syracuse(val)
        total += 1
        tmp = val
        while tmp > 0:
            if tmp % 3 == 0:
                with_zero += 1
                break
            tmp //= 3

print(f"  Total checks: {total}")
print(f"  With digit 0 in full base-3: {with_zero}")
print(f"  Ratio: {with_zero/total:.4f}")
print("  --> The full base-3 digit-0-free claim is FALSE for larger numbers.")
print("  --> The correct claim is only about the LEAST SIGNIFICANT digit: T^k(n) mod 3 != 0")
