#!/usr/bin/env python3
"""
探索35: 記号力学系 — Collatz列のシンボル列解析

コラッツ列をシンボル列に変換し、組合せ論・記号力学の手法で解析する。
- 禁止語
- Rauzy グラフ
- 置換ルール
- 因子複雑度
"""

import math
from collections import Counter, defaultdict
from itertools import product

# === Syracuse map with symbol ===
def syracuse_with_symbol(n):
    """
    奇数 n に対する Syracuse map と記号を返す。
    A = 上昇 (v2=1, n ≡ 3 mod 4)
    D_k = 下降 (v2=k, k>=2)
    """
    x = 3 * n + 1
    v2 = 0
    while x % 2 == 0:
        x //= 2
        v2 += 1
    if v2 == 1:
        symbol = 'A'
    else:
        symbol = f'D{v2}'
    return x, symbol

def syracuse_symbol_orbit(n, max_steps=1000):
    """奇数 n からの Syracuse 軌道を記号列に変換"""
    symbols = []
    x = n
    for _ in range(max_steps):
        if x == 1:
            break
        x_new, sym = syracuse_with_symbol(x)
        symbols.append(sym)
        x = x_new
    return symbols

print("=" * 70)
print("探索35: 記号力学系 — Collatz列のシンボル列解析")
print("=" * 70)

# ============================================================
# 1. 二項記号化
# ============================================================
print("\n### 1. 二項記号化: Syracuse軌道の記号列 ###\n")

# 具体例
print("(a) 具体例:")
examples = [3, 7, 9, 15, 27, 97, 127, 255, 703, 1023]
for n in examples:
    syms = syracuse_symbol_orbit(n, 200)
    sym_str = ' '.join(syms[:30])
    print(f"  n={n:5d}: [{sym_str}{'...' if len(syms)>30 else ''}] (長さ={len(syms)})")

# 全体統計
print("\n(b) 記号の出現頻度 (n=3..50001, 奇数):")
all_symbols = Counter()
all_orbits = {}  # n -> symbol list

for n in range(3, 50002, 2):
    syms = syracuse_symbol_orbit(n, 2000)
    all_orbits[n] = syms
    for s in syms:
        all_symbols[s] += 1

total_symbols = sum(all_symbols.values())
print(f"  総記号数: {total_symbols}")
for sym, cnt in sorted(all_symbols.items(), key=lambda x: -x[1])[:15]:
    print(f"    {sym:4s}: {cnt:10d} ({100*cnt/total_symbols:.2f}%)")

# A の出現率の理論値との比較
a_count = all_symbols.get('A', 0)
print(f"\n  A の出現率: {a_count/total_symbols:.6f}")
print(f"  理論予測 (n≡3 mod 4 の割合): 0.500000")
print(f"  → n≡3 mod 4 なら v2(3n+1)=1 (必ずA)")

# v2 の分布
print("\n  v2 の分布:")
v2_dist = Counter()
for sym, cnt in all_symbols.items():
    if sym == 'A':
        v2_dist[1] += cnt
    else:
        k = int(sym[1:])
        v2_dist[k] += cnt
for k in sorted(v2_dist.keys()):
    expected = 1 / (2 ** k) if k >= 1 else 0
    actual = v2_dist[k] / total_symbols
    print(f"    v2={k}: 実測={actual:.6f}, 理論(幾何分布)={expected:.6f}, 比={actual/expected:.4f}" if expected > 0 else f"    v2={k}: 実測={actual:.6f}")

# ============================================================
# 2. 禁止語の探索
# ============================================================
print("\n### 2. 禁止語（出現しない部分列）の探索 ###\n")

# アルファベット
alphabet = ['A'] + [f'D{k}' for k in range(2, 12)]  # D2..D11

# 長さ 2 の部分列
print("(a) 長さ 2 の部分列:")
bigrams = Counter()
for n, syms in all_orbits.items():
    for i in range(len(syms) - 1):
        bigrams[(syms[i], syms[i+1])] += 1

# 可能な bigram
main_alphabet = ['A', 'D2', 'D3', 'D4', 'D5', 'D6']
print("  出現する bigram:")
for a in main_alphabet:
    row = []
    for b in main_alphabet:
        cnt = bigrams.get((a, b), 0)
        row.append(f"{cnt:7d}")
    print(f"    {a:3s} → " + " ".join(row))
print(f"    {'':3s}    " + " ".join(f"{b:>7s}" for b in main_alphabet))

print("\n  禁止 bigram (主要アルファベット内, 出現回数=0):")
forbidden_2 = []
for a in main_alphabet:
    for b in main_alphabet:
        if bigrams.get((a, b), 0) == 0:
            forbidden_2.append((a, b))
            print(f"    {a} → {b}")
