#!/usr/bin/env python3
"""
平均入次数の正確な理論値の導出

実測で平均入次数 = 4/3 ≈ 1.333 が観測された。
これを理論的に説明する。

核心: T(n) の像に現れる m の個数 = N/2 中の n に対して、
      各 n は1つの m = T(n) を出力する。
      像に現れる異なる m の個数を M とすると、
      平均入次数 = (N/2) / M

問題: M / (N/2) の漸近値は?
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
    val = 3 * n + 1
    return val >> v2(val)

# ============================================================
# 1. 像のサイズ M(N) の精密測定
# ============================================================

print("=" * 70)
print("1. |T([1,N] ∩ Odd)| の精密測定")
print("=" * 70)

for N in [100, 1000, 10000, 100000, 500000]:
    num_inputs = 0
    reached = set()
    for n in range(1, N + 1, 2):
        reached.add(syracuse(n))
        num_inputs += 1

    M = len(reached)
    ratio = M / num_inputs
    avg_indeg = num_inputs / M

    # 奇数の総数のうち像に現れる割合
    total_odd_le_N = (N + 1) // 2
    reach_ratio = M / total_odd_le_N

    print(f"  N = {N:>7d}: 入力数 = {num_inputs}, |像| = {M}, "
          f"|像|/入力 = {ratio:.6f}, 平均入次数 = {avg_indeg:.6f}, "
          f"|像|/全奇数 = {reach_ratio:.6f}")

# ============================================================
# 2. 理論的導出: 平均入次数 = 4/3
# ============================================================

print()
print("=" * 70)
print("2. 平均入次数 = 4/3 の理論的導出")
print("=" * 70)

print("""
観測: 平均入次数 = 4/3, |像|/全奇数 = 3/4

理論的説明:
  [1,N] の奇数は N/2 個（入力数）
  T^{-1}(m) ∩ [1,N] ≠ 空 となる奇数 m の数 = M

  M の計算:
  ・m ≡ 5 (mod 6): n_min = (2m-1)/3 < m なので m ≤ N => 必ず逆像あり
    → N/6 個全て像に含まれる
  ・m ≡ 1 (mod 6): n_min = (4m-1)/3 ≤ N <=> m ≤ (3N+1)/4 ≈ 3N/4
    → m ≤ 3N/4 の範囲で N/8 個が像に含まれる
    （m ≡ 1 mod 6 は m ≤ 3N/4 の範囲に 3N/4 * 1/6 = N/8 個）
  ・m ≡ 3 (mod 6): 逆像なし → 0個

  合計 M ≈ N/6 + N/8 = 7N/24 ???

  しかし実測は M = 3N/8 = 0.375N

  修正: 奇数mのうち
  ・m ≡ 1 (mod 6): 全奇数の 1/3
  ・m ≡ 3 (mod 6): 全奇数の 1/3
  ・m ≡ 5 (mod 6): 全奇数の 1/3
