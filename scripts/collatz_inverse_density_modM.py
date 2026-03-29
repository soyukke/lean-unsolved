#!/usr/bin/env python3
"""
逆像密度のmod M分布とRenyi-Parry理論の応用

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} の逆像集合 T^{-1}(m) の
mod M (M=8,16,32) での分布を計算し、逆像が密な残基クラスと疎な残基クラスを分類する。
Renyi-Parry理論（beta-展開）との対応で、逆像密度の理論的予測を導出する。
"""

import math
from collections import defaultdict, Counter
import itertools

###############################################################
# Part 1: Syracuse関数と逆Syracuse関数の定義
###############################################################

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
    """Syracuse関数: 奇数n -> (3n+1)/2^{v2(3n+1)}"""
    m = 3 * n + 1
    return m >> v2(m)

def inverse_syracuse_all(m, max_val=None):
    """
    T^{-1}(m) を計算: Syracuse(n) = m となる全ての奇数 n のリスト。
    T(n) = (3n+1)/2^k = m  <=>  3n+1 = m * 2^k  <=>  n = (m*2^k - 1)/3
    nが奇数の正整数であることを確認する。
    """
    preimages = []
    # 2^k の上限: 3n+1 = m*2^k なので n ~ m*2^k/3
    # max_valが指定されていなければ 2^60 まで
    max_k = 60
    if max_val:
        max_k = int(math.log2(3 * max_val / m)) + 2 if m > 0 else 60
        max_k = min(max_k, 60)

    for k in range(1, max_k + 1):
        val = m * (1 << k) - 1
        if val % 3 == 0:
            n = val // 3
            if n > 0 and n % 2 == 1:
                # 実際にv2(3n+1) = k であることを確認
                if v2(3 * n + 1) == k:
                    if max_val is None or n <= max_val:
                        preimages.append(n)
    return preimages

###############################################################
# Part 2: mod M での逆像密度分布
###############################################################

def compute_inverse_density_modM(M, N_range, target_residues=None):
    """
    各残基クラス r (mod M) に属する奇数 m に対し、
    T^{-1}(m) の平均サイズと、前像の mod M 分布を計算する。

    Parameters:
        M: 法 (8, 16, 32)
        N_range: 調査範囲の上限
        target_residues: 調べる残基クラス (None=全奇数残基)

    Returns:
        結果辞書
    """
    if target_residues is None:
        target_residues = [r for r in range(M) if r % 2 == 1]

    results = {}

    for r in target_residues:
        # r (mod M) に属する奇数 m を列挙
        preimage_counts = []
        preimage_residue_dist = Counter()
        total_preimages = 0
        count_m = 0

        m = r if r > 0 else r + M
        while m <= N_range:
            if m % 2 == 1 and m > 0:  # 奇数のみ
                preimages = inverse_syracuse_all(m, max_val=N_range * 10)
                count_m += 1
                preimage_counts.append(len(preimages))
                total_preimages += len(preimages)

                for p in preimages:
                    preimage_residue_dist[p % M] += 1

            m += M

        if count_m > 0:
            avg_preimages = total_preimages / count_m
            results[r] = {
                'count_m': count_m,
                'avg_preimages': avg_preimages,
                'total_preimages': total_preimages,
                'preimage_residue_dist': dict(preimage_residue_dist),
                'preimage_counts_hist': Counter(preimage_counts),
            }

    return results

###############################################################
# Part 3: Renyi-Parry beta展開の理論的予測
###############################################################

