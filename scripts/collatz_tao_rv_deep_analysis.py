#!/usr/bin/env python3
"""
Tao Syracuse RV 相関構造 深掘り分析

前回の発見を踏まえ:
  1. 位置依存性は軌道の値縮小（nが小さくなること）による見かけの効果か検証
  2. 大きなNでの v2 分布の収束速度
  3. 累積ドリフト分散の亜拡散メカニズム解明
  4. サイズ別（初期値のbit長別）の相関構造比較
  5. Taoモデルからの乖離の系統的分解
"""

import math
from collections import defaultdict, Counter
import time
import random

def v2(n):
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2_of_3n1(n):
    return v2(3 * n + 1)

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def variance(lst):
    if len(lst) < 2:
        return 0.0
    m = mean(lst)
    return sum((x - m)**2 for x in lst) / len(lst)

# ============================================================
# 分析1: 大きな値のみでの v2 統計
# ============================================================

def analyze_large_values_only():
    """軌道中の値が十分大きい場合のみ v2 を測定
    → 値が小さくなることによるバイアスを除去"""
    print("=" * 70)
    print("分析1: 値の大きさによる v2 統計の層別化")
    print("=" * 70)

    N_MAX = 200_000
    SEQ_LEN = 50

    # bit長の閾値
    thresholds = [10, 15, 20, 25, 30]

    v2_by_bits = defaultdict(list)  # bit長 → v2値のリスト
    v2_all_trajectory = []

    for n in range(3, N_MAX + 1, 2):
        current = n
        for _ in range(SEQ_LEN):
            if current <= 1:
                break
            bits = current.bit_length()
            val = v2_of_3n1(current)
            v2_all_trajectory.append(val)

            # bit長カテゴリに分類
            for th in thresholds:
                if bits >= th:
                    v2_by_bits[th].append(val)

            current = syracuse(current)

    print(f"\n  閾値(bits) | 観測数      | E[v2]     | Var[v2]    | E-2.0      | Var-2.0")
    print(f"  " + "-" * 75)
    for th in thresholds:
        vals = v2_by_bits[th]
        if len(vals) > 100:
            m = mean(vals)
            v = variance(vals)
            print(f"  >= {th:3d} bits | {len(vals):>10,} | {m:9.6f} | {v:10.6f} | {m-2.0:+10.6f} | {v-2.0:+10.6f}")

    # 全体
    m = mean(v2_all_trajectory)
    v = variance(v2_all_trajectory)
    print(f"  全体       | {len(v2_all_trajectory):>10,} | {m:9.6f} | {v:10.6f} | {m-2.0:+10.6f} | {v-2.0:+10.6f}")

# ============================================================
# 分析2: 「真のランダム」奇数でのv2分析
# ============================================================

def analyze_random_large_odd():
    """大きなランダム奇数を直接選んでv2を1ステップだけ測定
    → 軌道の経路依存性を排除した純粋な1ステップ統計"""
    print("\n" + "=" * 70)
    print("分析2: ランダム大奇数での1ステップv2統計")
    print("=" * 70)

    random.seed(42)
    N_samples = 500_000

    for bit_size in [20, 30, 40, 50, 60]:
        v2_values = []
        for _ in range(N_samples):
            n = random.getrandbits(bit_size) | 1  # 奇数にする
            if n < 3:
                n = 3
            v = v2_of_3n1(n)
            v2_values.append(v)

        m = mean(v2_values)
        var_val = variance(v2_values)

        # v2の分布
        dist = Counter(v2_values)
        total = len(v2_values)

        print(f"\n  {bit_size}-bit 奇数 (N={N_samples:,})")
        print(f"    E[v2] = {m:.6f} (理論: 2.0, 差: {m-2.0:+.6f})")
        print(f"    Var[v2] = {var_val:.6f} (理論: 2.0, 差: {var_val-2.0:+.6f})")

        print(f"    分布: ", end="")
        for k in range(1, 8):
            p_emp = dist.get(k, 0) / total
            p_geom = 0.5 ** k
            print(f"P({k})={p_emp:.4f}[{p_geom:.4f}] ", end="")
        print()

# ============================================================
# 分析3: v2(3n+1) の v3(n) 依存性
# ============================================================

