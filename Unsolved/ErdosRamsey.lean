import Mathlib

set_option linter.style.longLine false
set_option linter.flexible false

/-!
# エルデシュ問題 #77: Ramsey Number Limit (ラムゼー数の極限)

lim_{k→∞} R(k)^{1/k} を求めよ。

R(k) はラムゼー数: 完全グラフ K_n の辺を2色で塗り分けたとき、
必ず単色の完全部分グラフ K_k が現れる最小の n。

## 既知の結果
- √2 ≤ liminf R(k)^{1/k} ≤ limsup R(k)^{1/k} ≤ 4 - ε
- Erdős-Szekeres (1935): R(k) ≤ C(2k-2, k-1) → 上界 4
- Erdős (1947): R(k) ≥ 2^{k/2} → 下界 √2
- Campos-Griffiths-Morris-Sahasrabudhe (2023): R(k) ≤ (4-ε)^k
- Gupta-Ndiaye-Norin-Wei: ε ≥ 0.2008 → ≤ 3.7992^k

## 探索1-2: Python数値実験と構造解析 (scripts/erdos77_ramsey.py)
- R(3)=6, R(4)=18 を全探索で検証
- K_5 での単色K_3回避塗り分けは12通り、全て次数列(2,2,2,2,2) = C_5型
- Paley(17) のクリーク数=独立数=3 を確認、R(4)≥18 の証拠

## 探索3: Lean形式化
- 完全グラフの2色塗り分けの定義
- 単色クリークの定義
- R(3) ≥ 6: K_5 上で単色K_3を回避するC_5塗り分けの構成
-/

-- =============================================================================
-- 基本定義
-- =============================================================================

/-- 完全グラフの辺の2色塗り分け。
    Fin n の頂点集合上で、各辺 {i,j} (i ≠ j) に色 (Bool) を割り当てる。
    対称性: coloring i j = coloring j i を要求。 -/
structure TwoColoring (n : ℕ) where
  color : Fin n → Fin n → Bool
  symm : ∀ i j : Fin n, color i j = color j i

/-- 頂点集合 S ⊆ Fin n が与えられた着色で「単色クリーク」であること。
    S 内の任意の2頂点を結ぶ辺が全て同じ色 c を持つ。 -/
def IsMonochromaticClique {n : ℕ} (col : TwoColoring n) (S : Finset (Fin n))
    (c : Bool) : Prop :=
  ∀ i ∈ S, ∀ j ∈ S, i ≠ j → col.color i j = c

/-- ラムゼー数の定義に対応する性質:
    K_n の任意の2色塗り分けに、サイズ k の単色クリークが存在する。 -/
def HasRamseyProperty (n k : ℕ) : Prop :=
  ∀ col : TwoColoring n,
    ∃ S : Finset (Fin n), S.card = k ∧
      (IsMonochromaticClique col S true ∨ IsMonochromaticClique col S false)

/-- ラムゼー数 R(k) の特徴付け:
    HasRamseyProperty n k が成り立つ最小の n -/
def IsRamseyNumber (k R : ℕ) : Prop :=
  HasRamseyProperty R k ∧ ¬HasRamseyProperty (R - 1) k

-- =============================================================================
-- R(3) ≥ 6 の部分検証: K_5 上で単色K_3を回避する塗り分けの構成
-- =============================================================================

/-- C_5の隣接関数: 距離1か4 (mod 5) なら true
    C_5 の辺: 0-1, 1-2, 2-3, 3-4, 4-0
    補グラフ: 0-2, 0-3, 1-3, 1-4, 2-4 (これも C_5) -/
def c5Adjacent (i j : Fin 5) : Bool :=
  let d := ((i.val + 5 - j.val) % 5)
  d == 1 || d == 4

/-- C_5の隣接関数は対称 -/
theorem c5Adjacent_symm (i j : Fin 5) : c5Adjacent i j = c5Adjacent j i := by
  fin_cases i <;> fin_cases j <;> decide

def c5Coloring : TwoColoring 5 where
  color := c5Adjacent
  symm := c5Adjacent_symm

-- =============================================================================
-- R(2) = 2 の検証
-- =============================================================================

