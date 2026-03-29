#!/usr/bin/env python3
"""
mod 18 下降逆像の再帰構造と Galton-Watson 接続

Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} (n奇数) の逆像
T^{-1}(m) = { n : n = (m*2^j - 1)/3, j>=1, n奇正整数 }

目標:
1. mod 6, mod 18 の各剰余類における逆像の分岐パターン分類
2. 各剰余類の入次数分布（有限範囲内）
3. 逆像ツリーの再帰的分岐率の統計
4. Galton-Watson過程パラメータの推定
5. 超臨界GW過程との定量的比較
"""

import math
import json
from collections import Counter, defaultdict
import sys

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)}"""
    assert n > 0 and n % 2 == 1
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse(m, N_bound):
    """
    T^{-1}(m) の要素で N_bound 以下のものを列挙
    n = (m * 2^j - 1) / 3 が正奇整数のとき
    """
    results = []
    j = 1
    while True:
        numerator = m * (1 << j) - 1
        if numerator // 3 > N_bound:
            break
        if numerator % 3 == 0:
            n = numerator // 3
            if n > 0 and n % 2 == 1:
                results.append((n, j))
        j += 1
    return results

# ============================================================
# Part 1: mod 6 での入次数分類（理論的確認）
# ============================================================

def analyze_mod6_indegree(N=100000):
    """mod 6 の各剰余類での入次数分布"""
    print("=" * 60)
    print("Part 1: mod 6 での入次数分類")
    print("=" * 60)

    # mod 6 剰余類ごとの入次数
    mod6_indeg = defaultdict(lambda: Counter())

    for m in range(1, N+1, 2):  # 奇数のみ
        preimages = inverse_syracuse(m, N)
        indeg = len(preimages)
        r = m % 6
        mod6_indeg[r][indeg] += 1

    print("\nmod 6 剰余類別 入次数分布:")
    for r in sorted(mod6_indeg.keys()):
        total = sum(mod6_indeg[r].values())
        print(f"  m ≡ {r} (mod 6): ", end="")
        for d in sorted(mod6_indeg[r].keys()):
            frac = mod6_indeg[r][d] / total
            print(f"deg{d}={mod6_indeg[r][d]}({frac:.3f}) ", end="")
        print()

    return dict(mod6_indeg)

# ============================================================
# Part 2: mod 18 での逆像分岐パターン詳細分類
# ============================================================

def analyze_mod18_branching(N=100000):
    """mod 18 の各剰余類における逆像構造の詳細分析"""
    print("\n" + "=" * 60)
    print("Part 2: mod 18 での逆像分岐パターン")
    print("=" * 60)

    # mod 18 剰余類ごとのデータ
    mod18_data = defaultdict(lambda: {
        'indeg_dist': Counter(),
        'j_dist': Counter(),
        'total_preimages': 0,
        'count': 0,
        'preimage_mod18': Counter()  # 逆像のmod18分布
    })

    for m in range(1, N+1, 2):  # 奇数のみ
        r = m % 18
        preimages = inverse_syracuse(m, N)
        indeg = len(preimages)
        mod18_data[r]['indeg_dist'][indeg] += 1
        mod18_data[r]['total_preimages'] += indeg
        mod18_data[r]['count'] += 1

        for n, j in preimages:
            mod18_data[r]['j_dist'][j] += 1
            mod18_data[r]['preimage_mod18'][n % 18] += 1

    print("\nmod 18 剰余類別 分析:")
    results = {}
    for r in sorted(mod18_data.keys()):
        data = mod18_data[r]
        if data['count'] == 0:
            continue
        avg_indeg = data['total_preimages'] / data['count']
        results[r] = {
            'count': data['count'],
            'avg_indegree': avg_indeg,
            'indeg_dist': dict(data['indeg_dist']),
            'j_dist': dict(data['j_dist']),
            'preimage_mod18': dict(data['preimage_mod18'])
        }

        print(f"\n  m ≡ {r} (mod 18):")
        print(f"    個数: {data['count']}")
        print(f"    平均入次数: {avg_indeg:.4f}")
        print(f"    入次数分布: ", end="")
        for d in sorted(data['indeg_dist'].keys()):
            frac = data['indeg_dist'][d] / data['count']
            print(f"deg{d}={frac:.3f} ", end="")
        print()

        # j値分布（上位5つ）
        top_j = sorted(data['j_dist'].items(), key=lambda x: -x[1])[:5]
        print(f"    j値分布(top5): ", end="")
        for j_val, cnt in top_j:
            print(f"j={j_val}:{cnt} ", end="")
        print()

    return results

# ============================================================
# Part 3: 逆像ツリー再帰的分岐率（BFS展開）
# ============================================================

def inverse_bfs_tree(root, depth, N_bound):
    """rootから逆像を再帰的にBFS展開"""
    current_layer = [root]
    tree = {0: [root]}
    layer_sizes = [1]

    for d in range(1, depth + 1):
        next_layer = []
        for m in current_layer:
            preimages = inverse_syracuse(m, N_bound)
            for n, j in preimages:
                next_layer.append(n)
        tree[d] = next_layer
        layer_sizes.append(len(next_layer))
        current_layer = next_layer
        if len(next_layer) == 0:
            break

    return tree, layer_sizes

def analyze_inverse_tree_growth(N_bound=500000, depth=8):
    """逆像ツリーの成長率分析"""
    print("\n" + "=" * 60)
    print("Part 3: 逆像ツリーの再帰的成長率")
    print("=" * 60)

    # 複数の根から逆像ツリーを展開
    roots = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]

    all_growth_rates = []
    mod18_growth = defaultdict(list)

    for root in roots:
        tree, sizes = inverse_bfs_tree(root, depth, N_bound)
        growth_rates = []
        for i in range(1, len(sizes)):
            if sizes[i-1] > 0:
                growth_rates.append(sizes[i] / sizes[i-1])

        r = root % 18
        mod18_growth[r].append(growth_rates)
        all_growth_rates.append(growth_rates)

        print(f"\n  root={root} (mod18={r}):")
        print(f"    層サイズ: {sizes}")
        if growth_rates:
            print(f"    成長率: {[f'{g:.3f}' for g in growth_rates]}")

    # 深さ別の平均成長率
    print("\n  深さ別平均成長率:")
    for d in range(depth):
        rates = [gr[d] for gr in all_growth_rates if d < len(gr)]
        if rates:
            avg = sum(rates) / len(rates)
            print(f"    depth {d+1}: {avg:.4f} (n={len(rates)})")

    return all_growth_rates, mod18_growth

# ============================================================
# Part 4: mod 18 遷移行列（逆像方向）
# ============================================================

def compute_mod18_transition_matrix(N=200000):
    """逆像方向の mod 18 遷移行列"""
    print("\n" + "=" * 60)
    print("Part 4: mod 18 逆像遷移行列")
    print("=" * 60)

    # 奇数のmod18剰余類: 1,3,5,7,9,11,13,15,17
    odd_residues = [r for r in range(18) if r % 2 == 1]

    # 遷移カウント: trans[to_r][from_r] = count
    # T(n) = m なら 逆方向は m -> n
    trans = defaultdict(lambda: Counter())
    total_from = Counter()

    for n in range(1, N+1, 2):  # 奇数
        m = syracuse(n)
        r_n = n % 18
        r_m = m % 18
        # 逆方向: m -> n (mのmod18クラスからnのmod18クラスへ)
        trans[r_m][r_n] += 1
        total_from[r_m] += 1

    print("\n  逆像遷移確率 P(preimage mod 18 = j | m mod 18 = i):")
    print(f"  {'from\\to':>8}", end="")
    for r in odd_residues:
        print(f"  {r:>6}", end="")
    print()

    matrix = {}
    for r_from in odd_residues:
        matrix[r_from] = {}
        print(f"  {r_from:>8}", end="")
        for r_to in odd_residues:
            if total_from[r_from] > 0:
                prob = trans[r_from][r_to] / total_from[r_from]
            else:
                prob = 0
            matrix[r_from][r_to] = prob
            print(f"  {prob:.4f}", end="")
        print(f"  (total={total_from[r_from]})")

    return matrix

# ============================================================
# Part 5: Galton-Watson 接続パラメータ推定
# ============================================================

def galton_watson_analysis(N=200000):
    """
    逆像分岐をGalton-Watson過程としてモデル化
    子孫数分布 p_k = P(|T^{-1}(m) cap [1,N]| = k) を推定
    """
    print("\n" + "=" * 60)
    print("Part 5: Galton-Watson 過程接続分析")
    print("=" * 60)

    # mod 18 別の子孫数分布
    mod18_offspring = defaultdict(lambda: Counter())
    overall_offspring = Counter()

    for m in range(1, N+1, 2):
        preimages = inverse_syracuse(m, N)
        k = len(preimages)
        r = m % 18
        mod18_offspring[r][k] += 1
        overall_offspring[k] += 1

    total = sum(overall_offspring.values())

    print("\n  全体の子孫数分布:")
    mu = 0  # 平均
    var = 0  # 分散
    for k in sorted(overall_offspring.keys()):
        p_k = overall_offspring[k] / total
        mu += k * p_k
        print(f"    P(K={k}) = {overall_offspring[k]}/{total} = {p_k:.6f}")

    for k in sorted(overall_offspring.keys()):
        p_k = overall_offspring[k] / total
        var += (k - mu)**2 * p_k

    print(f"\n  平均子孫数 mu = {mu:.6f}")
    print(f"  理論値 4/3 = {4/3:.6f}")
    print(f"  分散 sigma^2 = {var:.6f}")
    print(f"  sigma = {math.sqrt(var):.6f}")
    print(f"  超臨界判定: mu = {mu:.6f} {'> 1 (超臨界)' if mu > 1 else '<= 1'}")

    # GW過程の絶滅確率 q
    # q は p_0 + p_1*q + p_2*q^2 + ... = q の最小非負解
    # 超臨界のとき q < 1
    p = {}
    for k in range(max(overall_offspring.keys()) + 1):
        p[k] = overall_offspring.get(k, 0) / total

    # ニュートン法で絶滅確率を求める
    q = 0.5  # 初期値
    for _ in range(1000):
        f = -q
        fp = -1
        for k, pk in p.items():
            f += pk * q**k
            if k >= 1:
                fp += k * pk * q**(k-1)
        if abs(fp) < 1e-15:
            break
        q_new = q - f / fp
        q_new = max(0, min(1, q_new))
        if abs(q_new - q) < 1e-15:
            break
        q = q_new

    print(f"\n  GW絶滅確率 q = {q:.10f}")
    print(f"  生存確率 1-q = {1-q:.10f}")

    # mod 18 別のGWパラメータ
    print("\n  mod 18 別の子孫数分布:")
    mod18_params = {}
    for r in sorted(mod18_offspring.keys()):
        data = mod18_offspring[r]
        tot = sum(data.values())
        if tot == 0:
            continue
        mu_r = sum(k * data[k] for k in data) / tot
        var_r = sum((k - mu_r)**2 * data[k] for k in data) / tot
        mod18_params[r] = {'mu': mu_r, 'var': var_r, 'total': tot, 'dist': dict(data)}

        print(f"    m ≡ {r} (mod 18): mu={mu_r:.4f}, sigma={math.sqrt(var_r):.4f}, n={tot}")
        for k in sorted(data.keys()):
            print(f"      P(K={k}) = {data[k]/tot:.4f}", end="")
        print()

    return {
        'overall': {
            'mu': mu,
            'var': var,
            'extinction_prob': q,
            'offspring_dist': {str(k): v for k, v in overall_offspring.items()}
        },
        'mod18': {str(r): {'mu': v['mu'], 'var': v['var'], 'total': v['total']}
                  for r, v in mod18_params.items()}
    }

# ============================================================
# Part 6: 多段逆像のmod 18遷移パターン
# ============================================================

def multi_step_mod18_pattern(N=100000, steps=4):
    """多段逆像での mod 18 パターンの追跡"""
    print("\n" + "=" * 60)
    print(f"Part 6: {steps}段逆像での mod 18 パターン")
    print("=" * 60)

    # 各mod18クラスからの逆像チェインのmod18パターン
    chain_patterns = defaultdict(lambda: Counter())

    for m in range(1, min(N+1, 10001), 2):
        r0 = m % 18
        # 1段逆像
        pre1 = inverse_syracuse(m, N)
        for n1, j1 in pre1:
            r1 = n1 % 18
            pattern = (r0, r1)
            chain_patterns[2][pattern] += 1

            # 2段逆像
            pre2 = inverse_syracuse(n1, N)
            for n2, j2 in pre2:
                r2 = n2 % 18
                pattern3 = (r0, r1, r2)
                chain_patterns[3][pattern3] += 1

    # 頻出パターン（2段）
    print("\n  頻出2段パターン (m_mod18 -> preimage_mod18):")
    top_2 = sorted(chain_patterns[2].items(), key=lambda x: -x[1])[:20]
    for pat, cnt in top_2:
        print(f"    {pat[0]} -> {pat[1]}: {cnt}")

    # 頻出3段パターン
    print("\n  頻出3段パターン (m -> pre1 -> pre2) mod 18:")
    top_3 = sorted(chain_patterns[3].items(), key=lambda x: -x[1])[:15]
    for pat, cnt in top_3:
        print(f"    {pat[0]} -> {pat[1]} -> {pat[2]}: {cnt}")

    # mod 18 クラス間の接続グラフ密度
    edges = set()
    for pat, cnt in chain_patterns[2].items():
        if cnt >= 5:
            edges.add(pat)

    print(f"\n  mod 18逆像接続グラフ: {len(edges)} エッジ（閾値>=5）")

    return {
        'patterns_2step': {str(k): v for k, v in sorted(chain_patterns[2].items(), key=lambda x: -x[1])[:30]},
        'patterns_3step_count': len(chain_patterns[3]),
        'graph_edges': len(edges)
    }

# ============================================================
# Part 7: 剰余類条件付き分岐率（GW type-dependent）
# ============================================================

def power_iteration(M, n, iterations=200):
    """べき乗法で最大固有値を近似"""
    # 初期ベクトル
    v = [1.0/n] * n
    for _ in range(iterations):
        # Mv
        w = [0.0] * n
        for i in range(n):
            for j in range(n):
                w[i] += M[i][j] * v[j]
        # 正規化
        norm = max(abs(x) for x in w)
        if norm < 1e-15:
            return 0.0, v
        v = [x / norm for x in w]
        eigenvalue = norm
    return eigenvalue, v

def mat_mult(A, B, n):
    """n x n 行列の積"""
    C = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C

def typed_galton_watson(N=200000):
    """
    Multi-type Galton-Watson: mod 18 の各型での分岐
    遷移行列の固有値分析（純粋Python）
    """
    print("\n" + "=" * 60)
    print("Part 7: Multi-type Galton-Watson 分析")
    print("=" * 60)

    odd_residues = [r for r in range(18) if r % 2 == 1]
    n_types = len(odd_residues)
    res_to_idx = {r: i for i, r in enumerate(odd_residues)}

    # 平均子孫行列 M[i][j] = E[type-j の子孫数 | 親 = type-i]
    M_count = [[0.0]*n_types for _ in range(n_types)]
    type_count = [0]*n_types

    for m in range(1, N+1, 2):
        r_m = m % 18
        if r_m not in res_to_idx:
            continue
        i = res_to_idx[r_m]
        type_count[i] += 1

        preimages = inverse_syracuse(m, N)
        for n_val, j in preimages:
            r_n = n_val % 18
            if r_n in res_to_idx:
                jj = res_to_idx[r_n]
                M_count[i][jj] += 1

    # 平均子孫行列
    M = [[0.0]*n_types for _ in range(n_types)]
    for i in range(n_types):
        if type_count[i] > 0:
            for j in range(n_types):
                M[i][j] = M_count[i][j] / type_count[i]

    print("\n  平均子孫行列 M (行=親type, 列=子type):")
    print(f"  {'type':>6}", end="")
    for r in odd_residues:
        print(f"  {r:>6}", end="")
    print(f"  {'row_sum':>8}")

    for i, r_val in enumerate(odd_residues):
        print(f"  {r_val:>6}", end="")
        row_sum = 0.0
        for j in range(n_types):
            print(f"  {M[i][j]:.4f}", end="")
            row_sum += M[i][j]
        print(f"  {row_sum:.4f}")

    # べき乗法で最大固有値
    eigenvalue, pf_vec = power_iteration(M, n_types, iterations=500)

    # 正規化
    pf_sum = sum(abs(x) for x in pf_vec)
    if pf_sum > 0:
        pf_vec = [abs(x)/pf_sum for x in pf_vec]

    print(f"\n  最大固有値 (べき乗法) lambda_max = {eigenvalue:.6f}")
    print(f"  理論値 4/3 = {4/3:.6f}")
    print(f"  超臨界判定: lambda_max = {eigenvalue:.6f} {'> 1 (超臨界)' if eigenvalue > 1 else '<= 1'}")

    print(f"\n  Perron-Frobenius 固有ベクトル (正規化):")
    for i, r_val in enumerate(odd_residues):
        print(f"    type {r_val}: {pf_vec[i]:.6f}")

    # 行和（各タイプの平均子孫数の合計）
    row_sums = {}
    for i, r_val in enumerate(odd_residues):
        rs = sum(M[i][j] for j in range(n_types))
        row_sums[str(r_val)] = rs

    # M^k のトレースから他の固有値の手がかりを得る
    print(f"\n  M^k のトレース / n_types (固有値の平均k乗):")
    Mk = [[1.0 if i == j else 0.0 for j in range(n_types)] for i in range(n_types)]
    for k in range(1, 9):
        Mk = mat_mult(Mk, M, n_types)
        trace = sum(Mk[i][i] for i in range(n_types))
        print(f"    Tr(M^{k}) = {trace:.4f},  Tr/n = {trace/n_types:.6f},  lambda_max^{k} = {eigenvalue**k:.4f}")

    return {
        'max_eigenvalue': eigenvalue,
        'pf_vector': {str(odd_residues[i]): pf_vec[i] for i in range(n_types)},
        'mean_matrix_row_sums': row_sums
    }

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("mod 18 下降逆像の再帰構造と Galton-Watson 接続")
    print("=" * 70)

    # Part 1
    mod6_results = analyze_mod6_indegree(N=50000)

    # Part 2
    mod18_results = analyze_mod18_branching(N=50000)

    # Part 3
    growth_rates, mod18_growth = analyze_inverse_tree_growth(N_bound=300000, depth=6)

    # Part 4
    transition_matrix = compute_mod18_transition_matrix(N=100000)

    # Part 5
    gw_results = galton_watson_analysis(N=100000)

    # Part 6
    pattern_results = multi_step_mod18_pattern(N=50000, steps=3)

    # Part 7
    mtgw_results = typed_galton_watson(N=100000)

    # 結果を集約して保存
    final_results = {
        'mod18_branching': {str(k): {
            'avg_indegree': v['avg_indegree'],
            'count': v['count']
        } for k, v in mod18_results.items()},
        'galton_watson': gw_results,
        'multi_type_gw': mtgw_results,
        'patterns': pattern_results
    }

    output_path = '/Users/soyukke/study/lean-unsolved/results/mod18_galton_watson.json'
    with open(output_path, 'w') as f:
        json.dump(final_results, f, indent=2, default=str)

    print(f"\n\n結果を {output_path} に保存しました。")
