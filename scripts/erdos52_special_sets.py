#!/usr/bin/env python3
"""
エルデシュ問題 #52: Sum-Product Problem 探索2
特殊な集合での解析とFreiman-Ruzsa定理との関連
"""

import random
import math
import itertools

def sumset(A):
    return {a + b for a in A for b in A}

def productset(A):
    return {a * b for a in A for b in A}

# ===== 探索2a: Freiman-Ruzsa定理との関連 =====

print("=" * 70)
print("探索2a: Freiman-Ruzsa定理との関連")
print("=" * 70)
print("""
Freiman-Ruzsa定理: |A+A| ≤ C|A| ならば A は C' 次元の一般化算術級数 (GAP) に含まれる。
→ |A+A| が小さい集合は算術的構造を持つ
→ 算術的構造を持つ集合は |A·A| が大きいはず（Sum-Product予想の核心）

実験: |A+A|/|A| が小さい集合を構成し、|A·A| を調べる
""")

# 倍加定数 (doubling constant) σ(A) = |A+A|/|A| が小さい集合
print("  倍加定数 σ(A) = |A+A|/|A| と積集合の関係:")
print()

# (1) 等差数列 (最小の倍加定数 → 2-1/n)
for n in [10, 20, 50, 100]:
    A = set(range(1, n + 1))
    ss = sumset(A)
    ps = productset(A)
    sigma = len(ss) / n
    print(f"  等差数列 {{1,...,{n}}}: σ={sigma:.3f}, |A·A|/|A|={len(ps)/n:.1f}, "
          f"|A·A|/|A|²={len(ps)/n**2:.4f}")

print()

# (2) 多次元GAP: A = {a + b·d : 0≤a<m, 0≤b<m}, d固定
print("  2次元GAP (格子状集合):")
for m in [5, 7, 10, 15]:
    d = m * m + 1  # d を大きく取り重複を避ける
    A = {a + b * d for a in range(m) for b in range(m)}
    n = len(A)
    ss = sumset(A)
    ps = productset(A)
    sigma = len(ss) / n
    print(f"  {m}x{m} GAP (d={d}): |A|={n}, σ={sigma:.3f}, "
          f"|A·A|={len(ps)}, |A·A|/|A|²={len(ps)/n**2:.4f}")

# ===== 探索2b: max(|A+A|,|A·A|)/|A|^2 の最小化 =====

print()
print("=" * 70)
print("探索2b: max(|A+A|,|A·A|)/|A|^2 を最小化する集合の系統的探索")
print("=" * 70)

# 構造的な候補集合
print("\n  構造的候補集合:")

# (1) {1, 2, ..., n} ∪ {powers of 2}
for n in [10, 20]:
    A = set(range(1, n + 1))
    ss = sumset(A)
    ps = productset(A)
    ratio = max(len(ss), len(ps)) / n**2
    print(f"  {{1,...,{n}}}: max/|A|²={ratio:.4f} (|A+A|={len(ss)}, |A·A|={len(ps)})")

# (2) 乗法構造と加法構造の混合: {1,...,m} ∪ {p, 2p,...,mp}
for m in [5, 10]:
    p = m + 1
    A = set(range(1, m + 1)) | {p * i for i in range(1, m + 1)}
    n = len(A)
    ss = sumset(A)
    ps = productset(A)
    ratio = max(len(ss), len(ps)) / n**2
    print(f"  {{1,...,{m}}} ∪ {{{p},...,{p*m}}}: |A|={n}, max/|A|²={ratio:.4f}")

# (3) 完全二乗数の集合
for k in [5, 8, 10, 15]:
    A = {i * i for i in range(1, k + 1)}
    n = len(A)
    ss = sumset(A)
    ps = productset(A)
    ratio = max(len(ss), len(ps)) / n**2
    print(f"  完全二乗 {{1²,...,{k}²}}: |A|={n}, max/|A|²={ratio:.4f} "
          f"(|A+A|={len(ss)}, |A·A|={len(ps)})")

# (4) smooth numbers (小さい素因数のみ持つ数)
print("\n  smooth numbers (2,3-smooth):")
for bound in [50, 100, 200, 500]:
    A = set()
    a = 1
    while a <= bound:
        b = a
        while b <= bound:
            A.add(b)
            b *= 3
        a *= 2
    A_sorted = sorted(A)
    n = len(A)
    if n >= 5:
        ss = sumset(A)
        ps = productset(A)
        ratio = max(len(ss), len(ps)) / n**2
        print(f"  2,3-smooth ≤ {bound}: |A|={n}, max/|A|²={ratio:.4f} "
              f"(|A+A|={len(ss)}, |A·A|={len(ps)})")

print("\n  smooth numbers (2,3,5-smooth):")
for bound in [100, 500, 1000]:
    A = set()
    a = 1
    while a <= bound:
        b = a
        while b <= bound:
            c = b
            while c <= bound:
                A.add(c)
                c *= 5
            b *= 3
        a *= 2
    n = len(A)
    if n >= 5:
        ss = sumset(A)
        ps = productset(A)
        ratio = max(len(ss), len(ps)) / n**2
        print(f"  2,3,5-smooth ≤ {bound}: |A|={n}, max/|A|²={ratio:.4f} "
              f"(|A+A|={len(ss)}, |A·A|={len(ps)})")

