"""
Final blueprint for Lean formalization of:
  v2(3n+1) >= k  <=>  n % 2^k = (4^{ceil(k/2)} - 1) / 3

This script outputs the complete Lean proof blueprint.
"""

print("""
============================================================
LEAN PROOF BLUEPRINT: v2(3n+1) >= k の精密条件
============================================================

/-- Collatz residue: v2(3n+1) >= k を特徴づける剰余
    collatzResidue k = (4^{ceil(k/2)} - 1) / 3
    = (4^((k+1)/2) - 1) / 3  (Nat.div) -/
def collatzResidue (k : Nat) : Nat := (4 ^ ((k + 1) / 2) - 1) / 3

============================================================
STEP 1: collatzResidue の基本性質
============================================================

-- 具体値
example : collatzResidue 0 = 0 := by native_decide  -- or norm_num
example : collatzResidue 1 = 1 := by native_decide
example : collatzResidue 2 = 1 := by native_decide
example : collatzResidue 3 = 5 := by native_decide
example : collatzResidue 4 = 5 := by native_decide
example : collatzResidue 5 = 21 := by native_decide
example : collatzResidue 6 = 21 := by native_decide
example : collatzResidue 7 = 85 := by native_decide
example : collatzResidue 8 = 85 := by native_decide

-- 核心等式: 3 * collatzResidue k + 1 = 4^((k+1)/2)
theorem collatzResidue_identity (k : Nat) :
    3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2) := by
  -- (4^m - 1) / 3 * 3 = 4^m - 1 since 3 | (4^m - 1)
  -- 4^m - 1 + 1 = 4^m
  sorry -- needs: 3 | (4^m - 1) and div/mul cancellation

-- 補助: 3 | (4^m - 1)
theorem three_dvd_four_pow_sub_one (m : Nat) : 3 | (4 ^ m - 1) := by
  -- 4 = 1 (mod 3), so 4^m = 1 (mod 3), 4^m - 1 = 0 (mod 3)
  sorry

============================================================
STEP 2: 2^k | (3 * collatzResidue k + 1)
============================================================

-- 2^k | 4^((k+1)/2) since 4^((k+1)/2) = 2^(2*((k+1)/2)) >= 2^k
theorem two_pow_dvd_collatzResidue_step (k : Nat) :
    2 ^ k | (3 * collatzResidue k + 1) := by
  rw [collatzResidue_identity]
  -- Need: 2^k | 4^((k+1)/2) = 2^(2*((k+1)/2))
  -- and 2*((k+1)/2) >= k
  sorry

============================================================
STEP 3: v2(m) >= k <=> 2^k | m  (m > 0)
============================================================

theorem v2_ge_iff_dvd (m : Nat) (hm : m > 0) (k : Nat) :
    v2 m >= k <-> 2 ^ k | m := by
  -- By induction on k
  induction k with
  | zero => simp  -- 2^0 = 1 divides everything
  | succ k ih =>
    constructor
    . -- (=>) v2 m >= k+1 implies 2^(k+1) | m
      intro hge
      -- v2 m > 0 so m is even
      -- v2 m = 1 + v2(m/2) >= k+1 so v2(m/2) >= k
      -- IH: 2^k | m/2
      -- Therefore 2^(k+1) = 2 * 2^k | 2 * (m/2) = m
      sorry
    . -- (<=) 2^(k+1) | m implies v2 m >= k+1
      intro hdvd
      -- 2 | m (from 2^(k+1) | m)
      -- v2 m = 1 + v2(m/2)
      -- 2^k | m/2 (from 2^(k+1) | m)
      -- IH: v2(m/2) >= k
      -- So v2 m >= k+1
      sorry

============================================================
STEP 4: 合同条件の一意性
============================================================

-- 3r = -1 (mod 2^k) の解の一意性
-- gcd(3, 2^k) = 1 なので解は mod 2^k で一意
theorem mod_unique_solution (k : Nat) (a b : Nat)
    (ha : (3 * a + 1) % 2^k = 0)
    (hb : (3 * b + 1) % 2^k = 0)
    (ha_lt : a < 2^k) (hb_lt : b < 2^k) : a = b := by
  -- 3a = 3b (mod 2^k) and gcd(3, 2^k) = 1 so a = b (mod 2^k)
  sorry

============================================================
STEP 5: メイン定理
============================================================

/-- v2(3n+1) >= k の精密特徴づけ:
    v2(3n+1) >= k  <=>  n % 2^k = collatzResidue k -/
theorem v2_ge_iff_collatzResidue (n k : Nat) :
    v2 (3 * n + 1) >= k <-> n % 2^k = collatzResidue k := by
  constructor
  . -- (=>) v2(3n+1) >= k implies n % 2^k = collatzResidue k
    intro hge
    have hdvd : 2^k | (3*n+1) := (v2_ge_iff_dvd _ (by omega) k).mp hge
    -- (3*n+1) % 2^k = 0
    -- Also (3*collatzResidue k + 1) % 2^k = 0
    -- So 3*n = 3*collatzResidue k (mod 2^k)
    -- Since gcd(3, 2^k) = 1: n = collatzResidue k (mod 2^k)
    sorry
  . -- (<=) n % 2^k = collatzResidue k implies v2(3n+1) >= k
    intro hmod
    -- n = 2^k * q + collatzResidue k for some q
    -- 3n + 1 = 3 * 2^k * q + 3*collatzResidue k + 1
    --        = 3 * 2^k * q + 4^((k+1)/2)
    -- 2^k | both terms, so 2^k | (3n+1)
    -- v2(3n+1) >= k by v2_ge_iff_dvd
    sorry

============================================================
STEP 6: 既存補題の復元
============================================================

-- v2_ge_two_of_mod4_eq1 は k=2 の特殊ケース
theorem v2_ge_two_of_mod4_eq1' (n : Nat) (h : n % 4 = 1) :
    v2 (3 * n + 1) >= 2 := by
  rw [v2_ge_iff_collatzResidue]
  -- collatzResidue 2 = 1, and n % 4 = 1
  sorry  -- omega after unfolding collatzResidue

-- v2_ge_three_of_mod8_eq5 は k=3 の特殊ケース
theorem v2_ge_three_of_mod8_eq5' (n : Nat) (h : n % 8 = 5) :
    v2 (3 * n + 1) >= 3 := by
  rw [v2_ge_iff_collatzResidue]
  -- collatzResidue 3 = 5, and n % 8 = 5
  sorry

============================================================
PRACTICAL NOTES FOR LEAN IMPLEMENTATION
============================================================

1. collatzResidue の定義は (4^m - 1)/3 だが、
   3 | (4^m - 1) の証明が必要。
   これは 4 = 1 (mod 3) から 4^m = 1 (mod 3) で従う。

2. v2_ge_iff_dvd は既存の pow_v2_dvd と対になる重要な補題。
   Lean の既存コードには v2_even, v2_odd があるので
   これらを使った帰納法が自然。

3. 合同条件の一意性は ZMod を使うか、
   直接 Nat.mod の性質で示すか。
   omega が効く範囲では omega で済む。

4. メイン定理の (<=) 方向は比較的簡単:
   n = 2^k*q + r, 3r+1 = 0 (mod 2^k) なので
   3n+1 = 3*2^k*q + 3r+1 = 0 (mod 2^k)

5. (=>) 方向は一意性を使う:
   2^k | (3n+1) なので 3n = -1 (mod 2^k)
   3*collatzResidue k = -1 (mod 2^k) でもある
   gcd(3,2^k)=1 なので n = collatzResidue k (mod 2^k)
""")
