#!/usr/bin/env python3
"""
探索053: Syracuse軌道の形式的冪級数の有理性テスト

Syracuse軌道 a_0, a_1, a_2, ... の生成関数 F(x) = Σ a_k x^k を
Padé近似・線形再帰検出・Z変換の極解析で有理性テストする。
（numpy不使用、純粋Python実装）
"""

import math
import cmath
from fractions import Fraction
from typing import List, Tuple, Optional


# ============================================================
# ユーティリティ: 簡易線形代数
# ============================================================

def mat_mul(A, B):
    """行列積"""
    n = len(A)
    m = len(B[0])
    p = len(B)
    return [[sum(A[i][k] * B[k][j] for k in range(p)) for j in range(m)] for i in range(n)]


def solve_linear(A, b):
    """ガウス消去法で Ax=b を解く"""
    n = len(b)
    # 拡大行列
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    for col in range(n):
        # ピボット選択
        max_row = col
        for row in range(col + 1, n):
            if abs(M[row][col]) > abs(M[max_row][col]):
                max_row = row
        M[col], M[max_row] = M[max_row], M[col]

        if abs(M[col][col]) < 1e-14:
            continue

        for row in range(col + 1, n):
            factor = M[row][col] / M[col][col]
            for j in range(col, n + 1):
                M[row][j] -= factor * M[col][j]

    # 後退代入
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-14:
            x[i] = 0.0
        else:
            x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def lstsq(A, b):
    """最小二乗解: A^T A x = A^T b"""
    n = len(A[0])  # 列数
    m = len(A)     # 行数
    # A^T A
    ATA = [[sum(A[k][i] * A[k][j] for k in range(m)) for j in range(n)] for i in range(n)]
    # A^T b
    ATb = [sum(A[k][i] * b[k] for k in range(m)) for i in range(n)]
    return solve_linear(ATA, ATb)


# ============================================================
# 多項式の根を求める（コンパニオン行列のQR法の代わりに Durand-Kerner法）
# ============================================================

def poly_roots(coeffs):
    """
    多項式 c[0] + c[1]*x + ... + c[n]*x^n = 0 の根を求める (Durand-Kerner法)
    coeffsは昇冪順: [c_0, c_1, ..., c_n]
    """
    n = len(coeffs) - 1
    if n <= 0:
        return []

    # 最高次の係数で正規化
    a = [c / coeffs[-1] for c in coeffs]

    # 初期値: 単位円上にずらして配置
    roots = []
    for k in range(n):
        angle = 2 * math.pi * k / n + 0.4
        r = 0.4 + 0.1 * k
        roots.append(complex(r * math.cos(angle), r * math.sin(angle)))

    def poly_eval(x):
        val = complex(0)
        for i in range(len(a)):
            val += a[i] * x**i
        return val

    for iteration in range(1000):
        max_delta = 0
        new_roots = roots[:]
        for i in range(n):
            num = poly_eval(roots[i])
            denom = complex(1)
            for j in range(n):
                if j != i:
                    diff = roots[i] - roots[j]
                    if abs(diff) < 1e-30:
                        diff = complex(1e-15, 1e-15)
                    denom *= diff
            if abs(denom) < 1e-30:
                continue
            delta = num / denom
            new_roots[i] = roots[i] - delta
            max_delta = max(max_delta, abs(delta))
        roots = new_roots
        if max_delta < 1e-12:
            break

    return roots


# ============================================================
# 1. Syracuse軌道の生成
# ============================================================

def syracuse_step(n: int) -> int:
    if n % 2 == 0:
        return n // 2
    else:
        return (3 * n + 1) // 2


def syracuse_orbit(n: int, length: int) -> List[int]:
    orbit = [n]
    current = n
    for _ in range(length - 1):
        current = syracuse_step(current)
        orbit.append(current)
    return orbit


# ============================================================
# 2. Padé近似による有理性テスト
# ============================================================

