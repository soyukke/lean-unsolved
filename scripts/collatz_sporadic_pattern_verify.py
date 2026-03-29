#!/usr/bin/env python3
"""
散在的非排除残基 r = (2^(2m+1) - 1)/3 の正体を検証

観測パターン:
k=7:  r=85      = 0b1010101       = (2^7  - 1)/3 = 127/3 ... NG
k=9:  r=341     = 0b101010101     = (2^9  - 1)/3 = 511/3 ... NG
k=11: r=1365    = 0b10101010101   = (2^11 - 1)/3
k=13: r=5461    = 0b1010101010101

検証: r = (2^(k) - 1)/3 ? → (4^m - 1)/3 ?
"""

import math

def v2(n):
    if n == 0: return float('inf')
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c


# 散在的残基の正確な公式を特定
sporadic = [
    (7, 85), (9, 341), (11, 1365), (13, 5461),
    (15, 21845), (17, 87381), (19, 349525)
]

print("散在的非排除残基の正体")
print("=" * 60)

for k, r in sporadic:
    # r の各種表現
    print(f"\nk={k}, r={r}")
    print(f"  2進表現: {bin(r)}")
    print(f"  3r+1 = {3*r+1} = 2^{v2(3*r+1)} * {(3*r+1) >> v2(3*r+1)}")
    print(f"  r mod 4 = {r % 4}")

    # (2^k - 1)/3 ?
    if (2**k - 1) % 3 == 0:
        val = (2**k - 1) // 3
        print(f"  (2^{k} - 1)/3 = {val}  {'✓' if val == r else '✗'}")

    # (4^m - 1)/3 ?
    m = (k + 1) // 2
    if (4**m - 1) % 3 == 0:
        val = (4**m - 1) // 3
        print(f"  (4^{m} - 1)/3 = {val}  {'✓' if val == r else '✗'}")

    # 一般公式
    # 0b10101...01 (k bits) = sum_{i=0}^{(k-1)/2} 2^{2i} = (4^{(k+1)/2} - 1)/3
    if k % 2 == 1:
        m = (k + 1) // 2
        val = (4**m - 1) // 3
        print(f"  sum_{{i=0}}^{{{m-1}}} 4^i = (4^{m}-1)/3 = {val}  {'✓' if val == r else '✗'}")

    # Syracuse の挙動
    n = r
    print(f"  Syracuse軌道: {n}", end="")
    for step in range(10):
        val3 = 3 * n + 1
        v = v2(val3)
        n = val3 >> v
        print(f" --v2={v}--> {n}", end="")
        if n < r:
            print(f"  (下降! step={step+1})")
            break
    else:
        print(" ...")

print("\n" + "=" * 60)
print("\n公式: 奇数 k に対して、r = (4^{(k+1)/2} - 1)/3 が散在的非排除残基")
print("     = 2進表現 0b10101...01 (k桁の交互ビット)")
print()
print("性質:")
print("  3r + 1 = 3 * (4^m - 1)/3 + 1 = 4^m = 2^{2m} = 2^{k+1}")
print("  よって v2(3r+1) = k+1")
print("  T(r) = (3r+1) / 2^{k+1} = 1  (1ステップで1に到達!)")
print()
print("なぜ非排除?:")
print("  r ≡ 1 (mod 4) なので v2(3r+1) = k+1")
print("  記号的追跡: n = 2^k * j + r で T(n) = (3n+1)/2^v")
print("  v2(3*(2^k*j + r) + 1) = v2(3*2^k*j + 3r+1) = v2(3*2^k*j + 2^{k+1})")
print("  = v2(2^k * (3j + 2)) = k + v2(3j + 2)")
print("  3j+2 の v2 は j に依存 → 記号的に確定しない → 非排除")
print()
print("これは非排除であっても、具体的なnでは1ステップで1に到達する！")
print("つまりサイクルとは無関係の「偽陽性」非排除残基")
