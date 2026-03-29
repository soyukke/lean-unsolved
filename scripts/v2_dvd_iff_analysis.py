"""
v2(m) >= k iff 2^k | m の分析

目標: 以下の同値を証明する設計を分析
  v2(m) >= k <-> 2^k | m

既知:
  - pow_v2_dvd: 2^v2(m) | m  (順方向のベース)
  - v2_zero, v2_odd, v2_even, v2_two_mul

方針:
(1) 順方向 (v2(m)>=k -> 2^k|m):
    2^v2(m)|m と k<=v2(m) から 2^k | 2^v2(m) | m

(2) 逆方向 (2^k|m -> v2(m)>=k):
    kに関する帰納法、またはmに関する強帰納法
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    if n % 2 != 0:
        return 0
    return 1 + v2(n // 2)

# 検証
print("=== v2 values ===")
for m in range(20):
    print(f"v2({m}) = {v2(m)}")

print("\n=== Verification: v2(m) >= k iff 2^k | m ===")
errors = []
for m in range(1, 200):
    for k in range(10):
        lhs = v2(m) >= k
        rhs = m % (2**k) == 0
        if lhs != rhs:
            errors.append((m, k, lhs, rhs))

if errors:
    print(f"ERRORS FOUND: {errors[:10]}")
else:
    print("All cases verified for m in [1,199], k in [0,9]")

# m=0 の場合を分析
print("\n=== m=0 case ===")
for k in range(5):
    v = v2(0)
    dvd = 0 % (2**k) == 0
    print(f"k={k}: v2(0)={v} >= {k} is {v >= k}, 2^{k}|0 is {dvd}")

print("\n=== m=0の問題 ===")
print("v2(0)=0 だが 2^k|0 は任意のkで成立")
print("したがって v2(m)>=k <-> 2^k|m はm=0では逆方向が失敗")
print("修正案: m>0 の前提を追加、または m=0のときの別定義")

# 逆方向の帰納法設計
print("\n=== 逆方向証明設計 (k-induction) ===")
print("""
目標: 2^k | m -> v2(m) >= k  (m > 0の前提付き)

k=0: 自明 (v2(m) >= 0 は常に成立)
k -> k+1:
  2^(k+1) | m を仮定
  → 2 | m → m は偶数 → m ≠ 0 なので v2(m) = 1 + v2(m/2)  [v2_even]
  → 2^k | m/2  (2^(k+1)|m かつ m=2*(m/2) より)
  → IH: v2(m/2) >= k
  → v2(m) = 1 + v2(m/2) >= 1 + k = k+1
""")

# 順方向の設計
print("=== 順方向証明設計 ===")
print("""
目標: v2(m) >= k -> 2^k | m

方法1: 2^v2(m)|m (pow_v2_dvd) + k<=v2(m) → 2^k | 2^v2(m) | m
  具体的に: pow_dvd_pow 2 h : 2^k | 2^v2(m)  (h: k <= v2(m))
  dvd_trans (pow_dvd_pow 2 h) (pow_v2_dvd m) : 2^k | m
""")

# m-induction版の設計も考察
print("=== 代替: m-strong-induction ===")
print("""
逆方向をm強帰納法で証明する方法:

2^k | m → v2(m) >= k を示す (m強帰納法)

base: m=0 → m>0 前提で除外 (v2(0)=0 問題を回避)

m>0 case:
  by_cases k = 0: 自明
  k > 0:
    2^k | m → 2|m → m偶数
    m偶数 → v2(m) = 1 + v2(m/2)
    2^k | m → 2^(k-1) | (m/2)  [since 2*2^(k-1) | 2*(m/2)]
    IH: m/2 < m, so v2(m/2) >= k-1
    v2(m) = 1 + v2(m/2) >= 1 + (k-1) = k
""")

# 完全な定理ステートメントの候補
print("\n=== 最終ステートメント候補 ===")
print("""
1. v2_ge_iff_dvd (m : ℕ) (k : ℕ) (hm : m > 0) :
     v2 m >= k ↔ 2^k ∣ m

