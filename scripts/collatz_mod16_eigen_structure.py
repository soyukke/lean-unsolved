#!/usr/bin/env python3
"""
探索: mod 16遷移行列の固有構造と v2=4 過大表現の数論的起源

v2(3n+1) の連続値間の条件付き依存を mod 16 遷移行列で解析。
v2=4 が軌道上で過大表現される（理論1/16 = 0.0625 に対し 0.083 前後）原因を
遷移行列の固有値・固有ベクトルから特定する。

手法:
1. mod 16 での T(n) の遷移テーブル構築
2. v2値の遷移行列（条件付き確率 P(v2_next | v2_curr)）
3. 固有値・固有ベクトル解析
4. v2=4 過大表現のメカニズム特定
5. mod 32, 64 への拡張で収束確認
"""

import json
import math
from collections import defaultdict
from fractions import Fraction

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

def syracuse(n):
    """Syracuse map T(n) = (3n+1) / 2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    return val >> v2(val)

# ============================================================
# 1. mod 2^k での完全遷移テーブル
# ============================================================

def build_transition_table(k):
    """
    mod 2^k の奇数residue class に対する Syracuse 遷移テーブル。
    各奇数 r (mod 2^k) に対し:
      - v2(3r+1)
      - T(r) mod 2^{k'} (k' = k - v2(3r+1))
    """
    mod = 2**k
    table = {}
    for r in range(1, mod, 2):
        val = 3 * r + 1
        v = v2(val)
        t_r = (val >> v) % mod  # T(r) mod 2^k
        if t_r % 2 == 0:
            # T(r) が偶数になる場合は mod が小さすぎる；実際の T(r) は奇数
            # mod 2^k では T(r) の下位ビットのみ見える
            pass
        table[r] = {'v2': v, 'image': t_r, 'image_odd': t_r if t_r % 2 == 1 else None}
    return table


def build_v2_transition_matrix_exact(k_mod):
    """
    mod 2^{k_mod} で v2 値の遷移行列を構築。
    P[a][b] = Prob(v2(3*T(n)+1) = b | v2(3n+1) = a)
    を Fraction（厳密有理数）で計算。
    """
    mod = 2**k_mod
    # 各奇数 r に対し (v2_current, v2_next) のペアを収集
    v2_pairs = defaultdict(lambda: defaultdict(int))
    v2_count = defaultdict(int)

    for r in range(1, mod, 2):
        val = 3 * r + 1
        v_curr = v2(val)
        # T(r) を正確に計算（r は小さいので実際の値を使える）
        t_r = val >> v_curr
        # t_r は奇数のはず
        assert t_r % 2 == 1, f"T({r}) = {t_r} is not odd"
        val_next = 3 * t_r + 1
        v_next = v2(val_next)

        v2_pairs[v_curr][v_next] += 1
        v2_count[v_curr] += 1

    return v2_pairs, v2_count


def build_v2_transition_matrix_sampling(N, max_v2=8):
    """
    大量の奇数 n に対して実際の軌道を追い、v2 遷移を統計的に計算。
    """
    v2_pairs = defaultdict(lambda: defaultdict(int))
    v2_count = defaultdict(int)

    for n in range(1, 2*N, 2):  # 奇数のみ
        val = 3 * n + 1
        v_curr = min(v2(val), max_v2)
        t_n = val >> v2(val)
        val_next = 3 * t_n + 1
        v_next = min(v2(val_next), max_v2)

        v2_pairs[v_curr][v_next] += 1
        v2_count[v_curr] += 1

    return v2_pairs, v2_count


# ============================================================
# 2. 行列の固有値計算（QR法を使わず特性多項式の根で）
# ============================================================

def matrix_to_float(v2_pairs, v2_count, states):
    """遷移確率行列を float 行列として構築"""
    n = len(states)
    M = [[0.0] * n for _ in range(n)]
    for i, a in enumerate(states):
        if v2_count[a] == 0:
            continue
        for j, b in enumerate(states):
            M[i][j] = v2_pairs[a][b] / v2_count[a]
    return M


def power_iteration(M, n, num_iter=1000):
    """べき乗法で最大固有値と固有ベクトルを求める"""
    v = [1.0 / n] * n
    for _ in range(num_iter):
        # Mv
        w = [0.0] * n
        for i in range(n):
            for j in range(n):
                w[i] += M[j][i] * v[j]  # 転置（列ベクトル左から）
        # 正規化
        norm = max(abs(x) for x in w)
        if norm > 0:
            v = [x / norm for x in w]
        else:
            break
    # 固有値
    Mv = [0.0] * n
    for i in range(n):
        for j in range(n):
            Mv[i] += M[j][i] * v[j]
    eigenval = sum(Mv[i] for i in range(n)) / sum(v[i] for i in range(n)) if sum(v) != 0 else 0
    return eigenval, v


def mat_mul(A, B, n):
    C = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


def mat_sub_identity(M, n, lam):
    """M - lam * I"""
    R = [row[:] for row in M]
    for i in range(n):
        R[i][i] -= lam
    return R


def determinant(M, n):
    """LU分解による行列式計算"""
    A = [row[:] for row in M]
    det = 1.0
    for col in range(n):
        # ピボット選択
        max_val = abs(A[col][col])
        max_row = col
        for row in range(col+1, n):
            if abs(A[row][col]) > max_val:
                max_val = abs(A[row][col])
                max_row = row
        if max_val < 1e-15:
            return 0.0
        if max_row != col:
            A[col], A[max_row] = A[max_row], A[col]
            det *= -1
        det *= A[col][col]
        for row in range(col+1, n):
            factor = A[row][col] / A[col][col]
            for j in range(col+1, n):
                A[row][j] -= factor * A[col][j]
            A[row][col] = 0
    return det


def find_eigenvalues_sweep(M, n, num_points=2000):
    """
    特性多項式 det(M^T - lam*I) の根を数値的にスイープで探索。
    確率行列の固有値は [-1, 1] にあるはず。
    """
    # 転置
    MT = [[M[j][i] for j in range(n)] for i in range(n)]

    eigenvalues = []
    # [-1, 1] をスイープ
    lam_prev = -1.0
    det_prev = determinant(mat_sub_identity(MT, n, lam_prev), n)

    for step in range(1, num_points + 1):
        lam = -1.0 + 2.0 * step / num_points
        det_curr = determinant(mat_sub_identity(MT, n, lam), n)

        if det_prev * det_curr < 0:
            # 二分法で精密化
            lo, hi = lam_prev, lam
            for _ in range(60):
                mid = (lo + hi) / 2
                det_mid = determinant(mat_sub_identity(MT, n, mid), n)
                if det_prev * det_mid < 0:
                    hi = mid
                else:
                    lo = mid
                    det_prev = det_mid
            eigenvalues.append((lo + hi) / 2)

        lam_prev = lam
        det_prev = det_curr

    return sorted(eigenvalues, reverse=True)


# ============================================================
# 3. 定常分布の計算
# ============================================================

def stationary_distribution(M, n, num_iter=10000):
    """べき乗法で定常分布を計算（M^T の最大固有値1の固有ベクトル）"""
    pi = [1.0 / n] * n
    for _ in range(num_iter):
        pi_new = [0.0] * n
        for j in range(n):
            for i in range(n):
                pi_new[j] += pi[i] * M[i][j]
        # 正規化
        s = sum(pi_new)
        if s > 0:
            pi = [x / s for x in pi_new]
    return pi


# ============================================================
# 4. メイン解析
# ============================================================

print("=" * 70)
print("1. v2(3n+1) の代数的条件 (n mod 2^k)")
print("=" * 70)

# v2(3n+1) = j のための n mod 2^{j+1} の条件
for j in range(1, 7):
    mod = 2**(j+1)
    residues = []
    for r in range(1, mod, 2):
        if v2(3*r + 1) == j:
            residues.append(r)
    density = Fraction(len(residues), mod // 2)
    print(f"  v2 = {j}: n ≡ {residues} (mod {mod}), 奇数中の密度 = {density} = {float(density):.6f}")
print()

# ============================================================
# 5. mod 16 遷移行列（小さいモジュラスでの厳密計算）
# ============================================================

print("=" * 70)
print("2. mod 16 での v2 遷移（代数的）")
print("=" * 70)

# mod 16 の各奇数 residue について v2 と T(r) の v2 を計算
print("\n  r mod 16 | v2(3r+1) | T(r) | T(r) mod 16 | v2(3*T(r)+1)")
print("  " + "-" * 60)
for r in range(1, 16, 2):
    val = 3 * r + 1
    v_curr = v2(val)
    t_r = val >> v_curr
    val_next = 3 * t_r + 1
    v_next = v2(val_next)
    t_r_mod16 = t_r % 16
    print(f"  {r:>8} | {v_curr:>8} | {t_r:>4} | {t_r_mod16:>11} | {v_next}")

print()

# ============================================================
# 6. mod 2^k での v2 遷移行列を k=4..8 で構築・解析
# ============================================================

print("=" * 70)
print("3. mod 2^k での v2 遷移行列（k=4..8）")
print("=" * 70)

results_by_k = {}

for k_mod in range(4, 9):
    print(f"\n--- mod 2^{k_mod} = {2**k_mod} ---")
    v2_pairs, v2_count = build_v2_transition_matrix_exact(k_mod)

    # 状態空間: v2 = 1, 2, 3, ..., max_v2
    max_v2_seen = max(max(v2_pairs.keys()), max(v2_count.keys()))
    states = list(range(1, min(max_v2_seen + 1, k_mod + 1)))
    n_states = len(states)

    print(f"  状態数: {n_states}, 状態: {states}")

    # 遷移確率行列
    M = matrix_to_float(v2_pairs, v2_count, states)

    print(f"\n  遷移確率行列 P[i][j] = P(v2_next=j | v2_curr=i):")
    header = "        " + "".join(f"v2={s:>4}" for s in states)
    print(f"  {header}")
    for i, a in enumerate(states):
        row_str = f"  v2={a:<4}"
        for j, b in enumerate(states):
            row_str += f"{M[i][j]:>8.4f}"
        print(row_str)

    # 定常分布
    pi = stationary_distribution(M, n_states)
    print(f"\n  定常分布 pi:")
    for i, s in enumerate(states):
        theoretical = 1.0 / (2**s)  # 理論値: v2=s の確率は 1/2^s
        ratio = pi[i] / theoretical if theoretical > 0 else float('inf')
        print(f"    pi(v2={s}) = {pi[i]:.6f} (理論 1/2^{s} = {theoretical:.6f}, 比率 = {ratio:.4f})")

    # 固有値
    eigenvals = find_eigenvalues_sweep(M, n_states)
    print(f"\n  固有値: {[f'{e:.6f}' for e in eigenvals]}")

    if len(eigenvals) >= 2:
        spectral_gap = 1.0 - abs(eigenvals[1]) if abs(eigenvals[0] - 1.0) < 0.01 else None
        if spectral_gap is not None:
            mixing_time = 1.0 / spectral_gap if spectral_gap > 0 else float('inf')
            print(f"  スペクトルギャップ: {spectral_gap:.6f}")
            print(f"  混合時間 (1/gap): {mixing_time:.2f} ステップ")

    results_by_k[k_mod] = {
        'states': states,
        'stationary': {str(states[i]): pi[i] for i in range(n_states)},
        'eigenvalues': eigenvals,
        'transition_matrix': [[M[i][j] for j in range(n_states)] for i in range(n_states)]
    }

print()

# ============================================================
# 7. 大規模サンプリングによる v2 遷移の実測
# ============================================================

print("=" * 70)
print("4. 大規模サンプリング (N=500000) による v2 遷移の実測")
print("=" * 70)

N_sample = 500000
max_v2_track = 7

v2_pairs_emp, v2_count_emp = build_v2_transition_matrix_sampling(N_sample, max_v2_track)

states_emp = list(range(1, max_v2_track + 1))
n_emp = len(states_emp)
M_emp = matrix_to_float(v2_pairs_emp, v2_count_emp, states_emp)

print(f"\n  遷移確率行列（実測, N={N_sample}）:")
header = "        " + "".join(f"v2={s:>4}" for s in states_emp)
print(f"  {header}")
for i, a in enumerate(states_emp):
    row_str = f"  v2={a:<4}"
    for j, b in enumerate(states_emp):
        row_str += f"{M_emp[i][j]:>8.4f}"
    print(row_str)

pi_emp = stationary_distribution(M_emp, n_emp)
print(f"\n  定常分布（実測）:")
for i, s in enumerate(states_emp):
    theoretical = 1.0 / (2**s)
    ratio = pi_emp[i] / theoretical if theoretical > 0 else float('inf')
    print(f"    pi(v2={s}) = {pi_emp[i]:.6f} (理論 {theoretical:.6f}, 比率 {ratio:.4f})")

eigenvals_emp = find_eigenvalues_sweep(M_emp, n_emp)
print(f"\n  固有値（実測）: {[f'{e:.6f}' for e in eigenvals_emp]}")

print()

# ============================================================
# 8. v2=4 過大表現の因果分析
# ============================================================

print("=" * 70)
print("5. v2=4 過大表現の因果分析")
print("=" * 70)

# v2=4 への流入を分解
print("\n  v2=4 への流入経路分析:")
print("  （各 v2_curr からの v2=4 への遷移確率 × 定常確率）")

# mod 2^8 の結果を使用
k_use = 8
v2_pairs_k, v2_count_k = build_v2_transition_matrix_exact(k_use)
states_k = list(range(1, k_use + 1))
n_k = len(states_k)
M_k = matrix_to_float(v2_pairs_k, v2_count_k, states_k)
pi_k = stationary_distribution(M_k, n_k)

# v2=4 (index 3) への流入
idx_4 = 3  # v2=4 は states_k[3]
total_flow_to_4 = 0
print(f"\n  v2_curr | P(→v2=4) | pi(v2_curr) | flow = pi*P")
print(f"  " + "-" * 55)
for i, s in enumerate(states_k):
    p_to_4 = M_k[i][idx_4]
    flow = pi_k[i] * p_to_4
    total_flow_to_4 += flow
    if pi_k[i] > 1e-6:
        print(f"  v2={s:<4} | {p_to_4:>9.5f} | {pi_k[i]:>11.6f} | {flow:.6f}")

print(f"\n  合計流入 = {total_flow_to_4:.6f}")
print(f"  定常確率 pi(v2=4) = {pi_k[idx_4]:.6f}")
print(f"  理論値 1/16 = {1/16:.6f}")

# v2=4 → 各状態への流出
print(f"\n  v2=4 からの流出経路分析:")
print(f"  v2_next | P(v2=4→) | 理論P")
print(f"  " + "-" * 40)
for j, s in enumerate(states_k):
    p_from_4 = M_k[idx_4][j]
    theoretical_p = 1.0 / (2**s)  # 独立仮定での理論値
    if p_from_4 > 1e-6:
        print(f"  v2={s:<4} | {p_from_4:>9.5f} | {theoretical_p:.5f}")

print()

# ============================================================
# 9. 条件付き依存の強さ：相互情報量
# ============================================================

print("=" * 70)
print("6. 条件付き依存の相互情報量")
print("=" * 70)

# I(v2_next; v2_curr) = H(v2_next) - H(v2_next | v2_curr)
# H(v2_next) = -sum pi(j) log pi(j)
# H(v2_next | v2_curr) = sum_i pi(i) H(v2_next | v2_curr=i)

H_marginal = 0
for i in range(n_k):
    if pi_k[i] > 1e-15:
        H_marginal -= pi_k[i] * math.log2(pi_k[i])

H_conditional = 0
for i in range(n_k):
    if pi_k[i] < 1e-15:
        continue
    H_i = 0
    for j in range(n_k):
        if M_k[i][j] > 1e-15:
            H_i -= M_k[i][j] * math.log2(M_k[i][j])
    H_conditional += pi_k[i] * H_i

MI = H_marginal - H_conditional
print(f"  H(v2_next) = {H_marginal:.6f} bits")
print(f"  H(v2_next | v2_curr) = {H_conditional:.6f} bits")
print(f"  I(v2_next; v2_curr) = {MI:.6f} bits")
print(f"  相関比 I/H = {MI/H_marginal:.6f}")

# 独立の場合の理論 H
H_theoretical = 0
for s in states_k:
    p = 1.0 / (2**s)
    if s < max(states_k):
        if p > 0:
            H_theoretical -= p * math.log2(p)
# v2 >= k_use の残り
p_rest = 1.0 / (2**(max(states_k)-1))
# ... 近似

print(f"\n  独立仮定でのエントロピー参考値: {H_theoretical:.6f} bits")

print()

# ============================================================
# 10. Stern-Brocot 構造との関連: v2 の連鎖的依存
# ============================================================

print("=" * 70)
print("7. v2 連鎖依存の深さ: 2次、3次マルコフ性")
print("=" * 70)

# 2次マルコフ: P(v2_{i+2} | v2_{i+1}, v2_i)
# mod 2^8 の奇数について3ステップ追跡

triple_count = defaultdict(lambda: defaultdict(int))
pair_count = defaultdict(int)

mod_8 = 2**8
for r in range(1, mod_8, 2):
    val0 = 3 * r + 1
    v0 = v2(val0)
    t0 = val0 >> v0

    val1 = 3 * t0 + 1
    v1 = v2(val1)
    t1 = val1 >> v1

    val2 = 3 * t1 + 1
    v2_val = v2(val2)

    key = (v0, v1)
    triple_count[key][v2_val] += 1
    pair_count[key] += 1

print("\n  2次マルコフ遷移 P(v2_2 | v2_0, v2_1):")
print("  v2_0, v2_1 → 確率分布 {v2_2: prob}")
for key in sorted(triple_count.keys()):
    if pair_count[key] < 3:
        continue
    dist = {}
    for v2_next, cnt in sorted(triple_count[key].items()):
        dist[v2_next] = cnt / pair_count[key]
    # 1次マルコフからの予測との比較
    v1 = key[1]
    v1_idx = states_k.index(v1) if v1 in states_k else None
    print(f"  ({key[0]}, {key[1]}) → {{{', '.join(f'{k}:{v:.3f}' for k,v in sorted(dist.items()))}}}", end="")
    if v1_idx is not None:
        # 1次マルコフ予測
        pred_1st = {states_k[j]: M_k[v1_idx][j] for j in range(n_k) if M_k[v1_idx][j] > 0.01}
        deviations = []
        for v2_next in dist:
            if v2_next in pred_1st:
                dev = abs(dist[v2_next] - pred_1st[v2_next])
                if dev > 0.02:
                    deviations.append(f"v2={v2_next}: dev={dev:.3f}")
        if deviations:
            print(f"  ** 偏差: {', '.join(deviations)}", end="")
    print()

print()

# ============================================================
# 11. 軌道上の v2=4 頻度の実測
# ============================================================

print("=" * 70)
print("8. 軌道上の v2=4 頻度の実測（長い軌道）")
print("=" * 70)

def collatz_orbit_v2_freq(start, max_steps=10000):
    """start から始めて v2 の頻度を計測"""
    n = start
    if n % 2 == 0:
        n += 1
    freq = defaultdict(int)
    total = 0
    for _ in range(max_steps):
        if n <= 1:
            break
        val = 3 * n + 1
        v = v2(val)
        freq[v] += 1
        total += 1
        n = val >> v
    return freq, total

# 複数の開始値で試行
starts = [27, 97, 871, 6171, 77031, 837799, 8400511]
print(f"\n  開始値 | 軌道長 | v2=4 頻度 | v2=4 実測比率 | 理論1/16")
print(f"  " + "-" * 65)
for s in starts:
    freq, total = collatz_orbit_v2_freq(s, 200)
    if total > 0:
        f4 = freq.get(4, 0) / total
        print(f"  {s:>8} | {total:>6} | {freq.get(4, 0):>9} | {f4:>13.4f} | {1/16:.4f}")

# 大量の奇数の1ステップ v2 分布
print(f"\n  1ステップ v2 分布（奇数 1..2M）:")
v2_freq = defaultdict(int)
total_odd = 0
for n in range(1, 2000001, 2):
    v = v2(3*n + 1)
    v2_freq[v] += 1
    total_odd += 1

for k in sorted(v2_freq.keys()):
    observed = v2_freq[k] / total_odd
    theoretical = 1 / (2**k)
    ratio = observed / theoretical
    print(f"    v2={k}: {observed:.6f} (理論 {theoretical:.6f}, 比率 {ratio:.4f})")

print()

# ============================================================
# 12. 核心分析: なぜ定常分布が理論値からずれるか
# ============================================================

print("=" * 70)
print("9. 核心分析: 定常分布ずれの原因")
print("=" * 70)

# 遷移行列が非対角的 → 定常分布 ≠ 均一分布
# 鍵: P(v2=1 → v2=j) の分布が幾何分布と異なる

print("\n  各 v2_curr からの遷移分布 vs 理論（幾何分布）:")
for i, s_curr in enumerate(states_k):
    if pi_k[i] < 1e-6:
        continue
    print(f"\n  v2_curr = {s_curr} からの遷移:")
    kl_div = 0
    for j, s_next in enumerate(states_k):
        p = M_k[i][j]
        q = 1.0 / (2**s_next) if s_next < max(states_k) else 1.0 / (2**(max(states_k)-1))
        if p > 1e-10 and q > 1e-10:
            kl_div += p * math.log2(p / q)
        print(f"    → v2={s_next}: P={p:.5f}, 理論={q:.5f}, 比={p/q:.3f}" if q > 0 else f"    → v2={s_next}: P={p:.5f}")
    print(f"    KL divergence from geometric = {kl_div:.6f} bits")

print()

# ============================================================
# 13. 結果まとめ JSON
# ============================================================

# 最終結果構築
final_result = {
    'mod16_transition': {
        'table': [],
    },
    'eigenvalue_analysis': {},
    'stationary_distributions': {},
    'v2_4_overrep': {},
    'mutual_information': {
        'H_marginal': H_marginal,
        'H_conditional': H_conditional,
        'MI': MI,
        'MI_over_H': MI / H_marginal,
    },
}

# mod 16 テーブル
for r in range(1, 16, 2):
    val = 3 * r + 1
    v_c = v2(val)
    t_r = val >> v_c
    v_n = v2(3 * t_r + 1)
    final_result['mod16_transition']['table'].append({
        'r_mod16': r, 'v2_curr': v_c, 'T_r': t_r, 'v2_next': v_n
    })

# 各 mod 2^k の結果
for k_mod, data in results_by_k.items():
    key = f'mod_2^{k_mod}'
    final_result['eigenvalue_analysis'][key] = {
        'eigenvalues': data['eigenvalues'],
    }
    final_result['stationary_distributions'][key] = data['stationary']

# v2=4 過大表現
final_result['v2_4_overrep'] = {
    'stationary_pi_v2_4': pi_k[idx_4],
    'theoretical': 1/16,
    'ratio': pi_k[idx_4] / (1/16),
    'main_inflow_sources': {},
}

for i, s in enumerate(states_k):
    if pi_k[i] > 1e-6:
        final_result['v2_4_overrep']['main_inflow_sources'][str(s)] = {
            'P_to_4': M_k[i][idx_4],
            'pi': pi_k[i],
            'flow': pi_k[i] * M_k[i][idx_4]
        }

output_path = "/Users/soyukke/study/lean-unsolved/results/mod16_eigen_structure.json"
with open(output_path, 'w') as f:
    json.dump(final_result, f, indent=2, default=str)

print(f"\n結果を {output_path} に保存しました。")
print("\n=== 完了 ===")
