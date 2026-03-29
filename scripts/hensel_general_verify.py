"""
探索: 一般Hensel帰納法のLean実装詳細設計
数学的検証スクリプト

核心公式:
  2^k * (T^k(n) + 1) = 3^k * (n + 1)  ... (*)

この公式から:
  T^k(n) + 1 = 3^k * (n+1) / 2^k

n ≡ 2^{k+1} - 1 (mod 2^{k+1}) のとき:
  n + 1 = 2^{k+1} * m (m は正整数)
  T^k(n) + 1 = 3^k * 2^{k+1} * m / 2^k = 2 * 3^k * m

よって:
  T^k(n) = 2 * 3^k * m - 1

T^k(n) % 4 の計算:
  T^k(n) = 2 * 3^k * m - 1
  3^k は奇数なので 2*3^k*m mod 4 = 2*m mod 4
  - m が奇数: 2*m mod 4 = 2 → T^k(n) = 2*3^k*m - 1 ≡ 1 (mod 4) → 上昇停止
  - m が偶数: 2*m mod 4 = 0 → T^k(n) = 2*3^k*m - 1 ≡ 3 (mod 4) → 上昇継続

m の偶奇と n mod 2^{k+2}:
  n + 1 = 2^{k+1} * m
  m 偶数 ⟺ n + 1 ≡ 0 (mod 2^{k+2}) ⟺ n ≡ 2^{k+2} - 1 (mod 2^{k+2})
  m 奇数 ⟺ n ≡ 2^{k+1} - 1 (mod 2^{k+2})  [正確には n % 2^{k+2} = 2^{k+1} - 1]

これがHensel帰納法の核心:
  consecutiveAscents n k ⟺ n ≡ 2^{k+1} - 1 (mod 2^{k+1})
"""

