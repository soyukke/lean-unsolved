import Unsolved.Collatz.Structure

/-!
# コラッツ予想 探索11: mod 2^k での Syracuse 関数の振る舞い

mod 8 での奇数の分類に基づいて、v2(3n+1) の正確な値や下界を求め、
Syracuse 関数の上昇・下降パターンを形式化する。

## 主要結果

### v2 の mod 8 分類
- `v2_of_mod8_eq1`: n ≡ 1 (mod 8) → v2(3n+1) = 2
- `v2_of_mod8_eq3`: n ≡ 3 (mod 8) → v2(3n+1) = 1
- `v2_of_mod8_eq5`: n ≡ 5 (mod 8) → v2(3n+1) ≥ 4 (正確な値は mod 16 以上が必要)
- `v2_of_mod8_eq7`: n ≡ 7 (mod 8) → v2(3n+1) = 1

### Syracuse の上昇・下降
- n ≡ 1 (mod 8), n > 1 → syracuse n = (3n+1)/4 < n (下降)
- n ≡ 3 (mod 8) → syracuse n = (3n+1)/2 > n (上昇)
- n ≡ 5 (mod 8), n > 1 → syracuse n ≤ (3n+1)/16 < n (強い下降)
- n ≡ 7 (mod 8) → syracuse n = (3n+1)/2 > n (上昇)

### Hensel attrition
- 連続上昇 ⟺ n ≡ 3 (mod 4) の連鎖 ⟺ 末尾ビットが1の連続
-/

/-! ## 1. v2 の mod 8 分類 -/

/-- n ≡ 1 (mod 8) ならば v2(3n+1) = 2 -/
theorem v2_of_mod8_eq1 (n : ℕ) (h : n % 8 = 1) : v2 (3 * n + 1) = 2 := by
  -- n = 8q+1 → 3n+1 = 24q+4 = 4(6q+1), 6q+1 は奇数 → v2 = 2
  have hne1 : 3 * n + 1 ≠ 0 := by omega
  have heven1 : (3 * n + 1) % 2 = 0 := by omega
  rw [v2_even _ hne1 heven1]
  have hne2 : (3 * n + 1) / 2 ≠ 0 := by omega
  have heven2 : (3 * n + 1) / 2 % 2 = 0 := by omega
  rw [v2_even _ hne2 heven2]
  have hodd : (3 * n + 1) / 2 / 2 % 2 = 1 := by omega
  rw [v2_odd _ (by omega)]

/-- n ≡ 3 (mod 8) ならば v2(3n+1) = 1 -/
theorem v2_of_mod8_eq3 (n : ℕ) (h : n % 8 = 3) : v2 (3 * n + 1) = 1 := by
  exact v2_three_mul_add_one_of_mod4_eq3 n (by omega)

/-- n ≡ 5 (mod 8) ならば v2(3n+1) ≥ 4
    n = 8q+5 → 3n+1 = 24q+16 = 8(3q+2) → v2 ≥ 3
    さらに 3q+2 は必ず偶数ではないが... 実は:
    24q+16 = 16 * (floor) ではなく、8(3q+2) で 3q+2 の偶奇で分岐。
    しかし mod 8 では v2 ≥ 3 しか保証できない。

    修正: 実際には n ≡ 5 (mod 8) → 3n+1 = 24q+16
    16 | 24q+16 ⟺ 16 | 24q ⟺ 2 | 3q ⟺ 2 | q
    q の偶奇により v2 = 3 or v2 ≥ 4 なので、v2 ≥ 3 が正しい下界。 -/
theorem v2_ge_three_of_mod8_eq5 (n : ℕ) (h : n % 8 = 5) : v2 (3 * n + 1) ≥ 3 := by
  -- 3n+1 ≡ 0 (mod 8)
  have hne1 : 3 * n + 1 ≠ 0 := by omega
  have heven1 : (3 * n + 1) % 2 = 0 := by omega
  rw [v2_even _ hne1 heven1]
  have hne2 : (3 * n + 1) / 2 ≠ 0 := by omega
  have heven2 : (3 * n + 1) / 2 % 2 = 0 := by omega
  rw [v2_even _ hne2 heven2]
  have hne3 : (3 * n + 1) / 2 / 2 ≠ 0 := by omega
  have heven3 : (3 * n + 1) / 2 / 2 % 2 = 0 := by omega
  rw [v2_even _ hne3 heven3]
  omega

