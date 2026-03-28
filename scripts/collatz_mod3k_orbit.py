"""
コラッツ予想: Syracuse関数 T(n) = (3n+1)/2^v2(3n+1) の mod 3^k 軌道構造解析

目的:
1. T(n) mod 3^k (k=1..6) の完全分類
2. T^m(n) mod 3^k (m=1..5) の分布解析（一様性検証）
3. 3-adic構造の解明
4. mod 3^k 遷移行列の解析
"""

import json
import math
from collections import Counter, defaultdict

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2(n):
    """2-adic付値"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def v3(n):
    """3-adic付値"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 3 == 0:
        n //= 3
        c += 1
    return c

def syracuse_iter(n, m):
    """T^m(n): Syracuse関数をm回適用"""
    val = n
    for _ in range(m):
        val = syracuse(val)
    return val

def entropy(counter, total):
    """Shannon entropy in bits"""
    h = 0
    for c in counter.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h

# ============================================================
# 解析1: T(n) mod 3^k の分布 (奇数n, 1<=n<=N)
# ============================================================
def analyze_distribution(N, k_max=6):
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k
        counter = Counter()
        total = 0
        for n in range(1, N + 1, 2):
            t = syracuse(n)
            counter[t % mod] += 1
            total += 1

        non_zero_classes = {r: c for r, c in counter.items() if r % 3 != 0}
        zero_classes = {r: c for r, c in counter.items() if r % 3 == 0}

        expected_classes = [r for r in range(mod) if r % 2 == 1 and r % 3 != 0]
        if expected_classes:
            expected_count = total / len(expected_classes)
            chi2 = sum((counter.get(r, 0) - expected_count) ** 2 / expected_count for r in expected_classes)
            observed_in_expected = sum(counter.get(r, 0) for r in expected_classes)
        else:
            chi2 = 0
            observed_in_expected = 0

        results[k] = {
            "mod": mod,
            "total_odd_n": total,
            "distinct_residues_hit": len(counter),
            "residues_with_3_divides": len(zero_classes),
            "count_landing_on_mult_of_3": sum(zero_classes.values()),
            "num_expected_odd_non3_classes": len(expected_classes),
            "fraction_in_expected_classes": round(observed_in_expected / total, 6) if total > 0 else 0,
            "chi_squared": round(chi2, 2),
            "top_residues": dict(counter.most_common(10))
        }
    return results

# ============================================================
# 解析2: T^m(n) mod 3^k の分布
# ============================================================
def analyze_iterated_distribution(N, m_max=5, k_max=4):
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k
        for m in range(1, m_max + 1):
            counter = Counter()
            total = 0
            for n in range(1, N + 1, 2):
                t = syracuse_iter(n, m)
                counter[t % mod] += 1
                total += 1

            h = entropy(counter, total)
            max_h = math.log2(len(counter)) if len(counter) > 1 else 0

            key = f"k={k}_m={m}"
            results[key] = {
                "mod": mod,
                "iterations": m,
                "total": total,
                "distinct_residues": len(counter),
                "entropy": round(h, 6),
                "max_entropy": round(max_h, 6),
                "entropy_ratio": round(h / max_h, 6) if max_h > 0 else 0,
                "top5": dict(counter.most_common(5))
            }
    return results

# ============================================================
# 解析3: mod 3^k 遷移行列（簡易版）
# ============================================================
def analyze_transition_matrix(k_max=4):
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k
        odd_residues = [r for r in range(mod) if r % 2 == 1]

        transitions = defaultdict(Counter)
        sample_size = max(10000, mod * 100)
        for n in range(1, sample_size * 2 + 1, 2):
            r_from = n % mod
            t = syracuse(n)
            r_to = t % mod
            transitions[r_from][r_to] += 1

        deterministic = 0
        total_classes = len(odd_residues)
        branching_factors = []
        for r in odd_residues:
            num_targets = len(transitions[r])
            branching_factors.append(num_targets)
            if num_targets == 1:
                deterministic += 1

        avg_branching = sum(branching_factors) / len(branching_factors) if branching_factors else 0

        # 定常分布の近似: 各残基への遷移頻度
        incoming = Counter()
        total_transitions = 0
        for r_from in odd_residues:
            for r_to, count in transitions[r_from].items():
                incoming[r_to] += count
                total_transitions += count

        # L1 distance from uniform over odd residues
        if total_transitions > 0:
            uniform_prob = 1.0 / len(odd_residues)
            l1 = sum(abs(incoming.get(r, 0) / total_transitions - uniform_prob) for r in odd_residues)
        else:
            l1 = -1

        results[k] = {
            "mod": mod,
            "num_odd_residues": total_classes,
            "deterministic_transitions": deterministic,
            "deterministic_ratio": round(deterministic / total_classes, 4) if total_classes > 0 else 0,
            "avg_branching_factor": round(avg_branching, 4),
            "stationary_L1_from_uniform": round(l1, 6)
        }
    return results

