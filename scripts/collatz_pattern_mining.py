#!/usr/bin/env python3
"""
探索055: コラッツ軌道のビット表現における頻出部分列マイニング

Syracuse軌道の各値を2進表現し、ビットパターンの共通構造を探索する。
値そのものではなく、ビットパターンの遷移規則を発見することが目標。
"""

import math
import random
import statistics
from collections import Counter, defaultdict

# =============================================================================
# 基本関数
# =============================================================================

def syracuse(n):
    """Syracuse関数: 奇数 n → (3n+1) / 2^v2(3n+1)"""
    m = 3 * n + 1
    v = (m & -m).bit_length() - 1
    return m >> v, v

def syracuse_orbit(n, max_steps=1000):
    """Syracuse軌道を返す（奇数のみ）"""
    orbit = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        nxt, _ = syracuse(current)
        orbit.append(nxt)
        current = nxt
    return orbit

def syracuse_orbit_with_v2(n, max_steps=1000):
    """Syracuse軌道と各ステップのv2を返す"""
    orbit = [n]
    v2s = []
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        nxt, v = syracuse(current)
        orbit.append(nxt)
        v2s.append(v)
        current = nxt
    return orbit, v2s

def mean(lst):
    return sum(lst) / len(lst) if lst else 0

def median(lst):
    s = sorted(lst)
    n = len(s)
    if n == 0:
        return 0
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2

def stdev(lst):
    if len(lst) < 2:
        return 0
    m = mean(lst)
    return math.sqrt(sum((x - m) ** 2 for x in lst) / len(lst))

def linspace(start, stop, n):
    if n == 1:
        return [start]
    step = (stop - start) / (n - 1)
    return [start + i * step for i in range(n)]

def interp(xnew, xold_n, yold):
    """線形補間"""
    result = []
    for x in xnew:
        if x <= 0:
            result.append(yold[0])
        elif x >= xold_n - 1:
            result.append(yold[-1])
        else:
            i = int(x)
            frac = x - i
            result.append(yold[i] * (1 - frac) + yold[i + 1] * frac)
    return result


# =============================================================================
# 1. 下位kビットの遷移パターン
# =============================================================================

def analyze_lower_bits(max_n=100000, k_values=[3, 4, 5]):
    """下位kビットの遷移パターンを分析"""
    print("=" * 70)
    print("1. 下位kビットの遷移パターン")
    print("=" * 70)

    for k in k_values:
        mask = (1 << k) - 1
        transition_count = Counter()
        total = 0

        for n in range(3, max_n + 1, 2):
            orbit = syracuse_orbit(n, max_steps=500)
            for i in range(len(orbit) - 1):
                src = orbit[i] & mask
                dst = orbit[i + 1] & mask
                transition_count[(src, dst)] += 1
                total += 1

        print(f"\n--- 下位 {k} ビット遷移 (mod 2^{k} = mod {1 << k}) ---")
        print(f"総遷移数: {total}, ユニーク遷移数: {len(transition_count)}")
        print(f"理論的最大ユニーク数: {(1 << k) * (1 << k)} (全組合せ)")
        print(f"実際に現れた割合: {len(transition_count) / ((1 << k) * (1 << k)) * 100:.1f}%")

        odd_transitions = {(s, d): c for (s, d), c in transition_count.items()
                          if s % 2 == 1 and d % 2 == 1}
        print(f"奇数→奇数遷移数: {len(odd_transitions)}")

        top = transition_count.most_common(15)
        print(f"\nトップ15遷移:")
        print(f"  {'src':>10} {'dst':>10} {'count':>10} {'freq%':>8}")
        for (s, d), c in top:
            print(f"  {bin(s):>10} {bin(d):>10} {c:>10} {c/total*100:>7.3f}%")

    return transition_count


# =============================================================================
# 2. 上位kビットの遷移パターン
# =============================================================================

