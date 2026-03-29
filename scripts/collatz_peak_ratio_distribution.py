"""
コラッツ軌道のピーク/n比の漸近分布解析（純Python版）
=====================================================
Syracuse関数 T(n) = (3n+1) / 2^{v2(3n+1)} のもとで
peak(n) = max{T^k(n) : k>=0} として peak(n)/n の分布を調べる。

調査項目:
1. peak(n)/n の経験的分布（対数スケール含む）
2. record holder（peak(n)/nが過去最大を更新するn）の構造解析
3. log2(peak(n)/n) の分布形状（正規 vs Gumbel）
4. peak(n)/n > C となる最小nの成長率
5. record holderの mod 32, mod 64 パターン
"""

import math
import time
import json
from collections import defaultdict, Counter

# Syracuse function
def syracuse(n):
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def collatz_peak(n):
    """n の軌道における最大値を返す（n自身含む）"""
    peak = n
    current = n
    steps = 0
    while current != 1 and steps < 100000:
        current = syracuse(current)
        if current > peak:
            peak = current
        steps += 1
    return peak

def trailing_ones(n):
    """2進表示の末尾連続1の数"""
    c = 0
    while n & 1:
        n >>= 1
        c += 1
    return c

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def std(lst):
    if len(lst) < 2:
        return 0.0
    m = mean(lst)
    return math.sqrt(sum((x - m)**2 for x in lst) / len(lst))

def median_val(lst):
    s = sorted(lst)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0

def percentile(lst, p):
    s = sorted(lst)
    k = (len(s) - 1) * p / 100.0
    f = int(k)
    c = f + 1
    if c >= len(s):
        return s[-1]
    return s[f] + (k - f) * (s[c] - s[f])

def skewness(lst):
    m = mean(lst)
    s = std(lst)
    if s == 0:
        return 0.0
    return mean([(x - m)**3 for x in lst]) / s**3

def kurtosis_excess(lst):
    m = mean(lst)
    s = std(lst)
    if s == 0:
        return 0.0
    return mean([(x - m)**4 for x in lst]) / s**4 - 3.0

# ========================================
# Phase 1: peak(n)/n の基本分布統計
# ========================================
def phase1_basic_distribution(N_max=500000):
    print(f"=== Phase 1: peak(n)/n 基本分布 (n=1..{N_max}, n odd) ===")
    t0 = time.time()

    ratios = []
    log_ratios = []

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        ratios.append(r)
        log_ratios.append(math.log2(max(r, 1e-300)))

    elapsed = time.time() - t0
    print(f"  計算時間: {elapsed:.1f}s, サンプル数: {len(ratios)}")

    stats = {
        "count": len(ratios),
        "mean_ratio": mean(ratios),
        "median_ratio": median_val(ratios),
        "max_ratio": max(ratios),
        "min_ratio": min(ratios),
        "std_ratio": std(ratios),
        "mean_log2_ratio": mean(log_ratios),
        "median_log2_ratio": median_val(log_ratios),
        "std_log2_ratio": std(log_ratios),
        "skewness_log2": skewness(log_ratios),
        "kurtosis_excess_log2": kurtosis_excess(log_ratios),
    }

    for p in [90, 95, 99, 99.9]:
        stats[f"p{p}_ratio"] = percentile(ratios, p)
        stats[f"p{p}_log2_ratio"] = percentile(log_ratios, p)

    for threshold in [10, 100, 1000, 5000, 10000]:
        frac = sum(1 for r in ratios if r > threshold) / len(ratios)
        stats[f"frac_gt_{threshold}"] = frac

    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")

    return stats, ratios, log_ratios

