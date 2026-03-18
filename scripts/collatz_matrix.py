#!/usr/bin/env python3
"""
Exploration 043: Syracuse ステップの SL(2,Z) 行列積表現

各Collatzステップを2x2行列で表現し、軌道全体を行列積として分析する。

上昇ステップ: n → (3n+1)/2  =>  M_u = [[3/2, 1/2], [0, 1]]
下降ステップ: n → n/2       =>  M_d = [[1/2, 0], [0, 1]]

ベクトル (n, 1)^T に左から行列を掛けると、変換後の (n', 1)^T が得られる。
軌道全体の行列積 P = M_k ... M_2 M_1 の性質を調べる。
"""

from fractions import Fraction
from collections import defaultdict
import math


# === 正確な有理数行列演算 ===

def mat_mul_exact(A, B):
    """2x2 有理数行列の積"""
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
    ]

def mat_id():
    """単位行列"""
    return [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]

M_u = [[Fraction(3,2), Fraction(1,2)], [Fraction(0), Fraction(1)]]  # 上昇
M_d = [[Fraction(1,2), Fraction(0)], [Fraction(0), Fraction(1)]]    # 下降


def collatz_orbit_matrices(n):
    """
    n (奇数) の Syracuse 軌道を行列積として追跡。
    戻り値: (行列リスト, ステップ種別リスト, 行列積, 軌道)
    """
    steps = []
    step_types = []
    orbit = [n]
    current = n

    while current != 1:
        if current % 2 == 0:
            current //= 2
            steps.append('d')
        else:
            current = 3 * current + 1
            # (3n+1) は必ず偶数なので次のステップで /2 される
            # ここでは Syracuse 形式: 上昇 = (3n+1)/2 をひとまとめに
            current //= 2
            steps.append('u')
        orbit.append(current)

        if len(orbit) > 10000:
            break

    # 行列積を計算（右から左に適用）
    product = mat_id()
    matrices = []
    for s in steps:
        M = M_u if s == 'u' else M_d
        matrices.append(M)
        product = mat_mul_exact(M, product)

    return matrices, steps, product, orbit


def analyze_product(product):
    """行列積の性質を分析"""
    a, b = float(product[0][0]), float(product[0][1])
    c, d = float(product[1][0]), float(product[1][1])

    det = a*d - b*c
    trace = a + d
    # 固有値: λ = (trace ± sqrt(trace^2 - 4*det)) / 2
    disc = trace**2 - 4*det
    if disc >= 0:
        ev1 = (trace + math.sqrt(disc)) / 2
        ev2 = (trace - math.sqrt(disc)) / 2
        eigenvalues = (ev1, ev2)
    else:
        real = trace / 2
        imag = math.sqrt(-disc) / 2
        eigenvalues = (complex(real, imag), complex(real, -imag))

    norm = math.sqrt(a**2 + b**2 + c**2 + d**2)

    return {
        'det': det,
        'trace': trace,
        'eigenvalues': eigenvalues,
        'norm': norm,
        'a00': a, 'a01': b, 'a10': c, 'a11': d
    }


def exact_det_trace(product):
    """正確な行列式とトレース"""
    det = product[0][0]*product[1][1] - product[0][1]*product[1][0]
    trace = product[0][0] + product[1][1]
    return det, trace


# === メイン分析 ===

print("=" * 70)
print("探索043: Syracuse ステップの SL(2,Z) 行列積表現")
print("=" * 70)

# --- 1. 基本行列の性質 ---
print("\n■ 1. 基本行列の性質")
print(f"  M_u (上昇) = [[3/2, 1/2], [0, 1]]")
print(f"    det(M_u) = {M_u[0][0]*M_u[1][1] - M_u[0][1]*M_u[1][0]}")
print(f"    tr(M_u)  = {M_u[0][0] + M_u[1][1]}")
print(f"    固有値: 3/2, 1")
print(f"  M_d (下降) = [[1/2, 0], [0, 1]]")
print(f"    det(M_d) = {M_d[0][0]*M_d[1][1] - M_d[0][1]*M_d[1][0]}")
print(f"    tr(M_d)  = {M_d[0][0] + M_d[1][1]}")
print(f"    固有値: 1/2, 1")

print(f"\n  M_u ∈ GL(2,Q), det = 3/2 > 0 (拡大)")
print(f"  M_d ∈ GL(2,Q), det = 1/2 < 1 (縮小)")
print(f"  両者とも上三角行列 → 積も上三角")

