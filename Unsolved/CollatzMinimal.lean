import Unsolved.CollatzAccel

/-!
# コラッツ予想 探索37: 最小反例の制約

コラッツ予想の「最小反例」を定義し、その性質を形式化する。
最小反例が存在するとすれば、非常に強い制約を満たさなければならないことを示す。

## 主要結果

### 定義
- `reachesOne n`: n からコラッツ操作を有限回適用して1に到達する
- `isMinimalCounterexample n`: n は最小反例（1に到達しない最小の正整数）

### reachesOne の基本補題
- `reachesOne_one`: 1 は 1 に到達する
- `reachesOne_of_collatzStep`: collatzStep n が1に到達するなら n も到達する
- `reachesOne_double`: n が1に到達するなら 2*n も到達する
- `reachesOne_of_syracuse`: syracuse n が1に到達するなら n も到達する（奇数nに対して）

### 最小反例の制約
- `minimal_counterexample_gt_one`: 最小反例は n > 1
- `minimal_counterexample_odd`: 最小反例は奇数
- `minimal_counterexample_mod4`: 最小反例は n ≡ 3 (mod 4)
-/

/-! ## 1. reachesOne の定義 -/

/-- n からコラッツ操作を有限回適用して1に到達する -/
def reachesOne (n : ℕ) : Prop := ∃ k, collatzIter k n = 1

/-! ## 2. reachesOne の基本補題 -/

/-- 1 は 1 に到達する -/
theorem reachesOne_one : reachesOne 1 :=
  ⟨0, rfl⟩

/-- collatzStep n が1に到達するなら n も1に到達する -/
theorem reachesOne_of_collatzStep (n : ℕ) (h : reachesOne (collatzStep n)) :
    reachesOne n := by
  obtain ⟨k, hk⟩ := h
  exact ⟨k + 1, hk⟩

/-- n が1に到達するなら 2*n も1に到達する (n > 0) -/
theorem reachesOne_double (n : ℕ) (_hn : n > 0) (h : reachesOne n) :
    reachesOne (2 * n) := by
  apply reachesOne_of_collatzStep
  have heven : (2 * n) % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 (2 * n) heven]
  have : 2 * n / 2 = n := by omega
  rwa [this]

/-! ## 3. collatzIter の推移性 -/

/-- collatzIter の合成: collatzIter (a + b) n = collatzIter b (collatzIter a n) -/
theorem collatzIter_add (a b n : ℕ) :
    collatzIter (a + b) n = collatzIter b (collatzIter a n) := by
  induction a generalizing n with
  | zero => simp
  | succ a ih =>
    simp only [Nat.succ_add, collatzIter_succ]
    exact ih (collatzStep n)

/-- reachesOne の推移性: collatzIter k n = m かつ reachesOne m → reachesOne n -/
theorem reachesOne_of_collatzIter (n m k : ℕ)
    (hiter : collatzIter k n = m) (hm : reachesOne m) : reachesOne n := by
  obtain ⟨j, hj⟩ := hm
  exact ⟨k + j, by rw [collatzIter_add, hiter, hj]⟩

/-! ## 4. 偶数に対する collatzIter と除算の関係 -/

/-- 2^v2(m) は m を割り切る -/
private theorem pow_v2_dvd' (m : ℕ) : 2 ^ v2 m ∣ m := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hm : m = 0
    · subst hm; simp
    · by_cases hmod : m % 2 ≠ 0
      · rw [v2_odd m hmod]; simp
      · push_neg at hmod
        rw [v2_even m hm hmod]
        have ih_half := ih (m / 2) (by omega)
        change 2 ^ (1 + v2 (m / 2)) ∣ m
        rw [pow_add, pow_one]
        calc 2 * 2 ^ v2 (m / 2) ∣ 2 * (m / 2) := Nat.mul_dvd_mul_left 2 ih_half
          _ ∣ m := by exact ⟨1, by omega⟩

/-- 偶数 m を collatzIter k 回で m / 2^k にする:
    m が 2^k で割り切れるとき、collatzIter k m = m / 2^k -/
private theorem collatzIter_of_pow_dvd (m k : ℕ) (hdvd : 2 ^ k ∣ m) (hm : m > 0) :
    collatzIter k m = m / 2 ^ k := by
  induction k generalizing m with
  | zero => simp
  | succ k ih =>
    simp only [collatzIter_succ]
    have h2k1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
    rw [h2k1] at hdvd
    have h2_dvd : 2 ∣ m := Dvd.dvd.trans (dvd_mul_right 2 (2 ^ k)) hdvd
    have heven : m % 2 = 0 := Nat.mod_eq_zero_of_dvd h2_dvd
    rw [collatzStep_even_eq_div2 m heven]
    have hdvd_half : 2 ^ k ∣ m / 2 := by
      obtain ⟨c, hc⟩ := hdvd
      -- hc : m = 2 * 2 ^ k * c
      -- m / 2 = (2 * 2^k * c) / 2 = 2^k * c
      refine ⟨c, ?_⟩
      have hm_eq : m = 2 * 2 ^ k * c := hc
      rw [hm_eq, Nat.mul_assoc, Nat.mul_div_cancel_left _ (by omega)]
    rw [ih (m / 2) hdvd_half (by omega)]
    rw [Nat.div_div_eq_div_mul, h2k1]