def beta_expansion_prediction(M):
    """
    Renyi-Parry理論に基づく逆像密度の理論予測。

    Syracuse関数の逆写像は本質的に n -> m*2^k/3 の分岐構造を持つ。
    beta = 3/2 のときの不変測度は Parry測度に対応する。

    理論予測:
    - Syracuse逆像の分岐数は、v2の分布に依存
    - v2(3n+1) = k の確率は 幾何分布 1/2^k に近い（ただし mod 制約あり）
    - 各 r (mod M) での逆像の期待数は:
      E[|T^{-1}(m)|] = sum_{k: (m*2^k-1)%3=0 and (m*2^k-1)/3 is odd} 1
    """
    predictions = {}

    for r in range(M):
        if r % 2 == 0:
            continue  # 偶数residueは対象外

        # r (mod M) の代表として使える逆像の k 値を分類
        valid_k_count = 0
        checked_k = 0
        k_values = []

        for k in range(1, 100):
            val = r * (1 << k) - 1
            if val % 3 == 0:
                n = val // 3
                if n > 0 and n % 2 == 1:
                    # v2の確認: 3n+1の2-adic valuationがkである
                    actual_v2 = v2(3 * n + 1)
                    if actual_v2 == k:
                        valid_k_count += 1
                        k_values.append(k)
            checked_k += 1

        # beta = 3/2 のParry密度
        # 理論的には平均的に log_2(3) ~ 1.585 個の逆像がある
        # (各 k に対して 1/3 の確率で 3|m*2^k-1, そのうち約 1/2 が奇数)
        # なので期待値 ~ sum_{k>=1} 1/(2*3) * indicator = log_2(3)/3 ??
        # より正確には: E = sum_{k=1}^{infty} P(valid k)

        predictions[r] = {
            'valid_k_count_in_100': valid_k_count,
            'k_values': k_values[:20],  # 最初の20個
            'theoretical_density': valid_k_count / 100,  # 粗い推定
        }

    return predictions

###############################################################
# Part 4: mod M で逆像が密/疎な残基クラスの精密分類
###############################################################

def classify_dense_sparse(M, N_range=10000):
    """
    各残基クラスが逆像として「密」か「疎」かを分類する。

    T(n) = m について、n (mod M) のどの残基に集中するかを分析。
    """
    # 全奇数 n <= N_range について T(n) mod M を計算
    forward_dist = defaultdict(lambda: Counter())  # n%M -> T(n)%M の分布
    backward_dist = defaultdict(lambda: Counter())  # T(n)%M -> n%M の分布

    for n in range(1, N_range + 1, 2):  # 奇数のみ
        tn = syracuse(n)
        n_res = n % M
        t_res = tn % M
        forward_dist[n_res][t_res] += 1
        backward_dist[t_res][n_res] += 1

    return dict(forward_dist), dict(backward_dist)

###############################################################
# Part 5: 遷移行列と不変測度
###############################################################

def compute_transition_matrix(M, N_range=100000):
    """
    mod M での Syracuse遷移行列を計算。
    T_{ij} = P(T(n) ≡ j | n ≡ i) for odd residues.

    不変測度 pi を求め、Renyi-Parry測度と比較する。
    """
    odd_residues = [r for r in range(M) if r % 2 == 1]
    n_res = len(odd_residues)
    res_to_idx = {r: i for i, r in enumerate(odd_residues)}

    # 遷移カウント
    trans_count = [[0]*n_res for _ in range(n_res)]
    row_total = [0]*n_res

    for n in range(1, N_range + 1, 2):
        tn = syracuse(n)
        i = res_to_idx.get(n % M)
        j = res_to_idx.get(tn % M)
        if i is not None and j is not None:
            trans_count[i][j] += 1
            row_total[i] += 1

    # 遷移確率
    trans_prob = [[0.0]*n_res for _ in range(n_res)]
    for i in range(n_res):
        if row_total[i] > 0:
            for j in range(n_res):
                trans_prob[i][j] = trans_count[i][j] / row_total[i]

    # べき乗法で不変測度を近似
    pi = [1.0/n_res] * n_res
    for _ in range(1000):
        new_pi = [0.0] * n_res
        for j in range(n_res):
            for i in range(n_res):
                new_pi[j] += pi[i] * trans_prob[i][j]
        total = sum(new_pi)
        if total > 0:
            pi = [x/total for x in new_pi]

    return odd_residues, trans_prob, pi

###############################################################
# Part 6: beta=3/2 のParry測度との比較
###############################################################

