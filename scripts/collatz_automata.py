#!/usr/bin/env python3
"""
探索33: オートマトン的アプローチ
コラッツ写像をトランスデューサ/セルオートマトン/形式言語として解析
"""

import math
from collections import defaultdict, Counter

N_MAX = 50000

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def collatz_orbit(n):
    """軌道を返す (1に到達するまで)"""
    orbit = [n]
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        orbit.append(n)
    return orbit

def collatz_v2_sequence(n):
    """奇数コラッツの v2 列を返す: 奇数 n → (3n+1)/2^v2(3n+1) を繰り返す"""
    seq = []
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        if n % 2 == 0:
            n //= 2
            continue
        m = 3 * n + 1
        k = v2(m)
        seq.append(k)
        n = m >> k
    return seq

# ============================================================
# 1. 2進トランスデューサとしての Collatz
# ============================================================
print("=" * 70)
print("1. 2進トランスデューサとしての Collatz")
print("=" * 70)

print("\n1a. 3n+1 の2進演算: carry propagation パターン")
print(f"  奇数 n に対して 3n+1 = n + 2n + 1 の加算")
print(f"  n, 2n (=n<<1), n+2n+1 の2進表現と carry を解析\n")

print(f"  {'n':>8s}  {'bin(n)':>20s}  {'bin(3n+1)':>20s}  {'v2(3n+1)':>8s}  {'carry_len':>10s}  {'trail_1s':>8s}")
print("  " + "-" * 78)

for n in range(1, 64, 2):
    result = 3 * n + 1
    v = v2(result)
    # trailing 1s of n
    trail_ones = 0
    tmp = n
    while tmp & 1:
        trail_ones += 1
        tmp >>= 1

    # carry chain: 3n+1 = n + (n<<1) + 1
    # carry propagation length: find longest consecutive carry
    a = n
    b = (n << 1) + 1
    carry = 0
    max_carry_chain = 0
    current_chain = 0
    bits = max(a.bit_length(), b.bit_length()) + 2
    for bit in range(bits):
        bit_a = (a >> bit) & 1
        bit_b = (b >> bit) & 1
        s = bit_a + bit_b + carry
        carry = s >> 1
        if carry:
            current_chain += 1
            max_carry_chain = max(max_carry_chain, current_chain)
        else:
            current_chain = 0

    print(f"  {n:8d}  {bin(n):>20s}  {bin(result):>20s}  {v:8d}  {max_carry_chain:10d}  {trail_ones:8d}")

# 統計: carry chain の長さと v2 の関係
print("\n1b. carry chain の長さと v2(3n+1) の関係 (n=1..50000 奇数)")

carry_v2_data = defaultdict(list)  # carry_len -> [v2 values]
trail_v2_data = defaultdict(list)  # trailing_ones -> [v2 values]

for n in range(1, N_MAX + 1, 2):
    result = 3 * n + 1
    v = v2(result)

    # trailing 1s
    trail_ones = 0
    tmp = n
    while tmp & 1:
        trail_ones += 1
        tmp >>= 1

    # carry chain length
    a = n
    b = (n << 1) + 1
    carry = 0
    max_carry_chain = 0
    current_chain = 0
    bits = max(a.bit_length(), b.bit_length()) + 2
    for bit in range(bits):
        bit_a = (a >> bit) & 1
        bit_b = (b >> bit) & 1
        s = bit_a + bit_b + carry
        carry = s >> 1
        if carry:
            current_chain += 1
            max_carry_chain = max(max_carry_chain, current_chain)
        else:
            current_chain = 0

    carry_v2_data[max_carry_chain].append(v)
    trail_v2_data[trail_ones].append(v)

print(f"\n  carry chain長 → v2(3n+1) の平均:")
print(f"  {'carry_len':>10s}  {'count':>8s}  {'avg_v2':>10s}  {'min_v2':>8s}  {'max_v2':>8s}")
print("  " + "-" * 50)
for cl in sorted(carry_v2_data.keys())[:20]:
    vals = carry_v2_data[cl]
    print(f"  {cl:10d}  {len(vals):8d}  {sum(vals)/len(vals):10.4f}  {min(vals):8d}  {max(vals):8d}")