# ========================================
# Phase 2: Record holder の構造解析
# ========================================
def phase2_record_holders(N_max=2000000):
    print(f"\n=== Phase 2: Record Holders (n=1..{N_max}, n odd) ===")
    t0 = time.time()

    record_ratio = 0
    records = []

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        if r > record_ratio:
            record_ratio = r
            to = trailing_ones(n)
            rec = {
                "n": n,
                "peak": pk,
                "ratio": float(r),
                "log2_ratio": float(math.log2(r)) if r > 0 else 0,
                "trailing_ones": to,
                "n_mod8": n % 8,
                "n_mod16": n % 16,
                "n_mod32": n % 32,
                "n_mod64": n % 64,
                "n_mod128": n % 128,
                "n_bits": n.bit_length(),
                "n_binary_suffix": bin(n)[-8:] if n.bit_length() >= 8 else bin(n),
            }
            records.append(rec)

    elapsed = time.time() - t0
    print(f"  計算時間: {elapsed:.1f}s, レコード数: {len(records)}")

    mod32_dist = Counter(r["n_mod32"] for r in records)
    mod64_dist = Counter(r["n_mod64"] for r in records)
    trailing_dist = Counter(r["trailing_ones"] for r in records)

    print(f"\n  Top 20 record holders:")
    for r in records[-20:]:
        print(f"    n={r['n']:>10}, peak={r['peak']:>15}, ratio={r['ratio']:>12.2f}, "
              f"log2={r['log2_ratio']:.3f}, trail1s={r['trailing_ones']}, "
              f"mod32={r['n_mod32']}, suffix={r['n_binary_suffix']}")

    print(f"\n  Trailing ones分布: {dict(trailing_dist.most_common(10))}")
    print(f"  Mod 32分布 (top10): {dict(mod32_dist.most_common(10))}")

    # record holder間の間隔
    if len(records) >= 2:
        gaps = [records[i+1]["n"] / records[i]["n"] for i in range(len(records)-1)]
        print(f"\n  連続record holder間のn比: mean={mean(gaps):.3f}, median={median_val(gaps):.3f}")

    # record比の成長パターン
    if len(records) >= 5:
        log2_ratios = [r["log2_ratio"] for r in records]
        log2_ns = [math.log2(r["n"]) for r in records]
        # 簡易線形回帰（最後30レコード）
        recent = min(30, len(records))
        xs = log2_ns[-recent:]
        ys = log2_ratios[-recent:]
        mx, my = mean(xs), mean(ys)
        cov = sum((x-mx)*(y-my) for x,y in zip(xs, ys)) / len(xs)
        varx = sum((x-mx)**2 for x in xs) / len(xs)
        slope = cov / varx if varx > 0 else 0
        intercept = my - slope * mx
        print(f"  Record ratio成長: log2(ratio) ~ {slope:.4f} * log2(n) + {intercept:.4f}")

    return records, mod32_dist, trailing_dist

# ========================================
# Phase 3: peak(n)/n > C となる最小nの成長率
# ========================================
def phase3_threshold_growth(N_max=2000000):
    print(f"\n=== Phase 3: peak(n)/n > C の最小nの成長率 ===")
    t0 = time.time()

    thresholds = [2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000]
    first_exceed = {C: None for C in thresholds}

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        for C in thresholds:
            if first_exceed[C] is None and r > C:
                first_exceed[C] = n

    elapsed = time.time() - t0
    print(f"  計算時間: {elapsed:.1f}s")

    results = []
    print(f"\n  {'C':>8} | {'min_n':>12} | {'log2(C)':>8} | {'log2(n)':>8} | ratio_log")
    print(f"  {'-'*60}")
    for C in thresholds:
        n_val = first_exceed[C]
        if n_val is not None:
            log2C = math.log2(C)
            log2n = math.log2(n_val)
            ratio_log = log2n / log2C if log2C > 0 else float('inf')
            print(f"  {C:>8} | {n_val:>12} | {log2C:>8.3f} | {log2n:>8.3f} | {ratio_log:.4f}")
            results.append({
                "C": C, "min_n": n_val, "log2_C": float(log2C),
                "log2_n": float(log2n), "ratio_log2n_log2C": float(ratio_log)
            })
        else:
            print(f"  {C:>8} | {'not found':>12} |")
            results.append({"C": C, "min_n": None})

    # 回帰
    found = [(r["log2_C"], r["log2_n"]) for r in results if r["min_n"] is not None and r["log2_C"] > 0]
    if len(found) >= 3:
        xs, ys = zip(*found)
        mx, my = mean(xs), mean(ys)
        cov = sum((x-mx)*(y-my) for x,y in zip(xs, ys)) / len(xs)
        varx = sum((x-mx)**2 for x in xs) / len(xs)
        slope = cov / varx if varx > 0 else 0
        intercept = my - slope * mx
        print(f"\n  成長率回帰: log2(min_n) ~ {slope:.4f} * log2(C) + {intercept:.4f}")
        print(f"  つまり min_n ~ 2^{{{intercept:.2f}}} * C^{{{slope:.4f}}}")

    return results

