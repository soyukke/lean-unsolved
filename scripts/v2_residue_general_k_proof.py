"""
v2(3n+1) = j の正確な残基条件の一般k証明設計

目標: v2(3n+1) = j ⟺ n ≡ r_j (mod 2^{j+1})
ここで r_j = (2^j - 1) * 3^{-1} mod 2^{j+1}

探索138の発見: collatzResidue(k) = (4^{ceil(k/2)} - 1) / 3
これは v2(3n+1) >= k の条件。

本探索では:
1. v2(3n+1) = j (正確な等号) の条件を完全に特定
2. 一般kの帰納法による証明設計
3. Lean形式化の具体的なステップ
"""

import math
from typing import List, Tuple

# ==== Part 1: 基本的な検証 ====

def v2(n: int) -> int:
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def mod_inv_pow2(a: int, k: int) -> int:
    """a^{-1} mod 2^k (aが奇数のとき)"""
    mod = 2**k
    # 拡張ユークリッドの互除法
    return pow(a, -1, mod)

print("=" * 70)
print("Part 1: v2(3n+1) = j の残基条件テーブル")
print("=" * 70)

# j=1,...,10 について v2(3n+1)=j となる最小の奇数nと剰余類を調べる
for j in range(1, 11):
    mod = 2**(j+1)
    residues = []
    for r in range(1, mod, 2):  # 奇数のみ
        if v2(3*r + 1) == j:
            residues.append(r)

    # 理論値: r_j = (2^j - 1) * 3^{-1} mod 2^{j+1}
    inv3 = mod_inv_pow2(3, j+1)
    r_j_theory = ((2**j - 1) * inv3) % mod

    print(f"j={j}: v2(3n+1)=j の残基 mod {mod}: {residues}")
    print(f"  理論値 r_j = (2^{j}-1)*3^{{-1}} mod 2^{j+1} = {r_j_theory}")
    print(f"  一致: {residues == [r_j_theory]}")

print()

# ==== Part 2: 3^{-1} mod 2^k の系列 ====
print("=" * 70)
print("Part 2: 3^{-1} mod 2^k の系列")
print("=" * 70)

for k in range(1, 16):
    inv3 = mod_inv_pow2(3, k)
    print(f"  3^{{-1}} mod 2^{k:2d} = {inv3:6d}  (= {inv3} mod {2**k})")

print()

# ==== Part 3: r_j = (2^j - 1) / 3 の閉形式 ====
print("=" * 70)
print("Part 3: r_j の閉形式分析")
print("=" * 70)

# (2^j - 1) * 3^{-1} mod 2^{j+1} を別の方法で計算
# 注意: 2^j - 1 は (j >= 1のとき) 奇数
# 3 * r_j ≡ 2^j - 1 (mod 2^{j+1})
# つまり 3*r_j + 1 ≡ 2^j (mod 2^{j+1})
# つまり 3*r_j + 1 = 2^j + m * 2^{j+1} (ある整数m)
# つまり v2(3*r_j + 1) = j (mが奇数のとき)

for j in range(1, 16):
    mod = 2**(j+1)
    inv3 = mod_inv_pow2(3, j+1)
    r_j = ((2**j - 1) * inv3) % mod

    # 検証: 3*r_j + 1 が 2^j で割り切れるが 2^{j+1} で割り切れない
    val = 3 * r_j + 1
    v2_val = v2(val)

    # collatzResidue(k) = (4^{ceil(k/2)} - 1) / 3 との比較
    ck = (4**math.ceil(j/2) - 1) // 3

    # r_j のバイナリ表現
    binary = bin(r_j)[2:]

    print(f"j={j:2d}: r_j = {r_j:8d} (binary: {binary:>20s}), "
          f"3*r_j+1 = {val:8d}, v2 = {v2_val}, "
          f"collatzResidue = {ck}")

print()

# ==== Part 4: v2(3n+1) >= j と v2(3n+1) = j の関係 ====
print("=" * 70)
print("Part 4: v2(3n+1)>=j vs v2(3n+1)=j の残基条件")
print("=" * 70)

