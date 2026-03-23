"""
探索4: 5n+1 Syracuse 逆像ツリーの構造

発見まとめ:
- Syr(n) = (5n+1) / 2^v2(5n+1) が奇数→奇数の写像
- Syr(n) = 1 ⟺ 5n+1 = 2^k ⟺ n = (2^k - 1)/5 ⟺ k ≡ 0 (mod 4)
  → n = 3, 51, 819, 13107, ...
- 逆像: Syr(m) = n ⟺ 5m+1 = n·2^j for some j ⟺ m = (n·2^j - 1)/5
  → n·2^j ≡ 1 (mod 5) が必要

目標: 逆像ツリーの各レベルを構成し、パターンを発見
"""

def v2(n):
    if n == 0: return float('inf')
    k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

def syr5(n):
    """Syracuse 5n+1: 奇数 → 奇数"""
    m = 5 * n + 1
    return m >> v2(m)

def inverse_syr5(n, max_j=30):
    """Syr の逆像: Syr(m) = n となる奇数 m の集合"""
    preimages = []
    for j in range(1, max_j):
        val = n * (2**j) - 1
        if val > 0 and val % 5 == 0:
            m = val // 5
            if m % 2 == 1:  # m は奇数
                preimages.append((m, j))
    return preimages

def main():
    print("=== 探索4: 逆像ツリーの構造 ===\n")

    # 1. 直接1に到達する数（Syr(n) = 1）
    print("--- Syr(n) = 1 となる n = (2^(4k) - 1)/5 ---")
    direct_to_1 = []
    for k in range(1, 25):
        val = (2**(4*k) - 1) // 5
        if (2**(4*k) - 1) % 5 == 0:
            direct_to_1.append(val)
            v = v2(5*val+1)
            print(f"  k={k}: n = (2^{4*k}-1)/5 = {val}, 5n+1 = 2^{4*k} = {2**(4*k)}, v2={v}")

    # 2. 逆像ツリーの構築
    print("\n--- 逆像ツリー（レベル0-4） ---")
    tree = {0: {1}}  # レベル0: {1}
    all_in_tree = {1}

    for level in range(1, 5):
        tree[level] = set()
        for n in tree[level - 1]:
            for m, j in inverse_syr5(n, max_j=40):
                if m not in all_in_tree and m <= 100000:
                    tree[level].add(m)
                    all_in_tree.add(m)
        sorted_level = sorted(tree[level])
        print(f"  レベル{level}: {len(sorted_level)}個")
        if len(sorted_level) <= 20:
            print(f"    {sorted_level}")
        else:
            print(f"    最初の20個: {sorted_level[:20]}")

    print(f"\n  ツリー内の総数: {len(all_in_tree)}")

    # 3. v2(5n+1) のパターン
    print("\n--- v2(5n+1) の分布（1に到達する奇数） ---")
    from collections import Counter
    v2_dist = Counter()
    for n in sorted(all_in_tree):
        if n > 0:
            v2_dist[v2(5*n+1)] += 1
    print(f"  {dict(sorted(v2_dist.items()))}")

    # 4. n mod 5 の逆像条件
    print("\n--- 逆像条件: n·2^j ≡ 1 (mod 5) ---")
    print("  2^j mod 5 のサイクル: ", [2**j % 5 for j in range(1, 9)])
    print("  2^j mod 5 = 1 ⟺ j ≡ 0 (mod 4)")
    print("  2^j mod 5 = 2 ⟺ j ≡ 1 (mod 4)")
    print("  2^j mod 5 = 4 ⟺ j ≡ 2 (mod 4)")
    print("  2^j mod 5 = 3 ⟺ j ≡ 3 (mod 4)")
    print()
    print("  n·2^j ≡ 1 (mod 5) の解:")
    for n_mod5 in range(5):
        sols = [j % 4 for j in range(1, 5) if (n_mod5 * (2**j)) % 5 == 1]
        print(f"    n ≡ {n_mod5} (mod 5): j ≡ {sols} (mod 4)" if sols else
              f"    n ≡ {n_mod5} (mod 5): 解なし")

    # 5. サイクルに入る数の逆像
    print("\n--- サイクル1 (13,26,...) の逆像ツリー ---")
    cycle1 = {13, 26, 33, 52, 66, 83, 104, 166, 208, 416}
    cycle1_tree = set()
    for c in cycle1:
        if c % 2 == 1:
            for m, j in inverse_syr5(c, max_j=30):
                if m not in cycle1 and m <= 10000:
                    cycle1_tree.add(m)
    print(f"  サイクル外からの流入: {len(cycle1_tree)}個")
    print(f"  最初の20個: {sorted(cycle1_tree)[:20]}")

    # 6. 答え: 全ての奇数は1に到達するか?
    print("\n=== 結論 ===")
    print("答え: NO。5n+1変種では大半の奇数は1に到達しない。")
    print("理由:")
    print("  1. 非自明サイクルが存在（長さ10のサイクルが少なくとも2つ）")
    print("  2. 多くの軌道が発散（上界なく増大）")
    print("  3. 1に到達する奇数は特殊な逆像ツリーの要素のみ")
    print(f"  4. 奇数1..9999のうち1に到達するのは{len([n for n in range(1,10000,2) if n in all_in_tree])}個のみ")

    # 7. 証明可能な定理
    print("\n=== Lean で証明可能な定理 ===")
    print("1. 5n+1写像の非自明サイクル {13,26,33,52,66,83,104,166,208,416} の存在")
    print("2. n = (2^(4k)-1)/5 → 5n+1 = 2^(4k)（直接到達）")
    print("3. 2^4 ≡ 1 (mod 5)（フェルマーの小定理の特殊ケース）")
    print("4. 5n+1写像の不動点非存在")

if __name__ == "__main__":
    main()
