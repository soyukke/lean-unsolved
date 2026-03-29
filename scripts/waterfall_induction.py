"""
Waterfall公式の一般k帰納法証明とconsecutiveAscentsの接続

目標:
1. T^k(2^m - 1) = 3^k * 2^{m-k} - 1 (k < m) を帰納法で検証
2. 2^m - 1 が m-1 回連続上昇することの検証
3. consecutiveAscents との接続パスの分析
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)}"""
    m = 3 * n + 1
    return m // (2 ** v2(m))

def syracuse_iter(k, n):
    """Syracuse反復 T^k(n)"""
    for _ in range(k):
        n = syracuse(n)
    return n

print("=" * 70)
print("1. Waterfall公式 T^k(2^m - 1) = 3^k * 2^{m-k} - 1 の数値検証")
print("=" * 70)

for m in range(2, 16):
    n = 2**m - 1
    print(f"\nm = {m}, n = 2^{m} - 1 = {n}")
    for k in range(0, m):
        tk = syracuse_iter(k, n)
        expected = 3**k * 2**(m-k) - 1
        match = "OK" if tk == expected else "FAIL"
        print(f"  k={k}: T^{k}({n}) = {tk}, 3^{k}*2^{m-k}-1 = {expected}  [{match}]")
    # k = m-1 の値を特に注目
    tm1 = syracuse_iter(m-1, n)
    expected_m1 = 2 * 3**(m-1) - 1
    print(f"  -> k=m-1={m-1}: T^{{m-1}} = {tm1} = 2*3^{m-1}-1 = {expected_m1}")
    assert tm1 == expected_m1

print("\n" + "=" * 70)
print("2. 連続上昇の検証: 2^m-1 が m-1 回連続上昇するか")
print("=" * 70)

for m in range(2, 16):
    n = 2**m - 1
    ascents = 0
    current = n
    while True:
        next_val = syracuse(current)
        if next_val > current:
            ascents += 1
            current = next_val
        else:
            break
    # m-1 回目の値が mod 4 == 1 か
    tm1 = syracuse_iter(m-1, n)
    print(f"m={m:2d}: n={n:10d}, ascents={ascents}, m-1={m-1}, "
          f"T^{{m-1}} mod 4 = {tm1 % 4}, match={'OK' if ascents == m-1 else 'FAIL'}")

print("\n" + "=" * 70)
print("3. mod 2^{k+1} 条件の検証: 2^m-1 mod 2^{k+1} = 2^{k+1}-1")
print("=" * 70)

for m in range(2, 12):
    n = 2**m - 1
    print(f"\nm = {m}, n = {n}")
    for k in range(1, m):
        mod_val = n % (2**(k+1))
        expected_mod = 2**(k+1) - 1
        print(f"  k={k}: n mod 2^{k+1} = {mod_val}, 2^{k+1}-1 = {expected_mod}  "
              f"{'OK' if mod_val == expected_mod else 'FAIL'}")

print("\n" + "=" * 70)
print("4. 帰納法のステップ分析: T(3^k * 2^{m-k} - 1)")
print("=" * 70)
print("\n基礎ケース (k=0): T^0(2^m - 1) = 2^m - 1 = 3^0 * 2^m - 1  [trivial]")
print("\n帰納ステップ: T(3^k * 2^{m-k} - 1) = 3^{k+1} * 2^{m-k-1} - 1")
print("   n_k = 3^k * 2^{m-k} - 1")
print("   k < m-1 のとき m-k >= 2 なので 2^{m-k} >= 4")
print("   n_k = 3^k * 2^{m-k} - 1 ≡ -1 (mod 4) = 3 (mod 4)")
print("   [∵ 3^k * 2^{m-k} は 4 の倍数 (m-k >= 2)]")
print("   よって v2(3*n_k + 1) = 1, T(n_k) = (3*n_k + 1)/2")
print("   = (3*(3^k * 2^{m-k} - 1) + 1) / 2")
print("   = (3^{k+1} * 2^{m-k} - 3 + 1) / 2")
print("   = (3^{k+1} * 2^{m-k} - 2) / 2")
print("   = 3^{k+1} * 2^{m-k-1} - 1")

