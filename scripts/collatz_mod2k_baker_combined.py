#!/usr/bin/env python3
"""
mod 2^k 下降マップの固定点集合とBaker排除の拡張

目標:
1. mod 2^k (k=10..20) で Syracuse 1ステップ下降 T(n)<n となる残基を完全分類
2. Baker定理と組合せてサイクル排除の範囲を拡張
3. 非排除残基のサイクル可能性を分析

キーアイデア:
- mod 2^k で「下降しない」残基はサイクルの候補
- 周期pのサイクルに属する全てのnは、各ステップで特定のv2値を持つ
- mod 2^k の情報で、可能なv2パターンを制限できる
- Baker排除で不可能なパターンを除外 → 排除範囲を拡張
"""

import math
import json
import time
from collections import Counter, defaultdict
from fractions import Fraction

LOG2 = math.log(2)
LOG3 = math.log(3)
LOG2_3 = LOG3 / LOG2


def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def syracuse(n):
    """Syracuse map: odd n -> (3n+1)/2^v"""
    val = 3 * n + 1
    v = v2(val)
    return val >> v, v


# =====================================================================
# Part 1: mod 2^k での下降マップ完全分類
# =====================================================================

def classify_descent_mod2k(k, multi_step_depth=10):
    """
    mod 2^k の各奇数残基 r に対して:
    - 1ステップ下降: T(r mod 2^k) < r mod 2^k が全ての十分大きいnで成立
    - 多ステップ下降: d回のSyracuse適用で下降
    - 非排除: 決定的に下降しない

    返り値: 分類結果と統計
    """
    mod = 2 ** k
    total_odd = mod // 2

    # 各残基の分類
    one_step_desc = 0      # 1ステップ下降
    multi_step_desc = 0    # 多ステップ下降 (2..multi_step_depth)
    non_excluded = []       # 非排除

    desc_by_step = Counter()  # ステップ数ごとの分布
    v2_distribution = Counter()  # v2(3r+1) の分布

    for r in range(1, mod, 2):
        # v2(3r+1) を計算
        val = 3 * r + 1
        v = v2(val)
        v2_distribution[v] += 1

        # 記号的追跡: n = mod*j + r のSyracuse反復
        excluded, step = symbolic_descent(r, mod, multi_step_depth)

        if excluded and step == 1:
            one_step_desc += 1
            desc_by_step[1] += 1
        elif excluded:
            multi_step_desc += 1
            desc_by_step[step] += 1
        else:
            non_excluded.append(r)

    return {
        'k': k,
        'mod': mod,
        'total_odd': total_odd,
        'one_step_desc': one_step_desc,
        'multi_step_desc': multi_step_desc,
        'non_excluded_count': len(non_excluded),
        'excluded_ratio': (one_step_desc + multi_step_desc) / total_odd,
        'desc_by_step': dict(desc_by_step),
        'v2_distribution': dict(v2_distribution),
        'non_excluded_residues': non_excluded[:200],  # 先頭200個のみ
    }


def symbolic_descent(r, mod, max_depth=10):
    """
    記号的Syracuse追跡: n = mod*j + r に対してT反復。
    係数が確定的に下降するか判定。
    """
    a, b = mod, r  # n = a*j + b

    for depth in range(1, max_depth + 1):
        if b % 2 == 0:
            if a % 2 == 0:
                a //= 2
                b //= 2
                continue
            else:
                return False, depth  # パリティ分岐

        # 奇数: T(n) = (3n+1) / 2^v
        new_a = 3 * a
        new_b = 3 * b + 1
        v_b = v2(new_b)
        v_a = v2(new_a)

        if v_a >= v_b:
            divisor = 2 ** v_b
            a = new_a // divisor
            b = new_b // divisor

            # n' = a'*j + b', 元のn = mod*j + r
            # n' < n ⟺ a'*j + b' < mod*j + r ⟺ (a' - mod)*j < r - b'
            coeff_diff = a - mod
            const_diff = r - b

            if coeff_diff < 0:
                # a' < mod: 十分大きいjで確実にn' < n
                return True, depth
            elif coeff_diff == 0 and const_diff > 0:
                return True, depth
        else:
            return False, depth  # v2分岐

    return False, max_depth


# =====================================================================
# Part 2: 非排除残基のサイクル整合性検査
# =====================================================================

