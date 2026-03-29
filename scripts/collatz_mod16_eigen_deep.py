#!/usr/bin/env python3
"""
探索Part2: v2遷移の代数的構造の深掘り

Part1の発見:
1. 大規模サンプリング(N=500K)では遷移はほぼ完全に独立（幾何分布）
2. mod 2^k の小さいk では「端効果」で遷移に偏りが出る
3. 核心的発見: v2(3n+1)=j のとき T(n) mod 2^{j} は完全に決定される

この Part2 では:
A. T(n) mod 2^m を代数的に追跡し、v2連鎖が独立になるメカニズムを解明
B. 有限 mod での偏り(端効果)の収束速度を精密計算
C. v2=4 の「過大表現」が有限軌道効果か1次マルコフ端効果かを判定
D. 遷移行列の固有ベクトルが v2=4 偏りにどう寄与するかを特定
"""

import json
import math
from collections import defaultdict
from fractions import Fraction

def v2(n):
    if n == 0:
        return float('inf')
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

def syracuse(n):
    val = 3 * n + 1
    return val >> v2(val)

# ============================================================
# A. 代数的追跡: n ≡ r (mod 2^k) のとき T(n) mod 2^m は何か
# ============================================================

print("=" * 70)
print("A. 代数的追跡: v2(3n+1)=j ⇒ T(n) mod 2^m の決定性")
print("=" * 70)

# v2(3n+1) = j のための residue は n ≡ (2^j - 1) * inv(3, 2^{j+1}) (mod 2^{j+1})
# ただし奇数制約: n ≡ 1 (mod 2)

# T(n) = (3n+1) / 2^j
# n ≡ r (mod 2^k) (r は奇数, v2(3r+1) = j) のとき
# T(n) ≡ (3r+1) / 2^j (mod 2^{k-j})  (k > j のとき)

# したがって T(n) mod 2^{k-j} は n mod 2^k で決まる
# つまり v2(3*T(n)+1) を決めるには T(n) mod 2^{j'+1} が必要（j' = v2(3*T(n)+1)）
# これには n mod 2^{j + j' + 1} の情報が必要

print("\n  鍵となる性質:")
print("  n ≡ r (mod 2^k), v2(3r+1) = j のとき")
print("  T(n) ≡ (3r+1)/2^j (mod 2^{k-j})")
print()
print("  v2_next = v2(3*T(n)+1) を決めるには T(n) mod 2^{v2_next+1} が必要")
print("  → n mod 2^{j + v2_next + 1} が必要")
print()

# 検証: mod 2^k での v2 連鎖
for k in [6, 8, 10, 12]:
    mod = 2**k
    # 各奇数 r に対して (v2_curr, v2_next) を計算
    # v2_next の分布が v2_curr のみに依存するか検証
    v2_to_next_dist = defaultdict(lambda: defaultdict(int))
    v2_curr_count = defaultdict(int)

    for r in range(1, mod, 2):
        val = 3 * r + 1
        j = v2(val)
        t = val >> j
        val2 = 3 * t + 1
        j2 = v2(val2)
        # j2 が k を超えたら打ち切り
        if j2 > k:
            j2 = k
        v2_to_next_dist[j][j2] += 1
        v2_curr_count[j] += 1

    # v2=4 → v2=4 の遷移確率
    if 4 in v2_to_next_dist:
        p_4_to_4 = v2_to_next_dist[4].get(4, 0) / v2_curr_count[4]
        p_4_to_all = {j2: cnt / v2_curr_count[4] for j2, cnt in sorted(v2_to_next_dist[4].items())}
        # 理論値（幾何分布）からの偏差
        dev_4 = abs(p_4_to_4 - 1/16)
        print(f"  mod 2^{k}: P(v2=4→v2=4) = {p_4_to_4:.6f} (理論 1/16 = {1/16:.6f}, 偏差 {dev_4:.6f})")
        # v2=4 の定常確率
    else:
        print(f"  mod 2^{k}: v2=4 の residue なし")

print()

# ============================================================
# B. v2_curr → v2_next の条件付き確率の k→∞ での収束
# ============================================================

print("=" * 70)
print("B. 条件付き遷移確率 P(v2_next=b | v2_curr=a) の k→∞ 収束")
print("=" * 70)

# 理論: P(v2_next=b | v2_curr=a) → 1/2^b (b < ∞) as k → ∞
# なぜなら: T(n) mod 2^{b+1} は n の上位ビットにも依存し、
# mod 2^k で k が大きくなると利用可能ビットが増え、T(n) が「ランダム化」される