# ========================================
# Phase 4: log2(peak/n)分布形状の数値テスト
# ========================================
def phase4_distribution_shape(log_ratios):
    print(f"\n=== Phase 4: 分布形状テスト ===")

    data = sorted(log_ratios)
    n = len(data)
    mu = mean(data)
    sigma = std(data)

    # Gumbelパラメータ推定（モーメント法）
    euler_gamma = 0.5772156649
    beta_g = sigma * math.sqrt(6) / math.pi
    mu_g = mu - euler_gamma * beta_g

    # 正規CDF
    def normal_cdf(x, mu, sigma):
        return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))

    # Gumbel CDF: exp(-exp(-(x-mu_g)/beta_g))
    def gumbel_cdf(x, mu_g, beta_g):
        z = -(x - mu_g) / beta_g
        if z > 700:
            return 0.0
        if z < -700:
            return 1.0
        return math.exp(-math.exp(z))

    # KS統計量の計算
    max_diff_normal = 0
    max_diff_gumbel = 0
    for i, x in enumerate(data):
        ecdf = (i + 1) / n
        ecdf_prev = i / n

        fn = normal_cdf(x, mu, sigma)
        fg = gumbel_cdf(x, mu_g, beta_g)

        max_diff_normal = max(max_diff_normal, abs(ecdf - fn), abs(ecdf_prev - fn))
        max_diff_gumbel = max(max_diff_gumbel, abs(ecdf - fg), abs(ecdf_prev - fg))

    sk = skewness(log_ratios)
    kurt = kurtosis_excess(log_ratios)

    # 尾部解析: 上位テール
    p_levels = [0.9, 0.95, 0.99, 0.995, 0.999]
    tail_quantiles = {}
    for p in p_levels:
        idx = int(p * n)
        if idx < n:
            tail_quantiles[f"q{p}"] = data[idx]

    # 上位1%のlog2(peak/n)の分布
    top1pct = data[int(0.99 * n):]
    top1_mean = mean(top1pct)
    top1_std = std(top1pct)

    results = {
        "normal_KS": max_diff_normal,
        "gumbel_KS": max_diff_gumbel,
        "gumbel_params": {"mu_g": mu_g, "beta_g": beta_g},
        "normal_params": {"mu": mu, "sigma": sigma},
        "skewness": sk,
        "excess_kurtosis": kurt,
        "tail_quantiles": tail_quantiles,
        "top1pct_mean_log2": top1_mean,
        "top1pct_std_log2": top1_std,
        "better_fit": "gumbel" if max_diff_gumbel < max_diff_normal else "normal",
    }

    print(f"  正規KS統計量: {max_diff_normal:.6f}")
    print(f"  Gumbel KS統計量: {max_diff_gumbel:.6f}")
    print(f"  Gumbelパラメータ: mu_g={mu_g:.4f}, beta_g={beta_g:.4f}")
    print(f"  正規パラメータ: mu={mu:.4f}, sigma={sigma:.4f}")
    print(f"  歪度: {sk:.4f}, 超過尖度: {kurt:.4f}")
    print(f"  (参考: 正規=歪度0,尖度0 / Gumbel=歪度1.14,尖度2.4)")
    print(f"  -> {results['better_fit']}分布の方がよい適合")
    print(f"  尾部定量値: {tail_quantiles}")
    print(f"  上位1%: mean_log2={top1_mean:.4f}, std={top1_std:.4f}")

    return results

