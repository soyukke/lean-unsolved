"""
深掘り分析: 特に重要な発見の精査

Key findings to investigate:
1. n % 4 = 3 => T(n) % 3 = 2 (always!) -- L4
2. n % 8 = 7 => T(T(n)) % 3 = 2 (always!) -- 新発見
3. n % 16 = 11 => T(T(n)) % 3 = 1 (always!)
4. n % 16 = 9 => T(T(n)) % 3 = 2 (always!)
5. n % 16 = 15 => T(T(n)) % 3 = 2 (always!)
6. mod 9 分類: T(n)%9 = (n%3 -> {1,4,7}) の各行で v2%6 依存
"""

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

print("=" * 70)
print("DEEP ANALYSIS 1: n % 4 = 3 => T(n) % 3 = 2 の証明構造")
print("=" * 70)

# n % 4 = 3 => v2(3n+1) = 1 (既知: v2_three_mul_add_one_of_mod4_eq3)
# v2 = 1 は奇数 => syracuse_mod3_eq により T(n) % 3 = 2
# つまり証明: syracuse_mod3_eq + v2_three_mul_add_one_of_mod4_eq3

print("  Proof sketch:")
print("  1. v2_three_mul_add_one_of_mod4_eq3: n%4=3 => v2(3n+1)=1")
print("  2. 1 % 2 = 1 (odd)")
print("  3. syracuse_mod3_eq: v2 odd => T(n) % 3 = 2")
print("  QED")

print()
print("=" * 70)
print("DEEP ANALYSIS 2: n % 8 = 7 => T(T(n)) % 3 = 2")
print("=" * 70)

# n % 8 = 7 の場合:
# Step 1: n % 4 = 3 => v2(3n+1) = 1, T(n) = (3n+1)/2
# Step 2: T(n) = (3n+1)/2, n%8=7 => T(n) % 4 = 3
#   (by syracuse_mod4_of_mod8_eq7: (3n+1)/2 % 4 = 3)
# Step 3: T(n) % 4 = 3 => v2(3*T(n)+1) = 1
# Step 4: v2 = 1 odd => T(T(n)) % 3 = 2

print("  Proof sketch:")
print("  1. n%8=7 => n%4=3 => v2(3n+1)=1 => T(n)=(3n+1)/2")
print("  2. n%8=7 => (3n+1)/2 % 4 = 3 (syracuse_mod4_of_mod8_eq7)")
print("  3. T(n) % 4 = 3 => v2(3*T(n)+1) = 1 (v2_three_mul_add_one_of_mod4_eq3)")
print("  4. v2 = 1 is odd => T(T(n)) % 3 = 2 (syracuse_mod3_eq)")
print("  QED")

# 検証
all_ok = True
for n in range(7, 100000, 8):
    tn = syracuse(n)
    ttn = syracuse(tn)
    if ttn % 3 != 2:
        print(f"  FAIL: n={n}")
        all_ok = False
        break
if all_ok:
    print(f"  [VERIFIED] for all n≡7 (mod 8), n < 100000")

print()
print("=" * 70)
print("DEEP ANALYSIS 3: n % 16 = 11 => T(T(n)) % 3 = 1")
print("=" * 70)

# n % 16 = 11:
# n % 8 = 3 => n%4=3 => v2(3n+1)=1 => T(n) = (3n+1)/2
# n % 8 = 3 => T(n) % 4 = 1 (syracuse_mod4_eq1_of_mod8_eq3)
# T(n) % 4 = 1 => v2(3*T(n)+1) >= 2
# T(n) = (3n+1)/2 で n%16=11 のとき、T(n) の具体値は?
# n=16k+11 => 3n+1=48k+34, T(n)=(48k+34)/2=24k+17
# T(n) = 24k+17
# 3*T(n)+1 = 72k+52 = 4(18k+13)
# v2(3*T(n)+1) = 2 + v2(18k+13)
# 18k+13: k=0=>13(odd), k=1=>31(odd), k=2=>49(odd)...
# 18k+13 is always odd! (18k is even, +13 odd => odd)
# So v2(3*T(n)+1) = 2 (even)
# => T(T(n)) % 3 = 1

print("  Proof sketch:")
print("  1. n%16=11 => n%8=3 => n%4=3 => v2(3n+1)=1, T(n)=(3n+1)/2")
print("  2. n=16k+11 => T(n)=(48k+34)/2=24k+17")
print("  3. 3*T(n)+1=72k+52=4(18k+13)")
print("  4. 18k+13 is always odd (18k even + 13 odd)")
print("  5. v2(3*T(n)+1) = 2 (even)")
print("  6. syracuse_mod3_eq: v2 even => T(T(n)) % 3 = 1")
print("  QED")

