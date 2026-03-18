import Mathlib

/-!
# エルデシュ問題 #52: Sum-Product Problem（和積問題）

有限整数集合 A に対して max(|A+A|, |A·A|) ≫_ε |A|^{2-ε} が成り立つか？

## 定義
- A+A (sumset) = {a+b : a,b ∈ A}
- A·A (product set) = {a*b : a,b ∈ A}

## 予想 (Erdős-Szemerédi, 1983)
任意の ε > 0 に対して定数 c_ε が存在し、
全ての有限整数集合 A に対して max(|A+A|, |A·A|) ≥ c_ε |A|^{2-ε}

## 最良結果
Bloom (2025): max(|A+A|, |A·A|) ≥ |A|^{1270/951} (≈ |A|^{1.335})

## 探索の概要

### 探索1: Python数値実験 (scripts/erdos52_sum_product.py)
- 等差数列: |A+A| = 2n-1 (最小), |A·A| ≈ n²/ln(n) (大きい)
- 等比数列: |A·A| = 2n-1 (最小), |A+A| は巨大
- ランダム集合: |A+A| ≈ |A·A| ≈ |A|² に近い
- max(|A+A|,|A·A|)/|A|^α の比率は α<2 で発散傾向

### 探索2: 特殊集合の解析 (scripts/erdos52_special_sets.py)
- Freiman-Ruzsa: 倍加定数小 → 算術的 → |A·A| 大
- smooth numbers: 最も比率を抑えるが |A|^2 未満にはならない
- F_p 上: 二次剰余は |QR·QR|=|QR| だが |QR+QR|≈p
- 対数変換が加法/乗法構造の双対性の本質

### 探索3: Lean形式化（本ファイル）
- sumset, productset の Finset 上の定義
- 小さい例での検証
- 自明な下界の証明

### 探索10: A={1,...,n} の sumset カード = 2n-1
- {1,2,3,4} の sumset card = 7, productset card = 9
-/

open Finset

/-! ## sumset と productset の定義 -/

/-- sumset A + A: 集合 A の全ての2元の和の集合 -/
noncomputable def sumsetFinset (A : Finset ℕ) : Finset ℕ :=
  (A ×ˢ A).image (fun p => p.1 + p.2)

/-- productset A · A: 集合 A の全ての2元の積の集合 -/
noncomputable def prodsetFinset (A : Finset ℕ) : Finset ℕ :=
  (A ×ˢ A).image (fun p => p.1 * p.2)

/-! ## 小さい例での検証 -/

/-- A = {1, 2, 3} のとき |A+A| = |{2,3,4,5,6}| = 5 -/
theorem sumset_123_card :
    (sumsetFinset {1, 2, 3}).card = 5 := by
  simp only [sumsetFinset]
  decide

/-- A = {1, 2, 3} のとき |A·A| = |{1,2,3,4,6,9}| = 6 -/
theorem prodset_123_card :
    (prodsetFinset {1, 2, 3}).card = 6 := by
  simp only [prodsetFinset]
  decide

/-! ## 基本的な性質 -/

/-- sumset の要素は A×A の image -/
theorem mem_sumsetFinset {A : Finset ℕ} {x : ℕ} :
    x ∈ sumsetFinset A ↔ ∃ a ∈ A, ∃ b ∈ A, a + b = x := by
  unfold sumsetFinset
  simp only [Finset.mem_image, Finset.mem_product]
  constructor
  · rintro ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩
    exact ⟨a, ha, b, hb, heq⟩
  · rintro ⟨a, ha, b, hb, heq⟩
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩

/-- productset の要素は A×A の image -/
theorem mem_prodsetFinset {A : Finset ℕ} {x : ℕ} :
    x ∈ prodsetFinset A ↔ ∃ a ∈ A, ∃ b ∈ A, a * b = x := by
  unfold prodsetFinset
  simp only [Finset.mem_image, Finset.mem_product]
  constructor
  · rintro ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩
    exact ⟨a, ha, b, hb, heq⟩
  · rintro ⟨a, ha, b, hb, heq⟩
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩

/-- sumset は元の集合の全要素 a+a を含む -/
theorem mem_sumsetFinset_diag {A : Finset ℕ} {a : ℕ} (ha : a ∈ A) :
    a + a ∈ sumsetFinset A := by
  rw [mem_sumsetFinset]
  exact ⟨a, ha, a, ha, rfl⟩

/-- productset は元の集合の全要素 a*a を含む -/
theorem mem_prodsetFinset_diag {A : Finset ℕ} {a : ℕ} (ha : a ∈ A) :
    a * a ∈ prodsetFinset A := by
  rw [mem_prodsetFinset]
  exact ⟨a, ha, a, ha, rfl⟩

/-! ## 自明な下界 -/

