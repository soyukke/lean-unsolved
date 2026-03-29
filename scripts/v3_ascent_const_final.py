"""
v3(3^k - 2^k) と サイクル方程式: 最終まとめスクリプト

確定事実と新しい発見を整理する。
"""
import sys
sys.set_int_max_str_digits(10000)

import math
from collections import defaultdict

def vp(n, p):
    if n == 0: return float('inf')
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v

def multiplicative_order(a, m):
    if math.gcd(a, m) != 1:
        return None
    order = 1
    power = a % m
    while power != 1:
        power = (power * a) % m
        order += 1
        if order > m:
            return None
    return order

def factorize(n):
    if n <= 1: return {n: 1} if n == 1 else {}
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

# === 結論1: v3(ascentConst(k)) = v3(3^k - 2^k) = 0 ===
print("=" * 70)
print("結論1: v3(3^k - 2^k) = 0 for all k >= 1")
print("=" * 70)
print("""
証明:
  3^k - 2^k ≡ 0 - 2^k ≡ -2^k (mod 3)
  gcd(2, 3) = 1 なので 2^k ≢ 0 (mod 3)
  よって 3^k - 2^k ≢ 0 (mod 3)
  従って v3(3^k - 2^k) = 0

これは ascentConst(k) = 3^k - 2^k が 3 で割り切れないことを意味する。
Lean での形式化候補:
  theorem v3_ascentConst_eq_zero (k : Nat) (hk : k >= 1) :
    v3 (ascentConst k) = 0
""")

# === 結論2: v3(2^s - 3^p) = 0 (p >= 1) ===
print("=" * 70)
print("結論2: v3(2^s - 3^p) = 0 for all s, p with p >= 1")
print("=" * 70)
print("""
証明:
  2^s - 3^p ≡ 2^s - 0 ≡ 2^s (mod 3)
  gcd(2, 3) = 1 なので 2^s ≢ 0 (mod 3)
  よって v3(2^s - 3^p) = 0
""")

# === 結論3: サイクル方程式の v3 帰結 ===
print("=" * 70)
print("結論3: サイクル方程式の3-adic帰結")
print("=" * 70)
print("""
サイクル方程式: n(2^s - 3^p) = Σ_{i=0}^{p-1} 3^i * 2^{a_i}

v3 で評価:
  v3(LHS) = v3(n) + v3(2^s - 3^p) = v3(n)  [∵ 結論2]
  v3(RHS) = v3(2^{a_0} + 3*(...)) = 0       [∵ 2^{a_0}は3と互いに素]

よって v3(n) = 0。

これは「コラッツサイクル上の奇数は3の倍数でない」という既知結果の再導出。
(Terras (1976), Lagarias (1985) 等で知られる)
""")

# === 結論4: mod 9 での詳細制約 ===
print("=" * 70)
print("結論4: mod 9 でのサイクル方程式制約")
print("=" * 70)

ord_9 = multiplicative_order(2, 9)
print(f"ord_9(2) = {ord_9}")
print(f"2^s mod 9 の周期: {[pow(2, s, 9) for s in range(ord_9)]}")

# p >= 2: LHS ≡ n*2^s mod 9, RHS ≡ 2^{a_0} + 3*2^{a_1} mod 9
rhs_possible = set()
for a0 in range(ord_9):
    for a1 in range(ord_9):
        val = (pow(2, a0, 9) + 3 * pow(2, a1, 9)) % 9
        rhs_possible.add(val)

print(f"\n[p>=2の場合]")
print(f"RHS mod 9 の可能な値: {sorted(rhs_possible)}")
print(f"= 3で割れない非零値全体 {{1,2,4,5,7,8}} と一致!")
print("結論: mod 9 では追加の排除制約なし (RHS が全coprime-to-3値を取る)")

# === 結論5: v5 での新しい制約 ===
print("\n" + "=" * 70)
print("結論5: 5-adic解析によるサイクル制約")
print("=" * 70)

# v5(2^s - 3^p) > 0 iff 2^s ≡ 3^p mod 5
# ord_5(2) = 4, ord_5(3) = 4
# 2^s mod 5: [1,2,4,3] (period 4)
# 3^p mod 5: [1,3,4,2] (period 4)
# 2^s ≡ 3^p mod 5:
#   s≡0: 1, p≡0: 1 → match
#   s≡1: 2, p≡3: 2 → match
#   s≡2: 4, p≡2: 4 → match
#   s≡3: 3, p≡1: 3 → match

print("v5(2^s - 3^p) > 0 iff (s mod 4, p mod 4) in:")
matches = []
for s in range(4):
    for p in range(4):
        if pow(2, s, 5) == pow(3, p, 5):
            matches.append((s, p))
            print(f"  s≡{s}, p≡{p} mod 4  (2^s≡3^p≡{pow(2,s,5)} mod 5)")

print(f"\n制約: s ≡ -p mod 4 (i.e., s+p ≡ 0 mod 4 のとき v5(2^s-3^p)=0)")
print("(ただし p≡0→s≡0, p≡1→s≡3, p≡2→s≡2, p≡3→s≡1)")
print(f"つまり s+p ≡ 0 mod 4 かつ s≡0,p≡0; s+p≡0 mod 4 です。")

