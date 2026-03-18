import Mathlib

/-!
# ゴールドバッハ予想 (Goldbach's Conjecture)

2より大きい全ての偶数は、2つの素数の和で表せる。

1742年にゴールドバッハがオイラーに宛てた手紙で提唱。
約280年間未解決。

## 探索の概要

### 探索1: Mathlib調査
- Mathlibにゴールドバッハ予想の形式化は存在しない
- 利用可能な素数関連定理:
  - `Nat.Prime` の定義と基本性質 (`Data.Nat.Prime.Defs`)
  - 素数判定 (`norm_num` で小さい数は自動判定)
  - 素因数分解、最小素因数 (`minFac`)
  - 互いに素、素数のmod性質 (`Prime.eq_two_or_odd`)

### 探索2: Python数値実験 (scripts/goldbach_explore.py)
- 4 ≤ n ≤ 10000 の全偶数で予想成立を確認
- g(n)=1 となる偶数は 4, 6, 8, 12 の4個のみ
- g(n) は n/6 ≡ 0 のとき特に大きい（3の倍数の効果）
- Hardy-Littlewood 予想 g(n) ~ C₂·n/(ln n)² と概ね一致

### 探索3: Lean検証例の追加
- 8, 10, 12, 20, 100 での具体的検証
- ゴールドバッハ性の述語定義

### 探索4: mod 6/30 構造 (scripts/goldbach_mod_structure.py)
- mod 6 がg(n)を約2倍支配（n≡0 は平均127 vs n≡2,4 は 62-66）
- (p%6, q%6) の利用可能パターン数が差の主因

### 探索5: Hardy-Littlewood 予想式 (scripts/goldbach_hardy_littlewood.py)
- Singular series S(n) が g(n) の変動をよく説明
- S(n) が大きい偶数ほど g(n) が大きい

### 探索6: 弱いゴールドバッハ予想 (Helfgott 2013)
- IsWeakGoldbach, WeakGoldbachConjecture の定義
- goldbach_implies_weak_goldbach: 強い版 → 弱い版の含意を証明

### 探索7: mod 6 構造定理
- n ≡ 2 (mod 6) の Goldbach 分解 p+q=n (p,q>3 素数) は p ≡ q ≡ 1 (mod 6) のみ
- goldbach_mod6_implies_both_1: 4通りの場合分けで証明

### 探索8: 追加検証例
- 200 = 3+197, 500 = 13+487, 1000 = 3+997

### 探索9: n ≡ 0 (mod 6) の構造定理
- n ≡ 0 (mod 6) のとき p+q=n (p,q>3素数) は (p%6=1,q%6=5) ∨ (p%6=5,q%6=1)
- 1+5=6≡0 ✓, 5+1=6≡0 ✓, 1+1=2≡2 ✗, 5+5=10≡4 ✗

### 探索10: n ≡ 4 (mod 6) の構造定理
- n ≡ 4 (mod 6) のとき p+q=n (p,q>3素数) は p%6=5 ∧ q%6=5
- 5+5=10≡4 ✓ のみ

### 探索11: IsGoldbach の偶数性
- IsGoldbach n かつ n が奇数 → p=2 の分解が存在 (isGoldbach_odd_has_two)
- 偶数の IsGoldbach は4以上 (isGoldbach_even_ge_four)

### 探索12: 大きい検証例
- 2000 = 3+1997, 5000 = 7+4993, 10000 = 59+9941
- norm_num で4桁素数も判定可能であることを確認

### 探索13: isGoldbach_double_prime
- p が素数なら 2p は IsGoldbach (p + p = 2p)

### 探索14: ゴールドバッハ予想と素数ペアの一意性
- 10 = 5+5 の検証（既存の 3+7 と合わせて2通りの分解）
- isGoldbach_sum_comm: 素数 p+q → IsGoldbach(q+p)
-/

/-- ゴールドバッハ予想: 2より大きい全ての偶数は2つの素数の和で表せる -/
def GoldbachConjecture : Prop :=
  ∀ n : ℕ, n > 2 → n % 2 = 0 → ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

/-- 偶数 n がゴールドバッハ性を持つ: 2つの素数の和で表せる -/
def IsGoldbach (n : ℕ) : Prop :=
  ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q

/-! ## 小さい値での検証例 -/

-- 4 = 2 + 2
example : IsGoldbach 4 := ⟨2, 2, by norm_num, by norm_num, by norm_num⟩

