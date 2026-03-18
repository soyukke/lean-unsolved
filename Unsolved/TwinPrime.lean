import Mathlib

/-!
# 双子素数予想 (Twin Prime Conjecture)

差が2の素数の組（双子素数）は無限に存在する。

例: (3,5), (5,7), (11,13), (17,19), (29,31), ...

## 探索1: Mathlib調査結果
- Mathlibに双子素数の直接的な形式化は存在しない
- 関連する形式化:
  - `Nat.primeCounting` (素数計数関数 π)
  - `SelbergSieve` (Selberg篩の基本設定)
  - `SumPrimeReciprocals` (素数逆数和の発散)
  - `Chebyshev` (チェビシェフの定理)
- Brunの定理、Zhang/Maynard-Taoの有界ギャップ定理は未形式化

## 探索2: 数値実験結果 (scripts/twinprime_explore.py)
- π₂(10⁶) = 8,169 組
- p > 3 の双子素数は全て p ≡ 5 (mod 6) — 下記で証明
- mod 30 では 11, 17, 29 の3剰余類にほぼ均等分布
- Brunの定数 B₂ ≈ 1.711 (10⁶までの部分和)

## 探索3: Lean検証例と基本補題

## 探索7: 双子素数の mod 30 構造
- p > 5 の双子素数 (p, p+2) は p % 30 ∈ {11, 17, 29}
- twin_prime_mod30: 5の整除性を使った排除で証明

## 探索8: Cousin primes (差4) の構造
- p > 3 かつ (p, p+4) がともに素数なら p ≡ 1 (mod 6)
- p%6=5 なら (p+4)%6=3 で 3|(p+4) → 矛盾

## 探索9: Cousin prime の mod 30 構造
- p > 5 の cousin prime (p, p+4) は p%30 ∈ {1, 7, 13, 19}
- p%6=1 から p%30 ∈ {1, 7, 13, 19, 25} を導出、25 は 5|p で矛盾

## 探索10: Sexy primes (差6) の定義と検証例
- IsSexyPrime の定義: p, p+6 がともに素数
- 5, 7, 11, 13, 23 での検証

## 探索11: 双子素数の間の数は6の倍数 + 大きい双子素数の検証
- (p, p+2) が双子素数で p > 3 のとき、p+1 は 6 の倍数
- twin_prime_mod_six から p%6=5 を使い (p+1)%6=0 を導出
- 3桁の双子素数検証: (101,103), (107,109), (137,139), (149,151)

## 探索12: 双子素数ペアの対称性
- IsTwinPrime 定義述語の導入
- twin_prime_second: p+2 の素数性を明示
- 検証例: IsTwinPrime 3, 5, 11, 17, 29, 41
-/

/-- 双子素数予想: 差が2の素数の組は無限に存在する -/
def TwinPrimeConjecture : Prop :=
  ∀ N : ℕ, ∃ p : ℕ, p > N ∧ Nat.Prime p ∧ Nat.Prime (p + 2)

-- ===== 双子素数の検証例 =====

-- (3, 5) は双子素数
example : Nat.Prime 3 ∧ Nat.Prime 5 := by constructor <;> norm_num

-- (5, 7) は双子素数
example : Nat.Prime 5 ∧ Nat.Prime 7 := by constructor <;> norm_num

-- (11, 13) は双子素数
example : Nat.Prime 11 ∧ Nat.Prime 13 := by constructor <;> norm_num

-- (17, 19) は双子素数
example : Nat.Prime 17 ∧ Nat.Prime 19 := by constructor <;> norm_num

-- (29, 31) は双子素数
example : Nat.Prime 29 ∧ Nat.Prime 31 := by constructor <;> norm_num

-- (41, 43) は双子素数
example : Nat.Prime 41 ∧ Nat.Prime 43 := by constructor <;> norm_num

-- (59, 61) は双子素数
example : Nat.Prime 59 ∧ Nat.Prime 61 := by constructor <;> norm_num

-- (71, 73) は双子素数
example : Nat.Prime 71 ∧ Nat.Prime 73 := by constructor <;> norm_num

