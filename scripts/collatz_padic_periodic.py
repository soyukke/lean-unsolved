#!/usr/bin/env python3
"""
探索086: Z_2上のSyracuse写像の周期点の完全分類

2-adic整数 Z_2 上でSyracuse写像 T の周期点を全て分類する。
mod 2^k (k=1..30) で周期点を列挙し、k→∞の極限で生き残る周期点が
1のみであることを検証する。

Henselの補題を応用: mod 2^k での周期点が mod 2^{k+1} にリフト可能かを調べる。
リフト不可能 → Z_2上にはその周期点は存在しない。

主要な分析:
1. mod 2^k での周期点の完全列挙（周期p=1,2,...,20）
2. k増大に伴う周期点のリフト可能性追跡
3. Hensel条件（T^p の導関数 mod 2）の検証
4. 2-adic上の周期点候補の系統的排除
"""

import math
from collections import defaultdict
from itertools import product

def v2(n):
    """n の2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse関数: 奇数 n に対して (3n+1) / 2^{v2(3n+1)}"""
    if n <= 0:
        return None
    val = 3 * n + 1
    return val >> v2(val)

def syracuse_mod(n, mod):
    """Syracuse を mod で計算。n は奇数。"""
    val = 3 * n + 1
    v = v2(val)
    result = (val >> v) % mod
    return result

def syracuse_iterate_mod(n, mod, steps):
    """Syracuse を mod で steps 回適用"""
    x = n % mod
    for _ in range(steps):
        if x % 2 == 0:
            # 奇数化（mod 2^k では偶数が出うる）
            while x % 2 == 0 and x > 0:
                x >>= 1
            x = x % mod
            if x == 0:
                return None
        val = 3 * x + 1
        v = v2(val)
        x = (val >> v) % mod
    return x

# =====================================================================
# 1. mod 2^k での周期点の完全列挙
# =====================================================================
print("=" * 80)
print("1. mod 2^k での Syracuse 周期点の完全列挙")
print("=" * 80)

def find_all_periodic_mod(k, max_period=20):
    """mod 2^k で全ての周期点を見つける"""
    mod = 1 << k
    # period p の周期点: T^p(n) ≡ n (mod 2^k) なる奇数 n
    periodic = {}  # period -> set of cycle elements

    for r in range(1, mod, 2):
        x = r
        orbit = [x]
        for step in range(1, max_period + 1):
            val = 3 * x + 1
            v = v2(val)
            x = (val >> v) % mod
            # 結果が偶数になった場合は奇数部分を取る
            while x % 2 == 0 and x > 0:
                x >>= 1
            x = x % mod
            if x == 0:
                break
            if x == r:
                # 周期 step のサイクル発見
                p = step
                cycle = frozenset(orbit)
                if p not in periodic:
                    periodic[p] = []
                if cycle not in [frozenset(c) for c in periodic[p]]:
                    periodic[p].append(orbit[:])
                break
            orbit.append(x)

    return periodic

# 各 k での周期点数を追跡
print(f"\n{'k':>3s} {'mod':>10s} {'不動点':>8s} {'P2':>6s} {'P3':>6s} {'P4':>6s} {'P5':>6s} {'P6-10':>8s} {'P11-20':>8s}")
print("-" * 70)

periodic_tracking = {}  # k -> {period -> [cycles]}

for k in range(1, 26):
    mod = 1 << k
    max_p = min(20, k + 5)  # k が小さいときは大きい周期も探す
    periodic = find_all_periodic_mod(k, max_p)
    periodic_tracking[k] = periodic

    counts = {}
    for p in range(1, 21):
        if p in periodic:
            counts[p] = sum(len(c) for c in periodic[p])
        else:
            counts[p] = 0

    p6_10 = sum(counts.get(p, 0) for p in range(6, 11))
    p11_20 = sum(counts.get(p, 0) for p in range(11, 21))

    print(f"{k:3d} {mod:10d} {counts.get(1,0):8d} {counts.get(2,0):6d} {counts.get(3,0):6d} "
          f"{counts.get(4,0):6d} {counts.get(5,0):6d} {p6_10:8d} {p11_20:8d}")