# 検証
print("\n検証:")
for p_val in range(1, 20):
    s_val = int(p_val * math.log2(3)) + 1
    for s in range(s_val, s_val + 4):
        diff = 2**s - 3**p_val
        if diff > 0:
            v = vp(diff, 5)
            sp_mod4 = (s + p_val) % 4
            expected = 1 if sp_mod4 == 0 else 0
            if (v > 0) != (expected > 0):
                print(f"  [不一致] s={s}, p={p_val}: v5={v}, (s+p)mod4={sp_mod4}")

# === 結論6: ascentConst の素因数分解構造 ===
print("\n" + "=" * 70)
print("結論6: ascentConst(k) = 3^k - 2^k の素因数構造")
print("=" * 70)

print(f"\n素因数分解とZsygmondy原始因子:")
prev_primes = set()
for k in range(1, 31):
    ac = 3**k - 2**k
    factors = factorize(ac)
    primitive = set(factors.keys()) - prev_primes
    prev_primes |= set(factors.keys())
    factor_str = " * ".join(f"{p}^{e}" if e > 1 else str(p)
                           for p, e in sorted(factors.items()))
    prim_str = str(sorted(primitive)) if primitive else "NONE"
    print(f"  k={k:2d}: {factor_str:>40}  primitive={prim_str}")

# === 結論7: vp(3^k - 2^k) の一般公式 ===
print("\n" + "=" * 70)
print("結論7: vp(3^k - 2^k) の公式 (p >= 5)")
print("=" * 70)

print("""
素数 q >= 5 に対して:
  r_q = 3 * 2^{-1} mod q  (= 3 * (q+1)/2 mod q if q odd)
  d_q = ord_q(r_q) = ord_q(3/2 mod q)

定理: vq(3^k - 2^k) > 0 iff d_q | k

証明:
  3^k - 2^k ≡ 0 mod q
  iff 3^k ≡ 2^k mod q
  iff (3 * 2^{-1})^k ≡ 1 mod q  [∵ gcd(2,q)=1]
  iff d_q | k
""")

print("各素数 q の d_q:")
for q in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    inv2 = pow(2, q-2, q)
    ratio = (3 * inv2) % q
    d = multiplicative_order(ratio, q)
    print(f"  q={q:2d}: 3/2 mod q = {ratio:2d}, d_q = ord_q(3/2) = {d}")

# === 結論8: LTE の適用不可能性と代替公式 ===
print("\n" + "=" * 70)
print("結論8: Lifting the Exponent Lemma の非適用性")
print("=" * 70)

print("""
LTE (奇素数版): p | (a-b) かつ p ∤ a, p ∤ b のとき
  vp(a^n - b^n) = vp(a-b) + vp(n)

a=3, b=2, a-b=1 の場合:
  p | 1 を満たす素数 p は存在しない
  よって LTE は 3^k - 2^k に直接適用不可能

代替: q | (3^{d_q} - 2^{d_q}) を満たす最小の d_q に対して
LTE を「a = 3^{d_q}, b = 2^{d_q}」で適用:
  k = d_q * m のとき
  vq(3^k - 2^k) = vq(3^{d_q*m} - 2^{d_q*m})
  = vq((3^{d_q})^m - (2^{d_q})^m)

  ここで q | (3^{d_q} - 2^{d_q}) なので LTE 適用可能:
  = vq(3^{d_q} - 2^{d_q}) + vq(m)
  (ただし q ∤ 3^{d_q}, q ∤ 2^{d_q} が必要 → gcd(q,6)=1 で保証)
""")

# 検証
print("検証: q=5, d_5=2")
for m in range(1, 16):
    k = 2 * m
    actual = vp(3**k - 2**k, 5)
    base_v = vp(3**2 - 2**2, 5)  # vp(5, 5) = 1
    predicted = base_v + vp(m, 5)
    match = "OK" if actual == predicted else "MISMATCH"
    print(f"  k={k:3d} (m={m:2d}): v5 = {actual}, predicted = {base_v}+{vp(m,5)} = {predicted}  [{match}]")

print("\n検証: q=7, d_7=6")
for m in range(1, 10):
    k = 6 * m
    actual = vp(3**k - 2**k, 7)
    base_v = vp(3**6 - 2**6, 7)
    predicted = base_v + vp(m, 7)
    match = "OK" if actual == predicted else "MISMATCH"
    print(f"  k={k:3d} (m={m:2d}): v7 = {actual}, predicted = {base_v}+{vp(m,7)} = {predicted}  [{match}]")

# === 結論9: サイクル方程式への5-adic応用 ===
print("\n" + "=" * 70)
print("結論9: 5-adic制約のサイクル排除への応用")
print("=" * 70)

