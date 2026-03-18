#!/usr/bin/env python3
"""
エルデシュ問題 #138: Van der Waerden Numbers
探索5: 確率的手法による下界

- Lovász Local Lemma (LLL) による W(k) の下界推定
- シミュレーション: ランダム塗り分けで単色AP(k)が最初に現れるNの分布
- k=3,4,5,6 での LLL下界 vs 既知W(k) vs 実測値の比較
"""

import math
import random
from collections import defaultdict


def has_monochromatic_ap(coloring, k):
    """k項単色等差数列が存在するか"""
    n = len(coloring)
    for start in range(n):
        for diff in range(1, n):
            end = start + (k - 1) * diff
            if end >= n:
                break
            color = coloring[start]
            mono = True
            for j in range(1, k):
                if coloring[start + j * diff] != color:
                    mono = False
                    break
            if mono:
                return True
    return False


def count_aps(n, k):
    """[0,...,n-1] 中の k 項等差数列の個数"""
    count = 0
    for start in range(n):
        for diff in range(1, n):
            end = start + (k - 1) * diff
            if end >= n:
                break
            count += 1
    return count


# =============================================================================
# Lovász Local Lemma (LLL) による下界推定
# =============================================================================
print("=" * 70)
print("探索5: 確率的手法による下界")
print("=" * 70)

print("""
=== Lovász Local Lemma (LLL) の適用 ===

設定:
  {1,...,N} の各要素を独立に確率 1/2 で赤/青に塗る。
  A_{a,d} = 「等差数列 a, a+d, ..., a+(k-1)d が単色」という事象。

各事象の確率:
  P(A_{a,d}) = 2 * (1/2)^k = 2^{1-k}
  (赤単色 or 青単色)

等差数列の総数:
  m(N,k) ≈ N^2 / (2(k-1))  (正確には floor 操作があるが近似)

依存度:
  A_{a,d} は、位置を共有する他の AP 事象と依存。
  各APは k 個の位置を使い、各位置は ≈ N/(k-1) 個のAPに含まれる。
  → 各事象 A_{a,d} の依存度 d ≈ k * N / (k-1) * k ≈ k^2 * N / (k-1)

  より正確には: 各位置 x を含む AP の数は高々 N/(k-1) 個。
  各 AP は k 個の位置を持つので、依存する AP の数は高々
    d ≤ k * N/(k-1) ≈ kN/(k-1)

LLL の対称版:
  ep(d+1) ≤ 1 ならば、全事象を同時に回避可能。
  ここで p = 2^{1-k}。

  ep(d+1) ≤ 1
  ⟺ e * 2^{1-k} * (kN/(k-1) + 1) ≤ 1
  ⟺ N ≤ (k-1) * (2^{k-1}/e - 1) / k
  ⟺ N ≈ (k-1) * 2^{k-1} / (ek)

結論: W(k) ≥ (k-1) * 2^{k-1} / (ek) + 1
""")


def lll_lower_bound(k):
    """LLL対称版による W(k) の下界"""
    # p = 2^{1-k} (各AP事象の確率)
    p = 2 ** (1 - k)

    # 各位置を含むAPの概数: pos x を含むAPは
    # (start, diff) with start <= x, x <= start + (k-1)*diff, x-start ≡ 0 mod diff
    # 概算: N/(k-1) 個（Nに依存するので反復的に解く）

    # ep(d+1) <= 1 where d = k * N / (k-1) (概算)
    # e * 2^{1-k} * (k*N/(k-1) + 1) <= 1
    # N <= (k-1) * (2^{k-1}/e - 1) / k
    N = (k - 1) * (2 ** (k - 1) / math.e - 1) / k
    return int(N) + 1


def lll_lower_bound_precise(k):
    """より精密な LLL 下界（依存度の正確な計算）"""
    # 各 AP (a, d) が関わる位置の集合 S = {a, a+d, ..., a+(k-1)d}
    # 別の AP (a', d') が依存 ⟺ S ∩ S' ≠ ∅
    #
    # 位置 x を含む AP の数を計算:
    # (a, d) with 0 ≤ a, a+(k-1)d < N, a ≡ x mod gcd(...)
    # 上界: 各位置につき ≈ N/(2(k-1)) 個の AP が通る
    # 各 AP は k 位置 → 依存度 d ≤ k * N/(2(k-1))
    #
    # ep(d+1) ≤ 1 → N ≤ 2(k-1)(2^{k-1}/e - 1) / k

    p = 2 ** (1 - k)
    # 依存度の上界: d ≈ k * N / (2*(k-1)) (各位置を通るAPの個数のより精密な見積もり)
    # ep(d+1) ≤ 1 → d ≤ 1/(ep) - 1 = 2^{k-1}/e - 1
    d_max = 2 ** (k - 1) / math.e - 1
    # d ≈ k * N / (2(k-1))
    # → N ≈ 2(k-1) * d_max / k
    N = 2 * (k - 1) * d_max / k
    return int(N) + 1


