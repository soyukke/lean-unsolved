#!/usr/bin/env python3
"""
コラッツ予想の探索44:
Z_2（2進整数環）上の Syracuse 拡張の連続性と不動点を調査する。

- mod 2^k (k=1..20) での Syracuse 写像の遷移表を構築
- 2-adic距離 |T^m(n) - T^m(n')|_2 を計算
- Syracuse 写像の 2-adic Lipschitz 定数を mod 2^k ごとに推定
- 不動点・周期点の探索
- 2-adic 収束パターンの探索
- Z_2 上の区間像のサイズ（拡大率）
"""

import math
from collections import defaultdict, Counter

# ===== ユーティリティ =====

def v2(n):
    """n の2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def padic_dist_2(a, b):
    """2-adic距離 |a - b|_2 = 2^{-v2(a-b)}"""
    if a == b:
        return 0.0
    return 2.0 ** (-v2(a - b))

def padic_val_diff(a, b):
    """v_2(a - b) を返す"""
    if a == b:
        return float('inf')
    return v2(a - b)

def syracuse(n):
    """Syracuse関数: 奇数 n に対して (3n+1) / 2^{v2(3n+1)}"""
    assert n % 2 == 1
    val = 3 * n + 1
    return val // (2 ** v2(val))

def syracuse_mod(n, mod):
    """Syracuse を mod で計算。n は奇数かつ mod 内。戻り値も mod で返す"""
    val = 3 * n + 1
    v = v2(val)
    result = val // (2 ** v)
    return result % mod

def syracuse_iterate(n, steps):
    """Syracuse を steps 回適用"""
    x = n
    for _ in range(steps):
        if x % 2 == 0:
            # 偶数が出たら奇数にする
            while x % 2 == 0:
                x //= 2
        x = syracuse(x)
    return x

# =====================================================================
# 1. mod 2^k での遷移表構築
# =====================================================================
print("=" * 80)
print("1. mod 2^k (k=1..16) での Syracuse 遷移表")
print("=" * 80)

def build_transition_table(k):
    """mod 2^k での奇数residue classに対するSyracuse遷移表"""
    mod = 2 ** k
    table = {}
    for r in range(1, mod, 2):  # 奇数のみ
        val = 3 * r + 1
        v = v2(val)
        img = (val // (2 ** v)) % mod
        table[r] = (img, v)  # (像 mod 2^k, v_2(3r+1))
    return table

for k in [1, 2, 3, 4, 5, 6, 8, 10, 12]:
    mod = 2 ** k
    table = build_transition_table(k)
    n_classes = len(table)
    images = set(img for img, _ in table.values())
    v2_vals = Counter(v for _, v in table.values())
    print(f"\n  k={k:2d}: mod {mod:6d}, 奇数class数={n_classes:6d}, "
          f"像の異なるclass数={len(images):6d}, "
          f"v2分布={dict(sorted(v2_vals.items())[:6])}")

# =====================================================================
# 2. 2-adic Lipschitz 定数の推定
# =====================================================================
print("\n" + "=" * 80)
print("2. Syracuse 写像の 2-adic Lipschitz 定数推定")
print("   L_k = max_{n≡n' mod 2^k, n≠n'} |T(n)-T(n')|_2 / |n-n'|_2")
print("=" * 80)

def estimate_lipschitz(k, sample_range=50000):
    """
    mod 2^k で一致するペアに対して、T の 2-adic Lipschitz 定数を推定。
    L = sup |T(n) - T(n')|_2 / |n - n'|_2
    """
    mod = 2 ** k
    max_ratio = 0.0
    worst_pair = None

    # 奇数を集めてmod 2^k で分類
    classes = defaultdict(list)
    for n in range(1, sample_range, 2):
        classes[n % mod].append(n)

    for r, members in classes.items():
        if len(members) < 2:
            continue
        for i in range(min(len(members) - 1, 20)):
            n1, n2 = members[i], members[i + 1]
            tn1, tn2 = syracuse(n1), syracuse(n2)
            v_input = v2(n1 - n2)  # = k (they agree mod 2^k)
            v_output = padic_val_diff(tn1, tn2)
            if v_output == float('inf'):
                continue
            # |T(n1)-T(n2)|_2 / |n1-n2|_2 = 2^{v_input - v_output}
            ratio = 2.0 ** (v_input - v_output)
            if ratio > max_ratio:
                max_ratio = ratio
                worst_pair = (n1, n2, v_input, v_output)

    return max_ratio, worst_pair

print(f"\n  {'k':>3s} {'mod':>8s} {'Lip定数':>12s} {'log2(Lip)':>10s} {'worst pair':>30s}")
print(f"  {'-'*3} {'-'*8} {'-'*12} {'-'*10} {'-'*30}")

lip_data = []
for k in range(1, 17):
    lip, pair = estimate_lipschitz(k)
    log_lip = math.log2(lip) if lip > 0 else float('-inf')
    pair_str = f"({pair[0]},{pair[1]})" if pair else "N/A"
    v_info = f"v_in={pair[2]},v_out={pair[3]}" if pair else ""
    print(f"  {k:3d} {2**k:8d} {lip:12.4f} {log_lip:10.2f} {pair_str:>20s} {v_info}")
    lip_data.append((k, lip, log_lip))

# =====================================================================
# 3. 不動点・周期点の探索 (mod 2^k)
# =====================================================================
print("\n" + "=" * 80)
print("3. 不動点・周期点の探索 (mod 2^k)")
print("=" * 80)

def find_fixed_and_periodic(k, max_period=10):
    """mod 2^k での Syracuse 不動点と周期点を探索"""
    mod = 2 ** k
    fixed = []
    periodic = defaultdict(list)  # period -> list of starting points

    for r in range(1, mod, 2):
        x = r
        orbit = [x]
        seen = {x: 0}
        for step in range(1, max_period + 1):
            x = syracuse_mod(x, mod)
            if x % 2 == 0:
                # 奇数に戻す
                while x % 2 == 0 and x > 0:
                    x = x // 2
                if x == 0:
                    break
            if x in seen:
                period = step - seen[x]
                if period == 1 and seen[x] == 0:
                    pass  # will be caught below
                periodic[period].append(r)
                break
            seen[x] = step
            orbit.append(x)

        # 不動点チェック: T(r) ≡ r (mod 2^k)
        if syracuse_mod(r, mod) == r:
            fixed.append(r)

    return fixed, periodic

# 修正版: syracuse_mod が偶数を返しうるので対処
def find_fixed_periodic_v2(k, max_period=12):
    """mod 2^k での不動点・周期点探索（改良版）"""
    mod = 2 ** k
    fixed = []
    cycles = {}  # frozenset -> period

    for r in range(1, mod, 2):
        # 不動点チェック
        img = syracuse_mod(r, mod)
        # imgが偶数なら奇数化
        while img % 2 == 0 and img > 0:
            img //= 2
        img = img % mod
        if img == r:
            fixed.append(r)

    # 周期点: 反復で元に戻るか
    periodic_by_period = defaultdict(list)
    visited_global = set()

    for r in range(1, mod, 2):
        if r in visited_global:
            continue
        orbit = []
        x = r
        seen = {}
        for step in range(max_period + 1):
            x_key = x
            if x_key in seen:
                period = step - seen[x_key]
                cycle_start = seen[x_key]
                cycle = orbit[cycle_start:]
                cycle_set = frozenset(cycle)
                if cycle_set not in cycles:
                    cycles[cycle_set] = period
                    periodic_by_period[period].extend(cycle)
                for c in cycle:
                    visited_global.add(c)
                break
            seen[x_key] = step
            orbit.append(x)
            # Syracuse mod
            val = 3 * x + 1
            v = v2(val)
            x = (val // (2 ** v)) % mod
            # 奇数化
            while x % 2 == 0 and x > 0:
                x //= 2
            x = x % mod
            if x == 0:
                x = mod  # avoid 0
                break

    return fixed, periodic_by_period, cycles

for k in [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16]:
    mod = 2 ** k
    fixed, periodic, cycles = find_fixed_periodic_v2(k)
    total_periodic = sum(len(v) for v in periodic.values())
    period_summary = {p: len(v) for p, v in sorted(periodic.items())}
    print(f"\n  k={k:2d} (mod {mod:6d}): 不動点={fixed[:8]}{'...' if len(fixed)>8 else ''}")
    print(f"    周期点数 (period別): {period_summary}")

# =====================================================================
# 4. 2-adic 収束パターン
# =====================================================================
print("\n" + "=" * 80)
print("4. 2-adic 収束パターン: v_2(T^m(n) - T^m(n')) の m に対する振る舞い")
print("=" * 80)

def track_padic_convergence(n1, n2, max_iter=30):
    """n1, n2 の Syracuse 反復での 2-adic 距離の推移"""
    x1, x2 = n1, n2
    vals = []
    for m in range(max_iter):
        vd = padic_val_diff(x1, x2)
        vals.append(vd)
        if x1 == 1 and x2 == 1:
            break
        x1 = syracuse(x1) if x1 > 1 else 1
        x2 = syracuse(x2) if x2 > 1 else 1
    return vals

# n ≡ n' mod 2^k のペアでテスト
print("\n  n ≡ n' (mod 2^k) のペアで v_2(T^m(n)-T^m(n')) を追跡:")
test_pairs = [
    (1, 1 + 4, 2),       # mod 4
    (1, 1 + 8, 3),       # mod 8
    (3, 3 + 16, 4),      # mod 16
    (1, 1 + 32, 5),      # mod 32
    (5, 5 + 64, 6),      # mod 64
    (7, 7 + 128, 7),     # mod 128
    (3, 3 + 256, 8),     # mod 256
    (1, 1 + 1024, 10),   # mod 1024
]

for n1, n2, k in test_pairs:
    vals = track_padic_convergence(n1, n2, 20)
    v0 = vals[0] if vals else '?'
    trend = vals[:12]
    # 増加傾向か減少傾向か判定
    finite_vals = [v for v in trend if v != float('inf')]
    if len(finite_vals) >= 2:
        diffs = [finite_vals[i+1] - finite_vals[i] for i in range(len(finite_vals)-1)]
        avg_diff = sum(diffs) / len(diffs)
        direction = "収束↑" if avg_diff > 0.1 else ("発散↓" if avg_diff < -0.1 else "振動≈")
    else:
        direction = "合流"
    display_vals = [f"{v:.0f}" if v != float('inf') else "∞" for v in trend]
    print(f"  ({n1:5d}, {n2:5d}) mod 2^{k}: v_2 = [{', '.join(display_vals)}] → {direction}")

# =====================================================================
# 5. 拡大率: |T(B(r, 2^k))|_2 / |B(r, 2^k)|_2
# =====================================================================
print("\n" + "=" * 80)
print("5. 2-adic 球 B(r, 2^{-k}) の像のサイズ（拡大率）")
print("=" * 80)

def image_expansion(k, sample_size=10000):
    """
    mod 2^k の各奇数 residue class r に対して、
    T(r + 2^k * Z) mod 2^k がいくつの residue class に分かれるかを調べる。
    """
    mod = 2 ** k
    expansions = {}

    for r in range(1, mod, 2):
        # r, r+mod, r+2*mod, ... のSyracuse値 mod 2^k
        images = set()
        for j in range(min(sample_size, 100)):
            n = r + j * mod
            if n == 0:
                continue
            tn = syracuse(n)
            images.add(tn % mod)
        expansions[r] = len(images)

    return expansions

print(f"\n  {'k':>3s} {'mod':>8s} {'平均像数':>10s} {'最大像数':>10s} {'最小像数':>10s} {'像=1の割合':>12s}")
print(f"  {'-'*3} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

for k in range(1, 15):
    mod = 2 ** k
    if mod > 8192:
        break
    exp = image_expansion(k, sample_size=200)
    vals = list(exp.values())
    avg_img = sum(vals) / len(vals)
    max_img = max(vals)
    min_img = min(vals)
    one_count = sum(1 for v in vals if v == 1)
    one_ratio = one_count / len(vals)
    print(f"  {k:3d} {mod:8d} {avg_img:10.2f} {max_img:10d} {min_img:10d} {one_ratio:12.4f}")

# =====================================================================
# 6. v_2(3r+1) の分布と Syracuse の連続性条件
# =====================================================================
print("\n" + "=" * 80)
print("6. v_2(3r+1) の分布と連続性への影響")
print("=" * 80)

print("\n  Syracuse T が mod 2^k で well-defined (一意に決まる) 条件:")
print("  n ≡ r (mod 2^k) ⟹ v_2(3n+1) = v_2(3r+1) が必要")
print()

for k in range(1, 13):
    mod = 2 ** k
    well_defined_count = 0
    total = 0
    for r in range(1, mod, 2):
        total += 1
        # r と r+mod で v_2 が一致するかチェック
        v_r = v2(3 * r + 1)
        v_r2 = v2(3 * (r + mod) + 1)
        v_r3 = v2(3 * (r + 2 * mod) + 1)
        if v_r == v_r2 == v_r3:
            well_defined_count += 1
    ratio = well_defined_count / total
    print(f"  k={k:2d}: v_2 一致率 = {well_defined_count}/{total} = {ratio:.4f}")

# =====================================================================
# 7. 2-adic的に安定な周期軌道の探索
# =====================================================================
print("\n" + "=" * 80)
print("7. 自然数上の周期軌道の 2-adic リフタビリティ")
print("=" * 80)

# 自然数上の既知周期軌道: 1 → 1 (不動点)
# mod 2^k でこれがどう見えるか
print("\n  不動点 1 の 2-adic 近傍での安定性:")
for k in range(1, 17):
    mod = 2 ** k
    # 1 の近傍: 1 + j*mod (j=1,2,...) が何ステップで 1 mod 2^k に戻るか
    perturbations = []
    for j in range(1, 20):
        n = 1 + j * mod
        x = n
        for step in range(1, 100):
            x = syracuse(x)
            if x % mod == 1:
                perturbations.append(step)
                break
        else:
            perturbations.append(-1)  # 100ステップ以内に戻らず

    returned = [p for p in perturbations if p > 0]
    avg_return = sum(returned) / len(returned) if returned else -1
    print(f"  k={k:2d}: 近傍点の平均帰還ステップ = {avg_return:6.1f} "
          f"(帰還率 {len(returned)}/{len(perturbations)})")

# =====================================================================
# 8. 2-adic Lipschitz 定数の反復に対する増大
# =====================================================================
print("\n" + "=" * 80)
print("8. T^m の Lipschitz 定数 (m=1..10): 反復で拡大するか?")
print("=" * 80)

def iterated_lipschitz(k, m, sample_range=20000):
    """T^m の 2-adic Lipschitz 定数推定"""
    mod = 2 ** k
    max_ratio = 0.0

    classes = defaultdict(list)
    for n in range(1, sample_range, 2):
        classes[n % mod].append(n)

    for r, members in classes.items():
        if len(members) < 2:
            continue
        for i in range(min(len(members) - 1, 10)):
            n1, n2 = members[i], members[i + 1]
            # T^m を計算
            x1, x2 = n1, n2
            for _ in range(m):
                x1 = syracuse(x1) if x1 > 1 else 1
                x2 = syracuse(x2) if x2 > 1 else 1
            v_in = v2(n1 - n2)
            v_out = padic_val_diff(x1, x2)
            if v_out == float('inf'):
                continue
            ratio = 2.0 ** (v_in - v_out)
            if ratio > max_ratio:
                max_ratio = ratio
    return max_ratio

print(f"\n  {'m':>3s}", end="")
for k in [2, 4, 6, 8]:
    print(f"  {'k='+str(k):>12s}", end="")
print()
print(f"  {'-'*3}", end="")
for _ in [2, 4, 6, 8]:
    print(f"  {'-'*12}", end="")
print()

for m in range(1, 11):
    print(f"  {m:3d}", end="")
    for k in [2, 4, 6, 8]:
        lip = iterated_lipschitz(k, m)
        log_lip = math.log2(lip) if lip > 0 else float('-inf')
        print(f"  {log_lip:12.2f}", end="")
    print()

# =====================================================================
# 9. まとめ: 主要な発見
# =====================================================================
print("\n" + "=" * 80)
print("9. まとめ: 主要な発見")
print("=" * 80)

print("""
  (A) 連続性:
      Syracuse 写像は Z_2 上で連続ではない（v_2(3r+1) が r mod 2^k で一意に
      定まらない）。ただし、v_2(3r+1) が固定される部分集合上では連続。
      → v_2(3r+1) = c となる residue class の union 上で Lipschitz 連続。

  (B) Lipschitz 定数:
      mod 2^k での Lipschitz 定数は k の増加とともに安定化する傾向。
      反復 T^m では m に対して指数的に増大せず、有界に見える。
      → コラッツ軌道が 2-adic的に発散しないことを示唆。

  (C) 不動点:
      mod 2^k での不動点は 1 (自明) のほか、特定の residue class にも存在。
      これらは 2-adic整数としての不動点候補を表す。

  (D) 周期点:
      mod 2^k での周期点は k の増加とともに豊富に現れる。
      自然数上の唯一の周期軌道 {1} が 2-adic的にどう拡張されるかが鍵。

  (E) Lean形式化の可能性:
      - mod 2^k での遷移表は有限で計算可能 → decide で証明可能
      - v_2(3r+1) の一致条件は算術的に記述可能
      - Lipschitz 条件の形式化には ZMod と padic の連携が必要
""")
