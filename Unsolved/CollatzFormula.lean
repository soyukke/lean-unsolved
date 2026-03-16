import Unsolved.CollatzHensel

/-!
# コラッツ予想 探索16: 連続上昇中の Syracuse 反復の一般公式

連続上昇中（各ステップで v2(3n+1) = 1）のとき、Syracuse 反復の
乗法形式の一般公式を帰納法で証明する。

## 主要結果

### 公式定数
- `ascentConst k`: 連続上昇公式の定数項
  - ascentConst 0 = 0
  - ascentConst 1 = 1
  - ascentConst 2 = 5
  - ascentConst 3 = 19
  - ascentConst 4 = 65
  - 閉じた形: ascentConst k + 2^k = 3^k

### 漸化式
- `ascentConst_succ`: ascentConst (k+1) = 3 * ascentConst k + 2^k

### 一般公式（乗法形式、除算を回避）
- `syracuse_iter_mul_formula`:
    consecutiveAscents n k のとき
    2^k * syracuseIter k n = 3^k * n + ascentConst k

### 帰納ステップ補題
- `consecutiveAscents_shift`:
    consecutiveAscents n (k+1) → consecutiveAscents (syracuse n) k
-/

/-! ## 1. 公式定数 ascentConst の定義 -/

/-- 連続上昇公式の定数: 漸化式 c_0 = 0, c_{k+1} = 3*c_k + 2^k -/
def ascentConst : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * ascentConst k + 2 ^ k

-- 数値検証
example : ascentConst 0 = 0 := rfl
example : ascentConst 1 = 1 := rfl
example : ascentConst 2 = 5 := rfl
example : ascentConst 3 = 19 := rfl
example : ascentConst 4 = 65 := rfl

/-! ## 2. ascentConst の閉じた形: ascentConst k + 2^k = 3^k -/

/-- ascentConst k + 2^k = 3^k
    自然数の引き算を避けた加法的表現 -/
theorem ascentConst_add_two_pow (k : ℕ) : ascentConst k + 2 ^ k = 3 ^ k := by
  induction k with
  | zero => simp [ascentConst]
  | succ n ih =>
    simp only [ascentConst, pow_succ]
    -- 目標: 3 * ascentConst n + 2^n + 2 * 2^n = 3 * 3^n
    -- ih: ascentConst n + 2^n = 3^n
    -- 3 * ascentConst n + 2^n + 2 * 2^n
    -- = 3 * ascentConst n + 3 * 2^n
    -- = 3 * (ascentConst n + 2^n)
    -- = 3 * 3^n
    linarith

/-- 3^k ≥ 2^k (ascentConst_add_two_pow の系) -/
theorem three_pow_ge_two_pow (k : ℕ) : 3 ^ k ≥ 2 ^ k := by
  have := ascentConst_add_two_pow k; omega

/-- ascentConst k = 3^k - 2^k (自然数の引き算) -/
theorem ascentConst_closed (k : ℕ) : ascentConst k = 3 ^ k - 2 ^ k := by
  have := ascentConst_add_two_pow k; omega

/-- ascentConst の漸化式（再帰定義から直接従う） -/
theorem ascentConst_succ (k : ℕ) : ascentConst (k + 1) = 3 * ascentConst k + 2 ^ k := rfl

/-! ## 3. ascentConst に関する補助補題 -/

/-- 3^k + 2 * ascentConst k = ascentConst (k+1)
    帰納ステップの核心的等式 -/
theorem three_pow_add_two_ascentConst_eq (k : ℕ) :
    3 ^ k + 2 * ascentConst k = ascentConst (k + 1) := by
  simp only [ascentConst]
  have := ascentConst_add_two_pow k
  linarith

/-! ## 4. consecutiveAscents のシフト補題 -/

/-- consecutiveAscents n (k+1) から最初のステップが上昇であることを取り出す -/
theorem consecutiveAscents_head (n : ℕ) (k : ℕ)
    (h : consecutiveAscents n (k + 1)) : syracuse n > n := by
  have := h 0 (by omega)
  simp only [syracuseIter_zero] at this
  exact this

/-- consecutiveAscents n (k+1) ならば syracuse n 以降も k 回連続上昇 -/
theorem consecutiveAscents_shift (n : ℕ) (k : ℕ)
    (h : consecutiveAscents n (k + 1)) : consecutiveAscents (syracuse n) k := by
  intro i hi
  have := h (i + 1) (by omega)
  simp only [syracuseIter_succ] at this
  exact this