/-! ## 5. syracuse と collatzIter の関係 -/

/-- 奇数 n に対して、collatzIter (v2(3n+1) + 1) n = syracuse n -/
private theorem collatzIter_to_syracuse (n : ℕ) (_hn : n ≥ 1) (hodd : n % 2 = 1) :
    collatzIter (v2 (3 * n + 1) + 1) n = syracuse n := by
  simp only [collatzIter_succ]
  rw [collatzStep_odd_eq n hodd]
  rw [collatzIter_of_pow_dvd (3 * n + 1) (v2 (3 * n + 1))
    (pow_v2_dvd' (3 * n + 1)) (by omega)]
  -- syracuse n = (3 * n + 1) / 2 ^ v2 (3 * n + 1)
  rfl

/-- syracuse n が1に到達するなら、奇数 n ≥ 1 も1に到達する -/
theorem reachesOne_of_syracuse (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (h : reachesOne (syracuse n)) : reachesOne n :=
  reachesOne_of_collatzIter n (syracuse n)
    (v2 (3 * n + 1) + 1) (collatzIter_to_syracuse n hn hodd) h

/-! ## 6. 最小反例の定義 -/

/-- 最小反例: 1に到達しない最小の正整数 -/
def isMinimalCounterexample (n : ℕ) : Prop :=
  n ≥ 1 ∧ ¬reachesOne n ∧ ∀ m, m ≥ 1 → m < n → reachesOne m

/-! ## 7. 最小反例は n > 1 -/

/-- 最小反例は n > 1 -/
theorem minimal_counterexample_gt_one (n : ℕ) (h : isMinimalCounterexample n) :
    n > 1 := by
  obtain ⟨hge, hnr, _⟩ := h
  by_contra hle
  push_neg at hle
  have : n = 1 := by omega
  subst this
  exact hnr reachesOne_one

/-! ## 8. 最小反例は奇数 -/

/-- 最小反例は奇数 -/
theorem minimal_counterexample_odd (n : ℕ) (h : isMinimalCounterexample n) :
    n % 2 = 1 := by
  have hge := h.1
  have hnr := h.2.1
  have hmin := h.2.2
  by_contra hodd
  have heven : n % 2 = 0 := by omega
  have hgt1 := minimal_counterexample_gt_one n h
  have hstep : collatzStep n = n / 2 := collatzStep_even_eq_div2 n heven
  have hr : reachesOne (n / 2) := hmin (n / 2) (by omega) (by omega)
  rw [← hstep] at hr
  exact hnr (reachesOne_of_collatzStep n hr)

/-! ## 9. 最小反例に対する syracuse 下降からの矛盾 -/

/-- 最小反例に対して、syracuse n < n ならば矛盾 -/
private theorem minimal_contradiction_of_syracuse_lt (n : ℕ) (h : isMinimalCounterexample n)
    (hlt : syracuse n < n) : False := by
  have hge := h.1
  have hnr := h.2.1
  have hmin := h.2.2
  have hodd := minimal_counterexample_odd n h
  have hsyr_pos : syracuse n ≥ 1 := syracuse_pos n hge hodd
  exact hnr (reachesOne_of_syracuse n hge hodd (hmin (syracuse n) hsyr_pos hlt))

/-! ## 10. 最小反例は n ≡ 3 (mod 4) -/

/-- 最小反例は n ≡ 3 (mod 4) -/
theorem minimal_counterexample_mod4 (n : ℕ) (h : isMinimalCounterexample n) :
    n % 4 = 3 := by
  have hodd := minimal_counterexample_odd n h
  have hgt1 := minimal_counterexample_gt_one n h
  by_contra hne
  have hmod4 : n % 4 = 1 := by omega
  exact minimal_contradiction_of_syracuse_lt n h (syracuse_lt_of_mod4_eq1 n hmod4 hgt1)

/-! ## 11. 小さい値の reachesOne の具体的検証 -/

/-- reachesOne 3: 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1 -/
theorem reachesOne_three : reachesOne 3 :=
  ⟨7, by decide⟩

/-! ## 12. 数値検証 -/

example : reachesOne 1 := reachesOne_one
example : reachesOne 2 := ⟨1, by decide⟩
example : reachesOne 3 := reachesOne_three
example : reachesOne 4 := ⟨2, by decide⟩
example : reachesOne 5 := ⟨5, by decide⟩
example : reachesOne 6 := ⟨8, by decide⟩
example : reachesOne 7 := ⟨16, by decide⟩
example : reachesOne 8 := ⟨3, by decide⟩

/-! ## 13. 最小反例とコラッツ予想の関係 -/

/-- 最小反例が存在するならコラッツ予想は偽 -/
theorem collatz_false_of_minimal (n : ℕ) (h : isMinimalCounterexample n) :
    ¬CollatzConjecture := by
  intro hcc
  exact h.2.1 (hcc n h.1)

/-- コラッツ予想が真なら最小反例は存在しない -/
theorem no_minimal_of_collatz (hcc : CollatzConjecture) :
    ∀ n, ¬isMinimalCounterexample n := by
  intro n ⟨hge, hnr, _⟩
  exact hnr (hcc n hge)
