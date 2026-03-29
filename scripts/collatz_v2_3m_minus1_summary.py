"""
v2(3^m - 1) のLTE公式: 最終まとめ

主結果:
  (1) m奇数 (m>=1): v2(3^m - 1) = 1
  (2) m偶数 (m>=2): v2(3^m - 1) = 2 + v2(m)

Lean形式化の2つのルート:
  Route A: Mathlibの padicValNat.pow_two_sub_one を使う
  Route B: v2の定義から直接証明（因数分解 + 強帰納法）
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
print("最終まとめ: v2(3^m - 1) の LTE公式")
print("=" * 70)
print()

# 検証表: 最初の30値
print("完全検証表 (m=1..30):")
print(f"{'m':>3} {'parity':>6} {'v2(3^m-1)':>10} {'formula':>8} {'check':>6}")
print("-" * 40)
for m in range(1, 31):
    actual = v2(3**m - 1)
    if m % 2 == 1:
        formula = 1
        formula_str = "1"
    else:
        formula = 2 + v2(m)
        formula_str = f"2+v2({m})={formula}"
    parity = "odd" if m % 2 == 1 else "even"
    check = "OK" if actual == formula else "FAIL"
    print(f"{m:>3} {parity:>6} {actual:>10} {formula_str:>8} {check:>6}")

print()
print("=" * 70)
print("発見1: v2(3^k + 1) の閉形式（副産物）")
print("=" * 70)
print()
print("  k奇数 (k>=1): v2(3^k + 1) = 2")
print("  k偶数 (k>=2): v2(3^k + 1) = 1")
print()
print("  証明: 3^2 ≡ 1 (mod 8) なので")
print("    k奇数: 3^k ≡ 3 (mod 8) → 3^k+1 ≡ 4 (mod 8) → v2 = 2 (exactly)")
print("    k偶数: 3^k ≡ 1 (mod 8) → 3^k+1 ≡ 2 (mod 8) → v2 = 1 (exactly)")

print()
print("=" * 70)
print("発見2: v2(3^k - 2^k) = 0 (全ての k>=1)")
print("=" * 70)
print()
print("  ascentConst(k) = 3^k - 2^k は常に奇数!")
print("  証明: 3^k - 2^k mod 2:")
print("    k奇数: 3^k ≡ 1 (mod 2), 2^k ≡ 0 (mod 2) → 差 ≡ 1 (mod 2)")
print("    k偶数: 3^k ≡ 1 (mod 2), 2^k ≡ 0 (mod 2) → 差 ≡ 1 (mod 2)")
print("  → 全ての k>=1 で v2(3^k - 2^k) = 0")
print()
print("  これは ascentConst(k) が常に奇数であることを意味する。")
print("  Lean補題: ascentConst_odd : Odd (ascentConst k) (k>=1)")

# 検証
all_odd = True
for k in range(1, 100):
    if (3**k - 2**k) % 2 != 1:
        all_odd = False
        print(f"  FAIL at k={k}")
if all_odd:
    print("  検証OK: k=1..99 で全て奇数")

print()
print("=" * 70)
print("発見3: Syracuse軌道への応用")
print("=" * 70)
print()
print("n = (3^m - 1)/2 の形の奇数に対する Syracuse 値:")
print()

for m in [1, 3, 5, 7, 9, 11]:
    n = (3**m - 1) // 2
    three_n_plus_1 = 3*n + 1  # = (3^(m+1)-1)/2
    v = v2(three_n_plus_1)
    T_n = three_n_plus_1 // (2**v)

    # v2(3n+1) = v2((3^(m+1)-1)/2) = v2(3^(m+1)-1) - 1
    m_next = m + 1  # m+1 は偶数
    v2_formula = (2 + v2(m_next)) - 1  # = 1 + v2(m+1)

    print(f"  m={m}: n=(3^{m}-1)/2 = {n}")
    print(f"    3n+1 = (3^{m+1}-1)/2 = {three_n_plus_1}")
    print(f"    v2(3n+1) = v2(3^{m+1}-1) - 1 = {2+v2(m_next)} - 1 = {v2_formula} [actual: {v}]")
    print(f"    T(n) = {T_n}")
    print()

print("=" * 70)
print("Lean形式化ルートの比較")
print("=" * 70)
print()
print("Route A: Mathlibの pow_two_sub_one を使う")
print("  利点: 偶数ケースが1行で済む")
print("  欠点: v2 と padicValNat の関係証明が必要")
print("  必要な橋渡し補題: v2 n = padicValNat 2 n (n > 0)")
print()
print("Route B: 因数分解 + 帰納法で直接証明")
print("  利点: 自己完結、追加の依存なし")
print("  欠点: v2_mul の証明が必要（やや長い）")
print("  必要な補題:")
print("    (1) v2_mul: v2(a*b) = v2(a) + v2(b)")
print("    (2) three_pow_mod4: 3^m mod 4 (パリティ依存)")
print("    (3) three_pow_mod8: 3^m mod 8 (パリティ依存)")
print("    (4) v2_three_pow_plus_one: v2(3^k+1) (パリティ依存)")
print()
print("推奨: Route A が最短。v2 = padicValNat 2 の等価性さえ示せば")
print("      Mathlibの結果を直接活用できる。")

print()
print("=" * 70)
print("コラッツ予想全体への影響")
print("=" * 70)
print()
print("1. 連続上昇回数の制御:")
print("   連続上昇 k 回の条件は各ステップで v2(3T^i(n)+1) = 1")
print("   → T^i(n) ≡ 3 (mod 4)")
print("   v2(3^m-1) の公式は、特殊な初期値族の軌道を完全に追跡可能にする")
print()
print("2. ascentConst(k) = 3^k - 2^k が常に奇数:")
print("   連続上昇公式 2^k * T^k(n) = 3^k * n + ascentConst(k) において")
print("   右辺の v2 は min(v2(3^k * n), v2(ascentConst(k))) に依存")
print("   ascentConst(k) が奇数なので v2(右辺) = 0 (n が奇数のとき)")
print("   → T^k(n) = (3^k * n + ascentConst(k)) / 2^k は整数")
print()
print("3. Syracuse 固定点族の構造:")
print("   T(n)=1 ⟺ 3n+1 = 2^m の解は n = (2^m-1)/3 (m偶数)")
print("   より一般に T^k(n) = n の周期軌道解析に v2(3^m-1) が登場")
