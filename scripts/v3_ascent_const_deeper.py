"""
v3(3^k - 2^k) と サイクル方程式の3-adic構造: 深い解析

Part 1で確定した事実:
  v3(3^k - 2^k) = 0 for all k >= 1
  v3(2^s - 3^p) = 0 for all p >= 1

本スクリプトでは:
1. mod 9 での正確なサイクル方程式の制約
2. 5-adic, 7-adic 等の他の素数での解析
3. 2^s - 3^p の素因数分解パターンとサイクル排除
"""

import math
from collections import Counter, defaultdict

def vp(n, p):
    """p-adic valuation of n"""
    if n == 0:
        return float('inf')
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v

def multiplicative_order(a, m):
    """Order of a modulo m"""
    if math.gcd(a, m) != 1:
        return None
    order = 1
    power = a % m
    while power != 1:
        power = (power * a) % m
        order += 1
        if order > m:
            return None
    return order

# === Part 1: mod 9 の正確な解析 ===
print("=" * 70)
print("Part 1: ord_9(2) と mod 9 サイクル制約")
print("=" * 70)

ord_9 = multiplicative_order(2, 9)
print(f"ord_9(2) = {ord_9}")
print(f"\n2^s mod 9 の完全周期:")
for s in range(ord_9 + 1):
    print(f"  2^{s} mod 9 = {pow(2, s, 9)}")

# サイクル方程式 mod 9 (p >= 2):
# LHS: n * (2^s - 3^p) ≡ n * 2^s mod 9 (since 3^p ≡ 0 mod 9 for p >= 2)
# RHS: Σ 3^i * 2^{a_i} ≡ 2^{a_0} + 3*2^{a_1} mod 9 (since 3^i ≡ 0 mod 9 for i >= 2)

print(f"\nサイクル方程式 mod 9 (p >= 2):")
print(f"  LHS ≡ n * 2^s mod 9")
print(f"  RHS ≡ 2^{{a_0}} + 3 * 2^{{a_1}} mod 9")

# 右辺の全可能な値
print(f"\n右辺 2^a0 + 3*2^a1 mod 9 の全可能な値:")
rhs_vals_9 = {}
for a0_mod in range(ord_9):
    for a1_mod in range(ord_9):
        val = (pow(2, a0_mod, 9) + 3 * pow(2, a1_mod, 9)) % 9
        key = (a0_mod, a1_mod)
        rhs_vals_9[key] = val
        print(f"  a0≡{a0_mod}, a1≡{a1_mod} mod {ord_9}: 2^a0={pow(2,a0_mod,9)}, 3*2^a1={3*pow(2,a1_mod,9)%9}, sum≡{val} mod 9")

rhs_possible_9 = set(rhs_vals_9.values())
print(f"\n右辺の可能な値 mod 9: {sorted(rhs_possible_9)}")

# 左辺の可能な値
# n は奇数かつ v3(n)=0 なので n mod 9 ∈ {1,2,4,5,7,8}
n_mods = [r for r in range(9) if r % 2 == 1 and r % 3 != 0]
print(f"n mod 9 の可能な値: {n_mods}")

lhs_possible_9 = {}
for n_mod in n_mods:
    for s_mod in range(ord_9):
        val = (n_mod * pow(2, s_mod, 9)) % 9
        lhs_possible_9[(n_mod, s_mod)] = val

print(f"\nLHS = n*2^s mod 9 の表:")
print(f"{'n mod 9':>8} | " + " | ".join(f"s≡{s}" for s in range(ord_9)) + " |")
print("-" * 70)
for n_mod in n_mods:
    vals_str = " | ".join(f"{lhs_possible_9[(n_mod, s)]:>3}" for s in range(ord_9))
    print(f"{n_mod:>8} | {vals_str} |")

# 排除チェック
print(f"\n排除される (n mod 9, s mod {ord_9}) 組み合わせ:")
excluded_count = 0
total_count = 0
for n_mod in n_mods:
    for s_mod in range(ord_9):
        total_count += 1
        lhs_val = lhs_possible_9[(n_mod, s_mod)]
        if lhs_val not in rhs_possible_9:
            excluded_count += 1
            print(f"  n≡{n_mod} mod 9, s≡{s_mod} mod {ord_9}: LHS≡{lhs_val} mod 9 → 不可能!")

if excluded_count == 0:
    print("  なし")
