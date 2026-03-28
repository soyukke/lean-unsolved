#!/usr/bin/env python3
"""
探索: Record holderのv2平均≈1.71の構造解明とlog₂(3)への接近速度

Syracuse関数 T(n) = (3n+1) / 2^{v2(3n+1)} のrecord holder（stopping time最大）について:
1. N=10^k (k=4..8) でのrecord holderのv2平均のスケーリング
2. v2平均がlog₂(3)≈1.585にどこまで接近するか
3. record holderの2進表現パターン分析
4. d/u比（down steps / up steps）のスケーリング

JSON結果を出力。
"""

import json
import math
import time
from collections import Counter

LOG2_3 = math.log2(3)  # ≈ 1.58496...

def syracuse_trajectory(n):
    """
    Syracuse軌道を計算。各奇数ステップでのv2値を記録。
    Returns: (total_steps, v2_list, max_value, up_steps, down_steps)
    """
    x = n
    v2_list = []
    up_steps = 0
    down_steps = 0
    max_val = n
    total_steps = 0

    while x != 1:
        if x % 2 == 0:
            x //= 2
            down_steps += 1
        else:
            val = 3 * x + 1
            v2 = 0
            while val % 2 == 0:
                val //= 2
                v2 += 1
            v2_list.append(v2)
            x = val
            up_steps += 1
            down_steps += v2  # v2 divisions in Syracuse step
        total_steps += 1
        if x > max_val:
            max_val = x

    return total_steps, v2_list, max_val, up_steps, down_steps


def syracuse_stopping_time(n):
    """Fast stopping time (standard Collatz steps to reach 1)."""
    x = n
    steps = 0
    while x != 1:
        if x % 2 == 0:
            x //= 2
        else:
            x = 3 * x + 1
        steps += 1
    return steps


def bit_pattern_analysis(n):
    """2進表現の解析"""
    bits = bin(n)[2:]
    length = len(bits)
    ones = bits.count('1')
    # 連続1のラン長
    runs_of_1 = []
    current_run = 0
    for b in bits:
        if b == '1':
            current_run += 1
        else:
            if current_run > 0:
                runs_of_1.append(current_run)
            current_run = 0
    if current_run > 0:
        runs_of_1.append(current_run)

    return {
        "bit_length": length,
        "ones_count": ones,
        "ones_density": ones / length,
        "max_run_of_1": max(runs_of_1) if runs_of_1 else 0,
        "num_runs_of_1": len(runs_of_1),
        "avg_run_of_1": sum(runs_of_1) / len(runs_of_1) if runs_of_1 else 0,
    }


def check_mersenne_form(n):
    """2^a * 3^b - 1 形式かチェック"""
    for a in range(1, 70):
        for b in range(0, 44):
            val = (2**a) * (3**b) - 1
            if val == n:
                return {"is_2a3b_minus1": True, "a": a, "b": b}
            if val > n * 2:
                break
    return {"is_2a3b_minus1": False, "a": None, "b": None}


def find_record_holders(N_max):
    """N_maxまでのrecord holder（stopping time最大更新）を見つける"""
    records = []
    max_st = 0
    for n in range(2, N_max + 1):
        st = syracuse_stopping_time(n)
        if st > max_st:
            max_st = st
            records.append((n, st))
    return records


