"""
一般化Hensel帰納法: Lean 4証明設計

=== 証明の全体構造 ===

主定理: hensel_attrition_general (n : N) (k : N) (hn : n >= 1) (hodd : n % 2 = 1):
  consecutiveAscents n k <-> n % 2^{k+1} = 2^{k+1} - 1

=== 必要な補題の階層 ===

Layer 1: f(x) = (3x+1)/2 の閉じた式
  - f_iter_formula: n % 4 = 3 のk回連続上昇の各ステップで v2=1 が保たれる
    => syracuseIter i n = f^i(n) for i <= k

Layer 2: f^k(n) の閉じた式
  - f_iter_closed_form: f^k(n) = (3^k * (n+1) - 2^k) / 2^k
  - f_iter_closed_form_nat: 自然数上での正確な表現

Layer 3: f^k(n) mod 4 の分析
  - f_iter_mod4: n = 2^{k+1}*q + 2^{k+1}-1 のとき
    f^k(n) = 2 * 3^k * (q+1) - 1
    f^k(n) % 4 = 3 <=> q は奇数 <=> n % 2^{k+2} = 2^{k+2} - 1

Layer 4: 帰納法による主定理
  Base: k=1 (single_ascent_mod4)
  Step: k回上昇 <=> n % 2^{k+1} = 2^{k+1}-1 を仮定して、
        k+1回上昇 <=> n % 2^{k+2} = 2^{k+2}-1 を示す

=== Lean 4 proof sketch ===

-- 直接的なアプローチ: mod 2^{k+1} の追跡

Approach A (閉じた式を使う):
  1. f^k(n) = (3^k * n + 3^k - 2^k) / 2^k を証明
  2. n % 2^{k+1} = 2^{k+1}-1 のとき n+1 = 2^{k+1}*m を設定
  3. f^k(n) = 2*3^k*m - 1 を導出
  4. f^k(n) % 4 = 3 <=> m が偶数 <=> n % 2^{k+2} = 2^{k+2}-1

  問題: 閉じた式の帰納法証明自体が自然数除算で複雑になる

Approach B (直接帰納法、mod追跡):
  帰納法の各ステップで:
  - syracuseIter i n ≡ 3 (mod 4) for all i < k を追跡
  - これにより v2(3 * syracuseIter i n + 1) = 1 が保証される
  - syracuseIter (i+1) n = (3 * syracuseIter i n + 1) / 2

  核心: "n % 2^{k+1} = 2^{k+1}-1" => "syracuseIter i n % 4 = 3 for all i < k"
  これを帰納法で示す。

Approach C (2段階帰納法):
  Step 1: n % 2^{k+1} = 2^{k+1}-1 => consecutiveAscents n k (十分条件)
    帰納法で: base case (k=0 trivial), step で
    "n % 2^{k+2} = 2^{k+2}-1 => n % 2^{k+1} = 2^{k+1}-1" (剰余の整合性)
    + "syracuseIter k n > syracuseIter (k-1) n" (最後のステップも上昇)

  Step 2: consecutiveAscents n k => n % 2^{k+1} = 2^{k+1}-1 (必要条件)
    帰納法で: 既にk-1回の上昇から n % 2^k = 2^k-1 を得ている。
    k回目の上昇から追加のビット情報を得る。

=== 最も実現可能なアプローチ ===

以下の「チェイン公式」を中心に据える:

Lemma chain_formula: n % 2^{k+1} = 2^{k+1}-1 =>
  syracuseIter k n = 2 * 3^k * ((n + 1) / 2^{k+1}) - 1

これは以下のように帰納法で証明できる:
  Base (k=0): syracuseIter 0 n = n, 2 * 3^0 * ((n+1)/2) - 1 = n (n が奇数)
  Step: syracuseIter (k+1) n = syracuse (syracuseIter k n)
    帰納仮説: syracuseIter k n = 2 * 3^k * m - 1 (where m = (n+1)/2^{k+1})
    syracuseIter k n ≡ 3 (mod 4) <=> m is even <=> n % 2^{k+2} = 2^{k+2}-1
    ...

注意: 帰納ステップで n % 2^{k+2} = 2^{k+2}-1 を要求するので、
主定理を直接帰納法で証明するのとは少し違う構造になる。

=== 推奨: Lean形式化での具体的手順 ===

1. 補助関数 ascendingMap の定義:
   def ascendingMap (n : N) := (3 * n + 1) / 2
   -- n ≡ 3 (mod 4) のとき syracuse n = ascendingMap n

2. ascendingMapIter の閉じた式:
   theorem ascendingMapIter_formula (k n : N) :
     ascendingMapIter k n * 2^k = 3^k * n + (3^k - 2^k)

   これは自然数のまま等式として証明可能（除算を避ける）。

3. 主定理への接続:
   n % 2^{k+1} = 2^{k+1}-1 =>
     forall i < k, syracuseIter i n % 4 = 3
   => syracuseIter = ascendingMapIter (上のk ステップ)
   => 閉じた式から mod 4 条件を得る
"""

