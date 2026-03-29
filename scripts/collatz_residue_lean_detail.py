#!/usr/bin/env python3
"""
Lean 4 証明の詳細設計: collatzResidue_succ_odd の展開

collatzResidue (n + 1) の定義展開:
  if n % 2 = 0 then 4 * collatzResidue n + 1 else collatzResidue n

n % 2 = 1 のとき:
  n % 2 = 0 は偽 (because n % 2 = 1 implies n % 2 != 0)
  if False then ... else collatzResidue n
  = collatzResidue n

Lean 4 の if-then-else は `ite (p) t e` として表現され、
Decidable インスタンスを使う。n % 2 = 0 は Decidable。

simp [collatzResidue] は定義を展開する。
omega は n % 2 = 1 から n % 2 = 0 が偽であることを導出できる。

しかし、simp [collatzResidue] が if を残す場合:
  split を使って if を場合分けし、
  omega で矛盾を導く必要があるかもしれない。

代替案:
  theorem collatzResidue_succ_odd (n : Nat) (h : n % 2 = 1) :
      collatzResidue (n + 1) = collatzResidue n := by
    unfold collatzResidue
    simp [h]

  あるいは:
    show (if n % 2 = 0 then ... else collatzResidue n) = collatzResidue n
    have : n % 2 ≠ 0 := by omega
    simp [this]
"""

# Nat.pow_succ の方向を確認
# Lean 4 Mathlib: Nat.pow_succ : n ^ (k + 1) = n ^ k * n
# あるいは pow_succ : n ^ (k + 1) = n ^ k * n (for Monoid)
# だが、rw [h_exp, Nat.pow_succ] では
# 4 ^ ((n+1)/2 + 1) = 4 ^ ((n+1)/2) * 4
# そして linarith で ih と合わせて解く

# collatzResidue_closed の omega 可能性を検証
# h: 3 * c(k) + 1 = 4^m
# h_mod3: 4^m % 3 = 1
# => 4^m = 3 * q + 1 for some q
# => c(k) = q = (4^m - 1) / 3

# omega で解けるか? omega は線形算術。
# 3 * c(k) + 1 = 4^m かつ 4^m % 3 = 1 から c(k) = (4^m - 1) / 3
# これは 3 * c(k) + 1 = 4^m と 3 | (4^m - 1) から導かれる
# omega が Nat の除算を扱えるか?
# omega は % と / を扱えるので、可能かもしれない

# 代替案: h_mod3 を使って直接
# have h_div : 3 * ((4^m - 1) / 3) = 4^m - 1 := Nat.div_mul_cancel (...)
# then omega

print("Lean 4 証明の詳細設計: collatzResidue_closed")
print()
print("方針1: omega で直接解く")
print("  h: 3 * c(k) + 1 = 4^m")
print("  h_mod3: 4^m % 3 = 1")
print("  => omega が 3 * c(k) + 1 = 4^m, 4^m % 3 = 1 から")
print("     c(k) = (4^m - 1) / 3 を導けるか?")
print()
print("方針2: 明示的に変形")
print("  have : 4^m - 1 = 3 * c(k) := by omega")
print("  have : (4^m - 1) / 3 = c(k) := by")
print("    rw [this]; exact Nat.mul_div_cancel_left c(k) (by norm_num)")
print()

# 4^m % 3 = 1 の証明
# Nat.pow_mod で 4^m % 3 = (4 % 3)^m % 3 = 1^m % 3 = 1 % 3 = 1
# Lean: Nat.pow_mod: (a ^ n) % m = ((a % m) ^ n) % m
# simp で解けそう

print("方針3: Nat.pow_mod の利用")
print("  have h_mod3 : 4 ^ m % 3 = 1 := by")
print("    rw [Nat.pow_mod]")
print("    simp  -- 4 % 3 = 1, 1^m = 1, 1 % 3 = 1")
print()

