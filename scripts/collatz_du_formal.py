"""
探索45: コラッツ軌道の d/u 比の精密数値計算

down step (÷2) と up step (3n+1) の比 d/u を解析。
理論的には log_2(3) ≈ 1.585 に関連。
"""
import math
from collections import Counter


def collatz_trajectory(n, max_steps=10000):
    """コラッツ軌道を返す"""
    traj = [n]
    for _ in range(max_steps):
        if n == 1:
            break
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        traj.append(n)
    return traj


def count_du(n):
    """down/up ステップ数を返す"""
    d, u = 0, 0
    current = n
    while current != 1 and d + u < 100000:
        if current % 2 == 0:
            current = current // 2
            d += 1
        else:
            current = 3 * current + 1
            u += 1
    return d, u


def main():
    print("=== コラッツ軌道 d/u 比の精密計算 ===")
    print(f"理論値: log_2(3) = {math.log2(3):.10f}")
    print()

    # 奇数に対する d/u 比
    ratios = []
    for n in range(3, 10001, 2):
        d, u = count_du(n)
        if u > 0:
            ratio = d / u
            ratios.append((n, d, u, ratio))

    print(f"奇数 3~9999 の d/u 比統計:")
    ratio_vals = [r[3] for r in ratios]
    print(f"  平均: {sum(ratio_vals)/len(ratio_vals):.6f}")
    print(f"  最小: {min(ratio_vals):.6f} (n={min(ratios, key=lambda x: x[3])[0]})")
    print(f"  最大: {max(ratio_vals):.6f} (n={max(ratios, key=lambda x: x[3])[0]})")
    print()

    # mod 3 別の d/u 比
    for r in [1, 2]:
        subset = [x for x in ratios if x[0] % 3 == r]
        vals = [x[3] for x in subset]
        print(f"  n ≡ {r} (mod 3): 平均 d/u = {sum(vals)/len(vals):.6f}")

    # mod 6 別の詳細分析
    print("\nmod 6 別の d/u 比:")
    for r in [1, 3, 5]:
        subset = [x for x in ratios if x[0] % 6 == r]
        if subset:
            vals = [x[3] for x in subset]
            print(f"  n ≡ {r} (mod 6): 平均 d/u = {sum(vals)/len(vals):.6f}, 個数={len(vals)}")

    # 特定の値の詳細
    print("\n特定の値の詳細:")
    for n in [3, 7, 27, 97, 871, 6171]:
        d, u = count_du(n)
        if u > 0:
            print(f"  n={n}: d={d}, u={u}, d/u={d/u:.4f}, steps={d+u}")

    # d/u 比の分布
    print("\nd/u 比の分布:")
    bins = [1.0, 1.2, 1.4, 1.585, 1.8, 2.0, 2.5, 3.0, 4.0]
    for i in range(len(bins) - 1):
        count = sum(1 for r in ratio_vals if bins[i] <= r < bins[i+1])
        print(f"  [{bins[i]:.1f}, {bins[i+1]:.1f}): {count} ({100*count/len(ratio_vals):.1f}%)")

    # log_2(3) との偏差の統計
    log23 = math.log2(3)
    deviations = [r - log23 for r in ratio_vals]
    print(f"\nlog_2(3) からの偏差:")
    print(f"  平均偏差: {sum(deviations)/len(deviations):.6f}")
    print(f"  標準偏差: {(sum(d**2 for d in deviations)/len(deviations))**0.5:.6f}")
    positive = sum(1 for d in deviations if d > 0)
    print(f"  d/u > log_2(3) の割合: {100*positive/len(deviations):.1f}%")


if __name__ == "__main__":
    main()
