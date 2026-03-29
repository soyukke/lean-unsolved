#!/usr/bin/env python3
"""
追加解析: 逆コラッツ木GWモデルの深掘り

前回の結果から以下の疑問を探索:
1. 重複除去率が1.0000の理由 → 逆コラッツ木は実は「真の木」？
2. 被覆率が遅い理由 → 2n操作が支配的で (2n-1)/3 操作が稀
3. 多重型GW遷移行列のスペクトル半径 ≈ 1.3249 の意味
4. Syracuse版での真の分岐構造
5. 被覆時間のより精密な推定
"""

import math
import time
from collections import defaultdict, Counter

# ============================================================
# 1. 逆コラッツ木の衝突構造の厳密解析
# ============================================================

print("=" * 70)
print("1. 逆コラッツ木が真の木である理由の解析")
print("=" * 70)

# 逆操作: n → {2n, (2n-1)/3 if valid}
# 問題: 異なるノードから同じ子に到達する可能性は？
# n1 と n2 (n1 != n2) に対して:
# - 2*n1 = 2*n2 ⟹ n1 = n2 (矛盾)
# - 2*n1 = (2*n2-1)/3 ⟹ 6*n1 = 2*n2 - 1 (偶数=奇数: 不可能)
# - (2*n1-1)/3 = 2*n2 ⟹ 2*n1-1 = 6*n2 ⟹ n1 = (6*n2+1)/2 → n1 は正整数か？
# - (2*n1-1)/3 = (2*n2-1)/3 ⟹ n1 = n2 (矛盾)

print("\n衝突の可能性の代数的解析:")
print("  Case A: 2n1 = 2n2 → n1=n2 (自明な矛盾)")
print("  Case B: 2n1 = (2n2-1)/3 → 6n1 = 2n2-1 → 偶数=奇数 (不可能)")
print("  Case C: (2n1-1)/3 = 2n2 → 2n1-1 = 6n2 → n1 = (6n2+1)/2")
print("          これは n1 が整数なら、同じ子に2つの経路で到達")
print("          ただしこれは n1 → (2n1-1)/3 = 2n2 ← n2 の合流")
print("          BFS木では先に到達した方が親になるので衝突は「再訪問」")
print("  Case D: (2n1-1)/3 = (2n2-1)/3 → n1=n2 (自明な矛盾)")
print()
print("結論: BFS木の同一深さでの衝突は Case B で不可能。")
print("異なる深さからの合流は Case C で可能だが、BFSでは先着優先。")
print("→ BFS木のフロンティア内衝突率は0になるのは正しい。")
print("(ただし異なる深さからの「再訪問」はありうる)")

# Case C を具体的に確認
print("\nCase C の具体例: (2n1-1)/3 = 2n2 となる n1, n2 の探索")
case_c_count = 0
for n2 in range(1, 1000):
    val = 2 * n2  # 目標の子
    # n1 = (6*n2 + 1) / 2
    if (6 * n2 + 1) % 2 == 0:
        n1 = (6 * n2 + 1) // 2
        # 検証
        if (2 * n1 - 1) % 3 == 0 and (2 * n1 - 1) // 3 == val:
            case_c_count += 1
            if case_c_count <= 10:
                print(f"  n1={n1}, n2={n2}: (2*{n1}-1)/3 = {val} = 2*{n2}")

print(f"\n1..1000 で Case C が成立する n2 の数: {case_c_count}")
print("(これらは全て 6n2+1 が偶数 → 6n2 が奇数 → 不可能)")
print("→ Case C は成立しない！逆コラッツ操作では衝突が代数的に不可能。")

# 数値的に確認
print("\n数値的確認: 深さ30までで再訪問数を数える")
visited = {1: 0}
frontier = {1}
revisit_count = 0
revisit_depth = defaultdict(int)

for d in range(1, 31):
    next_frontier = set()
    for n in frontier:
        children = [2 * n]
        if (2 * n - 1) % 3 == 0:
            c2 = (2 * n - 1) // 3
            if c2 > 0:
                children.append(c2)

        for c in children:
            if c in visited:
                revisit_count += 1
                revisit_depth[d] += 1
            else:
                visited[c] = d
                next_frontier.add(c)

    frontier = next_frontier

