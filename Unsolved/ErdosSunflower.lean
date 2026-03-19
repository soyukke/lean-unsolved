import Mathlib

/-!
# エルデシュ問題 #20: Sunflower Conjecture（ひまわり予想）

## 問題
f(n,k) = n-均一集合族がk-ひまわりを含むための最小サイズとする。
f(n,k) < c_k^n が成り立つか？（c_k は k のみに依存する定数）

## 定義
- k-ひまわり: k個の集合で、任意の2つの共通部分が全て同じ（core）
  各集合からcoreを引いた「花びら」は互いに素

## 歴史
- Erdős-Rado (1960): f(n,k) ≤ (k-1)^n · n! + 1
- Alweiss-Lovett-Wu-Zhang (2020): f(n,k) ≤ (C·k·log(n))^n
- 予想（未解決）: f(n,k) ≤ c_k^n

## 探索の概要

### 探索1: Python数値実験 (scripts/erdos20_sunflower.py)
- f(n,3) の計算: f(1,3)=3, f(2,3)=7, f(3,3)=15, f(4,3)=27, f(5,3)=49
- f(n,3)^(1/n) は 3.0, 2.65, 2.47, 2.28, 2.18 と減少傾向
  → 最適定数 c_3 ≈ 2 程度と推定
- Erdős-Rado上界は大幅に緩い（n=5で3841 vs 実測49）
- ランダム集合族で n=2, m=5 でほぼ確実にひまわり出現

### 探索2: ひまわりフリー集合族の構造
- n=2: 最大サイズ6、2つの三角形に分離する構造
- n=3: 最大サイズ14、要素頻度が均等に近い
- 共通部分サイズが分散、包含関係なし
- 「均等に広がる」構造がひまわり回避に有利

### 探索3: Lean形式化（本ファイル）
- ひまわりの定義
- 小さいケースの検証
- 自明な補題
-/

/-! ## 基本定義 -/

/-- ひまわりの定義: 集合のリストがひまわりであるとは、
    あるcore Yが存在して、各集合 S_i に対して core ⊆ S_i
    かつ花びら S_i \ core が互いに素であること -/
def IsSunflower {α : Type*} [DecidableEq α] (family : List (Finset α)) : Prop :=
  ∃ core : Finset α,
    (∀ S ∈ family, core ⊆ S) ∧
    (∀ (i j : ℕ) (hi : i < family.length) (hj : j < family.length),
      i ≠ j →
      (family[i] \ core) ∩ (family[j] \ core) = ∅)

/-- n-均一集合族: 全ての集合のサイズが n -/
def IsUniform {α : Type*} (n : ℕ) (family : List (Finset α)) : Prop :=
  ∀ S ∈ family, S.card = n

/-- 集合族がk-ひまわりを含む: k個の集合からなる部分族がひまわり -/
def ContainsSunflower {α : Type*} [DecidableEq α]
    (family : List (Finset α)) (k : ℕ) : Prop :=
  ∃ subfamily : List (Finset α),
    subfamily.length = k ∧
    (∀ S ∈ subfamily, S ∈ family) ∧
    IsSunflower subfamily

/-- ひまわり予想の形式的記述:
    任意の k ≥ 2 に対して、ある定数 c_k が存在して、
    任意の n-均一集合族のサイズが c_k^n を超えるなら
    k-ひまわりを含む -/
def SunflowerConjecture : Prop :=
  ∀ k : ℕ, k ≥ 2 →
  ∃ c : ℝ, c > 0 ∧
    ∀ (n : ℕ) (α : Type) [DecidableEq α] [Fintype α]
      (family : List (Finset α)),
      IsUniform n family →
      (family.length : ℝ) > c ^ n →
      ContainsSunflower family k

/-! ## 小さいケースの検証 -/

/-- 空集合のみからなる3つのリストはひまわり（coreは空集合） -/
theorem sunflower_empty_sets :
    IsSunflower [(∅ : Finset ℕ), ∅, ∅] := by
  refine ⟨∅, ?_, ?_⟩
  · intro S hS
    simp [List.mem_cons] at hS
    rcases hS with rfl | rfl | rfl <;> exact Finset.empty_subset _
  · intro i j hi hj _
    simp only [Finset.sdiff_empty]
    have hi' : i < 3 := hi
    have hj' : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all

