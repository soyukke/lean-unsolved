import Unsolved.Collatz.Defs

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

/-! ## 9. 形式化可能な小さい結果 -/

/-! ### 9.1 奇数の 3n+1 は必ず偶数 -/

/-- 奇数 n に対して 3*n+1 は偶数 -/
theorem three_mul_add_one_even (n : ℕ) (hn : n % 2 = 1) : (3 * n + 1) % 2 = 0 := by
  omega

/-! ### 9.2 collatzStep (2*n) = n -/

/-- 正の整数 n に対して collatzStep (2*n) = n -/
theorem collatzStep_double (n : ℕ) (_hn : n > 0) : collatzStep (2 * n) = n := by
  have heven : (2 * n) % 2 = 0 := by omega
  rw [collatzStep_even_eq_div2 (2 * n) heven]
  omega

/-! ### 9.3 Syracuse 値の非零性 -/

/-- v2(m) に対応する 2^v2(m) は m を割り切る -/
private theorem pow_v2_dvd (m : ℕ) : 2 ^ v2 m ∣ m := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hm : m = 0
    · subst hm; simp
    · by_cases hmod : m % 2 ≠ 0
      · rw [v2_odd m hmod]; simp
      · push_neg at hmod
        rw [v2_even m hm hmod]
        have hdiv_lt : m / 2 < m := by omega
        have ih_half := ih (m / 2) hdiv_lt
        change 2 ^ (1 + v2 (m / 2)) ∣ m
        rw [pow_add, pow_one]
        -- 2^v2(m/2) ∣ m/2 from IH, and m = 2 * (m/2)
        calc 2 * 2 ^ v2 (m / 2) ∣ 2 * (m / 2) := Nat.mul_dvd_mul_left 2 ih_half
          _ ∣ m := by exact ⟨1, by omega⟩

/-- 2^v2(n) ≤ n （n > 0 のとき） -/
private theorem pow_v2_le (n : ℕ) (hn : n > 0) : 2 ^ v2 n ≤ n := by
  have ⟨c, hc⟩ := pow_v2_dvd n
  have hpow_pos : 2 ^ v2 n > 0 := by positivity
  have hc_pos : c > 0 := by
    by_contra h
    push_neg at h
    interval_cases c
    omega
  calc 2 ^ v2 n ≤ 2 ^ v2 n * c := Nat.le_mul_of_pos_right _ hc_pos
    _ = n := by omega

/-- 奇数 n ≥ 1 に対して syracuse n ≥ 1 -/
theorem syracuse_pos (n : ℕ) (_hn : n ≥ 1) (hodd : n % 2 = 1) : syracuse n ≥ 1 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) ≥ 1
  have hpow_le : 2 ^ v2 (3 * n + 1) ≤ 3 * n + 1 := pow_v2_le (3 * n + 1) (by omega)
  have hpow_pos : 2 ^ v2 (3 * n + 1) > 0 := by positivity
  exact Nat.div_pos hpow_le hpow_pos

/-! ### 9.4 T(n) は 3 の倍数にならない -/

/-- 3*n+1 は 3 の倍数でない -/
private theorem three_mul_add_one_not_div_three (n : ℕ) : (3 * n + 1) % 3 ≠ 0 := by
  omega

/-- 2^k と 3 は互いに素 -/
private theorem coprime_pow_two_three (k : ℕ) : Nat.Coprime (2 ^ k) 3 := by
  have h : Nat.Coprime 2 3 := by decide
  exact Nat.Coprime.pow_left k h

