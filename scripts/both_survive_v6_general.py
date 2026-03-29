"""
探索172 v6: 一般的な残基での排他性検証と形式化設計

確認済みの核心定理:
  T(r) = (3r+1)/2 (v2=1, つまり r≡3 mod 4 のとき)
  T の連続 j 回適用で r → r+2^k の差分:
    Δ_j = 3^j * 2^{k-j}  (全ステップで v2=1 の場合)
  
  j = k-1 のとき Δ_{k-1} = 3^{k-1} * 2, v2(Δ_{k-1}) = 1
  Δ_{k-1} mod 4 = 2 → mod 4 で差が2 → 一方が1, 他方が3
  → 排他性!

一般の残基（全ステップ v2=1 でない場合）はどうか？
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

# 核心定理の精密化と一般検証
print("=" * 70)
print("定理: 連続上昇パスでの差分 Δ_j = 3^j * 2^{k-j}")
print("=" * 70)

# この定理の証明:
# T(n) = (3n+1)/2 for n ≡ 3 (mod 4)
# T(n + 2^k) = (3(n+2^k)+1)/2 = (3n+1+3*2^k)/2 = T(n) + 3*2^{k-1}
# Δ_1 = 3*2^{k-1} = 3^1 * 2^{k-1}
#
# 帰納法: Δ_j = 3^j * 2^{k-j} と仮定
# T^j(n+2^k) - T^j(n) = Δ_j
# T^{j+1}(n+2^k) - T^{j+1}(n) = T(T^j(n) + Δ_j) - T(T^j(n))
# = (3*(T^j(n)+Δ_j)+1)/2 - (3*T^j(n)+1)/2
# = 3*Δ_j/2 = 3 * 3^j * 2^{k-j} / 2 = 3^{j+1} * 2^{k-j-1}
# QED!

print("\n代数的帰納法証明:")
print("  Δ_1 = 3*2^{k-1} = 3^1 * 2^{k-1}")
print("  帰納ステップ: Δ_{j+1} = 3*Δ_j/2 = 3^{j+1} * 2^{k-(j+1)}")
print("  これは T が (3n+1)/2 の形の場合にのみ成立")
print("  つまり全ステップで v2 = 1 (≡ 3 mod 4) の場合")

# v2 = 1 の条件: T^j(r) ≡ 3 (mod 4) for all j < k-1
# これは r ≡ 2^k - 1 (mod 2^k) に限られるか？
# Hensel attrition から: k-1 回連続上昇 ⟺ r ≡ 2^k - 1 (mod 2^k)

print()
print("=" * 70)
print("連続上昇条件と末尾ビットパターン")
print("=" * 70)

# r ≡ 2^k - 1 (mod 2^k) = 111...1 (kビット) は唯一の k-1 連続上昇パターン
# しかし mod 2^{k+1} では 2^k - 1 と 2^{k+1} - 1 の2つがある
# 2^k - 1 の末尾kビット: 0111...1
# 2^{k+1} - 1 の末尾(k+1)ビット: 1111...1
# つまり r = 2^k - 1: k-1回連続上昇後に mod 4 ≡ 1 (下降)
#        r = 2^{k+1} - 1: k回連続上昇

# 一般の非排除残基でも同様の排他性があるか？
# 非排除の定義を考え直す。

# 探索指示の「非排除残基rに対しr,r+2^kが同時に非排除にならない」は
# 「k回連続上昇」の条件ではなく、停止時間の非決定性を指している。

# しかし、以下の定理は確実に成立する:
# 「r ≡ 2^{k+1}-1 (mod 2^{k+1}) のリフトペアでは、
#   k-1ステップ後に一方が mod 4 ≡ 1, 他方が mod 4 ≡ 3」

# より一般的に:
# 2つの奇数 a, b が a - b = Δ, v2(Δ) = 1 を満たすなら
# a mod 4 != b mod 4 (一方が1, 他方が3)

print("\n一般的な排他性定理:")
print("  v2(Δ_{k-1}) = 1 ⟹ T^{k-1}(r) mod 4 ≠ T^{k-1}(r+2^k) mod 4")
print("  これは Δ_{k-1} mod 4 = 2 から自明")
print("  (2つの奇数の差が 4m+2 なら mod 4 が異なる)")

# Lean形式化可能な命題のリスト
print()
print("=" * 70)
print("Lean形式化可能な命題一覧")
print("=" * 70)

print("""
1. T_diff_eq (基本差分):
   r ≡ 3 (mod 4) → (3*(r+2^k)+1)/2 - (3*r+1)/2 = 3*2^{k-1}

2. T_diff_mod2k (mod 2^k差分):
   3*2^{k-1} mod 2^k = 2^{k-1}  (k >= 1)
   つまり T(r+2^k) ≡ T(r) + 2^{k-1} (mod 2^k)

3. T_iter_diff (反復差分の帰納):
   全ステップで v2=1 のとき:
   T^j(r+2^k) - T^j(r) = 3^j * 2^{k-j}  (j ≤ k)

