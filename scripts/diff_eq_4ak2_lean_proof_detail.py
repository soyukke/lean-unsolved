"""
探索193 Part 2: nat_div3_aux 補題の詳細検証と
Lean 4 形式化の最終的な具体コード案
"""

# =============================================
# Part A: nat_div3_aux の omega 適用可能性検証
# =============================================
print("=" * 60)
print("Part A: nat_div3_aux の代入後の形")
print("=" * 60)

# obtain ⟨c, hc⟩ := h2 で a - 2 = 3 * c を得る
# a >= 2 から a = 3*c + 2
# subst 後:
# Goal: (4 * (3*c + 2) - 2) / 3 = 4 * ((3*c + 2 - 2) / 3) + 2
# = (12*c + 8 - 2) / 3 = 4 * (3*c / 3) + 2
# = (12*c + 6) / 3 = 4*c + 2

# Lean の Nat.div: (12*c + 6) / 3 は?
# 12*c + 6 = 3*(4*c + 2) なので (12*c+6)/3 = 4*c+2

# omega は Nat.div を直接扱えないので、simp で展開する必要がある
# しかし、次の補題があれば:
#   Nat.mul_div_cancel_left : a * b / a = b (a > 0)
# 3*(4*c+2)/3 = 4*c+2

# 問題: ゴールが (12*c+6)/3 の形で、3*(4*c+2)/3 の形ではない
# ring_nf で 12*c+6 → 3*(4*c+2) に変形できるか?

# 実は、Lean での計算:
# 4*(3*c+2) - 2 の計算
# Nat では underflow の心配: 4*(3*c+2) >= 8 >= 2 なので大丈夫
# (3*c+2-2) = 3*c なので 3*c/3 = c (Nat.mul_div_cancel_left)

print("Goal after subst:")
print("  (4 * (3 * c + 2) - 2) / 3 = 4 * ((3 * c + 2 - 2) / 3) + 2")
print()
print("Simplification:")
print("  LHS: (12*c + 8 - 2) / 3 = (12*c + 6) / 3")
print("  RHS: 4 * (3*c / 3) + 2 = 4 * c + 2")
print()
print("Key: (12*c + 6) / 3 = 4*c + 2")
print("  Because: 12*c + 6 = 3 * (4*c + 2)")
print()

for c in range(20):
    lhs = (12*c + 6) // 3
    rhs = 4*c + 2
    assert lhs == rhs, f"Failed for c={c}"
print("Verified for c=0..19")

# =============================================
# Part B: Lean 証明の選択肢
# =============================================
print("\n" + "=" * 60)
print("Part B: Lean 証明の複数選択肢")
print("=" * 60)

options = """
選択肢1: obtain + omega (omega が Nat.div を扱えるか?)
  obtain ⟨c, hc⟩ := h2
  have ha : a = 3 * c + 2 := by omega
  subst ha
  -- Goal: (4 * (3*c+2) - 2) / 3 = 4 * ((3*c+2-2)/3) + 2
  simp  -- 3*c+2-2 → 3*c, then 3*c/3 → c via Nat.mul_div_cancel_left
  -- Remaining: (12*c+6)/3 = 4*c+2
  -- omega できないかも...

選択肢2: show + Nat.mul_div_cancel_left
  obtain ⟨c, hc⟩ := h2
  have ha : a = 3 * c + 2 := by omega
  subst ha
  -- RHS 簡約
  have h_rhs : (3*c+2-2) / 3 = c := by
    simp [Nat.mul_div_cancel_left c (by omega : 0 < 3)]
    -- or: show 3*c/3 = c; exact Nat.mul_div_cancel_left c (by omega)
  rw [h_rhs]
  -- Goal: (12*c+6)/3 = 4*c+2
  have h_lhs : 12*c + 6 = 3 * (4*c + 2) := by ring
  rw [show 4*(3*c+2)-2 = 12*c+6 from by ring]
  rw [h_lhs]
  exact Nat.mul_div_cancel_left (4*c+2) (by omega)

選択肢3: conv + ring_nf で 3*(...)  の形に持ち込む
  (最もrobust)

選択肢4: Int に移して証明
  have h_int : (↑(4*a-2) : Int) / 3 = 4 * ((↑(a-2) : Int) / 3) + 2
  ... (Int.div は omega で扱える可能性が高い)
  Int.toNat_div ... で Nat に戻す

推奨: 選択肢2 (最も明示的で確実)
"""
print(options)

# =============================================
# Part C: evenImageSizeAux_ge_two の証明
# =============================================
print("=" * 60)
print("Part C: evenImageSizeAux_ge_two の証明")
print("=" * 60)