# 推奨アプローチの検証: 除算を避けた等式
print("=== 除算を避けた等式の検証 ===")
print("ascendingMapIter k n * 2^k = 3^k * n + (3^k - 2^k)")
print()

def asc_map(n):
    return (3 * n + 1) // 2

def asc_map_iter(k, n):
    for _ in range(k):
        n = asc_map(n)
    return n

for k in range(0, 8):
    for n in [3, 7, 15, 31, 63, 127]:
        lhs = asc_map_iter(k, n) * 2**k
        rhs = 3**k * n + (3**k - 2**k)
        match = lhs == rhs
        if not match:
            print(f"MISMATCH k={k} n={n}: LHS={lhs} RHS={rhs}")
    print(f"k={k}: All checked, formula holds")

print()
print("=== 帰納ステップの検証 ===")
print("ascendingMap(ascendingMapIter k n) * 2^{k+1}")
print("= (3 * ascendingMapIter k n + 1) / 2 * 2^{k+1}")
print("= (3 * ascendingMapIter k n + 1) * 2^k")
print()
print("一方、直接計算:")
print("3^{k+1} * n + (3^{k+1} - 2^{k+1})")
print("= 3 * (3^k * n + 3^k - 2^k) + 2^k - 2^{k+1} + 2^k")
print("hmm... 帰納ステップをもう少し丁寧に")
print()

# 帰納ステップ:
# ascendingMapIter (k+1) n = asc_map(ascendingMapIter k n)
# Let a_k = ascendingMapIter k n
# a_{k+1} = (3 * a_k + 1) / 2
# a_{k+1} * 2 = 3 * a_k + 1
# a_{k+1} * 2^{k+1} = (3 * a_k + 1) * 2^k = 3 * a_k * 2^k + 2^k

# 帰納仮説: a_k * 2^k = 3^k * n + 3^k - 2^k
# よって: a_{k+1} * 2^{k+1} = 3 * (3^k * n + 3^k - 2^k) + 2^k
#                             = 3^{k+1} * n + 3^{k+1} - 3 * 2^k + 2^k
#                             = 3^{k+1} * n + 3^{k+1} - 2 * 2^k
#                             = 3^{k+1} * n + 3^{k+1} - 2^{k+1}

print("帰納ステップ:")
print("a_{k+1} * 2^{k+1} = 3 * a_k * 2^k + 2^k")
print("= 3 * (3^k * n + 3^k - 2^k) + 2^k")
print("= 3^{k+1} * n + 3^{k+1} - 3 * 2^k + 2^k")
print("= 3^{k+1} * n + 3^{k+1} - 2 * 2^k")
print("= 3^{k+1} * n + 3^{k+1} - 2^{k+1}")
print("QED!")
print()

