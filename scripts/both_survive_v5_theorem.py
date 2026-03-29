"""
探索172 v5: 形式化可能な定理の同定

確認済みの事実:
1. r ≡ 3 (mod 4) かつ v2(3r+1) = 1 のとき T(r) = (3r+1)/2
2. T(r+2^k) = T(r) + 3*2^{k-1}
3. T(r+2^k) ≡ T(r) + 2^{k-1} (mod 2^k)  [3*2^{k-1} mod 2^k = 2^{k-1}]

形式化目標:
(A) T(r+2^k) - T(r) = 3*2^{k-1}  [厳密な差分]
(B) T(r+2^k) mod 2^k = (T(r) + 2^{k-1}) mod 2^k  [mod 2^k の差分]
(C) 3*2^{k-1} mod 2^k = 2^{k-1}  [差分の簡約]

さらに、この差分がSyracuse反復追跡でどう作用するかの解析:
- T(r)が奇数（常に）→ T(r) mod 4 = 1 or 3
- T(r)+2^{k-1} mod 4 はk>=3のとき T(r) mod 4 と一致
  (2^{k-1} mod 4 = 0 for k >= 3)

排他性が成立する場面を正確に特定するため、2段目の差分を計算。
T^2(r) = syracuse(T(r)) vs T^2(r+2^k) = syracuse(T(r+2^k))
T(r+2^k) = T(r) + 3*2^{k-1}
"""

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

# 定理(A)の検証と同時に、2段目の差分を追跡
print("=" * 70)
print("2段目の差分: T^2(r+2^k) - T^2(r) の構造")
print("T^2(r) = syracuse(T(r)), where T(r) = (3r+1)/2")
print("=" * 70)

# T(r) ≡ 3 (mod 4) のとき (つまり r ≡ 7 mod 8):
# T^2(r) = (3*T(r)+1)/2 (since v2 = 1)
# T^2(r+2^k) = (3*(T(r)+3*2^{k-1})+1)/2 = (3*T(r)+1+9*2^{k-1})/2
#            = T^2(r) + 9*2^{k-2}
# 9*2^{k-2} mod 2^k = 9*2^{k-2} (for k >= 4, since 9*2^{k-2} < 2^k ⟺ 9 < 4 → false for k<5)
# Actually: 9*2^{k-2} mod 2^k depends on k
# k=3: 9*2^1 = 18, mod 8 = 2
# k=4: 9*2^2 = 36, mod 16 = 4
# k=5: 9*2^3 = 72, mod 32 = 8
# k=6: 9*2^4 = 144, mod 64 = 16
# General: 9*2^{k-2} mod 2^k = 9*2^{k-2} - 2^k * floor(9*2^{k-2}/2^k)
#  = 9*2^{k-2} - 2^k * floor(9/4)
#  = 9*2^{k-2} - 2^k * 2 = 2^{k-2}(9 - 8) = 2^{k-2}
# Wait: 9*2^{k-2} = (8+1)*2^{k-2} = 2^k + 2^{k-2}
# mod 2^k: 2^{k-2}

print("\n9*2^{k-2} mod 2^k の検証:")
for k in range(3, 15):
    val = (9 * 2**(k-2)) % (2**k)
    expected = 2**(k-2)
    print(f"  k={k}: 9*2^{k-2} = {9*2**(k-2)}, mod 2^k = {val}, 2^{k-2} = {expected}, match={val==expected}")

# T(r) ≡ 1 (mod 4) のとき (つまり r ≡ 3 mod 8):
# v2(3*T(r)+1) >= 2, so T^2(r) = (3*T(r)+1)/2^{v2}
# T(r+2^k) = T(r) + 3*2^{k-1}
# 3*T(r+2^k)+1 = 3*T(r)+1 + 9*2^{k-1}
# v2(9*2^{k-1}) = k-1

# For T(r) ≡ 1 (mod 4):
# 3*T(r)+1 ≡ 3+1 = 4 ≡ 0 (mod 4), so v2(3*T(r)+1) >= 2
# 3*T(r+2^k)+1 = 3*T(r)+1 + 9*2^{k-1}
# 差分 9*2^{k-1} の v2 は k-1
# v2(3T(r)+1) と k-1 の比較がカギ