# 検証
all_ok = True
for n in range(11, 100000, 16):
    tn = syracuse(n)
    ttn = syracuse(tn)
    if ttn % 3 != 1:
        print(f"  FAIL: n={n}, T(n)={tn}, T(T(n))={ttn}, T(T(n))%3={ttn%3}")
        all_ok = False
        break
if all_ok:
    print(f"  [VERIFIED] for all n≡11 (mod 16), n < 100000")

print()
print("=" * 70)
print("DEEP ANALYSIS 4: mod 9 完全分類定理の構造")
print("=" * 70)

# T(n) mod 9 は (n mod 3, v2(3n+1) mod 6) で完全決定
# 理由: T(n) * 2^v2 = 3n+1
# (3n+1) mod 9 は n mod 3 のみ依存:
#   n ≡ 0 (mod 3) => 3n+1 ≡ 1 (mod 9)
#   n ≡ 1 (mod 3) => 3n+1 ≡ 4 (mod 9)
#   n ≡ 2 (mod 3) => 3n+1 ≡ 7 (mod 9)
# 2^v mod 9 は v mod 6 のみ依存 (周期6)
# T(n) ≡ (3n+1) * (2^v)^{-1} (mod 9)

# ただし (3n+1) mod 9 は実は n mod 3 のみで決まる（n mod 9 ではない）
# 証明: 3n+1 mod 9 = (3*(n mod 3) + 1) mod 9 = (3r+1) mod 9 where r = n mod 3
# r=0: 1, r=1: 4, r=2: 7

# よって定理は:
# T(n) % 9 = f(n % 3, v2(3n+1) % 6)
# ここで f は 3x6 = 18 エントリの表

print("  Key insight: (3n+1) mod 9 depends only on n mod 3")
print("  (3n+1) mod 9:")
print("    n≡0 (mod 3): 1")
print("    n≡1 (mod 3): 4")
print("    n≡2 (mod 3): 7")
print()
print("  2^v mod 9 has period 6: [1, 2, 4, 8, 7, 5]")
print()

# 完全な lookup table
inv_table = {1:1, 2:5, 4:7, 5:2, 7:4, 8:8}
base_mod9 = {0: 1, 1: 4, 2: 7}  # (3n+1) mod 9 by n mod 3
pow2_mod9 = [1, 2, 4, 8, 7, 5]  # 2^v mod 9, period 6

print("  Complete T(n) % 9 = f(n%3, v2%6) table:")
print("  v2%6:  0  1  2  3  4  5")
for r3 in range(3):
    row = []
    for v6 in range(6):
        val = (base_mod9[r3] * inv_table[pow2_mod9[v6]]) % 9
        row.append(val)
    print(f"  n%3={r3}: {row}")

# 注意: T(n) % 9 が 0,3,6 にならないことの確認
print("\n  T(n) % 9 never equals 0, 3, or 6 (multiples of 3)")
print("  Because T(n) % 3 != 0 (syracuse_not_div_three)")

print()
print("=" * 70)
print("DEEP ANALYSIS 5: 上昇ステップでの mod 3 の確定的挙動")
print("=" * 70)

# 連続上昇の条件と mod 3 の関係
# 1回上昇: n%4=3 => T(n)%3=2  (確定)
# 2回上昇: n%8=7 => T(T(n))%3=2  (確定)
# 3回上昇: n%16=15 => T(T(T(n)))%3=?

# n%16=15 => T(T(T(n))) % 3
print("  Triple ascent (n%16=15):")
triple_mod3 = {}
for n in range(15, 100000, 16):
    t1 = syracuse(n)
    t2 = syracuse(t1)
    t3 = syracuse(t2)
    r = t3 % 3
    triple_mod3[r] = triple_mod3.get(r, 0) + 1

for r, c in sorted(triple_mod3.items()):
    print(f"    T^3(n) % 3 = {r}: {c} times")

# n%32=31 => 4回上昇
print("\n  Quadruple ascent (n%32=31):")
quad_mod3 = {}
for n in range(31, 100000, 32):
    t = n
    for _ in range(4):
        t = syracuse(t)
    r = t % 3
    quad_mod3[r] = quad_mod3.get(r, 0) + 1

for r, c in sorted(quad_mod3.items()):
    print(f"    T^4(n) % 3 = {r}: {c} times")