for j in range(1, 8):
    mod_ge = 2**j  # v2 >= j の法
    mod_eq = 2**(j+1)  # v2 = j の法

    # v2(3n+1) >= j の残基 (mod 2^j)
    res_ge = []
    for r in range(1, mod_ge, 2):
        if v2(3*r + 1) >= j:
            res_ge.append(r)

    # v2(3n+1) = j の残基 (mod 2^{j+1})
    res_eq = []
    for r in range(1, mod_eq, 2):
        if v2(3*r + 1) == j:
            res_eq.append(r)

    # v2(3n+1) >= j+1 の残基 (mod 2^{j+1})
    res_ge_next = []
    for r in range(1, mod_eq, 2):
        if v2(3*r + 1) >= j+1:
            res_ge_next.append(r)

    ck = (4**math.ceil(j/2) - 1) // 3
    ck1 = (4**math.ceil((j+1)/2) - 1) // 3

    print(f"j={j}:")
    print(f"  v2>=j  mod {mod_ge:4d}: {res_ge} (collatzResidue={ck})")
    print(f"  v2=j   mod {mod_eq:4d}: {res_eq}")
    print(f"  v2>=j+1 mod {mod_eq:4d}: {res_ge_next} (collatzResidue={ck1})")
    print(f"  関係: v2=j の残基 = v2>=j を mod {mod_eq} に持ち上げ \\ v2>=j+1")

print()

# ==== Part 5: Hensel lifting の核心 ====
print("=" * 70)
print("Part 5: Hensel lifting の帰納ステップ詳細")
print("=" * 70)

print("\nv2(3n+1)>=j の条件を v2(3n+1)>=j+1 に持ち上げる過程:")
print()

for j in range(1, 8):
    mod_j = 2**j
    mod_j1 = 2**(j+1)

    # v2(3n+1) >= j の唯一の残基 mod 2^j
    inv3_j = mod_inv_pow2(3, j)
    r_ge_j = ((2**j - 1) * inv3_j) % mod_j

    # v2(3n+1) >= j+1 の唯一の残基 mod 2^{j+1}
    inv3_j1 = mod_inv_pow2(3, j+1)
    r_ge_j1 = ((2**(j+1) - 1) * inv3_j1) % mod_j1

    # r_ge_j の2つのリフト
    lift_0 = r_ge_j
    lift_1 = r_ge_j + mod_j

    # どちらが v2 >= j+1 を満たすか
    v2_lift0 = v2(3 * lift_0 + 1)
    v2_lift1 = v2(3 * lift_1 + 1)

    print(f"j={j}: 残基 mod 2^{j} = {r_ge_j}")
    print(f"  リフト0: n ≡ {lift_0} (mod {mod_j1}) -> v2(3*{lift_0}+1) = v2({3*lift_0+1}) = {v2_lift0}")
    print(f"  リフト1: n ≡ {lift_1} (mod {mod_j1}) -> v2(3*{lift_1}+1) = v2({3*lift_1+1}) = {v2_lift1}")
    print(f"  v2=j: {lift_0 if v2_lift0 == j else lift_1}  (v2 exactly {j})")
    print(f"  v2>=j+1: {lift_0 if v2_lift0 >= j+1 else lift_1}")
    print()

# ==== Part 6: 核心的等式の証明要素 ====
print("=" * 70)
print("Part 6: 核心的等式と証明構造")
print("=" * 70)

print()
print("核心的定理:")
print("  v2(3n+1) >= j ⟺ n ≡ c_j (mod 2^j)")
print("  ここで c_j は唯一の奇数残基で 3*c_j + 1 ≡ 0 (mod 2^j)")
print()
print("帰納法のステップ:")
print("  v2(3n+1) >= j を仮定 ⟹ n = c_j + q * 2^j (qは整数)")
print("  3n + 1 = 3*c_j + 1 + 3*q*2^j = 2^j * (a + 3*q)")
print("  ここで a = (3*c_j + 1) / 2^j")
print()
print("  v2(3n+1) >= j+1 ⟺ a + 3*q ≡ 0 (mod 2)")
print("  aが奇数なら q が奇数のとき、aが偶数なら q が偶数のとき")
print()

# aの偶奇パターン
for j in range(1, 12):
    mod_j = 2**j
    inv3_j = mod_inv_pow2(3, j)
    c_j = ((mod_j - 1) * inv3_j) % mod_j
    if c_j % 2 == 0:
        c_j += mod_j  # 奇数にする（ただし mod 2*mod_j で考える）

    a_j = (3 * c_j + 1) // mod_j
    print(f"  j={j:2d}: c_j = {c_j:6d}, a_j = (3*{c_j}+1)/{mod_j} = {a_j}, "
          f"a_j mod 2 = {a_j % 2}")

print()

# ==== Part 7: collatzResidue の再帰的構造 ====
print("=" * 70)
print("Part 7: collatzResidue の再帰関係")
print("=" * 70)

