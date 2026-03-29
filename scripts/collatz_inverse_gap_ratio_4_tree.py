#!/usr/bin/env python3
"""
逆像ギャップ比=4の形式化設計とT^{-k}木の分岐構造

目的:
1. 逆像閉公式 |T^{-1}(m) ∩ [1,N]| = floor(log_2(3N/m) / 2) の厳密検証
2. 各ステップで逆像数が約4/3に増加することの証明
3. T^{-k}木の分岐構造の詳細分析
4. 形式化可能な補題の特定

理論的背景:
- Syracuse T(n) = (3n+1)/2^{v2(3n+1)} (奇数→奇数)
- T^{-1}(m): m≡1(mod6) => j∈{2,4,6,...}, m≡5(mod6) => j∈{1,3,5,...}
- 逆像 n_k = (m*2^j - 1)/3 where j = start + 2k
- 連続する逆像の比: n_{k+1}/n_k → 4 (ギャップ比)
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
    """Syracuse map T(n) = (3n+1)/2^{v2(3n+1)}"""
    assert n > 0 and n % 2 == 1, f"n={n} must be odd positive"
    val = 3 * n + 1
    return val >> v2(val)

def inverse_syracuse(m, j_max=60):
    """T^{-1}(m) の要素を列挙: n = (m*2^j - 1)/3"""
    results = []
    for j in range(1, j_max + 1):
        numerator = m * (1 << j) - 1
        if numerator % 3 == 0:
            n = numerator // 3
            if n > 0 and n % 2 == 1:
                results.append((n, j))
    return results

def inverse_syracuse_bounded(m, N, j_max=100):
    """T^{-1}(m) ∩ [1,N] の要素を列挙"""
    results = []
    for j in range(1, j_max + 1):
        numerator = m * (1 << j) - 1
        if numerator > 3 * N:
            break
        if numerator % 3 == 0:
            n = numerator // 3
            if n > 0 and n % 2 == 1 and n <= N:
                results.append((n, j))
    return results

# ============================================================
# Part 1: ギャップ比=4の厳密検証
# ============================================================

print("=" * 70)
print("Part 1: 連続逆像のギャップ比 = 4 の厳密検証")
print("=" * 70)

print("""
理論:
  m ≡ 1 (mod 6): 逆像 n_k = (m * 4^k - 1) / 3  (k=1,2,3,...)
                  [有効j = 2k]
  m ≡ 5 (mod 6): 逆像 n_k = (m * 2 * 4^{k-1} - 1) / 3  (k=1,2,3,...)
                  [有効j = 2k-1]

  いずれの場合も: n_{k+1} / n_k = 4 * (m * 2^{j+2} - 1) / (m * 2^j - 1)
                                  → 4 as k→∞

  正確には: n_{k+1} = 4*n_k + 1  (m ≡ 1 mod 6)
            n_{k+1} = 4*n_k + 1  (m ≡ 5 mod 6)
""")

# 代数的検証
print("代数的検証:")
print()
for m_mod6 in [1, 5]:
    if m_mod6 == 1:
        start = 2
    else:
        start = 1

    print(f"  m ≡ {m_mod6} (mod 6), start j = {start}:")
    print(f"    n_k = (m * 2^({start}+2(k-1)) - 1) / 3")
    print(f"    n_{{k+1}} = (m * 2^({start}+2k) - 1) / 3")
    print(f"    n_{{k+1}} = (m * 4 * 2^({start}+2(k-1)) - 1) / 3")
    print(f"           = (4 * m * 2^({start}+2(k-1)) - 1) / 3")
    print(f"           = (4 * (m * 2^({start}+2(k-1)) - 1) + 4 - 1) / 3")
    print(f"           = (4 * 3 * n_k + 3) / 3")
    print(f"           = 4 * n_k + 1")
    print()

# 数値検証
print("数値検証:")
exact_match = 0
total_checks = 0

for m in range(1, 200, 2):
    if m % 3 == 0:
        continue
    preimages = inverse_syracuse(m, j_max=40)
    if len(preimages) < 2:
        continue

    for i in range(len(preimages) - 1):
        n_k, j_k = preimages[i]
        n_k1, j_k1 = preimages[i+1]

        # 検証: n_{k+1} = 4*n_k + 1
        expected = 4 * n_k + 1
        if expected == n_k1:
            exact_match += 1
        else:
            print(f"  FAIL: m={m}, n_k={n_k}, n_{{k+1}}={n_k1}, expected={expected}")
        total_checks += 1

print(f"  検証結果: {exact_match}/{total_checks} ケースで n_{{k+1}} = 4*n_k + 1 が成立")
print()

# ============================================================
# Part 2: 閉公式の厳密導出と検証
# ============================================================

print("=" * 70)
print("Part 2: 閉公式 |T^{-1}(m) ∩ [1,N]| の厳密導出と検証")
print("=" * 70)

print("""
閉公式の導出:
  n_k ≤ N ⟺ (m * 2^j_k - 1) / 3 ≤ N ⟺ m * 2^j_k ≤ 3N + 1
           ⟺ j_k ≤ log_2((3N+1)/m)

  j_k = start + 2(k-1) なので:
    start + 2(k-1) ≤ log_2((3N+1)/m)
    k ≤ (log_2((3N+1)/m) - start) / 2 + 1
    k ≤ floor((log_2((3N+1)/m) - start) / 2) + 1

  最大 k: k_max = floor((floor(log_2((3N+1)/m)) - start) / 2) + 1
         = floor((J - start) / 2) + 1  where J = floor(log_2((3N+1)/m))
         (J ≥ start のとき。J < start なら 0)

  統一公式 (m ≢ 0 mod 3):
    start = 2  if m ≡ 1 (mod 6)
    start = 1  if m ≡ 5 (mod 6)

  簡略化:
    J = floor(log_2(3N/m))  (N >> m のとき (3N+1)/m ≈ 3N/m)
    |T^{-1}(m) ∩ [1,N]| ≈ floor(J / 2)  (近似)
