"""
Lean実装詳細設計: 一般Hensel帰納法
具体的なLean 4コードスケッチを出力する
"""

lean_sketch = r"""
/-!
# コラッツ予想: 一般 Hensel 帰納法 (General Hensel Induction)

## 主定理
consecutiveAscents n (k+1) ⟺ n % 2^{k+2} = 2^{k+2} - 1

これは k=1,2,3,4 の個別証明を一般の k に統合する。

## 証明の鍵
`syracuse_iter_alt_formula`:
    2^k * (T^k(n) + 1) = 3^k * (n + 1)

から T^k(n) + 1 = 2 * 3^k * m (where m = (n+1) / 2^{k+1}) を導出し、
T^k(n) % 4 を m の偶奇で判定する。
-/

import Unsolved.Collatz.Formula

/-! ## Part A: 補助補題 -/

/-- mod の弱化: 2^{k+2} での合同は 2^{k+1} での合同を含む -/
theorem mod_pow_succ_implies_mod_pow (n k : ℕ)
    (h : n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1) :
    n % 2 ^ (k + 1) = 2 ^ (k + 1) - 1 := by
  -- PROOF STRATEGY:
  -- 2^{k+2} = 2 * 2^{k+1}
  -- n = 2^{k+2} * q + (2^{k+2} - 1) for some q
  -- = 2 * 2^{k+1} * q + 2 * 2^{k+1} - 1
  -- = 2^{k+1} * (2*q + 1) + 2^{k+1} - 1
  -- n % 2^{k+1} = (2^{k+1} - 1) % 2^{k+1} = 2^{k+1} - 1
  --
  -- Lean: omega should handle this with appropriate setup
  -- Key: 2^{k+2} = 2 * 2^{k+1}
  have h2 : 2 ^ (k + 2) = 2 * 2 ^ (k + 1) := by ring
  omega  -- NOTE: omega may need help with 2^k terms; may need:
         -- have hpow : 2 ^ (k + 1) > 0 := Nat.pos_of_ne_zero (by positivity)
         -- and Nat.mod_mod_of_dvd

/-- n % 2^{k+1} = 2^{k+1} - 1 ⟺ (n+1) は 2^{k+1} で割り切れる -/
theorem mod_eq_pred_iff_dvd (n k : ℕ) :
    n % 2 ^ (k + 1) = 2 ^ (k + 1) - 1 ↔
    2 ^ (k + 1) ∣ (n + 1) := by
  -- PROOF STRATEGY:
  -- n % M = M - 1 ⟺ (n + 1) % M = 0 ⟺ M | (n+1)
  constructor
  · intro h
    have hpow : 2 ^ (k + 1) > 0 := Nat.pos_of_ne_zero (by positivity)
    -- n = M*q + (M-1) → n+1 = M*q + M = M*(q+1)
    omega  -- or use Nat.dvd_of_mod_eq_zero
  · intro ⟨m, hm⟩
    -- n + 1 = M * m → n = M*m - 1 → n % M = M - 1
    omega

/-! ## Part B: iter_mod4 -- 最も技術的な核心部分 -/

/-- T^k(n) + 1 の因数分解:
    consecutiveAscents n k ∧ n%2^{k+1}=2^{k+1}-1 のとき
    T^k(n) + 1 = 2 * 3^k * ((n + 1) / 2^{k+1))  -/
theorem iter_plus_one_factorization (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k)
    (hmod : n % 2 ^ (k + 1) = 2 ^ (k + 1) - 1) :
    syracuseIter k n + 1 = 2 * 3 ^ k * ((n + 1) / 2 ^ (k + 1)) := by
  -- PROOF STRATEGY:
  -- From syracuse_iter_alt_formula:
  --   2^k * (T^k(n) + 1) = 3^k * (n + 1)   ... (*)
  --
  -- From hmod: n + 1 ≡ 0 (mod 2^{k+1}), so n + 1 = 2^{k+1} * m
  -- where m = (n + 1) / 2^{k+1}
  --
  -- Substituting into (*):
  --   2^k * (T^k(n) + 1) = 3^k * 2^{k+1} * m = 2^{k+1} * 3^k * m
  --   T^k(n) + 1 = 2 * 3^k * m
  --
  -- LEAN PROOF STEPS:
  -- 1. Get alt_formula: 2^k * (iter + 1) = 3^k * (n + 1)
  have halt := syracuse_iter_alt_formula n k hn hodd hasc
  -- halt : 2^k * syracuseIter k n + 2^k = 3^k * (n + 1)
  -- つまり 2^k * (syracuseIter k n + 1) = 3^k * (n + 1)
  --
  -- 2. From hmod, get n + 1 = 2^{k+1} * m
  have hdvd : 2 ^ (k + 1) ∣ (n + 1) := by
    -- from hmod via mod_eq_pred_iff_dvd
    exact (mod_eq_pred_iff_dvd n k).mp hmod
  obtain ⟨m, hm⟩ := hdvd
  -- hm : n + 1 = 2 ^ (k + 1) * m
  --
  -- 3. Substitute and simplify
  -- 2^k * (iter + 1) = 3^k * (2^{k+1} * m) = 3^k * 2 * 2^k * m = 2^k * (2 * 3^k * m)
  -- Cancel 2^k from both sides
  -- iter + 1 = 2 * 3^k * m
  --
  -- NOTE: The main technical challenge is:
  -- - Rewriting 3^k * (2^{k+1} * m) as 2^k * (2 * 3^k * m)
  -- - Using Nat.eq_of_mul_eq_left to cancel 2^k
  --
  -- halt rewritten: 2^k * (iter + 1) = 3^k * (n + 1) = 3^k * (2^{k+1} * m)
  -- = 3^k * (2 * 2^k * m) = 2^k * (2 * 3^k * m)
  have hpow_pos : 2 ^ k > 0 := Nat.pos_of_ne_zero (by positivity)
  have h_rearrange : 3 ^ k * (n + 1) = 2 ^ k * (2 * 3 ^ k * m) := by
    rw [hm]; ring
  -- From halt: 2^k * (iter + 1) = 2^k * (2 * 3^k * m)
  -- Cancel 2^k:
  have h_eq : 2 ^ k * (syracuseIter k n + 1) = 2 ^ k * (2 * 3 ^ k * m) := by
    linarith
  exact Nat.eq_of_mul_eq_left hpow_pos h_eq  -- possibly wrong API name
  -- Alternative: omega or nlinarith after sufficient setup

/-- T^k(n) の mod 4 判定:
    上の因数分解から T^k(n) = 2*3^k*m - 1 なので
    T^k(n) % 4 は m の偶奇で決まる -/
theorem iter_mod4_of_factorization (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k)
    (hmod : n % 2 ^ (k + 1) = 2 ^ (k + 1) - 1) :
    -- m が偶数のとき T^k(n) % 4 = 3, m が奇数のとき T^k(n) % 4 = 1
    (((n + 1) / 2 ^ (k + 1)) % 2 = 0 → syracuseIter k n % 4 = 3) ∧
    (((n + 1) / 2 ^ (k + 1)) % 2 = 1 → syracuseIter k n % 4 = 1) := by
  -- PROOF STRATEGY:
  -- Let m = (n + 1) / 2^{k+1}
  -- From iter_plus_one_factorization: T^k(n) + 1 = 2 * 3^k * m
  -- T^k(n) = 2 * 3^k * m - 1
  --
  -- Key insight: 3^k is always odd, so:
  --   2 * 3^k * m mod 4:
  --   - m even (m = 2m'): 2 * odd * 2m' = 4 * odd * m' ≡ 0 mod 4
  --     → T^k(n) = 4j - 1 ≡ 3 mod 4
  --   - m odd: 2 * odd * odd = 2 * odd ≡ 2 mod 4
  --     → T^k(n) = 4j + 2 - 1 = 4j + 1 ≡ 1 mod 4
  --
  -- LEAN PROOF:
  -- 1. Get factorization
  have hfact := iter_plus_one_factorization n k hn hodd hasc hmod
  set m := (n + 1) / 2 ^ (k + 1)
  -- hfact : syracuseIter k n + 1 = 2 * 3^k * m
  --
  -- 2. 3^k is odd
  have h3k_odd : 3 ^ k % 2 = 1 := by
    induction k with
    | zero => simp
    | succ k ih => rw [pow_succ]; omega  -- or: Nat.Odd.pow
  --
  -- 3. Split on m % 2
  constructor
  · intro hm_even
    -- m = 2*m', so 2*3^k*m = 4*3^k*m' ≡ 0 mod 4
    -- T^k(n) = 4*3^k*m' - 1 ≡ 3 mod 4
    omega  -- after sufficient setup with hfact, h3k_odd, hm_even
  · intro hm_odd
    -- 2*3^k*m: since 3^k odd and m odd, 3^k*m is odd
    -- 2*odd ≡ 2 mod 4
    -- T^k(n) = 2 mod 4 - 1 = ... hmm, need to be more careful
    -- T^k(n) + 1 = 2 * (3^k * m) where 3^k*m is odd
    -- T^k(n) + 1 ≡ 2 mod 4
    -- T^k(n) ≡ 1 mod 4
    omega  -- after sufficient setup

/-! ## Part C: Forward direction (→) -/

/-- 一般 Hensel 帰納法 (→ 方向):
    consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2} - 1

    注意: 定理の変数は k を 0-indexed にしている。
    つまり k=0 が "1回上昇" に対応。

    帰納法で k に対して証明する。 -/
theorem hensel_general_forward (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n (k + 1)) :
    n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1 := by
  -- PROOF by induction on k
  induction k with
  | zero =>
    -- k = 0: consecutiveAscents n 1 → n % 4 = 3
    -- This is single_ascent_mod4
    have := (single_ascent_mod4 n hn hodd).mp hasc
    -- n % 4 = 3 → n % 2^2 = 2^2 - 1
    norm_num; omega
  | succ k ih =>
    -- k+1: consecutiveAscents n (k+2) → n % 2^{k+3} = 2^{k+3} - 1
    --
    -- Step 1: From hasc, get consecutiveAscents n (k+1)
    have hasc_k1 : consecutiveAscents n (k + 1) :=
      consecutiveAscents_mono n (by omega) hasc
    --
    -- Step 2: Apply IH to get n % 2^{k+2} = 2^{k+2} - 1
    have hmod_prev := ih hasc_k1
    -- hmod_prev : n % 2^{k+2} = 2^{k+2} - 1
    --
    -- Step 3: From consecutiveAscents n (k+2), step k+1 ascends
    -- i.e., syracuse(syracuseIter (k+1) n) > syracuseIter (k+1) n
    -- → syracuseIter (k+1) n % 4 = 3
    have h_step_ascend := hasc (k + 1) (by omega)
    -- h_step_ascend : syracuse (syracuseIter (k+1) n) > syracuseIter (k+1) n
    --
    -- Step 4: Get syracuseIter (k+1) n is odd and positive
    have hiter_odd := syracuseIter_odd_of_ascents n (k + 1) hn hodd hasc_k1
    have hiter_pos := syracuseIter_pos_of_ascents n (k + 1) hn hodd hasc_k1
    --
    -- Step 5: From step 3, get T^{k+1}(n) % 4 = 3
    have hiter_mod4 := (syracuse_ascent_iff_mod4_eq3
        (syracuseIter (k + 1) n) hiter_pos hiter_odd).mp h_step_ascend
    -- hiter_mod4 : syracuseIter (k + 1) n % 4 = 3
    --
    -- Step 6: Use iter_mod4_of_factorization at level k+1
    -- We need: n % 2^{k+2} = 2^{k+2} - 1 (which is hmod_prev)
    -- and: consecutiveAscents n (k+1) (which is hasc_k1)
    -- Conclusion: m is even (since T^{k+1}(n) % 4 = 3)
    -- where m = (n+1) / 2^{k+2}
    -- m even → n + 1 ≡ 0 (mod 2^{k+3})
    -- → n % 2^{k+3} = 2^{k+3} - 1
    --
    -- TECHNICAL DETAIL:
    -- iter_mod4_of_factorization gives us:
    --   m even → T^{k+1}(n) % 4 = 3
    --   m odd → T^{k+1}(n) % 4 = 1
    -- We know T^{k+1}(n) % 4 = 3, so m must be even.
    -- Contrapositive: if m were odd, T^{k+1}(n) % 4 = 1, contradiction.
    --
    -- From m even: (n+1) / 2^{k+2} is even
    -- → 2^{k+3} | (n+1)
    -- → n % 2^{k+3} = 2^{k+3} - 1
    --
    -- The actual proof may use:
    -- by_contra + show m is odd → T^{k+1}(n) % 4 = 1 → contradiction
    sorry  -- detailed proof needed

/-! ## Part D: Backward direction (←) -/

/-- 一般 Hensel 帰納法 (← 方向):
    n % 2^{k+2} = 2^{k+2} - 1 → consecutiveAscents n (k+1) -/
theorem hensel_general_backward (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hmod : n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1) :
    consecutiveAscents n (k + 1) := by
  -- PROOF by induction on k
  induction k with
  | zero =>
    -- n % 4 = 3 → consecutiveAscents n 1
    have : n % 4 = 3 := by norm_num at hmod; omega
    exact (single_ascent_mod4 n hn hodd).mpr this
  | succ k ih =>
    -- n % 2^{k+3} = 2^{k+3} - 1 → consecutiveAscents n (k+2)
    --
    -- Step 1: Get n % 2^{k+2} = 2^{k+2} - 1
    have hmod_prev := mod_pow_succ_implies_mod_pow n (k + 1) -- need correct args
    -- Apply IH: consecutiveAscents n (k+1)
    --
    -- Step 2: IH gives consecutiveAscents n (k+1)
    have hasc_k1 := ih hmod_prev
    --
    -- Step 3: Show the (k+1)-th step also ascends
    -- Use iter_mod4_of_factorization at level k+1:
    -- m = (n+1)/2^{k+2}, and from hmod, m is even
    -- → T^{k+1}(n) % 4 = 3
    -- → syracuse(T^{k+1}(n)) > T^{k+1}(n)
    --
    -- Step 4: Combine to get consecutiveAscents n (k+2)
    -- consecutiveAscents n (k+2) means:
    -- ∀ i < k+2, syracuse(syracuseIter i n) > syracuseIter i n
    -- For i < k+1: this follows from hasc_k1
    -- For i = k+1: this is what we just proved
    intro i hi
    by_cases hik : i < k + 1
    · exact hasc_k1 i hik
    · have : i = k + 1 := by omega
      subst this
      -- Need: syracuse(syracuseIter (k+1) n) > syracuseIter (k+1) n
      -- From T^{k+1}(n) % 4 = 3
      exact syracuse_gt_of_mod4_eq3 (syracuseIter (k + 1) n) sorry
      -- (the sorry here is iter_mod4 result)

/-! ## Part E: Main theorem -/

/-- 一般 Hensel 帰納法:
    consecutiveAscents n (k+1) ⟺ n % 2^{k+2} = 2^{k+2} - 1

    k=0: 1回上昇 ⟺ n ≡ 3 (mod 4)
    k=1: 2回連続上昇 ⟺ n ≡ 7 (mod 8)
    k=2: 3回連続上昇 ⟺ n ≡ 15 (mod 16)
    k=3: 4回連続上昇 ⟺ n ≡ 31 (mod 32)
    一般: (k+1)回連続上昇 ⟺ n ≡ 2^{k+2}-1 (mod 2^{k+2}) -/
theorem hensel_general (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n (k + 1) ↔ n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1 :=
  ⟨hensel_general_forward n k hn hodd,
   hensel_general_backward n k hn hodd⟩

/-! ## Part F: 等価な表現（確率的解釈用） -/

/-- 確率的解釈: k+1回連続上昇する n の割合は 1/2^{k+1}
    正確には: mod 2^{k+2} の奇数の中で条件を満たすのは 2^{k+2} 個中 1 個 -/
-- (これはコメントとして残す。証明は mod の計算で得られる。)

/-! ## Part G: 数値検証 -/

-- k=5: 6回連続上昇 ⟺ n ≡ 127 (mod 128)
-- example : hensel_general 127 5 (by omega) (by omega) |>.mpr (by norm_num)

-- k=6: 7回連続上昇 ⟺ n ≡ 255 (mod 256)
-- example : hensel_general 255 6 (by omega) (by omega) |>.mpr (by norm_num)
"""

