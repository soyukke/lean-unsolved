"""
Nat.dvd_div_iff_mul_dvd が使えない場合の代替戦略

逆方向 Step 3: 2^(k+1) | m → 2^k | (m/2) を手動で証明
"""

print("""
=== 代替1: 手動展開 ===

have hdvd_half : 2 ^ k ∣ m / 2 := by
  obtain ⟨c, hc⟩ := h    -- h: 2^(k+1)|m  →  m = 2^(k+1) * c
  have : m = 2 * (2^k * c) := by rw [hc, pow_succ]; ring
  have hdiv : m / 2 = 2^k * c := by omega
  exact ⟨c, hdiv⟩


=== 代替2: Nat.div_dvd_of_dvd + 逆方向 ===

実は直接的に:
  h : 2^(k+1)|m を分解
  2^(k+1) = 2 * 2^k
  m = 2 * 2^k * c
  m/2 = 2^k * c

  Leanでは:
    obtain ⟨c, hc⟩ := h
    rw [pow_succ, mul_assoc] at hc
    have := Nat.eq_of_mul_eq_left (by omega : (2:ℕ) > 0) (by omega : m = 2 * (2^k * c))
    -- or simply:
    exact dvd_of_eq (by omega)

  omegaが2^k関連の式を解けるか不明。
  確実な方法:

  have hdvd_half : 2 ^ k ∣ m / 2 := by
    obtain ⟨c, hc⟩ := h
    refine ⟨c, ?_⟩
    have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := pow_succ 2 k  -- or by ring
    rw [h1, mul_assoc] at hc
    -- hc: m = 2 * 2^k * c → m = 2 * (2^k * c)
    -- m/2 = 2^k * c
    have h2 : m / 2 = 2 ^ k * c := by
      rw [hc]; exact Nat.mul_div_cancel_left _ (by omega)
    exact h2


=== 代替3: mul_dvd_mul_leftをひっくり返す ===

2^(k+1)|m
= (2 * 2^k) | m
→ 2^k | m  (dvd_of_mul_dvd_mul_left ではない)

実は Nat.dvd_div_of_mul_dvd がある可能性:
  Nat.dvd_div_of_mul_dvd: a*b | c → a | c → b | c/a

探索:
""")

# もっとシンプルな方法を考える
print("""
=== 最もシンプルな証明 (代替4) ===

theorem v2_ge_of_dvd (m k : ℕ) (hm : m > 0) (h : 2 ^ k ∣ m) : v2 m ≥ k := by
  induction k generalizing m with
  | zero => omega
  | succ k ih =>
    have h2m : 2 ∣ m := dvd_trans (dvd_pow_self 2 (Nat.succ_ne_zero k)) h
    have heven : m % 2 = 0 := Nat.mod_eq_zero_of_dvd h2m
    have hne : m ≠ 0 := by omega
    rw [v2_even m hne heven]
    suffices v2 (m / 2) ≥ k by omega
    apply ih
    · omega  -- m/2 > 0
    · -- 2^k | m/2
      obtain ⟨c, hc⟩ := h
      exact ⟨c, by
        have : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
        rw [this, mul_assoc] at hc
        have : m / 2 = 2 ^ k * c := Nat.div_eq_of_eq_mul_left (by omega) hc
        exact this⟩

... ただし Nat.div_eq_of_eq_mul_left は存在しない可能性。

より確実:

    · obtain ⟨c, hc⟩ := h
      refine ⟨c, ?_⟩
      have h1 : m = 2 * (2 ^ k * c) := by
        rw [← mul_assoc, ← pow_succ]; exact hc
      calc m / 2 = 2 * (2 ^ k * c) / 2 := by rw [← h1]
        _ = 2 ^ k * c := Nat.mul_div_cancel_left _ (by omega)
""")

print("""
=== 完全な代替証明（omega回避） ===

theorem v2_ge_of_dvd (m k : ℕ) (hm : m > 0) (h : 2 ^ k ∣ m) : v2 m ≥ k := by
  induction k generalizing m with
  | zero => omega
  | succ k ih =>
    -- 2 | m from 2 | 2^(k+1) | m
    have h2dvd : (2 : ℕ) ∣ 2 ^ (k + 1) := dvd_pow_self 2 (Nat.succ_ne_zero k)
    have h2m : 2 ∣ m := dvd_trans h2dvd h
    have heven : m % 2 = 0 := Nat.mod_eq_zero_of_dvd h2m
    have hne : m ≠ 0 := Nat.not_eq_zero_of_lt (Nat.lt_of_lt_of_le Nat.zero_lt_one (Nat.one_le_iff_ne_zero.mpr (Nat.pos_of_ne_zero (by omega))))
    -- もっと簡単: have hne : m ≠ 0 := by omega
    rw [v2_even m hne heven]
    -- need: 1 + v2(m/2) ≥ k+1, i.e., v2(m/2) ≥ k
    suffices hsuff : v2 (m / 2) ≥ k by omega
    apply ih
    · -- m / 2 > 0
      exact Nat.div_pos (Nat.le_of_dvd hm h2m) (by omega)
      -- or simply: omega  (since m > 0 and m even → m ≥ 2 → m/2 ≥ 1)
    · -- 2^k ∣ m/2
      obtain ⟨c, hc⟩ := h   -- m = 2^(k+1) * c
      exact ⟨c, by
        have heq : m = 2 * (2 ^ k * c) := by
          calc m = 2 ^ (k + 1) * c := hc
            _ = (2 * 2 ^ k) * c := by rw [pow_succ]
            _ = 2 * (2 ^ k * c) := by ring
        calc m / 2 = 2 * (2 ^ k * c) / 2 := by rw [← heq]
          _ = 2 ^ k * c := Nat.mul_div_cancel_left _ (by omega : (2:ℕ) > 0)⟩
""")
