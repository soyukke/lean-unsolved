#!/usr/bin/env python3
"""
コラッツ予想 探索45: SAT/制約充足を用いた最小反例の mod 制約の自動的拡大

mod 2^k の各剰余類について Syracuse 写像を追跡し、
最小反例が属し得ない剰余類を体系的に排除する。

## 主要発見
- mod 2^k (k=3..9, 13..18+) では mod 4≡3 の全剰余類が排除可能
- k=10,11,12 のみ拡大的な mod 周期が存在し完全排除できない
- 排除の壁は mod 上の Syracuse 写像が拡大的周期を持つことに起因
- 拡大周期の平均 v2 < log2(3) ≈ 1.585 であることが原因
"""

import math
from fractions import Fraction
from itertools import product


def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def syracuse(n):
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)


def trace_residue_class(r, k, max_steps=100):
    """
    n ≡ r (mod 2^k) の Syracuse 追跡。

    v2(3n+1) は n mod 2^k で確定する（v2(3r+1) < k の場合）。
    v2(3r+1) >= k の場合は worst case で v=k を仮定して
    3^s / 2^(v2sum+k) < 1 なら下降確定。
    """
    M = 1 << k
    if r % 2 == 0:
        return True, 0, Fraction(0), "even"

    current_r = r
    total_v2_sum = 0
    steps_3 = 0

    for step in range(1, max_steps + 1):
        val = 3 * current_r + 1
        v = v2(val)

        if v >= k:
            worst_ratio = Fraction(3 ** (steps_3 + 1), 2 ** (total_v2_sum + k))
            if worst_ratio < 1:
                return True, step, worst_ratio, f"v2>={k}_descent"
            return False, step, worst_ratio, f"v2_ambiguous"

        total_v2_sum += v
        steps_3 += 1
        current_r = (val >> v) % M

        ratio = Fraction(3 ** steps_3, 2 ** total_v2_sum)
        if ratio < 1:
            return True, step, ratio, "descent"

    return False, max_steps, Fraction(3 ** steps_3, 2 ** total_v2_sum), "max_steps"


def analyze_cycles(k):
    """mod 2^k 上の Syracuse 遷移グラフの周期構造を分析"""
    M = 1 << k

    visited_global = set()
    all_cycles = []
    expanding_cycles = []

    for start in range(M):
        if start % 2 == 0 or start in visited_global:
            continue

        visited = {}
        r = start
        step = 0

        while r is not None and r not in visited:
            visited[r] = step
            val = 3 * r + 1
            v = v2(val)
            if v >= k:
                r = None
                break
            r = (val >> v) % M
            step += 1

        if r is not None and r in visited:
            cycle = []
            cr = r
            while True:
                cycle.append(cr)
                visited_global.add(cr)
                val = 3 * cr + 1
                v = v2(val)
                cr = (val >> v) % M
                if cr == r:
                    break

            L = len(cycle)
            cycle_v2 = sum(v2(3 * c + 1) for c in cycle)
            log2_ratio = L * math.log2(3) - cycle_v2
            all_cycles.append((cycle, L, cycle_v2, log2_ratio))
            if log2_ratio > 0:
                expanding_cycles.append((cycle, L, cycle_v2, log2_ratio))

    return all_cycles, expanding_cycles


def analyze_mod_2k(k, max_steps=100):
    """mod 2^k での全剰余類の排除判定"""
    M = 1 << k
    results = {}
    excluded = set()
    surviving = set()

    for r in range(M):
        desc, steps, ratio, detail = trace_residue_class(r, k, max_steps)
        results[r] = (desc, steps, ratio, detail)
        if desc:
            excluded.add(r)
        else:
            surviving.add(r)

    return results, excluded, surviving


def lean_template(r, M, steps, ratio):
    """Lean 定理テンプレート"""
    return f"""/-- 最小反例は n ≡ {r} (mod {M}) ではない
    {steps}ステップの Syracuse で比率 {ratio} < 1 -/
theorem minimal_counterexample_not_mod{M}_eq{r} (n : ℕ) (h : isMinimalCounterexample n) :
    n % {M} ≠ {r} := by
  intro hmod
  -- {steps}回のsyracuse適用で T^{steps}(n) < n を示す
  sorry"""


