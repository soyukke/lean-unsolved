"""
探索179: Lean 4 形式化設計

=== 定理の構造 ===

1. 定義: totalV2 n k (= S_k)
   - totalV2 n 0 = 0
   - totalV2 n (k+1) = totalV2 n k + v2(3 * syracuseIter k n + 1)

2. 定義: generalConst n k (= C_k)
   - generalConst n 0 = 0
   - generalConst n (k+1) = 3 * generalConst n k + 2^(totalV2 n k)

3. 主定理: syracuse_iter_general_mul_formula
   ∀ n k, n ≥ 1 → n % 2 = 1 →
     2^(totalV2 n k) * syracuseIter k n = 3^k * n + generalConst n k

4. 系: 既存公式の一般化
   - consecutiveAscents n k → totalV2 n k = k
   - consecutiveAscents n k → generalConst n k = ascentConst k

=== 帰納法の証明戦略 ===

Base case (k=0):
  2^0 * syracuseIter 0 n = 1 * n = n = 3^0 * n + 0

Inductive step (k → k+1):
  IH: 2^(S_k) * T^k(n) = 3^k * n + C_k

  Goal: 2^(S_{k+1}) * T^{k+1}(n) = 3^{k+1} * n + C_{k+1}

  Let m := T^k(n), v := v2(3m+1)
  Then: S_{k+1} = S_k + v, C_{k+1} = 3*C_k + 2^{S_k}

  LHS = 2^(S_k + v) * T(m)
      = 2^{S_k} * (2^v * T(m))
      = 2^{S_k} * (3m + 1)          -- by syracuse_mul_pow_v2
      = 3 * (2^{S_k} * m) + 2^{S_k}
      = 3 * (3^k * n + C_k) + 2^{S_k}  -- by IH
      = 3^{k+1} * n + 3*C_k + 2^{S_k}
      = 3^{k+1} * n + C_{k+1}

=== 依存する定理 ===

直接使用:
  - syracuse_mul_pow_v2: syracuse(n) * 2^v2(3n+1) = 3n+1
  - syracuseIter_zero/succ: 基本展開
  - syracuseIter_odd: T^k(n) は奇数 (n ≥ 1, n odd)
  - syracuseIter_pos: T^k(n) ≥ 1 (n ≥ 1, n odd)

暗黙的に使用:
  - v2 の定義と基本性質
  - 自然数算術 (ring, linarith, omega)

=== Lean 4 コード設計 ===
"""

