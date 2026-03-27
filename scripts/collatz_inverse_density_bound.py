#!/usr/bin/env python3
"""
コラッツ予想 探索: 逆コラッツ木の到達密度の下界と指数減衰の精密評価

目的:
  逆像木のレベルLまでの到達集合 R(L) の密度 |R(L) ∩ [1,N]| / N の下界を
  精密に計算し、1 - density(R(L)) が C * (3/4)^L 型の指数減衰に従うことを実証する。

既知:
  - 逆コラッツ写像: n -> 2n (常に), n -> (2n-1)/3 (2n ≡ 1 mod 3 のとき)
  - 逆像木の成長率 ≈ 4/3
  - コラッツ予想 ⟺ 逆像木が全正整数を包含

分析手法:
  1. 標準逆コラッツ木を深さLまで構築
  2. 各深さでの [1,N] 内の被覆密度を計測
  3. gap(L) = 1 - density(L) の指数減衰をフィッティング
  4. gap(L) ≈ C * alpha^L の C と alpha を推定
  5. 理論的予測 alpha = 3/4 = 0.75 との比較
"""

import math
import time
from collections import defaultdict


# ============================================================
# Part 1: 逆コラッツ木の構築 (BFS, 標準写像)
# ============================================================

def build_inverse_collatz_bfs(max_depth):
    """
    根=1から逆コラッツ操作でBFS展開。
    逆操作: n -> 2n, n -> (2n-1)/3 (条件付き)
    返却: depth_sets[d] = 深さdで初めて到達したノードの集合
    """
    all_nodes = {1}
    depth_sets = {0: {1}}
    frontier = {1}

    for d in range(1, max_depth + 1):
        new_frontier = set()
        for n in frontier:
            # 逆操作1: n -> 2n
            child1 = 2 * n
            if child1 not in all_nodes:
                all_nodes.add(child1)
                new_frontier.add(child1)

            # 逆操作2: n -> (2n-1)/3 (2n-1 ≡ 0 mod 3 のとき)
            if (2 * n - 1) % 3 == 0:
                child2 = (2 * n - 1) // 3
                if child2 > 0 and child2 not in all_nodes:
                    all_nodes.add(child2)
                    new_frontier.add(child2)

        depth_sets[d] = new_frontier
        frontier = new_frontier

        if not frontier:
            break

    return depth_sets, all_nodes


# ============================================================
# Part 2: 密度計算とギャップ解析
# ============================================================

def compute_density_profile(depth_sets, max_depth, N_values):
    """
    各深さLでの累積被覆密度 density(L, N) = |R(L) ∩ [1,N]| / N を計算。
    gap(L, N) = 1 - density(L, N) も返す。
    """
    cumulative = set()
    results = {}  # results[L] = {N: (density, gap, count)}

    for L in range(max_depth + 1):
        nodes = depth_sets.get(L, set())
        cumulative.update(nodes)

        level_result = {}
        for N in N_values:
            count = sum(1 for x in cumulative if 1 <= x <= N)
            density = count / N
            gap = 1.0 - density
            level_result[N] = (density, gap, count)

        results[L] = level_result

    return results


def fit_exponential_decay(gaps_by_depth, start_depth=5):
    """
    gap(L) ≈ C * alpha^L をフィッティング。
    log(gap) ≈ log(C) + L * log(alpha) の線形回帰。
    start_depth 以降のデータのみ使用（初期の過渡的挙動を除外）。
    """
    valid_points = [(L, g) for L, g in gaps_by_depth if L >= start_depth and g > 0]
    if len(valid_points) < 3:
        return None, None, None

    n = len(valid_points)
    sum_L = sum(L for L, _ in valid_points)
    sum_logG = sum(math.log(g) for _, g in valid_points)
    sum_L2 = sum(L * L for L, _ in valid_points)
    sum_L_logG = sum(L * math.log(g) for L, g in valid_points)

    denom = n * sum_L2 - sum_L ** 2
    if abs(denom) < 1e-15:
        return None, None, None

    slope = (n * sum_L_logG - sum_L * sum_logG) / denom
    intercept = (sum_logG - slope * sum_L) / n

    alpha = math.exp(slope)
    C = math.exp(intercept)

    # R^2 の計算
    mean_logG = sum_logG / n
    ss_tot = sum((math.log(g) - mean_logG) ** 2 for _, g in valid_points)
    ss_res = sum((math.log(g) - (intercept + slope * L)) ** 2 for L, g in valid_points)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return C, alpha, r_squared


