"""
Lean形式化の詳細設計: 帰納ステップのシフト補題
"""

print("""
======================================================================
LEAN 4 FORMALIZATION: COMPLETE DESIGN
======================================================================

=== Phase 1: Definitions (v2Seq, cumulV2, ckConst) ===

/-! ## v2列と累積和 -/

/-- v2列: n から Syracuse 反復した際の各ステップの v2 値。
    v2Seq n 0 = v2(3n+1),  v2Seq n k = v2Seq (syracuse n) (k-1) -/
def v2Seq (n : Nat) : Nat -> Nat
  | 0 => v2 (3 * n + 1)
  | k + 1 => v2Seq (syracuse n) k

/-- 累積v2和: S_k = v2Seq n 0 + ... + v2Seq n (k-1) -/
def cumulV2 (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => cumulV2 n k + v2Seq n k
-- Note: cumulV2 n k = v_1 + ... + v_k (sum of first k terms)

/-- C_k定数: T^k(n)の閉形式における定数項。
    C_0 = 0, C_{k+1} = 3 * C_k + 2^{S_k} -/
def ckConst (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => 3 * ckConst n k + 2 ^ cumulV2 n k

=== Phase 2: Shift Lemmas ===

KEY INSIGHT: v2Seq, cumulV2, ckConst are defined relative to starting point n.
When we apply the induction hypothesis to m = syracuse n, we need:

(Shift-1) v2Seq n (k+1) = v2Seq (syracuse n) k
  -- This is DEFINITIONAL (from the recursive definition of v2Seq)

(Shift-2) cumulV2 n (k+1) = v2Seq n 0 + cumulV2 (syracuse n) k
  -- Proof sketch:
  -- cumulV2 n (k+1) = cumulV2 n k + v2Seq n k  (by def)
  -- Need to show: this equals v2Seq n 0 + cumulV2 (syracuse n) k
  -- Actually: cumulV2 n (k+1) = sum_{j=0}^{k} v2Seq n j
  --         = v2Seq n 0 + sum_{j=1}^{k} v2Seq n j
  --         = v2Seq n 0 + sum_{j=0}^{k-1} v2Seq (syracuse n) j  (by Shift-1)
  --         = v2Seq n 0 + cumulV2 (syracuse n) k
  -- This requires an auxiliary lemma or a direct induction on k.

  ALTERNATIVE (simpler): Define cumulV2 differently!
  -- cumulV2 n 0 = 0
  -- cumulV2 n (k+1) = v2Seq n 0 + cumulV2 (syracuse n) k
  -- This makes Shift-2 DEFINITIONAL.
  -- But then we need to verify: this equals the original definition.

  Actually the SIMPLEST approach: directly define via the same recursion pattern.

(Shift-3) ckConst n (k+1) is related to ckConst (syracuse n) k
  -- ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}
  -- But we actually DON'T need a shift lemma for ckConst!
  -- The induction proof uses the RECURRENCE directly.

=== Phase 3: Main Theorem ===

theorem syracuse_iter_general_mul (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    2 ^ cumulV2 n k * syracuseIter k n = 3 ^ k * n + ckConst n k := by
  induction k generalizing n with
  | zero =>
    -- 2^0 * T^0(n) = 1 * n = n = 3^0 * n + 0
    simp [cumulV2, ckConst, syracuseIter]
  | succ k ih =>
    -- syracuseIter (k+1) n = syracuseIter k (syracuse n)
    simp only [syracuseIter_succ]
    -- Let m = syracuse n
    set m := syracuse n with hm_def
    -- m is odd and >= 1
    have hm_pos : m >= 1 := syracuse_pos n hn hodd
    have hm_odd : m % 2 = 1 := syracuse_odd n hn hodd
    -- IH: 2^{cumulV2 m k} * syracuseIter k m = 3^k * m + ckConst m k
    have ih_m := ih m hm_pos hm_odd

    -- KEY STEP: relate cumulV2 n (k+1) and ckConst n (k+1)
    -- to cumulV2 m k and ckConst m k

    -- Step A: cumulV2 n (k+1) = v2(3n+1) + cumulV2 m k
    have h_cumul : cumulV2 n (k + 1) = v2 (3 * n + 1) + cumulV2 m k := by
      -- Need the shift lemma here
      sorry  -- (this is the key lemma to prove)

    -- Step B: The recurrence for ckConst
    -- ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}
    -- But this uses ckConst n k, not ckConst m k!

    -- PROBLEM: The IH gives us information about ckConst m k,
    -- but we need information about ckConst n (k+1).
    -- These are DIFFERENT things!

    -- SOLUTION: Don't try to relate them. Instead, use the
    -- RECURRENCE approach directly.

    -- From syracuse_mul_pow_v2: m * 2^{v2(3n+1)} = 3n + 1
    have h_syr := syracuse_mul_pow_v2 n
    -- h_syr: syracuse n * 2^{v2(3n+1)} = 3n + 1

    -- From IH (rewritten):
    -- 2^{cumulV2 m k} * syracuseIter k m = 3^k * m + ckConst m k

    -- Goal: 2^{cumulV2 n (k+1)} * syracuseIter k m = 3^{k+1} * n + ckConst n (k+1)

    -- Multiply IH by 2^{v2(3n+1)}:
    -- 2^{v2(3n+1)} * 2^{cumulV2 m k} * syracuseIter k m
    --   = 2^{v2(3n+1)} * (3^k * m + ckConst m k)
    --   = 3^k * (2^{v2(3n+1)} * m) + 2^{v2(3n+1)} * ckConst m k
    --   = 3^k * (3n + 1) + 2^{v2(3n+1)} * ckConst m k
    --   = 3^{k+1} * n + 3^k + 2^{v2(3n+1)} * ckConst m k

    -- For this to equal 3^{k+1} * n + ckConst n (k+1),
    -- we need: ckConst n (k+1) = 3^k + 2^{v2(3n+1)} * ckConst m k

    -- But ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}

    -- MISMATCH! The recurrence for ckConst n is in terms of ckConst n k,
    -- not ckConst m k.

    sorry

-- THE ISSUE: ckConst is defined relative to the starting point n,
-- so ckConst n k and ckConst (syracuse n) k are different objects
-- with different v2 sequences.

-- We need EITHER:
-- (A) A shift lemma: ckConst n (k+1) = 3^k + 2^{v2(3n+1)} * ckConst (syracuse n) k
--     (relating ckConst at n to ckConst at syracuse n)
-- OR:
-- (B) Reformulate ckConst to be a function of the v2 sequence directly
--     (not implicitly via n)
-- OR:
-- (C) Use a DIFFERENT induction strategy

=== APPROACH C: Direct recurrence induction ===

Instead of generalizing n, we can define an auxiliary function:

/-- Auxiliary: 2^{S_k} * T^k(n) expressed as 3^k * n + C_k -/
-- Prove: for each n, the sequence a_k := 2^{S_k} * T^k(n) satisfies:
-- a_0 = n
-- a_{k+1} = 3 * a_k + 2^{S_k}

-- a_{k+1} = 2^{S_{k+1}} * T^{k+1}(n)
--         = 2^{S_k + v_{k+1}} * T(T^k(n))
--         = 2^{S_k} * (2^{v_{k+1}} * T(T^k(n)))
--         = 2^{S_k} * (3 * T^k(n) + 1)    [by syracuse_mul_pow_v2 applied to T^k(n)]
--         = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}
--         = 3 * a_k + 2^{S_k}

-- Then by induction on k:
-- a_0 = n = 3^0 * n + 0 = 3^0 * n + C_0
-- a_{k+1} = 3 * (3^k * n + C_k) + 2^{S_k}
--         = 3^{k+1} * n + (3 * C_k + 2^{S_k})
--         = 3^{k+1} * n + C_{k+1}

-- The key is that syracuse_mul_pow_v2 applied to T^k(n) gives:
-- T(T^k(n)) * 2^{v2(3*T^k(n)+1)} = 3*T^k(n) + 1

-- and v2(3*T^k(n)+1) = v2Seq n k (by definition of v2Seq!)

-- THIS WORKS! The proof is:

theorem syracuse_iter_general_mul_v2 (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    2 ^ cumulV2 n k * syracuseIter k n = 3 ^ k * n + ckConst n k := by
  induction k with   -- NOTE: do NOT generalize n
  | zero => simp [cumulV2, ckConst]
  | succ k ih =>
    -- Goal: 2^{cumulV2 n (k+1)} * T^{k+1}(n) = 3^{k+1} * n + ckConst n (k+1)

    -- ckConst n (k+1) = 3 * ckConst n k + 2^{cumulV2 n k}
    rw [ckConst]

    -- cumulV2 n (k+1) = cumulV2 n k + v2Seq n k
    rw [cumulV2]

    -- syracuseIter (k+1) n = syracuseIter k (syracuse n)
    rw [syracuseIter_succ]

    -- Now need:
    -- 2^{cumulV2 n k + v2Seq n k} * syracuseIter k (syracuse n)
    --   = 3^{k+1} * n + (3 * ckConst n k + 2^{cumulV2 n k})

    -- PROBLEM: We can't easily apply IH because IH is about n, not syracuse n!

    -- ih: 2^{cumulV2 n k} * syracuseIter k n = 3^k * n + ckConst n k

    -- We need a DIFFERENT induction: generalize BOTH n AND the cumulV2/ckConst.

    sorry

-- SOLUTION: Use the multiplication chain approach.
-- Define the recurrence directly.

-- KEY LEMMA (the recurrence step):
-- 2^{cumulV2 n (k+1)} * T^{k+1}(n) = 3 * (2^{cumulV2 n k} * T^k(n)) + 2^{cumulV2 n k}

-- This follows from:
-- T^{k+1}(n) = T(T^k(n))
-- T^k(n) is odd and >= 1 (by syracuseIter_odd, syracuseIter_pos)
-- syracuse_mul_pow_v2 applied to T^k(n):
--   T(T^k(n)) * 2^{v2(3*T^k(n)+1)} = 3*T^k(n) + 1
-- i.e., T^{k+1}(n) * 2^{v2Seq n k} = 3*T^k(n) + 1
-- Multiply by 2^{cumulV2 n k}:
--   T^{k+1}(n) * 2^{cumulV2 n k + v2Seq n k} = 2^{cumulV2 n k} * (3*T^k(n) + 1)
--   T^{k+1}(n) * 2^{cumulV2 n (k+1)} = 3 * (2^{cumulV2 n k} * T^k(n)) + 2^{cumulV2 n k}

-- This is a DIRECT calculation, no induction on k needed for this step!

-- Then the MAIN theorem follows by SIMPLE induction:

-- WAIT: There's a subtle issue. v2Seq n k is defined as:
-- v2Seq n k = v2(3 * syracuseIter k n + 1) ??? NO!
-- v2Seq n 0 = v2(3*n+1)
-- v2Seq n (k+1) = v2Seq (syracuse n) k
-- So v2Seq n k = v2(3 * T^k(n) + 1)? Let's verify:
-- v2Seq n 0 = v2(3n+1) = v2(3 * T^0(n) + 1) ✓
-- v2Seq n 1 = v2Seq (syracuse n) 0 = v2(3 * syracuse n + 1) = v2(3 * T^1(n) + 1) ✓
-- v2Seq n k = v2(3 * T^k(n) + 1)  (by simple induction on k)

-- LEMMA: v2Seq n k = v2(3 * syracuseIter k n + 1)
-- Proof by induction on k:
-- Base: v2Seq n 0 = v2(3n+1) = v2(3 * syracuseIter 0 n + 1) ✓
-- Step: v2Seq n (k+1) = v2Seq (syracuse n) k
--     = v2(3 * syracuseIter k (syracuse n) + 1)  (IH applied to syracuse n)
--     = v2(3 * syracuseIter (k+1) n + 1)  ✓

-- With this lemma, the recurrence step becomes clear:
-- 2^{cumulV2 n (k+1)} * T^{k+1}(n)
-- = 2^{cumulV2 n k + v2Seq n k} * T^{k+1}(n)
-- = 2^{cumulV2 n k} * 2^{v2Seq n k} * T^{k+1}(n)
-- = 2^{cumulV2 n k} * 2^{v2(3*T^k(n)+1)} * T(T^k(n))
-- = 2^{cumulV2 n k} * (3 * T^k(n) + 1)     [by syracuse_mul_pow_v2 for T^k(n)]
-- = 3 * (2^{cumulV2 n k} * T^k(n)) + 2^{cumulV2 n k}

-- And by IH: 2^{cumulV2 n k} * T^k(n) = 3^k * n + ckConst n k
-- So: = 3 * (3^k * n + ckConst n k) + 2^{cumulV2 n k}
--     = 3^{k+1} * n + (3 * ckConst n k + 2^{cumulV2 n k})
--     = 3^{k+1} * n + ckConst n (k+1)  ✓✓✓

-- THIS WORKS! The key is:
-- 1. Lemma v2Seq_eq_v2_iter: v2Seq n k = v2(3 * syracuseIter k n + 1)
-- 2. The non-generalizing induction on k (keep n fixed!)
-- 3. syracuse_mul_pow_v2 applied to syracuseIter k n

==================================================================
FINAL LEAN PROOF SKETCH
==================================================================

-- Definitions
def v2Seq (n : Nat) : Nat -> Nat
  | 0 => v2 (3 * n + 1)
  | k + 1 => v2Seq (syracuse n) k

def cumulV2 (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => cumulV2 n k + v2Seq n k

def ckConst (n : Nat) : Nat -> Nat
  | 0 => 0
  | k + 1 => 3 * ckConst n k + 2 ^ cumulV2 n k

-- Key lemma 1
theorem v2Seq_eq (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    v2Seq n k = v2 (3 * syracuseIter k n + 1) := by
  induction k generalizing n with
  | zero => simp [v2Seq, syracuseIter]
  | succ k ih =>
    simp [v2Seq, syracuseIter_succ]
    exact ih (syracuse n) (syracuse_pos n hn hodd) (syracuse_odd n hn hodd)

-- Key lemma 2 (recurrence step)
theorem recurrence_step (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    2 ^ cumulV2 n (k+1) * syracuseIter (k+1) n
    = 3 * (2 ^ cumulV2 n k * syracuseIter k n) + 2 ^ cumulV2 n k := by
  simp [cumulV2, syracuseIter_succ, pow_add]
  have hk_odd := syracuseIter_odd n k hn hodd
  have hk_pos := syracuseIter_pos n k hn hodd
  rw [v2Seq_eq n k hn hodd]
  -- Now we need:
  -- 2^{cumulV2 n k} * 2^{v2(3*T^k(n)+1)} * T(T^k(n))
  -- = 3 * (2^{cumulV2 n k} * T^k(n)) + 2^{cumulV2 n k}
  -- i.e., 2^{cumulV2 n k} * (2^{v2(3*m+1)} * T(m)) = 2^{cumulV2 n k} * (3m + 1)
  -- where m = T^k(n)
  -- This follows from syracuse_mul_pow_v2 applied to m
  have h_syr := syracuse_mul_pow_v2 (syracuseIter k n)
  -- h_syr: syracuse(T^k(n)) * 2^{v2(3*T^k(n)+1)} = 3*T^k(n)+1
  ring_nf  -- or linarith/omega after suitable rewriting
  sorry  -- details need careful ring lemmas

-- Main theorem
theorem syracuse_iter_general_mul (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    2 ^ cumulV2 n k * syracuseIter k n = 3 ^ k * n + ckConst n k := by
  induction k with
  | zero => simp [cumulV2, ckConst, syracuseIter]
  | succ k ih =>
    rw [recurrence_step n k hn hodd]
    rw [ih]
    simp [ckConst, pow_succ]
    ring

-- Corollary: mod 3^k
theorem syracuse_iter_mod3k (n k : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    (2 ^ cumulV2 n k * syracuseIter k n) % 3 ^ k = ckConst n k % 3 ^ k := by
  rw [syracuse_iter_general_mul n k hn hodd]
  omega  -- or: simp [Nat.add_mul_mod_self]

-- The v2-independence theorem:
-- Since ckConst n k and cumulV2 n k depend on n only through v2Seq,
-- and v2Seq determines a unique residue T^k(n) mod 3^k,
-- two starting points with the same v2 sequence give the same residue mod 3^k.
""")

