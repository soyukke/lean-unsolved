import Mathlib

/-!
# ゴールドバッハ予想 (Goldbach's Conjecture)

2より大きい全ての偶数は、2つの素数の和で表せる。

1742年にゴールドバッハがオイラーに宛てた手紙で提唱。
約280年間未解決。
-/

/-- ゴールドバッハ予想: 2より大きい全ての偶数は2つの素数の和で表せる -/
def GoldbachConjecture : Prop :=
  ∀ n : ℕ, n > 2 → n % 2 = 0 → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

-- 小さい値での検証例
example : ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ 4 = p + q := by
  exact ⟨2, 2, by norm_num, by norm_num, by norm_num⟩

example : ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ 6 = p + q := by
  exact ⟨3, 3, by norm_num, by norm_num, by norm_num⟩
