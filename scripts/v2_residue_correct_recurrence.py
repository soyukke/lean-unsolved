"""
collatzResidue の正しい漸化式の特定と証明設計

前のスクリプトで:
- 1ステップ漸化式は kの偶奇で分岐する不正確なパターンだった
- 2ステップ漸化式 c(k+2) = 4*c(k) + 2^k + 1 は不一致

ここでは正しい関係を正確に特定する。
"""

import math

def collatz_residue(k: int) -> int:
    """collatzResidue(k) = (4^{ceil(k/2)} - 1) / 3"""
    return (4**math.ceil(k/2) - 1) // 3

# 重要な観察: c(k) は k と k+1 で同じ値を持つ
# c(0)=0, c(1)=1, c(2)=1, c(3)=5, c(4)=5, c(5)=21, ...
# つまり c(2m) = c(2m+1) ではない!
# c(2m) = (4^m - 1)/3
# c(2m+1) = (4^{m+1} - 1)/3

print("="*70)
print("collatzResidue のペア構造")
print("="*70)

for m in range(0, 8):
    c_even = collatz_residue(2*m)
    c_odd = collatz_residue(2*m + 1)
    print(f"  c({2*m:2d}) = {c_even:6d} = (4^{m} - 1)/3")
    print(f"  c({2*m+1:2d}) = {c_odd:6d} = (4^{m+1} - 1)/3")
    print(f"     差 = {c_odd - c_even} = 4^{m} * 1 = {4**m}")
    print()

print("="*70)
print("正しい1ステップ漸化式")
print("="*70)

# c(2m) -> c(2m+1):  ceil((2m)/2) = m,  ceil((2m+1)/2) = m+1
# c(2m+1) = (4^{m+1}-1)/3, c(2m) = (4^m-1)/3
# c(2m+1) - c(2m) = (4^{m+1} - 4^m)/3 = 4^m
# つまり c(2m+1) = c(2m) + 4^m = c(2m) + 2^{2m}

# c(2m+1) -> c(2m+2): ceil((2m+1)/2) = m+1, ceil((2m+2)/2) = m+1
# c(2m+2) = (4^{m+1}-1)/3 = c(2m+1)
# つまり c(2m+2) = c(2m+1) (同じ!)

print()
print("1ステップ遷移パターン:")
for k in range(0, 16):
    ck = collatz_residue(k)
    ck1 = collatz_residue(k+1)
    diff = ck1 - ck
    if k % 2 == 0:
        m = k // 2
        print(f"  c({k:2d}) -> c({k+1:2d}): {ck:6d} -> {ck1:6d}, "
              f"差 = {diff:6d} = 4^{m} = {4**m}  [k偶数: c += 4^{k//2}]")
    else:
        print(f"  c({k:2d}) -> c({k+1:2d}): {ck:6d} -> {ck1:6d}, "
              f"差 = {diff:6d}  [k奇数: 変化なし]")

print()
print("="*70)
print("重要: c(2m+1) = c(2m+2) つまり奇数kと次の偶数kで同値!")
print("="*70)

print("""
この発見が意味すること:
  v2(3n+1) >= 2m+1  と  v2(3n+1) >= 2m+2  の mod 条件は
  c(2m+1) = c(2m+2) なので、同じ残基条件!

  つまり v2(3n+1) >= 奇数k は自動的に v2(3n+1) >= k+1 (偶数) も意味する
  (同じ残基条件だから)

  これは 3*c(k)+1 = 4^{ceil(k/2)} = 2^{2*ceil(k/2)} から分かる:
  - k = 2m のとき: v2(3*c(k)+1) = 2m = k (ぴったり)
  - k = 2m+1 のとき: v2(3*c(k)+1) = 2m+2 = k+1 (1つ余分!)
""")

