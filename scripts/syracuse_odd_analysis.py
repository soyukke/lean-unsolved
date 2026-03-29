"""
syracuse(n) が常に奇数を返すことの分析
核心: m / 2^v2(m) は任意の m > 0 に対して奇数

証明戦略の設計:
1. v2(m) の定義により、2^v2(m) | m（証明済: two_pow_v2_dvd）
2. m / 2^v2(m) が偶数と仮定すると矛盾を導く
3. 中間補題: m > 0 のとき v2(m) は maximal、すなわち 2^(v2(m)+1) | m が成り立たない
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function"""
    m = 3 * n + 1
    return m // (2 ** v2(m))

# 検証1: syracuse(n) は常に奇数か？
print("=== 検証1: syracuse(n) の奇数性 (n=1..1000, 奇数のみ) ===")
violations = []
for n in range(1, 1001, 2):
    s = syracuse(n)
    if s % 2 == 0:
        violations.append((n, s))
if violations:
    print(f"  反例発見: {violations[:10]}")
else:
    print(f"  全ての奇数 n in [1,999] で syracuse(n) は奇数 [OK]")

# 検証2: m / 2^v2(m) は常に奇数か？ (一般的な補題)
print("\n=== 検証2: m / 2^v2(m) の奇数性 (m=1..1000) ===")
violations2 = []
for m in range(1, 1001):
    q = m // (2 ** v2(m))
    if q % 2 == 0:
        violations2.append((m, v2(m), q))
if violations2:
    print(f"  反例発見: {violations2[:10]}")
else:
    print(f"  全ての m in [1,1000] で m/2^v2(m) は奇数 [OK]")

# 検証3: v2 の maximality (2^(v2(m)+1) は m を割らない)
print("\n=== 検証3: v2 の maximality ===")
violations3 = []
for m in range(1, 1001):
    v = v2(m)
    if m % (2 ** (v + 1)) == 0:
        violations3.append((m, v))
if violations3:
    print(f"  maximality が破れた例: {violations3[:10]}")
else:
    print(f"  全ての m in [1,1000] で 2^(v2(m)+1) ∤ m [OK]")

# 証明戦略の分析
print("\n=== 証明戦略の分析 ===")
print("""
■ 目標定理: syracuse_odd
  statement: forall n : Nat, n >= 1 -> n % 2 = 1 -> syracuse n % 2 = 1

■ 必要な中間補題:
  (A) odd_of_div_two_pow_v2: forall m : Nat, m > 0 -> (m / 2^v2(m)) % 2 = 1
      つまり: 2-adic valuation で2べき部分を完全に除去すると奇数になる

■ 補題(A)の証明戦略:
  方法1: 背理法 + v2_ge_iff_dvd
    m / 2^v2(m) が偶数と仮定
    -> 2 | (m / 2^v2(m))
    -> 2^(v2(m)+1) | m   (by Nat.mul_dvd_mul + two_pow_v2_dvd)
    -> v2(m) >= v2(m) + 1  (by v2_ge_iff_dvd の逆方向)
    -> 矛盾

  方法2: 直接的にv2の定義による強帰納法
    m = 0: 不要 (m > 0 の前提)
    m が奇数: v2(m) = 0, m / 2^0 = m, 奇数
    m が偶数: v2(m) = 1 + v2(m/2),
      m / 2^v2(m) = m / 2^(1+v2(m/2)) = (m/2) / 2^v2(m/2)
      帰納法の仮定より (m/2) / 2^v2(m/2) は奇数
""")

# 方法1の詳細分析
print("\n=== 方法1: 背理法の詳細 ===")
print("""
lemma odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  by_contra h
  push_neg at h  -- h : (m / 2^v2 m) % 2 <> 1
  -- (m / 2^v2 m) は 0 でない (m > 0 より) ので偶数
  have heven : (m / 2^v2 m) % 2 = 0 := by omega
  -- 2 | (m / 2^v2 m)
  have h2dvd : 2 | (m / 2^v2 m) := Nat.dvd_of_mod_eq_zero heven
  -- 2^v2(m) | m (証明済)
  have hpow_dvd := two_pow_v2_dvd m
  -- 2 * 2^v2(m) | m
  -- 具体的には: m / 2^v2(m) = q とおくと m = q * 2^v2(m)
  -- q が偶数なので q = 2 * q', m = 2*q' * 2^v2(m) = q' * 2^(v2(m)+1)
  -- したがって 2^(v2(m)+1) | m
  have h_next : 2^(v2 m + 1) | m := by
    ...
  -- v2_ge_of_dvd より v2(m) >= v2(m) + 1
  have := v2_ge_of_dvd m (v2 m + 1) hm h_next
  omega
""")

