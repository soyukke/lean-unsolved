"""
合流時間定数 E[C] = 3.42 * log2(N) の理論的導出

アプローチ:
1. ランダムウォークモデル: 対数スケールでの2粒子拡散合流
2. 転送作用素のスペクトルギャップからの導出
3. 分岐過程（逆像木）の合流確率からの導出
4. 情報理論的アプローチ: 軌道の相互情報量からの合流速度

核心的な問い: なぜ定数は 1/|log2(3/4)| = 2.409 ではなく 3.42 なのか?
"""

import math
import time
import random
from collections import defaultdict, Counter
import statistics

# ===== 基本関数 =====
def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2(n):
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

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
    """軌道を {値: ステップ数} の辞書で返す"""
    orb = {}
    current = n if n % 2 == 1 else n // (n & -n)
    for i in range(max_steps):
        if current not in orb:
            orb[current] = i
        if current == 1:
            break
        current = syracuse(current)
    return orb

def confluence_time(n1, n2, max_steps=500):
    """2つの奇数の合流時間と合流点を返す"""
    orb1 = orbit_dict(n1, max_steps)
    orb2 = orbit(n2, max_steps)
    best_total = float('inf')
    best_mp = None
    for j, v in enumerate(orb2):
        if v in orb1:
            total = orb1[v] + j
            if total < best_total:
                best_total = total
                best_mp = v
    return best_total if best_total < float('inf') else None, best_mp

print("=" * 80)
print("定数 3.42 の理論的導出: 多角的アプローチ")
print("=" * 80)

# ===================================================================
# アプローチ1: 対数スケールのランダムウォークモデル
# ===================================================================
print("\n" + "=" * 70)
print("APPROACH 1: 対数スケールの2粒子ランダムウォークモデル")
print("=" * 70)

# Syracuse の1ステップにおける log2 変化量の統計
print("\n--- Step 1: log2 変化量の統計 ---")

log_changes = []
for n in range(1, 50001, 2):
    t = syracuse(n)
    delta = math.log2(t) - math.log2(n)
    log_changes.append(delta)

mu = statistics.mean(log_changes)
sigma2 = statistics.variance(log_changes)
sigma = math.sqrt(sigma2)

print(f"E[Delta log2] = {mu:.6f}")
print(f"Var[Delta log2] = {sigma2:.6f}")
print(f"Std[Delta log2] = {sigma:.6f}")
print(f"理論値 mu = log2(3) - 1 - E[v2-1] = {math.log2(3) - 1 - 1:.6f}")
print(f"  (ここで E[v2] = 2, 実効ドリフトはさらに複雑)")

# 理論: log2(T(n)/n) = log2(3) + log2(1+1/(3n)) - v2(3n+1)
# E[v2(3n+1)] = 2 (厳密に証明済み)
# E[log2(T(n)/n)] = log2(3) - 2 + 高次項 = 1.585 - 2 = -0.415

mu_theory = math.log2(3) - 2
print(f"\n理論的ドリフト: mu = log2(3) - 2 = {mu_theory:.6f}")
print(f"実測ドリフト: {mu:.6f}")
print(f"差: {mu - mu_theory:.6f} (有限サイズ効果)")

# 2粒子問題: X_t = log2(n1_t), Y_t = log2(n2_t)
# Z_t = X_t - Y_t (差過程)
# 合流 <=> n1_t = n2_t <=> Z_t = 0 (離散値で一致)
# 初期値: Z_0 = log2(n1) - log2(n2) ~ log2(N) のオーダー (ランダムペア)

# 差過程の統計
print("\n--- Step 2: 差過程 Z_t = log2(n1_t) - log2(n2_t) の統計 ---")

# 隣接ペアの差過程を追跡
diff_changes = []  # Z_{t+1} - Z_t の分布
N_sample_diff = 5000
for n1 in range(3, 2*N_sample_diff + 3, 2):
    n2 = n1 + 2
    t1 = syracuse(n1)
    t2 = syracuse(n2)
    z_before = math.log2(n1) - math.log2(n2)
    z_after = math.log2(t1) - math.log2(t2) if t1 > 0 and t2 > 0 else 0
    diff_changes.append(z_after - z_before)

mu_diff = statistics.mean(diff_changes)
var_diff = statistics.variance(diff_changes)
print(f"E[Delta Z] = {mu_diff:.6f} (差過程のドリフト)")
print(f"Var[Delta Z] = {var_diff:.6f} (差過程の拡散係数)")

