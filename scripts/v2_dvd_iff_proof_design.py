"""
v2_dvd_iff の詳細証明設計

3つの定理:
  1. dvd_of_v2_ge: v2 m >= k -> 2^k | m
  2. v2_ge_of_dvd: m > 0 -> 2^k | m -> v2 m >= k
  3. v2_ge_iff_dvd: m > 0 -> (v2 m >= k <-> 2^k | m)
"""

print("""
=== 定理1: dvd_of_v2_ge ===
ステートメント: ∀ m k : ℕ, v2 m ≥ k → 2^k ∣ m

証明:
  v2 m ≥ k  →  2^k ∣ 2^(v2 m)  (pow_dvd_pow 2)
  2^(v2 m) ∣ m  (two_pow_v2_dvd)
  → dvd_trans で完了

Lean:
  theorem dvd_of_v2_ge (m k : ℕ) (h : v2 m ≥ k) : 2 ^ k ∣ m :=
    dvd_trans (pow_dvd_pow 2 h) (two_pow_v2_dvd m)

注: pow_dvd_pow は Mathlib.Algebra.GroupPower の定理
  pow_dvd_pow (a : M) {m n : ℕ} (h : m ≤ n) : a ^ m ∣ a ^ n


=== 定理2: v2_ge_of_dvd ===
ステートメント: ∀ m k : ℕ, m > 0 → 2^k ∣ m → v2 m ≥ k

k帰納法 (mは全称):

k=0: v2 m ≥ 0 は omega で自明

k+1:
  仮定: 2^(k+1) ∣ m, m > 0
  IH: ∀ m', m' > 0 → 2^k ∣ m' → v2 m' ≥ k

  Step 1: mは偶数
    2^(k+1) = 2 * 2^k ∣ m → 2 ∣ m → m % 2 = 0
    証明: dvd_pow_self 2 (Nat.succ_ne_zero k) : 2 ∣ 2^(k+1)
          dvd_trans ... h : 2 ∣ m

  Step 2: v2 m = 1 + v2 (m/2)
    v2_even m (by omega) heven

  Step 3: 2^k ∣ (m/2)
    Nat.dvd_div_iff_mul_dvd (from 2 ∣ m):
      2^k ∣ m/2 ↔ 2^k * 2 ∣ m
    2^k * 2 = 2^(k+1) (by pow_succ or ring)
    h : 2^(k+1) ∣ m
    → 2^k ∣ m/2

  Step 4: IH適用
    m/2 > 0 (m > 0, m偶数 → m ≥ 2 → m/2 ≥ 1)
    ih (m/2) ... : v2(m/2) ≥ k

  Step 5: 結論
    v2 m = 1 + v2(m/2) ≥ 1 + k = k + 1

Lean:

theorem v2_ge_of_dvd (m k : ℕ) (hm : m > 0) (h : 2 ^ k ∣ m) : v2 m ≥ k := by
  induction k generalizing m with
  | zero => omega
  | succ k ih =>
    -- Step 1: m is even
    have h2m : 2 ∣ m := by
      exact dvd_trans (dvd_pow_self 2 (Nat.succ_ne_zero k)) h
    have heven : m % 2 = 0 := Nat.mod_eq_zero_of_dvd h2m
    have hne : m ≠ 0 := by omega
    -- Step 2: unfold v2
    rw [v2_even m hne heven]
    -- Step 3: 2^k | m/2
    have hdvd_half : 2 ^ k ∣ m / 2 := by
      rwa [Nat.dvd_div_iff_mul_dvd h2m, pow_succ]
    -- Step 4 & 5: IH
    have hm2_pos : m / 2 > 0 := by omega
    have := ih (m / 2) hm2_pos hdvd_half
    omega

注意点:
  - induction k generalizing m が必要（mがkの帰納法の中で変わる）
  - Nat.dvd_div_iff_mul_dvd の引数: (hbc : c ∣ b) → (a ∣ b / c ↔ c * a ∣ b)
    ここで c=2, b=m, a=2^k なので
    h2m : 2 ∣ m → (2^k ∣ m/2 ↔ 2 * 2^k ∣ m)
  - pow_succ: 2^(k+1) = 2^k * 2 なので mul_comm が必要かも
    pow_succ' で a^(n+1) = a^n * a
    pow_succ で a^(n+1) = a * a^n
    → 2 * 2^k = 2^(k+1) = 2^k * 2
    rwa で h: 2^(k+1)|m を 2*2^k | m に書き換えたい
    pow_succ: 2^(k+1) = 2 * 2^k → h を rw するならこちら


=== 定理3: v2_ge_iff_dvd ===

theorem v2_ge_iff_dvd (m k : ℕ) (hm : m > 0) : v2 m ≥ k ↔ 2 ^ k ∣ m :=
  ⟨dvd_of_v2_ge m k, v2_ge_of_dvd m k hm⟩


=== 追加: v2_eq_iff ===
v2 m = k ↔ 2^k | m ∧ ¬(2^(k+1) | m) (m > 0)

これはv2_ge_iff_dvdから導出可能:
  v2 m = k ↔ v2 m ≥ k ∧ ¬(v2 m ≥ k+1)
           ↔ 2^k | m ∧ ¬(2^(k+1) | m)

theorem v2_eq_iff (m k : ℕ) (hm : m > 0) :
    v2 m = k ↔ 2 ^ k ∣ m ∧ ¬(2 ^ (k + 1) ∣ m) := by
  constructor
  · intro heq
    constructor
    · exact dvd_of_v2_ge m k (by omega)
    · intro h
      have := v2_ge_of_dvd m (k + 1) hm h
      omega
  · intro ⟨hge, hlt⟩
    have h1 := v2_ge_of_dvd m k hm hge
    by_contra hne
    have h2 : v2 m ≥ k + 1 := by omega
    exact hlt (dvd_of_v2_ge m (k + 1) h2)


=== 依存関係のチェック ===

Mathlibから必要な補題:
  1. pow_dvd_pow (a : M) (h : m ≤ n) : a^m ∣ a^n
     -- Mathlib.Algebra.GroupPower / Init
  2. dvd_trans
     -- 標準ライブラリ
  3. dvd_pow_self (a : α) (hn : n ≠ 0) : a ∣ a^n
     -- Mathlib.Algebra.Divisibility.Basic
  4. Nat.mod_eq_zero_of_dvd / Nat.dvd_of_mod_eq_zero
     -- 標準ライブラリ
  5. Nat.dvd_div_iff_mul_dvd (hbc : c ∣ b) : a ∣ b/c ↔ c*a ∣ b
     -- Mathlib.Data.Nat.Defs or Init
  6. pow_succ: a^(n+1) = a * a^n
     -- 標準ライブラリ

プロジェクト内で必要な補題:
  1. two_pow_v2_dvd (m : ℕ) : 2 ^ v2 m ∣ m
     -- Structure.lean で定義済み
  2. v2_even (n : ℕ) (hn : n ≠ 0) (h : n % 2 = 0) : v2 n = 1 + v2 (n / 2)
     -- Defs.lean で定義済み

配置場所: Structure.lean の two_pow_v2_dvd の直後が最適
""")

# pow_succ の方向の確認
print("\n=== pow_succ 方向検証 ===")
print("Lean 4 (Mathlib):")
print("  pow_succ:  a^(n+1) = a * a^n  (左乗法)")
print("  pow_succ': a^(n+1) = a^n * a  (右乗法)")
print("")
print("Nat.dvd_div_iff_mul_dvd の形: a ∣ b/c ↔ c*a ∣ b")
print("  c=2, a=2^k, b=m")
print("  2^k ∣ m/2 ↔ 2 * 2^k ∣ m")
print("  2 * 2^k = 2^(k+1)  (by pow_succ)")
print("  h: 2^(k+1) ∣ m を rw [pow_succ] at h で 2 * 2^k ∣ m に")
print("  → rwa で ok")
