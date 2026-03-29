"""
探索182 (続き): chainElem_odd の証明設計

chainElem(n, k) % 2 = 1 の証明に必要な要素を詳細に分析する。

方針A (再帰的定義ベース):
  base: chainElem(n, 0) = n, n % 2 = 1 => OK
  step: chainElem(n, k+1) = 4 * chainElem(n, k) + 1
        4 * (odd) + 1 = even + 1 = odd => OK
  これは非常にシンプル！

方針B (閉形式ベース):
  chainElem(n, k) = 4^k * n + (4^k - 1)/3
  k=0: n (奇数)
  k>=1: 4^k*n は偶数、(4^k-1)/3 は奇数 => 偶数+奇数 = 奇数
  (4^k-1)/3 の奇数性はやや面倒

結論: 方針Aが圧倒的にシンプル。再帰的定義を使う。
"""

# Lean における定義設計
# 方法1: 再帰関数として直接定義（推奨）
print("=== Lean定義設計 ===")
print()
print("--- 方法1: 再帰関数による定義 ---")
print("""
/-- 逆像鎖のオフセット: c(0)=0, c(k+1)=4c(k)+1 -/
def chainOffset : ℕ → ℕ
  | 0     => 0
  | k + 1 => 4 * chainOffset k + 1

/-- 逆像鎖の第k要素: 4^k * n + c(k) -/
def chainElem (n : ℕ) : ℕ → ℕ
  | 0     => n
  | k + 1 => 4 * chainElem n k + 1
""")

# chainElem の再帰的定義のメリット:
# 1. chainOffset を直接使わずに済む（chainElem自体が再帰的）
# 2. simp/unfold で展開が容易
# 3. 帰納法が直接適用できる

# ただし、chainElem が chainOffset と整合的であることも補題として証明可能:
# chainElem n k = 4^k * n + chainOffset k

print("--- 整合性補題 ---")
print("""
theorem chainElem_eq_pow_mul_add (n k : ℕ) :
    chainElem n k = 4 ^ k * n + chainOffset k

-- 証明: k に関する帰納法
-- base: chainElem n 0 = n = 4^0 * n + chainOffset 0 = 1*n + 0 = n ✓
-- step: chainElem n (k+1) = 4 * chainElem n k + 1
--       = 4 * (4^k * n + chainOffset k) + 1  [by IH]
--       = 4^(k+1) * n + (4 * chainOffset k + 1)
--       = 4^(k+1) * n + chainOffset (k+1) ✓
""")

print()
print("=== 主要証明の詳細設計 ===")
print()

# syracuse_chainElem の完全な証明設計
print("--- syracuse_chainElem ---")
print("""
theorem syracuse_chainElem (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuse (chainElem n k) = syracuse n := by
  induction k with
  | zero => simp [chainElem]
  | succ k ih =>
    -- Goal: syracuse (chainElem n (k+1)) = syracuse n
    -- chainElem n (k+1) = 4 * chainElem n k + 1
    simp only [chainElem]
    -- Now goal: syracuse (4 * chainElem n k + 1) = syracuse n
    -- Use syracuse_four_mul_add_one:
    --   需要: chainElem n k ≥ 1 と chainElem n k % 2 = 1
    have hpos : chainElem n k ≥ 1 := chainElem_pos n k hn
    have hodd_k : chainElem n k % 2 = 1 := chainElem_odd n k hodd
    rw [syracuse_four_mul_add_one (chainElem n k) hpos hodd_k]
    exact ih
""")

# chainElem_odd の証明設計
print("--- chainElem_odd ---")
print("""
theorem chainElem_odd (n : ℕ) (k : ℕ) (hodd : n % 2 = 1) :
    chainElem n k % 2 = 1 := by
  induction k with
  | zero => simp [chainElem]; exact hodd
  | succ k ih =>
    simp only [chainElem]
    -- chainElem n (k+1) = 4 * chainElem n k + 1
    -- 4 * x + 1 は常に奇数
    omega  -- 4 * (chainElem n k) + 1 の mod 2 = 1
    -- あるいは: have : (4 * chainElem n k + 1) % 2 = 1 := by omega
""")