print(f"再訪問の総数: {revisit_count}")
if revisit_count > 0:
    print(f"深さ別再訪問数: {dict(revisit_depth)}")
else:
    print("→ 再訪問ゼロ: 逆コラッツ木は真の木（合流なし）")

# ============================================================
# 2. 逆コラッツ木が真の木である証明
# ============================================================

print("\n" + "=" * 70)
print("2. 逆コラッツ木が真の木である証明")
print("=" * 70)

print("""
定理: 逆コラッツ木（根=1, 操作 n→2n と n→(2n-1)/3）は真の木である。
      すなわち、BFS構築において再訪問（合流）は発生しない。

証明の概略:
  コラッツ写像 T: N → N を T(n) = n/2 (偶) or (3n+1)/2 (奇) とする。
  逆コラッツ操作は T の逆写像。

  T が全射かつ各要素の逆像が有限 {2n, (2n-1)/3} であることから、
  コラッツグラフ（各 n → T(n) の有向グラフ）は各成分が「木+ループ」構造。

  コラッツ予想が真なら、このグラフは 1→2→1 のループを含む1つの成分。
  逆操作で作られるグラフは「根付き木+合流」だが...

  実際には:
  (a) T は関数なので、各 n は T(n) への辺を1本だけ持つ
  (b) したがって逆グラフでは各 n の入次数 = |T^{-1}(n)|
  (c) 順グラフで各 n の出次数 = 1 なので、逆グラフは forest (森)
  (d) コラッツ予想が真なら、1 を含む連結成分 = 全体
  (e) 森で連結 = 木

結論: 順コラッツグラフで各ノードの出次数=1 であることから、
      逆コラッツグラフは森であり、合流は代数的に不可能。
      コラッツ予想 ⟹ 逆コラッツグラフは全体が1つの木。

注意: これは「コラッツ予想が真なら木」という条件付きではなく、
      構造的に「森」であることは無条件。
      予想は「森が1つの木（連結）か」という問に同値。
""")

# ============================================================
# 3. Syracuse版 (奇数のみ) の分岐過程解析
# ============================================================

print("=" * 70)
print("3. Syracuse版 (奇数のみ) のGW過程詳細解析")
print("=" * 70)

# Syracuse T(n) = (3n+1)/2^v2(3n+1) for odd n
# T^{-1}(m) = { (2^k*m - 1)/3 : k>=1, 結果が正の奇数 }
# k が有効 ⟺ 2^k*m ≡ 1 (mod 3) かつ (2^k*m-1)/3 が奇数
#           ⟺ 2^k*m ≡ 1 (mod 3) かつ 2^k*m ≡ 4 (mod 6)
# 2^k mod 3: k=1→2, k=2→1, k=3→2, k=4→1, ...
# m mod 3: m=1→1, m=2→2 (m は奇数, m ≢ 0 mod 3 by T(n) ≢ 0 mod 3)

print("\nSyracuse逆像の k パリティ解析:")
print("  2^k mod 3 = 2 if k odd, 1 if k even")
print("  条件: 2^k*m ≡ 1 (mod 3)")
print("    m ≡ 1 (mod 3): k even (2^k ≡ 1 mod 3) → 1*1 ≡ 1 mod 3")
print("    m ≡ 2 (mod 3): k odd  (2^k ≡ 2 mod 3) → 2*2 ≡ 1 mod 3")
print()
print("  奇数条件: (2^k*m - 1)/3 が奇数")
print("    ⟺ 2^k*m - 1 ≡ 3 (mod 6)")
print("    ⟺ 2^k*m ≡ 4 (mod 6)")
print("    ⟺ 2^k*m ≡ 0 (mod 2) [常に真] かつ 2^k*m ≡ 1 (mod 3) [上の条件]")
print("    かつ (2^k*m - 1)/3 が奇数")
print()

# 有効なkの一般パターン
print("有効なkの列挙 (m=1の場合):")
for k in range(1, 61):
    val = (2**k * 1 - 1)
    if val % 3 == 0:
        result = val // 3
        if result > 0 and result % 2 == 1:
            print(f"  k={k}: (2^{k} - 1)/3 = {result} (奇数)")
        elif result > 0:
            print(f"  k={k}: (2^{k} - 1)/3 = {result} (偶数 → 無効)")
    if k > 20:
        break

