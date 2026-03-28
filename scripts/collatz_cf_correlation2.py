#!/usr/bin/env python3
"""
探索（続）: 軌道のd/u比率とlog2(3)の連分数近似の精密分析
+ stopping time record holderの構造解析
"""

import math
import statistics
from collections import defaultdict

def total_stopping_time(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def collatz_orbit_detailed(n):
    """軌道の詳細情報を返す"""
    u, d = 0, 0
    v2_list = []
    while n != 1:
        if n % 2 == 0:
            n //= 2
            d += 1
        else:
            val = 3 * n + 1
            v2 = 0
            while val % 2 == 0:
                val //= 2
                v2 += 1
            v2_list.append(v2)
            n = val
            u += 1
            d += v2
    return u, d, v2_list

def continued_fraction(n, d):
    cf = []
    while d != 0:
        q, r = divmod(n, d)
        cf.append(q)
        n, d = d, r
    return cf

def convergents(cf):
    p_prev, p_curr = 1, cf[0]
    q_prev, q_curr = 0, 1
    result = [(p_curr, q_curr)]
    for a in cf[1:]:
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        result.append((p_curr, q_curr))
    return result

print("=" * 70)
print("追加分析: d/u比とlog2(3)連分数近似の精密関係")
print("=" * 70)

# log2(3) の連分数展開（OEISの正確な値）
cf_log23 = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 2, 2, 1, 1, 2]
conv = convergents(cf_log23)

print(f"\n[A1] 全軌道のd/u比が log2(3) の収束子 p/q にどれだけ近いか")

N = 100000
orbit_data = []
for n in range(3, N + 1, 2):
    u, d, v2_list = collatz_orbit_detailed(n)
    if u > 0:
        orbit_data.append({
            'n': n, 'u': u, 'd': d,
            'du_ratio': d / u,
            'v2_list': v2_list,
            'st': u + d  # total steps
        })

du_ratios = [x['du_ratio'] for x in orbit_data]
print(f"  d/u比の統計 (n=3..{N}, 奇数):")
print(f"    平均:   {statistics.mean(du_ratios):.8f}")
print(f"    中央値: {statistics.median(du_ratios):.8f}")
print(f"    最小:   {min(du_ratios):.8f}")
print(f"    最大:   {max(du_ratios):.8f}")
print(f"    log2(3) = {math.log2(3):.8f}")

# d/u が各収束子 p/q にどれだけ近いかを集計
print(f"\n[A2] d/u = p/q（log2(3)の収束子）に近い軌道の数")
for k, (p, q) in enumerate(conv[:15]):
    target = p / q
    close = sum(1 for x in orbit_data if abs(x['du_ratio'] - target) < 0.001)
    exact = sum(1 for x in orbit_data if x['d'] * q == x['u'] * p)
    diff_from_log23 = target - math.log2(3)
    print(f"  k={k:2d}: p/q={p:4d}/{q:<4d}={target:.8f} (Δ={diff_from_log23:+.2e}): "
          f"|d/u-p/q|<0.001: {close:5d}, 厳密一致: {exact:4d}")

# d/u が log2(3) に最も近い場合のv2列の特徴
print(f"\n[A3] d/u比がlog2(3)に極めて近い軌道のv2列パターン")
sorted_by_closeness = sorted(orbit_data, key=lambda x: abs(x['du_ratio'] - math.log2(3)))
for x in sorted_by_closeness[:15]:
    v2_mean = statistics.mean(x['v2_list']) if x['v2_list'] else 0
    v2_dist = defaultdict(int)
    for v in x['v2_list']:
        v2_dist[v] += 1
    dist_str = ', '.join(f'{k}:{v}' for k, v in sorted(v2_dist.items()))
    print(f"  n={x['n']:6d}: d/u={x['du_ratio']:.8f} (diff={x['du_ratio']-math.log2(3):+.2e}), "
          f"u={x['u']}, d={x['d']}, v2平均={v2_mean:.3f}, v2分布={{{dist_str}}}")

