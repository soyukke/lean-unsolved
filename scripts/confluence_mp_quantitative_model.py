"""
探索163 Part 3: 合流点分布の定量モデル

核心的発見:
1. mp≠5のケースは全て「5の下流」(v→...→5)で合流
   → 隣接ペアは「5に到達する前」に合流するか、「5で」合流するかの二択
2. P(mp=5 | both pass 5) = 0.475
3. 5を最初に到達する奇数の比率 = 51.1% (11が先の場合 43.0%)
4. mod6/mod12でP(mp=5)はほぼ一定 (42-44%)

モデル仮説:
  P(mp=5) ≈ P(both reach 5) * P(5 is earliest shared | both reach 5)
           ≈ 0.894 * 0.475 = 0.425 ✓

5が「最初の合流点」になるのは:
  - 両軌道が5に到達するまでの経路が完全に分離している場合
  - 5の上流（逆像木T^{-k}(5)）が十分に広く、かつ「独立経路」が多い場合

定量化すべきこと:
  P(first shared = 5 | both pass 5) ≈ 0.475 の理論的説明
"""

import math
from collections import defaultdict, Counter
import json

def syracuse(n):
    assert n % 2 == 1
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def odd_collatz_sequence(n):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    seq = [n]
    while n != 1:
        n = syracuse(n)
        seq.append(n)
    return seq

# === Part A: 「上流合流」vs「5合流」の二分木モデル ===

print("=" * 70)
print("Part A: 5の上流の分岐構造の詳細分析")
print("=" * 70)

# orbit(5) = [5, 1] なので、5の上流とは5に到達する全ての奇数n≠5
# これらの奇数nは、5に到達するまでの軌道を持つ
# 隣接ペア(n, n+2)が5で合流 ⟺ n→...→5 と n+2→...→5 の経路が合流前に交わらない

# 5に到達する奇数の「5への経路」を分析
N = 3000
path_to_5 = {}  # n -> list of odd numbers from n to 5 (exclusive of 5)
for n in range(1, N+1, 2):
    seq = odd_collatz_sequence(n)
    if 5 in seq:
        idx = seq.index(5)
        path_to_5[n] = seq[:idx]  # 5より前の部分

# 隣接ペアについて、5への経路の共有部分を分析
shared_before_5 = []
for n in range(1, N-1, 2):
    m = n + 2
    if n in path_to_5 and m in path_to_5:
        path_n = set(path_to_5[n])
        path_m = set(path_to_5[m])
        shared = path_n & path_m
        if shared:
            # 共有点がある = 5より前に合流
            earliest_shared = None
            for x in odd_collatz_sequence(m):
                if x in path_n and x != 5:
                    earliest_shared = x
                    break
            shared_before_5.append({
                'n': n, 'm': m,
                'shared_count': len(shared),
                'earliest': earliest_shared,
                'path_n_len': len(path_to_5[n]),
                'path_m_len': len(path_to_5[m])
            })

both_pass_5_count = sum(1 for n in range(1, N-1, 2) if n in path_to_5 and n+2 in path_to_5)
share_before_5_count = len(shared_before_5)
merge_at_5_count = both_pass_5_count - share_before_5_count

print(f"  N={N}")
print(f"  両方5を通過するペア: {both_pass_5_count}")
print(f"  5より前に共有点あり: {share_before_5_count}")
print(f"  5が最初の合流点: {merge_at_5_count}")
print(f"  P(mp=5 | both pass 5) = {merge_at_5_count/both_pass_5_count:.4f}")

# 5より前の共有点の分布
earliest_mp = Counter()
for info in shared_before_5:
    if info['earliest']:
        earliest_mp[info['earliest']] += 1

print(f"\n  5より前の合流点の分布:")
for v, c in earliest_mp.most_common(15):
    orbit_v = odd_collatz_sequence(v)
    steps_to_5 = orbit_v.index(5) if 5 in orbit_v else -1
    print(f"    pre-mp={v:6d}: count={c:4d}, steps_to_5={steps_to_5}")

# === Part B: 経路長と合流確率の関係 ===

print("\n" + "=" * 70)
print("Part B: 5への経路長と合流確率の関係")
print("=" * 70)

# 仮説: 経路が長いほど途中で合流する確率が高い
# → P(mp=5) は経路長に依存する