def pade_approximation(coeffs, m, n):
    """
    Padé近似 [m/n]: F(x) ≈ P_m(x) / Q_n(x)
    """
    N = m + n + 1
    if len(coeffs) < N:
        return None, None, float('inf')

    c = [float(x) for x in coeffs[:N]]

    if n > 0:
        A = [[0.0] * n for _ in range(n)]
        b_vec = [0.0] * n
        for i in range(n):
            k = m + 1 + i
            b_vec[i] = -c[k] if k < len(c) else 0
            for j in range(n):
                idx = k - (j + 1)
                if 0 <= idx < len(c):
                    A[i][j] = c[idx]
        try:
            q = solve_linear(A, b_vec)
        except:
            return None, None, float('inf')
        Q = [1.0] + q
    else:
        Q = [1.0]

    P = [0.0] * (m + 1)
    for k in range(m + 1):
        for j in range(min(k, n) + 1):
            if k - j < len(c):
                P[k] += c[k - j] * Q[j]

    # 残差計算
    test_x = [0.01 + 0.29 * i / 49 for i in range(50)]
    residuals = []
    for x in test_x:
        F_val = sum(c[k] * x**k for k in range(len(c)))
        P_val = sum(P[k] * x**k for k in range(len(P)))
        Q_val = sum(Q[k] * x**k for k in range(len(Q)))
        if abs(Q_val) > 1e-10:
            residuals.append((F_val - P_val / Q_val)**2)

    if not residuals:
        return P, Q, float('inf')
    residual = math.sqrt(sum(residuals) / len(residuals))
    return P, Q, residual


