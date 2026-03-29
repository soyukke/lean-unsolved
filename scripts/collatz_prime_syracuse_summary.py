#!/usr/bin/env python3
"""
最終確認:
1. 素数のTST/Peakが合成数より小さい理由は「3の倍数排除」で説明可能か？
2. mod 8 条件付きでも有意差が残る原因の特定
"""
import math
from collections import defaultdict

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

def total_stopping_time(n):
    x, steps = n, 0
    while x != 1:
        x = collatz_step(x)
        steps += 1
        if steps > 100000: return -1
    return steps

def peak_value(n):
    x, peak = n, n
    while x != 1:
        x = collatz_step(x)
        peak = max(peak, x)
    return peak

def t_test(v1, v2):
    n1, n2 = len(v1), len(v2)
    if n1 < 2 or n2 < 2: return 0, 0, 0
    m1, m2 = sum(v1)/n1, sum(v2)/n2
    s1 = (sum((v-m1)**2 for v in v1)/(n1-1))**0.5
    s2 = (sum((v-m2)**2 for v in v2)/(n2-1))**0.5
    se = ((s1**2/n1)+(s2**2/n2))**0.5
    if se == 0: return 0, m1-m2, 0
    return (m1-m2)/se, m1-m2, se

LIMIT = 20000
is_prime = sieve_primes(LIMIT)

# =============================================
# 核心の検証: 3と5の倍数を排除した合成数との比較
# =============================================
print("=" * 70)
print("核心検証: 素数 vs 3,5の倍数を除外した合成数")
print("=" * 70)

# 素数の特殊性: mod 6 で 1 or 5 にしか存在しない（3除く）
# → 合成数集合から3の倍数を除外して比較

for r in [1, 3, 5, 7]:
    p_tst = []
    # 合成数を因子で分類
    c_tst_all = []
    c_tst_no3 = []  # 3の倍数除外
    c_tst_no35 = []  # 3と5の倍数除外
    c_tst_coprime6 = []  # gcd(n,6)=1 の合成数

    for n in range(r, LIMIT + 1, 8):
        if n < 5: continue
        if n % 2 == 0: continue
        tst = total_stopping_time(n)

        if is_prime[n]:
            p_tst.append(tst)
        else:
            c_tst_all.append(tst)
            if n % 3 != 0:
                c_tst_no3.append(tst)
            if n % 3 != 0 and n % 5 != 0:
                c_tst_no35.append(tst)
            if math.gcd(n, 6) == 1:
                c_tst_coprime6.append(tst)

    if p_tst:
        print(f"\n  r={r} mod 8 (P: {len(p_tst)}):")
        for label, c_vals in [("all composites", c_tst_all),
                               ("no mult of 3", c_tst_no3),
                               ("no mult of 3,5", c_tst_no35),
                               ("gcd(n,6)=1", c_tst_coprime6)]:
            if c_vals:
                t, d, _ = t_test(p_tst, c_vals)
                c_m = sum(c_vals)/len(c_vals)
                p_m = sum(p_tst)/len(p_tst)
                print(f"    vs {label:>20}: P={p_m:.2f} C={c_m:.2f} diff={d:.2f} t={t:.3f} (C:{len(c_vals)})")

# =============================================
# 最終検証: 半素数（2つの素数の積）との比較
# =============================================
print("\n" + "=" * 70)
print("最終検証: 素数 vs 半素数 (p*q, p,q素数)")
print("=" * 70)

def is_semiprime(n, is_p):
    """nが半素数（2つの素数の積）かどうか"""
    if n < 4: return False
    for p in range(2, int(n**0.5) + 1):
        if n % p == 0:
            q = n // p
            if q <= LIMIT and is_p[p] and is_p[q]:
                return True
            return False
    return False

# mod 8 ごとに
for r in [1, 3, 5, 7]:
    p_tst = []
    sp_tst = []  # 半素数

    for n in range(r, LIMIT + 1, 8):
        if n < 5 or n % 2 == 0: continue
        tst = total_stopping_time(n)

        if is_prime[n]:
            p_tst.append(tst)
        elif is_semiprime(n, is_prime):
            sp_tst.append(tst)

    if p_tst and sp_tst:
        t, d, _ = t_test(p_tst, sp_tst)
        p_m = sum(p_tst)/len(p_tst)
        sp_m = sum(sp_tst)/len(sp_tst)
        print(f"  r={r} mod 8: prime={p_m:.2f}({len(p_tst)}) semiprime={sp_m:.2f}({len(sp_tst)}) diff={d:.2f} t={t:.3f}")

# =============================================
# 結論の確認: 素数のnのサイズ分布効果
# =============================================
print("\n" + "=" * 70)
print("サイズマッチング: 素数と同じ mod 8、同じサイズ帯の合成数")
print("=" * 70)

import random
random.seed(42)

for r in [3, 7]:  # mod 8 で ST が非自明な残基
    # 素数リスト
    primes_r = [n for n in range(r, LIMIT+1, 8) if n >= 5 and is_prime[n]]

    # 各素数に対して同じmod 8、サイズが近い合成数をマッチング
    matched = []
    for p in primes_r:
        # p の +-200 以内で同じ mod 8 の合成数を探す
        candidates = []
        for delta in range(8, 400, 8):
            for sign in [1, -1]:
                c = p + sign * delta
                if 5 <= c <= LIMIT and c % 8 == r and not is_prime[c]:
                    candidates.append(c)
                    break
        if candidates:
            matched.append(total_stopping_time(candidates[0]))

    prime_tst = [total_stopping_time(p) for p in primes_r]

    if matched:
        t, d, _ = t_test(prime_tst, matched)
        p_m = sum(prime_tst)/len(prime_tst)
        m_m = sum(matched)/len(matched)
        print(f"  r={r} mod 8: prime={p_m:.2f}({len(prime_tst)}) matched_comp={m_m:.2f}({len(matched)}) diff={d:.2f} t={t:.3f}")

# =============================================
# 素数のmod 2^k分布の偏り調査
# =============================================
print("\n" + "=" * 70)
print("素数の mod 2^k 分布の偏り (STに影響する高ビット)")
print("=" * 70)

for k in [4, 5, 6]:
    mod = 2**k
    prime_dist = defaultdict(int)
    comp_dist = defaultdict(int)

    for n in range(5, LIMIT + 1, 2):
        r = n % mod
        if is_prime[n]:
            prime_dist[r] += 1
        else:
            comp_dist[r] += 1

    p_total = sum(prime_dist.values())
    c_total = sum(comp_dist.values())

    # 分布の偏りを計算（カイ二乗的）
    print(f"\n  mod 2^{k} = {mod}:")

    # STが高い残基（7 mod 8 系統）に素数がどれだけいるか
    high_st_residues = [r for r in range(mod) if r % 2 == 1 and r % 8 == 7]
    p_in_high = sum(prime_dist.get(r, 0) for r in high_st_residues)
    c_in_high = sum(comp_dist.get(r, 0) for r in high_st_residues)

    print(f"    高ST残基({len(high_st_residues)}個): 素数 {p_in_high/p_total*100:.1f}%, 合成数 {c_in_high/c_total*100:.1f}%")

print("\n" + "=" * 70)
print("全検証完了")
print("=" * 70)
