import Mathlib

/-!
# コラッツ予想 (Collatz Conjecture)
懸賞金: 日本の数学者が120万ドルを提示

任意の正の整数 n に対して、以下の操作を繰り返すと必ず1に到達する:
- n が偶数なら n / 2
- n が奇数なら 3 * n + 1
-/

/-- コラッツ関数: 偶数なら半分、奇数なら3倍して1を足す -/
def collatzStep (n : ℕ) : ℕ :=
  if n % 2 = 0 then n / 2 else 3 * n + 1

/-- n からコラッツ操作を k 回適用した結果 -/
def collatzIter : ℕ → ℕ → ℕ
  | 0, n => n
  | k + 1, n => collatzIter k (collatzStep n)

/-- コラッツ予想: 任意の正の整数は有限回の操作で1に到達する -/
def CollatzConjecture : Prop :=
  ∀ n : ℕ, n ≥ 1 → ∃ k : ℕ, collatzIter k n = 1

-- 小さい値での検証例
example : collatzStep 6 = 3 := by decide
example : collatzStep 3 = 10 := by decide
example : collatzStep 10 = 5 := by decide
example : collatzStep 5 = 16 := by decide

/-! ## 部分的結果: 偶数に対する性質 -/

/-- 偶数のコラッツステップは n / 2 -/
theorem collatzStep_even (n : ℕ) (h : n % 2 = 0) : collatzStep n = n / 2 := by
  simp [collatzStep, h]

/-- 奇数のコラッツステップは 3 * n + 1 -/
theorem collatzStep_odd (n : ℕ) (h : n % 2 ≠ 0) : collatzStep n = 3 * n + 1 := by
  simp [collatzStep, h]

/-! ## 部分的結果: 2のべき乗は1に到達する -/

/-- collatzIter 0 は恒等関数 -/
@[simp] theorem collatzIter_zero (n : ℕ) : collatzIter 0 n = n := rfl

/-- collatzIter の展開 -/
@[simp] theorem collatzIter_succ (k n : ℕ) :
    collatzIter (k + 1) n = collatzIter k (collatzStep n) := rfl

/-- 2^(k+1) は偶数 -/
theorem pow_two_succ_even (k : ℕ) : 2 ^ (k + 1) % 2 = 0 := by
  have : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
  omega

/-- 2^(k+1) / 2 = 2^k -/
theorem pow_two_succ_div_two (k : ℕ) : 2 ^ (k + 1) / 2 = 2 ^ k := by
  have : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
  omega

/-- 2のべき乗のコラッツステップは半分になる -/
theorem collatzStep_pow_two (k : ℕ) : collatzStep (2 ^ (k + 1)) = 2 ^ k := by
  simp [collatzStep, pow_two_succ_even, pow_two_succ_div_two]

/-- 2のべき乗に対してコラッツ操作を繰り返すと1に到達する -/
theorem collatz_pow_two : ∀ k : ℕ, collatzIter k (2 ^ k) = 1 := by
  intro k
  induction k with
  | zero => rfl
  | succ n ih =>
    simp only [collatzIter_succ, collatzStep_pow_two]
    exact ih

/-! ## Syracuse関数版コラッツ予想 -/

/-! ### 2-adic付値 (v2)
自然数 n が 2 で何回割り切れるかを返す。
n = 0 のときは 0 を返す。
-/

/-- 2-adic付値: n を 2 で割れる回数 -/
def v2 (n : ℕ) : ℕ :=
  if n = 0 then 0
  else if n % 2 ≠ 0 then 0
  else 1 + v2 (n / 2)
termination_by n
decreasing_by
  omega

/-- Syracuse関数: 奇数 n に対して (3n+1) / 2^v2(3n+1) を返す -/
def syracuse (n : ℕ) : ℕ :=
  let m := 3 * n + 1
  m / 2 ^ v2 m

/-- Syracuse反復: syracuse を k 回適用する -/
def syracuseIter : ℕ → ℕ → ℕ
  | 0, n => n
  | k + 1, n => syracuseIter k (syracuse n)

/-- Syracuse版コラッツ予想: 任意の奇数の正の整数に対し、
    有限回のSyracuse反復で1に到達する -/
def SyracuseConjecture : Prop :=
  ∀ n : ℕ, n ≥ 1 → n % 2 = 1 → ∃ k : ℕ, syracuseIter k n = 1

/-! ### v2 の基本補題 -/

@[simp] theorem v2_zero : v2 0 = 0 := by
  unfold v2; simp

theorem v2_odd (n : ℕ) (h : n % 2 ≠ 0) : v2 n = 0 := by
  unfold v2
  split
  · rfl
  · rfl

theorem v2_even (n : ℕ) (hn : n ≠ 0) (h : n % 2 = 0) : v2 n = 1 + v2 (n / 2) := by
  conv_lhs => rw [v2]
  have h1 : ¬(n = 0) := hn
  have h2 : ¬(n % 2 ≠ 0) := by omega
  simp only [h1, ↓reduceIte, h2]

theorem v2_two_mul (n : ℕ) (hn : n ≠ 0) : v2 (2 * n) = 1 + v2 n := by
  rw [v2_even (2 * n) (by omega) (by omega)]
  have : 2 * n / 2 = n := Nat.mul_div_cancel_left n (by omega)
  rw [this]

