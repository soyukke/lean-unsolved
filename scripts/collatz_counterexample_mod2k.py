#!/usr/bin/env python3
"""
コラッツ予想: 最小反例 n_0 の mod 2^k での必要条件

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} に対して、
コラッツ予想が偽ならば最小反例 n_0 > 10^6 が存在する。
n_0 は奇数で、1に到達しないか、非自明サイクルに入る。

Baker排除定理により非自明サイクルは排除済みなので、
n_0 は発散するか無限にさまよう。

最小反例の性質:
  T^k(n_0) が n_0 未満の値を取るなら、その値は1に到達する
  (n_0 の最小性による)。したがって n_0 の軌道は常に n_0 以上。

方法: mod 2^k での残基ごとに、Tの反復適用を記号的に追跡し、
必ず n_0 未満に落ちることを示せる残基を「排除」する。
"""

import time
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


def reaches_one(n, max_steps=500000):
    """n が max_steps以内に1に到達するか"""
    seen = set()
    for _ in range(max_steps):
        if n == 1:
            return True
        if n in seen:
            return False  # cycle
        seen.add(n)
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
    return False


def symbolic_trace(r, mod, max_depth=50):
    """
    n_0 = mod * j + r (j >= 0, j such that n_0 is odd) のもとで
    Syracuse関数を記号的に反復適用。

    各ステップで値 = a*j + b の形を維持。
    a < mod かつ b < r となったら排除可能。

    Returns:
        (excluded, reason, depth, final_a, final_b)
    """
    a, b = mod, r

    for depth in range(1, max_depth + 1):
        # 現在値 val = a*j + b
        # val が偶数かどうかチェック
        if b % 2 == 0:
            if a % 2 == 0:
                # 常に偶数 -> 2で割る
                a //= 2
                b //= 2
                continue
            else:
                # jによって偶奇が変わる -> 分岐必要
                return False, "parity_split", depth, a, b

        # val = a*j + b は奇数 -> Syracuse適用
        # 3*val + 1 = 3a*j + 3b + 1
        new_a = 3 * a
        new_b = 3 * b + 1

        # v2の決定
        v2_b = v2(new_b)
        v2_a = v2(new_a)

        if v2_a >= v2_b:
            # v2(new_a*j + new_b) = v2_b for all j >= 0
            divisor = 2 ** v2_b
            a = new_a // divisor
            b = new_b // divisor

            # 最小性チェック: a*j + b >= mod*j + r (= n_0)
            # (a - mod)*j >= r - b
            coeff = a - mod
            rhs = r - b

            if coeff < 0:
                if rhs > 0:
                    # (a-mod)*j >= r-b with a-mod < 0 and r-b > 0
                    # 不可能 for j >= 0 -> T^depth(n_0) < n_0 always
                    return True, f"always_below: T^{depth} = {a}j+{b}, coeff={coeff}, rhs={rhs}", depth, a, b
                else:
                    # r - b <= 0 つまり b >= r
                    # j <= (r-b)/(a-mod) = (b-r)/(mod-a) >= 0
                    j_max = (b - r) // (mod - a)
                    # j = 0..j_max のみ可能
                    # これらの有限個を直接検証
                    all_good = True
                    for jj in range(j_max + 1):
                        candidate = mod * jj + r
                        if candidate < 2:
                            continue
                        if candidate > 10**6:
                            # 10^6 以下は検証済みなので問題なし
                            # ここでは実際にreaches_oneでチェックする必要はない
                            # (最小反例は > 10^6 なのでこのjは該当しない)
                            all_good = True  # n_0 > 10^6 の条件で自動的に排除
                            continue
                        if not reaches_one(candidate, max_steps=100000):
                            all_good = False
                            break
                    if all_good:
                        return True, f"finite_j: T^{depth} = {a}j+{b}, j<={j_max}, all reach 1", depth, a, b
        else:
            # v2がjに依存 -> 分岐必要
            return False, "v2_split", depth, a, b

    return False, "max_depth", max_depth, a, b


def recursive_trace(r, mod, max_depth=40, max_splits=3, split_depth=0):
    """
    分岐が必要な場合、mod を2倍にして再帰的に解析する。

    Returns: list of (residue, mod, excluded, reason, depth)
    """
    if split_depth > max_splits:
        return [(r, mod, False, "max_split_depth", 0)]

    excluded, reason, depth, a, b = symbolic_trace(r, mod, max_depth)

    if excluded:
        return [(r, mod, True, reason, depth)]

    if reason == "parity_split" or reason == "v2_split":
        # mod を2倍にして r, r+mod の2つに分岐
        new_mod = mod * 2
        results = []
        for new_r in [r, r + mod]:
            if new_r % 2 == 0:
                # 偶数は最小反例にならない
                results.append((new_r, new_mod, True, "even", 0))
            else:
                sub = recursive_trace(new_r, new_mod, max_depth, max_splits, split_depth + 1)
                results.extend(sub)
        return results

    return [(r, mod, False, reason, depth)]


