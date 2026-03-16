import Unsolved.CollatzHensel

/-!
# コラッツ予想 探索14: 「上昇+下降」1サイクルの縮小率

Syracuse 関数の「上昇フェーズ→下降」をまとめた加速版を形式化する。

## アイデア

通常の Syracuse は1ステップずつだが、連続上昇+1回下降をまとめて
1サイクルとして扱うことで、縮小率の明示的な上界を得る。

## 主要結果

### 即時下降 (n ≡ 1 mod 4)
- `immediate_descent_bound`: T(n) ≤ (3n+1)/4

### 1回上昇+1回下降 (n ≡ 3 mod 8)
- `one_ascent_bound`: T²(n) ≤ (9n+5)/8

### 2回上昇+1回下降 (n ≡ 7 mod 16)
- `two_ascent_bound`: T³(n) ≤ (27n+19)/16

### 加速 Syracuse 関数
- `firstDescent`: fuel パターンで最初の下降までの反復を計算
- `firstDescentValue`: 下降した結果の値を返す

### 縮小率の分析
- 即時下降: ≈ 3n/4 (比率 3/4 < 1、縮小)
- 1回上昇+下降: ≈ 9n/8 (比率 9/8 > 1、膨張)
- 2回上昇+下降: ≈ 27n/16 (比率 27/16 > 1、膨張)
- 一般に k回上昇+下降: ≈ 3^{k+1}n/2^{2(k+1)}
- 幾何平均を取ると ≈ 3/4 < 1 (Tao の結果の基盤)
-/

/-! ## 1. 即時下降の上界 -/

/-- n ≡ 1 (mod 4) かつ n > 1 → syracuse n ≤ (3*n+1)/4
    （CollatzStructure からの再エクスポート） -/
theorem immediate_descent_bound (n : ℕ) (h : n % 4 = 1) (hn : n > 1) :
    syracuse n ≤ (3 * n + 1) / 4 :=
  syracuse_le_of_mod4_eq1 n h hn

/-! ## 2. 1回上昇 + 1回下降 (n ≡ 3 mod 8) -/

/-- n ≡ 3 (mod 8) のとき (3n+1)/2 は割り切れて 3n+1 = 2*((3n+1)/2) -/
theorem three_mul_add_one_div2_exact (n : ℕ) (h : n % 8 = 3) :
    2 * ((3 * n + 1) / 2) = 3 * n + 1 := by
  omega

/-- n ≡ 3 (mod 8) のとき T²(n) ≤ (9*n+5)/8.
    注意: 等式は一般には成り立たない。
    n=3 のとき T(3)=5, 3*5+1=16, v2(16)=4 なので T²(3)=1 だが (9*3+5)/8=4。
    v2 が 2 より大きくなりうるため不等式のみが成立する。 -/
theorem one_ascent_bound (n : ℕ) (h : n % 8 = 3) :
    syracuse (syracuse n) ≤ (9 * n + 5) / 8 := by
  -- T(n) = (3n+1)/2, T²(n) ≤ (3*T(n)+1)/4
  have hmod4 : n % 4 = 3 := by omega
  have hT1 : syracuse n = (3 * n + 1) / 2 := syracuse_mod4_eq3 n hmod4
  have hT1_mod4 : syracuse n % 4 = 1 := syracuse_mod4_eq1_of_mod8_eq3 n h
  have hT1_gt1 : syracuse n > 1 := syracuse_gt_one_of_mod8_eq3 n h
  have hT2_le : syracuse (syracuse n) ≤ (3 * syracuse n + 1) / 4 :=
    syracuse_le_of_mod4_eq1 (syracuse n) hT1_mod4 hT1_gt1
  -- Rewrite syracuse n in both the hypothesis and the goal
  rw [hT1] at hT2_le ⊢
  -- Now goal is: syracuse ((3*n+1)/2) ≤ (9*n+5)/8
  -- hT2_le: syracuse ((3*n+1)/2) ≤ (3*((3*n+1)/2)+1)/4
  -- And (3*((3*n+1)/2)+1)/4 = (9*n+5)/8 by omega
  have h_rhs_eq : (3 * ((3 * n + 1) / 2) + 1) / 4 = (9 * n + 5) / 8 := by omega
  omega