def analyze_v3_dependence():
    """v2(3n+1) が n mod 3^k にどう依存するか
    → Taoの3-adic構造との関係"""
    print("\n" + "=" * 70)
    print("分析3: v2(3n+1) の 3-adic 構造依存性")
    print("=" * 70)

    N_MAX = 300_000
    for mod_val in [3, 9, 27, 81]:
        class_data = defaultdict(list)
        for n in range(1, N_MAX + 1, 2):
            r = n % mod_val
            if r % 2 == 1:  # 奇数の剰余類のみ
                v = v2_of_3n1(n)
                class_data[r].append(v)

        print(f"\n  n mod {mod_val}:")
        print(f"    剰余 | E[v2]     | Var[v2]    | 観測数")
        print(f"    " + "-" * 50)
        for r in sorted(class_data.keys()):
            vals = class_data[r]
            if len(vals) > 100:
                m = mean(vals)
                v = variance(vals)
                print(f"    {r:5d} | {m:9.6f} | {v:10.6f} | {len(vals):,}")

# ============================================================
# 分析4: 累積ドリフトの亜拡散メカニズム
# ============================================================

def analyze_subdiffusion_mechanism():
    """累積ドリフト S_k の分散が k に対して亜線形成長する原因を分析
    仮説: 軌道が小さくなるにつれv2の平均が下がるため"""
    print("\n" + "=" * 70)
    print("分析4: 累積ドリフト亜拡散のメカニズム分析")
    print("=" * 70)

    N_MAX = 200_000
    SEQ_LEN = 30
    log2_3 = math.log2(3)

    # 方法: 「定常状態」近似として、軌道が十分大きい部分だけを使う
    # 各軌道の前半(値が大きい)と後半(値が小さい)を分けて分析

    sequences_full = []
    for n in range(3, N_MAX + 1, 2):
        seq = []
        current = n
        trajectory_values = [n]
        for _ in range(SEQ_LEN):
            if current <= 1:
                break
            val = v2_of_3n1(current)
            seq.append(val)
            current = syracuse(current)
            trajectory_values.append(current)
        if len(seq) >= SEQ_LEN:
            sequences_full.append((seq, trajectory_values))

    print(f"  軌道数: {len(sequences_full)}")

    # 軌道の値のサイズ変化を追跡
    print(f"\n  ステップ位置ごとの平均log2(n):")
    for step in range(0, SEQ_LEN + 1, 5):
        vals = [math.log2(t[1][step]) if len(t[1]) > step and t[1][step] > 0 else 0
                for t in sequences_full if len(t[1]) > step and t[1][step] > 0]
        if vals:
            print(f"    step {step:3d}: E[log2(n)] = {mean(vals):.3f}")

    # 「大きな値でのみ測定した」累積ドリフト
    # しきい値: 軌道中の値が 2^15 以上のステップだけ使う
    print(f"\n  値サイズしきい値付き累積ドリフト分散:")
    for min_bits in [0, 10, 15]:
        filtered_drifts = []
        for seq, traj in sequences_full:
            drifts = []
            for i, v in enumerate(seq):
                if traj[i] > (1 << min_bits):
                    drifts.append(log2_3 - v)
            if len(drifts) >= 20:
                filtered_drifts.append(drifts)

        if filtered_drifts:
            # 累積分散成長率
            single_var_list = []
            for ds in filtered_drifts:
                single_var_list.extend(ds)
            sv = variance(single_var_list)

            print(f"\n    min_bits >= {min_bits}: {len(filtered_drifts)} 軌道, 1step Var={sv:.6f}")
            print(f"    k  | Var[S_k] | kVar | 比率")
            for k in [1, 5, 10, 15, 20]:
                cums = []
                for ds in filtered_drifts:
                    if len(ds) >= k:
                        s = sum(ds[:k])
                        cums.append(s)
                if len(cums) > 100:
                    v_cum = variance(cums)
                    expected = k * sv
                    ratio = v_cum / expected if expected > 0 else 0
                    print(f"    {k:3d} | {v_cum:8.4f} | {expected:6.4f} | {ratio:.4f}")

# ============================================================
# 分析5: v2系列の「有効記憶長」の推定
# ============================================================

