"""
一般化Waterfall公式の正確な条件分析

T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1

条件の正確な検証
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
print("条件: s + 1 <= j - 1 vs s < j の違い")
print("=" * 70)

# s + 1 <= j - 1, つまり s <= j - 2
# 帰納ステップで waterfall_step の j' = j-s >= 2 が必要
# -> s <= j - 2

# 最終ステップ s = j-1 では j-s = 1 なので waterfall_step 適用不可
# しかし公式自体 (一般化waterfall) は s < j で成り立つ

print("\ns < j (最大 s = j-1) でのテスト:")
print("このとき j - s = 1 >= 1 だが >= 2 ではない")
print("")

# 帰納法では s = 0, 1, ..., j-2 まで問題なく進む
# s = j-1 は帰納ステップで s -> s+1 として到達するが、
# そのとき s = j-2 -> s+1 = j-1 で、j-(j-2) = 2 >= 2 なのでOK!

# 待って、もう一度整理しよう
# 帰納法: s = 0 がベース、s -> s+1 が帰納ステップ
# 帰納ステップ s -> s+1 で waterfall_step を使うとき:
#   既に ih: iter_s = 3^{k+s} * 2^{j-s} - 1
#   waterfall_step に a=3^{k+s}, j'=j-s を渡す
#   -> j' >= 2 が必要 -> j-s >= 2 -> s <= j-2
#   -> s+1 <= j-1

# つまり帰納法の適用範囲は s+1 <= j-1, つまり最終的に s = j-1 まで得られる
# s = j-1 のとき、帰納ステップは s = j-2 -> s+1 = j-1
# j - (j-2) = 2 >= 2 なのでOK

# 結論: 帰納法は s < j の全範囲をカバーする

print("帰納ステップの分析:")
print("s -> s+1 のステップでは j-s >= 2 が必要")
print("s+1 < j の前提から s < j-1, つまり s <= j-2, つまり j-s >= 2")
print("")

# ただし、注意: s=0 のベースケースから帰納ステップで s=1, s=2, ..., s=j-1 まで
# 帰納ステップ s -> s+1: 前提は s+1 < j
# ih は s < j の仮定の下で適用される
# 実際の帰納法の型は:
#   forall s, s < j -> P(s)
# ベース: P(0)
# ステップ: forall s, s+1 < j -> P(s) -> P(s+1)
# s+1 < j -> s < j-1 -> s <= j-2 -> j-s >= 2

# しかし最後 P(j-1) を得るには:
#   s = j-2 のステップ: j-2+1 = j-1 < j -> P(j-2) -> P(j-1)
#   waterfall_step の j' = j-(j-2) = 2 >= 2 OK

print("具体例で確認:")
for k in range(3):
    for j in range(2, 6):
        print(f"\n  k={k}, j={j}:")
        for s in range(j):  # s = 0, 1, ..., j-1
            n = 3**k * 2**j - 1
            lhs = syracuse_iter(s, n)
            rhs = 3**(k+s) * 2**(j-s) - 1

            # 帰納ステップで使うwaterfall_stepの条件
            if s > 0:
                # 前のステップ s-1 -> s
                j_prime = j - (s-1)
                ws_applicable = j_prime >= 2
                status = f"waterfall_step j'={j_prime}{'>=2 OK' if ws_applicable else '<2 NG'}"
            else:
                status = "base case"

            print(f"    s={s}: T^{s}({n})={lhs}, 3^{k+s}*2^{j-s}-1={rhs}, "
                  f"{'OK' if lhs==rhs else 'FAIL'}, [{status}]")

print("\n" + "=" * 70)
print("Lean帰納法の正確な構造")
print("=" * 70)

print("""
theorem generalized_waterfall_formula (k j s : Nat)
    (hj : j >= 2) (hs : s < j) :
    syracuseIter s (3^k * 2^j - 1) = 3^(k+s) * 2^(j-s) - 1

帰納法 on s:

