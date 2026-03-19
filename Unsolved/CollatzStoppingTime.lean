import Unsolved.CollatzStructure

/-!
# コラッツ予想 探索36,42: Stopping Time と s(2n) = s(n) + 1

コラッツ関数の stopping time（1に到達するまでのステップ数）を定義し、
偶数の基本性質 s(2n) = s(n) + 1 を形式証明する。

## 主要結果
- `collatzReaches n`: n が有限回の操作で1に到達する述語
- `stoppingTime`: 1に到達するまでの最小ステップ数
- `stoppingTime_double`: s(2n) = s(n) + 1 （n ≥ 1 のとき）
- `stoppingTime_pow_two_mul`: s(2^k * n) = s(n) + k （n ≥ 1 のとき）

## 探索42で追加
- `collatzReaches_of_pow_two_mul`: 2^k·n が1に到達 ⟹ n が1に到達
- `collatzReaches_pow_two_mul_iff`: 同値版
- `collatzReaches_four`: 4 が1に到達する
- `collatzReaches_step`: collatzStep に関して閉じている
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
  · -- stoppingTime (2*n) ≤ s + 1: s+1 ステップで到達するから
    apply Nat.find_le
    rw [collatzIter_succ_double s n (by omega)]
    exact collatzIter_stoppingTime n hr
  · -- stoppingTime (2*n) ≥ s + 1: s+1 未満では到達しないから
    by_contra hlt
    push_neg at hlt
    -- stoppingTime (2*n) ≤ s
    have hle : stoppingTime (2 * n) h2 ≤ s := by omega
    -- stoppingTime (2*n) ≥ 1 を示す
    have hst_pos : stoppingTime (2 * n) h2 ≥ 1 := by
      by_contra h0
      push_neg at h0
      have h0' : stoppingTime (2 * n) h2 = 0 := by omega
      have := collatzIter_stoppingTime (2 * n) h2
      rw [h0'] at this
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
    -- stoppingTime は Nat.find なので、同じ述語なら同じ値
    -- 2^(k+1)*n = 2*(2^k*n) を利用
    have heq : 2 ^ (k + 1) * n = 2 * (2 ^ k * n) := by ring
    -- stoppingTime_double を使うため、同値な形に変換
    have h_double := collatzReaches_double (2 ^ k * n) hpk hrk
    -- 目標を Nat.find の等価性で示す
    change Nat.find (collatzReaches_pow_two_mul (k + 1) n hn hr) = stoppingTime n hr + (k + 1)
    -- 2^(k+1)*n と 2*(2^k*n) は同じ値
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
      -- collatzStep (2^(n+1)) = 2^n
      have heven : (2 ^ (n + 1)) % 2 = 0 := by
        rw [Nat.pow_mod]; simp
      rw [collatzStep_even_eq_div2 _ heven]
      rw [show 2 ^ (n + 1) / 2 = 2 ^ n from by
        rw [pow_succ]; omega]
      rw [ihm]
      congr 1; omega

/-- ★ s(2^k) = k: 2のべき乗の stopping time はべき指数に等しい

    2^k は k ステップの半減で1に到達し、これが最小ステップ数。 -/
theorem stoppingTime_pow_two' (k : ℕ) :
    stoppingTime (2 ^ k) (collatzReaches_pow_two k) = k := by
  unfold stoppingTime
  apply le_antisymm
  · -- ≤ k: k ステップで到達するから
    exact Nat.find_le (collatz_pow_two k)
  · -- ≥ k: k 未満では到達しないから
    by_contra hlt
    push_neg at hlt
    set m := Nat.find (collatzReaches_pow_two k)
    have hfind := Nat.find_spec (collatzReaches_pow_two k)
    cases k with
    | zero => simp at hlt
    | succ k =>
      have hm_le : m ≤ k + 1 := by omega
      rw [collatzIter_pow_two_eq m (k + 1) hm_le] at hfind
      -- hfind : 2 ^ (k + 1 - m) = 1
      -- k + 1 - m ≥ 1 なので 2^(k+1-m) ≥ 2, 矛盾
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

/-! ## 7. 探索42: 追加補題 -/

/-! ### 7.1 到達可能性の同値性: 2^k·n ↔ n -/

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

/-! ### 7.2 特殊値の追加検証 -/

/-- 4 は1に到達する -/
theorem collatzReaches_four : collatzReaches 4 :=
  ⟨2, by decide⟩

/-- collatzReaches は collatzStep に関して閉じている:
    n が1に到達し n ≥ 2 ならば collatzStep n も1に到達する -/
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

/-- collatzStep に不動点はない（n ≥ 1 のとき）: collatzStep n ≠ n -/
theorem collatzStep_ne_self (n : ℕ) (hn : n ≥ 1) : collatzStep n ≠ n := by
  intro h
  by_cases hodd : n % 2 = 1
  · -- 奇数: collatzStep n = 3n+1 ≠ n (3n+1 > n for n ≥ 1)
    rw [collatzStep_odd_eq n hodd] at h
    omega
  · -- 偶数: collatzStep n = n/2 ≠ n (n/2 < n for n ≥ 1, even)
    have heven : n % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 n heven] at h
    omega