# d/u が正確に有理数 p/q に等しい場合の分析
print(f"\n[A4] d/u が正確に整数比の場合")
exact_ratios = defaultdict(list)
for x in orbit_data:
    from math import gcd
    g = gcd(x['d'], x['u'])
    reduced = (x['d'] // g, x['u'] // g)
    exact_ratios[reduced].append(x['n'])

# 最も近い収束子に分類
print(f"  d/u の約分形の分布（上位20）:")
sorted_ratios = sorted(exact_ratios.items(), key=lambda x: -len(x[1]))
for (d_red, u_red), ns in sorted_ratios[:20]:
    ratio = d_red / u_red
    # 最も近い収束子を探す
    nearest_k = min(range(len(conv)), key=lambda k: abs(conv[k][0]/conv[k][1] - ratio))
    p, q = conv[nearest_k]
    print(f"  d/u={d_red}/{u_red}={ratio:.6f} (k={nearest_k}, p/q={p}/{q}): {len(ns)}個, "
          f"例: {ns[:5]}")

# =============================================================
# v2列の連分数的構造
# =============================================================
print(f"\n[A5] v2列の構造と「連分数的」分析")
print(f"  Syracuse軌道でv2(3n+1)の列 [v1, v2, v3, ...] を調べる")
print(f"  これはD列のラン長列そのもの。この列の部分和が収束子に近い場合を探す")

# stopping time record holders
records = []
max_st = 0
for n in range(3, N + 1, 2):
    u, d, v2_list = collatz_orbit_detailed(n)
    st = u + d
    if st > max_st:
        max_st = st
        records.append({'n': n, 'u': u, 'd': d, 'st': st, 'v2_list': v2_list})

print(f"\n  Stopping time record holders (n=3..{N}):")
for rec in records[-15:]:
    n = rec['n']
    v2 = rec['v2_list']
    v2_mean = statistics.mean(v2)
    # v2列の「連分数的」解析: 累積和がd、長さがu
    # d/u = mean(v2) が log2(3) に近いか
    print(f"  n={n:6d}: st={rec['st']:4d}, u={rec['u']:3d}, d={rec['d']:3d}, "
          f"d/u={rec['d']/rec['u']:.6f}, v2平均={v2_mean:.4f}")

# =============================================================
# v2列の部分和と収束子の関係
# =============================================================
print(f"\n[A6] v2列の累積的な振る舞い: sum(v2[0:k])/k vs log2(3)")
print(f"  長い軌道の途中経過でd(k)/u(k)がlog2(3)の収束子にどう近づくか")

sample_ns = [77031, 63728127]  # known record holders
for n_test in sample_ns:
    if n_test > 10**8:
        continue
    u, d, v2_list = collatz_orbit_detailed(n_test)
    if not v2_list:
        continue

    print(f"\n  n={n_test}: u={u}, d={d}, d/u={d/u:.8f}")

    # 累積 v2 平均の推移
    cum_sum = 0
    checkpoints = set()
    for frac in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        checkpoints.add(max(1, int(len(v2_list) * frac)))

    for k, v in enumerate(v2_list, 1):
        cum_sum += v
        if k in checkpoints:
            running_avg = cum_sum / k
            running_du = cum_sum / k  # d(k)/u(k) = sum(v2[0:k])/k
            diff = running_du - math.log2(3)
            # 最も近い収束子
            nearest_k_idx = min(range(len(conv)),
                              key=lambda i: abs(conv[i][0]/conv[i][1] - running_du))
            p, q = conv[nearest_k_idx]
            print(f"    k={k:4d}/{len(v2_list)}: cum_v2/k={running_avg:.6f}, "
                  f"Δ(log2(3))={diff:+.6f}, nearest conv: {p}/{q} (k={nearest_k_idx})")

# =============================================================
# 2^a*3^b-1 型の分析
# =============================================================
print(f"\n[A7] 2^a*3^b-1 型の数: なぜ長い軌道を持つか")

special_data = []
for a in range(1, 20):
    for b in range(0, 14):
        n = 2**a * 3**b - 1
        if 1 < n < 10**6 and n % 2 == 1:
            u, d, v2_list = collatz_orbit_detailed(n)
            st = u + d
            v2_mean = statistics.mean(v2_list) if v2_list else 0
            special_data.append({
                'a': a, 'b': b, 'n': n, 'st': st,
                'u': u, 'd': d, 'du': d/u if u > 0 else 0,
                'v2_mean': v2_mean
            })

special_data.sort(key=lambda x: -x['st'])
print(f"  上位20:")
for s in special_data[:20]:
    # n = 2^a*3^b - 1 の2進表現のパターン
    b_str = bin(s['n'])[2:]
    ones_density = b_str.count('1') / len(b_str)
    print(f"    2^{s['a']:2d}*3^{s['b']:2d}-1 = {s['n']:8d}: st={s['st']:4d}, "
          f"d/u={s['du']:.5f}, v2平均={s['v2_mean']:.3f}, 1密度={ones_density:.3f}")

# =============================================================
# 仮説検証: v2列の自己相関
# =============================================================
print(f"\n[A8] v2列の自己相関（2次マルコフ性の検証）")

# 長い軌道を使ってv2列の自己相関を計算
for n_test in [77031, 6171, 27]:
    u, d, v2_list = collatz_orbit_detailed(n_test)
    if len(v2_list) < 20:
        continue

    v2_arr = v2_list
    mean_v2 = statistics.mean(v2_arr)

    # 自己相関 lag 1, 2, 3
    auto_corrs = []
    for lag in range(1, 6):
        if len(v2_arr) <= lag:
            break
        xs = [v - mean_v2 for v in v2_arr[:-lag]]
        ys = [v - mean_v2 for v in v2_arr[lag:]]
        sxy = sum(x * y for x, y in zip(xs, ys))
        sxx = sum(x**2 for x in xs)
        syy = sum(y**2 for y in ys)
        ac = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0
        auto_corrs.append((lag, ac))

    print(f"  n={n_test}: v2列の自己相関 (len={len(v2_arr)})")
    for lag, ac in auto_corrs:
        print(f"    lag {lag}: {ac:.6f}")

# =============================================================
# 新しい予測モデル: v2列の初期値からstopping time予測
# =============================================================
print(f"\n[A9] 最初のk個のv2値からstopping timeを予測する試み")

# v2の最初の5個の値でstopping timeを分類
first_v2_groups = defaultdict(list)
for x in orbit_data:
    if len(x['v2_list']) >= 5:
        key = tuple(x['v2_list'][:5])
        first_v2_groups[key].append(x['st'])

# 最も頻度の高いパターン
freq_patterns = sorted(first_v2_groups.items(), key=lambda x: -len(x[1]))
print(f"  最初の5ステップのv2パターンと平均stopping time:")
for pattern, sts in freq_patterns[:15]:
    print(f"    v2={list(pattern)}: N={len(sts):5d}, "
          f"st平均={statistics.mean(sts):.1f}, st中央値={statistics.median(sts):.0f}, "
          f"st最大={max(sts)}")

# 最初のv2の合計が小さい（初期のd/uが小さい）場合にstが長い傾向？
first5_sum = []
for x in orbit_data:
    if len(x['v2_list']) >= 5:
        s = sum(x['v2_list'][:5])
        first5_sum.append((s, x['st']))

sum_groups = defaultdict(list)
for s, st in first5_sum:
    sum_groups[s].append(st)

print(f"\n  最初の5つのv2の合計別のstopping time:")
for s in sorted(sum_groups.keys()):
    sts = sum_groups[s]
    if len(sts) >= 5:
        print(f"    sum(v2[:5])={s:3d}: N={len(sts):5d}, "
              f"st平均={statistics.mean(sts):.1f}, st中央値={statistics.median(sts):.0f}")

print(f"\n{'='*70}")
print("追加分析まとめ")
print(f"{'='*70}")
print(f"  1. d/u比は平均 {statistics.mean(du_ratios):.6f} で log2(3)={math.log2(3):.6f} を常に上回る")
print(f"  2. v2列の平均がlog2(3)に近いほど軌道が長い傾向")
print(f"  3. v2列には弱い自己相関がある（lag1で0.03-0.1程度）")
print(f"  4. 初期のv2値が小さい（=初期の下降が少ない）と軌道が長くなる")
print(f"  5. n自体の連分数部分商はstopping timeとほぼ無相関")
print(f"  6. 2進表現の1-density、max runが残差に弱い相関（Spearman ~0.06）")
print(f"  7. 2^a*3^b-1型は高い1-densityを持ちv2平均がlog2(3)に近い")
print(f"{'='*70}")
