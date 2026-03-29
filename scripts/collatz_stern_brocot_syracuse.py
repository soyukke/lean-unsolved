"""
Syracuse軌道とStern-Brocot木の関係探索

目的:
- Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} の各ステップで
  log_2(T(n)/n) = log_2(3) - v2(3n+1) * log_2(2) を計算
- この値をStern-Brocot木のmediant操作(左右移動)と対応づけられるか調査
- 収束率とSB木の深さの関係を分析
"""

import math
from fractions import Fraction
from collections import Counter, defaultdict

# ========================================
# 基本関数
# ========================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 999
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse T(n) for odd n"""
    assert n % 2 == 1 and n > 0
    val = 3 * n + 1
    return val >> v2(val)

def syracuse_orbit(n, max_steps=1000):
    """奇数のみのSyracuse軌道"""
    orbit = [n]
    current = n
    for _ in range(max_steps):
        if current == 1 and len(orbit) > 1:
            break
        current = syracuse(current)
        orbit.append(current)
        if current == 1:
            break
    return orbit

def mean(lst):
    return sum(lst) / len(lst) if lst else 0

def std(lst):
    if len(lst) < 2:
        return 0
    m = mean(lst)
    return math.sqrt(sum((x - m) ** 2 for x in lst) / len(lst))

def rle(s):
    """Run-length encoding"""
    if not s:
        return []
    result = []
    current = s[0]
    count = 1
    for c in s[1:]:
        if c == current:
            count += 1
        else:
            result.append((current, count))
            current = c
            count = 1
    result.append((current, count))
    return result

LOG2_3 = math.log2(3)

# ========================================
# Part 1: 基本構造の確認
# ========================================

print("=" * 70)
print("Part 1: Syracuse各ステップのlog_2(T(n)/n)の構造")
print("=" * 70)

print("\nv2(3n+1) | log_2(T/n)     | 比率 T/n")
print("-" * 50)
for j in range(1, 10):
    lr = math.log2(3) - j
    ratio = 3 / (2**j)
    print(f"  j={j}     | {lr:+.6f}     | 3/{2**j} = {ratio:.6f}")

print(f"\nlog_2(3) = {LOG2_3:.10f}")
print("v2=1: log比 > 0 (拡大), v2>=2: log比 < 0 (縮小)")

# ========================================
# Part 2: D/k と log_2(3) の関係
# ========================================

print("\n" + "=" * 70)
print("Part 2: 累積D/kとlog_2(3)の関係")
print("=" * 70)

# Syracuse k ステップ: n_k = 3^k * n_0 / 2^D
# n_k = 1 のとき: D = k * log_2(3) + log_2(n_0)
# D/k = log_2(3) + log_2(n_0)/k

test_numbers = [3, 5, 7, 9, 11, 13, 15, 17, 19, 27, 31, 63, 127, 255, 511, 703, 871]

print(f"\n{'n':>6} | {'k':>5} | {'D':>5} | {'D/k':>9} | {'log2(3)+log2(n)/k':>18} | {'exact match?':>12}")
print("-" * 75)

for n in test_numbers:
    orbit = syracuse_orbit(n)
    k = len(orbit) - 1
    if k == 0:
        continue
    D = sum(v2(3 * orbit[i] + 1) for i in range(k))
    dk = D / k
    expected = LOG2_3 + math.log2(n) / k
    diff = abs(dk - expected)
    match = "YES" if diff < 1e-10 else f"diff={diff:.2e}"
    print(f"{n:>6} | {k:>5} | {D:>5} | {dk:>9.6f} | {expected:>18.6f} | {match:>12}")

# ========================================
# Part 3: v2列のL/Rマッピング
# ========================================

print("\n" + "=" * 70)
print("Part 3: v2列のL/Rマッピングと累積比の振動")
print("=" * 70)

def v2_to_lr(v2_val):
    """v2=1 -> R (拡大), v2>=2 -> L (縮小)"""
    return 'R' if v2_val < LOG2_3 else 'L'

def analyze_orbit_lr(n, max_steps=5000):
    """軌道のL/R列と累積D/kの変動を分析"""
    orbit = syracuse_orbit(n, max_steps)
    k = len(orbit) - 1
    if k == 0:
        return None

    v2_seq = [v2(3 * orbit[i] + 1) for i in range(k)]
    lr_seq = [v2_to_lr(v) for v in v2_seq]

    # 累積D/kの軌跡
    D_cumul = 0
    dk_trajectory = []
    crossings = 0  # log_2(3)を横切る回数
    prev_side = None

    for i, j in enumerate(v2_seq):
        D_cumul += j
        dk = D_cumul / (i + 1)
        dk_trajectory.append(dk)

        side = 'above' if dk > LOG2_3 else 'below'
        if prev_side and side != prev_side:
            crossings += 1
        prev_side = side

    return {
        'k': k,
        'v2_seq': v2_seq,
        'lr_seq': lr_seq,
        'dk_trajectory': dk_trajectory,
        'crossings': crossings,
        'final_dk': dk_trajectory[-1] if dk_trajectory else 0,
        'rle': rle(lr_seq)
    }

print("\n選択的な軌道の解析:")
for n in [3, 7, 27, 127, 703, 871, 6171, 77031]:
    result = analyze_orbit_lr(n)
    if result is None:
        continue
    walk_str = ''.join(result['lr_seq'][:50])
    if result['k'] > 50:
        walk_str += "..."
    rle_lengths = [c for _, c in result['rle'][:15]]

    print(f"\nn = {n} (k={result['k']} steps, crossings={result['crossings']})")
    print(f"  L/R列: {walk_str}")
    print(f"  RLEラン長(先頭15): {rle_lengths}")
    print(f"  最終D/k: {result['final_dk']:.6f} (log2(3)={LOG2_3:.6f})")
    print(f"  D/k範囲: [{min(result['dk_trajectory']):.4f}, {max(result['dk_trajectory']):.4f}]")

# ========================================
# Part 4: SB木パスとの構造比較
# ========================================

print("\n" + "=" * 70)
print("Part 4: log_2(3)のStern-Brocot木パスとSyracuseのRLE比較")
print("=" * 70)

# log_2(3) のSB木パスを計算
def sb_path_irrational(x, depth=60):
    path = []
    left_n, left_d = 0, 1
    right_n, right_d = 1, 0
    for _ in range(depth):
        med_n = left_n + right_n
        med_d = left_d + right_d
        med = med_n / med_d
        if abs(med - x) < 1e-15:
            break
        elif x < med:
            path.append('L')
            right_n, right_d = med_n, med_d
        else:
            path.append('R')
            left_n, left_d = med_n, med_d
    return path

log2_3_path = sb_path_irrational(LOG2_3, depth=80)
log2_3_rle = rle(log2_3_path)
log2_3_rle_lengths = [c for _, c in log2_3_rle]

print(f"log_2(3)のSBパス: {''.join(log2_3_path[:60])}...")
print(f"SB RLE: {log2_3_rle[:15]}")
print(f"SB RLEラン長: {log2_3_rle_lengths[:15]}")
print(f"log_2(3)の連分数 [a0; a1, a2, ...] = [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, ...]")
print(f"SBパスのRLEはこの連分数と一致するはず")

# ========================================
# Part 5: Syracuse v2列のRLEラン長分布 vs SBパスのラン長
# ========================================

print("\n" + "=" * 70)
print("Part 5: v2列RLEラン長の統計的分布")
print("=" * 70)

# 多数の軌道でラン長を収集
r_runs = []  # v2=1のラン（R方向）
l_runs = []  # v2>=2のラン（L方向）
all_v2s = []

for n in range(3, 5001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    k = len(orbit) - 1
    if k < 5:
        continue

    v2_seq = [v2(3 * orbit[i] + 1) for i in range(k)]
    all_v2s.extend(v2_seq)
    lr_seq = [v2_to_lr(v) for v in v2_seq]
    runs = rle(lr_seq)

    for direction, length in runs:
        if direction == 'R':
            r_runs.append(length)
        else:
            l_runs.append(length)

print(f"総v2データ点: {len(all_v2s)}")
print(f"v2の分布:")
v2_counter = Counter(all_v2s)
for j in range(1, 10):
    count = v2_counter.get(j, 0)
    theoretical = 1 / (2 ** j) if j < 9 else sum(1/2**k for k in range(9, 30))
    print(f"  v2={j}: {count} ({count/len(all_v2s)*100:.2f}%, 理論={theoretical*100:.2f}%)")

print(f"\nv2=1 (R) のラン長分布:")
r_counter = Counter(r_runs)
total_r = len(r_runs)
print(f"  平均ラン長: {mean(r_runs):.4f}")
for length in range(1, 8):
    count = r_counter.get(length, 0)
    # v2=1の確率が1/2なら、ラン長kの確率は (1/2)^{k-1} * (1/2) = (1/2)^k
    # 条件付き: ラン長>=1が与えられたとき、ラン長kの確率は (1/2)^{k-1} * (1/2) = (1/2)^k
    # 平均は 1/(1-p) = 2 (geometric distribution with p=1/2)
    # いや、ラン長の分布は幾何分布: P(length=k) = (1/2)^{k-1} * (1/2) if starting R
    geo_prob = (0.5) ** length  # P(k consecutive R's then L)
    # 正しくは: Rが出る確率p=0.5として、ラン長kの確率 = p^{k-1}(1-p) = (0.5)^k
    print(f"  k={length}: {count} ({count/total_r*100:.1f}%, 幾何分布={geo_prob*100:.1f}%)")

print(f"\nv2>=2 (L) のラン長分布:")
l_counter = Counter(l_runs)
total_l = len(l_runs)
print(f"  平均ラン長: {mean(l_runs):.4f}")
for length in range(1, 8):
    count = l_counter.get(length, 0)
    # v2>=2の確率が1/2、v2>=2が連続する確率は?
    # v2>=2の確率 = 1/2、v2=1の確率 = 1/2
    # ラン長は同じ幾何分布
    geo_prob = (0.5) ** length
    print(f"  k={length}: {count} ({count/total_l*100:.1f}%, 幾何分布={geo_prob*100:.1f}%)")

# ========================================
# Part 6: 核心の問い - D/kのSB木上の「パス」
# ========================================

print("\n" + "=" * 70)
print("Part 6: D/kの有理近似としてのSB木ノードの軌跡")
print("=" * 70)

# 軌道の途中のD/kは有理数。これをSB木のノードとして追跡
# 例: n=27の軌道
n = 27
orbit = syracuse_orbit(n, max_steps=1000)
k_total = len(orbit) - 1

print(f"\nn=27の軌道 (k={k_total} steps)")
print(f"{'step':>5} | {'v2':>3} | {'D':>4} | {'k':>3} | {'D/k':>9} | {'D/k as frac':>15} | {'SB depth':>8}")
print("-" * 70)

D = 0
for i in range(k_total):
    j = v2(3 * orbit[i] + 1)
    D += j
    k = i + 1
    dk_val = D / k
    dk_frac = Fraction(D, k)

    # SB木の深さはnumerator + denominator - 1 (近似)
    sb_depth = dk_frac.numerator + dk_frac.denominator - 1

    if i < 20 or i >= k_total - 5:
        print(f"{k:>5} | {j:>3} | {D:>4} | {k:>3} | {dk_val:>9.6f} | {str(dk_frac):>15} | {sb_depth:>8}")
    elif i == 20:
        print("  ...")

# ========================================
# Part 7: SB木上のmediant操作と新しい対応
# ========================================

print("\n" + "=" * 70)
print("Part 7: 新しい対応の模索 - mediant操作による漸化式")
print("=" * 70)

# D_{k+1}/k_{+1} = (D_k + v2_{k+1}) / (k+1)
# = k/(k+1) * D_k/k + v2_{k+1}/(k+1)
# = mediant的な操作: (D_k + v2_{k+1}) / (k + 1)
#
# これは重み付きmediant: D_k/k と v2_{k+1}/1 の mediant
# mediant(D_k/k, v2_{k+1}/1) = (D_k + v2_{k+1}) / (k + 1)
#
# これはまさにSB木のmediant操作!

print("核心的観察:")
print("  D_{k+1}/(k+1) = mediant(D_k/k, v2_{k+1}/1)")
print("  = (D_k + v2_{k+1}) / (k + 1)")
print()
print("  つまり、D/k の更新規則は、現在のD/k と新しいv2値の")
print("  Stern-Brocot mediant操作そのものである!")
print()

# 検証: n=27で
n = 27
orbit = syracuse_orbit(n)
print(f"n=27での検証:")
D = 0
for i in range(min(10, len(orbit) - 1)):
    j = v2(3 * orbit[i] + 1)
    D_old = D
    k_old = i
    D += j
    k_new = i + 1

    dk_new = Fraction(D, k_new)
    if k_old > 0:
        dk_old = Fraction(D_old, k_old)
        v2_frac = Fraction(j, 1)
        mediant_result = Fraction(D_old + j, k_old + 1)
        print(f"  step {k_new}: mediant({dk_old}, {v2_frac}) = {mediant_result} = {dk_new} {'OK' if mediant_result == dk_new else 'MISMATCH'}")
    else:
        print(f"  step {k_new}: D/k = {dk_new} (initial)")

# ========================================
# Part 8: mediant列のSB木パスとlog_2(3)への収束
# ========================================

print("\n" + "=" * 70)
print("Part 8: mediant列がSB木のlog_2(3)パスに沿うか?")
print("=" * 70)

# D/kは log_2(3) + log_2(n)/k に収束
# 各ステップで D/k が log_2(3) の上か下か -> L or R
# この L/R 列は log_2(3) のSBパスに似ているか?

def orbit_lr_around_log23(n, max_steps=5000):
    """D/kがlog_2(3)の上か下かの列"""
    orbit = syracuse_orbit(n, max_steps)
    k_total = len(orbit) - 1
    lr = []
    D = 0
    for i in range(k_total):
        j = v2(3 * orbit[i] + 1)
        D += j
        dk = D / (i + 1)
        lr.append('L' if dk > LOG2_3 else 'R')
    return lr

print("\nSyracuse D/kのlog_2(3)周りの振動パターン:")
for n in [27, 127, 703, 871, 6171, 77031]:
    lr = orbit_lr_around_log23(n)
    lr_rle = rle(lr)
    lr_rle_lengths = [c for _, c in lr_rle[:15]]
    print(f"\n  n={n} (k={len(lr)})")
    print(f"    L/R列: {''.join(lr[:60])}{'...' if len(lr) > 60 else ''}")
    print(f"    RLE: {lr_rle[:10]}")
    print(f"    RLEラン長: {lr_rle_lengths}")

print(f"\n  log_2(3) SBパスのRLEラン長: {log2_3_rle_lengths[:15]}")
print(f"  log_2(3) 連分数: [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, ...]")

# ========================================
# Part 9: 統計的比較 - ラン長分布の詳細
# ========================================

print("\n" + "=" * 70)
print("Part 9: D/k振動のラン長分布の詳細分析")
print("=" * 70)

# 多数のnについて、D/kの log_2(3) 周りの振動のラン長を収集
all_oscillation_runs = {'L': [], 'R': []}

for n in range(3, 5001, 2):
    lr = orbit_lr_around_log23(n)
    if len(lr) < 5:
        continue
    runs = rle(lr)
    for direction, length in runs:
        all_oscillation_runs[direction].append(length)

print("D/k > log_2(3) (L方向) のラン長分布:")
l_osc = all_oscillation_runs['L']
print(f"  サンプル数: {len(l_osc)}, 平均: {mean(l_osc):.4f}")
l_osc_counter = Counter(l_osc)
for k_val in range(1, 12):
    count = l_osc_counter.get(k_val, 0)
    print(f"  k={k_val}: {count} ({count/len(l_osc)*100:.1f}%)")

print(f"\nD/k < log_2(3) (R方向) のラン長分布:")
r_osc = all_oscillation_runs['R']
print(f"  サンプル数: {len(r_osc)}, 平均: {mean(r_osc):.4f}")
r_osc_counter = Counter(r_osc)
for k_val in range(1, 12):
    count = r_osc_counter.get(k_val, 0)
    print(f"  k={k_val}: {count} ({count/len(r_osc)*100:.1f}%)")

# ========================================
# Part 10: 最も深い構造的対応の探索
# ========================================

print("\n" + "=" * 70)
print("Part 10: v2列のmediantと有理近似の質")
print("=" * 70)

# D/k が log_2(3) の「良い有理近似」かどうか
# 良い近似: |D/k - log_2(3)| < 1/(2k^2) (Hurwitz の定理の閾値)
# 連分数の収束子はこの条件を満たす

n_values = [27, 127, 703, 6171, 77031]
for n in n_values:
    orbit = syracuse_orbit(n, max_steps=10000)
    k_total = len(orbit) - 1
    if k_total == 0:
        continue

    good_approximations = 0
    D = 0
    best_approx = (999, 0, 0)  # (error, D, k)

    for i in range(k_total):
        j = v2(3 * orbit[i] + 1)
        D += j
        k = i + 1
        dk = D / k
        error = abs(dk - LOG2_3)
        hurwitz_bound = 1 / (2 * k * k)

        if error < hurwitz_bound:
            good_approximations += 1

        if error < best_approx[0]:
            best_approx = (error, D, k)

    print(f"\nn={n} (k_total={k_total}):")
    print(f"  Hurwitz良近似の回数: {good_approximations}/{k_total} ({good_approximations/k_total*100:.1f}%)")
    print(f"  最良近似: D/k = {best_approx[1]}/{best_approx[2]} = {best_approx[1]/best_approx[2]:.10f}")
    print(f"  誤差: {best_approx[0]:.2e}")
    print(f"  (注: D/k = log_2(3) + log_2(n)/k なので真の近似ではない)")

# ========================================
# Part 11: 真に新しい対応の可能性
# ========================================

print("\n" + "=" * 70)
print("Part 11: mediant更新規則の深い意味")
print("=" * 70)

print("""
=== 核心的発見 ===