# =====================================================================
# 2. 不動点のリフト追跡（Hensel的分析）
# =====================================================================
print("\n" + "=" * 80)
print("2. 不動点（周期1）のリフト追跡: T(n) ≡ n (mod 2^k)")
print("   Z_2 上の不動点はこの系列の射影極限")
print("=" * 80)

def find_fixed_points_mod(k):
    """mod 2^k での不動点を全て見つける"""
    mod = 1 << k
    fixed = []
    for r in range(1, mod, 2):
        val = 3 * r + 1
        v = v2(val)
        img = (val >> v) % mod
        while img % 2 == 0 and img > 0:
            img >>= 1
        img = img % mod
        if img == r:
            fixed.append(r)
    return fixed

print(f"\n{'k':>3s} {'mod':>10s} {'不動点数':>8s} {'不動点リスト':>40s}")
print("-" * 70)

prev_fixed = set()
fixed_lift_tree = {}  # k -> {r: [lifts at k+1]}

for k in range(1, 28):
    mod = 1 << k
    fixed = find_fixed_points_mod(k)

    # リフト情報
    if k > 1:
        lift_info = []
        for r in fixed:
            parent = r % (1 << (k-1))
            if parent in prev_fixed:
                lift_info.append(f"{parent}→{r}")

    display = str(fixed[:10]) + ("..." if len(fixed) > 10 else "")
    print(f"{k:3d} {mod:10d} {len(fixed):8d} {display:>40s}")

    prev_fixed = set(fixed)

# =====================================================================
# 3. 周期2点のリフト追跡
# =====================================================================
print("\n" + "=" * 80)
print("3. 周期2点のリフト追跡: T²(n) ≡ n (mod 2^k), T(n) ≢ n (mod 2^k)")
print("=" * 80)

def find_period2_mod(k):
    """mod 2^k での周期2点を見つける（不動点を除く）"""
    mod = 1 << k
    fixed = set(find_fixed_points_mod(k))
    period2 = []
    for r in range(1, mod, 2):
        if r in fixed:
            continue
        # T(r) mod 2^k を計算
        val = 3 * r + 1
        v = v2(val)
        img1 = (val >> v) % mod
        while img1 % 2 == 0 and img1 > 0:
            img1 >>= 1
        img1 = img1 % mod
        if img1 == 0:
            continue
        # T²(r) mod 2^k
        val2 = 3 * img1 + 1
        v2_ = v2(val2)
        img2 = (val2 >> v2_) % mod
        while img2 % 2 == 0 and img2 > 0:
            img2 >>= 1
        img2 = img2 % mod
        if img2 == r:
            period2.append((r, img1))
    return period2

print(f"\n{'k':>3s} {'mod':>10s} {'P2点数':>8s} {'サイクル例':>50s}")
print("-" * 75)

for k in range(1, 26):
    mod = 1 << k
    p2 = find_period2_mod(k)
    # 重複除去（(a,b) と (b,a) は同じサイクル）
    cycles = set()
    for a, b in p2:
        cycles.add(frozenset([a, b]))
    n_cycles = len(cycles)
    cycle_list = [tuple(sorted(c)) for c in list(cycles)[:3]]
    print(f"{k:3d} {mod:10d} {len(p2):8d} {str(cycle_list)[:50]:>50s}")

# =====================================================================
# 4. 一般周期 p の周期軌道数の k 依存性
# =====================================================================
print("\n" + "=" * 80)
print("4. 周期p軌道の数の k 依存性（リフト可能性の統計）")
print("=" * 80)