def syracuse(n):
    """Syracuse function: T(n) = (3n+1) / 2^v2(3n+1)"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def syracuse_iter(k, n):
    """k回Syracuse反復"""
    for _ in range(k):
        n = syracuse(n)
    return n

def consecutive_ascents(n, k):
    """n から k 回連続上昇するか"""
    cur = n
    for _ in range(k):
        nxt = syracuse(cur)
        if nxt <= cur:
            return False
        cur = nxt
    return True

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

print("=" * 70)
print("Part 1: 基本公式 2^k * (T^k(n) + 1) = 3^k * (n + 1) の検証")
print("=" * 70)
for k in range(1, 9):
    mod = 2**(k+1)
    n = mod - 1  # smallest n with n % mod == mod - 1
    Tk = syracuse_iter(k, n)
    lhs = 2**k * (Tk + 1)
    rhs = 3**k * (n + 1)
    print(f"k={k}, n={n:5d}, T^k(n)={Tk:10d}, "
          f"2^k*(T^k+1)={lhs:12d}, 3^k*(n+1)={rhs:12d}, match={lhs==rhs}")

print()
print("=" * 70)
print("Part 2: T^k(n) mod 4 = 2*3^k*m - 1 mod 4 の検証")
print("=" * 70)
for k in range(1, 7):
    mod = 2**(k+1)
    print(f"\n--- k={k}, mod=2^{k+1}={mod} ---")
    for q in range(8):
        n = mod * q + (mod - 1)
        if n == 0:
            continue
        if n % 2 == 0:
            continue
        m = (n + 1) // mod
        Tk = syracuse_iter(k, n)
        Tk_mod4 = Tk % 4
        two_3k_m = 2 * 3**k * m
        two_3k_m_minus1_mod4 = (two_3k_m - 1) % 4

        is_ascent_k = consecutive_ascents(n, k)
        is_ascent_kp1 = consecutive_ascents(n, k + 1)

        m_parity = "even" if m % 2 == 0 else "odd"
        n_mod_next = n % (2**(k+2))
        expected_next_mod = 2**(k+2) - 1

        print(f"  n={n:5d}, m={m:3d}({m_parity}), T^k(n)={Tk:8d}, "
              f"T^k mod4={Tk_mod4}, 2*3^k*m-1 mod4={two_3k_m_minus1_mod4}, "
              f"asc_k={is_ascent_k}, asc_{k+1}={is_ascent_kp1}, "
              f"n%2^{k+2}={n_mod_next}, 2^{k+2}-1={expected_next_mod}")

print()
print("=" * 70)
print("Part 3: 全数検証 k=1..8, 各 mod 2^{k+1} の奇数")
print("=" * 70)
for k in range(1, 9):
    mod = 2**(k+1)
    count_pass = 0
    count_fail = 0
    # Test: consecutiveAscents n k ⟺ n % mod == mod - 1
    # Check for n = 1, 3, 5, ..., 2*mod - 1 (odd numbers up to 2*mod)
    for n in range(1, 4 * mod, 2):
        is_asc = consecutive_ascents(n, k)
        expected = (n % mod == mod - 1)
        if is_asc == expected:
            count_pass += 1
        else:
            count_fail += 1
            print(f"  FAIL: k={k}, n={n}, asc={is_asc}, expected={expected}, "
                  f"n%{mod}={n%mod}, target={mod-1}")
    print(f"k={k}: mod=2^{k+1}={mod:4d}, tested {count_pass+count_fail} odd numbers, "
          f"pass={count_pass}, fail={count_fail}")

print()
print("=" * 70)
print("Part 4: Lean実装で必要な補題の一覧と依存関係")
print("=" * 70)

lemmas = [
    ("Lemma A", "mod_pow_weaken",
     "n % 2^{k+2} = 2^{k+2}-1 → n % 2^{k+1} = 2^{k+1}-1",
     "omega で一発"),
    ("Lemma B", "iter_mod4_from_alt_formula",
     "consecutiveAscents n k ∧ n%2^{k+1}=2^{k+1}-1 → \n"
     "     T^k(n) % 4 = if n%2^{k+2}=2^{k+2}-1 then 3 else 1",
     "syracuse_iter_alt_formula + omega"),
    ("Lemma C", "ascent_continuation",
     "T^k(n) % 4 = 3 → syracuse(T^k(n)) > T^k(n)",
     "既存の syracuse_gt_of_mod4_eq3"),
    ("Lemma D", "ascent_stop",
     "T^k(n) % 4 = 1 ∧ T^k(n) > 1 → syracuse(T^k(n)) < T^k(n)",
     "既存の syracuse_lt_of_mod4_eq1"),
    ("Main→", "hensel_general_forward",
     "consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2}-1",
     "帰納法: base k=0 + step using Lemma B"),
    ("Main←", "hensel_general_backward",
     "n % 2^{k+2} = 2^{k+2}-1 → consecutiveAscents n (k+1)",
     "帰納法: base k=0 + step using Lemma B"),
    ("Main", "hensel_general",
     "consecutiveAscents n (k+1) ⟺ n % 2^{k+2} = 2^{k+2}-1",
     "Iff.intro hensel_general_forward hensel_general_backward"),
]

for i, (label, name, stmt, proof_hint) in enumerate(lemmas):
    print(f"\n{i+1}. [{label}] {name}")
    print(f"   Statement: {stmt}")
    print(f"   Proof hint: {proof_hint}")

print()
print("=" * 70)
print("Part 5: T^k(n) + 1 の因子分解の検証")
print("=" * 70)
print("syracuse_iter_alt_formula から:")
print("  2^k * T^k(n) + 2^k = 3^k * (n+1)")
print("  2^k * (T^k(n) + 1) = 3^k * (n+1)")
print()
print("n % 2^{k+1} = 2^{k+1} - 1 のとき:")
print("  n + 1 ≡ 0 (mod 2^{k+1}), つまり n + 1 = 2^{k+1} * m")
print("  2^k * (T^k(n) + 1) = 3^k * 2^{k+1} * m = 2 * 3^k * 2^k * m")
print("  T^k(n) + 1 = 2 * 3^k * m")
print()

# Part 5の検証
for k in range(1, 7):
    mod = 2**(k+1)
    n = mod - 1
    m = (n + 1) // mod
    Tk = syracuse_iter(k, n)
    print(f"  k={k}, n={n}, m={m}, T^k(n)={Tk}, T^k(n)+1={Tk+1}, 2*3^k*m={2*3**k*m}, match={Tk+1 == 2*3**k*m}")

print()
print("=" * 70)
print("Part 6: Lean帰納法の step の詳細")
print("=" * 70)
print("""
帰納法の構造 (→ 方向):

