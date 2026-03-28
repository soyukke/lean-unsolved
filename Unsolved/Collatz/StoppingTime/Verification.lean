import Unsolved.Collatz.StoppingTime.Defs

/-!
# コラッツ予想: 数値検証

有界ステップ判定関数 `collatzReachesBounded` を定義し、
n ≤ 1,000,000 の全自然数がコラッツ操作で1に到達することを形式的に検証する。

## 主要結果
- `collatzReachesBounded`: 有界ステップ判定関数
- `collatzReaches_of_bounded`: 健全性
- `collatzReachesBounded_complete`: 完全性
- `collatzReaches_le_1000000`: n ≤ 10^6 の完全検証
-/

/-! ## 小さい値の到達可能性 -/

example : collatzStep 3 = 10 := by decide
example : collatzStep 10 = 5 := by decide
example : collatzStep 5 = 16 := by decide

theorem collatzReaches_three : collatzReaches 3 := ⟨7, by decide⟩
theorem collatzReaches_five : collatzReaches 5 := ⟨5, by decide⟩
theorem collatzReaches_six : collatzReaches 6 := ⟨8, by decide⟩
theorem collatzReaches_seven : collatzReaches 7 := ⟨16, by decide⟩
theorem collatzReaches_eight : collatzReaches 8 := ⟨3, by decide⟩
theorem collatzReaches_nine : collatzReaches 9 := ⟨19, by decide⟩
theorem collatzReaches_ten : collatzReaches 10 := ⟨6, by decide⟩
theorem collatzReaches_eleven : collatzReaches 11 := ⟨14, by decide⟩
theorem collatzReaches_twelve : collatzReaches 12 := ⟨9, by decide⟩
theorem collatzReaches_thirteen : collatzReaches 13 := ⟨9, by decide⟩
theorem collatzReaches_fourteen : collatzReaches 14 := ⟨17, by decide⟩
theorem collatzReaches_fifteen : collatzReaches 15 := ⟨17, by decide⟩
theorem collatzReaches_sixteen : collatzReaches 16 := collatzReaches_pow_two 4
theorem collatzReaches_seventeen : collatzReaches 17 := ⟨12, by decide⟩
theorem collatzReaches_eighteen : collatzReaches 18 := ⟨20, by decide⟩
theorem collatzReaches_nineteen : collatzReaches 19 := ⟨20, by decide⟩
theorem collatzReaches_twenty : collatzReaches 20 := ⟨7, by decide⟩
theorem collatzReaches_21 : collatzReaches 21 := ⟨7, by decide⟩
theorem collatzReaches_22 : collatzReaches 22 := ⟨15, by decide⟩
theorem collatzReaches_23 : collatzReaches 23 := ⟨15, by decide⟩
theorem collatzReaches_24 : collatzReaches 24 := ⟨10, by decide⟩
theorem collatzReaches_25 : collatzReaches 25 := ⟨23, by decide⟩

/-- 1 ≤ n ≤ 25 の全ての自然数は collatzReaches -/
theorem collatzReaches_le_25 (n : ℕ) (hn1 : n ≥ 1) (hn25 : n ≤ 25) :
    collatzReaches n := by
  interval_cases n <;> first
    | exact collatzReaches_one
    | exact collatzReaches_two
    | exact collatzReaches_three
    | exact collatzReaches_four
    | exact collatzReaches_five
    | exact collatzReaches_six
    | exact collatzReaches_seven
    | exact collatzReaches_eight
    | exact collatzReaches_nine
    | exact collatzReaches_ten
    | exact collatzReaches_eleven
    | exact collatzReaches_twelve
    | exact collatzReaches_thirteen
    | exact collatzReaches_fourteen
    | exact collatzReaches_fifteen
    | exact collatzReaches_sixteen
    | exact collatzReaches_seventeen
    | exact collatzReaches_eighteen
    | exact collatzReaches_nineteen
    | exact collatzReaches_twenty
    | exact collatzReaches_21
    | exact collatzReaches_22
    | exact collatzReaches_23
    | exact collatzReaches_24
    | exact collatzReaches_25

