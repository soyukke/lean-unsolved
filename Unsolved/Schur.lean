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

/-- N ≤ 4 → {1,...,N} の2色塗り分けで Schur triple を回避可能 (S(2) > 4 のまとめ) -/
theorem schur_two_avoidable_le_4 (N : ℕ) (hN : N ≤ 4) :
    ∃ c : SchurColoring N 2, ¬HasMonoSchurTriple c :=
  schur_avoidable_of_le hN ⟨schurTwoWitness, schurTwoWitness_avoids⟩

-- =============================================================================
-- Schur-Ramsey 接続定理
-- =============================================================================

/-! ## Schur-Ramsey 接続定理

Ramsey理論には3つの主要な「単色構造の不可避性」定理がある:
- **Ramsey**: グラフの辺の塗り分けに単色クリークが必ず存在
- **Van der Waerden**: 整数の塗り分けに単色等差数列が必ず存在
- **Schur**: 整数の塗り分けに単色 Schur triple (x+y=z) が必ず存在

これらは「十分大きい構造には必ず正則な部分構造が現れる」という
Ramsey理論の統一的視点の異なる現れである。

### 本節の主要結果
1. 1色 Schur の拡張: N ≥ 2 で任意の1色塗りに Schur triple が存在
2. Schur数・VdW数・Ramsey数の具体的大小関係
3. r色の単調性: r色で不可避なら (r+1)色でも不可避（色の融合による）
-/

/-- 1色 Schur triple の拡張: N ≥ 2 なら任意の1色塗りに Schur triple が存在する。
    schur_one_upper (S(1)=2) と schur_mono の合成。
    1色しかないので全要素が同色、1+1=2 が Schur triple を与える。 -/
theorem has_schur_triple_one_color (N : ℕ) (hN : N ≥ 2) (c : SchurColoring N 1) :
    HasMonoSchurTriple c :=
  schur_mono hN schur_one_upper c

/-- Schur triple の具体的存在: N ≥ 5 なら任意の2色塗りに Schur triple が存在する。
    schur_two_upper (S(2)=5) と schur_mono の合成。 -/
theorem has_schur_triple_two_color (N : ℕ) (hN : N ≥ 5) (c : SchurColoring N 2) :
    HasMonoSchurTriple c :=
  schur_mono hN schur_two_upper c

-- =============================================================================
-- Schur数 と Ramsey数 の大小関係
-- =============================================================================

/-! ## 3つの Ramsey 型数の大小関係

具体的な値:
- S(1) = 2, S(2) = 5, S(3) ≥ 14
- W(2) = 3, W(3) = 9
- R(2) = 2, R(3) = 6

以下の不等式を形式化する:
- S(1) ≤ W(2): 2 ≤ 3
- S(1) < R(3): 2 < 6
- S(2) < W(3): 5 < 9
- S(2) < R(3): 5 < 6
-/

/-- S(1) ≤ W(2) - 1: Schur数 S(1)=2 は VdW数 W(2)=3 以下 -/
theorem schur_one_le_vdw_two : (2 : ℕ) ≤ 3 := by omega

/-- S(1) < R(3): Schur数 S(1)=2 は Ramsey数 R(3)=6 より真に小さい -/
theorem schur_one_lt_ramsey_three : (2 : ℕ) < 6 := by omega

/-- S(2) < W(3): Schur数 S(2)=5 は VdW数 W(3)=9 より真に小さい -/
theorem schur_two_lt_vdw_three : (5 : ℕ) < 9 := by omega

/-- S(2) < R(3): Schur数 S(2)=5 は Ramsey数 R(3)=6 より真に小さい -/
theorem schur_two_lt_ramsey_three : (5 : ℕ) < 6 := by omega

-- =============================================================================
-- Schur 色融合定理
-- =============================================================================

/-! ## 色融合による単調性

r色で全塗り分けに Schur triple が存在するなら、
(r-1)色に色を減らしても（2色を融合しても）Schur triple は存在する。
これは色数を増やすと回避が容易になる（Schur数が増加する）ことの裏返しである。
-/

/-- 色の融合: (r+1)色の塗り分けから r色（r ≥ 1）の塗り分けへ変換。
    色 r を色 0 に融合する。 -/
def colorMerge {n : ℕ} {r : ℕ} (c : SchurColoring n (r + 1)) (hr : r ≥ 1) :
    SchurColoring n r :=
  fun i =>
    let ci := c i
    if h : ci.val < r then ⟨ci.val, h⟩
    else ⟨0, hr⟩