/-- m が 3 の倍数でなく、d が 3 と互いに素で、d ∣ m ならば m / d も 3 の倍数でない -/
private theorem not_div_three_of_div (m d : ℕ) (_hd_pos : d > 0) (hdvd : d ∣ m)
    (hm3 : m % 3 ≠ 0) (_hcop : Nat.Coprime d 3) : (m / d) % 3 ≠ 0 := by
  intro h
  apply hm3
  have ⟨c, hc⟩ := hdvd
  rw [hc, Nat.mul_div_cancel_left c (by omega)] at h
  have h3c : 3 ∣ c := Nat.dvd_of_mod_eq_zero (by omega)
  have h3m : 3 ∣ m := by rw [hc]; exact dvd_mul_of_dvd_right h3c d
  exact Nat.mod_eq_zero_of_dvd h3m

/-- 全ての奇数 n に対して syracuse n は 3 の倍数でない -/
theorem syracuse_not_div_three (n : ℕ) (_hn : n % 2 = 1) :
    syracuse n % 3 ≠ 0 := by
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) % 3 ≠ 0
  apply not_div_three_of_div (3 * n + 1) (2 ^ v2 (3 * n + 1))
  · positivity
  · exact pow_v2_dvd (3 * n + 1)
  · exact three_mul_add_one_not_div_three n
  · exact coprime_pow_two_three (v2 (3 * n + 1))

/-! ### 9.5 Syracuse値の素因子構造: p ∣ syracuse(n) ⟺ p ∣ (3n+1) -/

/-- 2^v2(m) は m を割り切る -/
theorem two_pow_v2_dvd (m : ℕ) : 2 ^ v2 m ∣ m := pow_v2_dvd m

/-- Syracuse値の乗法的分解: syracuse(n) * 2^v2(3n+1) = 3n+1 -/
theorem syracuse_mul_pow_v2 (n : ℕ) :
    syracuse n * 2 ^ v2 (3 * n + 1) = 3 * n + 1 :=
  Nat.div_mul_cancel (two_pow_v2_dvd (3 * n + 1))

/-- 素数 p ≠ 2 に対して: p ∣ syracuse(n) ⟺ p ∣ (3n+1)。
    Syracuse像の奇素因子は (3n+1) の奇素因子と完全に一致する。
    特に p = 3 では 3 ∤ (3n+1) なので 3 ∤ syracuse(n)、
    p ≥ 5 では p ∣ syracuse(n) ⟺ n ≡ -(3⁻¹) (mod p)。(探索096) -/
theorem syracuse_dvd_odd_prime_iff (n : ℕ) (p : ℕ) (hp : Nat.Prime p) (hp2 : p ≠ 2) :
    p ∣ syracuse n ↔ p ∣ (3 * n + 1) := by
  constructor
  · intro h
    have h2 := dvd_mul_of_dvd_left h (2 ^ v2 (3 * n + 1))
    rwa [syracuse_mul_pow_v2] at h2
  · intro h
    rw [← syracuse_mul_pow_v2 n] at h
    rcases hp.prime.dvd_or_dvd h with h1 | h2
    · exact h1
    · exfalso
      have h3 : p ∣ 2 := hp.prime.dvd_of_dvd_pow h2
      have hle : p ≤ 2 := Nat.le_of_dvd (by omega) h3
      exact hp2 (Nat.le_antisymm hle hp.two_le)

/-! ### 9.6 Syracuse不動点: syracuse(n) = 1 ⟺ 3n+1 = 2^m -/

/-- 2のべき乗の v2 値: v2(2^m) = m -/
theorem v2_pow_two (m : ℕ) : v2 (2 ^ m) = m := by
  induction m with
  | zero => exact v2_odd 1 (by omega)
  | succ k ih =>
    have : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
    rw [this, v2_two_mul (2 ^ k) (by positivity)]
    omega

/-- syracuse(n) = 1 ⟺ 3n+1 が 2 のべき乗。
    T(n)=1 となる奇数 n は n=(2^m-1)/3 (m偶数) の族に限る。
    特に n=(4^k-1)/3 すなわち n=1,5,21,85,... が唯一の族。(探索097) -/
