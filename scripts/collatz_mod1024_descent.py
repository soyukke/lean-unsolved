#!/usr/bin/env python3
"""
mod 2^10 = 1024 での下降ステップ数の完全分類

Syracuse関数 T(n) = (3n+1)/2^v2(3n+1) を用いて、
各奇数の剰余類 r (mod 1024) について、T^k(n) < n となる最小の k を調べる。

- 全奇数剰余類(512個)について下降ステップ数を分類
- mod 2^5, 2^8 との比較
- 特殊な剰余類の同定
- 下降率の統計分析
"""

import json
from collections import defaultdict, Counter
import math

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    v2 = 0
    while val % 2 == 0:
        val //= 2
        v2 += 1
    return val, v2

def descent_steps(n, max_steps=200):
    """T^k(n) < n となる最小の k を返す。見つからなければ -1"""
    original = n
    current = n
    for k in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return k
    return -1

def descent_ratio(n, steps):
    """k ステップ後の値 / 元の値"""
    current = n
    for _ in range(steps):
        current, _ = syracuse(current)
    return current / n

def analyze_residue_class(r, mod, num_samples=50, sample_range=10**6):
    """剰余類 r (mod mod) の下降ステップ数を多数サンプルで調査"""
    steps_list = []
    ratios = []
    # r が偶数なら奇数にならないのでスキップ
    if r % 2 == 0:
        return None

    for i in range(num_samples):
        n = r + mod * (2 * i + 1)  # 奇数を確保
        if n <= 0:
            continue
        if n % 2 == 0:
            n += mod
        if n % 2 == 0:
            continue

        s = descent_steps(n)
        if s > 0:
            steps_list.append(s)
            ratio = descent_ratio(n, s)
            ratios.append(ratio)

    if not steps_list:
        return None

    return {
        'min_steps': min(steps_list),
        'max_steps': max(steps_list),
        'mean_steps': sum(steps_list) / len(steps_list),
        'mode_steps': Counter(steps_list).most_common(1)[0][0],
        'mean_ratio': sum(ratios) / len(ratios),
        'min_ratio': min(ratios),
        'max_ratio': max(ratios),
        'step_dist': dict(Counter(steps_list)),
        'n_samples': len(steps_list),
    }

def compute_theoretical_steps(r, mod):
    """剰余類 r mod mod の理論的な最小下降ステップ数を計算
    （代表元に対するSyracuse写像の反復）"""
    # 十分大きな代表元で計算
    results = []
    for mult in range(1, 201, 2):
        n = r + mod * mult
        if n % 2 == 0:
            continue
        if n <= 1:
            continue
        s = descent_steps(n, max_steps=100)
        if s > 0:
            results.append(s)
        if len(results) >= 30:
            break

    if not results:
        return None
    return min(results)


print("=" * 70)
print("mod 2^10 = 1024 での下降ステップ数の完全分類")
print("=" * 70)

# ============================================================
# Part 1: 各奇数剰余類の下降ステップ数
# ============================================================
print("\n[Part 1] 全512個の奇数剰余類の下降ステップ数")

MOD = 1024
results_1024 = {}

for r in range(1, MOD, 2):  # 奇数のみ
    info = analyze_residue_class(r, MOD, num_samples=100)
    if info:
        results_1024[r] = info

# ステップ数のモード別分類
mode_groups = defaultdict(list)
for r, info in results_1024.items():
    mode_groups[info['mode_steps']].append(r)

print(f"\n全剰余類数: {len(results_1024)}")
print(f"\nモード別ステップ数の分布:")
for steps in sorted(mode_groups.keys()):
    residues = mode_groups[steps]
    print(f"  ステップ数 {steps}: {len(residues)} 個の剰余類")
    if len(residues) <= 10:
        print(f"    剰余類: {sorted(residues)}")

# ============================================================
# Part 2: 最悪ケース（最大下降ステップ数）の剰余類
# ============================================================
print("\n" + "=" * 70)
print("[Part 2] 最大下降ステップ数 (worst case) の剰余類 Top 20")
print("=" * 70)

by_max_steps = sorted(results_1024.items(), key=lambda x: x[1]['max_steps'], reverse=True)
for r, info in by_max_steps[:20]:
    print(f"  r={r:4d} (mod 1024): max_steps={info['max_steps']:3d}, "
          f"mean_steps={info['mean_steps']:.1f}, mode={info['mode_steps']}, "
          f"mean_ratio={info['mean_ratio']:.4f}")

# ============================================================
# Part 3: 最良ケース（最小下降ステップ数・最低下降率）
# ============================================================
print("\n" + "=" * 70)
print("[Part 3] 最低下降率 (best descent) の剰余類 Top 20")
print("=" * 70)