lean_code = '''
import Unsolved.Collatz.Structure  -- syracuse_mul_pow_v2, syracuseIter_odd/pos

/-!
# 探索179: Syracuse反復の一般乗法公式

consecutiveAscents 不要の完全一般化された公式:
  2^{totalV2 n k} * syracuseIter k n = 3^k * n + generalConst n k

既存の syracuse_iter_mul_formula は consecutiveAscents を仮定し、
v2 が常に1の特殊ケース（連続上昇中）に限定される。
本定理はその制限を完全に除去した一般版。
-/

/-! ## 1. 定義 -/

/-- 累積2-adic付値: S_k(n) = Σ_{i=0}^{k-1} v2(3 * T^i(n) + 1) -/
def totalV2 (n : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => totalV2 n k + v2 (3 * syracuseIter k n + 1)

/-- 一般化定数項: C_0 = 0, C_{k+1} = 3 * C_k + 2^{S_k} -/
def generalConst (n : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * generalConst n k + 2 ^ totalV2 n k

/-! ## 2. 展開補題 -/

@[simp] theorem totalV2_zero (n : ℕ) : totalV2 n 0 = 0 := rfl

@[simp] theorem totalV2_succ (n k : ℕ) :
    totalV2 n (k + 1) = totalV2 n k + v2 (3 * syracuseIter k n + 1) := rfl

@[simp] theorem generalConst_zero (n : ℕ) : generalConst n 0 = 0 := rfl

@[simp] theorem generalConst_succ (n k : ℕ) :
    generalConst n (k + 1) = 3 * generalConst n k + 2 ^ totalV2 n k := rfl

/-! ## 3. 主定理 -/

/-- ★ Syracuse反復の一般乗法公式（consecutiveAscents不要）:
    2^{totalV2 n k} * syracuseIter k n = 3^k * n + generalConst n k

    帰納ステップの核心は syracuse_mul_pow_v2:
      syracuse(m) * 2^{v2(3m+1)} = 3m+1
    を用いて2^v因子をキャンセルすること。 -/
theorem syracuse_iter_general_mul (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    2 ^ totalV2 n k * syracuseIter k n = 3 ^ k * n + generalConst n k := by
  induction k generalizing n with
  | zero =>
    simp [totalV2, generalConst, syracuseIter]
  | succ k ih =>
    -- m := T^k(n), v := v2(3m+1)
    -- T^{k+1}(n) = T(m), syracuseIter (k+1) n = syracuseIter k (syracuse n)
    simp only [syracuseIter_succ, totalV2_succ, generalConst_succ]
    -- 注意: ここで変数を導入
    -- set m := syracuseIter k n  -- だが syracuseIter succ の展開後は syracuseIter k (syracuse n)
    -- 実際は syracuseIter (k+1) n = syracuseIter k (syracuse n) なので
    -- 左辺は 2^(S_k + v2(3*T^k(n)+1)) * T^k(T(n))
    -- ... 構造的にはこう書き直す:

    -- 方針変更: k に関して generalizing n なので
    -- IH: ∀ n, n ≥ 1 → n%2=1 → 2^{totalV2 n k} * T^k(n) = 3^k*n + C_k(n)
    -- を syracuse n に適用する

    -- IH を syracuse n に適用
    have hsyr_pos := syracuse_pos n hn hodd
    have hsyr_odd := syracuse_odd n hn hodd

    -- ここで IH を syracuse n に使いたいが、totalV2 は n に依存するので
    -- totalV2 (syracuse n) k と totalV2 n (k+1) の関係が必要

    -- 実は syracuseIter (k+1) n = syracuseIter k (syracuse n) だが
    -- totalV2 n (k+1) ≠ totalV2 (syracuse n) k  (一般には)
    --
    -- totalV2 n (k+1) = totalV2 n k + v2(3 * syracuseIter k n + 1)
    --   = Σ_{i=0}^{k-1} v2(3*T^i(n)+1) + v2(3*T^k(n)+1)
    --   = Σ_{i=0}^{k} v2(3*T^i(n)+1)
    --
    -- totalV2 (syracuse n) k = Σ_{i=0}^{k-1} v2(3*T^i(T(n))+1)
    --   = Σ_{i=0}^{k-1} v2(3*T^{i+1}(n)+1)
    --   = Σ_{i=1}^{k} v2(3*T^i(n)+1)
    --
    -- つまり totalV2 n (k+1) = v2(3n+1) + totalV2 (syracuse n) k
    -- これは正しい! T^0(n) = n なので先頭項が v2(3n+1)

    sorry  -- 設計用プレースホルダ

-- === 補助定理: totalV2 のシフト ===

/-- totalV2 のシフト関係:
    totalV2 n (k+1) = v2(3n+1) + totalV2 (syracuse n) k

    これは Σ_{i=0}^{k} v2(3*T^i(n)+1) = v2(3n+1) + Σ_{i=0}^{k-1} v2(3*T^{i+1}(n)+1)
    から従う。T^{i+1}(n) = T^i(T(n)) に注意。 -/
theorem totalV2_shift (n k : ℕ) :
    totalV2 n (k + 1) = v2 (3 * n + 1) + totalV2 (syracuse n) k := by
  -- 帰納法で証明
  induction k with
  | zero =>
    simp [totalV2, syracuseIter]
  | succ k ih =>
    -- totalV2 n (k+2) = totalV2 n (k+1) + v2(3*T^{k+1}(n)+1)
    -- = (v2(3n+1) + totalV2 (T(n)) k) + v2(3*T^{k+1}(n)+1)  -- by IH
    -- T^{k+1}(n) = T^k(T(n))
    -- totalV2 (T(n)) (k+1) = totalV2 (T(n)) k + v2(3*T^k(T(n))+1)
    -- = totalV2 (T(n)) k + v2(3*T^{k+1}(n)+1)
    -- よって結果 = v2(3n+1) + totalV2 (T(n)) (k+1)
    simp only [totalV2_succ, syracuseIter_succ]
    rw [ih]
    ring  -- 加法の結合性

-- === 補助定理: generalConst のシフト ===

/-- generalConst のシフト関係:
    generalConst n (k+1) = 2^{totalV2 (syracuse n) k} * (generalConst (syracuse n) k) が
    成り立つ…わけではない。

    実際は:
    generalConst n (k+1) = 3 * generalConst n k + 2^{totalV2 n k}

    syracuse n 起点で書き直すには、もう少し工夫が必要。

    帰納法を直接適用する方が良い。 -/

-- === 修正版: 帰納法の構造を再設計 ===

-- 方針: k に関する帰納法で、n を固定しない（generalizing n）
-- IH: ∀ m, m ≥ 1 → m%2=1 → 2^{S_k(m)} * T^k(m) = 3^k*m + C_k(m)
-- Goal: 2^{S_{k+1}(n)} * T^{k+1}(n) = 3^{k+1}*n + C_{k+1}(n)

-- Step 1: T^{k+1}(n) = T^k(T(n)) なので
--   LHS = 2^{S_{k+1}(n)} * T^k(T(n))

-- Step 2: S_{k+1}(n) = v2(3n+1) + S_k(T(n))  (by totalV2_shift)
--   LHS = 2^{v2(3n+1) + S_k(T(n))} * T^k(T(n))
--       = 2^{v2(3n+1)} * 2^{S_k(T(n))} * T^k(T(n))

-- Step 3: IH with m := T(n):
--   2^{S_k(T(n))} * T^k(T(n)) = 3^k * T(n) + C_k(T(n))
--   LHS = 2^{v2(3n+1)} * (3^k * T(n) + C_k(T(n)))

-- Step 4: syracuse_mul_pow_v2: T(n) * 2^{v2(3n+1)} = 3n+1
--   つまり 2^{v2(3n+1)} * T(n) = 3n+1
--   LHS = 3^k * (2^{v2(3n+1)} * T(n)) + 2^{v2(3n+1)} * C_k(T(n))
--       = 3^k * (3n+1) + 2^{v2(3n+1)} * C_k(T(n))
--       = 3^{k+1}*n + 3^k + 2^{v2(3n+1)} * C_k(T(n))

-- Step 5: RHS = 3^{k+1}*n + C_{k+1}(n)
--   C_{k+1}(n) = 3*C_k(n) + 2^{S_k(n)}

-- これだと C_k(T(n)) と C_k(n) の関係が必要で複雑...

-- === 再々設計: n を固定する帰納法 ===

-- 方針: n を固定し、k に関する帰納法。
-- IH: 2^{S_k(n)} * T^k(n) = 3^k*n + C_k(n)  [n固定]
-- Goal: 2^{S_{k+1}(n)} * T^{k+1}(n) = 3^{k+1}*n + C_{k+1}(n)

-- Step 1: 定義を展開
--   S_{k+1} = S_k + v_k where v_k = v2(3*T^k(n)+1)
--   C_{k+1} = 3*C_k + 2^{S_k}
--   T^{k+1}(n) = T(T^k(n))

-- Step 2: m := T^k(n) とおく
--   LHS = 2^{S_k + v_k} * T(m)
--       = 2^{S_k} * 2^{v_k} * T(m)
--       = 2^{S_k} * (3m+1)  [by syracuse_mul_pow_v2, rewritten]
--       = 3 * 2^{S_k} * m + 2^{S_k}
--       = 3 * (2^{S_k} * m) + 2^{S_k}

-- Step 3: IH: 2^{S_k} * m = 2^{S_k} * T^k(n) = 3^k*n + C_k
--   LHS = 3 * (3^k*n + C_k) + 2^{S_k}
--       = 3^{k+1}*n + 3*C_k + 2^{S_k}
--       = 3^{k+1}*n + C_{k+1}  = RHS  ✓

-- このアプローチが正しい! n を固定する帰納法を使う。
-- Lean では induction k (generalizing n をしない) で実現。
-- ただし、Lean の induction では generalizing n がデフォルトではない。
-- → induction k with ... (n は外で束縛) でOK

print("=== 設計完了 ===")
print()
print("核心的な洞察:")
print("1. n を固定した k に関する帰納法を使う")
print("2. IH: 2^{S_k(n)} * T^k(n) = 3^k*n + C_k(n)")
print("3. 帰納ステップで set m := T^k(n) とし:")
print("   2^{S_{k+1}} * T(m)")
print("   = 2^{S_k} * (2^{v_k} * T(m))")
print("   = 2^{S_k} * (3m+1)  [syracuse_mul_pow_v2]")
print("   = 3*(2^{S_k}*m) + 2^{S_k}")
print("   = 3*(3^k*n + C_k) + 2^{S_k}  [IH]")
print("   = 3^{k+1}*n + C_{k+1}")
print()
print("必要な補助定理:")
print("  (a) syracuse_mul_pow_v2 の「左掛け版」:")
print("      2^{v2(3m+1)} * syracuse(m) = 3m+1")
print("      既存は syracuse(m) * 2^{v2(3m+1)} = 3m+1")
print("      → mul_comm で変換可能")
print()
print("  (b) pow_add の利用:")
print("      2^{S_k + v_k} = 2^{S_k} * 2^{v_k}")
print("      → Nat.pow_add で直接得られる")
print()
print("Lean 4 の証明行数見積もり:")
print("  - totalV2 定義: 4行")
print("  - generalConst 定義: 4行")
print("  - simp補題: 8行")
print("  - 主定理: ~20行")
print("  - 合計: ~36行")
'''