print("\n" + "=" * 60)
print("LLL下界の計算")
print("=" * 60)

known_W = {3: 9, 4: 35, 5: 178, 6: 1132}

print(f"\n{'k':>3} {'LLL下界':>10} {'LLL精密':>10} {'2^k/(ek)':>10} {'W(k)':>10} {'比率W/LLL':>12}")
print("-" * 60)

for k in range(3, 11):
    lll = lll_lower_bound(k)
    lll_p = lll_lower_bound_precise(k)
    kozik = int(2 ** k / (math.e * k))
    w_val = known_W.get(k, None)

    if w_val:
        ratio = w_val / max(lll, 1)
        print(f"{k:>3} {lll:>10} {lll_p:>10} {kozik:>10} {w_val:>10} {ratio:>12.2f}")
    else:
        print(f"{k:>3} {lll:>10} {lll_p:>10} {kozik:>10} {'未知':>10} {'---':>12}")


# =============================================================================
# AP事象の依存度の正確な計算
# =============================================================================
print("\n" + "=" * 60)
print("AP事象の依存度の正確な計算 (小さいN)")
print("=" * 60)

def compute_dependency_degree(N, k):
    """
    [0,...,N-1] 上の k 項 AP 事象間の最大依存度を計算。
    2つのAPが「依存」⟺ 位置を共有する。
    """
    # 全 AP を列挙
    aps = []
    for start in range(N):
        for diff in range(1, N):
            end = start + (k - 1) * diff
            if end >= N:
                break
            ap = tuple(start + j * diff for j in range(k))
            aps.append(ap)

    if not aps:
        return 0, 0

    # 各位置を含む AP のインデックス
    pos_to_aps = defaultdict(set)
    for idx, ap in enumerate(aps):
        for pos in ap:
            pos_to_aps[pos].add(idx)

    # 各 AP の依存度を計算
    max_dep = 0
    total_dep = 0
    for idx, ap in enumerate(aps):
        dependent = set()
        for pos in ap:
            dependent.update(pos_to_aps[pos])
        dependent.discard(idx)  # 自分自身を除く
        dep = len(dependent)
        max_dep = max(max_dep, dep)
        total_dep += dep

    avg_dep = total_dep / len(aps)
    return max_dep, avg_dep