# ========================================
# Phase 5: 極値分布 - ブロック最大値のGEVパラメータ推定
# ========================================
def phase5_block_maxima(N_max=500000, block_size=1000):
    print(f"\n=== Phase 5: ブロック最大値分布 (block={block_size}) ===")
    t0 = time.time()

    block_max_log_ratios = []
    current_block_max = -float('inf')
    count = 0

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        lr = math.log2(max(r, 1e-300))
        current_block_max = max(current_block_max, lr)
        count += 1
        if count == block_size:
            block_max_log_ratios.append(current_block_max)
            current_block_max = -float('inf')
            count = 0

    elapsed = time.time() - t0
    print(f"  ブロック数: {len(block_max_log_ratios)}, 計算時間: {elapsed:.1f}s")

    bm = block_max_log_ratios
    if len(bm) >= 5:
        # 簡易GEVパラメータ推定（PWM法の簡略版）
        bm_sorted = sorted(bm)
        bm_mean = mean(bm)
        bm_std = std(bm)
        bm_skew = skewness(bm)

        # Gumbel仮定でのパラメータ
        beta_block = bm_std * math.sqrt(6) / math.pi
        mu_block = bm_mean - 0.5772 * beta_block

        print(f"  ブロック最大値: mean={bm_mean:.4f}, std={bm_std:.4f}, skew={bm_skew:.4f}")
        print(f"  Gumbel近似: mu={mu_block:.4f}, beta={beta_block:.4f}")
        print(f"  (Gumbel歪度=1.14 vs 観測歪度={bm_skew:.4f})")

        if bm_skew > 1.14 + 0.3:
            print(f"  -> 歪度がGumbelより大きい: Frechet型（重い尾）の可能性")
            gev_type = "Frechet-like (heavy tail)"
        elif bm_skew < 1.14 - 0.3:
            print(f"  -> 歪度がGumbelより小さい: Weibull型（有界尾）の可能性")
            gev_type = "Weibull-like (bounded tail)"
        else:
            print(f"  -> 歪度がGumbel付近: Gumbel型（指数的尾）")
            gev_type = "Gumbel-like (exponential tail)"

        return {
            "block_size": block_size,
            "n_blocks": len(bm),
            "mean_block_max_log2": bm_mean,
            "std_block_max_log2": bm_std,
            "skewness_block_max": bm_skew,
            "gumbel_mu": mu_block,
            "gumbel_beta": beta_block,
            "gev_type_estimate": gev_type,
            "block_max_values": bm_sorted[-5:],
        }
    return {}

# ========================================
# Phase 6: mod構造とpeak ratioの相関
# ========================================
def phase6_mod_correlation(N_max=300000):
    print(f"\n=== Phase 6: mod構造とpeak ratio相関 ===")
    t0 = time.time()

    mod_ratios = defaultdict(list)

    for n in range(1, N_max + 1, 2):
        pk = collatz_peak(n)
        r = pk / n
        log_r = math.log2(max(r, 1e-300))
        for m in [8, 16, 32]:
            mod_ratios[(m, n % m)].append(log_r)

    elapsed = time.time() - t0
    print(f"  計算時間: {elapsed:.1f}s")

    results = {}
    for m in [8, 16, 32]:
        print(f"\n  mod {m} の平均 log2(peak/n):")
        mod_means = {}
        for residue in range(m):
            if residue % 2 == 0:
                continue
            data = mod_ratios.get((m, residue), [])
            if data:
                mod_means[residue] = {
                    "mean_log2_ratio": mean(data),
                    "std_log2_ratio": std(data),
                    "count": len(data),
                    "max_log2_ratio": max(data),
                }

        sorted_mods = sorted(mod_means.items(), key=lambda x: x[1]["mean_log2_ratio"], reverse=True)
        for res, info in sorted_mods[:8]:
            print(f"    {res:>3} (bin={bin(res):>10}): mean={info['mean_log2_ratio']:.4f}, "
                  f"std={info['std_log2_ratio']:.4f}, max={info['max_log2_ratio']:.4f}")

        results[f"mod{m}"] = mod_means

    return results

