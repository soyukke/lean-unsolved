"""
v3(ascentConst(k)) = v3(3^k - 2^k) の3-adic評価の体系的解析

目的:
1. v3(3^k - 2^k) を k=1..1000 で計算し、パターンを発見
2. サイクル方程式 n(2^s - 3^p) = sum(3^i * 2^{a_i}) の分母の3-adic構造を解析
3. サイクル排除への応用可能性を検討
"""

import math
from collections import Counter, defaultdict

# === Part 1: v3(3^k - 2^k) の計算 ===

def v3(n):
    """3-adic valuation of n"""
    if n == 0:
        return float('inf')
    n = abs(n)
    v = 0
    while n % 3 == 0:
        n //= 3
        v += 1
    return v

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    n = abs(n)
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v

print("=" * 70)
print("Part 1: v3(3^k - 2^k) for k = 1 to 200")
print("=" * 70)

max_k = 200
vals = {}
for k in range(1, max_k + 1):
    val = 3**k - 2**k
    v = v3(val)
    vals[k] = v

# 表示: 最初の50個
print(f"\n{'k':>4} | {'3^k - 2^k':>30} | {'v3':>4} | {'(3^k-2^k)/3^v3':>20}")
print("-" * 70)
for k in range(1, 51):
    val = 3**k - 2**k
    v = vals[k]
    reduced = val // (3**v) if v > 0 else val
    print(f"{k:>4} | {val:>30} | {v:>4} | {reduced:>20}")

# === Part 2: v3 のパターン分析 ===
print("\n" + "=" * 70)
print("Part 2: v3(3^k - 2^k) のパターン")
print("=" * 70)

# v3 の値ごとにkを分類
v3_groups = defaultdict(list)
for k in range(1, max_k + 1):
    v3_groups[vals[k]].append(k)

print("\nv3値ごとのkの分布:")
for v in sorted(v3_groups.keys()):
    ks = v3_groups[v]
    print(f"  v3 = {v}: k in {ks[:15]}{'...' if len(ks) > 15 else ''} (計{len(ks)}個)")

# v3 = 1 の k のパターン
print("\nv3 = 1 の k の mod 解析:")
v3_1_ks = v3_groups[1]
for m in [2, 3, 4, 6, 8, 12]:
    mods = Counter(k % m for k in v3_1_ks)
    print(f"  mod {m}: {dict(sorted(mods.items()))}")

# v3 >= 2 の k のパターン
print("\nv3 >= 2 の k:")
for k in range(1, max_k + 1):
    if vals[k] >= 2:
        print(f"  k={k}, v3={vals[k]}, k mod 2 = {k%2}, k mod 3 = {k%3}, k mod 6 = {k%6}")

# === Part 3: Lifting the Exponent Lemma (LTE) の検証 ===
print("\n" + "=" * 70)
print("Part 3: Lifting the Exponent Lemma の検証")
print("=" * 70)
print("""
LTE for odd primes: p odd, p | a-b, p ∤ a, p ∤ b
=> v_p(a^n - b^n) = v_p(a - b) + v_p(n)

ここで a=3, b=2, p=3:
- 3 | (3-2) = 1 → 3 ∤ 1 なので LTE の条件を満たさない!
- (a-b = 1 なので v3(a-b) = 0)

別の観点: a=3, b=2 で 3 | a だが 3 ∤ b なので、
v3(3^k - 2^k) = v3((-2^k)) = v3(2^k) = 0 ... これは間違い。
実際 3^k - 2^k ≡ -2^k mod 3 で 2^k は 3 と互いに素なので
3^k - 2^k ≢ 0 mod 3 ... のはずだが計算と矛盾!

確認してみよう:
""")

# 3^k - 2^k mod 3 の確認
print("3^k - 2^k mod 3:")
for k in range(1, 20):
    val = 3**k - 2**k
    print(f"  k={k}: 3^k-2^k = {val}, mod 3 = {val % 3}, 2^k mod 3 = {2**k % 3}")

