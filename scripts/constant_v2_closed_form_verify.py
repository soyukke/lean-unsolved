#!/usr/bin/env python3
"""
全 v_i = c パターンの閉じた形の精密検証

前のスクリプトで「n = 2^c / (2^c - 3)」という閉じた形を導出したが、
c=2 の数値計算で n=1 (C=D) となり不整合があった。
等比級数の計算を精密に再検証する。
"""

from fractions import Fraction

def compute_C_exact(vs):
    """C_p を厳密に計算"""
    p = len(vs)
    C = Fraction(0)
    for j in range(p):
        sigma_j = sum(vs[j+1:])
        C += Fraction(3)**j * Fraction(2)**sigma_j
    return C

def compute_D_exact(vs):
    """D = 2^J - 3^p を厳密に計算"""
    p = len(vs)
    J = sum(vs)
    return Fraction(2)**J - Fraction(3)**p

print("=" * 80)
print("全 v_i = c パターンの閉じた形の精密検証")
print("=" * 80)

# === 等比級数の再計算 ===
print("\n--- 等比級数の再計算 ---")
print("全 v_i = c のとき sigma_j = c * (p - 1 - j) + c - c = ?")
print("正確には: sigma_j = v_{j+1} + v_{j+2} + ... + v_p = c * (p - j - 1) + c")
print("いや、sigma_j = v_{j+1} + ... + v_p")
print("j=0: sigma_0 = v_1+v_2+...+v_p = cp (全部)")
print("j=1: sigma_1 = v_2+...+v_p = c(p-1)")
print("...")
print("j=p-1: sigma_{p-1} = v_p = c")
print("")
print("つまり sigma_j = c * (p - j)")
print("")
print("C_p = sum_{j=0}^{p-1} 3^j * 2^{c(p-j)}")
print("    = 2^{cp} + 3 * 2^{c(p-1)} + 9 * 2^{c(p-2)} + ... + 3^{p-1} * 2^c")
print("    = 2^c * [2^{c(p-1)} + 3 * 2^{c(p-2)} + ... + 3^{p-1}]")
print("    = 2^c * sum_{j=0}^{p-1} 3^j * 2^{c(p-1-j)}")
print("    = 2^c * sum_{k=0}^{p-1} 3^{p-1-k} * 2^{ck}  (k = p-1-j)")
print("    = 2^c * sum_{k=0}^{p-1} (2^c)^k * 3^{p-1-k}")
print("")
print("sum_{k=0}^{p-1} (2^c)^k * 3^{p-1-k} = (等比級数)")
print("  r = 2^c / 3 として")
print("  = 3^{p-1} * sum_{k=0}^{p-1} r^k")
print("  = 3^{p-1} * (r^p - 1) / (r - 1)")
print("  = 3^{p-1} * ((2^c/3)^p - 1) / (2^c/3 - 1)")
print("  = 3^{p-1} * (2^{cp}/3^p - 1) / ((2^c - 3)/3)")
print("  = 3^{p-1} * 3 * (2^{cp} - 3^p) / (3^p * (2^c - 3))")
print("  = (2^{cp} - 3^p) / (2^c - 3)")
print("")
print("よって C_p = 2^c * (2^{cp} - 3^p) / (2^c - 3)")
print("D = 2^{cp} - 3^p")
print("n = C_p / D = 2^c / (2^c - 3)")

# === 数値検証: 閉じた形 vs 直接計算 ===
print("\n\n--- 数値検証 ---")
for c in range(1, 8):
    print(f"\nc = {c}:")
    closed_n = Fraction(2**c, 2**c - 3) if 2**c != 3 else "undefined"
    print(f"  閉じた形: n = 2^{c} / (2^{c} - 3) = {closed_n}")

    for p in range(1, 8):
        vs = [c] * p
        C = compute_C_exact(vs)
        D = compute_D_exact(vs)

        if D == 0:
            print(f"  p={p}: D=0 (不可)")
            continue

        n_direct = C / D
        J = c * p

        # 閉じた形との比較
        if 2**c != 3:
            C_closed = Fraction(2**c) * (Fraction(2)**(c*p) - Fraction(3)**p) / (Fraction(2**c) - 3)
            D_exact = Fraction(2)**(c*p) - Fraction(3)**p
            n_closed = Fraction(2**c, 2**c - 3)

            match_C = (C == C_closed)
            match_n = (n_direct == n_closed)

            if not match_C or not match_n:
                print(f"  p={p}: C={C}, C_closed={C_closed}, MATCH_C={match_C}")
                print(f"         D={D}, n_direct={n_direct}, n_closed={n_closed}, MATCH_n={match_n}")
            else:
                print(f"  p={p}: n = {n_direct} (閉じた形と一致)")
        else:
            print(f"  p={p}: n = {n_direct} (2^c = 3 なので閉じた形なし)")

