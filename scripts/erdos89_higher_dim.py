"""
高次元格子の異なる距離の最小化

d次元格子上の n 点配置で異なる距離を最小化する。
d=2 では √n × √n 格子が最適。d=3 では？
"""
import math
from itertools import product as cartesian_product

def distinct_distances_grid(dim, side_length):
    """d次元格子の異なる距離の数を計算"""
    points = list(cartesian_product(range(side_length), repeat=dim))
    n = len(points)

    dist_sq_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            d2 = sum((points[i][k] - points[j][k])**2 for k in range(dim))
            dist_sq_set.add(d2)

    return n, len(dist_sq_set)

def main():
    print("=== 高次元格子の異なる距離 ===\n")

    for dim in [2, 3, 4]:
        print(f"--- 次元 d = {dim} ---")
        for side in range(2, 8 if dim <= 3 else 5):
            n, d = distinct_distances_grid(dim, side)
            ratio = d / n if n > 0 else 0
            log_n = math.log(n) if n > 1 else 1
            normalized = d / (n / math.sqrt(log_n)) if n > 1 else 0
            print(f"  side={side}: n={n}, d(n)={d}, d/n={ratio:.3f}, "
                  f"d/(n/√logn)={normalized:.3f}")
        print()

if __name__ == "__main__":
    main()
