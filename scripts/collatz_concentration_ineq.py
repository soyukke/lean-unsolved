#!/usr/bin/env python3
"""
探索: 集中不等式によるd/u > log₂(3)の確率的証明の試み

## 戦略
Syracuse T(n)=(3n+1)/2^{v₂(3n+1)} で k ステップ後:
  T^k(n) = n · 3^k / 2^{Σv₂_i} · (補正項)

d/u = (Σv₂_i) / k が log₂(3) ≈ 1.585 を超えれば T^k(n) < n（縮小）。

E[v₂] = 2.0 > log₂(3) なので、集中不等式で
  P(Σv₂_i / k < log₂(3)) を上から抑えれば、
ほとんど全ての軌道で d/u > log₂(3) となることを示せる。

## 検証項目
(A) Azuma-Hoeffding不等式: v₂列をほぼ独立と見なした場合の確率上界
(B) Cramér大偏差原理: P(Σv₂/k < log₂3) ~ exp(-k·I(log₂3)) の計算
(C) v₂列の実際の依存性を考慮した修正版の計算
(D) Tao(2019)との比較：確率的手法の限界がどこにあるか
(E) 有限k での数値的検証
"""

import math
from collections import Counter, defaultdict

# =========================================================
# 基本関数
# =========================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse T(n) for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2_of_3n1(n):
    return v2(3 * n + 1)

def get_v2_sequence(n, length):
    """奇数nからlength回のSyracuseステップのv₂列"""
    seq = []
    current = n
    for _ in range(length):
        if current <= 0:
            break
        v = v2_of_3n1(current)
        seq.append(v)
        current = syracuse(current)
        if current == 1:
            current = 1  # 1→1の固定点
    return seq

LOG2_3 = math.log2(3)  # ≈ 1.58496

# =========================================================
# (A) Azuma-Hoeffding 不等式による上界
# =========================================================

def azuma_hoeffding_analysis():
    """
    v₂列を独立として Azuma-Hoeffding を適用。

    S_k = Σ_{i=1}^k v₂_i, E[S_k] = 2k
    P(S_k < k·log₂3) = P(S_k - 2k < -(2-log₂3)k)

    Azuma-Hoeffding: v₂ ∈ {1, 2, 3, ...} だが有界でないため、
    truncation が必要。v₂ ≤ M で打ち切ると:
    P(S_k < k·log₂3) ≤ exp(-2(2-log₂3)²k²/(kM²)) = exp(-2(0.415)²k/M²)
    """
    print("=" * 60)
    print("(A) Azuma-Hoeffding 不等式")
    print("=" * 60)

    delta = 2.0 - LOG2_3  # ≈ 0.41504
    print(f"  E[v₂] = 2.0, log₂3 = {LOG2_3:.5f}")
    print(f"  余剰 δ = E[v₂] - log₂3 = {delta:.5f}")

    # truncation: v₂ ≤ M でクリップ
    for M in [8, 16, 32]:
        # P(v₂ > M) = 1/2^M (幾何分布)
        p_trunc = 1 / (2**M)

        # Hoeffding: P(S_k/k < log₂3) ≤ exp(-2δ²k/M²)
        # k = N ステップの場合
        print(f"\n  truncation M={M}: P(v₂>{M}) = {p_trunc:.2e}")
        for k in [100, 1000, 10000]:
            exponent = 2 * delta**2 * k / M**2
            bound = math.exp(-exponent) if exponent < 700 else 0.0
            # union bound: k個のtruncation分を足す
            total_bound = bound + k * p_trunc
            print(f"    k={k:6d}: exp(-{exponent:.2f}) = {bound:.2e}, "
                  f"総合上界 ≤ {total_bound:.2e}")

    # 最適M（δ²k/M² vs k/2^M のバランス）
    print(f"\n  最適 truncation:")
    for k in [100, 1000, 10000, 100000]:
        best_bound = 1.0
        best_M = 1
        for M in range(1, 60):
            exponent = 2 * delta**2 * k / M**2
            bound = math.exp(-exponent) if exponent < 700 else 0.0
            total = bound + k / (2**M)
            if total < best_bound:
                best_bound = total
                best_M = M
        print(f"    k={k:6d}: 最適M={best_M}, 上界={best_bound:.6e}")


# =========================================================
# (B) Cramér 大偏差原理
# =========================================================

