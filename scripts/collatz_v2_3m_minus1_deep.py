"""
v2(3^m - 1) のLTE公式: 深い分析

1. 証明の戦略（Lean形式化を見据えて）
2. Syracuse軌道でv2(3^m-1)が登場する具体的場面
3. ascentConstとの関連の詳細
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

print("=" * 70)
print("1. m奇数ケースの直接証明（LTE不要）")
print("=" * 70)
print()
print("証明: m奇数のとき v2(3^m - 1) = 1")
print()
print("  3 ≡ -1 (mod 4)")
print("  m奇数 → 3^m ≡ (-1)^m = -1 ≡ 3 (mod 4)")
print("  → 3^m - 1 ≡ 2 (mod 4)")
print("  → 2 | (3^m-1) かつ 4 ∤ (3^m-1)")
print("  → v2(3^m-1) = 1")
print()
print("Lean戦略: omega で直接証明可能（mod 4 の算術）")
print("  必要な補題: 3^m mod 4 = 3 when m is odd")
print("  これは Nat.pow_mod と帰納法で証明可能")

print()
print("数値確認:")
for m in range(1, 20, 2):
    val = 3**m - 1
    print(f"  m={m}: 3^m mod 4 = {(3**m) % 4}, 3^m-1 mod 4 = {val % 4}, v2 = {v2(val)}")

print()
print("=" * 70)
print("2. m偶数ケースの証明戦略")
print("=" * 70)
print()
print("方法A: LTE補題を使う（標準的だが、Mathlibへの依存が必要）")
print("  LTE (p=2): v2(x^n - y^n) = v2(x-y) + v2(x+y) + v2(n) - 1")
print("  x=3, y=1, n=m (偶数)")
print("  → v2(3^m - 1) = v2(2) + v2(4) + v2(m) - 1 = 1+2+v2(m)-1 = 2+v2(m)")
print()
print("方法B: 直接帰納法（LTE不使用、自己完結型）")
print("  基本ケース: m=2 → 3^2-1=8, v2(8)=3 = 2+v2(2) = 2+1")
print("  帰納ステップ: m偶数→m+2偶数")
print("    3^(m+2) - 1 = 9 * 3^m - 1 = 9*(3^m-1) + 8")
print("    v2(9*(3^m-1) + 8) = ???  ← これは直接的でない")
print()
print("方法C: m=2k と書いて帰納法")
print("  3^(2k) - 1 = (3^k - 1)(3^k + 1)")
print("  v2(3^(2k)-1) = v2(3^k-1) + v2(3^k+1)")
print()
print("  ケースC.1: k奇数")
print("    v2(3^k-1) = 1 (m奇数の結果)")
print("    3^k+1: k奇数→ 3^k ≡ 3 mod 4 → 3^k+1 ≡ 0 mod 4 → v2(3^k+1) >= 2")
print("    さらに、3^k+1 = 3^k+1")
print("    v2(3^k+1) を調べる:")

print()
for k in range(1, 20, 2):
    val_minus = 3**k - 1
    val_plus = 3**k + 1
    print(f"    k={k}: v2(3^k-1)={v2(val_minus)}, v2(3^k+1)={v2(val_plus)}, "
          f"sum={v2(val_minus)+v2(val_plus)}, v2(3^(2k)-1)={v2(3**(2*k)-1)}")

print()
print("  ケースC.2: k偶数 (k>=2)")
print("    帰納仮説: v2(3^k-1) = 2+v2(k)")
print("    3^k+1 = ?")

for k in range(2, 20, 2):
    val_minus = 3**k - 1
    val_plus = 3**k + 1
    print(f"    k={k}: v2(3^k-1)={v2(val_minus)}, v2(3^k+1)={v2(val_plus)}, "
          f"sum={v2(val_minus)+v2(val_plus)}, v2(3^(2k)-1)={v2(3**(2*k)-1)}")

print()
print("方法D: 完全帰納法を直接 v2 の定義に基づいて")
print("  m偶数→ m=2k")
print("  v2(3^(2k)-1) = v2((3^k-1)(3^k+1))")
print()
print("  v2(ab) の分解: v2(ab) = v2(a) + v2(b) が必要")
print("  これは Lean で示す必要がある基本補題")

print()
print("=" * 70)
print("3. v2の乗法性 v2(a*b) = v2(a) + v2(b)")
print("=" * 70)
print()
print("検証:")
import random
random.seed(42)
for _ in range(20):
    a = random.randint(1, 10000)
    b = random.randint(1, 10000)
    print(f"  v2({a}*{b}) = v2({a*b}) = {v2(a*b)}, v2({a})+v2({b}) = {v2(a)}+{v2(b)} = {v2(a)+v2(b)}, "
          f"{'OK' if v2(a*b)==v2(a)+v2(b) else 'FAIL'}")

print()
print("=" * 70)
print("4. v2(3^k + 1) の公式")
print("=" * 70)
print()
print("k奇数: 3^k ≡ 3 (mod 8)?")
for k in [1, 3, 5, 7, 9, 11]:
    print(f"  k={k}: 3^k mod 8 = {pow(3, k, 8)}, v2(3^k+1) = {v2(3**k + 1)}")

print()
print("k偶数: 3^k ≡ 1 (mod 8)?")
for k in [2, 4, 6, 8, 10, 12]:
    print(f"  k={k}: 3^k mod 8 = {pow(3, k, 8)}, v2(3^k+1) = {v2(3**k + 1)}")

print()
print("パターン:")
print("  k奇数: 3^k ≡ 3 (mod 8) → 3^k+1 ≡ 4 (mod 8) → v2(3^k+1) = 2")
print("  k偶数: 3^k ≡ 1 (mod 8) → 3^k+1 ≡ 2 (mod 8) → v2(3^k+1) = 1")

print()
print("検証:")
all_ok = True
for k in range(1, 50):
    val = 3**k + 1
    v = v2(val)
    if k % 2 == 1:
        expected = 2
    else:
        expected = 1
    ok = (v == expected)
    if not ok:
        all_ok = False
        print(f"  FAIL: k={k}, v2(3^k+1)={v}, expected={expected}")
if all_ok:
    print("  全て一致! v2(3^k+1) = 2 (k奇数), 1 (k偶数)")

print()
print("=" * 70)
print("5. 方法Cの完全な証明フロー")
print("=" * 70)
print()
print("主定理: v2(3^m - 1) = (1 if m odd) or (2 + v2(m) if m even, m>=2)")
print()
print("補助定理1: v2(3^k + 1) = 2 (k奇数), 1 (k偶数)")
print("  証明: 3 mod 8 = 3, 3^2 mod 8 = 1")
print("    k奇数: 3^k ≡ 3 (mod 8) → 3^k+1 ≡ 4 (mod 8), 4 ∤ 8 → v2 = 2")
print("    k偶数: 3^k ≡ 1 (mod 8) → 3^k+1 ≡ 2 (mod 8), 2 ∤ 4 → v2 = 1")
print()

# v2(3^k+1) の正確な値
print("v2(3^k+1) のより正確な値:")
for k in range(1, 30):
    v = v2(3**k + 1)
    print(f"  k={k}: v2(3^k+1) = {v}", end="")
    if k % 2 == 1:
        print(f"  [k odd → exactly 2]")
    else:
        print(f"  [k even → exactly 1]")

print()
print("=" * 70)
print("6. 証明: m偶数のとき v2(3^m-1) = 2+v2(m)")
print("=" * 70)
print()
print("m=2k とおく。強帰納法で k について証明。")
print()
print("3^(2k)-1 = (3^k-1)(3^k+1)")
print("v2(3^(2k)-1) = v2(3^k-1) + v2(3^k+1)")
print()
print("Case A: k奇数")
print("  v2(3^k-1) = 1 (奇数ケースの定理)")
print("  v2(3^k+1) = 2 (補助定理1)")
print("  v2(3^(2k)-1) = 1+2 = 3")
print("  一方、2+v2(2k) = 2+v2(2k)")
print("  k奇数→ v2(2k) = v2(2)+v2(k) = 1+0 = 1")
print("  → 2+1 = 3 ✓")
print()
print("Case B: k偶数 (k>=2)")
print("  v2(3^k-1) = 2+v2(k) (帰納仮説! kは偶数でk<m=2k)")
print("  v2(3^k+1) = 1 (補助定理1, k偶数)")
print("  v2(3^(2k)-1) = (2+v2(k)) + 1 = 3+v2(k)")
print("  一方、2+v2(2k) = 2+v2(2)+v2(k) = 2+1+v2(k) = 3+v2(k) ✓")
print()
print("基底ケース: m=2 (k=1)")
print(f"  v2(3^2-1) = v2(8) = {v2(8)}, 2+v2(2) = 2+{v2(2)} = 3 ✓")

print()
print("=" * 70)
print("7. Lean形式化のための補題リスト")
print("=" * 70)
print()
print("必要な新補題:")
print("  (a) v2_mul: v2(a*b) = v2(a) + v2(b)  [a>0, b>0]")
print("  (b) pow_mod_eight_odd: 3^m % 8 = 3 (m odd)")
print("  (c) pow_mod_eight_even: 3^m % 8 = 1 (m even)")
print("  (d) v2_three_pow_plus_one_odd: v2(3^k+1) = 2 (k odd)")
print("  (e) v2_three_pow_plus_one_even: v2(3^k+1) = 1 (k even, k>=1)")
print("  (f) v2_three_pow_sub_one_odd: v2(3^m-1) = 1 (m odd, m>=1)")
print("  (g) v2_three_pow_sub_one_even: v2(3^m-1) = 2+v2(m) (m even, m>=2)")
print()
print("既存の補題:")
print("  - v2_zero, v2_odd, v2_even, v2_two_mul, v2_pow_two")
print("  - pow_v2_dvd, pow_v2_le")
print()
print("(a) v2_mul が最も重要な新補題。")
print("    Mathlibに multiplicity_mul があれば使える可能性あり。")
print("    ない場合は帰納法で直接証明。")

print()
print("=" * 70)
print("8. コラッツへの応用: v2(3^m-1) の使い方")
print("=" * 70)
print()

print("応用1: 連続上昇 k 回後の Syracuse 値の 2-adic 評価")
print("  連続上昇 k 回 → 2^k * T^k(n) = 3^k*n + (3^k-2^k)")
print("  すなわち T^k(n) = (3^k*n + 3^k - 2^k) / 2^k")
print("  停止のための条件: T^k(n) < n")
print("  → 3^k*n + 3^k - 2^k < n * 2^k")
print("  → n(3^k - 2^k) < 2^k - 3^k  (これは 3^k > 2^k なので成立しない)")
print()
print("応用2: n = (3^m-1)/2 のとき (レプユニット数の一般化)")
n_vals = [(3**m - 1) // 2 for m in range(1, 12) if (3**m - 1) % 2 == 0]
print(f"  n 列: {n_vals}")
print()
for m in range(1, 10):
    n = (3**m - 1) // 2
    if n % 2 == 1 and n >= 1:
        sn = (3*n+1) // (2**v2(3*n+1))
        print(f"  m={m}: n={n}, 3n+1={(3*n+1)}, v2(3n+1)={v2(3*n+1)}, T(n)={sn}")
        # 3n+1 = 3*(3^m-1)/2 + 1 = (3^(m+1)-1)/2
        three_n_plus_1 = 3*n+1
        formula_val = (3**(m+1) - 1) // 2
        print(f"         3n+1 = (3^{m+1}-1)/2 = {formula_val} [check: {three_n_plus_1 == formula_val}]")
        # v2(3n+1) = v2((3^(m+1)-1)/2) = v2(3^(m+1)-1) - 1
        v_total = v2(3**(m+1) - 1)
        print(f"         v2(3^{m+1}-1) = {v_total}, v2(3n+1) = v2(3^{m+1}-1)-1 = {v_total-1}")
