"""
探索172 v3: 排他性の精密な定理の発見と証明

核心定理（候補）:
r ≡ 3 (mod 4) のとき、T(r) = (3r+1)/2 は奇数。
定義: S(r) = 3*T(r)+1 = 3*(3r+1)/2 + 1 = (9r+5)/2
     （ただし分子 9r+5 は偶数）

T(r+2^k) = T(r) + 3*2^{k-1}
S(r+2^k) = 3*T(r+2^k)+1 = 3*(T(r)+3*2^{k-1})+1 = S(r) + 9*2^{k-1}

v2(9*2^{k-1}) = k-1 (9は奇数)

超距離的性質:
  v2(S(r)) != k-1 → v2(S(r+2^k)) = min(v2(S(r)), k-1)
  v2(S(r)) = k-1  → v2(S(r+2^k)) >= k

排他性命題:
  v2(S(r)) >= k-1 ∨ v2(S(r+2^k)) >= k-1 は「常に」成り立つ？ → NO
  (v2(S(r)) < k-1 のとき v2(S(r+2^k)) = v2(S(r)) < k-1)

ではboth_survive=0が成り立たない理由を正確に突き止める。
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

# 定理の正確な形を探る
# 非排除残基の定義を再確認: stopping time based
# r mod 2^k の全ての代表元 r, r+2^k, r+2*2^k, ... で
# 「初めて値が元未満になるSyracuseステップ数」が一致するか

print("=" * 70)
print("非排除残基の正確な定義の検証")
print("=" * 70)

def stopping_steps(n, max_iter=500):
    """初めて n 未満になるまでのSyracuseステップ数"""
    cur = n
    for s in range(1, max_iter):
        cur = syracuse(cur)
        if cur < n:
            return s
    return -1

# k=5 で |NE|=4 と出た。そこの非排除残基を詳しく見る
k = 5
mod = 2**k
print(f"\nk={k}, mod={mod}")
print("全ての r ≡ 3 (mod 4) の停止時間パターン:")
ne_residues = []
for r in range(3, mod, 4):
    steps_list = []
    for j in range(8):
        n = r + j * mod
        if n == 0: continue
        steps_list.append(stopping_steps(n))
    steps_set = set(steps_list)
    is_ne = len(steps_set) > 1
    marker = " *** NE" if is_ne else ""
    print(f"  r={r:3d}: steps={steps_list}{marker}")
    if is_ne:
        ne_residues.append(r)

print(f"\n非排除残基 (k={k}): {ne_residues}")

# k=5, k+1=6 での排他性
print(f"\nk+1={k+1} でのリフト:")
k1 = k + 1
mod1 = 2**k1
ne_k1 = []
for r in range(3, mod1, 4):
    steps_list = []
    for j in range(8):
        n = r + j * mod1
        if n == 0: continue
        steps_list.append(stopping_steps(n))
    if len(set(steps_list)) > 1:
        ne_k1.append(r)

ne_k1_set = set(ne_k1)
print(f"NE at k+1={k1}: {sorted(ne_k1)}")
for r in ne_residues:
    low = r
    high = r + 2**k
    print(f"  r={r}: low={low} in NE_{k1}? {low in ne_k1_set}, high={high} in NE_{k1}? {high in ne_k1_set}")

# もっとkを小さくして構造を見る
print()
print("=" * 70)
print("k=3,4,5,6,7 での非排除と排他性の詳細")
print("=" * 70)

for k in range(3, 10):
    mod = 2**k
    ne_k = set()
    for r in range(3, mod, 4):
        steps_list = []
        for j in range(16):
            n = r + j * mod
            if n == 0: continue
            steps_list.append(stopping_steps(n))
        if len(set(steps_list)) > 1:
            ne_k.add(r)
    
    mod1 = 2**(k+1)
    ne_k1 = set()
    for r in range(3, mod1, 4):
        steps_list = []
        for j in range(16):
            n = r + j * mod1
            if n == 0: continue
            steps_list.append(stopping_steps(n))
        if len(set(steps_list)) > 1:
            ne_k1.add(r)
    
    both = 0
    one = 0
    neither = 0
    for r in sorted(ne_k):
        low_in = r in ne_k1
        high_in = (r + 2**k) in ne_k1
        if low_in and high_in:
            both += 1
        elif low_in or high_in:
            one += 1
        else:
            neither += 1
    
    print(f"k={k}: |NE_k|={len(ne_k):4d}, |NE_k+1|={len(ne_k1):4d}, "
          f"both={both}, one={one}, neither={neither}")

# これが根本的にboth > 0 なら、命題の再解釈が必要

# 別の解釈: "both_survive=0" は停止時間ベースではなく、
# 「v2(3r+1)の値による排除」の1ステップ版かもしれない
print()
print("=" * 70)
print("別解釈: v2排除 (v2(3r+1)>=2 なら排除) でのリフト排他性")
print("=" * 70)

for k in range(3, 16):
    mod = 2**k
    # 非排除 = v2(3r+1) = 1 のr (つまり r ≡ 3 mod 4)
    ne_k = set()
    for r in range(1, mod, 2):
        if v2(3*r + 1) == 1:
            ne_k.add(r)
    
    # k+1 でのリフト
    mod1 = 2**(k+1)
    ne_k1 = set()
    for r in range(1, mod1, 2):
        if v2(3*r + 1) == 1:
            ne_k1.add(r)
    
    both = 0
    for r in ne_k:
        if r in ne_k1 and (r + 2**k) in ne_k1:
            both += 1
    
    print(f"k={k:2d}: |NE_k|={len(ne_k):5d}, |NE_k+1|={len(ne_k1):5d}, both_survive={both}")
    # v2(3r+1)=1 ⟺ r≡3(mod4), v2(3(r+2^k)+1)=v2(3r+1+3*2^k)
    # 3r+1 ≡ 2 (mod 4) (since r≡3 mod4)
    # 3(r+2^k)+1 = 3r+1+3*2^k
    # v2(3*2^k) = k + v2(3) = k
    # For k>=2: v2(3r+1) = 1 and v2(3*2^k) = k
    # Since 1 < k for k>=2: v2(sum) = min(1, k) = 1
    # So BOTH survive! This is NOT exclusive for v2 definition.

# Let's check 3rd interpretation: iterated v2 exclusion
print()
print("=" * 70)  
print("3rd解釈: 反復的な非排除 — T^m で初めて mod 4 ≡ 1 になるステップ数")
print("=" * 70)

# 非排除残基の本質: T を反復適用して、mod 2^k の情報で
# T^m(r) mod 4 ≡ 1 (→ 下降確定) かどうかが決まるステップ数
# r ≡ 3 (mod 4) → T(r) = (3r+1)/2, T(r) mod 4 = ?
# T(r) ≡ 1 (mod 4) なら次は下降確定
# T(r) ≡ 3 (mod 4) なら次も上昇、さらに反復必要

def descent_step_mod2k(r, k):
    """mod 2^k の情報だけで下降確定するステップ数を返す
    確定できない場合は None"""
    mod = 2**k
    cur = r % mod
    for step in range(1, k+2):
        if cur % 4 == 1 and cur > 1:
            return step
        if cur % 2 == 0:
            return step  # even → guaranteed descent via standard collatz
        # cur is odd and cur % 4 == 3 → T(cur) = (3*cur+1)/2 mod 2^k
        cur = ((3 * cur + 1) // 2) % mod
    return None

# これにより「descent_step がNoneの残基」が非排除
for k in range(3, 13):
    mod = 2**k
    ne_k = set()
    for r in range(3, mod, 4):
        ds = descent_step_mod2k(r, k)
        if ds is None:
            ne_k.add(r)
    
    ne_k1 = set()
    mod1 = 2**(k+1)
    for r in range(3, mod1, 4):
        ds = descent_step_mod2k(r, k+1)
        if ds is None:
            ne_k1.add(r)
    
    both = 0
    one = 0
    neither = 0
    for r in sorted(ne_k):
        low_in = r in ne_k1
        high_in = (r + 2**k) in ne_k1
        if low_in and high_in:
            both += 1
        elif low_in or high_in:
            one += 1
        else:
            neither += 1
    
    print(f"k={k:2d}: |NE_k|={len(ne_k):4d}, |NE_k+1|={len(ne_k1):4d}, "
          f"both={both}, one={one}, neither={neither}")

# 4th interpretation: T(r) mod 4 の排他性 (not T(r) mod 2^k)
print()
print("=" * 70)
print("4th: T^j(r) vs T^j(r+2^k) のmod 4パリティ排他性")
print("(あるステップjで T^j(r) mod 4 と T^j(r+2^k) mod 4 が異なるか)")
print("=" * 70)

for k in range(3, 12):
    mod = 2**k
    exclusive_at_step = [0] * 10  # step 1..9
    never_exclusive = 0
    
    for r in range(3, mod, 4):
        found = False
        cur_r = r
        cur_r2 = r + mod
        for step in range(1, 10):
            Tr = (3*cur_r + 1) // 2 if cur_r % 2 == 1 else cur_r  # safety
            Tr2 = (3*cur_r2 + 1) // 2 if cur_r2 % 2 == 1 else cur_r2
            
            if Tr % 4 != Tr2 % 4:
                exclusive_at_step[step] += 1
                found = True
                break
            cur_r = Tr
            cur_r2 = Tr2
        
        if not found:
            never_exclusive += 1
    
    total = mod // 4
    excl_sum = sum(exclusive_at_step)
    print(f"k={k:2d}: total={total:4d}, excl_at_step={exclusive_at_step[1:6]}, "
          f"never={never_exclusive}")

# 5th: T(r) mod 2^{k-1} difference analysis
print()
print("=" * 70)
print("5th: T(r) mod 2^{k-1} での差分 — 3*2^{k-1} の影響")
print("=" * 70)

# T(r+2^k) - T(r) = 3*2^{k-1}
# mod 2^{k-1} では 3*2^{k-1} ≡ 0
# mod 2^k では 3*2^{k-1} ≠ 0
# つまり T(r) mod 2^{k-1} = T(r+2^k) mod 2^{k-1}
# しかし T(r) mod 2^k ≠ T(r+2^k) mod 2^k

# 二回目の操作:
# S(r) = (3*T(r)+1)/2^{v2(3*T(r)+1)}  (= syracuse(T(r)))
# S(r+2^k) = (3*T(r+2^k)+1)/2^{v2(3*T(r+2^k)+1)}

# 3*T(r+2^k)+1 = 3*T(r) + 9*2^{k-1} + 1 = (3*T(r)+1) + 9*2^{k-1}
# v2(9*2^{k-1}) = k-1

# 核心: 超距離的性質
# A = 3*T(r)+1, B = 9*2^{k-1}
# v2(A) vs v2(B) = k-1

# Case 1: v2(A) < k-1 → v2(A+B) = v2(A) → S(r) mod 2^? と S(r+2^k) mod 2^? は同じv2
# Case 2: v2(A) = k-1 → v2(A+B) >= k → v2が大きくなる → S(r+2^k)の下降が加速
# Case 3: v2(A) > k-1 → v2(A+B) = k-1 → S(r)の下降が加速

print("v2(3*T(r)+1) と k-1 の関係:")
for k in range(3, 12):
    mod = 2**k
    case1 = 0  # v2 < k-1: 両方同じv2
    case2 = 0  # v2 = k-1: r+2^kが有利
    case3 = 0  # v2 > k-1: rが有利
    
    for r in range(3, mod, 4):
        Tr = (3*r + 1) // 2
        A = 3*Tr + 1
        v = v2(A)
        if v < k-1:
            case1 += 1
        elif v == k-1:
            case2 += 1
        else:
            case3 += 1
    
    total = mod // 4
    print(f"  k={k:2d}: v2<k-1: {case1:4d} ({100*case1/total:.1f}%), "
          f"v2=k-1: {case2:3d} ({100*case2/total:.1f}%), "
          f"v2>k-1: {case3:3d} ({100*case3/total:.1f}%)")

print()
print("注目: v2(3T(r)+1) = k-1 or > k-1 の残基は少数。")
print("大半は v2 < k-1 で、排他性は1ステップ目で発生しない。")
print("→ 排他性は複数ステップの蓄積効果として現れる可能性。")