-- ===== 基本補題: 双子素数の mod 6 構造 =====

/-- 素数 p > 3 は 2 で割れない -/
private lemma prime_gt_three_not_dvd_two {p : ℕ} (hp : Nat.Prime p) (hp3 : p > 3) :
    ¬ (2 ∣ p) := by
  intro h2
  have := hp.eq_one_or_self_of_dvd 2 h2
  omega

/-- 素数 p > 3 は 3 で割れない -/
private lemma prime_gt_three_not_dvd_three {p : ℕ} (hp : Nat.Prime p) (hp3 : p > 3) :
    ¬ (3 ∣ p) := by
  intro h3
  have := hp.eq_one_or_self_of_dvd 3 h3
  omega

/-- 3より大きい素数は 6 で割った余りが 1 か 5 -/
lemma prime_gt_three_mod_six {p : ℕ} (hp : Nat.Prime p) (hp3 : p > 3) :
    p % 6 = 1 ∨ p % 6 = 5 := by
  have hmod : p % 6 < 6 := Nat.mod_lt p (by norm_num)
  have h2 : ¬ (2 ∣ p) := prime_gt_three_not_dvd_two hp hp3
  have h3 : ¬ (3 ∣ p) := prime_gt_three_not_dvd_three hp hp3
  -- p % 6 ∈ {0,1,2,3,4,5} のうち偶数(0,2,4)と3の倍数(0,3)を除外
  have h0 : p % 6 ≠ 0 := fun h => h2 ⟨p / 6 * 3, by omega⟩
  have h2' : p % 6 ≠ 2 := fun h => h2 ⟨p / 6 * 3 + 1, by omega⟩
  have h3' : p % 6 ≠ 3 := fun h => h3 ⟨p / 6 * 2 + 1, by omega⟩
  have h4 : p % 6 ≠ 4 := fun h => h2 ⟨p / 6 * 3 + 2, by omega⟩
  omega

/-- p > 3 かつ p, p+2 がともに素数なら、p % 6 = 5
    （つまり双子素数 (p, p+2) で p > 3 なら p ≡ 5 mod 6 = 6k-1 の形） -/
theorem twin_prime_mod_six {p : ℕ} (hp : Nat.Prime p) (hp2 : Nat.Prime (p + 2))
    (hp3 : p > 3) : p % 6 = 5 := by
  rcases prime_gt_three_mod_six hp hp3 with h1 | h5
  · -- p % 6 = 1 の場合、(p+2) % 6 = 3 なので 3 ∣ (p+2)
    exfalso
    have hmod : (p + 2) % 6 = 3 := by omega
    have h3dvd : 3 ∣ (p + 2) := ⟨(p + 2) / 3, by omega⟩
    have := hp2.eq_one_or_self_of_dvd 3 h3dvd
    omega
  · exact h5

/-- 双子素数 (p, p+2) の p+2 > 3 なら (p+2) % 6 = 1
    つまり大きい方は 6k+1 の形 -/
theorem twin_prime_plus_two_mod_six {p : ℕ} (hp : Nat.Prime p) (hp2 : Nat.Prime (p + 2))
    (hp3 : p > 3) : (p + 2) % 6 = 1 := by
  have h5 := twin_prime_mod_six hp hp2 hp3
  omega

/-! ## 探索7: 双子素数の mod 30 構造 -/