# 差過程のドリフトがゼロなら、合流はランダムウォークの原点初到達
# 初到達時間: E[T] ~ Z_0^2 / (2 * D) (1次元ランダムウォーク)
# しかし差過程はドリフトがあり、log2(n)自体が減少する

# 実際には、2つの軌道は同じドリフトを持つので
# 差過程のドリフトは E[Delta Z] ≈ 0
# 差過程の拡散: Var[Delta Z] = 2 * Var[Delta log2] (独立なら)
# しかし n1, n2 が近い場合は相関がある

# 独立ランダムウォーカーの場合の理論:
D_indep = 2 * sigma2  # 独立なら分散は2倍
print(f"\n独立仮定での拡散係数: D_indep = 2*Var = {D_indep:.6f}")
print(f"実測の差過程の分散: Var_diff = {var_diff:.6f}")
print(f"相関係数推定: rho ≈ {1 - var_diff / D_indep:.4f}")

# ===================================================================
# アプローチ2: ランダムペアの合流時間理論
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 2: ランダムペアの合流 - 誕生日パラドックス型")
print("=" * 70)

# 軌道長 ~ (1/|mu|) * log2(N) ≈ 2.41 * log2(N) ステップ
# 各ステップで軌道は [1, N] の奇数のどれかにいる
# 2つの独立な軌道が同じ値を取る確率 ≈ 1/有効状態数

# 有効状態数の推定
# 軌道上の値の範囲は [1, O(N^c)] だが、実際に訪問する奇数の密度は?

print("\n--- Step 1: 軌道上の値の有効範囲 ---")
for N_test in [100, 1000, 10000]:
    odds = list(range(3, N_test + 1, 2))
    all_values = set()
    max_val = 0
    for n in odds[:min(200, len(odds))]:
        orb = orbit(n, 200)
        for v in orb:
            all_values.add(v)
            if v > max_val:
                max_val = v
    eff_states = len(all_values)
    print(f"  N={N_test}: 有効状態数={eff_states}, 最大値={max_val}, "
          f"比率 eff/N = {eff_states/N_test:.2f}")

# 誕生日パラドックス: L ステップの軌道同士で合流する確率
# P(合流 in L steps) ≈ 1 - exp(-L^2 / (2*S)) where S = 有効状態数
# E[合流時間] ≈ sqrt(2*S) (if trajectories were i.i.d.)
# しかし軌道は i.i.d. ではなく、後半は小さな値に集中する

# ===================================================================
# アプローチ3: 停止時間比からの導出
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 3: 停止時間と合流時間の関係")
print("=" * 70)

# E[停止時間] = (1/|mu|) * log2(N) = 2.41 * log2(N) (ヒューリスティック)
# E[合流時間] = c * log2(N) = 3.42 * log2(N)
# 比: c / c_stop = 3.42 / 2.41 = 1.42