""")

def closed_form_preimage_count(m, N):
    """
    厳密な閉公式: |T^{-1}(m) ∩ [1,N]|
    """
    if m % 3 == 0 or m % 2 == 0:
        return 0

    bound = 3 * N + 1
    if bound <= m:
        return 0

    # J = floor(log_2((3N+1)/m))
    # 整数演算で正確に計算
    J = (bound // m).bit_length() - 1
    # 検証: 2^J ≤ (3N+1)/m < 2^{J+1}
    while (1 << J) > bound // m:
        J -= 1
    while (1 << (J + 1)) <= bound // m:
        J += 1

    m6 = m % 6
    if m6 == 1:
        start = 2
    elif m6 == 5:
        start = 1
    else:
        return 0  # should not reach for odd m not div by 3

    if J < start:
        return 0

    return (J - start) // 2 + 1

# 大規模検証
print("大規模数値検証:")
for N in [1000, 10000, 100000, 1000000]:
    errors = 0
    tested = 0
    total_actual = 0
    total_formula = 0

    for m in range(1, min(N, 2000), 2):
        if m % 3 == 0:
            continue

        # 実際の逆像数
        actual = len(inverse_syracuse_bounded(m, N))
        # 閉公式
        formula = closed_form_preimage_count(m, N)

        total_actual += actual
        total_formula += formula

        if actual != formula:
            errors += 1
            if errors <= 3:
                print(f"    MISMATCH at m={m}: actual={actual}, formula={formula}")
        tested += 1

    print(f"  N={N:>8d}: {tested} テスト, {errors} 不一致, "
          f"合計逆像数(実際/公式): {total_actual}/{total_formula}")
print()

# ============================================================
# Part 3: T^{-k}木の分岐構造の解析
# ============================================================

print("=" * 70)
print("Part 3: T^{-k}木の分岐構造（逆BFS成長率の理論）")
print("=" * 70)

print("""
理論:
  T^{-1}(m) の要素数は N 以下で約 floor(log_2(3N/m) / 2) 個。
  全 m の合計: Σ_{m odd, m≤N, 3∤m} |T^{-1}(m) ∩ [1,N]|

  これは「[1,N] の奇数のうち Syracuse 写像で到達される奇数の総数」= N/2
  （各 n ∈ [1,N] の奇数が正確に1つの m = T(n) に寄与）

  平均入次数 = (N/2) / |image(T) ∩ [1,N]|

  image のサイズ:
    m ≡ 5(mod6) の最小逆像 n_min = (2m-1)/3 < m なので必ず像に入る
    m ≡ 1(mod6) の最小逆像 n_min = (4m-1)/3 > m なので m ≤ 3N/4 のとき像

  |image ∩ [1,N]| ≈ N/6 + N/8 + ... = N * (1/6 + 1/8) = N * 7/24 ≈ 0.29N
  ... いや、より正確には:

  奇数 m ≤ N のうち 3∤m のものは (N/2) * (2/3) = N/3 個
  うち像に入るもの:
    m≡5(mod6): N/6個全て像に入る (n_min < m < N)
    m≡1(mod6): 3N/(4*6) = N/8 個が像に入る
  合計 ≈ N/6 + N/8 = 7N/24

  ... 再計算が必要。直接計測する。
