"""
Syracuse軌道の合流統計分析

異なる始点 n1, n2 の Syracuse 軌道が合流するまでのステップ数を計算。
合流時間の分布、合流点のmod構造を調べる。

Syracuse関数: T(n) = (3n+1) / 2^{v2(3n+1)}  (奇数 -> 奇数)
"""

import math
import time
import json
from collections import defaultdict, Counter
import statistics

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} for odd n"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=1000):
    """nからのSyracuse軌道を計算。奇数のみ。"""
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    trajectory = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        trajectory.append(current)
    return trajectory

def confluence_steps(n1, n2, max_steps=500):
    """
    n1, n2 の軌道が合流するまでのステップ数を返す。
    合流 = 同じ値に到達すること。
    返り値: (steps1, steps2, meeting_point) or None
    steps1: n1側から合流点までのステップ数
    steps2: n2側から合流点までのステップ数
    """
    # 両方の完全軌道を計算
    orb1 = orbit(n1, max_steps)
    orb2 = orbit(n2, max_steps)

    # 軌道1の値 -> ステップ数 マッピング
    pos1 = {}
    for i, v in enumerate(orb1):
        if v not in pos1:
            pos1[v] = i

    # 軌道2の各値を軌道1と比較
    best = None
    for j, v in enumerate(orb2):
        if v in pos1:
            i = pos1[v]
            total = i + j
            if best is None or total < best[0] + best[1]:
                best = (i, j, v)

    return best

def make_odd(n):
    while n % 2 == 0:
        n //= 2
    return n

# ===== 分析1: 合流時間の分布 =====
print("=" * 70)
print("分析1: Syracuse軌道の合流時間の分布")
print("=" * 70)

N_max = 500  # 奇数の範囲
odd_numbers = [n for n in range(3, N_max + 1, 2)]  # 3, 5, 7, ..., 499

confluence_data = []
total_steps_list = []
meeting_points = []

t0 = time.time()
pair_count = 0
no_confluence = 0

for i, n1 in enumerate(odd_numbers):
    for n2 in odd_numbers[i+1:]:
        result = confluence_steps(n1, n2)
        pair_count += 1
        if result:
            s1, s2, mp = result
            total = s1 + s2
            confluence_data.append({
                'n1': n1, 'n2': n2,
                'steps1': s1, 'steps2': s2,
                'total': total,
                'meeting_point': mp
            })
            total_steps_list.append(total)
            meeting_points.append(mp)
        else:
            no_confluence += 1

t1 = time.time()
print(f"ペア数: {pair_count}, 合流成功: {len(confluence_data)}, 失敗: {no_confluence}")
print(f"計算時間: {t1-t0:.2f}秒")