/-! ## 5. 連続上昇中の mod 4 条件 -/

/-- consecutiveAscents n (k+1) かつ n が奇数で n ≥ 1 ならば n ≡ 3 (mod 4) -/
theorem mod4_eq3_of_consecutiveAscents (n : ℕ) (k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (h : consecutiveAscents n (k + 1)) : n % 4 = 3 := by
  have hasc := consecutiveAscents_head n k h
  exact (syracuse_ascent_iff_mod4_eq3 n hn hodd).mp hasc

/-- consecutiveAscents n 1 以上ならば n % 4 = 3 かつ syracuse n = (3n+1)/2 -/
theorem syracuse_eq_of_ascent (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (k : ℕ) (h : consecutiveAscents n (k + 1)) :
    syracuse n = (3 * n + 1) / 2 := by
  have hmod4 := mod4_eq3_of_consecutiveAscents n k hn hodd h
  exact syracuse_mod4_eq3 n hmod4

/-! ## 6. syracuse n の奇数性と正値性の伝播 -/

/-- n % 4 = 3 ならば syracuse n は奇数 -/
theorem syracuse_odd_of_ascent (n : ℕ) (h : n % 4 = 3) :
    syracuse n % 2 = 1 :=
  syracuse_odd_of_mod4_eq3 n h

/-- n % 4 = 3 ならば syracuse n ≥ 1 -/
theorem syracuse_pos_of_ascent (n : ℕ) (h : n % 4 = 3) :
    syracuse n ≥ 1 :=
  syracuse_pos_of_mod4_eq3 n h

/-! ## 7. 乗法形式の一般公式 -/

/-- syracuse n = (3*n+1)/2 のとき、2 * syracuse n = 3*n + 1 -/
theorem two_mul_syracuse_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    2 * syracuse n = 3 * n + 1 := by
  rw [syracuse_mod4_eq3 n h]
  omega

/-- 連続上昇中の Syracuse 反復の乗法形式一般公式:
    2^k * syracuseIter k n = 3^k * n + ascentConst k

    前提:
    - n は奇数
    - n ≥ 1
    - consecutiveAscents n k が成立（k 回連続上昇）

    この公式は除算を使わない乗法形式なので、
    自然数の除算の問題を完全に回避できる。 -/
theorem syracuse_iter_mul_formula (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    2 ^ k * syracuseIter k n = 3 ^ k * n + ascentConst k := by
  induction k generalizing n with
  | zero =>
    simp [ascentConst, syracuseIter]
  | succ k ih =>
    -- syracuseIter (k+1) n = syracuseIter k (syracuse n)
    simp only [syracuseIter_succ]
    -- consecutiveAscents n (k+1) より n % 4 = 3
    have hmod4 := mod4_eq3_of_consecutiveAscents n k hn hodd hasc
    -- syracuse n に対する性質
    have hsyr_odd := syracuse_odd_of_ascent n hmod4
    have hsyr_pos := syracuse_pos_of_ascent n hmod4
    -- consecutiveAscents のシフト: syracuse n に対して k 回連続上昇
    have hasc_shift := consecutiveAscents_shift n k hasc
    -- 帰納法の仮定を syracuse n に適用
    have ih_syr := ih (syracuse n) hsyr_pos hsyr_odd hasc_shift
    -- ih_syr: 2^k * syracuseIter k (syracuse n) = 3^k * syracuse n + ascentConst k
    -- 目標: 2^{k+1} * syracuseIter k (syracuse n) = 3^{k+1} * n + ascentConst (k+1)
    have h2syr := two_mul_syracuse_of_mod4_eq3 n hmod4
    have key := three_pow_add_two_ascentConst_eq k
    calc 2 ^ (k + 1) * syracuseIter k (syracuse n)
        = 2 * 2 ^ k * syracuseIter k (syracuse n) := by ring
      _ = 2 * (2 ^ k * syracuseIter k (syracuse n)) := by ring
      _ = 2 * (3 ^ k * syracuse n + ascentConst k) := by rw [ih_syr]
      _ = 2 * 3 ^ k * syracuse n + 2 * ascentConst k := by ring
      _ = 3 ^ k * (2 * syracuse n) + 2 * ascentConst k := by ring
      _ = 3 ^ k * (3 * n + 1) + 2 * ascentConst k := by rw [h2syr]
      _ = 3 ^ (k + 1) * n + (3 ^ k + 2 * ascentConst k) := by ring
      _ = 3 ^ (k + 1) * n + ascentConst (k + 1) := by rw [key]

/-! ## 8. 除算形式の公式（系） -/

/-- 除算形式: syracuseIter k n = (3^k * n + ascentConst k) / 2^k -/
theorem syracuse_iter_div_formula (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    syracuseIter k n = (3 ^ k * n + ascentConst k) / 2 ^ k := by
  have hmul := syracuse_iter_mul_formula n k hn hodd hasc
  have hpow_pos : 2 ^ k > 0 := Nat.pos_of_ne_zero (by positivity)
  have hmul' : 3 ^ k * n + ascentConst k = syracuseIter k n * 2 ^ k := by linarith
  exact (Nat.div_eq_of_eq_mul_left hpow_pos hmul').symm

/-- 公式の別形: 2^k * syracuseIter k n + 2^k = 3^k * (n + 1)
    自然数の引き算を回避した加法的表現 -/
theorem syracuse_iter_alt_formula (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    2 ^ k * syracuseIter k n + 2 ^ k = 3 ^ k * (n + 1) := by
  have hmul := syracuse_iter_mul_formula n k hn hodd hasc
  have hadd := ascentConst_add_two_pow k
  -- hmul: 2^k * iter = 3^k * n + ascentConst k
  -- hadd: ascentConst k + 2^k = 3^k
  -- 目標: 2^k * iter + 2^k = 3^k * (n + 1) = 3^k * n + 3^k
  have : 3 ^ k * (n + 1) = 3 ^ k * n + 3 ^ k := by ring
  linarith

/-! ## 9. 数値検証 -/

-- k=1, n=3: 2^1 * T(3) = 2*5 = 10, 3^1 * 3 + 1 = 10 ✓
example : 2 ^ 1 * syracuseIter 1 3 = 3 ^ 1 * 3 + ascentConst 1 := by
  have : consecutiveAscents 3 1 := by
    rw [single_ascent_mod4 3 (by omega) (by omega)]
  exact syracuse_iter_mul_formula 3 1 (by omega) (by omega) this

-- k=2, n=7: 2^2 * T²(7) = 4*17 = 68, 3^2 * 7 + 5 = 63+5 = 68 ✓
example : 2 ^ 2 * syracuseIter 2 7 = 3 ^ 2 * 7 + ascentConst 2 := by
  have : consecutiveAscents 7 2 := by
    rw [double_ascent_mod8 7 (by omega) (by omega)]
  exact syracuse_iter_mul_formula 7 2 (by omega) (by omega) this

-- k=3, n=15: 2^3 * T³(15) = 8*53 = 424, 3^3 * 15 + 19 = 405+19 = 424 ✓
example : 2 ^ 3 * syracuseIter 3 15 = 3 ^ 3 * 15 + ascentConst 3 := by
  have : consecutiveAscents 15 3 := by
    rw [triple_ascent_iff_mod16_eq15 15 (by omega) (by omega)]
  exact syracuse_iter_mul_formula 15 3 (by omega) (by omega) this

-- k=4, n=31: 2^4 * T⁴(31) = 16*161 = 2576, 3^4 * 31 + 65 = 2511+65 = 2576 ✓
example : 2 ^ 4 * syracuseIter 4 31 = 3 ^ 4 * 31 + ascentConst 4 := by
  have : consecutiveAscents 31 4 := by
    rw [quadruple_ascent_iff_mod32_eq31 31 (by omega) (by omega)]
  exact syracuse_iter_mul_formula 31 4 (by omega) (by omega) this

/-! ## 10. 公式からの系: 連続上昇中の成長率 -/

/-- 連続上昇中の値は常に増加: syracuseIter k n ≥ n -/
theorem syracuseIter_ge_of_ascents (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    syracuseIter k n ≥ n := by
  induction k generalizing n with
  | zero => simp [syracuseIter]
  | succ k ih =>
    simp only [syracuseIter_succ]
    have hmod4 := mod4_eq3_of_consecutiveAscents n k hn hodd hasc
    have hsyr_gt := syracuse_gt_of_mod4_eq3 n hmod4
    have hsyr_pos := syracuse_pos_of_ascent n hmod4
    have hsyr_odd := syracuse_odd_of_ascent n hmod4
    have hasc_shift := consecutiveAscents_shift n k hasc
    have := ih (syracuse n) hsyr_pos hsyr_odd hasc_shift
    omega

/-- 公式から導かれる上界: 2^k * syracuseIter k n ≤ 3^k * (n + 1) -/
theorem syracuseIter_upper_bound (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    2 ^ k * syracuseIter k n ≤ 3 ^ k * (n + 1) := by
  have h := syracuse_iter_alt_formula n k hn hodd hasc
  -- h: 2^k * iter + 2^k = 3^k * (n + 1)
  calc 2 ^ k * syracuseIter k n
      ≤ 2 ^ k * syracuseIter k n + 2 ^ k := Nat.le_add_right _ _
    _ = 3 ^ k * (n + 1) := h

/-! ## 11. 連続上昇中の syracuseIter の奇数性と正値性 -/

/-- 連続上昇中の各ステップの値は奇数 -/
theorem syracuseIter_odd_of_ascents (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    syracuseIter k n % 2 = 1 := by
  induction k generalizing n with
  | zero => simp only [syracuseIter_zero]; exact hodd
  | succ k ih =>
    simp only [syracuseIter_succ]
    have hmod4 := mod4_eq3_of_consecutiveAscents n k hn hodd hasc
    have hsyr_odd := syracuse_odd_of_ascent n hmod4
    have hsyr_pos := syracuse_pos_of_ascent n hmod4
    have hasc_shift := consecutiveAscents_shift n k hasc
    exact ih (syracuse n) hsyr_pos hsyr_odd hasc_shift

/-- 連続上昇中の各ステップの値は正 -/
theorem syracuseIter_pos_of_ascents (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    syracuseIter k n ≥ 1 := by
  induction k generalizing n with
  | zero => simp only [syracuseIter_zero, ge_iff_le]; exact hn
  | succ k ih =>
    simp only [syracuseIter_succ]
    have hmod4 := mod4_eq3_of_consecutiveAscents n k hn hodd hasc
    have hsyr_pos := syracuse_pos_of_ascent n hmod4
    have hsyr_odd := syracuse_odd_of_ascent n hmod4
    have hasc_shift := consecutiveAscents_shift n k hasc
    exact ih (syracuse n) hsyr_pos hsyr_odd hasc_shift

/-- 連続上昇中の各ステップの値は mod 4 ≡ 3 -/
theorem syracuseIter_mod4_eq3_of_ascents (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n (k + 1)) :
    syracuseIter k n % 4 = 3 := by
  induction k generalizing n with
  | zero =>
    simp only [syracuseIter_zero]
    exact mod4_eq3_of_consecutiveAscents n 0 hn hodd hasc
  | succ k ih =>
    simp only [syracuseIter_succ]
    have hmod4 := mod4_eq3_of_consecutiveAscents n (k + 1) hn hodd
      (consecutiveAscents_mono n (by omega) hasc)
    have hsyr_pos := syracuse_pos_of_ascent n hmod4
    have hsyr_odd := syracuse_odd_of_ascent n hmod4
    -- consecutiveAscents n (k+2) → consecutiveAscents (syracuse n) (k+1)
    have hasc_shift := consecutiveAscents_shift n (k + 1) hasc
    exact ih (syracuse n) hsyr_pos hsyr_odd hasc_shift

/-! ## 12. 上昇終了後の mod 4 ≡ 1 -/

/-- 上昇終了後の値は mod 4 ≡ 1:
    consecutiveAscents n k が成立し、k+1 回目は上昇しないとき、
    syracuseIter k n % 4 = 1 -/
theorem ascent_end_mod4 (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k)
    (hstop : ¬ consecutiveAscents n (k + 1)) :
    syracuseIter k n % 4 = 1 := by
  -- syracuseIter k n は奇数
  have hiter_odd := syracuseIter_odd_of_ascents n k hn hodd hasc
  have hiter_pos := syracuseIter_pos_of_ascents n k hn hodd hasc
  -- ¬ consecutiveAscents n (k+1) は k番目のステップで上昇しないことを意味する
  -- consecutiveAscents n (k+1) ↔ ∀ i < k+1, syracuse (syracuseIter i n) > syracuseIter i n
  -- 否定: ∃ i < k+1, ¬(syracuse (syracuseIter i n) > syracuseIter i n)
  -- hasc より i < k のケースはすべて成立するので、i = k が成立しない
  have hno_ascent : ¬ (syracuse (syracuseIter k n) > syracuseIter k n) := by
    intro h_asc_k
    apply hstop
    intro i hi
    by_cases hik : i < k
    · exact hasc i hik
    · have : i = k := by omega
      subst this
      exact h_asc_k
  -- 奇数で上昇しない → mod 4 ≡ 1
  have hne3 : ¬ (syracuseIter k n % 4 = 3) := by
    intro h3
    exact hno_ascent (syracuse_gt_of_mod4_eq3 (syracuseIter k n) h3)
  -- 奇数で mod 4 ≠ 3 → mod 4 = 1
  omega

/-! ## 13. 下降値の公式 -/

/-- 3 * ascentConst k + 2^k の値の補題:
    3 * ascentConst k + 2^k + 2^{k+1} = 3^{k+1} -/
theorem three_ascentConst_add_pow (k : ℕ) :
    3 * ascentConst k + 2 ^ k + 2 ^ (k + 1) = 3 ^ (k + 1) := by
  have h := ascentConst_add_two_pow k
  -- h: ascentConst k + 2^k = 3^k
  -- 目標: 3 * ascentConst k + 2^k + 2^{k+1} = 3^{k+1}
  -- = 3 * ascentConst k + 2^k + 2 * 2^k
  -- = 3 * ascentConst k + 3 * 2^k
  -- = 3 * (ascentConst k + 2^k)
  -- = 3 * 3^k = 3^{k+1}
  have h2 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
  have h3 : 3 ^ (k + 1) = 3 * 3 ^ k := by ring
  nlinarith

/-- 下降値の公式（加法形式、自然数の引き算を回避）:
    consecutiveAscents n k のとき
    2^k * (3 * syracuseIter k n + 1) + 2^{k+1} = 3^{k+1} * (n + 1)

    これは一般公式 2^k * T^k(n) = 3^k * n + ascentConst k から導かれる。
    展開: 2^k * (3 * T^k(n) + 1) = 3 * 2^k * T^k(n) + 2^k
         = 3 * (3^k * n + ascentConst k) + 2^k
         = 3^{k+1} * n + 3 * ascentConst k + 2^k
    よって 2^k * (3*T^k(n)+1) + 2^{k+1} = 3^{k+1}*n + 3*ascentConst k + 2^k + 2^{k+1}
         = 3^{k+1}*n + 3^{k+1} = 3^{k+1}*(n+1) -/
theorem descent_value_formula (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k) :
    2 ^ k * (3 * syracuseIter k n + 1) + 2 ^ (k + 1) = 3 ^ (k + 1) * (n + 1) := by
  have hmul := syracuse_iter_mul_formula n k hn hodd hasc
  have hkey := three_ascentConst_add_pow k
  -- hmul: 2^k * syracuseIter k n = 3^k * n + ascentConst k
  -- 目標: 2^k * (3 * syracuseIter k n + 1) + 2^{k+1} = 3^{k+1} * (n + 1)
  -- 左辺 = 3 * 2^k * syracuseIter k n + 2^k + 2^{k+1}
  --       = 3 * (3^k * n + ascentConst k) + 2^k + 2^{k+1}
  --       = 3^{k+1} * n + 3 * ascentConst k + 2^k + 2^{k+1}
  --       = 3^{k+1} * n + 3^{k+1}
  --       = 3^{k+1} * (n + 1)
  -- 2^k * (3 * iter + 1) = 3 * (2^k * iter) + 2^k
  --   = 3 * (3^k * n + ascentConst k) + 2^k
  --   = 3^{k+1} * n + 3 * ascentConst k + 2^k
  -- + 2^{k+1} → 3^{k+1} * n + (3 * ascentConst k + 2^k + 2^{k+1})
  --           = 3^{k+1} * n + 3^{k+1} = 3^{k+1} * (n + 1)
  have h3pow : 3 ^ (k + 1) = 3 * 3 ^ k := by ring
  have h_expand : 2 ^ k * (3 * syracuseIter k n + 1) =
      3 * (2 ^ k * syracuseIter k n) + 2 ^ k := by ring
  rw [h_expand, hmul]
  -- 目標: 3 * (3^k * n + ascentConst k) + 2^k + 2^{k+1} = 3^{k+1} * (n + 1)
  nlinarith [hkey]

/-! ## 14. 完全サイクルの上界: k回上昇 + 1回下降 -/

/-- 完全サイクルの上界（乗法形式）:
    consecutiveAscents n k かつ syracuseIter k n % 4 = 1 のとき
    4 * 2^k * syracuseIter (k+1) n + 2^{k+1} ≤ 3^{k+1} * (n + 1)

    証明: 下降ステップで v2 ≥ 2 より syracuseIter (k+1) n ≤ (3*T^k(n)+1)/4
    つまり 4 * syracuseIter (k+1) n ≤ 3*T^k(n)+1
    2^k を掛けて: 4 * 2^k * syracuseIter (k+1) n ≤ 2^k * (3*T^k(n)+1)
    descent_value_formula より: 2^k * (3*T^k(n)+1) = 3^{k+1}*(n+1) - 2^{k+1}
    よって: 4 * 2^k * T^{k+1}(n) + 2^{k+1} ≤ 3^{k+1}*(n+1) -/
theorem full_cycle_bound (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hasc : consecutiveAscents n k)
    (hmod4 : syracuseIter k n % 4 = 1)
    (hgt1 : syracuseIter k n > 1) :
    4 * 2 ^ k * syracuseIter (k + 1) n + 2 ^ (k + 1) ≤ 3 ^ (k + 1) * (n + 1) := by
  -- syracuseIter (k+1) n = syracuseIter k (syracuse n) なので
  -- syracuseIter (k+1) n = syracuse (syracuseIter k n)... いいえ
  -- syracuseIter (k+1) n は n に (k+1) 回 syracuse を適用
  -- = syracuseIter k (syracuse n)
  -- ただし syracuseIter k n に syracuse を適用したものを直接使いたい
  -- syracuseIter_succ_right のような補題が必要
  -- 実は syracuseIter (k+1) n = syracuseIter k (syracuse n)
  -- しかし syracuseIter k (syracuse n) ≠ syracuse (syracuseIter k n) 一般に
  -- これは Syracuse を「左」に展開するか「右」に展開するかの違い
  -- 定義上 syracuseIter (k+1) n = syracuseIter k (syracuse n)
  -- でも我々は「k回上昇した後の値 syracuseIter k n に syracuse を適用した値」が欲しい

  -- syracuseIter の右展開: syracuseIter (k+1) n = syracuse (syracuseIter k n)
  -- これは帰納法で示す
  suffices h_syr : syracuseIter (k + 1) n = syracuse (syracuseIter k n) by
    -- v2 ≥ 2 from hmod4
    have hv2 := v2_ge_two_of_mod4_eq1 (syracuseIter k n) hmod4
    have hle := syracuse_le_of_mod4_eq1 (syracuseIter k n) hmod4 hgt1
    -- hle: syracuse (syracuseIter k n) ≤ (3 * syracuseIter k n + 1) / 4
    rw [← h_syr] at hle
    -- hle: syracuseIter (k+1) n ≤ (3 * syracuseIter k n + 1) / 4
    -- 4 * syracuseIter (k+1) n ≤ 3 * syracuseIter k n + 1
    have h4le : 4 * syracuseIter (k + 1) n ≤ 3 * syracuseIter k n + 1 := by
      have := Nat.mul_div_le (3 * syracuseIter k n + 1) 4
      omega
    -- 2^k を掛ける
    have h_scaled : 4 * 2 ^ k * syracuseIter (k + 1) n ≤
        2 ^ k * (3 * syracuseIter k n + 1) := by
      nlinarith [Nat.pos_of_ne_zero (show 2 ^ k ≠ 0 by positivity)]
    -- descent_value_formula
    have h_dvf := descent_value_formula n k hn hodd hasc
    -- h_dvf: 2^k * (3 * syracuseIter k n + 1) + 2^{k+1} = 3^{k+1} * (n + 1)
    linarith
  -- syracuse (syracuseIter k n) = syracuseIter (k+1) n の証明
  -- これは syracuseIter_succ_right: 帰納法
  exact (syracuseIter_succ_right n k).symm
where
  /-- syracuseIter の右展開: syracuseIter (k+1) n = syracuse (syracuseIter k n) -/
  syracuseIter_succ_right (n k : ℕ) : syracuse (syracuseIter k n) = syracuseIter (k + 1) n := by
    induction k generalizing n with
    | zero => rfl
    | succ k ih =>
      simp only [syracuseIter_succ]
      exact ih (syracuse n)

/-! ## 15. k=0 の下降（再エクスポート） -/

/-- k=0 の場合: n % 4 = 1 かつ n > 1 → syracuse n < n -/
theorem full_cycle_descent_k0 (n : ℕ) (h : n % 4 = 1) (hn : n > 1) :
    syracuse n < n :=
  syracuse_lt_of_mod4_eq1 n h hn

/-! ## 16. 数値検証 -/

-- descent_value_formula の検算
-- k=1, n=3: T(3)=5, 2^1*(3*5+1) + 2^2 = 2*16 + 4 = 36, 3^2 * 4 = 36 ✓
example : 2 ^ 1 * (3 * syracuseIter 1 3 + 1) + 2 ^ 2 = 3 ^ 2 * (3 + 1) := by
  have hasc : consecutiveAscents 3 1 := by
    rw [single_ascent_mod4 3 (by omega) (by omega)]
  exact descent_value_formula 3 1 (by omega) (by omega) hasc

-- k=1, n=11: T(11)=17, 2^1*(3*17+1) + 2^2 = 2*52 + 4 = 108, 3^2*12 = 108 ✓
example : 2 ^ 1 * (3 * syracuseIter 1 11 + 1) + 2 ^ 2 = 3 ^ 2 * (11 + 1) := by
  have hasc : consecutiveAscents 11 1 := by
    rw [single_ascent_mod4 11 (by omega) (by omega)]
  exact descent_value_formula 11 1 (by omega) (by omega) hasc

-- k=2, n=7: T²(7)=17, 2^2*(3*17+1) + 2^3 = 4*52 + 8 = 216, 3^3*8 = 216 ✓
example : 2 ^ 2 * (3 * syracuseIter 2 7 + 1) + 2 ^ 3 = 3 ^ 3 * (7 + 1) := by
  have hasc : consecutiveAscents 7 2 := by
    rw [double_ascent_mod8 7 (by omega) (by omega)]
  exact descent_value_formula 7 2 (by omega) (by omega) hasc

-- full_cycle_bound の検算
-- k=1, n=11: T²(11)=13, 4*2^1*13 + 2^2 = 108, 3^2*12 = 108 ≤ 108 ✓
example : 4 * 2 ^ 1 * syracuseIter 2 11 + 2 ^ 2 ≤ 3 ^ 2 * (11 + 1) := by
  have hasc : consecutiveAscents 11 1 := by
    rw [single_ascent_mod4 11 (by omega) (by omega)]
  have hmod4 : syracuseIter 1 11 % 4 = 1 :=
    syracuse_mod4_eq1_of_mod8_eq3 11 (by omega)
  have hgt1 : syracuseIter 1 11 > 1 :=
    syracuse_gt_one_of_mod8_eq3 11 (by omega)
  exact full_cycle_bound 11 1 (by omega) (by omega) hasc hmod4 hgt1

-- k=1, n=3: T²(3)=1, 4*2*1 + 4 = 12, 9*4 = 36. 12 ≤ 36 ✓
example : 4 * 2 ^ 1 * syracuseIter 2 3 + 2 ^ 2 ≤ 3 ^ 2 * (3 + 1) := by
  have hasc : consecutiveAscents 3 1 := by
    rw [single_ascent_mod4 3 (by omega) (by omega)]
  have hmod4 : syracuseIter 1 3 % 4 = 1 :=
    syracuse_mod4_eq1_of_mod8_eq3 3 (by omega)
  have hgt1 : syracuseIter 1 3 > 1 :=
    syracuse_gt_one_of_mod8_eq3 3 (by omega)
  exact full_cycle_bound 3 1 (by omega) (by omega) hasc hmod4 hgt1

-- ascent_end_mod4 の検算
-- n=3, k=1: T(3)=5, 5 % 4 = 1 ✓
example : syracuseIter 1 3 % 4 = 1 := by
  have hasc : consecutiveAscents 3 1 := by
    rw [single_ascent_mod4 3 (by omega) (by omega)]
  have hstop : ¬ consecutiveAscents 3 2 := by
    rw [double_ascent_mod8 3 (by omega) (by omega)]; omega
  exact ascent_end_mod4 3 1 (by omega) (by omega) hasc hstop
