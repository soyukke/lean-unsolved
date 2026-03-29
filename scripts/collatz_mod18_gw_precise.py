#!/usr/bin/env python3
"""
有限N→∞極限での正確な平均入次数の理論導出

問題: N→∞で有限N平均入次数は 5/6 に収束するように見えるが、
      理論値は 4/3。この矛盾を解明する。

鍵: 有限[1,N]での制限と、真の無限逆像ツリーの違い
"""

import math
from collections import Counter

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    assert n > 0 and n % 2 == 1
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse(m, N_bound):
    results = []
    j = 1
    while True:
        numerator = m * (1 << j) - 1
        if numerator // 3 > N_bound:
            break
        if numerator % 3 == 0:
            n = numerator // 3
            if n > 0 and n % 2 == 1:
                results.append((n, j))
        j += 1
    return results

print("=" * 60)
print("有限N平均入次数 vs 理論値 4/3 の精密解析")
print("=" * 60)

# ============================================================
# 1. 正確な測定: 入次数の2種類の定義
# ============================================================

print("\n[1] 入次数の2種類の定義")
print("  定義A: |{n in [1,N]_odd : T(n) = m}| / |[1,N]_odd|")
print("  定義B: |T^{-1}(m) 全体| (無限) → これが 4/3 on average")

# 定義Aは有限制限、定義Bは無限

# 定義Aの正確な値
print("\n[2] 定義Aの正確な計算")

for N in [1000, 10000, 100000]:
    total_odd = (N + 1) // 2

    # 方法1: 各m の逆像を数える
    total_pre = 0
    for m in range(1, N+1, 2):
        total_pre += len(inverse_syracuse(m, N))

    # 方法2: 各n でT(n)がN以下か数える
    count_tn_in_range = 0
    count_tn_out = 0
    for n in range(1, N+1, 2):
        m = syracuse(n)
        if 1 <= m <= N:
            count_tn_in_range += 1
        else:
            count_tn_out += 1

    avg_A = total_pre / total_odd
    out_frac = count_tn_out / total_odd

    print(f"  N={N}: avg_A={avg_A:.6f}, |T(n)>N|/total={out_frac:.6f}")
    print(f"    total_pre={total_pre}, count_in={count_tn_in_range}, count_out={count_tn_out}")
    print(f"    avg_A = 1 - out_frac = {1 - out_frac:.6f} ???")

# ============================================================
# 2. T(n) > N となる n の分析
# ============================================================

print("\n[3] T(n) > N となる n の特徴（N=10000）")
N = 10000
out_of_range = []
for n in range(1, N+1, 2):
    m = syracuse(n)
    if m > N:
        out_of_range.append((n, m, m/n, n%6, v2(3*n+1)))

print(f"  T(n)>N の個数: {len(out_of_range)} / {(N+1)//2} = {len(out_of_range)/((N+1)//2):.4f}")

# mod 6 分布
mod6_dist = Counter(x[3] for x in out_of_range)
print(f"  mod 6 分布: {dict(mod6_dist)}")

# v2(3n+1) 分布
v2_dist = Counter(x[4] for x in out_of_range)
print(f"  v2(3n+1) 分布: {dict(sorted(v2_dist.items()))}")