/-- R(2) = 2: 任意の2色塗り分けで、辺(=2頂点)は必ずどちらかの色 -/
theorem ramsey_2_holds : HasRamseyProperty 2 2 := by
  intro col
  -- 2頂点 0, 1 の辺の色で場合分け
  by_cases h : col.color ⟨0, by omega⟩ ⟨1, by omega⟩ = true
  · -- 色が true の場合
    exact ⟨{⟨0, by omega⟩, ⟨1, by omega⟩}, by simp, Or.inl (by
      intro i hi j hj hij
      simp [Finset.mem_insert, Finset.mem_singleton] at hi hj
      rcases hi with rfl | rfl <;> rcases hj with rfl | rfl
      · exact absurd rfl hij
      · exact h
      · rw [col.symm]; exact h
      · exact absurd rfl hij)⟩
  · -- 色が false の場合
    have h' : col.color ⟨0, by omega⟩ ⟨1, by omega⟩ = false := by
      cases hc : col.color ⟨0, by omega⟩ ⟨1, by omega⟩ <;> simp_all
    exact ⟨{⟨0, by omega⟩, ⟨1, by omega⟩}, by simp, Or.inr (by
      intro i hi j hj hij
      simp [Finset.mem_insert, Finset.mem_singleton] at hi hj
      rcases hi with rfl | rfl <;> rcases hj with rfl | rfl
      · exact absurd rfl hij
      · exact h'
      · rw [col.symm]; exact h'
      · exact absurd rfl hij)⟩

-- =============================================================================
-- 既知のラムゼー数の事実
-- =============================================================================

/-- R(1) = 1: 1頂点は自明に単色K_1 -/
theorem ramsey_1_holds : HasRamseyProperty 1 1 := by
  intro col
  exact ⟨{⟨0, by omega⟩}, by simp, Or.inl (by
    intro i hi j hj hij
    simp [Finset.mem_singleton] at hi hj
    subst hi; subst hj
    exact absurd rfl hij)⟩

-- =============================================================================
-- Erdős-Szekeres 上界の一般的な形の述べ方
-- =============================================================================

/-- Erdős-Szekeres上界の命題: R(s,t) ≤ C(s+t-2, s-1)
    ここでは対角ケース R(k) ≤ C(2k-2, k-1) を述べる。
    これは R(k)^{1/k} → 4 の根拠。 -/
def ErdosSzekeresUpperBound : Prop :=
  ∀ k : ℕ, k ≥ 2 → HasRamseyProperty (Nat.choose (2 * k - 2) (k - 1)) k

/-- 確率的方法による下界の命題: R(k) ≥ 2^{(k-1)/2}
    これは R(k)^{1/k} ≥ √2 の根拠。 -/
def ErdosProbabilisticLowerBound : Prop :=
  ∀ k : ℕ, k ≥ 2 → ¬HasRamseyProperty (2 ^ ((k - 1) / 2)) k

-- =============================================================================
-- 問題の形式化
-- =============================================================================

/-- エルデシュ問題 #77 の中心的な問いの1つ:
    R(k)^{1/k} の上極限は4未満である (2023年に解決)。
    より具体的には、ある ε > 0 が存在して、
    十分大きい全ての k に対し R(k) < (4-ε)^k。 -/
def CamposGriffithsMorrisSahasrabudhe : Prop :=
  ∃ ε : ℝ, ε > 0 ∧ ∃ K : ℕ, ∀ k : ℕ, k ≥ K →
    HasRamseyProperty (Nat.floor ((4 - ε) ^ k)) k

/-- エルデシュの元々の問い: lim R(k)^{1/k} は存在するか？
    存在するなら、全てのn ≥ R(k) で HasRamseyProperty n k が成り立ち、
    かつ R(k)^{1/k} が収束すること。($100 の問題) -/
def RamseyLimitExists : Prop :=
  ∃ L : ℝ, L > 0 ∧ ∀ ε : ℝ, ε > 0 →
    ∃ K : ℕ, ∀ k : ℕ, k ≥ K →
      ∀ R : ℕ, IsRamseyNumber k R →
        |((R : ℝ) ^ (1 / (k : ℝ))) - L| < ε

/-- エルデシュの推測: lim R(k)^{1/k} = 2 -/
def ErdosConjecture_RamseyLimit : Prop :=
  ∀ ε : ℝ, ε > 0 →
    ∃ K : ℕ, ∀ k : ℕ, k ≥ K →
      ∀ R : ℕ, IsRamseyNumber k R →
        |((R : ℝ) ^ (1 / (k : ℝ))) - 2| < ε

-- =============================================================================
-- 探索6: R(k) ≥ 2 for k ≥ 2
-- =============================================================================

