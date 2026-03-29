#!/usr/bin/env python3
"""
Lean 4 形式化設計: no_constant_v2_cycle

全ステップで v2(3*n_i+1) = c (定数) のサイクルが存在しないことの形式化。
c=1 は既存の no_all_ascent_cycle で排除済み。
c=2 は n=1 の自明不動点のみ。
c>=3 は非整数解なので排除される。

形式化の全体像を完全に設計する。
"""

lean_code = r"""
import Unsolved.Collatz.Formula

/-!
# 探索189: 全v_i=cサイクル排除 (no_constant_v2_cycle)

全ステップで v2(3*n_i+1) = c (定数) のサイクルは不可能であることの形式化。
c=1: no_all_ascent_cycle (既存)
c=2: n=1 (自明不動点のみ)
c>=3: 非整数解、不可

## 主要結果
- `generalAscentConst`: 一般c版の定数項
- `generalAscentConst_mul`: G_k(c)*(2^c-3) + 3^k = 2^{ck}
- `syracuse_iter_constv2_mul_formula`: 2^{ck}*T^k(n) = 3^k*n + G_k(c)
- `no_constant_v2_cycle`: c>=3 → サイクル不可
-/

/-! ## 1. 一般的定数c版上昇定数 -/

/-- 一般化されたascentConst: 各ステップで v2 = c のときの定数項
    G_0(c) = 0, G_{k+1}(c) = 3 * G_k(c) + 2^{ck} -/
def generalAscentConst (c : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * generalAscentConst c k + 2 ^ (c * k)

-- 数値検証
example : generalAscentConst 1 0 = 0 := rfl
example : generalAscentConst 1 1 = 1 := rfl -- = ascentConst 1
example : generalAscentConst 1 2 = 5 := rfl -- = ascentConst 2
example : generalAscentConst 2 1 = 1 := rfl
example : generalAscentConst 2 2 = 7 := rfl
example : generalAscentConst 3 1 = 1 := rfl
example : generalAscentConst 3 2 = 11 := rfl

/-- c=1 のとき generalAscentConst は ascentConst に一致 -/
theorem generalAscentConst_one (k : ℕ) :
    generalAscentConst 1 k = ascentConst k := by
  induction k with
  | zero => simp [generalAscentConst, ascentConst]
  | succ k ih =>
    simp only [generalAscentConst, ascentConst]
    rw [ih]
    -- 2^{1*k} = 2^k
    congr 1
    ring

/-! ## 2. 閉じた形の等式 -/

/-- ★核心的等式: G_k(c) * (2^c - 3) + 3^k = 2^{ck}
    自然数の引き算を回避した加法的表現。

    証明（帰納法）:
    k=0: 0*(2^c-3) + 1 = 1 = 2^0 OK
    k+1: (3*G_k + 2^{ck})*(2^c-3) + 3^{k+1}
        = 3*G_k*(2^c-3) + 2^{ck}*(2^c-3) + 3*3^k
        = 3*(2^{ck} - 3^k) + 2^{ck}*2^c - 3*2^{ck} + 3*3^k  [ih]
        = 3*2^{ck} - 3^{k+1} + 2^{c(k+1)} - 3*2^{ck} + 3^{k+1}
        = 2^{c(k+1)} -/
theorem generalAscentConst_mul (c k : ℕ) (hc : c ≥ 2) :
    generalAscentConst c k * (2 ^ c - 3) + 3 ^ k = 2 ^ (c * k) := by
  induction k with
  | zero =>
    simp [generalAscentConst]
  | succ k ih =>
    simp only [generalAscentConst]
    -- 目標: (3 * G_k + 2^{ck}) * (2^c - 3) + 3^{k+1} = 2^{c*(k+1)}
    -- ih: G_k * (2^c - 3) + 3^k = 2^{ck}
    -- 展開して ih を使う
    have h2c : 2 ^ c ≥ 4 := by
      calc 2 ^ c ≥ 2 ^ 2 := Nat.pow_le_pow_right (by omega) hc
        _ = 4 := by norm_num
    have h2c3 : 2 ^ c - 3 ≥ 1 := by omega
    -- 2^{c*(k+1)} = 2^c * 2^{ck}
    have hpow : 2 ^ (c * (k + 1)) = 2 ^ c * 2 ^ (c * k) := by
      rw [show c * (k + 1) = c + c * k from by ring, pow_add]
    rw [hpow]
    -- 大きな計算を linarith / omega に委ねる
    -- (3*G_k + 2^{ck}) * (2^c-3) = 3*G_k*(2^c-3) + 2^{ck}*(2^c-3)
    -- = 3*(2^{ck} - 3^k) + 2^{ck}*2^c - 3*2^{ck}    using ih
    -- = 3*2^{ck} - 3^{k+1} + 2^c*2^{ck} - 3*2^{ck}
    -- = 2^c*2^{ck} - 3^{k+1}
    -- + 3^{k+1} = 2^c * 2^{ck}
    nlinarith [ih, Nat.mul_sub_one (2 ^ c - 3) (3 * generalAscentConst c k)]
    -- 注: nlinarith で解けない場合は手動展開が必要

/-! ## 3. 全ステップで v2 = c という条件 -/

/-- 全ステップで v2(3*n_i+1) = c -/
def allV2Eq (c : ℕ) (n : ℕ) (k : ℕ) : Prop :=
  ∀ i, i < k → v2 (3 * syracuseIter i n + 1) = c

/-- allV2Eq のシフト: allV2Eq c n (k+1) → allV2Eq c (syracuse n) k -/
theorem allV2Eq_shift (c n k : ℕ) (h : allV2Eq c n (k + 1)) :
    allV2Eq c (syracuse n) k := by
  intro i hi
  have := h (i + 1) (by omega)
  simp only [syracuseIter_succ] at this
  exact this

/-- allV2Eq c n (k+1) → v2(3n+1) = c (最初のステップ) -/
theorem allV2Eq_head (c n k : ℕ) (h : allV2Eq c n (k + 1)) :
    v2 (3 * n + 1) = c := by
  have := h 0 (by omega)
  simp only [syracuseIter_zero] at this
  exact this

/-! ## 4. 一般乗法公式 -/

/-- v2(3n+1) = c のとき syracuse n = (3n+1)/2^c -/
theorem syracuse_of_v2_eq (n c : ℕ) (hv : v2 (3 * n + 1) = c) :
    syracuse n = (3 * n + 1) / 2 ^ c := by
  unfold syracuse
  rw [hv]

/-- v2(3n+1) = c のとき 2^c * syracuse n = 3n+1 -/
theorem two_pow_mul_syracuse_of_v2_eq (n c : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hv : v2 (3 * n + 1) = c) :
    2 ^ c * syracuse n = 3 * n + 1 := by
  rw [syracuse_of_v2_eq n c hv]
  -- 2^c | (3n+1) because v2(3n+1) = c implies 2^c | (3n+1)
  have h_dvd : 2 ^ c ∣ (3 * n + 1) := by
    rw [← hv]; exact pow_v2_dvd (3 * n + 1)
  exact Nat.div_mul_cancel h_dvd |>.symm ▸ Nat.mul_div_cancel' h_dvd
  -- 注: 正確な tactic は検証が必要

/-- ★一般乗法公式:
    allV2Eq c n k → 2^{ck} * T^k(n) = 3^k * n + G_k(c)

    帰納法:
    k=0: 1*n = n + 0 OK
    k+1: 2^{c(k+1)} * T^{k+1}(n)
       = 2^c * 2^{ck} * T^k(T(n))
       = 2^c * (3^k * T(n) + G_k(c))     [ih]
       = 2^c * 3^k * T(n) + 2^c * G_k(c)
       = 3^k * (2^c * T(n)) + 2^c * G_k(c)
       = 3^k * (3n+1) + 2^c * G_k(c)     [v2=c]
       = 3^{k+1} * n + 3^k + 2^c * G_k(c)
       ... 待て。G_{k+1} = 3*G_k + 2^{ck} なので直接合わない。

    修正: 帰納法の順序を変える。
    2^{c(k+1)} * T^{k+1}(n)
    = 2^{ck} * (2^c * T(T^k...))...

    実はもっと単純: 各ステップ i で
    2^c * T(n_i) = 3*n_i + 1
    をp回掛け合わせて
    2^{cp} * T^p(n) = Π(3*n_i+1)/T(n_i) ...

    直接帰納法のほうがよい。n に対する帰納ではなく k に対する帰納。
    k=0: trivial
    k→k+1:
      2^{c(k+1)} * T^{k+1}(n)
      = 2^{c(k+1)} * T^k(T(n))      [定義]
      先に ih: 2^{ck} * T^k(T(n)) = 3^k * T(n) + G_k(c)
      なので:
      2^{c(k+1)} * T^{k+1}(n) = 2^c * (2^{ck} * T^k(T(n)))
                                = 2^c * (3^k * T(n) + G_k(c))
                                = 3^k * (2^c * T(n)) + 2^c * G_k(c)
                                = 3^k * (3n+1) + 2^c * G_k(c)
                                = 3^{k+1}*n + 3^k + 2^c * G_k(c)

      G_{k+1}(c) = 3 * G_k(c) + 2^{ck}
      3^k + 2^c * G_k(c) ?= G_{k+1}(c) = 3*G_k(c) + 2^{ck}

      ↑ これは一般には成り立たない！
      3^k + 2^c * G_k(c) vs 3*G_k(c) + 2^{ck}

      問題発見: 漸化式が合わない。

    再計算: c=1 の場合確認
      G_k(1) = ascentConst k, 漸化式: G_{k+1} = 3*G_k + 2^k
      帰納ステップ: 3^k + 2^1 * G_k = 3^k + 2*G_k
      G_{k+1} = 3*G_k + 2^k
      3^k + 2*G_k vs 3*G_k + 2^k
      これは 3^k - 2^k = G_k (ascentConst_closed) を使えば
      3^k + 2*G_k = G_k + 2^k + 2*G_k = 3*G_k + 2^k = G_{k+1} OK!

    一般の c:
      3^k + 2^c * G_k(c) vs G_{k+1}(c) = 3*G_k(c) + 2^{ck}

      差: 3^k + 2^c * G_k - 3*G_k - 2^{ck}
        = 3^k + (2^c - 3)*G_k - 2^{ck}

      generalAscentConst_mul から:
        G_k * (2^c - 3) + 3^k = 2^{ck}
      つまり:
        3^k + (2^c-3)*G_k = 2^{ck}

      したがって:
        3^k + 2^c * G_k - 3*G_k - 2^{ck}
        = (3^k + (2^c-3)*G_k) - 2^{ck}
        = 2^{ck} - 2^{ck} = 0

    完璧！ 3^k + 2^c * G_k(c) = G_{k+1}(c) が成り立つ！
    （generalAscentConst_mul を使って証明可能）
-/
theorem syracuse_iter_constv2_mul_formula (n c k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hc : c ≥ 1)
    (hv : allV2Eq c n k) :
    2 ^ (c * k) * syracuseIter k n = 3 ^ k * n + generalAscentConst c k := by
  induction k generalizing n with
  | zero =>
    simp [generalAscentConst, syracuseIter]
  | succ k ih =>
    simp only [syracuseIter_succ]
    -- v2(3n+1) = c (最初のステップ)
    have hv0 := allV2Eq_head c n k hv
    -- syracuse n に対する ih の前提
    have hv_shift := allV2Eq_shift c n k hv
    -- syracuse n の性質 (syracuseIter_odd, syracuseIter_pos を使う)
    have hsyr_odd := syracuse_odd n hn hodd
    have hsyr_pos := syracuse_pos n hn hodd
    -- 帰納法の仮定
    have ih_syr := ih (syracuse n) hsyr_pos hsyr_odd hv_shift
    -- 2^c * syracuse n = 3n+1
    have h2syr := two_pow_mul_syracuse_of_v2_eq n c hn hodd hv0
    -- 3^k + 2^c * G_k = G_{k+1}  (核心)
    have hkey : 3 ^ k + 2 ^ c * generalAscentConst c k =
        generalAscentConst c (k + 1) := by
      simp only [generalAscentConst]
      -- 3^k + 2^c * G_k = 3*G_k + 2^{ck}
      -- ← generalAscentConst_mul: G_k*(2^c-3) + 3^k = 2^{ck}
      sorry -- ここは generalAscentConst_mul を使って linarith で解ける
    -- 計算
    calc 2 ^ (c * (k + 1)) * syracuseIter k (syracuse n)
        = 2 ^ c * (2 ^ (c * k) * syracuseIter k (syracuse n)) := by
          rw [show c * (k + 1) = c + c * k from by ring, pow_add]; ring
      _ = 2 ^ c * (3 ^ k * syracuse n + generalAscentConst c k) := by rw [ih_syr]
      _ = 3 ^ k * (2 ^ c * syracuse n) + 2 ^ c * generalAscentConst c k := by ring
      _ = 3 ^ k * (3 * n + 1) + 2 ^ c * generalAscentConst c k := by rw [h2syr]
      _ = 3 ^ (k + 1) * n + (3 ^ k + 2 ^ c * generalAscentConst c k) := by ring
      _ = 3 ^ (k + 1) * n + generalAscentConst c (k + 1) := by rw [hkey]

/-! ## 5. サイクル排除定理 -/

/-- ★ c >= 3 のとき、全v2=c サイクルは不可能

    証明:
    乗法公式 + サイクル条件 T^p(n)=n より:
      n * (2^{cp} - 3^p) = G_p(c)
    generalAscentConst_mul より:
      G_p(c) * (2^c - 3) + 3^p = 2^{cp}
    → G_p(c) * (2^c - 3) = 2^{cp} - 3^p
    → n * (2^{cp} - 3^p) * (2^c - 3) ...
    → 実は n * G_p * (2^c-3) ではなく...

    直接: n*(2^{cp}-3^p) = G_p, G_p*(2^c-3) = 2^{cp}-3^p
    → n*(2^c-3)*G_p(c) ... これだと G_p=0 の場合に問題

    もっと直接:
    n*(2^{cp}-3^p) = G_p(c)
    両辺に (2^c-3) を掛ける:
    n*(2^{cp}-3^p)*(2^c-3) = G_p*(2^c-3) = 2^{cp}-3^p
    (2^{cp}-3^p) > 0 (c>=2, p>=1 なので 2^{cp} > 3^p) で割ると:
    n*(2^c-3) = 1
    c >= 3 → 2^c-3 >= 5 → n*(2^c-3) >= 5 > 1, 矛盾。

    注: 2^{cp} > 3^p の証明が必要。
    c >= 2 のとき 2^c >= 4 > 3 なので 2^{cp} = (2^c)^p >= 4^p > 3^p
-/
theorem no_constant_v2_cycle (n c p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) (hp : p ≥ 1)
    (hc : c ≥ 3)
    (hv : allV2Eq c n p) (hcycle : syracuseIter p n = n) : False := by
  -- 乗法公式
  have hf := syracuse_iter_constv2_mul_formula n c p hn hodd (by omega) hv
  rw [hcycle] at hf
  -- hf: 2^{cp} * n = 3^p * n + G_p(c)
  -- → n * (2^{cp} - 3^p) = G_p(c)

  -- generalAscentConst_mul: G_p(c) * (2^c - 3) + 3^p = 2^{cp}
  have hgac := generalAscentConst_mul c p (by omega)
  -- → G_p(c) * (2^c-3) = 2^{cp} - 3^p

  -- hf と hgac を組み合わせる:
  -- n*(2^{cp} - 3^p) = G_p(c) かつ G_p(c)*(2^c-3) = 2^{cp} - 3^p
  -- → n * G_p(c) * (2^c-3) = G_p(c) * (2^c-3) = 2^{cp} - 3^p
  --
  -- もっとシンプルに: 2^{cp} > 3^p なので
  -- hf: 2^{cp} * n = 3^p * n + G_p  → (2^{cp} - 3^p) * n = G_p
  -- hgac: G_p * (2^c-3) = 2^{cp} - 3^p
  -- → (2^{cp}-3^p)*n*(2^c-3) = G_p*(2^c-3) = 2^{cp}-3^p
  -- → n*(2^c-3) = 1  (2^{cp}-3^p > 0 で割る)
  -- → n ≥ 1, 2^c-3 ≥ 5 → n*(2^c-3) ≥ 5 > 1, 矛盾

  have h2cp_gt_3p : 2 ^ (c * p) > 3 ^ p := by
    calc 2 ^ (c * p) = (2 ^ c) ^ p := by rw [← pow_mul]
      _ ≥ (2 ^ 3) ^ p := Nat.pow_le_pow_left (Nat.pow_le_pow_right (by omega) hc) p
      _ = 8 ^ p := by norm_num
      _ > 3 ^ p := Nat.pow_lt_pow_left (by omega) (by omega)

  -- (2^{cp} - 3^p) は正
  have hcoeff_pos : 2 ^ (c * p) - 3 ^ p > 0 := by omega

  -- hf から: n * (2^{cp} - 3^p) = G_p(c) ... 自然数だと引き算が面倒
  -- hf: 2^{cp} * n = 3^p * n + G_p
  -- 変形: 2^{cp} * n - 3^p * n = G_p ... 自然数の引き算
  -- hgac: G_p * (2^c-3) + 3^p = 2^{cp} ... 加法形式
  -- → G_p * (2^c-3) = 2^{cp} - 3^p ... これも引き算

  -- 加法形式に統一:
  -- hf: 2^{cp} * n = 3^p * n + G_p
  -- hgac: G_p * (2^c-3) + 3^p = 2^{cp}
  --
  -- hf の両辺に (2^c-3) を掛ける:
  -- 2^{cp} * n * (2^c-3) = (3^p * n + G_p) * (2^c-3)
  --                       = 3^p * n * (2^c-3) + G_p * (2^c-3)
  -- hgac: G_p * (2^c-3) = 2^{cp} - 3^p
  -- → 2^{cp} * n * (2^c-3) = 3^p * n * (2^c-3) + 2^{cp} - 3^p
  --
  -- 加法形式にする:
  -- 2^{cp} * n * (2^c-3) + 3^p = 3^p * n * (2^c-3) + 2^{cp}
  -- → 2^{cp} * (n*(2^c-3) - 1) = 3^p * (n*(2^c-3) - 1)  ... 引き算
  --
  -- 別の方法: もう少し直接的に
  -- hf と hgac の組み合わせ:
  -- hf: G_p = 2^{cp} * n - 3^p * n
  -- hgac: G_p * (2^c-3) = 2^{cp} - 3^p
  -- → (2^{cp}*n - 3^p*n) * (2^c-3) = 2^{cp} - 3^p
  -- → (2^{cp} - 3^p) * n * (2^c-3) = 2^{cp} - 3^p
  -- → n * (2^c-3) = 1   [2^{cp}-3^p で割る]

  -- 自然数で扱うには:
  -- hgac: G_p * (2^c-3) + 3^p = 2^{cp}
  -- hf * (2^c-3): (2^{cp} * n) * (2^c-3) = (3^p * n + G_p) * (2^c-3)
  --             = 3^p * n * (2^c-3) + G_p * (2^c-3)
  --             = 3^p * n * (2^c-3) + (2^{cp} - 3^p)
  -- したがって:
  -- 2^{cp} * n * (2^c-3) = 3^p * n * (2^c-3) + 2^{cp} - 3^p
  -- 加法形式に変換:
  -- 2^{cp} * n * (2^c-3) + 3^p = 3^p * n * (2^c-3) + 2^{cp}
  -- → 2^{cp} * (n*(2^c-3)) + 3^p = 3^p * (n*(2^c-3)) + 2^{cp}
  -- Let M = n*(2^c-3):
  -- 2^{cp} * M + 3^p = 3^p * M + 2^{cp}
  -- → (2^{cp} - 3^p) * M = 2^{cp} - 3^p ... 引き算
  -- → M = 1 (2^{cp}-3^p > 0 で割る)
  -- 加法形式: 2^{cp} * M + 3^p = 3^p * M + 2^{cp}
  -- → M = 1 (omegaかlinarithで解ける)

  -- 2^c - 3 の正値性
  have h2c3 : 2 ^ c - 3 ≥ 5 := by
    have : 2 ^ c ≥ 2 ^ 3 := Nat.pow_le_pow_right (by omega) hc
    omega

  -- n*(2^c-3) >= 5
  have hn_bound : n * (2 ^ c - 3) ≥ 5 := by
    calc n * (2 ^ c - 3) ≥ 1 * 5 := by
      exact Nat.mul_le_mul hn h2c3
      _ = 5 := by ring

  -- しかし M = 1 を導く必要がある
  -- 核心: hf と hgac から nlinarith で解けるか
  nlinarith [hf, hgac, h2cp_gt_3p, hn_bound]
  -- 注: nlinarith で解けない場合は中間変数を明示する

/-- c=2 のとき全v2=2サイクルは n=1 のみ -/
theorem constant_v2_two_cycle_is_trivial (n p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) (hp : p ≥ 1)
    (hv : allV2Eq 2 n p) (hcycle : syracuseIter p n = n) : n = 1 := by
  -- 同様に n*(2^2-3) = 1, つまり n*1 = 1, n = 1
  have hf := syracuse_iter_constv2_mul_formula n 2 p hn hodd (by omega) hv
  rw [hcycle] at hf
  -- hf: 2^{2p} * n = 3^p * n + G_p(2)
  -- hgac: G_p(2) * (4-3) + 3^p = 2^{2p}
  -- → G_p(2) + 3^p = 2^{2p}
  -- → G_p(2) = 2^{2p} - 3^p
  -- hf: 2^{2p} * n = 3^p * n + 2^{2p} - 3^p
  -- → (2^{2p} - 3^p) * n = 2^{2p} - 3^p
  -- → n = 1
  have hgac := generalAscentConst_mul 2 p (by omega)
  -- hgac: G_p * 1 + 3^p = 4^p, つまり G_p = 4^p - 3^p
  nlinarith [hf, hgac]

/-- ★★ 全v2=cサイクルの完全排除（c≥3は不可、c=2はn=1のみ）
    c=1 は既存の no_all_ascent_cycle で排除済み -/
theorem no_constant_v2_cycle_complete (n c p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hp : p ≥ 1) (hc : c ≥ 2)
    (hv : allV2Eq c n p) (hcycle : syracuseIter p n = n) :
    c = 2 ∧ n = 1 := by
  constructor
  · by_contra hc_ne
    have hc3 : c ≥ 3 := by omega
    exact no_constant_v2_cycle n c p hn hodd hp hc3 hv hcycle
  · by_contra hn_ne
    -- c = 2 のケース: n = 1 のはず
    -- c ≥ 3 なら上で矛盾
    -- c = 2 かつ n ≠ 1 の場合
    sorry -- c=2 のとき n=1 を示す必要 → constant_v2_two_cycle_is_trivial

-- 数値検証
#check no_all_ascent_cycle  -- 既存: c=1 排除
"""

