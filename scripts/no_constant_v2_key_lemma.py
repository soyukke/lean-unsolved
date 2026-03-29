#!/usr/bin/env python3
"""
核心補題の厳密検証:
  3^k + 2^c * G_k(c) = G_{k+1}(c)

ここで G_{k+1}(c) = 3*G_k(c) + 2^{ck}

すなわち: 3^k + 2^c * G_k = 3*G_k + 2^{ck}
       → 3^k = 3*G_k + 2^{ck} - 2^c*G_k
       → 3^k = (3 - 2^c)*G_k + 2^{ck}
       → 3^k + (2^c - 3)*G_k = 2^{ck}

これは generalAscentConst_mul そのもの!
"""

def G(c, k):
    if k == 0:
        return 0
    return 3 * G(c, k-1) + 2**(c*(k-1))

print("=== 核心補題: 3^k + 2^c * G_k(c) = G_{k+1}(c) の検証 ===\n")

for c in range(1, 7):
    for k in range(0, 8):
        lhs = 3**k + 2**c * G(c, k)
        rhs = G(c, k+1)
        match = "OK" if lhs == rhs else "FAIL"
        if match == "FAIL":
            print(f"c={c}, k={k}: LHS={lhs}, RHS={rhs}, {match}")
    print(f"c={c}: 全て OK")

print("\n=== generalAscentConst_mul の検証: G_k*(2^c-3) + 3^k = 2^{ck} ===\n")

for c in range(2, 7):
    for k in range(0, 8):
        lhs = G(c, k) * (2**c - 3) + 3**k
        rhs = 2**(c*k)
        match = "OK" if lhs == rhs else "FAIL"
        if match == "FAIL":
            print(f"c={c}, k={k}: LHS={lhs}, RHS={rhs}, {match}")
    print(f"c={c}: 全て OK")

print("\n=== サイクル排除の最終ステップ ===\n")
print("""
前提:
  hf:   2^{cp} * n = 3^p * n + G_p(c)
  hgac: G_p(c) * (2^c-3) + 3^p = 2^{cp}

結合:
  hf の両辺に (2^c-3) を掛ける:
    (2^{cp} * n) * (2^c-3) = (3^p * n + G_p) * (2^c-3)
    = 3^p * n * (2^c-3) + G_p * (2^c-3)

  hgac から G_p*(2^c-3) = 2^{cp} - 3^p:
    2^{cp} * n * (2^c-3) = 3^p * n * (2^c-3) + 2^{cp} - 3^p

  加法形式に書き換え:
    2^{cp} * n * (2^c-3) + 3^p = 3^p * n * (2^c-3) + 2^{cp}

  M = n * (2^c-3) とおくと:
    2^{cp} * M + 3^p = 3^p * M + 2^{cp}

  整理: 2^{cp} * M - 2^{cp} = 3^p * M - 3^p
    → 2^{cp} * (M-1) = 3^p * (M-1)

  自然数なので加法形式:
    2^{cp} * M + 3^p = 3^p * M + 2^{cp}

  M = 1 のとき: 2^{cp} + 3^p = 3^p + 2^{cp}  ← 成立

  M > 1 のとき:
    2^{cp} * M > 2^{cp} (M >= 2)
    3^p * M + 2^{cp} = 3^p * M + 2^{cp}

    2^{cp} * M + 3^p vs 3^p * M + 2^{cp}

    M >= 2 で c >= 3 なら 2^{cp} >= 8^p > 3^p なので:
    2^{cp} * M > 3^p * M → 2^{cp} * M + 3^p > 3^p * M + 3^p
    また 3^p < 2^{cp} → ... もっと丁寧に

    (2^{cp} - 3^p) * M = 2^{cp} - 3^p
    これは自然数の引き算で、2^{cp} > 3^p (c >= 2, p >= 1) なので
    M = 1 が必要。

    Lean では引き算を避けたいので:
    2^{cp} * M + 3^p = 3^p * M + 2^{cp}
    ⟺ 2^{cp} * (M - 1) = 3^p * (M - 1)  ... でも引き算

    omega / nlinarith で M = 1 を導くのが最善。

    あるいは:
    M >= 2 を仮定して矛盾を導く。
    M >= 2 → 2^{cp} * M >= 2 * 2^{cp}
    → 2^{cp} * M + 3^p >= 2 * 2^{cp} + 3^p
    → 3^p * M + 2^{cp} < (2^{cp}) * M + 2^{cp}   (3^p < 2^{cp})
    = (M+1) * 2^{cp} <= (M+1) * 2^{cp}
    ... 矛盾の導出が面倒。

    最も簡単: nlinarith に丸投げ。
    nlinarith が解けない場合:
      have : (2^{cp} - 3^p) * M = 2^{cp} - 3^p
      have : M = 1    (Nat.eq_one_of_pos_of_self_mul_eq)
""")

