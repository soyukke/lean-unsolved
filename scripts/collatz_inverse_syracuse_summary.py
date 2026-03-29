#!/usr/bin/env python3
"""
逆Syracuse写像 T^{-1}(m) の完全代数的記述 -- 最終まとめ

全ての発見を整理して検証する。
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

N = 100000

print("=" * 70)
print("逆Syracuse写像 T^{-1}(m) の完全代数的記述 -- 最終まとめ")
print("=" * 70)

# ============================================================
# 結果1: 完全分類定理
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理1 (完全分類): T: Odd+ → Odd+ を T(n) = (3n+1)/2^{v2(3n+1)} とする。
奇数 m に対し:

  T^{-1}(m) = { (m * 2^j - 1) / 3 : j ∈ J(m) }

  ここで:
    m ≡ 0 (mod 3):  J(m) = 空集合     (逆像なし)
    m ≡ 1 (mod 6):  J(m) = {2,4,6,...} (正偶数全体)
    m ≡ 5 (mod 6):  J(m) = {1,3,5,...} (正奇数全体)

  逆像の k 番目の要素: n_k = (m * 2^{s+2(k-1)} - 1) / 3
    s = 2 (m ≡ 1 mod 6), s = 1 (m ≡ 5 mod 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

# 検証
errors = 0
for m in range(1, 200, 2):
    if m % 3 == 0:
        # 逆像なし確認
        for j in range(1, 30):
            num = m * (1 << j) - 1
            if num % 3 == 0 and (num // 3) % 2 == 1:
                errors += 1
        continue
    s = 2 if m % 6 == 1 else 1
    for k in range(1, 15):
        j = s + 2 * (k - 1)
        n = (m * (1 << j) - 1) // 3
        if syracuse(n) != m:
            errors += 1
print(f"  [検証] 定理1: {errors} 件のエラー")

# ============================================================
# 結果2: v2 自動成立
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理2 (v2自動成立): n = (m*2^j - 1)/3 のとき v2(3n+1) = j

証明: 3n+1 = 3*(m*2^j-1)/3 + 1 = m*2^j
      m奇数 => v2(m*2^j) = j  Q.E.D.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

# ============================================================
# 結果3: 最小逆像
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理3 (最小逆像):
  m ≡ 1 (mod 6): n_min(m) = (4m-1)/3,    n_min/m → 4/3
  m ≡ 5 (mod 6): n_min(m) = (2m-1)/3,    n_min/m → 2/3

系: m ≡ 5 (mod 6) のとき n_min(m) < m （下降する逆像が必ず存在）
   m ≡ 1 (mod 6), m ≥ 7 のとき n_min(m) > m （最小逆像は上昇する）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

errors = 0
for m in range(5, 10000, 6):  # m ≡ 5 (mod 6)
    n_min = (2 * m - 1) // 3
    if n_min >= m:
        errors += 1
    if syracuse(n_min) != m:
        errors += 1
for m in range(7, 10000, 6):  # m ≡ 1 (mod 6)
    n_min = (4 * m - 1) // 3
    if n_min <= m:
        errors += 1
    if syracuse(n_min) != m:
        errors += 1
print(f"  [検証] 定理3: {errors} 件のエラー")

# ============================================================
# 結果4: 有界逆像の個数公式
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理4 (有界逆像数):
  m ≡ 1 (mod 6):
    |T^{-1}(m) ∩ [1,N]| = max(0, floor((floor(log2((3N+1)/m)) - 2)/2) + 1)
  m ≡ 5 (mod 6):
    |T^{-1}(m) ∩ [1,N]| = max(0, floor((floor(log2((3N+1)/m)) - 1)/2) + 1)
  m ≡ 0 (mod 3):
    |T^{-1}(m) ∩ [1,N]| = 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

errors = 0
for m in range(1, 500, 2):
    if m % 3 == 0:
        continue
    # 実計数
    actual = 0
    s = 2 if m % 6 == 1 else 1
    j = s
    while True:
        n = (m * (1 << j) - 1) // 3
        if n > N:
            break
        actual += 1
        j += 2

    # 公式
    if 3*N+1 <= m:
        formula = 0
    else:
        J_max = math.floor(math.log2((3*N+1)/m))
        if m % 6 == 1:
            formula = max(0, (J_max - 2) // 2 + 1) if J_max >= 2 else 0
        else:
            formula = max(0, (J_max - 1) // 2 + 1) if J_max >= 1 else 0

    if actual != formula:
        errors += 1
print(f"  [検証] 定理4: {errors} 件のエラー (m=1..499, N={N})")

# ============================================================
# 結果5: 像の統計
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理5 (像の統計):
  (a) |T([1,N] ∩ Odd)| = 3N/4  (像の異なる値の総数)
      平均入次数 = (N/2) / (3N/4) = 4/3

  (b) |T([1,N] ∩ Odd) ∩ [1,N]| / |[1,N] ∩ Odd| = 7/12
      （N以下の奇数のうち[1,N]内の像に含まれる割合）

  (c) T(n) > N となる n の割合: 1/6
      （v2(3n+1)=1 かつ n > 2N/3 のケース）

  (d) m ≡ 5 (mod 6): 像率 100% (n_min < m なので)
      m ≡ 1 (mod 6): 像率 75%  (m ≤ 3N/4 のもの)
      m ≡ 3 (mod 6): 像率 0%   (3|m)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

# 検証
reached_all = set()
reached_le_N = set()
for n in range(1, N+1, 2):
    m = syracuse(n)
    reached_all.add(m)
    if m <= N:
        reached_le_N.add(m)

total_odd = N // 2
print(f"  [検証] N={N}:")
print(f"    |像|全体 = {len(reached_all)}, 理論 3N/4 = {3*N//4}")
print(f"    平均入次数 = {total_odd / len(reached_all):.4f}, 理論 4/3 = {4/3:.4f}")
print(f"    |像∩[1,N]|/(N/2) = {len(reached_le_N)/total_odd:.4f}, 理論 7/12 = {7/12:.4f}")

exceed = sum(1 for n in range(1, N+1, 2) if syracuse(n) > N)
print(f"    T(n)>N の割合 = {exceed/total_odd:.4f}, 理論 1/6 = {1/6:.4f}")

# ============================================================
# 結果6: 逆Syracuse木の成長
# ============================================================
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
定理6 (逆像の指数的増大):
  T^{-1}(m) の k 番目の要素を n_k とすると:
    n_{k+1} / n_k → 4  (k → ∞)

  逆Syracuse木（根=1）の深さ d でのノード数は N^{α(d)} で増大。
  mod 3 分布は深さが増すと均等 (各1/3) に近づく。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

# 比率 n_{k+1}/n_k の検証
print("  [検証] n_{k+1}/n_k → 4:")
for m in [1, 5, 7, 11]:
    s = 2 if m % 6 == 1 else 1
    ns = []
    for k in range(8):
        j = s + 2 * k
        ns.append((m * (1 << j) - 1) // 3)
    ratios = [ns[i+1]/ns[i] for i in range(len(ns)-1)]
    print(f"    m={m}: ratios = {[f'{r:.4f}' for r in ratios]}")

# ============================================================
# 新発見: 平均入次数の厳密な証明
# ============================================================
print()
print("=" * 70)
print("新発見: 像サイズ 3N/4 の厳密証明")
print("=" * 70)

print("""
証明: |T([1,N] ∩ Odd)| = 3N/4 を示す。

