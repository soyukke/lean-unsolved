"""
コラッツグラフ SCC 分析の追加調査:
1. 入次数=2のノードの正確なパターン分析
2. 逆BFS成長率の理論値との比較
3. SCCが全て自明であることの意味の深堀り
4. 拡張Syracuseグラフ（T(n)>Nも許容）のSCC分析
5. 逆方向到達密度の精密計測
"""

import math
from collections import defaultdict

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

# ===== 分析1: 入次数=2のノードの正確なパターン =====
print("=" * 70)
print("分析1: 入次数=2のノードの特徴付け")
print("=" * 70)

N = 100000
in_degree = defaultdict(int)
predecessors = defaultdict(list)

for n in range(1, N + 1):
    target = collatz_step(n)
    if target <= N:
        in_degree[target] += 1
        predecessors[target].append(n)

# 入次数=2のノードの特徴
deg2_nodes = [n for n in range(1, N + 1) if in_degree[n] == 2]

print(f"\n入次数2のノード数: {len(deg2_nodes)}")
print(f"\n最初の30個の入次数2ノードとその前駆:")
for n in deg2_nodes[:30]:
    preds = predecessors[n]
    print(f"  n={n}: 前駆={preds}, n mod 6 = {n % 6}, n mod 3 = {n % 3}")

# mod 6 パターン
mod6_dist = defaultdict(int)
for n in deg2_nodes:
    mod6_dist[n % 6] += 1
print(f"\n入次数2ノードの mod 6 分布:")
for k in sorted(mod6_dist.keys()):
    print(f"  n mod 6 = {k}: {mod6_dist[k]} ({100*mod6_dist[k]/len(deg2_nodes):.1f}%)")

# 入次数=0のノード（葉）の mod 分布
deg0_nodes = [n for n in range(1, N + 1) if in_degree[n] == 0]
mod6_dist0 = defaultdict(int)
for n in deg0_nodes:
    mod6_dist0[n % 6] += 1
print(f"\n入次数0ノードの mod 6 分布:")
for k in sorted(mod6_dist0.keys()):
    print(f"  n mod 6 = {k}: {mod6_dist0[k]} ({100*mod6_dist0[k]/len(deg0_nodes):.1f}%)")

# 入次数=1のノードの mod 分布
deg1_nodes = [n for n in range(1, N + 1) if in_degree[n] == 1]
mod6_dist1 = defaultdict(int)
for n in deg1_nodes:
    mod6_dist1[n % 6] += 1
print(f"\n入次数1ノードの mod 6 分布:")
for k in sorted(mod6_dist1.keys()):
    print(f"  n mod 6 = {k}: {mod6_dist1[k]} ({100*mod6_dist1[k]/len(deg1_nodes):.1f}%)")


# ===== 分析2: 入次数の決定論的パターン =====
print("\n" + "=" * 70)
print("分析2: 入次数の決定論的パターン")
print("=" * 70)

# nの前駆ノードは:
# (a) 2n (偶数化の逆): 常に存在（2n <= N の場合）
# (b) (n-1)/3 (3m+1の逆): n ≡ 1 (mod 3), (n-1)/3 が奇数、かつ (n-1)/3 >= 1

print("\n理論的分析:")
print("  nの前駆は:")
print("  (a) 2n: 2n <= N なら常に存在")
print("  (b) (n-1)/3: n ≡ 1 mod 3, (n-1)/3 が奇数 (つまり n ≡ 4 mod 6)")
print("")
print("  したがって:")
print("  - 入次数0: n > N/2 かつ (nが(b)を満たさない)")
print("  - 入次数1: n <= N/2 かつ (nが(b)を満たさない) OR n > N/2 かつ (nが(b)を満たす)")
print("  - 入次数2: n <= N/2 かつ n ≡ 4 mod 6")

