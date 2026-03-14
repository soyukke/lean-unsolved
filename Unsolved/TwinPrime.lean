import Mathlib

/-!
# 双子素数予想 (Twin Prime Conjecture)

差が2の素数の組（双子素数）は無限に存在する。

例: (3,5), (5,7), (11,13), (17,19), (29,31), ...
-/

/-- 双子素数予想: 差が2の素数の組は無限に存在する -/
def TwinPrimeConjecture : Prop :=
  ∀ N : ℕ, ∃ p : ℕ, p > N ∧ Nat.Prime p ∧ Nat.Prime (p + 2)

-- (3, 5) は双子素数
example : Nat.Prime 3 ∧ Nat.Prime 5 := by
  constructor
  · exact Nat.prime_iff.mpr ⟨by omega, by omega⟩
  · exact Nat.prime_iff.mpr ⟨by omega, by omega⟩

-- (11, 13) は双子素数
example : Nat.Prime 11 ∧ Nat.Prime 13 := by
  constructor
  · exact Nat.prime_iff.mpr ⟨by omega, by omega⟩
  · exact Nat.prime_iff.mpr ⟨by omega, by omega⟩
