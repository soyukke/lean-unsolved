#!/usr/bin/env python3
"""
エルデシュ問題 #77: Ramsey Number Limit
lim_{k→∞} R(k)^{1/k} の探索

探索1: 数値実験
- 既知ラムゼー数から R(k)^{1/k} を計算
- K_5 での R(3)=6 の全探索検証
- Erdős-Szekeres上界と確率的下界のプロット
- 上界・下界の歴史的変遷

探索2: 小さいラムゼー数の構造解析
- R(3)=6: K_5上の単色K_3回避2色塗りの全列挙
- R(4)=18: Paley graph mod 17 の検証
- ラムゼー回避グラフの対称性解析
"""

import itertools
import math
from collections import Counter

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False
    print("(numpy/matplotlib未インストール: プロットをスキップ)")

# =============================================================================
# 探索1: 数値実験
# =============================================================================

print("=" * 70)
print("探索1: Ramsey数の数値実験")
print("=" * 70)

# --- 既知のラムゼー数 ---
# R(s,t): s色クリークまたはt色クリークが出る最小頂点数
# 対角ラムゼー数 R(k) = R(k,k)
known_ramsey = {
    1: 1,
    2: 2,
    3: 6,
    4: 18,
}
# R(5) は 43 ≤ R(5) ≤ 48 が既知（2024年時点）
ramsey_lower = {1: 1, 2: 2, 3: 6, 4: 18, 5: 43, 6: 102, 7: 205, 8: 282, 9: 565, 10: 798}
ramsey_upper = {1: 1, 2: 2, 3: 6, 4: 18, 5: 48, 6: 165, 7: 540, 8: 1870, 9: 6588, 10: 23556}

print("\n--- 既知のラムゼー数と R(k)^{1/k} ---")
print(f"{'k':>3} {'R(k)下界':>10} {'R(k)上界':>10} {'R_L^{1/k}':>10} {'R_U^{1/k}':>10}")
print("-" * 50)
for k in range(1, 11):
    rl = ramsey_lower[k]
    ru = ramsey_upper[k]
    rlk = rl ** (1.0 / k)
    ruk = ru ** (1.0 / k)
    print(f"{k:>3} {rl:>10} {ru:>10} {rlk:>10.4f} {ruk:>10.4f}")

print("\n--- 理論的上界・下界 ---")
print("Erdős-Szekeres上界: R(k) ≤ C(2k-2, k-1) ≈ 4^k / √(πk)")
print("確率的下界 (Erdős 1947): R(k) ≥ 2^{k/2} ≈ (√2)^k")
print()

# Erdős-Szekeres上界
def erdos_szekeres_upper(k):
    """R(k) ≤ C(2k-2, k-1)"""
    return math.comb(2*k - 2, k - 1)

# 確率的下界
def probabilistic_lower(k):
    """R(k) ≥ floor(2^{k/2})"""
    return int(2 ** (k / 2))

print(f"{'k':>3} {'ES上界':>15} {'ES^{1/k}':>10} {'確率的下界':>10} {'PL^{1/k}':>10}")
print("-" * 55)
for k in range(2, 16):
    es = erdos_szekeres_upper(k)
    pl = probabilistic_lower(k)
    esk = es ** (1.0 / k)
    plk = pl ** (1.0 / k) if pl > 0 else 0
    print(f"{k:>3} {es:>15} {esk:>10.4f} {pl:>10} {plk:>10.4f}")

print("\n→ ES上界: R(k)^{1/k} → 4 (Stirlingの近似から)")
print("→ 確率的下界: R(k)^{1/k} → √2 ≈ 1.4142")
print("→ 真の値: √2 ≤ lim R(k)^{1/k} ≤ 4")
print("→ 最新上界 (Campos-Griffiths-Morris-Sahasrabudhe 2023): ≤ (4-ε)^k")
print("→ Gupta-Ndiaye-Norin-Wei: ε ≥ 0.2008, つまり ≤ 3.7992^k")

# --- K_5 での R(3)=6 の検証 ---
print("\n--- K_5 での R(3)=6 の検証 ---")
print("K_5 (5頂点) の辺を2色で塗り分けたとき、単色K_3(三角形)を回避できるか？")