print(f"\n  末尾連続1の個数 → v2(3n+1) の平均:")
print(f"  {'trail_1s':>10s}  {'count':>8s}  {'avg_v2':>10s}  {'min_v2':>8s}  {'max_v2':>8s}")
print("  " + "-" * 50)
for t in sorted(trail_v2_data.keys())[:16]:
    vals = trail_v2_data[t]
    print(f"  {t:10d}  {len(vals):8d}  {sum(vals)/len(vals):10.4f}  {min(vals):8d}  {max(vals):8d}")

# ============================================================
# 2. Carry chain の詳細解析
# ============================================================
print("\n" + "=" * 70)
print("2. Carry chain の詳細解析")
print("=" * 70)

print("\n2a. v2(3n+1) と末尾1の個数の正確な関係")
print("  定理: n が奇数のとき、n の末尾が ...0 1^k (k個の1) なら")
print("  3n+1 の末尾ビットパターンは?")

# n = ...b 0 1...1 (k個の1) のとき
# 3n + 1 = 3(...b 0 1...1) + 1
# 末尾 k ビットが 1 なので n mod 2^k = 2^k - 1
# 3(2^k - 1) + 1 = 3*2^k - 2 = 2(3*2^(k-1) - 1)
# v2(3(2^k-1)+1) は?

print(f"\n  末尾パターン別の v2(3n+1):")
for k in range(1, 17):
    # n = 2^(k+1)*m + (2^k - 1) for m=0,1,2,...
    # つまり n ≡ 2^k - 1 (mod 2^(k+1)) なら末尾は 0 1^k
    # n ≡ 2^(k+1) - 1 (mod 2^(k+2)) なら末尾は 1^(k+1)
    n_test = (1 << k) - 1  # 1^k (k個の1)
    result = 3 * n_test + 1
    v = v2(result)
    print(f"  n = 1^{k} = {n_test}: 3n+1 = {result}, v2 = {v}, (3n+1)/2^v2 = {result >> v}")

print("\n2b. 連続する奇数ステップでの carry chain の伝播")

# 奇数コラッツ: T(n) = (3n+1) / 2^v2(3n+1) を繰り返す
# 各ステップでのcarry chain を追跡
print(f"\n  n=27 の奇数コラッツ軌道:")
n = 27
step = 0
while n != 1 and step < 50:
    if n % 2 == 0:
        n //= 2
        continue
    result = 3 * n + 1
    v = v2(result)
    next_n = result >> v

    # carry chain
    a = n
    b = (n << 1) + 1
    carry = 0
    max_cc = 0
    cur_cc = 0
    bits = max(a.bit_length(), b.bit_length()) + 2
    for bit in range(bits):
        bit_a = (a >> bit) & 1
        bit_b = (b >> bit) & 1
        s = bit_a + bit_b + carry
        carry = s >> 1
        if carry:
            cur_cc += 1
            max_cc = max(max_cc, cur_cc)
        else:
            cur_cc = 0

    trail_ones = 0
    tmp = n
    while tmp & 1:
        trail_ones += 1
        tmp >>= 1

    print(f"  step {step:2d}: n={n:10d} ({bin(n):>30s}) → v2={v}, carry={max_cc}, trail_1s={trail_ones}, next={next_n}")
    n = next_n
    step += 1

# ============================================================
# 3. Cellular automaton としての解釈
# ============================================================
print("\n" + "=" * 70)
print("3. Cellular automaton としての解釈")
print("=" * 70)

print("\n3a. コラッツ1ステップの「局所ルール」抽出")
print("  各ビット位置の変化を近傍のビットから予測できるか？")

# コラッツ1ステップ（奇数の場合）のビット変化ルール
# 入力: bit i-1, bit i, bit i+1 → 出力: bit i' (変換後のbit i)
# これは carry に依存するので非局所的！

rule_table = defaultdict(Counter)  # (neighborhood) -> Counter of output bits

for n in range(1, 10001, 2):
    result = 3 * n + 1
    bits_in = max(n.bit_length(), result.bit_length()) + 2

    for i in range(1, bits_in - 1):
        # 3-bit neighborhood of n
        b_left = (n >> (i + 1)) & 1
        b_center = (n >> i) & 1
        b_right = (n >> (i - 1)) & 1
        neighborhood = (b_left, b_center, b_right)

        # output bit
        out_bit = (result >> i) & 1
        rule_table[neighborhood][out_bit] += 1

