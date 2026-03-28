#!/usr/bin/env python3
"""
mod 1024 追加分析:
1. 遅延下降の剰余類のビットパターン解析
2. 下降ステップ数の理論的決定（代数的に決まるか確率的か）
3. r=341 (v2=10) の特殊性
4. 連続上昇回数と下降ステップの厳密な関係
5. mode steps の安定性（本当に代数的に決まるか）
"""

def syracuse(n):
    val = 3 * n + 1
    v2 = 0
    while val % 2 == 0:
        val //= 2
        v2 += 1
    return val, v2

def descent_steps(n, max_steps=200):
    original = n
    current = n
    for k in range(1, max_steps + 1):
        current, _ = syracuse(current)
        if current < original:
            return k
    return -1

def syracuse_iterate(n, steps):
    """Syracuse関数をsteps回反復し、各ステップの値を返す"""
    path = [n]
    current = n
    for _ in range(steps):
        current, _ = syracuse(current)
        path.append(current)
    return path

# ============================================================
# 分析1: mode steps は代数的に決定されるか？
# ============================================================
print("=" * 70)
print("分析1: mode steps の代数的決定性")
print("=" * 70)

# 各剰余類について、多数サンプルでステップ数の一意性を確認
from collections import Counter
MOD = 1024

deterministic_count = 0
non_deterministic = []

for r in range(1, MOD, 2):
    step_counter = Counter()
    for i in range(200):
        n = r + MOD * (2 * i + 1)
        if n % 2 == 0:
            continue
        s = descent_steps(n, max_steps=100)
        if s > 0:
            step_counter[s] += 1

    if len(step_counter) == 1:
        deterministic_count += 1
    else:
        total = sum(step_counter.values())
        dominant = step_counter.most_common(1)[0]
        non_deterministic.append((r, dict(step_counter), dominant[1] / total))

print(f"\n完全決定的（全サンプルで同一ステップ数）: {deterministic_count} / 512")
print(f"非決定的（複数ステップ数出現）: {len(non_deterministic)} / 512")

