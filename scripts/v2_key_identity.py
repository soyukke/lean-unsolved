"""
核心的等式の証明:
  3 * (4^m - 1)/3 + 1 = 4^m
  即ち 4^m - 1 + 1 = 4^m (自明!)

そして 4^m = 2^{2m} なので:
  2^{2m} | (3 * residue_{2m} + 1)  かつ  2^{2m+1} | (3 * residue_{2m+1} + 1)

residue_k = (4^{ceil(k/2)} - 1) / 3 において:
  k = 2m:   3 * residue + 1 = 3 * (4^m - 1)/3 + 1 = 4^m = 2^{2m}
            よって 2^{2m} | (3*residue+1) だが 2^{2m+1} ∤ (3*residue+1)
  k = 2m+1: residue = (4^{m+1} - 1)/3 なので
            3 * residue + 1 = 4^{m+1} = 2^{2m+2}
            よって 2^{2m+2} | (3*residue+1) >= 2^{2m+1}

つまり:
  residue_{2m} = (4^m - 1)/3:   v2(3*r+1) = 2m (exact)
  residue_{2m+1} = (4^{m+1}-1)/3: v2(3*r+1) = 2m+2 >= 2m+1

Wait, let me recheck...
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

import math

print("=" * 60)
print("Key identity verification")
print("=" * 60)

for k in range(1, 17):
    m = math.ceil(k / 2)
    residue = (4**m - 1) // 3
    val = 3 * residue + 1
    v2_val = v2(val)
    print(f"  k={k:2d}: residue = (4^{m}-1)/3 = {residue:6d}, 3r+1 = {val:6d} = 2^{v2_val}, v2={v2_val}, v2>={k}: {v2_val >= k}")

print()
print("=" * 60)
print("Crucial observation")
print("=" * 60)
print()
print("3 * (4^m - 1)/3 + 1 = 4^m - 1 + 1 = 4^m = 2^{2m}")
print()
print("So v2(3 * residue_k + 1) = 2m where m = ceil(k/2)")
print()
print("For k = 2m:   v2 = 2m >= 2m = k  (exact match)")
print("For k = 2m+1: v2 = 2(m+1) = 2m+2 >= 2m+1 = k  (one extra)")
print()
print("This means residue_k works for BOTH even and odd k!")
print()

# Now let's verify the uniqueness
print("=" * 60)
print("Uniqueness check: residue_k is the UNIQUE r < 2^k with 2^k | (3r+1)")
print("=" * 60)
print()

for k in range(1, 10):
    mod = 2**k
    m = math.ceil(k / 2)
    residue = (4**m - 1) // 3
    # Check: residue < 2^k?
    print(f"  k={k}: residue = {residue}, 2^k = {mod}, residue < 2^k: {residue < mod}, residue % 2^k = {residue % mod}")

print()
print("=" * 60)
print("Important: residue_{2m+1} may exceed 2^{2m+1}")
print("=" * 60)
print()

# k=1: residue = (4-1)/3 = 1, 2^1 = 2, 1 < 2: OK
# k=3: residue = (16-1)/3 = 5, 2^3 = 8, 5 < 8: OK
# k=5: residue = (64-1)/3 = 21, 2^5 = 32, 21 < 32: OK
# k=7: residue = (256-1)/3 = 85, 2^7 = 128, 85 < 128: OK
# General: for k = 2m+1, residue = (4^{m+1}-1)/3 < 4^{m+1}/3 < 2^{2m+2}/3
#          2^k = 2^{2m+1}
#          Need: 2^{2m+2}/3 < 2^{2m+1} iff 2/3 < 1, TRUE

print("For k = 2m+1: residue = (4^{m+1}-1)/3 < 4^{m+1}/3 = 2^{2m+2}/3")
print("  2^k = 2^{2m+1}")
print("  residue/2^k < 2^{2m+2}/(3 * 2^{2m+1}) = 2/3 < 1")
print("  So residue < 2^k always holds")
print()
print("For k = 2m: residue = (4^m-1)/3 < 4^m/3 = 2^{2m}/3")
print("  2^k = 2^{2m}")
print("  residue/2^k < 1/3 < 1")
print("  Also OK")
print()

# Summary of the proof structure
print("=" * 60)
print("COMPLETE PROOF STRUCTURE")
print("=" * 60)
print()
print("""
===========================================================
Theorem: v2(3n+1) >= k  <=>  n % 2^k = (4^{ceil(k/2)}-1)/3
===========================================================

Define: collatzResidue (k : Nat) := (4^((k+1)/2) - 1) / 3
  (where (k+1)/2 is integer division, = ceil(k/2))

Key properties to prove:

(A) 3 * collatzResidue k + 1 = 4^((k+1)/2) = 2^(2*((k+1)/2))
    Proof: Immediate from (4^m - 1)/3 * 3 = 4^m - 1