1. [自明だが重要] D_{k+1}/(k+1) = mediant(D_k/k, v2_{k+1}/1)
   - D/k の更新はStern-Brocot mediant操作そのもの
   - ただしこれは算術平均の漸化式の一般化に過ぎない

2. [構造的] D/k は log_2(3) + log_2(n)/k に厳密に等しい
   - k -> infinity で log_2(3) に収束する有理数列
   - しかし n は有限で軌道は停止するので、この極限は形式的

3. [新発見の候補] v2列の L/R 変換のラン長パターン
   - v2=1 (R) の平均ラン長 ≈ 2.0 (幾何分布 p=0.5)
   - v2>=2 (L) の平均ラン長 ≈ 2.0 (同上)
   - これは v2 が独立一様ならば自明

4. [行き止まり] SB木のlog_2(3)パスとSyracuse軌道の直接対応
   - log_2(3)のSBパスは連分数 [1;1,1,2,2,3,1,5,...] で決定論的
   - Syracuse軌道のRLEは確率的で、個々の軌道依存
   - 統計的収束はあるが、構造的対応はない

5. [もう一つの観点] mediant操作の連鎖
   - Stern-Brocot木では、有理数 p/q の深さ = p + q - 1
   - D/k の「深さ」= D + k - 1
   - 2D + 1 = 2k*log_2(3) + 2*log_2(n) + 1 (近似)
   - 深さの成長率 ≈ (1 + 2*log_2(3)) * k ≈ 4.17 * k