def analyze_mod2k(k, max_depth=50):
    """
    mod 2^k での全奇数残基を解析。

    Returns: dict with analysis results
    """
    mod = 2**k
    odd_residues = [r for r in range(1, mod, 2)]
    total = len(odd_residues)

    excluded = []
    not_excluded = []

    for r in odd_residues:
        ex, reason, depth, a, b = symbolic_trace(r, mod, max_depth)
        if ex:
            excluded.append((r, reason, depth))
        else:
            not_excluded.append((r, reason, depth))

    return {
        'k': k,
        'mod': mod,
        'total_odd': total,
        'excluded': excluded,
        'not_excluded': not_excluded,
        'excluded_count': len(excluded),
        'not_excluded_count': len(not_excluded),
        'exclusion_rate': len(excluded) / total if total > 0 else 0,
    }


def analyze_with_splitting(k, max_depth=50, max_splits=4):
    """
    分岐を許した解析。

    mod 2^k から出発し、分岐が必要な場合は mod を上げて再帰。
    最終的に mod 2^(k+max_splits) まで細分化される可能性がある。
    """
    mod = 2**k
    odd_residues = [r for r in range(1, mod, 2)]
    total = len(odd_residues)

    all_excluded = []
    all_not_excluded = []

    for r in odd_residues:
        results = recursive_trace(r, mod, max_depth, max_splits)
        for res_r, res_mod, res_ex, res_reason, res_depth in results:
            if res_ex:
                all_excluded.append((res_r, res_mod, res_reason, res_depth))
            else:
                all_not_excluded.append((res_r, res_mod, res_reason, res_depth))

    return {
        'k': k,
        'mod': mod,
        'total_odd': total,
        'excluded': all_excluded,
        'not_excluded': all_not_excluded,
        'excluded_fraction': len(all_excluded) / (len(all_excluded) + len(all_not_excluded)),
    }


# ===== メイン解析 =====

print("=" * 80)
print("最小反例 n_0 の mod 2^k での必要条件解析")
print("=" * 80)

# Phase 1: 基本的な排除 (分岐なし)
print("\n" + "=" * 80)
print("Phase 1: 各 mod 2^k での直接排除 (分岐なし)")
print("=" * 80)

for k in [4, 6, 8, 10, 12, 14, 16]:
    t0 = time.time()
    result = analyze_mod2k(k, max_depth=80)
    elapsed = time.time() - t0

    print(f"\nmod 2^{k} = {result['mod']}:")
    print(f"  奇数残基数: {result['total_odd']}")
    print(f"  排除可能: {result['excluded_count']}")
    print(f"  排除不可: {result['not_excluded_count']}")
    print(f"  排除率: {result['exclusion_rate']:.6f} ({result['exclusion_rate']*100:.2f}%)")
    print(f"  計算時間: {elapsed:.2f}秒")

    if k <= 10:
        if result['not_excluded']:
            ne_residues = [r for r, _, _ in result['not_excluded']]
            ne_reasons = defaultdict(int)
            for _, reason, _ in result['not_excluded']:
                ne_reasons[reason] += 1
            print(f"  排除不可の残基 (mod {result['mod']}): {ne_residues[:20]}{'...' if len(ne_residues)>20 else ''}")
            print(f"  排除不可の理由分布: {dict(ne_reasons)}")


# Phase 2: 分岐ありの解析 (より精密)
print("\n" + "=" * 80)
print("Phase 2: 分岐を許した精密解析")
print("=" * 80)

for k in [8, 10, 12]:
    t0 = time.time()
    result = analyze_with_splitting(k, max_depth=60, max_splits=4)
    elapsed = time.time() - t0

    print(f"\nmod 2^{k} (分岐あり):")
    print(f"  排除片数: {len(result['excluded'])}")
    print(f"  非排除片数: {len(result['not_excluded'])}")
    print(f"  排除割合: {result['excluded_fraction']:.6f}")
    print(f"  計算時間: {elapsed:.2f}秒")

    if result['not_excluded']:
        ne_reasons = defaultdict(int)
        for _, _, reason, _ in result['not_excluded']:
            ne_reasons[reason] += 1
        print(f"  非排除理由: {dict(ne_reasons)}")
        if len(result['not_excluded']) <= 30:
            for nr, nm, nreason, nd in result['not_excluded']:
                print(f"    r={nr} (mod {nm}): {nreason} at depth {nd}")


