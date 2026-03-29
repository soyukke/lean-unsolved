"""
Syracuse軌道の合流統計: 理論的まとめ

1. 合流時間 ~ 3.42 * log2(N) のスケーリング法則の理論的裏付け
2. n=5漏斗の定量的特徴付け
3. 50ステップ以内の完全合流の意味
4. 合流点のmod構造の理論的説明
"""

import math
from collections import defaultdict, Counter

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=500):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    trajectory = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        trajectory.append(current)
    return trajectory

# ===== 理論1: スケーリング定数の意味 =====
print("=" * 70)
print("理論1: スケーリング定数 c ≈ 3.42 の意味")
print("=" * 70)

# Syracuse の1ステップ平均縮小率
# T(n) のログ変化量: E[log2(T(n)/n)] = log2(3/2) - E[v2(3n+1)] * log2(2) + ...
# ヒューリスティック: E[log2(T(n))] ≈ log2(n) + log2(3/2) - 1 ≈ log2(n) - 0.415
# よって 1ステップで log2 が約 0.415 減少 (平均)

# 2つの独立ランダムウォーカーが同じ点に到達するまでの期待時間は
# 1次元で E[T] ∝ (初期距離)^2 / D だが、
# ここではログスケールでの距離 ≈ log2(|n1-n2|)
# 各ステップで log2 が独立に減少 → 実効的にはログスケールで収縮

shrink_rates = []
for n in range(3, 10001, 2):
    t = syracuse(n)
    shrink = math.log2(t / n) if t > 0 else 0
    shrink_rates.append(shrink)

avg_shrink = sum(shrink_rates) / len(shrink_rates)
var_shrink = sum((r - avg_shrink)**2 for r in shrink_rates) / len(shrink_rates)
print(f"E[log2(T(n)/n)]: {avg_shrink:.6f}")
print(f"Var[log2(T(n)/n)]: {var_shrink:.6f}")
print(f"理論値 E = log2(3/4) = {math.log2(3/4):.6f}")
print(f"(3/4 = 3/(2*E[2^v2]) where E[2^v2]=2)")

# 合流のための条件: 2つの軌道が同じ値を取る
# 軌道の値は log スケールで [0, log2(n)] の中を拡散
# 合流は「2つの軌道が同じ bin に入る」確率で決まる
# bin の数 ≈ n (各奇数が1つのbin) → 誕生日パラドックス

# 隣接数の合流: |n1-n2|=2, log2(n1/n2) ≈ 2/n → 小さい
# 初期の軌道はほぼ同じ → 分岐してから再合流までの時間が支配的

print(f"\n--- 理論的解釈 ---")
print(f"合流時間 ≈ 3.42 * log2(N) の物理的意味:")
print(f"  - Syracuse軌道は平均 log2(3/4) ≈ -0.415 のドリフト")
print(f"  - log2(N) のオーダーの停止時間で1に到達")
print(f"  - 2つの軌道が合流するには停止時間のかなりの部分が必要")
print(f"  - 比率 3.42 / (1/0.415) ≈ 3.42 / 2.41 ≈ 1.42")
print(f"  - つまり停止時間の約 1.42 倍が合流時間の良い推定")

# ===== 理論2: 5への漏斗の完全な特徴付け =====
print("\n" + "=" * 70)
print("理論2: 5への漏斗の完全な特徴付け")
print("=" * 70)

# 軌道が5を通る確率が94%超の理由
# 1. T(5)=1 なので5は1の直前
# 2. 1に到達するには必ず5を通るか? → No. T(1)=1なので1→1のループだが
#    初めて1に到達するとき、直前が5とは限らない
# 3. T(m)=1 となる m は: m such that (3m+1)/2^v2(3m+1) = 1
#    3m+1 = 2^a → m = (2^a - 1)/3
#    a=2: m=1, a=4: m=5, a=6: m=21, a=8: m=85, a=10: m=341

m_to_1 = []
for a in range(2, 30, 2):
    val = (2**a - 1)
    if val % 3 == 0:
        m = val // 3
        if m % 2 == 1:
            m_to_1.append((m, a))

print("T(m) = 1 となる奇数 m:")
for m, a in m_to_1[:10]:
    print(f"  m = {m} (a={a})")

# これらのうち、5を通らずに1に到達するもの
print(f"\n5を通らずに1に到達する奇数 (N<=5000):")
count_no5 = 0
examples_no5 = []
for n in range(3, 5001, 2):
    orb = orbit(n, 500)
    if 1 in orb and 5 not in orb[:-1]:  # 軌道に5が含まれない
        count_no5 += 1
        if len(examples_no5) < 20:
            examples_no5.append(n)

print(f"  総数: {count_no5}/2499 ({100*count_no5/2499:.1f}%)")
print(f"  例: {examples_no5}")

