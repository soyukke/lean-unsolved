#!/usr/bin/env python3
"""
探索093: mod 2^k での決定的下降割合の収束検証

目的:
- mod 2^10 で 87.5% (448/512) だった決定的下降割合が
  mod 2^12, 2^14 でも 7/8 = 87.5% に収束するか検証
- 非決定的剰余類の構造（r ≡ 31 (mod 32) への集中）の持続を確認
- 収束の理論的根拠を探る

定義:
- 「決定的」= 下降ステップ数（Syracuseを何回適用すれば初期値を下回るか）が
  mod 2^k の剰余類で一意に決まる
- 「非決定的」= 同じ剰余類内でステップ数がバラつく
"""

import json
import time
from collections import Counter, defaultdict


def syracuse(n):
    """Syracuse関数: 奇数 n → (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    return val, v


def descent_steps(n, max_steps=100):
    """奇数 n から Syracuse 反復で初めて n を下回るまでのステップ数"""
    original = n
    current = n
    for k in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return k
    return -1


def analyze_mod2k(k, num_samples=200):
    """
    mod 2^k の各奇数剰余類について、下降ステップ数が決定的かを判定。
    各クラスから num_samples 個のサンプルで検証。
    """
    mod = 2 ** k
    total_odd = mod // 2

    deterministic_count = 0
    non_deterministic_list = []
    det_step_dist = Counter()

    for r in range(1, mod, 2):
        step_counter = Counter()
        for i in range(num_samples):
            n = r + mod * (2 * i + 1)
            if n % 2 == 0:
                continue
            s = descent_steps(n, max_steps=100)
            if s > 0:
                step_counter[s] += 1

        if len(step_counter) == 1:
            deterministic_count += 1
            step_val = list(step_counter.keys())[0]
            det_step_dist[step_val] += 1
        else:
            total = sum(step_counter.values())
            dominant = step_counter.most_common(1)[0]
            non_deterministic_list.append({
                "r": r,
                "r_mod32": r % 32,
                "distribution": dict(step_counter),
                "dominant_ratio": round(dominant[1] / total, 4),
            })

    non_det_count = len(non_deterministic_list)

    return {
        "k": k,
        "mod": mod,
        "total_odd": total_odd,
        "deterministic": deterministic_count,
        "non_deterministic": non_det_count,
        "det_ratio": round(deterministic_count / total_odd, 8),
        "det_step_distribution": dict(det_step_dist),
        "non_det_mod32": dict(Counter(nd["r_mod32"] for nd in non_deterministic_list)),
        "non_det_details": non_deterministic_list[:20],  # 最初の20個のみ保存
    }


def main():
    results = {
        "exploration_id": "093",
        "title": "mod 2^k での決定的下降割合の収束検証",
        "hypothesis": "決定的割合は 7/8 = 87.5% に収束する",
        "definition": "決定的 = 下降ステップ数が剰余類で一意に決まる",
        "convergence_table": [],
        "non_det_mod32_by_k": {},
        "det_step_dist_by_k": {},
        "conclusion": "",
    }

    print("=" * 80)
    print("探索093: mod 2^k での決定的下降割合の収束検証")
    print("=" * 80)
    print("定義: 「決定的」= 下降ステップ数が剰余類内で一意")
    print()

    # k=3..10 はサンプル200で高速に実行
    # k=12 はサンプル100で実行
    # k=14 はサンプル50で実行（計算コスト大）

    configs = [
        (3, 200), (4, 200), (5, 200), (6, 200),
        (7, 200), (8, 200), (9, 200), (10, 200),
        (11, 150), (12, 100),
    ]

    print(f"{'k':>3} | {'mod':>8} | {'奇数':>8} | {'決定的':>8} | {'非決定':>8} | "
          f"{'決定率':>10} | {'=7/8?':>6} | {'時間':>8}")
    print("-" * 80)

    for k, samples in configs:
        t0 = time.time()
        res = analyze_mod2k(k, num_samples=samples)
        elapsed = time.time() - t0

        is_7_8 = "YES" if abs(res["det_ratio"] - 0.875) < 0.002 else "NO"

        row = {
            "k": k,
            "mod": res["mod"],
            "total_odd": res["total_odd"],
            "deterministic": res["deterministic"],
            "non_deterministic": res["non_deterministic"],
            "det_ratio": res["det_ratio"],
            "samples_per_class": samples,
            "elapsed_sec": round(elapsed, 2),
        }
        results["convergence_table"].append(row)
        results["non_det_mod32_by_k"][str(k)] = res["non_det_mod32"]
        results["det_step_dist_by_k"][str(k)] = res["det_step_distribution"]

        print(f"{k:>3} | {res['mod']:>8} | {res['total_odd']:>8} | "
              f"{res['deterministic']:>8} | {res['non_deterministic']:>8} | "
              f"{res['det_ratio']:>10.6f} | {is_7_8:>6} | {elapsed:>7.1f}s")

    # 非決定的の mod 32 分布
    print("\n" + "=" * 80)
    print("非決定的剰余類の mod 32 分布")
    print("=" * 80)

    for k_str, dist in results["non_det_mod32_by_k"].items():
        k = int(k_str)
        if k in [6, 8, 10, 12]:
            print(f"\n  k={k}: {dist}")

    # 決定的ステップ数の分布
    print("\n" + "=" * 80)
    print("決定的剰余類のステップ数分布")
    print("=" * 80)

    for k_str, dist in results["det_step_dist_by_k"].items():
        k = int(k_str)
        if k in [6, 8, 10, 12]:
            total_det = sum(dist.values())
            print(f"\n  k={k} (決定的 {total_det} 個):")
            for s in sorted(dist.keys(), key=int):
                print(f"    step={s}: {dist[s]} 個 ({dist[s]/total_det*100:.1f}%)")

    # k=12 の非決定的剰余類の詳細
    print("\n" + "=" * 80)
    print("k=12 の非決定的剰余類の詳細（上位10個）")
    print("=" * 80)

    if 12 <= max(c[0] for c in configs):
        res12 = analyze_mod2k(12, num_samples=100)
        for nd in res12["non_det_details"][:10]:
            top3 = sorted(nd["distribution"].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  r={nd['r']:5d} (mod32={nd['r_mod32']:2d}): "
                  f"dominant={nd['dominant_ratio']:.2%}, top3={top3}")

    # 7/8 の理論的根拠の検証
    print("\n" + "=" * 80)
    print("7/8 収束の理論的検証")
    print("=" * 80)

    print("\n  非決定的個数の推移:")
    print(f"  {'k':>3} | {'奇数数':>8} | {'非決定的':>8} | {'非決定的/奇数数':>15} | {'= 1/8?':>8}")
    print("  " + "-" * 55)
    for row in results["convergence_table"]:
        k = row["k"]
        total = row["total_odd"]
        nd = row["non_deterministic"]
        ratio = nd / total
        expected = total / 8
        match = "YES" if abs(ratio - 0.125) < 0.005 else "NO"
        print(f"  {k:>3} | {total:>8} | {nd:>8} | {ratio:>15.6f} | {match:>8}")

    # 非決定的な r の末尾ビット構造の解析
    print("\n" + "=" * 80)
    print("非決定的剰余類の末尾ビットパターン解析")
    print("=" * 80)

    for k in [8, 10]:
        res_k = analyze_mod2k(k, num_samples=200)
        print(f"\n  k={k}:")
        trailing_ones_dist = Counter()
        for nd in res_k["non_det_details"]:
            r = nd["r"]
            # 末尾連続1ビット数
            t = 0
            temp = r
            while temp % 2 == 1:
                t += 1
                temp >>= 1
            trailing_ones_dist[t] += 1

        for t in sorted(trailing_ones_dist.keys()):
            print(f"    末尾連続1={t}: {trailing_ones_dist[t]} 個")

    # 結論
    det_ratios = [(row["k"], row["det_ratio"]) for row in results["convergence_table"]]
    converges = all(abs(r - 0.875) < 0.005 for k, r in det_ratios if k >= 5)

    if converges:
        conclusion = (
            "確認: k >= 5 のとき決定的割合は 7/8 = 87.5% に収束。"
            "非決定的剰余類は全奇数剰余類の 1/8 を占め、"
            "r ≡ 7,15,23,31 (mod 32) などの特定パターンに集中。"
            "mod 2^12 でも 87.5% が維持されることを確認。"
        )
    else:
        # 実際の値を報告
        k10 = next((r for k, r in det_ratios if k == 10), None)
        k12 = next((r for k, r in det_ratios if k == 12), None)
        conclusion = (
            f"mod 2^10 での決定的割合: {k10}, "
            f"mod 2^12 での決定的割合: {k12}。"
            "収束パターンの詳細を報告。"
        )

    results["conclusion"] = conclusion

    print("\n" + "=" * 80)
    print("結論")
    print("=" * 80)
    print(f"\n  {conclusion}")

    # JSON出力
    output_path = "/Users/soyukke/study/lean-unsolved/results/exploration_093.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n  結果を {output_path} に保存しました。")
    return results


if __name__ == "__main__":
    main()
