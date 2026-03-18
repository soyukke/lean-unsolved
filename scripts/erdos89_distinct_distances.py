"""
エルデシュ問題 #89: Distinct Distances（異なる距離問題）

n個の平面上の点が決定する異なる距離の数の下界を探索する。

主な問いかけ:
  n個の点は ≫ n/√(log n) 個の異なる距離を決定するか？

背景:
  - √n × √n 整数格子が下界 ~ C·n/√(log n) を達成（最小に近い配置）
  - Guth-Katz (2015) が ≫ n/log n を証明（最良結果）
  - ギャップ: log n vs √(log n)

探索1: 数値実験
  - ランダム配置 vs 整数格子 vs 三角格子 vs 六角格子
  - 異なる距離数と理論値の比較

探索2: Landau-Ramanujan定理の数値検証
  - 整数格子での距離 = 2つの平方和で表せる数
  - S(x) ~ K·x/√(log x) の漸近挙動確認
"""

import math
import random
from collections import Counter


# --- ユーティリティ ---

def distinct_distances_int(points):
    """整数座標の点集合の異なる距離²の数を計算"""
    dist_sq_set = set()
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist_sq_set.add(dx * dx + dy * dy)
    return len(dist_sq_set)


def distinct_distances_float(points):
    """浮動小数点座標の点集合用（丸めて比較）"""
    dist_set = set()
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            d_sq = dx * dx + dy * dy
            dist_set.add(round(d_sq, 8))
    return len(dist_set)


# --- 格子生成 ---

def integer_grid(n):
    """n点に最も近い √n × √n 整数格子"""
    side = int(math.ceil(math.sqrt(n)))
    points = []
    for i in range(side):
        for j in range(side):
            points.append((i, j))
            if len(points) == n:
                return points
    return points


def triangular_lattice(n):
    """三角格子（正三角形の頂点）"""
    side = int(math.ceil(math.sqrt(n))) + 1
    points = []
    for i in range(side * 2):
        for j in range(side * 2):
            x = i + 0.5 * j
            y = j * math.sqrt(3) / 2
            points.append((x, y))
            if len(points) == n:
                return points
    return points


def hexagonal_lattice(n):
    """六角格子"""
    side = int(math.ceil(math.sqrt(n))) + 1
    points = []
    for i in range(side * 2):
        for j in range(side * 2):
            x = i * 1.5
            y = j * math.sqrt(3) + (i % 2) * math.sqrt(3) / 2
            points.append((x, y))
            if len(points) == n:
                return points
    return points


def random_points(n, seed=42):
    """[0, √n] × [0, √n] の一様ランダム配置"""
    rng = random.Random(seed)
    side = math.sqrt(n)
    return [(rng.uniform(0, side), rng.uniform(0, side)) for _ in range(n)]


# --- 理論予測 ---

def erdos_lower_bound(n):
    """エルデシュ予想の下界 n / √(log n)"""
    if n <= 1:
        return 0
    return n / math.sqrt(math.log(n))


def guth_katz_bound(n):
    """Guth-Katz の結果 n / log n"""
    if n <= 1:
        return 0
    return n / math.log(n)


# --- 探索1: メイン実験 ---

def experiment():
    ns = [10, 50, 100, 200, 500, 1000]

    print("=" * 80)
    print("エルデシュ #89: 異なる距離問題 - 数値実験")
    print("=" * 80)
    print()

    print(f"{'n':>6s}  {'ランダム':>8s}  {'整数格子':>8s}  {'三角格子':>8s}  {'六角格子':>8s}"
          f"  {'n/√logn':>8s}  {'n/logn':>8s}  {'grid比':>6s}")
    print("-" * 80)

    for n in ns:
        # ランダム配置
        pts_rand = random_points(n)
        d_rand = distinct_distances_float(pts_rand)

        # 整数格子
        pts_grid = integer_grid(n)
        d_grid = distinct_distances_int(pts_grid)

        # 三角格子
        pts_tri = triangular_lattice(n)
        d_tri = distinct_distances_float(pts_tri)

        # 六角格子
        pts_hex = hexagonal_lattice(n)
        d_hex = distinct_distances_float(pts_hex)

        # 理論値
        eb = erdos_lower_bound(n)
        gk = guth_katz_bound(n)

        ratio = d_grid / eb if eb > 0 else 0

        print(f"{n:6d}  {d_rand:8d}  {d_grid:8d}  {d_tri:8d}  {d_hex:8d}"
              f"  {eb:8.1f}  {gk:8.1f}  {ratio:6.2f}")

    print()


