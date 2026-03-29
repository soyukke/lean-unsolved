"""
Well-ordering principle による最小反例の制約分析

コラッツ予想の最小反例 n0 に対して:
1. n0 >= 1, not reachesOne(n0)
2. forall m, 1 <= m < n0 -> reachesOne(m)

既に証明済み:
- n0 > 1
- n0 は奇数 (n0 % 2 = 1)
- n0 ≡ 3 (mod 4)
- n0 % 16 != 3
- n0 % 32 != 11
- n0 % 32 != 23

Syracuse関数 T(n) = (3n+1) / 2^{v2(3n+1)} を使う。

戦略: n ≡ r (mod M) のとき、T^k(n) < n を示して矛盾を導く。
T^k(n) < n かつ T^k(n) >= 1 かつ ¬reachesOne(T^k(n)) → 最小性矛盾。
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

def analyze_residue_class(mod, residue, max_steps=20):
    """
    n ≡ residue (mod mod) の場合に、
    T^k(n) < n が最初に成立するステップ数を分析。
    q をパラメータとして n = mod * q + residue とおく。
    """
    # まず具体値で検証
    results = []
    for q in range(1, 50):
        n = mod * q + residue
        if n < 2:
            continue
        if n % 2 == 0:  # 偶数は除外
            continue

        current = n
        for step in range(1, max_steps + 1):
            current = syracuse(current)
            if current < n:
                results.append((q, n, step, current))
                break
        else:
            results.append((q, n, -1, current))  # 下降しなかった

    return results

def symbolic_analysis(mod, residue, max_steps=10):
    """
    n = mod * q + residue のとき、T^k(n) を q の関数として表現。
    各ステップで (3n+1) の v2 を mod 値から決定する。
    """
    print(f"\n=== Symbolic analysis: n ≡ {residue} (mod {mod}) ===")
    print(f"n = {mod}*q + {residue}")

    # 各ステップの T(n) を線形式 a*q + b で表す
    a, b = mod, residue  # n = a*q + b

    for step in range(1, max_steps + 1):
        # T(a*q + b) = (3*(a*q + b) + 1) / 2^v
        numerator_a = 3 * a
        numerator_b = 3 * b + 1

        # v2 は (3*b + 1) から決まる（q に依存しない部分）
        # ただし a が 2 のべきで割り切れる場合は注意
        v = v2(numerator_b)

        # 実際には v2(3*a*q + 3*b + 1) は一般に q に依存しうる
        # しかし mod が十分大きければ、v2 は分子の定数部分で決まる
        # 条件: a が 2^v で割り切れる
        if numerator_a % (2 ** v) != 0:
            print(f"  Step {step}: T^{step}(n) の v2 が q に依存する（分析困難）")
            print(f"    3*a = {numerator_a}, 3*b+1 = {numerator_b}, v2 = {v}")
            print(f"    {numerator_a} % {2**v} = {numerator_a % (2**v)}")
            break

        new_a = numerator_a // (2 ** v)
        new_b = numerator_b // (2 ** v)

        ratio = new_a / a if a != 0 else float('inf')
        diff = new_b - b  # T^k(n) - n の定数部分の寄与

        print(f"  Step {step}: T^{step}(n) = {new_a}*q + {new_b}")
        print(f"    v2 = {v}, 比率 a'/a = {new_a}/{a} = {ratio:.4f}")
        print(f"    T^{step}(n) < n iff {new_a}*q + {new_b} < {mod}*q + {residue}")

        if new_a < mod:
            threshold_q = (new_b - residue) / (mod - new_a) if mod > new_a else float('inf')
            print(f"    → {mod - new_a}*q > {new_b - residue}")
            print(f"    → q > {threshold_q:.4f}")
            if threshold_q < 0:
                print(f"    → 全ての q >= 0 で成立！（強い結果）")
            else:
                print(f"    → q >= {int(threshold_q) + 1} で成立")
        elif new_a == mod:
            print(f"    → 定数比較: {new_b} vs {residue}")
            if new_b < residue:
                print(f"    → 全ての q で成立！")
            else:
                print(f"    → 成立しない（比率 = 1）")
        else:
            print(f"    → 成立しない（a' > mod）")

        a, b = new_a, new_b

        # 新しい値が奇数かチェック
        if new_b % 2 == 0:
            print(f"    注意: 定数部分 {new_b} が偶数 → T の次の適用は意味が異なる")
            break

# 既に排除済みの mod 4 残基
print("=" * 60)
print("既に排除済み:")
print("  n ≡ 1 (mod 4): n ≡ 1 mod 4 → T(n) < n")
print("  n ≡ 3 (mod 16): 2ステップで下降")
print("  n ≡ 11 (mod 32): 3ステップで下降")
print("  n ≡ 23 (mod 32): 3ステップで下降")
print()

# n ≡ 3 (mod 4) の残りの剰余類を調べる
# mod 4 で 3 のみ可能
# mod 16 で 3 は排除済み → {7, 11, 15} が可能
# mod 32 で 11, 23 は排除済み
# mod 32 で 3 mod 4 かつ 排除されていないもの:
#   mod 32: 3, 7, 11, 15, 19, 23, 27, 31 のうち mod 4 = 3 は
#   3, 7, 11, 15, 19, 23, 27, 31
# 実は mod 4 = 3 は: 3, 7, 11, 15, 19, 23, 27, 31 のうち r % 4 == 3 のもの

print("mod 32 で n ≡ 3 (mod 4) の剰余類:")
remaining = []
for r in range(32):
    if r % 4 == 3:
        eliminated = False
        # mod 16: 3 排除
        if r % 16 == 3:
            eliminated = True
            print(f"  {r}: mod 16 ≡ 3 → 排除済み")
        # mod 32: 11, 23 排除
        elif r % 32 == 11 or r % 32 == 23:
            eliminated = True
            print(f"  {r}: mod 32 ≡ {r} → 排除済み")
        else:
            remaining.append(r)
            print(f"  {r}: 未排除")

print(f"\nmod 32 で未排除: {remaining}")

# 各未排除クラスの分析
for r in remaining:
    symbolic_analysis(32, r)
    # 数値検証
    results = analyze_residue_class(32, r)
    if results:
        first_few = results[:5]
        for q, n, step, val in first_few:
            print(f"  n={n} (q={q}): step={step}, T^{step}(n)={val}")

# さらに mod 64 で分析
print("\n" + "=" * 60)
print("mod 64 で未排除の剰余類:")
remaining_64 = []
for r in range(64):
    if r % 4 != 3:
        continue
    eliminated = False
    if r % 16 == 3:
        eliminated = True
    elif r % 32 == 11 or r % 32 == 23:
        eliminated = True
    if not eliminated:
        remaining_64.append(r)

print(f"  {remaining_64}")
print(f"  合計 {len(remaining_64)} / 64 = {len(remaining_64)/64:.1%} が残存")

for r in remaining_64:
    symbolic_analysis(64, r)

# mod 128, 256 ... まで拡張
print("\n" + "=" * 60)
print("剰余類排除の進捗:")
for M in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
    total = M
    eliminated = 0
    for r in range(M):
        if r % 2 == 0:
            eliminated += 1  # 偶数は除外
            continue
        if r % 4 == 1:
            eliminated += 1  # mod 4 = 1 は即下降
            continue
        # mod 4 = 3 の中で排除可能かチェック
        n_test = M * 100 + r  # 大きめの q で試す
        current = n_test
        for step in range(20):
            current = syracuse(current)
            if current < n_test:
                eliminated += 1
                break

    remaining_pct = (total - eliminated) / total * 100
    print(f"  mod {M:5d}: 排除 {eliminated}/{total} ({eliminated/total:.1%}), 残存 {remaining_pct:.1f}%")
