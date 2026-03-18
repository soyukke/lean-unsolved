#!/usr/bin/env python3
"""
Collatz Exploration 049: 逆Syracuse木の密度と成長率の精密解析

逆Syracuse木を根(=1)から展開し、各深さでのノード数・成長率・被覆率を測定する。
コラッツ予想 ⟺ 逆木が全正整数を含む。
"""

import math
from collections import defaultdict

def inverse_syracuse(n):
    """
    逆Syracuse写像: nの全前像を返す。
    Syracuse写像 T(n) = n/2 (偶数), (3n+1)/2 (奇数) の逆。
    T(m) = n となる m を全て求める:
      - m = 2n (常に前像)
      - 3m+1 が偶数で (3m+1)/2 = n ⟹ m = (2n-1)/3 (整数かつ奇数のとき)
    """
    results = set()
    # 前像1: m = 2n (T(m)=m/2=n for even m)
    results.add(2 * n)
    # 前像2: m = (2n - 1) / 3 (T(m)=(3m+1)/2=n for odd m)
    if (2 * n - 1) % 3 == 0:
        m = (2 * n - 1) // 3
        if m > 0 and m % 2 == 1:  # mは奇数でなければならない
            results.add(m)
    return results


def inverse_collatz(n):
    """
    逆コラッツ写像: C(m) = n となる m を全て求める。
    C(m) = m/2 (偶数), 3m+1 (奇数)
      - m = 2n (常に前像)
      - 3m+1 = n ⟹ m = (n-1)/3 (整数かつ奇数のとき)
    """
    results = set()
    results.add(2 * n)
    if (n - 1) % 3 == 0:
        m = (n - 1) // 3
        if m > 0 and m % 2 == 1:
            results.add(m)
    return results


def build_inverse_tree(root, max_depth, use_syracuse=True):
    """
    逆木をBFSで構築。各深さのノード集合を返す。
    use_syracuse=True: Syracuse写像(奇数ステップ)の逆を使用
    use_syracuse=False: 標準Collatz写像の逆を使用
    """
    inv_func = inverse_syracuse if use_syracuse else inverse_collatz

    all_nodes = {root}
    depth_nodes = {0: {root}}
    new_at_depth = {0: {root}}

    current_frontier = {root}

    for d in range(1, max_depth + 1):
        next_frontier = set()
        for n in current_frontier:
            for pre in inv_func(n):
                if pre not in all_nodes:
                    next_frontier.add(pre)
                    all_nodes.add(pre)

        depth_nodes[d] = next_frontier
        new_at_depth[d] = next_frontier.copy()
        current_frontier = next_frontier

        if not next_frontier:
            break

    return depth_nodes, new_at_depth, all_nodes