def analyze_upper_bits(max_n=100000, k_values=[3, 4]):
    """上位kビットの遷移パターンを分析"""
    print("\n" + "=" * 70)
    print("2. 上位kビットの遷移パターン")
    print("=" * 70)

    for k in k_values:
        transition_count = Counter()
        bitlen_changes = Counter()
        total = 0

        for n in range(3, max_n + 1, 2):
            orbit = syracuse_orbit(n, max_steps=500)
            for i in range(len(orbit) - 1):
                val = orbit[i]
                nxt = orbit[i + 1]
                bl_val = val.bit_length()
                bl_nxt = nxt.bit_length()

                if bl_val >= k and bl_nxt >= k:
                    upper_src = val >> (bl_val - k)
                    upper_dst = nxt >> (bl_nxt - k)
                    transition_count[(upper_src, upper_dst)] += 1
                    bitlen_changes[bl_nxt - bl_val] += 1
                    total += 1

        print(f"\n--- 上位 {k} ビット遷移 ---")
        print(f"総遷移数: {total}, ユニーク遷移数: {len(transition_count)}")

        top = transition_count.most_common(15)
        print(f"\nトップ15遷移:")
        print(f"  {'src':>10} {'dst':>10} {'count':>10} {'freq%':>8}")
        for (s, d), c in top:
            print(f"  {bin(s):>10} {bin(d):>10} {c:>10} {c/total*100:>7.3f}%")

        print(f"\nビット長変化の分布:")
        for delta in sorted(bitlen_changes.keys()):
            c = bitlen_changes[delta]
            print(f"  Δ = {delta:+d}: {c:>10} ({c/total*100:.2f}%)")


# =============================================================================
# 3. log2スケール正規化パターン
# =============================================================================

def analyze_log2_patterns(max_n=100000):
    """軌道のlog2スケール正規化パターン"""
    print("\n" + "=" * 70)
    print("3. log2スケール正規化パターン")
    print("=" * 70)

    frac_hist = defaultdict(int)
    bins = 20
    log_diffs = []

    for n in range(3, max_n + 1, 2):
        orbit = syracuse_orbit(n, max_steps=500)
        for val in orbit:
            if val > 1:
                lg = math.log2(val)
                frac = lg - int(lg)
                bucket = int(frac * bins)
                if bucket >= bins:
                    bucket = bins - 1
                frac_hist[bucket] += 1

        for i in range(len(orbit) - 1):
            if orbit[i] > 1 and orbit[i + 1] > 1:
                diff = math.log2(orbit[i + 1]) - math.log2(orbit[i])
                log_diffs.append(diff)

    print(f"\nlog2値の小数部分の分布 ({bins}分割):")
    total = sum(frac_hist.values())
    for b in range(bins):
        c = frac_hist.get(b, 0)
        bar = '#' * int(c / total * 200)
        print(f"  [{b/bins:.2f}, {(b+1)/bins:.2f}): {c/total*100:5.2f}% {bar}")

    print(f"\nlog2差分（ステップ間）の統計:")
    print(f"  平均: {mean(log_diffs):.6f}")
    print(f"  中央値: {median(log_diffs):.6f}")
    print(f"  標準偏差: {stdev(log_diffs):.6f}")
    print(f"  理論平均 (log2(3/4)): {math.log2(3/4):.6f}")
    print(f"  最小: {min(log_diffs):.4f}, 最大: {max(log_diffs):.4f}")

    # 差分のヒストグラム
    lo, hi = min(log_diffs), max(log_diffs)
    nbins = 20
    bw = (hi - lo) / nbins
    hist = [0] * nbins
    for v in log_diffs:
        idx = int((v - lo) / bw)
        if idx >= nbins:
            idx = nbins - 1
        hist[idx] += 1

    print(f"\nlog2差分ヒストグラム:")
    for i in range(nbins):
        edge_l = lo + i * bw
        edge_r = lo + (i + 1) * bw
        bar = '#' * int(hist[i] / len(log_diffs) * 200)
        print(f"  [{edge_l:+.2f}, {edge_r:+.2f}): {hist[i]/len(log_diffs)*100:5.2f}% {bar}")


# =============================================================================
# 4. Carry propagation パターン
# =============================================================================

def compute_carry_chain(n):
    """3n+1 の加算時の最長carry propagation chainを計算"""
    s = 3 * n  # 3n
    # +1のcarry: 3nの下位連続1ビットの数
    if s == 0:
        return 0
    low_ones = 0
    tmp = s
    while tmp & 1:
        low_ones += 1
        tmp >>= 1
    return low_ones

