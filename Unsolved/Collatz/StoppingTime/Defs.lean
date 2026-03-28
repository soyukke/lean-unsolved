import Unsolved.Collatz.Structure

/-!
# コラッツ予想: Stopping Time の基本定義と性質

コラッツ関数の stopping time（1に到達するまでのステップ数）を定義し、
基本的な性質を形式証明する。

## 主要結果
- `collatzReaches n`: n が有限回の操作で1に到達する述語
- `stoppingTime`: 1に到達するまでの最小ステップ数
- `stoppingTime_double`: s(2n) = s(n) + 1 （n ≥ 1 のとき）
- `stoppingTime_pow_two_mul`: s(2^k * n) = s(n) + k （n ≥ 1 のとき）
- `collatzIter_add'`: collatzIter の結合法則
- `CollatzConjectureR` / `SyracuseConjectureR`: 同値な予想形式
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
    change 2 * n = 1 at hk; omega
  | succ k =>
    rw [collatzIter_succ_double k n (by omega)] at hk
    exact ⟨k, hk⟩

/-- 核心補題: collatzIter (k+1) (2*n) = 1 ⟺ collatzIter k n = 1 （n > 0 のとき） -/
theorem collatzIter_double_iff (k n : ℕ) (hn : n > 0) :
    collatzIter (k + 1) (2 * n) = 1 ↔ collatzIter k n = 1 := by
  rw [collatzIter_succ_double k n hn]

/-- stoppingTime は証明の選択に依存しない -/
theorem stoppingTime_proof_irrel (n : ℕ) (h1 h2 : collatzReaches n) :
    stoppingTime n h1 = stoppingTime n h2 := by
  simp [stoppingTime]

/-- ★主定理: s(2n) = s(n) + 1 （n ≥ 1 のとき）

  直感的には明らか: 2n は偶数なので最初の1ステップで n/2 = n になり、
  その後は n と同じ軌道を辿る。よって stopping time は1つ多い。 -/