/-- 互いに素な3集合はひまわり（coreは空集合） -/
theorem sunflower_disjoint_three :
    IsSunflower [({0, 1} : Finset ℕ), {2, 3}, {4, 5}] := by
  refine ⟨∅, ?_, ?_⟩
  · intro S hS
    simp [List.mem_cons] at hS
    rcases hS with rfl | rfl | rfl <;> exact Finset.empty_subset _
  · intro i j hi hj hij
    simp only [Finset.sdiff_empty]
    have hi' : i < 3 := hi
    have hj' : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;> decide

/-- 共通要素を持つ3集合のひまわり（coreは{0}） -/
theorem sunflower_with_core :
    IsSunflower [({0, 1} : Finset ℕ), {0, 2}, {0, 3}] := by
  refine ⟨{0}, ?_, ?_⟩
  · intro S hS
    simp [List.mem_cons] at hS
    rcases hS with rfl | rfl | rfl <;> simp [Finset.subset_iff] <;> omega
  · intro i j hi hj hij
    have hi' : i < 3 := hi
    have hj' : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;> decide

/-! ## 自明な補題 -/

/-- n-均一集合族で重複なしなら、族のサイズが台集合のn-元部分集合の数以下 -/
theorem uniform_family_size_bound {α : Type*} [Fintype α]
    (family : List (Finset α)) (hnodup : family.Nodup)
    (hunif : IsUniform n family) :
    family.length ≤ (Fintype.card α).choose n := by
  classical
  have hsub : family.toFinset ⊆ Finset.univ.powersetCard n := by
    intro S hS
    rw [Finset.mem_powersetCard]
    exact ⟨Finset.subset_univ S, hunif S (List.mem_toFinset.mp hS)⟩
  have hlen : family.toFinset.card ≤ (Finset.univ.powersetCard n).card :=
    Finset.card_le_card hsub
  rw [List.toFinset_card_of_nodup hnodup] at hlen
  simpa [Finset.card_powersetCard] using hlen

/-- 1-均一集合族で重複なしなら、サイズは台集合のサイズ以下（鳩の巣原理） -/
theorem uniform1_family_bound {α : Type*} [Fintype α]
    (family : List (Finset α))
    (hnodup : family.Nodup)
    (hunif : IsUniform 1 family) :
    family.length ≤ Fintype.card α := by
  have h := uniform_family_size_bound family hnodup hunif
  simp [Nat.choose_one_right] at h
  exact h

/-! ## 探索6: f(1,k) = k — 1-均一族のひまわり定理

1-均一族（各集合がシングルトン）で重複なし・k個あるなら、それ自体が
k-ひまわり（coreは空集合、花びらは互いに素なシングルトン）。

証明方針:
- core = ∅ とする
- ∅ ⊆ S は自明
- 花びらの互いに素性: S_i \ ∅ = S_i, S_j \ ∅ = S_j で、
  |S_i|=|S_j|=1 かつ S_i ≠ S_j なのでサイズ1の異なるFinsetは disjoint
-/

/-- サイズ1の異なるFinsetは互いに素 -/
theorem disjoint_of_card_one_ne {α : Type*} [DecidableEq α]
    {s t : Finset α} (hs : s.card = 1) (ht : t.card = 1) (hne : s ≠ t) :
    s ∩ t = ∅ := by
  rw [Finset.card_eq_one] at hs ht
  obtain ⟨a, rfl⟩ := hs
  obtain ⟨b, rfl⟩ := ht
  have hab : a ≠ b := by
    intro h; exact hne (congrArg _ h)
  have hba : b ≠ a := Ne.symm hab
  have : b ∉ ({a} : Finset α) := by simp [hba]
  rw [Finset.inter_singleton_of_notMem this]

/-- 1-均一族の k 個の異なるシングルトンは k-ひまわり -/
theorem sunflower_uniform1_singletons {α : Type*} [DecidableEq α]
    (family : List (Finset α))
    (hunif : IsUniform 1 family)
    (hnodup : family.Nodup) :
    IsSunflower family := by
  refine ⟨∅, ?_, ?_⟩
  · intro S _; exact Finset.empty_subset S
  · intro i j hi hj hij
    simp only [Finset.sdiff_empty]
    have hsi := hunif (family[i]) (List.getElem_mem hi)
    have hsj := hunif (family[j]) (List.getElem_mem hj)
    have hne : family[i] ≠ family[j] := by
      intro h
      exact absurd (hnodup.getElem_inj_iff.mp h) hij
    exact disjoint_of_card_one_ne hsi hsj hne

/-! ## 探索7: Erdős-Rado 上界 (n=1) の形式化

空族・単一集合族がひまわりであることの自明な事実。
これは Erdős-Rado 定理 f(n,k) ≤ (k-1)^n · n! + 1 の n=1 の場合、
すなわち f(1,k) ≤ k の検証に向けた基礎補題である。
-/

