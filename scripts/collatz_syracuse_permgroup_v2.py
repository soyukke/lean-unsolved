"""
Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の mod 2^k 上の構造分析 (v2)

T は mod 2^k 上では全単射ではない。
以下の3つのアプローチで置換群的構造を探る:

A. v2層別: v2(3n+1)=j の層上での置換 (奇数 mod 2^k → 奇数 mod 2^{k-j})
   - v2=1層に限定すれば T_1(n) = (3n+1)/2 で mod 2^{k-1} 上の置換になるか?

B. 修正Syracuse写像: T'(n) = (3n+1)/2 mod 2^k (偶数も含む)
   - 「2で1回だけ割る」写像は well-defined かつ奇→偶の写像

C. 像の比率パターン: |Image(T mod 2^k)| / 2^{k-1} の k→inf での挙動
   - 既知の閉公式との整合性

D. T を v2=1 に制限した置換群の構造
"""

from math import gcd, log2
from collections import Counter
import json
import time

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
    while val % 2 == 0:
        val //= 2
    return val

def factorize(n):
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def format_factorization(n):
    facs = factorize(n)
    if not facs:
        return str(n)
    return " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facs.items()))

def cycle_decomposition(perm):
    visited = set()
    cycles = []
    for start in sorted(perm.keys()):
        if start in visited:
            continue
        cycle = []
        current = start
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = perm[current]
        if cycle:
            cycles.append(tuple(cycle))
    return cycles

def perm_order(cycles):
    lengths = [len(c) for c in cycles]
    if not lengths:
        return 1
    result = lengths[0]
    for l in lengths[1:]:
        result = result * l // gcd(result, l)
    return result

def perm_sign(cycles):
    sign = 1
    for c in cycles:
        if len(c) % 2 == 0:
            sign *= -1
    return sign

# ==========================================================
print("=" * 70)
print("A. v2=1 層に制限した置換構造")
print("   n equiv 1 mod 2 かつ v2(3n+1)=1 の残基上で T_1(n) = (3n+1)/2")
print("=" * 70)

# v2(3n+1) = 1 の条件: 3n+1 equiv 2 mod 4
#  => 3n equiv 1 mod 4 => n equiv 3 mod 4
# (3*3+1 = 10, v2(10)=1; 3*7+1=22, v2(22)=1)

# 問題: v2=1層の入力は n equiv 3 mod 4 の奇数
# 出力 T_1(n) = (3n+1)/2 は必ずしも 3 mod 4 ではない → 層内で閉じない
# しかし、出力を mod 2^{k-1} の奇数全体への写像として見ることはできる

# アプローチ: n equiv 3 mod 4 の残基 mod 2^k から 奇数 mod 2^{k-1} への写像
print("\nv2=1 層: 入力 n equiv 3 mod 4, 出力 (3n+1)/2 mod 2^{k-1}")
print()

for k in range(3, 15):
    mod = 2**k
    target_mod = 2**(k-1)

    # 入力: n equiv 3 mod 4, n < mod, n odd
    inputs = [n for n in range(3, mod, 4)]
    # 出力: odds mod target_mod
    target_odds = set(range(1, target_mod, 2))

    mapping = {}
    for n in inputs:
        t = (3*n + 1) // 2  # v2=1 なので必ず2で割れる
        t_mod = t % target_mod
        mapping[n] = t_mod

    image = set(mapping.values())
    is_surj = (image == target_odds)
    is_inj = (len(set(mapping.values())) == len(inputs))

    # 入力を target_mod で縮約
    reduced_map = {}
    for n in inputs:
        n_red = n % target_mod
        reduced_map[n_red] = mapping[n]

    # 縮約した入力集合は何か？
    reduced_inputs = set(n % target_mod for n in inputs)

    # reduced_inputs == target_odds かチェック
    # n equiv 3 mod 4 を target_mod = 2^{k-1} で縮約すると:
    # {3, 7, 11, ...} mod 2^{k-1} → 3 mod 4 の奇数 mod 2^{k-1}
    # これは target_odds の半分

    bij = (reduced_inputs == target_odds)

    if k <= 8:
        print(f"  k={k}: |inputs|={len(inputs)}, |target_odds|={len(target_odds)}, "
              f"|image|={len(image)}, surj={is_surj}, inj={is_inj}")
        print(f"    reduced_inputs == target_odds: {bij}")
        print(f"    |reduced_inputs|={len(reduced_inputs)}, |target_odds|={len(target_odds)}")

