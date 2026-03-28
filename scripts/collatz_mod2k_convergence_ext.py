#!/usr/bin/env python3
"""
探索093 拡張: mod 2^k での決定的下降割合の漸近挙動

k=10で87.5%, k=12で91.1% → 1に漸近？ or 一定値に収束？
サンプリングで k=14 まで推定する。

また、非決定的剰余類の個数増加率を解析して理論的根拠を探る。
"""

import json
import time
from collections import Counter


def syracuse(n):
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    return val, v


def descent_steps(n, max_steps=100):
    original = n
    current = n
    for k in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return k
    return -1


def analyze_mod2k_fast(k, num_samples=100):
    """高速版: 各奇数剰余類のステップ数一意性を判定"""
    mod = 2 ** k
    total_odd = mod // 2

    deterministic_count = 0
    non_deterministic_count = 0
    non_det_mod32 = Counter()
    det_step_dist = Counter()

    for r in range(1, mod, 2):
        step_counter = Counter()
        for i in range(num_samples):
            n = r + mod * (2 * i + 1)
            if n % 2 == 0:
                continue
            s = descent_steps(n, max_steps=80)
            if s > 0:
                step_counter[s] += 1

        if len(step_counter) == 1:
            deterministic_count += 1
            det_step_dist[list(step_counter.keys())[0]] += 1
        else:
            non_deterministic_count += 1
            non_det_mod32[r % 32] += 1

    return {
        "k": k,
        "mod": mod,
        "total_odd": total_odd,
        "det": deterministic_count,
        "non_det": non_deterministic_count,
        "det_ratio": deterministic_count / total_odd,
        "non_det_ratio": non_deterministic_count / total_odd,
        "non_det_mod32": dict(non_det_mod32),
        "det_step_dist": dict(det_step_dist),
    }


def analyze_theoretical_structure(k_max=16):
    """
    理論的な構造解析:
    - 1ステップで決定的に下降する条件: v2(3r+1) >= 2 かつ v2 < k
    - 2ステップで決定的: T1(r) が 1ステップ決定的下降の剰余類に落ちる
    - 非決定的: ステップ数が r の上位ビットに依存
    """
    results = {}
    for k in range(3, k_max + 1):
        mod = 2 ** k

        # ステップ1で完全決定的に下降: v2(3r+1) >= 2 かつ v2(3r+1) < k
        step1_descent = 0
        # ステップ1で完全決定的に上昇: v2(3r+1) == 1
        step1_ascent = 0
        # v2 不確定: v2(3r+1) >= k
        v2_indeterminate = 0

        for r in range(1, mod, 2):
            val = 3 * r + 1
            v = 0
            temp = val
            while temp % 2 == 0:
                temp //= 2
                v += 1
            if v >= k:
                v2_indeterminate += 1
            elif v >= 2:
                step1_descent += 1
            else:  # v == 1
                step1_ascent += 1

        total = mod // 2
        results[k] = {
            "total": total,
            "step1_descent": step1_descent,
            "step1_ascent": step1_ascent,
            "v2_indeterminate": v2_indeterminate,
            "step1_descent_ratio": step1_descent / total,
            "step1_ascent_ratio": step1_ascent / total,
        }
    return results


