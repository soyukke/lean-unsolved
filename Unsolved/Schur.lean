import Mathlib

set_option linter.style.longLine false

/-!
# Schur Numbers

Schur数 S(r): {1,...,N} を r 色で塗り分けたとき、
必ず単色の x + y = z (x, y, z 全て同色) が存在する最小の N。

## 主要結果
- S(1) = 2 の完全特徴付け
- S(2) = 5 の完全特徴付け
- S(3) ≥ 14 の下界（具体的回避塗り分けによる証明）
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

set_option linter.style.nativeDecide false in
/-- N=2, r=2 でも Schur triple は回避可能（S(2) > 2） -/
theorem schur_avoidable_two_two : ∃ c : SchurColoring 2 2, ¬HasMonoSchurTriple c := by
  native_decide

set_option linter.style.nativeDecide false in
/-- N=3, r=2 でも Schur triple は回避可能（S(2) > 3） -/
theorem schur_avoidable_three_two : ∃ c : SchurColoring 3 2, ¬HasMonoSchurTriple c := by
  native_decide

set_option linter.style.nativeDecide false in
/-- N=4, r=2 でも Schur triple は回避可能（S(2) > 4） -/
theorem schur_avoidable_four_two : ∃ c : SchurColoring 4 2, ¬HasMonoSchurTriple c := by
  native_decide

set_option linter.style.nativeDecide false in
/-- S(1) > 1: N=1 で r=1 色の Schur triple 回避が可能。
    {1} のみなので x+y=z を満たす三つ組は存在しない。 -/
theorem schur_avoidable_one_one : ∃ c : SchurColoring 1 1, ¬HasMonoSchurTriple c := by
  native_decide

set_option linter.style.nativeDecide false in
/-- S(r) ≥ 2 for r=3: N=1 では3色で Schur triple を回避可能。
    {1} のみなので x+y=z を満たす三つ組は存在しない。 -/
theorem schur_avoidable_one_three : ∃ c : SchurColoring 1 3, ¬HasMonoSchurTriple c := by
  native_decide

-- =============================================================================
-- S(3) ≥ 14
-- =============================================================================

/-- S(3) ≥ 14 の回避塗り分け（具体的構成）。
    色0: {1,4,10,13}, 色1: {5,6,7,8,9}, 色2: {2,3,11,12}
    この塗り分けは {1,...,13} 上で単色 Schur triple x+y=z を回避する。 -/
def schurThreeWitness : SchurColoring 13 3 :=
  fun i => match i.val with
    | 0 => 0   -- 1 → 色0
    | 1 => 2   -- 2 → 色2
    | 2 => 2   -- 3 → 色2
    | 3 => 0   -- 4 → 色0
    | 4 => 1   -- 5 → 色1
    | 5 => 1   -- 6 → 色1
    | 6 => 1   -- 7 → 色1
    | 7 => 1   -- 8 → 色1
    | 8 => 1   -- 9 → 色1
    | 9 => 0   -- 10 → 色0
    | 10 => 2  -- 11 → 色2
    | 11 => 2  -- 12 → 色2
    | 12 => 0  -- 13 → 色0
    | _ => 0

set_option linter.style.nativeDecide false in
/-- schurThreeWitness が Schur triple を持たないことの検証 -/
theorem schurThreeWitness_avoids : ¬HasMonoSchurTriple schurThreeWitness := by
  native_decide

set_option linter.style.nativeDecide false in
/-- S(3) ≥ 14: {1,...,13} で3色塗り分けにより Schur triple 回避可能 -/
theorem schur_three_lower : ∃ c : SchurColoring 13 3, ¬HasMonoSchurTriple c :=
  ⟨schurThreeWitness, schurThreeWitness_avoids⟩

-- =============================================================================
-- Sum-free 集合
-- =============================================================================

/-! ## Sum-free 集合

集合 A が sum-free: ∀ x y z ∈ A, x + y ≠ z
これは Schur triple の不在と同値。
-/

/-- 集合 A ⊆ {1,...,n} が sum-free: A 内に x + y = z となる組がない -/
def IsSumFree (A : Finset ℕ) : Prop :=
  ∀ x ∈ A, ∀ y ∈ A, ∀ z ∈ A, x + y ≠ z

/-- 奇数の集合は sum-free: 奇数+奇数=偶数 なので和は集合に入らない -/
theorem isSumFree_odds (A : Finset ℕ) (hA : ∀ a ∈ A, a % 2 = 1) : IsSumFree A := by
  intro x hx y hy z hz heq
  have hxo := hA x hx
  have hyo := hA y hy
  have hzo := hA z hz
  -- x + y は偶数だが z は奇数
  omega

/-- {1, 4} は sum-free -/
example : IsSumFree {1, 4} := by
  intro x hx y hy z hz heq
  fin_cases hx <;> fin_cases hy <;> fin_cases hz <;> omega

/-- 空集合は sum-free -/
theorem isSumFree_empty : IsSumFree ∅ := by
  intro x hx
  simp at hx