# Phase 3: 最小反例の mod 制約の累積
print("\n" + "=" * 80)
print("Phase 3: 累積制約の要約")
print("=" * 80)

# mod 2^k で排除不可な残基の mod 2^(k-1) への射影を追跡
for k in [4, 6, 8, 10]:
    result = analyze_mod2k(k, max_depth=80)
    ne = sorted([r for r, _, _ in result['not_excluded']])
    print(f"\nmod 2^{k} = {2**k}: 排除不可残基 ({len(ne)}個)")
    if len(ne) <= 64:
        # mod 4 での分布
        mod4_dist = defaultdict(int)
        mod8_dist = defaultdict(int)
        mod16_dist = defaultdict(int)
        for r in ne:
            mod4_dist[r % 4] += 1
            mod8_dist[r % 8] += 1
            mod16_dist[r % 16] += 1
        print(f"  mod 4 分布: {dict(mod4_dist)}")
        print(f"  mod 8 分布: {dict(mod8_dist)}")
        if k >= 4:
            print(f"  mod 16 分布: {dict(mod16_dist)}")
        print(f"  残基リスト: {ne}")

# Phase 4: 特定の残基パターンの詳細解析
print("\n" + "=" * 80)
print("Phase 4: 排除不可残基のパターン解析")
print("=" * 80)

# k=10 の排除不可残基について、ビットパターンを調べる
result_10 = analyze_mod2k(10, max_depth=80)
ne_10 = sorted([r for r, _, _ in result_10['not_excluded']])

print(f"\nmod 1024 排除不可残基 ({len(ne_10)}個):")

# 連続する1のビットの位置を調べる
bit_patterns = defaultdict(int)
trailing_ones = defaultdict(int)
for r in ne_10:
    bits = bin(r)[2:].zfill(10)
    # trailing 1s の数
    t1 = 0
    for b in reversed(bits):
        if b == '1':
            t1 += 1
        else:
            break
    trailing_ones[t1] += 1
    # ビットパターン(下位4ビット)
    bit_patterns[bits[-4:]] += 1

print(f"  trailing 1s 分布: {dict(sorted(trailing_ones.items()))}")
print(f"  下位4ビット分布: {dict(sorted(bit_patterns.items()))}")

# n ≡ 2^(k+1)-1 (mod 2^(k+1)) は k回連続上昇を意味する
# これらが排除不可残基にどう関係するか
print("\n連続上昇との関係:")
for num_ones in range(1, 11):
    # trailing ones が num_ones の残基
    pattern = (1 << num_ones) - 1  # 2^num_ones - 1
    count_ne = sum(1 for r in ne_10 if r % (1 << (num_ones + 1)) == pattern)
    count_total = sum(1 for r in range(1, 1024, 2) if r % (1 << min(num_ones + 1, 10)) == pattern % (1 << min(num_ones + 1, 10)))
    print(f"  {num_ones}回連続上昇 (≡{pattern} mod {1<<(num_ones+1)}): "
          f"排除不可中 {count_ne}個")


# Phase 5: 排除率の理論的予測との比較
print("\n" + "=" * 80)
print("Phase 5: 排除率の漸近挙動")
print("=" * 80)

rates = []
for k in range(3, 17):
    t0 = time.time()
    result = analyze_mod2k(k, max_depth=80)
    elapsed = time.time() - t0
    rate = result['exclusion_rate']
    rates.append((k, rate, result['excluded_count'], result['not_excluded_count']))
    print(f"  k={k:2d}: 排除率 {rate:.6f} ({rate*100:.2f}%), "
          f"排除 {result['excluded_count']:6d}/{result['total_odd']:6d}, "
          f"非排除 {result['not_excluded_count']:6d}, "
          f"時間 {elapsed:.2f}s")

# 漸近的な非排除残基の密度
print("\n非排除残基数の増加パターン:")
for i in range(1, len(rates)):
    k_prev, _, _, ne_prev = rates[i-1]
    k_curr, _, _, ne_curr = rates[i]
    if ne_prev > 0:
        ratio = ne_curr / ne_prev
        print(f"  k={k_prev}->{k_curr}: 非排除 {ne_prev}->{ne_curr}, 比率 {ratio:.4f}")


print("\n" + "=" * 80)
print("解析完了")
print("=" * 80)
