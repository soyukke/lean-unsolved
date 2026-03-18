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