# chainElem_pos の証明設計
print("--- chainElem_pos ---")
print("""
theorem chainElem_pos (n : ℕ) (k : ℕ) (hn : n ≥ 1) :
    chainElem n k ≥ 1 := by
  induction k with
  | zero => simp [chainElem]; exact hn
  | succ k ih =>
    simp only [chainElem]
    -- 4 * chainElem n k + 1 ≥ 1
    omega  -- 4 * (≥1) + 1 ≥ 1
""")

print()
print("=== omega の適用可能性チェック ===")

# Lean の omega タクティクは線形算術を解ける
# 4 * x + 1 % 2 = 1 は omega で解けるか?
# omega は mod を扱えない場合がある。

# 代替案: 明示的に証明
print("""
代替証明 (chainElem_odd のステップ):
    have h : chainElem n k % 2 = 1 := ih
    -- Goal: (4 * chainElem n k + 1) % 2 = 1
    -- 方法1: omega（mod 2 を直接扱える場合）
    -- 方法2: Nat.add_mod + Nat.mul_mod を使う
    --   (4 * x + 1) % 2
    --   = ((4 * x) % 2 + 1 % 2) % 2
    --   = (0 + 1) % 2
    --   = 1
    -- Lean: rw [Nat.add_mul_mod_self_left] or similar
    omega
""")

# omega は Lean 4 の最近のバージョンで mod を扱えるようになっている
# ただし確実性のために代替案も用意

print("=== 完全なLeanコード設計 ===")
print("""
/-!
## 逆像鎖 (Inverse Image Chain)

Syracuse関数の逆像構造: n → 4n+1 → 4(4n+1)+1 → ... の鎖を形式化。
主定理: この鎖の全要素は同じSyracuse像を持つ。(探索182)
-/

/-- 逆像鎖のオフセット列: c(0)=0, c(k+1)=4c(k)+1 -/
def chainOffset : ℕ → ℕ
  | 0     => 0
  | k + 1 => 4 * chainOffset k + 1

/-- 逆像鎖の第k要素: chainElem n 0 = n, chainElem n (k+1) = 4 * chainElem n k + 1 -/
def chainElem (n : ℕ) : ℕ → ℕ
  | 0     => n
  | k + 1 => 4 * chainElem n k + 1

@[simp] theorem chainOffset_zero : chainOffset 0 = 0 := rfl
@[simp] theorem chainOffset_succ (k : ℕ) : chainOffset (k + 1) = 4 * chainOffset k + 1 := rfl
@[simp] theorem chainElem_zero (n : ℕ) : chainElem n 0 = n := rfl
@[simp] theorem chainElem_succ (n k : ℕ) : chainElem n (k + 1) = 4 * chainElem n k + 1 := rfl

/-- chainElem と chainOffset の関係 -/
theorem chainElem_eq_pow_mul_add (n k : ℕ) :
    chainElem n k = 4 ^ k * n + chainOffset k := by
  induction k with
  | zero => simp
  | succ k ih => simp [ih]; ring

/-- chainElem は常に正（n≥1のとき）-/
theorem chainElem_pos (n k : ℕ) (hn : n ≥ 1) : chainElem n k ≥ 1 := by
  induction k with
  | zero => simp; exact hn
  | succ k ih => simp; omega

/-- chainElem は常に奇数（nが奇数のとき）-/
theorem chainElem_odd (n k : ℕ) (hodd : n % 2 = 1) : chainElem n k % 2 = 1 := by
  induction k with
  | zero => simp; exact hodd
  | succ k ih => simp; omega

/-- ★主定理: 逆像鎖の全要素は同じSyracuse像を持つ (探索182) -/
theorem syracuse_chainElem (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuse (chainElem n k) = syracuse n := by
  induction k with
  | zero => simp
  | succ k ih =>
    simp only [chainElem_succ]
    rw [syracuse_four_mul_add_one _ (chainElem_pos n k hn) (chainElem_odd n k hodd)]
    exact ih
""")
