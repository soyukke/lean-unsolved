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
