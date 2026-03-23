"""
探索8: 5n+1 のサイクル完全分類

疑問:
1. 長さ10のサイクルは2つだけか？他にもあるか？
2. 長さ10以外のサイクルはあるか？
3. 1に到達する数の密度は0か？

深掘り: サイクルの代数的構造
サイクル: n₁ → 5n₁+1 → (5n₁+1)/2^a₁ = n₂ → ... → n₁
つまり: Syracuse 写像 S の周期点
"""

def v2(n):
    if n == 0: return 0
    k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

def syr5(n):
    m = 5 * n + 1
    return m >> v2(m)

def step5(n):
    return n // 2 if n % 2 == 0 else 5 * n + 1

def main():
    print("=== 探索8: 5n+1 サイクルの完全分類 ===\n")

    # 1. Syracuse 写像の全周期点を列挙（奇数のみ）
    print("--- Syracuse 5n+1 の周期点列挙（奇数 ≤ 100000） ---")
    cycles = {}
    for n in range(1, 100001, 2):
        # Syracuse 軌道を追跡
        seen = {}
        current = n
        for step in range(1000):
            if current in seen:
                # サイクル発見
                cycle_start = seen[current]
                cycle = []
                c = current
                for _ in range(step - cycle_start):
                    cycle.append(c)
                    c = syr5(c)
                cycle_key = tuple(sorted(cycle))
                if cycle_key not in cycles:
                    cycles[cycle_key] = {
                        'elements': sorted(cycle),
                        'length': len(cycle),
                        'min': min(cycle),
                        'max': max(cycle),
                        'first_found': n
                    }
                break
            if current == 1:
                break
            seen[current] = step
            current = syr5(current)

    print(f"発見されたサイクル数: {len(cycles)}")
    for i, (key, info) in enumerate(sorted(cycles.items(), key=lambda x: x[1]['min'])):
        print(f"\n  サイクル{i+1}:")
        print(f"    長さ: {info['length']}")
        print(f"    min={info['min']}, max={info['max']}")
        if info['length'] <= 20:
            # Syracuse 順序で表示
            start = info['elements'][0]
            seq = [start]
            c = syr5(start)
            while c != start:
                seq.append(c)
                c = syr5(c)
            print(f"    Syracuse順: {' → '.join(map(str, seq))}")

    # 2. サイクルの代数的分析
    print("\n--- サイクルの代数的構造 ---")
    for key, info in sorted(cycles.items(), key=lambda x: x[1]['min']):
        elements = info['elements']
        start = elements[0]
        # 各ステップの v₂ を記録
        v2_seq = []
        c = start
        for _ in range(info['length']):
            v = v2(5 * c + 1)
            v2_seq.append(v)
            c = syr5(c)

        total_v2 = sum(v2_seq)
        print(f"  サイクル(min={info['min']}): v₂列 = {v2_seq}")
        print(f"    Σv₂ = {total_v2}")
        print(f"    5^{info['length']} / 2^{total_v2} = "
              f"{5**info['length']}/{2**total_v2} = {5**info['length']/2**total_v2:.6f}")
        print(f"    → サイクル条件: 5^k / 2^(Σv₂) ≈ 1 （周期点の必要条件）")

    # 3. サイクル条件の理論的分析
    print("\n--- サイクル条件: 5^k ≈ 2^s の解 ---")
    print("  k-サイクルでは 5^k = 2^s · (補正項) が必要")
    print("  s = Σv₂ は k ステップでの総除算回数")
    print()
    import math
    print("  5^k と 2^s の近似:")
    for k in range(1, 21):
        s_approx = k * math.log2(5)
        s_floor = int(s_approx)
        s_ceil = s_floor + 1
        ratio_floor = 5**k / 2**s_floor
        ratio_ceil = 5**k / 2**s_ceil
        if 0.8 < ratio_floor < 1.3 or 0.8 < ratio_ceil < 1.3:
            print(f"    k={k:2d}: s≈{s_approx:.2f}, "
                  f"5^{k}/2^{s_floor}={ratio_floor:.4f}, "
                  f"5^{k}/2^{s_ceil}={ratio_ceil:.4f}")

    # 4. 1に到達する数の密度
    print("\n--- 1に到達する奇数の密度 ---")
    for limit in [100, 1000, 10000, 50000]:
        count = 0
        for n in range(1, limit + 1, 2):
            seen = set()
            c = n
            reached = False
            for _ in range(10000):
                if c == 1:
                    reached = True
                    break
                if c in seen:
                    break
                seen.add(c)
                c = step5(c)
            if reached:
                count += 1
        total_odd = (limit + 1) // 2
        print(f"  奇数 ≤ {limit:6d}: 到達={count:5d}/{total_odd:5d} = {100*count/total_odd:.3f}%")

if __name__ == "__main__":
    main()