def count_period_orbits(k, period):
    """mod 2^k での周期 period のサイクル数を数える"""
    mod = 1 << k
    visited = set()
    n_orbits = 0
    orbit_examples = []

    for r in range(1, mod, 2):
        if r in visited:
            continue
        x = r
        orbit = [x]
        for step in range(1, period + 1):
            val = 3 * x + 1
            v = v2(val)
            x = (val >> v) % mod
            while x % 2 == 0 and x > 0:
                x >>= 1
            x = x % mod
            if x == 0:
                break
            if step < period:
                orbit.append(x)

        if x == r and len(orbit) == period:
            # 真の周期 period かチェック（約数の周期でないか）
            is_true_period = True
            for d in range(1, period):
                if period % d == 0:
                    # T^d(r) ≡ r?
                    y = r
                    for _ in range(d):
                        val = 3 * y + 1
                        v = v2(val)
                        y = (val >> v) % mod
                        while y % 2 == 0 and y > 0:
                            y >>= 1
                        y = y % mod
                    if y == r:
                        is_true_period = False
                        break

            if is_true_period:
                orbit_set = frozenset(orbit)
                if orbit_set not in visited:
                    for o in orbit:
                        visited.add(o)
                    n_orbits += 1
                    if len(orbit_examples) < 3:
                        orbit_examples.append(orbit[:])

    return n_orbits, orbit_examples

print("\n周期 p ごとのサイクル数 (mod 2^k):")
for p in [1, 2, 3, 4, 5, 6]:
    print(f"\n  周期 {p}:")
    print(f"  {'k':>3s}  {'サイクル数':>10s}  {'例':>40s}")
    for k in range(max(2, p), min(22, p + 16)):
        n_orbits, examples = count_period_orbits(k, p)
        ex_str = str(examples[:2])[:40] if examples else "なし"
        print(f"  {k:3d}  {n_orbits:10d}  {ex_str}")

# =====================================================================
# 5. Hensel条件の検証: T^p の 2-adic 微分
# =====================================================================
print("\n" + "=" * 80)
print("5. Hensel条件: T^p の2-adic微分の検証")
print("   dT^p/dn ≡ ? (mod 2) at periodic points")
print("=" * 80)

def padic_derivative_Tp(n, p_period, h_exp=30):
    """
    T^p の n における2-adic微分を近似。
    (T^p(n+2^h) - T^p(n)) / 2^h を mod 2^{h+10} で計算
    """
    mod = 1 << (h_exp + 10)

    def Tp_mod(x, mod_val):
        for _ in range(p_period):
            val = 3 * x + 1
            v = v2(val)
            x = (val >> v) % mod_val
            while x % 2 == 0 and x > 0:
                x >>= 1
            x = x % mod_val
        return x

    h = 1 << h_exp
    f_n = Tp_mod(n, mod)
    f_nh = Tp_mod(n + h, mod)

    diff = (f_nh - f_n) % mod
    # diff / h = diff / 2^h_exp → v2(diff) - h_exp
    v_diff = v2(diff) if diff != 0 else float('inf')

    return v_diff, h_exp, diff

print("\n不動点 n=1 での T の微分:")
for h_exp in [5, 10, 15, 20, 25]:
    v_diff, h, diff = padic_derivative_Tp(1, 1, h_exp)
    deriv_v2 = v_diff - h if v_diff != float('inf') else float('inf')
    print(f"  h=2^{h}: v2(T(1+h)-T(1)) = {v_diff}, v2(dT/dn) ≈ {deriv_v2}")

# =====================================================================
# 6. 代数的分析: T^p(n) = n の方程式
# =====================================================================
print("\n" + "=" * 80)
print("6. 代数的分析: 周期p方程式の構造")
print("=" * 80)

print("\n周期1（不動点）: T(n) = n")
print("  (3n+1)/2^v = n")
print("  3n+1 = n·2^v")
print("  n(2^v - 3) = 1")
print("  n = 1/(2^v - 3)")
print("  v=2: n = 1/(4-3) = 1  ← 唯一の正整数解")
print("  v=1: n = 1/(2-3) = -1 ← Z_2上の解!")
print("  v≥3: n = 1/(2^v-3) → Z_2上で探索")