# 実際にv2の値を確認
print("v2(3*c(k)+1) の値:")
for k in range(0, 16):
    ck = collatz_residue(k)
    val = 3*ck + 1
    from v2_residue_general_k_proof import v2
    v2_val = v2(val)
    print(f"  k={k:2d}: c(k)={ck:6d}, 3c+1={val:6d}, v2={v2_val:2d}, "
          f"2*ceil(k/2)={2*math.ceil(k/2):2d}, k={k:2d}")

print()
print("="*70)
print("Lean 定義の正しいバージョン")
print("="*70)

print("""
定義方法A: ペア構造を使う
  def collatzResiduePair (m : Nat) : Nat :=
    (4 ^ m - 1) / 3

  -- c(2m) = c(2m+1) = collatzResiduePair m  は不正確
  -- 正しくは:
  -- c(2m)   = (4^m - 1) / 3
  -- c(2m+1) = (4^{m+1} - 1) / 3

定義方法B: 閉形式 (推奨)
  def collatzResidue (k : Nat) : Nat :=
    (4 ^ ((k + 1) / 2) - 1) / 3

  -- Nat除算では (k+1)/2 = ceil(k/2)
  -- k=0: (4^0-1)/3 = 0 ✓  (0+1)/2=0
  -- k=1: (4^1-1)/3 = 1 ✓  (1+1)/2=1
  -- k=2: (4^1-1)/3 = 1 ✓  (2+1)/2=1
  -- k=3: (4^2-1)/3 = 5 ✓  (3+1)/2=2
  -- k=4: (4^2-1)/3 = 5 ✓  (4+1)/2=2
  -- k=5: (4^3-1)/3 = 21 ✓ (5+1)/2=3

定義方法C: 再帰的定義 (Leanでの停止性が自明)
  def collatzResidue : Nat -> Nat
    | 0 => 0
    | n + 1 => if n % 2 = 0 then
                 collatzResidue n + 4 ^ (n / 2)
               else
                 collatzResidue n
""")