# omega が division を含む等式を解けるかテスト
# c(k) = (4^m - 1) / 3 where 3 * c(k) + 1 = 4^m and 4^m % 3 = 1
# これは:
#   3 * c(k) = 4^m - 1
#   c(k) = (4^m - 1) / 3
# Nat の除算なので 3 * c(k) = 4^m - 1 かつ 4^m >= 1 から導かれる
# omega は a = b / c を直接扱えないが、
# 3 * c(k) + 1 = 4^m から 4^m - 1 = 3 * c(k) (Nat引き算に注意) が分かり、
# (4^m - 1) / 3 = (3 * c(k)) / 3 = c(k) (by Nat.mul_div_cancel_left)

print("=" * 60)
print("最終的な Lean 4 コード設計 (collatzResidue_closed)")
print("=" * 60)

lean_closed = r"""
/-- 4^m ≡ 1 (mod 3) for all m -/
theorem four_pow_mod3 (m : Nat) : 4 ^ m % 3 = 1 := by
  induction m with
  | zero => simp
  | succ n ih =>
    rw [Nat.pow_succ]
    omega

/-- collatzResidue k = (4 ^ ((k + 1) / 2) - 1) / 3 -/
theorem collatzResidue_closed (k : Nat) :
    collatzResidue k = (4 ^ ((k + 1) / 2) - 1) / 3 := by
  have h := collatzResidue_core_eq k
  -- h: 3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2)
  set m := (k + 1) / 2
  -- 4^m >= 1
  have hge : 4 ^ m >= 1 := Nat.one_le_pow m 4 (by omega)
  -- 4^m - 1 = 3 * collatzResidue k
  have hsub : 4 ^ m - 1 = 3 * collatzResidue k := by omega
  -- (4^m - 1) / 3 = collatzResidue k
  rw [hsub, Nat.mul_div_cancel_left _ (by norm_num : (3 : Nat) > 0)]
"""
print(lean_closed)

print()
print("=" * 60)
print("collatzResidue と Hensel pattern の関連")
print("=" * 60)

# collatzResidue(k) の値は 2^{k+1} - 1 (mod 2^{k+1}) の世界で
# 連続上昇パターンに対応する "残差" を蓄積する関数

# Hensel で: k 回連続上昇 <=> n ≡ 2^{k+1} - 1 (mod 2^{k+1})
# Formula で: 2^k * T^k(n) = 3^k * n + ascentConst(k)
# ascentConst(k) = 3^k - 2^k

# collatzResidue は異なる再帰で c(k) = (4^{ceil(k/2)} - 1) / 3
# これは "2ステップごとに4倍して1を足す" 操作の累積

# 関連:
# 4 = 2^2, ceil(k/2) は「偶数ステップの回数」
# 偶数インデックスで c(k+1) = 4*c(k)+1 なので、
# 「2回のコラッツステップ（偶→奇）をまとめた操作」の定数項

print("collatzResidue(k) は 偶数インデックスごとに 4*c+1 を適用する。")
print("これは 2-adic の文脈で「2ステップごとの残差蓄積」に対応。")
print()

# ascentConst との比較
# ascentConst(k) = 3^k - 2^k = sum_{i=0}^{k-1} 3^i * 2^{k-1-i}
# collatzResidue(k) = (4^{ceil(k/2)} - 1) / 3 = sum_{i=0}^{ceil(k/2)-1} 4^i

# 両者とも幾何級数の形だが、底が異なる

def ascentConst(k):
    return 3**k - 2**k

import math
print(f"{'k':>4} {'c(k)':>12} {'a(k)':>12} {'4^ceil':>12} {'3^k':>12} {'2^k':>12}")
for k in range(12):
    ck = (4**math.ceil(k/2) - 1) // 3
    ak = ascentConst(k)
    print(f"{k:>4} {ck:>12} {ak:>12} {4**math.ceil(k/2):>12} {3**k:>12} {2**k:>12}")