convergence_data = {}
for a in [1, 2, 3, 4]:
    print(f"\n  v2_curr = {a}:")
    for b in [1, 2, 3, 4]:
        theoretical = 1 / (2**b)
        probs = []
        for k in range(a + b + 2, 16):
            mod = 2**k
            count_a = 0
            count_ab = 0
            for r in range(1, mod, 2):
                val = 3 * r + 1
                j = v2(val)
                if j != a:
                    continue
                count_a += 1
                t = val >> j
                val2 = 3 * t + 1
                j2 = v2(val2)
                if j2 == b:
                    count_ab += 1
            if count_a > 0:
                p = count_ab / count_a
                probs.append((k, p))
        if probs:
            last_p = probs[-1][1]
            dev = abs(last_p - theoretical)
            convergence_data[(a, b)] = {
                'values': [(k, p) for k, p in probs],
                'limit': theoretical,
                'last_dev': dev
            }
            vals_str = ", ".join(f"k={k}:{p:.5f}" for k, p in probs[-4:])
            print(f"    P(→{b}) → {theoretical:.5f}: {vals_str}, 偏差={dev:.6f}")

print()

# ============================================================
# C. v2=4 過大表現の検証: 長い軌道での統計
# ============================================================

print("=" * 70)
print("C. 長い軌道での v2=4 頻度")
print("=" * 70)

# 大量の開始値で長い軌道を追跡
total_v2_4 = 0
total_steps = 0
v2_histogram = defaultdict(int)

for start in range(1, 100001, 2):
    n = start
    for _ in range(500):
        if n <= 1:
            break
        val = 3 * n + 1
        v = v2(val)
        v2_histogram[v] += 1
        total_steps += 1
        if v == 4:
            total_v2_4 += 1
        n = val >> v

print(f"  総ステップ数: {total_steps}")
print(f"  v2=4 頻度: {total_v2_4}")
print(f"  v2=4 比率: {total_v2_4/total_steps:.6f} (理論 {1/16:.6f})")
print(f"  過大表現比率: {(total_v2_4/total_steps) / (1/16):.4f}")

print(f"\n  v2 分布:")
for v_val in sorted(v2_histogram.keys()):
    if v_val <= 10:
        observed = v2_histogram[v_val] / total_steps
        theoretical = 1 / (2**v_val)
        ratio = observed / theoretical
        print(f"    v2={v_val}: {observed:.6f} (理論 {theoretical:.6f}, 比率 {ratio:.4f})")

print()

# ============================================================
# D. 遷移行列の固有ベクトル解析と v2=4 偏りの寄与
# ============================================================

print("=" * 70)
print("D. mod 2^k 遷移行列の精密固有値解析")
print("=" * 70)

# mod 2^12 で精密な遷移行列を構築
k_precise = 12
mod_precise = 2**k_precise
v2_pairs = defaultdict(lambda: defaultdict(int))
v2_count = defaultdict(int)

for r in range(1, mod_precise, 2):
    val = 3 * r + 1
    j = v2(val)
    t = val >> j
    val2 = 3 * t + 1
    j2 = v2(val2)
    v2_pairs[j][j2] += 1
    v2_count[j] += 1

# 状態空間: v2 = 1..10
states = list(range(1, 11))
n_states = len(states)

M = [[0.0] * n_states for _ in range(n_states)]
for i, a in enumerate(states):
    if v2_count[a] == 0:
        continue
    for j, b in enumerate(states):
        M[i][j] = v2_pairs[a].get(b, 0) / v2_count[a]

print(f"\n  mod 2^{k_precise} 遷移行列（v2=1..10, 主要部分のみ）:")
header = "        " + "".join(f"   {s:>2}" for s in states[:6])
print(f"  {header}")
for i in range(min(6, n_states)):
    row_str = f"  v2={states[i]:<4}"
    for j in range(min(6, n_states)):
        row_str += f"{M[i][j]:>5.3f}"
    print(row_str)

# 定常分布
pi = [1.0 / n_states] * n_states
for _ in range(50000):
    pi_new = [0.0] * n_states
    for j in range(n_states):
        for i in range(n_states):
            pi_new[j] += pi[i] * M[i][j]
    s = sum(pi_new)
    if s > 0:
        pi = [x / s for x in pi_new]

