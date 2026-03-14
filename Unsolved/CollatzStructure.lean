import Unsolved.Collatz

/-!
# コラッツ予想 フェーズ3: 構造的性質

コラッツ関数・Syracuse関数の構造的な性質を形式化する。
-/

/-! ## 1. 奇数ステップの結果は必ず偶数 -/

/-- 奇数に collatzStep を適用すると偶数になる -/
theorem collatzStep_odd_gives_even (n : ℕ) (h : n % 2 = 1) :
    collatzStep n % 2 = 0 := by
  have : n % 2 ≠ 0 := by omega
  rw [collatzStep_odd n this]
  omega

/-! ## 2. 4→2→1 サイクルの形式的証明 -/

theorem collatzStep_one : collatzStep 1 = 4 := by decide

theorem collatzStep_four : collatzStep 4 = 2 := by decide

theorem collatzStep_two : collatzStep 2 = 1 := by decide

/-- 1 から始まるコラッツ列は 1→4→2→1 のサイクルを形成する -/
theorem collatz_cycle_1_4_2 :
    collatzStep (collatzStep (collatzStep 1)) = 1 := by decide

/-! ## 3. n ≡ 3 (mod 4) のとき v2(3n+1) = 1 -/

/-- n ≡ 3 (mod 4) ならば 3n+1 ≡ 2 (mod 4) なので v2(3n+1) = 1 -/
theorem v2_three_mul_add_one_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    v2 (3 * n + 1) = 1 := by
  have hn_pos : 3 * n + 1 ≥ 1 := by omega
  -- 3n+1 is even but (3n+1)/2 is odd
  have hmod2 : (3 * n + 1) % 2 = 0 := by omega
  have hne : 3 * n + 1 ≠ 0 := by omega
  rw [v2_even _ hne hmod2]
  have hdiv : (3 * n + 1) / 2 % 2 = 1 := by omega
  rw [v2_odd _ (by omega)]

/-! ## 4. 偶数に対する collatzStep の上界 -/

/-- 偶数 n ≥ 2 に対して collatzStep n = n / 2 -/
theorem collatzStep_even_eq_div2 (n : ℕ) (h : n % 2 = 0) :
    collatzStep n = n / 2 := by
  simp [collatzStep, h]

/-- 偶数 n ≥ 2 に対して collatzStep n < n -/
theorem collatzStep_even_lt (n : ℕ) (hn : n ≥ 2) (h : n % 2 = 0) :
    collatzStep n < n := by
  rw [collatzStep_even_eq_div2 n h]
  omega

/-- 偶数 n に対して collatzStep n ≤ n / 2 -/
theorem collatzStep_even_le_half (n : ℕ) (h : n % 2 = 0) :
    collatzStep n ≤ n / 2 := by
  rw [collatzStep_even_eq_div2 n h]

/-! ## 5. Syracuse 関数と collatzStep の関係 -/

/-- 奇数 n に対して syracuse n = collatzStep (3*n+1) を十分回繰り返した結果
    まず最初の一歩: syracuse n の分子は collatzStep n に等しい (3n+1) -/
theorem collatzStep_odd_eq (n : ℕ) (h : n % 2 = 1) :
    collatzStep n = 3 * n + 1 := by
  simp [collatzStep]
  omega

/-- v2 n > 0 ならば n は偶数 -/
theorem even_of_v2_pos (n : ℕ) (h : v2 n > 0) : n % 2 = 0 := by
  by_contra hc
  push_neg at hc
  have : n % 2 = 1 := by omega
  have := v2_odd n (by omega)
  omega

/-- v2 n > 0 ならば n ≠ 0 -/
theorem ne_zero_of_v2_pos (n : ℕ) (h : v2 n > 0) : n ≠ 0 := by
  intro heq
  subst heq
  simp at h

/-- 奇数の3n+1は必ず偶数なので v2 > 0 -/
theorem v2_pos_of_odd_step (n : ℕ) (_hn : n ≥ 1) (h : n % 2 = 1) :
    v2 (3 * n + 1) > 0 := by
  have heven : (3 * n + 1) % 2 = 0 := by omega
  have hne : 3 * n + 1 ≠ 0 := by omega
  rw [v2_even _ hne heven]
  omega

/-! ## 6. mod 4 による軌道の上昇・下降の決定 -/

/-- n ≡ 1 (mod 4) ならば v2(3n+1) ≥ 2 -/
theorem v2_ge_two_of_mod4_eq1 (n : ℕ) (h : n % 4 = 1) :
    v2 (3 * n + 1) ≥ 2 := by
  -- n = 4q + 1 → 3n+1 = 12q+4 = 4(3q+1)
  -- 3n+1 is divisible by 4, so v2 ≥ 2
  have hne1 : 3 * n + 1 ≠ 0 := by omega
  have heven1 : (3 * n + 1) % 2 = 0 := by omega
  rw [v2_even _ hne1 heven1]
  -- Now need: 1 + v2 ((3*n+1)/2) ≥ 2, i.e., v2 ((3*n+1)/2) ≥ 1
  have hdiv_even : (3 * n + 1) / 2 % 2 = 0 := by omega
  have hdiv_ne : (3 * n + 1) / 2 ≠ 0 := by omega
  rw [v2_even _ hdiv_ne hdiv_even]
  omega

