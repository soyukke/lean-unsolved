#!/usr/bin/env python3
"""
Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の逆像分岐分析

T^{-k}(1) = 「1にちょうどkステップで到達する奇数の集合」の構造解析

分析項目:
1. |T^{-k}(1)| の成長率 (k=1..40)
2. mod 8, 16, 32 での分布
3. 層間の遷移パターン
4. 累積被覆密度
5. 各層の数の統計的性質
"""

import math
from collections import defaultdict, Counter
import json
import time

# ============================================================
# Syracuse写像とその逆写像
# ============================================================

def v2(n):
    """2-adic valuation: nを割り切る2の最大べき"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse写像 T(n) = (3n+1) / 2^{v2(3n+1)} (奇数nに対して)"""
    assert n % 2 == 1, f"Syracuse写像は奇数に対してのみ定義: n={n}"
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse_odd(m):
    """
    逆Syracuse写像: T(n) = m となる奇数 n を全て返す。

    T(n) = (3n+1)/2^a = m  =>  3n+1 = m * 2^a  =>  n = (m*2^a - 1)/3
    条件: nが正の奇数、a >= 1

    n が奇数 <=> m*2^a - 1 ≡ 0 (mod 2) は自動(m奇数, 2^a偶数なので m*2^a偶数、-1で奇数)
    n が3で割り切れる: m*2^a ≡ 1 (mod 3)

    m ≡ 1 (mod 3) のとき: 2^a ≡ 1 (mod 3) => a ≡ 0 (mod 2)
    m ≡ 2 (mod 3) のとき: 2^a ≡ 2 (mod 3) => a ≡ 1 (mod 2)
    m ≡ 0 (mod 3) のとき: nは整数にならない (3n+1 = m*2^a, 3|m*2^a だが 3 nmid (3n+1))
    """
    if m % 3 == 0:
        return []  # 3の倍数は前像を持たない（奇数の前像として）

    results = []
    # aの上限: n >= 1 => m*2^a - 1 >= 3 => m*2^a >= 4
    # 実用上、十分大きなaまで試す
    max_a = 100  # 十分大きい

    if m % 3 == 1:
        # a ≡ 0 (mod 2), a = 2, 4, 6, ...
        start_a = 2
        step = 2
    else:  # m % 3 == 2
        # a ≡ 1 (mod 2), a = 1, 3, 5, ...
        start_a = 1
        step = 2

    for a in range(start_a, max_a + 1, step):
        n = (m * (1 << a) - 1) // 3
        if n > 0 and n % 2 == 1:
            # 検証
            assert (m * (1 << a) - 1) % 3 == 0
            assert syracuse(n) == m, f"検証失敗: T({n}) = {syracuse(n)} != {m}"
            results.append((n, a))

    return results

def inverse_syracuse_odd_bounded(m, max_val):
    """
    逆Syracuse写像で、n <= max_val の前像のみ返す。
    """
    if m % 3 == 0:
        return []

    results = []
    if m % 3 == 1:
        start_a = 2
        step = 2
    else:
        start_a = 1
        step = 2

    a = start_a
    while True:
        n = (m * (1 << a) - 1) // 3
        if n > max_val:
            break
        if n > 0 and n % 2 == 1:
            results.append((n, a))
        a += step

    return results

# ============================================================
# T^{-k}(1) の構築
# ============================================================

def build_inverse_layers(root, max_depth, max_val=None):
    """
    T^{-k}(root) を k=0 から max_depth まで構築。
    max_val: 探索する値の上限（Noneなら無制限だが実用上制限が必要）

    返り値: layers[k] = T^{-k}(root) の要素集合
    """
    layers = [set() for _ in range(max_depth + 1)]
    layers[0] = {root}
    all_visited = {root: 0}  # value -> depth (最短ステップ)

    for k in range(1, max_depth + 1):
        new_layer = set()
        for m in layers[k - 1]:
            if max_val:
                preimages = inverse_syracuse_odd_bounded(m, max_val)
            else:
                preimages = inverse_syracuse_odd(m)
            for n, a in preimages:
                if n not in all_visited:
                    new_layer.add(n)
                    all_visited[n] = k
        layers[k] = new_layer

    return layers, all_visited

