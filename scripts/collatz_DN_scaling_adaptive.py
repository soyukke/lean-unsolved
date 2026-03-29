"""
D(N) スケーリング分析 - 適応的計算版
まずN=10^8を目標とし、速度に応じて拡張する。

高速化戦略:
1. メモ化テーブル (n < 10M)
2. bitwise 最適化
3. 漸進的計算 + 途中結果保存
"""

import math
import time
import json

# ===== 高速 stopping time =====
CACHE_SIZE = 5_000_000
cache = bytearray(CACHE_SIZE * 2)  # uint16 で格納 (最大65535)

def st_to_bytes(val):
    return (val & 0xFF, (val >> 8) & 0xFF)

def bytes_to_st(b0, b1):
    return b0 | (b1 << 8)

def cache_get(n):
    if n < CACHE_SIZE:
        idx = n * 2
        return bytes_to_st(cache[idx], cache[idx+1])
    return 0

def cache_set(n, val):
    if n < CACHE_SIZE and val < 65536:
        idx = n * 2
        cache[idx] = val & 0xFF
        cache[idx+1] = (val >> 8) & 0xFF

# 初期値セット
cache_set(1, 0)

def stopping_time(n):
    """高速 stopping time with memoization"""
    orig_n = n
    steps = 0
    trail = []

    while n > 1:
        if n < CACHE_SIZE:
            cached = cache_get(n)
            if cached > 0 or n == 1:
                steps += cached
                break
        trail.append((n, steps))
        if n & 1 == 0:
            n >>= 1
            steps += 1
        else:
            n = (3 * n + 1) >> 1  # 3n+1 は常に偶数なので一気に /2
            steps += 2

    # write back
    for prev_n, prev_steps in trail:
        total = steps - prev_steps
        if prev_n < CACHE_SIZE and total < 65536:
            cache_set(prev_n, total)

    return steps

# ===== ウォームアップ =====
print("ウォームアップ (n=1..5M)...", flush=True)
t0 = time.time()
max_st_warmup = 0
for n in range(2, CACHE_SIZE):
    st = stopping_time(n)
    if st > max_st_warmup:
        max_st_warmup = st
print(f"完了: {time.time()-t0:.1f}秒, max ST(1..5M) = {max_st_warmup}", flush=True)

# ===== D(N) 計算 =====
# チェックポイント
checkpoints = set()
for k in range(30, 91):
    checkpoints.add(int(round(10**(k/10.0))))
for k in range(3, 10):
    checkpoints.add(10**k)
# 追加のチェックポイント (10^7.5, 10^8.5 等)
for k_half in range(60, 181, 5):  # 10^(k/20) for k=60..180 (10^3..10^9)
    checkpoints.add(int(round(10**(k_half/20.0))))

checkpoints = sorted(checkpoints)

# 段階的に計算
targets = [10**7, 5*10**7, 10**8, 2*10**8, 5*10**8, 10**9]
DN_results = {}
record_holders = []
current_max_st = max_st_warmup  # ウォームアップの結果を引き継ぐ
prev_n = CACHE_SIZE

# ウォームアップ範囲のチェックポイントを埋める
warmup_max = 0
for cp in checkpoints:
    if cp < CACHE_SIZE:
        # キャッシュからmax STを再計算
        local_max = 0
        for nn in range(1, cp+1):
            st = stopping_time(nn)
            if st > local_max:
                local_max = st
        DN_results[cp] = local_max
    else:
        break

# ウォームアップ範囲のrecord holders再構築
print("Record holders再構築 (n=1..5M)...", flush=True)
t0 = time.time()
rm = 0
for n in range(1, CACHE_SIZE):
    st = stopping_time(n)
    if st > rm:
        rm = st
        record_holders.append((n, st))
current_max_st = rm
# ウォームアップ範囲のチェックポイント
cp_idx = 0
for cp in checkpoints:
    if cp < CACHE_SIZE:
        DN_results[cp] = rm if cp >= record_holders[-1][0] else 0

