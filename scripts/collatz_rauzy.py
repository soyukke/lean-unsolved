#!/usr/bin/env python3
"""
探索054: Syracuse軌道のsubstitution dynamicsとRauzy fractal的構造解析

Syracuse軌道を U/D 記号列に符号化し、substitution rule の探索、
エントロピー率、自己相関、Rauzy fractal 的プロットを行う。
(numpy不使用版)
"""

import math
import cmath
from collections import Counter, defaultdict
from itertools import product as iter_product

# ============================================================
# 基本的な線形代数ユーティリティ
# ============================================================

def mat_mul(A, B):
    """2x2 行列の積"""
    n = len(A)
    m = len(B[0])
    k = len(B)
    C = [[0.0]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            for l in range(k):
                C[i][j] += A[i][l] * B[l][j]
    return C

def eigenvalues_2x2(M):
    """2x2行列の固有値"""
    a, b = M[0][0], M[0][1]
    c, d = M[1][0], M[1][1]
    trace = a + d
    det = a * d - b * c
    disc = trace**2 - 4*det
    if disc >= 0:
        sq = math.sqrt(disc)
        return [(trace + sq)/2, (trace - sq)/2]
    else:
        sq = cmath.sqrt(disc)
        return [(trace + sq)/2, (trace - sq)/2]

def eigenvector_2x2(M, lam):
    """2x2行列の固有ベクトル (近似)"""
    a, b = M[0][0] - lam, M[0][1]
    c, d = M[1][0], M[1][1] - lam
    if abs(a) > 1e-12 or abs(b) > 1e-12:
        if abs(b) > abs(a):
            v = [b, -a]
        else:
            v = [-b if abs(b) > 1e-12 else 1.0, a if abs(b) > 1e-12 else 0.0]
            # (M - λI)v = 0 → a*v1 + b*v2 = 0 → v = (-b, a)
            v = [-b, a]
    else:
        v = [-d, c]
    norm = math.sqrt(v[0]**2 + v[1]**2)
    if norm > 0:
        v = [v[0]/norm, v[1]/norm]
    return v

# ============================================================
# 1. コラッツ軌道の生成とU/D符号化
# ============================================================

def syracuse_trajectory(n, max_steps=10000):
    """Syracuse形式: 奇数だけを追跡。T(n) = (3n+1)/2^v2(3n+1)"""
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    traj = [n]
    steps_info = []
    while n != 1 and len(traj) < max_steps:
        m = 3 * n + 1
        v2 = 0
        while m % 2 == 0:
            m //= 2
            v2 += 1
        steps_info.append(v2)
        n = m
        traj.append(n)
    return traj, steps_info

def encode_ud(steps_info):
    """v2値をU/D記号に符号化。v2=1→U(上昇傾向), v2>=2→D(下降傾向)"""
    return ''.join('U' if v == 1 else 'D' for v in steps_info)

def encode_ud_fine(steps_info):
    """より細かい符号化: v2=1→A, v2=2→B, v2>=3→C"""
    def sym(v):
        if v == 1: return 'A'
        elif v == 2: return 'B'
        else: return 'C'
    return ''.join(sym(v) for v in steps_info)


# ============================================================
# 2. 部分列の頻度分析
# ============================================================

def subsequence_frequencies(seq, max_len=8):
    """長さ 1..max_len の全部分列の出現頻度"""
    results = {}
    for k in range(1, max_len + 1):
        counter = Counter()
        for i in range(len(seq) - k + 1):
            sub = seq[i:i+k]
            counter[sub] += 1
        total = sum(counter.values())
        freq = {s: c / total for s, c in counter.most_common()}
        results[k] = freq
    return results


# ============================================================
# 3. エントロピー率
# ============================================================

def block_entropy(seq, k):
    """長さkブロックのShannon entropy"""
    counter = Counter()
    for i in range(len(seq) - k + 1):
        counter[seq[i:i+k]] += 1
    total = sum(counter.values())
    h = 0.0
    for c in counter.values():
        p = c / total
        if p > 0:
            h -= p * math.log2(p)
    return h

def entropy_rate(seq, max_k=12):
    """エントロピー率 h = lim (H_k - H_{k-1})"""
    entropies = []
    for k in range(1, max_k + 1):
        if len(seq) - k + 1 < 2:
            break
        entropies.append(block_entropy(seq, k))
    rates = [entropies[0]]
    for i in range(1, len(entropies)):
        rates.append(entropies[i] - entropies[i-1])
    return entropies, rates


# ============================================================
# 4. Substitution 規則の探索
# ============================================================

def substitution_matrix(rules, alphabet):
    """置換行列: M[i][j] = rules[alphabet[j]] 中の alphabet[i] の出現数"""
    n = len(alphabet)
    M = [[0.0]*n for _ in range(n)]
    for j, s in enumerate(alphabet):
        for c in rules[s]:
            i = alphabet.index(c)
            M[i][j] += 1
    return M


def apply_substitution(seq, rules, iterations=1):
    """置換規則を文字列に適用"""
    for _ in range(iterations):
        seq = ''.join(rules.get(c, c) for c in seq)
    return seq


def find_substitution_heuristic(seq, alphabet, max_image_len=3):
    """
    ヒューリスティックにsubstitution ruleを探索。
    """
    results = []
    actual_counter = Counter(seq)
    total = len(seq)
    actual_freq = {s: actual_counter.get(s, 0)/total for s in alphabet}

    for img_len_u in range(1, max_image_len+1):
        for img_len_d in range(1, max_image_len+1):
            for img_u in iter_product(alphabet, repeat=img_len_u):
                img_u_str = ''.join(img_u)
                for img_d in iter_product(alphabet, repeat=img_len_d):
                    img_d_str = ''.join(img_d)
                    rules = {alphabet[0]: img_u_str, alphabet[1]: img_d_str}

                    M = substitution_matrix(rules, alphabet)

                    if len(alphabet) == 2:
                        eigvals = eigenvalues_2x2(M)
                    else:
                        continue

                    max_eig_abs = max(abs(e) for e in eigvals)
                    if max_eig_abs < 1.0:
                        continue

                    # Perron-Frobenius 固有ベクトルから記号頻度を計算
                    try:
                        idx = 0 if abs(eigvals[0]) >= abs(eigvals[1]) else 1
                        lam = eigvals[idx].real if isinstance(eigvals[idx], complex) else eigvals[idx]
                        ev = eigenvector_2x2(M, lam)
                        ev = [abs(v) for v in ev]
                        ev_sum = sum(ev)
                        if ev_sum == 0:
                            continue
                        ev = [v/ev_sum for v in ev]

                        # 各記号の寄与
                        char_count = {s: 0.0 for s in alphabet}
                        for i, s in enumerate(alphabet):
                            for c in rules[s]:
                                char_count[c] += ev[i]
                        total_chars = sum(char_count.values())
                        if total_chars == 0:
                            continue
                        pred_freq = {s: char_count[s]/total_chars for s in alphabet}
                    except:
                        continue

                    score = sum((pred_freq.get(s, 0) - actual_freq.get(s, 0))**2
                               for s in alphabet)
                    results.append((score, rules, max_eig_abs, pred_freq))

    results.sort(key=lambda x: x[0])
    return results[:20]


def check_pisot(rules, alphabet):
    """置換行列の最大固有値がPisot数かチェック"""
    M = substitution_matrix(rules, alphabet)
    if len(alphabet) == 2:
        eigvals = eigenvalues_2x2(M)
    else:
        return False, [], []

    abs_eigs = sorted([abs(e) for e in eigvals], reverse=True)
    is_pisot = abs_eigs[0] > 1.0 and all(e < 1.0 for e in abs_eigs[1:])
    return is_pisot, abs_eigs, eigvals


# ============================================================
# 5. 自己相関関数とpower spectrum
# ============================================================

def autocorrelation(seq, max_lag=200):
    """記号列の自己相関（U=1, D=0として数値化）"""
    x = [1.0 if c == 'U' else 0.0 for c in seq]
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    n = len(x)
    var = sum(v**2 for v in x)
    if var == 0:
        return [1.0] * min(max_lag, n)
    acf = []
    for lag in range(min(max_lag, n)):
        val = sum(x[i] * x[i+lag] for i in range(n-lag)) / var
        acf.append(val)
    return acf

def power_spectrum(seq, nfft=512):
    """パワースペクトル (simple DFT)"""
    x = [1.0 if c == 'U' else 0.0 for c in seq]
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    N = min(len(x), nfft)
    x = x[:N]

    # DFT
    spectrum = []
    freqs = []
    for k in range(1, N//2):
        re = sum(x[n] * math.cos(2*math.pi*k*n/N) for n in range(N))
        im = sum(x[n] * math.sin(2*math.pi*k*n/N) for n in range(N))
        spectrum.append(re**2 + im**2)
        freqs.append(k / N)
    return freqs, spectrum


# ============================================================
# 6. de Bruijn グラフ解析
# ============================================================

def de_bruijn_graph(seq, k=3):
    """de Bruijn グラフ"""
    nodes = set()
    edges = Counter()
    for i in range(len(seq) - k):
        prefix = seq[i:i+k]
        suffix = seq[i+1:i+k+1]
        nodes.add(prefix)
        nodes.add(suffix)
        edges[(prefix, suffix)] += 1
    return nodes, edges


# ============================================================
# 7. Rauzy fractal 的プロット（複素平面上の累積和）
# ============================================================

def rauzy_plot_data(seq, theta1=0.0, theta2=2*math.pi/3):
    """U → e^{iθ₁}, D → e^{iθ₂} として累積和を計算"""
    dir_u = cmath.exp(1j * theta1)
    dir_d = cmath.exp(1j * theta2)
    z = 0.0 + 0.0j
    xs, ys = [0.0], [0.0]
    for c in seq:
        z += dir_u if c == 'U' else dir_d
        xs.append(z.real)
        ys.append(z.imag)
    return xs, ys


# ============================================================
# 8. Box-counting 次元推定
# ============================================================

def estimate_box_dimension(xs, ys, n_scales=10):
    """Box-counting法によるフラクタル次元推定"""
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range == 0 or y_range == 0:
        return 1.0

    max_range = max(x_range, y_range)

    sizes = []
    counts = []

    for i in range(2, n_scales + 2):
        eps = max_range / (2**i)
        if eps == 0:
            continue

        boxes = set()
        for j in range(len(xs)):
            ix = int((xs[j] - x_min) / eps)
            iy = int((ys[j] - y_min) / eps)
            boxes.add((ix, iy))
        if len(boxes) > 1:
            sizes.append(math.log(1.0/eps))
            counts.append(math.log(len(boxes)))

    if len(sizes) < 3:
        return 1.0

    # 線形フィット (最小二乗法)
    n = len(sizes)
    sx = sum(sizes)
    sy = sum(counts)
    sxx = sum(s**2 for s in sizes)
    sxy = sum(sizes[i]*counts[i] for i in range(n))
    slope = (n * sxy - sx * sy) / (n * sxx - sx**2)
    return slope


# ============================================================
# メイン解析
# ============================================================

def analyze_single(n, label=""):
    """単一の初期値に対する全解析"""
    print(f"\n{'='*70}")
    print(f"  n = {n} {label}")
    print(f"{'='*70}")

    traj, steps_info = syracuse_trajectory(n)
    ud_seq = encode_ud(steps_info)
    fine_seq = encode_ud_fine(steps_info)

    print(f"Syracuse軌道長: {len(traj)}")
    print(f"U/D列長: {len(ud_seq)}")
    print(f"U/D列（先頭100文字）: {ud_seq[:100]}")
    print(f"細分列（先頭100文字）: {fine_seq[:100]}")

    # v2 値の分布
    v2_counter = Counter(steps_info)
    print(f"\nv2値分布:")
    for v in sorted(v2_counter.keys()):
        print(f"  v2={v}: {v2_counter[v]} ({v2_counter[v]/len(steps_info)*100:.1f}%)")

    # 記号頻度
    ud_counter = Counter(ud_seq)
    print(f"\nU/D頻度: U={ud_counter.get('U',0)} ({ud_counter.get('U',0)/len(ud_seq)*100:.1f}%), "
          f"D={ud_counter.get('D',0)} ({ud_counter.get('D',0)/len(ud_seq)*100:.1f}%)")

    return traj, steps_info, ud_seq, fine_seq


def main():
    print("=" * 70)
    print("  探索054: Syracuse軌道のsubstitution dynamics")
    print("         と Rauzy fractal 的構造解析")
    print("=" * 70)

    test_values = [7, 27, 97, 171, 649, 871, 6171, 9663, 77031, 837799]
    all_results = {}

    for n in test_values:
        traj, steps_info, ud_seq, fine_seq = analyze_single(n)
        all_results[n] = {
            'traj_len': len(traj),
            'ud_seq': ud_seq,
            'fine_seq': fine_seq,
            'steps_info': steps_info,
        }

    # ============================================================
    # 長い軌道で詳細解析（n=837799）
    # ============================================================
    long_n = 837799
    print(f"\n\n{'#'*70}")
    print(f"  詳細解析: n = {long_n}")
    print(f"{'#'*70}")

    ud_seq = all_results[long_n]['ud_seq']
    fine_seq = all_results[long_n]['fine_seq']
    steps_info = all_results[long_n]['steps_info']

    # --- 部分列頻度 ---
    print(f"\n--- 部分列頻度分析 (U/D) ---")
    freqs = subsequence_frequencies(ud_seq, max_len=6)
    for k in range(1, 7):
        print(f"\n長さ {k}:")
        for s, f in sorted(freqs[k].items(), key=lambda x: -x[1])[:10]:
            print(f"  {s}: {f:.6f}")

    # --- エントロピー率 ---
    print(f"\n--- エントロピー率 ---")
    entropies, rates = entropy_rate(ud_seq, max_k=10)
    for k in range(len(entropies)):
        print(f"  H({k+1}) = {entropies[k]:.6f},  h({k+1}) = {rates[k]:.6f}")
    print(f"  → エントロピー率推定: h ≈ {rates[-1]:.6f} bits/symbol")

    p_u = Counter(ud_seq)['U'] / len(ud_seq)
    h_max = -p_u * math.log2(p_u) - (1-p_u) * math.log2(1-p_u) if 0 < p_u < 1 else 0
    print(f"  理論最大（独立）: H_max = {h_max:.6f}")
    if h_max > 0:
        print(f"  冗長度: {1 - rates[-1]/h_max:.4f}")

    # --- 細分記号列のエントロピー ---
    print(f"\n--- 細分記号列 (A/B/C) エントロピー率 ---")
    entropies_f, rates_f = entropy_rate(fine_seq, max_k=8)
    for k in range(len(entropies_f)):
        print(f"  H({k+1}) = {entropies_f[k]:.6f},  h({k+1}) = {rates_f[k]:.6f}")

    # --- Substitution規則探索 ---
    print(f"\n--- Substitution規則探索 (U/D) ---")
    combined_ud = ''.join(all_results[n]['ud_seq'] for n in test_values if len(all_results[n]['ud_seq']) > 50)
    print(f"結合列長: {len(combined_ud)}")

    alphabet_ud = ['U', 'D']
    heuristic_results = find_substitution_heuristic(combined_ud, alphabet_ud, max_image_len=3)

    print(f"\n上位10候補:")
    for i, (score, rules, max_eig, pred_freq) in enumerate(heuristic_results[:10]):
        is_pisot, sorted_eigs, eigvals = check_pisot(rules, alphabet_ud)
        print(f"  {i+1}. U→{rules['U']}, D→{rules['D']}  "
              f"score={score:.6f}, λ_max={max_eig:.4f}, "
              f"Pisot={'Yes' if is_pisot else 'No'}, "
              f"pred_U={pred_freq['U']:.4f}")

        if i < 3:
            M = substitution_matrix(rules, alphabet_ud)
            print(f"     置換行列: [{M[0][0]:.0f},{M[0][1]:.0f}; {M[1][0]:.0f},{M[1][1]:.0f}]")
            eig_str = ", ".join(f"{e:.4f}" if isinstance(e, float) else f"{e}" for e in eigvals)
            print(f"     固有値: {eig_str}")

            seed = 'U'
            for it in range(1, 8):
                seed = apply_substitution(seed, rules)
                if len(seed) > 80:
                    print(f"     {it}回適用 (len={len(seed)}): {seed[:80]}...")
                    break
                else:
                    print(f"     {it}回適用: {seed}")

    # --- 3記号分布 ---
    print(f"\n--- 細分記号 (A/B/C) 頻度 ---")
    combined_fine = ''.join(all_results[n]['fine_seq'] for n in test_values if len(all_results[n]['fine_seq']) > 50)
    alphabet_fine = ['A', 'B', 'C']
    fine_counter = Counter(combined_fine)
    total_fine = len(combined_fine)
    print(f"記号頻度: " + ", ".join(f"{s}={fine_counter[s]/total_fine:.4f}" for s in alphabet_fine))

    # --- 自己相関 ---
    print(f"\n--- 自己相関関数 ---")
    acf = autocorrelation(ud_seq, max_lag=51)
    print("lag  ACF")
    for lag in [0, 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50]:
        if lag < len(acf):
            print(f"  {lag:3d}  {acf[lag]:.6f}")

    threshold = 2.0 / math.sqrt(len(ud_seq))
    peaks = [(lag, acf[lag]) for lag in range(1, len(acf)) if abs(acf[lag]) > threshold]
    if peaks:
        print(f"\n有意な相関ピーク (閾値 {threshold:.4f}):")
        for lag, val in peaks[:20]:
            print(f"  lag={lag}: {val:.6f}")
    else:
        print(f"\n有意な相関ピークなし（閾値 {threshold:.4f}）")

    # --- パワースペクトル ---
    print(f"\n--- パワースペクトル ---")
    freqs_ps, spectrum = power_spectrum(ud_seq, nfft=256)
    # 上位ピーク
    indexed = list(enumerate(spectrum))
    indexed.sort(key=lambda x: -x[1])
    print("Top 10 spectral peaks:")
    for idx, pwr in indexed[:10]:
        print(f"  freq={freqs_ps[idx]:.6f}, power={pwr:.2f}")

    # --- de Bruijn グラフ ---
    print(f"\n--- de Bruijn グラフ (k=3) ---")
    nodes, edges = de_bruijn_graph(ud_seq, k=3)
    print(f"ノード数: {len(nodes)}")
    print(f"エッジ数: {len(edges)}")
    print("エッジ（出現頻度順）:")
    for (src, dst), cnt in sorted(edges.items(), key=lambda x: -x[1])[:15]:
        print(f"  {src} → {dst}: {cnt}")

    print(f"\n--- de Bruijn グラフ (k=4) ---")
    nodes4, edges4 = de_bruijn_graph(ud_seq, k=4)
    print(f"ノード数: {len(nodes4)}")
    print(f"エッジ数: {len(edges4)}")
    for (src, dst), cnt in sorted(edges4.items(), key=lambda x: -x[1])[:15]:
        print(f"  {src} → {dst}: {cnt}")

    # --- Rauzy fractal 的プロット ---
    print(f"\n--- Rauzy fractal 的プロット ---")
    angle_pairs = [
        (0, 2*math.pi/3, "θ₁=0, θ₂=2π/3"),
        (0, math.pi * (math.sqrt(5)-1)/2, "θ₁=0, θ₂=π·φ（黄金比）"),
        (0, math.pi/2, "θ₁=0, θ₂=π/2"),
        (math.pi/6, 5*math.pi/6, "θ₁=π/6, θ₂=5π/6"),
    ]

    for theta1, theta2, label in angle_pairs:
        xs, ys = rauzy_plot_data(ud_seq, theta1, theta2)
        x_range = max(xs) - min(xs)
        y_range = max(ys) - min(ys)
        dim = estimate_box_dimension(xs, ys)
        print(f"\n{label}:")
        print(f"  x範囲: [{min(xs):.2f}, {max(xs):.2f}] (幅 {x_range:.2f})")
        print(f"  y範囲: [{min(ys):.2f}, {max(ys):.2f}] (幅 {y_range:.2f})")
        print(f"  Box-counting次元推定: {dim:.4f}")
        print(f"  終点: ({xs[-1]:.4f}, {ys[-1]:.4f})")

    # --- 全初期値の比較 ---
    print(f"\n\n{'#'*70}")
    print(f"  全初期値の統計比較")
    print(f"{'#'*70}")

    print(f"\n{'n':>8s} | {'軌道長':>6s} | {'U%':>7s} | {'D%':>7s} | {'h_rate':>8s} | {'ACF(1)':>8s} | {'dim':>6s}")
    print("-" * 72)
    for n in test_values:
        ud = all_results[n]['ud_seq']
        if len(ud) < 10:
            continue
        uc = Counter(ud)
        u_pct = uc.get('U', 0) / len(ud) * 100
        d_pct = uc.get('D', 0) / len(ud) * 100
        _, r = entropy_rate(ud, max_k=min(8, max(2, len(ud)//3)))
        h = r[-1] if r else 0
        ac = autocorrelation(ud, max_lag=5)
        ac1 = ac[1] if len(ac) > 1 else 0
        rxs, rys = rauzy_plot_data(ud, 0, 2*math.pi/3)
        dim = estimate_box_dimension(rxs, rys)
        tl = all_results[n]['traj_len']
        print(f"{n:>8d} | {tl:>6d} | {u_pct:>6.1f}% | {d_pct:>6.1f}% | {h:>8.4f} | {ac1:>8.4f} | {dim:>6.3f}")

    # --- v2の分布の普遍性 ---
    print(f"\n--- v2分布の普遍性テスト ---")
    print(f"理論値（独立仮定）: v2=1: 50%, v2=2: 25%, v2=3: 12.5%, v2=4: 6.25%, v2≥5: 6.25%")
    print(f"\n{'n':>8s} | {'v2=1':>8s} | {'v2=2':>8s} | {'v2=3':>8s} | {'v2=4':>8s} | {'v2≥5':>8s}")
    print("-" * 60)
    for n in test_values:
        si = all_results[n]['steps_info']
        if len(si) < 10:
            continue
        total = len(si)
        v_counts = Counter(si)
        v1 = v_counts.get(1, 0) / total * 100
        v2 = v_counts.get(2, 0) / total * 100
        v3 = v_counts.get(3, 0) / total * 100
        v4 = v_counts.get(4, 0) / total * 100
        v5p = sum(v_counts.get(k, 0) for k in v_counts if k >= 5) / total * 100
        print(f"{n:>8d} | {v1:>7.2f}% | {v2:>7.2f}% | {v3:>7.2f}% | {v4:>7.2f}% | {v5p:>7.2f}%")

    # --- 置換規則の適合テスト ---
    print(f"\n--- 置換規則の適合テスト ---")
    if heuristic_results:
        best_score, best_rules, _, _ = heuristic_results[0]
        print(f"最良規則: U→{best_rules['U']}, D→{best_rules['D']}")

        generated = apply_substitution('U', best_rules, iterations=15)
        gen_len = min(len(generated), len(combined_ud))
        generated = generated[:gen_len]

        print(f"\n部分列頻度比較:")
        actual_freq_dict = subsequence_frequencies(combined_ud, 4)
        gen_freq_dict = subsequence_frequencies(generated, 4)
        for k in [2, 3, 4]:
            print(f"\n  長さ {k}:")
            all_subs = set(list(actual_freq_dict[k].keys()) + list(gen_freq_dict[k].keys()))
            for s in sorted(all_subs):
                a = actual_freq_dict[k].get(s, 0)
                g = gen_freq_dict[k].get(s, 0)
                print(f"    {s}: 実際={a:.4f}, 生成={g:.4f}, 差={abs(a-g):.4f}")

    # --- 連の分布 ---
    print(f"\n--- 連（run）の分布 ---")
    for sym in ['U', 'D']:
        runs = []
        count = 0
        for c in ud_seq:
            if c == sym:
                count += 1
            else:
                if count > 0:
                    runs.append(count)
                count = 0
        if count > 0:
            runs.append(count)
        run_counter = Counter(runs)
        print(f"\n{sym}の連長分布:")
        for length in sorted(run_counter.keys()):
            print(f"  長さ {length}: {run_counter[length]} ({run_counter[length]/len(runs)*100:.1f}%)")
        if runs:
            avg_run = sum(runs) / len(runs)
            max_run = max(runs)
            print(f"  平均連長: {avg_run:.2f}, 最大連長: {max_run}")

    print(f"\n{'='*70}")
    print("  解析完了")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