/-! ## 3. 2回上昇 + 1回下降 (n ≡ 7 mod 16) -/

/-- n ≡ 7 (mod 16) のとき T²(n) ≡ 1 (mod 4) (2ステップ後に下降) -/
theorem two_ascent_T2_mod4 (n : ℕ) (h : n % 16 = 7) :
    syracuse (syracuse n) % 4 = 1 :=
  syracuse2_mod4_of_mod16_eq7 n h

/-- n ≡ 7 (mod 16) のとき T²(n) > 1 -/
theorem two_ascent_T2_gt1 (n : ℕ) (h : n % 16 = 7) :
    syracuse (syracuse n) > 1 := by
  rw [syracuse2_of_mod8_eq7 n (by omega)]
  omega

/-- n ≡ 7 (mod 16) のとき T³(n) ≤ (27*n+19)/16 -/
theorem two_ascent_bound (n : ℕ) (h : n % 16 = 7) :
    syracuse (syracuse (syracuse n)) ≤ (27 * n + 19) / 16 := by
  -- T²(n) ≡ 1 (mod 4) and T²(n) > 1, so T³(n) ≤ (3*T²(n)+1)/4
  have hT2_mod4 := two_ascent_T2_mod4 n h
  have hT2_gt1 := two_ascent_T2_gt1 n h
  have hT3_le : syracuse (syracuse (syracuse n)) ≤
      (3 * syracuse (syracuse n) + 1) / 4 :=
    syracuse_le_of_mod4_eq1 (syracuse (syracuse n)) hT2_mod4 hT2_gt1
  -- T²(n) = (3*((3n+1)/2)+1)/2 from syracuse2_of_mod8_eq7
  have hT2_eq := syracuse2_of_mod8_eq7 n (by omega)
  -- Rewrite syracuse (syracuse n) in both hT3_le and the goal
  rw [hT2_eq] at hT3_le ⊢
  -- Now hT3_le: syracuse (...) ≤ (3 * (...) + 1) / 4
  -- Goal: syracuse (...) ≤ (27*n+19)/16
  have h_rhs_eq : (3 * ((3 * ((3 * n + 1) / 2) + 1) / 2) + 1) / 4 =
      (27 * n + 19) / 16 := by omega
  omega

/-! ## 4. 数値検証 -/

-- 即時下降: n=5 (5 % 4 = 1), syracuse 5 = 1, (3*5+1)/4 = 4
-- T(5) = 1 ≤ 4 ✓
example : syracuse 5 ≤ (3 * 5 + 1) / 4 := by
  have : syracuse 5 = 1 := by
    change (3 * 5 + 1) / 2 ^ v2 (3 * 5 + 1) = 1
    have : v2 16 = 4 := by unfold v2; unfold v2; unfold v2; unfold v2; unfold v2; simp
    rw [this]; norm_num
  omega

-- 1回上昇+下降: n=3 (3 % 8 = 3), T(3)=5, T²(3)=1, (9*3+5)/8 = 4
-- T²(3) = 1 ≤ 4 ✓ (v2 が大きいので等式ではなく厳密に小さい)
example : syracuse (syracuse 3) ≤ (9 * 3 + 5) / 8 := by
  exact one_ascent_bound 3 (by omega)

-- 1回上昇+下降: n=11 (11 % 8 = 3), T(11)=17, T²(11)=13, (9*11+5)/8 = 104/8 = 13
-- T²(11) = 13 = 13 ✓ (この場合は等しい)
example : syracuse (syracuse 11) = (9 * 11 + 5) / 8 := by
  -- T(11) = 17, T(17) = 13
  have hT1 : syracuse 11 = 17 := by
    change (3 * 11 + 1) / 2 ^ v2 (3 * 11 + 1) = 17
    have : v2 34 = 1 := by unfold v2; unfold v2; simp
    rw [this]; norm_num
  have hT2 : syracuse 17 = 13 := by
    change (3 * 17 + 1) / 2 ^ v2 (3 * 17 + 1) = 13
    have : v2 52 = 2 := by unfold v2; unfold v2; unfold v2; simp
    rw [this]; norm_num
  rw [hT1, hT2]