/-- 奇数との積の v2: a が奇数なら v2(a*b) = v2(b) -/
theorem v2_odd_mul (a b : ℕ) (ha : a % 2 = 1) : v2 (a * b) = v2 b := by
  induction b using Nat.strongRecOn with
  | ind b ih =>
    by_cases hb0 : b = 0
    · subst hb0; simp [v2]
    · by_cases hb_odd : b % 2 = 1
      · -- a*b is odd (odd * odd = odd)
        have hab_odd : (a * b) % 2 = 1 := by
          rw [Nat.mul_mod]; simp [ha, hb_odd]
        rw [v2_odd _ (by omega), v2_odd _ (by omega)]
      · -- b is even: b = 2*(b/2), a*b = 2*(a*(b/2))
        push_neg at hb_odd
        have hb_even : b % 2 = 0 := by omega
        have hb2_lt : b / 2 < b := Nat.div_lt_self (by omega) (by omega)
        have hab_eq : a * b = 2 * (a * (b / 2)) := by
          have hb2 : b = 2 * (b / 2) := by omega
          conv_lhs => rw [hb2]
          ring
        have hab_ne : a * (b / 2) ≠ 0 := by
          intro h; simp at h; omega
        rw [hab_eq, v2_two_mul _ hab_ne, ih _ hb2_lt,
            v2_even b hb0 hb_even]

/-- v2 の乗法性: v2(a*b) = v2(a) + v2(b) (a,b > 0) -/
theorem v2_mul (a b : ℕ) (ha : a > 0) (hb : b > 0) : v2 (a * b) = v2 a + v2 b := by
  induction a using Nat.strongRecOn with
  | ind a ih =>
    by_cases ha_odd : a % 2 = 1
    · -- a odd: v2(a) = 0
      have hva : v2 a = 0 := v2_odd a (by omega)
      rw [v2_odd_mul a b ha_odd, hva]; simp
    · -- a even: a = 2*(a/2)
      push_neg at ha_odd
      have ha_even : a % 2 = 0 := by omega
      have ha2_lt : a / 2 < a := Nat.div_lt_self ha (by omega)
      have ha2_pos : a / 2 > 0 := by omega
      have hab_eq : a * b = 2 * ((a / 2) * b) := by
        have ha2 : a = 2 * (a / 2) := by omega
        conv_lhs => rw [ha2]
        ring
      have hab_ne : (a / 2) * b ≠ 0 := by
        intro h; simp at h; omega
      rw [hab_eq, v2_two_mul _ hab_ne, ih _ ha2_lt ha2_pos]
      have hva : v2 a = 1 + v2 (a / 2) := v2_even a (by omega) ha_even
      omega

/-! ### Syracuse の基本定理 -/

private theorem v2_4 : v2 4 = 2 := by unfold v2; unfold v2; unfold v2; simp

/-- 1 は Syracuse 関数の不動点 -/
theorem syracuse_one : syracuse 1 = 1 := by
  change (3 * 1 + 1) / 2 ^ v2 (3 * 1 + 1) = 1
  norm_num [v2_4]

/-! ### 小さい値での検証例 -/

-- v2 の展開を繰り返す補助マクロの代わりに unfold を繰り返す
example : v2 4 = 2 := v2_4
example : v2 8 = 3 := by unfold v2; unfold v2; unfold v2; unfold v2; simp
example : v2 6 = 1 := by unfold v2; unfold v2; simp
example : v2 12 = 2 := by unfold v2; unfold v2; unfold v2; simp

-- syracuse の検証
example : syracuse 1 = 1 := syracuse_one

private theorem v2_10 : v2 10 = 1 := by unfold v2; unfold v2; simp
private theorem v2_16 : v2 16 = 4 := by unfold v2; unfold v2; unfold v2; unfold v2; unfold v2; simp
private theorem v2_22 : v2 22 = 1 := by unfold v2; unfold v2; simp
private theorem v2_28 : v2 28 = 2 := by unfold v2; unfold v2; unfold v2; simp
private theorem v2_34 : v2 34 = 1 := by unfold v2; unfold v2; simp

example : syracuse 3 = 5 := by
  change 10 / 2 ^ v2 10 = 5; rw [v2_10]; norm_num

example : syracuse 5 = 1 := by
  change 16 / 2 ^ v2 16 = 1; rw [v2_16]; norm_num

example : syracuse 7 = 11 := by
  change 22 / 2 ^ v2 22 = 11; rw [v2_22]; norm_num

example : syracuse 9 = 7 := by
  change 28 / 2 ^ v2 28 = 7; rw [v2_28]; norm_num

example : syracuse 11 = 17 := by
  change 34 / 2 ^ v2 34 = 17; rw [v2_34]; norm_num

/-! ### syracuseIter の基本補題 -/

@[simp] theorem syracuseIter_zero (n : ℕ) : syracuseIter 0 n = n := rfl

@[simp] theorem syracuseIter_succ (k n : ℕ) :
    syracuseIter (k + 1) n = syracuseIter k (syracuse n) := rfl

private theorem syracuse_3 : syracuse 3 = 5 := by
  change 10 / 2 ^ v2 10 = 5; rw [v2_10]; norm_num

private theorem syracuse_5 : syracuse 5 = 1 := by
  change 16 / 2 ^ v2 16 = 1; rw [v2_16]; norm_num

/-- 3 は2ステップで1に到達する: 3 → 5 → 1 -/
example : syracuseIter 2 3 = 1 := by
  simp only [syracuseIter_succ, syracuseIter_zero]
  rw [syracuse_3, syracuse_5]