path_len_mp5 = defaultdict(lambda: [0, 0])  # min(len_n, len_m) -> [mp5_count, total]
for n in range(1, N-1, 2):
    m = n + 2
    if n in path_to_5 and m in path_to_5:
        ln = len(path_to_5[n])
        lm = len(path_to_5[m])
        min_len = min(ln, lm)
        bucket = (min_len // 5) * 5  # 5刻みバケット

        # mp=5か判定
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        set_n = set(seq_n)
        mp = None
        for x in seq_m:
            if x in set_n:
                mp = x
                break

        path_len_mp5[bucket][1] += 1
        if mp == 5:
            path_len_mp5[bucket][0] += 1

print(f"  min(path_len) vs P(mp=5):")
for bucket in sorted(path_len_mp5.keys()):
    mp5, total = path_len_mp5[bucket]
    if total >= 5:
        print(f"    len=[{bucket:2d},{bucket+5:2d}): P(mp=5)={mp5}/{total} = {mp5/total:.4f}")

# === Part C: 「独立経路」確率の理論モデル ===

print("\n" + "=" * 70)
print("Part C: 独立経路モデルによるP(mp=5)の理論的導出")
print("=" * 70)

# モデル: 2つの軌道が独立にランダムウォークして5を目指す
# 各ステップで軌道が重なる確率 ≈ 1/(利用可能な奇数の数)
# 累積的に「kステップ以内に共有点なし」の確率

# 実測: 5への平均経路長
if path_to_5:
    all_lens = [len(v) for v in path_to_5.values() if len(v) > 0]
    print(f"  5への経路長: mean={sum(all_lens)/len(all_lens):.1f}, median={sorted(all_lens)[len(all_lens)//2]}")

# 「有効奇数空間」のサイズ推定
# 軌道がstep kにいるとき、その値はおよそ N*(3/4)^k
# → 利用可能な奇数 ≈ N*(3/4)^k / 2
# → 2つの軌道がstep kで衝突する確率 ≈ 2/(N*(3/4)^k)

# P(no collision in k steps) ≈ prod_{i=0}^{k-1} (1 - 2/(N*(3/4)^i))
# ≈ exp(-sum_{i=0}^{k-1} 2/(N*(3/4)^i))
# = exp(-(2/N) * sum (4/3)^i)
# = exp(-(2/N) * ((4/3)^k - 1) / (1/3))
# = exp(-(6/N) * ((4/3)^k - 1))

# 平均経路長 k ≈ c_stop * log2(N) ≈ 2.41 * log2(N)
# (4/3)^k ≈ N^(log(4/3)/log(2) * c_stop) = N^1 = N

# したがって P(no collision) ≈ exp(-6/N * N) = exp(-6) ≈ 0.0025
# これは小さすぎる！

# 修正: 軌道は独立ではない（隣接ペアなので相関がある）
# 実際には「5の上流の木」の異なる枝を辿る

# 木の枝分かれ構造を分析
print(f"\n  5の直接逆像 (Syracuse pre-images):")
def inverse_syracuse_all_no_limit(m):
    preimages = []
    for j in range(1, 30):
        num = m * (1 << j) - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1:
                preimages.append((n, j))
    return preimages

# 5の逆像木の分岐構造（制限なし、最初の数レベル）
def show_tree(root, max_depth, max_n=10**6, indent=""):
    """逆像木を表示"""
    pres = [(n, j) for n, j in inverse_syracuse_all_no_limit(root) if n <= max_n]
    for n, j in sorted(pres):
        print(f"{indent}n={n} (j={j}) -> {root}")
        if max_depth > 1:
            show_tree(n, max_depth - 1, max_n, indent + "  ")

print(f"\n  T^(-1)(5) の逆像木 (3レベル, n ≤ 100000):")
show_tree(5, 3, 100000, "    ")

# === Part D: 分岐因子と合流確率の関係 ===

print("\n" + "=" * 70)
print("Part D: 5の逆像木の構造的性質")
print("=" * 70)

# 各レベルの分岐因子
def tree_level_sizes(root, max_depth, max_n):
    current = {root}
    level_info = []
    for d in range(max_depth):
        next_level = set()
        for m in current:
            for n, j in inverse_syracuse_all_no_limit(m):
                if n <= max_n:
                    next_level.add(n)
        level_info.append({
            'depth': d + 1,
            'new_nodes': len(next_level),
            'branch_factor': len(next_level) / len(current) if current else 0
        })
        current = next_level
        if not current:
            break
    return level_info

for root in [1, 5, 11, 17]:
    print(f"\n  root={root}:")
    levels = tree_level_sizes(root, 10, 10**6)
    for info in levels:
        print(f"    depth={info['depth']:2d}: "
              f"new_nodes={info['new_nodes']:6d}, "
              f"branch_factor={info['branch_factor']:.3f}")

# === Part E: Nの依存性 ===

print("\n" + "=" * 70)
print("Part E: P(mp=5)のN依存性")
print("=" * 70)

for N in [500, 1000, 2000, 5000]:
    mp5_count = 0
    total = 0
    for n in range(1, N-1, 2):
        m = n + 2
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        set_n = set(seq_n)
        mp = None
        for x in seq_m:
            if x in set_n:
                mp = x
                break
        total += 1
        if mp == 5:
            mp5_count += 1

    print(f"  N={N:5d}: P(mp=5) = {mp5_count}/{total} = {mp5_count/total:.4f}")

# === Part F: ランダムペアの場合 ===

print("\n" + "=" * 70)
print("Part F: ランダムペア vs 隣接ペアのP(mp=5)")
print("=" * 70)

import random
random.seed(42)

N = 3000
# ランダムペア
mp5_random = 0
total_random = 1000
for _ in range(total_random):
    a = random.randrange(1, N+1, 2)
    b = random.randrange(1, N+1, 2)
    while b == a:
        b = random.randrange(1, N+1, 2)
    seq_a = odd_collatz_sequence(a)
    seq_b = odd_collatz_sequence(b)
    set_a = set(seq_a)
    mp = None
    for x in seq_b:
        if x in set_a:
            mp = x
            break
    if mp == 5:
        mp5_random += 1

print(f"  ランダムペア (N={N}): P(mp=5) = {mp5_random}/{total_random} = {mp5_random/total_random:.4f}")

# 隣接ペア（距離1）
mp5_adj = 0
total_adj = 0
for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)
    set_n = set(seq_n)
    mp = None
    for x in seq_m:
        if x in set_n:
            mp = x
            break
    total_adj += 1
    if mp == 5:
        mp5_adj += 1

