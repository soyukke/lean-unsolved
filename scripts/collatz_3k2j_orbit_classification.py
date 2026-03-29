"""
3^k * 2^j - 1 型数の軌道パターン完全分類

目標:
- n = 3^k * 2^j - 1 (k=0..5, j=1..20) の Syracuse 軌道を計算
- k=0 は Waterfall (2^j - 1): 既知の公式 T^i(2^j-1) = 3^i * 2^{j-i} - 1
- k>=1 で新しいパターンを発見する
- 特に k=1 (n=3*2^j-1) は Waterfall の帰着値

出力:
1. 各(k,j)に対する軌道長、最大値、1到達ステップ
2. 連続上昇回数のパターン
3. k>=1 での閉じた公式の発見
"""

import json
from collections import defaultdict

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1) / 2^{v2(3n+1)}"""
    if n == 0:
        return 0
    m = 3 * n + 1
    return m >> v2(m)

def full_orbit(n, max_steps=10000):
    """軌道を1に到達するまで計算"""
    orbit = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        orbit.append(current)
    return orbit

def consecutive_ascents(n):
    """連続上昇回数"""
    count = 0
    current = n
    while True:
        nxt = syracuse(current)
        if nxt > current:
            count += 1
            current = nxt
        else:
            break
    return count

def orbit_signature(n, depth=10):
    """最初のdepthステップの上昇/下降パターン"""
    sig = []
    current = n
    for _ in range(depth):
        if current == 1:
            break
        nxt = syracuse(current)
        sig.append('U' if nxt > current else 'D')
        current = nxt
    return ''.join(sig)

# ============================================================
# Part 1: 基本統計の計算
# ============================================================
print("=" * 80)
print("Part 1: n = 3^k * 2^j - 1 の基本統計")
print("=" * 80)

results = {}
for k in range(6):  # k = 0..5
    results[k] = {}
    for j in range(1, 21):  # j = 1..20
        n = 3**k * 2**j - 1
        if n < 1:
            continue
        orb = full_orbit(n)
        asc = consecutive_ascents(n)
        steps_to_1 = len(orb) - 1 if orb[-1] == 1 else -1
        max_val = max(orb)

        results[k][j] = {
            'n': n,
            'steps_to_1': steps_to_1,
            'max_val': max_val,
            'consecutive_ascents': asc,
            'mod4': n % 4,
            'mod8': n % 8,
            'orbit_sig': orbit_signature(n, 15),
            'first_few': orb[:min(10, len(orb))],
        }

# 表形式で出力
for k in range(6):
    print(f"\n--- k = {k} (n = {3**k} * 2^j - 1) ---")
    print(f"{'j':>3} {'n':>12} {'steps':>6} {'asc':>4} {'mod4':>4} {'mod8':>4} {'signature':<16} {'first_steps'}")
    for j in range(1, 21):
        r = results[k][j]
        first = ' -> '.join(str(x) for x in r['first_few'][:6])
        print(f"{j:3d} {r['n']:12d} {r['steps_to_1']:6d} {r['consecutive_ascents']:4d} "
              f"{r['mod4']:4d} {r['mod8']:4d} {r['orbit_sig']:<16} {first}")

# ============================================================
# Part 2: k=0 (Waterfall) の公式検証
# ============================================================
print("\n" + "=" * 80)
print("Part 2: k=0 (Waterfall) T^i(2^j - 1) = 3^i * 2^{j-i} - 1 の検証")
print("=" * 80)

for j in range(2, 16):
    n = 2**j - 1
    print(f"\nj={j}: n=2^{j}-1={n}")
    current = n
    for i in range(j):
        expected = 3**i * 2**(j-i) - 1
        actual = current
        match = "OK" if actual == expected else "FAIL"
        # Waterfall 帰着値 (i=j-1)
        tag = " <-- LANDING" if i == j-1 else ""
        print(f"  T^{i}={actual:10d}, formula={expected:10d} [{match}]{tag}")
        if i < j-1:
            current = syracuse(current)

# ============================================================
# Part 3: k=1 (n = 3*2^j - 1) Waterfall帰着値の軌道パターン
# ============================================================
print("\n" + "=" * 80)
print("Part 3: k=1 (Waterfall帰着値 3*2^j - 1) の詳細分析")
print("=" * 80)

print("\n--- k=1 の軌道開始パターン ---")
print("注: 3*2^j - 1 = 2*3^1*2^{j-1} - 1 は Waterfall公式の landing value")
print("    waterfall_landing_mod4: 2*3^{m-1}-1 === 1 (mod 4)")

for j in range(1, 21):
    n = 3 * 2**j - 1
    v2_3n1 = v2(3*n+1)
    t_n = syracuse(n)
    mod4 = n % 4
    # 最初のステップの公式
    # T(3*2^j - 1) = ?
    # 3n+1 = 3*(3*2^j - 1) + 1 = 9*2^j - 2 = 2*(9*2^{j-1} - 1)
    expected_3n1 = 9 * 2**j - 2
    actual_3n1 = 3*n + 1
    assert actual_3n1 == expected_3n1

    print(f"j={j:2d}: n={n:10d}, mod4={mod4}, v2(3n+1)={v2_3n1:2d}, "
          f"T(n)={t_n:10d}")

# ============================================================
# Part 4: k=1 の T(3*2^j-1) の閉じた公式探索
# ============================================================
print("\n" + "=" * 80)
print("Part 4: T(3*2^j - 1) の公式探索")
print("=" * 80)

print("\n3*2^j - 1 mod 4 のパターン:")
for j in range(1, 21):
    n = 3 * 2**j - 1
    mod4 = n % 4
    print(f"  j={j:2d}: n={n:10d}, mod4={mod4}, "
          f"{'ASCEND (mod4=3)' if mod4 == 3 else 'DESCEND (mod4=1)'}")

print("\n分析:")
print("j=1: n=5,  mod4=1 -> 下降. T(5) = (16)/v2(16) = 1. v2(16)=4")
print("j>=2: n=3*2^j-1")
print("  j偶数: 3*2^j = 3*(4^{j/2}) = 3*4^{j/2}, mod4の分析:")

for j in range(1, 25):
    n = 3 * 2**j - 1
    mod4 = n % 4
    v2_val = v2(3*n + 1)
    t = syracuse(n)

    # 3n+1 = 9*2^j - 2 の v2 分析
    val_9_2j_m2 = 9 * 2**j - 2
    v2_direct = v2(val_9_2j_m2)

    # 9*2^j - 2 = 2*(9*2^{j-1} - 1) when j>=1
    inner = 9 * 2**(j-1) - 1
    inner_mod2 = inner % 2

    # v2(9*2^j - 2) = 1 + v2(9*2^{j-1} - 1)
    # 9*2^{j-1} - 1 の偶奇は?
    # j=1: 9-1=8 -> 偶数, v2=3 -> total v2 = 1+3=4
    # j=2: 18-1=17 -> 奇数, v2=0 -> total v2 = 1
    # j=3: 36-1=35 -> 奇数, v2=0 -> total v2 = 1
    # j=4: 72-1=71 -> 奇数, v2=0 -> total v2 = 1
    # ...
    # j>=2 のとき 9*2^{j-1} は偶数なので 9*2^{j-1}-1 は奇数 -> v2=0
    # よって j>=2 では v2(3n+1) = 1

    # j=1 の特殊性: 9*2^0 = 9 -> 9-1 = 8 = 2^3

    if j <= 6:
        print(f"  j={j:2d}: 9*2^{j}-2={val_9_2j_m2}, v2={v2_direct}, "
              f"inner=9*2^{j-1}-1={inner}(mod2={inner_mod2}), T(n)={t}")

print("\n公式:")
print("j=1: v2(3n+1) = 4, T(3*2-1) = T(5) = 16/16 = 1")
print("j>=2: v2(3n+1) = 1, T(3*2^j-1) = (9*2^j-2)/2 = 9*2^{j-1}-1")

print("\n検証: T(3*2^j - 1) = 9*2^{j-1} - 1 for j>=2")
for j in range(2, 21):
    n = 3 * 2**j - 1
    t = syracuse(n)
    expected = 9 * 2**(j-1) - 1
    match = "OK" if t == expected else "FAIL"
    print(f"  j={j:2d}: T({n:10d}) = {t:10d}, 9*2^{j-1}-1 = {expected:10d} [{match}]")

# ============================================================
# Part 5: k=1 の2ステップ目 T^2(3*2^j - 1) の公式
# ============================================================
print("\n" + "=" * 80)
print("Part 5: T^2(3*2^j - 1) の公式 (j>=2)")
print("=" * 80)

print("\nT(3*2^j-1) = 9*2^{j-1}-1 (j>=2)")
print("次: T(9*2^{j-1}-1) = ?")
print("\n9*2^{j-1}-1 mod 4 のパターン:")

for j in range(2, 21):
    n1 = 9 * 2**(j-1) - 1  # = T(3*2^j - 1)
    mod4 = n1 % 4
    v2_val = v2(3*n1 + 1)
    t2 = syracuse(n1)
    print(f"  j={j:2d}: 9*2^{j-1}-1={n1:10d}, mod4={mod4}, v2(3n+1)={v2_val}, T={t2:10d}")

# 一般パターン: 9*2^{j-1} - 1
# j=2: 9*2-1=17, mod4=1 -> 下降
# j=3: 9*4-1=35, mod4=3 -> 上昇
# j>=3 and j-1>=2: 9*2^{j-1}は4の倍数, mod4=3 -> 上昇, v2=1
# T(9*2^{j-1}-1) = (27*2^{j-1}-2)/2 = 27*2^{j-2}-1 (j>=3)

print("\n検証: T(9*2^{j-1}-1) = 27*2^{j-2}-1 for j>=3")
for j in range(3, 21):
    n1 = 9 * 2**(j-1) - 1
    t = syracuse(n1)
    expected = 27 * 2**(j-2) - 1
    match = "OK" if t == expected else "FAIL"
    print(f"  j={j:2d}: T({n1:10d}) = {t:10d}, 27*2^{j-2}-1 = {expected:10d} [{match}]")

# ============================================================
# Part 6: 一般化 T^i(3^k * 2^j - 1) のパターン
# ============================================================
print("\n" + "=" * 80)
print("Part 6: 一般帰納公式 T(3^k * 2^j - 1) の分析")
print("=" * 80)

print("\n仮説: a が奇数, j >= 2 のとき T(a*2^j - 1) = 3a*2^{j-1} - 1")
print("(これは waterfall_step と同じ)")

# k=1: T^i(3*2^j - 1)
# i=0: 3*2^j - 1 = 3^1 * 2^j - 1
# i=1: T(3*2^j - 1) = 9*2^{j-1} - 1 = 3^2 * 2^{j-1} - 1  (j>=2)
# i=2: T(9*2^{j-1}-1) = 27*2^{j-2} - 1 = 3^3 * 2^{j-2} - 1  (j>=3)
# ...
# i=s: T^s(3*2^j - 1) = 3^{s+1} * 2^{j-s} - 1  (j-s >= 2, つまり s <= j-2)

print("\n仮説: T^s(3*2^j - 1) = 3^{s+1} * 2^{j-s} - 1  for s <= j-2")

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

print("\n検証:")
for j in range(2, 16):
    n = 3 * 2**j - 1
    for s in range(0, j-1):
        actual = syracuse_iter(s, n)
        expected = 3**(s+1) * 2**(j-s) - 1
        match = "OK" if actual == expected else "FAIL"
        if match == "FAIL" or s <= 3:
            print(f"  j={j}, s={s}: T^{s}(3*2^{j}-1) = {actual}, 3^{s+1}*2^{j-s}-1 = {expected} [{match}]")

# ============================================================
# Part 7: 一般 k>=2 のパターン
# ============================================================
print("\n" + "=" * 80)
print("Part 7: k >= 2 のパターン T^s(3^k * 2^j - 1)")
print("=" * 80)

print("\n仮説: T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1  for s <= j-2")
print("(waterfall_step の繰り返し適用)")

all_ok = True
fail_count = 0
for k in range(0, 6):
    for j in range(2, 16):
        n = 3**k * 2**j - 1
        for s in range(0, min(j-1, 10)):
            actual = syracuse_iter(s, n)
            expected = 3**(k+s) * 2**(j-s) - 1
            if actual != expected:
                all_ok = False
                fail_count += 1
                print(f"  FAIL: k={k}, j={j}, s={s}: T^{s}={actual}, expected={expected}")

if all_ok:
    print("  全テスト成功!")
else:
    print(f"  失敗数: {fail_count}")

print("\n定理: T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1  (s <= j-2)")
print("条件: j-s >= 2 (つまり 2^{j-s} >= 4 なので mod4=3 が保証)")

# ============================================================
# Part 8: s = j-1 での特殊ケース（Waterfallの着地点）
# ============================================================
print("\n" + "=" * 80)
print("Part 8: s = j-1 での着地点 T^{j-1}(3^k * 2^j - 1)")
print("=" * 80)

print("\ns = j-1 のとき: T^{j-1}(3^k * 2^j - 1) = 3^{k+j-1} * 2^1 - 1 = 2*3^{k+j-1} - 1")
print("これは mod4 === 1 (waterfall_landing_mod4 の一般化)")
print("つまり着地後は必ず下降する")

for k in range(0, 6):
    print(f"\n  k={k}:")
    for j in range(2, 12):
        n = 3**k * 2**j - 1
        landing = syracuse_iter(j-1, n)
        expected_landing = 2 * 3**(k+j-1) - 1
        mod4 = landing % 4
        next_val = syracuse(landing)
        descends = next_val < landing
        print(f"    j={j:2d}: landing = T^{j-1}({n}) = {landing:12d}, "
              f"2*3^{k+j-1}-1 = {expected_landing:12d}, "
              f"mod4={mod4}, {'DESCEND' if descends else 'ASCEND'}")

# ============================================================
# Part 9: 着地後の軌道 T^{j}(3^k * 2^j - 1) = T(2*3^{k+j-1} - 1)
# ============================================================
print("\n" + "=" * 80)
print("Part 9: 着地後の1ステップ T(2*3^m - 1) where m = k+j-1")
print("=" * 80)

print("\nn = 2*3^m - 1, mod4 = 1")
print("3n+1 = 6*3^m - 2 = 2*(3^{m+1} - 1)")
print("v2(3n+1) = 1 + v2(3^{m+1} - 1)")
print("v2(3^p - 1): p奇数 -> 1, p偶数 -> 2 + v2(p)")

for m in range(1, 20):
    n = 2 * 3**m - 1
    v2_val = v2(3*n + 1)
    t_n = syracuse(n)
    # 3^{m+1} - 1 の v2
    p = m + 1
    v2_3p_m1 = v2(3**p - 1)

    # 公式: v2(3^p - 1) = 1 if p odd, 2+v2(p) if p even
    if p % 2 == 1:
        expected_v2_inner = 1
    else:
        expected_v2_inner = 2 + v2(p)

    total_v2 = 1 + expected_v2_inner

    # T(n) = (3n+1) / 2^{v2(3n+1)} = 2*(3^{m+1}-1) / 2^{total_v2}
    #       = (3^{m+1}-1) / 2^{total_v2 - 1}
    expected_t = (3**(m+1) - 1) // 2**(total_v2 - 1)

    match = "OK" if t_n == expected_t else "FAIL"
    print(f"  m={m:2d}: n={n:12d}, v2(3n+1)={v2_val:2d}, T(n)={t_n:12d}, "
          f"v2(3^{p}-1)={v2_3p_m1}, expected_v2={expected_v2_inner}, "
          f"expected_T={expected_t:12d} [{match}]")

# ============================================================
# Part 10: 着地後の軌道の分岐パターン
# ============================================================
print("\n" + "=" * 80)
print("Part 10: T(2*3^m - 1) のパターン分類")
print("=" * 80)

print("\nm+1 が奇数 (m偶数): v2(3^{m+1}-1) = 1, v2(3n+1) = 2")
print("  T(2*3^m-1) = (3^{m+1}-1)/2")
print("m+1 が偶数 (m奇数): v2(3^{m+1}-1) = 2+v2(m+1), v2(3n+1) = 3+v2(m+1)")
print("  T(2*3^m-1) = (3^{m+1}-1) / 2^{2+v2(m+1)}")

for m in range(1, 16):
    n = 2 * 3**m - 1
    t = syracuse(n)
    p = m + 1
    if m % 2 == 0:
        # m even, p = m+1 odd
        expected = (3**p - 1) // 2
        parity = "m even"
    else:
        # m odd, p = m+1 even
        v2_p = v2(p)
        expected = (3**p - 1) // 2**(2 + v2_p)
        parity = f"m odd, v2(m+1)={v2_p}"

    match = "OK" if t == expected else "FAIL"
    ratio = t / n if n > 0 else 0
    print(f"  m={m:2d} ({parity:20s}): T(2*3^{m}-1) = {t:12d}, ratio={ratio:.4f} [{match}]")

# ============================================================
# Part 11: 全体の連続上昇回数パターン
# ============================================================
print("\n" + "=" * 80)
print("Part 11: 3^k * 2^j - 1 の連続上昇回数 == j-1 の検証")
print("=" * 80)

print("\n仮説: 3^k * 2^j - 1 は常に j-1 回連続上昇する (j>=2)")
print("(waterfallフェーズで j-1 回上昇, j-1回目の着地で mod4=1 → 下降)")

for k in range(0, 6):
    print(f"\n  k={k}:")
    for j in range(1, 21):
        n = 3**k * 2**j - 1
        asc = consecutive_ascents(n)
        expected = j - 1 if j >= 2 else 0
        match = "OK" if asc == expected else "MISMATCH"
        if match == "MISMATCH" or j <= 5:
            print(f"    j={j:2d}: n={n:10d}, ascents={asc}, expected={expected} [{match}]")

# ============================================================
# Part 12: j=1 の特殊ケース分析
# ============================================================
print("\n" + "=" * 80)
print("Part 12: j=1 の特殊ケース (n = 3^k * 2 - 1 = 2*3^k - 1)")
print("=" * 80)

for k in range(0, 10):
    n = 2 * 3**k - 1
    mod4 = n % 4
    asc = consecutive_ascents(n)
    orb = full_orbit(n, 100)
    steps = len(orb) - 1
    print(f"  k={k}: n={n:8d}, mod4={mod4}, ascents={asc}, "
          f"steps_to_1={steps}, orbit_start={orb[:8]}")

# ============================================================
# Part 13: 着地後の完全軌道追跡
# ============================================================
print("\n" + "=" * 80)
print("Part 13: 着地後の完全分析 - T^{j+r}(3^k * 2^j - 1) for r=0,1,2,3")
print("=" * 80)

print("\n着地点: T^{j-1}(3^k*2^j-1) = 2*3^{k+j-1}-1")
print("着地後1歩: T(2*3^m-1) の値 (m = k+j-1)")

# 着地後のパターンテーブル
landing_patterns = defaultdict(list)

for k in range(0, 4):
    for j in range(2, 15):
        n = 3**k * 2**j - 1
        m = k + j - 1  # 着地インデックス
        landing = syracuse_iter(j-1, n)
        assert landing == 2 * 3**m - 1, f"Landing mismatch: k={k},j={j}"

        # 着地後3ステップ
        post = [landing]
        current = landing
        for _ in range(5):
            current = syracuse(current)
            post.append(current)

        # 着地後の連続下降数
        desc_count = 0
        current = landing
        while True:
            nxt = syracuse(current)
            if nxt < current:
                desc_count += 1
                current = nxt
            else:
                break

        # v2(3^{m+1} - 1) による分類
        p = m + 1
        if p % 2 == 1:
            category = "p_odd"
        else:
            category = f"p_even_v2={v2(p)}"

        if j <= 8:
            print(f"  k={k}, j={j}: m={m}, cat={category:12s}, "
                  f"descent_run={desc_count}, "
                  f"post_landing: {' -> '.join(str(x) for x in post[:4])}")

        landing_patterns[category].append((k, j, m, desc_count))

print("\n--- カテゴリ別統計 ---")
for cat, entries in sorted(landing_patterns.items()):
    desc_counts = [e[3] for e in entries]
    avg_desc = sum(desc_counts) / len(desc_counts) if desc_counts else 0
    print(f"  {cat:16s}: count={len(entries):3d}, avg_descent_run={avg_desc:.1f}, "
          f"desc_counts={sorted(set(desc_counts))}")

# ============================================================
# Part 14: 比率分析 T^{j-1}(n) / n
# ============================================================
print("\n" + "=" * 80)
print("Part 14: Landing ratio = T^{j-1}(3^k*2^j-1) / (3^k*2^j-1)")
print("=" * 80)

import math

print("\n理論値: (2*3^{k+j-1}-1) / (3^k*2^j-1)")
print("大きな j で: ~ 2*3^{k+j-1} / (3^k*2^j) = 2*(3/2)^{j-1} * 3^{k-1}/3^k ")
print("= (2/3) * (3/2)^{j-1} -> exponentially growing for j>>1")

for k in [0, 1, 2]:
    print(f"\n  k={k}:")
    for j in range(2, 21):
        n = 3**k * 2**j - 1
        landing = 2 * 3**(k+j-1) - 1
        ratio = landing / n
        log_ratio = math.log2(ratio)
        theoretical = (3/2)**(j-1) * 2 / 3  # approximate
        print(f"    j={j:2d}: ratio={ratio:.6f}, log2(ratio)={log_ratio:.4f}, "
              f"(3/2)^{j-1}={(3/2)**(j-1):.4f}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
[定理1] 一般化Waterfall公式:
  T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1  for 0 <= s <= j-2

  証明: waterfall_step の繰り返し適用
  各ステップで a = 3^{k+s} (奇数), 指数 = j-s >= 2 なので
  T(3^{k+s} * 2^{j-s} - 1) = 3 * 3^{k+s} * 2^{j-s-1} - 1
                             = 3^{k+s+1} * 2^{j-(s+1)} - 1

[定理2] 連続上昇回数:
  3^k * 2^j - 1 は正確に j-1 回連続上昇する (j >= 2)

  証明: [定理1]より s=0,...,j-2 で
  T^{s+1} = 3^{k+s+1} * 2^{j-s-1} - 1 > 3^{k+s} * 2^{j-s} - 1 = T^s
  (∵ 3^{k+s+1} * 2^{j-s-1} = (3/2) * 3^{k+s} * 2^{j-s} > 3^{k+s} * 2^{j-s})

  s=j-1 で: T^{j-1} = 2*3^{k+j-1} - 1, mod4=1 → 下降

[定理3] 着地値:
  T^{j-1}(3^k * 2^j - 1) = 2 * 3^{k+j-1} - 1
  mod 4 === 1 (必ず下降)

[定理4] 着地後の分岐:
  T(2*3^m - 1) = (3^{m+1} - 1) / 2^{v2(3^{m+1}-1)}
  where v2(3^{m+1}-1) = 1 if m+1 odd, 2+v2(m+1) if m+1 even

[定理5] k=1 特殊公式:
  T(3*2^j - 1) = 9*2^{j-1} - 1  for j >= 2
  T(3*2   - 1) = T(5) = 1  (j=1の特殊ケース)

[新発見] 3^k*2^j-1 型は k に関係なく、j-1 回の waterfall を経て
  2*3^{k+j-1}-1 型に帰着する。これは k=0 の Waterfall の自然な一般化。
  kの効果は着地値の「高さ」を 3^k 倍にするだけ。
""")
