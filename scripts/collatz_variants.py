#!/usr/bin/env python3
"""
探索 048: 3n+d 変種（5n+1, 3n+3, 3n-1, 7n+1 等）との系統比較

コラッツ写像 T(n) = (3n+1)/2^{v2(3n+1)} の変種を系統的に調査し、
3n+1 の特殊性を定量化する。

変種:
  (A) T_d(n) = (3n+d)/2^{v2(3n+d)} for d = 1, 3, 5, 7, -1
  (B) T_a(n) = (an+1)/2^{v2(an+1)} for a = 3, 5, 7, 9
"""

import math
from collections import Counter, defaultdict


def v2(n):
    """2-adic valuation of n."""
    if n == 0:
        return float('inf')
    n = abs(n)
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def collatz_variant_step(n, a, d):
    """One step of the (an+d) variant for odd n.
    Returns (result, num_divisions) where result is the odd part."""
    val = a * n + d
    if val <= 0:
        return None, 0  # invalid
    k = v2(val)
    return val >> k, k


def run_orbit(n, a, d, max_steps=10000, threshold=10**9):
    """Run the orbit of n under the variant map.

    Returns:
        status: 'reached_1', 'cycle', 'diverged', 'max_steps'
        steps: number of steps taken
        cycle: list of cycle elements if cycle found, else None
        max_val: maximum value encountered
        total_down: total number of /2 divisions
        total_up: total number of (an+d) applications
    """
    visited = {}
    current = n
    step = 0
    max_val = n
    total_down = 0
    total_up = 0

    while step < max_steps:
        if current in visited:
            # Found a cycle
            cycle_start = visited[current]
            # Reconstruct cycle
            cycle = []
            c = current
            while True:
                cycle.append(c)
                if c % 2 == 0:
                    c = c // 2
                    # This shouldn't happen in our odd-only tracking
                    break
                val = a * c + d
                if val <= 0:
                    break
                k = v2(val)
                total_down_tmp = k
                c = val >> k
                if c == current:
                    break
            return 'cycle', step, cycle, max_val, total_down, total_up

        visited[current] = step

        if current == 1 and a == 3 and d == 1:
            return 'reached_1', step, None, max_val, total_down, total_up

        # For general variant: check if we've reached a fixed point or trivial cycle
        if current == 1:
            val = a * 1 + d
            if val <= 0:
                return 'reached_1', step, None, max_val, total_down, total_up
            k = v2(val)
            next_val = val >> k
            if next_val == 1:
                return 'cycle', step, [1], max_val, total_down, total_up

        if current > threshold:
            return 'diverged', step, None, max_val, total_down, total_up

        # Apply the map: odd -> (a*n+d)/2^v2 -> ... keep dividing by 2
        if current % 2 == 0:
            # Shouldn't normally happen, but handle gracefully
            k = v2(current)
            current = current >> k
            total_down += k
            continue

        val = a * current + d
        if val <= 0:
            return 'negative', step, None, max_val, total_down, total_up

        k = v2(val)
        current = val >> k
        total_down += k
        total_up += 1

        if current > max_val:
            max_val = current

    return 'max_steps', step, None, max_val, total_down, total_up


def find_cycles(a, d, max_n=10000, max_steps=5000, threshold=10**9):
    """Find all cycles for the variant (an+d) among starting values 1..max_n."""
    cycles_found = {}  # frozenset -> list
    results = Counter()
    max_stopping_time = 0
    du_ratios = []

    for n in range(1, max_n + 1, 2):  # Only odd numbers
        status, steps, cycle, max_val, total_down, total_up = run_orbit(
            n, a, d, max_steps=max_steps, threshold=threshold
        )
        results[status] += 1

        if steps > max_stopping_time:
            max_stopping_time = steps

        if total_up > 0:
            du_ratios.append(total_down / total_up)

        if status == 'cycle' and cycle is not None:
            key = frozenset(cycle)
            if key not in cycles_found:
                cycles_found[key] = sorted(cycle)

    return results, cycles_found, max_stopping_time, du_ratios


