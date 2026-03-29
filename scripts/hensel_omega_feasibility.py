"""
Lean omega feasibility analysis for Hensel general induction.

omega handles linear arithmetic but not 2^k.
We need to find what intermediate facts to provide as hypotheses.
"""

print("=" * 70)
print("Lean omega feasibility: 帰納法ステップの omega 化可能性")
print("=" * 70)

print("""
帰納法の step (→ 方向) のkey equation:

Givens:
  halt : 2^k * (Tk + 1) = 3^k * (n + 1)     -- syracuse_iter_alt_formula
  hmod : n % 2^{k+1} = 2^{k+1} - 1          -- IH
  hmod4: Tk % 4 = 3                          -- from ascent at step k

Goal: n % 2^{k+2} = 2^{k+2} - 1

Key intermediate steps (all involving 2^k as variable):

Step A: hmod → 2^{k+1} | (n+1)
  Use: Nat.dvd_of_mod_eq_zero (after showing (n+1) % 2^{k+1} = 0)
  This needs: have h_mod_n1 : (n + 1) % 2^{k+1} = 0 := by omega -- needs 2^{k+1} as var

  Alternative approach: introduce m := (n+1) / 2^{k+1} directly
  and have hm_def : n + 1 = 2^{k+1} * m (from hmod, needs omega help)

Step B: halt + hm_def → Tk + 1 = 2 * 3^k * m
  2^k * (Tk + 1) = 3^k * 2^{k+1} * m
  2^k * (Tk + 1) = 2 * 2^k * 3^k * m  (by ring on 2^{k+1} = 2 * 2^k)
  Tk + 1 = 2 * 3^k * m                 (cancel 2^k)

  For the cancellation, we need Nat.mul_left_cancel or similar.
  omega cannot do this with variable 2^k, 3^k.

Step C: hmod4 + Step B → m is even
  Tk + 1 = 2 * 3^k * m, Tk % 4 = 3
  → (2 * 3^k * m - 1) % 4 = 3
  → 2 * 3^k * m % 4 = 0

  Since 3^k is odd: (3^k % 2 = 1)
  2 * odd * m % 4 = 0 ⟺ m is even

  omega CAN handle this IF we introduce:
  - let P = 3^k (abstract as odd variable)
  - have hP_odd : P % 2 = 1
  - have h_val : Tk + 1 = 2 * P * m
  - have h_mod : Tk % 4 = 3
  Then: omega should derive m % 2 = 0

Step D: m even → 2^{k+2} | (n+1) → n % 2^{k+2} = 2^{k+2} - 1
  m = 2 * m'
  n + 1 = 2^{k+1} * m = 2^{k+1} * 2 * m' = 2^{k+2} * m'
  → 2^{k+2} | (n + 1)
  → n % 2^{k+2} = 2^{k+2} - 1

  This needs: have h_m_even : m % 2 = 0  (from Step C)
  and: n + 1 = 2^{k+1} * m = 2^{k+2} * (m / 2)

  omega cannot work with 2^{k+1} * m = 2^{k+2} * (m/2) directly.
  Need: have : 2^{k+2} = 2 * 2^{k+1} := by ring
  and:  have : m = 2 * (m / 2) := by omega  (from m even)
  then: n + 1 = 2^{k+1} * (2 * (m/2)) = 2 * 2^{k+1} * (m/2) = 2^{k+2} * (m/2)
""")

print("\n" + "=" * 70)
print("推奨される Lean 証明構造 (→ 方向の step)")
print("=" * 70)