print(f"\n  3-bit近傍 → 出力ビットの条件付き確率:")
print(f"  {'(L,C,R)':>10s}  {'P(out=0)':>10s}  {'P(out=1)':>10s}  {'count':>10s}  {'決定的?':>8s}")
print("  " + "-" * 52)

for nbr in sorted(rule_table.keys()):
    counts = rule_table[nbr]
    total = counts[0] + counts[1]
    p0 = counts[0] / total
    p1 = counts[1] / total
    deterministic = "YES" if p0 > 0.99 or p1 > 0.99 else "NO"
    print(f"  {str(nbr):>10s}  {p0:10.4f}  {p1:10.4f}  {total:10d}  {deterministic:>8s}")

print("\n  → carry 伝播のため、局所ルールでは決定的にならない")
print("  → コラッツ写像は本質的に非局所的 (carry = 長距離相互作用)")

# 5-bit neighborhood
print("\n  5-bit近傍での決定性:")
rule_table5 = defaultdict(Counter)

for n in range(1, 10001, 2):
    result = 3 * n + 1
    bits_in = max(n.bit_length(), result.bit_length()) + 2

    for i in range(2, bits_in - 2):
        nbr = tuple((n >> (i + j)) & 1 for j in range(-2, 3))
        out_bit = (result >> i) & 1
        rule_table5[nbr][out_bit] += 1

deterministic_count = 0
total_nbr = 0
for nbr in rule_table5:
    counts = rule_table5[nbr]
    total = counts[0] + counts[1]
    if total >= 10:
        total_nbr += 1
        p0 = counts[0] / total
        if p0 > 0.99 or p0 < 0.01:
            deterministic_count += 1

print(f"  5-bit近傍パターン数: {total_nbr}")
print(f"  決定的 (P>0.99): {deterministic_count} ({100*deterministic_count/total_nbr:.1f}%)")
print(f"  非決定的: {total_nbr - deterministic_count} ({100*(total_nbr-deterministic_count)/total_nbr:.1f}%)")

# ============================================================
# 4. v2 列の言語としての解析
# ============================================================
print("\n" + "=" * 70)
print("4. v2 列の言語としての解析")
print("=" * 70)

print("\n4a. v2 列のアルファベットと頻度")

v2_freq = Counter()
all_v2_seqs = []

for n in range(1, N_MAX + 1, 2):
    seq = collatz_v2_sequence(n)
    all_v2_seqs.append(seq)
    for v in seq:
        v2_freq[v] += 1

total_symbols = sum(v2_freq.values())
print(f"  総シンボル数: {total_symbols}")
print(f"  {'v2値':>6s}  {'出現数':>10s}  {'割合':>10s}  {'理論値 (1/2^k)':>15s}")
print("  " + "-" * 45)
for k in sorted(v2_freq.keys())[:15]:
    count = v2_freq[k]
    ratio = count / total_symbols
    theory = 1 / (2 ** k)
    print(f"  {k:6d}  {count:10d}  {ratio:10.6f}  {theory:15.6f}")

# 4b. v2 列のエントロピー
print("\n4b. v2 列のエントロピー")
entropy = 0
for k in v2_freq:
    p = v2_freq[k] / total_symbols
    if p > 0:
        entropy -= p * math.log2(p)

# 理論エントロピー (幾何分布 p=1/2)
theory_entropy = sum(-(1/2**k) * math.log2(1/2**k) for k in range(1, 30))
print(f"  実測エントロピー: {entropy:.6f} bits/symbol")
print(f"  理論エントロピー (幾何分布): {theory_entropy:.6f} bits/symbol")

# 4c. 2-gram, 3-gram 解析
print("\n4c. v2 列の n-gram 解析")

bigram_freq = Counter()
trigram_freq = Counter()

for seq in all_v2_seqs:
    for i in range(len(seq) - 1):
        bigram_freq[(seq[i], seq[i+1])] += 1
    for i in range(len(seq) - 2):
        trigram_freq[(seq[i], seq[i+1], seq[i+2])] += 1

print(f"\n  2-gram 上位20:")
print(f"  {'(a,b)':>12s}  {'count':>8s}  {'割合':>10s}")
print("  " + "-" * 34)
total_bigrams = sum(bigram_freq.values())
for bg, cnt in bigram_freq.most_common(20):
    print(f"  {str(bg):>12s}  {cnt:8d}  {cnt/total_bigrams:10.6f}")

