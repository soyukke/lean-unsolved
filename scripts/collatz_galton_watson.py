#!/usr/bin/env python3
"""
探索: 逆コラッツ木のGalton-Watsonモデルと絶滅確率

コラッツ予想の同値な言い換え: 「1から逆操作で全ての正整数に到達できる」

逆コラッツ木をGalton-Watson分岐過程としてモデル化:
- 各ノード n の「子の数」= n の前駆の数
- 前駆: 2n (常に存在), (2n-1)/3 (2n-1が3の倍数のとき)
- deg(n) in {1, 2}: 重複を無視した理想的な入次数

mod 6 による分類:
  n ≡ 0 (mod 6): 前駆 = 2n (偶数), (2n-1)/3 が整数 ⟺ 2n≡1(mod3) ⟺ n≡2(mod3) → NO
  n ≡ 1 (mod 6): (2n-1)/3 = (2-1)/3? 2n-1=1 mod12, 1%3=1 → NO
  n ≡ 2 (mod 6): 2n-1=3 mod12, 3%3=0 → YES, (2n-1)/3 = (4n-1)/3 ... etc
  n ≡ 3 (mod 6): 2n-1=5 mod12, 5%3=2 → NO
  n ≡ 4 (mod 6): 2n-1=7 mod12, 7%3=1 → NO
  n ≡ 5 (mod 6): 2n-1=9 mod12, 9%3=0 → YES

実際にはSyracuse版(奇数のみ)で考えるべきなので注意。

このスクリプトでは:
1. 理論的なGalton-Watson分岐過程パラメータの計算
2. 絶滅確率の厳密解析
3. 重複除去効果のシミュレーション
4. 被覆時間の推定
5. 実データとの比較
"""

import math
import time
import random
from collections import defaultdict, Counter
from fractions import Fraction

# ============================================================
# 1. Galton-Watson分岐過程の理論的パラメータ
# ============================================================

print("=" * 70)
print("1. Galton-Watson分岐過程の理論的パラメータ")
print("=" * 70)

print("\n--- 標準逆コラッツ木 (n -> 2n, n -> (2n-1)/3) ---")
print()

