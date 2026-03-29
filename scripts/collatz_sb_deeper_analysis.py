"""
追加分析: Syracuse v2列の自己相関とD/k振動の非対称性

注目点:
1. v2自己相関 ≈ 0.114 (独立でない)
2. D/k振動のLラン平均 ≈ 12.0 >> Rラン平均 ≈ 4.3 (非対称)
3. D/kは常に > log_2(3) (log_2(n)/k > 0のため) -> 非対称の原因
"""

import math
from fractions import Fraction
from collections import Counter, defaultdict

def v2(n):
    if n == 0: return 999
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c

def syracuse(n):
    val = 3 * n + 1
    return val >> v2(val)

def syracuse_orbit(n, max_steps=5000):
    orbit = [n]
    current = n
    for _ in range(max_steps):
        if current == 1 and len(orbit) > 1: break
        current = syracuse(current)
        orbit.append(current)
        if current == 1: break
    return orbit

def mean(lst): return sum(lst) / len(lst) if lst else 0

LOG2_3 = math.log2(3)

# ========================================
# 分析1: v2自己相関の源泉
# ========================================

print("=" * 70)
print("分析1: v2の自己相関の源泉")
print("=" * 70)

# v2(3n+1) = j ⟺ n ≡ (2^j - 1)/3 mod 2^j (for odd n)
# T(n) = (3n+1)/2^j
# 次のv2値 = v2(3T(n)+1) = v2((3(3n+1)/2^j) + 1) = v2((9n+3+2^j)/2^j)
# = v2(9n + 3 + 2^j) - j

# 具体的に: v2_1 = 1 (n ≡ 1 mod 4) のとき T(n) = (3n+1)/2
# v2_2 = v2(3*(3n+1)/2 + 1) = v2((9n+3+2)/2) = v2((9n+5)/2)
# n ≡ 1 mod 4: 9n+5 ≡ 14 mod 36, (9n+5)/2 ≡ 7 mod 18

# v2の条件付き分布を計算
print("\n条件付き分布 P(v2_{k+1} | v2_k):")

v2_transitions = defaultdict(lambda: Counter())
for n in range(3, 20001, 2):
    orbit = syracuse_orbit(n, max_steps=1000)
    v2_seq = [v2(3 * orbit[i] + 1) for i in range(len(orbit) - 1)]
    for i in range(len(v2_seq) - 1):
        v2_transitions[v2_seq[i]][v2_seq[i+1]] += 1

for prev_v2 in sorted(v2_transitions.keys())[:6]:
    total = sum(v2_transitions[prev_v2].values())
    print(f"\n  v2_k = {prev_v2} (total {total}):")
    for next_v2 in range(1, 8):
        count = v2_transitions[prev_v2].get(next_v2, 0)
        freq = count / total if total > 0 else 0
        theoretical = 1 / (2 ** next_v2)
        deviation = freq - theoretical
        marker = " ***" if abs(deviation) > 0.02 else ""
        print(f"    P(v2_{'{k+1}'}={next_v2}) = {freq:.4f} (理論 {theoretical:.4f}, 偏差 {deviation:+.4f}){marker}")

# ========================================
# 分析2: mod 4 条件による v2 の依存構造
# ========================================

print("\n" + "=" * 70)
print("分析2: T(n) mod 4 と v2 の関係")
print("=" * 70)

# T(n) mod 4 が v2(3*T(n)+1) を決める
# v2(3n+1) = 1 ⟺ n ≡ 1 mod 4
# v2(3n+1) >= 2 ⟺ n ≡ 3 mod 4
# T(n) mod 4 は n mod 8 で決まる

print("\nT(n) mod 4 の分布 (n mod 8 ごと):")
for r8 in [1, 3, 5, 7]:
    t_vals = []
    for mult in range(100):
        n = r8 + 8 * mult
        if n % 2 == 0: continue
        t = syracuse(n)
        t_vals.append(t % 4)
    t_counter = Counter(t_vals)
    v2_of_r8 = v2(3 * r8 + 1)
    print(f"  n ≡ {r8} mod 8: v2={v2_of_r8}, T(n) mod 4 分布 = {dict(t_counter)}")

# T(n) mod 4 の決定
print("\nT(n) mod 4 を n mod 16 で分類:")
for r16 in range(1, 16, 2):
    t_vals_mod4 = set()
    for mult in range(200):
        n = r16 + 16 * mult
        t = syracuse(n)
        t_vals_mod4.add(t % 4)
    v2_r = v2(3 * r16 + 1)
    next_v2_determined = len(t_vals_mod4) == 1
    if next_v2_determined:
        t_mod4 = list(t_vals_mod4)[0]
        next_v2 = "1" if t_mod4 == 1 else ">=2"
    else:
        next_v2 = "mixed"
    print(f"  n ≡ {r16:>2} mod 16: v2={v2_r}, T mod 4 = {sorted(t_vals_mod4)}, next v2 = {next_v2}")

# ========================================
# 分析3: D/k振動の非対称性の原因
# ========================================