print("""
重要な発見: 3^k ≡ 0 mod 3 なので 3^k - 2^k ≡ -2^k mod 3
- k 奇数: 2^k ≡ 2 mod 3 → -2^k ≡ 1 mod 3 → v3 = 0
- k 偶数: 2^k ≡ 1 mod 3 → -2^k ≡ 2 mod 3 → v3 = 0

あれ? v3 = 0 になるはず... でも計算結果は v3 >= 1!
これは 3^k の 3^1 を括り出すと:
3^k - 2^k = 3 * 3^{k-1} - 2^k
k=1: 3 - 2 = 1, v3(1) = 0 ← 矛盾!
""")

# 再検算
print("再検算:")
for k in range(1, 10):
    val = 3**k - 2**k
    print(f"  k={k}: 3^{k}-2^{k} = {3**k}-{2**k} = {val}, v3({val}) = {v3(val)}")

# === Part 4: 正確な v3 パターンの理論 ===
print("\n" + "=" * 70)
print("Part 4: v3(3^k - 2^k) の正確な理論")
print("=" * 70)

# k=1: 3-2=1, v3=0
# k=2: 9-4=5, v3=0
# k=3: 27-8=19, v3=0
# k=4: 81-16=65, v3=0
# k=5: 243-32=211, v3=0
# k=6: 729-64=665, v3=0

# 全て v3=0 のはず! 確認
print("v3(3^k - 2^k) を正確に再計算:")
all_zero = True
non_zero_ks = []
for k in range(1, 201):
    val = 3**k - 2**k
    v = v3(val)
    if v != 0:
        all_zero = False
        non_zero_ks.append((k, v))
        print(f"  [非ゼロ] k={k}: v3(3^k-2^k) = v3({val}) = {v}")

if all_zero:
    print("  全て v3 = 0 (k=1..200)")

if non_zero_ks:
    print(f"\n  非ゼロの個数: {len(non_zero_ks)}")
else:
    print("\n結論: v3(3^k - 2^k) = 0 for all k >= 1")
    print("理由: 3^k ≡ 0 mod 3, 2^k ≢ 0 mod 3 なので 3^k - 2^k ≡ -2^k ≢ 0 mod 3")

# === Part 5: サイクル方程式の3-adic解析 ===
print("\n" + "=" * 70)
print("Part 5: サイクル方程式 n(2^s - 3^p) = Σ3^i·2^{a_i} の3-adic解析")
print("=" * 70)

print("""
サイクル方程式: Syracuse のp回の上昇ステップ、合計s回の2除算で元に戻る場合:
  n * (2^s - 3^p) = Σ_{i=0}^{p-1} 3^i * 2^{a_i}  ... (*)

ここで a_0 > a_1 > ... > a_{p-1} >= 0 (各ステップでの2の累乗)

サイクルが存在するには:
  1. 2^s > 3^p (n > 0 の場合) → s > p * log_2(3) ≈ 1.585*p
  2. n は正の奇数
  3. a_i は各ステップの v2(3*n_i+1)

右辺の3-adic評価を分析する:
""")

# 右辺 Σ_{i=0}^{p-1} 3^i * 2^{a_i} の v3 を計算
# v3(Σ 3^i * 2^{a_i}) = v3(2^{a_0} + 3·2^{a_1} + 9·2^{a_2} + ...)
# = v3(2^{a_0}) + ... いや、これは和なので単純ではない
# 最小のiに対応する項が支配的: v3 = 0 (i=0の項が3で割れないため)

print("右辺の3-adic valuation:")
print("  RHS = 2^{a_0} + 3·2^{a_1} + 9·2^{a_2} + ...")
print("  i=0の項: 3^0 · 2^{a_0} = 2^{a_0}")
print("  v3(2^{a_0}) = 0")
print("  残りの項は全て 3 の倍数")
print("  よって v3(RHS) = v3(2^{a_0} + 3M) = 0 (2^{a_0}は3で割れない)")
print()

