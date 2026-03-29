#!/usr/bin/env python3
"""
T^{-1}(m) ∩ [1,N] の全単射的構造の解明

核心的発見: N=6k のとき像のサイズは 正確に 3N/8。
これは偶然ではない。以下を証明する:

  T: {1,3,...,N-1} → OddPos は全射でも単射でもないが、

  (1) v2(3n+1) の分布は正確に P(j) = 1/2^j
  (2) m ≡ 5(mod6) かつ m ≤ 3N/2 の全ての m は像に含まれる
  (3) m ≡ 1(mod6) かつ m ≤ 3N/4 の全ての m は像に含まれる
  (4) 他の m は像に含まれない

  |image| = (3N/2)/6 + (3N/4)/6 = N/4 + N/8 = 3N/8

なぜこれが正確なのかの本質的理由:
  n ≡ 1(mod4) → v2(3n+1) = 1 → T(n) = (3n+1)/2 ≡ 2(mod3)
                                      → T(n) ≡ 5(mod6) (T(n)奇数だから)
  n ≡ 3(mod4) → v2(3n+1) ≥ 2 → T(n) は j に依存

  n ≡ 1(mod4) のとき T(n) = (3n+1)/2
    n = 4k+1 → T(n) = (12k+4)/2 = 6k+2 ... 偶数!
    これは collatzStep の話で、Syracuse は v2 を全て除去する

  再考: T(n) = (3n+1)/2^{v2(3n+1)}
    n奇数 → 3n+1偶数 → v2(3n+1) ≥ 1

    v2(3n+1) = j は n mod 2^{j+1} で決まる
    正確には: 3n+1 ≡ 0 (mod 2^j) かつ 3n+1 ≢ 0 (mod 2^{j+1})

本分析: 各 j について T^{-1}_j(m) = {n : T(n)=m, v2(3n+1)=j} の構造を解明
"""

import math
from collections import Counter, defaultdict

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
# Part 1: v2(3n+1) = j の正確な条件
# ============================================================

print("=" * 70)
print("Part 1: v2(3n+1) = j の正確な条件 (mod 2^{j+1})")
print("=" * 70)

for j in range(1, 8):
    mod_val = 2**(j+1)
    valid_residues = []
    for r in range(1, mod_val, 2):  # 奇数 r のみ
        val = 3*r + 1
        if v2(val) == j:
            valid_residues.append(r)

    count = len(valid_residues)
    total_odd = mod_val // 2
    proportion = count / total_odd

    print(f"  j={j}: n ≡ {valid_residues[:8]}{'...' if len(valid_residues)>8 else ''} "
          f"(mod {mod_val})")
    print(f"       {count}/{total_odd} 個の奇数剰余類 (比率 = {proportion:.4f} = 1/{int(1/proportion) if proportion > 0 else 'inf'})")

print()

# ============================================================
# Part 2: T(n) = m かつ v2(3n+1) = j のとき n ↔ m の対応
# ============================================================

print("=" * 70)
print("Part 2: 固定 j に対する T_j^{-1}(m) の構造")
print("=" * 70)

print("""
T(n) = m, v2(3n+1) = j のとき:
  3n+1 = m * 2^j
  n = (m * 2^j - 1) / 3

  条件: (1) 3 | (m*2^j - 1)
        (2) n 奇数
        (3) n ≥ 1

  (1) m*2^j ≡ 1 (mod 3)
      2^j mod 3: j偶数 → 1, j奇数 → 2
      j偶数: m ≡ 1 (mod 3) → OK,  m ≡ 2 (mod 3) → NG
      j奇数: m ≡ 2 (mod 3) → OK,  m ≡ 1 (mod 3) → NG

  (2) n = (m*2^j - 1)/3 の奇偶性
      m*2^j - 1 = 3n → n奇数 ⟺ 3n ≡ 3 (mod 6) ⟺ m*2^j - 1 ≡ 3 (mod 6)
                     ⟺ m*2^j ≡ 4 (mod 6)
""")