# --- 2. 行列積の構造 ---
print("\n■ 2. 行列積の一般的構造")
print("  M_u^a * M_d^b の場合:")
print("    det = (3/2)^a * (1/2)^b = 3^a / 2^(a+b)")
print("    (0,0)成分 = (3/2)^a * (1/2)^b = 3^a / 2^(a+b)")
print("    (1,1)成分 = 1 (常に)")
print("    → 1に到達 ⟺ P(n,1)^T = (1,1)^T")
print("    → P[0][0]*n + P[0][1] = 1")

# --- 3. 具体例の分析 ---
print("\n■ 3. 具体的な軌道の行列積分析")

test_values = [3, 7, 9, 15, 27, 31, 63, 97, 127, 255, 511, 703, 871, 6171]

results = []
for n in test_values:
    matrices, steps, product, orbit = collatz_orbit_matrices(n)
    det_exact, trace_exact = exact_det_trace(product)
    props = analyze_product(product)

    u_count = steps.count('u')
    d_count = steps.count('d')
    total = len(steps)

    results.append({
        'n': n,
        'steps': total,
        'u': u_count,
        'd': d_count,
        'ratio_d_u': d_count / u_count if u_count > 0 else float('inf'),
        'det_exact': det_exact,
        'product': product,
        'props': props,
        'step_seq': ''.join(steps),
    })

    print(f"\n  n = {n}: {total} ステップ (u={u_count}, d={d_count}, d/u={d_count/u_count:.4f})")
    print(f"    ステップ列: {''.join(steps)}")
    print(f"    det(P) = {det_exact} = 3^{u_count}/2^{u_count+d_count}")
    print(f"    P[0][0] = {product[0][0]}")
    print(f"    P[0][1] = {product[0][1]}")
    print(f"    検証: P[0][0]*{n} + P[0][1] = {product[0][0]*n + product[0][1]}")

# --- 4. 行列式の対数と d/u 比の関係 ---
print("\n\n■ 4. 行列式の対数と収束条件")
print("  det(P) = 3^u / 2^(u+d)")
print("  log2(det) = u*log2(3) - (u+d) = u*(log2(3)-1) - d")
print("  1に到達するには det(P) ≈ 1/n (直感的に)")
print()

for r in results:
    det_float = float(r['det_exact'])
    log2_det = math.log2(abs(det_float)) if det_float != 0 else float('-inf')
    log2_n = math.log2(r['n'])
    print(f"  n={r['n']:>5}: log2(det)={log2_det:>10.4f}, -log2(n)={-log2_n:>8.4f}, "
          f"差={log2_det + log2_n:>8.4f}, d/u={r['ratio_d_u']:.4f}")

# --- 5. P[0][1] の構造分析 ---
print("\n\n■ 5. 行列積の (0,1) 成分の構造")
print("  P[0][0]*n + P[0][1] = 1 なので P[0][1] = 1 - P[0][0]*n")
print("  P[0][0] = 3^u / 2^(u+d) = det(P)")
print()

for r in results:
    p00 = r['product'][0][0]
    p01 = r['product'][0][1]
    print(f"  n={r['n']:>5}: P[0][0]={str(p00):>20s}, P[0][1]={str(p01):>25s}")

# --- 6. 中間行列積のノルム推移 ---
print("\n\n■ 6. 中間行列積のノルム・行列式の推移 (n=27)")

n_example = 27
matrices, steps, product, orbit = collatz_orbit_matrices(n_example)

print(f"  n=27 の軌道長: {len(steps)} ステップ")
print(f"  ステップ列: {''.join(steps)}")
print()
print(f"  {'ステップ':>6} {'型':>2} {'det':>15} {'log2(det)':>12} {'(0,0)':>15} {'(0,1)':>20} {'値':>6}")

partial = mat_id()
current = n_example
for i, s in enumerate(steps):
    M = M_u if s == 'u' else M_d
    partial = mat_mul_exact(M, partial)
    det_p = partial[0][0]*partial[1][1] - partial[0][1]*partial[1][0]
    val = partial[0][0] * n_example + partial[0][1]
    det_f = float(det_p)
    log2_d = math.log2(abs(det_f)) if det_f != 0 else 0
    if i < 30 or i >= len(steps) - 5:
        print(f"  {i+1:>6} {s:>2} {str(det_p):>15} {log2_d:>12.4f} {str(partial[0][0]):>15} "
              f"{str(partial[0][1]):>20} {str(val):>6}")
    elif i == 30:
        print(f"  {'...':>6}")


