#!/usr/bin/env python3
"""
Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の逆像分岐分析 (v3: 二方向分析)

方針A: [1,N]に制限した逆木 - 有限区間での被覆密度
方針B: 無制限逆木のk=1..10の精密構造分析（前回データ活用）
方針C: 小さいNでの完全分析（mod分布、遷移パターン等）
"""

import math
from collections import defaultdict, Counter
import time
import sys

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse_bounded(m, max_n):
    """T(n) = m となる奇数 n で n <= max_n のものを全て返す"""
    if m % 3 == 0:
        return []
    results = []
    if m % 3 == 1:
        start_a, step = 2, 2
    else:
        start_a, step = 1, 2
    a = start_a
    while True:
        val = m * (1 << a) - 1
        n_cand = val // 3
        if n_cand > max_n:
            break
        if val % 3 == 0 and n_cand > 0 and n_cand % 2 == 1:
            results.append((n_cand, a))
        a += step
    return results

# ============================================================
# 方針A: [1, N] に制限した逆木（BFS）
# ============================================================
print("=" * 70)
print("方針A: [1, N] に制限した逆像木")
print("=" * 70)

def build_bounded_inverse_tree(root, N, max_depth):
    """[1, N]の奇数のみで逆像木を構築"""
    layers = [set() for _ in range(max_depth + 1)]
    layers[0] = {root}
    all_visited = {root: 0}

    for k in range(1, max_depth + 1):
        new_layer = set()
        for m in layers[k-1]:
            for n, a in inverse_syracuse_bounded(m, N):
                if n not in all_visited:
                    new_layer.add(n)
                    all_visited[n] = k
        layers[k] = new_layer
        if not new_layer:
            break  # 新しいノードがなければ終了

    return layers, all_visited

# 異なるNで実験
for N in [10**3, 10**4, 10**5, 10**6, 10**7]:
    t0 = time.time()
    layers, visited = build_bounded_inverse_tree(1, N, 100)

    # 有効な層数
    max_k = max(k for k in range(len(layers)) if len(layers[k]) > 0)

    total_odd = len([x for x in range(1, N+1, 2)])
    covered = len(visited)
    density = covered / total_odd

    # 成長率
    sizes = [len(layers[k]) for k in range(max_k + 1)]
    rates = []
    for k in range(1, max_k + 1):
        if sizes[k-1] > 0 and sizes[k] > 0:
            rates.append(sizes[k] / sizes[k-1])

    t1 = time.time()
    print(f"\nN = {N:>10,}:")
    print(f"  被覆奇数: {covered:>10,} / {total_odd:>10,} = {density:.6f}")
    print(f"  最大深さ: {max_k}")
    print(f"  層サイズ(最初10個): {sizes[:min(10, len(sizes))]}")
    if rates:
        print(f"  成長率(最初10個): {[f'{r:.3f}' for r in rates[:10]]}")
        avg_rate = sum(rates) / len(rates)
        print(f"  平均成長率: {avg_rate:.4f}")
    print(f"  時間: {t1-t0:.2f}s")

# ============================================================
# 方針B: N=10^6での詳細分析
# ============================================================
print("\n" + "=" * 70)
print("方針B: N=10^6 での詳細分析")
print("=" * 70)

N = 10**6
layers, visited = build_bounded_inverse_tree(1, N, 200)
max_k = max(k for k in range(len(layers)) if len(layers[k]) > 0)

# 層サイズと成長率
print(f"\n{'k':>4} {'|層|':>10} {'成長率':>10} {'累積':>10} {'密度':>10}")
print("-" * 50)
cumulative = 0
total_odd = (N + 1) // 2

for k in range(max_k + 1):
    size = len(layers[k])
    cumulative += size
    if k > 0 and len(layers[k-1]) > 0:
        rate = size / len(layers[k-1])
        rate_str = f"{rate:.4f}"
    else:
        rate_str = "   ---"
    density = cumulative / total_odd
    print(f"{k:>4} {size:>10,} {rate_str:>10} {cumulative:>10,} {density:>10.6f}")