# ============================================================
# 解析4: 3-adic収束パターン
# ============================================================
def analyze_3adic_convergence(N=30000):
    results = {}
    for k in range(1, 5):
        mod = 3 ** k
        by_m = defaultdict(list)

        for r in range(1, mod, 2):
            if r % 3 == 0:
                continue
            reps = [n for n in range(r, min(N, r + mod * 20), mod) if n > 0 and n % 2 == 1][:8]
            if len(reps) < 2:
                continue
            for i in range(len(reps)):
                for j in range(i + 1, min(i + 3, len(reps))):
                    n1, n2 = reps[i], reps[j]
                    for m in range(1, 6):
                        t1 = syracuse_iter(n1, m)
                        t2 = syracuse_iter(n2, m)
                        diff = abs(t1 - t2)
                        if diff > 0:
                            by_m[m].append(v3(diff))

        results[f"k={k}"] = {
            "mod": mod,
            "avg_v3_by_iteration": {
                m: round(sum(vals) / len(vals), 4) if vals else None
                for m, vals in sorted(by_m.items())
            },
            "num_pairs": sum(len(v) for v in by_m.values())
        }
    return results

# ============================================================
# 解析5: mod 3^k での禁止パターン
# ============================================================
def analyze_forbidden_patterns(N=100000, k_max=5):
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k
        reachable = set()
        for n in range(1, N + 1, 2):
            t = syracuse(n)
            reachable.add(t % mod)

        all_odd = set(r for r in range(mod) if r % 2 == 1)
        all_odd_non3 = set(r for r in all_odd if r % 3 != 0)
        unreachable_odd = all_odd - reachable
        unreachable_odd_non3 = all_odd_non3 - reachable
        reachable_mult3 = set(r for r in reachable if r % 3 == 0)

        results[k] = {
            "mod": mod,
            "total_odd_residues": len(all_odd),
            "total_odd_non3_residues": len(all_odd_non3),
            "reachable_odd_residues": len(reachable & all_odd),
            "unreachable_odd_residues": sorted(list(unreachable_odd))[:20],
            "unreachable_odd_non3_residues": sorted(list(unreachable_odd_non3))[:20],
            "num_unreachable_odd": len(unreachable_odd),
            "num_unreachable_odd_non3": len(unreachable_odd_non3),
            "reachable_mult3_residues": sorted(list(reachable_mult3))[:20],
            "forbidden_ratio_odd": round(len(unreachable_odd) / len(all_odd), 6) if all_odd else 0,
            "forbidden_ratio_odd_non3": round(len(unreachable_odd_non3) / len(all_odd_non3), 6) if all_odd_non3 else 0
        }
    return results

# ============================================================
# 解析6: T(n) mod 9 の完全分類（理論的）
# ============================================================
def analyze_mod9_theory():
    results = {}
    mod = 18  # 奇数 mod 18

    classifications = []
    for r in range(1, mod, 2):
        samples = []
        for k_val in range(200):
            n = r + 18 * k_val
            if n > 0:
                t = syracuse(n)
                samples.append(t % 9)

        unique_outputs = sorted(set(samples))
        v2_val = v2(3 * r + 1)

        classifications.append({
            "n_mod_18": r,
            "n_mod_3": r % 3,
            "n_mod_9": r % 9,
            "v2_of_3r_plus_1": v2_val,
            "T_mod_9_values": unique_outputs,
            "is_deterministic": len(unique_outputs) == 1,
            "deterministic_value": unique_outputs[0] if len(unique_outputs) == 1 else None
        })

    det_count = sum(1 for c in classifications if c["is_deterministic"])

    results["mod_18_classification"] = classifications
    results["deterministic_count"] = det_count
    results["total_classes"] = len(classifications)
    results["deterministic_ratio"] = round(det_count / len(classifications), 4)

    return results

# ============================================================
# 解析7: mod 3^k 拡張分類 (mod 2*3^k で確定的遷移を探す)
# ============================================================
def analyze_extended_classification(k_max=4):
    """mod 2^a * 3^k で確定的遷移が増えるかを調べる"""
    results = {}
    for k in range(1, k_max + 1):
        mod3k = 3 ** k
        for a in range(1, 8):
            mod = (2 ** a) * mod3k
            det_count = 0
            total_count = 0
            for r in range(1, mod, 2):
                samples = set()
                for mult in range(100):
                    n = r + mod * mult
                    if n > 0:
                        t = syracuse(n)
                        samples.add(t % mod3k)
                total_count += 1
                if len(samples) == 1:
                    det_count += 1

            results[f"k={k}_a={a}"] = {
                "mod_input": mod,
                "mod_output": mod3k,
                "total_classes": total_count,
                "deterministic": det_count,
                "det_ratio": round(det_count / total_count, 4) if total_count > 0 else 0
            }
    return results