2. 分割版:
   a. dvd_of_v2_ge (m k : ℕ) (h : v2 m >= k) : 2^k ∣ m
      -- pow_v2_dvd + pow_dvd_pow + dvd_trans で即座

   b. v2_ge_of_dvd (m k : ℕ) (hm : m > 0) (h : 2^k ∣ m) : v2 m >= k
      -- k帰納法 or m強帰納法

3. m=0版 (iffにするなら hm 不要):
   dvd_of_v2_ge は m=0 でも成立 (v2(0)=0 → k=0 → 2^0=1|0 ✓)
""")

# v2(m) >= k → 2^k | m がm=0でも成立するか確認
print("\n=== v2(m)>=k → 2^k|m for m=0 ===")
m = 0
for k in range(5):
    if v2(m) >= k:
        dvd = m % (2**k) == 0
        print(f"v2(0)={v2(0)} >= {k}: True, 2^{k}|0 = {dvd}")
print("k=0のみ: v2(0)=0>=0 で 2^0=1|0 ✓")
print("順方向はm=0でも問題なし")

# pow_dvd_pow が使えるか
print("\n=== Lean戦略 ===")
print("""
Lean 4での証明戦略:

-- 順方向
theorem dvd_of_v2_ge (m k : ℕ) (h : v2 m ≥ k) : 2 ^ k ∣ m := by
  exact dvd_trans (pow_dvd_pow 2 h) (two_pow_v2_dvd m)

-- 逆方向 (k帰納法)
theorem v2_ge_of_dvd (m k : ℕ) (hm : m > 0) (h : 2 ^ k ∣ m) : v2 m ≥ k := by
  induction k with
  | zero => omega
  | succ k ih =>
    have heven : m % 2 = 0 := by
      have : 2 ∣ m := dvd_trans (dvd_pow_self 2 (Nat.succ_ne_zero k)) h
      exact Nat.mod_eq_zero_of_dvd this
    have hne : m ≠ 0 := by omega
    rw [v2_even m hne heven]
    suffices v2 (m / 2) ≥ k by omega
    apply ih (m / 2) ?_ ?_
    · omega  -- m/2 > 0 since m > 0 and m even
    · -- 2^(k+1)|m → 2^k | m/2
      ... (Nat.div_dvd_of_dvd 等を使う)

-- 同値
theorem v2_ge_iff_dvd (m k : ℕ) (hm : m > 0) : v2 m ≥ k ↔ 2 ^ k ∣ m := by
  constructor
  · exact dvd_of_v2_ge m k
  · exact v2_ge_of_dvd m k hm
""")

# 2^(k+1) | m → 2^k | (m/2) の補題が必要
print("\n=== 2^(k+1)|m → 2^k|(m/2) の証明 ===")
for m in [4, 8, 12, 16, 24, 32]:
    for k in range(5):
        if m % (2**(k+1)) == 0:
            half = m // 2
            dvd_half = half % (2**k) == 0
            print(f"2^{k+1}|{m}: True, 2^{k}|{m//2}={half}: {dvd_half}")

print("""
2^(k+1)|m かつ m偶数のとき:
  m = 2^(k+1) * c  for some c
  m/2 = 2^k * c
  → 2^k | (m/2)

Lean: have ⟨c, hc⟩ := h  -- h: 2^(k+1)|m
      -- m = 2^(k+1)*c = 2*(2^k*c)
      -- m/2 = 2^k * c
      exact ⟨c, by rw [pow_succ] at hc; omega⟩
""")

# Nat.dvd_div_of_mul_dvd の確認
print("\n=== Mathlibの関連補題 ===")
print("""
候補:
- Nat.div_dvd_of_dvd: a ∣ b → b / a ∣ b (違う方向)
- Nat.dvd_div_iff_mul_dvd: (k ∣ m) → (l ∣ m / k ↔ l * k ∣ m)
  - 使い方: 2 ∣ m → (2^k ∣ m/2 ↔ 2^k * 2 ∣ m)
  - 2^k * 2 = 2^(k+1) なので 2^(k+1)|m ↔ 2^k | m/2

- pow_succ: 2^(k+1) = 2^k * 2 (or 2 * 2^k)

実際のLean証明:
  apply ih
  · omega
  · rwa [Nat.dvd_div_iff_mul_dvd (dvd_of_mod_eq_zero heven), pow_succ']
    -- pow_succ' : a ^ (n+1) = a ^ n * a
""")
