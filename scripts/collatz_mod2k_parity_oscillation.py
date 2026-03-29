#!/usr/bin/env python3
"""
探索: 非排除残基数のパリティ振動と分岐構造の精密解析

前段で発見された重要パターン:
- N(k)/N(k-1) が k の偶奇で振動: 偶数k で ~2.0, 奇数k で ~1.6
- 生存率は大半が 1.0 だが、特定の k で <1 になる
- 非排除残基は全て mod 4 ≡ 3 かつ v2=1

この探索では:
1. 偶奇振動の正確な特徴づけ
2. N(k) の正確な漸化式の同定
3. 分岐時の「新生」残基と「死亡」残基の構造的理由
"""

import json
import time
import math
from collections import Counter


def syracuse(n):
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    return val, v


def descent_steps(n, max_steps=200):
    original = n
    current = n
    for step in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return step
    return -1


def get_non_excluded(k, num_samples=50):
    mod = 2 ** k
    non_excluded = set()
    for r in range(1, mod, 2):
        steps_seen = set()
        for i in range(num_samples):
            n = r + mod * (2 * i + 1)
            s = descent_steps(n, max_steps=max(k * 3, 60))
            if s > 0:
                steps_seen.add(s)
            else:
                steps_seen.add(-1)
            if len(steps_seen) > 1:
                break
        if len(steps_seen) > 1:
            non_excluded.add(r)
    return non_excluded