print(lean_sketch)

# 最も困難な技術的ポイントの分析
print("\n" + "=" * 70)
print("技術的困難ポイントの詳細分析")
print("=" * 70)

issues = [
    ("Issue 1: omega と 2^k",
     """omega は一般に 2^k を含む式を直接扱えない。
     対策:
     a) have : 2 ^ (k+2) = 2 * 2 ^ (k+1) := by ring
        これを omega に渡す
     b) Nat.mod_mod_of_dvd を使う:
        Nat.mod_mod_of_dvd n (2^{k+1}) (2) : n % (2*2^{k+1}) % 2^{k+1} = n % 2^{k+1}
     c) 最悪の場合 nlinarith + ring で対処"""),

    ("Issue 2: Nat.eq_of_mul_eq_left の使用",
     """2^k * a = 2^k * b から a = b を得る。
     Mathlib API: Nat.eq_of_mul_eq_left (h : 0 < c) : c * a = c * b → a = b
     実際のAPIは Nat.mul_left_cancel かもしれない。
     Alternative: have := Nat.div_eq_of_eq_mul_right ... を使う"""),

    ("Issue 3: (n+1) / 2^{k+1} の偶奇判定",
     """n % 2^{k+2} = 2^{k+2} - 1 から (n+1)/2^{k+1} が偶数であることを導く。

     n + 1 = 2^{k+2} * q + 2^{k+2} = 2^{k+2} * (q + 1) [hmod から]
     ... ではなく:
     n = 2^{k+2} * q + (2^{k+2} - 1) for some q
     n + 1 = 2^{k+2} * q + 2^{k+2} = 2^{k+2} * (q + 1)
     (n+1) / 2^{k+1} = 2 * (q + 1) [偶数]

     Lean でこれを示すには:
     have : n + 1 = 2^{k+2} * ((n + 1) / 2^{k+2}) := ...
     have : (n + 1) / 2^{k+1} = 2 * ((n + 1) / 2^{k+2}) := ...
     """),

    ("Issue 4: 帰納法のインデックスずれ",
     """定理は consecutiveAscents n (k+1) の形で、k に対して帰納法。
     base case k=0 は single_ascent_mod4 に対応。
     step は k → k+1。

     注意: Lean の induction k with は k=0 と k+1 で分岐するが、
     ここでの定理の構造は
       ∀ k, consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2} - 1
     なので、帰納法の IH は
       consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2} - 1
     であり、step では
       consecutiveAscents n (k+2) → n % 2^{k+3} = 2^{k+3} - 1
     を示す。

     IH を使うには consecutiveAscents n (k+1) が必要で、
     これは consecutiveAscents_mono で hasc から得られる。"""),
]

for title, desc in issues:
    print(f"\n--- {title} ---")
    print(desc)

# 代替設計: 定理文の変形
print("\n" + "=" * 70)
print("代替定理文の検討")
print("=" * 70)
print("""
Option A (現行):
  hensel_general n k : consecutiveAscents n (k+1) ↔ n % 2^{k+2} = 2^{k+2} - 1
  k=0 が 1回上昇に対応。インデックスがずれて読みにくい。

Option B (シフト版):
  hensel_general n k (hk : k ≥ 1) :
    consecutiveAscents n k ↔ n % 2^{k+1} = 2^{k+1} - 1
  k=1 が 1回上昇に対応。数学的に自然だが hk ≥ 1 が必要。

Option C (0回上昇を含む):
  hensel_general n k :
    consecutiveAscents n k ↔ n % 2^{k+1} = 2^{k+1} - 1 (k ≥ 1)
  k=0 では consecutiveAscents n 0 = True, n % 2 = 1 (前提の hodd)。
  整合性あり。ただし k=0 を特別扱いする必要がある。

推奨: Option A を採用。理由:
  - 帰納法の base case が k=0 で clean
  - k+1, k+2 のパターンは Lean で標準的
  - 既存の single_ascent_mod4 とも合致
""")