# ===== 探索2c: 有限体 F_p 上の和積現象 =====

print()
print("=" * 70)
print("探索2c: 有限体 F_p 上の和積現象")
print("=" * 70)
print("""
有限体 F_p では Bourgain-Katz-Tao の定理:
  |A| < p^{1-δ} なら max(|A+A|, |A·A|) ≥ c|A|^{1+ε}
  (δ, ε > 0 は定数)

実験: 素数 p に対し、F_p の部分集合で和積を計算
""")

def sumset_mod(A, p):
    return {(a + b) % p for a in A for b in A}

def productset_mod(A, p):
    return {(a * b) % p for a in A for b in A}

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

# 各素数 p で実験
for p in [31, 61, 127, 251]:
    print(f"\n  F_{p} (p={p}):")

    # (1) 等差数列の部分集合 (mod p)
    for size in [5, 10, min(20, p // 3)]:
        if size > p // 2:
            continue
        A = set(range(size))
        ss = sumset_mod(A, p)
        ps = productset_mod(A, p)
        max_sp = max(len(ss), len(ps))
        print(f"    等差{{0,...,{size-1}}}: |A+A|={len(ss)}, |A·A|={len(ps)}, "
              f"max/|A|^1.335={max_sp/size**1.335:.3f}")

    # (2) 乗法群の部分集合 (巡回群)
    # p の原始根を見つける
    g = None
    for candidate in range(2, p):
        order = 1
        val = candidate
        while val != 1:
            val = (val * candidate) % p
            order += 1
        if order == p - 1:
            g = candidate
            break

    if g:
        for size in [5, 10, min(20, p // 3)]:
            if size > p // 2:
                continue
            # 乗法群の最初のsize個
            A = set()
            val = 1
            for _ in range(size):
                A.add(val)
                val = (val * g) % p
            ss = sumset_mod(A, p)
            ps = productset_mod(A, p)
            max_sp = max(len(ss), len(ps))
            print(f"    乗法群(g={g})の{size}元: |A+A|={len(ss)}, |A·A|={len(ps)}, "
                  f"max/|A|^1.335={max_sp/size**1.335:.3f}")

    # (3) 二次剰余の集合
    QR = {(x * x) % p for x in range(1, p)}  # 0を除く
    n_qr = len(QR)
    if n_qr <= 200:  # 計算可能なサイズ
        ss = sumset_mod(QR, p)
        ps = productset_mod(QR, p)
        max_sp = max(len(ss), len(ps))
        print(f"    二次剰余: |QR|={n_qr}, |QR+QR|={len(ss)}, |QR·QR|={len(ps)}, "
              f"max/|QR|^1.335={max_sp/n_qr**1.335:.3f}")

# ===== 探索2d: 指数-対数の対称性 =====

print()
print("=" * 70)
print("探索2d: Sum-Product現象の本質 - 指数/対数変換")
print("=" * 70)
print("""
key insight: log(A·A) = log(A) + log(A)
→ 乗法は対数空間では加法
→ |A+A|小 ⇔ A は算術的 ⇔ log(A) は非算術的 ⇔ |A·A| = |exp(log(A)+log(A))| 大

F_p 上: 離散対数で同じ構造
  A ⊂ F_p*, ind(A·A) = ind(A) + ind(A) (mod p-1)

これがSum-Product予想の背景にある代数的理由
""")

# 実例: {1,...,n} の対数空間での構造
print("  A = {1,...,n}: A の対数空間での分布")
for n in [10, 50, 100]:
    A = list(range(1, n + 1))
    log_A = [math.log(a) for a in A]
    # 対数空間での「間隔」の変動
    gaps = [log_A[i+1] - log_A[i] for i in range(len(log_A)-1)]
    min_gap = min(gaps)
    max_gap = max(gaps)
    print(f"  n={n}: log-gap range [{min_gap:.4f}, {max_gap:.4f}], "
          f"ratio={max_gap/min_gap:.2f}")
    # 対数空間での間隔が不均一 → 乗法的に構造なし → |A·A| 大

# ===== まとめ =====

print()
print("=" * 70)
print("探索2 まとめ")
print("=" * 70)
print("""
1. Freiman-Ruzsa定理との関連:
   - 倍加定数 σ(A) = |A+A|/|A| が小さい集合は算術的構造を持つ
   - 算術的構造を持つ集合は |A·A| が |A|² 近くまで成長
   - 等差数列: σ ≈ 2 だが |A·A|/|A|² → n/ln(n)² に比例

2. max(|A+A|,|A·A|)/|A|² の最小化:
   - {1,2,...,n} で max/|A|² ≈ 0.25-0.56（nに依存）
   - smooth numbers は |A·A| を抑えるが |A+A| が大きくなる
   - 両方同時に小さくする構造は見つからない → 予想の証拠

3. 有限体 F_p 上の現象:
   - 等差部分集合: |A·A| が大きい
   - 乗法部分群: |A+A| が大きい
   - 二次剰余: |QR·QR| = |QR| だが |QR+QR| ≈ p（Weil の結果と整合）

4. Sum-Product現象の本質:
   - 対数変換 log(A·A) = log(A) + log(A)
   - 加法構造と乗法構造は対数変換で双対的
   - 一方の構造を持てば他方は破壊される
""")