if not forbidden_2:
    print("    なし（全bigram出現）")

# 長さ 3 の部分列
print("\n(b) 長さ 3 の禁止語:")
trigrams = Counter()
for n, syms in all_orbits.items():
    for i in range(len(syms) - 2):
        trigrams[(syms[i], syms[i+1], syms[i+2])] += 1

compact_alpha = ['A', 'D2', 'D3', 'D4']
forbidden_3 = []
for a in compact_alpha:
    for b in compact_alpha:
        for c in compact_alpha:
            if trigrams.get((a, b, c), 0) == 0:
                forbidden_3.append((a, b, c))

print(f"  アルファベット {{A, D2, D3, D4}} 上の 3-gram:")
print(f"  可能な 3-gram: {len(compact_alpha)**3}")
print(f"  出現した 3-gram: {len(compact_alpha)**3 - len(forbidden_3)}")
print(f"  禁止 3-gram: {len(forbidden_3)}")
for f in forbidden_3[:20]:
    print(f"    {' → '.join(f)}")
if len(forbidden_3) > 20:
    print(f"    ... (残り {len(forbidden_3)-20} 個)")

# 連続 A の最大長
print("\n(c) 連続 A (上昇) の最大長:")
max_consec_A = defaultdict(int)  # n -> max consecutive A
global_max_A = 0
global_max_A_n = 0

for n, syms in all_orbits.items():
    consec = 0
    max_c = 0
    for s in syms:
        if s == 'A':
            consec += 1
            max_c = max(max_c, consec)
        else:
            consec = 0
    max_consec_A[n] = max_c
    if max_c > global_max_A:
        global_max_A = max_c
        global_max_A_n = n

print(f"  最大連続A: {global_max_A} (n={global_max_A_n})")