/-- 空族はひまわり（自明） -/
theorem isSunflower_nil {α : Type*} [DecidableEq α] :
    IsSunflower ([] : List (Finset α)) := by
  refine ⟨∅, ?_, ?_⟩
  · intro S hS; simp at hS
  · intro i j hi; exact absurd hi (Nat.not_lt_zero i)

/-- 単一集合はひまわり -/
theorem isSunflower_singleton {α : Type*} [DecidableEq α] (S : Finset α) :
    IsSunflower [S] := by
  refine ⟨S, ?_, ?_⟩
  · intro T hT; simp at hT; rw [hT]
  · intro i j hi hj hij
    have : i < 1 := hi
    have : j < 1 := hj
    omega

/-! ## 探索8: 2集合族のひまわり性

任意の2つの集合 S, T からなる族 [S, T] は必ずひまわりである。
core = S ∩ T とすれば、花びら S \ (S∩T) と T \ (S∩T) は互いに素。
これは IsSunflower の定義に対する基本的な検証。
-/

/-- 2つの集合からなる族は必ずひまわり（core = 共通部分） -/
theorem isSunflower_pair {α : Type*} [DecidableEq α] (S T : Finset α) :
    IsSunflower [S, T] := by
  refine ⟨S ∩ T, ?_, ?_⟩
  · intro U hU
    simp at hU
    rcases hU with rfl | rfl
    · exact Finset.inter_subset_left
    · exact Finset.inter_subset_right
  · intro i j hi hj hij
    have hi' : i < 2 := hi
    have hj' : j < 2 := hj
    have h01 : (S \ (S ∩ T)) ∩ (T \ (S ∩ T)) = ∅ := by
      ext x; simp only [Finset.mem_sdiff, Finset.mem_inter]
      constructor
      · rintro ⟨⟨hS, hnST⟩, hT, _⟩; exact absurd ⟨hS, hT⟩ hnST
      · tauto
    have h10 : (T \ (S ∩ T)) ∩ (S \ (S ∩ T)) = ∅ := by
      ext x; simp only [Finset.mem_sdiff, Finset.mem_inter]
      constructor
      · rintro ⟨⟨hT, hnST⟩, hS, _⟩; exact absurd ⟨hS, hT⟩ hnST
      · tauto
    interval_cases i <;> interval_cases j <;> simp_all

/-! ## 探索9: ひまわりの長さに関する単調性 -/

/-- 4つの空集合はひまわり -/
theorem sunflower_four_empty :
    IsSunflower [(∅ : Finset ℕ), ∅, ∅, ∅] := by
  refine ⟨∅, ?_, ?_⟩
  · intro S hS; exact Finset.empty_subset S
  · intro i j hi hj _
    simp only [Finset.sdiff_empty]
    have : i < 4 := hi; have : j < 4 := hj
    interval_cases i <;> interval_cases j <;> simp_all

/-! ## 探索10: ContainsSunflower の自明なケース -/

/-- 任意の族は 0-ひまわりを含む（空の部分族） -/
theorem containsSunflower_zero {α : Type*} [DecidableEq α]
    (family : List (Finset α)) : ContainsSunflower family 0 := by
  refine ⟨[], rfl, ?_, isSunflower_nil⟩
  intro S hS; simp at hS

/-- 任意の非空族は 1-ひまわりを含む -/
theorem containsSunflower_one {α : Type*} [DecidableEq α]
    (family : List (Finset α)) (hne : family ≠ []) :
    ContainsSunflower family 1 := by
  match family, hne with
  | S :: _, _ =>
    refine ⟨[S], rfl, ?_, isSunflower_singleton S⟩
    intro T hT; simp at hT; rw [hT]; simp

/-! ## 探索11: ひまわりの具体例（共通coreが非空） -/

/-- {1,2,3}, {1,4,5}, {1,6,7} はひまわり（core = {1}） -/
theorem sunflower_core1 :
    IsSunflower [({1, 2, 3} : Finset ℕ), {1, 4, 5}, {1, 6, 7}] := by
  refine ⟨{1}, ?_, ?_⟩
  · intro S hS
    simp at hS
    rcases hS with rfl | rfl | rfl <;> simp [Finset.subset_iff] <;> omega
  · intro i j hi hj hij
    have : i < 3 := hi; have : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;> decide

/-! ## 探索12: 2-均一族のひまわり検証 -/