/-! ## 探索6: R(k) ≥ 2 for k ≥ 2

1頂点グラフ K_1 にはサイズ k ≥ 2 のクリークが存在しないことを示す。
Fin 1 の部分集合は高々1要素なので、|S| = k ≥ 2 は不可能。
-/

-- =============================================================================
-- 探索7: ラムゼーの基本性質
-- =============================================================================

/-! ## 探索7: ラムゼーの基本性質

k=0 や k=1 の場合のラムゼー性質は自明に成り立つ。
また C5 着色が三角形フリーであることの具体的な検証を行う。
-/

/-- k=0 のラムゼー性質は自明に成立（空クリーク） -/
theorem hasRamseyProperty_zero (n : ℕ) : HasRamseyProperty n 0 := by
  intro col
  exact ⟨∅, by simp, Or.inl (fun i hi => by simp at hi)⟩

/-- k=1 のラムゼー性質: n ≥ 1 なら成立（任意の1頂点が単色K_1） -/
theorem hasRamseyProperty_one (n : ℕ) (hn : n ≥ 1) : HasRamseyProperty n 1 := by
  intro col
  exact ⟨{⟨0, by omega⟩}, by simp, Or.inl (by
    intro i hi j hj hij
    simp [Finset.mem_singleton] at hi hj
    subst hi; subst hj
    exact absurd rfl hij)⟩

/-- C5着色で {0,2} は隣接していない (距離2) -/
theorem c5_not_adjacent_0_2 : c5Coloring.color ⟨0, by omega⟩ ⟨2, by omega⟩ = false := by
  decide

/-- C5着色で {1,3} は隣接していない (距離2) -/
theorem c5_not_adjacent_1_3 : c5Coloring.color ⟨1, by omega⟩ ⟨3, by omega⟩ = false := by
  decide

-- =============================================================================
-- 探索6: R(k) ≥ 2 for k ≥ 2
-- =============================================================================

/-- 1頂点グラフにはサイズ2以上のクリークがない -/
theorem not_hasRamseyProperty_one_of_ge_two (k : ℕ) (hk : k ≥ 2) :
    ¬HasRamseyProperty 1 k := by
  intro h
  -- Fin 1 上の自明な塗り分け
  have col : TwoColoring 1 := ⟨fun _ _ => true, fun _ _ => rfl⟩
  obtain ⟨S, hcard, _⟩ := h col
  -- S ⊆ Fin 1 で |S| ≥ 2 だが |Finset.univ : Finset (Fin 1)| = 1
  have hsle : S.card ≤ Fintype.card (Fin 1) := S.card_le_univ
  simp [Fintype.card_fin] at hsle
  omega

-- =============================================================================
-- 探索8: 2色塗り分けの基本的な性質
-- =============================================================================

/-! ## 探索8: 2色塗り分けの基本的な性質

2色塗り分けにおいて、各辺の色は true か false のいずれかである。
また C5 着色の具体的な辺の色を decide で網羅的に検証する。
-/

/-- 2色塗り分けの色は true か false -/
theorem two_coloring_color_cases {n : ℕ} (col : TwoColoring n) (i j : Fin n) :
    col.color i j = true ∨ col.color i j = false := by
  cases col.color i j <;> simp

/-- 自己ループの色は対称性から任意（反射の特殊ケース） -/
theorem two_coloring_self {n : ℕ} (col : TwoColoring n) (i : Fin n) :
    col.color i i = col.color i i := rfl

/-- C5着色で頂点0,1は隣接（色true） -/
example : c5Coloring.color ⟨0, by omega⟩ ⟨1, by omega⟩ = true := by decide

/-- C5着色で頂点0,2は非隣接（色false） -/
example : c5Coloring.color ⟨0, by omega⟩ ⟨2, by omega⟩ = false := by decide

/-- C5着色で頂点1,4は非隣接（距離3 mod 5 = 距離2） -/
example : c5Coloring.color ⟨1, by omega⟩ ⟨4, by omega⟩ = false := by decide

/-- C5着色で頂点2,3は隣接（色true） -/
example : c5Coloring.color ⟨2, by omega⟩ ⟨3, by omega⟩ = true := by decide

/-- C5着色で頂点0,3は非隣接（色false） -/
example : c5Coloring.color ⟨0, by omega⟩ ⟨3, by omega⟩ = false := by decide

/-- C5着色で頂点1,3は非隣接（色false） -/
example : c5Coloring.color ⟨1, by omega⟩ ⟨3, by omega⟩ = false := by decide

