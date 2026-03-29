#!/usr/bin/env python3
"""
コラッツ写像の位相的エントロピー h(T) の数値推定

Bowen-Dinaburg定義:
  h(T) = lim_{eps->0} limsup_{n->inf} (1/n) log N(n, eps)
  N(n, eps) = (n, eps)-分離集合の最大サイズ

手法:
1. Syracuse写像 T: odd -> odd の有限区間上の軌道を追跡
2. (n, eps)-分離集合のサイズを推定
3. 2進シフト sigma (h(sigma)=log2) との比較
4. パリティ列のエントロピーレートを計算
5. 転送行列法による区間写像のエントロピー推定
"""

import math
import random
from collections import Counter, defaultdict

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n >>= 1
        c += 1
    return c

def syracuse(n):
    """Syracuse写像 T: odd -> odd"""
    m = 3 * n + 1
    while m % 2 == 0:
        m >>= 1
    return m

def collatz_step(n):
    """通常のコラッツ写像 T: N -> N"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def collatz_orbit(n, steps):
    """n から steps ステップのコラッツ軌道"""
    orbit = [n]
    x = n
    for _ in range(steps):
        x = collatz_step(x)
        orbit.append(x)
    return orbit

def syracuse_orbit(n, steps):
    """奇数nからstepsステップのSyracuse軌道"""
    orbit = [n]
    x = n
    for _ in range(steps):
        if x == 1:
            x = 1  # 1に留まる
        x = syracuse(x)
        orbit.append(x)
    return orbit

# ============================================================
# 方法1: (n, eps)-分離集合のサイズ推定 (Bowen-Dinaburg直接法)
# ============================================================

def dn_metric(orbit1, orbit2, n):
    """
    d_n(x, y) = max_{0<=k<n} |T^k(x) - T^k(y)|
    Bowen-Dinaburgの n-step 距離
    ただし対数スケールで正規化
    """
    max_dist = 0
    for k in range(min(n, len(orbit1), len(orbit2))):
        # 対数スケールでの距離 (大きな数を扱うため)
        if orbit1[k] > 0 and orbit2[k] > 0:
            dist = abs(math.log(orbit1[k]) - math.log(orbit2[k]))
        else:
            dist = abs(orbit1[k] - orbit2[k])
        max_dist = max(max_dist, dist)
    return max_dist

def estimate_separated_set_size(N_max, n, eps, num_samples=2000):
    """
    [1, N_max] の奇数から始めて (n, eps)-分離集合のサイズを推定
    グリーディアルゴリズムで最大分離集合を構成
    """
    # 奇数のサンプリング
    candidates = []
    for _ in range(num_samples):
        x = random.randint(1, N_max)
        if x % 2 == 0:
            x += 1
        candidates.append(x)
    candidates = list(set(candidates))

    # 軌道を計算
    orbits = {}
    for x in candidates:
        orbits[x] = syracuse_orbit(x, n)

    # グリーディに分離集合を構成
    separated = []
    for x in candidates:
        is_separated = True
        for y in separated:
            if dn_metric(orbits[x], orbits[y], n) < eps:
                is_separated = False
                break
        if is_separated:
            separated.append(x)

    return len(separated)

def bowen_dinaburg_entropy_estimate():
    """Bowen-Dinaburg定義に基づく位相的エントロピーの推定"""
    print("=" * 60)
    print("方法1: Bowen-Dinaburg直接法 (Syracuse写像)")
    print("=" * 60)

    N_max = 10000
    eps_values = [2.0, 1.0, 0.5, 0.3]
    n_values = [5, 10, 15, 20, 25, 30]

    for eps in eps_values:
        print(f"\n--- eps = {eps} (対数スケール) ---")
        entropies = []
        for n in n_values:
            N_n_eps = estimate_separated_set_size(N_max, n, eps, num_samples=3000)
            if N_n_eps > 1:
                h_est = math.log(N_n_eps) / n
            else:
                h_est = 0
            entropies.append((n, N_n_eps, h_est))
            print(f"  n={n:3d}: N(n,eps)={N_n_eps:6d}, (1/n)log N = {h_est:.4f}")

        # 末尾の値を使ってlimsupを推定
        if len(entropies) >= 2:
            h_final = entropies[-1][2]
            print(f"  => h(T) 推定値 (n={n_values[-1]}): {h_final:.4f}")

    return entropies

# ============================================================
# 方法2: パリティ列のシャノンエントロピーレート
# ============================================================

def parity_entropy_rate():
    """
    コラッツ軌道のパリティ列 (0=偶数, 1=奇数) のエントロピーレート

    パリティ列は 2進シフトの記号力学に対応
    エントロピーレート = lim (1/n) H(X_1, ..., X_n)
    """
    print("\n" + "=" * 60)
    print("方法2: パリティ列のエントロピーレート")
    print("=" * 60)

    # k-gram確率を計算
    max_k = 10
    num_samples = 5000
    orbit_len = 500

    for k in range(1, max_k + 1):
        kgram_counts = Counter()
        total = 0

        for _ in range(num_samples):
            n = random.randint(3, 100000)
            if n % 2 == 0:
                n += 1
            orbit = collatz_orbit(n, orbit_len)
            parity = [x % 2 for x in orbit]

            for i in range(len(parity) - k):
                kgram = tuple(parity[i:i+k])
                kgram_counts[kgram] += 1
                total += 1

        # シャノンエントロピー H_k
        H_k = 0
        for count in kgram_counts.values():
            p = count / total
            if p > 0:
                H_k -= p * math.log2(p)

        # エントロピーレート h_k = H_k / k
        h_k = H_k / k

        # 条件付きエントロピー h = H_k - H_{k-1} (k >= 2)
        print(f"  k={k:2d}: H_{k}={H_k:.4f} bits, h_{k} = H_{k}/k = {h_k:.4f} bits/symbol")

    # k-gramの条件付きエントロピー (より正確な推定)
    print("\n  条件付きエントロピーレート (h = H_k - H_{k-1}):")
    for k in range(2, max_k + 1):
        # k-gram と (k-1)-gram を再計算
        kgram_counts = Counter()
        km1gram_counts = Counter()
        total_k = 0
        total_km1 = 0

        for _ in range(num_samples):
            n = random.randint(3, 100000)
            if n % 2 == 0:
                n += 1
            orbit = collatz_orbit(n, orbit_len)
            parity = [x % 2 for x in orbit]

            for i in range(len(parity) - k):
                kgram = tuple(parity[i:i+k])
                kgram_counts[kgram] += 1
                total_k += 1

            for i in range(len(parity) - k + 1):
                km1gram = tuple(parity[i:i+k-1])
                km1gram_counts[km1gram] += 1
                total_km1 += 1

        H_k = -sum(c/total_k * math.log2(c/total_k) for c in kgram_counts.values() if c > 0)
        H_km1 = -sum(c/total_km1 * math.log2(c/total_km1) for c in km1gram_counts.values() if c > 0)
        h_cond = H_k - H_km1

        print(f"  k={k:2d}: h = H_{k} - H_{k-1} = {H_k:.4f} - {H_km1:.4f} = {h_cond:.4f} bits/symbol")

# ============================================================
# 方法3: 転送行列法 (区間上の区分線形近似)
# ============================================================

def transfer_matrix_entropy():
    """
    コラッツ写像を区間 [1, N] 上の写像として近似し、
    転送行列のスペクトル半径から位相的エントロピーを推定

    区間を M 個のビンに分割
    T_{ij} = 1 if bin_j の像が bin_i と交差
    h(T) ≈ log(spectral_radius(T))
    """
    print("\n" + "=" * 60)
    print("方法3: 転送行列法")
    print("=" * 60)

    for N in [100, 500, 1000, 5000]:
        M = min(N, 200)  # ビン数
        bin_size = N / M

        # 転送行列の構築
        # T[i][j] = 1 if collatz(x in bin_j) intersects bin_i
        T = [[0] * M for _ in range(M)]

        for j in range(M):
            # bin_j の代表点でのコラッツ写像
            for x in range(max(1, int(j * bin_size)), min(N, int((j + 1) * bin_size))):
                y = collatz_step(x)
                if 1 <= y <= N:
                    i = min(int((y - 1) / bin_size), M - 1)
                    T[i][j] = 1

        # べき乗法でスペクトル半径を推定
        v = [1.0 / M] * M
        for iteration in range(100):
            new_v = [0.0] * M
            for i in range(M):
                for j in range(M):
                    new_v[i] += T[i][j] * v[j]
            norm = max(abs(x) for x in new_v)
            if norm > 0:
                v = [x / norm for x in new_v]
            else:
                break

        # スペクトル半径 ≈ norm
        spectral_radius = norm
        h_est = math.log(spectral_radius) if spectral_radius > 0 else 0

        print(f"  N={N:5d}, M={M:3d}: spectral_radius = {spectral_radius:.4f}, h ≈ log(rho) = {h_est:.4f}")
        print(f"    非ゼロ要素: {sum(T[i][j] for i in range(M) for j in range(M))}/{M*M}")

# ============================================================
# 方法4: 軌道の成長率 (Lap number)
# ============================================================

def lap_number_entropy():
    """
    Lap number法: L_n = T^n の単調区間の数
    h(T) = lim (1/n) log L_n

    コラッツ写像の場合、[1,N]上で単調な区間の数を数える
    """
    print("\n" + "=" * 60)
    print("方法4: Lap number (単調区間数) 法")
    print("=" * 60)

    N = 2000

    for n_iter in [1, 2, 3, 4, 5, 6, 7, 8]:
        # T^n の値を計算
        values = []
        for x in range(1, N + 1):
            y = x
            for _ in range(n_iter):
                y = collatz_step(y)
            values.append(y)

        # 単調区間の数 (方向転換の回数 + 1)
        laps = 1
        for i in range(1, len(values) - 1):
            if (values[i] - values[i-1]) * (values[i+1] - values[i]) < 0:
                laps += 1

        h_est = math.log(laps) / n_iter if laps > 0 else 0
        print(f"  n={n_iter}: L_n = {laps:8d}, (1/n)log(L_n) = {h_est:.4f}")

# ============================================================
# 方法5: Syracuse写像のリアプノフ指数との関係
# ============================================================

def lyapunov_entropy_relation():
    """
    Ruelle不等式: h(T) <= sum of positive Lyapunov exponents
    Pesin公式 (SRBの場合): h(T) = sum of positive Lyapunov exponents

    Syracuse写像のリアプノフ指数を再計算し、位相的エントロピーとの関係を検討
    """
    print("\n" + "=" * 60)
    print("方法5: リアプノフ指数とRuelle不等式")
    print("=" * 60)

    # Syracuse写像のリアプノフ指数
    num_samples = 50000
    orbit_len = 200

    # 方法A: v2の平均から計算
    v2_sum = 0
    v2_count = 0

    # 方法B: 直接の伸縮率
    log_deriv_sum = 0
    log_deriv_count = 0

    for _ in range(num_samples):
        n = random.randint(3, 1000000)
        if n % 2 == 0:
            n += 1

        x = n
        for step in range(orbit_len):
            if x <= 1:
                break

            # v2(3x+1)
            val = v2(3 * x + 1)
            v2_sum += val
            v2_count += 1

            # Syracuse写像の"微分" = 3 / 2^v2(3x+1)
            # log|T'| = log(3) - v2(3x+1) * log(2)
            log_deriv = math.log(3) - val * math.log(2)
            log_deriv_sum += log_deriv
            log_deriv_count += 1

            x = syracuse(x)

    avg_v2 = v2_sum / v2_count
    lyapunov_syracuse = log_deriv_sum / log_deriv_count

    # 通常のコラッツ写像のリアプノフ指数
    # 偶数 step: |T'| = 1/2, 奇数 step: |T'| = 3
    # 奇数の出現確率 ≈ p とすると
    # lambda = p * log(3) + (1-p) * log(1/2)

    # 実際のパリティ統計
    odd_count = 0
    total_count = 0

    for _ in range(num_samples):
        n = random.randint(3, 1000000)
        orbit = collatz_orbit(n, orbit_len)
        for x in orbit[:-1]:
            if x % 2 == 1:
                odd_count += 1
            total_count += 1

    p_odd = odd_count / total_count
    lyapunov_collatz = p_odd * math.log(3) + (1 - p_odd) * math.log(0.5)

    print(f"  Syracuse写像:")
    print(f"    平均 v2(3x+1) = {avg_v2:.4f}")
    print(f"    リアプノフ指数 lambda = log(3) - <v2>*log(2) = {lyapunov_syracuse:.4f}")
    print(f"")
    print(f"  通常コラッツ写像:")
    print(f"    奇数出現確率 p = {p_odd:.4f}")
    print(f"    リアプノフ指数 lambda = p*log(3) + (1-p)*log(1/2) = {lyapunov_collatz:.4f}")
    print(f"")
    print(f"  Ruelle不等式: h(T) <= max(lambda, 0)")
    print(f"    Syracuse: h(T) <= max({lyapunov_syracuse:.4f}, 0) = {max(lyapunov_syracuse, 0):.4f}")
    print(f"    Collatz:  h(T) <= max({lyapunov_collatz:.4f}, 0) = {max(lyapunov_collatz, 0):.4f}")
    print(f"")
    print(f"  参考値:")
    print(f"    log(2) = {math.log(2):.4f}")
    print(f"    log(3) = {math.log(3):.4f}")
    print(f"    log(3)/log(2) = {math.log(3)/math.log(2):.4f}")
    print(f"    2進シフトのエントロピー h(sigma) = log(2) = {math.log(2):.4f}")

# ============================================================
# 方法6: パリティ列の記号力学的エントロピー
# ============================================================

def symbolic_entropy():
    """
    パリティ列をシンボリックダイナミクスとして解析

    コラッツ写像の各ステップで 0(偶数→割る2) or 1(奇数→3x+1) を記録
    この記号力学のエントロピーを推定

    全てのパリティ列が実現可能なら h = log(2) (full shift)
    制約があれば h < log(2)
    """
    print("\n" + "=" * 60)
    print("方法6: パリティ列の記号力学的エントロピー")
    print("=" * 60)

    # パリティ列で実現可能な k-ブロックの数を調査
    num_samples = 100000
    orbit_len = 200

    for k in range(1, 16):
        observed_blocks = set()

        for _ in range(num_samples):
            n = random.randint(1, 1000000)
            orbit = collatz_orbit(n, orbit_len)
            parity = [x % 2 for x in orbit]

            for i in range(len(parity) - k):
                block = tuple(parity[i:i+k])
                observed_blocks.add(block)

        possible = 2 ** k
        observed = len(observed_blocks)
        ratio = observed / possible
        h_k = math.log(observed) / k if observed > 0 else 0

        print(f"  k={k:2d}: 実現可能ブロック = {observed:6d}/{possible:6d} ({ratio:.4f}), "
              f"(1/k)log(|B_k|) = {h_k:.4f}")

    # 連続する1の禁止パターン分析
    print("\n  禁止パターン分析:")
    print("  (連続する奇数ステップは制限される)")

    # コラッツで奇数の次は必ず偶数 (3x+1 は偶数)
    # なので parity 列で "11" は出現しないはず...
    # しかし通常のコラッツでは奇数 -> 3x+1(偶数) -> 割る2 -> 奇数or偶数
    # なので連続する1は起きない

    # 実際に確認
    max_consecutive_ones = 0
    for _ in range(10000):
        n = random.randint(1, 1000000)
        orbit = collatz_orbit(n, 500)
        parity = [x % 2 for x in orbit]

        consec = 0
        for p in parity:
            if p == 1:
                consec += 1
                max_consecutive_ones = max(max_consecutive_ones, consec)
            else:
                consec = 0

    print(f"  最大連続奇数ステップ: {max_consecutive_ones}")
    print(f"  (コラッツでは奇数->3x+1は常に偶数なので、連続1は不可能)")

    # 黄金比シフト(フィボナッチ)のエントロピーとの比較
    # "11"が禁止のシフト空間のエントロピー
    golden_ratio = (1 + math.sqrt(5)) / 2
    h_golden = math.log(golden_ratio)

    print(f"\n  '11'禁止のシフト空間 (黄金比シフト):")
    print(f"    エントロピー = log(phi) = {h_golden:.4f}")
    print(f"    phi = (1+sqrt(5))/2 = {golden_ratio:.4f}")

    # コラッツの場合の制約はもっと強い
    # 奇数の後は必ず偶数 => "1" の後は必ず "0"
    # つまり許される遷移: 0->0, 0->1, 1->0
    # これは転送行列 [[1,1],[1,0]] のシフト => 黄金比シフトと同一!

    print(f"\n  コラッツのパリティ列制約:")
    print(f"    許可遷移: 0->0, 0->1, 1->0")
    print(f"    禁止遷移: 1->1")
    print(f"    転送行列: [[1,1],[1,0]] (黄金比シフトと同一)")
    print(f"    => パリティ記号力学のエントロピー = log(phi) = {h_golden:.4f}")

# ============================================================
# 方法7: 2進シフトとの比較 - 拡張コラッツ写像
# ============================================================

def binary_shift_comparison():
    """
    コラッツ写像 T と2進シフト sigma の関係

    2進シフト: sigma(x) = 2x mod 1  (h(sigma) = log 2)

    コラッツを [0,1) 上の写像として解釈:
    T(x) = x/2       if x in [0, 1/2)  (偶数分岐)
    T(x) = (3x+1)/2  mod ...           (奇数分岐)

    この写像の位相的エントロピーを推定
    """
    print("\n" + "=" * 60)
    print("方法7: 2進シフトとの比較")
    print("=" * 60)

    # コラッツ写像の分岐の傾き
    print("  コラッツ写像の分岐:")
    print(f"    偶数分岐: T(x) = x/2       傾き = 1/2")
    print(f"    奇数分岐: T(x) = (3x+1)/2  傾き = 3/2")
    print(f"")
    print(f"  区分線形写像のエントロピー (Milnor-Thurston):")
    print(f"    |slope_0| = 1/2, |slope_1| = 3/2")
    print(f"    h(T) = max(0, log(max|slope|)) = log(3/2) = {math.log(1.5):.4f}")
    print(f"    (ただしこれは単純な区分線形の場合)")

    # より精密: コラッツは可逆的な「分岐」を持つ
    # 各ステップで log(3) の拡大と log(2^v2) の縮小

    # 平均拡大率の計算
    total_expansion = 0
    count = 0

    for _ in range(100000):
        n = random.randint(3, 1000000)
        orbit = collatz_orbit(n, 100)
        for i in range(len(orbit) - 1):
            x = orbit[i]
            y = orbit[i + 1]
            if x > 0 and y > 0:
                # 局所的な拡大率 |T'(x)|
                if x % 2 == 0:
                    expansion = 0.5
                else:
                    expansion = 1.5  # (3x+1)/2x ≈ 3/2
                total_expansion += math.log(expansion)
                count += 1

    avg_log_expansion = total_expansion / count
    print(f"\n  平均対数拡大率: <log|T'|> = {avg_log_expansion:.4f}")
    print(f"  exp(<log|T'|>) = {math.exp(avg_log_expansion):.4f}")

    # Syracuse写像でのエントロピー
    # T_syrac の各ステップは 3/2^v2(3x+1) の傾き
    # 位相的エントロピーの上界: E[max(0, log|T'|)]

    pos_lyap_sum = 0
    pos_lyap_count = 0

    for _ in range(100000):
        n = random.randint(3, 1000000)
        if n % 2 == 0:
            n += 1
        x = n
        for _ in range(100):
            if x <= 1:
                break
            val = v2(3 * x + 1)
            log_deriv = math.log(3) - val * math.log(2)
            if log_deriv > 0:
                pos_lyap_sum += log_deriv
            pos_lyap_count += 1
            x = syracuse(x)

    avg_pos_lyap = pos_lyap_sum / pos_lyap_count
    print(f"\n  Syracuse写像:")
    print(f"    E[max(0, log|T'|)] = {avg_pos_lyap:.4f}")
    print(f"    (Ruelle不等式の上界)")

# ============================================================
# 方法8: 逆像の成長率
# ============================================================

def preimage_growth():
    """
    位相的エントロピーの別定義:
    h(T) = lim (1/n) log |T^{-n}(x)|

    コラッツの逆写像:
    x -> 2x (常に)
    x -> (2x-1)/3 (if 2x ≡ 1 mod 3)
    """
    print("\n" + "=" * 60)
    print("方法8: 逆像の成長率")
    print("=" * 60)

    def collatz_preimages(x, max_val=10**8):
        """xのコラッツ写像での逆像"""
        pre = []
        # x = T(2x) -> 2x は逆像
        pre.append(2 * x)
        # x = T((2x-1)/3) -> (2x-1)/3 が奇数の正整数なら逆像
        if (2 * x - 1) % 3 == 0:
            y = (2 * x - 1) // 3
            if y > 0 and y % 2 == 1:
                pre.append(y)
        return [p for p in pre if p <= max_val]

    # BFS で n-step 逆像の数を計算
    start = 1
    max_val = 10**10

    print(f"  始点: {start}")
    print(f"  上界: {max_val}")

    current_set = {start}
    for n in range(1, 31):
        next_set = set()
        for x in current_set:
            for p in collatz_preimages(x, max_val):
                next_set.add(p)
        current_set = next_set

        if len(current_set) > 0:
            h_est = math.log(len(current_set)) / n
        else:
            h_est = 0

        print(f"  n={n:2d}: |T^{{-n}}(1)| = {len(current_set):10d}, (1/n)log|...| = {h_est:.4f}")

        # メモリ制限
        if len(current_set) > 500000:
            print(f"  (集合が大きくなりすぎたため打ち切り)")
            break

# ============================================================
# 総合分析
# ============================================================

def comprehensive_analysis():
    """全手法の結果を総合的に分析"""
    print("\n" + "=" * 60)
    print("総合分析: コラッツ写像の位相的エントロピー")
    print("=" * 60)

    golden_ratio = (1 + math.sqrt(5)) / 2

    print(f"\n  参考定数:")
    print(f"    log(2) = {math.log(2):.6f}  (2進シフトのエントロピー)")
    print(f"    log(3/2) = {math.log(1.5):.6f}  (3/2-拡大写像)")
    print(f"    log(phi) = {math.log(golden_ratio):.6f}  (黄金比シフト, '11'禁止)")
    print(f"    log(3) = {math.log(3):.6f}")
    print(f"    log(3)/log(2) = {math.log(3)/math.log(2):.6f}")

    print(f"\n  理論的考察:")
    print(f"    1. コラッツ予想が真なら、全ての軌道は有限時間で1に到達")
    print(f"       => 不変集合は {{1,2,4}} のみ")
    print(f"       => 不変測度のエントロピー = 0 (Santana 2025)")
    print(f"    2. しかし位相的エントロピーは不変測度のエントロピーの上限")
    print(f"       h_top(T) = sup_mu h_mu(T)  (変分原理)")
    print(f"       h_mu = 0 for all mu => h_top = 0 は必ずしも成り立たない")
    print(f"    3. パリティ列の制約: '11' は禁止")
    print(f"       => 記号力学のエントロピー <= log(phi) = {math.log(golden_ratio):.6f}")
    print(f"    4. 逆像の成長率は位相的エントロピーを与える")
    print(f"       各点の逆像は最大2個 => h_top <= log(2)")
    print(f"    5. コラッツ写像は [1,N] 上では位相力学系ではない")
    print(f"       (定義域が自然数全体で非コンパクト)")
    print(f"       => Bowen-Dinaburg定義の厳密な適用には注意が必要")

    print(f"\n  エントロピーの推定値まとめ:")
    print(f"    パリティ記号力学:  log(phi) ≈ {math.log(golden_ratio):.4f} (上界)")
    print(f"    逆像成長率:        ~ log(2) ≈ {math.log(2):.4f} の近傍")
    print(f"    不変測度エントロピー: 0 (予想が真の場合)")
    print(f"    2進シフト比較:     log(2) = {math.log(2):.4f}")
    print(f"    log(3/2)候補:      {math.log(1.5):.4f}")

# ============================================================
# メイン
# ============================================================

if __name__ == "__main__":
    random.seed(42)

    bowen_dinaburg_entropy_estimate()
    parity_entropy_rate()
    transfer_matrix_entropy()
    lap_number_entropy()
    lyapunov_entropy_relation()
    symbolic_entropy()
    binary_shift_comparison()
    preimage_growth()
    comprehensive_analysis()
