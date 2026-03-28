"""
探索087: v2値列の組合せ的制約と実現可能列の数え上げ

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} において、
v2(3n+1) の値は n mod 2^k で決定される。
長さLのv2値列 (v1, v2, ..., vL) が実現可能かどうかを
mod 2^K の算術で判定し、以下を調べる:

1. v2値列の遷移確率行列(1次マルコフ近似)
2. 長さLの実現可能v2列の数え上げ vs 理論的上界
3. 禁止パターン(実現不可能な短い部分列)の探索
4. v2=2トラップの遷移構造の精密化
"""

import json
import math
from collections import defaultdict, Counter
from itertools import product

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) for odd n"""
    val = 3 * n + 1
    return val >> v2(val)

def get_v2_of_3n1(n):
    """v2(3n+1) for odd n"""
    return v2(3 * n + 1)

# ============================================================
# Part 1: v2(3n+1) の n mod 2^k による決定構造
# ============================================================
def analyze_v2_mod_structure(max_k=10):
    """n mod 2^k でv2(3n+1)がどこまで決定されるか"""
    results = {}
    for k in range(1, max_k + 1):
        mod = 2**k
        # 奇数の剰余類のみ
        v2_by_class = {}
        for r in range(1, mod, 2):
            v2_by_class[r] = get_v2_of_3n1(r)

        # v2値の分布
        v2_dist = Counter(v2_by_class.values())
        total = len(v2_by_class)

        results[k] = {
            "mod": mod,
            "num_odd_classes": total,
            "v2_distribution": {str(v): c for v, c in sorted(v2_dist.items())},
            "v2_proportions": {str(v): round(c/total, 6) for v, c in sorted(v2_dist.items())}
        }
    return results

# ============================================================
# Part 2: v2値列の遷移確率行列
# ============================================================
def compute_v2_transition_matrix(N_samples=10_000_000, max_v2=8):
    """大量の軌道からv2値の1次遷移行列を推定"""
    transitions = [[0] * (max_v2 + 1) for _ in range(max_v2 + 1)]

    for start in range(1, N_samples * 2, 2):
        if start > N_samples * 2:
            break
        n = start
        prev_v = get_v2_of_3n1(n)
        if prev_v > max_v2:
            prev_v = max_v2

        for _ in range(20):
            n = syracuse(n)
            if n == 1:
                break
            curr_v = get_v2_of_3n1(n)
            if curr_v > max_v2:
                curr_v = max_v2
            transitions[prev_v][curr_v] += 1
            prev_v = curr_v

    # 正規化
    prob_matrix = [[0.0] * (max_v2 + 1) for _ in range(max_v2 + 1)]
    for i in range(max_v2 + 1):
        row_sum = sum(transitions[i])
        if row_sum > 0:
            for j in range(max_v2 + 1):
                prob_matrix[i][j] = transitions[i][j] / row_sum

    return transitions, prob_matrix

# ============================================================
# Part 3: mod 2^K での実現可能v2列の厳密な数え上げ
# ============================================================
def enumerate_realizable_v2_sequences(L, K=12):
    """
    長さLのv2値列を mod 2^K で厳密に数え上げる。
    各奇数 r (mod 2^K) について軌道を追跡し、
    得られるv2値列を記録する。
    """
    mod = 2**K
    sequence_counts = Counter()

    for r in range(1, mod, 2):
        n = r
        seq = []
        valid = True
        for step in range(L):
            vv = get_v2_of_3n1(n)
            seq.append(vv)
            n = syracuse(n)
            # mod 2^K の範囲で追跡
            # nが偶数になることはないはず(Syracuseは奇数→奇数)
            n = n % mod
            if n == 0:
                n = mod - 1  # wraparound
                valid = False
                break
        if valid and len(seq) == L:
            sequence_counts[tuple(seq)] += 1

    return sequence_counts

# ============================================================
# Part 4: 禁止パターンの探索
# ============================================================
def find_forbidden_v2_patterns(max_len=4, K=16):
    """
    長さmax_lenまでの全v2値パターンのうち、
    mod 2^K で実現不可能なものを探索
    """
    mod = 2**K
    max_v2_check = 6  # v2=1..6 を考慮

    # まず全ての実現可能パターンを収集
    realized = set()
    for r in range(1, mod, 2):
        n = r
        seq = []
        for step in range(max_len):
            vv = get_v2_of_3n1(n)
            if vv > max_v2_check:
                vv = max_v2_check  # cap
            seq.append(vv)
            n = syracuse(n)
            n = n % mod
            if n == 0:
                break

        # 全ての部分列長を登録
        for length in range(1, len(seq) + 1):
            for start in range(len(seq) - length + 1):
                realized.add(tuple(seq[start:start+length]))

    # 理論的に可能なパターンとの差分 = 禁止パターン
    forbidden_by_length = {}
    for length in range(2, max_len + 1):
        all_patterns = set(product(range(1, max_v2_check + 1), repeat=length))
        forbidden = all_patterns - realized
        forbidden_by_length[length] = sorted(forbidden)

    return forbidden_by_length, realized

# ============================================================
# Part 5: v2=2 トラップの遷移詳細
# ============================================================
def analyze_v2_2_trap(N=1_000_000):
    """v2=2からの遷移を詳細に分析"""
    # v2=2 の条件: n ≡ 1 (mod 4) → 3n+1 ≡ 4 (mod 8) → v2=2
    trap_stats = {
        "v2_2_to_v2": Counter(),
        "consecutive_v2_2": Counter(),
        "escape_after_k": Counter(),
    }

    for start in range(1, N * 2, 2):
        if start > N * 2:
            break
        n = start
        consec = 0
        for _ in range(100):
            if n == 1:
                break
            vv = get_v2_of_3n1(n)
            n_next = syracuse(n)

            if vv == 2:
                vv_next = get_v2_of_3n1(n_next) if n_next > 1 else 0
                trap_stats["v2_2_to_v2"][vv_next] += 1
                consec += 1
            else:
                if consec > 0:
                    trap_stats["consecutive_v2_2"][consec] += 1
                    trap_stats["escape_after_k"][consec] += 1
                consec = 0
            n = n_next

    return trap_stats

# ============================================================
# Part 6: 高次マルコフ性の検定
# ============================================================
def test_markov_order(N_samples=2_000_000, max_order=3, max_v2=4):
    """v2列がk次マルコフかどうかを条件付き分布の比較で検定"""
    # order次の遷移を記録
    results = {}

    for order in range(1, max_order + 1):
        # (history of length order) -> next v2 の分布
        cond_dist = defaultdict(lambda: Counter())

        for start in range(1, N_samples * 2, 2):
            if start > N_samples * 2:
                break
            n = start
            history = []

            for _ in range(30):
                if n == 1:
                    break
                vv = min(get_v2_of_3n1(n), max_v2)

                if len(history) >= order:
                    key = tuple(history[-order:])
                    cond_dist[key][vv] += 1

                history.append(vv)
                n = syracuse(n)

        # 条件付きエントロピーを計算
        total_entropy = 0.0
        total_count = 0
        for key, dist in cond_dist.items():
            total = sum(dist.values())
            if total < 10:
                continue
            entropy = 0.0
            for v, c in dist.items():
                p = c / total
                if p > 0:
                    entropy -= p * math.log2(p)
            total_entropy += entropy * total
            total_count += total

        avg_entropy = total_entropy / total_count if total_count > 0 else 0
        results[order] = {
            "avg_conditional_entropy": round(avg_entropy, 6),
            "num_contexts": len(cond_dist),
            "total_transitions": total_count
        }

    return results

# ============================================================
# メイン実行
# ============================================================
def main():
    print("=== 探索087: v2値列の組合せ的制約 ===")

    # Part 1: mod構造
    print("\n[Part 1] v2(3n+1) の mod 2^k 決定構造...")
    mod_structure = analyze_v2_mod_structure(max_k=10)

    # Part 2: 遷移行列 (サンプル数を抑える)
    print("\n[Part 2] v2遷移確率行列...")
    transitions, prob_matrix = compute_v2_transition_matrix(N_samples=500_000, max_v2=6)

    # Part 3: 実現可能列の数え上げ
    print("\n[Part 3] 実現可能v2列の数え上げ...")
    realizable_counts = {}
    for L in range(1, 6):
        print(f"  L={L}...")
        seq_counts = enumerate_realizable_v2_sequences(L, K=14)
        num_distinct = len(seq_counts)
        # v2=1..6の理論的組合せ数
        theoretical_max = 6**L
        realizable_counts[L] = {
            "num_distinct_sequences": num_distinct,
            "theoretical_max_6values": theoretical_max,
            "realization_ratio": round(num_distinct / theoretical_max, 6) if theoretical_max > 0 else 0,
            "top_sequences": {str(k): v for k, v in seq_counts.most_common(10)}
        }

    # Part 4: 禁止パターン
    print("\n[Part 4] 禁止v2パターンの探索...")
    forbidden, realized = find_forbidden_v2_patterns(max_len=4, K=16)
    forbidden_summary = {}
    for length, patterns in forbidden.items():
        forbidden_summary[str(length)] = {
            "count": len(patterns),
            "examples": [str(p) for p in patterns[:20]],
            "realized_count": len([p for p in realized if len(p) == length])
        }

    # Part 5: v2=2 トラップ
    print("\n[Part 5] v2=2 トラップ分析...")
    trap_stats = analyze_v2_2_trap(N=500_000)
    trap_summary = {
        "v2_2_to_next": {str(k): v for k, v in trap_stats["v2_2_to_v2"].most_common()},
        "consecutive_v2_2_distribution": {str(k): v for k, v in sorted(trap_stats["consecutive_v2_2"].items())[:15]},
    }
    # P(v2=2 → v2=2) を計算
    total_from_2 = sum(trap_stats["v2_2_to_v2"].values())
    stay_at_2 = trap_stats["v2_2_to_v2"].get(2, 0)
    if total_from_2 > 0:
        trap_summary["P_stay_at_v2_2"] = round(stay_at_2 / total_from_2, 6)

    # Part 6: 高次マルコフ検定
    print("\n[Part 6] v2列のマルコフ次数検定...")
    markov_results = test_markov_order(N_samples=500_000, max_order=3, max_v2=4)

    # 遷移行列をJSON化
    transition_dict = {}
    for i in range(1, 7):
        row = {}
        for j in range(1, 7):
            if prob_matrix[i][j] > 0.001:
                row[str(j)] = round(float(prob_matrix[i][j]), 6)
        if row:
            transition_dict[str(i)] = row

    # 結果をまとめ
    result = {
        "exploration_id": "087",
        "title": "v2値列の組合せ的制約と実現可能列の数え上げ",
        "method": "mod 2^K算術によるv2列の厳密な数え上げ・遷移行列・禁止パターン探索",
        "findings": {
            "mod_structure": {
                "description": "v2(3n+1)はn mod 2^kで決定される",
                "data": {str(k): v for k, v in mod_structure.items()}
            },
            "transition_matrix": {
                "description": "v2値の1次遷移確率行列 P(v2_next=j | v2_curr=i)",
                "matrix": transition_dict
            },
            "realizable_sequences": {
                "description": "長さLの実現可能v2値列の数え上げ",
                "data": realizable_counts
            },
            "forbidden_patterns": {
                "description": "mod 2^16で実現不可能なv2値パターン",
                "data": forbidden_summary
            },
            "v2_2_trap": {
                "description": "v2=2トラップの遷移詳細",
                "data": trap_summary
            },
            "markov_order_test": {
                "description": "v2列のマルコフ次数検定(条件付きエントロピー)",
                "data": markov_results
            }
        },
        "key_insights": []
    }

    # Key insightsの生成
    insights = []

    # 遷移行列からの洞察
    if "2" in transition_dict:
        p22 = transition_dict["2"].get("2", 0)
        insights.append(f"v2=2→v2=2 遷移確率: {p22} (トラップ確率)")

    # 実現可能列の比率
    for L in range(1, 6):
        r = realizable_counts[L]["realization_ratio"]
        insights.append(f"L={L}: 実現比率={r} ({realizable_counts[L]['num_distinct_sequences']}/{realizable_counts[L]['theoretical_max_6values']})")

    # 禁止パターン数
    for length_str, data in forbidden_summary.items():
        insights.append(f"長さ{length_str}の禁止パターン: {data['count']}個 (実現: {data['realized_count']}個)")

    # マルコフ次数
    for order, data in markov_results.items():
        insights.append(f"{order}次マルコフの条件付きエントロピー: {data['avg_conditional_entropy']} bits")

    result["key_insights"] = insights

    # JSON出力
    output_path = "/Users/soyukke/study/lean-unsolved/results/exploration_087.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n結果を {output_path} に保存しました")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
