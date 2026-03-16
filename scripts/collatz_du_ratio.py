#!/usr/bin/env python3
"""
コラッツ予想 探索30: d/u > log₂(3) の深堀り

偶数ステップ数 d と奇数ステップ数 u の比 d/u が
常に log₂(3) ≈ 1.585 を超えるかどうかを大規模に検証し、
そのメカニズムを解明する。
"""

import math
from collections import defaultdict

LOG2_3 = math.log2(3)  # ≈ 1.58496...

# ===========================================================
# ユーティリティ
# ===========================================================

def collatz_du(n):
    """n の軌道で d(偶数ステップ=÷2回数), u(奇数ステップ=3n+1回数) を返す"""
    d, u = 0, 0
    x = n
    while x != 1:
        if x % 2 == 0:
            x //= 2
            d += 1
        else:
            x = 3 * x + 1
            u += 1
    return d, u


def collatz_du_with_cycles(n):
    """
    サイクル(連続上昇k回 + 下降v2回)ごとの情報を返す。
    各サイクル: (k, v2) where k=連続奇数ステップ数, v2=その後の連続偶数ステップ数
    """
    cycles = []
    x = n
    while x != 1:
        # 奇数フェーズ: 連続して 3x+1 → ÷2 (奇数の間続ける)
        k = 0
        while x != 1 and x % 2 == 1:
            x = 3 * x + 1
            k += 1
            # 3x+1 は必ず偶数なので1回÷2
            x //= 2
        # ここで x は偶数 or 1
        # 追加の偶数ステップ
        v2 = 0
        while x != 1 and x % 2 == 0:
            x //= 2
            v2 += 1
        # サイクル: 上昇k回(各回で÷2が1回含まれる)→追加下降v2回
        # total d in cycle = k + v2, total u in cycle = k
        if k > 0 or v2 > 0:
            cycles.append((k, v2))
    return cycles


# ===========================================================
# 1. d/u の最小値を大規模に探索
# ===========================================================
print("=" * 70)
print("1. d/u の最小値を大規模に探索 (n=1..10^6 の奇数)")
print("=" * 70)

results = []  # (d/u, n, d, u)
N_MAX = 1_000_000

for n in range(3, N_MAX + 1, 2):  # 奇数のみ
    d, u = collatz_du(n)
    if u > 0:
        ratio = d / u
        results.append((ratio, n, d, u))

results.sort()

print(f"\n全 {len(results)} 個の奇数を調査")
print(f"log₂(3) = {LOG2_3:.10f}")
print(f"\nd/u が最小の上位50個:")
print(f"{'Rank':>4} {'n':>10} {'d':>6} {'u':>6} {'d/u':>12} {'d/u - log₂3':>14}")
print("-" * 60)
for i, (ratio, n, d, u) in enumerate(results[:50]):
    diff = ratio - LOG2_3
    print(f"{i+1:>4} {n:>10} {d:>6} {u:>6} {ratio:>12.8f} {diff:>14.8f}")

# d/u < log₂(3) のものがあるか？
below = [(r, n, d, u) for r, n, d, u in results if r < LOG2_3]
print(f"\nd/u < log₂(3) の個数: {len(below)}")
if below:
    print("  *** d/u < log₂(3) となる n が存在！***")
    for r, n, d, u in below[:10]:
        print(f"    n={n}, d={d}, u={u}, d/u={r:.10f}")

# 範囲ごとの最小 d/u の推移
print(f"\n範囲ごとの最小 d/u:")
print(f"{'Range':>20} {'min d/u':>14} {'n*':>10} {'d':>6} {'u':>6}")
print("-" * 60)
for exp in range(1, 7):
    upper = 10 ** exp
    subset = [(r, n, d, u) for r, n, d, u in results if n <= upper]
    if subset:
        r, n, d, u = min(subset)
        print(f"{'n ≤ ' + str(upper):>20} {r:>14.10f} {n:>10} {d:>6} {u:>6}")


# ===========================================================
# 2. d/u が小さい n の共通パターン
# ===========================================================
print("\n" + "=" * 70)
print("2. d/u が小さい n の共通パターン")
print("=" * 70)

top100 = results[:100]