# === 核心: c=2 の詳細検証 ===
print("\n\n--- c=2 の詳細検証 ---")
c = 2
for p in range(1, 10):
    vs = [2] * p
    C = compute_C_exact(vs)
    D = compute_D_exact(vs)
    J = 2 * p
    print(f"p={p}: J={J}, C={C}, D={D}, C/D={C/D}")
    print(f"  2^c = {2**c}, 2^c - 3 = {2**c - 3}")
    print(f"  閉じた形 n = {Fraction(2**c, 2**c - 3)} = {Fraction(4, 1)}")
    print(f"  直接計算 n = {C/D}")
    print(f"  C_closed = 2^c * D / (2^c - 3) = 4 * {D} / 1 = {4*D}")
    print(f"  C == C_closed? {C == 4*D}")

# !! ここで不整合発見: 直接計算で n=1 なのに閉じた形で n=4
# 原因を突き止める

print("\n\n--- 不整合の原因調査 ---")
print("c=2, p=1:")
vs = [2]
# sigma_0 = v_1 = 2
# C = 3^0 * 2^{sigma_0} = 1 * 2^2 = 4?
# いや、sigma_0 = sum(vs[1:]) = 0!
# C = 3^0 * 2^0 = 1
# D = 2^2 - 3^1 = 1
# n = 1

print("sigma_j の定義を再確認:")
print("sigma_j = v_{j+1} + v_{j+2} + ... + v_p")
print("j は 0-indexed で j=0,...,p-1")
print("")
print("p=1, c=2:")
print("  j=0: sigma_0 = (nothing, since j+1=1 > p=1) = 0")
print("  C = 3^0 * 2^0 = 1")
print("  D = 2^2 - 3^1 = 1")
print("  n = 1")
print("")
print("p=2, c=2:")
print("  j=0: sigma_0 = v_1 = v[1] = 2 (0-indexed: vs[1])")
print("  j=1: sigma_1 = 0")
print("  C = 3^0 * 2^2 + 3^1 * 2^0 = 4 + 3 = 7")
print("  D = 2^4 - 3^2 = 16 - 9 = 7")
print("  n = 1")

print("\nしかし等比級数の計算では:")
print("C_p = sum_{j=0}^{p-1} 3^j * 2^{c(p-j)}")

for p in range(1, 5):
    c = 2
    print(f"\np={p}:")
    C_formula = 0
    C_actual = 0
    for j in range(p):
        sigma_j_formula = c * (p - j)  # 閉じた形で想定していた sigma_j
        sigma_j_actual = c * (p - j - 1)  # 正しい sigma_j (v_{j+1}+...+v_p)

        # 実は sigma_j = sum(vs[j+1:]) = c * (p - (j+1)) = c * (p - j - 1)
        # ただし j は 0-indexed で vs = [c, c, ..., c]

        term_formula = 3**j * 2**sigma_j_formula
        term_actual = 3**j * 2**sigma_j_actual
        C_formula += term_formula
        C_actual += term_actual
        print(f"  j={j}: sigma_j(formula)={sigma_j_formula}, sigma_j(actual)={sigma_j_actual}")
        print(f"         term(formula)={term_formula}, term(actual)={term_actual}")

    print(f"  C(formula) = {C_formula}, C(actual) = {C_actual}")
    J = c * p
    D = 2**J - 3**p
    print(f"  D = {D}")
    if D != 0:
        print(f"  n(formula) = {Fraction(C_formula, D)}, n(actual) = {Fraction(C_actual, D)}")

print("\n\n★★★ 不整合の原因 ★★★")
print("sigma_j の定義は v_{j+1} + ... + v_p")
print("j=0-indexed, vs = [v_1, v_2, ..., v_p] (1-indexed)")
print("Pythonでは vs[j+1:] なので:")
print("  j=0: sum(vs[1:]) = c*(p-1)")
print("  j=1: sum(vs[2:]) = c*(p-2)")
print("  ...")
print("  j=p-1: sum(vs[p:]) = 0")
print("")
print("つまり sigma_j = c * (p - 1 - j)  (NOT c*(p-j))")
print("")
print("正しい等比級数:")
print("  C_p = sum_{j=0}^{p-1} 3^j * 2^{c(p-1-j)}")
print("      = 2^{c(p-1)} + 3 * 2^{c(p-2)} + ... + 3^{p-1}")
print("      (NOT 2^{cp} + 3 * 2^{c(p-1)} + ...)")

# 正しい閉じた形
print("\n\n--- 正しい閉じた形の導出 ---")
print("C_p = sum_{j=0}^{p-1} 3^j * 2^{c(p-1-j)}")
print("    = sum_{k=0}^{p-1} 3^{p-1-k} * 2^{ck}  (k = p-1-j)")
print("    = sum_{k=0}^{p-1} 3^{p-1-k} * (2^c)^k")
print("")
print("2^c != 3 のとき:")
print("    = ((2^c)^p - 3^p) / (2^c - 3)")
print("    = (2^{cp} - 3^p) / (2^c - 3)")
print("")
print("D = 2^{cp} - 3^p (全 v_i=c のとき J = cp)")
print("")
print("n = C_p / D = (2^{cp} - 3^p) / ((2^c - 3) * (2^{cp} - 3^p))")
print("           = 1 / (2^c - 3)")
print("")
print("★★★ 正しい閉じた形: n = 1 / (2^c - 3) ★★★")