/-- C5着色で頂点3,4は隣接（色true） -/
example : c5Coloring.color ⟨3, by omega⟩ ⟨4, by omega⟩ = true := by decide

/-- C5着色で頂点2,4は非隣接（色false） -/
example : c5Coloring.color ⟨2, by omega⟩ ⟨4, by omega⟩ = false := by decide

/-- C5着色で頂点1,2は隣接（色true） -/
example : c5Coloring.color ⟨1, by omega⟩ ⟨2, by omega⟩ = true := by decide

/-- C5着色で頂点0,4は隣接（色true） -/
example : c5Coloring.color ⟨0, by omega⟩ ⟨4, by omega⟩ = true := by decide

/-! ## 探索9: 自明な塗り分けの例 -/

/-- 全て同色（true）の塗り分け -/
def allTrueColoring (n : ℕ) : TwoColoring n where
  color := fun _ _ => true
  symm := fun _ _ => rfl

/-- 全て同色の塗り分けでは、任意の2頂点が単色クリーク -/
theorem allTrue_mono_clique (n : ℕ) (S : Finset (Fin n)) :
    IsMonochromaticClique (allTrueColoring n) S true := by
  intro i _ j _ _
  rfl

/-! ## 探索10: allFalseColoring -/

/-- 全て色false の塗り分け -/
def allFalseColoring (n : ℕ) : TwoColoring n where
  color := fun _ _ => false
  symm := fun _ _ => rfl

/-- 全て色false の塗り分けでは任意の部分集合が false 単色クリーク -/
theorem allFalse_mono_clique (n : ℕ) (S : Finset (Fin n)) :
    IsMonochromaticClique (allFalseColoring n) S false := by
  intro i _ j _ _; rfl

/-! ## 探索11: HasRamseyProperty 3 2 の証明 -/

/-- 全辺 true の K_n で n ≥ k なら、カード k の任意の部分集合が true 単色クリーク -/
theorem hasRamseyProperty_of_allTrue (n k : ℕ) (hk : k ≤ n) :
    ∀ (S : Finset (Fin n)), S.card = k →
    IsMonochromaticClique (allTrueColoring n) S true := by
  intro S _ i hi j hj hij
  rfl

/-! ## 探索12: HasRamseyProperty の合成 -/

/-- HasRamseyProperty n k かつ k ≥ 1 → n ≥ 1 -/
theorem hasRamseyProperty_pos {n k : ℕ} (hk : k ≥ 1) (h : HasRamseyProperty n k) :
    n ≥ 1 := by
  by_contra hn
  push_neg at hn
  have : n = 0 := by omega
  subst this
  -- K_0 上の塗り分けを構成
  have col : TwoColoring 0 :=
    ⟨fun i => Fin.elim0 i, fun i => Fin.elim0 i⟩
  obtain ⟨S, hcard, _⟩ := h col
  -- S ⊆ Fin 0 で |S| = k ≥ 1 だが |Fin 0| = 0
  have hsle : S.card ≤ Fintype.card (Fin 0) := Finset.card_le_univ S
  rw [hcard, Fintype.card_fin] at hsle
  omega

/-! ## 探索14: C5着色の独立集合検証 -/

-- {0, 2} は C5 で独立集合（false色）
example : c5Coloring.color ⟨0, by omega⟩ ⟨2, by omega⟩ = false := by decide
-- {1, 3} は C5 で独立集合
example : c5Coloring.color ⟨1, by omega⟩ ⟨3, by omega⟩ = false := by decide
-- {0, 4} は隣接
example : c5Coloring.color ⟨0, by omega⟩ ⟨4, by omega⟩ = true := by decide

-- =============================================================================
-- R(3,3) ≤ 6 の証明: HasRamseyProperty 6 3
-- =============================================================================

/-! ## R(3,3) ≤ 6: K_6 の任意の2色塗り分けに単色三角形が存在する

数学的証明:
1. 頂点 v を固定。v から他の5頂点への辺は2色なので鳩の巣原理で3辺以上が同色 c
2. その3頂点 a, b, c のうち:
   - ab, ac, bc のいずれかが色 c → v と合わせて色 c の三角形
   - 全て ¬c → abc が色 ¬c の三角形
-/

/-- 頂点 v の色 c の近傍集合 -/
def colorNeighbors {n : ℕ} (col : TwoColoring n) (v : Fin n) (c : Bool) : Finset (Fin n) :=
  (Finset.univ.erase v).filter (fun u => col.color v u = c)