# 条件付き確率: P(v2_{i+1} | v2_i)
print(f"\n  条件付き確率 P(v2_{{i+1}} = b | v2_i = a) 上位:")
cond_prob = defaultdict(Counter)
for (a, b), cnt in bigram_freq.items():
    cond_prob[a][b] += cnt

print(f"  {'v2_i':>6s}  {'v2_i+1':>8s}  {'P(b|a)':>10s}  {'count':>8s}")
print("  " + "-" * 36)
for a in sorted(cond_prob.keys())[:6]:
    total_a = sum(cond_prob[a].values())
    for b, cnt in cond_prob[a].most_common(5):
        print(f"  {a:6d}  {b:8d}  {cnt/total_a:10.6f}  {cnt:8d}")
    print()

# 4d. 1次マルコフエントロピー vs 0次エントロピー
print("4d. マルコフ性の検定")
# 0次エントロピー (iid仮定)
H0 = entropy

# 1次マルコフエントロピー
H1 = 0
for a in cond_prob:
    total_a = sum(cond_prob[a].values())
    p_a = total_a / total_bigrams
    for b in cond_prob[a]:
        p_ba = cond_prob[a][b] / total_a
        if p_ba > 0:
            H1 -= p_a * p_ba * math.log2(p_ba)

print(f"  0次エントロピー H(0): {H0:.6f} bits/symbol")
print(f"  1次マルコフエントロピー H(1): {H1:.6f} bits/symbol")
print(f"  情報利得 H(0) - H(1): {H0 - H1:.6f} bits/symbol")
print(f"  → {'マルコフ依存あり' if H0 - H1 > 0.01 else 'ほぼ独立'}")

# ============================================================
# 5. 最小 DFA の構成
# ============================================================
print("\n" + "=" * 70)
print("5. 最小DFAの構成: 「n が k ステップで 1 に到達する」")
print("=" * 70)

print("\n5a. 各 k に対して、ちょうど k ステップで 1 に到達する奇数の集合")

# 奇数コラッツ: T(n) = (3n+1)/2^v2(3n+1)
# k回の奇数ステップで1に到達する奇数の個数

def odd_collatz_steps(n):
    """奇数コラッツで1に到達するまでの奇数ステップ数"""
    steps = 0
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        if n % 2 == 0:
            n //= 2
            continue
        n = 3 * n + 1
        steps += 1
        while n % 2 == 0:
            n //= 2
    return steps if n == 1 else -1

step_counts = defaultdict(list)
for n in range(1, N_MAX + 1, 2):
    k = odd_collatz_steps(n)
    if k >= 0:
        step_counts[k].append(n)

print(f"  {'k':>4s}  {'count':>8s}  {'例 (最小5個)':>40s}")
print("  " + "-" * 56)
for k in sorted(step_counts.keys())[:25]:
    examples = step_counts[k][:5]
    print(f"  {k:4d}  {len(step_counts[k]):8d}  {examples}")

# 5b. mod 2^m での分類
print("\n5b. 「k 奇数ステップで到達」を mod 2^m で分類できるか")

for k_target in [1, 2, 3, 4, 5]:
    target_set = set(step_counts.get(k_target, []))
    if not target_set:
        continue

    print(f"\n  k={k_target} (到達する奇数: {len(target_set)} 個):")

    for m in range(1, 10):
        modulus = 1 << m
        residue_sets = defaultdict(lambda: [0, 0])  # residue -> [in_target, not_in_target]

        for n in range(1, min(N_MAX + 1, 50001), 2):
            r = n % modulus
            steps = odd_collatz_steps(n)
            if steps == k_target:
                residue_sets[r][0] += 1
            else:
                residue_sets[r][1] += 1

        # 「純粋な」残余類: その残余類の全要素が target に属する or 属さない
        pure_in = 0
        pure_out = 0
        mixed = 0
        for r in residue_sets:
            in_t, out_t = residue_sets[r]
            if in_t > 0 and out_t == 0:
                pure_in += 1
            elif in_t == 0 and out_t > 0:
                pure_out += 1
            else:
                mixed += 1

        total_classes = pure_in + pure_out + mixed
        if total_classes > 0:
            purity = (pure_in + pure_out) / total_classes
            print(f"    mod 2^{m}={modulus:5d}: 純粋クラス={pure_in+pure_out:4d}/{total_classes:4d} ({100*purity:.1f}%), 混合={mixed:4d}")

