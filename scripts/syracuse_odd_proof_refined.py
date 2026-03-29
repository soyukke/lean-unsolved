"""
syracuse_odd の証明設計: 最終版

2つのアプローチを比較し、最も実現可能な証明を特定する。
"""

print("=" * 70)
print("syracuse_odd 証明設計: 最終版")
print("=" * 70)

print("""
============================================================
■ 目標定理
============================================================

theorem syracuse_odd (n : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    syracuse n % 2 = 1

syracuse n = (3*n+1) / 2^v2(3*n+1) なので、
m := 3*n+1 とおけば m > 0 であり、
目標は m / 2^v2(m) % 2 = 1 を示すことに帰着。

============================================================
■ 推奨アプローチ: 背理法 (方法1)
============================================================

理由:
- 自然数除算の煩雑な書き換えを避けられる
- 既存の v2_ge_of_dvd を直接活用できる
- 必要な補題が全て既存

■ 必要な補題 (全て既存):
  1. two_pow_v2_dvd (m : Nat) : 2 ^ v2 m | m
  2. v2_ge_of_dvd (m k : Nat) (hm : m > 0) (h : 2^k | m) : v2 m >= k
  3. pow_v2_le は private だが、
     Nat.le_of_dvd (h1 : m > 0) (h2 : d | m) : d <= m
     + two_pow_v2_dvd で代用可能

■ 新規必要補題: なし！全て既存の定理で完結する。

============================================================
■ 証明の全体構造
============================================================

-- 補助: m > 0 のとき m / 2^v2(m) > 0
-- (pow_v2_le は private なので再証明が必要)
private theorem div_two_pow_v2_pos (m : Nat) (hm : m > 0) :
    m / 2 ^ v2 m > 0 := by
  apply Nat.div_pos
  · exact Nat.le_of_dvd hm (two_pow_v2_dvd m)
  · positivity

-- メイン中間補題
theorem odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  by_contra h
  -- h : ¬ ((m / 2 ^ v2 m) % 2 = 1)
  -- m / 2^v2(m) > 0 なので m / 2^v2(m) % 2 = 0
  have hq_pos : m / 2 ^ v2 m > 0 := div_two_pow_v2_pos m hm
  have heven : (m / 2 ^ v2 m) % 2 = 0 := by omega
  -- Step 1: 2 | (m / 2^v2(m))
  have h2dvd : 2 ∣ (m / 2 ^ v2 m) :=
    Nat.dvd_of_mod_eq_zero (by omega)
  -- Step 2: 2^v2(m) | m (既存定理)
  have hpow_dvd : 2 ^ v2 m ∣ m := two_pow_v2_dvd m
  -- Step 3: 2^(v2(m)+1) | m
  -- m = 2^v2(m) * (m / 2^v2(m)) (割り切れるので)
  -- m / 2^v2(m) = 2 * k なので m = 2^v2(m) * 2 * k = 2^(v2(m)+1) * k
  have h_next : 2 ^ (v2 m + 1) ∣ m := by
    rw [pow_succ]
    -- 目標: 2 ^ v2 m * 2 | m
    -- m = 2^v2(m) * q where q = m / 2^v2(m) and 2 | q
    have hm_eq : m = 2 ^ v2 m * (m / 2 ^ v2 m) :=
      (Nat.mul_div_cancel' hpow_dvd).symm
    rw [hm_eq]
    exact Nat.mul_dvd_mul_left (2 ^ v2 m) h2dvd
  -- Step 4: v2(m) >= v2(m) + 1 (矛盾)
  have hge := v2_ge_of_dvd m (v2 m + 1) hm h_next
  omega

-- メイン定理
theorem syracuse_odd (n : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    syracuse n % 2 = 1 := by
  -- syracuse n = (3*n+1) / 2^v2(3*n+1)
  change (3 * n + 1) / 2 ^ v2 (3 * n + 1) % 2 = 1
  exact odd_of_div_two_pow_v2 (3 * n + 1) (by omega)

============================================================
■ 証明の核心ステップと使用 tactic の一覧
============================================================

Step 1: by_contra + omega
  - 背理法を開始
  - h : ¬ (q % 2 = 1) から q % 2 = 0 を得る (omega)

Step 2: Nat.dvd_of_mod_eq_zero
  - q % 2 = 0 から 2 | q を得る

Step 3: two_pow_v2_dvd (既存定理)
  - 2^v2(m) | m

Step 4: Nat.mul_div_cancel' + rw
  - m = 2^v2(m) * (m / 2^v2(m)) を得る

Step 5: pow_succ + Nat.mul_dvd_mul_left
  - 2^(v2+1) = 2^v2 * 2 と書き換え
  - 2 | q から 2^v2 * 2 | 2^v2 * q = m

Step 6: v2_ge_of_dvd (既存定理)
  - 2^(v2+1) | m から v2(m) >= v2(m)+1

Step 7: omega
  - v2(m) >= v2(m)+1 は矛盾

============================================================
■ 別解: 帰納法 (方法2) - より洗練された版
============================================================

-- 自然数除算の問題を omega で解決する版
theorem odd_of_div_two_pow_v2_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hodd : m % 2 = 1
    · -- m 奇数: v2(m) = 0
      rw [v2_odd m (by omega), pow_zero, Nat.div_one]
      exact hodd
    · -- m 偶数
      have heven : m % 2 = 0 := by omega
      have hne : m ≠ 0 := by omega
      have hm2_pos : m / 2 > 0 := by omega
      rw [v2_even m hne heven]
      -- 目標: m / 2 ^ (1 + v2 (m / 2)) % 2 = 1
      -- 核心: m / 2^(1+k) = (m/2) / 2^k (m が偶数のとき)
      -- これは omega では解けないが、以下の補題で対処
      have hkey : m / 2 ^ (1 + v2 (m / 2)) = (m / 2) / 2 ^ v2 (m / 2) := by
        -- m = 2 * (m/2) (m が偶数)
        have hm_eq : m = 2 * (m / 2) := by omega
        conv_lhs => rw [hm_eq]
        rw [show 1 + v2 (m / 2) = v2 (m / 2) + 1 from by omega, pow_succ]
        -- 目標: 2 * (m/2) / (2^v2(m/2) * 2) = (m/2) / 2^v2(m/2)
        rw [Nat.mul_comm (2 ^ v2 (m / 2)) 2]
        -- 目標: 2 * (m/2) / (2 * 2^v2(m/2)) = (m/2) / 2^v2(m/2)
        rw [Nat.mul_div_mul_left _ _ (by omega : 0 < 2)]
        -- Nat.mul_div_mul_left: (d * n) / (d * m) = n / m (d > 0)
      rw [hkey]
      exact ih (m / 2) (Nat.div_lt_self (by omega) (by omega)) hm2_pos

============================================================
■ 使用する Mathlib 定理の確認
============================================================

必要な Mathlib/Core の定理:
1. Nat.mul_div_cancel' : d | m -> d * (m / d) = m
   (逆方向: (Nat.mul_div_cancel' h).symm : m = d * (m / d))
2. Nat.dvd_of_mod_eq_zero : m % d = 0 -> d | m
3. Nat.mul_dvd_mul_left : d | b -> a * d | a * b
   (正確には: a * d | a * b ⟸ d | b, Nat.mul_dvd_mul_left a h)
4. Nat.div_pos : d <= m -> 0 < d -> 0 < m / d
5. Nat.le_of_dvd : 0 < m -> d | m -> d <= m
6. Nat.mul_div_mul_left (n m : Nat) (hk : 0 < k) : k * n / (k * m) = n / m

方法1で使用: 1, 2, 3, 4, 5 + two_pow_v2_dvd + v2_ge_of_dvd
方法2で使用: 6 + v2_odd + v2_even + Nat.strongRecOn

============================================================
■ 推奨: 方法1（背理法）
============================================================

理由:
1. 既存定理のみで完結（新しい補題不要）
2. 自然数除算のトリッキーな等式を避けられる
3. 証明が短い（約15行）
4. 各ステップが明確で検証しやすい

方法2も有力だが、Nat.mul_div_mul_left の正確な型シグネチャの
確認が必要で、Lean 4 の版違いによるリスクがある。
""")