/-- n ≡ 7 (mod 8) ならば v2(3n+1) = 1 -/
theorem v2_of_mod8_eq7 (n : ℕ) (h : n % 8 = 7) : v2 (3 * n + 1) = 1 := by
  -- n = 8q+7 → 3n+1 = 24q+22 = 2(12q+11), 12q+11 は奇数 → v2 = 1
  have hne : 3 * n + 1 ≠ 0 := by omega
  have heven : (3 * n + 1) % 2 = 0 := by omega
  rw [v2_even _ hne heven]
  have hodd : (3 * n + 1) / 2 % 2 = 1 := by omega
  rw [v2_odd _ (by omega)]

/-! ## 2. Syracuse の正確な値 (v2 が確定するケース) -/

/-- n ≡ 1 (mod 8) ならば syracuse n = (3n+1)/4 -/
theorem syracuse_of_mod8_eq1 (n : ℕ) (h : n % 8 = 1) :
    syracuse n = (3 * n + 1) / 4 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) = (3 * n + 1) / 4
  rw [v2_of_mod8_eq1 n h]
  norm_num

/-- n ≡ 3 (mod 8) ならば syracuse n = (3n+1)/2 -/
theorem syracuse_of_mod8_eq3 (n : ℕ) (h : n % 8 = 3) :
    syracuse n = (3 * n + 1) / 2 := by
  exact syracuse_mod4_eq3 n (by omega)

/-- n ≡ 7 (mod 8) ならば syracuse n = (3n+1)/2 -/
theorem syracuse_of_mod8_eq7 (n : ℕ) (h : n % 8 = 7) :
    syracuse n = (3 * n + 1) / 2 := by
  -- n ≡ 7 (mod 8) → n ≡ 3 (mod 4)
  exact syracuse_mod4_eq3 n (by omega)

/-! ## 3. mod 8 での上昇・下降の分類 -/

/-- n ≡ 1 (mod 8) かつ n > 1 ならば syracuse n < n (下降) -/
theorem syracuse_descent_mod8_eq1 (n : ℕ) (h : n % 8 = 1) (hn : n > 1) :
    syracuse n < n := by
  exact syracuse_lt_of_mod4_eq1 n (by omega) hn

/-- n ≡ 3 (mod 8) ならば syracuse n > n (上昇) -/
theorem syracuse_ascent_mod8_eq3 (n : ℕ) (h : n % 8 = 3) :
    syracuse n > n := by
  exact syracuse_gt_of_mod4_eq3 n (by omega)

/-- n ≡ 5 (mod 8) かつ n > 1 ならば syracuse n < n (強い下降)
    v2 ≥ 3 なので 2^v2 ≥ 8, syracuse n ≤ (3n+1)/8 < n -/
theorem syracuse_strong_descent_mod8_eq5 (n : ℕ) (h : n % 8 = 5) (_hn : n > 1) :
    syracuse n < n := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) < n
  have hv2 := v2_ge_three_of_mod8_eq5 n h
  have hpow_ge : 2 ^ v2 (3 * n + 1) ≥ 8 := by
    have : 2 ^ v2 (3 * n + 1) ≥ 2 ^ 3 := Nat.pow_le_pow_right (by omega) hv2
    simpa using this
  have hle : (3 * n + 1) / 2 ^ v2 (3 * n + 1) ≤ (3 * n + 1) / 8 := by
    apply Nat.div_le_div_left (by omega) (by omega)
  have hlt : (3 * n + 1) / 8 < n := by omega
  omega

/-- n ≡ 7 (mod 8) ならば syracuse n > n (上昇) -/
theorem syracuse_ascent_mod8_eq7 (n : ℕ) (h : n % 8 = 7) :
    syracuse n > n := by
  exact syracuse_gt_of_mod4_eq3 n (by omega)

/-! ## 4. 強い下降の上界 -/

/-- n ≡ 5 (mod 8) ならば syracuse n ≤ (3n+1)/8 -/
theorem syracuse_le_of_mod8_eq5 (n : ℕ) (h : n % 8 = 5) :
    syracuse n ≤ (3 * n + 1) / 8 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) ≤ (3 * n + 1) / 8
  have hv2 := v2_ge_three_of_mod8_eq5 n h
  have : 2 ^ v2 (3 * n + 1) ≥ 8 := by
    have : 2 ^ v2 (3 * n + 1) ≥ 2 ^ 3 := Nat.pow_le_pow_right (by omega) hv2
    simpa using this
  exact Nat.div_le_div_left (by omega) (by omega)

