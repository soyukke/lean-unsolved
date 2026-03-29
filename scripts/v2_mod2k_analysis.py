"""
v2(3n+1) >= k の条件を mod 2^k で精密に分析する。

核心的主張: v2(3n+1) >= k iff n = (2^k - 1)/3 (mod 2^k)

ただし (2^k-1)/3 は Z/2^kZ での 3^{-1} * (2^k - 1) を意味する。
k が偶数のとき 2^k - 1 = 3 * ((4^{k/2}-1)/3) なので (2^k-1)/3 は整数。
k が奇数のとき 3 | (2^k - 1) iff 2^k = 1 mod 3 iff k は偶数。
よって k が奇数のとき 3 ∤ (2^k - 1) なので (2^k-1)/3 は通常の整数ではない。
mod 2^k での 3 の逆元を使う必要がある。

正確な主張を導出しよう。
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def mod_inverse_3(k):
    """3^{-1} mod 2^k を計算する。3 * x = 1 (mod 2^k) となる x。"""
    mod = 2**k
    # 拡張ユークリッドの互除法
    # 3 は奇数なので gcd(3, 2^k) = 1 で逆元が存在
    return pow(3, -1, mod)

print("=" * 60)
print("Part 1: 3^{-1} mod 2^k の計算")
print("=" * 60)
for k in range(1, 13):
    inv3 = mod_inverse_3(k)
    print(f"  3^{{-1}} mod 2^{k:2d} = {inv3:6d}  (= {inv3} mod {2**k}),  check: 3*{inv3} mod {2**k} = {(3*inv3) % (2**k)}")

print()
print("=" * 60)
print("Part 2: v2(3n+1) >= k iff n = ? (mod 2^k)")
print("=" * 60)
print()

for k in range(1, 9):
    mod = 2**k
    # 全ての n mod 2^k で v2(3n+1) >= k となるものを列挙
    valid_residues = []
    for r in range(mod):
        val = 3 * r + 1
        if v2(val) >= k:
            valid_residues.append(r)

    # (2^k - 1) * 3^{-1} mod 2^k を計算
    inv3 = mod_inverse_3(k)
    predicted = ((mod - 1) * inv3) % mod

    print(f"  k={k}: v2(3n+1)>={k} iff n mod {mod} in {valid_residues}")
    print(f"       predicted: (2^{k}-1) * 3^{{-1}} mod 2^{k} = ({mod-1}) * {inv3} mod {mod} = {predicted}")
    print(f"       match: {valid_residues == [predicted]}")
    print()

print("=" * 60)
print("Part 3: 条件の同値変形を検証")
print("=" * 60)
print()
print("v2(3n+1) >= k")
print("<=> 2^k | (3n+1)")
print("<=> 3n + 1 = 0  (mod 2^k)")
print("<=> 3n = -1     (mod 2^k)")
print("<=> 3n = 2^k-1  (mod 2^k)")
print("<=> n = (2^k-1)/3 (mod 2^k)  [3 is invertible in Z/2^kZ]")
print()

for k in range(1, 9):
    mod = 2**k
    inv3 = mod_inverse_3(k)
    residue = ((mod - 1) * inv3) % mod

    # 検算: 3 * residue + 1 = 0 mod 2^k ?
    check = (3 * residue + 1) % mod
    print(f"  k={k}: n = {residue} (mod {mod}), check: 3*{residue}+1 = {3*residue+1}, mod {mod} = {check}")

print()
print("=" * 60)
print("Part 4: v2(3n+1) = k (exact) の条件")
print("=" * 60)
print()
print("v2(3n+1) = k iff v2(3n+1) >= k AND NOT v2(3n+1) >= k+1")
print("iff n = (2^k-1)/3 (mod 2^k) AND n != (2^{k+1}-1)/3 (mod 2^{k+1})")
print()

for k in range(1, 7):
    mod = 2**k
    mod2 = 2**(k+1)
    inv3_k = mod_inverse_3(k)
    inv3_k1 = mod_inverse_3(k+1)
    residue_ge_k = ((mod - 1) * inv3_k) % mod
    residue_ge_k1 = ((mod2 - 1) * inv3_k1) % mod2

    # v2 = k exactly の残余
    exact_residues = []
    for r in range(mod2):
        if r % mod == residue_ge_k and r != residue_ge_k1:
            exact_residues.append(r)

    # 検証
    actual_exact = []
    for r in range(mod2):
        val = 3 * r + 1
        if v2(val) == k:
            actual_exact.append(r)

    print(f"  k={k}: v2(3n+1)={k} iff n mod {mod2} in {actual_exact}")
    print(f"       predicted: {exact_residues}")
    print(f"       match: {actual_exact == exact_residues}")
    print()

print("=" * 60)
print("Part 5: 既存Lean補題との整合性チェック")
print("=" * 60)
print()

# v2_of_mod8_eq1: n = 1 (mod 8) => v2(3n+1) = 2
print("v2_of_mod8_eq1: n = 1 (mod 8) => v2(3n+1) = 2")
for n in [1, 9, 17, 25, 33]:
    print(f"  n={n}: v2(3*{n}+1) = v2({3*n+1}) = {v2(3*n+1)}")

# v2_of_mod8_eq3: n = 3 (mod 8) => v2(3n+1) = 1
print("v2_of_mod8_eq3: n = 3 (mod 8) => v2(3n+1) = 1")
for n in [3, 11, 19, 27, 35]:
    print(f"  n={n}: v2(3*{n}+1) = v2({3*n+1}) = {v2(3*n+1)}")

# v2_ge_three_of_mod8_eq5: n = 5 (mod 8) => v2(3n+1) >= 3
print("v2_ge_three_of_mod8_eq5: n = 5 (mod 8) => v2(3n+1) >= 3")
for n in [5, 13, 21, 29, 37]:
    print(f"  n={n}: v2(3*{n}+1) = v2({3*n+1}) = {v2(3*n+1)}")

# v2_of_mod8_eq7: n = 7 (mod 8) => v2(3n+1) = 1
print("v2_of_mod8_eq7: n = 7 (mod 8) => v2(3n+1) = 1")
for n in [7, 15, 23, 31, 39]:
    print(f"  n={n}: v2(3*{n}+1) = v2({3*n+1}) = {v2(3*n+1)}")

print()
print("=" * 60)
print("Part 6: n = 5 (mod 8) の細分: v2(3n+1) の正確な値")
print("=" * 60)
print()
print("n = 5 (mod 8) は 3^{-1}*(2^k-1) パターンで k >= 3")
for k in range(3, 10):
    mod = 2**k
    inv3 = mod_inverse_3(k)
    residue = ((mod - 1) * inv3) % mod
    print(f"  v2(3n+1) >= {k}: n = {residue} (mod {mod}), {residue} mod 8 = {residue % 8}")

print()
print("Note: v2(3n+1) >= 3 の条件は n = 5 (mod 8)")
print("      v2(3n+1) >= 4 の条件は n = 5 (mod 16)")
print("      v2(3n+1) >= 5 の条件は n = 21 (mod 32)")
print("      ...etc")

print()
print("=" * 60)
print("Part 7: (2^k-1) * 3^{-1} mod 2^k の閉形式パターン")
print("=" * 60)
print()

for k in range(1, 16):
    mod = 2**k
    inv3 = mod_inverse_3(k)
    residue = ((mod - 1) * inv3) % mod
    # residue = (2^k - 1)/3 in Z/2^kZ
    # Let's see if there's a pattern
    print(f"  k={k:2d}: 3^{{-1}} mod 2^k = {inv3:6d}, (2^k-1)*3^{{-1}} mod 2^k = {residue:6d}, binary = {bin(residue)}")

print()
print("=" * 60)
print("Part 8: 3^{-1} mod 2^k のパターン")
print("=" * 60)
print()

# 3^{-1} mod 2^k follows a pattern based on sum of powers of (-2)^i / 3
# Actually, 3^{-1} mod 2^k can be computed by the formula:
# 3^{-1} = sum_{i=0}^{k-2} (-2)^i mod 2^k  ... no
# Let's verify: 3 * x = 1 mod 2^k
# If 3x = 1 mod 2, x = 1 mod 2
# If 3x = 1 mod 4, x = 3 mod 4
# If 3x = 1 mod 8, x = 3 mod 8
# If 3x = 1 mod 16, x = 11 mod 16
# If 3x = 1 mod 32, x = 11 mod 32

# Check: the inverse lifts by Hensel's lemma
for k in range(1, 16):
    inv = mod_inverse_3(k)
    print(f"  3^{{-1}} mod 2^{k:2d} = {inv:6d}")

# Verify: alternating pattern
# k=1: 1
# k=2: 3 = 1 + 2
# k=3: 3 = 1 + 2
# k=4: 11 = 3 + 8
# k=5: 11 = 3 + 8
# k=6: 43 = 11 + 32
# k=7: 43 = 11 + 32
# k=8: 171 = 43 + 128
# Pattern: inv3(k) = inv3(k-1) if k is odd, inv3(k-1) + 2^{k-2} if k is even

print()
print("Checking pattern: inv3(2m) = inv3(2m-1) + 2^{2m-2}, inv3(2m+1) = inv3(2m)")
for k in range(2, 16):
    inv_k = mod_inverse_3(k)
    inv_km1 = mod_inverse_3(k-1)
    diff = inv_k - inv_km1
    if diff != 0:
        import math
        log2_diff = math.log2(diff) if diff > 0 else "N/A"
        print(f"  k={k}: inv3({k}) - inv3({k-1}) = {inv_k} - {inv_km1} = {diff}, log2 = {log2_diff}")
    else:
        print(f"  k={k}: inv3({k}) = inv3({k-1}) = {inv_k}")

print()
print("=" * 60)
print("Part 9: Lean証明設計のための核心等式")
print("=" * 60)
print()
print("Main theorem: v2(3n+1) >= k <=> 2^k | (3n+1) <=> n = (2^k-1) * 3^{-1} (mod 2^k)")
print()
print("For Lean formalization, the cleanest approach is:")
print("  1. Define: residue_k := the unique r < 2^k such that 3r + 1 = 0 (mod 2^k)")
print("  2. Show: v2(3n+1) >= k <=> n % 2^k = residue_k")
print("  3. Show: residue_k = (2^k - 1) * inv3_mod_2k (mod 2^k)")
print()
print("Alternatively, the condition 2^k | (3n+1) can be stated directly:")
print("  v2(3n+1) >= k <=> (3*n + 1) % 2^k = 0")
print("  <=> n % 2^k = residue_k where 3 * residue_k + 1 = 0 (mod 2^k)")
print()

# Compute residue_k for small k
for k in range(1, 9):
    mod = 2**k
    for r in range(mod):
        if (3 * r + 1) % mod == 0:
            print(f"  k={k}: residue_{k} = {r}, check: 3*{r}+1 = {3*r+1}, mod {mod} = {(3*r+1) % mod}")
            break

print()
print("=" * 60)
print("Part 10: 3の逆元と(2^k-1)/3の関係")
print("=" * 60)
print()
print("residue_k = (2^k - 1) / 3 in Z/2^kZ")
print("= (2^k - 1) * 3^{-1} mod 2^k")
print()
print("When k is even: 2^k - 1 = (2^2)^{k/2} - 1 = 4^{k/2} - 1 = 0 mod 3")
print("  So (2^k-1)/3 is an integer!")
print("When k is odd: 2^k - 1 = 2 mod 3, so (2^k-1)/3 is NOT an integer")
print("  But (2^k-1) * 3^{-1} mod 2^k is still well-defined")
print()

for k in range(1, 13):
    mod = 2**k
    val = mod - 1
    inv3 = mod_inverse_3(k)
    residue = (val * inv3) % mod
    is_int = val % 3 == 0
    if is_int:
        int_val = val // 3
        print(f"  k={k:2d}: (2^k-1)/3 = {int_val} (integer), mod 2^k residue = {residue}, match: {int_val % mod == residue}")
    else:
        print(f"  k={k:2d}: (2^k-1)/3 not integer, mod 2^k residue via inv = {residue}")
