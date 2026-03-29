"""
探索: C_k閉形式 T^k(n) mod 3^k の形式化分析 (v2)

正しい公式の導出:
T(n) = (3n+1) / 2^{v_1}   where v_1 = v2(3n+1)

T^2(n) = T(T(n)) = (3 T(n) + 1) / 2^{v_2}   where v_2 = v2(3 T(n) + 1)
       = (3(3n+1)/2^{v_1} + 1) / 2^{v_2}
       = (3(3n+1) + 2^{v_1}) / (2^{v_1} * 2^{v_2})
       = (3^2 n + 3 + 2^{v_1}) / 2^{S_2}   where S_2 = v_1 + v_2
       = (9n + 3 + 2^{v_1}) / 2^{S_2}

一般に:
T^k(n) = (3^k n + C_k) / 2^{S_k}

ここで C_k は漸化式:
C_0 = 0
C_{k+1} = 3 C_k + 2^{S_k}   (where S_k = v_1 + ... + v_k)

閉形式: C_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i}
       = sum_{i=1}^{k} 3^{k-i} * 2^{S_{i-1}}
(ここで S_0 = 0)
"""

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

def compute_v2_sequence(n, k):
    vs = []
    cur = n
    for _ in range(k):
        v = v2(3 * cur + 1)
        vs.append(v)
        cur = syracuse(cur)
    return vs

def compute_Ck_correct(vs, k):
    """
    C_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i}

    Recurrence: C_0 = 0, C_{k+1} = 3*C_k + 2^{S_k}
    """
    Ss = [0]
    for i in range(k):
        Ss.append(Ss[-1] + vs[i])

    result = 0
    for i in range(k):
        result += 3**(k-1-i) * 2**Ss[i]

    return result

def verify_Tk_formula(n, k):
    vs = compute_v2_sequence(n, k)
    Ck = compute_Ck_correct(vs, k)
    Sk = sum(vs)

    Tk_actual = syracuse_iter(k, n)
    numerator = 3**k * n + Ck

    assert numerator % 2**Sk == 0, f"Not divisible for n={n}, k={k}: {numerator} % {2**Sk} = {numerator % 2**Sk}"
    Tk_formula = numerator // 2**Sk
    assert Tk_actual == Tk_formula, f"Formula mismatch for n={n}, k={k}: {Tk_actual} vs {Tk_formula}"

    return True

print("=" * 70)
print("Step 1: Verify T^k(n) = (3^k n + C_k) / 2^{S_k}")
print("=" * 70)
for k in range(1, 6):
    for n in range(1, 100, 2):
        verify_Tk_formula(n, k)
    print(f"  k={k}: All odd n in [1,99] verified!")

print("\n" + "=" * 70)
print("Step 2: Derive T^k(n) mod 3^k")
print("=" * 70)
print("""
T^k(n) = (3^k n + C_k) / 2^{S_k}

mod 3^k:  3^k n ≡ 0 (mod 3^k)

So T^k(n) ≡ C_k / 2^{S_k} (mod 3^k)
          = C_k * (2^{S_k})^{-1} (mod 3^k)
          = (sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i}) * 2^{-S_k} (mod 3^k)
          = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i - S_k} (mod 3^k)
          = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{-(S_k - S_i)} (mod 3^k)

Let j = k-1-i (so i = k-1-j, j goes from 0 to k-1):
          = sum_{j=0}^{k-1} 3^j * 2^{-(S_k - S_{k-1-j})} (mod 3^k)
          = sum_{j=0}^{k-1} 3^j * 2^{-(v_{k-j} + ... + v_k)} (mod 3^k)

Or equivalently with original indexing:
          = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{-(v_{i+1} + ... + v_k)} (mod 3^k)

This depends ONLY on v2 sequence (v_1, ..., v_k)!
""")

def compute_mod3k_from_v2seq(vs, k):
    """
    T^k(n) mod 3^k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i - S_k} mod 3^k
    """
    mod3k = 3**k
    if mod3k <= 1:
        return 0

    Ss = [0]
    for v in vs:
        Ss.append(Ss[-1] + v)
    Sk = Ss[k]

    result = 0
    for i in range(k):
        exp = Ss[i] - Sk  # S_i - S_k (negative)
        inv_2_power = pow(2, exp, mod3k)  # Python handles negative exp as modular inverse
        result = (result + pow(3, k-1-i, mod3k) * inv_2_power) % mod3k

    return result