""")

# 直接計測: 逆BFS成長率
print("逆BFS (T^{-k}) 成長率の直接計測:")
print()

for root in [1, 3, 5, 7, 11, 13]:
    current_layer = {root}
    all_visited = {root}

    print(f"  root = {root}:")
    for depth in range(1, 13):
        next_layer = set()
        for m in current_layer:
            for n, j in inverse_syracuse(m, j_max=50):
                if n not in all_visited and n < 10**12:
                    next_layer.add(n)

        all_visited |= next_layer

        if len(current_layer) > 0:
            growth = len(next_layer) / len(current_layer)
        else:
            growth = 0

        if depth <= 8:
            print(f"    depth {depth:2d}: |layer| = {len(next_layer):>10d}, "
                  f"growth = {growth:.4f}")

        current_layer = next_layer
        if not current_layer:
            break

    print(f"    total visited = {len(all_visited)}")
    print()

# ============================================================
# Part 4: 平均入次数 = 4/3 の厳密な導出
# ============================================================

print("=" * 70)
print("Part 4: 平均入次数 = 4/3 の厳密な代数的導出")
print("=" * 70)

print("""
定理: Syracuse 写像 T の平均入次数は 4/3

証明:
  [1,N] の奇数全体を S_N = {1,3,5,...,N-1} とする (|S_N| = N/2)。

  各 n ∈ S_N に対し T(n) を計算すると、像は奇数になる。
  合計入力数 = |S_N| = N/2。

  像のサイズ M = |T(S_N)| を計算する。

  各奇数 m ≢ 0 (mod 3) に対し、T^{-1}(m) ∩ S_N の要素数を数える:

  (A) m ≡ 5 (mod 6): 最小逆像 n_min = (2m-1)/3
      n_min/m = (2m-1)/(3m) → 2/3 < 1
      よって m ≤ N なら n_min ≤ N（ほぼ必ず）
      → 約 N/6 個の m が像に入る

  (B) m ≡ 1 (mod 6): 最小逆像 n_min = (4m-1)/3
      n_min/m = (4m-1)/(3m) → 4/3 > 1
      n_min ≤ N ⟺ m ≤ (3N+1)/4 ≈ 3N/4
      → m ≤ 3N/4 のうち m ≡ 1 (mod 6) のもの: 約 (3N/4)/6 = N/8 個

  合計: M ≈ N/6 + N/8 = 7N/24

  ... しかし実測値は M ≈ 3N/8 (= 0.375N) のはず (平均入次数4/3から逆算)。

  再考が必要。正確な計算を行う。
""")

# 正確な計測
print("正確な |image(T) ∩ [1,N]| / (N/2) の計測:")
for N in [10000, 50000, 100000, 500000]:
    inputs = 0
    image_set = set()
    for n in range(1, N + 1, 2):
        m = syracuse(n)
        image_set.add(m)
        inputs += 1

    M = len(image_set)
    avg_indeg = inputs / M
    image_ratio = M / inputs

    # mod 6 分類
    mod6_counts = Counter()
    for m in image_set:
        mod6_counts[m % 6] += 1

    print(f"  N={N:>7d}: inputs={inputs}, |image|={M}, "
          f"avg_indeg={avg_indeg:.6f}, |image|/inputs={image_ratio:.6f}")
    print(f"    image mod 6: {dict(sorted(mod6_counts.items()))}")
print()

# ============================================================
# Part 5: 各 mod6 クラスの入次数の理論解析
# ============================================================

print("=" * 70)
print("Part 5: 入次数の mod 6 分類の精密分析")
print("=" * 70)

for N in [100000]:
    # 全奇数の入次数を計算
    indeg = Counter()
    for n in range(1, N + 1, 2):
        m = syracuse(n)
        indeg[m] += 1

    # mod 6 別の入次数分布
    mod6_degs = defaultdict(list)
    for m, deg in indeg.items():
        mod6_degs[m % 6].append(deg)

    # 入次数0 (像に現れないm) の数
    all_odd_m = set(range(1, N + 1, 2))
    not_in_image = all_odd_m - set(indeg.keys())
    mod6_notimg = Counter()
    for m in not_in_image:
        mod6_notimg[m % 6] += 1

    print(f"N={N}:")
    print(f"  入次数0のm (像に現れない): {len(not_in_image)}")
    print(f"  mod 6 別の像外の数: {dict(sorted(mod6_notimg.items()))}")

    for r in sorted(mod6_degs.keys()):
        degs = mod6_degs[r]
        avg = sum(degs) / len(degs) if degs else 0
        deg_dist = Counter(degs)
        print(f"  m ≡ {r} (mod 6): count={len(degs)}, avg_indeg={avg:.4f}, "
              f"deg_dist={dict(sorted(deg_dist.items()))}")

    # 入次数0をmod6=3のmが全てカバーするか確認
    mod3_0 = sum(1 for m in not_in_image if m % 3 == 0)
    mod3_nonzero = len(not_in_image) - mod3_0
    print(f"  像外のうち 3|m: {mod3_0}, 3∤m: {mod3_nonzero}")
print()

# ============================================================
# Part 6: 逆像ギャップ比=4 の帰結と T^{-k} 木のサイズ
# ============================================================

print("=" * 70)
print("Part 6: T^{-k}(m) のサイズの理論予測")
print("=" * 70)

print("""
T^{-1}(m) の各要素 n に対して、T^{-1}(n) を再帰的に取ると木が得られる。