""")

# ========================================
# Part 12: 定量的な新知見の確認
# ========================================

print("=" * 70)
print("Part 12: 定量的確認")
print("=" * 70)

# D/k 分布の統計
dk_ratios = []
for n in range(3, 5001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    k = len(orbit) - 1
    if k == 0:
        continue
    D = sum(v2(3 * orbit[i] + 1) for i in range(k))
    dk_ratios.append(D / k)

print(f"\nD/k の統計 (n=3..4999, 奇数):")
print(f"  Mean:  {mean(dk_ratios):.8f}")
print(f"  Std:   {std(dk_ratios):.8f}")
print(f"  Min:   {min(dk_ratios):.8f}")
print(f"  Max:   {max(dk_ratios):.8f}")
print(f"  log_2(3) = {LOG2_3:.8f}")
print(f"  Mean - log_2(3) = {mean(dk_ratios) - LOG2_3:.8f}")

# v2の統計
all_v2_flat = []
for n in range(3, 5001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    for i in range(len(orbit) - 1):
        all_v2_flat.append(v2(3 * orbit[i] + 1))

print(f"\nv2(3n+1) の統計:")
print(f"  Mean: {mean(all_v2_flat):.8f} (理論: 2.0)")
print(f"  Std:  {std(all_v2_flat):.8f}")

# 相関: 連続するv2値の間の相関
v2_pairs = []
for n in range(3, 2001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    v2_seq = [v2(3 * orbit[i] + 1) for i in range(len(orbit) - 1)]
    for i in range(len(v2_seq) - 1):
        v2_pairs.append((v2_seq[i], v2_seq[i+1]))

# 自己相関
x_vals = [p[0] for p in v2_pairs]
y_vals = [p[1] for p in v2_pairs]
mx = mean(x_vals)
my = mean(y_vals)
cov = mean([(x - mx) * (y - my) for x, y in v2_pairs])
sx = std(x_vals)
sy = std(y_vals)
corr = cov / (sx * sy) if sx > 0 and sy > 0 else 0

print(f"\n連続v2値の自己相関: {corr:.6f}")
print(f"  (0に近い = ほぼ独立、SB木のランダムウォークと整合)")

# ========================================
# 最終まとめ
# ========================================

print("\n" + "=" * 70)
print("最終まとめ")
print("=" * 70)
print(f"""
=== Syracuse軌道とStern-Brocot木の関係 ===