if total_steps_list:
    print(f"\n--- 合流時間(total steps)の統計 ---")
    print(f"  平均: {statistics.mean(total_steps_list):.2f}")
    print(f"  中央値: {statistics.median(total_steps_list):.1f}")
    print(f"  最大: {max(total_steps_list)}")
    print(f"  最小: {min(total_steps_list)}")
    print(f"  標準偏差: {statistics.stdev(total_steps_list):.2f}")

    # ヒストグラム（テキスト版）
    step_counts = Counter(total_steps_list)
    print(f"\n--- 合流時間のヒストグラム (ビン幅=5) ---")
    bins = defaultdict(int)
    for s in total_steps_list:
        b = (s // 5) * 5
        bins[b] += 1
    for b in sorted(bins.keys())[:20]:
        bar = '#' * (bins[b] * 60 // max(bins.values()))
        print(f"  [{b:3d}-{b+4:3d}]: {bins[b]:5d} {bar}")
    if len(bins) > 20:
        print(f"  ... (残り {len(bins)-20} ビン)")

# ===== 分析2: 合流点のmod構造 =====
print("\n" + "=" * 70)
print("分析2: 合流点のmod構造")
print("=" * 70)

if meeting_points:
    # mod 3 分布
    mod3 = Counter(mp % 3 for mp in meeting_points)
    print(f"\n合流点 mod 3:")
    for r in sorted(mod3.keys()):
        pct = 100 * mod3[r] / len(meeting_points)
        print(f"  {r}: {mod3[r]} ({pct:.1f}%)")

    # mod 4 分布
    mod4 = Counter(mp % 4 for mp in meeting_points)
    print(f"\n合流点 mod 4 (奇数のみなので 1 or 3):")
    for r in sorted(mod4.keys()):
        pct = 100 * mod4[r] / len(meeting_points)
        print(f"  {r}: {mod4[r]} ({pct:.1f}%)")

    # mod 8 分布
    mod8 = Counter(mp % 8 for mp in meeting_points)
    print(f"\n合流点 mod 8:")
    for r in sorted(mod8.keys()):
        pct = 100 * mod8[r] / len(meeting_points)
        print(f"  {r}: {mod8[r]} ({pct:.1f}%)")

    # 最頻合流点
    mp_counts = Counter(meeting_points)
    print(f"\n最頻合流点 TOP 15:")
    for mp, cnt in mp_counts.most_common(15):
        print(f"  n={mp}: {cnt}回 (mod3={mp%3}, mod8={mp%8})")

    # 合流点=1の割合
    cnt1 = mp_counts.get(1, 0)
    print(f"\n合流点=1: {cnt1}/{len(meeting_points)} ({100*cnt1/len(meeting_points):.1f}%)")

# ===== 分析3: gcd(n1,n2)と合流時間の関係 =====
print("\n" + "=" * 70)
print("分析3: gcd(n1,n2) と合流時間の関係")
print("=" * 70)

gcd_groups = defaultdict(list)
for d in confluence_data:
    g = math.gcd(d['n1'], d['n2'])
    gcd_groups[g].append(d['total'])

print(f"\ngcd(n1,n2) -> 平均合流時間:")
for g in sorted(gcd_groups.keys())[:15]:
    vals = gcd_groups[g]
    if len(vals) >= 5:
        print(f"  gcd={g}: mean={statistics.mean(vals):.1f}, n={len(vals)}")

# ===== 分析4: |n1-n2|と合流時間の関係 =====
print("\n" + "=" * 70)
print("分析4: |n1-n2| と合流時間の関係")
print("=" * 70)

diff_groups = defaultdict(list)
for d in confluence_data:
    diff = abs(d['n1'] - d['n2'])
    diff_bin = diff // 20  # 20刻みでビニング
    diff_groups[diff_bin].append(d['total'])

print(f"\n|n1-n2|ビン -> 平均合流時間:")
for b in sorted(diff_groups.keys())[:15]:
    vals = diff_groups[b]
    lo, hi = b * 20, b * 20 + 19
    print(f"  [{lo:3d}-{hi:3d}]: mean={statistics.mean(vals):.1f}, n={len(vals)}")

# ===== 分析5: 合流時間と n1 mod 8, n2 mod 8 の関係 =====
print("\n" + "=" * 70)
print("分析5: (n1 mod 8, n2 mod 8) と平均合流時間")
print("=" * 70)

mod8_pair_data = defaultdict(list)
for d in confluence_data:
    r1 = d['n1'] % 8
    r2 = d['n2'] % 8
    key = (min(r1, r2), max(r1, r2))  # 対称化
    mod8_pair_data[key].append(d['total'])

print(f"\n(r1 mod8, r2 mod8) -> 平均合流時間:")
for key in sorted(mod8_pair_data.keys()):
    vals = mod8_pair_data[key]
    if len(vals) >= 10:
        print(f"  {key}: mean={statistics.mean(vals):.1f}, median={statistics.median(vals):.0f}, n={len(vals)}")

# ===== 分析6: n1, n2 が同じ mod 2^k 残基を持つ場合 =====
print("\n" + "=" * 70)
print("分析6: n1 ≡ n2 (mod 2^k) のときの合流時間")
print("=" * 70)

for k in range(1, 8):
    m = 2**k
    same_mod = [d['total'] for d in confluence_data if d['n1'] % m == d['n2'] % m]
    diff_mod = [d['total'] for d in confluence_data if d['n1'] % m != d['n2'] % m]
    if same_mod and diff_mod:
        print(f"  mod 2^{k} (={m}): 一致={statistics.mean(same_mod):.1f} (n={len(same_mod)}), "
              f"不一致={statistics.mean(diff_mod):.1f} (n={len(diff_mod)})")

# ===== 分析7: 「ハブ」合流点の逆木入次数構造 =====
print("\n" + "=" * 70)
print("分析7: ハブ合流点の構造分析")
print("=" * 70)

if meeting_points:
    mp_counts = Counter(meeting_points)
    top_hubs = mp_counts.most_common(20)

    print(f"\nTop 20 ハブ合流点の詳細:")
    for mp, cnt in top_hubs:
        # 逆Syracuse: T(m) = mp の解を列挙
        # m = (2^a * mp - 1) / 3 for a s.t. 2^a * mp ≡ 1 (mod 3)
        preimages = []
        for a in range(1, 30):
            val = (2**a * mp - 1)
            if val % 3 == 0:
                pre = val // 3
                if pre > 0 and pre % 2 == 1:  # 奇数のみ
                    preimages.append((pre, a))

        pre_str = ", ".join(f"{p}(a={a})" for p, a in preimages[:5])
        print(f"  mp={mp}: {cnt}回, mod3={mp%3}, mod8={mp%8}, "
              f"逆像: [{pre_str}]")

# ===== 分析8: 合流距離のスケーリング =====
print("\n" + "=" * 70)
print("分析8: 合流時間のスケーリング (log(n)依存性)")
print("=" * 70)

# n1+n2 の対数と合流時間の関係
scale_bins = defaultdict(list)
for d in confluence_data:
    log_sum = math.log2(d['n1'] + d['n2'])
    b = int(log_sum)
    scale_bins[b].append(d['total'])

print(f"\nlog2(n1+n2)ビン -> 平均合流時間:")
for b in sorted(scale_bins.keys()):
    vals = scale_bins[b]
    if len(vals) >= 20:
        print(f"  log2 ~ {b}: mean={statistics.mean(vals):.1f}, "
              f"median={statistics.median(vals):.0f}, n={len(vals)}")

# ===== 分析9: 同じ軌道に落ちる初期値のクラスタ =====
print("\n" + "=" * 70)
print("分析9: k=3 ステップ後に一致するペアの分類")
print("=" * 70)

for k_steps in [1, 2, 3, 5]:
    # kステップ後の値でグルーピング
    groups = defaultdict(list)
    for n in odd_numbers:
        val = n
        for _ in range(k_steps):
            if val == 1:
                break
            val = syracuse(val)
        groups[val].append(n)

    multi_groups = {v: ns for v, ns in groups.items() if len(ns) > 1}
    total_in_groups = sum(len(ns) for ns in multi_groups.values())
    print(f"\n  k={k_steps}: {len(multi_groups)} クラスタ, "
          f"{total_in_groups}/{len(odd_numbers)} が非自明クラスタに属する")

    # 最大クラスタを表示
    if multi_groups:
        biggest = max(multi_groups.items(), key=lambda x: len(x[1]))
        print(f"    最大クラスタ: T^{k_steps}={biggest[0]}, "
              f"メンバー={biggest[1][:10]}{'...' if len(biggest[1])>10 else ''}")

# ===== 分析10: 合流までの軌道の「形状」比較 =====
print("\n" + "=" * 70)
print("分析10: 合流パターンのタイプ分類")
print("=" * 70)

# 合流タイプ:
# A型: n1が先に合流点に到達し、n2が後から追いつく (steps1 < steps2)
# B型: n2が先 (steps1 > steps2)
# C型: 同時到達 (steps1 == steps2)

type_A = sum(1 for d in confluence_data if d['steps1'] < d['steps2'])
type_B = sum(1 for d in confluence_data if d['steps1'] > d['steps2'])
type_C = sum(1 for d in confluence_data if d['steps1'] == d['steps2'])

print(f"\n合流タイプ:")
print(f"  A型 (n1先着): {type_A} ({100*type_A/len(confluence_data):.1f}%)")
print(f"  B型 (n2先着): {type_B} ({100*type_B/len(confluence_data):.1f}%)")
print(f"  C型 (同時): {type_C} ({100*type_C/len(confluence_data):.1f}%)")

# 同時到達ペアの特徴
if type_C > 0:
    simultaneous = [d for d in confluence_data if d['steps1'] == d['steps2']]
    print(f"\n  C型ペアの例 (最大10):")
    for d in simultaneous[:10]:
        print(f"    ({d['n1']}, {d['n2']}) -> mp={d['meeting_point']} at step {d['steps1']}")

# ===== 分析11: 大きな範囲での合流時間の成長 =====
print("\n" + "=" * 70)
print("分析11: 合流時間の成長率 (N増大時)")
print("=" * 70)

for N_test in [100, 200, 500, 1000, 2000]:
    # ランダムではなく等間隔サンプリング
    test_odds = list(range(3, N_test + 1, 2))
    sample_steps = []
    # 隣接ペアのみで高速化
    for i in range(len(test_odds) - 1):
        result = confluence_steps(test_odds[i], test_odds[i+1])
        if result:
            sample_steps.append(result[0] + result[1])

    if sample_steps:
        avg = statistics.mean(sample_steps)
        print(f"  N={N_test:5d}: 隣接ペア平均合流時間={avg:.2f}, "
              f"log2(N)={math.log2(N_test):.1f}, "
              f"ratio={avg/math.log2(N_test):.2f}")

# ===== 分析12: 合流点 n=3077 への集中度 =====
print("\n" + "=" * 70)
print("分析12: 特定合流点 (n=1, n=5, n=3077 等) への到達")
print("=" * 70)

special_points = [1, 5, 7, 11, 13, 17, 19, 23, 85, 3077]
for sp in special_points:
    cnt = sum(1 for mp in meeting_points if mp == sp)
    if cnt > 0:
        print(f"  合流点={sp}: {cnt}回 ({100*cnt/len(meeting_points):.2f}%)")

# 3077が軌道に含まれるnの数
pass_3077 = 0
for n in odd_numbers:
    orb = orbit(n, 500)
    if 3077 in orb:
        pass_3077 += 1
pct_3077 = 100 * pass_3077 / len(odd_numbers)
print(f"\n  3077を通過するn (3..{N_max}の奇数): {pass_3077}/{len(odd_numbers)} ({pct_3077:.1f}%)")

print("\n" + "=" * 70)
print("全分析完了")
print("=" * 70)