def main():
    print("=" * 80)
    print("非排除残基数のパリティ振動と分岐構造")
    print("=" * 80)

    results = {
        "title": "非排除残基数のパリティ振動解析",
        "data": {},
    }

    # ============================================================
    # Part 1: k=3..16 の非排除残基を集合として保持
    # ============================================================
    print("\n[Part 1] 非排除残基の完全列挙")

    all_ne = {}
    configs = [
        (3, 200), (4, 200), (5, 200), (6, 200),
        (7, 150), (8, 150), (9, 120), (10, 100),
        (11, 80),  (12, 60),  (13, 40),  (14, 30),
        (15, 20),  (16, 15),
    ]

    for k, samples in configs:
        t0 = time.time()
        ne = get_non_excluded(k, num_samples=samples)
        elapsed = time.time() - t0
        all_ne[k] = ne
        print(f"  k={k:2d}: N(k) = {len(ne):5d} (time={elapsed:.1f}s)")

    N = {k: len(ne) for k, ne in all_ne.items()}

    # ============================================================
    # Part 2: 偶奇分離フィッティング
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 2] 偶数k と 奇数k の分離フィッティング")
    print("=" * 80)

    k_vals = sorted(N.keys())

    # 偶数k
    even_k = [(k, N[k]) for k in k_vals if k % 2 == 0 and k >= 6]
    odd_k = [(k, N[k]) for k in k_vals if k % 2 == 1 and k >= 7]

    print(f"\n  偶数k: {[(k, n) for k, n in even_k]}")
    print(f"  奇数k: {[(k, n) for k, n in odd_k]}")

    # N(k) ~ C * alpha^k の形でフィッティング
    for label, data in [("偶数k", even_k), ("奇数k", odd_k)]:
        if len(data) < 2:
            continue
        ks = [d[0] for d in data]
        log_ns = [math.log(d[1]) for d in data]
        n = len(ks)
        sum_k = sum(ks)
        sum_logn = sum(log_ns)
        sum_k2 = sum(ki**2 for ki in ks)
        sum_k_logn = sum(ki * li for ki, li in zip(ks, log_ns))
        denom = n * sum_k2 - sum_k**2
        if abs(denom) < 1e-10:
            continue
        slope = (n * sum_k_logn - sum_k * sum_logn) / denom
        intercept = (sum_logn - slope * sum_k) / n
        alpha = math.exp(slope)
        C = math.exp(intercept)

        print(f"\n  {label}: N(k) ~ {C:.4f} * {alpha:.6f}^k")
        print(f"    alpha = {alpha:.8f}, log2(alpha) = {math.log2(alpha):.6f}")
        print(f"    密度 = N(k)/2^(k-1) ~ {C:.4f} * ({alpha/2:.6f})^k")
        print(f"    密度の減衰率 = {alpha/2:.6f}")

        # 予測 vs 実測
        print(f"    {'k':>4} | {'実測':>8} | {'予測':>10} | {'誤差%':>8}")
        print(f"    " + "-" * 35)
        for ki, ni in data:
            pred = C * alpha ** ki
            err = abs(ni - pred) / ni * 100
            print(f"    {ki:>4} | {ni:>8} | {pred:>10.1f} | {err:>7.2f}%")

    # ============================================================
    # Part 3: N(k) の偶奇振動の正確な記述
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 3] N(k+2)/N(k) の比率（2ステップおきの成長率）")
    print("=" * 80)

    print(f"\n  {'k':>3} -> {'k+2':>3} | {'N(k)':>8} | {'N(k+2)':>8} | {'比率':>10}")
    print("  " + "-" * 45)

    ratios_2step = []
    for i in range(len(k_vals) - 2):
        k = k_vals[i]
        k2 = k_vals[i + 2]
        if k2 != k + 2:
            continue
        ratio = N[k2] / N[k]
        ratios_2step.append((k, ratio))
        print(f"  {k:>3} -> {k2:>3} | {N[k]:>8} | {N[k2]:>8} | {ratio:>10.6f}")

    if ratios_2step:
        # k >= 8 以降の平均
        stable = [r for k, r in ratios_2step if k >= 8]
        if stable:
            avg = sum(stable) / len(stable)
            print(f"\n  k>=8 以降の平均2ステップ成長率: {avg:.6f}")
            print(f"  対応する1ステップ率 = sqrt({avg:.6f}) = {math.sqrt(avg):.6f}")
            print(f"  密度減衰率 = {math.sqrt(avg)/2:.6f}")

    # ============================================================
    # Part 4: 分岐詳細解析
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 4] k -> k+1 での分岐パターンの詳細")
    print("=" * 80)

    for i in range(len(k_vals) - 1):
        k = k_vals[i]
        k1 = k_vals[i + 1]
        if k1 != k + 1:
            continue
        if k < 6:
            continue

        ne_k = all_ne[k]
        ne_k1 = all_ne[k1]
        mod_k = 2 ** k

        # 各親残基の子の状態
        both_ne = 0  # 両方の子が非排除
        one_ne = 0   # 片方だけ非排除
        none_ne = 0  # 両方とも排除（死亡）
        new_ne = 0   # 親が排除だが子が非排除（新生）

        for r in ne_k:
            c0 = r          # mod 2^(k+1)
            c1 = r + mod_k  # mod 2^(k+1)
            c0_ne = c0 in ne_k1
            c1_ne = c1 in ne_k1
            if c0_ne and c1_ne:
                both_ne += 1
            elif c0_ne or c1_ne:
                one_ne += 1
            else:
                none_ne += 1

        # 新生の数: ne_k1 の要素のうち、parent が ne_k にない
        for r1 in ne_k1:
            parent = r1 % mod_k
            if parent not in ne_k:
                new_ne += 1

        total_parent = len(ne_k)
        print(f"\n  k={k} -> {k1}: 親 {total_parent} 個")
        print(f"    両方非排除: {both_ne} ({both_ne/total_parent*100:.1f}%)")
        print(f"    片方非排除: {one_ne} ({one_ne/total_parent*100:.1f}%)")
        print(f"    両方排除:   {none_ne} ({none_ne/total_parent*100:.1f}%)")
        print(f"    新生:       {new_ne}")
        print(f"    検算: 2*both + one + new = {2*both_ne + one_ne + new_ne} = N(k+1) = {len(ne_k1)}")

    # ============================================================
    # Part 5: 偶数k -> 奇数k+1 vs 奇数k -> 偶数k+1 の区別
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 5] 偶数→奇数 vs 奇数→偶数 の分岐パターンの差異")
    print("=" * 80)

    even_to_odd = []
    odd_to_even = []

    for i in range(len(k_vals) - 1):
        k = k_vals[i]
        k1 = k_vals[i + 1]
        if k1 != k + 1 or k < 6:
            continue

        ne_k = all_ne[k]
        ne_k1 = all_ne[k1]
        mod_k = 2 ** k

        both = 0
        one = 0
        none_ = 0
        new_ = 0

        for r in ne_k:
            c0 = r
            c1 = r + mod_k
            c0_ne = c0 in ne_k1
            c1_ne = c1 in ne_k1
            if c0_ne and c1_ne:
                both += 1
            elif c0_ne or c1_ne:
                one += 1
            else:
                none_ += 1

        for r1 in ne_k1:
            parent = r1 % mod_k
            if parent not in ne_k:
                new_ += 1

        record = {
            "k": k,
            "N_k": len(ne_k),
            "N_k1": len(ne_k1),
            "both": both,
            "one": one,
            "none": none_,
            "new": new_,
            "ratio": len(ne_k1) / len(ne_k),
        }

        if k % 2 == 0:
            even_to_odd.append(record)
        else:
            odd_to_even.append(record)

    print("\n  偶数k -> 奇数k+1:")
    for rec in even_to_odd:
        print(f"    k={rec['k']:2d}: N={rec['N_k']:5d} -> {rec['N_k1']:5d} "
              f"(ratio={rec['ratio']:.4f}) both={rec['both']}, one={rec['one']}, "
              f"none={rec['none']}, new={rec['new']}")

    print("\n  奇数k -> 偶数k+1:")
    for rec in odd_to_even:
        print(f"    k={rec['k']:2d}: N={rec['N_k']:5d} -> {rec['N_k1']:5d} "
              f"(ratio={rec['ratio']:.4f}) both={rec['both']}, one={rec['one']}, "
              f"none={rec['none']}, new={rec['new']}")

    # 偶→奇 と 奇→偶 の平均分岐率
    if even_to_odd:
        avg_eo = sum(r['ratio'] for r in even_to_odd) / len(even_to_odd)
        avg_eo_k8 = [r['ratio'] for r in even_to_odd if r['k'] >= 8]
        print(f"\n  偶→奇の平均分岐率: {avg_eo:.4f}")
        if avg_eo_k8:
            print(f"  偶→奇の平均分岐率 (k>=8): {sum(avg_eo_k8)/len(avg_eo_k8):.4f}")

    if odd_to_even:
        avg_oe = sum(r['ratio'] for r in odd_to_even) / len(odd_to_even)
        avg_oe_k8 = [r['ratio'] for r in odd_to_even if r['k'] >= 8]
        print(f"  奇→偶の平均分岐率: {avg_oe:.4f}")
        if avg_oe_k8:
            print(f"  奇→偶の平均分岐率 (k>=8): {sum(avg_oe_k8)/len(avg_oe_k8):.4f}")

    # ============================================================
    # Part 6: 非排除残基の「深さ」分析
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 6] 非排除残基の『深さ』(最小の k で非排除となる k)")
    print("=" * 80)

    # k=16 の非排除残基について、何kから非排除だったかを追跡
    if 16 in all_ne:
        depth_dist = Counter()
        for r in all_ne[16]:
            min_k = 16
            for k in range(3, 16):
                if k in all_ne and (r % (2**k)) in all_ne[k]:
                    min_k = k
                    break
            depth_dist[min_k] += 1

        print(f"\n  k=16 の非排除残基 {len(all_ne[16])} 個の起源:")
        for depth in sorted(depth_dist.keys()):
            pct = depth_dist[depth] / len(all_ne[16]) * 100
            print(f"    深さ {depth:2d} から: {depth_dist[depth]:5d} ({pct:.1f}%)")

    # ============================================================
    # Part 7: 成長率の偶奇パターンの数学的モデル
    # ============================================================
    print("\n" + "=" * 80)
    print("[Part 7] 成長率モデルの検証")
    print("=" * 80)

    # 仮説: N(k) ~ C * alpha^k * (1 + epsilon * (-1)^k) の形
    # 偶数k: N(k) ~ C * alpha^k * (1 + epsilon)
    # 奇数k: N(k) ~ C * alpha^k * (1 - epsilon)

    # alpha と epsilon を推定
    if len(even_k) >= 2 and len(odd_k) >= 2:
        # 偶数k の alpha_e
        log_ne_even = [(k, math.log(n)) for k, n in even_k if n > 0]
        # 奇数k の alpha_o
        log_ne_odd = [(k, math.log(n)) for k, n in odd_k if n > 0]

        # 全体でフィッティング
        all_data = [(k, N[k]) for k in k_vals if k >= 8]
        ks = [d[0] for d in all_data]
        log_ns = [math.log(d[1]) for d in all_data]
        parities = [(-1)**k for k in ks]

        # N(k) ~ exp(a + b*k + c*(-1)^k)
        # log N(k) ~ a + b*k + c*(-1)^k
        # 3変数の最小二乗法
        n_data = len(ks)
        X = [[1, ki, pi] for ki, pi in zip(ks, parities)]
        # 正規方程式
        XtX = [[sum(X[i][j] * X[i][l] for i in range(n_data)) for l in range(3)] for j in range(3)]
        Xty = [sum(X[i][j] * log_ns[i] for i in range(n_data)) for j in range(3)]

        # 3x3 連立方程式を解く (Cramer)
        def det3(m):
            return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
                   -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                   +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

        D = det3(XtX)
        if abs(D) > 1e-10:
            def replace_col(M, col, b):
                M2 = [row[:] for row in M]
                for i in range(3):
                    M2[i][col] = b[i]
                return M2

            a_coeff = det3(replace_col(XtX, 0, Xty)) / D
            b_coeff = det3(replace_col(XtX, 1, Xty)) / D
            c_coeff = det3(replace_col(XtX, 2, Xty)) / D

            alpha = math.exp(b_coeff)
            C_val = math.exp(a_coeff)
            epsilon = c_coeff  # log-space での振幅

            print(f"\n  モデル: N(k) ~ {C_val:.4f} * {alpha:.6f}^k * exp({epsilon:.4f} * (-1)^k)")
            print(f"  = {C_val:.4f} * {alpha:.6f}^k * (偶数k: x{math.exp(epsilon):.4f}, 奇数k: x{math.exp(-epsilon):.4f})")
            print(f"  基本成長率 alpha = {alpha:.8f}")
            print(f"  密度減衰率 = alpha/2 = {alpha/2:.8f}")
            print(f"  偶奇振幅 epsilon = {epsilon:.6f}")

            # 予測 vs 実測
            print(f"\n    {'k':>4} | {'実測':>8} | {'予測':>10} | {'誤差%':>8}")
            print(f"    " + "-" * 35)
            for ki in k_vals:
                if ki < 6:
                    continue
                pred = C_val * alpha**ki * math.exp(epsilon * (-1)**ki)
                actual = N[ki]
                err = abs(actual - pred) / actual * 100
                print(f"    {ki:>4} | {actual:>8} | {pred:>10.1f} | {err:>7.2f}%")

            results["data"]["oscillation_model"] = {
                "C": round(C_val, 6),
                "alpha": round(alpha, 8),
                "epsilon": round(epsilon, 6),
                "density_decay": round(alpha/2, 8),
            }

    # ============================================================
    # 最終まとめ
    # ============================================================
    print("\n" + "=" * 80)
    print("最終まとめ")
    print("=" * 80)

    summary = {
        "key_numbers": {k: N[k] for k in k_vals},
        "density": {k: N[k] / 2**(k-1) for k in k_vals},
    }

    print("\n  非排除残基数の数列 (k=3..16):")
    seq = [N[k] for k in k_vals]
    print(f"    {seq}")

    print(f"\n  2ステップ成長率 N(k+2)/N(k):")
    for i in range(len(k_vals) - 2):
        k = k_vals[i]
        if k_vals[i+2] == k + 2 and k >= 6:
            r = N[k+2] / N[k]
            print(f"    N({k+2})/N({k}) = {N[k+2]}/{N[k]} = {r:.6f}")

    results["data"]["summary"] = summary

    # OEIS検索用の数列を表示
    print(f"\n  OEIS検索用: {','.join(str(N[k]) for k in k_vals)}")

    output_path = "/Users/soyukke/study/lean-unsolved/results/mod2k_parity_oscillation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n結果を {output_path} に保存しました。")


if __name__ == "__main__":
    main()