ギャップ比=4の帰結:
  T^{-1}(m) ∩ [1,N] の要素数 ≈ log_4(3N/m)  (≈ log_2(3N/m)/2)

  T^{-k}(m) のサイズは、各ノードが平均 4/3 個の子を持つ木。

  厳密には:
  - m ≡ 5 (mod 6) の逆像は j=1,3,5,... を使い、最小逆像 (2m-1)/3
  - m ≡ 1 (mod 6) の逆像は j=2,4,6,... を使い、最小逆像 (4m-1)/3

  m mod 3 による分岐:
  - m ≡ 1 (mod 3) => m ≡ 1 (mod 6): 最小逆像比 4/3 (膨張)
  - m ≡ 2 (mod 3) => m ≡ 5 (mod 6): 最小逆像比 2/3 (縮小)

  平均: (1/2)(4/3) + (1/2)(2/3) = 1  ← 最小逆像だけでは成長しない

  しかし追加の逆像（4倍ずつ増加）が寄与するため、
  全体では成長率 > 1 になる。
""")

# T^{-k}(1) のサイズを計測
print("T^{-k}(1) のサイズ (N制限なし、値の上限で制限):")
for upper in [10**6, 10**8, 10**10]:
    current = {1}
    all_nodes = {1}

    for depth in range(1, 20):
        next_set = set()
        for m in current:
            preims = inverse_syracuse(m, j_max=80)
            for n, j in preims:
                if n <= upper and n not in all_nodes:
                    next_set.add(n)

        all_nodes |= next_set
        if len(current) > 0:
            growth = len(next_set) / len(current) if len(current) > 0 else 0
        else:
            growth = 0

        print(f"  upper={upper:.0e}, depth {depth:2d}: "
              f"|layer|={len(next_set):>10d}, |total|={len(all_nodes):>10d}, "
              f"growth={growth:.4f}")

        current = next_set
        if not current:
            break
    print()

# ============================================================
# Part 7: 形式化設計
# ============================================================

print("=" * 70)
print("Part 7: Lean 4 形式化設計")
print("=" * 70)

print("""
形式化ターゲット（優先度順）:

1. [確実] n_{k+1} = 4*n_k + 1 (逆像の漸化式)
   -- 既存の逆像公式 n = (m*2^j - 1)/3 から直接導出
   theorem inverse_preimage_recurrence (m n_k : Nat)
     (hm : m % 2 = 1) (hm3 : m % 3 != 0)
     (hn : 3 * n_k + 1 = m * 2^j) :
     exists n_{k+1}, 3 * n_{k+1} + 1 = m * 2^(j+2)
       /\\ n_{k+1} = 4 * n_k + 1

   証明: n_{k+1} = (m*2^{j+2} - 1)/3 = (4*m*2^j - 1)/3
                  = (4*(3*n_k + 1) - 1)/3 = (12*n_k + 3)/3 = 4*n_k + 1

2. [確実] v2条件の自動成立
   theorem v2_of_inverse_preimage (m j : Nat)
     (hm : m % 2 = 1) :
     v2(m * 2^j) = j

   証明: v2_mul + v2_odd + v2_pow_two (既存)

3. [中程度] 閉公式
   theorem preimage_count_formula (m N : Nat)
     (hm : m % 2 = 1) (hm3 : m % 3 != 0) :
     |{n : Nat | n <= N /\\ n % 2 = 1 /\\ syracuse n = m}|
       = closed_form(m, N)

