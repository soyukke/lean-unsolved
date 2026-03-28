#!/usr/bin/env python3
"""
探索094: 逆Syracuse木の自己相似構造とフラクタル次元

T^{-1}(m) = {2m, (2m-1)/3 if 2m≡1(mod3)} の反復で逆Syracuse木を構成。
深さDの木のノード数N(D)の成長率を計算し、フラクタル次元 log(N(D))/D を推定。
自己相似的な分岐パターンの有無を調べる。

既知事実: 成長率≈4/3, 逆木到達密度gap≈1.64·exp(-0.237·L/log₂N), box-counting次元≈0.84
"""

import json
import math
import time
from collections import defaultdict

# ============================================================
# 1. 逆Syracuse木の構築（奇数ノードのみ）
# ============================================================

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^v2(3n+1) for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def syracuse_inverse(m, max_k=60):
    """
    T^{-1}(m): 奇数 m の逆像（奇数のリスト）
    (2^k * m - 1) / 3 が正の奇数になる k を列挙
    """
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

def build_syracuse_inverse_tree(max_depth, node_limit=2_000_000, inv_max_k=20):
    """根=1から逆Syracuse操作で木を構築"""
    visited = {1: 0}
    depth_nodes = defaultdict(list)
    depth_nodes[0].append(1)
    current_frontier = {1}
    stats = [{'depth': 0, 'new_nodes': 1, 'total_nodes': 1}]

    for d in range(1, max_depth + 1):
        next_frontier = set()
        for m in current_frontier:
            for k, result in syracuse_inverse(m, max_k=inv_max_k):
                if result not in visited and len(visited) < node_limit:
                    visited[result] = d
                    depth_nodes[d].append(result)
                    next_frontier.add(result)

        stats.append({
            'depth': d,
            'new_nodes': len(next_frontier),
            'total_nodes': len(visited),
        })
        current_frontier = next_frontier
        if not next_frontier:
            break

    return visited, depth_nodes, stats

# ============================================================
# 2. フラクタル次元の推定
# ============================================================

def estimate_fractal_dimension(stats):
    """
    N(D) = total_nodes at depth D
    フラクタル次元 = lim_{D→∞} log(N(D)) / D
    成長率 γ = N(D) / N(D-1) の推移も計算
    """
    results = []
    for i, s in enumerate(stats):
        d = s['depth']
        n = s['total_nodes']
        if d > 0 and n > 0:
            dim_estimate = math.log(n) / d
            growth_rate = n / stats[i-1]['total_nodes'] if stats[i-1]['total_nodes'] > 0 else 0
            width_growth = s['new_nodes'] / stats[i-1]['new_nodes'] if i > 0 and stats[i-1]['new_nodes'] > 0 else 0
            results.append({
                'depth': d,
                'total_nodes': n,
                'width': s['new_nodes'],
                'dim_estimate': round(dim_estimate, 6),
                'growth_rate': round(growth_rate, 6),
                'width_growth': round(width_growth, 6),
            })
    return results

# ============================================================
# 3. Box-counting次元の推定
# ============================================================