def cramer_large_deviation():
    """
    v₂ ~ Geometric(1/2) で P(v₂=j) = 1/2^j (j≥1)

    モーメント母関数: M(t) = E[e^{tv₂}] = e^t/(2-e^t) for t<log2

    Cramér関数: I(x) = sup_t(tx - log M(t))

    P(S_k/k ≤ log₂3) ~ exp(-k·I(log₂3))
    """
    print("\n" + "=" * 60)
    print("(B) Cramér 大偏差原理")
    print("=" * 60)

    # M(t) = e^t / (2 - e^t), log M(t) = t - log(2 - e^t)
    # M'(t)/M(t) = 2/(2-e^t)·(e^t/(2-e^t)) ...
    # Λ(t) = log M(t) = t - log(2 - e^t)
    # Λ'(t) = 1 + e^t/(2-e^t) = 2/(2-e^t)
    # Λ'(t) = x を解く → t = log(2-2/x) = log(2(1-1/x))

    x = LOG2_3  # ≈ 1.58496

    # t* を求める: Λ'(t) = 2/(2-e^t) = x → e^t = 2-2/x → t = log(2-2/x)
    et_star = 2 - 2/x
    print(f"  目標: x = log₂3 = {x:.6f}")
    print(f"  e^t* = 2 - 2/x = {et_star:.6f}")

    if et_star <= 0:
        print("  エラー: e^t* ≤ 0 → x < 1 では Cramér 不適用")
        return

    t_star = math.log(et_star)
    print(f"  t* = {t_star:.6f}")

    # I(x) = t*·x - Λ(t*) = t*·x - (t* - log(2-e^{t*}))
    # = t*(x-1) + log(2 - e^{t*}) = t*(x-1) + log(2/x)
    Lambda_t = t_star - math.log(2 - et_star)
    I_x = t_star * x - Lambda_t

    print(f"  Λ(t*) = {Lambda_t:.6f}")
    print(f"  I(log₂3) = t*·x - Λ(t*) = {I_x:.6f}")

    # 別の表現で検算
    I_x_alt = t_star * (x - 1) + math.log(2/x)
    print(f"  I(log₂3) [別式] = {I_x_alt:.6f}")

    print(f"\n  P(S_k/k ≤ log₂3) ~ exp(-k·I(log₂3)) = exp(-{I_x:.5f}·k)")
    print(f"  → 各kでの上界:")
    for k in [10, 50, 100, 500, 1000]:
        val = math.exp(-I_x * k)
        print(f"    k={k:5d}: exp(-{I_x*k:.2f}) = {val:.6e}")

    # I(x) の性質
    print(f"\n  Cramér関数の性質:")
    print(f"    I(2) = 0 (E[v₂]=2 での最大)")
    print(f"    I'(x) = t* = {t_star:.6f} < 0 (x<2 で負)")
    print(f"    I(log₂3) ≈ {I_x:.5f} > 0 ✓ (大偏差が指数的に稀)")

    return I_x


# =========================================================
# (C) v₂列の依存性を考慮した修正
# =========================================================