-- 6 = 3 + 3
example : IsGoldbach 6 := ⟨3, 3, by norm_num, by norm_num, by norm_num⟩

-- 8 = 3 + 5
example : IsGoldbach 8 := ⟨3, 5, by norm_num, by norm_num, by norm_num⟩

-- 10 = 3 + 7
example : IsGoldbach 10 := ⟨3, 7, by norm_num, by norm_num, by norm_num⟩

-- 12 = 5 + 7
example : IsGoldbach 12 := ⟨5, 7, by norm_num, by norm_num, by norm_num⟩

-- 20 = 3 + 17
example : IsGoldbach 20 := ⟨3, 17, by norm_num, by norm_num, by norm_num⟩

-- 100 = 3 + 97
example : IsGoldbach 100 := ⟨3, 97, by norm_num, by norm_num, by norm_num⟩

/-! ## ゴールドバッハ性の基本補題 -/

/-- ゴールドバッハ予想は IsGoldbach を用いて同値に書ける -/
theorem goldbachConjecture_iff :
    GoldbachConjecture ↔ ∀ n : ℕ, n > 2 → n % 2 = 0 → IsGoldbach n := by
  unfold GoldbachConjecture IsGoldbach
  rfl

/-- 2つの素数の和は2以上 -/
theorem IsGoldbach.two_le {n : ℕ} (h : IsGoldbach n) : n ≥ 2 := by
  obtain ⟨p, q, hp, hq, heq⟩ := h
  have hp2 := hp.two_le
  have hq2 := hq.two_le
  omega

/-- 素数 p と素数 q の和は IsGoldbach -/
theorem isGoldbach_of_prime_add {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q) :
    IsGoldbach (p + q) :=
  ⟨p, q, hp, hq, rfl⟩

/-- 2つの奇素数の和は偶数 -/
theorem even_of_odd_prime_add {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) : Even (p + q) := by
  have hoddp := hp.odd_of_ne_two hp2
  have hoddq := hq.odd_of_ne_two hq2
  exact hoddp.add_odd hoddq

/-! ## 弱いゴールドバッハ予想 (Weak Goldbach Conjecture)

奇数版ゴールドバッハ予想、またはGoldbachの三素数予想とも呼ばれる。
「5より大きい全ての奇数は3つの素数の和で表せる」
2013年にHarald Helfgottにより証明された。
-/

/-- 自然数 n が弱いゴールドバッハ性を持つ: 3つの素数の和で表せる -/
def IsWeakGoldbach (n : ℕ) : Prop :=
  ∃ p q r : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ Nat.Prime r ∧ n = p + q + r

/-- 弱いゴールドバッハ予想: 5より大きい全ての奇数は3つの素数の和で表せる (Helfgott 2013) -/
def WeakGoldbachConjecture : Prop :=
  ∀ n : ℕ, n > 5 → n % 2 = 1 → IsWeakGoldbach n

/-! ## 弱いゴールドバッハ予想の小ケース検証 -/

-- 7 = 2 + 2 + 3
example : IsWeakGoldbach 7 := ⟨2, 2, 3, by norm_num, by norm_num, by norm_num, by norm_num⟩

-- 9 = 3 + 3 + 3
example : IsWeakGoldbach 9 := ⟨3, 3, 3, by norm_num, by norm_num, by norm_num, by norm_num⟩

-- 11 = 3 + 3 + 5
example : IsWeakGoldbach 11 := ⟨3, 3, 5, by norm_num, by norm_num, by norm_num, by norm_num⟩

-- 15 = 3 + 5 + 7
example : IsWeakGoldbach 15 := ⟨3, 5, 7, by norm_num, by norm_num, by norm_num, by norm_num⟩

-- 21 = 3 + 5 + 13
example : IsWeakGoldbach 21 := ⟨3, 5, 13, by norm_num, by norm_num, by norm_num, by norm_num⟩

/-! ## ゴールドバッハ予想と弱いゴールドバッハ予想の関係 -/

/-- ゴールドバッハ予想が成り立つならば、弱いゴールドバッハ予想も成り立つ -/
theorem goldbach_implies_weak_goldbach :
    GoldbachConjecture → WeakGoldbachConjecture := by
  intro hG n hn hodd
  -- n > 5 かつ n は奇数なので n - 3 > 2 かつ n - 3 は偶数
  -- n - 3 にゴールドバッハ予想を適用して p + q を得る
  -- すると n = 3 + p + q
  have hn3_gt : n - 3 > 2 := by omega
  have hn3_even : (n - 3) % 2 = 0 := by omega
  obtain ⟨p, q, hp, hq, heq⟩ := hG (n - 3) hn3_gt hn3_even
  exact ⟨3, p, q, by norm_num, hp, hq, by omega⟩