def collatz_residue(k: int) -> int:
    """collatzResidue(k) = (4^{ceil(k/2)} - 1) / 3"""
    return (4**math.ceil(k/2) - 1) // 3

print()
print("collatzResidue(k) と v2 >= k の残基条件:")
for k in range(1, 13):
    ck = collatz_residue(k)
    mod_k = 2**k
    # 検証
    v2_val = v2(3*ck + 1)
    # ck mod 2^k
    ck_mod = ck % mod_k
    print(f"  k={k:2d}: collatzResidue = {ck:6d}, mod 2^k = {ck_mod:6d}, "
          f"v2(3*{ck}+1) = {v2_val}, 3*ck+1 = {3*ck+1}")

print()

# 再帰関係の検証
print("再帰関係:")
print("  collatzResidue(1) = 1")
print("  collatzResidue(k+1) = ?")
for k in range(1, 11):
    ck = collatz_residue(k)
    ck1 = collatz_residue(k+1)
    diff = ck1 - ck
    print(f"  c({k+1}) = c({k}) + {diff} = {ck} + {diff} = {ck1}, "
          f"diff/2^k = {diff / 2**k}")

print()

# ==== Part 8: 正確な v2=j 条件の閉形式 ====
print("=" * 70)
print("Part 8: v2(3n+1)=j の正確な残基条件")
print("=" * 70)

print()
print("v2(3n+1) = j の残基 r_j (mod 2^{j+1}):")
for j in range(1, 13):
    mod = 2**(j+1)
    # v2(3n+1) = j の残基
    res_eq = None
    for r in range(1, mod, 2):
        if v2(3*r + 1) == j:
            res_eq = r
            break

    # v2 >= j の残基 c_j (mod 2^j)
    c_j = collatz_residue(j) % (2**j)

    # v2 >= j+1 の残基 c_{j+1} (mod 2^{j+1})
    c_j1 = collatz_residue(j+1) % (2**(j+1))

    # r_j は c_j の2つのリフトのうち c_{j+1} でないほう
    lift_0 = c_j
    lift_1 = c_j + 2**j

    if lift_0 == c_j1:
        r_j_computed = lift_1
    else:
        r_j_computed = lift_0

    # r_j の閉形式
    # r_j = collatzResidue(j) + 2^j if c_{j+1} = c_j
    #      = collatzResidue(j)      if c_{j+1} = c_j + 2^j

    print(f"  j={j:2d}: r_j = {res_eq:6d}, "
          f"computed = {r_j_computed:6d}, "
          f"c_j={c_j:6d}, c_{{j+1}}={c_j1:6d}, "
          f"match: {res_eq == r_j_computed}")

print()

# ==== Part 9: Lean証明のブループリント ====
print("=" * 70)
print("Part 9: Lean形式化のブループリント")
print("=" * 70)

print("""
Lean形式化の6段階設計:

Stage 1: collatzResidue の定義
  def collatzResidue : Nat -> Nat
    | 0 => 0
    | k + 1 => if k % 2 = 0 then 4 * collatzResidue k + 1
               else collatzResidue k + 2^k

  あるいは閉形式:
    collatzResidue k = (4^(Nat.div2 k + k % 2) - 1) / 3
    = (4^{ceil(k/2)} - 1) / 3

Stage 2: 核心等式
  theorem core_identity (k : Nat) (hk : k >= 1) :
    3 * collatzResidue k + 1 = 2^k * (something odd or even)

  より正確に:
    3 * collatzResidue k + 1 = 4^{ceil(k/2)}
    = 2^{2*ceil(k/2)}
    = 2^k * 2^{ceil(k/2) - floor(k/2)}  (kが奇数なら 2^k * 2, kが偶数なら 2^k * 1)

Stage 3: v2(3n+1) >= k の必要十分条件
  theorem v2_ge_iff_mod (n k : Nat) (hodd : n % 2 = 1) :
    v2 (3*n+1) >= k <-> n % 2^k = collatzResidue k % 2^k

  帰納法で証明:
  - 基底: k=0 は自明 (v2 >= 0 は常に真)
  - ステップ: k -> k+1
    v2(3n+1) >= k+1
    <-> 2^{k+1} | (3n+1)
    <-> 2^k | (3n+1) かつ (3n+1)/2^k は偶数
    <-> n % 2^k = c_k かつ (追加条件)

Stage 4: v2(3n+1) = j の正確な条件
  theorem v2_eq_iff_mod (n j : Nat) (hodd : n % 2 = 1) (hj : j >= 1) :
    v2 (3*n+1) = j <-> n % 2^{j+1} = r_j

  ここで r_j は collatzResidue(j) を 2^{j+1} でリフトして
  v2 >= j+1 の残基でない方

Stage 5: Hensel lifting補題
  theorem hensel_lift (k : Nat) :
    collatzResidue (k+1) % 2^k = collatzResidue k % 2^k

  つまり上位ビットの追加による持ち上げ

Stage 6: 主定理の統合
  v2_of_mod8_eq1, v2_of_mod8_eq3 等の既存定理が
  一般定理の特殊ケースとして回収される
""")