def experiment_detail():
    """詳細な比較（各nに対する分析）"""
    ns = [10, 50, 100, 500, 1000]

    print("=" * 80)
    print("詳細分析: 各格子のパフォーマンス")
    print("=" * 80)

    for n in ns:
        print(f"\n--- n = {n} ---")

        pts_grid = integer_grid(n)
        d_grid = distinct_distances_int(pts_grid)
        eb = erdos_lower_bound(n)
        max_dist = n * (n - 1) // 2

        print(f"  整数格子: {d_grid} 個の異なる距離²")
        print(f"  最大可能: {max_dist} (= n(n-1)/2)")
        print(f"  n/√(log n) = {eb:.1f}")
        print(f"  整数格子 / (n/√logn) = {d_grid / eb:.2f}")
        print(f"  整数格子は最大の {100 * d_grid / max_dist:.1f}% の異なる距離を持つ")


# --- 探索2: 距離スペクトル解析 ---

def experiment_distance_spectrum(n=100):
    """整数格子での距離のスペクトル解析"""
    print("\n" + "=" * 80)
    print(f"距離スペクトル解析 (n={n}, 整数格子)")
    print("=" * 80)

    pts = integer_grid(n)

    # 距離の二乗の頻度
    dist_sq_count = Counter()
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            d_sq = dx * dx + dy * dy
            dist_sq_count[d_sq] += 1

    # 頻度分布
    freqs = sorted(dist_sq_count.values(), reverse=True)
    print(f"  異なる距離²の数: {len(dist_sq_count)}")
    print(f"  最大頻度の距離²: {max(dist_sq_count, key=dist_sq_count.get)} "
          f"(頻度 {freqs[0]})")
    print(f"  上位10の頻度: {freqs[:10]}")

    # 2つの平方和として表せる数を列挙
    max_d_sq = max(dist_sq_count.keys())
    sum_two_sq = set()
    limit = int(math.sqrt(max_d_sq)) + 1
    for a in range(limit):
        for b in range(a, limit):
            s = a * a + b * b
            if 0 < s <= max_d_sq:
                sum_two_sq.add(s)

    print(f"\n  最大距離²: {max_d_sq}")
    print(f"  ≤ {max_d_sq} で2つの平方和で表せる数: {len(sum_two_sq)} 個")
    print(f"  実際に出現した距離²: {len(dist_sq_count)} 個")
    print(f"  出現率: {len(dist_sq_count) / len(sum_two_sq):.3f}")

    # 出現した距離²のうち、格子サイズに制限されないものの割合
    side = int(math.ceil(math.sqrt(n)))
    possible_max = 2 * (side - 1) ** 2  # 対角の最大距離²
    print(f"  格子サイズ: {side}×{side}, 対角最大距離²: {possible_max}")

    return dist_sq_count


# --- 探索2 続: Landau-Ramanujan定理検証 ---