# 2進表現の特徴
print("\n--- 2進表現（上位20個）---")
for i, (ratio, n, d, u) in enumerate(top100[:20]):
    binary = bin(n)[2:]
    ones = binary.count('1')
    print(f"  n={n:>10} = {binary:>25} (長さ{len(binary):>3}, 1の数{ones:>3}, d/u={ratio:.8f})")

# mod の分布
print("\n--- mod 分布 (上位100) ---")
for mod_val in [8, 16, 32]:
    counts = defaultdict(int)
    for _, n, _, _ in top100:
        counts[n % mod_val] += 1
    print(f"  mod {mod_val}: ", end="")
    for k in sorted(counts.keys()):
        if counts[k] >= 3:
            print(f"{k}({counts[k]})", end=" ")
    print()

# 連続上昇回数との関係
print("\n--- 最大連続上昇回数 (上位20) ---")
for i, (ratio, n, d, u) in enumerate(top100[:20]):
    cycles = collatz_du_with_cycles(n)
    max_k = max(k for k, v2 in cycles) if cycles else 0
    avg_k = sum(k for k, v2 in cycles) / len(cycles) if cycles else 0
    print(f"  n={n:>10}: max_k={max_k:>3}, avg_k={avg_k:.2f}, d/u={ratio:.8f}")

# メルセンヌ数
print("\n--- メルセンヌ数 2^k - 1 の d/u ---")
print(f"{'k':>4} {'n=2^k-1':>15} {'d':>6} {'u':>6} {'d/u':>12} {'d/u - log₂3':>14}")
print("-" * 60)
for k in range(2, 21):
    n = 2**k - 1
    d, u = collatz_du(n)
    if u > 0:
        ratio = d / u
        diff = ratio - LOG2_3
        print(f"{k:>4} {n:>15} {d:>6} {u:>6} {ratio:>12.8f} {diff:>14.8f}")


# ===========================================================
# 3. d/u の理論的下界の導出試行
# ===========================================================
print("\n" + "=" * 70)
print("3. d/u の理論的下界の導出試行")
print("=" * 70)

print(f"""
■ サイクル分析

1サイクル = 連続上昇 k 回 + 追加下降 v2 回
  - 上昇1回: n → (3n+1)/2 で u+=1, d+=1
  - 追加下降: n → n/2^v2 で d+=v2

サイクルの d/u = (k + v2) / k  (k≥1)

■ 個別サイクルの d/u の下界

3n+1 が偶数なので、上昇後は少なくとも1回追加で÷2できる可能性がある。
実際には v2≥1 が保証される（追加の÷2）。

しかし k回連続上昇のとき:
  T^k(n) = (3^k·n + (3^k - 2^k)) / 2^k (上昇フェーズ)
  その後 v2 回 ÷2 (下降フェーズ)

全体での d = k + v2, u = k
""")

# サイクル(k, v2)の実際の分布を調べる
print("■ サイクル (k, v2) の分布 (n=3..10^5 の奇数)")
cycle_counts = defaultdict(int)
total_cycles = 0
for n in range(3, 100001, 2):
    cycles = collatz_du_with_cycles(n)
    for k, v2 in cycles:
        if k > 0:
            cycle_counts[(k, v2)] += 1
            total_cycles += 1

print(f"総サイクル数: {total_cycles}")
print(f"\n上位30のサイクルタイプ:")
print(f"{'(k,v2)':>10} {'count':>8} {'%':>8} {'d/u=(k+v2)/k':>14}")
print("-" * 45)
sorted_cycles = sorted(cycle_counts.items(), key=lambda x: -x[1])
for (k, v2), cnt in sorted_cycles[:30]:
    pct = cnt / total_cycles * 100
    ratio = (k + v2) / k if k > 0 else float('inf')
    marker = " *** < log₂3" if ratio < LOG2_3 else ""
    print(f"  ({k},{v2:>2}){cnt:>10} {pct:>7.2f}% {ratio:>14.8f}{marker}")

# k ごとの v2 の平均
print(f"\n■ k ごとの v2 の平均と d/u")
k_v2_sum = defaultdict(float)
k_count = defaultdict(int)
for (k, v2), cnt in cycle_counts.items():
    if k > 0:
        k_v2_sum[k] += v2 * cnt
        k_count[k] += cnt

