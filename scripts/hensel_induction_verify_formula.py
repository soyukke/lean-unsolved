"""
公式の正確な検証:
n % 2^{k+1} = 2^{k+1}-1 の条件下でのみ成立する公式。

ascendingMapIter k n * 2^k = 3^k * n + 3^k - 2^k
...は実数の式。自然数では除算の切り捨てにより一般には成立しない。

修正: n % 2^{k+1} = 2^{k+1}-1 という条件下で、
ascendingMapIter がちゃんと整数になることを確認。

さらに、Leanで使いやすい「引き算を避けた」形を設計する。
"""

def asc_map(n):
    return (3 * n + 1) // 2

def asc_map_iter(k, n):
    for _ in range(k):
        n = asc_map(n)
    return n

# 条件付き検証: n % 2^{k+1} = 2^{k+1}-1 のときのみ
print("=== 条件付き公式検証 ===")
print("n % 2^{k+1} = 2^{k+1}-1 のとき:")
print("ascendingMapIter k n * 2^k + 2^k = 3^k * (n + 1)")
print("同値: (ascendingMapIter k n + 1) * 2^k = 3^k * (n + 1)")
print()

all_ok = True
for k in range(0, 10):
    modulus = 2**(k+1)
    target = modulus - 1
    for mult in range(20):
        n = target + mult * modulus
        if n == 0:
            continue
        ak = asc_map_iter(k, n)
        lhs = (ak + 1) * 2**k
        rhs = 3**k * (n + 1)
        if lhs != rhs:
            print(f"FAIL k={k} n={n}: LHS={lhs} RHS={rhs}")
            all_ok = False

if all_ok:
    print("ALL PASS: (ascendingMapIter k n + 1) * 2^k = 3^k * (n + 1)")
    print("条件: n % 2^{k+1} = 2^{k+1} - 1")

# Lean向け: 引き算なし、除算なしの等式
print("\n=== Lean向け等式（引き算・除算なし） ===")
print("(ascendingMapIter k n + 1) * 2^k = 3^k * (n + 1)")
print()
print("帰納ステップ検証:")
print("k -> k+1:")
print("(a_{k+1} + 1) * 2^{k+1} = 3^{k+1} * (n+1)")
print()
print("a_{k+1} = (3 * a_k + 1) / 2")
print("(a_{k+1} + 1) * 2 = 3 * a_k + 1 + 2 = 3 * a_k + 3 = 3 * (a_k + 1)")
print("(a_{k+1} + 1) * 2^{k+1} = (a_{k+1} + 1) * 2 * 2^k = 3 * (a_k + 1) * 2^k")
print("= 3 * 3^k * (n+1) = 3^{k+1} * (n+1)")
print("QED!")
print()

# ただし、a_{k+1} = (3*a_k + 1) / 2 が正確に割り切れることの保証が必要
# a_k が奇数 <=> 3*a_k + 1 が偶数 (自動的に成立)
# なので (3*a_k+1)/2 は常に整数

# しかし、Lean の自然数除算では 2 | (3*a_k+1) を示す必要がある
# a_k は奇数 => 3*a_k は奇数 => 3*a_k+1 は偶数 OK

# a_k が奇数であることの証明:
# (a_k + 1) * 2^k = 3^k * (n+1), where n+1 = 2^{k+1} * m
# (a_k + 1) * 2^k = 3^k * 2^{k+1} * m = 2^k * 2 * 3^k * m
# a_k + 1 = 2 * 3^k * m
# a_k = 2 * 3^k * m - 1 (奇数)

print("=== a_k の奇数性 ===")
print("(a_k + 1) * 2^k = 3^k * (n+1), n+1 = 2^{k+1} * m")
print("=> a_k + 1 = 2 * 3^k * m")
print("=> a_k = 2 * 3^k * m - 1 (奇数)")
print()

# n % 2^{k+1} = 2^{k+1}-1 を満たすnについて、
# 各ステップの a_i も奇数であることの確認
print("=== 各ステップでの奇数性の確認 ===")
for k in range(1, 8):
    modulus = 2**(k+1)
    target = modulus - 1
    all_odd = True
    for n in [target, target + modulus, target + 2*modulus]:
        for step in range(k):
            ai = asc_map_iter(step, n)
            if ai % 2 == 0:
                all_odd = False
                print(f"  EVEN! k={k} n={n} step={step}: a_{step}={ai}")
    print(f"k={k}: All intermediate values odd? {all_odd}")

# n % 2^{k+1} = 2^{k+1}-1 は十分条件。
# 実は a_i の奇数性は帰納法で示す:
# a_0 = n は奇数 (前提)
# a_i が奇数 => 3*a_i + 1 は偶数 => a_{i+1} = (3*a_i+1)/2 は整数
# a_{i+1} の奇数性は a_i % 4 = 3 から導かれる:
#   a_i ≡ 3 (mod 4) => 3*a_i+1 ≡ 2 (mod 4) => (3*a_i+1)/2 は奇数

print("\n=== mod 4 = 3 の伝播条件 ===")
print("a_i ≡ 3 (mod 4) の場合:")
print("  3*a_i + 1 ≡ 10 ≡ 2 (mod 4)")
print("  (3*a_i + 1)/2 ≡ 奇数")
print("  さらに (3*a_i+1)/2 % 4 は a_i % 8 に依存")
print()

