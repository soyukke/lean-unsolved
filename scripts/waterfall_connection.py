"""
Waterfall公式とconsecutiveAscentsの接続: 詳細分析

核心的な問題:
1. mersenne_orbit_mul → waterfall_formula (T^k(2^m-1) = 3^k * 2^{m-k} - 1) の導出
2. waterfall_formula → mersenne_consecutive_ascents の導出
3. 一般 hensel_attrition の帰納法ステップの分析
"""

def v2(n):
    if n == 0: return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

print("=" * 70)
print("A. mersenne_orbit_mul → waterfall_formula の詳細導出")
print("=" * 70)

print("""
既存: mersenne_orbit_mul (m k : N) (hm : m >= 1) (hk : k+1 <= m) :
  2^k * syracuseIter k (2^m - 1) + 2^k = 3^k * 2^m

目標: waterfall_formula:
  syracuseIter k (2^m - 1) = 3^k * 2^{m-k} - 1

導出:
  2^k * T^k + 2^k = 3^k * 2^m
  2^k * (T^k + 1) = 3^k * 2^m
  T^k + 1 = 3^k * 2^m / 2^k = 3^k * 2^{m-k}
  T^k = 3^k * 2^{m-k} - 1

Lean での実装:
  hpow_pos : 2^k > 0
  h_mul : 2^k * (T^k + 1) = 3^k * 2^m  [from mersenne_orbit_mul]
  h_cancel : T^k + 1 = 3^k * 2^{m-k}   [Nat.eq_of_mul_eq_mul_left]

  ただし 3^k * 2^m = 2^k * (3^k * 2^{m-k}) を示す必要あり:
  2^k * (3^k * 2^{m-k}) = 3^k * (2^k * 2^{m-k}) = 3^k * 2^m
  ← pow_add: 2^k * 2^{m-k} = 2^{k+(m-k)} = 2^m (when k <= m)

  最後に T^k = 3^k * 2^{m-k} - 1 は
  T^k + 1 = 3^k * 2^{m-k} から omega で得られる

  前提: 3^k * 2^{m-k} >= 1 (常に成立)
""")

# 数値確認
print("数値確認: 2^k * (3^k * 2^{m-k}) = 3^k * 2^m")
for m in range(2, 8):
    for k in range(0, m):
        lhs = 2**k * (3**k * 2**(m-k))
        rhs = 3**k * 2**m
        print(f"  m={m}, k={k}: {lhs} = {rhs}  {'OK' if lhs == rhs else 'FAIL'}")

print("\n" + "=" * 70)
print("B. waterfall_formula → mersenne_consecutive_ascents")
print("=" * 70)

print("""
目標: consecutiveAscents (2^m - 1) (m-1)  for m >= 2

定義: ∀ i < m-1, syracuse(syracuseIter i (2^m-1)) > syracuseIter i (2^m-1)

waterfall_formula: syracuseIter i (2^m-1) = 3^i * 2^{m-i} - 1

i < m-1 ⟹ m-i >= 2 ⟹ 4 | 3^i * 2^{m-i}
⟹ (3^i * 2^{m-i} - 1) mod 4 = 3
⟹ syracuse(x) > x (by syracuse_gt_of_mod4_eq3)

Lean での実装:
  intro i hi  -- i < m-1
  rw [waterfall_formula の右展開]
  -- 正確には syracuseIter_succ_right と waterfall_formula を使って
  -- syracuse(syracuseIter i (2^m-1)) = syracuseIter (i+1) (2^m-1)
  -- = 3^{i+1} * 2^{m-i-1} - 1
  -- syracuseIter i (2^m-1) = 3^i * 2^{m-i} - 1
  -- 3^{i+1} * 2^{m-i-1} - 1 > 3^i * 2^{m-i} - 1
  -- ⟺ 3^{i+1} * 2^{m-i-1} > 3^i * 2^{m-i}
  -- ⟺ 3 * 3^i * 2^{m-i-1} > 3^i * 2 * 2^{m-i-1}
  -- ⟺ 3 > 2 ✓

  あるいは mod 4 条件を使う方が簡単:
  - iter_i = 3^i * 2^{m-i} - 1
  - m-i ≥ 2 (since i < m-1)
  - 4 | 3^i * 2^{m-i}  (since m-i ≥ 2)
  - iter_i mod 4 = 3
  - syracuse_gt_of_mod4_eq3 iter_i ... : syracuse iter_i > iter_i
""")

# 不等式の検証: 3^{i+1} * 2^{m-i-1} > 3^i * 2^{m-i}
print("不等式の検証: T^{i+1} > T^i")
for m in range(3, 8):
    for i in range(0, m-1):
        ti = 3**i * 2**(m-i) - 1
        ti1 = 3**(i+1) * 2**(m-i-1) - 1
        mod4_ti = ti % 4
        print(f"  m={m}, i={i}: T^i={ti} (mod4={mod4_ti}), T^{{i+1}}={ti1}, "
              f"ascending={'YES' if ti1 > ti else 'NO'}")

