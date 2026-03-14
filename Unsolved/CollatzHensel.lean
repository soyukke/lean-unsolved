import Unsolved.CollatzMod

/-!
# コラッツ予想 探索13: Hensel Attrition（2-adic消耗）

Syracuse関数での「上昇」(syracuse n > n) が連続する条件を
mod 2^{k+1} の制約として形式化する。

## 核心的アイデア
- 1回上昇: n ≡ 3 (mod 4), 確率 1/2
- 2回連続上昇: n ≡ 7 (mod 8), 確率 1/4
- 3回連続上昇: n ≡ 15 (mod 16), 確率 1/8
- k回連続上昇: n ≡ 2^{k+1} - 1 (mod 2^{k+1}), 確率 1/2^k

連続上昇は末尾ビットが全て1であることを要求し、
上昇回数が増えるほど指数的に稀になる。
これが「Hensel attrition」（2-adic消耗）の基本メカニズムである。

## 主要結果
- `consecutiveAscents`: 連続上昇の形式的定義
- `single_ascent_mod4`: 1回上昇 ↔ n ≡ 3 (mod 4)
- `double_ascent_mod8`: 2回連続上昇 ↔ n ≡ 7 (mod 8)
- `triple_ascent_iff_mod16_eq15`: 3回連続上昇 ↔ n ≡ 15 (mod 16)
- `quadruple_ascent_iff_mod32_eq31`: 4回連続上昇 ↔ n ≡ 31 (mod 32)
- `hensel_attrition_k1` ~ `hensel_attrition_k4`: 統一的な表現
-/

/-! ## 1. 連続上昇の形式的定義 -/

/-- k 回連続上昇: Syracuse 反復の各ステップで値が増加する。
    syracuseIter を使い、第 i ステップの結果が第 (i+1) ステップで増加する -/
def consecutiveAscents (n : ℕ) (k : ℕ) : Prop :=
  ∀ i, i < k → syracuse (syracuseIter i n) > syracuseIter i n

/-! ## 2. 基本的な展開補題 -/

/-- consecutiveAscents の 0 ステップ目は syracuse n > n -/
theorem consecutiveAscents_zero_step (n : ℕ) (k : ℕ) (hk : k ≥ 1)
    (h : consecutiveAscents n k) : syracuse n > n := by
  have := h 0 (by omega)
  simp only [syracuseIter_zero] at this
  exact this

/-- consecutiveAscents の単調性: k 回連続上昇は k' ≤ k 回の連続上昇を含む -/
theorem consecutiveAscents_mono (n : ℕ) {k k' : ℕ} (hle : k' ≤ k)
    (h : consecutiveAscents n k) : consecutiveAscents n k' := by
  intro i hi
  exact h i (by omega)

/-! ## 3. n ≡ 7 (mod 8) のとき syracuse n の mod 4 / mod 8 -/

/-- n ≡ 7 (mod 8) → syracuse n ≡ 3 (mod 4)
    n = 8q+7 → syracuse n = (3n+1)/2 = 12q+11 ≡ 3 (mod 4) -/
theorem syracuse_mod4_eq3_of_mod8_eq7 (n : ℕ) (h : n % 8 = 7) :
    syracuse n % 4 = 3 := by
  rw [syracuse_mod4_eq3 n (by omega)]
  omega

/-- n ≡ 3 (mod 4) → (syracuse n ≡ 3 (mod 4) ↔ n ≡ 7 (mod 8)) -/
theorem syracuse_mod4_eq3_iff_mod8_eq7 (n : ℕ) (h4 : n % 4 = 3) :
    syracuse n % 4 = 3 ↔ n % 8 = 7 := by
  rw [syracuse_mod4_eq3 n h4]
  constructor <;> omega

/-! ## 4. 1回上昇の条件 -/

