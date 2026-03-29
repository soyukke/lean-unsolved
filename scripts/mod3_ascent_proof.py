"""
連続上昇 => T^k(n) % 3 = 2 の証明構造の精密分析

核心: 上昇ステップ ⟺ v2(3n+1) = 1 ⟺ n ≡ 3 (mod 4)
v2 = 1 は奇数なので syracuse_mod3_eq により T(n) % 3 = 2

帰納法: k回連続上昇のとき、各 T^i(n) で v2 = 1 なので T^i(n) % 3 = 2
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
    return m // (2 ** v2(m))

print("=" * 70)
print("PROOF: k consecutive ascents => T^k(n) % 3 = 2 for all k")
print("=" * 70)

print("""
Theorem: consecutive_ascent_mod3_always_two
  For any odd n >= 1 and k >= 1, if
    consecutiveAscents n k
  (meaning T^i(n) > T^{i-1}(n) for each step 0..k-1),
  then T^k(n) % 3 = 2.

Proof by induction on k:

Base case (k=1):
  consecutiveAscents n 1 means syracuse n > n.
  By syracuse_ascent_iff_mod4_eq3: n % 4 = 3.
  By v2_three_mul_add_one_of_mod4_eq3: v2(3n+1) = 1.
  Since 1 % 2 = 1 (odd), syracuse_mod3_eq gives T(n) % 3 = 2.

Inductive step (k -> k+1):
  Assume consecutiveAscents n (k+1).
  By consecutiveAscents_head: syracuse n > n.
  By syracuse_ascent_iff_mod4_eq3: n % 4 = 3.
  So T(n) % 3 = 2 (base case).

  By consecutiveAscents_shift: consecutiveAscents (syracuse n) k.
  By IH: T^k(syracuse n) % 3 = 2.
  But T^k(syracuse n) = T^{k+1}(n) = syracuseIter (k+1) n.
  So T^{k+1}(n) % 3 = 2.

QED.

Note: The key insight is that each ascent step FORCES v2 = 1 (odd),
which FORCES mod 3 = 2. This is a chain of deterministic consequences.
""")

print()
print("=" * 70)
print("PROOF: Alternative direct proof using v2 = 1 characterization")
print("=" * 70)

print("""
Alternative, more direct proof:

Lemma: ascent_implies_v2_one
  If syracuse n > n (n odd, n >= 1), then v2(3n+1) = 1.
  Proof: syracuse_ascent_iff_mod4_eq3 gives n%4=3,
         then v2_three_mul_add_one_of_mod4_eq3 gives v2=1.

Main theorem:
  consecutiveAscents n k means for each i < k:
    syracuseIter (i+1) n > syracuseIter i n.
  In particular, for the LAST step (i = k-1):
    syracuse (syracuseIter (k-1) n) > syracuseIter (k-1) n.
  By ascent_implies_v2_one:
    v2(3 * syracuseIter (k-1) n + 1) = 1.
  Since 1 is odd, syracuse_mod3_eq gives:
    syracuse (syracuseIter (k-1) n) % 3 = 2.
  But syracuse (syracuseIter (k-1) n) = syracuseIter k n.
  So syracuseIter k n % 3 = 2.

QED (no induction needed!).
""")

# 検証: この「最後のステップのv2=1」論法
print("Verification: last step v2=1 argument")
for k in range(1, 8):
    mod_val = 2**(k+1)
    start = mod_val - 1
    all_ok = True
    for n in range(start, 50000, mod_val):
        # Check that the last ascent step has v2=1
        x = n
        for _ in range(k-1):
            x = syracuse(x)
        # x = T^{k-1}(n), check v2(3x+1) = 1
        v = v2(3*x+1)
        if v != 1:
            all_ok = False
            print(f"  FAIL: k={k}, n={n}, T^{k-1}(n)={x}, v2(3x+1)={v}")
            break
    if all_ok:
        print(f"  k={k}: All last ascent steps have v2=1 [VERIFIED]")

print()
print("=" * 70)
print("LEAN 4 PROOF SKETCH for syracuse_ascent_mod3")
print("=" * 70)

print("""
-- Priority 1: Direct corollary
/-- 上昇ステップでの mod 3 挙動: T(n) ≡ 2 (mod 3) -/
theorem syracuse_ascent_mod3 (n : ℕ) (hn : n % 2 = 1) (hn1 : n ≥ 1)
    (hasc : syracuse n > n) : syracuse n % 3 = 2 := by
  have hmod4 := (syracuse_ascent_iff_mod4_eq3 n hn1 hn).mp hasc
  have hv2 := v2_three_mul_add_one_of_mod4_eq3 n hmod4
  rw [syracuse_mod3_eq n hn, hv2]
  simp
  -- or: decide / norm_num / omega

