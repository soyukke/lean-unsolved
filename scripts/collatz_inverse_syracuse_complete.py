#!/usr/bin/env python3
"""
逆Syracuse写像 T^{-1}(m) の完全代数的記述

Syracuse写像: T(n) = (3n+1) / 2^{v2(3n+1)}  (n: 奇数)
逆像: T^{-1}(m) = {n odd : T(n) = m}

定理: n が T^{-1}(m) に属する iff n = (m * 2^j - 1) / 3 で
  (1) j >= 1
  (2) m * 2^j ≡ 1 (mod 3)  (すなわち 3 | (m*2^j - 1))
  (3) n は奇数 (自動的に成立)
  (4) n >= 1

本スクリプトは以下を検証:
  A. m mod 6 による有効 j の完全分類
  B. 各 m に対する T^{-1}(m) の構造
  C. 入次数 (in-degree) の分布
  D. 閉公式 |T^{-1}(m) ∩ [1,N]| の検証
  E. v2条件の自動成立の確認
  F. m ≡ 0 (mod 3) => 逆像なし の確認
"""

import math
from collections import Counter, defaultdict

# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)}"""
    assert n > 0 and n % 2 == 1, f"n={n} must be odd positive"
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse_all(m, j_max=30):
    """
    T^{-1}(m) の要素を j=1,...,j_max で列挙
    n = (m * 2^j - 1) / 3 が正奇整数のとき
    """
    results = []
    for j in range(1, j_max + 1):
        numerator = m * (1 << j) - 1
        if numerator % 3 == 0:
            n = numerator // 3
            if n > 0 and n % 2 == 1:
                results.append((n, j))
    return results

# ============================================================
# A. m mod 6 による有効 j の完全分類
# ============================================================

print("=" * 70)
print("A. m mod 6 による有効 j の完全分類")
print("=" * 70)

# 理論的分析:
# 2^j mod 3 は周期2: 2^1≡2, 2^2≡1, 2^3≡2, 2^4≡1, ...
# つまり 2^j ≡ 2 (mod 3) if j odd, 2^j ≡ 1 (mod 3) if j even
#
# 条件: m * 2^j ≡ 1 (mod 3)
#
# m ≡ 0 (mod 3): m*2^j ≡ 0 (mod 3) ≠ 1 => 解なし
# m ≡ 1 (mod 3):
#   j even: 1*1 = 1 ≡ 1 (mod 3) => OK
#   j odd:  1*2 = 2 ≡ 2 (mod 3) => NG
# m ≡ 2 (mod 3):
#   j even: 2*1 = 2 ≡ 2 (mod 3) => NG
#   j odd:  2*2 = 4 ≡ 1 (mod 3) => OK

print("\n理論予測:")
print("  m ≡ 0 (mod 3): 逆像なし")
print("  m ≡ 1 (mod 3): j ∈ {2, 4, 6, 8, ...} (偶数のみ)")
print("  m ≡ 2 (mod 3): j ∈ {1, 3, 5, 7, ...} (奇数のみ)")
print()

# nの奇数性の追加条件を分析
# n = (m * 2^j - 1) / 3
# nが奇数 <=> (m * 2^j - 1) / 3 が奇数 <=> m * 2^j - 1 ≡ 3 (mod 6)
# <=> m * 2^j ≡ 4 (mod 6) <=> m * 2^j ≡ 4 (mod 6)

print("n の奇数性の詳細分析:")
print()