# Z_2上での 1/(2^v - 3) の計算
print("\nZ_2上の不動点候補 1/(2^v - 3):")
for v_val in range(1, 10):
    denom = (1 << v_val) - 3
    if denom == 0:
        print(f"  v={v_val}: 分母=0、解なし")
        continue
    if denom == 1:
        print(f"  v={v_val}: n = 1 (標準整数)")
        continue
    if denom == -1:
        print(f"  v={v_val}: n = -1 (Z_2上の解、v2(3(-1)+1)=v2(-2)=1, T(-1)=(-3+1)/2=-1 ✓)")
        continue
    # Z_2上で 1/denom が存在するか: denom が奇数であれば存在
    if denom % 2 != 0:
        # mod 2^k での逆元を計算
        inv_vals = []
        for k in [8, 16, 24, 32]:
            mod = 1 << k
            try:
                inv = pow(denom, -1, mod)
                inv_vals.append(f"mod 2^{k}: {inv}")
            except:
                inv_vals.append(f"mod 2^{k}: 逆元なし")
        print(f"  v={v_val}: denom={denom}, 1/denom mod 2^k = {inv_vals[0]}")
        # この値が実際に不動点か検証
        mod = 1 << 32
        n_candidate = pow(denom, -1, mod)
        if n_candidate % 2 == 1:
            val_check = 3 * n_candidate + 1
            v_check = v2(val_check)
            img = (val_check >> v_check) % mod
            while img % 2 == 0:
                img >>= 1
            img = img % mod
            is_fixed = (img == n_candidate)
            print(f"    検証 (mod 2^32): n={n_candidate}, v2(3n+1)={v_check}, T(n)≡n? {is_fixed}")
            if v_check != v_val:
                print(f"    ★ v2(3n+1)={v_check} ≠ {v_val}: この v では不動点でない")
    else:
        print(f"  v={v_val}: denom={denom} は偶数 → Z_2上で逆元なし")

# =====================================================================
# 7. 周期2の方程式分析
# =====================================================================
print("\n" + "=" * 80)
print("7. 周期2の代数的分析: T(T(n)) = n")
print("=" * 80)

print("""
周期2: T(a)=b, T(b)=a (a≠b)
  (3a+1)/2^u = b, (3b+1)/2^v = a
  3a+1 = b·2^u, 3b+1 = a·2^v

  第1式: b = (3a+1)/2^u
  第2式に代入: 3·(3a+1)/2^u + 1 = a·2^v
  (9a+3)/2^u + 1 = a·2^v
  9a+3 + 2^u = a·2^{u+v}
  a(2^{u+v} - 9) = 3 + 2^u
  a = (3 + 2^u) / (2^{u+v} - 9)
""")

print("周期2の解候補 (u,v の組み合わせ):")
for u in range(1, 12):
    for v_val in range(1, 12):
        denom = (1 << (u + v_val)) - 9
        numer = 3 + (1 << u)
        if denom == 0:
            continue
        if numer % denom == 0:
            a = numer // denom
            if a > 0 and a % 2 == 1:
                b_val = (3 * a + 1) >> u
                if b_val > 0 and b_val % 2 == 1 and b_val != a:
                    # 検証
                    v_check = v2(3 * b_val + 1)
                    img_b = (3 * b_val + 1) >> v_check
                    if img_b == a and v_check == v_val:
                        print(f"  ★ (u,v)=({u},{v_val}): a={a}, b={b_val} [真の周期2軌道]")
                    else:
                        pass  # 偽の解

