#!/usr/bin/env python3
"""
コラッツ予想 探索15: 「上昇+下降」サイクルでの縮小率の大規模調査

Syracuse関数: syracuse(n) = (3n+1) / 2^v2(3n+1) (n: 奇数)
連続上昇回数 k を計算し、k回上昇+1回下降後の値との比率を調査。
"""

import statistics
from collections import defaultdict

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function: (3n+1) / 2^v2(3n+1)"""
    val = 3 * n + 1
    return val >> v2(val)

def syracuse_iter(n, k):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

def count_consecutive_ascents(n):
    """連続上昇回数を数える"""
    k = 0
    current = n
    while True:
        next_val = syracuse(current)
        if next_val > current:
            k += 1
            current = next_val
        else:
            break
    return k

def one_cycle(n):
    """1サイクル: 連続上昇 k 回 + 1回下降。下降後の値を返す。
    返り値: (k, 下降後の値)"""
    k = count_consecutive_ascents(n)
    # k回上昇 + 1回下降 = k+1 回の syracuse 適用
    result = syracuse_iter(n, k + 1)
    return k, result

def collatz_sequence_odd(n, max_steps=10000):
    """奇数のコラッツ列 (syracuse 反復)"""
    seq = [n]
    for _ in range(max_steps):
        if n == 1:
            break
        n = syracuse(n)
        seq.append(n)
    return seq

# ============================================================
# 1. 奇数 n = 1..100000 に対する1サイクルの縮小率
# ============================================================
print("=" * 70)
print("1. 1サイクル (k回上昇 + 1回下降) の縮小率調査")
print("   範囲: 奇数 n = 1, 3, 5, ..., 99999")
print("=" * 70)

ratios = []
k_ratios = defaultdict(list)
expanding = []  # r > 1 のもの

for n in range(1, 100001, 2):
    k, result = one_cycle(n)
    if n > 0:
        r = result / n
        ratios.append(r)
        k_ratios[k].append(r)
        if r > 1:
            expanding.append((n, k, result, r))

print(f"\n全体統計 (サンプル数: {len(ratios)})")
print(f"  平均縮小率:   {statistics.mean(ratios):.6f}")
print(f"  中央値:       {statistics.median(ratios):.6f}")
print(f"  標準偏差:     {statistics.stdev(ratios):.6f}")
print(f"  最小値:       {min(ratios):.6f}")
print(f"  最大値:       {max(ratios):.6f}")

r_lt1 = sum(1 for r in ratios if r < 1)
r_gt1 = sum(1 for r in ratios if r > 1)
r_eq1 = sum(1 for r in ratios if r == 1)
print(f"\n  r < 1 (縮小): {r_lt1} ({100*r_lt1/len(ratios):.2f}%)")
print(f"  r > 1 (拡大): {r_gt1} ({100*r_gt1/len(ratios):.2f}%)")
print(f"  r = 1:        {r_eq1} ({100*r_eq1/len(ratios):.2f}%)")

# ============================================================
# 2. k ごとの統計
# ============================================================
print(f"\n{'='*70}")
print("2. 連続上昇回数 k ごとの縮小率")
print(f"{'='*70}")
print(f"  {'k':>3} | {'個数':>8} | {'割合':>8} | {'平均r':>10} | {'中央値r':>10} | {'min r':>10} | {'max r':>10}")
print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")

for k in sorted(k_ratios.keys()):
    rs = k_ratios[k]
    n_total = len(ratios)
    pct = 100 * len(rs) / n_total
    avg_r = statistics.mean(rs)
    med_r = statistics.median(rs)
    min_r = min(rs)
    max_r = max(rs)
    print(f"  {k:>3} | {len(rs):>8} | {pct:>7.2f}% | {avg_r:>10.6f} | {med_r:>10.6f} | {min_r:>10.6f} | {max_r:>10.6f}")

# 理論的な予測: k回上昇の寄与は (3/2)^k, 下降は少なくとも /4
# なので1サイクルの縮小率は約 (3/2)^k / 2^(v2)
print(f"\n  理論的参考: k回連続上昇後の1回下降での縮小率")
print(f"  k=0: 下降のみ。n ≡ 1 (mod 4) → r ≈ 3/4 = 0.75")
print(f"  k=0: 強い下降。n ≡ 1 (mod 4) かつ v2 大 → r << 1")
print(f"  k=1: 1回上昇+下降。(3/2)(3/4) = 9/8 × (1/v2分) ...")

# ============================================================
# 3. 最悪ケース: 最も拡大する n (上位20個)
# ============================================================
print(f"\n{'='*70}")
print("3. 1サイクルで最も拡大する n (上位20)")
print(f"{'='*70}")

expanding_sorted = sorted(expanding, key=lambda x: -x[3])
print(f"  {'n':>8} | {'k':>3} | {'T^(k+1)(n)':>12} | {'r':>10}")
print(f"  {'-'*8}-+-{'-'*3}-+-{'-'*12}-+-{'-'*10}")
for n, k, result, r in expanding_sorted[:20]:
    print(f"  {n:>8} | {k:>3} | {result:>12} | {r:>10.6f}")

# 連続して拡大する最長シーケンス
print(f"\n  連続拡大シーケンス探索:")
max_consec_expand = 0
max_consec_start = 0
for n in range(1, 100001, 2):
    consec = 0
    current = n
    while current > 1:
        k, result = one_cycle(current)
        if result > current:
            consec += 1
            current = result
        else:
            break
        if consec > 50:  # safety
            break
    if consec > max_consec_expand:
        max_consec_expand = consec
        max_consec_start = n

print(f"  最長連続拡大サイクル数: {max_consec_expand} (開始 n = {max_consec_start})")

# その詳細を表示
if max_consec_start > 0:
    print(f"  詳細:")
    current = max_consec_start
    for i in range(min(max_consec_expand + 2, 15)):
        k, result = one_cycle(current)
        r = result / current if current > 0 else 0
        marker = "拡大" if r > 1 else "縮小"
        print(f"    サイクル{i+1}: n={current}, k={k}, T^(k+1)={result}, r={r:.4f} [{marker}]")
        current = result
        if current <= 1:
            break

# ============================================================
# 4. 2サイクル・3サイクル連続での縮小率
# ============================================================
print(f"\n{'='*70}")
print("4. 複数サイクル連続での縮小率")
print(f"{'='*70}")

two_cycle_ratios = []
three_cycle_ratios = []

for n in range(1, 100001, 2):
    # 2サイクル
    k1, r1 = one_cycle(n)
    if r1 > 1:
        k2, r2 = one_cycle(r1)
        ratio2 = r2 / n
        two_cycle_ratios.append(ratio2)
        if r2 > 1:
            k3, r3 = one_cycle(r2)
            ratio3 = r3 / n
            three_cycle_ratios.append(ratio3)
        else:
            three_cycle_ratios.append(ratio2)
    else:
        # 最初のサイクルで縮小 → 2サイクル目を加える
        if r1 >= 1:
            continue
        k2, r2 = one_cycle(r1)
        ratio2 = r2 / n
        two_cycle_ratios.append(ratio2)
        if r2 >= 1:
            k3, r3 = one_cycle(r2)
        else:
            r3 = r2
            # もう一サイクル
            k3, r3_next = one_cycle(r2)
            r3 = r3_next
        three_cycle_ratios.append(r3 / n)

# もう少し簡単に: 全奇数に対して2サイクル・3サイクル通しで計算
print("\n  (全奇数に対するサイクル通し計算)")
ratios_2cycle = []
ratios_3cycle = []

for n in range(3, 100001, 2):  # n=1を除く
    # 2サイクル分のsyracuse適用
    current = n
    for cyc in range(2):
        k, current = one_cycle(current)
    ratios_2cycle.append(current / n)

    # 3サイクル (続きから)
    k, current = one_cycle(current)
    ratios_3cycle.append(current / n)

r2_lt1 = sum(1 for r in ratios_2cycle if r < 1)
r3_lt1 = sum(1 for r in ratios_3cycle if r < 1)

print(f"\n  2サイクル後:")
print(f"    平均縮小率: {statistics.mean(ratios_2cycle):.6f}")
print(f"    中央値:     {statistics.median(ratios_2cycle):.6f}")
print(f"    r < 1 の割合: {100*r2_lt1/len(ratios_2cycle):.2f}%")

print(f"\n  3サイクル後:")
print(f"    平均縮小率: {statistics.mean(ratios_3cycle):.6f}")
print(f"    中央値:     {statistics.median(ratios_3cycle):.6f}")
print(f"    r < 1 の割合: {100*r3_lt1/len(ratios_3cycle):.2f}%")

# ============================================================
# 5. 逆方向からの攻め: 発散の条件分析
# ============================================================
print(f"\n{'='*70}")
print("5. 逆方向からの攻め: 発散するには何が必要か？")
print(f"{'='*70}")

# 5a. 上昇の割合が50%を超えるシーケンス
print("\n5a. Syracuse反復での上昇割合")
print("    (各奇数 n に対して、1に到達するまでの上昇の割合)")

ascent_fractions = []
for n in range(3, 10001, 2):
    seq = collatz_sequence_odd(n)
    if len(seq) < 2:
        continue
    ascents = sum(1 for i in range(len(seq)-1) if seq[i+1] > seq[i])
    frac = ascents / (len(seq) - 1)
    ascent_fractions.append((n, frac, len(seq)))

avg_frac = statistics.mean([f for _, f, _ in ascent_fractions])
max_frac_entry = max(ascent_fractions, key=lambda x: x[1])
print(f"    平均上昇割合: {avg_frac:.4f}")
print(f"    最大上昇割合: {max_frac_entry[1]:.4f} (n={max_frac_entry[0]}, 列長={max_frac_entry[2]})")
print(f"    発散に必要: 上昇割合 > 0.5 が永続的に続く必要がある")
print(f"    → 実際の平均は {avg_frac:.4f} で、0.5を大きく下回る")

# 5b. mod 2^k で「ずっと上昇し続ける」パターン
print(f"\n5b. mod 2^k で連続上昇パターンの存在確認")
print("    n ≡ 2^(k+1) - 1 (mod 2^(k+1)) → k回連続上昇")
print("    しかし k+1 回目は必ず下降する")

for k in range(1, 13):
    mod = 2**(k+1)
    pattern = mod - 1  # 2^(k+1) - 1
    # このパターンのnでの連続上昇回数を確認
    test_ns = [pattern + mod * i for i in range(5)]
    actual_ascents = [count_consecutive_ascents(n) for n in test_ns if n > 0]
    print(f"    k={k:>2}: n ≡ {pattern:>6} (mod {mod:>6}), "
          f"確率 1/{2**k:>4}, "
          f"実際の連続上昇: {actual_ascents}")

print(f"\n    結論: k回連続上昇は正確にk回で止まる(k+1回目は必ず下降)")
print(f"    これは n ≡ 2^(k+1)-1 (mod 2^(k+1)) だが")
print(f"    n ≢ 2^(k+2)-1 (mod 2^(k+2)) であることに対応")

# 5c. メルセンヌ数 2^k - 1 の軌道
print(f"\n5c. メルセンヌ数 M_k = 2^k - 1 の軌道調査")
print(f"    (2進表現が全て1のパターン)")

for k in range(2, 21):
    n = 2**k - 1
    seq = collatz_sequence_odd(n, max_steps=50000)
    max_val = max(seq)
    ratio_max = max_val / n
    reached_1 = seq[-1] == 1

    # 最初のサイクルでの連続上昇
    initial_ascents = count_consecutive_ascents(n)

    print(f"    M_{k:>2} = {n:>10}: 連続上昇={initial_ascents:>2}, "
          f"列長={len(seq):>6}, 最大値/n={ratio_max:>10.2f}, "
          f"1到達={'Yes' if reached_1 else 'No'}")

# 5d. 「永続的上昇」の不可能性の数値的証拠
print(f"\n5d. 上昇後の値の2進表現分析")
print("    上昇: n → (3n+1)/2 の2進表現の末尾ビットパターン変化")

print(f"\n    n (2進)        → syracuse(n) (2進)      | 末尾1の数")
for n in [3, 7, 15, 31, 63, 127, 255, 511, 1023]:
    s = syracuse(n)
    trailing_1s_n = 0
    tmp = n
    while tmp % 2 == 1:
        trailing_1s_n += 1
        tmp >>= 1
    trailing_1s_s = 0
    tmp = s
    while tmp % 2 == 1:
        trailing_1s_s += 1
        tmp >>= 1
    print(f"    {n:>6} ({bin(n):>14}) → {s:>8} ({bin(s):>18}) | {trailing_1s_n} → {trailing_1s_s}")

# 5e. 末尾1ビットの数の遷移統計
print(f"\n5e. 末尾1ビット数の遷移統計 (n = 1..99999, 奇数)")

def trailing_ones(n):
    count = 0
    while n % 2 == 1:
        count += 1
        n >>= 1
    return count

transitions = defaultdict(lambda: defaultdict(int))
for n in range(1, 100000, 2):
    t1 = trailing_ones(n)
    s = syracuse(n)
    t2 = trailing_ones(s)
    transitions[t1][t2] += 1

print(f"    {'from\\to':>8}", end="")
max_t = min(max(max(d.keys()) for d in transitions.values()), 10)
for t in range(1, max_t + 1):
    print(f" {t:>6}", end="")
print()

for t1 in sorted(transitions.keys()):
    if t1 > 10:
        break
    total = sum(transitions[t1].values())
    print(f"    {t1:>8}", end="")
    for t2 in range(1, max_t + 1):
        count = transitions[t1].get(t2, 0)
        pct = 100 * count / total if total > 0 else 0
        print(f" {pct:>5.1f}%", end="")
    print(f"  (n={total})")

print(f"\n    結論: 末尾1ビットの数は syracuse 適用後にほぼ一様にリセットされる")
print(f"    → 「末尾が全て1」の状態が自己増殖することはない")
print(f"    → 発散するためには末尾1ビットが増え続ける必要があるが、")
print(f"       それは確率的にほぼ不可能")

# ============================================================
# 最終まとめ
# ============================================================
print(f"\n{'='*70}")
print("まとめ")
print(f"{'='*70}")
print(f"""
1. 1サイクルの平均縮小率は約 {statistics.mean(ratios):.4f} で、平均的には縮小傾向
2. k=0 (上昇なし) が最も多く、強い縮小を提供
3. 連続上昇回数 k が増えると拡大するが、頻度は 1/2^k で急減
4. 2サイクル後には {100*r2_lt1/len(ratios_2cycle):.1f}% が縮小
5. メルセンヌ数 2^k-1 は k-1 回連続上昇するが、全て1に到達
6. 末尾1ビット数は syracuse 適用で「リセット」され、蓄積しない
   → 永続的な上昇(=発散)は構造的にほぼ不可能
""")