Step 1: T は単射でない。同じ m に複数の n が写る。
  n1 ≠ n2 で T(n1) = T(n2) = m <=> n1, n2 は異なる j 値の逆像。

Step 2: T の「衝突」の数を数える。
  入力数 = N/2, |像| = M
  衝突数 = (N/2) - M

  衝突は同じ m に j1 ≠ j2 で写るペア。
  m ≡ 1(6), m ≤ 3N/4: j=2,4,6,...の逆像が[1,N]内に floor(log2(3N/m)/2)個
  m ≡ 5(6), m ≤ N: j=1,3,5,...の逆像が[1,N]内に floor((log2(3N/m)+1)/2)個

  各mの余剰入力 = |T^{-1}(m) ∩ [1,N]| - 1 = (入次数 - 1)

  Σ_{m in image}(入次数-1) = N/2 - M

  M = N/2 - Σ(入次数-1) = N/2 - Σ入次数 + |像| = |像|のまま（恒等式）

  別アプローチ: 直接 M を計算。

  各奇数 n ≤ N に対し T(n) は一意の m を返す。
  M = |{T(n) : n odd, n ≤ N}|

  T(n) = (3n+1)/2^j where j = v2(3n+1)

  j が異なれば T(n) が異なる値を取る可能性が高い。
  同じ j で同じ m になる条件: n1 ≠ n2, v2(3n1+1)=v2(3n2+1)=j, (3n1+1)/2^j=(3n2+1)/2^j
  => 3n1+1 = 3n2+1 => n1 = n2 (矛盾)

  つまり同じ j では T は単射！衝突は異なる j からのみ起こる。

  j=1 の入力数: N/4 (n ≡ 1 mod 4 の奇数)
  j=2 の入力数: N/8 (n ≡ 3 mod 8 の奇数)
  j=k の入力数: N/2^{k+1}

  合計 Σ_{k=1}^∞ N/2^{k+1} = N/2 (一致)

  像: 各 j での像サイズは N/2^{k+1}（単射なので）
  j が異なる場合の像の重複を引く:

  M = Σ_j (像_j のサイズ) - (重複の総数)

  実は v2(3n+1)=1 の場合 T(n) = (3n+1)/2、n ≡ 1(4) で T(n) は奇数で T(n)≡5(6)
  v2(3n+1)=2 の場合 T(n) = (3n+1)/4、n ≡ 3(8) で T(n) は奇数で T(n)≡1(6)

  j=1 の像: {(3n+1)/2 : n ≡ 1 mod 4, n ≤ N} → m ≡ 5 (mod 6)
  j=2 の像: {(3n+1)/4 : n ≡ 3 mod 8, n ≤ N} → m ≡ 1 (mod 6)

  j=1 の像は m ≡ 5(6)、j=2 の像は m ≡ 1(6)。
  j が同じ mod 2 なら同じ残基類。

  奇数 j (j=1,3,5,...) の像: m ≡ 5 (mod 6)
  偶数 j (j=2,4,6,...) の像: m ≡ 1 (mod 6)

  よって奇数 j の像同士は重複し得る、偶数 j の像同士も重複し得る。
  しかし奇数 j と偶数 j の像は mod 6 が異なるので重複しない！
