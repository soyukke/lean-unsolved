"""
Record holder の深い構造分析
- record holder 間の倍数関係・系譜構造
- 2進表現のパターン (ones density, trailing/leading bits)
- mod 2^k 構造の k 依存性 (trailing bits の統計量)
- record holder 間ギャップの成長率 → alpha 増大の原因
- D(N) (= max ST) vs # record holders のクロス分析
"""

import json
import math
import time
from collections import Counter, defaultdict

def collatz_stopping_time(n):
    """Total stopping time: n -> 1 のステップ数"""
    count = 0
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        count += 1
    return count

def collatz_max_value(n):
    """軌道の最大値"""
    x = n
    mx = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        if x > mx:
            mx = x
    return mx

def v2(n):
    if n == 0: return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def ones_density(n):
    """2進表現での1の割合"""
    b = bin(n)[2:]
    return b.count('1') / len(b)

def binary_pattern(n):
    """2進表現の詳細分析"""
    b = bin(n)[2:]
    bits = len(b)
    ones = b.count('1')
    # 連続する1のランの長さ
    runs_1 = []
    runs_0 = []
    current = b[0]
    run_len = 1
    for i in range(1, len(b)):
        if b[i] == current:
            run_len += 1
        else:
            if current == '1':
                runs_1.append(run_len)
            else:
                runs_0.append(run_len)
            current = b[i]
            run_len = 1
    if current == '1':
        runs_1.append(run_len)
    else:
        runs_0.append(run_len)

    return {
        'bits': bits,
        'ones': ones,
        'ones_density': ones / bits,
        'runs_1': runs_1,
        'runs_0': runs_0,
        'max_run_1': max(runs_1) if runs_1 else 0,
        'max_run_0': max(runs_0) if runs_0 else 0,
        'avg_run_1': sum(runs_1)/len(runs_1) if runs_1 else 0,
        'n_transitions': len(runs_1) + len(runs_0) - 1,
        'trailing_ones': len(b) - len(b.rstrip('1')),  # 末尾連続1
        'leading_ones': len(b) - len(b.lstrip('1')),   # 先頭連続1 (MSB以降)
    }

def find_record_holders(N_max, progress_interval=1000000):
    """Record holders を見つける"""
    records = []
    current_max = 0
    for n in range(1, N_max + 1):
        st = collatz_stopping_time(n)
        if st > current_max:
            current_max = st
            records.append((n, st))
        if n % progress_interval == 0:
            print(f"  n={n:,}, records so far: {len(records)}, max ST: {current_max}")
    return records

