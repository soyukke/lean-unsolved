#!/usr/bin/env python3
"""
探索178: root(m) の mod 6 場合分けの数値検証

Syracuse逆写像木において、奇数 m に対する「根」root(m) を定義する。
root(m) は syracuse(root(m)) = m を満たす最小の奇数。

Syracuse: T(n) = (3n+1) / 2^v2(3n+1)

逆問題: T(r) = m を解く。
  (3r+1) / 2^v2(3r+1) = m
  3r+1 = m * 2^k (ある k に対して)
  r = (m * 2^k - 1) / 3

r が正の奇数になるための条件を m の mod 6 で分類する。

仮説:
  m ≡ 1 (mod 6) → root = (4m - 1) / 3
  m ≡ 5 (mod 6) → root = (2m - 1) / 3
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
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)

def find_all_preimages(m, limit=10000):
    """Find all odd n such that syracuse(n) = m, with n < limit"""
    preimages = []
    for n in range(1, limit, 2):  # odd numbers only
        if syracuse(n) == m:
            preimages.append(n)
    return preimages

print("=" * 60)
print("Part 1: Verify root formulas for small m")
print("=" * 60)

for m in range(1, 100, 2):  # odd m
    preimages = find_all_preimages(m, 5000)
    if not preimages:
        continue
    root = min(preimages)
    mod6 = m % 6

    # Check formulas
    if mod6 == 1:
        formula_val = (4 * m - 1) // 3
        formula_check = (4 * m - 1) % 3 == 0
        match = (root == formula_val)
    elif mod6 == 3:
        # m ≡ 3 (mod 6) means 3 | m, so syracuse can't produce it (3 never divides syracuse output)
        formula_val = None
        formula_check = False
        match = False
    elif mod6 == 5:
        formula_val = (2 * m - 1) // 3
        formula_check = (2 * m - 1) % 3 == 0
        match = (root == formula_val)
    else:
        formula_val = None
        formula_check = False
        match = False

    if not match and mod6 != 3:
        print(f"  MISMATCH: m={m}, mod6={mod6}, root={root}, formula={formula_val}")

    if m <= 30:
        print(f"m={m:3d}, mod6={mod6}, preimages={preimages[:5]}, root={root}, formula={formula_val}, match={match}")

print("\n" + "=" * 60)
print("Part 2: Algebraic verification of the formulas")
print("=" * 60)

print("\nCase m ≡ 1 (mod 6): root = (4m-1)/3")
print("  m = 6k+1, root = (4(6k+1)-1)/3 = (24k+3)/3 = 8k+1")
print("  Check: root = 8k+1 is odd (yes)")
print("  Check: 3*root+1 = 3(8k+1)+1 = 24k+4 = 4(6k+1) = 4m")
print("  So v2(3*root+1) = v2(4m) = 2 + v2(m)")
print("  Since m = 6k+1 is odd, v2(m) = 0, so v2(3*root+1) = 2")
print("  Syracuse(root) = (3*root+1) / 2^2 = 4m / 4 = m ✓")

print("\nCase m ≡ 5 (mod 6): root = (2m-1)/3")
print("  m = 6k+5, root = (2(6k+5)-1)/3 = (12k+9)/3 = 4k+3")
print("  Check: root = 4k+3 is odd (yes)")
print("  Check: 3*root+1 = 3(4k+3)+1 = 12k+10 = 2(6k+5) = 2m")
print("  So v2(3*root+1) = v2(2m) = 1 + v2(m)")
print("  Since m = 6k+5 is odd, v2(m) = 0, so v2(3*root+1) = 1")
print("  Syracuse(root) = (3*root+1) / 2^1 = 2m / 2 = m ✓")

print("\n" + "=" * 60)
print("Part 3: Verify that root is actually the MINIMUM preimage")
print("=" * 60)

print("\nFor m ≡ 1 (mod 6):")
for m in [1, 7, 13, 19, 25, 31, 37, 43, 49]:
    preimages = find_all_preimages(m, 10000)
    root_formula = (4 * m - 1) // 3
    is_min = (root_formula == min(preimages)) if preimages else "no preimages"
    print(f"  m={m:3d}: root_formula={root_formula}, preimages[:5]={preimages[:5]}, is_min={is_min}")

print("\nFor m ≡ 5 (mod 6):")
for m in [5, 11, 17, 23, 29, 35, 41, 47, 53]:
    preimages = find_all_preimages(m, 10000)
    root_formula = (2 * m - 1) // 3
    is_min = (root_formula == min(preimages)) if preimages else "no preimages"
    print(f"  m={m:3d}: root_formula={root_formula}, preimages[:5]={preimages[:5]}, is_min={is_min}")

print("\n" + "=" * 60)
print("Part 4: Structure of all preimages vs the root")
print("=" * 60)

print("\nPreimage pattern analysis:")
for m in [7, 11, 13, 17, 19, 23]:
    preimages = find_all_preimages(m, 20000)
    if len(preimages) >= 2:
        diffs = [preimages[i+1] - preimages[i] for i in range(min(5, len(preimages)-1))]
        ratios = [preimages[i+1] / preimages[0] if preimages[0] > 0 else 0 for i in range(min(5, len(preimages)-1))]
        print(f"  m={m:3d} (mod6={m%6}): preimages[:6]={preimages[:6]}")
        print(f"    root = {preimages[0]}, pattern: each preimage p has 4p+1 also a preimage")
        # verify 4p+1 pattern
        for p in preimages[:3]:
            if 4*p+1 in preimages:
                print(f"    4*{p}+1 = {4*p+1} is preimage: True")

print("\n" + "=" * 60)
print("Part 5: Key relationships for Lean formalization")
print("=" * 60)

print("\nTheorem 1: root_mod6_eq1")
print("  Statement: For odd m with m % 6 = 1,")
print("    let r := (4*m - 1) / 3")
print("    then syracuse r = m")
print("  Proof sketch in Lean:")
print("    1. Show (4*m - 1) % 3 = 0 using m % 6 = 1")
print("    2. Let r = (4*m - 1) / 3")
print("    3. Show r is odd: r = 8k+1 where m = 6k+1")
print("    4. Show 3*r + 1 = 4*m")
print("    5. Show v2(4*m) = 2 (since m is odd)")
print("    6. Conclude syracuse(r) = 4m/4 = m")

print("\nTheorem 2: root_mod6_eq5")
print("  Statement: For odd m with m % 6 = 5,")
print("    let r := (2*m - 1) / 3")
print("    then syracuse r = m")
print("  Proof sketch in Lean:")
print("    1. Show (2*m - 1) % 3 = 0 using m % 6 = 5")
print("    2. Let r = (2*m - 1) / 3")
print("    3. Show r is odd: r = 4k+3 where m = 6k+5")
print("    4. Show 3*r + 1 = 2*m")
print("    5. Show v2(2*m) = 1 (since m is odd)")
print("    6. Conclude syracuse(r) = 2m/2 = m")

print("\nTheorem 3 (more general): root_mod6_eq1_alt")
print("  Statement: For n with n % 6 = 1 and n >= 1,")
print("    syracuse ((4*n - 1) / 3) = n")

# Verify these hold for large range
print("\n" + "=" * 60)
print("Part 6: Large-scale verification")
print("=" * 60)

errors_1 = 0
errors_5 = 0
for m in range(1, 100000, 2):
    mod6 = m % 6
    if mod6 == 1:
        r = (4 * m - 1) // 3
        if syracuse(r) != m:
            errors_1 += 1
            if errors_1 <= 3:
                print(f"  ERROR mod6=1: m={m}, r={r}, syr(r)={syracuse(r)}")
    elif mod6 == 5:
        r = (2 * m - 1) // 3
        if syracuse(r) != m:
            errors_5 += 1
            if errors_5 <= 3:
                print(f"  ERROR mod6=5: m={m}, r={r}, syr(r)={syracuse(r)}")

print(f"Verified mod6=1 formula for {50000 - errors_1}/{50000 - (50000//3)} odd m up to 100000")
print(f"Verified mod6=5 formula for {50000 - errors_5}/{50000 - (50000//3)} odd m up to 100000")
print(f"Errors: mod6=1: {errors_1}, mod6=5: {errors_5}")

print("\n" + "=" * 60)
print("Part 7: Lean 4 theorem design")
print("=" * 60)

lean_code = """
-- Theorem: root_of_mod6_eq1
-- For m with m % 6 = 1 (which implies m is odd and m % 3 ≠ 0),
-- syracuse((4*m - 1) / 3) = m
--
-- Key algebraic identity: 3 * ((4*m - 1) / 3) + 1 = 4 * m
-- when m % 6 = 1 (since (4m-1) % 3 = 0)
--
-- Required lemmas:
-- 1. four_mul_sub_one_div3_mod6_1 (m : ℕ) (h : m % 6 = 1) :
--      3 * ((4 * m - 1) / 3) + 1 = 4 * m
-- 2. four_mul_sub_one_div3_odd (m : ℕ) (h : m % 6 = 1) :
--      ((4 * m - 1) / 3) % 2 = 1
-- 3. v2_four_mul_odd (m : ℕ) (hodd : m % 2 = 1) :
--      v2 (4 * m) = 2
-- 4. syracuse_root_mod6_eq1 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 1) :
--      syracuse ((4 * m - 1) / 3) = m