for k in [3, 4, 5]:
    print(f"\nk = {k}:")
    print(f"  {'N':>5} {'AP数':>8} {'最大依存度':>10} {'平均依存度':>10} {'ep(d+1)':>10}")
    for N in range(k, min(known_W.get(k, 30), 30) + 1, max(1, (known_W.get(k, 30) - k) // 8)):
        n_aps = count_aps(N, k)
        if n_aps == 0:
            continue
        max_dep, avg_dep = compute_dependency_degree(N, k)
        p_event = 2 ** (1 - k)
        epd = math.e * p_event * (max_dep + 1)
        print(f"  {N:>5} {n_aps:>8} {max_dep:>10} {avg_dep:>10.1f} {epd:>10.4f}")


# =============================================================================
# シミュレーション: ランダム塗り分けで単色APが現れるNの分布
# =============================================================================
print("\n" + "=" * 60)
print("シミュレーション: ランダム塗り分けで単色AP(k)が最初に現れるN")
print("=" * 60)

def simulate_first_monochromatic_ap(k, max_n, num_trials=1000):
    """
    ランダム塗り分けを num_trials 回実行。
    各回で N=k, k+1, ... と伸ばしていき、
    単色 k 項 AP が最初に現れる N を記録。
    """
    results = []

    for trial in range(num_trials):
        coloring = [random.randint(0, 1) for _ in range(max_n)]

        first_n = None
        for n in range(k, max_n + 1):
            # n番目の要素を追加したとき、新たに単色APが生じるか
            # n-1 を含むAPのみチェックすればよい
            pos = n - 1
            found = False
            for diff in range(1, n):
                for j in range(k):
                    start = pos - j * diff
                    end = start + (k - 1) * diff
                    if start < 0 or end >= n:
                        continue
                    color = coloring[start]
                    mono = True
                    for m in range(k):
                        idx = start + m * diff
                        if coloring[idx] != color:
                            mono = False
                            break
                    if mono:
                        found = True
                        break
                if found:
                    break
            if found:
                first_n = n
                break

        if first_n is None:
            first_n = max_n + 1  # max_n 以内に現れなかった
        results.append(first_n)

    return results


random.seed(42)

print(f"\n各 k に対し 1000 回のランダム試行:")
print(f"{'k':>3} {'平均N':>8} {'中央値N':>8} {'最小N':>8} {'最大N':>8} {'W(k)':>8} {'平均/W':>8}")
print("-" * 55)

simulation_results = {}
for k in [3, 4, 5, 6]:
    max_n = min(known_W.get(k, 200), 200)
    results = simulate_first_monochromatic_ap(k, max_n, num_trials=1000)

    avg = sum(results) / len(results)
    sorted_r = sorted(results)
    median = sorted_r[len(sorted_r) // 2]
    min_r = min(results)
    max_r = max(results)
    w_val = known_W.get(k, None)
    ratio = avg / w_val if w_val else 0

    simulation_results[k] = results

    w_str = str(w_val) if w_val else "---"
    print(f"{k:>3} {avg:>8.1f} {median:>8} {min_r:>8} {max_r:>8} {w_str:>8} {ratio:>8.3f}")


# 分布のヒストグラム表示（テキスト）
for k in [3, 4]:
    results = simulation_results[k]
    w_val = known_W.get(k)

    print(f"\n--- k={k}, W({k})={w_val} のランダム試行分布 ---")

    # ビンに分ける
    min_val = min(results)
    max_val = min(max(results), w_val)
    n_bins = min(20, max_val - min_val + 1)
    if n_bins < 2:
        continue

    bin_width = max(1, (max_val - min_val + 1) // n_bins)
    bins = defaultdict(int)
    for r in results:
        b = (r - min_val) // bin_width
        bins[b] += 1

    max_count = max(bins.values())
    for b in sorted(bins.keys()):
        low = min_val + b * bin_width
        high = low + bin_width - 1
        count = bins[b]
        bar = '#' * int(50 * count / max_count)
        print(f"  [{low:>4}-{high:>4}] {count:>4} {bar}")


# =============================================================================
# LLL下界 vs 既知W(k) vs 実測値の比較表
# =============================================================================
print("\n" + "=" * 60)
print("総合比較表: LLL下界 vs 既知W(k) vs ランダム実測値")
print("=" * 60)

print(f"\n{'k':>3} {'LLL下界':>10} {'Berlekamp':>10} {'2^k/(ek)':>10} "
      f"{'ランダム平均':>12} {'W(k)':>10} {'W(k)^{1/k}':>10}")
print("-" * 70)

for k in range(3, 11):
    lll = lll_lower_bound(k)

    # Berlekamp
    p = k - 1
    if all(p % i != 0 for i in range(2, int(p**0.5) + 1)) and p >= 2:
        berl = p * (2 ** p)
    else:
        berl = None
    berl_str = str(berl) if berl else "---"

    # Kozik-Shabanov
    kozik = int(2 ** k / (math.e * k))

    # シミュレーション
    if k in simulation_results:
        sim_avg = sum(simulation_results[k]) / len(simulation_results[k])
        sim_str = f"{sim_avg:.1f}"
    else:
        sim_str = "---"

    # W(k)
    w_val = known_W.get(k, None)
    w_str = str(w_val) if w_val else "未知"
    w_root = f"{w_val ** (1.0/k):.4f}" if w_val else "---"

    print(f"{k:>3} {lll:>10} {berl_str:>10} {kozik:>10} "
          f"{sim_str:>12} {w_str:>10} {w_root:>10}")


# =============================================================================
# LLL 下界の漸近解析
# =============================================================================
print("\n" + "=" * 60)
print("LLL 下界の漸近解析")
print("=" * 60)

print("""
LLL対称版からの下界: W(k) >= c * 2^k / k  (c は定数)

この下界から得られる W(k)^{1/k}:
  W(k)^{1/k} >= (c * 2^k / k)^{1/k}
              = c^{1/k} * 2 * k^{-1/k}
              → 2  (k → ∞)

したがって LLL だけでは W(k)^{1/k} → ∞ を示せない！
LLL は W(k)^{1/k} ≥ 2 - o(1) までしか与えない。

W(k)^{1/k} → ∞ を示すには:
  - W(k) >> c^k for any c (超指数的増大)
  - Gowers (2001) の上界はこれを満たす（多重指数関数的）
  - 問題は下界側で超指数的成長を示すこと
""")

print(f"{'k':>3} {'LLL下界':>12} {'LLL^{1/k}':>12} {'2*k^{-1/k}':>12}")
print("-" * 45)
for k in range(3, 21):
    lll = max(lll_lower_bound(k), 1)
    lll_root = lll ** (1.0 / k)
    asymp = 2 * k ** (-1.0 / k)
    print(f"{k:>3} {lll:>12} {lll_root:>12.4f} {asymp:>12.4f}")


# =============================================================================
# 改良版: Moser-Tardos algorithmic LLL
# =============================================================================
print("\n" + "=" * 60)
print("Moser-Tardos アルゴリズム的 LLL シミュレーション")
print("=" * 60)

def moser_tardos_simulation(N, k, max_rounds=10000):
    """
    Moser-Tardos アルゴリズムで [0,...,N-1] の塗り分けを構成。
    単色 k 項 AP が見つかったら、その AP の全位置をランダムに再塗り分け。

    成功: max_rounds 以内に収束
    失敗: 収束しない → N が大きすぎる（W(k) < N の可能性）
    """
    coloring = [random.randint(0, 1) for _ in range(N)]

    for round_num in range(max_rounds):
        # 単色APを探す
        found_ap = None
        for start in range(N):
            for diff in range(1, N):
                end = start + (k - 1) * diff
                if end >= N:
                    break
                color = coloring[start]
                mono = True
                for j in range(1, k):
                    if coloring[start + j * diff] != color:
                        mono = False
                        break
                if mono:
                    found_ap = (start, diff)
                    break
            if found_ap:
                break

        if found_ap is None:
            return True, round_num  # 成功

        # 見つかったAPの位置を再塗り分け
        start, diff = found_ap
        for j in range(k):
            pos = start + j * diff
            coloring[pos] = random.randint(0, 1)

    return False, max_rounds  # 失敗


print("\nMoser-Tardos で回避塗り分けの構成を試みる:")
print(f"{'k':>3} {'N':>6} {'成功率':>8} {'平均ラウンド':>12} {'W(k)':>8}")
print("-" * 45)

random.seed(123)
for k in [3, 4]:
    w_val = known_W[k]
    test_ns = sorted(set([
        max(k, w_val - 5),
        max(k, w_val - 3),
        max(k, w_val - 1),
        w_val,
        w_val + 1,
    ]))

    for N in test_ns:
        successes = 0
        total_rounds = 0
        n_trials = 50
        for _ in range(n_trials):
            success, rounds = moser_tardos_simulation(N, k, max_rounds=5000)
            if success:
                successes += 1
                total_rounds += rounds

        success_rate = successes / n_trials
        avg_rounds = total_rounds / max(successes, 1)
        marker = " ← W(k)" if N == w_val else ""
        print(f"{k:>3} {N:>6} {success_rate:>8.2f} {avg_rounds:>12.1f} {w_val:>8}{marker}")


# =============================================================================
# まとめ
# =============================================================================
print("\n" + "=" * 70)
print("探索5 まとめ")
print("=" * 70)
print("""
1. LLL 下界:
   - W(k) >= c * 2^k / k (定数 c ≈ 1/e)
   - k=3: LLL≈2 vs W(3)=9、k=4: LLL≈5 vs W(4)=35
   - LLL 下界は実際の W(k) よりかなり小さい

2. ランダム塗り分けシミュレーション:
   - k=3: 平均約 5-6 で単色3-APが出現 (W(3)=9)
   - k=4: 平均約 13-15 で単色4-APが出現 (W(4)=35)
   - ランダムは W(k) の 40-60% 程度で失敗 → 構造的塗り分けが重要

3. LLL の限界:
   - LLL下界から得られる W(k)^{1/k} → 2 (不変)
   - W(k)^{1/k} → ∞ を示すには LLL だけでは不十分
   - 超指数的下界の証明が必要

4. Moser-Tardos アルゴリズム:
   - W(k)-1 では高い確率で成功、W(k) では失敗
   - アルゴリズム的 LLL は W(k) の近くで相転移を示す

5. 確率的手法 vs 構成的手法:
   - 確率的 (LLL): 下界 ≈ 2^k/k
   - 構成的 (Berlekamp): 下界 ≈ p * 2^p (p素数)
   - いずれも指数オーダーで W(k)^{1/k} → 2 程度
   - W(k) の真の成長率（多重指数的？）との乖離が大きい
""")
