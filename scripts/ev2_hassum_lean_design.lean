/-!
# E[v₂] = 2 の HasSum 形式化: 完全設計書

## 目標
  HasSum (fun n : ℕ => ((n + 1 : ℝ) / 2 ^ (n + 1))) 2

  数学的意味: Σ_{j=1}^∞ j / 2^j = 2

## ファイル名: Unsolved/Collatz/ExpectedV2.lean
## import: import Mathlib

## 必要な Mathlib API (全て存在確認済み)

  1. hasSum_iff_tendsto_nat_of_nonneg
     場所: Mathlib.Topology.Algebra.InfiniteSum.ENNReal
     型: {f : ℕ → ℝ} → (∀ i, 0 ≤ f i) → (r : ℝ) →
         (HasSum f r ↔ Tendsto (fun n => Σ i ∈ range n, f i) atTop (nhds r))

  2. tendsto_self_mul_const_pow_of_lt_one
     場所: Mathlib.Analysis.SpecificLimits.Normed
     型: {r : ℝ} → 0 ≤ r → r < 1 →
         Tendsto (fun n => ↑n * r ^ n) atTop (nhds 0)

  3. tendsto_pow_atTop_nhds_zero_of_lt_one
     場所: Mathlib.Analysis.SpecificLimits.Basic
     型: 0 ≤ r → r < 1 → Tendsto (fun n => r ^ n) atTop (nhds 0)

  4. tendsto_const_nhds.sub : 定数からの引き算の Tendsto
  5. Tendsto.add : Tendsto の和
  6. Tendsto.const_mul : 定数倍の Tendsto
  7. Finset.sum_range_succ : 部分和の展開
  8. field_simp, ring : 代数的整理
  9. positivity : 非負性

## 推定総行数: 60-90行 (コメント除く)
-/

import Mathlib

noncomputable section

open Finset Filter Topology

/-! ============================================================
    Section 1: 有限部分和公式 (Thm B)  [推定: 15-20行]
    ============================================================ -/

/-- 有限部分和公式:
    Σ_{j ∈ range K} (j+1)/2^{j+1} = 2 - (K+2)/2^K

  帰納法:
  - Base (K=0): 0 = 2 - 2/1 = 0
  - Step: field_simp + ring -/
theorem partial_sum_ev2 (K : ℕ) :
    ∑ j in range K, ((j + 1 : ℝ) / 2 ^ (j + 1)) = 2 - (↑K + 2) / 2 ^ K := by
  induction K with
  | zero => simp
  | succ K ih =>
    rw [sum_range_succ, ih]
    have h2K : (2 : ℝ) ^ K ≠ 0 := pow_ne_zero K two_ne_zero
    have h2K1 : (2 : ℝ) ^ (K + 1) ≠ 0 := pow_ne_zero (K + 1) two_ne_zero
    -- 代数的計算: 2 - (K+2)/2^K + (K+2)/2^{K+1} = 2 - (K+3)/2^{K+1}
    -- ここでの K+2 は Lean では ↑K + 2 (ℝへのキャスト)
    field_simp
    ring

/-! ============================================================
    Section 2: 余項の収束 (K+2)/2^K → 0  [推定: 15-25行]
    ============================================================ -/

/-- 余項 (↑K + 2) / 2^K → 0

  分解: (↑K + 2) / 2^K = ↑K * (1/2)^K + 2 * (1/2)^K

  各項の収束:
  - ↑K * (1/2)^K → 0 by tendsto_self_mul_const_pow_of_lt_one
  - 2 * (1/2)^K → 0 by tendsto_pow_atTop_nhds_zero_of_lt_one + const_mul -/
theorem tendsto_remainder_ev2 :
    Tendsto (fun K : ℕ => (↑K + 2 : ℝ) / 2 ^ K) atTop (nhds 0) := by
  -- (K+2)/2^K を K*(1/2)^K + 2*(1/2)^K に分解
  have key : ∀ K : ℕ, (↑K + 2 : ℝ) / 2 ^ K = ↑K * (1/2)^K + 2 * (1/2)^K := by
    intro K
    rw [one_div, inv_pow, div_eq_mul_inv]
    ring
  simp_rw [key]
  -- 和の極限 = 極限の和
  have h1 : Tendsto (fun K : ℕ => (↑K : ℝ) * (1/2)^K) atTop (nhds 0) :=
    tendsto_self_mul_const_pow_of_lt_one (by norm_num) (by norm_num)
  have h2 : Tendsto (fun K : ℕ => (2 : ℝ) * (1/2)^K) atTop (nhds 0) := by
    have := (tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num : (0:ℝ) ≤ 1/2) (by norm_num : (1:ℝ)/2 < 1)).const_mul 2
    simp at this
    exact this
  have : (0 : ℝ) = 0 + 0 := by ring
  rw [this]
  exact h1.add h2

/-! ============================================================
    Section 3: HasSum 本体 (Thm C)  [推定: 10-15行]
    ============================================================ -/

/-- E[v₂] = 2: 級数 Σ_{n=0}^∞ (n+1)/2^{n+1} は 2 に収束する

  証明:
  1. hasSum_iff_tendsto_nat_of_nonneg で部分和の収束に帰着
  2. partial_sum_ev2 で部分和 = 2 - (K+2)/2^K に変換
  3. tendsto_remainder_ev2 で (K+2)/2^K → 0
  4. よって部分和 → 2 - 0 = 2 -/
theorem hasSum_ev2 :
    HasSum (fun n : ℕ => ((↑n + 1 : ℝ) / 2 ^ (n + 1))) 2 := by
  rw [hasSum_iff_tendsto_nat_of_nonneg (fun i => by positivity) 2]
  simp_rw [partial_sum_ev2]
  -- goal: Tendsto (fun K => 2 - (↑K + 2)/2^K) atTop (nhds 2)
  conv_rhs => rw [show (2 : ℝ) = 2 - 0 from by ring]
  exact tendsto_const_nhds.sub tendsto_remainder_ev2

/-! ============================================================
    系: tsum 版
    ============================================================ -/

/-- tsum 版: Σ (n+1)/2^{n+1} = 2 -/
theorem tsum_ev2 : ∑' n : ℕ, ((↑n + 1 : ℝ) / 2 ^ (n + 1)) = 2 :=
  hasSum_ev2.tsum_eq

/-! ============================================================
    将来の拡張: v₂ の確率分布との接続

    奇数 n が [1, 2^{K+1}) で一様ランダムに選ばれたとき:
    Pr[v₂(3n+1) = j] ≈ 1/2^j  (j ≥ 1)

    これは既存の v2_of_mod8_eq* と合わせて示せる。
    具体的には:
    - n ≡ 1 (mod 4) → v₂(3n+1) ≥ 2  (確率 1/2)
    - n ≡ 3 (mod 4) → v₂(3n+1) = 1  (確�� 1/2)
    - n ≡ 1 (mod 8) → v₂(3n+1) = 2  (確率 1/4)
    - n ≡ 5 (mod 8) → v₂(3n+1) ≥ 3  (確率 1/4)

    一般パターン:
    n ≡ 2^j - 1 (mod 2^{j+1}) → v₂(3n+1) = j (for certain j)
    このパターンは Hensel.lean の hensel_attrition_k* と対応
    ============================================================ -/

end