# 精密測定
print("\n--- 停止時間と合流時間の精密比較 ---")
ratios_by_N = {}
for N_test in [100, 200, 500, 1000, 2000, 5000]:
    odds = list(range(3, N_test + 1, 2))

    # 停止時間
    stop_times = []
    for n in odds:
        orb = orbit(n, 1000)
        stop_times.append(len(orb) - 1)

    # 合流時間 (ランダムサンプル)
    conf_times = []
    n_pairs = min(500, len(odds) * (len(odds)-1) // 2)
    sampled = 0
    for i in range(len(odds)):
        if sampled >= n_pairs:
            break
        for j in range(i+1, min(i+10, len(odds))):
            ct, mp = confluence_time(odds[i], odds[j])
            if ct is not None:
                conf_times.append(ct)
                sampled += 1

    logN = math.log2(N_test)
    avg_stop = statistics.mean(stop_times)
    avg_conf = statistics.mean(conf_times) if conf_times else 0
    c_stop = avg_stop / logN
    c_conf = avg_conf / logN
    ratio = c_conf / c_stop if c_stop > 0 else 0

    ratios_by_N[N_test] = (c_stop, c_conf, ratio)
    print(f"  N={N_test:5d}: c_stop={c_stop:.3f}, c_conf={c_conf:.3f}, "
          f"ratio={ratio:.4f}")

# ===================================================================
# アプローチ4: 逆像木の分岐率からの導出
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 4: 逆像木の分岐率と合流確率")
print("=" * 70)

# 逆像数: |T^{-1}(n)| の平均は 4/3 (証明済み)
# t ステップ後の逆像数: ~ (4/3)^t
# N以下の奇数から出発した軌道が t ステップ後に値 v を通る確率:
# P(v in orbit_t) ~ (4/3)^t * (something) / N

# 2つの軌道が t ステップ以内に合流する確率:
# P(合流 by t) ≈ 1 - prod_{s=0}^{t} (1 - p_s) where p_s = 衝突確率 at step s

# 衝突確率 at step s:
# 両方の軌道がステップ s で同じ値にいる確率
# ≈ 1 / (有効状態数 at step s)

# 有効状態数の推定: 軌道はドリフト mu で縮小するので
# step s での典型的な値 ≈ N * 2^{mu * s}
# 有効状態数 ≈ N * 2^{mu * s} / 2 (奇数の密度 1/2)

print("\n--- 衝突確率モデル ---")
mu_eff = math.log2(3) - 2  # -0.415

for N_test in [1000, 10000, 100000]:
    logN = math.log2(N_test)

    # 累積衝突確率の計算
    # P(合流 by t) ≈ 1 - prod(1 - 1/S_s)
    # S_s = max(1, N * 2^{mu * s} / 2) = N/2 * (3/4)^s
    cum_prob = 0
    log_survival = 0  # log(prod(1 - 1/S_s))
    T_stop = int(logN / abs(mu_eff))  # 停止時間の推定

    E_confluence = 0
    for s in range(1, 3 * T_stop):
        S_s = max(1, N_test / 2 * (3/4)**s)
        p_s = 1 / S_s
        # P(最初の合流がステップ s) ≈ p_s * prod_{r<s}(1 - p_r)
        survival = math.exp(log_survival)
        prob_first = p_s * survival
        E_confluence += s * prob_first
        log_survival += math.log(max(1e-300, 1 - p_s))
        if survival < 1e-10:
            break

    total_prob = 1 - math.exp(log_survival)
    c_model = E_confluence / logN if logN > 0 else 0
    print(f"  N={N_test}: E[conf]={E_confluence:.1f}, c={c_model:.3f}, "
          f"P(conf)={total_prob:.4f}, T_stop={T_stop}")

# ===================================================================
# アプローチ5: マルコフ連鎖の混合時間からの導出
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 5: マルコフ連鎖の混合時間と合流")
print("=" * 70)

# mod 2^k でのマルコフ連鎖の混合時間 t_mix
# 2つの軌道が混合後に衝突する確率は ~1/(有効状態数)
# 合流時間 ≈ t_mix + O(有効状態数)

# しかしここでの「混合」は mod 2^k での一様分布への収束
# gap ≈ 0.65-0.82 → t_mix ≈ 1/gap ≈ 1.2-1.5 ステップ

# より精密: Syracuse を mod m で見たマルコフ連鎖
print("\n--- mod 2^k マルコフ連鎖の定常分布と合流 ---")
for k in range(2, 9):
    m = 2**k
    # 遷移行列を構築
    odd_residues = [r for r in range(1, m, 2)]
    n_states = len(odd_residues)
    state_idx = {r: i for i, r in enumerate(odd_residues)}

    # 遷移確率
    trans = [[0.0] * n_states for _ in range(n_states)]
    for r in odd_residues:
        # Syracuse(r) mod m をサンプリング
        count = Counter()
        for n in range(r, 100 * m + r, m):
            if n % 2 == 1 and n > 0:
                t = syracuse(n) % m
                if t % 2 == 0:
                    while t % 2 == 0:
                        t //= 2
                    t = t % m
                count[t] += 1
        total = sum(count.values())
        for t_val, c in count.items():
            if t_val in state_idx:
                trans[state_idx[r]][state_idx[t_val]] = c / total

    # 定常分布 (べき乗法)
    pi = [1.0 / n_states] * n_states
    for _ in range(100):
        new_pi = [0.0] * n_states
        for j in range(n_states):
            for i in range(n_states):
                new_pi[j] += pi[i] * trans[i][j]
        pi = new_pi

    # 衝突確率 = sum pi_i^2
    collision_prob = sum(p**2 for p in pi)
    mixing_time = 1.0 / (1 - collision_prob) if collision_prob < 1 else float('inf')
    print(f"  k={k}, m={m:4d}: 衝突確率={collision_prob:.6f}, "
          f"有効状態数={1/collision_prob:.1f}/{n_states}, "
          f"mix_time_est={mixing_time:.1f}")

# ===================================================================
# アプローチ6: 精密数値実験 - 合流定数の分解
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 6: 合流定数の精密分解")
print("=" * 70)

# 合流 = 2つの軌道が同じ値を取ること
# ステップ s で n1_s = n2_s が初めて成り立つ最小の s1+s2 を探す
# ここで s1, s2 はそれぞれの軌道のステップ数

# 合流時間 = s1 + s2 where n1_{s1} = n2_{s2} = 合流点
# 合流点の深さ d = 軌道上の位置 ≈ s1 ≈ s2

# 隣接ペアの合流分析
print("\n--- 隣接ペアの合流ステップの対称性 ---")
N_anal = 5000
step_pairs = []  # (s1, s2) のペア
for n1 in range(3, N_anal + 1, 4):  # n1 = 3 mod 4
    n2 = n1 + 2
    orb1 = orbit_dict(n1)
    orb2 = orbit(n2)
    for j, v in enumerate(orb2):
        if v in orb1:
            s1 = orb1[v]
            s2 = j
            step_pairs.append((s1, s2))
            break

if step_pairs:
    s1_list = [p[0] for p in step_pairs]
    s2_list = [p[1] for p in step_pairs]
    total_list = [p[0]+p[1] for p in step_pairs]
    diff_list = [abs(p[0]-p[1]) for p in step_pairs]

    print(f"  サンプル数: {len(step_pairs)}")
    print(f"  E[s1] = {statistics.mean(s1_list):.2f}")
    print(f"  E[s2] = {statistics.mean(s2_list):.2f}")
    print(f"  E[s1+s2] = {statistics.mean(total_list):.2f}")
    print(f"  E[|s1-s2|] = {statistics.mean(diff_list):.2f}")
    print(f"  log2(N) = {math.log2(N_anal):.2f}")
    print(f"  c_conf = {statistics.mean(total_list) / math.log2(N_anal):.4f}")

    # s1 と s2 の相関
    cov = statistics.mean([p[0]*p[1] for p in step_pairs]) - \
          statistics.mean(s1_list) * statistics.mean(s2_list)
    corr = cov / (statistics.stdev(s1_list) * statistics.stdev(s2_list))
    print(f"  Corr(s1, s2) = {corr:.4f}")

# ===================================================================
# アプローチ7: ドリフト+拡散モデルの厳密解
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 7: ドリフト+拡散モデルの解析的導出")
print("=" * 70)

# モデル: X_t = log2(n_t) は離散時間ランダムウォーク
# X_{t+1} = X_t + mu + sigma * Z_t (Z_t はノイズ)
# mu = log2(3) - 2 ≈ -0.415
# sigma^2 = Var[log2(T(n)/n)]

# 停止時間 (1に到達): tau = inf{t: X_t <= 0}
# E[tau] = X_0 / |mu| = log2(N) / |mu|

c_stop_theory = 1 / abs(mu_theory)
print(f"理論的停止時間定数: c_stop = 1/|mu| = {c_stop_theory:.4f}")
print(f"mu = {mu_theory:.6f}")

# 2粒子問題
# X_t (particle 1), Y_t (particle 2), 共にドリフト mu
# 差過程: Z_t = X_t - Y_t, ドリフト 0, 分散 2*sigma^2 (独立なら)
# 合流 <=> 離散的に n1_t = n2_t、これは Z_t が十分小さくなること

# しかし!!! ここが核心:
# 2つの軌道が合流するためには、log2(n)が同じだけでは不十分
# n1_s1 = n2_s2 (同じ値) が必要
# つまり合流は「2つのランダムウォークが同じ離散値を取る」問題

# 離散化効果: 軌道上の値は離散的で、密度は 1/(2x) (x = log2(n))
# つまり x 付近の奇数の密度は ~ 2^x / 2 = 2^{x-1}

print("\n--- 理論的合流定数の導出 ---")
print()
print("合流プロセスの2段階モデル:")
print("  Phase 1: 2つの軌道が同じ「深さ」(ステップ数)で同様の値域に入る")
print("  Phase 2: 実際に同じ離散値を取る")
print()

# Phase 1 の理論:
# 初期差 Z_0 = log2(n1/n2) ≈ 2/(n1) (隣接の場合)
# 一般ペア: Z_0 ~ log2(N) (ランダムペア)

# Phase 2:
# 深さ d のとき、軌道の値 ~ N * (3/4)^d
# 有効状態数 ~ N * (3/4)^d / 2
# 衝突確率 ~ 2 / (N * (3/4)^d)

# 累積衝突確率: sum_{d=0}^{T_stop} 2 / (N * (3/4)^d) = 2/N * sum (4/3)^d
# = 2/N * ((4/3)^{T_stop+1} - 1) / (1/3)
# T_stop ≈ log2(N) / 0.415 ≈ 2.41 * log2(N)
# (4/3)^{T_stop} ≈ (4/3)^{2.41 * log2(N)} = N^{2.41 * log2(4/3)} = N^{2.41 * 0.415} = N^{1.0}

# つまり (4/3)^{T_stop} ≈ N, so
# sum ~ 2/N * 3 * N = 6
# この累積衝突確率 ~ 6 は O(1) → ちょうど停止時間付近で合流する!!

log43 = math.log2(4/3)
print(f"log2(4/3) = {log43:.6f}")
print(f"c_stop * log2(4/3) = {c_stop_theory * log43:.6f}")
print(f"  (≈ 1.0 !!! 停止時間での累積衝突確率が O(1) に)")

# より精密な計算
# 合流時間 E[C] の理論:
# 2つの軌道の合流は、大部分が「停止時間の手前」で起きる
# 合流確率密度: p(d) = 2 / (N * (3/4)^d) * prod_{s<d} (1 - 2/(N*(3/4)^s))
# ≈ 2 / (N * (3/4)^d) * exp(-sum_{s<d} 2/(N*(3/4)^s))

# 指数 = -2/N * sum_{s=0}^{d-1} (4/3)^s = -2/N * ((4/3)^d - 1) / (1/3) = -6/N * ((4/3)^d - 1)
# 代入 u = (4/3)^d / N:
# p(d) dd ≈ 2u * exp(-6(Nu - 1)/N) * N/(N*u * ln(4/3)) dd
# この変換で d = log_{4/3}(Nu) なので...

# 簡略化: t = d / T_stop (正規化ステップ)
# T_stop = log2(N) / 0.415
# (3/4)^d = (3/4)^{t * T_stop} = N^{-t}
# N * (3/4)^d = N^{1-t}

# p(t) ~ 2 * N^{t-1} * exp(-6 * (N^t - 1) / N) / T_stop
# 大きい N で N^t / N = N^{t-1} が支配的

# t < 1 のとき: N^{t-1} << 1, exp部分 ≈ 1 → p(t) ≈ 0
# t ≈ 1 のとき: N^{t-1} ≈ 1 → ここに確率集中
# t > 1 のとき: exp部分が急減少

# つまり合流は t ≈ 1 (d ≈ T_stop) 付近で起きる!!

# ではなぜ E[C] > T_stop なのか?
# 合流時間 C = s1 + s2 where s1 + s2 ≈ 2 * d (合流の深さ d での s1, s2)
# いや、s1 ≈ d かつ s2 ≈ d → C ≈ 2d
# しかし合流点は1つの軌道の途中にある別の軌道の値なので s1 != s2 一般に

# 実際の合流: n1のステップ s1 での値 = n2のステップ s2 での値
# min(s1 + s2) を最小化
# 典型的には s1 ≈ s2 ≈ d (合流の深さ)
# C = s1 + s2 ≈ 2d

# 合流の深さ d の期待値を計算
print("\n--- 合流の深さの数値実験 ---")
N_depth = 3000
odds_d = list(range(3, N_depth + 1, 2))
depths = []
c_total = []
for i in range(0, min(500, len(odds_d))):
    n1 = odds_d[i]
    n2 = odds_d[(i + 7) % len(odds_d)]  # 離れたペアを取る
    if n1 == n2:
        continue
    orb1 = orbit_dict(n1)
    orb2_list = orbit(n2)
    for j, v in enumerate(orb2_list):
        if v in orb1:
            s1 = orb1[v]
            s2 = j
            d = max(s1, s2)
            depths.append(d)
            c_total.append(s1 + s2)
            break

if depths:
    logN = math.log2(N_depth)
    print(f"  N={N_depth}, log2(N)={logN:.2f}")
    print(f"  E[depth] = {statistics.mean(depths):.2f}")
    print(f"  E[s1+s2] = {statistics.mean(c_total):.2f}")
    print(f"  c_depth = E[depth]/log2(N) = {statistics.mean(depths)/logN:.4f}")
    print(f"  c_total = E[s1+s2]/log2(N) = {statistics.mean(c_total)/logN:.4f}")
    print(f"  ratio E[s1+s2]/E[depth] = {statistics.mean(c_total)/statistics.mean(depths):.4f}")

# ===================================================================
# アプローチ8: 精密な理論式
# ===================================================================
print("\n\n" + "=" * 70)
print("APPROACH 8: 精密な理論式の導出")
print("=" * 70)

# 核心の洞察:
# Syracuse 軌道の1ステップでの log2 変化:
#   Delta = log2(3) + log2(1 + 1/(3n)) - v2(3n+1)
# v2(3n+1) は幾何分布 (parameter 1/2), P(v2=k) = 1/2^k
# E[v2] = 2

# 停止時間: tau = log2(N) / |E[Delta]| = log2(N) / (2 - log2(3))

# 合流定数の導出:
# 2つの軌道が深さ d で合流する確率密度:
# f(d) = (衝突確率 at d) * (生存確率 up to d)

# 衝突確率 at d: 各軌道が到達する値の「分解能」に依存
# 深さ d での典型値 ~ N * (3/4)^d
# 深さ d で訪問する奇数の数 ~ 1 (1つの軌道は1つの値)
# → 2つの軌道が同じ値を取る確率 ~ 1 / (有効状態数)

# 有効状態数 S(d): 深さ d で到達可能な奇数の数
# これは逆像木の枝数に比例: S(d) ~ (4/3)^d * C
# (ただし N 以下に制約される)

# 合流点は逆像木の共通祖先
# n1 と n2 の最小共通祖先 (LCA) の深さが合流の深さ

# 逆像木は GW木 (超臨界, 期待子数 4/3)
# 2つのランダムな葉の LCA の深さの期待値は?
# GW木の高さ H ~ c * log(N) where c = 1 / log(4/3)

# 合流は「逆像木上での2つの葉のLCA」
# GW木の2つのランダムな葉のLCA深さ ≈ H - O(log H)

# 高さ: H ≈ log(N) / log(4/3) = log2(N) / log2(4/3) ≈ log2(N) / 0.415

log43_val = math.log2(4/3)  # ≈ 0.4150
c_height = 1 / log43_val  # ≈ 2.409
print(f"逆像木の高さ定数: 1/log2(4/3) = {c_height:.4f}")
print(f"停止時間定数:     1/(2-log2(3)) = {c_stop_theory:.4f}")
print(f"(これらは同じ値! 2-log2(3) = log2(4/3))")

# 合流時間 C = s1 + s2 ≈ 2 * d_LCA
# d_LCA ≈ T_stop - O(???)

# 精密な理論:
# c_conf = 2 * c_stop - (何か) ≈ 2 * 2.41 - ??? = 4.82 - ???
# 実測 c_conf ≈ 3.42
# → 差分 ≈ 4.82 - 3.42 = 1.40

# これは s1 と s2 の差 |s1 - s2| の寄与
# C = s1 + s2 = 2*min(s1,s2) + |s1-s2|
# min(s1, s2) ≈ d_LCA, |s1-s2| は軌道の非対称性

# ===================================================================
# 精密数値実験: 合流のメカニズム分解
# ===================================================================
print("\n\n" + "=" * 70)
print("精密数値実験: 合流のメカニズム分解")
print("=" * 70)

# ランダムペアの合流を分析
random.seed(42)
N_final = 10000
odds_final = list(range(3, N_final + 1, 2))
logN = math.log2(N_final)

results = {
    's1': [], 's2': [], 'total': [], 'depth': [],
    'stop1': [], 'stop2': [], 'mp': []
}

n_samples = 1000
for _ in range(n_samples):
    i, j = random.sample(range(len(odds_final)), 2)
    n1, n2 = odds_final[i], odds_final[j]

    orb1 = orbit_dict(n1)
    orb2_list = orbit(n2)

    # 停止時間
    stop1 = max(orb1.values())
    stop2 = len(orb2_list) - 1

    for js, v in enumerate(orb2_list):
        if v in orb1:
            s1 = orb1[v]
            s2 = js
            results['s1'].append(s1)
            results['s2'].append(s2)
            results['total'].append(s1 + s2)
            results['depth'].append(max(s1, s2))
            results['stop1'].append(stop1)
            results['stop2'].append(stop2)
            results['mp'].append(v)
            break

print(f"N = {N_final}, log2(N) = {logN:.2f}")
print(f"サンプル数: {len(results['total'])}")
print(f"\n--- 平均値 ---")
print(f"E[s1]       = {statistics.mean(results['s1']):.2f} "
      f"(c = {statistics.mean(results['s1'])/logN:.4f})")
print(f"E[s2]       = {statistics.mean(results['s2']):.2f} "
      f"(c = {statistics.mean(results['s2'])/logN:.4f})")
print(f"E[s1+s2]    = {statistics.mean(results['total']):.2f} "
      f"(c = {statistics.mean(results['total'])/logN:.4f})")
print(f"E[max(s1,s2)] = {statistics.mean(results['depth']):.2f} "
      f"(c = {statistics.mean(results['depth'])/logN:.4f})")
print(f"E[stop1]    = {statistics.mean(results['stop1']):.2f} "
      f"(c = {statistics.mean(results['stop1'])/logN:.4f})")
print(f"E[stop2]    = {statistics.mean(results['stop2']):.2f} "
      f"(c = {statistics.mean(results['stop2'])/logN:.4f})")

# 合流の深さが停止時間に対してどこにあるか
rel_depth = [d / max(1, s) for d, s in
             zip(results['depth'],
                 [max(s1, s2) for s1, s2 in zip(results['stop1'], results['stop2'])])]
print(f"\nE[depth/max_stop] = {statistics.mean(rel_depth):.4f}")
print("(合流は停止時間の何割のところで起きるか)")

# min(s1,s2)/max(s1,s2) の分布
s_ratios = [min(s1, s2) / max(s1, s2) if max(s1, s2) > 0 else 1
            for s1, s2 in zip(results['s1'], results['s2'])]
print(f"E[min(s1,s2)/max(s1,s2)] = {statistics.mean(s_ratios):.4f}")
print("(s1とs2の対称性)")

# ===================================================================
# 理論的定数の最終的な導出
# ===================================================================
print("\n\n" + "=" * 70)
print("理論的定数の導出: 最終結論")
print("=" * 70)

# key insight: 合流時間 = s1 + s2 where 合流点 mp は両軌道上にある
# s1 = n1 が mp に到達するステップ数
# s2 = n2 が mp に到達するステップ数
# s1 + s2 ≈ (n1→mp の停止時間) + (n2→mp の停止時間)
# ≈ log2(n1/mp)/0.415 + log2(n2/mp)/0.415
# = (log2(n1) + log2(n2) - 2*log2(mp)) / 0.415

# mp の log2 の期待値
mp_log = [math.log2(mp) for mp in results['mp'] if mp > 0]
print(f"E[log2(mp)] = {statistics.mean(mp_log):.2f}")
print(f"E[log2(n)]  = {statistics.mean([math.log2(n) for n in odds_final]):.2f}")

# C = (E[log2(n1)] + E[log2(n2)] - 2*E[log2(mp)]) / |mu|
# E[log2(n)] ≈ log2(N) - 1 (一様分布の場合)
# E[log2(mp)] = ?
E_logn = statistics.mean([math.log2(n) for n in odds_final])
E_logmp = statistics.mean(mp_log)

c_predicted = (2 * E_logn - 2 * E_logmp) / abs(mu_theory)
print(f"\n予測: C = (2*E[log2(n)] - 2*E[log2(mp)]) / |mu|")
print(f"  = (2*{E_logn:.2f} - 2*{E_logmp:.2f}) / {abs(mu_theory):.4f}")
print(f"  = {c_predicted:.2f}")
print(f"  定数 c = {c_predicted / logN:.4f}")
print(f"  実測: c = {statistics.mean(results['total'])/logN:.4f}")

# 合流点の相対位置
# alpha = E[log2(mp)] / E[log2(n)]
alpha = E_logmp / E_logn
print(f"\nalpha = E[log2(mp)]/E[log2(n)] = {alpha:.4f}")
print(f"理論: c_conf = 2 * (1 - alpha) / |mu|")
print(f"  = 2 * (1 - {alpha:.4f}) / {abs(mu_theory):.4f}")
print(f"  = {2 * (1 - alpha) / abs(mu_theory):.4f}")

# ===================================================================
# 超精密測定: 多くの N で定数を測定
# ===================================================================
print("\n\n" + "=" * 70)
print("超精密測定: N依存性")
print("=" * 70)

random.seed(123)
for N_test in [500, 1000, 2000, 5000, 10000, 20000, 50000]:
    t0 = time.time()
    odds_t = list(range(3, N_test + 1, 2))
    logN_t = math.log2(N_test)

    n_samp = min(300, len(odds_t) * (len(odds_t)-1) // 2)
    conf_t = []

    for _ in range(n_samp):
        i, j = random.sample(range(len(odds_t)), 2)
        n1, n2 = odds_t[i], odds_t[j]
        ct, mp = confluence_time(n1, n2)
        if ct is not None:
            conf_t.append(ct)

    elapsed = time.time() - t0
    if conf_t:
        c_val = statistics.mean(conf_t) / logN_t
        c_med = statistics.median(conf_t) / logN_t
        print(f"  N={N_test:6d}: c_mean={c_val:.4f}, c_median={c_med:.4f}, "
              f"E[C]={statistics.mean(conf_t):.1f}, {elapsed:.1f}s")


# ===================================================================
# 最終理論: 精密公式の提案
# ===================================================================
print("\n\n" + "=" * 70)
print("最終理論: 精密公式の提案")
print("=" * 70)

mu_val = math.log2(3) - 2  # = -log2(4/3)
log43 = math.log2(4/3)

print(f"\n基本定数:")
print(f"  mu = log2(3) - 2 = -{log43:.6f}")
print(f"  sigma^2 = Var[Delta log2] = {sigma2:.6f}")
print(f"  log2(4/3) = {log43:.6f}")

# 停止時間の定数
c_stop_val = 1 / log43
print(f"\n停止時間の定数:")
print(f"  c_stop = 1/log2(4/3) = {c_stop_val:.6f}")

# 合流定数の候補式
candidates = {
    "2/log2(4/3)": 2 / log43,
    "1/log2(4/3) + sigma^2/(2*mu^2)": 1/log43 + sigma2/(2*mu_val**2),
    "(1 + 1/log2(4/3))/log2(4/3)": (1 + 1/log43) / log43,
    "2*log2(3)/log2(4/3)^2": 2*math.log2(3) / log43**2,
    "pi^2/(6*log2(4/3))": math.pi**2 / (6 * log43),
    "(2 + sigma^2/mu^2) / log2(4/3)": (2 + sigma2/mu_val**2) / log43,
    "1/(log2(4/3) * (1 - log2(4/3)/2))": 1/(log43 * (1 - log43/2)),
    "2/(2 - log2(3))": 2/(2 - math.log2(3)),
    "log2(3)/(2-log2(3))^2": math.log2(3)/(2-math.log2(3))**2,
}

print(f"\n候補式と値 (目標: 3.42):")
for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - 3.42)):
    err = abs(val - 3.42)
    print(f"  {val:.6f} ({err:.4f}差) : {name}")