# --- 7. 整数行列への変換 ---
print("\n\n■ 7. 整数行列への変換 (2倍スケーリング)")
print("  2*M_u = [[3, 1], [0, 2]], 2*M_d = [[1, 0], [0, 2]]")
print("  これらは Z 上の行列。Γ_0(2) の部分群に関連。")

M_u_int = [[3, 1], [0, 2]]
M_d_int = [[1, 0], [0, 2]]

print(f"\n  2*M_u: det = {3*2 - 1*0} = 6")
print(f"  2*M_d: det = {1*2 - 0*0} = 2")
print(f"  k ステップ後の行列積の det = 2^d * 6^u / (元のスケーリングを考慮)")

# --- 8. ステップ列のパターンと行列積 ---
print("\n\n■ 8. 連続上昇/下降パターンの行列べき")

# M_u^k の閉形式
print("  M_u^k = [[（3/2)^k, (3/2)^k - 1], [0, 1]]")
print("  M_d^k = [[(1/2)^k, 0], [0, 1]]")

print("\n  検証:")
for k in range(1, 6):
    Muk = mat_id()
    for _ in range(k):
        Muk = mat_mul_exact(M_u, Muk)
    expected_00 = Fraction(3,2)**k
    expected_01 = Fraction(3,2)**k - 1
    print(f"    M_u^{k}: [0][0]={Muk[0][0]} (期待: {expected_00}), "
          f"[0][1]={Muk[0][1]} (期待: {expected_01}), "
          f"一致: {Muk[0][0] == expected_00 and Muk[0][1] == expected_01}")


# --- 9. 到達条件の代数的表現 ---
print("\n\n■ 9. 1への到達条件の代数的表現")
print("  軌道のステップ列 s1, s2, ..., sk に対する行列積 P = M_sk ... M_s1")
print("  条件: P[0][0] * n + P[0][1] = 1")
print("  すなわち: n = (1 - P[0][1]) / P[0][0]")
print("  P[0][0] = 3^u / 2^(u+d) (行列式と等しい)")
print()
print("  よって: n = (1 - P[0][1]) * 2^(u+d) / 3^u")
print("  これが正の奇数整数になるステップ列が、有効な Collatz 軌道に対応。")

print("\n  逆問題: ステップ列から出発点 n を復元")
# ランダムなステップ列から n を計算
import itertools
print(f"\n  長さ4のすべてのステップ列 (上昇u, 下降d) と対応する n:")
for length in [3, 4, 5]:
    print(f"\n  長さ {length}:")
    valid_count = 0
    for seq in itertools.product('ud', repeat=length):
        seq_str = ''.join(seq)
        P = mat_id()
        for s in seq:
            M = M_u if s == 'u' else M_d
            P = mat_mul_exact(M, P)
        # n = (1 - P[0][1]) / P[0][0]
        if P[0][0] != 0:
            n_val = (1 - P[0][1]) / P[0][0]
            if n_val > 0 and n_val.denominator == 1:
                n_int = int(n_val)
                if n_int % 2 == 1 and n_int > 1:
                    # 検証
                    _, check_steps, _, _ = collatz_orbit_matrices(n_int)
                    check_str = ''.join(check_steps)
                    match = check_str == seq_str
                    if match:
                        valid_count += 1
                        if valid_count <= 10:
                            print(f"    {seq_str} → n = {n_int} (検証: {'OK' if match else 'NG'})")
    print(f"    有効なステップ列数: {valid_count}")


# --- 10. 大きな n に対する統計 ---
print("\n\n■ 10. 奇数 n = 1,3,...,999 に対する統計")

log2_3 = math.log2(3)
d_u_ratios = []
det_ratios = []
steps_list = []

for n in range(3, 1000, 2):
    _, steps, product, orbit = collatz_orbit_matrices(n)
    u = steps.count('u')
    d = steps.count('d')
    if u > 0:
        ratio = d / u
        d_u_ratios.append(ratio)
        det_exact, _ = exact_det_trace(product)
        log2_det = float(u) * math.log2(3) - float(u + d)
        det_ratios.append(log2_det)
        steps_list.append(len(steps))