# ==== Part 10: Lean 証明の具体的難所 ====
print("=" * 70)
print("Part 10: 証明の核心的難所の分析")
print("=" * 70)

# 最も重要な等式: 3 * collatzResidue(k) + 1 = 4^{ceil(k/2)}
print()
print("核心等式の検証: 3 * collatzResidue(k) + 1 = 4^{ceil(k/2)}")
for k in range(0, 15):
    ck = collatz_residue(k)
    lhs = 3 * ck + 1
    rhs = 4**math.ceil(k/2)
    print(f"  k={k:2d}: 3*{ck:6d}+1 = {lhs:6d}, 4^{math.ceil(k/2):d} = {rhs:6d}, match: {lhs == rhs}")

print()

# collatzResidue の漸化式パターン
print("collatzResidue の漸化式:")
print("  偶数k -> k+1 (奇数): c(k+1) = c(k) + 2^k")
print("  奇数k -> k+1 (偶数): c(k+1) = 4*c(k) + 1")
for k in range(0, 12):
    ck = collatz_residue(k)
    ck1 = collatz_residue(k+1)
    if k % 2 == 0:
        # k偶数 -> k+1奇数
        expected = ck + 2**k
        print(f"  k={k:2d}(even): c({k+1}) = c({k}) + 2^{k} = {ck} + {2**k} = {expected}, actual = {ck1}, match: {expected == ck1}")
    else:
        # k奇数 -> k+1偶数
        expected = 4 * ck + 1
        print(f"  k={k:2d}(odd):  c({k+1}) = 4*c({k}) + 1 = 4*{ck} + 1 = {expected}, actual = {ck1}, match: {expected == ck1}")

print()

# ==== Part 11: 漸化式の証明 ====
print("=" * 70)
print("Part 11: 漸化式の証明構造")
print("=" * 70)

print("""
漸化式 (重要な2パターン):

Case A: k偶数 (k = 2m)
  c(2m+1) = c(2m) + 2^{2m}
  証明: c(2m) = (4^m - 1)/3
         c(2m+1) = (4^{m+1} - 1)/3
         差 = (4^{m+1} - 4^m)/3 = 4^m * (4-1)/3 = 4^m = (2^2)^m = 2^{2m}

Case B: k奇数 (k = 2m+1)
  c(2m+2) = 4*c(2m+1) + 1
  証明: c(2m+1) = (4^{m+1} - 1)/3
         4*c(2m+1) + 1 = 4*(4^{m+1}-1)/3 + 1 = (4^{m+2}-4+3)/3 = (4^{m+2}-1)/3
         = c(2m+2)

Lean での表現:
  theorem collatzResidue_even_step (m : Nat) :
    collatzResidue (2*m + 1) = collatzResidue (2*m) + 2^(2*m)

  theorem collatzResidue_odd_step (m : Nat) :
    collatzResidue (2*m + 2) = 4 * collatzResidue (2*m + 1) + 1

代替の漸化式定義:
  def collatzResidue' : Nat -> Nat
    | 0 => 0
    | 1 => 1
    | k + 2 => 4 * collatzResidue' (k + 1) + 2^k + 1

  しかしこれは証明しにくい。2ステップ漸化式のほうが良い:

  def collatzResidue : Nat -> Nat
    | 0 => 0
    | 1 => 1
    | k + 2 => 4 * collatzResidue k + (2^k + 1)  -- ??? 要検証
""")

# 2ステップ漸化式の検証
print("2ステップ漸化式 c(k+2) = 4*c(k) + 2^k + 1 の検証:")
for k in range(0, 10):
    ck = collatz_residue(k)
    ck2 = collatz_residue(k+2)
    expected = 4 * ck + 2**k + 1
    print(f"  c({k+2}) = 4*c({k}) + 2^{k} + 1 = 4*{ck} + {2**k+1} = {expected}, "
          f"actual = {ck2}, match: {expected == ck2}")

print()