/-- 空でない集合の sumset は空でない -/
theorem sumsetFinset_nonempty {A : Finset ℕ} (hA : A.Nonempty) :
    (sumsetFinset A).Nonempty := by
  obtain ⟨a, ha⟩ := hA
  exact ⟨a + a, mem_sumsetFinset_diag ha⟩

/-- 空でない集合の productset は空でない -/
theorem prodsetFinset_nonempty {A : Finset ℕ} (hA : A.Nonempty) :
    (prodsetFinset A).Nonempty := by
  obtain ⟨a, ha⟩ := hA
  exact ⟨a * a, mem_prodsetFinset_diag ha⟩

/-- |A+A| ≥ |A|: 各 a ∈ A に対し a + min(A) は互いに異なり sumset に含まれる -/
theorem card_le_sumsetFinset_card {A : Finset ℕ} :
    A.card ≤ (sumsetFinset A).card := by
  by_cases hA : A = ∅
  · simp [hA, sumsetFinset]
  · have hne : A.Nonempty := Finset.nonempty_of_ne_empty hA
    let m := A.min' hne
    have hm : m ∈ A := Finset.min'_mem A hne
    -- A.image (· + m) ⊆ sumsetFinset A を示し、image の単射性から card を得る
    have hsub : A.image (· + m) ⊆ sumsetFinset A := by
      intro x hx
      rw [Finset.mem_image] at hx
      obtain ⟨a, ha, rfl⟩ := hx
      rw [mem_sumsetFinset]
      exact ⟨a, ha, m, hm, rfl⟩
    have hinj : Set.InjOn (· + m) (A : Set ℕ) := by
      intro a₁ _ a₂ _ h
      simp only at h
      omega
    calc A.card = (A.image (· + m)).card := by
              rw [Finset.card_image_of_injOn hinj]
         _ ≤ (sumsetFinset A).card := Finset.card_le_card hsub

/-!
## Sum-Product 予想の形式的記述

エルデシュ-セメレディ予想: 任意の ε > 0 に対し、定数 C_ε が存在して、
全ての有限整数集合 A (|A| ≥ 2) に対して
  max(|A+A|, |A·A|) ≥ C_ε |A|^{2-ε}
-/

/-- Sum-Product予想の形式的記述（実数版） -/
def SumProductConjecture : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ C : ℝ, C > 0 ∧
      ∀ A : Finset ℕ, A.card ≥ 2 →
        (max (sumsetFinset A).card (prodsetFinset A).card : ℝ) ≥
          C * (A.card : ℝ) ^ (2 - ε)

/-! ## 探索6: |A·A| ≥ |A| の証明

sumsetFinset の既存証明 `card_le_sumsetFinset_card` と同様のアプローチ。
A の最小元 m を取り、A.image (· * m) ⊆ prodsetFinset A を示す。
(· * m) は A 上で単射（m > 0 であるため）。
よって |A.image (· * m)| = |A| ≤ |prodsetFinset A|。

0 ∈ A の場合は 0*a = 0 で全て潰れるため、∀ a ∈ A, a > 0 の仮定が必要。
-/

/-- productset のサイズは元の集合のサイズ以上: |A·A| ≥ |A| -/
theorem card_le_prodsetFinset_card {A : Finset ℕ} (hA : ∀ a ∈ A, a > 0) :
    A.card ≤ (prodsetFinset A).card := by
  by_cases hAe : A = ∅
  · simp [hAe, prodsetFinset]
  · have hne : A.Nonempty := Finset.nonempty_of_ne_empty hAe
    let m := A.min' hne
    have hm : m ∈ A := Finset.min'_mem A hne
    have hm_pos : m > 0 := hA m hm
    have hsub : A.image (· * m) ⊆ prodsetFinset A := by
      intro x hx
      rw [Finset.mem_image] at hx
      obtain ⟨a, ha, rfl⟩ := hx
      rw [mem_prodsetFinset]
      exact ⟨a, ha, m, hm, rfl⟩
    have hinj : Set.InjOn (· * m) (A : Set ℕ) := by
      intro a₁ _ a₂ _ h
      simp only at h
      have : a₁ * m / m = a₂ * m / m := by rw [h]
      simp [Nat.mul_div_cancel _ (by omega : m > 0)] at this
      exact this
    calc A.card = (A.image (· * m)).card := by
              rw [Finset.card_image_of_injOn hinj]
         _ ≤ (prodsetFinset A).card := Finset.card_le_card hsub

/-! ## 探索7: sumset/productset の追加性質 -/

/-- 部分集合の sumset は元の sumset の部分集合 -/
theorem sumsetFinset_mono {A B : Finset ℕ} (h : A ⊆ B) :
    sumsetFinset A ⊆ sumsetFinset B := by
  intro x hx
  rw [mem_sumsetFinset] at hx ⊢
  obtain ⟨a, ha, b, hb, heq⟩ := hx
  exact ⟨a, h ha, b, h hb, heq⟩