# 数値で確認
print("\n数値確認:")
for m in range(3, 10):
    for k in range(0, m-1):
        n_k = 3**k * 2**(m-k) - 1
        tn_k = syracuse(n_k)
        expected = 3**(k+1) * 2**(m-k-1) - 1
        # mod 4 check
        mod4 = n_k % 4
        v2_val = v2(3*n_k + 1)
        print(f"  m={m}, k={k}: n_k={n_k}, mod4={mod4}, v2(3n+1)={v2_val}, "
              f"T(n_k)={tn_k}, expected={expected}  "
              f"{'OK' if tn_k == expected else 'FAIL'}")

print("\n" + "=" * 70)
print("5. mod 4 = 3 の証明分析: n_k ≡ 3 (mod 4) when k < m-1")
print("=" * 70)

print("\nn_k = 3^k * 2^{m-k} - 1")
print("k < m-1 ⟹ m-k ≥ 2 ⟹ 4 | 2^{m-k}")
print("⟹ 4 | 3^k * 2^{m-k}")
print("⟹ n_k ≡ -1 ≡ 3 (mod 4)")
print("\nこれが帰納ステップの核心: 各ステップで v2 = 1 が保証される")

print("\n" + "=" * 70)
print("6. consecutiveAscents 接続分析")
print("=" * 70)

print("""
接続パスは2つ:

パスA: Waterfall公式 → consecutiveAscents
  T^k(2^m-1) = 3^k * 2^{m-k} - 1 (k < m-1)
  これらの値は全て mod 4 ≡ 3 (上で証明)
  syracuse(n) > n ⟺ n ≡ 3 (mod 4) (既存の syracuse_gt_of_mod4_eq3)
  ∴ 2^m - 1 は m-1 回連続上昇

パスB: consecutiveAscents → Waterfall公式
  consecutiveAscents (2^m-1) k と syracuse_iter_mul_formula を使って
  2^k * T^k(2^m-1) = 3^k * (2^m-1) + ascentConst k
                    = 3^k * 2^m - 3^k + (3^k - 2^k)  [ascentConst k = 3^k - 2^k]
                    = 3^k * 2^m - 2^k
  ∴ T^k(2^m-1) = (3^k * 2^m - 2^k) / 2^k = 3^k * 2^{m-k} - 1
""")

# パスBの数値確認
print("パスBの数値確認:")
for m in range(2, 10):
    n = 2**m - 1
    for k in range(1, m):
        # syracuse_iter_mul_formula: 2^k * T^k(n) = 3^k * n + ascentConst(k)
        tk = syracuse_iter(k, n)
        lhs = 2**k * tk
        ascent_const = 3**k - 2**k
        rhs = 3**k * n + ascent_const
        waterfall = 3**k * 2**(m-k) - 1
        print(f"  m={m}, k={k}: 2^k*T^k = {lhs}, 3^k*n+ac = {rhs}, "
              f"T^k = {tk} = 3^k*2^{{m-k}}-1 = {waterfall}  "
              f"{'OK' if lhs == rhs and tk == waterfall else 'FAIL'}")

print("\n" + "=" * 70)
print("7. mersenne_orbit_mul との関係")
print("=" * 70)

print("""
既存の mersenne_orbit_mul:
  2^k * T^k(2^m-1) + 2^k = 3^k * 2^m

これを変形:
  2^k * T^k(2^m-1) = 3^k * 2^m - 2^k
  T^k(2^m-1) = (3^k * 2^m - 2^k) / 2^k = 3^k * 2^{m-k} - 1

∴ mersenne_orbit_mul は実質的に Waterfall公式そのものを含んでいる！
""")