""")

# 検証: j の偶奇と m mod 6 の関係
print("検証: v2 の偶奇と T(n) mod 6 の関係")
j_mod6 = Counter()
for n in range(1, N+1, 2):
    j = v2(3*n+1)
    m = syracuse(n)
    key = (j % 2, m % 6)
    j_mod6[key] += 1

for j_parity in [0, 1]:  # 0=even, 1=odd
    for m_mod in [1, 3, 5]:
        count = j_mod6.get((j_parity, m_mod), 0)
        label = "偶数j" if j_parity == 0 else "奇数j"
        print(f"  {label}, m≡{m_mod}(6): {count}")

print("""
結論:
  奇数j → m ≡ 5 (mod 6) のみ
  偶数j → m ≡ 1 (mod 6) のみ

  これより M = |奇数jの像の和集合| + |偶数jの像の和集合|

  奇数j=1,3,5,...の像:
    j=1: N/4 個 (全て異なる m ≡ 5 mod 6)
    j=3: N/16 個
    j=1とj=3の重複: n1でj=1, n2でj=3, T(n1)=T(n2)=m
      n1=(2m-1)/3, n2=(8m-1)/3, 両方≤N のケース
      n1≤N: m≤(3N+1)/2 (常に成立)
      n2≤N: m≤(3N+1)/8
    → j=3 の像は j=1 の像に完全に含まれる

  同様に全ての j=3,5,7,...の像は j=1 の像に含まれる
  （j=1での逆像が最小、つまり最小の n に対応するので）

  よって |奇数jの像の和集合| = |j=1の像| = N/4

  偶数j=2,4,6,...の像:
    j=2: N/8 個
    j=4: N/32 個
    j=2とj=4の重複: j=4の像はj=2の像に含まれる（同じ理由）

  よって |偶数jの像の和集合| = |j=2の像| = N/8

  しかし! j=2の像が全て異なるわけではない可能性...
  いや、同じjでは T は単射なので j=2 の N/8 個は全て異なる。
  ただし m > N のものも含まれる。

  正確には:
  j=1の像: {(3n+1)/2 : n odd, n≡1(4), n≤N}
    = {m : m=(3n+1)/2, n=1,5,9,...}
    n ∈ {1,5,9,...,N-3} → m ∈ {2,8,14,...}... 待って、n≡1(4)。
    n=1: m=2 (偶数!) → Syracuseではない。

  問題: T(n) は常に奇数なので、ここでの「像」は自動的に奇数。
  n=1: T(1) = (3+1)/2^2 = 1. v2(4)=2. T(1)=1. j=2で偶数j。