def estimate_memory_length():
    """v2系列がどの程度の過去に依存するか:
    条件付きエントロピー H(v2_{i+1} | v2_i, ..., v2_{i-m}) の
    mに対する収束速度を測定"""
    print("\n" + "=" * 70)
    print("分析5: v2系列の有効記憶長推定")
    print("=" * 70)

    N_MAX = 300_000
    SEQ_LEN = 20
    MAX_V = 5  # 値のクリッピング

    # データ収集
    sequences = []
    for n in range(3, N_MAX + 1, 2):
        seq = []
        current = n
        for _ in range(SEQ_LEN):
            if current <= 1:
                break
            val = min(v2_of_3n1(current), MAX_V)
            seq.append(val)
            current = syracuse(current)
        if len(seq) >= SEQ_LEN:
            sequences.append(seq)

    print(f"  軌道数: {len(sequences)}")

    # m次条件付きエントロピー
    for m in range(0, 6):
        if m == 0:
            # H(v2) = 無条件エントロピー
            counts = Counter()
            for seq in sequences:
                for v in seq:
                    counts[v] += 1
            total = sum(counts.values())
            entropy = -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
            print(f"\n  m=0 (無条件): H(v2) = {entropy:.6f} bits")
            print(f"    Geom(1/2)理論: {-sum(0.5**k * math.log2(0.5**k) for k in range(1,20)):.6f} bits")
        else:
            # H(v2_{i+1} | v2_i, ..., v2_{i-m+1})
            joint_counts = defaultdict(lambda: Counter())
            context_counts = Counter()

            for seq in sequences:
                for i in range(m, len(seq)):
                    context = tuple(seq[i-m:i])
                    value = seq[i]
                    joint_counts[context][value] += 1
                    context_counts[context] += 1

            # 条件付きエントロピー
            cond_entropy = 0.0
            total = sum(context_counts.values())
            for context, count in context_counts.items():
                p_context = count / total
                vals = joint_counts[context]
                context_total = sum(vals.values())
                for v, c in vals.items():
                    p_v_given_context = c / context_total
                    if p_v_given_context > 0:
                        cond_entropy -= p_context * p_v_given_context * math.log2(p_v_given_context)

            # 相互情報量 = H(v2) - H(v2 | context)
            counts_marginal = Counter()
            for seq in sequences:
                for v in seq:
                    counts_marginal[v] += 1
            total_m = sum(counts_marginal.values())
            h_marginal = -sum((c/total_m) * math.log2(c/total_m) for c in counts_marginal.values() if c > 0)

            mi = h_marginal - cond_entropy
            print(f"  m={m}: H(v2|past_{m}) = {cond_entropy:.6f} bits, MI = {mi:.6f} bits")

# ============================================================
# 分析6: n mod 4 による完全決定と残差の分析
# ============================================================

def analyze_mod4_deterministic():
    """n mod 4 が v2(3n+1) の最小値を決定する:
    n = 1 mod 4 → 3n+1 = 4 mod 16 → v2 >= 2
    n = 3 mod 4 → 3n+1 = 10 mod 16 → v2 = 1
    この決定論的成分を除去した「残差」の相関を測定"""
    print("\n" + "=" * 70)
    print("分析6: mod 4 決定論的成分と残差相関")
    print("=" * 70)

    N_MAX = 200_000
    SEQ_LEN = 30

    # データ収集（奇数nのmod4クラスも追跡）
    mod4_sequences = []  # (mod4_i, v2_i) のペア列
    for n in range(3, N_MAX + 1, 2):
        seq = []
        current = n
        for _ in range(SEQ_LEN):
            if current <= 1:
                break
            r4 = current % 4  # 1 or 3
            val = v2_of_3n1(current)
            seq.append((r4, val))
            current = syracuse(current)
        if len(seq) >= SEQ_LEN:
            mod4_sequences.append(seq)

    print(f"  軌道数: {len(mod4_sequences)}")

    # mod 4 別のv2統計
    for r4 in [1, 3]:
        vals = [val for seq in mod4_sequences for (r, val) in seq if r == r4]
        print(f"\n  n mod 4 = {r4}: E[v2] = {mean(vals):.6f}, Var = {variance(vals):.6f}, N = {len(vals):,}")
        # 分布
        dist = Counter(vals)
        total = len(vals)
        for k in range(1, 8):
            p = dist.get(k, 0) / total
            print(f"    P(v2={k}) = {p:.5f}  (Geom: {0.5**k:.5f})")

    # 残差: v2 - E[v2 | n mod 4]
    # n=1 mod 4 のとき E[v2]=? , n=3 mod 4 のとき v2=1常に
    # 実際: n=3 mod 4 → 3n+1 = 3*3+1=10, v2(10)=1
    #        n=1 mod 4 → 3n+1 = 3*1+1=4, v2(4)=2 最低
    # n=3 mod 4: v2 は常に1? 確認
    vals_mod3 = [val for seq in mod4_sequences for (r, val) in seq if r == 3]
    dist_mod3 = Counter(vals_mod3)
    print(f"\n  n=3 mod 4 の v2 分布: {dict(dist_mod3.most_common(5))}")

    # mod 4 の系列自体の相関
    mod4_only = []
    for seq in mod4_sequences:
        mod4_only.append([r for r, v in seq])

    # n mod 4 の系列のACF
    all_r4 = []
    for seq in mod4_only:
        all_r4.extend(seq)
    mu_r4 = mean(all_r4)
    var_r4 = variance(all_r4)
    print(f"\n  mod4系列: E = {mu_r4:.4f}, Var = {var_r4:.4f}")

    if var_r4 > 0:
        for lag in [1, 2, 3, 4, 5]:
            cov = 0.0
            cnt = 0
            for seq in mod4_only:
                for i in range(len(seq) - lag):
                    cov += (seq[i] - mu_r4) * (seq[i+lag] - mu_r4)
                    cnt += 1
            acf_lag = (cov / cnt) / var_r4 if cnt > 0 else 0
            print(f"  mod4 ACF(lag={lag}) = {acf_lag:.6f}")

