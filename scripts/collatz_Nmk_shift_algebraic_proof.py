"""
N(m,k) = N(m-1,k-2) の代数的証明の構成と検証

=== 定義 ===
Syracuse関数: T(n) = (3n+1) / 2^{v2(3n+1)} ただし n は奇数
mod 2^k 版: T_k(r) = T(r) mod 2^k  (r は奇数, 1 <= r < 2^k)

多重度: mult_k(t) = |{r 奇数 mod 2^k : T_k(r) = t}|
N(m,k) = |{t : mult_k(t) = m}|

=== 証明の戦略 ===

ステップ1: 自然射影 pi: Z/2^{k+2}Z -> Z/2^kZ の持ち上げ解析
  - 各奇数 r mod 2^k は 4つの持ち上げ r, r+2^k, r+2^{k+1}, r+3*2^k mod 2^{k+2}
  - T_{k+2}(lift) mod 2^k = T_k(r) (整合性)
  - 問題: T_{k+2} での多重度分布がどう変化するか

ステップ2: v2層分解
  - v2(3r+1) = j のとき、T(r) = (3r+1)/2^j
  - 持ち上げ r' = r + c*2^k (c=0,1,2,3) で v2(3r'+1) がどう変化するか
  - 3r' + 1 = 3r + 1 + 3c*2^k
  - v2(3r'+1) は v2(3r+1) と v2(3c) の min に依存

ステップ3: 衝突の持ち上げ
  - T_k(r1) = T_k(r2) (mod 2^k での衝突) ⟹ T_{k+2} での衝突はどうなるか
  - 多重度 m の像が多重度 m+1 になる仕組み

=== 実装 ===
"""

from collections import Counter, defaultdict
import itertools

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^{v2(3n+1)}"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def odd_residues(k):
    """奇数残基 mod 2^k"""
    return list(range(1, 2**k, 2))

def compute_Tk(k):
    """T mod 2^k のマップと多重度"""
    mod = 2**k
    fmap = {}
    for r in odd_residues(k):
        fmap[r] = syracuse(r) % mod
    return fmap

def multiplicity_distribution(k):
    """N(m,k) の計算"""
    fmap = compute_Tk(k)
    img_count = Counter(fmap.values())
    mult_dist = Counter(img_count.values())
    return dict(sorted(mult_dist.items()))

# =======================================================
# Part 1: 基本的な事実の確認
# =======================================================
print("=" * 70)
print("Part 1: N(m,k) = N(m-1,k-2) の数値的再確認")
print("=" * 70)

Ndict = {}
for k in range(3, 18):
    md = multiplicity_distribution(k)
    for m, count in md.items():
        Ndict[(m, k)] = count

print("\n再帰関係の検証:")
violations = 0
for k in range(5, 18):
    for m in range(2, 15):
        if (m, k) in Ndict and (m-1, k-2) in Ndict:
            if Ndict[(m, k)] != Ndict[(m-1, k-2)]:
                print(f"  NG: N({m},{k})={Ndict[(m,k)]} != N({m-1},{k-2})={Ndict[(m-1,k-2)]}")
                violations += 1
print(f"  違反: {violations}件 (0なら全成立)")

# =======================================================
# Part 2: 持ち上げのメカニズム分析
# =======================================================
print("\n" + "=" * 70)
print("Part 2: mod 2^k -> mod 2^{k+2} の持ち上げ解析")
print("=" * 70)

def analyze_lifting(k):
    """k -> k+2 の持ち上げで各像の逆像数がどう変化するか"""
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    # mod 2^k の逆像マップ
    fmap_k = compute_Tk(k)
    preimage_k = defaultdict(list)
    for r, t in fmap_k.items():
        preimage_k[t].append(r)

    # mod 2^{k+2} の逆像マップ
    fmap_k2 = compute_Tk(k+2)
    preimage_k2 = defaultdict(list)
    for r, t in fmap_k2.items():
        preimage_k2[t].append(r)

    # 各 t mod 2^k について、持ち上げ t' mod 2^{k+2} (t' ≡ t mod 2^k) の多重度合計
    results = {}
    for t_k, preim_k in preimage_k.items():
        mult_k = len(preim_k)
        # t mod 2^k の持ち上げ: t, t+2^k, t+2^{k+1}, t+3*2^k (奇数のみ)
        lifts_t = []
        for c in range(4):
            t_lift = (t_k + c * mod_k) % mod_k2
            if t_lift % 2 == 1:  # 奇数のみ
                lifts_t.append(t_lift)

        lift_mults = {}
        for t_lift in lifts_t:
            mult_k2 = len(preimage_k2.get(t_lift, []))
            lift_mults[t_lift] = mult_k2

        results[t_k] = {
            'mult_k': mult_k,
            'lifts': lift_mults,
            'total_lifts_mult': sum(lift_mults.values()),
            'preim_k': preim_k
        }

    return results

for k in [5, 6, 7, 8]:
    print(f"\nk={k} -> k+2={k+2}:")
    results = analyze_lifting(k)

    # 多重度別に集計
    by_mult = defaultdict(list)
    for t_k, info in results.items():
        by_mult[info['mult_k']].append(info)

    for mult_k in sorted(by_mult.keys()):
        items = by_mult[mult_k]
        lift_mult_patterns = Counter()
        for info in items:
            pattern = tuple(sorted(info['lifts'].values(), reverse=True))
            lift_mult_patterns[pattern] += 1

        print(f"  多重度 {mult_k} の像 ({len(items)}個):")
        for pattern, count in lift_mult_patterns.most_common():
            print(f"    持ち上げパターン {pattern}: {count}個")