/-! ## 探索7: mod 6 構造定理 -/

/-- 3より大きい素数は mod 6 で 1 か 5 -/
private lemma prime_gt3_mod6 {p : ℕ} (hp : Nat.Prime p) (hp3 : p > 3) :
    p % 6 = 1 ∨ p % 6 = 5 := by
  have h2 : ¬(2 ∣ p) := by intro h; have := hp.eq_one_or_self_of_dvd 2 h; omega
  have h3 : ¬(3 ∣ p) := by intro h; have := hp.eq_one_or_self_of_dvd 3 h; omega
  have : p % 6 < 6 := Nat.mod_lt p (by norm_num)
  have h0 : p % 6 ≠ 0 := fun h => h2 ⟨p / 6 * 3, by omega⟩
  have h2' : p % 6 ≠ 2 := fun h => h2 ⟨p / 6 * 3 + 1, by omega⟩
  have h3' : p % 6 ≠ 3 := fun h => h3 ⟨p / 6 * 2 + 1, by omega⟩
  have h4 : p % 6 ≠ 4 := fun h => h2 ⟨p / 6 * 3 + 2, by omega⟩
  omega

/-- n ≡ 2 (mod 6) のとき、p+q=n かつ p,q > 3 素数ならば p ≡ 1 (mod 6) かつ q ≡ 1 (mod 6) -/
theorem goldbach_mod6_implies_both_1 {n p q : ℕ}
    (hn : n % 6 = 2) (hpq : p + q = n)
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hp3 : p > 3) (hq3 : q > 3) :
    p % 6 = 1 ∧ q % 6 = 1 := by
  have hpmod := prime_gt3_mod6 hp hp3
  have hqmod := prime_gt3_mod6 hq hq3
  have hsum : (p % 6 + q % 6) % 6 = 2 := by omega
  rcases hpmod with hp1 | hp5 <;> rcases hqmod with hq1 | hq5
  · exact ⟨hp1, hq1⟩
  · exfalso; omega
  · exfalso; omega
  · exfalso; omega

/-! ## 探索9: n ≡ 0 (mod 6) の構造定理 -/

/-- n % 6 = 0 のとき、p+q=n かつ p,q > 3 素数ならば
    (p%6=1 ∧ q%6=5) ∨ (p%6=5 ∧ q%6=1) -/
theorem goldbach_mod6_zero {n p q : ℕ}
    (hn : n % 6 = 0) (hpq : p + q = n)
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hp3 : p > 3) (hq3 : q > 3) :
    (p % 6 = 1 ∧ q % 6 = 5) ∨ (p % 6 = 5 ∧ q % 6 = 1) := by
  have hpmod := prime_gt3_mod6 hp hp3
  have hqmod := prime_gt3_mod6 hq hq3
  have hsum : (p % 6 + q % 6) % 6 = 0 := by omega
  rcases hpmod with hp1 | hp5 <;> rcases hqmod with hq1 | hq5
  · exfalso; omega
  · left; exact ⟨hp1, hq5⟩
  · right; exact ⟨hp5, hq1⟩
  · exfalso; omega

/-! ## 探索10: n ≡ 4 (mod 6) の構造定理 -/

/-- n % 6 = 4 のとき、p+q=n かつ p,q > 3 素数ならば p%6=5 ∧ q%6=5 -/
theorem goldbach_mod6_four {n p q : ℕ}
    (hn : n % 6 = 4) (hpq : p + q = n)
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hp3 : p > 3) (hq3 : q > 3) :
    p % 6 = 5 ∧ q % 6 = 5 := by
  have hpmod := prime_gt3_mod6 hp hp3
  have hqmod := prime_gt3_mod6 hq hq3
  have hsum : (p % 6 + q % 6) % 6 = 4 := by omega
  rcases hpmod with hp1 | hp5 <;> rcases hqmod with hq1 | hq5
  · exfalso; omega
  · exfalso; omega
  · exfalso; omega
  · exact ⟨hp5, hq5⟩

/-! ## 探索11: IsGoldbach の偶数性 -/