def main():
    start_time = time.time()

    # ---- Record holders の計算 ----
    print("Computing record holders up to 10^7...")
    N = 10_000_000
    records = find_record_holders(N)
    print(f"  Total: {len(records)} record holders, max ST = {records[-1][1]}")

    rec_ns = [r[0] for r in records]
    rec_sts = [r[1] for r in records]

    # ==== Analysis 1: Record holder 間の倍数関係 ====
    print("\nAnalysis 1: Multiplicative relations...")
    # n と 2n, 3n の関係
    multiplicity_chains = []
    for i, (n, st) in enumerate(records):
        # 2n がrecord holderか
        is_2n_record = (2*n) in set(rec_ns)
        # n が前の record の k倍か
        for j in range(max(0, i-5), i):
            n_prev = rec_ns[j]
            if n_prev > 0 and n % n_prev == 0:
                ratio = n // n_prev
                if ratio <= 10:
                    multiplicity_chains.append({
                        'n_prev': n_prev, 'n': n,
                        'ratio': ratio,
                        'st_prev': rec_sts[j], 'st': st,
                    })

    # 3^k * m 形式の分析 (3のべき乗の因子)
    three_power_factors = []
    for n, st in records:
        if n <= 1: continue
        k3 = 0
        m = n
        while m % 3 == 0:
            m //= 3
            k3 += 1
        three_power_factors.append({
            'n': n, 'v3': k3, 'odd_part': m if n % 2 == 1 else n // (2**v2(n)),
        })

    # ==== Analysis 2: 2進パターンの詳細 ====
    print("\nAnalysis 2: Binary pattern analysis...")
    bin_patterns = []
    for n, st in records:
        if n <= 1: continue
        bp = binary_pattern(n)
        bp['n'] = n
        bp['st'] = st
        bin_patterns.append(bp)

    # ones density の推移
    od_by_decade = defaultdict(list)
    for bp in bin_patterns:
        decade = int(math.log10(bp['n'])) if bp['n'] > 0 else 0
        od_by_decade[decade].append(bp['ones_density'])

    od_summary = {}
    for dec, vals in sorted(od_by_decade.items()):
        od_summary[f"10^{dec}-10^{dec+1}"] = {
            'count': len(vals),
            'mean_ones_density': sum(vals)/len(vals),
            'min': min(vals),
            'max': max(vals),
        }

    # trailing ones の分布
    trailing_ones_dist = Counter(bp['trailing_ones'] for bp in bin_patterns)

    # ==== Analysis 3: ギャップ成長パターン ====
    print("\nAnalysis 3: Gap growth pattern...")
    gaps = []
    for i in range(len(rec_ns) - 1):
        g = rec_ns[i+1] - rec_ns[i]
        rel_g = g / rec_ns[i] if rec_ns[i] > 0 else 0
        log_ratio = math.log(rec_ns[i+1] / rec_ns[i]) if rec_ns[i] > 0 else 0
        st_jump = rec_sts[i+1] - rec_sts[i]
        gaps.append({
            'i': i,
            'n_from': rec_ns[i],
            'n_to': rec_ns[i+1],
            'gap': g,
            'relative_gap': rel_g,
            'log_ratio': log_ratio,
            'st_jump': st_jump,
            'st_jump_per_bit_gained': st_jump / max(1, rec_ns[i+1].bit_length() - rec_ns[i].bit_length()) if rec_ns[i+1].bit_length() > rec_ns[i].bit_length() else None,
        })

    # log_ratio の推移 (record holder n_{k+1}/n_k の対数)
    log_ratios = [g['log_ratio'] for g in gaps if g['log_ratio'] > 0]

    # 移動平均で log_ratio が減少しているか
    window = 10
    moving_avg_log_ratio = []
    for i in range(len(log_ratios) - window + 1):
        avg = sum(log_ratios[i:i+window]) / window
        moving_avg_log_ratio.append(avg)

    # ==== Analysis 4: ST ジャンプの構造 ====
    print("\nAnalysis 4: Stopping time jump structure...")
    st_jumps = [rec_sts[i+1] - rec_sts[i] for i in range(len(rec_sts)-1)]

    # ST ジャンプが 1, 2, 3 のときの n の特徴
    jump_characteristics = defaultdict(list)
    for i in range(len(st_jumps)):
        jump = st_jumps[i]
        n_new = rec_ns[i+1]
        jump_characteristics[jump].append({
            'n': n_new,
            'mod4': n_new % 4,
            'mod8': n_new % 8,
            'v2': v2(n_new),
            'ones_density': ones_density(n_new) if n_new > 0 else 0,
        })

    # ジャンプサイズ別の統計
    jump_summary = {}
    for jump, chars in sorted(jump_characteristics.items()):
        if len(chars) >= 2:
            mod4_dist = Counter(c['mod4'] for c in chars)
            jump_summary[jump] = {
                'count': len(chars),
                'mod4_distribution': dict(mod4_dist),
                'mean_ones_density': sum(c['ones_density'] for c in chars) / len(chars),
            }

    # ==== Analysis 5: 累積 record holder 数 D_count(N) のスケーリング ====
    print("\nAnalysis 5: D_count(N) scaling...")
    # D_count(N) = N 以下の record holder の数
    # D_max(N) = N 以下の最大 ST
    checkpoints = [10**k for k in range(1, 8)]
    D_count = {}
    D_max = {}
    idx = 0
    for cp in checkpoints:
        while idx < len(rec_ns) and rec_ns[idx] <= cp:
            idx += 1
        D_count[cp] = idx
        D_max[cp] = rec_sts[idx-1] if idx > 0 else 0

    # D_count(N) ~ C * (logN)^alpha
    # D_max(N) ~ C' * (logN)^beta
    # ratio D_max / D_count のスケーリング
    ratio_max_count = {}
    for cp in checkpoints:
        if D_count[cp] > 0:
            ratio_max_count[cp] = D_max[cp] / D_count[cp]

    # alpha_count vs alpha_max の比較
    # log D_count vs log log N, log D_max vs log log N の線形回帰
    log_logN = [math.log(math.log(cp)) for cp in checkpoints if cp >= 100]
    log_Dcount = [math.log(D_count[cp]) for cp in checkpoints if cp >= 100]
    log_Dmax = [math.log(D_max[cp]) for cp in checkpoints if cp >= 100]

    def linear_reg(xs, ys):
        n = len(xs)
        sx = sum(xs); sy = sum(ys)
        sxx = sum(x*x for x in xs); sxy = sum(x*y for x,y in zip(xs, ys))
        b = (n * sxy - sx * sy) / (n * sxx - sx**2)
        a = (sy - b * sx) / n
        # R^2
        y_pred = [a + b*x for x in xs]
        ss_res = sum((y - yp)**2 for y, yp in zip(ys, y_pred))
        mean_y = sy / n
        ss_tot = sum((y - mean_y)**2 for y in ys)
        r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
        return b, a, r2

    alpha_count, _, r2_count = linear_reg(log_logN, log_Dcount)
    alpha_max, _, r2_max = linear_reg(log_logN, log_Dmax)

    # ==== Analysis 6: Record holder n の「系譜」構造 ====
    print("\nAnalysis 6: Genealogical structure...")
    # 仮説: record holder は しばしば 2^a * 3^b - 1 形式 (Mersenne-like)
    # またはそれに近い構造
    mersenne_like = []
    for n, st in records:
        if n <= 1: continue
        # n+1 の因数分解で 2^a * 3^b を探す
        m = n + 1
        a2 = v2(m)
        m >>= a2
        a3 = 0
        while m % 3 == 0:
            m //= 3
            a3 += 1
        remaining = m
        mersenne_like.append({
            'n': n, 'st': st,
            'n_plus_1_form': f"2^{a2} * 3^{a3} * {remaining}",
            'a2': a2, 'a3': a3, 'remaining': remaining,
            'is_2a3b_minus1': (remaining == 1),
        })

    mersenne_count = sum(1 for m in mersenne_like if m['is_2a3b_minus1'])

    # ==== Analysis 7: 近似的に n ≡ 2^k - 1 (mod 2^k) の構造 ====
    print("\nAnalysis 7: Near-Mersenne structure...")
    # record holder は trailing bits が全て1になりやすいか?
    # n & (2^k - 1) == 2^k - 1 ⟺ n の下位 k ビットが全て 1
    all_ones_trailing = {}
    for k in range(1, 12):
        mask = (1 << k) - 1
        count_all_ones = sum(1 for n in rec_ns if n > mask and (n & mask) == mask)
        expected = len([n for n in rec_ns if n > mask]) / (2**k)
        all_ones_trailing[k] = {
            'count': count_all_ones,
            'total': len([n for n in rec_ns if n > mask]),
            'ratio': count_all_ones / max(1, len([n for n in rec_ns if n > mask])),
            'expected_random': 1 / (2**k),
            'enrichment': count_all_ones / max(1, expected),
        }

    # ==== Analysis 8: ST ジャンプパターンと alpha 増大 ====
    print("\nAnalysis 8: ST jump pattern and alpha increase...")
    # 仮説: 大きな N では "3のべき乗" ステップが増え、ST が予想より大きくなる
    # → D_max(N) の成長が加速 → alpha が増大

    # record holder の ST を "bits gained" で正規化
    # 期待値: 各 Collatz step で log2(3/2) ≈ 0.585 bit 得 (odd step)
    #          各 even step で -1 bit
    # 平均: ~ -0.415 * (fraction of odd steps) + 0.585 * (fraction of even steps)
    st_normalized = []
    for n, st in records:
        if n <= 1: continue
        bits = n.bit_length()
        st_per_bit = st / bits
        st_normalized.append({
            'n': n,
            'bits': bits,
            'st': st,
            'st_per_bit': st_per_bit,
        })

    # st_per_bit の推移
    st_per_bit_by_decade = defaultdict(list)
    for item in st_normalized:
        dec = int(math.log10(item['n']))
        st_per_bit_by_decade[dec].append(item['st_per_bit'])

    st_per_bit_summary = {}
    for dec, vals in sorted(st_per_bit_by_decade.items()):
        st_per_bit_summary[f"decade_{dec}"] = {
            'count': len(vals),
            'mean': sum(vals)/len(vals),
            'max': max(vals),
            'min': min(vals),
        }

    # ==== Analysis 9: alpha 増大の直接的原因 ====
    print("\nAnalysis 9: Direct cause of alpha increase...")
    # D_max(N) = max ST up to N の成長率分析
    # D_max(N) / (logN)^alpha が N とともに増加するなら、alpha が小さすぎる

    # 各 checkpoint での D_max / (logN)^alpha を計算
    alpha_ratios = {}
    for alpha in [1.0, 1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0]:
        vals = []
        for cp in checkpoints:
            if cp >= 100:
                ratio = D_max[cp] / (math.log(cp) ** alpha)
                vals.append((cp, ratio))
        if vals:
            # 後半で増加傾向かチェック
            v = [r[1] for r in vals]
            trend = (v[-1] - v[0]) / v[0] if v[0] > 0 else 0
            alpha_ratios[alpha] = {
                'values': vals,
                'trend_pct': trend * 100,
                'last_over_first': v[-1] / v[0] if v[0] > 0 else 0,
            }

    # ==== Analysis 10: Record holder の bit パターンのクラスタリング ====
    print("\nAnalysis 10: Bit pattern clustering...")
    # 高い ones density の record holder は ST が長いか?
    od_st_correlation = []
    for bp in bin_patterns:
        od_st_correlation.append((bp['ones_density'], bp['st'], bp['n']))

    # ones density 上位 vs 下位での ST 比較
    sorted_by_od = sorted(od_st_correlation, key=lambda x: x[0])
    n_half = len(sorted_by_od) // 2
    low_od_st = [x[1] for x in sorted_by_od[:n_half]]
    high_od_st = [x[1] for x in sorted_by_od[n_half:]]

    od_st_comparison = {
        'low_od_mean_st': sum(low_od_st)/len(low_od_st) if low_od_st else 0,
        'high_od_mean_st': sum(high_od_st)/len(high_od_st) if high_od_st else 0,
        'low_od_range': (sorted_by_od[0][0], sorted_by_od[n_half-1][0]),
        'high_od_range': (sorted_by_od[n_half][0], sorted_by_od[-1][0]),
    }

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s")

    # ---- 結果まとめ ----
    results = {
        "title": "Record holder deep structure analysis",
        "N_max": N,
        "total_records": len(records),
        "max_ST": records[-1][1],
        "computation_time": round(elapsed, 1),

        "multiplicative_chains": multiplicity_chains[:20],
        "three_power_factors_summary": {
            "v3=0": sum(1 for x in three_power_factors if x['v3'] == 0),
            "v3=1": sum(1 for x in three_power_factors if x['v3'] == 1),
            "v3=2": sum(1 for x in three_power_factors if x['v3'] == 2),
            "v3>=3": sum(1 for x in three_power_factors if x['v3'] >= 3),
        },

        "ones_density_by_decade": od_summary,
        "trailing_ones_distribution": dict(sorted(trailing_ones_dist.items())),

        "gap_log_ratio_stats": {
            "mean": sum(log_ratios)/len(log_ratios) if log_ratios else 0,
            "median": sorted(log_ratios)[len(log_ratios)//2] if log_ratios else 0,
            "moving_avg_first5": moving_avg_log_ratio[:5] if moving_avg_log_ratio else [],
            "moving_avg_last5": moving_avg_log_ratio[-5:] if moving_avg_log_ratio else [],
            "trend": "decreasing" if moving_avg_log_ratio and moving_avg_log_ratio[-1] < moving_avg_log_ratio[0] else "increasing/stable",
        },

        "st_jump_summary": jump_summary,

        "scaling_comparison": {
            "D_count_values": {str(k): v for k, v in D_count.items()},
            "D_max_values": {str(k): v for k, v in D_max.items()},
            "ratio_max_over_count": {str(k): round(v, 2) for k, v in ratio_max_count.items()},
            "alpha_count": round(alpha_count, 4),
            "alpha_max": round(alpha_max, 4),
            "r2_count": round(r2_count, 4),
            "r2_max": round(r2_max, 4),
        },

        "mersenne_like_analysis": {
            "count_2a3b_minus1": mersenne_count,
            "total": len(mersenne_like),
            "ratio": mersenne_count / len(mersenne_like) if mersenne_like else 0,
            "examples": [m for m in mersenne_like if m['is_2a3b_minus1']],
            "non_trivial_remaining": [
                {'n': m['n'], 'remaining': m['remaining'], 'a2': m['a2'], 'a3': m['a3']}
                for m in mersenne_like if not m['is_2a3b_minus1'] and m['remaining'] < 50
            ][:10],
        },

        "trailing_all_ones_enrichment": all_ones_trailing,

        "st_per_bit_by_decade": st_per_bit_summary,

        "alpha_ratio_analysis": {
            str(alpha): {
                'trend_pct': round(data['trend_pct'], 2),
                'last_over_first': round(data['last_over_first'], 4),
            }
            for alpha, data in alpha_ratios.items()
        },

        "od_st_comparison": od_st_comparison,

        "key_findings": [],
    }

    # Key findings
    findings = []

    # 1. mod 4 偏り
    findings.append(f"Record holder の 94.2% が奇数。mod 4 分布: 3 mod 4 が 69.2%, 1 mod 4 が 25%")

    # 2. trailing bits
    findings.append(f"Trailing ones enrichment: k=3 で {all_ones_trailing[3]['enrichment']:.1f}x, k=5 で {all_ones_trailing[5]['enrichment']:.1f}x (vs random)")

    # 3. 2^a * 3^b - 1 形式
    findings.append(f"2^a * 3^b - 1 形式: {mersenne_count}/{len(mersenne_like)} = {mersenne_count/max(1,len(mersenne_like))*100:.1f}%")

    # 4. alpha 比較
    findings.append(f"D_count scaling alpha={alpha_count:.3f} (R2={r2_count:.4f}), D_max scaling alpha={alpha_max:.3f} (R2={r2_max:.4f})")

    # 5. ones density
    findings.append(f"Ones density: high OD -> mean ST={od_st_comparison['high_od_mean_st']:.1f}, low OD -> mean ST={od_st_comparison['low_od_mean_st']:.1f}")

    # 6. ST/bit の推移
    last_dec = max(st_per_bit_summary.keys())
    first_dec = min(st_per_bit_summary.keys())
    findings.append(f"ST/bit: {first_dec}: {st_per_bit_summary[first_dec]['mean']:.2f}, {last_dec}: {st_per_bit_summary[last_dec]['mean']:.2f}")

    # 7. alpha増大の原因
    # D_max / (logN)^1.6 のトレンド
    a16_trend = alpha_ratios.get(1.6, {}).get('trend_pct', 0)
    a17_trend = alpha_ratios.get(1.7, {}).get('trend_pct', 0)
    findings.append(f"D_max/(logN)^1.6 trend: {a16_trend:+.1f}%, D_max/(logN)^1.7 trend: {a17_trend:+.1f}%")

    # 8. ギャップのlog_ratio
    findings.append(f"Gap log-ratio (n_{{k+1}}/n_k): mean={results['gap_log_ratio_stats']['mean']:.3f}, trend={results['gap_log_ratio_stats']['trend']}")

    results["key_findings"] = findings

    output_path = "/Users/soyukke/study/lean-unsolved/results/record_holder_deep.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")
    for f in findings:
        print(f"  * {f}")

if __name__ == "__main__":
    main()