# =======================================================
# Part 3: 代数的メカニズムの解析
# =======================================================
print("\n" + "=" * 70)
print("Part 3: v2層別の持ち上げ解析")
print("=" * 70)

def analyze_v2_layer_lifting(k):
    """v2層ごとの持ち上げの詳細"""
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    # v2層の分類
    layers = defaultdict(list)
    for r in odd_residues(k):
        j = v2(3*r + 1)
        layers[j].append(r)

    print(f"\nk={k}:")
    for j in sorted(layers.keys()):
        rlist = layers[j]
        print(f"  v2層 j={j}: {len(rlist)} elements")

        # 持ち上げの衝突分析
        for r in rlist[:3]:  # 最初の3個だけ
            lifts = [r + c * mod_k for c in range(4)]
            lifts_odd = [l for l in lifts if l % 2 == 1]

            v2_vals = [(l, v2(3*l+1)) for l in lifts_odd]
            T_vals = [(l, syracuse(l) % mod_k2) for l in lifts_odd]

            print(f"    r={r}: lifts_odd={lifts_odd}")
            print(f"      v2: {v2_vals}")
            print(f"      T mod 2^{k+2}: {T_vals}")

for k in [5, 7]:
    analyze_v2_layer_lifting(k)

# =======================================================
# Part 4: 衝突の代数的構造
# =======================================================
print("\n" + "=" * 70)
print("Part 4: 衝突構造の解析 - なぜ N(m,k)=N(m-1,k-2) か")
print("=" * 70)

def analyze_collisions(k):
    """衝突ペアの代数的構造"""
    mod = 2**k
    fmap = compute_Tk(k)

    # 逆像リスト
    preimage = defaultdict(list)
    for r, t in fmap.items():
        preimage[t].append(r)

    # 衝突ペアの差分分析
    collision_data = []
    for t, preim in preimage.items():
        if len(preim) >= 2:
            for i in range(len(preim)):
                for j in range(i+1, len(preim)):
                    r1, r2 = preim[i], preim[j]
                    diff = abs(r1 - r2)
                    v2_diff = v2(diff)
                    j1 = v2(3*r1 + 1)
                    j2 = v2(3*r2 + 1)
                    collision_data.append({
                        'r1': r1, 'r2': r2, 't': t,
                        'diff': diff, 'v2_diff': v2_diff,
                        'v2_layer_r1': j1, 'v2_layer_r2': j2
                    })

    return collision_data

for k in [5, 7, 9]:
    coll = analyze_collisions(k)
    print(f"\nk={k}: 衝突ペア数 = {len(coll)}")

    # v2層ペアの分類
    layer_pairs = Counter()
    v2diff_dist = Counter()
    for c in coll:
        layer_pairs[(c['v2_layer_r1'], c['v2_layer_r2'])] += 1
        v2diff_dist[c['v2_diff']] += 1

    print(f"  v2層ペア分布:")
    for (j1, j2), cnt in sorted(layer_pairs.items()):
        print(f"    (j1={j1}, j2={j2}): {cnt}")

    print(f"  衝突差分の v2 分布:")
    for v, cnt in sorted(v2diff_dist.items()):
        print(f"    v2(diff)={v}: {cnt}")

# =======================================================
# Part 5: 核心的な代数的議論
# =======================================================
print("\n" + "=" * 70)
print("Part 5: 持ち上げと衝突保存の代数的証明")
print("=" * 70)

