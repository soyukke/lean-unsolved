#!/usr/bin/env python3
"""
コラッツ予想の力学系解析
Syracuse写像 T: odd → odd を力学系として捉え、
圧縮写像性、エントロピー、自己相関、リャプノフ指数、
転送作用素、周期軌道を調べる。
(numpy/scipy不要 - 純粋Python実装)
"""

import math
import random
import time
from collections import Counter, defaultdict

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n >>= 1
        c += 1
    return c

def syracuse(n):
    """Syracuse写像 T: odd -> odd"""
    m = 3 * n + 1
    while m % 2 == 0:
        m >>= 1
    return m

def collatz_orbit_odd(n, max_steps=10000):
    """奇数nから始めて奇数のみの軌道を返す"""
    orbit = [n]
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x = syracuse(x)
        orbit.append(x)
    return orbit

def v2_sequence(n, max_steps=10000):
    """奇数nの軌道でv2(3x+1)の列を返す"""
    seq = []
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        a = v2(3 * x + 1)
        seq.append(a)
        x = (3 * x + 1) >> a
    return seq

def mean(lst):
    return sum(lst) / len(lst) if lst else 0

def stdev(lst):
    if len(lst) < 2:
        return 0
    m = mean(lst)
    return math.sqrt(sum((x - m)**2 for x in lst) / (len(lst) - 1))

def median(lst):
    s = sorted(lst)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2

def percentile(lst, p):
    s = sorted(lst)
    k = (len(s) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)

# ============================================================
# 1. 圧縮写像としての性質
# ============================================================

def analyze_contraction(N=50000):
    print("=" * 70)
    print("1. 圧縮写像としての性質")
    print("   d(x,y) = |log2(x) - log2(y)| に対する Lipschitz定数の推定")
    print("=" * 70)

    odds = list(range(3, 2*N, 2))
    log2_vals = {}
    log2_T_vals = {}

    for n in odds:
        log2_vals[n] = math.log2(n)
        log2_T_vals[n] = math.log2(syracuse(n))

    rng = random.Random(42)
    num_samples = 500_000
    max_ratio = 0.0
    ratios = []

    for _ in range(num_samples):
        a = rng.choice(odds)
        b = rng.choice(odds)
        if a == b:
            continue
        d_input = abs(log2_vals[a] - log2_vals[b])
        d_output = abs(log2_T_vals[a] - log2_T_vals[b])
        if d_input < 1e-15:
            continue
        ratio = d_output / d_input
        ratios.append(ratio)
        if ratio > max_ratio:
            max_ratio = ratio

    print(f"\n  サンプル数: {len(ratios):,}")
    print(f"  Lipschitz定数 (sup ratio): {max_ratio:.6f}")
    print(f"  平均 ratio:                {mean(ratios):.6f}")
    print(f"  中央値 ratio:              {median(ratios):.6f}")
    print(f"  95パーセンタイル:          {percentile(ratios, 95):.6f}")
    print(f"  99パーセンタイル:          {percentile(ratios, 99):.6f}")
    print(f"  99.9パーセンタイル:        {percentile(ratios, 99.9):.6f}")

    if max_ratio < 1.0:
        print("\n  → L < 1: 圧縮写像！ Banach不動点定理により不動点に収束")
    else:
        print(f"\n  → L = {max_ratio:.4f} >= 1: 大域的圧縮写像ではない")
        print("    ただし、「平均的」には圧縮的かもしれない")

    expansion_frac = sum(1 for r in ratios if r > 1.0) / len(ratios)
    print(f"  ratio > 1 の割合: {expansion_frac:.4%}")

    # 分布
    print("\n  ratio の分布:")
    bins = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, float('inf')]
    for i in range(len(bins)-1):
        count = sum(1 for r in ratios if bins[i] <= r < bins[i+1])
        frac = count / len(ratios)
        bar = '#' * int(frac * 60)
        hi = f"{bins[i+1]:5.1f}" if bins[i+1] != float('inf') else "  inf"
        print(f"    [{bins[i]:5.1f}, {hi}): {frac:6.2%} {bar}")

# ============================================================
# 2. 軌道のエントロピー
# ============================================================