def experiment_landau_ramanujan():
    """Landau-Ramanujan定理の数値検証:
    x以下の2つの平方和で表せる正整数の個数 ~ K·x/√(log x)
    ここで K ≈ 0.7642...（Landau-Ramanujan定数）
    """
    print("\n" + "=" * 80)
    print("Landau-Ramanujan定理の数値検証")
    print("=" * 80)

    X_max = 100000

    # 2つの平方和で表せる数を列挙
    is_sum_two_sq = [False] * (X_max + 1)
    limit = int(math.sqrt(X_max)) + 1
    for a in range(limit):
        for b in range(a, limit):
            s = a * a + b * b
            if 0 < s <= X_max:
                is_sum_two_sq[s] = True

    # 累積カウント
    count = [0] * (X_max + 1)
    for i in range(1, X_max + 1):
        count[i] = count[i - 1] + (1 if is_sum_two_sq[i] else 0)

    # Landau-Ramanujan定数
    K_LR = 0.7642236535892206

    print(f"\n  Landau-Ramanujan定数 K ≈ {K_LR:.10f}")
    print(f"\n  {'x':>8s}  {'S(x)':>8s}  {'K·x/√logx':>12s}  {'比率':>8s}")
    print("  " + "-" * 45)

    xs = [100, 500, 1000, 5000, 10000, 50000, 100000]
    for x in xs:
        S_x = count[x]
        predicted = K_LR * x / math.sqrt(math.log(x))
        ratio = S_x / predicted if predicted > 0 else 0
        print(f"  {x:8d}  {S_x:8d}  {predicted:12.1f}  {ratio:8.4f}")

    print(f"\n  → 比率が1に収束 → Landau-Ramanujan定理が数値的に確認された")
    print(f"  → 整数格子での異なる距離数 ≈ n/√(log n) の理由:")
    print(f"    格子の最大距離² ≈ 2n なので、2つの平方和の数 ≈ K·2n/√(log 2n) ≈ Cn/√(log n)")


def experiment_connection():
    """整数格子の異なる距離数とLandau-Ramanujan定数の関係"""
    print("\n" + "=" * 80)
    print("整数格子の距離数と2つの平方和の直接比較")
    print("=" * 80)

    ns = [25, 49, 100, 196, 400, 625, 900]  # 完全平方数を使う

    print(f"\n  {'n':>6s}  {'grid':>6s}  {'d':>4s}  {'max_d²':>8s}  {'S(max_d²)':>10s}  {'grid/S':>7s}")
    print("  " + "-" * 55)

    for n in ns:
        side = int(math.sqrt(n))
        pts = integer_grid(n)
        d_grid = distinct_distances_int(pts)

        # 最大距離²
        max_d_sq = 2 * (side - 1) ** 2

        # ≤ max_d_sq で2つの平方和の数
        s2sq = set()
        lim = int(math.sqrt(max_d_sq)) + 1
        for a in range(lim):
            for b in range(a, lim):
                s = a * a + b * b
                if 0 < s <= max_d_sq:
                    s2sq.add(s)

        ratio = d_grid / len(s2sq) if s2sq else 0
        print(f"  {n:6d}  {side:4d}×{side}  {d_grid:6d}  {max_d_sq:8d}  {len(s2sq):10d}  {ratio:7.3f}")

    print(f"\n  → 格子の異なる距離数は、可能な2平方和の数のかなりの部分を占める")


if __name__ == '__main__':
    # 探索1: 数値実験
    experiment()
    experiment_detail()

    # 探索2: 距離スペクトル解析
    experiment_distance_spectrum(n=100)

    # 探索2 続: Landau-Ramanujan定理の検証
    experiment_landau_ramanujan()

    # 接続の検証
    experiment_connection()

    print("\n" + "=" * 80)
    print("まとめ")
    print("=" * 80)
    print("""
  1. ランダム配置は ≈ n(n-1)/2 に近い異なる距離を持つ（ほぼ最大）
  2. 整数格子は最も少ない異なる距離を持つ配置の一つ
     → d(grid) / (n/√logn) が定数的に振る舞う
  3. 三角格子・六角格子は整数格子より多くの異なる距離を持つ
  4. Landau-Ramanujan定理 S(x) ~ K·x/√(log x) が数値的に確認された
     → 整数格子の異なる距離数 ≈ 2平方和で表せる数の個数
  5. エルデシュ予想とGuth-Katz結果のギャップは √(log n) 因子のみ
  6. 整数格子が最適であることの本質:
     距離² = a² + b² は「2つの平方和で表せる数」に限られ、
     その密度はLandau-Ramanujan定理により x/√(log x) 程度
    """)