# 正確にチェックポイント値を計算
rm2 = 0
sorted_cps_small = sorted([cp for cp in checkpoints if cp < CACHE_SIZE])
cp_ptr = 0
for n in range(1, CACHE_SIZE):
    st = stopping_time(n)
    if st > rm2:
        rm2 = st
    while cp_ptr < len(sorted_cps_small) and sorted_cps_small[cp_ptr] == n:
        DN_results[sorted_cps_small[cp_ptr]] = rm2
        cp_ptr += 1

print(f"完了: {time.time()-t0:.1f}秒", flush=True)

# 大きい N の計算
print(f"\n大規模計算開始 (N={CACHE_SIZE:,} .. targets)", flush=True)
t_start = time.time()

sorted_cps_big = sorted([cp for cp in checkpoints if cp >= CACHE_SIZE])
cp_ptr_big = 0

for target_N in targets:
    if target_N < CACHE_SIZE:
        continue

    start_n = max(CACHE_SIZE, prev_n + 1)
    if start_n > target_N:
        continue

    t_seg = time.time()
    for n in range(start_n, target_N + 1):
        st = stopping_time(n)
        if st > current_max_st:
            current_max_st = st
            record_holders.append((n, st))

        while cp_ptr_big < len(sorted_cps_big) and sorted_cps_big[cp_ptr_big] == n:
            DN_results[sorted_cps_big[cp_ptr_big]] = current_max_st
            cp_ptr_big += 1

    elapsed_seg = time.time() - t_seg
    elapsed_total = time.time() - t_start
    rate = (target_N - start_n + 1) / elapsed_seg if elapsed_seg > 0 else 0
    print(f"  N={target_N:>14,}: D(N)={current_max_st:>6}, "
          f"segment={elapsed_seg:>7.1f}s, total={elapsed_total:>7.1f}s, "
          f"rate={rate:,.0f}/s", flush=True)

    prev_n = target_N

    # 10分超えたら打ち切り
    if elapsed_total > 540:
        print(f"  時間切れ (>540s)。ここまでの結果で分析します。", flush=True)
        break

total_time = time.time() - t_start
actual_N_max = prev_n

# ===== 分析 =====
print("\n" + "=" * 90)
print(f"分析 (実効 N_max = {actual_N_max:,})")
print("=" * 90)

# 有効なチェックポイントのみ
Ns = sorted([n for n in DN_results.keys() if n <= actual_N_max and DN_results[n] > 0])
DNs = [DN_results[n] for n in Ns]
logNs = [math.log(n) for n in Ns]
logDNs = [math.log(d) for d in DNs]
loglogNs = [math.log(ln) for ln in logNs]

# テーブル表示
print(f"\n{'N':>16} {'D(N)':>8} {'logN':>8} {'loglogN':>8} "
      f"{'D/(logN)^1.5':>14} {'D/(logN)^1.6':>14} {'D/(logN)^1.7':>14}")