/-- 2-サイクルの非存在: collatzStep (collatzStep n) = n → n ≤ 2 -/
theorem collatzStep_step_ne_self (n : ℕ) (hn : n > 2) :
    collatzStep (collatzStep n) ≠ n := by
  intro h
  by_cases hodd : n % 2 = 1
  · -- n 奇数 → collatzStep n = 3n+1（偶数） → collatzStep(3n+1) = (3n+1)/2
    rw [collatzStep_odd_eq n hodd] at h
    have heven : (3 * n + 1) % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 (3 * n + 1) heven] at h
    -- (3n+1)/2 = n → 3n+1 = 2n → n = -1 (impossible in ℕ)
    omega
  · -- n 偶数 → collatzStep n = n/2
    have heven : n % 2 = 0 := by omega
    rw [collatzStep_even_eq_div2 n heven] at h
    by_cases hodd2 : (n / 2) % 2 = 1
    · -- n/2 奇数 → collatzStep(n/2) = 3(n/2)+1 = n → omega
      rw [collatzStep_odd_eq (n / 2) hodd2] at h
      omega
    · -- n/2 偶数 → collatzStep(n/2) = n/4 = n → omega
      have heven2 : (n / 2) % 2 = 0 := by omega
      rw [collatzStep_even_eq_div2 (n / 2) heven2] at h
      omega

/-- collatzStep 1 = 4 -/
theorem collatzStep_one_eq : collatzStep 1 = 4 := by decide

/-- collatzStep 4 = 2 -/
theorem collatzStep_four_eq : collatzStep 4 = 2 := by decide

/-- collatzStep 2 = 1 -/
theorem collatzStep_two_eq : collatzStep 2 = 1 := by decide

/-- 唯一の周期軌道 {1, 2, 4}: 1 → 4 → 2 → 1 の3ステップサイクル -/
theorem collatzIter_three_cycle : collatzIter 3 1 = 1 := by decide

/-- n ≥ 2 なら collatzReaches n ↔ collatzReaches (collatzStep n)
    collatzReaches_step と collatzReaches_of_step の統合 -/
theorem collatzReaches_step_iff (n : ℕ) (hn : n ≥ 2) :
    collatzReaches n ↔ collatzReaches (collatzStep n) :=
  ⟨collatzReaches_step n hn, collatzReaches_of_step n hn⟩

/-! ## 8. 探索44: stoppingTime の奇数に対する下界 -/

/-- 奇数 n > 1 に対して collatzIter 1 n > 1 :
    collatzStep n = 3n+1 ≥ 4 > 1 -/