print("\n" + "=" * 70)
print("Step 3: Verify the modular formula")
print("=" * 70)
for k in range(1, 6):
    mod3k = 3**k
    all_ok = True
    for n in range(1, 500, 2):
        vs = compute_v2_sequence(n, k)
        Tk = syracuse_iter(k, n)
        actual = Tk % mod3k
        predicted = compute_mod3k_from_v2seq(vs, k)
        if actual != predicted:
            all_ok = False
            print(f"  FAIL k={k}, n={n}: actual={actual}, predicted={predicted}, vs={vs}")
    if all_ok:
        print(f"  k={k}: All 250 odd numbers verified!")

print("\n" + "=" * 70)
print("Step 4: Verify v2-sequence independence")
print("=" * 70)
from collections import defaultdict
for k in range(1, 5):
    mod3k = 3**k
    v2seq_to_mods = defaultdict(set)
    for n in range(1, 1000, 2):
        vs = compute_v2_sequence(n, k)
        Tk = syracuse_iter(k, n)
        v2seq_to_mods[tuple(vs)].add(Tk % mod3k)

    all_unique = all(len(mods) == 1 for mods in v2seq_to_mods.values())
    print(f"  k={k}: {len(v2seq_to_mods)} distinct v2-sequences, "
          f"all map to unique mod 3^k value: {all_unique}")

    # Show some examples
    for seq in sorted(v2seq_to_mods.keys())[:5]:
        mods = v2seq_to_mods[seq]
        print(f"    v2_seq={seq}: mod 3^{k} = {sorted(mods)}")

print("\n" + "=" * 70)
print("Step 5: Induction step analysis")
print("=" * 70)
print("""
INDUCTION PROOF STRUCTURE:

Goal: T^k(n) mod 3^k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{S_i - S_k} mod 3^k

Equivalent to: 2^{S_k} * T^k(n) mod 3^k = C_k mod 3^k
            i.e., 2^{S_k} * T^k(n) ≡ C_k (mod 3^k)

Since 2^{S_k} * T^k(n) = 3^k * n + C_k  (exact equality),
we have 2^{S_k} * T^k(n) ≡ C_k (mod 3^k) trivially.

So the whole thing reduces to:
  T^k(n) = (3^k n + C_k) / 2^{S_k}

which is proved by induction:

Base: T^0(n) = n = (1 * n + 0) / 1  (trivially)

Step: T^{k+1}(n) = T(T^k(n))
  Let m = T^k(n) = (3^k n + C_k) / 2^{S_k}  (IH)

  T(m) = (3m + 1) / 2^{v_{k+1}}
       = (3(3^k n + C_k)/2^{S_k} + 1) / 2^{v_{k+1}}
       = (3^{k+1} n + 3 C_k + 2^{S_k}) / (2^{S_k} * 2^{v_{k+1}})
       = (3^{k+1} n + C_{k+1}) / 2^{S_{k+1}}

  where C_{k+1} = 3 C_k + 2^{S_k}  (recurrence)
  and S_{k+1} = S_k + v_{k+1}

KEY: The step "3(3^k n + C_k)/2^{S_k} + 1 = (3^{k+1} n + 3C_k + 2^{S_k}) / 2^{S_k}"
requires that 2^{S_k} | (3^k n + C_k), i.e., the intermediate values are exact integers.
This is guaranteed by the definition of T^k(n).

For the Lean formalization, the MULTIPLICATION FORM is key:
  2^{S_k} * T^k(n) = 3^k * n + C_k

This avoids division entirely!
""")