def analyze_entropy(N=50000):
    print("\n" + "=" * 70)
    print("2. 軌道のエントロピー（v2列の経験的エントロピー）")
    print("=" * 70)

    global_v2_counts = Counter()
    entropies = []

    for n in range(3, 2*N, 2):
        seq = v2_sequence(n)
        if len(seq) < 5:
            continue

        counts = Counter(seq)
        total = len(seq)
        H = 0
        for c in counts.values():
            p = c / total
            H -= p * math.log2(p)
        entropies.append(H)

        for v in seq:
            global_v2_counts[v] += 1

    total_v2 = sum(global_v2_counts.values())
    print(f"\n  全体のv2分布 (n=3..{2*N-1} の奇数, 計{total_v2:,}個):")

    print(f"  {'v2':>4s}  {'実測頻度':>10s}  {'理論値(1/2^k)':>12s}  {'比率':>8s}")
    for k in sorted(global_v2_counts.keys()):
        if k > 15:
            break
        p_obs = global_v2_counts[k] / total_v2
        p_theory = 1 / (2**k)
        ratio = p_obs / p_theory if p_theory > 0 else 0
        print(f"  {k:4d}  {p_obs:10.6f}  {p_theory:12.6f}  {ratio:8.4f}")

    H_global = 0
    for c in global_v2_counts.values():
        p = c / total_v2
        H_global -= p * math.log2(p)

    H_theory = sum(-(1/2**k) * math.log2(1/2**k) for k in range(1, 30))

    print(f"\n  全体エントロピー H_global: {H_global:.6f} bits")
    print(f"  理論値 (独立幾何分布):     {H_theory:.6f} bits")
    print(f"  差異:                      {H_global - H_theory:.6f} bits")
    print(f"\n  個別軌道エントロピーの統計:")
    print(f"    平均:     {mean(entropies):.4f}")
    print(f"    標準偏差: {stdev(entropies):.4f}")
    print(f"    最小:     {min(entropies):.4f}")
    print(f"    最大:     {max(entropies):.4f}")

# ============================================================
# 3. 自己相関関数
# ============================================================

def analyze_autocorrelation(N=50000, max_lag=20):
    print("\n" + "=" * 70)
    print("3. v2列の自己相関関数")
    print("=" * 70)

    all_sequences = []
    for n in range(3, 2*N, 2):
        seq = v2_sequence(n)
        if len(seq) >= max_lag + 10:
            all_sequences.append(seq)

    print(f"\n  解析対象の軌道数: {len(all_sequences):,} (長さ >= {max_lag+10})")

    mean_autocorr = [0.0] * (max_lag + 1)

    for lag in range(max_lag + 1):
        corrs = []
        for seq in all_sequences:
            n = len(seq)
            if n < lag + 2:
                continue
            x = seq[:n-lag] if lag > 0 else seq
            y = seq[lag:] if lag > 0 else seq
            if len(x) < 2:
                continue
            mx = mean(x)
            my = mean(y)
            sx = stdev(x)
            sy = stdev(y)
            if sx < 1e-15 or sy < 1e-15:
                continue
            cov = sum((x[i] - mx) * (y[i] - my) for i in range(len(x))) / len(x)
            c = cov / (sx * sy)
            corrs.append(c)
        if corrs:
            mean_autocorr[lag] = mean(corrs)

    print(f"\n  {'lag':>4s}  {'C(lag)':>10s}  {'可視化':s}")
    for lag in range(max_lag + 1):
        c = mean_autocorr[lag]
        bar_len = int(abs(c) * 50)
        bar = ('+' if c >= 0 else '-') * bar_len
        print(f"  {lag:4d}  {c:10.6f}  |{bar}")

    n_eff = mean([len(s) for s in all_sequences])
    se = 1.0 / math.sqrt(n_eff)
    print(f"\n  有効標本サイズ (平均軌道長): {n_eff:.0f}")
    print(f"  帰無仮説下の標準誤差 ≈ 1/sqrt(n) ≈ {se:.6f}")

    significant = [lag for lag in range(1, max_lag + 1)
                   if abs(mean_autocorr[lag]) > 2 * se]
    if significant:
        print(f"  2SE以上の有意な自己相関: lag = {significant}")
    else:
        print(f"  有意な自己相関は見つからず（ランダムに近い）")

# ============================================================
# 4. リャプノフ指数
# ============================================================