set_option linter.style.nativeDecide false in
/-- 1 ≤ n ≤ 100 の全自然数はコラッツ操作で1に到達する -/
theorem collatzReaches_le_100 (n : ℕ) (hn1 : n ≥ 1) (hn100 : n ≤ 100) :
    collatzReaches n := by
  interval_cases n
    <;> first
    | exact ⟨0, by native_decide⟩
    | exact ⟨1, by native_decide⟩
    | exact ⟨2, by native_decide⟩
    | exact ⟨3, by native_decide⟩
    | exact ⟨4, by native_decide⟩
    | exact ⟨5, by native_decide⟩
    | exact ⟨6, by native_decide⟩
    | exact ⟨7, by native_decide⟩
    | exact ⟨8, by native_decide⟩
    | exact ⟨9, by native_decide⟩
    | exact ⟨10, by native_decide⟩
    | exact ⟨11, by native_decide⟩
    | exact ⟨12, by native_decide⟩
    | exact ⟨13, by native_decide⟩
    | exact ⟨14, by native_decide⟩
    | exact ⟨15, by native_decide⟩
    | exact ⟨16, by native_decide⟩
    | exact ⟨17, by native_decide⟩
    | exact ⟨18, by native_decide⟩
    | exact ⟨19, by native_decide⟩
    | exact ⟨20, by native_decide⟩
    | exact ⟨21, by native_decide⟩
    | exact ⟨22, by native_decide⟩
    | exact ⟨23, by native_decide⟩
    | exact ⟨24, by native_decide⟩
    | exact ⟨25, by native_decide⟩
    | exact ⟨26, by native_decide⟩
    | exact ⟨27, by native_decide⟩
    | exact ⟨29, by native_decide⟩
    | exact ⟨30, by native_decide⟩
    | exact ⟨32, by native_decide⟩
    | exact ⟨34, by native_decide⟩
    | exact ⟨35, by native_decide⟩
    | exact ⟨92, by native_decide⟩
    | exact ⟨102, by native_decide⟩
    | exact ⟨104, by native_decide⟩
    | exact ⟨105, by native_decide⟩
    | exact ⟨106, by native_decide⟩
    | exact ⟨107, by native_decide⟩
    | exact ⟨109, by native_decide⟩
    | exact ⟨110, by native_decide⟩
    | exact ⟨111, by native_decide⟩
    | exact ⟨112, by native_decide⟩
    | exact ⟨115, by native_decide⟩
    | exact ⟨118, by native_decide⟩

/-! ## 有界ステップ判定 -/

/-- collatzReachesBounded: steps ステップ以内に 1 に到達するか判定する補助関数 -/
def collatzReachesBounded (steps n : ℕ) : Bool :=
  match steps with
  | 0 => n == 1
  | k + 1 => n == 1 || collatzReachesBounded k (collatzStep n)

/-- collatzReachesBounded が true ならば collatzReaches が成り立つ -/
theorem collatzReaches_of_bounded (steps n : ℕ) (h : collatzReachesBounded steps n = true) :
    collatzReaches n := by
  induction steps generalizing n with
  | zero =>
    simp only [collatzReachesBounded, beq_iff_eq] at h
    exact ⟨0, by simp only [collatzIter_zero]; exact h⟩
  | succ k ih =>
    simp only [collatzReachesBounded, Bool.or_eq_true, beq_iff_eq] at h
    rcases h with h | h
    · exact ⟨0, by simp only [collatzIter_zero]; exact h⟩
    · obtain ⟨j, hj⟩ := ih _ h
      exact ⟨j + 1, by rw [collatzIter_succ]; exact hj⟩

/-- collatzReachesBounded の完全性: collatzReaches n → ∃ k, collatzReachesBounded k n -/
theorem collatzReachesBounded_complete {n : ℕ} (h : collatzReaches n) :
    ∃ k, collatzReachesBounded k n = true := by
  obtain ⟨k, hk⟩ := h
  exact ⟨k, by induction k generalizing n with
    | zero =>
      simp [collatzReachesBounded]
      change n = 1 at hk
      exact hk
    | succ k ih =>
      simp [collatzReachesBounded]
      by_cases h1 : n = 1
      · simp [h1]
      · right; exact ih (by rw [collatzIter_succ] at hk; exact hk)⟩