# 方法2の詳細分析
print("\n=== 方法2: 強帰納法の詳細 ===")
print("""
lemma odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hm0 : m = 0
    . omega  -- m > 0 と矛盾
    . by_cases hodd : m % 2 = 1
      . -- m が奇数: v2 m = 0, m / 2^0 = m / 1 = m
        rw [v2_odd m (by omega)]
        simp
        exact hodd
      . -- m が偶数: v2 m = 1 + v2(m/2)
        push_neg at hodd
        have heven : m % 2 = 0 := by omega
        rw [v2_even m hm0 heven]
        -- m / 2^(1 + v2(m/2)) = m / (2 * 2^v2(m/2))
        -- = (m/2) / 2^v2(m/2)
        have hkey : m / 2^(1 + v2(m/2)) = (m/2) / 2^v2(m/2) := by
          rw [pow_add, pow_one]
          rw [Nat.div_div_eq_div_mul]
        rw [hkey]
        -- 帰納法: m/2 < m, m/2 > 0
        exact ih (m/2) (by omega) (by omega)
""")

# 方法2のステップバイステップ検証
print("\n=== 方法2のステップ検証 (偶数の場合) ===")
for m in [2, 4, 6, 8, 12, 16, 24, 32, 48]:
    v = v2(m)
    half = m // 2
    v_half = v2(half)
    result_direct = m // (2 ** v)
    result_recursive = half // (2 ** v_half)
    print(f"  m={m}: v2(m)={v}, m/2^v2={result_direct}, "
          f"m/2={half}, v2(m/2)={v_half}, (m/2)/2^v2(m/2)={result_recursive}, "
          f"一致={result_direct == result_recursive}")

# syracuse_odd 定理の完全な証明
print("\n=== syracuse_odd 定理の完全な Lean 証明設計 ===")
print("""
/-- m > 0 のとき m / 2^v2(m) は奇数 -/
theorem odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hodd : m % 2 = 1
    · -- m が奇数
      rw [v2_odd m (by omega), pow_zero, Nat.div_one]
      exact hodd
    · -- m が偶数
      push_neg at hodd
      have heven : m % 2 = 0 := by omega
      have hm0 : m <> 0 := by omega
      rw [v2_even m hm0 heven, pow_succ, Nat.div_div_eq_div_mul,
          Nat.mul_comm]
      -- 目標: m / (2 * 2 ^ v2 (m/2)) % 2 = 1
      -- = (m / 2) / 2^v2(m/2) % 2 = 1
      -- ただし Nat.div_div_eq_div_mul で
      -- m / (2^1 * 2^v2(m/2)) = m / (2 * 2^v2(m/2))
      -- これは必ずしも (m/2) / 2^v2(m/2) と等しくない（自然数除算）
      -- 正確には: m / (a * b) = (m / a) / b が成り立つには a | m が必要
      -- 2 | m は heven から成立
      -- よって正確には:
      rw [Nat.div_div_eq_div_mul] -- m / 2 / 2^v2(m/2)
      -- hmm, pow_succ と div_div の順序に注意
      sorry

-- 代替アプローチ: pow_succ を直接使わず、div_div を活用
/-- 改善版 -/
theorem odd_of_div_two_pow_v2' (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hodd : m % 2 = 1
    · rw [v2_odd m (by omega), pow_zero, Nat.div_one]
      exact hodd
    · have heven : m % 2 = 0 := by omega
      have hm0 : m <> 0 := by omega
      have hm2_pos : m / 2 > 0 := by omega
      rw [v2_even m hm0 heven]
      -- v2 m = 1 + v2(m/2)
      -- 2 ^ (1 + v2(m/2)) = 2 * 2 ^ v2(m/2)
      -- m / (2 * 2^v2(m/2))
      -- 2 | m なので m = 2 * (m/2)
      -- m / (2 * k) = (m/2) / k when 2 | m
      -- つまり Nat.mul_div_mul_left 的な補題が必要
      have h2dvd : 2 | m := Nat.dvd_of_mod_eq_zero (by omega)
      have := ih (m / 2) (Nat.div_lt_self (by omega) (by omega)) hm2_pos
      -- this : (m/2) / 2^v2(m/2) % 2 = 1
      -- 目標: m / 2^(1 + v2(m/2)) % 2 = 1
      -- = m / (2 * 2^v2(m/2)) % 2 = 1
      -- m = 2*(m/2) なので
      -- 2*(m/2) / (2 * 2^v2(m/2)) = (m/2) / 2^v2(m/2)
      convert this using 1
      rw [pow_succ, mul_comm]
      -- 目標: m / (2^v2(m/2) * 2) = m/2 / 2^v2(m/2)
      -- Nat.div_div_eq_div_mul の逆: a / (b * c) = a / b / c
      rw [<- Nat.div_div_eq_div_mul]
      -- 目標: m / 2 ^ v2 (m / 2) / 2 = m / 2 / 2 ^ v2 (m / 2)
      -- ここで問題: 除算の順序が違う
      sorry
""")

