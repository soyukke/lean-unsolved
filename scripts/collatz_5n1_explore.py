"""
探索1: 5n+1 コラッツ変種の基本調査

T(n) = n/2     (n が偶数)
T(n) = 5n+1    (n が奇数)

問: 全ての正整数 n は最終的に 1 に到達するか？
"""

def collatz_5n1_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 5 * n + 1

def collatz_5n1_trajectory(n, max_steps=10000):
    """軌道を返す"""
    traj = [n]
    visited = {n}
    for _ in range(max_steps):
        n = collatz_5n1_step(n)
        traj.append(n)
        if n == 1:
            return traj, "reaches_1"
        if n in visited:
            # サイクル検出
            cycle_start = traj.index(n)
            cycle = traj[cycle_start:]
            return traj, f"cycle_len={len(cycle)-1}_at={n}"
        visited.add(n)
    return traj, "unknown"

def main():
    print("=== 5n+1 コラッツ変種の基本調査 ===\n")

    # 小さい値の挙動
    print("--- 小さい値の軌道 ---")
    for n in range(1, 51):
        traj, status = collatz_5n1_trajectory(n, max_steps=1000)
        if status == "reaches_1":
            print(f"  n={n}: {len(traj)-1}ステップで1に到達")
        else:
            print(f"  n={n}: {status}, 最大値={max(traj[:min(100,len(traj))])}")

    print("\n--- サイクルの詳細調査 ---")
    cycles_found = set()
    for n in range(1, 1001):
        traj, status = collatz_5n1_trajectory(n, max_steps=10000)
        if "cycle" in status:
            cycle_start_idx = -1
            last = traj[-1]
            for i, v in enumerate(traj[:-1]):
                if v == last:
                    cycle_start_idx = i
                    break
            if cycle_start_idx >= 0:
                cycle = tuple(sorted(traj[cycle_start_idx:-1]))
                if cycle not in cycles_found:
                    cycles_found.add(cycle)
                    cycle_vals = traj[cycle_start_idx:-1]
                    print(f"  新サイクル発見 (n={n}): 長さ={len(cycle_vals)}, "
                          f"min={min(cycle_vals)}, max={max(cycle_vals)}")
                    if len(cycle_vals) <= 20:
                        print(f"    サイクル: {cycle_vals}")

    print(f"\n  発見されたサイクル数: {len(cycles_found)}")

    # 1に到達する数の統計
    print("\n--- 1に到達する数の統計 ---")
    reaches_1 = 0
    diverges = 0
    cycles = 0
    for n in range(1, 10001):
        _, status = collatz_5n1_trajectory(n, max_steps=10000)
        if status == "reaches_1":
            reaches_1 += 1
        elif "cycle" in status:
            cycles += 1
        else:
            diverges += 1

    print(f"  n=1..10000:")
    print(f"    1に到達: {reaches_1}")
    print(f"    サイクル: {cycles}")
    print(f"    不明(発散?): {diverges}")

if __name__ == "__main__":
    main()