# ==========================================================
print("\n" + "=" * 70)
print("B. 修正アプローチ: T_1(n)=(3n+1)/2 を 3 mod 4 の残基間の自己写像として解析")
print("   T_1 が 3 mod 4 に戻るか、1 mod 4 に行くかで分岐")
print("=" * 70)

for k in range(3, 12):
    mod = 2**k

    # 3 mod 4 の奇数残基
    res3 = [n for n in range(3, mod, 4)]

    # T_1(n) = (3n+1)/2 の行き先の mod 4 分布
    to_1mod4 = 0
    to_3mod4 = 0
    for n in res3:
        t = (3*n + 1) // 2
        if t % 4 == 1:
            to_1mod4 += 1
        elif t % 4 == 3:
            to_3mod4 += 1

    if k <= 8:
        print(f"  k={k}: |3mod4|={len(res3)}, T_1 → 1mod4: {to_1mod4}, → 3mod4: {to_3mod4}")
        print(f"    ratio to_3mod4 = {to_3mod4/len(res3):.4f}")

# ==========================================================
print("\n" + "=" * 70)
print("C. 加速写像 A(n) = T(T(...T(n)...)) 一回の奇数→奇数ステップの反復")
print("   mod 2^k の奇数上で A^m(n) の到達可能集合サイズ")
print("=" * 70)

for k in range(3, 14):
    mod = 2**k
    odds = list(range(1, mod, 2))
    n_odds = len(odds)

    # T の反復で到達可能な集合
    # 各出発点 n からの軌道を追跡
    # T(n) mod 2^k

    # 全ての奇数から出発した「1ステップ像」
    one_step = set()
    for n in odds:
        one_step.add(syracuse(n) % mod)

    # m ステップ像
    current_image = set(odds)  # 全体から出発
    for m in range(1, 20):
        next_image = set()
        for n in current_image:
            next_image.add(syracuse(n) % mod)
        if next_image == current_image:
            if k <= 10:
                print(f"  k={k}: 像はステップ {m} で安定。|image|={len(current_image)}/{n_odds} "
                      f"= {len(current_image)/n_odds:.4f}")
            break
        current_image = next_image
    else:
        if k <= 10:
            print(f"  k={k}: 20ステップでは安定せず。|image|={len(current_image)}/{n_odds}")

# ==========================================================
print("\n" + "=" * 70)
print("D. 像の比率パターンの詳細分析")
print("   |Image(T mod 2^k)| / 2^{k-1} のkに対する挙動")
print("=" * 70)

image_ratios = []
for k in range(3, 18):
    mod = 2**k
    odds = list(range(1, mod, 2))
    n_odds = len(odds)

    image = set()
    for n in odds:
        image.add(syracuse(n) % mod)

    ratio = len(image) / n_odds
    image_ratios.append((k, len(image), n_odds, ratio))

    # 閉公式との比較
    # k奇 → 3/4, k偶 → 7/12 (既知)
    if k % 2 == 1:
        expected = 3/4
    else:
        expected = 7/12

    print(f"  k={k}: |Image|={len(image)}, n_odds={n_odds}, "
          f"ratio={ratio:.6f}, expected(k{'odd' if k%2==1 else 'even'})={expected:.6f}, "
          f"diff={ratio-expected:.6f}")

# ==========================================================
print("\n" + "=" * 70)
print("E. T の反復 T^m mod 2^k の写像としての像サイズ")
print("   各 m に対して |Image(T^m mod 2^k)| を計算")
print("=" * 70)

for k in [5, 7, 9, 11]:
    mod = 2**k
    odds = list(range(1, mod, 2))
    n_odds = len(odds)
    odd_set = set(odds)

    print(f"\n  k={k}, mod={mod}:")

    # T^m の写像を計算
    current_map = {n: syracuse(n) % mod for n in odds}

    for m in range(1, 25):
        # 現在の写像の像サイズ
        image = set(current_map.values())
        image_odd = image & odd_set

        # 固定点
        fixed = sum(1 for n in odds if current_map.get(n) == n)

        print(f"    T^{m:2d}: |Image|={len(image):>6}, |Image∩Odds|={len(image_odd):>6}, "
              f"固定点={fixed:>4}, ratio={len(image_odd)/n_odds:.4f}")

        # 次のステップ: T^{m+1} = T o T^m
        next_map = {}
        for n in odds:
            val = current_map[n]
            next_map[n] = syracuse(val) % mod
        current_map = next_map

        # 像が安定したか？
        if len(image_odd) == fixed and m >= 3:
            print(f"    ... 全像が固定点。安定。")
            break

