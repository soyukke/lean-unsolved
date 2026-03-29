"""
v2(a*b) = v2(a) + v2(b) の数値検証と証明戦略の分析

証明戦略:
1. v2_odd_mul: a%2=1 -> v2(a*b) = v2(b)   (奇数*任意)
2. v2_mul: a>0 -> b>0 -> v2(a*b) = v2(a) + v2(b)  (一般乗法性)

帰納法の設計:
- strongRecOn (a*b) での帰納法
- a偶数: a=2*a', v2(2*a'*b) = 1+v2(a'*b), IH適用で 1+v2(a')+v2(b) = (1+v2(a'))+v2(b) = v2(a)+v2(b)
- a奇数: v2(a)=0, v2(a*b)=v2(b) (v2_odd_mulから) = 0+v2(b) = v2(a)+v2(b)
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    if n % 2 != 0:
        return 0
    return 1 + v2(n // 2)

# v2_odd_mul の検証: a奇数 => v2(a*b) = v2(b)
print("=== v2_odd_mul の検証 ===")
print("a (odd) | b | v2(a*b) | v2(b) | match?")
print("-" * 50)
all_ok = True
for a in range(1, 50, 2):  # 奇数のみ
    for b in range(0, 50):
        result = v2(a * b)
        expected = v2(b)
        if result != expected:
            print(f"  FAIL: a={a}, b={b}, v2({a*b})={result}, v2({b})={expected}")
            all_ok = False
if all_ok:
    print("  ALL PASSED (a in 1..49 odd, b in 0..49)")

# v2_mul の検証: a>0, b>0 => v2(a*b) = v2(a) + v2(b)
print("\n=== v2_mul の検証 ===")
print("a | b | v2(a*b) | v2(a)+v2(b) | match?")
print("-" * 50)
all_ok = True
for a in range(1, 100):
    for b in range(1, 100):
        result = v2(a * b)
        expected = v2(a) + v2(b)
        if result != expected:
            print(f"  FAIL: a={a}, b={b}, v2({a*b})={result}, v2({a})+v2({b})={expected}")
            all_ok = False
if all_ok:
    print("  ALL PASSED (a in 1..99, b in 1..99)")

# v2(0) のケース確認
print("\n=== v2(0) のケース ===")
print(f"  v2(0) = {v2(0)}")
print(f"  v2(0*5) = v2(0) = {v2(0*5)}")
print(f"  v2(0) + v2(5) = {v2(0) + v2(5)} -- v2_mulは a>0, b>0 を仮定するので 0 は除外")
print(f"  注: v2(0*b) = v2(0) = 0 だが v2(0)+v2(b) = 0+v2(b) = v2(b)")
print(f"       よって b>0 で b が偶数のとき v2(0*b)=0 != v2(b)>0")
print(f"       例: v2(0*4) = {v2(0*4)} だが v2(0)+v2(4) = {v2(0)+v2(4)}")

# v2_odd_mul で b=0 の場合
print("\n=== v2_odd_mul で b=0 の場合 ===")
for a in [1, 3, 5, 7]:
    print(f"  a={a}, b=0: v2({a}*0) = v2(0) = {v2(a*0)}, v2(0) = {v2(0)}")

# 帰納法の構造分析: strongRecOn a での場合分け
print("\n=== 帰納法の構造分析 ===")
print("Approach A: strongRecOn a (aに関する強い帰納法)")
print("  Case 1: a%2 = 1 (奇数)")
print("    -> v2(a) = 0")
print("    -> v2(a*b) = v2(b) (by v2_odd_mul)")
print("    -> 0 + v2(b) = v2(b) ✓")
print()
print("  Case 2: a%2 = 0 (偶数), a>0")
print("    -> a = 2*(a/2), a/2 > 0 (since a>0 and a even)")
print("    -> a/2 < a (since a>0)")
print("    -> v2(a*b) = v2(2*(a/2)*b) = v2(2*((a/2)*b))")
print("    -> = 1 + v2((a/2)*b)   (by v2_two_mul, since (a/2)*b > 0)")
print("    -> = 1 + (v2(a/2) + v2(b))  (by IH on a/2 < a)")
print("    -> = (1 + v2(a/2)) + v2(b)")
print("    -> = v2(a) + v2(b)   (by v2_even)")
print()

# v2_odd_mul の証明戦略
print("=== v2_odd_mul の証明戦略 ===")
print("Approach: strongRecOn b")
print("  Case b=0: v2(a*0) = v2(0) = 0 = v2(0) ✓")
print("  Case b>0, b%2=1 (奇数):")
print("    a*b は奇数*奇数 = 奇数")
print("    v2(a*b) = 0 = v2(b) ✓")
print("  Case b>0, b%2=0 (偶数):")
print("    b = 2*(b/2), b/2 < b")
print("    a*b = a*(2*(b/2)) = 2*(a*(b/2))")
print("    v2(a*b) = v2(2*(a*(b/2))) = 1 + v2(a*(b/2))")
print("    = 1 + v2(b/2)  (IH)")
print("    = v2(b)  (by v2_even)")

# Lean 4 での直接的な形式化構造
print("\n=== Lean 4 証明スケッチ ===")
lean_sketch_odd_mul = """
-- v2_odd_mul: 奇数 * 任意 の v2
theorem v2_odd_mul (a b : Nat) (ha : a % 2 = 1) : v2 (a * b) = v2 b := by
  induction b using Nat.strongRecOn with
  | ind b ih =>
    by_cases hb0 : b = 0
    . simp [hb0]
    . by_cases hb_odd : b % 2 != 0
      . -- a*b is odd (odd*odd)
        have hab_odd : (a * b) % 2 != 0 := by omega  -- 要検証
        rw [v2_odd _ hab_odd, v2_odd _ hb_odd]
      . -- b even: b = 2*(b/2)
        push_neg at hb_odd
        have hb_even : b % 2 = 0 := by omega
        have hb2_lt : b / 2 < b := by omega
        -- a*b = 2*(a*(b/2)) ? No! a*b = a*(2*(b/2))
        -- key: a*(2*k) = 2*(a*k) by ring
        have h_eq : a * b = 2 * (a * (b / 2)) := by omega -- 要検証: b = 2*(b/2)
        rw [v2_even (a * b) (by omega) (by ...)]
        -- Need: (a*b) / 2 = a * (b/2)
        -- Then apply IH
        sorry