print("\n" + "=" * 70)
print("C. 一般 hensel_attrition 帰納ステップの詳細分析")
print("=" * 70)

print("""
目標: consecutiveAscents n (k+1) → n mod 2^{k+2} = 2^{k+2} - 1
  前提: consecutiveAscents n k → n mod 2^{k+1} = 2^{k+1} - 1 (帰納仮説)

n mod 2^{k+1} = 2^{k+1} - 1 のとき:
  n = 2^{k+1} * q + (2^{k+1} - 1)  for some q
  n mod 2^{k+2} は q の偶奇で決まる:
    q 偶数: n mod 2^{k+2} = 2^{k+1} - 1
    q 奇数: n mod 2^{k+2} = 2^{k+2} - 1

k+1 回目の上昇条件:
  syracuse(syracuseIter k n) > syracuseIter k n
  ⟺ syracuseIter k n mod 4 = 3

乗法公式: 2^k * syracuseIter k n = 3^k * n + ascentConst(k) = 3^k * n + 3^k - 2^k
  = 3^k * (n+1) - 2^k

syracuseIter k n = (3^k * (n+1) - 2^k) / 2^k = 3^k * (n+1) / 2^k - 1

n+1 = 2^{k+1} * q + 2^{k+1} = 2^{k+1} * (q+1)

syracuseIter k n = 3^k * 2^{k+1} * (q+1) / 2^k - 1 = 3^k * 2 * (q+1) - 1

mod 4 分析:
  3^k * 2 * (q+1) - 1 mod 4
  = 2 * 3^k * (q+1) - 1 mod 4

  3^k mod 2 = 1 (always odd)
  2 * 3^k mod 4 = 2

  2 * (q+1) mod 4:
    q+1 偶数 (q 奇数): 2 * (q+1) ≡ 0 (mod 4)
    q+1 奇数 (q 偶数): 2 * (q+1) ≡ 2 (mod 4)

  実際: 2 * 3^k * (q+1) mod 4
  = (2 * 3^k mod 4) * ((q+1) mod ?) ... これは乗法ではないので注意

  直接計算:
  syracuseIter k n = 2 * 3^k * (q+1) - 1

  q 偶数のとき (n mod 2^{k+2} = 2^{k+1} - 1):
    q+1 は奇数
    2 * 3^k * (q+1) は偶数 (2の倍数だが4の倍数ではない可能性)
    実際 2 * 3^k * (odd) = 2 * (odd) なので mod 4 は 2
    2 * 3^k * (q+1) - 1 mod 4 = 2 - 1 = 1

  q 奇数のとき (n mod 2^{k+2} = 2^{k+2} - 1):
    q+1 は偶数
    q+1 = 2 * r for some r
    2 * 3^k * 2 * r = 4 * 3^k * r
    mod 4: 0
    4 * 3^k * r - 1 mod 4 = -1 = 3

結論:
  T^k(n) mod 4 = 1 ⟺ q 偶数 ⟺ n mod 2^{k+2} = 2^{k+1} - 1
  T^k(n) mod 4 = 3 ⟺ q 奇数 ⟺ n mod 2^{k+2} = 2^{k+2} - 1

∴ k+1 回目が上昇 ⟺ T^k(n) mod 4 = 3 ⟺ n mod 2^{k+2} = 2^{k+2} - 1

これが一般 hensel_attrition の帰納ステップ！
""")

# 数値検証
print("帰納ステップの数値検証:")
for k in range(1, 8):
    print(f"\nk={k}:")
    # n = 2^{k+1} * q + 2^{k+1} - 1 の形の数を調べる
    modulus_k = 2**(k+1)
    modulus_k1 = 2**(k+2)
    for q in range(0, 8):
        n = modulus_k * q + modulus_k - 1
        if n < 1 or n % 2 == 0:
            continue
        # check consecutiveAscents
        has_k_ascents = True
        current = n
        for i in range(k):
            next_val = syracuse(current)
            if next_val <= current:
                has_k_ascents = False
                break
            current = next_val

        if not has_k_ascents:
            continue

        # T^k(n)
        tk = syracuse_iter(k, n)
        tk_mod4 = tk % 4
        n_mod_k2 = n % modulus_k1

        # k+1 回目の上昇チェック
        tk1_ascending = syracuse(tk) > tk

        expected_q_parity = "odd" if n_mod_k2 == modulus_k1 - 1 else "even"
        actual_q_parity = "odd" if q % 2 == 1 else "even"

        print(f"  n={n:6d}, q={q}, q_parity={actual_q_parity}, "
              f"n mod 2^{k+2}={n_mod_k2}, "
              f"T^{k}={tk:8d}, T^{k} mod4={tk_mod4}, "
              f"asc_{k+1}={tk1_ascending}")

print("\n" + "=" * 70)
print("D. 帰納ステップの核心等式の検証")
print("=" * 70)