/-- colorNeighbors の互いに素性 -/
theorem colorNeighbors_disjoint {n : ℕ} (col : TwoColoring n) (v : Fin n) :
    Disjoint (colorNeighbors col v true) (colorNeighbors col v false) := by
  unfold colorNeighbors
  exact Finset.disjoint_filter.mpr (fun u _ ht hf => by simp [ht] at hf)

/-- colorNeighbors の和集合 -/
theorem colorNeighbors_union {n : ℕ} (col : TwoColoring n) (v : Fin n) :
    colorNeighbors col v true ∪ colorNeighbors col v false = Finset.univ.erase v := by
  unfold colorNeighbors
  ext u
  simp only [Finset.mem_union, Finset.mem_filter, Finset.mem_erase, Finset.mem_univ]
  constructor
  · rintro (⟨h, _⟩ | ⟨h, _⟩) <;> exact h
  · intro h
    cases hc : col.color v u
    · right; exact ⟨h, rfl⟩
    · left; exact ⟨h, rfl⟩

/-- 色 true/false の近傍で v 以外の頂点を分割: |N_true| + |N_false| = n - 1 -/
theorem colorNeighbors_card_add {n : ℕ} (col : TwoColoring n) (v : Fin n) :
    (colorNeighbors col v true).card + (colorNeighbors col v false).card = n - 1 := by
  rw [← Finset.card_union_of_disjoint (colorNeighbors_disjoint col v),
      colorNeighbors_union col v,
      Finset.card_erase_of_mem (Finset.mem_univ v), Finset.card_univ, Fintype.card_fin]

/-- n=6 なら少なくとも一方の色の近傍が3以上 -/
theorem exists_large_color_neighborhood (col : TwoColoring 6) (v : Fin 6) :
    ∃ c : Bool, 3 ≤ (colorNeighbors col v c).card := by
  have h := colorNeighbors_card_add col v
  -- h : ... + ... = 6 - 1 = 5
  by_cases ht : 3 ≤ (colorNeighbors col v true).card
  · exact ⟨true, ht⟩
  · exact ⟨false, by omega⟩

/-- colorNeighbors の要素は v と異なる -/
theorem colorNeighbors_ne {n : ℕ} (col : TwoColoring n) (v : Fin n) (c : Bool)
    (u : Fin n) (hu : u ∈ colorNeighbors col v c) : u ≠ v := by
  unfold colorNeighbors at hu
  simp [Finset.mem_filter, Finset.mem_erase] at hu
  exact hu.1

/-- colorNeighbors の要素は色 c の辺を持つ -/
theorem colorNeighbors_color {n : ℕ} (col : TwoColoring n) (v : Fin n) (c : Bool)
    (u : Fin n) (hu : u ∈ colorNeighbors col v c) : col.color v u = c := by
  unfold colorNeighbors at hu
  simp [Finset.mem_filter, Finset.mem_erase] at hu
  exact hu.2

/-- Bool の否定: b ≠ true → b = false, b ≠ false → b = true -/
theorem bool_eq_not_of_ne {b : Bool} {c : Bool} (h : b ≠ c) : b = !c := by
  cases b <;> cases c <;> simp_all

/-- 3頂点の単色クリーク: 全ペアの辺が同じ色 -/
private theorem mono_clique_of_three {n : ℕ} {col : TwoColoring n}
    {x y z : Fin n} {c : Bool}
    (hxy : x ≠ y) (hxz : x ≠ z) (hyz : y ≠ z)
    (exy : col.color x y = c) (exz : col.color x z = c) (eyz : col.color y z = c) :
    IsMonochromaticClique col {x, y, z} c := by
  intro i hi j hj hij
  simp [Finset.mem_insert, Finset.mem_singleton] at hi hj
  rcases hi with rfl | rfl | rfl <;> rcases hj with rfl | rfl | rfl
  all_goals (first | exact absurd rfl hij | exact exy | exact exz | exact eyz | (rw [col.symm]; first | exact exy | exact exz | exact eyz))

