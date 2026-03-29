"""
探索172: 軌道不変測度のmod 2^k表現とTao ergodic approachとの接続

目標:
1. 軌道上でn≡r(mod 2^k)の頻度 mu_k(r) の精密計算
2. Syracuse遷移行列の定常分布との比較
3. mu_k(r) の閉公式（あるいは漸近公式）の導出
4. v2=4過大表現(1.42倍)のTao理論的説明
5. 軌道truncationと終端効果の分離

numpy不使用、純粋Python実装
"""

import json
import math
import random
from collections import Counter, defaultdict

# === ユーティリティ ===

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def syracuse(n):
    """Syracuse map: n odd -> (3n+1)/2^v2(3n+1)"""
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def collatz_orbit_odd(n, max_steps=10000):
    """コラッツ軌道の奇数ステップを列挙"""
    steps = []
    x = n
    if x % 2 == 0:
        while x % 2 == 0:
            x //= 2
    seen = set()
    for _ in range(max_steps):
        steps.append(x)
        if x == 1:
            break
        if x in seen:
            break
        seen.add(x)
        x = syracuse(x)
    return steps


# ============================================================
# Part 1: 軌道不変測度の大規模計算
# ============================================================

def compute_orbit_measure(N_max, k, odd_only_start=True):
    """軌道上のmod 2^k頻度を計算"""
    mod = 2 ** k
    freq = Counter()
    total = 0

    start_range = range(3, N_max + 1, 2) if odd_only_start else range(1, N_max + 1)
    for n0 in start_range:
        orbit = collatz_orbit_odd(n0)
        for x in orbit:
            freq[x % mod] += 1
            total += 1

    return freq, total

print("=" * 60)
print("Part 1: 軌道不変測度 mu_k(r) の計算")
print("=" * 60)

N_MAX = 30000
print(f"初期値: N=3..{N_MAX} (奇数のみ)")

# 各 k での測度
all_measures = {}
for k in range(2, 8):
    freq, total = compute_orbit_measure(N_MAX, k)
    mod = 2 ** k
    odd_res = [r for r in range(mod) if r % 2 == 1]
    uniform_val = total / len(odd_res)

    measure = {}
    for r in odd_res:
        mu = freq[r] / total
        ratio = freq[r] / uniform_val
        measure[r] = {"mu": mu, "ratio": ratio, "v2_3r1": v2(3*r+1)}

    all_measures[k] = {"mod": mod, "total": total, "measure": measure}

# mod 32 (k=5) 詳細表示
print("\n--- mod 32 残基分布（ratio_to_uniform降順）---")
k5 = all_measures[5]
sorted_res = sorted(k5["measure"].items(), key=lambda x: -x[1]["ratio"])
for r, data in sorted_res:
    print(f"  r={r:2d}: mu={data['mu']:.6f}, ratio={data['ratio']:.4f}, v2(3r+1)={data['v2_3r1']}")


# ============================================================
# Part 2: v2分布のmod 2^k依存性
# ============================================================

print("\n" + "=" * 60)
print("Part 2: v2分布の測度からの導出")
print("=" * 60)

for k in [4, 5, 6, 7]:
    m = all_measures[k]
    v2_mu = defaultdict(float)
    v2_count = defaultdict(int)
    for r, data in m["measure"].items():
        v = data["v2_3r1"]
        v2_mu[v] += data["mu"]
        v2_count[v] += 1

    print(f"\n--- mod {2**k} (k={k}) ---")
    for vv in sorted(v2_mu.keys()):
        if vv > k:
            continue
        theory = 1.0 / (2**vv)
        ratio = v2_mu[vv] / theory if theory > 0 else 0
        print(f"  v2={vv}: mu_sum={v2_mu[vv]:.6f}, theory=1/{2**vv}={theory:.6f}, ratio={ratio:.4f}, #res={v2_count[vv]}")


# ============================================================
# Part 3: Syracuse遷移行列の定常分布（べき乗法）
# ============================================================

print("\n" + "=" * 60)
print("Part 3: Syracuse遷移行列の定常分布")
print("=" * 60)