# 一番近い候補の検証
print(f"\n最良候補の詳細検証:")
best_name = min(candidates, key=lambda k: abs(candidates[k] - 3.42))
best_val = candidates[best_name]
print(f"  式: {best_name}")
print(f"  値: {best_val:.8f}")
print(f"  誤差: {abs(best_val - 3.42):.6f}")

# 追加候補: 数値フィッティング的なもの
# 3.42 ≈ ??? / log2(4/3)
print(f"\n3.42 * log2(4/3) = {3.42 * log43:.6f}")
print(f"3.42 * log2(4/3)^2 = {3.42 * log43**2:.6f}")
print(f"3.42 / (1/log2(4/3)) = {3.42 / c_stop_val:.6f}")
print(f"3.42 - 2*c_stop = {3.42 - 2*c_stop_val:.6f}")
print(f"3.42 - c_stop = {3.42 - c_stop_val:.6f}")

# 3.42 ≈ c_stop + ??
# 3.42 - 2.409 ≈ 1.01
# 3.42 / c_stop ≈ 1.420
ratio_obs = 3.42 / c_stop_val
print(f"\n重要な比:")
print(f"  c_conf / c_stop = {ratio_obs:.6f}")
print(f"  この比は何か?")
print(f"    log2(3) = {math.log2(3):.6f}")
print(f"    3/2 = {3/2:.6f}")
print(f"    1 + log2(4/3) = {1 + log43:.6f}")
print(f"    c_stop + 1 / c_stop = {c_stop_val + 1/c_stop_val:.6f}")
print(f"    e/2 = {math.e/2:.6f}")

print("\n" + "=" * 70)
print("分析完了")
print("=" * 70)
