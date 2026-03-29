"""
syracuse_mod3_eq の系として有用な補題の設計

既知: syracuse_mod3_eq:
  T(n) % 3 = if v2(3n+1) % 2 == 0 then 1 else 2

調査項目:
1. T(n) ≡ 2 (mod 3) <=> v2(3n+1) が奇数  の具体的検証
2. T(T(n)) の mod 3 追跡
3. mod 9 への拡張可能性
4. 連続 Syracuse 反復での mod 3 パターン
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
    return m // (2 ** v2(m))

def syracuse_iter(n, k):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

print("=" * 70)
print("1. syracuse_mod3_eq の検証: T(n) % 3 vs v2(3n+1) の偶奇")
print("=" * 70)

# 奇数 n に対して検証
consistent = True
for n in range(1, 200, 2):  # odd numbers
    m = 3 * n + 1
    v = v2(m)
    tn = syracuse(n)
    expected = 1 if v % 2 == 0 else 2
    actual = tn % 3
    if actual != expected:
        print(f"MISMATCH: n={n}, v2(3n+1)={v}, T(n)={tn}, T(n)%3={actual}, expected={expected}")
        consistent = False
    if n < 30:
        print(f"  n={n:3d}: 3n+1={m:5d}, v2={v}, T(n)={tn:5d}, T(n)%3={actual}, v2%2={'even' if v%2==0 else 'odd'} => expected {expected} {'OK' if actual==expected else 'FAIL'}")

if consistent:
    print("  [ALL CONSISTENT for n in 1..199 odd]")

print()
print("=" * 70)
print("2. T(n) ≡ 2 (mod 3) <=> v2(3n+1) 奇数 の同値性の検証")
print("=" * 70)

# 系1: T(n) ≡ 2 (mod 3) <=> v2 odd
mod3_eq2_count = 0
mod3_eq1_count = 0
for n in range(1, 10000, 2):
    tn = syracuse(n)
    v = v2(3 * n + 1)
    if tn % 3 == 2:
        mod3_eq2_count += 1
        assert v % 2 == 1, f"Failed at n={n}"
    else:
        mod3_eq1_count += 1
        assert tn % 3 == 1
        assert v % 2 == 0, f"Failed at n={n}"

print(f"  T(n)≡1 (mod 3) count: {mod3_eq1_count}")
print(f"  T(n)≡2 (mod 3) count: {mod3_eq2_count}")
print(f"  ratio (mod3=1)/(mod3=2): {mod3_eq1_count/mod3_eq2_count:.4f}")

print()
print("=" * 70)
print("3. T(T(n)) の mod 3 パターン追跡")
print("=" * 70)

# T(n) は必ず奇数なので T(T(n)) も定義できる
# T(n) % 3 = 1 or 2 (never 0, by syracuse_not_div_three)
# T(T(n)) % 3 はどうなるか?

transitions = {}  # (T(n)%3) -> (T(T(n))%3) の遷移
for n in range(1, 10000, 2):
    tn = syracuse(n)
    ttn = syracuse(tn)
    key = (tn % 3, ttn % 3)
    transitions[key] = transitions.get(key, 0) + 1

print("  Transitions (T(n)%3 -> T(T(n))%3):")
for k in sorted(transitions.keys()):
    print(f"    {k[0]} -> {k[1]}: {transitions[k]} times")

# v2 の偶奇遷移
v2_transitions = {}
for n in range(1, 10000, 2):
    tn = syracuse(n)
    v1 = v2(3 * n + 1) % 2
    v2_val = v2(3 * tn + 1) % 2
    key = (v1, v2_val)
    v2_transitions[key] = v2_transitions.get(key, 0) + 1

print("\n  v2 parity transitions (v2(3n+1)%2 -> v2(3*T(n)+1)%2):")
for k in sorted(v2_transitions.keys()):
    print(f"    {'even' if k[0]==0 else 'odd'} -> {'even' if k[1]==0 else 'odd'}: {v2_transitions[k]} times")

print()
print("=" * 70)
print("4. mod 9 への拡張: T(n) % 9 の分布")
print("=" * 70)

mod9_dist = {}
for n in range(1, 10000, 2):
    tn = syracuse(n)
    r = tn % 9
    mod9_dist[r] = mod9_dist.get(r, 0) + 1

print("  T(n) % 9 distribution:")
for r in sorted(mod9_dist.keys()):
    print(f"    T(n)≡{r} (mod 9): {mod9_dist[r]} times")

# v2(3n+1) のmod別 T(n) % 9 分布
print("\n  T(n) % 9 by v2(3n+1) value:")
v2_mod9 = {}
for n in range(1, 10000, 2):
    v = v2(3 * n + 1)
    tn = syracuse(n)
    r = tn % 9
    key = (v, r)
    v2_mod9[key] = v2_mod9.get(key, 0) + 1

# v2=1..8 ごとにmod9分布を表示
for v_val in range(1, 9):
    results = [(r, v2_mod9.get((v_val, r), 0)) for r in range(9)]
    nonzero = [(r, c) for r, c in results if c > 0]
    if nonzero:
        print(f"    v2={v_val}: {dict(nonzero)}")

print()
print("=" * 70)
print("5. 2^v mod 9 の値: mod9における完全分類")
print("=" * 70)

# 2^v mod 9 の周期性
for v_val in range(12):
    print(f"  2^{v_val} mod 9 = {pow(2, v_val) % 9}")

# T(n) * 2^v = 3n+1, so T(n) mod 9 = (3n+1) * (2^v)^{-1} mod 9
# 2^v mod 9 の逆元:
# 2^0=1 mod 9, inv=1
# 2^1=2 mod 9, inv=5 (2*5=10=1 mod 9)
# 2^2=4 mod 9, inv=7 (4*7=28=1 mod 9)
# 2^3=8 mod 9, inv=8 (8*8=64=1 mod 9)
# 2^4=7 mod 9, inv=4 (7*4=28=1 mod 9)
# 2^5=5 mod 9, inv=2 (5*2=10=1 mod 9)
# 周期6

print("\n  2^v mod 9 inverses:")
for v_val in range(6):
    m = pow(2, v_val, 9)
    # find inverse
    for inv in range(9):
        if (m * inv) % 9 == 1:
            print(f"    v={v_val}: 2^v≡{m} (mod 9), inverse≡{inv} (mod 9)")
            break

# T(n) ≡ (3n+1) * inv(2^v2) (mod 9) の確認
# 3n+1 ≡ 1 (mod 3) always, but mod 9?
# 3n+1 mod 9: n mod 3 = 0 => 1, n mod 3 = 1 => 4, n mod 3 = 2 => 7
# つまり 3n+1 mod 9 ∈ {1, 4, 7}

print("\n  (3n+1) mod 9 by n mod 3:")
for r in range(3):
    vals = set()
    for n in range(r, 100, 3):
        if n % 2 == 1:  # odd only
            vals.add((3*n+1) % 9)
    if vals:
        print(f"    n≡{r} (mod 3): (3n+1) mod 9 ∈ {sorted(vals)}")

# さらに n mod 9 別の完全分類
print("\n  (3n+1) mod 9 by n mod 9 (odd n only):")
for r in [1, 3, 5, 7]:  # odd residues mod 8... actually mod 9
    for s in range(9):
        if s % 2 == 1:  # odd
            val = (3*s+1) % 9
            print(f"    n≡{s} (mod 9): (3n+1) mod 9 = {val}")
    break  # just need mod 9

print()
print("=" * 70)
print("6. syracuse_mod3_eq の直接系: 同値形")
print("=" * 70)

# 系1: T(n) ≡ 2 (mod 3) <=> v2(3n+1) % 2 = 1
# 系2: T(n) ≡ 1 (mod 3) <=> v2(3n+1) % 2 = 0
# これらは syracuse_mod3_eq の if-then-else 分解

print("  Corollary 1: T(n) ≡ 2 (mod 3) <=> v2(3n+1) odd")
print("  Corollary 2: T(n) ≡ 1 (mod 3) <=> v2(3n+1) even")
print("  These are direct rewrites of syracuse_mod3_eq.")

print()
print("=" * 70)
print("7. mod 3 の軌道パターン（連続反復）")
print("=" * 70)

# 各奇数 n から始めて T^k(n) % 3 の列を追跡
patterns = {}
for n in range(1, 100, 2):
    seq = []
    x = n
    for _ in range(10):
        x = syracuse(x)
        seq.append(x % 3)
    pat = tuple(seq[:6])
    if pat not in patterns:
        patterns[pat] = []
    patterns[pat].append(n)

print(f"  Number of distinct mod 3 patterns (length 6): {len(patterns)}")
for pat, ns in sorted(patterns.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"    pattern {pat}: {ns[:5]}{'...' if len(ns)>5 else ''} ({len(ns)} values)")

print()
print("=" * 70)
print("8. T(T(n)) mod 3 の完全予測: v2 連鎖")
print("=" * 70)

# T(T(n)) % 3 は v2(3*T(n)+1) の偶奇で決まる
# T(n) は奇数なので 3*T(n)+1 は偶数で v2 が定義される
# T(T(n)) % 3 = 1 if v2(3*T(n)+1) even, 2 if odd

# 問: v2(3*T(n)+1) はどう予測できるか?
# T(n) = (3n+1)/2^v  where v = v2(3n+1)
# 3*T(n)+1 = 3*(3n+1)/2^v + 1 = (3(3n+1) + 2^v) / 2^v = (9n+3+2^v) / 2^v

print("  T(T(n)) % 3 prediction requires v2(3*T(n)+1)")
print("  3*T(n)+1 = (9n + 3 + 2^v) / 2^v where v = v2(3n+1)")
print()

# 検証: n mod 8 別の T(T(n)) % 3
mod8_tt_mod3 = {}
for n in range(1, 10000, 2):
    r8 = n % 8
    tn = syracuse(n)
    ttn = syracuse(tn)
    key = (r8, ttn % 3)
    mod8_tt_mod3[key] = mod8_tt_mod3.get(key, 0) + 1

print("  T(T(n)) % 3 by n mod 8:")
for r8 in [1, 3, 5, 7]:
    results = {mod3: mod8_tt_mod3.get((r8, mod3), 0) for mod3 in [1, 2]}
    print(f"    n≡{r8} (mod 8): T(T(n))%3: {results}")

# n mod 16 で
print("\n  T(T(n)) % 3 by n mod 16:")
mod16_tt_mod3 = {}
for n in range(1, 20000, 2):
    r16 = n % 16
    tn = syracuse(n)
    ttn = syracuse(tn)
    key = (r16, ttn % 3)
    mod16_tt_mod3[key] = mod16_tt_mod3.get(key, 0) + 1

for r16 in range(16):
    if r16 % 2 == 1:
        results = {mod3: mod16_tt_mod3.get((r16, mod3), 0) for mod3 in [1, 2]}
        total = sum(results.values())
        if total > 0:
            ratios = {k: f"{v/total:.2%}" for k, v in results.items()}
            print(f"    n≡{r16:2d} (mod 16): {results} ({ratios})")

print()
print("=" * 70)
print("9. mod 9 拡張: T(n) mod 9 = f(n mod 9, v2)")
print("=" * 70)

# T(n) = (3n+1) / 2^v
# T(n) mod 9 = ((3n+1) mod 9) * (2^v mod 9)^{-1} mod 9
# ただし 2^v mod 9 は周期6

inv_table = {}
for m in range(1, 9):
    if m % 3 != 0:  # coprime to 9
        for inv in range(9):
            if (m * inv) % 9 == 1:
                inv_table[m] = inv
                break

print(f"  Modular inverses mod 9: {inv_table}")
print(f"  2^v mod 9 cycle: {[pow(2,v)%9 for v in range(6)]}")

# 検証
errors = 0
for n in range(1, 5000, 2):
    m = 3 * n + 1
    v = v2(m)
    tn = m // (2**v)

    m_mod9 = m % 9
    pow2v_mod9 = pow(2, v) % 9

    if pow2v_mod9 in inv_table:
        predicted = (m_mod9 * inv_table[pow2v_mod9]) % 9
        actual = tn % 9
        if predicted != actual:
            errors += 1
            if errors <= 3:
                print(f"  ERROR: n={n}, m={m}, v={v}, m%9={m_mod9}, 2^v%9={pow2v_mod9}, pred={predicted}, actual={actual}")

if errors == 0:
    print("  [VERIFIED] T(n) mod 9 = (3n+1) mod 9 * inv(2^v2 mod 9) mod 9  for all odd n in [1..4999]")
else:
    print(f"  Errors: {errors}")

# 完全な T(n) mod 9 の分類: (n mod 9, v2 mod 6) -> T(n) mod 9
print("\n  Complete T(n) mod 9 classification by (n mod 9, v2 mod 6):")
classification = {}
for n in range(1, 10000, 2):
    m = 3 * n + 1
    v = v2(m)
    tn = syracuse(n)
    key = (n % 9, v % 6)
    val = tn % 9
    if key not in classification:
        classification[key] = set()
    classification[key].add(val)

# n mod 9 の奇数値のみ
for n9 in range(9):
    for v6 in range(6):
        if (n9, v6) in classification:
            vals = classification[(n9, v6)]
            if len(vals) == 1:
                print(f"    (n%9={n9}, v2%6={v6}): T(n)%9 = {list(vals)[0]}")

print()
print("=" * 70)
print("10. T(n) mod 3 の連続軌道：1-2-1-2パターン?")
print("=" * 70)

# mod 3 列のパターン統計
from collections import Counter

all_patterns = Counter()
for n in range(1, 5000, 2):
    seq = []
    x = n
    for _ in range(8):
        x = syracuse(x)
        seq.append(x % 3)
    all_patterns[tuple(seq)] += 1

# 上位10パターン
print("  Top 10 mod 3 orbit patterns (length 8):")
for pat, count in all_patterns.most_common(10):
    print(f"    {pat}: {count} times")

# 連続で同じ mod 3 が続く最大長
print("\n  Max consecutive same mod 3 value in orbits:")
max_run_1 = 0
max_run_2 = 0
for n in range(1, 10000, 2):
    x = n
    run_1 = 0
    run_2 = 0
    current_run = 0
    last_mod = -1
    for _ in range(50):
        x = syracuse(x)
        m = x % 3
        if m == last_mod:
            current_run += 1
        else:
            current_run = 1
        last_mod = m
        if m == 1:
            max_run_1 = max(max_run_1, current_run)
        if m == 2:
            max_run_2 = max(max_run_2, current_run)

print(f"    Max consecutive T^k(n)≡1 (mod 3): {max_run_1}")
print(f"    Max consecutive T^k(n)≡2 (mod 3): {max_run_2}")

print()
print("=" * 70)
print("11. 有用な補題候補のまとめ")
print("=" * 70)

# T(n)が mod4=3 (上昇する)かつ T(n)%3の性質
print("  Lemma candidates:")
print()
print("  [L1] syracuse_mod3_eq_two_iff:")
print("      T(n) % 3 = 2 <-> v2(3n+1) % 2 = 1")
print("      (direct rewrite of syracuse_mod3_eq)")
print()
print("  [L2] syracuse_mod3_eq_one_iff:")
print("      T(n) % 3 = 1 <-> v2(3n+1) % 2 = 0")
print("      (direct rewrite of syracuse_mod3_eq)")
print()
print("  [L3] syracuse_mod9_eq (mod 9 extension):")
print("      T(n) % 9 = ((3n+1) % 9) * modular_inverse(2^(v2(3n+1)) % 9) % 9")
print("      (requires 2^v mod 9 has period 6)")
print()
print("  [L4] syracuse_ascent_mod3 (上昇ステップでの mod 3):")
print("      n % 4 = 3 => T(n) % 3 = 2")
print("      (because v2(3n+1)=1 which is odd)")

# L4 の検証
print("\n  Verifying L4: n%4=3 => T(n)%3=2")
all_ok = True
for n in range(3, 10000, 4):
    tn = syracuse(n)
    if tn % 3 != 2:
        print(f"    FAIL: n={n}, T(n)={tn}, T(n)%3={tn%3}")
        all_ok = False
if all_ok:
    print("    [VERIFIED] for all n≡3 (mod 4), 3≤n<10000")

print()
print("  [L5] syracuse_descent_mod3:")
print("      n % 4 = 1 and n > 1 => T(n) % 3 ∈ {1, 2}")
print("      (v2 ≥ 2, parity depends on exact v2)")

# v2(3n+1) for n%4=1
print("\n  v2 distribution for n≡1 (mod 4):")
v2_dist_mod4_1 = Counter()
for n in range(1, 10000, 4):
    v2_dist_mod4_1[v2(3*n+1)] += 1
for v, count in sorted(v2_dist_mod4_1.items()):
    parity = "even" if v % 2 == 0 else "odd"
    mod3 = 1 if v % 2 == 0 else 2
    print(f"    v2={v} ({parity}, T(n)%3={mod3}): {count} times")

print()
print("  [L6] two_ascent_second_mod3:")
print("      n % 8 = 7 => T(T(n)) % 3 depends on deeper structure")

# n%8=7 でのT(T(n))%3
print("\n  T(T(n)) % 3 for n≡7 (mod 8):")
tt_mod3_dist = Counter()
for n in range(7, 10000, 8):
    tn = syracuse(n)
    ttn = syracuse(tn)
    tt_mod3_dist[ttn % 3] += 1
print(f"    {dict(tt_mod3_dist)}")
