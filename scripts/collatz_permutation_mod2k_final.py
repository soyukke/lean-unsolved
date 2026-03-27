"""
Syracuse写像の mod 2^k 上の置換構造 - 最終まとめ

核心発見:
1. T(n) は mod 2^k 上で well-defined でない（v2(3n+1) が確定しないため）
2. v2(3n+1) で層別すると、各層は全単射写像を誘導する
3. v2=j 層: 2^{k-1-j} 個の入力残基 → 奇数 mod 2^{k-j} への全単射
4. 情報損失: 1ステップあたり平均2 bits
5. T_1^j(n) = (3/2)^j (n+1) - 1 のアフィン公式
"""

from collections import Counter
from math import gcd

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

def perm_sign(cycles):
    sign = 1
    for c in cycles:
        if len(c) % 2 == 0:
            sign *= -1
    return sign

def perm_order(cycles):
    lengths = [len(c) for c in cycles]
    if not lengths:
        return 1
    result = lengths[0]
    for l in lengths[1:]:
        result = result * l // gcd(result, l)
    return result

# ============================================================
print("=" * 70)
print("Syracuse写像の mod 2^k 層別全単射構造 - 完全分析")
print("=" * 70)

# ============================================================
# A. v2 層ごとの全単射性の検証
# ============================================================
print("\nA. v2 層ごとの全単射性 (k=3..13)")
print("-" * 50)

all_bijective = True
for k in range(3, 14):
    mod = 2**k
    odds = [i for i in range(1, mod, 2)]

    for j in range(1, k):
        layer = [r for r in odds if v2(3*r+1) == j]
        if not layer:
            continue

        target_mod = 2**(k-j)

        # well-definedness と全単射性チェック
        mapping = {}
        well_def = True
        for r in layer:
            vals = set()
            for m in range(30):
                n = r + m * mod
                if n > 0:
                    vals.add(syracuse(n) % target_mod)
            if len(vals) > 1:
                well_def = False
                break
            mapping[r] = vals.pop()

        if not well_def:
            print(f"  k={k}, v2={j}: NOT well-defined!")
            all_bijective = False
            continue

        image = set(mapping.values())
        target_odds = set(i for i in range(1, target_mod, 2))
        is_bij = (image == target_odds) and (len(image) == len(layer))

        if not is_bij:
            print(f"  k={k}, v2={j}: NOT bijective (|layer|={len(layer)}, |target|={len(target_odds)}, |image|={len(image)})")
            all_bijective = False

if all_bijective:
    print("  全 k, 全 v2 層で BIJECTIVE であることを確認 ✓")

# ============================================================
# B. v2=1 層の置換構造（最大の層）
# ============================================================
print("\nB. v2=1 層の置換構造 (入力: n≡3 mod 4, T(n)=(3n+1)/2)")
print("-" * 50)
print("  v2=1 層は mod 2^k の奇数 2^{k-2} 個から")
print("  奇数 mod 2^{k-1} (= 2^{k-2} 個) への全単射")
print()

# v2=1 の残基は n ≡ 3 (mod 4) のもの
# これらは mod 2^{k-1} で見ると奇数全体を被覆する