print(lean_code)
exec(lean_code.split("print(")[0].split("sorry")[0].replace("sorry", ""))
# 最後の exec 部分は実行しない（Leanコード）
# 代わりに設計結果のみ出力

print("=== 設計完了 ===")
print()
print("核心的な洞察:")
print("1. n を固定した k に関する帰納法を使う")
print("2. IH: 2^{S_k(n)} * T^k(n) = 3^k*n + C_k(n)")
print("3. 帰納ステップで set m := T^k(n) とし:")
print("   2^{S_{k+1}} * T(m)")
print("   = 2^{S_k} * (2^{v_k} * T(m))")
print("   = 2^{S_k} * (3m+1)  [syracuse_mul_pow_v2]")
print("   = 3*(2^{S_k}*m) + 2^{S_k}")
print("   = 3*(3^k*n + C_k) + 2^{S_k}  [IH]")
print("   = 3^{k+1}*n + C_{k+1}")
print()
print("必要な補助定理:")
print("  (a) syracuse_mul_pow_v2 の「左掛け版」:")
print("      2^{v2(3m+1)} * syracuse(m) = 3m+1")
print("      既存は syracuse(m) * 2^{v2(3m+1)} = 3m+1")
print("      → mul_comm で変換可能")
print()
print("  (b) pow_add の利用:")
print("      2^{S_k + v_k} = 2^{S_k} * 2^{v_k}")
print("      → Nat.pow_add で直接得られる")
print()
print("Lean 4 の証明行数見積もり:")
print("  - totalV2 定義: 4行")
print("  - generalConst 定義: 4行")
print("  - simp補題: 8行")
print("  - 主定理: ~20行")
print("  - 合計: ~36行")