theorem syracuse_eq_one_iff_pow_two (n : ℕ) :
    syracuse n = 1 ↔ ∃ m : ℕ, 3 * n + 1 = 2 ^ m := by
  constructor
  · intro h
    exact ⟨v2 (3 * n + 1), by
      have := syracuse_mul_pow_v2 n
      rw [h, one_mul] at this
      exact this.symm⟩
  · intro ⟨m, hm⟩
    change (3 * n + 1) / 2 ^ v2 (3 * n + 1) = 1
    rw [hm, v2_pow_two]
    exact Nat.div_self (by positivity)

/-! ### 9.7 v2(3^m - 1) の閉形式（LTE公式） -/

/-- 3^m は全ての m で奇数（Structure版、Formula.leanにも同名あり） -/
private theorem three_pow_odd' (m : ℕ) : 3 ^ m % 2 = 1 := by
  have ⟨k, hk⟩ : Odd (3 ^ m) := Odd.pow (by decide : Odd 3)
  omega

/-- 9^k ≡ 1 (mod 4) -/
private theorem nine_pow_mod4 (k : ℕ) : 9 ^ k % 4 = 1 := by
  induction k with
  | zero => simp
  | succ n ih => rw [pow_succ]; omega

/-- m が奇数のとき v2(3^m - 1) = 1。
    証明: 3^(2k+1) = 9^k·3 ≡ 1·3 = 3 (mod 4) → 3^m-1 ≡ 2 (mod 4)。(探索117) -/
theorem v2_three_pow_sub_one_odd (m : ℕ) (hm : m % 2 = 1) :
    v2 (3 ^ m - 1) = 1 := by
  obtain ⟨k, rfl⟩ : ∃ k, m = 2 * k + 1 := ⟨m / 2, by omega⟩
  -- 3^(2k) = 9^k
  have h9k : (3 : ℕ) ^ (2 * k) = 9 ^ k := by
    have : (9 : ℕ) = 3 ^ 2 := by norm_num
    rw [this, ← pow_mul, Nat.mul_comm]
  -- 3^(2k+1) % 4 = 3
  have hmod4 : 3 ^ (2 * k + 1) % 4 = 3 := by
    rw [pow_succ, h9k]; have := nine_pow_mod4 k; omega
  have hge : 3 ^ (2 * k + 1) ≥ 3 := by
    calc 3 ^ (2 * k + 1) ≥ 3 ^ 1 := Nat.pow_le_pow_right (by omega) (by omega)
      _ = 3 := by norm_num
  have hne : 3 ^ (2 * k + 1) - 1 ≠ 0 := by omega
  have heven : (3 ^ (2 * k + 1) - 1) % 2 = 0 := by have := three_pow_odd' (2 * k + 1); omega
  -- (3^(2k+1)-1)/2 is odd → v2 = 0 → 1 + 0 = 1
  have hmod4_sub : (3 ^ (2 * k + 1) - 1) % 4 = 2 := by omega
  set q := (3 ^ (2 * k + 1) - 1) / 4
  have h_eq : 3 ^ (2 * k + 1) - 1 = 4 * q + 2 := by omega
  have h_div2 : (3 ^ (2 * k + 1) - 1) / 2 = 2 * q + 1 := by omega
  rw [v2_even _ hne heven, h_div2, v2_odd _ (by omega)]

/-- 9^k ≡ 1 (mod 8) -/
private theorem nine_pow_mod8 (k : ℕ) : 9 ^ k % 8 = 1 := by
  induction k with
  | zero => simp
  | succ n ih => rw [pow_succ]; omega

/-- k が奇数のとき v2(3^k + 1) = 2。
    証明: 3^(2j+1) = 9^j·3 ≡ 3 (mod 8) → 3^k+1 ≡ 4 (mod 8)。(探索117) -/
