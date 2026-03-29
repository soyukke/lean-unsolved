#!/usr/bin/env python3
"""
探索194 最終確認: 肥沃率2/3の精密な証明と既知の区別
"""

# P(v2 奇数) = sum_{k=0}^infty P(v2=2k+1) = sum 1/2^{2k+1} = (1/2)/(1-1/4) = 2/3
# P(v2 偶数) = sum_{k=1}^infty P(v2=2k) = sum 1/2^{2k} = (1/4)/(1-1/4) = 1/3

# 確認
from fractions import Fraction

p_v2_odd = Fraction(0)
p_v2_even = Fraction(0)
for k in range(50):
    p_v2_odd += Fraction(1, 2**(2*k+1))
    if k >= 1:
        p_v2_even += Fraction(1, 2**(2*k))
    
print("P(v2(3n+1) 奇数) =", p_v2_odd, "=", float(p_v2_odd))
print("P(v2(3n+1) 偶数) =", p_v2_even, "=", float(p_v2_even))
print("合計:", p_v2_odd + p_v2_even)

print()
print("つまり:")
print("  syracuse(n) ≡ 5 (mod 6) となる確率 = 2/3")
print("  syracuse(n) ≡ 1 (mod 6) となる確率 = 1/3")
print()
print("肥沃率の意味:")
print("  像の mod 6 = 5 (mod3=2) のとき j=1逆像 (2m-1)/3 が存在")
print("  像の mod 6 = 1 (mod3=1) のとき j=2逆像 (4m-1)/3 が存在")
print("  両方とも逆像あり → 肥沃率 = 2/3 + 1/3 = 1... いや、")
print()
print("  肥沃率の正確な定義: 任意の奇数 m に対して")
print("  P(m%3 ≠ 0) = 2/3 (自然密度)")
print("  これは syracuse の像とは無関係に、逆像 n が存在するための必要十分条件")
print()

# 既知 vs 新発見の区別
print("=" * 70)
print("既知の結果 vs 新発見の区別")
print("=" * 70)
print()
print("[既知・形式化済み]")
print("  - syracuse_not_div_three: Syracuse の像は3の倍数でない")
print("  - syracuse_four_mul_add_one: syracuse(4n+1) = syracuse(n)")
print("  - collatzStep_indeg_le_two: 入次数 <= 2")
print("  - v2(3n+1)=1 ⟺ n≡3 (mod 4)")
print()
print("[新発見 (本探索)]")
print("  1. syracuse(n) mod 6 は v2(3n+1) の偶奇で完全決定")
print("     v2奇 → mod6=5, v2偶 → mod6=1")
print("  2. 具体的逆像の構成:")
print("     m≡5(mod6) → n=(2m-1)/3 が逆像 (v2(3n+1)=1で)")
print("     m≡1(mod6) → n=(4m-1)/3 が逆像 (v2(3n+1)=2で)")
print("  3. fertile_iff: 逆像存在 ⟺ m%3≠0 の完全な同値証明")
print("  4. mod18遷移行列がmod6で退化する構造の発見")
print("  5. P(v2奇)=2/3 と P(v2偶)=1/3 の級数的解釈")

# 既存の syracuse_mod3_eq の確認
print()
print("[部分的に既知]")
print("  - syracuse_mod3_eq は Structure.lean に存在する可能性")
print("    (v2=1のケースは syracuse_ascent_mod3 として証明済み)")
print("  - 一般の v2 に対する mod3 の結果は新しい")