private theorem collatzIter_one_odd_gt_one (n : ℕ) (hn : n > 1) (hodd : ¬ 2 ∣ n) :
    collatzIter 1 n ≠ 1 := by
  simp only [collatzIter_succ, collatzIter_zero]
  have hmod : n % 2 ≠ 0 := by
    intro h; exact hodd ⟨n / 2, by omega⟩
  rw [collatzStep_odd n hmod]
  omega

/-- 奇数 n > 1 の stopping time は 2 以上:
    奇数 → collatzStep で 3n+1（偶数） → もう1ステップ必要
    つまり n → 3n+1 → (3n+1)/2 で、少なくとも2ステップ -/
theorem stoppingTime_odd_ge_two (n : ℕ) (hn : n > 1) (hodd : ¬ 2 ∣ n)
    (hr : collatzReaches n) :
    stoppingTime n hr ≥ 2 := by
  -- ステップ0 で到達しないことを示す
  have h0 : collatzIter 0 n ≠ 1 := by change n ≠ 1; omega
  -- ステップ1 で到達しないことを示す
  have h1 : collatzIter 1 n ≠ 1 := collatzIter_one_odd_gt_one n hn hodd
  -- stoppingTime は最小の k で collatzIter k n = 1、0 と 1 はダメなので ≥ 2
  by_contra hlt
  push_neg at hlt
  have hle : stoppingTime n hr ≤ 1 := by omega
  have hst := collatzIter_stoppingTime n hr
  -- stoppingTime ≤ 1 だが、0 でも 1 でも collatzIter で 1 に到達しない
  have h01 : stoppingTime n hr = 0 ∨ stoppingTime n hr = 1 := by omega
  rcases h01 with h | h
  · rw [h] at hst; exact h0 hst
  · rw [h] at hst; exact h1 hst

/-! ## 9. 探索: collatzStep の合成性質 -/

/-- 偶数 n > 0 の collatzStep は n より小さい -/
theorem collatzStep_lt_of_even (n : ℕ) (hn : n > 0) (heven : n % 2 = 0) :
    collatzStep n < n := by
  rw [collatzStep_even_eq_div2 n heven]
  omega

/-! ## 10. collatzIter の追加性質 -/

/-- collatzIter 0 n = n -/
theorem collatzIter_zero' (n : ℕ) : collatzIter 0 n = n := by
  rfl

/-- collatzIter の結合法則的性質: collatzIter (a+b) n = collatzIter b (collatzIter a n)
    つまり「先に a 回適用してから b 回適用」と「まとめて a+b 回適用」は等しい -/
theorem collatzIter_add' (a b n : ℕ) :
    collatzIter (a + b) n = collatzIter b (collatzIter a n) := by
  induction a generalizing n with
  | zero => simp
  | succ a ih =>
    simp only [Nat.succ_add, collatzIter_succ]
    exact ih (collatzStep n)

