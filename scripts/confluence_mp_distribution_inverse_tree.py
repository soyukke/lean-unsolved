"""
探索163: 合流点分布P(mp=v)の逆像木分岐構造からの導出

核心問題: なぜmp=5が45%なのか?
逆像木（T^{-k}の分岐構造）から合流点分布を理論的に導出する。

アプローチ:
1. 各奇数vについて、逆像木T^{-k}(v)のサイズ（到達可能な数の数）を計算
2. 「vに合流する確率」∝「T^{-k}(v)のペアで合流するペア数」を検証
3. ギャップ比=4の構造が合流点集中にどう寄与するか分析
"""

import math
from collections import defaultdict, Counter
import time

# === Part 1: Syracuse関数の定義と基本ツール ===

def syracuse(n):
    """Syracuse map: T(n) for odd n"""
    assert n % 2 == 1
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def collatz_step(n):
    """Collatz step (works for any positive integer)"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def collatz_sequence(n):
    """Full Collatz sequence from n down to 1"""
    seq = [n]
    while n != 1:
        n = collatz_step(n)
        seq.append(n)
    return seq

def odd_collatz_sequence(n):
    """Syracuse sequence (odd numbers only) from n down to 1"""
    if n % 2 == 0:
        # find first odd
        while n % 2 == 0:
            n //= 2
    seq = [n]
    while n != 1:
        n = syracuse(n)
        seq.append(n)
    return seq

# === Part 2: 合流点の計算 ===

def meeting_point(a, b):
    """Find meeting point of Collatz sequences of a and b"""
    seq_a = set(collatz_sequence(a))
    seq_b = collatz_sequence(b)
    for x in seq_b:
        if x in seq_a:
            return x
    return None

def odd_meeting_point(a, b):
    """Find odd meeting point of Syracuse sequences"""
    seq_a = set(odd_collatz_sequence(a))
    seq_b = odd_collatz_sequence(b)
    for x in seq_b:
        if x in seq_a:
            return x
    return None

# === Part 3: 合流点分布の実測 ===

print("=" * 70)
print("Part 3: 合流点分布P(mp=v)の実測")
print("=" * 70)

N = 5000
mp_counter = Counter()
total_pairs = 0

# 隣接奇数ペア
for n in range(1, N, 2):
    m = n + 2
    if m <= N:
        mp = odd_meeting_point(n, m)
        mp_counter[mp] += 1
        total_pairs += 1

print(f"\n[1,{N}]内の隣接奇数ペア数: {total_pairs}")
print(f"\n合流点分布 (上位15):")
for v, count in mp_counter.most_common(15):
    print(f"  mp={v:6d}: count={count:5d}, P={count/total_pairs:.4f} ({count/total_pairs*100:.1f}%)")

# === Part 4: 逆像木のサイズと合流点確率の関係 ===

print("\n" + "=" * 70)
print("Part 4: 逆像木T^{-k}(v)のサイズと合流点確率")
print("=" * 70)

def inverse_syracuse_all(m, N_max):
    """Find all preimages n such that T(n)=m, n <= N_max, n odd"""
    preimages = []
    # n = (m * 2^j - 1) / 3, j=1,2,...
    for j in range(1, 60):
        num = m * (1 << j) - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1 and n <= N_max:
                preimages.append(n)
            if n > N_max:
                break
    return preimages

def inverse_bfs(root, depth, N_max):
    """BFS over inverse Syracuse tree, up to given depth, within [1, N_max]"""
    current_level = {root}
    all_reached = {root}
    for d in range(depth):
        next_level = set()
        for m in current_level:
            for pre in inverse_syracuse_all(m, N_max):
                if pre not in all_reached:
                    next_level.add(pre)
                    all_reached.add(pre)
        current_level = next_level
        if not current_level:
            break
    return all_reached

# 各合流点候補について逆像木サイズを計算
N_max = 10000
depth = 20
candidates = [1, 5, 11, 23, 91, 17, 7, 13, 3, 85, 341, 45, 181, 35, 71]

print(f"\n逆像木 T^{{-{depth}}}(v) のサイズ (v ∈ [1,{N_max}]の奇数):")
tree_sizes = {}
for v in candidates:
    tree = inverse_bfs(v, depth, N_max)
    tree_sizes[v] = len(tree)
    print(f"  v={v:6d}: |T^{{-{depth}}}(v)| = {len(tree)}")

# === Part 5: 合流確率とtree sizeの二乗の関係 ===

print("\n" + "=" * 70)
print("Part 5: P(mp=v) vs |T^{-k}(v)|^2 の関係")
print("=" * 70)

# 理論: ペア(a,b)がvで合流 ⟺ a,bともにT^{-k}(v)に入る
# → P(mp=v) ∝ |T^{-k}(v)|^2 (独立ペアの場合)
# ただし隣接ペアなので独立ではないが、近似として

# 全奇数中の比率
total_odd_in_range = len([n for n in range(1, N_max+1, 2)])
print(f"\n[1,{N_max}]内の奇数総数: {total_odd_in_range}")

# P(mp=v) の実測値（N=5000での値を使う）
for v in sorted(mp_counter.keys(), key=lambda x: -mp_counter[x])[:10]:
    if v in tree_sizes:
        p_measured = mp_counter[v] / total_pairs
        tree_frac = tree_sizes[v] / total_odd_in_range
        print(f"  v={v:6d}: P_measured={p_measured:.4f}, "
              f"|tree|/total={tree_frac:.4f}, "
              f"|tree|^2/total^2={tree_frac**2:.6f}, "
              f"ratio P/frac^2={p_measured/tree_frac**2:.2f}" if tree_frac > 0 else f"  v={v}: no tree")

# === Part 6: より深い分析 - 逆像木の重なり ===

print("\n" + "=" * 70)
print("Part 6: 逆像木の分岐確率と合流メカニズム")
print("=" * 70)

# コラッツ軌道が v を通過する確率 = |{n ∈ [1,N]: orbit(n) ∋ v}| / (N/2)
N_check = 5000
passage_count = Counter()
for n in range(1, N_check+1, 2):
    orbit = set(odd_collatz_sequence(n))
    for v in candidates:
        if v in orbit:
            passage_count[v] += 1

total_odd = N_check // 2
print(f"\n各奇数vを通過する確率 (N={N_check}):")
for v in candidates:
    p_pass = passage_count[v] / total_odd
    print(f"  v={v:6d}: P(orbit ∋ v) = {passage_count[v]}/{total_odd} = {p_pass:.4f} ({p_pass*100:.1f}%)")

# 合流確率 ≈ P(pass_a) * P(pass_b | pass_a) の推定
# 隣接ペアの場合、条件付き確率を直接計算

print("\n" + "=" * 70)
print("Part 7: P(mp=v) ≈ P(pass)^2 * correction の検証")
print("=" * 70)

# P(mp=v) vs P(pass)^2
print(f"\n  {'v':>6s}  {'P(mp=v)':>10s}  {'P(pass)':>10s}  {'P(pass)^2':>12s}  {'ratio':>8s}")
for v in sorted(mp_counter.keys(), key=lambda x: -mp_counter[x])[:10]:
    if v in passage_count:
        p_mp = mp_counter[v] / total_pairs
        p_pass = passage_count[v] / total_odd
        p2 = p_pass ** 2
        ratio = p_mp / p2 if p2 > 0 else float('inf')
        print(f"  {v:6d}  {p_mp:10.4f}  {p_pass:10.4f}  {p2:12.6f}  {ratio:8.2f}")

# === Part 8: より正確なモデル - 「最初の合流」確率 ===
print("\n" + "=" * 70)
print("Part 8: 最初の合流点 vs 単なる通過点")
print("=" * 70)

# 軌道上の位置（何番目に v に到達するか）
# mp = v ⟺ v は両軌道の「最初の」共有点
# → 到達順序が重要

# 各奇数nについて、軌道上で各候補に到達するステップ数を記録
def steps_to_reach(n, target):
    """Syracuse sequence上でtargetに到達するステップ数 (到達しなければ-1)"""
    seq = odd_collatz_sequence(n)
    for i, x in enumerate(seq):
        if x == target:
            return i
    return -1

# 隣接ペアについて、「最初に共有する奇数」の位置を分析
sample_pairs = [(n, n+2) for n in range(1, 1000, 2) if n+2 <= 1000]
first_shared_depth = []
for a, b in sample_pairs[:200]:
    seq_a = odd_collatz_sequence(a)
    seq_b = odd_collatz_sequence(b)
    set_a = set(seq_a)
    # bの軌道を辿って最初にaの軌道と共有する点を見つける
    mp = None
    for x in seq_b:
        if x in set_a:
            mp = x
            break
    if mp:
        # mpに到達するステップ数
        idx_a = seq_a.index(mp)
        idx_b = seq_b.index(mp)
        first_shared_depth.append((a, b, mp, idx_a, idx_b))

print(f"\n合流点への到達ステップ数の分析 (先頭200ペア):")
mp_depth_stats = defaultdict(list)
for a, b, mp, da, db in first_shared_depth:
    mp_depth_stats[mp].append((da, db))

for v in sorted(mp_depth_stats.keys(), key=lambda x: -len(mp_depth_stats[x]))[:10]:
    depths = mp_depth_stats[v]
    avg_da = sum(d[0] for d in depths) / len(depths)
    avg_db = sum(d[1] for d in depths) / len(depths)
    print(f"  mp={v:6d}: count={len(depths):4d}, "
          f"avg_step_a={avg_da:.1f}, avg_step_b={avg_db:.1f}, "
          f"avg_total={avg_da+avg_db:.1f}")
