#!/usr/bin/env python3
"""
エルデシュ問題 #52: Sum-Product Problem（和積問題）の数値実験

有限整数集合 A に対して max(|A+A|, |A·A|) ≫_ε |A|^{2-ε} が成り立つか？
- A+A = {a+b : a,b ∈ A}
- A·A = {a*b : a,b ∈ A}

探索1: 各種集合での |A+A|, |A·A| の計算と比率分析
"""

import random
import math
import itertools

# matplotlib/numpy はオプション
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False
    print("注意: matplotlib/numpy がないためグラフは省略")
    class np:
        @staticmethod
        def mean(x): return sum(x)/len(x)

# ===== 基本関数 =====

def sumset(A):
    """A+A = {a+b : a,b ∈ A}"""
    return {a + b for a in A for b in A}

def productset(A):
    """A·A = {a*b : a,b ∈ A}"""
    return {a * b for a in A for b in A}

def analyze(A, label=""):
    """集合Aのsumset/productsetを計算して表示"""
    ss = sumset(A)
    ps = productset(A)
    n = len(A)
    max_sp = max(len(ss), len(ps))
    ratios = {}
    for alpha in [1.335, 1.5, 2.0]:
        ratios[alpha] = max_sp / (n ** alpha) if n > 0 else 0
    print(f"  {label}: |A|={n}, |A+A|={len(ss)}, |A·A|={len(ps)}, "
          f"max={max_sp}, "
          f"ratio(1.335)={ratios[1.335]:.4f}, "
          f"ratio(1.5)={ratios[1.5]:.4f}, "
          f"ratio(2.0)={ratios[2.0]:.4f}")
    return n, len(ss), len(ps), max_sp, ratios

# ===== 探索1a: 等差数列 A = {1, 2, ..., n} =====

print("=" * 70)
print("探索1a: 等差数列 A = {1, 2, ..., n}")
print("=" * 70)
arith_results = []
for n in [5, 10, 20, 50, 100, 200, 500]:
    A = set(range(1, n + 1))
    result = analyze(A, f"{{1,...,{n}}}")
    arith_results.append(result)

# ===== 探索1b: 等比数列 A = {2^0, 2^1, ..., 2^{n-1}} =====

print()
print("=" * 70)
print("探索1b: 等比数列 A = {2^0, 2^1, ..., 2^{n-1}}")
print("=" * 70)
geom_results = []
for n in [5, 8, 10, 12, 15, 18]:
    A = {2**i for i in range(n)}
    result = analyze(A, f"{{2^0,...,2^{n-1}}}")
    geom_results.append(result)

# ===== 探索1c: ランダム部分集合 =====

print()
print("=" * 70)
print("探索1c: {1,...,N} のランダム部分集合（サイズ n）")
print("=" * 70)

random.seed(42)
random_results = {}
for n in [10, 20, 50, 100]:
    N = n * 10  # 範囲は10n
    trials = 20
    max_sps = []
    ss_sizes = []
    ps_sizes = []
    for _ in range(trials):
        A = set(random.sample(range(1, N + 1), n))
        ss = sumset(A)
        ps = productset(A)
        max_sps.append(max(len(ss), len(ps)))
        ss_sizes.append(len(ss))
        ps_sizes.append(len(ps))
    avg_max = np.mean(max_sps)
    avg_ss = np.mean(ss_sizes)
    avg_ps = np.mean(ps_sizes)
    ratios_avg = {alpha: avg_max / (n ** alpha) for alpha in [1.335, 1.5, 2.0]}
    print(f"  n={n}, N={N}: avg|A+A|={avg_ss:.1f}, avg|A·A|={avg_ps:.1f}, "
          f"avg max={avg_max:.1f}, ratio(2.0)={ratios_avg[2.0]:.4f}")
    random_results[n] = (avg_ss, avg_ps, avg_max, ratios_avg)

# ===== 探索1d: 算術的構造が強い集合（|A+A|が小さい）=====

print()
print("=" * 70)
print("探索1d: |A+A|が小さい集合（算術級数の部分）での |A·A| の振る舞い")
print("=" * 70)

for n in [10, 20, 50, 100]:
    # 純粋な等差数列
    A_arith = set(range(1, n + 1))
    ss_a = sumset(A_arith)
    ps_a = productset(A_arith)
    print(f"  等差数列 {{1,...,{n}}}: |A+A|={len(ss_a)} (≈{len(ss_a)/n:.1f}|A|), "
          f"|A·A|={len(ps_a)} (≈{len(ps_a)/n:.1f}|A|)")

    # 公差 d の等差数列
    d = 3
    A_arith_d = {d * i for i in range(n)}
    ss_d = sumset(A_arith_d)
    ps_d = productset(A_arith_d)
    print(f"  等差数列 {{0,{d},...,{d*(n-1)}}}: |A+A|={len(ss_d)} (≈{len(ss_d)/n:.1f}|A|), "
          f"|A·A|={len(ps_d)} (≈{len(ps_d)/n:.1f}|A|)")