-- Priority 2: consecutive ascent version
/-- k回連続上昇なら T^k(n) ≡ 2 (mod 3) -/
theorem consecutive_ascent_mod3_two (n k : ℕ) (hn : n % 2 = 1) (hn1 : n ≥ 1)
    (hk : k ≥ 1) (hasc : consecutiveAscents n k) :
    syracuseIter k n % 3 = 2 := by
  -- The last step is an ascent
  have h_last := hasc (k-1) (by omega)
  -- syracuseIter k n = syracuse (syracuseIter (k-1) n)
  -- ... (needs to establish oddness and positivity of syracuseIter (k-1) n)
  -- Then apply syracuse_ascent_mod3
  sorry -- needs helper lemmas about oddness preservation

-- Priority 1b: Iff versions
/-- T(n) ≡ 2 (mod 3) iff v2(3n+1) is odd -/
theorem syracuse_mod3_eq_two_iff (n : ℕ) (hn : n % 2 = 1) :
    syracuse n % 3 = 2 ↔ v2 (3 * n + 1) % 2 = 1 := by
  rw [syracuse_mod3_eq n hn]
  split_ifs with h <;> omega

/-- T(n) ≡ 1 (mod 3) iff v2(3n+1) is even -/
theorem syracuse_mod3_eq_one_iff (n : ℕ) (hn : n % 2 = 1) :
    syracuse n % 3 = 1 ↔ v2 (3 * n + 1) % 2 = 0 := by
  rw [syracuse_mod3_eq n hn]
  split_ifs with h <;> omega
""")

print()
print("=" * 70)
print("SUMMARY: mod 9 table structure")
print("=" * 70)

# mod 9 テーブルの美しい構造
print("""
T(n) % 9 complete classification:

  Let a = n % 3, v = v2(3n+1) % 6.
  Let base = [1, 4, 7][a]  (= (3n+1) mod 9)
  Let inv  = [1, 5, 7, 8, 4, 2][v]  (= inverse of 2^v mod 9)
  Then T(n) % 9 = (base * inv) % 9.

  Beautiful pattern: the table rows are cyclic permutations of [1,5,7,8,4,2]!

  v2%6:  0  1  2  3  4  5
  n%3=0: 1  5  7  8  4  2    (starts at index 0)
  n%3=1: 4  2  1  5  7  8    (starts at index 2, shifted by 2)
  n%3=2: 7  8  4  2  1  5    (starts at index 4, shifted by 4)

  This is because:
  - base values [1, 4, 7] correspond to indices [0, 2, 4] in the cycle [1, 2, 4, 8, 7, 5]
    (well, in the inverse cycle [1, 5, 7, 8, 4, 2])
  - Multiplying by a fixed base shifts the cyclic sequence

  The non-zero residues mod 9 that appear: {1, 2, 4, 5, 7, 8}
  These are exactly the residues coprime to 3!
""")

# 最終確認
print("Final verification of the cyclic structure:")
cycle = [1, 5, 7, 8, 4, 2]
for a in range(3):
    base_val = [1, 4, 7][a]
    row = []
    for v6 in range(6):
        inv_val = [1, 5, 7, 8, 4, 2][v6]
        val = (base_val * inv_val) % 9
        row.append(val)
    # Find the starting index in the cycle
    start_idx = cycle.index(row[0])
    expected = [cycle[(start_idx + i) % 6] for i in range(6)]
    match = row == expected
    print(f"  n%3={a}: {row}, cycle start={start_idx}, cyclic={match}")
