"""
探索179: 一般乗法公式 2^{S_k} * T^k(n) = 3^k * n + C_k の数値検証

目標:
  consecutiveAscents不要の完全一般化された乗法公式:
    2^{S_k(n)} * T^k(n) = 3^k * n + C_k(n)

  ここで:
    S_k(n) = Σ_{i=0}^{k-1} v2(3 * T^i(n) + 1)  (合計 2-adic付値)
    C_0(n) = 0
    C_{k+1}(n) = 3 * C_k(n) + 2^{S_k(n)}         (漸化式)

  S_0 = 0
  S_{k+1} = S_k + v2(3 * T^k(n) + 1)

  既存の公式 (consecutiveAscents版) との違い:
    既存: v2 は常に 1 (mod 4 ≡ 3 のとき)、S_k = k、C_k = ascentConst k = 3^k - 2^k
    一般: v2 は可変、S_k は一般的な和、C_k は n 依存

  帰納ステップ:
    2^{S_{k+1}} * T^{k+1}(n)
    = 2^{S_k + v_k} * T(T^k(n))           where v_k = v2(3*T^k(n)+1)
    = 2^{S_k} * (2^{v_k} * T(T^k(n)))
    = 2^{S_k} * (3*T^k(n) + 1)            by syracuse_mul_pow_v2
    = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}
    = 3 * (3^k * n + C_k) + 2^{S_k}      by IH
    = 3^{k+1} * n + (3 * C_k + 2^{S_k})
    = 3^{k+1} * n + C_{k+1}
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function"""
    m = 3 * n + 1
    return m // (2 ** v2(m))

def syracuse_iter(k, n):
    """Syracuse iteration"""
    for _ in range(k):
        n = syracuse(n)
    return n

def compute_S_k(n, k):
    """S_k(n) = sum of v2(3*T^i(n)+1) for i=0..k-1"""
    s = 0
    cur = n
    for i in range(k):
        s += v2(3 * cur + 1)
        cur = syracuse(cur)
    return s

def compute_C_k(n, k):
    """C_k(n) by recurrence: C_0=0, C_{k+1}=3*C_k+2^{S_k}"""
    if k == 0:
        return 0
    # We compute iteratively
    c = 0
    s = 0
    cur = n
    for i in range(k):
        vi = v2(3 * cur + 1)
        c = 3 * c + (2 ** s)  # C_{i+1} = 3*C_i + 2^{S_i}
        s += vi  # S_{i+1} = S_i + v_i
        cur = syracuse(cur)
    return c

print("=" * 70)
print("数値検証: 2^{S_k(n)} * T^k(n) = 3^k * n + C_k(n)")
print("=" * 70)

test_cases = [
    (3, 1), (3, 2), (3, 3), (3, 5),
    (5, 1), (5, 2), (5, 3),
    (7, 1), (7, 2), (7, 3), (7, 4),
    (9, 1), (9, 2), (9, 3),
    (11, 1), (11, 2),
    (13, 1), (13, 2),
    (15, 1), (15, 2), (15, 3), (15, 4),
    (27, 1), (27, 2), (27, 5), (27, 10),
    (31, 1), (31, 2), (31, 3), (31, 4), (31, 5),
]

all_pass = True
for n, k in test_cases:
    Tk = syracuse_iter(k, n)
    Sk = compute_S_k(n, k)
    Ck = compute_C_k(n, k)
    lhs = (2 ** Sk) * Tk
    rhs = (3 ** k) * n + Ck
    passed = (lhs == rhs)
    if not passed:
        all_pass = False
    print(f"n={n:3d}, k={k:2d}: T^k={Tk:6d}, S_k={Sk:3d}, C_k={Ck:8d}, "
          f"2^S_k*T^k={lhs:10d}, 3^k*n+C_k={rhs:10d}, {'OK' if passed else 'FAIL'}")

print(f"\n全テスト: {'PASS' if all_pass else 'FAIL'}")

# consecutiveAscents の特殊ケース検証
print("\n" + "=" * 70)
print("特殊ケース: n % 4 = 3 連続上昇のとき S_k = k, C_k = 3^k - 2^k")
print("=" * 70)

for n in [3, 7, 15, 31, 63]:
    for k in range(1, 6):
        Tk = syracuse_iter(k, n)
        Sk = compute_S_k(n, k)
        Ck = compute_C_k(n, k)
        ascent_const = 3**k - 2**k
        is_ascent = (Sk == k and Ck == ascent_const)
        print(f"n={n:3d}, k={k}: S_k={Sk:3d} (=k? {Sk==k}), "
              f"C_k={Ck:8d} (=3^k-2^k? {Ck==ascent_const})")

# C_k の別表現を検証
print("\n" + "=" * 70)
print("C_k(n) の閉形式: C_k + 2^{S_k} = ?")
print("=" * 70)
for n in [3, 7, 9, 11, 15, 27]:
    for k in range(1, 6):
        Sk = compute_S_k(n, k)
        Ck = compute_C_k(n, k)
        sum_val = Ck + 2**Sk
        factor = sum_val / (3**k) if 3**k > 0 else None
        print(f"n={n:3d}, k={k}: C_k+2^S_k = {sum_val:10d}, "
              f"3^k*(n+1) = {3**k*(n+1):10d}, "
              f"ratio = {factor:.4f}, eq? {sum_val == 3**k * (n+1)}")

# S_kの漸化式の確認
print("\n" + "=" * 70)
print("S_k の漸化式: S_{k+1} = S_k + v2(3*T^k(n)+1)")
print("=" * 70)
for n in [3, 7, 9, 27]:
    print(f"\nn={n}:")
    cur = n
    s = 0
    for i in range(8):
        vi = v2(3 * cur + 1)
        print(f"  i={i}: T^i(n)={cur:6d}, v2(3*T^i+1)={vi}, S_{i}={s}, S_{i+1}={s+vi}")
        s += vi
        cur = syracuse(cur)

# 帰納ステップの核心を検証
print("\n" + "=" * 70)
print("帰納ステップ検証: 2^{v_k}*T(T^k(n)) = 3*T^k(n)+1")
print("(これは syracuse_mul_pow_v2)")
print("=" * 70)
for n in [3, 7, 9, 11, 27]:
    for k in range(5):
        Tk = syracuse_iter(k, n)
        vk = v2(3 * Tk + 1)
        TTk = syracuse(Tk)
        lhs = 2**vk * TTk
        rhs = 3 * Tk + 1
        print(f"n={n:3d}, k={k}: T^k={Tk:6d}, v_k={vk}, "
              f"2^v_k*T(T^k)={lhs:8d}, 3*T^k+1={rhs:8d}, eq? {lhs==rhs}")
