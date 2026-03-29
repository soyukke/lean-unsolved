"""
E[v2] = 2 の厳密証明の Lean 4 形式化戦略設計

== 目標 ==
一様ランダムな奇数 n に対して、v2(3n+1) の期待値が 2 であることを
Lean 4 + Mathlib で形式化可能な形で表現し、証明戦略を設計する。

== 数学的背景 ==
P(v2(3n+1) = j | n odd, n uniform in [1..2N]) の極限 (N -> inf) が 1/2^j.
E[v2] = sum_{j=1}^{inf} j * P(v2=j) = sum_{j=1}^{inf} j / 2^j = 2.

== 戦略 ==
Phase 1: 有限 mod での数え上げ (mod 2^k での正確な計算)
Phase 2: テレスコープ和 sum_{j=1}^{K} j/2^j = 2 - (K+2)/2^K の閉形式
Phase 3: 極限移行 (K -> inf で (K+2)/2^K -> 0)
Phase 4: Mathlib の tsum で無限和として E[v2] = 2

== Mathlib での利用可能ツール ==
- hasSum_geometric_of_lt_one: sum r^n = 1/(1-r) for 0 <= r < 1
- tsum_geometric_two: sum (1/2)^n = 2
- Summable / HasSum / tsum の基本API
"""

from fractions import Fraction

# =============================================================
# Phase 1 検証: mod 2^k での v2 分布の正確な数え上げ
# =============================================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count

def count_v2_distribution_mod2k(k):
    """
    mod 2^k の奇数全てについて v2(3n+1) の分布を数える。
    奇数 n in {1, 3, 5, ..., 2^k - 1} について v2(3n+1) を計算。
    """
    M = 2**k
    odd_residues = [r for r in range(1, M, 2)]  # 奇数の剰余類
    total = len(odd_residues)  # = 2^(k-1)

    dist = {}
    for r in odd_residues:
        val = 3 * r + 1
        v = v2(val)
        # v2(3n+1) for n = r mod 2^k は少なくとも min(v, k) で確定
        v_capped = min(v, k)  # mod 2^k では k 以上は区別できない
        dist[v_capped] = dist.get(v_capped, 0) + 1

    return dist, total

print("=" * 70)
print("Phase 1: mod 2^k での v2(3n+1) 分布")
print("=" * 70)

for k in range(3, 12):
    dist, total = count_v2_distribution_mod2k(k)
    print(f"\nmod 2^{k} (total odd = {total}):")

    # 期待する分布: P(v2=j) = count_j / total
    # 理論値: count_j / total should be 1/2^j for j < k, remainder for j >= k
    for j in sorted(dist.keys()):
        frac = Fraction(dist[j], total)
        theory = Fraction(1, 2**j) if j < k else None
        match = "OK" if theory and frac == theory else ("accumulate" if j >= k-1 else "MISMATCH")
        print(f"  v2 = {j}: count = {dist[j]:5d}, P = {frac} (theory: {theory}, {match})")

# =============================================================
# Phase 2: テレスコープ和の閉形式の検証
# =============================================================

print("\n" + "=" * 70)
print("Phase 2: Telescope sum: S(K) = sum_{j=1}^{K} j/2^j = 2 - (K+2)/2^K")
print("=" * 70)

def partial_sum_j_over_2j(K):
    """sum_{j=1}^{K} j / 2^j"""
    return sum(Fraction(j, 2**j) for j in range(1, K+1))

def closed_form(K):
    """2 - (K+2) / 2^K"""
    return 2 - Fraction(K + 2, 2**K)

for K in range(1, 21):
    s = partial_sum_j_over_2j(K)
    c = closed_form(K)
    ok = "OK" if s == c else "MISMATCH"
    print(f"  K={K:2d}: S(K) = {float(s):.10f}, closed = {float(c):.10f}, match = {ok}")

# =============================================================
# Phase 2b: テレスコープ和の帰納法検証
# =============================================================

print("\n" + "=" * 70)
print("Phase 2b: Inductive step verification")
print("=" * 70)

print("\nWe prove S(K) = 2 - (K+2)/2^K by induction on K.")
print("Base: S(1) = 1/2 = 2 - 3/2 = 1/2. OK")
print("Inductive step: S(K+1) = S(K) + (K+1)/2^{K+1}")
print("  = [2 - (K+2)/2^K] + (K+1)/2^{K+1}")
print("  = 2 - 2(K+2)/2^{K+1} + (K+1)/2^{K+1}")
print("  = 2 - [2(K+2) - (K+1)]/2^{K+1}")
print("  = 2 - [2K+4-K-1]/2^{K+1}")
print("  = 2 - (K+3)/2^{K+1}")
print("  = 2 - ((K+1)+2)/2^{K+1}. QED")

