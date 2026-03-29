#!/usr/bin/env python3
"""
探索178: omega が Nat.div を扱えない問題の回避策検証

Lean 4 の omega は Nat.div を含む等式を直接証明できないことがある。
最も安全な方法は Nat.div_add_mod を使う方法。
"""

print("=" * 70)
print("omega 回避策: Nat.div_add_mod パターン")
print("=" * 70)

lean_workaround = r"""
-- 安全な証明パターン (omega が Nat.div を直接扱えない場合)

-- Pattern A: 3 * ((4*m - 1) / 3) + 1 = 4*m の証明
theorem key_eq_mod6_eq1_safe (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
    3 * ((4 * m - 1) / 3) + 1 = 4 * m := by
  have h_div_mod : 4 * m - 1 = 3 * ((4 * m - 1) / 3) + (4 * m - 1) % 3 :=
    (Nat.div_add_mod (4 * m - 1) 3).symm
  have h_mod : (4 * m - 1) % 3 = 0 := by omega
  omega

-- Pattern B: 3 * ((2*m - 1) / 3) + 1 = 2*m の証明
theorem key_eq_mod6_eq5_safe (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 5) :
    3 * ((2 * m - 1) / 3) + 1 = 2 * m := by
  have h_div_mod : 2 * m - 1 = 3 * ((2 * m - 1) / 3) + (2 * m - 1) % 3 :=
    (Nat.div_add_mod (2 * m - 1) 3).symm
  have h_mod : (2 * m - 1) % 3 = 0 := by omega
  omega

-- Pattern C: root の奇数性 (除算を含むので同様のパターン)
theorem root_odd_mod6_eq1_safe (m : ℕ) (h : m % 6 = 1) :
    ((4 * m - 1) / 3) % 2 = 1 := by
  -- パラメータ化: m = 6k + 1
  obtain ⟨k, hk⟩ : ∃ k, m = 6 * k + 1 := by
    exact ⟨m / 6, by omega⟩
  subst hk
  -- (4*(6k+1) - 1) / 3 = (24k+3)/3 = 8k+1
  have : (4 * (6 * k + 1) - 1) / 3 = 8 * k + 1 := by omega
  rw [this]
  omega

-- Pattern D: 代替方法 - 存在を使う
theorem root_odd_mod6_eq5_safe (m : ℕ) (h : m % 6 = 5) :
    ((2 * m - 1) / 3) % 2 = 1 := by
  obtain ⟨k, hk⟩ : ∃ k, m = 6 * k + 5 := by
    exact ⟨m / 6, by omega⟩
  subst hk
  have : (2 * (6 * k + 5) - 1) / 3 = 4 * k + 3 := by omega
  rw [this]
  omega
"""

print(lean_workaround)

print("\n" + "=" * 70)
print("主定理の代替証明 (パラメータ化アプローチ)")
print("=" * 70)

lean_alt = r"""
-- 代替証明: パラメータ化で除算を消す
-- これが最も確実な方法

/-- m ≡ 1 (mod 6) のとき syracuse((4m-1)/3) = m
    パラメータ化版: m = 6k+1 として r = 8k+1 -/
theorem syracuse_root_mod6_eq1_v2 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
    syracuse ((4 * m - 1) / 3) = m := by
  -- m = 6k+1 とパラメータ化
  obtain ⟨k, hk⟩ : ∃ k, m = 6 * k + 1 := ⟨m / 6, by omega⟩
  subst hk
  -- r = (4(6k+1)-1)/3 = (24k+3)/3 = 8k+1
  have hr : (4 * (6 * k + 1) - 1) / 3 = 8 * k + 1 := by omega
  rw [hr]
  -- syracuse (8k+1) = (3(8k+1)+1) / 2^v2(3(8k+1)+1)
  -- = (24k+4) / 2^v2(24k+4)
  -- = 4(6k+1) / 2^v2(4(6k+1))
  show (3 * (8 * k + 1) + 1) / 2 ^ v2 (3 * (8 * k + 1) + 1) = 6 * k + 1
  -- 3(8k+1)+1 = 24k+4 = 4(6k+1)
  have hkey : 3 * (8 * k + 1) + 1 = 4 * (6 * k + 1) := by ring
  rw [hkey]
  -- v2(4(6k+1)) = 2 (6k+1 is odd)
  rw [show (4 : ℕ) * (6 * k + 1) = 2 * (2 * (6 * k + 1)) from by ring]
  rw [v2_two_mul (2 * (6 * k + 1)) (by omega)]
  rw [v2_two_mul (6 * k + 1) (by omega)]
  rw [v2_odd (6 * k + 1) (by omega)]
  -- 4(6k+1) / 2^2 = 4(6k+1)/4 = 6k+1
  simp
  -- or: exact Nat.mul_div_cancel_left (6*k+1) (by norm_num : 0 < 4)

/-- m ≡ 5 (mod 6) のとき syracuse((2m-1)/3) = m
    パラメータ化版: m = 6k+5 として r = 4k+3 -/
theorem syracuse_root_mod6_eq5_v2 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 5) :
    syracuse ((2 * m - 1) / 3) = m := by
  obtain ⟨k, hk⟩ : ∃ k, m = 6 * k + 5 := ⟨m / 6, by omega⟩
  subst hk
  have hr : (2 * (6 * k + 5) - 1) / 3 = 4 * k + 3 := by omega
  rw [hr]
  show (3 * (4 * k + 3) + 1) / 2 ^ v2 (3 * (4 * k + 3) + 1) = 6 * k + 5
  -- 3(4k+3)+1 = 12k+10 = 2(6k+5)
  have hkey : 3 * (4 * k + 3) + 1 = 2 * (6 * k + 5) := by ring
  rw [hkey]
  -- v2(2(6k+5)) = 1 (6k+5 is odd)
  rw [v2_two_mul (6 * k + 5) (by omega)]
  rw [v2_odd (6 * k + 5) (by omega)]
  -- 2(6k+5) / 2^1 = 6k+5
  simp
  -- or: exact Nat.mul_div_cancel_left (6*k+5) (by norm_num : 0 < 2)
"""

print(lean_alt)

# 証明戦略の比較
print("\n" + "=" * 70)
print("証明戦略の比較")
print("=" * 70)
print("""
戦略1: Nat.div_add_mod パターン
  利点: 汎用的、omega で完結しやすい
  欠点: omega が Nat.div + 剰余を同時に扱えない場合がある

戦略2: パラメータ化 (m = 6k + r)
  利点: 除算が具体的な式に置き換わる、最も確実
  欠点: subst が必要、若干冗長

戦略3: change + rewrite
  利点: syracuse の定義に直接的
  欠点: show/change の式が長い

推奨: 戦略2 (パラメータ化) が最も確実。
  omega が Nat.div を扱えない場合でも問題なく動作する。
  また、ring が 3*(8k+1)+1 = 4*(6k+1) を自動証明するので楽。
""")