# Verify the recurrence step numerically
print("\n\nNumerical verification of recurrence step:")
print("2^{S_{k+1}} * T^{k+1}(n) = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}")
for n in [1, 3, 5, 7, 11, 15]:
    for k in range(5):
        vs = compute_v2_sequence(n, k + 1)
        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)

        Tk = syracuse_iter(k, n)
        Tkp1 = syracuse_iter(k + 1, n)

        lhs = 2**Ss[k+1] * Tkp1
        rhs = 3 * (2**Ss[k] * Tk) + 2**Ss[k]

        match = "OK" if lhs == rhs else "FAIL"
        if n <= 7:
            print(f"  n={n}, k={k}: LHS={lhs}, RHS={rhs} [{match}]")

def v2_val(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

# Also verify v2Seq_eq
print("\nVerify v2Seq(n, k) = v2(3 * T^k(n) + 1):")
for n in [1, 3, 5, 7]:
    for k in range(5):
        vs = compute_v2_sequence(n, k + 1)
        Tk = syracuse_iter(k, n)
        v2seq_k = vs[k]
        v2_direct = v2_val(3 * Tk + 1)
        match = "OK" if v2seq_k == v2_direct else "FAIL"
        print(f"  n={n}, k={k}: v2Seq(n,{k})={v2seq_k}, v2(3*T^{k}(n)+1)={v2_direct} [{match}]")
