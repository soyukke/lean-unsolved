#!/usr/bin/env python3
"""
コラッツ予想 探索24: s3(n) mod 2 が Syracuse写像の不変量か調査・証明

s3(n) = n の3進桁和
T(n) = (3n+1) / 2^{v2(3n+1)}  (Syracuse写像, n は奇数)
"""

def s3(n):
    """3進桁和"""
    s = 0
    while n > 0:
        s += n % 3
        n //= 3
    return s

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v

def syracuse(n):
    """Syracuse写像 T(n) = (3n+1)/2^v2(3n+1)"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def to_base3(n):
    """3進表現を文字列で返す"""
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    return ''.join(reversed(digits))

print("=" * 70)
print("探索24: s3(n) mod 2 が Syracuse写像で保存されるか調査")
print("=" * 70)

# ============================================================
# 1. Step A: s3(3n+1) = s3(n) + 1 が常に成立するか
# ============================================================
print("\n" + "=" * 70)
print("Step A: s3(3n+1) vs s3(n) + 1 の関係")
print("=" * 70)

print("\n理論: 3n は n の3進表現の末尾に0を追加 → s3(3n) = s3(n)")
print("      3n+1 は末尾の0を1に変える → s3(3n+1) = s3(n) + 1 ... 本当？")
print()

# 反例チェック
step_a_counter = 0
step_a_fail = 0
for n in range(1, 10001):
    lhs = s3(3 * n + 1)
    rhs = s3(n) + 1
    step_a_counter += 1
    if lhs != rhs:
        step_a_fail += 1
        if step_a_fail <= 10:
            print(f"  反例: n={n}, s3(3n+1)={lhs}, s3(n)+1={rhs}, "
                  f"n₃={to_base3(n)}, (3n+1)₃={to_base3(3*n+1)}")

print(f"\nStep A 結果: {step_a_counter} 件中 {step_a_fail} 件の反例")
if step_a_fail == 0:
    print("→ s3(3n+1) = s3(n) + 1 は n=1..10000 で常に成立！")
else:
    print("→ s3(3n+1) = s3(n) + 1 は常に成立するわけではない")

# s3(3n+1) と s3(n) の差の分布
from collections import Counter
diff_a = Counter()
for n in range(1, 10001):
    d = s3(3 * n + 1) - s3(n)
    diff_a[d] += 1

print(f"\ns3(3n+1) - s3(n) の分布:")
for d in sorted(diff_a.keys()):
    print(f"  差={d}: {diff_a[d]} 件")

# mod 2 での関係
print(f"\ns3(3n+1) mod 2 vs s3(n) mod 2:")
match_count = 0
flip_count = 0
for n in range(1, 10001):
    if s3(3 * n + 1) % 2 == s3(n) % 2:
        match_count += 1
    else:
        flip_count += 1
print(f"  同じ: {match_count}, 異なる（フリップ）: {flip_count}")

# ============================================================
# 2. Step B: s3(m/2) と s3(m) の関係（m偶数）
# ============================================================
print("\n" + "=" * 70)
print("Step B: s3(m/2) vs s3(m) の関係（m偶数）")
print("=" * 70)

diff_b = Counter()
for m in range(2, 20001, 2):
    d = s3(m // 2) - s3(m)
    diff_b[d] += 1

print(f"\ns3(m/2) - s3(m) の分布 (m=2,4,...,20000):")
for d in sorted(diff_b.keys()):
    print(f"  差={d}: {diff_b[d]} 件")

# mod 2 の関係
print(f"\ns3(m/2) mod 2 vs s3(m) mod 2 (m偶数):")
same = 0
diff = 0
for m in range(2, 20001, 2):
    if s3(m // 2) % 2 == s3(m) % 2:
        same += 1
    else:
        diff += 1
print(f"  同じ: {same}, 異なる: {diff}")
print("→ s3(m/2) mod 2 は s3(m) mod 2 と一定の関係を持たない")

# ============================================================
# 3. Step C: s3(m/2^k) mod 2 の関係
# ============================================================
print("\n" + "=" * 70)
print("Step C: s3(m/2^k) mod 2 vs s3(m) mod 2 の関係")
print("=" * 70)

# m = 3n+1 (n奇数), k = v2(m) のケースを調査
print("\n奇数n に対して m=3n+1, k=v2(m), T(n)=m/2^k:")
print("s3(T(n)) mod 2 vs s3(n) mod 2 の直接比較:")

match = 0
total = 0
for n in range(1, 10001, 2):  # 奇数のみ
    tn = syracuse(n)
    if s3(tn) % 2 == s3(n) % 2:
        match += 1
    total += 1

print(f"  一致: {match}/{total} ({100*match/total:.2f}%)")

# ============================================================
# 4. 大きなnでの再検証
# ============================================================
print("\n" + "=" * 70)
print("大きなnでの再検証: n=1..200001 の奇数")
print("=" * 70)

match = 0
total = 0
counterexamples = []
for n in range(1, 200001, 2):
    tn = syracuse(n)
    if s3(tn) % 2 == s3(n) % 2:
        match += 1
    else:
        if len(counterexamples) < 20:
            counterexamples.append(n)
    total += 1

print(f"一致: {match}/{total} ({100*match/total:.4f}%)")
if counterexamples:
    print(f"反例: {counterexamples[:20]}")
    print(f"\n反例の詳細分析:")
    for n in counterexamples[:10]:
        tn = syracuse(n)
        m = 3 * n + 1
        k = v2(m)
        print(f"  n={n}: s3(n)={s3(n)} (mod2={s3(n)%2}), "
              f"T(n)={tn}: s3(T(n))={s3(tn)} (mod2={s3(tn)%2}), "
              f"v2(3n+1)={k}, "
              f"n₃={to_base3(n)}, T(n)₃={to_base3(tn)}")
else:
    print("反例なし！ 不変量として成立する可能性が高い")

# ============================================================
# 5. より精密な分析: なぜ保存されるのか
# ============================================================
print("\n" + "=" * 70)
print("精密分析: s3(3n+1) - s3(n) と v2(3n+1) の関係")
print("=" * 70)

print("\n理論:")
print("  s3(T(n)) = s3((3n+1)/2^k) where k = v2(3n+1)")
print("  保存条件: s3(T(n)) ≡ s3(n) (mod 2)")
print("  つまり s3((3n+1)/2^k) ≡ s3(n) (mod 2)")
print()

# s3(3n+1) - s3(n) の分析（n奇数のみ）
print("n奇数のとき s3(3n+1) - s3(n) の分布:")
diff_odd = Counter()
for n in range(1, 20001, 2):
    d = s3(3 * n + 1) - s3(n)
    diff_odd[d] += 1
for d in sorted(diff_odd.keys()):
    print(f"  差={d}: {diff_odd[d]} 件")

# 核心: s3(m) と s3(m/2) の差を3進の繰り上がり/繰り下がりで分析
print("\n" + "=" * 70)
print("核心分析: s3(m) - s3(m/2) のメカニズム（m偶数）")
print("=" * 70)

print("\n例を見る:")
for m in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]:
    q = m // 2
    print(f"  m={m:3d} ({to_base3(m):>8s}₃), m/2={q:3d} ({to_base3(q):>8s}₃), "
          f"s3(m)={s3(m)}, s3(m/2)={s3(q)}, 差={s3(q)-s3(m)}")

# ============================================================
# 6. 3進での 2による除算のルール
# ============================================================
print("\n" + "=" * 70)
print("3進での 2による除算のルール")
print("=" * 70)

print("\n2^{-1} ≡ 2 (mod 3)")
print("m/2 を3進で計算するとき、3進の各桁で「2倍して余り」の逆演算")
print()

# m が偶数のとき m/2 の3進桁和の変化
# m の3進最下位桁による場合分け
print("m の3進最下位桁と s3(m/2) - s3(m) の関係:")
for last_digit in [0, 1, 2]:
    diffs = Counter()
    for m in range(2, 20001, 2):
        if m % 3 == last_digit:
            d = s3(m // 2) - s3(m)
            diffs[d] += 1
    print(f"\n  m ≡ {last_digit} (mod 3):")
    for d in sorted(diffs.keys()):
        print(f"    差={d}: {diffs[d]} 件")

# ============================================================
# 7. 別アプローチ: 直接 T(n) の3進桁和を追跡
# ============================================================
print("\n" + "=" * 70)
print("直接追跡: n → 3n+1 → /2 を繰り返す際の s3 の変化")
print("=" * 70)

print("\nn奇数に対して、3n+1 の後 2で割る各ステップでの s3 mod 2 の変化:")
for n in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]:
    m = 3 * n + 1
    k = v2(m)
    chain = [m]
    val = m
    for _ in range(k):
        val //= 2
        chain.append(val)
    s3_chain = [s3(x) for x in chain]
    s3_mod2_chain = [s3(x) % 2 for x in chain]
    print(f"  n={n:3d} (s3={s3(n)},mod2={s3(n)%2}): "
          f"3n+1={m} → /2 chain: {chain}")
    print(f"       s3 chain: {s3_chain}, mod2 chain: {s3_mod2_chain}, v2={k}")

# ============================================================
# 8. /2 のときの s3 mod 2 の変化パターン
# ============================================================
print("\n" + "=" * 70)
print("/2 のときの s3 mod 2 の変化: フリップするかしないか")
print("=" * 70)

flip_by_mod9 = {}
for m in range(2, 100001, 2):
    mod9 = m % 9
    flipped = (s3(m // 2) % 2) != (s3(m) % 2)
    if mod9 not in flip_by_mod9:
        flip_by_mod9[mod9] = [0, 0]  # [not_flipped, flipped]
    flip_by_mod9[mod9][int(flipped)] += 1

print("\nm mod 9 別の s3 フリップ率:")
for mod9 in sorted(flip_by_mod9.keys()):
    nf, f = flip_by_mod9[mod9]
    total = nf + f
    print(f"  m ≡ {mod9} (mod 9): フリップ {f}/{total} ({100*f/total:.1f}%)")

# ============================================================
# 9. 完全な追跡: s3(3n+1) mod 2 = s3(n) + 1 mod 2、
#    そして /2 を v2 回行った後の s3 mod 2
# ============================================================
print("\n" + "=" * 70)
print("完全追跡: 3n+1 で +1、各 /2 でのフリップ回数")
print("=" * 70)

# /2 を k 回行うとき、s3 mod 2 は何回フリップするか？
# 保存条件: フリップ回数が奇数（3n+1 での +1 を打ち消す）
flip_count_dist = Counter()
for n in range(1, 100001, 2):
    m = 3 * n + 1
    k = v2(m)
    flips = 0
    val = m
    for _ in range(k):
        old_mod2 = s3(val) % 2
        val //= 2
        new_mod2 = s3(val) % 2
        if old_mod2 != new_mod2:
            flips += 1
    flip_count_dist[(k, flips)] += 1

print(f"\n(v2, フリップ回数) の分布:")
for key in sorted(flip_count_dist.keys()):
    k, flips = key
    count = flip_count_dist[key]
    parity = "偶数" if flips % 2 == 0 else "奇数"
    # 保存条件: s3(n)+1 (3n+1による) から flips 回フリップ
    # s3(T(n)) ≡ s3(n) + 1 + flips (mod 2)  ← フリップ1回で mod2 が変わる
    # 保存には 1 + flips ≡ 0 (mod 2) → flips が奇数
    preserves = "保存" if flips % 2 == 1 else "非保存"
    print(f"  v2={k}, flips={flips}: {count:6d} 件 (フリップ{parity}) → {preserves}")

# 保存率
preserve_count = sum(v for (k, f), v in flip_count_dist.items() if f % 2 == 1)
total_count = sum(flip_count_dist.values())
print(f"\n保存: {preserve_count}/{total_count} ({100*preserve_count/total_count:.4f}%)")

# ============================================================
# 10. フリップ回数が常に奇数である理由
# ============================================================
print("\n" + "=" * 70)
print("分析: なぜフリップ回数は常に奇数か？")
print("=" * 70)

print("\n仮説: m=3n+1 が偶数のとき、m/2^k (k=v2(m)) まで割る過程で")
print("s3 mod 2 のフリップは常に奇数回起こる")
print()

# m=3n+1 の特殊構造を利用
# 3n+1 ≡ 1 (mod 3) when n ≡ 0 (mod 3)
# 3n+1 ≡ 2 (mod 3) when n ≡ 2 (mod 3)  (n odd → n ≡ 1 mod 2)
# 3n+1 ≡ 0 (mod 3) is impossible (3n+1 ≡ 1 mod 3)

print("重要: 3n+1 ≡ 1 (mod 3) は常に成立（3n ≡ 0 mod 3 なので）")
print()

# もっと直接的に: s3(m) と s3(m/2^k) の差
print("直接比較: s3(3n+1) mod 2 vs s3(T(n)) mod 2")
print("s3(3n+1) = s3(n) + 1 なので")
print("s3(3n+1) mod 2 = (s3(n) + 1) mod 2")
print("保存には s3(T(n)) mod 2 = s3(n) mod 2 が必要")
print("つまり s3(T(n)) mod 2 ≠ s3(3n+1) mod 2 が必要")
print()

# s3(m/2^k) mod 2 vs s3(m) mod 2 (m ≡ 1 mod 3, m ≡ 0 mod 2^k)
print("m ≡ 1 (mod 3) かつ m ≡ 0 (mod 2^k) のとき:")
print("s3(m/2^k) mod 2 ≠ s3(m) mod 2 が常に成立するか？")
print()

# テスト
for k in range(1, 8):
    same = 0
    diff_cnt = 0
    tested = 0
    for m in range(2**k, 100001, 2**k):
        if m % 3 == 1 and v2(m) == k:  # exactly k factors of 2
            q = m // (2**k)
            if q % 2 == 1:  # q should be odd (Syracuse output)
                tested += 1
                if s3(q) % 2 == s3(m) % 2:
                    same += 1
                else:
                    diff_cnt += 1
    if tested > 0:
        print(f"  k={k}: 同じ={same}, 異なる={diff_cnt}, 計={tested}, "
              f"異なる率={100*diff_cnt/tested:.2f}%")

# ============================================================
# 11. 3進の Kummer の定理的アプローチ
# ============================================================
print("\n" + "=" * 70)
print("Kummer的アプローチ: s_p(a+b) = s_p(a) + s_p(b) - (p-1)*carries")
print("=" * 70)

print("\n3進での加算と桁和の関係:")
print("s3(a + b) = s3(a) + s3(b) - 2 * (3進加算での繰り上がり回数)")
print()
print("s3(3n+1) = s3(3n) + s3(1) - 2 * carries(3n, 1)")
print("         = s3(n) + 1 - 2 * carries(3n, 1)")
print("3n の末尾桁は 0 なので、3n + 1 で繰り上がりは起きない")
print("→ s3(3n+1) = s3(n) + 1 ✓")

# ============================================================
# 12. Lifting the exponent lemma的アプローチ
# ============================================================
print("\n" + "=" * 70)
print("2進と3進の相互作用: s3(2^k * q) vs s3(q)")
print("=" * 70)

# s3(2^k * q) を調べる
for k in range(1, 6):
    print(f"\nk={k} (2^k={2**k}):")
    diffs = Counter()
    for q in range(1, 5001, 2):  # q odd
        d = s3(2**k * q) - s3(q)
        diffs[d % 2] += 1
    for p in sorted(diffs.keys()):
        print(f"  s3(2^{k}*q) - s3(q) mod 2 = {p}: {diffs[p]} 件")

print("\n→ s3(2^k * q) mod 2 と s3(q) mod 2 の関係は k によって異なる？")

# ============================================================
# 13. 真の不変量の正体
# ============================================================
print("\n" + "=" * 70)
print("真の不変量: s3(n) mod 2 が本当に不変か、大規模検証")
print("=" * 70)

# n=1..500000 の奇数で検証
match = 0
total = 0
first_counterexample = None
for n in range(1, 500001, 2):
    tn = syracuse(n)
    if s3(tn) % 2 == s3(n) % 2:
        match += 1
    else:
        if first_counterexample is None:
            first_counterexample = n
    total += 1

print(f"n=1..500000 の奇数: 一致 {match}/{total} ({100*match/total:.6f}%)")
if first_counterexample:
    n = first_counterexample
    tn = syracuse(n)
    m = 3 * n + 1
    k = v2(m)
    print(f"\n最初の反例: n={n}")
    print(f"  s3(n)={s3(n)} (mod2={s3(n)%2})")
    print(f"  T(n)={tn}, s3(T(n))={s3(tn)} (mod2={s3(tn)%2})")
    print(f"  3n+1={m}, v2={k}")
    print(f"  n₃ = {to_base3(n)}")
    print(f"  T(n)₃ = {to_base3(tn)}")
else:
    print("反例なし！")

# ============================================================
# 14. 反例がない場合、複数ステップでも保存されるか
# ============================================================
print("\n" + "=" * 70)
print("複数ステップでの保存: T^k(n) で s3 mod 2 が保存されるか")
print("=" * 70)

def syracuse_trajectory(n, max_steps=100):
    """Syracuse軌道を返す"""
    traj = [n]
    for _ in range(max_steps):
        if n == 1:
            break
        n = syracuse(n)
        traj.append(n)
    return traj

preserved_all_steps = 0
total_tested = 0
any_failure = False
for n in range(1, 50001, 2):
    traj = syracuse_trajectory(n, max_steps=200)
    s3_mod2_start = s3(n) % 2
    all_preserved = True
    for t in traj:
        if s3(t) % 2 != s3_mod2_start:
            all_preserved = False
            if not any_failure:
                print(f"  軌道内で初めて失敗: n={n}, 軌道中の値 t={t}")
                print(f"    s3(n)={s3(n)} mod2={s3_mod2_start}, s3(t)={s3(t)} mod2={s3(t)%2}")
                any_failure = True
            break
    if all_preserved:
        preserved_all_steps += 1
    total_tested += 1

print(f"全軌道で保存: {preserved_all_steps}/{total_tested} ({100*preserved_all_steps/total_tested:.4f}%)")

# ============================================================
# 15. s3 mod 2 の値ごとの分布
# ============================================================
print("\n" + "=" * 70)
print("s3(n) mod 2 = 0 と 1 の分布（奇数 n=1..10000）")
print("=" * 70)

count0 = sum(1 for n in range(1, 10001, 2) if s3(n) % 2 == 0)
count1 = sum(1 for n in range(1, 10001, 2) if s3(n) % 2 == 1)
print(f"  s3(n) mod 2 = 0: {count0}")
print(f"  s3(n) mod 2 = 1: {count1}")

# ============================================================
# 16. 証明のための鍵: s3(2n) mod 2 のパターン
# ============================================================
print("\n" + "=" * 70)
print("鍵の分析: s3(2n) と s3(n) の3進桁レベルの追跡")
print("=" * 70)

print("\n2倍を3進で追跡:")
print("n₃ の各桁 d に対して 2d を計算:")
print("  d=0: 2*0=0, 繰り上がり=0, 出力桁=0")
print("  d=1: 2*1=2, 繰り上がり=0, 出力桁=2")
print("  d=2: 2*2=4=1*3+1, 繰り上がり=1, 出力桁=1")
print()
print("桁和の変化: d → 出力桁 + (繰り上がりへの寄与)")
print("  d=0 → 0 (差 0)")
print("  d=1 → 2 (差 +1)")
print("  d=2 → 1 + carry (差 -1 + carry_contribution)")
print()

# 具体例
print("具体例:")
for n in range(1, 31):
    n3 = to_base3(n)
    n2_3 = to_base3(2 * n)
    print(f"  n={n:3d} ({n3:>6s}₃), 2n={2*n:3d} ({n2_3:>6s}₃), "
          f"s3(n)={s3(n)}, s3(2n)={s3(2*n)}, diff={s3(2*n)-s3(n)}")

# ============================================================
# 17. Legendre公式的アプローチ
# ============================================================
print("\n" + "=" * 70)
print("Legendre公式: s_p(n) = (n - ν_p(n!)) * (p-1)^{-1} は使えないが...")
print("代わりに: s3(n) ≡ n (mod 2) かどうか")
print("=" * 70)

# s3(n) mod 2 = n mod 2 ?
match_count = 0
for n in range(1, 10001):
    if s3(n) % 2 == n % 2:
        match_count += 1
print(f"s3(n) mod 2 = n mod 2: {match_count}/10000")

# s3(n) mod 2 = ? のパターン
print("\ns3(n) mod 2 の周期性?")
for period in [2, 3, 4, 6, 8, 9, 12, 18, 27]:
    pattern = [s3(n) % 2 for n in range(1, period + 1)]
    # Check if periodic
    is_periodic = True
    for n in range(1, 1001):
        if s3(n) % 2 != pattern[(n - 1) % period]:
            is_periodic = False
            break
    if is_periodic:
        print(f"  周期 {period}: {pattern} → 周期的！")

# ============================================================
# 18. 直接的な mod 2 の追跡
# ============================================================
print("\n" + "=" * 70)
print("直接追跡: s3(n) mod 2 の自己相似構造")
print("=" * 70)

# s3(n) = s3(n // 3) + (n % 3)
# s3(n) mod 2 = (s3(n // 3) + (n % 3)) mod 2
# = s3(n // 3) mod 2  if n % 3 == 0 or 2
# ≠ s3(n // 3) mod 2  if n % 3 == 1

print("s3(n) mod 2 は n の3進表現における桁1の個数の偶奇で決まる")
print("（桁0と桁2は偶数を足すので mod 2 に影響しない）")
print()

# 検証
def count_ones_base3(n):
    c = 0
    while n > 0:
        if n % 3 == 1:
            c += 1
        n //= 3
    return c

match_count = 0
for n in range(1, 100001):
    if s3(n) % 2 == count_ones_base3(n) % 2:
        match_count += 1
print(f"s3(n) mod 2 = (3進の桁1の個数) mod 2: {match_count}/100000")

# いや、s3(n) = Σ d_i, mod 2 では d_i mod 2 の合計
# d=0: 0 mod 2 = 0
# d=1: 1 mod 2 = 1
# d=2: 2 mod 2 = 0
# なので s3(n) mod 2 = (3進で桁が1であるものの個数) mod 2  ← これは正しい？
# いや、s3(n) = Σ d_i, s3(n) mod 2 = Σ (d_i mod 2) mod 2 = (桁1の個数) mod 2
# (桁2は mod 2 = 0 に寄与)

print("\n確認: s3(n) mod 2 = Σ(d_i mod 2) mod 2 = #{i: d_i = 1} mod 2")
print("つまり s3(n) mod 2 は n の3進表現での「1」の個数の偶奇")
print()

# ============================================================
# 19. T(n) での「1」の個数の偶奇が保存される理由
# ============================================================
print("=" * 70)
print("核心: T(n) = (3n+1)/2^v2(3n+1) で")
print("3進の「1」の個数の偶奇が保存される理由を探る")
print("=" * 70)

print("\nn の3進表現と T(n) の3進表現の比較:")
for n in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51]:
    if n % 2 == 0:
        continue
    tn = syracuse(n)
    n3 = to_base3(n)
    tn3 = to_base3(tn)
    c1_n = count_ones_base3(n)
    c1_tn = count_ones_base3(tn)
    m = 3 * n + 1
    k = v2(m)
    print(f"  n={n:3d} ({n3:>8s}₃, #1={c1_n}), T(n)={tn:5d} ({tn3:>12s}₃, #1={c1_tn}), "
          f"Δ#1={c1_tn-c1_n}, v2={k}")

# ============================================================
# 20. 最終まとめ
# ============================================================
print("\n" + "=" * 70)
print("最終まとめ")
print("=" * 70)

print("""
事実の確認:
1. s3(n) mod 2 = n の3進表現における桁1の個数の偶奇
2. s3(3n+1) = s3(n) + 1 （n に対して常に成立）
3. Syracuse T(n) = (3n+1)/2^{v2(3n+1)} に対して
   s3(T(n)) mod 2 = s3(n) mod 2 が数値的に 500000 個の奇数で確認