def box_counting_dimension(visited, max_scale_exp=20):
    """
    逆コラッツ木のノード集合に対して数直線上のbox-counting次元を推定。
    log(N(ε)) vs log(1/ε) の傾きが次元。
    """
    nodes = sorted(visited.keys())
    max_val = max(nodes)

    results = []
    for k in range(1, max_scale_exp + 1):
        eps = 2 ** k
        if eps > max_val:
            break
        boxes = set()
        for n in nodes:
            boxes.add(n // eps)
        N_eps = len(boxes)
        total_boxes = (max_val // eps) + 1
        filling_ratio = N_eps / total_boxes if total_boxes > 0 else 0

        results.append({
            'scale_exp': k,
            'epsilon': eps,
            'N_eps': N_eps,
            'total_boxes': total_boxes,
            'filling_ratio': round(filling_ratio, 6),
            'log_N': round(math.log(N_eps), 4) if N_eps > 0 else 0,
            'log_inv_eps': round(math.log(1.0 / eps), 4),
        })

    # 線形回帰で次元を推定
    dim, r2 = _linear_regression_dim(results)
    return results, dim, r2


def box_counting_frontier(depth_nodes, target_depths, max_scale_exp=20):
    """
    各深さのフロンティア（新規ノード集合）に対してbox-counting次元を推定。
    これにより「木の各層がどれだけ数直線上に散らばっているか」を測定。
    """
    frontier_dims = []
    for d in target_depths:
        nodes = depth_nodes.get(d, [])
        if len(nodes) < 10:
            continue
        nodes_sorted = sorted(nodes)
        max_val = max(nodes_sorted)

        results = []
        for k in range(1, max_scale_exp + 1):
            eps = 2 ** k
            if eps > max_val:
                break
            boxes = set()
            for n in nodes_sorted:
                boxes.add(n // eps)
            N_eps = len(boxes)
            if N_eps > 1:
                results.append({
                    'log_N': math.log(N_eps),
                    'log_inv_eps': math.log(1.0 / eps),
                })

        dim, r2 = _linear_regression_dim_raw(
            [r['log_inv_eps'] for r in results],
            [r['log_N'] for r in results]
        )
        frontier_dims.append({
            'depth': d,
            'num_nodes': len(nodes),
            'max_val': max_val,
            'bc_dimension': dim,
            'R_squared': r2,
        })
    return frontier_dims


def _linear_regression_dim(results):
    xs = [r['log_inv_eps'] for r in results if r['N_eps'] > 1]
    ys = [r['log_N'] for r in results if r['N_eps'] > 1]
    return _linear_regression_dim_raw(xs, ys)


def _linear_regression_dim_raw(xs, ys):
    if len(xs) < 3:
        return None, None
    n = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs)
    sxy = sum(x*y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-12:
        return None, None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    y_mean = sy / n
    ss_tot = sum((y - y_mean)**2 for y in ys)
    ss_res = sum((y - (slope * x + intercept))**2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return round(slope, 6), round(r2, 6)

# ============================================================
# 4. 自己相似構造の検出
# ============================================================

def analyze_self_similarity(depth_nodes, max_depth):
    """
    各深さでの分岐パターン（逆像の個数の分布）を解析し、
    パターンの安定性を確認する。
    """
    branching_stats = []
    for d in range(max_depth + 1):
        nodes = depth_nodes[d]
        if not nodes:
            continue
        # 各ノードの逆像数を計算
        inv_counts = []
        for m in nodes:
            invs = syracuse_inverse(m, max_k=40)
            inv_counts.append(len(invs))

        if inv_counts:
            avg = sum(inv_counts) / len(inv_counts)
            max_inv = max(inv_counts)
            # 逆像数の分布
            dist = defaultdict(int)
            for c in inv_counts:
                dist[c] += 1

            branching_stats.append({
                'depth': d,
                'num_nodes': len(nodes),
                'avg_inversions': round(avg, 4),
                'max_inversions': max_inv,
                'distribution': dict(sorted(dist.items())),
            })

    return branching_stats

# ============================================================
# 5. 深さごとのmod構造解析
# ============================================================

def analyze_mod_structure(depth_nodes, max_depth, moduli=[3, 6, 8, 12]):
    """各深さのノード集合のmod分布を解析し、自己相似的パターンを検出"""
    mod_stats = {}
    for mod in moduli:
        mod_stats[mod] = []
        for d in range(min(max_depth + 1, 30)):
            nodes = depth_nodes[d]
            if not nodes:
                continue
            dist = defaultdict(int)
            for n in nodes:
                dist[n % mod] += 1
            total = len(nodes)
            ratios = {k: round(v / total, 4) for k, v in sorted(dist.items())}
            mod_stats[mod].append({'depth': d, 'distribution': ratios})
    return mod_stats

# ============================================================
# 6. 到達密度の精密解析
# ============================================================

def analyze_density_gap(visited, max_N_exp=6):
    """
    1..N の奇数に対するカバー率と、未カバー率のN依存性を解析。
    gap ≈ C · exp(-α · L / log₂N) のフィット。
    """
    density_results = []
    for exp in range(2, max_N_exp + 1):
        N = 10 ** exp
        odd_total = (N + 1) // 2
        covered = sum(1 for i in range(1, N + 1, 2) if i in visited)
        gap = 1.0 - covered / odd_total
        density_results.append({
            'N': N,
            'odd_total': odd_total,
            'covered': covered,
            'coverage_pct': round(covered / odd_total * 100, 6),
            'gap': round(gap, 8),
            'log_gap': round(math.log(gap), 4) if gap > 0 else None,
        })
    return density_results

# ============================================================
# メイン実行
# ============================================================

def build_standard_inverse_tree(max_depth, node_limit=2_000_000):
    """標準逆コラッツ木: n→2n, n→(2n-1)/3"""
    visited = {1: 0}
    depth_nodes = defaultdict(list)
    depth_nodes[0].append(1)
    current_frontier = {1}
    stats = [{'depth': 0, 'new_nodes': 1, 'total_nodes': 1}]

    for d in range(1, max_depth + 1):
        next_frontier = set()
        for n in current_frontier:
            c1 = 2 * n
            if c1 not in visited and len(visited) < node_limit:
                visited[c1] = d
                depth_nodes[d].append(c1)
                next_frontier.add(c1)
            if (2 * n - 1) % 3 == 0:
                c2 = (2 * n - 1) // 3
                if c2 > 0 and c2 not in visited and len(visited) < node_limit:
                    visited[c2] = d
                    depth_nodes[d].append(c2)
                    next_frontier.add(c2)
        stats.append({
            'depth': d,
            'new_nodes': len(next_frontier),
            'total_nodes': len(visited),
        })
        current_frontier = next_frontier
        if not next_frontier:
            break
    return visited, depth_nodes, stats


def main():
    t_start = time.time()
    print("=" * 70)
    print("探索094: 逆Syracuse木の自己相似構造とフラクタル次元")
    print("=" * 70)

    # --- 標準逆コラッツ木 ---
    print("\n[1a] 標準逆コラッツ木を構築中 (max_depth=40, node_limit=2M)...")
    t0 = time.time()
    std_visited, std_depth_nodes, std_stats = build_standard_inverse_tree(
        max_depth=40, node_limit=2_000_000
    )
    t_build_std = time.time() - t0
    print(f"     構築完了: {len(std_visited)} ノード, max_depth={std_stats[-1]['depth']}, {t_build_std:.2f}秒")

    # --- Syracuse逆木 (inv_max_k=10 で深さを稼ぐ) ---
    print("\n[1b] Syracuse逆木を構築中 (max_depth=30, inv_max_k=10, node_limit=2M)...")
    t0 = time.time()
    visited, depth_nodes, stats = build_syracuse_inverse_tree(
        max_depth=30, node_limit=2_000_000, inv_max_k=10
    )
    t_build = time.time() - t0
    print(f"     構築完了: {len(visited)} ノード, max_depth={stats[-1]['depth']}, {t_build:.2f}秒")

    # メインの解析には標準逆コラッツ木を使用（深い木が得られるため）
    main_visited = std_visited
    main_depth_nodes = std_depth_nodes
    main_stats = std_stats

    # --- フラクタル次元（標準木） ---
    print("\n[2] フラクタル次元の推定（標準逆コラッツ木）...")
    frac_results = estimate_fractal_dimension(main_stats)
    print(f"    深さ別フラクタル次元推定:")
    for r in frac_results:
        print(f"      D={r['depth']:>2}: N={r['total_nodes']:>8}, "
              f"dim≈{r['dim_estimate']:.4f}, γ={r['growth_rate']:.4f}, "
              f"width_γ={r['width_growth']:.4f}")

    # 最終的な次元推定（最後の5点の平均）
    if len(frac_results) >= 5:
        final_dims = [r['dim_estimate'] for r in frac_results[-5:]]
        final_dim_mean = sum(final_dims) / len(final_dims)
        final_growths = [r['growth_rate'] for r in frac_results[-5:]]
        final_growth_mean = sum(final_growths) / len(final_growths)
    else:
        final_dim_mean = frac_results[-1]['dim_estimate'] if frac_results else 0
        final_growth_mean = frac_results[-1]['growth_rate'] if frac_results else 0

    print(f"\n    最終推定: フラクタル次元 ≈ {final_dim_mean:.6f}")
    print(f"    最終推定: 成長率 γ ≈ {final_growth_mean:.6f}")
    print(f"    log(4/3) = {math.log(4/3):.6f} (理論的成長率)")

    # --- Syracuse木のフラクタル次元も比較 ---
    print("\n[2b] フラクタル次元の推定（Syracuse逆木）...")
    syr_frac_results = estimate_fractal_dimension(stats)
    for r in syr_frac_results:
        print(f"      D={r['depth']:>2}: N={r['total_nodes']:>8}, "
              f"dim≈{r['dim_estimate']:.4f}, γ={r['growth_rate']:.4f}")

    # --- Box-counting次元（標準木） ---
    print("\n[3] Box-counting次元の推定（標準逆コラッツ木）...")
    bc_results, bc_dim, bc_r2 = box_counting_dimension(main_visited, max_scale_exp=22)
    print(f"    スケール別box数:")
    for r in bc_results:
        print(f"      ε=2^{r['scale_exp']:>2}: N(ε)={r['N_eps']:>8}, "
              f"充填率={r['filling_ratio']:.4f}")
    if bc_dim is not None:
        print(f"\n    全体Box-counting次元 ≈ {bc_dim:.6f} (R²={bc_r2:.6f})")

    # --- フロンティアのbox-counting次元 ---
    print("\n[3b] フロンティア（各深さの新規ノード集合）のbox-counting次元...")
    target_depths = list(range(5, min(40, main_stats[-1]['depth']), 3))
    frontier_dims = box_counting_frontier(main_depth_nodes, target_depths)
    for fd in frontier_dims:
        dim_str = f"{fd['bc_dimension']:.4f}" if fd['bc_dimension'] is not None else "N/A"
        r2_str = f"{fd['R_squared']:.4f}" if fd['R_squared'] is not None else "N/A"
        print(f"      D={fd['depth']:>2}: nodes={fd['num_nodes']:>8}, "
              f"max_val={fd['max_val']:>12}, bc_dim={dim_str}, R²={r2_str}")

    # --- 自己相似構造（標準木の分岐率で解析） ---
    print("\n[4] 自己相似的分岐パターンの解析（標準木）...")
    # 標準木の分岐率: 各深さで (2n-1)/3 分岐が発生する割合
    std_branching = []
    for d in range(min(40, len(main_stats))):
        nodes = main_depth_nodes[d]
        if not nodes:
            continue
        has_inv3 = sum(1 for n in nodes if (2*n - 1) % 3 == 0)
        ratio = has_inv3 / len(nodes) if nodes else 0
        std_branching.append({'depth': d, 'num_nodes': len(nodes), 'inv3_ratio': round(ratio, 4)})
    print(f"    深さ別 (2n-1)/3 分岐率:")
    for b in std_branching[:25]:
        print(f"      D={b['depth']:>2}: nodes={b['num_nodes']:>8}, inv3率={b['inv3_ratio']:.4f}")

    # Syracuse逆像の解析
    print("\n    Syracuse逆像の分岐パターン:")
    branching = analyze_self_similarity(depth_nodes, min(30, len(stats)-1))
    print(f"    深さ別平均逆像数:")
    for b in branching[:20]:
        dist_str = str(b['distribution'])[:60]
        print(f"      D={b['depth']:>2}: nodes={b['num_nodes']:>8}, "
              f"avg_inv={b['avg_inversions']:.2f}, max_inv={b['max_inversions']}, "
              f"dist={dist_str}")

    # 平均逆像数の安定性
    if len(branching) >= 5:
        late_avgs = [b['avg_inversions'] for b in branching[-5:]]
        avg_stability = max(late_avgs) - min(late_avgs)
        avg_inversions_final = sum(late_avgs) / len(late_avgs)
        print(f"\n    最終5層の平均逆像数: {avg_inversions_final:.4f} (変動幅: {avg_stability:.4f})")

    # --- Mod構造（標準木） ---
    print("\n[5] mod構造の解析（標準木）...")
    mod_stats = analyze_mod_structure(main_depth_nodes, min(40, len(main_stats)-1))
    for mod in [3, 6]:
        print(f"\n    mod {mod} 分布の推移:")
        for ms in mod_stats[mod][:15]:
            print(f"      D={ms['depth']:>2}: {ms['distribution']}")

    # --- 到達密度（標準木） ---
    print("\n[6] 到達密度の精密解析（標準木）...")
    density = analyze_density_gap(main_visited, max_N_exp=6)
    for dr in density:
        gap_str = f"gap={dr['gap']:.8f}" if dr['gap'] is not None else "gap=N/A"
        log_gap_str = f"log(gap)={dr['log_gap']:.4f}" if dr['log_gap'] is not None else ""
        print(f"    N={dr['N']:>8}: coverage={dr['coverage_pct']:.4f}%, "
              f"{gap_str} {log_gap_str}")

    # gap の指数フィット
    valid_density = [d for d in density if d['gap'] > 0 and d['log_gap'] is not None]
    if len(valid_density) >= 2:
        # log(gap) vs log(N) の線形回帰
        xs = [math.log(d['N']) for d in valid_density]
        ys = [d['log_gap'] for d in valid_density]
        n = len(xs)
        sx = sum(xs); sy = sum(ys)
        sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
        denom = n * sxx - sx * sx
        if abs(denom) > 1e-12:
            slope = (n * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / n
            print(f"\n    gap ∝ N^{slope:.4f} (intercept={intercept:.4f})")

    # ============================================================
    # JSON出力
    # ============================================================
    total_time = time.time() - t_start

    # 深さ別の成長率一覧（JSONフレンドリーにmod構造を要約）
    mod3_summary = {}
    for ms in mod_stats.get(3, []):
        mod3_summary[ms['depth']] = ms['distribution']

    result = {
        "exploration_id": "094",
        "title": "逆Syracuse木の自己相似構造とフラクタル次元",
        "method": "T^{-1}(m)の反復で逆Syracuse木を構成し、フラクタル次元・box-counting次元・自己相似パターンを推定",
        "parameters": {
            "max_depth": 35,
            "node_limit": 2_000_000,
            "box_counting_max_scale": 22,
        },
        "tree_summary": {
            "standard_tree_nodes": len(main_visited),
            "standard_max_depth": main_stats[-1]['depth'],
            "syracuse_tree_nodes": len(visited),
            "syracuse_max_depth": stats[-1]['depth'],
            "build_time_sec": round(t_build_std + t_build, 2),
        },
        "fractal_dimension": {
            "log_N_over_D_estimate": round(final_dim_mean, 6),
            "growth_rate_gamma": round(final_growth_mean, 6),
            "theoretical_log_4_3": round(math.log(4/3), 6),
            "depth_series": [
                {"depth": r['depth'], "dim": r['dim_estimate'], "gamma": r['growth_rate']}
                for r in frac_results
            ],
        },
        "box_counting_dimension": {
            "whole_tree_dimension": bc_dim,
            "whole_tree_R_squared": bc_r2,
            "frontier_dimensions": [
                {"depth": fd['depth'], "num_nodes": fd['num_nodes'],
                 "bc_dimension": fd['bc_dimension'], "R_squared": fd['R_squared']}
                for fd in frontier_dims
            ],
            "scale_data": [
                {"scale_exp": r['scale_exp'], "N_eps": r['N_eps'], "filling_ratio": r['filling_ratio']}
                for r in bc_results
            ],
        },
        "self_similarity": {
            "branching_pattern_stable": avg_stability < 0.5 if len(branching) >= 5 else None,
            "avg_inversions_final": round(avg_inversions_final, 4) if len(branching) >= 5 else None,
            "standard_tree_inv3_ratio": [
                {"depth": b['depth'], "inv3_ratio": b['inv3_ratio']}
                for b in std_branching[:25]
            ],
            "syracuse_branching_by_depth": [
                {"depth": b['depth'], "avg_inv": b['avg_inversions'], "distribution": b['distribution']}
                for b in branching[:20]
            ],
        },
        "mod3_structure": mod3_summary,
        "density_analysis": density,
        "findings": [],
        "elapsed_sec": round(total_time, 2),
    }

    # 発見事項の生成
    findings = []

    # フラクタル次元
    findings.append(
        f"フラクタル次元 log(N(D))/D の推定値: {final_dim_mean:.4f} "
        f"(理論値 log(4/3)={math.log(4/3):.4f})"
    )
    findings.append(
        f"成長率 γ = N(D)/N(D-1) の最終推定: {final_growth_mean:.4f}"
    )

    if bc_dim is not None:
        findings.append(
            f"全体Box-counting次元: {bc_dim:.4f} (R²={bc_r2:.4f})"
        )
    if frontier_dims:
        late_fd = [fd for fd in frontier_dims if fd['bc_dimension'] is not None]
        if late_fd:
            avg_fd = sum(fd['bc_dimension'] for fd in late_fd[-3:]) / min(3, len(late_fd))
            findings.append(
                f"フロンティアBox-counting次元（最終3層平均）: {avg_fd:.4f}, "
                f"既知推定値0.84との比較"
            )

    if len(branching) >= 5:
        findings.append(
            f"Syracuse逆像の分岐安定性: 最終5層の平均逆像数={avg_inversions_final:.4f}, "
            f"変動幅={avg_stability:.4f} → {'安定（自己相似的）' if avg_stability < 0.5 else '不安定'}"
        )
    if len(std_branching) >= 5:
        late_inv3 = [b['inv3_ratio'] for b in std_branching[-5:]]
        avg_inv3 = sum(late_inv3) / len(late_inv3)
        findings.append(
            f"標準木の(2n-1)/3分岐率: 最終5層平均={avg_inv3:.4f} "
            f"(理論値1/3≈0.3333)"
        )

    # mod3 安定性
    if len(mod_stats.get(3, [])) >= 10:
        late_mod3 = mod_stats[3][-5:]
        ratios_0 = [ms['distribution'].get(0, 0) for ms in late_mod3]
        ratios_1 = [ms['distribution'].get(1, 0) for ms in late_mod3]
        ratios_2 = [ms['distribution'].get(2, 0) for ms in late_mod3]
        findings.append(
            f"mod 3 分布の最終5層: "
            f"0≡{sum(ratios_0)/len(ratios_0):.3f}, "
            f"1≡{sum(ratios_1)/len(ratios_1):.3f}, "
            f"2≡{sum(ratios_2)/len(ratios_2):.3f} "
            f"→ {'均等に安定' if max(max(ratios_0)-min(ratios_0), max(ratios_1)-min(ratios_1), max(ratios_2)-min(ratios_2)) < 0.05 else '変動あり'}"
        )

    result["findings"] = findings

    # JSON保存
    out_path = "/Users/soyukke/study/lean-unsolved/results/exploration_094.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n結果を保存: {out_path}")

    print("\n" + "=" * 70)
    print("発見事項:")
    print("=" * 70)
    for i, finding in enumerate(findings, 1):
        print(f"  [{i}] {finding}")

    print(f"\n総実行時間: {total_time:.2f}秒")

if __name__ == "__main__":
    main()