# ========================================
# Phase 7: 連続record holderのビットパターン深堀
# ========================================
def phase7_record_bit_patterns(records):
    print(f"\n=== Phase 7: Record holderのビットパターン深堀 ===")

    if len(records) < 5:
        print("  レコードが少なすぎます")
        return {}

    # 2進表現の長さ vs log2(ratio)
    bits_vs_ratio = [(r["n_bits"], r["log2_ratio"]) for r in records]

    # 末尾パターン（下位8bit）の頻度
    suffix_dist = Counter(r["n_binary_suffix"] for r in records)
    print(f"  末尾8bit頻度 (top10): ")
    for suffix, count in suffix_dist.most_common(10):
        print(f"    {suffix}: {count}回")

    # trailing ones vs ratio の相関
    trail_groups = defaultdict(list)
    for r in records:
        trail_groups[r["trailing_ones"]].append(r["log2_ratio"])

    print(f"\n  trailing_ones別の平均log2(ratio):")
    for to in sorted(trail_groups.keys()):
        vals = trail_groups[to]
        print(f"    trail_ones={to}: mean_log2_ratio={mean(vals):.4f}, count={len(vals)}")

    # record ratio の成長間隔
    ratio_jumps = []
    for i in range(1, len(records)):
        jump = records[i]["log2_ratio"] - records[i-1]["log2_ratio"]
        n_gap = records[i]["n"] / records[i-1]["n"]
        ratio_jumps.append((records[i]["n"], jump, n_gap))

    # 大きなジャンプ
    ratio_jumps.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  最大ratio ジャンプ (top10):")
    for n_val, jump, gap in ratio_jumps[:10]:
        print(f"    n={n_val}, delta_log2_ratio={jump:.4f}, n_gap_ratio={gap:.2f}")

    return {
        "suffix_distribution": dict(suffix_dist.most_common(10)),
        "trailing_ones_groups": {
            str(to): {"mean_log2_ratio": mean(vals), "count": len(vals)}
            for to, vals in trail_groups.items()
        },
        "top_jumps": [
            {"n": j[0], "delta_log2": j[1], "n_gap": j[2]}
            for j in ratio_jumps[:10]
        ],
    }


# ========================================
# Main
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("コラッツ軌道 peak(n)/n 比の漸近分布解析")
    print("=" * 70)

    total_t0 = time.time()

    # Phase 1: 基本分布
    stats1, ratios, log_ratios = phase1_basic_distribution(N_max=500000)

    # Phase 2: Record holders
    records, mod32_dist, trailing_dist = phase2_record_holders(N_max=2000000)

    # Phase 3: 閾値成長率
    growth_results = phase3_threshold_growth(N_max=2000000)

    # Phase 4: 分布形状テスト
    dist_shape = phase4_distribution_shape(log_ratios)

    # Phase 5: ブロック最大値
    block_results = phase5_block_maxima(N_max=500000, block_size=1000)

    # Phase 6: mod相関
    mod_results = phase6_mod_correlation(N_max=300000)

    # Phase 7: Record holderビットパターン
    bit_patterns = phase7_record_bit_patterns(records)

    total_elapsed = time.time() - total_t0
    print(f"\n{'='*70}")
    print(f"総計算時間: {total_elapsed:.1f}s")

    # JSON出力
    output = {
        "phase1_basic_stats": stats1,
        "phase2_records_summary": {
            "total_records": len(records),
            "top_records": records[-10:],
            "trailing_ones_dist": dict(trailing_dist),
            "mod32_dist": {str(k): v for k, v in mod32_dist.items()},
        },
        "phase3_threshold_growth": growth_results,
        "phase4_distribution_shape": dist_shape,
        "phase5_block_maxima": block_results,
        "phase6_mod_correlation_summary": {
            mod_key: {
                "top3_residues": sorted(
                    [(int(k), v["mean_log2_ratio"]) for k, v in mod_data.items()],
                    key=lambda x: x[1], reverse=True
                )[:3]
            }
            for mod_key, mod_data in mod_results.items()
        },
        "phase7_bit_patterns": bit_patterns,
    }

    with open("/Users/soyukke/study/lean-unsolved/results/peak_ratio_distribution.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n結果を results/peak_ratio_distribution.json に保存しました")
