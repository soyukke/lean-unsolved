import Mathlib

/-!
# エルデシュ問題 #89: Distinct Distances（異なる距離問題）

## 問題
n個の平面上の点は ≫ n/√(log n) 個の異なる距離を決定するか？

## 背景
- √n × √n 整数格子が下界の最適性を示す
- Guth-Katz (2015) が ≫ n/log n を証明（現在の最良結果）
- 残りのギャップは log n と √(log n) の差

## 探索の概要

### 探索1: Python数値実験 (scripts/erdos89_distinct_distances.py)
- n=10~1000でランダム配置、整数格子、三角格子、六角格子を比較
- 整数格子が最小の異なる距離を持つ配置であることを確認
- d(grid) / (n/√logn) ≈ 1.1-1.3 で定数的
- ランダム配置はほぼ最大（≈ n(n-1)/2）

### 探索2: 数論的構造解析
- 整数格子の距離² = a² + b² → 2つの平方和で表せる数
- Landau-Ramanujan定理: S(x) ~ K·x/√(log x), K ≈ 0.7642
- 数値的に確認: 比率が1に収束
- 格子の異なる距離数は可能な2平方和の ≈72-88% を実現

### 探索3: Lean形式化（本ファイル）
- 問題の形式的定義
- 小さいケースでの検証
- 自明な補題の証明
-/

/-! ## 基本定義 -/

/-- 平面上の点（整数座標） -/
abbrev Point := ℤ × ℤ

/-- 2点間の距離の二乗 -/
def distSq (p q : Point) : ℤ :=
  (p.1 - q.1) ^ 2 + (p.2 - q.2) ^ 2

/-- 距離の二乗は非負 -/
theorem distSq_nonneg (p q : Point) : 0 ≤ distSq p q := by
  unfold distSq
  positivity

/-- 距離の二乗は対称 -/
theorem distSq_comm (p q : Point) : distSq p q = distSq q p := by
  unfold distSq
  ring

/-- 距離の二乗が0 ⟺ 同じ点 -/
theorem distSq_eq_zero_iff (p q : Point) : distSq p q = 0 ↔ p = q := by
  unfold distSq
  constructor
  · intro h
    have h1 : (p.1 - q.1) ^ 2 ≥ 0 := sq_nonneg _
    have h2 : (p.2 - q.2) ^ 2 ≥ 0 := sq_nonneg _
    have h3 : (p.1 - q.1) ^ 2 = 0 := by omega
    have h4 : (p.2 - q.2) ^ 2 = 0 := by omega
    rw [sq_eq_zero_iff, sub_eq_zero] at h3 h4
    exact Prod.ext h3 h4
  · intro h
    rw [h]
    simp

/-- 有限点集合の異なる距離の集合 -/
noncomputable def distinctDistSqSet (S : Finset Point) : Finset ℤ :=
  (S.product S).image (fun pq => distSq pq.1 pq.2) |>.filter (· > 0)

/-- 有限点集合の異なる距離の数 -/
noncomputable def numDistinctDist (S : Finset Point) : ℕ :=
  (distinctDistSqSet S).card

/-- エルデシュの異なる距離予想の形式的記述:
    n点の集合は Ω(n/√(log n)) 個の異なる距離を決定する -/
def ErdosDistinctDistConjecture : Prop :=
  ∃ c : ℝ, c > 0 ∧ ∀ n : ℕ, n ≥ 2 →
    ∀ S : Finset Point, S.card = n →
      (numDistinctDist S : ℝ) ≥ c * n / Real.sqrt (Real.log n)

/-! ## 小さいケースでの検証 -/

/-- 2点は少なくとも1つの異なる距離を持つ -/
theorem two_points_one_distance (p q : Point) (hne : p ≠ q) :
    distSq p q > 0 := by
  rw [show (0 : ℤ) = distSq p p from by simp [distSq]]
  unfold distSq
  have : ¬(p.1 - q.1 = 0 ∧ p.2 - q.2 = 0) := by
    intro ⟨h1, h2⟩
    apply hne
    exact Prod.ext (by omega) (by omega)
  rcases not_and_or.mp this with h | h
  · have : (p.1 - q.1) ^ 2 > 0 := by positivity
    have : (p.2 - q.2) ^ 2 ≥ 0 := sq_nonneg _
    have : (p.1 - p.1) ^ 2 = 0 := by ring
    have : (p.2 - p.2) ^ 2 = 0 := by ring
    nlinarith [sq_nonneg (p.1 - q.1), sq_nonneg (p.2 - q.2)]
  · have : (p.2 - q.2) ^ 2 > 0 := by positivity
    have : (p.1 - q.1) ^ 2 ≥ 0 := sq_nonneg _
    have : (p.1 - p.1) ^ 2 = 0 := by ring
    have : (p.2 - p.2) ^ 2 = 0 := by ring
    nlinarith [sq_nonneg (p.1 - q.1), sq_nonneg (p.2 - q.2)]

/-! ## 具体例での検証 -/

/-- 原点と (1,0) の距離の二乗は 1 -/
example : distSq (0, 0) (1, 0) = 1 := by decide

/-- 原点と (1,1) の距離の二乗は 2 -/
example : distSq (0, 0) (1, 1) = 2 := by decide