/-- {1,5}, {2,6}, {3,7} は互いに素なので3-ひまわり（core=空） -/
theorem sunflower_disjoint_156 :
    IsSunflower [({1, 5} : Finset ℕ), {2, 6}, {3, 7}] := by
  refine ⟨∅, ?_, ?_⟩
  · intro S hS; exact Finset.empty_subset S
  · intro i j hi hj hij
    simp only [Finset.sdiff_empty]
    have : i < 3 := hi; have : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;> decide

/-! ## 探索13: ひまわりの core サイズの性質 -/

-- ひまわりのcore が空でなく族が2以上なら、各集合はcoreを含む非空集合
-- （IsSunflower の定義の系）

/-- 2つの同一集合のリストはひまわり -/
theorem isSunflower_repeat {α : Type*} [DecidableEq α] (S : Finset α) :
    IsSunflower [S, S] := by
  exact isSunflower_pair S S

/-! ## 探索15: 3-均一族のひまわり -/

-- {1,2,3}, {1,2,4}, {1,2,5} はひまわり（core={1,2}）
theorem sunflower_core12 :
    IsSunflower [({1, 2, 3} : Finset ℕ), {1, 2, 4}, {1, 2, 5}] := by
  refine ⟨{1, 2}, ?_, ?_⟩
  · intro S hS; simp at hS; rcases hS with rfl | rfl | rfl <;> simp [Finset.subset_iff] <;> omega
  · intro i j hi hj hij
    have : i < 3 := hi; have : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;> decide

/-! ## Erdős-Rado 上界 (n=1) の一般化

1-均一族（各集合がシングルトン）で重複なし・k個以上あるなら、
k-ひまわりを含む。先頭 k 個を取れば、それ自体が k-ひまわりとなる。

証明: sunflower_uniform1_singletons を部分リスト family.take k に適用する。
-/

/-- 1-均一族でサイズ ≥ k なら k-ひまわりを含む（Erdős-Rado n=1 ケース） -/
theorem erdosRado_uniform1 {α : Type*} [DecidableEq α]
    (family : List (Finset α)) (hunif : IsUniform 1 family) (hnodup : family.Nodup)
    (hlen : family.length ≥ k) : ContainsSunflower family k := by
  refine ⟨family.take k, ?_, ?_, ?_⟩
  · -- length
    exact List.length_take_of_le (by omega)
  · -- membership
    intro S hS
    exact List.mem_of_mem_take hS
  · -- sunflower
    apply sunflower_uniform1_singletons
    · -- IsUniform 1
      intro S hS
      exact hunif S (List.mem_of_mem_take hS)
    · -- Nodup
      exact List.Nodup.sublist (List.take_sublist k family) hnodup

-- =============================================================================
-- 互いに素な集合族のひまわり性
-- =============================================================================

/-! ## 互いに素な集合族は自動的にひまわり

k 個の互いに素な集合からなる族は、core = ∅ のひまわりである。
各集合 S_i \ ∅ = S_i で、仮定から互いに素。
-/

/-- 互いに素な k 個の集合はひまわり（core = 空集合） -/
theorem isSunflower_of_pairwise_disjoint {α : Type*} [DecidableEq α]
    (family : List (Finset α))
    (hdisjoint : ∀ (i j : ℕ) (hi : i < family.length) (hj : j < family.length),
      i ≠ j → family[i] ∩ family[j] = ∅) :
    IsSunflower family := by
  refine ⟨∅, ?_, ?_⟩
  · intro S _; exact Finset.empty_subset S
  · intro i j hi hj hij
    simp only [Finset.sdiff_empty]
    exact hdisjoint i j hi hj hij

-- =============================================================================
-- Erdős-Rado 上界 (n=2, k=3): 9個以上の異なる2元集合の族は3-ひまわりを含む
-- =============================================================================

/-! ## Erdős-Rado n=2, k=3

f(2,3) ≤ (3-1)^2 · 2! + 1 = 9 の証明。
9個以上の異なる2元集合の族は必ず3-ひまわりを含む。

### 証明戦略
- Case 1: ある要素が3個以上の集合に含まれる → core = {x} のスターひまわり
- Case 2: 全要素が高々2個の集合にしか含まれない → 貪欲法で3つの互いに素な集合を選ぶ

ここでは、まず Case 1 に対応するスター補題を証明し、
次に具体例として9個の2元集合族での3-ひまわり存在を示す。
-/

section ErdosRadoN2K3

/-! ### 補題: 共通要素を持つ3つの異なる2元集合はひまわり -/