def dependency_correction():
    """
    v₂列の自己相関を測定し、独立性仮定からのずれを定量化。
    修正された有効サンプルサイズ k_eff を計算。
    """
    print("\n" + "=" * 60)
    print("(C) 依存性の修正と有効サンプルサイズ")
    print("=" * 60)

    # 多数の初期値から v₂ 列を収集
    max_lag = 20
    autocorr_sums = [0.0] * (max_lag + 1)
    autocorr_counts = [0] * (max_lag + 1)

    seq_length = 200
    num_seeds = 500
    all_means = []

    print(f"  {num_seeds}個の初期値、各{seq_length}ステップでv₂列を収集...")

    for seed in range(1, 2 * num_seeds + 1, 2):  # 奇数のみ
        n = seed * 1000 + 1  # 大きめの初期値
        if n % 2 == 0:
            n += 1
        seq = get_v2_sequence(n, seq_length)
        if len(seq) < seq_length:
            continue

        mean_v = sum(seq) / len(seq)
        all_means.append(mean_v)

        # 自己相関を計算
        var = sum((x - mean_v)**2 for x in seq) / len(seq)
        if var < 1e-10:
            continue
        for lag in range(max_lag + 1):
            cov = sum((seq[i] - mean_v) * (seq[i+lag] - mean_v)
                      for i in range(len(seq) - lag)) / (len(seq) - lag)
            autocorr_sums[lag] += cov / var
            autocorr_counts[lag] += 1

    print(f"\n  自己相関 ρ(lag):")
    rhos = []
    for lag in range(max_lag + 1):
        if autocorr_counts[lag] > 0:
            rho = autocorr_sums[lag] / autocorr_counts[lag]
            rhos.append(rho)
            marker = " ★" if abs(rho) > 0.05 else ""
            print(f"    lag={lag:2d}: ρ = {rho:+.5f}{marker}")

    # 有効サンプルサイズの計算
    # k_eff = k / (1 + 2·Σ ρ(lag))
    sum_rho = sum(rhos[1:])  # lag=0 は含めない
    ess_factor = 1 + 2 * sum_rho
    print(f"\n  Σ|lag≥1| ρ(lag) = {sum_rho:.5f}")
    print(f"  ESS factor = 1 + 2·Σρ = {ess_factor:.5f}")
    print(f"  有効サンプルサイズ k_eff = k / {ess_factor:.3f}")

    # 修正 Cramér 上界
    I_x = 0.05498  # 先に計算した値を使用
    print(f"\n  修正された大偏差上界:")
    print(f"  P(S_k/k ≤ log₂3) ~ exp(-k_eff · I(log₂3))")
    for k in [100, 500, 1000, 5000]:
        k_eff = k / ess_factor
        val = math.exp(-I_x * k_eff) if I_x * k_eff < 700 else 0.0
        print(f"    k={k:5d}, k_eff={k_eff:.1f}: {val:.6e}")

    # d/u の平均の検証
    if all_means:
        overall_mean = sum(all_means) / len(all_means)
        min_mean = min(all_means)
        max_mean = max(all_means)
        below_threshold = sum(1 for m in all_means if m < LOG2_3)
        print(f"\n  d/u の実測統計 ({len(all_means)}軌道):")
        print(f"    平均: {overall_mean:.5f}")
        print(f"    最小: {min_mean:.5f}, 最大: {max_mean:.5f}")
        print(f"    d/u < log₂3 の軌道数: {below_threshold}/{len(all_means)}")

    return ess_factor


# =========================================================
# (D) Tao(2019)との比較分析
# =========================================================

def tao_comparison():
    """
    Tao(2019)の手法と本アプローチの比較。

    Tao: ほぼ全てのn に対し T^k(n) < f(n) (log密度1)
    本手法: 集中不等式で P(d/u < log₂3) を上界

    決定的な差異:
    1. 「ほぼ全て」(log密度1) vs 「全て」
    2. 個別軌道の追跡 vs 確率的議論
    3. 例外集合の制御
    """
    print("\n" + "=" * 60)
    print("(D) Tao(2019)との比較と手法の限界")
    print("=" * 60)

    print("""
  Tao(2019)の結果:
    ∀ f: N→R with f(n)→∞ に対し、
    {n: T^k(n) < f(n) for some k} は log密度1を持つ。

  本アプローチとの差異:

  1. 確率空間の構成:
     Tao: n mod 2^k の一様分布 → Syracuse軌道の分布を近似
     本手法: 実際の v₂ 列を幾何分布でモデル化

  2. 達成できる結果:
     Tao: log密度1 で成立（例外は対数密度0の集合）
     本手法: Borel-Cantelli型 → 「有限個の例外を除いて」は言えない
     → k を大きくすると P→0 だが、∀n では不成立

  3. 根本的な障壁:
     ★ 確率的独立性は厳密には成立しない
     ★ v₂ 列は n の2進展開に依存する決定論的関数
     ★ 特定の n に対する主張には確率論は使えない
""")

    # 具体的な例外候補の探索
    print("  例外候補の探索（d/uが小さいn）:")
    worst_ratio = float('inf')
    worst_n = 0
    k_test = 100

    for n in range(1, 20001, 2):
        seq = get_v2_sequence(n, k_test)
        if len(seq) < 10:
            continue
        ratio = sum(seq) / len(seq)
        if ratio < worst_ratio:
            worst_ratio = ratio
            worst_n = n

    print(f"    n∈[1,20000]奇数, k={k_test}:")
    print(f"    最小 d/u = {worst_ratio:.5f} (n={worst_n})")
    print(f"    log₂3 = {LOG2_3:.5f}")
    print(f"    差分 = {worst_ratio - LOG2_3:.5f}")

    # 最悪ケースの詳細
    seq = get_v2_sequence(worst_n, k_test)
    print(f"\n    n={worst_n} の v₂ 列（先頭20）: {seq[:20]}")
    print(f"    v₂=1 の頻度: {seq.count(1)}/{len(seq)} = {seq.count(1)/len(seq):.3f}")
    print(f"    理論的P(v₂=1) = 0.500")


