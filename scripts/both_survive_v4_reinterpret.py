"""
探索172 v4: 命題の正しい解釈の発見

実験結果のまとめ:
1. 停止時間ベースの非排除: both > 0 (排他性は成立しない)  
2. v2(3r+1)=1ベースの非排除: both = 全数 (trivially fails)
3. 反復v2排除: NE = 0 (trivially true but vacuous)

新たなアプローチ: 
問題文を再度読む:
「非排除残基rに対しr,r+2^kが同時に非排除にならない。
 v2(3r+1)=1のケースでT(r+2^k)とT(r)のmod 2^k差分が2^{k-1}であることから導出。」

これは T(r) と T(r+2^k) の差分を mod 2^k で見たとき 2^{k-1} であることに注目。
差分 = 3*2^{k-1} の mod 2^k = 3*2^{k-1} (k >= 3 なので 3*2^{k-1} < 2^k は k=2 まで)

Wait: 3*2^{k-1} vs 2^k
3*2^{k-1} = 1.5 * 2^k > 2^k for all k >= 1
なので mod 2^k: 3*2^{k-1} mod 2^k = 3*2^{k-1} - 2^k = 2^{k-1}(3-2) = 2^{k-1}

つまり T(r+2^k) ≡ T(r) + 2^{k-1} (mod 2^k)

この差分 2^{k-1} こそが排他性のメカニズム!
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

# 差分の検証
print("=" * 70)
print("T(r+2^k) - T(r) mod 2^k の検証")
print("=" * 70)

for k in range(3, 12):
    mod = 2**k
    all_match = True
    for r in range(3, mod, 4):  # r ≡ 3 mod 4
        Tr = (3*r + 1) // 2
        Tr2 = (3*(r + mod) + 1) // 2
        diff = (Tr2 - Tr) % mod
        expected = 2**(k-1)
        if diff != expected:
            all_match = False
            print(f"  MISMATCH k={k}, r={r}: diff mod 2^k = {diff}, expected {expected}")
    if all_match:
        print(f"k={k:2d}: T(r+2^k) ≡ T(r) + 2^{{k-1}} (mod 2^k) ✓")

# 差分の数学的証明:
# T(r) = (3r+1)/2
# T(r+2^k) = (3(r+2^k)+1)/2 = (3r+1)/2 + 3*2^{k-1} = T(r) + 3*2^{k-1}
# mod 2^k: 3*2^{k-1} mod 2^k = 3*2^{k-1} - 2^k = 2^{k-1} (since 3*2^{k-1} = 2^k + 2^{k-1})
print()
print("代数的証明:")
print("  T(r+2^k) = T(r) + 3*2^{k-1}")
print("  3*2^{k-1} = 2^k + 2^{k-1}")
print("  mod 2^k: 3*2^{k-1} ≡ 2^{k-1}")
print("  よって T(r+2^k) ≡ T(r) + 2^{k-1} (mod 2^k)")

# では、T(r) mod 2^k を見たとき、T(r) と T(r) + 2^{k-1} が
# mod 2^k の非排除残基の中で同時に生存できないことを示す必要がある

# T(r) は奇数（r≡3 mod 4 なので）
# T(r) mod 2^k の非排除をさらに追跡すると...

# T(r) の mod 4 は一定 (3*2^{k-1} ≡ 0 mod 4 for k>=3)
# しかし mod 2^{k-1} で見ると差分は 0
# mod 2^k で見ると差分は 2^{k-1}

# これは mod 2^k の情報が1ビット分追加されたことで排除が起こるメカニズム

# 正しい命題:
# 非排除残基 r (mod 2^k) をリフトして mod 2^{k+1} で考えたとき、
# T(r) mod 2^k と T(r+2^k) mod 2^k の差が 2^{k-1} であることから、
# 「非排除テスト」の際に、T の値の上位ビットが異なるため、
# mod 2^{k+1} での判定で片方が排除される。

# より具体的に: k+1ビットの情報で、rリフトの一方の追跡が
# mod 4 ≡ 1 に落ちる（→ 排除）ことを示す

print()
print("=" * 70)
print("排除メカニズム: T(r) mod 2^k の値と mod 4 の関係")
print("=" * 70)

# Syracuse反復を mod 2^k で追跡
def syracuse_mod(r, k):
    """Syracuse関数を mod 2^k で計算"""
    mod = 2**k
    m = (3 * r + 1) % (2 * mod)  # 十分大きなmodで計算
    return (m >> v2(m)) % mod

# 正しい非排除定義: descent step が mod 2^k で確定しない
# = mod 2^k の追跡で T^j(r) mod 4 が常に 3 (j < k ステップの間)
def non_excluded_precise(r, k):
    """rがmod 2^kで非排除かどうか"""
    mod = 2**k
    # rから始めてSyracuse反復を追跡
    # mod 2^k の情報で「下降ステップ」が確定するかどうか
    cur = r % mod
    for step in range(k):
        if cur % 2 == 0:
            return False  # 偶数は即下降
        if cur % 4 == 1:
            return False  # mod 4 ≡ 1 → v2 >= 2 → 下降確定
        # cur % 4 == 3: 上昇ステップ T(cur) = (3*cur+1)/2
        cur = ((3 * cur + 1) // 2) % mod
    return True  # k ステップ経っても下降確定しない

print("\n反復追跡による非排除 (precise):")
for k in range(3, 14):
    mod = 2**k
    ne_k = set()
    for r in range(3, mod, 4):
        if non_excluded_precise(r, k):
            ne_k.add(r)
    
    ne_k1 = set()
    mod1 = 2**(k+1)
    for r in range(3, mod1, 4):
        if non_excluded_precise(r, k+1):
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

print()
print("=" * 70)
print("ステップ数制限なしの非排除 (k-1 ステップまで)")
print("=" * 70)

def non_excluded_v2(r, k, max_steps):
    """rがmod 2^kでmax_stepsステップ以内に下降確定しないか"""
    mod = 2**k
    cur = r % mod
    for step in range(max_steps):
        if cur % 2 == 0:
            return False
        if cur % 4 == 1:
            return False
        cur = ((3 * cur + 1) // 2) % mod
    return True

for max_s in [1, 2, 3]:
    print(f"\nmax_steps = {max_s}:")
    for k in range(3, 14):
        mod = 2**k
        ne_k = set()
        for r in range(3, mod, 4):
            if non_excluded_v2(r, k, max_s):
                ne_k.add(r)
        
        ne_k1 = set()
        mod1 = 2**(k+1)
        for r in range(3, mod1, 4):
            if non_excluded_v2(r, k+1, max_s):
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
        
        print(f"  k={k:2d}: |NE_k|={len(ne_k):4d}, |NE_k+1|={len(ne_k1):4d}, "
              f"both={both}, one={one}, neither={neither}")