theorem stoppingTime_double (n : ℕ) (hn : n ≥ 1)
    (hr : collatzReaches n) :
    stoppingTime (2 * n) (collatzReaches_double n hn hr) = stoppingTime n hr + 1 := by
  set s := stoppingTime n hr with hs_def
  set h2 := collatzReaches_double n hn hr
  apply le_antisymm
  · apply Nat.find_le
    rw [collatzIter_succ_double s n (by omega)]
    exact collatzIter_stoppingTime n hr
  · by_contra hlt
    push_neg at hlt
    have hle : stoppingTime (2 * n) h2 ≤ s := by omega
    have hst_pos : stoppingTime (2 * n) h2 ≥ 1 := by
      by_contra h0
      push_neg at h0
      have h0' : stoppingTime (2 * n) h2 = 0 := by omega
      have := collatzIter_stoppingTime (2 * n) h2
      rw [h0'] at this
      change 2 * n = 1 at this; omega
    obtain ⟨m, hm_eq⟩ : ∃ m, stoppingTime (2 * n) h2 = m + 1 :=
      ⟨stoppingTime (2 * n) h2 - 1, by omega⟩
    have hreach := collatzIter_stoppingTime (2 * n) h2
    rw [hm_eq] at hreach
    rw [collatzIter_succ_double m n (by omega)] at hreach
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
    have heq : 2 ^ (k + 1) * n = 2 * (2 ^ k * n) := by ring
    have h_double := collatzReaches_double (2 ^ k * n) hpk hrk
    change Nat.find (collatzReaches_pow_two_mul (k + 1) n hn hr) = stoppingTime n hr + (k + 1)
    have : (fun j => collatzIter j (2 ^ (k + 1) * n) = 1)
         = (fun j => collatzIter j (2 * (2 ^ k * n)) = 1) := by
      ext j; rw [heq]
    rw [show stoppingTime n hr + (k + 1) = (stoppingTime n hr + k) + 1 from by omega,
        ← ih, ← stoppingTime_double (2 ^ k * n) hpk hrk]
    change Nat.find _ = Nat.find _
    congr 1

/-- 補助補題: m ≤ n のとき collatzIter m (2^n) = 2^(n-m) -/
private theorem collatzIter_pow_two_eq (m n : ℕ) (hmn : m ≤ n) :
    collatzIter m (2 ^ n) = 2 ^ (n - m) := by
  induction m generalizing n with
  | zero => simp
  | succ m ih =>
    cases n with
    | zero => omega
    | succ n =>
      rw [collatzIter_succ]
      have : m ≤ n := by omega
      have ihm := ih n this
      have heven : (2 ^ (n + 1)) % 2 = 0 := by
        rw [Nat.pow_mod]; simp
      rw [collatzStep_even_eq_div2 _ heven]
      rw [show 2 ^ (n + 1) / 2 = 2 ^ n from by
        rw [pow_succ]; omega]
      rw [ihm]
      congr 1; omega

/-- ★ s(2^k) = k: 2のべき乗の stopping time はべき指数に等しい -/
theorem stoppingTime_pow_two' (k : ℕ) :
    stoppingTime (2 ^ k) (collatzReaches_pow_two k) = k := by
  unfold stoppingTime
  apply le_antisymm
  · exact Nat.find_le (collatz_pow_two k)
  · by_contra hlt
    push_neg at hlt
    set m := Nat.find (collatzReaches_pow_two k)
    have hfind := Nat.find_spec (collatzReaches_pow_two k)
    cases k with
    | zero => simp at hlt
    | succ k =>
      have hm_le : m ≤ k + 1 := by omega
      rw [collatzIter_pow_two_eq m (k + 1) hm_le] at hfind
      have hge1 : k + 1 - m ≥ 1 := by omega
      have : 2 ^ (k + 1 - m) ≥ 2 ^ 1 := Nat.pow_le_pow_right (by omega : 0 < 2) hge1
      simp at this
      omega

/-! ## 6. 特殊値の検証 -/

/-- 2 は1に到達する -/
theorem collatzReaches_two : collatzReaches 2 :=
  ⟨1, by decide⟩

/-- s(2) = 1 -/
theorem stoppingTime_two : stoppingTime 2 collatzReaches_two = 1 := by
  unfold stoppingTime
  rw [Nat.find_eq_iff]
  constructor
  · decide
  · intro m hm
    interval_cases m
    simp [collatzIter]

/-! ## 7. 到達可能性の同値性: 2^k·n ↔ n -/

/-- 2^k·n が1に到達する ⟹ n が1に到達する （n ≥ 1 のとき） -/
theorem collatzReaches_of_pow_two_mul (k n : ℕ) (hn : n ≥ 1)
    (h : collatzReaches (2 ^ k * n)) : collatzReaches n := by
  induction k with
  | zero => simpa using h
  | succ k ih =>
    apply ih
    have heq : 2 ^ (k + 1) * n = 2 * (2 ^ k * n) := by ring
    rw [heq] at h
    have hpk : 2 ^ k * n ≥ 1 := by
      have : 2 ^ k * n ≥ 1 * 1 :=
        Nat.mul_le_mul (Nat.one_le_pow k 2 (by omega)) hn
      omega
    exact collatzReaches_of_double (2 ^ k * n) hpk h

/-- ★ 2^k·n が1に到達する ⟺ n が1に到達する （n ≥ 1 のとき） -/
theorem collatzReaches_pow_two_mul_iff (k n : ℕ) (hn : n ≥ 1) :
    collatzReaches (2 ^ k * n) ↔ collatzReaches n :=
  ⟨collatzReaches_of_pow_two_mul k n hn, collatzReaches_pow_two_mul k n hn⟩

/-- 4 は1に到達する -/
theorem collatzReaches_four : collatzReaches 4 :=
  ⟨2, by decide⟩

/-- collatzReaches は collatzStep に関して閉じている -/
theorem collatzReaches_step (n : ℕ) (hn : n ≥ 2) (hr : collatzReaches n) :
    collatzReaches (collatzStep n) := by
  obtain ⟨k, hk⟩ := hr
  cases k with
  | zero =>
    change n = 1 at hk; omega
  | succ k =>
    exact ⟨k, by rwa [collatzIter_succ] at hk⟩

/-- collatzStep n が1に到達するならば n も1に到達する（n ≥ 2 のとき） -/
theorem collatzReaches_of_step (n : ℕ) (hn : n ≥ 2) (hr : collatzReaches (collatzStep n)) :
    collatzReaches n := by
  obtain ⟨k, hk⟩ := hr
  exact ⟨k + 1, by rw [collatzIter_succ]; exact hk⟩

/-! ## 短いサイクルの非存在 -/

/-- collatzStep に不動点はない（n ≥ 1 のとき） -/
theorem collatzStep_ne_self (n : ℕ) (hn : n ≥ 1) : collatzStep n ≠ n := by
  intro h
  by_cases hodd : n % 2 = 1
  · rw [collatzStep_odd_eq n hodd] at h; omega
  · have heven : n % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 n heven] at h; omega

