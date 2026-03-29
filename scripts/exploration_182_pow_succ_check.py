"""
pow_succ の定義方向の確認

Lean 4 / Mathlib における pow_succ:
  pow_succ (a : M) (n : ℕ) : a ^ (n + 1) = a ^ n * a
  
しかし一部のバージョンでは:
  pow_succ' (a : M) (n : ℕ) : a ^ (n + 1) = a * a ^ n

chainOffset_closed で使う形:
  4 ^ (k + 1) = 4 * 4 ^ k  ... これは pow_succ' の形

代替案:
  show (4 : ℕ) ^ (k + 1) = 4 * 4 ^ k from by ring

ring なら pow_succ の方向に依存しないので安全。
"""

print("=== chainOffset_closed の安全な証明 ===")
print("""
-- 方法A: pow_succ を使う（方向に注意）
rw [show (4 : ℕ) ^ (k + 1) = 4 * 4 ^ k from pow_succ 4 k]
-- pow_succ : a ^ (n+1) = a ^ n * a なので
-- これは 4^k * 4 になる。mul_comm で 4 * 4^k に変換が必要かも。

-- 方法B: ring で回避（最も安全）
have h4pow : (4 : ℕ) ^ (k + 1) = 4 * 4 ^ k := by ring

-- 方法C: nlinarith で一気に解く
nlinarith
""")

# 結論: ring を使えば pow_succ の方向に依存しない
print()
print("結論: chainOffset_closed の証明は以下が最も堅牢:")
print("""
theorem chainOffset_closed (k : ℕ) : 3 * chainOffset k + 1 = 4 ^ k := by
  induction k with
  | zero => simp
  | succ k ih =>
    simp only [chainOffset_succ]
    have : (4 : ℕ) ^ (k + 1) = 4 * 4 ^ k := by ring
    linarith
""")
