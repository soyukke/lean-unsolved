#!/usr/bin/env python3
"""
探索: 転送作用素のスペクトルギャップの精密計算

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} の転送作用素を
mod 2^k (k=3..15) の空間上で構成し、そのスペクトルギャップを計算する。

numpy不使用。固有値は冪乗法とGerschgorin円で推定。
"""

import time
import math
from fractions import Fraction

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 999
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)}"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def build_permutation(k):
    """mod 2^k 奇数空間上の Syracuse 置換を構成"""
    mod = 2**k
    odds = list(range(1, mod, 2))
    N = len(odds)
    odd_to_idx = {o: i for i, o in enumerate(odds)}

    perm = [0] * N  # perm[i] = j means T(odds[i]) ≡ odds[j] mod 2^k
    v2_vals = [0] * N

    for i, n_res in enumerate(odds):
        val = 3 * n_res + 1
        vv = v2(val)
        target = (val >> vv) % mod
        v2_vals[i] = vv
        if target in odd_to_idx:
            perm[i] = odd_to_idx[target]
        else:
            # should not happen
            perm[i] = 0

    return perm, odds, v2_vals

def cycle_decomposition(perm):
    """置換の巡回分解"""
    N = len(perm)
    visited = [False] * N
    cycles = []
    for i in range(N):
        if not visited[i]:
            cycle = []
            j = i
            while not visited[j]:
                visited[j] = True
                cycle.append(j)
                j = perm[j]
            cycles.append(cycle)
    return cycles

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(lst):
    result = 1
    for x in lst:
        result = lcm(result, x)
    return result

# ============================================================
# Part 1: 置換の巡回構造
# ============================================================
def part1_cycle_structure():
    print("=" * 80)
    print("Part 1: 確定的遷移（置換）の巡回構造")
    print("=" * 80)

    for k in range(3, 18):
        t0 = time.time()
        perm, odds, v2_vals = build_permutation(k)
        cycles = cycle_decomposition(perm)
        cycle_lens = sorted([len(c) for c in cycles], reverse=True)
        period = lcm_list(cycle_lens) if cycle_lens else 1
        dt = time.time() - t0

        N = len(odds)
        print(f"\nk={k:2d}: N={N:6d}, "
              f"巡回数={len(cycles):4d}, "
              f"最大巡回長={cycle_lens[0]:6d}, "
              f"周期(LCM)={period}, "
              f"({dt:.3f}s)")
        if k <= 10:
            print(f"  巡回長: {cycle_lens[:15]}")

        # 確定的置換のスペクトル: 固有値は巡回長 L の原始L乗根
        # |λ| = 1 for all eigenvalues (unitary spectrum)
        # スペクトルギャップ = 0 （全固有値の絶対値が1）
        # → 置換行列としてのスペクトルギャップは 0

    print("\n→ 確定的置換行列は全固有値の絶対値が1（ユニタリ）")
    print("  → スペクトルギャップ = 0。混合は起こらない。")
    print("  → 確率的な扱い（上位ビットのランダム性）が必要。")

# ============================================================
# Part 2: 確率的遷移行列の構成とスペクトルギャップ
# ============================================================

def mat_vec_mult(M, v):
    """行列×ベクトル"""
    N = len(v)
    result = [0.0] * N
    for i in range(N):
        s = 0.0
        for j in range(N):
            s += M[i][j] * v[j]
        result[i] = s
    return result

def vec_norm(v):
    return math.sqrt(sum(x*x for x in v))

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(len(a))]

def power_method(M, N, num_iter=200):
    """冪乗法で最大固有値と対応する固有ベクトルを計算"""
    v = [1.0/math.sqrt(N)] * N
    eigenvalue = 0.0

    for _ in range(num_iter):
        w = mat_vec_mult(M, v)
        norm = vec_norm(w)
        if norm < 1e-15:
            return 0.0, v
        eigenvalue = norm
        v = [x / norm for x in w]

    return eigenvalue, v