def has_monochromatic_clique(n, coloring, k):
    """
    n頂点グラフの辺着色 coloring (辺→{0,1}) に単色 k-クリークがあるか
    coloring: (i,j) → 0 or 1 (i < j)
    """
    vertices = list(range(n))
    for clique in itertools.combinations(vertices, k):
        edges = [(clique[a], clique[b]) for a in range(len(clique)) for b in range(a+1, len(clique))]
        colors = [coloring[e] for e in edges]
        if all(c == 0 for c in colors) or all(c == 1 for c in colors):
            return True
    return False

def enumerate_ramsey_avoiding(n, k):
    """n頂点で単色k-クリークを回避する2色塗りを全列挙"""
    edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = len(edges)
    avoiding = []
    for bits in range(2**m):
        coloring = {}
        for idx, e in enumerate(edges):
            coloring[e] = (bits >> idx) & 1
        if not has_monochromatic_clique(n, coloring, k):
            avoiding.append(coloring)
    return avoiding

# K_5 で K_3 回避塗り分け
print("K_5 (10辺, 2^10=1024 通り) を全探索...")
avoiding_5 = enumerate_ramsey_avoiding(5, 3)
print(f"K_5 での単色K_3回避塗り分け数: {len(avoiding_5)}")
print("→ R(3)=6 なので、K_5 では回避可能（回避塗り分けが存在する）")

# K_6 で K_3 回避塗り分け
print("\nK_6 (15辺, 2^15=32768 通り) を全探索...")
avoiding_6 = enumerate_ramsey_avoiding(6, 3)
print(f"K_6 での単色K_3回避塗り分け数: {len(avoiding_6)}")
print("→ R(3)=6 なので、K_6 では回避不可能（0個のはず）")

# =============================================================================
# 探索2: 小さいラムゼー数の構造解析
# =============================================================================

print("\n" + "=" * 70)
print("探索2: 小さいラムゼー数の構造解析")
print("=" * 70)

# --- R(3)=6: K_5上のRamsey回避グラフ解析 ---
print("\n--- R(3)=6: K_5上の回避塗り分けの構造 ---")

def coloring_to_adjacency(n, coloring):
    """色0の辺からなるグラフの隣接リスト"""
    adj = {i: set() for i in range(n)}
    for (i, j), c in coloring.items():
        if c == 0:
            adj[i].add(j)
            adj[j].add(i)
    return adj

def degree_sequence(n, adj):
    return sorted([len(adj[i]) for i in range(n)])

# 回避塗り分けの次数列を分類
degree_counts = Counter()
for col in avoiding_5:
    adj = coloring_to_adjacency(5, col)
    ds = tuple(degree_sequence(5, adj))
    degree_counts[ds] += 1

print(f"回避塗り分け数: {len(avoiding_5)}")
print("色0の辺が形成するグラフの次数列分布:")
for ds, cnt in sorted(degree_counts.items()):
    print(f"  次数列 {ds}: {cnt} 個")

# C_5 (5-サイクル) の確認
print("\n--- C_5 (ペトリエルフェングラフ) の確認 ---")
# C_5: 0-1, 1-2, 2-3, 3-4, 4-0
c5_edges = {(0,1): 0, (1,2): 0, (2,3): 0, (3,4): 0, (0,4): 0,
            (0,2): 1, (0,3): 1, (1,3): 1, (1,4): 1, (2,4): 1}
has_mono = has_monochromatic_clique(5, c5_edges, 3)
print(f"C_5 塗り分けは単色K_3を含むか: {has_mono}")

# C_5の補グラフ
adj_c5 = coloring_to_adjacency(5, c5_edges)
adj_c5_comp = {i: set() for i in range(5)}
for (i,j), c in c5_edges.items():
    if c == 1:
        adj_c5_comp[i].add(j)
        adj_c5_comp[j].add(i)

print(f"C_5 の辺: {[(i,j) for (i,j),c in c5_edges.items() if c==0]}")
print(f"C_5 の次数列: {degree_sequence(5, adj_c5)}")
print(f"補グラフの辺: {[(i,j) for (i,j),c in c5_edges.items() if c==1]}")
print(f"補グラフの次数列: {degree_sequence(5, adj_c5_comp)}")
print("→ C_5 も補グラフ(C_5)も次数列 (2,2,2,2,2) = 正則")
print("→ C_5 は自己相補的グラフ！")