# ============================================================
# 方針C: mod 分布の詳細
# ============================================================
print("\n" + "=" * 70)
print("方針C: mod 分布の詳細 (N=10^6)")
print("=" * 70)

# mod 6 分布
print("\n--- mod 6 分布 ---")
print(f"{'k':>4} {'≡1(6)':>8} {'≡3(6)':>8} {'≡5(6)':>8} {'|層|':>8}")
for k in range(min(max_k + 1, 50)):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    c1 = sum(1 for n in layers[k] if n % 6 == 1) / total
    c3 = sum(1 for n in layers[k] if n % 6 == 3) / total
    c5 = sum(1 for n in layers[k] if n % 6 == 5) / total
    print(f"{k:>4} {c1:>8.4f} {c3:>8.4f} {c5:>8.4f} {total:>8,}")

# mod 8 分布
print("\n--- mod 8 分布 ---")
print(f"{'k':>4} {'≡1':>7} {'≡3':>7} {'≡5':>7} {'≡7':>7}")
for k in range(min(max_k + 1, 50)):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    vals = [sum(1 for n in layers[k] if n % 8 == r) / total for r in [1, 3, 5, 7]]
    print(f"{k:>4} {vals[0]:>7.4f} {vals[1]:>7.4f} {vals[2]:>7.4f} {vals[3]:>7.4f}")

# mod 16 分布
print("\n--- mod 16 分布 (安定した層 k >= 10) ---")
print(f"{'k':>4} {'≡1':>6} {'≡3':>6} {'≡5':>6} {'≡7':>6} {'≡9':>6} {'≡11':>6} {'≡13':>6} {'≡15':>6}")
for k in range(10, min(max_k + 1, 50)):
    if len(layers[k]) < 10:
        continue
    total = len(layers[k])
    vals = [sum(1 for n in layers[k] if n % 16 == r) / total for r in [1,3,5,7,9,11,13,15]]
    print(f"{k:>4} " + " ".join(f"{v:>6.3f}" for v in vals))

# 理論的一様分布との比較
print("\n理論的一様分布(奇数のmod 16): 各1/8 = 0.1250")

# ============================================================
# 方針D: 層間遷移パターン
# ============================================================
print("\n" + "=" * 70)
print("方針D: 層間遷移パターン")
print("=" * 70)

print(f"\n各層の要素が次の層に生む子の数分布:")
print(f"{'k':>4} {'0子':>8} {'1子':>8} {'2子':>8} {'3+子':>8} {'平均':>8}")

for k in range(min(40, max_k)):
    if len(layers[k]) == 0:
        continue

    child_dist = Counter()
    total_children = 0

    for m in layers[k]:
        children_in_next = 0
        for n, a in inverse_syracuse_bounded(m, N):
            if n in layers[k + 1]:
                children_in_next += 1
        child_dist[children_in_next] += 1
        total_children += children_in_next

    total = len(layers[k])
    if total == 0:
        continue
    avg = total_children / total
    c0 = child_dist.get(0, 0) / total * 100
    c1 = child_dist.get(1, 0) / total * 100
    c2 = child_dist.get(2, 0) / total * 100
    c3p = sum(v for kk, v in child_dist.items() if kk >= 3) / total * 100
    print(f"{k:>4} {c0:>7.1f}% {c1:>7.1f}% {c2:>7.1f}% {c3p:>7.1f}% {avg:>8.4f}")

# ============================================================
# 方針E: v2(3n+1)分布
# ============================================================
print("\n" + "=" * 70)
print("方針E: v2(3n+1) 分布")
print("=" * 70)

print(f"{'k':>4} {'v=1':>8} {'v=2':>8} {'v=3':>8} {'v=4':>8} {'v>=5':>8} {'平均':>8}")
for k in range(min(max_k + 1, 50)):
    if len(layers[k]) == 0:
        continue
    total = len(layers[k])
    vc = Counter()
    vs = 0
    for n in layers[k]:
        v = v2(3 * n + 1)
        vc[v] += 1
        vs += v
    avg = vs / total
    vals = [vc.get(i, 0) / total * 100 for i in range(1, 5)]
    v5p = sum(v for kk, v in vc.items() if kk >= 5) / total * 100
    print(f"{k:>4} {vals[0]:>7.1f}% {vals[1]:>7.1f}% {vals[2]:>7.1f}% {vals[3]:>7.1f}% {v5p:>7.1f}% {avg:>8.4f}")

