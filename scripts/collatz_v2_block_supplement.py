#!/usr/bin/env python3
"""
v2列ブロック統計 補足分析

1. 個別の長い軌道でのエントロピー率
2. (4,2,2,4,3)パターンのアトラクション機構の特定
3. エントロピー率の理論的下界推定
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

def get_v2_sequence(n, length=5000):
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

def extract_blocks(seq, L):
    blocks = []
    for i in range(len(seq) - L + 1):
        block = tuple(seq[i:i+L])
        blocks.append(block)
    return blocks

def compute_block_entropy(seq, L):
    blocks = extract_blocks(seq, L)
    counter = Counter(blocks)
    total = len(blocks)
    H = 0.0
    for block, count in counter.items():
        p = count / total
        if p > 0:
            H -= p * math.log2(p)
    return H, total

print("=" * 70)
print("v2列ブロック統計 補足分析")
print("=" * 70)

# ========================================
# Part 1: 大きなnの長い軌道でのエントロピー
# ========================================
print("\n" + "-" * 70)
print("Part 1: 大きなnの長い軌道でのブロックエントロピー")
print("-" * 70)

# 有名な長い軌道を持つ数
long_ns = [837799, 626331, 939497, 511935, 796095, 1564063, 2643183]
print(f"\n個別の長い軌道でのエントロピー率:")
print(f"{'n':>10} {'軌道長':>8} {'H(1)':>8} {'H(3)/3':>8} {'H(5)/5':>8} {'H(8)/8':>8}")

for n in long_ns:
    seq = get_v2_sequence(n, 5000)
    if len(seq) < 50:
        continue
    H1, _ = compute_block_entropy(seq, 1)

    results = [H1]
    for L in [3, 5, 8]:
        if len(seq) >= L + 5:
            HL, total = compute_block_entropy(seq, L)
            results.append(HL / L)
        else:
            results.append(float('nan'))

    print(f"  {n:10d} {len(seq):8d} {results[0]:8.4f} {results[1]:8.4f} "
          f"{results[2]:8.4f} {results[3]:8.4f}")


# ========================================
# Part 2: (4,2,2,4,3) パターンの共有軌道
# ========================================
print("\n" + "-" * 70)
print("Part 2: (4,2,2,4,3) パターンへの合流構造")
print("-" * 70)

# パターン直前の値を追跡
pre_pattern_values = []
for n in range(3, 50001, 2):
    seq = get_v2_sequence(n, 500)
    orbit = [n]
    current = n
    for i in range(len(seq)):
        val = 3 * current + 1
        current = val >> v2(val)
        orbit.append(current)

    for i in range(len(seq) - 4):
        if tuple(seq[i:i+5]) == (4, 2, 2, 4, 3):
            # パターン開始時のnの値
            pre_pattern_values.append(orbit[i])
            break

counter = Counter(pre_pattern_values)
print(f"(4,2,2,4,3)パターン開始時の値 (上位20):")
for val, cnt in counter.most_common(20):
    print(f"  値={val}: {cnt}回 (v2(3*{val}+1)={v2(3*val+1)})")

# 最も共通の値からの具体的軌道
most_common_val = counter.most_common(1)[0][0]
print(f"\n最も共通の値 {most_common_val} からの軌道:")
current = most_common_val
for step in range(10):
    val = 3 * current + 1
    v = v2(val)
    next_n = val >> v
    print(f"  step {step}: n={current}, v2(3n+1)=v2({val})={v}, T(n)={next_n}")
    current = next_n


# ========================================
# Part 3: エントロピー率の理論的推定
# ========================================
print("\n" + "-" * 70)
print("Part 3: エントロピー率の理論的推定")
print("-" * 70)

# h(k) = H(k+1) - H(k) の推移から漸近的エントロピー率を推定
# 集約データで計算
from collections import Counter as C

def aggregate_v2(n_start, n_end, step=2, max_len=500):
    all_seq = []
    count = 0
    for n in range(n_start, n_end + 1, step):
        if n % 2 == 0:
            continue
        seq = get_v2_sequence(n, max_len)
        if len(seq) >= 10:
            all_seq.extend(seq)
            count += 1
    return all_seq, count

all_seq, n_count = aggregate_v2(3, 49999, step=2, max_len=500)
print(f"v2列総長: {len(all_seq)}")

# H(k)をk=1..8で計算
entropies = {}
for L in range(1, 9):
    HL, total = compute_block_entropy(all_seq, L)
    entropies[L] = HL

# 条件付きエントロピー率
h_rates = []
for k in range(1, 8):
    h = entropies[k + 1] - entropies[k]
    h_rates.append(h)

print(f"\n条件付きエントロピー率の推移:")
for i, h in enumerate(h_rates):
    print(f"  h({i+1}) = {h:.6f}")

# Richardsonの外挿
print(f"\nh_rates の差分:")
diffs = []
for i in range(len(h_rates) - 1):
    d = h_rates[i] - h_rates[i + 1]
    diffs.append(d)
    print(f"  h({i+1}) - h({i+2}) = {d:.6f}")

print(f"\n差分の差分:")
for i in range(len(diffs) - 1):
    dd = diffs[i] - diffs[i + 1]
    print(f"  dd({i+1}) = {dd:.6f}")

# 推定: h(k)がおよそ幾何的に減少するなら
# h_inf = lim h(k) を推定
if len(h_rates) >= 3:
    # 最後の3点で外挿
    h7 = h_rates[-1]  # h(7)
    h6 = h_rates[-2]  # h(6)
    h5 = h_rates[-3]  # h(5)

    # h(k) ~ h_inf + A * r^k と仮定
    # h6 - h7 = A*r^6*(1-r)
    # h5 - h6 = A*r^5*(1-r)
    # ratio = r
    if (h5 - h6) > 0:
        r_est = (h6 - h7) / (h5 - h6)
        print(f"\n減少率の推定: r = {r_est:.4f}")
        if abs(r_est) < 1:
            h_inf_est = h7 - (h6 - h7) * r_est / (1 - r_est)
            print(f"漸近エントロピー率 h_inf の推定: {h_inf_est:.6f} bits")
            print(f"（比較: 独立仮定では H(1) = {entropies[1]:.6f} bits）")
            print(f"情報量の削減率: {(1 - h_inf_est/entropies[1])*100:.2f}%")
        else:
            print(f"r >= 1 なのでエントロピー率は0に収束する可能性")
            print(f"v2列は高い冗長度を持つ（決定論的構造が強い）")


# ========================================
# Part 4: v2=4の特異な構造の数論的解明
# ========================================
print("\n" + "-" * 70)
print("Part 4: v2=4が過大表現される数論的メカニズム")
print("-" * 70)

# v2(3n+1) = 4 iff 3n+1 = 16m (mは奇数) iff n = (16m-1)/3
# n = 5 mod 16
print(f"v2(3n+1)=4 の条件: n = 5 mod 16")

# Syracuse: T(n) = (3n+1)/16 when v2=4
# 次にv2(3*T(n)+1) = v2(3*(3n+1)/16+1) = v2((9n+3+16)/16) = v2((9n+19)/16)
# Wait, 3*T(n)+1 = 3*(3n+1)/16 + 1 = (9n+3+16)/16 = (9n+19)/16

# v2(3n+1)の分布は n mod 2^k で決まる
# 実測のv2=4の頻度: 0.0902 vs 理論 0.0625
# 比率 = 1.4428

# これは軌道がn=5 mod 16 を通過する確率が1/8より高いことを意味する
print(f"\n実測 P(v2=4) = 0.0902, 理論 P(v2=4) = 0.0625, 比 = 1.44")

# mod 16 での遷移を追跡
print(f"\n各 n mod 16 -> T(n) mod 16 の遷移:")
for r in range(16):
    if r % 2 == 0:
        continue
    val = 3 * r + 1
    v = v2(val)
    t = (val >> v)
    t_mod16 = t % 16
    print(f"  n={r:2d} mod 16: v2={v}, T(n)={t:3d} mod 16 -> T(n) mod 16 = {t_mod16:2d}")

# n = 5 mod 16 に向かう経路の数を数える
print(f"\nT(n) = 5 mod 16 になるnの残基:")
targets_5 = []
for r in range(32):
    if r % 2 == 0:
        continue
    val = 3 * r + 1
    v = v2(val)
    t = val >> v
    if t % 16 == 5:
        targets_5.append(r)
        print(f"  n = {r} mod 32: T(n) = {t} -> {t%16} mod 16")

print(f"\n  T(n) mod 16 = 5 となる奇数残基の数: {len(targets_5)}/16")


# ========================================
# Part 5: ブロック (1,1,...,1,k) の頻度パターン
# ========================================
print("\n" + "-" * 70)
print("Part 5: ブロック (1,1,...,1,k) の頻度パターン")
print("-" * 70)

# 連続する1の後の値による条件付き分布
for prefix_len in [1, 2, 3, 4, 5]:
    prefix = tuple([1] * prefix_len)
    suffix_counts = Counter()
    for i in range(len(all_seq) - prefix_len):
        if tuple(all_seq[i:i+prefix_len]) == prefix:
            suffix_counts[all_seq[i + prefix_len]] += 1

    total = sum(suffix_counts.values())
    if total < 100:
        continue
    print(f"\nP(v2 | {prefix}) [n={total}]:")
    for v in sorted(suffix_counts.keys())[:8]:
        obs = suffix_counts[v] / total
        theo = 1.0 / (2 ** v)
        print(f"  v2={v}: 実測={obs:.4f}, 理論={theo:.4f}, 比={obs/theo:.4f}")


print("\n" + "=" * 70)
print("補足分析完了")
print("=" * 70)
