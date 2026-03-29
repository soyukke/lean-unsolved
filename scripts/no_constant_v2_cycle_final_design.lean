/-
  ===================================================================
  探索189: no_constant_v2_cycle Lean 4 形式化設計 (読み取り専用)
  ===================================================================

  これは設計文書であり、実際のLeanコンパイルは意図していない。
  形式化の完全な構造、各定理の証明戦略、依存関係を記述する。

  ファイル配置: Unsolved/Collatz/ConstV2Cycle.lean (新規)
  import: Unsolved.Collatz.Formula (→ Hensel → Mod → Structure → Defs)
  推定行数: 110-130行
-/

-- ================================================================
-- ファイルヘッダ
-- ================================================================

-- import Unsolved.Collatz.Formula

/-!
# 全ステップ v2 定数サイクルの排除 (no_constant_v2_cycle)

Syracuse反復で全ステップ v2(3*n_i+1) = c (定数) のサイクルは
c=2, n=1 の自明な場合を除いて不可能であることを示す。

## 背景
- c=1: 既存の `no_all_ascent_cycle` で排除済み
- c=2: n=1 (syracuse 1 = 1) が唯一の不動点
- c>=3: サイクル方程式の解 n=1/(2^c-3) が非整数のため不可

## 主要結果
- `generalAscentConst`: 一般c版の定数項 G_k(c)
- `generalAscentConst_mul_add`: G_k(c)*(2^c-3) + 3^k = 2^{ck}
- `three_pow_add_mul_generalAscentConst`: 3^k + 2^c*G_k = G_{k+1}
- `syracuse_iter_constv2_mul_formula`: 2^{ck}*T^k(n) = 3^k*n + G_k(c)
- `no_constant_v2_cycle`: c>=3 のサイクル排除
- `constant_v2_two_cycle_trivial`: c=2 のサイクルは n=1 のみ
-/


-- ================================================================
-- Section 1: generalAscentConst (5行)
-- ================================================================

/-
/-- 一般化 ascentConst: 各ステップで v2 = c のときの定数項
    G_0(c) = 0, G_{k+1}(c) = 3 * G_k(c) + 2^{ck} -/