/-- n ≡ 3 (mod 4) ならば syracuse n = (3*n+1)/2 -/
theorem syracuse_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    syracuse n = (3 * n + 1) / 2 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) = (3 * n + 1) / 2
  rw [v2_three_mul_add_one_of_mod4_eq3 n h]
  simp

/-- n ≡ 3 (mod 4) ならば syracuse n > n (上昇ステップ) -/
theorem syracuse_gt_of_mod4_eq3 (n : ℕ) (h : n % 4 = 3) :
    syracuse n > n := by
  rw [syracuse_mod4_eq3 n h]
  omega

/-- n ≡ 1 (mod 4) かつ n > 1 ならば syracuse n < n (下降ステップ) -/
theorem syracuse_lt_of_mod4_eq1 (n : ℕ) (h : n % 4 = 1) (hn : n > 1) :
    syracuse n < n := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) < n
  have hv2 := v2_ge_two_of_mod4_eq1 n h
  -- We know v2(3n+1) ≥ 2, so 2^v2(3n+1) ≥ 4
  have hpow_pos : 2 ^ v2 (3 * n + 1) ≥ 4 := by
    have : 2 ^ v2 (3 * n + 1) ≥ 2 ^ 2 := Nat.pow_le_pow_right (by omega) hv2
    simpa using this
  -- (3n+1) / 2^v2 ≤ (3n+1) / 4
  have hle : (3 * n + 1) / 2 ^ v2 (3 * n + 1) ≤ (3 * n + 1) / 4 := by
    apply Nat.div_le_div_left (by omega) (by omega)
  -- (3n+1)/4 < n when n > 1
  have hlt : (3 * n + 1) / 4 < n := by omega
  omega

/-! ## 7. 2ステップ下降補題: n ≡ 3 (mod 8) の場合 -/

/-- n ≡ 3 (mod 8) ならば n ≡ 3 (mod 4) -/
theorem mod4_eq3_of_mod8_eq3 (n : ℕ) (h : n % 8 = 3) : n % 4 = 3 := by
  omega

/-- n ≡ 3 (mod 8) ならば syracuse n ≡ 1 (mod 4) -/
theorem syracuse_mod4_eq1_of_mod8_eq3 (n : ℕ) (h : n % 8 = 3) :
    syracuse n % 4 = 1 := by
  rw [syracuse_mod4_eq3 n (mod4_eq3_of_mod8_eq3 n h)]
  omega

/-- n ≡ 3 (mod 8) ならば syracuse n > 1 -/
theorem syracuse_gt_one_of_mod8_eq3 (n : ℕ) (h : n % 8 = 3) :
    syracuse n > 1 := by
  rw [syracuse_mod4_eq3 n (mod4_eq3_of_mod8_eq3 n h)]
  omega

/-- n ≡ 3 (mod 8) ならば syracuse(syracuse(n)) < syracuse(n)
    (2ステップ目は下降) -/
theorem syracuse_two_step_descent (n : ℕ) (h : n % 8 = 3) :
    syracuse (syracuse n) < syracuse n := by
  exact syracuse_lt_of_mod4_eq1 (syracuse n)
    (syracuse_mod4_eq1_of_mod8_eq3 n h)
    (syracuse_gt_one_of_mod8_eq3 n h)

/-! ## 8. 2ステップの上界 -/

/-- n ≡ 1 (mod 4) かつ n > 1 ならば syracuse n ≤ (3*n+1)/4 -/
theorem syracuse_le_of_mod4_eq1 (n : ℕ) (h : n % 4 = 1) (_hn : n > 1) :
    syracuse n ≤ (3 * n + 1) / 4 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) ≤ (3 * n + 1) / 4
  have hv2 := v2_ge_two_of_mod4_eq1 n h
  have hpow_ge : 2 ^ v2 (3 * n + 1) ≥ 4 := by
    have : 2 ^ v2 (3 * n + 1) ≥ 2 ^ 2 := Nat.pow_le_pow_right (by omega) hv2
    simpa using this
  exact Nat.div_le_div_left (by omega) (by omega)

/-- n ≡ 3 (mod 8) ならば syracuse(syracuse(n)) ≤ (3 * syracuse n + 1) / 4
    上昇後の下降ステップにおける上界 -/
theorem syracuse_two_step_upper_bound (n : ℕ) (h : n % 8 = 3) :
    syracuse (syracuse n) ≤ (3 * syracuse n + 1) / 4 := by
  exact syracuse_le_of_mod4_eq1 (syracuse n)
    (syracuse_mod4_eq1_of_mod8_eq3 n h)
    (syracuse_gt_one_of_mod8_eq3 n h)

/-- n ≡ 3 (mod 8) ならば syracuse n = (3 * n + 1) / 2 かつ
    syracuse(syracuse(n)) ≤ (3 * ((3 * n + 1) / 2) + 1) / 4
    上昇→下降サイクルの上界をnの式で表現 -/
theorem syracuse_two_step_bound_in_n (n : ℕ) (h : n % 8 = 3) :
    syracuse (syracuse n) ≤ (3 * ((3 * n + 1) / 2) + 1) / 4 := by
  have heq : syracuse n = (3 * n + 1) / 2 :=
    syracuse_mod4_eq3 n (mod4_eq3_of_mod8_eq3 n h)
  calc syracuse (syracuse n)
      ≤ (3 * syracuse n + 1) / 4 := syracuse_two_step_upper_bound n h
    _ = (3 * ((3 * n + 1) / 2) + 1) / 4 := by rw [heq]