/-- 1回上昇 ↔ n ≡ 3 (mod 4)（n が奇数かつ n ≥ 1 の場合） -/
theorem single_ascent_mod4 (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 1 ↔ n % 4 = 3 := by
  unfold consecutiveAscents
  constructor
  · intro h
    have h0 := h 0 (by omega)
    simp only [syracuseIter_zero] at h0
    exact (syracuse_ascent_iff_mod4_eq3 n hn hodd).mp h0
  · intro hmod4 i hi
    have : i = 0 := by omega
    subst this
    simp only [syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 n hmod4

/-! ## 5. mod 16 による細分類 -/

/-- n ≡ 7 (mod 16) → syracuse n ≡ 3 (mod 8) -/
theorem syracuse_mod8_of_mod16_eq7 (n : ℕ) (h : n % 16 = 7) :
    syracuse n % 8 = 3 := by
  rw [syracuse_mod4_eq3 n (by omega)]
  omega

/-- n ≡ 15 (mod 16) → syracuse n ≡ 7 (mod 8) -/
theorem syracuse_mod8_of_mod16_eq15 (n : ℕ) (h : n % 16 = 15) :
    syracuse n % 8 = 7 := by
  rw [syracuse_mod4_eq3 n (by omega)]
  omega

/-! ## 6. 2回連続上昇 ↔ n ≡ 7 (mod 8) -/

/-- 2回連続上昇 ↔ n ≡ 7 (mod 8) -/
theorem double_ascent_mod8 (n : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 2 ↔ n % 8 = 7 := by
  unfold consecutiveAscents
  constructor
  · intro h
    have h0 := h 0 (by omega)
    have h1 := h 1 (by omega)
    simp only [syracuseIter_zero] at h0
    simp only [syracuseIter_succ, syracuseIter_zero] at h1
    exact (double_ascent_iff_mod8_eq7 n hn hodd).mp ⟨h0, h1⟩
  · intro h8 i hi
    interval_cases i
    · simp only [syracuseIter_zero]
      exact (double_ascent_iff_mod8_eq7 n hn hodd).mpr h8 |>.1
    · simp only [syracuseIter_succ, syracuseIter_zero]
      exact (double_ascent_iff_mod8_eq7 n hn hodd).mpr h8 |>.2

/-! ## 7. 3回連続上昇 ↔ n ≡ 15 (mod 16) -/

/-- n ≡ 7 (mod 8) のとき syracuse(syracuse n) の明示的な値 -/
theorem syracuse2_of_mod8_eq7 (n : ℕ) (h : n % 8 = 7) :
    syracuse (syracuse n) = (3 * ((3 * n + 1) / 2) + 1) / 2 := by
  have hmod4 : syracuse n % 4 = 3 :=
    syracuse_mod4_eq3_of_mod8_eq7 n h
  conv_lhs => rw [syracuse_mod4_eq3 (syracuse n) hmod4]
  rw [syracuse_mod4_eq3 n (by omega)]

/-- n ≡ 7 (mod 16) → syracuse^2 n ≡ 1 (mod 4) → 3回目は下降 -/
theorem syracuse2_mod4_of_mod16_eq7 (n : ℕ) (h : n % 16 = 7) :
    syracuse (syracuse n) % 4 = 1 := by
  rw [syracuse2_of_mod8_eq7 n (by omega)]
  omega

/-- n ≡ 15 (mod 16) → syracuse^2 n ≡ 3 (mod 4) → 3回目も上昇 -/
theorem syracuse2_mod4_of_mod16_eq15 (n : ℕ) (h : n % 16 = 15) :
    syracuse (syracuse n) % 4 = 3 := by
  rw [syracuse2_of_mod8_eq7 n (by omega)]
  omega

/-- 3回連続上昇 → n ≡ 15 (mod 16) -/
theorem triple_ascent_implies_mod16_eq15 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1)
    (h : consecutiveAscents n 3) : n % 16 = 15 := by
  have h2 : consecutiveAscents n 2 :=
    consecutiveAscents_mono n (by omega) h
  have h8 := (double_ascent_mod8 n hn hodd).mp h2
  have h_asc2 := h 2 (by omega)
  simp only [syracuseIter_succ, syracuseIter_zero] at h_asc2
  by_contra h16
  have hmod16 : n % 16 = 7 := by omega
  have hmod4_1 := syracuse2_mod4_of_mod16_eq7 n hmod16
  have hsyr2_pos : syracuse (syracuse n) ≥ 1 := by
    have h1 := syracuse_gt_of_mod4_eq3 n (by omega)
    have h2' := syracuse_gt_of_mod4_eq3 (syracuse n)
      (syracuse_mod4_eq3_of_mod8_eq7 n (by omega))
    omega
  have hsyr2_odd : syracuse (syracuse n) % 2 = 1 := by omega
  have hsyr2_mod4 :=
    (syracuse_ascent_iff_mod4_eq3
      (syracuse (syracuse n)) hsyr2_pos hsyr2_odd).mp h_asc2
  omega

/-- n ≡ 15 (mod 16) → 3回連続上昇 -/
theorem mod16_eq15_implies_triple_ascent (n : ℕ) (h : n % 16 = 15) :
    consecutiveAscents n 3 := by
  intro i hi
  interval_cases i
  · simp only [syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 n (by omega)
  · simp only [syracuseIter_succ, syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 (syracuse n)
      (syracuse_mod4_eq3_of_mod8_eq7 n (by omega))
  · simp only [syracuseIter_succ, syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 (syracuse (syracuse n))
      (syracuse2_mod4_of_mod16_eq15 n h)

/-- 3回連続上昇 ↔ n ≡ 15 (mod 16) -/
theorem triple_ascent_iff_mod16_eq15 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 3 ↔ n % 16 = 15 :=
  ⟨triple_ascent_implies_mod16_eq15 n hn hodd,
   mod16_eq15_implies_triple_ascent n⟩

/-! ## 8. mod 32 による 4回連続上昇 -/

/-- n ≡ 15 (mod 32) → syracuse^2 n ≡ 3 (mod 8)
    n = 32s+15 → syracuse n = 48s+23 → syracuse^2 n = 72s+35
    72s+35 mod 8 = 3 -/
theorem syracuse2_mod8_of_mod32_eq15 (n : ℕ) (h : n % 32 = 15) :
    syracuse (syracuse n) % 8 = 3 := by
  rw [syracuse2_of_mod8_eq7 n (by omega)]
  omega

/-- n ≡ 31 (mod 32) → syracuse^2 n ≡ 7 (mod 8) -/
theorem syracuse2_mod8_of_mod32_eq31 (n : ℕ) (h : n % 32 = 31) :
    syracuse (syracuse n) % 8 = 7 := by
  rw [syracuse2_of_mod8_eq7 n (by omega)]
  omega

/-- Syracuse の3段目: n ≡ 15 (mod 16) のとき -/
theorem syracuse3_of_mod16_eq15 (n : ℕ) (h : n % 16 = 15) :
    syracuse (syracuse (syracuse n)) =
    (3 * ((3 * ((3 * n + 1) / 2) + 1) / 2) + 1) / 2 := by
  have hmod4_syr2 := syracuse2_mod4_of_mod16_eq15 n h
  conv_lhs =>
    rw [syracuse_mod4_eq3 (syracuse (syracuse n)) hmod4_syr2]
  rw [syracuse2_of_mod8_eq7 n (by omega)]

/-- n ≡ 15 (mod 32) → syracuse^3 n ≡ 1 (mod 4) -/
theorem syracuse3_mod4_of_mod32_eq15 (n : ℕ) (h : n % 32 = 15) :
    syracuse (syracuse (syracuse n)) % 4 = 1 := by
  rw [syracuse3_of_mod16_eq15 n (by omega)]
  omega

/-- n ≡ 31 (mod 32) → syracuse^3 n ≡ 3 (mod 4) -/
theorem syracuse3_mod4_of_mod32_eq31 (n : ℕ) (h : n % 32 = 31) :
    syracuse (syracuse (syracuse n)) % 4 = 3 := by
  rw [syracuse3_of_mod16_eq15 n (by omega)]
  omega

/-- 4回連続上昇 → n ≡ 31 (mod 32) -/
theorem quadruple_ascent_implies_mod32_eq31 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1)
    (h : consecutiveAscents n 4) : n % 32 = 31 := by
  have h3 : consecutiveAscents n 3 :=
    consecutiveAscents_mono n (by omega) h
  have h16 := triple_ascent_implies_mod16_eq15 n hn hodd h3
  by_contra h32
  have hmod32 : n % 32 = 15 := by omega
  have hmod4 := syracuse3_mod4_of_mod32_eq15 n hmod32
  have h_asc3 := h 3 (by omega)
  simp only [syracuseIter_succ, syracuseIter_zero] at h_asc3
  have hsyr3_pos : syracuse (syracuse (syracuse n)) ≥ 1 := by
    have h1 := syracuse_gt_of_mod4_eq3 n (by omega)
    have h2' := syracuse_gt_of_mod4_eq3 (syracuse n)
      (syracuse_mod4_eq3_of_mod8_eq7 n (by omega))
    have h3' := syracuse_gt_of_mod4_eq3 (syracuse (syracuse n))
      (syracuse2_mod4_of_mod16_eq15 n h16)
    omega
  have hsyr3_odd :
      syracuse (syracuse (syracuse n)) % 2 = 1 := by omega
  have := (syracuse_ascent_iff_mod4_eq3
    (syracuse (syracuse (syracuse n)))
    hsyr3_pos hsyr3_odd).mp h_asc3
  omega

/-- n ≡ 31 (mod 32) → 4回連続上昇 -/
theorem mod32_eq31_implies_quadruple_ascent (n : ℕ)
    (h : n % 32 = 31) : consecutiveAscents n 4 := by
  intro i hi
  interval_cases i
  · simp only [syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 n (by omega)
  · simp only [syracuseIter_succ, syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 (syracuse n)
      (syracuse_mod4_eq3_of_mod8_eq7 n (by omega))
  · simp only [syracuseIter_succ, syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3 (syracuse (syracuse n))
      (syracuse2_mod4_of_mod16_eq15 n (by omega))
  · simp only [syracuseIter_succ, syracuseIter_zero]
    exact syracuse_gt_of_mod4_eq3
      (syracuse (syracuse (syracuse n)))
      (syracuse3_mod4_of_mod32_eq31 n h)

/-- 4回連続上昇 ↔ n ≡ 31 (mod 32) -/
theorem quadruple_ascent_iff_mod32_eq31 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 4 ↔ n % 32 = 31 :=
  ⟨quadruple_ascent_implies_mod32_eq31 n hn hodd,
   mod32_eq31_implies_quadruple_ascent n⟩

/-! ## 9. Hensel Attrition パターンの総括

k回連続上昇は n ≡ 2^{k+1} - 1 (mod 2^{k+1}) を要求する。
- k=1: n ≡ 3 (mod 4)     = 2^2 - 1 (mod 2^2)
- k=2: n ≡ 7 (mod 8)     = 2^3 - 1 (mod 2^3)
- k=3: n ≡ 15 (mod 16)   = 2^4 - 1 (mod 2^4)
- k=4: n ≡ 31 (mod 32)   = 2^5 - 1 (mod 2^5)
各ケースで mod 2^{k+1} の剰余類は1つだけ → 確率 1/2^k -/

/-- k=1: 1回上昇 → n ≡ 2^2 - 1 (mod 2^2) -/
theorem hensel_attrition_k1 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 1 → n % (2 ^ 2) = 2 ^ 2 - 1 := by
  rw [single_ascent_mod4 n hn hodd]
  intro h; norm_num; omega

/-- k=2: 2回連続上昇 → n ≡ 2^3 - 1 (mod 2^3) -/
theorem hensel_attrition_k2 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 2 → n % (2 ^ 3) = 2 ^ 3 - 1 := by
  rw [double_ascent_mod8 n hn hodd]
  intro h; norm_num; omega

/-- k=3: 3回連続上昇 → n ≡ 2^4 - 1 (mod 2^4) -/
theorem hensel_attrition_k3 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 3 → n % (2 ^ 4) = 2 ^ 4 - 1 := by
  rw [triple_ascent_iff_mod16_eq15 n hn hodd]
  intro h; norm_num; omega

/-- k=4: 4回連続上昇 → n ≡ 2^5 - 1 (mod 2^5) -/
theorem hensel_attrition_k4 (n : ℕ)
    (hn : n ≥ 1) (hodd : n % 2 = 1) :
    consecutiveAscents n 4 → n % (2 ^ 5) = 2 ^ 5 - 1 := by
  rw [quadruple_ascent_iff_mod32_eq31 n hn hodd]
  intro h; norm_num; omega

/-! ## 10. 数値検証 -/

-- v2 による中間値計算で syracuse の具体的な値を求める
-- n = 3: syracuse 3 = 5
private theorem syracuse_3_val : syracuse 3 = 5 := by
  change (3 * 3 + 1) / 2 ^ v2 (3 * 3 + 1) = 5
  have : v2 10 = 1 := by unfold v2; unfold v2; simp
  rw [this]; norm_num

-- n = 5: syracuse 5 = 1, so not ascending
private theorem syracuse_5_val : syracuse 5 = 1 := by
  change (3 * 5 + 1) / 2 ^ v2 (3 * 5 + 1) = 1
  have : v2 16 = 4 := by
    unfold v2; unfold v2; unfold v2; unfold v2; unfold v2; simp
  rw [this]; norm_num

-- 1回上昇の検証: n = 3
example : consecutiveAscents 3 1 := by
  rw [single_ascent_mod4 3 (by omega) (by omega)]

-- 2回連続上昇の検証: n = 7
example : consecutiveAscents 7 2 := by
  rw [double_ascent_mod8 7 (by omega) (by omega)]

-- 3回連続上昇の検証: n = 15
example : consecutiveAscents 15 3 := by
  rw [triple_ascent_iff_mod16_eq15 15 (by omega) (by omega)]

-- 4回連続上昇の検証: n = 31
example : consecutiveAscents 31 4 := by
  rw [quadruple_ascent_iff_mod32_eq31 31 (by omega) (by omega)]

-- n = 3 は 2回連続上昇しない (3 % 8 = 3 ≠ 7)
example : ¬ consecutiveAscents 3 2 := by
  rw [double_ascent_mod8 3 (by omega) (by omega)]
  omega

-- n = 7 は 3回連続上昇しない (7 % 16 = 7 ≠ 15)
example : ¬ consecutiveAscents 7 3 := by
  rw [triple_ascent_iff_mod16_eq15 7 (by omega) (by omega)]
  omega

-- n = 15 は 4回連続上昇しない (15 % 32 = 15 ≠ 31)
example : ¬ consecutiveAscents 15 4 := by
  rw [quadruple_ascent_iff_mod32_eq31 15 (by omega) (by omega)]
  omega