print(f"{'k':>4} {'count':>10} {'avg v2':>10} {'avg d/u':>12} {'theory min':>12}")
print("-" * 50)
for k in sorted(k_count.keys()):
    avg_v2 = k_v2_sum[k] / k_count[k]
    avg_ratio = (k + avg_v2) / k
    theory_min = (k + 1) / k  # v2=1の場合
    print(f"{k:>4} {k_count[k]:>10} {avg_v2:>10.4f} {avg_ratio:>12.8f} {theory_min:>12.8f}")

# 重み付き平均 d/u
print(f"\n■ 全サイクルの重み付き平均 d/u")
total_d = sum((k + v2) * cnt for (k, v2), cnt in cycle_counts.items() if k > 0)
total_u = sum(k * cnt for (k, v2), cnt in cycle_counts.items() if k > 0)
overall_ratio = total_d / total_u
print(f"  Σd / Σu = {total_d} / {total_u} = {overall_ratio:.10f}")
print(f"  log₂(3) = {LOG2_3:.10f}")
print(f"  差 = {overall_ratio - LOG2_3:.10f}")

print(f"""
■ 理論的考察

k回連続上昇のサイクルの確率的モデル:
  上昇k回後の値 ≈ (3/2)^k · n
  追加下降v2回の確率 ≈ Pr[v2(X)=j] ≈ 1/2^j (幾何分布)

  E[v2] ≈ 1 (幾何分布の期待値、ただし v2≥1)
  → E[d/u] ≈ E[(k+v2)/k] = 1 + E[v2]/k ≈ 1 + 1/k

  k=1: E[d/u] ≈ 2.0
  k→∞: E[d/u] → 1.0

  しかし全軌道での d/u はサイクルの平均ではなく、
  各 k が出現する確率で重み付けする必要がある。

  k回連続上昇の確率 ≈ (1/2)^k（各ステップで奇数になる確率1/2）
  → E[k] = Σ k·(1/2)^k = 2

  全体の d/u ≈ E[k + v2] / E[k]
  = (E[k] + E[v2]) / E[k]
  = 1 + E[v2] / E[k]
  ≈ 1 + 1/2 = 1.5 ← log₂(3) より小さい?

  いや、E[v2] は k に依存しない独立な幾何分布ではない。
  実際の分布を使って計算する。
""")


# ===========================================================
# 4. サイクルごとの累積 d/u の推移
# ===========================================================
print("=" * 70)
print("4. サイクルごとの累積 d/u の推移")
print("=" * 70)

test_numbers = [27, 703, 871, 2**20 - 1, 2**15 - 1, 2**10 - 1]

for n in test_numbers:
    cycles = collatz_du_with_cycles(n)
    cum_d, cum_u = 0, 0
    below_log23 = False
    min_ratio = float('inf')
    min_ratio_idx = 0

    trajectory = []
    for i, (k, v2) in enumerate(cycles):
        cum_d += k + v2
        cum_u += k
        if cum_u > 0:
            ratio = cum_d / cum_u
            trajectory.append((i, cum_d, cum_u, ratio))
            if ratio < LOG2_3:
                below_log23 = True
            if ratio < min_ratio:
                min_ratio = ratio
                min_ratio_idx = i

    d_total, u_total = cum_d, cum_u
    final_ratio = d_total / u_total if u_total > 0 else float('inf')

    print(f"\nn = {n}")
    print(f"  サイクル数: {len(cycles)}, 最終 d={d_total}, u={u_total}, d/u={final_ratio:.8f}")
    print(f"  最小累積d/u: {min_ratio:.8f} (サイクル{min_ratio_idx})")
    print(f"  累積d/u < log₂(3) の瞬間: {'あり' if below_log23 else 'なし'}")

    # 推移の詳細（最初と最後、最小付近）
    if len(trajectory) > 0:
        print(f"  推移（抜粋）:")
        show_indices = set()
        # 最初の10
        for i in range(min(10, len(trajectory))):
            show_indices.add(i)
        # 最小付近
        for i in range(max(0, min_ratio_idx-2), min(len(trajectory), min_ratio_idx+3)):
            show_indices.add(i)
        # 最後の5
        for i in range(max(0, len(trajectory)-5), len(trajectory)):
            show_indices.add(i)

        prev_shown = -1
        for i in sorted(show_indices):
            if i > prev_shown + 1 and prev_shown >= 0:
                print(f"       ...")
            idx, cd, cu, r = trajectory[i]
            marker = " *** < log₂3" if r < LOG2_3 else ""
            print(f"    cycle {idx:>4}: cum_d={cd:>5}, cum_u={cu:>5}, d/u={r:.8f}{marker}")
            prev_shown = i