/-! ## n ≤ 1000 の検証 -/

set_option linter.style.nativeDecide false in
set_option maxHeartbeats 400000 in
/-- 1 ≤ n ≤ 1000 の全自然数はコラッツ操作で1に到達する -/
theorem collatzReaches_le_1000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 1000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 200
  revert n
  native_decide

set_option maxHeartbeats 4000000 in
set_option linter.style.nativeDecide false in
/-- 1 ≤ n ≤ 10000 の全自然数はコラッツ操作で1に到達する -/
theorem collatzReaches_le_10000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 10000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 300
  revert n
  native_decide

set_option maxHeartbeats 40000000 in
set_option linter.style.nativeDecide false in
/-- 1 ≤ n ≤ 50000 の全自然数はコラッツ操作で1に到達する -/
theorem collatzReaches_le_50000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 50000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 400
  revert n
  native_decide

/-! ## 範囲検証ヘルパー -/

/-- collatzAllReachBounded: range [lo, hi] の全要素が bounded steps で到達 -/
def collatzAllReachBounded (steps lo hi : ℕ) : Bool :=
  (List.range (hi - lo + 1)).all fun i => collatzReachesBounded steps (lo + i)

/-- collatzAllReachBounded が true ならば範囲内の全 n は collatzReaches -/
theorem collatzReaches_of_allReachBounded {steps lo hi : ℕ}
    (h : collatzAllReachBounded steps lo hi = true)
    (n : ℕ) (hlo : n ≥ lo) (hhi : n ≤ hi) :
    collatzReaches n := by
  apply collatzReaches_of_bounded steps
  simp only [collatzAllReachBounded, List.all_eq_true, List.mem_range] at h
  have := h (n - lo) (by omega)
  simp only [Nat.add_sub_cancel' (by omega : lo ≤ n)] at this
  exact this

/-! ## n ≤ 100000 の検証 -/

set_option linter.style.nativeDecide false in
theorem collatzAllReach_50001_75000 : collatzAllReachBounded 400 50001 75000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_75001_100000 : collatzAllReachBounded 400 75001 100000 = true := by
  native_decide

theorem collatzReaches_le_100000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 100000) :
    collatzReaches n := by
  by_cases h50 : n ≤ 50000
  · exact collatzReaches_le_50000 n hn1 h50
  · by_cases h75 : n ≤ 75000
    · exact collatzReaches_of_allReachBounded collatzAllReach_50001_75000 n (by omega) h75
    · exact collatzReaches_of_allReachBounded collatzAllReach_75001_100000 n (by omega) hn

/-! ## n ≤ 500000 の検証 -/

set_option linter.style.nativeDecide false in
theorem collatzAllReach_100001_150000 : collatzAllReachBounded 500 100001 150000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_150001_200000 : collatzAllReachBounded 500 150001 200000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_200001_250000 : collatzAllReachBounded 500 200001 250000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_250001_300000 : collatzAllReachBounded 500 250001 300000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_300001_350000 : collatzAllReachBounded 500 300001 350000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_350001_400000 : collatzAllReachBounded 500 350001 400000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_400001_450000 : collatzAllReachBounded 500 400001 450000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_450001_500000 : collatzAllReachBounded 500 450001 500000 = true := by
  native_decide