print(r"""
| succ k ih =>
    -- Goal: consecutiveAscents n (k+2) → n % 2^{k+3} = 2^{k+3} - 1
    -- hasc : consecutiveAscents n (k + 2)

    -- Step 1: 弱化して IH 適用
    have hasc_k1 : consecutiveAscents n (k + 1) :=
      consecutiveAscents_mono n (by omega) hasc
    have hmod_prev := ih hasc_k1
    -- hmod_prev : n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1

    -- Step 2: k+1 番目のステップの上昇条件
    have hiter_pos := syracuseIter_pos_of_ascents n (k+1) hn hodd hasc_k1
    have hiter_odd := syracuseIter_odd_of_ascents n (k+1) hn hodd hasc_k1
    have h_step := hasc (k + 1) (by omega)
    have hiter_mod4 := (syracuse_ascent_iff_mod4_eq3
        (syracuseIter (k+1) n) hiter_pos hiter_odd).mp h_step

    -- Step 3: alt_formula
    have halt := syracuse_iter_alt_formula n (k+1) hn hodd hasc_k1
    -- halt : 2^{k+1} * T^{k+1}(n) + 2^{k+1} = 3^{k+1} * (n+1)
    -- つまり 2^{k+1} * (T^{k+1}(n) + 1) = 3^{k+1} * (n+1)

    -- Step 4: n+1 の因数分解
    -- hmod_prev → 2^{k+2} | (n+1)
    set M := 2 ^ (k + 2) with hM_def
    set Tk := syracuseIter (k + 1) n
    set P := 3 ^ (k + 1) with hP_def
    set L := 2 ^ (k + 1) with hL_def

    have hL_pos : L > 0 := Nat.pos_of_ne_zero (by positivity)
    have hM_eq : M = 2 * L := by rw [hM_def, hL_def]; ring

    -- n + 1 = M * m for some m
    have hmod_rewrite : (n + 1) % M = 0 := by
      rw [hM_def]; omega  -- from hmod_prev
    obtain ⟨m, hm⟩ := Nat.dvd_of_mod_eq_zero hmod_rewrite
    -- hm : n + 1 = M * m

    -- Step 5: Tk + 1 = 2 * P * m
    -- halt: L * (Tk + 1) = P * (n + 1) = P * M * m = P * 2 * L * m
    --      = L * (2 * P * m)
    -- Cancel L: Tk + 1 = 2 * P * m
    have h_cancel_setup : L * (Tk + 1) = L * (2 * P * m) := by
      calc L * (Tk + 1)
          = L * Tk + L := by ring
        _ = P * (n + 1) := halt
        _ = P * (M * m) := by rw [hm]
        _ = P * (2 * L * m) := by rw [hM_eq]
        _ = L * (2 * P * m) := by ring
    have hTk_plus1 : Tk + 1 = 2 * P * m :=
      Nat.eq_of_mul_eq_left hL_pos h_cancel_setup
      -- or: Mul.mul のcancelation lemma

    -- Step 6: P は奇数
    have hP_odd : P % 2 = 1 := by
      rw [hP_def]; exact Nat.Odd.pow ... -- or: 奇数のべき乗は奇数
      -- alternative: induction, or: (3 % 2 = 1).pow

    -- Step 7: m は偶数
    -- Tk % 4 = 3 and Tk + 1 = 2*P*m
    -- → 2*P*m % 4 = 0 (since Tk % 4 = 3 → (Tk+1) % 4 = 0)
    -- → P*m は偶数
    -- → m は偶数 (P is odd)
    have h_Tk1_mod4 : (Tk + 1) % 4 = 0 := by omega  -- from hiter_mod4
    have h_2Pm_mod4 : (2 * P * m) % 4 = 0 := by rw [← hTk_plus1]; exact h_Tk1_mod4
    have hm_even : m % 2 = 0 := by
      -- 2 * P * m ≡ 0 (mod 4) and P odd
      -- → 2 * m ≡ 0 (mod 4) [since P ≡ 1 mod 2, can factor]
      -- → m ≡ 0 (mod 2)
      by_contra hm_odd
      push_neg at hm_odd
      have : m % 2 = 1 := by omega
      -- 2 * P * m where P,m both odd → 2 * odd ≡ 2 mod 4
      -- But 2*P*m % 4 = 0, contradiction
      have : (2 * P * m) % 4 = 2 := by
        -- P*m is odd (odd*odd=odd)
        have hPm_odd : (P * m) % 2 = 1 := by omega  -- P odd, m odd
        omega  -- 2 * odd mod 4 = 2
      omega  -- contradiction: 0 = 2

    -- Step 8: 結論
    -- m = 2*m', n+1 = M*m = 2*L * 2*m' = 4*L*m' = 2^{k+3} * m'
    -- → n % 2^{k+3} = 2^{k+3} - 1
    obtain ⟨m', hm'⟩ := Nat.dvd_of_mod_eq_zero (by omega : m % 2 = 0 → ...)
    -- or: have hm' : m = 2 * (m / 2) := by omega
    have hm' : m = 2 * (m / 2) := by omega
    have h_n1 : n + 1 = 2 ^ (k + 3) * (m / 2) := by
      rw [hm, hM_eq, hm']
      ring
    -- n + 1 = 2^{k+3} * (m/2) → n % 2^{k+3} = 2^{k+3} - 1
    omega  -- should work after h_n1
""")

