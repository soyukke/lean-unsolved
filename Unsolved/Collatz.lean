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
example : collatzStep 6 = 3 := by native_decide
example : collatzStep 3 = 10 := by native_decide
example : collatzStep 10 = 5 := by native_decide
example : collatzStep 5 = 16 := by native_decide