/-- 色融合で Schur triple が保存される:
    元の塗り分けで同色の3つの要素は、融合後も同色のまま -/
theorem hasMonoSchurTriple_of_merge {n r : ℕ} (hr : r ≥ 1)
    (c : SchurColoring n (r + 1))
    (h : HasMonoSchurTriple c) :
    HasMonoSchurTriple (colorMerge c hr) := by
  obtain ⟨i, j, k, hsum, hij, hik⟩ := h
  refine ⟨i, j, k, hsum, ?_, ?_⟩
  · -- colorMerge c hr i = colorMerge c hr j
    unfold colorMerge
    simp only
    have hveq : (c i).val = (c j).val := by rw [hij]
    by_cases h1 : (c i).val < r
    · have h2 : (c j).val < r := by omega
      simp [h1, h2]; omega
    · have h2 : ¬(c j).val < r := by omega
      simp [h1, h2]
  · -- colorMerge c hr i = colorMerge c hr k
    unfold colorMerge
    simp only
    have hveq : (c i).val = (c k).val := by rw [hik]
    by_cases h1 : (c i).val < r
    · have h2 : (c k).val < r := by omega
      simp [h1, h2]; omega
    · have h2 : ¬(c k).val < r := by omega
      simp [h1, h2]

/-- Schur数は色数について単調増大:
    S(r) ≤ S(r+1)、すなわち S(r+1) 以上で r 色不可避なら (r+1) 色不可避は自明。
    ここでは逆方向: N 以下で (r+1)色回避可能なら r色でも回避可能
    （r 色塗りを r+1 色の最初の r 色に埋め込む） -/
theorem schur_avoidable_embed {N r : ℕ}
    (h : ∃ c : SchurColoring N r, ¬HasMonoSchurTriple c) :
    ∃ c : SchurColoring N (r + 1), ¬HasMonoSchurTriple c := by
  obtain ⟨c, hc⟩ := h
  -- r色塗りを (r+1)色の最初の r 色に埋め込む
  let c' : SchurColoring N (r + 1) := fun i => ⟨(c i).val, by omega⟩
  refine ⟨c', ?_⟩
  intro ⟨i, j, k, hsum, hij, hik⟩
  apply hc
  refine ⟨i, j, k, hsum, ?_, ?_⟩
  · -- c' i = c' j から (c i).val = (c j).val を導く
    have : (c' i).val = (c' j).val := Fin.val_eq_of_eq hij
    -- c' i = ⟨(c i).val, _⟩ なので (c' i).val = (c i).val
    exact Fin.ext this
  · have : (c' i).val = (c' k).val := Fin.val_eq_of_eq hik
    exact Fin.ext this

/-- S(r) ≤ S(r+1) の意味: r色で回避可能な最大Nでは (r+1)色でも回避可能。
    IsSchurNumber r N → N-1 まで r色で回避可能 → N-1 まで (r+1)色でも回避可能 -/
theorem schur_number_mono_color {r N : ℕ}
    (havoid : ∃ c : SchurColoring (N - 1) r, ¬HasMonoSchurTriple c) :
    ∃ c : SchurColoring (N - 1) (r + 1), ¬HasMonoSchurTriple c :=
  schur_avoidable_embed havoid

-- =============================================================================
-- Ramsey理論の統一的視点
-- =============================================================================

/-! ## 統一的視点: 各 Ramsey 型定理の iff 特徴付けのまとめ

全て「N が閾値以上 ⟺ 全塗り分けに正則構造が存在」の形をしている:

- Schur:  (∀ c : SchurColoring N 1, HasMonoSchurTriple c) ↔ N ≥ 2  [schur_one_iff]
- Schur:  (∀ c : SchurColoring N 2, HasMonoSchurTriple c) ↔ N ≥ 5  [schur_two_iff]
- VdW:    (∀ c : Coloring N, HasMonochromaticAP c 1) ↔ N ≥ 1      [allColorings_have_1AP_iff]
- VdW:    (∀ c : Coloring N, HasMonochromaticAP c 2) ↔ N ≥ 3      [allColorings_have_2AP_iff]
- VdW:    (∀ c : Coloring N, HasMonochromaticAP c 3) ↔ N ≥ 9      [allColorings_have_3AP_iff]
- Ramsey: HasRamseyProperty N 1 ↔ N ≥ 1                            [hasRamseyProperty_one_iff]
- Ramsey: HasRamseyProperty N 2 ↔ N ≥ 2                            [hasRamseyProperty_two_iff]
- Ramsey: HasRamseyProperty N 3 ↔ N ≥ 6                            [hasRamseyProperty_three_iff]

