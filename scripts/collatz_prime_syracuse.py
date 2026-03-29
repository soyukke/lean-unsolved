#!/usr/bin/env python3
"""
素数 p の Syracuse 軌道の統計的特殊性を調査する。
stopping time, peak value, v2(2-adic valuation)列を素数 vs 非素数で比較。
mod構造の差異を分析。
"""
import math
import json
from collections import Counter, defaultdict

# === 素数判定 ===
def sieve_primes(limit):
    """エラトステネスの篩"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

# === コラッツ関数 ===
def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def syracuse(n):
    """Syracuse map: T(n) = collatz applied until odd"""
    if n % 2 == 0:
        raise ValueError("Syracuse is defined on odd numbers")
    x = 3 * n + 1
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return x, v

def full_orbit(n, max_steps=10000):
    """完全なコラッツ軌道を返す"""
    orbit = [n]
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x = collatz_step(x)
        orbit.append(x)
    return orbit

def syracuse_orbit(n, max_steps=5000):
    """Syracuse軌道（奇数のみ）とv2列を返す"""
    if n % 2 == 0:
        return [], []
    odds = [n]
    v2s = []
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x_next, v = syracuse(x)
        v2s.append(v)
        odds.append(x_next)
        x = x_next
    return odds, v2s

def stopping_time(n):
    """n が初めて n 未満になるまでのステップ数"""
    x = n
    steps = 0
    while x >= n and x != 1:
        x = collatz_step(x)
        steps += 1
        if steps > 10000:
            return -1
    return steps

def total_stopping_time(n):
    """n が 1 に到達するまでの総ステップ数"""
    x = n
    steps = 0
    while x != 1:
        x = collatz_step(x)
        steps += 1
        if steps > 100000:
            return -1
    return steps

def peak_value(n):
    """軌道中の最大値"""
    x = n
    peak = n
    while x != 1:
        x = collatz_step(x)
        peak = max(peak, x)
        if x > 10**18:
            return peak
    return peak

# === 統計計算 ===
def compute_stats(values):
    if not values:
        return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0}
    n = len(values)
    mean = sum(values) / n
    sorted_v = sorted(values)
    median = sorted_v[n // 2]
    variance = sum((v - mean)**2 for v in values) / n if n > 1 else 0
    std = variance ** 0.5
    return {
        "mean": round(mean, 4),
        "median": median,
        "std": round(std, 4),
        "min": min(values),
        "max": max(values),
        "count": n
    }

# =============================================
# 実験1: stopping time と total stopping time の比較
# =============================================
print("=" * 70)
print("実験1: 素数 vs 非素数(奇数)の stopping time 比較")
print("=" * 70)

LIMIT = 10000
is_prime = sieve_primes(LIMIT)

prime_st = []
composite_st = []
prime_tst = []
composite_tst = []
prime_peaks = []
composite_peaks = []

for n in range(3, LIMIT + 1, 2):  # 奇数のみ
    st = stopping_time(n)
    tst = total_stopping_time(n)
    pk = peak_value(n)

    if is_prime[n]:
        prime_st.append(st)
        prime_tst.append(tst)
        prime_peaks.append(pk)
    else:
        composite_st.append(st)
        composite_tst.append(tst)
        composite_peaks.append(pk)

print(f"\n素数(奇数): {len(prime_st)}個, 奇数合成数: {len(composite_st)}個")
print(f"\n--- Stopping Time ---")
print(f"素数:     {compute_stats(prime_st)}")
print(f"合成数:   {compute_stats(composite_st)}")
print(f"\n--- Total Stopping Time ---")
print(f"素数:     {compute_stats(prime_tst)}")
print(f"合成数:   {compute_stats(composite_tst)}")
print(f"\n--- Peak Value (log2) ---")
prime_log_peaks = [math.log2(p) if p > 0 else 0 for p in prime_peaks]
comp_log_peaks = [math.log2(p) if p > 0 else 0 for p in composite_peaks]
print(f"素数:     {compute_stats(prime_log_peaks)}")
print(f"合成数:   {compute_stats(comp_log_peaks)}")

# =============================================
# 実験2: v2列（2-adic valuation列）の比較
# =============================================
print("\n" + "=" * 70)
print("実験2: Syracuse軌道のv2列の分布比較")
print("=" * 70)

prime_v2_all = []
composite_v2_all = []
prime_v2_first5 = defaultdict(list)
composite_v2_first5 = defaultdict(list)

for n in range(3, LIMIT + 1, 2):
    odds, v2s = syracuse_orbit(n)
    if is_prime[n]:
        prime_v2_all.extend(v2s)
        for i, v in enumerate(v2s[:10]):
            prime_v2_first5[i].append(v)
    else:
        composite_v2_all.extend(v2s)
        for i, v in enumerate(v2s[:10]):
            composite_v2_first5[i].append(v)

print(f"\nv2全体の分布:")
prime_v2_counter = Counter(prime_v2_all)
comp_v2_counter = Counter(composite_v2_all)
prime_v2_total = len(prime_v2_all)
comp_v2_total = len(composite_v2_all)

print(f"{'v2':>4} | {'素数 freq':>12} | {'合成数 freq':>12} | {'理論値 2^(-k)':>14}")
print("-" * 50)
for k in range(1, 12):
    p_freq = prime_v2_counter.get(k, 0) / prime_v2_total if prime_v2_total > 0 else 0
    c_freq = comp_v2_counter.get(k, 0) / comp_v2_total if comp_v2_total > 0 else 0
    theory = 2**(-k)
    print(f"{k:>4} | {p_freq:>12.6f} | {c_freq:>12.6f} | {theory:>14.6f}")

# v2列の最初の数ステップでの差
print(f"\n最初の10ステップにおけるv2の平均:")
print(f"{'Step':>6} | {'素数 mean':>12} | {'合成数 mean':>12} | {'差':>10}")
print("-" * 50)
for i in range(10):
    p_vals = prime_v2_first5[i]
    c_vals = composite_v2_first5[i]
    if p_vals and c_vals:
        p_mean = sum(p_vals) / len(p_vals)
        c_mean = sum(c_vals) / len(c_vals)
        print(f"{i+1:>6} | {p_mean:>12.4f} | {c_mean:>12.4f} | {p_mean - c_mean:>10.4f}")

# =============================================
# 実験3: mod 構造による分類
# =============================================
print("\n" + "=" * 70)
print("実験3: mod 8, mod 16 での素数/合成数の stopping time 分布")
print("=" * 70)

# mod 8 での分類
for mod_val in [8, 16]:
    print(f"\n--- mod {mod_val} ---")
    prime_by_mod = defaultdict(list)
    comp_by_mod = defaultdict(list)

    for n in range(3, LIMIT + 1, 2):
        r = n % mod_val
        st = stopping_time(n)
        if is_prime[n]:
            prime_by_mod[r].append(st)
        else:
            comp_by_mod[r].append(st)

    print(f"{'r':>4} | {'P count':>8} | {'P mean ST':>10} | {'C count':>8} | {'C mean ST':>10} | {'差':>8}")
    print("-" * 60)
    for r in sorted(set(list(prime_by_mod.keys()) + list(comp_by_mod.keys()))):
        if r % 2 == 0:
            continue
        p_vals = prime_by_mod[r]
        c_vals = comp_by_mod[r]
        p_mean = sum(p_vals) / len(p_vals) if p_vals else 0
        c_mean = sum(c_vals) / len(c_vals) if c_vals else 0
        diff = p_mean - c_mean if p_vals and c_vals else float('nan')
        print(f"{r:>4} | {len(p_vals):>8} | {p_mean:>10.2f} | {len(c_vals):>8} | {c_mean:>10.2f} | {diff:>8.2f}")

# =============================================
# 実験4: 素数の末尾ビットパターンと軌道の関係
# =============================================
print("\n" + "=" * 70)
print("実験4: 末尾kビットパターンとstopping timeの関係")
print("=" * 70)

for k_bits in [3, 4, 5]:
    mod = 2**k_bits
    pattern_prime = defaultdict(list)
    pattern_comp = defaultdict(list)

    for n in range(3, LIMIT + 1, 2):
        pattern = n % mod
        st = stopping_time(n)
        if is_prime[n]:
            pattern_prime[pattern].append(st)
        else:
            pattern_comp[pattern].append(st)

    print(f"\n--- 末尾 {k_bits} ビット (mod {mod}) ---")
    # 素数と合成数のST差が大きいパターンを見つける
    diffs = []
    for pattern in sorted(pattern_prime.keys()):
        if pattern in pattern_comp and len(pattern_prime[pattern]) >= 5 and len(pattern_comp[pattern]) >= 5:
            p_mean = sum(pattern_prime[pattern]) / len(pattern_prime[pattern])
            c_mean = sum(pattern_comp[pattern]) / len(pattern_comp[pattern])
            diffs.append((pattern, p_mean, c_mean, p_mean - c_mean, len(pattern_prime[pattern]), len(pattern_comp[pattern])))

    diffs.sort(key=lambda x: abs(x[3]), reverse=True)
    print(f"{'Pattern':>8} | {'P mean':>8} | {'C mean':>8} | {'差':>8} | {'P#':>5} | {'C#':>5}")
    print("-" * 55)
    for pat, pm, cm, d, pn, cn in diffs[:10]:
        bits = bin(pat)[2:].zfill(k_bits)
        print(f"{bits:>8} | {pm:>8.2f} | {cm:>8.2f} | {d:>8.2f} | {pn:>5} | {cn:>5}")

# =============================================
# 実験5: 素数 p と 3p, 5p, 7p の軌道比較
# =============================================
print("\n" + "=" * 70)
print("実験5: 素数 p と kp (k=3,5,7,9) の軌道比較")
print("=" * 70)

print(f"\n{'p':>8} | {'ST(p)':>8} | {'ST(3p)':>8} | {'ST(5p)':>8} | {'ST(7p)':>8} | {'ST(9p)':>8}")
print("-" * 60)

# 小さい素数で個別調査
primes_list = [p for p in range(3, 200) if is_prime[p]]
for p in primes_list[:20]:
    vals = [stopping_time(p)]
    for k in [3, 5, 7, 9]:
        kp = k * p
        if kp % 2 == 1:
            vals.append(stopping_time(kp))
        else:
            vals.append(-1)  # 偶数の場合
    print(f"{p:>8} | {vals[0]:>8} | {vals[1]:>8} | {vals[2]:>8} | {vals[3]:>8} | {vals[4]:>8}")

# =============================================
# 実験6: Syracuse 軌道中の素数の出現頻度
# =============================================
print("\n" + "=" * 70)
print("実験6: Syracuse軌道中に素数が出現する頻度")
print("=" * 70)

prime_in_orbit_prime = []
prime_in_orbit_comp = []

for n in range(3, 2000, 2):
    odds, v2s = syracuse_orbit(n)
    if len(odds) < 2:
        continue
    prime_count = sum(1 for x in odds[1:] if x < LIMIT + 1 and is_prime[x])
    ratio = prime_count / len(odds[1:]) if len(odds) > 1 else 0

    if is_prime[n]:
        prime_in_orbit_prime.append(ratio)
    else:
        prime_in_orbit_comp.append(ratio)

print(f"素数出発:   素数出現率の平均 = {sum(prime_in_orbit_prime)/len(prime_in_orbit_prime):.6f} ({len(prime_in_orbit_prime)}サンプル)")
print(f"合成数出発: 素数出現率の平均 = {sum(prime_in_orbit_comp)/len(prime_in_orbit_comp):.6f} ({len(prime_in_orbit_comp)}サンプル)")

# =============================================
# 実験7: 同一 mod 残基内での精密比較
# =============================================
print("\n" + "=" * 70)
print("実験7: mod 24 で同一残基内の素数 vs 合成数")
print("=" * 70)

# mod 24 は素数の分布で意味がある (24 = 2^3 * 3)
for mod_val in [24, 120]:
    print(f"\n--- mod {mod_val} ---")
    residues = defaultdict(lambda: {"prime_st": [], "comp_st": [], "prime_tst": [], "comp_tst": []})

    for n in range(3, LIMIT + 1, 2):
        r = n % mod_val
        st = stopping_time(n)
        tst = total_stopping_time(n)
        key = "prime" if is_prime[n] else "comp"
        residues[r][f"{key}_st"].append(st)
        residues[r][f"{key}_tst"].append(tst)

    print(f"{'r':>5} | {'P#':>5} | {'C#':>5} | {'P_ST':>8} | {'C_ST':>8} | {'diff_ST':>8} | {'P_TST':>8} | {'C_TST':>8} | {'diff_TST':>8}")
    print("-" * 90)

    significant_diffs = []
    for r in sorted(residues.keys()):
        if r % 2 == 0:
            continue
        d = residues[r]
        if len(d["prime_st"]) < 3 or len(d["comp_st"]) < 3:
            continue
        p_st = sum(d["prime_st"]) / len(d["prime_st"])
        c_st = sum(d["comp_st"]) / len(d["comp_st"])
        p_tst = sum(d["prime_tst"]) / len(d["prime_tst"])
        c_tst = sum(d["comp_tst"]) / len(d["comp_tst"])
        diff_st = p_st - c_st
        diff_tst = p_tst - c_tst

        print(f"{r:>5} | {len(d['prime_st']):>5} | {len(d['comp_st']):>5} | {p_st:>8.2f} | {c_st:>8.2f} | {diff_st:>8.2f} | {p_tst:>8.2f} | {c_tst:>8.2f} | {diff_tst:>8.2f}")
        significant_diffs.append((r, diff_st, diff_tst, len(d["prime_st"]), len(d["comp_st"])))

# =============================================
# 実験8: 統計的検定（手動t検定近似）
# =============================================
print("\n" + "=" * 70)
print("実験8: 全体での統計的有意性（t値の手動計算）")
print("=" * 70)

def t_test(vals1, vals2):
    """2群のt検定（近似）"""
    n1, n2 = len(vals1), len(vals2)
    if n1 < 2 or n2 < 2:
        return 0, 0, 0
    m1 = sum(vals1) / n1
    m2 = sum(vals2) / n2
    s1 = (sum((v - m1)**2 for v in vals1) / (n1 - 1)) ** 0.5
    s2 = (sum((v - m2)**2 for v in vals2) / (n2 - 1)) ** 0.5
    se = ((s1**2 / n1) + (s2**2 / n2)) ** 0.5
    if se == 0:
        return 0, m1 - m2, 0
    t = (m1 - m2) / se
    return t, m1 - m2, se

# 全体比較
t_st, diff_st, se_st = t_test(prime_st, composite_st)
t_tst, diff_tst, se_tst = t_test(prime_tst, composite_tst)
t_peak, diff_peak, se_peak = t_test(prime_log_peaks, comp_log_peaks)

print(f"\nStopping Time:       t = {t_st:.4f}, diff = {diff_st:.4f}, SE = {se_st:.4f}")
print(f"Total Stopping Time: t = {t_tst:.4f}, diff = {diff_tst:.4f}, SE = {se_tst:.4f}")
print(f"Log2(Peak):          t = {t_peak:.4f}, diff = {diff_peak:.4f}, SE = {se_peak:.4f}")
print(f"\n|t| > 2.0 は統計的に有意 (p < 0.05 相当)")

# mod 8 内でのt検定
print(f"\n--- mod 8 内での t検定 ---")
for r in [1, 3, 5, 7]:
    p_vals = [stopping_time(n) for n in range(r, LIMIT + 1, 8) if n > 1 and is_prime[n]]
    c_vals = [stopping_time(n) for n in range(r, LIMIT + 1, 8) if n > 1 and not is_prime[n] and n % 2 == 1]
    if p_vals and c_vals:
        t, d, se = t_test(p_vals, c_vals)
        print(f"  r={r} mod 8: t = {t:.4f}, diff = {d:.4f} (P: {len(p_vals)}, C: {len(c_vals)})")

# =============================================
# 実験9: v2列の自己相関の違い
# =============================================
print("\n" + "=" * 70)
print("実験9: v2列の自己相関比較（lag 1-5）")
print("=" * 70)

def autocorrelation(seq, lag):
    """自己相関"""
    n = len(seq)
    if n <= lag:
        return 0
    mean = sum(seq) / n
    num = sum((seq[i] - mean) * (seq[i + lag] - mean) for i in range(n - lag))
    denom = sum((seq[i] - mean)**2 for i in range(n))
    if denom == 0:
        return 0
    return num / denom

prime_v2_seqs = []
comp_v2_seqs = []

for n in range(3, 5000, 2):
    odds, v2s = syracuse_orbit(n)
    if len(v2s) >= 20:
        if is_prime[n]:
            prime_v2_seqs.append(v2s[:50])
        else:
            comp_v2_seqs.append(v2s[:50])

print(f"\n{'Lag':>5} | {'素数 autocorr':>15} | {'合成数 autocorr':>15} | {'差':>10}")
print("-" * 55)
for lag in range(1, 6):
    p_ac = sum(autocorrelation(s, lag) for s in prime_v2_seqs) / len(prime_v2_seqs)
    c_ac = sum(autocorrelation(s, lag) for s in comp_v2_seqs) / len(comp_v2_seqs)
    print(f"{lag:>5} | {p_ac:>15.6f} | {c_ac:>15.6f} | {p_ac - c_ac:>10.6f}")

# =============================================
# 実験10: 大きな素数でのスケーリング
# =============================================
print("\n" + "=" * 70)
print("実験10: 範囲を変えたときのST差のスケーリング")
print("=" * 70)

for upper in [1000, 2000, 5000, 10000]:
    is_p = sieve_primes(upper)
    p_sts = []
    c_sts = []
    for n in range(3, upper + 1, 2):
        st = stopping_time(n)
        if is_p[n]:
            p_sts.append(st)
        else:
            c_sts.append(st)

    if p_sts and c_sts:
        t, d, se = t_test(p_sts, c_sts)
        p_mean = sum(p_sts) / len(p_sts)
        c_mean = sum(c_sts) / len(c_sts)
        print(f"N <= {upper:>6}: P_mean = {p_mean:.3f}, C_mean = {c_mean:.3f}, diff = {d:.3f}, t = {t:.3f} (P:{len(p_sts)}, C:{len(c_sts)})")

print("\n" + "=" * 70)
print("全実験完了")
print("=" * 70)
