#!/usr/bin/env python3
"""
逆Syracuse写像の入次数の精密分析

既知: コラッツグラフでの入次数は {0, 1, 2} のいずれか
疑問: Syracuse写像 T(n) での入次数の正確な分布はどうなるか?

重要な区別:
- コラッツ写像 C(n): n偶数 -> n/2, n奇数 -> 3n+1
- Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} (奇数->奇数)

T^{-1}(m) ∩ [1,N] の入次数は N に依存して際限なく増える。
しかし、C のコラッツグラフでの入次数は {0, 1, 2}。

本スクリプトでは:
1. T^{-1}(m) ∩ [1,N] の入次数分布を N 依存で分析
2. 入次数の理論的期待値と実測値の比較
3. m ≡ 1 (mod 6) vs m ≡ 5 (mod 6) の入次数の差異
4. 「入次数0」のm（N以下で逆像なし）の密度分析
5. T^{-1}(m)の最小要素 n_min(m) の分布
"""

import math
from collections import Counter, defaultdict

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

# ============================================================
# 1. 入次数分布の N 依存性
# ============================================================

print("=" * 70)
print("1. 入次数分布の N 依存性")
print("=" * 70)

for N in [100, 1000, 10000, 100000]:
    indegree = Counter()
    for n in range(1, N + 1, 2):
        m = syracuse(n)
        indegree[m] += 1

    deg_dist = Counter(indegree.values())
    max_deg = max(indegree.values()) if indegree else 0

    # 奇数m ≤ N のうち逆像ありの割合
    total_odd = (N + 1) // 2
    reached_count = len(indegree)

    # 理論値: |T^{-1}(m) ∩ [1,N]| ≈ log2(3N/m) / 2 の平均
    # m ≤ N の奇数 m に対する平均入次数 = (N/2) / reached_count
    avg_deg = sum(indegree.values()) / len(indegree) if indegree else 0

    print(f"\n  N = {N:>7d}:")
    print(f"    max入次数 = {max_deg}")
    print(f"    平均入次数 = {avg_deg:.3f}")
    print(f"    像に現れるm数 = {reached_count} / {total_odd} odd nums = {reached_count/total_odd*100:.1f}%")
    deg_str = ", ".join(f"{d}:{c}" for d, c in sorted(deg_dist.items())[:8])
    print(f"    分布: {deg_str}{'...' if len(deg_dist) > 8 else ''}")

# ============================================================
# 2. m mod 6 別の入次数0の密度精密分析
# ============================================================

print()
print("=" * 70)
print("2. 入次数0の密度: m ≡ 1(mod6) vs m ≡ 5(mod6)")
print("=" * 70)

# 理論分析:
# m ≡ 1 (mod 6): 最小逆像 n_min = (4m-1)/3
#   n_min ≤ N <=> m ≤ (3N+1)/4
#   なので m > 3N/4 の場合、[1,N]内に逆像なし
#
# m ≡ 5 (mod 6): 最小逆像 n_min = (2m-1)/3
#   n_min ≤ N <=> m ≤ (3N+1)/2
#   なので m > 3N/2 のときのみ逆像なし（m ≤ N なら常に逆像あり）

