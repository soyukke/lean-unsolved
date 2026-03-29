#!/usr/bin/env python3
"""
コラッツ最小反例 mod 2^k: trailing 1s の完全な2冪構造の解析

前段階で発見した驚くべきパターン:
  k=18のとき trailing 1s >= m の非排除残基数:
    m=12: 64, m=13: 32, m=14: 16, m=15: 8, m=16: 4, m=17: 2, m=18: 1
  → 正確に 2^(k-m) のパターン！

k=20のとき:
    m=13: 128, m=14: 64, m=15: 32, ...
  → 同様に 2^(k-m+1) ?

この「完全2冪」構造を証明的に解析する。
"""

from collections import defaultdict

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def symbolic_trace(r, mod, max_depth=100):
    a, b = mod, r
    for depth in range(1, max_depth + 1):
        if b % 2 == 0:
            if a % 2 == 0:
                a //= 2
                b //= 2
                continue
            else:
                return False, depth
        new_a = 3 * a
        new_b = 3 * b + 1
        v2_b = v2(new_b)
        v2_a = v2(new_a)
        if v2_a >= v2_b:
            divisor = 2 ** v2_b
            a = new_a // divisor
            b = new_b // divisor
            coeff = a - mod
            if coeff < 0:
                rhs = r - b
                if rhs > 0:
                    return True, depth
                else:
                    j_max = (b - r) // (mod - a)
                    max_candidate = mod * j_max + r
                    return True, depth
        else:
            return False, depth
    return False, max_depth


def get_non_excluded(k, max_depth=100):
    mod = 2**k
    ne = []
    for r in range(1, mod, 2):
        ex, _ = symbolic_trace(r, mod, max_depth)
        if not ex:
            ne.append(r)
    return ne


# ===== 構造1: trailing 1s >= m の非排除残基数の正確な値 =====
print("=" * 80)
print("trailing 1s >= m の非排除残基数: 2冪パターンの検証")
print("=" * 80)

for k in [10, 12, 14, 16, 18, 20]:
    ne = get_non_excluded(k)
    print(f"\nk={k} (mod 2^{k}={2**k}), 非排除 {len(ne)}個:")

    total = len(ne)
    for m in range(2, k+1):
        count = sum(1 for r in ne if all((r >> i) & 1 == 1 for i in range(m)))
        # これは trailing m bits が全て1 → r ≡ 2^m - 1 (mod 2^m)
        expected_power = k - m  # 仮説: count = 2^(k-m) ?
        is_power = (count > 0 and count & (count - 1) == 0)  # 2の冪かチェック
        log2_count = count.bit_length() - 1 if count > 0 else -1
        match_str = f"= 2^{log2_count}" if is_power and count > 0 else f"≠ 2^{expected_power}"
        print(f"  trailing 1s >= {m:2d}: {count:6d} {match_str}")
        if count == 0:
            break


# ===== 構造2: 非排除残基の具体的な構成 =====
print("\n" + "=" * 80)
print("構造2: trailing 1s が高い非排除残基の具体例")
print("=" * 80)

for k in [14, 18, 20]:
    ne = get_non_excluded(k)
    # trailing 1s が k-1 以上のもの
    for m in [k-1, k-2, k-3]:
        mask = (1 << m) - 1
        high_ne = [r for r in ne if (r & mask) == mask]
        if high_ne:
            print(f"\n  k={k}, trailing 1s >= {m}: {high_ne}")
            for r in high_ne:
                print(f"    r = {r} = {bin(r)} (trailing 1s = {m})")


# ===== 構造3: 非排除残基の再帰構造 =====
print("\n" + "=" * 80)
print("構造3: k → k+1 での非排除残基のリフト構造")
print("=" * 80)

for k in [8, 10, 12, 14]:
    ne_k = set(get_non_excluded(k))
    ne_k1 = set(get_non_excluded(k+1))
    mod_k = 2**k
    mod_k1 = 2**(k+1)

    # ne_k の各残基 r に対し、r と r + 2^k のどちらが ne_k1 に入るか
    both = 0
    only_r = 0
    only_r_plus = 0
    neither = 0

    for r in ne_k:
        in_low = r in ne_k1
        in_high = (r + mod_k) in ne_k1
        if in_low and in_high:
            both += 1
        elif in_low:
            only_r += 1
        elif in_high:
            only_r_plus += 1
        else:
            neither += 1

    # ne_k1 の中で ne_k に射影されないもの
    new_in_k1 = 0
    for r in ne_k1:
        if (r % mod_k) not in ne_k:
            new_in_k1 += 1

    print(f"\n  k={k} → k+1={k+1}:")
    print(f"    ne(k) = {len(ne_k)}, ne(k+1) = {len(ne_k1)}")
    print(f"    両方生存: {both}, r のみ: {only_r}, r+2^k のみ: {only_r_plus}, どちらも消滅: {neither}")
    print(f"    新規出現 (ne_k に親なし): {new_in_k1}")
    print(f"    比率 ne(k+1)/ne(k) = {len(ne_k1)/len(ne_k):.4f}")
    print(f"    分岐率 (both/ne_k) = {both/len(ne_k):.4f}")


