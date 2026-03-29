#!/usr/bin/env python3
"""
v2列のブロック統計: 長さLブロックの頻度とエントロピー

コラッツ予想のSyracuse関数 T(n) = (3n+1) / 2^{v2(3n+1)} において、
v2列 {v2(3*T^k(n)+1)} のL=3,4,5ブロックの実測頻度を計算し、
独立仮定からの偏差を定量化する。

ブロックエントロピー H(L) と L*H(1) の差（冗長度）を計算。
"""

import math
from collections import Counter, defaultdict
import json
import sys

# ========================================
# 基本関数
# ========================================

def v2(n):
    """2-adic valuation of n (nを割り切る2の最大冪)"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def syracuse(n):
    """Syracuse写像 T(n) = (3n+1) / 2^{v2(3n+1)}
    奇数nに対して定義。結果も奇数。"""
    val = 3 * n + 1
    return val >> v2(val)


def get_v2_sequence(n, length=500):
    """奇数nからSyracuse軌道のv2列を生成
    v2(k) = v2(3*T^k(n) + 1) を返す
    1に到達したら停止"""
    seq = []
    current = n
    for _ in range(length):
        if current == 1:
            break
        val = 3 * current + 1
        v = v2(val)
        seq.append(v)
        current = val >> v
    return seq


def get_v2_sequence_long(n, length=2000):
    """長いv2列を生成（1に到達しても継続: 1->2->1のサイクルで周期2）
    ただし1に到達したら停止する方が正確なので、到達前の列のみ使用"""
    return get_v2_sequence(n, length)


# ========================================
# ブロック頻度の計算
# ========================================

def extract_blocks(seq, L):
    """長さLの連続ブロックを抽出"""
    blocks = []
    for i in range(len(seq) - L + 1):
        block = tuple(seq[i:i+L])
        blocks.append(block)
    return blocks


def compute_block_frequencies(seq, L):
    """ブロック頻度を計算"""
    blocks = extract_blocks(seq, L)
    counter = Counter(blocks)
    total = len(blocks)
    freqs = {block: count / total for block, count in counter.items()}
    return freqs, counter, total


def theoretical_independent_freq(block):
    """独立仮定での理論的頻度: P(v2=j) = 1/2^j"""
    prob = 1.0
    for v in block:
        prob *= 1.0 / (2 ** v)
    return prob


def compute_block_entropy(freqs):
    """ブロック頻度からShannon entropyを計算"""
    H = 0.0
    for block, freq in freqs.items():
        if freq > 0:
            H -= freq * math.log2(freq)
    return H


def compute_single_v2_entropy(seq):
    """単一v2値のShannon entropy H(1)"""
    counter = Counter(seq)
    total = len(seq)
    H = 0.0
    for v, count in counter.items():
        p = count / total
        if p > 0:
            H -= p * math.log2(p)
    return H


def theoretical_single_entropy():
    """理論的な単一v2のエントロピー (幾何分布 p=1/2)
    H = sum_{j=1}^{inf} (1/2^j) * log2(2^j) = sum j/2^j = 2 bits"""
    return 2.0


# ========================================
# 大規模解析
# ========================================

def aggregate_v2_sequences(n_start, n_end, step=2, max_orbit_len=1000):
    """多数の奇数nに対するv2列を連結して集約"""
    all_seq = []
    count = 0
    for n in range(n_start, n_end + 1, step):
        if n % 2 == 0:
            continue
        seq = get_v2_sequence(n, max_orbit_len)
        if len(seq) >= 10:  # 十分長い軌道のみ
            all_seq.extend(seq)
            count += 1
    return all_seq, count


# ========================================
# メイン解析
# ========================================

print("=" * 70)
print("v2列のブロック統計: 長さLブロックの頻度とエントロピー")
print("=" * 70)

# ========================================
# Part 1: 個別のnでのv2列の確認
# ========================================
print("\n" + "-" * 70)
print("Part 1: 個別のnでのv2列サンプル")
print("-" * 70)

sample_ns = [27, 97, 127, 703, 6171, 77031, 837799]
for n in sample_ns:
    seq = get_v2_sequence(n, 500)
    print(f"\nn = {n}: v2列の長さ = {len(seq)}")
    print(f"  先頭20個: {seq[:20]}")
    if len(seq) > 0:
        counter = Counter(seq)
        total = len(seq)
        print(f"  値の分布:")
        for v in sorted(counter.keys()):
            obs = counter[v] / total
            theo = 1.0 / (2 ** v)
            print(f"    v2={v}: 実測={obs:.4f}, 理論={theo:.4f}, 比={obs/theo:.4f}")


# ========================================
# Part 2: 集約v2列からブロック頻度を計算
# ========================================
print("\n" + "-" * 70)
print("Part 2: 集約v2列からのブロック頻度 (n=3,5,...,49999)")
print("-" * 70)

all_seq, n_count = aggregate_v2_sequences(3, 49999, step=2, max_orbit_len=500)
print(f"集約した奇数の個数: {n_count}")
print(f"v2列の総長: {len(all_seq)}")

# 単一v2の分布
single_counter = Counter(all_seq)
single_total = len(all_seq)
print(f"\n単一v2値の分布:")
print(f"  {'v2':>3} {'実測頻度':>10} {'理論(1/2^j)':>12} {'比率':>8} {'実測数':>10}")
for v in sorted(single_counter.keys()):
    obs = single_counter[v] / single_total
    theo = 1.0 / (2 ** v)
    print(f"  {v:3d} {obs:10.6f} {theo:12.6f} {obs/theo:8.4f} {single_counter[v]:10d}")

H1 = compute_single_v2_entropy(all_seq)
H1_theo = theoretical_single_entropy()
print(f"\n単一v2エントロピー H(1): 実測={H1:.6f} bits, 理論={H1_theo:.6f} bits")


# ========================================
# Part 3: L=2,3,4,5 ブロック頻度
# ========================================
print("\n" + "-" * 70)
print("Part 3: ブロック長 L=2,3,4,5 での頻度・エントロピー")
print("-" * 70)

results = {}

for L in [2, 3, 4, 5]:
    freqs, counter, total = compute_block_frequencies(all_seq, L)
    HL = compute_block_entropy(freqs)
    redundancy = L * H1 - HL  # 冗長度 (正なら独立より少ない情報)

    # 理論的に出現しうるブロック数（v2値を1..max_vとして）
    max_v = max(all_seq)

    # 出現した異なるブロックの数
    n_observed = len(counter)

    # 理論独立頻度との比較
    chi_sq_stat = 0
    kl_divergence = 0
    top_overrepresented = []
    top_underrepresented = []

    for block, count in counter.items():
        obs_freq = count / total
        theo_freq = theoretical_independent_freq(block)
        if theo_freq > 0:
            ratio = obs_freq / theo_freq
            chi_sq_stat += (count - total * theo_freq) ** 2 / (total * theo_freq) if total * theo_freq > 5 else 0
            if obs_freq > 0:
                kl_divergence += obs_freq * math.log2(obs_freq / theo_freq)
            top_overrepresented.append((block, obs_freq, theo_freq, ratio))

    top_overrepresented.sort(key=lambda x: x[3], reverse=True)

    print(f"\n--- L = {L} ---")
    print(f"  総ブロック数: {total}")
    print(f"  観測された異なるブロック数: {n_observed}")
    print(f"  ブロックエントロピー H({L}): {HL:.6f} bits")
    print(f"  L * H(1): {L * H1:.6f} bits")
    print(f"  冗長度 L*H(1) - H(L): {redundancy:.6f} bits")
    print(f"  冗長度/L*H(1): {redundancy / (L * H1):.6f}")
    print(f"  KL divergence (実測 || 独立): {kl_divergence:.6f} bits")

    # 最も過大表現されたブロック
    print(f"\n  過大表現 top 10 (実測/理論 比率):")
    for block, obs, theo, ratio in top_overrepresented[:10]:
        count_val = counter[block]
        print(f"    {str(block):>18s}: 実測={obs:.6f}, 理論={theo:.6f}, "
              f"比={ratio:.4f}, 出現数={count_val}")

    # 最も過小表現されたブロック（理論上頻度が高いはずのもの）
    print(f"\n  過小表現 top 10 (実測/理論 比率) [理論>0.001のみ]:")
    underrep = [(b, o, t, r) for b, o, t, r in top_overrepresented if t > 0.001]
    underrep.sort(key=lambda x: x[3])
    for block, obs, theo, ratio in underrep[:10]:
        count_val = counter[block]
        print(f"    {str(block):>18s}: 実測={obs:.6f}, 理論={theo:.6f}, "
              f"比={ratio:.4f}, 出現数={count_val}")

    results[L] = {
        'H_L': HL,
        'L_times_H1': L * H1,
        'redundancy': redundancy,
        'KL_divergence': kl_divergence,
        'n_observed_blocks': n_observed,
        'total_blocks': total,
    }


# ========================================
# Part 4: 禁止パターンの分析
# ========================================
print("\n" + "-" * 70)
print("Part 4: 禁止パターン（理論上出現しうるが実測ゼロ）の分析")
print("-" * 70)

for L in [3, 4, 5]:
    freqs, counter, total = compute_block_frequencies(all_seq, L)
    max_v = 6  # v2値は1..6を考慮（6以上はまれ）

    # 理論上頻度が高い（>0.001）のに出現しないブロック
    forbidden = []
    possible_count = 0

    # v2値の範囲を1..max_vで全列挙
    from itertools import product
    for block in product(range(1, max_v + 1), repeat=L):
        theo = theoretical_independent_freq(block)
        if theo > 0.0001:  # 理論上ある程度の頻度があるもの
            possible_count += 1
            if block not in counter:
                forbidden.append((block, theo))

    forbidden.sort(key=lambda x: x[1], reverse=True)

    print(f"\n--- L = {L} ---")
    print(f"  理論頻度>0.0001のブロック数: {possible_count}")
    print(f"  そのうち実測ゼロのブロック数: {len(forbidden)}")
    print(f"  禁止率: {len(forbidden) / possible_count:.4f}" if possible_count > 0 else "  N/A")

    if forbidden:
        print(f"  理論頻度が高い禁止パターン top 15:")
        for block, theo in forbidden[:15]:
            print(f"    {str(block):>18s}: 理論頻度={theo:.6f}")


# ========================================
# Part 5: 条件付き確率の分析
# ========================================
print("\n" + "-" * 70)
print("Part 5: 条件付き確率 P(v2_{k+1} | v2_k) の実測")
print("-" * 70)

# 遷移行列の計算
transition_counts = defaultdict(lambda: defaultdict(int))
for i in range(len(all_seq) - 1):
    v_curr = all_seq[i]
    v_next = all_seq[i + 1]
    transition_counts[v_curr][v_next] += 1

print(f"\n遷移確率 P(v2_next | v2_curr):")
print(f"  {'curr\\next':>8}", end="")
for j in range(1, 8):
    print(f"  v2={j:d}  ", end="")
print()

for i in range(1, 7):
    total_i = sum(transition_counts[i].values())
    if total_i == 0:
        continue
    print(f"  v2={i:d}    ", end="")
    for j in range(1, 8):
        p = transition_counts[i][j] / total_i if total_i > 0 else 0
        theo = 1.0 / (2 ** j)
        # 色付け: 大きく外れたものをマーク
        mark = "*" if abs(p - theo) / theo > 0.1 and total_i > 100 else " "
        print(f" {p:.4f}{mark}", end="")
    print(f"  (n={total_i})")

print(f"\n  理論値（独立仮定）:")
print(f"  {'theo':>8}", end="")
for j in range(1, 8):
    print(f"  {1/(2**j):.4f} ", end="")
print()


# ========================================
# Part 6: 2次条件付き確率 P(v2_{k+2} | v2_k, v2_{k+1})
# ========================================
print("\n" + "-" * 70)
print("Part 6: 2次条件付き確率 P(v2_{k+2} | v2_k, v2_{k+1})")
print("-" * 70)

# 2次遷移の計算
second_order = defaultdict(lambda: defaultdict(int))
for i in range(len(all_seq) - 2):
    pair = (all_seq[i], all_seq[i + 1])
    v_next = all_seq[i + 2]
    second_order[pair][v_next] += 1

print(f"\n主要な2次遷移確率 (前2ステップ -> 次のv2):")
print(f"  {'(v_k, v_{k+1})':>14} {'v_{k+2}=1':>10} {'v_{k+2}=2':>10} "
      f"{'v_{k+2}=3':>10} {'v_{k+2}=4':>10} {'total':>8}")

for i in range(1, 5):
    for j in range(1, 5):
        pair = (i, j)
        total_pair = sum(second_order[pair].values())
        if total_pair < 50:
            continue
        probs = []
        for k in range(1, 5):
            p = second_order[pair][k] / total_pair
            probs.append(p)
        print(f"  ({i},{j})        ", end="")
        for p in probs:
            print(f" {p:9.4f}", end="")
        print(f" {total_pair:8d}")

# 独立からの最大偏差
print(f"\n独立仮定からの最大偏差のある2次遷移:")
max_devs = []
for pair, next_counts in second_order.items():
    total_pair = sum(next_counts.values())
    if total_pair < 100:
        continue
    for v_next, count in next_counts.items():
        obs_prob = count / total_pair
        theo_prob = 1.0 / (2 ** v_next)
        deviation = abs(obs_prob - theo_prob) / theo_prob
        max_devs.append((pair, v_next, obs_prob, theo_prob, deviation, total_pair))

max_devs.sort(key=lambda x: x[4], reverse=True)
print(f"  {'前2步':>10} {'次v2':>5} {'実測':>8} {'理論':>8} {'偏差%':>8} {'サンプル':>8}")
for pair, v_next, obs, theo, dev, n_samp in max_devs[:15]:
    print(f"  {str(pair):>10} {v_next:5d} {obs:8.4f} {theo:8.4f} {dev*100:7.2f}% {n_samp:8d}")


# ========================================
# Part 7: エントロピー率と冗長度のまとめ
# ========================================
print("\n" + "-" * 70)
print("Part 7: エントロピー率と冗長度のまとめ")
print("-" * 70)

print(f"\n{'L':>3} {'H(L)':>12} {'L*H(1)':>12} {'冗長度':>12} {'冗長度率':>10} "
      f"{'H(L)/L':>10} {'KL div':>10}")
for L in [1, 2, 3, 4, 5]:
    if L == 1:
        HL = H1
        red = 0
        kl = 0
    else:
        HL = results[L]['H_L']
        red = results[L]['redundancy']
        kl = results[L]['KL_divergence']
    LH1 = L * H1
    red_rate = red / LH1 if LH1 > 0 else 0
    HL_per_L = HL / L
    print(f"  {L:3d} {HL:12.6f} {LH1:12.6f} {red:12.6f} {red_rate:10.6f} "
          f"{HL_per_L:10.6f} {kl:10.6f}")

# 条件付きエントロピー h(L) = H(L) - H(L-1)
print(f"\n条件付きエントロピー h(L) = H(L) - H(L-1):")
prev_H = H1
for L in [2, 3, 4, 5]:
    HL = results[L]['H_L']
    cond_H = HL - prev_H
    print(f"  h({L}) = H({L}) - H({L-1}) = {cond_H:.6f} bits")
    prev_H = HL

# エントロピー率の収束
print(f"\nエントロピー率 H(L)/L の収束:")
for L in [1, 2, 3, 4, 5]:
    if L == 1:
        HL = H1
    else:
        HL = results[L]['H_L']
    print(f"  H({L})/{L} = {HL/L:.6f}")


# ========================================
# Part 8: 大きなnでの検証
# ========================================
print("\n" + "-" * 70)
print("Part 8: 大きなn (10^6近傍) でのブロック統計")
print("-" * 70)

large_seq, large_count = aggregate_v2_sequences(999001, 1000001, step=2, max_orbit_len=500)
print(f"集約した奇数の個数: {large_count}")
print(f"v2列の総長: {len(large_seq)}")

H1_large = compute_single_v2_entropy(large_seq)
print(f"H(1) [大きなn]: {H1_large:.6f}")

for L in [3, 5]:
    freqs_l, counter_l, total_l = compute_block_frequencies(large_seq, L)
    HL_l = compute_block_entropy(freqs_l)
    red_l = L * H1_large - HL_l
    print(f"\nL={L}: H({L})={HL_l:.6f}, L*H(1)={L*H1_large:.6f}, "
          f"冗長度={red_l:.6f}, H({L})/{L}={HL_l/L:.6f}")


# ========================================
# 結果のJSON出力
# ========================================
print("\n" + "=" * 70)
print("解析完了")
print("=" * 70)

summary = {
    "total_v2_length": len(all_seq),
    "n_count": n_count,
    "H1_observed": H1,
    "H1_theoretical": H1_theo,
    "block_analysis": {},
}

for L in [2, 3, 4, 5]:
    summary["block_analysis"][f"L={L}"] = {
        "H_L": results[L]['H_L'],
        "L_times_H1": results[L]['L_times_H1'],
        "redundancy": results[L]['redundancy'],
        "KL_divergence": results[L]['KL_divergence'],
        "n_observed_blocks": results[L]['n_observed_blocks'],
        "total_blocks": results[L]['total_blocks'],
    }

print(f"\n要約JSON:")
print(json.dumps(summary, indent=2))
