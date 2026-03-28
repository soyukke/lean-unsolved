import Unsolved.Collatz.StoppingTime.Defs
import Unsolved.Collatz.StoppingTime.Verification

/-!
# コラッツ予想: 周期軌道・サイクル分類・軌道減少性

周期軌道の完全分類、k-サイクルの非存在、コラッツ予想の同値条件を証明する。

## 主要結果
- `collatzIter_three_periodic` ~ `collatzIter_seven_periodic`: 3~7-サイクル分類
- `collatzReaches_periodic_trivial`: 周期軌道は {0,1,2,4} のみ
- `collatzConjectureR_iff_bounded`: コラッツ予想 ↔ 有界ステップ判定
- `collatzConjectureR_iff_eventually_decreases`: コラッツ予想 ↔ 軌道減少性
-/

/-! ## 3-サイクルの完全分類 -/

/-- 3ステップ周期点は {0, 1, 2, 4} のみ -/
theorem collatzIter_three_periodic (n : ℕ) (h : collatzIter 3 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  simp [collatzStep] at h
  split at h <;> split at h <;> split at h <;> omega

set_option maxHeartbeats 400000 in
/-- 4ステップ周期点は {0, 1, 2, 4} のみ -/
theorem collatzIter_four_periodic (n : ℕ) (h : collatzIter 4 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  simp [collatzStep] at h
  split at h <;> split at h <;> split at h <;> split at h <;> omega

set_option maxHeartbeats 800000 in
/-- 5ステップ周期点は {0, 1, 2, 4} のみ -/
theorem collatzIter_five_periodic (n : ℕ) (h : collatzIter 5 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  simp [collatzStep] at h
  split at h <;> split at h <;> split at h <;> split at h <;> split at h <;> omega

set_option maxHeartbeats 4000000 in
/-- 6ステップ周期点は {0, 1, 2, 4} のみ -/
theorem collatzIter_six_periodic (n : ℕ) (h : collatzIter 6 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  have h6 : collatzIter 3 (collatzIter 3 n) = n := by
    rw [← collatzIter_add' 3 3 n]; exact h
  set m := collatzIter 3 n with hm_def
  simp [collatzStep] at hm_def
  split at hm_def <;> split at hm_def <;> split at hm_def
  all_goals (simp [collatzStep] at h6; split at h6 <;> split at h6 <;> split at h6 <;> omega)

set_option maxHeartbeats 8000000 in
/-- 7ステップ周期点は {0, 1, 2, 4} のみ -/
theorem collatzIter_seven_periodic (n : ℕ) (h : collatzIter 7 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  have h7 : collatzIter 4 (collatzIter 3 n) = n := by
    rw [← collatzIter_add' 3 4 n]; exact h
  set m := collatzIter 3 n with hm_def
  simp [collatzStep] at hm_def
  split at hm_def <;> split at hm_def <;> split at hm_def
  all_goals (simp [collatzStep] at h7; split at h7 <;> split at h7 <;> split at h7 <;> split at h7 <;> omega)

/-! ## k-サイクルの有界検証 -/

/-- noCycleBelow k bound: n < bound で非自明な k-サイクルがないことを判定 -/
def noCycleBelow (k bound : ℕ) : Bool :=
  (List.range bound).all fun n =>
    if n == 0 || n == 1 || n == 2 || n == 4 then true
    else collatzIter k n != n

/-- noCycleBelow が true なら、n < bound かつ collatzIter k n = n → n ∈ {0,1,2,4} -/
theorem noCycle_of_check {k bound : ℕ} (hcheck : noCycleBelow k bound = true)
    (n : ℕ) (hn : n < bound) (hcycle : collatzIter k n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  simp only [noCycleBelow, List.all_eq_true, List.mem_range] at hcheck
  have hn_check := hcheck n hn
  simp only [Bool.ite_eq_true_distrib] at hn_check
  by_cases h0 : n = 0
  · left; exact h0
  · by_cases h1 : n = 1
    · right; left; exact h1
    · by_cases h2 : n = 2
      · right; right; left; exact h2
      · by_cases h4 : n = 4
        · right; right; right; exact h4
        · exfalso
          have : (n == 0 || n == 1 || n == 2 || n == 4) = false := by
            simp [beq_iff_eq, h0, h1, h2, h4]
          rw [this, if_neg (by simp)] at hn_check
          simp [bne_iff_ne] at hn_check
          exact hn_check hcycle

set_option linter.style.nativeDecide false in
theorem noCycleBelow_eight : noCycleBelow 8 6562 = true := by native_decide

set_option linter.style.nativeDecide false in
theorem noCycleBelow_nine : noCycleBelow 9 19684 = true := by native_decide

set_option linter.style.nativeDecide false in
theorem noCycleBelow_ten : noCycleBelow 10 59050 = true := by native_decide

/-! ## {1,2,4} サイクルの閉包 -/

/-- {1,2,4} の各値に対して collatzIter k の結果が {1,2,4} に留まる -/
private theorem collatzIter_cycle_aux (k : ℕ) :
    (collatzIter k 1 = 1 ∨ collatzIter k 1 = 2 ∨ collatzIter k 1 = 4) ∧
    (collatzIter k 2 = 1 ∨ collatzIter k 2 = 2 ∨ collatzIter k 2 = 4) ∧
    (collatzIter k 4 = 1 ∨ collatzIter k 4 = 2 ∨ collatzIter k 4 = 4) := by
  induction k with
  | zero => exact ⟨Or.inl rfl, Or.inr (Or.inl rfl), Or.inr (Or.inr rfl)⟩
  | succ k ih =>
    obtain ⟨ih1, ih2, ih4⟩ := ih
    have h14 : collatzStep 1 = 4 := by decide
    have h21 : collatzStep 2 = 1 := by decide
    have h42 : collatzStep 4 = 2 := by decide
    refine ⟨?_, ?_, ?_⟩
    · rw [collatzIter_succ, h14]
      rcases ih4 with h | h | h
      · left; exact h
      · right; left; exact h
      · right; right; exact h
    · rw [collatzIter_succ, h21]
      rcases ih1 with h | h | h
      · left; exact h
      · right; left; exact h
      · right; right; exact h
    · rw [collatzIter_succ, h42]
      rcases ih2 with h | h | h
      · left; exact h
      · right; left; exact h
      · right; right; exact h

/-- collatzIter k 1 ∈ {1, 2, 4} -/
theorem collatzIter_one_in_cycle (k : ℕ) :
    collatzIter k 1 = 1 ∨ collatzIter k 1 = 2 ∨ collatzIter k 1 = 4 :=
  (collatzIter_cycle_aux k).1

/-- collatzIter k 2 ∈ {1, 2, 4} -/
theorem collatzIter_two_in_cycle (k : ℕ) :
    collatzIter k 2 = 1 ∨ collatzIter k 2 = 2 ∨ collatzIter k 2 = 4 :=
  (collatzIter_cycle_aux k).2.1

/-- collatzIter k 4 ∈ {1, 2, 4} -/
theorem collatzIter_four_in_cycle (k : ℕ) :
    collatzIter k 4 = 1 ∨ collatzIter k 4 = 2 ∨ collatzIter k 4 = 4 :=
  (collatzIter_cycle_aux k).2.2

/-! ## 周期軌道の完全分類 -/

/-- 周期性の帰結: k ステップで n に戻るなら、m*k ステップでも n に戻る -/
theorem collatzIter_mul_periodic (n k : ℕ) (hcycle : collatzIter k n = n) (m : ℕ) :
    collatzIter (m * k) n = n := by
  induction m with
  | zero => simp [collatzIter]
  | succ m ih =>
    have heq : (m + 1) * k = m * k + k := by ring
    rw [heq, collatzIter_add' (m * k) k n, ih, hcycle]

/-- ★ コラッツ予想の下での周期軌道の完全分類:
    collatzReaches n かつ collatzIter k n = n (k ≥ 1) ならば n ∈ {0, 1, 2, 4} -/
theorem collatzReaches_periodic_trivial (n k : ℕ) (hk : k ≥ 1)
    (hr : collatzReaches n) (hcycle : collatzIter k n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  by_cases hn0 : n = 0
  · left; exact hn0
  · right
    obtain ⟨j, hj⟩ := hr
    have hk_pos : k > 0 := by omega
    set q := j / k
    set r := j % k
    have hr_lt : r < k := Nat.mod_lt j hk_pos
    have hmod : j = q * k + r := by
      rw [mul_comm]; exact (Nat.div_add_mod j k).symm
    have hqkr : collatzIter (q * k + r) n = 1 := by rw [hmod] at hj; exact hj
    have hqk : collatzIter (q * k) n = n := collatzIter_mul_periodic n k hcycle q
    have hr1 : collatzIter r n = 1 := by
      rw [collatzIter_add'] at hqkr
      rw [hqk] at hqkr
      exact hqkr
    have hkr : r + (k - r) = k := by omega
    have hn_eq : n = collatzIter (k - r) 1 := by
      calc n = collatzIter k n := hcycle.symm
        _ = collatzIter (r + (k - r)) n := by rw [hkr]
        _ = collatzIter (k - r) (collatzIter r n) := collatzIter_add' r (k - r) n
        _ = collatzIter (k - r) 1 := by rw [hr1]
    have h124 := collatzIter_one_in_cycle (k - r)
    rw [← hn_eq] at h124
    exact h124

/-- コラッツ予想が成り立つなら、全ての n ≥ 1 は最終的に {1,2,4} サイクルに入る -/
theorem collatzReaches_enters_cycle (n : ℕ) (hn : n ≥ 1) (hr : collatzReaches n) :
    ∃ k, collatzIter k n = 1 ∨ collatzIter k n = 2 ∨ collatzIter k n = 4 := by
  obtain ⟨j, hj⟩ := hr
  exact ⟨j, Or.inl hj⟩

/-! ## コラッツ予想 ↔ 有界ステップ判定 -/

/-- CollatzConjectureR ↔ ∀ n ≥ 1, ∃ k, collatzReachesBounded k n = true -/
theorem collatzConjectureR_iff_bounded :
    CollatzConjectureR ↔ ∀ n : ℕ, n ≥ 1 → ∃ k, collatzReachesBounded k n = true := by
  constructor
  · intro h n hn
    exact collatzReachesBounded_complete (h n hn)
  · intro h n hn
    obtain ⟨k, hk⟩ := h n hn
    exact collatzReaches_of_bounded k n hk

/-! ## 軌道の性質 -/

/-- collatzReaches 1 ∧ collatzReaches 2 ∧ collatzReaches 3 -/
theorem collatzReaches_one_two_three :
    collatzReaches 1 ∧ collatzReaches 2 ∧ collatzReaches 3 :=
  ⟨collatzReaches_one, collatzReaches_two, collatzReaches_three⟩

/-- 2^k は常に collatzReaches -/
theorem collatzReaches_pow2 (k : ℕ) : collatzReaches (2^k) := collatzReaches_pow_two k

/-- collatzReaches は max に閉じる -/
theorem collatzReaches_max {n m : ℕ} (hn : collatzReaches n) (hm : collatzReaches m) :
    collatzReaches (max n m) := by
  rcases Nat.le_total n m with h | h
  · rw [max_eq_right h]; exact hm
  · rw [max_eq_left h]; exact hn

/-- collatzReaches は min に閉じる -/
theorem collatzReaches_min {n m : ℕ} (hn : collatzReaches n) (hm : collatzReaches m) :
    collatzReaches (min n m) := by
  rcases Nat.le_total n m with h | h
  · rw [min_eq_left h]; exact hn
  · rw [min_eq_right h]; exact hm

/-- collatzReaches は定数関数ではない -/
theorem collatzReaches_not_constant : collatzReaches 1 ∧ ¬collatzReaches 0 :=
  ⟨collatzReaches_one, not_collatzReaches_zero⟩

/-! ## 算術的補題 -/

theorem syracuse_plus_n (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    (3 * n + 1) / 2 + n = (5 * n + 1) / 2 := by omega

theorem three_mul_add_one_ne (n : ℕ) : 3 * n + 1 ≠ n := by omega

theorem three_mul_add_one_sub_succ (n : ℕ) : 3 * n + 1 - (n + 1) = 2 * n := by omega

theorem syracuse_ge_five (n : ℕ) (hn : n ≥ 3) (hodd : n % 2 = 1) :
    (3 * n + 1) / 2 ≥ 5 := by omega

theorem syracuse_ge_eight (n : ℕ) (hn : n ≥ 5) (hodd : n % 2 = 1) :
    (3 * n + 1) / 2 ≥ 8 := by omega

theorem three_mul_add_one_gt_triple (n : ℕ) : 3 * n + 1 > 3 * n := by omega

theorem three_mul_add_one_even_omega (n : ℕ) (hodd : n % 2 = 1) : (3 * n + 1) % 2 = 0 := by omega

theorem half_add_half (n : ℕ) (heven : n % 2 = 0) : n / 2 + n / 2 = n := by omega

/-! ## 軌道の有界性と減少性 -/

/-- collatzReaches n ∧ n ≥ 2 → ∃ k ≥ 1, collatzIter k n < n -/
theorem collatzReaches_eventually_decreases (n : ℕ) (hn : n ≥ 2) (hr : collatzReaches n) :
    ∃ k, k ≥ 1 ∧ collatzIter k n < n := by
  obtain ⟨j, hj⟩ := hr
  have hj_pos : j ≥ 1 := by
    by_contra h; push_neg at h; have : j = 0 := by omega
    subst this; change n = 1 at hj; omega
  exact ⟨j, hj_pos, by omega⟩

/-- collatzStep n > 0 for n > 0 -/
theorem collatzStep_pos (n : ℕ) (hn : n > 0) : collatzStep n > 0 := by
  by_cases hodd : n % 2 = 1
  · rw [collatzStep_odd_eq n hodd]; omega
  · have heven : n % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 n heven]; omega

/-- collatzIter k n > 0 for n > 0 -/
theorem collatzIter_pos (k n : ℕ) (hn : n > 0) : collatzIter k n > 0 := by
  induction k generalizing n with
  | zero => simpa [collatzIter]
  | succ k ih => rw [collatzIter_succ]; exact ih (collatzStep n) (collatzStep_pos n hn)

/-- CollatzConjectureR → 全 n ≥ 2 の軌道に n 未満の値が現れる -/
theorem collatzConjectureR_implies_decreasing (h : CollatzConjectureR) :
    ∀ n : ℕ, n ≥ 2 → ∃ k, k ≥ 1 ∧ collatzIter k n < n :=
  fun n hn => collatzReaches_eventually_decreases n hn (h n (by omega))

/-! ## 軌道減少性 ↔ コラッツ予想 -/

/-- 軌道減少性 → コラッツ予想 -/
theorem collatzConjectureR_of_eventually_decreases
    (h : ∀ n : ℕ, n ≥ 2 → ∃ k, k ≥ 1 ∧ collatzIter k n < n) :
    CollatzConjectureR := by
  unfold CollatzConjectureR
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro hn
    by_cases h1 : n = 1
    · rw [h1]; exact collatzReaches_one
    · obtain ⟨k, hk1, hklt⟩ := h n (by omega)
      have hpos : collatzIter k n > 0 := collatzIter_pos k n (by omega)
      have hr := ih (collatzIter k n) hklt (by omega)
      obtain ⟨j, hj⟩ := hr
      exact ⟨k + j, by rw [collatzIter_add' k j n, hj]⟩

/-- ★ コラッツ予想 ↔ 軌道減少性 -/
theorem collatzConjectureR_iff_eventually_decreases :
    CollatzConjectureR ↔ (∀ n : ℕ, n ≥ 2 → ∃ k, k ≥ 1 ∧ collatzIter k n < n) :=
  ⟨collatzConjectureR_implies_decreasing, collatzConjectureR_of_eventually_decreases⟩

/-- collatzReaches n ならば任意の j ステップ後も 1 に到達する -/
theorem collatzReaches_collatzIter {n : ℕ} (hr : collatzReaches n) (j : ℕ) :
    collatzReaches (collatzIter j n) := by
  obtain ⟨k, hk⟩ := hr
  by_cases hjk : j ≤ k
  · exact ⟨k - j, by
      have h := collatzIter_add' j (k - j) n
      rw [Nat.add_sub_cancel' hjk] at h; rw [← h, hk]⟩
  · push_neg at hjk
    have hle : k ≤ j := by omega
    have h := collatzIter_add' k (j - k) n
    rw [Nat.add_sub_cancel' hle] at h
    rw [h, hk]
    rcases collatzIter_one_in_cycle (j - k) with h1 | h1 | h1
    · rw [h1]; exact collatzReaches_one
    · rw [h1]; exact collatzReaches_two
    · rw [h1]; exact collatzReaches_four

/-- collatzReaches n ↔ ∃ j, collatzIter j n ∈ {1, 2, 4} -/
theorem collatzReaches_iff_enters_cycle (n : ℕ) (hn : n ≥ 1) :
    collatzReaches n ↔ ∃ j, collatzIter j n = 1 ∨ collatzIter j n = 2 ∨ collatzIter j n = 4 := by
  constructor
  · intro hr
    obtain ⟨k, hk⟩ := hr
    exact ⟨k, Or.inl hk⟩
  · intro ⟨j, hj⟩
    rcases hj with h | h | h
    · exact ⟨j, h⟩
    · exact ⟨j + 1, by rw [collatzIter_add' j 1 n, h]; decide⟩
    · exact ⟨j + 2, by rw [collatzIter_add' j 2 n, h]; decide⟩

theorem syracuse_double (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    (3 * n + 1) / 2 + (3 * n + 1) / 2 = 3 * n + 1 := by omega

theorem collatzStep_step_one : collatzStep (collatzStep 1) = 2 := by decide

/-! ## ★ 軌道のシフト関係 -/

/-- ★ 奇数 n に対して collatzStep(2n+1) = 2·collatzStep(n) + 2 -/
theorem collatzStep_double_plus_one (n : ℕ) (hodd : n % 2 = 1) :
    collatzStep (2 * n + 1) = 2 * collatzStep n + 2 := by
  have h1 : (2 * n + 1) % 2 = 1 := by omega
  rw [collatzStep_odd_eq (2 * n + 1) h1, collatzStep_odd_eq n hodd]
  ring

/-- ★ collatzStep(collatzStep(2n+1)) = 3n+2（奇数 n） -/
theorem collatzStep_step_odd_double (n : ℕ) (hodd : n % 2 = 1) :
    collatzStep (collatzStep (2 * n + 1)) = 3 * n + 2 := by
  rw [collatzStep_double_plus_one n hodd]
  have heven : (2 * collatzStep n + 2) % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 (2 * collatzStep n + 2) heven]
  rw [collatzStep_odd_eq n hodd]
  omega
