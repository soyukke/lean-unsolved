"""
探索2: 5n+1 変種の深堀り

発見:
- 1に到達するのは全体の2.56%
- 2つの非自明サイクル（長さ10）
- 大半は「発散」

疑問:
1. 1に到達する数はどんな構造？
2. サイクルに入る数の特徴は？
3. 「発散」は本当に発散か、巨大サイクルか？
"""

def step(n):
    return n // 2 if n % 2 == 0 else 5 * n + 1

def trajectory(n, max_steps=100000):
    traj = [n]
    visited = {n}
    for _ in range(max_steps):
        n = step(n)
        traj.append(n)
        if n == 1:
            return traj, "reaches_1"
        if n in visited:
            idx = traj.index(n)
            return traj, ("cycle", traj[idx:-1])
        visited.add(n)
    return traj, "unknown"

def main():
    print("=== 探索2: 1に到達する数の構造 ===\n")

    # 1に到達する数を詳しく調べる
    reaches_1_set = set()
    for n in range(1, 100001):
        _, status = trajectory(n, max_steps=10000)
        if status == "reaches_1":
            reaches_1_set.add(n)

    print(f"n=1..100000 で1に到達する数: {len(reaches_1_set)}")

    # 小さい順に列挙
    sorted_r1 = sorted(reaches_1_set)
    print(f"最初の50個: {sorted_r1[:50]}")

    # 2のべき乗チェック
    powers_of_2 = {2**k for k in range(20)}
    r1_powers = reaches_1_set & powers_of_2
    print(f"\n2のべき乗で到達: {sorted(r1_powers)}")

    # 2進表現の分析
    print(f"\n--- 1に到達する数の2進表現 ---")
    for n in sorted_r1[:30]:
        print(f"  {n:6d} = {bin(n):>20s}  (v2={n & -n if n > 0 else 0})")

    # 1に到達する数の mod パターン
    print(f"\n--- mod パターン ---")
    for m in [2, 3, 4, 5, 6, 8, 10, 16]:
        counts = [0] * m
        for n in sorted_r1:
            if n <= 10000:
                counts[n % m] += 1
        print(f"  mod {m:2d}: {counts}")

    # 3·2^k の形の数
    print(f"\n--- 3·2^k の形 ---")
    for k in range(20):
        n = 3 * (2 ** k)
        if n <= 100000:
            _, status = trajectory(n, max_steps=10000)
            label = "reaches_1" if status == "reaches_1" else str(status)[:30]
            print(f"  3·2^{k} = {n}: {label}")

    # p·2^k (p=1,3,5,7,...) の形
    print(f"\n--- p·2^k の形で1に到達するか ---")
    for p in [1, 3, 5, 7, 9, 11, 13, 15, 19, 25]:
        results = []
        for k in range(15):
            n = p * (2 ** k)
            if n <= 100000 and n >= 1:
                _, status = trajectory(n, max_steps=10000)
                results.append(("✓" if status == "reaches_1" else "✗", k))
        r_str = " ".join(f"k={k}:{s}" for s, k in results[:10])
        print(f"  p={p:3d}: {r_str}")

    # サイクルに入る数の分析
    print(f"\n=== サイクルに入る数の分析 ===")
    cycle1_set = set()  # {13, 26, 33, 52, 66, 83, 104, 166, 208, 416}
    cycle2_set = set()  # {17, 27, 34, 43, 54, 68, 86, 108, 136, 216}

    for n in range(1, 10001):
        _, status = trajectory(n, max_steps=10000)
        if isinstance(status, tuple) and status[0] == "cycle":
            cycle = set(status[1])
            if 13 in cycle:
                cycle1_set.add(n)
            elif 17 in cycle:
                cycle2_set.add(n)

    print(f"サイクル1（13を含む）に到達する数: {len(cycle1_set)}")
    print(f"  最初の20個: {sorted(cycle1_set)[:20]}")
    print(f"サイクル2（17を含む）に到達する数: {len(cycle2_set)}")
    print(f"  最初の20個: {sorted(cycle2_set)[:20]}")

    # サイクルの mod 10 構造
    print(f"\n--- サイクル1の要素 mod 10 ---")
    c1 = [26, 13, 66, 33, 166, 83, 416, 208, 104, 52]
    print(f"  サイクル: {c1}")
    print(f"  mod 10: {[x % 10 for x in c1]}")
    print(f"  mod 5:  {[x % 5 for x in c1]}")
    print(f"  mod 3:  {[x % 3 for x in c1]}")

    print(f"\n--- サイクル2の要素 mod 10 ---")
    c2 = [17, 86, 43, 216, 108, 54, 27, 136, 68, 34]
    print(f"  サイクル: {c2}")
    print(f"  mod 10: {[x % 10 for x in c2]}")
    print(f"  mod 5:  {[x % 5 for x in c2]}")
    print(f"  mod 3:  {[x % 3 for x in c2]}")

if __name__ == "__main__":
    main()