# ==========================================================
print("\n" + "=" * 70)
print("F. v2=1 制限写像 T_1(n)=(3n+1)/2 の mod 2^k 上の置換構造")
print("   全奇数上の写像として（v2 >= 2 の場合は T_1 を別途定義）")
print("=" * 70)

# T_1(n) = (3n+1)/2 は全ての奇数 n に対して well-defined
# ただし結果は偶数になりうる
# T_1(1) = 2 (偶数!)
# T_1(3) = 5 (奇数)

# 代替: 全ての奇数に対して g(n) = (3n+1)/2 mod 2^k を計算
# g は奇数→全体（偶奇混合）の写像

# さらに代替: 奇数上の「Collatz map restricted to odds」
# C(n): n → 3n+1 → /2 を繰り返して次の奇数に至る
# これは syracuse(n) と同じ

# 核心: T mod 2^k が全単射にならない理由の定量分析
print("\n衝突の構造分析:")

for k in range(3, 14):
    mod = 2**k
    odds = list(range(1, mod, 2))

    # 写像 T(n) mod 2^k
    fwd = {}
    for n in odds:
        fwd[n] = syracuse(n) % mod

    # 逆像のサイズ分布
    preimage_count = Counter(fwd.values())
    size_dist = Counter(preimage_count.values())

    # 衝突ペアの分析
    # 衝突: fwd[n1] == fwd[n2] for n1 != n2
    # v2(3n1+1) != v2(3n2+1) だが結果が同じ mod 2^k

    collisions = 0
    for val, count in preimage_count.items():
        if count > 1:
            collisions += count * (count - 1) // 2

    n_missing = len(set(odds) - set(fwd.values()))

    print(f"  k={k}: |Image|={len(set(fwd.values()))}, missing={n_missing}, "
          f"collisions={collisions}")
    print(f"    preimage sizes: {dict(sorted(size_dist.items()))}")

    # v2層別の衝突分析
    if k <= 8:
        v2_groups = {}
        for n in odds:
            j = v2(3*n + 1)
            if j not in v2_groups:
                v2_groups[j] = []
            v2_groups[j].append(n)

        for j in sorted(v2_groups.keys()):
            layer = v2_groups[j]
            layer_images = [fwd[n] for n in layer]
            layer_img_set = set(layer_images)
            intra_collision = len(layer) - len(layer_img_set)
            print(f"    v2={j}: |layer|={len(layer)}, |image|={len(layer_img_set)}, "
                  f"intra-collision={intra_collision}")

# ==========================================================
print("\n" + "=" * 70)
print("G. v2=1 層内自己写像の置換構造")
print("   n equiv 3 mod 4 で T_1(n)=(3n+1)/2 が再び 3 mod 4 に戻る場合のみ追跡")
print("=" * 70)