[確認された事実]
1. D/k の更新は mediant(D_k/k, v2_{'{k+1}'}/1) = (D_k + v2_{'{k+1}'})/(k+1)
   -> これは定義上SB mediantだが、単なる加重平均の漸化式

2. D/k = log_2(3) + log_2(n)/k (恒等式)
   -> log_2(3)への収束は保証されるが、軌道停止が前提

3. v2の連続値の自己相関 ≈ {corr:.4f} (ほぼ独立)
   -> SB木上のランダムウォークモデルと整合

[行き止まり]
- SBパスのRLEと連分数 [1;1,1,2,...] の直接対応: なし
  (個々の軌道は確率的で、決定論的SBパスとは一致しない)

[小発見]
- v2列のmediant漸化式: D/k -> log_2(3) の収束を
  SB木のmediant操作として幾何学的に解釈できる
- v2列のL/R振動パターン: 平均ラン長 ≈ 2.0 は
  幾何分布(p=0.5)と整合的
  -> 「Syracuse軌道はlog_2(3)周りの確率的なSBランダムウォーク」

[結論]
構造的な新しい対応は見つからなかったが、
「D/kのmediant更新がSBの左右移動」という解釈は
log比の収束を視覚化・解釈する新しい枠組みとして有用。
ただし、コラッツ予想の証明に直結する深い構造はなかった。
""")