# ============================================================
# 分析7: 2-adic から 3-adic 写像の転送行列分析
# ============================================================

def transfer_matrix_analysis():
    """Syracuse写像の mod 2^k での遷移行列を構成し、
    そのスペクトルギャップから混合時間を推定"""
    print("\n" + "=" * 70)
    print("分析7: Syracuse mod 2^k 遷移行列のスペクトル分析")
    print("=" * 70)

    for k in [3, 4, 5, 6]:
        mod = 2 ** k
        # 奇数 mod 2^k の状態空間
        states = [r for r in range(mod) if r % 2 == 1]
        n_states = len(states)
        state_idx = {s: i for i, s in enumerate(states)}

        # 遷移カウント（実データから）
        trans = defaultdict(lambda: Counter())
        N_MAX = 100_000
        for n in range(1, N_MAX + 1, 2):
            r_from = n % mod
            s_next = syracuse(n)
            r_to = s_next % mod
            if r_from in state_idx and r_to in state_idx:
                trans[r_from][r_to] += 1

        # 遷移確率行列（簡易的にべき乗法でスペクトルギャップ推定）
        # まず行列を構成
        matrix = []
        for s in states:
            row = []
            total = sum(trans[s].values())
            for t in states:
                row.append(trans[s].get(t, 0) / total if total > 0 else 0)
            matrix.append(row)

        # 定常分布（べき乗法）
        vec = [1.0 / n_states] * n_states
        for _ in range(100):
            new_vec = [0.0] * n_states
            for j in range(n_states):
                for i in range(n_states):
                    new_vec[j] += vec[i] * matrix[i][j]
            norm = sum(new_vec)
            vec = [v / norm for v in new_vec]

        # 2番目に大きい固有値の推定（べき乗法）
        # v - (v . pi) * 1 を使う
        test = [random.gauss(0, 1) for _ in range(n_states)]
        # pi との直交化
        dot = sum(test[i] * vec[i] for i in range(n_states))
        test = [test[i] - dot for i in range(n_states)]

        for _ in range(200):
            new_test = [0.0] * n_states
            for j in range(n_states):
                for i in range(n_states):
                    new_test[j] += test[i] * matrix[i][j]
            # 直交化
            dot = sum(new_test[i] * vec[i] for i in range(n_states))
            new_test = [new_test[i] - dot for i in range(n_states)]
            norm = math.sqrt(sum(v**2 for v in new_test))
            if norm > 1e-12:
                new_test = [v / norm for v in new_test]
            test = new_test

        # Rayleigh quotient for lambda_2
        Mv = [0.0] * n_states
        for j in range(n_states):
            for i in range(n_states):
                Mv[j] += test[i] * matrix[i][j]
        lambda2 = sum(test[i] * Mv[i] for i in range(n_states))

        gap = 1.0 - abs(lambda2)
        mix_time = 1.0 / gap if gap > 0 else float('inf')

        print(f"\n  mod 2^{k} (|states|={n_states}):")
        print(f"    |lambda_2| ~ {abs(lambda2):.6f}")
        print(f"    spectral gap ~ {gap:.6f}")
        print(f"    mixing time ~ {mix_time:.1f} steps")
        print(f"    定常分布 (一部): {', '.join(f'{states[i]}:{vec[i]:.4f}' for i in range(min(5, n_states)))}")

# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 80)
    print("Tao Syracuse RV 相関構造 深掘り分析")
    print("=" * 80)

    t0 = time.time()

    analyze_large_values_only()
    analyze_random_large_odd()
    analyze_v3_dependence()
    analyze_subdiffusion_mechanism()
    estimate_memory_length()
    analyze_mod4_deterministic()
    transfer_matrix_analysis()

    total_time = time.time() - t0
    print(f"\n{'='*80}")
    print(f"総実行時間: {total_time:.1f}秒")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