print("\n" + "=" * 70)
print("推奨される Lean 証明構造 (← 方向の step)")
print("=" * 70)

print(r"""
| succ k ih =>
    -- Goal: n % 2^{k+3} = 2^{k+3} - 1 → consecutiveAscents n (k+2)
    -- hmod : n % 2 ^ (k + 3) = 2 ^ (k + 3) - 1

    -- Step 1: 弱化
    have hmod_prev : n % 2 ^ (k + 2) = 2 ^ (k + 2) - 1 := by
      have : 2 ^ (k + 3) = 2 * 2 ^ (k + 2) := by ring
      omega  -- needs intermediate: Nat.mod_mod_of_dvd or manual
      -- Alternative: use mod_pow_succ_implies_mod_pow

    -- Step 2: IH 適用
    have hasc_k1 : consecutiveAscents n (k + 1) := ih hmod_prev

    -- Step 3: k+1 番目のステップも上昇することを示す
    -- alt_formula
    have halt := syracuse_iter_alt_formula n (k+1) hn hodd hasc_k1
    set M := 2 ^ (k + 2) with hM_def
    set Tk := syracuseIter (k + 1) n
    set P := 3 ^ (k + 1) with hP_def
    set L := 2 ^ (k + 1) with hL_def

    -- (前と同様に m を定義)
    have hmod_rewrite : (n + 1) % M = 0 := by omega
    obtain ⟨m, hm⟩ := Nat.dvd_of_mod_eq_zero hmod_rewrite

    -- Tk + 1 = 2 * P * m (前と同じ手順)
    have hTk_plus1 : Tk + 1 = 2 * P * m := by
      -- (same as forward direction)
      sorry

    -- hmod から m は偶数
    -- n + 1 = M * m = 2*L * m
    -- n % 2^{k+3} = 2^{k+3} - 1
    -- → 2^{k+3} | (n+1)
    -- → 4*L | (2*L * m) → 2 | m
    have hm_even : m % 2 = 0 := by
      -- n % 2^{k+3} = 2^{k+3} - 1 → 2^{k+3} | (n+1)
      -- 2^{k+3} = 2 * 2^{k+2} = 2 * M
      -- M * m = n + 1 is divisible by 2*M → m is even
      have h2M_dvd : (2 * M) ∣ (n + 1) := by
        have : 2 ^ (k + 3) = 2 * M := by rw [hM_def]; ring
        omega  -- from hmod
      rw [hm] at h2M_dvd
      -- 2 * M | (M * m) → 2 | m
      exact ... -- Nat.dvd cancelation

    -- Tk % 4 = 3
    have hP_odd : P % 2 = 1 := by ...
    have hTk_mod4 : Tk % 4 = 3 := by
      -- Tk + 1 = 2 * P * m, m even, P odd
      -- Tk + 1 = 2 * odd * even = 4 * odd * (m/2)
      -- Tk + 1 ≡ 0 mod 4
      -- Tk ≡ 3 mod 4
      have hm' : m = 2 * (m / 2) := by omega
      have : Tk + 1 = 4 * (P * (m / 2)) := by
        rw [hTk_plus1, hm']; ring
      omega

    -- Step 4: Combine
    intro i hi
    by_cases hik : i < k + 1
    · exact hasc_k1 i hik
    · have : i = k + 1 := by omega
      subst this
      exact syracuse_gt_of_mod4_eq3 Tk hTk_mod4
""")

# 最終的な実装難易度の見積もり
print("\n" + "=" * 70)
print("実装難易度サマリ")
print("=" * 70)
print("""
1. mod_pow_succ_implies_mod_pow:
   難易度: 低 (omega + ring で 5-10行)

2. iter_plus_one_factorization (核心):
   難易度: 中～高 (Nat.eq_of_mul_eq_left の正しいAPI + calc で 15-25行)
   技術的課題: 2^k のキャンセルの API を特定する必要あり

3. m の偶奇判定 (iter_mod4 相当):
   難易度: 中 (omega + by_contra で 10-15行)

4. hensel_general_forward:
   難易度: 中 (帰納法 + 上記補題の組み合わせで 40-60行)

5. hensel_general_backward:
   難易度: 中 (同様の構造で 40-60行)

合計見積もり: 120-180行
最大のリスク: Lean の Nat 算術の API が期待通り動くか
""")
