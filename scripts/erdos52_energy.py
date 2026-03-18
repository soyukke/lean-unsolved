"""
Erdős #52 探索5: 対数変換と加法エネルギー

- 加法エネルギー E(A) = |{(a,b,c,d) : a+b=c+d}| の計算
- 乗法エネルギー E*(A) = |{(a,b,c,d) : ab=cd}| の計算
- Balog-Szemeredi-Gowers 型の関係 E(A)·E*(A) と |A|^4 の比較
- A = {1,...,n}, 等比数列, smooth numbers での比較
"""

from collections import Counter, defaultdict
import math


def additive_energy(A):
    """
    加法エネルギー E(A) = |{(a,b,c,d) ∈ A^4 : a+b = c+d}|
    = Σ_s r_{A+A}(s)^2 where r(s) = |{(a,b): a+b=s}|
    """
    A_list = list(A)
    sum_count = Counter()
    for a in A_list:
        for b in A_list:
            sum_count[a + b] += 1
    return sum(c * c for c in sum_count.values())


def multiplicative_energy(A):
    """
    乗法エネルギー E*(A) = |{(a,b,c,d) ∈ A^4 : ab = cd}|
    = Σ_p r_{A·A}(p)^2 where r(p) = |{(a,b): ab=p}|
    """
    A_list = list(A)
    prod_count = Counter()
    for a in A_list:
        for b in A_list:
            prod_count[a * b] += 1
    return sum(c * c for c in prod_count.values())


def sumset_size(A):
    """|A+A|"""
    A_list = list(A)
    sums = set()
    for a in A_list:
        for b in A_list:
            sums.add(a + b)
    return len(sums)


def prodset_size(A):
    """|A·A|"""
    A_list = list(A)
    prods = set()
    for a in A_list:
        for b in A_list:
            prods.add(a * b)
    return len(prods)


def interval_set(n):
    """A = {1, 2, ..., n}"""
    return list(range(1, n + 1))


def geometric_set(n, ratio=2):
    """A = {1, r, r^2, ..., r^{n-1}} の等比数列"""
    return [ratio ** i for i in range(n)]


def smooth_numbers(bound, B):
    """B-smooth numbers up to bound"""
    # エラトステネスの篩の変形
    primes = []
    sieve = list(range(bound + 1))
    for i in range(2, bound + 1):
        if sieve[i] == i:  # prime
            if i <= B:
                primes.append(i)
            for j in range(i * i, bound + 1, i):
                if sieve[j] == j:
                    sieve[j] = i

    result = [1]
    for x in range(2, bound + 1):
        # xのすべての素因数がB以下か
        temp = x
        is_smooth = True
        while temp > 1:
            found = False
            for p in primes:
                if p > B:
                    break
                if temp % p == 0:
                    temp //= p
                    found = True
                    break
            if not found:
                is_smooth = False
                break
        if is_smooth:
            result.append(x)

    return result


def arithmetic_progression(n, start=1, diff=1):
    """等差数列"""
    return [start + i * diff for i in range(n)]


def analyze_set(name, A):
    """集合の和積エネルギー分析"""
    n = len(A)
    if n == 0:
        return

    ea = additive_energy(A)
    em = multiplicative_energy(A)
    ss = sumset_size(A)
    ps = prodset_size(A)
    n4 = n ** 4

    # Cauchy-Schwarz: E(A) ≥ |A|^4 / |A+A|
    cs_add_lower = n4 / ss
    cs_mul_lower = n4 / ps

    print(f"\n  {name} (|A|={n}):")
    print(f"    A = {A[:10]}{'...' if n > 10 else ''}")
    print(f"    |A+A| = {ss}, |A·A| = {ps}")
    print(f"    E(A)  = {ea:>12}, E*(A) = {em:>12}")
    print(f"    |A|^4 = {n4:>12}")
    print(f"    E(A)/|A|^3  = {ea/n**3:.4f}  (≥1, =n iff AP)")
    print(f"    E*(A)/|A|^3 = {em/n**3:.4f}  (≥1, =n iff GP)")
    print(f"    E(A)·E*(A)  = {ea*em:.2e}")
    print(f"    |A|^4       = {n4:.2e}")
    print(f"    E(A)·E*(A) / |A|^4 = {ea*em/n4:.4f}")

    # BSG的関係: E(A) ≤ |A+A|^3 (粗い形)
    # より正確: |A+A| ≥ |A|^4 / E(A) (Cauchy-Schwarz)
    print(f"    C-S下界: |A+A| ≥ |A|^4/E(A) = {cs_add_lower:.1f} (実際: {ss})")
    print(f"    C-S下界: |A·A| ≥ |A|^4/E*(A) = {cs_mul_lower:.1f} (実際: {ps})")

    return {
        'name': name, 'n': n,
        'ea': ea, 'em': em,
        'ss': ss, 'ps': ps,
        'ea_em_ratio': ea * em / n4,
    }