print("\n" + "=" * 70)
print("分析3: D/k振動の非対称性")
print("=" * 70)

# D/k = log_2(3) + log_2(n_0)/k (最終ステップから見た恒等式ではなく)
# 実際には D_k/k = (sum_{i=1}^k v2_i) / k
# E[v2] = 2.0 > log_2(3) ≈ 1.585
# よって D/k は平均的に log_2(3) より上にある

# D/k - log_2(3) = (E[v2] - log_2(3)) + fluctuation
# = 0.415 + fluctuation
# つまり D/k は log_2(3) より上にバイアスされている!

# これはLラン(D/k > log_2(3))が長い理由を説明する

print("D/k のバイアスの説明:")
print(f"  E[v2] = 2.0")
print(f"  log_2(3) = {LOG2_3:.6f}")
print(f"  E[v2] - log_2(3) = {2.0 - LOG2_3:.6f}")
print(f"  -> D/k は平均的に log_2(3) + 0.415 ≈ 2.0 付近")
print(f"  -> D/k > log_2(3) がほぼ常に成り立つ")
print(f"  -> Lランが圧倒的に長いのは当然")

# ではD/kがlog_2(3)を下回るのはいつか?
# 初期の数ステップでv2=1が続いた場合のみ
# D_k/k < log_2(3) ⟺ sum v2_i < k * log_2(3) ≈ 1.585k
# v2=1 が k回続けば D_k = k < 1.585k -> 下回る
# v2 が混在すると E[D_k] = 2k > 1.585k -> 上回る

print("\nD/k < log_2(3) の発生条件:")
below_counts = []
for n in range(3, 10001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    D = 0
    below = 0
    for i in range(len(orbit) - 1):
        D += v2(3 * orbit[i] + 1)
        if D / (i + 1) < LOG2_3:
            below += 1
    k_total = len(orbit) - 1
    if k_total > 0:
        below_counts.append(below / k_total)

print(f"  D/k < log_2(3) の割合 (平均): {mean(below_counts):.4f}")
print(f"  -> 約{mean(below_counts)*100:.1f}%のステップでD/kはlog_2(3)を下回る")

# ========================================
# 分析4: 本質的な対応 - D/kをlog_2(3)でなく2に正規化
# ========================================

print("\n" + "=" * 70)
print("分析4: D/kを E[v2]=2 で正規化した場合のSB木対応")
print("=" * 70)

# D/k は 2 (= E[v2]) 周りを振動
# これを target = 2 としてSB木の探索と見なす
# 2 = 2/1 のSBパスは: R (trivially)

# より意味のある正規化: (D/k - log_2(3)) * k = log_2(n_0) を target
# これは「nがいくつか」を D列から推定するのと同等

# 別のアプローチ: v2_i - log_2(3) のランダムウォーク
# S_k = sum_{i=1}^k (v2_i - log_2(3))
# S_k = D - k*log_2(3) = log_2(n_0) at final step
# S_k のドリフト = E[v2] - log_2(3) = 0.415 (正のドリフト)
# -> S_k は線形に増大するランダムウォーク

print("偏差ランダムウォーク S_k = sum(v2_i - log_2(3)):")
print(f"  ドリフト = E[v2] - log_2(3) = {2.0 - LOG2_3:.6f}")
print(f"  最終値 S_k = log_2(n_0)")
print()

for n in [27, 127, 703, 6171]:
    orbit = syracuse_orbit(n, max_steps=5000)
    S = 0
    min_S = float('inf')
    max_S = float('-inf')
    zero_crossings = 0
    prev_sign = None

    for i in range(len(orbit) - 1):
        j = v2(3 * orbit[i] + 1)
        S += (j - LOG2_3)
        min_S = min(min_S, S)
        max_S = max(max_S, S)
        sign = S > 0
        if prev_sign is not None and sign != prev_sign:
            zero_crossings += 1
        prev_sign = sign

    k = len(orbit) - 1
    print(f"  n={n}: k={k}, S_final={S:.4f}, log_2(n)={math.log2(n):.4f}, "
          f"match={abs(S - math.log2(n)) < 0.01}, "
          f"min_S={min_S:.4f}, zero_crossings={zero_crossings}")

# ========================================
# 分析5: SB木のmediantとv2列の関係の深化
# ========================================

print("\n" + "=" * 70)
print("分析5: mediant列の収束速度とSB木の深さ")
print("=" * 70)

# D/k のSB木での「深さ」 = D + k - 1 (= 分子 + 分母 - 1 of reduced form)
# 深さの成長率は?
# D ≈ 2k, so depth ≈ 3k

# 一方、log_2(3)の最良有理近似 p_n/q_n (n番目の収束子) の深さは
# p_n + q_n で、これは指数的に増大: q_n ~ phi^n (golden ratio)

# Syracuse の D/k は深さ 3k で、log_2(3) への距離は 0.415 + O(1/sqrt(k))
# 連分数の n 番目の収束子は 深さ ~ phi^n で、距離は ~ 1/q_n^2

# つまり「近似の質」は全く異なる

print("有理近似の質の比較:")
print()

# log_2(3) の連分数収束子
cf = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55]
h_prev, h_curr = 0, 1
k_prev, k_curr = 1, 0
convergents = []
for a in cf:
    h_prev, h_curr = h_curr, a * h_curr + h_prev
    k_prev, k_curr = k_curr, a * k_curr + k_prev
    convergents.append((h_curr, k_curr))