# 検証
print("\n検証:")
for c in range(1, 10):
    d = 2**c - 3
    if d == 0:
        print(f"  c={c}: 2^c - 3 = 0, 不定")
        continue
    n_closed = Fraction(1, d)
    print(f"  c={c}: n = 1 / (2^{c} - 3) = 1/{d} = {n_closed} = {float(n_closed):.6f}")

    # 直接計算との比較
    for p in [1, 2, 3]:
        vs = [c] * p
        C = compute_C_exact(vs)
        D = compute_D_exact(vs)
        if D != 0:
            n_direct = C / D
            match = n_closed == n_direct
            if not match:
                print(f"    p={p}: n_direct={n_direct}, MISMATCH!")
            # else: pass  # match

print("\n\n★★★ 修正された結論 ★★★")
print("全 v_i = c パターン (c >= 1, p >= 1):")
print("  n = 1 / (2^c - 3)")
print("")
print("整数条件: (2^c - 3) | 1 ⟺ 2^c - 3 ∈ {-1, 1}")
print("  2^c - 3 = -1 → 2^c = 2 → c = 1, n = 1/(-1) = -1")
print("  2^c - 3 = 1  → 2^c = 4 → c = 2, n = 1/1 = 1")
print("")
print("c=1: n = -1 (負の数、正整数サイクルでない)")
print("  しかし! Z_2 上では n = -1 = ...111 (2-adic) がサイクル点")
print("  → これは 2-adic での「自明な」固定点に対応")
print("")
print("c=2: n = 1 (自明なサイクル n=1)")
print("  → v2(3*1+1) = v2(4) = 2 → v2 整合!")
print("  → 1 → (3*1+1)/4 = 1 → 1 ... これは自明な不動点")
print("")
print("c >= 3: n = 1/(2^c - 3) は正だが非整数")
print("  → 排除")
print("")
print("★結論: 全 v_i = c パターンの「非自明」正奇数整数サイクルは不可能")
print("  c=2, n=1 の自明サイクル (不動点) のみが存在")
print("  これは既存の syracuse_unique_fixed_point で排除済み")

# === 前のスクリプトの誤りの修正 ===
print("\n\n--- 前スクリプトの sigma_j 誤りの原因特定 ---")
print("前スクリプトの等比級数計算で sigma_j = c*(p-j) としていたが、")
print("正しくは sigma_j = c*(p-1-j)。")
print("sigma_j は v_{j+1},...,v_p の和であり、v_j は含まない。")
print("p=1, j=0 のとき sigma_0 = 0 (vs[1:] = []) であり、")
print("sigma_0 = c*(p-0) = c は誤り。")
print("")
print("前スクリプトの compute_C_and_D は正しい実装だった (直接 sum(vs[j+1:]) を使用)。")
print("問題は Part 6 の「閉じた形」セクションの理論的分析のみ。")
print("数値結果は全て正しい。")

# === 新しい統一定理 ===
print("\n\n" + "=" * 80)
print("★ 正しい統一定理 (修正版)")
print("=" * 80)
print()
print("定理 (no_constant_v2_cycle):")
print("  p >= 1, c >= 1 のとき、全 v_i = c パターンのSyracuseサイクル方程式")
print("  (2^{cp} - 3^p) * n = C_p の唯一の正整数解は n = 1 (c=2 のとき)。")
print()
print("  n > 1 の正奇数整数解は存在しない。")
print()
print("証明:")
print("  sigma_j = c*(p-1-j) なので")
print("  C_p = sum_{j=0}^{p-1} 3^j * 2^{c(p-1-j)} = (2^{cp} - 3^p) / (2^c - 3)")
print("  n = C_p / D = 1 / (2^c - 3)")
print("  整数解条件: 2^c - 3 ∈ {-1, 1}")
print("  c=1: n=-1 (負), c=2: n=1 (自明)")
print()
print("Lean形式化の方針:")
print("  1. constantAscConst c p := sum_{j=0}^{p-1} 3^j * (2^c)^{p-1-j} を定義")
print("  2. constantAscConst c p = (2^{cp} - 3^p) / (2^c - 3) を証明")
print("     (等比級数の和)")
print("  3. サイクル条件 T^p(n) = n のとき n * (2^c - 3) = 1 を導出")
print("  4. c >= 3: 2^c - 3 >= 5 なので n * (2^c - 3) >= 5 > 1 矛盾")
print("     c = 2: n = 1 (自明)")
print("     c = 1: no_all_ascent_cycle で既に証明済 (別の方法)")
print()
print("  注: c=1 は特殊。D = 2^p - 3^p < 0 (p>=1) なので正の解がない。")
print("  一般公式 n = 1/(2^c-3) は c=1 で n = -1 を与え、")
print("  これは正ではないため自動的に排除。")