theorem v2_three_pow_add_one_odd (k : ℕ) (hk : k % 2 = 1) :
    v2 (3 ^ k + 1) = 2 := by
  obtain ⟨j, rfl⟩ : ∃ j, k = 2 * j + 1 := ⟨k / 2, by omega⟩
  have h9j : (3 : ℕ) ^ (2 * j) = 9 ^ j := by
    have : (9 : ℕ) = 3 ^ 2 := by norm_num
    rw [this, ← pow_mul, Nat.mul_comm]
  have hmod8 : (3 ^ (2 * j + 1) + 1) % 8 = 4 := by
    rw [pow_succ, h9j]; have := nine_pow_mod8 j; omega
  -- 3^k+1 ≡ 4 (mod 8) → v2 = 2
  have hne0 : 3 ^ (2 * j + 1) + 1 ≠ 0 := by positivity
  have heven1 : (3 ^ (2 * j + 1) + 1) % 2 = 0 := by omega
  -- Step-by-step: v2_even twice, then v2_odd
  set q := (3 ^ (2 * j + 1) + 1) / 8
  have heq8 : 3 ^ (2 * j + 1) + 1 = 8 * q + 4 := by omega
  have hdiv2 : (3 ^ (2 * j + 1) + 1) / 2 = 4 * q + 2 := by omega
  rw [v2_even _ hne0 heven1, hdiv2]
  have hne1 : 4 * q + 2 ≠ 0 := by omega
  have heven2 : (4 * q + 2) % 2 = 0 := by omega
  rw [v2_even _ hne1 heven2]
  have hdiv4 : (4 * q + 2) / 2 = 2 * q + 1 := by omega
  rw [hdiv4, v2_odd _ (by omega)]

/-- k が偶数のとき v2(3^k + 1) = 1。
    証明: 3^{2j} = 9^j ≡ 1 (mod 4) → 3^k+1 ≡ 2 (mod 4)。(探索117) -/
theorem v2_three_pow_add_one_even (k : ℕ) (hk : k % 2 = 0) :
    v2 (3 ^ k + 1) = 1 := by
  obtain ⟨j, rfl⟩ : ∃ j, k = 2 * j := ⟨k / 2, by omega⟩
  have h9j : (3 : ℕ) ^ (2 * j) = 9 ^ j := by
    have : (9 : ℕ) = 3 ^ 2 := by norm_num
    rw [this, ← pow_mul, Nat.mul_comm]
  have hmod4 : (3 ^ (2 * j) + 1) % 4 = 2 := by
    rw [h9j]; have := nine_pow_mod4 j; omega
  have hne : 3 ^ (2 * j) + 1 ≠ 0 := by positivity
  have heven : (3 ^ (2 * j) + 1) % 2 = 0 := by omega
  set q := (3 ^ (2 * j) + 1) / 4
  have heq4 : 3 ^ (2 * j) + 1 = 4 * q + 2 := by omega
  have hdiv2 : (3 ^ (2 * j) + 1) / 2 = 2 * q + 1 := by omega
  rw [v2_even _ hne heven, hdiv2, v2_odd _ (by omega)]

/-- m が偶数(m≥2)のとき v2(3^m - 1) = 2 + v2(m)。
    証明: 強帰納法 + 因数分解 3^{2k}-1=(3^k-1)(3^k+1) + v2_mul。(探索117 LTE公式) -/