by_ratio = sorted(results_1024.items(), key=lambda x: x[1]['mean_ratio'])
for r, info in by_ratio[:20]:
    print(f"  r={r:4d} (mod 1024): mean_ratio={info['mean_ratio']:.6f}, "
          f"mode_steps={info['mode_steps']}, mean_steps={info['mean_steps']:.1f}")

print("\n" + "=" * 70)
print("[Part 3b] 最高下降率 (worst descent = slowest) の剰余類 Top 20")
print("=" * 70)

by_ratio_worst = sorted(results_1024.items(), key=lambda x: x[1]['mean_ratio'], reverse=True)
for r, info in by_ratio_worst[:20]:
    print(f"  r={r:4d} (mod 1024): mean_ratio={info['mean_ratio']:.6f}, "
          f"mode_steps={info['mode_steps']}, mean_steps={info['mean_steps']:.1f}")

# ============================================================
# Part 4: mod 32, mod 256 との比較
# ============================================================
print("\n" + "=" * 70)
print("[Part 4] mod 32, mod 256 との精密化の比較")
print("=" * 70)

for smaller_mod in [32, 256]:
    print(f"\n--- mod {smaller_mod} → mod 1024 の精密化 ---")
    for r_small in range(1, smaller_mod, 2):
        # r_small の下位剰余類を1024内で集める
        sub_residues = [r for r in range(r_small, MOD, smaller_mod) if r % 2 == 1]
        if not sub_residues:
            continue

        ratios = [results_1024[r]['mean_ratio'] for r in sub_residues if r in results_1024]
        steps = [results_1024[r]['mean_steps'] for r in sub_residues if r in results_1024]

        if ratios:
            ratio_spread = max(ratios) - min(ratios)
            steps_spread = max(steps) - min(steps)
            if ratio_spread > 0.15:  # 大きなばらつきがあるもの
                print(f"  r≡{r_small:3d} (mod {smaller_mod}): "
                      f"ratio範囲=[{min(ratios):.4f}, {max(ratios):.4f}] "
                      f"(spread={ratio_spread:.4f}), "
                      f"steps範囲=[{min(steps):.1f}, {max(steps):.1f}]")

# ============================================================
# Part 5: 連続上昇パターン（k回連続上昇 ⟺ n ≡ 2^{k+1}-1 (mod 2^{k+1})）
# ============================================================
print("\n" + "=" * 70)
print("[Part 5] 連続上昇パターンの検証 (mod 1024)")
print("=" * 70)

for k in range(1, 10):
    target_r = (1 << (k + 1)) - 1  # 2^{k+1} - 1
    target_mod = 1 << (k + 1)

    # mod 1024 内でこの条件を満たす剰余類
    matching = [r for r in range(1, MOD, 2) if r % target_mod == target_r]

    if matching and matching[0] in results_1024:
        avg_steps = sum(results_1024[r]['mean_steps'] for r in matching if r in results_1024) / len(matching)
        avg_ratio = sum(results_1024[r]['mean_ratio'] for r in matching if r in results_1024) / len(matching)
        print(f"  k={k} 回連続上昇 (n≡{target_r} mod {target_mod}): "
              f"{len(matching)} 個, 平均steps={avg_steps:.2f}, 平均ratio={avg_ratio:.4f}")

# ============================================================
# Part 6: v2(3n+1) のパターン（mod 1024での詳細）
# ============================================================
print("\n" + "=" * 70)
print("[Part 6] v2(3n+1) の詳細パターン (mod 1024)")
print("=" * 70)

v2_by_residue = {}
for r in range(1, MOD, 2):
    val = 3 * r + 1
    v2 = 0
    while val % 2 == 0:
        val //= 2
        v2 += 1
    v2_by_residue[r] = v2

v2_dist = Counter(v2_by_residue.values())
print(f"\nv2(3r+1) の分布 (r は奇数, r < 1024):")
for v, count in sorted(v2_dist.items()):
    expected = 512 / (2 ** v) if v < 10 else 0
    print(f"  v2={v:2d}: {count:4d} 個 (理論値 ≈ {expected:.1f}, P=1/2^{v})")

# 高い v2 を持つ剰余類
print(f"\nv2(3r+1) ≥ 5 の剰余類:")
for r in sorted(v2_by_residue.keys()):
    if v2_by_residue[r] >= 5:
        info = results_1024.get(r)
        ratio_str = f", ratio={info['mean_ratio']:.4f}" if info else ""
        print(f"  r={r:4d}: v2={v2_by_residue[r]}{ratio_str}")

# ============================================================
# Part 7: 周期性パターンの探索
# ============================================================
print("\n" + "=" * 70)
print("[Part 7] 下降ステップ数の周期性パターン")
print("=" * 70)

# 各剰余類のモードステップ数を配列にして周期性を探す
mode_array = []
for r in range(1, MOD, 2):
    if r in results_1024:
        mode_array.append(results_1024[r]['mode_steps'])
    else:
        mode_array.append(0)