/-- 2-サイクルの非存在: collatzStep (collatzStep n) = n → n ≤ 2 -/
theorem collatzStep_step_ne_self (n : ℕ) (hn : n > 2) :
    collatzStep (collatzStep n) ≠ n := by
  intro h
  by_cases hodd : n % 2 = 1
  · rw [collatzStep_odd_eq n hodd] at h
    have heven : (3 * n + 1) % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 (3 * n + 1) heven] at h; omega
  · have heven : n % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 n heven] at h
    by_cases hodd2 : (n / 2) % 2 = 1
    · rw [collatzStep_odd_eq (n / 2) hodd2] at h; omega
    · have heven2 : (n / 2) % 2 = 0 := by omega
      rw [collatzStep_even_eq_div2 (n / 2) heven2] at h; omega

theorem collatzStep_one_eq : collatzStep 1 = 4 := by decide
theorem collatzStep_four_eq : collatzStep 4 = 2 := by decide
theorem collatzStep_two_eq : collatzStep 2 = 1 := by decide

/-- 唯一の周期軌道 {1, 2, 4}: 1 → 4 → 2 → 1 の3ステップサイクル -/
theorem collatzIter_three_cycle : collatzIter 3 1 = 1 := by decide

/-- n ≥ 2 なら collatzReaches n ↔ collatzReaches (collatzStep n) -/
theorem collatzReaches_step_iff (n : ℕ) (hn : n ≥ 2) :
    collatzReaches n ↔ collatzReaches (collatzStep n) :=
  ⟨collatzReaches_step n hn, collatzReaches_of_step n hn⟩

/-! ## stoppingTime の奇数に対する下界 -/

/-- 奇数 n > 1 に対して collatzIter 1 n > 1 -/
private theorem collatzIter_one_odd_gt_one (n : ℕ) (hn : n > 1) (hodd : ¬ 2 ∣ n) :
    collatzIter 1 n ≠ 1 := by
  simp only [collatzIter_succ, collatzIter_zero]
  have hmod : n % 2 ≠ 0 := by
    intro h; exact hodd ⟨n / 2, by omega⟩
  rw [collatzStep_odd n hmod]; omega

/-- 奇数 n > 1 の stopping time は 2 以上 -/
theorem stoppingTime_odd_ge_two (n : ℕ) (hn : n > 1) (hodd : ¬ 2 ∣ n)
    (hr : collatzReaches n) :
    stoppingTime n hr ≥ 2 := by
  have h0 : collatzIter 0 n ≠ 1 := by change n ≠ 1; omega
  have h1 : collatzIter 1 n ≠ 1 := collatzIter_one_odd_gt_one n hn hodd
  by_contra hlt
  push_neg at hlt
  have hle : stoppingTime n hr ≤ 1 := by omega
  have hst := collatzIter_stoppingTime n hr
  have h01 : stoppingTime n hr = 0 ∨ stoppingTime n hr = 1 := by omega
  rcases h01 with h | h
  · rw [h] at hst; exact h0 hst
  · rw [h] at hst; exact h1 hst