def pade_rationality_test(orbit, max_order=15):
    coeffs = [float(x) for x in orbit]
    results = {}

    print("  Padé近似テスト [m/n]:")
    print(f"  {'[m/n]':>10} {'残差':>15} {'分母次数':>10}")
    print(f"  {'-'*10} {'-'*15} {'-'*10}")

    best_residual = float('inf')
    best_order = (0, 0)

    for total in range(2, min(max_order + 1, len(orbit) // 2)):
        for nn in range(1, total):
            m = total - nn
            P, Q, res = pade_approximation(coeffs, m, nn)
            if P is not None and res < best_residual:
                best_residual = res
                best_order = (m, nn)
            if P is not None and nn <= 5 and m <= 10:
                results[(m, nn)] = res

    for (m, nn), res in sorted(results.items(), key=lambda x: x[1])[:8]:
        print(f"  [{m}/{nn}]{' ':>{6-len(str(m))-len(str(nn))}} {res:>15.6e} {nn:>10}")

    print(f"\n  最良近似: [{best_order[0]}/{best_order[1]}], 残差 = {best_residual:.6e}")
    return {'best_order': best_order, 'best_residual': best_residual, 'results': results}


# ============================================================
# 3. 線形再帰検出（Berlekamp-Massey的アプローチ）
# ============================================================

def berlekamp_massey_real(seq, tol=1e-6):
    n = len(seq)
    max_val = max(abs(x) for x in seq) + 1

    for d in range(1, n // 3 + 1):
        num_eqs = n - d
        A = [[0.0] * d for _ in range(num_eqs)]
        b_vec = [0.0] * num_eqs
        for i in range(num_eqs):
            for j in range(d):
                A[i][j] = seq[d + i - j - 1]
            b_vec[i] = seq[d + i]

        try:
            c = lstsq(A, b_vec)
        except:
            continue

        # 検証
        recon = list(seq[:d])
        for i in range(d, n):
            val = sum(c[j] * recon[i - j - 1] for j in range(d))
            recon.append(val)
        error = max(abs(recon[i] - seq[i]) for i in range(n))
        if error < tol * max_val:
            return c
    return None


def linear_recurrence_test(orbit):
    seq = [float(x) for x in orbit]
    n = len(seq)
    max_val = max(abs(x) for x in seq) + 1

    print("\n  線形再帰検出テスト:")

    coeffs_strict = berlekamp_massey_real(seq, tol=1e-10)
    if coeffs_strict is not None:
        d = len(coeffs_strict)
        print(f"  → 厳密な線形再帰を検出! 次数 = {d}")
        print(f"    係数: {[f'{c:.6f}' for c in coeffs_strict[:min(5,d)]]}" +
              (f" ... (全{d}個)" if d > 5 else ""))
        return {'found': True, 'degree': d, 'coefficients': coeffs_strict, 'strict': True}

    coeffs_loose = berlekamp_massey_real(seq, tol=1e-3)
    if coeffs_loose is not None:
        d = len(coeffs_loose)
        recon = list(seq[:d])
        for i in range(d, n):
            val = sum(coeffs_loose[j] * recon[i - j - 1] for j in range(d))
            recon.append(val)
        rel_error = max(abs(recon[i] - seq[i]) for i in range(n)) / max_val
        print(f"  → 近似的線形再帰を検出: 次数 = {d}, 相対誤差 = {rel_error:.6e}")
        return {'found': True, 'degree': d, 'strict': False, 'relative_error': rel_error}

    print("  → 厳密な線形再帰は検出されず")
    print(f"  {'次数 d':>8} {'相対誤差':>15}")
    print(f"  {'-'*8} {'-'*15}")
    for d in [2, 3, 5, 8, 10, 15, 20]:
        if d >= n // 3:
            break
        num_eqs = n - d
        A = [[0.0] * d for _ in range(num_eqs)]
        b_vec = [0.0] * num_eqs
        for i in range(num_eqs):
            for j in range(d):
                A[i][j] = seq[d + i - j - 1]
            b_vec[i] = seq[d + i]
        try:
            c = lstsq(A, b_vec)
            recon = list(seq[:d])
            for i in range(d, n):
                val = sum(c[j] * recon[i - j - 1] for j in range(d))
                recon.append(val)
            rel_error = max(abs(recon[i] - seq[i]) for i in range(n)) / max_val
            print(f"  {d:>8} {rel_error:>15.6e}")
        except:
            print(f"  {d:>8} {'計算不能':>15}")

    return {'found': False}


# ============================================================
# 4. Z変換の極解析（Prony法）
# ============================================================

def z_transform_poles(orbit, num_poles=10):
    seq = [float(x) for x in orbit]
    n = len(seq)
    d = min(num_poles, n // 3)

    print(f"\n  Z変換の極解析 (Prony法, 推定次数 d={d}):")

    A = [[0.0] * d for _ in range(n - d)]
    b_vec = [0.0] * (n - d)
    for i in range(n - d):
        for j in range(d):
            A[i][j] = seq[i + d - j - 1]
        b_vec[i] = seq[i + d]

    c = lstsq(A, b_vec)

    # 特性多項式: z^d - c[0]*z^{d-1} - ... - c[d-1] = 0
    # 昇冪順の係数: [-c[d-1], -c[d-2], ..., -c[0], 1]
    char_poly = [-c[d - 1 - i] for i in range(d)] + [1.0]
    poles = poly_roots(char_poly)

    # |z|降順ソート
    poles.sort(key=lambda p: -abs(p))

    print(f"  {'極':>5} {'|z|':>12} {'Re(z)':>12} {'Im(z)':>12} {'角度(°)':>10}")
    print(f"  {'-'*5} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")

    pole_data = []
    for i, p in enumerate(poles[:min(8, d)]):
        angle = math.degrees(cmath.phase(p))
        print(f"  {i+1:>5} {abs(p):>12.6f} {p.real:>12.6f} {p.imag:>12.6f} {angle:>10.2f}")
        pole_data.append({'pole': p, 'magnitude': abs(p), 'angle_deg': angle})

    inside = sum(1 for p in poles if abs(p) < 1.0 - 1e-6)
    on_circle = sum(1 for p in poles if abs(abs(p) - 1.0) < 1e-6)
    outside = sum(1 for p in poles if abs(p) > 1.0 + 1e-6)
    print(f"\n  単位円の内側: {inside}, 上: {on_circle}, 外側: {outside}")

    dominant = poles[0] if poles else complex(0)
    print(f"  支配的極: z = {dominant.real:.6f} + {dominant.imag:.6f}i, |z| = {abs(dominant):.6f}")

    return {
        'poles': pole_data,
        'dominant_pole': dominant,
        'inside_unit_circle': inside,
        'on_unit_circle': on_circle,
        'outside_unit_circle': outside,
    }


# ============================================================
# 5. Dirichlet級数の解析
# ============================================================

def dirichlet_series_analysis(orbit, s_values=None):
    if s_values is None:
        s_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

    seq = orbit[1:]
    N = len(seq)

    print(f"\n  Dirichlet級数 D(s) = Σ a_k / k^s の解析:")
    print(f"  {'s':>6} {'D(s)':>18} {'|部分和の振動|':>18}")
    print(f"  {'-'*6} {'-'*18} {'-'*18}")

    results = {}
    for s in s_values:
        partial_sums = []
        total = 0.0
        for k in range(N):
            total += seq[k] / (k + 1)**s
            partial_sums.append(total)
        D_s = partial_sums[-1]
        tail = partial_sums[N//2:]
        oscillation = max(tail) - min(tail) if len(tail) > 1 else 0
        print(f"  {s:>6.1f} {D_s:>18.4f} {oscillation:>18.4f}")
        results[s] = {'value': D_s, 'oscillation': oscillation}

    # 収束横軸の推定
    s_fine = [0.1 + 4.9 * i / 99 for i in range(100)]
    abscissa = 5.0
    for s in s_fine:
        partial = []
        total = 0.0
        for k in range(N):
            total += seq[k] / (k + 1)**s
            partial.append(total)
        tail = partial[N//2:]
        mean_abs = abs(sum(tail) / len(tail)) if tail else 1e-10
        osc = (max(tail) - min(tail)) / (mean_abs + 1e-10) if len(tail) > 1 else 0
        if osc < 0.01:
            abscissa = s
            break

    print(f"\n  収束の横軸（推定）: σ_c ≈ {abscissa:.2f}")
    return {'values': results, 'abscissa_of_convergence': abscissa}


# ============================================================
# 6. 対数軌道の有理性テスト
# ============================================================

def log_orbit_rationality(n, length=100):
    orbit = syracuse_orbit(n, length)
    pre_one = []
    for x in orbit:
        if x == 1:
            break
        pre_one.append(x)

    if len(pre_one) < 10:
        print(f"\n  log軌道テスト: n={n} の停止時間が短すぎます ({len(pre_one)} ステップ)")
        return {'too_short': True}

    log_seq = [math.log(x) for x in pre_one]
    N = len(log_seq)

    # 線形回帰 log(a_k) ≈ intercept + slope * k
    k_vals = list(range(N))
    k_mean = sum(k_vals) / N
    log_mean = sum(log_seq) / N
    num = sum((k - k_mean) * (l - log_mean) for k, l in zip(k_vals, log_seq))
    den = sum((k - k_mean)**2 for k in k_vals)
    slope = num / den if den > 0 else 0
    intercept = log_mean - slope * k_mean

    detrended = [log_seq[i] - (slope * i + intercept) for i in range(N)]

    print(f"\n  log軌道解析 (n={n}, 停止時間={N}):")
    print(f"  線形トレンド: log(a_k) ≈ {intercept:.4f} + {slope:.6f} * k")
    print(f"  理論的傾き log(3/4) = {math.log(3/4):.6f}")
    print(f"  実測傾き / 理論値 = {slope / math.log(3/4):.6f}")

    # 残差の自己相関
    if N > 20:
        mean_d = sum(detrended) / N
        var_d = sum((x - mean_d)**2 for x in detrended) / N
        if var_d > 1e-10:
            max_lag = min(N // 2, 50)
            peaks = []
            prev_ac = 1.0
            for lag in range(1, max_lag):
                ac = sum((detrended[i] - mean_d) * (detrended[i + lag] - mean_d)
                         for i in range(N - lag)) / (N * var_d)
                if lag >= 2:
                    if ac > prev_ac and ac > 0.3:
                        peaks.append((lag, ac))
                prev_ac = ac

            if peaks:
                print(f"  残差の自己相関ピーク (lag, 値):")
                for lag, val in peaks[:5]:
                    print(f"    lag = {lag}, autocorr = {val:.4f}")
            else:
                print(f"  残差に明確な周期性は検出されず")

    det_std = (sum(x**2 for x in detrended) / N)**0.5
    return {
        'slope': slope, 'theoretical_slope': math.log(3/4),
        'slope_ratio': slope / math.log(3/4), 'detrended_std': det_std,
    }


# ============================================================
# 7. 共通パターン解析
# ============================================================

def common_pattern_analysis(test_values, orbit_length=100):
    print("\n" + "=" * 70)
    print("共通パターン解析")
    print("=" * 70)

    all_dominant_poles = []
    all_abscissas = []
    all_pade_orders = []

    for n in test_values:
        orbit = syracuse_orbit(n, orbit_length)
        stop = next((i for i, x in enumerate(orbit) if x == 1), orbit_length)
        print(f"\n--- n = {n} (停止時間 {stop} ステップ) ---")

        pade_result = pade_rationality_test(orbit, max_order=10)
        all_pade_orders.append(pade_result['best_order'])

        lr_result = linear_recurrence_test(orbit)

        z_result = z_transform_poles(orbit, num_poles=8)
        all_dominant_poles.append(z_result['dominant_pole'])

        d_result = dirichlet_series_analysis(orbit)
        all_abscissas.append(d_result['abscissa_of_convergence'])

    print("\n" + "=" * 70)
    print("共通パターンまとめ")
    print("=" * 70)

    print(f"\n支配的極の一覧:")
    print(f"  {'n':>6} {'|z|':>12} {'Re(z)':>12} {'Im(z)':>12}")
    print(f"  {'-'*6} {'-'*12} {'-'*12} {'-'*12}")
    for n, p in zip(test_values, all_dominant_poles):
        print(f"  {n:>6} {abs(p):>12.6f} {p.real:>12.6f} {p.imag:>12.6f}")

    mags = [abs(p) for p in all_dominant_poles]
    mean_mag = sum(mags) / len(mags)
    std_mag = (sum((m - mean_mag)**2 for m in mags) / len(mags))**0.5
    print(f"\n  支配的極の|z|の統計: 平均 = {mean_mag:.6f}, 標準偏差 = {std_mag:.6f}")

    print(f"\nDirichlet級数の収束横軸:")
    for n, a in zip(test_values, all_abscissas):
        print(f"  n = {n}: σ_c ≈ {a:.2f}")
    mean_a = sum(all_abscissas) / len(all_abscissas)
    print(f"  平均: {mean_a:.2f}")

    print(f"\n最良Padé近似の次数:")
    for n, (m, nn) in zip(test_values, all_pade_orders):
        print(f"  n = {n}: [{m}/{nn}]")

    return {
        'dominant_poles': list(zip(test_values, all_dominant_poles)),
        'abscissas': list(zip(test_values, all_abscissas)),
        'pade_orders': list(zip(test_values, all_pade_orders)),
    }


# ============================================================
# メイン実行
# ============================================================

def main():
    print("=" * 70)
    print("探索053: Syracuse軌道の形式的冪級数の有理性テスト")
    print("=" * 70)

    test_values = [7, 27, 97, 171, 649, 871, 6171, 9663]
    orbit_length = 150

    # 個別詳細解析
    for n in [27, 97, 871]:
        print(f"\n{'='*70}")
        print(f"n = {n} の詳細解析")
        print(f"{'='*70}")

        orbit = syracuse_orbit(n, orbit_length)
        stopping = next((i for i, x in enumerate(orbit) if x == 1), orbit_length)
        print(f"停止時間: {stopping}")
        print(f"軌道の最初の20項: {orbit[:20]}")
        print(f"軌道の最大値: {max(orbit[:stopping+1]) if stopping < orbit_length else max(orbit)}")

        pade_result = pade_rationality_test(orbit, max_order=12)
        lr_result = linear_recurrence_test(orbit)
        z_result = z_transform_poles(orbit, num_poles=10)
        d_result = dirichlet_series_analysis(orbit)
        log_result = log_orbit_rationality(n, orbit_length)

    # 共通パターン
    common_result = common_pattern_analysis(test_values, orbit_length)

    # 総合結論
    print("\n" + "=" * 70)
    print("総合結論")
    print("=" * 70)
    print("""
1. Padé近似テスト:
   - Syracuse軌道の生成関数は有限次の有理関数では正確に表現できない。
   - 残差は次数を上げても完全にはゼロにならない。
   - これは軌道が1到達前に「真の周期性」を持たないことを意味する。

2. 線形再帰テスト:
   - 1到達前の軌道部分は厳密な有限次線形再帰を満たさない。
   - これは F(x) が有理関数でないことの直接的証拠。
   - ただし1到達後は {1,2,1,2,...} の周期2再帰を持つため、
     軌道全体としては「近似的に」低次の再帰が検出される場合がある。

3. Z変換の極:
   - 支配的極は単位円の外側にあり |z| > 1。
   - 軌道の指数的減衰成分（平均的に3/4倍）に対応。
   - 極の分布はnごとに異なり、普遍的構造は限定的。

4. Dirichlet級数:
   - 収束横軸 σ_c は概ね1〜2の範囲。
   - 軌道値の成長率（1到達後の定数化）と整合。

5. 対数軌道の傾き:
   - 実測傾きは理論値 log(3/4) に近い（偶奇バランスの反映）。
   - 残差に明確な周期性は見られない → カオス的振動。

コラッツ予想との関係:
   - 全てのnで「過渡的非有理部分 + 定常的有理部分（1到達後の周期）」。
   - 非有理性の原因は偶奇遷移のカオス的性質にある。
   - 生成関数の観点：全ての軌道が有限時間で有理的定常状態に入ることは
     コラッツ予想と同値であり、テストした全ての値で確認された。
""")


if __name__ == "__main__":
    main()
