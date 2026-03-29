"""
探索172 v2: 非排除の定義を再考し、both_survive=0の成立条件を探る

非排除残基の定義について2つのアプローチ:
(A) 停止時間に基づく定義（従来）: 同じ残基クラスの代表元で停止時間が異なる
(B) v2に基づく排除: mod 2^k で v2(3r+1) >= 2 なら1ステップで下降確定 → 排除
    非排除 = v2(3r+1) = 1 の残基

「both_survive=0」の正しい解釈:
非排除残基 r (mod 2^k) のリフト r, r+2^k (mod 2^{k+1}) について、
v2(3r+1)=1 のケースで T(r) = (3r+1)/2 を考えたとき、
T(r) mod 2^{k} と T(r+2^k) mod 2^{k} の振る舞いの違いにより
「さらに進んだ先での排除」が片方に必ず起こる、という命題かもしれない。

あるいは: v2(T(r)) と v2(T(r+2^k)) の一方が必ず大きい → 片方は2ステップ目で
下降確定。
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

def T_simple(r):
    """v2(3r+1)=1 のとき T(r) = (3r+1)/2"""
    return (3*r + 1) // 2

# Approach 1: v2(T(r)) と v2(T(r+2^k)) の排他的パターン
print("=" * 70)
print("アプローチ1: v2(T(r)) vs v2(T(r+2^k))")
print("T(r) = (3r+1)/2, T(r+2^k) = T(r) + 3*2^{k-1}")
print("v2(a + 3*2^{k-1}) where v2(3*2^{k-1}) = k-1")
print("=" * 70)

# Key insight:
# T(r+2^k) = T(r) + 3*2^{k-1}
# v2(3*2^{k-1}) = k-1
# By ultrametric: v2(T(r) + 3*2^{k-1}) = min(v2(T(r)), k-1) if v2(T(r)) != k-1
#                                        >= k if v2(T(r)) = k-1

for k in range(3, 16):
    mod = 2**k
    count_v2_less = 0
    count_v2_equal = 0
    count_v2_greater = 0
    
    # v2(T(r)) != k-1 のとき: min(v2(T(r)), k-1) 
    # → 一方は v2 = min(v2_Tr, k-1), 他方は v2_Tr
    # v2_Tr < k-1 のとき: v2(T(r)) = v2_Tr, v2(T(r+2^k)) = v2_Tr (同じ!)
    # v2_Tr > k-1 のとき: v2(T(r)) = v2_Tr, v2(T(r+2^k)) = k-1
    # v2_Tr = k-1 のとき: v2(T(r+2^k)) >= k (cancellation)
    
    for r in range(3, mod, 4):  # r ≡ 3 (mod 4) only
        Tr = T_simple(r)
        v2_Tr = v2(Tr)
        Tr2 = T_simple(r + mod)
        v2_Tr2 = v2(Tr2)
        
        if v2_Tr < k-1:
            count_v2_less += 1
        elif v2_Tr == k-1:
            count_v2_equal += 1
        else:
            count_v2_greater += 1
    
    total = mod // 4
    print(f"k={k:2d}: total r≡3(mod4)={total:5d}, v2(T(r))<k-1: {count_v2_less:5d}, "
          f"=k-1: {count_v2_equal:5d}, >k-1: {count_v2_greater:5d}")


# Approach 2: T(r) のmod 2値の解析
print()
print("=" * 70)
print("アプローチ2: T(r) の偶奇パターン — v2排除メカニズム")
print("=" * 70)

# r ≡ 3 (mod 4) → T(r) = (3r+1)/2 は奇数
# T(r) mod 2 のパターン: always odd? Let's check
print("\nT(r) = (3r+1)/2 mod 2 の分布:")
for k in range(3, 10):
    mod = 2**k
    even_count = 0
    odd_count = 0
    for r in range(3, mod, 4):
        Tr = T_simple(r)
        if Tr % 2 == 0:
            even_count += 1
        else:
            odd_count += 1
    print(f"  k={k}: T(r) even={even_count}, odd={odd_count}")

# Approach 3: 真の排除メカニズム — v2(3*T(r)+1) の解析
print()
print("=" * 70)
print("アプローチ3: 2ステップ目の排除 — v2(3*T(r)+1) の比較")
print("=" * 70)

# T(r) は奇数（r≡3 mod 4 なら）、次のステップは 3*T(r)+1
# r と r+2^k のリフトで v2(3*T(r)+1) と v2(3*T(r+2^k)+1) を比較
# T(r+2^k) = T(r) + 3*2^{k-1}
# 3*T(r+2^k)+1 = 3*(T(r) + 3*2^{k-1})+1 = 3*T(r)+1 + 9*2^{k-1}

for k in range(3, 13):
    mod = 2**k
    both_large = 0  # 両方とも v2 = 1 (つまり両方上昇)
    one_large = 0    # 片方が v2 >= 2 (片方は下降確定)
    
    for r in range(3, mod, 4):
        Tr = T_simple(r)
        Tr2 = T_simple(r + mod)
        
        # T(r) must be odd for this analysis
        if Tr % 2 == 0 or Tr2 % 2 == 0:
            continue
        
        v2_next_r = v2(3 * Tr + 1)
        v2_next_r2 = v2(3 * Tr2 + 1)
        
        # mod 4 check on T(r)
        Tr_mod4 = Tr % 4
        Tr2_mod4 = Tr2 % 4
        
        if Tr_mod4 == 3 and Tr2_mod4 == 3:
            both_large += 1
        elif Tr_mod4 == 3 or Tr2_mod4 == 3:
            one_large += 1
    
    total = mod // 4
    print(f"k={k:2d}: T(r)≡3&T(r+2^k)≡3(mod4)={both_large:4d}, one≡3={one_large:4d}, total={total:5d}")

# Approach 4: T(r) mod 4 のパターンの詳細
print()
print("=" * 70)
print("アプローチ4: T(r) mod 4 vs T(r+2^k) mod 4 の排他性")
print("=" * 70)
print("T(r+2^k) = T(r) + 3*2^{k-1}")
print("mod 4 での差分: 3*2^{k-1} mod 4")
print()

for k in range(3, 10):
    diff = (3 * 2**(k-1)) % 4
    print(f"  k={k}: 3*2^{k-1} = {3*2**(k-1)}, mod 4 = {diff}")

print()
print("重要な帰結:")
print("k=3: 差分 = 3*4 = 12, mod 4 = 0 → T(r)とT(r+8)は mod4 が同じ")
print("k=4: 差分 = 3*8 = 24, mod 4 = 0 → 同上")
print("k=5: 差分 = 3*16 = 48, mod 4 = 0 → 同上")
print("→ 3*2^{k-1} mod 4 = 0 for k >= 3 (since k-1 >= 2)")
print("→ T(r) mod 4 = T(r+2^k) mod 4 ALWAYS!")
print("→ mod 4 による排他性は成立しない")

# Approach 5: T(r) mod 8 での排他性 (k >= 4)
print()
print("=" * 70)
print("アプローチ5: T(r) mod 8 での排他性")
print("=" * 70)
print("3*2^{k-1} mod 8:")
for k in range(3, 12):
    diff = (3 * 2**(k-1)) % 8
    print(f"  k={k}: 3*2^{k-1} mod 8 = {diff}")

print()
print("k=3: diff mod 8 = 4 → T(r)とT(r+8)は mod8 が4だけ異なる")
print("k=4: diff mod 8 = 0 → T(r) mod 8 = T(r+16) mod 8")
print("k>=4: diff mod 8 = 0")
print()

# Approach 6: 最も重要な観察 — T(r) mod 2^{k-1} の分析
# T(r+2^k) = T(r) + 3*2^{k-1}
# mod 2^{k-1}: T(r+2^k) ≡ T(r) (mod 2^{k-1})
# mod 2^k: T(r+2^k) ≡ T(r) + 3*2^{k-1} (mod 2^k)
# 差分 3*2^{k-1} は mod 2^k で非ゼロ (since v2(3*2^{k-1}) = k-1 < k)

print("=" * 70)
print("核心: 2^{k-1} での差分による v2 排他性の精密分析")
print("=" * 70)
print()

# v2(T(r)) の分布を精密に
for k in range(3, 14):
    mod = 2**k
    v2_dist = {}
    
    for r in range(3, mod, 4):
        Tr = T_simple(r)
        v = v2(Tr)
        v2_dist[v] = v2_dist.get(v, 0) + 1
    
    print(f"k={k:2d}: v2(T(r)) distribution: ", end="")
    for v in sorted(v2_dist.keys()):
        print(f"v2={v}:{v2_dist[v]} ", end="")
    print()

# T(r) は常に奇数なので v2(T(r)) = 0!
print()
print("*** 重要発見: r ≡ 3 (mod 4) → T(r) = (3r+1)/2 は常に奇数 ***")
print("*** よって v2(T(r)) = 0 always ***")
print()
print("ということは、T(r) の次のステップ syracuse(T(r)) の解析が本質。")
print("T(r) は奇数なので、T(r) mod 4 = 1 or 3 が問題。")

# Approach 7: T(r) mod 4 のパターンと排他性
print()
print("=" * 70)  
print("決定的分析: v2(3*T(r)+1) と v2(3*T(r+2^k)+1)")
print("=" * 70)

# T(r+2^k) = T(r) + 3*2^{k-1}
# 3*T(r+2^k)+1 = 3*T(r)+1 + 9*2^{k-1}
# v2(9*2^{k-1}) = k-1 (since 9 is odd)
# By ultrametric property:
# if v2(3*T(r)+1) != k-1: v2(3*T(r+2^k)+1) = min(v2(3*T(r)+1), k-1)
# if v2(3*T(r)+1) = k-1: v2(3*T(r+2^k)+1) >= k

print("\nv2(3*T(r)+1) の分布:")
for k in range(3, 14):
    mod = 2**k
    v2_dist = {}
    
    for r in range(3, mod, 4):
        Tr = T_simple(r)
        v = v2(3*Tr + 1)
        v2_dist[v] = v2_dist.get(v, 0) + 1
    
    print(f"k={k:2d}: ", end="")
    for v in sorted(v2_dist.keys()):
        if v2_dist[v] > 0:
            marker = " ***" if v == k-1 else ""
            print(f"v2={v}:{v2_dist[v]}{marker} ", end="")
    print()

print()
print("排他性検証: v2(3*T(r)+1) < k-1 のとき")
print("  min(v2(3T(r)+1), k-1) = v2(3T(r)+1)")
print("  つまり v2(3T(r+2^k)+1) = v2(3T(r)+1): 同じ! → 排他性なし")
print()
print("v2(3*T(r)+1) = k-1 のとき:")
print("  v2(3T(r+2^k)+1) >= k → 一方が大きく下降確定")
print("  → 排他性あり!")
print()
print("v2(3*T(r)+1) > k-1 のとき:")
print("  v2(3T(r+2^k)+1) = k-1 → 逆に他方が固定")
print("  → 排他性あり!")

