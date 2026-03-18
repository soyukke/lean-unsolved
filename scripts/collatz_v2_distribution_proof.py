#!/usr/bin/env python3
"""
探索059: v2(3n+1) の分布が幾何分布であることの厳密な証明

奇数 n を mod 2^k で分類したとき、v2(3n+1) = j となる残基クラスの数を
正確に数え上げ、P(v2 = j) = 1/2^j が成り立つことを厳密に証明する。

数学的主張:
  mod 2^k の奇数のうち v2(3r+1) = j のものは正確に 2^{k-1-j} 個 (j=1,...,k-1)
  v2(3r+1) >= k のものは 1 個

よって P(v2 = j | n は奇数 mod 2^k) = 2^{k-1-j} / 2^{k-1} = 1/2^j
これは幾何分布 Geom(1/2) の質量関数。
"""

import math


# ============================================================
# 基本関数
# ============================================================

def v2(n):
    """n の 2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


# ============================================================
# Part 1: mod 2^k での v2(3r+1) の分布を完全に数え上げ
# ============================================================

def count_v2_classes():
    print("=" * 70)
    print("Part 1: mod 2^k での v2(3r+1) = j の残基クラス数")
    print("=" * 70)

    print("\n主張: mod 2^k の奇数 2^{k-1} 個のうち、")
    print("  v2(3r+1) = j のもの: 2^{k-1-j} 個 (j = 1, ..., k-1)")
    print("  v2(3r+1) >= k のもの: 1 個")
    print()

    all_pass = True

    for k in range(2, 21):
        M = 2 ** k
        odd_residues = [r for r in range(1, M, 2)]
        total_odd = len(odd_residues)  # = 2^{k-1}
        assert total_odd == 2 ** (k - 1)

        # v2(3r+1) の値ごとにカウント
        v2_counts = {}
        for r in odd_residues:
            val = v2(3 * r + 1)
            j = min(val, k)  # v2 >= k は全て ">=k" として扱う
            if j >= k:
                j = 'ge_k'
            v2_counts[j] = v2_counts.get(j, 0) + 1

        # 検証
        ok = True
        for j in range(1, k):
            expected = 2 ** (k - 1 - j)
            actual = v2_counts.get(j, 0)
            if actual != expected:
                ok = False
                all_pass = False

        # v2 >= k のクラス数
        ge_k_count = v2_counts.get('ge_k', 0)
        if ge_k_count != 1:
            ok = False
            all_pass = False

        status = "OK" if ok else "FAIL"
        if k <= 12:
            parts = []
            for j in range(1, k):
                parts.append(f"j={j}:{v2_counts.get(j, 0)}/{2**(k-1-j)}")
            parts.append(f">=k:{ge_k_count}/1")
            print(f"  k={k:>2} (mod {M:>6}): 奇数={total_odd:>5}  [{status}]  {', '.join(parts)}")
        else:
            print(f"  k={k:>2} (mod 2^{k}): 奇数={total_odd:>7}  [{status}]")

    print(f"\n全 k で検証: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


# ============================================================
# Part 2: 確率の計算と幾何分布の証明
# ============================================================

def prove_geometric_distribution():
    print("\n" + "=" * 70)
    print("Part 2: 確率の計算 -- 幾何分布の厳密な証明")
    print("=" * 70)

    print("""
■ 定理: 奇数 n を一様ランダムに mod 2^k から選ぶとき、
  P(v2(3n+1) = j) = 1/2^j  (j = 1, 2, ..., k-1)