# 確認
print("mersenne_orbit_mul → Waterfall:")
for m in range(2, 10):
    n = 2**m - 1
    for k in range(0, m):
        tk = syracuse_iter(k, n)
        mol = 2**k * tk + 2**k  # mersenne_orbit_mul の左辺
        rhs = 3**k * 2**m       # 右辺
        waterfall = 3**k * 2**(m-k) - 1
        print(f"  m={m}, k={k}: 2^k*T+2^k={mol}, 3^k*2^m={rhs}, T={tk}={waterfall}  "
              f"{'OK' if mol == rhs and tk == waterfall else 'FAIL'}")

print("\n" + "=" * 70)
print("8. 一般k帰納法に必要な追加補題")
print("=" * 70)

print("""
Waterfall公式 T^k(2^m-1) = 3^k * 2^{m-k} - 1 を直接帰納法で証明する場合:

必要な補題:
(a) 基礎: T^0(2^m-1) = 2^m - 1 = 3^0 * 2^m - 1  [trivial]
(b) 帰納ステップ: T(3^k * 2^j - 1) = 3^{k+1} * 2^{j-1} - 1  when j ≥ 2
    ← これは syracuse_two_pow_sub_one の一般化

    具体的に:
    n = 3^k * 2^j - 1, j ≥ 2
    n ≡ 3 (mod 4)  [∵ 4 | 3^k * 2^j]
    v2(3n+1) = 1   [∵ n ≡ 3 (mod 4)]
    T(n) = (3n+1)/2 = (3 * (3^k * 2^j - 1) + 1) / 2
         = (3^{k+1} * 2^j - 2) / 2
         = 3^{k+1} * 2^{j-1} - 1

既存の状態:
- syracuse_two_pow_sub_one: T(2^m - 1) = 3 * 2^{m-1} - 1  (k=0 のケース)
- mersenne_orbit_mul: 間接的にWaterfall公式を含むが、直接的形ではない

追加で形式化すべきもの:
1. waterfall_step: T(a * 2^j - 1) = (3a) * 2^{j-1} - 1  when j ≥ 2, a odd
   (より一般的な形)
2. waterfall_induction: T^k(2^m - 1) = 3^k * 2^{m-k} - 1  (k ≤ m-1)
3. mersenne_consecutive_ascents: consecutiveAscents (2^m-1) (m-1)
   (2^m-1 の m-1 回連続上昇)
""")

print("\n" + "=" * 70)
print("9. waterfall_step の一般化: T(a * 2^j - 1) when a odd, j ≥ 2")
print("=" * 70)

# a が奇数, j ≥ 2 のとき T(a * 2^j - 1) = 3a * 2^{j-1} - 1
for a in [1, 3, 5, 7, 9, 11, 13, 27, 81]:
    for j in [2, 3, 4, 5]:
        n = a * 2**j - 1
        tn = syracuse(n)
        expected = 3 * a * 2**(j-1) - 1
        mod4 = n % 4
        v2_val = v2(3*n + 1)
        status = "OK" if tn == expected else "FAIL"
        print(f"  a={a:3d}, j={j}: n={n:6d}, mod4={mod4}, v2={v2_val}, "
              f"T(n)={tn:6d}, 3a*2^{{j-1}}-1={expected:6d}  [{status}]")

print("\n" + "=" * 70)
print("10. 形式化戦略の比較")
print("=" * 70)