# 14 * 4^j >= 14 >= 2 は自明
print("14 * 4^j >= 14 >= 2 for all j >= 0")
print("Lean proof: by simp [evenImageSizeAux]; positivity (or omega)")
print()
for j in range(10):
    val = 14 * 4**j
    print(f"  j={j}: evenImageSizeAux = {val} >= 2")

# =============================================
# Part D: evenImageSizeAux_sub_two_div3 の詳細
# =============================================
print("\n" + "=" * 60)
print("Part D: evenImageSizeAux_sub_two_div3 の帰納法")
print("=" * 60)

# base: j=0: 14*1 - 2 = 12, 3|12
# step: 14*4^{j+1} - 2 = 56*4^j - 2
#      = 4*(14*4^j) - 2
#      = 4*(14*4^j - 2) + 4*2 - 2
#      = 4*(14*4^j - 2) + 6
# IH: 3 | (14*4^j - 2)
# 3|6 なので 3 | (4*(14*4^j-2) + 6)

# Lean の Nat 引き算の問題:
# 14*4^{j+1} - 2 = 4*(14*4^j) - 2
# ここで 14*4^{j+1} = 14*4*4^j = 56*4^j
# 56*4^j - 2 = 4*(14*4^j - 2) + 6
# 自然数では: 56*4^j >= 2 (OK), 14*4^j >= 2 (OK)

# Lean での dvd の扱い:
# 3 ∣ (56*4^j - 2) を直接示す
# 帰納法 + obtain ⟨d, hd⟩ := ih で 14*4^j - 2 = 3*d
# 56*4^j - 2 = 4*(14*4^j) - 2 = 4*(3*d + 2) - 2 = 12*d + 6 = 3*(4*d + 2)

print("Lean proof sketch:")
print("""
theorem evenImageSizeAux_sub_two_div3 (j : Nat) :
    3 ∣ (14 * 4 ^ j - 2) := by
  induction j with
  | zero => norm_num  -- 14 - 2 = 12, 3 | 12
  | succ n ih =>
    obtain ⟨d, hd⟩ := ih
    -- hd : 14 * 4^n - 2 = 3 * d
    -- Goal: 3 ∣ (14 * 4^(n+1) - 2)
    -- 14*4^{n+1} = 56*4^n = 4*(14*4^n)
    -- 14*4^{n+1} - 2 = 4*(14*4^n) - 2
    --                = 4*(3*d+2) - 2  [using hd: 14*4^n = 3*d+2]
    --                = 12*d + 6 = 3*(4*d+2)
    have h14 : 14 * 4^n >= 2 := by positivity
    have h_eq : 14 * 4^n = 3 * d + 2 := by omega  -- from hd
    have h_step : 14 * 4^(n+1) - 2 = 3*(4*d+2) := by
      have : 14 * 4^(n+1) = 4 * (14 * 4^n) := by ring
      rw [this, h_eq]
      ring  -- or omega
    exact ⟨4*d+2, h_step⟩
""")

# 検証
for j in range(15):
    val = 14 * 4**j - 2
    assert val % 3 == 0, f"Failed for j={j}"
    d = val // 3
    # Check step
    if j > 0:
        prev_d = (14 * 4**(j-1) - 2) // 3
        step_val = 4*prev_d + 2
        assert d == step_val, f"Step failed for j={j}"
        print(f"  j={j}: 14*4^j - 2 = {val} = 3*{d}, d = 4*{prev_d}+2 = {step_val} OK")
    else:
        print(f"  j={j}: 14*4^j - 2 = {val} = 3*{d} (base)")

# =============================================
# Part E: 完全な Lean 4 コード（最終版）
# =============================================
print("\n" + "=" * 60)
print("Part E: 完全な Lean 4 コード（最終版）")
print("=" * 60)