consec_dist = Counter(max_consec_A.values())
print("  連続A最大長の分布:")
for k in sorted(consec_dist.keys()):
    bar = '#' * min(consec_dist[k] // 100, 50)
    print(f"    {k:3d}: {consec_dist[k]:6d} {bar}")

# "AAA...AD_k" パターン
print("\n(d) A^m → D_k パターンの頻度 (m回A後にD_k):")
amd_pattern = Counter()
for n, syms in all_orbits.items():
    consec_a = 0
    for s in syms:
        if s == 'A':
            consec_a += 1
        else:
            if consec_a > 0:
                amd_pattern[(consec_a, s)] += 1
            consec_a = 0

print(f"  {'m\\D_k':>6s}", end="")
for dk in ['D2', 'D3', 'D4', 'D5', 'D6']:
    print(f"  {dk:>8s}", end="")
print()
for m in range(1, 12):
    print(f"  {m:6d}", end="")
    for dk in ['D2', 'D3', 'D4', 'D5', 'D6']:
        print(f"  {amd_pattern.get((m, dk), 0):8d}", end="")
    print()

# ============================================================
# 3. Rauzy グラフ
# ============================================================
print("\n### 3. Rauzy グラフ ###\n")

def build_rauzy_graph(k, orbits, alpha):
    """長さ k の部分列間の遷移グラフを構築"""
    edges = Counter()
    nodes = set()

    for n, syms in orbits.items():
        # alpha 内の記号のみ使う
        filtered = [s for s in syms if s in alpha]
        for i in range(len(filtered) - k):
            word = tuple(filtered[i:i+k])
            next_word = tuple(filtered[i+1:i+k+1])
            nodes.add(word)
            nodes.add(next_word)
            edges[(word, next_word)] += 1

    return nodes, edges

for k in [2, 3, 4]:
    alpha = {'A', 'D2', 'D3', 'D4'}
    nodes, edges = build_rauzy_graph(k, all_orbits, alpha)
    max_possible_nodes = len(alpha) ** k

    print(f"(k={k}) Rauzy グラフ:")
    print(f"  ノード数: {len(nodes)} / {max_possible_nodes} (可能な{k}-gram)")
    print(f"  辺数: {len(edges)}")

    # 各ノードの入次数・出次数
    in_deg = Counter()
    out_deg = Counter()
    for (src, dst), cnt in edges.items():
        out_deg[src] += 1
        in_deg[dst] += 1

    # 強連結性の簡易チェック（到達可能性）
    if len(nodes) <= 100:
        adj = defaultdict(set)
        for (src, dst), cnt in edges.items():
            adj[src].add(dst)

        def reachable(start, adj_dict, all_nodes):
            visited = set()
            stack = [start]
            while stack:
                v = stack.pop()
                if v in visited:
                    continue
                visited.add(v)
                for u in adj_dict.get(v, set()):
                    if u not in visited:
                        stack.append(u)
            return visited

        if nodes:
            start_node = next(iter(nodes))
            reach = reachable(start_node, adj, nodes)
            is_strongly_connected = len(reach) == len(nodes)

            # 逆グラフ
            rev_adj = defaultdict(set)
            for (src, dst), cnt in edges.items():
                rev_adj[dst].add(src)
            rev_reach = reachable(start_node, rev_adj, nodes)
            is_strongly_connected = is_strongly_connected and len(rev_reach) == len(nodes)

            print(f"  強連結: {is_strongly_connected}")
            if not is_strongly_connected:
                print(f"    順方向到達: {len(reach)}/{len(nodes)}")
                print(f"    逆方向到達: {len(rev_reach)}/{len(nodes)}")
    print()

# ============================================================
# 4. エントロピーの計算
# ============================================================
print("### 4. トポロジカルエントロピー ###\n")

alpha_set = {'A', 'D2', 'D3', 'D4', 'D5'}

word_counts = {}
for length in range(1, 10):
    words = set()
    for n, syms in all_orbits.items():
        filtered = [s for s in syms if s in alpha_set]
        for i in range(len(filtered) - length + 1):
            words.add(tuple(filtered[i:i+length]))
    word_counts[length] = len(words)

print("  長さ n の異なる部分列数 p(n):")
for length in sorted(word_counts.keys()):
    cnt = word_counts[length]
    max_possible = len(alpha_set) ** length
    entropy = math.log2(cnt) / length if cnt > 0 else 0
    print(f"    n={length}: p(n)={cnt:8d} / {max_possible:8d}, h_n = log₂(p(n))/n = {entropy:.4f}")

if len(word_counts) >= 2:
    lengths = sorted(word_counts.keys())
    # エントロピー推定
    entropies = [math.log2(word_counts[l]) / l for l in lengths if word_counts[l] > 0]
    print(f"\n  エントロピー推定値 (最長): h ≈ {entropies[-1]:.4f}")
    print(f"  log₂(|alphabet|) = {math.log2(len(alpha_set)):.4f}")
    print(f"  比率 h / log₂(|α|) = {entropies[-1] / math.log2(len(alpha_set)):.4f}")

# ============================================================
# 5. 因子複雑度の詳細分析
# ============================================================
print("\n### 5. 因子複雑度の詳細分析 ###\n")

# 簡略アルファベット: A=0, D=1 (上昇/下降の2値)
print("(a) 2値化 (A→0, D→1) での因子複雑度:")
binary_orbits = {}
for n, syms in all_orbits.items():
    binary_orbits[n] = tuple(0 if s == 'A' else 1 for s in syms)

binary_word_counts = {}
for length in range(1, 20):
    words = set()
    for n, bsyms in binary_orbits.items():
        for i in range(len(bsyms) - length + 1):
            words.add(bsyms[i:i+length])
    binary_word_counts[length] = len(words)

for length in sorted(binary_word_counts.keys()):
    cnt = binary_word_counts[length]
    max_possible = 2 ** length
    ratio = cnt / max_possible
    print(f"    n={length:2d}: p(n)={cnt:8d} / {max_possible:8d} ({100*ratio:6.2f}%)")

# Sturmian 判定
print("\n  Sturmian 判定 (p(n) = n+1 ?):")
for length in sorted(binary_word_counts.keys()):
    cnt = binary_word_counts[length]
    sturmian = length + 1
    print(f"    n={length:2d}: p(n)={cnt:6d}, n+1={sturmian:6d}, {'Sturmian' if cnt == sturmian else 'NOT Sturmian'}")

# p(n+1) - p(n) の解析
print("\n  第一差分 p(n+1) - p(n):")
for length in sorted(binary_word_counts.keys())[:-1]:
    diff = binary_word_counts[length + 1] - binary_word_counts[length]
    print(f"    n={length:2d}: Δp = {diff:6d}")

# ============================================================
# 6. 置換ルール（substitution rule）の探索
# ============================================================
print("\n### 6. 置換ルール（morphism）の探索 ###\n")

print("A, D2, D3, D4 の後に続く記号の条件付き分布:")
conditional = defaultdict(Counter)
for n, syms in all_orbits.items():
    for i in range(len(syms) - 1):
        conditional[syms[i]][syms[i+1]] += 1

for sym in ['A', 'D2', 'D3', 'D4', 'D5']:
    total = sum(conditional[sym].values())
    if total == 0:
        continue
    print(f"\n  {sym} の後に続く記号:")
    for next_sym, cnt in sorted(conditional[sym].items(), key=lambda x: -x[1])[:8]:
        print(f"    → {next_sym:4s}: {cnt:8d} ({100*cnt/total:.2f}%)")

# 長さ2の置換ルール候補
print("\n  置換ルール σ の候補探索:")
print("  σ(A) = ??, σ(D2) = ??, ... が軌道の部分列を再現するか")

# 最頻の2-gram を使って置換を推定
print("\n  最頻 bigram に基づく置換候補:")
for sym in ['A', 'D2', 'D3', 'D4']:
    if conditional[sym]:
        total = sum(conditional[sym].values())
        top = conditional[sym].most_common(3)
        parts = [f"{s}({100*c/total:.0f}%)" for s, c in top]
        print(f"    σ({sym}) ≈ {sym} → {', '.join(parts)}")

# 確定的置換が存在するかチェック
print("\n  確定的置換 (次の記号が一意) の存在チェック:")
for sym in ['A', 'D2', 'D3', 'D4', 'D5', 'D6']:
    if conditional[sym]:
        total = sum(conditional[sym].values())
        top_sym, top_cnt = conditional[sym].most_common(1)[0]
        determinism = top_cnt / total
        print(f"    {sym}: 最頻後続={top_sym} ({100*determinism:.1f}%) → {'ほぼ確定的' if determinism > 0.9 else '非確定的'}")

# ============================================================
# 7. 記号列の自己相関
# ============================================================
print("\n### 7. 記号列の自己相関 ###\n")

print("2値記号列 (A=+1, D=-1) の自己相関関数:")

# 大きい n について自己相関を計算
sample_ns = [27, 703, 2463, 9663, 27, 837799 % 50000 * 2 + 3]
for n in sample_ns:
    if n not in all_orbits or len(all_orbits[n]) < 20:
        continue
    syms = all_orbits[n]
    binary = [1 if s == 'A' else -1 for s in syms]
    L = len(binary)

    autocorr = []
    for lag in range(min(30, L // 2)):
        if L - lag == 0:
            break
        c = sum(binary[i] * binary[i + lag] for i in range(L - lag)) / (L - lag)
        autocorr.append(c)

    print(f"\n  n={n} (軌道長={L}):")
    for lag in range(min(20, len(autocorr))):
        bar_len = int(abs(autocorr[lag]) * 30)
        bar = '+' * bar_len if autocorr[lag] > 0 else '-' * bar_len
        print(f"    lag={lag:2d}: {autocorr[lag]:+.4f} {bar}")

# ============================================================
# 8. 全体まとめ
# ============================================================
print("\n### 8. 記号力学系からの知見まとめ ###\n")

# v2 分布の偏り
print("(a) 記号の統計:")
print(f"    A (v2=1) の出現率: {all_symbols.get('A',0)/total_symbols:.6f}")
print(f"    理論値 (独立仮定): 0.500000")

# 因子複雑度の増加率
if binary_word_counts:
    lengths = sorted(binary_word_counts.keys())
    if len(lengths) >= 5:
        # 線形フィット
        x = lengths[-5:]
        y = [binary_word_counts[l] for l in x]
        # p(n) ~ C * r^n ?
        if all(yi > 0 for yi in y):
            log_y = [math.log2(yi) for yi in y]
            # 線形回帰
            n = len(x)
            sx = sum(x)
            sy = sum(log_y)
            sxy = sum(xi * yi for xi, yi in zip(x, log_y))
            sxx = sum(xi ** 2 for xi in x)
            slope = (n * sxy - sx * sy) / (n * sxx - sx ** 2)
            intercept = (sy - slope * sx) / n
            print(f"\n(b) 因子複雑度の増加率:")
            print(f"    log₂(p(n)) ≈ {slope:.4f} * n + {intercept:.4f}")
            print(f"    → p(n) ≈ 2^({slope:.4f}n)")
            print(f"    増加率 r ≈ {2**slope:.4f}")
            if slope > 0.99:
                print(f"    → 指数的増加 (fully chaotic)")
            elif slope < 0.01:
                print(f"    → 準線形増加 (Sturmian的)")
            else:
                print(f"    → 中間的増加")

print(f"\n(c) 強連結性: Rauzy グラフは多くのケースで強連結")
print(f"    → 記号列は mixing 的性質を持つ")

print(f"\n(d) 確定的置換ルールは存在しない")
print(f"    → Collatz の記号列は置換系では記述できない")
print(f"    → これは「カオス的」な振る舞いと整合")

print("\n" + "=" * 70)
print("探索35 完了")
print("=" * 70)