/-- 部分集合の productset は元の productset の部分集合 -/
theorem prodsetFinset_mono {A B : Finset ℕ} (h : A ⊆ B) :
    prodsetFinset A ⊆ prodsetFinset B := by
  intro x hx
  rw [mem_prodsetFinset] at hx ⊢
  obtain ⟨a, ha, b, hb, heq⟩ := hx
  exact ⟨a, h ha, b, h hb, heq⟩

/-- |A+A| ≤ |A|^2 -/
theorem sumsetFinset_card_le_sq {A : Finset ℕ} :
    (sumsetFinset A).card ≤ A.card * A.card := by
  unfold sumsetFinset
  have h1 : ((A ×ˢ A).image (fun p => p.1 + p.2)).card ≤ (A ×ˢ A).card :=
    Finset.card_image_le
  have h2 : (A ×ˢ A).card = A.card * A.card := Finset.card_product A A
  omega

/-- |A·A| ≤ |A|^2 -/
theorem prodsetFinset_card_le_sq {A : Finset ℕ} :
    (prodsetFinset A).card ≤ A.card * A.card := by
  unfold prodsetFinset
  have h1 : ((A ×ˢ A).image (fun p => p.1 * p.2)).card ≤ (A ×ˢ A).card :=
    Finset.card_image_le
  have h2 : (A ×ˢ A).card = A.card * A.card := Finset.card_product A A
  omega

/-! ## 探索8: 特殊集合の sumset/productset

シングルトン集合 {a} の sumset は {2a}、productset は {a²} である。
これは和積問題において自明な等号ケース: max(|A+A|, |A·A|) = 1 = |A|。
また {1,2} での計算例も確認する。
-/

/-- シングルトン {a} の sumset は {a+a} -/
theorem sumsetFinset_singleton (a : ℕ) :
    sumsetFinset {a} = {a + a} := by
  ext x
  rw [mem_sumsetFinset]
  simp only [Finset.mem_singleton]
  constructor
  · rintro ⟨b, rfl, c, rfl, rfl⟩; rfl
  · intro hx; exact ⟨a, rfl, a, rfl, hx.symm⟩

/-- シングルトン {a} の productset は {a*a} -/
theorem prodsetFinset_singleton (a : ℕ) :
    prodsetFinset {a} = {a * a} := by
  ext x
  rw [mem_prodsetFinset]
  simp only [Finset.mem_singleton]
  constructor
  · rintro ⟨b, rfl, c, rfl, rfl⟩; rfl
  · intro hx; exact ⟨a, rfl, a, rfl, hx.symm⟩

/-- {1,2} の sumset のカード数は 3: {2,3,4} -/
theorem sumset_12_card : (sumsetFinset {1, 2}).card = 3 := by
  simp only [sumsetFinset]; decide

/-- {1,2} の productset のカード数は 3: {1,2,4} -/
theorem prodset_12_card : (prodsetFinset {1, 2}).card = 3 := by
  simp only [prodsetFinset]; decide

/-! ## 探索9: 2元集合の和積比較 -/

/-- {1, 3}: sumset = {2, 4, 6}, card = 3 -/
theorem sumset_13_card : (sumsetFinset {1, 3}).card = 3 := by
  simp only [sumsetFinset]; decide

/-- {1, 3}: prodset = {1, 3, 9}, card = 3 -/
theorem prodset_13_card : (prodsetFinset {1, 3}).card = 3 := by
  simp only [prodsetFinset]; decide

/-- {2, 3}: sumset = {4, 5, 6}, card = 3 -/
theorem sumset_23_card : (sumsetFinset {2, 3}).card = 3 := by
  simp only [sumsetFinset]; decide

/-- {2, 3}: prodset = {4, 6, 9}, card = 3 -/
theorem prodset_23_card : (prodsetFinset {2, 3}).card = 3 := by
  simp only [prodsetFinset]; decide

/-! ## 探索10: A={1,...,n} の sumset カード = 2n-1 -/

-- {1,2,3,4} の sumset カード = 7
theorem sumset_1234_card : (sumsetFinset {1, 2, 3, 4}).card = 7 := by
  simp only [sumsetFinset]; decide

-- {1,2,3,4} の productset カード = 9
theorem prodset_1234_card : (prodsetFinset {1, 2, 3, 4}).card = 9 := by
  simp only [prodsetFinset]; decide

/-! ## 探索11: 3元集合の和積 -/

-- {1,2,4} (等比的): sumset card = 6, prodset card = 5
theorem sumset_124_card : (sumsetFinset {1, 2, 4}).card = 6 := by
  simp only [sumsetFinset]; decide

theorem prodset_124_card : (prodsetFinset {1, 2, 4}).card = 5 := by
  simp only [prodsetFinset]; decide

/-! ## 探索12: 等差数列の sumset = 2n-1 -/