def analyze_carry_propagation(max_n=100000):
    """3n+1 のcarry propagation チェーンの長さ分布を分析"""
    print("\n" + "=" * 70)
    print("4. Carry Propagation パターン (3n+1)")
    print("=" * 70)

    carry_lengths = []
    carry_by_bitlen = defaultdict(list)
    max_carry_examples = []

    for n in range(3, max_n + 1, 2):
        orbit = syracuse_orbit(n, max_steps=500)
        for val in orbit:
            if val == 1:
                continue
            carry_chain = compute_carry_chain(val)
            carry_lengths.append(carry_chain)
            carry_by_bitlen[val.bit_length()].append(carry_chain)

            if carry_chain >= 10:
                max_carry_examples.append((val, carry_chain))

    print(f"\nCarry chain 長さの統計:")
    print(f"  サンプル数: {len(carry_lengths)}")
    print(f"  平均: {mean(carry_lengths):.4f}")
    print(f"  中央値: {median(carry_lengths):.1f}")
    print(f"  最大: {max(carry_lengths)}")
    print(f"  標準偏差: {stdev(carry_lengths):.4f}")

    counter = Counter(carry_lengths)
    print(f"\nCarry chain 長さの分布:")
    for length in sorted(counter.keys()):
        c = counter[length]
        bar = '#' * min(int(c / len(carry_lengths) * 200), 80)
        print(f"  長さ {length:>3}: {c:>10} ({c/len(carry_lengths)*100:6.3f}%) {bar}")

    print(f"\nビット長別の平均carry chain 長さ:")
    for bl in sorted(carry_by_bitlen.keys()):
        vals = carry_by_bitlen[bl]
        if len(vals) >= 100:
            avg = sum(vals) / len(vals)
            print(f"  {bl:>3}ビット: 平均 {avg:.3f} (n={len(vals)})")

    max_carry_examples.sort(key=lambda x: -x[1])
    print(f"\n最長carry chain の例 (トップ10):")
    for val, cl in max_carry_examples[:10]:
        print(f"  n = {val} ({val.bit_length()}ビット), carry chain = {cl}")
        print(f"    bin: {bin(val)}")
        print(f"    3n+1 = {3*val+1}, bin: {bin(3*val+1)}")

    return carry_lengths


# =============================================================================
# 5. v2 と上位ビットの関係
# =============================================================================

def analyze_v2_upper_bits(max_n=100000):
    """v2(3n+1) と nの上位ビットの関係"""
    print("\n" + "=" * 70)
    print("5. v2(3n+1) と上位ビットの関係")
    print("=" * 70)

    v2_by_upper = defaultdict(list)
    v2_by_lower = defaultdict(list)

    for n in range(3, max_n + 1, 2):
        orbit = syracuse_orbit(n, max_steps=500)
        for val in orbit:
            if val == 1:
                continue
            _, v = syracuse(val)
            bl = val.bit_length()
            if bl >= 3:
                upper3 = val >> (bl - 3)
                v2_by_upper[upper3].append(v)
            lower3 = val & 0b111
            v2_by_lower[lower3].append(v)

    print(f"\n上位3ビット別のv2分布:")
    for upper in sorted(v2_by_upper.keys()):
        vals = v2_by_upper[upper]
        avg = sum(vals) / len(vals)
        counter = Counter(vals)
        top3 = counter.most_common(3)
        top3_str = ", ".join(f"v2={v}:{c}" for v, c in top3)
        print(f"  上位{bin(upper):>5}: 平均v2={avg:.3f}, n={len(vals):>8}, 頻出: {top3_str}")

    print(f"\n下位3ビット別のv2分布 (奇数のみ):")
    for lower in sorted(v2_by_lower.keys()):
        if lower % 2 == 0:
            continue
        vals = v2_by_lower[lower]
        avg = sum(vals) / len(vals)
        counter = Counter(vals)
        top5 = counter.most_common(5)
        top5_str = ", ".join(f"v2={v}:{c}" for v, c in top5)
        print(f"  下位{bin(lower):>5}: 平均v2={avg:.3f}, n={len(vals):>8}, 頻出: {top5_str}")

    print(f"\n理論値 (n mod 8 → v2(3n+1)):")
    for r in [1, 3, 5, 7]:
        m = 3 * r + 1
        v = (m & -m).bit_length() - 1
        print(f"  n ≡ {r} (mod 8): 3n+1 ≡ {m} (mod 24), v2 ≥ {v}")


