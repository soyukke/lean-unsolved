#!/usr/bin/env python3
"""
探索189: 全v_i=cサイクル排除の数学的分析

Syracuse反復で全ステップ v2(3*n_i+1) = c (定数) のサイクルは不可能であることの検証。

各ステップで v2 = c なら:
  T(n) = (3n+1) / 2^c

p-サイクル T^p(n) = n の場合:
  2^{cp} * T^p(n) = 3^p * n + C_p(c)

ここで C_p(c) は漸化式:
  C_0(c) = 0
  C_{p+1}(c) = 3 * C_p(c) + 2^{cp}

閉じた形: C_p(c) = (3^p - 2^{cp}) / (3 - 2^c)
         = (2^{cp} - 3^p) / (2^c - 3)   (c >= 2 のとき)

T^p(n) = n より:
  2^{cp} * n = 3^p * n + C_p(c)
  n * (2^{cp} - 3^p) = C_p(c)
  n = C_p(c) / (2^{cp} - 3^p)
  n = 1 / (2^c - 3)    (C_p(c) = (2^{cp}-3^p)/(2^c-3) を代入)

c=1: 2^c-3 = -1 → n = -1 (非正数、排除済み: no_all_ascent_cycle)
c=2: 2^c-3 = 1  → n = 1  (自明サイクル)
c>=3: 2^c-3 >= 5 → n = 1/5, 1/13, ... (非整数、排除)
"""

import math

print("=== 全v_i=cサイクル排除の分析 ===\n")

# c の各値での分析
for c in range(1, 10):
    denom = 2**c - 3
    print(f"c={c}: 2^c-3 = {denom}")
    if denom == 0:
        print(f"  → 分母0: C_p(c)/0 は不定")
    elif denom < 0:
        print(f"  → n = 1/{denom} = {1/denom:.4f} (負数、自然数サイクルには不可)")
    elif denom == 1:
        print(f"  → n = 1/{denom} = 1 (自明サイクル: T(1)=(3+1)/4=1)")
    else:
        print(f"  → n = 1/{denom} (非整数、不可)")
    print()

print("\n=== C_p(c) の漸化式検証 ===\n")

def ascent_const_general(p, c):
    """C_p(c) = 漸化式で計算"""
    result = 0
    for k in range(p):
        result = 3 * result + 2**(c*k)
    return result

def ascent_const_closed(p, c):
    """C_p(c) = (2^{cp} - 3^p) / (2^c - 3)  (c >= 2)"""
    numer = 2**(c*p) - 3**p
    denom = 2**c - 3
    if denom == 0:
        return None
    return numer // denom

# 漸化式と閉じた形の一致検証
print("p  c  recurrence  closed_form  match?")
for c in range(2, 6):
    for p in range(1, 8):
        rec = ascent_const_general(p, c)
        closed = ascent_const_closed(p, c)
        if closed is not None:
            match = "OK" if rec == closed else "FAIL"
            print(f"{p}  {c}  {rec:>12d}  {closed:>12d}  {match}")
    print()

print("\n=== サイクル方程式の検証 ===\n")
print("T^p(n)=n のとき: n*(2^{cp}-3^p) = C_p(c)")
print("n = C_p(c) / (2^{cp}-3^p) = 1/(2^c-3)\n")

for c in range(2, 6):
    denom = 2**c - 3
    for p in range(1, 6):
        C_p = ascent_const_general(p, c)
        coeff = 2**(c*p) - 3**p
        if coeff != 0:
            n_exact = C_p / coeff
            print(f"c={c}, p={p}: C_p={C_p}, coeff={coeff}, n = {C_p}/{coeff} = {n_exact:.6f}, 1/(2^c-3) = {1/denom:.6f}")
    print()

print("\n=== 既存 no_all_ascent_cycle (c=1) との関係 ===\n")
print("c=1 のとき:")
print("  ascentConst k + 2^k = 3^k  →  ascentConst k = 3^k - 2^k")
print("  T^p(n)=n → 2^p*n = 3^p*n + (3^p-2^p)")
print("  → n*(2^p-3^p) = 3^p-2^p")
print("  → n*(-1)*(3^p-2^p) = 3^p-2^p")
print("  → n = -1 (負数、自然数では不可)")
print("  → 2^p*(n+1) = 3^p*(n+1) → 2^p=3^p で矛盾 (p>=1)")
print()

print("c>=2 の一般化:")
print("  各ステップ T_c(n) = (3n+1)/2^c")
print("  p回反復: 2^{cp} * T_c^p(n) = 3^p*n + C_p(c)")
print("  T_c^p(n)=n: n*(2^{cp}-3^p) = C_p(c)")
print("  C_p(c) = (2^{cp}-3^p)/(2^c-3)")
print("  → n = 1/(2^c-3)")
print()