def check_cycle_compatibility(non_excluded, mod, p_max=20):
    """
    非排除残基がサイクルの一部になれるかを検査。

    周期pのサイクルでは: n_1 → n_2 → ... → n_p → n_1
    各 n_i mod 2^k が非排除残基でなければならない（排除残基なら必ず下降する）。

    さらに、v2パターンの整合性を検査。
    """
    ne_set = set(non_excluded)
    results = {}

    for p in range(1, min(p_max + 1, 15)):
        # 周期pの最小s
        s_min = math.ceil(p * LOG2_3)
        if s_min > 0 and 2**s_min <= 3**p:
            s_min += 1

        # v2パターン (v_1,...,v_p) で s = sum(v_i) となるもの
        # ただし各v_i >= 1
        # 非排除残基のv2値のみ許容

        allowed_v2 = set()
        for r in non_excluded:
            v = v2(3 * r + 1)
            allowed_v2.add(v)

        # v2パターンの制約
        # 実際にはmod 2^kで見たv2(3r+1)の値で制限される
        v2_from_ne = Counter()
        for r in non_excluded:
            v = v2(3 * r + 1)
            v2_from_ne[v] += 1

        results[p] = {
            'allowed_v2_values': sorted(allowed_v2),
            'v2_count_from_ne': dict(v2_from_ne),
            's_min': s_min,
        }

    return results


def trace_non_excluded_orbit(non_excluded, mod, max_orbit=50):
    """
    非排除残基から出発してSyracuse反復を追跡し、
    次のステップでmod上の残基がどの集合に入るか分析。

    サイクルが存在するなら、軌道は非排除残基の中で閉じなければならない。
    """
    ne_set = set(non_excluded)

    # 遷移先の分析
    stays_in_ne = 0
    leaves_ne = 0
    transitions = defaultdict(int)

    for r in non_excluded:
        # T(r) mod 2^k (代表値で計算)
        # 実際の遷移はrに依存するが、mod 2^k での計算
        val = 3 * r + 1
        v = v2(val)
        t_r = (val >> v) % mod

        if t_r in ne_set:
            stays_in_ne += 1
            transitions[('ne', 'ne')] += 1
        else:
            leaves_ne += 1
            transitions[('ne', 'ex')] += 1

    return {
        'total_ne': len(non_excluded),
        'stays_in_ne': stays_in_ne,
        'leaves_ne': leaves_ne,
        'stay_ratio': stays_in_ne / len(non_excluded) if non_excluded else 0,
    }


# =====================================================================
# Part 3: Baker排除 + mod 2^k の交差分析
# =====================================================================

def numerator_for_pattern(vs):
    """パターン (v_1,...,v_p) に対する分子 C"""
    p = len(vs)
    C = 0
    for j in range(p):
        sigma_j = sum(vs[j+1:])
        C += (3 ** j) * (2 ** sigma_j)
    return C