def verify_bsg_relation(results):
    """Balog-Szemeredi-Gowers 型の関係を検証"""
    print(f"\n  BSG型関係 E(A)·E*(A) ≥ |A|^4 の検証:")
    print(f"  {'集合':>25} | {'|A|':>4} | {'E(A)·E*(A)/|A|^4':>18} | {'成立':>4}")
    print("  " + "-" * 65)

    for r in results:
        holds = "Yes" if r['ea_em_ratio'] >= 1.0 else "NO"
        print(f"  {r['name']:>25} | {r['n']:>4} | {r['ea_em_ratio']:>18.4f} | {holds:>4}")


def log_transform_analysis():
    """対数変換による和積の関係分析"""
    print("\n\n■ 対数変換分析")
    print("  A の乗法構造は log(A) の加法構造に対応")
    print("  ab = c ⟺ log(a) + log(b) = log(c)")

    for n in [5, 8, 10, 15]:
        A = interval_set(n)
        log_A = [math.log(a) for a in A]

        ea_A = additive_energy(A)
        em_A = multiplicative_energy(A)

        # log(A) の加法エネルギーは A の乗法エネルギーに対応
        # 離散的には完全一致しないが、構造的に近い
        print(f"\n  A = {{1,...,{n}}}:")
        print(f"    E(A)/|A|^3 = {ea_A/n**3:.4f} (加法エネルギー密度)")
        print(f"    E*(A)/|A|^3 = {em_A/n**3:.4f} (乗法エネルギー密度)")
        print(f"    比率 E(A)/E*(A) = {ea_A/em_A:.4f}")
        print(f"    → 区間 {{1,...,n}} は加法的に構造化されている (E(A) > E*(A))")


def energy_tradeoff_analysis():
    """加法/乗法エネルギーのトレードオフ分析"""
    print("\n\n■ 加法/乗法エネルギーのトレードオフ")
    print("  「E(A)が大きい ⟹ |A+A|が小さい ⟹ |A·A|が大きい」を検証")

    results_table = []

    for n in [6, 8, 10, 12]:
        A_int = interval_set(n)
        A_geo = geometric_set(n, ratio=2)
        A_ap = arithmetic_progression(n, start=1, diff=3)

        # smooth numbers（n個選ぶ）
        all_smooth = smooth_numbers(n * 10, 5)
        A_smooth = all_smooth[:n] if len(all_smooth) >= n else all_smooth

        sets = [
            (f"{{1,...,{n}}}", A_int),
            (f"GP(2,{n})", A_geo),
            (f"AP(1,3,{n})", A_ap),
            (f"5-smooth({n})", A_smooth),
        ]

        print(f"\n  n = {n}:")
        print(f"  {'集合':>18} | {'E(A)/n^3':>9} | {'E*(A)/n^3':>10} | {'|A+A|':>6} | {'|A·A|':>6} | {'E·E*/n^4':>10}")
        print("  " + "-" * 75)

        for name, A in sets:
            if len(A) < n:
                continue
            A = A[:n]
            ea = additive_energy(A)
            em = multiplicative_energy(A)
            ss = sumset_size(A)
            ps = prodset_size(A)
            n3 = n ** 3
            n4 = n ** 4
            print(f"  {name:>18} | {ea/n3:>9.4f} | {em/n3:>10.4f} | {ss:>6} | {ps:>6} | {ea*em/n4:>10.4f}")
            results_table.append({
                'n': n, 'name': name,
                'ea_norm': ea / n3, 'em_norm': em / n3,
                'ss': ss, 'ps': ps,
                'product': ea * em / n4,
            })

    return results_table