# 全体統計: d/u が途中で log₂(3) を下回る n の割合
print(f"\n--- n=3..10000(奇数)で途中の累積d/u < log₂(3) になる割合 ---")
count_below = 0
count_total = 0
for n in range(3, 10001, 2):
    cycles = collatz_du_with_cycles(n)
    cum_d, cum_u = 0, 0
    found_below = False
    for k, v2 in cycles:
        cum_d += k + v2
        cum_u += k
        if cum_u > 0 and cum_d / cum_u < LOG2_3:
            found_below = True
            break
    count_total += 1
    if found_below:
        count_below += 1

print(f"  途中で d/u < log₂(3) になる n の数: {count_below} / {count_total} ({count_below/count_total*100:.1f}%)")


# ===========================================================
# 5. d/u の martingale 的性質
# ===========================================================
print("\n" + "=" * 70)
print("5. d/u の martingale 的性質")
print("=" * 70)

print("""
■ 各ステップでの d/u の変化を分析

偶数ステップ (n→n/2): d→d+1, u→u, d/u → (d+1)/u
  Δ(d/u) = 1/u > 0

奇数ステップ (n→3n+1): d→d, u→u+1, d/u → d/(u+1)
  Δ(d/u) = d/(u+1) - d/u = -d/(u(u+1)) < 0

偶数ステップでは d/u が増加、奇数ステップでは減少。
""")

# 実際の軌道でステップごとの d/u を追跡
print("■ ステップごとの d/u 変化の統計 (n=3..100000, 奇数)")

# d/u の区間ごとに、次のステップが偶数/奇数になる確率
bins = {}  # {bin_key: [count_even, count_odd, sum_delta]}
for n in range(3, 100001, 2):
    x = n
    d, u = 0, 0
    while x != 1:
        if d > 0 and u > 0:
            ratio = d / u
            # 区間: [1.0, 1.1), [1.1, 1.2), ..., [2.4, 2.5)
            bin_key = round(ratio * 10) / 10  # 0.1刻み
            if bin_key not in bins:
                bins[bin_key] = [0, 0, 0.0]

            if x % 2 == 0:
                bins[bin_key][0] += 1
                delta = 1 / u
            else:
                bins[bin_key][1] += 1
                delta = -d / (u * (u + 1))
            bins[bin_key][2] += delta

        if x % 2 == 0:
            x //= 2
            d += 1
        else:
            x = 3 * x + 1
            u += 1

print(f"\n{'d/u区間':>10} {'偶数step':>10} {'奇数step':>10} {'P(偶数)':>10} {'E[Δ(d/u)]':>12} {'d/u vs log₂3':>14}")
print("-" * 70)
for key in sorted(bins.keys()):
    if 1.0 <= key <= 3.0:
        even, odd, sum_delta = bins[key]
        total = even + odd
        if total > 100:  # ノイズ除去
            p_even = even / total
            avg_delta = sum_delta / total
            vs = "below" if key < LOG2_3 else "above"
            marker = " <<<" if key < LOG2_3 and avg_delta > 0 else ""
            marker = marker or (" >>>" if key >= LOG2_3 and avg_delta < 0 else "")
            print(f"{key:>10.1f} {even:>10} {odd:>10} {p_even:>10.4f} {avg_delta:>12.8f} {vs:>14}{marker}")

print(f"""
■ 解釈

d/u < log₂(3) の領域で E[Δ(d/u)] > 0 なら:
  → d/u は log₂(3) に向かって「押し戻される」傾向がある
  → 復元力（restoring force）が存在

d/u > log₂(3) の領域で E[Δ(d/u)] の符号は:
  → 正なら d/u はさらに増大する傾向
  → 負なら d/u は log₂(3) に引き戻される
""")