# 一般化: k回連続上昇 => T^k(n) % 3 = 2?
print("\n  Checking: k consecutive ascents => T^k(n) % 3 = 2")
for k in range(1, 8):
    mod_val = 2**(k+1)
    start = mod_val - 1  # n ≡ 2^{k+1}-1 (mod 2^{k+1})
    all_2 = True
    count = 0
    for n in range(start, 100000, mod_val):
        t = n
        ascending = True
        for _ in range(k):
            tn = syracuse(t)
            if tn <= t:
                ascending = False
                break
            t = tn
        if ascending:
            count += 1
            if t % 3 != 2:
                all_2 = False
                break
    print(f"    k={k}: n≡{start} (mod {mod_val}), {count} tested, all T^k%3=2: {all_2}")

print()
print("=" * 70)
print("DEEP ANALYSIS 6: T(n) ≡ 2 (mod 3) の頻度分析")
print("=" * 70)

# v2(3n+1) が奇数になる確率 -> T(n) ≡ 2 (mod 3) の頻度
# n%4=3 => v2=1(奇) 確定
# n%4=1 => v2≥2, v2の偶奇はn%2^{v2+1}に依存

# 奇数全体での T(n)%3=2 の密度
# n%4=3: 全体の1/2 -> 全てT(n)%3=2
# n%4=1: 全体の1/2
#   v2=2(even, T%3=1): 1/2 of n%4=1 -> 1/4 of odd
#   v2=3(odd, T%3=2): 1/4 of n%4=1 -> 1/8 of odd
#   v2=4(even, T%3=1): 1/8 of n%4=1 -> 1/16 of odd
#   ...
# P(T(n)%3=2 | n%4=1) = 1/4 + 1/16 + 1/64 + ... = (1/4)/(1-1/4) = 1/3
# P(T(n)%3=2) = 1/2 + (1/2)(1/3) = 1/2 + 1/6 = 2/3

print("  Density of T(n) ≡ 2 (mod 3) among odd n:")
print("    n%4=3 (half of odd): always T(n)%3=2")
print("    n%4=1 (half of odd):")
print("      v2=2 (even): T%3=1, density 1/2 of n%4=1")
print("      v2=3 (odd):  T%3=2, density 1/4 of n%4=1")
print("      v2=4 (even): T%3=1, density 1/8 of n%4=1")
print("      ...")
print("    P(T(n)%3=2 | n%4=1) = sum_{k=0}^inf (1/2)^{2k+2} = 1/3")
print("    P(T(n)%3=2) = 1/2 * 1 + 1/2 * 1/3 = 2/3")
print()

# 検証
count_2 = sum(1 for n in range(1, 100000, 2) if syracuse(n) % 3 == 2)
total = len(range(1, 100000, 2))
print(f"    Empirical: {count_2}/{total} = {count_2/total:.6f} (expected 2/3 = {2/3:.6f})")

print()
print("=" * 70)
print("DEEP ANALYSIS 7: Lean形式化可能な補題の優先順位")
print("=" * 70)

print("""
  Priority 1 (直接的な系、証明簡単):

  [L1] syracuse_ascent_mod3:
    n % 4 = 3 -> syracuse n % 3 = 2
    Proof: rw [syracuse_mod3_eq]; rw [v2_three_mul_add_one_of_mod4_eq3]; simp

  [L2] syracuse_mod3_eq_two_iff:
    n % 2 = 1 -> (syracuse n % 3 = 2 <-> v2(3n+1) % 2 = 1)
    Proof: rw [syracuse_mod3_eq]; split_ifs <;> omega

  [L3] syracuse_mod3_eq_one_iff:
    n % 2 = 1 -> (syracuse n % 3 = 1 <-> v2(3n+1) % 2 = 0)
    Proof: similar to L2

  Priority 2 (二段階の系、中程度の証明):

  [L4] double_ascent_both_mod3_two:
    n % 8 = 7 -> syracuse (syracuse n) % 3 = 2
    Proof: uses syracuse_ascent_mod3 twice + syracuse_mod4_of_mod8_eq7

  [L5] syracuse_two_step_mod3_of_mod16_eq11:
    n % 16 = 11 -> syracuse (syracuse n) % 3 = 1
    Proof: explicit v2 computation showing v2 = 2 (even)

  Priority 3 (密度定理、重要だが証明は関数解析的):

  [L6] density_mod3_eq_two:
    (informal) Among odd n, T(n) ≡ 2 (mod 3) has density 2/3

  Priority 4 (mod 9 拡張):

  [L7] syracuse_mod9_eq:
    T(n) % 9 = ((3n+1) % 9) * modular_inverse(2^(v2%6), 9) % 9
    Requires: 2^v mod 9 periodicity, modular inverse machinery

  [L8] consecutive_ascent_mod3_always_two:
    k consecutive ascents => T^k(n) % 3 = 2
    Proof: induction on k, each ascent has v2=1
""")