■ 証明:
  Step 1: mod 2^k の奇数は 2^{k-1} 個。

  Step 2: v2(3r+1) = j ⟺ 2^j | (3r+1) かつ 2^{j+1} ∤ (3r+1)
          ⟺ 3r+1 ≡ 0 (mod 2^j) かつ 3r+1 ≢ 0 (mod 2^{j+1})
          ⟺ r ≡ (2^j - 1)/3 (mod 2^j) のある解で、
             かつその解が mod 2^{j+1} で 2 つの解のうち 1 つ

  Step 3: 3 は mod 2^k で可逆（gcd(3, 2^k) = 1）なので、
          3r ≡ -1 (mod 2^j) の解は r ≡ 3^{-1}·(-1) ≡ (2^j - 1)·3^{-1} (mod 2^j)
          ただし 3^{-1} mod 2^j は一意に存在。

  Step 4: 2^j | (3r+1) の条件で mod 2^k 中の奇数の数:
          mod 2^k の全整数のうち 2^j | (3r+1) を満たすものは 2^{k-j} 個。
          そのうち奇数は 2^{k-j-1} 個（j < k-1 のとき）。

          しかしこれは「v2 >= j」のクラス数。「v2 = j」は:
          v2 = j のクラス数 = (v2 >= j のクラス数) - (v2 >= j+1 のクラス数)
                            = 2^{k-1-j} - 2^{k-1-(j+1)}
                            = 2^{k-1-j} - 2^{k-2-j}
                            = 2^{k-2-j}

          ... ここで矛盾が生じるように見える。修正が必要。
""")

    print("■ 正しい数え上げ（直接検証による帰納的構成）:")
    print()

    # 直接的な数え上げ
    for k in [4, 6, 8]:
        M = 2 ** k
        odd_residues = [r for r in range(1, M, 2)]

        # v2 >= j のクラス数を数える
        print(f"  k = {k} (mod {M}):")
        for j in range(1, k + 1):
            ge_j = sum(1 for r in odd_residues if v2(3 * r + 1) >= j)
            eq_j = sum(1 for r in odd_residues if v2(3 * r + 1) == j)
            if j <= k:
                print(f"    v2 >= {j}: {ge_j:>5}  (= 2^{k-1-j} = {2**(k-1-j) if k-1-j>=0 else '?'}?)"
                      f"    v2 = {j}: {eq_j:>5}  (= 2^{k-1-j} = {2**(k-1-j) if k-1-j>=0 else '?'}?)")
        print()

    print("""
