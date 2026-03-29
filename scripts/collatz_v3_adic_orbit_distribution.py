"""
コラッツ予想: 3-adic評価 v3(T^k(n)) の軌道分布と v3(T^k(n)-r) の解析

目的:
1. v3(T^k(n)) の分布確認 (T(n)≡/≡0 mod 3 なので常に0のはず)
2. v3(T^k(n) - 1) の分布: T(n)≡1 mod 3 となる頻度と3-adic深度
3. v3(T^k(n) - 2) の分布: T(n)≡2 mod 3 となる頻度と3-adic深度
4. v3(T^k(n) - r) が幾何分布 Geo(1/3) に従うか検証
5. 軌道上の連続パターン v3(T^k(n)-1), v3(T^{k+1}(n)-1), ... の相関
6. n mod 3 による条件付き分布の違い
"""

import json
import math
from collections import Counter, defaultdict
import time

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v3(n):
    """3-adic付値"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 3 == 0:
        n //= 3
        c += 1
    return c

def full_orbit(n, max_steps=1000):
    """nからの完全軌道 (1に到達するまで、最大max_steps)"""
    orbit = [n]
    cur = n
    for _ in range(max_steps):
        if cur == 1:
            break
        cur = syracuse(cur)
        orbit.append(cur)
    return orbit

def main():
    start_time = time.time()
    N_MAX = 200000  # 奇数nの範囲
    MAX_ORBIT_STEPS = 500

    print(f"=== 3-adic評価 v3(T^k(n)-r) の分布解析 ===")
    print(f"N_MAX = {N_MAX}, MAX_ORBIT_STEPS = {MAX_ORBIT_STEPS}")

    # =========================================================
    # Analysis 1: v3(T(n)) の確認 (常に0であることの検証)
    # =========================================================
    print("\n--- Analysis 1: v3(T(n)) の分布 ---")
    v3_T_counts = Counter()
    for n in range(1, N_MAX + 1, 2):  # 奇数のみ
        t = syracuse(n)
        v3_T_counts[v3(t)] += 1

    total_odd = sum(v3_T_counts.values())
    print(f"Total odd n tested: {total_odd}")
    print(f"v3(T(n)) distribution: {dict(v3_T_counts)}")
    assert v3_T_counts[0] == total_odd, "v3(T(n)) should always be 0!"
    print("CONFIRMED: v3(T(n)) = 0 for all odd n (T(n) never divisible by 3)")

    # =========================================================
    # Analysis 2: T(n) mod 3 の分布 (n mod 3 による条件付き)
    # =========================================================
    print("\n--- Analysis 2: T(n) mod 3 の分布 ---")
    mod3_conditional = defaultdict(Counter)
    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        r_n = n % 3
        r_t = t % 3
        mod3_conditional[r_n][r_t] += 1

    for r_n in sorted(mod3_conditional.keys()):
        cnt = mod3_conditional[r_n]
        total_rn = sum(cnt.values())
        print(f"  n ≡ {r_n} (mod 3): ", end="")
        for r_t in sorted(cnt.keys()):
            print(f"T(n)≡{r_t}: {cnt[r_t]} ({cnt[r_t]/total_rn:.4f})", end="  ")
        print()

    # =========================================================
    # Analysis 3: v3(T(n) - 1) と v3(T(n) - 2) の分布
    # =========================================================
    print("\n--- Analysis 3: v3(T(n)-1) と v3(T(n)-2) の分布 ---")
    v3_Tn_minus1 = Counter()
    v3_Tn_minus2 = Counter()

    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        v3_Tn_minus1[v3(t - 1)] += 1
        v3_Tn_minus2[v3(t - 2)] += 1

    print("v3(T(n)-1) distribution:")
    geo_expected_1_over_3 = {}
    for k in range(8):
        obs_1 = v3_Tn_minus1.get(k, 0)
        obs_2 = v3_Tn_minus2.get(k, 0)
        # T(n) mod 3 ∈ {1,2}, so v3(T(n)-1) counts those with T(n)≡1 mod 3^{k+1} roughly
        # For T(n)≡1 mod 3: v3(T(n)-1) >= 1 always
        # For T(n)≡2 mod 3: v3(T(n)-1) = 0 always
        # So v3(T(n)-1) = 0 iff T(n)≡2 mod 3
        geo_expected_1_over_3[k] = (2/3) * (1/3)**k  # rough model
        print(f"  v3(T(n)-1) = {k}: count={obs_1}, freq={obs_1/total_odd:.6f}")

    print("\nv3(T(n)-2) distribution:")
    for k in range(8):
        obs_2 = v3_Tn_minus2.get(k, 0)
        print(f"  v3(T(n)-2) = {k}: count={obs_2}, freq={obs_2/total_odd:.6f}")

    # =========================================================
    # Analysis 4: v3(T(n)-1) の条件付き分布 (T(n)≡1 mod 3 のみ)
    # T(n)≡1 mod 3 の場合、v3(T(n)-1) >= 1
    # v3(T(n)-1)-1 が Geo(1/3) に従うか
    # =========================================================
    print("\n--- Analysis 4: 条件付き分布 v3(T(n)-1) | T(n)≡1 mod 3 ---")
    v3_cond1 = Counter()  # v3(T(n)-1) when T(n) ≡ 1 mod 3
    v3_cond2 = Counter()  # v3(T(n)-2) when T(n) ≡ 2 mod 3

    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        if t % 3 == 1:
            v3_cond1[v3(t - 1)] += 1
        elif t % 3 == 2:
            v3_cond2[v3(t - 2)] += 1

    total_cond1 = sum(v3_cond1.values())
    total_cond2 = sum(v3_cond2.values())

    print(f"Count with T(n)≡1 mod 3: {total_cond1}")
    print(f"Count with T(n)≡2 mod 3: {total_cond2}")
    print(f"Ratio T≡1 / total: {total_cond1/total_odd:.6f} (expect ~1/3)")
    print(f"Ratio T≡2 / total: {total_cond2/total_odd:.6f} (expect ~2/3)")

    print("\nv3(T(n)-1) | T(n)≡1 mod 3 (should start at 1):")
    geo_test_1 = []
    for k in range(1, 8):
        obs = v3_cond1.get(k, 0)
        # Geo(1/3) shifted: P(v3=k) = (2/3)*(1/3)^{k-1} for k>=1
        expected = total_cond1 * (2/3) * (1/3)**(k-1)
        ratio = obs / expected if expected > 0 else float('inf')
        geo_test_1.append((k, obs, expected, ratio))
        print(f"  v3={k}: obs={obs}, expected_geo={expected:.1f}, ratio={ratio:.4f}")

    print("\nv3(T(n)-2) | T(n)≡2 mod 3 (should start at 1):")
    geo_test_2 = []
    for k in range(1, 8):
        obs = v3_cond2.get(k, 0)
        expected = total_cond2 * (2/3) * (1/3)**(k-1)
        ratio = obs / expected if expected > 0 else float('inf')
        geo_test_2.append((k, obs, expected, ratio))
        print(f"  v3={k}: obs={obs}, expected_geo={expected:.1f}, ratio={ratio:.4f}")

    # =========================================================
    # Analysis 5: v3(T(n)-1) の n mod 3 による条件付き分布
    # =========================================================
    print("\n--- Analysis 5: v3(T(n)-1) を n mod 3 で条件付け ---")
    v3_by_nmod3 = defaultdict(Counter)

    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        r_n = n % 3
        v3_by_nmod3[r_n][v3(t - 1)] += 1

    for r_n in sorted(v3_by_nmod3.keys()):
        cnt = v3_by_nmod3[r_n]
        total_rn = sum(cnt.values())
        print(f"  n ≡ {r_n} (mod 3): total={total_rn}")
        for k in range(6):
            obs = cnt.get(k, 0)
            print(f"    v3(T(n)-1)={k}: {obs} ({obs/total_rn:.6f})")

    # =========================================================
    # Analysis 6: 軌道上の連続 v3(T^k(n)-1) パターン
    # =========================================================
    print("\n--- Analysis 6: 軌道上の v3(T^k(n)-1) 連続パターン ---")
    # 軌道上で v3(T^k(n)-1) >= 2 (高い3-adic付値) が連続する頻度
    consecutive_high_v3 = Counter()  # 長さごとのカウント
    v3_orbit_autocorr = defaultdict(list)  # lag相関

    sample_orbits = range(1, min(50001, N_MAX + 1), 2)
    orbit_v3_values = []

    for n in sample_orbits:
        orbit = full_orbit(n, MAX_ORBIT_STEPS)
        v3_seq = [v3(x - 1) if x > 1 else 0 for x in orbit]
        orbit_v3_values.append(v3_seq)

        # 連続して v3 >= 1 (つまり T^k(n) ≡ 1 mod 3) となるランの長さ
        run_len = 0
        for v in v3_seq:
            if v >= 1:
                run_len += 1
            else:
                if run_len > 0:
                    consecutive_high_v3[run_len] += 1
                run_len = 0
        if run_len > 0:
            consecutive_high_v3[run_len] += 1

    print("Runs of consecutive T^k(n) ≡ 1 (mod 3) in orbits:")
    for length in sorted(consecutive_high_v3.keys())[:15]:
        print(f"  run length {length}: {consecutive_high_v3[length]} occurrences")

    # =========================================================
    # Analysis 7: 軌道上の T^k(n) mod 3 の遷移確率
    # =========================================================
    print("\n--- Analysis 7: 軌道上 T^k(n) mod 3 → T^{k+1}(n) mod 3 遷移行列 ---")
    transition = defaultdict(Counter)

    for v3_seq_data in orbit_v3_values:
        pass  # v3_seq から復元は面倒なので別途計算

    # 直接計算
    for n in range(1, min(100001, N_MAX + 1), 2):
        orbit = full_orbit(n, 200)
        for i in range(len(orbit) - 1):
            a = orbit[i] % 3
            b = orbit[i+1] % 3
            transition[a][b] += 1

    print("Transition matrix (row=current mod 3, col=next mod 3):")
    for a in [1, 2]:  # 0 is excluded since T(n) not div by 3
        total_a = sum(transition[a].values())
        if total_a > 0:
            row = {b: transition[a][b]/total_a for b in [1, 2]}
            print(f"  {a} → 1: {row.get(1,0):.6f}, 2: {row.get(2,0):.6f}")

    # =========================================================
    # Analysis 8: v3(T(n)-1) と v2(3n+1) の相関
    # =========================================================
    print("\n--- Analysis 8: v3(T(n)-1) と v2(3n+1) の相関 ---")
    v2_vals = []
    v3_minus1_vals = []

    for n in range(1, N_MAX + 1, 2):
        val_3n1 = 3 * n + 1
        v2_val = 0
        tmp = val_3n1
        while tmp % 2 == 0:
            tmp //= 2
            v2_val += 1
        t = val_3n1 // (2 ** v2_val)
        v3_val = v3(t - 1) if t > 1 else 0
        v2_vals.append(v2_val)
        v3_minus1_vals.append(v3_val)

    # v2 ごとの v3(T(n)-1) の平均
    v2_to_v3 = defaultdict(list)
    for v2v, v3v in zip(v2_vals, v3_minus1_vals):
        v2_to_v3[v2v].append(v3v)

    print("Mean v3(T(n)-1) conditioned on v2(3n+1):")
    for v2v in sorted(v2_to_v3.keys())[:10]:
        vals = v2_to_v3[v2v]
        mean_v3 = sum(vals) / len(vals)
        print(f"  v2(3n+1)={v2v}: mean_v3(T(n)-1)={mean_v3:.4f}, count={len(vals)}")

    # =========================================================
    # Analysis 9: v3(T^k(n)-1) の高い値の出現パターン
    # =========================================================
    print("\n--- Analysis 9: v3(T^k(n)-1) >= 3 の出現パターン ---")
    high_v3_examples = []

    for n in range(1, min(100001, N_MAX+1), 2):
        t = syracuse(n)
        v = v3(t - 1)
        if v >= 3:
            high_v3_examples.append((n, t, v, n % 9, n % 27, n % 81))

    print(f"Count with v3(T(n)-1) >= 3: {len(high_v3_examples)}")

    # n mod 27 の分布
    mod27_dist = Counter()
    mod81_dist = Counter()
    for (n, t, v, m9, m27, m81) in high_v3_examples:
        mod27_dist[m27] += 1
        mod81_dist[m81] += 1

    print(f"n mod 27 distribution (for v3(T(n)-1)>=3):")
    for r in sorted(mod27_dist.keys()):
        if mod27_dist[r] > 0:
            print(f"  n≡{r} (mod 27): {mod27_dist[r]}")

    # =========================================================
    # Analysis 10: v3(T^2(n)-1) の分布
    # =========================================================
    print("\n--- Analysis 10: v3(T^2(n)-1) の分布 ---")
    v3_T2_minus1 = Counter()
    for n in range(1, N_MAX + 1, 2):
        t1 = syracuse(n)
        t2 = syracuse(t1)
        v3_T2_minus1[v3(t2 - 1)] += 1

    print("v3(T^2(n)-1) distribution:")
    for k in range(8):
        obs = v3_T2_minus1.get(k, 0)
        print(f"  v3(T^2(n)-1) = {k}: count={obs}, freq={obs/total_odd:.6f}")

    # =========================================================
    # Analysis 11: 3^k | (T(n)-1) の代数的条件
    # =========================================================
    print("\n--- Analysis 11: 代数的条件 3|(T(n)-1) ⟺ 条件 ---")
    # T(n) = (3n+1)/2^v2(3n+1)
    # T(n) ≡ 1 mod 3 ⟺ (3n+1)/2^v ≡ 1 mod 3 ⟺ 1/2^v ≡ 1 mod 3
    # 2^v mod 3: v even → 1, v odd → 2
    # So T(n)≡1 mod 3 ⟺ v2(3n+1) even ⟺ 1≡1 mod 3 ✓
    # T(n)≡2 mod 3 ⟺ v2(3n+1) odd ⟺ 1/2≡2 mod 3 ✓

    # Verify algebraically
    even_v2_count = 0
    odd_v2_count = 0
    for n in range(1, N_MAX + 1, 2):
        val = 3 * n + 1
        v = 0
        while val % 2 == 0:
            val //= 2
            v += 1
        if v % 2 == 0:
            even_v2_count += 1
            assert val % 3 == 1, f"n={n}: v2 even but T(n) mod 3 != 1"
        else:
            odd_v2_count += 1
            assert val % 3 == 2, f"n={n}: v2 odd but T(n) mod 3 != 2"

    print(f"v2(3n+1) even (→ T(n)≡1 mod 3): {even_v2_count} ({even_v2_count/total_odd:.6f})")
    print(f"v2(3n+1) odd  (→ T(n)≡2 mod 3): {odd_v2_count} ({odd_v2_count/total_odd:.6f})")
    print("CONFIRMED: T(n) mod 3 is completely determined by parity of v2(3n+1)")

    # =========================================================
    # Analysis 12: v3(T(n)-1) >= 2 の正確な代数的条件
    # =========================================================
    print("\n--- Analysis 12: v3(T(n)-1) >= 2 の代数的条件 ---")
    # T(n)≡1 mod 9 の条件を調べる
    # T(n) = (3n+1)/2^v, T(n)≡1 mod 9
    # (3n+1)/2^v ≡ 1 mod 9 ⟺ 3n+1 ≡ 2^v mod 9
    # 3n+1 mod 9: depends on n mod 3
    # n=3m+1 (odd, so m can be anything): 3(3m+1)+1 = 9m+4
    # n=3m+2: 3(3m+2)+1 = 9m+7
    # n=3m (excluded since n odd and 3|n: n=3,9,15,...)
    #   Actually n can be 3m and odd: n=3,9,15,...
    #   3(3m)+1 = 9m+1

    v3_ge2_by_nmod9 = Counter()
    total_by_nmod9 = Counter()
    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        r = n % 9
        total_by_nmod9[r] += 1
        if v3(t - 1) >= 2:
            v3_ge2_by_nmod9[r] += 1

    print("v3(T(n)-1) >= 2 by n mod 9:")
    for r in sorted(total_by_nmod9.keys()):
        tot = total_by_nmod9[r]
        cnt = v3_ge2_by_nmod9.get(r, 0)
        frac = cnt / tot if tot > 0 else 0
        print(f"  n≡{r} (mod 9): {cnt}/{tot} = {frac:.6f}")

    # =========================================================
    # Analysis 13: v3(T(n)-1) の平均と分散 (理論予測との比較)
    # =========================================================
    print("\n--- Analysis 13: 統計量 ---")
    all_v3_minus1 = []
    all_v3_minus2 = []
    for n in range(1, N_MAX + 1, 2):
        t = syracuse(n)
        all_v3_minus1.append(v3(t - 1))
        all_v3_minus2.append(v3(t - 2))

    mean_v3_1 = sum(all_v3_minus1) / len(all_v3_minus1)
    mean_v3_2 = sum(all_v3_minus2) / len(all_v3_minus2)
    var_v3_1 = sum((x - mean_v3_1)**2 for x in all_v3_minus1) / len(all_v3_minus1)
    var_v3_2 = sum((x - mean_v3_2)**2 for x in all_v3_minus2) / len(all_v3_minus2)

    # Theoretical: if T(n) ≡ 1 mod 3 with prob 1/3 and ≡ 2 with prob 2/3
    # v3(T(n)-1): =0 with prob 2/3 (T≡2), then Geo(1/3) from 1 with prob 1/3
    # Mean = 1/3 * (1/(1-1/3)) = 1/3 * 3/2 = 1/2
    # Actually: E[v3(T(n)-1)] = sum_{k>=1} P(v3>=k) = sum_{k>=1} (1/3)^k = 1/2

    print(f"E[v3(T(n)-1)] = {mean_v3_1:.6f} (theoretical for uniform random: 1/2 = 0.5)")
    print(f"Var[v3(T(n)-1)] = {var_v3_1:.6f}")
    print(f"E[v3(T(n)-2)] = {mean_v3_2:.6f} (theoretical for uniform random: 1/2 = 0.5)")
    print(f"Var[v3(T(n)-2)] = {var_v3_2:.6f}")

    # Sum: v3(T(n)-1) + v3(T(n)-2) は T(n) mod 3 に依存
    # T≡1: v3(T-1)>=1, v3(T-2)=0
    # T≡2: v3(T-1)=0, v3(T-2)>=1
    # So exactly one of them is >= 1 always
    both_zero = sum(1 for a, b in zip(all_v3_minus1, all_v3_minus2) if a == 0 and b == 0)
    both_positive = sum(1 for a, b in zip(all_v3_minus1, all_v3_minus2) if a > 0 and b > 0)
    print(f"\nBoth v3(T-1)=0 and v3(T-2)=0: {both_zero} (should be 0)")
    print(f"Both v3(T-1)>0 and v3(T-2)>0: {both_positive} (should be 0)")

    # =========================================================
    # Analysis 14: 軌道上のmod3パターンのエントロピー変化
    # =========================================================
    print("\n--- Analysis 14: 軌道上のmod3パターンのMarkov性検証 ---")
    # T^k(n) mod 3 → T^{k+1}(n) mod 3 の遷移がMarkov的か
    # 2ステップ遷移を調べる
    transition_2step = defaultdict(Counter)

    for n in range(1, min(50001, N_MAX + 1), 2):
        orbit = full_orbit(n, 100)
        for i in range(len(orbit) - 2):
            pair = (orbit[i] % 3, orbit[i+1] % 3)
            nxt = orbit[i+2] % 3
            transition_2step[pair][nxt] += 1

    print("2-step transition (a,b) → c:")
    for pair in sorted(transition_2step.keys()):
        cnt = transition_2step[pair]
        total_p = sum(cnt.values())
        if total_p > 100:  # sufficient data
            probs = {c: cnt[c]/total_p for c in sorted(cnt.keys())}
            print(f"  ({pair[0]},{pair[1]}) → {probs}")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s")

    # =========================================================
    # Results compilation
    # =========================================================
    results = {
        "exploration_id": "v3_adic_orbit_distribution",
        "category": "3-adic_analysis",
        "description": "v3(T^k(n)-r)の分布とSyracuse軌道上の3-adic構造",
        "parameters": {
            "N_MAX": N_MAX,
            "MAX_ORBIT_STEPS": MAX_ORBIT_STEPS
        },
        "key_findings": {
            "v3_T_always_zero": True,
            "T_mod3_determined_by_v2_parity": True,
            "T_mod3_distribution": {
                "T_equiv_1": even_v2_count / total_odd,
                "T_equiv_2": odd_v2_count / total_odd,
            },
            "mean_v3_T_minus_1": mean_v3_1,
            "mean_v3_T_minus_2": mean_v3_2,
            "theoretical_mean": 0.5,
            "deviation_from_random_v3_T1": abs(mean_v3_1 - 0.5),
            "deviation_from_random_v3_T2": abs(mean_v3_2 - 0.5),
            "geo_test_v3_T1_ratios": [(k, r) for k, _, _, r in geo_test_1],
            "geo_test_v3_T2_ratios": [(k, r) for k, _, _, r in geo_test_2],
            "both_zero_count": both_zero,
            "both_positive_count": both_positive,
        },
        "transition_matrix_mod3": {
            str(a): {str(b): transition[a][b] / sum(transition[a].values())
                     for b in [1, 2]}
            for a in [1, 2] if sum(transition[a].values()) > 0
        },
        "v3_ge2_by_nmod9": {
            str(r): {
                "count": v3_ge2_by_nmod9.get(r, 0),
                "total": total_by_nmod9[r],
                "fraction": v3_ge2_by_nmod9.get(r, 0) / total_by_nmod9[r] if total_by_nmod9[r] > 0 else 0
            }
            for r in sorted(total_by_nmod9.keys())
        },
        "v3_T_minus1_distribution": {str(k): v3_Tn_minus1.get(k, 0) for k in range(8)},
        "v3_T_minus2_distribution": {str(k): v3_Tn_minus2.get(k, 0) for k in range(8)},
    }

    return results

if __name__ == "__main__":
    results = main()

    output_path = "/Users/soyukke/study/lean-unsolved/results/v3_adic_orbit_distribution.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")