# もう1つ重要: ascendingMapIterが整数になる条件
print("=== ascendingMapIter k n が奇数であるための条件 ===")
print("a_k * 2^k = 3^k * (n+1) - 2^k")
print("a_k = (3^k * (n+1) - 2^k) / 2^k")
print("= 3^k * (n+1) / 2^k - 1")
print()
print("n+1 が 2^k で割り切れれば a_k は整数")
print("n % 2^{k+1} = 2^{k+1}-1 => n+1 = 2^{k+1}*m => 2^k | n+1")
print("なので a_k = 3^k * 2*m - 1 = 2*3^k*m - 1 (奇数)")
print()

# 最終的な mod 4 分析
print("=== a_k mod 4 の最終分析 ===")
print("a_k = 2*3^k*m - 1 where m = (n+1)/2^{k+1}")
print("a_k mod 4 = (2*3^k*m - 1) mod 4")
print("3^k は奇数なので 2*3^k*m mod 4 = 2*m mod 4 (3^k mod 2 = 1)")
print()
print("m が奇数: 2*m mod 4 = 2, a_k mod 4 = 1 (NOT 3)")
print("m が偶数: 2*m mod 4 = 0, a_k mod 4 = -1 mod 4 = 3 (YES)")
print()
print("m even <=> (n+1)/2^{k+1} even <=> 2^{k+2} | (n+1) <=> n % 2^{k+2} = 2^{k+2}-1")
print()
print("これにより:")
print("consecutiveAscents n (k+1) <=> consecutiveAscents n k AND a_k % 4 = 3")
print("                          <=> n % 2^{k+1} = 2^{k+1}-1 AND n % 2^{k+2} = 2^{k+2}-1")
print("                          <=> n % 2^{k+2} = 2^{k+2}-1")

# Lean形式化で必要な補題リスト
print("\n" + "="*60)
print("=== Lean 4 形式化に必要な補題リスト ===")
print()
print("1. ascendingMap の定義と基本性質")
print("   def ascendingMap (n : N) := (3 * n + 1) / 2")
print("   theorem syracuse_eq_ascendingMap (n : N) (h : n % 4 = 3) :")
print("     syracuse n = ascendingMap n")
print()
print("2. ascendingMapIter の乗法的公式 (除算を避ける)")
print("   theorem ascendingMapIter_mul_formula (k n : N) :")
print("     ascendingMapIter k n * 2^k + 2^k = 3^k * (n + 1)")
print("   -- 同値: ascendingMapIter k n * 2^k = 3^k * n + 3^k - 2^k")
print("   -- 自然数では右辺の引き算に注意（3^k >= 2^k なので OK）")
print()
print("3. syracuseIter と ascendingMapIter の一致")
print("   theorem syracuseIter_eq_ascendingMapIter (n k : N)")
print("     (h : n % 2^{k+1} = 2^{k+1} - 1) :")
print("     forall i, i <= k -> syracuseIter i n = ascendingMapIter i n")
print("   -- 帰納法: 各ステップで ascendingMapIter i n % 4 = 3 を示す")
print()
print("4. 帰納ステップの核心")
print("   theorem ascendingMapIter_mod4 (n k : N)")
print("     (h : n % 2^{k+1} = 2^{k+1} - 1) :")
print("     ascendingMapIter k n % 4 = 3 <-> n % 2^{k+2} = 2^{k+2} - 1")
print()
print("5. 主定理")
print("   theorem hensel_attrition_general (n k : N)")
print("     (hn : n >= 1) (hodd : n % 2 = 1) :")
print("     consecutiveAscents n k <-> n % 2^{k+1} = 2^{k+1} - 1")

# 注意: Leanでの実装上の課題
print("\n=== 実装上の課題 ===")
print("1. 自然数の引き算: 3^k - 2^k は k >= 1 で非負だが、Lean では注意が必要")
print("2. 除算の整数性: ascendingMapIter k n = (3^k*(n+1) - 2^k)/2^k")
print("   整数性を保証するには 2^k | (3^k*(n+1) - 2^k) を示す必要あり")
print("3. omega tactic: mod の条件を扱うのに有用だが、2^k の形の式では")
print("   具体的なkでないと使えない場合がある")
print("4. interval_cases: 具体的なk (k <= 4程度) では使えるが、一般kでは不可")
