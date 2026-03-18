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