-- 2回上昇+下降: n=7 (7 % 16 = 7), T(7)=11, T²(7)=17, T³(7)=13
-- (27*7+19)/16 = 208/16 = 13 ✓
example : syracuse (syracuse (syracuse 7)) = (27 * 7 + 19) / 16 := by
  have hT1 : syracuse 7 = 11 := by
    change (3 * 7 + 1) / 2 ^ v2 (3 * 7 + 1) = 11
    have : v2 22 = 1 := by unfold v2; unfold v2; simp
    rw [this]; norm_num
  have hT2 : syracuse 11 = 17 := by
    change (3 * 11 + 1) / 2 ^ v2 (3 * 11 + 1) = 17
    have : v2 34 = 1 := by unfold v2; unfold v2; simp
    rw [this]; norm_num
  have hT3 : syracuse 17 = 13 := by
    change (3 * 17 + 1) / 2 ^ v2 (3 * 17 + 1) = 13
    have : v2 52 = 2 := by unfold v2; unfold v2; unfold v2; simp
    rw [this]; norm_num
  rw [hT1, hT2, hT3]

/-! ## 5. 加速 Syracuse 関数 (fuel パターン) -/

/-- firstDescent: n から最大 fuel ステップの Syracuse 反復を行い、
    最初に「下降」(T(m) < m) するまでの反復回数を返す。
    fuel = 0 のとき、または下降を検出したときは停止する。
    返り値: (ステップ数, 下降後の値) -/
def firstDescent (fuel : ℕ) (n : ℕ) : ℕ × ℕ :=
  match fuel with
  | 0 => (0, n)
  | fuel' + 1 =>
    let next := syracuse n
    if next < n then (1, next)  -- 下降を検出
    else
      let (steps, val) := firstDescent fuel' next
      (steps + 1, val)

/-- firstDescentValue: 最初の下降の結果の値だけを返す -/
def firstDescentValue (fuel : ℕ) (n : ℕ) : ℕ :=
  (firstDescent fuel n).2

/-- firstDescentSteps: 最初の下降までのステップ数を返す -/
def firstDescentSteps (fuel : ℕ) (n : ℕ) : ℕ :=
  (firstDescent fuel n).1

/-! ### firstDescent の基本性質 -/

/-- 下降が即座に起こる場合 -/
theorem firstDescent_immediate (fuel : ℕ) (n : ℕ) (h : syracuse n < n) :
    firstDescent (fuel + 1) n = (1, syracuse n) := by
  simp [firstDescent, h]

/-- 上昇の場合は再帰 -/
theorem firstDescent_ascent (fuel : ℕ) (n : ℕ) (h : ¬ (syracuse n < n)) :
    firstDescent (fuel + 1) n =
    let (steps, val) := firstDescent fuel (syracuse n)
    (steps + 1, val) := by
  simp [firstDescent, h]

/-! ### 数値検証 -/

set_option linter.style.nativeDecide false in
-- n=5 (≡ 1 mod 4): 即時下降, T(5)=1
example : firstDescent 10 5 = (1, 1) := by native_decide

set_option linter.style.nativeDecide false in
-- n=3 (≡ 3 mod 8): 1回上昇+1回下降, T(3)=5→T(5)=1
example : firstDescent 10 3 = (2, 1) := by native_decide

set_option linter.style.nativeDecide false in
-- n=7 (≡ 7 mod 16): 2回上昇+1回下降, T(7)=11→T(11)=17→T(17)=13
example : firstDescent 10 7 = (3, 13) := by native_decide

set_option linter.style.nativeDecide false in
-- n=11 (≡ 3 mod 8): 1回上昇+1回下降, T(11)=17→T(17)=13
example : firstDescent 10 11 = (2, 13) := by native_decide

set_option linter.style.nativeDecide false in
-- n=9 (≡ 1 mod 8): 即時下降, T(9)=7
example : firstDescent 10 9 = (1, 7) := by native_decide

