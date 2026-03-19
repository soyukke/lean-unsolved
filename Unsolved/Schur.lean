import Mathlib

set_option linter.style.longLine false

/-!
# Schur Numbers

Schur数 S(r): {1,...,N} を r 色で塗り分けたとき、
必ず単色の x + y = z (x, y, z 全て同色) が存在する最小の N。

## 主要結果
- S(1) = 2 の完全特徴付け
- S(2) = 5 の完全特徴付け
-/

-- =============================================================================
-- 基本定義
-- =============================================================================

/-- {1,...,n} の r 色塗り分け。Fin n の i 番目は値 i+1 に対応する。 -/
abbrev SchurColoring (n r : ℕ) := Fin n → Fin r

/-- 単色 Schur triple: x + y = z で x, y, z ∈ {1,...,n}, 全て同色。
    Fin n のインデックスでは (i.val+1) + (j.val+1) = (k.val+1) -/
def HasMonoSchurTriple {n r : ℕ} (c : SchurColoring n r) : Prop :=
  ∃ (i j k : Fin n),
    (i.val + 1) + (j.val + 1) = k.val + 1 ∧
    c i = c j ∧ c i = c k

instance instDecidableHasMonoSchurTriple {n r : ℕ} (c : SchurColoring n r) :
    Decidable (HasMonoSchurTriple c) :=
  inferInstanceAs (Decidable (∃ (i j k : Fin n),
    (i.val + 1) + (j.val + 1) = k.val + 1 ∧
    c i = c j ∧ c i = c k))

-- =============================================================================
-- S(1) = 2
-- =============================================================================

/-- S(1) ≤ 2: {1,2} の任意の1色塗りに単色 Schur triple が存在する。
    1 + 1 = 2 が唯一の解。 -/
theorem schur_one_upper : ∀ c : SchurColoring 2 1, HasMonoSchurTriple c := by
  native_decide

/-- S(1) ≥ 2: {1} の1色塗りで Schur triple を回避可能。
    x + y = z で x, y, z ∈ {1} とすると 1+1=2 ∉ {1} なので回避可能。 -/
theorem schur_one_lower : ∃ c : SchurColoring 1 1, ¬HasMonoSchurTriple c := by
  native_decide

-- =============================================================================
-- S(2) = 5
-- =============================================================================

/-- S(2) ≤ 5: {1,...,5} の任意の2色塗りに単色 Schur triple が存在する -/
theorem schur_two_upper : ∀ c : SchurColoring 5 2, HasMonoSchurTriple c := by
  native_decide

/-- S(2) ≥ 5: {1,...,4} で Schur triple を回避する2色塗りが存在する。
    回避例: {1,4} を色0、{2,3} を色1
    - 色0: 1+4=5∉{1,4}, 1+1=2∉{1,4}, 4+4=8∉{1,4}
    - 色1: 2+3=5∉{2,3}, 2+2=4∉{2,3}, 3+3=6∉{2,3} -/
theorem schur_two_lower : ∃ c : SchurColoring 4 2, ¬HasMonoSchurTriple c := by
  native_decide

-- =============================================================================
-- Schur 数の特徴付け
-- =============================================================================

/-- Schur 数の特徴付け: S(r) = N とは、
    {1,...,N} の任意の r 色塗りに単色 Schur triple が存在し、
    かつ {1,...,N-1} で回避可能な r 色塗りが存在すること。 -/
def IsSchurNumber (r N : ℕ) : Prop :=
  (∀ c : SchurColoring N r, HasMonoSchurTriple c) ∧
  (N ≥ 1 → ∃ c : SchurColoring (N - 1) r, ¬HasMonoSchurTriple c)

/-- S(1) = 2 の完全特徴付け -/
theorem isSchurNumber_one : IsSchurNumber 1 2 :=
  ⟨schur_one_upper, fun _ => schur_one_lower⟩

/-- S(2) = 5 の完全特徴付け -/
theorem isSchurNumber_two : IsSchurNumber 2 5 :=
  ⟨schur_two_upper, fun _ => schur_two_lower⟩

-- =============================================================================
-- 回避塗り分けの具体的構成
-- =============================================================================

/-- S(2) の回避例: {1,4} → 0, {2,3} → 1 -/
def schurTwoWitness : SchurColoring 4 2 :=
  ![⟨0, by omega⟩, ⟨1, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]

/-- schurTwoWitness が Schur triple を持たないことの検証 -/
theorem schurTwoWitness_avoids : ¬HasMonoSchurTriple schurTwoWitness := by
  native_decide

-- =============================================================================
-- Schur 数の追加性質
-- =============================================================================

/-- S(r) の定義で N=1 は r=2 色で常に回避可能（{1} で x+y=z を満たす三つ組なし） -/
theorem schur_avoidable_one_two : ∃ c : SchurColoring 1 2, ¬HasMonoSchurTriple c := by
  native_decide