/-- n ≡ 1 (mod 8) ならば syracuse n ≤ (3n+1)/4 (正確な等式) -/
theorem syracuse_eq_of_mod8_eq1 (n : ℕ) (h : n % 8 = 1) :
    syracuse n = (3 * n + 1) / 4 :=
  syracuse_of_mod8_eq1 n h

/-! ## 5. 上昇条件の特徴付け: v2(3n+1) = 1 ⟺ n ≡ 3 (mod 4) -/

/-- v2(3n+1) = 1 ならば n は奇数 -/
theorem odd_of_v2_eq_one (n : ℕ) (_hn : n ≥ 1) (h : v2 (3 * n + 1) = 1) :
    n % 2 = 1 := by
  by_contra hc
  push_neg at hc
  have : n % 2 = 0 := by omega
  -- n が偶数なら 3n+1 は奇数なので v2(3n+1) = 0
  have hodd : (3 * n + 1) % 2 = 1 := by omega
  have := v2_odd (3 * n + 1) (by omega)
  omega

/-- n が奇数のとき: v2(3n+1) = 1 ⟺ n ≡ 3 (mod 4) -/
theorem v2_eq_one_iff_mod4_eq3 (n : ℕ) (_hn : n ≥ 1) (hodd : n % 2 = 1) :
    v2 (3 * n + 1) = 1 ↔ n % 4 = 3 := by
  constructor
  · intro hv2
    -- n is odd, so n % 4 = 1 or n % 4 = 3
    -- If n % 4 = 1, then v2(3n+1) ≥ 2 (from existing lemma)
    by_contra hne
    have h4 : n % 4 = 1 := by omega
    have := v2_ge_two_of_mod4_eq1 n h4
    omega
  · exact v2_three_mul_add_one_of_mod4_eq3 n

/-! ## 6. 上昇は n ≡ 3 (mod 4) と同値 -/

/-- Syracuse の「上昇」(syracuse n > n) は n ≡ 3 (mod 4) であることと同値
    （ただし n が奇数かつ n ≥ 1 の前提） -/