# 左辺の解析
print("左辺 n(2^s - 3^p) の3-adic valuation:")
print("  v3(LHS) = v3(n) + v3(2^s - 3^p)")
print()

# v3(2^s - 3^p) の計算
print("v3(2^s - 3^p) を計算:")
print(f"{'s':>4} {'p':>4} | {'2^s - 3^p':>20} | {'v3':>4} | {'s/p':>8}")
print("-" * 55)

# s/p > log_2(3) ≈ 1.585 が必要
for p in range(1, 15):
    s_min = int(p * math.log2(3)) + 1
    for s in range(s_min, s_min + 5):
        diff = 2**s - 3**p
        if diff > 0:
            v = v3(diff)
            print(f"{s:>4} {p:>4} | {diff:>20} | {v:>4} | {s/p:>8.4f}")

# === Part 6: v3(2^s - 3^p) の詳細パターン ===
print("\n" + "=" * 70)
print("Part 6: v3(2^s - 3^p) の詳細パターン")
print("=" * 70)

print("2^s ≡ 3^p mod 3 の解析:")
print("  2^s mod 3: s偶→1, s奇→2")
print("  3^p mod 3 = 0 (p>=1)")
print("  よって 2^s - 3^p ≡ 2^s mod 3")
print("  2^s mod 3 ≠ 0 なので v3(2^s - 3^p) = 0 (p>=1)")
print()

# 確認
print("確認: v3(2^s - 3^p) for p >= 1:")
all_zero_v3 = True
for p in range(1, 20):
    for s in range(1, 50):
        diff = 2**s - 3**p
        if diff > 0:
            v = v3(diff)
            if v != 0:
                all_zero_v3 = False
                print(f"  [非ゼロ!] s={s}, p={p}: v3(2^s - 3^p) = {v}")

if all_zero_v3:
    print("  全て v3 = 0 確認済み (p=1..19, s=1..49, 2^s > 3^p)")

# === Part 7: サイクル方程式の帰結 ===
print("\n" + "=" * 70)
print("Part 7: サイクル排除への帰結")
print("=" * 70)

print("""
【定理】サイクル方程式 (*) の3-adic解析

サイクル方程式: n(2^s - 3^p) = Σ_{i=0}^{p-1} 3^i · 2^{a_i}

左辺の3-adic valuation:
  v3(LHS) = v3(n) + v3(2^s - 3^p) = v3(n) + 0 = v3(n)
  (p >= 1 では v3(2^s - 3^p) = 0 が成立)

右辺の3-adic valuation:
  v3(RHS) = 0
  (i=0の項 2^{a_0} が3と互いに素なため)

よって v3(n) = 0、すなわちサイクル上の値 n は 3 で割り切れない。

これは既知の結果を再導出している:
  コラッツサイクル上の奇数は全て 3 で割れない (n ≡ 1 or 2 mod 3)
""")

# === Part 8: より細かい分析 - mod 9 ===
print("=" * 70)
print("Part 8: mod 9 (3^2) での解析")
print("=" * 70)

print("\n2^s mod 9 の周期:")
for s in range(20):
    print(f"  2^{s} mod 9 = {pow(2, s, 9)}", end="")
    if s > 0 and pow(2, s, 9) == 2:
        print(f"  ← 周期は {s} (ord_9(2) = {s})")
        ord9 = s
        break
    print()

print(f"\n2 の位数 mod 9 = {ord9}")
print(f"2 の位数 mod 27 = ?")
for s in range(1, 100):
    if pow(2, s, 27) == 1:
        print(f"2 の位数 mod 27 = {s}")
        ord27 = s
        break

for s in range(1, 200):
    if pow(2, s, 81) == 1:
        print(f"2 の位数 mod 81 = {s}")
        ord81 = s
        break