4. T_iter_diff_parity (k-1ステップ後のパリティ):
   T^{k-1}(r+2^k) - T^{k-1}(r) = 3^{k-1} * 2
   v2(3^{k-1} * 2) = 1
   → T^{k-1}(r+2^k) mod 4 ≠ T^{k-1}(r) mod 4

5. parity_exclusion (排他的排除):
   T^{k-1}(r+2^k) - T^{k-1}(r) ≡ 2 (mod 4)
   かつ両者が奇数
   → 一方は mod 4 ≡ 1 (下降確定)、他方は mod 4 ≡ 3 (上昇)
""")

# 数値検証: 定理4の一般残基での成否
print("=" * 70)
print("検証: 全ビット1パターン以外の残基での k-1 ステップ排他性")
print("=" * 70)

for k in range(3, 10):
    mod = 2**k
    # r ≡ 2^k - 1 (mod 2^k) 以外で v2=1 が k-1 回続く残基はあるか?
    continuous_ascent_residues = []
    for r in range(3, mod, 4):
        cur = r
        all_mod4_3 = True
        for j in range(k-1):
            if cur % 4 != 3:
                all_mod4_3 = False
                break
            cur = (3*cur + 1) // 2
        if all_mod4_3:
            continuous_ascent_residues.append(r)
    print(f"k={k}: k-1={k-1}回連続上昇: {continuous_ascent_residues} "
          f"(Hensel理論: {mod-1} のみのはず)")

# Hensel attrition定理との関連確認
print()
print("=" * 70)
print("Hensel Attrition確認: k-1回連続上昇 ⟺ r ≡ 2^k - 1 (mod 2^k)")
print("=" * 70)

for k in range(3, 12):
    mod = 2**k
    expected = mod - 1
    count = 0
    for r in range(3, mod, 4):
        cur = r
        ok = True
        for j in range(k-1):
            if cur % 4 != 3:
                ok = False
                break
            cur = (3*cur + 1) // 2
        if ok:
            count += 1
            if r != expected:
                print(f"  k={k}: UNEXPECTED r={r} (expected only {expected})")
    print(f"k={k:2d}: {count} residue(s) with k-1 continuous ascent (expected: 1, r=2^k-1={expected})")

# 結論: 排他性は連続上昇パス（末尾全1ビット）に限定される
# しかし、これは非排除の定義と直接は対応しない

# 探索の再方向付け: Lean形式化可能な確実な定理に集中
print()
print("=" * 70)
print("形式化すべき定理の最終選定")
print("=" * 70)

print("""
=== 確実に形式化可能な定理 ===

定理A: T_lift_diff
  ∀ r k : ℕ, r % 4 = 3 → k ≥ 1 →
  (3 * (r + 2^k) + 1) / 2 = (3 * r + 1) / 2 + 3 * 2^{k-1}

定理B: three_pow_two_pow_mod
  ∀ k : ℕ, k ≥ 1 → 3 * 2^{k-1} % 2^k = 2^{k-1}

定理C: T_lift_mod2k
  ∀ r k : ℕ, r % 4 = 3 → k ≥ 1 →
  (3 * (r + 2^k) + 1) / 2 % 2^k = ((3 * r + 1) / 2 + 2^{k-1}) % 2^k

定理D: iter_diff_formula (帰納法)
  連続上昇パスで T^j の差分が 3^j * 2^{k-j}
  
定理E: parity_split (最重要)
  ∀ a b : ℕ, a % 2 = 1 → b % 2 = 1 → (b - a) % 4 = 2 →
  (a % 4 = 1 ∧ b % 4 = 3) ∨ (a % 4 = 3 ∧ b % 4 = 1)

定理F: hensel_lift_exclusive
  ∀ k : ℕ, k ≥ 3 →
  let r := 2^k - 1
  let a := T^{k-1}(r)
  let b := T^{k-1}(r + 2^k)
  (a % 4 = 1 ∧ b % 4 = 3) ∨ (a % 4 = 3 ∧ b % 4 = 1)
""")

# 定理A,B,C の数値検証
print("定理A検証:")
for k in range(1, 10):
    for r in [3, 7, 11, 15, 23]:
        lhs = (3 * (r + 2**k) + 1) // 2
        rhs = (3 * r + 1) // 2 + 3 * 2**(k-1)
        assert lhs == rhs, f"FAIL: k={k}, r={r}"
print("  全てのテストケースでPASS")

print("\n定理B検証:")
for k in range(1, 20):
    val = (3 * 2**(k-1)) % (2**k)
    assert val == 2**(k-1), f"FAIL: k={k}"
print("  全てのテストケースでPASS")

print("\n定理E検証:")
for a in range(1, 100, 2):
    for b in range(1, 100, 2):
        diff = (b - a) % 4
        if diff == 2:
            ok = (a % 4 == 1 and b % 4 == 3) or (a % 4 == 3 and b % 4 == 1)
            assert ok, f"FAIL: a={a}, b={b}"
print("  全てのテストケースでPASS")