def build_transition_matrix(k, num_lifts=300):
    """mod 2^k でのSyracuse遷移行列を構築"""
    mod = 2 ** k
    odd_res = sorted([r for r in range(mod) if r % 2 == 1])
    n = len(odd_res)
    idx = {r: i for i, r in enumerate(odd_res)}

    # P[i][j]
    P = [[0.0] * n for _ in range(n)]

    for r in odd_res:
        targets = Counter()
        for lift in range(num_lifts):
            x = r + lift * mod
            if x <= 0:
                continue
            y = syracuse(x)
            t = y % mod
            if t % 2 == 0:
                # make odd
                while t % 2 == 0:
                    t = (t + mod) if t == 0 else t
                    # this shouldn't happen for Syracuse output
                    break
            targets[t] += 1

        total = sum(targets.values())
        i = idx[r]
        for t, count in targets.items():
            if t in idx:
                P[i][idx[t]] = count / total

    return P, odd_res, idx

def power_iteration(P, n, iterations=500):
    """べき乗法で定常分布を近似"""
    # 初期ベクトル
    pi = [1.0 / n] * n

    for _ in range(iterations):
        new_pi = [0.0] * n
        for j in range(n):
            for i in range(n):
                new_pi[j] += pi[i] * P[i][j]
        # 正規化
        s = sum(new_pi)
        pi = [x / s for x in new_pi]

    return pi

for k in [3, 4, 5]:
    P, residues, idx = build_transition_matrix(k, num_lifts=500)
    n = len(residues)
    pi = power_iteration(P, n, iterations=1000)
    uniform = 1.0 / n

    print(f"\n--- mod {2**k} (k={k}) 定常分布 vs 軌道測度 ---")

    orbit_m = all_measures[k]["measure"] if k in all_measures else {}

    for i, r in enumerate(residues):
        pi_r = pi[i]
        ratio_pi = pi_r / uniform
        orbit_ratio = orbit_m[r]["ratio"] if r in orbit_m else 0
        if abs(ratio_pi - 1.0) > 0.03 or abs(orbit_ratio - 1.0) > 0.03:
            print(f"  r={r:3d}: pi_stationary={ratio_pi:.4f}, orbit_measure={orbit_ratio:.4f}, diff={abs(ratio_pi - orbit_ratio):.4f}")


# ============================================================
# Part 4: 終端効果の分離
# ============================================================

print("\n" + "=" * 60)
print("Part 4: 終端効果の分離（1除外・truncation）")
print("=" * 60)

# 4a: 1を除外
def compute_measure_excl1(N_max, k):
    """n=1を除外した軌道測度"""
    mod = 2 ** k
    freq = Counter()
    total = 0

    for n0 in range(3, N_max + 1, 2):
        orbit = collatz_orbit_odd(n0)
        for x in orbit:
            if x != 1:
                freq[x % mod] += 1
                total += 1

    return freq, total

# 4b: 1とn=5を除外
def compute_measure_excl15(N_max, k):
    """n=1,5を除外した軌道測度"""
    mod = 2 ** k
    freq = Counter()
    total = 0

    for n0 in range(3, N_max + 1, 2):
        orbit = collatz_orbit_odd(n0)
        for x in orbit:
            if x != 1 and x != 5:
                freq[x % mod] += 1
                total += 1

    return freq, total

# 4c: 最初のK ステップのみ
def compute_measure_first_k_steps(N_max, mod_k, max_orbit_len):
    """軌道の最初のmax_orbit_lenステップのみ"""
    mod = 2 ** mod_k
    freq = Counter()
    total = 0

    for n0 in range(3, N_max + 1, 2):
        orbit = collatz_orbit_odd(n0, max_steps=max_orbit_len)
        for x in orbit[:max_orbit_len]:
            freq[x % mod] += 1
            total += 1

    return freq, total

# 比較
k = 5
mod = 32
odd_res = [r for r in range(mod) if r % 2 == 1]

# 通常
freq_all, tot_all = compute_orbit_measure(20000, k)
# 1除外
freq_e1, tot_e1 = compute_measure_excl1(20000, k)
# 1,5除外
freq_e15, tot_e15 = compute_measure_excl15(20000, k)

print("\nmod 32: 通常 vs 1除外 vs 1,5除外")
print(f"{'r':>3} {'all':>8} {'excl1':>8} {'excl1,5':>8} {'v2':>4}")
for r in sorted(odd_res):
    ratio_all = (freq_all[r] / tot_all) * 16
    ratio_e1 = (freq_e1[r] / tot_e1) * 16
    ratio_e15 = (freq_e15[r] / tot_e15) * 16
    v2_val = v2(3*r + 1)
    if abs(ratio_all - 1.0) > 0.02 or abs(ratio_e1 - 1.0) > 0.02:
        print(f"  {r:2d}   {ratio_all:7.4f}  {ratio_e1:7.4f}  {ratio_e15:7.4f}  v2={v2_val}")