# =============================================================================
# 6. 軌道の「形」のクラスタリング
# =============================================================================

def analyze_orbit_shapes(max_n=50000, n_clusters=8):
    """軌道を正規化してクラスタリング"""
    print("\n" + "=" * 70)
    print("6. 軌道の「形」のクラスタリング")
    print("=" * 70)

    orbits_raw = []
    orbit_ns = []
    for n in range(3, max_n + 1, 2):
        orbit = syracuse_orbit(n, max_steps=500)
        if len(orbit) >= 5:
            orbits_raw.append(orbit)
            orbit_ns.append(n)

    lengths = [len(o) for o in orbits_raw]
    print(f"\n軌道長の分布:")
    print(f"  平均: {mean(lengths):.1f}")
    print(f"  中央値: {median(lengths):.1f}")
    print(f"  最大: {max(lengths)}")
    print(f"  最小: {min(lengths)}")

    # 正規化: log2スケールにして固定長にリサンプル
    target_len = 50
    normalized = []
    for orbit in orbits_raw:
        log_orbit = [math.log2(v) if v > 0 else 0 for v in orbit]
        max_log = max(log_orbit) if log_orbit else 1
        if max_log == 0:
            max_log = 1
        norm = [v / max_log for v in log_orbit]
        indices = linspace(0, len(norm) - 1, target_len)
        resampled = interp(indices, len(norm), norm)
        normalized.append(resampled)

    # k-means
    print(f"\n正規化軌道のクラスタリング (k={n_clusters})...")
    random.seed(42)
    idx = random.sample(range(len(normalized)), n_clusters)
    centroids = [normalized[i][:] for i in idx]

    labels = [0] * len(normalized)
    for iteration in range(30):
        # 割り当て
        changed = False
        for i, vec in enumerate(normalized):
            best_k = 0
            best_d = float('inf')
            for ki in range(n_clusters):
                d = sum((vec[j] - centroids[ki][j]) ** 2 for j in range(target_len))
                if d < best_d:
                    best_d = d
                    best_k = ki
            if labels[i] != best_k:
                changed = True
            labels[i] = best_k

        if not changed:
            print(f"  収束: {iteration+1}回で収束")
            break

        # セントロイド更新
        for ki in range(n_clusters):
            members = [normalized[i] for i in range(len(normalized)) if labels[i] == ki]
            if members:
                centroids[ki] = [sum(m[j] for m in members) / len(members)
                                 for j in range(target_len)]

    # クラスタ統計
    print(f"\nクラスタ別統計:")
    for ki in range(n_clusters):
        members_idx = [i for i in range(len(normalized)) if labels[i] == ki]
        if not members_idx:
            continue
        member_lengths = [lengths[i] for i in members_idx]
        member_ns = [orbit_ns[i] for i in members_idx]
        print(f"\n  クラスタ {ki}: {len(members_idx)} 軌道 ({len(members_idx)/len(normalized)*100:.1f}%)")
        print(f"    軌道長: 平均{mean(member_lengths):.1f}, "
              f"中央値{median(member_lengths):.0f}, "
              f"範囲[{min(member_lengths)}, {max(member_lengths)}]")
        print(f"    初期値の例: {member_ns[:5]}")

        c = centroids[ki]
        peak_pos = c.index(max(c))
        print(f"    ピーク位置: {peak_pos}/{target_len} ({peak_pos/target_len*100:.0f}%)")
        print(f"    ピーク高さ: {c[peak_pos]:.4f}")
        print(f"    最終値: {c[-1]:.4f}")

    return centroids, labels


# =============================================================================
# 7. 頻出ビットサブストリング
# =============================================================================