# ============================================================
# 分析1: |T^{-k}(1)| の成長率
# ============================================================

print("=" * 70)
print("分析1: |T^{-k}(1)| のサイズと成長率 (k=0..40)")
print("=" * 70)

MAX_DEPTH = 40
MAX_VAL = 10**15  # 十分大きな上限

start_time = time.time()
layers, all_visited = build_inverse_layers(1, MAX_DEPTH, max_val=MAX_VAL)
elapsed = time.time() - start_time

print(f"\n構築時間: {elapsed:.2f}秒")
print(f"総ノード数: {len(all_visited)}")

layer_sizes = []
growth_rates = []
cumulative = 0

print(f"\n{'k':>4} {'|T^{-k}(1)|':>15} {'成長率':>12} {'累積':>15} {'最小値':>15} {'最大値':>20}")
print("-" * 90)

for k in range(MAX_DEPTH + 1):
    size = len(layers[k])
    cumulative += size
    if k > 0 and len(layers[k-1]) > 0:
        rate = size / len(layers[k-1])
    else:
        rate = float('nan')

    layer_sizes.append(size)
    growth_rates.append(rate)

    min_val = min(layers[k]) if layers[k] else 0
    max_val_layer = max(layers[k]) if layers[k] else 0

    print(f"{k:>4} {size:>15,} {rate:>12.6f} {cumulative:>15,} {min_val:>15,} {max_val_layer:>20,}")

# ============================================================
# 分析2: 成長率の収束と理論値比較
# ============================================================

print("\n" + "=" * 70)
print("分析2: 成長率の収束分析")
print("=" * 70)

# 理論的な成長率の上界: 各ノードは最大で無限個の前像を持つが、
# 実効的には 4/3 付近と予測されている
# (Galton-Watson過程の平均子孫数 = sum over a of 1/3 * (1/2)^a = ...)

# 期待成長率の理論計算
# T(n) = m の前像数: m mod 3 == 0 なら 0個
# m mod 3 == 1 なら a=2,4,6,...  -> 各aに1つ前像
# m mod 3 == 2 なら a=1,3,5,...  -> 各aに1つ前像
# ただし n <= max_val の制約で有限個

# 有限範囲 [1, N] での平均前像数
print("\n期待前像数（理論）:")
print("  m ≡ 1 (mod 3): 前像の a は 2,4,6,... -> n = (m*2^a - 1)/3")
print("  m ≡ 2 (mod 3): 前像の a は 1,3,5,... -> n = (m*2^a - 1)/3")
print("  m ≡ 0 (mod 3): 前像なし (入次数 = 0)")

# 直近10層の平均成長率
if len(growth_rates) > 15:
    recent_rates = [r for r in growth_rates[10:] if not math.isnan(r)]
    avg_recent = sum(recent_rates) / len(recent_rates)
    print(f"\n直近(k=10..{MAX_DEPTH})の平均成長率: {avg_recent:.6f}")
    print(f"理論的期待値 (4/3 ≈ 1.3333): {4/3:.6f}")
    print(f"差: {avg_recent - 4/3:.6f}")

# ============================================================
# 分析3: mod 8, 16, 32 での分布
# ============================================================

print("\n" + "=" * 70)
print("分析3: T^{-k}(1) の mod 8, 16, 32 での分布")
print("=" * 70)

def analyze_mod_distribution(layers, modulus, depths_to_show):
    """各層の要素の mod modulus での分布を分析"""
    results = {}
    for k in depths_to_show:
        if k >= len(layers) or len(layers[k]) == 0:
            continue
        counts = Counter()
        for n in layers[k]:
            counts[n % modulus] += 1
        total = len(layers[k])
        dist = {}
        for r in range(modulus):
            if r % 2 == 0:
                continue  # 奇数のみなので偶数residueは0
            dist[r] = counts.get(r, 0) / total if total > 0 else 0
        results[k] = dist
    return results

# mod 8 分析
print("\n--- mod 8 分布 (奇数residue: 1,3,5,7) ---")
depths = [1, 5, 10, 15, 20, 25, 30, 35, 40]
mod8_dist = analyze_mod_distribution(layers, 8, depths)