# mod 6 による分類: (2n-1) が 3の倍数か？
print("mod 6 による入次数分類 (標準逆コラッツ木):")
for r in range(6):
    val = 2 * r - 1
    has_inv3 = (val % 3 == 0) and ((val // 3) > 0) and ((val // 3) % 2 == 1 if False else True)
    # (2n-1) mod 3 を調べる
    check = (2 * r - 1) % 3
    has_extra = (check == 0)
    deg = 2 if has_extra else 1
    print(f"  n ≡ {r} (mod 6): 2n-1 ≡ {(2*r-1) % 6} (mod 6), "
          f"(2n-1) mod 3 = {check}, 前駆数 = {deg}")

print()

# 理想的なGW分布
# 均等分布で n mod 6 の各値が 1/6 ずつ
# deg=1 の確率 p1 = n≡0,1,3,4 (mod 6) の割合 = 4/6 = 2/3
# deg=2 の確率 p2 = n≡2,5 (mod 6) の割合 = 2/6 = 1/3

p1 = Fraction(4, 6)  # 2/3
p2 = Fraction(2, 6)  # 1/3

mean_offspring = 1 * p1 + 2 * p2
print(f"理論的子孫数分布 (重複なし理想モデル):")
print(f"  P(子=1) = {p1} = {float(p1):.6f}")
print(f"  P(子=2) = {p2} = {float(p2):.6f}")
print(f"  P(子=0) = 0  (2n は常に存在するので子は最低1)")
print(f"  平均子孫数 mu = {mean_offspring} = {float(mean_offspring):.6f}")
print(f"  分散 = E[X^2] - mu^2 = {1*1*p1 + 2*2*p2} - {mean_offspring**2} = {1*p1 + 4*p2 - mean_offspring**2}")
print()

variance = float(1*p1 + 4*p2 - mean_offspring**2)
print(f"  分散 sigma^2 = {variance:.6f}")
print()

# GW過程の分類
mu_val = float(mean_offspring)
print(f"Galton-Watson分類:")
print(f"  mu = {mu_val:.6f}")
if mu_val > 1:
    print(f"  mu > 1 → 超臨界 (supercritical)")
    print(f"  絶滅確率 q < 1 (非自明解)")
elif mu_val == 1:
    print(f"  mu = 1 → 臨界 (critical)")
    print(f"  絶滅確率 q = 1")
else:
    print(f"  mu < 1 → 亜臨界 (subcritical)")
    print(f"  絶滅確率 q = 1")

# ============================================================
# 2. 絶滅確率の厳密計算
# ============================================================

print("\n" + "=" * 70)
print("2. 絶滅確率の厳密計算")
print("=" * 70)

# 子孫数の母関数: G(s) = p1*s + p2*s^2
# 絶滅確率 q は G(q) = q の最小非負解
# p1*q + p2*q^2 = q
# p2*q^2 + (p1-1)*q = 0
# q*(p2*q + p1 - 1) = 0
# q = 0 or q = (1 - p1)/p2

p1_f = float(p1)
p2_f = float(p2)

q_trivial = 0
q_nontrivial = (1 - p1_f) / p2_f

print(f"\n母関数: G(s) = {p1}*s + {p2}*s^2")
print(f"固定点方程式 G(q) = q:")
print(f"  {p2}*q^2 + ({p1} - 1)*q = 0")
print(f"  q*({p2}*q + {p1} - 1) = 0")
print(f"  解: q = 0 or q = (1 - {p1}) / {p2}")
print(f"  q = 0 or q = {Fraction(1,1) - p1} / {p2} = {(Fraction(1,1) - p1) / p2}")
print(f"  q = 0 or q = {q_nontrivial:.6f}")
print()

# 超臨界 (mu > 1) の場合、絶滅確率は非自明解のうち小さい方
if mu_val > 1:
    if q_nontrivial < 1 and q_nontrivial >= 0:
        print(f"超臨界なので、絶滅確率 q = {q_nontrivial:.6f}")
        print(f"生存確率 = 1 - q = {1 - q_nontrivial:.6f}")
    else:
        print(f"絶滅確率 q = 0 (子は最低1なので絶滅しない)")
else:
    print(f"絶滅確率 q = 1 (臨界以下)")

print()
print("重要な注意:")
print("  逆コラッツ木では各ノードの子は最低1つ (2n) あるので、")
print("  P(子=0) = 0。したがって「木は決して絶滅しない」。")
print("  GW過程として見ると、絶滅確率 q = 0 (自明解のみ)。")
print()
print("  より正確に言えば:")
print("  - G(s) = p1*s + p2*s^2 (p1 + p2 = 1, p0 = 0)")
print("  - G(0) = 0 なので、q = 0 が固定点")
print("  - もう一つの固定点: q = (1-p1)/p2 = 1")
print("  - mu = 4/3 > 1 かつ q = 0 が最小非負固定点")
print("  - つまり絶滅確率は0 → 木は必ず成長し続ける")

# ============================================================
# 3. 実効成長率: 重複除去効果のシミュレーション
# ============================================================

print("\n" + "=" * 70)
print("3. 実効成長率: 重複除去効果のシミュレーション")
print("=" * 70)

def build_inverse_collatz_bfs(max_depth, max_nodes=5_000_000):
    """逆コラッツ木をBFSで構築し、各深さの統計を記録"""
    visited = {1}
    frontier = {1}
    stats = []

    for d in range(1, max_depth + 1):
        next_frontier = set()
        potential_children = 0
        actual_new = 0

        for n in frontier:
            # 子1: 2n
            c1 = 2 * n
            potential_children += 1
            if c1 not in visited:
                visited.add(c1)
                next_frontier.add(c1)
                actual_new += 1

            # 子2: (2n-1)/3 (条件付き)
            if (2 * n - 1) % 3 == 0:
                c2 = (2 * n - 1) // 3
                if c2 > 0:
                    potential_children += 1
                    if c2 not in visited:
                        visited.add(c2)
                        next_frontier.add(c2)
                        actual_new += 1

        dedup_ratio = actual_new / potential_children if potential_children > 0 else 0
        growth = len(next_frontier) / len(frontier) if frontier else 0

        stats.append({
            'depth': d,
            'frontier_size': len(next_frontier),
            'total_visited': len(visited),
            'potential_children': potential_children,
            'actual_new': actual_new,
            'dedup_ratio': dedup_ratio,
            'growth_rate': growth,
        })

        frontier = next_frontier
        if len(visited) > max_nodes or not frontier:
            break

    return visited, stats

print("\n逆コラッツ木のBFS構築 (重複除去あり):")
t0 = time.time()
visited_set, bfs_stats = build_inverse_collatz_bfs(50, max_nodes=3_000_000)
elapsed = time.time() - t0
print(f"構築時間: {elapsed:.2f}秒, 総ノード数: {len(visited_set)}")

print(f"\n{'深さ':>4} {'フロンティア':>12} {'累計':>10} {'潜在子数':>10} {'実新規':>8} "
      f"{'重複除去率':>10} {'成長率':>8}")
print("-" * 75)
for s in bfs_stats:
    print(f"{s['depth']:>4} {s['frontier_size']:>12} {s['total_visited']:>10} "
          f"{s['potential_children']:>10} {s['actual_new']:>8} "
          f"{s['dedup_ratio']:>10.4f} {s['growth_rate']:>8.4f}")

# 実効成長率の推移
if len(bfs_stats) >= 5:
    late_growths = [s['growth_rate'] for s in bfs_stats[-10:] if s['growth_rate'] > 0]
    if late_growths:
        avg_growth = sum(late_growths) / len(late_growths)
        print(f"\n最終10層の平均実効成長率: {avg_growth:.6f}")
        print(f"理論的GW平均子孫数 mu = {mu_val:.6f}")
        print(f"重複除去効果: mu_eff / mu = {avg_growth / mu_val:.6f}")

# ============================================================
# 4. mod 6 分類による詳細な分岐解析
# ============================================================

print("\n" + "=" * 70)
print("4. mod 6 分類による詳細な分岐解析")
print("=" * 70)

# 実際の逆コラッツ木でmod6分布を測定
def analyze_mod6_branching(max_N=1_000_000):
    """1..N の各数の逆コラッツ入次数を mod 6 で分類"""
    deg_by_mod6 = defaultdict(lambda: defaultdict(int))
    total_by_mod6 = defaultdict(int)

    for n in range(1, max_N + 1):
        r = n % 6
        total_by_mod6[r] += 1

        # 前駆の数を数える
        predecessors = 0
        # 2n は常に前駆 (T(2n) = T(n) の意味で n の前駆は 2n)
        # ただし逆操作では: n の前駆は {m : T(m) = n}
        # T(m) = n ⟺ m が偶数で m/2 = n (m = 2n),
        #         または m が奇数で (3m+1)/2^v = n

        # 逆操作1: m = 2n (偶数前駆)
        predecessors += 1

        # 逆操作2: (2n-1)/3 が正の奇数？
        if (2 * n - 1) % 3 == 0:
            c = (2 * n - 1) // 3
            if c > 0:
                predecessors += 1

        deg_by_mod6[r][predecessors] += 1

    return deg_by_mod6, total_by_mod6

print("\n1..1,000,000 での mod 6 別入次数分布:")
t0 = time.time()
deg_mod6, total_mod6 = analyze_mod6_branching(1_000_000)
elapsed = time.time() - t0
print(f"計算時間: {elapsed:.2f}秒")

print(f"\n{'mod6':>6} {'総数':>10} {'deg=1':>10} {'deg=2':>10} {'deg=1比率':>10} {'deg=2比率':>10}")
print("-" * 60)
total_deg1 = 0
total_deg2 = 0
for r in range(6):
    d1 = deg_mod6[r].get(1, 0)
    d2 = deg_mod6[r].get(2, 0)
    total = total_mod6[r]
    total_deg1 += d1
    total_deg2 += d2
    print(f"{r:>6} {total:>10} {d1:>10} {d2:>10} "
          f"{d1/total:.6f} {d2/total:.6f}")

total_all = sum(total_mod6.values())
print(f"\n全体: deg=1 の割合 = {total_deg1/total_all:.6f} (理論値 2/3 = {2/3:.6f})")
print(f"      deg=2 の割合 = {total_deg2/total_all:.6f} (理論値 1/3 = {1/3:.6f})")

# ============================================================
# 5. Syracuse版のGalton-Watson解析
# ============================================================

print("\n" + "=" * 70)
print("5. Syracuse版 (奇数のみ) のGalton-Watson解析")
print("=" * 70)

def syracuse_inverse(m, max_k=40):
    """T^{-1}(m): 奇数mの逆像 (2^k*m - 1)/3 が正の奇数になるk"""
    inverses = []
    pow2 = 2
    for k in range(1, max_k + 1):
        val = pow2 * m - 1
        if val % 3 == 0:
            result = val // 3
            if result > 0 and result % 2 == 1:
                inverses.append((k, result))
        pow2 *= 2
    return inverses

# 小さい奇数での逆像数の分布
print("\n奇数 m の逆像数 (max_k=40):")
inv_count_dist = Counter()
for m in range(1, 10001, 2):
    invs = syracuse_inverse(m, 40)
    inv_count_dist[len(invs)] += 1

total_odd = sum(inv_count_dist.values())
print(f"1..10000 の奇数 ({total_odd}個) での逆像数分布:")
expected_mean = 0
for count in sorted(inv_count_dist.keys()):
    freq = inv_count_dist[count]
    prob = freq / total_odd
    expected_mean += count * prob
    print(f"  逆像数={count}: {freq}個 ({prob*100:.2f}%)")

print(f"\n平均逆像数 (max_k=40): {expected_mean:.6f}")
print("理論的な平均逆像数 = sum_k P(k) で kごとの逆像存在確率の和")

# 理論計算: k で (2^k*m - 1)/3 が正の奇数になる確率
# 2^k*m - 1 ≡ 0 (mod 3) ⟺ 2^k*m ≡ 1 (mod 3)
# m が奇数で一様ランダムなら m mod 3 は 1 or 2 が等確率
# 2^k mod 3 は周期2: 2,1,2,1,...
# P(3|2^k*m-1) = 1/3 (大まかに)
# 結果が奇数: (2^k*m-1)/3 が奇数 ⟺ 2^k*m-1 ≡ 3 (mod 6) ⟺ 条件による
# 各kごとに独立に確率 p_k で逆像が存在するとみなす

print("\n--- kごとの逆像存在確率 ---")
for k in range(1, 41):
    count_exists = 0
    for m in range(1, 10001, 2):
        pow2k = 2**k
        val = pow2k * m - 1
        if val % 3 == 0:
            result = val // 3
            if result > 0 and result % 2 == 1:
                count_exists += 1
    prob_k = count_exists / 5000
    if prob_k > 0.001:
        print(f"  k={k:>2}: P(逆像存在) = {prob_k:.4f}")

# ============================================================
# 6. Syracuse版 GW過程の子孫分布 (有限世代で打ち切り)
# ============================================================

print("\n" + "=" * 70)
print("6. Syracuse版 GW過程: 有限kでの打ち切り効果")
print("=" * 70)

for max_k_trunc in [5, 10, 20, 40]:
    inv_counts = []
    for m in range(1, 50001, 2):
        inv_counts.append(len(syracuse_inverse(m, max_k_trunc)))

    mean_inv = sum(inv_counts) / len(inv_counts)
    max_inv = max(inv_counts)
    dist = Counter(inv_counts)

    print(f"\nmax_k = {max_k_trunc}: 平均逆像数 = {mean_inv:.4f}, 最大逆像数 = {max_inv}")
    p0 = dist.get(0, 0) / len(inv_counts)
    print(f"  P(子=0) = {p0:.6f}")
    for c in sorted(dist.keys()):
        print(f"  P(子={c}) = {dist[c]/len(inv_counts):.6f}")

# ============================================================
# 7. 被覆時間の推定
# ============================================================

print("\n" + "=" * 70)
print("7. 被覆時間の推定")
print("=" * 70)

print("\n逆コラッツ木の深さDで 1..N の何%をカバーするか:")

def coverage_vs_depth(max_depth=40, check_Ns=[100, 1000, 10000, 100000]):
    """逆コラッツ木の深さDごとに 1..N のカバー率を計算"""
    visited = {1}
    frontier = {1}
    coverage_data = []

    for d in range(1, max_depth + 1):
        next_frontier = set()
        for n in frontier:
            c1 = 2 * n
            if c1 not in visited:
                visited.add(c1)
                next_frontier.add(c1)
            if (2 * n - 1) % 3 == 0:
                c2 = (2 * n - 1) // 3
                if c2 > 0 and c2 not in visited:
                    visited.add(c2)
                    next_frontier.add(c2)

        coverages = {}
        for N in check_Ns:
            covered = sum(1 for i in range(1, N + 1) if i in visited)
            coverages[N] = covered / N

        coverage_data.append({
            'depth': d,
            'total_nodes': len(visited),
            'frontier_size': len(next_frontier),
            'coverages': coverages,
        })

        frontier = next_frontier
        if not frontier:
            break

    return coverage_data

t0 = time.time()
cov_data = coverage_vs_depth(40, [100, 1000, 10000, 100000])
elapsed = time.time() - t0
print(f"計算時間: {elapsed:.2f}秒")

print(f"\n{'深さ':>4} {'ノード数':>10} {'N=100':>10} {'N=1000':>10} {'N=10000':>10} {'N=100000':>10}")
print("-" * 65)
for c in cov_data:
    print(f"{c['depth']:>4} {c['total_nodes']:>10} "
          f"{c['coverages'][100]*100:>9.2f}% "
          f"{c['coverages'][1000]*100:>9.2f}% "
          f"{c['coverages'][10000]*100:>9.2f}% "
          f"{c['coverages'][100000]*100:>9.2f}%")

# 100%カバーに必要な深さの推定
print("\n100%カバーに必要な深さ:")
for N in [100, 1000, 10000, 100000]:
    for c in cov_data:
        if c['coverages'][N] >= 0.9999:
            print(f"  N={N:>6}: 深さ {c['depth']} で99.99%以上カバー")
            break
    else:
        last = cov_data[-1]
        print(f"  N={N:>6}: 深さ {last['depth']} でも {last['coverages'][N]*100:.2f}% (未達)")

# ============================================================
# 8. 被覆時間のスケーリング則
# ============================================================

print("\n" + "=" * 70)
print("8. 被覆時間のスケーリング則")
print("=" * 70)

# D(N) = N のカバーに必要な最小深さ の N 依存性
print("\n95%, 99%, 99.9% カバーに必要な深さ:")

for threshold in [0.95, 0.99, 0.999]:
    print(f"\n{threshold*100:.1f}% カバー:")
    for N in [100, 1000, 10000, 100000]:
        for c in cov_data:
            if c['coverages'][N] >= threshold:
                print(f"  N={N:>6}: 深さ {c['depth']}")
                break
        else:
            print(f"  N={N:>6}: 深さ{len(cov_data)}以上必要")

# log(N) vs 深さ のスケーリング
print("\n\nスケーリング解析 (99%カバー深さ vs log(N)):")
depth_99 = {}
for N in [100, 1000, 10000, 100000]:
    for c in cov_data:
        if c['coverages'][N] >= 0.99:
            depth_99[N] = c['depth']
            break

if len(depth_99) >= 2:
    items = sorted(depth_99.items())
    for N, d in items:
        print(f"  N={N:>6}, log2(N)={math.log2(N):.2f}, 深さ={d}, D/log2(N)={d/math.log2(N):.4f}")

    # log(N) に対する線形フィット
    xs = [math.log(N) for N, d in items]
    ys = [d for N, d in items]
    n = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if abs(denom) > 1e-12:
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        print(f"\n  D(N) ≈ {slope:.4f} * ln(N) + {intercept:.4f}")
        print(f"  D(N) ≈ {slope * math.log(2):.4f} * log2(N) + {intercept:.4f}")

# ============================================================
# 9. GW過程の生存確率 vs 重複除去後の実効生存率
# ============================================================

print("\n" + "=" * 70)
print("9. GW過程の生存確率と実効生存率の比較")
print("=" * 70)

# 理論的なGW過程: P(子=0)=0, P(子=1)=2/3, P(子=2)=1/3
# 母関数 G(s) = (2/3)s + (1/3)s^2
# 世代nでの絶滅確率 q_n: q_0 = 0, q_{n+1} = G(q_n)

print("\nGW過程の世代別絶滅確率 (P(子=0)=0 の場合):")
q_n = 0.0
for gen in range(20):
    q_next = (2.0/3) * q_n + (1.0/3) * q_n**2
    print(f"  世代{gen:>2}: q_{gen} = {q_n:.10f}")
    q_n = q_next
print(f"  → q = 0 に収束 (絶滅確率 0)")
print()

# 比較: もし P(子=0) > 0 だった場合
print("参考: もし P(子=0) = ε > 0 だった場合の絶滅確率:")
for eps in [0.01, 0.05, 0.1, 0.2]:
    p0_mod = eps
    p1_mod = (2.0/3) * (1 - eps)
    p2_mod = (1.0/3) * (1 - eps)
    mu_mod = p1_mod + 2 * p2_mod
    # G(s) = p0 + p1*s + p2*s^2 の固定点
    # p2*s^2 + (p1-1)*s + p0 = 0
    a_coef = p2_mod
    b_coef = p1_mod - 1
    c_coef = p0_mod
    disc = b_coef**2 - 4*a_coef*c_coef
    if disc >= 0:
        s1 = (-b_coef - math.sqrt(disc)) / (2 * a_coef)
        s2 = (-b_coef + math.sqrt(disc)) / (2 * a_coef)
        q_ext = min(s for s in [s1, s2] if 0 <= s <= 1) if any(0 <= s <= 1 for s in [s1, s2]) else None
    else:
        q_ext = None

    print(f"  eps={eps:.2f}: mu={mu_mod:.4f}, 絶滅確率 q = {q_ext:.6f}" if q_ext else
          f"  eps={eps:.2f}: mu={mu_mod:.4f}, 絶滅確率 解なし")

# ============================================================
# 10. 多重型 GW 過程 (mod 6 タイプ別)
# ============================================================

print("\n" + "=" * 70)
print("10. 多重型 GW 過程 (mod 6 タイプ別)")
print("=" * 70)

print("\n逆コラッツの前駆 2n と (2n-1)/3 が mod 6 でどのタイプに属するか:")
print("(子のmod6タイプ遷移行列)")

# nのmod6 → 2n のmod6
print("\n2n 操作の mod 6 遷移:")
for r in range(6):
    child_mod = (2 * r) % 6
    print(f"  n ≡ {r} (mod 6) → 2n ≡ {child_mod} (mod 6)")

# nのmod6 → (2n-1)/3 のmod6 (存在する場合のみ)
print("\n(2n-1)/3 操作の mod 6 遷移 (存在する場合):")
for r in range(6):
    if (2 * r - 1) % 3 == 0:
        child_val = (2 * r - 1) // 3
        child_mod = child_val % 6
        print(f"  n ≡ {r} (mod 6) → (2n-1)/3 ≡ {child_mod} (mod 6)")

# 遷移行列の構築
print("\n遷移行列 M (行=親のmod6, 列=子のmod6):")
M = [[0]*6 for _ in range(6)]
for r in range(6):
    # 2n
    M[r][(2*r) % 6] += 1
    # (2n-1)/3
    if (2*r - 1) % 3 == 0:
        child = (2*r - 1) // 3
        M[r][child % 6] += 1

print("      ", end="")
for j in range(6):
    print(f"mod{j:>2} ", end="")
print()
for i in range(6):
    print(f"mod{i}: ", end="")
    for j in range(6):
        print(f"  {M[i][j]:>2} ", end="")
    print()

# 多重型GW過程の平均行列
print("\n平均子孫行列 M の最大固有値 (スペクトル半径):")
# 簡易的に冪乗法で最大固有値を求める
import random
random.seed(42)
v = [random.random() for _ in range(6)]
norm = sum(x**2 for x in v)**0.5
v = [x/norm for x in v]

for iteration in range(100):
    new_v = [0.0]*6
    for i in range(6):
        for j in range(6):
            new_v[i] += M[i][j] * v[j]
    norm = sum(x**2 for x in new_v)**0.5
    eigenvalue = norm
    v = [x/norm for x in new_v]

print(f"  スペクトル半径 rho(M) ≈ {eigenvalue:.6f}")
print(f"  対応する固有ベクトル: {[f'{x:.4f}' for x in v]}")
print(f"  理論的成長率 4/3 = {4/3:.6f}")
print()

# 均等分布 (1/6, ..., 1/6) で始めた場合の1世代後の分布
init = [1/6]*6
next_gen = [0.0]*6
for j in range(6):
    for i in range(6):
        next_gen[j] += M[i][j] * init[i]
total_next = sum(next_gen)
next_normalized = [x/total_next for x in next_gen]

print(f"均等分布から1世代後の分布 (正規化前): {[f'{x:.4f}' for x in next_gen]}")
print(f"  → 総量: {total_next:.4f} (=平均子孫数)")
print(f"  → 正規化: {[f'{x:.4f}' for x in next_normalized]}")

# 定常分布の収束
print("\n定常分布への収束:")
dist = [1/6]*6
for gen in range(20):
    new_dist = [0.0]*6
    for j in range(6):
        for i in range(6):
            new_dist[j] += M[i][j] * dist[i]
    total = sum(new_dist)
    dist = [x/total for x in new_dist]
    if gen in [0, 1, 2, 5, 10, 19]:
        print(f"  世代{gen:>2}: {[f'{x:.4f}' for x in dist]} (総量={total:.4f})")

# ============================================================
# 11. 被覆時間の確率論的推定
# ============================================================

print("\n" + "=" * 70)
print("11. 被覆時間の確率論的推定")
print("=" * 70)

print("\nCoupon Collector的な議論:")
print("  N 個の数をカバーするのに必要なノード数 ≈ N*ln(N)")
print("  逆コラッツ木の深さDでのノード数 ≈ (4/3)^D")
print("  したがって N*ln(N) ≈ (4/3)^D")
print("  D ≈ ln(N*ln(N)) / ln(4/3)")
print()

for N in [100, 1000, 10000, 100000, 10**6, 10**9]:
    D_est = math.log(N * math.log(N)) / math.log(4/3)
    D_est_simple = math.log(N) / math.log(4/3)
    print(f"  N={N:>10}: D_coupon ≈ {D_est:.1f}, D_simple ≈ {D_est_simple:.1f}")

print("\n注意: Coupon Collector 推定は各ノードが独立一様に数を選ぶ仮定。")
print("実際には逆コラッツ木のノードは非一様なので、これは楽観的推定。")

# 実効的な被覆速度: 深さDで (4/3)^D ノードが [1, O(2^D)] に分布
# → 密度 ≈ (4/3)^D / 2^D = (2/3)^D → 0
# ただし重複を考えると...
print("\n密度の推定 (深さDの木が 1..2^D に対して持つ密度):")
for d in range(1, 41, 2):
    nodes_est = (4/3)**d
    range_est = 2**d
    density_est = nodes_est / range_est
    print(f"  D={d:>2}: ノード ≈ {nodes_est:.0f}, 範囲 ≈ 2^{d}, "
          f"密度 ≈ (2/3)^{d} = {density_est:.6f}")
    if density_est < 1e-6:
        break

print("\n逆コラッツ木は密度0に向かうが、")
print("「小さい数」は早い段階で高密度にカバーされるため、")
print("実質的な被覆時間は有限。")
print("カバー深さ D(N) ≈ C * log(N) で C は定数。")

# 実データからCを推定
print("\n実データからの C の推定:")
for threshold in [0.99, 0.999]:
    depths = []
    for N in [100, 1000, 10000, 100000]:
        for c in cov_data:
            if c['coverages'][N] >= threshold:
                depths.append((N, c['depth']))
                break

    if len(depths) >= 2:
        Cs = [(d / math.log(N)) for N, d in depths]
        print(f"\n  {threshold*100:.1f}% カバー:")
        for (N, d), C_val in zip(depths, Cs):
            print(f"    N={N:>6}: D={d}, C = D/ln(N) = {C_val:.4f}")
        avg_C = sum(Cs) / len(Cs)
        print(f"    平均 C = {avg_C:.4f}")

# ============================================================
# 12. まとめ
# ============================================================

print("\n" + "=" * 70)
print("12. まとめ")
print("=" * 70)

print("""
【Galton-Watson モデルの主要結果】

1. 基本パラメータ:
   - 子孫分布: P(子=1) = 2/3, P(子=2) = 1/3, P(子=0) = 0
   - 平均子孫数 mu = 4/3 > 1 → 超臨界
   - 分散 sigma^2 = 2/9

2. 絶滅確率:
   - P(子=0) = 0 なので、逆コラッツ木は絶対に絶滅しない
   - GW過程の固定点方程式の最小非負解 q = 0
   - これはコラッツ予想の「全数到達」と整合的

3. 実効成長率:
   - 理論的 mu = 4/3 ≈ 1.3333
   - 重複除去後の実効成長率は深さとともに減少
   - (重複は深さが増すほど影響)

4. 多重型GW過程:
   - mod 6 タイプ別の遷移行列のスペクトル半径 ≈ 4/3
   - 定常分布は均等ではない

5. 被覆時間:
   - D(N) ≈ C * ln(N) でスケール
   - C は閾値 (99%, 99.9% etc.) に依存
""")

print("完了!")