for s in range(1, 500):
    if pow(2, s, 243) == 1:
        print(f"2 の位数 mod 243 = {s}")
        ord243 = s
        break

print(f"\nord_{{3^j}}(2) の列: {[ord9, ord27, ord81, ord243]}")
print(f"比率: {ord27/ord9}, {ord81/ord27}, {ord243/ord81}")

# === Part 9: 2^s ≡ 3^p mod 9 の解析 ===
print("\n" + "=" * 70)
print("Part 9: 2^s ≡ 3^p mod 9 の条件")
print("=" * 70)

print("\n3^p mod 9:")
for p in range(10):
    print(f"  3^{p} mod 9 = {pow(3, p, 9)}")

print(f"\np >= 2 のとき 3^p ≡ 0 mod 9")
print(f"p = 1 のとき 3^p ≡ 3 mod 9")
print(f"p = 0 のとき 3^p ≡ 1 mod 9")

print("\n2^s - 3^p mod 9 (p >= 2):")
print("  2^s mod 9 の繰り返し: ", [pow(2, s, 9) for s in range(ord9)])
print("  2^s - 0 mod 9 = 2^s mod 9")
print("  これが 0 mod 9 になるには 2^s ≡ 0 mod 9 が必要だが、gcd(2,9)=1 なので不可能")
print("  よって p >= 2 のとき v3(2^s - 3^p) = v3(2^s mod 9 * ...) = 1 (exactly)")

# 実際の v3 を p >= 2 で確認
print("\nv3(2^s - 3^p) for p >= 2:")
v3_vals_p2plus = []
for p in range(2, 15):
    for s in range(int(p * 1.585) + 1, int(p * 1.585) + 6):
        diff = 2**s - 3**p
        if diff > 0:
            v = v3(diff)
            v3_vals_p2plus.append((s, p, v))
            if v != 1:
                print(f"  [v3≠1] s={s}, p={p}: v3 = {v}, 2^s-3^p = {diff}")

# 全て v3=1 か確認
all_one = all(v == 1 for _, _, v in v3_vals_p2plus)
if all_one:
    print("  p >= 2, 2^s > 3^p の範囲で全て v3 = 1")
else:
    v3_counter = Counter(v for _, _, v in v3_vals_p2plus)
    print(f"  v3の分布: {dict(v3_counter)}")
    for s, p, v in v3_vals_p2plus:
        if v >= 2:
            print(f"    s={s}, p={p}: v3 = {v}")

# === Part 10: v3(2^s - 3^p) のより広い範囲での計算 ===
print("\n" + "=" * 70)
print("Part 10: v3(2^s - 3^p) の広範囲計算")
print("=" * 70)

max_p = 50
results = []
for p in range(2, max_p + 1):
    s_min = int(p * math.log2(3)) + 1
    for s in range(s_min, s_min + 20):
        diff = 2**s - 3**p
        if diff > 0:
            v = v3(diff)
            results.append((s, p, v))
            if v >= 2:
                print(f"  v3 >= 2: s={s}, p={p}, v3={v}, s mod {ord9}={s%ord9}, p mod ?")

# v3(2^s - 3^p) の正確な理論
print("\n" + "=" * 70)
print("Part 11: v3(2^s - 3^p) の正確な公式導出 (p >= 2)")
print("=" * 70)

print("""
a = 2^s, b = 3^p として:
  v3(2^s - 3^p) = v3(2^s) + v3(1 - 3^p/2^s) ... これは整数でない場合意味がない

別のアプローチ:
  2^s - 3^p mod 3 = 2^s mod 3 ≠ 0 (gcd(2,3)=1)

  えっ? でも p >= 2 で 3^p mod 3 = 0 で...

正しい計算:
  2^s - 3^p (mod 3)
  = 2^s - 0 (mod 3)  [∵ p >= 1 なら 3 | 3^p]
  = 2^s (mod 3)
  ≠ 0 (mod 3)  [∵ gcd(2,3) = 1]

つまり v3(2^s - 3^p) = 0 for p >= 1!

これは正しいのか? 再確認...
""")