# 方法Cの検証
def cr_method_c(k):
    if k == 0: return 0
    n = k - 1  # k = n + 1
    if n % 2 == 0:
        return cr_method_c(n) + 4**(n // 2)
    else:
        return cr_method_c(n)

print("方法C (再帰) の検証:")
for k in range(0, 16):
    cr_c = cr_method_c(k)
    cr_closed = collatz_residue(k)
    print(f"  k={k:2d}: method_c = {cr_c:6d}, closed = {cr_closed:6d}, match: {cr_c == cr_closed}")

print()
print("="*70)
print("帰納法の核心: v2(3n+1) >= k ⟺ n % 2^k = c(k) % 2^k")
print("="*70)

print("""
方針: v2 と整除性の関係を使い帰納法で証明

v2(m) >= k ⟺ 2^k | m

よって:
  v2(3n+1) >= k ⟺ 2^k | (3n+1) ⟺ 3n ≡ -1 (mod 2^k) ⟺ n ≡ -3^{-1} (mod 2^k)

ここで -3^{-1} mod 2^k = (2^k - 1) * 3^{-1} mod 2^k

これは直接計算可能!
  -1/3 mod 2^k = (2^k - 1) * 3^{-1} mod 2^k

確認:
""")

for k in range(1, 13):
    mod = 2**k
    inv3 = pow(3, -1, mod)
    minus_inv3 = (-inv3) % mod
    # = (mod - 1) * inv3 mod mod
    alt = ((mod - 1) * inv3) % mod
    ck = collatz_residue(k) % mod

    print(f"  k={k:2d}: -3^{{-1}} mod 2^k = {minus_inv3:6d}, "
          f"(2^k-1)*3^{{-1}} mod 2^k = {alt:6d}, "
          f"c(k) mod 2^k = {ck:6d}, match: {minus_inv3 == ck}")

print()
print("="*70)
print("決定的発見: c(k) mod 2^k = (2^k - 1)/3 mod 2^k = -1/3 mod 2^k")
print("="*70)

print("""
本質: v2(3n+1) >= k ⟺ 3n + 1 ≡ 0 (mod 2^k)
                     ⟺ 3n ≡ -1 (mod 2^k)
                     ⟺ n ≡ -3^{-1} (mod 2^k)

そして -3^{-1} mod 2^k = c(k) mod 2^k

これはLeanでは:
  (1) 3^{-1} mod 2^k が存在する (3は奇数なので gcd(3, 2^k) = 1)
  (2) n * 3 ≡ 2^k - 1 (mod 2^k) の唯一解が c(k) mod 2^k

実はこれは (2^k - 1) / 3 そのものではない。
2^k - 1 が3で割り切れるのは k偶数のときだけ:
  k偶数: 2^k ≡ 1 (mod 3) → 2^k - 1 ≡ 0 (mod 3) → (2^k-1)/3 は整数
  k奇数: 2^k ≡ 2 (mod 3) → 2^k - 1 ≡ 1 (mod 3) → (2^k-1)/3 は整数でない

では実際に (2^k-1) * 3^{-1} mod 2^k は何か？
""")

for k in range(1, 13):
    mod = 2**k
    inv3 = pow(3, -1, mod)
    val = ((mod - 1) * inv3) % mod
    ck = collatz_residue(k) % mod

    # (2^k - 1) が3の倍数かどうか
    div3 = (2**k - 1) % 3 == 0

    if div3:
        exact_div = (2**k - 1) // 3
        print(f"  k={k:2d}: (2^k-1)={2**k-1:5d}, 3|? YES, "
              f"(2^k-1)/3 = {exact_div:6d} mod 2^k = {exact_div % mod:6d}, "
              f"c(k) mod 2^k = {ck:6d}, match: {exact_div % mod == ck}")
    else:
        print(f"  k={k:2d}: (2^k-1)={2**k-1:5d}, 3|? NO,  "
              f"(2^k-1)*3^{{-1}} mod 2^k = {val:6d}, "
              f"c(k) mod 2^k = {ck:6d}, match: {val == ck}")

print()
print("="*70)
print("最終的なLean証明ロードマップ")
print("="*70)

print("""
[核心の単純化]
  v2(3n+1) >= k  は  2^k | (3n+1)  と同値。
  これは  n ≡ c(k) (mod 2^k)  と同値。
  ここで c(k) = (4^{ceil(k/2)} - 1) / 3

  証明:
    2^k | (3n+1)
    ⟺ 3n ≡ -1 (mod 2^k)
    ⟺ n ≡ (-1) * 3^{-1} (mod 2^k)

    -3^{-1} mod 2^k = c(k) mod 2^k は以下で証明:
    3 * c(k) + 1 = 4^{ceil(k/2)} (核心等式)
    4^{ceil(k/2)} = 2^{2*ceil(k/2)} (2のべき乗)
    2*ceil(k/2) >= k (常に成り立つ)
    よって 2^k | 4^{ceil(k/2)} = 3*c(k) + 1
    つまり 3*c(k) ≡ -1 (mod 2^k)
    つまり c(k) ≡ -3^{-1} (mod 2^k)

[Lean証明の推奨順序]

1. 定義:
   def collatzResidue (k : Nat) : Nat := (4^((k+1)/2) - 1) / 3

2. 核心等式 (帰納法 on k/2):
   theorem three_collatzResidue_add_one (k : Nat) :
     3 * collatzResidue k + 1 = 4 ^ ((k+1)/2)

3. 整除性:
   theorem two_pow_dvd_three_collatzResidue_add_one (k : Nat) :
     2^k ∣ (3 * collatzResidue k + 1)

   証明: 4^{ceil(k/2)} = 2^{2*ceil(k/2)}, 2*ceil(k/2) >= k

4. v2 >= k の特徴付け (帰納法 on k):
   theorem v2_ge_iff_mod (n k : Nat) (hodd : n % 2 = 1) :
     v2 (3*n+1) >= k ↔ n % 2^k = collatzResidue k % 2^k

   帰納ステップの核心:
     2^{k+1} | (3n+1)
     ⟺ 2^k | (3n+1)  かつ  (3n+1)/2^k は偶数
     これは v2 の定義から直接従う

   しかしより直接的には:
     v2(3n+1) >= k ⟺ 2^k | (3n+1)
     を v2_dvd_iff 的な補題で橋渡し

5. v2 = j の条件:
   theorem v2_eq_iff_mod (n j : Nat) (hodd : n % 2 = 1) (hj : j >= 1) :
     v2 (3*n+1) = j ↔
       n % 2^j = collatzResidue j % 2^j ∧
       ¬(n % 2^(j+1) = collatzResidue (j+1) % 2^(j+1))

6. 既存定理の回収:
   v2_of_mod8_eq1, v2_of_mod8_eq3, etc. は j=1,2 の特殊ケース

[Leanでの主な技術的課題]
  A. Nat 除算の取り扱い: (4^m - 1) / 3
     → 3 * ((4^m - 1)/3) = 4^m - 1 を示す必要
     → 4^m ≡ 1 (mod 3) (帰納法)

  B. v2 と 2^k | m の同値性
     → v2_eq_dvd: v2(m) >= k ⟺ 2^k | m
     → これは v2 の定義から帰納法で証明

  C. 2^k での mod 演算と整除性の接続
     → Nat.dvd_iff_mod_eq_zero 等を活用

  D. ceil(k/2) の扱い
     → Lean では (k+1)/2 (自然数除算)
     → 2*((k+1)/2) >= k は場合分けで証明
""")

# 最後に: v2 = j の場合の r_j の閉形式
print("="*70)
print("v2(3n+1) = j の残基 r_j の閉形式")
print("="*70)

print("""
r_j (v2 = j exactlyの残基 mod 2^{j+1}) について:

v2(3n+1) = j ⟺ v2(3n+1) >= j ∧ ¬(v2(3n+1) >= j+1)

v2 >= j:   n ≡ c(j) (mod 2^j)      ... c(j)のリフトが2つ
v2 >= j+1: n ≡ c(j+1) (mod 2^{j+1}) ... 1つだけ

r_j = c(j)のリフト2つのうち、c(j+1)でないほう
""")

for j in range(1, 13):
    cj = collatz_residue(j) % (2**j)
    cj1 = collatz_residue(j+1) % (2**(j+1))

    lift0 = cj
    lift1 = cj + 2**j

    if lift0 == cj1:
        r_j = lift1
        lifted_from = 1
    else:
        r_j = lift0
        lifted_from = 0

    # r_j の閉形式を求める
    # r_j = (2^j - 1) * 3^{-1} mod 2^{j+1}
    inv3 = pow(3, -1, 2**(j+1))
    r_j_formula = ((2**j - 1) * inv3) % (2**(j+1))

    print(f"  j={j:2d}: c(j)%2^j={cj:6d}, lifts=[{lift0},{lift1}], "
          f"c(j+1)%2^{{j+1}}={cj1:6d}, "
          f"r_j={r_j:6d} (lift{lifted_from}), "
          f"formula={(2**j-1)*inv3%(2**(j+1)):6d}, match: {r_j == r_j_formula}")

print()
# lift パターンの分析
print("どちらのリフトが選ばれるか (j の偶奇):")
for j in range(1, 16):
    cj = collatz_residue(j) % (2**j)
    cj1 = collatz_residue(j+1) % (2**(j+1))

    lift0 = cj
    lift1 = cj + 2**j

    if lift0 == cj1:
        choice = "lift1 (= c_j + 2^j)"
    else:
        choice = "lift0 (= c_j)"

    print(f"  j={j:2d} ({'even' if j%2==0 else 'odd '}): r_j = {choice}")