# 自己相関で周期を探索
print(f"\nモードステップ数列の基本統計:")
print(f"  長さ: {len(mode_array)}")
print(f"  最小: {min(mode_array)}, 最大: {max(mode_array)}")
print(f"  平均: {sum(mode_array)/len(mode_array):.2f}")
print(f"  分布: {dict(Counter(mode_array))}")

# ステップ数が特に大きい剰余類（遅延下降）の構造解析
print(f"\n遅延下降（平均ステップ数 > 5）の剰余類:")
slow_descent = [(r, info) for r, info in results_1024.items() if info['mean_steps'] > 5]
slow_descent.sort(key=lambda x: x[1]['mean_steps'], reverse=True)
for r, info in slow_descent[:30]:
    binary = format(r, '010b')
    print(f"  r={r:4d} (0b{binary}): mean_steps={info['mean_steps']:.2f}, "
          f"v2(3r+1)={v2_by_residue.get(r, '?')}, ratio={info['mean_ratio']:.4f}")

# ============================================================
# Part 8: 下降率の全体分布
# ============================================================
print("\n" + "=" * 70)
print("[Part 8] 下降率の全体分布 (ヒストグラム)")
print("=" * 70)

all_ratios = [info['mean_ratio'] for info in results_1024.values()]
bins = [(i/20, (i+1)/20) for i in range(0, 20)]
print(f"\n下降率の分布:")
for lo, hi in bins:
    count = sum(1 for r in all_ratios if lo <= r < hi)
    if count > 0:
        bar = '#' * (count // 2)
        print(f"  [{lo:.2f}, {hi:.2f}): {count:3d} {bar}")

overall_mean = sum(all_ratios) / len(all_ratios)
overall_std = (sum((r - overall_mean)**2 for r in all_ratios) / len(all_ratios)) ** 0.5
print(f"\n全体統計: 平均={overall_mean:.6f}, 標準偏差={overall_std:.6f}")
print(f"  最小={min(all_ratios):.6f}, 最大={max(all_ratios):.6f}")

# ============================================================
# Part 9: mod 2^5, 2^8, 2^10 の比較テーブル
# ============================================================
print("\n" + "=" * 70)
print("[Part 9] mod 2^5, 2^8, 2^10 のステップ数分布比較")
print("=" * 70)

for mod_exp in [5, 8, 10]:
    mod_val = 1 << mod_exp
    step_counter = Counter()
    for r in range(1, mod_val, 2):
        info = analyze_residue_class(r, mod_val, num_samples=30)
        if info:
            step_counter[info['mode_steps']] += 1

    total = sum(step_counter.values())
    print(f"\nmod 2^{mod_exp} = {mod_val}: 奇数剰余類 {total} 個")
    for s in sorted(step_counter.keys()):
        pct = step_counter[s] / total * 100
        print(f"  step={s}: {step_counter[s]:4d} ({pct:.1f}%)")

# ============================================================
# Part 10: 特殊残基の同定
# ============================================================
print("\n" + "=" * 70)
print("[Part 10] 特殊残基の同定")
print("=" * 70)

# 常にステップ1で下降する剰余類
step1_always = [r for r, info in results_1024.items()
                if info['mode_steps'] == 1 and info['max_steps'] == 1]
print(f"\n常にステップ1で下降: {len(step1_always)} 個")
if step1_always:
    # mod 8 での内訳
    mod8_dist = Counter(r % 8 for r in step1_always)
    print(f"  mod 8 分布: {dict(mod8_dist)}")

# 常にステップ2以上必要な剰余類
step2_plus = [r for r, info in results_1024.items() if info['min_steps'] >= 2]
print(f"\n常にステップ2以上必要: {len(step2_plus)} 個")
step2_plus_mod8 = Counter(r % 8 for r in step2_plus)
print(f"  mod 8 分布: {dict(step2_plus_mod8)}")

# 常にステップ3以上必要な剰余類
step3_plus = [r for r, info in results_1024.items() if info['min_steps'] >= 3]
print(f"\n常にステップ3以上必要: {len(step3_plus)} 個")
if step3_plus:
    print(f"  剰余類: {sorted(step3_plus)[:30]}{'...' if len(step3_plus) > 30 else ''}")

# 極端に小さい下降率（急速下降）
fast_descent = [(r, info) for r, info in results_1024.items() if info['mean_ratio'] < 0.1]
fast_descent.sort(key=lambda x: x[1]['mean_ratio'])
print(f"\n極端に急速な下降 (ratio < 0.1): {len(fast_descent)} 個")
for r, info in fast_descent[:10]:
    print(f"  r={r:4d}: ratio={info['mean_ratio']:.6f}, steps={info['mode_steps']}")

print("\n" + "=" * 70)
print("完了")
print("=" * 70)