print("再確認: 具体値")
for p in range(2, 8):
    s = int(p * math.log2(3)) + 1
    diff = 2**s - 3**p
    print(f"  p={p}, s={s}: 2^{s}-3^{p} = {2**s}-{3**p} = {diff}")
    print(f"    {diff} mod 3 = {diff % 3}")
    print(f"    v3({diff}) = {v3(diff)}")

# === Part 12: サイクル方程式の最終的な帰結 ===
print("\n" + "=" * 70)
print("Part 12: 最終結論")
print("=" * 70)

print("""
【確定事実】
1. v3(3^k - 2^k) = 0 for all k >= 1
   証明: 3^k ≡ 0 mod 3, 2^k ≢ 0 mod 3
   よって 3^k - 2^k ≡ -2^k ≢ 0 mod 3

2. v3(2^s - 3^p) = 0 for all p >= 1
   証明: 同様に 2^s - 3^p ≡ 2^s ≢ 0 mod 3

3. ascentConst(k) = 3^k - 2^k は3で割り切れない (v3 = 0)

【サイクル方程式 n(2^s - 3^p) = Σ 3^i · 2^{a_i} への応用】

v3で両辺を比較:
  左辺: v3(n) + v3(2^s - 3^p) = v3(n) + 0 = v3(n)
  右辺: v3(Σ 3^i · 2^{a_i}) = 0 (i=0の項が支配)

結論: v3(n) = 0 (サイクル上の n は 3 で割れない)

【3^2 での解析】
n(2^s - 3^p) mod 9 を調べる:
""")

# mod 9 解析
print("2^s mod 9 の完全表:")
for s in range(ord9):
    print(f"  2^{s} ≡ {pow(2, s, 9)} mod 9")

print(f"\nサイクル方程式 mod 9:")
print(f"  左辺: n · 2^s mod 9  (∵ 3^p ≡ 0 mod 9 for p >= 2)")
print(f"  右辺: 2^{{a_0}} + 3·2^{{a_1}} mod 9  (∵ 3^i·2^{{a_i}} ≡ 0 mod 9 for i >= 2)")
print()

# n · 2^s ≡ 2^{a_0} + 3·2^{a_1} mod 9 の制約
print("制約方程式 mod 9: n · 2^s ≡ 2^{a_0} + 3·2^{a_1} (mod 9)")
print("右辺の取りうる値 mod 9:")
rhs_mod9 = set()
for a0_mod in range(ord9):
    for a1_mod in range(ord9):
        val = (pow(2, a0_mod, 9) + 3 * pow(2, a1_mod, 9)) % 9
        rhs_mod9.add(val)
print(f"  右辺 mod 9 の可能な値: {sorted(rhs_mod9)}")
print(f"  (p >= 2 の場合)")

# 各値の実現可能な組み合わせ
print("\n右辺の各 mod 9 値の実現パターン:")
for target in sorted(rhs_mod9):
    combos = []
    for a0_mod in range(ord9):
        for a1_mod in range(ord9):
            val = (pow(2, a0_mod, 9) + 3 * pow(2, a1_mod, 9)) % 9
            if val == target:
                combos.append((a0_mod, a1_mod))
    print(f"  RHS ≡ {target} mod 9: (a0 mod {ord9}, a1 mod {ord9}) = {combos}")