/-- IsGoldbach n かつ n が奇数ならば、p=2 の分解が存在する -/
theorem isGoldbach_odd_has_two {n : ℕ} (hg : IsGoldbach n) (hodd : n % 2 = 1) :
    ∃ q : ℕ, Nat.Prime q ∧ n = 2 + q := by
  obtain ⟨p, q, hp, hq, heq⟩ := hg
  by_cases hp2 : p = 2
  · exact ⟨q, hq, by omega⟩
  · by_cases hq2 : q = 2
    · exact ⟨p, hp, by omega⟩
    · -- p,q ともに奇数素数 → p+q は偶数 → 矛盾
      exfalso
      have heven := even_of_odd_prime_add hp hq hp2 hq2
      obtain ⟨k, hk⟩ := heven
      omega

/-- 偶数の IsGoldbach は4以上 -/
theorem isGoldbach_even_ge_four {n : ℕ} (hg : IsGoldbach n) (heven : n % 2 = 0) :
    n ≥ 4 := by
  obtain ⟨p, q, hp, hq, heq⟩ := hg
  have := hp.two_le
  have := hq.two_le
  omega

/-! ## 探索8: 追加検証例 -/

-- 200 = 3 + 197
example : IsGoldbach 200 := ⟨3, 197, by norm_num, by norm_num, by norm_num⟩

-- 500 = 13 + 487
example : IsGoldbach 500 := ⟨13, 487, by norm_num, by norm_num, by norm_num⟩

-- 1000 = 3 + 997
example : IsGoldbach 1000 := ⟨3, 997, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索12: 大きい検証例 -/

-- 2000 = 3 + 1997
example : IsGoldbach 2000 := ⟨3, 1997, by norm_num, by norm_num, by norm_num⟩

-- 5000 = 7 + 4993
example : IsGoldbach 5000 := ⟨7, 4993, by norm_num, by norm_num, by norm_num⟩

-- 10000 = 59 + 9941
example : IsGoldbach 10000 := ⟨59, 9941, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索13: isGoldbach_double_prime -/

/-- p が素数なら 2p は IsGoldbach -/
theorem isGoldbach_double_prime {p : ℕ} (hp : Nat.Prime p) : IsGoldbach (2 * p) :=
  ⟨p, p, hp, hp, by ring⟩

/-! ## 探索14: ゴールドバッハ予想と素数ペアの一意性 -/

/-- p+q = p'+q' = n で (p,q) ≠ (p',q') の具体例: 10 = 3+7 = 5+5 -/
example : IsGoldbach 10 := ⟨5, 5, by norm_num, by norm_num, by norm_num⟩
-- (既存の 3+7 と合わせて2通りの分解)

/-- 素数 + 素数 = 偶数 の系 -/
theorem isGoldbach_sum_comm {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q) :
    IsGoldbach (q + p) :=
  ⟨q, p, hq, hp, rfl⟩

/-! ## 探索15: ゴールドバッハ予想の同値な定式化 -/

/-- ゴールドバッハ予想は「全ての偶数 n ≥ 4 に対して IsGoldbach n」と同値 -/
theorem goldbachConjecture_iff_ge4 :
    GoldbachConjecture ↔ ∀ n : ℕ, n ≥ 4 → n % 2 = 0 → IsGoldbach n := by
  constructor
  · intro hG n hn heven
    exact hG n (by omega) heven
  · intro h n hn heven
    exact h n (by omega) heven

/-! ## 探索16: ゴールドバッハ分解の最小素数 -/

-- 30 = 7 + 23
example : IsGoldbach 30 := ⟨7, 23, by norm_num, by norm_num, by norm_num⟩

-- 50 = 3 + 47
example : IsGoldbach 50 := ⟨3, 47, by norm_num, by norm_num, by norm_num⟩

-- 42 = 5 + 37
example : IsGoldbach 42 := ⟨5, 37, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索17: IsGoldbach の合成 -/

-- IsGoldbach n かつ IsGoldbach m → IsGoldbach は和に関して閉じない（一般には）
-- しかし以下の特殊ケースは成り立つ:

/-- 4 は IsGoldbach (2+2) -/
example : IsGoldbach 4 := ⟨2, 2, by norm_num, by norm_num, by norm_num⟩
-- 既存だが明示的に再確認

/-- 偶数 + 偶数 = 偶数 の場合は可能性がある -/
-- 14 = 3 + 11
example : IsGoldbach 14 := ⟨3, 11, by norm_num, by norm_num, by norm_num⟩
-- 16 = 3 + 13
example : IsGoldbach 16 := ⟨3, 13, by norm_num, by norm_num, by norm_num⟩
-- 18 = 5 + 13
example : IsGoldbach 18 := ⟨5, 13, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索18: 連続偶数の IsGoldbach -/