# v2=4 集約
print("\nv2=4 ratio:")
v2_4_residues = [r for r in odd_res if v2(3*r+1) == 4]
for label, freq_d, tot_d in [("all", freq_all, tot_all), ("excl1", freq_e1, tot_e1), ("excl1,5", freq_e15, tot_e15)]:
    mu_v2_4 = sum(freq_d[r] for r in v2_4_residues) / tot_d
    ratio = mu_v2_4 / (1/16)
    print(f"  {label:8s}: mu(v2=4) = {mu_v2_4:.6f}, ratio = {ratio:.4f}")

# 4d: truncation実験
print("\n軌道truncation実験 (mod 32):")
print(f"{'max_steps':>10} {'L2_dev':>10} {'v2_4_ratio':>12}")
for max_s in [3, 5, 10, 20, 50, 100, 500]:
    freq_t, tot_t = compute_measure_first_k_steps(20000, 5, max_s)
    if tot_t == 0:
        continue
    uniform_val = tot_t / 16
    l2 = 0
    mu_v2_4 = sum(freq_t[r] for r in v2_4_residues) / tot_t
    for r in odd_res:
        ratio_r = freq_t[r] / uniform_val
        l2 += (ratio_r - 1.0) ** 2
    l2 = math.sqrt(l2 / 16)
    v2_4_r = mu_v2_4 / (1/16)
    print(f"  {max_s:8d}   {l2:10.6f}   {v2_4_r:12.4f}")


# ============================================================
# Part 5: Tao的mixing解釈 - 非一様性のk依存性
# ============================================================

print("\n" + "=" * 60)
print("Part 5: 非一様性のk依存性（Tao mixing rate）")
print("=" * 60)

nonunif_data = {}
for k in range(2, 9):
    freq, total = compute_orbit_measure(min(N_MAX, 10000 * (k-1)), k)
    mod = 2 ** k
    odd_res_k = [r for r in range(mod) if r % 2 == 1]
    uniform_val = total / len(odd_res_k)

    max_ratio = 0
    min_ratio = float('inf')
    l2 = 0

    for r in odd_res_k:
        ratio_r = freq[r] / uniform_val if uniform_val > 0 else 0
        max_ratio = max(max_ratio, ratio_r)
        min_ratio = min(min_ratio, ratio_r)
        l2 += (ratio_r - 1.0) ** 2

    l2 = math.sqrt(l2 / len(odd_res_k))
    nonunif_data[k] = {"max": max_ratio, "min": min_ratio, "l2": l2}
    print(f"  k={k:2d} (mod {mod:4d}): max_ratio={max_ratio:.4f}, min_ratio={min_ratio:.4f}, L2_dev={l2:.6f}")

# L2 スケーリング
print("\nL2偏差のスケーリング（k -> k+1）:")
for k in range(3, 9):
    if k-1 in nonunif_data and k in nonunif_data:
        r = nonunif_data[k]["l2"] / nonunif_data[k-1]["l2"] if nonunif_data[k-1]["l2"] > 0 else 0
        print(f"  k={k-1}->{k}: ratio = {r:.4f}")


# ============================================================
# Part 6: 閉公式の探索
# ============================================================

print("\n" + "=" * 60)
print("Part 6: mu_k(r) の閉公式探索")
print("=" * 60)

# mod 4 (k=2) の場合: 奇数residue = {1, 3}
# v2(3*1+1)=2, v2(3*3+1)=1
# Syracuse(1) = 1, Syracuse(3) = 5 ≡ 1 (mod 4)
# mod 4 での遷移: 1->1, 3->1 (全て1に行く)
# → 定常分布は pi(1)=1, pi(3)=0 か？
# いいえ、軌道測度は初期値分布にも依存

# mod 8 (k=3): 奇数 = {1,3,5,7}
# Syracuse: 1->1(v2=2), 3->5(v2=1), 5->1(v2=4), 7->11≡3(v2=1)
k3 = all_measures[3]
print("\nmod 8:")
for r, data in sorted(k3["measure"].items()):
    print(f"  r={r}: mu={data['mu']:.6f}, ratio={data['ratio']:.4f}")
    # Syracuse(r) mod 8
    s = syracuse(r)
    print(f"         Syracuse({r}) = {s}, mod 8 = {s % 8}")