theorem collatzReaches_le_500000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 500000) :
    collatzReaches n := by
  by_cases h100 : n ≤ 100000
  · exact collatzReaches_le_100000 n hn1 h100
  · push_neg at h100
    by_cases h150 : n ≤ 150000
    · exact collatzReaches_of_allReachBounded collatzAllReach_100001_150000 n (by omega) h150
    · push_neg at h150
      by_cases h200 : n ≤ 200000
      · exact collatzReaches_of_allReachBounded collatzAllReach_150001_200000 n (by omega) h200
      · push_neg at h200
        by_cases h250 : n ≤ 250000
        · exact collatzReaches_of_allReachBounded collatzAllReach_200001_250000 n (by omega) h250
        · push_neg at h250
          by_cases h300 : n ≤ 300000
          · exact collatzReaches_of_allReachBounded collatzAllReach_250001_300000 n (by omega) h300
          · push_neg at h300
            by_cases h350 : n ≤ 350000
            · exact collatzReaches_of_allReachBounded collatzAllReach_300001_350000 n (by omega) h350
            · push_neg at h350
              by_cases h400 : n ≤ 400000
              · exact collatzReaches_of_allReachBounded collatzAllReach_350001_400000 n (by omega) h400
              · push_neg at h400
                by_cases h450 : n ≤ 450000
                · exact collatzReaches_of_allReachBounded collatzAllReach_400001_450000 n (by omega) h450
                · exact collatzReaches_of_allReachBounded collatzAllReach_450001_500000 n (by omega) hn

/-! ## n ≤ 1000000 の検証 -/

set_option linter.style.nativeDecide false in
theorem collatzAllReach_500001_550000 : collatzAllReachBounded 600 500001 550000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_550001_600000 : collatzAllReachBounded 600 550001 600000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_600001_650000 : collatzAllReachBounded 600 600001 650000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_650001_700000 : collatzAllReachBounded 600 650001 700000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_700001_750000 : collatzAllReachBounded 600 700001 750000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_750001_800000 : collatzAllReachBounded 600 750001 800000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_800001_850000 : collatzAllReachBounded 600 800001 850000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_850001_900000 : collatzAllReachBounded 600 850001 900000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_900001_950000 : collatzAllReachBounded 600 900001 950000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
theorem collatzAllReach_950001_1000000 : collatzAllReachBounded 600 950001 1000000 = true := by
  native_decide

theorem collatzReaches_le_1000000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 1000000) :
    collatzReaches n := by
  by_cases h500 : n ≤ 500000
  · exact collatzReaches_le_500000 n hn1 h500
  · push_neg at h500
    by_cases h550 : n ≤ 550000
    · exact collatzReaches_of_allReachBounded collatzAllReach_500001_550000 n (by omega) h550
    · push_neg at h550
      by_cases h600 : n ≤ 600000
      · exact collatzReaches_of_allReachBounded collatzAllReach_550001_600000 n (by omega) h600
      · push_neg at h600
        by_cases h650 : n ≤ 650000
        · exact collatzReaches_of_allReachBounded collatzAllReach_600001_650000 n (by omega) h650
        · push_neg at h650
          by_cases h700 : n ≤ 700000
          · exact collatzReaches_of_allReachBounded collatzAllReach_650001_700000 n (by omega) h700
          · push_neg at h700
            by_cases h750 : n ≤ 750000
            · exact collatzReaches_of_allReachBounded collatzAllReach_700001_750000 n (by omega) h750
            · push_neg at h750
              by_cases h800 : n ≤ 800000
              · exact collatzReaches_of_allReachBounded collatzAllReach_750001_800000 n (by omega) h800
              · push_neg at h800
                by_cases h850 : n ≤ 850000
                · exact collatzReaches_of_allReachBounded collatzAllReach_800001_850000 n (by omega) h850
                · push_neg at h850
                  by_cases h900 : n ≤ 900000
                  · exact collatzReaches_of_allReachBounded collatzAllReach_850001_900000 n (by omega) h900
                  · push_neg at h900
                    by_cases h950 : n ≤ 950000
                    · exact collatzReaches_of_allReachBounded collatzAllReach_900001_950000 n (by omega) h950
                    · exact collatzReaches_of_allReachBounded collatzAllReach_950001_1000000 n (by omega) hn

/-- コラッツ予想が n ≤ 1000000 で成り立つ -/
theorem collatzConjectureR_verified_le_1000000 :
    ∀ n : ℕ, n ≥ 1 → n ≤ 1000000 → collatzReaches n :=
  fun n hn1 hn => collatzReaches_le_1000000 n hn1 hn
