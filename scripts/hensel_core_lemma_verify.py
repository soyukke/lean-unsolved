"""
一般化Hensel帰納法の核心補題の最終検証。

既存の Formula.lean にある:
- syracuse_iter_alt_formula:
    2^k * syracuseIter k n + 2^k = 3^k * (n + 1)
  (条件: consecutiveAscents n k, n >= 1, n % 2 = 1)

必要な新しい補題:

核心補題 (forward direction):
  consecutiveAscents n k & n % 2^{k+1} = 2^{k+1}-1
  => syracuseIter k n mod 4 = 3 <=> n % 2^{k+2} = 2^{k+2}-1

  証明ルート:
  syracuse_iter_alt_formula から:
    2^k * (T^k(n) + 1) = 3^k * (n + 1)
  n % 2^{k+1} = 2^{k+1}-1 なので n+1 = 2^{k+1} * m (m = (n+1)/2^{k+1})
    2^k * (T^k(n) + 1) = 3^k * 2^{k+1} * m
    T^k(n) + 1 = 2 * 3^k * m
    T^k(n) = 2 * 3^k * m - 1

  T^k(n) % 4 = (2 * 3^k * m - 1) % 4
  3^k は奇数なので 3^k % 2 = 1
  2 * 3^k * m % 4:
    m even: 2 * odd * even ≡ 0 (mod 4), so T^k(n) % 4 = (0-1)%4 = 3
    m odd: 2 * odd * odd ≡ 2 (mod 4), so T^k(n) % 4 = (2-1)%4 = 1

  m even <=> (n+1)/(2^{k+1}) even <=> 2^{k+2} | (n+1) <=> n % 2^{k+2} = 2^{k+2}-1
"""

def syracuse(n):
    m = 3 * n + 1
    count = 0
    while m % 2 == 0:
        m //= 2
        count += 1
    return m

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

def consecutive_ascents(n, k):
    for i in range(k):
        curr = syracuse_iter(i, n)
        next_val = syracuse(curr)
        if next_val <= curr:
            return False
    return True

# 核心補題の検証
print("=== 核心補題の検証 ===")
print("条件: consecutiveAscents n k AND n % 2^{k+1} = 2^{k+1}-1")
print("結論: T^k(n) % 4 = 3 <=> n % 2^{k+2} = 2^{k+2}-1")
print()

for k in range(1, 8):
    mod1 = 2**(k+1)
    target1 = mod1 - 1
    mod2 = 2**(k+2)
    target2 = mod2 - 1

    all_correct = True
    tested = 0
    for mult in range(50):
        n = target1 + mult * mod1
        if n == 0 or n % 2 == 0:
            continue
        if not consecutive_ascents(n, k):
            continue

        tk = syracuse_iter(k, n)
        tk_mod4 = tk % 4
        n_mod_next = n % mod2
        expected = 3 if n_mod_next == target2 else 1

        if tk_mod4 != expected:
            print(f"FAIL k={k} n={n}: T^k(n)={tk}, mod4={tk_mod4}, expected={expected}")
            all_correct = False
        tested += 1

    print(f"k={k}: tested {tested} cases, all correct: {all_correct}")

# 逆方向の検証: 必要十分条件
print("\n=== 主定理の検証 ===")
print("hensel_general: consecutiveAscents n k <=> n % 2^{k+1} = 2^{k+1}-1")
print("(条件: n >= 1, n % 2 = 1)")
print()

for k in range(0, 9):
    mod = 2**(k+1)
    target = mod - 1

    match_count = 0
    mismatch_count = 0
    for n in range(1, 1024, 2):  # odd numbers 1 to 1023
        asc = consecutive_ascents(n, k)
        mod_cond = (n % mod == target)
        if asc == mod_cond:
            match_count += 1
        else:
            mismatch_count += 1
            if mismatch_count <= 3:
                print(f"  MISMATCH k={k} n={n}: asc={asc}, mod={n%mod}=={target}? {mod_cond}")

    print(f"k={k}: matches={match_count}, mismatches={mismatch_count}")

# Lean実装計画の最終サマリー
print("\n" + "=" * 60)
print("=== Lean実装計画: 最終サマリー ===")
print()
print("既存の資産:")
print("  - consecutiveAscents の定義と基本性質 (Hensel.lean)")
print("  - k=1,2,3,4 の個別証明 (Hensel.lean)")
print("  - ascentConst の定義と閉じた形 (Formula.lean)")
print("  - syracuse_iter_mul_formula (Formula.lean)")
print("  - syracuse_iter_alt_formula (Formula.lean)")
print("  - syracuseIter_mod4_eq3_of_ascents (Formula.lean)")
print("  - syracuseIter_odd_of_ascents (Formula.lean)")
print("  - syracuseIter_pos_of_ascents (Formula.lean)")
print()
print("新規に必要な補題:")
print()
print("Lemma A: mod_condition_weaken")
print("  n % 2^{k+2} = 2^{k+2}-1 => n % 2^{k+1} = 2^{k+1}-1")
print("  証明: 2^{k+1} | 2^{k+2} から直接。omega で行ける可能性あり。")
print()
print("Lemma B: iter_mod4_from_alt_formula (核心)")
print("  consecutiveAscents n k, n % 2^{k+1} = 2^{k+1}-1 のとき")
print("  syracuseIter k n % 4 = 3 <=> n % 2^{k+2} = 2^{k+2}-1")
print()
print("  証明���ート:")
print("  1. alt_formula: 2^k * (T^k(n) + 1) = 3^k * (n+1)")
print("  2. n+1 = 2^{k+1} * m を設定 (n % 2^{k+1} = 2^{k+1}-1 より)")
print("  3. T^k(n) + 1 = 2 * 3^k * m を導出")
print("  4. T^k(n) % 4 の値は m の偶奇で決まる:")
print("     - m even => T^k(n) % 4 = 3")
print("     - m odd => T^k(n) % 4 = 1")
print("  5. m even <=> 2^{k+2} | (n+1) <=> n % 2^{k+2} = 2^{k+2}-1")
print()
print("  技術的困難:")
print("  - ステップ 3 で 2^k の約分 (Nat.eq_of_mul_eq_mul_left)")
print("  - ステップ 4 で 2*3^k*m mod 4 の計算")
print("    3^k mod 2 = 1 の証明 (Nat.odd_pow.mpr)")
print("    2 * odd * m mod 4 = 2*m mod 4")
print("  - ステップ 5 で m の定義と n の mod 条件の接続")
print()
print("Lemma C: hensel_general (主定理)")
print("  k に関する強帰納法")
print("  Base (k=0): trivial")
print("  Step (k -> k+1):")
print("    =>: mono + IH + Lemma B")
print("    <=: Lemma A + IH + Lemma B + syracuse_gt_of_mod4_eq3")
print()
print("推定難易度: Lemma B が最も技術的に困難。約50-80行。")
print("Lemma A は 5-10行。Lemma C は 30-50行。")
print("合計: 100-150行の新規Leanコード。")
