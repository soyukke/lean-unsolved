#!/usr/bin/env python3
"""
探索: mod 2^k での一意下降経路の解析

目的:
1. mod 2^k (k=8..16) で、kステップ以内にn未満に到達する残基の割合を計算
2. k->infinity での漸近100%到達の数値的証拠を提供
3. 非排除残基の密度が指数減衰することの検証
4. v2=1 の非排除残基の mod 4 分布

定義:
- 「排除」= mod 2^k の全ての代表元が k ステップ以内に初期値を下回ることが
  剰余類の情報だけで保証される（一意な下降経路を持つ）
- 「非排除」= 剰余類内に下降ステップ数が異なるものが存在

既知結果:
- mod 1024 (k=10) で 87.5% 決定的下降
- mod 2^20 で 94.4% 排除
- 非排除密度 ~ 0.883^k 指数収束
- v2=1 の非排除残基は mod 4 ≡ 3 に集中
"""

import json
import time
import math
from collections import Counter, defaultdict


def syracuse(n):
    """Syracuse関数: 奇数 n -> (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    return val, v


def descent_steps(n, max_steps=200):
    """奇数 n から Syracuse 反復で初めて n を下回るまでのステップ数"""
    original = n
    current = n
    for step in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return step
    return -1


def is_deterministic_class(r, mod, num_samples=100, max_steps=None):
    """
    剰余類 r (mod mod) が決定的下降を持つか判定。
    num_samples 個の代表元を検査し、全て同じステップ数なら決定的。
    max_steps: 最大何ステップまで調べるか（Noneならmod2^kのkに相当）
    戻り値: (is_det, step_value_or_None, v2_of_first_step)
    """
    if max_steps is None:
        max_steps = 200

    steps_seen = set()
    v2_first = None

    for i in range(num_samples):
        n = r + mod * (2 * i + 1)
        if n <= 0:
            continue
        s = descent_steps(n, max_steps=max_steps)
        if s > 0:
            steps_seen.add(s)
            if v2_first is None:
                # 最初のステップの v2
                val = 3 * n + 1
                v = 0
                while val % 2 == 0:
                    val //= 2
                    v += 1
                v2_first = v
        else:
            steps_seen.add(-1)

        if len(steps_seen) > 1:
            return False, None, v2_first

    if len(steps_seen) == 1:
        return True, steps_seen.pop(), v2_first
    return False, None, v2_first


def analyze_mod2k_descent(k, num_samples=80):
    """
    mod 2^k での一意下降経路解析
    """
    mod = 2 ** k
    total_odd = mod // 2

    det_count = 0
    non_det_count = 0
    det_step_dist = Counter()
    non_det_v2_dist = Counter()
    non_det_mod4_dist = Counter()
    non_det_residues = []

    # kステップ以内に下降が保証される残基数
    det_within_k_steps = 0

    for r in range(1, mod, 2):
        is_det, step_val, v2_first = is_deterministic_class(
            r, mod, num_samples=num_samples, max_steps=max(k * 2, 50)
        )

        if is_det:
            det_count += 1
            det_step_dist[step_val] += 1
            if step_val <= k:
                det_within_k_steps += 1
        else:
            non_det_count += 1
            if v2_first is not None:
                non_det_v2_dist[v2_first] += 1
            non_det_mod4_dist[r % 4] += 1
            if len(non_det_residues) < 50:
                non_det_residues.append({
                    "r": r,
                    "r_mod4": r % 4,
                    "r_mod8": r % 8,
                    "r_mod32": r % 32,
                    "v2_first": v2_first,
                    "binary_suffix": format(r, f'0{k}b')[-min(k, 8):],
                })

    # 非排除密度
    non_det_density = non_det_count / total_odd if total_odd > 0 else 0

    return {
        "k": k,
        "mod": mod,
        "total_odd": total_odd,
        "deterministic": det_count,
        "non_deterministic": non_det_count,
        "det_ratio": det_count / total_odd,
        "det_within_k_steps": det_within_k_steps,
        "det_within_k_ratio": det_within_k_steps / total_odd,
        "non_det_density": non_det_density,
        "det_step_distribution": dict(det_step_dist),
        "non_det_v2_distribution": dict(non_det_v2_dist),
        "non_det_mod4_distribution": dict(non_det_mod4_dist),
        "non_det_samples": non_det_residues,
    }


def fit_exponential_decay(k_values, densities):
    """非排除密度の指数減衰フィッティング: density ~ a * base^k"""
    # log(density) = log(a) + k * log(base)
    # 最小二乗法
    valid = [(k, d) for k, d in zip(k_values, densities) if d > 0]
    if len(valid) < 2:
        return None, None

    ks = [v[0] for v in valid]
    log_ds = [math.log(v[1]) for v in valid]

    n = len(ks)
    sum_k = sum(ks)
    sum_logd = sum(log_ds)
    sum_k2 = sum(ki**2 for ki in ks)
    sum_k_logd = sum(ki * li for ki, li in zip(ks, log_ds))

    denom = n * sum_k2 - sum_k ** 2
    if abs(denom) < 1e-15:
        return None, None

    slope = (n * sum_k_logd - sum_k * sum_logd) / denom
    intercept = (sum_logd - slope * sum_k) / n

    base = math.exp(slope)
    a = math.exp(intercept)

    return a, base


def main():
    print("=" * 80)
    print("探索: mod 2^k での一意下降経路解析")
    print("=" * 80)
    print()

    results = {
        "title": "mod 2^k での一意下降経路解析",
        "approach": "mod 2^k (k=3..16) で決定的下降割合と非排除密度の指数減衰を計算",
        "convergence_table": [],
        "exponential_fit": {},
        "non_det_mod4_analysis": {},
        "non_det_v2_analysis": {},
        "findings": [],
        "hypotheses": [],
        "dead_ends": [],
    }

    # k=3..14 で計算（k=15,16 はコスト大なので別途検討）
    configs = [
        (3, 200),  (4, 200),  (5, 200),  (6, 200),
        (7, 150),  (8, 150),  (9, 120),  (10, 100),
        (11, 80),  (12, 60),  (13, 40),  (14, 30),
    ]

    print(f"{'k':>3} | {'mod':>8} | {'奇数':>8} | {'決定的':>8} | {'非排除':>8} | "
          f"{'決定率':>10} | {'k以内率':>10} | {'非排除密度':>12} | {'時間':>8}")
    print("-" * 100)

    k_values = []
    densities = []
    det_ratios = []

    for k, samples in configs:
        t0 = time.time()
        res = analyze_mod2k_descent(k, num_samples=samples)
        elapsed = time.time() - t0

        k_values.append(k)
        densities.append(res["non_det_density"])
        det_ratios.append(res["det_ratio"])

        row = {
            "k": k,
            "mod": res["mod"],
            "total_odd": res["total_odd"],
            "deterministic": res["deterministic"],
            "non_deterministic": res["non_deterministic"],
            "det_ratio": round(res["det_ratio"], 8),
            "det_within_k_steps": res["det_within_k_steps"],
            "det_within_k_ratio": round(res["det_within_k_ratio"], 8),
            "non_det_density": round(res["non_det_density"], 8),
            "samples_per_class": samples,
            "elapsed_sec": round(elapsed, 2),
        }
        results["convergence_table"].append(row)
        results["non_det_mod4_analysis"][str(k)] = res["non_det_mod4_distribution"]
        results["non_det_v2_analysis"][str(k)] = res["non_det_v2_distribution"]

        print(f"{k:>3} | {res['mod']:>8} | {res['total_odd']:>8} | "
              f"{res['deterministic']:>8} | {res['non_deterministic']:>8} | "
              f"{res['det_ratio']:>10.6f} | {res['det_within_k_ratio']:>10.6f} | "
              f"{res['non_det_density']:>12.8f} | {elapsed:>7.1f}s")

    # ============================================================
    # 指数減衰フィッティング
    # ============================================================
    print("\n" + "=" * 80)
    print("非排除密度の指数減衰フィッティング")
    print("=" * 80)

    # k >= 5 のデータでフィッティング
    fit_k = [k for k in k_values if k >= 5]
    fit_d = [densities[i] for i, k in enumerate(k_values) if k >= 5]

    a, base = fit_exponential_decay(fit_k, fit_d)
    if a is not None:
        print(f"\n  フィッティング結果: density ~ {a:.6f} * {base:.6f}^k")
        print(f"  減衰率 base = {base:.6f}")
        print(f"  既知値 0.883 との比較: 差 = {abs(base - 0.883):.6f}")

        results["exponential_fit"] = {
            "a": round(a, 8),
            "base": round(base, 8),
            "formula": f"density ~ {a:.6f} * {base:.6f}^k",
            "fit_range": f"k={min(fit_k)}..{max(fit_k)}",
            "comparison_to_0883": round(abs(base - 0.883), 6),
        }

        # 予測値 vs 実測値の比較
        print(f"\n  {'k':>3} | {'実測密度':>14} | {'予測密度':>14} | {'誤差%':>10}")
        print("  " + "-" * 50)
        for i, k in enumerate(k_values):
            if k >= 3:
                predicted = a * base ** k
                actual = densities[i]
                err_pct = abs(actual - predicted) / actual * 100 if actual > 0 else 0
                print(f"  {k:>3} | {actual:>14.8f} | {predicted:>14.8f} | {err_pct:>9.2f}%")

        # 外挿: k=20, 30, 50 での予測
        print(f"\n  外挿予測:")
        for k_pred in [16, 20, 30, 50, 100]:
            pred_density = a * base ** k_pred
            pred_det_ratio = 1.0 - pred_density
            print(f"    k={k_pred:3d}: 非排除密度 = {pred_density:.2e}, "
                  f"決定的割合 = {pred_det_ratio:.10f} ({pred_det_ratio*100:.6f}%)")
    else:
        print("  フィッティング失敗")

    # ============================================================
    # 非排除残基の mod 4 分布
    # ============================================================
    print("\n" + "=" * 80)
    print("非排除残基の mod 4 分布の推移")
    print("=" * 80)

    print(f"\n  {'k':>3} | {'mod4=1':>10} | {'mod4=3':>10} | {'mod4=3の割合':>12}")
    print("  " + "-" * 50)

    for k_str in sorted(results["non_det_mod4_analysis"].keys(), key=int):
        dist = results["non_det_mod4_analysis"][k_str]
        c1 = dist.get(1, 0)
        c3 = dist.get(3, 0)
        total = c1 + c3
        r3 = c3 / total if total > 0 else 0
        print(f"  {int(k_str):>3} | {c1:>10} | {c3:>10} | {r3:>11.4f}")

        results["non_det_mod4_analysis"][k_str]["ratio_mod4_3"] = round(r3, 6)

    # ============================================================
    # 非排除残基の v2(3r+1) 分布
    # ============================================================
    print("\n" + "=" * 80)
    print("非排除残基の v2(3r+1) 分布")
    print("=" * 80)

    for k_val in [8, 10, 12, 14]:
        k_str = str(k_val)
        if k_str in results["non_det_v2_analysis"]:
            dist = results["non_det_v2_analysis"][k_str]
            total = sum(dist.values())
            print(f"\n  k={k_val} (非排除 {total} 個):")
            for v2 in sorted(dist.keys(), key=int):
                cnt = dist[v2]
                pct = cnt / total * 100 if total > 0 else 0
                print(f"    v2={v2}: {cnt:6d} ({pct:6.2f}%)")

    # ============================================================
    # 非排除密度の連続比 (d(k+1)/d(k)) の解析
    # ============================================================
    print("\n" + "=" * 80)
    print("非排除密度の連続比 d(k+1)/d(k)")
    print("=" * 80)

    print(f"\n  {'k':>3} -> {'k+1':>3} | {'d(k)':>14} | {'d(k+1)':>14} | {'比率':>10}")
    print("  " + "-" * 60)

    ratios_list = []
    for i in range(len(k_values) - 1):
        if densities[i] > 0 and densities[i+1] > 0:
            ratio = densities[i+1] / densities[i]
            ratios_list.append(ratio)
            print(f"  {k_values[i]:>3} -> {k_values[i+1]:>3} | "
                  f"{densities[i]:>14.8f} | {densities[i+1]:>14.8f} | {ratio:>10.6f}")

    if ratios_list:
        avg_ratio = sum(ratios_list) / len(ratios_list)
        # k >= 6 以降の安定比率
        stable_ratios = ratios_list[3:]  # k=6以降
        if stable_ratios:
            stable_avg = sum(stable_ratios) / len(stable_ratios)
            print(f"\n  全体平均比率: {avg_ratio:.6f}")
            print(f"  k>=6以降の平均比率: {stable_avg:.6f}")
            print(f"  0.883 との差: {abs(stable_avg - 0.883):.6f}")

    # ============================================================
    # 新発見の整理: 非排除パターンの末尾ビット構造
    # ============================================================
    print("\n" + "=" * 80)
    print("非排除残基の末尾ビット構造解析")
    print("=" * 80)

    # k=12 の非排除残基の末尾ビットパターン
    if 12 <= max(k_values):
        res12 = analyze_mod2k_descent(12, num_samples=40)
        trailing_ones = Counter()
        mod8_dist = Counter()
        mod16_dist = Counter()
        mod32_dist = Counter()

        for nd in res12["non_det_samples"]:
            r = nd["r"]
            # 末尾連続1ビット数
            t = 0
            temp = r
            while temp & 1:
                t += 1
                temp >>= 1
            trailing_ones[t] += 1
            mod8_dist[r % 8] += 1
            mod16_dist[r % 16] += 1
            mod32_dist[r % 32] += 1

        print(f"\n  k=12 の非排除残基 (サンプル {len(res12['non_det_samples'])} 個):")
        print(f"\n  末尾連続1ビット数の分布:")
        for t in sorted(trailing_ones.keys()):
            print(f"    trailing_ones={t}: {trailing_ones[t]} 個")

        print(f"\n  mod 8 分布: {dict(mod8_dist)}")
        print(f"  mod 16 分布: {dict(mod16_dist)}")
        print(f"  mod 32 分布: {dict(mod32_dist)}")

    # ============================================================
    # kステップ「以内」の保証率の漸近挙動
    # ============================================================
    print("\n" + "=" * 80)
    print("kステップ以内の下降保証率の漸近挙動")
    print("=" * 80)

    print(f"\n  {'k':>3} | {'k以内率':>12} | {'1-k以内率':>14} | {'log(1-率)':>12}")
    print("  " + "-" * 55)

    for row in results["convergence_table"]:
        k = row["k"]
        within_ratio = row["det_within_k_ratio"]
        complement = 1.0 - within_ratio
        log_complement = math.log(complement) if complement > 0 else float('-inf')
        print(f"  {k:>3} | {within_ratio:>12.8f} | {complement:>14.10f} | {log_complement:>12.6f}")

    # ============================================================
    # 結論と発見の整理
    # ============================================================
    print("\n" + "=" * 80)
    print("結論")
    print("=" * 80)

    findings = []
    hypotheses = []
    dead_ends = []

    # 87.5% 収束の検証
    stable_det_ratios = [r for k, r in zip(k_values, det_ratios) if k >= 6]
    if stable_det_ratios:
        min_det = min(stable_det_ratios)
        max_det = max(stable_det_ratios)
        if min_det > 0.85:
            findings.append(f"k=6..14 での決定的割合は {min_det:.4f}~{max_det:.4f} で安定 (87.5% 付近)")
        if max_det > 0.875:
            findings.append(f"k増加で決定的割合は 87.5% を超えて増加傾向")

    # 指数減衰の検証
    if a is not None and base is not None:
        findings.append(f"非排除密度の指数減衰率 = {base:.6f} (既知値 0.883 との差: {abs(base - 0.883):.6f})")
        if abs(base - 0.883) < 0.02:
            findings.append("指数減衰率 0.883 を数値的に確認")
        elif base < 1.0:
            findings.append(f"指数減衰は確認されたが、率は {base:.6f} (0.883 とは差がある)")

    # mod 4 分布
    latest_k = str(max(int(k) for k in results["non_det_mod4_analysis"].keys()))
    if latest_k in results["non_det_mod4_analysis"]:
        dist = results["non_det_mod4_analysis"][latest_k]
        if "ratio_mod4_3" in dist:
            r3 = dist["ratio_mod4_3"]
            if r3 > 0.55:
                findings.append(f"非排除残基の mod 4 ≡ 3 集中を確認 (k={latest_k} で {r3:.1%})")

    # 仮説
    if a is not None and base is not None and base < 1.0:
        hypotheses.append(f"k->infinity で非排除密度 -> 0 (決定的割合 -> 100%)")
        hypotheses.append(f"非排除密度 ~ {a:.4f} * {base:.4f}^k の指数減衰")
        hypotheses.append("全ての十分大きな奇数は有限ステップで下降 (コラッツ予想と同値)")

    results["findings"] = findings
    results["hypotheses"] = hypotheses
    results["dead_ends"] = dead_ends

    for f in findings:
        print(f"  [発見] {f}")
    for h in hypotheses:
        print(f"  [仮説] {h}")

    # JSON出力
    output_path = "/Users/soyukke/study/lean-unsolved/results/mod2k_unique_descent_path.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n結果を {output_path} に保存しました。")
    return results


if __name__ == "__main__":
    main()
