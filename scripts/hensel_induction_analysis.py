"""
一般化Hensel帰納法の分析:
k回連続上昇 <=> n ≡ 2^{k+1} - 1 (mod 2^{k+1})

帰納ステップの核心を分析する。

帰納仮説: k回連続上昇 <=> n % 2^{k+1} = 2^{k+1} - 1
帰納ステップ: (k+1)回連続上昇 <=> n % 2^{k+2} = 2^{k+2} - 1

鍵: n が 2^{k+1}-1 (mod 2^{k+1}) を満たすとき、
    syracuseIter k n の mod 条件を追跡する。
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
    """Syracuse function T(n) = (3n+1)/2^{v2(3n+1)}"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

def consecutive_ascents(n, k):
    """Check if n has k consecutive ascents"""
    for i in range(k):
        curr = syracuse_iter(i, n)
        next_val = syracuse(curr)
        if next_val <= curr:
            return False
    return True

# === 基本パターンの検証 ===
print("=== パターン検証: k回連続上昇 <=> n ≡ 2^{k+1}-1 (mod 2^{k+1}) ===")
for k in range(1, 8):
    modulus = 2 ** (k + 1)
    target = modulus - 1
    # 全ての奇数 1..127 について検証
    matches = 0
    mismatches = 0
    for n in range(1, 256, 2):
        has_ascents = consecutive_ascents(n, k)
        satisfies_mod = (n % modulus == target)
        if has_ascents == satisfies_mod:
            matches += 1
        else:
            mismatches += 1
            print(f"  MISMATCH k={k}: n={n}, ascents={has_ascents}, mod={n%modulus}=={target}? {satisfies_mod}")
    print(f"k={k}: mod {modulus} = {target}, matches={matches}, mismatches={mismatches}")

# === 帰納ステップの核心分析 ===
print("\n=== 帰納ステップ分析: k回上昇後のsyracuseIter k n の mod 条件 ===")
print("n ≡ 2^{k+1}-1 (mod 2^{k+1}) のとき、syracuseIter k n の mod 4 は？")
print("k+1回目の上昇 <=> syracuseIter k n ≡ 3 (mod 4)")
print()

for k in range(1, 7):
    modulus = 2 ** (k + 1)
    target = modulus - 1
    modulus_next = 2 ** (k + 2)
    target_next = modulus_next - 1

    print(f"--- k={k} → k+1={k+1} ---")
    # n ≡ 2^{k+1}-1 (mod 2^{k+1}) を満たすnについて
    # syracuseIter k n の mod 4 と n mod 2^{k+2} の関係を調べる

    # n mod 2^{k+2} = target (つまり 2^{k+1}-1) か target_next (つまり 2^{k+2}-1) の2通り
    for n_mod in [target, target_next]:
        n = n_mod  # 代表元
        if n == 0:
            continue
        # 複数の代表元で検証
        results = []
        for mult in range(8):
            n_test = n_mod + mult * modulus_next
            if n_test == 0:
                continue
            if n_test % 2 == 0:
                continue
            iter_val = syracuse_iter(k, n_test)
            mod4 = iter_val % 4
            ascent_kp1 = consecutive_ascents(n_test, k + 1)
            results.append((n_test, iter_val, mod4, ascent_kp1))

        if results:
            mod4_vals = set(r[2] for r in results)
            ascent_vals = set(r[3] for r in results)
            print(f"  n ≡ {n_mod} (mod {modulus_next}): "
                  f"syracuseIter {k} n mod 4 = {mod4_vals}, "
                  f"(k+1)ascent = {ascent_vals}")

# === syracuseIter k n の明示的計算（mod 分析） ===
print("\n=== syracuseIter k n の明示的な式 ===")
print("n ≡ 2^{k+1}-1 (mod 2^{k+1}) のとき、各ステップでの値")
print()

for k in range(1, 6):
    modulus = 2 ** (k + 1)
    target = modulus - 1
    print(f"k={k}: n ≡ {target} (mod {modulus})")

    # nを可変にして数個のサンプルで確認
    for n in [target, target + modulus, target + 2*modulus, target + 3*modulus]:
        if n == 0:
            continue
        orbit = [n]
        for step in range(k + 2):
            curr = orbit[-1]
            nxt = syracuse(curr)
            v = v2(3 * curr + 1)
            orbit.append(nxt)

        orbit_str = " -> ".join(str(x) for x in orbit[:k+3])
        ascent_marks = []
        for j in range(len(orbit)-1):
            ascent_marks.append("↑" if orbit[j+1] > orbit[j] else "↓")
        marks_str = " ".join(ascent_marks[:k+2])
        print(f"  n={n}: {orbit_str}  [{marks_str}]")
    print()

# === 帰納ステップの鍵: Syracuse chain formula ===
print("=== Syracuse chain formula: n≡3(mod4) のとき syracuse(n) = (3n+1)/2 ===")
print("k回連続上昇すると、各ステップで (3x+1)/2 が適用される")
print("つまり syracuseIter k n = f^k(n) where f(x) = (3x+1)/2")
print()