print(f"{'k':>4} {'mod1':>8} {'mod3':>8} {'mod5':>8} {'mod7':>8} {'|層|':>10}")
for k in depths:
    if k in mod8_dist:
        d = mod8_dist[k]
        print(f"{k:>4} {d.get(1,0):>8.4f} {d.get(3,0):>8.4f} {d.get(5,0):>8.4f} {d.get(7,0):>8.4f} {len(layers[k]):>10,}")

# mod 16 分析
print("\n--- mod 16 分布 ---")
mod16_dist = analyze_mod_distribution(layers, 16, depths)

print(f"{'k':>4} {'m1':>6} {'m3':>6} {'m5':>6} {'m7':>6} {'m9':>6} {'m11':>6} {'m13':>6} {'m15':>6}")
for k in depths:
    if k in mod16_dist:
        d = mod16_dist[k]
        residues = [1, 3, 5, 7, 9, 11, 13, 15]
        vals = [f"{d.get(r,0):>6.3f}" for r in residues]
        print(f"{k:>4} {''.join(vals)}")

# mod 6 分析（入次数との関連）
print("\n--- mod 6 分布 (入次数構造と直結) ---")
mod6_dist = analyze_mod_distribution(layers, 6, depths)

print(f"{'k':>4} {'mod1':>8} {'mod3':>8} {'mod5':>8} {'|層|':>10}")
print("  (注: mod6≡1,5は入次数1, mod6≡3は入次数2を許容)")
for k in depths:
    if k in mod6_dist:
        d = mod6_dist[k]
        print(f"{k:>4} {d.get(1,0):>8.4f} {d.get(3,0):>8.4f} {d.get(5,0):>8.4f} {len(layers[k]):>10,}")

# ============================================================
# 分析4: 各層の入次数分布
# ============================================================

print("\n" + "=" * 70)
print("分析4: 各層の要素の入次数分布")
print("=" * 70)

def compute_indegree(n):
    """奇数nのSyracuse逆像の数（入次数）"""
    # n ≡ 0 (mod 3): 入次数0（前像なし）... だがnは奇数なのでn≡0(mod3)は可能
    # 実際には: 入次数の条件は n mod 3 と n mod 2 に依存
    # 奇数nの前像: m = (n*2^a - 1)/3 が奇数になるaの数
    count = 0
    for a in range(1, 100):
        val = n * (1 << a) - 1
        if val % 3 == 0:
            m = val // 3
            if m > 0 and m % 2 == 1:
                count += 1
    return count

print("\n各層の入次数分類:")
print(f"{'k':>4} {'deg0(%)':>10} {'deg1(%)':>10} {'deg2(%)':>10} {'|層|':>10}")

for k in [0, 1, 5, 10, 15, 20, 25, 30]:
    if k >= len(layers) or len(layers[k]) == 0:
        continue
    # サンプリング（大きい層は全数だと重い）
    sample = list(layers[k])
    if len(sample) > 500:
        import random
        random.seed(42)
        sample = random.sample(sample, 500)

    deg_counts = Counter()
    for n in sample:
        # 簡易入次数判定: n mod 6
        if n % 3 == 0:
            deg_counts[0] += 1
        else:
            # n ≡ 4 (mod 6) は偶数なので奇数では起きない
            # 奇数で n ≡ 1 (mod 6) or n ≡ 5 (mod 6): 入次数1以上
            # 奇数で n ≡ 3 (mod 6): 入次数2以上
            # 正確に言うと: 奇数nに対して
            # n ≡ 1 (mod 2) かつ n ≡ 0 (mod 3) => deg=0
            # それ以外 => deg >= 1
            # nが奇数で n mod 6 == 3 => n ≡ 3 (mod 6), 3|n => deg=0
            if n % 6 == 3:
                deg_counts[0] += 1
            else:
                # n ≡ 1 (mod 6) or n ≡ 5 (mod 6)
                # これらは入次数1（n ≡ 2 mod 3）または
                # 入次数は実際に計算が必要
                # 簡易: 小さいaで前像数を数える
                preimages = inverse_syracuse_odd_bounded(n, n * (1 << 20))
                deg = len(preimages)
                if deg == 0:
                    deg_counts[0] += 1
                elif deg == 1:
                    deg_counts[1] += 1
                else:
                    deg_counts[2] += 1

    total = len(sample)
    d0 = deg_counts.get(0, 0) / total * 100
    d1 = deg_counts.get(1, 0) / total * 100
    d2 = deg_counts.get(2, 0) / total * 100
    print(f"{k:>4} {d0:>10.2f} {d1:>10.2f} {d2:>10.2f} {len(layers[k]):>10,}")