for k in range(3, 15):
    mod = 2**k

    # 3 mod 4 の奇数残基
    domain = [n for n in range(3, mod, 4)]
    domain_set = set(domain)

    # T_1(n) = (3n+1)/2 mod 2^k
    mapping = {}
    stays_in = 0
    leaves = 0
    for n in domain:
        t = ((3*n + 1) // 2) % mod
        mapping[n] = t
        if t in domain_set:
            stays_in += 1
        else:
            leaves += 1

    # domain 内で閉じる部分写像
    restricted = {n: mapping[n] for n in domain if mapping[n] in domain_set}

    # 反復的に到達可能な集合（domain内に留まり続ける部分）
    # 最大不変部分集合を求める
    current = set(domain)
    for iteration in range(50):
        new = set()
        for n in current:
            t = mapping[n]
            if t in current:
                new.add(n)
        if new == current:
            break
        current = new

    invariant = current

    if invariant:
        # invariant 上の置換
        inv_map = {n: mapping[n] for n in invariant}
        if set(inv_map.values()) == invariant:
            cycles = cycle_decomposition(inv_map)
            order = perm_order(cycles)
            sign = perm_sign(cycles)
            n_fixed = sum(1 for c in cycles if len(c) == 1)
            ct = Counter(len(c) for c in cycles)

            print(f"  k={k}: |domain|={len(domain)}, stays_in={stays_in}, "
                  f"|invariant|={len(invariant)}")
            print(f"    置換の位数={order} = {format_factorization(order)}")
            print(f"    符号={'even' if sign==1 else 'odd'}, 巡回数={len(cycles)}, 不動点={n_fixed}")
            if k <= 8:
                print(f"    巡回長: {dict(sorted(ct.items()))}")
                if k <= 6:
                    for c in cycles:
                        print(f"      巡回: {c}")
        else:
            print(f"  k={k}: |invariant|={len(invariant)} だが全単射でない")
    else:
        print(f"  k={k}: 不変部分集合が空")

# ==========================================================
print("\n" + "=" * 70)
print("H. 全奇数上のSyracuse写像 T(n) mod 2^k: 最大不変全単射部分集合")
print("=" * 70)

invariant_orders = []

for k in range(3, 15):
    mod = 2**k
    odds = list(range(1, mod, 2))
    odd_set = set(odds)

    mapping = {n: syracuse(n) % mod for n in odds}

    # 最大不変部分集合: mapping で閉じる最大部分集合
    current = set(odds)
    for iteration in range(100):
        # 像が current 内に入る要素のみ残す
        new = set()
        for n in current:
            if mapping[n] in current:
                new.add(n)
        # さらに、像として到達される要素のみ残す（全射性）
        image_in = set(mapping[n] for n in new)
        new2 = new & image_in

        if new2 == current:
            break
        current = new2

    invariant = current

    if invariant:
        inv_map = {n: mapping[n] for n in invariant}
        image = set(inv_map.values())
        is_bij = (image == invariant)

        if is_bij:
            cycles = cycle_decomposition(inv_map)
            order = perm_order(cycles)
            sign = perm_sign(cycles)
            n_fixed = sum(1 for c in cycles if len(c) == 1)
            ct = Counter(len(c) for c in cycles)

            invariant_orders.append((k, len(invariant), order))

            print(f"  k={k}: |invariant|={len(invariant)}/{len(odds)}, "
                  f"ratio={len(invariant)/len(odds):.4f}")
            print(f"    位数={order} = {format_factorization(order)}")
            print(f"    符号={'even' if sign==1 else 'odd'}, 巡回数={len(cycles)}, 不動点={n_fixed}")
            print(f"    巡回長: {dict(sorted(ct.items()))}")
            if k <= 6:
                for c in cycles:
                    if len(c) <= 20:
                        print(f"      巡回: {c}")
        else:
            print(f"  k={k}: |invariant|={len(invariant)} but not bijective")
    else:
        print(f"  k={k}: 不変部分集合が空")

# 不変集合の位数の成長
print("\n--- 最大不変集合の位数の成長 ---")
if invariant_orders:
    print(f"{'k':>4} {'|invariant|':>12} {'order':>15} {'log2(order)':>12}")
    for k, inv_size, order in invariant_orders:
        l2 = log2(order) if order > 1 else 0
        print(f"{k:>4} {inv_size:>12} {order:>15} {l2:>12.4f}")

    # 成長率
    print("\n--- 位数の成長率 ---")
    for i in range(len(invariant_orders) - 1):
        k1, _, o1 = invariant_orders[i]
        k2, _, o2 = invariant_orders[i+1]
        if o1 > 0:
            ratio = o2 / o1
            print(f"  k={k1}→{k2}: ratio={ratio:.4f} (log2={log2(ratio):.4f})")

# ==========================================================
# JSON保存
# ==========================================================
output = {
    'title': 'Syracuse T mod 2^k permutation group - v2 analysis',
    'image_ratios': [
        {'k': k, 'image_size': img, 'n_odds': n, 'ratio': r}
        for k, img, n, r in image_ratios
    ],
    'invariant_subset_orders': [
        {'k': k, 'invariant_size': s, 'order': o, 'log2_order': log2(o) if o > 1 else 0}
        for k, s, o in invariant_orders
    ]
}

with open('/Users/soyukke/study/lean-unsolved/results/syracuse_permgroup_v2.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n\n結果を results/syracuse_permgroup_v2.json に保存しました。")