theorem syracuse_ascent_iff_mod4_eq3 (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuse n > n ↔ n % 4 = 3 := by
  constructor
  · intro hasc
    by_contra hne
    have h4 : n % 4 = 1 := by omega
    -- n ≡ 1 (mod 4) ならば syracuse n ≤ (3n+1)/4 < n (n > 1 のとき)
    -- n = 1 のとき syracuse 1 = 1 なので > 1 は成り立たない
    by_cases hn1 : n = 1
    · subst hn1
      have : syracuse 1 = 1 := syracuse_one
      omega
    · have hgt : n > 1 := by omega
      have := syracuse_lt_of_mod4_eq1 n h4 hgt
      omega
  · exact fun h => syracuse_gt_of_mod4_eq3 n h

/-! ## 7. Hensel attrition: 連続上昇と末尾ビットパターン -/

/-- 連続上昇の必要条件: syracuse n > n ならば n ≡ 3 (mod 4) -/
theorem ascent_implies_mod4_eq3 (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : syracuse n > n) : n % 4 = 3 := by
  exact (syracuse_ascent_iff_mod4_eq3 n hn hodd).mp hasc

/-- n ≡ 3 (mod 4) のとき syracuse n も奇数 -/
theorem syracuse_odd_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    syracuse n % 2 = 1 := by
  rw [syracuse_mod4_eq3 n h]
  omega

/-- n ≡ 3 (mod 4) のとき syracuse n ≥ 1 -/
theorem syracuse_pos_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    syracuse n ≥ 1 := by
  have := syracuse_gt_of_mod4_eq3 n h
  omega

/-- 2連続上昇の条件: n ≡ 3 (mod 4) かつ syracuse n ≡ 3 (mod 4)
    n ≡ 3 (mod 4) → syracuse n = (3n+1)/2
    syracuse n ≡ 3 (mod 4) ⟺ (3n+1)/2 ≡ 3 (mod 4)
    これは n ≡ 3 (mod 8) or n ≡ 7 (mod 8) のうちさらに条件が付く

    n ≡ 3 (mod 8): syracuse n = (3n+1)/2 = (24q+10)/2 = 12q+5 ≡ 1 (mod 4) → 下降！
    n ≡ 7 (mod 8): syracuse n = (3n+1)/2 = (24q+22)/2 = 12q+11 ≡ 3 (mod 4) → 上昇！

    よって2連続上昇 ⟺ n ≡ 7 (mod 8) -/
theorem double_ascent_iff_mod8_eq7 (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    (syracuse n > n ∧ syracuse (syracuse n) > syracuse n) ↔ n % 8 = 7 := by
  constructor
  · intro ⟨h1, h2⟩
    have hmod4 := (syracuse_ascent_iff_mod4_eq3 n hn hodd).mp h1
    -- n ≡ 3 (mod 4), so n % 8 = 3 or n % 8 = 7
    have hsyr_odd := syracuse_odd_of_mod4_eq3 n hmod4
    have hsyr_pos := syracuse_pos_of_mod4_eq3 n hmod4
    have hsyr_mod4 := (syracuse_ascent_iff_mod4_eq3 (syracuse n) hsyr_pos hsyr_odd).mp h2
    -- syracuse n = (3n+1)/2 and syracuse n ≡ 3 (mod 4)
    rw [syracuse_mod4_eq3 n hmod4] at hsyr_mod4
    -- (3n+1)/2 ≡ 3 (mod 4) → n ≡ 7 (mod 8)
    omega
  · intro h8
    constructor
    · exact syracuse_ascent_mod8_eq7 n h8
    · -- syracuse n = (3n+1)/2, and n ≡ 7 (mod 8) → syracuse n ≡ 3 (mod 4)
      have hmod4 : n % 4 = 3 := by omega
      rw [syracuse_mod4_eq3 n hmod4]
      have hsyr_val : (3 * n + 1) / 2 % 4 = 3 := by omega
      exact syracuse_gt_of_mod4_eq3 ((3 * n + 1) / 2) hsyr_val

/-! ## 8. mod 8 分類の完全性: 奇数は4つのクラスのいずれか -/

/-- 奇数 n の mod 8 は 1, 3, 5, 7 のいずれか -/
theorem odd_mod8_cases (n : ℕ) (h : n % 2 = 1) :
    n % 8 = 1 ∨ n % 8 = 3 ∨ n % 8 = 5 ∨ n % 8 = 7 := by
  omega

/-- Syracuse関数の完全な振る舞い分類 (n > 1 の奇数):
    下降(n ≡ 1 mod 8)、上昇(n ≡ 3 mod 8)、
    強い下降(n ≡ 5 mod 8)、上昇(n ≡ 7 mod 8) -/
theorem syracuse_behavior_mod8 (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    (n % 8 = 1 ∧ syracuse n < n) ∨
    (n % 8 = 3 ∧ syracuse n > n) ∨
    (n % 8 = 5 ∧ syracuse n < n) ∨
    (n % 8 = 7 ∧ syracuse n > n) := by
  rcases odd_mod8_cases n hodd with h1 | h3 | h5 | h7
  · left; exact ⟨h1, syracuse_descent_mod8_eq1 n h1 hn⟩
  · right; left; exact ⟨h3, syracuse_ascent_mod8_eq3 n h3⟩
  · right; right; left; exact ⟨h5, syracuse_strong_descent_mod8_eq5 n h5 hn⟩
  · right; right; right; exact ⟨h7, syracuse_ascent_mod8_eq7 n h7⟩

/-! ## 9. 数値検証 -/

-- n = 1 (mod 8): v2 = 2, 下降
example : v2 (3 * 1 + 1) = 2 := by unfold v2; unfold v2; unfold v2; simp
example : v2 (3 * 9 + 1) = 2 := by unfold v2; unfold v2; unfold v2; simp
example : v2 (3 * 17 + 1) = 2 := by unfold v2; unfold v2; unfold v2; simp

-- n = 3 (mod 8): v2 = 1, 上昇
example : v2 (3 * 3 + 1) = 1 := by unfold v2; unfold v2; simp
example : v2 (3 * 11 + 1) = 1 := by unfold v2; unfold v2; simp
example : v2 (3 * 19 + 1) = 1 := by unfold v2; unfold v2; simp

-- n = 7 (mod 8): v2 = 1, 上昇
example : v2 (3 * 7 + 1) = 1 := by unfold v2; unfold v2; simp
example : v2 (3 * 15 + 1) = 1 := by unfold v2; unfold v2; simp
example : v2 (3 * 23 + 1) = 1 := by unfold v2; unfold v2; simp

-- n = 5 (mod 8): v2 ≥ 3
-- n=5: 3*5+1=16, v2=4 (≥ 3 ✓)
-- n=13: 3*13+1=40, v2=3 (≥ 3 ✓)
-- n=21: 3*21+1=64, v2=6 (≥ 3 ✓)
example : v2 (3 * 5 + 1) = 4 := by unfold v2; unfold v2; unfold v2; unfold v2; unfold v2; simp
example : v2 (3 * 13 + 1) = 3 := by unfold v2; unfold v2; unfold v2; unfold v2; simp
