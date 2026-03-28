#!/usr/bin/env python3
"""
探索: stopping time が異常に長い数の密度と数論的特徴

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} を用いて stopping time を計算し、
N=10^k (k=3..7) の範囲で stopping time > C*log(N)^2 となる n の密度を調べる。
尾部分布の形状と、異常に遅い到達の数論的特徴を分析する。
"""

import math
import time
from collections import defaultdict, Counter
import json

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)}"""
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n

def stopping_time(n):
    """n が n 未満の値に初めて到達するまでのステップ数 (Syracuse関数ベース)"""
    original = n
    steps = 0
    current = n
    while current >= original:
        if current == 1 and original != 1:
            return steps
        current = syracuse(current)
        steps += 1
        if steps > 10000:
            return steps  # 安全弁
    return steps

def total_stopping_time(n):
    """n が 1 に到達するまでの総ステップ数 (Syracuse関数ベース)"""
    steps = 0
    current = n
    while current != 1:
        current = syracuse(current)
        steps += 1
        if steps > 100000:
            return steps
    return steps

def analyze_range(N, use_total=True):
    """[1, N] の奇数について stopping time を計算"""
    func = total_stopping_time if use_total else stopping_time
    results = {}
    for n in range(1, N + 1, 2):  # 奇数のみ
        results[n] = func(n)
    return results

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def trailing_ones(n):
    """末尾の連続1ビット数"""
    count = 0
    while n & 1:
        n >>= 1
        count += 1
    return count

def is_form_2a3b_minus1(n, max_a=50, max_b=30):
    """n が 2^a * 3^b - 1 の形かチェック"""
    for b in range(max_b + 1):
        val = n + 1
        pow3 = 3 ** b
        if val % pow3 != 0:
            continue
        rem = val // pow3
        if rem > 0 and (rem & (rem - 1)) == 0:  # 2の冪チェック
            a = rem.bit_length() - 1
            return True, a, b
    return False, 0, 0

def main():
    print("=" * 70)
    print("探索: Stopping Time の異常値密度と数論的特徴")
    print("=" * 70)

    t0 = time.time()

    # ==============================
    # Phase 1: 各スケールでの密度計算
    # ==============================
    print("\n[Phase 1] 各スケール N=10^k での stopping time 分布")

    C_values = [1.0, 1.5, 2.0, 2.5, 3.0]
    density_results = {}

    for k in range(3, 8):
        N = 10 ** k
        print(f"\n--- N = 10^{k} = {N} ---")

        count_odd = N // 2  # おおよその奇数の数
        logN = math.log(N)
        logN2 = logN ** 2

        # stopping time 統計
        st_values = []
        for n in range(1, N + 1, 2):
            st = total_stopping_time(n)
            st_values.append((n, st))

        all_st = [s for _, s in st_values]
        mean_st = sum(all_st) / len(all_st)
        max_st = max(all_st)
        max_n = [n for n, s in st_values if s == max_st][0]

        # 各閾値での密度
        densities = {}
        for C in C_values:
            threshold = C * logN2
            exceed_count = sum(1 for s in all_st if s > threshold)
            density = exceed_count / len(all_st)
            densities[C] = (threshold, exceed_count, density)

        density_results[k] = {
            'N': N,
            'count_odd': len(all_st),
            'mean_st': mean_st,
            'max_st': max_st,
            'max_n': max_n,
            'logN': logN,
            'logN2': logN2,
            'densities': densities,
            'all_st': all_st,
            'st_values': st_values,
        }

        print(f"  奇数の数: {len(all_st)}")
        print(f"  平均 stopping time: {mean_st:.2f}")
        print(f"  最大 stopping time: {max_st} (n={max_n})")
        print(f"  log(N) = {logN:.3f}, log(N)^2 = {logN2:.3f}")
        for C in C_values:
            thr, cnt, dens = densities[C]
            print(f"  C={C}: threshold={thr:.1f}, count={cnt}, density={dens:.6f}")

        if time.time() - t0 > 600:  # 10分超えたら打ち切り
            print("時間制限に近づいたため打ち切り")
            break

    # ==============================
    # Phase 2: 尾部分布の形状分析
    # ==============================
    print("\n" + "=" * 70)
    print("[Phase 2] 尾部分布の形状分析")

    # 最大スケールのデータで分析
    max_k = max(density_results.keys())
    data = density_results[max_k]
    all_st = data['all_st']
    N = data['N']
    logN = data['logN']

    # 累積分布 P(ST > t) を計算
    sorted_st = sorted(all_st)
    total = len(sorted_st)

    # パーセンタイルでの stopping time
    percentiles = [50, 75, 90, 95, 99, 99.5, 99.9, 99.95, 99.99]
    print(f"\nN=10^{max_k} でのパーセンタイル:")
    for p in percentiles:
        idx = min(int(total * p / 100), total - 1)
        print(f"  {p}%ile: ST = {sorted_st[idx]}")

    # log-log でべき乗則チェック
    # P(ST > t) vs t の両対数プロット用データ
    print("\n尾部 P(ST > t):")
    tail_data = []
    for t_val in range(int(data['mean_st']), data['max_st'] + 1, max(1, (data['max_st'] - int(data['mean_st'])) // 30)):
        count_exceed = sum(1 for s in all_st if s > t_val)
        if count_exceed > 0:
            prob = count_exceed / total
            tail_data.append((t_val, count_exceed, prob))

    # べき乗則フィット: log P(ST > t) ~ -alpha * log(t) + const
    if len(tail_data) > 5:
        # 上位25%のtail_dataでフィット
        fit_data = tail_data[len(tail_data)//2:]
        if len(fit_data) >= 3:
            log_t = [math.log(d[0]) for d in fit_data if d[0] > 0 and d[2] > 0]
            log_p = [math.log(d[2]) for d in fit_data if d[0] > 0 and d[2] > 0]
            if len(log_t) >= 3:
                # 最小二乗法
                n_fit = len(log_t)
                sum_x = sum(log_t)
                sum_y = sum(log_p)
                sum_xy = sum(x*y for x, y in zip(log_t, log_p))
                sum_x2 = sum(x*x for x in log_t)
                denom = n_fit * sum_x2 - sum_x ** 2
                if denom != 0:
                    alpha = -(n_fit * sum_xy - sum_x * sum_y) / denom
                    intercept = (sum_y + alpha * sum_x) / n_fit
                    print(f"\nべき乗則フィット: P(ST > t) ~ t^(-{alpha:.3f})")
                    print(f"  (上位尾部でのフィット)")

    # 指数関数フィット: log P(ST > t) ~ -beta * t + const
    if len(tail_data) > 5:
        fit_data = tail_data[len(tail_data)//2:]
        t_vals = [d[0] for d in fit_data if d[2] > 0]
        log_p_vals = [math.log(d[2]) for d in fit_data if d[2] > 0]
        if len(t_vals) >= 3:
            n_fit = len(t_vals)
            sum_x = sum(t_vals)
            sum_y = sum(log_p_vals)
            sum_xy = sum(x*y for x, y in zip(t_vals, log_p_vals))
            sum_x2 = sum(x*x for x in t_vals)
            denom = n_fit * sum_x2 - sum_x ** 2
            if denom != 0:
                beta = -(n_fit * sum_xy - sum_x * sum_y) / denom
                intercept = (sum_y + beta * sum_x) / n_fit
                print(f"指数関数フィット: P(ST > t) ~ exp(-{beta:.6f} * t)")

    # ==============================
    # Phase 3: 密度のスケーリング分析
    # ==============================
    print("\n" + "=" * 70)
    print("[Phase 3] 密度のスケーリング則")

    # 各Cでの密度がNとともにどう減衰するか
    for C in C_values:
        print(f"\nC = {C}:")
        prev_density = None
        for k in sorted(density_results.keys()):
            thr, cnt, dens = density_results[k]['densities'][C]
            ratio = ""
            if prev_density and prev_density > 0 and dens > 0:
                ratio = f"  ratio={prev_density/dens:.3f}"
                log_ratio = math.log(prev_density / dens) / math.log(10) if prev_density > 0 and dens > 0 else 0
                ratio += f"  log10(ratio)={log_ratio:.3f}"
            prev_density = dens
            print(f"  k={k}: density={dens:.8f}, count={cnt}{ratio}")

    # ==============================
    # Phase 4: 異常値の数論的特徴
    # ==============================
    print("\n" + "=" * 70)
    print("[Phase 4] Stopping time 上位の数論的特徴")

    # k=5 (N=10^5) のデータで上位分析
    analysis_k = min(6, max_k)
    data_an = density_results[analysis_k]
    st_values = data_an['st_values']

    # 上位1%を取得
    threshold_99 = sorted([s for _, s in st_values])[int(len(st_values) * 0.99)]
    top_entries = [(n, s) for n, s in st_values if s >= threshold_99]
    top_entries.sort(key=lambda x: -x[1])

    print(f"\nN=10^{analysis_k} での上位1% (ST >= {threshold_99}):")
    print(f"  該当数: {len(top_entries)}")

    # 末尾1ビット分析
    trailing_ones_top = [trailing_ones(n) for n, _ in top_entries]
    trailing_ones_all = [trailing_ones(n) for n, _ in st_values]

    top_trail_counter = Counter(trailing_ones_top)
    all_trail_counter = Counter(trailing_ones_all)

    print("\n  末尾連続1ビット分布 (上位1% vs 全体):")
    for bits in sorted(set(list(top_trail_counter.keys()) + list(all_trail_counter.keys()))):
        top_frac = top_trail_counter.get(bits, 0) / len(top_entries) if len(top_entries) > 0 else 0
        all_frac = all_trail_counter.get(bits, 0) / len(st_values) if len(st_values) > 0 else 0
        if top_frac > 0 or all_frac > 0.01:
            ratio = top_frac / all_frac if all_frac > 0 else float('inf')
            print(f"    {bits}ビット: 上位={top_frac:.4f}, 全体={all_frac:.4f}, 濃縮比={ratio:.2f}")

    # mod 小さい素数での分布
    print("\n  mod p での分布 (上位1% vs 全体):")
    for p in [3, 5, 7, 9, 11, 13, 16, 27, 32]:
        top_mod = Counter(n % p for n, _ in top_entries)
        all_mod = Counter(n % p for n, _ in st_values)
        # chi-squared的な偏り
        max_enrichment = 0
        max_res = -1
        for r in range(p):
            top_frac = top_mod.get(r, 0) / len(top_entries)
            all_frac = all_mod.get(r, 0) / len(st_values)
            if all_frac > 0:
                enrichment = top_frac / all_frac
                if enrichment > max_enrichment:
                    max_enrichment = enrichment
                    max_res = r
        if max_enrichment > 1.3:
            print(f"    mod {p}: 最大濃縮 r={max_res}, ratio={max_enrichment:.3f}")

    # 2^a * 3^b - 1 形式チェック
    form_count = 0
    near_form_count = 0
    for n, s in top_entries[:100]:
        is_form, a, b = is_form_2a3b_minus1(n)
        if is_form:
            form_count += 1
            if s >= threshold_99 * 1.1:
                print(f"    2^{a}*3^{b}-1 = {n}, ST={s}")

    print(f"\n  上位100件中 2^a*3^b-1 形式: {form_count}")

    # ==============================
    # Phase 5: stopping time / log(n) の比率分析
    # ==============================
    print("\n" + "=" * 70)
    print("[Phase 5] ST/log(n) 比率の分布")

    for k in sorted(density_results.keys()):
        data_k = density_results[k]
        ratios = []
        for n, s in data_k['st_values']:
            if n > 1:
                ratios.append(s / math.log(n))

        mean_ratio = sum(ratios) / len(ratios)
        max_ratio = max(ratios)
        # 標準偏差
        var_ratio = sum((r - mean_ratio)**2 for r in ratios) / len(ratios)
        std_ratio = math.sqrt(var_ratio)

        print(f"  k={k}: mean={mean_ratio:.4f}, std={std_ratio:.4f}, max={max_ratio:.4f}, max/mean={max_ratio/mean_ratio:.2f}")

    # ==============================
    # Phase 6: 超対数尾部の判定
    # ==============================
    print("\n" + "=" * 70)
    print("[Phase 6] 超対数尾部の判定")

    # density(C, k) が k→∞ で多項式的に減衰するか指数的に減衰するかを判定
    # C=1.5 での密度を使う
    C_test = 1.5
    ks = sorted(density_results.keys())
    densities_for_fit = []
    for k in ks:
        _, _, dens = density_results[k]['densities'][C_test]
        if dens > 0:
            densities_for_fit.append((k, dens))

    if len(densities_for_fit) >= 3:
        # log(density) vs k のフィット（指数的減衰なら線形）
        log_dens = [(k, math.log(d)) for k, d in densities_for_fit]
        n_fit = len(log_dens)
        sum_x = sum(k for k, _ in log_dens)
        sum_y = sum(y for _, y in log_dens)
        sum_xy = sum(k*y for k, y in log_dens)
        sum_x2 = sum(k*k for k, _ in log_dens)
        denom = n_fit * sum_x2 - sum_x ** 2
        if denom != 0:
            slope = (n_fit * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n_fit
            print(f"\n  C={C_test}: log(density) ~ {slope:.4f} * k + {intercept:.4f}")
            print(f"  → 密度はおおよそ 10^({slope/math.log(10):.3f} * k) で減衰")

            # 残差
            for k, d in densities_for_fit:
                predicted = math.exp(slope * k + intercept)
                print(f"    k={k}: actual={d:.8f}, predicted={predicted:.8f}, ratio={d/predicted:.3f}")

        # log(density) vs log(k) のフィット（べき乗的減衰なら線形）
        log_log_dens = [(math.log(k), math.log(d)) for k, d in densities_for_fit]
        n_fit = len(log_log_dens)
        sum_x = sum(x for x, _ in log_log_dens)
        sum_y = sum(y for _, y in log_log_dens)
        sum_xy = sum(x*y for x, y in log_log_dens)
        sum_x2 = sum(x*x for x in (x for x, _ in log_log_dens))
        denom = n_fit * sum_x2 - sum_x ** 2
        if denom != 0:
            slope2 = (n_fit * sum_xy - sum_x * sum_y) / denom
            intercept2 = (sum_y - slope2 * sum_x) / n_fit
            print(f"\n  べき乗フィット: log(density) ~ {slope2:.4f} * log(k)")
            print(f"  → 密度はおおよそ k^({slope2:.2f}) で減衰")

    # ==============================
    # まとめ
    # ==============================
    elapsed = time.time() - t0
    print(f"\n{'='*70}")
    print(f"計算時間: {elapsed:.1f}秒")
    print("=" * 70)

    # Top 20 の異常値
    print("\n[付録] 各スケールでの最大 stopping time の数:")
    for k in sorted(density_results.keys()):
        d = density_results[k]
        st_sorted = sorted(d['st_values'], key=lambda x: -x[1])[:5]
        print(f"  k={k}:")
        for n, s in st_sorted:
            bin_repr = bin(n)
            trail = trailing_ones(n)
            print(f"    n={n} (0b...{bin_repr[-min(16,len(bin_repr)-2):]}), ST={s}, trail_1s={trail}")

if __name__ == "__main__":
    main()