print(f"\n排除率: {excluded_count}/{total_count} = {excluded_count/total_count:.2%}")

# === Part 2: p=1 の特別な場合 ===
print("\n" + "=" * 70)
print("Part 2: p=1 (Syracuse 1ステップサイクル) の mod 9 解析")
print("=" * 70)
print("p=1: n(2^s - 3) = 2^{a_0}")
print("  n = 2^{a_0} / (2^s - 3)")
print("  s >= 2 が必要")

for s in range(2, 20):
    denom = 2**s - 3
    if denom > 0:
        # n = 2^{a_0} / denom で n が正奇数整数
        # a_0 >= 1 (since 3n+1 is even)
        # 実際には a_0 = s (全除算) なのでこの場合 n = 2^s/(2^s-3) は整数でない
        # 一般には a_0 は自由パラメータではなく v2(3n+1) で決まる
        print(f"  s={s}: 2^s-3 = {denom}, v3={vp(denom,3)}, factors: ", end="")
        d = denom
        for p in [2,3,5,7,11,13,17,19,23,29,31,37]:
            while d % p == 0:
                print(f"{p}", end="*")
                d //= p
        if d > 1:
            print(f"{d}", end="")
        print()

# === Part 3: 他の素数での解析 ===
print("\n" + "=" * 70)
print("Part 3: vp(3^k - 2^k) for various primes p")
print("=" * 70)

for p in [5, 7, 11, 13, 17, 19, 23]:
    print(f"\np = {p}:")
    ord_p = multiplicative_order(2, p)
    ord_p_3 = multiplicative_order(3, p)
    print(f"  ord_{p}(2) = {ord_p}, ord_{p}(3) = {ord_p_3}")

    # 3^k ≡ 2^k mod p iff (3/2)^k ≡ 1 mod p iff (3*2^{-1})^k ≡ 1 mod p
    inv2 = pow(2, p-2, p)  # 2^{-1} mod p (Fermat)
    ratio = (3 * inv2) % p
    ord_ratio = multiplicative_order(ratio, p)
    print(f"  3*2^{{-1}} mod {p} = {ratio}, ord = {ord_ratio}")

    # vp(3^k - 2^k) > 0 iff ord_ratio | k
    non_zero_ks = [k for k in range(1, 50) if vp(3**k - 2**k, p) > 0]
    print(f"  v{p}(3^k-2^k) > 0 for k = {non_zero_ks}")

    if non_zero_ks:
        # LTE の検証
        for k in non_zero_ks[:5]:
            actual_vp = vp(3**k - 2**k, p)
            lte_pred = vp(3 - 2, p) + vp(k, p)  # LTE formula (when applicable)
            print(f"    k={k}: v{p}(3^k-2^k) = {actual_vp}, v{p}(1)+v{p}(k) = {vp(1,p)}+{vp(k,p)} = {lte_pred}")

# === Part 4: LTE for p = 5 (detailed) ===
print("\n" + "=" * 70)
print("Part 4: Lifting the Exponent Lemma for p=5")
print("=" * 70)

# LTE: if p | a-b, p ∤ a, p ∤ b, and p odd prime:
#   v_p(a^n - b^n) = v_p(a-b) + v_p(n)
# For a=3, b=2: a-b=1, so p ∤ (a-b) for any p >= 2
# So LTE doesn't directly apply.

# Instead: v5(3^k - 2^k) > 0 iff 3^k ≡ 2^k mod 5
# 3 mod 5 = 3, 2 mod 5 = 2
# 3/2 mod 5 = 3 * 3 = 9 ≡ 4 mod 5
# ord_5(4) = ?
print(f"3*2^(-1) mod 5 = {3 * pow(2, 3, 5) % 5}")
print(f"4^k mod 5: {[pow(4, k, 5) for k in range(6)]}")
print(f"ord_5(4) = {multiplicative_order(4, 5)}")
print()
print("v5(3^k - 2^k) > 0 iff 2|k:")
for k in range(1, 21):
    v = vp(3**k - 2**k, 5)
    mark = " <-- v5 > 0" if v > 0 else ""
    print(f"  k={k}: v5 = {v}, k mod 2 = {k%2}{mark}")