# ============================================================
# 分析5: 層間遷移パターン
# ============================================================

print("\n" + "=" * 70)
print("分析5: 層間遷移パターン (各要素の前像数の分布)")
print("=" * 70)

print("\n各層の要素が次の層に生む子の数の分布:")
print(f"{'k':>4} {'0子(%)':>10} {'1子(%)':>10} {'2子(%)':>10} {'3+子(%)':>10} {'平均':>8}")

for k in range(min(35, MAX_DEPTH)):
    if len(layers[k]) == 0:
        continue

    child_counts = Counter()
    total_children = 0

    for m in layers[k]:
        # mの前像でlayers[k+1]に入ったもの
        children = 0
        if k + 1 < len(layers):
            preimages = inverse_syracuse_odd_bounded(m, MAX_VAL)
            for n, a in preimages:
                if n in layers[k + 1]:
                    children += 1
        child_counts[children] += 1
        total_children += children

    total = len(layers[k])
    avg = total_children / total if total > 0 else 0
    c0 = child_counts.get(0, 0) / total * 100
    c1 = child_counts.get(1, 0) / total * 100
    c2 = child_counts.get(2, 0) / total * 100
    c3p = sum(v for kk, v in child_counts.items() if kk >= 3) / total * 100
    print(f"{k:>4} {c0:>10.2f} {c1:>10.2f} {c2:>10.2f} {c3p:>10.2f} {avg:>8.4f}")

# ============================================================
# 分析6: 累積被覆密度
# ============================================================

print("\n" + "=" * 70)
print("分析6: 累積被覆密度 (奇数のうち何割がT^{-k}(1)に含まれるか)")
print("=" * 70)

# 各閾値Nについて、[1,N]の奇数のうちall_visitedに含まれる割合
thresholds = [100, 1000, 10000, 100000, 1000000]

print(f"\n{'N':>12} {'被覆奇数':>12} {'奇数総数':>12} {'密度':>10}")
for N in thresholds:
    covered = sum(1 for v in all_visited if v <= N and v % 2 == 1)
    total_odd = (N + 1) // 2
    density = covered / total_odd
    print(f"{N:>12,} {covered:>12,} {total_odd:>12,} {density:>10.6f}")

# ============================================================
# 分析7: v2(3n+1) の分布（各層のステップ長）
# ============================================================

print("\n" + "=" * 70)
print("分析7: 各層の v2(3n+1) 分布（Syracuse写像のステップ長）")
print("=" * 70)

print(f"\n{'k':>4} {'v2=1(%)':>10} {'v2=2(%)':>10} {'v2=3(%)':>10} {'v2=4(%)':>10} {'v2>=5(%)':>10} {'平均v2':>10}")

for k in range(min(35, MAX_DEPTH)):
    if len(layers[k]) == 0:
        continue

    v2_counts = Counter()
    v2_sum = 0

    for n in layers[k]:
        v = v2(3 * n + 1)
        v2_counts[v] += 1
        v2_sum += v

    total = len(layers[k])
    avg_v2 = v2_sum / total
    v1 = v2_counts.get(1, 0) / total * 100
    v2_pct = v2_counts.get(2, 0) / total * 100
    v3 = v2_counts.get(3, 0) / total * 100
    v4 = v2_counts.get(4, 0) / total * 100
    v5p = sum(v for kk, v in v2_counts.items() if kk >= 5) / total * 100
    print(f"{k:>4} {v1:>10.2f} {v2_pct:>10.2f} {v3:>10.2f} {v4:>10.2f} {v5p:>10.2f} {avg_v2:>10.4f}")