/-- 3頂点 + 中心頂点から単色三角形を構成する核心補題 -/
theorem ramsey_triangle_from_three {col : TwoColoring 6} {v a b c_vtx : Fin 6}
    {color : Bool}
    (hab : a ≠ b) (hac : a ≠ c_vtx) (hbc : b ≠ c_vtx)
    (hva : col.color v a = color) (hvb : col.color v b = color) (hvc : col.color v c_vtx = color)
    (hav : a ≠ v) (hbv : b ≠ v) (hcv : c_vtx ≠ v) :
    ∃ S : Finset (Fin 6), S.card = 3 ∧
      (IsMonochromaticClique col S true ∨ IsMonochromaticClique col S false) := by
  by_cases hab_c : col.color a b = color
  · -- {v, a, b} が色 color の三角形
    refine ⟨{v, a, b}, Finset.card_eq_three.mpr ⟨v, a, b, hav.symm, hbv.symm, hab, rfl⟩, ?_⟩
    cases color
    · exact Or.inr (mono_clique_of_three hav.symm hbv.symm hab hva hvb hab_c)
    · exact Or.inl (mono_clique_of_three hav.symm hbv.symm hab hva hvb hab_c)
  · by_cases hac_c : col.color a c_vtx = color
    · -- {v, a, c_vtx} が色 color の三角形
      refine ⟨{v, a, c_vtx}, Finset.card_eq_three.mpr ⟨v, a, c_vtx, hav.symm, hcv.symm, hac, rfl⟩, ?_⟩
      cases color
      · exact Or.inr (mono_clique_of_three hav.symm hcv.symm hac hva hvc hac_c)
      · exact Or.inl (mono_clique_of_three hav.symm hcv.symm hac hva hvc hac_c)
    · by_cases hbc_c : col.color b c_vtx = color
      · -- {v, b, c_vtx} が色 color の三角形
        refine ⟨{v, b, c_vtx}, Finset.card_eq_three.mpr ⟨v, b, c_vtx, hbv.symm, hcv.symm, hbc, rfl⟩, ?_⟩
        cases color
        · exact Or.inr (mono_clique_of_three hbv.symm hcv.symm hbc hvb hvc hbc_c)
        · exact Or.inl (mono_clique_of_three hbv.symm hcv.symm hbc hvb hvc hbc_c)
      · -- 全て ≠ color なので {a, b, c_vtx} が色 !color の三角形
        have hab' : col.color a b = !color := bool_eq_not_of_ne hab_c
        have hac' : col.color a c_vtx = !color := bool_eq_not_of_ne hac_c
        have hbc' : col.color b c_vtx = !color := bool_eq_not_of_ne hbc_c
        refine ⟨{a, b, c_vtx}, Finset.card_eq_three.mpr ⟨a, b, c_vtx, hab, hac, hbc, rfl⟩, ?_⟩
        cases color
        · exact Or.inl (mono_clique_of_three hab hac hbc hab' hac' hbc')
        · exact Or.inr (mono_clique_of_three hab hac hbc hab' hac' hbc')

/-- R(3,3) ≤ 6: K_6 の任意の2色塗り分けに単色三角形が存在する -/
theorem ramsey_three_three : HasRamseyProperty 6 3 := by
  intro col
  -- Step 1: 頂点 0 を固定
  set v : Fin 6 := ⟨0, by omega⟩
  -- Step 2: 鳩の巣原理で3頂点以上が同色
  obtain ⟨c, hc⟩ := exists_large_color_neighborhood col v
  -- Step 3: 3元以上の集合から3つの異なる要素を取り出す
  have hc' : 2 < (colorNeighbors col v c).card := by omega
  rw [Finset.two_lt_card] at hc'
  obtain ⟨a, ha, b, hb, c_vtx, hc_vtx, hab, hac, hbc⟩ := hc'
  -- Step 4: 色の情報を取得
  have hva := colorNeighbors_color col v c a ha
  have hvb := colorNeighbors_color col v c b hb
  have hvc := colorNeighbors_color col v c c_vtx hc_vtx
  have hav := colorNeighbors_ne col v c a ha
  have hbv := colorNeighbors_ne col v c b hb
  have hcv := colorNeighbors_ne col v c c_vtx hc_vtx
  -- Step 5: 三角形を構成
  exact ramsey_triangle_from_three hab hac hbc hva hvb hvc hav hbv hcv

-- =============================================================================
-- R(3,3) ≥ 6 の証明: ¬HasRamseyProperty 5 3
-- =============================================================================

/-! ## R(3,3) ≥ 6: K₅ には単色三角形を含まない2色塗り分けが存在する

C₅着色（5頂点の環状グラフ: 隣接=true, 非隣接=false）において、
true色の三角形も false色の三角形も存在しない。
- C₅のクリーク数 = 2（最大クリークは隣接する2頂点）
- C₅の補グラフもC₅なので、独立数 = 2
- よってどちらの色でもサイズ3のクリークは存在しない
-/

/-- R(3,3) ≥ 6: K₅ の2色塗り分けで単色三角形を含まないものが存在する -/
theorem not_hasRamseyProperty_five_three : ¬HasRamseyProperty 5 3 := by
  intro h
  obtain ⟨S, hcard, hmono⟩ := h c5Coloring
  rw [Finset.card_eq_three] at hcard
  obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := hcard
  cases hmono with
  | inl htrue =>
    have h1 := htrue a (by simp) b (by simp) hab
    have h2 := htrue a (by simp) c (by simp) hac
    have h3 := htrue b (by simp) c (by simp) hbc
    fin_cases a <;> fin_cases b <;> fin_cases c <;> simp_all [c5Coloring, c5Adjacent]
  | inr hfalse =>
    have h1 := hfalse a (by simp) b (by simp) hab
    have h2 := hfalse a (by simp) c (by simp) hac
    have h3 := hfalse b (by simp) c (by simp) hbc
    fin_cases a <;> fin_cases b <;> fin_cases c <;> simp_all [c5Coloring, c5Adjacent]

-- =============================================================================
-- R(3,3) = 6 の完全特徴付け
-- =============================================================================

/-- R(2,2) = 2 の完全特徴付け: HasRamseyProperty 2 2 かつ ¬HasRamseyProperty 1 2 -/
theorem isRamseyNumber_two : IsRamseyNumber 2 2 :=
  ⟨ramsey_2_holds, not_hasRamseyProperty_one_of_ge_two 2 (by omega)⟩

/-- R(3,3) = 6 の完全特徴付け: HasRamseyProperty 6 3 かつ ¬HasRamseyProperty 5 3 -/
theorem isRamseyNumber_three : IsRamseyNumber 3 6 := by
  exact ⟨ramsey_three_three, not_hasRamseyProperty_five_three⟩

-- =============================================================================
-- HasRamseyProperty の n に関する単調性
-- =============================================================================

/-! ## HasRamseyProperty は n に関して単調

HasRamseyProperty m k かつ n ≥ m ならば HasRamseyProperty n k。
n 頂点の塗り分けを Fin m → Fin n の自然な埋め込みで m 頂点に制限し、
m 頂点版のラムゼー性質を適用して得られる単色クリークを Fin n にリフトする。
-/

/-- Fin m → Fin n の自然な埋め込み（m ≤ n のとき） -/
private def finEmb (m n : ℕ) (hmn : m ≤ n) : Fin m → Fin n :=
  fun i => ⟨i.val, by omega⟩

private theorem finEmb_injective {m n : ℕ} (hmn : m ≤ n) :
    Function.Injective (finEmb m n hmn) := by
  intro a b hab
  simp [finEmb] at hab
  exact Fin.ext hab

/-- HasRamseyProperty は n に関して単調: m ≤ n かつ HasRamseyProperty m k → HasRamseyProperty n k -/
theorem hasRamseyProperty_mono {m n k : ℕ} (hmn : m ≤ n) (h : HasRamseyProperty m k) :
    HasRamseyProperty n k := by
  intro col
  -- col を m 頂点に制限
  let emb := finEmb m n hmn
  let col_m : TwoColoring m := ⟨
    fun i j => col.color (emb i) (emb j),
    fun i j => col.symm (emb i) (emb j)⟩
  -- m 頂点でラムゼー性質を適用
  obtain ⟨S, hcard, hmono⟩ := h col_m
  -- S を Fin n にリフト
  have hinj : Set.InjOn emb (S : Set (Fin m)) := by
    intro a _ b _ hab
    exact finEmb_injective hmn hab
  refine ⟨S.image emb, ?_, ?_⟩
  · -- card の保存
    rw [Finset.card_image_of_injOn hinj]
    exact hcard
  · -- 単色性の保存
    cases hmono with
    | inl ht =>
      left
      intro i hi j hj hij
      rw [Finset.mem_image] at hi hj
      obtain ⟨i', hi', rfl⟩ := hi
      obtain ⟨j', hj', rfl⟩ := hj
      have hij' : i' ≠ j' := by
        intro heq; apply hij; exact congrArg emb heq
      change col_m.color i' j' = true
      exact ht i' hi' j' hj' hij'
    | inr hf =>
      right
      intro i hi j hj hij
      rw [Finset.mem_image] at hi hj
      obtain ⟨i', hi', rfl⟩ := hi
      obtain ⟨j', hj', rfl⟩ := hj
      have hij' : i' ≠ j' := by
        intro heq; apply hij; exact congrArg emb heq
      change col_m.color i' j' = false
      exact hf i' hi' j' hj' hij'

/-- 系: R(3,3) ≤ 6 から、n ≥ 6 ならば HasRamseyProperty n 3 -/
theorem hasRamseyProperty_ge_six {n : ℕ} (hn : n ≥ 6) : HasRamseyProperty n 3 :=
  hasRamseyProperty_mono hn ramsey_three_three

-- =============================================================================
-- 単色クリークの部分集合性
-- =============================================================================

/-- 単色クリークの部分集合も単色クリーク -/
theorem isMonochromaticClique_subset {n : ℕ} {col : TwoColoring n}
    {S T : Finset (Fin n)} {c : Bool}
    (h : IsMonochromaticClique col S c) (hTS : T ⊆ S) :
    IsMonochromaticClique col T c :=
  fun i hi j hj hij => h i (hTS hi) j (hTS hj) hij

-- =============================================================================
-- HasRamseyProperty の k に関する単調性（下方）
-- =============================================================================

-- =============================================================================
-- R(1) = 1 の完全特徴付け
-- =============================================================================

/-! ## R(1) = 1 の完全特徴付け

R(1) = 1: K_1 の任意の2色塗り分けにサイズ1の単色クリークが存在し（ramsey_1_holds）、
K_0 にはサイズ1の単色クリークが存在しない（0頂点にはサイズ1の部分集合がない）。
-/

/-- R(1) = 1 の完全特徴付け -/
theorem isRamseyNumber_one : IsRamseyNumber 1 1 := by
  constructor
  · exact ramsey_1_holds
  · -- ¬HasRamseyProperty 0 1
    intro h
    have col : TwoColoring 0 :=
      ⟨fun i => Fin.elim0 i, fun i => Fin.elim0 i⟩
    obtain ⟨S, hcard, _⟩ := h col
    have hsle : S.card ≤ Fintype.card (Fin 0) := Finset.card_le_univ S
    rw [hcard, Fintype.card_fin] at hsle
    omega

/-- HasRamseyProperty n (k+1) → HasRamseyProperty n k (k ≥ 1) -/
theorem hasRamseyProperty_k_mono {n k : ℕ} (hk : k ≥ 1)
    (h : HasRamseyProperty n (k + 1)) : HasRamseyProperty n k := by
  intro col
  obtain ⟨S, hcard, hmono⟩ := h col
  -- S から1元を除いて k 元部分集合を作る
  have hne : S.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]; intro he; rw [he] at hcard; simp at hcard
  obtain ⟨x, hx⟩ := hne
  refine ⟨S.erase x, ?_, ?_⟩
  · rw [Finset.card_erase_of_mem hx, hcard]; omega
  · cases hmono with
    | inl ht => exact Or.inl (isMonochromaticClique_subset ht (Finset.erase_subset x S))
    | inr hf => exact Or.inr (isMonochromaticClique_subset hf (Finset.erase_subset x S))

/-! ## 探索: HasRamseyProperty の系 -/

/-- HasRamseyProperty n k かつ k ≥ 1 → n ≥ k（鳩の巣原理の系） -/
theorem hasRamseyProperty_card_le {n k : ℕ} (h : HasRamseyProperty n k) :
    k ≤ n := by
  -- 全色 true の塗り分けを使う
  obtain ⟨S, hcard, _⟩ := h (allTrueColoring n)
  rw [← hcard]
  have : S.card ≤ Fintype.card (Fin n) := Finset.card_le_univ S
  rwa [Fintype.card_fin] at this

/-- n ≥ 2 なら任意の2色塗り分けに単色辺が存在 -/
theorem hasRamseyProperty_ge_two (n : ℕ) (hn : n ≥ 2) : HasRamseyProperty n 2 :=
  hasRamseyProperty_mono hn ramsey_2_holds

/-- n < k → ¬HasRamseyProperty n k（hasRamseyProperty_card_le の対偶） -/
theorem not_hasRamseyProperty_of_lt {n k : ℕ} (h : n < k) : ¬HasRamseyProperty n k := by
  intro hr; exact absurd (hasRamseyProperty_card_le hr) (by omega)
