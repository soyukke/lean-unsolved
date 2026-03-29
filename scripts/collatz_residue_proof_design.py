#!/usr/bin/env python3
"""
collatzResidue の Lean 証明設計: 帰納法の各ステップの詳細

特に:
1. 再帰定義の well-definedness
2. 核心等式の帰納ステップの代数的詳細
3. v2条件の証明パスの設計
4. 既存補題との接続
"""

def v2(n):
    if n == 0: return float('inf')
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c

def ceil_half(k):
    return (k + 1) // 2

def cr(k):
    return (4**ceil_half(k) - 1) // 3

print("=" * 80)
print("A. 再帰定義の帰納ステップの代数的検証")
print("=" * 80)
print()

print("定義: collatzResidue 0 = 0")
print("      collatzResidue (k+1) = if k even then 4*c(k)+1 else c(k)")
print()

# k偶数の場合の核心等式:
# 仮定: 3*c(k)+1 = 4^{ceil(k/2)} = 4^{k/2}  (k偶数のとき ceil(k/2)=k/2)
# 目標: 3*c(k+1)+1 = 4^{ceil((k+1)/2)} = 4^{(k+2)/2} = 4^{k/2+1}  (k+1奇数のとき ceil((k+1)/2)=(k+2)/2)
# c(k+1) = 4*c(k)+1
# 3*(4*c(k)+1)+1 = 12*c(k)+4 = 4*(3*c(k)+1) = 4*4^{k/2} = 4^{k/2+1} ✓

print("k偶数ステップ:")
for k in range(0, 12, 2):
    ck = cr(k)
    ck1 = cr(k+1)
    lhs = 3*(4*ck+1)+1
    rhs = 4**(ceil_half(k+1))
    mid = 4*(3*ck+1)
    print(f"  k={k}: 3*(4*{ck}+1)+1 = {lhs}, 4*(3*{ck}+1) = {mid}, 4^{ceil_half(k+1)} = {rhs}, OK={lhs==rhs}")

print()

# k奇数の場合の核心等式:
# 仮定: 3*c(k)+1 = 4^{ceil(k/2)} = 4^{(k+1)/2}  (k奇数のとき)
# 目標: 3*c(k+1)+1 = 4^{ceil((k+1)/2)} = 4^{(k+1)/2}  (k+1偶数のとき ceil((k+1)/2)=(k+1)/2)
# c(k+1) = c(k)
# 3*c(k)+1 = 4^{(k+1)/2}
# ceil((k+1)/2) = (k+1)/2 = ceil(k/2) (k奇数のとき)
# → そのまま成立 ✓

print("k奇数ステップ:")
for k in range(1, 12, 2):
    ck = cr(k)
    ck1 = cr(k+1)
    assert ck == ck1, f"c(k)={ck} != c(k+1)={ck1}"
    lhs = 3*ck+1
    rhs_k = 4**ceil_half(k)
    rhs_k1 = 4**ceil_half(k+1)
    print(f"  k={k}: c(k)=c(k+1)={ck}, 3*c+1={lhs}, "
          f"4^ceil(k/2)={rhs_k}, 4^ceil((k+1)/2)={rhs_k1}, "
          f"equal={rhs_k==rhs_k1}")

print()
print("=" * 80)
print("B. Lean 証明設計: 核心等式")
print("=" * 80)