print("=== Lean形式化で必要な補題 ===\n")

# c=2: T(n) = (3n+1)/4, n=1 のサイクル
# T(1) = 4/4 = 1. 自明。
print("c=2: T(1) = (3*1+1)/4 = 1. 自明な不動点。")

# c>=3: n=1/(2^c-3) は非整数 → サイクル不可
# 証明: (2^c-3) >= 5 で 1/(2^c-3) < 1 なので n >= 1 と矛盾
print("c>=3: 2^c-3 >= 5 → n=1/(2^c-3) < 1 → n>=1 と矛盾")
print()

print("=== 形式化構造 ===\n")
print("""
形式化の方針:
1. constV2Ascents(c, n, k) の定義: 各ステップで v2(3*n_i+1) = c
2. 一般乗法公式: 2^{ck} * T_c^k(n) = 3^k * n + generalAscentConst(c, k)
3. generalAscentConst(c, k) の閉じた形: (2^{ck} - 3^k) / (2^c - 3)
4. サイクル条件 T^p(n)=n → n*(2^{cp}-3^p) = C_p
5. n = 1/(2^c-3)
6. c=1: 2^c-3 = -1 → 既存定理で排除
7. c=2: n=1 は自明（syracuse不動点）
8. c>=3: 2^c-3 >= 5, n < 1 で矛盾

ただし注意:
- 自然数でやるので「1/(2^c-3)は整数でない」ではなく
  「n*(2^c-3) = 1 を満たす自然数nは存在しない (2^c-3 >= 5のとき)」
  として形式化する方が簡単
""")

# generalAscentConst の Z (整数) での閉じた形検証
print("=== Z上での検証: n*(2^{cp}-3^p) = C_p(c) で n=1/(2^c-3) ===\n")
for c in [3, 4, 5]:
    for p in [1, 2, 3, 5, 10]:
        numer = 2**(c*p) - 3**p
        denom = 2**c - 3
        C_p = ascent_const_general(p, c)
        # C_p * (2^c - 3) = 2^{cp} - 3^p を検証
        lhs = C_p * denom
        rhs = numer
        print(f"c={c}, p={p}: C_p*(2^c-3) = {lhs}, 2^{{cp}}-3^p = {rhs}, match={lhs==rhs}")
    print()

print("=== Lean形式化の設計（完全版） ===\n")
print("""
-- ============================================================
-- Phase 1: 定義
-- ============================================================

-- 一般的な定数c上昇定数
def generalAscentConst (c : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * generalAscentConst c k + 2 ^ (c * k)

-- 全ステップで v2 = c であるという条件
def allV2Eq (c : ℕ) (n : ℕ) (k : ℕ) : Prop :=
  ∀ i, i < k → v2 (3 * syracuseIter i n + 1) = c

-- ============================================================
-- Phase 2: 一般乗法公式
-- ============================================================

-- 乗法公式: allV2Eq c n k → 2^{ck} * T^k(n) = 3^k * n + generalAscentConst c k
-- 帰納法で証明。各ステップ: T(n_i) = (3*n_i+1)/2^c

-- ============================================================
-- Phase 3: 閉じた形の等式
-- ============================================================

-- generalAscentConst c k * (2^c - 3) = 2^{ck} - 3^k   (c >= 2)
-- 帰納法で証明:
-- k=0: 0*(2^c-3) = 1-1 = 0 OK
-- k+1: (3*G_k + 2^{ck}) * (2^c-3)
--     = 3*G_k*(2^c-3) + 2^{ck}*(2^c-3)
--     = 3*(2^{ck}-3^k) + 2^{c(k+1)} - 3*2^{ck}
--     = 3*2^{ck} - 3^{k+1} + 2^{c(k+1)} - 3*2^{ck}
--     = 2^{c(k+1)} - 3^{k+1}

-- ============================================================
-- Phase 4: サイクル排除
-- ============================================================

-- T^p(n) = n かつ allV2Eq c n p → n*(2^{cp}-3^p) = generalAscentConst c p
-- → n*(2^{cp}-3^p) = (2^{cp}-3^p)/(2^c-3)
-- → n*(2^c-3) = 1
-- c >= 3 → 2^c-3 >= 5 → n*(2^c-3) >= 5 > 1, 矛盾
-- c = 2 → n = 1 (自明不動点)
-- c = 1 → 既存 no_all_ascent_cycle
""")