set_option linter.style.nativeDecide false in
-- n=31 (≡ 31 mod 32): 4回上昇+1回下降
-- T(31)=47→T(47)=71→T(71)=107→T(107)=161→T(161)=..?
-- 161 % 4 = 1, T(161) = (3*161+1)/4 = 484/4 = 121 < 161
example : firstDescent 10 31 = (5, 121) := by native_decide

/-! ## 6. 上界の合成: mod 8 分類による最悪ケース -/

/-- n ≡ 3 (mod 8) → T²(n) < 2*n (1回上昇+下降は2倍未満) -/
theorem one_ascent_lt_double (n : ℕ) (h : n % 8 = 3) (_hn : n ≥ 3) :
    syracuse (syracuse n) < 2 * n := by
  have hle := one_ascent_bound n h
  -- (9n+5)/8 < 2n ⟺ 9n+5 < 16n ⟺ 5 < 7n ⟺ n ≥ 1
  have : (9 * n + 5) / 8 < 2 * n := by omega
  omega

/-- n ≡ 7 (mod 16) → T³(n) < 2*n (2回上昇+下降は2倍未満) -/
theorem two_ascent_lt_double (n : ℕ) (h : n % 16 = 7) (_hn : n ≥ 7) :
    syracuse (syracuse (syracuse n)) < 2 * n := by
  have hle := two_ascent_bound n h
  -- (27n+19)/16 < 2n ⟺ 27n+19 < 32n ⟺ 19 < 5n ⟺ n ≥ 4
  have : (27 * n + 19) / 16 < 2 * n := by omega
  omega

/-! ## 7. 上昇+下降サイクルの一般的パターン

k 回上昇 + 1 回下降のとき、値の上界は:
  T^{k+1}(n) ≤ (3^{k+1} * n + C_k) / 2^{2+k}

ここで C_k は定数。具体値:
- k=0: T(n) ≤ (3n+1)/4,           C_0 = 1
- k=1: T²(n) ≤ (9n+5)/8,          C_1 = 5
- k=2: T³(n) ≤ (27n+19)/16,       C_2 = 19

パターン: C_k = (3^{k+1} - 2^{k+1} - 1)/(?) ... 実際は
C_0 = 1
C_1 = 3*C_0 + 1 + ? = 3*1 + 2 = 5
C_2 = 3*C_1 + 1 + ? = 3*5 + 4 = 19

漸化式: C_{k+1} = 3*C_k + 2^{k+1}

これは決定的な（確率的でない）結果であり、
個々のサイクルでは 3^{k+1}/2^{k+2} > 1 (k ≥ 1) なので縮小を保証しないが、
下降ステップの「確率」が上昇ステップより高いことと合わせると、
平均的には縮小する（Tao の結果の基盤）。
-/

/-- 上界定数の漸化式: C_0 = 1, C_{k+1} = 3*C_k + 2^{k+1} -/
def boundConst : ℕ → ℕ
  | 0 => 1
  | k + 1 => 3 * boundConst k + 2 ^ (k + 1)

-- 定数の検証
example : boundConst 0 = 1 := rfl
example : boundConst 1 = 5 := rfl
example : boundConst 2 = 19 := rfl
example : boundConst 3 = 65 := rfl

/-- 上界の分母: 2^{k+2} -/
def boundDenom (k : ℕ) : ℕ := 2 ^ (k + 2)

-- 分母の検証
example : boundDenom 0 = 4 := rfl
example : boundDenom 1 = 8 := rfl
example : boundDenom 2 = 16 := rfl

/-! ## 8. 縮小率の限界の明示化

即時下降の場合: T(n) ≤ (3n+1)/4
ここで (3n+1)/4 < n ⟺ 3n+1 < 4n ⟺ 1 < n
つまり n > 1 なら必ず縮小する。

1回上昇+下降の場合: T²(n) ≤ (9n+5)/8
ここで (9n+5)/8 > n ⟺ 9n+5 > 8n ⟺ n > -5 (常に成立)
つまり必ず「膨張」しうる（ただし2倍未満）。