/-- x ∈ S かつ S.card = 2 のとき、(S \ {x}).card = 1 -/
private theorem card_sdiff_singleton_of_mem_card_two {α : Type*} [DecidableEq α]
    {S : Finset α} {x : α} (hx : x ∈ S) (hc : S.card = 2) :
    (S \ {x}).card = 1 := by
  have hsub : {x} ⊆ S := Finset.singleton_subset_iff.mpr hx
  rw [Finset.card_sdiff_of_subset hsub, hc, Finset.card_singleton]

/-- S₁ ≠ S₂ で x ∈ S₁ ∩ S₂ かつ card = 2 なら花びら S₁ \ {x} ≠ S₂ \ {x} -/
private theorem petal_ne_of_ne {α : Type*} [DecidableEq α]
    {S₁ S₂ : Finset α} {x : α}
    (hx1 : x ∈ S₁) (hx2 : x ∈ S₂)
    (_hc1 : S₁.card = 2) (_hc2 : S₂.card = 2)
    (hne : S₁ ≠ S₂) :
    S₁ \ {x} ≠ S₂ \ {x} := by
  intro h
  apply hne
  ext y
  by_cases hyx : y = x
  · subst hyx; exact ⟨fun _ => hx2, fun _ => hx1⟩
  · constructor
    · intro hy
      have : y ∈ S₁ \ {x} := by
        simp only [Finset.mem_sdiff, Finset.mem_singleton]; exact ⟨hy, hyx⟩
      rw [h] at this
      exact (Finset.mem_sdiff.mp this).1
    · intro hy
      have : y ∈ S₂ \ {x} := by
        simp only [Finset.mem_sdiff, Finset.mem_singleton]; exact ⟨hy, hyx⟩
      rw [← h] at this
      exact (Finset.mem_sdiff.mp this).1

/-- 共通要素を持つ3つの異なる2元集合はひまわり（一般版）

    x を含む3つの異なるサイズ2の Finset は 3-ひまわり。
    core = {x}, 花びらは {aᵢ} で互いに素。-/
theorem sunflower_star_general {α : Type*} [DecidableEq α]
    (S₁ S₂ S₃ : Finset α) (x : α)
    (hmem1 : x ∈ S₁) (hmem2 : x ∈ S₂) (hmem3 : x ∈ S₃)
    (hcard1 : S₁.card = 2) (hcard2 : S₂.card = 2) (hcard3 : S₃.card = 2)
    (hne12 : S₁ ≠ S₂) (hne13 : S₁ ≠ S₃) (hne23 : S₂ ≠ S₃) :
    IsSunflower [S₁, S₂, S₃] := by
  refine ⟨{x}, ?_, ?_⟩
  · -- core ⊆ S_i
    intro S hS
    simp only [List.mem_cons, List.mem_nil_iff, or_false] at hS
    rcases hS with rfl | rfl | rfl <;> exact Finset.singleton_subset_iff.mpr ‹_›
  · -- 花びらの互いに素性
    -- 花びら S_i \ {x} はサイズ1で、異なる集合の花びらは異なる
    -- サイズ1の異なる Finset は互いに素（disjoint_of_card_one_ne）
    have hpc1 := card_sdiff_singleton_of_mem_card_two hmem1 hcard1
    have hpc2 := card_sdiff_singleton_of_mem_card_two hmem2 hcard2
    have hpc3 := card_sdiff_singleton_of_mem_card_two hmem3 hcard3
    have hpne12 := petal_ne_of_ne hmem1 hmem2 hcard1 hcard2 hne12
    have hpne13 := petal_ne_of_ne hmem1 hmem3 hcard1 hcard3 hne13
    have hpne23 := petal_ne_of_ne hmem2 hmem3 hcard2 hcard3 hne23
    have hpne21 : S₂ \ {x} ≠ S₁ \ {x} := Ne.symm hpne12
    have hpne31 : S₃ \ {x} ≠ S₁ \ {x} := Ne.symm hpne13
    have hpne32 : S₃ \ {x} ≠ S₂ \ {x} := Ne.symm hpne23
    intro i j hi hj hij
    have hi3 : i < 3 := hi
    have hj3 : j < 3 := hj
    interval_cases i <;> interval_cases j <;> simp_all <;>
      exact disjoint_of_card_one_ne ‹_› ‹_› ‹_›