# ============================================================
# Part 3: 逐次ギャップ比率の解析
# ============================================================

def analyze_gap_ratios(gaps_by_depth):
    """
    gap(L+1) / gap(L) の比率を計算。
    理論的に alpha = 3/4 に収束するかを確認。
    """
    ratios = []
    for i in range(1, len(gaps_by_depth)):
        L_prev, g_prev = gaps_by_depth[i - 1]
        L_curr, g_curr = gaps_by_depth[i]
        if g_prev > 0 and g_curr > 0:
            ratio = g_curr / g_prev
            ratios.append((L_curr, ratio))
    return ratios


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 80)
    print("逆コラッツ木の到達密度の下界 -- 指数減衰の精密評価")
    print("=" * 80)

    # --- 木の構築 ---
    MAX_DEPTH = 55
    N_VALUES = [1000, 10000, 100000, 1000000]

    print(f"\n逆コラッツ木を深さ {MAX_DEPTH} まで構築中...")
    t0 = time.time()
    depth_sets, all_nodes = build_inverse_collatz_bfs(MAX_DEPTH)
    elapsed = time.time() - t0
    print(f"構築完了: {elapsed:.2f}秒, 総ノード数 = {len(all_nodes):,}")

    # 各深さのノード数
    print(f"\n{'深さ':>4} | {'新規ノード':>12} | {'成長率':>10}")
    print("-" * 35)
    prev_count = 0
    for d in range(MAX_DEPTH + 1):
        nc = len(depth_sets.get(d, set()))
        rate_str = f"{nc/prev_count:.4f}" if prev_count > 0 else "---"
        if d <= 15 or d % 5 == 0:
            print(f"{d:>4} | {nc:>12,} | {rate_str:>10}")
        prev_count = nc

    # --- 密度プロファイル ---
    print(f"\n{'='*80}")
    print("密度プロファイル: density(L, N) = |R(L) ∩ [1,N]| / N")
    print(f"{'='*80}")

    t0 = time.time()
    density_profile = compute_density_profile(depth_sets, MAX_DEPTH, N_VALUES)
    elapsed = time.time() - t0
    print(f"密度計算完了: {elapsed:.2f}秒")

    # テーブル表示
    header = f"{'深さ':>4}"
    for N in N_VALUES:
        header += f" | N={N:>8}: density / gap"
    print(f"\n{header}")
    print("-" * (6 + 30 * len(N_VALUES)))

    for L in range(MAX_DEPTH + 1):
        if L <= 30 or L % 5 == 0:
            line = f"{L:>4}"
            for N in N_VALUES:
                density, gap, count = density_profile[L][N]
                if gap > 0:
                    line += f" | {density:.6f} / {gap:.2e}"
                else:
                    line += f" | {density:.6f} / 0.00e+00"
            print(line)

    # --- 指数フィッティング ---
    print(f"\n{'='*80}")
    print("指数減衰フィッティング: gap(L) ≈ C * alpha^L")
    print(f"{'='*80}")

    for N in N_VALUES:
        gaps = [(L, density_profile[L][N][1]) for L in range(MAX_DEPTH + 1)]
        gaps_positive = [(L, g) for L, g in gaps if g > 0]

        if not gaps_positive:
            print(f"\nN={N:>8}: 深さ{MAX_DEPTH}で完全被覆! gap=0")
            continue

        # 複数の開始深さでフィッティング
        print(f"\nN={N:>8,}:")
        for start_d in [3, 5, 8, 10]:
            C, alpha, r2 = fit_exponential_decay(gaps_positive, start_depth=start_d)
            if C is not None:
                print(f"  開始深さ={start_d:>2}: C={C:.6f}, alpha={alpha:.6f}, R^2={r2:.8f}")
                print(f"               理論値 3/4={0.75:.6f}, 誤差={abs(alpha-0.75)/0.75*100:.2f}%")

    # --- ギャップ比率の解析 ---
    print(f"\n{'='*80}")
    print("ギャップ比率: gap(L+1) / gap(L) → alpha の収束")
    print(f"{'='*80}")

    for N in N_VALUES:
        gaps = [(L, density_profile[L][N][1]) for L in range(MAX_DEPTH + 1)]
        gaps_positive = [(L, g) for L, g in gaps if g > 0]

        ratios = analyze_gap_ratios(gaps_positive)

        if not ratios:
            continue

        print(f"\nN={N:>8,}:")
        print(f"  {'深さ':>4} | {'gap(L)':>12} | {'gap(L)/gap(L-1)':>16} | {'3/4=0.75との差':>14}")
        print(f"  {'-'*55}")

        for L, r in ratios:
            gap_val = density_profile[L][N][1]
            diff = r - 0.75
            if L <= 30 or L % 5 == 0:
                print(f"  {L:>4} | {gap_val:>12.2e} | {r:>16.6f} | {diff:>+14.6f}")

        # 後半の平均比率
        if len(ratios) > 10:
            late_ratios = [r for _, r in ratios[-10:]]
            avg_late = sum(late_ratios) / len(late_ratios)
            print(f"  後半10点の平均比率: {avg_late:.6f} (3/4={0.75})")

    # --- 下界定理の形式 ---
    print(f"\n{'='*80}")
    print("下界定理の定量的評価")
    print(f"{'='*80}")

    print("\n命題: density(R(L)) >= 1 - C * alpha^L")
    print("ここで C, alpha は以下の通り:")

    # N=10^6 でのフィッティングを基準に
    N_ref = max(N_VALUES)
    gaps_ref = [(L, density_profile[L][N_ref][1]) for L in range(MAX_DEPTH + 1)]
    gaps_ref_pos = [(L, g) for L, g in gaps_ref if g > 0]

    C_best, alpha_best, r2_best = fit_exponential_decay(gaps_ref_pos, start_depth=5)

    if C_best is not None:
        print(f"\n  N = {N_ref:,} での最適フィット:")
        print(f"  C     = {C_best:.6f}")
        print(f"  alpha = {alpha_best:.6f}")
        print(f"  R^2   = {r2_best:.10f}")
        print(f"  理論的 alpha = 3/4 = 0.750000")

        # 下界の検証: 各Lで density >= 1 - C * alpha^L が成立するか
        print(f"\n  下界の検証 (N={N_ref:,}):")
        print(f"  {'深さ':>4} | {'実測density':>12} | {'下界 1-C*a^L':>14} | {'余裕':>12} | {'成立':>4}")
        print(f"  {'-'*60}")

        violations = 0
        for L in range(MAX_DEPTH + 1):
            density_actual = density_profile[L][N_ref][0]
            bound = 1.0 - C_best * alpha_best ** L
            margin = density_actual - bound
            ok = "OK" if margin >= -1e-10 else "NG"
            if margin < -1e-10:
                violations += 1
            if L <= 30 or L % 5 == 0:
                print(f"  {L:>4} | {density_actual:>12.8f} | {bound:>14.8f} | {margin:>+12.2e} | {ok:>4}")

        print(f"\n  違反数: {violations} / {MAX_DEPTH + 1}")

        # 安全な下界（全てのLで成立するC）の推定
        print(f"\n安全な下界定数の推定:")
        print(f"  alpha = {alpha_best:.6f} 固定で、全Lで density >= 1 - C_safe * alpha^L が成立する最小の C_safe:")

        max_C_needed = 0
        for L in range(MAX_DEPTH + 1):
            density_actual = density_profile[L][N_ref][0]
            gap_actual = 1.0 - density_actual
            alpha_L = alpha_best ** L
            if alpha_L > 1e-15:
                C_needed = gap_actual / alpha_L
                max_C_needed = max(max_C_needed, C_needed)

        print(f"  C_safe = {max_C_needed:.6f}")
        print(f"  下界: density(R(L)) >= 1 - {max_C_needed:.4f} * {alpha_best:.4f}^L")

        # alpha = 3/4 固定でも検証
        print(f"\n  alpha = 3/4 固定での安全な下界:")
        max_C_needed_34 = 0
        for L in range(MAX_DEPTH + 1):
            density_actual = density_profile[L][N_ref][0]
            gap_actual = 1.0 - density_actual
            alpha_L = 0.75 ** L
            if alpha_L > 1e-15:
                C_needed = gap_actual / alpha_L
                max_C_needed_34 = max(max_C_needed_34, C_needed)

        print(f"  C_safe(3/4) = {max_C_needed_34:.6f}")
        print(f"  下界: density(R(L)) >= 1 - {max_C_needed_34:.4f} * (3/4)^L")

    # --- 複数Nでの整合性チェック ---
    print(f"\n{'='*80}")
    print("N依存性: 異なるNでの alpha の安定性")
    print(f"{'='*80}")

    print(f"\n{'N':>10} | {'C':>10} | {'alpha':>10} | {'R^2':>12} | {'C_safe':>10} | {'C_safe(3/4)':>12}")
    print("-" * 75)

    for N in N_VALUES:
        gaps = [(L, density_profile[L][N][1]) for L in range(MAX_DEPTH + 1)]
        gaps_pos = [(L, g) for L, g in gaps if g > 0]

        C, alpha, r2 = fit_exponential_decay(gaps_pos, start_depth=5)

        if C is not None:
            # C_safe
            max_C = 0
            max_C_34 = 0
            for L in range(MAX_DEPTH + 1):
                d_actual = density_profile[L][N][0]
                g_actual = 1.0 - d_actual
                aL = alpha ** L
                if aL > 1e-15:
                    max_C = max(max_C, g_actual / aL)
                aL34 = 0.75 ** L
                if aL34 > 1e-15:
                    max_C_34 = max(max_C_34, g_actual / aL34)

            print(f"{N:>10,} | {C:>10.6f} | {alpha:>10.6f} | {r2:>12.8f} | {max_C:>10.6f} | {max_C_34:>12.6f}")

    # --- 到達に必要な最小深さの分布 ---
    print(f"\n{'='*80}")
    print("各整数の最小到達深さの分布")
    print(f"{'='*80}")

    # 最小到達深さを記録
    first_depth = {}
    for d in range(MAX_DEPTH + 1):
        for n in depth_sets.get(d, set()):
            if n not in first_depth:
                first_depth[n] = d

    # [1, N] 内の到達深さ分布
    for N in [1000, 10000]:
        depth_hist = defaultdict(int)
        not_reached = 0
        for x in range(1, N + 1):
            if x in first_depth:
                depth_hist[first_depth[x]] += 1
            else:
                not_reached += 1

        print(f"\n[1, {N:,}] 内の最小到達深さの分布:")
        print(f"  {'深さ':>4} | {'個数':>8} | {'割合':>8} | {'累積':>8}")
        print(f"  {'-'*40}")
        cumul = 0
        for d in sorted(depth_hist.keys()):
            cnt = depth_hist[d]
            cumul += cnt
            pct = cnt / N * 100
            cum_pct = cumul / N * 100
            if d <= 25 or d % 5 == 0 or cnt > 0:
                print(f"  {d:>4} | {cnt:>8,} | {pct:>7.2f}% | {cum_pct:>7.2f}%")
        if not_reached > 0:
            print(f"  未到達: {not_reached:,} ({not_reached/N*100:.2f}%)")
        else:
            print(f"  全数到達! (深さ{MAX_DEPTH}以内)")

        # 平均到達深さ
        total_depth = sum(d * c for d, c in depth_hist.items())
        reached_count = sum(depth_hist.values())
        if reached_count > 0:
            avg_depth = total_depth / reached_count
            print(f"  平均到達深さ: {avg_depth:.2f}")

    # --- 理論的考察 ---
    print(f"\n{'='*80}")
    print("理論的考察")
    print(f"{'='*80}")

    print("""
逆コラッツ木の成長率が 4/3 であるという事実から:
  |R(L)| ≈ C_0 * (4/3)^L

一方、R(L) 内の最大値は ≈ 2^L * 1 = 2^L のオーダーで成長する。
したがって [1, N] 内の被覆密度は:

  density(L, N) ≈ |R(L) ∩ [1,N]| / N

N が十分大きいとき、ギャップ gap(L) = 1 - density(L) は:
  - 逆木の各レベルで約 4/3 倍のノードが追加
  - しかし [1,N] 内の「新たにカバーされる」整数の割合は減少
  - gap は約 (3/4)^L の速さで減衰

これは以下の直観に基づく:
  - 各ステップで (2n-1)/3 分岐が約 1/3 の確率で発生
  - 2n 分岐は常に発生するが、値が大きくなるため [1,N] への寄与は減少
  - 正味の効果として、カバーされていない整数の割合が各ステップで約 3/4 倍に減少
""")

    print("=" * 80)
    print("解析完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