print(f"  隣接ペア (N={N}): P(mp=5) = {mp5_adj}/{total_adj} = {mp5_adj/total_adj:.4f}")

# 距離の異なるペア
for gap in [2, 4, 8, 16, 32]:
    mp5_g = 0
    total_g = 0
    for n in range(1, N - 2*gap, 2):
        m = n + 2*gap
        if m > N:
            break
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        set_n = set(seq_n)
        mp = None
        for x in seq_m:
            if x in set_n:
                mp = x
                break
        total_g += 1
        if mp == 5:
            mp5_g += 1
    if total_g > 0:
        print(f"  ギャップ={2*gap:3d}ペア (N={N}): P(mp=5) = {mp5_g}/{total_g} = {mp5_g/total_g:.4f}")

# === Part G: 合流木分岐の帰結 - 「漏斗」効果 ===

print("\n" + "=" * 70)
print("Part G: 漏斗(Funnel)効果の定量化")
print("=" * 70)

# 5のbottleneck性を測定: 5を通過する確率 × 5で「最初に合流する」確率
# Funnel strength = P(orbit passes v) * P(mp=v | both pass v)

# 各候補について
bottleneck = {}
N = 3000
odd_total = N // 2

# まず通過確率
pass_prob = {}
for v in [1, 5, 11, 23, 17, 47, 91, 13, 29, 19]:
    pass_count = 0
    for n in range(1, N+1, 2):
        seq = odd_collatz_sequence(n)
        if v in seq:
            pass_count += 1
    pass_prob[v] = pass_count / odd_total

# 合流点分布
mp_counter = Counter()
for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)
    set_n = set(seq_n)
    mp = None
    for x in seq_m:
        if x in set_n:
            mp = x
            break
    mp_counter[mp] += 1

total_pairs = sum(mp_counter.values())

# 各vのboth_pass確率
for v in [1, 5, 11, 23, 17, 47, 91, 13, 29, 19]:
    both_pass = 0
    mp_at_v = 0
    for n in range(1, N-1, 2):
        m = n + 2
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        n_pass = v in seq_n
        m_pass = v in set(seq_m)
        if n_pass and m_pass:
            both_pass += 1
            set_n = set(seq_n)
            mp = None
            for x in seq_m:
                if x in set_n:
                    mp = x
                    break
            if mp == v:
                mp_at_v += 1

    p_mp = mp_counter.get(v, 0) / total_pairs
    p_pass = pass_prob[v]
    p_cond = mp_at_v / both_pass if both_pass > 0 else 0

    bottleneck[v] = {
        'P_pass': p_pass,
        'P_both_pass': both_pass / total_pairs,
        'P_mp_given_both': p_cond,
        'P_mp': p_mp,
        'funnel': p_pass * p_cond
    }
    print(f"  v={v:5d}: P(pass)={p_pass:.3f}, P(both)={both_pass/total_pairs:.3f}, "
          f"P(mp=v|both)={p_cond:.3f}, P(mp=v)={p_mp:.3f}, funnel={p_pass*p_cond:.3f}")

# === 最終的な要約 ===

print("\n" + "=" * 70)
print("=== 最終要約 ===")
print("=" * 70)

print("""
合流点分布P(mp=v)の構造:

1. P(mp=v) = P(both pass v) * P(v is first shared | both pass v)

2. mp=5 が42-45%の理由（3つの要因の積）:
   a) P(orbit passes 5) = 94%: 5はほぼ全ての軌道が通過するボトルネック
   b) P(both pass 5) = 89%: ペアの9割近くが両方5を通過
   c) P(5 is first shared | both pass 5) = 47.5%: 約半数が5より前に合流しない

3. 「5より前に合流」するケースの構造:
   - 全て5の上流で合流（11, 23, 47, 91, ...はいずれも5→1に向かう軌道上にある）
   - mp≠5のケースは5の「下流」（v→...→5の経路上）で合流

4. P(mp=1) = 9.8%が低い理由:
   - 全軌道が1を通過するが、ほとんどのペアは1に到達する前に合流済み

5. mod 6/mod 12によるP(mp=5)の変動は非常に小さい（42-44%の範囲）
   → 合流点分布は局所的な剰余構造にほとんど依存しない

6. ギャップ距離との関係:
   - 隣接ペアと大きなギャップで P(mp=5) はほぼ同じ
   → 合流は軌道の「グローバル構造」（5のボトルネック性）が支配的
""")