/-- 2-均一族で、ある要素が3つ以上の集合に含まれるなら、3-ひまわりを含む -/
theorem containsSunflower3_of_element_appears_thrice {α : Type*} [DecidableEq α]
    (family : List (Finset α))
    (hunif : IsUniform 2 family) (hnodup : family.Nodup) (x : α)
    (hcount : (family.filter (fun S => x ∈ S)).length ≥ 3) :
    ContainsSunflower family 3 := by
  -- x を含む集合を3つ取り出す
  set fx := family.filter (fun S => x ∈ S) with hfx_def
  -- fx.length ≥ 3 なので先頭3つを取れる
  have hfx3 : fx.length ≥ 3 := hcount
  have h0 : 0 < fx.length := by omega
  have h1 : 1 < fx.length := by omega
  have h2 : 2 < fx.length := by omega
  set S₁ := fx[0] with hS1_def
  set S₂ := fx[1] with hS2_def
  set S₃ := fx[2] with hS3_def
  -- S_i ∈ family
  have hS1_in_fx : S₁ ∈ fx := List.getElem_mem h0
  have hS2_in_fx : S₂ ∈ fx := List.getElem_mem h1
  have hS3_in_fx : S₃ ∈ fx := List.getElem_mem h2
  have hS1_mem : S₁ ∈ family := List.mem_of_mem_filter hS1_in_fx
  have hS2_mem : S₂ ∈ family := List.mem_of_mem_filter hS2_in_fx
  have hS3_mem : S₃ ∈ family := List.mem_of_mem_filter hS3_in_fx
  -- x ∈ S_i (filter condition gives decidability witness)
  have hx1 : x ∈ S₁ := by
    have := (List.mem_filter.mp hS1_in_fx).2; simpa using this
  have hx2 : x ∈ S₂ := by
    have := (List.mem_filter.mp hS2_in_fx).2; simpa using this
  have hx3 : x ∈ S₃ := by
    have := (List.mem_filter.mp hS3_in_fx).2; simpa using this
  -- S_i.card = 2
  have hc1 : S₁.card = 2 := hunif S₁ hS1_mem
  have hc2 : S₂.card = 2 := hunif S₂ hS2_mem
  have hc3 : S₃.card = 2 := hunif S₃ hS3_mem
  -- S_i は互いに異なる（fx は family の部分リストで Nodup）
  have hfx_nodup : fx.Nodup := List.Nodup.filter _ hnodup
  have hne12 : S₁ ≠ S₂ := by
    intro h; exact absurd (hfx_nodup.getElem_inj_iff.mp h) (by omega)
  have hne13 : S₁ ≠ S₃ := by
    intro h; exact absurd (hfx_nodup.getElem_inj_iff.mp h) (by omega)
  have hne23 : S₂ ≠ S₃ := by
    intro h; exact absurd (hfx_nodup.getElem_inj_iff.mp h) (by omega)
  -- [S₁, S₂, S₃] はひまわり
  have hsf := sunflower_star_general S₁ S₂ S₃ x
    hx1 hx2 hx3 hc1 hc2 hc3 hne12 hne13 hne23
  refine ⟨[S₁, S₂, S₃], rfl, ?_, hsf⟩
  intro S hS
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hS
  rcases hS with rfl | rfl | rfl
  · exact hS1_mem
  · exact hS2_mem
  · exact hS3_mem

/-! ### Erdős-Rado n=2, k=3 の完全な定理（今後の課題）

完全な証明には Case 2（全要素の出現回数 ≤ 2 の場合に貪欲法で
3つの互いに素な集合を見つける）が必要。これは:
1. 各2元集合 S = {a,b} と交わる集合が高々3個であること（包除原理 + Nodup）
2. 9 - 3 = 6, 6 - 3 = 3, 3 ≥ 1 から3回の貪欲選択が可能
3. 選ばれた3集合が互いに素であること

の形式化が必要で、List ベースの操作が煩雑になるため、
ここでは Case 1（スター補題）の完全証明に留める。

### 定理の記述（証明は将来の探索に委ねる）
-/

end ErdosRadoN2K3

-- =============================================================================
-- Case 2 に向けた補題群
-- =============================================================================

/-! ## 出現頻度と互いに素性

2-均一族で全要素の出現回数が1以下なら、全集合が互いに素であることを示す。
また、出現回数 ≤ 2 の場合に各集合と交わる他の集合が高々2個であることも示す。
-/

section FrequencyLemmas

variable {α : Type*} [DecidableEq α]