def prove_shift_law(k_start=5, k_end=14):
    """
    N(m,k) = N(m-1,k-2) の証明の核心:

    定義: pi_k: Z/2^{k+2}Z -> Z/2^kZ を自然射影とする。

    主張: mod 2^{k+2} で多重度 m+1 を持つ像の個数
         = mod 2^k で多重度 m を持つ像の個数 (m >= 1)

    すなわち N(m+1, k+2) = N(m, k) ∀m >= 1
    これは N(m, k) = N(m-1, k-2) と同値。

    鍵となる補題:
    補題: r1 != r2 (奇数 mod 2^k) で T_k(r1) = T_k(r2) = t ならば、
    r1, r2 の 2^{k+2} への各持ち上げ r1', r2' で
    T_{k+2}(r1') = T_{k+2}(r2') となるものが正確に1通り存在する。

    すなわち、mod 2^k の各衝突は mod 2^{k+2} に正確に保存される。
    加えて、mod 2^{k+2} で新規に生じる衝突は、多重度を1だけ増やす。
    """

    for k in range(k_start, min(k_end, 14)):
        mod_k = 2**k
        mod_k2 = 2**(k+2)

        fmap_k = compute_Tk(k)
        fmap_k2 = compute_Tk(k+2)

        # mod 2^k の逆像
        preimage_k = defaultdict(set)
        for r, t in fmap_k.items():
            preimage_k[t].add(r)

        # mod 2^{k+2} の逆像
        preimage_k2 = defaultdict(set)
        for r, t in fmap_k2.items():
            preimage_k2[t].add(r)

        # 各 t mod 2^{k+2} について、pi(t) = t mod 2^k の多重度との関係
        mult_shift_check = Counter()  # (mult_k, mult_k2) -> count

        for t2, preim2 in preimage_k2.items():
            m2 = len(preim2)
            t_red = t2 % mod_k
            m_red = len(preimage_k.get(t_red, set()))
            mult_shift_check[(m_red, m2)] += 1

        # 像でない mod 2^{k+2} の残基
        non_image_k2 = set()
        for r in odd_residues(k+2):
            if r not in set(fmap_k2.values()):
                non_image_k2.add(r)

        print(f"\nk={k} -> k+2={k+2}:")
        print(f"  (mult_k, mult_{k+2}) -> count:")
        for (mk, mk2), cnt in sorted(mult_shift_check.items()):
            print(f"    ({mk}, {mk2}): {cnt}")

        # N(m, k+2) vs N(m-1, k) の直接比較
        md_k = multiplicity_distribution(k)
        md_k2 = multiplicity_distribution(k+2)

        print(f"  N(m,k+2) vs N(m-1,k):")
        all_ok = True
        max_m = max(list(md_k.keys()) + list(md_k2.keys()))
        for m in range(2, max_m + 2):
            n_k2 = md_k2.get(m, 0)
            n_k = md_k.get(m-1, 0)
            status = "OK" if n_k2 == n_k else "NG"
            if n_k2 > 0 or n_k > 0:
                print(f"    N({m},{k+2})={n_k2}, N({m-1},{k})={n_k}: {status}")
            if status == "NG":
                all_ok = False

        if all_ok:
            print(f"  => N(m,{k+2}) = N(m-1,{k}) 全成立!")

prove_shift_law()

# =======================================================
# Part 6: ファイバー上の持ち上げ構造の精密解析
# =======================================================
print("\n" + "=" * 70)
print("Part 6: ファイバー持ち上げの精密構造")
print("=" * 70)