# Verify algebraically
for K in range(1, 15):
    # S(K+1) = S(K) + (K+1)/2^{K+1}
    lhs = closed_form(K) + Fraction(K + 1, 2**(K+1))
    rhs = closed_form(K + 1)
    assert lhs == rhs, f"Failed at K={K}"
print("Inductive step verified for K=1..14")

# =============================================================
# Phase 3: 極限 (K+2)/2^K -> 0 の確認
# =============================================================

print("\n" + "=" * 70)
print("Phase 3: (K+2)/2^K -> 0 as K -> inf")
print("=" * 70)

for K in [10, 20, 30, 50, 100]:
    val = (K + 2) / 2**K
    print(f"  K={K:3d}: (K+2)/2^K = {val:.2e}")

# =============================================================
# Phase 4: Lean形式化のための定理ステートメント設計
# =============================================================

print("\n" + "=" * 70)
print("Phase 4: Lean 4 形式化戦略")
print("=" * 70)

lean_strategy = """
== Lean 4 形式化の具体的な定理と証明戦略 ==

--- Step 1: 有限 mod 2^k での数え上げ定理 ---

定理 (v2_count_mod2k):
  k >= 2, 1 <= j < k のとき、
  #{n in {1,3,...,2^k-1} | v2(3n+1) = j} = 2^{k-1-j}

証明戦略:
  mod 2^k の奇数は 2^{k-1} 個。
  n mod 2^{j+1} で v2(3n+1) = j が確定する。
  - v2(3n+1) = 1 <=> n ≡ 3 (mod 4) : 2^{k-2} 個 / 2^{k-1} 個 = 1/2
  - v2(3n+1) = 2 <=> n ≡ 1 (mod 8) : 2^{k-3} 個 / 2^{k-1} 個 = 1/4
  帰納法で一般の j に対して示す。

Lean 4:
  theorem v2_count_mod2k (k j : Nat) (hk : k >= 2) (hj : 1 <= j) (hjk : j < k) :
    Finset.card (Finset.filter
      (fun n => v2 (3 * n + 1) = j)
      (Finset.filter (fun n => n % 2 = 1) (Finset.range (2^k)))) = 2^(k-1-j) := sorry

--- Step 2: テレスコープ和の閉形式 ---

定理 (partial_sum_j_over_2j):
  forall K >= 1, sum_{j=1}^{K} (j : R) / 2^j = 2 - (K+2 : R) / 2^K

証明: 帰納法
  Base: K=1 は norm_num で。
  Inductive step: 代数的操作で帰結。

Lean 4 (実数上):
  theorem partial_sum_j_div_2pow (K : Nat) (hK : K >= 1) :
    (Finset.sum (Finset.range K) (fun j =>
      ((j + 1 : Nat) : R) / (2 : R) ^ (j + 1)))
    = 2 - ((K + 2 : Nat) : R) / (2 : R) ^ K := sorry

--- Step 3: 無限和の収束 ---

定理 (hasSum_j_div_2j):
  HasSum (fun j => ((j + 1) : R) / 2^(j+1)) 2

証明戦略 A (直接法):
  HasSum f a <-> partial sums converge to a.
  partial_sum_j_div_2pow + (K+2)/2^K -> 0 で直接示す。

証明戦略 B (テレスコープ分解):
  j / 2^j = sum_{i=j}^{inf} 1/2^i = 2 * (1/2)^j
  (ただし j >= 1 に対して)

  実は: sum_{j=1}^{inf} j * x^j = x / (1-x)^2 for |x| < 1
  x = 1/2 => sum = (1/2) / (1/2)^2 = 2

Lean 4 (戦略B):
  -- Mathlib には hasSum_geometric_two: HasSum (1/2)^n = 2 がある
  -- また tsum_geometric_two も利用可能
  -- x/(1-x)^2 = d/dx [x/(1-x)] を利用する手もある

  -- 最も簡潔な戦略:
  -- sum_{j=1}^{inf} j/2^j
  -- = sum_{j=1}^{inf} sum_{i=1}^{j} 1/2^j
  -- = sum_{i=1}^{inf} sum_{j=i}^{inf} 1/2^j  (Fubini)
  -- = sum_{i=1}^{inf} (1/2)^i / (1 - 1/2)
  -- = sum_{i=1}^{inf} 2 * (1/2)^i
  -- = 2 * (sum_{i=0}^{inf} (1/2)^i - 1)
  -- = 2 * (2 - 1) = 2

証明戦略 C (有限和+極限):
  partial_sum_j_div_2pow で S(K) = 2 - (K+2)/2^K を示し、
  tendsto_nhds で K -> inf の極限が 2 であることを示す。
  次に hasSum_iff_tendsto_nat_of_nonneg を使って HasSum を得る。

--- Step 4: 有限 mod での E[v2] の計算 ---

有限版の期待値:
  E_k[v2] = (1/2^{k-1}) * sum_{n odd < 2^k} v2(3n+1)
           = sum_{j=1}^{k-1} j * (count of v2=j) / 2^{k-1}
           + contribution from v2 >= k

limit as k -> inf equals 2.

--- 推奨戦略 ---

最も形式化しやすいのは戦略C:
1. partial_sum_j_div_2pow を帰納法で証明 (純代数的)
2. (K+2)/2^K -> 0 を Mathlib の tendsto 補題で証明
3. hasSum_iff_tendsto_nat_of_nonneg で HasSum を導出

これは Mathlib の無限和理論の核心部分を使わずに済み、
実数の基本的な代数操作と極限の基本定理だけで完結する。

--- 必要な Mathlib 補題 ---

1. pow_pos : 0 < (2:R) -> 0 < 2^n
2. div_nonneg : 有理/実数の非負性
3. Finset.sum_range_succ : 部分和の展開
4. tendsto_pow_atTop_nhds_zero_of_lt_one : |r| < 1 -> r^n -> 0
5. Tendsto.div / Tendsto.mul : 極限の演算
6. hasSum_iff_tendsto_nat_of_nonneg : 非負項級数の HasSum
7. HasSum.tsum_eq : HasSum から tsum の値を得る
"""

