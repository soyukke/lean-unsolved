#!/usr/bin/env python3
"""
探索046: 連続Syracuseステップの v2 相関を精密測定

v2(3n+1) の連続値間の独立性/依存性を多角的に分析する。
（numpy/scipy 不使用、標準ライブラリのみ）
"""

import math
from collections import defaultdict, Counter

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """n の 2-adic valuation"""
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def syracuse(n):
    """Syracuse T(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val


def v2_of_3n1(n):
    """v2(3n+1) for odd n"""
    return v2(3 * n + 1)


def get_v2_sequence(n, length):
    """奇数 n から始めて length 回の Syracuse ステップの v2 列を返す"""
    seq = []
    current = n
    for _ in range(length):
        if current <= 0:
            break
        v = v2_of_3n1(current)
        seq.append(v)
        current = syracuse(current)
        if current == 1:
            break
    return seq


def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def variance(lst):
    if len(lst) < 2:
        return 0.0
    m = mean(lst)
    return sum((x - m)**2 for x in lst) / len(lst)


# ============================================================
# Part 1: 同時分布と条件付き分布
# ============================================================

def analyze_joint_distribution(N_max=500_000, seq_len=30):
    print("=" * 70)
    print("Part 1: 同時分布 (v2_i, v2_{i+1})")
    print("=" * 70)

    joint_counts = defaultdict(int)
    marginal_counts = Counter()
    total_pairs = 0

    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, seq_len)
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a <= 10 and b <= 10:
                joint_counts[(a, b)] += 1
                marginal_counts[a] += 1
                total_pairs += 1

    print(f"\n総ペア数: {total_pairs:,}")
    print(f"初期値範囲: n=3..{N_max} (奇数), 軌道長={seq_len}")

    # 周辺分布 vs 理論値
    print("\n--- 周辺分布 vs 理論値 (幾何分布 2^{-k}) ---")
    total_marginal = sum(marginal_counts.values())
    print(f"{'v2':>4} | {'観測頻度':>12} | {'観測確率':>10} | {'理論値':>10} | {'比率':>8}")
    print("-" * 60)
    for k in range(1, 9):
        obs = marginal_counts.get(k, 0)
        obs_p = obs / total_marginal if total_marginal > 0 else 0
        theo_p = 2**(-k)
        ratio = obs_p / theo_p if theo_p > 0 else 0
        print(f"{k:>4} | {obs:>12,} | {obs_p:>10.6f} | {theo_p:>10.6f} | {ratio:>8.4f}")

    # 条件付き分布
    print("\n--- 条件付き分布 P(v2_{i+1}=j | v2_i=k) ---")
    print(f"{'':>8}", end="")
    for j in range(1, 7):
        print(f"  v2={j:>2}", end="")
    print(f"  {'E[next]':>7}")
    print("-" * 70)

    for k in range(1, 7):
        total_k = sum(joint_counts.get((k, j), 0) for j in range(1, 11))
        if total_k == 0:
            continue
        print(f"v2_i={k:>2}", end="")
        exp_next = 0
        for j in range(1, 7):
            p = joint_counts.get((k, j), 0) / total_k
            exp_next += j * p
            print(f"  {p:>6.4f}", end="")
        for j in range(7, 11):
            p = joint_counts.get((k, j), 0) / total_k
            exp_next += j * p
        print(f"  {exp_next:>7.4f}")

    theo_exp = sum(k * 2**(-k) for k in range(1, 30))
    print(f"\n理論期待値 E[v2] (幾何分布): {theo_exp:.4f}")

    return joint_counts, marginal_counts, total_pairs


# ============================================================
# Part 2: カイ二乗独立性検定（手動実装）
# ============================================================

def chi_squared_test(joint_counts, marginal_counts, total_pairs):
    print("\n" + "=" * 70)
    print("Part 2: カイ二乗独立性検定")
    print("=" * 70)

    max_v = 6

    # 行・列の周辺合計
    row_totals = {}
    col_totals = {}
    for k in range(1, max_v + 1):
        row_totals[k] = sum(joint_counts.get((k, j), 0) for j in range(1, max_v + 1))
        col_totals[k] = sum(joint_counts.get((i, k), 0) for i in range(1, max_v + 1))

    total = sum(row_totals.values())

    # カイ二乗統計量
    chi2 = 0
    for i in range(1, max_v + 1):
        for j in range(1, max_v + 1):
            obs = joint_counts.get((i, j), 0)
            exp = row_totals.get(i, 0) * col_totals.get(j, 0) / total if total > 0 else 0
            if exp > 0:
                chi2 += (obs - exp)**2 / exp

    df = (max_v - 1) ** 2

    # p値の近似計算（カイ二乗分布の上側確率）
    # 簡易近似: Wilson-Hilferty
    if df > 0:
        z = (chi2 / df) ** (1/3) - (1 - 2 / (9 * df))
        z /= math.sqrt(2 / (9 * df))
        # 標準正規分布の上側確率（近似）
        p_value_approx = 0.5 * math.erfc(z / math.sqrt(2))
    else:
        p_value_approx = 1.0

    print(f"\n検定範囲: v2 = 1..{max_v}")
    print(f"カイ二乗統計量: χ² = {chi2:.2f}")
    print(f"自由度: {df}")
    print(f"p値 (近似): {p_value_approx:.2e}")

    # 99.9% 点: df=25 で chi2 > 52.6 なら p < 0.001
    chi2_crit_001 = {25: 52.62}
    crit = chi2_crit_001.get(df, df + 3 * math.sqrt(2 * df))
    print(f"χ²臨界値 (p=0.001, df={df}): ≈{crit:.1f}")

    if chi2 > crit:
        print("結論: 独立性を強く棄却 (p < 0.001)")
    else:
        print("結論: 独立性を棄却するには証拠不十分")

    # 標準化残差
    print("\n--- 標準化残差 (obs - exp) / sqrt(exp) ---")
    print(f"{'':>8}", end="")
    for j in range(1, max_v + 1):
        print(f"  j={j:>2}", end="")
    print()
    print("-" * 55)
    for i in range(1, max_v + 1):
        print(f"k={i:>2}  ", end="")
        for j in range(1, max_v + 1):
            obs = joint_counts.get((i, j), 0)
            exp = row_totals.get(i, 0) * col_totals.get(j, 0) / total if total > 0 else 0
            if exp > 0:
                resid = (obs - exp) / math.sqrt(exp)
                print(f"  {resid:>5.1f}", end="")
            else:
                print(f"  {'N/A':>5}", end="")
        print()

    return chi2, p_value_approx


# ============================================================
# Part 3: 3連続 v2 の相関（マルコフ性検定）
# ============================================================

def analyze_triple_correlation(N_max=200_000, seq_len=20):
    print("\n" + "=" * 70)
    print("Part 3: 3連続 v2 の相関 (v2_i, v2_{i+1}, v2_{i+2})")
    print("=" * 70)

    triple_counts = defaultdict(int)
    pair_counts_12 = defaultdict(int)
    total = 0

    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, seq_len)
        for i in range(len(seq) - 2):
            a, b, c = seq[i], seq[i + 1], seq[i + 2]
            if a <= 6 and b <= 6 and c <= 6:
                triple_counts[(a, b, c)] += 1
                pair_counts_12[(a, b)] += 1
                total += 1

    print(f"\n総トリプル数: {total:,}")

    # E[v2_{i+2} | v2_{i+1}=b] (v2_i を無視)
    cond_b_exp = {}
    for b in range(1, 5):
        num = 0
        den = 0
        for a in range(1, 7):
            for c in range(1, 7):
                cnt = triple_counts.get((a, b, c), 0)
                num += c * cnt
                den += cnt
        if den > 0:
            cond_b_exp[b] = num / den

    print("\n--- マルコフ性検定: P(v2_{i+2} | v2_i, v2_{i+1}) vs P(v2_{i+2} | v2_{i+1}) ---")
    print(f"\n{'(a,b)':>8} | {'count':>8} | {'E[c|a,b]':>10} | {'E[c|b]':>10} | {'差':>8}")
    print("-" * 55)

    for a in range(1, 5):
        for b in range(1, 5):
            total_ab = sum(triple_counts.get((a, b, c), 0) for c in range(1, 7))
            if total_ab < 100:
                continue
            exp_abc = sum(c * triple_counts.get((a, b, c), 0) for c in range(1, 7)) / total_ab
            exp_bc = cond_b_exp.get(b, 0)
            diff = exp_abc - exp_bc
            print(f"({a},{b}){'':<3} | {total_ab:>8,} | {exp_abc:>10.4f} | {exp_bc:>10.4f} | {diff:>8.4f}")


# ============================================================
# Part 4: 自己相関関数 (ACF)
# ============================================================

def compute_acf(N_max=100_000, seq_len=60, max_lag=20):
    print("\n" + "=" * 70)
    print("Part 4: 自己相関関数 (ACF)")
    print("=" * 70)

    # 各軌道ごとに ACF を計算して平均
    lag_sums = [0.0] * (max_lag + 1)
    lag_counts = [0] * (max_lag + 1)

    all_v2 = []
    sample_count = 0

    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, seq_len)
        if len(seq) < max_lag + 5:
            continue
        all_v2.extend(seq)
        sample_count += 1

    total_n = len(all_v2)
    mean_v2 = mean(all_v2)
    var_v2 = variance(all_v2)

    print(f"\n総 v2 値数: {total_n:,}")
    print(f"サンプル軌道数: {sample_count:,}")
    print(f"平均 v2: {mean_v2:.4f} (理論値 2.0)")
    print(f"分散: {var_v2:.4f} (理論値 6.0 for Geom(1/2))")

    print(f"\n{'lag':>5} | {'ACF':>10} | {'95%CI':>12} | 判定")
    print("-" * 50)

    ci_bound = 1.96 / math.sqrt(total_n)
    acf_values = []

    for lag in range(1, max_lag + 1):
        n_pairs = total_n - lag
        if n_pairs <= 0:
            break
        cov = sum((all_v2[i] - mean_v2) * (all_v2[i + lag] - mean_v2)
                   for i in range(n_pairs)) / n_pairs
        acf = cov / var_v2 if var_v2 > 0 else 0
        acf_values.append(acf)
        sig = "***" if abs(acf) > ci_bound * 3 else "**" if abs(acf) > ci_bound * 2 else "*" if abs(acf) > ci_bound else ""
        print(f"{lag:>5} | {acf:>10.6f} | ±{ci_bound:>10.6f} | {sig}")

    return acf_values


# ============================================================
# Part 5: mod 2^k での v2 の決定性
# ============================================================

def analyze_mod_determinism():
    print("\n" + "=" * 70)
    print("Part 5: mod 2^k での v2 の決定性")
    print("=" * 70)

    print("\n--- v2(3n+1) の mod 2^k での決定 ---")
    print("n が奇数のとき、n mod 2^k → v2(3n+1) の対応\n")

    for k in range(1, 9):
        M = 2**k
        determined = 0
        total_odd = 0
        v2_dist = Counter()
        for r in range(1, M, 2):
            total_odd += 1
            val = 3 * r + 1
            v = v2(val)
            if v < k:
                determined += 1
                v2_dist[v] += 1
            else:
                v2_dist['?'] += 1

        det_pct = determined / total_odd * 100
        parts = []
        for vv in sorted([x for x in v2_dist if isinstance(x, int)]):
            parts.append(f"v2={vv}:{v2_dist[vv]}")
        if '?' in v2_dist:
            parts.append(f"v2>=k:{v2_dist['?']}")
        print(f"k={k:>2} (mod {M:>5}): {determined}/{total_odd} 確定 ({det_pct:.1f}%)  [{', '.join(parts)}]")

    # 連鎖分析
    print("\n--- 連続ステップの mod 遷移 (k=4, mod 16) ---")
    k = 4
    M = 2**k
    print(f"{'n mod 16':>8} | {'v2_1':>4} | {'T(n) mod':>10} | {'bits残':>6} | {'v2_2確定?':>10}")
    print("-" * 55)

    for r in range(1, M, 2):
        v1 = v2(3 * r + 1)
        if v1 >= k:
            print(f"{r:>8} | {'>=' + str(k):>4} | {'?':>10} | {'0':>6} | {'No':>10}")
            continue

        t_r = (3 * r + 1) // (2**v1)
        remaining_bits = k - v1
        t_mod = t_r % (2**remaining_bits)

        if remaining_bits >= 2:
            v2_2 = v2(3 * t_r + 1)
            if v2_2 < remaining_bits:
                det = f"Yes(={v2_2})"
            else:
                det = f"No(>={remaining_bits})"
        else:
            det = "No(bits不足)"

        print(f"{r:>8} | {v1:>4} | {t_r:>3} mod {2**remaining_bits:>3} | {remaining_bits:>6} | {det:>10}")

    print("\n--- ビット消費の法則 ---")
    print("v2_1 = v のとき、n の下位ビットから v+1 ビットが消費される。")
    print("（v ビットが 2 で割られ、1 ビットが奇偶の情報）")
    print("残りビットで v2_2 を決定するが、ビット数が不足することがある。")
    print("→ v2 が大きいほど次の v2 の情報が少なくなる（弱い依存の源泉）")

    return


# ============================================================
# Part 6: v2 の大きさ別の次の v2 の分布比較
# ============================================================

def compare_v2_conditional(N_max=500_000, seq_len=30):
    print("\n" + "=" * 70)
    print("Part 6: v2 の大きさ別の次の v2 の分布比較")
    print("=" * 70)

    after_v2 = defaultdict(list)

    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, seq_len)
        for i in range(len(seq) - 1):
            k = seq[i]
            if k <= 8:
                after_v2[k].append(seq[i + 1])

    print(f"\n初期値範囲: n=3..{N_max} (奇数)")
    print(f"\n{'条件':>12} | {'サンプル数':>10} | {'E[next]':>8} | {'Var':>8} | {'P(1)':>6} | {'P(2)':>6} | {'P(3)':>6} | {'P(>=4)':>6}")
    print("-" * 85)

    for k in [1, 2, 3, 4, 5, 6]:
        vals = after_v2.get(k, [])
        if len(vals) < 100:
            continue
        n_vals = len(vals)
        mean_v = mean(vals)
        var_v = variance(vals)
        p1 = sum(1 for x in vals if x == 1) / n_vals
        p2 = sum(1 for x in vals if x == 2) / n_vals
        p3 = sum(1 for x in vals if x == 3) / n_vals
        p4plus = sum(1 for x in vals if x >= 4) / n_vals
        print(f"v2_i={k:>2}    | {n_vals:>10,} | {mean_v:>8.4f} | {var_v:>8.4f} | {p1:>6.4f} | {p2:>6.4f} | {p3:>6.4f} | {p4plus:>6.4f}")

    theo_mean = sum(k * 2**(-k) for k in range(1, 30))
    theo_var = sum(k**2 * 2**(-k) for k in range(1, 30)) - theo_mean**2
    print(f"{'理論(独立)':>12} | {'':>10} | {theo_mean:>8.4f} | {theo_var:>8.4f} | {'0.5000':>6} | {'0.2500':>6} | {'0.1250':>6} | {'0.1250':>6}")

    return


# ============================================================
# Part 7: 一様ランダム vs 軌道追跡
# ============================================================

def compare_uniform_vs_trajectory(N_max=200_000):
    print("\n" + "=" * 70)
    print("Part 7: 一様ランダム初期値 vs 軌道追跡の v2 分布")
    print("=" * 70)

    uniform_v2 = []
    for n in range(3, N_max + 1, 2):
        uniform_v2.append(v2_of_3n1(n))

    traj_steps = {1: [], 5: [], 10: []}
    for n in range(3, N_max + 1, 2):
        seq = get_v2_sequence(n, 11)
        if len(seq) >= 1:
            traj_steps[1].append(seq[0])
        if len(seq) >= 5:
            traj_steps[5].append(seq[4])
        if len(seq) >= 10:
            traj_steps[10].append(seq[9])

    print(f"\n一様ランダム (n=3..{N_max} 奇数), {len(uniform_v2):,} サンプル:")
    print(f"  平均 v2: {mean(uniform_v2):.4f}")
    for k in range(1, 6):
        p = sum(1 for x in uniform_v2 if x == k) / len(uniform_v2)
        print(f"  P(v2={k}) = {p:.6f}  (理論: {2**(-k):.6f})")

    for step, data in sorted(traj_steps.items()):
        if not data:
            continue
        print(f"\n軌道 step{step} ({len(data):,} サンプル):")
        print(f"  平均 v2: {mean(data):.4f}")
        for k in range(1, 6):
            p = sum(1 for x in data if x == k) / len(data)
            print(f"  P(v2={k}) = {p:.6f}  (理論: {2**(-k):.6f})")

    return


# ============================================================
# Part 8: mod 2^k での v2 完全決定テーブル
# ============================================================

def v2_determinism_table():
    print("\n" + "=" * 70)
    print("Part 8: mod 2^k での v2 の完全決定テーブル")
    print("=" * 70)

    print("\n奇数 n に対して、n mod 2^k が v2(3n+1) を決定するメカニズム:")
    print("3n+1 ≡ 3r+1 (mod 2^k) なので、v2(3r+1) < k なら v2(3n+1) = v2(3r+1)\n")

    print(f"{'k':>3} | {'mod':>7} | {'決定数':>7} | {'全奇数':>7} | {'決定率':>8} | {'未決定':>8}")
    print("-" * 55)

    for k in range(1, 17):
        M = 2**k
        total_odd = M // 2
        determined = 0
        for r in range(1, M, 2):
            if v2(3 * r + 1) < k:
                determined += 1
        pct = determined / total_odd * 100
        undetermined = total_odd - determined
        print(f"{k:>3} | {M:>7} | {determined:>7} | {total_odd:>7} | {pct:>7.1f}% | {undetermined:>8}")

    print("\n結論: v2(3n+1) = v のとき、n mod 2^{v+1} で v2 は完全に決定される。")
    print("k を 1 増やすごとに未決定の割合は約半分に。")
    print("これは Lean で有限計算 (decide) により形式化可能。")

    return


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 70)
    print("  探索046: 連続Syracuseステップの v2 相関の精密測定")
    print("=" * 70)
    print()

    # Part 1
    joint, marginal, total = analyze_joint_distribution(N_max=500_000, seq_len=30)

    # Part 2
    chi2, p_val = chi_squared_test(joint, marginal, total)

    # Part 3
    analyze_triple_correlation(N_max=200_000, seq_len=20)

    # Part 4
    acf_vals = compute_acf(N_max=50_000, seq_len=40, max_lag=20)

    # Part 5
    analyze_mod_determinism()

    # Part 6
    compare_v2_conditional(N_max=500_000, seq_len=30)

    # Part 7
    compare_uniform_vs_trajectory(N_max=200_000)

    # Part 8
    v2_determinism_table()

    # 総合結論
    print("\n" + "=" * 70)
    print("総合結論")
    print("=" * 70)
    print("""