def generalAscentConst (c : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * generalAscentConst c k + 2 ^ (c * k)

-- 数値検証 (by rfl)
-- generalAscentConst 1 k = ascentConst k  (後で証明)
-- generalAscentConst 2 1 = 1, generalAscentConst 2 2 = 7
-- generalAscentConst 3 1 = 1, generalAscentConst 3 2 = 11
-/


-- ================================================================
-- Section 2: 閉じた形の等式 (15行)
-- ================================================================

/-
/-- ★核心的等式: G_k(c) * (2^c - 3) + 3^k = 2^{ck}   (c >= 2)

    証明（k に関する帰納法）:

    base case (k=0):
      0 * (2^c - 3) + 1 = 1 = 2^0  ← simp

    inductive step (k → k+1):
      仮定: G_k * (2^c-3) + 3^k = 2^{ck}
      目標: (3*G_k + 2^{ck}) * (2^c-3) + 3^{k+1} = 2^{c(k+1)}

      左辺 = 3*G_k*(2^c-3) + 2^{ck}*(2^c-3) + 3*3^k
           = 3*(2^{ck} - 3^k) + 2^{ck}*2^c - 3*2^{ck} + 3*3^k   [ih 使用]
           = 3*2^{ck} - 3^{k+1} + 2^{c(k+1)} - 3*2^{ck} + 3^{k+1}
           = 2^{c(k+1)}

      tactic: nlinarith [ih] after rewriting 2^{c*(k+1)} = 2^c * 2^{c*k}
      代替: linarith [ih] if we can prove intermediate steps
-/
theorem generalAscentConst_mul_add (c k : ℕ) (hc : c ≥ 2) :
    generalAscentConst c k * (2 ^ c - 3) + 3 ^ k = 2 ^ (c * k) := by
  induction k with
  | zero => simp [generalAscentConst]
  | succ k ih =>
    simp only [generalAscentConst]
    -- 2^{c*(k+1)} = 2^c * 2^{c*k}
    have hpow : 2 ^ (c * (k + 1)) = 2 ^ c * 2 ^ (c * k) := by
      rw [show c * (k + 1) = c + c * k from by ring, pow_add]
    rw [hpow]
    -- 2^c >= 4
    have h2c_ge : 2 ^ c ≥ 4 := by
      calc 2 ^ c ≥ 2 ^ 2 := Nat.pow_le_pow_right (by omega) hc
        _ = 4 := by norm_num
    -- ih: G_k * (2^c - 3) + 3^k = 2^{ck}
    -- 目標: (3 * G_k + 2^{ck}) * (2^c - 3) + 3 * 3^k = 2^c * 2^{ck}
    -- 展開: 3*G_k*(2^c-3) + 2^{ck}*(2^c-3) + 3*3^k
    -- ih より G_k*(2^c-3) = 2^{ck} - 3^k, so 3*G_k*(2^c-3) = 3*2^{ck} - 3^{k+1}
    -- = 3*2^{ck} - 3^{k+1} + 2^{ck}*2^c - 3*2^{ck} + 3^{k+1}
    -- = 2^{ck}*2^c = 2^c * 2^{ck}
    nlinarith [ih, h2c_ge,
               Nat.mul_sub_one (generalAscentConst c k) (2 ^ c - 3)]
    -- 注: nlinarith が通らない場合は手動展開:
    -- have h1 : generalAscentConst c k * (2 ^ c - 3) = 2 ^ (c * k) - 3 ^ k := by omega
    -- ... 自然数の引き算に注意
-/


-- ================================================================
-- Section 3: 帰納ステップの核心補題 (10行)
-- ================================================================

/-
/-- 帰納ステップの核心: 3^k + 2^c * G_k(c) = G_{k+1}(c)
    generalAscentConst_mul_add から導出。

    G_{k+1} = 3*G_k + 2^{ck}
    3^k + 2^c*G_k = 3^k + 2^c*G_k
    generalAscentConst_mul_add: G_k*(2^c-3) + 3^k = 2^{ck}
    つまり 3^k = 2^{ck} - G_k*(2^c-3) = 2^{ck} - 2^c*G_k + 3*G_k
    → 3^k + 2^c*G_k = 2^{ck} + 3*G_k = G_{k+1} -/
theorem three_pow_add_mul_generalAscentConst (c k : ℕ) (hc : c ≥ 2) :
    3 ^ k + 2 ^ c * generalAscentConst c k = generalAscentConst c (k + 1) := by
  simp only [generalAscentConst]
  -- 目標: 3^k + 2^c * G_k = 3*G_k + 2^{ck}
  have := generalAscentConst_mul_add c k hc
  -- this: G_k*(2^c-3) + 3^k = 2^{ck}
  -- 2^c >= 4 > 3
  have h2c_ge : 2 ^ c ≥ 4 := by
    calc 2 ^ c ≥ 2 ^ 2 := Nat.pow_le_pow_right (by omega) hc
      _ = 4 := by norm_num
  -- G_k*(2^c-3) = 2^c*G_k - 3*G_k  (自然数の引き算に注意)
  -- 3^k = 2^{ck} - G_k*(2^c-3) = 2^{ck} - 2^c*G_k + 3*G_k
  nlinarith
-/


-- ================================================================
-- Section 4: allV2Eq の定義とシフト補題 (15行)
-- ================================================================

/-
/-- 全ステップで v2(3*n_i+1) = c -/
def allV2Eq (c : ℕ) (n : ℕ) (k : ℕ) : Prop :=
  ∀ i, i < k → v2 (3 * syracuseIter i n + 1) = c

/-- allV2Eq のシフト -/
theorem allV2Eq_shift (c n k : ℕ) (h : allV2Eq c n (k + 1)) :
    allV2Eq c (syracuse n) k := by
  intro i hi
  have := h (i + 1) (by omega)
  simp only [syracuseIter_succ] at this
  exact this

/-- allV2Eq の先頭取り出し -/
theorem allV2Eq_head (c n k : ℕ) (h : allV2Eq c n (k + 1)) :
    v2 (3 * n + 1) = c := by
  have := h 0 (by omega)
  simp only [syracuseIter_zero] at this
  exact this
-/


-- ================================================================
-- Section 5: v2 = c のときの Syracuse (10行)
-- ================================================================

/-
/-- v2(3n+1) = c のとき 2^c * syracuse n = 3n+1

    証明:
    syracuse n = (3n+1) / 2^{v2(3n+1)}
    v2(3n+1) = c なので syracuse n = (3n+1) / 2^c
    2^c ∣ (3n+1) (v2 の定義から)
    Nat.mul_div_cancel' で等式を得る。-/
theorem two_pow_mul_syracuse_of_v2_eq (n c : ℕ)
    (hv : v2 (3 * n + 1) = c) :
    2 ^ c * syracuse n = 3 * n + 1 := by
  have hdvd : 2 ^ c ∣ (3 * n + 1) := by
    rw [← hv]; exact two_pow_v2_dvd (3 * n + 1)
  change 2 ^ c * ((3 * n + 1) / 2 ^ v2 (3 * n + 1)) = 3 * n + 1
  rw [hv]
  exact Nat.mul_div_cancel' hdvd
  -- 注: mul_comm が必要かも: Nat.div_mul_cancel hdvd の左右を swap
-/


-- ================================================================
-- Section 6: 一般乗法公式 (25行)
-- ================================================================

/-
/-- ★一般乗法公式:
    allV2Eq c n k, n>=1, n odd → 2^{ck} * T^k(n) = 3^k * n + G_k(c)

    帰納法（kに関して、nは一般化）:

    k=0: 1*n = n + 0  ← simp

    k→k+1:
      allV2Eq c n (k+1) から:
        v2(3n+1) = c  [allV2Eq_head]
        allV2Eq c (syracuse n) k  [allV2Eq_shift]

      ih: 2^{ck} * T^k(T(n)) = 3^k * T(n) + G_k(c)

      2^{c(k+1)} * T^{k+1}(n)
      = 2^c * 2^{ck} * T^k(T(n))              [pow_add]
      = 2^c * (3^k * T(n) + G_k(c))           [ih]
      = 3^k * (2^c * T(n)) + 2^c * G_k(c)     [ring]
      = 3^k * (3n+1) + 2^c * G_k(c)           [two_pow_mul_syracuse_of_v2_eq]
      = 3^{k+1}*n + 3^k + 2^c*G_k(c)         [ring]
      = 3^{k+1}*n + G_{k+1}(c)                [three_pow_add_mul_generalAscentConst]
-/
theorem syracuse_iter_constv2_mul_formula (n c k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hc : c ≥ 1)
    (hv : allV2Eq c n k) :
    2 ^ (c * k) * syracuseIter k n = 3 ^ k * n + generalAscentConst c k := by
  induction k generalizing n with
  | zero => simp [generalAscentConst, syracuseIter]
  | succ k ih =>
    simp only [syracuseIter_succ]
    have hv0 := allV2Eq_head c n k hv
    have hv_shift := allV2Eq_shift c n k hv
    have hsyr_odd := syracuse_odd n hn hodd
    have hsyr_pos := syracuse_pos n hn hodd
    have ih_syr := ih (syracuse n) hsyr_pos hsyr_odd hv_shift
    have h2syr := two_pow_mul_syracuse_of_v2_eq n c hv0
    -- hc >= 2 が必要（three_pow_add_mul_generalAscentConst用）
    -- c = 1 の場合は別途処理するか、hc >= 2 のみとする
    -- 実は hc >= 1 でも three_pow_add_mul が成り立つか？
    -- c=1: 3^k + 2*G_k(1) = G_{k+1}(1) = ascentConst(k+1)
    --   ascentConst(k+1) = 3*ascentConst(k) + 2^k
    --   3^k + 2*ascentConst(k) = 3*ascentConst(k) + 2^k
    --   → 3^k - 2^k = ascentConst(k) (= ascentConst_closed)
    --   → 3^k + 2*ascentConst(k) = ascentConst(k) + 2^k + 2*ascentConst(k)
    --     = 3*ascentConst(k) + 2^k ✓
    -- → c=1でも成り立つ！ただし証明が generalAscentConst_mul_add に依存し、
    --   c >= 2 を仮定しているため、c=1 用の別補題が必要。
    -- → 形式化では hc >= 2 として、c=1は既存 syracuse_iter_mul_formula に委ねる
    sorry -- calc で上記の計算を実行
-/


-- ================================================================
-- Section 7: サイクル排除 (c >= 3) (20行)
-- ================================================================

/-
/-- ★ c >= 3 のとき全v2=cサイクルは不可能

    前提: T^p(n) = n, allV2Eq c n p, n>=1, n odd, p>=1, c>=3

    証明:
    1. 乗法公式: 2^{cp} * n = 3^p * n + G_p(c)     [syracuse_iter_constv2_mul_formula]
    2. 閉じた形: G_p(c) * (2^c-3) + 3^p = 2^{cp}   [generalAscentConst_mul_add]

    これらを加法形式で組み合わせる:
    (1) の両辺に (2^c-3) を掛ける:
      2^{cp} * n * (2^c-3) = 3^p * n * (2^c-3) + G_p * (2^c-3)
                            = 3^p * n * (2^c-3) + (2^{cp} - 3^p)  [(2)から]

    加法形式: 2^{cp} * n * (2^c-3) + 3^p = 3^p * n * (2^c-3) + 2^{cp}

    設 M = n * (2^c-3):
      2^{cp} * M + 3^p = 3^p * M + 2^{cp}

    M = 1 ← 等式から必然 (2^{cp} ≠ 3^p なので M=1 が唯一解)

    しかし c >= 3 → 2^c-3 >= 5 → M = n*(2^c-3) >= 1*5 = 5 > 1

    矛盾。-/
theorem no_constant_v2_cycle (n c p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) (hp : p ≥ 1)
    (hc : c ≥ 3)
    (hv : allV2Eq c n p) (hcycle : syracuseIter p n = n) : False := by
  have hf := syracuse_iter_constv2_mul_formula n c p hn hodd (by omega) hv
  rw [hcycle] at hf
  -- hf: 2^{cp} * n = 3^p * n + G_p
  have hgac := generalAscentConst_mul_add c p (by omega)
  -- hgac: G_p * (2^c-3) + 3^p = 2^{cp}

  -- 2^c - 3 >= 5
  have h2c3 : 2 ^ c - 3 ≥ 5 := by
    have : 2 ^ c ≥ 2 ^ 3 := Nat.pow_le_pow_right (by omega) hc
    omega

  -- hf * (2^c-3) + 3^p の計算:
  -- 2^{cp} * n * (2^c-3) + 3^p = (3^p * n + G_p) * (2^c-3) + 3^p
  -- = 3^p * n * (2^c-3) + G_p * (2^c-3) + 3^p
  -- = 3^p * n * (2^c-3) + 2^{cp}   [hgac]
  --
  -- つまり: 2^{cp} * (n*(2^c-3)) + 3^p = 3^p * (n*(2^c-3)) + 2^{cp}
  -- n*(2^c-3) >= 5 なので LHS >= 5*2^{cp} + 3^p
  -- RHS = 5*3^p + 2^{cp} (n*(2^c-3)=5の場合)
  -- 2^{cp} > 3^p (c>=3, p>=1) なので
  -- 5*2^{cp} + 3^p > 5*3^p + 2^{cp} (4*2^{cp} > 4*3^p)
  -- → LHS > RHS, 矛盾（等式のはずなのに）

  -- 実際の証明は nlinarith で:
  have hmul := Nat.mul_le_mul_right (2 ^ c - 3) (show 2 ^ (c * p) * n = 3 ^ p * n + generalAscentConst c p from hf)
  -- ... 複雑なので段階的に:

  -- Step 1: n*(2^c-3) >= 5
  have hM : n * (2 ^ c - 3) ≥ 5 := Nat.le_of_eq (by omega) |>.trans (Nat.mul_le_mul hn h2c3)

  -- Step 2: 2^{cp} > 3^p
  have h2cp_gt : 2 ^ (c * p) > 3 ^ p := by
    calc 2 ^ (c * p) = (2 ^ c) ^ p := by rw [← pow_mul]
      _ ≥ 8 ^ p := by exact Nat.pow_le_pow_left (by omega : 2 ^ c ≥ 8) p
      _ > 3 ^ p := Nat.pow_lt_pow_left (by omega) (by omega)

  -- Step 3: nlinarith で矛盾
  nlinarith [hf, hgac, hM, h2cp_gt, mul_comm n (2 ^ c - 3)]

  -- 注: nlinarith が通らない場合の代替戦略:
  --   have h_eq : 2^{cp} * (n*(2^c-3)) + 3^p = 3^p * (n*(2^c-3)) + 2^{cp} := by nlinarith
  --   have : n * (2^c-3) = 1 := by nlinarith [h2cp_gt]
  --   omega  -- n*(2^c-3) >= 5 > 1 で矛盾
-/


-- ================================================================
-- Section 8: c=2 のサイクルは n=1 (10行)
-- ================================================================

/-
/-- c=2 で全v2=2サイクルなら n=1

    2^c-3 = 1 なので n*(2^c-3) = n*1 = n = 1 -/
theorem constant_v2_two_cycle_trivial (n p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) (hp : p ≥ 1)
    (hv : allV2Eq 2 n p) (hcycle : syracuseIter p n = n) : n = 1 := by
  have hf := syracuse_iter_constv2_mul_formula n 2 p hn hodd (by omega) hv
  rw [hcycle] at hf
  -- hf: 4^p * n = 3^p * n + G_p(2)
  have hgac := generalAscentConst_mul_add 2 p (by omega)
  -- hgac: G_p(2) * 1 + 3^p = 4^p, つまり G_p = 4^p - 3^p
  -- hf: 4^p * n = 3^p * n + (4^p - 3^p)
  -- → (4^p - 3^p) * n = 4^p - 3^p
  -- → n = 1
  -- 自然数: 4^p * n = 3^p * n + G_p, G_p + 3^p = 4^p
  -- → 4^p * n = 3^p * n + 4^p - 3^p
  -- 加法: 4^p * n + 3^p = 3^p * n + 4^p
  -- → 4^p * (n-1) = 3^p * (n-1)  (n >= 1)
  -- → n = 1  (4^p ≠ 3^p)
  nlinarith [hf, hgac, show 4 ^ p > 3 ^ p from Nat.pow_lt_pow_left (by omega) (by omega)]
-/


-- ================================================================
-- Section 9: 統合定理 (10行)
-- ================================================================

/-
/-- ★★ 統合: c>=2 の全v2=cサイクルは c=2∧n=1 のみ -/
theorem no_constant_v2_cycle_complete (n c p : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hp : p ≥ 1) (hc : c ≥ 2)
    (hv : allV2Eq c n p) (hcycle : syracuseIter p n = n) :
    c = 2 ∧ n = 1 := by
  by_cases hc3 : c ≥ 3
  · -- c >= 3: 矛盾
    exact absurd (no_constant_v2_cycle n c p hn hodd hp hc3 hv hcycle) (not_false)
  · -- c = 2
    have hceq : c = 2 := by omega
    subst hceq
    exact ⟨rfl, constant_v2_two_cycle_trivial n p hn hodd hp hv hcycle⟩
-/


-- ================================================================
-- 依存関係まとめ
-- ================================================================

/-
既存定理（直接使用）:
  - syracuseIter_zero, syracuseIter_succ       [Defs.lean]
  - syracuse_odd, syracuse_pos                  [Structure.lean]
  - two_pow_v2_dvd                              [Structure.lean]
  - Nat.mul_div_cancel'                         [Mathlib]
  - Nat.pow_le_pow_right, Nat.pow_lt_pow_left   [Mathlib]

既存定理（間接使用、Formula.lean 経由）:
  - ascentConst, ascentConst_add_two_pow        [Formula.lean]
  - syracuse_iter_mul_formula                   [Formula.lean]
  - no_all_ascent_cycle                         [Formula.lean]

新規定義:
  - generalAscentConst (c : ℕ) : ℕ → ℕ
  - allV2Eq (c n k : ℕ) : Prop

新規定理 (8個):
  1. generalAscentConst_mul_add
  2. three_pow_add_mul_generalAscentConst
  3. allV2Eq_shift
  4. allV2Eq_head
  5. two_pow_mul_syracuse_of_v2_eq
  6. syracuse_iter_constv2_mul_formula
  7. no_constant_v2_cycle
  8. constant_v2_two_cycle_trivial
  9. no_constant_v2_cycle_complete

技術的リスク:
  - 中: nlinarith が非線形項（2^{cp}, 3^p, n*(2^c-3)）の積を扱えるか
    → 解決策: 中間変数を have で明示的に束縛
  - 低: 自然数の引き算問題
    → 解決策: 加法形式で一貫
  - 低: 乗法公式の帰納ステップ
    → 解決策: three_pow_add_mul_generalAscentConst を事前に証明
-/
