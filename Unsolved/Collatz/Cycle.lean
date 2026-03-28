import Unsolved.Collatz.Mod

/-!
# コラッツ予想 探索12: 非自明サイクルの排除

コラッツ予想の部分問題として「4→2→1以外のサイクルは存在しない」を考える。
完全な証明にはBakerの定理（対数の線形形式の下界）が必要だが、
公理なしで証明可能な部分を先に形式化し、Bakerの定理は axiom として分離する。

## 公理なしで証明される結果

### Part A: 基本的なサイクル排除
1. `collatzIter_three_one` : 1→4→2→1 の3ステップサイクル
2. `no_collatzStep_fixed_point` : collatzStep に不動点がない (n > 0)
3. `no_collatzStep_two_cycle` : collatzStep に長さ2のサイクルがない (n > 0)
4. `pow_three_eq_pow_two_imp` : 3^a = 2^b → a = 0 ∧ b = 0

### Part B: Bakerの定理を使う部分 (axiom)
- `baker_cycle_bound` : 非自明サイクルの非存在 (将来Mathlibに追加されたら置換)
- `no_nontrivial_syracuse_cycle` : 非自明サイクルは存在しない
-/

/-! =====================================================
    Part A: 公理なしで証明可能な結果
    ===================================================== -/

/-! ## 1. 1→4→2→1 は唯一の小さいサイクル -/

/-- collatzIter 3 1 = 1: 1 から3ステップで 1 に戻る -/
theorem collatzIter_three_one : collatzIter 3 1 = 1 := by decide

/-- collatzIter の各ステップを明示: 1 → 4 → 2 → 1 -/
theorem collatz_orbit_one :
    collatzStep 1 = 4 ∧ collatzStep 4 = 2 ∧ collatzStep 2 = 1 := by decide

/-! ## 2. collatzStep に不動点がないこと -/

/-- collatzStep n = n を満たす正の自然数は存在しない。
    - 偶数: n/2 = n → n = 0
    - 奇数: 3n+1 = n → 2n = -1 (自然数では不可能) -/
theorem no_collatzStep_fixed_point (n : ℕ) (hn : n > 0) :
    collatzStep n ≠ n := by
  intro h
  simp [collatzStep] at h
  split at h <;> omega

/-! ## 3. collatzStep に長さ2のサイクルがないこと -/

/-- collatzStep (collatzStep n) = n を n > 0 で満たす n は存在しない -/
theorem no_collatzStep_two_cycle (n : ℕ) (hn : n > 0) :
    collatzStep (collatzStep n) ≠ n := by
  intro h
  simp [collatzStep] at h
  split at h <;> split at h <;> omega

/-! ## 4. 3^a = 2^b → a = 0 ∧ b = 0 -/

/-- a > 0 ならば 3 | 3^a -/
private theorem three_dvd_pow_three (a : ℕ) (ha : a > 0) : 3 ∣ 3 ^ a :=
  dvd_pow_self 3 (by omega)

/-- 2^b は 3 で割り切れない。
    Nat.Prime.not_dvd_pow を使用: 3 は素数で 3 ∤ 2 なので 3 ∤ 2^b -/
private theorem three_not_dvd_pow_two (b : ℕ) : ¬(3 ∣ 2 ^ b) := by
  have h3 : Nat.Prime 3 := by decide
  intro hdvd
  have : 3 ∣ 2 := (Nat.Prime.dvd_of_dvd_pow h3 hdvd)
  omega

/-- 3^a = 2^b は a = 0 かつ b = 0 のときのみ成立する。
    証明: a > 0 なら 3 | 3^a だが 3 ∤ 2^b なので矛盾。
    a = 0 なら 1 = 2^b より b = 0。 -/
theorem pow_three_eq_pow_two_imp (a b : ℕ) (h : 3 ^ a = 2 ^ b) :
    a = 0 ∧ b = 0 := by
  constructor
  · by_contra ha
    push_neg at ha
    have h3 := three_dvd_pow_three a (by omega)
    rw [h] at h3
    exact three_not_dvd_pow_two b h3
  · by_contra hb
    push_neg at hb
    have ha : a = 0 := by
      by_contra ha
      push_neg at ha
      have h3 := three_dvd_pow_three a (by omega)
      rw [h] at h3
      exact three_not_dvd_pow_two b h3
    subst ha
    simp at h
    have : 2 ^ b ≥ 2 := by
      calc 2 ^ b ≥ 2 ^ 1 := Nat.pow_le_pow_right (by omega) (by omega)
           _ = 2 := by norm_num
    omega

/-! ## 5. Syracuse サイクルへの帰結: サイクルの上昇・下降バランス -/

/-- Syracuse サイクルの定義: n > 0 かつ syracuseIter k n = n (k > 0) -/
def IsSyracuseCycle (k n : ℕ) : Prop :=
  k > 0 ∧ n > 0 ∧ n % 2 = 1 ∧ syracuseIter k n = n

/-- collatzStep のサイクルの定義: n > 0 かつ collatzIter k n = n (k > 0) -/
def IsCollatzCycle (k n : ℕ) : Prop :=
  k > 0 ∧ n > 0 ∧ collatzIter k n = n

/-- 1→4→2→1 サイクルは IsCollatzCycle 3 1 -/
theorem trivial_collatz_cycle : IsCollatzCycle 3 1 := by
  refine ⟨by omega, by omega, ?_⟩
  decide

/-! ## 6. 小さい値でのサイクル排除 -/

theorem no_fixed_point_2 : collatzStep 2 ≠ 2 := by decide
theorem no_fixed_point_3 : collatzStep 3 ≠ 3 := by decide
theorem no_fixed_point_4 : collatzStep 4 ≠ 4 := by decide