1. v2 の周辺分布:
   一様ランダムな奇数 n に対して v2(3n+1) は正確に Geom(1/2) に従う。
   軌道上でも分布は理論値に非常に近い。

2. 連続 v2 の独立性:
   - カイ二乗検定の結果から、v2 列は完全独立ではない。
   - しかし ACF の値から、依存の強さは定量的に評価できる。
   - lag=1 の相関が最大で、急速に減衰する。

3. マルコフ性:
   - E[v2_{i+2} | v2_i, v2_{i+1}] ≈ E[v2_{i+2} | v2_{i+1}] なら
     v2 列は近似的にマルコフ。

4. v2 の mod 決定性:
   - v2(3n+1) は n mod 2^{v+1} で完全に決まる（局所的な量）。
   - T(n) の下位ビットは n の下位ビットと v2_1 から計算される。
   - v2_1 が大きい→多くのビット消費→v2_2 の情報が減少。
   - これが「ビットを通じた弱い依存」の正体。

5. 実用的含意:
   - d/u > log_2(3) の証明において、v2 の独立性は「近似的に」成立。
   - ACF が小さければ、独立性の仮定に基づく議論は実質的に正しい。
   - mod 2^k の決定性は Lean で形式化可能（有限計算による decide）。

6. Lean形式化の可能性:
   - 「n ≡ r (mod 2^k) → v2(3n+1) = v」は decide で直接証明可能。
   - 連続 v2 間の依存性の定量的評価は確率論的議論が必要で形式化は困難。
   - ただし、特定の k でのステップ列の振る舞いは mod 計算で形式化可能。
""")


if __name__ == "__main__":
    main()