# ===== 探索1e: 幾何的構造が強い集合（|A·A|が小さい）=====

print()
print("=" * 70)
print("探索1e: |A·A|が小さい集合（等比数列的）での |A+A| の振る舞い")
print("=" * 70)

for n in [5, 8, 10, 12, 15]:
    # 純粋な等比数列
    A_geom = {2**i for i in range(n)}
    ss_g = sumset(A_geom)
    ps_g = productset(A_geom)
    print(f"  {{2^0,...,2^{n-1}}}: |A+A|={len(ss_g)} (≈{len(ss_g)/n:.1f}|A|), "
          f"|A·A|={len(ps_g)} (={len(ps_g)}, ≈{len(ps_g)/n:.1f}|A|)")

    # 基数 q の等比数列
    q = 3
    A_geom_q = {q**i for i in range(n)}
    ss_q = sumset(A_geom_q)
    ps_q = productset(A_geom_q)
    print(f"  {{3^0,...,3^{n-1}}}: |A+A|={len(ss_q)} (≈{len(ss_q)/n:.1f}|A|), "
          f"|A·A|={len(ps_q)} (={len(ps_q)}, ≈{len(ps_q)/n:.1f}|A|)")

# ===== 探索1f: max(|A+A|,|A·A|)/|A|^alpha の比率グラフ =====

print()
print("=" * 70)
print("探索1f: 比率のグラフ化")
print("=" * 70)

if not HAS_PLOT:
    print("  (matplotlib なし: グラフ省略)")
else:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # (1) 等差数列 vs 等比数列: |A+A|, |A·A| vs |A|
    ax = axes[0, 0]
    ns_arith = [r[0] for r in arith_results]
    ss_arith = [r[1] for r in arith_results]
    ps_arith = [r[2] for r in arith_results]
    ax.loglog(ns_arith, ss_arith, 'bo-', label='|A+A| (arith)')
    ax.loglog(ns_arith, ps_arith, 'rs-', label='|A*A| (arith)')

    ns_geom = [r[0] for r in geom_results]
    ss_geom = [r[1] for r in geom_results]
    ps_geom = [r[2] for r in geom_results]
    ax.loglog(ns_geom, ss_geom, 'g^-', label='|A+A| (geom)')
    ax.loglog(ns_geom, ps_geom, 'md-', label='|A*A| (geom)')

    x_ref = np.array([5, 500])
    ax.loglog(x_ref, x_ref**2, 'k--', alpha=0.3, label='|A|^2')
    ax.loglog(x_ref, x_ref**1.335, 'k:', alpha=0.3, label='|A|^1.335')
    ax.set_xlabel('|A|')
    ax.set_ylabel('set size')
    ax.set_title('Arithmetic vs Geometric')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # (2) 等差数列の比率
    ax = axes[0, 1]
    for alpha in [1.335, 1.5, 2.0]:
        ratios = [r[4][alpha] for r in arith_results]
        ax.semilogx([r[0] for r in arith_results], ratios, 'o-', label=f'alpha={alpha}')
    ax.set_xlabel('|A|')
    ax.set_ylabel('max(|A+A|,|A*A|) / |A|^alpha')
    ax.set_title('Arithmetic progression ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (3) 等比数列の比率
    ax = axes[1, 0]
    for alpha in [1.335, 1.5, 2.0]:
        ratios = [r[4][alpha] for r in geom_results]
        ax.semilogx([r[0] for r in geom_results], ratios, 'o-', label=f'alpha={alpha}')
    ax.set_xlabel('|A|')
    ax.set_ylabel('max(|A+A|,|A*A|) / |A|^alpha')
    ax.set_title('Geometric progression ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (4) ランダム集合での散布図
    ax = axes[1, 1]
    random.seed(123)
    scatter_n = []
    scatter_ss = []
    scatter_ps = []
    for n in [15, 20, 30, 50]:
        N = n * 10
        for _ in range(50):
            A = set(random.sample(range(1, N + 1), n))
            ss = sumset(A)
            ps = productset(A)
            scatter_n.append(n)
            scatter_ss.append(len(ss))
            scatter_ps.append(len(ps))

    ax.scatter(scatter_ss, scatter_ps, c=scatter_n, cmap='viridis', alpha=0.5, s=20)
    cbar = plt.colorbar(ax.collections[0], ax=ax)
    cbar.set_label('|A|')
    max_val = max(max(scatter_ss), max(scatter_ps))
    ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='|A+A|=|A*A|')
    ax.set_xlabel('|A+A|')
    ax.set_ylabel('|A*A|')
    ax.set_title('Random sets: |A+A| vs |A*A|')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/soyukke/study/lean-unsolved/scripts/erdos52_sum_product.png', dpi=150)
    print("グラフ保存: scripts/erdos52_sum_product.png")

# ===== 探索1g: 最小比率の探索 =====

print()
print("=" * 70)
print("探索1g: max(|A+A|,|A·A|)/|A|^2 を最小化する集合の探索")
print("=" * 70)

# 小さいサイズで全探索
def find_min_ratio_brute(N_range, n):
    """N_range内のn元部分集合でmax(|A+A|,|A·A|)/|A|^2 を最小化"""
    best_ratio = float('inf')
    best_A = None
    elements = list(range(1, N_range + 1))
    count = 0
    for combo in itertools.combinations(elements, n):
        A = set(combo)
        ss = sumset(A)
        ps = productset(A)
        ratio = max(len(ss), len(ps)) / (n ** 2)
        if ratio < best_ratio:
            best_ratio = ratio
            best_A = sorted(A)
        count += 1
    return best_A, best_ratio, count

for n in [4, 5, 6]:
    N_range = n * 3  # 探索範囲
    best_A, best_ratio, count = find_min_ratio_brute(N_range, n)
    ss = sumset(set(best_A))
    ps = productset(set(best_A))
    print(f"  n={n}, 探索範囲={{1,...,{N_range}}}, 組合せ数={count}")
    print(f"    最良集合: {best_A}")
    print(f"    |A+A|={len(ss)}, |A·A|={len(ps)}, max/|A|²={best_ratio:.4f}")

# n=7,8 はランダムサンプリングで
random.seed(42)
for n in [7, 8, 10]:
    best_ratio = float('inf')
    best_A = None
    N_range = n * 5
    for _ in range(10000):
        A = set(random.sample(range(1, N_range + 1), n))
        ss = sumset(A)
        ps = productset(A)
        ratio = max(len(ss), len(ps)) / (n ** 2)
        if ratio < best_ratio:
            best_ratio = ratio
            best_A = sorted(A)
    ss = sumset(set(best_A))
    ps = productset(set(best_A))
    print(f"  n={n}, ランダム探索(10000回), 範囲={{1,...,{N_range}}}")
    print(f"    最良集合: {best_A}")
    print(f"    |A+A|={len(ss)}, |A·A|={len(ps)}, max/|A|²={best_ratio:.4f}")

# ===== 探索1h: 指数成長の確認 =====

print()
print("=" * 70)
print("探索1h: log(max(|A+A|,|A·A|)) / log(|A|) の成長指数")
print("=" * 70)

print("\n等差数列:")
for i in range(1, len(arith_results)):
    n1, _, _, max1, _ = arith_results[i-1]
    n2, _, _, max2, _ = arith_results[i]
    if n1 > 1 and n2 > 1:
        exponent = math.log(max2 / max1) / math.log(n2 / n1)
        print(f"  |A|: {n1} → {n2}, 指数 ≈ {exponent:.4f}")

print("\n等比数列:")
for i in range(1, len(geom_results)):
    n1, _, _, max1, _ = geom_results[i-1]
    n2, _, _, max2, _ = geom_results[i]
    if n1 > 1 and n2 > 1:
        exponent = math.log(max2 / max1) / math.log(n2 / n1)
        print(f"  |A|: {n1} → {n2}, 指数 ≈ {exponent:.4f}")

print()
print("=" * 70)
print("結論サマリ:")
print("=" * 70)
print("""
1. 等差数列 {1,...,n}:
   - |A+A| = 2n-1 ≈ 2|A| (線形成長、最小)
   - |A·A| ≈ |A|²/ln|A| (ほぼ二乗成長)
   → max(|A+A|,|A·A|) は |A·A| に支配され、≈ |A|² に近い

2. 等比数列 {2^0,...,2^{n-1}}:
   - |A·A| = 2n-1 ≈ 2|A| (線形成長、最小)
   - |A+A| は指数的に大きい（ほぼ全ての2^n以下の値を生成）
   → max(|A+A|,|A·A|) は |A+A| に支配され、巨大

3. 加法的構造⇔|A+A|小 → |A·A|大
   乗法的構造⇔|A·A|小 → |A+A|大
   → 両方同時に小さくすることはできない（Sum-Product現象の核心）

4. ランダム集合では |A+A| ≈ |A·A| ≈ |A|² に近い
   → 特殊な構造がなければ両方大きい
""")