for N in [1000, 10000, 100000]:
    mod1_total = 0
    mod1_unreached = 0
    mod5_total = 0
    mod5_unreached = 0

    reached = set()
    for n in range(1, N + 1, 2):
        reached.add(syracuse(n))

    for m in range(1, N + 1, 2):
        if m % 3 == 0:
            continue
        if m % 6 == 1:
            mod1_total += 1
            if m not in reached:
                mod1_unreached += 1
        elif m % 6 == 5:
            mod5_total += 1
            if m not in reached:
                mod5_unreached += 1

    # 理論予測
    # m ≡ 1 (mod 6): 3N/4 < m ≤ N のm数 = N/4 * (1/3) ≈ N/12
    # m ≡ 5 (mod 6): 3N/2 < m ≤ N => 常にm ≤ N < 3N/2 => 全てreached
    theory_mod1_unreached = sum(1 for m in range(1, N+1, 2) if m % 6 == 1 and m > 3*N//4)

    print(f"\n  N = {N}:")
    print(f"    m ≡ 1 (mod 6): unreached = {mod1_unreached}/{mod1_total} ({mod1_unreached/mod1_total*100:.1f}%)")
    print(f"      理論予測 (m > 3N/4): {theory_mod1_unreached}")
    print(f"    m ≡ 5 (mod 6): unreached = {mod5_unreached}/{mod5_total} ({mod5_unreached/mod5_total*100:.1f}%)")
    print(f"      理論予測: 0 (n_min = (2m-1)/3 < m ≤ N)")

# ============================================================
# 3. 最小逆像 n_min(m) の閉じた公式と分布
# ============================================================

print()
print("=" * 70)
print("3. 最小逆像 n_min(m) の閉じた公式")
print("=" * 70)

print("""
定理: 奇数 m に対する最小逆像 n_min(m):

  m ≡ 1 (mod 6): n_min(m) = (4m - 1) / 3    (j=2)
  m ≡ 5 (mod 6): n_min(m) = (2m - 1) / 3    (j=1)
  m ≡ 0 (mod 3): 逆像なし

確認: n_min は必ず奇数か?
  m ≡ 1 (mod 6): 4m ≡ 4 (mod 6), 4m-1 ≡ 3 (mod 6), (4m-1)/3 ≡ 1 (mod 2) OK
  m ≡ 5 (mod 6): 2m ≡ 10 ≡ 4 (mod 6), 2m-1 ≡ 3 (mod 6), (2m-1)/3 ≡ 1 (mod 2) OK

比率 n_min(m) / m:
  m ≡ 1 (mod 6): n_min/m → 4/3 ≈ 1.333...
  m ≡ 5 (mod 6): n_min/m → 2/3 ≈ 0.667...
""")

# 数値検証
errors = 0
for m in range(1, 10000, 2):
    if m % 3 == 0:
        continue
    if m % 6 == 1:
        n_theory = (4 * m - 1) // 3
    else:  # m % 6 == 5
        n_theory = (2 * m - 1) // 3

    # 検証: T(n_theory) == m
    actual = syracuse(n_theory)
    if actual != m:
        print(f"  ERROR: m={m}, n_theory={n_theory}, T(n_theory)={actual}")
        errors += 1

print(f"n_min の閉公式検証: m=1..9999 (奇数, 3∤m) 全 {(10000//6)*2} 件, エラー = {errors}")

# ============================================================
# 4. 入次数の理論的期待値
# ============================================================

print()
print("=" * 70)
print("4. 有界入次数の理論的期待値")
print("=" * 70)

print("""
T^{-1}(m) ∩ [1,N] のサイズの理論値:

  m ≡ 1 (mod 6): |T^{-1}(m) ∩ [1,N]| = floor((J_max - 2) / 2) + 1
    where J_max = floor(log2((3N+1)/m))
    = floor(log2((3N+1)/m) / 2)   (j_max >= 2 のとき)

  m ≡ 5 (mod 6): |T^{-1}(m) ∩ [1,N]| = floor((J_max - 1) / 2) + 1
    where J_max = floor(log2((3N+1)/m))
    = floor((log2((3N+1)/m) + 1) / 2)  (j_max >= 1 のとき)
""")

# 精密検証
N_test = 100000
errors = 0
for m in range(1, 1000, 2):
    if m % 3 == 0:
        continue

    # 実際の逆像
    actual = 0
    if m % 6 == 1:
        j = 2
        while True:
            n = (m * (1 << j) - 1) // 3
            if n > N_test:
                break
            actual += 1
            j += 2
    else:  # m % 6 == 5
        j = 1
        while True:
            n = (m * (1 << j) - 1) // 3
            if n > N_test:
                break
            actual += 1
            j += 2

    # 閉公式
    if 3 * N_test + 1 <= m:
        formula = 0
    else:
        J_max = math.floor(math.log2((3 * N_test + 1) / m))
        if m % 6 == 1:
            if J_max < 2:
                formula = 0
            else:
                formula = (J_max - 2) // 2 + 1
        else:  # m % 6 == 5
            if J_max < 1:
                formula = 0
            else:
                formula = (J_max - 1) // 2 + 1

    if actual != formula:
        print(f"  m={m}: actual={actual}, formula={formula} [MISMATCH]")
        errors += 1

print(f"閉公式精密検証: 全テストケースでエラー = {errors}")

# 平均入次数の理論予測
print(f"\nN={N_test} での平均入次数の理論予測:")
# 平均値 = (1/count_m) * sum_{m: odd, m≢0(3), m≤N} floor(log2(3N/m)/2)
# ≈ integral from 1 to N of (log2(3N/x)/2) * (2/3) dx / N
# = (2/3N) * integral_1^N log2(3N/x)/2 dx
# = (1/3N) * integral_1^N (log2(3N) - log2(x)) dx
# = (1/3N) * [N*log2(3N) - integral_1^N log2(x) dx]
# = (1/3N) * [N*log2(3N) - (N*log2(N) - N/ln2 + 1/ln2)]
# = (1/3) * [log2(3N) - log2(N) + 1/ln2 - 1/(N*ln2)]
# = (1/3) * [log2(3) + 1/ln2]
# ≈ (1/3) * [1.585 + 1.443] = (1/3) * 3.028 ≈ 1.009

theory_avg = (math.log2(3) + 1/math.log(2)) / 3
print(f"  理論予測（漸近）: {theory_avg:.4f}")

# 実測
indegree = Counter()
for n in range(1, N_test + 1, 2):
    indegree[syracuse(n)] += 1
actual_avg = sum(indegree.values()) / len(indegree)
print(f"  実測値: {actual_avg:.4f}")

# ============================================================
# 5. 新発見: m ≡ 5 (mod 6) は常に入次数 >= 1
# ============================================================

print()
print("=" * 70)
print("5. 重要な性質: m ≡ 5 (mod 6) は [1,m] 内に必ず逆像を持つ")
print("=" * 70)

print("""
定理: m ≡ 5 (mod 6) かつ m >= 5 のとき、T^{-1}(m) ∩ [1, m-1] ≠ 空

証明:
  n_min = (2m - 1) / 3
  m ≡ 5 (mod 6) のとき m >= 5
  n_min = (2m-1)/3 < m  <=>  2m-1 < 3m  <=>  m > -1  (常に成立)

  また n_min >= 1 <=> 2m-1 >= 3 <=> m >= 2 (常に成立)

  さらに T(n_min) = m を確認:
  3*n_min + 1 = 3*(2m-1)/3 + 1 = 2m-1+1 = 2m
  v2(2m) = 1 (mは奇数)
  T(n_min) = 2m / 2 = m  Q.E.D.

系: m ≡ 5 (mod 6) のとき、n = (2m-1)/3 は m の唯一の「自明な逆像」。
    この逆像では v2(3n+1) = 1、つまり1回だけ2で割る（最小回数）。

対照的に:
  m ≡ 1 (mod 6) のとき、n_min = (4m-1)/3 > m
  → m 自身より小さい逆像が存在するとは限らない！
""")

# 数値検証
print("検証: m ≡ 5 (mod 6) で n_min < m を確認")
all_ok = True
for m in range(5, 10000, 6):
    n_min = (2 * m - 1) // 3
    if n_min >= m:
        print(f"  FAIL: m={m}, n_min={n_min} >= m")
        all_ok = False
    if syracuse(n_min) != m:
        print(f"  FAIL: T({n_min}) = {syracuse(n_min)} != {m}")
        all_ok = False
if all_ok:
    print(f"  OK: m=5,11,...,9995 全て n_min < m かつ T(n_min)=m")

print("\n検証: m ≡ 1 (mod 6) で n_min > m を確認")
all_ok = True
for m in range(1, 10000, 6):
    n_min = (4 * m - 1) // 3
    if n_min <= m:
        print(f"  NOTE: m={m}, n_min={n_min} <= m")
        all_ok = False
if all_ok:
    print(f"  OK: m=1,7,...,9997 全て n_min > m")
else:
    print("  (上記は m=1 の特殊ケース)")

# ============================================================
# 6. 逆Syracuse木の分岐因子
# ============================================================

print()
print("=" * 70)
print("6. 逆Syracuse木の分岐因子の理論分析")
print("=" * 70)

print("""
逆Syracuse木（根=1から T^{-1} を反復適用）の分岐因子:

深さ k での新ノード数を B(k) とすると:
  B(k) / B(k-1) → ? (成長率)

各ノード m の分岐数 = |T^{-1}(m) ∩ [1,N]|
  m ≡ 0 (mod 3): 分岐数 = 0
  m ≡ 1 (mod 6): 分岐数 ≈ log2(3N/m) / 2
  m ≡ 5 (mod 6): 分岐数 ≈ (log2(3N/m) + 1) / 2

m mod 3 の分布:
  奇数 m のうち m ≡ 0 (mod 3) は 1/3
  残り 2/3 が逆像を持つ

平均分岐因子（N → ∞ での漸近）:
  各世代の m の 1/3 は分岐0（行き止まり）
  残り 2/3 は各々 ~log(N)/2 の分岐を持つ
  有効分岐因子 ≈ (2/3) * log2(3N/m_avg) / 2
""")

# 実測
N_bound = 10**6
current = {1}
growth = []
for depth in range(1, 12):
    next_nodes = set()
    for m in current:
        if m % 3 == 0:
            continue
        if m % 6 == 1:
            j = 2
            while True:
                n = (m * (1 << j) - 1) // 3
                if n > N_bound:
                    break
                next_nodes.add(n)
                j += 2
        else:  # m % 6 == 5
            j = 1
            while True:
                n = (m * (1 << j) - 1) // 3
                if n > N_bound:
                    break
                next_nodes.add(n)
                j += 2

    current = next_nodes
    growth.append(len(current))

print(f"\n根=1からの逆Syracuse木 (N_bound={N_bound}):")
print(f"  深さ:  {list(range(1, len(growth)+1))}")
print(f"  ノード数: {growth}")
ratios = [f"{growth[i]/growth[i-1]:.2f}" for i in range(1, len(growth)) if growth[i-1] > 0]
print(f"  成長率: {ratios}")

# mod 3 分布の確認
for depth_check in [5, 8]:
    if depth_check <= len(growth):
        # 再計算
        current_check = {1}
        for d in range(depth_check):
            next_nodes = set()
            for m in current_check:
                if m % 3 == 0:
                    continue
                if m % 6 == 1:
                    j = 2
                    while True:
                        n = (m * (1 << j) - 1) // 3
                        if n > N_bound:
                            break
                        next_nodes.add(n)
                        j += 2
                else:
                    j = 1
                    while True:
                        n = (m * (1 << j) - 1) // 3
                        if n > N_bound:
                            break
                        next_nodes.add(n)
                        j += 2
            current_check = next_nodes

        mod3_dist = Counter(n % 3 for n in current_check)
        mod6_dist = Counter(n % 6 for n in current_check)
        total = len(current_check)
        print(f"\n  深さ{depth_check}での mod 3 分布: ", end="")
        for r in [0, 1, 2]:
            print(f"{r}:{mod3_dist[r]/total*100:.1f}% ", end="")
        print(f"\n  深さ{depth_check}での mod 6 分布: ", end="")
        for r in [1, 3, 5]:
            print(f"{r}:{mod6_dist[r]/total*100:.1f}% ", end="")
        print()

print()
print("=" * 70)
print("分析完了")
print("=" * 70)