# 核心的帰結を見つける: T の j ステップ後の差分パターン
print()
print("=" * 70)
print("j段反復後の差分: T^j(r+2^k) - T^j(r) mod 2^k")
print("(r≡3 mod 4 に限定)")
print("=" * 70)

def T_iter_mod(r, k, j):
    """T を j 回反復適用した結果の mod 2^k"""
    mod = 2**k
    cur = r % mod
    for _ in range(j):
        if cur % 2 == 0:
            # 偶数の場合は Syracuse の定義外
            return None
        if cur % 4 == 3:
            # v2 = 1 case
            cur = ((3 * cur + 1) // 2) % mod
        elif cur % 4 == 1:
            # v2 >= 2, but exact value depends on more bits
            # Can't compute exactly mod 2^k
            m = 3 * cur + 1
            cur = (m >> v2(m)) % mod
    return cur

for k in range(3, 12):
    mod = 2**k
    print(f"\nk={k}:")
    for r in range(3, min(mod, 64), 4):
        diffs = []
        for j in range(1, min(k, 6)):
            Tj_r = T_iter_mod(r, k, j)
            Tj_r2 = T_iter_mod(r + mod, k, j)
            if Tj_r is not None and Tj_r2 is not None:
                diff = (Tj_r2 - Tj_r) % mod
                diffs.append(diff)
            else:
                diffs.append(None)
        
        # 差分が 2^{k-j} になるパターンを確認
        print(f"  r={r:3d}: diffs (j=1..{min(k,6)-1}): {diffs}")

# 理論的帰結:
# j=1: diff = 2^{k-1}
# j=2 (if both still ≡ 3 mod 4): diff = 2^{k-2}
# j=3: diff = 2^{k-3}
# ...
# j=k-2: diff = 2^1 = 2
# j=k-1: diff = 1 → mod 4 パリティが分岐!

print()
print("=" * 70)
print("差分収縮の帰結: j ステップ後の差分 = 2^{k-1-j}?")
print("=" * 70)

# 連続上昇（T^j(r)≡3 mod 4 for all j < k-1）の場合:
# 差分は j ステップごとに半分になる？
# NOT exactly. 差分の増大/縮小パターンは (3/2)^j * 2^{k-1} を考える必要

# T^j(r+2^k) - T^j(r) を Δ_j とする
# Δ_0 = 2^k
# v2=1の場合: Δ_1 = (3*Δ_0)/2 mod 2^k = 3*2^{k-1} mod 2^k = 2^{k-1}
# Wait, Δ_1 = 3*2^{k-1} (exact), mod 2^k = 2^{k-1}
# Δ_1 exact = 3*2^{k-1}
# v2=1 continued: Δ_2 = (3*Δ_1)/2 = 3*3*2^{k-2}/2 = ... 
# No: Δ_2 = (3*(T(r)+3*2^{k-1})+1)/2 - (3*T(r)+1)/2 = 9*2^{k-2}
# Δ_2 exact = 9*2^{k-2}, mod 2^k = 2^{k-2}
# Δ_3 exact = 27*2^{k-3}, mod 2^k = 27*2^{k-3} mod 2^k
#   27*2^{k-3} = (32-5)*2^{k-3} = 2^k - 5*2^{k-3}
#   mod 2^k = -5*2^{k-3} mod 2^k = 2^k - 5*2^{k-3}
#   Hmm, that's not 2^{k-3}

# Let me just verify empirically
print("\nΔ_j の厳密値 (連続上昇の場合):")
for k in range(5, 10):
    mod = 2**k
    # r = 2^k - 1 は全ビット1 → 連続上昇
    r = mod - 1
    r2 = r + mod
    
    cur_r = r
    cur_r2 = r2
    print(f"\nk={k}, r={r} (= 2^k - 1):")
    for j in range(1, k):
        cur_r = (3 * cur_r + 1) // 2  # T operation (v2=1 since we're in all-1s pattern)
        cur_r2 = (3 * cur_r2 + 1) // 2
        delta = cur_r2 - cur_r
        delta_mod = delta % mod
        # Factor out powers of 2
        v2_delta = v2(delta) if delta != 0 else '?'
        odd_part = delta >> v2(delta) if isinstance(v2_delta, int) else '?'
        print(f"  j={j}: Δ = {delta} = {odd_part} * 2^{v2_delta}, mod 2^k = {delta_mod}")

# Key insight: Δ_j = 3^j * 2^{k-j}
# v2(Δ_j) = k - j (decreasing)
# odd part = 3^j
# mod 2^k: 3^j * 2^{k-j} mod 2^k
# For j < k: v2(Δ_j) = k-j > 0
# For j = k: v2(Δ_k) = 0 → Δ_k is odd → mod 4 could differ!

print()
print("=" * 70)
print("核心定理: Δ_j = 3^j * 2^{k-j} (連続v2=1の場合)")
print("j = k-1 で Δ_{k-1} = 3^{k-1} * 2 → v2 = 1")
print("j = k-2 で Δ_{k-2} = 3^{k-2} * 4 → mod 4 ≡ 0 → 同一mod4")
print("=" * 70)

# 最も重要:
# Δ_{k-2} = 3^{k-2} * 4 → mod 4 = 0 → T^{k-2}(r) ≡ T^{k-2}(r+2^k) (mod 4)
# Δ_{k-1} = 3^{k-1} * 2 → mod 4 = 2 → T^{k-1}(r) と T^{k-1}(r+2^k) は mod 4 で差 2
# つまり一方が mod 4 ≡ 1, 他方が mod 4 ≡ 3 (差が2)

# しかし T^j は常に奇数なので、mod 4 は 1 か 3
# 差が 2 mod 4 なら: 一方が 1, 他方が 3!
# → 片方は下降確定 (mod 4 ≡ 1)、片方は上昇 (mod 4 ≡ 3)
# → これが排他性!

print("\n*** 大発見 ***")
print("連続上昇パス (全ステップで v2=1) に限れば:")
print("Δ_j = 3^j * 2^{k-j}")
print()
print("ステップ j = k-2 のとき:")
print("  Δ_{k-2} mod 4 = 3^{k-2} * 4 mod 4 = 0")
print("  → T^{k-2}(r) と T^{k-2}(r+2^k) は mod 4 が同じ")
print()
print("ステップ j = k-1 のとき:")
print("  Δ_{k-1} = 3^{k-1} * 2")
print("  Δ_{k-1} mod 4 = 2 (since 3^{k-1} is odd)")
print("  → T^{k-1}(r) と T^{k-1}(r+2^k) の mod 4 差は 2")
print("  → T^{k-1}(r) ≡ 1 mod 4 かつ T^{k-1}(r+2^k) ≡ 3 mod 4、またはその逆")
print("  → 片方は必ず下降確定! (mod 4 ≡ 1)")
print()
print("これが both_survive = 0 の核心メカニズム!")

# 検証: 実際に k-1 ステップ追跡で排他性が成立するか
print()
print("=" * 70)
print("検証: k-1 ステップ追跡での排他性")
print("=" * 70)

for k in range(3, 13):
    mod = 2**k
    # r = 2^{k+1}-1 mod 2^{k+1} のリフトペア
    # 全ビット1パターンのみ検証
    r = mod - 1  # r ≡ -1 ≡ 2^k - 1 (mod 2^k)
    r_low = r
    r_high = r + mod
    
    # k-1 ステップ追跡
    cur_low = r_low
    cur_high = r_high
    
    all_v2_1_low = True
    all_v2_1_high = True
    
    for j in range(k-1):
        if cur_low % 4 != 3:
            all_v2_1_low = False
            break
        if cur_high % 4 != 3:
            all_v2_1_high = False
            break
        cur_low = (3 * cur_low + 1) // 2
        cur_high = (3 * cur_high + 1) // 2
    
    low_mod4 = cur_low % 4
    high_mod4 = cur_high % 4
    exclusive = (low_mod4 == 1 and high_mod4 == 3) or (low_mod4 == 3 and high_mod4 == 1)
    
    print(f"k={k:2d}: r={r_low}, r+2^k={r_high}: after {k-1} steps: "
          f"low mod4={low_mod4}, high mod4={high_mod4}, exclusive={exclusive}, "
          f"all_v2_1: low={all_v2_1_low}, high={all_v2_1_high}")