def analyze_variant(a, d, max_n=10000, label=None):
    """Full analysis of a single variant."""
    if label is None:
        label = f"{a}n+{d}" if d >= 0 else f"{a}n{d}"

    print(f"\n{'='*60}")
    print(f"  変種: {label}")
    print(f"  写像: T(n) = ({label}) / 2^{{v2({label})}}")
    print(f"  理論的成長率: log₂({a}) = {math.log2(a):.4f}")
    print(f"  臨界値 d/u = log₂(2) = 1.0 vs log₂({a}) = {math.log2(a):.4f}")
    print(f"  余裕 (margin): 1 - log₂({a}/2) = {1 - math.log2(a/2):.4f}")
    print(f"{'='*60}")

    total_odd = max_n // 2  # approximate count of odd numbers

    results, cycles, max_st, du_ratios = find_cycles(a, d, max_n=max_n)

    total = sum(results.values())

    print(f"\n  結果 (n=1..{max_n}, 奇数のみ, 計 {total} 個):")
    for status, count in results.most_common():
        pct = 100.0 * count / total
        print(f"    {status:15s}: {count:6d} ({pct:5.1f}%)")

    print(f"\n  最大 stopping time: {max_st}")

    if du_ratios:
        avg_du = sum(du_ratios) / len(du_ratios)
        print(f"  平均 d/u 比: {avg_du:.4f}")
        print(f"  log₂({a}) = {math.log2(a):.4f}")
        print(f"  d/u - log₂({a}) = {avg_du - math.log2(a):.4f} (正なら収束傾向)")

    if cycles:
        print(f"\n  発見されたサイクル数: {len(cycles)}")
        for i, (key, cycle) in enumerate(sorted(cycles.items(), key=lambda x: min(x[1]))):
            if len(cycle) <= 20:
                print(f"    サイクル {i+1}: {cycle}")
            else:
                print(f"    サイクル {i+1}: 長さ {len(cycle)}, 最小値 {min(cycle)}, 最大値 {max(cycle)}")
    else:
        print(f"\n  サイクル: なし（全軌道が発散 or max_steps 到達）")

    return {
        'label': label,
        'a': a,
        'd': d,
        'results': results,
        'cycles': cycles,
        'max_stopping_time': max_st,
        'du_ratios': du_ratios,
        'log2_a': math.log2(a),
    }


