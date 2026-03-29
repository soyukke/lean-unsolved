"""
v2(3n+1) >= k <=> n % 2^k = residue_k の証明設計。

核心的発見:
  residue_k = (4^{ceil(k/2)} - 1) / 3

具体的には:
  k=1,2: residue = 1 = (4-1)/3 = (4^1-1)/3
  k=3,4: residue = 5 = (16-1)/3 = (4^2-1)/3
  k=5,6: residue = 21 = (64-1)/3 = (4^3-1)/3
  k=7,8: residue = 85 = (256-1)/3 = (4^4-1)/3

つまり residue_k = (4^{ceil(k/2)} - 1) / 3

もっとシンプルに: residue_{2m} = residue_{2m-1} = (4^m - 1)/3
"""

import math

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

print("=" * 60)
print("Part 1: residue_k の閉形式")
print("=" * 60)
print()

for k in range(1, 17):
    mod = 2**k
    # Find residue
    for r in range(mod):
        if (3 * r + 1) % mod == 0:
            residue = r
            break

    # Predicted: (4^{ceil(k/2)} - 1) / 3
    m = math.ceil(k / 2)
    predicted = (4**m - 1) // 3

    print(f"  k={k:2d}: residue = {residue:6d}, (4^{m} - 1)/3 = {predicted:6d}, match: {residue == predicted}")

print()
print("=" * 60)
print("Part 2: 証明の方針分析")
print("=" * 60)
print()
print("--- 方針A: v2 >= k <=> 2^k | (3n+1) を直接示す ---")
print()
print("v2(m) >= k <=> 2^k | m は v2 の定義から帰納法で示せる。")
print("そして 2^k | (3n+1) <=> (3n+1) % 2^k = 0 <=> n % 2^k = residue_k")
print()

print("--- 方針B: 帰納的構成 ---")
print()
print("v2(3n+1) >= k の基本ステップ:")
print("  k=0: 常に真")
print("  k=1: n は奇数 (n % 2 = 1)")
print("  k=2: n % 4 = 1")
print("  k=3: n % 8 = 5")
print("  k => k+1: n % 2^{k+1} の条件を n % 2^k の条件に帰着")
print()

# k -> k+1 の帰着
for k in range(1, 9):
    mod_k = 2**k
    mod_k1 = 2**(k+1)
    res_k = None
    res_k1 = None
    for r in range(mod_k):
        if (3 * r + 1) % mod_k == 0:
            res_k = r
            break
    for r in range(mod_k1):
        if (3 * r + 1) % mod_k1 == 0:
            res_k1 = r
            break

    print(f"  k={k} -> k+1={k+1}: v2 >= {k} <=> n%{mod_k}={res_k}, v2 >= {k+1} <=> n%{mod_k1}={res_k1}")
    print(f"    Refinement: {res_k1} mod {mod_k} = {res_k1 % mod_k} (should be {res_k}): {res_k1 % mod_k == res_k}")

print()
print("=" * 60)
print("Part 3: Lean形式化のための核心補題リスト")
print("=" * 60)
print()
print("Lemma 1 (v2_ge_iff_dvd): v2(m) >= k <=> 2^k | m")
print("  証明: m に関する強帰納法 + v2 の定義展開")
print()
print("Lemma 2 (v2_ge_iff_mod): v2(3n+1) >= k <=> (3*n+1) % 2^k = 0")
print("  証明: Lemma 1 + Nat.dvd_iff_mod_eq_zero")
print()
print("Lemma 3 (v2_ge_iff_residue): v2(3n+1) >= k <=> n % 2^k = residue_k")
print("  where residue_k = (4^{ceil(k/2)} - 1) / 3")
print("  証明: Lemma 2 + 合同式の計算")
print()

print("=" * 60)
print("Part 4: Lemma 1 の証明設計の詳細")
print("=" * 60)
print()
print("v2(m) >= k <=> 2^k | m")
print()
print("(=>): k に関する帰納法")
print("  k=0: trivial (2^0 = 1 | m)")
print("  k+1: v2(m) >= k+1")
print("    m != 0 and m % 2 = 0 (v2(m) > 0 より)")
print("    v2(m) = 1 + v2(m/2) >= k+1")
print("    v2(m/2) >= k")
print("    IH: 2^k | m/2")
print("    2 * 2^k | 2 * (m/2) = m")
print("    2^{k+1} | m")
print()
print("(<=): k に関する帰納法")
print("  k=0: trivial (v2(m) >= 0)")
print("  k+1: 2^{k+1} | m")
print("    2 | m, so m != 0 and m % 2 = 0")
print("    v2(m) = 1 + v2(m/2)")
print("    2^k | m/2 (from 2^{k+1} | m)")
print("    IH: v2(m/2) >= k")
print("    v2(m) = 1 + v2(m/2) >= k+1")
print()

print("=" * 60)
print("Part 5: 重要な補助定理 - 3の逆元の漸化式")
print("=" * 60)
print()

# residue_k の漸化式を導出
print("residue_k の列: ", end="")
residues = []
for k in range(0, 17):
    mod = 2**k if k > 0 else 1
    if k == 0:
        residues.append(0)
        print("0, ", end="")
        continue
    for r in range(mod):
        if (3 * r + 1) % mod == 0:
            residues.append(r)
            print(f"{r}, ", end="")
            break
print()
print()