# mod 4
k2 = all_measures[2]
print("\nmod 4:")
for r, data in sorted(k2["measure"].items()):
    print(f"  r={r}: mu={data['mu']:.6f}, ratio={data['ratio']:.4f}")

# mod 16 (k=4)
k4 = all_measures[4]
print("\nmod 16:")
for r, data in sorted(k4["measure"].items()):
    s = syracuse(r)
    print(f"  r={r:2d}: mu={data['mu']:.6f}, ratio={data['ratio']:.4f}, Syr({r:2d})={s:3d} mod16={s%16:2d}")


# ============================================================
# Part 7: 不変測度の解析的構造
# ============================================================

print("\n" + "=" * 60)
print("Part 7: 不変測度の再帰構造")
print("=" * 60)

# mod 2^k での不変測度 mu は T_*mu = mu を満たすべき
# T: Syracuse写像
# mu(A) = sum_{r: T(r) in A} mu(pre(A))
# だが軌道測度は「有限軌道の平均」であり、真の不変測度とは異なる

# 代わりに「頻度行列」の構造を見る
# 各 r -> Syracuse(r) mod 2^k の対応

for k in [3, 4, 5]:
    mod = 2 ** k
    odd_res = sorted([r for r in range(mod) if r % 2 == 1])

    print(f"\n--- mod {mod} Syracuse グラフ ---")
    # 各residueのSyracuse像（複数のリフトの統計）
    for r in odd_res:
        # 最も頻出のSyracuse像
        targets = Counter()
        for lift in range(500):
            x = r + lift * mod
            if x > 0:
                y = syracuse(x)
                targets[y % mod] += 1
        # 上位の遷移先
        top = targets.most_common(3)
        total = sum(targets.values())
        desc = ", ".join([f"{t}({c/total:.2f})" for t, c in top])
        print(f"  {r:3d} -> {desc}")


# ============================================================
# Part 8: r=1 のアトラクター効果の定量化
# ============================================================

print("\n" + "=" * 60)
print("Part 8: r=1 アトラクター効果とv2=4の関係")
print("=" * 60)

# r=1 (mod 2^k) は不動点。軌道が1に到達すると永遠に留まる。
# → 軌道測度では r=1 が過大表現される。
# → r=1 を「sink」として除外した測度を計算

# 軌道の最後のステップ（=1）を除いた場合
def compute_measure_no_sink(N_max, k):
    """sinkステップ（1に留まる）を除外"""
    mod = 2 ** k
    freq = Counter()
    total = 0

    for n0 in range(3, N_max + 1, 2):
        orbit = collatz_orbit_odd(n0)
        # 最後のステップ（1）を除く
        for x in orbit[:-1]:
            freq[x % mod] += 1
            total += 1

    return freq, total

freq_ns, tot_ns = compute_measure_no_sink(20000, 5)
print("\nmod 32: sink除外 vs 通常")
v2_agg = defaultdict(lambda: {"ns": 0, "all": 0})

for r in sorted(odd_res):
    ratio_all = (freq_all[r] / tot_all) * 16
    ratio_ns = (freq_ns[r] / tot_ns) * 16 if tot_ns > 0 else 0
    v_val = v2(3*r + 1)
    v2_agg[v_val]["ns"] += freq_ns[r]
    v2_agg[v_val]["all"] += freq_all[r]
    if abs(ratio_all - ratio_ns) > 0.02:
        print(f"  r={r:2d}: all={ratio_all:.4f}, no_sink={ratio_ns:.4f}, diff={ratio_ns-ratio_all:+.4f}, v2={v_val}")

print("\nv2集約 (sink除外):")
for vv in sorted(v2_agg.keys()):
    theory = 1.0 / (2**vv)
    mu_all = v2_agg[vv]["all"] / tot_all
    mu_ns = v2_agg[vv]["ns"] / tot_ns if tot_ns > 0 else 0
    print(f"  v2={vv}: all_ratio={mu_all/theory:.4f}, no_sink_ratio={mu_ns/theory:.4f}")


# ============================================================
# Part 9: Tao理論との接続 - 対数密度的測度
# ============================================================