def analyze_tree():
    """メイン解析"""
    print("=" * 80)
    print("Collatz Exploration 049: 逆Syracuse木の密度と成長率の精密解析")
    print("=" * 80)

    # ============================================================
    # Part 1: 逆Syracuse木（Syracuse写像ベース）
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 1: 逆Syracuse木 (Syracuse写像 T(n)=n/2 or (3n+1)/2)")
    print("=" * 80)

    MAX_DEPTH = 35
    depth_nodes, new_at_depth, all_nodes_syr = build_inverse_tree(1, MAX_DEPTH, use_syracuse=True)

    print(f"\n{'深さ':>4} | {'新規ノード数':>12} | {'累積ノード数':>12} | {'成長率':>10} | {'最小値':>10} | {'最大値':>12}")
    print("-" * 80)

    cumulative = 0
    prev_new = 0
    growth_rates = []
    cumulative_counts = []
    max_vals = []

    for d in range(MAX_DEPTH + 1):
        nodes = depth_nodes.get(d, set())
        new_count = len(nodes)
        cumulative += new_count

        if nodes:
            min_val = min(nodes)
            max_val = max(nodes)
        else:
            min_val = max_val = 0

        if prev_new > 0 and new_count > 0:
            rate = new_count / prev_new
            growth_rates.append((d, rate))
        else:
            rate = float('inf') if new_count > 0 else 0

        cumulative_counts.append(cumulative)
        max_vals.append(max_val)

        rate_str = f"{rate:.4f}" if rate != float('inf') else "inf"
        print(f"{d:>4} | {new_count:>12,} | {cumulative:>12,} | {rate_str:>10} | {min_val:>10,} | {max_val:>12,}")

        prev_new = new_count

    # 成長率の統計
    if growth_rates:
        rates = [r for _, r in growth_rates]
        avg_rate = sum(rates) / len(rates)
        print(f"\n平均成長率: {avg_rate:.6f}")
        print(f"理論値 4/3 = {4/3:.6f}")
        print(f"後半10ステップの平均: {sum(rates[-10:]) / min(10, len(rates[-10:])):.6f}")

    # ============================================================
    # Part 2: 逆Collatz木（標準Collatz写像ベース）
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 2: 逆Collatz木 (標準Collatz C(n)=n/2 or 3n+1)")
    print("=" * 80)

    MAX_DEPTH_C = 50
    depth_nodes_c, new_at_depth_c, all_nodes_col = build_inverse_tree(1, MAX_DEPTH_C, use_syracuse=False)

    print(f"\n{'深さ':>4} | {'新規ノード数':>12} | {'累積ノード数':>12} | {'成長率':>10} | {'最小値':>10} | {'最大値':>12}")
    print("-" * 80)

    cumulative_c = 0
    prev_new_c = 0
    growth_rates_c = []

    for d in range(MAX_DEPTH_C + 1):
        nodes = depth_nodes_c.get(d, set())
        new_count = len(nodes)
        cumulative_c += new_count

        if nodes:
            min_val = min(nodes)
            max_val = max(nodes)
        else:
            min_val = max_val = 0

        if prev_new_c > 0 and new_count > 0:
            rate = new_count / prev_new_c
            growth_rates_c.append((d, rate))
        else:
            rate = float('inf') if new_count > 0 else 0

        rate_str = f"{rate:.4f}" if rate != float('inf') else "inf"
        print(f"{d:>4} | {new_count:>12,} | {cumulative_c:>12,} | {rate_str:>10} | {min_val:>10,} | {max_val:>12,}")

        prev_new_c = new_count

    if growth_rates_c:
        rates_c = [r for _, r in growth_rates_c]
        avg_rate_c = sum(rates_c) / len(rates_c)
        print(f"\n平均成長率: {avg_rate_c:.6f}")
        print(f"後半10ステップの平均: {sum(rates_c[-10:]) / min(10, len(rates_c[-10:])):.6f}")

    # ============================================================
    # Part 3: 被覆率解析 (Collatz木を使用、より多くのノード)
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 3: 被覆率解析")
    print("=" * 80)

    # Syracuse木の方を使う（奇数のみ対象なのでCollatz木で正整数全体の被覆を見る）
    all_reached = all_nodes_col

    for M in [10**3, 10**4, 10**5, 10**6]:
        count_in_M = sum(1 for x in all_reached if x <= M)
        coverage = count_in_M / M
        print(f"[1, {M:>10,}] 内の被覆率: {count_in_M:>10,} / {M:>10,} = {coverage:.6f} ({coverage*100:.2f}%)")

    # ============================================================
    # Part 4: 未到達整数の分布解析
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 4: 未到達整数の分布解析")
    print("=" * 80)

    # [1, 10^5] 範囲で未到達の整数を調べる
    M_check = 100000
    not_reached = set(range(1, M_check + 1)) - all_reached

    print(f"\n[1, {M_check:,}] 内の未到達整数: {len(not_reached):,} 個")

    if not_reached:
        sorted_unreached = sorted(not_reached)
        print(f"最小の未到達整数: {sorted_unreached[0]}")
        print(f"最大の未到達整数: {sorted_unreached[-1]}")
        print(f"最初の20個: {sorted_unreached[:20]}")

        # mod パターン解析
        print("\n未到達整数の mod パターン:")
        for m in [2, 3, 4, 6, 8, 12, 16, 24]:
            residue_counts = defaultdict(int)
            for x in not_reached:
                residue_counts[x % m] += 1
            total = len(not_reached)
            print(f"  mod {m:>2}: ", end="")
            for r in sorted(residue_counts.keys()):
                pct = residue_counts[r] / total * 100
                print(f"{r}:{pct:.1f}% ", end="")
            print()

        # 2進表現の特徴
        print("\n未到達整数の2進桁数分布:")
        bit_counts = defaultdict(int)
        for x in not_reached:
            bit_counts[x.bit_length()] += 1
        for bits in sorted(bit_counts.keys()):
            total_with_bits = 2**(bits-1) if bits > 1 else 1  # その桁数の整数の総数
            pct_of_unreached = bit_counts[bits] / len(not_reached) * 100
            print(f"  {bits:>2}ビット: {bit_counts[bits]:>6,} 個 ({pct_of_unreached:.1f}%)")

        # 1の密度(ビット中の1の割合)
        print("\n未到達整数のビット中の1の割合分布:")
        one_density_buckets = defaultdict(int)
        for x in not_reached:
            ones = bin(x).count('1')
            density = ones / x.bit_length() if x.bit_length() > 0 else 0
            bucket = round(density, 1)
            one_density_buckets[bucket] += 1
        for d in sorted(one_density_buckets.keys()):
            print(f"  密度 {d:.1f}: {one_density_buckets[d]:>6,} 個")

    # ============================================================
    # Part 5: 理論的成長率 vs 実測の比較
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 5: 理論的成長率 (4/3)^d vs 実測累積ノード数の比較")
    print("=" * 80)

    # Syracuse木で比較
    print("\n[Syracuse木]")
    print(f"{'深さ':>4} | {'(4/3)^d':>14} | {'3*(4/3)^d':>14} | {'実測累積':>12} | {'比率':>10}")
    print("-" * 65)
    cumul = 0
    for d in range(min(MAX_DEPTH + 1, 36)):
        nodes = depth_nodes.get(d, set())
        new_count = len(nodes)
        cumul += new_count
        theoretical = (4/3) ** d
        theoretical_3 = 3 * theoretical  # 定数倍の補正
        ratio = cumul / theoretical if theoretical > 0 else 0
        if d <= 30 or d % 5 == 0:
            print(f"{d:>4} | {theoretical:>14.2f} | {theoretical_3:>14.2f} | {cumul:>12,} | {ratio:>10.4f}")

    # ============================================================
    # Part 6: 各深さでの新規ノードの特徴
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 6: 各深さでの新規ノードの特徴 (Collatz木)")
    print("=" * 80)

    print(f"\n{'深さ':>4} | {'新規数':>8} | {'奇数%':>7} | {'偶数%':>7} | {'平均値':>12} | {'中央値':>12} | {'3で割れる%':>10}")
    print("-" * 80)

    for d in range(min(MAX_DEPTH_C + 1, 51)):
        nodes = depth_nodes_c.get(d, set())
        if not nodes:
            continue
        n_count = len(nodes)
        odd_count = sum(1 for x in nodes if x % 2 == 1)
        even_count = n_count - odd_count
        div3_count = sum(1 for x in nodes if x % 3 == 0)
        sorted_nodes = sorted(nodes)
        mean_val = sum(nodes) / n_count
        median_val = sorted_nodes[n_count // 2]

        odd_pct = odd_count / n_count * 100
        even_pct = even_count / n_count * 100
        div3_pct = div3_count / n_count * 100

        if d <= 20 or d % 5 == 0:
            print(f"{d:>4} | {n_count:>8,} | {odd_pct:>6.1f}% | {even_pct:>6.1f}% | {mean_val:>12,.0f} | {median_val:>12,} | {div3_pct:>9.1f}%")

    # ============================================================
    # Part 7: 逆木のフラクタル的構造
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 7: 深さごとの到達比率の推移")
    print("=" * 80)

    # 累積到達数 vs 深さ d での [1, N(d)] の被覆
    cumul_set = set()
    print(f"\n{'深さ':>4} | {'累積ノード':>12} | {'max値':>12} | {'[1,max]被覆率':>12} | {'[1,1000]被覆':>12} | {'[1,10000]被覆':>12}")
    print("-" * 85)

    for d in range(min(MAX_DEPTH_C + 1, 51)):
        nodes = depth_nodes_c.get(d, set())
        cumul_set.update(nodes)
        cumul_count = len(cumul_set)

        if cumul_set:
            max_val = max(cumul_set)
        else:
            max_val = 0

        coverage_max = cumul_count / max_val if max_val > 0 else 0
        coverage_1k = sum(1 for x in cumul_set if x <= 1000) / 1000
        coverage_10k = sum(1 for x in cumul_set if x <= 10000) / 10000

        if d <= 25 or d % 5 == 0:
            print(f"{d:>4} | {cumul_count:>12,} | {max_val:>12,} | {coverage_max:>11.6f} | {coverage_1k:>11.4f} | {coverage_10k:>11.4f}")

    # ============================================================
    # Part 8: 遅延到達整数の詳細分析
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 8: 遅延到達整数の詳細分析")
    print("=" * 80)

    # 各整数がどの深さで初めて到達されるかを記録
    first_reached = {}
    cumul_set2 = set()
    for d in range(MAX_DEPTH_C + 1):
        nodes = depth_nodes_c.get(d, set())
        for n in nodes:
            if n not in first_reached:
                first_reached[n] = d
        cumul_set2.update(nodes)

    # [1, 10000] 内で到達深さの分布
    M_detail = 10000
    depth_dist = defaultdict(int)
    late_arrivals = []  # 深さ30以上で到達

    for x in range(1, M_detail + 1):
        if x in first_reached:
            d = first_reached[x]
            depth_dist[d] += 1
            if d >= 30:
                late_arrivals.append((x, d))

    print(f"\n[1, {M_detail:,}] 内の整数の初回到達深さ分布:")
    print(f"{'深さ':>4} | {'個数':>8} | {'累積':>8} | {'累積%':>8}")
    print("-" * 40)
    cumul_pct = 0
    for d in sorted(depth_dist.keys()):
        count = depth_dist[d]
        cumul_pct += count
        pct = cumul_pct / M_detail * 100
        print(f"{d:>4} | {count:>8,} | {cumul_pct:>8,} | {pct:>7.2f}%")

    not_reached_detail = M_detail - cumul_pct
    print(f"\n深さ{MAX_DEPTH_C}までに未到達: {not_reached_detail:,} 個 ({not_reached_detail/M_detail*100:.2f}%)")

    if late_arrivals:
        print(f"\n深さ30以上で初到達の整数 (最初の20個):")
        for x, d in sorted(late_arrivals)[:20]:
            print(f"  {x:>6} (深さ {d}), bin={bin(x)}, mod6={x%6}, mod12={x%12}")

    # ============================================================
    # Part 9: 密度の漸近的振る舞い
    # ============================================================
    print("\n" + "=" * 80)
    print("Part 9: 累積被覆密度の推移 (Collatz木)")
    print("=" * 80)

    # 深さごとに各M=[100,1000,10000,100000]での被覆率を追跡
    cumul_set3 = set()
    M_values = [100, 1000, 10000, 100000]

    print(f"\n{'深さ':>4}", end="")
    for M in M_values:
        print(f" | [1,{M:>6}]被覆率", end="")
    print()
    print("-" * (6 + 20 * len(M_values)))

    for d in range(MAX_DEPTH_C + 1):
        nodes = depth_nodes_c.get(d, set())
        cumul_set3.update(nodes)

        if d <= 30 or d % 5 == 0:
            print(f"{d:>4}", end="")
            for M in M_values:
                cov = sum(1 for x in cumul_set3 if x <= M) / M
                print(f" | {cov:>16.6f}", end="")
            print()

    print("\n" + "=" * 80)
    print("解析完了")
    print("=" * 80)


if __name__ == "__main__":
    analyze_tree()