"""

lean_sketch_mul = """
-- v2_mul: 一般乗法性
theorem v2_mul (a b : Nat) (ha : a > 0) (hb : b > 0) : v2 (a * b) = v2 a + v2 b := by
  induction a using Nat.strongRecOn with
  | ind a ih =>
    by_cases ha_odd : a % 2 != 0
    . -- a is odd: v2(a) = 0
      rw [v2_odd a ha_odd, v2_odd_mul a b (by omega)]
      simp
    . -- a is even: a = 2*(a/2), a/2 < a
      push_neg at ha_odd
      have ha_even : a % 2 = 0 := by omega
      have ha2_pos : a / 2 > 0 := by omega
      have ha2_lt : a / 2 < a := by omega
      -- v2(a) = 1 + v2(a/2)
      rw [v2_even a (by omega) ha_even]
      -- a*b = 2*(a/2)*b = 2*((a/2)*b)
      have h_eq : a * b = 2 * ((a / 2) * b) := by omega -- needs: a = 2*(a/2)
      -- v2(a*b) = v2(2*((a/2)*b)) = 1 + v2((a/2)*b)
      rw [show a * b = 2 * ((a/2) * b) from by omega]
      rw [v2_two_mul ((a/2) * b) (by omega)]
      -- 1 + v2((a/2)*b) = 1 + (v2(a/2) + v2(b))  by IH
      rw [ih (a/2) ha2_lt ha2_pos hb]
      -- 1 + (v2(a/2) + v2(b)) = (1 + v2(a/2)) + v2(b)
      omega
