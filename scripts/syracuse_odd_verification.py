"""
syracuse_odd の証明可能性を検証するスクリプト

背理法による証明の各ステップを数値的に検証する。
"""

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

print("=" * 60)
print("Syracuse(n) 奇数性の検証")
print("=" * 60)

# 大規模検証
max_n = 100000
print(f"\n[1] syracuse(n) % 2 == 1 検証 (n=1,3,5,...,{max_n-1})")
all_ok = True
for n in range(1, max_n, 2):
    if syracuse(n) % 2 != 1:
        print(f"  反例: n={n}, syracuse(n)={syracuse(n)}")
        all_ok = False
        break
if all_ok:
    print(f"  全{max_n//2}個の奇数で OK")

# 背理法の核心: v2 の maximality
print(f"\n[2] v2 maximality 検証 (m=1,...,{max_n})")
all_ok = True
for m in range(1, max_n + 1):
    v = v2(m)
    if m % (2 ** (v + 1)) == 0:
        print(f"  反例: m={m}, v2(m)={v}, 2^(v+1)={2**(v+1)}")
        all_ok = False
        break
if all_ok:
    print(f"  全{max_n}個で OK: 2^(v2(m)+1) は m を割らない")

# m / 2^v2(m) の奇数性
print(f"\n[3] m / 2^v2(m) % 2 == 1 検証 (m=1,...,{max_n})")
all_ok = True
for m in range(1, max_n + 1):
    q = m // (2 ** v2(m))
    if q % 2 != 1:
        print(f"  反例: m={m}, q={q}")
        all_ok = False
        break
if all_ok:
    print(f"  全{max_n}個で OK")

# 背理法の各ステップの検証
print(f"\n[4] 背理法ステップの具体例検証")
test_cases = [4, 12, 24, 48, 96, 100, 256, 1000]
for m in test_cases:
    v = v2(m)
    q = m // (2 ** v)
    pow_dvd = m % (2 ** v) == 0  # 2^v | m
    q_odd = q % 2 == 1  # q は奇数
    next_pow_not_dvd = m % (2 ** (v + 1)) != 0  # 2^(v+1) ∤ m
    print(f"  m={m:4d}: v2={v}, q=m/2^v={q:4d}, "
          f"2^v|m={pow_dvd}, q%2=1={q_odd}, 2^(v+1)∤m={next_pow_not_dvd}")

print(f"\n[5] 証明に使用する既存定理の一覧")
print("""
  (a) two_pow_v2_dvd (m : Nat) : 2 ^ v2 m | m
      場所: Structure.lean:284

  (b) v2_ge_of_dvd (m k : Nat) (hm : m > 0) (h : 2^k | m) : v2 m >= k
      場所: Structure.lean:291

  (c) Nat.div_mul_cancel (h : d | m) : m / d * d = m
      場所: Lean 4 core (Mathlib)

  (d) Nat.dvd_of_mod_eq_zero : m % d = 0 -> d | m
      場所: Lean 4 core

  (e) Nat.mul_dvd_mul_left (k : Nat) (h : d | m) : k * d | k * m
      場所: Lean 4 core

  (f) Nat.div_pos (h1 : d <= m) (h2 : 0 < d) : 0 < m / d
      場所: Lean 4 core

  (g) Nat.le_of_dvd (h1 : 0 < m) (h2 : d | m) : d <= m
      場所: Lean 4 core
""")

# 2つの方法の比較
print("[6] 方法の比較")
print("""
  方法1 (背理法 + v2_ge_of_dvd):
    利点: 除算の等式変形が不要。全て整除性と omega で閉じる。
    欠点: なし（推奨）

  方法2 (強帰納法 + Nat.mul_div_mul_left):
    利点: 構成的。直接的。
    欠点: Nat.mul_div_mul_left の型シグネチャ確認が必要。
          除算の順序問題がある。

  結論: 方法1を推奨。
""")