print("""
サイクル方程式: n(2^s - 3^p) = Σ 3^i * 2^{a_i}

v5 で評価:
  v5(LHS) = v5(n) + v5(2^s - 3^p)
  v5(RHS) = v5(Σ 3^i * 2^{a_i})

v5(2^s - 3^p) は s+p ≡ 0 mod 4 のとき > 0、それ以外で 0。

case 1: s+p ≢ 0 mod 4 → v5(2^s-3^p)=0
  → v5(n) = v5(RHS)
  → n の5-adic valuationが右辺で決まる

case 2: s+p ≡ 0 mod 4 → v5(2^s-3^p) >= 1
  → v5(n) + v5(2^s-3^p) = v5(RHS)
  → n の5で割れる回数が制約される

RHS の v5 を分析:
  RHS = Σ_{i=0}^{p-1} 3^i * 2^{a_i}
  v5(3^i * 2^{a_i}) = 0 (gcd(6,5)=1)
  よって各項は 5 と互いに素だが、和は 5 で割れうる。

p=2 の場合: RHS = 2^{a_0} + 3*2^{a_1}
  v5(RHS) = v5(2^{a_0} + 3*2^{a_1}) = v5(2^{a_1}(2^d + 3))  where d=a_0-a_1
  = v5(2^d + 3)
  > 0 iff d ≡ 1 mod 4
""")

# p=2 のサイクル条件まとめ
print("p=2 のサイクル: n(2^s - 9) = 2^{a_0} + 3*2^{a_1}")
print("  s >= 4 (2^s > 9)")
print("  a_0 = s - a_1 (a_0 + a_1 = s)")

# 実際に p=2 のサイクルは存在するか確認
print("\np=2 サイクル候補の数値チェック:")
for s in range(4, 30):
    denom = 2**s - 9
    if denom <= 0:
        continue
    for a1 in range(s):
        a0 = s - 1  # 最大の a_0
        # 実際のサイクルでは a_i は軌道で決まるので自由パラメータではない
        # 簡単化: a_0 + a_1 = s の制約はない。正しくは a_0, a_1 は独立
    # n = (2^{a_0} + 3*2^{a_1}) / (2^s - 9)
    # n が正の奇数整数になる (a_0, a_1) を探す
    found = False
    for a0 in range(1, s + 5):
        for a1 in range(0, a0):
            rhs = 2**a0 + 3 * 2**a1
            if rhs % denom == 0:
                n = rhs // denom
                if n > 0 and n % 2 == 1:
                    print(f"  s={s}: n={n}, a0={a0}, a1={a1}, denom={denom}")
                    # 検証: syracuseIter 2 n = n ?
                    # Syracuse step 1: (3n+1)/2^{v2(3n+1)}
                    m = 3*n + 1
                    v = vp(m, 2)
                    n1 = m // (2**v)
                    # Syracuse step 2: (3*n1+1)/2^{v2(3*n1+1)}
                    m2 = 3*n1 + 1
                    v2_val = vp(m2, 2)
                    n2 = m2 // (2**v2_val)
                    actual_s = v + v2_val
                    cycle = (n2 == n)
                    print(f"    T(n)={n1}, T^2(n)={n2}, total_s={actual_s}, cycle={cycle}")
                    found = True
                    break
        if found:
            break

# === 最終サマリー ===
print("\n" + "=" * 70)
print("最終サマリー")
print("=" * 70)

print("""
【確定した数学的事実】

1. v3(ascentConst(k)) = v3(3^k - 2^k) = 0 for all k >= 1
   (ascentConst(k) は 3 で割り切れない)

2. v3(2^s - 3^p) = 0 for all p >= 1
   (サイクル方程式の「分母」は 3 で割り切れない)

3. サイクル方程式の v3 帰結: サイクル上の奇数 n は v3(n) = 0
   (既知結果の 3-adic 再導出)

4. ascentConst(k) mod 3 = (-2^k) mod 3
   - k 奇数: ≡ 1 mod 3
   - k 偶数: ≡ 2 mod 3

5. ascentConst(k) mod 9 は 2^k mod 9 の周期6パターンに従う:
   k mod 6: [0→8, 1→7, 2→5, 3→1, 4→2, 5→4] (mod 9)

【部分的に新しい発見】

6. vq(3^k - 2^k) の一般公式 (q >= 5, gcd(q,6)=1):
   d_q = ord_q(3/2 mod q) とすると
   vq(3^k - 2^k) > 0 iff d_q | k
   d_q | k のとき: vq(3^k - 2^k) = vq(3^{d_q} - 2^{d_q}) + vq(k/d_q)

7. v5(2^s - 3^p) > 0 iff s + p ≡ 0 mod 4
   (5-adic でのサイクルパラメータ制約)

8. mod 9 ではサイクル方程式の追加排除は得られない
   (RHS mod 9 が {1,2,4,5,7,8} の全値を取りうる)

【行き止まり】

- 3-adic 解析だけでは新しいサイクル排除制約が得られない
  (v3 が常に 0 なので情報量がない)
- mod 9, mod 27 でも右辺が全ての coprime-to-3 値を取るため排除不可能
- 5-adic の制約 (s+p mod 4) は必要条件だが十分条件ではない
""")