# ============================================================
# 分析8: 層のサイズの漸近解析
# ============================================================

print("\n" + "=" * 70)
print("分析8: |T^{-k}(1)| の漸近フィット")
print("=" * 70)

# log(|T^{-k}(1)|) vs k の線形回帰
valid_data = [(k, math.log(s)) for k, s in enumerate(layer_sizes) if s > 0 and k >= 5]

if len(valid_data) >= 5:
    ks = [d[0] for d in valid_data]
    logs = [d[1] for d in valid_data]

    n_pts = len(valid_data)
    sum_k = sum(ks)
    sum_log = sum(logs)
    sum_k2 = sum(k**2 for k in ks)
    sum_klog = sum(k * l for k, l in zip(ks, logs))

    slope = (n_pts * sum_klog - sum_k * sum_log) / (n_pts * sum_k2 - sum_k**2)
    intercept = (sum_log - slope * sum_k) / n_pts

    growth_base = math.exp(slope)

    print(f"log(|T^{{-k}}(1)|) ≈ {slope:.6f} * k + {intercept:.6f}")
    print(f"=> |T^{{-k}}(1)| ≈ {math.exp(intercept):.4f} * {growth_base:.6f}^k")
    print(f"実効成長率 (exp(slope)): {growth_base:.6f}")
    print(f"理論値 4/3 = {4/3:.6f}")
    print(f"差: {growth_base - 4/3:.6f}")

    # 残差分析
    residuals = [l - (slope * k + intercept) for k, l in zip(ks, logs)]
    max_res = max(abs(r) for r in residuals)
    avg_res = sum(abs(r) for r in residuals) / len(residuals)
    print(f"残差: 最大={max_res:.6f}, 平均={avg_res:.6f}")

# ============================================================
# 分析9: 層内の数のビット長分布
# ============================================================

print("\n" + "=" * 70)
print("分析9: 各層の要素のビット長統計")
print("=" * 70)

print(f"\n{'k':>4} {'平均bit長':>12} {'最小bit':>10} {'最大bit':>10} {'標準偏差':>12}")

for k in range(min(35, MAX_DEPTH)):
    if len(layers[k]) == 0:
        continue

    bit_lengths = [n.bit_length() for n in layers[k]]
    avg_bl = sum(bit_lengths) / len(bit_lengths)
    min_bl = min(bit_lengths)
    max_bl = max(bit_lengths)
    var = sum((b - avg_bl)**2 for b in bit_lengths) / len(bit_lengths)
    std = math.sqrt(var)

    print(f"{k:>4} {avg_bl:>12.2f} {min_bl:>10} {max_bl:>10} {std:>12.2f}")

# ============================================================
# 分析10: 特殊パターンの検出
# ============================================================

print("\n" + "=" * 70)
print("分析10: 特殊パターン - メルセンヌ数、2^k-1型、等")
print("=" * 70)

# 各層の最小要素の列
print("\n各層の最小要素の列:")
min_elements = []
for k in range(min(35, MAX_DEPTH)):
    if layers[k]:
        m = min(layers[k])
        min_elements.append((k, m))
        print(f"  k={k}: min = {m}")

# 各層に含まれる2^a - 1型の数
print("\n2^a - 1 型 (メルセンヌ数) の出現層:")
for a in range(2, 60):
    m = (1 << a) - 1
    if m in all_visited:
        print(f"  2^{a} - 1 = {m}: 層 {all_visited[m]}")

# 3^a 型の出現
print("\n3^a * k + r 型のパターン:")
for k in range(1, 25):
    if k in [0, 1, 5, 10, 15, 20] and k < len(layers):
        sample = sorted(list(layers[k]))[:10]
        print(f"  k={k}: 最小10個 = {sample}")

# ============================================================
# JSON出力
# ============================================================

output = {
    "layer_sizes": layer_sizes,
    "growth_rates": [r if not math.isnan(r) else None for r in growth_rates],
    "total_nodes": len(all_visited),
    "max_depth": MAX_DEPTH,
    "asymptotic_growth_rate": growth_base if 'growth_base' in dir() else None,
}

print("\n" + "=" * 70)
print("完了。")
print("=" * 70)