# 重要: a_i % 4 = 3 を全ステップで保つ条件は？
# 閉じた式から: a_i = 2 * 3^i * m_i - 1 where m_i = (n+1)/2^{i+1}
# a_i % 4 = (2 * 3^i * m_i - 1) % 4
# 3^i は奇数なので 2 * 3^i * m_i % 4 = 2 * m_i % 4
# m_i even => 2*m_i % 4 = 0 => a_i % 4 = 3
# m_i odd => 2*m_i % 4 = 2 => a_i % 4 = 1

# m_i = (n+1)/2^{i+1}
# m_i even <=> 2^{i+2} | (n+1) <=> n % 2^{i+2} = 2^{i+2}-1

# つまり: a_i % 4 = 3 <=> n % 2^{i+2} = 2^{i+2}-1

# k回連続上昇するには:
# a_0 % 4 = 3: n % 4 = 3 <=> n % 2^2 = 3
# a_1 % 4 = 3: n % 8 = 7 <=> n % 2^3 = 7
# ...
# a_{k-1} % 4 = 3: n % 2^{k+1} = 2^{k+1}-1

# これが全て同時に成立する条件は: n % 2^{k+1} = 2^{k+1}-1
# (2^{k+1} | (n+1) は 2^i | (n+1) for all i <= k+1 を含む)

print("=== 最終的な証明構造 ===")
print()
print("Lemma 1 (chain formula, 引き算なし):")
print("  ascendingMapIter_formula: n % 2 = 1 =>")
print("    (ascendingMapIter k n + 1) * 2^k = 3^k * (n + 1)")
print("  証明: k に関する帰納法")
print("    base: (n + 1) * 1 = 1 * (n + 1)")
print("    step: (a_{k+1} + 1) * 2^{k+1} = 3*(a_k+1) * 2^k = 3*3^k*(n+1) = 3^{k+1}*(n+1)")
print("    注意: (3*a_k+1)/2 + 1 = (3*a_k+3)/2 = 3*(a_k+1)/2")
print("    => (a_{k+1}+1)*2 = 3*(a_k+1) ... a_k が奇数 <=> a_k+1 が偶数 <=> 割り切れる")
print()
print("  問題: a_k が奇数であることの保証が先に必要")
print("  -> n が奇数 => a_0 = n は奇数")
print("  -> a_k が奇数 => 3a_k+1 偶数 => a_{k+1} = (3a_k+1)/2 整数")
print("  -> a_{k+1} の奇数性: a_k が奇数なら 3a_k は奇数、3a_k+1 は偶数")
print("     3a_k+1 ≡ 2 (mod 4) <=> a_k ≡ 3 (mod 4)")
print("     一般には a_{k+1} の奇偶は a_k の mod 4 に依存")
print()
print("  解決策: Lemma 1 は n が奇数のときのみ必要。")
print("  しかし中間の a_i が偶数になりうる。")
print("  ascendingMap 自体は任意の自然数に定義される:")
print("  ascendingMap(x) = (3x+1)/2 (Nat除算なので常に定義)")
print()
print("  実は、Nat除算の性質上:")
print("  x 奇数 => (3x+1)/2 = exact, (3x+1) mod 2 = 0")
print("  x 偶数 => (3x+1)/2 = floor((3x+1)/2), (3x+1) mod 2 = 1")
print("  なので x が偶数のとき (3x+1)/2 * 2 = 3x (NOT 3x+1)")
print()
print("  => chain formula は a_k が常に奇数であるときのみ正しい")
print("  => n % 2^{k+1} = 2^{k+1}-1 のとき全ての a_i が奇数")
print("  => 強い仮定が必要")
print()
print("推奨アプローチ: 主定理を直接帰納法で証明する")
print()
print("Theorem hensel_general (n k : N) (hn : n >= 1) (hodd : n % 2 = 1):")
print("  consecutiveAscents n k <-> n % 2^{k+1} = 2^{k+1} - 1")
print()
print("証明 by strong induction on k:")
print("  k = 0: trivial (consecutiveAscents n 0 is vacuously true,")
print("          n % 2 = 1 <=> n % 2^1 = 2^1-1 = 1)")
print("  k + 1:")
print("    (=>) consecutiveAscents n (k+1)")
print("      => consecutiveAscents n k (monotonicity)")
print("      => n % 2^{k+1} = 2^{k+1}-1 (IH)")
print("      + k番目のステップも上昇: syracuse(syracuseIter k n) > syracuseIter k n")
print("      => syracuseIter k n % 4 = 3")
print("      chain formula + mod analysis => n % 2^{k+2} = 2^{k+2}-1")
print()
print("    (<=) n % 2^{k+2} = 2^{k+2}-1")
print("      => n % 2^{k+1} = 2^{k+1}-1 (mod divisibility)")
print("      => consecutiveAscents n k (IH)")
print("      + chain formula => syracuseIter k n % 4 = 3")
print("      => syracuse(syracuseIter k n) > syracuseIter k n")
print("      => consecutiveAscents n (k+1)")

# 注意: k=0 の場合を再確認
print("\n=== k=0 のケース ===")
print("consecutiveAscents n 0: forall i < 0, ... は空真")
print("n % 2^1 = 2^1-1 = 1: n が奇数")
print("hodd: n % 2 = 1 が前提なので、n % 2 = 1 は自動的に成立")
print("よって k=0 は trivial")