# 5を通らないものの特徴を確認
for n in examples_no5[:5]:
    orb = orbit(n, 20)
    print(f"  orbit({n}) = {orb}")

# ===== 理論3: 合流点の mod 3 バイアス =====
print("\n" + "=" * 70)
print("理論3: 合流点の mod 3 偏り (23% vs 77%)")
print("=" * 70)

# mod 3 = 0 は不可能 (Syracuse は mod 3 = 0 を出力しない)
# T(n) ≡ 0 (mod 3) は起きない: T(n) = (3n+1)/2^v ≡ 1/2^v (mod 3)
# v が偶数 → 1/1 ≡ 1, v が奇数 → 1/2 ≡ 2 (mod 3)
# つまり T(n) mod 3 = 1 if v2(3n+1) even, = 2 if v2(3n+1) odd

# v2(3n+1) の偶奇分布
v2_parity = Counter()
for n in range(1, 10001, 2):
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    v2_parity[v % 2] += 1

print(f"v2(3n+1) の偶奇分布 (n=1..9999 odd):")
print(f"  偶数: {v2_parity[0]} ({100*v2_parity[0]/(v2_parity[0]+v2_parity[1]):.1f}%)")
print(f"  奇数: {v2_parity[1]} ({100*v2_parity[1]/(v2_parity[0]+v2_parity[1]):.1f}%)")

# v2 の分布
v2_dist = Counter()
for n in range(1, 10001, 2):
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    v2_dist[v] += 1

print(f"\nv2(3n+1) の分布:")
for v in sorted(v2_dist.keys()):
    pct = 100 * v2_dist[v] / 5000
    theory = 100 / 2**v
    print(f"  v={v}: {v2_dist[v]} ({pct:.1f}%) [理論: {theory:.1f}%]")

print(f"\nよって:")
print(f"  T(n) mod 3 = 1 の確率: v2偶数の確率 = sum 1/2^(2k) = 1/(1-1/4) * (1/4) ≈ 1/3")
print(f"  T(n) mod 3 = 2 の確率: v2奇数の確率 ≈ 2/3")
print(f"  → 合流点の mod 3 偏りは Syracuse 関数の出力 mod 3 偏りの直接的帰結")
print(f"  実測: mod3=1 が 23.3%, mod3=2 が 76.7% (理論: 33% vs 67%)")
print(f"  偏りがさらに強い理由: 合流点は軌道が長い値ほど多く出現 → 定常分布の偏り")

# ===== 理論4: 50ステップ完全合流の意味 =====
print("\n" + "=" * 70)
print("理論4: 50ステップ以内の完全合流")
print("=" * 70)

# N=300の全ペアが50ステップで合流
# 停止時間の最大値を確認
max_st = 0
max_n = 0
for n in range(3, 301, 2):
    orb = orbit(n, 500)
    st = len(orb) - 1
    if st > max_st:
        max_st = st
        max_n = n

print(f"N=300以下の奇数の最大停止時間: {max_st} (n={max_n})")
print(f"orbit({max_n}) 長さ: {max_st}")
orb_max = orbit(max_n, 500)
print(f"orbit({max_n}) = {orb_max}")

# 合流時間 ≤ max(st(n1) + st(n2)) が自明な上界
# 実際にはもっと早く合流する

# ===== 理論5: 合流時間分布の二峰性の完全な説明 =====
print("\n" + "=" * 70)
print("理論5: 二峰性分布の構造")
print("=" * 70)
print("合流時間分布のピークは2つ:")
print("  第1ピーク: steps ≈ 10-14 (合流点 != 5)")
print("    → 軌道の初期部分で早期に合流。主に小さい合流点。")
print("  第2ピーク: steps ≈ 45-49 (合流点 = 5)")
print("    → n=5は「最後から2番目」のため、ほぼ停止時間に近い時間がかかる")
print("")
print("メカニズム:")
print("  94%の軌道が5を通る → 大半のペアは「5で合流するか、それ以前で合流するか」")
print("  以前に合流 → 第1ピーク (早い合流)")
print("  5まで合流しない → 第2ピーク (遅い合流、≈ 停止時間)")
print("")

# 合流点が5の場合、steps1とsteps2の関係
print("合流点=5のとき: steps = 停止時間(n1→5) + 停止時間(n2→5) - 共通部分")
# 5への到達時間の分布
times_to_5 = []
for n in range(3, 501, 2):
    orb = orbit(n, 500)
    for i, v in enumerate(orb):
        if v == 5:
            times_to_5.append(i)
            break

if times_to_5:
    import statistics
    print(f"\n5への到達時間分布 (N=500の奇数):")
    print(f"  平均: {statistics.mean(times_to_5):.1f}")
    print(f"  中央値: {statistics.median(times_to_5):.0f}")
    print(f"  最大: {max(times_to_5)}")

print("\n" + "=" * 70)
print("全理論分析完了")
print("=" * 70)