/-- 5より大きい双子素数 (p, p+2) の p は p % 30 ∈ {11, 17, 29} -/
theorem twin_prime_mod30 {p : ℕ} (hp : Nat.Prime p) (hp2 : Nat.Prime (p + 2)) (hp5 : p > 5) :
    p % 30 = 11 ∨ p % 30 = 17 ∨ p % 30 = 29 := by
  have h6 := twin_prime_mod_six hp hp2 (by omega)
  -- p % 6 = 5 なので p % 30 ∈ {5, 11, 17, 23, 29}
  have hmod30 : p % 30 < 30 := Nat.mod_lt p (by norm_num)
  -- p % 30 % 6 = 5
  have h630 : p % 30 % 6 = 5 := by omega
  -- p % 30 ≠ 5: p ≡ 5 (mod 30) → 5 ∣ p → p = 5 だが p > 5
  have h5 : p % 30 ≠ 5 := by
    intro heq
    have : 5 ∣ p := ⟨p / 30 * 6 + 1, by omega⟩
    have := hp.eq_one_or_self_of_dvd 5 this
    omega
  -- p % 30 ≠ 23: (p+2) % 30 = 25, so 5 ∣ (p+2), p+2 > 5 → 矛盾
  have h23 : p % 30 ≠ 23 := by
    intro heq
    have hmod2 : (p + 2) % 30 = 25 := by omega
    have : 5 ∣ (p + 2) := ⟨(p + 2) / 30 * 6 + 5, by omega⟩
    have := hp2.eq_one_or_self_of_dvd 5 this
    omega
  omega

/-! ## 探索8: Cousin primes (差4) の構造 -/

/-- p > 3 かつ p, p+4 がともに素数なら p % 6 = 1
    (cousin primes (p, p+4) で p > 3 なら p ≡ 1 mod 6) -/
theorem cousin_prime_mod_six {p : ℕ} (hp : Nat.Prime p) (hp4 : Nat.Prime (p + 4))
    (hp3 : p > 3) : p % 6 = 1 := by
  rcases prime_gt_three_mod_six hp hp3 with h1 | h5
  · exact h1
  · -- p % 6 = 5 の場合、(p+4) % 6 = 3 なので 3 ∣ (p+4)
    exfalso
    have hmod : (p + 4) % 6 = 3 := by omega
    have h3dvd : 3 ∣ (p + 4) := ⟨(p + 4) / 3, by omega⟩
    have := hp4.eq_one_or_self_of_dvd 3 h3dvd
    omega

/-! ## 探索9: Cousin prime の mod 30 構造 -/

/-- p > 5 の cousin prime (p, p+4) は p%30 ∈ {1, 7, 13, 19} -/
theorem cousin_prime_mod30 {p : ℕ} (hp : Nat.Prime p) (hp4 : Nat.Prime (p + 4))
    (hp5 : p > 5) : p % 30 = 1 ∨ p % 30 = 7 ∨ p % 30 = 13 ∨ p % 30 = 19 := by
  have h6 := cousin_prime_mod_six hp hp4 (by omega)
  have hmod30 : p % 30 < 30 := Nat.mod_lt p (by norm_num)
  have h630 : p % 30 % 6 = 1 := by omega
  -- p%30 ∈ {1, 7, 13, 19, 25} から 25 を除外
  have h25 : p % 30 ≠ 25 := by
    intro heq
    have : 5 ∣ p := ⟨p / 30 * 6 + 5, by omega⟩
    have := hp.eq_one_or_self_of_dvd 5 this
    omega
  omega

/-! ## 探索10: Sexy primes (差6) -/

/-- sexy primes の定義: 差が6の素数ペア -/
def IsSexyPrime (p : ℕ) : Prop := Nat.Prime p ∧ Nat.Prime (p + 6)

-- 検証例
example : IsSexyPrime 5 := ⟨by norm_num, by norm_num⟩
example : IsSexyPrime 7 := ⟨by norm_num, by norm_num⟩
example : IsSexyPrime 11 := ⟨by norm_num, by norm_num⟩
example : IsSexyPrime 13 := ⟨by norm_num, by norm_num⟩
example : IsSexyPrime 23 := ⟨by norm_num, by norm_num⟩

/-! ## 探索11: 双子素数の間の数は6の倍数 -/

/-- (p, p+2) が双子素数で p > 3 のとき、p+1 は 6 の倍数 -/
theorem twin_prime_middle_div6 {p : ℕ} (hp : Nat.Prime p) (hp2 : Nat.Prime (p + 2))
    (hp3 : p > 3) : 6 ∣ (p + 1) := by
  have h5 := twin_prime_mod_six hp hp2 hp3
  -- p % 6 = 5 → (p+1) % 6 = 0
  exact ⟨(p + 1) / 6, by omega⟩

