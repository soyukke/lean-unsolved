"""
Lean証明の詳細設計 - 算術ステップの問題点と解決策
"""

print("=" * 70)
print("Lean証明の詳細な障害分析")
print("=" * 70)

print("""
障害1: congr 1 と自然数引き算

  目標: 3 * 3^(k+s) * 2^(j-s-1) - 1 = 3^(k+s+1) * 2^(j-(s+1)) - 1

  congr 1 で - 1 を消すと:
    3 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-(s+1))

  しかし、自然数の引き算で a - 1 = b - 1 から a = b は
  a >= 1 かつ b >= 1 のとき成り立つ。
  congr 1 は Lean で使えるかどうか文脈依存。

  代替策: Nat.sub_right_injective を使うか、
  omega / nlinarith で直接証明する。

  正確には:
    3 * 3^(k+s) * 2^(j-s-1) >= 1  (3, 3^(k+s), 2^(j-s-1) >= 1)
    3^(k+s+1) * 2^(j-(s+1)) >= 1  (同様)
  なので a - 1 = b - 1 <-> a = b は成立。

  ただし、そもそも Lean の Nat.sub は saturation subtraction なので
  congr 1 が素直に動くか不明。

  より安全な方法:
    have h1 : 3 * 3^(k+s) * 2^(j-s-1) >= 1 := by positivity
    have h2 : 3^(k+s+1) * 2^(j-(s+1)) >= 1 := by positivity
    suffices 3 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-(s+1)) by omega
    <prove equality>

障害2: waterfall_step の出力形式

  waterfall_step の声明:
    syracuse (a * 2^j - 1) = 3 * a * 2^(j-1) - 1

  出力: 3 * a * 2^(j-1) - 1

  一方、目標は: 3^(k+s+1) * 2^(j-(s+1)) - 1

  waterfall_step に a = 3^(k+s), j' = j-s を渡すと:
    syracuse (3^(k+s) * 2^(j-s) - 1) = 3 * 3^(k+s) * 2^(j-s-1) - 1

  ここで j-s-1 は Nat.sub の定義より j-s から 1 を引いた値。
  j-s >= 2 なので j-s-1 >= 1。

  目標は 3^(k+s+1) * 2^(j-(s+1)) - 1

  等式を示す必要がある:
    3 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-(s+1))

  左辺: 3^1 * 3^(k+s) * 2^(j-s-1)
       = 3^((k+s)+1) * 2^(j-s-1)

  右辺: 3^(k+s+1) * 2^(j-(s+1))
       = 3^(k+s+1) * 2^(j-s-1)  (j-(s+1) = j-s-1 when s+1 <= j)

  (k+s)+1 = k+s+1 は trivially true
  j-(s+1) = j-s-1 は s+1 <= j のとき true (omega で証明)

  よって十分な等式:
    3 * 3^(k+s) = 3^(k+s+1) ... (A)
    j - s - 1 = j - (s + 1) ... (B)
  から:
    3 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-(s+1))

障害3: pow_succ の方向

  Lean 4 (Mathlib) では:
    pow_succ : a^(n+1) = a^n * a
  or
    pow_succ' : a^(n+1) = a * a^n

  我々は 3^(k+s+1) = 3 * 3^(k+s) を示したい。
  これは pow_succ' の形: a^(n+1) = a * a^n  (a=3, n=k+s)

  しかし 3 * 3^(k+s) は乗算の順序が逆になりえる。
  ring で統一可能。

障害4: Nat.sub の canonical 形

  Lean では j - s - 1 が (j - s) - 1 として解釈される。
  一方 j - (s + 1) は別の形。
  s + 1 <= j のとき両者は等しいが、Lean の型チェッカーは
  自動的に等しいとは認識しない。

  解決: have h_eq : j - s - 1 = j - (s + 1) := by omega
  で明示的に等式を導入し、rw する。

  ただし Lean の rw は Nat.sub の正規化をうまく扱えないことがある。
  conv を使う必要があるかもしれない。

  代替: show を使って目標を書き換える
    show ... = 3^(k+(s+1)) * 2^(j-s-1) - 1
  としてから等式を示す。
""")

print("=" * 70)
print("最終的なLean証明（完全版）")
print("=" * 70)

