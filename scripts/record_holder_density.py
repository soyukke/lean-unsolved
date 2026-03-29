"""
Record holder n の出現密度分析
D(N) = max stopping time up to N を更新する n の統計的構造を調べる。
- ギャップ分布
- mod 構造 (mod 2, 4, 8, 16, ...)
- trailing bits (2-adic valuation)
- 探索170の alpha 増大の原因解明
"""

import json
import math
import time
from collections import Counter, defaultdict

def collatz_stopping_time(n):
    """Total stopping time: n が 1 に到達するまでのステップ数"""
    count = 0
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        count += 1
    return count

def find_record_holders(N_max):
    """1 から N_max まで走査し、stopping time の record holder を見つける"""
    records = []  # (n, stopping_time)
    current_max = 0
    for n in range(1, N_max + 1):
        st = collatz_stopping_time(n)
        if st > current_max:
            current_max = st
            records.append((n, st))
    return records

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

def v3(n):
    """3-adic valuation of n"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 3 == 0:
        n //= 3
        v += 1
    return v

def bit_length(n):
    return n.bit_length()

def trailing_bits(n, k):
    """n の下位 k ビットを取得"""
    return n & ((1 << k) - 1)

def main():
    start_time = time.time()

    # ---- Phase 1: Record holders の計算 ----
    print("Phase 1: Computing record holders up to 10^7...")
    N = 10_000_000
    records = find_record_holders(N)
    D_N = len(records)
    print(f"  D({N}) = {D_N}")
    print(f"  Time: {time.time() - start_time:.1f}s")

    # Record holder n のリスト
    rec_ns = [r[0] for r in records]
    rec_sts = [r[1] for r in records]

    # ---- Phase 2: ギャップ分析 ----
    print("\nPhase 2: Gap analysis...")
    gaps = [rec_ns[i+1] - rec_ns[i] for i in range(len(rec_ns)-1)]
    gap_ratios = [rec_ns[i+1] / rec_ns[i] for i in range(len(rec_ns)-1) if rec_ns[i] > 0]

    # ギャップの統計
    gap_stats = {
        "count": len(gaps),
        "mean": sum(gaps) / len(gaps),
        "median": sorted(gaps)[len(gaps)//2],
        "max": max(gaps),
        "min": min(gaps),
    }

    # ギャップ比 (gap / n) の分析
    relative_gaps = [gaps[i] / rec_ns[i] for i in range(len(gaps)) if rec_ns[i] > 0]

    # ---- Phase 3: mod 構造分析 ----
    print("\nPhase 3: Mod structure analysis...")
    mod_analysis = {}
    for m in [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96]:
        residues = [n % m for n in rec_ns if n > 1]
        counter = Counter(residues)
        # 各残基の出現頻度
        total = len(residues)
        freq = {r: counter.get(r, 0) / total for r in range(m)}
        # 奇数比率
        odd_count = sum(1 for n in rec_ns if n > 1 and n % 2 == 1)
        # 最頻残基
        most_common = counter.most_common(5)
        mod_analysis[m] = {
            "most_common": most_common,
            "entropy": -sum(f * math.log2(f) for f in freq.values() if f > 0),
            "max_entropy": math.log2(m),
        }

    odd_ratio = sum(1 for n in rec_ns if n > 1 and n % 2 == 1) / (len(rec_ns) - 1)

    # ---- Phase 4: 2-adic valuation 分析 ----
    print("\nPhase 4: 2-adic valuation analysis...")
    v2_vals = [v2(n) for n in rec_ns if n > 0]
    v2_counter = Counter(v2_vals)
    v2_distribution = dict(sorted(v2_counter.items()))

    # 比較: 一様ランダムなら v2=k の確率は 1/2^(k+1) (k>=0), ただし奇数が 1/2
    # record holder は奇数が多いはず

    # ---- Phase 5: trailing bits パターン ----
    print("\nPhase 5: Trailing bits pattern analysis...")
    trailing_analysis = {}
    for k in [2, 3, 4, 5, 6, 7, 8]:
        patterns = [trailing_bits(n, k) for n in rec_ns if n >= (1 << k)]
        counter = Counter(patterns)
        total = len(patterns)
        # 奇数パターンのみ (record holder は奇数が多い)
        odd_patterns = {p: c for p, c in counter.items() if p % 2 == 1}
        even_patterns = {p: c for p, c in counter.items() if p % 2 == 0}
        trailing_analysis[k] = {
            "total": total,
            "odd_count": sum(odd_patterns.values()),
            "even_count": sum(even_patterns.values()),
            "top_5_odd": sorted(odd_patterns.items(), key=lambda x: -x[1])[:5],
            "top_5_even": sorted(even_patterns.items(), key=lambda x: -x[1])[:5],
        }

    # ---- Phase 6: D(N) の成長速度分析 ----
    print("\nPhase 6: D(N) growth rate analysis...")
    checkpoints = [10, 100, 1000, 10000, 100000, 1000000, 10000000]
    DN_values = {}
    idx = 0
    for cp in checkpoints:
        while idx < len(rec_ns) and rec_ns[idx] <= cp:
            idx += 1
        DN_values[cp] = idx

    # D(N) / (log N)^alpha の安定性チェック
    alpha_check = {}
    for alpha in [1.0, 1.2, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.2, 2.4]:
        ratios = []
        for cp in checkpoints:
            if cp >= 100 and DN_values[cp] > 0:
                ratio = DN_values[cp] / (math.log(cp) ** alpha)
                ratios.append((cp, ratio))
        if ratios:
            vals = [r[1] for r in ratios]
            mean = sum(vals) / len(vals)
            std = (sum((v - mean)**2 for v in vals) / len(vals)) ** 0.5
            cv = std / mean if mean > 0 else float('inf')
            alpha_check[alpha] = {
                "ratios": ratios,
                "mean": mean,
                "std": std,
                "cv": cv,
            }

    # ---- Phase 7: Record holder の局所密度 ----
    print("\nPhase 7: Local density analysis...")
    # 区間 [10^k, 10^(k+1)] 内の record holder 数
    decade_counts = {}
    for k in range(8):  # 10^0 to 10^7
        lo = 10 ** k
        hi = 10 ** (k + 1)
        count = sum(1 for n in rec_ns if lo <= n < hi)
        decade_counts[k] = {
            "range": f"[10^{k}, 10^{k+1})",
            "count": count,
            "log_interval_width": math.log(hi) - math.log(lo),
            "density_per_logunit": count / (math.log(hi) - math.log(lo)),
        }

    # ---- Phase 8: Stopping time 増分分析 ----
    print("\nPhase 8: Stopping time increment analysis...")
    st_increments = [rec_sts[i+1] - rec_sts[i] for i in range(len(rec_sts)-1)]
    st_inc_stats = {
        "mean": sum(st_increments) / len(st_increments) if st_increments else 0,
        "median": sorted(st_increments)[len(st_increments)//2] if st_increments else 0,
        "max": max(st_increments) if st_increments else 0,
        "min": min(st_increments) if st_increments else 0,
        "mode": Counter(st_increments).most_common(5),
    }

    # stopping time 増分 vs n のスケーリング
    # 新しい record が出るとき、ST がどれくらい増えるか
    st_vs_logn = [(math.log(rec_ns[i]), rec_sts[i]) for i in range(len(rec_ns)) if rec_ns[i] > 1]

    # ---- Phase 9: Record holder n の mod 構造の変化（Nの増加に伴う） ----
    print("\nPhase 9: Evolution of mod structure with N...")
    # 最初の100個、次の100個、... での mod 構造の比較
    chunk_size = 100
    n_chunks = min(len(rec_ns) // chunk_size, 6)
    mod_evolution = {}
    for m in [4, 8, 16]:
        evolution = []
        for c in range(n_chunks):
            chunk = rec_ns[c*chunk_size : (c+1)*chunk_size]
            residues = [n % m for n in chunk]
            counter = Counter(residues)
            odd_ratio_chunk = sum(1 for n in chunk if n % 2 == 1) / len(chunk)
            evolution.append({
                "chunk": f"{c*chunk_size}-{(c+1)*chunk_size}",
                "n_range": f"[{chunk[0]}, {chunk[-1]}]",
                "odd_ratio": odd_ratio_chunk,
                "top_residues": counter.most_common(5),
            })
        mod_evolution[m] = evolution

    # ---- Phase 10: 3 mod 4 vs 1 mod 4 分析 ----
    print("\nPhase 10: Detailed mod 4 analysis...")
    mod4_counts = Counter(n % 4 for n in rec_ns if n > 2)
    mod4_total = sum(mod4_counts.values())
    mod4_freq = {k: v/mod4_total for k, v in sorted(mod4_counts.items())}

    # 3 mod 4 が多い理由: 3n+1 のステップが 1 回で 2^1 しか割れない場合が多い
    # -> ST が長くなりやすい
    # n ≡ 3 (mod 4): 3n+1 ≡ 10 ≡ 2 (mod 4) -> 1回しか2で割れない
    # n ≡ 1 (mod 4): 3n+1 ≡ 4 ≡ 0 (mod 4) -> 2回以上2で割れる

    # ---- Phase 11: ビット長と ST の相関 ----
    print("\nPhase 11: Bit length vs stopping time correlation...")
    bit_st_data = [(bit_length(n), st) for n, st in records if n > 1]
    bits = [b for b, s in bit_st_data]
    sts = [s for b, s in bit_st_data]

    # 線形回帰: ST = a * bits + b
    n_data = len(bits)
    sum_x = sum(bits)
    sum_y = sum(sts)
    sum_xy = sum(b * s for b, s in bit_st_data)
    sum_x2 = sum(b * b for b, s in bit_st_data)

    a = (n_data * sum_xy - sum_x * sum_y) / (n_data * sum_x2 - sum_x ** 2)
    b = (sum_y - a * sum_x) / n_data

    # R^2
    ss_res = sum((s - (a * bi + b)) ** 2 for bi, s in bit_st_data)
    ss_tot = sum((s - sum_y / n_data) ** 2 for bi, s in bit_st_data)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    bit_st_regression = {
        "slope": a,
        "intercept": b,
        "R2": r2,
        "interpretation": f"Record ST ~ {a:.3f} * bits + {b:.1f}",
    }

    # ---- Phase 12: alpha 増大の原因分析 ----
    print("\nPhase 12: Alpha increase cause analysis...")
    # 仮説: 大きな N では、record holder が出現するパターンが変化する
    # -> record holder 間の gap が相対的に小さくなる (密度が上がる)

    # 各 decade での record holder 密度 (per log unit)
    densities_per_decade = []
    for k in range(1, 8):
        lo = 10 ** k
        hi = 10 ** (k + 1)
        count = sum(1 for n in rec_ns if lo <= n < hi)
        density = count / math.log(10)  # per log-unit
        densities_per_decade.append({
            "decade": k,
            "count": count,
            "density_per_log10": density,
        })

    # 密度の成長率
    if len(densities_per_decade) >= 2:
        density_growth = []
        for i in range(1, len(densities_per_decade)):
            if densities_per_decade[i-1]["density_per_log10"] > 0:
                ratio = densities_per_decade[i]["density_per_log10"] / densities_per_decade[i-1]["density_per_log10"]
                density_growth.append({
                    "decades": f"{densities_per_decade[i-1]['decade']}->{densities_per_decade[i]['decade']}",
                    "ratio": ratio,
                })

    # ---- Phase 13: 大きな gap が出る n の特徴 ----
    print("\nPhase 13: Large gap characterization...")
    # ギャップが大きい record holder を分析
    gap_data = [(rec_ns[i], rec_ns[i+1], gaps[i], gaps[i]/rec_ns[i]) for i in range(len(gaps))]
    gap_data_sorted = sorted(gap_data, key=lambda x: -x[3])  # 相対ギャップでソート

    large_gaps = []
    for n_prev, n_next, gap, rel_gap in gap_data_sorted[:20]:
        large_gaps.append({
            "n_prev": n_prev,
            "n_next": n_next,
            "gap": gap,
            "relative_gap": rel_gap,
            "n_next_mod4": n_next % 4,
            "n_next_mod8": n_next % 8,
            "n_next_mod16": n_next % 16,
            "n_next_v2": v2(n_next),
            "n_next_bits": bit_length(n_next),
        })

    # ---- Phase 14: Record holder の連続 odd/even パターン ----
    print("\nPhase 14: Consecutive parity patterns...")
    parity_seq = [n % 2 for n in rec_ns if n > 1]
    # 連続する奇数の run length
    odd_runs = []
    even_runs = []
    current_run = 1
    for i in range(1, len(parity_seq)):
        if parity_seq[i] == parity_seq[i-1]:
            current_run += 1
        else:
            if parity_seq[i-1] == 1:
                odd_runs.append(current_run)
            else:
                even_runs.append(current_run)
            current_run = 1
    if parity_seq[-1] == 1:
        odd_runs.append(current_run)
    else:
        even_runs.append(current_run)

    parity_pattern = {
        "odd_ratio": sum(parity_seq) / len(parity_seq),
        "odd_run_mean": sum(odd_runs) / len(odd_runs) if odd_runs else 0,
        "odd_run_max": max(odd_runs) if odd_runs else 0,
        "even_run_mean": sum(even_runs) / len(even_runs) if even_runs else 0,
        "even_run_max": max(even_runs) if even_runs else 0,
        "odd_run_dist": dict(Counter(odd_runs).most_common(10)),
        "even_run_dist": dict(Counter(even_runs).most_common(10)),
    }

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s")

    # ---- 結果まとめ ----
    results = {
        "title": "Record holder n density analysis for D(N)",
        "N_max": N,
        "D_N": D_N,
        "computation_time_sec": round(elapsed, 1),

        "gap_statistics": gap_stats,
        "relative_gap_stats": {
            "mean": sum(relative_gaps) / len(relative_gaps),
            "median": sorted(relative_gaps)[len(relative_gaps)//2],
            "max": max(relative_gaps),
            "min": min(relative_gaps),
        },

        "odd_ratio": odd_ratio,
        "mod4_frequency": mod4_freq,
        "mod_analysis_entropy": {
            m: {
                "entropy": data["entropy"],
                "max_entropy": data["max_entropy"],
                "entropy_ratio": data["entropy"] / data["max_entropy"],
                "most_common_3": data["most_common"][:3],
            }
            for m, data in mod_analysis.items()
        },

        "v2_distribution": v2_distribution,
        "trailing_bits_analysis": {
            k: {
                "odd_ratio": data["odd_count"] / data["total"] if data["total"] > 0 else 0,
                "top_3_odd": data["top_5_odd"][:3],
                "top_3_even": data["top_5_even"][:3],
            }
            for k, data in trailing_analysis.items()
        },

        "DN_growth": {
            "DN_values": {str(k): v for k, v in DN_values.items()},
            "best_alpha_cv": min(alpha_check.items(), key=lambda x: x[1]["cv"]),
            "alpha_cv_table": {str(a): round(data["cv"], 4) for a, data in alpha_check.items()},
        },

        "decade_density": densities_per_decade,
        "density_growth_ratios": density_growth if 'density_growth' in dir() else [],

        "stopping_time_increment": st_inc_stats,
        "bit_st_regression": bit_st_regression,

        "mod_evolution_mod8": mod_evolution.get(8, []),

        "large_relative_gaps_top10": large_gaps[:10],

        "parity_pattern": parity_pattern,

        "alpha_cause_analysis": {
            "hypothesis": "alpha increases because record holder density per log-unit grows faster than (logN)^c for any fixed c",
            "decade_density_per_log10": [d["density_per_log10"] for d in densities_per_decade],
            "density_growth": density_growth if 'density_growth' in dir() else [],
        },
    }

    # 追加分析: 最後の50個の record holder の特徴
    last_50 = records[-50:]
    last_50_mod4 = Counter(n % 4 for n, st in last_50)
    last_50_mod8 = Counter(n % 8 for n, st in last_50)
    results["last_50_records"] = {
        "n_range": f"[{last_50[0][0]}, {last_50[-1][0]}]",
        "mod4_dist": dict(last_50_mod4),
        "mod8_dist": dict(last_50_mod8),
        "mean_st_increment": sum(last_50[i+1][1] - last_50[i][1] for i in range(len(last_50)-1)) / (len(last_50)-1),
        "mean_relative_gap": sum((last_50[i+1][0] - last_50[i][0]) / last_50[i][0] for i in range(len(last_50)-1)) / (len(last_50)-1),
    }

    # 先頭20個の record holder を出力
    results["first_20_records"] = [(n, st) for n, st in records[:20]]
    results["last_20_records"] = [(n, st) for n, st in records[-20:]]

    output_path = "/Users/soyukke/study/lean-unsolved/results/record_holder_density.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")
    print(f"\nKey findings:")
    print(f"  D(10^7) = {D_N}")
    print(f"  Odd ratio among record holders: {odd_ratio:.4f}")
    print(f"  mod 4 distribution: {mod4_freq}")
    print(f"  Best alpha (by CV): {results['DN_growth']['best_alpha_cv']}")
    print(f"  Bit-ST regression: slope={a:.3f}, R2={r2:.4f}")

    return results

if __name__ == "__main__":
    results = main()