def analyze_records(records, label):
    """record holderのv2平均やd/u比を解析"""
    results = []
    for n, st in records:
        total_steps, v2_list, max_val, up_steps, down_steps = syracuse_trajectory(n)
        v2_avg = sum(v2_list) / len(v2_list) if v2_list else 0
        v2_med = sorted(v2_list)[len(v2_list) // 2] if v2_list else 0
        du_ratio = down_steps / up_steps if up_steps > 0 else 0
        bp = bit_pattern_analysis(n)

        results.append({
            "n": n,
            "stopping_time": st,
            "up_steps": up_steps,
            "down_steps": down_steps,
            "d_over_u": round(du_ratio, 6),
            "v2_mean": round(v2_avg, 6),
            "v2_median": v2_med,
            "v2_max": max(v2_list) if v2_list else 0,
            "v2_distribution": dict(Counter(v2_list)),
            "log_max_over_log_n": round(math.log2(max_val) / math.log2(n), 4) if n > 1 else 0,
            "bit_length": bp["bit_length"],
            "ones_density": round(bp["ones_density"], 4),
            "max_run_of_1": bp["max_run_of_1"],
        })
    return results


def main():
    t0 = time.time()

    # スケーリング解析: 各N_maxでのrecord holderのv2平均推移
    scaling_ranges = [
        (10_000, "10^4"),
        (100_000, "10^5"),
        (1_000_000, "10^6"),
        (10_000_000, "10^7"),
    ]

    all_scaling = []
    all_records_detail = {}

    cumulative_records = []
    max_st_global = 0

    # 一度に10^7まで走査し、各閾値でスナップショットを取る
    print("Computing record holders up to 10^7...")
    thresholds = [r[0] for r in scaling_ranges]
    threshold_idx = 0

    for n in range(2, thresholds[-1] + 1):
        st = syracuse_stopping_time(n)
        if st > max_st_global:
            max_st_global = st
            cumulative_records.append((n, st))

        while threshold_idx < len(thresholds) and n == thresholds[threshold_idx]:
            label = scaling_ranges[threshold_idx][1]
            # この時点でのrecord holdersを解析
            # 最後の20件のrecord holderのv2平均を計算
            recent = cumulative_records[-20:] if len(cumulative_records) >= 20 else cumulative_records
            top = cumulative_records[-1]  # 最大stopping timeのrecord holder

            # top record holderの詳細解析
            total_steps, v2_list, max_val, up_steps, down_steps = syracuse_trajectory(top[0])
            v2_avg_top = sum(v2_list) / len(v2_list) if v2_list else 0
            du_top = down_steps / up_steps if up_steps > 0 else 0

            # recent record holdersのv2平均の平均
            v2_avgs = []
            du_ratios = []
            for rn, rst in recent:
                _, vl, _, u, d = syracuse_trajectory(rn)
                if vl:
                    v2_avgs.append(sum(vl) / len(vl))
                if u > 0:
                    du_ratios.append(d / u)

            avg_of_v2_avgs = sum(v2_avgs) / len(v2_avgs) if v2_avgs else 0
            avg_du = sum(du_ratios) / len(du_ratios) if du_ratios else 0

            all_scaling.append({
                "N_max": thresholds[threshold_idx],
                "label": label,
                "num_records": len(cumulative_records),
                "top_record_n": top[0],
                "top_stopping_time": top[1],
                "top_v2_mean": round(v2_avg_top, 6),
                "top_d_over_u": round(du_top, 6),
                "recent20_avg_v2_mean": round(avg_of_v2_avgs, 6),
                "recent20_avg_d_over_u": round(avg_du, 6),
                "gap_to_log2_3_top": round(v2_avg_top - LOG2_3, 6),
                "gap_to_log2_3_recent": round(avg_of_v2_avgs - LOG2_3, 6),
            })

            # 最後の10件の詳細
            detail_recent = cumulative_records[-10:]
            all_records_detail[label] = analyze_records(detail_recent, label)

            print(f"  {label}: {len(cumulative_records)} records, top n={top[0]}, "
                  f"v2_mean={v2_avg_top:.4f}, gap={v2_avg_top - LOG2_3:.4f}")

            threshold_idx += 1

    # 10^8はコストが高いので、サンプリングベースで推定
    # 10^7〜10^8の区間でrecord holderが出る確率的推定
    print("\nEstimating 10^8 behavior from 10^7 data...")

    # 2^a * 3^b - 1 形式チェック（上位record holders）
    print("\nChecking 2^a·3^b-1 form for top records...")
    mersenne_checks = []
    for n, st in cumulative_records[-15:]:
        mc = check_mersenne_form(n)
        mersenne_checks.append({
            "n": n,
            "stopping_time": st,
            **mc
        })

    # v2分布の集約（全record holderの合算）
    print("\nAggregating v2 distribution across all record holders...")
    all_v2_counts = Counter()
    total_v2_samples = 0
    for rn, rst in cumulative_records:
        _, vl, _, _, _ = syracuse_trajectory(rn)
        for v in vl:
            all_v2_counts[v] += 1
            total_v2_samples += 1

    v2_distribution_all = {}
    for k in sorted(all_v2_counts.keys()):
        v2_distribution_all[str(k)] = {
            "count": all_v2_counts[k],
            "frequency": round(all_v2_counts[k] / total_v2_samples, 6),
            "geometric_prediction": round((1/2)**k, 6),  # E[v2]=geom(1/2)
        }

    # Cramér関数 I(x) = x*log(x/2) - x + 2 の評価点
    # record holderのv2平均1.71付近
    x_rh = all_scaling[-1]["top_v2_mean"] if all_scaling else 1.71
    cramer_at_rh = x_rh * math.log(x_rh / 2) - x_rh + 2
    cramer_at_log2_3 = LOG2_3 * math.log(LOG2_3 / 2) - LOG2_3 + 2

    # スケーリング指数の推定: gap ~ N^(-alpha)
    # gap = v2_mean - log2(3) vs N
    if len(all_scaling) >= 2:
        gaps = [(s["N_max"], s["top_v2_mean"] - LOG2_3) for s in all_scaling if s["top_v2_mean"] > LOG2_3]
        if len(gaps) >= 2:
            # log-log回帰
            log_N = [math.log(g[0]) for g in gaps]
            log_gap = [math.log(g[1]) for g in gaps]
            # 線形回帰 (手動)
            n_pts = len(log_N)
            sx = sum(log_N)
            sy = sum(log_gap)
            sxx = sum(x*x for x in log_N)
            sxy = sum(x*y for x, y in zip(log_N, log_gap))
            slope = (n_pts * sxy - sx * sy) / (n_pts * sxx - sx * sx)
            intercept = (sy - slope * sx) / n_pts
            scaling_exponent = slope
        else:
            scaling_exponent = None
    else:
        scaling_exponent = None

    elapsed = time.time() - t0

    # 結果を組み立て
    result = {
        "exploration_id": "096",
        "title": "Record holderのv2平均スケーリング解析とlog₂(3)への接近速度",
        "method": "N=10^4〜10^7でrecord holderのv2平均・d/u比・2進パターンのスケーリング",
        "constants": {
            "log2_3": round(LOG2_3, 8),
            "E_v2_random": 2.0,
            "cramer_I_at_log2_3": round(cramer_at_log2_3, 6),
            "cramer_I_at_observed": round(cramer_at_rh, 6),
        },
        "scaling_summary": all_scaling,
        "scaling_exponent_estimate": {
            "description": "gap(N) = v2_mean(top) - log2(3) ~ N^alpha のalpha推定",
            "alpha": round(scaling_exponent, 6) if scaling_exponent is not None else None,
            "note": "負ならgapは縮小（log2(3)に接近）、0に近ければgapは安定"
        },
        "v2_distribution_all_records": v2_distribution_all,
        "mersenne_form_checks": mersenne_checks,
        "top10_records_by_range": all_records_detail,
        "key_findings": [],
        "elapsed_seconds": round(elapsed, 2),
    }

    # Key findings を生成
    findings = []
    if all_scaling:
        last = all_scaling[-1]
        findings.append(
            f"N=10^7でのtop record holder (n={last['top_record_n']}): "
            f"v2_mean={last['top_v2_mean']:.4f}, gap to log₂(3)={last['gap_to_log2_3_top']:.4f}"
        )
        findings.append(
            f"Recent 20 records平均: v2_mean={last['recent20_avg_v2_mean']:.4f}, "
            f"d/u={last['recent20_avg_d_over_u']:.4f}"
        )
    if scaling_exponent is not None:
        findings.append(
            f"スケーリング指数 alpha≈{scaling_exponent:.4f} "
            f"({'gap縮小' if scaling_exponent < 0 else 'gap安定/拡大'})"
        )

    # v2=1の頻度確認（record holderでv2=1が多いならlog2(3)接近の主因）
    if "1" in v2_distribution_all:
        v2_1_freq = v2_distribution_all["1"]["frequency"]
        geo_pred = v2_distribution_all["1"]["geometric_prediction"]
        findings.append(
            f"v2=1の頻度: {v2_1_freq:.4f} (幾何分布予測: {geo_pred:.4f}, "
            f"偏差: {v2_1_freq - geo_pred:+.4f})"
        )

    mersenne_count = sum(1 for m in mersenne_checks if m["is_2a3b_minus1"])
    findings.append(f"上位15 record holderのうち 2^a·3^b-1 形式: {mersenne_count}個")

    result["key_findings"] = findings

    # JSON出力
    output = json.dumps(result, indent=2, ensure_ascii=False)
    print("\n" + output)

    # ファイル保存
    with open("/Users/soyukke/study/lean-unsolved/results/exploration_096.json", "w") as f:
        f.write(output)

    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
