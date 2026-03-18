import Unsolved.CollatzStructure

/-!
# コラッツ予想 探索43: mod 3 不変量

collatzStep の mod 3 に関する性質を証明する。

## 主要結果
- `three_mul_add_one_mod3`: 任意の n に対して (3n+1) % 3 = 1
- `collatzStep_odd_mod3_eq_one`: 奇数 n に対して collatzStep(n) % 3 = 1 ではなく、
  (3n+1) % 3 = 1 を示す（collatzStep は 3n+1 を返すため）
- `collatzStep_even_mod3`: 偶数 n に対する mod 3 の解析
- `syracuse_mod3`: Syracuse 値の mod 3 性質

## 数学的背景
奇数 n に対して:
- n % 3 = 1 のとき: 3n+1 ≡ 3·1+1 = 4 ≡ 1 (mod 3)
- n % 3 = 2 のとき: 3n+1 ≡ 3·2+1 = 7 ≡ 1 (mod 3)
- n % 3 = 0 のとき: 3n+1 ≡ 0+1 = 1 ≡ 1 (mod 3)
つまり、任意の n に対して常に (3n+1) % 3 = 1 が成立する。
-/

/-! ## 1. (3n+1) mod 3 の基本性質 -/

/-- 任意の自然数 n に対して (3n+1) % 3 = 1 -/
theorem three_mul_add_one_mod3 (n : ℕ) : (3 * n + 1) % 3 = 1 := by
  omega

/-- 任意の自然数 n に対して (3n+1) は 3 の倍数でない -/
theorem three_mul_add_one_not_mul3 (n : ℕ) : ¬ (3 ∣ (3 * n + 1)) := by
  intro ⟨k, hk⟩
  omega

/-! ## 2. 奇数ステップの mod 3 性質 -/

/-- 奇数 n に対して collatzStep n = 3n+1 であり、(3n+1) % 3 = 1 -/
theorem collatzStep_odd_result_mod3 (n : ℕ) (hodd : n % 2 = 1) :
    collatzStep n % 3 = 1 := by
  rw [collatzStep_odd_eq n hodd]
  exact three_mul_add_one_mod3 n

/-! ## 3. 偶数ステップの mod 3 性質 -/

-- 偶数 n で n % 3 = 1 のとき、n/2 の mod 3 は n の値に依存する
-- （一般的な保存則は成り立たないが、特定の場合を記述）

/-- n % 6 = 0 のとき collatzStep n % 3 = 0 -/
theorem collatzStep_even_mod6_eq0 (n : ℕ) (h : n % 6 = 0) :
    collatzStep n % 3 = 0 := by
  have heven : n % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 n heven]
  omega

/-- n % 6 = 2 のとき collatzStep n % 3 = 1 -/
theorem collatzStep_even_mod6_eq2 (n : ℕ) (h : n % 6 = 2) :
    collatzStep n % 3 = 1 := by
  have heven : n % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 n heven]
  omega

/-- n % 6 = 4 のとき collatzStep n % 3 = 2 -/
theorem collatzStep_even_mod6_eq4 (n : ℕ) (h : n % 6 = 4) :
    collatzStep n % 3 = 2 := by
  have heven : n % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 n heven]
  omega

/-! ## 4. Syracuse 関数の mod 3 性質（既存定理の拡張） -/

/-- 奇数 n かつ n % 3 = 1 のとき: 3n+1 ≡ 1 (mod 3) -/
theorem odd_mod3_eq1_step (n : ℕ) (_hodd : n % 2 = 1) (hmod : n % 3 = 1) :
    (3 * n + 1) % 3 = 1 := by
  omega

/-- 奇数 n かつ n % 3 = 2 のとき: 3n+1 ≡ 1 (mod 3) -/
theorem odd_mod3_eq2_step (n : ℕ) (_hodd : n % 2 = 1) (hmod : n % 3 = 2) :
    (3 * n + 1) % 3 = 1 := by
  omega

/-! ## 5. mod 3 軌道の閉じ込め -/

/-- コラッツ軌道において、3 の倍数でない値から出発すると、
    奇数ステップ後の値は常に mod 3 = 1 になる。
    これは three_mul_add_one_mod3 の直接的帰結。 -/
theorem collatz_odd_step_mod3_invariant (n : ℕ) (hodd : n % 2 = 1) (hmod : n % 3 ≠ 0) :
    collatzStep n % 3 = 1 := by
  rw [collatzStep_odd_eq n hodd]
  exact three_mul_add_one_mod3 n

/-! ## 6. 数値検証 -/

-- n = 1 (奇数, mod 3 = 1): collatzStep 1 = 4, 4 % 3 = 1 ✓
example : collatzStep 1 % 3 = 1 := by decide
-- n = 5 (奇数, mod 3 = 2): collatzStep 5 = 16, 16 % 3 = 1 ✓
example : collatzStep 5 % 3 = 1 := by decide
-- n = 7 (奇数, mod 3 = 1): collatzStep 7 = 22, 22 % 3 = 1 ✓
example : collatzStep 7 % 3 = 1 := by decide
-- n = 3 (奇数, mod 3 = 0): collatzStep 3 = 10, 10 % 3 = 1 ✓
example : collatzStep 3 % 3 = 1 := by decide
-- n = 11 (奇数, mod 3 = 2): collatzStep 11 = 34, 34 % 3 = 1 ✓
example : collatzStep 11 % 3 = 1 := by decide