# n のサイズ分布
print(f"  n の範囲:")
ranges = [(1, N//4), (N//4, N//2), (N//2, 3*N//4), (3*N//4, N)]
for lo, hi in ranges:
    cnt = sum(1 for x in out_of_range if lo <= x[0] <= hi)
    print(f"    [{lo}, {hi}]: {cnt}")

# T(n)/n 分布
print(f"  T(n)/n の統計:")
ratios = [x[2] for x in out_of_range]
if ratios:
    print(f"    min={min(ratios):.4f}, max={max(ratios):.4f}, avg={sum(ratios)/len(ratios):.4f}")

# ============================================================
# 3. 正しい理論: なぜ 5/6 であって 4/3 ではないか
# ============================================================

print("\n[4] 理論的説明")
print("""
  核心的な区別:

  (A) |T^{-1}(m) ∩ [1,N]| の m∈[1,N]_odd での平均 → 5/6 (N→∞)

  (B) Σ_{m odd} |T^{-1}(m) ∩ [1,N]| / (N/2) =
      |{n ∈ [1,N]_odd : T(n) ∈ odd}| / (N/2) = 1 - ε(N)
      ここで ε(N) = |{n : T(n) > N}| / (N/2) → 1/6 ?

  確認: T(n) > N となる割合は...
""")

# T(n) > N の割合の N 依存性
print("  T(n)>N の割合:")
for N in [100, 1000, 10000, 100000]:
    total = (N+1)//2
    out = sum(1 for n in range(1, N+1, 2) if syracuse(n) > N)
    print(f"    N={N}: {out}/{total} = {out/total:.6f}")

# ============================================================
# 4. 正確な理論: m に対する合計 vs m のカウント方法
# ============================================================

print("\n[5] 入次数合計と平均の区別")

for N in [10000, 50000, 100000]:
    total_odd = (N+1)//2
    # 合計逆像数 = [1,N] で T(n)がoddな n の数
    # （すべての奇数 n に対して T(n) は奇数なので = total_odd - out_count）
    out = sum(1 for n in range(1, N+1, 2) if syracuse(n) > N)
    in_count = total_odd - out

    # 平均入次数（全奇数で割る）
    avg_all = in_count / total_odd

    # 像集合のサイズ
    image_set = set()
    for n in range(1, N+1, 2):
        m = syracuse(n)
        if m <= N:
            image_set.add(m)

    # 像は [1,N]_odd の何割か
    image_frac = len(image_set) / total_odd

    # 「像に入る m」での平均入次数
    avg_on_image = in_count / len(image_set) if image_set else 0

    print(f"  N={N}:")
    print(f"    合計逆像 / 全奇数 = {in_count}/{total_odd} = {avg_all:.6f}")
    print(f"    像サイズ / 全奇数 = {len(image_set)}/{total_odd} = {image_frac:.6f}")
    print(f"    合計逆像 / 像サイズ = {in_count}/{len(image_set)} = {avg_on_image:.6f}")
    print(f"    4/3 = {4/3:.6f}")

# ============================================================
# 5. 像の3/8公式の検証
# ============================================================

print("\n[6] 像サイズの理論検証")
print("  像 = T([1,N]_odd ∩ {n:T(n)≤N}) の [1,N]_odd での密度")

for N in [10000, 50000, 100000, 500000]:
    total_odd = (N+1)//2
    image_set = set()
    for n in range(1, N+1, 2):
        m = syracuse(n)
        if m <= N:
            image_set.add(m)

    frac = len(image_set) / total_odd
    print(f"  N={N}: |Image|={len(image_set)}, |Image|/|Odd|={frac:.6f}")

# ============================================================
# 6. 理論値 4/3 の正しい解釈
# ============================================================

print("\n[7] 理論値 4/3 の正しい解釈")
print("""
  4/3 は「像サイズ」に対する平均入次数:

  (全 n ∈ [1,N]_odd) / (像 m ∈ [1,N]_odd) → 4/3 ではない

  実際の 4/3 は:
  像のサイズ = 3N/8 (mod 3 ≠ 0 の奇数は 2N/3 個、mod 6 ≡ 3 は入次数0)
  ...ではない。

  正確には:
  |{n odd ≤ N : T(n) odd ≤ N}| / N → ?
  |{m odd}| → N/2

  真の 4/3 = 逆像の漸近密度:
  固定 m に対して |T^{-1}(m) ∩ [1,N]| / (N/m) → ?

  あるいは:
  Σ_{m odd ≤ M} |T^{-1}(m)∩[1,N]| / M → ? as M,N→∞ jointly
""")

# 固定 m に対する |T^{-1}(m) ∩ [1,N]| の成長
print("[8] 固定 m に対する逆像数の N 成長")
for m in [1, 5, 7, 11]:
    print(f"  m={m}: ", end="")
    for N in [100, 1000, 10000, 100000, 1000000]:
        cnt = len(inverse_syracuse(m, N))
        logN = math.log2(N) if N > 0 else 0
        print(f"N={N}:{cnt}(log2N/2={logN/2:.1f}) ", end="")
    print()

print("\n  → 固定 m に対し |T^{-1}(m) ∩ [1,N]| ∼ log_4(N/m)")
print("  → N→∞ で無限大。だから「平均入次数」は有限にならない！")
print("  → 4/3 は「密度」の意味: Σ|T^{-1}(m)∩[1,N]| / (N/2) → 1")
print("     ここで各 n は正確に1つの m に写る")

# ============================================================
# 7. GW接続の正しい理論
# ============================================================

print("\n[9] GW過程接続の正しい定式化")
print("""
  GW過程としてのモデル化:

  1. 逆BFSツリーで各層の「成長率」が 4/3
     → 実測: depth 増加で成長率は 4/3 に収束しない?
     → 実測では収束が遅い（有限N効果）

  2. 正しいGWモデル:
     奇数 m を「粒子」とする。
     m の「子孫」= T^{-1}(m) の元（範囲制限なし）

     しかし T^{-1}(m) は無限集合（j→∞）!
     → 各 m に対して無限の逆像がある
     → これはGW過程ではない!

  3. 修正GWモデル:
     j を制限して逆像を定義:
     T_j^{-1}(m) = {n : T(n)=m, v2(3n+1)=j}

     これは各 j で高々1つの逆像（n = (m*2^j-1)/3）
     → 確率 p ≈ 1/2 で逆像が存在（j の偶奇条件 + 奇数条件）

     しかし j を固定するとGWにならない。

  4. Tao (2019) のアプローチ:
     Syracuse写像のランダムモデル:
     T(n) = (3n+1)/2^{V} where V ∼ Geom(1/2)

     平均収縮率: E[3/(2^V)] = 3 * E[1/2^V] = 3 * (1/2)/(1-1/2) = 3
     ...ではなく E[log(3/2^V)] = log3 - E[V]*log2 = log3 - 2*log2 < 0

     → 対数的には平均収縮（ほぼすべての軌道が十分小さくなる）
""")

# Tao のランダムモデルパラメータ
print("[10] Tao ランダムモデルのパラメータ")
print(f"  E[V] = sum_{{j>=1}} j*(1/2)^j = 2")
print(f"  E[log(3/2^V)] = log(3) - 2*log(2) = {math.log(3) - 2*math.log(2):.6f}")
print(f"  log(3)/log(2) = {math.log(3)/math.log(2):.6f} < 2")
print(f"  → 対数的には平均 {math.log(3) - 2*math.log(2):.6f} だけ減少")
print(f"  → k ステップ後: log(n) + k*(log3 - 2*log2) → -∞")
print(f"  → 約 log(n) / {2*math.log(2) - math.log(3):.4f} ≈ {1/(2*math.log(2)-math.log(3)):.2f}*log(n) ステップで 1 に到達")

# 逆像との関連
print(f"\n[11] 逆像GW率 4/3 とTao収縮率の関係")
print(f"  逆像の成長率 4/3 は「密度」の意味での成長")
print(f"  BFSの各層は前層の 4/3 倍の個数を持つ")
print(f"  → k 層目のサイズ ∼ (4/3)^k")
print(f"  → 半径 k の逆像ツリーがカバーするのは [1, C*(4/3)^k] 程度")
print(f"  → 全奇数 [1,N] をカバーするには k ∼ log(N)/log(4/3)")
print(f"  → log(4/3) = {math.log(4/3):.6f}")
print(f"  → 1/log(4/3) = {1/math.log(4/3):.2f}")

# 逆方向BFS成長率の精密測定
print(f"\n[12] 逆BFS成長率の大規模精密測定")

def inverse_bfs_unbounded(root, depth, N_bound):
    """N_bound は探索の上限（メモリ制約）"""
    current = {root}
    sizes = [1]
    for d in range(depth):
        next_set = set()
        for m in current:
            j = 1
            while True:
                num = m * (1 << j) - 1
                n_val = num // 3
                if n_val > N_bound:
                    break
                if num % 3 == 0 and n_val > 0 and n_val % 2 == 1:
                    next_set.add(n_val)
                j += 1
        sizes.append(len(next_set))
        current = next_set
        if not current:
            break
    return sizes

for root in [1, 5, 7]:
    sizes = inverse_bfs_unbounded(root, 12, 10**8)
    print(f"\n  root={root}: 層サイズ = {sizes}")
    rates = []
    for i in range(1, len(sizes)):
        if sizes[i-1] > 0:
            r = sizes[i] / sizes[i-1]
            rates.append(r)
    print(f"  成長率 = {[f'{r:.4f}' for r in rates]}")
    if len(rates) >= 3:
        avg_late = sum(rates[-3:]) / min(3, len(rates[-3:]))
        print(f"  後半3層の平均成長率 = {avg_late:.6f}")

print("\n完了")