theorem v2_three_pow_sub_one_even (m : ℕ) (hm_even : m % 2 = 0) (hm_pos : m ≥ 2) :
    v2 (3 ^ m - 1) = 2 + v2 m := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    obtain ⟨k, rfl⟩ : ∃ k, m = 2 * k := ⟨m / 2, by omega⟩
    have hk_pos : k ≥ 1 := by omega
    -- Factor: 3^{2k} - 1 = (3^k - 1)(3^k + 1)
    have h3k_ge : 3 ^ k ≥ 3 := by
      calc 3 ^ k ≥ 3 ^ 1 := Nat.pow_le_pow_right (by omega) hk_pos
        _ = 3 := by norm_num
    have hfactor : 3 ^ (2 * k) - 1 = (3 ^ k - 1) * (3 ^ k + 1) := by
      suffices h : (3 ^ k - 1) * (3 ^ k + 1) + 1 = 3 ^ (2 * k) by omega
      have h3k_pos : 3 ^ k ≥ 1 := Nat.one_le_pow _ _ (by omega)
      have hsq : 3 ^ (2 * k) = 3 ^ k * 3 ^ k := by rw [← pow_add]; congr 1; omega
      rw [hsq]; zify [h3k_pos]; ring
    rw [hfactor, v2_mul _ _ (by omega) (by omega)]
    -- v2(2k) = 1 + v2(k)
    have hv2m : v2 (2 * k) = 1 + v2 k := v2_two_mul k (by omega)
    by_cases hk_odd : k % 2 = 1
    · -- k odd: v2(3^k-1)=1, v2(3^k+1)=2
      rw [v2_three_pow_sub_one_odd k hk_odd, v2_three_pow_add_one_odd k hk_odd]
      have : v2 k = 0 := v2_odd k (by omega)
      omega
    · -- k even (k≥2): v2(3^k-1)=2+v2(k) by IH, v2(3^k+1)=1
      have hk_even : k % 2 = 0 := by omega
      have hk_ge2 : k ≥ 2 := by omega
      have hk_lt : k < 2 * k := by omega
      have ih_k := ih k hk_lt hk_even hk_ge2
      rw [ih_k, v2_three_pow_add_one_even k hk_even]
      omega

/-! ### 9.8 Syracuse値の mod 3 分類: T(n) mod 3 は v2 の偶奇で決定 -/

/-- 2^v mod 3: v偶数→1, v奇数→2 -/
private theorem two_pow_mod3 (v : ℕ) : 2 ^ v % 3 = if v % 2 = 0 then 1 else 2 := by
  induction v with
  | zero => simp
  | succ k ih =>
    rw [pow_succ]
    by_cases hk : k % 2 = 0
    · have h2k : 2 ^ k % 3 = 1 := by rw [ih, if_pos hk]
      rw [if_neg (show (k + 1) % 2 ≠ 0 from by omega)]; omega
    · have h2k : 2 ^ k % 3 = 2 := by rw [ih, if_neg hk]
      rw [if_pos (show (k + 1) % 2 = 0 from by omega)]; omega

/-- Syracuse値の mod 3 は v2(3n+1) の偶奇で完全決定。
    v2 偶数 → T(n) ≡ 1 (mod 3)、v2 奇数 → T(n) ≡ 2 (mod 3)。
    3-adic構造が2-adicに従属する核心定理。(探索129) -/
theorem syracuse_mod3_eq (n : ℕ) (_hn : n % 2 = 1) :
    syracuse n % 3 = if v2 (3 * n + 1) % 2 = 0 then 1 else 2 := by
  have hmul := syracuse_mul_pow_v2 n
  have hmod_prod : (syracuse n * 2 ^ v2 (3 * n + 1)) % 3 = 1 := by rw [hmul]; omega
  rw [Nat.mul_mod] at hmod_prod
  rw [two_pow_mod3] at hmod_prod
  split_ifs at hmod_prod ⊢ with hv <;> omega

/-- 上昇ステップでは T(n) ≡ 2 (mod 3): n ≡ 3 (mod 4) → T(n) % 3 = 2。
    上昇では v2(3n+1)=1(奇数)なので syracuse_mod3_eq から直ちに従う。(探索143) -/
theorem syracuse_ascent_mod3 (n : ℕ) (_hn : n ≥ 1) (hodd : n % 2 = 1) (hmod4 : n % 4 = 3) :
    syracuse n % 3 = 2 := by
  rw [syracuse_mod3_eq n hodd, if_neg]
  rw [v2_three_mul_add_one_of_mod4_eq3 n hmod4]; omega