# 検証
count_theory_deg2 = sum(1 for n in range(1, N+1) if n <= N//2 and n % 6 == 4)
count_actual_deg2 = len(deg2_nodes)
print(f"\n理論的入次数2の数 (n <= N/2, n ≡ 4 mod 6): {count_theory_deg2}")
print(f"実際の入次数2の数: {count_actual_deg2}")

# さらに細かくチェック
mismatches = []
for n in range(1, N+1):
    expected_deg = 0
    # (a) 2n <= N?
    if 2 * n <= N:
        expected_deg += 1
    # (b) n ≡ 4 mod 6?
    if n % 6 == 4 and (n - 1) // 3 >= 1:
        expected_deg += 1
    if expected_deg != in_degree[n]:
        mismatches.append((n, expected_deg, in_degree[n]))

print(f"理論と実際の不一致数: {len(mismatches)}")
if mismatches:
    print(f"最初の10個: {mismatches[:10]}")


# ===== 分析3: Syracuse DAG の深さ分布とlog比率の精密分析 =====
print("\n" + "=" * 70)
print("分析3: Syracuse DAG 深さの理論的予測")
print("=" * 70)

# E[log2(T(n)/n)] = -0.41503 (既知)
# これは log(2/3) / log(2) とほぼ同じ？
ratio_theory = math.log(2/3) / math.log(2)
print(f"\nlog(2/3)/log(2) = {ratio_theory:.5f}")
print(f"既知の E[log2(T(n)/n)] = -0.41503")
print(f"差: {abs(ratio_theory - (-0.41503)):.5f}")

# 正しい理論値: E[log2(T(n)/n)] = (log(3/2) + sum_v E[log2(1/2^v)]?)
# 実際は 3/4 の比率に関連
ratio_34 = math.log(3/4) / math.log(2)
print(f"\nlog(3/4)/log(2) = {ratio_34:.5f}")

# Syracuse ステップ数の理論予測
# E[steps to 1] ~ C * log(n), C = 1 / |E[log2(T(n)/n)]| = 1/0.41503
C_theory = 1.0 / 0.41503
print(f"\n1/0.41503 = {C_theory:.4f}")
print(f"実測の平均比率 (ステップ数/log2(n)): ~2.51 (Part 4の結果)")
print(f"理論予測値: {C_theory:.4f}")
print(f"一致度: {100*2.51/C_theory:.1f}%")

# Syracuseではなくコラッツでのステップ数比率
print(f"\nコラッツ(standard)での理論的ステップ数/log2(n) 比:")
print(f"  各ステップの期待縮小率は log2(T(n)/n) ≈ -0.41503")
print(f"  コラッツ1ステップ = 偶数:n/2, 奇数:3n+1")
print(f"  平均として E[log2(next/n)] = 0.5*log2(0.5) + 0.5*log2(1.5+) ≈ ?")

# 直接測定
ratios_collatz = []
for n in range(3, 100001, 2):  # 奇数のみ
    val = 3 * n + 1
    r = math.log2(val / n)
    ratios_collatz.append(r)
avg_odd_ratio = sum(ratios_collatz) / len(ratios_collatz)
print(f"  奇数: E[log2((3n+1)/n)] = {avg_odd_ratio:.6f} (理論: log2(3) = {math.log2(3):.6f})")
print(f"  偶数: log2(n/2 / n) = log2(1/2) = -1.0")
print(f"  合成: 奇数で+log2(3)≈1.585, 偶数で-1.0, 合計は...")


# ===== 分析4: 拡張 Syracuse グラフ（大きな N での非自明SCC探索） =====
print("\n" + "=" * 70)
print("分析4: 拡張Syracuse - 非自明サイクルの探索")
print("=" * 70)

# T(n)がNを超えても追跡してサイクルを探す
print("\n各奇数nについてSyracuse軌道を追跡し、サイクルを探索...")

def find_syracuse_cycle(n, max_iter=500):
    """nからSyracuse軌道を追跡しサイクルを検出"""
    visited = {}
    curr = n
    for i in range(max_iter):
        if curr in visited:
            cycle_start = visited[curr]
            cycle_len = i - cycle_start
            return cycle_start, cycle_len, curr
        visited[curr] = i
        curr = syracuse(curr)
    return None

# n=1..200000の奇数でサイクル検出
cycles_found = set()
for n in range(1, 200001, 2):
    result = find_syracuse_cycle(n)
    if result:
        start, length, cycle_node = result
        if cycle_node != 1:  # 1以外のサイクル
            cycles_found.add((cycle_node, length))

if cycles_found:
    print(f"  1以外のサイクルが見つかった！: {cycles_found}")
else:
    print(f"  n <= 200000 の全奇数について、唯一のサイクルは {1} (自明サイクル)")

# 1のサイクル長を確認
print(f"\n  T(1) = {syracuse(1)}")
# T(1) = (3*1+1)/2^v = 4/4 = 1
print(f"  1は不動点: T(1) = 1")


# ===== 分析5: 逆BFS成長率の理論的分析 =====
print("\n" + "=" * 70)
print("分析5: 逆BFS成長率の理論的根拠")
print("=" * 70)

print("""
逆コラッツ写像の分岐:
  n -> {2n, (2n-1)/3 (if 条件合致)}

理論的成長率:
  各ノードの子の期待数 = 1 + P[(2n-1)/3 が有効]

  n が一様ランダムなら:
  - 2n は常に子
  - (2n-1)/3 が正整数の条件: 2n ≡ 1 mod 3, つまり n ≡ 2 mod 3 (確率 1/3)

  期待子数 = 1 + 1/3 = 4/3 ≈ 1.333

  しかし実測の成長率 ≈ 1.11 はこれより小さい。
  これは境界条件 (n <= N) とBFS層の非一様性による。
""")

# より正確な成長率を大きなNで測定
from collections import deque

def measure_growth_rate(N_limit, max_depth=200):
    """逆BFSの成長率を測定"""
    visited = {1}
    current_layer = {1}
    layer_sizes = [1]

    for d in range(max_depth):
        next_layer = set()
        for n in current_layer:
            # 子1: 2n
            child1 = 2 * n
            if child1 <= N_limit and child1 not in visited:
                visited.add(child1)
                next_layer.add(child1)

            # 子2: (n-1)/3 が条件を満たすなら
            if (n - 1) % 3 == 0 and n > 1:
                child2 = (n - 1) // 3
                if child2 > 0 and child2 % 2 == 1 and child2 <= N_limit and child2 not in visited:
                    visited.add(child2)
                    next_layer.add(child2)

        if not next_layer:
            break
        current_layer = next_layer
        layer_sizes.append(len(next_layer))

    return layer_sizes, len(visited)

for N_test in [10**5, 10**6, 10**7]:
    layers, total = measure_growth_rate(N_test, max_depth=150)
    if len(layers) > 20:
        # 深さ10-50の成長率
        growth_10_50 = [layers[i]/layers[i-1] for i in range(10, min(50, len(layers))) if layers[i-1] > 0]
        avg_g = sum(growth_10_50) / len(growth_10_50) if growth_10_50 else 0

        # 深さ50-100の成長率
        growth_50_100 = [layers[i]/layers[i-1] for i in range(50, min(100, len(layers))) if layers[i-1] > 0]
        avg_g2 = sum(growth_50_100) / len(growth_50_100) if growth_50_100 else 0

        coverage = sum(1 for v in range(1, min(N_test+1, 10**6+1)) if v in range(1, N_test+1)) # rough
        print(f"N={N_test:.0e}: 深さ{len(layers)-1}, 成長率(10-50)={avg_g:.4f}, 成長率(50-100)={avg_g2:.4f}, 到達ノード={total}")


# ===== 分析6: 到達密度の精密測定 =====
print("\n" + "=" * 70)
print("分析6: 逆BFS到達密度の精密測定")
print("=" * 70)

N_density = 10**6
layers_d, total_d = measure_growth_rate(N_density, max_depth=200)

# 各閾値での到達密度
print(f"\n逆BFS (N={N_density}) による到達密度:")
# visited setを再構築
visited_set = {1}
current_layer = {1}
for d in range(200):
    next_layer = set()
    for n in current_layer:
        child1 = 2 * n
        if child1 <= N_density and child1 not in visited_set:
            visited_set.add(child1)
            next_layer.add(child1)
        if (n - 1) % 3 == 0 and n > 1:
            child2 = (n - 1) // 3
            if child2 > 0 and child2 % 2 == 1 and child2 <= N_density and child2 not in visited_set:
                visited_set.add(child2)
                next_layer.add(child2)
    if not next_layer:
        break
    current_layer = next_layer

for threshold in [100, 1000, 10000, 100000, 1000000]:
    count = sum(1 for v in visited_set if v <= threshold)
    print(f"  [1..{threshold:>7}]: {count}/{threshold} = {100*count/threshold:.2f}%")


print("\n" + "=" * 70)
print("追加分析完了")
print("=" * 70)