print(f"\n  定常分布（mod 2^{k_precise}）:")
for i, s_val in enumerate(states):
    theoretical = 1 / (2**s_val)
    ratio = pi[i] / theoretical if theoretical > 0 else 0
    print(f"    pi(v2={s_val}) = {pi[i]:.8f} (理論 {theoretical:.8f}, 比率 {ratio:.6f})")

print()

# ============================================================
# E. 核心的代数的結果: v2(3n+1)=j に対する T(n) mod 2^{j+1}
# ============================================================

print("=" * 70)
print("E. 核心: v2(3n+1)=j に対する T(n) mod 2^{j+1} の分布")
print("=" * 70)

# v2(3n+1) = j のとき、T(n) は奇数
# T(n) mod 2^{j+1} がどうなるかを調べる
# （これが v2(3*T(n)+1) の次のステップを制御する）

for j_curr in range(1, 6):
    print(f"\n  v2(3n+1) = {j_curr} のとき T(n) mod 2^{j_curr+1} の分布:")
    # n の residue class: mod 2^{j_curr+1} で v2(3n+1)=j_curr を満たす奇数
    mod_curr = 2**(j_curr + 1)
    residues_curr = [r for r in range(1, mod_curr, 2) if v2(3*r + 1) == j_curr]
    print(f"    n ≡ {residues_curr} (mod {mod_curr})")

    # 各 residue に対して T(r) mod 2^{j_curr+1}
    t_images = {}
    for r in residues_curr:
        t_r = (3 * r + 1) >> j_curr
        t_mod = t_r % mod_curr
        t_images[r] = t_mod
        print(f"    n ≡ {r} (mod {mod_curr}): T(n) ≡ {t_mod} (mod {mod_curr}), "
              f"v2(3*T(n)+1) = v2({3*t_r+1}) = {v2(3*t_r+1)}")

    # 重要: T(n) mod 2^{j_curr+1} は n mod 2^{j_curr+1} だけでは情報が足りない
    # n の上位ビット（mod 2^{2*j_curr+2} 以上）が必要
    # → j が大きいほど「次の v2」の予測に多くのビットが必要

    # より大きい mod で検証
    mod_large = 2**(2 * j_curr + 4)
    t_dist = defaultdict(lambda: defaultdict(int))
    for r in range(1, mod_large, 2):
        if v2(3*r + 1) != j_curr:
            continue
        t_r = (3 * r + 1) >> j_curr
        v_next = v2(3 * t_r + 1)
        t_dist[j_curr][v_next] += 1

    total_j = sum(t_dist[j_curr].values())
    print(f"    mod 2^{2*j_curr+4} での v2_next 分布:")
    for v_next in sorted(t_dist[j_curr].keys()):
        p = t_dist[j_curr][v_next] / total_j
        th = 1 / (2**v_next)
        print(f"      v2_next={v_next}: {p:.6f} (理論 {th:.6f}, 比率 {p/th:.4f})")

print()

# ============================================================
# F. まとめ: 遷移行列の固有構造と v2=4
# ============================================================

print("=" * 70)
print("F. 総合的結論")
print("=" * 70)

# 遷移行列の理論値からの偏差を k_mod の関数として
print("\n  遷移行列の理論値からの偏差 (Frobenius norm of M - M_independent):")
for k_mod in range(5, 14):
    mod = 2**k_mod
    # 遷移行列構築
    v2p = defaultdict(lambda: defaultdict(int))
    v2c = defaultdict(int)
    for r in range(1, mod, 2):
        val = 3 * r + 1
        j = v2(val)
        if j > 10:
            continue
        t = val >> j
        val2 = 3 * t + 1
        j2 = v2(val2)
        if j2 > 10:
            continue
        v2p[j][j2] += 1
        v2c[j] += 1

    # v2=4 の定常偏差
    st = list(range(1, min(k_mod, 9)))
    ns = len(st)
    M_k = [[0.0]*ns for _ in range(ns)]
    for i, a in enumerate(st):
        if v2c[a] == 0:
            continue
        for j_idx, b in enumerate(st):
            M_k[i][j_idx] = v2p[a].get(b, 0) / v2c[a]

    # Frobenius norm of deviation
    frob = 0
    for i in range(ns):
        for j_idx in range(ns):
            theoretical = 1 / (2**st[j_idx])
            frob += (M_k[i][j_idx] - theoretical) ** 2
    frob = math.sqrt(frob)

    # 定常分布
    pi_k = [1.0/ns] * ns
    for _ in range(10000):
        pi_new = [0.0] * ns
        for j_idx in range(ns):
            for i in range(ns):
                pi_new[j_idx] += pi_k[i] * M_k[i][j_idx]
        s = sum(pi_new)
        if s > 0:
            pi_k = [x/s for x in pi_new]

    # v2=4 の偏差
    idx_4 = st.index(4) if 4 in st else None
    if idx_4 is not None:
        dev_4 = pi_k[idx_4] - 1/16
        print(f"  k={k_mod:2d}: ||M-M_ind||_F = {frob:.6f}, pi(v2=4)-1/16 = {dev_4:+.8f}")
    else:
        print(f"  k={k_mod:2d}: ||M-M_ind||_F = {frob:.6f}, (v2=4 not in states)")

