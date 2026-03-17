import Unsolved.CollatzStructure

/-!
# コラッツ予想 探索36: Stopping Time と s(2n) = s(n) + 1

コラッツ関数の stopping time（1に到達するまでのステップ数）を定義し、
偶数の基本性質 s(2n) = s(n) + 1 を形式証明する。

## 主要結果
- `collatzReaches n`: n が有限回の操作で1に到達する述語
- `stoppingTime`: 1に到達するまでの最小ステップ数
- `stoppingTime_double`: s(2n) = s(n) + 1 （n ≥ 1 のとき）
- `stoppingTime_pow_two_mul`: s(2^k * n) = s(n) + k （n ≥ 1 のとき）
-/

/-! ## 1. コラッツ到達可能性 -/

/-- n がコラッツ操作で1に到達する: ∃ k, collatzIter k n = 1 -/
def collatzReaches (n : ℕ) : Prop :=
  ∃ k : ℕ, collatzIter k n = 1

/-- 1 はコラッツ操作で1に到達する（0ステップ） -/
theorem collatzReaches_one : collatzReaches 1 :=
  ⟨0, rfl⟩

/-- 2のべき乗はコラッツ操作で1に到達する -/
theorem collatzReaches_pow_two (k : ℕ) : collatzReaches (2 ^ k) :=
  ⟨k, collatz_pow_two k⟩

/-! ## 2. collatzIter の移行補題 -/

/-- n > 0 のとき collatzIter (k+1) (2*n) = collatzIter k n -/
theorem collatzIter_succ_double (k n : ℕ) (hn : n > 0) :
    collatzIter (k + 1) (2 * n) = collatzIter k n := by
  simp only [collatzIter_succ]
  rw [collatzStep_double n hn]

/-! ## 3. Stopping Time の定義 -/

/-- stopping time: 1に到達するまでの最小ステップ数
    collatzReaches n が成り立つことを前提とする -/
noncomputable def stoppingTime (n : ℕ) (h : collatzReaches n) : ℕ :=
  Nat.find h

/-- stoppingTime の特性: stoppingTime ステップで1に到達する -/
theorem collatzIter_stoppingTime (n : ℕ) (h : collatzReaches n) :
    collatzIter (stoppingTime n h) n = 1 :=
  Nat.find_spec h

/-- stoppingTime の最小性: k < stoppingTime ならば collatzIter k n ≠ 1 -/
theorem stoppingTime_min (n : ℕ) (h : collatzReaches n) (k : ℕ)
    (hk : k < stoppingTime n h) : collatzIter k n ≠ 1 :=
  Nat.find_min h hk

/-- 1 の stopping time は 0 -/
theorem stoppingTime_one : stoppingTime 1 collatzReaches_one = 0 := by
  unfold stoppingTime
  rw [Nat.find_eq_zero]
  rfl

/-! ## 4. s(2n) = s(n) + 1 の証明 -/

/-- n が1に到達するならば 2n も1に到達する -/
theorem collatzReaches_double (n : ℕ) (hn : n ≥ 1) (h : collatzReaches n) :
    collatzReaches (2 * n) := by
  obtain ⟨k, hk⟩ := h
  exact ⟨k + 1, by rw [collatzIter_succ_double k n (by omega), hk]⟩

/-- 2n が1に到達するならば n も1に到達する（n ≥ 1 のとき） -/
theorem collatzReaches_of_double (n : ℕ) (hn : n ≥ 1) (h : collatzReaches (2 * n)) :
    collatzReaches n := by
  obtain ⟨k, hk⟩ := h
  cases k with
  | zero =>
    -- collatzIter 0 (2*n) = 2*n = 1 だが 2*n ≥ 2, 矛盾
    change 2 * n = 1 at hk; omega
  | succ k =>
    rw [collatzIter_succ_double k n (by omega)] at hk
    exact ⟨k, hk⟩

/-- 核心補題: collatzIter (k+1) (2*n) = 1 ⟺ collatzIter k n = 1 （n > 0 のとき） -/
theorem collatzIter_double_iff (k n : ℕ) (hn : n > 0) :
    collatzIter (k + 1) (2 * n) = 1 ↔ collatzIter k n = 1 := by
  rw [collatzIter_succ_double k n hn]

/-- ★主定理: s(2n) = s(n) + 1 （n ≥ 1 のとき）

  直感的には明らか: 2n は偶数なので最初の1ステップで n/2 = n になり、
  その後は n と同じ軌道を辿る。よって stopping time は1つ多い。 -/