print("-" * 100)
for i in range(len(Ns)):
    n = Ns[i]
    d = DNs[i]
    ln = logNs[i]
    lln = loglogNs[i]
    # 主要ポイントのみ表示
    if n in [10**k for k in range(3,10)] or n in targets or (i % max(1, len(Ns)//20) == 0):
        print(f"{n:>16,} {d:>8} {ln:>8.3f} {lln:>8.4f} "
              f"{d/ln**1.5:>14.4f} {d/ln**1.6:>14.4f} {d/ln**1.7:>14.4f}")

# ===== 統計 =====
def mean(xs):
    return sum(xs) / len(xs) if xs else 0

def std(xs):
    if len(xs) < 2: return 0
    m = mean(xs)
    return math.sqrt(sum((x - m)**2 for x in xs) / len(xs))

def linear_regression(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sxx = sum((x - mx)**2 for x in xs)
    if sxx == 0: return my, 0.0
    b = sxy / sxx
    a = my - b * mx
    return a, b

def pearson_r(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx)**2 for x in xs))
    dy = math.sqrt(sum((y - my)**2 for y in ys))
    return num / (dx * dy) if dx > 0 and dy > 0 else 0

# モデル1: D(N) = C * (logN)^alpha
a1, b1 = linear_regression(loglogNs, logDNs)
alpha1 = b1; C1 = math.exp(a1)
r1 = pearson_r(loglogNs, logDNs)

print(f"\n=== モデル1: D(N) = C*(logN)^alpha ===")
print(f"全データ: alpha = {alpha1:.4f}, C = {C1:.4f}, R^2 = {r1**2:.6f}")

# alpha の安定性
print(f"\n--- alpha の安定性 ---")
print(f"{'N_min':>16} {'N_max':>16} {'alpha':>8} {'R^2':>10} {'pts':>6}")
print("-" * 60)
stability_results = {}
for N_min_exp in [3.0, 4.0, 5.0, 6.0, 7.0, 7.5, 8.0, 8.5]:
    N_min_val = int(10**N_min_exp)
    idx = [i for i in range(len(Ns)) if Ns[i] >= N_min_val]
    if len(idx) < 4: continue
    sub_x = [loglogNs[i] for i in idx]
    sub_y = [logDNs[i] for i in idx]
    a, b = linear_regression(sub_x, sub_y)
    r = pearson_r(sub_x, sub_y)
    stability_results[N_min_exp] = b
    print(f"{N_min_val:>16,} {Ns[-1]:>16,} {b:>8.4f} {r**2:>10.6f} {len(idx):>6}")

# モデル2: N^gamma
a2, b2 = linear_regression(logNs, logDNs)
gamma2 = b2; C2 = math.exp(a2)
r2 = pearson_r(logNs, logDNs)
print(f"\n=== モデル2: D(N) = C*N^gamma ===")
print(f"全データ: gamma = {gamma2:.6f}, C = {C2:.4f}, R^2 = {r2**2:.6f}")

# 局所 alpha
local_alphas = []
for i in range(1, len(Ns)):
    d_logD = logDNs[i] - logDNs[i-1]
    d_loglogN = loglogNs[i] - loglogNs[i-1]
    if abs(d_loglogN) > 1e-10 and d_logD > 0:
        local_alphas.append((Ns[i], d_logD / d_loglogN))

window = 7
smoothed_a = []
for i in range(window, len(local_alphas)):
    vals = [a[1] for a in local_alphas[i-window:i]]
    smoothed_a.append((local_alphas[i][0], mean(vals)))

print(f"\n=== 局所 alpha_local (移動平均 window={window}) ===")
if smoothed_a:
    # 10^k 近辺の値
    for s_n, s_a in smoothed_a:
        logn = math.log10(s_n)
        if abs(logn - round(logn)) < 0.15 or s_n == smoothed_a[-1][0]:
            print(f"  N ~ 10^{logn:.1f}: alpha_local = {s_a:.4f}")

    last_vals = [a[1] for a in smoothed_a[-10:]]
    print(f"\n  最後10点: mean={mean(last_vals):.4f}, std={std(last_vals):.4f}")

# CV最小化
def cv_ratio(alpha, indices=None):
    if indices is None:
        indices = range(len(Ns))
    ratios = [DNs[i] / logNs[i]**alpha for i in indices]
    m = mean(ratios)
    s = std(ratios)
    return s / m if m > 0 else float('inf')

best_alpha_cv = 1.0; best_cv = float('inf')
for ax100 in range(100, 300):
    a_test = ax100 / 100.0
    cv = cv_ratio(a_test)
    if cv < best_cv: best_cv = cv; best_alpha_cv = a_test
for ax1000 in range(int((best_alpha_cv-0.1)*1000), int((best_alpha_cv+0.1)*1000)+1):
    a_test = ax1000 / 1000.0
    cv = cv_ratio(a_test)
    if cv < best_cv: best_cv = cv; best_alpha_cv = a_test

print(f"\n=== CV最小化 ===")
print(f"最適 alpha (全データ) = {best_alpha_cv:.3f}, CV = {best_cv:.4f}")

# N>=10^6 の部分でCV
big_idx = [i for i in range(len(Ns)) if Ns[i] >= 10**6]
best_alpha_big = 1.0; best_cv_big = float('inf')
for ax100 in range(100, 300):
    a_test = ax100 / 100.0
    cv = cv_ratio(a_test, big_idx)
    if cv < best_cv_big: best_cv_big = cv; best_alpha_big = a_test
for ax1000 in range(int((best_alpha_big-0.1)*1000), int((best_alpha_big+0.1)*1000)+1):
    a_test = ax1000 / 1000.0
    cv = cv_ratio(a_test, big_idx)
    if cv < best_cv_big: best_cv_big = cv; best_alpha_big = a_test

print(f"最適 alpha (N>=10^6) = {best_alpha_big:.3f}, CV = {best_cv_big:.4f}")

# D(10^k) ペアからの alpha
dk_vals = {}
for k in range(3, 10):
    N = 10**k
    if N in DN_results and DN_results[N] > 0:
        dk_vals[k] = DN_results[N]

print(f"\n=== D(10^k) ペア alpha 推定 ===")
print(f"{'pair':>10} {'alpha':>10}")
print("-" * 22)
dk_keys = sorted(dk_vals.keys())
for i in range(len(dk_keys)-1):
    k1, k2 = dk_keys[i], dk_keys[-1]
    d1, d2 = dk_vals[k1], dk_vals[k2]
    logN1 = k1 * math.log(10)
    logN2 = k2 * math.log(10)
    if d2 > d1:
        alpha_est = math.log(d2/d1) / math.log(logN2/logN1)
        print(f"  {k1}-{k2}: {alpha_est:>10.4f}")

# Record holders
print(f"\n=== Record holders (最後20件, 合計{len(record_holders)}件) ===")
print(f"{'n':>16} {'ST':>8} {'logn':>8} {'ST/(logn)^1.6':>16}")
for nn, st in record_holders[-20:]:
    ln = math.log(nn)
    print(f"{nn:>16,} {st:>8} {ln:>8.3f} {st/ln**1.6:>16.4f}")

# ===== JSON =====
output = {
    "actual_N_max": actual_N_max,
    "computation_time_sec": round(total_time, 1),
    "num_checkpoints": len(Ns),
    "num_record_holders": len(record_holders),
    "DN_at_powers_of_10": {str(k): dk_vals[k] for k in dk_vals},
    "model1_log_power": {
        "alpha": round(alpha1, 4),
        "C": round(C1, 4),
        "R2": round(r1**2, 6)
    },
    "model2_N_power": {
        "gamma": round(gamma2, 6),
        "C": round(C2, 4),
        "R2": round(r2**2, 6)
    },
    "alpha_stability": {f"N_ge_1e{k}": round(v, 4) for k, v in stability_results.items()},
    "optimal_alpha_cv_all": round(best_alpha_cv, 3),
    "optimal_alpha_cv_big": round(best_alpha_big, 3),
    "local_alpha_last10": {
        "mean": round(mean([a[1] for a in smoothed_a[-10:]]), 4) if smoothed_a else None,
        "std": round(std([a[1] for a in smoothed_a[-10:]]), 4) if smoothed_a else None,
    },
    "last_record_holder": {
        "n": record_holders[-1][0],
        "ST": record_holders[-1][1]
    } if record_holders else None,
    "alpha_pair_estimates": {},
}

for i in range(len(dk_keys)-1):
    k1, k2 = dk_keys[i], dk_keys[-1]
    d1, d2 = dk_vals[k1], dk_vals[k2]
    logN1 = k1 * math.log(10)
    logN2 = k2 * math.log(10)
    if d2 > d1:
        output["alpha_pair_estimates"][f"{k1}-{k2}"] = round(
            math.log(d2/d1) / math.log(logN2/logN1), 4)

json_path = "/Users/soyukke/study/lean-unsolved/results/DN_scaling_large.json"
with open(json_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nJSON保存: {json_path}")