/-! ## 7. v₂(3n+1) の基本性質 -/

/-- 奇数 n に対して 2 | (3n+1) -/
theorem two_dvd_three_mul_add_one (n : ℕ) (hodd : n % 2 = 1) : 2 ∣ (3 * n + 1) := by
  exact ⟨(3 * n + 1) / 2, by omega⟩

/-- n ≡ 1 (mod 4) のとき (3n+1) % 4 = 0 -/
theorem three_mul_add_one_mod4_of_mod4_eq1 (n : ℕ) (h : n % 4 = 1) :
    (3 * n + 1) % 4 = 0 := by omega

/-- n ≡ 3 (mod 4) のとき (3n+1) % 4 = 2 だが (3n+1) % 4 ≠ 0 -/
theorem three_mul_add_one_mod4_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    (3 * n + 1) % 4 = 2 := by omega

/-- n ≡ 3 (mod 4) → (3n+1)/2 は奇数 -/
theorem three_mul_add_one_div2_odd_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    ((3 * n + 1) / 2) % 2 = 1 := by omega

/-! ## 8. (3n+1) mod 8 の完全分類 -/

/-- n ≡ 1 (mod 8) → (3n+1) % 8 = 4 -/
theorem three_mul_add_one_mod8_1 (n : ℕ) (h : n % 8 = 1) : (3 * n + 1) % 8 = 4 := by omega

/-- n ≡ 3 (mod 8) → (3n+1) % 8 = 2 -/
theorem three_mul_add_one_mod8_3 (n : ℕ) (h : n % 8 = 3) : (3 * n + 1) % 8 = 2 := by omega

/-- n ≡ 5 (mod 8) → (3n+1) % 8 = 0 -/
theorem three_mul_add_one_mod8_5 (n : ℕ) (h : n % 8 = 5) : (3 * n + 1) % 8 = 0 := by omega

/-- n ≡ 7 (mod 8) → (3n+1) % 8 = 6 -/
theorem three_mul_add_one_mod8_7 (n : ℕ) (h : n % 8 = 7) : (3 * n + 1) % 8 = 6 := by omega

/-! ## 9. 2ステップ合成: 奇数 n の collatzStep(collatzStep(n)) -/

/-- 奇数 n に対して collatzStep(n) = 3n+1 は偶数なので、
    collatzStep(collatzStep(n)) = (3n+1)/2 -/
theorem collatzStep_step_odd (n : ℕ) (hn : n > 0) (hodd : n % 2 = 1) :
    collatzStep (collatzStep n) = (3 * n + 1) / 2 := by
  rw [collatzStep_odd_eq n hodd]
  have heven : (3 * n + 1) % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 (3 * n + 1) heven]

/-! ## 10. (3n+1) mod 16 の完全分類 -/

/-- n ≡ 1 (mod 16) → (3n+1) % 16 = 4 -/
theorem three_mul_add_one_mod16_1 (n : ℕ) (h : n % 16 = 1) : (3*n+1) % 16 = 4 := by omega

/-- n ≡ 3 (mod 16) → (3n+1) % 16 = 10 -/
theorem three_mul_add_one_mod16_3 (n : ℕ) (h : n % 16 = 3) : (3*n+1) % 16 = 10 := by omega

/-- n ≡ 5 (mod 16) → (3n+1) % 16 = 0 -/
theorem three_mul_add_one_mod16_5 (n : ℕ) (h : n % 16 = 5) : (3*n+1) % 16 = 0 := by omega

/-- n ≡ 7 (mod 16) → (3n+1) % 16 = 6 -/
theorem three_mul_add_one_mod16_7 (n : ℕ) (h : n % 16 = 7) : (3*n+1) % 16 = 6 := by omega

/-- n ≡ 9 (mod 16) → (3n+1) % 16 = 12 -/
theorem three_mul_add_one_mod16_9 (n : ℕ) (h : n % 16 = 9) : (3*n+1) % 16 = 12 := by omega

/-- n ≡ 11 (mod 16) → (3n+1) % 16 = 2 -/
theorem three_mul_add_one_mod16_11 (n : ℕ) (h : n % 16 = 11) : (3*n+1) % 16 = 2 := by omega

/-- n ≡ 13 (mod 16) → (3n+1) % 16 = 8 -/
theorem three_mul_add_one_mod16_13 (n : ℕ) (h : n % 16 = 13) : (3*n+1) % 16 = 8 := by omega

/-- n ≡ 15 (mod 16) → (3n+1) % 16 = 14 -/
theorem three_mul_add_one_mod16_15 (n : ℕ) (h : n % 16 = 15) : (3*n+1) % 16 = 14 := by omega

/-! ## 11. v₂(3n+1) の正確な値（一部） -/

/-- n ≡ 1 (mod 8) → (3n+1)/4 は奇数、すなわち v₂(3n+1) = 2 -/
theorem three_mul_add_one_div4_odd_of_mod8_eq1 (n : ℕ) (h : n % 8 = 1) :
    ((3 * n + 1) / 4) % 2 = 1 := by omega
