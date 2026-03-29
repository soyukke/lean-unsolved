#!/usr/bin/env python3
"""
探索178: root(m) の Lean 形式化設計 - 詳細版

既存の利用可能な補題:
- v2_two_mul (n : N) (hn : n != 0) : v2 (2 * n) = 1 + v2 n
- v2_odd (n : N) (h : n % 2 != 0) : v2 n = 0
- v2_even (n : N) (hn : n != 0) (h : n % 2 = 0) : v2 n = 1 + v2 (n / 2)
- syracuse_four_mul_add_one (n : N) (hn : n >= 1) (hodd : n % 2 = 1) :
    syracuse (4 * n + 1) = syracuse n

新しく証明すべき定理と詳細な証明戦略
"""

print("=" * 70)
print("Lean 4 形式化設計: root(m) の mod 6 場合分け")
print("=" * 70)

lean_design = r"""
/-!
# Syracuse 逆像の根: mod 6 場合分け (探索178)

奇数 m (ただし 3 ∤ m) に対して、syracuse(r) = m を満たす
最小の奇数 r (= root(m)) の明示公式を証明する。

## 主要結果
- `syracuse_root_mod6_eq1`: m ≡ 1 (mod 6) → syracuse((4m-1)/3) = m
- `syracuse_root_mod6_eq5`: m ≡ 5 (mod 6) → syracuse((2m-1)/3) = m

## 証明の核心
mod 6 の条件から自然数の除算が正確になることを利用。
3 * ((4m-1)/3) + 1 = 4m (m ≡ 1 mod 6 のとき)
3 * ((2m-1)/3) + 1 = 2m (m ≡ 5 mod 6 のとき)
-/

import Unsolved.Collatz.Structure -- syracuse_four_mul_add_one を利用

/-! ## 補助補題 1: 自然数除算の正確性 -/

/-- m ≡ 1 (mod 6) のとき (4m - 1) は 3 で割り切れる -/
theorem four_mul_sub_one_mod3_of_mod6_eq1 (m : ℕ) (h : m % 6 = 1) :
    (4 * m - 1) % 3 = 0 := by
  omega

/-- m ≡ 1 (mod 6) のとき 3 * ((4m-1)/3) = 4m - 1 -/
theorem three_mul_four_sub_div3_of_mod6_eq1 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
    3 * ((4 * m - 1) / 3) = 4 * m - 1 := by
  -- m >= 1 and m % 6 = 1 imply 4m >= 4 > 1, so 4m - 1 >= 3
  -- (4m - 1) % 3 = 0 from the mod condition
  have h1 : 4 * m ≥ 4 := by omega
  have h2 : (4 * m - 1) % 3 = 0 := by omega
  -- Nat.div_mul_cancel or omega should work
  omega

/-- m ≡ 1 (mod 6) のとき、核心等式: 3 * ((4m-1)/3) + 1 = 4m -/
theorem key_eq_mod6_eq1 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
    3 * ((4 * m - 1) / 3) + 1 = 4 * m := by
  have := three_mul_four_sub_div3_of_mod6_eq1 m hm h
  omega

/-- m ≡ 5 (mod 6) のとき (2m - 1) は 3 で割り切れる -/
theorem two_mul_sub_one_mod3_of_mod6_eq5 (m : ℕ) (h : m % 6 = 5) :
    (2 * m - 1) % 3 = 0 := by
  omega

/-- m ≡ 5 (mod 6) のとき、核心等式: 3 * ((2m-1)/3) + 1 = 2m -/
theorem key_eq_mod6_eq5 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 5) :
    3 * ((2 * m - 1) / 3) + 1 = 2 * m := by
  omega

/-! ## 補助補題 2: root の奇数性 -/

/-- m ≡ 1 (mod 6) のとき (4m-1)/3 は奇数 -/
theorem root_odd_mod6_eq1 (m : ℕ) (h : m % 6 = 1) :
    ((4 * m - 1) / 3) % 2 = 1 := by
  -- m = 6k+1, (4m-1)/3 = (24k+3)/3 = 8k+1, which is odd
  omega

/-- m ≡ 5 (mod 6) のとき (2m-1)/3 は奇数 -/
theorem root_odd_mod6_eq5 (m : ℕ) (h : m % 6 = 5) :
    ((2 * m - 1) / 3) % 2 = 1 := by
  -- m = 6k+5, (2m-1)/3 = (12k+9)/3 = 4k+3, which is odd
  omega

/-! ## 補助補題 3: v2 の計算 -/

/-- m が奇数のとき v2(4m) = 2 -/
theorem v2_four_mul_odd (m : ℕ) (hm : m ≥ 1) (hodd : m % 2 = 1) :
    v2 (4 * m) = 2 := by
  -- 4m = 2 * (2 * m)
  rw [show (4 : ℕ) * m = 2 * (2 * m) from by ring]
  rw [v2_two_mul (2 * m) (by omega)]
  rw [v2_two_mul m (by omega)]
  rw [v2_odd m (by omega)]

/-- m が奇数のとき v2(2m) = 1 -/
theorem v2_two_mul_odd (m : ℕ) (hm : m ≥ 1) (hodd : m % 2 = 1) :
    v2 (2 * m) = 1 := by
  rw [v2_two_mul m (by omega)]
  rw [v2_odd m (by omega)]

/-! ## 主定理 -/

/-- ★ m ≡ 1 (mod 6) のとき syracuse((4m-1)/3) = m -/
theorem syracuse_root_mod6_eq1 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
    syracuse ((4 * m - 1) / 3) = m := by
  -- r := (4m-1)/3 と置く
  set r := (4 * m - 1) / 3 with hr_def
  -- Syracuse の定義を展開: syracuse r = (3r+1) / 2^v2(3r+1)
  show (3 * r + 1) / 2 ^ v2 (3 * r + 1) = m
  -- 核心: 3r + 1 = 4m
  have hkey : 3 * r + 1 = 4 * m := key_eq_mod6_eq1 m hm h
  rw [hkey]
  -- v2(4m) = 2 (m は奇数なので)
  have hodd : m % 2 = 1 := by omega  -- m % 6 = 1 implies odd
  have hv2 : v2 (4 * m) = 2 := v2_four_mul_odd m hm hodd
  rw [hv2]
  -- 4m / 2^2 = 4m / 4 = m
  norm_num
  -- or: simp [Nat.mul_div_cancel_left m (by norm_num : (0:ℕ) < 4)]

/-- ★ m ≡ 5 (mod 6) のとき syracuse((2m-1)/3) = m -/
theorem syracuse_root_mod6_eq5 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 5) :
    syracuse ((2 * m - 1) / 3) = m := by
  set r := (2 * m - 1) / 3 with hr_def
  show (3 * r + 1) / 2 ^ v2 (3 * r + 1) = m
  -- 核心: 3r + 1 = 2m
  have hkey : 3 * r + 1 = 2 * m := key_eq_mod6_eq5 m hm h
  rw [hkey]
  -- v2(2m) = 1 (m は奇数なので)
  have hodd : m % 2 = 1 := by omega  -- m % 6 = 5 implies odd
  have hv2 : v2 (2 * m) = 1 := v2_two_mul_odd m hm hodd
  rw [hv2]
  -- 2m / 2^1 = 2m / 2 = m
  simp [Nat.mul_div_cancel_left m (by norm_num : (0:ℕ) < 2)]

/-! ## 系: 全射性 (surjectivity) -/

/-- Syracuse 関数は奇数で 3 の倍数でない m への全射 -/
theorem syracuse_surjective_on_odd_non_mul3 (m : ℕ) (hm : m ≥ 1)
    (hodd : m % 2 = 1) (hnot3 : m % 3 ≠ 0) :
    ∃ r : ℕ, r ≥ 1 ∧ r % 2 = 1 ∧ syracuse r = m := by
  -- m は奇数で 3 の倍数でないので m % 6 = 1 or m % 6 = 5
  have hmod6 : m % 6 = 1 ∨ m % 6 = 5 := by omega
  rcases hmod6 with h1 | h5
  · -- Case m ≡ 1 (mod 6)
    refine ⟨(4 * m - 1) / 3, ?_, ?_, ?_⟩
    · omega  -- (4m-1)/3 >= 1
    · exact root_odd_mod6_eq1 m h1
    · exact syracuse_root_mod6_eq1 m hm h1
  · -- Case m ≡ 5 (mod 6)
    refine ⟨(2 * m - 1) / 3, ?_, ?_, ?_⟩
    · omega  -- (2m-1)/3 >= 1 when m >= 5
    · exact root_odd_mod6_eq5 m h5
    · exact syracuse_root_mod6_eq5 m hm h5

/-! ## root と syracuse_four_mul_add_one の接続 -/

/-- 逆像の連鎖: root, 4*root+1, 4*(4*root+1)+1, ... が全て同じ m の逆像 -/
-- これは syracuse_four_mul_add_one の反復適用から直ちに従う
"""

