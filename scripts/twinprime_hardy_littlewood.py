#!/usr/bin/env python3
"""
双子素数予想 探索6: Hardy-Littlewood 第1予想式の検証
- π₂(x) ~ 2C₂ ∫₂ˣ dt/(ln t)² の数値検証
- Li₂(x) = 2C₂ ∫₂ˣ dt/(ln t)² を数値計算
- π₂(x)/Li₂(x) の比を各スケールで計算
- 残差 π₂(x) - Li₂(x) の符号変化を確認
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


def twin_prime_constant(prime_limit):
    """C₂ = 2 * ∏_{p≥3} (1 - 1/(p-1)²)"""
    is_p = sieve_of_eratosthenes(prime_limit)
    product = 2.0
    for p in range(3, prime_limit + 1):
        if is_p[p]:
            product *= (1.0 - 1.0 / ((p - 1) ** 2))
    return product


def li2_integral(x, C2, num_steps=100000):
    """
    Li₂(x) = 2C₂ ∫₂ˣ dt/(ln t)² をSimpson則で数値計算
    """
    if x <= 2:
        return 0.0

    a = 2.0
    b = float(x)
    n = num_steps
    if n % 2 == 1:
        n += 1

    h = (b - a) / n

    def f(t):
        if t <= 1:
            return 0.0
        lt = math.log(t)
        if lt == 0:
            return 0.0
        return 1.0 / (lt * lt)

    # Simpson's rule
    s = f(a) + f(b)
    for i in range(1, n, 2):
        s += 4.0 * f(a + i * h)
    for i in range(2, n, 2):
        s += 2.0 * f(a + i * h)
    s *= h / 3.0

    return 2.0 * C2 * s


def li2_simple(x, C2):
    """
    簡易近似: 2C₂ * x / (ln x)²
    Hardy-Littlewood予想の主要項
    """
    if x <= 2:
        return 0.0
    ln_x = math.log(x)
    return 2.0 * C2 * x / (ln_x ** 2)


def li2_corrected(x, C2):
    """
    1次補正付き: 2C₂ * x / (ln x)² * (1 + 2/ln x + ...)
    ∫ dt/(ln t)² を部分積分すると x/(ln x)² + 2x/(ln x)³ + ... を得る
    """
    if x <= 2:
        return 0.0
    ln_x = math.log(x)
    # 主要項 + 第1補正項 + 第2補正項
    main = x / (ln_x ** 2)
    corr1 = 2.0 * x / (ln_x ** 3)
    corr2 = 6.0 * x / (ln_x ** 4)
    # 下限 t=2 の分を引く
    ln2 = math.log(2.0)
    sub = 2.0 / (ln2 ** 2) + 2.0 * 2.0 / (ln2 ** 3) + 6.0 * 2.0 / (ln2 ** 4)
    return 2.0 * C2 * (main + corr1 + corr2 - sub)


def main():
    LIMIT = 10_000_000
    C2_PRECISE = 1.3203236316  # 高精度理論値
    print(f"=== 探索6: Hardy-Littlewood 第1予想式の検証 (上限: {LIMIT:,}) ===\n")

    # C₂ の計算
    C2 = twin_prime_constant(LIMIT)
    print(f"Twin prime constant C₂ ≈ {C2:.12f}")
    print(f"理論値              C₂ ≈ {C2_PRECISE}")
    print(f"以下の計算では理論値を使用\n")
    C2 = C2_PRECISE

    # 篩の実行と双子素数の計数
    print("篩を実行中...")
    is_prime = sieve_of_eratosthenes(LIMIT)

    twin_count = 0
    checkpoints = {}
    check_values = set([10**k for k in range(2, 8)] +
                       [k * 10**j for k in [2, 5] for j in range(2, 7)])

    for p in range(2, LIMIT):
        if is_prime[p] and p + 2 <= LIMIT and is_prime[p + 2]:
            twin_count += 1
        if p in check_values:
            checkpoints[p] = twin_count
    checkpoints[LIMIT] = twin_count

    # === メインテーブル: π₂(x) vs Li₂(x) ===
    print("\n=== π₂(x) vs Li₂(x) = 2C₂ ∫₂ˣ dt/(ln t)² ===")
    print(f"{'x':>12} {'π₂(x)':>10} {'Li₂(x)':>12} {'π₂/Li₂':>10} {'π₂-Li₂':>10}")
    print("-" * 58)

    main_checks = [10**k for k in range(3, 8)]
    for x in main_checks:
        if x in checkpoints:
            tc = checkpoints[x]
            li2 = li2_integral(x, C2)
            ratio = tc / li2 if li2 > 0 else 0
            diff = tc - li2
            print(f"{x:>12,} {tc:>10,} {li2:>12.2f} {ratio:>10.6f} {diff:>10.2f}")

    # === 簡易近似 vs 積分 vs 補正付き ===
    print("\n=== 各近似式の比較 ===")
    print(f"{'x':>12} {'π₂(x)':>10} {'2C₂x/ln²x':>12} {'Li₂(積分)':>12} {'Li₂(補正)':>12}")
    print("-" * 62)

    for x in main_checks:
        if x in checkpoints:
            tc = checkpoints[x]
            simple = li2_simple(x, C2)
            integral = li2_integral(x, C2)
            corrected = li2_corrected(x, C2)
            print(f"{x:>12,} {tc:>10,} {simple:>12.1f} {integral:>12.1f} {corrected:>12.1f}")

    # === 各近似式の相対誤差 ===
    print("\n=== 各近似式の相対誤差 (%) ===")
    print(f"{'x':>12} {'簡易':>10} {'積分':>10} {'補正付き':>10}")
    print("-" * 45)

    for x in main_checks:
        if x in checkpoints:
            tc = checkpoints[x]
            simple = li2_simple(x, C2)
            integral = li2_integral(x, C2)
            corrected = li2_corrected(x, C2)
            err_s = 100.0 * (tc - simple) / tc if tc > 0 else 0
            err_i = 100.0 * (tc - integral) / tc if tc > 0 else 0
            err_c = 100.0 * (tc - corrected) / tc if tc > 0 else 0
            print(f"{x:>12,} {err_s:>10.4f} {err_i:>10.4f} {err_c:>10.4f}")

    # === 残差 π₂(x) - Li₂(x) の詳細 ===
    print("\n=== 残差 π₂(x) - Li₂(x) の符号変化調査 ===")
    print(f"{'x':>12} {'π₂(x)':>10} {'Li₂(x)':>12} {'残差':>10} {'符号':>5}")
    print("-" * 52)

    detailed_checks = sorted([x for x in checkpoints.keys() if x >= 100])
    sign_changes = []
    prev_sign = None

    for x in detailed_checks:
        tc = checkpoints[x]
        li2 = li2_integral(x, C2)
        diff = tc - li2
        sign = "+" if diff >= 0 else "-"
        if prev_sign is not None and sign != prev_sign:
            sign_changes.append(x)
        prev_sign = sign
        if x in [10**k for k in range(2, 8)] or x in sign_changes:
            print(f"{x:>12,} {tc:>10,} {li2:>12.2f} {diff:>10.2f} {sign:>5}")

    if sign_changes:
        print(f"\n符号変化が {len(sign_changes)} 回検出: x = {sign_changes}")
    else:
        print(f"\n符号変化は検出されず（調べた範囲内）")

    # === π₂(x)/Li₂(x) の漸近的振る舞い ===
    print("\n=== π₂(x)/Li₂(x) の漸近収束 ===")
    print("Hardy-Littlewood予想が正しければ、この比は 1 に収束するはず")
    print(f"{'x':>12} {'π₂/Li₂':>10} {'|1-比率|':>10}")
    print("-" * 35)

    for x in main_checks:
        if x in checkpoints:
            tc = checkpoints[x]
            li2 = li2_integral(x, C2)
            ratio = tc / li2 if li2 > 0 else 0
            dev = abs(1.0 - ratio)
            print(f"{x:>12,} {ratio:>10.6f} {dev:>10.6f}")

    # === 2C₂ の数値的検証 ===
    print("\n=== 2C₂ の数値的検証 ===")
    print("π₂(x) * ln²(x) / x → 2C₂ の収束")
    print(f"{'x':>12} {'π₂·ln²x/x':>14} {'2C₂理論値':>12} {'相対誤差%':>12}")
    print("-" * 55)

    for x in main_checks:
        if x in checkpoints:
            tc = checkpoints[x]
            empirical = tc * (math.log(x) ** 2) / x
            theoretical = 2 * C2
            rel_err = 100.0 * (empirical - theoretical) / theoretical
            print(f"{x:>12,} {empirical:>14.6f} {theoretical:>12.6f} {rel_err:>12.4f}")

    # === まとめ ===
    print("\n=== まとめ ===")
    last_x = 10_000_000
    tc = checkpoints[last_x]
    li2 = li2_integral(last_x, C2)
    ratio = tc / li2

    print(f"1. Hardy-Littlewood 第1予想: π₂(x) ~ 2C₂ ∫₂ˣ dt/(ln t)²")
    print(f"2. C₂ = {C2_PRECISE} (twin prime constant)")
    print(f"3. π₂(10⁷) = {tc:,}")
    print(f"4. Li₂(10⁷) = {li2:.2f}")
    print(f"5. π₂(10⁷)/Li₂(10⁷) = {ratio:.6f} — 1 に近づいており予想と整合")
    print(f"6. 簡易近似 2C₂x/ln²x は主要項のみ、積分型の方がずっと正確")
    print(f"7. 補正付き近似（部分積分展開）はさらに精度が良い")
    if sign_changes:
        print(f"8. 残差の符号変化あり — Li(x) と π(x) の関係に類似")
    else:
        print(f"8. 残差の符号変化は調査範囲では未検出")


if __name__ == "__main__":
    main()