/-- 原点と (2,1) の距離の二乗は 5 -/
example : distSq (0, 0) (2, 1) = 5 := by decide

/-- 正三角形に近い3点: (0,0), (2,0), (1,1)
    距離²: 4, 2, 2 → 異なる距離は2つ -/
example : distSq (0, 0) (2, 0) = 4 := by decide
example : distSq (0, 0) (1, 1) = 2 := by decide
example : distSq (2, 0) (1, 1) = 2 := by decide

/-- 正方形の4頂点: (0,0), (1,0), (0,1), (1,1)
    距離²: 1,1,1,1,2,2 → 異なる距離は2つ（1と2） -/
example : distSq (0, 0) (1, 0) = 1 := by decide
example : distSq (0, 0) (0, 1) = 1 := by decide
example : distSq (0, 0) (1, 1) = 2 := by decide
example : distSq (1, 0) (0, 1) = 2 := by decide
example : distSq (1, 0) (1, 1) = 1 := by decide
example : distSq (0, 1) (1, 1) = 1 := by decide

/-! ## 2つの平方和に関する基本的な性質 -/

/-- 整数格子上の距離の二乗は2つの整数の二乗の和 -/
theorem distSq_is_sum_of_squares (p q : Point) :
    ∃ a b : ℤ, distSq p q = a ^ 2 + b ^ 2 :=
  ⟨p.1 - q.1, p.2 - q.2, rfl⟩

/-- 2つの平方和の積も2つの平方和（ブラーマグプタ–フィボナッチ恒等式）
    (a² + b²)(c² + d²) = (ac - bd)² + (ad + bc)² -/
theorem sum_sq_mul_sum_sq (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by
  ring

/-! ## 探索6: n ≥ 2 点では異なる距離が 1 以上 -/

/-- 異なる2点があれば距離集合は空でない -/
theorem distinctDistSqSet_nonempty_of_two_points {S : Finset Point}
    (hcard : S.card ≥ 2) :
    (distinctDistSqSet S).Nonempty := by
  -- card ≥ 2 から 2つの異なる要素を取る
  have hne : S.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro h; rw [h] at hcard; simp at hcard
  obtain ⟨p, hp⟩ := hne
  have hS' : (S.erase p).Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro h
    have : (S.erase p).card = S.card - 1 := Finset.card_erase_of_mem hp
    rw [h] at this; simp at this; omega
  obtain ⟨q, hq⟩ := hS'
  have hqS : q ∈ S := Finset.mem_of_mem_erase hq
  have hpq : p ≠ q := by
    intro h; subst h
    have := Finset.mem_erase.mp hq
    exact this.1 rfl
  -- distSq p q > 0
  have hdist : distSq p q > 0 := two_points_one_distance p q hpq
  -- distSq p q ∈ distinctDistSqSet S
  refine ⟨distSq p q, ?_⟩
  unfold distinctDistSqSet
  rw [Finset.mem_filter]
  constructor
  · rw [Finset.mem_image]
    exact ⟨(p, q), Finset.mem_product.mpr ⟨hp, hqS⟩, rfl⟩
  · exact hdist

/-- n ≥ 2 点の集合は少なくとも1つの異なる距離を持つ -/
theorem numDistinctDist_ge_one {S : Finset Point} (hcard : S.card ≥ 2) :
    numDistinctDist S ≥ 1 := by
  unfold numDistinctDist
  have h := distinctDistSqSet_nonempty_of_two_points hcard
  exact Finset.Nonempty.card_pos h

/-! ## 探索7: 共線点集合の異なる距離 -/

/-- 同一直線上の n 点（等間隔）は n-1 個の異なる距離を持つ
    形式的には: 点 (0,0), (1,0), ..., (n-1, 0) の距離集合 -/

-- 具体例: 3点 (0,0), (1,0), (2,0) の距離²は {1, 4} の2つ
example : distSq (0, 0) (1, 0) = 1 := by decide
example : distSq (0, 0) (2, 0) = 4 := by decide
example : distSq (1, 0) (2, 0) = 1 := by decide

-- 4点 (0,0), (1,0), (2,0), (3,0) の距離²は {1, 4, 9} の3つ
example : distSq (0, 0) (3, 0) = 9 := by decide
example : distSq (1, 0) (3, 0) = 4 := by decide
example : distSq (2, 0) (3, 0) = 1 := by decide

/-! ## 探索8: distSq の座標別分解と基本性質 -/

/-- 同一x座標の2点の距離の二乗は y差の二乗 -/
theorem distSq_same_x (y1 y2 : ℤ) :
    distSq (0, y1) (0, y2) = (y1 - y2) ^ 2 := by
  unfold distSq; ring

/-- 同一y座標の2点の距離の二乗は x差の二乗 -/
theorem distSq_same_y (x1 x2 : ℤ) :
    distSq (x1, 0) (x2, 0) = (x1 - x2) ^ 2 := by
  unfold distSq; ring

/-- 原点からの距離の二乗 -/
theorem distSq_origin (x y : ℤ) :
    distSq (0, 0) (x, y) = x ^ 2 + y ^ 2 := by
  unfold distSq; ring