print("\n" + "=" * 60)
print("Part 9: 対数密度的軌道測度")
print("=" * 60)

# Taoは「対数密度」を使用: sum_{n<=N, P(n)} 1/n
# 軌道測度も 1/n 重みを付けた場合にどう変わるか

def compute_log_weighted_measure(N_max, k):
    """1/n 重み付き軌道測度"""
    mod = 2 ** k
    freq = defaultdict(float)
    total = 0.0

    for n0 in range(3, N_max + 1, 2):
        orbit = collatz_orbit_odd(n0)
        for x in orbit:
            w = 1.0 / x if x > 0 else 0
            freq[x % mod] += w
            total += w

    return freq, total

freq_log, tot_log = compute_log_weighted_measure(20000, 5)

print("\nmod 32: 通常 vs 1/n重み付き")
print(f"{'r':>3} {'uniform':>10} {'log_weighted':>13} {'diff':>8}")
for r in sorted(odd_res):
    ratio_u = (freq_all[r] / tot_all) * 16
    ratio_l = (freq_log[r] / tot_log) * 16 if tot_log > 0 else 0
    if abs(ratio_u - 1.0) > 0.02 or abs(ratio_l - 1.0) > 0.02:
        print(f"  {r:2d}   {ratio_u:10.4f}   {ratio_l:13.4f}   {ratio_l-ratio_u:+7.4f}")

# v2=4 の比較
v2_4_log = sum(freq_log[r] for r in v2_4_residues) / tot_log if tot_log > 0 else 0
v2_4_unif = sum(freq_all[r] for r in v2_4_residues) / tot_all if tot_all > 0 else 0
print(f"\nv2=4: uniform_weight={v2_4_unif/(1/16):.4f}, log_weight={v2_4_log/(1/16):.4f}")


# ============================================================
# 結果の集約
# ============================================================

print("\n" + "=" * 60)
print("結果サマリー")
print("=" * 60)

# 核心的な数値を集める
mod32_key_ratios = {}
for r in sorted(odd_res):
    data = all_measures[5]["measure"][r]
    mod32_key_ratios[str(r)] = round(data["ratio"], 4)

v2_ratios = {}
for k in [5, 6, 7]:
    m = all_measures[k]
    v2_mu_k = defaultdict(float)
    for r, data in m["measure"].items():
        v2_mu_k[data["v2_3r1"]] += data["mu"]
    for vv in sorted(v2_mu_k.keys()):
        if vv <= k:
            theory = 1.0 / (2**vv)
            v2_ratios[f"k={k},v2={vv}"] = round(v2_mu_k[vv] / theory, 4)

# JSON出力
result = {
    "title": "軌道不変測度のmod 2^k表現: Tao ergodic approachとの接続",
    "approach": "コラッツ軌道上のmod 2^k頻度分布mu_k(r)を大規模計算し、Syracuse遷移行列定常分布、終端効果(sink除外)、truncation、対数重み測度と比較。Taoのmixing理論との接続を定量化。",
    "mod32_orbit_measure_ratios": mod32_key_ratios,
    "v2_distribution_ratios": v2_ratios,
    "nonuniformity_scaling": {str(k): round(v["l2"], 6) for k, v in nonunif_data.items()},
    "key_numbers": {
        "v2_4_ratio_full": round(v2_4_unif / (1/16), 4),
        "v2_4_ratio_excl1": None,  # 後で更新
        "v2_4_ratio_excl15": None,
        "v2_4_ratio_log_weighted": round(v2_4_log / (1/16), 4)
    }
}

# excl1, excl15 の v2=4
v2_4_e1 = sum(freq_e1[r] for r in v2_4_residues) / tot_e1 if tot_e1 > 0 else 0
v2_4_e15 = sum(freq_e15[r] for r in v2_4_residues) / tot_e15 if tot_e15 > 0 else 0
result["key_numbers"]["v2_4_ratio_excl1"] = round(v2_4_e1 / (1/16), 4)
result["key_numbers"]["v2_4_ratio_excl15"] = round(v2_4_e15 / (1/16), 4)

with open("results/orbit_invariant_measure_mod2k.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n結果を results/orbit_invariant_measure_mod2k.json に保存")
print(json.dumps(result["key_numbers"], indent=2))
print(json.dumps(result["nonuniformity_scaling"], indent=2))
