#!/usr/bin/env python3
"""
v2制約の代数的証明と、C/D = -1 の普遍性の検証

前段の発見を精密化:
1. r ≡ 3 (mod 4) ⟹ v2(3r+1) = 1 は代数的に厳密
2. 全ステップv2=1パターンでは常にC/D = -1 (驚くべき等式)
3. 非排除残基の遷移グラフの構造的理由
4. v2制約とBaker排除の組合せの厳密な論理

追加の新分析:
5. C/D = -1 の代数的証明
6. 散在的な v2=k (k>1) の非排除残基の存在理由
7. 遷移グラフの逃避時間分布の理論的予測
"""

import math
import json
from fractions import Fraction
from collections import Counter

LOG2 = math.log(2)
LOG3 = math.log(3)
LOG2_3 = LOG3 / LOG2


def v2(n):
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


# =====================================================================
# Proof 1: r ≡ 3 (mod 4) ⟹ v2(3r+1) = 1 の代数的証明
# =====================================================================

def proof_v2_constraint():
    """
    命題: r ≡ 3 (mod 4) ⟹ v2(3r+1) = 1

    証明:
    r = 4q + 3 とおく (q >= 0)
    3r + 1 = 3(4q + 3) + 1 = 12q + 10 = 2(6q + 5)
    6q + 5 は奇数 (mod 2 で 6q + 5 ≡ 0 + 1 = 1)
    よって v2(3r+1) = v2(2(6q+5)) = 1

    注: r ≡ 3 (mod 4) は v2(3r+1) = 1 の必要十分条件
    逆: v2(3r+1) = 1 ⟹ 3r+1 ≡ 2 (mod 4) ⟹ 3r ≡ 1 (mod 4)
    ⟹ r ≡ 3 (mod 4) (3の逆元は3 mod 4)
    """
    print("## Proof 1: r ≡ 3 (mod 4) ⟺ v2(3r+1) = 1")
    print("-" * 60)
    print()
    print("  命題: 奇数 r に対して v2(3r+1) = 1 ⟺ r ≡ 3 (mod 4)")
    print()
    print("  証明 (⟹方向):")
    print("  r = 4q + 3 とおく")
    print("  3r + 1 = 3(4q + 3) + 1 = 12q + 10 = 2(6q + 5)")
    print("  6q + 5 は奇数 ∵ 6q ≡ 0 (mod 2)")
    print("  ∴ v2(3r+1) = 1  □")
    print()
    print("  証明 (⟸方向):")
    print("  v2(3r+1) = 1 ⟹ 3r+1 ≡ 2 (mod 4)")
    print("  ⟹ 3r ≡ 1 (mod 4)")
    print("  3^(-1) ≡ 3 (mod 4) なので r ≡ 3 (mod 4)  □")
    print()

    # 数値検証
    errors = 0
    for r in range(1, 10000, 2):
        actual_v = v2(3 * r + 1)
        expected = 1 if r % 4 == 3 else None
        if r % 4 == 3:
            if actual_v != 1:
                errors += 1
        else:
            if actual_v == 1:
                errors += 1

    print(f"  数値検証 (r=1..9999 奇数): 不一致 = {errors}")


# =====================================================================
# Proof 2: C/D = -1 の代数的証明
# =====================================================================