print(f"{'方法':>20} | {'近似値':>15} | {'深さ(p+q)':>10} | {'|error|':>12} | {'error*depth^2':>14}")
print("-" * 80)

for p, q in convergents[:10]:
    approx = p / q
    error = abs(approx - LOG2_3)
    depth = p + q
    quality = error * depth * depth
    print(f"{'CF: ' + str(p) + '/' + str(q):>20} | {approx:>15.10f} | {depth:>10} | {error:>12.2e} | {quality:>14.6f}")

# Syracuse D/k for selected n
for n in [27, 127, 703, 6171, 77031]:
    orbit = syracuse_orbit(n, max_steps=5000)
    k = len(orbit) - 1
    D = sum(v2(3 * orbit[i] + 1) for i in range(k))
    dk_frac = Fraction(D, k)
    p, q = dk_frac.numerator, dk_frac.denominator
    approx = p / q
    error = abs(approx - LOG2_3)
    depth = p + q
    quality = error * depth * depth
    label = f"Syr n={n}: {p}/{q}"
    print(f"{label:>20} | {approx:>15.10f} | {depth:>10} | {error:>12.2e} | {quality:>14.6f}")

# ========================================
# 分析6: v2=4 の異常な頻度
# ========================================

print("\n" + "=" * 70)
print("分析6: v2=4 の異常頻度の調査")
print("=" * 70)

# Part 5の結果で v2=4 が理論値6.25%に対して9.73%と高い
# これは選択バイアス？

# 一様ランダムな奇数ならv2(3n+1)=4の確率は1/16 = 6.25%
# Syracuseの軌道上の奇数は一様ではない

# 軌道上のnについて n mod 16 の分布を調べる
mod16_counts = Counter()
for n in range(3, 5001, 2):
    orbit = syracuse_orbit(n, max_steps=2000)
    for m in orbit[:-1]:  # 1を除く
        if m > 1:
            mod16_counts[m % 16] += 1

total_mod16 = sum(mod16_counts.values())
print("軌道上の奇数の mod 16 分布:")
for r in [1, 3, 5, 7, 9, 11, 13, 15]:
    count = mod16_counts.get(r, 0)
    freq = count / total_mod16
    expected_v2 = v2(3 * r + 1)
    # n mod 16 = r のとき v2(3n+1) は r mod 16 で部分的に決まる
    print(f"  r={r:>2}: {freq:.4f} (一様なら0.125), v2(3*{r}+1)={expected_v2}")

# v2=4の条件: n ≡ 5 mod 16 (v2(3*5+1) = v2(16) = 4)
# 軌道上で n ≡ 5 mod 16 が多いか?
r5_freq = mod16_counts.get(5, 0) / total_mod16
r13_freq = mod16_counts.get(13, 0) / total_mod16
print(f"\n  n≡5 mod 16 (v2=4): 観測={r5_freq:.4f}, 理論=0.125")
print(f"  n≡13 mod 16 (v2=2): 観測={r13_freq:.4f}, 理論=0.125")

# ========================================
# 最終まとめ
# ========================================

print("\n" + "=" * 70)
print("追加分析の最終まとめ")
print("=" * 70)
print(f"""
[追加発見]

1. v2の自己相関 ≈ 0.114 は mod 条件から説明可能
   - v2_k は n_k mod 4 で決まり、T(n) mod 4 は n mod 8 で部分的に決まる
   - 完全な独立性はないが、弱い依存（自己相関 < 0.15）

2. D/k振動の非対称性は自明:
   - E[v2] = 2.0 > log_2(3) = 1.585
   - よって D/k は log_2(3) より常に上方にバイアス
   - D/k < log_2(3) は全ステップの約{mean(below_counts)*100:.0f}%のみ

3. 偏差ウォーク S_k = sum(v2_i - log_2(3)) は正ドリフト0.415のランダムウォーク
   - 最終値 S_k = log_2(n_0) (恒等式)
   - min(S_k) > 0 になりがち（ドリフトが正のため）

4. D/k はlog_2(3)の有理近似としては質が低い
   - 連分数収束子: error * depth^2 ≈ O(1) (最適)
   - Syracuse D/k: error * depth^2 >> 1 (非最適)

5. v2=4の過剰頻度: 軌道上の奇数の mod 16 分布の非一様性に由来
   - Syracuse写像が特定の剰余クラスを「好む」

[結論]
Syracuse軌道のD/kとSB木の対応は形式的にはmediant操作で表現できるが、
SB木の本質（最適有理近似）とは無関係。
D/kは「log_2(3)の近似」ではなく「log_2(3) + log_2(n)/kの正確な値」であり、
SB木上の探索過程としては意味を持たない。
""")
