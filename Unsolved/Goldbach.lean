import Mathlib

/-!
# ゴールドバッハ予想 (Goldbach's Conjecture)

2より大きい全ての偶数は、2つの素数の和で表せる。

1742年にゴールドバッハがオイラーに宛てた手紙で提唱。
約280年間未解決。

## 探索の概要

### 探索1: Mathlib調査
- Mathlibにゴールドバッハ予想の形式化は存在しない
- 利用可能な素数関連定理:
  - `Nat.Prime` の定義と基本性質 (`Data.Nat.Prime.Defs`)
  - 素数判定 (`norm_num` で小さい数は自動判定)
  - 素因数分解、最小素因数 (`minFac`)
  - 互いに素、素数のmod性質 (`Prime.eq_two_or_odd`)

### 探索2: Python数値実験 (scripts/goldbach_explore.py)
- 4 ≤ n ≤ 10000 の全偶数で予想成立を確認
- g(n)=1 となる偶数は 4, 6, 8, 12 の4個のみ
- g(n) は n/6 ≡ 0 のとき特に大きい（3の倍数の効果）
- Hardy-Littlewood 予想 g(n) ~ C₂·n/(ln n)² と概ね一致

### 探索3: Lean検証例の追加
- 8, 10, 12, 20, 100 での具体的検証
- ゴールドバッハ性の述語定義
-/

/-- ゴールドバッハ予想: 2より大きい全ての偶数は2つの素数の和で表せる -/
def GoldbachConjecture : Prop :=
  ∀ n : ℕ, n > 2 → n % 2 = 0 → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

/-- 偶数 n がゴールドバッハ性を持つ: 2つの素数の和で表せる -/
def IsGoldbach (n : ℕ) : Prop :=
  ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

/-! ## 小さい値での検証例 -/

-- 4 = 2 + 2
example : IsGoldbach 4 := ⟨2, 2, by norm_num, by norm_num, by norm_num⟩

-- 6 = 3 + 3
example : IsGoldbach 6 := ⟨3, 3, by norm_num, by norm_num, by norm_num⟩

-- 8 = 3 + 5
example : IsGoldbach 8 := ⟨3, 5, by norm_num, by norm_num, by norm_num⟩

-- 10 = 3 + 7
example : IsGoldbach 10 := ⟨3, 7, by norm_num, by norm_num, by norm_num⟩

-- 12 = 5 + 7
example : IsGoldbach 12 := ⟨5, 7, by norm_num, by norm_num, by norm_num⟩

-- 20 = 3 + 17
example : IsGoldbach 20 := ⟨3, 17, by norm_num, by norm_num, by norm_num⟩

-- 100 = 3 + 97
example : IsGoldbach 100 := ⟨3, 97, by norm_num, by norm_num, by norm_num⟩

/-! ## ゴールドバッハ性の基本補題 -/

/-- ゴールドバッハ予想は IsGoldbach を用いて同値に書ける -/
theorem goldbachConjecture_iff :
    GoldbachConjecture ↔ ∀ n : ℕ, n > 2 → n % 2 = 0 → IsGoldbach n := by
  unfold GoldbachConjecture IsGoldbach
  rfl

/-- 2つの素数の和は2以上 -/
theorem IsGoldbach.two_le {n : ℕ} (h : IsGoldbach n) : n ≥ 2 := by
  obtain ⟨p, q, hp, hq, heq⟩ := h
  have hp2 := hp.two_le
  have hq2 := hq.two_le
  omega

/-- 素数 p と素数 q の和は IsGoldbach -/
theorem isGoldbach_of_prime_add {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q) :
    IsGoldbach (p + q) :=
  ⟨p, q, hp, hq, rfl⟩

/-- 2つの奇素数の和は偶数 -/
theorem even_of_odd_prime_add {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) : Even (p + q) := by
  have hoddp := hp.odd_of_ne_two hp2
  have hoddq := hq.odd_of_ne_two hq2
  exact hoddp.add_odd hoddq