-- {1,...,5}: sumset card = 9 = 2*5-1
theorem sumset_12345_card : (sumsetFinset {1, 2, 3, 4, 5}).card = 9 := by
  simp only [sumsetFinset]; decide

-- {1,...,5}: prodset card
theorem prodset_12345_card : (prodsetFinset {1, 2, 3, 4, 5}).card = 14 := by
  simp only [prodsetFinset]; decide

/-! ## 探索13: sumset の自明な等式 -/

/-- 空集合の sumset は空 -/
theorem sumsetFinset_empty : sumsetFinset (∅ : Finset ℕ) = ∅ := by
  simp [sumsetFinset]

/-- 空集合の productset は空 -/
theorem prodsetFinset_empty : prodsetFinset (∅ : Finset ℕ) = ∅ := by
  simp [prodsetFinset]

/-! ## 探索14: sumset の等差数列公式 -/

/-- 等差数列 {1,...,n} の sumset は {2,...,2n} で |A+A| = 2n-1 -/
-- {1,2,3}: card 5 = 2*3-1 (既存 sumset_123_card)
-- {1,...,4}: card 7 = 2*4-1 (既存 sumset_1234_card)
-- {1,...,5}: card 9 = 2*5-1 (既存 sumset_12345_card)

-- {1,...,6}: card = 11 = 2*6-1
theorem sumset_123456_card : (sumsetFinset {1, 2, 3, 4, 5, 6}).card = 11 := by
  simp only [sumsetFinset]; decide

/-! ## 探索15: シングルトンの sumset/prodset -/

/-- シングルトン {1} の sumset のカードは 1 -/
theorem sumsetFinset_singleton1_card : (sumsetFinset {1}).card = 1 := by
  simp only [sumsetFinset]; decide

/-! ## 探索16: prodset の等差数列 -/
-- {1,2,3,4,5,6} の prodset card
theorem prodset_123456_card : (prodsetFinset {1, 2, 3, 4, 5, 6}).card = 18 := by
  simp only [prodsetFinset]; decide

/-! ## 探索16: 等比数列の prodset -/

-- {1,2,4,8}: prodset card
theorem prodset_1248_card : (prodsetFinset {1, 2, 4, 8}).card = 7 := by
  simp only [prodsetFinset]; decide

/-! ## |A+A| ≥ 2|A| - 1: Cauchy-Davenport 型の下界

等差数列 {1,...,n} で |A+A| = 2n-1 が達成される。
一般の有限集合 A に対しても |A+A| ≥ 2|A| - 1 が成り立つ。

証明のアイデア:
- m = min(A), M = max(A)
- S₁ = A.image (· + m) ⊆ A+A: 全元 ≤ M + m
- S₂' = (A.erase m).image (· + M) ⊆ A+A: 全元 > m + M（a > m なので a + M > m + M）
- S₁ と S₂' は disjoint
- |A+A| ≥ |S₁| + |S₂'| = |A| + (|A| - 1) = 2|A| - 1
-/

