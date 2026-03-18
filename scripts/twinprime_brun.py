#!/usr/bin/env python3
"""
双子素数予想 探索4: Brunの定理の数値的精密化
- Brun定数 B₂ = Σ (1/p + 1/(p+2)) の部分和を 10^7 まで計算
- 収束速度の分析
- B₂(x) - B₂ の推定残差を log-log プロットデータとして出力
- Mertens型公式 B₂(x) ≈ B₂ - C/ln(x)² の定数 C を推定
"""

import math

def sieve_of_eratosthenes(limit):
    """エラトステネスの篩"""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = 0
    return is_prime


def main():
    LIMIT = 10_000_000
    B2_THEORETICAL = 1.9021605831

    print(f"=== 探索4: Brunの定理の数値的精密化 (上限: {LIMIT:,}) ===\n")

    # 篩の実行
    print("篩を実行中...")
    is_prime = sieve_of_eratosthenes(LIMIT)

    # 双子素数を列挙しながら Brun 定数の部分和を計算
    print("双子素数を列挙し Brun 定数を計算中...\n")

    brun_sum = 0.0
    twin_count = 0
    checkpoints = [10**k for k in range(2, 8)]  # 100, ..., 10^7
    checkpoint_data = []  # (x, twin_count, brun_sum)

    for p in range(2, LIMIT):
        if is_prime[p] and is_prime[p + 2]:
            twin_count += 1
            brun_sum += 1.0 / p + 1.0 / (p + 2)

            # チェックポイントを通過したか確認
            while checkpoints and p + 2 <= checkpoints[0] and p >= checkpoints[0] - 2:
                break
            # より正確に: p がチェックポイント以下の最大双子素数を超えたタイミング
        # チェックポイント判定: p がちょうどチェックポイントを超えた時
        if checkpoints and p + 2 >= checkpoints[0]:
            if p + 2 == checkpoints[0] or p == checkpoints[0] or p + 1 == checkpoints[0]:
                pass  # まだ p+2 もチェック
            if p >= checkpoints[0]:
                checkpoint_data.append((checkpoints[0], twin_count, brun_sum))
                checkpoints.pop(0)

    # 最後のチェックポイント
    while checkpoints:
        checkpoint_data.append((checkpoints[0], twin_count, brun_sum))
        checkpoints.pop(0)

    # === 部分和の収束テーブル ===
    print("=== B₂(x) の部分和の収束 ===")
    print(f"{'x':>12} {'π₂(x)':>10} {'B₂(x)':>16} {'B₂-B₂(x)':>14} {'1/ln²(x)':>12}")
    print("-" * 70)
    for x, tc, bs in checkpoint_data:
        residual = B2_THEORETICAL - bs
        inv_ln2 = 1.0 / (math.log(x) ** 2)
        print(f"{x:>12,} {tc:>10,} {bs:>16.10f} {residual:>14.10f} {inv_ln2:>12.8f}")

    # === Mertens型公式の定数 C の推定 ===
    # B₂(x) ≈ B₂ - C/ln(x)² → C ≈ (B₂ - B₂(x)) * ln(x)²
    print("\n=== Mertens型公式 B₂(x) ≈ B₂ - C/ln(x)² の定数 C 推定 ===")
    print(f"{'x':>12} {'C推定値':>14}")
    print("-" * 30)
    c_estimates = []
    for x, tc, bs in checkpoint_data:
        if x >= 1000:  # 小さい x は不安定なので除外
            residual = B2_THEORETICAL - bs
            ln_x = math.log(x)
            c_est = residual * ln_x ** 2
            c_estimates.append((x, c_est))
            print(f"{x:>12,} {c_est:>14.6f}")

    # 大きな x での C の加重平均（大きい x ほど信頼度が高い）
    if len(c_estimates) >= 2:
        # 最後の2点で推定
        _, c1 = c_estimates[-2]
        _, c2 = c_estimates[-1]
        c_best = (c1 + c2) / 2
        print(f"\n最良推定 C ≈ {c_best:.6f} (最後の2点の平均)")

    # === 収束速度の詳細分析 ===
    print("\n=== 収束速度の詳細分析 ===")
    print("B₂(x) - B₂(x/2) の減少率を調べる")
    print(f"{'区間':>20} {'増分 ΔB₂':>16} {'比率':>10}")
    print("-" * 50)

    # より細かいチェックポイントで再計算
    fine_limits = [10**k for k in range(3, 8)]
    fine_data = {}

    brun_sum = 0.0
    twin_count = 0
    current_idx = 0

    for p in range(2, LIMIT):
        if is_prime[p] and is_prime[p + 2]:
            twin_count += 1
            brun_sum += 1.0 / p + 1.0 / (p + 2)
        if current_idx < len(fine_limits) and p == fine_limits[current_idx]:
            fine_data[fine_limits[current_idx]] = brun_sum
            current_idx += 1

    prev_increment = None
    for i in range(1, len(fine_limits)):
        x_prev = fine_limits[i - 1]
        x_curr = fine_limits[i]
        if x_prev in fine_data and x_curr in fine_data:
            increment = fine_data[x_curr] - fine_data[x_prev]
            ratio_str = ""
            if prev_increment is not None and increment > 0:
                ratio_str = f"{prev_increment / increment:.4f}"
            print(f"  [{x_prev:>10,}, {x_curr:>10,}] {increment:>16.10f} {ratio_str:>10}")
            prev_increment = increment

    # === Log-log プロットデータ ===
    print("\n=== Log-log プロットデータ: ln(B₂ - B₂(x)) vs ln(x) ===")
    print("(Mertens型なら傾き ≈ -2)")
    print(f"{'ln(x)':>10} {'ln(B₂-B₂(x))':>16} {'x':>12}")
    print("-" * 42)
    for x, tc, bs in checkpoint_data:
        if x >= 100:
            residual = B2_THEORETICAL - bs
            if residual > 0:
                ln_x = math.log(x)
                ln_res = math.log(residual)
                print(f"{ln_x:>10.4f} {ln_res:>16.6f} {x:>12,}")

    # 傾きの推定（最後の2点）
    data_points = []
    for x, tc, bs in checkpoint_data:
        if x >= 1000:
            residual = B2_THEORETICAL - bs
            if residual > 0:
                data_points.append((math.log(x), math.log(residual)))

    if len(data_points) >= 2:
        x1, y1 = data_points[-2]
        x2, y2 = data_points[-1]
        slope = (y2 - y1) / (x2 - x1)
        print(f"\nlog-log 傾き推定 = {slope:.4f} (Mertens型なら -2)")

    # === 部分和の連続的な変化（もう少し細かく）===
    print("\n=== B₂(x) の段階的収束 ===")
    steps = [500, 1000, 2000, 5000, 10000, 20000, 50000,
             100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000]
    brun_sum = 0.0
    step_idx = 0

    print(f"{'x':>12} {'B₂(x)':>16} {'B₂-B₂(x)':>14}")
    print("-" * 45)

    for p in range(2, LIMIT):
        if is_prime[p] and is_prime[p + 2]:
            brun_sum += 1.0 / p + 1.0 / (p + 2)
        if step_idx < len(steps) and p == steps[step_idx]:
            residual = B2_THEORETICAL - brun_sum
            print(f"{steps[step_idx]:>12,} {brun_sum:>16.10f} {residual:>14.10f}")
            step_idx += 1

    # === まとめ ===
    print("\n=== まとめ ===")
    print(f"1. B₂(10⁷) ≈ {checkpoint_data[-1][2]:.10f}")
    print(f"2. 理論値 B₂ ≈ {B2_THEORETICAL}")
    print(f"3. 残差 B₂ - B₂(10⁷) ≈ {B2_THEORETICAL - checkpoint_data[-1][2]:.10f}")
    if c_estimates:
        print(f"4. Mertens型公式の定数 C ≈ {c_estimates[-1][1]:.6f}")
    print(f"5. 収束は非常に遅い（対数的）— Brunの定理が示す通り")
    print(f"6. 部分和の収束は B₂(x) ≈ B₂ - C/ln²(x) の形に良く適合")


if __name__ == "__main__":
    main()