def specialness_analysis(all_results):
    """3n+1 の特殊性を定量化する分析。"""
    print("\n" + "=" * 70)
    print("  3n+1 の特殊性分析")
    print("=" * 70)

    print("\n  ■ 変種間比較テーブル")
    print(f"  {'変種':12s} {'log₂(a)':>8s} {'到達1%':>8s} {'発散%':>8s} {'サイクル数':>10s} {'平均d/u':>8s} {'余裕':>8s}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*8}")

    for r in all_results:
        total = sum(r['results'].values())
        reach1 = r['results'].get('reached_1', 0) + r['results'].get('cycle', 0)
        diverged = r['results'].get('diverged', 0)
        pct_1 = 100.0 * reach1 / total if total > 0 else 0
        pct_div = 100.0 * diverged / total if total > 0 else 0
        n_cycles = len(r['cycles'])
        avg_du = sum(r['du_ratios']) / len(r['du_ratios']) if r['du_ratios'] else 0
        margin = avg_du - r['log2_a']

        print(f"  {r['label']:12s} {r['log2_a']:8.4f} {pct_1:7.1f}% {pct_div:7.1f}% {n_cycles:10d} {avg_du:8.4f} {margin:+8.4f}")

    print("\n  ■ 3n+1 の特殊性要因:")
    print("    1. 成長率 log₂(3) ≈ 1.585 < 2: 奇数ステップ1回で平均1.585ビット増加")
    print("       だが偶数ステップで平均 ~1.585 ビット以上減少（d/u > log₂(3)）")
    print("    2. d=1 は最小の正奇数オフセット → 3n+1 が 2 の高い冪で割れやすい")
    print("    3. a=3 は 2 < 3 < 4 の唯一の奇数素数 → 2 の冪との比が臨界的")

    # Compute specialness index
    r_3n1 = None
    for r in all_results:
        if r['a'] == 3 and r['d'] == 1:
            r_3n1 = r
            break

    if r_3n1:
        total = sum(r_3n1['results'].values())
        reach1 = r_3n1['results'].get('reached_1', 0) + r_3n1['results'].get('cycle', 0)
        convergence_rate = reach1 / total if total > 0 else 0
        avg_du = sum(r_3n1['du_ratios']) / len(r_3n1['du_ratios']) if r_3n1['du_ratios'] else 0
        margin = avg_du - r_3n1['log2_a']
        n_spurious_cycles = len(r_3n1['cycles']) - 1  # Subtract the {1} cycle

        # Compare with other variants
        other_convergence = []
        for r in all_results:
            if r['a'] == 3 and r['d'] == 1:
                continue
            total_o = sum(r['results'].values())
            reach1_o = r['results'].get('reached_1', 0) + r['results'].get('cycle', 0)
            if total_o > 0:
                other_convergence.append(reach1_o / total_o)

        print(f"\n  ■ 特殊性指標:")
        print(f"    3n+1 収束率: {convergence_rate:.4f}")
        print(f"    他の変種の平均収束率: {sum(other_convergence)/len(other_convergence):.4f}" if other_convergence else "    他の変種: データなし")
        print(f"    3n+1 d/u 余裕: {margin:+.4f}")
        print(f"    3n+1 非自明サイクル数: {max(0, n_spurious_cycles)}")


def detailed_cycle_analysis(a, d, max_n=1000):
    """Detailed analysis of cycles: compute the exact contraction ratio."""
    print(f"\n  ■ {a}n+{d} のサイクル縮約率分析")

    # Find cycles with more detail
    cycles = {}
    for start in range(1, max_n + 1, 2):
        visited = {}
        current = start
        step = 0
        path = []

        while step < 5000 and current < 10**9:
            if current in visited:
                # Extract cycle
                idx = visited[current]
                cycle = path[idx:]
                key = frozenset(cycle)
                if key not in cycles:
                    # Compute contraction ratio for this cycle
                    ups = 0
                    downs = 0
                    c = current
                    for _ in range(len(cycle)):
                        val = a * c + d
                        k = v2(val)
                        downs += k
                        ups += 1
                        c = val >> k
                    ratio = (a ** ups) / (2 ** downs)
                    cycles[key] = {
                        'elements': sorted(cycle),
                        'length': len(cycle),
                        'ups': ups,
                        'downs': downs,
                        'ratio': ratio,
                        'min': min(cycle),
                        'max': max(cycle),
                    }
                break

            visited[current] = step
            path.append(current)

            if current % 2 == 0:
                k = v2(current)
                current = current >> k
            else:
                val = a * current + d
                if val <= 0:
                    break
                k = v2(val)
                current = val >> k
            step += 1

    if cycles:
        print(f"    発見サイクル: {len(cycles)} 個")
        for i, (key, info) in enumerate(sorted(cycles.items(), key=lambda x: x[1]['min'])):
            print(f"\n    サイクル {i+1}:")
            print(f"      長さ: {info['length']}, 最小: {info['min']}, 最大: {info['max']}")
            print(f"      ups(奇数ステップ): {info['ups']}, downs(2除算): {info['downs']}")
            print(f"      縮約率 {a}^{info['ups']}/2^{info['downs']} = {info['ratio']:.6f}")
            if info['length'] <= 15:
                print(f"      要素: {info['elements']}")
    else:
        print(f"    サイクルなし")

    return cycles


