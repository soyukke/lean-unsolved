"""
奇数*奇数=奇数 のLean証明の詳細設計

== 問題 ==
ha : a % 2 = 1
hb_odd : b % 2 != 0   (つまり b % 2 = 1)
Goal: (a * b) % 2 != 0

== 解決策A: Nat.mul_mod + simp ==
rw [Nat.mul_mod]
-- Goal: ((a % 2) * (b % 2)) % 2 != 0
simp [ha]
-- simplify a%2 to 1: (1 * (b%2)) % 2 != 0
-- simplify 1*x to x: (b%2) % 2 != 0
-- b%2 is 0 or 1, and hb_odd says it's not 0
omega

== 解決策B: rw で手動変換 ==
have h1 : (a * b) % 2 = ((a % 2) * (b % 2)) % 2 := Nat.mul_mod a b 2
rw [h1, ha]
-- Goal: (1 * (b % 2)) % 2 != 0
simp
-- Goal: b % 2 != 0
exact hb_odd

== 解決策C: Odd 型を使う ==
have hodd_a : Odd a := by omega  -- from ha : a % 2 = 1
have hodd_b : Odd b := by omega  -- from hb_odd
have hodd_ab := hodd_a.mul hodd_b  -- Odd (a*b)
omega  -- Odd (a*b) => (a*b) % 2 = 1 => != 0

== 最も安全な選択 ==
解決策Bが最も安全。rw + simp + exact の組み合わせで予測可能。
解決策Cも良いが、Odd の unfold がどう動くか不確定。
"""

print("=== 奇数*奇数=奇数: 3つの証明戦略 ===")
print()
print("Strategy A: Nat.mul_mod + simp + omega")
print('  have hab_odd : (a * b) % 2 ≠ 0 := by')
print('    rw [Nat.mul_mod]; simp [ha]; omega')
print()
print("Strategy B: 手動リライト")
print('  have hab_odd : (a * b) % 2 ≠ 0 := by')
print('    have h1 : (a * b) % 2 = ((a % 2) * (b % 2)) % 2 := Nat.mul_mod a b 2')
print('    rw [h1, ha]')
print('    simp; exact hb_odd')
print()
print("Strategy C: Odd 型")
print('  have hab_odd : (a * b) % 2 ≠ 0 := by')
print('    have : Odd a := by omega')
print('    have : Odd b := by omega')
print('    have : Odd (a * b) := Odd.mul this this')
print('    omega')
print()

# v2_odd_mul のb=0ケースの詳細
print("=== v2_odd_mul の b=0 ケース ===")
print("subst hb0 で b=0 を代入後:")
print("  Goal: v2 (a * 0) = v2 0")
print("  a * 0 = 0 by ring/simp")
print("  v2 0 = 0 by v2_zero")
print("  simp で十分のはず")
print()

# v2_even の逆方向リライトの詳細
print("=== v2_even 逆方向リライトの詳細 ===")
print("Goal at end of even case of v2_odd_mul:")
print("  1 + v2 (b / 2) = v2 b")
print()
print("v2_even b hb0 hb_even : v2 b = 1 + v2 (b / 2)")
print("← v2_even b hb0 hb_even でゴールの v2 b を 1 + v2 (b/2) に置換")
print("しかしゴールの左辺は 1 + v2(b/2)、右辺は v2 b")
print("rw [← v2_even b hb0 hb_even] はゴールの v2 b を 1+v2(b/2) に書き換える")
print("=> ゴール: 1 + v2(b/2) = 1 + v2(b/2)")
print("=> rfl で完了")
print()
print("あるいは:")
print("  symm")
print("  exact v2_even b hb0 hb_even")

# 代替: v2_even を先に使ってからリライト
print()
print("=== 代替: omega で完了 ===")
print("Goal: 1 + v2 (b / 2) = v2 b")
print("have hv2b := v2_even b hb0 hb_even")
print("-- hv2b : v2 b = 1 + v2 (b/2)")
print("omega")
print("-- omega can solve: 1 + v2(b/2) = v2 b given v2 b = 1 + v2(b/2)")

# positivity の代替
print()
print("=== positivity の代替 ===")
print("positivity が使えない場合:")
print("  have : a * (b / 2) ≠ 0 := by")
print("    have : a > 0 := by omega")
print("    have : b / 2 > 0 := by omega")
print("    exact Nat.ne_of_gt (Nat.mul_pos ‹a > 0› ‹b / 2 > 0›)")
print()
print("あるいは単純に:")
print("  have : a * (b / 2) > 0 := Nat.mul_pos (by omega) (by omega)")
print("  omega  -- to get ≠ 0")