# For 3^k - 2^k with k even:
print("\nk偶数での v5(3^k - 2^k):")
print("3^{2m} - 2^{2m} = (3^m - 2^m)(3^m + 2^m)")
for m in range(1, 16):
    k = 2*m
    v = vp(3**k - 2**k, 5)
    v_minus = vp(3**m - 2**m, 5)
    v_plus = vp(3**m + 2**m, 5)
    print(f"  k={k} (m={m}): v5(3^k-2^k) = {v}, v5(3^m-2^m) = {v_minus}, v5(3^m+2^m) = {v_plus}, sum = {v_minus + v_plus}")

# === Part 5: サイクル方程式での v5 解析 ===
print("\n" + "=" * 70)
print("Part 5: サイクル方程式の v5 解析")
print("=" * 70)

print("v5(2^s - 3^p):")
print("  2^s ≡ 3^p mod 5 iff (2/3)^s ≡ 3^{p-s} mod 5")
print("  2 mod 5 = 2, 3 mod 5 = 3")
print(f"  ord_5(2) = {multiplicative_order(2, 5)}")
print(f"  ord_5(3) = {multiplicative_order(3, 5)}")

# 2^s mod 5 と 3^p mod 5 の表
print(f"\n2^s mod 5: {[pow(2, s, 5) for s in range(4)]}, period = 4")
print(f"3^p mod 5: {[pow(3, p, 5) for p in range(4)]}, period = 4")

# 2^s ≡ 3^p mod 5 の条件
print("\n2^s ≡ 3^p mod 5 の条件表:")
for s_mod in range(4):
    for p_mod in range(4):
        if pow(2, s_mod, 5) == pow(3, p_mod, 5):
            print(f"  s≡{s_mod} mod 4, p≡{p_mod} mod 4: 2^s≡3^p≡{pow(2,s_mod,5)} mod 5")

# v5 > 0 のケース
print("\nv5(2^s - 3^p) > 0 のケースを実データで確認:")
for p in range(1, 30):
    s_min = int(p * math.log2(3)) + 1
    for s in range(s_min, s_min + 10):
        diff = 2**s - 3**p
        if diff > 0:
            v = vp(diff, 5)
            if v > 0:
                print(f"  s={s}, p={p}: v5 = {v}, s mod 4 = {s%4}, p mod 4 = {p%4}")

# === Part 6: サイクル方程式の全素数解析 ===
print("\n" + "=" * 70)
print("Part 6: サイクル方程式の多素数同時制約")
print("=" * 70)

print("""
サイクル方程式: n(2^s - 3^p) = Σ_{i=0}^{p-1} 3^i · 2^{a_i}

各素数 q で:
  vq(LHS) = vq(n) + vq(2^s - 3^p)
  vq(RHS) は a_i に依存

q = 3: v3(n) = 0 (既に証明)
q = 5: v5(n) + v5(2^s-3^p) = v5(RHS)
q = 7: v7(n) + v7(2^s-3^p) = v7(RHS)
""")

# RHS = Σ 3^i * 2^{a_i} の vq
# vq(RHS) = vq(Σ 3^i * 2^{a_i})
# q ≠ 2, 3 の場合、各項の vq = vq(3^i) + vq(2^{a_i}) = 0
# よって各項は q と互いに素
# しかし和の vq は 0 とは限らない

# 例: q=5, p=2
# RHS = 2^{a_0} + 3*2^{a_1}
# v5(RHS) = v5(2^{a_0} + 3*2^{a_1})
# = v5(2^{a_1}(2^{a_0-a_1} + 3)) if a_0 > a_1
# = v5(2^{a_0-a_1} + 3)

print("q=5 での RHS 解析 (p=2):")
print("RHS = 2^{a_0} + 3·2^{a_1}, a_0 > a_1 >= 0")
print("= 2^{a_1}(2^{a_0-a_1} + 3)")
print("v5(RHS) = v5(2^{a_0-a_1} + 3)")
print()
print(f"v5(2^d + 3) for d = a_0 - a_1:")
for d in range(1, 25):
    val = 2**d + 3
    v = vp(val, 5)
    if v > 0:
        print(f"  d={d}: 2^{d}+3 = {val}, v5 = {v}")

print(f"\n2^d + 3 mod 5:")
for d in range(8):
    print(f"  d={d}: 2^{d}+3 = {2**d+3}, mod 5 = {(2**d+3)%5}")
print(f"  周期: {[((2**d+3)%5) for d in range(4)]}")
print(f"  v5(2^d+3) > 0 iff 2^d ≡ 2 mod 5 iff d ≡ 1 mod 4")

