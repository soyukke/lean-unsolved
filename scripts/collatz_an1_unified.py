"""
探索7: an+1 変種の統一理論

T_a(n) = n/2     (n even)
T_a(n) = an+1    (n odd)

a=3: 通常コラッツ（全到達予想）
a=5: 非自明サイクル、大半発散
a=7,9,11,...: ?

核心的疑問: a のどの値で「全到達」が起こるか？
仮説: a < 2^(期待v₂) のとき収束、そうでなければ発散
"""

def v2(n):
    if n == 0: return 0
    k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

def step_a(n, a):
    return n // 2 if n % 2 == 0 else a * n + 1

def trajectory_a(n, a, max_steps=10000):
    visited = set()
    for _ in range(max_steps):
        if n == 1: return "reaches_1"
        if n in visited: return "cycle"
        visited.add(n)
        n = step_a(n, a)
    return "unknown"

def main():
    print("=== 探索7: an+1 変種の統一理論 ===\n")

    # 各 a について到達率を計算
    print("--- a=1,3,5,7,9,11,13,15 の到達率 ---")
    for a in [1, 3, 5, 7, 9, 11, 13, 15]:
        reaches = 0
        cycles = 0
        unknown = 0
        for n in range(1, 10001):
            result = trajectory_a(n, a, 10000)
            if result == "reaches_1": reaches += 1
            elif result == "cycle": cycles += 1
            else: unknown += 1

        print(f"  a={a:2d}: 到達={reaches:5d}, サイクル={cycles:5d}, "
              f"不明={unknown:5d}, 到達率={100*reaches/10000:.1f}%")

    # v₂(an+1) の mod 構造
    print(f"\n--- v₂(an+1) の平均値（奇数 n ≤ 9999） ---")
    for a in [1, 3, 5, 7, 9, 11]:
        v2_sum = 0
        count = 0
        for n in range(1, 10000, 2):
            v2_sum += v2(a * n + 1)
            count += 1
        avg_v2 = v2_sum / count
        import math
        threshold = math.log2(a)
        print(f"  a={a:2d}: 平均v₂={avg_v2:.4f}, log₂(a)={threshold:.4f}, "
              f"{'収束' if avg_v2 > threshold else '発散'}傾向")

    # 幾何平均増加率の分析
    print(f"\n--- 幾何平均増加率 ---")
    import math
    for a in [1, 3, 5, 7, 9, 11]:
        # mod 2a の各奇数剰余類で v₂(an+1) を計算
        mod = 2 * a
        log_growth_sum = 0
        count = 0
        for r in range(1, mod, 2):
            v = v2(a * r + 1)
            growth = a / (2**v)
            if growth > 0:
                log_growth_sum += math.log(growth)
                count += 1
        if count > 0:
            geo_mean = math.exp(log_growth_sum / count)
            print(f"  a={a:2d}: 幾何平均増加率 = {geo_mean:.6f} "
                  f"({'> 1 (発散)' if geo_mean > 1 else '< 1 (収束)'})")

    # 分岐点の特定
    print(f"\n--- 分岐条件: a のどの値で収束→発散が切り替わるか ---")
    for a in range(1, 20, 2):
        mod = 2 * a
        log_sum = 0
        cnt = 0
        for r in range(1, mod, 2):
            v = v2(a * r + 1)
            g = a / (2**v)
            if g > 0:
                log_sum += math.log(g)
                cnt += 1
        if cnt > 0:
            gm = math.exp(log_sum / cnt)
            status = "発散" if gm > 1 else "収束"
            print(f"  a={a:2d}: geo_mean={gm:.6f} ({status})")

    # サイクルの探索
    print(f"\n--- 各 a でのサイクル ---")
    for a in [1, 3, 5, 7, 9]:
        cycles_found = set()
        for n in range(2, 1001):
            visited = {}
            current = n
            for step in range(10000):
                if current in visited:
                    cycle_start = visited[current]
                    cycle = []
                    c = current
                    for _ in range(step - cycle_start):
                        cycle.append(c)
                        c = step_a(c, a)
                    cycle_key = tuple(sorted(cycle))
                    if cycle_key not in cycles_found and 1 not in cycle:
                        cycles_found.add(cycle_key)
                        if len(cycles_found) <= 3:
                            print(f"  a={a}: サイクル(長さ{len(cycle)}): {cycle[:10]}{'...' if len(cycle)>10 else ''}")
                    break
                visited[current] = step
                current = step_a(current, a)
                if current == 1:
                    break
        if not cycles_found:
            print(f"  a={a}: 非自明サイクルなし（1..1000で探索）")

if __name__ == "__main__":
    main()