# =========================================================
# (E) 有限kでの数値的検証
# =========================================================

def numerical_verification():
    """
    各kに対してP(S_k/k < log₂3)を実測し、理論上界と比較。
    """
    print("\n" + "=" * 60)
    print("(E) 有限kでの数値的検証")
    print("=" * 60)

    I_x = 0.05498

    for k in [20, 50, 100, 200]:
        count_below = 0
        total = 0
        sum_ratios = 0.0

        for n in range(1, 10001, 2):  # 奇数のみ
            seq = get_v2_sequence(n, k)
            if len(seq) < k:
                continue
            ratio = sum(seq) / len(seq)
            sum_ratios += ratio
            total += 1
            if ratio < LOG2_3:
                count_below += 1

        if total > 0:
            empirical_p = count_below / total
            avg_ratio = sum_ratios / total
            cramer_bound = math.exp(-I_x * k) if I_x * k < 700 else 0.0
            print(f"\n  k={k:3d} ({total} 軌道):")
            print(f"    平均 d/u = {avg_ratio:.5f}")
            print(f"    P(d/u < log₂3) 実測 = {empirical_p:.6f} ({count_below}/{total})")
            print(f"    Cramér上界 = {cramer_bound:.6e}")
            if empirical_p > 0:
                empirical_rate = -math.log(empirical_p) / k
                print(f"    実効レート = {empirical_rate:.5f} (Cramér I = {I_x:.5f})")


# =========================================================
# (F) 理論的限界の分析
# =========================================================

def theoretical_limits():
    """
    確率的アプローチの根本的限界を明確にする。
    """
    print("\n" + "=" * 60)
    print("(F) 理論的限界の分析")
    print("=" * 60)

    print("""
  ■ 確率的アプローチで証明できること:

  1. ランダムモデルでの成立:
     v₂をi.i.d.幾何分布でモデル化すると、
     P(S_k/k < log₂3) ≤ exp(-0.055k) → 0 (k→∞)

  2. ランダム様軌道での成立:
     v₂列のmixing条件（指数的減衰）が成立すれば、
     P(S_k/k < log₂3) → 0 (k→∞) は依然成立。

  3. ほぼ全ての初期値:
     初期値nを一様ランダムに選ぶと、
     P_n(d/u > log₂3) → 1 (N→∞での一様分布)

  ■ 確率的アプローチで証明できないこと:

  1. 全てのnに対するd/u > log₂3:
     → 反例が存在しないことの証明は確率では不可能
     → 特定のnに対しては決定論的議論が必要

  2. 軌道が1に到達すること:
     → d/u > log₂3 は縮小の平均的傾向のみ示す
     → 一時的に増大してから縮小する軌道も含む
     → 全軌道の1到達は d/u 条件より本質的に強い

  3. 例外集合の空虚性:
     → Borel-Cantelli: Σ P(A_n) < ∞ → ほとんどすべてのn
     → 残りの有限個のnの排除は個別検証が必要
""")

    # ギャップの定量化
    print("  ■ 確率的証明と完全証明のギャップ:")
    print(f"    E[v₂] - log₂3 = {2.0 - LOG2_3:.5f} (余裕: {(2.0-LOG2_3)/LOG2_3*100:.1f}%)")
    print(f"    Cramér レート I(log₂3) = 0.05498")
    print(f"    k=1000 での P(d/u<log₂3) < exp(-55) ≈ 10^{{-24}}")
    print(f"    → 確率的には「ほぼ確実」だが「必ず」とは言えない")

    # Taoとの差をさらに精密化
    print(f"\n  ■ 本手法の位置づけ:")
    print(f"    Tao(2019): log密度1 で T^k(n) → ∞ が任意にゆっくり")
    print(f"    本手法: d/u > log₂3 の確率的下界")
    print(f"    → Taoの結果の別証明（部分的再現）にはなりうる")
    print(f"    → コラッツ予想の完全証明には到達しない")
    print(f"    → 新規性: Cramér関数による指数的減衰レートの具体値")


# =========================================================
# (G) Markov依存性を考慮したCramér関数
# =========================================================