print("\n有効なkの列挙 (m=3の場合):")
for k in range(1, 21):
    val = (2**k * 3 - 1)
    if val % 3 == 0:
        result = val // 3
        if result > 0 and result % 2 == 1:
            print(f"  k={k}: (2^{k}*3 - 1)/3 = {result} (奇数)")
        elif result > 0:
            print(f"  k={k}: (2^{k}*3 - 1)/3 = {result} (偶数 → 無効)")

# Syracuse版の分岐: 各奇数 m に対する逆像の数の分布
print("\n\nSyracuse逆像数の分布 (max_k=60):")
inv_count_by_mod = defaultdict(lambda: Counter())
total_by_mod = defaultdict(int)

for m in range(1, 100001, 2):
    count = 0
    pow2 = 2
    for k in range(1, 61):
        val = pow2 * m - 1
        if val % 3 == 0:
            result = val // 3
            if result > 0 and result % 2 == 1:
                count += 1
        pow2 *= 2
    mod6 = m % 6
    inv_count_by_mod[mod6][count] += 1
    total_by_mod[mod6] += 1

print(f"\nmod 6 別逆像数分布 (m: 1..100000 の奇数, max_k=60):")
for mod in sorted(inv_count_by_mod.keys()):
    dist = inv_count_by_mod[mod]
    total = total_by_mod[mod]
    avg = sum(c * n for c, n in dist.items()) / total
    print(f"\n  m ≡ {mod} (mod 6): 総数={total}, 平均逆像数={avg:.4f}")
    for c in sorted(dist.keys()):
        print(f"    逆像数={c}: {dist[c]}個 ({dist[c]/total*100:.2f}%)")

# ============================================================
# 4. Syracuse逆木のBFS構築と被覆率
# ============================================================

print("\n" + "=" * 70)
print("4. Syracuse逆木のBFS構築と被覆率")
print("=" * 70)

def syracuse_inverse_list(m, max_k=60):
    inverses = []
    pow2 = 2
    for k in range(1, max_k + 1):
        val = pow2 * m - 1
        if val % 3 == 0:
            result = val // 3
            if result > 0 and result % 2 == 1:
                inverses.append(result)
        pow2 *= 2
    return inverses

# Syracuse逆木のBFS (奇数のみ)
print("\nSyracuse逆木BFS (根=1, max_k=60):")
syr_visited = {1: 0}
syr_frontier = {1}
syr_stats = []
revisit_syr = 0

for d in range(1, 40):
    next_frontier = set()
    potential = 0
    actual = 0

    for m in syr_frontier:
        invs = syracuse_inverse_list(m, 60)
        potential += len(invs)
        for inv in invs:
            if inv not in syr_visited:
                syr_visited[inv] = d
                next_frontier.add(inv)
                actual += 1
            else:
                revisit_syr += 1

    growth = len(next_frontier) / len(syr_frontier) if syr_frontier else 0
    dedup = actual / potential if potential > 0 else 0

    syr_stats.append({
        'depth': d,
        'frontier': len(next_frontier),
        'total': len(syr_visited),
        'potential': potential,
        'actual': actual,
        'growth': growth,
        'dedup': dedup,
    })

    syr_frontier = next_frontier
    if not syr_frontier or len(syr_visited) > 5_000_000:
        break

print(f"\n{'深さ':>4} {'フロンティア':>12} {'累計':>10} {'潜在':>8} {'実新規':>8} "
      f"{'成長率':>8} {'重複除去率':>10}")
print("-" * 70)
for s in syr_stats:
    print(f"{s['depth']:>4} {s['frontier']:>12} {s['total']:>10} "
          f"{s['potential']:>8} {s['actual']:>8} "
          f"{s['growth']:>8.4f} {s['dedup']:>10.4f}")

print(f"\n再訪問の総数: {revisit_syr}")

# Syracuse版の奇数カバー率
print("\nSyracuse逆木の奇数カバー率:")
for N in [100, 1000, 10000, 100000]:
    odd_total = (N + 1) // 2
    covered = sum(1 for i in range(1, N + 1, 2) if i in syr_visited)
    print(f"  奇数 in 1..{N:>6}: {covered:>6}/{odd_total} = {covered/odd_total*100:.4f}%")