avg_ratio = sum(d_u_ratios) / len(d_u_ratios)
min_ratio = min(d_u_ratios)
max_ratio = max(d_u_ratios)

print(f"  d/u 比の平均: {avg_ratio:.6f}")
print(f"  d/u 比の範囲: [{min_ratio:.4f}, {max_ratio:.4f}]")
print(f"  log2(3) - 1 = {log2_3 - 1:.6f} (理論的な d/u の臨界値)")
print(f"  平均 d/u と log2(3)-1 の比: {avg_ratio / (log2_3 - 1):.6f}")
print()
print(f"  log2(det) の平均: {sum(det_ratios)/len(det_ratios):.4f}")
print(f"  ステップ数の平均: {sum(steps_list)/len(steps_list):.2f}")

# d/u > log2(3) のとき det < 1 (縮小条件)
shrink_count = sum(1 for r in d_u_ratios if r > log2_3 - 1)
print(f"\n  d/u > log2(3)-1 (縮小条件) を満たす割合: {shrink_count}/{len(d_u_ratios)} "
      f"= {shrink_count/len(d_u_ratios)*100:.1f}%")


# --- 11. 行列積の半群構造 ---
print("\n\n■ 11. 行列積の半群構造と word の同値性")
print("  M_u と M_d で生成される半群 S = <M_u, M_d>")
print("  この半群の元は上三角行列 [[a, b], [0, 1]] (a > 0)")
print("  → アフィン群 Aff(Q) = { x → ax + b } と同型")
print("  → Collatz の各ステップはアフィン変換: ")
print("    上昇: x → (3/2)x + 1/2")
print("    下降: x → (1/2)x")
print()
print("  Syracuse 関数の k 回適用は、アフィン変換の合成")
print("  f(x) = (3^u / 2^(u+d)) x + c  (c は経路依存の定数)")

# 軌道のアフィン表現
print("\n  アフィン表現の例:")
for r in results[:6]:
    p00 = r['product'][0][0]
    p01 = r['product'][0][1]
    print(f"    n={r['n']:>5}: f(x) = ({p00})x + ({p01})")
    print(f"           f({r['n']}) = {p00 * r['n'] + p01} (= 1 ✓)")


# --- 12. 行列のリアプノフ指数 ---
print("\n\n■ 12. 行列積のリアプノフ指数")
print("  λ = lim (1/k) log ||P_k||  (k → ∞)")
print("  上三角なので λ = max(log|P[0][0]|, 0) / k")

print(f"\n  {'n':>6} {'ステップ':>6} {'u':>4} {'d':>4} {'log2|P[0][0]|/k':>16} {'log2(3/2)*u/k-d/k':>20}")

for r in results:
    k = r['steps']
    p00 = float(r['product'][0][0])
    if p00 > 0 and k > 0:
        lyap = math.log2(p00) / k
        theory = (r['u'] * math.log2(1.5) - r['d']) / k
        print(f"  {r['n']:>6} {k:>6} {r['u']:>4} {r['d']:>4} {lyap:>16.6f} {theory:>20.6f}")


# --- サマリー ---
print("\n\n" + "=" * 70)
print("■ サマリー")
print("=" * 70)
print("""
1. 各Collatzステップは上三角アフィン行列で表現可能:
   M_u = [[3/2, 1/2], [0, 1]],  M_d = [[1/2, 0], [0, 1]]

2. 行列積 P は常に上三角: P = [[3^u/2^(u+d), c], [0, 1]]
   - (0,0) 成分は行列式 det(P) = 3^u / 2^(u+d) に等しい
   - (0,1) 成分 c は経路に依存する定数

3. 1への到達条件: n = (1 - c) / det(P) が正の奇数整数
   → 逆に、ステップ列から出発点 n を一意に復元可能

4. Collatz 予想は「任意の正奇数 n に対し、
   n = (1 - c) * 2^(u+d) / 3^u を満たすステップ列 (u,d,c) が存在する」
   と同値

5. 行列式 det(P) = 3^u/2^(u+d) < 1/n が必要 (縮小条件)
   → d/u > log2(3) - 1 ≈ 0.585 が統計的に成り立つ

6. アフィン群の観点: Collatz は Aff(Q) 上のランダムウォークと見なせる
   リアプノフ指数が負 → ほぼ確実に収束 (エルゴード理論的議論)
""")
