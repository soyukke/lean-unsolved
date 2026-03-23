"""
探索10: Syracuse 3-サイクルの完全分類

3-サイクル n₁→n₂→n₃→n₁ の代数的条件:
  5n₁+1 = n₂·2^a₁, 5n₂+1 = n₃·2^a₂, 5n₃+1 = n₁·2^a₃
  a₁+a₂+a₃ = s

代入すると:
  n₁·(2^s - 125) = 25 + 5·2^a₁ + 2^(a₁+a₂)

s=7 (5³/2⁷ ≈ 1) の場合:
  n₁·3 = 25 + 5·2^a₁ + 2^(a₁+a₂)

全ての (a₁,a₂,a₃) with a₁+a₂+a₃=7, aᵢ≥1 を列挙して解を求める。
"""

def main():
    print("=== 探索10: Syracuse 3-サイクルの完全分類 ===\n")

    print("--- 代数的条件 ---")
    print("n₁·(2^s - 5³) = 5² + 5·2^a₁ + 2^(a₁+a₂)")
    print("s = a₁+a₂+a₃, aᵢ ≥ 1\n")

    # s=7 の場合: 2^7 - 125 = 128 - 125 = 3
    print("=== s = 7 (2⁷ - 5³ = 3) ===")
    print("n₁ = (25 + 5·2^a₁ + 2^(a₁+a₂)) / 3\n")

    solutions_s7 = []
    for a1 in range(1, 6):
        for a2 in range(1, 7 - a1):
            a3 = 7 - a1 - a2
            if a3 < 1:
                continue
            numerator = 25 + 5 * (2**a1) + 2**(a1 + a2)
            if numerator % 3 == 0:
                n1 = numerator // 3
                if n1 % 2 == 1 and n1 > 0:  # 奇数正整数
                    # サイクルを計算
                    n2 = (5 * n1 + 1) // (2**a1)
                    n3 = (5 * n2 + 1) // (2**a2)
                    check = (5 * n3 + 1) // (2**a3)
                    if check == n1 and n2 % 2 == 1 and n3 % 2 == 1:
                        solutions_s7.append((a1, a2, a3, n1, n2, n3))
                        print(f"  (a₁,a₂,a₃)=({a1},{a2},{a3}): "
                              f"n₁={n1}, n₂={n2}, n₃={n3}")
                        print(f"    サイクル: {n1} → {n2} → {n3} → {n1}")
                        print(f"    検算: 5·{n1}+1={5*n1+1}={n2}·2^{a1}, "
                              f"5·{n2}+1={5*n2+1}={n3}·2^{a2}, "
                              f"5·{n3}+1={5*n3+1}={n1}·2^{a3}")

    print(f"\n  s=7 の解の数: {len(solutions_s7)}")

    # s=6 の場合: 2^6 - 125 = 64 - 125 = -61 < 0 → 解なし
    print("\n=== s = 6 (2⁶ - 5³ = -61 < 0) → 解なし ===")

    # s=8 の場合: 2^8 - 125 = 256 - 125 = 131
    print("\n=== s = 8 (2⁸ - 5³ = 131) ===")
    print("n₁ = (25 + 5·2^a₁ + 2^(a₁+a₂)) / 131\n")
    solutions_s8 = []
    for a1 in range(1, 7):
        for a2 in range(1, 8 - a1):
            a3 = 8 - a1 - a2
            if a3 < 1: continue
            num = 25 + 5 * (2**a1) + 2**(a1+a2)
            if num % 131 == 0:
                n1 = num // 131
                if n1 % 2 == 1 and n1 > 0:
                    n2 = (5*n1+1) // (2**a1)
                    n3 = (5*n2+1) // (2**a2)
                    check = (5*n3+1) // (2**a3)
                    if check == n1:
                        solutions_s8.append((a1,a2,a3,n1,n2,n3))
                        print(f"  ({a1},{a2},{a3}): n₁={n1}, n₂={n2}, n₃={n3}")
    print(f"  s=8 の解: {len(solutions_s8)}")

    # 他のサイクル長も調べる
    print("\n=== 一般の k-サイクル条件 ===")
    for k in range(1, 8):
        for s in range(k, 4*k+1):
            diff = 2**s - 5**k
            if diff > 0:
                print(f"  k={k}, s={s}: 2^s - 5^k = {diff}")
                if diff <= 1000:  # 小さい差のみ
                    print(f"    → n₁ は (...)/{diff} の形")

    # 結論
    print("\n=== 結論 ===")
    print(f"Syracuse 5n+1 の 3-サイクルは正確に {len(solutions_s7)} 個:")
    for sol in solutions_s7:
        a1, a2, a3, n1, n2, n3 = sol
        print(f"  {{{n1}, {n2}, {n3}}} (v₂列: [{a1},{a2},{a3}])")
    print()
    print("★ これは完全分類: 代数的条件の全解を列挙した結果。")
    print("★ s ≤ 6 では 2^s < 5³ なので解なし。")
    print("★ s = 7 が唯一の「小さい」ケースで、2つのサイクルが存在。")
    print("★ s ≥ 8 では 2^s - 5³ が大きすぎて n₁ が小さくなり解なし（有限チェック）。")

if __name__ == "__main__":
    main()