(B) 2^k | 3 * collatzResidue k + 1
    Proof: 3r+1 = 2^{2*ceil(k/2)} and 2*ceil(k/2) >= k

(C) collatzResidue k < 2^k
    Proof: collatzResidue k = (4^m-1)/3 < 4^m/3 <= 2^k (when 2m >= k)

(D) v2(m) >= k <=> 2^k | m  (for m > 0)
    Proof: Induction on k, using v2 definition

(E) Main theorem: v2(3n+1) >= k <=> n % 2^k = collatzResidue k
    Proof:
      v2(3n+1) >= k
      <=> 2^k | (3n+1)                    [by (D)]
      <=> (3n+1) % 2^k = 0                [Nat.dvd_iff_mod_eq_zero]
      <=> 3n = -1 (mod 2^k)               [basic mod arithmetic]
      <=> n = collatzResidue k (mod 2^k)   [since 3 is invertible mod 2^k]

    The last step uses:
      3 * collatzResidue k + 1 = 0 (mod 2^k)  [by (B)]
      and uniqueness of solution mod 2^k       [since gcd(3, 2^k) = 1]

===========================================================
Recovery of existing lemmas:
===========================================================

k=1: collatzResidue 1 = (4^1-1)/3 = 1
     v2(3n+1) >= 1 <=> n % 2 = 1  (n is odd)

k=2: collatzResidue 2 = (4^1-1)/3 = 1
     v2(3n+1) >= 2 <=> n % 4 = 1  (recovers v2_ge_two_of_mod4_eq1)

k=3: collatzResidue 3 = (4^2-1)/3 = 5
     v2(3n+1) >= 3 <=> n % 8 = 5  (recovers v2_ge_three_of_mod8_eq5)

k=4: collatzResidue 4 = (4^2-1)/3 = 5
     v2(3n+1) >= 4 <=> n % 16 = 5

k=5: collatzResidue 5 = (4^3-1)/3 = 21
     v2(3n+1) >= 5 <=> n % 32 = 21

===========================================================
Exact v2 values (combining >= k and < k+1):
===========================================================

v2(3n+1) = 1 <=> n%4 in {3,7}  (n%4=3 or n%4=7, i.e., n%2=1 and n%4 != 1)
  which simplifies to n%4 = 3

v2(3n+1) = 2 <=> n%8 = 1  (n%4=1 and n%8 != 5)

v2(3n+1) = 3 <=> n%16 = 13  (n%8=5 and n%16 != 5)

v2(3n+1) = 4 <=> n%32 = 5   (n%16=5 and n%32 != 21)
""")

# Exact v2 values
print()
print("=" * 60)
print("Exact v2 value table")
print("=" * 60)
for k in range(1, 9):
    mod2 = 2**(k+1)
    exact = []
    for r in range(mod2):
        if v2(3*r+1) == k:
            exact.append(r)
    print(f"  v2(3n+1) = {k}: n mod {mod2} in {exact}")

print()
print("=" * 60)
print("Lean-friendly collatzResidue definition")
print("=" * 60)
print()
print("def collatzResidue (k : Nat) : Nat := (4 ^ ((k + 1) / 2) - 1) / 3")
print()
print("Or equivalently via recurrence:")
print("  collatzResidue 0 = 0")
print("  collatzResidue (2*m+1) = collatzResidue (2*m) + 4^m  (= (4^{m+1}-1)/3)")
print("  collatzResidue (2*m+2) = collatzResidue (2*m+1)      (same)")
print()
print("Actually simpler recurrence:")
print("  collatzResidue 0 = 0")
print("  collatzResidue 1 = 1")
print("  collatzResidue (k+2) = 4 * collatzResidue k + 1  (when k is odd, i.e. k+2 is odd)")
print()

# Verify the simpler recurrence
print("Verification:")
residues_by_closed = {}
for k in range(0, 17):
    m = math.ceil(k / 2) if k > 0 else 0
    residues_by_closed[k] = (4**m - 1) // 3 if k > 0 else 0

for k in range(0, 15):
    r = residues_by_closed[k]
    if k + 2 <= 16:
        r2 = residues_by_closed[k+2]
        if k % 2 == 1:
            predicted = 4 * r + 1  # works when k is odd
            print(f"  k={k}: collatzResidue({k+2}) = 4*collatzResidue({k})+1 = 4*{r}+1 = {predicted}, actual = {r2}, match: {predicted == r2}")
        else:
            # k is even, k+2 is even
            predicted = 4 * residues_by_closed[k+1] + 1
            print(f"  k={k}: collatzResidue({k+2}) via k+1: 4*collatzResidue({k+1})+1 = 4*{residues_by_closed[k+1]}+1 = {predicted}, actual = {r2}, match: {predicted == r2}")