# Lean の Nat.div_div_eq_div_mul の動作確認
print("\n=== Nat.div_div の動作 ===")
print("Nat.div_div_eq_div_mul: a / b / c = a / (b * c)")
for m in [24, 48, 12, 8]:
    v = v2(m)
    half = m // 2
    v_half = v2(half)

    # m / 2^v = m / 2^(1+v_half) = m / (2 * 2^v_half)
    lhs = m // (2 ** v)

    # (m / 2) / 2^v_half  (div_div 方向)
    rhs_way1 = (m // 2) // (2 ** v_half)

    # m / (2^v_half) / 2  (逆順)
    rhs_way2 = (m // (2 ** v_half)) // 2

    # m / (2 * 2^v_half)
    rhs_way3 = m // (2 * (2 ** v_half))

    print(f"  m={m}, v2={v}, v2(m/2)={v_half}:")
    print(f"    m/2^v2(m) = {lhs}")
    print(f"    (m/2)/2^v2(m/2) = {rhs_way1}")
    print(f"    m/2^v2(m/2)/2 = {rhs_way2}")
    print(f"    m/(2*2^v2(m/2)) = {rhs_way3}")

# 正しい変換ルート
print("\n=== 正しい証明ルート ===")
print("""
核心の等式: m > 0, m偶数のとき
  m / 2^(1 + v2(m/2)) = (m/2) / 2^v2(m/2)

これは次のように示せる:
  2^(1 + v2(m/2)) = 2 * 2^v2(m/2)     -- pow_succ
  m / (2 * 2^v2(m/2))
  = m / 2 / 2^v2(m/2)                  -- Nat.div_div_eq_div_mul (逆方向)
  つまり a / (b*c) = a/b/c  -> m / (2 * k) = m/2/k

Lean では:
  Nat.div_div_eq_div_mul : a / b / c = a / (b * c)

  逆方向: m / (b*c) を m/b/c に変換
  rw [<- Nat.div_div_eq_div_mul]  -- NG: 方向が逆

  正方向: m / (2 * k) と書いてから
  have : m / (2 * k) = m / 2 / k  -- これを直接示す

  Lean 4 Mathlib には Nat.div_div_eq_div_mul がある:
    n / a / b = n / (a * b)

  したがって:
  (m / 2) / 2^v2(m/2)     -- 目標をこの形に変形したい
  = m / (2 * 2^v2(m/2))   -- by Nat.div_div_eq_div_mul
  = m / 2^(1 + v2(m/2))   -- by pow_succ, mul_comm

結局:
  目標: m / 2^(1 + v2(m/2)) % 2 = 1
  = m / (2 * 2^v2(m/2)) % 2 = 1    [pow_succ, mul_comm]
  IH: (m/2) / 2^v2(m/2) % 2 = 1
  (m/2) / 2^v2(m/2) = m/2 / 2^v2(m/2)   [同じもの]

  示すべき: m / (2 * 2^v2(m/2)) = m/2 / 2^v2(m/2)
  これは Nat.div_div_eq_div_mul の逆:
    m/2 / 2^v2(m/2) = m / (2 * 2^v2(m/2))

完全な Lean 証明:

theorem odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hodd : m % 2 = 1
    . rw [v2_odd m (by omega), pow_zero, Nat.div_one]
      exact hodd
    . have heven : m % 2 = 0 := by omega
      have hm0 : m <> 0 := by omega
      have hm2_pos : m / 2 > 0 := by omega
      rw [v2_even m hm0 heven]
      -- 目標: m / 2 ^ (1 + v2 (m / 2)) % 2 = 1
      -- 2 ^ (1 + v2(m/2)) = 2 * 2^v2(m/2)
      conv_lhs => rw [pow_succ, mul_comm]
      -- 目標: m / (2^v2(m/2) * 2) % 2 = 1
      -- Nat.div_div_eq_div_mul: a / b / c = a / (b * c) ⟸  m / (k * 2) = m / k / 2
      -- hmm, 順序の問題がある
      -- 実は pow_succ: 2^(n+1) = 2^n * 2 (Lean 4 Mathlibでは 2 * 2^n かも)
      -- pow_succ' : 2^(n+1) = 2^n * 2
      -- 確認が必要
      sorry
""")

# pow_succ の方向確認
print("\n=== pow_succ の展開方向 (Lean 4) ===")
print("Lean 4 Mathlib:")
print("  pow_succ (a : M) (n : Nat) : a ^ (n + 1) = a ^ n * a")
print("  pow_succ' は存在しない場合がある")
print("")
print("したがって: 2^(1 + v2(m/2)) = 2^(v2(m/2) + 1) = 2^v2(m/2) * 2")
print("(1 + v2(m/2) を v2(m/2) + 1 に書き換えてから pow_succ を使う)")

# 最終的な証明スケッチ
print("\n=== 最終的な証明スケッチ ===")
print("""
-- 中間補題: m / 2^v2(m) は奇数
theorem odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  induction m using Nat.strongRecOn with
  | ind m ih =>
    by_cases hodd : m % 2 = 1
    . -- m が奇数: v2(m) = 0
      rw [v2_odd m (by omega), pow_zero, Nat.div_one]
      exact hodd
    . -- m が偶数
      have heven : m % 2 = 0 := by omega
      have hne : m <> 0 := by omega
      have hm2_pos : m / 2 > 0 := by omega
      rw [v2_even m hne heven]
      -- 目標: m / 2 ^ (1 + v2 (m / 2)) % 2 = 1
      -- 1 + v2(m/2) = v2(m/2) + 1 への書き換え
      rw [Nat.add_comm]
      -- 目標: m / 2 ^ (v2(m/2) + 1) % 2 = 1
      rw [pow_succ]
      -- 目標: m / (2 ^ v2(m/2) * 2) % 2 = 1
      rw [<- Nat.div_div_eq_div_mul]
      -- 目標: m / 2 ^ v2(m/2) / 2 % 2 = 1
      -- ここで困る: m / 2^v2(m/2) / 2 を (m/2) / 2^v2(m/2) に変形したい
      -- しかしこれは一般に成り立たない
      -- 実は m / a / b = m / b / a は自然数除算では成り立たない！
      -- 特別な条件（割り切れる場合）が必要
      sorry

-- より良いアプローチ: 背理法を使う

/-- v2 の maximality: 2^(v2(m)+1) は m を割らない (m > 0 のとき) -/
theorem not_dvd_two_pow_succ_v2 (m : Nat) (hm : m > 0) :
    ¬ (2 ^ (v2 m + 1) ∣ m) := by
  intro h
  have := v2_ge_of_dvd m (v2 m + 1) hm h
  omega

/-- m / 2^v2(m) は奇数 (背理法版) -/
theorem odd_of_div_two_pow_v2 (m : Nat) (hm : m > 0) :
    (m / 2 ^ v2 m) % 2 = 1 := by
  by_contra h
  have heven : (m / 2 ^ v2 m) % 2 = 0 := by omega
  -- m / 2^v2(m) > 0
  have hq_pos : m / 2 ^ v2 m > 0 := Nat.div_pos (pow_v2_le m hm) (by positivity)
  -- 2 | (m / 2^v2(m))
  have h2dvd : 2 ∣ (m / 2 ^ v2 m) := Nat.dvd_of_mod_eq_zero (by omega)
  -- 2^v2(m) | m
  have hpow_dvd : 2 ^ v2 m ∣ m := two_pow_v2_dvd m
  -- 2 * 2^v2(m) | m
  -- m = (m / 2^v2(m)) * 2^v2(m)
  -- m / 2^v2(m) = 2*q なので m = 2*q * 2^v2(m) = q * 2^(v2(m)+1)
  have h_mul : 2 ^ (v2 m + 1) ∣ m := by
    obtain <k, hk> := h2dvd
    obtain <c, hc> := hpow_dvd
    -- hk : m / 2^v2(m) = 2 * k
    -- hc : m = 2^v2(m) * c  (c = m / 2^v2(m))
    -- c = m / 2^v2(m) = 2 * k
    -- m = 2^v2(m) * (2 * k) = 2^(v2(m)+1) * k
    rw [pow_succ]
    -- 目標: 2 ^ v2 m * 2 ∣ m
    have : m = 2 ^ v2 m * (m / 2 ^ v2 m) := (Nat.mul_div_cancel' hpow_dvd).symm
    rw [this]
    exact Nat.mul_dvd_mul_left (2 ^ v2 m) h2dvd
  exact not_dvd_two_pow_succ_v2 m hm h_mul

-- メイン定理
theorem syracuse_odd (n : Nat) (hn : n >= 1) (hodd : n % 2 = 1) :
    syracuse n % 2 = 1 :=
  odd_of_div_two_pow_v2 (3 * n + 1) (by omega)
""")