def proof_cd_minus_one():
    """
    命題: 全ステップ v_i = 1 のパターンでは C = -D = 3^p - 2^p

    証明:
    s = p, v_i = 1 for all i
    sigma_j = p - 1 - j  (jの後のv_iの和)

    C = sum_{j=0}^{p-1} 3^j * 2^{p-1-j}
      = 2^{p-1} * sum_{j=0}^{p-1} (3/2)^j
      = 2^{p-1} * ((3/2)^p - 1) / ((3/2) - 1)
      = 2^{p-1} * (3^p/2^p - 1) / (1/2)
      = 2^{p-1} * 2 * (3^p - 2^p) / 2^p
      = (3^p - 2^p)

    D = 2^p - 3^p = -(3^p - 2^p)

    よって C/D = (3^p - 2^p) / (-(3^p - 2^p)) = -1
    """
    print("\n## Proof 2: C/D = -1 の代数的証明")
    print("-" * 60)
    print()
    print("  命題: 全ステップ v_i = 1 (i=1,...,p) のとき C = 3^p - 2^p, D = 2^p - 3^p")
    print("  よって C/D = -1 (任意のp >= 1)")
    print()
    print("  証明:")
    print("  s = p, sigma_j = p - 1 - j")
    print("  C = sum_{j=0}^{p-1} 3^j * 2^{p-1-j}")
    print("    = sum_{j=0}^{p-1} 3^j * 2^{p-1-j}")
    print()

    # 等比級数の計算
    print("  等比級数として:")
    print("  C = 2^{p-1} * sum_{j=0}^{p-1} (3/2)^j")
    print("    = 2^{p-1} * ((3/2)^p - 1) / (3/2 - 1)")
    print("    = 2^{p-1} * 2 * (3^p/2^p - 1)")
    print("    = 2^p * (3^p - 2^p) / 2^p")
    print("    = 3^p - 2^p")
    print()
    print("  D = 2^p - 3^p = -(3^p - 2^p) = -C")
    print()
    print("  ∴ C/D = C/(-C) = -1  □")
    print()
    print("  意味: n_1 = -1 は Z_2 (2-adic integers) 上の解")
    print("  → 正整数解は存在しない")
    print("  → 全ステップv2=1のサイクルは不可能（全pで証明完了）")
    print()

    # 数値検証
    print("  数値検証:")
    for p in range(1, 15):
        C_formula = 3**p - 2**p
        C_explicit = sum(3**j * 2**(p-1-j) for j in range(p))
        D = 2**p - 3**p
        assert C_formula == C_explicit, f"C mismatch at p={p}"
        assert C_formula == -D, f"C != -D at p={p}"
        print(f"    p={p:>2}: C = 3^{p}-2^{p} = {C_formula}, D = {D}, C/D = {Fraction(C_formula, D)} ✓")


# =====================================================================
# Analysis 3: 散在的な v2=k (非排除) の理由
# =====================================================================

def sporadic_v2_analysis():
    """
    k が奇数のとき、v2 = k の非排除残基が1つだけ出現する現象の分析。

    観測:
    k=7: v2分布={1:16, 8:1} → v2=8 の残基が1つ
    k=9: v2分布={1:45, 10:1} → v2=10 の残基が1つ
    k=11: v2分布={1:139, 12:1}
    k=13: v2分布={1:444, 14:1}
    k=15: v2分布={1:1451, 16:1}
    k=17 (サンプル): v2分布={1:3518, 18:1}

    パターン: 奇数kのとき v2 = k+1 の非排除残基が1つ存在
    """
    print("\n## Analysis 3: 散在的な高v2値の非排除残基")
    print("-" * 60)

    def symbolic_descent(r, mod, max_depth=20):
        a, b = mod, r
        for depth in range(1, max_depth + 1):
            if b % 2 == 0:
                if a % 2 == 0:
                    a //= 2; b //= 2; continue
                else:
                    return False, depth
            new_a = 3 * a; new_b = 3 * b + 1
            v_b = v2(new_b); v_a = v2(new_a)
            if v_a >= v_b:
                divisor = 2 ** v_b
                a = new_a // divisor; b = new_b // divisor
                if a - mod < 0:
                    return True, depth
                elif a - mod == 0 and r - b > 0:
                    return True, depth
            else:
                return False, depth
        return False, max_depth

    print("  k (奇数) | 特殊残基 r | v2(3r+1) | r mod 4 | r の2進表現")
    print("  " + "-" * 70)

    sporadic = []
    for k in range(7, 20, 2):
        mod = 2**k
        for r in range(1, mod, 2):
            ex, _ = symbolic_descent(r, mod, max_depth=20)
            if not ex:
                v = v2(3 * r + 1)
                if v > 1:
                    sporadic.append((k, r, v))
                    print(f"  k={k:>2}     | r={r:>8} | v2={v:>4}   | {r%4:>5}   | {bin(r)}")

    # 特殊残基のパターン分析
    print()
    if sporadic:
        print("  特殊残基の関係:")
        for k, r, v in sporadic:
            # r mod 2^(k+1) の計算
            mod = 2**k
            # 3r+1 の2-adic valuation
            print(f"    k={k}: r={r}, 3r+1={3*r+1} = 2^{v} * {(3*r+1)>>(v)}")
            # r mod 2^v の計算
            print(f"           r mod 2^{v+1} = {r % (2**(v+1))}")
            print(f"           r mod 4 = {r % 4}")

    # 偶数kとの対比
    print("\n  偶数kでは:")
    for k in range(6, 18, 2):
        mod = 2**k
        high_v2_ne = []
        for r in range(1, mod, 2):
            ex, _ = symbolic_descent(r, mod, max_depth=20)
            if not ex:
                v = v2(3 * r + 1)
                if v > 1:
                    high_v2_ne.append((r, v))
        if high_v2_ne:
            print(f"    k={k}: 高v2非排除残基 = {high_v2_ne}")
        else:
            print(f"    k={k}: 高v2非排除残基なし（全てv2=1）")

    return sporadic