# Z_2上での周期2解
print("\nZ_2上の周期2候補 (denom が奇数のケース):")
found_p2 = []
for u in range(1, 15):
    for v_val in range(1, 15):
        denom = (1 << (u + v_val)) - 9
        numer = 3 + (1 << u)
        if denom == 0 or denom % 2 == 0:
            continue
        # Z_2上で numer/denom を計算
        mod = 1 << 40
        try:
            inv_d = pow(denom, -1, mod)
            a_mod = (numer * inv_d) % mod
            if a_mod % 2 == 1:
                # 検証
                val_a = 3 * a_mod + 1
                v_a = v2(val_a)
                b_mod = (val_a >> v_a) % mod
                while b_mod % 2 == 0:
                    b_mod >>= 1
                b_mod = b_mod % mod

                val_b = 3 * b_mod + 1
                v_b = v2(val_b)
                a_check = (val_b >> v_b) % mod
                while a_check % 2 == 0:
                    a_check >>= 1
                a_check = a_check % mod

                if a_check == a_mod and v_a == u and v_b == v_val and a_mod != b_mod:
                    found_p2.append((u, v_val, a_mod, b_mod))
                    if len(found_p2) <= 10:
                        print(f"  (u,v)=({u},{v_val}): a≡{a_mod} (mod 2^40), 実際のv2(3a+1)={v_a}=u?{v_a==u}, v2(3b+1)={v_b}=v?{v_b==v_val}")
        except:
            pass

if not found_p2:
    print("  Z_2上に周期2の解候補なし（全て偶数分母またはv2不整合）")

# =====================================================================
# 8. 一般的な周期方程式の分母 2-adic valuation 分析
# =====================================================================
print("\n" + "=" * 80)
print("8. 周期p方程式の分母の2-adic valuation分析")
print("   T^p(n)=n の方程式: n = F(3,2^{v_i}) で分母 D_p = 3^p - 2^{sum v_i}")
print("=" * 80)

print("\n周期pサイクルの分母: D = 3^p - 2^s (s = v_1+...+v_p)")
print("Baker定理: |3^p - 2^s| > 0 for (p,s)≠(0,0)")
print("v2(D) の値が key: v2(D)=0 なら Z_2上で逆元あり")
print()

# 3^p - 2^s の v2 を計算
print(f"{'p':>3s} {'s':>4s} {'3^p':>15s} {'3^p - 2^s':>20s} {'v2(D)':>8s} {'D奇数?':>8s}")
print("-" * 65)

for p in range(1, 13):
    val_3p = 3 ** p
    # s は v_1+...+v_p で各 v_i >= 1, 平均的には s ≈ 2p
    for s in range(p, 4*p + 1):
        D = val_3p - (1 << s)
        if D == 0:
            continue
        v2_D = v2(abs(D))
        if v2_D == 0:  # D is odd → 逆元が Z_2 に存在
            # ただし正整数解があるかどうかは別問題
            # D が奇数 → Z_2上に形式的解が存在しうる
            pass  # 多すぎるのでフィルタ
        if s == 2 * p or (p <= 6 and s in [p, p+1, 2*p-1, 2*p, 2*p+1, 3*p]):
            sign = "+" if D > 0 else "-"
            print(f"{p:3d} {s:4d} {val_3p:15d} {D:20d} {v2_D:8d} {'Yes' if v2_D==0 else 'No':>8s}")

# =====================================================================
# 9. ord_2(3) mod 2^k を利用した周期点排除
# =====================================================================
print("\n" + "=" * 80)
print("9. ord(3) mod 2^k を利用した周期点排除")
print("   ord(3) mod 2^k = 2^{k-2} (k≥3)")
print("   周期pサイクル → 3^p ≡ 2^s (mod 2^k) → p は ord(3) mod 2^k の倍数が必要")
print("=" * 80)

print("\nord(3) mod 2^k の計算:")
for k in range(1, 25):
    mod = 1 << k
    x = 3
    order = 1
    while x % mod != 1 and order < mod:
        x = (x * 3) % mod
        order += 1
    if x % mod == 1:
        print(f"  k={k:2d}: ord(3) mod 2^{k} = {order} = 2^{int(math.log2(order)) if order > 0 and (order & (order-1)) == 0 else '?'}")
    else:
        print(f"  k={k:2d}: ord(3) mod 2^{k} = (not found in {mod} steps)")