print("""
戦略1: 直接帰納法 (Waterfall公式を直接証明)
  - 新補題 waterfall_step: T(a*2^j-1) = 3a*2^{j-1}-1
  - 帰納法: a_k = 3^k (奇数), j_k = m-k (≥2)
  - メリット: シンプル、追加依存なし
  - デメリット: consecutiveAscents との接続が別途必要

戦略2: mersenne_orbit_mul からの導出
  - 既存の mersenne_orbit_mul を使って変形
  - T^k(2^m-1) = (3^k * 2^m - 2^k) / 2^k = 3^k * 2^{m-k} - 1
  - メリット: 既存結果を最大活用、除算は 2^k で割るだけ
  - デメリット: 自然数の除算と引き算の扱い

戦略3: consecutiveAscents + syracuse_iter_mul_formula
  - まず mersenne_consecutive_ascents を証明
  - 次に syracuse_iter_mul_formula を適用
  - 2^k * T^k = 3^k * (2^m-1) + (3^k - 2^k) = 3^k * 2^m - 2^k
  - T^k = 3^k * 2^{m-k} - 1
  - メリット: 既存のフレームワーク活用、接続が自然
  - デメリット: consecutiveAscents の証明が先に必要

推奨: 戦略2 (mersenne_orbit_mul からの導出)
  既に形式証明済みの結果から直接導けるため最も安全。
  接続は後から行える。
""")

print("\n" + "=" * 70)
print("11. consecutiveAscents (2^m-1) (m-1) の証明戦略")
print("=" * 70)

print("""
方針: 2^m - 1 ≡ 2^{k+1} - 1 (mod 2^{k+1}) を示す

2^m - 1 = (2^{k+1}) * (2^{m-k-1} - 1) + 2^{k+1} - 1  ... ではない
2^m - 1 mod 2^{k+1}:
  2^m = 2^{k+1} * 2^{m-k-1}  (when k+1 ≤ m)
  2^m ≡ 0 (mod 2^{k+1})
  2^m - 1 ≡ -1 ≡ 2^{k+1} - 1 (mod 2^{k+1})

これは k+1 ≤ m のとき常に成立！

k=1,2,3,4 は Hensel.lean で個別証明済み。
一般 k は上の議論から明らか: 2^{k+1} | 2^m (since k+1 ≤ m)
⟹ 2^m - 1 ≡ -1 (mod 2^{k+1})
⟹ 2^m - 1 ≡ 2^{k+1} - 1 (mod 2^{k+1})
""")

# 数値確認
print("数値確認: 2^m - 1 mod 2^{k+1} = 2^{k+1} - 1")
for m in range(2, 10):
    for k in range(1, m):
        n = 2**m - 1
        mod = n % (2**(k+1))
        expected = 2**(k+1) - 1
        print(f"  m={m}, k={k}: (2^{m}-1) mod 2^{k+1} = {mod}, 2^{k+1}-1 = {expected}  "
              f"{'OK' if mod == expected else 'FAIL'}")

print("\n" + "=" * 70)
print("12. 一般 hensel_attrition の形式化ギャップ分析")
print("=" * 70)

print("""
既存 (Hensel.lean): k=1,2,3,4 の個別証明
  - 各 k で omega タクティクによる modular arithmetic

一般k の証明に必要なもの:
  帰納法で k回連続上昇 ⟺ n ≡ 2^{k+1}-1 (mod 2^{k+1})

→方向 (hensel_attrition_general):
  consecutiveAscents n k → n ≡ 2^{k+1}-1 (mod 2^{k+1})

  帰納法:
  - k=0: 自明 (0回連続上昇は常に真、条件なし)...
    待て、k=1 が最小の非自明ケース
  - k=1: single_ascent_mod4 (既存)
  - k→k+1: consecutiveAscents n (k+1)
    → consecutiveAscents n k (by mono) → n ≡ 2^{k+1}-1 (mod 2^{k+1}) (帰納仮説)
    → さらに Syracuse 関数の行動から 2^{k+2} | ... を示す

  問題: k→k+1 のステップで、syracuse^k(n) ≡ 3 (mod 4) を使って
  n mod 2^{k+2} を決定する必要がある。

  核心的困難: mod 2^{k+1} の情報から mod 2^{k+2} への持ち上げ (Hensel lifting!)

  T^k(n) の値が n mod 2^{k+2} に依存する
  → T^k(n) > T^{k-1}(n) かどうかが n mod 2^{k+2} を決定する

←方向 (mod_implies_ascents):
  n ≡ 2^{k+1}-1 (mod 2^{k+1}) → consecutiveAscents n k

  mersenne_orbit_mul + syracuse_iter_mul_formula の利用可能

  n = 2^{k+1} * q + 2^{k+1} - 1 の形
  Waterfall公式的に各ステップで mod 4 ≡ 3 を示す

このギャップは大きい。個別の k=1,...,4 は omega で処理できたが、
一般 k では帰納法の構造を明示的に扱う必要がある。
""")

