"""
探索5: 5n+1 のv₂構造と増加率

核心的疑問: なぜ5n+1では大半の軌道が発散するのか？
→ v₂(5n+1) の分布が鍵。3n+1との比較。
"""

def v2(n):
    if n == 0: return float('inf')
    k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

def main():
    print("=== 探索5: v₂(5n+1) の mod 構造 ===\n")

    # v₂(5n+1) の mod 8 依存性
    print("--- v₂(5n+1) の mod 8 完全分類 ---")
    for r in [1, 3, 5, 7]:
        # n = 8k + r の場合
        vals = [v2(5 * (8 * k + r) + 1) for k in range(100)]
        from collections import Counter
        dist = Counter(vals)
        growth = (5 * r + 1) / (2 ** min(vals))
        print(f"  n ≡ {r} (mod 8): v₂ 分布 = {dict(sorted(dist.items()))}")
        print(f"    5n+1 = 5·{r}+1 = {5*r+1}, v₂({5*r+1}) = {v2(5*r+1)}")
        print(f"    Syracuse 値 ≈ 5n/{2**v2(5*r+1)}, 増加率 = 5/{2**v2(5*r+1)} = {5/(2**v2(5*r+1)):.4f}")

    # 3n+1 との比較
    print("\n--- 3n+1 との比較 ---")
    print("3n+1 の mod 4 分類:")
    for r in [1, 3]:
        v = v2(3 * r + 1)
        print(f"  n ≡ {r} (mod 4): v₂(3n+1) = {v}, 増加率 = 3/{2**v} = {3/(2**v):.4f}")

    print("\n5n+1 の mod 8 分類:")
    growth_factors_5 = []
    for r in [1, 3, 5, 7]:
        v = v2(5 * r + 1)
        gf = 5 / (2**v)
        growth_factors_5.append(gf)
        print(f"  n ≡ {r} (mod 8): v₂(5n+1) = {v}, 増加率 = 5/{2**v} = {gf:.4f}")

    # 幾何平均増加率
    import math
    geo_mean_5 = math.exp(sum(math.log(g) for g in growth_factors_5) / len(growth_factors_5))
    print(f"\n5n+1 の幾何平均増加率: {geo_mean_5:.6f}")
    print(f"  = (5^4 / (2·16·2·4))^(1/4) = (625/256)^(1/4) = {(625/256)**0.25:.6f}")

    growth_factors_3 = [3/4, 3/2]  # n≡1(mod4): v2=2, n≡3(mod4): v2=1
    geo_mean_3 = math.exp(sum(math.log(g) for g in growth_factors_3) / len(growth_factors_3))
    print(f"3n+1 の幾何平均増加率: {geo_mean_3:.6f}")
    print(f"  = (3^2 / (4·2))^(1/2) = (9/8)^(1/2) = {(9/8)**0.5:.6f}")

    print(f"\n★ 3n+1: {geo_mean_3:.4f} > 1 だが、偶数ステップ(÷2)を含めると < 1")
    print(f"★ 5n+1: {geo_mean_5:.4f} > 1 で、偶数ステップを含めても > 1")

    # より精密: 1ステップ（奇偶含む）の平均増加率
    print("\n--- 1ステップの平均増加率（奇偶含む） ---")
    # 奇数ステップ: n → 5n+1（×5）→ ÷2^v₂ で奇数に
    # 偶数ステップ: n → n/2
    # 奇数から: 平均 1 + v₂ ステップで次の奇数に
    # 増加率/ステップ = (5/2^v₂)^(1/(1+v₂))

    print("奇数から次の奇数までの平均ステップ数と増加率:")
    for r in [1, 3, 5, 7]:
        v = v2(5 * r + 1)
        steps = 1 + v  # 奇数→5n+1→÷2を v 回
        per_step = (5 / (2**v)) ** (1/steps)
        print(f"  n ≡ {r} (mod 8): {steps}ステップ, 増加率/ステップ = {per_step:.4f}")

    # mod 16 でさらに精密に
    print("\n--- v₂(5n+1) の mod 16 分類 ---")
    for r in range(1, 16, 2):
        v = v2(5 * r + 1)
        print(f"  n ≡ {r:2d} (mod 16): 5n+1 = {5*r+1:3d}, v₂ = {v}, (5n+1)/2^v₂ = {(5*r+1)//(2**v)}")

    # 重要な発見の確認
    print("\n=== 核心的な発見 ===")
    print("5n+1 変種で大半が発散する理由:")
    print(f"  幾何平均増加率 = (625/256)^(1/4) ≈ {(625/256)**0.25:.6f} > 1")
    print("  → 奇数ステップの平均的な増加が ÷2 を上回る")
    print()
    print("3n+1 (通常コラッツ) で収束が期待される理由:")
    print(f"  幾何平均増加率 = (9/8)^(1/2) ≈ {(9/8)**0.5:.6f} > 1")
    print("  しかし、偶数ステップ(÷2)がより頻繁に起こるため全体では < 1")
    print("  （v₂(3n+1) の期待値が log₂(3) ≈ 1.585 で、1ステップ÷2を上回る）")

    # Lean で証明可能な定理
    print("\n=== Lean で証明可能な新定理 ===")
    print("1. v₂(5n+1) の mod 8 完全分類（4パターン）")
    print("2. 625 > 256（増加率 > 1 の算術的根拠）")
    print("3. n ≡ 1 (mod 8) → (5n+1)/2 > 2n（具体的増加）")
    print("4. n ≡ 5 (mod 8) → (5n+1)/2 > 2n（具体的増加）")
    print("5. n ≡ 7 (mod 8) → (5n+1)/4 > n（具体的増加）")

if __name__ == "__main__":
    main()
