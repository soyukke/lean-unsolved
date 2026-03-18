"""
探索: Plünnecke-Ruzsa不等式の数値検証

A が有限集合のとき、|nA| ≤ (|A+A|/|A|)^n · |A| (Plünnecke-Ruzsa)
"""
from itertools import combinations


def sumset(A):
    return set(a + b for a in A for b in A)


def iterated_sumset(A, n):
    """n-fold sumset: nA = A + A + ... + A"""
    result = set(A)
    for _ in range(n - 1):
        result = set(a + b for a in result for b in A)
    return result


def productset(A):
    return set(a * b for a in A for b in A)


def main():
    print("=== Plünnecke-Ruzsa不等式の数値検証 ===\n")

    test_sets = {
        "等差数列 {1..10}": list(range(1, 11)),
        "等比数列 {1,2,4,8,16}": [1, 2, 4, 8, 16],
        "ランダム風 {1,3,7,12,20}": [1, 3, 7, 12, 20],
        "稠密集合 {1,2,3,4,5}": [1, 2, 3, 4, 5],
    }

    for name, A in test_sets.items():
        A_set = set(A)
        AA = sumset(A_set)
        PP = productset(A_set)
        doubling = len(AA) / len(A_set)
        print(f"{name}: |A|={len(A_set)}, |A+A|={len(AA)}, |A·A|={len(PP)}, "
              f"doubling={doubling:.3f}")

        for n in [2, 3, 4]:
            nA = iterated_sumset(A_set, n)
            bound = doubling ** n * len(A_set)
            print(f"  |{n}A|={len(nA)}, PR bound={bound:.1f}, "
                  f"ratio={len(nA)/bound:.3f}")
        print()

    # Sum-product comparison
    print("=== Sum-Product 比較 ===\n")
    for n in [5, 10, 20, 50]:
        A = set(range(1, n + 1))
        ss = sumset(A)
        ps = productset(A)
        print(f"|A|={n}: |A+A|={len(ss)}, |A·A|={len(ps)}, "
              f"max/|A|={max(len(ss), len(ps))/n:.2f}")


if __name__ == "__main__":
    main()