# Step 6: Design the Lean formalization
print("\n" + "=" * 70)
print("Step 6: Lean formalization design")
print("=" * 70)
print("""
LEAN FORMALIZATION PLAN

=== Definitions ===

-- v2 sequence for k steps starting from n
def v2Seq (n : Nat) : Nat -> Nat
  | 0 => v2 (3 * n + 1)
  | k + 1 => v2Seq (syracuse n) k

-- Cumulative sum S_k = v_1 + ... + v_k
def cumulV2 (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => cumulV2 n k + v2Seq n k

-- C_k constant (depends on v2 sequence)
def ckConst (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => 3 * ckConst n k + 2 ^ cumulV2 n k

=== Main Theorem (Multiplication Form) ===

theorem syracuse_iter_mul_formula_general
    (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    2 ^ cumulV2 n k * syracuseIter k n = 3 ^ k * n + ckConst n k

Proof by induction on k, generalizing n:

Base (k=0):
  2^0 * syracuseIter 0 n = 1 * n = n = 3^0 * n + 0

Step (k -> k+1):
  syracuseIter (k+1) n = syracuseIter k (syracuse n)

  Let m = syracuse n.
  By IH: 2^{cumulV2 m k} * syracuseIter k m = 3^k * m + ckConst m k

  Need: 2^{cumulV2 n (k+1)} * syracuseIter (k+1) n = 3^{k+1} * n + ckConst n (k+1)

  Key relationships:
  (a) cumulV2 n (k+1) = v2(3n+1) + cumulV2 (syracuse n) k
  (b) ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}
  (c) syracuse n * 2^{v2(3n+1)} = 3n + 1  (syracuse_mul_pow_v2)

  But there's a subtlety: v2Seq n j and v2Seq (syracuse n) j need to be related!
  v2Seq n 0 = v2(3n+1) = v_1
  v2Seq n j = v2Seq (syracuse n) (j-1) for j >= 1

  This means:
  cumulV2 n (k+1) = v2Seq n 0 + ... + v2Seq n k
                   = v2(3n+1) + (v2Seq (syracuse n) 0 + ... + v2Seq (syracuse n) (k-1))
                   = v2(3n+1) + cumulV2 (syracuse n) k

  Similarly:
  ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}

  But ckConst n k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{cumulV2 n i}
  ckConst (syracuse n) k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^{cumulV2 (syracuse n) i}

  The key lemma needed:
    ckConst n (k+1) = v2(3n+1) already accounts for the shift...

  Actually let me think of a simpler approach.

=== SIMPLER APPROACH: Direct Recurrence ===

Just prove the recurrence:
  2^{S_{k+1}} * T^{k+1}(n) = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}
  where S_k = cumulV2 n k

This follows from:
  T^{k+1}(n) = T(T^k(n)) = (3 * T^k(n) + 1) / 2^{v_{k+1}}
  => 2^{v_{k+1}} * T^{k+1}(n) = 3 * T^k(n) + 1
  => 2^{S_k} * 2^{v_{k+1}} * T^{k+1}(n) = 2^{S_k} * (3 * T^k(n) + 1)
  => 2^{S_{k+1}} * T^{k+1}(n) = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}

Then by induction:
  Base: 2^0 * T^0(n) = n = 3^0 * n + 0
  Step: 2^{S_{k+1}} * T^{k+1}(n)
      = 3 * (3^k * n + C_k) + 2^{S_k}
      = 3^{k+1} * n + (3 * C_k + 2^{S_k})
      = 3^{k+1} * n + C_{k+1}

This is EXACTLY the structure of the existing syracuse_iter_mul_formula,
but generalized to arbitrary v2 sequences (not just all-1 = consecutive ascents).

=== COROLLARY: mod 3^k independence ===

From 2^{S_k} * T^k(n) = 3^k * n + C_k:
  2^{S_k} * T^k(n) ≡ C_k (mod 3^k)
  T^k(n) ≡ C_k * 2^{-S_k} (mod 3^k)

C_k and S_k both depend only on (v_1, ..., v_k), not on n.
Therefore T^k(n) mod 3^k depends only on the v2 sequence. QED.
""")

# Step 7: Verify relationship to existing ascentConst
print("\n" + "=" * 70)
print("Step 7: Relationship to existing ascentConst")
print("=" * 70)
print("""
When all v_i = 1 (consecutive ascents):
  S_k = k
  C_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^i = (3^k - 2^k) / (3-2) = 3^k - 2^k

This is exactly ascentConst k = 3^k - 2^k!

The existing formula:
  2^k * syracuseIter k n = 3^k * n + ascentConst k
  (when consecutiveAscents n k)

is a SPECIAL CASE of the general formula:
  2^{S_k} * syracuseIter k n = 3^k * n + C_k
  (for all odd n >= 1)

where C_k depends on the v2 sequence.
""")