前提: consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2} - 1

base case (k=0):
  consecutiveAscents n 1 → n % 4 = 3
  これは single_ascent_mod4 から直接得られる。

inductive step:
  IH: ∀ n, consecutiveAscents n k → n % 2^{k+1} = 2^{k+1} - 1
  Goal: consecutiveAscents n (k+1) → n % 2^{k+2} = 2^{k+2} - 1

  Proof:
  1. hasc : consecutiveAscents n (k+1) とする
  2. hasc_k := consecutiveAscents_mono (k ≤ k+1) hasc : consecutiveAscents n k
     [ここが重要: k+1回上昇はk回上昇を含む]
  3. IH(n, hasc_k) より: n % 2^{k+1} = 2^{k+1} - 1
  4. syracuse_iter_alt_formula より:
     2^k * (T^k(n) + 1) = 3^k * (n + 1)
  5. n + 1 = 2^{k+1} * m (step 3 より)
  6. T^k(n) + 1 = 2 * 3^k * m (step 4,5 より)
  7. hasc の k 番目のステップ:
     syracuse(T^k(n)) > T^k(n)
     → T^k(n) % 4 = 3 (by syracuse_ascent_iff_mod4_eq3)
  8. T^k(n) = 2*3^k*m - 1
     T^k(n) % 4 = 3
     → (2*3^k*m - 1) % 4 = 3
     → 2*3^k*m % 4 = 0
     → m % 2 = 0 (since 3^k is odd, 2*odd*m ≡ 0 mod 4 ⟺ m even)
     → m = 2*m'
  9. n + 1 = 2^{k+1} * 2 * m' = 2^{k+2} * m'
     → n % 2^{k+2} = 2^{k+2} - 1
""")

print()
print("=" * 70)
print("Part 7: Lean帰納法のstep (← 方向) の詳細")
print("=" * 70)
print("""
前提: n % 2^{k+2} = 2^{k+2} - 1 → consecutiveAscents n (k+1)

base case (k=0):
  n % 4 = 3 → consecutiveAscents n 1
  single_ascent_mod4 (の逆方向) から。

inductive step:
  IH: ∀ n, n % 2^{k+1} = 2^{k+1} - 1 → consecutiveAscents n k
  Goal: n % 2^{k+2} = 2^{k+2} - 1 → consecutiveAscents n (k+1)

  Proof:
  1. hmod : n % 2^{k+2} = 2^{k+2} - 1 とする
  2. n % 2^{k+1} = 2^{k+1} - 1 (hmod より、omega)
  3. IH(n, step 2) より: consecutiveAscents n k
  4. あとはステップ k で上昇することを示せばよい
     (consecutiveAscents n k の各ステップ + k番目のステップ)
  5. syracuse_iter_alt_formula で T^k(n) + 1 = 2 * 3^k * m を得る
     ここで m = (n+1) / 2^{k+1}
  6. hmod より m は偶数 → T^k(n) % 4 = 3
  7. syracuse_gt_of_mod4_eq3 で k 番目のステップも上昇
  8. consecutiveAscents の定義に合わせて結合
""")

print()
print("=" * 70)
print("Part 8: 想定される行数と難易度")
print("=" * 70)
print("""
A. 補助補題群 (30-40行):
   - mod_pow_weaken: 5行 (omega)
   - v2_divisibility / factor lemmas: 10行
   - Nat.div_mod manipulation: 15行

B. iter_mod4_from_alt_formula (40-60行):
   - syracuse_iter_alt_formula の使用
   - n+1 = 2^{k+1}*m の分解
   - 2*3^k*m の mod 4 計算
   - 最も技術的に困難な部分

C. hensel_general_forward (40-60行):
   - Nat.strongRecOn による帰納法
   - base case: single_ascent_mod4
   - step: IH + iter_mod4 + ascent判定

D. hensel_general_backward (40-60行):
   - 同様の帰納法 (逆方向)

E. 主定理 hensel_general (5行):
   - Iff.intro

合計: 約 150-220行
""")