print(lean_strategy)

# =============================================================
# Phase 5: v2(3n+1) の mod 2^{j+1} による完全決定の検証
# =============================================================

print("\n" + "=" * 70)
print("Phase 5: v2(3n+1) = j <==> specific residue classes mod 2^{j+1}")
print("=" * 70)

for j in range(1, 8):
    M = 2**(j+1)
    residues_with_v2_j = []
    for r in range(1, M, 2):  # odd residues mod 2^{j+1}
        if v2(3*r + 1) == j:
            residues_with_v2_j.append(r)

    total_odd = M // 2  # = 2^j
    count = len(residues_with_v2_j)
    expected_frac = Fraction(1, 2**j)
    actual_frac = Fraction(count, total_odd)

    print(f"  j={j}: residues mod {M:4d} with v2=j: {residues_with_v2_j}")
    print(f"        count={count}, total_odd={total_odd}, P={actual_frac} (expected {expected_frac}) {'OK' if actual_frac == expected_frac else 'MISMATCH'}")

# =============================================================
# Phase 6: mod 2^{j+1} で v2(3n+1) = j を持つ唯一の剰余類の特定
# =============================================================

print("\n" + "=" * 70)
print("Phase 6: The unique residue class r_j mod 2^{j+1} with v2(3r_j+1) = j")
print("=" * 70)

print("\nFor each j, there is exactly ONE odd residue r mod 2^{j+1} such that v2(3r+1) = j")
for j in range(1, 12):
    M = 2**(j+1)
    for r in range(1, M, 2):
        if v2(3*r + 1) == j:
            # Check: this r determines a unique class mod 2^{j+1}
            # And there are 2^{k-1}/2^j = 2^{k-1-j} copies in [0, 2^k)
            print(f"  j={j:2d}: r = {r:6d} mod {M:6d}  (r = {r})")
            # Verify: r = (2^j - 1) / 3 * 4 + ... pattern?
            # Actually: 3r + 1 = 2^j * m where m is odd
            m = (3*r + 1) // (2**j)
            print(f"         3r+1 = {3*r+1} = 2^{j} * {m} (m odd: {m % 2 == 1})")
            break

# =============================================================
# Summary: key formula for the unique residue class
# =============================================================

print("\n" + "=" * 70)
print("Summary: r_j (the unique odd residue mod 2^{j+1} with v2(3r_j+1) = j)")
print("=" * 70)

for j in range(1, 12):
    M = 2**(j+1)
    for r in range(1, M, 2):
        if v2(3*r + 1) == j:
            # Check if r = (2^{j+1} - 1) / 3 * (something)
            # r is the unique solution to 3r + 1 ≡ 0 (mod 2^j) and 3r+1 not ≡ 0 (mod 2^{j+1})
            # 3r ≡ -1 (mod 2^j) => r ≡ -3^{-1} (mod 2^j)
            # 3^{-1} mod 2^j:
            inv3 = pow(3, -1, 2**j)
            r_formula = (-inv3) % (2**j)
            # But we need r odd and mod 2^{j+1}
            # v2(3r+1) = j means 2^j | (3r+1) but 2^{j+1} does not divide (3r+1)
            print(f"  j={j:2d}: r_j = {r:6d}, 3^(-1) mod 2^j = {inv3}, -3^(-1) mod 2^j = {r_formula}")
            # Verify
            assert (3 * r + 1) % (2**j) == 0, f"Failed divisibility"
            assert (3 * r + 1) % (2**(j+1)) != 0, f"Failed non-divisibility"
            break

print("\n\nDone. All verifications passed.")