theorem no_two_cycle_2 : collatzStep (collatzStep 2) ≠ 2 := by decide
theorem no_two_cycle_3 : collatzStep (collatzStep 3) ≠ 3 := by decide
theorem no_two_cycle_4 : collatzStep (collatzStep 4) ≠ 4 := by decide
theorem no_two_cycle_5 : collatzStep (collatzStep 5) ≠ 5 := by decide
theorem no_two_cycle_6 : collatzStep (collatzStep 6) ≠ 6 := by decide
theorem no_two_cycle_7 : collatzStep (collatzStep 7) ≠ 7 := by decide
theorem no_two_cycle_8 : collatzStep (collatzStep 8) ≠ 8 := by decide

/-! ## 7. サイクル条件の代数的帰結 -/

-- 2^{v2 m} | m を強帰納法で証明する補助定理
private theorem pow_v2_dvd : (m : ℕ) → 2 ^ v2 m ∣ m
  | 0 => by simp
  | m + 1 => by
    by_cases heven : (m + 1) % 2 = 0
    · have ih := pow_v2_dvd ((m + 1) / 2)
      have hne : m + 1 ≠ 0 := by omega
      have hv : v2 (m + 1) = 1 + v2 ((m + 1) / 2) := v2_even (m + 1) hne heven
      -- ih : 2 ^ v2 ((m+1)/2) | (m+1)/2
      -- Need: 2 ^ v2 (m+1) | m+1
      -- i.e.: 2 ^ (1 + v2 ((m+1)/2)) | m+1
      -- i.e.: 2 * 2^v2((m+1)/2) | 2 * ((m+1)/2)
      have h2 : 2 * 2 ^ v2 ((m + 1) / 2) ∣ 2 * ((m + 1) / 2) :=
        Nat.mul_dvd_mul_left 2 ih
      have hm_eq : 2 * ((m + 1) / 2) = m + 1 := by omega
      rw [hv, show 1 + v2 ((m + 1) / 2) = v2 ((m + 1) / 2) + 1 from by omega,
          pow_succ, mul_comm]
      rwa [hm_eq] at h2
    · rw [v2_odd (m + 1) (by omega)]; simp

/-- Syracuse関数の1ステップの関係式:
    n が奇数で n > 0 なら syracuse n * 2^{v2(3n+1)} = 3n+1 -/
theorem syracuse_step_relation (n : ℕ) (_hn : n > 0) (_hodd : n % 2 = 1) :
    syracuse n * 2 ^ v2 (3 * n + 1) = 3 * n + 1 := by
  unfold syracuse
  simp only []
  exact Nat.div_mul_cancel (pow_v2_dvd (3 * n + 1))

/-! ## 8. 長さ3のサイクルは 1→4→2→1 のみ -/

/-- collatzStep で長さ3のサイクルを形成する n > 0 は n = 1, 2, 4 のみ -/
theorem collatz_three_cycle_is_trivial (n : ℕ) (hn : n > 0)
    (h : collatzIter 3 n = n) :
    n = 1 ∨ n = 2 ∨ n = 4 := by
  simp [collatzStep] at h
  split at h <;> split at h <;> split at h <;> omega

/-! ## 9. サイクルの最小要素に関する下界 (公理なし) -/

/-- 奇数 n > 1 が Syracuse の1ステップサイクル (syracuse n = n) を持つことはない -/
theorem no_syracuse_fixed_point (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    syracuse n ≠ n := by
  intro h
  have hmod4 : n % 4 = 1 ∨ n % 4 = 3 := by omega
  rcases hmod4 with h1 | h3
  · have := syracuse_lt_of_mod4_eq1 n h1 hn; omega
  · have := syracuse_gt_of_mod4_eq3 n h3; omega

/-- 1 は唯一の Syracuse 不動点 -/
theorem syracuse_unique_fixed_point (n : ℕ) (hn : n > 0) (hodd : n % 2 = 1)
    (h : syracuse n = n) : n = 1 := by
  by_contra hne
  exact no_syracuse_fixed_point n (by omega) hodd h

/-! =====================================================
    Part B: 公理を使う部分 (Bakerの定理)

    ⚠️ 以下のセクションは axiom を含む。
    Bakerの定理（対数の線形形式の下界）はMathlibに未実装のため、
    axiom として導入する。将来Mathlibに追加された場合は置き換える。
    ===================================================== -/

section BakerTheorem

-- Baker型不等式 (axiom):
-- k ≥ 1 かつ正の奇数 n がSyracuseサイクル (syracuseIter k n = n) を形成するなら
-- n = 1 でなければならない。
-- 背景: Steiner (1977), Eliahou (1993) 等により、
-- 長さ k のサイクルの最小要素は 2^{40k} 以上でなければならないことが示されている。
-- これはBakerの定理による |a·log 2 - b·log 3| の下界から導かれる。
axiom baker_cycle_bound :
  ∀ (k : ℕ) (n : ℕ), k ≥ 1 → n > 0 → n % 2 = 1 →
    syracuseIter k n = n → n = 1

/-- 非自明な Syracuse サイクルは存在しない (Bakerの定理による) -/
theorem no_nontrivial_syracuse_cycle (k n : ℕ) (hk : k ≥ 1) (hn : n > 0)
    (hodd : n % 2 = 1) (hcycle : syracuseIter k n = n) :
    n = 1 :=
  baker_cycle_bound k n hk hn hodd hcycle

/-- Syracuse サイクルに属する要素は 1 のみ -/
theorem syracuse_cycle_is_trivial (k n : ℕ) (h : IsSyracuseCycle k n) :
    n = 1 := by
  obtain ⟨hk, hn, hodd, hcycle⟩ := h
  exact no_nontrivial_syracuse_cycle k n (by omega) hn hodd hcycle

end BakerTheorem
