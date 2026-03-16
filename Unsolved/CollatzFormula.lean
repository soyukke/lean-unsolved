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