4. [発展] 平均入次数 = 4/3
   -- 密度引数が必要で形式化は困難
""")

# ============================================================
# Part 8: 漸化式 n_{k+1} = 4*n_k + 1 の代数的検証（厳密版）
# ============================================================

print("=" * 70)
print("Part 8: 漸化式の代数的証明の詳細")
print("=" * 70)

print("""
補題: m を正の奇数で 3 ∤ m とする。
      n = (m * 2^j - 1) / 3 が T^{-1}(m) の要素のとき、
      n' = (m * 2^{j+2} - 1) / 3 も T^{-1}(m) の要素で、
      n' = 4n + 1 が成り立つ。

証明:
  3n = m * 2^j - 1  ...(*)
  3n' = m * 2^{j+2} - 1 = 4 * m * 2^j - 1
      = 4 * (3n + 1) - 1      [(*) より m*2^j = 3n+1]
      = 12n + 3

  よって n' = (12n + 3) / 3 = 4n + 1。

  T(n') = m の確認:
    3n' + 1 = 12n + 4 = 4 * (3n + 1) = 4 * m * 2^j = m * 2^{j+2}
    v2(3n'+1) = v2(m * 2^{j+2}) = j+2  (m が奇数なので)
    T(n') = (3n'+1) / 2^{j+2} = m * 2^{j+2} / 2^{j+2} = m  ✓

  n' の奇数性:
    n' = 4n + 1 ≡ 1 (mod 2) ✓ (常に奇数)

  n' の正性:
    n ≥ 1 => n' = 4n + 1 ≥ 5 > 0 ✓
""")

# ============================================================
# Part 9: 形式化用の最終まとめ
# ============================================================

print("=" * 70)
print("Part 9: 形式化可能な定理一覧と依存関係")
print("=" * 70)

print("""
確実に形式化可能な定理:

A. 基盤 (既存の補題を使用):
   - v2_odd_mul: a が奇数なら v2(a*b) = v2(b)  [Structure.lean に存在]
   - v2_mul: v2(a*b) = v2(a) + v2(b)  [Structure.lean に存在]

B. 新規定理:

   B1. syracuse_preimage_char:
       n が正の奇数、m が正の奇数のとき:
       syracuse(n) = m ⟺ ∃ j ≥ 1, 3*n+1 = m * 2^j ∧ v2(3*n+1) = j
       ⟺ ∃ j ≥ 1, n = (m*2^j - 1)/3 ∧ 3 | (m*2^j - 1) ∧ m % 2 = 1

   B2. preimage_gap_ratio_4:
       syracuse(n) = m ∧ v2(3*n+1) = j
       ⟹ syracuse(4*n+1) = m ∧ v2(3*(4*n+1)+1) = j+2

       証明: 3*(4n+1)+1 = 12n+4 = 4*(3n+1) = 4*m*2^j = m*2^{j+2}
             v2(m*2^{j+2}) = j+2  (m奇数)
             (4n+1) は奇数

   B3. preimage_gap_ratio_4_odd:
       4*n+1 は常に奇数  (自明)

   B4. preimage_mod6_classification:
       m ≡ 1 (mod 6): T^{-1}(m) の最小要素は (4m-1)/3
       m ≡ 5 (mod 6): T^{-1}(m) の最小要素は (2m-1)/3
       m ≡ 3 (mod 6): T^{-1}(m) = 空

依存関係: B1 は Defs.lean の syracuse, v2 を使用
          B2 は B1 + v2_odd_mul を使用
          B4 は B1 + mod 6 の算術を使用
""")

# 最終検証: B2 の数値テスト
print("\n最終検証: B2 (preimage_gap_ratio_4) の包括的テスト")
success = 0
fail = 0

for m in range(1, 1000, 2):
    if m % 3 == 0:
        continue
    for n in range(1, 500, 2):
        if syracuse(n) == m:
            j = v2(3 * n + 1)
            n_prime = 4 * n + 1

            # 検証
            if syracuse(n_prime) != m:
                print(f"  FAIL: T({n_prime}) = {syracuse(n_prime)} != {m}")
                fail += 1
            elif v2(3 * n_prime + 1) != j + 2:
                print(f"  FAIL: v2(3*{n_prime}+1) = {v2(3*n_prime+1)} != {j+2}")
                fail += 1
            else:
                success += 1

print(f"  結果: {success} 成功, {fail} 失敗")
if fail == 0:
    print("  => B2 は全テストケースで成立!")
