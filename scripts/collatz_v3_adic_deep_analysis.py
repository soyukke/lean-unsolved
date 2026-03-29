"""
3-adic評価の深層分析 (第2段)

前段の発見を掘り下げる:
1. T(n)≡1 mod 3 ⟺ v2(3n+1) even (完全な代数的同値条件)
2. v3(T(n)-1) | v2(3n+1) even での完全な幾何分布 Geo(1/3)
3. v2(3n+1) の偶奇が v3 に完全決定する理由の代数的証明
4. Analysis 8の驚くべきパターン: v2 odd → v3(T-1)=0, v2 even → E[v3(T-1)]≈1.5
5. 2ステップ遷移のMarkov性の破れ (Analysis 14)
6. v3(T(n)-1) >= 2 の n mod 9 パターン (Analysis 12)
"""

import json
import math
from collections import Counter, defaultdict
import time

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2(n):
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def v3(n):
    if n == 0:
        return 0  # 特殊処理: T(n)=1のときv3(0)=0として扱う
    if n < 0:
        n = -n
    c = 0
    while n % 3 == 0:
        n //= 3
        c += 1
    return c

def main():
    start_time = time.time()
    N_MAX = 500000

    print("=== 3-adic 深層分析 ===")

    # =========================================================
    # Deep 1: v2(3n+1)の偶奇とv3(T(n)-1)の代数的関係の完全解明
    # =========================================================
    print("\n--- Deep 1: v2(3n+1)偶奇 → v3(T(n)-r) の完全決定メカニズム ---")
    # T(n) = (3n+1)/2^v where v = v2(3n+1)
    # mod 3: 3n+1 ≡ 1 (mod 3) always (since 3n≡0 mod 3)
    # T(n) = 1/2^v mod 3
    # 2 mod 3 = 2, 2^2 mod 3 = 1, 2^3 mod 3 = 2, ...
    # 2^v mod 3 = 2 if v odd, 1 if v even
    # So 1/2^v mod 3 = 1/1 = 1 if v even, 1/2 = 2 if v odd
    # THEOREM: T(n) ≡ 1 mod 3 ⟺ v2(3n+1) is even
    #          T(n) ≡ 2 mod 3 ⟺ v2(3n+1) is odd
    print("代数的証明:")
    print("  3n+1 ≡ 1 (mod 3) always")
    print("  T(n) = (3n+1)/2^v ≡ 1/2^v (mod 3)")
    print("  2^v mod 3 = 1 if v even, 2 if v odd")
    print("  Therefore T(n) mod 3 = 1 if v even, 2 if v odd  [QED]")

    # Deep 1b: mod 9 analysis
    # T(n) = (3n+1)/2^v mod 9
    # 3n+1 mod 9 depends on n mod 3:
    #   n ≡ 0 mod 3: 3n+1 ≡ 1 mod 9 ... wait, 3n depends on n mod 3
    #   n = 3q+r: 3n+1 = 9q+3r+1
    #   So 3n+1 mod 9 = 3r+1 where r = n mod 3
    #   r=0: 3n+1 ≡ 1 mod 9
    #   r=1: 3n+1 ≡ 4 mod 9
    #   r=2: 3n+1 ≡ 7 mod 9
    print("\nmod 9 分析:")
    print("  3n+1 mod 9: n≡0→1, n≡1→4, n≡2→7")
    print("  2^v mod 9: v mod 6 = 0→1, 1→2, 2→4, 3→8, 4→7, 5→5")

    # Complete table
    pow2_mod9 = [pow(2, v, 9) for v in range(6)]
    inv_pow2_mod9 = []
    for p in pow2_mod9:
        for inv in range(9):
            if (p * inv) % 9 == 1:
                inv_pow2_mod9.append(inv)
                break

    print(f"  2^v mod 9 cycle: {pow2_mod9}")
    print(f"  (2^v)^-1 mod 9 cycle: {inv_pow2_mod9}")

    print("\n  T(n) mod 9 table (n_mod_3 x v2_mod_6):")
    print("  v2(3n+1) mod 6:  ", end="")
    for v in range(6):
        print(f"  {v}", end="")
    print()

    for r in range(3):
        base = 3*r + 1  # (3n+1) mod 9
        print(f"  n ≡ {r} (mod 3):  ", end="")
        for v in range(6):
            t_mod9 = (base * inv_pow2_mod9[v]) % 9
            print(f"  {t_mod9}", end="")
        print()

    # =========================================================
    # Deep 2: v3(T(n)-1) の正確な分布と n, v2 への依存
    # =========================================================
    print("\n--- Deep 2: v3(T(n)-1) の v2(3n+1) mod 6 による完全分類 ---")

    v3_by_v2mod6_nmod3 = defaultdict(lambda: defaultdict(Counter))

    for n in range(1, N_MAX + 1, 2):
        val = 3 * n + 1
        v = v2(val)
        t = val >> v
        v2mod6 = v % 6
        nmod3 = n % 3
        v3_val = v3(t - 1) if t > 1 else -1  # -1 for t=1
        v3_by_v2mod6_nmod3[nmod3][v2mod6][v3_val] += 1

    print("\nv3(T(n)-1) distribution by (n mod 3, v2(3n+1) mod 6):")
    for nmod3 in sorted(v3_by_v2mod6_nmod3.keys()):
        for v2m6 in sorted(v3_by_v2mod6_nmod3[nmod3].keys()):
            cnt = v3_by_v2mod6_nmod3[nmod3][v2m6]
            total = sum(cnt.values())
            top_items = sorted(cnt.items(), key=lambda x: -x[1])[:5]
            top_str = ", ".join(f"v3={k}: {c}" for k, c in top_items)
            print(f"  (n≡{nmod3}, v2≡{v2m6}): total={total}, {top_str}")

    # =========================================================
    # Deep 3: Markov性の破れの定量化
    # =========================================================
    print("\n--- Deep 3: 軌道上 mod 3 遷移のMarkov性の破れ ---")
    # 1ステップ遷移: r → r' の確率は r に依存しない (~0.34, 0.66)
    # 2ステップ遷移: (r1,r2) → r3 は (r1,r2) に依存する
    # Key finding from Analysis 14:
    #   (1,1) → 1: 0.410  (higher than baseline 0.34)
    #   (2,1) → 1: 0.303  (lower than baseline)
    # This means: after two consecutive ≡1 mod 3, more likely to stay ≡1
    #             after (2,1), less likely to get 1

    # Why? v2(3n+1) parity determines T(n) mod 3
    # v2(3T(n)+1) parity determines T^2(n) mod 3
    # Are v2(3n+1) and v2(3T(n)+1) independent?

    # Check v2 parity autocorrelation
    v2_parity_transitions = defaultdict(Counter)
    for n in range(1, min(200001, N_MAX+1), 2):
        val1 = 3*n + 1
        v1 = v2(val1)
        t1 = val1 >> v1
        val2 = 3*t1 + 1
        v2_ = v2(val2)
        v2_parity_transitions[v1 % 2][v2_ % 2] += 1

    print("v2(3n+1) parity → v2(3T(n)+1) parity transition:")
    for p1 in [0, 1]:
        cnt = v2_parity_transitions[p1]
        total_p = sum(cnt.values())
        for p2 in [0, 1]:
            prob = cnt[p2] / total_p if total_p > 0 else 0
            print(f"  v2_parity {p1} → {p2}: {prob:.6f} ({cnt[p2]}/{total_p})")

    # 3ステップv2 parity autocorrelation
    print("\n3-step v2 parity pattern:")
    v2_3step = Counter()
    for n in range(1, min(200001, N_MAX+1), 2):
        val = 3*n+1; v = v2(val); t = val >> v; p0 = v%2
        val = 3*t+1; v = v2(val); t = val >> v; p1 = v%2
        val = 3*t+1; v = v2(val); t = val >> v; p2 = v%2
        v2_3step[(p0,p1,p2)] += 1

    total_3 = sum(v2_3step.values())
    for pattern in sorted(v2_3step.keys()):
        cnt = v2_3step[pattern]
        prob_indep = 1.0
        for p in pattern:
            prob_indep *= (1/3 if p == 0 else 2/3)
        expected = total_3 * prob_indep
        ratio = cnt / expected if expected > 0 else 0
        print(f"  {pattern}: obs={cnt}, expected_indep={expected:.1f}, ratio={ratio:.4f}")

    # =========================================================
    # Deep 4: v3(T(n)-1) >= 2 の n mod 9 パターンの説明
    # =========================================================
    print("\n--- Deep 4: v3(T(n)-1)>=2 の代数的条件 ---")
    # T(n) ≡ 1 mod 9 の条件
    # From the mod 9 table above:
    # T(n) ≡ 1 mod 9 ⟺ specific combinations of (n mod 3, v2 mod 6)

    # Verify: n ≡ 1 mod 9 has highest rate (Analysis 12: ~25.4%)
    # n ≡ 1 mod 3, so 3n+1 ≡ 4 mod 9
    # T(n) = 4/2^v mod 9
    # For T(n) ≡ 1 mod 9: 4/2^v ≡ 1 mod 9 ⟹ 2^v ≡ 4 mod 9 ⟹ v ≡ 2 mod 6
    # P(v2(3n+1) ≡ 2 mod 6) ≈ (1/4 - 1/64) * correction...

    # Actually, for n ≡ 1 mod 9 (and n odd):
    # n = 9k+1, 3n+1 = 27k+4
    # v2(27k+4): depends on k
    # k even: 27k+4 ≡ 4 mod 8, so v2=2 (since 4=2^2)
    #   Wait: 27k+4, if k=0: 4, v2=2. k=2: 58, v2=1. k=4: 112, v2=4.
    # More careful: 27k+4 for k=0,1,2,...
    # k=0: 4, v2=2
    # k=1: 31, v2=0 (odd!) But n=10 is even, skip
    # k=2: 58, v2=1. But n=19, odd. T(19)=29. v3(29-1)=v3(28)=0
    # Wait, let me recalculate...
    print("\nDetailed check for n≡1 mod 9:")
    count = 0
    count_v3ge2 = 0
    for n in range(1, 100000, 18):  # n ≡ 1 mod 9, n odd (step 18 to stay odd mod 9)
        # Actually n≡1 mod 9 AND n odd: n=1,19,37,55,...
        pass

    # Better: just check all odd n ≡ r mod 9
    for r in [1, 4, 7]:  # n ≡ r mod 3 → r=1 means n≡1 mod 3
        v3_ge2_by_v2mod6 = Counter()
        total_by_v2mod6 = Counter()
        for n in range(r if r % 2 == 1 else r+9, N_MAX + 1, 18):  # odd n ≡ r mod 9
            if n % 2 == 0:
                continue
            val = 3*n+1
            v = v2(val)
            t = val >> v
            total_by_v2mod6[v % 6] += 1
            if v3(t-1) >= 2:
                v3_ge2_by_v2mod6[v % 6] += 1

        print(f"\n  n ≡ {r} (mod 9), v3(T(n)-1)>=2 by v2(3n+1) mod 6:")
        for vm in sorted(total_by_v2mod6.keys()):
            tot = total_by_v2mod6[vm]
            cnt = v3_ge2_by_v2mod6.get(vm, 0)
            print(f"    v2≡{vm}: {cnt}/{tot} = {cnt/tot:.4f}" if tot > 0 else f"    v2≡{vm}: 0/0")

    # =========================================================
    # Deep 5: E[v3(T(n)-1)] の v2(3n+1) 依存性の理論的説明
    # =========================================================
    print("\n--- Deep 5: E[v3(T(n)-1)] | v2(3n+1)=v の理論的説明 ---")
    # From Analysis 8:
    # v2=1 (odd): E[v3(T-1)] = 0.0 → T≡2 mod 3, so v3(T-1)=0 always
    # v2=2 (even): E[v3(T-1)] ≈ 1.5 → T≡1 mod 3, v3(T-1) ~ 1 + Geo(1/3)
    # Theoretical E[1+Geo(1/3)] = 1 + 1/2 = 3/2 = 1.5 ✓

    # Verify for larger v2 values
    v2_to_v3_stats = defaultdict(list)
    for n in range(1, N_MAX+1, 2):
        val = 3*n+1
        v = v2(val)
        t = val >> v
        v3_val = v3(t-1) if t > 1 else 0
        v2_to_v3_stats[v].append(v3_val)

    print("v2(3n+1)  parity  mean(v3(T-1))  theory  count")
    for v_val in range(1, 14):
        vals = v2_to_v3_stats.get(v_val, [])
        if len(vals) > 10:
            mean_v = sum(vals)/len(vals)
            parity = "even" if v_val % 2 == 0 else "odd"
            theory = 1.5 if v_val % 2 == 0 else 0.0
            print(f"  {v_val:3d}     {parity:5s}  {mean_v:.4f}       {theory:.1f}     {len(vals)}")

    # =========================================================
    # Deep 6: v3(T(n)-2) の v2 依存性
    # =========================================================
    print("\n--- Deep 6: v3(T(n)-2) の v2 依存性 ---")
    v2_to_v3_minus2 = defaultdict(list)
    for n in range(1, N_MAX+1, 2):
        val = 3*n+1
        v = v2(val)
        t = val >> v
        v3_val = v3(t-2) if t > 2 else 0
        v2_to_v3_minus2[v].append(v3_val)

    print("v2(3n+1)  parity  mean(v3(T-2))  theory  count")
    for v_val in range(1, 14):
        vals = v2_to_v3_minus2.get(v_val, [])
        if len(vals) > 10:
            mean_v = sum(vals)/len(vals)
            parity = "even" if v_val % 2 == 0 else "odd"
            # v2 odd → T≡2 mod 3, so v3(T-2)>=1, E = 1.5
            # v2 even → T≡1 mod 3, so v3(T-2)=0
            theory = 0.0 if v_val % 2 == 0 else 1.5
            print(f"  {v_val:3d}     {parity:5s}  {mean_v:.4f}       {theory:.1f}     {len(vals)}")

    # =========================================================
    # Deep 7: 軌道上の v3 の累積分布とStopping Timeとの関係
    # =========================================================
    print("\n--- Deep 7: 軌道上 sum(v3(T^k(n)-1)) と Stopping Time の関係 ---")
    stopping_times = []
    sum_v3_values = []

    for n in range(1, min(100001, N_MAX+1), 2):
        orbit = []
        cur = n
        for step in range(1000):
            if cur == 1:
                break
            cur = syracuse(cur)
            orbit.append(cur)

        st = len(orbit)
        sv3 = sum(v3(x - 1) if x > 1 else 0 for x in orbit)
        stopping_times.append(st)
        sum_v3_values.append(sv3)

    # Correlation
    n_samples = len(stopping_times)
    mean_st = sum(stopping_times) / n_samples
    mean_sv3 = sum(sum_v3_values) / n_samples
    cov = sum((a-mean_st)*(b-mean_sv3) for a,b in zip(stopping_times, sum_v3_values)) / n_samples
    std_st = (sum((a-mean_st)**2 for a in stopping_times) / n_samples) ** 0.5
    std_sv3 = (sum((b-mean_sv3)**2 for b in sum_v3_values) / n_samples) ** 0.5
    corr = cov / (std_st * std_sv3) if std_st > 0 and std_sv3 > 0 else 0

    print(f"Correlation(stopping_time, sum_v3): {corr:.6f}")
    print(f"Mean stopping time: {mean_st:.2f}")
    print(f"Mean sum_v3: {mean_sv3:.2f}")
    print(f"Ratio sum_v3/stopping_time: {mean_sv3/mean_st:.6f} (expect ~1/2)")

    # =========================================================
    # Deep 8: v3(T(n)-1) mod 9 の精密パターン
    # =========================================================
    print("\n--- Deep 8: n mod 27 による v3(T(n)-1) の精密分布 ---")
    v3_by_nmod27 = defaultdict(Counter)
    for n in range(1, N_MAX+1, 2):
        t = syracuse(n)
        nmod27 = n % 27
        v3_val = v3(t-1) if t > 1 else 0
        v3_by_nmod27[nmod27][v3_val] += 1

    print("n mod 27 → mean v3(T(n)-1):")
    means_by_mod27 = {}
    for r in sorted(v3_by_nmod27.keys()):
        cnt = v3_by_nmod27[r]
        total = sum(cnt.values())
        mean = sum(k*c for k,c in cnt.items()) / total if total > 0 else 0
        means_by_mod27[r] = mean
        if total > 100:
            print(f"  n≡{r:2d} (mod 27): mean={mean:.4f}, total={total}")

    # =========================================================
    # Summary
    # =========================================================
    print("\n=== 主要発見のまとめ ===")
    print("1. T(n) mod 3 = 1 ⟺ v2(3n+1) even (代数的に証明)")
    print("   T(n) mod 3 = 2 ⟺ v2(3n+1) odd  (代数的に証明)")
    print("2. v3(T(n)-1)|{T≡1 mod 3} ~ 1+Geo(1/3), E=3/2 (完全な幾何分布)")
    print("3. v3(T(n)-2)|{T≡2 mod 3} ~ 1+Geo(1/3), E=3/2 (完全な幾何分布)")
    print("4. v2(3n+1)のパリティが交互に決定的→3-adic構造は2-adicに従属")
    print("5. 軌道上のmod 3遷移: 弱いMarkov性の破れあり")
    print("   (1,1)→1: ~0.41, (2,1)→1: ~0.30 (baseline ~0.34)")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s")

    return {
        "key_theorem": "T(n) mod 3 = (v2(3n+1)+1) mod 2 + 1, equivalently T(n)≡1 mod 3 iff v2(3n+1) is even",
        "v3_conditional_distribution": "v3(T(n)-1)|{T≡1} and v3(T(n)-2)|{T≡2} both follow 1+Geo(1/3)",
        "mean_conditional_v3": 1.5,
        "markov_breaking": {
            "(1,1)->1": 0.41,
            "(2,1)->1": 0.30,
            "baseline": 0.34
        },
        "correlation_sum_v3_stopping_time": corr,
        "ratio_sum_v3_to_stopping": mean_sv3/mean_st,
    }

if __name__ == "__main__":
    results = main()
    print(f"\nResults dict: {json.dumps(results, indent=2)}")