# === Part 7: サイクルの s と p の関係の精密化 ===
print("\n" + "=" * 70)
print("Part 7: サイクル排除 - s/p の有理近似制約")
print("=" * 70)

print("""
サイクル方程式: n(2^s - 3^p) = RHS

n > 0 かつ RHS > 0 なので 2^s > 3^p が必要。
つまり s*log2 > p*log3, s/p > log3/log2 = log_2(3)

逆に n = RHS / (2^s - 3^p) が正の奇数整数。
RHS < 3^p * 2^{max(a_i)} なので n < 3^p * 2^s / (2^s - 3^p)

s/p が log_2(3) ≈ 1.58496... に近いほど n は大きくなる。

Baker の定理による下界:
  |s*log2 - p*log3| > C / s^M (定数 C, M > 0)
  これが n の上界と矛盾 → サイクル排除
""")

log2_3 = math.log2(3)
print(f"log_2(3) = {log2_3}")
print(f"\n最良の有理近似 s/p ≈ log_2(3):")

# 連分数展開で最良近似を求める
from fractions import Fraction

def continued_fraction_convergents(x, n_terms=20):
    """連分数展開の近似分数列を返す"""
    convergents = []
    a = int(x)
    p_prev, p_curr = 1, a
    q_prev, q_curr = 0, 1
    convergents.append((p_curr, q_curr))

    remainder = x - a
    for _ in range(n_terms):
        if abs(remainder) < 1e-15:
            break
        x_next = 1.0 / remainder
        a = int(x_next)
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        convergents.append((p_curr, q_curr))
        remainder = x_next - a
    return convergents

convergents = continued_fraction_convergents(log2_3, 30)
print(f"{'s/p':>10} | {'s':>6} {'p':>6} | {'2^s - 3^p':>20} | {'|s/p - log_2(3)|':>20}")
print("-" * 75)
for s, p in convergents[:15]:
    diff = 2**s - 3**p
    approx_err = abs(s/p - log2_3)
    print(f"{s/p:>10.6f} | {s:>6} {p:>6} | {diff:>20} | {approx_err:>20.2e}")

# === Part 8: ascentConst と サイクル方程式の同時制約まとめ ===
print("\n" + "=" * 70)
print("Part 8: ascentConst(k) = 3^k - 2^k の素因数分解")
print("=" * 70)

def factorize(n):
    """Simple factorization"""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

print(f"\nascentConst(k) = 3^k - 2^k の素因数分解:")
for k in range(1, 31):
    ac = 3**k - 2**k
    factors = factorize(ac)
    factor_str = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
    print(f"  k={k:2d}: {ac:>15} = {factor_str}")

# === Part 9: (3^k-2^k) の最小素因数のパターン ===
print("\n" + "=" * 70)
print("Part 9: ascentConst(k) の最小素因数")
print("=" * 70)

print(f"\n{'k':>4} | {'3^k-2^k':>15} | {'最小素因数':>10} | {'k mod 4':>7}")
print("-" * 50)
for k in range(1, 51):
    ac = 3**k - 2**k
    min_p = min(factorize(ac).keys()) if ac > 1 else 1
    print(f"{k:>4} | {ac:>15} | {min_p:>10} | {k%4:>7}")

# Zsygmondy の定理との関連
print("\n" + "=" * 70)
print("Part 10: Zsygmondy の定理の応用")
print("=" * 70)
print("""
Zsygmondy の定理: a > b >= 1, n >= 3 のとき、
a^n - b^n は a^k - b^k (k < n) のいずれも割り切れない素因数を持つ
(primitive prime divisor が存在する)。
例外: (a,b,n) = (2,1,6) のとき 2^6-1 = 63 = 9*7 で primitive divisor なし。

a=3, b=2 の場合:
3^n - 2^n は各 n >= 3 で primitive prime divisor を持つ。
""")

# primitive prime divisor を見つける
prev_primes = set()
for k in range(1, 31):
    ac = 3**k - 2**k
    factors = set(factorize(ac).keys())
    primitive = factors - prev_primes
    prev_primes |= factors
    if primitive:
        print(f"  k={k:2d}: primitive primes = {sorted(primitive)}")
    else:
        print(f"  k={k:2d}: NO primitive prime! (factors = {sorted(factors)})")