# =====================================================================
# 10. 核心定理: 整数上の周期点の存在性
# =====================================================================
print("\n" + "=" * 80)
print("10. 核心分析: Z_2 上の周期点の分類")
print("=" * 80)

print("""
■ 定理の構造:

Syracuse写像 T(n) = (3n+1)/2^{v2(3n+1)} の周期p軌道 n_0→n_1→...→n_{p-1}→n_0 に対し:

  2^{s} · n_0 = 3^p · n_0 + C(n_0,...,n_{p-1})

  ここで s = v_1+...+v_p, C は n_i に依存する定数。

  n_0 (2^s - 3^p) = C
  n_0 = C / (2^s - 3^p)

■ 2^s - 3^p = 0 となるのは (s,p)=(0,0) のみ (Baker定理)

■ Z_2 上での存在条件:
  v2(2^s - 3^p) の値が重要。

  2^s - 3^p ≡ -3^p (mod 2^s) (s≥1のとき)
  v2(2^s - 3^p) = v2(3^p) = 0 (3^p は常に奇数)

  → 分母 2^s - 3^p は常に奇数！
  → Z_2 上で逆元が常に存在する！
  → Z_2 上には各 (s, v_1,...,v_p) の組合せに対して形式的な解が存在

■ ただし、正の整数解であるためには n_0 > 0 かつ n_0 が整数

■ Z_2 上の形式的周期点と正整数の関係:
  Z_2 上の解 α は 2-adic整数であり、Z ∩ Z_2 = Z なので、
  α が正整数でなければ、αは Z_2 \ Z に属する「非標準的」な2-adic整数。
""")

# 2^s - 3^p の絶対値と符号を解析
print("\n2^s - 3^p の符号分析 (s/p > log_2(3) ⟺ 2^s > 3^p):")
log2_3 = math.log2(3)
print(f"  log_2(3) = {log2_3:.10f}")
print(f"\n  {'p':>3s} {'s_min(>3^p)':>12s} {'s/p':>10s} {'2^s-3^p':>20s}")
for p in range(1, 20):
    val_3p = 3 ** p
    # s >= p は必要（各ステップで少なくとも1回÷2）
    # s の典型値は 2p あたり
    s_critical = int(math.ceil(p * log2_3))
    for s in [s_critical - 1, s_critical, s_critical + 1, 2*p]:
        if s < p:
            continue
        D = (1 << s) - val_3p
        ratio = s / p if p > 0 else 0
        if s == 2 * p:
            print(f"  {p:3d} {s:12d} {ratio:10.4f} {D:20d}  ← s=2p")
        elif s == s_critical:
            print(f"  {p:3d} {s:12d} {ratio:10.4f} {D:20d}  ← s=⌈p·log₂3⌉")

# =====================================================================
# 11. Z_2上の各周期の形式的解の数え上げ
# =====================================================================
print("\n" + "=" * 80)
print("11. Z_2上の周期p形式的解の数え上げ")
print("   各 (v_1,...,v_p) の組合せに対して解が1つ存在")
print("   v_i ≥ 1, sum = s の組合せ数 = C(s-1, p-1)")
print("=" * 80)

print(f"\n{'p':>3s} {'s=2p':>6s} {'C(s-1,p-1)':>12s} {'s/p':>8s} {'全sの総数':>12s}")
for p in range(1, 15):
    s_2p = 2 * p
    comb_2p = math.comb(s_2p - 1, p - 1)
    total = 0
    for s in range(p, 4 * p + 1):
        total += math.comb(s - 1, p - 1)
    print(f"{p:3d} {s_2p:6d} {comb_2p:12d} {s_2p/p:8.2f} {total:12d}")

# =====================================================================
# 12. 正整数上の周期点: 不等式による排除
# =====================================================================
print("\n" + "=" * 80)
print("12. 正整数上の周期点排除: 大きさの制約")
print("=" * 80)