print("""
/-- collatzResidue: v2(3n+1)≥k条件の剰余
    再帰定義: c(0)=0, k偶→c(k+1)=4c(k)+1, k奇→c(k+1)=c(k) -/
def collatzResidue : Nat → Nat
  | 0 => 0
  | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
             else collatzResidue n

-- 数値検証
example : collatzResidue 0 = 0 := rfl
example : collatzResidue 1 = 1 := rfl
example : collatzResidue 2 = 1 := rfl    -- 1%2=1≠0, so c(2)=c(1)=1
example : collatzResidue 3 = 5 := rfl    -- 2%2=0, so c(3)=4*1+1=5
example : collatzResidue 4 = 5 := rfl    -- 3%2=1≠0, so c(4)=c(3)=5
example : collatzResidue 5 = 21 := rfl   -- 4%2=0, so c(5)=4*5+1=21

問題点: 「n+1」パターンだと n の偶奇チェックが必要。
  collatzResidue (n+1) で:
    n=0(偶): c(1) = 4*0+1 = 1 ✓
    n=1(奇): c(2) = c(1) = 1 ✓
    n=2(偶): c(3) = 4*1+1 = 5 ✓
    n=3(奇): c(4) = c(3) = 5 ✓
    n=4(偶): c(5) = 4*5+1 = 21 ✓

これは正しい！

---

/-- 核心等式: 3 * collatzResidue k + 1 = 4 ^ ((k+1)/2)
    (Natの除算: (k+1)/2 = ceil(k/2)) -/
theorem collatzResidue_core_eq (k : Nat) :
    3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2) := by
  induction k with
  | zero => simp [collatzResidue]
  | succ n ih =>
    -- goal: 3 * collatzResidue (n+1) + 1 = 4 ^ ((n+2)/2)
    unfold collatzResidue
    split  -- n % 2 = 0 で場合分け
    · case _ h =>  -- n even
      -- collatzResidue (n+1) = 4 * collatzResidue n + 1
      -- 3*(4*c(n)+1)+1 = 12*c(n)+4 = 4*(3*c(n)+1) = 4*4^{(n+1)/2}
      -- n 偶数: (n+2)/2 = (n+1)/2 + 1 ... ではない
      -- n 偶数のとき n=2m: (n+1)/2 = (2m+1)/2 = m, (n+2)/2 = (2m+2)/2 = m+1
      -- 4^{m+1} = 4 * 4^m ✓
      -- ih: 3*c(n)+1 = 4^{(n+1)/2} = 4^m
      -- goal: 3*(4*c(n)+1)+1 = 4^{m+1}
      -- = 12*c(n)+4 = 4*(3*c(n)+1) = 4*4^m = 4^{m+1} ✓
      sorry
    · case _ h =>  -- n odd
      -- collatzResidue (n+1) = collatzResidue n
      -- 3*c(n)+1 = 4^{(n+1)/2}
      -- n 奇数のとき n=2m+1: (n+1)/2 = (2m+2)/2 = m+1, (n+2)/2 = (2m+3)/2 = m+1
      -- (n+1)/2 = (n+2)/2 ✓ (Natの除算で)
      sorry

---

帰納ステップの核心は:
1. n偶数: (n+2)/2 = (n+1)/2 + 1 の証明 (Nat.divでは直接使えない)
   → n=2*m のとき (2m+2)/2 = m+1, (2m+1)/2 = m
   → (n+2)/2 = (n+1)/2 + 1 は n偶数のとき成立 (Nat)
   → omega で処理可能

2. n奇数: (n+2)/2 = (n+1)/2 の証明
   → n=2m+1 のとき (2m+3)/2 = m+1, (2m+2)/2 = m+1
   → omega で処理可能

""")

print()
print("=" * 80)
print("C. v2条件の証明設計")
print("=" * 80)

print("""
/-- v2(3n+1) >= k <-> n % 2^k = collatzResidue k -/
theorem v2_ge_iff_collatzResidue (n k : Nat) (hodd : n % 2 = 1) :
    v2 (3 * n + 1) >= k <-> n % 2^k = collatzResidue k

証明の骨格:
  核心等式より 3 * collatzResidue k + 1 = 4^{(k+1)/2}
  v2(3*c(k)+1) = v2(4^{(k+1)/2}) = 2*(k+1)/2

  ここで重要: v2(4^j) = 2j
  k偶数(k=2m): ceil(k/2)=m, v2(4^m)=2m=k ✓
  k奇数(k=2m+1): ceil(k/2)=m+1, v2(4^{m+1})=2m+2=k+1 > k ✓

  つまり v2(3*c(k)+1) >= k は常に成立！

  [十分性]: n ≡ c(k) (mod 2^k) ならば v2(3n+1) >= k
    3n+1 ≡ 3*c(k)+1 ≡ 0 (mod 2^k) (核心等式+k|2*ceil(k/2) から)

  [必要性]: v2(3n+1) >= k ならば n ≡ c(k) (mod 2^k)
    2^k | 3n+1 → 3n ≡ -1 (mod 2^k) → n ≡ -1/3 (mod 2^k) = c(k)
    3 は 2^k と互いに素なので逆元が一意に存在

既存補題の活用:
  - v2_ge_iff_dvd: v2(m)>=k <-> 2^k | m
  → v2(3n+1) >= k <-> 2^k | (3n+1)
  → 2^k | (3n+1) <-> 3n+1 ≡ 0 (mod 2^k) <-> n ≡ c(k) (mod 2^k)
""")

print()
print("=" * 80)
print("D. 2^k | (3c(k)+1) の証明設計（核心等式の系）")
print("=" * 80)

# 核心等式: 3*c(k)+1 = 4^{ceil(k/2)}
# 2^k | 4^{ceil(k/2)} = 2^{2*ceil(k/2)}
# 必要: k <= 2*ceil(k/2) = 2*((k+1)/2)
# k偶数(k=2m): 2*m = k ✓
# k奇数(k=2m+1): 2*(m+1) = k+1 > k ✓

print("検証: k <= 2*ceil(k/2)")
for k in range(20):
    ch = ceil_half(k)
    lhs = k
    rhs = 2 * ch
    print(f"  k={k}: k={lhs} <= 2*ceil(k/2)={rhs}: {lhs <= rhs}")