def parry_measure_beta_3_2(M):
    """
    beta = 3/2 に対するParry測度の近似計算。

    Renyi-Parry理論: T_beta(x) = beta*x mod 1 に対する不変測度は
    Parry条件を満たす。beta = 3/2 の場合:

    不変密度 h(x) = C * sum_{n=0}^{infty} (1/beta^n) * 1_{[0, T^n(1))}(x)

    ここでは離散版として、mod M の各残基クラスに対する
    重みを計算する。
    """
    beta = 3/2

    # T_beta: x -> beta*x mod 1 の軌道
    # 1 のParry展開を計算
    x = 1.0
    orbit = [x]
    for _ in range(200):
        x = (beta * x) % 1.0
        orbit.append(x)

    # 各ビン [i/M, (i+1)/M) への重み
    weights = [0.0] * M
    for n, xn in enumerate(orbit[:100]):
        w = (2/3)**n  # 1/beta^n
        # xn より下の区間にw加算
        for i in range(M):
            if i/M < xn:
                weights[i] += w

    total = sum(weights)
    if total > 0:
        weights = [w/total for w in weights]

    return weights

###############################################################
# Part 7: 逆像のv2分布の精密解析（mod M条件付き）
###############################################################

def v2_distribution_conditional(M, N_range=50000):
    """
    各残基クラス r (mod M) ごとに v2(3n+1) の分布を計算。
    これは逆像の分岐構造を決定する。
    """
    dist = defaultdict(lambda: Counter())

    for n in range(1, N_range + 1, 2):
        r = n % M
        k = v2(3 * n + 1)
        dist[r][k] += 1

    return dict(dist)

###############################################################
# Main: 全ての解析を実行
###############################################################

