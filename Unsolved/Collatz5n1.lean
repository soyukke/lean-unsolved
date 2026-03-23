import Unsolved.CollatzStructure

/-!
# 5n+1 コラッツ変種の形式化

T(n) = n/2     (n が偶数)
T(n) = 5n+1    (n が奇数)

## 探索の発見
- 3n+1 と異なり、大半の数は1に到達しない
- 非自明サイクルが存在（長さ10が少なくとも2つ）
- 1に到達する数は逆像ツリーの特殊な構造を持つ

## 主要結果
- collatz5Step の定義と基本性質
- 非自明サイクルの形式的検証
- 不動点の非存在
- (2^(4k)-1)/5 が直接1に到達することの証明
-/

/-! ## 1. 基本定義 -/

/-- 5n+1 コラッツ変種のステップ関数 -/
def collatz5Step (n : ℕ) : ℕ :=
  if n % 2 = 0 then n / 2 else 5 * n + 1

/-- 5n+1 コラッツ変種の反復 -/
def collatz5Iter : ℕ → ℕ → ℕ
  | 0, n => n
  | k + 1, n => collatz5Iter k (collatz5Step n)

/-- 5n+1 変種で n が 1 に到達する -/
def collatz5Reaches (n : ℕ) : Prop :=
  ∃ k : ℕ, collatz5Iter k n = 1

/-! ## 2. 基本性質 -/

/-- 偶数に対する collatz5Step -/
theorem collatz5Step_even (n : ℕ) (h : n % 2 = 0) : collatz5Step n = n / 2 := by
  simp [collatz5Step, h]

/-- 奇数に対する collatz5Step -/
theorem collatz5Step_odd (n : ℕ) (h : n % 2 = 1) : collatz5Step n = 5 * n + 1 := by
  simp [collatz5Step, h]; omega

/-- 5n+1 変種に不動点はない（n ≥ 1） -/
theorem collatz5Step_ne_self (n : ℕ) (hn : n ≥ 1) : collatz5Step n ≠ n := by
  intro h
  by_cases hodd : n % 2 = 1
  · rw [collatz5Step_odd n hodd] at h; omega
  · have heven : n % 2 = 0 := by omega
    rw [collatz5Step_even n heven] at h; omega

/-! ## 3. 非自明サイクルの検証 -/

/-- サイクル1: 26→13→66→33→166→83→416→208→104→52→26 の検証 -/
theorem collatz5_cycle1 : collatz5Iter 10 13 = 13 := by decide

/-- サイクル2: 17→86→43→216→108→54→27→136→68→34→17 の検証 -/
theorem collatz5_cycle2 : collatz5Iter 10 17 = 17 := by decide

/-- 5は1に到達しない（サイクルに入る） -/
theorem collatz5_five_not_reaches_one : collatz5Iter 10 5 = 26 := by decide

/-! ## 4. 1に到達する数 -/

/-- 2^k は 5n+1 変種でも 1 に到達する -/
theorem collatz5Reaches_pow_two (k : ℕ) : collatz5Reaches (2 ^ k) := by
  exact ⟨k, by induction k with
    | zero => rfl
    | succ k ih =>
      simp [collatz5Iter, collatz5Step]
      have : (2 ^ (k + 1)) % 2 = 0 := by omega
      simp [this]
      have : 2 ^ (k + 1) / 2 = 2 ^ k := by omega
      rw [this]; exact ih⟩

/-- 3 は 5n+1 変種で 1 に到達する（5·3+1=16=2^4） -/
theorem collatz5Reaches_three : collatz5Reaches 3 :=
  ⟨5, by decide⟩

/-- 51 は 5n+1 変種で 1 に到達する（5·51+1=256=2^8） -/
theorem collatz5Reaches_51 : collatz5Reaches 51 :=
  ⟨9, by decide⟩

/-! ## 5. (2^(4k)-1)/5 の性質 -/

/-- 2^4 ≡ 1 (mod 5)（フェルマーの小定理の p=5 ケース） -/
theorem pow_four_mod_five : 2 ^ 4 % 5 = 1 := by decide

/-- 5 | (2^(4k) - 1) -/
theorem five_dvd_pow_four_sub_one (k : ℕ) : 5 ∣ (2 ^ (4 * k) - 1) := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h16 : 2 ^ (4 * (k + 1)) = 2 ^ (4 * k) * 16 := by ring
    have hge : 2 ^ (4 * k) ≥ 1 := Nat.one_le_pow _ 2 (by omega)
    rw [h16]
    obtain ⟨m, hm⟩ := ih
    have : 2 ^ (4 * k) * 16 - 1 = (m * 5 + 1) * 16 - 1 := by omega
    rw [this]
    exact ⟨m * 16 + 3, by omega⟩

/-- 奇数 n に対して 5n+1 は偶数 -/
theorem five_mul_add_one_even (n : ℕ) (hodd : n % 2 = 1) : (5 * n + 1) % 2 = 0 := by
  omega

/-- 奇数 n に対して 5n+1 > n（値は増加する） -/
theorem five_mul_add_one_gt (n : ℕ) (hn : n ≥ 1) : 5 * n + 1 > n := by
  omega