lean_code = """
/-!
# mod 2^k での Syracuse 写像の像サイズの差分方程式

## 閉公式
- k奇数 (k = 2j+3, j >= 0): |Im(T mod 2^k)| = 3 * 4^j
- k偶数 (k = 2j+4, j >= 0): |Im(T mod 2^k)| = (14 * 4^j - 2) / 3

## 差分方程式
- k奇数: a(k+2) = 4 * a(k)
- k偶数: a(k+2) = 4 * a(k) + 2

## 形式化戦略
除算を含む k偶数の公式は、乗法形式 3*a(k)+2 = 14*4^j で扱い、
Nat.div の操作を最小限に抑える。
-/

import Mathlib

/-! ## 1. k奇数の像サイズ -/

/-- k奇数 (k = 2j+3) のときの像サイズ -/
def oddImageSize (j : Nat) : Nat := 3 * 4 ^ j

/-- 初期値: a(3) = 3 -/
theorem oddImageSize_base : oddImageSize 0 = 3 := by
  simp [oddImageSize]

/-- 差分方程式: a(2(j+1)+3) = 4 * a(2j+3)
    つまり a(k+2) = 4 * a(k) (k奇数) -/
theorem oddImageSize_step (j : Nat) :
    oddImageSize (j + 1) = 4 * oddImageSize j := by
  simp [oddImageSize, pow_succ]
  ring

/-! ## 2. k偶数の乗法形式 -/

/-- k偶数 (k = 2j+4) のときの乗法形式: 3 * a(k) + 2 -/
def evenImageSizeAux (j : Nat) : Nat := 14 * 4 ^ j

/-- 乗法形式の初期値: 3*a(4)+2 = 14 -/
theorem evenImageSizeAux_base : evenImageSizeAux 0 = 14 := by
  simp [evenImageSizeAux]

/-- 乗法形式の差分方程式: b(j+1) = 4 * b(j) -/
theorem evenImageSizeAux_step (j : Nat) :
    evenImageSizeAux (j + 1) = 4 * evenImageSizeAux j := by
  simp [evenImageSizeAux, pow_succ]
  ring

/-- 乗法形式は 2 以上 -/
theorem evenImageSizeAux_ge_two (j : Nat) : evenImageSizeAux j >= 2 := by
  simp [evenImageSizeAux]
  have : 4 ^ j >= 1 := Nat.one_le_pow j 4 (by omega)
  omega

/-- 乗法形式から 2 を引いたものは 3 で割り切れる -/
theorem evenImageSizeAux_sub_two_dvd3 (j : Nat) :
    3 ∣ (evenImageSizeAux j - 2) := by
  induction j with
  | zero => simp [evenImageSizeAux]  -- 14 - 2 = 12
  | succ n ih =>
    obtain ⟨d, hd⟩ := ih
    have hge : 14 * 4 ^ n >= 2 := evenImageSizeAux_ge_two n
    have heq : 14 * 4 ^ n = 3 * d + 2 := by omega
    refine ⟨4 * d + 2, ?_⟩
    -- 14*4^{n+1} - 2 = 4*(14*4^n) - 2 = 4*(3*d+2) - 2 = 12*d+6 = 3*(4*d+2)
    have : 14 * 4 ^ (n + 1) = 4 * (14 * 4 ^ n) := by ring
    omega

/-! ## 3. k偶数の実際の像サイズ -/

/-- k偶数 (k = 2j+4) のときの像サイズ -/
def evenImageSize (j : Nat) : Nat := (evenImageSizeAux j - 2) / 3

/-- 初期値: a(4) = 4 -/
theorem evenImageSize_base : evenImageSize 0 = 4 := by
  simp [evenImageSize, evenImageSizeAux]

/-- 核心補題: 3 | (a-2) かつ a >= 2 のとき (4a-2)/3 = 4*((a-2)/3) + 2 -/
lemma div3_step (a : Nat) (hge : a >= 2) (hdvd : 3 ∣ (a - 2)) :
    (4 * a - 2) / 3 = 4 * ((a - 2) / 3) + 2 := by
  obtain ⟨c, hc⟩ := hdvd
  have ha : a = 3 * c + 2 := by omega
  subst ha
  -- Goal: (4 * (3*c+2) - 2) / 3 = 4 * ((3*c+2-2)/3) + 2
  -- LHS: (12*c+6)/3, RHS: 4*(3*c/3)+2 = 4*c+2
  simp only [show 3 * c + 2 - 2 = 3 * c from by omega]
  rw [Nat.mul_div_cancel_left c (by omega : 0 < 3)]
  rw [show 4 * (3 * c + 2) - 2 = 3 * (4 * c + 2) from by ring]
  exact Nat.mul_div_cancel_left (4 * c + 2) (by omega : 0 < 3)

/-- 差分方程式: a(2(j+1)+4) = 4 * a(2j+4) + 2
    つまり a(k+2) = 4 * a(k) + 2 (k偶数) -/
theorem evenImageSize_step (j : Nat) :
    evenImageSize (j + 1) = 4 * evenImageSize j + 2 := by
  simp only [evenImageSize]
  -- Goal: (evenImageSizeAux(j+1) - 2)/3 = 4*((evenImageSizeAux(j)-2)/3) + 2
  rw [evenImageSizeAux_step]
  exact div3_step (evenImageSizeAux j)
    (evenImageSizeAux_ge_two j)
    (evenImageSizeAux_sub_two_dvd3 j)

/-! ## 4. 乗法形式と実際の像サイズの関係 -/

/-- 3 * evenImageSize j + 2 = evenImageSizeAux j -/
theorem evenImageSize_mul3_add2 (j : Nat) :
    3 * evenImageSize j + 2 = evenImageSizeAux j := by
  simp [evenImageSize]
  have hdvd := evenImageSizeAux_sub_two_dvd3 j
  have hge := evenImageSizeAux_ge_two j
  obtain ⟨c, hc⟩ := hdvd
  have : evenImageSizeAux j = 3 * c + 2 := by omega
  rw [this, show 3 * c + 2 - 2 = 3 * c from by omega,
      Nat.mul_div_cancel_left c (by omega : 0 < 3)]
  ring

/-! ## 5. 数値検証 -/

-- a(3) = 3
example : oddImageSize 0 = 3 := by decide
-- a(4) = 4
example : evenImageSize 0 = 4 := by decide
-- a(5) = 12
example : oddImageSize 1 = 12 := by decide
-- a(6) = 18
example : evenImageSize 1 = 18 := by decide
-- a(7) = 48
example : oddImageSize 2 = 48 := by decide
-- a(8) = 74
example : evenImageSize 2 = 74 := by decide
-- a(9) = 192
example : oddImageSize 3 = 192 := by decide
-- a(10) = 298
example : evenImageSize 3 = 298 := by decide

/-! ## 6. 統合定義と統合定理 -/

/-- 統合像サイズ関数: k >= 3 のときの像サイズ -/
def collatzImageSize : Nat → Nat
  | 0 => 0  -- placeholder
  | 1 => 0  -- placeholder
  | 2 => 0  -- placeholder
  | k + 3 => if k % 2 = 0 then oddImageSize (k / 2)
              else evenImageSize ((k - 1) / 2)

/-- 統合差分方程式 -/
theorem collatzImageSize_step (k : Nat) (hk : k >= 3) :
    collatzImageSize (k + 2) =
    if k % 2 = 1 then 4 * collatzImageSize k
    else 4 * collatzImageSize k + 2 := by
  sorry  -- 場合分け + oddImageSize_step / evenImageSize_step

-- 注: 統合定理は偶奇分離版から自動的に従う。
-- 実用上は偶奇分離版（oddImageSize_step, evenImageSize_step）で十分。
"""