def f(x):
    """f(x) = (3x+1)/2 (整数除算)"""
    return (3 * x + 1) // 2

def f_iter(k, x):
    for _ in range(k):
        x = f(x)
    return x

# 検証: 連続上昇中は syracuseIter = f_iter か？
print("検証: 連続上昇中は syracuseIter k n = f_iter k n か？")
for k in range(1, 7):
    modulus = 2 ** (k + 1)
    target = modulus - 1
    all_match = True
    for mult in range(20):
        n = target + mult * modulus
        if n == 0:
            continue
        for step in range(k):
            s_val = syracuse_iter(step, n)
            f_val = f_iter(step, n)
            if s_val != f_val:
                all_match = False
                print(f"  MISMATCH k={k} n={n} step={step}: syr={s_val} f={f_val}")
    print(f"k={k}: syracuseIter = f_iter for all {k} steps? {all_match}")

# === f^k(n) の閉じた式 ===
print("\n=== f^k(n) の閉じた式分析 ===")
print("f(x) = (3x+1)/2")
print("f^1(x) = (3x+1)/2")
print("f^2(x) = (3*(3x+1)/2 + 1)/2 = (9x+3+2)/4 = (9x+5)/4")
print("f^3(x) = (3*(9x+5)/4 + 1)/2 = (27x+15+4)/8 = (27x+19)/8")
print("f^4(x) = (3*(27x+19)/8 + 1)/2 = (81x+57+8)/16 = (81x+65)/16")
print()

# 一般項: f^k(n) = (3^k * n + (3^k - 1)/2) / 2^k ???
# 検証してみる
# f^k(n) = (3^k * n + c_k) / 2^k where c_k = ?

for k in range(1, 8):
    # c_k を n=0 で計算（形式的に、n は奇数前提だが数式として）
    # f^k(0) = c_k / 2^k
    # しかし n は正の奇数なので、もっと多くのサンプルで

    # 実際に f^k(n) = (3^k * n + c_k) / 2^k と仮定して c_k を求める
    n_test = 2**(k+1) - 1  # 典型的な n
    fk = f_iter(k, n_test)
    # fk = (3^k * n + c_k) / 2^k
    # c_k = fk * 2^k - 3^k * n
    ck = fk * (2**k) - (3**k) * n_test

    # 別の n でも c_k が同じか確認
    n_test2 = 2**(k+1) - 1 + 2**(k+1)
    fk2 = f_iter(k, n_test2)
    ck2 = fk2 * (2**k) - (3**k) * n_test2

    n_test3 = 2**(k+1) - 1 + 2 * 2**(k+1)
    fk3 = f_iter(k, n_test3)
    ck3 = fk3 * (2**k) - (3**k) * n_test3

    print(f"k={k}: c_k from n={n_test}: {ck}, n={n_test2}: {ck2}, n={n_test3}: {ck3}")

    # 3^k - 1 の値
    print(f"  3^k - 1 = {3**k - 1}, (3^k-1)/2 = {(3**k-1)//2}, c_k = {ck}")
    # c_k = (3^k - 1) / 2 ?
    if ck == (3**k - 1) // 2:
        print(f"  => c_k = (3^k - 1)/2 CONFIRMED")
    else:
        print(f"  => c_k != (3^k - 1)/2")

print()
print("=== 結論: f^k(n) = (3^k * n + (3^k - 1)/2) / 2^k ===")
print("= (3^k * (2n + 1) - 1) / 2^{k+1}")

# === 帰納ステップの mod 条件分析 ===
print("\n=== 帰納ステップ: f^k(n) mod 4 の分析 ===")
print("n ≡ 2^{k+1}-1 (mod 2^{k+1}) のとき")
print("f^k(n) ≡ 3 (mod 4) <=> n ≡ 2^{k+2}-1 (mod 2^{k+2})")
print()

for k in range(1, 7):
    modulus = 2**(k+1)
    target = modulus - 1
    modulus_next = 2**(k+2)
    target_next = modulus_next - 1

    # n ≡ target (mod modulus) には2つのサブクラス modulo modulus_next:
    # n ≡ target (mod modulus_next) or n ≡ target + modulus (mod modulus_next)
    # = target or target_next

    sub1 = target  # 2^{k+1}-1 mod 2^{k+2}
    sub2 = target + modulus  # 2^{k+2}-1 mod 2^{k+2}

    # f^k(sub1) mod 4 と f^k(sub2) mod 4
    results1 = []
    results2 = []
    for mult in range(20):
        n1 = sub1 + mult * modulus_next
        n2 = sub2 + mult * modulus_next
        if n1 > 0:
            results1.append(f_iter(k, n1) % 4)
        if n2 > 0:
            results2.append(f_iter(k, n2) % 4)

    print(f"k={k}: n≡{sub1}(mod {modulus_next}) => f^{k}(n) mod 4 = {set(results1)}")
    print(f"k={k}: n≡{sub2}(mod {modulus_next}) => f^{k}(n) mod 4 = {set(results2)}")
    print(f"  => (k+1)上昇には n≡{sub2}(mod {modulus_next}) = 2^{k+2}-1 (mod 2^{k+2}) が必要")
    print()