# ==== Part 12: Lean定義の最終設計 ====
print("=" * 70)
print("Part 12: Lean定義の最終設計案")
print("=" * 70)

print("""
推奨定義 (Lean 4):

-- 方法1: 閉形式 (ceil(k/2)を使う)
def collatzResidue (k : Nat) : Nat :=
  (4 ^ ((k + 1) / 2) - 1) / 3

-- 注意: Nat.div2 の使用は微妙。(k+1)/2 = ceil(k/2) in Nat division

-- 方法2: 明示的な2ステップ漸化式 (Lean向き)
def collatzResidue : Nat -> Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => 4 * collatzResidue n + 2^n + 1

-- 核心定理:
theorem collatzResidue_closed (k : Nat) :
  collatzResidue k = (4 ^ ((k + 1) / 2) - 1) / 3

-- v2条件 (≥バージョン):
theorem v2_ge_iff (n k : Nat) (hodd : n % 2 = 1) (hk : k >= 1) :
  v2 (3 * n + 1) >= k <-> n % 2^k = collatzResidue k % 2^k

-- v2条件 (=バージョン):
-- r_j(v2=j) は 2つのリフトの一方
theorem v2_eq_iff (n j : Nat) (hodd : n % 2 = 1) (hj : j >= 1) :
  v2 (3 * n + 1) = j <->
    n % 2^(j+1) = collatzResidue j % 2^(j+1) /\\
    n % 2^(j+1) != collatzResidue (j+1) % 2^(j+1)

-- または同値的に:
-- v2(3n+1) = j <-> v2(3n+1) >= j /\\ ~(v2(3n+1) >= j+1)
-- <-> n % 2^j = c_j % 2^j /\\ n % 2^{j+1} != c_{j+1} % 2^{j+1}
""")

# 方法2の漸化式定義と閉形式の一致検証
print("方法2の2ステップ漸化式 c(n+2) = 4*c(n) + 2^n + 1 の最終検証:")
def cr_recursive(n):
    if n == 0: return 0
    if n == 1: return 1
    return 4 * cr_recursive(n-2) + 2**(n-2) + 1

for k in range(0, 15):
    cr = cr_recursive(k)
    ck = collatz_residue(k)
    print(f"  k={k:2d}: recursive = {cr:6d}, closed = {ck:6d}, match: {cr == ck}")

print()
print("=" * 70)
print("総括: 一般k証明の核心要素")
print("=" * 70)
print("""
[核心1] collatzResidue(k) の定義
  - 漸化式: c(0)=0, c(1)=1, c(k+2)=4*c(k)+2^k+1
  - 閉形式: c(k) = (4^{ceil(k/2)}-1)/3

[核心2] 3*c(k)+1 = 4^{ceil(k/2)} = 2^{2*ceil(k/2)}
  → v2(3*c(k)+1) = 2*ceil(k/2) >= k (等号は偶数kのとき)

[核心3] v2(3n+1) >= k ⟺ n ≡ c(k) (mod 2^k)
  → 各 mod 2^k で唯一の奇数残基

[核心4] v2(3n+1) = j ⟺ v2>=j かつ NOT v2>=j+1
  ⟺ n%2^j = c(j)%2^j かつ n%2^{j+1} != c(j+1)%2^{j+1}

[既存定理との接続]
  - v2_of_mod8_eq1: j=2, n%8=1 → v2=2
    c(2)=5, c(2)%4=1 ✓ (n%4=1 ⟺ v2>=2)
    c(3)=5, c(3)%8=5 (n%8=5 ⟺ v2>=3)
    よって v2=2 ⟺ n%4=1 かつ n%8!=5 ⟺ n%8=1

  - v2_of_mod8_eq3: j=1, v2=1 ⟺ v2>=1 かつ NOT v2>=2
    c(1)=1, c(1)%2=1 (n%2=1 ⟺ v2>=1)
    c(2)=5, c(2)%4=1 (n%4=1 ⟺ v2>=2)
    v2=1 ⟺ n%2=1 かつ n%4!=1 ⟺ n%4=3

[Lean証明の推奨順序]
  1. collatzResidue の漸化式定義
  2. 閉形式 = 漸化式の証明
  3. 核心等式 3*c(k)+1 = 4^{ceil(k/2)}
  4. v2(3*c(k)+1) >= k の証明 (核心等式から直接)
  5. v2>=k ⟺ mod条件 の帰納法証明
  6. v2=j 条件の導出 (v2>=j ∧ ¬v2>=j+1)
""")