print("""
-- 必要に応じて syracuseIter_succ_right を独立して定義
-- (full_cycle_bound.syracuseIter_succ_right が使えない場合)

private theorem syracuseIter_succ_right' (n k : Nat) :
    syracuseIter (k + 1) n = syracuse (syracuseIter k n) := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih =>
    simp only [syracuseIter_succ]
    exact ih (syracuse n)

/-- 一般化Waterfall公式:
    T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1
    waterfall_step を用いた帰納法による証明。

    条件:
    - j >= 2 (初期値 3^k * 2^j - 1 が waterfall 構造を持つため)
    - s < j (反復回数が指数を超えない)

    これは waterfall_formula (k=0) の一般化であり、
    3^k * 2^j - 1 型の数の軌道が完全に予測可能であることを示す。-/
theorem generalized_waterfall_formula (k j s : Nat)
    (hj : j >= 2) (hs : s < j) :
    syracuseIter s (3 ^ k * 2 ^ j - 1) = 3 ^ (k + s) * 2 ^ (j - s) - 1 := by
  induction s with
  | zero =>
    -- 目標: 3^k * 2^j - 1 = 3^(k+0) * 2^(j-0) - 1
    simp only [syracuseIter_zero, Nat.add_zero, Nat.sub_zero]
  | succ s ih =>
    -- 前提: s + 1 < j
    -- ih: s < j -> syracuseIter s (...) = 3^(k+s) * 2^(j-s) - 1
    have hs' : s < j := by omega
    have ih_eq := ih hs'
    -- Step 1: 右展開
    -- syracuseIter (s+1) n = syracuse (syracuseIter s n)
    rw [syracuseIter_succ_right']
    -- Step 2: 帰納仮定で書き換え
    rw [ih_eq]
    -- 目標: syracuse (3^(k+s) * 2^(j-s) - 1) = 3^(k+(s+1)) * 2^(j-(s+1)) - 1
    -- Step 3: waterfall_step 適用
    have ha_odd : 3 ^ (k + s) % 2 = 1 := three_pow_odd (k + s)
    have ha_pos : 3 ^ (k + s) >= 1 := Nat.one_le_pow _ _ (by omega)
    have hjs : j - s >= 2 := by omega
    rw [waterfall_step (3 ^ (k + s)) (j - s) ha_odd ha_pos hjs]
    -- 目標: 3 * 3^(k+s) * 2^(j-s-1) - 1 = 3^(k+(s+1)) * 2^(j-(s+1)) - 1
    -- Step 4: 算術
    -- j - s - 1 = j - (s + 1)
    have hsub : j - s - 1 = j - (s + 1) := by omega
    -- 3 * 3^(k+s) = 3^(k+s+1) = 3^(k+(s+1))
    have hpow : 3 * 3 ^ (k + s) = 3 ^ (k + (s + 1)) := by
      rw [show k + (s + 1) = (k + s) + 1 from by omega, pow_succ]
      ring
    -- congr を使って - 1 を消す
    -- suffices で等式に帰着
    suffices h : 3 * 3 ^ (k + s) * 2 ^ (j - s - 1) =
        3 ^ (k + (s + 1)) * 2 ^ (j - (s + 1)) by
      omega  -- a >= 1 かつ b >= 1 のとき a - 1 = b - 1 <-> a = b
    rw [hsub, hpow]

注意: 最後の omega は少し乱暴かもしれない。
以下の方がより明示的:
    rw [hsub, hpow]
    -- 目標: 3^(k+(s+1)) * 2^(j-(s+1)) = 3^(k+(s+1)) * 2^(j-(s+1))
    -- rfl
""")

print("=" * 70)
print("代替アプローチ: 加法形式での証明")
print("=" * 70)

print("""
自然数の引き算を避ける加法形式:

定理: syracuseIter s (3^k * 2^j - 1) + 1 = 3^(k+s) * 2^(j-s)

これなら引き算が現れず、Nat の問題を回避できる。

ただし + 1 と - 1 の変換は omega で簡単にできるので、
直接的な引き算形式でも問題ない可能性が高い。

加法形式の証明:
  induction s with
  | zero =>
    simp only [syracuseIter_zero, Nat.add_zero, Nat.sub_zero]
    -- 3^k * 2^j - 1 + 1 = 3^k * 2^j
    have : 3^k * 2^j >= 1 := by positivity
    omega
  | succ s ih =>
    rw [syracuseIter_succ_right']
    -- ih: iter_s + 1 = 3^(k+s) * 2^(j-s)
    -- 目標: syracuse(iter_s) + 1 = 3^(k+s+1) * 2^(j-s-1)
    -- waterfall_step から:
    --   syracuse(iter_s) = 3 * 3^(k+s) * 2^(j-s-1) - 1
    --   => syracuse(iter_s) + 1 = 3 * 3^(k+s) * 2^(j-s-1)
    --                            = 3^(k+s+1) * 2^(j-s-1)
    -- ここで iter_s = 3^(k+s) * 2^(j-s) - 1 を使う
    ...
""")