print(lean_design)

# 追加の omega 実現可能性チェック
print("\n" + "=" * 70)
print("omega タクティクで解けるかのシミュレーション")
print("=" * 70)

print("\n1. (4*m - 1) % 3 = 0 when m % 6 = 1:")
for m in range(1, 100, 6):
    assert (4 * m - 1) % 3 == 0, f"Failed at m={m}"
print("   All passed (m=1,7,13,...,97)")

print("\n2. ((4*m - 1) / 3) % 2 = 1 when m % 6 = 1:")
for m in range(1, 100, 6):
    assert ((4 * m - 1) // 3) % 2 == 1, f"Failed at m={m}"
print("   All passed")

print("\n3. (2*m - 1) % 3 = 0 when m % 6 = 5:")
for m in range(5, 100, 6):
    assert (2 * m - 1) % 3 == 0, f"Failed at m={m}"
print("   All passed")

print("\n4. ((2*m - 1) / 3) % 2 = 1 when m % 6 = 5:")
for m in range(5, 100, 6):
    assert ((2 * m - 1) // 3) % 2 == 1, f"Failed at m={m}"
print("   All passed")

print("\nNote: omega in Lean 4 handles linear arithmetic over Nat/Int.")
print("The key equations 3*((4m-1)/3)+1 = 4m and 3*((2m-1)/3)+1 = 2m")
print("require showing divisibility first, then omega can finish.")
print("In Lean 4, omega can handle modular arithmetic with Nat.div,")
print("but may need help with non-linear (m * k) terms.")
print("Strategy: use 'have h_div : 3 ∣ (4*m-1) := by omega' first.")

# Dependence analysis
print("\n" + "=" * 70)
print("依存関係分析")
print("=" * 70)

deps = """
必要な既存定理:
  1. v2_two_mul (Defs.lean, line 121)
  2. v2_odd (Defs.lean, line 109)
  3. syracuse の定義 (Defs.lean, line 89-92)
  4. syracuse_four_mul_add_one (Structure.lean, line 618) -- 系で使用

新しい補題の依存関係:
  key_eq_mod6_eq1 ← omega (m % 6 = 1 条件のみ)
  key_eq_mod6_eq5 ← omega (m % 6 = 5 条件のみ)
  root_odd_mod6_eq1 ← omega
  root_odd_mod6_eq5 ← omega
  v2_four_mul_odd ← v2_two_mul, v2_odd
  v2_two_mul_odd ← v2_two_mul, v2_odd
  syracuse_root_mod6_eq1 ← key_eq_mod6_eq1, v2_four_mul_odd
  syracuse_root_mod6_eq5 ← key_eq_mod6_eq5, v2_two_mul_odd
  syracuse_surjective_on_odd_non_mul3 ← 上記全て

推奨ファイル配置:
  Unsolved/Collatz/Mod.lean の末尾に追加
  (Structure.lean をインポート済み、v2 補題が利用可能)
"""
print(deps)

print("\n" + "=" * 70)
print("omega が Nat.div を扱えるかの確認ポイント")
print("=" * 70)
print("""
Lean 4 の omega は自然数の除算 (Nat.div) を直接は扱えない。
しかし、以下のアプローチで回避可能:

方法1: Nat.div_add_mod を使って分解
  have h1 : 4 * m - 1 = 3 * ((4 * m - 1) / 3) + (4 * m - 1) % 3 :=
    (Nat.div_add_mod (4 * m - 1) 3).symm
  have h2 : (4 * m - 1) % 3 = 0 := by omega
  omega

方法2: Nat.div_mul_cancel を使用
  have h_dvd : 3 ∣ (4 * m - 1) := by omega  -- omega が modular arithmetic を解く
  have := Nat.div_mul_cancel h_dvd
  -- 結果: (4 * m - 1) / 3 * 3 = 4 * m - 1
  omega

方法3: 直接的なパラメータ化
  obtain ⟨k, hk⟩ : ∃ k, m = 6 * k + 1 := by omega
  subst hk
  -- これで (4 * (6*k+1) - 1) / 3 = (24*k + 3) / 3 = 8*k + 1
  -- を norm_num/simp で計算可能
""")