# m mod 6 と j の組み合わせで完全分類
for m_mod6 in range(6):
    m_mod3 = m_mod6 % 3
    if m_mod3 == 0:
        print(f"  m ≡ {m_mod6} (mod 6): 3|m なので逆像なし")
        continue

    valid_j = []
    for j in range(1, 25):
        numerator = m_mod6 * (2**j) - 1
        # 3で割り切れるか
        if numerator % 3 != 0:
            continue
        n_mod2 = (numerator // 3) % 2
        n_mod6_val = (numerator // 3) % 6
        valid_j.append((j, n_mod2, n_mod6_val))

    # jの偶奇パターン
    j_vals = [x[0] for x in valid_j if x[1] == 1]  # nが奇数のもの
    j_all_div3 = [x[0] for x in valid_j]  # 3|条件のみ

    print(f"  m ≡ {m_mod6} (mod 6):")
    print(f"    3|(m*2^j-1) となる j: {[x[0] for x in valid_j[:10]]} ...")
    print(f"    さらに n奇数 となる j: {j_vals[:10]} ...")

    # パターン検出
    if len(j_vals) >= 3:
        diffs = [j_vals[i+1] - j_vals[i] for i in range(min(8, len(j_vals)-1))]
        print(f"    j の差分列: {diffs}")

print()

# 数値検証
print("数値検証 (m=1..30 に対して T^{-1}(m) を計算):")
print()

for m in range(1, 31, 2):  # 奇数mのみ（Syracuse写像の値域は奇数）
    preimages = inverse_syracuse_all(m, j_max=40)
    m_mod6 = m % 6
    m_mod3 = m % 3

    # 検証: 各preimageが本当にT(n)=mか
    for n, j in preimages:
        actual = syracuse(n)
        if actual != m:
            print(f"  WARNING: T({n})={actual} != {m} (j={j})")

    j_list = [j for _, j in preimages]
    n_list = [n for n, _ in preimages]

    if preimages:
        print(f"  m={m:3d} (≡{m_mod6} mod 6): "
              f"|T^{{-1}}|={len(preimages):2d}, "
              f"j={j_list[:6]}{'...' if len(j_list)>6 else ''}, "
              f"n={n_list[:4]}{'...' if len(n_list)>4 else ''}")
    else:
        print(f"  m={m:3d} (≡{m_mod6} mod 6): 逆像なし")

# ============================================================
# B. 完全代数的記述の定理
# ============================================================

print()
print("=" * 70)
print("B. 完全代数的記述の定理")
print("=" * 70)

# m mod 6 ごとの有効 j のパターンを厳密に決定
print()
print("定理: T^{-1}(m) の完全記述")
print()

for m_mod6 in range(6):
    print(f"--- m ≡ {m_mod6} (mod 6) ---")
    m_mod3 = m_mod6 % 3
    m_mod2 = m_mod6 % 2

    if m_mod3 == 0:
        print("  逆像: 空集合 (3|m のため T(n) ≡ 0 mod 3 にならない)")
        print()
        continue

    # 有効 j の完全リスト（パターン抽出）
    valid_j_pattern = []
    for j in range(1, 50):
        num = m_mod6 * (2**j) - 1
        if num % 3 == 0:
            n_check = num // 3
            if n_check % 2 == 1:
                valid_j_pattern.append(j)

    # パターンを見つける
    if len(valid_j_pattern) >= 3:
        period = valid_j_pattern[1] - valid_j_pattern[0]
        start = valid_j_pattern[0]
        all_match = all(valid_j_pattern[i] == start + i * period
                       for i in range(len(valid_j_pattern)))

        if all_match:
            print(f"  有効 j: j = {start} + {period}k (k = 0, 1, 2, ...)")
            print(f"  具体的: j ∈ {{{start}, {start+period}, {start+2*period}, ...}}")
            print(f"  逆像: n_k = (m * 2^({start}+{period}k) - 1) / 3")

            # 比率
            ratio = 2**period
            print(f"  n_{'{k+1}'}/n_k → {ratio} as k → ∞")
            print(f"  つまり逆像は指数的に疎")
        else:
            # 複合パターンか確認
            diffs = [valid_j_pattern[i+1] - valid_j_pattern[i]
                    for i in range(len(valid_j_pattern)-1)]
            unique_diffs = list(set(diffs[:10]))
            print(f"  有効 j の最初の数個: {valid_j_pattern[:10]}")
            print(f"  差分: {diffs[:10]}")
    print()

# ============================================================
# C. 入次数の分布
# ============================================================

print("=" * 70)
print("C. 入次数 (in-degree) の分布")
print("=" * 70)

# N以下の奇数に対する入次数を計算
N = 10000
indegree = Counter()

for n in range(1, N + 1, 2):  # 奇数のみ
    m = syracuse(n)
    indegree[m] += 1

# 入次数の分布
deg_dist = Counter(indegree.values())
total_odd_m = sum(1 for m in range(1, N+1, 2) if m in indegree)

print(f"\nN = {N} 以下の奇数 n に対する入次数分布:")
print(f"  像に現れる m の個数: {len(indegree)}")
for deg in sorted(deg_dist.keys()):
    count = deg_dist[deg]
    print(f"  入次数 {deg}: {count} 個 ({count/len(indegree)*100:.1f}%)")

# m mod 6 別の入次数
print(f"\nm mod 6 別の平均入次数 (m ≤ {N}):")
mod6_deg = defaultdict(list)
for m, deg in indegree.items():
    mod6_deg[m % 6].append(deg)

for r in range(6):
    if mod6_deg[r]:
        avg = sum(mod6_deg[r]) / len(mod6_deg[r])
        print(f"  m ≡ {r} (mod 6): 平均入次数 = {avg:.3f}, サンプル数 = {len(mod6_deg[r])}")
    else:
        print(f"  m ≡ {r} (mod 6): (データなし or 逆像なし)")

# ============================================================
# D. 閉公式の検証
# ============================================================

print()
print("=" * 70)
print("D. 閉公式 |T^{-1}(m) ∩ [1,N]| = floor(log2(3N/m) / period) の検証")
print("=" * 70)

def count_preimages_formula(m, N):
    """
    閉公式: m ≡ 1 (mod 3) => period=2, start=2
             m ≡ 2 (mod 3) => period=2, start は m mod 6 に依存

    正確な公式: 有効 j の最大値は floor(log2((3N+1)/m))
    有効 j は等差数列 j = start + 2k なので
    |T^{-1}(m) ∩ [1,N]| = floor((j_max - start) / 2) + 1 (if j_max >= start)
    """
    if m % 3 == 0:
        return 0

    # n <= N <=> m * 2^j - 1 <= 3N <=> 2^j <= (3N+1)/m
    if 3*N + 1 <= m:
        return 0
    j_max = math.floor(math.log2((3*N + 1) / m))

    # m mod 6 に基づく start と period
    m6 = m % 6
    if m6 == 1:
        start, period = 2, 2
    elif m6 == 5:
        start, period = 1, 2
    elif m6 == 2:
        # m偶数: mが偶数の場合は直接適用不可（Syracuseは奇数→奇数）
        # ただし T^{-1}(m) を考える場合 m は奇数のみ
        return -1  # mが偶数の場合は対象外
    elif m6 == 4:
        return -1
    else:
        return 0

    if j_max < start:
        return 0

    return (j_max - start) // period + 1

# 奇数mに対する検証
print("\n奇数 m に対する閉公式の検証 (N=100000):")
N_test = 100000
errors = 0
tested = 0

for m in range(1, 200, 2):  # 奇数mのみ
    if m % 3 == 0:
        continue

    # 実際の逆像数
    actual_preimages = inverse_syracuse_all(m, j_max=60)
    actual_bounded = [(n, j) for n, j in actual_preimages if n <= N_test]
    actual_count = len(actual_bounded)

    # 閉公式
    formula_count = count_preimages_formula(m, N_test)

    if formula_count != actual_count:
        print(f"  m={m}: 実際={actual_count}, 公式={formula_count} [MISMATCH]")
        errors += 1
    tested += 1

if errors == 0:
    print(f"  全 {tested} ケースで閉公式が一致!")
else:
    print(f"  {tested} ケース中 {errors} 件の不一致")

# ============================================================
# E. v2条件の自動成立の検証
# ============================================================

print()
print("=" * 70)
print("E. v2(3n+1) = j の自動成立の検証")
print("=" * 70)

print("\nn = (m * 2^j - 1) / 3 のとき v2(3n+1) = j を検証:")
v2_ok = 0
v2_fail = 0

for m in range(1, 100, 2):  # 奇数m
    preimages = inverse_syracuse_all(m, j_max=30)
    for n, j in preimages:
        val = 3 * n + 1
        actual_v2 = v2(val)
        if actual_v2 == j:
            v2_ok += 1
        else:
            print(f"  FAIL: m={m}, n={n}, j={j}, v2(3n+1)={actual_v2}")
            v2_fail += 1

print(f"  検証: {v2_ok} 件成功, {v2_fail} 件失敗")

if v2_fail == 0:
    print("  => v2条件は自動的に成立!")
    print()
    print("  証明:")
    print("    n = (m * 2^j - 1) / 3 のとき")
    print("    3n = m * 2^j - 1")
    print("    3n + 1 = m * 2^j")
    print("    m は奇数なので v2(m * 2^j) = v2(m) + j = 0 + j = j")
    print("    よって v2(3n+1) = j  (Q.E.D.)")

# ============================================================
# F. m mod 6 の完全分類表
# ============================================================

print()
print("=" * 70)
print("F. 完全分類定理のまとめ")
print("=" * 70)

print("""
定理 (逆Syracuse写像の完全代数的記述):

Syracuse写像 T: 奇数 → 奇数 を T(n) = (3n+1)/2^{v2(3n+1)} と定義する。
m を正の奇数とするとき:

(1) m ≡ 0 (mod 3) のとき: T^{-1}(m) = 空集合
    理由: 任意の奇数 n に対し 3n+1 ≡ 1 (mod 3) なので
          T(n) = (3n+1)/2^k ≢ 0 (mod 3)

(2) m ≡ 1 (mod 6) のとき:
    T^{-1}(m) = { (m * 2^{2k} - 1) / 3 : k = 1, 2, 3, ... }
    = { (4m-1)/3, (16m-1)/3, (64m-1)/3, ... }
    有効 j: j ∈ {2, 4, 6, 8, ...} (正偶数全体)

(3) m ≡ 5 (mod 6) のとき:
    T^{-1}(m) = { (m * 2^{2k-1} - 1) / 3 : k = 1, 2, 3, ... }
    = { (2m-1)/3, (8m-1)/3, (32m-1)/3, ... }
    有効 j: j ∈ {1, 3, 5, 7, ...} (正奇数全体)

注意: m が偶数の場合、Syracuse写像の値域に偶数は含まれる可能性があるが、
      コラッツ予想の文脈では T は奇数→奇数 の写像として扱う。

系1: |T^{-1}(m) ∩ [1,N]| = floor(log_2(3N/m) / 2) (m≢0 mod3, N十分大)

系2: v2(3n+1) = j は自動的に成立する。
     証明: n = (m*2^j - 1)/3 => 3n+1 = m*2^j, v2(m*2^j) = j (m奇数)

系3: 各 m ≢ 0 (mod 3) に対して、T^{-1}(m) は可算無限集合であり、
     その要素は指数的に増大する（比率 → 4）。
""")

# ============================================================
# G. 新発見の探索: 偶数 m への拡張
# ============================================================

print("=" * 70)
print("G. 偶数 m への拡張分析")
print("=" * 70)

# 偶数 m に対しても T^{-1}(m) を考える
# T(n) = (3n+1)/2^{v2(3n+1)} は奇数を返すので、偶数 m は値域にない
# ただし、「部分」Syracuse T_k(n) = (3n+1)/2^k を考えた場合は異なる

print("\nT(n) の値域は常に奇数であることの確認:")
not_odd_count = 0
for n in range(1, 100000, 2):
    m = syracuse(n)
    if m % 2 == 0:
        not_odd_count += 1
        print(f"  T({n}) = {m} [偶数!]")
if not_odd_count == 0:
    print("  確認: n=1..99999 (奇数) に対し T(n) は常に奇数")

# ============================================================
# H. 入次数の精密分析: m mod 6 と入次数 0 の関係
# ============================================================

print()
print("=" * 70)
print("H. 入次数 0 の奇数 m の分析")
print("=" * 70)

# 大きなNで入次数0のmを見つける
N2 = 50000
reached = set()
for n in range(1, N2 + 1, 2):
    reached.add(syracuse(n))

unreached_by_mod6 = defaultdict(int)
total_by_mod6 = defaultdict(int)
unreached_examples = defaultdict(list)

for m in range(1, N2 + 1, 2):
    total_by_mod6[m % 6] += 1
    if m not in reached:
        unreached_by_mod6[m % 6] += 1
        if len(unreached_examples[m % 6]) < 5:
            unreached_examples[m % 6].append(m)

print(f"\nN = {N2} 以下の奇数 m で T^{{-1}}(m) ∩ [1,{N2}] = 空 となるもの:")
for r in [1, 3, 5]:
    total = total_by_mod6[r]
    unreached = unreached_by_mod6[r]
    if total > 0:
        pct = unreached / total * 100
        print(f"  m ≡ {r} (mod 6): {unreached}/{total} ({pct:.1f}%)")
        if r == 3:
            print(f"    => 全て (3|m なので理論通り)")
        else:
            print(f"    例: {unreached_examples[r]}")
            # これらは T^{-1}(m) が存在するが、最小要素が N より大きいだけ
            for m_ex in unreached_examples[r][:3]:
                preimages = inverse_syracuse_all(m_ex, j_max=60)
                if preimages:
                    min_n = min(n for n, j in preimages)
                    print(f"    m={m_ex}: 最小逆像 n={min_n} (j={[j for n,j in preimages if n==min_n][0]})")

# ============================================================
# I. 逆像の連鎖構造: T^{-k}(m) の成長率
# ============================================================

print()
print("=" * 70)
print("I. 逆像の連鎖: T^{-k}(m) のサイズの成長")
print("=" * 70)

def count_iterated_preimages(m, depth, N_bound):
    """T^{-k}(m) ∩ [1,N_bound] のサイズを k=1,...,depth まで計算"""
    current_set = {m}
    sizes = [1]

    for k in range(1, depth + 1):
        next_set = set()
        for target in current_set:
            preimages = inverse_syracuse_all(target, j_max=60)
            for n, j in preimages:
                if n <= N_bound:
                    next_set.add(n)
        current_set = next_set
        sizes.append(len(current_set))

    return sizes

N_bound = 10**7
for m_root in [1, 5, 7, 11, 13]:
    sizes = count_iterated_preimages(m_root, 8, N_bound)
    ratios = []
    for i in range(1, len(sizes)):
        if sizes[i-1] > 0:
            ratios.append(f"{sizes[i]/sizes[i-1]:.2f}" if sizes[i-1] > 0 else "inf")
    print(f"  m={m_root}: サイズ列 = {sizes}")
    print(f"          成長率 = {ratios}")

# ============================================================
# J. 新発見の候補: j の算術級数構造と m mod 12 分類
# ============================================================

print()
print("=" * 70)
print("J. より精密な分類: m mod 12")
print("=" * 70)

print("\nm mod 12 による逆像の最小要素の分布:")

for m_mod12 in range(12):
    if m_mod12 % 2 == 0:
        continue  # mは奇数のみ
    if m_mod12 % 3 == 0:
        print(f"  m ≡ {m_mod12:2d} (mod 12): 逆像なし (3|m)")
        continue

    min_ns = []
    for m in range(m_mod12, 1000, 12):
        if m == 0:
            continue
        preimages = inverse_syracuse_all(m, j_max=20)
        if preimages:
            min_n = min(n for n, j in preimages)
            min_ns.append(min_n / m)  # 正規化

    if min_ns:
        avg_ratio = sum(min_ns) / len(min_ns)
        print(f"  m ≡ {m_mod12:2d} (mod 12): 平均 min(n)/m = {avg_ratio:.4f}, "
              f"理論値 = {(2**(1 if m_mod12%6==5 else 2) - 1/m):.4f}")

        # 最小のjを特定
        m_test = m_mod12 if m_mod12 > 0 else 12
        preimages = inverse_syracuse_all(m_test, j_max=20)
        if preimages:
            j_list = sorted(j for _, j in preimages)
            print(f"    m={m_test} の有効 j: {j_list[:8]}")
            # 最小 n = (m * 2^{j_min} - 1) / 3
            j_min = j_list[0]
            n_min = (m_test * 2**j_min - 1) // 3
            print(f"    最小逆像: n = (m * 2^{j_min} - 1)/3 = {n_min}")

print()
print("=" * 70)
print("探索完了")
print("=" * 70)