def analyze_bit_substrings(max_n=50000, substr_lens=[4, 5, 6]):
    """軌道値の2進表現における頻出部分列"""
    print("\n" + "=" * 70)
    print("7. 頻出ビットサブストリング")
    print("=" * 70)

    for slen in substr_lens:
        substr_count = Counter()
        total = 0

        for n in range(3, max_n + 1, 2):
            orbit = syracuse_orbit(n, max_steps=200)
            for val in orbit:
                if val <= 1:
                    continue
                bits = bin(val)[2:]
                for i in range(len(bits) - slen + 1):
                    sub = bits[i:i + slen]
                    substr_count[sub] += 1
                    total += 1

        print(f"\n--- 長さ {slen} のビットサブストリング ---")
        print(f"  総出現: {total}, ユニーク: {len(substr_count)}/{2**slen}")

        top = substr_count.most_common(10)
        bottom = substr_count.most_common()[-5:]
        uniform = total / (2 ** slen)

        print(f"  均一分布期待値: {uniform:.1f}")
        print(f"\n  頻出トップ10:")
        for s, c in top:
            ratio = c / uniform
            print(f"    {s}: {c:>10} (期待値の{ratio:.3f}倍)")

        print(f"\n  希少ボトム5:")
        for s, c in bottom:
            ratio = c / uniform
            print(f"    {s}: {c:>10} (期待値の{ratio:.3f}倍)")


# =============================================================================
# 8. 最小反例の制約（ビット視点）
# =============================================================================

def analyze_minimal_counterexample_bits():
    """最小反例が満たすべきビットパターン制約"""
    print("\n" + "=" * 70)
    print("8. 最小反例の制約（ビットパターン視点）")
    print("=" * 70)

    min_bits = 69  # 検証済み: 2^68

    print(f"\n基本制約:")
    print(f"  最小ビット長: {min_bits}")
    print(f"  最小値: > 2^{min_bits-1} ≈ {2**(min_bits-1):.2e}")

    print(f"\n下位ビット制約 (最小反例 n の場合):")
    print(f"  n は奇数 → 最下位ビット = 1")

    print(f"  最小反例の軌道上の最小値は反例自身")
    print(f"  Syracuse(n) >= n が必要 (最初のステップで下がらない)")
    print(f"  → v2(3n+1) = 1")
    print(f"  → n ≡ 3 (mod 4)")
    print(f"  → 下位2ビット: ...11")

    print(f"\n  n mod 8 別の制約:")
    for r in [3, 7]:
        s1 = (3 * r + 1)
        v1 = (s1 & -s1).bit_length() - 1
        s1_val = s1 >> v1
        print(f"  n ≡ {r} (mod 8):")
        print(f"    Syracuse(n) ≡ (3·{r}+1)/2^{v1} ≡ {s1_val} ... (mod ?)")
        if s1_val % 2 == 1 and s1_val > 1:
            s2_base = 3 * s1_val + 1
            v2_val = (s2_base & -s2_base).bit_length() - 1
            print(f"    Syracuse²(n) involves v2 = {v2_val}")

    print(f"\n  n mod 16 別の2ステップ先制約:")
    for r in range(16):
        if r % 2 == 0 or r % 4 != 3:
            continue
        n_test = r
        s1, v1 = syracuse(n_test) if n_test > 1 else (n_test, 0)
        if s1 > 1:
            s2, v2_val = syracuse(s1)
            total_shrink = v1 + v2_val
            print(f"  n ≡ {r:>2} (mod 16): "
                  f"ステップ1 v2={v1}, ステップ2 v2={v2_val}, "
                  f"合計シフト={total_shrink}, "
                  f"拡大率=9/2^{total_shrink}={9/2**total_shrink:.4f}")

    # 連続kステップの最悪ケース分析
    print(f"\n  連続kステップでの最悪ケース拡大率 (mod 2^k 全探索):")
    for k in range(3, 9):
        mod = 1 << k
        worst_growth = 0
        worst_r = 0
        for r in range(mod):
            if r % 2 == 0 or r < 3:
                continue
            n_test = r + mod * 100  # 十分大きな値
            val = n_test
            growth = 1.0
            steps = 0
            for _ in range(k):
                if val <= 1:
                    break
                nxt, v = syracuse(val)
                growth *= 3.0 / (2 ** v)
                val = nxt
                steps += 1
            if growth > worst_growth and steps == k:
                worst_growth = growth
                worst_r = r
        print(f"  mod 2^{k}: 最悪拡大率 = {worst_growth:.4f} (r={worst_r}), "
              f"{'発散可能' if worst_growth > 1 else '収縮'}")

    print(f"\n  carry propagation の制約:")
    print(f"  反例の軌道が永久に発散するには、3n+1 の carry が頻繁に短い必要がある")
    print(f"  carry chain が短い ↔ ビット表現で連続1が少ない")
    print(f"  しかし3n+1操作は連続1を増やす傾向がある → 矛盾の源泉")