# n mod 9 の制約
print("\nn mod 9 と s mod 6 の制約表:")
print("  (n が奇数かつ 3 で割れないので n mod 9 ∈ {1,2,4,5,7,8})")
for n_mod in [1, 2, 4, 5, 7, 8]:
    for s_mod in range(ord9):
        lhs_mod9 = (n_mod * pow(2, s_mod, 9)) % 9
        if lhs_mod9 in rhs_mod9:
            possible = "可能"
        else:
            possible = "不可能!"
        # 表示は制約が厳しい場合のみ
        if possible == "不可能!":
            print(f"  n≡{n_mod} mod 9, s≡{s_mod} mod {ord9}: n·2^s ≡ {lhs_mod9} mod 9 → {possible}")

print("\n全ての (n mod 9, s mod 6) は RHS の可能な値と一致する")
print("(mod 9 での追加排除は得られない)")

# === Part 13: より高い3のべきでの解析 ===
print("\n" + "=" * 70)
print("Part 13: mod 27 での解析")
print("=" * 70)

print(f"ord_27(2) = {ord27}")
print(f"\nサイクル方程式 mod 27 (p >= 3 の場合):")
print(f"  左辺: n · 2^s mod 27")
print(f"  右辺: 2^{{a_0}} + 3·2^{{a_1}} + 9·2^{{a_2}} mod 27")

rhs_mod27 = set()
for a0 in range(ord27):
    for a1 in range(ord27):
        for a2 in range(ord27):
            val = (pow(2, a0, 27) + 3 * pow(2, a1, 27) + 9 * pow(2, a2, 27)) % 27
            rhs_mod27.add(val)

print(f"  右辺 mod 27 の可能な値: {sorted(rhs_mod27)} ({len(rhs_mod27)}個)")
print(f"  mod 27 の 3 と互いに素な値の総数: {len([x for x in range(27) if math.gcd(x,3)==1])}")

# n · 2^s の可能な値 mod 27
lhs_mod27 = set()
for n_mod in range(27):
    if n_mod % 2 == 1 and n_mod % 3 != 0 and n_mod > 0:  # 奇数かつ3で割れない
        for s_mod in range(ord27):
            val = (n_mod * pow(2, s_mod, 27)) % 27
            lhs_mod27.add(val)

print(f"  左辺 mod 27 の可能な値: {sorted(lhs_mod27)} ({len(lhs_mod27)}個)")

excluded = lhs_mod27 - rhs_mod27
if excluded:
    print(f"  排除される左辺の値: {sorted(excluded)}")
else:
    print(f"  mod 27 でも追加の排除なし")

# 密度解析
print("\n密度解析: RHS mod 3^j で可能な値の割合")
for j in range(1, 5):
    modulus = 3**j
    # ordを計算
    for s in range(1, 3**j * 10):
        if pow(2, s, modulus) == 1:
            ord_j = s
            break

    # 右辺の可能な値を計算(最初のj項のみ)
    # これは組合せ爆発するので近似
    print(f"  mod 3^{j} = {modulus}: ord(2) = {ord_j}")

print("\n" + "=" * 70)
print("Part 14: ascentConst(k) の mod 解析サマリー")
print("=" * 70)

for k in range(1, 21):
    ac = 3**k - 2**k
    print(f"  ascentConst({k:2d}) = {ac:>10}, mod 3 = {ac%3}, mod 9 = {ac%9}, mod 27 = {ac%27}, mod 81 = {ac%81}")

# ascentConst(k) mod 3 のパターン
print("\nascentConst(k) mod 3 = (-2^k) mod 3:")
print("  k奇数: 2^k ≡ 2 mod 3 → -2^k ≡ 1 mod 3")
print("  k偶数: 2^k ≡ 1 mod 3 → -2^k ≡ 2 mod 3")

# ascentConst(k) mod 9
print("\nascentConst(k) mod 9 = (-2^k) mod 9 = (9 - 2^k mod 9) mod 9:")
for k in range(1, 13):
    print(f"  k={k}: 2^{k} mod 9 = {pow(2,k,9)}, ascentConst mod 9 = {(3**k - 2**k) % 9} = {(- pow(2,k,9)) % 9}")