def baker_mod2k_combined_exclusion(k, p_max=15):
    """
    Baker排除 + mod 2^k の組合せ排除。

    手法:
    1. mod 2^k で非排除の残基集合 NE(k) を求める
    2. 周期pのサイクルでは全ステップで非排除残基を経由
    3. mod 2^k での v2(3r+1) の制約をBakerパターン列挙に適用
    4. 制約付きパターンだけを検査 → 排除範囲拡張
    """
    mod = 2 ** k

    # Step 1: 非排除残基の分類
    non_excluded = []
    ne_v2_vals = set()

    for r in range(1, mod, 2):
        excluded, _ = symbolic_descent(r, mod, max_depth=15)
        if not excluded:
            non_excluded.append(r)
            v = v2(3 * r + 1)
            ne_v2_vals.add(v)

    ne_set = set(non_excluded)

    # Step 2: 非排除残基間の遷移グラフ
    # r -> T(r) mod 2^k が非排除に留まるかチェック
    ne_transitions = {}
    for r in non_excluded:
        val = 3 * r + 1
        v = v2(val)
        t_r = (val >> v) % mod
        # t_r が奇数でなければ偶数の場合は /2 を繰り返す
        while t_r % 2 == 0 and t_r > 0:
            t_r //= 2
        if t_r in ne_set:
            ne_transitions[r] = (t_r, v)

    # Step 3: 閉じたサイクルの探索（非排除残基内）
    cycles_found = []
    visited_global = set()

    for start in non_excluded:
        if start in visited_global:
            continue

        path = [start]
        visited = {start: 0}
        current = start

        for step in range(min(p_max * 2, 50)):
            if current not in ne_transitions:
                break

            next_r, v = ne_transitions[current]

            if next_r in visited:
                cycle_start = visited[next_r]
                cycle = path[cycle_start:]
                if len(cycle) <= p_max:
                    cycles_found.append(cycle)
                break

            visited[next_r] = len(path)
            path.append(next_r)
            visited_global.add(next_r)
            current = next_r

    # Step 4: v2制約付きBakerパターンカウント
    baker_with_constraint = {}
    for p in range(1, min(p_max + 1, 12)):
        s_min = math.ceil(p * LOG2_3)
        if 2**s_min <= 3**p:
            s_min += 1

        # 制約なしのパターン数
        total_unconstrained = 0
        total_constrained = 0

        for s in range(s_min, s_min + 10):
            D = 2**s - 3**p
            if D <= 0:
                continue

            # 制約なし: v_i >= 1, sum = s
            from math import comb
            if s >= p:
                n_unconstrained = comb(s - 1, p - 1)
            else:
                n_unconstrained = 0

            # 制約あり: 各v_i は ne_v2_vals に含まれる値のみ
            # (近似: allowed_v2 の最大値で制限)
            n_constrained = count_constrained_patterns(p, s, ne_v2_vals)

            total_unconstrained += n_unconstrained
            total_constrained += n_constrained

        baker_with_constraint[p] = {
            'unconstrained': total_unconstrained,
            'constrained': total_constrained,
            'reduction_ratio': total_constrained / total_unconstrained if total_unconstrained > 0 else 0,
        }

    return {
        'k': k,
        'ne_count': len(non_excluded),
        'ne_ratio': len(non_excluded) / (mod // 2),
        'ne_v2_values': sorted(ne_v2_vals),
        'ne_transition_count': len(ne_transitions),
        'ne_transition_ratio': len(ne_transitions) / len(non_excluded) if non_excluded else 0,
        'cycles_in_ne': cycles_found,
        'baker_constraint': baker_with_constraint,
    }


def count_constrained_patterns(p, s, allowed_v2, max_v=30):
    """
    v_i in allowed_v2, sum(v_i)=s のパターン数を動的計画法で計算。
    """
    allowed = sorted([v for v in allowed_v2 if v <= s - p + 1])
    if not allowed:
        return 0

    # dp[i][j] = i個のv_iを選んで合計jのパターン数
    # メモリ効率のため1次元化
    dp_prev = [0] * (s + 1)
    dp_prev[0] = 1

    for i in range(p):
        dp_curr = [0] * (s + 1)
        for j in range(s + 1):
            if dp_prev[j] == 0:
                continue
            for v in allowed:
                if j + v <= s:
                    dp_curr[j + v] += dp_prev[j]
        dp_prev = dp_curr

    return dp_prev[s]


# =====================================================================
# Part 4: 漸近密度分析
# =====================================================================

def asymptotic_density_analysis(k_range=range(6, 19)):
    """
    k を増やしたときの排除率・非排除残基数の漸近挙動。
    """
    results = []

    for k in k_range:
        t0 = time.time()
        mod = 2 ** k
        total_odd = mod // 2

        excluded_count = 0
        ne_count = 0
        ne_v2_dist = Counter()
        ne_mod4 = Counter()
        ne_mod8 = Counter()
        ne_mod16 = Counter()
        ne_trailing = Counter()

        for r in range(1, mod, 2):
            ex, _ = symbolic_descent(r, mod, max_depth=15)
            if ex:
                excluded_count += 1
            else:
                ne_count += 1
                ne_v2_dist[v2(3 * r + 1)] += 1
                ne_mod4[r % 4] += 1
                ne_mod8[r % 8] += 1
                ne_mod16[r % 16] += 1
                # trailing 1s count
                t = 0
                x = r
                while x & 1:
                    t += 1
                    x >>= 1
                ne_trailing[t] += 1

        elapsed = time.time() - t0

        results.append({
            'k': k,
            'mod': mod,
            'total_odd': total_odd,
            'excluded': excluded_count,
            'ne_count': ne_count,
            'excluded_ratio': excluded_count / total_odd,
            'ne_ratio': ne_count / total_odd,
            'ne_v2_dist': dict(ne_v2_dist),
            'ne_mod4': dict(ne_mod4),
            'ne_mod8': dict(ne_mod8),
            'ne_trailing': dict(ne_trailing),
            'elapsed': elapsed,
        })

        print(f"  k={k:>2}: excluded={excluded_count:>8}/{total_odd:>8} "
              f"({excluded_count/total_odd*100:.2f}%), ne={ne_count:>6}, "
              f"t={elapsed:.2f}s")

    return results


# =====================================================================
# Part 5: 非排除残基のサイクル整合性の深い分析
# =====================================================================

def deep_cycle_analysis(k=12, p_max=15):
    """
    mod 2^k の非排除残基がサイクルの一部になれるかの精密検査。

    周期pのサイクル条件:
    (2^s - 3^p) * n_1 = C(v_1,...,v_p)

    mod 2^k での整合条件:
    n_i mod 2^k は非排除残基でなければならない
    v_i = v2(3*n_i + 1) はmod 2^kで決定される

    従って:
    非排除残基の遷移グラフ内の長さpの閉路が存在しなければ、
    mod 2^k レベルで周期pのサイクルは不可能。
    """
    mod = 2 ** k

    # 非排除残基を求める
    non_excluded = []
    for r in range(1, mod, 2):
        ex, _ = symbolic_descent(r, mod, max_depth=20)
        if not ex:
            non_excluded.append(r)

    ne_set = set(non_excluded)

    # 遷移グラフ構築
    # r -> set of possible T(r) mod 2^k values (非排除内のみ)
    graph = defaultdict(set)
    v2_map = {}

    for r in non_excluded:
        val = 3 * r + 1
        v = v2(val)
        t_r = (val >> v) % mod
        # t_r を奇数にする
        while t_r % 2 == 0 and t_r > 0:
            t_r //= 2
        v2_map[r] = v

        if t_r in ne_set:
            graph[r].add(t_r)

    # 長さ p の閉路をDFSで探索
    cycle_results = {}
    for p in range(1, min(p_max + 1, 10)):
        cycles = find_cycles_length_p(graph, non_excluded, p)
        cycle_results[p] = {
            'cycle_count': len(cycles),
            'examples': cycles[:5],  # 最大5例
        }

    return {
        'k': k,
        'ne_count': len(non_excluded),
        'graph_edges': sum(len(v) for v in graph.values()),
        'nodes_with_edges': len(graph),
        'cycle_results': cycle_results,
        'v2_map_sample': {r: v2_map[r] for r in non_excluded[:20]},
    }


def find_cycles_length_p(graph, nodes, p):
    """長さ p の閉路を探索 (BFS/DFS)"""
    cycles = []
    if p > 8:
        return []  # 計算量制約

    for start in nodes[:min(len(nodes), 500)]:  # 開始点を制限
        # 深さpのDFS
        stack = [(start, [start])]
        while stack:
            current, path = stack.pop()
            if len(path) == p:
                # pathの最後からstartに戻るか？
                if start in graph.get(current, set()):
                    # v2パターンを抽出
                    vs = []
                    for r in path:
                        vs.append(v2(3 * r + 1))
                    cycle_repr = tuple(sorted(path))
                    if cycle_repr not in [tuple(sorted(c['path'])) for c in cycles]:
                        cycles.append({'path': path[:], 'vs': vs})
                continue

            for next_node in graph.get(current, set()):
                if len(path) < p - 1:
                    if next_node not in path:  # 中間で繰り返さない
                        stack.append((next_node, path + [next_node]))
                elif len(path) == p - 1:
                    # 最後のステップ: next_node は start でなくてよいが
                    # 次にstartに戻れるかを上で確認
                    if next_node not in path:
                        stack.append((next_node, path + [next_node]))

    return cycles


# =====================================================================
# メイン
# =====================================================================

def main():
    t_start = time.time()
    output = {}

    print("=" * 80)
    print("mod 2^k 下降マップの固定点集合とBaker排除の拡張")
    print("=" * 80)

    # --- Part 1: 漸近密度分析 ---
    print("\n## Part 1: mod 2^k 排除率の漸近分析 (k=6..18)")
    print("-" * 60)

    density_results = asymptotic_density_analysis(range(6, 19))
    output['density'] = density_results

    # 非排除残基の増加率を計算
    print("\n  k  | ne_count | ne_ratio | growth_ratio")
    print("  " + "-" * 50)
    for i in range(1, len(density_results)):
        prev = density_results[i-1]
        curr = density_results[i]
        growth = curr['ne_count'] / prev['ne_count'] if prev['ne_count'] > 0 else 0
        print(f"  {curr['k']:>2} | {curr['ne_count']:>8} | {curr['ne_ratio']:.6f} | {growth:.4f}")

    # --- Part 2: 非排除残基の遷移分析 ---
    print("\n\n## Part 2: 非排除残基の遷移グラフ分析")
    print("-" * 60)

    for k in [10, 12, 14]:
        print(f"\n  k={k}:")
        mod = 2 ** k
        ne_list = []
        for r in range(1, mod, 2):
            ex, _ = symbolic_descent(r, mod, max_depth=15)
            if not ex:
                ne_list.append(r)

        transit = trace_non_excluded_orbit(ne_list, mod)
        print(f"    非排除残基: {transit['total_ne']}")
        print(f"    NE内遷移: {transit['stays_in_ne']} ({transit['stay_ratio']:.4f})")
        print(f"    NE外遷移: {transit['leaves_ne']}")
        output[f'transition_k{k}'] = transit

    # --- Part 3: Baker + mod 2^k 組合せ排除 ---
    print("\n\n## Part 3: Baker + mod 2^k 組合せ排除分析")
    print("-" * 60)

    for k in [10, 12]:
        print(f"\n  k={k}:")
        combined = baker_mod2k_combined_exclusion(k, p_max=12)
        print(f"    非排除残基: {combined['ne_count']} ({combined['ne_ratio']:.4f})")
        print(f"    許容v2値: {combined['ne_v2_values']}")
        print(f"    NE内遷移率: {combined['ne_transition_ratio']:.4f}")
        print(f"    NE内サイクル: {len(combined['cycles_in_ne'])}個")

        print(f"    Baker制約付きパターン削減率:")
        for p, info in combined['baker_constraint'].items():
            if info['unconstrained'] > 0:
                print(f"      p={p}: {info['constrained']}/{info['unconstrained']} "
                      f"= {info['reduction_ratio']:.4f}")

        output[f'combined_k{k}'] = combined

    # --- Part 4: サイクル閉路の深い分析 ---
    print("\n\n## Part 4: 非排除残基のサイクル閉路分析")
    print("-" * 60)

    for k in [10, 12]:
        print(f"\n  k={k}:")
        cycle_analysis = deep_cycle_analysis(k, p_max=8)
        print(f"    非排除残基数: {cycle_analysis['ne_count']}")
        print(f"    遷移グラフ辺数: {cycle_analysis['graph_edges']}")
        print(f"    辺を持つ頂点数: {cycle_analysis['nodes_with_edges']}")

        for p, info in cycle_analysis['cycle_results'].items():
            n_cycles = info['cycle_count']
            if n_cycles > 0:
                print(f"    長さ{p}閉路: {n_cycles}個")
                for c in info['examples'][:3]:
                    print(f"      path={c['path']}, vs={c['vs']}")
            else:
                print(f"    長さ{p}閉路: なし")

        output[f'cycle_k{k}'] = cycle_analysis

    # --- Part 5: 新しい発見の整理 ---
    print("\n\n## Part 5: 核心的発見と仮説")
    print("=" * 60)

    # 漸近分析
    if len(density_results) >= 3:
        ne_ratios = [r['ne_ratio'] for r in density_results]
        growth_rates = []
        for i in range(1, len(density_results)):
            if density_results[i-1]['ne_count'] > 0:
                growth_rates.append(
                    density_results[i]['ne_count'] / density_results[i-1]['ne_count']
                )

        print(f"\n  1. 非排除率の漸近: {ne_ratios[-1]:.6f} (k={density_results[-1]['k']})")
        if growth_rates:
            avg_growth = sum(growth_rates[-3:]) / min(3, len(growth_rates[-3:]))
            print(f"     非排除残基の増加率 (最近3ステップ平均): {avg_growth:.4f}")
            # 理論予測: 増加率が2未満なら密度は0に収束
            if avg_growth < 2:
                print(f"     → 増加率 < 2 → 非排除密度は0に収束 (指数的減衰)")
                predicted_limit = 0
            else:
                predicted_limit = 1 - 1 / avg_growth
                print(f"     → 増加率 >= 2 → 非排除密度は正の値に収束?")

    elapsed = time.time() - t_start
    print(f"\n  総計算時間: {elapsed:.1f}秒")

    # --- JSON出力 ---
    json_result = {
        'exploration': 'mod 2^k 下降マップの固定点集合とBaker排除の拡張',
        'density_summary': {
            'k_range': f"{density_results[0]['k']}-{density_results[-1]['k']}",
            'final_ne_ratio': density_results[-1]['ne_ratio'],
            'final_ne_count': density_results[-1]['ne_count'],
            'growth_rates': growth_rates[-5:] if 'growth_rates' in dir() else [],
        },
        'elapsed': elapsed,
    }

    print("\n\n" + json.dumps(json_result, indent=2, ensure_ascii=False, default=str))

    return output


if __name__ == '__main__':
    result = main()