/-- 2つの集合に共通要素が存在するなら、その要素は少なくとも2つの集合に出現する -/
private theorem freq_ge_two_of_common_element
    (family : List (Finset α)) (hnodup : family.Nodup)
    (i j : ℕ) (hi : i < family.length) (hj : j < family.length) (hij : i ≠ j)
    (x : α) (hxi : x ∈ family[i]) (hxj : x ∈ family[j]) :
    (family.filter (fun S => x ∈ S)).length ≥ 2 := by
  set fx := family.filter (fun S => x ∈ S)
  have hSi_in_fx : family[i] ∈ fx := by
    simp only [fx, List.mem_filter]
    exact ⟨List.getElem_mem hi, by simpa using hxi⟩
  have hSj_in_fx : family[j] ∈ fx := by
    simp only [fx, List.mem_filter]
    exact ⟨List.getElem_mem hj, by simpa using hxj⟩
  have hne : family[i] ≠ family[j] := by
    intro h; exact absurd (hnodup.getElem_inj_iff.mp h) hij
  have hfx_nodup : fx.Nodup := List.Nodup.filter _ hnodup
  -- Use toFinset to count distinct elements
  have hcard : fx.toFinset.card ≥ 2 := by
    have hi_in : family[i] ∈ fx.toFinset := List.mem_toFinset.mpr hSi_in_fx
    have hj_in : family[j] ∈ fx.toFinset := List.mem_toFinset.mpr hSj_in_fx
    have : ({family[i], family[j]} : Finset (Finset α)) ⊆ fx.toFinset := by
      intro S hS
      simp only [Finset.mem_insert, Finset.mem_singleton] at hS
      rcases hS with rfl | rfl
      · exact hi_in
      · exact hj_in
    calc 2 = ({family[i], family[j]} : Finset (Finset α)).card := by
            rw [Finset.card_pair hne]
      _ ≤ fx.toFinset.card := Finset.card_le_card this
  rwa [List.toFinset_card_of_nodup hfx_nodup] at hcard

/-- 全要素の出現回数が1以下のとき、任意の2つの異なる集合は互いに素 -/
theorem pairwise_disjoint_of_freq_le_one
    (family : List (Finset α))
    (hnodup : family.Nodup)
    (hfreq : ∀ x : α, (family.filter (fun S => x ∈ S)).length ≤ 1) :
    ∀ (i j : ℕ) (hi : i < family.length) (hj : j < family.length),
      i ≠ j → family[i] ∩ family[j] = ∅ := by
  intro i j hi hj hij
  by_contra h
  have hne : (family[i] ∩ family[j]).Nonempty := by
    rwa [Finset.nonempty_iff_ne_empty]
  obtain ⟨x, hx⟩ := hne
  rw [Finset.mem_inter] at hx
  have hge2 := freq_ge_two_of_common_element family hnodup i j hi hj hij x hx.1 hx.2
  have hle1 := hfreq x
  omega

/-- 全要素の出現回数が1以下の3個以上の集合族は、3つの互いに素な集合を含み、
    したがって3-ひまわりを含む -/
theorem containsSunflower3_of_freq_le_one
    (family : List (Finset α))
    (hnodup : family.Nodup)
    (hfreq : ∀ x : α, (family.filter (fun S => x ∈ S)).length ≤ 1)
    (hlen : family.length ≥ 3) :
    ContainsSunflower family 3 := by
  set sub := family.take 3 with hsub_def
  have hsub_len : sub.length = 3 := List.length_take_of_le (by omega)
  have hsub_nodup : sub.Nodup := List.Nodup.sublist (List.take_sublist 3 family) hnodup
  have hsub_mem : ∀ S ∈ sub, S ∈ family := fun S hS => List.mem_of_mem_take hS
  -- sub has pairwise disjoint elements
  have hdisjoint : ∀ (i j : ℕ) (hi : i < sub.length) (hj : j < sub.length),
      i ≠ j → sub[i] ∩ sub[j] = ∅ := by
    intro i j hi hj hij
    have htake_le : sub.length ≤ family.length := by
      simp [hsub_def, List.length_take]
    have hi' : i < family.length := by omega
    have hj' : j < family.length := by omega
    rw [List.getElem_take, List.getElem_take]
    exact pairwise_disjoint_of_freq_le_one family hnodup hfreq i j hi' hj' hij
  refine ⟨sub, hsub_len, hsub_mem, isSunflower_of_pairwise_disjoint sub hdisjoint⟩

end FrequencyLemmas

-- =============================================================================
-- スター補題の k 一般化
-- =============================================================================

/-! ## スター補題の一般化

2-均一族で要素 x が k 回以上出現するなら k-ひまわりを含む。
k=3 の `containsSunflower3_of_element_appears_thrice` の一般化。

証明方針:
- x を含む集合を k 個取り出す（先頭 k 個）
- core = {x} で、花びら S_i \ {x} はサイズ1
- 異なる2元集合の花びらは異なるサイズ1集合 → 互いに素
-/