def analyze_lyapunov(N=50000):
    print("\n" + "=" * 70)
    print("4. リャプノフ指数")
    print("   lambda = (1/n) * sum log2(T(x_i)/x_i)")
    print("   理論的予測: log2(3) - 2 ≈ -0.4150")
    print("=" * 70)

    lyapunov_exponents = []
    deltas_all = []

    for n in range(3, 2*N, 2):
        orbit = collatz_orbit_odd(n)
        if len(orbit) < 3:
            continue

        deltas = []
        for i in range(len(orbit) - 1):
            x = orbit[i]
            tx = orbit[i+1]
            delta = math.log2(tx) - math.log2(x)
            deltas.append(delta)
            deltas_all.append(delta)

        lam = mean(deltas)
        lyapunov_exponents.append((n, lam))

    lams = [l for _, l in lyapunov_exponents]

    theory = math.log2(3) - 2

    print(f"\n  理論予測 (log2(3)-2):     {theory:.6f}")
    print(f"\n  リャプノフ指数の統計 (n=3..{2*N-1} の奇数):")
    print(f"    平均:     {mean(lams):.6f}")
    print(f"    中央値:   {median(lams):.6f}")
    print(f"    標準偏差: {stdev(lams):.6f}")
    print(f"    最小:     {min(lams):.6f}")
    print(f"    最大:     {max(lams):.6f}")

    pos_count = sum(1 for l in lams if l > 0)
    pos_frac = pos_count / len(lams)
    print(f"\n  lambda > 0 の割合: {pos_frac:.4%}")

    if pos_count > 0:
        print(f"  lambda > 0 の軌道数: {pos_count}")
        top5 = sorted(lyapunov_exponents, key=lambda x: -x[1])[:5]
        print(f"  lambda が最大の5つ:")
        for n_val, l_val in top5:
            if l_val > 0:
                print(f"    n={n_val}: lambda={l_val:.6f}")

    print(f"\n  1ステップの delta = log2(T(x)/x) の分布:")
    print(f"    平均:     {mean(deltas_all):.6f}")
    print(f"    中央値:   {median(deltas_all):.6f}")
    print(f"    標準偏差: {stdev(deltas_all):.6f}")

    # deltaのヒストグラム
    print(f"\n  delta の分布:")
    bins = [-12, -10, -8, -6, -4, -2, -1, 0, 0.58, 1, 2, 4]
    counts_hist = [0] * (len(bins) - 1)
    for d in deltas_all:
        for i in range(len(bins) - 1):
            if bins[i] <= d < bins[i+1]:
                counts_hist[i] += 1
                break
    max_count = max(counts_hist) if counts_hist else 1
    for i in range(len(counts_hist)):
        if counts_hist[i] > 0:
            bar = '#' * int(counts_hist[i] / max_count * 40)
            print(f"    [{bins[i]:6.2f}, {bins[i+1]:6.2f}): {counts_hist[i]:8d} {bar}")

# ============================================================
# 5. 転送作用素（簡易版 - べき乗法で最大固有値を推定）
# ============================================================

def analyze_transfer_operator(N_states=2000):
    print("\n" + "=" * 70)
    print(f"5. 転送作用素のスペクトル解析 (状態数={N_states})")
    print(f"   奇数 {{1,3,5,...,{2*N_states-1}}} 上のSyracuse写像の遷移行列")
    print("=" * 70)

    def odd_to_idx(n):
        return (n - 1) // 2

    # 遷移マップを構築（疎表現）
    # T_map[j] = i means column j has a 1 in row i
    T_map = {}
    escapes = 0
    in_degree = Counter()

    for j in range(N_states):
        n = 2 * j + 1
        if n == 1:
            T_map[j] = 0  # 1は不動点
            in_degree[0] += 1
            continue
        tn = syracuse(n)
        idx_tn = odd_to_idx(tn)
        if idx_tn < N_states:
            T_map[j] = idx_tn
            in_degree[idx_tn] += 1
        else:
            escapes += 1

    print(f"\n  脱出する遷移の数: {escapes} / {N_states} ({escapes/N_states:.1%})")

    # べき乗法で最大固有値を推定
    # v_{k+1} = T * v_k / ||T * v_k||
    rng = random.Random(123)
    v = [rng.random() for _ in range(N_states)]
    norm = math.sqrt(sum(x*x for x in v))
    v = [x / norm for x in v]

    eigenvalue_estimates = []
    for iteration in range(200):
        # w = T * v (sparse matrix-vector multiply)
        w = [0.0] * N_states
        for j, i in T_map.items():
            w[i] += v[j]

        # Rayleigh quotient: lambda ≈ v^T * w / v^T * v
        vw = sum(v[i] * w[i] for i in range(N_states))
        vv = sum(v[i] * v[i] for i in range(N_states))
        lam = vw / vv if vv > 0 else 0

        norm = math.sqrt(sum(x*x for x in w))
        if norm > 0:
            v = [x / norm for x in w]

        if iteration >= 150:
            eigenvalue_estimates.append(lam)

    avg_eigenvalue = mean(eigenvalue_estimates)
    print(f"\n  べき乗法による最大固有値推定: {avg_eigenvalue:.6f}")

    # in-degree分布（構造の理解に重要）
    print(f"\n  in-degree分布 (何個の奇数がその奇数に遷移するか):")
    deg_counts = Counter(in_degree.values())
    for deg in sorted(deg_counts.keys())[:15]:
        count = deg_counts[deg]
        print(f"    in-degree {deg:3d}: {count:5d} nodes")

    # 到達不能ノード（in_degree = 0 かつ T_mapにも入っていない）
    reachable = set(in_degree.keys())
    unreachable = N_states - len(reachable)
    print(f"\n  到達不能ノード数: {unreachable} / {N_states}")

    # 1への吸収時間の分布
    absorb_times = []
    for j in range(1, N_states):  # 0 (=n=1) は除く
        n = 2 * j + 1
        x = n
        steps = 0
        while x != 1 and steps < 1000:
            x = syracuse(x)
            steps += 1
        if x == 1:
            absorb_times.append(steps)

    if absorb_times:
        print(f"\n  1への吸収時間 (Syracuse写像のステップ数):")
        print(f"    平均:     {mean(absorb_times):.1f}")
        print(f"    中央値:   {median(absorb_times):.1f}")
        print(f"    最大:     {max(absorb_times)}")