""")

# 正確な数え上げ
print("正確な数え上げ:")
for N in [10000, 100000]:
    total_odd = (N + 1) // 2
    mod1_total = sum(1 for m in range(1, N+1, 2) if m % 6 == 1)
    mod3_total = sum(1 for m in range(1, N+1, 2) if m % 6 == 3)
    mod5_total = sum(1 for m in range(1, N+1, 2) if m % 6 == 5)

    print(f"\n  N={N}: 全奇数={total_odd}")
    print(f"    m≡1(6): {mod1_total} ({mod1_total/total_odd*100:.1f}%)")
    print(f"    m≡3(6): {mod3_total} ({mod3_total/total_odd*100:.1f}%)")
    print(f"    m≡5(6): {mod5_total} ({mod5_total/total_odd*100:.1f}%)")

    # 像に含まれる数
    reached = set()
    for n in range(1, N+1, 2):
        reached.add(syracuse(n))

    r1 = sum(1 for m in reached if m % 6 == 1)
    r3 = sum(1 for m in reached if m % 6 == 3)
    r5 = sum(1 for m in reached if m % 6 == 5)
    r_other = len(reached) - r1 - r3 - r5

    print(f"    像のうち m≡1(6): {r1} ({r1/mod1_total*100:.1f}% of m≡1)")
    print(f"    像のうち m≡3(6): {r3} ({r3/mod3_total*100:.1f}% of m≡3)")
    print(f"    像のうち m≡5(6): {r5} ({r5/mod5_total*100:.1f}% of m≡5)")
    if r_other > 0:
        print(f"    像のうち偶数等: {r_other}")

    # m ≡ 1 (mod 6) で像に含まれるもの: m ≤ 3N/4
    threshold_1 = 3 * N // 4
    r1_theory = sum(1 for m in range(1, threshold_1 + 1, 2) if m % 6 == 1)
    print(f"    m≡1(6)の理論 (m≤3N/4={threshold_1}): {r1_theory}")

    # 合計理論値
    M_theory = r1_theory + mod5_total  # m≡3は0
    print(f"    |像|理論 = {M_theory}, |像|実測 = {len(reached)}")
    print(f"    |像|/全奇数 理論 = {M_theory/total_odd:.4f}, 実測 = {len(reached)/total_odd:.4f}")

# ============================================================
# 3. 像の密度 3/4 の厳密証明
# ============================================================

print()
print("=" * 70)
print("3. |像|/全奇数 = 3/4 の厳密証明")
print("=" * 70)

print("""
定理: |T([1,N] ∩ Odd)|  / |[1,N] ∩ Odd| → 3/4  as N → ∞

証明:
  奇数 m ≤ N のうち T^{-1}(m) ∩ [1,N] ≠ 空 となるのは:

  Case 1: m ≡ 5 (mod 6)
    n_min = (2m-1)/3 < m ≤ N  →  常に [1,N] 内に逆像あり
    → 全 m ≡ 5 (mod 6), m ≤ N が像に含まれる
    → 個数 ≈ N/6

  Case 2: m ≡ 1 (mod 6)
    n_min = (4m-1)/3 ≤ N  <=>  m ≤ (3N+1)/4
    → m ≡ 1 (mod 6), m ≤ 3N/4 が像に含まれる
    → 個数 ≈ (3N/4) / 6 = N/8

  Case 3: m ≡ 3 (mod 6)
    逆像なし → 0個

  合計: N/6 + N/8 = 7N/24

  しかし実測は 3N/8 = 9N/24

  差分: 像に含まれるが N を超える m が存在する！
  つまり T(n) > N となる n ≤ N が存在し、その像 m > N も数えている。
""")

# 像が N を超えるケースの分析
print("像の範囲分析:")
for N in [10000, 100000]:
    reached_le_N = 0
    reached_gt_N = 0
    all_reached = set()
    for n in range(1, N + 1, 2):
        m = syracuse(n)
        all_reached.add(m)
        if m <= N:
            reached_le_N += 1
        else:
            reached_gt_N += 1

    m_le_N_in_image = sum(1 for m in all_reached if m <= N)
    m_gt_N_in_image = sum(1 for m in all_reached if m > N)
    total_odd = (N + 1) // 2

    print(f"\n  N={N}:")
    print(f"    入力 n ≤ N: {total_odd}")
    print(f"    像の異なる値の総数: {len(all_reached)}")
    print(f"    像 m ≤ N の異なる値: {m_le_N_in_image} ({m_le_N_in_image/total_odd*100:.1f}%)")
    print(f"    像 m > N の異なる値: {m_gt_N_in_image}")
    print(f"    max(像): {max(all_reached)}")

    # n→T(n)で T(n) > N となる n の割合
    upward = sum(1 for n in range(1, N+1, 2) if syracuse(n) > N)
    print(f"    T(n) > N となる n の数: {upward} ({upward/total_odd*100:.1f}%)")

# ============================================================
# 4. 正しい像密度の導出
# ============================================================

print()
print("=" * 70)
print("4. 正しい像密度の導出")
print("=" * 70)

print("""
修正: |T([1,N] ∩ Odd) ∩ [1,N]| / |[1,N] ∩ Odd| を計算する。