# 理論分布
print(f"\n理論分布 v2(3n+1) for random odd n:")
print(f"  P(v=k) = 1/2^k for k >= 1")
print(f"  v=1: 50%, v=2: 25%, v=3: 12.5%, v=4: 6.25%, v>=5: 6.25%")
print(f"  期待値: 2.0")

# ============================================================
# 方針F: 逆木に到達しない奇数の分析
# ============================================================
print("\n" + "=" * 70)
print("方針F: N=10^6で逆木に到達しない奇数（存在すればコラッツ予想の反例候補）")
print("=" * 70)

unreached = []
for n in range(1, N + 1, 2):
    if n not in visited:
        unreached.append(n)

print(f"到達しない奇数の数: {len(unreached)}")
if unreached:
    print(f"最初の20個: {unreached[:20]}")

    # これらが本当に1に到達するか確認
    print("\nこれらのSyracuse軌道が1に到達するか確認:")
    for n in unreached[:10]:
        x = n
        steps = 0
        while x != 1 and steps < 1000:
            x = syracuse(x)
            steps += 1
        status = f"→1 ({steps}ステップ)" if x == 1 else f"未到達 ({steps}ステップ後 x={x})"
        print(f"  n={n}: {status}")

    if len(unreached) > 0:
        print(f"\n到達しない奇数はBFS深さが{max_k}では足りない奇数。")
        print(f"これらは到達距離が > {max_k} の奇数。")

        # 到達しない奇数のmod分布
        print(f"\n到達しない奇数の mod 6 分布:")
        ur_mod6 = Counter(n % 6 for n in unreached)
        for r in [1, 3, 5]:
            print(f"  ≡{r} (mod 6): {ur_mod6.get(r, 0)} ({ur_mod6.get(r, 0)/len(unreached)*100:.1f}%)")

# ============================================================
# 方針G: 到達距離の分布
# ============================================================
print("\n" + "=" * 70)
print("方針G: 到達距離(1からの逆BFS深さ)の分布")
print("=" * 70)

depth_dist = Counter(visited.values())
print(f"\n{'深さk':>8} {'ノード数':>10} {'割合(%)':>10}")
for k in sorted(depth_dist.keys()):
    count = depth_dist[k]
    pct = count / len(visited) * 100
    print(f"{k:>8} {count:>10,} {pct:>10.2f}")

# 平均到達距離
depths = list(visited.values())
avg_depth = sum(depths) / len(depths)
max_depth = max(depths)
print(f"\n平均到達距離: {avg_depth:.2f}")
print(f"最大到達距離: {max_depth}")

# ============================================================
# 方針H: 成長率の収束と揺らぎ分析
# ============================================================
print("\n" + "=" * 70)
print("方針H: 有限[1,N]での実効成長率の収束")
print("=" * 70)

# 異なるNで成長率がどう変わるか
print(f"\n{'N':>10} {'平均成長率':>12} {'最大層深さ':>12} {'被覆密度':>10}")
for N_test in [1000, 5000, 10000, 50000, 100000, 500000, 1000000]:
    layers_t, visited_t = build_bounded_inverse_tree(1, N_test, 200)
    max_k_t = max(k for k in range(len(layers_t)) if len(layers_t[k]) > 0)
    sizes_t = [len(layers_t[k]) for k in range(max_k_t + 1)]

    rates_t = []
    for k in range(1, max_k_t + 1):
        if sizes_t[k-1] > 0 and sizes_t[k] > 0:
            rates_t.append(sizes_t[k] / sizes_t[k-1])

    # ピーク前の成長率のみ（減衰フェーズを除く）
    peak_k = sizes_t.index(max(sizes_t))
    early_rates = rates_t[:max(1, peak_k)]
    avg_rate = sum(early_rates) / len(early_rates) if early_rates else 0

    total_odd = (N_test + 1) // 2
    density = len(visited_t) / total_odd

    print(f"{N_test:>10,} {avg_rate:>12.6f} {max_k_t:>12} {density:>10.6f}")