# ============================================================
# 6. 周期軌道の探索
# ============================================================

def search_periodic_orbits(N=500000, max_period=100):
    print("\n" + "=" * 70)
    print(f"6. 周期軌道の探索 (n <= {N}, 周期 <= {max_period})")
    print("   T^k(n) = n となる (n,k) を探索")
    print("=" * 70)

    periodic = []

    for n in range(1, N + 1, 2):
        x = n
        for k in range(1, max_period + 1):
            x = syracuse(x)
            if x == n:
                periodic.append((n, k))
                break
            if x > 10 * N:
                break

    print(f"\n  発見された周期軌道:")
    if periodic:
        for n, k in periodic:
            orbit = [n]
            x = n
            for _ in range(k):
                x = syracuse(x)
                if x != n:
                    orbit.append(x)
            print(f"    n={n}, 周期={k}, 軌道={orbit}")
    else:
        print(f"    なし")

    print(f"\n  n=1 の周期:")
    print(f"    T(1) = syracuse(1) = {syracuse(1)}")
    print(f"    → 1 は不動点 (周期1)")

    non_trivial = [p for p in periodic if p[0] != 1]
    print(f"\n  探索範囲 n=1..{N} (奇数のみ、{N//2}個)")
    print(f"  1以外の周期軌道: {len(non_trivial)}個")

# ============================================================
# 追加: v2遷移確率（マルコフ性の検証）
# ============================================================

def analyze_orbit_statistics(N=50000):
    print("\n" + "=" * 70)
    print("追加解析: v2遷移確率（マルコフ性の検証）")
    print("=" * 70)

    transition_counts = defaultdict(Counter)

    for n in range(3, 2*N, 2):
        seq = v2_sequence(n)
        for i in range(len(seq) - 1):
            transition_counts[seq[i]][seq[i+1]] += 1

    print(f"\n  v2の遷移確率 P(v2_{{i+1}} = j | v2_i = k):")
    print(f"  （理論的に独立なら、各行は同じ分布になるはず）\n")

    max_k = 8
    print(f"  {'k\\j':>4s}", end="")
    for j in range(1, max_k+1):
        print(f"  {j:>6d}", end="")
    print()

    for k in range(1, max_k+1):
        total = sum(transition_counts[k].values())
        if total == 0:
            continue
        print(f"  {k:4d}", end="")
        for j in range(1, max_k+1):
            p = transition_counts[k][j] / total
            print(f"  {p:6.3f}", end="")
        print(f"  (n={total})")

    print(f"\n  独立幾何分布の理論値:")
    print(f"  {'':>4s}", end="")
    for j in range(1, max_k+1):
        p = 1 / (2**j)
        print(f"  {p:6.3f}", end="")
    print()

    # カイ二乗偏差
    print(f"\n  各行の理論値からの偏差 (chi-squared / n):")
    for k in range(1, max_k+1):
        total = sum(transition_counts[k].values())
        if total < 100:
            continue
        chi2 = 0
        for j in range(1, 20):
            obs = transition_counts[k].get(j, 0)
            exp = total / (2**j)
            if exp > 0:
                chi2 += (obs - exp)**2 / exp
        print(f"    k={k}: chi2/n = {chi2/total:.6f} (chi2={chi2:.1f}, n={total})")

# ============================================================
# メイン
# ============================================================

if __name__ == "__main__":
    start = time.time()

    print("=" * 70)
    print("コラッツ予想の力学系解析")
    print(f"解析範囲: 奇数 n = 3, 5, 7, ..., 99999 (50000個)")
    print(f"開始時刻: {time.strftime('%H:%M:%S')}")
    print("=" * 70)

    t0 = time.time()
    analyze_contraction(N=50000)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    analyze_entropy(N=50000)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    analyze_autocorrelation(N=50000, max_lag=20)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    analyze_lyapunov(N=50000)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    analyze_transfer_operator(N_states=2000)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    search_periodic_orbits(N=500000, max_period=100)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    t0 = time.time()
    analyze_orbit_statistics(N=50000)
    print(f"\n  [所要時間: {time.time()-t0:.1f}秒]")

    print("\n" + "=" * 70)
    print(f"全解析完了。総所要時間: {time.time()-start:.1f}秒")
    print("=" * 70)