# 5c. DFA状態数の推定
print("\n5c. DFA状態数の推定 (Myhill-Nerode 同値類)")
print("  「n が k ステップ以内で到達」を判定する言語の複雑さ")

# n を2進数としてLSBから読む言語
# 同値類: n1 ≡ n2 iff (任意の suffix w について n1w と n2w が同じ言語に属する)
# 近似: mod 2^m で同じ振る舞いをする最小の m を見る

print(f"\n  {'k_max':>6s}  {'必要な mod 2^m':>15s}  {'推定状態数':>12s}")
print("  " + "-" * 37)

for k_max in range(1, 16):
    target = set()
    for k in range(0, k_max + 1):
        target.update(step_counts.get(k, []))

    # mod 2^m で完全に分離できる最小の m を探す
    best_m = None
    for m in range(1, 14):
        modulus = 1 << m
        residue_behavior = {}
        separates = True

        for r in range(modulus):
            if r % 2 == 0:
                continue  # 奇数のみ
            # r mod modulus の要素のうち target に属する割合
            in_count = 0
            total = 0
            for n in range(r, min(N_MAX + 1, 20001), modulus):
                if n > 0:
                    total += 1
                    steps = odd_collatz_steps(n)
                    if steps >= 0 and steps <= k_max:
                        in_count += 1

            if total > 0:
                ratio = in_count / total
                if 0.01 < ratio < 0.99:
                    separates = False
                    break

        if separates:
            best_m = m
            state_count = modulus // 2  # 奇数残余類の数
            break

    if best_m is not None:
        print(f"  {k_max:6d}  {'mod 2^' + str(best_m):>15s}  {state_count:12d}")
    else:
        print(f"  {k_max:6d}  {'>2^13':>15s}  {'>4096':>12s}")

# ============================================================
# 追加: carry propagation のパターンと v2 の厳密な関係
# ============================================================
print("\n" + "=" * 70)
print("追加: carry propagation と v2 の厳密な関係")
print("=" * 70)

print("\n  定理の検証: 奇数 n の末尾が ...0 1^k (k個の連続1) のとき")
print("  v2(3n+1) = 1 (k=1の場合を除き一般には不成立)")
print()

# 実際の関係を調べる
print("  末尾ビットパターン (最大6bit) → v2(3n+1) の決定性:")
for pattern_len in range(2, 7):
    modulus = 1 << pattern_len
    pattern_v2 = defaultdict(set)

    for n in range(1, min(N_MAX + 1, 100001), 2):
        pattern = n % modulus
        v = v2(3 * n + 1)
        pattern_v2[pattern].add(v)

    deterministic = sum(1 for p in pattern_v2 if len(pattern_v2[p]) == 1)
    total = len(pattern_v2)
    print(f"  {pattern_len} bits: 決定的 {deterministic}/{total} ({100*deterministic/total:.1f}%)")

    if pattern_len <= 4:
        for p in sorted(pattern_v2.keys()):
            vals = sorted(pattern_v2[p])
            det = "FIXED" if len(vals) == 1 else "varies"
            if len(vals) <= 3:
                print(f"    n≡{p} (mod {modulus}): v2 ∈ {vals} [{det}]")
            else:
                print(f"    n≡{p} (mod {modulus}): v2 ∈ {{{vals[0]},...,{vals[-1]}}} ({len(vals)} values) [{det}]")

print("\n" + "=" * 70)
print("総合考察")
print("=" * 70)
print("""
1. 2進トランスデューサとして:
   - 3n+1 は carry propagation を伴う加算
   - carry chain の長さが v2(3n+1) と相関するが、完全には決定しない
   - 末尾の連続1の個数が v2 を部分的に決める

2. セルオートマトンとして:
   - 3-bit 近傍では出力ビットは決定的にならない (carry のため)
   - 5-bit 近傍でも非決定的なパターンが残る
   - → コラッツ写像は本質的に非局所的 (長距離 carry 伝播)

3. 形式言語として:
   - v2 列のエントロピーは幾何分布に近い
   - 1次マルコフ依存は弱い → v2 列はほぼ独立
   - 「k ステップで到達」を判定する DFA の状態数は k とともに急速に増加

4. 含意:
   - コラッツの困難さは carry propagation の非局所性に起因
   - 局所的な（mod 2^m の）解析には限界がある
   - v2 列のほぼ独立性が「ランダムっぽく見える」理由
""")