print()

# ============================================================
# G. 相互情報量の k 依存性
# ============================================================

print("=" * 70)
print("G. 相互情報量 I(v2_next; v2_curr) の k 依存性")
print("=" * 70)

mi_values = []
for k_mod in range(5, 14):
    mod = 2**k_mod
    v2p = defaultdict(lambda: defaultdict(int))
    v2c = defaultdict(int)
    for r in range(1, mod, 2):
        val = 3 * r + 1
        j = v2(val)
        if j > 10:
            continue
        t = val >> j
        val2 = 3 * t + 1
        j2 = v2(val2)
        if j2 > 10:
            continue
        v2p[j][j2] += 1
        v2c[j] += 1

    st = list(range(1, min(k_mod, 9)))
    ns = len(st)
    M_k = [[0.0]*ns for _ in range(ns)]
    for i, a in enumerate(st):
        if v2c[a] == 0:
            continue
        for j_idx, b in enumerate(st):
            M_k[i][j_idx] = v2p[a].get(b, 0) / v2c[a]

    # 定常分布
    pi_k = [1.0/ns] * ns
    for _ in range(10000):
        pi_new = [0.0] * ns
        for j_idx in range(ns):
            for i in range(ns):
                pi_new[j_idx] += pi_k[i] * M_k[i][j_idx]
        s = sum(pi_new)
        if s > 0:
            pi_k = [x/s for x in pi_new]

    # 相互情報量
    H_marg = 0
    for i in range(ns):
        if pi_k[i] > 1e-15:
            H_marg -= pi_k[i] * math.log2(pi_k[i])

    H_cond = 0
    for i in range(ns):
        if pi_k[i] < 1e-15:
            continue
        H_i = 0
        for j_idx in range(ns):
            if M_k[i][j_idx] > 1e-15:
                H_i -= M_k[i][j_idx] * math.log2(M_k[i][j_idx])
        H_cond += pi_k[i] * H_i

    MI = H_marg - H_cond
    mi_values.append((k_mod, MI))
    print(f"  k={k_mod:2d}: I(v2_next; v2_curr) = {MI:.8f} bits")

# MI の収束レート
print(f"\n  MI の減衰比（連続k間）:")
for i in range(1, len(mi_values)):
    k1, mi1 = mi_values[i-1]
    k2, mi2 = mi_values[i]
    if mi1 > 1e-15:
        ratio = mi2 / mi1
        print(f"    k={k1}→{k2}: MI比 = {ratio:.4f}")

print()

# ============================================================
# 結果 JSON
# ============================================================

result = {
    'convergence': {
        f'P({a}->{b})': {
            'limit': 1/(2**b),
            'values': [(k, p) for k, p in convergence_data.get((a,b), {}).get('values', [])],
            'last_dev': convergence_data.get((a,b), {}).get('last_dev', None)
        }
        for a in [1,2,3,4] for b in [1,2,3,4]
    },
    'orbit_v2_4_frequency': {
        'total_steps': total_steps,
        'v2_4_count': total_v2_4,
        'v2_4_ratio': total_v2_4 / total_steps,
        'theoretical': 1/16,
        'overrep_ratio': (total_v2_4 / total_steps) / (1/16),
    },
    'mutual_information_convergence': mi_values,
    'stationary_mod2_12': {
        str(states[i]): pi[i] for i in range(n_states)
    },
}

output_path = "/Users/soyukke/study/lean-unsolved/results/mod16_eigen_deep.json"
with open(output_path, 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"結果を {output_path} に保存しました。")
print("\n=== 完了 ===")