問題の分解:
- 3n+1 の操作: s3 を +1 する → mod 2 をフリップ
- /2^k の操作: s3 mod 2 のフリップ回数は常に奇数
  → 合計で mod 2 は偶数回フリップ = 保存

検証済み:
- /2^k でのフリップ回数は常に奇数（n=1..100000 の奇数で確認）
- ただし、なぜ常に奇数になるかの代数的証明はまだ得られていない

可能な証明方針:
- 3進での2による除算の桁和への影響を一桁ずつ追跡
- m = 3n+1 ≡ 1 (mod 3) という制約が鍵
- m を2で割るとき、3進での繰り下がり構造が s3 mod 2 を制御
""")

# ============================================================
# 21. 証明の試み: m ≡ 1 (mod 3) のとき s3(m) - s3(m/2) は常に奇数？
# ============================================================
print("=" * 70)
print("証明の試み: m ≡ 1 (mod 3) かつ m偶数 のとき s3(m) - s3(m/2) の偶奇")
print("=" * 70)

# m ≡ 1 (mod 3) かつ偶数
parity_diff = Counter()
for m in range(4, 100001, 2):
    if m % 3 == 1:
        d = (s3(m) - s3(m // 2)) % 2
        parity_diff[d] += 1

print(f"\nm ≡ 1 (mod 3), m偶数:")
print(f"  s3(m) - s3(m/2) ≡ 0 (mod 2): {parity_diff[0]}")
print(f"  s3(m) - s3(m/2) ≡ 1 (mod 2): {parity_diff[1]}")
print(f"→ 常に奇数ではない!")

print("\nでは m ≡ 1 (mod 3) かつ m ≡ 0 (mod 2^k) で k=v2(m) のとき？")
for k_val in range(1, 7):
    p0 = 0
    p1 = 0
    for m in range(2**k_val, 100001, 2**k_val):
        if m % 3 == 1 and v2(m) == k_val:
            q = m // (2**k_val)
            if q % 2 == 1:  # q is odd
                d = (s3(m) - s3(q)) % 2
                if d == 0:
                    p0 += 1
                else:
                    p1 += 1
    total = p0 + p1
    if total > 0:
        print(f"  k={k_val}: s3(m)-s3(m/2^k) mod 2: "
              f"偶数={p0} ({100*p0/total:.1f}%), 奇数={p1} ({100*p1/total:.1f}%)")

print("\n重要な発見:")
print("m = 3n+1 (n奇数) のとき k=v2(m) として")
print("s3(m) - s3(m/2^k) mod 2 は必ず奇数")
print("これは m が一般の m≡1 (mod 3) とは異なる特殊構造を持つため")

# m = 3n+1 の特殊構造
print("\nm = 3n+1 (n奇数) の追加制約:")
print("n が奇数 → 3n+1 ≡ 0 (mod 2) だが、更に:")
for n in range(1, 51, 2):
    m = 3 * n + 1
    k = v2(m)
    print(f"  n={n:3d}: 3n+1={m:4d}, mod6={m%6}, mod12={m%12}, mod18={m%18}, v2={k}")

# ============================================================
# 22. 最終的な数値的結論
# ============================================================
print("\n" + "=" * 70)
print("最終的な数値的結論")
print("=" * 70)

# 大規模検証
import time
t0 = time.time()
match = 0
total = 0
for n in range(1, 1000001, 2):
    tn = syracuse(n)
    if s3(tn) % 2 == s3(n) % 2:
        match += 1
    total += 1
t1 = time.time()

print(f"\nn=1..1000000 の奇数 ({total} 個) で検証: {t1-t0:.2f}秒")
print(f"s3(T(n)) mod 2 = s3(n) mod 2: {match}/{total} ({100*match/total:.8f}%)")

if match == total:
    print("\n結論: s3(n) mod 2 は Syracuse写像 T の不変量である（数値的に確認）")
    print("\nこれは以下を意味する:")
    print("  奇数 n に対して s3(n) mod 2 = 0 ならば、軌道上の全ての値で s3 mod 2 = 0")
    print("  奇数 n に対して s3(n) mod 2 = 1 ならば、軌道上の全ての値で s3 mod 2 = 1")
    print("  特に s3(1) = 1, 1 mod 2 = 1 なので、1 に到達する全ての奇数は s3 mod 2 = 1")
    print()
    print("待って... s3(1) = 1, mod 2 = 1")
    print("もし s3(n) mod 2 = 0 の奇数 n が存在するなら、その軌道は 1 に到達しない！")
    print("→ コラッツ予想が正しいなら、奇数で s3(n) mod 2 = 0 のものは存在しない？")
    print()

    # s3(n) mod 2 = 0 の奇数は存在する？
    examples = []
    for n in range(1, 101, 2):
        if s3(n) % 2 == 0:
            examples.append(n)
    print(f"s3(n) mod 2 = 0 の奇数 (n=1..100): {examples}")

    if examples:
        print("\nこれらの軌道を確認:")
        for n in examples[:5]:
            traj = syracuse_trajectory(n, max_steps=100)
            print(f"  n={n}: 軌道 = {traj[:10]}...")
            s3_vals = [s3(t) % 2 for t in traj[:10]]
            print(f"        s3 mod 2 = {s3_vals}")

        print("\n!!! s3(n) mod 2 = 0 の奇数が存在し、かつ 1 に到達している !!!")
        print("→ s3 mod 2 は不変量ではないか、何かを見落としている")
        print()

        # 再確認
        n = examples[0]
        tn = syracuse(n)
        print(f"再確認: n={n}, s3(n)={s3(n)}, mod2={s3(n)%2}")
        print(f"  T(n)={tn}, s3(T(n))={s3(tn)}, mod2={s3(tn)%2}")
        if s3(tn) % 2 != s3(n) % 2:
            print("  → これは反例！最初の大規模検証が間違っている？")
        else:
            print("  → 1ステップでは保存。でも最終的に 1 に到達？")
            print(f"  s3(1)={s3(1)}, mod2={s3(1)%2}")
            print("  → 軌道の中で mod 2 が変わるステップがあるはず！")
            traj = syracuse_trajectory(n, max_steps=300)
            for i in range(len(traj) - 1):
                if s3(traj[i]) % 2 != s3(traj[i+1]) % 2:
                    print(f"  ステップ {i}: {traj[i]} → {traj[i+1]}")
                    print(f"    s3 mod 2: {s3(traj[i])%2} → {s3(traj[i+1])%2}")
                    break
            else:
                print("  → 変わるステップなし！ つまり全軌道で保存されている")
                print(f"  最終値: {traj[-1]}, s3={s3(traj[-1])}, mod2={s3(traj[-1])%2}")
else:
    print(f"\n反例あり: {total - match} 個")
