#!/usr/bin/env python3
"""
探索: Syracuse軌道と連分数展開の相関の精密分析

n の連分数展開 [a0; a1, a2, ...] の部分商列と Syracuse 軌道の
上昇/下降パターンの相関を定量的に調べる。

仮説: 部分商の算術平均が大きい n ほど stopping time が長い
"""

import math
import statistics
from collections import defaultdict

# =============================================================
# 基本関数
# =============================================================

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^v2(3n+1)"""
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def total_stopping_time(n):
    """1に到達するまでのステップ数（偶数・奇数両方カウント）"""
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def syracuse_stopping_time(n):
    """Syracuse関数でのstopping time（奇数ステップのみカウント）"""
    steps = 0
    while n != 1:
        n = syracuse(n) if n % 2 == 1 else n // 2
        if n % 2 == 1 or n == 1:
            steps += 1
    # 再実装: 標準的なstopping time
    return total_stopping_time(n)

def collatz_orbit_ud(n):
    """軌道のU/Dパターンを返す。U=奇数(上昇), D=偶数(下降)"""
    pattern = []
    while n != 1:
        if n % 2 == 0:
            n //= 2
            pattern.append('D')
        else:
            n = 3 * n + 1
            pattern.append('U')
    return pattern

def continued_fraction(n, d):
    """n/d の連分数展開を返す（有理数）"""
    cf = []
    while d != 0:
        q, r = divmod(n, d)
        cf.append(q)
        n, d = d, r
    return cf

def cf_of_rational(p, q):
    """p/q の連分数展開"""
    return continued_fraction(p, q)

def cf_of_integer_ratio(n):
    """n の「連分数的特徴」- n/1 は自明なので、代わりに n と近傍の2冪の比を使う。
    具体的には n / 2^floor(log2(n)) の連分数展開"""
    if n <= 1:
        return [n]
    k = n.bit_length() - 1  # floor(log2(n))
    power2 = 1 << k
    # n/power2 は [1, ...] の形
    return continued_fraction(n, power2)

def cf_of_odd(n):
    """奇数 n について、n と最近傍の2冪の比率を連分数展開。
    また、3n+1 と 2冪の関係も調べる"""
    k = n.bit_length()
    power2 = 1 << k  # 2^k > n
    # power2/n の連分数展開
    return continued_fraction(power2, n)

def cf_statistics(cf):
    """連分数の部分商の統計量"""
    if len(cf) <= 1:
        return {'mean': cf[0] if cf else 0, 'max': cf[0] if cf else 0,
                'length': len(cf), 'sum': sum(cf), 'geo_mean': cf[0] if cf else 0}
    partial = cf[1:]  # a0を除く（整数部分は除外）
    if not partial:
        return {'mean': 0, 'max': 0, 'length': 0, 'sum': 0, 'geo_mean': 0}
    geo = math.exp(sum(math.log(max(a, 1)) for a in partial) / len(partial))
    return {
        'mean': statistics.mean(partial),
        'max': max(partial),
        'length': len(partial),
        'sum': sum(partial),
        'geo_mean': geo
    }

# =============================================================
# 分析1: n自体の連分数特徴とstopping time
# =============================================================
print("=" * 70)
print("探索: Syracuse軌道と連分数展開の相関の精密分析")
print("=" * 70)

N = 100000
print(f"\n[1] n/2^floor(log2(n)) の連分数展開とstopping timeの相関 (n=3..{N}, 奇数)")

data = []
for n in range(3, N + 1, 2):
    st = total_stopping_time(n)
    cf = cf_of_integer_ratio(n)
    stats = cf_statistics(cf)
    data.append({
        'n': n,
        'st': st,
        'cf_mean': stats['mean'],
        'cf_max': stats['max'],
        'cf_len': stats['length'],
        'cf_sum': stats['sum'],
        'cf_geo': stats['geo_mean'],
    })

# 相関係数の計算
def pearson_corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    sxx = sum((x-mx)**2 for x in xs)
    syy = sum((y-my)**2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0
    return sxy / math.sqrt(sxx * syy)

def spearman_corr(xs, ys):
    """Spearman順位相関"""
    n = len(xs)
    rx = [0] * n
    ry = [0] * n
    sx = sorted(range(n), key=lambda i: xs[i])
    sy = sorted(range(n), key=lambda i: ys[i])
    for rank, idx in enumerate(sx):
        rx[idx] = rank
    for rank, idx in enumerate(sy):
        ry[idx] = rank
    return pearson_corr(rx, ry)

st_list = [d['st'] for d in data]
cf_mean_list = [d['cf_mean'] for d in data]
cf_max_list = [d['cf_max'] for d in data]
cf_len_list = [d['cf_len'] for d in data]
cf_sum_list = [d['cf_sum'] for d in data]
cf_geo_list = [d['cf_geo'] for d in data]
log_n_list = [math.log(d['n']) for d in data]

print(f"\n  Pearson相関係数:")
print(f"    st vs cf_mean:   {pearson_corr(st_list, cf_mean_list):.6f}")
print(f"    st vs cf_max:    {pearson_corr(st_list, cf_max_list):.6f}")
print(f"    st vs cf_len:    {pearson_corr(st_list, cf_len_list):.6f}")
print(f"    st vs cf_sum:    {pearson_corr(st_list, cf_sum_list):.6f}")
print(f"    st vs cf_geo:    {pearson_corr(st_list, cf_geo_list):.6f}")
print(f"    st vs log(n):    {pearson_corr(st_list, log_n_list):.6f}")

print(f"\n  Spearman順位相関:")
print(f"    st vs cf_mean:   {spearman_corr(st_list, cf_mean_list):.6f}")
print(f"    st vs cf_max:    {spearman_corr(st_list, cf_max_list):.6f}")
print(f"    st vs cf_len:    {spearman_corr(st_list, cf_len_list):.6f}")
print(f"    st vs cf_sum:    {spearman_corr(st_list, cf_sum_list):.6f}")
print(f"    st vs cf_geo:    {spearman_corr(st_list, cf_geo_list):.6f}")
print(f"    st vs log(n):    {spearman_corr(st_list, log_n_list):.6f}")

# =============================================================
# 分析2: 2^k/n の連分数展開（nが2冪にどう近いか）
# =============================================================
print(f"\n[2] 2^ceil(log2(n))/n の連分数展開とstopping timeの相関")

data2 = []
for n in range(3, N + 1, 2):
    st = total_stopping_time(n)
    cf = cf_of_odd(n)
    stats = cf_statistics(cf)
    data2.append({
        'n': n,
        'st': st,
        'cf_mean': stats['mean'],
        'cf_max': stats['max'],
        'cf_len': stats['length'],
        'cf_sum': stats['sum'],
        'cf_geo': stats['geo_mean'],
    })

st2 = [d['st'] for d in data2]
cf_mean2 = [d['cf_mean'] for d in data2]
cf_max2 = [d['cf_max'] for d in data2]
cf_len2 = [d['cf_len'] for d in data2]
cf_geo2 = [d['cf_geo'] for d in data2]

print(f"\n  Pearson相関係数:")
print(f"    st vs cf_mean:   {pearson_corr(st2, cf_mean2):.6f}")
print(f"    st vs cf_max:    {pearson_corr(st2, cf_max2):.6f}")
print(f"    st vs cf_len:    {pearson_corr(st2, cf_len2):.6f}")
print(f"    st vs cf_geo:    {pearson_corr(st2, cf_geo2):.6f}")

print(f"\n  Spearman順位相関:")
print(f"    st vs cf_mean:   {spearman_corr(st2, cf_mean2):.6f}")
print(f"    st vs cf_max:    {spearman_corr(st2, cf_max2):.6f}")
print(f"    st vs cf_len:    {spearman_corr(st2, cf_len2):.6f}")
print(f"    st vs cf_geo:    {spearman_corr(st2, cf_geo2):.6f}")

# =============================================================
# 分析3: 3n+1の2進表現と連分数
# =============================================================
print(f"\n[3] (3n+1) の連分数的特徴とv2(3n+1)の関係")

v2_data = []
for n in range(3, min(N + 1, 50001), 2):
    val = 3 * n + 1
    v2 = 0
    temp = val
    while temp % 2 == 0:
        v2 += 1
        temp //= 2
    # val / 2^v2 の連分数展開（奇数部分と2冪の関係）
    odd_part = temp
    if odd_part > 1:
        k = odd_part.bit_length()
        power2 = 1 << k
        cf = continued_fraction(power2, odd_part)
        stats = cf_statistics(cf)
        v2_data.append({
            'n': n, 'v2': v2,
            'cf_mean': stats['mean'],
            'cf_max': stats['max'],
            'odd_part': odd_part
        })

# v2ごとのcf_mean平均
v2_groups = defaultdict(list)
for d in v2_data:
    v2_groups[d['v2']].append(d['cf_mean'])

print(f"  v2(3n+1) ごとの部分商平均の平均:")
for v2 in sorted(v2_groups.keys()):
    vals = v2_groups[v2]
    print(f"    v2={v2}: cf_mean平均={statistics.mean(vals):.4f} (N={len(vals)})")

# =============================================================
# 分析4: U/Dパターンの連続長と連分数部分商の対応
# =============================================================
print(f"\n[4] U/Dパターンのラン長分布と連分数部分商の対比")

def run_length_encoding(pattern):
    """連続同一文字のラン長"""
    if not pattern:
        return []
    runs = []
    current = pattern[0]
    count = 1
    for c in pattern[1:]:
        if c == current:
            count += 1
        else:
            runs.append((current, count))
            current = c
            count = 1
    runs.append((current, count))
    return runs

sample_ns = [27, 703, 871, 6171, 77031, 837799, 8400511]
for n in sample_ns:
    if n > N:
        continue
    pattern = collatz_orbit_ud(n)
    rle = run_length_encoding(pattern)
    d_runs = [length for char, length in rle if char == 'D']
    u_runs = [length for char, length in rle if char == 'U']

    cf = cf_of_integer_ratio(n)

    print(f"\n  n={n}: stopping_time={len(pattern)}")
    print(f"    連分数: {cf[:10]}{'...' if len(cf)>10 else ''}")
    print(f"    Dラン長: 平均={statistics.mean(d_runs):.2f}, 最大={max(d_runs)}, "
          f"全{len(d_runs)}ラン")
    if u_runs:
        print(f"    Uラン長: 平均={statistics.mean(u_runs):.2f}, 最大={max(u_runs)}, "
              f"全{len(u_runs)}ラン")
    print(f"    Dラン長分布: {sorted(d_runs, reverse=True)[:15]}")

# =============================================================
# 分析5: stopping time上位のnの連分数特徴
# =============================================================
print(f"\n[5] stopping time上位100のnの連分数特徴 vs 全体平均")

sorted_data = sorted(data, key=lambda d: -d['st'])
top100 = sorted_data[:100]
bottom100 = sorted_data[-100:]

print(f"  全体平均 (n=3..{N}):")
print(f"    cf_mean: {statistics.mean(cf_mean_list):.4f}")
print(f"    cf_max:  {statistics.mean(cf_max_list):.4f}")
print(f"    cf_geo:  {statistics.mean(cf_geo_list):.4f}")
print(f"    st:      {statistics.mean(st_list):.1f}")

print(f"  上位100 (stopping time大):")
top_cf_mean = [d['cf_mean'] for d in top100]
top_cf_max = [d['cf_max'] for d in top100]
top_cf_geo = [d['cf_geo'] for d in top100]
top_st = [d['st'] for d in top100]
print(f"    cf_mean: {statistics.mean(top_cf_mean):.4f}")
print(f"    cf_max:  {statistics.mean(top_cf_max):.4f}")
print(f"    cf_geo:  {statistics.mean(top_cf_geo):.4f}")
print(f"    st:      {statistics.mean(top_st):.1f}")

print(f"  下位100 (stopping time小):")
bot_cf_mean = [d['cf_mean'] for d in bottom100]
bot_cf_max = [d['cf_max'] for d in bottom100]
bot_cf_geo = [d['cf_geo'] for d in bottom100]
bot_st = [d['st'] for d in bottom100]
print(f"    cf_mean: {statistics.mean(bot_cf_mean):.4f}")
print(f"    cf_max:  {statistics.mean(bot_cf_max):.4f}")
print(f"    cf_geo:  {statistics.mean(bot_cf_geo):.4f}")
print(f"    st:      {statistics.mean(bot_st):.1f}")

# =============================================================
# 分析6: n の2進展開パターンと連分数部分商の関係
# =============================================================
print(f"\n[6] nの2進表現の特徴とstopping timeの相関")

bin_data = []
for n in range(3, N + 1, 2):
    st = total_stopping_time(n)
    b = bin(n)[2:]  # 2進表現
    ones = b.count('1')
    zeros = b.count('0')
    bit_len = len(b)
    density = ones / bit_len  # 1-density

    # 2進表現のラン長
    rle = run_length_encoding(list(b))
    run_lens = [l for _, l in rle]
    max_run = max(run_lens)
    mean_run = statistics.mean(run_lens)

    bin_data.append({
        'n': n, 'st': st,
        'density': density,
        'max_run': max_run,
        'mean_run': mean_run,
        'bit_len': bit_len
    })

st_b = [d['st'] for d in bin_data]
density_b = [d['density'] for d in bin_data]
max_run_b = [d['max_run'] for d in bin_data]
mean_run_b = [d['mean_run'] for d in bin_data]

print(f"  Pearson相関:")
print(f"    st vs 1-density:  {pearson_corr(st_b, density_b):.6f}")
print(f"    st vs max_run:    {pearson_corr(st_b, max_run_b):.6f}")
print(f"    st vs mean_run:   {pearson_corr(st_b, mean_run_b):.6f}")

print(f"  Spearman順位相関:")
print(f"    st vs 1-density:  {spearman_corr(st_b, density_b):.6f}")
print(f"    st vs max_run:    {spearman_corr(st_b, max_run_b):.6f}")
print(f"    st vs mean_run:   {spearman_corr(st_b, mean_run_b):.6f}")

# =============================================================
# 分析7: 残差分析 - log(n)で説明できない部分とcf特徴
# =============================================================
print(f"\n[7] 残差分析: st - α·log(n) の残差と連分数特徴の相関")

# 線形回帰 st = α·log(n) + β
mean_log = statistics.mean(log_n_list)
mean_st = statistics.mean(st_list)
sxy = sum((x - mean_log) * (y - mean_st) for x, y in zip(log_n_list, st_list))
sxx = sum((x - mean_log)**2 for x in log_n_list)
alpha = sxy / sxx
beta = mean_st - alpha * mean_log
print(f"  線形回帰: st ≈ {alpha:.4f}·log(n) + {beta:.4f}")

residuals = [d['st'] - (alpha * math.log(d['n']) + beta) for d in data]

print(f"  残差 vs 連分数特徴のPearson相関:")
print(f"    residual vs cf_mean: {pearson_corr(residuals, cf_mean_list):.6f}")
print(f"    residual vs cf_max:  {pearson_corr(residuals, cf_max_list):.6f}")
print(f"    residual vs cf_geo:  {pearson_corr(residuals, cf_geo_list):.6f}")
print(f"    residual vs cf_len:  {pearson_corr(residuals, cf_len_list):.6f}")

print(f"  残差 vs 2進特徴のPearson相関:")
print(f"    residual vs 1-density:  {pearson_corr(residuals, density_b):.6f}")
print(f"    residual vs max_run:    {pearson_corr(residuals, max_run_b):.6f}")
print(f"    residual vs mean_run:   {pearson_corr(residuals, mean_run_b):.6f}")

# Spearman
print(f"  残差 vs 連分数特徴のSpearman相関:")
print(f"    residual vs cf_mean: {spearman_corr(residuals, cf_mean_list):.6f}")
print(f"    residual vs cf_max:  {spearman_corr(residuals, cf_max_list):.6f}")
print(f"    residual vs cf_geo:  {spearman_corr(residuals, cf_geo_list):.6f}")

print(f"  残差 vs 2進特徴のSpearman相関:")
print(f"    residual vs 1-density:  {spearman_corr(residuals, density_b):.6f}")
print(f"    residual vs max_run:    {spearman_corr(residuals, max_run_b):.6f}")

# =============================================================
# 分析8: 2進ラン長列を「連分数」とみなす解析
# =============================================================
print(f"\n[8] nの2進表現のラン長列を連分数と解釈")
print(f"  n の2進表現 = 1...10...01...1 のラン長列 [r1, r2, ...] を")
print(f"  連分数 [r1; r2, r3, ...] と解釈した値との相関")

bin_cf_data = []
for n in range(3, min(N+1, 50001), 2):
    b = bin(n)[2:]
    rle = run_length_encoding(list(b))
    run_lens = [l for _, l in rle]

    if len(run_lens) >= 2:
        # 連分数 [r1; r2, r3, ...] の値を計算
        # 逆から計算
        val = run_lens[-1]
        for r in reversed(run_lens[:-1]):
            val = r + 1.0 / val if val != 0 else r

        st = total_stopping_time(n)
        bin_cf_data.append({
            'n': n, 'st': st, 'bin_cf_val': val,
            'run_lens': run_lens,
            'n_runs': len(run_lens),
            'run_mean': statistics.mean(run_lens),
        })

st8 = [d['st'] for d in bin_cf_data]
bcv = [d['bin_cf_val'] for d in bin_cf_data]
nruns = [d['n_runs'] for d in bin_cf_data]
rmean = [d['run_mean'] for d in bin_cf_data]

print(f"  Pearson相関:")
print(f"    st vs bin_cf_val:  {pearson_corr(st8, bcv):.6f}")
print(f"    st vs n_runs:      {pearson_corr(st8, nruns):.6f}")
print(f"    st vs run_mean:    {pearson_corr(st8, rmean):.6f}")
print(f"  Spearman相関:")
print(f"    st vs bin_cf_val:  {spearman_corr(st8, bcv):.6f}")
print(f"    st vs n_runs:      {spearman_corr(st8, nruns):.6f}")
print(f"    st vs run_mean:    {spearman_corr(st8, rmean):.6f}")

# =============================================================
# 分析9: Gauss-Kuzminの定理との比較
# =============================================================
print(f"\n[9] Gauss-Kuzmin分布との比較")
print(f"  ランダムな有理数の連分数部分商はGauss-Kuzmin分布に従う:")
print(f"  P(a_k = j) = -log2(1 - 1/(j+1)^2)")

# 理論的なGK分布
print(f"  理論分布:")
for j in range(1, 11):
    p = -math.log2(1 - 1/(j+1)**2)
    print(f"    P(a=  {j}) = {p:.6f}")

# 実際のcf部分商の分布 (n/2^floor(log2(n)))
all_partials = []
for d in data:
    n = d['n']
    cf = cf_of_integer_ratio(n)
    all_partials.extend(cf[1:])  # a0を除く

partial_counts = defaultdict(int)
for a in all_partials:
    partial_counts[a] += 1

total_partials = len(all_partials)
print(f"\n  実測分布 (n/2^floor(log2(n)) の部分商, 全{total_partials}個):")
for j in range(1, 11):
    obs = partial_counts.get(j, 0)
    p_obs = obs / total_partials
    p_gk = -math.log2(1 - 1/(j+1)**2)
    print(f"    P(a={j:2d}) = {p_obs:.6f}  (GK理論値: {p_gk:.6f}, 比: {p_obs/p_gk:.4f})")

# stopping time上位のnの部分商分布
top_partials = []
for d in top100:
    n = d['n']
    cf = cf_of_integer_ratio(n)
    top_partials.extend(cf[1:])

top_partial_counts = defaultdict(int)
for a in top_partials:
    top_partial_counts[a] += 1

total_top = len(top_partials)
if total_top > 0:
    print(f"\n  stopping time上位100の部分商分布 (全{total_top}個):")
    for j in range(1, 11):
        obs = top_partial_counts.get(j, 0)
        p_obs = obs / total_top if total_top > 0 else 0
        p_all = partial_counts.get(j, 0) / total_partials
        print(f"    P(a={j:2d}) = {p_obs:.6f}  (全体: {p_all:.6f})")

# =============================================================
# 分析10: 多重回帰モデル
# =============================================================
print(f"\n[10] stopping timeの多重回帰モデル")
print(f"  st = α·log(n) + β·cf_mean + γ·density + δ")

# 手動最小二乗法（4変数）
# X = [log(n), cf_mean, density, 1]
# XtX の逆行列を計算するのは面倒なので、段階的に

# まず各変数の寄与をみる
# residual from log(n) regression
res_from_logn = residuals  # already computed

# residual from log(n) + density
# density と res_from_logn の回帰
mean_dens = statistics.mean(density_b)
mean_res = statistics.mean(res_from_logn)
sxy_d = sum((x - mean_dens) * (y - mean_res) for x, y in zip(density_b, res_from_logn))
sxx_d = sum((x - mean_dens)**2 for x in density_b)
gamma = sxy_d / sxx_d if sxx_d != 0 else 0
res_from_logn_dens = [r - gamma * (d - mean_dens) for r, d in zip(res_from_logn, density_b)]

print(f"  R² の改善:")
var_st = statistics.variance(st_list)
var_res1 = statistics.variance(res_from_logn)
var_res2 = statistics.variance(res_from_logn_dens)
r2_logn = 1 - var_res1 / var_st
r2_logn_dens = 1 - var_res2 / var_st
print(f"    log(n) のみ:              R² = {r2_logn:.6f}")
print(f"    log(n) + density:         R² = {r2_logn_dens:.6f}")

# + cf_mean
mean_cf = statistics.mean(cf_mean_list)
mean_res2 = statistics.mean(res_from_logn_dens)
sxy_cf = sum((x - mean_cf) * (y - mean_res2) for x, y in zip(cf_mean_list, res_from_logn_dens))
sxx_cf = sum((x - mean_cf)**2 for x in cf_mean_list)
beta_cf = sxy_cf / sxx_cf if sxx_cf != 0 else 0
res_from_all = [r - beta_cf * (c - mean_cf) for r, c in zip(res_from_logn_dens, cf_mean_list)]
var_res3 = statistics.variance(res_from_all)
r2_all = 1 - var_res3 / var_st
print(f"    log(n) + density + cf_mean: R² = {r2_all:.6f}")

# =============================================================
# 分析11: 特殊な数のクラスごとの分析
# =============================================================
print(f"\n[11] 特殊クラスのnの連分数特徴")

classes = {
    '2^a-1 (メルセンヌ型)': [2**a - 1 for a in range(2, 17) if (2**a - 1) % 2 == 1],
    '2^a+1': [2**a + 1 for a in range(1, 17) if (2**a + 1) % 2 == 1],
    '3^a': [3**a for a in range(1, 11)],
    '2^a*3^b-1': [2**a * 3**b - 1 for a in range(1, 14) for b in range(1, 8)
                   if (2**a * 3**b - 1) > 2 and (2**a * 3**b - 1) % 2 == 1 and (2**a * 3**b - 1) < N],
}

for name, nums in classes.items():
    print(f"\n  {name}:")
    cf_means = []
    sts = []
    for n in sorted(nums)[:20]:
        st = total_stopping_time(n)
        cf = cf_of_integer_ratio(n)
        stats = cf_statistics(cf)
        cf_means.append(stats['mean'])
        sts.append(st)
        if len(nums) <= 15:
            print(f"    n={n:8d}: st={st:4d}, cf={cf[:8]}, cf_mean={stats['mean']:.2f}")
    if cf_means:
        print(f"    平均 cf_mean={statistics.mean(cf_means):.2f}, 平均 st={statistics.mean(sts):.1f}")

# =============================================================
# まとめ
# =============================================================
print(f"\n{'='*70}")
print("まとめ")
print(f"{'='*70}")
print(f"  1. n/2^floor(log2(n))の連分数部分商の算術平均とstopping timeの相関は弱い")
print(f"  2. 2進表現の1-densityがstopping timeとより強い相関を示す")
print(f"  3. log(n)が主要な予測因子 (R² = {r2_logn:.4f})")
print(f"  4. 1-densityを加えるとR²が改善: {r2_logn_dens:.4f}")
print(f"  5. 連分数特徴はlog(n)と1-densityで説明できない残差をほとんど説明しない")
print(f"{'='*70}")