print()
print("=" * 80)
print("E. 一意性の証明（3の逆元の一意性）")
print("=" * 80)

print("""
命題: 奇数nに対して 2^k | (3n+1) を満たす n mod 2^k は一意

証明:
  2^k | (3n+1) <-> 3n ≡ -1 (mod 2^k) <-> n ≡ (-1) * 3^{-1} (mod 2^k)
  gcd(3, 2^k) = 1 なので 3^{-1} mod 2^k は一意に存在

  Lean では:
  - Nat.Coprime (3, 2^k) は Nat.Coprime.pow_right で証明
  - 逆元の存在は ZMod.unitOfCoprime 等
  - ただし自然数演算で直接やるなら omega + 帰納法が現実的

直接的な証明:
  2^k | (3n+1) かつ 2^k | (3m+1) → 2^k | 3(n-m) → 2^k | (n-m)
  (3 と 2^k は互いに素なので)
  → n ≡ m (mod 2^k)
""")

print()
print("=" * 80)
print("F. v2(3n+1)=kの剰余（正確な値の場合）")
print("=" * 80)

# v2(3n+1) = k (exactly) の条件
for k in range(1, 9):
    mod = 2**(k+1)
    residues = []
    for n in range(1, mod, 2):
        if v2(3*n+1) == k:
            residues.append(n)
    cr_k = cr(k)
    cr_k1 = cr(k+1)
    print(f"  v2(3n+1)={k} (exactly): n % {mod} in {residues}")
    print(f"    collatzResidue({k})={cr_k}, collatzResidue({k+1})={cr_k1}")
    # v2=k exactly means: 2^k | (3n+1) but 2^{k+1} ∤ (3n+1)
    # i.e., n % 2^k = c(k) but n % 2^{k+1} != c(k+1)
    for r in residues:
        assert r % (2**k) == cr_k, f"FAIL: {r} % {2**k} = {r%(2**k)} != {cr_k}"
    print(f"    All residues satisfy n%2^k = c(k) ✓")

print()
print("=" * 80)
print("G. 推奨する形式化ステップ（6段階）")
print("=" * 80)

print("""
Step 1: collatzResidue の再帰定義
  def collatzResidue : Nat → Nat
    | 0 => 0
    | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
               else collatzResidue n

Step 2: 数値検証 (rfl で)
  example : collatzResidue 0 = 0 := rfl
  example : collatzResidue 1 = 1 := rfl
  ...

Step 3: 核心等式 (kに関する帰納法)
  theorem collatzResidue_core_eq (k : Nat) :
    3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2)

Step 4: 2^k整除性 (核心等式+整除性)
  theorem two_pow_dvd_three_cr_add_one (k : Nat) :
    2^k ∣ (3 * collatzResidue k + 1)

Step 5: v2条件 (v2_ge_iff_dvdとStep 4の接続)
  theorem v2_ge_of_mod_eq_cr (n k : Nat) (hodd : n % 2 = 1)
    (hmod : n % 2^k = collatzResidue k) :
    v2 (3 * n + 1) ≥ k

Step 6: 同値条件 (一意性)
  theorem v2_ge_iff_mod_eq_cr (n k : Nat) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    v2 (3 * n + 1) ≥ k ↔ n % 2^k = collatzResidue k

各ステップの難易度:
  Step 1-2: 簡単（定義＋rfl）
  Step 3: 中程度（kの偶奇場合分け＋算術）
  Step 4: 簡単（Step 3の系、pow_dvd_pow）
  Step 5: 中程度（v2_ge_iff_dvd＋合同式の扱い）
  Step 6: 難（3の逆元の一意性、自然数での合同演算）
""")

print()
print("=" * 80)
print("H. 最終的な形式化価値の評価")
print("=" * 80)

print("""
★★ 形式化価値の評価:

既存成果との差分:
  - hensel_general: 連続上昇⟷全ビット1条件 (異なる条件)
  - v2_ge_iff_dvd: v2とdvdの接続 (基盤補題)
  - ascentConst: 連続上昇公式の定数 (異なる量)

新規貢献:
  1. collatzResidue の定義: v2(3n+1)≥kを特徴付ける剰余
  2. 核心等式: 3c(k)+1 = 4^{ceil(k/2)}
  3. 交互ビットパターン: c(k) = ...010101 (2進数)
  4. v2条件の同値定理
  5. 3の2-adic逆数との関係

応用可能性:
  - Syracuse関数の下降幅の制御
  - 「強い下降」(v2≥3以上)の条件の精密記述
  - 軌道長の下界見積もりへの応用
  - mod 2^k での Syracuse の振る舞いの完全記述

結論: Step 1-4 は確実に形式化可能。Step 5-6 は v2_ge_iff_dvd を
     活用すれば中程度の難易度。全体として中程度の形式化価値。
""")