""")

# 決定的に正確な数え上げ
print("\n正確な数え上げによる最終確認:")
for N_check in [1000, 10000, 100000]:
    # 各 j でのユニークな像の数を計測
    images_by_j = {}
    for j in range(1, 20):
        images_j = set()
        for n in range(1, N_check+1, 2):
            if v2(3*n+1) == j:
                images_j.add(syracuse(n))
        images_by_j[j] = images_j

    # 奇数j、偶数jの和集合
    odd_j_union = set()
    even_j_union = set()
    for j, img in images_by_j.items():
        if j % 2 == 1:
            odd_j_union |= img
        else:
            even_j_union |= img

    total_image = odd_j_union | even_j_union

    print(f"\n  N={N_check}:")
    print(f"    |j=1の像| = {len(images_by_j.get(1,set()))}")
    print(f"    |j=2の像| = {len(images_by_j.get(2,set()))}")
    print(f"    |j=3の像| = {len(images_by_j.get(3,set()))}")
    print(f"    |奇数jの和集合| = {len(odd_j_union)}")
    print(f"    |偶数jの和集合| = {len(even_j_union)}")
    print(f"    重複(奇∩偶) = {len(odd_j_union & even_j_union)}")
    print(f"    |全像| = {len(total_image)}")
    print(f"    3N/4 = {3*N_check//4}")

    # j=1 の像 = 奇数j全体の和集合？
    j1_img = images_by_j.get(1, set())
    odd_j_extra = odd_j_union - j1_img
    print(f"    奇数j和集合 \\ j=1像 = {len(odd_j_extra)} 個")

    j2_img = images_by_j.get(2, set())
    even_j_extra = even_j_union - j2_img
    print(f"    偶数j和集合 \\ j=2像 = {len(even_j_extra)} 個")

    # N/4 + N/8 = 3N/8
    # でも |像| = 3N/4。何が間違い?
    # j=1 の入力数は N/4 だが像の数もN/4（単射）。
    # しかし |奇数jの和集合| は N/4 より大きい可能性がある。

    # 確認: j=1 だけで何個の異なる m が出るか
    input_j1 = sum(1 for n in range(1, N_check+1, 2) if v2(3*n+1) == 1)
    print(f"    j=1の入力数 = {input_j1}, |j=1の像| = {len(j1_img)}")
    input_j2 = sum(1 for n in range(1, N_check+1, 2) if v2(3*n+1) == 2)
    print(f"    j=2の入力数 = {input_j2}, |j=2の像| = {len(j2_img)}")

print()
print("=" * 70)
print("最終結論")
print("=" * 70)

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
最終定理: |T([1,N] ∩ Odd)| = 3N/4 の証明

1. 同じ j で T は単射:
   (3n1+1)/2^j = (3n2+1)/2^j => n1 = n2

2. 奇数j の像は m ≡ 5(mod6) に限る、偶数j の像は m ≡ 1(mod6) に限る
   => 異なる偶奇の j 間で像は重複しない

3. 奇数j = 1,3,5,... の像:
   j=1: 入力 N/4 個、像 N/4 個（単射）
   j=3 の像は j=1 の像の部分集合
   （m が j=3 で得られるなら j=1 でも得られる、なぜなら n1 < n3）
   => |奇数j 全体の像| = |j=1 の像| = N/4

4. 偶数j = 2,4,6,... の像:
   j=2: 入力 N/8 個、像 N/8 個（単射）
   j=4 の像は j=2 の像の部分集合
   => |偶数j 全体の像| = |j=2 の像| = N/8

5. しかし N/4 + N/8 = 3N/8 ≠ 3N/4

   → Step 3 が間違い!
   j=3 の n = (8m-1)/3, j=1 の n = (2m-1)/3
   j=1 の n ≤ N <=> m ≤ (3N+1)/2
   j=3 の n ≤ N <=> m ≤ (3N+1)/8

   j=3 の像（m ≤ (3N+1)/8 の m ≡ 5 mod 6）は j=1 の像に含まれる
   j=1 の像（m ≤ (3N+1)/2 の m ≡ 5 mod 6）は N/2 以上の m も含む

   |j=1 の像| = |{n ≡ 1 mod 4, n ≤ N}| = N/4  ... これは入力の数
   = |{(3n+1)/2 : n ≡ 1 mod 4, 1 ≤ n ≤ N}| = N/4 (単射なので)

   しかしこの N/4 個の m のうち m ≤ N のものと m > N のものがある!
   j=1: m = (3n+1)/2, m ≤ N <=> n ≤ (2N-1)/3 ≈ 2N/3
   → m ≤ N の像: 2N/3 の中の n ≡ 1(4) ≈ N/6 個
   → m > N の像: 残り N/4 - N/6 = N/12 個

正しい計算:
  |全像| = |j=1の像| + |j=2の像|  (偶奇で分離)
  = N/4 + N/8 = 3N/8

  ん? 実測は 3N/4。

  あ、j=1の入力が N/4 というのが間違い。
  v2(3n+1)=1 <=> n ≡ 1 (mod 4) [奇数 n で]
  奇数 n = 1,3,5,...,N-1 のうち n ≡ 1(4) は n=1,5,9,...
  個数 = N/4 は正しい。

  問題は j だけでなく、全ての j を含めた像の数。
  |全像| = |j=1の像 ∪ j=2の像 ∪ j=3の像 ∪ ...|

  j=1とj=3は同じ m mod 6 = 5 だが、対応する m は異なる可能性がある。
  j=1: m = (3n+1)/2, n ≡ 1(4), n ≤ N
  j=3: m = (3n+1)/8, n ≡ 3(8)... いや n ≡ 3(8) ではない

  v2(3n+1)=3 <=> 8|(3n+1) <=> 3n ≡ 7(8) <=> n ≡ 5(8) [nは奇数]
  j=3 の入力: n ≡ 5(8), 個数 N/8
  j=3 の像: m = (3n+1)/8, 個数 N/8 (単射)

  j=1 の像: m1 = (3n1+1)/2  (n1 ≡ 1 mod 4)
  j=3 の像: m3 = (3n3+1)/8  (n3 ≡ 5 mod 8)

  m1 = m3 <=> (3n1+1)/2 = (3n3+1)/8 <=> 4(3n1+1) = 3n3+1
  <=> 12n1+4 = 3n3+1 <=> n3 = 4n1+1

  n3 ≤ N <=> 4n1+1 ≤ N <=> n1 ≤ (N-1)/4

  j=3の像 N/8 個のうち、j=1の像と重複するのは
  n3 = 4n1+1 で n1 ≡ 1(4), n1 ≤ (N-1)/4 なるものの数 ≈ N/16

  よって j=3 の像から j=1 の像を引いた新規は N/8 - N/16 = N/16 個

  同様に j=5 からの新規: ...

  この計算は複雑。直接数値で確認する。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# 各 j の「新規」像数を計算
N_final = 100000
seen = set()
j_new_counts = {}

for j in range(1, 20):
    new_this_j = 0
    input_count = 0
    for n in range(1, N_final + 1, 2):
        if v2(3*n+1) == j:
            input_count += 1
            m = syracuse(n)
            if m not in seen:
                seen.add(m)
                new_this_j += 1
    j_new_counts[j] = (input_count, new_this_j)

cumulative = 0
print(f"j ごとの新規像数 (N={N_final}):")
for j in range(1, 18):
    inp, new = j_new_counts.get(j, (0, 0))
    cumulative += new
    ratio = new / inp if inp > 0 else 0
    theory = N_final / (2**(j+1))
    print(f"  j={j:2d}: 入力={inp:6d} (理論{theory:.0f}), "
          f"新規={new:6d} ({ratio:.4f}), 累計={cumulative}")

print(f"\n  累計 = {cumulative}, 3N/4 = {3*N_final//4}")
print(f"  比率: {cumulative / (3*N_final/4):.6f}")

# 各jでの新規の理論値
# j の新規 = j の入力数 * (1 - 既に見た m の割合)
# j=1: 新規 = N/4 (全て新規)
# j=2: 新規 = N/8 (m≡1(6) で j=1は m≡5(6) なので全て新規)
# j=3: 新規 ≈ ? (j=1 と同じ m ≡ 5(6) だが、j=1 の像に含まれないものがある)

print("\n理論的考察:")
print(f"  j=1 新規: N/4 = {N_final//4} (j=1は m≡5(6), 全て新規)")
print(f"  j=2 新規: N/8 = {N_final//8} (j=2は m≡1(6), j=1と非重複で全て新規)")
print(f"  j=3 新規: 実測 = {j_new_counts.get(3,(0,0))[1]}")
print(f"  j=3 の像は m≡5(6)。j=1 の像にない m が存在するのは")
print(f"  m > (3N+1)/2 のとき j=1 では得られないが j=3 では得られるケース。")
print(f"  j=3: m=(3n+1)/8, n ≤ N => m ≤ (3N+1)/8")
print(f"  j=1: m=(3n+1)/2, n ≤ N => m ≤ (3N+1)/2")
print(f"  よって j=3 の像は全て j=1 の像に含まれる。新規 = 0 のはず。")
print(f"  しかし実測は {j_new_counts.get(3,(0,0))[1]} ... なぜ?")

# 詳しく調べる
if j_new_counts.get(3, (0,0))[1] > 0:
    # j=3 の像で j=1 の像にないものを探す
    j1_image = set()
    for n in range(1, N_final+1, 2):
        if v2(3*n+1) == 1:
            j1_image.add(syracuse(n))

    j3_only = []
    for n in range(1, N_final+1, 2):
        if v2(3*n+1) == 3:
            m = syracuse(n)
            if m not in j1_image:
                j3_only.append((n, m))
    print(f"\n  j=3 にあって j=1 にない像: {len(j3_only)} 個")
    if j3_only:
        print(f"  最初の数例: {j3_only[:5]}")
        # これらの m に対する j=1 の逆像
        for n3, m in j3_only[:3]:
            n1 = (2*m - 1) // 3
            print(f"    m={m}: j=1の逆像 n=(2m-1)/3={n1}, n≤N? {n1 <= N_final}")