# ============================================================
# 5. GW理論 vs 実データの精密比較
# ============================================================

print("\n" + "=" * 70)
print("5. GW理論 vs 実データの精密比較")
print("=" * 70)

# 標準逆コラッツ木
print("\n--- 標準逆コラッツ木 ---")
print("GW理論: mu=4/3, 深さDでの期待ノード数 = (4/3)^D")
print("実データ:")

visited_std = {1: 0}
frontier_std = {1}
std_stats = []

for d in range(1, 60):
    next_frontier = set()
    for n in frontier_std:
        c1 = 2 * n
        if c1 not in visited_std:
            visited_std[c1] = d
            next_frontier.add(c1)
        if (2 * n - 1) % 3 == 0:
            c2 = (2 * n - 1) // 3
            if c2 > 0 and c2 not in visited_std:
                visited_std[c2] = d
                next_frontier.add(c2)

    expected = (4/3)**d
    ratio = len(next_frontier) / expected if expected > 0 else 0

    std_stats.append({
        'depth': d,
        'actual_width': len(next_frontier),
        'expected_gw': expected,
        'ratio': ratio,
        'total': len(visited_std),
    })

    frontier_std = next_frontier
    if len(visited_std) > 10_000_000:
        break

print(f"\n{'深さ':>4} {'実際の幅':>12} {'GW期待値':>14} {'比率':>10} {'累計':>12}")
print("-" * 60)
for s in std_stats:
    print(f"{s['depth']:>4} {s['actual_width']:>12} {s['expected_gw']:>14.1f} "
          f"{s['ratio']:>10.4f} {s['total']:>12}")

# 比率の漸近的挙動
if len(std_stats) >= 10:
    late_ratios = [s['ratio'] for s in std_stats[-10:]]
    print(f"\n最終10層の比率の平均: {sum(late_ratios)/len(late_ratios):.6f}")
    print(f"最終10層の比率の範囲: [{min(late_ratios):.6f}, {max(late_ratios):.6f}]")

# ============================================================
# 6. 遷移行列の固有値の厳密計算
# ============================================================

print("\n" + "=" * 70)
print("6. 遷移行列の固有値の厳密計算")
print("=" * 70)

# mod 6 遷移行列
M = [[0]*6 for _ in range(6)]
for r in range(6):
    M[r][(2*r) % 6] += 1
    if (2*r - 1) % 3 == 0:
        child = (2*r - 1) // 3
        M[r][child % 6] += 1

print("遷移行列 M:")
for i in range(6):
    print(f"  {M[i]}")

# 特性多項式を計算 (6x6 は簡略化のため数値解)
# numpy なしで固有値を求める: 冪乗法と逆冪乗法
print("\n冪乗法による固有値:")

# 最大固有値
v = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
for it in range(200):
    new_v = [0.0]*6
    for i in range(6):
        for j in range(6):
            new_v[i] += M[i][j] * v[j]
    norm = max(abs(x) for x in new_v)
    v = [x/norm for x in new_v]
    if it >= 195:
        print(f"  反復{it}: lambda_max = {norm:.10f}, v = {[f'{x:.6f}' for x in v]}")

lambda_max = norm
print(f"\n最大固有値 lambda_max = {lambda_max:.10f}")
print(f"4/3 = {4/3:.10f}")
print(f"差 = {lambda_max - 4/3:.10f}")

# 注意: mod 6 では偶数と奇数が分離する
# mod 6 = 0, 2, 4 は偶数のみ、mod 6 = 1, 3, 5 は奇数のみ
# 逆コラッツで 2n は常に偶数、(2n-1)/3 は常に奇数
print("\nmod 6 の偶奇分離:")
print("  偶数: mod 6 ∈ {0, 2, 4}")
print("  奇数: mod 6 ∈ {1, 3, 5}")
print("  2n: 常に偶数 → 偶数ノードからのみ偶数の子")
print("  (2n-1)/3: n≡2,5(mod6) → 奇数の子")
print()