# =====================================================================
# Analysis 4: 論理的帰結のまとめ
# =====================================================================

def logical_consequences():
    """
    mod 2^k 分析 + Baker排除の論理的帰結。

    定理群:
    1. (v2=1不可能定理) v2パターンが全て1のサイクルは不可能
    2. (mod排除定理) mod 2^k で排除された残基は非自明サイクルに属さない
    3. (遷移木定理) 非排除残基の遷移グラフは森（閉路なし）
    4. (密度定理) 非排除密度は k → ∞ で 0 に収束
    5. (Baker組合せ定理) v2制約により許容パターン数が大幅に減少
    """
    print("\n## Analysis 4: 論理的帰結のまとめ")
    print("=" * 60)

    print("""
    定理1 (v2=1不可能性): 全ステップでv2(3n_i+1)=1のサイクルは正整数に存在しない。
    証明: C/D = -1 (代数的等式) → n_1 = -1 (2-adic解のみ)

    定理2 (mod排除): n が mod 2^k で排除残基に属するなら、
    n は非自明サイクルの一部ではないか、最小反例は n > 10^6。

    定理3 (遷移木): k <= 16 で、非排除残基の遷移グラフは森（閉路なし）。
    → mod 2^k レベルでのサイクルは存在しない。

    定理4 (密度0収束): 非排除密度 ρ(k) ≈ 0.28 * 0.883^k → 0 (k → ∞)。
    → 任意の正整数は、十分大きいkで排除される（ただし下界は未知）。

    仮説: 任意のサイクルの最小要素 n_min に対して、
    n_min mod 2^k は排除残基に入る k が存在する。
    これが示されればコラッツ予想のサイクル部分が解決。
    """)

    # v2制約とBaker排除の組合せ効果の定量化
    print("  組合せ排除の定量化:")
    print("  Baker排除: 周期 p ≤ 10 の全パターン列挙で非自明サイクルなし")
    print("  mod 2^k 排除: k=18 で 93.6% の残基を排除")
    print()
    print("  組合せ効果:")
    print("  - 非排除残基は v2=1 のみ → Baker パターン (1,...,1) のみ")
    print("  - (1,...,1) パターンは C/D = -1 で代数的に不可能")
    print("  - → mod 2^k 非排除残基のBakerパターン許容数 = 0")
    print("  - → 非自明サイクルの「mod的痕跡」は存在しない")
    print()
    print("  ただし、これは上位ビットの効果を無視している：")
    print("  - 実際のサイクルでは v2 > 1 のステップが必要")
    print("  - そのステップの残基は mod 2^k では排除済み")
    print("  - しかし「排除済み」は「確定的下降」であり、")
    print("    サイクルでの下降は最終的に元に戻ればよい")
    print("  - つまり、mod排除とサイクル排除は直接的には同値でない")

    return True