# 実際に v2=1 層の置換を計算
for k in range(3, 12):
    mod = 2**k
    odds = [i for i in range(1, mod, 2)]
    j = 1
    layer = [r for r in odds if v2(3*r+1) == j]
    target_mod = 2**(k-1)
    target_odds = sorted(i for i in range(1, target_mod, 2))

    # layer → target_odds への写像
    mapping = {r: syracuse(r) % target_mod for r in layer}

    # layer の要素を target_mod で縮約
    # layer の各要素 r について r mod target_mod が何か
    layer_reduced = {}
    for r in layer:
        rm = r % target_mod
        layer_reduced[rm] = mapping[r]

    # layer_reduced が target_odds 上の置換になっているか？
    if set(layer_reduced.keys()) == set(target_odds):
        perm = layer_reduced
        cycles = cycle_decomposition(perm)
        ct = Counter(len(c) for c in cycles)
        order = perm_order(cycles)
        sign = perm_sign(cycles)
        print(f"  k={k}: 置換 on {len(target_odds)} odds mod {target_mod}")
        print(f"    巡回数={len(cycles)}, 不動点={ct.get(1,0)}, 位数={order}, 符号={'偶' if sign==1 else '奇'}")
        print(f"    巡回長: {dict(sorted(ct.items()))}")
        if k <= 5:
            for c in cycles:
                print(f"    巡回: {c}")
    else:
        # layer mod target_mod が target_odds と一致しない場合
        # n ≡ 3 (mod 4) の中で mod target_mod = mod 2^{k-1}
        # 3 mod 4 の奇数を 2^{k-1} で見ると: ≡ 3 mod 4 のもの
        layer_mod_set = set(r % target_mod for r in layer)
        print(f"  k={k}: layer mod {target_mod} = {len(layer_mod_set)} distinct, target_odds = {len(target_odds)}")
        print(f"    layer_mod ⊂ target_odds: {layer_mod_set <= set(target_odds)}")

        # v2=1 層の像と v2=2 層の像を合わせて分析
        # v2=2 の残基
        layer2 = [r for r in odds if v2(3*r+1) == 2]
        mapping2 = {r: syracuse(r) % (target_mod // 2) for r in layer2}
        print(f"    v2=2 層: {len(layer2)} residues → odds mod {target_mod//2}")

# ============================================================
# C. 全層を統合した「階段的全単射」構造
# ============================================================
print("\nC. 階段的全単射構造")
print("-" * 50)
print("""
  Syracuse写像 T は「階段的全単射」を構成する:

  奇数 mod 2^k = Union_{j=1}^{k-1} Layer(j) ∪ Layer(≥k)

  Layer(j) の要素数 = 2^{k-1-j}  (j=1,...,k-2)
  Layer(k-1) の要素数 = 1
  Layer(≥k) の要素数 = 1

  T|_{Layer(j)} : Layer(j) → 奇数 mod 2^{k-j} は全単射

  これは k bits → (k-j) bits への「階段的情報損失」を意味する。
  各層での情報損失量 j は確定的（入力 mod 2^k で決まる）。

  平均情報損失:
  E[j] = Σ j · |Layer(j)| / 2^{k-1}
       = Σ_{j=1}^{k-2} j · 2^{k-1-j} / 2^{k-1} + (k-1)·1/2^{k-1} + ...
       ≈ Σ j / 2^j ≈ 2
""")

# 平均情報損失の正確な計算
for k in range(3, 16):
    total = 2**(k-1)
    avg = 0
    for j in range(1, k-1):
        count = 2**(k-1-j)
        avg += j * count
    avg += (k-1) * 1  # Layer(k-1)
    # Layer(>=k) は v2 >= k で、j の平均は k + 何か... 近似的に k
    avg += k * 1  # 近似
    avg /= total
    print(f"  k={k}: E[v2] ≈ {avg:.6f}")

print(f"\n  極限: E[v2] = 2 (k→∞)")

# ============================================================
# D. 3x+1 の mod 2^k 乗法的構造
# ============================================================
print("\nD. 3n+1 写像の乗法的構造")
print("-" * 50)

# 3n+1 mod 2^k は (n mod 2^k) のアフィン関数
# f(n) = 3n + 1 mod 2^k
# これは Z/2^k Z 上のアフィン写像

for k in range(3, 10):
    mod = 2**k
    odds = [i for i in range(1, mod, 2)]

    # f(n) = 3n + 1 mod 2^k (奇数 → 偶数)
    # v2(f(n)) は n mod 2^k で決定される
    # g(n) = f(n) / 2^{v2(f(n))} mod 2^{k - v2(f(n))}

    # 「3n+1 写像の全体像」:
    # 奇数 n → 偶数 3n+1 → 奇数 T(n) = (3n+1)/2^j

    # 3 の 2-adic における特殊性:
    # 3 は Z_2^× の元、|3|_2 = 1
    # 3^{ord} ≡ 1 (mod 2^k) となる ord は？

    ord3 = 1
    val = 3
    while val % mod != 1:
        val = (val * 3) % mod
        ord3 += 1
        if ord3 > mod:
            ord3 = -1
            break

    print(f"  k={k}: ord(3) mod {mod} = {ord3}")
    # 3 は mod 2^k で位数 2^{k-2} (k >= 3)
    expected = 2**(k-2)
    if ord3 == expected:
        print(f"    = 2^{k-2} ✓ (理論通り)")

# ============================================================
# E. 核心定理: なぜ各層で全単射か？
# ============================================================
print("\nE. 各層での全単射性の代数的証明")
print("-" * 50)
print("""
  定理: v2(3n+1) = j の層上で、T(n) mod 2^{k-j} は n mod 2^k の全単射

  証明のスケッチ:
  n ≡ r (mod 2^k) で v2(3r+1) = j とする。
  3n+1 = 3r+1 + 3(n-r) = 3r+1 + 3·m·2^k (m = (n-r)/2^k)
  v2(3r+1) = j より 3r+1 = 2^j · q (q は奇数)
  3n+1 = 2^j · q + 3·m·2^k = 2^j(q + 3·m·2^{k-j})

  v2(3n+1) >= j は保証される。
  さらに v2(3n+1) = j ⟺ q + 3·m·2^{k-j} が奇数 ⟺ q は奇数（常に成立）
  ...ただし k-j > 0 のとき 3·m·2^{k-j} は偶数なので q + (偶数) の奇偶は q と同じ。
  q は奇数なので v2(3n+1) = j が確定する（j < k のとき）。

  ★ 重要: v2(3n+1) = j が n mod 2^k で確定する（j < k の場合）!
  これは v2 の不確定性が j >= k のときのみ発生することを意味する。

  T(n) = (3n+1)/2^j = q + 3·m·2^{k-j}
  T(n) mod 2^{k-j} = q mod 2^{k-j} = (3r+1)/2^j mod 2^{k-j}
  これは r のみに依存 → well-defined。

  単射性: r ≠ r' (mod 2^k) で v2(3r+1) = v2(3r'+1) = j のとき
  T(r) mod 2^{k-j} = (3r+1)/2^j mod 2^{k-j}
  T(r') mod 2^{k-j} = (3r'+1)/2^j mod 2^{k-j}
  これらが等しい ⟺ 3(r-r') ≡ 0 (mod 2^k)
  ⟺ r ≡ r' (mod 2^k) (3 と 2^k は互いに素)
  → 単射 ✓

  |Layer(j)| = |奇数 mod 2^{k-j}| = 2^{k-j-1} ...
  実際 |Layer(j)| = 2^{k-1-j} = 2^{k-j-1} = |奇数 mod 2^{k-j}| ✓
  → 単射 + |domain| = |codomain| → 全単射 ✓
""")

# ============================================================
# F. v2=1 層の具体的な置換公式
# ============================================================
print("F. v2=1 層の置換の明示公式")
print("-" * 50)

# v2=1 層: n ≡ 3 (mod 4)
# T(n) = (3n+1)/2
# mod 2^{k-1} 上の写像

# n mod 2^k の中で n ≡ 3 (mod 4) のもの
# これらは {3, 7, 11, ..., 2^k - 1} (mod 4 == 3)

# T(n) = (3n+1)/2 mod 2^{k-1}
# = (3·(4m+3)+1)/2 = (12m+10)/2 = 6m+5
# n = 4m+3 → T(n) = 6m+5

# mod 2^{k-1}: T(4m+3) ≡ 6m+5 (mod 2^{k-1})
# m は 0 ≤ m < 2^{k-2} の範囲

# m → 6m+5 mod 2^{k-1} のアフィン写像
# これは Z/2^{k-2}Z → Z/2^{k-1}Z ではなく
# 奇数 mod 2^{k-1} 上の置換

# n ≡ 3 mod 4: n mod 2^{k-1} の取りうる値
# k=4: mod 8, n ∈ {3,7,11,15} mod 16 → mod 8: {3,7,3,7} → 重複!
# だから「v2=1 層の残基 mod target_mod」が target_odds と一致しなかった

print("  v2=1 層の残基と target_mod での像:")
for k in range(3, 8):
    mod = 2**k
    target_mod = 2**(k-1)
    layer = [r for r in range(1, mod, 2) if v2(3*r+1) == 1]
    print(f"\n  k={k} (mod {mod}):")
    print(f"    v2=1 残基: {layer}")
    print(f"    残基 mod {target_mod}: {[r % target_mod for r in layer]}")
    print(f"    T(r) mod {target_mod}: {[syracuse(r) % target_mod for r in layer]}")

    # 写像の全体像
    for r in layer:
        t = syracuse(r)
        print(f"      T({r}) = {t} ≡ {t % target_mod} (mod {target_mod})")

# ============================================================
# G. まとめ: 遷移行列としての構造
# ============================================================
print("\n\nG. 遷移確率行列の構造")
print("-" * 50)

for k in [3, 4, 5]:
    mod = 2**k
    odds = sorted(i for i in range(1, mod, 2))
    n_odds = len(odds)
    idx = {v: i for i, v in enumerate(odds)}

    print(f"\n  k={k} (mod {mod}), {n_odds} states:")

    # 遷移行列: P[i][j] = Prob(T(n) ≡ odds[j] | n ≡ odds[i])
    # 各 src の compatible targets を使って計算
    matrix = [[0]*n_odds for _ in range(n_odds)]

    for src in odds:
        j_val = v2(3*src + 1)
        t_val = syracuse(src)
        target_mod_val = 2**(k - min(j_val, k))
        if target_mod_val <= 0:
            target_mod_val = 1

        t_mod = t_val % target_mod_val if target_mod_val > 1 else 0

        # compatible = odds that match t_mod mod target_mod_val
        compatible = [d for d in odds if (target_mod_val == 1) or (d % target_mod_val == t_mod)]
        prob = 1.0 / len(compatible) if compatible else 0

        si = idx[src]
        for d in compatible:
            di = idx[d]
            matrix[si][di] = prob

    # 表示
    header = "      " + "".join(f"{o:>6}" for o in odds)
    print(header)
    for i, src in enumerate(odds):
        row = f"  {src:>3} " + "".join(f"{matrix[i][j]:>6.3f}" for j in range(n_odds))
        print(row)

    # 定常分布の近似（べき乗法）
    import copy
    vec = [1.0/n_odds] * n_odds
    for _ in range(100):
        new_vec = [0.0] * n_odds
        for j_idx in range(n_odds):
            for i_idx in range(n_odds):
                new_vec[j_idx] += vec[i_idx] * matrix[i_idx][j_idx]
        vec = new_vec

    print(f"  定常分布: {['%.4f' % v for v in vec]}")
    print(f"  一様分布: {1/n_odds:.4f}")
    is_uniform = all(abs(v - 1/n_odds) < 0.01 for v in vec)
    print(f"  一様に収束: {'YES ✓' if is_uniform else 'NO'}")
