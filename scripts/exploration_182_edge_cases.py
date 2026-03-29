"""
探索182 (続き): エッジケースと代替証明経路の分析

1. simp がうまく動かない場合の代替
2. omega が mod を扱えない場合の代替
3. chainElem_eq_pow_mul_add で ring が動くかの分析
4. 名前衝突の確認
"""

print("=== 1. simp の挙動分析 ===")
print("""
chainElem_zero は rfl なので simp で展開できる。
chainElem_succ も rfl なので simp で展開できる。

潜在的問題:
- `simp [chainElem]` は再帰関数を展開しようとして
  無限ループする可能性がある。
- 推奨: `simp only [chainElem_succ]` や `simp only [chainElem_zero]` を使う。
- chainElem を @[simp] 属性で定義しないこと。
  代わりに展開定理 chainElem_zero/chainElem_succ を @[simp] にする。
""")

print("=== 2. omega と mod の分析 ===")
print("""
Lean 4 の omega タクティクは Nat.mod を扱える（バージョン依存）。

問題になりうるケース:
  Goal: (4 * chainElem n k + 1) % 2 = 1
  omega には chainElem n k の値が不明。
  しかし `ih : chainElem n k % 2 = 1` があれば、
  omega は以下の推論が可能:
    ∃ q, chainElem n k = 2*q + 1
    4*(2*q+1) + 1 = 8*q + 5
    (8*q+5) % 2 = 1

代替案（omega が失敗する場合）:
  have h := ih  -- chainElem n k % 2 = 1
  -- (4 * x + 1) % 2 = 1 は x の値によらない
  -- 4*x は常に偶数なので 4*x + 1 は常に奇数
  have : (4 * chainElem n k + 1) % 2 = 1 := by
    have : (4 * chainElem n k) % 2 = 0 := by
      rw [Nat.mul_mod]; norm_num
    omega
""")

print("=== 3. chainElem_eq_pow_mul_add の ring 分析 ===")
print("""
帰納法のステップ:
  ih : chainElem n k = 4 ^ k * n + chainOffset k
  Goal: 4 * chainElem n k + 1 = 4 ^ (k + 1) * n + (4 * chainOffset k + 1)

simp [ih] で ih を代入した後:
  4 * (4 ^ k * n + chainOffset k) + 1 = 4 ^ (k + 1) * n + (4 * chainOffset k + 1)

これは ring で解ける：
  LHS = 4 * 4^k * n + 4 * chainOffset k + 1
  RHS = 4^(k+1) * n + 4 * chainOffset k + 1
  4 * 4^k = 4^(k+1) なので等しい。

ただし Lean で pow_succ の扱いに注意:
  4 ^ (k + 1) = 4 * 4 ^ k  （Lean はこれを自動認識するか？）
  ring はこれを扱える。
""")

print("=== 4. 名前衝突の確認 ===")
print("""
既存のコードベースで chainOffset, chainElem が使われていないか確認が必要。
（Grep で確認済み: 使われていない）

Syracuse関数の定義は Defs.lean にあり、
syracuse_four_mul_add_one は Structure.lean にある。
新しい定理は Structure.lean に追加する形が自然。
""")

print("=== 5. 追加の系定理 ===")
print("""
主定理から直接導出できる系:

/-- 逆像鎖は syracuseIter に対しても保存される -/
theorem syracuseIter_chainElem (n k j : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuseIter j (chainElem n k) = syracuseIter j n := by
  induction j generalizing n with
  | zero => simp
  | succ j ih =>
    simp only [syracuseIter_succ]
    rw [syracuse_chainElem n k hn hodd]

/-- chainOffset の閉形式 -/
theorem chainOffset_closed (k : ℕ) : 3 * chainOffset k + 1 = 4 ^ k := by
  induction k with
  | zero => simp
  | succ k ih =>
    simp
    -- 3 * (4 * chainOffset k + 1) + 1 = 4 * 4^k
    -- 12 * chainOffset k + 3 + 1 = 4 * 4^k
    -- 12 * chainOffset k + 4 = 4 * 4^k
    -- 4 * (3 * chainOffset k + 1) = 4 * 4^k
    -- 3 * chainOffset k + 1 = 4^k  [by ih]
    linarith [ih]

-- これは chainOffset k = (4^k - 1) / 3 と等価
-- 自然数での除算を避けるため 3 * c(k) + 1 = 4^k の形が扱いやすい
""")

# chainOffset_closed の数値検証
print("chainOffset_closed の数値検証:")
for k in range(10):
    c = (4**k - 1) // 3
    lhs = 3 * c + 1
    rhs = 4**k
    print(f"  k={k}: 3*c({k})+1 = {lhs}, 4^{k} = {rhs}, match={lhs==rhs}")

print()
print("=== 6. 最終的な依存関係グラフ ===")
print("""
既存:
  syracuse_four_mul_add_one (Structure.lean, 行618)
  syracuse_pos (Structure.lean, 行243)
  syracuse_odd (Structure.lean, 行575)

新規定義:
  chainOffset : ℕ → ℕ
  chainElem : ℕ → ℕ → ℕ

新規定理（依存順）:
  1. chainOffset_zero     [rfl]
  2. chainOffset_succ     [rfl]
  3. chainElem_zero       [rfl]
  4. chainElem_succ       [rfl]
  5. chainElem_pos        [chainElem_succ, omega]
  6. chainElem_odd        [chainElem_succ, omega]
  7. chainElem_eq_pow_mul_add  [chainElem_succ, ring]  -- オプション
  8. chainOffset_closed   [chainOffset_succ, linarith]  -- オプション
  9. syracuse_chainElem   [chainElem_succ, chainElem_pos, chainElem_odd, syracuse_four_mul_add_one]
  10. syracuseIter_chainElem  [syracuse_chainElem]  -- オプション
""")