/-! ## 探索11: 大きい双子素数の検証 -/

-- (101, 103) は双子素数
example : Nat.Prime 101 ∧ Nat.Prime 103 := by constructor <;> norm_num

-- (107, 109) は双子素数
example : Nat.Prime 107 ∧ Nat.Prime 109 := by constructor <;> norm_num

-- (137, 139) は双子素数
example : Nat.Prime 137 ∧ Nat.Prime 139 := by constructor <;> norm_num

-- (149, 151) は双子素数
example : Nat.Prime 149 ∧ Nat.Prime 151 := by constructor <;> norm_num

/-! ## 探索12: 双子素数ペアの対称性 -/

/-- (p, p+2) が双子素数なら p+2 も素数（自明だが明示） -/
theorem twin_prime_second {p : ℕ} (hp : Nat.Prime p) (hp2 : Nat.Prime (p + 2)) :
    Nat.Prime (p + 2) := hp2

/-- 双子素数の定義述語 -/
def IsTwinPrime (p : ℕ) : Prop := Nat.Prime p ∧ Nat.Prime (p + 2)

-- 検証例
example : IsTwinPrime 3 := ⟨by norm_num, by norm_num⟩
example : IsTwinPrime 5 := ⟨by norm_num, by norm_num⟩
example : IsTwinPrime 11 := ⟨by norm_num, by norm_num⟩
example : IsTwinPrime 17 := ⟨by norm_num, by norm_num⟩
example : IsTwinPrime 29 := ⟨by norm_num, by norm_num⟩
example : IsTwinPrime 41 := ⟨by norm_num, by norm_num⟩

/-! ## 探索13: IsTwinPrime の基本性質 -/

/-- IsTwinPrime p → Nat.Prime p -/
theorem IsTwinPrime.prime_left {p : ℕ} (h : IsTwinPrime p) : Nat.Prime p := h.1

/-- IsTwinPrime p → Nat.Prime (p+2) -/
theorem IsTwinPrime.prime_right {p : ℕ} (h : IsTwinPrime p) : Nat.Prime (p + 2) := h.2

/-- IsTwinPrime p → p ≥ 2 -/
theorem IsTwinPrime.two_le {p : ℕ} (h : IsTwinPrime p) : p ≥ 2 := h.1.two_le

/-! ## 探索14: IsTwinPrime と twin_prime_mod_six の連携 -/

/-- IsTwinPrime p かつ p > 3 → p % 6 = 5 -/
theorem IsTwinPrime.mod_six {p : ℕ} (h : IsTwinPrime p) (hp3 : p > 3) :
    p % 6 = 5 :=
  twin_prime_mod_six h.1 h.2 hp3

/-- IsTwinPrime p かつ p > 3 → (p+1) は 6 の倍数 -/
theorem IsTwinPrime.middle_div6 {p : ℕ} (h : IsTwinPrime p) (hp3 : p > 3) :
    6 ∣ (p + 1) :=
  twin_prime_middle_div6 h.1 h.2 hp3

/-! ## 探索15: 大きい双子素数の検証 -/

-- 59 と 61 は双子素数
example : IsTwinPrime 59 := ⟨by norm_num, by norm_num⟩
-- 71 と 73 は双子素数
example : IsTwinPrime 71 := ⟨by norm_num, by norm_num⟩

/-! ## 探索16: TwinPrimeConjecture の同値な定式化 -/

/-- 双子素数予想は IsTwinPrime を使って書ける -/
theorem twinPrimeConjecture_iff :
    TwinPrimeConjecture ↔ ∀ N : ℕ, ∃ p : ℕ, p > N ∧ IsTwinPrime p := by
  unfold TwinPrimeConjecture IsTwinPrime
  constructor
  · intro h N
    obtain ⟨p, hp1, hp2, hp3⟩ := h N
    exact ⟨p, hp1, hp2, hp3⟩
  · intro h N
    obtain ⟨p, hp1, hp2, hp3⟩ := h N
    exact ⟨p, hp1, hp2, hp3⟩