/-- 単元集合は sum-free: {a} で a + a ≠ a（a > 0 のとき） -/
theorem isSumFree_singleton (a : ℕ) (ha : a > 0) : IsSumFree {a} := by
  intro x hx y hy z hz heq
  rw [Finset.mem_singleton] at hx hy hz
  subst hx; subst hy; subst hz
  omega

-- =============================================================================
-- Sum-free 集合の最大サイズ検証
-- =============================================================================

/-! ## Sum-free 集合の追加例と最大サイズ -/

/-- {3, 4, 5} は sum-free（奇数集合の特殊ケース） -/
example : IsSumFree {3, 4, 5} := by
  intro x hx y hy z hz heq
  fin_cases hx <;> fin_cases hy <;> fin_cases hz <;> omega

/-- {1, 3, 5} は sum-free（奇数の部分集合） -/
example : IsSumFree {1, 3, 5} := by
  intro x hx y hy z hz heq
  fin_cases hx <;> fin_cases hy <;> fin_cases hz <;> omega

/-- {2, 3} は sum-free -/
example : IsSumFree {2, 3} := by
  intro x hx y hy z hz heq
  fin_cases hx <;> fin_cases hy <;> fin_cases hz <;> omega

-- =============================================================================
-- Schur 数と Sum-free の関係
-- =============================================================================

/-! ## Schur triple なし ⟺ 全色クラスが sum-free

2色塗り分けの各色クラスが sum-free であれば、Schur triple は存在しない。
これは HasMonoSchurTriple の定義から直接従う。
-/

-- =============================================================================
-- Schur 単調性
-- =============================================================================

/-- Schur の N-単調性: 小さい N で全 r-coloring に Schur triple → 大きい M でも -/
theorem schur_mono {N M r : ℕ} (hNM : N ≤ M)
    (h : ∀ c : SchurColoring N r, HasMonoSchurTriple c) :
    ∀ c : SchurColoring M r, HasMonoSchurTriple c := by
  intro c
  let c' : SchurColoring N r := fun i => c ⟨i.val, by omega⟩
  obtain ⟨x, y, z, hsum, hcx, hcz⟩ := h c'
  exact ⟨⟨x.val, by omega⟩, ⟨y.val, by omega⟩, ⟨z.val, by omega⟩, hsum, hcx, hcz⟩

/-- 回避塗り分けの下方単調性: 大きい M で回避可能なら小さい N でも回避可能 -/
theorem schur_avoidable_of_le {N M r : ℕ} (hNM : N ≤ M)
    (h : ∃ c : SchurColoring M r, ¬HasMonoSchurTriple c) :
    ∃ c : SchurColoring N r, ¬HasMonoSchurTriple c := by
  obtain ⟨c, hc⟩ := h
  refine ⟨fun i => c ⟨i.val, by omega⟩, ?_⟩
  intro ⟨x, y, z, hsum, hcx, hcz⟩
  exact hc ⟨⟨x.val, by omega⟩, ⟨y.val, by omega⟩, ⟨z.val, by omega⟩, hsum, hcx, hcz⟩

/-- S(2) の iff 特徴付け: 全2色塗りに Schur triple が存在する ⟺ N ≥ 5 -/
theorem schur_two_iff (N : ℕ) :
    (∀ c : SchurColoring N 2, HasMonoSchurTriple c) ↔ N ≥ 5 := by
  constructor
  · intro h
    by_contra hlt; push_neg at hlt
    have := schur_avoidable_of_le (show N ≤ 4 by omega) schur_avoidable_four_two
    obtain ⟨c, hc⟩ := this
    exact hc (h c)
  · intro hN
    exact schur_mono (show 5 ≤ N by omega) schur_two_upper

-- =============================================================================
-- Sum-free 集合の追加性質
-- =============================================================================

/-- 全色クラスが sum-free ならば Schur triple は存在しない:
    塗り分け c に対して、任意の色 a のクラス上で x+y≠z が成り立つならば
    HasMonoSchurTriple c は偽 -/
theorem no_schur_triple_of_all_sumfree {n r : ℕ} (c : SchurColoring n r)
    (h : ∀ (a : Fin r), ∀ (i j k : Fin n),
      c i = a → c j = a → c k = a →
      (i.val + 1) + (j.val + 1) ≠ k.val + 1) :
    ¬HasMonoSchurTriple c := by
  intro ⟨i, j, k, heq, hij, hik⟩
  exact h (c i) i j k rfl hij.symm hik.symm heq

-- =============================================================================
-- S(1) の iff 特徴付け
-- =============================================================================

/-- S(1) の iff: (∀ c : SchurColoring N 1, HasMonoSchurTriple c) ↔ N ≥ 2 -/
theorem schur_one_iff (N : ℕ) :
    (∀ c : SchurColoring N 1, HasMonoSchurTriple c) ↔ N ≥ 2 := by
  constructor
  · intro h; by_contra hlt; push_neg at hlt
    have := schur_avoidable_of_le (show N ≤ 1 by omega) schur_avoidable_one_one
    obtain ⟨c, hc⟩ := this; exact hc (h c)
  · intro hN; exact schur_mono (show 2 ≤ N by omega) schur_one_upper