# mod 6 の偶奇ブロック構造
print("遷移の偶奇構造:")
print("  偶数{0,2,4} → 偶数{0,2,4}: 2n 操作")
print("  偶数{2} → 奇数{1}: (2n-1)/3 操作")
print("  偶数{4} → なし")
print("  奇数{1,3,5} → 偶数{2,0,4}: 2n 操作")
print("  奇数{5} → 奇数{3}: (2n-1)/3 操作")
print("  奇数{1} → なし")
print("  奇数{3} → なし")

# 偶数・奇数それぞれのサブ行列
print("\n偶数サブ行列 (インデックス 0,2,4):")
even_idx = [0, 2, 4]
for i in even_idx:
    row = [M[i][j] for j in even_idx]
    print(f"  {row}")

print("\n奇数サブ行列 (インデックス 1,3,5):")
odd_idx = [1, 3, 5]
for i in odd_idx:
    row = [M[i][j] for j in odd_idx]
    print(f"  {row}")

# ============================================================
# 7. 被覆時間の精密推定 (より深い木で)
# ============================================================

print("\n" + "=" * 70)
print("7. 被覆時間の精密推定")
print("=" * 70)

# 深い逆コラッツ木での被覆率
print("\n深い逆コラッツ木での1..N のカバー率:")
check_Ns = [100, 500, 1000, 5000, 10000]

depth_data = []
for d_target in [20, 30, 40, 50, 55]:
    if d_target <= len(std_stats):
        total = std_stats[d_target - 1]['total']
        coverages = {}
        for N in check_Ns:
            covered = sum(1 for i in range(1, N + 1) if i in visited_std)
            coverages[N] = covered / N * 100
        depth_data.append({'depth': d_target, 'total': total, 'coverages': coverages})

print(f"\n{'深さ':>4} {'総ノード':>12}", end="")
for N in check_Ns:
    print(f" {'N='+str(N):>10}", end="")
print()
print("-" * (30 + 11 * len(check_Ns)))
for dd in depth_data:
    print(f"{dd['depth']:>4} {dd['total']:>12}", end="")
    for N in check_Ns:
        print(f" {dd['coverages'][N]:>9.2f}%", end="")
    print()

# 最小未カバー数
print("\n最小未カバー数 (各深さでの木に含まれない最小の正整数):")
# 標準逆コラッツ木での最小未カバー
min_uncovered = None
for i in range(2, 10001):
    if i not in visited_std:
        min_uncovered = i
        break
if min_uncovered:
    print(f"  深さ{len(std_stats)}の木での最小未カバー: {min_uncovered}")
else:
    print(f"  深さ{len(std_stats)}の木で 1..10000 は全てカバー")

# 1..100 で未カバーの数
uncovered_100 = [i for i in range(1, 101) if i not in visited_std]
print(f"  1..100 で未カバー: {uncovered_100[:20]} (計{len(uncovered_100)}個)")

# ============================================================
# 8. 逆コラッツ木の到達パターン解析
# ============================================================

print("\n" + "=" * 70)
print("8. 未カバー数の構造解析")
print("=" * 70)

# 1..10000 の未カバー数を収集
uncovered = [i for i in range(1, 10001) if i not in visited_std]
if uncovered:
    print(f"\n1..10000 で未カバーの数: {len(uncovered)}個")
    print(f"先頭30: {uncovered[:30]}")

    # mod 分布
    mod_dist = Counter()
    for n in uncovered:
        mod_dist[n % 6] += 1
    print(f"\n未カバー数の mod 6 分布:")
    for r in range(6):
        print(f"  mod {r}: {mod_dist[r]}個 ({mod_dist[r]/len(uncovered)*100:.1f}%)")

    # コラッツ軌道の長さ
    print(f"\n未カバー数のコラッツ軌道長 (T^k(n)=1 となる最小 k):")
    def collatz_steps(n):
        steps = 0
        while n != 1:
            if n % 2 == 0:
                n //= 2
            else:
                n = (3 * n + 1) // 2
            steps += 1
            if steps > 10000:
                return -1
        return steps

    orbit_lengths = [collatz_steps(n) for n in uncovered[:50]]
    print(f"  先頭50個の軌道長: {orbit_lengths}")
    avg_orbit = sum(orbit_lengths) / len(orbit_lengths)
    print(f"  平均軌道長: {avg_orbit:.1f}")

    # カバー済みの数との比較
    covered_sample = [i for i in range(1, 10001) if i in visited_std][:500]
    orbit_covered = [collatz_steps(n) for n in covered_sample]
    avg_covered = sum(orbit_covered) / len(orbit_covered)
    print(f"  カバー済みの数の平均軌道長: {avg_covered:.1f}")
    print(f"  → 未カバーの数は{'長い' if avg_orbit > avg_covered else '短い'}軌道を持つ傾向")

