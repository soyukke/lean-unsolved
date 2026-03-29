#!/usr/bin/env python3
"""
深堀り分析: 実験1の結果で有意差が出た項目を精査する。
- TST (total stopping time) で素数 < 合成数 (t = -2.47)
- log2(peak) で素数 < 合成数 (t = -4.46)
これらが真の差なのか、mod分布のバイアスで説明できるのかを検証。
"""
import math
from collections import defaultdict

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def total_stopping_time(n):
    x = n
    steps = 0
    while x != 1:
        x = collatz_step(x)
        steps += 1
        if steps > 100000:
            return -1
    return steps

def peak_value(n):
    x = n
    peak = n
    while x != 1:
        x = collatz_step(x)
        peak = max(peak, x)
        if x > 10**18:
            return peak
    return peak

def stopping_time(n):
    x = n
    steps = 0
    while x >= n and x != 1:
        x = collatz_step(x)
        steps += 1
        if steps > 10000:
            return -1
    return steps

def t_test(vals1, vals2):
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

LIMIT = 20000
is_prime = sieve_primes(LIMIT)

# =============================================
# 分析A: mod分布バイアスの検証
# 素数は mod 6 で 1 or 5 に偏る。これが TST/peak の差を説明するか？
# =============================================
print("=" * 70)
print("分析A: mod分布バイアスの検証")
print("=" * 70)

# 素数の mod 分布を確認
print("\n素数の mod 分布:")
for m in [4, 6, 8, 12, 24]:
    counts = defaultdict(int)
    for n in range(3, LIMIT + 1, 2):
        if is_prime[n]:
            counts[n % m] += 1
    total = sum(counts.values())
    print(f"  mod {m}: ", end="")
    for r in sorted(counts.keys()):
        print(f"{r}:{counts[r]}({counts[r]/total*100:.1f}%) ", end="")
    print()

# 合成数の mod 分布を確認
print("\n奇数合成数の mod 分布:")
for m in [4, 6, 8, 12, 24]:
    counts = defaultdict(int)
    for n in range(3, LIMIT + 1, 2):
        if not is_prime[n] and n > 1:
            counts[n % m] += 1
    total = sum(counts.values())
    print(f"  mod {m}: ", end="")
    for r in sorted(counts.keys()):
        print(f"{r}:{counts[r]}({counts[r]/total*100:.1f}%) ", end="")
    print()

# =============================================
# 分析B: mod 8 条件付き TST/Peak 比較
# mod 8 の各残基内で比較すれば、mod分布バイアスは除去される
# =============================================
print("\n" + "=" * 70)
print("分析B: mod 8 条件付き TST / Peak 比較")
print("=" * 70)

for r in [1, 3, 5, 7]:
    p_tst = []
    c_tst = []
    p_peak = []
    c_peak = []
    for n in range(r, LIMIT + 1, 8):
        if n < 3:
            continue
        tst = total_stopping_time(n)
        pk = math.log2(peak_value(n))
        if is_prime[n]:
            p_tst.append(tst)
            p_peak.append(pk)
        elif n % 2 == 1:
            c_tst.append(tst)
            c_peak.append(pk)

    t_tst, d_tst, _ = t_test(p_tst, c_tst)
    t_pk, d_pk, _ = t_test(p_peak, c_peak)
    print(f"  r={r} mod 8: TST: t={t_tst:.3f} diff={d_tst:.3f} (P:{len(p_tst)},C:{len(c_tst)}) | Peak: t={t_pk:.3f} diff={d_pk:.3f}")

# =============================================
# 分析C: mod 24 条件付き比較（素数は mod 24 で 6つの残基のみ）
# =============================================
print("\n" + "=" * 70)
print("分析C: mod 24 条件付き TST / Peak 比較")
print("=" * 70)

# 素数は 2,3 以外では 6k+1 または 6k+5 に限られる
# mod 24 では: 1,5,7,11,13,17,19,23 のみ(2,3除外)
for r in [1, 5, 7, 11, 13, 17, 19, 23]:
    p_tst = []
    c_tst = []
    p_peak = []
    c_peak = []
    for n in range(r, LIMIT + 1, 24):
        if n < 5:
            continue
        tst = total_stopping_time(n)
        pk = math.log2(peak_value(n))
        if is_prime[n]:
            p_tst.append(tst)
            p_peak.append(pk)
        else:
            c_tst.append(tst)
            c_peak.append(pk)

    if len(p_tst) >= 5 and len(c_tst) >= 5:
        t_tst, d_tst, _ = t_test(p_tst, c_tst)
        t_pk, d_pk, _ = t_test(p_peak, c_peak)
        print(f"  r={r:>2} mod 24: TST: t={t_tst:>7.3f} diff={d_tst:>7.2f} (P:{len(p_tst):>4},C:{len(c_tst):>4}) | Peak: t={t_pk:>7.3f} diff={d_pk:>7.3f}")