実測から |image ∩ [1,N]| / (N/2) = 0.75 = 3/4

再分析:
  奇数 m ≤ N が像に含まれる条件:
  ∃ odd n ≤ N such that T(n) = m

  m ≡ 5 (mod 6): n_min = (2m-1)/3 ≤ N iff m ≤ (3N+1)/2
    m ≤ N < (3N+1)/2 なので常に成立
    → N/6 個

  m ≡ 1 (mod 6): n_min = (4m-1)/3 ≤ N iff m ≤ (3N+1)/4
    → (3N+1)/4 以下の m ≡ 1 (mod 6) の個数 ≈ N/8

  しかし N/6 + N/8 = 7N/24 ≈ 0.292N ≠ 0.375N

  何が足りない?
  → m ≡ 1 (mod 6) で m > 3N/4 でも、j > 2 の逆像 n ≤ N が存在する場合がある？
  → いや、j=2 が最小なので n_min > N なら全ての逆像 > N。

  正しい計算: m ≡ 5 (mod 6) で m > N の場合も数える必要がある。
  T(n) = m > N が成り立つ n ≤ N が存在する。
""")

# 再度正確に数える
N = 100000
reached_in_N = set()
for n in range(1, N + 1, 2):
    m = syracuse(n)
    if m <= N and m % 2 == 1:
        reached_in_N.add(m)

total_odd_N = (N + 1) // 2

# mod 6 別
for r in [1, 3, 5]:
    count_in_image = sum(1 for m in reached_in_N if m % 6 == r)
    count_total = sum(1 for m in range(r, N + 1, 6))
    frac = count_in_image / count_total if count_total > 0 else 0
    print(f"  m ≡ {r} (mod 6): 像内 {count_in_image} / 全 {count_total} = {frac:.4f}")

print(f"\n  全体: 像内 {len(reached_in_N)} / 全奇数 {total_odd_N} = {len(reached_in_N)/total_odd_N:.4f}")

# T(n) = m の分布をもう少し詳しく
# T(n) = m のとき、n = (m * 2^j - 1)/3, v2(3n+1) = j
# n ≤ N で m ≤ N のケース数

print("\nv2(3n+1) = j の分布（n ≤ N, T(n) ≤ N）:")
j_dist = Counter()
j_total = Counter()
for n in range(1, N + 1, 2):
    j_val = v2(3 * n + 1)
    j_total[j_val] += 1
    if syracuse(n) <= N:
        j_dist[j_val] += 1

for j in sorted(j_total.keys())[:12]:
    total_j = j_total[j]
    in_N_j = j_dist.get(j, 0)
    print(f"  j={j:2d}: 総数={total_j:6d} ({total_j/(N//2)*100:.1f}%), "
          f"T(n)≤N: {in_N_j:6d} ({in_N_j/total_j*100:.1f}%)")

# ============================================================
# 5. 決定的な分析: 75% の由来
# ============================================================

print()
print("=" * 70)
print("5. 像密度 3/4 の由来")
print("=" * 70)

# 全奇数 n ≤ N のうち T(n) ≤ N となる割合
stay_in = sum(1 for n in range(1, N+1, 2) if syracuse(n) <= N)
total = N // 2
print(f"  T(n) ≤ N となる n の割合: {stay_in}/{total} = {stay_in/total:.4f}")

# v2(3n+1) = 1 のとき T(n) = (3n+1)/2 ≈ 3n/2 > n → T(n) > N iff n > 2N/3
# v2(3n+1) = 2 のとき T(n) = (3n+1)/4 ≈ 3n/4 < n → T(n) ≤ N iff n ≤ 4N/3 (常に)
# 一般: v2(3n+1) = j のとき T(n) ≈ 3n/2^j

# v2分布: v2(3n+1) = j の確率 ≈ 1/2^j (j ≥ 1, nが奇数のとき)
# T(n) > N <=> 3n/2^j > N <=> n > N*2^j/3
# P(T(n) > N | v2=j) ≈ max(0, 1 - N*2^j/(3*N)) = max(0, 1 - 2^j/3)
# j=1: P = 1 - 2/3 = 1/3
# j≥2: P = 1 - 2^j/3 < 0 → P = 0

# P(T(n) > N) ≈ P(v2=1) * P(T(n)>N|v2=1) = (1/2) * (1/3) = 1/6
# P(T(n) ≤ N) ≈ 1 - 1/6 = 5/6

# これでは 5/6 ≠ 3/4。v2の分布をもっと正確に見る必要がある

print("\nv2(3n+1) の分布 (n odd, n ≤ N):")
v2_dist = Counter()
for n in range(1, N + 1, 2):
    v2_dist[v2(3*n+1)] += 1

for j in range(1, 10):
    c = v2_dist.get(j, 0)
    print(f"  v2={j}: {c}/{total} = {c/total:.6f} (理論 1/2^j = {1/2**j:.6f})")

# 各 j での T(n) > N の割合
print("\n各 j での T(n) > N の割合:")
for j in range(1, 8):
    # v2(3n+1) = j の n: n ≡ (2^j - 1)/3 (mod 2^j) [適切な残基]
    count_j = v2_dist.get(j, 0)
    exceed_j = sum(1 for n in range(1, N+1, 2) if v2(3*n+1) == j and syracuse(n) > N)
    if count_j > 0:
        print(f"  j={j}: T(n)>N は {exceed_j}/{count_j} = {exceed_j/count_j:.4f}")
        # 理論: n > N*2^j/3 の割合
        threshold = N * 2**j / 3
        theory = max(0, (N - threshold) / N) if threshold < N else 0
        print(f"       理論 (n > N*2^j/3): {theory:.4f}")

# 正確な計算:
# T(n) > N <=> (3n+1)/2^j > N <=> n > (N*2^j - 1)/3
# j=1: n > (2N-1)/3 ≈ 2N/3
#   v2=1 の n は n ≡ 1 (mod 4) つまり n = 1,5,9,...
#   n > 2N/3 の割合 ≈ 1/3
#   寄与: (1/2) * (1/3) = 1/6
# j=2: n > (4N-1)/3 ≈ 4N/3 > N => 全て T(n) ≤ N
#   寄与: 0
# j≥2: 同様に 0

# よって P(T(n) > N) ≈ 1/6
# しかし実測は 1 - 0.75 ≠ 1/6

# 再計算
exceed_total = sum(1 for n in range(1, N+1, 2) if syracuse(n) > N)
print(f"\n  T(n) > N: {exceed_total}/{total} = {exceed_total/total:.4f}")
print(f"  T(n) ≤ N: {total - exceed_total}/{total} = {(total-exceed_total)/total:.4f}")

# 像密度は「T(n) ≤ N の割合」ではない。
# 像密度 = |{m ≤ N : ∃n ≤ N, T(n)=m}| / |{m ≤ N : m odd}|
# 全く別物！

print()
print("=" * 70)
print("決定的発見: 像密度 3/4 のメカニズム")
print("=" * 70)

print("""
正しい理解:

像密度 = |{m odd, m ≤ N : T^{-1}(m) ∩ [1,N] ≠ 空}| / |{m odd, m ≤ N}|

m ≡ 3 (mod 6): 3|m なので決して像にならない → 0/N*1/6 = 0
  奇数の 1/3 が消去される → 上限 2/3

m ≡ 5 (mod 6): n_min(m) = (2m-1)/3 < m → 常に像に含まれる
  → 奇数の 1/3 が確実に像

m ≡ 1 (mod 6): n_min(m) = (4m-1)/3 ≤ N iff m ≤ 3(N+1)/4
  → m ≤ 3N/4 の範囲の m ≡ 1 (mod 6) のみ
  → 奇数 m ≤ N の 1/3 のうち 3/4 = 1/4

合計: 0 + 1/3 + 1/4 = 7/12 ≈ 0.583...
  → これでも 3/4 にならない！

問題: 上の計算は「最小 j のみ」で判定している。
j > 2（m≡1 mod 6）の場合、j=4 の逆像 n=(16m-1)/3 ≤ N iff m ≤ (3N+1)/16
これは m ≤ 3N/4 に含まれるので追加にならない。
しかし m > 3N/4 の場合でも、他の m' の逆像が m の近くに来る可能性がある。

→ いや、T^{-1}(m) の要素は m に対して決定的。
   m > 3N/4 で m ≡ 1 (mod 6) なら [1,N] に逆像なし。