section StarGeneralization

variable {α : Type*} [DecidableEq α]

/-- x を含む異なる2元集合のリストは {x} を core とするひまわり -/
private theorem isSunflower_star_uniform2
    (family : List (Finset α)) (x : α)
    (hunif : ∀ S ∈ family, S.card = 2)
    (hmem : ∀ S ∈ family, x ∈ S)
    (hnodup : family.Nodup) :
    IsSunflower family := by
  refine ⟨{x}, ?_, ?_⟩
  · intro S hS
    exact Finset.singleton_subset_iff.mpr (hmem S hS)
  · intro i j hi hj hij
    have hci := hunif _ (List.getElem_mem hi)
    have hcj := hunif _ (List.getElem_mem hj)
    have hne : family[i] ≠ family[j] := by
      intro h; exact absurd (hnodup.getElem_inj_iff.mp h) hij
    have hpi := card_sdiff_singleton_of_mem_card_two (hmem _ (List.getElem_mem hi)) hci
    have hpj := card_sdiff_singleton_of_mem_card_two (hmem _ (List.getElem_mem hj)) hcj
    have hpne := petal_ne_of_ne (hmem _ (List.getElem_mem hi)) (hmem _ (List.getElem_mem hj))
      hci hcj hne
    exact disjoint_of_card_one_ne hpi hpj hpne

/-- 2-均一族で要素 x が k 回以上出現するなら k-ひまわりを含む -/
theorem containsSunflower_of_element_appears_k
    (family : List (Finset α)) (k : ℕ)
    (hunif : IsUniform 2 family) (hnodup : family.Nodup)
    (x : α) (hfreq : (family.filter (fun S => x ∈ S)).length ≥ k) :
    ContainsSunflower family k := by
  set fx := family.filter (fun S => x ∈ S) with hfx_def
  set sub := fx.take k with hsub_def
  have hsub_len : sub.length = k := List.length_take_of_le (by omega)
  -- sub の各要素は family のメンバー
  have hsub_mem_family : ∀ S ∈ sub, S ∈ family := by
    intro S hS
    exact List.mem_of_mem_filter (List.mem_of_mem_take hS)
  -- sub の各要素は x を含む
  have hsub_has_x : ∀ S ∈ sub, x ∈ S := by
    intro S hS
    have hS_fx : S ∈ fx := List.mem_of_mem_take hS
    have := (List.mem_filter.mp hS_fx).2
    simpa using this
  -- sub の各要素は 2元集合
  have hsub_unif : ∀ S ∈ sub, S.card = 2 := by
    intro S hS; exact hunif S (hsub_mem_family S hS)
  -- sub は Nodup
  have hfx_nodup : fx.Nodup := List.Nodup.filter _ hnodup
  have hsub_nodup : sub.Nodup := List.Nodup.sublist (List.take_sublist k fx) hfx_nodup
  -- sub はひまわり
  have hsf := isSunflower_star_uniform2 sub x hsub_unif hsub_has_x hsub_nodup
  exact ⟨sub, hsub_len, hsub_mem_family, hsf⟩

end StarGeneralization

/-! ## family が空なら ContainsSunflower は k = 0 のときのみ -/

/-- family が空なら ContainsSunflower family k は k = 0 のときのみ -/
theorem containsSunflower_nil_iff {α : Type*} [DecidableEq α] {k : ℕ} :
    ContainsSunflower ([] : List (Finset α)) k ↔ k = 0 := by
  constructor
  · intro ⟨sub, hlen, hmem, _⟩
    by_contra hk
    have hk_pos : k > 0 := by omega
    have hlen_pos : sub.length > 0 := by omega
    have ⟨S, hS⟩ := List.exists_mem_of_length_pos hlen_pos
    have := hmem S hS
    simp at this
  · intro h; subst h; exact containsSunflower_zero []

/-- ContainsSunflower family k かつ k ≥ 1 → family は非空 -/
theorem family_nonempty_of_containsSunflower {α : Type*} [DecidableEq α]
    {family : List (Finset α)} {k : ℕ} (hk : k ≥ 1)
    (h : ContainsSunflower family k) : family ≠ [] := by
  obtain ⟨sub, hlen, hmem, _⟩ := h
  intro he; rw [he] at hmem
  have hsub_ne : sub ≠ [] := by
    intro hsub_e; rw [hsub_e] at hlen; simp at hlen; omega
  obtain ⟨S, hS⟩ := List.exists_mem_of_ne_nil sub hsub_ne
  have := hmem S hS
  simp at this
