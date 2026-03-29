"""
合流定数 3.42 の精密な理論的導出 (第2段)

前の実験で判明した核心的構造:
  c_conf = 2 * (1 - alpha) / |mu|
  where alpha = E[log2(mp)] / E[log2(n)]
  mu = log2(3) - 2 = -log2(4/3)

  alpha ≈ 0.29 が定数 3.42 を決める

問い: alpha ≈ 0.29 は何で決まるか?
  - 逆像木の構造
  - 合流点の分布
  - 軌道の共有部分の長さ
"""

import math
import random
from collections import defaultdict, Counter
import statistics

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=1000):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    traj = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        traj.append(current)
    return traj

def orbit_dict(n, max_steps=500):
    orb = {}
    current = n if n % 2 == 1 else n // (n & -n)
    for i in range(max_steps):
        if current not in orb:
            orb[current] = i
        if current == 1:
            break
        current = syracuse(current)
    return orb

mu = math.log2(3) - 2  # = -0.415037
log43 = math.log2(4/3)

# ===================================================================
# Part 1: alpha = E[log2(mp)] / E[log2(n)] のN依存性
# ===================================================================
print("=" * 70)
print("Part 1: alpha のN依存性の精密測定")
print("=" * 70)

random.seed(42)
for N_test in [200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)

    log_mps = []
    s1_list = []
    s2_list = []
    total_list = []
    n_samp = min(500, len(odds)//2)

    for _ in range(n_samp):
        i, j = random.sample(range(len(odds)), 2)
        n1, n2 = odds[i], odds[j]
        orb1 = orbit_dict(n1)
        orb2 = orbit(n2)
        for js, v in enumerate(orb2):
            if v in orb1:
                s1 = orb1[v]
                s2 = js
                if v > 0:
                    log_mps.append(math.log2(v))
                s1_list.append(s1)
                s2_list.append(s2)
                total_list.append(s1 + s2)
                break

    if log_mps:
        alpha_val = statistics.mean(log_mps) / logN
        E_logn = statistics.mean([math.log2(n) for n in odds])
        alpha_rel = statistics.mean(log_mps) / E_logn
        c_val = statistics.mean(total_list) / logN
        c_pred = 2 * (1 - alpha_rel) / abs(mu)
        print(f"  N={N_test:6d}: alpha={alpha_val:.4f}, alpha_rel={alpha_rel:.4f}, "
              f"c_meas={c_val:.4f}, c_pred={c_pred:.4f}, "
              f"E[log2(mp)]={statistics.mean(log_mps):.2f}")

# ===================================================================
# Part 2: 合流点の分布の理論的モデル
# ===================================================================
print("\n" + "=" * 70)
print("Part 2: 合流点 mp の log2 分布")
print("=" * 70)

N_test = 10000
odds = list(range(3, N_test + 1, 2))
random.seed(42)

log_mps_detail = []
mp_vals = []
for _ in range(2000):
    i, j = random.sample(range(len(odds)), 2)
    n1, n2 = odds[i], odds[j]
    orb1 = orbit_dict(n1)
    orb2 = orbit(n2)
    for js, v in enumerate(orb2):
        if v in orb1:
            if v > 0:
                log_mps_detail.append(math.log2(v))
                mp_vals.append(v)
            break

print(f"サンプル数: {len(log_mps_detail)}")
print(f"E[log2(mp)] = {statistics.mean(log_mps_detail):.4f}")
print(f"Std[log2(mp)] = {statistics.stdev(log_mps_detail):.4f}")
print(f"Median[log2(mp)] = {statistics.median(log_mps_detail):.4f}")

# log2(mp) の分布をヒストグラムで
logN = math.log2(N_test)
print(f"\nlog2(mp) の分布 (N={N_test}, log2(N)={logN:.2f}):")
bins_hist = defaultdict(int)
for lm in log_mps_detail:
    b = int(lm)
    bins_hist[b] += 1

for b in sorted(bins_hist.keys()):
    bar = '#' * (bins_hist[b] * 50 // max(bins_hist.values()))
    pct = 100 * bins_hist[b] / len(log_mps_detail)
    print(f"  [{b:3d},{b+1:3d}): {bins_hist[b]:5d} ({pct:5.1f}%) {bar}")

# 合流点の頻度分布
mp_freq = Counter(mp_vals)
print(f"\n合流点 TOP 15:")
for mp, cnt in mp_freq.most_common(15):
    pct = 100 * cnt / len(mp_vals)
    print(f"  mp={mp:8d} (log2={math.log2(mp):.2f}): {cnt:4d} ({pct:.1f}%)")

# ===================================================================
# Part 3: 合流点分布の理論モデル
# ===================================================================
print("\n" + "=" * 70)
print("Part 3: 合流点分布の理論モデル")
print("=" * 70)

# 合流点 mp の分布はどう決まるか?
# mp は2つの軌道が最初に出会う点
# mp の値は、軌道の「共通部分」の始点

# 軌道上の値 n_s ≈ N * (3/4)^s (平均的に)
# 2つの軌道が深さ s で衝突する確率 ≈ 1 / S(s)
# S(s) = 深さ s で到達可能な奇数の個数

# S(s) の推定: |{T^s(n) : n odd, n <= N}|
print("\n--- 到達可能集合のサイズ S(s) ---")
N_reach = 5000
odds_reach = list(range(3, N_reach + 1, 2))

for s_depth in range(0, 40, 5):
    reach_set = set()
    for n in odds_reach:
        current = n
        for _ in range(s_depth):
            if current == 1:
                break
            current = syracuse(current)
        reach_set.add(current)
    S_s = len(reach_set)
    # 理論: S(s) ≈ N/2 * (3/4)^s (各ステップで 3/4 に縮小)
    theory = N_reach / 2 * (3/4)**s_depth
    print(f"  s={s_depth:3d}: S(s)={S_s:6d}, theory={theory:.0f}, "
          f"ratio={S_s/max(1,theory):.3f}")

# ===================================================================
# Part 4: 合流確率密度 f(s) の厳密推定
# ===================================================================
print("\n" + "=" * 70)
print("Part 4: 合流確率密度 f(d) - 深さ d での初合流確率")
print("=" * 70)

# d を「合流の深さ」= max(s1, s2) とする
N_dens = 5000
odds_dens = list(range(3, N_dens + 1, 2))
logN = math.log2(N_dens)
random.seed(42)

depth_hist = defaultdict(int)
for _ in range(3000):
    i, j = random.sample(range(len(odds_dens)), 2)
    n1, n2 = odds_dens[i], odds_dens[j]
    orb1 = orbit_dict(n1)
    orb2 = orbit(n2)
    for js, v in enumerate(orb2):
        if v in orb1:
            d = max(orb1[v], js)
            depth_hist[d] += 1
            break

total_samples = sum(depth_hist.values())
print(f"サンプル数: {total_samples}")
print(f"log2(N) = {logN:.2f}")

# 深さの分布
T_stop_est = int(logN / abs(mu))
print(f"推定停止時間: T_stop = {T_stop_est}")
print(f"\n深さ d の分布:")
cum = 0
for d in sorted(depth_hist.keys()):
    cnt = depth_hist[d]
    cum += cnt
    pct = 100 * cnt / total_samples
    bar = '#' * int(pct * 2)
    if cnt >= 20:
        print(f"  d={d:3d}: {cnt:4d} ({pct:4.1f}%) cum={100*cum/total_samples:5.1f}% {bar}")

# E[depth] の計算
E_depth = sum(d * c for d, c in depth_hist.items()) / total_samples
print(f"\nE[depth] = {E_depth:.2f}")
print(f"E[depth]/log2(N) = {E_depth/logN:.4f}")
print(f"E[depth]/T_stop = {E_depth/T_stop_est:.4f}")

# ===================================================================
# Part 5: 合流定数の理論的導出 - 第1原理から
# ===================================================================
print("\n" + "=" * 70)
print("Part 5: 理論的導出の試み")
print("=" * 70)

# ==== 核心モデル ====
# 2つの独立な Syracuse 軌道を考える
# 軌道1: n1, T(n1), T^2(n1), ...
# 軌道2: n2, T(n2), T^2(n2), ...
# 合流: T^{s1}(n1) = T^{s2}(n2)

# 仮定: ステップ s での軌道値は [1, N*(3/4)^s] の奇数から
#        「ほぼ一様」にサンプルされる

# 衝突確率モデル:
# P(T^{s1}(n1) = T^{s2}(n2)) ≈ 1/S(s) where s = typical depth
# S(s) ≈ N/2 * (3/4)^s

# 合流の条件: s1 + s2 = C (最小化)
# 制約: T^{s1}(n1) = T^{s2}(n2)
# 合流の深さ d ≈ max(s1, s2)

# 各深さ d での衝突確率:
# P(d) ≈ number_of_pairs_at_d / S(d)^2
# ≈ S(d) * S(d) / S(d) (各軌道が d 個中1つの値にいる)
# ≈ 1 / S(d)

# しかし!! 重要な補正: 深さ d での「有効な」ペア数
# s1 + s2 = C で s1 <= d, s2 <= d というペアは d+1 個ある
# → 衝突の trial 数は d+1

# より精密: 深さ d まで生存(合流していない)確率を P_surv(d) とすると
# P(最初の合流が深さ d) ≈ P_surv(d) * (d+1) / S(d)

print("\n--- 理論モデル: 累積衝突確率 ---")
for N_model in [1000, 5000, 10000, 50000, 100000]:
    logN_m = math.log2(N_model)
    T_stop_m = logN_m / abs(mu)

    # 累積衝突確率と合流時間の期待値
    log_surv = 0
    E_C = 0
    total_prob = 0

    for d in range(1, int(3 * T_stop_m)):
        # 有効状態数 at depth d
        S_d = max(1, N_model / 2 * (3/4)**d)

        # 衝突 trial 数 at depth d (新しい深さで試行できる回数)
        # 深さ d-1 まで: d ペア, 深さ d で新規: 1 ペア (asymptotic)
        # 簡略化: p_hit = 1/S_d

        surv = math.exp(log_surv)
        p_first = (1/S_d) * surv
        E_C += d * p_first
        total_prob += p_first
        log_surv += math.log(max(1e-300, 1 - 1/S_d))

        if surv < 1e-12:
            break

    # 合流時間 C ≈ s1 + s2 ≈ 2 * depth (or depth * factor)
    c_depth = E_C / logN_m
    c_total_pred = E_C / logN_m * 1.42  # 経験的補正
    print(f"  N={N_model:7d}: E[depth]={E_C:.1f}, c_depth={c_depth:.4f}, "
          f"P={total_prob:.4f}, T_stop={T_stop_m:.1f}")

# ===================================================================
# Part 6: alpha の理論的決定
# ===================================================================
print("\n" + "=" * 70)
print("Part 6: alpha = E[log2(mp)]/E[log2(n)] の理論的決定")
print("=" * 70)

# 合流点 mp の期待値: mp ≈ N * (3/4)^{d_conf}
# E[log2(mp)] = log2(N) + d_conf * log2(3/4) = log2(N) - d_conf * log2(4/3)
# alpha = 1 - d_conf * log2(4/3) / log2(N)

# d_conf ≈ c_depth * log2(N) なので
# alpha = 1 - c_depth * log2(4/3)

# 実験: c_depth を精密測定
print("\n--- c_depth の精密測定 ---")
random.seed(42)
for N_test in [500, 1000, 2000, 5000, 10000, 20000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    depths = []
    totals = []
    mp_logs = []
    n_samp = min(1000, len(odds)//2)

    for _ in range(n_samp):
        i, j = random.sample(range(len(odds)), 2)
        n1, n2 = odds[i], odds[j]
        orb1 = orbit_dict(n1)
        orb2 = orbit(n2)
        for js, v in enumerate(orb2):
            if v in orb1:
                depths.append(max(orb1[v], js))
                totals.append(orb1[v] + js)
                if v > 0:
                    mp_logs.append(math.log2(v))
                break

    if depths:
        c_d = statistics.mean(depths) / logN
        c_t = statistics.mean(totals) / logN
        alpha_m = statistics.mean(mp_logs) / logN if mp_logs else 0
        alpha_pred = 1 - c_d * log43
        ratio_td = statistics.mean(totals) / statistics.mean(depths)
        print(f"  N={N_test:6d}: c_depth={c_d:.4f}, c_total={c_t:.4f}, "
              f"alpha_meas={alpha_m:.4f}, alpha_pred={alpha_pred:.4f}, "
              f"total/depth={ratio_td:.4f}")

# ===================================================================
# Part 7: ratio = c_total / c_depth の理論的導出
# ===================================================================
print("\n" + "=" * 70)
print("Part 7: ratio = E[s1+s2]/E[depth] の理論的解析")
print("=" * 70)

# depth = max(s1, s2), total = s1 + s2
# ratio = (s1 + s2) / max(s1, s2)
# = 1 + min(s1,s2)/max(s1,s2)

# s1 と s2 の関係:
# 合流点 mp で n1 の s1 ステップ後 = n2 の s2 ステップ後
# s1 = (log2(n1) - log2(mp)) / |mu| + noise
# s2 = (log2(n2) - log2(mp)) / |mu| + noise
# n1, n2 は [3, N] の一様ランダムな奇数

# s1/s2 ≈ (log2(n1) - log2(mp)) / (log2(n2) - log2(mp))

# n1, n2 が独立一様なら:
# E[log2(n)] ≈ log2(N) - 1/ln(2) + O(1/N)
# (log2(n1) - log2(mp)) は正の値で、分布は log2(n) - log2(mp) に依存

# ratio の精密測定
random.seed(42)
N_ratio = 10000
odds_r = list(range(3, N_ratio + 1, 2))
ratios = []
s1_over_s2 = []
for _ in range(3000):
    i, j = random.sample(range(len(odds_r)), 2)
    n1, n2 = odds_r[i], odds_r[j]
    orb1 = orbit_dict(n1)
    orb2 = orbit(n2)
    for js, v in enumerate(orb2):
        if v in orb1:
            s1 = orb1[v]
            s2 = js
            d = max(s1, s2)
            if d > 0:
                ratios.append((s1 + s2) / d)
                if s2 > 0:
                    s1_over_s2.append(s1 / s2 if s1 <= s2 else s2 / s1)
            break

print(f"E[total/depth] = {statistics.mean(ratios):.6f}")
print(f"E[min(s1,s2)/max(s1,s2)] = {statistics.mean(s1_over_s2):.6f}")
print(f"ratio = 1 + E[min/max] = {1 + statistics.mean(s1_over_s2):.6f}")

# min/max の分布
print(f"\nmin(s1,s2)/max(s1,s2) の分位数:")
sorted_ratios = sorted(s1_over_s2)
for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
    idx = int(q * len(sorted_ratios))
    print(f"  {q*100:.0f}%: {sorted_ratios[idx]:.4f}")

# もし s1, s2 が独立同分布なら:
# E[min/max] = integral_0^1 integral_0^1 min(x,y)/max(x,y) dx dy
# = 2 * integral_0^1 integral_0^x y/x dy dx = 2 * integral_0^1 x/2 dx = 1/2
# しかし s1, s2 は同分布ではない (mp に依存)

# 一様分布の場合: E[min/max] = 1/2 (if s1,s2 i.i.d.)
# → ratio = 1 + 1/2 = 3/2 = 1.5
print(f"\n理論 (s1, s2 i.i.d. 一様): ratio = 3/2 = 1.5")
print(f"実測: ratio = {statistics.mean(ratios):.4f}")

# ===================================================================
# Part 8: 合流定数の最終公式
# ===================================================================
print("\n" + "=" * 70)
print("Part 8: 合流定数の最終公式")
print("=" * 70)

# c_conf = ratio * c_depth
# c_depth を理論的に決定する

# モデル: 深さ d での衝突確率 p(d) = 1 / S(d)
# S(d) = N/2 * (3/4)^d (有効状態数)
# 累積: P(conf by d) = 1 - prod_{s=1}^{d} (1 - 1/S(s))
# ≈ 1 - exp(-sum 1/S(s))

# sum_{s=1}^{d} 1/S(s) = sum 2/(N * (3/4)^s) = 2/N * sum (4/3)^s
# = 2/N * ((4/3)^{d+1} - 4/3) / (1/3)
# = 6/N * ((4/3)^{d+1} - 4/3)

# 合流条件: 6/N * (4/3)^d ≈ 1
# → (4/3)^d ≈ N/6
# → d ≈ log(N/6) / log(4/3) = log2(N/6) / log2(4/3)
# → d ≈ (log2(N) - log2(6)) / log2(4/3)

# c_depth ≈ 1/log2(4/3) - log2(6) / (log2(N) * log2(4/3))
# → c_depth → 1/log2(4/3) = c_stop as N → inf

# しかし!! この単純モデルでは c_depth = c_stop = 2.41 となり
# c_conf = 1.5 * 2.41 = 3.61 (3.42 より大きい)

print("単純衝突モデル:")
print(f"  c_depth → c_stop = {1/log43:.4f}")
print(f"  ratio = {statistics.mean(ratios):.4f}")
print(f"  c_conf_pred = ratio * c_stop = {statistics.mean(ratios) * 1/log43:.4f}")

# 修正: 衝突確率の精密化
# 実際には S(d) は (3/4)^d より速く減少する
# なぜなら軌道は必ず既存の軌道と合流するから
# → 有効状態数は「まだ合流していない」軌道の数

# これは「クーポンコレクター」問題に近い
# 実効 S(d) = S_0(d) * P_surv(d) where P_surv = まだ合流していない確率

# 別アプローチ: c_depth を直接測って c_conf = ratio * c_depth
print("\n--- N→∞ での c_depth, ratio, c_conf の推定 ---")
random.seed(42)
for N_test in [1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    depths = []
    totals = []
    n_samp = min(500, len(odds)//2)

    for _ in range(n_samp):
        i, j = random.sample(range(len(odds)), 2)
        n1, n2 = odds[i], odds[j]
        orb1 = orbit_dict(n1)
        orb2 = orbit(n2)
        for js, v in enumerate(orb2):
            if v in orb1:
                depths.append(max(orb1[v], js))
                totals.append(orb1[v] + js)
                break

    c_d = statistics.mean(depths) / logN
    c_t = statistics.mean(totals) / logN
    r = statistics.mean(totals) / statistics.mean(depths) if statistics.mean(depths) > 0 else 0
    print(f"  N={N_test:6d}: c_depth={c_d:.4f}, c_total={c_t:.4f}, ratio={r:.4f}")

# ===================================================================
# Part 9: 定数の精密同定
# ===================================================================
print("\n" + "=" * 70)
print("Part 9: 定数の精密同定")
print("=" * 70)

# 前の結果から:
# c_conf / c_stop ≈ 1.42
# 3.42 / 2.409 = 1.420

# 候補: c_conf = (1 + log2(4/3)) / log2(4/3)
val1 = (1 + log43) / log43
# = 1/log43 + 1 = c_stop + 1 = 3.409
print(f"候補1: c_stop + 1 = {val1:.6f}")

# 候補2: c_conf = 2/(2-log2(3)) - 1 = 2*c_stop - 1 = 3.819
val2 = 2 / log43 - 1
print(f"候補2: 2*c_stop - 1 = {val2:.6f}")

# 候補3: c_conf = c_stop * (1 + log2(4/3))
val3 = 1/log43 * (1 + log43)
print(f"候補3: c_stop * (1 + log2(4/3)) = {val3:.6f}")
# これは候補1と同じ

# 候補4: c_conf = c_stop + c_stop * log2(4/3) = c_stop * (1 + log2(4/3))
# = (1 + log2(4/3)) / log2(4/3)

# 候補1は 3.409 で 3.42 に非常に近い!!
# 差: 3.42 - 3.409 = 0.011 (0.3% の誤差)

# 候補5: c_conf = (3 + log2(3)) / (2*(2-log2(3)))
val5 = (3 + math.log2(3)) / (2 * log43)
print(f"候補5: (3+log2(3))/(2*log2(4/3)) = {val5:.6f}")

# 候補6: c_conf = (2+log2(3))/(2*log2(4/3))
val6 = (2 + math.log2(3)) / (2 * log43)
print(f"候補6: (2+log2(3))/(2*log2(4/3)) = {val6:.6f}")

# 候補7: log2(3) / log2(4/3)^2
val7 = math.log2(3) / log43**2
print(f"候補7: log2(3)/log2(4/3)^2 = {val7:.6f}")

# 候補8: 2*log2(3)/log2(4) (= log2(3) since log2(4)=2)
val8 = 2 * math.log2(3) / math.log2(4)
print(f"候補8: 2*log2(3)/2 = log2(3) = {val8:.6f}")

# 候補9: (1 + 1/(2*log2(4/3))) / log2(4/3)
val9 = (1 + 1/(2*log43)) / log43
print(f"候補9: (1 + 1/(2*log2(4/3)))/log2(4/3) = {val9:.6f}")

# 候補10: 精密値からの逆算
# 3.42 * log2(4/3) = 1.4194
# 1.4194 ≈ ???
target_ratio = 3.42 * log43
print(f"\n3.42 * log2(4/3) = {target_ratio:.6f}")
print(f"候補:")
print(f"  1 + log2(4/3) = {1 + log43:.6f}")
print(f"  log2(e) = {math.log2(math.e):.6f}")
print(f"  1/ln(2) = {1/math.log(2):.6f}")
print(f"  log2(3) - 1/6 = {math.log2(3) - 1/6:.6f}")
print(f"  sqrt(2) = {math.sqrt(2):.6f}")
print(f"  3*log2(4/3) + 1/6 = {3*log43 + 1/6:.6f}")

# 重要な発見: 1 + log2(4/3) = 1.415 ≈ 3.42 * log2(4/3) = 1.419
# 差は 0.004、非常に近い!
# しかし c = (1+log2(4/3))/log2(4/3) = 3.409 vs 3.42

# ===================================================================
# Part 10: 二次補正の計算
# ===================================================================
print("\n" + "=" * 70)
print("Part 10: 二次補正項の推定")
print("=" * 70)

# c(N) = c_inf + b / log2(N) + ... の形を仮定
# フィッティング

random.seed(42)
c_values = []
for N_test in [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]:
    odds = list(range(3, min(N_test + 1, 100001), 2))
    logN = math.log2(N_test)
    totals = []
    n_samp = min(800, len(odds)//2)

    for _ in range(n_samp):
        i, j = random.sample(range(len(odds)), 2)
        n1, n2 = odds[i], odds[j]
        orb1 = orbit_dict(n1)
        orb2 = orbit(n2)
        for js, v in enumerate(orb2):
            if v in orb1:
                totals.append(orb1[v] + js)
                break

    if totals:
        c_val = statistics.mean(totals) / logN
        c_values.append((logN, c_val, N_test))
        print(f"  N={N_test:7d}, log2(N)={logN:.2f}: c = {c_val:.4f}")

# 線形フィット: c = a + b/log2(N)
if len(c_values) >= 3:
    xs = [1/v[0] for v in c_values]  # 1/log2(N)
    ys = [v[1] for v in c_values]    # c(N)
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxy = sum(x*y for x,y in zip(xs, ys))
    sxx = sum(x*x for x in xs)
    b_fit = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    a_fit = (sy - b_fit*sx) / n
    print(f"\nフィット: c(N) = {a_fit:.4f} + {b_fit:.2f} / log2(N)")
    print(f"c_inf (N→∞推定) = {a_fit:.6f}")
    print(f"比較: c_stop + 1 = {1/log43 + 1:.6f}")
    print(f"比較: (1+log2(4/3))/log2(4/3) = {(1+log43)/log43:.6f}")

# ===================================================================
# 最終まとめ
# ===================================================================
print("\n\n" + "=" * 70)
print("最終まとめ: 合流定数 c の理論的導出")
print("=" * 70)

print(f"""
核心的な構造:

1. Syracuse 軌道の平均ドリフト: mu = log2(3) - 2 = -{log43:.6f}
2. 停止時間定数: c_stop = 1/log2(4/3) = {1/log43:.6f}
3. 合流定数: c_conf ≈ {a_fit:.4f} (N→∞ 推定)

理論的公式 (提案):
  c_conf = (1 + log2(4/3)) / log2(4/3) = {(1+log43)/log43:.6f}
       = c_stop + 1

物理的解釈:
  - 合流時間 C = s1 + s2 where T^s1(n1) = T^s2(n2) = mp
  - s1 ≈ (log2(n1) - log2(mp)) / |mu| (n1 → mp の到達時間)
  - s2 ≈ (log2(n2) - log2(mp)) / |mu| (n2 → mp の到達時間)
  - C ≈ (log2(n1) + log2(n2) - 2*log2(mp)) / |mu|

  合流点の深さ d ≈ c_stop * log2(N) ステップ
  → log2(mp) ≈ log2(N) - d * |mu| ≈ log2(N) * (1 - c_stop * |mu|)
     = log2(N) * (1 - 1) = 0  (!)

  つまり合流点は O(1) のサイズ → E[log2(mp)] = O(1) = {statistics.mean(log_mps_detail):.2f}

  C ≈ (2 * log2(N) - 2 * O(1)) / |mu|
    = 2 * c_stop * log2(N) - O(1)
    ≈ {2*1/log43:.3f} * log2(N)

  しかし!! 合流は停止時間より前に起きるため:
  c_conf < 2 * c_stop = {2/log43:.4f}

  精密には:
  c_conf ≈ c_stop + 1 = {1/log43 + 1:.4f}
  (追加の "+1" は合流点のlog2期待値 / |mu| に対応)

数値検証:
  実測 c ≈ 3.42 (探索142)
  理論 c = c_stop + 1 = {1/log43 + 1:.4f}
  誤差 ≈ {abs(3.42 - (1/log43 + 1)):.3f} ({100*abs(3.42 - (1/log43 + 1))/3.42:.1f}%)

上界・下界:
  下界: c_stop = {1/log43:.4f} (1つの軌道の停止時間)
  上界: 2 * c_stop = {2/log43:.4f} (2つの独立軌道の停止時間の和)
  実測: 3.42 ∈ ({1/log43:.2f}, {2/log43:.2f})
""")