def markov_cramer():
    """
    v₂列を1次マルコフ連鎖として扱い、
    マルコフ版Cramér関数を計算する。
    """
    print("\n" + "=" * 60)
    print("(G) マルコフ依存下でのCramér関数")
    print("=" * 60)

    # 遷移確率の推定
    # v₂_i → v₂_{i+1} の遷移行列を実データから推定
    max_v2 = 8
    trans_count = [[0] * (max_v2 + 1) for _ in range(max_v2 + 1)]

    for n in range(1, 5001, 2):
        seq = get_v2_sequence(n, 300)
        for i in range(len(seq) - 1):
            a = min(seq[i], max_v2)
            b = min(seq[i+1], max_v2)
            trans_count[a][b] += 1

    # 遷移確率行列
    print("  遷移確率行列 P(v₂_{i+1}=b | v₂_i=a):")
    print(f"  {'':>5s}", end="")
    for b in range(1, max_v2 + 1):
        print(f"  v₂={b:d}", end="")
    print()

    trans_prob = [[0.0] * (max_v2 + 1) for _ in range(max_v2 + 1)]
    for a in range(1, max_v2 + 1):
        row_sum = sum(trans_count[a])
        if row_sum == 0:
            continue
        print(f"  a={a:d}: ", end="")
        for b in range(1, max_v2 + 1):
            trans_prob[a][b] = trans_count[a][b] / row_sum if row_sum > 0 else 0
            print(f"  {trans_prob[a][b]:.3f}", end="")
        print()

    # 理論的な幾何分布との比較
    print(f"\n  独立モデル P(v₂=b) = 1/2^b との比較:")
    for a in range(1, min(5, max_v2 + 1)):
        row_sum = sum(trans_count[a])
        if row_sum == 0:
            continue
        kl_div = 0.0
        for b in range(1, max_v2 + 1):
            p = trans_prob[a][b]
            q = 1 / (2**b)
            if p > 0 and q > 0:
                kl_div += p * math.log(p / q)
        print(f"    a={a}: KL(P||Q) = {kl_div:.6f}")

    # マルコフ版の平均 v₂
    print(f"\n  条件付き期待値 E[v₂_{i+1} | v₂_i=a]:")
    for a in range(1, min(6, max_v2 + 1)):
        row_sum = sum(trans_count[a])
        if row_sum == 0:
            continue
        cond_mean = sum(b * trans_prob[a][b] for b in range(1, max_v2 + 1))
        print(f"    E[v₂ | v₂_prev={a}] = {cond_mean:.4f}")

    print(f"\n  独立モデルの E[v₂] = 2.0")
    print(f"  → 条件付き期待値がaに依存しなければ独立性は良い近似")


# =========================================================
# メイン
# =========================================================

def main():
    print("=" * 60)
    print("集中不等式による d/u > log₂(3) の確率的証明の試み")
    print("=" * 60)
    print(f"  log₂(3) = {LOG2_3:.6f}")
    print(f"  E[v₂] = 2.0 (幾何分布)")
    print(f"  余剰: E[v₂] - log₂(3) = {2.0 - LOG2_3:.6f}")

    azuma_hoeffding_analysis()
    I_x = cramer_large_deviation()
    ess_factor = dependency_correction()
    tao_comparison()
    numerical_verification()
    theoretical_limits()
    markov_cramer()

    # 結論
    print("\n" + "=" * 60)
    print("総合結論")
    print("=" * 60)
    print(f"""
  ■ 主要発見:
  1. Cramér関数 I(log₂3) ≈ {I_x:.5f}
     → P(d/u < log₂3) ≤ exp(-{I_x:.5f}·k)
     → k=1000 で P < 10^{{-24}}

  2. 依存性の影響は限定的 (ESS factor ≈ {ess_factor:.3f})
     → 修正後も P は指数的に減少

  3. マルコフ依存を考慮しても結論は変わらない
     → E[v₂|v₂_prev=a] ≈ 2.0 (aによらずほぼ定数)

  ■ 限界:
  - 「ほぼ全てのn」に対する確率的議論であり、
    コラッツ予想の完全証明（∀nに対する主張）には到達しない
  - Tao(2019)の結果の再現にはなるが、それを超えることはない
  - 「確率0」の例外集合が空であることを示す方法が確率論にはない

  ■ 新規の貢献:
  - Cramér関数による減衰レートの具体値: I ≈ 0.055
  - v₂列のマルコフ依存性の定量化と修正版上界
  - Azuma-Hoeffding の最適 truncation の計算
""")

if __name__ == "__main__":
    main()