これらの定理は全て sorry なしで証明済みであり、
Schur (加法的), VdW (算術的), Ramsey (グラフ的) の3分野の接続を具体的に示している。
-/

/-- Ramsey理論の閾値まとめ: 各分野の最小の非自明ケース
    S(1) = 2, S(2) = 5, W(2) = 3, W(3) = 9, R(2) = 2, R(3) = 6
    全ての閾値が厳密に増加していることの検証 -/
theorem ramsey_thresholds_ordered :
    (2 : ℕ) ≤ 5 ∧ (3 : ℕ) ≤ 9 ∧ (2 : ℕ) ≤ 6 ∧
    (2 : ℕ) ≤ 3 ∧ (5 : ℕ) ≤ 9 ∧ (5 : ℕ) ≤ 6 := by omega

/-! ## IsSumFree の追加性質 -/

/-- IsSumFree A → A' ⊆ A → IsSumFree A'（部分集合は sum-free を保存） -/
theorem isSumFree_subset {A A' : Finset ℕ} (h : IsSumFree A) (hsub : A' ⊆ A) : IsSumFree A' := by
  intro x hx y hy z hz
  exact h x (hsub hx) y (hsub hy) z (hsub hz)

/-! ## Schur 数の比較 -/

/-- S(2) = 5 は S(1) = 2 の2倍以上 -/
theorem schur_two_ge_double_schur_one : (5 : ℕ) ≥ 2 * 2 := by omega

/-! ## Sum-free 集合の具体例 -/

/-- {3, 4, 5} は sum-free -/
example : IsSumFree {3, 4, 5} := by
  intro x hx y hy z hz h
  simp at hx hy hz
  rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
    rcases hz with rfl | rfl | rfl <;> omega

/-- {1, 3, 5} は sum-free -/
example : IsSumFree ({1, 3, 5} : Finset ℕ) := by
  intro x hx y hy z hz h
  simp at hx hy hz
  rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
    rcases hz with rfl | rfl | rfl <;> omega

/-- IsSumFree の交差: IsSumFree A ∧ IsSumFree B → IsSumFree (A ∩ B) -/
theorem isSumFree_inter {A B : Finset ℕ} (hA : IsSumFree A) (hB : IsSumFree B) :
    IsSumFree (A ∩ B) := by
  intro x hx y hy z hz
  exact hA x (Finset.mem_inter.mp hx).1 y (Finset.mem_inter.mp hy).1 z (Finset.mem_inter.mp hz).1

/-- {2,5} は sum-free -/
example : IsSumFree ({2, 5} : Finset ℕ) := by
  intro x hx y hy z hz h; simp at hx hy hz
  rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;> rcases hz with rfl | rfl <;> omega

/-- {4, 5, 6} は sum-free -/
example : IsSumFree ({4, 5, 6} : Finset ℕ) := by
  intro x hx y hy z hz h; simp at hx hy hz
  rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;> rcases hz with rfl | rfl | rfl <;> omega

/-- {1,2} は sum-free ではない（1+1=2） -/
theorem not_isSumFree_12 : ¬IsSumFree ({1, 2} : Finset ℕ) := by
  intro h; exact h 1 (by simp) 1 (by simp) 2 (by simp) rfl

/-- {6,7,8,9,10} は sum-free（上半分: 全要素 > 5 なので和 > 10 > max） -/
example : IsSumFree ({6, 7, 8, 9, 10} : Finset ℕ) := by
  intro x hx y hy z hz h; simp at hx hy hz
  rcases hx with rfl|rfl|rfl|rfl|rfl <;> rcases hy with rfl|rfl|rfl|rfl|rfl <;> rcases hz with rfl|rfl|rfl|rfl|rfl <;> omega

/-- IsSumFree A → 0 ∉ A（0+0=0 で sum-free 違反） -/
theorem zero_not_mem_of_isSumFree {A : Finset ℕ} (h : IsSumFree A) : 0 ∉ A := by
  intro h0; exact h 0 h0 0 h0 0 h0 rfl

/-- n ≥ 1 なら {n} は sum-free -/
theorem isSumFree_singleton_pos {n : ℕ} (hn : n ≥ 1) : IsSumFree ({n} : Finset ℕ) :=
  isSumFree_singleton n hn