-- 22 = 3 + 19
example : IsGoldbach 22 := ⟨3, 19, by norm_num, by norm_num, by norm_num⟩
-- 24 = 5 + 19
example : IsGoldbach 24 := ⟨5, 19, by norm_num, by norm_num, by norm_num⟩
-- 26 = 3 + 23
example : IsGoldbach 26 := ⟨3, 23, by norm_num, by norm_num, by norm_num⟩
-- 28 = 5 + 23
example : IsGoldbach 28 := ⟨5, 23, by norm_num, by norm_num, by norm_num⟩

/-- 全ての素数 p ≥ 2 に対し 2p は IsGoldbach（isGoldbach_double_prime の系） -/
-- 既存だが、具体例:
-- 2·11 = 22
example : IsGoldbach 22 := isGoldbach_double_prime (by norm_num : Nat.Prime 11)

/-! ## 探索19: ゴールドバッハ検証の系統化 -/

-- 連続偶数 32-40
example : IsGoldbach 32 := ⟨3, 29, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 34 := ⟨3, 31, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 36 := ⟨5, 31, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 38 := ⟨7, 31, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 40 := ⟨3, 37, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索20: 3桁の偶数の検証 -/

example : IsGoldbach 102 := ⟨5, 97, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 110 := ⟨3, 107, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 150 := ⟨11, 139, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索21: mod 6 構造と組み合わせた検証 -/

-- 6k (k≥9) の検証例
-- 54 = 7 + 47
example : IsGoldbach 54 := ⟨7, 47, by norm_num, by norm_num, by norm_num⟩
-- 60 = 7 + 53
example : IsGoldbach 60 := ⟨7, 53, by norm_num, by norm_num, by norm_num⟩
-- 66 = 5 + 61
example : IsGoldbach 66 := ⟨5, 61, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索22: IsGoldbach と偶数性の関係 -/

-- 300 = 7 + 293
example : IsGoldbach 300 := ⟨7, 293, by norm_num, by norm_num, by norm_num⟩
-- 400 = 11 + 389
example : IsGoldbach 400 := ⟨11, 389, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索23: 500未満の偶数検証例の補充 -/

-- 72 = 5 + 67
example : IsGoldbach 72 := ⟨5, 67, by norm_num, by norm_num, by norm_num⟩
-- 80 = 7 + 73
example : IsGoldbach 80 := ⟨7, 73, by norm_num, by norm_num, by norm_num⟩
-- 90 = 7 + 83
example : IsGoldbach 90 := ⟨7, 83, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索24: 100の倍数の検証 -/
-- 600 = 7 + 593
example : IsGoldbach 600 := ⟨7, 593, by norm_num, by norm_num, by norm_num⟩
-- 700 = 17 + 683
example : IsGoldbach 700 := ⟨17, 683, by norm_num, by norm_num, by norm_num⟩
-- 800 = 3 + 797
example : IsGoldbach 800 := ⟨3, 797, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索25: 1000台の検証 -/
-- 1100 = 3 + 1097
example : IsGoldbach 1100 := ⟨3, 1097, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索26: 偶数の系統的検証（4-100の全偶数） -/

-- 44 = 3 + 41
example : IsGoldbach 44 := ⟨3, 41, by norm_num, by norm_num, by norm_num⟩
-- 46 = 3 + 43
example : IsGoldbach 46 := ⟨3, 43, by norm_num, by norm_num, by norm_num⟩
-- 48 = 5 + 43
example : IsGoldbach 48 := ⟨5, 43, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索27: 偶数の系統的検証（続き） -/

example : IsGoldbach 52 := ⟨5, 47, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 56 := ⟨3, 53, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 58 := ⟨5, 53, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 62 := ⟨3, 59, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 64 := ⟨3, 61, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 68 := ⟨7, 61, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 70 := ⟨3, 67, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 74 := ⟨3, 71, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 76 := ⟨3, 73, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 78 := ⟨5, 73, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 82 := ⟨3, 79, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 84 := ⟨5, 79, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 86 := ⟨3, 83, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 88 := ⟨5, 83, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 92 := ⟨3, 89, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 94 := ⟨5, 89, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 96 := ⟨7, 89, by norm_num, by norm_num, by norm_num⟩
example : IsGoldbach 98 := ⟨19, 79, by norm_num, by norm_num, by norm_num⟩

/-! ## 探索28: 偶数 74-100 の個別 Goldbach 検証（4-72は既出） -/
