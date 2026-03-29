"""
探索172: both_survive=0 の精密解析
非排除残基rに対し、r と r+2^k が同時に非排除にならないことの検証と
Lean形式化に向けた数学的構造の分析。

定義:
- 奇数残基 r mod 2^k が「非排除」= Syracuseの下降ステップ数がrだけで決まらない
- 非排除の必要条件: r ≡ 3 (mod 4) (すなわち v2(3r+1) = 1)
- "both_survive=0": r が非排除なら r + 2^k は非排除でない
"""

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
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)

def get_non_excluded(k):
    """mod 2^k での非排除残基集合を返す"""
    mod = 2**k
    # 各奇数残基について、同じ残基類の代表元全てが同じ下降ステップ数を持つか検証
    # 非排除 = そのmod 2^kクラスの異なる代表元でステップ数が異なる
    non_excluded = set()
    for r in range(1, mod, 2):
        # rと同じ残基類の数個の代表元でSyracuseの振る舞いをチェック
        # T(r) mod 2^k vs T(r + 2^k) mod 2^k
        # 非排除の定義: v2(3r+1) = 1 かつ T(r) mod 2^{k-1} が一意でない
        # 簡易版: v2(3r+1) = 1 のものだけが候補
        if v2(3*r + 1) != 1:
            continue
        # T(r) = (3r+1)/2 for v2=1 case
        T_r = (3*r + 1) // 2
        # T_r の mod 2^k での振る舞いを見る
        # r と r + 2^k で T の値の mod 2^{k-1} が一致するか
        r2 = r + mod
        T_r2 = (3*r2 + 1) // 2
        # T(r) mod 2^{k-1} と T(r+2^k) mod 2^{k-1} の比較
        # T(r+2^k) = T(r) + 3*2^{k-1}
        # 差分 = 3 * 2^{k-1}
        # v2 の振る舞いが同じかどうかが問題
        # 非排除の精密な定義: mod 2^k の残基クラスの中で
        # 下降に必要なステップ数が完全に決まらないもの
        
        # 代替アプローチ: 複数の代表元で停止時間が一致するか
        steps_set = set()
        for rep_idx in range(8):  # 0..7
            n_rep = r + rep_idx * mod
            if n_rep == 0:
                continue
            # 停止時間（初めてn未満になるまでのsyracuseステップ数）を概算
            cur = n_rep
            steps = 0
            for _ in range(200):
                cur = syracuse(cur)
                steps += 1
                if cur < n_rep:
                    break
            steps_set.add(steps)
        if len(steps_set) > 1:
            non_excluded.add(r)
    return non_excluded

# k=3..14 での非排除残基を計算し、リフトの排他性を検証
print("=" * 70)
print("both_survive=0 検証: r と r+2^k が同時に非排除にならないことの検証")
print("=" * 70)

results = []
for k in range(3, 15):
    ne_k = get_non_excluded(k)
    ne_k1 = get_non_excluded(k+1)
    
    # r ∈ ne_k のとき、mod 2^{k+1} のリフトは r と r + 2^k
    # ne_k1 にどちらが属するか
    both_survive = 0
    one_survives = 0
    none_survives = 0
    
    for r in sorted(ne_k):
        r_low = r  # r mod 2^{k+1}
        r_high = r + 2**k  # r + 2^k mod 2^{k+1}
        
        low_in = r_low in ne_k1
        high_in = r_high in ne_k1
        
        if low_in and high_in:
            both_survive += 1
        elif low_in or high_in:
            one_survives += 1
        else:
            none_survives += 1
    
    total_ne = len(ne_k)
    print(f"k={k:2d}: |NE_k|={total_ne:4d}, both={both_survive}, one={one_survives}, none={none_survives}")
    results.append({
        'k': k, 'ne_k': total_ne, 'ne_k1': len(ne_k1),
        'both': both_survive, 'one': one_survives, 'none': none_survives
    })