print(lean_code)

# =============================================
# Part F: 関連する既存 Lean ファイルとの整合性
# =============================================
print("\n" + "=" * 60)
print("Part F: ファイル配置と依存関係")
print("=" * 60)

placement = """
推奨ファイル: Unsolved/Collatz/ImageSize.lean (新規)

依存:
  import Mathlib  (ring, omega, pow_succ, Nat.mul_div_cancel_left)

既存ファイルとの関係:
  - Defs.lean: syracuse, v2 の定義 (直接使わない - 純粋に数列の代数)
  - Mod.lean: v2 の mod 8 分類 (将来的に像サイズとの接続に使用)
  - Formula.lean: 一般乗法公式 (将来的にCk -> 像サイズの導出に使用)

形式化の独立性:
  この形式化は数列の代数的性質のみを扱い、
  Syracuse 関数の定義に依存しない。
  閉公式と漸化式の等価性は純粋な自然数算術。

  将来的に「Syracuse 像サイズ = この数列」を証明する際に
  Defs.lean, Mod.lean と接続する。
"""
print(placement)

# =============================================
# Part G: 行数見積もり
# =============================================
print("\n" + "=" * 60)
print("Part G: 行数見積もり")
print("=" * 60)

estimates = [
    ("ヘッダ・コメント", 15),
    ("oddImageSize 定義", 1),
    ("oddImageSize_base", 2),
    ("oddImageSize_step", 3),
    ("evenImageSizeAux 定義", 1),
    ("evenImageSizeAux_base", 2),
    ("evenImageSizeAux_step", 3),
    ("evenImageSizeAux_ge_two", 3),
    ("evenImageSizeAux_sub_two_dvd3", 12),
    ("evenImageSize 定義", 1),
    ("evenImageSize_base", 2),
    ("div3_step 補題", 10),
    ("evenImageSize_step", 6),
    ("evenImageSize_mul3_add2", 8),
    ("数値検証", 10),
    ("合計", 0),
]

total = 0
for name, lines in estimates:
    if name != "合計":
        total += lines
        print(f"  {name:40s} {lines:>3} 行")
    else:
        print(f"  {'合計':40s} {total:>3} 行")

print(f"\n推定: sorry 1個 (統合定理のみ、省略可能)")
print(f"核心定理は全て sorry なしで形式化可能")