しかし重要なのは:
- 即時下降 (確率1/2): 比率 ≤ 3/4
- 1回上昇+下降 (確率1/4): 比率 ≤ 9/8
- 2回上昇+下降 (確率1/8): 比率 ≤ 27/16

対数的な期待値: (1/2)*log(3/4) + (1/4)*log(9/8) + (1/8)*log(27/16) + ...
= log(3/4) が支配的 → 平均的に縮小
-/

/-- 即時下降は縮小: n ≡ 1 (mod 4), n > 1 → T(n) < n -/
theorem immediate_descent_shrinks (n : ℕ) (h : n % 4 = 1) (hn : n > 1) :
    syracuse n < n :=
  syracuse_lt_of_mod4_eq1 n h hn

/-- 1回上昇+下降は2倍未満に収まることの別表現:
    n ≡ 3 (mod 8) → 8 * T²(n) ≤ 9*n + 5 -/
theorem one_ascent_bound_scaled (n : ℕ) (h : n % 8 = 3) :
    8 * syracuse (syracuse n) ≤ 9 * n + 5 := by
  have hle := one_ascent_bound n h
  -- T²(n) ≤ (9n+5)/8 → 8*T²(n) ≤ 8*((9n+5)/8) ≤ 9n+5
  have : 8 * ((9 * n + 5) / 8) ≤ 9 * n + 5 := Nat.mul_div_le (9 * n + 5) 8
  omega

/-- 2回上昇+下降は2倍未満に収まることの別表現:
    n ≡ 7 (mod 16) → 16 * T³(n) ≤ 27*n + 19 -/
theorem two_ascent_bound_scaled (n : ℕ) (h : n % 16 = 7) :
    16 * syracuse (syracuse (syracuse n)) ≤ 27 * n + 19 := by
  have hle := two_ascent_bound n h
  have : 16 * ((27 * n + 19) / 16) ≤ 27 * n + 19 := Nat.mul_div_le (27 * n + 19) 16
  omega

/-! ## 9. 即時下降の正確な等式 (mod 8 分類) -/

/-- n ≡ 1 (mod 8) → T(n) = (3n+1)/4 (正確な等式) -/
theorem immediate_descent_eq_mod8_eq1 (n : ℕ) (h : n % 8 = 1) :
    syracuse n = (3 * n + 1) / 4 :=
  syracuse_of_mod8_eq1 n h

/-- n ≡ 5 (mod 8) → T(n) ≤ (3n+1)/8 (強い下降) -/
theorem strong_descent_bound_mod8_eq5 (n : ℕ) (h : n % 8 = 5) :
    syracuse n ≤ (3 * n + 1) / 8 :=
  syracuse_le_of_mod8_eq5 n h

/-! ## 10. 総合: mod 8 分類に基づく1サイクルの上界まとめ -/

/-- mod 8 分類に基づく Syracuse 1サイクルの上界:
    奇数 n > 1 に対して、上昇+下降1サイクル後の値の上界。

    - n ≡ 1 (mod 8): T(n) < n (即時下降、縮小)
    - n ≡ 3 (mod 8): T²(n) < 2n (1回上昇+下降、2倍未満)
    - n ≡ 5 (mod 8): T(n) < n (即時強下降、縮小)
    - n ≡ 7 (mod 16): T³(n) < 2n (2回上昇+下降、2倍未満)

    注: n ≡ 7 (mod 8) の場合、T²(n) は上昇しうる（T²(n) > n）ため
    mod 16 での分岐が必要。n ≡ 15 (mod 16) は3回上昇で、さらに mod 32 が必要。 -/
theorem cycle_bound_mod8 (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    (n % 8 = 1 → syracuse n < n) ∧
    (n % 8 = 3 → syracuse (syracuse n) < 2 * n) ∧
    (n % 8 = 5 → syracuse n < n) ∧
    (n % 16 = 7 → syracuse (syracuse (syracuse n)) < 2 * n) := by
  refine ⟨fun h => syracuse_descent_mod8_eq1 n h hn,
         fun h => one_ascent_lt_double n h (by omega),
         fun h => syracuse_strong_descent_mod8_eq5 n h hn,
         fun h => two_ascent_lt_double n h (by omega)⟩