# =============================================================================
# 9. ビット遷移の詳細規則
# =============================================================================

def analyze_bit_transition_rules(max_n=50000):
    """Syracuse適用前後のビット変化の詳細規則"""
    print("\n" + "=" * 70)
    print("9. Syracuse適用前後のビット変化規則")
    print("=" * 70)

    max_bits = 20
    bit_flip_count = [0] * max_bits
    bit_total_count = [0] * max_bits
    bl_v2_count = Counter()

    for n in range(3, max_n + 1, 2):
        orbit, v2s = syracuse_orbit_with_v2(n, max_steps=200)
        for i in range(len(orbit) - 1):
            val = orbit[i]
            nxt = orbit[i + 1]
            bl = min(max(val.bit_length(), nxt.bit_length()), max_bits)

            for b in range(bl):
                bit_val = (val >> b) & 1
                bit_nxt = (nxt >> b) & 1
                if b < max_bits:
                    bit_total_count[b] += 1
                    if bit_val != bit_nxt:
                        bit_flip_count[b] += 1

            v2_val = v2s[i] if i < len(v2s) else 0
            bl_change = nxt.bit_length() - val.bit_length()
            bl_v2_count[(bl_change, v2_val)] += 1

    print(f"\nビット位置別の反転確率:")
    for b in range(max_bits):
        if bit_total_count[b] > 0:
            p = bit_flip_count[b] / bit_total_count[b]
            bar = '#' * int(p * 50)
            print(f"  ビット{b:>2}: {p:.4f} {bar}")

    print(f"\nビット長変化とv2の同時分布 (頻出上位20):")
    total_bv = sum(bl_v2_count.values())
    for (bl_c, v2_val), c in bl_v2_count.most_common(20):
        print(f"  Δbit_len={bl_c:+d}, v2={v2_val}: {c:>8} ({c/total_bv*100:.2f}%)")

    # v2 の分布
    v2_counter = Counter()
    for n in range(3, max_n + 1, 2):
        _, v2s = syracuse_orbit_with_v2(n, max_steps=200)
        for v in v2s:
            v2_counter[v] += 1

    total_v2 = sum(v2_counter.values())
    print(f"\nv2(3n+1) の分布:")
    for v in sorted(v2_counter.keys()):
        c = v2_counter[v]
        theoretical = 1 / (2 ** v)
        actual = c / total_v2
        print(f"  v2={v:>2}: {actual*100:6.3f}% (理論: {theoretical*100:.3f}%)")


# =============================================================================
# メイン
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("探索055: コラッツ軌道のビット表現における頻出部分列マイニング")
    print("=" * 70)

    # 1. 下位kビット遷移
    analyze_lower_bits(max_n=50000, k_values=[3, 4, 5])

    # 2. 上位kビット遷移
    analyze_upper_bits(max_n=50000, k_values=[3, 4])

    # 3. log2スケールパターン
    analyze_log2_patterns(max_n=50000)

    # 4. Carry propagation
    carry_data = analyze_carry_propagation(max_n=50000)

    # 5. v2と上位ビット
    analyze_v2_upper_bits(max_n=50000)

    # 6. 軌道のクラスタリング
    centroids, labels = analyze_orbit_shapes(max_n=30000, n_clusters=8)

    # 7. ビットサブストリング
    analyze_bit_substrings(max_n=30000, substr_lens=[4, 5, 6])

    # 8. 最小反例制約
    analyze_minimal_counterexample_bits()

    # 9. ビット遷移規則
    analyze_bit_transition_rules(max_n=30000)

    print("\n" + "=" * 70)
    print("探索055完了")
    print("=" * 70)