# E[Δ(d/u)] のより精密な計算
# d/u = r のとき、次のステップが偶数になる確率を p とすると
# E[Δ] = p · (1/u) + (1-p) · (-d/(u(u+1)))
# = p/u - (1-p)·r/(u+1)
# = (1/u) · [p - (1-p)·r·u/(u+1)]

# E[Δ] = 0 ⟺ p = r·u/((u+1) + r·u) ≈ r/(1+r) for large u
# Heuristic: p ≈ log₂(3)/(1+log₂(3)) ≈ 0.613 if random model

print("\n■ 均衡条件の理論分析")
print(f"  確率的モデル: 各ステップで偶数になる確率 p")
print(f"  E[Δ(d/u)] = 0 の条件: p = r/(1+r) (大きな u の近似)")
print(f"  d/u = log₂(3) ≈ 1.585 のとき: p* = {LOG2_3/(1+LOG2_3):.6f}")
print(f"")
print(f"  コラッツ過程の実測 p:")

# 実測の偶数確率
total_even = sum(bins[k][0] for k in bins)
total_odd = sum(bins[k][1] for k in bins)
total_all = total_even + total_odd
p_empirical = total_even / total_all
print(f"  p(偶数) = {total_even}/{total_all} = {p_empirical:.8f}")
print(f"  p*/(1+p*) → d/u* = p/(1-p) = {p_empirical/(1-p_empirical):.8f}")
print(f"  log₂(3) = {LOG2_3:.8f}")
print(f"  差 = {p_empirical/(1-p_empirical) - LOG2_3:.8f}")

# ===========================================================
# 追加: 理論的な「なぜ d/u > log₂(3) か」のまとめ
# ===========================================================
print("\n" + "=" * 70)
print("6. 総合考察: なぜ d/u > log₂(3) なのか")
print("=" * 70)
print(f"""
■ 核心的メカニズム

1. 偶数ステップの確率的優位性:
   コラッツ過程で x → 3x+1 の結果は必ず偶数。
   つまり奇数ステップの直後に必ず偶数ステップが来る。
   これにより P(偶数) > 1/2 が構造的に保証される。

2. 均衡点の計算:
   P(偶数) = p のとき、長期的な d/u → p/(1-p)
   実測 p ≈ {p_empirical:.6f} → d/u → {p_empirical/(1-p_empirical):.6f}
   log₂(3) に必要な p* = {LOG2_3/(1+LOG2_3):.6f}

   実測 p > p* ⟺ d/u > log₂(3)

3. 復元力の存在:
   d/u < log₂(3) の区間では E[Δ(d/u)] > 0 の傾向
   → d/u は log₂(3) を下回っても押し戻される

4. 収束のカスケード:
   n → 1 への収束 ⟺ 2^d > 3^u（軌道全体で）
   ⟺ d/u > log₂(3)（ステップ数の比で）
   ⟺ P(偶数) > log₂(3)/(1+log₂(3)) ≈ 0.613

5. Lean 4 への示唆:
   もし「有限軌道をもつ全ての n で d/u > log₂(3)」を示せれば、
   コラッツ予想の証明に帰着する。
   必要なのは P(偶数) > 0.613... の構造的保証。
""")

# 最後に: d/u が log₂(3) に最も近い n のサイクル構造
print("■ d/u が log₂(3) に最も近い n=", results[0][1], "のサイクル構造")
_, closest_n, _, _ = results[0]
cycles = collatz_du_with_cycles(closest_n)
print(f"  サイクル数: {len(cycles)}")
print(f"  サイクル (k, v2) の列:")
for i, (k, v2) in enumerate(cycles):
    ratio_c = (k + v2) / k if k > 0 else float('inf')
    print(f"    {i:>3}: k={k}, v2={v2}, サイクルd/u={(k+v2)/k if k>0 else 'inf':.4f}")
    if i > 30:
        print(f"    ... (以降省略, 全{len(cycles)}サイクル)")
        break

print("\n完了")