"""

print(lean_sketch_odd_mul)
print(lean_sketch_mul)

# omega で a*b = 2 * ((a/2) * b) が解けるか検証
print("\n=== omega の限界分析 ===")
print("問題: a % 2 = 0 のとき a * b = 2 * ((a/2) * b) を omega で解けるか?")
print("omega は線形算術に限定されるため、a*b のような非線形項は直接扱えない")
print("しかし Lean の omega は一部のケースで a = 2 * (a/2) を扱える")
print()
print("代替戦略:")
print("  1. have h_div : a = 2 * (a / 2) := by omega  (これは omega で解ける)")
print("  2. calc a * b = (2 * (a / 2)) * b := by rw [h_div]")
print("             _ = 2 * ((a / 2) * b) := by ring")
print("  3. これで a * b = 2 * ((a/2) * b) が得られる")

# v2_odd_mul でも同様の問題
print("\n=== v2_odd_mul での乗法の書き換え ===")
print("b%2=0 のとき a*b = 2*(a*(b/2)) を示す必要がある")
print("  have hb_div : b = 2 * (b / 2) := by omega")
print("  calc a * b = a * (2 * (b / 2)) := by rw [hb_div]")
print("           _ = 2 * (a * (b / 2)) := by ring")

# 奇数*奇数 = 奇数 の omega 解決可能性
print("\n=== 奇数*奇数 = 奇数 ===")
print("a%2=1, b%2=1 => (a*b)%2 = 1")
print("これは omega では解けない (非線形)")
print("Mathlibの Nat.odd_mul を使うか、以下の補題を自前で証明:")
print("  have : (a * b) % 2 = (a % 2) * (b % 2) % 2 := by ...")
print("  または Odd.mul のような Mathlib 補題を使用")

# 偶数*任意の書き換え
print("\n=== (a*b)/2 = (a/2)*b の証明 (a even) ===")
print("a%2=0 のとき: (a*b)/2 = (a/2)*b")
print("  have : a = 2 * (a/2) := by omega")
print("  calc (a*b)/2 = (2*(a/2)*b)/2 := by rw [this]")
print("             _ = (2*((a/2)*b))/2 := by ring_nf")
print("             _ = (a/2)*b := Nat.mul_div_cancel_left _ (by omega)")

# (a*b)%2 の非線形性に対処するMathlib補題の候補
print("\n=== Mathlib 補題候補 ===")
print("1. Nat.mul_mod : (a * b) % n = ((a % n) * (b % n)) % n")
print("   -> (a*b)%2 = ((a%2)*(b%2))%2")
print("2. Odd.mul : Odd a -> Odd b -> Odd (a*b)")
print("3. Nat.even_mul_of_even_left / right")
print("4. Even.mul_right / Even.mul_left")
print()

# v2_even の条件: (a*b)/2 のリライトの詳細
print("=== v2_even 適用時の詳細 ===")
print("v2_even (a*b) (ne_zero) (even_cond) gives:")
print("  v2(a*b) = 1 + v2((a*b)/2)")
print()
print("For v2_odd_mul (b even case):")
print("  Need: v2((a*b)/2) = v2(a*(b/2))")
print("  i.e., (a*b)/2 = a*(b/2)")
print("  Proof: b = 2*(b/2), so a*b = a*(2*(b/2)) = 2*(a*(b/2))")
print("         Then (a*b)/2 = (2*(a*(b/2)))/2 = a*(b/2)")
print()
print("For v2_mul (a even case):")
print("  Need: v2((a*b)/2) = v2((a/2)*b)")
print("  i.e., (a*b)/2 = (a/2)*b")
print("  Proof: a = 2*(a/2), so a*b = 2*(a/2)*b = 2*((a/2)*b)")
print("         Then (a*b)/2 = (2*((a/2)*b))/2 = (a/2)*b")

# まとめ
print("\n" + "="*60)
print("=== まとめ: Lean 4 形式化の具体設計 ===")
print("="*60)
print()
print("Step 1: v2_odd_mul (奇数*任意)")
print("  theorem v2_odd_mul (a b : Nat) (ha : a % 2 = 1) :")
print("      v2 (a * b) = v2 b")
print("  証明: b に対する strongRecOn")
print("    - b=0: simp")
print("    - b odd: (a*b) odd, 両方 v2=0")
print("    - b even: v2(a*b) = 1 + v2(a*(b/2)) = 1 + v2(b/2) = v2(b)")
print()
print("Step 2: v2_mul (一般乗法性)")
print("  theorem v2_mul (a b : Nat) (ha : a > 0) (hb : b > 0) :")
print("      v2 (a * b) = v2 a + v2 b")
print("  証明: a に対する strongRecOn")
print("    - a odd: v2(a)=0, v2(a*b) = v2(b) = 0 + v2(b)")
print("    - a even: v2(a*b) = 1 + v2((a/2)*b) = 1 + v2(a/2) + v2(b)")
print("              = (1+v2(a/2)) + v2(b) = v2(a) + v2(b)")
print()
print("Key Lean tactics needed:")
print("  - Nat.strongRecOn for induction")
print("  - omega for linear arithmetic (a = 2*(a/2), b = 2*(b/2))")
print("  - ring / ring_nf for commutativity/associativity")
print("  - Nat.mul_div_cancel_left for (2*k)/2 = k")
print("  - Nat.mul_mod or Odd.mul for odd*odd=odd")
print("  - v2_odd, v2_even, v2_two_mul from existing codebase")