theorem stoppingTime_double (n : ℕ) (hn : n ≥ 1)
    (hr : collatzReaches n) :
    stoppingTime (2 * n) (collatzReaches_double n hn hr) = stoppingTime n hr + 1 := by
  set s := stoppingTime n hr with hs_def
  set h2 := collatzReaches_double n hn hr
  apply le_antisymm
  · -- stoppingTime (2*n) ≤ s + 1: s+1 ステップで到達するから
    apply Nat.find_le
    rw [collatzIter_succ_double s n (by omega)]
    exact collatzIter_stoppingTime n hr
  · -- stoppingTime (2*n) ≥ s + 1: s+1 未満では到達しないから
    by_contra hlt
    push_neg at hlt
    -- stoppingTime (2*n) ≤ s
    have hle : stoppingTime (2 * n) h2 ≤ s := by omega
    -- stoppingTime (2*n) = 0 ならば 2*n = 1 だが n ≥ 1 なので矛盾
    -- stoppingTime (2*n) ≥ 1 を示す
    have hst_pos : stoppingTime (2 * n) h2 ≥ 1 := by
      by_contra h0
      push_neg at h0
      have h0' : stoppingTime (2 * n) h2 = 0 := by omega
      have := collatzIter_stoppingTime (2 * n) h2
      rw [h0'] at this
      -- collatzIter 0 (2*n) = 2*n = 1 だが 2*n ≥ 2
      change 2 * n = 1 at this; omega
    -- stoppingTime (2*n) = m + 1 と書ける
    obtain ⟨m, hm_eq⟩ : ∃ m, stoppingTime (2 * n) h2 = m + 1 :=
      ⟨stoppingTime (2 * n) h2 - 1, by omega⟩
    -- collatzIter (m+1) (2*n) = 1
    have hreach := collatzIter_stoppingTime (2 * n) h2
    rw [hm_eq] at hreach
    -- = collatzIter m n
    rw [collatzIter_succ_double m n (by omega)] at hreach
    -- m < s なので矛盾
    have : m < s := by omega
    exact stoppingTime_min n hr m this hreach

/-! ## 5. 応用: 2^k * n に対する一般化 -/

/-- n が1に到達するならば 2^k * n も1に到達する （n ≥ 1 のとき） -/
theorem collatzReaches_pow_two_mul (k n : ℕ) (hn : n ≥ 1) (hr : collatzReaches n) :
    collatzReaches (2 ^ k * n) := by
  induction k with
  | zero => simpa
  | succ k ih =>
    have : 2 ^ (k + 1) * n = 2 * (2 ^ k * n) := by ring
    rw [this]
    apply collatzReaches_double
    · have : 2 ^ k * n ≥ 1 * 1 := by
        apply Nat.mul_le_mul
        · exact Nat.one_le_pow k 2 (by omega)
        · exact hn
      omega
    · exact ih

/-- stoppingTime は証明の選択に依存しない -/
theorem stoppingTime_proof_irrel (n : ℕ) (h1 h2 : collatzReaches n) :
    stoppingTime n h1 = stoppingTime n h2 := by
  simp [stoppingTime]

/-- ★一般化: s(2^k * n) = s(n) + k （n ≥ 1 のとき） -/
theorem stoppingTime_pow_two_mul (k n : ℕ) (hn : n ≥ 1) (hr : collatzReaches n) :
    stoppingTime (2 ^ k * n) (collatzReaches_pow_two_mul k n hn hr)
    = stoppingTime n hr + k := by
  induction k with
  | zero =>
    simp [stoppingTime]
  | succ k ih =>
    have hpk : 2 ^ k * n ≥ 1 := by
      have : 2 ^ k * n ≥ 1 * 1 := by
        apply Nat.mul_le_mul
        · exact Nat.one_le_pow k 2 (by omega)
        · exact hn
      omega
    set hrk := collatzReaches_pow_two_mul k n hn hr
    -- 2^(k+1) * n = 2 * (2^k * n) を使って書き換え
    have heq : 2 ^ (k + 1) * n = 2 * (2 ^ k * n) := by ring
    -- stoppingTime は値が同じなら証明に依存しない
    -- Nat.find の congr を使う
    conv_lhs => rw [show 2 ^ (k + 1) * n = 2 * (2 ^ k * n) from by ring]
    rw [stoppingTime_proof_irrel _ _ (collatzReaches_double (2 ^ k * n) hpk hrk),
        stoppingTime_double (2 ^ k * n) hpk hrk, ih]
    omega

/-! ## 6. 特殊値の検証 -/

/-- 2 は1に到達する -/
theorem collatzReaches_two : collatzReaches 2 :=
  ⟨1, by decide⟩

/-- s(2) = 1: stoppingTime_double の特殊ケースとしても得られる -/
theorem stoppingTime_two : stoppingTime 2 collatzReaches_two = 1 := by
  have hr_double := collatzReaches_double 1 (by omega) collatzReaches_one
  conv_lhs => rw [show (2 : ℕ) = 2 * 1 from by omega]
  rw [stoppingTime_proof_irrel _ _ hr_double,
      stoppingTime_double 1 (by omega) collatzReaches_one, stoppingTime_one]