# ============================================================
# 9. GW過程のサバイバル定理とコラッツ予想
# ============================================================

print("\n" + "=" * 70)
print("9. GW過程のサバイバル定理とコラッツ予想への含意")
print("=" * 70)

print("""
【定理の要約】

GW分岐過程において:
- 子孫分布 p_k (k=0,1,2,...) に対して
- 平均子孫数 mu = sum(k * p_k)

(a) mu <= 1 → P(絶滅) = 1
(b) mu > 1 → P(絶滅) = q < 1 (非自明)
    ただし p_0 = 0 の場合 → P(絶滅) = 0

逆コラッツ木への適用:
- p_0 = 0, p_1 = 2/3, p_2 = 1/3
- mu = 4/3 > 1 (超臨界)
- P(絶滅) = 0

これは:
- 逆コラッツ木は必ず無限に成長する
- 木のサイズは指数的に増大する (成長率 ≈ 4/3)
- ただし「全ての正整数をカバーする」保証にはならない

カバーの問題:
- GW過程は「木のサイズ」について語る
- 「特定の数 n がカバーされるか」は別問題
- 木のノードは [1, ∞) に散布されるが、密度 → 0
- しかし「1..N のカバー」には O(N*polylog(N)) ノードで十分 (Coupon Collector)
- 木のサイズが (4/3)^D で成長するなら、D = O(log N) で十分

核心的困難:
- 逆コラッツ木のノードは一様ランダムではない
- 2^a * 3^b 型の値に偏りがある
- この非一様性が被覆の「穴」を生む可能性がある
""")

# ============================================================
# 10. スペクトル半径 と 実効成長率 の関係
# ============================================================

print("=" * 70)
print("10. スペクトル半径の詳細解析")
print("=" * 70)

# 実は遷移行列のスペクトル半径 ≈ 1.3249 ≠ 4/3 の理由
# mod 6 だけでは不十分で、ノードの到達可能性に制約がある

# 行列 M の特性方程式を解く
# det(M - lambda*I) = 0
# M は疎で構造的

print("\n遷移行列のスペクトル解析:")
print("M の構造:")
print("  0→0, 1→2, 2→4+1, 3→0, 4→2, 5→4+3")
print()
print("到達可能な mod 6 クラス (根=1 から):")
print("  1 → 2 (2n)")
print("  2 → 4+1 (2n と (2n-1)/3)")
print("  4 → 2 (2n)")
print("  1 → (逆像なし)")
print()
print("到達可能集合: {1, 2, 4} → mod 6 の偶奇混在だが mod 3 では {1, 2}")
print("mod 6 = 0, 3 はルート 1 から直接到達不能")