# ============================================================
# 解析8: 連続反復のmod 3^k構造
# ============================================================
def analyze_consecutive_orbits(k_max=3):
    """T, T^2, T^3 の mod 3^k 値の組 (tuple) の分布"""
    results = {}
    N = 50000
    for k in range(1, k_max + 1):
        mod = 3 ** k
        triple_counter = Counter()
        total = 0
        for n in range(1, N + 1, 2):
            t1 = syracuse(n)
            t2 = syracuse(t1)
            t3 = syracuse(t2)
            triple = (t1 % mod, t2 % mod, t3 % mod)
            triple_counter[triple] += 1
            total += 1

        h = entropy(triple_counter, total)
        max_possible = len(triple_counter)
        max_h = math.log2(max_possible) if max_possible > 1 else 0

        # 禁止三つ組
        all_odd_non3 = [r for r in range(mod) if r % 2 == 1 and r % 3 != 0]
        theoretical_max = len(all_odd_non3) ** 3

        results[k] = {
            "mod": mod,
            "total_triples_observed": total,
            "distinct_triples": len(triple_counter),
            "theoretical_max_triples": theoretical_max,
            "coverage_ratio": round(len(triple_counter) / theoretical_max, 6) if theoretical_max > 0 else 0,
            "entropy": round(h, 4),
            "max_entropy": round(max_h, 4),
            "entropy_ratio": round(h / max_h, 6) if max_h > 0 else 0,
            "top5_triples": {str(k_): v for k_, v in triple_counter.most_common(5)}
        }
    return results

# ============================================================
# メイン実行
# ============================================================
if __name__ == "__main__":
    N = 100000

    print("解析1: T(n) mod 3^k の分布...")
    dist_results = analyze_distribution(N, k_max=6)

    print("解析2: T^m(n) mod 3^k の反復分布...")
    iter_results = analyze_iterated_distribution(min(N, 50000), m_max=5, k_max=4)

    print("解析3: mod 3^k 遷移行列...")
    trans_results = analyze_transition_matrix(k_max=4)

    print("解析4: 3-adic収束パターン...")
    adic_results = analyze_3adic_convergence(N=20000)

    print("解析5: mod 3^k 禁止パターン...")
    forbidden_results = analyze_forbidden_patterns(N, k_max=5)

    print("解析6: T(n) mod 9 完全分類...")
    mod9_results = analyze_mod9_theory()

    print("解析7: 拡張分類 mod 2^a*3^k...")
    extended_results = analyze_extended_classification(k_max=3)

    print("解析8: 連続軌道の三つ組分布...")
    consec_results = analyze_consecutive_orbits(k_max=3)

    # 主要発見の抽出
    findings = []

    # T(n)≢0(mod3)確認
    k1 = dist_results[1]
    if k1["count_landing_on_mult_of_3"] == 0:
        findings.append("CONFIRMED: T(n) ≢ 0 (mod 3) for all tested odd n")

    # 確定的遷移の退化
    for k in range(1, 5):
        tr = trans_results[k]
        findings.append(f"mod 3^{k}: det_ratio={tr['deterministic_ratio']}, avg_branching={tr['avg_branching_factor']}, L1={tr['stationary_L1_from_uniform']}")

    # 禁止パターン
    for k in range(1, 6):
        fb = forbidden_results[k]
        findings.append(f"mod 3^{k}: {fb['num_unreachable_odd']} unreachable odd, {fb['num_unreachable_odd_non3']} unreachable odd-non3, forbidden_ratio={fb['forbidden_ratio_odd']}")

    # mod 9 分類
    m9 = mod9_results
    findings.append(f"mod 9 classification: {m9['deterministic_count']}/{m9['total_classes']} deterministic (ratio={m9['deterministic_ratio']})")

    # 拡張分類
    for key, val in extended_results.items():
        if val["det_ratio"] > 0.5:
            findings.append(f"Extended {key}: det_ratio={val['det_ratio']} ({val['deterministic']}/{val['total_classes']})")

    # 三つ組のカバレッジ
    for k in range(1, 4):
        c = consec_results[k]
        findings.append(f"mod 3^{k} triples: coverage={c['coverage_ratio']}, entropy_ratio={c['entropy_ratio']}")

    # 統合結果
    final_results = {
        "exploration_id": "mod3k_orbit_structure",
        "category": "algebraic_structure",
        "description": "Syracuse関数T(n)のmod 3^k軌道構造と3-adic解析",
        "parameters": {"sample_size": N, "k_max": 6},
        "analysis_1_distribution": dist_results,
        "analysis_2_iterated_distribution": iter_results,
        "analysis_3_transition_matrix": trans_results,
        "analysis_4_3adic_convergence": adic_results,
        "analysis_5_forbidden_patterns": forbidden_results,
        "analysis_6_mod9_classification": mod9_results,
        "analysis_7_extended_classification": extended_results,
        "analysis_8_consecutive_orbits": consec_results,
        "key_findings": findings
    }

    import os
    output_path = "/Users/soyukke/study/lean-unsolved/results/mod3k_orbit_structure.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f"\n結果を {output_path} に保存しました")
    print(f"\n主要発見 ({len(findings)}件):")
    for i, finding in enumerate(findings, 1):
        print(f"  {i}. {finding}")

    # JSON出力
    print("\n" + json.dumps(final_results, indent=2, ensure_ascii=False))