print("\n" + "=" * 70)
print("13. waterfall_step 形式化のための分析")
print("=" * 70)

print("""
補題 waterfall_step:
  a が奇数, j ≥ 2 のとき T(a * 2^j - 1) = 3a * 2^{j-1} - 1

証明スケッチ:
  n = a * 2^j - 1
  1. n ≡ 3 (mod 4):
     a * 2^j は 4 の倍数 (j ≥ 2)
     n = 4k - 1 for some k
     n mod 4 = 3

  2. v2(3n+1) = 1:
     n ≡ 3 (mod 4) より (既存の v2_three_mul_add_one_of_mod4_eq3)

  3. T(n) = (3n+1)/2:
     = (3(a * 2^j - 1) + 1) / 2
     = (3a * 2^j - 3 + 1) / 2
     = (3a * 2^j - 2) / 2
     = 3a * 2^{j-1} - 1

Lean での形式化:
  syracuse_mod4_eq3 を使って syracuse n = (3n+1)/2
  あとは自然数の算術: (3a * 2^j - 2) / 2 = 3a * 2^{j-1} - 1

  j ≥ 2 なので a * 2^j ≥ 4, n ≥ 3
  3a * 2^j ≥ 12 > 2 なので引き算は安全
  2^j = 2 * 2^{j-1} より 3a * 2^j - 2 = 2 * (3a * 2^{j-1} - 1)
""")

# 代数的確認
print("代数的確認: 3(a*2^j - 1) + 1 = 3a*2^j - 2 = 2*(3a*2^{j-1} - 1)")
for a in [1, 3, 9, 27]:
    for j in [2, 3, 4]:
        n = a * 2**j - 1
        val1 = 3 * n + 1
        val2 = 3 * a * 2**j - 2
        val3 = 2 * (3 * a * 2**(j-1) - 1)
        print(f"  a={a}, j={j}: 3n+1={val1}, 3a*2^j-2={val2}, 2*(3a*2^{{j-1}}-1)={val3}  "
              f"{'OK' if val1 == val2 == val3 else 'FAIL'}")

print("\n" + "=" * 70)
print("まとめ: 形式化の優先順位")
print("=" * 70)

print("""
優先度1 (容易、高価値):
  waterfall_formula: T^k(2^m-1) = 3^k * 2^{m-k} - 1
  → mersenne_orbit_mul から直接導出可能
  → 形式: mersenne_orbit_mul の等式 2^k*(T^k+1) = 3^k*2^m を
    T^k = 3^k * 2^{m-k} - 1 に変形するだけ

優先度2 (中程度):
  waterfall_step: T(a*2^j - 1) = 3a*2^{j-1} - 1 (a odd, j ≥ 2)
  → syracuse_two_pow_sub_one の一般化
  → 直接帰納法で waterfall_formula を証明するための鍵

優先度3 (困難だが重要):
  mersenne_consecutive_ascents: consecutiveAscents (2^m-1) (m-1)
  → Waterfall公式から各ステップが上昇であることを示す
  → mod 4 条件の連鎖

優先度4 (非常に困難):
  一般 hensel_attrition: k回連続上昇 ⟺ n ≡ 2^{k+1}-1 (mod 2^{k+1})
  → 帰納法の k→k+1 ステップが Hensel lifting を必要とする
""")