# Verify the ascentConst relationship
print("Verification: ascentConst vs ckConst when all v_i = 1")
for k in range(1, 6):
    ascent_const = 3**k - 2**k
    # Find an n with k consecutive ascents (n ≡ 2^{k+1}-1 mod 2^{k+1})
    n = 2**(k+1) - 1  # This gives k consecutive ascents
    vs = compute_v2_sequence(n, k)
    all_one = all(v == 1 for v in vs)
    ck = compute_Ck_correct(vs, k)
    print(f"  k={k}: n={n}, vs={vs}, all_v=1: {all_one}, "
          f"C_k={ck}, ascentConst={ascent_const}, match={ck == ascent_const}")

# Step 8: What existing Lean infrastructure is needed
print("\n" + "=" * 70)
print("Step 8: Required Lean infrastructure for formalization")
print("=" * 70)
print("""
EXISTING (available):
  1. syracuse, syracuseIter, v2 - definitions
  2. syracuse_mul_pow_v2: syracuse n * 2^{v2(3n+1)} = 3n+1
  3. syracuse_odd: T(n) % 2 = 1 (for odd n >= 1)
  4. syracuse_pos: T(n) >= 1 (for odd n >= 1)
  5. syracuseIter_odd, syracuseIter_pos
  6. syracuse_mod3_eq: T(n) mod 3 depends on v2(3n+1) parity
  7. v2_mul, v2_odd_mul, v2_two_mul - v2 arithmetic

NEW DEFINITIONS NEEDED:
  1. v2Seq n k: the k-th v2 value in the Syracuse iteration from n
  2. cumulV2 n k: cumulative sum S_k = sum of first k v2 values
  3. ckConst n k: the C_k constant

NEW THEOREMS:
  1. syracuse_iter_general_mul: 2^{S_k} * T^k(n) = 3^k * n + C_k
     (generalization of syracuse_iter_mul_formula)
  2. syracuse_iter_mod3k: T^k(n) mod 3^k = C_k * (2^{S_k})^{-1} mod 3^k
     (corollary: mod 3^k independence from n)

PROOF DIFFICULTY ESTIMATE:
  - v2Seq, cumulV2, ckConst definitions: straightforward (5 lines each)
  - Main theorem (mul form): ~30 lines, induction on k
    Key step uses syracuse_mul_pow_v2
  - Corollary (mod 3^k): ~10 lines, from main theorem + modular arithmetic

TOTAL ESTIMATE: ~80-100 lines of Lean code
""")

# Step 9: Verify the key step in detail
print("\n" + "=" * 70)
print("Step 9: Detailed verification of induction step")
print("=" * 70)
for n in [1, 3, 5, 7, 11, 15, 27, 31]:
    for k in [1, 2, 3]:
        vs = compute_v2_sequence(n, k+1)
        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)

        Ck = compute_Ck_correct(vs[:k], k)
        Ckp1 = compute_Ck_correct(vs[:k+1], k+1)

        # Verify recurrence: C_{k+1} = 3 * C_k + 2^{S_k}
        rhs = 3 * Ck + 2**Ss[k]
        match = Ckp1 == rhs

        # Verify shift: Ck computed from (syracuse n) matches
        m = syracuse(n)
        vs_m = compute_v2_sequence(m, k)
        Ck_from_m = compute_Ck_correct(vs_m, k)

        # The Ck for the original n at step k uses vs[0:k]
        # But C_k computed from m = T(n) uses v2Seq starting from m

        if n <= 7:
            print(f"  n={n}, k={k}: vs={vs[:k+1]}, C_k={Ck}, C_{{k+1}}={Ckp1}, "
                  f"3*C_k+2^S_k={rhs}, match={match}")
            print(f"    T(n)={m}, vs_from_T(n)={vs_m}, C_k_from_T(n)={Ck_from_m}")
            # Check that vs[1:k+1] == vs_m
            print(f"    vs[1:k+1]={vs[1:k+1]}, vs_m={vs_m}, shift_match={vs[1:k+1] == vs_m}")

print("\nDone!")