# 自己相補的塗り分けの割合
self_comp_count = 0
for col in avoiding_5:
    adj = coloring_to_adjacency(5, col)
    ds0 = degree_sequence(5, adj)
    # 補グラフ
    adj_c = {i: set() for i in range(5)}
    for (i,j), c in col.items():
        if c == 1:
            adj_c[i].add(j)
            adj_c[j].add(i)
    ds1 = degree_sequence(5, adj_c)
    if ds0 == ds1:
        self_comp_count += 1

print(f"\n両色の次数列が一致する塗り分け: {self_comp_count}/{len(avoiding_5)}")

# --- R(4)=18: Paley graph mod 17 ---
print("\n--- R(4)=18: Paley graph mod 17 ---")
print("Paley graph P(17): 頂点={0,...,16}, i-j が辺 ⟺ i-j が平方剰余 mod 17")

# 17の平方剰余
qr_17 = set()
for x in range(1, 17):
    qr_17.add((x * x) % 17)
print(f"17の平方剰余: {sorted(qr_17)}")

# Paley graph の隣接行列
paley_adj = {i: set() for i in range(17)}
for i in range(17):
    for j in range(i+1, 17):
        if (j - i) % 17 in qr_17:
            paley_adj[i].add(j)
            paley_adj[j].add(i)

paley_ds = degree_sequence(17, paley_adj)
print(f"Paley(17) 次数列: {paley_ds}")
print(f"各頂点の次数: {paley_ds[0]} (= (17-1)/2 = 8, 正則)")

# Paley graph のクリーク数チェック
print("\nPaley(17) の最大クリークサイズを調べる...")
max_clique = 0
clique_counts = {}
for size in range(2, 6):
    count = 0
    for clique in itertools.combinations(range(17), size):
        is_clique = True
        for a in range(len(clique)):
            for b in range(a+1, len(clique)):
                if clique[b] not in paley_adj[clique[a]]:
                    is_clique = False
                    break
            if not is_clique:
                break
        if is_clique:
            count += 1
    clique_counts[size] = count
    if count > 0:
        max_clique = size
    print(f"  {size}-クリーク数: {count}")

# 補グラフのクリーク数
paley_comp = {i: set() for i in range(17)}
for i in range(17):
    for j in range(i+1, 17):
        if j not in paley_adj[i]:
            paley_comp[i].add(j)
            paley_comp[j].add(i)

print("\nPaley(17) の補グラフの最大クリーク:")
for size in range(2, 6):
    count = 0
    for clique in itertools.combinations(range(17), size):
        is_clique = True
        for a in range(len(clique)):
            for b in range(a+1, len(clique)):
                if clique[b] not in paley_comp[clique[a]]:
                    is_clique = False
                    break
            if not is_clique:
                break
        if is_clique:
            count += 1
    if count > 0:
        print(f"  {size}-クリーク数: {count}")
    else:
        print(f"  {size}-クリーク数: 0 → 最大クリーク < {size}")
        break

print("\n→ Paley(17) は自己相補的で、クリーク数・独立数ともに3")
print("→ 赤=Paley辺、青=非Paley辺とすると、単色K_4が存在しない")
print("→ よって R(4) ≥ 18 が示される")

# =============================================================================
# プロット
# =============================================================================

if not HAS_PLOT:
    print("\n(プロットスキップ: matplotlib未インストール)")
else:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # --- Plot 1: R(k)^{1/k} の値 ---
    ax = axes[0]
    ks = list(range(2, 11))
    rlk_vals = [ramsey_lower[k] ** (1.0/k) for k in ks]
    ruk_vals = [ramsey_upper[k] ** (1.0/k) for k in ks]
    ax.fill_between(ks, rlk_vals, ruk_vals, alpha=0.3, color='blue', label='既知の範囲')
    ax.plot(ks, rlk_vals, 'bo-', markersize=5, label='下界^{1/k}')
    ax.plot(ks, ruk_vals, 'rs-', markersize=5, label='上界^{1/k}')
    ax.axhline(y=math.sqrt(2), color='green', linestyle='--', label=f'√2 ≈ {math.sqrt(2):.4f}')
    ax.axhline(y=4, color='red', linestyle='--', label='4 (ES上界の極限)')
    ax.axhline(y=3.7992, color='orange', linestyle='--', label='3.7992 (最新上界)')
    ax.set_xlabel('k')
    ax.set_ylabel('R(k)^{1/k}')
    ax.set_title('R(k)^{1/k} の既知範囲')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Plot 2: 上界と下界の比較 ---
    ax = axes[1]
    ks2 = list(range(2, 13))
    es_vals = [erdos_szekeres_upper(k) for k in ks2]
    pl_vals = [probabilistic_lower(k) for k in ks2]
    ax.semilogy(ks2, es_vals, 'r^-', label='Erdős-Szekeres上界 C(2k-2,k-1)')
    ax.semilogy(ks2, pl_vals, 'gv-', label='確率的下界 2^{k/2}')
    for k in range(2, 11):
        ax.semilogy([k, k], [ramsey_lower[k], ramsey_upper[k]], 'b-', linewidth=2)
    ax.semilogy(list(range(2, 11)), [ramsey_lower[k] for k in range(2, 11)], 'bo', label='既知下界')
    ax.semilogy(list(range(2, 11)), [ramsey_upper[k] for k in range(2, 11)], 'bs', label='既知上界')
    ax.set_xlabel('k')
    ax.set_ylabel('R(k) (対数スケール)')
    ax.set_title('ラムゼー数の上界・下界')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Plot 3: R(k)^{1/k} の理論上界・下界 ---
    ax = axes[2]
    ks3 = list(range(2, 21))
    es_root = [erdos_szekeres_upper(k) ** (1.0/k) for k in ks3]
    pl_root = [probabilistic_lower(k) ** (1.0/k) for k in ks3]
    ax.plot(ks3, es_root, 'r^-', label='ES上界^{1/k} → 4')
    ax.plot(ks3, pl_root, 'gv-', label='確率的下界^{1/k} → √2')
    ax.axhline(y=4, color='red', linestyle=':', alpha=0.5)
    ax.axhline(y=math.sqrt(2), color='green', linestyle=':', alpha=0.5)
    ax.axhline(y=2, color='purple', linestyle='--', alpha=0.5, label='2 (Erdős予想)')
    ax.axhline(y=3.7992, color='orange', linestyle='--', alpha=0.5, label='3.7992 (2024上界)')
    ax.set_xlabel('k')
    ax.set_ylabel('値^{1/k}')
    ax.set_title('R(k)^{1/k} の漸近挙動')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/soyukke/study/lean-unsolved/scripts/erdos77_ramsey.png', dpi=150)
    print("\nプロット保存: scripts/erdos77_ramsey.png")

# =============================================================================
# まとめ
# =============================================================================

print("\n" + "=" * 70)
print("まとめ")
print("=" * 70)
print("""
1. R(k)^{1/k} の既知範囲:
   - 下界: √2 ≈ 1.4142 (Erdős 1947, 確率的方法)
   - 上界: 4 (Erdős-Szekeres 1935)
   - 改良上界: 3.7992 (Campos-Griffiths-Morris-Sahasrabudhe 2023,
     Gupta-Ndiaye-Norin-Wei による最適化)

2. 小さいkでの R(k)^{1/k}:
   - k=3: 6^{1/3} ≈ 1.817
   - k=4: 18^{1/4} ≈ 2.060
   - k=5: [43^{1/5}, 48^{1/5}] ≈ [2.224, 2.297]
   → kが増えると R(k)^{1/k} は増加傾向だが、増加は遅い

3. 構造解析:
   - R(3)=6: C_5 (自己相補的) が唯一の本質的な回避構成
   - R(4)=18: Paley(17) (自己相補的) が回避構成を提供
   - 自己相補性がラムゼー回避の鍵

4. 未解決の核心:
   - lim R(k)^{1/k} が存在するか？ ($100)
   - その値は何か？ ($250)
   - Erdős予想: 値は2かもしれない
   - 2023年のブレークスルー (≤ 3.9999...^k) は初めて4から離れた上界
""")