print("""
核心: n mod 2^{k+1} = 2^{k+1} - 1 のとき (n+1 = 2^{k+1}*(q+1))

T^k(n) = 2 * 3^k * (q+1) - 1

これを syracuse_iter_alt_formula:
  2^k * T^k(n) + 2^k = 3^k * (n+1)
  T^k(n) = (3^k * (n+1) - 2^k) / 2^k
  = (3^k * 2^{k+1} * (q+1) - 2^k) / 2^k
  = 3^k * 2 * (q+1) - 1
  = 2 * 3^k * (q+1) - 1
""")

for k in range(1, 6):
    print(f"\nk={k}:")
    modulus = 2**(k+1)
    for q in range(0, 10):
        n = modulus * q + modulus - 1
        if n < 1 or n % 2 == 0:
            continue

        # Check if consecutiveAscents n k holds
        has_ascents = True
        current = n
        for i in range(k):
            next_v = syracuse(current)
            if next_v <= current:
                has_ascents = False
                break
            current = next_v

        if not has_ascents:
            continue

        tk = syracuse_iter(k, n)
        expected_formula = 2 * 3**k * (q+1) - 1
        match = "OK" if tk == expected_formula else "FAIL"
        print(f"  q={q:2d}, n={n:6d}: T^{k}={tk:8d}, 2*3^{k}*(q+1)-1={expected_formula:8d}  [{match}]")

print("\n" + "=" * 70)
print("E. 形式化に必要な主要補題リスト")
print("=" * 70)

print("""
=== 優先度1: waterfall_formula (容易) ===

theorem waterfall_formula (m k : N) (hm : m >= 1) (hk : k + 1 <= m) :
    syracuseIter k (2^m - 1) = 3^k * 2^{m-k} - 1

証明: mersenne_orbit_mul から
  2^k * (T^k + 1) = 3^k * 2^m = 2^k * (3^k * 2^{m-k})
  T^k + 1 = 3^k * 2^{m-k}
  T^k = 3^k * 2^{m-k} - 1

=== 優先度2: mersenne_consecutive_ascents (中程度) ===

theorem mersenne_consecutive_ascents (m : N) (hm : m >= 2) :
    consecutiveAscents (2^m - 1) (m - 1)

証明: waterfall_formula + mod 4 条件
  i < m-1 のとき T^i = 3^i * 2^{m-i} - 1, m-i >= 2 なので mod4 = 3

=== 優先度3: waterfall_step (中程度) ===

theorem waterfall_step (a j : N) (ha : a % 2 = 1) (hj : j >= 2) (ha_pos : a >= 1) :
    syracuse (a * 2^j - 1) = 3 * a * 2^{j-1} - 1

証明: mod 4 条件 + 算術

=== 優先度4: general_hensel_attrition (困難) ===

-- →方向
theorem hensel_attrition_forward (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
    consecutiveAscents n k → n % 2^{k+1} = 2^{k+1} - 1

-- ←方向
theorem hensel_attrition_backward (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
    n % 2^{k+1} = 2^{k+1} - 1 → consecutiveAscents n k

証明 (→方向):
  k=0: trivial (n % 2 = 1 → n % 2^1 = 1 = 2^1 - 1)
  k→k+1:
    帰納仮説: n % 2^{k+1} = 2^{k+1} - 1
    仮定: consecutiveAscents n (k+1)
    T^k(n) = 2*3^k*(q+1) - 1  where n = 2^{k+1}*q + 2^{k+1} - 1
    k+1回目上昇 → T^k(n) mod 4 = 3 → q 奇数 → n mod 2^{k+2} = 2^{k+2} - 1

  核心は T^k(n) = 2*3^k*(q+1) - 1 を示すこと。
  これは syracuse_iter_alt_formula から:
    2^k * T^k(n) + 2^k = 3^k * (n+1)
    n+1 = 2^{k+1} * (q+1)
    2^k * (T^k(n) + 1) = 3^k * 2^{k+1} * (q+1) = 2^k * 2 * 3^k * (q+1)
    T^k(n) + 1 = 2 * 3^k * (q+1)
""")

# 最終確認: T^k(n) = 2 * 3^k * (q+1) - 1 の一般的成立
print("T^k(n) = 2*3^k*(q+1) - 1 の検証 (n = 2^{k+1}*q + 2^{k+1}-1, k回上昇):")
total_checks = 0
total_ok = 0
for k in range(1, 7):
    mod = 2**(k+1)
    for q in range(0, 20):
        n = mod * q + mod - 1
        if n < 1 or n % 2 == 0:
            continue
        # k回上昇チェック
        has_ascents = True
        current = n
        for i in range(k):
            nxt = syracuse(current)
            if nxt <= current:
                has_ascents = False
                break
            current = nxt
        if not has_ascents:
            continue

        total_checks += 1
        tk = syracuse_iter(k, n)
        expected = 2 * 3**k * (q+1) - 1
        if tk == expected:
            total_ok += 1
        else:
            print(f"  FAIL: k={k}, q={q}, n={n}, T^k={tk}, expected={expected}")

print(f"\n総チェック数: {total_checks}, 成功: {total_ok}, 失敗: {total_checks - total_ok}")