# ============================================================
# 方針I: 無制限木の成長率（小さいkのみ）
# ============================================================
print("\n" + "=" * 70)
print("方針I: 無制限逆木の成長率 (k=1..9, v2データ出力参照)")
print("=" * 70)

# v2の出力から得られたデータ
unbounded_sizes = [1, 13, 93, 618, 4158, 28063, 190437, 1301998, 8967246, 62176944, 433780783]
print(f"\n{'k':>4} {'|T^{-k}(1)|':>15} {'成長率':>12} {'log2(成長率)':>14}")
for k in range(len(unbounded_sizes)):
    s = unbounded_sizes[k]
    if k > 0:
        rate = s / unbounded_sizes[k-1]
        log_rate = math.log2(rate)
    else:
        rate = float('nan')
        log_rate = float('nan')
    print(f"{k:>4} {s:>15,} {rate:>12.4f} {log_rate:>14.4f}")

# 漸近フィット
valid = [(k, math.log(s)) for k, s in enumerate(unbounded_sizes) if k >= 2]
ks = [d[0] for d in valid]; logs = [d[1] for d in valid]
n_p = len(valid); sk = sum(ks); sl = sum(logs); sk2 = sum(x**2 for x in ks); skl = sum(x*y for x,y in zip(ks, logs))
slope = (n_p * skl - sk * sl) / (n_p * sk2 - sk**2)
intercept = (sl - slope * sk) / n_p
ub_growth = math.exp(slope)

print(f"\n無制限木の漸近成長率: {ub_growth:.6f}")
print(f"log(成長率): {slope:.6f}")
print(f"比較: log(4/3) = {math.log(4/3):.6f}")
print(f"比較: 実測/log(4/3) = {slope / math.log(4/3):.4f}")

# ============================================================
# 方針J: 無制限vs有限の成長率ギャップの理論的考察
# ============================================================
print("\n" + "=" * 70)
print("方針J: 理論的考察")
print("=" * 70)

print("""
無制限逆木の成長率の解析:

各奇数mに対する前像数の期待値:
  m ≡ 0 (mod 3): 前像0個
  m ≡ 1 (mod 3): 前像は a=2,4,6,... で n=(m*2^a-1)/3
  m ≡ 2 (mod 3): 前像は a=1,3,5,... で n=(m*2^a-1)/3

各aに対して1つの前像が存在し、前像のサイズは m*2^a/3 程度。
→ 無制限では前像数は無限大！

有限[1,N]に制限すると:
  n = (m*2^a-1)/3 <= N  =>  a <= log2(3N/m)
  前像数 ≈ floor(log2(3N/m) / 2)  (aのステップ幅2で)

つまり有限区間では:
  - 小さいmほど多くの前像
  - 大きいmほど少ない前像
  - 平均前像数は log2(N) のオーダーで成長

無制限の場合、成長率がlog(4/3)のk倍ではなく、
実際には各ステップで前像が多数生成されるため、指数的に大きい成長率になる。

重要な洞察:
  有限[1,N]逆木の「被覆密度が1に近づく」ことと、
  無制限逆木の「成長率が4/3を超える」ことは、
  コラッツ予想の正しさの異なる側面を反映している。
""")

# ============================================================
# 最終まとめ JSON出力用
# ============================================================
print("\n" + "=" * 70)
print("JSON出力用サマリー")
print("=" * 70)

summary = {
    "bounded_N1M": {
        "N": 1000000,
        "covered_odd": len(visited),
        "total_odd": (N+1)//2,
        "density": len(visited) / ((N+1)//2),
        "max_depth": max_k,
        "avg_depth": avg_depth,
    },
    "unbounded_sizes_k0_10": unbounded_sizes,
    "unbounded_growth_rate": ub_growth,
    "theory_growth_rate": 4/3,
}

import json
print(json.dumps(summary, indent=2))

print("\n完了。")