def main():
    print("=" * 70)
    print("  探索 048: 3n+d 変種との系統比較")
    print("  コラッツ写像の特殊性を変種比較により定量化")
    print("=" * 70)

    all_results = []

    # ===== Part A: 3n+d variants (d = 1, 3, 5, 7, -1) =====
    print("\n\n" + "#" * 70)
    print("  Part A: 3n+d 変種 (d = 1, 3, 5, 7, -1)")
    print("#" * 70)

    for d in [1, -1, 3, 5, 7]:
        label = f"3n+{d}" if d >= 0 else f"3n{d}"
        r = analyze_variant(3, d, max_n=10000, label=label)
        all_results.append(r)
        detailed_cycle_analysis(3, d, max_n=2000)

    # ===== Part B: an+1 variants (a = 3, 5, 7, 9) =====
    print("\n\n" + "#" * 70)
    print("  Part B: an+1 変種 (a = 3, 5, 7, 9)")
    print("#" * 70)

    for a in [5, 7, 9]:
        label = f"{a}n+1"
        r = analyze_variant(a, 1, max_n=10000, label=label)
        all_results.append(r)
        detailed_cycle_analysis(a, 1, max_n=2000)

    # ===== Part C: Specialness analysis =====
    print("\n\n" + "#" * 70)
    print("  Part C: 3n+1 の特殊性分析")
    print("#" * 70)

    specialness_analysis(all_results)

    # ===== Part D: Why 3n+1 is special - theoretical argument =====
    print("\n\n" + "#" * 70)
    print("  Part D: 理論的考察")
    print("#" * 70)

    print("""
  ■ なぜ 3n+1 だけが単一サイクル {4,2,1} に見えるのか

  1. 成長率の条件: a/2 < 2 ⟹ a < 4
     - a=1: 自明（n+1 は常に偶数で即座に収束）
     - a=3: 唯一の非自明な奇数 → 3n+1 が唯一の候補
     - a=5,7,9,...: a/2 > 2 なので一般的に発散

  2. d=1 の最適性:
     - d=1: 3n+1 は常に偶数（奇数×奇数+奇数=偶数）→ 即座に /2 可能
     - d=3: 3(n+1) → n+1 が偶数なら 3×偶数 → v2 が n+1 の v2 に依存
     - d=-1: 3n-1 も常に偶数だが、負方向へのバイアスがサイクル構造を変える

  3. 余裕 (margin) の概念:
     - 奇数 n に対し平均 d/u ≈ log₂(3) + ε の「余裕」がある
     - この余裕が正であることが収束の鍵
     - 3n+1 では d/u ≈ 1.6~1.7 > log₂(3) ≈ 1.585

  4. エルゴード的議論:
     - 3n+1 のとき、v2(3n+1) の分布は幾何分布に近い
     - E[v2] = 2 (正確には v2 ≥ 1 が保証)
     - E[v2] = 2 > log₂(3) ≈ 1.585 なので「平均的に」収束
""")

    # ===== Part E: v2 distribution comparison =====
    print("\n" + "#" * 70)
    print("  Part E: v2 分布の変種間比較")
    print("#" * 70)

    for a, d, label in [(3, 1, "3n+1"), (3, -1, "3n-1"), (3, 5, "3n+5"), (5, 1, "5n+1"), (7, 1, "7n+1")]:
        v2_counts = Counter()
        total = 0
        for n in range(1, 20001, 2):
            val = a * n + d
            if val > 0:
                v2_counts[v2(val)] += 1
                total += 1

        print(f"\n  {label}: v2 分布 (n=1..20000, 奇数)")
        ev2 = 0
        for k in sorted(v2_counts.keys()):
            if k <= 8:
                pct = 100.0 * v2_counts[k] / total
                ev2 += k * v2_counts[k] / total
                print(f"    v2={k}: {v2_counts[k]:5d} ({pct:5.1f}%)")
        print(f"    E[v2] ≈ {ev2:.4f}, log₂({a}) = {math.log2(a):.4f}, 差 = {ev2 - math.log2(a):+.4f}")

    print("\n" + "=" * 70)
    print("  完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