/-- 偶数 n > 0 の collatzStep は n より小さい -/
theorem collatzStep_lt_of_even (n : ℕ) (hn : n > 0) (heven : n % 2 = 0) :
    collatzStep n < n := by
  rw [collatzStep_even_eq_div2 n heven]; omega

/-! ## collatzIter の結合法則 -/

/-- collatzIter 0 n = n -/
theorem collatzIter_zero' (n : ℕ) : collatzIter 0 n = n := by rfl

/-- collatzIter の結合法則: collatzIter (a+b) n = collatzIter b (collatzIter a n) -/
theorem collatzIter_add' (a b n : ℕ) :
    collatzIter (a + b) n = collatzIter b (collatzIter a n) := by
  induction a generalizing n with
  | zero => simp
  | succ a ih =>
    simp only [Nat.succ_add, collatzIter_succ]
    exact ih (collatzStep n)

/-- collatzReaches は推移的 -/
theorem collatzReaches_trans (n m : ℕ) (k : ℕ)
    (hiter : collatzIter k n = m) (hm : collatzReaches m) : collatzReaches n := by
  obtain ⟨j, hj⟩ := hm
  exact ⟨k + j, by rw [collatzIter_add', hiter, hj]⟩

/-- 軌道上の全ての中間点は1に到達する -/
theorem collatzReaches_of_iter_le (n : ℕ) (k j : ℕ)
    (hj : collatzIter j n = 1) (hk : k ≤ j) : collatzReaches (collatzIter k n) :=
  ⟨j - k, by
    have h := collatzIter_add' k (j - k) n
    rw [Nat.add_sub_cancel' hk] at h
    rw [← h, hj]⟩

/-! ## collatzReaches の合成性質 -/

/-- n が偶数で n > 0 なら collatzReaches n ↔ collatzReaches (n/2) -/
theorem collatzReaches_even_iff (n : ℕ) (_hn : n > 0) (heven : n % 2 = 0) :
    collatzReaches n ↔ collatzReaches (n / 2) := by
  constructor
  · intro ⟨k, hk⟩
    cases k with
    | zero => change n = 1 at hk; omega
    | succ k =>
      rw [collatzIter_succ, collatzStep_even_eq_div2 n heven] at hk
      exact ⟨k, hk⟩
  · intro ⟨k, hk⟩
    exact ⟨k + 1, by rw [collatzIter_succ, collatzStep_even_eq_div2 n heven, hk]⟩

/-- 奇数 n > 1 なら collatzReaches n ↔ collatzReaches (3*n+1) -/
theorem collatzReaches_odd_iff (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    collatzReaches n ↔ collatzReaches (3 * n + 1) := by
  constructor
  · intro ⟨k, hk⟩
    cases k with
    | zero => change n = 1 at hk; omega
    | succ k =>
      rw [collatzIter_succ, collatzStep_odd_eq n hodd] at hk
      exact ⟨k, hk⟩
  · intro ⟨k, hk⟩
    exact ⟨k + 1, by rw [collatzIter_succ, collatzStep_odd_eq n hodd, hk]⟩

/-- n が偶数で collatzReaches (n/2) なら collatzReaches n -/
theorem collatzReaches_of_half (n : ℕ) (hn : n > 0) (heven : n % 2 = 0)
    (hr : collatzReaches (n / 2)) : collatzReaches n :=
  (collatzReaches_even_iff n hn heven).mpr hr

/-- 奇数 n > 1 に対して collatzReaches n ↔ collatzReaches ((3*n+1)/2) -/
theorem collatzReaches_syracuse_iff (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    collatzReaches n ↔ collatzReaches ((3 * n + 1) / 2) := by
  have h1 := collatzReaches_odd_iff n hn hodd
  have heven : (3 * n + 1) % 2 = 0 := by omega
  have hpos : 3 * n + 1 > 0 := by omega
  have h2 := collatzReaches_even_iff (3 * n + 1) hpos heven
  exact h1.trans h2

/-! ## collatzReaches 0 は偽 -/

/-- collatzReaches 0 は偽: collatzStep 0 = 0 なので 0 は永遠に 0 のまま -/
theorem not_collatzReaches_zero : ¬collatzReaches 0 := by
  intro ⟨k, hk⟩
  induction k with
  | zero => change 0 = 1 at hk; omega
  | succ k ih =>
    rw [collatzIter_succ] at hk
    have hstep : collatzStep 0 = 0 := by simp [collatzStep]
    rw [hstep] at hk
    exact ih hk

/-- collatzReaches n ならば n > 0 -/
theorem collatzReaches_pos {n : ℕ} (h : collatzReaches n) : n > 0 := by
  by_contra hle
  push_neg at hle
  have : n = 0 := by omega
  subst this
  exact not_collatzReaches_zero h

/-! ## コラッツ予想は奇数で十分 -/

/-- 全奇数 n ≥ 1 が1に到達するならば、全自然数 n ≥ 1 が1に到達する -/
theorem collatzReaches_of_all_odd
    (h : ∀ n : ℕ, n ≥ 1 → n % 2 = 1 → collatzReaches n) :
    ∀ n : ℕ, n ≥ 1 → collatzReaches n := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro hn
    by_cases hodd : n % 2 = 1
    · exact h n hn hodd
    · have heven : n % 2 = 0 := by omega
      have hpos : n > 0 := by omega
      rw [collatzReaches_even_iff n hpos heven]
      have hdiv : n / 2 < n := by omega
      have hdiv_pos : n / 2 ≥ 1 := by omega
      exact ih (n / 2) hdiv hdiv_pos

/-- 全ての奇数 n > 1 が1に到達するならば、全自然数 n ≥ 1 が1に到達する -/
theorem collatzReaches_of_all_odd_gt1
    (h : ∀ n : ℕ, n > 1 → n % 2 = 1 → collatzReaches n) :
    ∀ n : ℕ, n ≥ 1 → collatzReaches n := by
  apply collatzReaches_of_all_odd
  intro n hn hodd
  by_cases h1 : n = 1
  · rw [h1]; exact collatzReaches_one
  · exact h n (by omega) hodd

/-! ## collatzReaches 版コラッツ予想の同値形式 -/

/-- collatzReaches 版コラッツ予想 -/
def CollatzConjectureR : Prop := ∀ n : ℕ, n ≥ 1 → collatzReaches n

/-- collatzReaches 版 Syracuse 予想 -/
def SyracuseConjectureR : Prop := ∀ n : ℕ, n ≥ 1 → n % 2 = 1 → collatzReaches n

/-- collatzReaches 版: コラッツ予想と Syracuse 予想は同値 -/
theorem collatzR_iff_syracuseR : CollatzConjectureR ↔ SyracuseConjectureR := by
  constructor
  · intro h n hn _hodd; exact h n hn
  · intro h n hn
    exact collatzReaches_of_all_odd (fun m hm hodd => h m hm hodd) n hn

/-! ## stoppingTime の下界 -/

/-- 偶数 n ≥ 2 の stopping time は 1 以上 -/
theorem stoppingTime_even_ge_one (n : ℕ) (hn : n ≥ 2) (heven : n % 2 = 0)
    (hr : collatzReaches n) :
    stoppingTime n hr ≥ 1 := by
  by_contra h0
  push_neg at h0
  have h0' : stoppingTime n hr = 0 := by omega
  have := collatzIter_stoppingTime n hr
  rw [h0'] at this
  change n = 1 at this; omega

/-- n ≥ 2 の stopping time は 1 以上 -/
theorem stoppingTime_ge_one (n : ℕ) (hn : n ≥ 2)
    (hr : collatzReaches n) :
    stoppingTime n hr ≥ 1 := by
  by_contra h0
  push_neg at h0
  have h0' : stoppingTime n hr = 0 := by omega
  have := collatzIter_stoppingTime n hr
  rw [h0'] at this
  change n = 1 at this; omega