# =============================================
# 分析D: 3の倍数近傍の効果
# 合成数 = 3*k (奇数) は 3n+1 演算で 9k+1 になり特殊
# =============================================
print("\n" + "=" * 70)
print("分析D: 3の倍数の奇数合成数の TST (3n+1 演算の特殊性)")
print("=" * 70)

mult3_tst = []
non_mult3_comp_tst = []
prime_tst_all = []

for n in range(3, LIMIT + 1, 2):
    if n == 3:
        continue
    tst = total_stopping_time(n)
    if is_prime[n]:
        prime_tst_all.append(tst)
    elif n % 3 == 0:
        mult3_tst.append(tst)
    else:
        non_mult3_comp_tst.append(tst)

p_mean = sum(prime_tst_all) / len(prime_tst_all)
m3_mean = sum(mult3_tst) / len(mult3_tst)
nm3_mean = sum(non_mult3_comp_tst) / len(non_mult3_comp_tst)

print(f"  素数の TST 平均:           {p_mean:.3f} ({len(prime_tst_all)}個)")
print(f"  3の倍数合成数の TST 平均:  {m3_mean:.3f} ({len(mult3_tst)}個)")
print(f"  非3倍数合成数の TST 平均:  {nm3_mean:.3f} ({len(non_mult3_comp_tst)}個)")

t_pm, d_pm, _ = t_test(prime_tst_all, mult3_tst)
t_pnm, d_pnm, _ = t_test(prime_tst_all, non_mult3_comp_tst)
print(f"\n  素数 vs 3倍数合成数:   t = {t_pm:.3f}, diff = {d_pm:.3f}")
print(f"  素数 vs 非3倍数合成数: t = {t_pnm:.3f}, diff = {d_pnm:.3f}")

# =============================================
# 分析E: 小さい因子を持つ合成数の影響
# =============================================
print("\n" + "=" * 70)
print("分析E: 最小素因子による分類")
print("=" * 70)

def smallest_prime_factor(n):
    if n < 2:
        return n
    if n % 2 == 0:
        return 2
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return i
    return n  # n is prime

categories = defaultdict(list)
for n in range(5, LIMIT + 1, 2):
    tst = total_stopping_time(n)
    if is_prime[n]:
        categories["prime"].append(tst)
    else:
        spf = smallest_prime_factor(n)
        if spf == 3:
            categories["spf=3"].append(tst)
        elif spf == 5:
            categories["spf=5"].append(tst)
        elif spf == 7:
            categories["spf=7"].append(tst)
        elif spf <= 13:
            categories["spf=11,13"].append(tst)
        else:
            categories["spf>=17"].append(tst)

for cat in ["prime", "spf=3", "spf=5", "spf=7", "spf=11,13", "spf>=17"]:
    vals = categories[cat]
    if vals:
        mean = sum(vals) / len(vals)
        t, d, _ = t_test(categories["prime"], vals)
        print(f"  {cat:>12}: mean={mean:>8.2f}, count={len(vals):>5}, vs prime: t={t:>7.3f}")

# =============================================
# 分析F: 正規化した比較 (TST / log2(n))
# =============================================
print("\n" + "=" * 70)
print("分析F: 正規化 TST/log2(n) の比較")
print("=" * 70)

prime_norm_tst = []
comp_norm_tst = []

for n in range(5, LIMIT + 1, 2):
    tst = total_stopping_time(n)
    norm = tst / math.log2(n)
    if is_prime[n]:
        prime_norm_tst.append(norm)
    else:
        comp_norm_tst.append(norm)

t_norm, d_norm, se_norm = t_test(prime_norm_tst, comp_norm_tst)
print(f"  素数:   mean = {sum(prime_norm_tst)/len(prime_norm_tst):.4f}")
print(f"  合成数: mean = {sum(comp_norm_tst)/len(comp_norm_tst):.4f}")
print(f"  t = {t_norm:.4f}, diff = {d_norm:.6f}")

# mod 8 内で
for r in [1, 3, 5, 7]:
    p_norm = []
    c_norm = []
    for n in range(r, LIMIT + 1, 8):
        if n < 5:
            continue
        tst = total_stopping_time(n)
        norm = tst / math.log2(n)
        if is_prime[n]:
            p_norm.append(norm)
        elif n % 2 == 1:
            c_norm.append(norm)
    if p_norm and c_norm:
        t, d, _ = t_test(p_norm, c_norm)
        print(f"  r={r} mod 8: t = {t:.4f}, diff = {d:.6f}")

# =============================================
# 分析G: 素数の密度効果
# 素数定理により素数は小さいnに偏る。nのサイズで層別化
# =============================================
print("\n" + "=" * 70)
print("分析G: nのサイズで層別化した比較")
print("=" * 70)