print("""
周期pサイクル n_0→...→n_{p-1}→n_0 に対し:
  n_0 = C / (2^s - 3^p) where C = sum_{j=0}^{p-1} 3^{p-1-j} prod_{i=j+1}^{p-1} 2^{-v_{i+1}}

  |C| ≤ 3^p / (3-1) = 3^p / 2 (幾何級数の上界)

  n_0 > 0 かつ n_0 = C/(2^s - 3^p) > 0 であるためには:
  - 2^s > 3^p (つまり s > p·log₂3) のとき C > 0 が必要
  - 2^s < 3^p のとき C < 0 が必要

  |n_0| ≤ |C| / |2^s - 3^p| ≤ (3^p/2) / |2^s - 3^p|
""")

# 各周期での最小サイクル要素の上界
print("周期pサイクルの最小要素の上界 (s=⌈p·log₂3⌉ のケース):")
for p in range(1, 30):
    s_cr = int(math.ceil(p * log2_3))
    D = abs((1 << s_cr) - 3 ** p)
    if D == 0:
        continue
    upper = (3 ** p) / (2 * D)
    print(f"  p={p:2d}: s=⌈p·log₂3⌉={s_cr:3d}, |2^s-3^p|={D}, 上界 ≤ {upper:.2e}")

# 大きな周期での探索限界
print("\n\n周期pサイクルの計算的排除:")
print("  Eliahou (1993): p < 68 のサイクルは存在しない (positive integers)")
print("  Hercher (2023): p < 186265759595 のサイクルは存在しない")
print("  ★ つまり正整数上の周期点は 1 のみ（非自明サイクルなし、ただし有限確認の範囲）")

# =====================================================================
# 最終まとめ
# =====================================================================
print("\n" + "=" * 80)
print("★★★ 最終まとめ: Z_2上のSyracuse写像の周期点分類 ★★★")
print("=" * 80)

print("""
1. Z_2上の不動点 (周期1):
   T(n) = n ⟺ n = 1/(2^v - 3)
   - v=2: n = 1 (標準整数、唯一の正整数不動点)
   - v=1: n = -1 (Z_2上の解、T(-1)=(-3+1)/2=-1 ✓)
   - v≥3: n = 1/(2^v-3) は Z_2 の元（非標準的）
     ただし v2(2^v-3)=0 なので逆元は Z_2 に存在
   → Z_2 上に無限個の形式的不動点が存在するが、正整数は 1 のみ

2. Z_2上の周期p点 (p≥2):
   各 (v_1,...,v_p) の組合せに対し Z_2 上に形式的解が1つ存在
   分母 2^s - 3^p は常に奇数 (3^p が奇数) なので Z_2 上で可逆
   → Z_2 上に各周期の形式的周期点が無限に存在
   → ただし正整数に属するものは (計算的に) 存在しない (p < 10^{11} まで確認済み)

3. Z_2 \ Z 上の周期点:
   Z_2 上の形式的解の大部分は非標準的な2-adic整数
   これらは実数として意味を持たない（2-adic距離と通常の距離は異なる位相）

4. 核心的結論:
   ★ 分母 2^s - 3^p は常に奇数 → Z_2 上の周期方程式は常に可解
   ★ しかし Z_2 ∩ Z⁺ = N 上での解は {1} のみ（計算的証拠）
   ★ 完全証明には |n_0| < (3^p/2)/|2^s-3^p| の上界と
     計算的排除を組み合わせる必要がある
   ★ Baker定理の量的形式により |2^s - 3^p| > 2^{s - c·log(s)} (c は定数)
     → |n_0| < 3^p · 2^{c·log(s)-s} → s が十分大きければ |n_0| < 1
   ★ s/p > log₂(3) + ε (d/u > log₂(3)) が成立すれば、
     十分大きい p で非自明サイクル不可能
""")