def fiber_analysis(k):
    """
    mod 2^k で多重度 m の像 t について:
    - t の mod 2^{k+2} への持ち上げ t' (奇数) は 2つ存在
    - 各持ち上げ t' の逆像は、t の逆像の持ち上げから来る
    - 衝突の保存と新規衝突の生成を追跡
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    fmap_k = compute_Tk(k)
    fmap_k2 = compute_Tk(k+2)

    preimage_k = defaultdict(list)
    for r, t in fmap_k.items():
        preimage_k[t].append(r)

    preimage_k2 = defaultdict(list)
    for r, t in fmap_k2.items():
        preimage_k2[t].append(r)

    # 各 t mod 2^k の持ち上げ分析
    for mult_target in [1, 2, 3]:
        targets = [t for t, p in preimage_k.items() if len(p) == mult_target]
        if not targets:
            continue

        print(f"\n  k={k}, 多重度 {mult_target} の像 ({len(targets)}個): 持ち上げ先の多重度分布")

        lift_pattern_counter = Counter()
        for t in targets:
            # t の奇数持ち上げ
            lifts_t = []
            for c in range(4):
                tl = (t + c * mod_k) % mod_k2
                if tl % 2 == 1:
                    lifts_t.append(tl)

            mults = tuple(sorted([len(preimage_k2.get(tl, [])) for tl in lifts_t], reverse=True))
            lift_pattern_counter[mults] += 1

        for pattern, count in lift_pattern_counter.most_common():
            print(f"    パターン {pattern}: {count}個")

for k in [5, 6, 7, 8, 9]:
    print(f"\n--- k={k} ---")
    fiber_analysis(k)

# =======================================================
# Part 7: 核心定理の代数的証明の骨格
# =======================================================
print("\n" + "=" * 70)
print("Part 7: 代数的証明の骨格")
print("=" * 70)

def algebraic_proof_skeleton():
    """
    定理: N(m, k+2) = N(m-1, k) for all m >= 2, k >= 3
    (等価的に N(m, k) = N(m-1, k-2))

    証明の骨格:

    1. v2層分解:
       奇数 r mod 2^k を j = v2(3r+1) で分類。
       j=1 の層: r ≡ 1 (mod 4)   → |層| = 2^{k-2}
       j=2 の層: r ≡ 3 (mod 8)   → |層| = 2^{k-3}
       j>=3 の層: r ≡ 2^j - 1 (mod 2^{j+1}) → |層| = 2^{k-j-1}

    2. v2層内全単射 (既知):
       j = v2(3r+1) のとき、写像 r ↦ (3r+1)/2^j mod 2^{k-j} は
       {r 奇数 mod 2^k : v2(3r+1) = j} から {s 奇数 mod 2^{k-j}} への全単射。

    3. 衝突の源泉:
       T_k(r1) = T_k(r2) で r1 ≠ r2 ならば、必ず
       v2(3r1+1) ≠ v2(3r2+1) (異なるv2層からの衝突)。

       具体的に: j1 < j2 のとき、
       (3r1+1)/2^{j1} ≡ (3r2+1)/2^{j2} (mod 2^k)
       ⟺ 2^{j2-j1}(3r1+1) ≡ 3r2+1 (mod 2^{k+j2})
       ... ここで mod 2^k の精度で一致。

    4. k → k+2 の持ち上げ:
       r mod 2^k の 4つの持ち上げ: r, r+2^k, r+2^{k+1}, r+3·2^k
       (うち奇数は r と r+2^{k+1} の2つ if k>=2)

       Wait: 2^k が偶数なので r+2^k は r と同じ奇偶。
       r は奇数なので r+2^k も奇数。同様に r+2^{k+1}, r+3·2^k。
       → 4つ全て奇数!
    """

    # 検証: 4つの持ち上げの奇偶
    for k in [5, 7]:
        mod_k = 2**k
        for r in [1, 3, 5]:
            lifts = [r + c * mod_k for c in range(4)]
            parities = [l % 2 for l in lifts]
            print(f"  k={k}, r={r}: lifts={lifts}, parities={parities}")

    # ただし mod 2^{k+2} の奇数残基は 2^{k+1} 個
    # mod 2^k の奇数残基は 2^{k-1} 個
    # 各残基が 4つ持ち上がるので 4 * 2^{k-1} = 2^{k+1} で一致

    print("\n  各 r mod 2^k は 4つの奇数持ち上げ r+c*2^k (c=0,1,2,3) を持つ")
    print("  4 * 2^{k-1} = 2^{k+1} = (mod 2^{k+2} の奇数残基数)")

    # 核心: v2(3(r + c*2^k) + 1) の計算
    print("\n  v2(3(r + c*2^k) + 1) の解析:")
    print("  3(r + c*2^k) + 1 = (3r+1) + 3c*2^k")
    print("  j = v2(3r+1) とすると:")
    print("  3r+1 = 2^j * q (qは奇数)")
    print("  3c*2^k = 2^k * 3c  (c=0,1,2,3)")
    print("")
    print("  Case 1: j < k のとき (ほとんどの場合)")
    print("    v2(3(r+c*2^k)+1) = v2(2^j*q + 3c*2^k) = j  (j < k)")
    print("    よって v2層は保存される!")
    print("")
    print("  Case 2: j >= k のとき")
    print("    v2(3r+1) >= k  (特殊ケース)")
    print("    3c*2^k のv2はkまたはinf (c=0)")
    print("    この場合 v2 は変化しうる")

    # 数値検証: j < k でv2が保存されるか
    print("\n  数値検証: j < k のとき v2 保存")
    for k in [5, 7, 9]:
        mod_k = 2**k
        all_preserved = True
        exceptions = 0
        for r in odd_residues(k):
            j = v2(3*r + 1)
            for c in range(1, 4):
                r_lift = r + c * mod_k
                j_lift = v2(3*r_lift + 1)
                if j < k and j_lift != j:
                    all_preserved = False
                    exceptions += 1
        print(f"    k={k}: j<k のとき v2 変化 = {exceptions}件")

algebraic_proof_skeleton()

# =======================================================
# Part 8: v2保存下での像の分岐
# =======================================================
print("\n" + "=" * 70)
print("Part 8: v2保存下での像の分岐 - 新衝突の源泉")
print("=" * 70)

def image_branching(k):
    """
    j < k のとき v2 が保存されるので:
    T_{k+2}(r + c*2^k) = (3(r+c*2^k)+1) / 2^j
                        = (3r+1)/2^j + 3c*2^k/2^j
                        = T(r) + 3c*2^{k-j}

    mod 2^{k+2} で:
    T_{k+2}(r + c*2^k) = T_k(r) + 3c*2^{k-j} (mod 2^{k+2})

    ここで T_k(r) を t とすると、
    4つの持ち上げの像は: t, t + 3*2^{k-j}, t + 6*2^{k-j}, t + 9*2^{k-j} (mod 2^{k+2})

    これらが mod 2^{k+2} でいつ一致するか?
    差分 3*2^{k-j} の v2 は k-j + v2(3) = k-j (3は奇数)

    一致条件: 3c1*2^{k-j} ≡ 3c2*2^{k-j} (mod 2^{k+2})
    ⟺ 3(c1-c2)*2^{k-j} ≡ 0 (mod 2^{k+2})
    ⟺ (c1-c2) ≡ 0 (mod 2^{j+2})

    c1, c2 in {0,1,2,3} なので |c1-c2| <= 3 < 2^2 = 4 <= 2^{j+2} for j >= 0
    → j >= 0 で常に 4つの像は全て異なる!

    Wait: j=0 のとき 2^{j+2} = 4 で c差分 <= 3 なので c1 != c2 ⟹ 差≠0.
    つまり v2(3r+1) >= 1 (3r+1は常に偶数) だから OK。

    ただし j=1 のとき 2^{j+2} = 8 > 3 なのでやはり異なる。

    結論: j < k のとき、r の4つの持ち上げは4つの異なる像を持つ。
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    collision_in_lifts = 0
    total = 0

    for r in odd_residues(k):
        j = v2(3*r + 1)
        if j >= k:
            continue

        images = set()
        for c in range(4):
            r_lift = r + c * mod_k
            t_lift = syracuse(r_lift) % mod_k2
            images.add(t_lift)

        total += 1
        if len(images) < 4:
            collision_in_lifts += 1

    print(f"  k={k}: {total}個の r (j<k) 中、持ち上げ内衝突 = {collision_in_lifts}個")
    return collision_in_lifts

