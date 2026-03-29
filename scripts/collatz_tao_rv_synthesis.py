#!/usr/bin/env python3
"""
Tao Syracuse RV 相関構造 統合分析

前2回の分析で判明した主要な発見:
  1. n=3 mod 4 → v2=1 が決定論的 (非確率的成分)
  2. n=1 mod 4 → v2 ~ Geom(1/2)+1 にシフト
  3. 累積ドリフトの亜拡散は値の縮小だけでは説明不可
  4. 記憶長がm=4,5で急増

本スクリプト:
  A. mod 4 決定論成分を除去した「残差系列」の相関分析
  B. 大きなランダム奇数での連続ステップv2相関の直接計測
  C. 乖離の系統的分解と定量化
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
# A: 残差系列の相関分析
# ============================================================

def residual_correlation_analysis():
    """mod 4 の決定論的成分を除去した残差 R_i = v2_i - E[v2|n_i mod 4]
    n=1 mod 4: E[v2] ~ 2.79, n=3 mod 4: E[v2]=1.0
    残差 R_i の系列相関を測定"""
    print("=" * 70)
    print("A: mod 4 残差系列の相関分析")
    print("=" * 70)

    N_MAX = 200_000
    SEQ_LEN = 30

    # まず条件付き平均を計算
    # n=3 mod 4 → v2=1 (常に)
    # n=1 mod 4 → v2 の分布を計測
    cond_means = {}
    for r4 in [1, 3]:
        vals = []
        for n in range(r4, 100001, 4):
            if n % 2 == 0:
                continue
            vals.append(v2_of_3n1(n))
        cond_means[r4] = mean(vals)
    print(f"  E[v2 | n=1 mod 4] = {cond_means[1]:.6f}")
    print(f"  E[v2 | n=3 mod 4] = {cond_means[3]:.6f}")

    # 残差系列の収集
    residual_sequences = []
    raw_sequences = []
    for n in range(3, N_MAX + 1, 2):
        seq_raw = []
        seq_res = []
        current = n
        for _ in range(SEQ_LEN):
            if current <= 1:
                break
            val = v2_of_3n1(current)
            r4 = current % 4
            residual = val - cond_means[r4]
            seq_raw.append(val)
            seq_res.append(residual)
            current = syracuse(current)
        if len(seq_res) >= SEQ_LEN:
            residual_sequences.append(seq_res)
            raw_sequences.append(seq_raw)

    print(f"  軌道数: {len(residual_sequences)}")

    # 残差の基本統計
    all_res = []
    for seq in residual_sequences:
        all_res.extend(seq)
    print(f"  E[R] = {mean(all_res):.6f} (理想: 0)")
    print(f"  Var[R] = {variance(all_res):.6f}")

    # 残差のACF
    mu_r = mean(all_res)
    var_r = variance(all_res)
    print(f"\n  残差ACF:")
    print(f"  Lag | ACF_raw     | ACF_residual | 差")
    print(f"  " + "-" * 55)

    for lag in range(11):
        # raw ACF
        cov_raw = 0.0
        cnt_raw = 0
        all_raw = []
        for seq in raw_sequences:
            all_raw.extend(seq)
        mu_raw = mean(all_raw)
        var_raw = variance(all_raw)

        for seq in raw_sequences:
            for i in range(len(seq) - lag):
                cov_raw += (seq[i] - mu_raw) * (seq[i+lag] - mu_raw)
                cnt_raw += 1
        acf_raw = (cov_raw / cnt_raw) / var_raw if cnt_raw > 0 and var_raw > 0 else 0

        # residual ACF
        cov_res = 0.0
        cnt_res = 0
        for seq in residual_sequences:
            for i in range(len(seq) - lag):
                cov_res += (seq[i] - mu_r) * (seq[i+lag] - mu_r)
                cnt_res += 1
        acf_res = (cov_res / cnt_res) / var_r if cnt_res > 0 and var_r > 0 else 0

        diff = acf_raw - acf_res
        print(f"  {lag:3d} | {acf_raw:+11.6f} | {acf_res:+12.6f} | {diff:+.6f}")

# ============================================================
# B: 大きなランダム奇数での連続ステップ相関
# ============================================================

def large_random_multistep_correlation():
    """ランダムに選んだ大きな奇数から連続数ステップの v2 列を取り、
    その相関構造を測定 → 軌道の初期値効果を排除"""
    print("\n" + "=" * 70)
    print("B: 大きなランダム奇数での連続ステップ相関")
    print("=" * 70)

    random.seed(12345)
    N_SAMPLES = 200_000
    STEPS = 10

    for bit_size in [40, 50, 60]:
        sequences = []
        for _ in range(N_SAMPLES):
            n = random.getrandbits(bit_size) | 1
            if n < 3:
                n = 3
            seq = []
            current = n
            for _ in range(STEPS):
                if current <= 1:
                    break
                val = v2_of_3n1(current)
                seq.append(val)
                current = syracuse(current)
            if len(seq) >= STEPS:
                sequences.append(seq)

        if not sequences:
            continue

        print(f"\n  {bit_size}-bit 奇数: {len(sequences)} 軌道")

        # 各位置の統計
        all_vals = []
        for seq in sequences:
            all_vals.extend(seq)
        mu = mean(all_vals)
        var_val = variance(all_vals)
        print(f"    E[v2] = {mu:.6f}, Var = {var_val:.6f}")

        # ACF
        print(f"    ACF: ", end="")
        for lag in range(1, 6):
            cov = 0.0
            cnt = 0
            for seq in sequences:
                for i in range(len(seq) - lag):
                    cov += (seq[i] - mu) * (seq[i + lag] - mu)
                    cnt += 1
            acf_l = (cov / cnt) / var_val if cnt > 0 and var_val > 0 else 0
            print(f"lag{lag}={acf_l:+.6f} ", end="")
        print()

        # MI lag=1
        joint = defaultdict(int)
        mx = Counter()
        my = Counter()
        total = 0
        for seq in sequences:
            for i in range(len(seq) - 1):
                x = min(seq[i], 8)
                y = min(seq[i+1], 8)
                joint[(x, y)] += 1
                mx[x] += 1
                my[y] += 1
                total += 1
        mi = 0.0
        for (x, y), c in joint.items():
            pxy = c / total
            px = mx[x] / total
            py = my[y] / total
            if pxy > 0 and px > 0 and py > 0:
                mi += pxy * math.log2(pxy / (px * py))
        print(f"    MI(lag=1) = {mi:.6f} bits")

        # 条件付き: P(v2_{i+1} | v2_i)
        print(f"    E[v2_{{i+1}} | v2_i=k]:", end="")
        for k in range(1, 5):
            cond_vals = [seq[i+1] for seq in sequences for i in range(len(seq)-1) if seq[i] == k]
            if cond_vals:
                print(f" k={k}:{mean(cond_vals):.4f}", end="")
        print()

        # 累積ドリフト分散
        log2_3 = math.log2(3)
        print(f"    累積ドリフト分散成長:")
        single_drifts = [log2_3 - v for v in all_vals]
        sv = variance(single_drifts)
        for k in [1, 3, 5, 8, 10]:
            cums = []
            for seq in sequences:
                if len(seq) >= k:
                    s = sum(log2_3 - seq[i] for i in range(k))
                    cums.append(s)
            if cums:
                cv = variance(cums)
                ratio = cv / (k * sv) if sv > 0 else 0
                print(f"      k={k:2d}: Var/k*Var1 = {ratio:.4f}")

# ============================================================
# C: 乖離の系統的分解
# ============================================================

def systematic_decomposition():
    """Taoモデルからの乖離を系統的に分解:
    全乖離 = (1)周辺分布の乖離 + (2)2点相関 + (3)高次相関"""
    print("\n" + "=" * 70)
    print("C: Taoモデルからの乖離の系統的分解")
    print("=" * 70)

    random.seed(42)
    N_SAMPLES = 300_000
    STEPS = 10
    BIT_SIZE = 50

    # 実データ収集
    real_sequences = []
    for _ in range(N_SAMPLES):
        n = random.getrandbits(BIT_SIZE) | 1
        if n < 3:
            n = 3
        seq = []
        current = n
        for _ in range(STEPS):
            if current <= 1:
                break
            val = v2_of_3n1(current)
            seq.append(val)
            current = syracuse(current)
        if len(seq) >= STEPS:
            real_sequences.append(seq)

    # Taoモデル(iid Geom(1/2))による模擬データ
    geom_sequences = []
    for _ in range(len(real_sequences)):
        seq = []
        for _ in range(STEPS):
            # Geom(1/2): P(k) = 2^{-k}, k=1,2,...
            k = 1
            while random.random() < 0.5 and k < 50:
                k += 1
            seq.append(k)
        geom_sequences.append(seq)

    print(f"  実データ: {len(real_sequences)} 軌道 x {STEPS} ステップ")
    print(f"  モデル: {len(geom_sequences)} 軌道 x {STEPS} ステップ")

    # 比較指標の計算
    log2_3 = math.log2(3)

    for label, seqs in [("実軌道", real_sequences), ("Geom(1/2)モデル", geom_sequences)]:
        all_v = [v for s in seqs for v in s]
        mu = mean(all_v)
        var_v = variance(all_v)

        # ACF
        acf_vals = []
        for lag in range(1, 6):
            cov = 0.0
            cnt = 0
            for seq in seqs:
                for i in range(len(seq) - lag):
                    cov += (seq[i] - mu) * (seq[i + lag] - mu)
                    cnt += 1
            acf_l = (cov / cnt) / var_v if cnt > 0 and var_v > 0 else 0
            acf_vals.append(acf_l)

        # 累積ドリフト
        cum_ratios = []
        sv = variance([log2_3 - v for v in all_v])
        for k in [5, 10]:
            cums = [sum(log2_3 - seq[i] for i in range(k)) for seq in seqs if len(seq) >= k]
            if cums:
                cv = variance(cums)
                cum_ratios.append((k, cv / (k * sv) if sv > 0 else 0))

        # 3点相関
        three_pt = 0.0
        cnt3 = 0
        for seq in seqs:
            for i in range(len(seq) - 2):
                three_pt += (seq[i] - mu) * (seq[i+1] - mu) * (seq[i+2] - mu)
                cnt3 += 1
        three_pt = three_pt / cnt3 if cnt3 > 0 else 0

        print(f"\n  [{label}]")
        print(f"    E[v2] = {mu:.6f}, Var = {var_v:.6f}")
        print(f"    ACF: {' '.join(f'{a:+.6f}' for a in acf_vals)}")
        print(f"    3点相関: {three_pt:.6f}")
        for k, r in cum_ratios:
            print(f"    累積ドリフト Var[S_{k}]/(k*Var1) = {r:.4f}")

    # 差の定量化
    print(f"\n  【乖離の定量化】")
    real_v = [v for s in real_sequences for v in s]
    geom_v = [v for s in geom_sequences for v in s]

    mu_r = mean(real_v)
    mu_g = mean(geom_v)
    var_r = variance(real_v)
    var_g = variance(geom_v)

    print(f"    平均の差: {mu_r - mu_g:+.6f}")
    print(f"    分散の差: {var_r - var_g:+.6f}")

    # 分布のKL
    dist_r = Counter(min(v, 10) for v in real_v)
    dist_g = Counter(min(v, 10) for v in geom_v)
    tot_r = sum(dist_r.values())
    tot_g = sum(dist_g.values())
    kl = 0.0
    for k in range(1, 11):
        pr = dist_r.get(k, 0) / tot_r
        pg = dist_g.get(k, 0) / tot_g
        if pr > 0 and pg > 0:
            kl += pr * math.log(pr / pg)
    print(f"    KL(実測 || Geom) = {kl:.8f} nats")

    # n mod 4 → v2 の完全決定成分の定量化
    # n=3 mod 4 は v2=1 が確定。この「情報量」は?
    # P(n=3 mod 4) ~ 0.5 (奇数中で)
    # この場合 v2 のエントロピーは H = 0 (決定的)
    # n=1 mod 4 の場合 v2 ~ Geom(1/2) + 1
    # → 全体の条件付きエントロピー H(v2|n mod 4) < H(v2|Geom)
    mod4_info = 0.0
    for n_start in random.sample(range(3, 100000, 2), min(50000, 49999)):
        current = n_start
        for _ in range(5):
            if current <= 1:
                break
            r4 = current % 4
            if r4 == 3:
                mod4_info += 1  # v2 = 1 is deterministic, gives 1 bit of info vs Geom
            current = syracuse(current)

    print(f"\n  【mod 4 決定論成分の影響】")
    print(f"    n=3 mod 4 の割合 (軌道中): P ~ {sum(1 for s in real_sequences for i in range(len(s)) if True)}")
    # 再計算
    mod3_count = 0
    total_steps = 0
    for _ in range(min(100000, len(real_sequences))):
        n = random.getrandbits(BIT_SIZE) | 1
        if n < 3:
            n = 3
        current = n
        for _ in range(10):
            if current <= 1:
                break
            if current % 4 == 3:
                mod3_count += 1
            total_steps += 1
            current = syracuse(current)
    p_mod3 = mod3_count / total_steps if total_steps > 0 else 0
    print(f"    軌道中 n=3 mod 4 の割合: {p_mod3:.4f}")
    print(f"    → v2=1 が決定論的に出る確率: {p_mod3:.4f}")
    print(f"    → 全体のエントロピー削減: ~{p_mod3:.4f} * log2(2) = {p_mod3:.4f} bits")

    # n=1 mod 4 の場合の v2-1 の分布
    v2_minus1_vals = []
    for _ in range(200000):
        n = random.getrandbits(BIT_SIZE) | 1
        if n < 3:
            n = 3
        if n % 4 == 1:
            val = v2_of_3n1(n) - 1  # shift by 1
            v2_minus1_vals.append(val)

    if v2_minus1_vals:
        print(f"\n    n=1 mod 4 での v2-1 の分布:")
        dist = Counter(v2_minus1_vals)
        total = len(v2_minus1_vals)
        print(f"      E[v2-1] = {mean(v2_minus1_vals):.6f} (Geom(1/2)なら2.0)")
        for k in range(1, 8):
            p = dist.get(k, 0) / total
            print(f"      P(v2-1={k}) = {p:.5f} (Geom: {0.5**k:.5f})")

# ============================================================
# D: 2-adic valuation のmod構造による連鎖依存性の定量化
# ============================================================

def chain_dependency_analysis():
    """Syracuse(n) の mod 4 クラスが n の mod 8 クラスに依存する
    → v2(3*Syr(n)+1) が v2(3n+1) に依存するチェーン"""
    print("\n" + "=" * 70)
    print("D: mod構造による連鎖依存性")
    print("=" * 70)

    # n mod 2^k → Syr(n) mod 2^k の遷移を計算
    for k in [3, 4, 5]:
        mod = 2 ** k
        print(f"\n  n mod {mod} → Syr(n) mod {mod}:")
        trans = defaultdict(Counter)
        N = 100_000
        for n in range(1, N + 1, 2):
            r_in = n % mod
            r_out = syracuse(n) % mod
            trans[r_in][r_out] += 1

        # 各入力クラスからの出力分布を表示（一部）
        for r_in in sorted(trans.keys())[:8]:
            total = sum(trans[r_in].values())
            top = trans[r_in].most_common(3)
            desc = ", ".join(f"{r}({c/total:.2f})" for r, c in top)
            print(f"    {r_in:3d} → {desc}")

    # v2(3n+1) → v2(3*Syr(n)+1) の遷移を直接計算
    print(f"\n  v2(3n+1) → v2(3*Syr(n)+1) 遷移確率:")
    trans_v2 = defaultdict(Counter)
    N = 300_000
    for n in range(3, N + 1, 2):
        v1 = v2_of_3n1(n)
        s = syracuse(n)
        if s > 1:
            v2_next = v2_of_3n1(s)
            trans_v2[v1][v2_next] += 1

    for v1 in range(1, 7):
        total = sum(trans_v2[v1].values())
        if total > 100:
            probs = {}
            for v2_val in range(1, 8):
                p = trans_v2[v1].get(v2_val, 0) / total
                probs[v2_val] = p
            geom_probs = {k: 0.5**k for k in range(1, 8)}
            kl = sum(probs[k] * math.log(probs[k] / geom_probs[k])
                    for k in range(1, 8) if probs[k] > 0)
            print(f"    v2={v1}: E[v2_next]={sum(k*p for k,p in probs.items()):.4f}, "
                  f"P(1)={probs.get(1,0):.4f}, P(2)={probs.get(2,0):.4f}, "
                  f"P(3)={probs.get(3,0):.4f}, KL={kl:.6f}")

# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 80)
    print("Tao Syracuse RV 相関構造 統合分析")
    print("=" * 80)

    t0 = time.time()

    residual_correlation_analysis()
    large_random_multistep_correlation()
    systematic_decomposition()
    chain_dependency_analysis()

    total_time = time.time() - t0
    print(f"\n{'='*80}")
    print(f"総実行時間: {total_time:.1f}秒")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
