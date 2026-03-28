#!/usr/bin/env python3
"""
探索: stopping time 尾部分布の精密分析（第2弾）

Phase 1の結果から、max ST ≈ O(log(N)^2) だが C≧1.5 では超える数がゼロ。
→ 閾値を C*log(N) ベースに変更し、密度のスケーリングを精密に調べる。
また ST/log(n) の分布を詳細に分析。
"""

import math
import time
from collections import Counter
import statistics

def syracuse(n):
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def total_stopping_time(n):
    steps = 0
    current = n
    while current != 1:
        current = syracuse(current)
        steps += 1
        if steps > 100000:
            return steps
    return steps

def trailing_ones(n):
    count = 0
    while n & 1:
        n >>= 1
        count += 1
    return count

def main():
    t0 = time.time()

    print("=" * 70)
    print("探索: Stopping Time 尾部分布の精密分析")
    print("=" * 70)

    # ==============================
    # Phase A: ST/log(n) 比率の精密分布
    # ==============================
    print("\n[Phase A] ST/log(n) 比率分布のスケール依存性")

    all_data = {}  # k -> list of (n, st)

    for k in range(3, 8):
        N = 10 ** k
        st_list = []
        for n in range(3, N + 1, 2):
            st = total_stopping_time(n)
            st_list.append((n, st))
        all_data[k] = st_list

        ratios = [st / math.log(n) for n, st in st_list]
        mean_r = statistics.mean(ratios)
        std_r = statistics.stdev(ratios)
        max_r = max(ratios)
        p99 = sorted(ratios)[int(len(ratios) * 0.99)]
        p999 = sorted(ratios)[int(len(ratios) * 0.999)]

        print(f"  k={k} (N=10^{k}): mean={mean_r:.4f}, std={std_r:.4f}, "
              f"99%={p99:.4f}, 99.9%={p999:.4f}, max={max_r:.4f}")

    # ==============================
    # Phase B: 閾値 C*log(N) での密度
    # ==============================
    print("\n[Phase B] ST > C*log(N) となる密度のスケーリング")

    C_vals = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    density_table = {}

    for C in C_vals:
        row = []
        for k in sorted(all_data.keys()):
            N = 10 ** k
            logN = math.log(N)
            threshold = C * logN
            st_list = all_data[k]
            count_exceed = sum(1 for _, st in st_list if st > threshold)
            density = count_exceed / len(st_list)
            row.append((k, density, count_exceed))
        density_table[C] = row

    for C in C_vals:
        print(f"\n  C={C:.1f}:")
        for k, dens, cnt in density_table[C]:
            logN = math.log(10**k)
            thr = C * logN
            print(f"    k={k}: threshold={thr:.1f}, density={dens:.8f} ({cnt}件)")

    # スケーリング: 固定閾値tでの P(ST > t) をNで見る
    print("\n[Phase C] 固定閾値 t での密度のN依存性")
    for t_fixed in [50, 75, 100, 125, 150, 175, 200]:
        print(f"\n  t={t_fixed}:")
        prev_dens = None
        for k in sorted(all_data.keys()):
            N = 10**k
            st_list = all_data[k]
            cnt = sum(1 for _, st in st_list if st > t_fixed)
            dens = cnt / len(st_list)
            ratio_str = ""
            if prev_dens is not None and prev_dens > 0 and dens > 0:
                ratio_str = f", N*10→dens*{prev_dens/dens:.3f}"
            prev_dens = dens
            print(f"    k={k}: density={dens:.8f} ({cnt}件){ratio_str}")

    # ==============================
    # Phase D: 尾部のべき乗/指数判定
    # ==============================
    print("\n[Phase D] N=10^7 での累積分布テイルの形状")

    k = 7
    st_all = sorted([st for _, st in all_data[k]])
    total = len(st_all)
    mean_st = statistics.mean(st_all)
    median_st = statistics.median(st_all)

    print(f"  N=10^7: mean={mean_st:.2f}, median={median_st:.2f}")

    # P(ST > t) for various t
    print(f"\n  t, P(ST>t), -log(P):")
    tail_points = []
    for t in range(50, 260, 5):
        cnt = sum(1 for s in st_all if s > t)
        if cnt > 0:
            p = cnt / total
            tail_points.append((t, p))
            if t % 20 == 0:
                print(f"    t={t}: P={p:.8f}, -log(P)={-math.log(p):.4f}")

    # フィット: 尾部(t > mean)で log P(ST>t) = a + b*t (指数)
    fit_points = [(t, math.log(p)) for t, p in tail_points if t > mean_st and p > 1e-6]
    if len(fit_points) >= 5:
        xs = [x for x, _ in fit_points]
        ys = [y for _, y in fit_points]
        n_f = len(xs)
        sx = sum(xs); sy = sum(ys); sxy = sum(x*y for x,y in zip(xs,ys)); sx2 = sum(x*x for x in xs)
        denom = n_f*sx2 - sx*sx
        b_exp = (n_f*sxy - sx*sy)/denom
        a_exp = (sy - b_exp*sx)/n_f
        # R^2
        y_pred = [a_exp + b_exp*x for x in xs]
        ss_res = sum((y-yp)**2 for y,yp in zip(ys, y_pred))
        y_mean = sy/n_f
        ss_tot = sum((y-y_mean)**2 for y in ys)
        r2_exp = 1 - ss_res/ss_tot if ss_tot > 0 else 0
        print(f"\n  指数フィット: log P = {a_exp:.4f} + {b_exp:.6f}*t, R²={r2_exp:.6f}")
        print(f"    → P(ST>t) ~ exp({b_exp:.6f}*t), 半減期={-math.log(2)/b_exp:.1f}")

    # フィット: log P(ST>t) = a + b*log(t) (べき乗)
    fit_points2 = [(math.log(t), math.log(p)) for t, p in tail_points if t > mean_st and p > 1e-6]
    if len(fit_points2) >= 5:
        xs = [x for x, _ in fit_points2]
        ys = [y for _, y in fit_points2]
        n_f = len(xs)
        sx = sum(xs); sy = sum(ys); sxy = sum(x*y for x,y in zip(xs,ys)); sx2 = sum(x*x for x in xs)
        denom = n_f*sx2 - sx*sx
        b_pow = (n_f*sxy - sx*sy)/denom
        a_pow = (sy - b_pow*sx)/n_f
        y_pred = [a_pow + b_pow*x for x in xs]
        ss_res = sum((y-yp)**2 for y,yp in zip(ys, y_pred))
        y_mean = sy/n_f
        ss_tot = sum((y-y_mean)**2 for y in ys)
        r2_pow = 1 - ss_res/ss_tot if ss_tot > 0 else 0
        print(f"  べき乗フィット: log P = {a_pow:.4f} + {b_pow:.4f}*log(t), R²={r2_pow:.6f}")
        print(f"    → P(ST>t) ~ t^({b_pow:.2f})")

    # フィット: log P(ST>t) = a + b*t^2 (ガウス的)
    fit_points3 = [(t**2, math.log(p)) for t, p in tail_points if t > mean_st and p > 1e-6]
    if len(fit_points3) >= 5:
        xs = [x for x, _ in fit_points3]
        ys = [y for _, y in fit_points3]
        n_f = len(xs)
        sx = sum(xs); sy = sum(ys); sxy = sum(x*y for x,y in zip(xs,ys)); sx2 = sum(x*x for x in xs)
        denom = n_f*sx2 - sx*sx
        b_gauss = (n_f*sxy - sx*sy)/denom
        a_gauss = (sy - b_gauss*sx)/n_f
        y_pred = [a_gauss + b_gauss*x for x in xs]
        ss_res = sum((y-yp)**2 for y,yp in zip(ys, y_pred))
        y_mean = sy/n_f
        ss_tot = sum((y-y_mean)**2 for y in ys)
        r2_gauss = 1 - ss_res/ss_tot if ss_tot > 0 else 0
        print(f"  ガウスフィット: log P = {a_gauss:.6f} + {b_gauss:.8f}*t², R²={r2_gauss:.6f}")
        print(f"    → P(ST>t) ~ exp({b_gauss:.8f}*t²)")

    print(f"\n  ベストフィット: ", end="")
    models = [("指数", r2_exp), ("べき乗", r2_pow), ("ガウス", r2_gauss)]
    models.sort(key=lambda x: -x[1])
    for name, r2 in models:
        print(f"{name}(R²={r2:.6f}) ", end="")
    print()

    # ==============================
    # Phase E: 末尾ビットと ST の関係（定量化）
    # ==============================
    print("\n[Phase E] 末尾連続1ビット数と平均STの関係")

    k = 7
    st_by_trail = {}
    for n, st in all_data[k]:
        tr = trailing_ones(n)
        if tr not in st_by_trail:
            st_by_trail[tr] = []
        st_by_trail[tr].append(st)

    for tr in sorted(st_by_trail.keys()):
        vals = st_by_trail[tr]
        if len(vals) >= 10:
            m = statistics.mean(vals)
            s = statistics.stdev(vals) if len(vals) > 1 else 0
            mx = max(vals)
            print(f"  trail_1s={tr:2d}: count={len(vals):7d}, mean_ST={m:.2f}, std={s:.2f}, max={mx}")

    # ==============================
    # Phase F: mod residue と ST の関係
    # ==============================
    print("\n[Phase F] mod 残基クラスと平均STの偏り (N=10^6)")

    k = 6
    for mod in [3, 8, 9, 16, 27, 32, 64]:
        st_by_mod = {}
        for n, st in all_data[k]:
            r = n % mod
            if r not in st_by_mod:
                st_by_mod[r] = []
            st_by_mod[r].append(st)

        overall_mean = statistics.mean([st for _, st in all_data[k]])
        # 最も高い/低い残基クラス
        means = {r: statistics.mean(vals) for r, vals in st_by_mod.items() if len(vals) >= 10}
        if means:
            best_r = max(means, key=means.get)
            worst_r = min(means, key=means.get)
            print(f"  mod {mod:2d}: overall={overall_mean:.2f}, "
                  f"max_r={best_r}(mean={means[best_r]:.2f}), "
                  f"min_r={worst_r}(mean={means[worst_r]:.2f}), "
                  f"spread={means[best_r]-means[worst_r]:.2f}")

    # ==============================
    # Phase G: max ST vs N のスケーリング
    # ==============================
    print("\n[Phase G] max(ST) vs N のスケーリング")

    for k in sorted(all_data.keys()):
        N = 10**k
        max_st = max(st for _, st in all_data[k])
        logN = math.log(N)
        ratio1 = max_st / logN
        ratio2 = max_st / logN**2
        print(f"  k={k}: max_ST={max_st}, ST/logN={ratio1:.4f}, ST/logN²={ratio2:.6f}")

    # max_st vs logN のフィット
    log_maxst = [(math.log(math.log(10**k)), math.log(max(st for _, st in all_data[k]))) for k in sorted(all_data.keys())]
    xs = [x for x, _ in log_maxst]
    ys = [y for _, y in log_maxst]
    n_f = len(xs)
    sx = sum(xs); sy = sum(ys); sxy = sum(x*y for x,y in zip(xs,ys)); sx2 = sum(x*x for x in xs)
    denom = n_f*sx2 - sx*sx
    if denom != 0:
        b = (n_f*sxy - sx*sy)/denom
        a = (sy - b*sx)/n_f
        print(f"\n  フィット: log(max_ST) = {a:.4f} + {b:.4f}*log(logN)")
        print(f"  → max_ST ~ (logN)^{b:.3f}")

    elapsed = time.time() - t0
    print(f"\n計算時間: {elapsed:.1f}秒")

if __name__ == "__main__":
    main()