ベースケース (s=0):
  目標: syracuseIter 0 (3^k * 2^j - 1) = 3^(k+0) * 2^(j-0) - 1
  = 3^k * 2^j - 1 = 3^k * 2^j - 1
  syracuseIter_zero で左辺 simplify、simp で完了

帰納ステップ (s -> s+1):
  前提: hs : s + 1 < j (つまり j - s >= 2)
  帰納仮定: ih : s < j -> P(s) つまり P(s) が使える (s < j は hs から)

  目標: syracuseIter (s+1) (3^k * 2^j - 1) = 3^(k+s+1) * 2^(j-s-1) - 1

  ステップ 1: 右展開
    syracuseIter (s+1) _ = syracuse (syracuseIter s _)

  ステップ 2: 帰納仮定適用
    syracuseIter s (3^k * 2^j - 1) = 3^(k+s) * 2^(j-s) - 1

  ステップ 3: waterfall_step 適用
    syracuse (3^(k+s) * 2^(j-s) - 1) = 3 * 3^(k+s) * 2^(j-s-1) - 1
    条件: 3^(k+s) は奇数、3^(k+s) >= 1、j-s >= 2 (s+1 < j から)

  ステップ 4: 算術
    3 * 3^(k+s) * 2^(j-s-1) - 1 = 3^(k+s+1) * 2^(j-(s+1)) - 1

    - 3 * 3^(k+s) = 3^(k+s+1): pow_succ / ring
    - j - s - 1 = j - (s + 1): Nat 算術 (s + 1 <= j のとき)

Leanでの書き方の注意:
  - induction s with で帰納法
  - 帰納仮定 ih が自動的に s < j -> P(s) の形を持つ
  - ih (by omega) で s < j の証明を与える
  - full_cycle_bound.syracuseIter_succ_right で右展開
  - 3^n の奇数性: three_pow_odd or Odd.pow

重要: j-s-1 と j-(s+1) は Nat.sub_succ で等しいが、
Lean では直接 omega で証明できる
""")

print("=" * 70)
print("Odd 3^n -> (3^n) % 2 = 1 の変換")
print("=" * 70)

print("""
Odd.pow : Odd 3 -> Odd (3^n)
three_pow_odd (既存): 3^k % 2 = 1

waterfall_step の第1引数は a % 2 = 1 なので three_pow_odd を使える
""")

print("=" * 70)
print("最終的なLean証明の骨格")
print("=" * 70)

print("""
-- syracuseIter の右展開を独立定理として
theorem syracuseIter_succ_right (n k : Nat) :
    syracuseIter (k + 1) n = syracuse (syracuseIter k n) := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih =>
    simp only [syracuseIter_succ]
    exact ih (syracuse n)

-- 一般化 Waterfall 公式
theorem generalized_waterfall_formula (k j s : Nat)
    (hj : j >= 2) (hs : s < j) :
    syracuseIter s (3 ^ k * 2 ^ j - 1) = 3 ^ (k + s) * 2 ^ (j - s) - 1 := by
  induction s with
  | zero =>
    simp only [syracuseIter_zero, Nat.add_zero, Nat.sub_zero]
  | succ s ih =>
    have hs' : s < j := by omega
    have ih_eq := ih hs'
    -- 右展開
    rw [syracuseIter_succ_right]
    -- 帰納仮定で書き換え
    rw [ih_eq]
    -- waterfall_step 適用
    have ha_odd : 3 ^ (k + s) % 2 = 1 := three_pow_odd (k + s)
    have ha_pos : 3 ^ (k + s) >= 1 := Nat.one_le_pow _ _ (by omega)
    have hjs : j - s >= 2 := by omega
    rw [waterfall_step (3 ^ (k + s)) (j - s) ha_odd ha_pos hjs]
    -- 算術: 3 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-(s+1))
    congr 1
    · -- 3 * 3^(k+s) = 3^(k+(s+1))
      rw [show k + (s + 1) = (k + s) + 1 from by omega]
      rw [pow_succ]
      ring
    · -- j - s - 1 = j - (s + 1)  -- Nat arithmetic
      omega
""")