# 各 j について m mod 6 の条件を直接計算
for j in range(1, 9):
    print(f"  j={j}:")
    valid_m_mod6 = []
    for m_mod6 in [1, 3, 5]:  # m は奇数
        numerator = m_mod6 * (2**j) - 1
        if numerator % 3 == 0:
            n_mod2 = (numerator // 3) % 2
            if n_mod2 == 1:
                valid_m_mod6.append(m_mod6)
                print(f"    m ≡ {m_mod6} (mod 6): m*2^{j} ≡ {m_mod6 * (2**j) % 6} (mod 6), "
                      f"n mod 2 = {n_mod2} → OK")
            else:
                print(f"    m ≡ {m_mod6} (mod 6): m*2^{j} ≡ {m_mod6 * (2**j) % 6} (mod 6), "
                      f"n mod 2 = {n_mod2} → NG (偶数)")
        else:
            print(f"    m ≡ {m_mod6} (mod 6): 3 ∤ (m*2^{j}-1) → NG")

    print(f"    有効: m ≡ {valid_m_mod6} (mod 6)")
    print()

# ============================================================
# Part 3: T は「ほぼ」全単射であることの確認
# ============================================================

print("=" * 70)
print("Part 3: (n, j) ↔ m の対応の全単射性")
print("=" * 70)

print("""
T(n) = m, v2(3n+1) = j のとき n = (m*2^j - 1)/3

逆に: m と j が与えられたとき n = (m*2^j - 1)/3 が一意に決まる

つまり (m, j) → n は単射！

よって T^{-1}_j(m) は各 (m,j) に対して高々1個の n を持つ。

重要: T は全体として単射ではない（異なる n が同じ m を異なる j で与える）
      しかし j を指定すれば単射。

入力の分解:
  S_N = {1,3,...,N-1} を j = v2(3n+1) で分類:
    S_N^{(j)} = {n ∈ S_N : v2(3n+1) = j}
    |S_N^{(j)}| = N/(2^{j+1})  (n mod 2^{j+1} の条件から正確に)

  各 S_N^{(j)} に対して T|_{S_N^{(j)}} は単射
  像: T(S_N^{(j)}) = {m : n = (m*2^j-1)/3 ∈ S_N^{(j)}}
""")

# 検証: T が j を固定したとき単射であることの確認
for N in [10000]:
    for j_fixed in range(1, 8):
        n_set = [n for n in range(1, N+1, 2) if v2(3*n+1) == j_fixed]
        m_set = [syracuse(n) for n in n_set]

        is_injective = len(m_set) == len(set(m_set))
        print(f"  j={j_fixed}: |S_N^(j)| = {len(n_set)}, |T(S_N^(j))| = {len(set(m_set))}, "
              f"injective = {is_injective}")

print()

# ============================================================
# Part 4: 入次数分布の厳密な理論
# ============================================================

print("=" * 70)
print("Part 4: 入次数分布の完全な理論")
print("=" * 70)

print("""
定理 (入次数分布):
  m を正の奇数で 3 ∤ m とする。
  S_N = {1,3,...,N-1} に対し、

  indeg(m) = |{n ∈ S_N : T(n) = m}|

  m ≡ 5 (mod 6): 有効な j は 1,3,5,7,...
    j=1: n=(2m-1)/3 ≤ N ⟺ m ≤ (3N+1)/2
    j=3: n=(8m-1)/3 ≤ N ⟺ m ≤ (3N+1)/8
    j=5: n=(32m-1)/3 ≤ N ⟺ m ≤ (3N+1)/32
    ...
    j=2k-1: m ≤ (3N+1)/2^{2k-1}

  indeg(m) = |{k ≥ 1 : m ≤ (3N+1)/2^{2k-1}}|
           = |{k ≥ 1 : 2k-1 ≤ log_2((3N+1)/m)}|

  m ≡ 1 (mod 6): 有効な j は 2,4,6,8,...
    j=2: n=(4m-1)/3 ≤ N ⟺ m ≤ (3N+1)/4
    j=4: n=(16m-1)/3 ≤ N ⟺ m ≤ (3N+1)/16
    j=6: n=(64m-1)/3 ≤ N ⟺ m ≤ (3N+1)/64
    ...
    j=2k: m ≤ (3N+1)/2^{2k}

  indeg(m) = |{k ≥ 1 : m ≤ (3N+1)/2^{2k}}|

入次数 d の m の数:
  m ≡ 5 (mod 6):
    indeg = d ⟺ m ≤ (3N+1)/2^{2d-1} かつ m > (3N+1)/2^{2d+1}
    |{such m}| ≈ (3N)/(6 * 2^{2d-1}) - (3N)/(6 * 2^{2d+1})
              = (3N/6) * (1/2^{2d-1} - 1/2^{2d+1})
              = (N/2) * (1/2^{2d-1}) * (1 - 1/4)
              = (N/2) * (3/4) / 2^{2d-1}
              = 3N / (8 * 2^{2d-1})
              = 3N / (4 * 2^{2d})

  d=1: 3N/(4*4) = 3N/16 ≈ ...

  実測と比較:
""")

N = 100000
indeg = Counter()
for n in range(1, N + 1, 2):
    m = syracuse(n)
    indeg[m] += 1

# mod 6 別の入次数分布
for m_mod6 in [1, 5]:
    print(f"  m ≡ {m_mod6} (mod 6):")
    deg_counts = Counter()
    for m, d in indeg.items():
        if m % 6 == m_mod6:
            deg_counts[d] += 1

    total_in_class = sum(deg_counts.values())
    for d in sorted(deg_counts.keys()):
        count = deg_counts[d]
        # 理論値
        if m_mod6 == 5:
            # m ≡ 5(6): j_start=1, period=2
            # indeg=d ⟺ (3N+1)/2^{2d+1} < m ≤ (3N+1)/2^{2d-1}
            upper = (3*N+1) // (2**(2*d-1))
            lower = (3*N+1) // (2**(2*d+1))
            theory = len(range(m_mod6, upper+1, 6)) - len(range(m_mod6, lower+1, 6))
        else:
            # m ≡ 1(6): j_start=2, period=2
            upper = (3*N+1) // (2**(2*d))
            lower = (3*N+1) // (2**(2*d+2))
            theory = len(range(m_mod6, upper+1, 6)) - len(range(m_mod6, lower+1, 6))

        print(f"    d={d}: actual={count}, theory={theory}, "
              f"match={'YES' if count==theory else 'NO'}")

print()

# ============================================================
# Part 5: 入次数の比率 3/4 の本質的理由
# ============================================================

print("=" * 70)
print("Part 5: |image|/|input| = 3/4 の本質的理由")
print("=" * 70)

print("""
証明:
  入力: S_N = {n odd : n ≤ N}, |S_N| = N/2

  像: T(S_N) の要素数 M を計算する。

  T は (m,j) → n = (m*2^j - 1)/3 により逆転できる。
  ここで T|_{j固定} は単射。

  入力 n ∈ S_N は唯一の (m, j) に対応: m = T(n), j = v2(3n+1)

  逆に、像の各 m に対して、到達する j の値は {j : (m*2^j-1)/3 ≤ N} の中で
  さらに mod 条件を満たすもの。

  ★核心: 各 n は唯一の m を定め、同じ m を異なる j で到達する n たちが
  入次数 > 1 を作る。

  v2(3n+1) の分布: 正確に P(j=k) = 1/2^k (k≥1)
    証明: n が [1,N] の一様ランダムな奇数のとき、3n+1 mod 2^{k+1} は
          {0, 4, 8, ..., 2^{k+1}-4, 2^{k+1}-2, 2^{k+1}} のいずれか
          v2(3n+1) ≥ k ⟺ 2^k | 3n+1 ⟺ n ≡ (2^k - 1)/3 (mod 2^k/gcd...)
          実際には n mod 2^k の一様性から P(v2≥k) = 1/2^{k-1} (k≥1)
          よって P(v2=k) = 1/2^{k-1} - 1/2^k = 1/2^k ✓

  平均入次数 = Σ_n 1 / Σ_{m in image} 1
             = (N/2) / M

  M = |image(T)|

  各 m に対して: m が像に含まれる ⟺ 最小の逆像 n_min(m) ≤ N
    m ≡ 5(6): n_min = (2m-1)/3, n_min ≤ N ⟺ m ≤ (3N+1)/2
    m ≡ 1(6): n_min = (4m-1)/3, n_min ≤ N ⟺ m ≤ (3N+1)/4

  M = |{m ≡ 5(6) : 5 ≤ m ≤ (3N+1)/2}| + |{m ≡ 1(6) : 1 ≤ m ≤ (3N+1)/4}|

  6 | N のとき（簡潔化のため）:
    |{m ≡ 5(6) : m ≤ 3N/2}| = 3N/2 / 6 = N/4
    |{m ≡ 1(6) : m ≤ 3N/4}| = 3N/4 / 6 = N/8
    M = N/4 + N/8 = 3N/8

  avg_indeg = (N/2) / (3N/8) = (N/2) * (8/3N) = 4/3  ■

注意: この証明で使用したのは:
  (i)   逆像公式 n = (m*2^j - 1)/3
  (ii)  mod 6 分類 (m≡1(6): start=2, m≡5(6): start=1)
  (iii) 各 m に対する最小逆像の計算
  (iv)  mod 6 の剰余類の密度 = 1/6

  形式化には (i)-(iv) の全てが必要。
  (i) は定理B2 (ギャップ比=4) の基盤
  (ii) は mod 算術
  (iii) は (i)+(ii) の帰結
  (iv) は自然数の基本的性質
""")

# ============================================================
# Part 6: 入次数分布 P(indeg=d) の完全記述
# ============================================================

print("=" * 70)
print("Part 6: 入次数分布 P(indeg=d) の完全理論")
print("=" * 70)

print("""
定理: 像に含まれる m のうち indeg(m) = d であるものの割合は:
  P(d) = 3/(4^d) * (1 - 1/4) = 3^2/(4^{d+1})   ... ではなく:

  m ≡ 5(6): P(d) = (3/4)*(1/4)^{d-1}  (d=1,2,3,...)
             indeg=d ⟺ (3N+1)/2^{2d+1} < m ≤ (3N+1)/2^{2d-1}
             count ≈ (N/4)*(1-1/4)/4^{d-1} = (3N/16)/4^{d-1}

  m ≡ 1(6): P(d) = (3/4)*(1/4)^{d-1}  (同じ分布!)
             indeg=d ⟺ (3N+1)/2^{2(d+1)} < m ≤ (3N+1)/2^{2d}
             count ≈ (N/8)*(1-1/4)/4^{d-1} = (3N/32)/4^{d-1}

  全体: count(d) = (3N/16 + 3N/32) / 4^{d-1}
                 = (9N/32) / 4^{d-1}

  検証: Σ count(d) = (9N/32) * Σ 1/4^{d-1} = (9N/32) * 4/3 = 3N/8 = M ✓
""")

# 数値検証
N = 100000
indeg = Counter()
for n in range(1, N + 1, 2):
    m = syracuse(n)
    indeg[m] += 1

deg_dist = Counter(indeg.values())
M = len(indeg)

print(f"N={N}, M={M}, N/2={N//2}, M/(N/2)={M/(N/2):.6f}")
print()

for d in range(1, 10):
    actual = deg_dist.get(d, 0)
    # 理論: count(d) = (9N/32) / 4^{d-1}
    theory = 9 * N / 32 / (4 ** (d - 1))
    print(f"  d={d}: actual={actual:>6d}, theory={theory:.1f}, "
          f"ratio={actual/theory if theory > 0 else 'N/A':.4f}")

print()
print("幾何分布の確認: actual[d+1] / actual[d]")
for d in range(1, 7):
    if deg_dist.get(d, 0) > 0:
        ratio = deg_dist.get(d+1, 0) / deg_dist[d]
        print(f"  d={d}→{d+1}: {ratio:.4f} (理論 = 1/4 = 0.25)")