# ===== 構造4: 非排除残基の mod 3 * 2^k パターン =====
print("\n" + "=" * 80)
print("構造4: 3-adic構造の深掘り")
print("=" * 80)

for k in [12, 16, 20]:
    ne = get_non_excluded(k)
    mod = 2**k

    # n_0 ≡ r (mod 2^k) のとき、T(n_0) mod 2^k-? の分布
    # (n_0 = r のとき T(r) の値)
    t_values = []
    for r in ne[:50]:  # 最初の50個
        if r % 2 == 0:
            continue
        m = 3 * r + 1
        while m % 2 == 0:
            m //= 2
        t_values.append((r, m, m % mod))

    # T(r) mod 2^k が ne に入るか？
    ne_set = set(ne)
    t_in_ne = sum(1 for _, _, tm in t_values if tm in ne_set)
    print(f"\n  k={k}: T(r) mod 2^k が非排除集合に入る割合: {t_in_ne}/{len(t_values)}")


# ===== 構造5: 非排除密度の精密な漸近公式 =====
print("\n" + "=" * 80)
print("構造5: 非排除残基数の精密な漸近公式")
print("=" * 80)

import math

data = []
for k in range(6, 21):
    ne = get_non_excluded(k)
    data.append((k, len(ne)))

print(f"{'k':>4} {'ne(k)':>10} {'ne(k)/ne(k-1)':>14} {'ne(k)/k':>10} {'ne(k)/(k*1.74^k)':>18}")
for i, (k, ne) in enumerate(data):
    ratio = ne / data[i-1][1] if i > 0 else 0
    per_k = ne / k
    scaled = ne / (k * 1.7363**k) if k > 0 else 0
    print(f"  {k:2d}  {ne:10d}  {ratio:14.6f}  {per_k:10.2f}  {scaled:18.8f}")


# trailing 1s = m の非排除数の公式
print("\n\ntrailing 1s = m の非排除残基数 f(k, m):")
print(f"{'k\\m':>4}", end="")
for m in range(2, 11):
    print(f" {'m='+str(m):>8}", end="")
print()

for k in [10, 12, 14, 16, 18, 20]:
    ne = get_non_excluded(k)
    print(f"  {k:2d}", end="")
    for m in range(2, 11):
        mask = (1 << m) - 1
        # trailing 1s が正確に m のもの
        count_ge_m = sum(1 for r in ne if (r & ((1 << m) - 1)) == (1 << m) - 1)
        count_ge_m1 = sum(1 for r in ne if (r & ((1 << (m+1)) - 1)) == (1 << (m+1)) - 1)
        exact_m = count_ge_m - count_ge_m1
        print(f" {exact_m:8d}", end="")
    print()

# f(k, m) / f(k-2, m) の比率
print("\nf(k, m) / f(k-2, m) の比率:")
ne_data = {}
for k in [10, 12, 14, 16, 18, 20]:
    ne = get_non_excluded(k)
    ne_data[k] = ne

for k in [14, 16, 18, 20]:
    ne = ne_data[k]
    ne_prev = ne_data[k-2] if k-2 in ne_data else None
    if ne_prev is None:
        continue
    print(f"  k={k}:", end="")
    for m in range(2, min(k-2, 10)):
        c1 = sum(1 for r in ne if (r & ((1<<m)-1)) == (1<<m)-1) - \
             sum(1 for r in ne if (r & ((1<<(m+1))-1)) == (1<<(m+1))-1)
        c2 = sum(1 for r in ne_prev if (r & ((1<<m)-1)) == (1<<m)-1) - \
             sum(1 for r in ne_prev if (r & ((1<<(m+1))-1)) == (1<<(m+1))-1)
        ratio = c1/c2 if c2 > 0 else 0
        print(f"  m={m}: {ratio:.3f}", end="")
    print()


print("\n" + "=" * 80)
print("解析完了")
print("=" * 80)