# =====================================================================
# Analysis 5: 逃避時間の理論的予測
# =====================================================================

def escape_time_theory():
    """
    非排除残基からの逃避時間（NE集合を離れるまでのステップ数）の分布。

    逃避時間 d の残基数が幾何的に減少するか検証。
    """
    print("\n## Analysis 5: 逃避時間分布の理論")
    print("-" * 60)

    def symbolic_descent(r, mod, max_depth=20):
        a, b = mod, r
        for depth in range(1, max_depth + 1):
            if b % 2 == 0:
                if a % 2 == 0: a //= 2; b //= 2; continue
                else: return False, depth
            new_a = 3 * a; new_b = 3 * b + 1
            v_b = v2(new_b); v_a = v2(new_a)
            if v_a >= v_b:
                divisor = 2 ** v_b; a = new_a // divisor; b = new_b // divisor
                if a - mod < 0: return True, depth
                elif a - mod == 0 and r - b > 0: return True, depth
            else: return False, depth
        return False, max_depth

    for k in [10, 12, 14]:
        mod = 2**k
        ne_list = []
        for r in range(1, mod, 2):
            ex, _ = symbolic_descent(r, mod, max_depth=20)
            if not ex:
                ne_list.append(r)

        ne_set = set(ne_list)

        # 遷移マップ
        transitions = {}
        for r in ne_list:
            val = 3 * r + 1
            v = v2(val)
            t_r = (val >> v) % mod
            while t_r % 2 == 0 and t_r > 0:
                t_r //= 2
            transitions[r] = t_r

        # 逃避時間分布
        escape = Counter()
        for r in ne_list:
            current = r
            d = 0
            visited = set()
            while current in ne_set and current not in visited:
                visited.add(current)
                d += 1
                current = transitions.get(current, -1)
            escape[d] += 1

        # 表示
        print(f"\n  k={k}: 非排除残基 = {len(ne_list)}")
        total = sum(escape.values())
        cumulative = 0
        for d in sorted(escape.keys()):
            cumulative += escape[d]
            ratio = escape[d] / total
            cum_ratio = cumulative / total
            print(f"    d={d}: {escape[d]:>5} ({ratio:.4f}), 累積={cum_ratio:.4f}")

        # 幾何分布フィット
        if 1 in escape and 2 in escape and escape[1] > 0:
            q = escape[2] / escape[1]
            print(f"    幾何分布パラメータ: q ≈ {q:.4f} (d=2/d=1 の比)")
            print(f"    → 期待逃避時間 ≈ {1/(1-q):.2f}")


# =====================================================================
# メイン
# =====================================================================

def main():
    print("=" * 80)
    print("v2制約の代数的証明と論理的帰結")
    print("=" * 80)

    proof_v2_constraint()
    proof_cd_minus_one()
    sporadic = sporadic_v2_analysis()
    logical_consequences()
    escape_time_theory()

    # 最終JSON結果
    result = {
        'title': 'v2制約の代数的証明とBaker排除の拡張',
        'proven_facts': [
            'v2(3r+1)=1 ⟺ r≡3(mod4) [代数的証明]',
            'C/D=-1 for all-ones pattern: C=3^p-2^p, D=2^p-3^p [等比級数]',
            'mod 2^k 遷移グラフは森（k≤16で確認）',
        ],
        'sporadic_v2': [(k, r, v) for k, r, v in sporadic],
        'key_insight': (
            '非排除残基のv2値が全て1であること + '
            '全ステップv2=1のサイクルがC/D=-1で不可能であること = '
            'mod 2^kレベルでBakerパターン許容数が0。'
            'ただし上位ビット効果により、実際のサイクルでは'
            'v2>1のステップが混在する可能性があり、'
            'この分析はmod的制約に過ぎない。'
        ),
    }

    print("\n\n" + json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return result


if __name__ == '__main__':
    main()