■ 修正した証明:

  核心的な事実: mod 2^k の奇数 r に対して、
    #{r : v2(3r+1) >= j} = 2^{k-1-j}   (j = 0, 1, ..., k-1)

  これは以下のように示せる:

  v2(3r+1) >= j ⟺ 2^j | (3r+1) ⟺ 3r ≡ -1 (mod 2^j)

  3 は mod 2^j で可逆なので、r ≡ 3^{-1}·(-1) (mod 2^j) が唯一の解クラス。
  mod 2^k の全整数のうち、この合同条件を満たすのは 2^{k-j} 個。
  そのうち奇数のものを数える:

  r ≡ c (mod 2^j) を満たす r ∈ {0, 1, ..., 2^k - 1} は
    c, c + 2^j, c + 2·2^j, ..., c + (2^{k-j} - 1)·2^j
  の 2^{k-j} 個。

  j >= 1 のとき c = 3^{-1}·(-1) mod 2^j は奇数
  （∵ 3r+1 ≡ 0 (mod 2) ⟹ r は奇数）。
  c が奇数で 2^j は偶数（j >= 1）なので c + m·2^j の偶奇は c と同じ、つまり全て奇数。
  → 奇数の数 = 2^{k-j} 個。

  ただし mod 2^k の奇数は全部で 2^{k-1} 個なので:
    #{r 奇数 : v2(3r+1) >= j} = 2^{k-j}

  ... これは 2^{k-1} を超えてしまう（j=0 のとき）。
  j = 0 のとき: v2(3r+1) >= 0 は常に成立なので数は 2^{k-1}。OK。
  j = 1 のとき: 3r+1 ≡ 0 (mod 2) ⟺ r ≡ 1 (mod 2)、つまり全ての奇数。数 = 2^{k-1}。

  ここに問題がある。v2(3r+1) >= 1 は r が奇数なら「常に成立」！

  正しい計算:
  r が奇数 → 3r は奇数 → 3r+1 は偶数 → v2(3r+1) >= 1 は自明。

  v2(3r+1) >= j+1 ⟺ 2^{j+1} | (3r+1)    (j >= 0)

  mod 2^k の奇数 r で 2^{j+1} | (3r+1) を満たすものの数:
    3r ≡ -1 (mod 2^{j+1})
    r ≡ 3^{-1}·(-1) (mod 2^{j+1})

    この c = 3^{-1}·(-1) mod 2^{j+1} は奇数（上と同じ理由）。
    j+1 >= 1 なので 2^{j+1} は偶数。
    c + m·2^{j+1} は全て奇数。
    数 = 2^{k-(j+1)} = 2^{k-j-1}

  よって:
    #{r 奇数 mod 2^k : v2(3r+1) >= j+1} = 2^{k-j-1}    (j = 0, 1, ..., k-2)
    #{r 奇数 mod 2^k : v2(3r+1) = j+1}
      = #{v2 >= j+1} - #{v2 >= j+2}
      = 2^{k-j-1} - 2^{k-j-2}
      = 2^{k-j-2}                                         (j = 0, ..., k-3)

    j' = j+1 と置くと:
    #{v2(3r+1) = j'} = 2^{k-j'-1} = 2^{k-1-j'}          (j' = 1, ..., k-1)

  確率:
    P(v2 = j') = 2^{k-1-j'} / 2^{k-1} = 1/2^{j'}        ■

  E[v2] = Σ_{j=1}^{k-1} j / 2^j + (remainder from v2 >= k)
         → Σ_{j=1}^∞ j / 2^j = 2.0  (k → ∞)
""")


# ============================================================
# Part 3: v2(3r+1) = j の残基クラスの具体的な特定
# ============================================================

def identify_residue_classes():
    print("=" * 70)
    print("Part 3: v2(3r+1) = j の残基クラスの具体的特定")
    print("=" * 70)

    for k in [4, 6, 8]:
        M = 2 ** k
        print(f"\n  k = {k} (mod {M}):")
        for j in range(1, k):
            residues = [r for r in range(1, M, 2) if v2(3 * r + 1) == j]
            expected_count = 2 ** (k - 1 - j)
            assert len(residues) == expected_count, \
                f"k={k}, j={j}: got {len(residues)}, expected {expected_count}"

            # 残基を mod 2^{j+1} で分類
            mod_classes = set(r % (2 ** (j + 1)) for r in residues)
            if j <= 5:
                print(f"    v2 = {j}: {len(residues):>3} 個, "
                      f"mod 2^{j+1} の代表元: {sorted(mod_classes)}")

        # v2 >= k
        ge_k = [r for r in range(1, M, 2) if v2(3 * r + 1) >= k]
        print(f"    v2 >= {k}: {len(ge_k)} 個, 残基: {ge_k}")


# ============================================================
# Part 4: 3^{-1} mod 2^k の計算と閉じた公式
# ============================================================

def compute_inverse_formula():
    print("\n" + "=" * 70)
    print("Part 4: 3^{-1} mod 2^k と v2(3r+1)=j の閉じた公式")
    print("=" * 70)

    print("\n  3^{-1} mod 2^k の値:")
    for k in range(1, 17):
        M = 2 ** k
        # 3^{-1} mod M: 3 * x ≡ 1 (mod M)
        inv3 = pow(3, -1, M)
        # v2(3r+1) >= j+1 の条件: r ≡ (-1) * 3^{-1} = M - inv3 (mod 2^{j+1})
        c = (M - inv3) % M
        print(f"    k={k:>2}: 3^{{-1}} mod 2^{k} = {inv3:>7}, "
              f"(-1)·3^{{-1}} mod 2^{k} = {c:>7}")

    print("\n  v2(3r+1) = j の条件（閉じた公式）:")
    print("  r ≡ (2^{j+1} - 1) / 3  (mod 2^{j+1}) かつ")
    print("  r ≢ (2^{j+2} - 1) / 3  (mod 2^{j+2})  [j < k-1 のとき]")
    print()

    for j in range(1, 10):
        # (2^{j+1} - 1) / 3 が整数かどうか
        num = 2 ** (j + 1) - 1
        if num % 3 == 0:
            c = num // 3
            print(f"    j={j}: r ≡ (2^{j+1} - 1)/3 = {c} (mod 2^{j+1} = {2**(j+1)})")
        else:
            # 3^{-1} · (-1) mod 2^{j+1}
            M = 2 ** (j + 1)
            c = (M - pow(3, -1, M)) % M
            print(f"    j={j}: r ≡ {c} (mod {M})  [直接計算]")

    # 検証: (2^{j+1} - 1) / 3 と 3^{-1}·(-1) mod 2^{j+1} は同じか？
    print("\n  検証: (2^{j+1}-1)/3 mod 2^{j+1} vs (-1)·3^{-1} mod 2^{j+1}")
    for j in range(1, 12):
        M = 2 ** (j + 1)
        c_formula = (M - pow(3, -1, M)) % M
        # 2^{j+1} - 1 を 3 で割る: j+1 が偶数のとき (2^{j+1}-1) は 3 で割れる
        num = 2 ** (j + 1) - 1
        if num % 3 == 0:
            c_closed = num // 3
            match = "MATCH" if c_formula == c_closed else "DIFFER"
            print(f"    j={j}: formula={c_formula}, closed={c_closed}  [{match}]")
        else:
            print(f"    j={j}: formula={c_formula}, 2^{j+1}-1 not div by 3")


# ============================================================
# Part 5: E[v2] の厳密計算
# ============================================================

def compute_expected_v2():
    print("\n" + "=" * 70)
    print("Part 5: E[v2(3n+1)] の厳密計算")
    print("=" * 70)

    print("\n  E[v2] = Σ_{j=1}^∞ j · P(v2=j) = Σ_{j=1}^∞ j / 2^j")
    print()

    # 部分和の収束
    print(f"  {'k':>5} | {'部分和 Σ_{j=1}^{k}':>20} | {'誤差':>15}")
    print("  " + "-" * 50)

    total = 0.0
    for kk in range(1, 31):
        total += kk / (2 ** kk)
        error = 2.0 - total
        print(f"  {kk:>5} | {total:>20.15f} | {error:>15.2e}")

    print(f"\n  極限値: E[v2] = 2.0 (厳密)")
    print()

    # 証明スケッチ
    print("  ■ 閉じた公式の導出:")
    print("    S = Σ_{j=1}^∞ j x^j  (|x| < 1)")
    print("    S = x d/dx [Σ x^j] = x d/dx [x/(1-x)] = x/(1-x)^2")
    print("    x = 1/2: S = (1/2)/(1/2)^2 = (1/2)/(1/4) = 2  ■")
    print()

    # 分散
    print("  ■ V[v2] の計算:")
    print("    E[v2^2] = Σ j^2 / 2^j = 6")
    print("    V[v2] = E[v2^2] - (E[v2])^2 = 6 - 4 = 2  ... ではなく:")

    e_v2_sq = sum(j ** 2 / (2 ** j) for j in range(1, 50))
    var_v2 = e_v2_sq - 4.0
    print(f"    E[v2^2] = Σ j^2/2^j = {e_v2_sq:.10f}")
    print(f"    V[v2] = {e_v2_sq:.10f} - 4 = {var_v2:.10f}")
    print()

    # 実測との比較
    print("  ■ 実測との比較 (n = 1, 3, 5, ..., 2M-1 の奇数):")
    for M_exp in [10, 14, 18]:
        M = 2 ** M_exp
        total_v2 = 0
        total_v2_sq = 0
        count = 0
        for r in range(1, M, 2):
            j = v2(3 * r + 1)
            total_v2 += j
            total_v2_sq += j * j
            count += 1
        emp_mean = total_v2 / count
        emp_var = total_v2_sq / count - emp_mean ** 2
        print(f"    n < 2^{M_exp}: E[v2] = {emp_mean:.6f}, V[v2] = {emp_var:.6f}  "
              f"(N = {count:,})")


# ============================================================
# Part 6: 帰納法による証明の構造
# ============================================================

def induction_proof_structure():
    print("\n" + "=" * 70)
    print("Part 6: 帰納法による証明の構造（Lean 形式化用）")
    print("=" * 70)

    print("""
  ■ 定理 (v2_count_mod):
    ∀ k ≥ 2, ∀ j ∈ {1, ..., k-1},
    #{r ∈ {1,3,...,2^k-1} : v2(3r+1) = j} = 2^{k-1-j}

  ■ 証明（k に関する帰納法）:

  基底 k = 2:
    mod 4 の奇数: {1, 3}
    v2(3·1+1) = v2(4) = 2 ≥ k=2, なので v2 >= k の残基
    v2(3·3+1) = v2(10) = 1
    j=1 のクラス数 = 1 = 2^{2-1-1} = 2^0 = 1  ✓

  帰納ステップ k → k+1:
    mod 2^{k+1} の奇数 r は、r mod 2^k と r の (k+1) ビット目で決まる。
    mod 2^k で v2(3r+1) = j (j < k) となる r₀ に対して:
      r₀ と r₀ + 2^k の両方が mod 2^{k+1} での奇数。
      v2(3r₀+1) と v2(3(r₀+2^k)+1) は:
        3(r₀+2^k)+1 = 3r₀+1 + 3·2^k
        v2(3r₀+1) = j < k なので、3r₀+1 = 2^j · m (m は奇数)
        3·2^k の v2 は k+... (k >= 2 なので v2(3·2^k) = k)
        3(r₀+2^k)+1 = 2^j · m + 2^k · 3
        j < k なので 2^j | 両方の項 → 2^j | (3(r₀+2^k)+1)
        = 2^j · (m + 3·2^{k-j})
        m は奇数、3·2^{k-j} は偶数(k-j >= 1) → m + 3·2^{k-j} は奇数
        → v2(3(r₀+2^k)+1) = j

      つまり j < k のとき、mod 2^k で v2 = j の各残基 r₀ は
      mod 2^{k+1} でも r₀ と r₀+2^k の両方で v2 = j。
      → v2 = j のクラス数は 2 倍: 2·2^{k-1-j} = 2^{k-j} = 2^{(k+1)-1-j}  ✓

    j = k のクラス数:
      mod 2^k で v2 >= k の残基は 1 個（r₀ とする）。
      r₀ と r₀+2^k のうち、一方は v2 = k、もう一方は v2 >= k+1。
      → v2 = k のクラス数 = 1 = 2^{(k+1)-1-k} = 2^0  ✓

    v2 >= k+1 のクラス数 = 1  ✓

  ■ 帰納ステップの核心の検証:
""")

    # 帰納ステップの核心を数値検証
    for k in range(2, 12):
        M_k = 2 ** k
        M_k1 = 2 ** (k + 1)

        # mod 2^k で v2 >= k の残基
        ge_k_old = [r for r in range(1, M_k, 2) if v2(3 * r + 1) >= k]
        assert len(ge_k_old) == 1, f"k={k}: ge_k count = {len(ge_k_old)}"
        r0 = ge_k_old[0]

        # r0 と r0 + 2^k の v2
        v2_r0 = v2(3 * r0 + 1)
        v2_r0_plus = v2(3 * (r0 + M_k) + 1)

        # 一方が v2 = k、もう一方が v2 >= k+1
        eq_k = (v2_r0 == k) + (v2_r0_plus == k)
        ge_k1 = (v2_r0 >= k + 1) + (v2_r0_plus >= k + 1)

        status = "OK" if eq_k == 1 and ge_k1 == 1 else "FAIL"
        print(f"    k={k:>2}: r₀={r0:>7}, v2(3r₀+1)={v2_r0:>3}, "
              f"v2(3(r₀+2^k)+1)={v2_r0_plus:>3}  "
              f"[v2=k: {eq_k}, v2>={k+1}: {ge_k1}]  {status}")

    # j < k のケースも検証
    print("\n    帰納ステップ (j < k): v2 が保存されることの検証")
    for k in [3, 5, 8]:
        M_k = 2 ** k
        all_ok = True
        for j in range(1, k):
            eq_j_old = [r for r in range(1, M_k, 2) if v2(3 * r + 1) == j]
            for r0 in eq_j_old:
                if v2(3 * (r0 + M_k) + 1) != j:
                    all_ok = False
        print(f"    k={k}: j < k での v2 保存 = {'OK' if all_ok else 'FAIL'}")


# ============================================================
# Part 7: Lean で形式化可能な有限ケースの列挙
# ============================================================

def lean_decidable_cases():
    print("\n" + "=" * 70)
    print("Part 7: Lean で decide 可能な有限ケース")
    print("=" * 70)

    print("""
  以下の命題は Lean 4 で `decide` により証明可能:

  ∀ k = 2, 3, 4, 5, 6 に対して:
    #{r ∈ Fin(2^k) : r は奇数 ∧ v2(3r+1) = j} = 2^{k-1-j}  (j=1,...,k-1)

  具体的な example:
""")

    for k in range(2, 7):
        M = 2 ** k
        for j in range(1, k):
            count = sum(1 for r in range(1, M, 2) if v2(3 * r + 1) == j)
            expected = 2 ** (k - 1 - j)
            print(f"    k={k}, j={j}: count = {count} = 2^{k-1-j} = {expected}")


# ============================================================
# Part 8: 補足 -- v2 >= k の唯一の残基の閉じた公式
# ============================================================

def unique_residue_formula():
    print("\n" + "=" * 70)
    print("Part 8: v2(3r+1) >= k の唯一の残基の閉じた公式")
    print("=" * 70)

    print("\n  v2(3r+1) >= k ⟺ 2^k | (3r+1) ⟺ r ≡ (2^k - 1)/3 (mod 2^k) [k 偶数]")
    print("  ⟺ r ≡ (2^k - 1)·3^{-1} (mod 2^k)")
    print()

    for k in range(2, 21):
        M = 2 ** k
        ge_k = [r for r in range(1, M, 2) if v2(3 * r + 1) >= k]
        assert len(ge_k) == 1
        r0 = ge_k[0]

        # 閉じた公式: (-1) · 3^{-1} mod 2^k
        inv3 = pow(3, -1, M)
        c = (M - inv3) % M

        # (2^k - 1) / 3
        if (M - 1) % 3 == 0:
            c_alt = (M - 1) // 3
            formula = f"(2^{k}-1)/3 = {c_alt}"
        else:
            c_alt = None
            formula = f"(2^{k}-1) not div by 3"

        match = r0 == c and (c_alt is None or c == c_alt)
        print(f"    k={k:>2}: r₀ = {r0:>7}, (-1)·3^{{-1}} mod 2^k = {c:>7}, "
              f"{formula}  [{'OK' if match else 'CHECK'}]")


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 70)
    print("  探索059: v2(3n+1) の幾何分布の厳密な証明")
    print("=" * 70)
    print()

    # Part 1: 数え上げ検証
    count_v2_classes()

    # Part 2: 確率計算と証明
    prove_geometric_distribution()

    # Part 3: 残基クラスの特定
    identify_residue_classes()

    # Part 4: 閉じた公式
    compute_inverse_formula()

    # Part 5: 期待値
    compute_expected_v2()

    # Part 6: 帰納法の構造
    induction_proof_structure()

    # Part 7: Lean で形式化可能なケース
    lean_decidable_cases()

    # Part 8: 唯一の残基
    unique_residue_formula()

    # 総合結論
    print("\n" + "=" * 70)
    print("総合結論")
    print("=" * 70)
    print("""
1. 厳密な定理:
   mod 2^k の奇数 r に対して、v2(3r+1) = j の残基クラス数は正確に 2^{k-1-j} 個。
   これにより P(v2 = j) = 1/2^j（幾何分布 Geom(1/2)）が厳密に成立。

2. 証明の方法:
   k に関する数学的帰納法で証明可能。
   核心: j < k のとき v2 値は mod 2^k → mod 2^{k+1} で保存される
   （3·2^k の 2-adic valuation が k であることによる）。

3. 期待値:
   E[v2] = Σ j/2^j = 2.0（厳密）
   V[v2] = 6 - 4 = 2.0（厳密）

4. Lean 形式化:
   - k = 2, ..., 6 での有限ケースは decide で証明可能
   - 一般の k に対する帰納法は v2 の性質に関する補題が必要
   - 帰納ステップの核心: v2(a + b) の評価（a と b の v2 が異なる場合）

5. コラッツ予想への含意:
   Syracuse 写像 T(n) = (3n+1)/2^{v2(3n+1)} における 1ステップの
   対数的変化は log2(3) - v2 ≈ 1.585 - v2。
   E[v2] = 2 > log2(3) ≈ 1.585 なので、平均的には対数スケールで減少。
   これが「ほとんど全ての n でコラッツ予想が成立する」根拠の中核。
""")


if __name__ == "__main__":
    main()