print()
print("=" * 70)
print("数学的分析: v2(3r+1)=1 のときの T(r) と T(r+2^k) の差分")
print("=" * 70)

# T(r) = (3r+1)/2 for r ≡ 3 (mod 4)
# T(r + 2^k) = (3(r + 2^k) + 1) / 2 = (3r + 1 + 3*2^k) / 2
#             = T(r) + 3 * 2^{k-1}
# 差分 = 3 * 2^{k-1}

print("T(r + 2^k) - T(r) = 3 * 2^{k-1} (v2=1のとき)")
print()

# T(r) と T(r + 2^k) の mod 2 の振る舞いを分析
# T(r) = (3r+1)/2
# v2(T(r)) vs v2(T(r+2^k))
# T(r+2^k) = T(r) + 3*2^{k-1}
# v2(T(r) + 3*2^{k-1}) = ?

print("v2(T(r)) と v2(T(r+2^k)) の関係:")
for k in range(3, 11):
    ne_k = get_non_excluded(k)
    for r in sorted(ne_k)[:5]:  # 各kの最初の5つ
        Tr = (3*r + 1) // 2
        Tr2 = (3*(r + 2**k) + 1) // 2
        diff = Tr2 - Tr
        v2_Tr = v2(Tr)
        v2_Tr2 = v2(Tr2)
        print(f"  k={k}, r={r:4d}: T(r)={Tr:6d} (v2={v2_Tr}), T(r+2^k)={Tr2:6d} (v2={v2_Tr2}), diff={diff} = 3*2^{k-1}={3*2**(k-1)}")
    print()

print("=" * 70)
print("核心分析: T(r) mod 2^{k-1} の値とリフト生存の関係")
print("=" * 70)

# 仮説: v2(T(r)) と v2(T(r+2^k)) のうち少なくとも一方が大きい
# → 少なくとも一方のリフトで下降ステップが確定する
# T(r+2^k) = T(r) + 3*2^{k-1}
# min(v2(T(r)), v2(T(r)+3*2^{k-1})) = min(v2(T(r)), k-1) if v2(T(r)) != k-1
# (because v2(3*2^{k-1}) = k-1 since 3 is odd)

# v2(a + b) = min(v2(a), v2(b)) if v2(a) != v2(b)
# v2(a + b) >= min(v2(a), v2(b)) + 1 if v2(a) == v2(b)

print("\nv2(T(r)) の分布とリフト排他性の因果関係:")
for k in range(3, 13):
    ne_k = get_non_excluded(k)
    ne_k1 = get_non_excluded(k+1)
    
    v2_Tr_vs_km1 = {'less': 0, 'equal': 0, 'greater': 0}
    exclusive_when = {'less': [0, 0], 'equal': [0, 0], 'greater': [0, 0]}
    
    for r in sorted(ne_k):
        Tr = (3*r + 1) // 2
        v2_Tr = v2(Tr)
        
        if v2_Tr < k - 1:
            cat = 'less'
        elif v2_Tr == k - 1:
            cat = 'equal'
        else:
            cat = 'greater'
        
        v2_Tr_vs_km1[cat] += 1
        
        r_low = r
        r_high = r + 2**k
        low_in = r_low in ne_k1
        high_in = r_high in ne_k1
        
        if low_in and high_in:
            exclusive_when[cat][0] += 1  # both survive (violation)
        else:
            exclusive_when[cat][1] += 1  # exclusive (OK)
    
    print(f"k={k:2d}: v2(T(r)) < k-1: {v2_Tr_vs_km1['less']:3d} (both={exclusive_when['less'][0]}, excl={exclusive_when['less'][1]})")
    print(f"       v2(T(r)) = k-1: {v2_Tr_vs_km1['equal']:3d} (both={exclusive_when['equal'][0]}, excl={exclusive_when['equal'][1]})")
    print(f"       v2(T(r)) > k-1: {v2_Tr_vs_km1['greater']:3d} (both={exclusive_when['greater'][0]}, excl={exclusive_when['greater'][1]})")