# 非決定的なもののうち、dominant ratio が低いもの
non_deterministic.sort(key=lambda x: x[2])
print(f"\n最も非決定的な剰余類 Top 20:")
for r, dist, dom_ratio in non_deterministic[:20]:
    top3 = sorted(dist.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  r={r:4d}: dominant={dom_ratio:.2%}, 分布={top3}")

# 非決定的なものの mod 構造
print(f"\n非決定的な剰余類の mod 8 分布:")
nd_mod8 = Counter(r % 8 for r, _, _ in non_deterministic)
print(f"  {dict(nd_mod8)}")

print(f"\n非決定的な剰余類の mod 32 分布:")
nd_mod32 = Counter(r % 32 for r, _, _ in non_deterministic)
for k in sorted(nd_mod32.keys()):
    print(f"  r≡{k:2d} (mod 32): {nd_mod32[k]} 個")

# ============================================================
# 分析2: 遅延下降の二進構造
# ============================================================
print("\n" + "=" * 70)
print("分析2: 遅延下降（非決定的）剰余類のビットパターン")
print("=" * 70)

# 非決定的なものの中で末尾ビットパターンを分析
print("\n末尾ビット（下位10ビット）パターン:")
for r, dist, dom_ratio in non_deterministic[:30]:
    binary = format(r, '010b')
    # 連続する1の数を数える（下位ビットから）
    trailing_ones = 0
    temp = r
    while temp % 2 == 1:
        trailing_ones += 1
        temp >>= 1
    top_step = sorted(dist.items(), key=lambda x: x[1], reverse=True)[0][0]
    print(f"  r={r:4d} (0b{binary}): trailing_1s={trailing_ones}, "
          f"mode_step={top_step}, dominant={dom_ratio:.2%}")

# ============================================================
# 分析3: r=341 (v2=10, ratio≈0.001) の特殊性
# ============================================================
print("\n" + "=" * 70)
print("分析3: r=341 の超急速下降の仕組み")
print("=" * 70)

r = 341
print(f"\nr = {r} = 0b{format(r, '010b')}")
print(f"3r+1 = {3*r+1}")
v = 3*r+1
v2 = 0
while v % 2 == 0:
    v //= 2
    v2 += 1
print(f"v2(3*341+1) = v2({3*341+1}) = {v2}")
print(f"T(341) = {3*341+1} / 2^{v2} = {(3*341+1) // (2**v2)}")
print(f"T(341)/341 = {(3*341+1) / (2**v2) / 341:.10f}")
print(f"\n341 = (2^10 - 1) / 3 (Mersenne関連)")
print(f"  2^10 - 1 = {2**10 - 1}, /3 = {(2**10-1)/3}")

# 他の (2^k-1)/3 の形
print(f"\n(2^k-1)/3 型の数のv2:")
for k in range(2, 20, 2):
    val = (2**k - 1) // 3
    if val % 2 == 1 and val > 0:
        v = 3 * val + 1
        v2_count = 0
        while v % 2 == 0:
            v //= 2
            v2_count += 1
        print(f"  k={k:2d}: (2^{k}-1)/3 = {val:8d}, v2(3n+1) = {v2_count}, "
              f"ratio = 3/{2**v2_count} = {3/2**v2_count:.10f}")

# ============================================================
# 分析4: 決定的 vs 非決定的の閾値
# ============================================================
print("\n" + "=" * 70)
print("分析4: ステップ数が決定的に決まる条件")
print("=" * 70)

# 決定的な剰余類のステップ数分布
det_steps = {}
for r in range(1, MOD, 2):
    step_counter = Counter()
    for i in range(100):
        n = r + MOD * (2 * i + 1)
        if n % 2 == 0:
            continue
        s = descent_steps(n, max_steps=100)
        if s > 0:
            step_counter[s] += 1

    if len(step_counter) == 1:
        det_steps[r] = list(step_counter.keys())[0]

det_step_dist = Counter(det_steps.values())
print(f"\n決定的剰余類のステップ数分布:")
for s in sorted(det_step_dist.keys()):
    print(f"  step={s}: {det_step_dist[s]} 個")

# 決定的ステップ数と v2(3r+1) の関係
print(f"\n決定的ステップ数と v2(3r+1) の関係:")
for step_val in sorted(det_step_dist.keys()):
    residues = [r for r, s in det_steps.items() if s == step_val]
    v2_vals = []
    for r in residues:
        v = 3 * r + 1
        v2 = 0
        while v % 2 == 0:
            v //= 2
            v2 += 1
        v2_vals.append(v2)
    v2_counter = Counter(v2_vals)
    print(f"  step={step_val}: v2分布={dict(v2_counter)}")

# ============================================================
# 分析5: 下降率の理論値
# ============================================================
print("\n" + "=" * 70)
print("分析5: 決定的剰余類の下降率の理論値パターン")
print("=" * 70)

# step=1 で決定的なもの: T(n) = (3n+1)/2^v2 < n ⟺ v2 >= 2
# 下降率 = 3/2^v2
print("\nstep=1 決定的: ratio = 3/2^v2(3r+1)")
step1_residues = [r for r, s in det_steps.items() if s == 1]
ratio_groups = {}
for r in step1_residues:
    v = 3 * r + 1
    v2 = 0
    while v % 2 == 0:
        v //= 2
        v2 += 1
    key = f"3/2^{v2}"
    if key not in ratio_groups:
        ratio_groups[key] = []
    ratio_groups[key].append(r)

for key in sorted(ratio_groups.keys()):
    count = len(ratio_groups[key])
    print(f"  {key}: {count} 個")

# step=2 の理論値
print("\nstep=2 決定的: 各剰余類の2ステップ後の値を解析")
step2_residues = [r for r, s in det_steps.items() if s == 2][:5]
for r in step2_residues:
    n = r + MOD * 3  # 代表的サンプル
    path = syracuse_iterate(n, 2)
    print(f"  r={r}: {n} → {path[1]} → {path[2]}, ratio={path[2]/n:.6f}")

# ============================================================
# 分析6: 2^5, 2^8, 2^10 での非決定的割合の推移
# ============================================================
print("\n" + "=" * 70)
print("分析6: modの増大と非決定的割合の推移")
print("=" * 70)

for exp in [3, 4, 5, 6, 7, 8, 9, 10]:
    mod_val = 1 << exp
    n_det = 0
    n_total = 0
    for r in range(1, mod_val, 2):
        step_counter = Counter()
        for i in range(100):
            n = r + mod_val * (2 * i + 1)
            if n % 2 == 0:
                continue
            s = descent_steps(n, max_steps=80)
            if s > 0:
                step_counter[s] += 1

        n_total += 1
        if len(step_counter) == 1:
            n_det += 1

    print(f"  mod 2^{exp:2d} = {mod_val:5d}: "
          f"決定的 {n_det:4d}/{n_total:4d} = {n_det/n_total:.1%}, "
          f"非決定的 {n_total-n_det:4d} ({(n_total-n_det)/n_total:.1%})")

print("\n" + "=" * 70)
print("完了")
print("=" * 70)