# 到達可能な mod 6 クラスの確認
reachable_mod6 = set()
current_mods = {1}  # 根は 1 (mod 6)
for step in range(10):
    next_mods = set()
    for r in current_mods:
        # 2n
        next_mods.add((2 * r) % 6)
        # (2n-1)/3
        if (2 * r - 1) % 3 == 0:
            child = ((2 * r - 1) // 3) % 6
            next_mods.add(child)
    reachable_mod6.update(next_mods)
    current_mods = next_mods

print(f"\n根=1 から到達可能な mod 6 クラス: {sorted(reachable_mod6)}")

# 到達可能サブ行列
reachable = sorted(reachable_mod6)
print(f"\n到達可能サブ行列 (mod 6 = {reachable}):")
sub_M = []
for i in reachable:
    row = [M[i][j] for j in reachable]
    sub_M.append(row)
    print(f"  {row}")

# サブ行列の最大固有値
dim = len(reachable)
v = [1.0] * dim
for it in range(200):
    new_v = [0.0] * dim
    for i in range(dim):
        for j in range(dim):
            new_v[i] += sub_M[i][j] * v[j]
    norm = max(abs(x) for x in new_v)
    v = [x/norm for x in new_v]

print(f"\nサブ行列の最大固有値: {norm:.10f}")
print(f"4/3 = {4/3:.10f}")
print(f"差: {norm - 4/3:.10f}")

# 実はmod 12 やmod 18 で見るとどうか
print("\n--- mod 12 での解析 ---")
M12 = [[0]*12 for _ in range(12)]
for r in range(12):
    M12[r][(2*r) % 12] += 1
    if (2*r - 1) % 3 == 0:
        child = ((2*r - 1) // 3) % 12
        M12[r][child] += 1

# 到達可能 mod 12
reachable_12 = set()
current = {1}
for _ in range(20):
    nxt = set()
    for r in current:
        nxt.add((2*r) % 12)
        if (2*r-1) % 3 == 0:
            nxt.add(((2*r-1)//3) % 12)
    reachable_12.update(nxt)
    current = nxt

print(f"根=1 から到達可能な mod 12 クラス: {sorted(reachable_12)}")

# サブ行列
r12 = sorted(reachable_12)
sub_M12 = []
for i in r12:
    row = [M12[i][j] for j in r12]
    sub_M12.append(row)

dim12 = len(r12)
v12 = [1.0] * dim12
for it in range(300):
    new_v = [0.0] * dim12
    for i in range(dim12):
        for j in range(dim12):
            new_v[i] += sub_M12[i][j] * v12[j]
    norm12 = max(abs(x) for x in new_v)
    if norm12 > 0:
        v12 = [x/norm12 for x in new_v]

print(f"mod 12 サブ行列の最大固有値: {norm12:.10f}")

# ============================================================
# 11. 正しい成長率の理論的説明
# ============================================================

print("\n" + "=" * 70)
print("11. 成長率 4/3 と スペクトル半径の不一致の理論的説明")
print("=" * 70)

print("""
観察: 実効成長率 ≈ 1.3333 (=4/3) だが、
      mod 6 遷移行列のスペクトル半径 ≈ 1.3249

説明:
  mod 6 遷移行列は「各 mod 6 クラスのノード数」の成長を記述する。
  しかし逆コラッツ木では、各深さでの mod 6 分布は均等ではない。

  実効成長率 4/3 は「全ノード数」の成長率:
    W(d+1) = W(d) * (1 + P(deg=2))
    ここで P(deg=2) は深さ d のフロンティアでの deg=2 の割合。
    均等なら P(deg=2) = 1/3 → W(d+1)/W(d) = 4/3。

  スペクトル半径 ≈ 1.3249 は mod 6 遷移行列の最大固有値で、
  各クラスの「相対的な成長」を記述する。
  これが 4/3 より小さいのは、mod 6 クラス間の相互作用による。

実データ確認: 深さごとの mod 6 分布
""")

# 実際のフロンティアの mod 6 分布
print("フロンティアの mod 6 分布:")
v_check = {1: 0}
f_check = {1}
for d in range(1, 55):
    nxt = set()
    for n in f_check:
        c1 = 2 * n
        if c1 not in v_check:
            v_check[c1] = d
            nxt.add(c1)
        if (2*n-1) % 3 == 0:
            c2 = (2*n-1)//3
            if c2 > 0 and c2 not in v_check:
                v_check[c2] = d
                nxt.add(c2)
    if not nxt:
        break
    mod6_count = Counter(n % 6 for n in nxt)
    total_f = len(nxt)
    deg2_frac = sum(1 for n in nxt if (2*n-1) % 3 == 0) / total_f
    growth = total_f / len(f_check)
    if d <= 30 or d % 5 == 0:
        dist_str = ", ".join(f"{r}:{mod6_count.get(r,0)/total_f:.3f}" for r in range(6))
        print(f"  D={d:>2}: width={total_f:>10}, growth={growth:.4f}, "
              f"deg2率={deg2_frac:.4f}, mod6=[{dist_str}]")
    f_check = nxt
    if len(v_check) > 10_000_000:
        break

print("\n完了!")