def build_stochastic_matrix(k, num_samples=128):
    """
    確率的遷移行列。n mod 2^k を状態とし、
    n, n+2^k, n+2*2^k, ... で T を計算して遷移確率を推定。
    """
    mod = 2**k
    odds = list(range(1, mod, 2))
    N = len(odds)
    odd_to_idx = {o: i for i, o in enumerate(odds)}

    P = [[0.0]*N for _ in range(N)]

    for i, n_res in enumerate(odds):
        targets = {}
        for s in range(num_samples):
            n = n_res + s * mod
            if n == 0:
                continue
            t = syracuse(n)
            t_mod = t % mod
            if t_mod in odd_to_idx:
                j = odd_to_idx[t_mod]
                targets[j] = targets.get(j, 0) + 1

        total = sum(targets.values())
        if total > 0:
            for j, count in targets.items():
                P[i][j] = count / total

    return P, odds

def compute_spectral_gap_power_method(P, N):
    """
    冪乗法 + deflation で λ₁, λ₂ を推定。
    P は確率行列なので λ₁ = 1。
    λ₂ を求めるために、定常分布方向を引いた行列で冪乗法を行う。
    """
    # λ₁ = 1, 対応する右固有ベクトルは定常分布に関係
    # 一様分布が定常分布なら、deflated行列 P' = P - (1/N)*1*1^T

    # まず P の λ₁ を確認
    v1 = [1.0/math.sqrt(N)] * N
    for _ in range(100):
        w = mat_vec_mult(P, v1)
        norm = vec_norm(w)
        if norm < 1e-15:
            break
        v1 = [x / norm for x in w]

    # Deflation: P' = P - λ₁ * v₁ * v₁^T (ランク1修正)
    # 一様ベクトルで deflate
    uniform = [1.0/N] * N
    P_deflated = [[0.0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            P_deflated[i][j] = P[i][j] - uniform[j]  # P - (1/N)11^T * ...

    # P' の最大固有値の絶対値 = |λ₂|
    # ランダム初期ベクトル（一様と直交するように）
    import random
    random.seed(42)
    v2 = [random.gauss(0, 1) for _ in range(N)]
    # 一様成分を除去
    mean_v2 = sum(v2) / N
    v2 = [x - mean_v2 for x in v2]
    norm = vec_norm(v2)
    if norm > 1e-15:
        v2 = [x / norm for x in v2]

    lambda2 = 0.0
    for iteration in range(300):
        w = mat_vec_mult(P, v2)
        # 一様成分を除去
        mean_w = sum(w) / N
        w = [x - mean_w for x in w]
        norm = vec_norm(w)
        if norm < 1e-15:
            lambda2 = 0.0
            break
        lambda2 = norm
        v2_new = [x / norm for x in w]

        # 収束チェック
        diff = vec_norm(vec_sub(v2_new, v2))
        v2 = v2_new
        if diff < 1e-12:
            break

    return 1.0, lambda2, 1.0 - lambda2

def part2_stochastic_spectral():
    print("\n" + "=" * 80)
    print("Part 2: 確率的遷移行列のスペクトルギャップ")
    print("（上位ビットをランダムと仮定し、num_samples=128 でサンプリング）")
    print("=" * 80)

    results = []
    for k in range(3, 14):
        N = 2**(k-1)
        if N > 4096:
            print(f"\nk={k}: N={N} 大きすぎ、スキップ")
            continue

        t0 = time.time()
        P, odds = build_stochastic_matrix(k, num_samples=128)
        lambda1, lambda2, gap = compute_spectral_gap_power_method(P, N)
        dt = time.time() - t0

        mixing_time = 1.0 / gap if gap > 1e-10 else float('inf')
        results.append({'k': k, 'N': N, 'lambda1': lambda1, 'lambda2': lambda2,
                        'gap': gap, 'mixing_time': mixing_time})

        print(f"\nk={k:2d}: N={N:5d}, "
              f"λ₁={lambda1:.6f}, |λ₂|={lambda2:.6f}, "
              f"ギャップ={gap:.6f}, "
              f"混合時間≈{mixing_time:.2f}, "
              f"({dt:.3f}s)")

    return results

# ============================================================
# Part 3: v2 重み付き転送作用素のスペクトル半径
# ============================================================
def part3_weighted_spectral_radius():
    print("\n" + "=" * 80)
    print("Part 3: v₂重み付き転送作用素 L_s のスペクトル半径")
    print("  L_s: (L_s f)(m) = Σ_{T(n)=m} 2^{-s·v₂(3n+1)} f(n)")
    print("  s=1 で ρ(L_1) < 1 なら平均的に縮小を意味")
    print("=" * 80)

    for k in [5, 7, 9, 11]:
        mod = 2**k
        odds = list(range(1, mod, 2))
        N = len(odds)
        odd_to_idx = {o: i for i, o in enumerate(odds)}

        print(f"\nk={k} (N={N}):")
        print(f"  {'s':>6s}  {'ρ(L_s)':>10s}  {'log₂ρ':>10s}")

        for s_int in range(0, 21):  # s = 0.0, 0.1, ..., 2.0
            s = s_int / 10.0

            # L_s 行列を構成
            L = [[0.0]*N for _ in range(N)]
            for i, n_res in enumerate(odds):
                val = 3 * n_res + 1
                vv = v2(val)
                target = (val >> vv) % mod
                if target in odd_to_idx:
                    j = odd_to_idx[target]
                    weight = 2.0**(-s * vv)
                    L[j][i] += weight

            # 冪乗法でスペクトル半径を推定
            rho, _ = power_method(L, N, num_iter=200)
            log2_rho = math.log2(rho) if rho > 0 else float('-inf')
            print(f"  {s:6.1f}  {rho:10.6f}  {log2_rho:10.6f}")

# ============================================================
# Part 4: E[v₂] の精密計算
# ============================================================
def part4_ev2_precise():
    print("\n" + "=" * 80)
    print("Part 4: E[v₂] の精密計算（k依存性）")
    print("  理論: E[v₂] = 2 - (k+2)/2^k")
    print("=" * 80)

    print(f"{'k':>3s}  {'E[v₂]':>14s}  {'E[v₂]-2':>16s}  {'理論(E[v₂]-2)':>16s}  {'一致':>6s}")
    for k in range(3, 22):
        mod = 2**k
        total_v2 = 0
        count = 0
        for n in range(1, mod, 2):
            total_v2 += v2(3 * n + 1)
            count += 1
        mean_v2 = Fraction(total_v2, count)
        theoretical_diff = Fraction(-(k + 2), 2**k)
        actual_diff = mean_v2 - 2
        match = "✓" if actual_diff == theoretical_diff else "✗"
        print(f"{k:3d}  {float(mean_v2):14.10f}  {float(actual_diff):16.12f}  "
              f"{float(theoretical_diff):16.12f}  {match}")

# ============================================================
# Part 5: v2分布の精密解析
# ============================================================
def part5_v2_distribution():
    print("\n" + "=" * 80)
    print("Part 5: v₂の分布（各k での P(v₂=j) と幾何分布 1/2^j の比較）")
    print("=" * 80)

    for k in [5, 8, 10, 12, 15]:
        mod = 2**k
        count = 0
        v2_counts = {}
        for n in range(1, mod, 2):
            vv = v2(3*n + 1)
            v2_counts[vv] = v2_counts.get(vv, 0) + 1
            count += 1

        print(f"\nk={k} (N={count}):")
        print(f"  {'j':>3s}  {'P(v₂=j)':>12s}  {'1/2^j':>12s}  {'比率':>10s}")
        for j in sorted(v2_counts.keys()):
            p_emp = v2_counts[j] / count
            p_geo = 1.0 / (2**j)
            ratio = p_emp / p_geo if p_geo > 0 else 0
            print(f"  {j:3d}  {p_emp:12.8f}  {p_geo:12.8f}  {ratio:10.6f}")

# ============================================================
# Part 6: スペクトルギャップの k 依存性フィッティング
# ============================================================
def part6_gap_fitting(results):
    print("\n" + "=" * 80)
    print("Part 6: スペクトルギャップの k 依存性")
    print("=" * 80)

    if len(results) < 3:
        print("データ不足")
        return

    # gap vs k をプロット（テキスト）
    print(f"\n{'k':>3s}  {'gap':>12s}  {'|λ₂|':>12s}  {'log₂(gap)':>12s}  {'1/gap':>12s}")
    for r in results:
        lg = math.log2(r['gap']) if r['gap'] > 1e-15 else -999
        print(f"{r['k']:3d}  {r['gap']:12.8f}  {r['lambda2']:12.8f}  {lg:12.4f}  {1.0/r['gap'] if r['gap']>0 else 999:12.4f}")

    # 線形回帰: log(gap) = a*k + b → gap ≈ exp(b) * exp(a)^k
    ks = [r['k'] for r in results if r['gap'] > 1e-10]
    lg = [math.log(r['gap']) for r in results if r['gap'] > 1e-10]
    if len(ks) >= 2:
        n = len(ks)
        mean_k = sum(ks) / n
        mean_lg = sum(lg) / n
        cov = sum((ks[i] - mean_k) * (lg[i] - mean_lg) for i in range(n))
        var = sum((ks[i] - mean_k)**2 for i in range(n))
        if var > 0:
            a = cov / var
            b = mean_lg - a * mean_k
            alpha = math.exp(a)
            C = math.exp(b)
            print(f"\nフィッティング: gap ≈ {C:.4f} × {alpha:.4f}^k")
            print(f"  指数減衰率 α = {alpha:.6f}")
            print(f"  半減期 k ≈ {-math.log(2)/a:.2f}" if a < 0 else "  （増加傾向）")

            # |λ₂| のフィッティング
            l2s = [r['lambda2'] for r in results if r['gap'] > 1e-10]
            print(f"\n|λ₂| の推移:")
            for i, r in enumerate(results):
                if r['gap'] > 1e-10:
                    pred_gap = C * alpha**r['k']
                    print(f"  k={r['k']}: |λ₂|={r['lambda2']:.6f}, gap={r['gap']:.6f}, predicted_gap={pred_gap:.6f}")

# ============================================================
# Part 7: 収束速度の理論的評価
# ============================================================
def part7_convergence():
    print("\n" + "=" * 80)
    print("Part 7: 収束速度の理論的評価")
    print("=" * 80)

    print("""
v₂の分布が幾何分布 P(v₂=j) = 1/2^j に収束する速度を評価。

スペクトルギャップ Δ が正であるとき:
  ||P^t(v₂=j|n₀) - 1/2^j||_TV ≤ C · (1-Δ)^t

ここで:
  - P^t は t 回のSyracuse反復後の v₂ の条件付き分布
  - || · ||_TV はTV距離
  - Δ はスペクトルギャップ
  - C は定数（初期条件依存）

スペクトルギャップ Δ > 0 が全ての k で成立すれば、
v₂ の分布は幾何分布に指数的に収束する。
""")

    # 実際に T^t を繰り返して v2 分布の収束を確認
    print("T^t 反復後の v₂ 分布の収束（n₀=1 から出発）:")
    n = 1
    v2_history = []
    for t in range(100):
        n = syracuse(n) if n > 0 else 1
        v2_history.append(v2(3 * n + 1))

    # 最初の T ステップでの v2 分布
    for window in [10, 20, 50, 100]:
        hist = v2_history[:window]
        counts = {}
        for vv in hist:
            counts[vv] = counts.get(vv, 0) + 1
        tv_dist = 0.0
        for j in range(1, max(counts.keys()) + 1):
            p_emp = counts.get(j, 0) / window
            p_geo = 1.0 / (2**j)
            tv_dist += abs(p_emp - p_geo)
        tv_dist /= 2.0
        print(f"  window={window:3d}: TV距離 = {tv_dist:.4f}")

    # 多数の初期値から
    print("\n多数の初期値からの T^t 後の v₂ 分布収束:")
    for t_steps in [1, 3, 5, 10, 20]:
        counts = {}
        num_init = 10000
        for n0 in range(1, 2*num_init, 2):
            n = n0
            for _ in range(t_steps):
                n = syracuse(n)
            vv = v2(3*n + 1)
            counts[vv] = counts.get(vv, 0) + 1

        tv_dist = 0.0
        max_j = max(counts.keys())
        for j in range(1, max_j + 1):
            p_emp = counts.get(j, 0) / num_init
            p_geo = 1.0 / (2**j)
            tv_dist += abs(p_emp - p_geo)
        # 残りの j の寄与
        tv_dist += 1.0 / (2**max_j)  # tail
        tv_dist /= 2.0
        print(f"  t={t_steps:2d}: TV距離 = {tv_dist:.6f}")


def main():
    part1_cycle_structure()
    results = part2_stochastic_spectral()
    part3_weighted_spectral_radius()
    part4_ev2_precise()
    part5_v2_distribution()
    part6_gap_fitting(results)
    part7_convergence()

if __name__ == '__main__':
    main()