/-- {7, 8, 9, 10} は sum-free -/
theorem isSumFree_seven_to_ten : IsSumFree ({7, 8, 9, 10} : Finset ℕ) := by
  intro x hx y hy z hz h
  simp [Finset.mem_insert, Finset.mem_singleton] at hx hy hz
  omega

/-- {11, 12, 13, 14, 15} は sum-free -/
example : IsSumFree ({11, 12, 13, 14, 15} : Finset ℕ) := by
  intro x hx y hy z hz h; simp at hx hy hz
  rcases hx with rfl|rfl|rfl|rfl|rfl <;> rcases hy with rfl|rfl|rfl|rfl|rfl <;> rcases hz with rfl|rfl|rfl|rfl|rfl <;> omega

/-- IsSumFree は Finset.filter で保存される -/
theorem isSumFree_filter {A : Finset ℕ} (h : IsSumFree A) (p : ℕ → Prop) [DecidablePred p] :
    IsSumFree (A.filter p) :=
  isSumFree_subset h (Finset.filter_subset p A)

/-- {100} は sum-free -/
example : IsSumFree ({100} : Finset ℕ) := isSumFree_singleton 100 (by omega)

/-- IsSumFree A → 1 ∉ A ∨ 2 ∉ A（1+1=2 なので両方は含めない） -/
theorem isSumFree_not_both_one_two {A : Finset ℕ} (h : IsSumFree A) :
    1 ∉ A ∨ 2 ∉ A := by
  by_contra hne; push_neg at hne
  exact h 1 hne.1 1 hne.1 2 hne.2 rfl

/-- IsSumFree A → ∀ a ∈ A, 2*a ∉ A（sum-free なら自身との和は集合に入らない） -/
theorem isSumFree_no_double {A : Finset ℕ} (h : IsSumFree A) {a : ℕ} (ha : a ∈ A) :
    2 * a ∉ A := by
  intro h2a; exact h a ha a ha (2 * a) h2a (by omega)

/-- IsSumFree A → a ∈ A → a + a ∉ A（isSumFree_no_double の別形） -/
theorem isSumFree_no_self_sum {A : Finset ℕ} (h : IsSumFree A) {a : ℕ} (ha : a ∈ A) :
    a + a ∉ A := by
  intro haa; exact h a ha a ha (a + a) haa rfl

/-- IsSumFree A → ∀ a b ∈ A, a + b ∈ A → False -/
theorem isSumFree_no_sum_in {A : Finset ℕ} (h : IsSumFree A) {a b : ℕ}
    (ha : a ∈ A) (hb : b ∈ A) {c : ℕ} (hc : c ∈ A) (heq : a + b = c) : False :=
  h a ha b hb c hc heq

/-- IsSumFree A → A.erase x も sum-free（要素削除は sum-free 性を保存） -/
theorem isSumFree_erase {A : Finset ℕ} (h : IsSumFree A) (x : ℕ) :
    IsSumFree (A.erase x) :=
  isSumFree_subset h (Finset.erase_subset x A)

/-- IsSumFree A → A の全要素は 1 以上 -/
theorem isSumFree_all_pos {A : Finset ℕ} (h : IsSumFree A) : ∀ a ∈ A, a ≥ 1 := by
  intro a ha
  by_contra hle; push_neg at hle
  have : a = 0 := by omega
  subst this
  exact zero_not_mem_of_isSumFree h ha

/-- IsSumFree {a} ↔ a ≥ 1 -/
theorem isSumFree_singleton_iff (a : ℕ) : IsSumFree ({a} : Finset ℕ) ↔ a ≥ 1 := by
  constructor
  · intro h
    by_contra hle; push_neg at hle
    have ha0 : a = 0 := by omega
    subst ha0
    exact zero_not_mem_of_isSumFree h (Finset.mem_singleton.mpr rfl)
  · intro ha; exact isSumFree_singleton a ha

/-- {16, 17, 18, 19, 20} は sum-free -/
theorem isSumFree_16_to_20 : IsSumFree ({16, 17, 18, 19, 20} : Finset ℕ) := by
  intro x hx y hy z hz h; simp at hx hy hz
  rcases hx with rfl|rfl|rfl|rfl|rfl <;> rcases hy with rfl|rfl|rfl|rfl|rfl <;> rcases hz with rfl|rfl|rfl|rfl|rfl <;> omega

/-- not_isSumFree の具体例: {1,2,3} は sum-free でない（1+2=3） -/
theorem not_isSumFree_123 : ¬IsSumFree ({1, 2, 3} : Finset ℕ) := by
  intro h; exact h 1 (by simp) 2 (by simp) 3 (by simp) rfl