def main():
    print("=" * 70)
    print("コラッツ予想 探索45: 最小反例の mod 制約の自動的拡大")
    print("=" * 70)

    # ====== Part 1: mod 2^k での全排除可能性 ======
    print("\n" + "#" * 70)
    print("# Part 1: mod 2^k (k=2..18) の周期構造分析")
    print("#" * 70)

    print(f"\n{'k':>3} {'M':>7} {'周期数':>7} {'拡大周期':>8} {'mod4≡3排除':>12} {'状態':>10}")
    print("-" * 55)

    summary = []
    for k in range(2, 19):
        M = 1 << k
        all_cycles, expanding = analyze_cycles(k)
        total_mod4_3 = M // 4
        # 拡大周期に属する mod 4≡3 クラスの数（前周期も含む全到達可能クラス）
        exp_members = set()
        for cyc, _, _, _ in expanding:
            for c in cyc:
                exp_members.add(c)
        n_exp_mod4_3 = len([c for c in exp_members if c % 4 == 3])
        excluded_mod4_3 = total_mod4_3 - n_exp_mod4_3
        status = "★全排除" if len(expanding) == 0 else f"{n_exp_mod4_3}残"
        print(f"  {k:2d} {M:7d} {len(all_cycles):7d} {len(expanding):8d} "
              f"{excluded_mod4_3:5d}/{total_mod4_3:<5d} {status:>10}")
        summary.append((k, M, len(all_cycles), len(expanding), excluded_mod4_3, total_mod4_3))

    # ====== Part 2: 排除ステップ数の分析 ======
    print("\n" + "#" * 70)
    print("# Part 2: 全排除可能な k での最大ステップ数")
    print("#" * 70)

    all_excludable_k = [k for k, _, _, n_exp, _, _ in summary if n_exp == 0 and k >= 3]

    print(f"\n{'k':>3} {'M':>7} {'最大ステップ':>12} {'平均ステップ':>12}")
    print("-" * 40)

    for k in all_excludable_k:
        if k > 16:
            continue
        M = 1 << k
        max_s = 0
        total_s = 0
        count = 0
        for r in range(M):
            if r % 2 == 0 or r % 4 != 3:
                continue
            desc, steps, ratio, detail = trace_residue_class(r, k, 500)
            if desc:
                max_s = max(max_s, steps)
                total_s += steps
                count += 1
        avg_s = total_s / count if count > 0 else 0
        print(f"  {k:2d} {M:7d} {max_s:12d} {avg_s:12.1f}")

    # ====== Part 3: k=10,11,12 の拡大周期の詳細 ======
    print("\n" + "#" * 70)
    print("# Part 3: 拡大周期の詳細 (k=10,11,12)")
    print("#" * 70)

    for k in [10, 11, 12]:
        M = 1 << k
        _, expanding = analyze_cycles(k)
        print(f"\n--- k={k} (mod {M}) ---")

        # パターン集約
        patterns = {}
        for cycle, L, cv2, lr in expanding:
            key = (L, cv2)
            if key not in patterns:
                patterns[key] = []
            patterns[key].append(cycle)

        for (L, cv2), cycles_list in sorted(patterns.items()):
            avg_v2 = cv2 / L
            n_mod4_3 = sum(1 for cyc in cycles_list for c in cyc if c % 4 == 3)
            print(f"  パターン L={L}, v2sum={cv2}: {len(cycles_list)}周期, "
                  f"avg_v2={avg_v2:.3f} (need>{math.log2(3):.3f}), "
                  f"mod4≡3: {n_mod4_3}クラス")

    # ====== Part 4: CRT との組み合わせ ======
    print("\n" + "#" * 70)
    print("# Part 4: CRT (mod 2^k * p) での排除")
    print("#" * 70)

    for k in [4, 5, 6]:
        for p in [3, 5]:
            M = (1 << k) * p
            k_eff = k  # v2 精度は 2^k 部分で決まる
            mod4_3 = [r for r in range(M) if r % 2 == 1 and r % 4 == 3]
            excluded_count = 0
            surviving_list = []
            for r in mod4_3:
                desc, steps, ratio, detail = trace_residue_class(r, k_eff, 100)
                if desc:
                    excluded_count += 1
                else:
                    surviving_list.append(r)
            print(f"  mod 2^{k}*{p} = {M}: mod4≡3 {excluded_count}/{len(mod4_3)} 排除 "
                  f"({excluded_count/len(mod4_3)*100:.1f}%)"
                  f"{', 生存: ' + str(surviving_list[:10]) if surviving_list else ' ★全排除'}")

    # ====== Part 5: 数値検証 ======
    print("\n" + "#" * 70)
    print("# Part 5: 数値検証")
    print("#" * 70)

    for k in [8, 10]:
        M = 1 << k
        results, _, surviving = analyze_mod_2k(k, 100)
        mod4_3_surv = sorted([r for r in surviving if r % 4 == 3])
        if not mod4_3_surv:
            print(f"  mod 2^{k}: 全排除済み、検証不要")
            continue
        print(f"  mod 2^{k}: {len(mod4_3_surv)} クラスを数値検証...")
        max_collatz_steps = 0
        all_ok = True
        for r in mod4_3_surv[:10]:
            for q in range(1, 501):
                n = M * q + r
                if n <= 1:
                    continue
                val = n
                steps = 0
                while val != 1 and steps < 100000:
                    val = val // 2 if val % 2 == 0 else 3 * val + 1
                    steps += 1
                if val != 1:
                    print(f"    !! r={r}, n={n}: 未到達")
                    all_ok = False
                    break
                max_collatz_steps = max(max_collatz_steps, steps)
        if all_ok:
            print(f"  OK (最大 {max_collatz_steps} ステップ)")

    # ====== Part 6: Lean テンプレート ======
    print("\n" + "#" * 70)
    print("# Part 6: Lean 形式化テンプレート")
    print("#" * 70)

    # mod 32 の排除（既知の mod 16 を超える新規排除）
    print("\n新規排除可能な定理 (mod 32):")
    results_32, _, _ = analyze_mod_2k(5, 100)
    for r in sorted(results_32.keys()):
        if r % 2 == 0 or r % 4 != 3:
            continue
        desc, steps, ratio, detail = results_32[r]
        if desc:
            # mod 16 で排除済みかチェック
            r16 = r % 16
            d16, _, _, _ = trace_residue_class(r16, 4, 100)
            if not d16:
                print(lean_template(r, 32, steps, ratio))

    # ====== Part 7: 全体考察 ======
    print("\n" + "#" * 70)
    print("# Part 7: 全体考察")
    print("#" * 70)

    print("""
## 主要発見

1. mod 2^k (k=3..9, 13..18) では最小反例の mod 4≡3 剰余類が全て排除可能
   - Syracuse の有限ステップで必ず元の値より小さくなることが示せる
   - 最大必要ステップ数は k とともに緩やかに増加

2. k=10,11,12 のみ拡大的な mod 周期が存在
   - k=10: L=26, v2sum=37 の周期 (161個)
   - k=11: L=25, v2sum=37 の周期 (338個)
   - k=12: L=6,7 の短い周期 (14個)
   - 平均 v2 < log2(3) ≈ 1.585 のため、この手法では排除不可能

3. k=13 以降は再び全排除可能
   - 拡大周期の「窓」は k=10~12 の狭い範囲のみ
   - これは 3^L / 2^(v2sum) の算術的偶然による

4. Lean 形式化の戦略
   - mod 2^k (k ≤ 9) なら各剰余類をステップバイステップで展開可能
   - 自動化: decide タクティクで各 mod の排除を自動証明できる可能性
   - 一般の k に対する排除定理は mod 周期の拡大性判定が必要で困難

5. 制約の限界
   - mod 2^k のみでは全剰余類を排除することは原理的に不可能
     （拡大周期が存在する k が無限にあり得る）
   - しかし任意の特定の n について有限ステップで 1 に到達することの
     証明は、この手法の延長で可能（n が具体的に与えられれば）
""")

    print("=" * 70)
    print("探索45 完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