/-- collatzReaches は推移的: n が m に到達し m が 1 に到達するなら n も 1 に到達する -/
theorem collatzReaches_trans (n m : ℕ) (k : ℕ)
    (hiter : collatzIter k n = m) (hm : collatzReaches m) : collatzReaches n := by
  obtain ⟨j, hj⟩ := hm
  exact ⟨k + j, by rw [collatzIter_add', hiter, hj]⟩

/-- n が1に到達するなら、k ステップ後の点も1に到達する（k が到達ステップ数以下のとき）
    軌道上の全ての中間点は1に到達する -/
theorem collatzReaches_of_iter_le (n : ℕ) (k j : ℕ)
    (hj : collatzIter j n = 1) (hk : k ≤ j) : collatzReaches (collatzIter k n) :=
  ⟨j - k, by
    have h := collatzIter_add' k (j - k) n
    rw [Nat.add_sub_cancel' hk] at h
    rw [← h, hj]⟩

/-! ## 11. stoppingTime の追加性質 -/

/-- collatzStep 3 = 10 -/
example : collatzStep 3 = 10 := by decide

/-- collatzStep 10 = 5 -/
example : collatzStep 10 = 5 := by decide

/-- collatzStep 5 = 16 -/
example : collatzStep 5 = 16 := by decide

/-- 3 はコラッツ操作で1に到達する -/
theorem collatzReaches_three : collatzReaches 3 :=
  ⟨7, by decide⟩

/-! ## 12. 小さい値の到達可能性 -/

/-- 5 はコラッツ操作で1に到達する -/
theorem collatzReaches_five : collatzReaches 5 :=
  ⟨5, by decide⟩

/-- 6 はコラッツ操作で1に到達する -/
theorem collatzReaches_six : collatzReaches 6 :=
  ⟨8, by decide⟩

/-- 7 はコラッツ操作で1に到達する -/
theorem collatzReaches_seven : collatzReaches 7 :=
  ⟨16, by decide⟩

/-! ## 13. 小さい値の stoppingTime 検証 -/

/-- collatzReaches 8 -/
theorem collatzReaches_eight : collatzReaches 8 :=
  ⟨3, by decide⟩

/-- collatzReaches 9 -/
theorem collatzReaches_nine : collatzReaches 9 :=
  ⟨19, by decide⟩

/-- collatzReaches 10 -/
theorem collatzReaches_ten : collatzReaches 10 :=
  ⟨6, by decide⟩

/-! ## 14. collatzReaches の合成性質 -/

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

/-! ## 15. collatzReaches の奇数版 -/

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

/-! ## 16. collatzReaches の合成 -/

/-- collatzReaches 13 -/
theorem collatzReaches_thirteen : collatzReaches 13 :=
  ⟨9, by decide⟩

/-- collatzReaches 15 -/
theorem collatzReaches_fifteen : collatzReaches 15 :=
  ⟨17, by decide⟩

/-- collatzReaches 16 -/
theorem collatzReaches_sixteen : collatzReaches 16 :=
  collatzReaches_pow_two 4

/-! ## 17. collatzReaches の偶数・奇数合成 -/

/-- n が偶数で collatzReaches (n/2) なら collatzReaches n -/
theorem collatzReaches_of_half (n : ℕ) (hn : n > 0) (heven : n % 2 = 0)
    (hr : collatzReaches (n / 2)) : collatzReaches n :=
  (collatzReaches_even_iff n hn heven).mpr hr

/-- collatzReaches 20 -/
theorem collatzReaches_twenty : collatzReaches 20 :=
  ⟨7, by decide⟩

/-! ## 18. stoppingTime の上界 -/

/-- collatzReaches 32 -/
theorem collatzReaches_thirtytwo : collatzReaches 32 :=
  collatzReaches_pow_two 5

/-- collatzReaches 64 -/
theorem collatzReaches_sixtyfour : collatzReaches 64 :=
  collatzReaches_pow_two 6

/-! ## 19. collatzReaches の2のべき乗によるリフト -/

/-- collatzReaches 100 -/
theorem collatzReaches_hundred : collatzReaches 100 :=
  ⟨25, by decide⟩

/-! ## 20. collatzReaches の基数による分類 -/

/-- collatzReaches 128 = 2^7 -/
theorem collatzReaches_128 : collatzReaches 128 :=
  collatzReaches_pow_two 7

/-- collatzReaches 256 = 2^8 -/
theorem collatzReaches_256 : collatzReaches 256 :=
  collatzReaches_pow_two 8

/-- collatzReaches 1024 = 2^10 -/
theorem collatzReaches_1024 : collatzReaches 1024 :=
  collatzReaches_pow_two 10

/-! ## 21. 大きな2のべき乗の到達性 -/

theorem collatzReaches_2048 : collatzReaches 2048 := collatzReaches_pow_two 11
theorem collatzReaches_4096 : collatzReaches 4096 := collatzReaches_pow_two 12

/-! ## 22. collatzReaches の系統的検証 -/

-- 奇数の到達性（小さい値の系統的検証）
theorem collatzReaches_17 : collatzReaches 17 := ⟨12, by decide⟩
theorem collatzReaches_19 : collatzReaches 19 := ⟨20, by decide⟩
theorem collatzReaches_21 : collatzReaches 21 := ⟨7, by decide⟩

/-! ## 23. collatzReaches の奇数系統検証（続き） -/

theorem collatzReaches_23 : collatzReaches 23 := ⟨15, by decide⟩
theorem collatzReaches_25 : collatzReaches 25 := ⟨23, by decide⟩

/-! ## 24. Syracuse 同値定理 -/

/-- 奇数 n > 1 に対して collatzReaches n ↔ collatzReaches ((3*n+1)/2)
    （Syracuse 関数による簡約） -/
theorem collatzReaches_syracuse_iff (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    collatzReaches n ↔ collatzReaches ((3 * n + 1) / 2) := by
  -- n → 3n+1 → (3n+1)/2 の2ステップを1つにまとめる
  have h1 := collatzReaches_odd_iff n hn hodd
  -- collatzReaches n ↔ collatzReaches (3n+1)
  have heven : (3 * n + 1) % 2 = 0 := by omega
  have hpos : 3 * n + 1 > 0 := by omega
  have h2 := collatzReaches_even_iff (3 * n + 1) hpos heven
  -- collatzReaches (3n+1) ↔ collatzReaches ((3n+1)/2)
  exact h1.trans h2

/-! ## 25. 全 n ≤ 25 の体系的検証 -/

/-- collatzReaches 11 -/
theorem collatzReaches_eleven : collatzReaches 11 := ⟨14, by decide⟩

/-- collatzReaches 12 -/
theorem collatzReaches_twelve : collatzReaches 12 := ⟨9, by decide⟩

/-- collatzReaches 14 -/
theorem collatzReaches_fourteen : collatzReaches 14 := ⟨17, by decide⟩

/-- collatzReaches 18 -/
theorem collatzReaches_eighteen : collatzReaches 18 := ⟨20, by decide⟩

/-- collatzReaches 22 -/
theorem collatzReaches_twentytwo : collatzReaches 22 := ⟨15, by decide⟩

/-- collatzReaches 24 -/
theorem collatzReaches_twentyfour : collatzReaches 24 := ⟨10, by decide⟩

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
    | exact collatzReaches_17
    | exact collatzReaches_eighteen
    | exact collatzReaches_19
    | exact collatzReaches_twenty
    | exact collatzReaches_21
    | exact collatzReaches_twentytwo
    | exact collatzReaches_23
    | exact collatzReaches_twentyfour
    | exact collatzReaches_25

/-! ## 26. 全 n ≤ 100 の体系的検証 -/

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

/-! ## 27. CollatzConjecture ↔ SyracuseConjecture -/

-- CollatzConjecture と SyracuseConjecture は Collatz.lean で定義済み。
-- ここでは同値性を証明する（collatzReaches_of_all_odd が先に必要なので後置）。

/-! ## 28. コラッツ予想は奇数で十分 -/

/-- コラッツ予想は奇数で十分:
    全奇数 n ≥ 1 が1に到達するならば、全自然数 n ≥ 1 が1に到達する。
    偶数 n は n/2 に帰着でき、n/2 < n なので強帰納法で完了する。 -/
theorem collatzReaches_of_all_odd
    (h : ∀ n : ℕ, n ≥ 1 → n % 2 = 1 → collatzReaches n) :
    ∀ n : ℕ, n ≥ 1 → collatzReaches n := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro hn
    by_cases hodd : n % 2 = 1
    · exact h n hn hodd
    · -- n は偶数
      have heven : n % 2 = 0 := by omega
      have hpos : n > 0 := by omega
      rw [collatzReaches_even_iff n hpos heven]
      have hdiv : n / 2 < n := by omega
      have hdiv_pos : n / 2 ≥ 1 := by omega
      exact ih (n / 2) hdiv hdiv_pos

/-- コラッツ予想は奇数 > 1 で十分（1は自明に到達）:
    全ての奇数 n > 1 が1に到達するならば、全自然数 n ≥ 1 が1に到達する。 -/
theorem collatzReaches_of_all_odd_gt1
    (h : ∀ n : ℕ, n > 1 → n % 2 = 1 → collatzReaches n) :
    ∀ n : ℕ, n ≥ 1 → collatzReaches n := by
  apply collatzReaches_of_all_odd
  intro n hn hodd
  by_cases h1 : n = 1
  · rw [h1]; exact collatzReaches_one
  · exact h n (by omega) hodd

/-! ## 30. collatzReaches 版のコラッツ予想の同値形式化 -/

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

/-! ## 31. 偶数の stoppingTime ≥ 1 -/

/-- 偶数 n ≥ 2 の stopping time は 1 以上:
    偶数 n ≥ 2 ≠ 1 なので 0 ステップでは到達しない -/
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

/-! ## 32. 有界ステップ判定と n ≤ 1000 の検証 -/

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

set_option linter.style.nativeDecide false in
set_option maxHeartbeats 400000 in
-- native_decide で 1000×200 ステップの有界探索を実行するため heartbeats を増加
/-- 1 ≤ n ≤ 1000 の全自然数はコラッツ操作で1に到達する -/
theorem collatzReaches_le_1000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 1000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 200
  revert n
  native_decide

set_option maxHeartbeats 4000000 in
set_option linter.style.nativeDecide false in
/-- 1 ≤ n ≤ 10000 の全自然数はコラッツ操作で1に到達する
    n ≤ 10000 で最大のステップ数は n=6171 の261ステップ。上界300で十分。 -/
theorem collatzReaches_le_10000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 10000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 300
  revert n
  native_decide

set_option maxHeartbeats 40000000 in
set_option linter.style.nativeDecide false in
/-- 1 ≤ n ≤ 50000 の全自然数はコラッツ操作で1に到達する
    n ≤ 50000 で最大のステップ数は n=35655 の323ステップ。上界400で十分。 -/
theorem collatzReaches_le_50000 (n : ℕ) (hn1 : n ≥ 1) (hn : n ≤ 50000) :
    collatzReaches n := by
  apply collatzReaches_of_bounded 400
  revert n
  native_decide

/-! ## コラッツ到達性のリフト -/

/-- collatzReaches 0 は偽: collatzStep 0 = 0 なので 0 は永遠に 0 のまま -/
theorem not_collatzReaches_zero : ¬collatzReaches 0 := by
  intro ⟨k, hk⟩
  induction k with
  | zero => change 0 = 1 at hk; omega
  | succ k ih =>
    rw [collatzIter_succ] at hk
    have hstep : collatzStep 0 = 0 := by
      simp [collatzStep]
    rw [hstep] at hk
    exact ih hk

/-! ## 3-サイクルの完全分類 -/

/-- collatzIter 3 n = n となる n は {0, 1, 2, 4} のみ。
    唯一の非自明な3-サイクルは 1→4→2→1。
    n = 0 は不動点（collatzStep 0 = 0）、n ∈ {1,2,4} はサイクル。
    n > 4 では collatzStep の場合分け（偶奇の3段展開、8通り）により矛盾。 -/
theorem collatzIter_three_periodic (n : ℕ) (h : collatzIter 3 n = n) :
    n = 0 ∨ n = 1 ∨ n = 2 ∨ n = 4 := by
  -- collatzIter 3 n = collatzStep (collatzStep (collatzStep n)) を展開し、
  -- collatzStep の if 分岐を simp で展開、split で場合分け、omega で算術処理
  simp [collatzStep] at h
  split at h <;> split at h <;> split at h <;> omega