-- Theorem: root_of_mod6_eq5
-- For m with m % 6 = 5,
-- syracuse((2*m - 1) / 3) = m
--
-- Key algebraic identity: 3 * ((2*m - 1) / 3) + 1 = 2 * m
-- when m % 6 = 5 (since (2m-1) % 3 = 0)
--
-- Required lemmas:
-- 1. two_mul_sub_one_div3_mod6_5 (m : ℕ) (h : m % 6 = 5) :
--      3 * ((2 * m - 1) / 3) + 1 = 2 * m
-- 2. two_mul_sub_one_div3_odd (m : ℕ) (h : m % 6 = 5) :
--      ((2 * m - 1) / 3) % 2 = 1
-- 3. v2_two_mul_odd (m : ℕ) (hodd : m % 2 = 1) :
--      v2 (2 * m) = 1
-- 4. syracuse_root_mod6_eq5 (m : ℕ) (hm : m ≥ 1) (h : m % 6 = 5) :
--      syracuse ((2 * m - 1) / 3) = m
"""
print(lean_code)

print("\n" + "=" * 60)
print("Part 8: Additional relationship - root and syracuse_four_mul_add_one")
print("=" * 60)

print("\nThe existing theorem syracuse_four_mul_add_one states:")
print("  For odd n >= 1: syracuse(4n+1) = syracuse(n)")
print("\nThis means: if syracuse(r) = m, then syracuse(4r+1) = m too.")
print("So all preimages form a chain: r, 4r+1, 4(4r+1)+1, ...")
print("The ROOT is the smallest in this chain.")

print("\nConnection to root formula:")
print("  For m ≡ 1 (mod 6): root = (4m-1)/3")
print("    Next: 4*root+1 = 4*(4m-1)/3 + 1 = (16m-4+3)/3 = (16m-1)/3")
print("  For m ≡ 5 (mod 6): root = (2m-1)/3")
print("    Next: 4*root+1 = 4*(2m-1)/3 + 1 = (8m-4+3)/3 = (8m-1)/3")

# Verify this chain
print("\nChain verification:")
for m in [7, 11, 13, 17, 19, 23, 25, 29]:
    preimages = find_all_preimages(m, 50000)
    if len(preimages) >= 3:
        chain_check = all(4*preimages[i]+1 == preimages[i+1] for i in range(len(preimages)-1))
        print(f"  m={m} (mod6={m%6}): preimages={preimages[:4]}..., chain_valid={chain_check}")