print("Pattern:")
print("  residue_0 = 0")
print("  residue_1 = 1")
for k in range(2, 15):
    r = residues[k]
    r_prev = residues[k-1]
    diff = r - r_prev
    print(f"  residue_{k} = {r} = residue_{k-1} + {diff}" + (f" = {r_prev} + 2^{k-2}" if diff == 2**(k-2) else f" = {r_prev} (same)"))

print()
print("Pattern summary:")
print("  residue_{2m} = residue_{2m-1}  (stable for even -> odd transition)")
print("  residue_{2m+1} = residue_{2m} + 2^{2m-1}  (jump for odd -> even transition)")
print()

# Verify
print("Verification of the recurrence:")
for m in range(1, 8):
    k_even = 2*m
    k_odd = 2*m + 1
    if k_odd < len(residues):
        expected_odd = residues[k_even] + 2**(2*m - 1)
        print(f"  residue_{k_odd} = residue_{k_even} + 2^{2*m-1} = {residues[k_even]} + {2**(2*m-1)} = {expected_odd}, actual = {residues[k_odd]}, match: {expected_odd == residues[k_odd]}")

print()
print("=" * 60)
print("Part 6: 最もシンプルな閉形式")
print("=" * 60)
print()
print("residue_k = (2^k - 1) * 3^{-1} mod 2^k")
print()
print("しかし Lean で 3^{-1} mod 2^k を扱うのは面倒。")
print("代替: 直接 3 * residue_k + 1 = 0 (mod 2^k) を示す方が簡単。")
print()
print("Most practical Lean approach:")
print("  1. Define residue_k by a closed form: (4^{ceil(k/2)} - 1) / 3")
print("  2. Verify 3 * residue_k + 1 = 0 (mod 2^k) by computation")
print("  3. Use uniqueness of residue mod 2^k")
print()

# 閉形式の検証
print("Closed form: residue_k = (4^{ceil(k/2)} - 1) / 3")
print("Equivalently:")
print("  k = 2m:   residue = (4^m - 1) / 3")
print("  k = 2m+1: residue = (4^{m+1} - 1) / 3")
print()

for k in range(1, 13):
    m = math.ceil(k / 2)
    closed = (4**m - 1) // 3
    actual = residues[k]
    # Verify: 3 * closed + 1 = 0 mod 2^k
    check = (3 * closed + 1) % (2**k)
    print(f"  k={k:2d}: (4^{m} - 1)/3 = {closed:6d}, actual residue = {actual:6d}, 3*r+1 mod 2^k = {check}")

print()
print("=" * 60)
print("Part 7: もう一つの閉形式: residue_k = sum_{i=0}^{ceil(k/2)-1} 4^i")
print("=" * 60)
print()
print("(4^m - 1)/3 = 1 + 4 + 4^2 + ... + 4^{m-1}")
print("= sum_{i=0}^{m-1} 4^i")
print("= sum_{i=0}^{m-1} 2^{2i}")
print()
print("Binary representation: alternating 01 pattern")
print("  m=1: 1       = 01")
print("  m=2: 5       = 0101")
print("  m=3: 21      = 010101")
print("  m=4: 85      = 01010101")
print("  m=5: 341     = 0101010101")
print()
print("This is the 'checkerboard' pattern in binary!")

print()
print("=" * 60)
print("Part 8: Lean証明の具体的戦略")
print("=" * 60)
print()
print("""
Strategy for Lean formalization:

-- Step 1: v2_ge_iff_dvd
theorem v2_ge_iff_dvd (m : Nat) (k : Nat) (hm : m > 0) :
    v2 m >= k <-> 2^k | m

-- Step 2: v2_3n1_ge_iff_mod
theorem v2_3n1_ge_iff_mod (n k : Nat) :
    v2 (3*n+1) >= k <-> (3*n+1) % 2^k = 0

-- Step 3: mod_condition  (the key equivalence)
theorem v2_3n1_ge_iff_residue (n k : Nat) :
    (3*n+1) % 2^k = 0 <-> n % 2^k = collatz_residue k
  where collatz_residue k = ... (to be defined)

-- Step 4: specific instances recovering existing lemmas
-- k=1: n%2=1 (odd)
-- k=2: n%4=1  (v2_ge_two_of_mod4_eq1)
-- k=3: n%8=5  (v2_ge_three_of_mod8_eq5)
-- k=4: n%16=5
-- k=5: n%32=21
""")

print()
print("=" * 60)
print("Part 9: omega で解ける範囲の確認")
print("=" * 60)
print()
print("Lean の omega タクティクは線形算術を解く。")
print("(3*n+1) % 2^k = 0 <=> n % 2^k = r は omega で直接解ける場合がある。")
print()
print("テスト: 具体的な k に対して omega で十分か?")
for k in range(1, 7):
    mod = 2**k
    r = residues[k]
    print(f"  k={k}: (3*n+1) % {mod} = 0 <=> n % {mod} = {r}")
    # This is: 3n + 1 = mod * q for some q, and n = mod * p + r for some p
    # 3*(mod*p + r) + 1 = mod*q
    # 3*mod*p + 3r + 1 = mod*q
    # mod | (3r+1) (which is true by construction)
    # So this should be provable by omega for fixed k
    print(f"       3*{r}+1 = {3*r+1}, {3*r+1} / {mod} = {(3*r+1)//mod}, remainder = {(3*r+1)%mod}")