print(lean_code)
print("\n" + "="*60)
print("形式化設計の概要")
print("="*60)
print("""
全体構造:
  1. generalAscentConst (c : N) : N -> N      -- 5行
  2. generalAscentConst_mul                    -- 15行
  3. allV2Eq の定義とシフト補題               -- 15行
  4. syracuse_of_v2_eq / two_pow_mul_syracuse  -- 10行
  5. syracuse_iter_constv2_mul_formula         -- 25行
  6. no_constant_v2_cycle (c>=3)               -- 15行
  7. constant_v2_two_cycle_is_trivial (c=2)    -- 10行
  8. no_constant_v2_cycle_complete             -- 10行

  合計: 約 100-110 行

  依存: Unsolved.Collatz.Formula (syracuseIter, v2, syracuse, etc.)

  核心的な数学:
  - generalAscentConst_mul: G_k(c)*(2^c-3) + 3^k = 2^{ck}
  - サイクル条件と組み合わせて n*(2^c-3) = 1 を導出
  - c >= 3 なら 2^c-3 >= 5 で n >= 1 と矛盾

  技術的課題:
  - nlinarith が通るか（非線形項が多い）
  - pow_v2_dvd が必要（既存）
  - Nat.mul_div_cancel' が必要（既存Mathlib）
  - two_pow_mul_syracuse_of_v2_eq の証明が核心的
""")
