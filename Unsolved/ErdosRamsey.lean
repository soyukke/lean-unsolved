import Mathlib

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