ranges = [(5, 500), (500, 2000), (2000, 5000), (5000, 10000), (10000, 20000)]
for lo, hi in ranges:
    p_tst = []
    c_tst = []
    for n in range(lo if lo % 2 == 1 else lo + 1, hi + 1, 2):
        tst = total_stopping_time(n)
        if is_prime[n]:
            p_tst.append(tst)
        else:
            c_tst.append(tst)
    if p_tst and c_tst:
        t, d, _ = t_test(p_tst, c_tst)
        p_m = sum(p_tst) / len(p_tst)
        c_m = sum(c_tst) / len(c_tst)
        print(f"  [{lo:>6},{hi:>6}]: P_mean={p_m:>7.2f} C_mean={c_m:>7.2f} diff={d:>7.2f} t={t:>7.3f} (P:{len(p_tst):>4},C:{len(c_tst):>4})")

# =============================================
# 分析H: 末尾ビットが確定する場合のST完全一致検証
# =============================================
print("\n" + "=" * 70)
print("分析H: mod 2^k でSTが完全に決まるかの検証")
print("=" * 70)

for k in range(3, 9):
    mod = 2**k
    st_by_residue = defaultdict(set)
    for n in range(3, 2000, 2):
        st = stopping_time(n)
        st_by_residue[n % mod].add(st)

    deterministic = 0
    total = 0
    for r, st_set in st_by_residue.items():
        if r % 2 == 1:
            total += 1
            if len(st_set) == 1:
                deterministic += 1

    print(f"  mod 2^{k} = {mod:>4}: {deterministic}/{total} 残基でST確定 ({deterministic/total*100:.1f}%)")

# =============================================
# 分析I: 確率論的理由の確認
# E[TST] ~ C * log(n) で C の推定
# =============================================
print("\n" + "=" * 70)
print("分析I: TST ~ C * log(n) の係数推定")
print("=" * 70)

# 素数は平均してlog(n)が小さい → TSTも小さくなるはず
# ただし正規化後の差が本質
import random
random.seed(42)

# ランダムな奇数との比較
random_odd_tst = []
for _ in range(2000):
    n = random.randrange(5, LIMIT + 1, 2)
    random_odd_tst.append(total_stopping_time(n))

r_mean = sum(random_odd_tst) / len(random_odd_tst)
print(f"  ランダム奇数 TST 平均: {r_mean:.3f}")

# 素数と同じサイズ分布を持つランダム奇数
# 素数は n ~ N/(ln N) で分布するので、同じn分布のサンプルを作成
prime_list = [n for n in range(5, LIMIT + 1, 2) if is_prime[n]]
matched_comp_tst = []
for p in prime_list:
    # p と同じ mod 8 残基を持つ最も近い合成数
    for delta in range(8, 1000, 8):
        candidate = p + delta
        if candidate <= LIMIT and candidate % 2 == 1 and not is_prime[candidate]:
            matched_comp_tst.append(total_stopping_time(candidate))
            break

if matched_comp_tst:
    m_mean = sum(matched_comp_tst) / len(matched_comp_tst)
    t_m, d_m, _ = t_test([total_stopping_time(p) for p in prime_list], matched_comp_tst)
    print(f"  マッチド合成数 TST 平均: {m_mean:.3f} ({len(matched_comp_tst)}個)")
    print(f"  素数 vs マッチド合成数: t = {t_m:.3f}, diff = {d_m:.3f}")

# =============================================
# 分析J: 最初のSyracuseステップの構造差
# T(p) = (3p+1)/2^v2(3p+1) の分布
# =============================================
print("\n" + "=" * 70)
print("分析J: 最初のSyracuseステップ T(n) の性質")
print("=" * 70)

def syracuse_first(n):
    """最初のSyracuse step"""
    x = 3 * n + 1
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return x, v

prime_ratio = []  # T(p)/p
comp_ratio = []   # T(n)/n

for n in range(5, LIMIT + 1, 2):
    x, v = syracuse_first(n)
    ratio = x / n
    if is_prime[n]:
        prime_ratio.append(ratio)
    else:
        comp_ratio.append(ratio)

t_r, d_r, _ = t_test(prime_ratio, comp_ratio)
print(f"  素数:   T(p)/p 平均 = {sum(prime_ratio)/len(prime_ratio):.6f}")
print(f"  合成数: T(n)/n 平均 = {sum(comp_ratio)/len(comp_ratio):.6f}")
print(f"  t = {t_r:.4f}, diff = {d_r:.6f}")

# v2(3n+1)の分布
print(f"\n  v2(3n+1) の分布:")
prime_v2_first = defaultdict(int)
comp_v2_first = defaultdict(int)
for n in range(5, LIMIT + 1, 2):
    _, v = syracuse_first(n)
    if is_prime[n]:
        prime_v2_first[v] += 1
    else:
        comp_v2_first[v] += 1

p_total = sum(prime_v2_first.values())
c_total = sum(comp_v2_first.values())
print(f"  {'v2':>4} | {'素数 freq':>12} | {'合成数 freq':>12} | {'差':>10}")
for v in range(1, 10):
    pf = prime_v2_first.get(v, 0) / p_total
    cf = comp_v2_first.get(v, 0) / c_total
    print(f"  {v:>4} | {pf:>12.6f} | {cf:>12.6f} | {pf - cf:>10.6f}")

print("\n" + "=" * 70)
print("全分析完了")
print("=" * 70)
