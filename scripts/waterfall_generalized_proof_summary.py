"""
一般化Waterfall公式のLean証明 - 最終サマリ

定理: generalized_waterfall_formula
  T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1

条件: j >= 2, s < j
"""

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

print("=" * 70)
print("最終数値検証: 大きな値での確認")
print("=" * 70)

all_ok = True
count = 0
for k in range(8):
    for j in range(2, 10):
        for s in range(j):
            n = 3**k * 2**j - 1
            lhs = syracuse_iter(s, n)
            rhs = 3**(k+s) * 2**(j-s) - 1
            if lhs != rhs:
                print(f"FAIL: k={k}, j={j}, s={s}")
                all_ok = False
            count += 1

print(f"テスト数: {count}")
print(f"結果: {'全合格' if all_ok else '失敗あり'}")

print("\n" + "=" * 70)
print("waterfall_formula との関係")
print("=" * 70)

print("""
waterfall_formula (m k) : T^k(2^m - 1) = 3^k * 2^{m-k} - 1  (k < m)

これは generalized_waterfall_formula の k=0 の場合:
  T^s(3^0 * 2^j - 1) = 3^(0+s) * 2^(j-s) - 1
  = T^s(2^j - 1) = 3^s * 2^(j-s) - 1

m を j に、k を s にリネームすれば完全に一致。
したがって generalized_waterfall_formula は waterfall_formula の真の一般化。
""")

print("=" * 70)
print("Lean証明の完全版（推奨実装）")
print("=" * 70)

print("""
/-- 一般化Waterfall公式:
    T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1

    waterfall_step を核としたs に関する帰納法で証明。
    各帰納ステップで、3^{k+s} の奇数性と j-s >= 2 を利用して
    waterfall_step を適用する。

    k=0 の場合は既存の waterfall_formula に一致する。 -/
theorem generalized_waterfall_formula (k j s : Nat)
    (hj : j >= 2) (hs : s < j) :
    syracuseIter s (3 ^ k * 2 ^ j - 1) =
    3 ^ (k + s) * 2 ^ (j - s) - 1 := by
  induction s with
  | zero =>
    simp only [syracuseIter_zero, Nat.add_zero, Nat.sub_zero]
  | succ s ih =>
    -- 帰納仮定を s < j の証明とともに適用
    have hs' : s < j := by omega
    have ih_eq := ih hs'
    -- 右展開: syracuseIter (s+1) n = syracuse (syracuseIter s n)
    rw [show syracuseIter (s + 1) (3 ^ k * 2 ^ j - 1) =
        syracuse (syracuseIter s (3 ^ k * 2 ^ j - 1)) from
      (full_cycle_bound.syracuseIter_succ_right
        (3 ^ k * 2 ^ j - 1) s).symm]
    -- 帰納仮定で書き換え
    rw [ih_eq]
    -- waterfall_step の前提条件
    have ha_odd : 3 ^ (k + s) % 2 = 1 := three_pow_odd (k + s)
    have ha_pos : 3 ^ (k + s) >= 1 :=
      Nat.one_le_pow _ _ (by omega)
    have hjs : j - s >= 2 := by omega
    -- waterfall_step 適用
    rw [waterfall_step (3 ^ (k + s)) (j - s)
      ha_odd ha_pos hjs]
    -- 目標: 3 * 3^(k+s) * 2^(j-s-1) - 1
    --     = 3^(k+(s+1)) * 2^(j-(s+1)) - 1
    -- suffices で - 1 の前の等式に帰着
    suffices h : 3 * 3 ^ (k + s) * 2 ^ (j - s - 1) =
        3 ^ (k + (s + 1)) * 2 ^ (j - (s + 1)) by
      omega
    -- 指数の等式
    have h1 : j - s - 1 = j - (s + 1) := by omega
    have h2 : k + (s + 1) = (k + s) + 1 := by omega
    rw [h1, h2, pow_succ]
    ring

-- 代替: suffices の代わりに congr 1 を使う版
-- (congr 1 が Nat.sub に対して動作する場合)
""")

print("=" * 70)
print("証明で使用する既存補題一覧")
print("=" * 70)

print("""
1. syracuseIter_zero: syracuseIter 0 n = n
2. full_cycle_bound.syracuseIter_succ_right:
   syracuse (syracuseIter k n) = syracuseIter (k+1) n
3. waterfall_step:
   a%2=1, a>=1, j>=2 => syracuse(a*2^j-1) = 3*a*2^{j-1}-1
4. three_pow_odd: 3^k % 2 = 1
5. Nat.one_le_pow: n^k >= 1 (n >= 1)
6. pow_succ: a^(n+1) = a^n * a

すべて Formula.lean / Structure.lean / Defs.lean で定義済み。
新しい補題は不要。
""")

print("=" * 70)
print("証明の難易度評価")
print("=" * 70)

print("""
難易度: 中程度

理由:
1. 帰納法の構造は単純明快
2. 各ステップの論理は明確 (waterfall_step の直接適用)
3. 算術は omega / ring で処理可能
4. 自然数引き算の処理が多少面倒だが omega で解決可能

潜在的な問題:
1. full_cycle_bound.syracuseIter_succ_right の
   アクセス可能性 (private/where 節の問題)
   -> 解決策: 同等の定理を独立して定義
2. congr 1 が Nat.sub - 1 に対して期待通り動くか
   -> 解決策: suffices で等式に帰着
3. rw の順序が重要 (waterfall_step の rw 後の
   目標の形が期待通りか)
   -> 解決策: show で目標を明示的に書き換え

結論:
既存の waterfall_step を核とした帰納法証明は
実現可能であり、Lean 4 + Mathlib の標準的なタクティクで
完結する。新しい数学的アイデアは不要で、純粋に
既存の結果の組み合わせと算術処理で証明できる。
""")