for k in range(3, 14):
    image_branching(k)

print("\n  結論: j < k のとき、各 r の4つの持ち上げは常に4つの異なる像を持つ")
print("  → 層内では衝突は起きない")

# =======================================================
# Part 9: 異v2層間の新衝突の分析
# =======================================================
print("\n" + "=" * 70)
print("Part 9: 異v2層間の衝突 - 多重度増加のメカニズム")
print("=" * 70)

def cross_layer_collision_analysis(k):
    """
    mod 2^{k+2} での新規衝突の解析。

    r1 (v2層j1) と r2 (v2層j2, j1 != j2) の持ち上げ同士で
    T_{k+2}(r1') = T_{k+2}(r2') となるケースを調べる。

    T_{k+2}(r1 + c1*2^k) = T_k(r1) + 3c1*2^{k-j1} (mod 2^{k+2})
    T_{k+2}(r2 + c2*2^k) = T_k(r2) + 3c2*2^{k-j2} (mod 2^{k+2})

    一致条件:
    T_k(r1) + 3c1*2^{k-j1} ≡ T_k(r2) + 3c2*2^{k-j2} (mod 2^{k+2})

    もし T_k(r1) ≡ T_k(r2) (mod 2^k) ならば（既存衝突）:
    T_k(r1) - T_k(r2) = d * 2^k (d some integer)

    3c1*2^{k-j1} - 3c2*2^{k-j2} ≡ -d*2^k (mod 2^{k+2})
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    fmap_k2 = compute_Tk(k+2)
    fmap_k = compute_Tk(k)

    # mod 2^{k+2} での衝突ペア
    preimage_k2 = defaultdict(list)
    for r, t in fmap_k2.items():
        preimage_k2[t].append(r)

    new_collisions = 0  # mod 2^k では衝突しないが mod 2^{k+2} で衝突
    preserved_collisions = 0  # mod 2^k の衝突が mod 2^{k+2} でも保存

    for t2, preim2 in preimage_k2.items():
        if len(preim2) >= 2:
            for i in range(len(preim2)):
                for j_idx in range(i+1, len(preim2)):
                    r1, r2 = preim2[i], preim2[j_idx]
                    # mod 2^k での像
                    t1_k = fmap_k.get(r1 % mod_k)
                    t2_k = fmap_k.get(r2 % mod_k)

                    if r1 % mod_k == r2 % mod_k:
                        # 同じ r mod 2^k からの異なる持ち上げ → 不可能（Part8で示した）
                        # → これは j >= k の場合にのみ起こりうる
                        pass
                    else:
                        # 異なる r mod 2^k
                        if t1_k == t2_k:
                            preserved_collisions += 1
                        else:
                            new_collisions += 1

    print(f"  k={k}: 保存衝突={preserved_collisions}, 新規衝突={new_collisions}")
    return preserved_collisions, new_collisions

for k in range(5, 12):
    cross_layer_collision_analysis(k)

# =======================================================
# Part 10: 完全な持ち上げ追跡
# =======================================================
print("\n" + "=" * 70)
print("Part 10: 多重度の正確な追跡: mod 2^k の像 t と mod 2^{k+2} の持ち上げ")
print("=" * 70)

def full_multiplicity_tracking(k):
    """
    t mod 2^k が多重度 m を持つとき、
    t の mod 2^{k+2} への奇数持ち上げ {t'} の多重度分布を追跡。

    各 t の持ち上げは t, t+2^k, t+2^{k+1}, t+3*2^k の4つ（全て奇数 since t奇数, 2^k偶数）。

    t の m 個の逆像 r1, ..., rm のそれぞれが 4つに持ち上がる → 4m 個の入力。
    これらが 4つの出力像に分配される。

    核心: この分配パターンは何か?
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    fmap_k = compute_Tk(k)
    fmap_k2 = compute_Tk(k+2)

    preimage_k = defaultdict(list)
    for r, t in fmap_k.items():
        preimage_k[t].append(r)

    preimage_k2 = defaultdict(list)
    for r, t in fmap_k2.items():
        preimage_k2[t].append(r)

    # 各 t mod 2^k について
    for mult_target in [1, 2, 3]:
        targets = [(t, p) for t, p in preimage_k.items() if len(p) == mult_target]
        if not targets:
            continue

        # 持ち上げの多重度分布パターン
        patterns = Counter()
        detailed = []

        for t, preim in targets:
            # t の奇数持ち上げ
            lifts_t = [(t + c * mod_k) % mod_k2 for c in range(4)]

            # 各持ち上げの多重度
            mults = []
            for tl in lifts_t:
                mults.append(len(preimage_k2.get(tl, [])))

            pattern = tuple(sorted(mults, reverse=True))
            patterns[pattern] += 1

            if len(detailed) < 3:
                # 逆像の持ち上げ先を追跡
                for r in preim:
                    for c in range(4):
                        r_lift = r + c * mod_k
                        t_lift = fmap_k2.get(r_lift)
                        detailed.append(f"    r={r}, c={c}: r'={r_lift}, T(r')={t_lift}")

        print(f"\n  k={k}, 多重度{mult_target} ({len(targets)}個)の持ち上げパターン:")
        for pattern, count in patterns.most_common():
            print(f"    {pattern}: {count}個")
            total_preim = sum(pattern)
            expected = mult_target * 4
            print(f"      (逆像合計: {total_preim}, 期待: {expected})")

for k in [5, 7, 9, 11]:
    print(f"\n=== k={k} ===")
    full_multiplicity_tracking(k)

# =======================================================
# Part 11: 証明の完成 - パターン (m+1, m, m, m-1) の解明
# =======================================================
print("\n" + "=" * 70)
print("Part 11: 証明の完成")
print("=" * 70)

print("""
=== N(m,k) = N(m-1,k-2) の代数的証明 ===

【定義】
T_k(r) = T(r) mod 2^k, 奇数 r mod 2^k に対して。
mult_k(t) = |T_k^{-1}(t)|
N(m,k) = |{t : mult_k(t) = m}|

【v2層全単射】(既知)
j = v2(3r+1) のとき、層 L_j(k) = {r 奇数 mod 2^k : v2(3r+1)=j} 上で
phi_j: r -> (3r+1)/2^j mod 2^{k-j} は L_j(k) から奇数 mod 2^{k-j} への全単射。

したがって T_k の像は phi_j の像の和集合で、衝突は異なる層間でのみ起こる。

【持ち上げの構造 (k -> k+2)】
r mod 2^k を r' = r + c*2^k (c=0,1,2,3) に持ち上げる。

3r' + 1 = (3r+1) + 3c*2^k

j = v2(3r+1) < k のとき（これがほぼ全てのケース）:
  v2(3r'+1) = v2((3r+1)(1 + 3c*2^{k-j}/q)) = j  (q = (3r+1)/2^j は奇数)
  ∵ 3c*2^{k-j}/q は 2^{k-j} の倍数で、k-j >= 1

T_{k+2}(r + c*2^k) = (3r+1+3c*2^k)/2^j mod 2^{k+2}
                    = T_k(r) + 3c*2^{k-j} mod 2^{k+2}

【4つの持ち上げの像は全て異なる】
持ち上げの像の差: 3(c1-c2)*2^{k-j} (c1 != c2)
これが 2^{k+2} で割り切れる条件: (c1-c2) が 2^{j+2}/gcd(3,2^{j+2}) = 2^{j+2} の倍数。
|c1-c2| <= 3 < 4 <= 2^{j+2} (j >= 0) → 不可能。
よって 4つの像は全て mod 2^{k+2} で異なる。

【衝突の写像 (重要な核心)】
t mod 2^k が多重度 m の像とする。
t の逆像 r1, ..., rm (異なるv2層) の4m個の持ち上げが
t の 4つの持ち上げ t' = t + d*2^k (d=0,1,2,3) に分配される。

ri の v2層が ji とすると:
T_{k+2}(ri + c*2^k) = t + 3c*2^{k-ji} mod 2^{k+2}

これが t + d*2^k に等しくなる条件:
3c*2^{k-ji} ≡ d*2^k (mod 2^{k+2})
→ d ≡ 3c*2^{-ji} (mod 4)  ... ★

層 ji の ri から来る c=0,1,2,3 の行き先 d:
d(c) = 3c * 2^{-ji} mod 4

ji mod 2 により:
- ji 偶: 2^{-ji} mod 4 = inverse of 1 mod 4 = 1 → d = 3c mod 4 = {0,3,2,1}
- ji 奇: 2^{-ji} mod 4 = inverse of 2 mod 4 → 2は mod 4 で逆元なし!

Wait、これは正しくない。再考が必要。
""")

# 実際に d(c, j) を計算
print("d(c, j) の計算: d ≡ 3c * 2^{k-j} / 2^k = 3c / 2^j (mod 4)")
print("ただし 2^j の mod 4 での逆元は j < 2 のときのみ存在")
print("")
print("正しい計算: T_{k+2}(ri + c*2^k) は t + 3c*2^{k-ji} (mod 2^{k+2})")
print("t の持ち上げは t + d*2^k (d=0,1,2,3)")
print("一致条件: 3c*2^{k-ji} ≡ d*2^k (mod 2^{k+2})")

for j in range(1, 6):
    print(f"\n  v2層 j={j}:")
    for c in range(4):
        # 3c * 2^{k-j} = d * 2^k + e * 2^{k+2}
        # つまり 3c * 2^{k-j} / 2^k = 3c / 2^j = d mod 4
        # j=1: 3c/2 ... これは整数でない可能性
        #
        # 正確には: 3c * 2^{k-j} mod 2^{k+2} の 2^k 係数
        # = (3c * 2^{k-j}) >> k mod 4
        # = 3c >> j mod 4 ... j <= k

        # 3c * 2^{k-j} = 3c * 2^{k-j}
        # これを 2^k で割った商 mod 4:
        # k-j >= 0 なので 3c * 2^{k-j} は 2^{k-j} の倍数
        # 2^k で割ると: 3c * 2^{-j} ... j > 0 のとき整数でない場合がある

        # 実際の計算:
        val = 3 * c  # * 2^{k-j}
        # mod 2^{k+2} で考えると、val * 2^{k-j} の (2^k の上の2ビット) が d
        # d = floor(val * 2^{k-j} / 2^k) mod 4 = floor(val / 2^j) mod 4
        # ただし val/2^j が整数でないとき...

        # 実は mod 2^{k+2} の世界で考える:
        # 3c * 2^{k-j} mod 2^{k+2}
        # j <= k のとき、これは 2^{k-j} の倍数
        # 2^k のブロック = floor(3c * 2^{k-j} / 2^k) mod 4
        # = floor(3c / 2^j) mod 4

        if j <= 2:
            # 3c が 2^j で割り切れる場合のみ d は定まる
            pass

        # 具体的に k を固定して計算
        k_test = 9
        mod_k2_test = 2**(k_test+2)
        actual_val = (3 * c * 2**(k_test - j)) % mod_k2_test
        d = (actual_val >> k_test) % 4
        print(f"    c={c}: 3c*2^{{k-j}} mod 2^{{k+2}} (k={k_test}) => d={d}")

# =======================================================
# Part 12: 正確な分配表の作成
# =======================================================
print("\n" + "=" * 70)
print("Part 12: c -> d 分配表 (v2層jごと)")
print("=" * 70)

def compute_cd_table():
    """各 v2層 j に対して、c ↦ d の対応を計算"""
    # d は k に依存しない（k が十分大きければ）
    # d = floor(3c * 2^{k-j} / 2^k) mod 4
    # = 3c を 2進展開して j ビット右シフトした下位2ビット

    for j in range(1, 8):
        print(f"\nv2層 j={j}:")
        d_map = {}
        for c in range(4):
            val = 3 * c  # 0, 3, 6, 9
            # 2^j で割った商の mod 4
            # val の 2進表現: 0=0, 3=11, 6=110, 9=1001
            # j ビット右シフト:
            d = (val >> j) % 4
            # ただし val が 2^j で割り切れない場合、
            # 2^{k-j} を掛けて 2^k で割るので切り捨てが起きる
            # 実際は: 3c * 2^{k-j} を 2^k 以上 2^{k+2} 未満の部分で取る
            # = (3c * 2^{k-j}) // 2^k % 4
            # = (3c) // 2^j % 4   (k が十分大きいとき)

            # k=20 で検証
            k_test = 20
            exact_d = ((3 * c * 2**(k_test - j)) >> k_test) % 4
            d_map[c] = exact_d
            print(f"  c={c}: d={exact_d}  (3c={3*c}, 3c>>j={3*c >> j}, mod4={exact_d})")

        # d のパターン
        d_values = [d_map[c] for c in range(4)]
        is_permutation = len(set(d_values)) == 4
        print(f"  d values: {d_values}, 置換? {is_permutation}")

compute_cd_table()

print("\n" + "=" * 70)
print("まとめ: 分配パターンの意味")
print("=" * 70)

print("""
v2層 j の元 r の4つの持ち上げ (c=0,1,2,3) が
t の4つの持ち上げ (d=0,1,2,3) にどう対応するか:

  j=1: c -> d: [0,1,3,0] → d=0 が2回! (c=0, c=3 が同じ d=0 に行く)
  j=2: c -> d: [0,0,1,2] → d=0 が2回! (c=0, c=1 が同じ d=0 に行く)
  j=3: c -> d: [0,0,0,1] → d=0 が3回!
  j=4: c -> d: [0,0,0,0] → d=0 が4回! 全て同じ!
  j>=5: c -> d: [0,0,0,0] → 全て d=0

Wait、これは衝突を生む! つまり同一 v2層内でも持ち上げ先が衝突する!

しかし Part 8 で「4つの像は全て異なる」ことを示した。矛盾?
→ d は「t のどの持ち上げに行くか」だが、t + d*2^k は像の
   上位ビットも変えているので、実際の像は t + 3c*2^{k-j} (mod 2^{k+2})
   であり、d = floor(3c/2^j) mod 4 は近似にすぎない。

   正確には像は t + 3c*2^{k-j} mod 2^{k+2} で、
   これが t + d*2^k (t の持ち上げ) に「最も近い」ものに対応するが、
   2^{k-j} < 2^k のとき (j > 0) 像は t の持ち上げ間を「飛び越える」。

→ 分析を修正する必要がある。
""")

# =======================================================
# Part 13: 正しい分析 - 像空間でのグルーピング
# =======================================================
print("\n" + "=" * 70)
print("Part 13: 正しい分析 - mod 2^k の衝突がどう持ち上がるか")
print("=" * 70)

def correct_lifting_analysis(k):
    """
    mod 2^k で T_k(r1) = T_k(r2) = t (r1, r2 異層) のとき、
    r1, r2 の各持ち上げの mod 2^{k+2} での像をトレース。

    r1 (層 j1), r2 (層 j2) として:
    T_{k+2}(r1 + c1*2^k) = t + 3*c1*2^{k-j1} (mod 2^{k+2})
    T_{k+2}(r2 + c2*2^k) = t + 3*c2*2^{k-j2} (mod 2^{k+2})

    一致条件: 3*c1*2^{k-j1} ≡ 3*c2*2^{k-j2} (mod 2^{k+2})
    ⟺ c1*2^{k-j1} ≡ c2*2^{k-j2} (mod 2^{k+2}/3)

    Wait: 3は 2^{k+2} と互いに素なので:
    c1*2^{k-j1} ≡ c2*2^{k-j2} (mod 2^{k+2})

    j1 < j2 とすると:
    c1 ≡ c2*2^{j1-j2} (mod 2^{j1+2})

    j1-j2 < 0 なので 2^{j1-j2} は 2-adic で考える必要がある。

    もっと直接的に:
    2^{k-j1}(c1 - c2*2^{j1-j2}) ≡ 0 (mod 2^{k+2})
    c1 - c2*2^{j1-j2} ≡ 0 (mod 2^{j1+2})

    j1 < j2 → j1 - j2 < 0 → 2^{j1-j2} は分数。

    書き直し: c1*2^{k-j1} - c2*2^{k-j2} ≡ 0 (mod 2^{k+2})
    2^{k-j2}(c1*2^{j2-j1} - c2) ≡ 0 (mod 2^{k+2})
    c1*2^{j2-j1} - c2 ≡ 0 (mod 2^{j2+2})
    c2 ≡ c1*2^{j2-j1} (mod 2^{j2+2})

    c1 in {0,1,2,3}, c2 in {0,1,2,3}:
    j2-j1 >= 1 なので c1*2^{j2-j1} は偶数（c1>0のとき）。
    c2 は 0,1,2,3 のいずれか。
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    fmap_k = compute_Tk(k)
    fmap_k2 = compute_Tk(k+2)

    preimage_k = defaultdict(list)
    for r, t in fmap_k.items():
        preimage_k[t].append(r)

    # 多重度2の像を1つ取って詳細分析
    for t, preim in preimage_k.items():
        if len(preim) == 2:
            r1, r2 = preim
            j1 = v2(3*r1 + 1)
            j2 = v2(3*r2 + 1)
            if j1 > j2:
                r1, r2 = r2, r1
                j1, j2 = j2, j1

            print(f"\n  t={t} mod 2^{k}, r1={r1}(j={j1}), r2={r2}(j={j2}):")

            # 衝突方程式の解
            delta_j = j2 - j1
            print(f"  衝突条件: c2 ≡ c1 * 2^{delta_j} (mod 2^{j2+2})")

            solutions = []
            for c1 in range(4):
                for c2 in range(4):
                    lhs = (c1 * 2**(k-j1)) % mod_k2
                    rhs = (c2 * 2**(k-j2)) % mod_k2
                    if lhs == rhs:
                        solutions.append((c1, c2))

            print(f"  解 (c1, c2): {solutions}")

            # 実際の検証
            print(f"  実際の像:")
            for c1 in range(4):
                r1_lift = r1 + c1 * mod_k
                t1 = syracuse(r1_lift) % mod_k2
                for c2 in range(4):
                    r2_lift = r2 + c2 * mod_k
                    t2 = syracuse(r2_lift) % mod_k2
                    if t1 == t2:
                        print(f"    衝突! c1={c1}, c2={c2}: T({r1_lift}) = T({r2_lift}) = {t1} (mod 2^{k+2})")

            break  # 1例だけ

for k in [5, 7, 9]:
    correct_lifting_analysis(k)

# =======================================================
# Part 14: 衝突数の正確なカウント
# =======================================================
print("\n" + "=" * 70)
print("Part 14: 衝突保存定理の検証")
print("=" * 70)

def collision_preservation_theorem(k):
    """
    定理の候補:
    mod 2^k で多重度 m の像 t が、mod 2^{k+2} で
    [多重度 m+1 の像1つ] + [多重度 m の像2つ] + [多重度 m-1 の像1つ]
    を生むか検証。(パスカル的な分裂)

    あるいは別のパターンか。
    """
    mod_k = 2**k
    mod_k2 = 2**(k+2)

    fmap_k = compute_Tk(k)
    fmap_k2 = compute_Tk(k+2)

    preimage_k = defaultdict(list)
    for r, t in fmap_k.items():
        preimage_k[t].append(r)

    preimage_k2 = defaultdict(list)
    for r, t in fmap_k2.items():
        preimage_k2[t].append(r)

    # 像 t mod 2^k の4つの持ち上げそれぞれの多重度
    by_mult = defaultdict(lambda: Counter())

    for t, preim in preimage_k.items():
        m = len(preim)
        lifts_t = [(t + c * mod_k) % mod_k2 for c in range(4)]
        mults = tuple(sorted([len(preimage_k2.get(tl, [])) for tl in lifts_t], reverse=True))
        by_mult[m][mults] += 1

    # 像でない t (多重度 0) の持ち上げ
    all_odd = set(odd_residues(k))
    image_set = set(fmap_k.values())
    non_image = all_odd - image_set
    for t in non_image:
        lifts_t = [(t + c * mod_k) % mod_k2 for c in range(4)]
        mults = tuple(sorted([len(preimage_k2.get(tl, [])) for tl in lifts_t], reverse=True))
        by_mult[0][mults] += 1

    print(f"\nk={k}:")
    for m in sorted(by_mult.keys()):
        print(f"  多重度 {m} ({sum(by_mult[m].values())}個の像):")
        for pattern, count in by_mult[m].most_common():
            print(f"    -> {pattern}: {count}個")

for k in [5, 6, 7, 8, 9, 10, 11]:
    collision_preservation_theorem(k)