# 自然数での最終ステップの検証
print("\n=== 自然数演算での等式 ===\n")
for c in [3, 4, 5]:
    for p in [1, 2, 3]:
        for n in range(1, 5):
            M = n * (2**c - 3)
            lhs = 2**(c*p) * M + 3**p
            rhs = 3**p * M + 2**(c*p)
            if lhs == rhs:
                print(f"c={c}, p={p}, n={n}: M={M}, LHS=RHS={lhs} ← M=1? {M==1}")

print("\n=== nlinarith の入力となる項の確認 ===\n")
print("""
Lean形式化の最終ステップ（omega/nlinarith向け）:

前提（全て自然数の等式・不等式）:
  hf:       2^{cp} * n = 3^p * n + G_p
  hgac:     G_p * (2^c - 3) + 3^p = 2^{cp}
  hn:       n >= 1
  hc:       c >= 3   (→ 2^c - 3 >= 5)
  hp:       p >= 1
  h2cp_gt:  2^{cp} > 3^p

目標: False

方法1: nlinarith [hf, hgac, hn, hc, hp, h2cp_gt] で直接

方法2: 中間変数を展開
  have h1: G_p * (2^c - 3) = 2^{cp} - 3^p := by omega (hgac から)
  have h2: (2^{cp} - 3^p) * n = G_p := by omega (hf から)
  -- h1 と h2 を組み合わせ:
  -- G_p * (2^c - 3) = 2^{cp} - 3^p = (2^{cp}-3^p)*n/n ... 面倒
  --
  -- 直接: h2 → G_p = (2^{cp}-3^p)*n
  --       h1 → (2^{cp}-3^p)*n*(2^c-3) = 2^{cp}-3^p
  --       2^{cp}-3^p > 0 で割る → n*(2^c-3) = 1
  --       n >= 1, 2^c-3 >= 5 → n*(2^c-3) >= 5 > 1, 矛盾
  --
  -- Lean では Nat.mul_right_cancel で n*(2^c-3) = 1 を導ける

方法3: 全て加法形式のまま
  hf:       2^{cp} * n = 3^p * n + G_p
  hgac:     G_p * (2^c - 3) + 3^p = 2^{cp}

  hf * (2^c-3):
    (2^{cp} * n) * (2^c-3) = (3^p * n + G_p) * (2^c-3)
    = 3^p * n * (2^c-3) + G_p * (2^c-3)

  G_p * (2^c-3) = 2^{cp} - 3^p  (hgac)

  → 2^{cp} * n * (2^c-3) = 3^p * n * (2^c-3) + 2^{cp} - 3^p

  加法形式:
    2^{cp} * n * (2^c-3) + 3^p = 3^p * n * (2^c-3) + 2^{cp}

  ここで n*(2^c-3) >= 5 (hn, hc) なので
    LHS = 2^{cp} * n*(2^c-3) + 3^p >= 2^{cp} * 5 + 3^p
    RHS = 3^p * n*(2^c-3) + 2^{cp} <= 3^p * n*(2^c-3) + 2^{cp}

  LHS - RHS = (2^{cp} - 3^p)*(n*(2^c-3) - 1)
  n*(2^c-3) >= 5 > 1 かつ 2^{cp} > 3^p なので
  LHS > RHS, 矛盾。

  nlinarith hint:
    nlinarith [mul_comm (2^(c*p)) (n*(2^c-3)),
               mul_comm (3^p) (n*(2^c-3)),
               hf, hgac,
               Nat.mul_le_mul hn (show 2^c-3 >= 5 from ...)]
""")

# 実際に nlinarith が処理する形の確認
print("\n=== nlinarith 向けの不等式展開 ===\n")
for c in [3, 4]:
    for p in [1, 2]:
        for n in [1, 2, 3]:
            G_p = G(c, p)
            lhs_hf = 2**(c*p) * n  # = 3^p * n + G_p
            rhs_hf = 3**p * n + G_p
            lhs_hgac = G_p * (2**c - 3) + 3**p  # = 2^{cp}
            rhs_hgac = 2**(c*p)
            M = n * (2**c - 3)

            hf_ok = lhs_hf == rhs_hf
            hgac_ok = lhs_hgac == rhs_hgac

            if hf_ok and hgac_ok:
                eq_ok = (2**(c*p) * M + 3**p == 3**p * M + 2**(c*p))
                print(f"c={c}, p={p}, n={n}: M={M}, hf={hf_ok}, hgac={hgac_ok}, eq={eq_ok}")