""")

# もう一度丁寧に数える
for N in [100000]:
    total_odd = 0
    mod1_in = 0
    mod1_total = 0
    mod3_in = 0
    mod3_total = 0
    mod5_in = 0
    mod5_total = 0

    reached = set()
    for n in range(1, N+1, 2):
        reached.add(syracuse(n))

    for m in range(1, N+1, 2):
        total_odd += 1
        r = m % 6
        if r == 1:
            mod1_total += 1
            if m in reached:
                mod1_in += 1
        elif r == 3:
            mod3_total += 1
            if m in reached:
                mod3_in += 1
        elif r == 5:
            mod5_total += 1
            if m in reached:
                mod5_in += 1

    print(f"\nN={N} 精密数え上げ:")
    print(f"  全奇数: {total_odd}")
    print(f"  m≡1(6): {mod1_in}/{mod1_total} = {mod1_in/mod1_total:.6f}")
    print(f"  m≡3(6): {mod3_in}/{mod3_total} = {mod3_in/mod3_total:.6f}")
    print(f"  m≡5(6): {mod5_in}/{mod5_total} = {mod5_in/mod5_total:.6f}")
    print(f"  合計像: {mod1_in+mod3_in+mod5_in}/{total_odd} = {(mod1_in+mod3_in+mod5_in)/total_odd:.6f}")

    # m ≡ 1 (mod 6) の像率 = 0.75 = 3/4 !!!
    # → m ≡ 1 (mod 6) で m ≤ 3N/4 のもの
    print(f"\n  m≡1(6)で m ≤ 3N/4={3*N//4}: ", end="")
    count_le = sum(1 for m in range(1, 3*N//4 + 1, 2) if m % 6 == 1)
    print(f"{count_le} (率: {count_le/mod1_total:.6f})")

    # → 全体の像密度 = (0 + mod1_rate * 1/3 + 1 * 1/3) = (3/4 * 1/3 + 1/3) = 1/4 + 1/3 = 7/12 ???
    # 計算が合わない... 直接確認
    print(f"\n  直接計算: 像密度 = {(mod1_in+mod5_in)/total_odd:.6f}")
    print(f"  = mod1_in/total + mod5_in/total")
    print(f"  = {mod1_in/total_odd:.6f} + {mod5_in/total_odd:.6f}")
    print(f"  mod1_in/total_odd ≈ {mod1_in}/{total_odd} = 3/4 * 1/3 = 1/4 = {1/4:.6f}")
    print(f"  mod5_in/total_odd ≈ {mod5_in}/{total_odd} = 1 * 1/3 = 1/3 = {1/3:.6f}")
    print(f"  合計: 1/4 + 1/3 = 7/12 = {7/12:.6f}")

    # 7/12 ≈ 0.583 ≠ 0.75。何が間違っている?
    # あ、T(n) の像にはNを超える m も含まれるが、ここでは m ≤ N のみを見ている。
    # T(n) で n ≤ N のとき m = T(n) > N となるケースがある。
    # その m > N の逆像 n' ≤ N が別にあるかもしれない。
    # → いや、m > N の場合は数えていない。

    # 間違いに気づいた:
    # reached は T(n) の全ての像を含む。m > N のものも含む。
    # reached ∩ [1,N] を見るべき。
    reached_le_N = sum(1 for m in reached if m <= N and m % 2 == 1)
    print(f"\n  |reached ∩ [1,N] ∩ Odd| = {reached_le_N}")
    print(f"  率 = {reached_le_N / total_odd:.6f}")

    # 合わない... reached_le_N が先ほどの合計と同じか確認
    print(f"  mod1+mod3+mod5 = {mod1_in+mod3_in+mod5_in}")

print()
print("=" * 70)
print("最終分析完了")
print("=" * 70)