/-- |A+A| ≥ 2|A| - 1: sumset の精密な下界 -/
theorem card_sumsetFinset_ge_two_mul_sub_one {A : Finset ℕ} (hA : A.Nonempty) :
    (sumsetFinset A).card ≥ 2 * A.card - 1 := by
  -- min と max を取る
  let m := A.min' hA
  let M := A.max' hA
  have hm : m ∈ A := Finset.min'_mem A hA
  have hM : M ∈ A := Finset.max'_mem A hA
  -- S₁ = A.image (· + m)
  let S₁ := A.image (· + m)
  -- S₂' = (A.erase m).image (· + M)
  let S₂' := (A.erase m).image (· + M)
  -- S₁ ⊆ sumsetFinset A
  have hS₁_sub : S₁ ⊆ sumsetFinset A := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    rw [mem_sumsetFinset]
    exact ⟨a, ha, m, hm, rfl⟩
  -- S₂' ⊆ sumsetFinset A
  have hS₂'_sub : S₂' ⊆ sumsetFinset A := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha_erase, rfl⟩ := hx
    have ha : a ∈ A := Finset.mem_of_mem_erase ha_erase
    rw [mem_sumsetFinset]
    exact ⟨a, ha, M, hM, rfl⟩
  -- S₁ の元は ≤ M + m
  have hS₁_le : ∀ x ∈ S₁, x ≤ M + m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    have : a ≤ M := Finset.le_max' A a ha
    omega
  -- S₂' の元は > m + M (つまり ≥ m + M + 1)
  have hS₂'_gt : ∀ x ∈ S₂', x > m + M := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha_erase, rfl⟩ := hx
    have ha : a ∈ A := Finset.mem_of_mem_erase ha_erase
    have ha_ne : a ≠ m := Finset.ne_of_mem_erase ha_erase
    have : m ≤ a := Finset.min'_le A a ha
    omega
  -- S₁ と S₂' は disjoint
  have hdisj : Disjoint S₁ S₂' := by
    rw [Finset.disjoint_left]
    intro x hx₁ hx₂
    have h₁ := hS₁_le x hx₁
    have h₂ := hS₂'_gt x hx₂
    omega
  -- |S₁| = |A|
  have hcard_S₁ : S₁.card = A.card := by
    apply Finset.card_image_of_injOn
    intro a₁ _ a₂ _ h
    simp only at h
    omega
  -- |S₂'| = |A| - 1
  have hcard_S₂' : S₂'.card = A.card - 1 := by
    have : S₂'.card = (A.erase m).card := by
      apply Finset.card_image_of_injOn
      intro a₁ _ a₂ _ h
      simp only at h
      omega
    rw [this, Finset.card_erase_of_mem hm]
  -- |S₁ ∪ S₂'| = |S₁| + |S₂'|
  have hunion : (S₁ ∪ S₂').card = S₁.card + S₂'.card :=
    Finset.card_union_of_disjoint hdisj
  -- S₁ ∪ S₂' ⊆ sumsetFinset A
  have hsub_union : S₁ ∪ S₂' ⊆ sumsetFinset A :=
    Finset.union_subset hS₁_sub hS₂'_sub
  -- 結論
  calc (sumsetFinset A).card
      ≥ (S₁ ∪ S₂').card := Finset.card_le_card hsub_union
    _ = S₁.card + S₂'.card := hunion
    _ = A.card + (A.card - 1) := by rw [hcard_S₁, hcard_S₂']
    _ = 2 * A.card - 1 := by omega

/-! ## |A·A| ≥ 2|A| - 1: 正整数集合の productset の精密下界

等比数列 {1,2,4,...,2^{n-1}} で |A·A| = 2n-1 が達成される。
一般の正整数有限集合 A に対しても |A·A| ≥ 2|A| - 1 が成り立つ。

証明のアイデア:
- m = min(A), M = max(A)（全て > 0）
- S₁ = A.image (· * m) ⊆ A·A: 全元 ≤ M * m
- S₂' = (A.erase m).image (· * M) ⊆ A·A: 全元 > m * M（a > m なので a * M > m * M）
- M * m = m * M なので S₁ の最大元 ≤ m * M < S₂' の全元
- S₁ と S₂' は disjoint
- |A·A| ≥ |S₁| + |S₂'| = |A| + (|A| - 1) = 2|A| - 1
-/

/-- 正整数集合の productset の精密下界: |A·A| ≥ 2|A|-1 -/
theorem card_prodsetFinset_ge_two_mul_sub_one {A : Finset ℕ}
    (hA : A.Nonempty) (hpos : ∀ a ∈ A, a > 0) :
    (prodsetFinset A).card ≥ 2 * A.card - 1 := by
  -- min と max を取る
  let m := A.min' hA
  let M := A.max' hA
  have hm : m ∈ A := Finset.min'_mem A hA
  have hM : M ∈ A := Finset.max'_mem A hA
  have hm_pos : m > 0 := hpos m hm
  have hM_pos : M > 0 := hpos M hM
  -- S₁ = A.image (· * m)
  let S₁ := A.image (· * m)
  -- S₂' = (A.erase m).image (· * M)
  let S₂' := (A.erase m).image (· * M)
  -- S₁ ⊆ prodsetFinset A
  have hS₁_sub : S₁ ⊆ prodsetFinset A := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    rw [mem_prodsetFinset]
    exact ⟨a, ha, m, hm, rfl⟩
  -- S₂' ⊆ prodsetFinset A
  have hS₂'_sub : S₂' ⊆ prodsetFinset A := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha_erase, rfl⟩ := hx
    have ha : a ∈ A := Finset.mem_of_mem_erase ha_erase
    rw [mem_prodsetFinset]
    exact ⟨a, ha, M, hM, rfl⟩
  -- S₁ の元は ≤ M * m
  have hS₁_le : ∀ x ∈ S₁, x ≤ M * m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    have : a ≤ M := Finset.le_max' A a ha
    exact Nat.mul_le_mul_right m this
  -- S₂' の元は > m * M (つまり > M * m)
  have hS₂'_gt : ∀ x ∈ S₂', x > m * M := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha_erase, rfl⟩ := hx
    have ha : a ∈ A := Finset.mem_of_mem_erase ha_erase
    have ha_ne : a ≠ m := Finset.ne_of_mem_erase ha_erase
    have hm_le : m ≤ a := Finset.min'_le A a ha
    have hm_lt : m < a := Nat.lt_of_le_of_ne hm_le (Ne.symm ha_ne)
    exact Nat.mul_lt_mul_of_pos_right hm_lt hM_pos
  -- S₁ と S₂' は disjoint
  have hdisj : Disjoint S₁ S₂' := by
    rw [Finset.disjoint_left]
    intro x hx₁ hx₂
    have h₁ := hS₁_le x hx₁
    have h₂ := hS₂'_gt x hx₂
    rw [Nat.mul_comm m M] at h₂
    omega
  -- |S₁| = |A|
  have hcard_S₁ : S₁.card = A.card := by
    apply Finset.card_image_of_injOn
    intro a₁ _ a₂ _ h
    simp only at h
    exact Nat.mul_right_cancel hm_pos h
  -- |S₂'| = |A| - 1
  have hcard_S₂' : S₂'.card = A.card - 1 := by
    have : S₂'.card = (A.erase m).card := by
      apply Finset.card_image_of_injOn
      intro a₁ _ a₂ _ h
      simp only at h
      exact Nat.mul_right_cancel hM_pos h
    rw [this, Finset.card_erase_of_mem hm]
  -- |S₁ ∪ S₂'| = |S₁| + |S₂'|
  have hunion : (S₁ ∪ S₂').card = S₁.card + S₂'.card :=
    Finset.card_union_of_disjoint hdisj
  -- S₁ ∪ S₂' ⊆ prodsetFinset A
  have hsub_union : S₁ ∪ S₂' ⊆ prodsetFinset A :=
    Finset.union_subset hS₁_sub hS₂'_sub
  -- 結論
  calc (prodsetFinset A).card
      ≥ (S₁ ∪ S₂').card := Finset.card_le_card hsub_union
    _ = S₁.card + S₂'.card := hunion
    _ = A.card + (A.card - 1) := by rw [hcard_S₁, hcard_S₂']
    _ = 2 * A.card - 1 := by omega

-- =============================================================================
-- 等差数列の sumset カード検証の拡充
-- =============================================================================

/-! ## 等差数列 {1,...,n} の sumset card = 2n-1 の検証

等差数列の sumset は最小の sumset を達成する。
{1,...,n} + {1,...,n} = {2,...,2n} なのでカードは 2n-1。
ここでは n=7 の場合を具体的に検証する。
-/

/-- {1,...,7}: sumset card = 13 = 2*7-1 -/
theorem sumset_1to7_card : (sumsetFinset {1, 2, 3, 4, 5, 6, 7}).card = 13 := by
  simp only [sumsetFinset]; decide

-- =============================================================================
-- sum-product の下界: max(|A+A|, |A·A|) ≥ 2|A|-1
-- =============================================================================

/-- sum-product の下界: max(|A+A|, |A·A|) ≥ 2|A|-1 -/
theorem max_sumset_prodset_ge {A : Finset ℕ} (hA : A.Nonempty) :
    max (sumsetFinset A).card (prodsetFinset A).card ≥ 2 * A.card - 1 := by
  have h1 := card_sumsetFinset_ge_two_mul_sub_one hA
  calc 2 * A.card - 1 ≤ (sumsetFinset A).card := h1
    _ ≤ max (sumsetFinset A).card (prodsetFinset A).card := le_max_left _ _

-- =============================================================================
-- 一般化 sumset: A + B = {a + b : a ∈ A, b ∈ B}
-- =============================================================================

/-! ## 一般化 sumset

2つの有限自然数集合 A, B に対して A + B = {a + b : a ∈ A, b ∈ B} を定義し、
|A + B| ≥ |A| + |B| - 1 を証明する。
これは |A + A| ≥ 2|A| - 1 の一般化であり、Cauchy-Davenport 不等式の自然数版。
-/

/-- 2集合の sumset: A + B = {a + b : a ∈ A, b ∈ B} -/
noncomputable def sumsetFinset2 (A B : Finset ℕ) : Finset ℕ :=
  (A ×ˢ B).image (fun p => p.1 + p.2)

/-- sumsetFinset2 の要素の特徴付け -/
theorem mem_sumsetFinset2 {A B : Finset ℕ} {x : ℕ} :
    x ∈ sumsetFinset2 A B ↔ ∃ a ∈ A, ∃ b ∈ B, a + b = x := by
  unfold sumsetFinset2
  simp only [Finset.mem_image, Finset.mem_product]
  constructor
  · rintro ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩
    exact ⟨a, ha, b, hb, heq⟩
  · rintro ⟨a, ha, b, hb, heq⟩
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩

/-- sumsetFinset は sumsetFinset2 の特殊ケース: sumsetFinset A = sumsetFinset2 A A -/
theorem sumsetFinset_eq_sumsetFinset2 (A : Finset ℕ) :
    sumsetFinset A = sumsetFinset2 A A := by
  ext x
  rw [mem_sumsetFinset, mem_sumsetFinset2]

/-- |A + B| ≥ |A| + |B| - 1: 一般化 sumset の Cauchy-Davenport 型下界 -/
theorem card_sumsetFinset2_ge {A B : Finset ℕ} (hA : A.Nonempty) (hB : B.Nonempty) :
    (sumsetFinset2 A B).card ≥ A.card + B.card - 1 := by
  -- min(B) と max(A) を取る
  let m := B.min' hB
  let M := A.max' hA
  have hm : m ∈ B := Finset.min'_mem B hB
  have hM : M ∈ A := Finset.max'_mem A hA
  -- S₁ = A.image (· + m): |A| 個の元、全元 ≤ M + m
  let S₁ := A.image (· + m)
  -- S₂' = (B.erase m).image (M + ·): |B| - 1 個の元、全元 > M + m
  let S₂' := (B.erase m).image (M + ·)
  -- S₁ ⊆ sumsetFinset2 A B
  have hS₁_sub : S₁ ⊆ sumsetFinset2 A B := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    rw [mem_sumsetFinset2]
    exact ⟨a, ha, m, hm, rfl⟩
  -- S₂' ⊆ sumsetFinset2 A B
  have hS₂'_sub : S₂' ⊆ sumsetFinset2 A B := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨b, hb_erase, rfl⟩ := hx
    have hb : b ∈ B := Finset.mem_of_mem_erase hb_erase
    rw [mem_sumsetFinset2]
    exact ⟨M, hM, b, hb, rfl⟩
  -- S₁ の元は ≤ M + m
  have hS₁_le : ∀ x ∈ S₁, x ≤ M + m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    have : a ≤ M := Finset.le_max' A a ha
    omega
  -- S₂' の元は > M + m
  have hS₂'_gt : ∀ x ∈ S₂', x > M + m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨b, hb_erase, rfl⟩ := hx
    have hb : b ∈ B := Finset.mem_of_mem_erase hb_erase
    have hb_ne : b ≠ m := Finset.ne_of_mem_erase hb_erase
    have : m ≤ b := Finset.min'_le B b hb
    omega
  -- S₁ と S₂' は disjoint
  have hdisj : Disjoint S₁ S₂' := by
    rw [Finset.disjoint_left]
    intro x hx₁ hx₂
    have h₁ := hS₁_le x hx₁
    have h₂ := hS₂'_gt x hx₂
    omega
  -- |S₁| = |A|
  have hcard_S₁ : S₁.card = A.card := by
    apply Finset.card_image_of_injOn
    intro a₁ _ a₂ _ h
    simp only at h
    omega
  -- |S₂'| = |B| - 1
  have hcard_S₂' : S₂'.card = B.card - 1 := by
    have : S₂'.card = (B.erase m).card := by
      apply Finset.card_image_of_injOn
      intro b₁ _ b₂ _ h
      simp only at h
      omega
    rw [this, Finset.card_erase_of_mem hm]
  -- |S₁ ∪ S₂'| = |S₁| + |S₂'|
  have hunion : (S₁ ∪ S₂').card = S₁.card + S₂'.card :=
    Finset.card_union_of_disjoint hdisj
  -- S₁ ∪ S₂' ⊆ sumsetFinset2 A B
  have hsub_union : S₁ ∪ S₂' ⊆ sumsetFinset2 A B :=
    Finset.union_subset hS₁_sub hS₂'_sub
  -- 結論
  calc (sumsetFinset2 A B).card
      ≥ (S₁ ∪ S₂').card := Finset.card_le_card hsub_union
    _ = S₁.card + S₂'.card := hunion
    _ = A.card + (B.card - 1) := by rw [hcard_S₁, hcard_S₂']
    _ = A.card + B.card - 1 := by
        have : B.card ≥ 1 := Finset.Nonempty.card_pos hB
        omega

-- =============================================================================
-- 一般化 productset: A · B = {a * b : a ∈ A, b ∈ B}
-- =============================================================================

/-! ## 一般化 productset

2つの有限正整数集合 A, B に対して A · B = {a * b : a ∈ A, b ∈ B} を定義し、
|A · B| ≥ |A| + |B| - 1 を証明する。
これは |A · A| ≥ 2|A| - 1 の一般化。
-/

/-- 2集合の一般化 productset: A·B = {a*b : a ∈ A, b ∈ B} -/
noncomputable def prodsetFinset2 (A B : Finset ℕ) : Finset ℕ :=
  (A ×ˢ B).image (fun p => p.1 * p.2)

/-- prodsetFinset2 の要素の特徴付け -/
theorem mem_prodsetFinset2 {A B : Finset ℕ} {x : ℕ} :
    x ∈ prodsetFinset2 A B ↔ ∃ a ∈ A, ∃ b ∈ B, a * b = x := by
  unfold prodsetFinset2
  simp only [Finset.mem_image, Finset.mem_product]
  constructor
  · rintro ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩
    exact ⟨a, ha, b, hb, heq⟩
  · rintro ⟨a, ha, b, hb, heq⟩
    exact ⟨⟨a, b⟩, ⟨ha, hb⟩, heq⟩

/-- prodsetFinset は prodsetFinset2 の特殊ケース: prodsetFinset A = prodsetFinset2 A A -/
theorem prodsetFinset_eq_prodsetFinset2 (A : Finset ℕ) :
    prodsetFinset A = prodsetFinset2 A A := by
  ext x
  rw [mem_prodsetFinset, mem_prodsetFinset2]

/-- |A·B| ≥ |A| + |B| - 1（A, B は正整数の集合） -/
theorem card_prodsetFinset2_ge {A B : Finset ℕ}
    (hA : A.Nonempty) (hB : B.Nonempty)
    (hposA : ∀ a ∈ A, a > 0) (hposB : ∀ b ∈ B, b > 0) :
    (prodsetFinset2 A B).card ≥ A.card + B.card - 1 := by
  -- min(B) と max(A) を取る
  let m := B.min' hB
  let M := A.max' hA
  have hm : m ∈ B := Finset.min'_mem B hB
  have hM : M ∈ A := Finset.max'_mem A hA
  have hm_pos : m > 0 := hposB m hm
  have hM_pos : M > 0 := hposA M hM
  -- S₁ = A.image (· * m): |A| 個の元、全元 ≤ M * m
  let S₁ := A.image (· * m)
  -- S₂' = (B.erase m).image (M * ·): |B| - 1 個の元、全元 > M * m
  let S₂' := (B.erase m).image (M * ·)
  -- S₁ ⊆ prodsetFinset2 A B
  have hS₁_sub : S₁ ⊆ prodsetFinset2 A B := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    rw [mem_prodsetFinset2]
    exact ⟨a, ha, m, hm, rfl⟩
  -- S₂' ⊆ prodsetFinset2 A B
  have hS₂'_sub : S₂' ⊆ prodsetFinset2 A B := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨b, hb_erase, rfl⟩ := hx
    have hb : b ∈ B := Finset.mem_of_mem_erase hb_erase
    rw [mem_prodsetFinset2]
    exact ⟨M, hM, b, hb, rfl⟩
  -- S₁ の元は ≤ M * m
  have hS₁_le : ∀ x ∈ S₁, x ≤ M * m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨a, ha, rfl⟩ := hx
    have : a ≤ M := Finset.le_max' A a ha
    exact Nat.mul_le_mul_right m this
  -- S₂' の元は > M * m
  have hS₂'_gt : ∀ x ∈ S₂', x > M * m := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨b, hb_erase, rfl⟩ := hx
    have hb : b ∈ B := Finset.mem_of_mem_erase hb_erase
    have hb_ne : b ≠ m := Finset.ne_of_mem_erase hb_erase
    have hm_le : m ≤ b := Finset.min'_le B b hb
    have hm_lt : m < b := Nat.lt_of_le_of_ne hm_le (Ne.symm hb_ne)
    exact Nat.mul_lt_mul_of_pos_left hm_lt hM_pos
  -- S₁ と S₂' は disjoint
  have hdisj : Disjoint S₁ S₂' := by
    rw [Finset.disjoint_left]
    intro x hx₁ hx₂
    have h₁ := hS₁_le x hx₁
    have h₂ := hS₂'_gt x hx₂
    omega
  -- |S₁| = |A|
  have hcard_S₁ : S₁.card = A.card := by
    apply Finset.card_image_of_injOn
    intro a₁ _ a₂ _ h
    simp only at h
    exact Nat.mul_right_cancel hm_pos h
  -- |S₂'| = |B| - 1
  have hcard_S₂' : S₂'.card = B.card - 1 := by
    have : S₂'.card = (B.erase m).card := by
      apply Finset.card_image_of_injOn
      intro b₁ _ b₂ _ h
      simp only at h
      exact Nat.mul_left_cancel hM_pos h
    rw [this, Finset.card_erase_of_mem hm]
  -- |S₁ ∪ S₂'| = |S₁| + |S₂'|
  have hunion : (S₁ ∪ S₂').card = S₁.card + S₂'.card :=
    Finset.card_union_of_disjoint hdisj
  -- S₁ ∪ S₂' ⊆ prodsetFinset2 A B
  have hsub_union : S₁ ∪ S₂' ⊆ prodsetFinset2 A B :=
    Finset.union_subset hS₁_sub hS₂'_sub
  -- 結論
  calc (prodsetFinset2 A B).card
      ≥ (S₁ ∪ S₂').card := Finset.card_le_card hsub_union
    _ = S₁.card + S₂'.card := hunion
    _ = A.card + (B.card - 1) := by rw [hcard_S₁, hcard_S₂']
    _ = A.card + B.card - 1 := by
        have : B.card ≥ 1 := Finset.Nonempty.card_pos hB
        omega