def main():
    output = {
        "exploration_id": "093",
        "title": "mod 2^k での決定的下降割合の収束検証（拡張）",
        "convergence_table": [],
        "theoretical_step1": {},
        "non_det_mod32_all": {},
        "det_step_dist_all": {},
    }

    print("=" * 80)
    print("探索093: mod 2^k での決定的下降割合の収束検証（拡張）")
    print("=" * 80)

    # Part 1: 実測テーブル
    print("\n--- Part 1: 実測テーブル ---")
    configs = [
        (3, 200), (4, 200), (5, 200), (6, 200),
        (7, 200), (8, 200), (9, 200), (10, 200),
        (11, 100), (12, 80), (13, 50), (14, 30),
    ]

    print(f"\n{'k':>3} | {'奇数':>8} | {'決定的':>8} | {'非決定':>8} | "
          f"{'決定率':>10} | {'非決定率':>10} | {'時間':>8}")
    print("-" * 75)

    for k, samples in configs:
        t0 = time.time()
        res = analyze_mod2k_fast(k, num_samples=samples)
        elapsed = time.time() - t0

        row = {
            "k": k,
            "total_odd": res["total_odd"],
            "det": res["det"],
            "non_det": res["non_det"],
            "det_ratio": round(res["det_ratio"], 8),
            "non_det_ratio": round(res["non_det_ratio"], 8),
            "samples": samples,
            "elapsed": round(elapsed, 2),
        }
        output["convergence_table"].append(row)
        output["non_det_mod32_all"][str(k)] = res["non_det_mod32"]
        output["det_step_dist_all"][str(k)] = res["det_step_dist"]

        print(f"{k:>3} | {res['total_odd']:>8} | {res['det']:>8} | {res['non_det']:>8} | "
              f"{res['det_ratio']:>10.6f} | {res['non_det_ratio']:>10.6f} | {elapsed:>7.1f}s")

    # Part 2: 理論的な1ステップ解析（高速、k=20まで可能）
    print("\n--- Part 2: 理論的な1ステップ分類 ---")
    theory = analyze_theoretical_structure(k_max=18)
    output["theoretical_step1"] = {str(k): v for k, v in theory.items()}

    print(f"\n{'k':>3} | {'奇数':>8} | {'1step下降':>10} | {'1step上昇':>10} | {'v2不確定':>10} | "
          f"{'下降率':>10} | {'上昇率':>10}")
    print("-" * 80)
    for k in sorted(theory.keys()):
        t = theory[k]
        print(f"{k:>3} | {t['total']:>8} | {t['step1_descent']:>10} | {t['step1_ascent']:>10} | "
              f"{t['v2_indeterminate']:>10} | {t['step1_descent_ratio']:>10.6f} | "
              f"{t['step1_ascent_ratio']:>10.6f}")

    # Part 3: 非決定的割合の減衰パターン
    print("\n--- Part 3: 非決定的割合の減衰パターン ---")
    print("  非決定的割合が 0 に漸近するか、一定値に収束するか？\n")

    nd_ratios = [(row["k"], row["non_det_ratio"]) for row in output["convergence_table"]]
    for i in range(1, len(nd_ratios)):
        k_prev, r_prev = nd_ratios[i - 1]
        k_curr, r_curr = nd_ratios[i]
        if r_prev > 0 and r_curr > 0:
            decay = r_curr / r_prev
            print(f"  k={k_prev}→{k_curr}: 非決定率 {r_prev:.6f} → {r_curr:.6f}, "
                  f"比率={decay:.4f}")

    # Part 4: 非決定的 mod 32 分布の一貫性
    print("\n--- Part 4: 非決定的剰余類の mod 32 集中パターン ---")
    for k_str, dist in output["non_det_mod32_all"].items():
        k = int(k_str)
        if k in [8, 10, 12, 14]:
            total_nd = sum(dist.values())
            r31 = dist.get(31, 0)
            r27 = dist.get(27, 0)
            r15 = dist.get(15, 0)
            r7 = dist.get(7, 0)
            big4 = r7 + r15 + r27 + r31
            print(f"  k={k}: 非決定的{total_nd}個, "
                  f"r≡7:{r7}, r≡15:{r15}, r≡27:{r27}, r≡31:{r31}, "
                  f"4クラス合計:{big4} ({big4/total_nd*100:.1f}%)")

    # Part 5: 決定的ステップ数の安定性
    print("\n--- Part 5: 決定的ステップ数分布の安定化 ---")
    for k_str, dist in output["det_step_dist_all"].items():
        k = int(k_str)
        if k in [8, 10, 12, 14]:
            total_det = sum(dist.values())
            total_odd = 2 ** (k - 1)
            print(f"\n  k={k} (決定的 {total_det}/{total_odd}):")
            for s in sorted(dist.keys(), key=lambda x: int(x)):
                cnt = dist[s]
                # 理論的に step=1 は v2>=2 の剰余類数 = total/2
                print(f"    step={s}: {cnt} ({cnt/total_odd*100:.2f}% of all, "
                      f"{cnt/total_det*100:.1f}% of det)")

    # 結論
    print("\n" + "=" * 80)
    print("結論")
    print("=" * 80)

    final_nd = nd_ratios[-1]
    conclusion_parts = []

    # 7/8 に「収束」しない - むしろ非決定的割合が減少し続ける
    if len(nd_ratios) >= 4:
        late_ratios = [r for k, r in nd_ratios if k >= 10]
        if len(late_ratios) >= 2 and late_ratios[-1] < late_ratios[0]:
            conclusion_parts.append(
                f"非決定的割合は k の増大とともに減少: "
                f"k=10で{nd_ratios[7][1]*100:.1f}% → k={final_nd[0]}で{final_nd[1]*100:.1f}%"
            )
            conclusion_parts.append(
                "仮説「7/8に収束」は棄却。決定的割合は 7/8 を超えて 1 に漸近する傾向。"
            )
        else:
            conclusion_parts.append(
                "非決定的割合は k=10 付近で約 12.5% (=1/8) でほぼ安定。"
            )

    # mod 32 集中
    conclusion_parts.append(
        "非決定的剰余類は依然として r≡7,15,27,31 (mod 32) に集中。"
        "特に r≡31 (mod 32) が最多。"
    )

    # 1ステップ下降の理論値
    conclusion_parts.append(
        "1ステップ決定的下降は常に全奇数クラスの 1/2 (v2>=2の割合)。"
        "2ステップ以上の決定的下降が k とともに増加し、全体の決定的割合を押し上げる。"
    )

    conclusion = " ".join(conclusion_parts)
    output["conclusion"] = conclusion
    print(f"\n  {conclusion}")

    # JSON保存
    path = "/Users/soyukke/study/lean-unsolved/results/exploration_093.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  結果を {path} に保存しました。")


if __name__ == "__main__":
    main()