def main():
    print("=" * 80)
    print("逆像密度のmod M分布とRenyi-Parry理論の応用")
    print("=" * 80)

    # -------------------------------------------------------
    # 解析1: v2の条件付き分布 (mod 8, 16, 32)
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析1: v2(3n+1)の条件付き分布 mod M")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} ---")
        dist = v2_distribution_conditional(M, N_range=50000)

        odd_residues = sorted([r for r in range(M) if r % 2 == 1])
        for r in odd_residues:
            if r in dist:
                total = sum(dist[r].values())
                sorted_k = sorted(dist[r].items())
                print(f"  r={r:2d}: ", end="")
                for k, cnt in sorted_k[:8]:
                    print(f"v2={k}:{cnt/total:.3f} ", end="")
                # 平均v2
                avg_v2 = sum(k*c for k,c in dist[r].items()) / total
                print(f"  <v2>={avg_v2:.4f}")

    # -------------------------------------------------------
    # 解析2: 逆像の個数分布 (mod 8, 16, 32)
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析2: 逆像 |T^{-1}(m)| の平均 mod M")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} (N_range=5000) ---")
        results = compute_inverse_density_modM(M, N_range=5000)

        for r in sorted(results.keys()):
            res = results[r]
            avg = res['avg_preimages']
            hist = res['preimage_counts_hist']
            print(f"  r={r:2d}: avg|T^-1|={avg:.4f}, "
                  f"count_m={res['count_m']}, "
                  f"total_preimg={res['total_preimages']}, "
                  f"hist={dict(sorted(hist.items())[:6])}")

    # -------------------------------------------------------
    # 解析3: 逆像の残基クラス分布
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析3: 逆像の残基クラス分布（前像のmod M分布）")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} ---")
        results = compute_inverse_density_modM(M, N_range=3000)

        for r in sorted(results.keys()):
            res = results[r]
            dist = res['preimage_residue_dist']
            total = res['total_preimages']
            if total > 0:
                print(f"  T(n)≡{r:2d}(mod {M}): ", end="")
                for res_class in sorted(dist.keys()):
                    if res_class % 2 == 1:  # 奇数残基のみ
                        frac = dist[res_class] / total
                        print(f"n≡{res_class}:{frac:.3f} ", end="")
                print()

    # -------------------------------------------------------
    # 解析4: 遷移行列と不変測度
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析4: 遷移行列の不変測度 vs Parry測度")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} ---")
        residues, trans_prob, pi_empirical = compute_transition_matrix(M, N_range=100000)
        parry_weights = parry_measure_beta_3_2(M)

        # 奇数残基のParry重み (正規化)
        odd_parry = [parry_weights[r] for r in residues]
        total_op = sum(odd_parry)
        if total_op > 0:
            odd_parry = [w/total_op for w in odd_parry]

        print(f"  {'Residue':>8} {'Invariant':>10} {'Parry':>10} {'Ratio':>10}")
        for i, r in enumerate(residues):
            ratio = pi_empirical[i] / odd_parry[i] if odd_parry[i] > 0 else float('inf')
            print(f"  {r:8d} {pi_empirical[i]:10.6f} {odd_parry[i]:10.6f} {ratio:10.4f}")

        # 遷移行列を表示 (mod 8のみ)
        if M == 8:
            print(f"\n  遷移行列 P[i->j] (mod {M}):")
            header = "       " + "".join(f"{r:8d}" for r in residues)
            print(header)
            for i, ri in enumerate(residues):
                row = f"  {ri:4d}: " + "".join(f"{trans_prob[i][j]:8.4f}" for j in range(len(residues)))
                print(row)

    # -------------------------------------------------------
    # 解析5: 密/疎残基クラスの分類
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析5: 逆像密度による密/疎クラス分類")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} ---")
        fwd, bwd = classify_dense_sparse(M, N_range=50000)

        odd_residues = sorted([r for r in range(M) if r % 2 == 1])

        # 各 m%M について、逆像が来る残基クラスの偏り
        print(f"  逆像分布 (backward): T(n)=m のとき n mod {M} の分布")
        for m_res in odd_residues:
            if m_res in bwd:
                total = sum(bwd[m_res].values())
                print(f"  m≡{m_res:2d}: ", end="")
                for n_res in odd_residues:
                    frac = bwd[m_res].get(n_res, 0) / total if total > 0 else 0
                    print(f"n≡{n_res}:{frac:.3f} ", end="")
                print(f" (total={total})")

    # -------------------------------------------------------
    # 解析6: Renyi-Parry beta=3/2 の理論予測
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析6: Renyi-Parry (beta=3/2) 理論予測との比較")
    print("=" * 80)

    for M in [8, 16, 32]:
        print(f"\n--- mod {M} ---")
        predictions = beta_expansion_prediction(M)

        for r in sorted(predictions.keys()):
            pred = predictions[r]
            print(f"  r={r:2d}: valid_k_in_100={pred['valid_k_count_in_100']}, "
                  f"density={pred['theoretical_density']:.3f}, "
                  f"k_values={pred['k_values'][:10]}")

    # -------------------------------------------------------
    # 解析7: 理論的な逆像数の導出
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析7: 逆像数の理論的導出")
    print("=" * 80)

    print("\nSyracuse T(n) = m の逆像: n = (m*2^k - 1)/3")
    print("条件: (1) m*2^k ≡ 1 (mod 3) → 2^k ≡ m^{-1} (mod 3)")
    print("      (2) n = (m*2^k - 1)/3 が奇数 → m*2^k ≡ 1 (mod 6)")
    print("      (3) v2(3n+1) = k (正しい分岐)")
    print()

    # 条件(1): m ≡ 1 (mod 3) なら k偶数, m ≡ 2 (mod 3) なら k奇数
    # 条件(2): 追加条件
    # 条件(3): v2 の一致条件

    for m_mod3 in [1, 2]:
        print(f"m ≡ {m_mod3} (mod 3):")
        if m_mod3 == 1:
            print(f"  2^k ≡ 1 (mod 3) → k ≡ 0 (mod 2)")
            print(f"  有効な k: 2, 4, 6, 8, ... (偶数)")
        else:
            print(f"  2^k ≡ 2 (mod 3) → k ≡ 1 (mod 2)")
            print(f"  有効な k: 1, 3, 5, 7, ... (奇数)")

        # 追加でmod 6チェック
        for k in range(1, 13):
            if (m_mod3 * (1 << k) - 1) % 3 == 0:
                n_val = (m_mod3 * (1 << k) - 1) // 3
                n_odd = "奇数" if n_val % 2 == 1 else "偶数"
                n_mod6 = n_val % 6
                print(f"    k={k}: n=(m*2^{k}-1)/3 ≡ ({m_mod3}*{1<<k}-1)/3 = {n_val} (mod ?), {n_odd}, n mod 6 = {n_mod6}")
        print()

    # -------------------------------------------------------
    # 解析8: 逆像密度の漸近評価
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析8: 逆像密度の漸近評価 |T^{-1}(m) ∩ [1,N]|")
    print("=" * 80)

    test_ms = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]
    for m in test_ms:
        counts = []
        for N in [100, 1000, 10000, 100000]:
            preimages = inverse_syracuse_all(m, max_val=N)
            counts.append(len(preimages))

        # log_2(N) に対する逆像数
        ratios = []
        for i, N in enumerate([100, 1000, 10000, 100000]):
            if math.log2(N) > 0:
                ratios.append(counts[i] / math.log2(N))

        print(f"  m={m:3d} (m%8={m%8}): "
              f"|T^-1 ∩ [1,100]|={counts[0]:3d}, "
              f"|T^-1 ∩ [1,1000]|={counts[1]:3d}, "
              f"|T^-1 ∩ [1,10000]|={counts[2]:3d}, "
              f"|T^-1 ∩ [1,100000]|={counts[3]:3d}, "
              f"ratio/log2N={ratios[-1]:.4f}" if ratios else "")

    print("\n理論予測: |T^{-1}(m) ∩ [1,N]| ~ C(m) * log_2(N)")
    print("C(m) は m の mod 構造に依存する定数")

    # C(m) の mod 8 別平均
    c_by_mod8 = defaultdict(list)
    for m in range(1, 1000, 2):
        preimages = inverse_syracuse_all(m, max_val=100000)
        c = len(preimages) / math.log2(100000) if len(preimages) > 0 else 0
        c_by_mod8[m % 8].append(c)

    print("\nC(m) の mod 8 別平均:")
    for r in [1, 3, 5, 7]:
        vals = c_by_mod8[r]
        avg = sum(vals) / len(vals) if vals else 0
        std = (sum((v-avg)**2 for v in vals) / len(vals))**0.5 if vals else 0
        print(f"  r={r}: avg_C={avg:.4f}, std={std:.4f}, count={len(vals)}")

    # C(m) の mod 16 別平均
    print("\nC(m) の mod 16 別平均:")
    c_by_mod16 = defaultdict(list)
    for m in range(1, 2000, 2):
        preimages = inverse_syracuse_all(m, max_val=100000)
        c = len(preimages) / math.log2(100000) if len(preimages) > 0 else 0
        c_by_mod16[m % 16].append(c)

    for r in sorted(c_by_mod16.keys()):
        vals = c_by_mod16[r]
        avg = sum(vals) / len(vals) if vals else 0
        std = (sum((v-avg)**2 for v in vals) / len(vals))**0.5 if vals else 0
        print(f"  r={r:2d}: avg_C={avg:.4f}, std={std:.4f}")

    # beta=3/2 理論値との比較
    # 理論的には E[逆像数] = sum_{k: valid} P(v2 = k | conditions)
    # beta展開: 平均分岐数 ~ 2/3 (各ステップで 1/3 の確率で有効な逆像)
    # N までの逆像数 ~ (2/3) * log_{3/2}(N) = (2/3) * log_2(N) / log_2(3/2)
    #                ~ (2/3) * log_2(N) / 0.585 ~ 1.138 * log_2(N)
    theoretical_C = (2/3) / math.log2(3/2)
    print(f"\n理論予測 C_theory = (2/3)/log_2(3/2) = {theoretical_C:.4f}")

    # 別の導出: 各 k について確率 1/(2*3) = 1/6 で有効
    # (mod 3 条件 × 奇数条件)
    # sum_{k=1}^{log_2(N)} 1/6 ではなく、
    # 有効な k は全体の 1/3 で、そのうち v2 条件で制限される
    # 正確には: P(k valid) = 1/3 × 1/2 = 1/6 → C ~ 1/6 ではない
    # n ≤ N → m*2^k - 1 ≤ 3N → 2^k ≤ 3N/m + 1/m → k ≤ log_2(3N/m)
    # k_max ~ log_2(3N/m), 有効な割合 1/3, 奇数条件 1/2
    # → |T^{-1}(m) ∩ [1,N]| ~ log_2(3N/m) × 1/3 = log_2(N)/3 + O(1)
    # しかし v2 条件でさらに減る...

    alt_C = 1/3
    print(f"別の推定 C_alt = 1/3 = {alt_C:.4f}")

    print("\n" + "=" * 80)
    print("完了")
    print("=" * 80)

if __name__ == "__main__":
    main()
