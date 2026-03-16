#!/usr/bin/env python3
"""
コラッツ予想 探索19: 対数的ポテンシャル関数の探索

一般公式 2^k * T^k(n) + 2^k = 3^k * (n+1) から:
  T^k(n) = 3^k/2^k * (n+1) - 1
k回連続上昇すると (3/2)^k 倍に増大。下降で v2>=2 なので ÷4以上。
「上昇と下降の対数的バランス」を可視化して新しい不変量を探す。
"""

import math
import statistics
from collections import Counter, defaultdict
import struct

# ── ユーティリティ ──────────────────────────────────────────

def v2(n):
    """n の 2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse写像 T(n) = (3n+1) / 2^{v2(3n+1)}  (n: 奇数)"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_trajectory(n, max_steps=10000):
    """奇数 n の Syracuse 軌道 (奇数列)"""
    traj = [n]
    cur = n
    for _ in range(max_steps):
        cur = syracuse(cur)
        traj.append(cur)
        if cur == 1:
            break
    return traj

def trailing_ones(n):
    """n の2進表現の末尾連続1ビット数"""
    c = 0
    while n & 1:
        n >>= 1
        c += 1
    return c

# ══════════════════════════════════════════════════════════════
# 1. 対数的ポテンシャルとデルタの分布
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("1. 対数的ポテンシャル delta = log2(T(n)) - log2(n) の分布")
print("=" * 70)

N_MAX = 100000
deltas = []
v2_values = []
delta_by_v2 = defaultdict(list)

for n in range(1, N_MAX + 1, 2):  # 奇数のみ
    tn = syracuse(n)
    delta = math.log2(tn) - math.log2(n)
    v = v2(3 * n + 1)
    deltas.append(delta)
    v2_values.append(v)
    delta_by_v2[v].append(delta)

print(f"奇数 n = 1..{N_MAX} に対する delta の統計:")
print(f"  サンプル数: {len(deltas)}")
print(f"  平均: {statistics.mean(deltas):.6f}")
print(f"  中央値: {statistics.median(deltas):.6f}")
print(f"  標準偏差: {statistics.stdev(deltas):.6f}")
print(f"  最小値: {min(deltas):.6f}")
print(f"  最大値: {max(deltas):.6f}")
print()

# v2 ごとの分布
print("v2(3n+1) ごとの delta 分布:")
print(f"  {'v2':>4} | {'count':>7} | {'ratio':>8} | {'mean delta':>12} | {'理論値 log2(3)-v':>18}")
print("  " + "-" * 60)
for v in sorted(delta_by_v2.keys()):
    vals = delta_by_v2[v]
    theory = math.log2(3) - v
    ratio = len(vals) / len(deltas)
    print(f"  {v:4d} | {len(vals):7d} | {ratio:8.5f} | {statistics.mean(vals):12.6f} | {theory:18.6f}")
print()

# v2 の実測分布と理論分布 (1/2^v) の比較
print("v2 の分布: 実測 vs 理論 (P(v2=v) = 1/2^v):")
for v in sorted(delta_by_v2.keys()):
    observed = len(delta_by_v2[v]) / len(deltas)
    theoretical = 1 / (2 ** v)
    print(f"  v2={v}: 実測={observed:.5f}, 理論={theoretical:.5f}, 比={observed/theoretical:.4f}")

# ══════════════════════════════════════════════════════════════
# 2. 累積ポテンシャルの軌道
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("2. 累積ポテンシャル S_t(n) = log2(T^t(n)) - log2(n) の軌道")
print("=" * 70)

test_values = [27, 703, 871, 6171, 77031, 837799]

trajectory_data = {}  # SVG用に保存

for n in test_values:
    traj = syracuse_trajectory(n, max_steps=2000)
    steps = len(traj) - 1
    # 累積ポテンシャル
    log_n = math.log2(n)
    S = [math.log2(traj[t]) - log_n for t in range(len(traj))]

    trajectory_data[n] = S

    # 統計
    max_S = max(S)
    min_S = min(S)
    max_pos = S.index(max_S)

    print(f"\nn = {n}:")
    print(f"  停止ステップ数: {steps}")
    print(f"  S の最大値: {max_S:.4f} (ステップ {max_pos})")
    print(f"  S の最小値: {min_S:.4f}")
    print(f"  最終値 S_end = log2(1) - log2({n}) = {S[-1]:.4f}")
    print(f"  平均ステップあたり変化: {S[-1]/steps:.4f}")

# ══════════════════════════════════════════════════════════════
# 3. ドリフトの理論値と実測値の比較
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("3. ドリフトの理論値と実測値")
print("=" * 70)

# 理論値
# E[delta] = sum_{v=1}^inf P(v2=v) * (log2(3) - v)
#           = sum_{v=1}^inf (1/2^v) * (log2(3) - v)
#           = log2(3) * 1 - 2
#           = log2(3) - 2
drift_theory = math.log2(3) - 2
print(f"理論的ドリフト E[delta] = log2(3) - 2 = {drift_theory:.6f}")
print()

# 実測値（1ステップ）
drift_measured = statistics.mean(deltas)
print(f"実測ドリフト (1ステップ平均, n=1..{N_MAX} 奇数): {drift_measured:.6f}")
print(f"差: {abs(drift_measured - drift_theory):.6f}")
print()

# 軌道ベースの実測
print("軌道ベースのドリフト実測:")
all_traj_deltas = []
for n in range(1, 10001, 2):
    traj = syracuse_trajectory(n, max_steps=2000)
    for i in range(len(traj) - 1):
        d = math.log2(traj[i+1]) - math.log2(traj[i])
        all_traj_deltas.append(d)

traj_drift = statistics.mean(all_traj_deltas)
print(f"  軌道内 delta の平均 (n=1..10000 奇数): {traj_drift:.6f}")
print(f"  理論値との差: {abs(traj_drift - drift_theory):.6f}")

# 理論導出の詳細
print()
print("【理論導出の詳細】")
print("  E[delta] = Σ_{v=1}^∞ (1/2^v) * (log₂3 - v)")
print(f"           = log₂3 * Σ(1/2^v) - Σ(v/2^v)")
print(f"           = log₂3 * 1 - 2")
print(f"           = {math.log2(3):.6f} - 2")
print(f"           = {drift_theory:.6f}")
print()
print("  ※ Σ_{v=1}^∞ 1/2^v = 1 (等比級数)")
print("  ※ Σ_{v=1}^∞ v/2^v = 2 (べき級数の微分)")

# ══════════════════════════════════════════════════════════════
# 4. 分散の理論値と実測値
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("4. 分散の理論値と実測値")
print("=" * 70)

# E[delta^2] = sum_{v=1}^inf (1/2^v) * (log2(3) - v)^2
E_delta2 = 0
for v in range(1, 100):
    E_delta2 += (1 / 2**v) * (math.log2(3) - v)**2

var_theory = E_delta2 - drift_theory**2
std_theory = math.sqrt(var_theory)

var_measured = statistics.variance(deltas)
std_measured = statistics.stdev(deltas)

var_traj = statistics.variance(all_traj_deltas)
std_traj = statistics.stdev(all_traj_deltas)

print(f"理論値:")
print(f"  E[delta^2] = {E_delta2:.6f}")
print(f"  Var[delta] = E[delta^2] - E[delta]^2 = {var_theory:.6f}")
print(f"  Std[delta] = {std_theory:.6f}")
print()
print(f"実測値 (1ステップ, n=1..{N_MAX}):")
print(f"  Var[delta] = {var_measured:.6f}")
print(f"  Std[delta] = {std_measured:.6f}")
print()
print(f"実測値 (軌道内, n=1..10000):")
print(f"  Var[delta] = {var_traj:.6f}")
print(f"  Std[delta] = {std_traj:.6f}")
print()

# E[delta^2] の理論導出
print("【分散の理論導出】")
print("  E[(log₂3 - v)²] = Σ_{v=1}^∞ (1/2^v)(log₂3 - v)²")
print(f"                   = {E_delta2:.6f}")
print(f"  Var = {E_delta2:.6f} - ({drift_theory:.6f})² = {var_theory:.6f}")

# ══════════════════════════════════════════════════════════════
# 5. 停止時間の予測
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("5. 停止時間の予測 vs 実測")
print("=" * 70)

# 理論予測: E[stopping time] ≈ log2(n) / |drift| = log2(n) / 0.415
abs_drift = abs(drift_theory)
print(f"理論予測: E[停止時間] ≈ log₂(n) / |ドリフト| = log₂(n) / {abs_drift:.4f} ≈ {1/abs_drift:.4f} * log₂(n)")
print()

# 実測
stopping_times = {}
for n in range(1, 100001, 2):
    traj = syracuse_trajectory(n, max_steps=5000)
    stopping_times[n] = len(traj) - 1

# log2(n) vs stopping time の比較
print(f"{'n':>8} | {'log₂(n)':>8} | {'予測':>8} | {'実測':>8} | {'比率':>8}")
print("-" * 55)
for n in [3, 7, 27, 255, 703, 871, 6171, 27003, 77031, 99999]:
    log_n = math.log2(n)
    predicted = log_n / abs_drift
    actual = stopping_times.get(n, "N/A")
    if isinstance(actual, int) and actual > 0:
        ratio = actual / predicted
        print(f"{n:8d} | {log_n:8.2f} | {predicted:8.1f} | {actual:8d} | {ratio:8.3f}")

print()

# 停止時間 / log2(n) の分布
ratios = []
for n in range(3, 100001, 2):
    st = stopping_times[n]
    log_n = math.log2(n)
    ratios.append(st / log_n)

print("停止時間 / log₂(n) の統計:")
print(f"  平均: {statistics.mean(ratios):.4f}  (理論予測: {1/abs_drift:.4f})")
print(f"  中央値: {statistics.median(ratios):.4f}")
print(f"  標準偏差: {statistics.stdev(ratios):.4f}")
print(f"  最小値: {min(ratios):.4f}")
print(f"  最大値: {max(ratios):.4f}")

# ══════════════════════════════════════════════════════════════
# 6. 異常値の検出
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("6. 異常値の検出: 停止時間 > 4 * log₂(n) の n")
print("=" * 70)

threshold_factor = 4.0
anomalies = []
for n in range(3, 100001, 2):
    st = stopping_times[n]
    log_n = math.log2(n)
    if st > threshold_factor * log_n:
        anomalies.append((n, st, st / log_n))

anomalies.sort(key=lambda x: -x[2])

print(f"閾値: 停止時間 > {threshold_factor} * log₂(n)")
print(f"異常値の数: {len(anomalies)} / {len(stopping_times)} ({100*len(anomalies)/len(stopping_times):.2f}%)")
print()

print("上位20件:")
print(f"{'n':>8} | {'停止時間':>8} | {'log₂(n)':>8} | {'比率':>8} | {'n mod 8':>8} | {'末尾1':>6} | {'2進表現'}")
print("-" * 85)
for n, st, ratio in anomalies[:20]:
    t1 = trailing_ones(n)
    bin_rep = bin(n)[2:]
    if len(bin_rep) > 20:
        bin_rep = bin_rep[:10] + "..." + bin_rep[-10:]
    print(f"{n:8d} | {st:8d} | {math.log2(n):8.2f} | {ratio:8.3f} | {n%8:8d} | {t1:6d} | {bin_rep}")

# mod パターン分析
print()
print("異常値の mod パターン分析:")
for mod in [4, 8, 16, 32]:
    counts = Counter()
    for n, _, _ in anomalies:
        counts[n % mod] += 1
    total = len(anomalies)
    print(f"\n  mod {mod}:")
    for r in sorted(counts.keys()):
        pct = 100 * counts[r] / total
        expected = 100 / (mod // 2)  # 奇数のみなので
        bar = "#" * int(pct)
        print(f"    {r:3d}: {counts[r]:5d} ({pct:5.1f}%, 期待{expected:.1f}%) {bar}")

# 2進表現の 1-bit 密度
print()
print("異常値 vs 全体の 1-bit 密度:")
anom_density = []
for n, _, _ in anomalies:
    b = bin(n)[2:]
    anom_density.append(b.count('1') / len(b))
all_density = []
for n in range(3, 100001, 2):
    b = bin(n)[2:]
    all_density.append(b.count('1') / len(b))
print(f"  異常値の平均 1-bit 密度: {statistics.mean(anom_density):.4f}")
print(f"  全体の平均 1-bit 密度: {statistics.mean(all_density):.4f}")

# 末尾1ビット数
print()
print("異常値 vs 全体の末尾連続1ビット数:")
anom_t1 = [trailing_ones(n) for n, _, _ in anomalies]
all_t1 = [trailing_ones(n) for n in range(3, 100001, 2)]
print(f"  異常値の平均末尾1ビット数: {statistics.mean(anom_t1):.4f}")
print(f"  全体の平均末尾1ビット数: {statistics.mean(all_t1):.4f}")
t1_counts = Counter(anom_t1)
print(f"  異常値の末尾1ビット分布: {dict(sorted(t1_counts.items()))}")

# ══════════════════════════════════════════════════════════════
# 7. 新しいポテンシャル関数の探索
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("7. 新しいポテンシャル関数の探索")
print("=" * 70)

def evaluate_potential(phi_func, phi_name, n_range=range(3, 50001, 2), max_steps=1000):
    """ポテンシャル関数の「単調性」を評価"""
    total_steps = 0
    increasing_steps = 0  # phi が増加するステップ数
    max_increase = 0  # 最大の増加量
    longest_decrease_streak = 0  # 最長の連続減少ステップ

    for n in n_range:
        traj = syracuse_trajectory(n, max_steps=max_steps)
        if len(traj) < 2:
            continue
        streak = 0
        for i in range(len(traj) - 1):
            total_steps += 1
            d = phi_func(traj[i+1]) - phi_func(traj[i])
            if d > 0:
                increasing_steps += 1
                max_increase = max(max_increase, d)
                streak = 0
            else:
                streak += 1
                longest_decrease_streak = max(longest_decrease_streak, streak)

    monotone_ratio = 1 - increasing_steps / total_steps if total_steps > 0 else 0
    return {
        'name': phi_name,
        'total_steps': total_steps,
        'increasing_steps': increasing_steps,
        'monotone_ratio': monotone_ratio,
        'max_increase': max_increase,
        'longest_decrease_streak': longest_decrease_streak,
    }

# ポテンシャル関数の定義
potentials = [
    (lambda n: math.log2(n), "log₂(n)"),
    (lambda n: math.log2(n) + 0.3 * trailing_ones(n), "log₂(n) + 0.3 * trailing_1s"),
    (lambda n: math.log2(n) + 0.5 * trailing_ones(n), "log₂(n) + 0.5 * trailing_1s"),
    (lambda n: math.log2(n) + 1.0 * trailing_ones(n), "log₂(n) + 1.0 * trailing_1s"),
    (lambda n: math.log2(n) / math.log2(3), "log₃(n) (3-adic的)"),
    (lambda n: n ** 0.1, "n^0.1"),
    (lambda n: n ** 0.01, "n^0.01"),
    (lambda n: math.log2(n) + 0.5 * math.log2(n % 8 + 1), "log₂(n) + 0.5*log₂(n%8+1)"),
    (lambda n: math.log2(n) * (1 + 0.1 * trailing_ones(n)), "log₂(n) * (1 + 0.1*trailing_1s)"),
    (lambda n: math.log2(n) + 0.585 * trailing_ones(n), "log₂(n) + log₂(3/2)*trailing_1s"),
]

print()
print(f"{'ポテンシャル関数':<38} | {'減少率':>8} | {'増加ステップ':>12} | {'最大増加':>10} | {'最長連続減少':>12}")
print("-" * 100)

results = []
test_range = range(3, 20001, 2)

for phi_func, phi_name in potentials:
    res = evaluate_potential(phi_func, phi_name, n_range=test_range)
    results.append(res)
    print(f"{res['name']:<38} | {res['monotone_ratio']:8.4f} | {res['increasing_steps']:12d} | {res['max_increase']:10.4f} | {res['longest_decrease_streak']:12d}")

# ベスト結果
print()
best = max(results, key=lambda r: r['monotone_ratio'])
print(f"最も単調に近いポテンシャル: {best['name']}")
print(f"  減少率: {best['monotone_ratio']:.4f} ({best['monotone_ratio']*100:.2f}%)")
print(f"  増加ステップ: {best['increasing_steps']} / {best['total_steps']}")

# ══════════════════════════════════════════════════════════════
# 8. 追加解析: 連続上昇回数と delta の関係
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("8. 追加解析: 連続上昇と下降のパターン")
print("=" * 70)

# 連続上昇(delta>0)の後の下降(delta<0)のサイズ
ascent_then_descent = defaultdict(list)
for n in range(3, 50001, 2):
    traj = syracuse_trajectory(n, max_steps=1000)
    ascent_count = 0
    for i in range(len(traj) - 1):
        d = math.log2(traj[i+1]) - math.log2(traj[i])
        if d > 0:
            ascent_count += 1
        else:
            if ascent_count > 0:
                ascent_then_descent[ascent_count].append(d)
            ascent_count = 0

print("連続上昇 k 回後の下降 delta の平均:")
print(f"  {'k':>4} | {'count':>8} | {'mean descent':>14} | {'理論: log₂3-k-next_v2':>22}")
print("  " + "-" * 55)
for k in sorted(ascent_then_descent.keys()):
    if k > 10:
        break
    vals = ascent_then_descent[k]
    # k回上昇 = v2が k回1だった → 累積 +k*log2(3)-k
    # 次の下降で v2>=2 → -log2(3)+v2 程度
    print(f"  {k:4d} | {len(vals):8d} | {statistics.mean(vals):14.4f} |")

# 累積で見る: k回上昇の累積 vs 次の1回下降
print()
print("k回上昇の累積ポテンシャル変化:")
for k in range(1, 8):
    cumulative_up = k * (math.log2(3) - 1)  # 各ステップで v2=1
    print(f"  k={k}: 累積上昇 = {cumulative_up:.4f}, log₂((3/2)^k) = {k*math.log2(1.5):.4f}")
    if k in ascent_then_descent:
        mean_down = statistics.mean(ascent_then_descent[k])
        net = cumulative_up + mean_down
        print(f"        平均下降 = {mean_down:.4f}, 純変化 = {net:.4f}")

# ══════════════════════════════════════════════════════════════
# SVG出力
# ══════════════════════════════════════════════════════════════

def create_trajectory_svg(trajectory_data, filename):
    """累積ポテンシャル軌道のSVGプロット"""
    width, height = 1000, 600
    margin = {'top': 40, 'right': 150, 'bottom': 50, 'left': 70}
    pw = width - margin['left'] - margin['right']
    ph = height - margin['top'] - margin['bottom']

    # データ範囲
    max_steps = max(len(s) for s in trajectory_data.values())
    all_vals = [v for s in trajectory_data.values() for v in s]
    y_min, y_max = min(all_vals), max(all_vals)
    y_pad = (y_max - y_min) * 0.05
    y_min -= y_pad
    y_max += y_pad

    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628']

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">']
    svg.append(f'<rect width="{width}" height="{height}" fill="white"/>')
    svg.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">'
               f'累積ポテンシャル S_t = log₂(T^t(n)) - log₂(n)</text>')

    # 軸
    svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" stroke="black" stroke-width="1"/>')
    svg.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="black" stroke-width="1"/>')

    # y=0 の線
    if y_min < 0 < y_max:
        y0 = margin['top'] + ph * (1 - (0 - y_min) / (y_max - y_min))
        svg.append(f'<line x1="{margin["left"]}" y1="{y0:.1f}" x2="{width-margin["right"]}" y2="{y0:.1f}" stroke="gray" stroke-width="0.5" stroke-dasharray="4,4"/>')
        svg.append(f'<text x="{margin["left"]-5}" y="{y0:.1f}" text-anchor="end" font-size="10" dominant-baseline="middle">0</text>')

    # Y軸ラベル
    n_yticks = 6
    for i in range(n_yticks + 1):
        val = y_min + (y_max - y_min) * i / n_yticks
        y = margin['top'] + ph * (1 - i / n_yticks)
        svg.append(f'<text x="{margin["left"]-5}" y="{y:.1f}" text-anchor="end" font-size="10" dominant-baseline="middle">{val:.1f}</text>')
        svg.append(f'<line x1="{margin["left"]}" y1="{y:.1f}" x2="{margin["left"]+3}" y2="{y:.1f}" stroke="black"/>')

    # X軸ラベル
    n_xticks = 5
    for i in range(n_xticks + 1):
        val = int(max_steps * i / n_xticks)
        x = margin['left'] + pw * i / n_xticks
        svg.append(f'<text x="{x:.1f}" y="{height-margin["bottom"]+15}" text-anchor="middle" font-size="10">{val}</text>')

    svg.append(f'<text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="12">ステップ数</text>')
    svg.append(f'<text x="15" y="{height//2}" text-anchor="middle" font-size="12" transform="rotate(-90,15,{height//2})">S_t</text>')

    # 軌道のプロット
    for idx, (n, S) in enumerate(trajectory_data.items()):
        color = colors[idx % len(colors)]
        points = []
        # 間引き
        step = max(1, len(S) // 500)
        for t in range(0, len(S), step):
            x = margin['left'] + pw * t / max_steps
            y = margin['top'] + ph * (1 - (S[t] - y_min) / (y_max - y_min))
            points.append(f"{x:.1f},{y:.1f}")
        # 最後の点も追加
        if (len(S)-1) % step != 0:
            x = margin['left'] + pw * (len(S)-1) / max_steps
            y = margin['top'] + ph * (1 - (S[-1] - y_min) / (y_max - y_min))
            points.append(f"{x:.1f},{y:.1f}")

        svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.8"/>')

        # 凡例
        ly = margin['top'] + 20 + idx * 20
        svg.append(f'<line x1="{width-margin["right"]+10}" y1="{ly}" x2="{width-margin["right"]+30}" y2="{ly}" stroke="{color}" stroke-width="2"/>')
        svg.append(f'<text x="{width-margin["right"]+35}" y="{ly}" font-size="11" dominant-baseline="middle">n={n}</text>')

    # ドリフト線
    drift_end_y = margin['top'] + ph * (1 - (drift_theory * max_steps - y_min) / (y_max - y_min))
    drift_end_y_clamp = max(margin['top'], min(height - margin['bottom'], drift_end_y))
    # Find where drift line exits the plot
    if drift_theory * max_steps < y_min:
        t_exit = (y_min) / drift_theory
        x_exit = margin['left'] + pw * t_exit / max_steps
        svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"] + ph * (1 - (0 - y_min)/(y_max-y_min)):.1f}" '
                   f'x2="{x_exit:.1f}" y2="{height-margin["bottom"]}" '
                   f'stroke="black" stroke-width="1" stroke-dasharray="6,3" opacity="0.5"/>')

    svg.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"\n[SVG保存] {filename}")

def create_stopping_time_svg(stopping_times, filename):
    """停止時間 vs 理論予測のSVGプロット"""
    width, height = 900, 600
    margin = {'top': 40, 'right': 30, 'bottom': 50, 'left': 70}
    pw = width - margin['left'] - margin['right']
    ph = height - margin['top'] - margin['bottom']

    # サンプリング (多すぎるので間引く)
    sample_ns = list(range(3, 100001, 2))
    sample_step = max(1, len(sample_ns) // 2000)
    sampled = sample_ns[::sample_step]

    x_vals = [math.log2(n) for n in sampled]
    y_vals = [stopping_times[n] for n in sampled]

    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = 0, max(y_vals)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">']
    svg.append(f'<rect width="{width}" height="{height}" fill="white"/>')
    svg.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">'
               f'停止時間 vs log₂(n)</text>')

    # 軸
    svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" stroke="black"/>')
    svg.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="black"/>')

    # 散布図
    for x, y in zip(x_vals, y_vals):
        px = margin['left'] + pw * (x - x_min) / (x_max - x_min)
        py = margin['top'] + ph * (1 - y / y_max)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="#377eb8" opacity="0.3"/>')

    # 理論予測線: y = log2(n) / 0.415
    pred_factor = 1 / abs_drift
    x1_line = x_min
    x2_line = x_max
    y1_line = x1_line * pred_factor
    y2_line = x2_line * pred_factor

    px1 = margin['left']
    py1 = margin['top'] + ph * (1 - y1_line / y_max)
    px2 = margin['left'] + pw
    py2 = margin['top'] + ph * (1 - y2_line / y_max)
    svg.append(f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" stroke="red" stroke-width="2" stroke-dasharray="6,3"/>')

    # 4*log2(n) の閾値線
    y1_thresh = x1_line * 4
    y2_thresh = x2_line * 4
    py1t = margin['top'] + ph * (1 - y1_thresh / y_max)
    py2t = margin['top'] + ph * (1 - y2_thresh / y_max)
    svg.append(f'<line x1="{px1:.1f}" y1="{py1t:.1f}" x2="{px2:.1f}" y2="{py2t:.1f}" stroke="orange" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # X軸ラベル
    for i in range(6):
        val = x_min + (x_max - x_min) * i / 5
        x = margin['left'] + pw * i / 5
        svg.append(f'<text x="{x:.1f}" y="{height-margin["bottom"]+15}" text-anchor="middle" font-size="10">{val:.1f}</text>')

    # Y軸ラベル
    for i in range(6):
        val = int(y_max * i / 5)
        y = margin['top'] + ph * (1 - i / 5)
        svg.append(f'<text x="{margin["left"]-5}" y="{y:.1f}" text-anchor="end" font-size="10" dominant-baseline="middle">{val}</text>')

    svg.append(f'<text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="12">log₂(n)</text>')
    svg.append(f'<text x="15" y="{height//2}" text-anchor="middle" font-size="12" transform="rotate(-90,15,{height//2})">停止時間</text>')

    # 凡例
    svg.append(f'<circle cx="{width-180}" cy="{margin["top"]+15}" r="3" fill="#377eb8"/>')
    svg.append(f'<text x="{width-170}" y="{margin["top"]+15}" font-size="11" dominant-baseline="middle">実測値</text>')
    svg.append(f'<line x1="{width-185}" y1="{margin["top"]+35}" x2="{width-175}" y2="{margin["top"]+35}" stroke="red" stroke-width="2" stroke-dasharray="4,2"/>')
    svg.append(f'<text x="{width-170}" y="{margin["top"]+35}" font-size="11" dominant-baseline="middle">{1/abs_drift:.2f}*log₂(n)</text>')
    svg.append(f'<line x1="{width-185}" y1="{margin["top"]+55}" x2="{width-175}" y2="{margin["top"]+55}" stroke="orange" stroke-width="1.5" stroke-dasharray="4,2"/>')
    svg.append(f'<text x="{width-170}" y="{margin["top"]+55}" font-size="11" dominant-baseline="middle">4*log₂(n)</text>')

    svg.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"[SVG保存] {filename}")

def create_delta_distribution_svg(deltas, v2_values, filename):
    """delta のヒストグラム SVG"""
    width, height = 900, 500
    margin = {'top': 40, 'right': 30, 'bottom': 50, 'left': 70}
    pw = width - margin['left'] - margin['right']
    ph = height - margin['top'] - margin['bottom']

    # ヒストグラム作成（v2ごとに色分け）
    v2_max_show = 6
    bin_width = 0.05
    d_min, d_max = min(deltas) - 0.1, max(deltas) + 0.1
    n_bins = int((d_max - d_min) / bin_width) + 1

    bins = [d_min + i * bin_width for i in range(n_bins + 1)]

    # v2 ごとのヒストグラム
    hist_by_v2 = {}
    for v in range(1, v2_max_show + 1):
        hist_by_v2[v] = [0] * n_bins

    for d, v in zip(deltas, v2_values):
        bi = int((d - d_min) / bin_width)
        bi = min(bi, n_bins - 1)
        vk = min(v, v2_max_show)
        hist_by_v2[vk][bi] += 1

    max_count = max(max(h) for h in hist_by_v2.values())

    colors_v2 = {1: '#e41a1c', 2: '#377eb8', 3: '#4daf4a', 4: '#984ea3', 5: '#ff7f00', 6: '#a65628'}

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">']
    svg.append(f'<rect width="{width}" height="{height}" fill="white"/>')
    svg.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">'
               f'delta = log₂(T(n)) - log₂(n) の分布 (v2別)</text>')

    svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" stroke="black"/>')
    svg.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" stroke="black"/>')

    bar_w = pw / n_bins

    for v in range(v2_max_show, 0, -1):
        for i in range(n_bins):
            if hist_by_v2[v][i] == 0:
                continue
            h = ph * hist_by_v2[v][i] / max_count
            x = margin['left'] + bar_w * i
            y = height - margin['bottom'] - h
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{colors_v2[v]}" opacity="0.7"/>')

    # X軸ラベル
    for val in range(-6, 2):
        if d_min <= val <= d_max:
            x = margin['left'] + pw * (val - d_min) / (d_max - d_min)
            svg.append(f'<text x="{x:.1f}" y="{height-margin["bottom"]+15}" text-anchor="middle" font-size="10">{val}</text>')

    # ドリフト線
    drift_x = margin['left'] + pw * (drift_theory - d_min) / (d_max - d_min)
    svg.append(f'<line x1="{drift_x:.1f}" y1="{margin["top"]}" x2="{drift_x:.1f}" y2="{height-margin["bottom"]}" '
               f'stroke="black" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg.append(f'<text x="{drift_x:.1f}" y="{margin["top"]-5}" text-anchor="middle" font-size="10">E[δ]={drift_theory:.3f}</text>')

    svg.append(f'<text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="12">delta</text>')

    # 凡例
    for v in range(1, v2_max_show + 1):
        ly = margin['top'] + 10 + (v-1) * 18
        svg.append(f'<rect x="{width-120}" y="{ly-6}" width="12" height="12" fill="{colors_v2[v]}" opacity="0.7"/>')
        svg.append(f'<text x="{width-105}" y="{ly}" font-size="10" dominant-baseline="middle">v2={v}{"+" if v==v2_max_show else ""}</text>')

    svg.append('</svg>')

    with open(filename, 'w') as f:
        f.write('\n'.join(svg))
    print(f"[SVG保存] {filename}")

# SVG生成
print()
print("=" * 70)
print("SVG グラフ生成")
print("=" * 70)

svg_dir = "/Users/soyukke/study/lean-unsolved/scripts"
create_trajectory_svg(trajectory_data, f"{svg_dir}/potential_trajectory.svg")
create_stopping_time_svg(stopping_times, f"{svg_dir}/stopping_time_prediction.svg")
create_delta_distribution_svg(deltas, v2_values, f"{svg_dir}/delta_distribution.svg")

# ══════════════════════════════════════════════════════════════
# まとめ
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("まとめ")
print("=" * 70)
print()
print("1. 対数的ポテンシャル delta = log₂(T(n)) - log₂(n) ≈ log₂(3) - v₂(3n+1)")
print(f"   → v₂の分布が 1/2^v に従うため、E[delta] = log₂(3) - 2 ≈ {drift_theory:.4f}")
print()
print("2. 累積ポテンシャルはランダムウォーク的な振る舞いを示す")
print("   → 負のドリフトがあるため、ほぼ確実に -∞ に発散 (= 1 に到達)")
print()
print(f"3. ドリフト: 理論={drift_theory:.6f}, 実測={drift_measured:.6f}")
print(f"   分散: 理論={var_theory:.6f}, 実測={var_measured:.6f}")
print(f"   → 理論とよく一致。コラッツ写像は「ほぼランダム」に振る舞う。")
print()
print(f"4. 停止時間の予測: E[T] ≈ {1/abs_drift:.2f} * log₂(n)")
print(f"   実測平均比: {statistics.mean(ratios):.2f}")
print(f"   → やや過小評価。軌道の相関が影響。")
print()
print(f"5. 異常値 (停止時間 > 4*log₂(n)): {len(anomalies)}個")
print(f"   → 1-bit密度が高い（末尾1が多い）n で停止時間が長い傾向")
print()
print("6. ポテンシャル関数の探索:")
print(f"   最良: {best['name']} (減少率 {best['monotone_ratio']*100:.1f}%)")
print("   → 完全に単調なポテンシャルは見つからず。")
print("   → ただし末尾1ビット補正で改善される傾向あり。")
print()
print("【重要な洞察】")
print("  コラッツ予想は本質的に「負のドリフトを持つランダムウォーク」。")
print("  log₂(3) - 2 < 0 であることが、全ての軌道が 1 に到達する")
print("  「統計的な理由」。ただしこれは確率的議論であり、")
print("  全ての n に対する証明には deterministic な議論が必要。")
print("  末尾1ビットの補正が最も有望な方向性。")