def main():
    print("=" * 70)
    print("Erdős #52 探索5: 対数変換と加法エネルギー")
    print("=" * 70)

    # --- 基本分析 ---
    print("\n■ 各種集合の加法/乗法エネルギー分析")

    all_results = []

    for n in [5, 8, 10]:
        print(f"\n{'='*50}")
        print(f"n = {n}")

        # {1,...,n}
        r = analyze_set(f"{{1,...,{n}}}", interval_set(n))
        if r:
            all_results.append(r)

        # 等比数列
        r = analyze_set(f"GP(2,{n})", geometric_set(n, 2))
        if r:
            all_results.append(r)

        # 等比数列 (比3)
        r = analyze_set(f"GP(3,{n})", geometric_set(n, 3))
        if r:
            all_results.append(r)

        # smooth numbers
        all_smooth = smooth_numbers(n * 15, 5)
        sm = all_smooth[:n]
        r = analyze_set(f"5-smooth({n})", sm)
        if r:
            all_results.append(r)

        # 等差数列
        r = analyze_set(f"AP(1,2,{n})", arithmetic_progression(n, 1, 2))
        if r:
            all_results.append(r)

    # --- BSG関係の検証 ---
    print(f"\n\n{'='*70}")
    print("■ Balog-Szemeredi-Gowers 型関係の検証")
    verify_bsg_relation(all_results)

    # --- 対数変換 ---
    print(f"\n{'='*70}")
    log_transform_analysis()

    # --- トレードオフ分析 ---
    print(f"\n{'='*70}")
    energy_tradeoff_analysis()

    # --- エネルギーと和積サイズの関係 ---
    print(f"\n\n{'='*70}")
    print("■ Cauchy-Schwarz不等式による和積下界の厳しさ分析")
    print("  |A+A| ≥ |A|^4/E(A), |A·A| ≥ |A|^4/E*(A)")
    print("  → E(A)とE*(A)が同時に大きくなれない場合、")
    print("    |A+A|·|A·A| ≥ |A|^8/(E(A)·E*(A))")
    print("  → E(A)·E*(A) ≤ |A|^4·|A+A|·|A·A| (CS x2)")

    for n in [8, 10, 12]:
        print(f"\n  n={n}:")
        sets = [
            (f"{{1,...,{n}}}", interval_set(n)),
            (f"GP(2,{n})", geometric_set(n, 2)),
        ]
        for name, A in sets:
            ea = additive_energy(A)
            em = multiplicative_energy(A)
            ss = sumset_size(A)
            ps = prodset_size(A)
            n_val = len(A)

            # |A+A|·|A·A| の下界
            product_lower = n_val ** 8 / (ea * em)
            actual_product = ss * ps

            print(f"    {name}: |A+A|·|A·A| = {actual_product}, CS下界 = {product_lower:.1f}")
            print(f"      実際/下界 = {actual_product/product_lower:.4f}")

    # --- まとめ ---
    print(f"\n\n{'='*70}")
    print("■ まとめ")
    print("  1. 区間 {1,...,n} は E(A) が大きく E*(A) が相対的に小さい")
    print("     → 加法的に構造化 → |A+A| は小さいが |A·A| は大きい")
    print("  2. 等比数列は E*(A) が大きく E(A) が小さい")
    print("     → 乗法的に構造化 → |A·A| は小さいが |A+A| は大きい")
    print("  3. smooth numbers は両方のエネルギーがやや高い")
    print("     → 和と積の両方がやや小さい（和積の「敵」）")
    print("  4. BSG型関係 E(A)·E*(A) ≥ |A|^4 は全ケースで成立")
    print("     → これは |A+A| と |A·A| の同時最小化の障壁")
    print("  5. 対数変換により、乗法構造の分析を加法構造に帰着可能")
    print("     → Erdős-Szemerédi予想の本質は")
    print("       「加法と乗法が同時に退化できない」ことの定量化")


if __name__ == "__main__":
    main()
