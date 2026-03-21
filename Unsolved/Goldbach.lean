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

/-! ## ゴールドバッハ予想と弱ゴールドバッハ予想の定量的関係 -/

/-- n > 7 が奇数のとき、IsGoldbach (n - 3) → IsWeakGoldbach n
    n - 3 は偶数かつ > 4 なのでゴールドバッハ分解 p + q = n - 3 が存在し、
    n = 3 + p + q と書ける。 -/
theorem weakGoldbach_of_goldbach_sub3 {n : ℕ} (hn : n > 7) (hodd : n % 2 = 1)
    (hg : IsGoldbach (n - 3)) : IsWeakGoldbach n := by
  obtain ⟨p, q, hp, hq, heq⟩ := hg
  exact ⟨3, p, q, by norm_num, hp, hq, by omega⟩

/-! ## 探索: IsGoldbach の追加性質 -/

/-- 6以上の偶数が IsGoldbach なら、少なくとも1つの奇素数を含む分解が存在 -/
theorem isGoldbach_has_odd_prime {n : ℕ} (hg : IsGoldbach n) (hn : n ≥ 6) (heven : n % 2 = 0) :
    ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q ∧ p % 2 = 1 := by
  obtain ⟨p, q, hp, hq, heq⟩ := hg
  by_cases hp2 : p = 2
  · -- p = 2 → q = n - 2 ≥ 4 > 2 → q は奇素数
    subst hp2
    have hq_gt2 : q ≠ 2 := by omega
    have hodd_q := hq.odd_of_ne_two hq_gt2
    have hq_mod : q % 2 = 1 := Nat.odd_iff.mp hodd_q
    exact ⟨q, 2, hq, by norm_num, by omega, hq_mod⟩
  · -- p ≠ 2 → p は奇素数
    have hodd_p := hp.odd_of_ne_two hp2
    have hp_mod : p % 2 = 1 := Nat.odd_iff.mp hodd_p
    exact ⟨p, q, hp, hq, heq, hp_mod⟩

/-- IsGoldbach 4 の唯一の分解は 2+2 -/
theorem isGoldbach_four_unique {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 4 = p + q) : p = 2 ∧ q = 2 := by
  have hp2 := hp.two_le
  have hq2 := hq.two_le
  omega

/-- 偶数 n の IsGoldbach で p = q の場合、n = 2p -/
theorem isGoldbach_eq_double {n p : ℕ} (_hp : Nat.Prime p) (heq : n = p + p) :
    n = 2 * p := by omega

-- =============================================================================
-- 2つの奇素数の和の偶数性（精密版）
-- =============================================================================

/-! ## 2つの奇素数の和は偶数

IsGoldbach の分解 n = p + q において p, q がともに奇素数（≠ 2）ならば
n は偶数である。even_of_odd_prime_add の系として n % 2 = 0 を直接示す。
-/

/-- 2つの奇素数の和は mod 2 で 0 -/
theorem isGoldbach_both_odd_implies_even {n p q : ℕ}
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hp2 : p ≠ 2) (hq2 : q ≠ 2)
    (heq : n = p + q) : n % 2 = 0 := by
  have heven := even_of_odd_prime_add hp hq hp2 hq2
  obtain ⟨k, hk⟩ := heven
  omega

/-! ## IsGoldbach の小さい素数による分解 -/

/-- IsGoldbach n なら n/2 以下の素数 p で分解可能:
    p + q = n で p > n/2 なら q < n/2 なので p, q を入れ替えればよい -/
theorem isGoldbach_small_prime {n : ℕ} (hg : IsGoldbach n) :
    ∃ p q : ℕ, Nat.Prime p ∧ Nat.Prime q ∧ n = p + q ∧ p ≤ n / 2 := by
  obtain ⟨p, q, hp, hq, heq⟩ := hg
  by_cases hle : p ≤ n / 2
  · exact ⟨p, q, hp, hq, heq, hle⟩
  · push_neg at hle
    have hq_le : q ≤ n / 2 := by omega
    exact ⟨q, p, hq, hp, by omega, hq_le⟩

/-! ## 2つの素数の和で一方が2の場合 -/

/-- n - 2 が素数かつ n ≥ 4 なら IsGoldbach n -/
theorem isGoldbach_with_two {n : ℕ} (hp : Nat.Prime (n - 2)) (hn : n ≥ 4) :
    IsGoldbach n := by
  exact ⟨2, n - 2, by norm_num, hp, by omega⟩

/-! ## 有界検証: 全偶数 4 ≤ n ≤ 1000 の Goldbach 性 -/

/-- isGoldbachBool: n がゴールドバッハ性を持つかをブール判定する関数
    p を 2 から n/2 まで走査し、p が素数かつ n-p が素数であるか確認 -/
def isGoldbachBool (n : ℕ) : Bool :=
  if n < 4 then false
  else if n % 2 ≠ 0 then false
  else
    (List.range (n / 2 - 1)).any fun i =>
      let p := i + 2
      decide (Nat.Prime p) && decide (Nat.Prime (n - p))

/-- isGoldbachBool が true ならば IsGoldbach -/
theorem isGoldbach_of_bool {n : ℕ} (h : isGoldbachBool n = true) : IsGoldbach n := by
  simp only [isGoldbachBool] at h
  split at h
  · simp at h
  · rename_i h_ge
    push_neg at h_ge
    split at h
    · simp at h
    · rename_i h_even
      push_neg at h_even
      have heven : n % 2 = 0 := by omega
      simp only [List.any_eq_true, List.mem_range] at h
      obtain ⟨i, hi_range, hi⟩ := h
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hi
      have hp := hi.1
      have hq := hi.2
      have : i + 2 ≤ n := by omega
      exact ⟨i + 2, n - (i + 2), hp, hq, by omega⟩

/-- goldbachCheck: bound 以下の全偶数 ≥ 4 が isGoldbachBool で true かを判定 -/
def goldbachCheck (bound : ℕ) : Bool :=
  (List.range (bound + 1)).all fun n =>
    if n < 4 then true
    else if n % 2 ≠ 0 then true
    else isGoldbachBool n

/-- goldbachCheck が true ならば、bound 以下の全偶数 ≥ 4 で IsGoldbach -/
theorem isGoldbach_of_check {bound : ℕ} (hcheck : goldbachCheck bound = true)
    (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ bound) (heven : n % 2 = 0) : IsGoldbach n := by
  simp only [goldbachCheck, List.all_eq_true, List.mem_range, Bool.ite_eq_true_distrib] at hcheck
  have hmem : n < bound + 1 := by omega
  have := hcheck n hmem
  split at this
  · omega
  · split at this
    · omega
    · exact isGoldbach_of_bool this

set_option maxHeartbeats 8000000 in
set_option linter.style.nativeDecide false in
-- 1000以下の全偶数(≥4)について native_decide で isGoldbachBool を評価
/-- 全ての偶数 n (4 ≤ n ≤ 1000) は2つの素数の和で表せる -/
theorem isGoldbach_even_le_1000 (n : ℕ) (hn4 : n ≥ 4) (hn1000 : n ≤ 1000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  have hcheck : goldbachCheck 1000 = true := by native_decide
  exact isGoldbach_of_check hcheck n hn4 hn1000 heven

set_option maxHeartbeats 40000000 in
set_option linter.style.nativeDecide false in
/-- 全ての偶数 n (4 ≤ n ≤ 10000) は2つの素数の和で表せる
    5000個の偶数の検証。素数判定が各 O(√n) で n ≤ 10000 なので十分高速。 -/
theorem isGoldbach_even_le_10000 (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ 10000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  have hcheck : goldbachCheck 10000 = true := by native_decide
  exact isGoldbach_of_check hcheck n hn4 hn heven

/-! ## Goldbach と素数分布 -/

/-- p + q = n で p ≤ q なら q ≥ n/2 -/
theorem goldbach_larger_prime {n p q : ℕ} (_hp : Nat.Prime p) (_hq : Nat.Prime q)
    (heq : n = p + q) (hle : p ≤ q) : q ≥ n / 2 := by omega

/-! ## 有界検証: 全偶数 4 ≤ n ≤ 50000 の Goldbach 性 -/

set_option maxHeartbeats 400000000 in
set_option linter.style.nativeDecide false in
/-- 全ての偶数 n (4 ≤ n ≤ 50000) は2つの素数の和で表せる -/
theorem isGoldbach_even_le_50000 (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ 50000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  have hcheck : goldbachCheck 50000 = true := by native_decide
  exact isGoldbach_of_check hcheck n hn4 hn heven

set_option maxHeartbeats 4000000000 in
set_option linter.style.nativeDecide false in
/-- 全ての偶数 n (4 ≤ n ≤ 100000) は2つの素数の和で表せる
    50000偶数の検証。native_decide で素数判定を実行。 -/
theorem isGoldbach_even_le_100000 (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ 100000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  have hcheck : goldbachCheck 100000 = true := by native_decide
  exact isGoldbach_of_check hcheck n hn4 hn heven

/-! ## 有界検証: 全偶数 4 ≤ n ≤ 500000 の Goldbach 性 -/

/-- goldbachCheckRange: [lo, hi] の全偶数 ≥ 4 が isGoldbachBool で true かを判定 -/
def goldbachCheckRange (lo hi : ℕ) : Bool :=
  (List.range (hi - lo + 1)).all fun i =>
    let n := lo + i
    if n < 4 then true
    else if n % 2 ≠ 0 then true
    else isGoldbachBool n

/-- goldbachCheckRange が true ならば、範囲内の全偶数 ≥ 4 で IsGoldbach -/
theorem isGoldbach_of_checkRange {lo hi : ℕ} (hcheck : goldbachCheckRange lo hi = true)
    (n : ℕ) (hn4 : n ≥ 4) (hlo : n ≥ lo) (hhi : n ≤ hi) (heven : n % 2 = 0) :
    IsGoldbach n := by
  simp only [goldbachCheckRange, List.all_eq_true, List.mem_range, Bool.ite_eq_true_distrib] at hcheck
  have hmem : n - lo < hi - lo + 1 := by omega
  have := hcheck (n - lo) hmem
  simp only [Nat.add_sub_cancel' (by omega : lo ≤ n)] at this
  split at this
  · omega
  · split at this
    · omega
    · exact isGoldbach_of_bool this

set_option linter.style.nativeDecide false in
/-- 100001 ≤ n ≤ 200000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_100001_200000 : goldbachCheckRange 100001 200000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 200001 ≤ n ≤ 300000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_200001_300000 : goldbachCheckRange 200001 300000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 300001 ≤ n ≤ 400000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_300001_400000 : goldbachCheckRange 300001 400000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 400001 ≤ n ≤ 500000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_400001_500000 : goldbachCheckRange 400001 500000 = true := by
  native_decide

/-- 全ての偶数 n (4 ≤ n ≤ 500000) は2つの素数の和で表せる
    250000個の偶数の検証。100000 までは既存の定理を再利用し、
    残りは100000ずつ4分割して検証。 -/
theorem isGoldbach_even_le_500000 (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ 500000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  by_cases h100 : n ≤ 100000
  · exact isGoldbach_even_le_100000 n hn4 h100 heven
  · push_neg at h100
    by_cases h200 : n ≤ 200000
    · exact isGoldbach_of_checkRange goldbachCheckRange_100001_200000 n hn4 (by omega) h200 heven
    · push_neg at h200
      by_cases h300 : n ≤ 300000
      · exact isGoldbach_of_checkRange goldbachCheckRange_200001_300000 n hn4 (by omega) h300 heven
      · push_neg at h300
        by_cases h400 : n ≤ 400000
        · exact isGoldbach_of_checkRange goldbachCheckRange_300001_400000 n hn4 (by omega) h400 heven
        · exact isGoldbach_of_checkRange goldbachCheckRange_400001_500000 n hn4 (by omega) hn heven

/-! ## 有界検証: 全偶数 4 ≤ n ≤ 1000000 の Goldbach 性 -/

set_option linter.style.nativeDecide false in
/-- 500001 ≤ n ≤ 600000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_500001_600000 : goldbachCheckRange 500001 600000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 600001 ≤ n ≤ 700000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_600001_700000 : goldbachCheckRange 600001 700000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 700001 ≤ n ≤ 800000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_700001_800000 : goldbachCheckRange 700001 800000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 800001 ≤ n ≤ 900000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_800001_900000 : goldbachCheckRange 800001 900000 = true := by
  native_decide

set_option linter.style.nativeDecide false in
/-- 900001 ≤ n ≤ 1000000 の全偶数は IsGoldbach -/
theorem goldbachCheckRange_900001_1000000 : goldbachCheckRange 900001 1000000 = true := by
  native_decide

/-- 全ての偶数 n (4 ≤ n ≤ 1000000) は2つの素数の和で表せる
    500000個の偶数の検証。500000 までは既存の定理を再利用し、
    残りは100000ずつ5分割して検証。 -/
theorem isGoldbach_even_le_1000000 (n : ℕ) (hn4 : n ≥ 4) (hn : n ≤ 1000000) (heven : n % 2 = 0) :
    IsGoldbach n := by
  by_cases h500 : n ≤ 500000
  · exact isGoldbach_even_le_500000 n hn4 h500 heven
  · push_neg at h500
    by_cases h600 : n ≤ 600000
    · exact isGoldbach_of_checkRange goldbachCheckRange_500001_600000 n hn4 (by omega) h600 heven
    · push_neg at h600
      by_cases h700 : n ≤ 700000
      · exact isGoldbach_of_checkRange goldbachCheckRange_600001_700000 n hn4 (by omega) h700 heven
      · push_neg at h700
        by_cases h800 : n ≤ 800000
        · exact isGoldbach_of_checkRange goldbachCheckRange_700001_800000 n hn4 (by omega) h800 heven
        · push_neg at h800
          by_cases h900 : n ≤ 900000
          · exact isGoldbach_of_checkRange goldbachCheckRange_800001_900000 n hn4 (by omega) h900 heven
          · exact isGoldbach_of_checkRange goldbachCheckRange_900001_1000000 n hn4 (by omega) hn heven

/-! ## Goldbach予想が偶数 ≤ N まで成立するなら弱Goldbach予想も奇数 ≤ N+3 まで成立 -/

/-- Goldbach予想が偶数 ≤ N まで成立するなら、弱Goldbach予想も奇数 ≤ N+3 まで成立 -/
theorem weakGoldbach_of_goldbach_le {N : ℕ}
    (hG : ∀ n, n ≥ 4 → n ≤ N → n % 2 = 0 → IsGoldbach n)
    (m : ℕ) (hm : m > 7) (hm_le : m ≤ N + 3) (hodd : m % 2 = 1) :
    IsWeakGoldbach m := by
  have hm3 : m - 3 ≥ 4 := by omega
  have hm3_le : m - 3 ≤ N := by omega
  have hm3_even : (m - 3) % 2 = 0 := by omega
  obtain ⟨p, q, hp, hq, heq⟩ := hG (m - 3) hm3 hm3_le hm3_even
  exact ⟨3, p, q, by norm_num, hp, hq, by omega⟩

/-- Goldbach予想が100万まで成立 + weakGoldbach_of_goldbach_le の系:
    全奇数 8 ≤ m ≤ 1000003 は3つの素数の和（弱Goldbach） -/
theorem weakGoldbach_le_1000003 (m : ℕ) (hm : m > 7) (hm_le : m ≤ 1000003) (hodd : m % 2 = 1) :
    IsWeakGoldbach m :=
  weakGoldbach_of_goldbach_le
    (fun n hn4 hn_le heven => isGoldbach_even_le_1000000 n hn4 (by omega) heven)
    m hm hm_le hodd

/-! ## 最終まとめ: Goldbach予想の総合的形式化 -/

/-- Goldbach予想が偶数 ≤ 1000000 で成り立つ -/
theorem goldbachConjecture_verified_le_1000000 :
    ∀ n : ℕ, n ≥ 4 → n ≤ 1000000 → n % 2 = 0 → IsGoldbach n :=
  fun n hn4 hn heven => isGoldbach_even_le_1000000 n hn4 hn heven

/-- 弱Goldbach予想が奇数 ≤ 1000003 で成り立つ -/
theorem weakGoldbachConjecture_verified_le_1000003 :
    ∀ m : ℕ, m > 7 → m ≤ 1000003 → m % 2 = 1 → IsWeakGoldbach m :=
  fun m hm hm_le hodd => weakGoldbach_le_1000003 m hm hm_le hodd

/-! ## IsGoldbach 6 の全分解の列挙 -/

/-- IsGoldbach 6 の全分解の列挙: 6 = 3+3 のみ -/
theorem isGoldbach_six_unique {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 6 = p + q) (hle : p ≤ q) : p = 3 ∧ q = 3 := by
  have hp2 := hp.two_le
  have hq2 := hq.two_le
  have hpub : p ≤ 3 := by omega
  interval_cases p
  · -- p = 2 → q = 4, 4 は素数でないので矛盾
    have hq4 : q = 4 := by omega
    subst hq4; exact absurd hq (by decide)
  · exact ⟨rfl, by omega⟩

/-! ## n-3 が素数の場合の Goldbach 分解 -/

/-- 偶数 n ≥ 6 で n-3 が素数なら、n = 3 + (n-3) の分解を持つ -/
theorem isGoldbach_with_three {n : ℕ} (hp : Nat.Prime (n - 3)) (hn : n ≥ 6) (heven : n % 2 = 0) :
    IsGoldbach n := by
  exact ⟨3, n - 3, by norm_num, hp, by omega⟩

/-! ## Goldbach 分解の一意性と多重性 -/

/-- IsGoldbach 8 の一意性: 8 = p+q, p≤q, 素数 → p=3, q=5 -/
theorem isGoldbach_eight_unique {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 8 = p + q) (hle : p ≤ q) : p = 3 ∧ q = 5 := by
  have hp2 := hp.two_le; have hq2 := hq.two_le
  have hpub : p ≤ 4 := by omega
  interval_cases p
  · -- p = 2: q = 6, not prime
    have hq6 : q = 6 := by omega
    subst hq6; exact absurd hq (by decide)
  · -- p = 3: q = 5
    exact ⟨rfl, by omega⟩
  · -- p = 4: not prime
    exact absurd hp (by decide)

/-- IsGoldbach 10 は2通りの分解: 3+7 と 5+5 -/
theorem isGoldbach_ten_two_ways :
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ 10 = p + q ∧ p < q) ∧
    (∃ p, Nat.Prime p ∧ 10 = p + p) :=
  ⟨⟨3, 7, by norm_num, by norm_num, by norm_num, by omega⟩,
   ⟨5, by norm_num, by norm_num⟩⟩

/-- IsGoldbach 12 の分解: 12=5+7のみ（p≤q前提） -/
theorem isGoldbach_twelve_unique {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 12 = p + q) (hle : p ≤ q) : p = 5 ∧ q = 7 := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 12 - p := by omega
  subst hq_val; have : p ≤ 12 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- 偶数 n で n/2 が素数なら IsGoldbach n -/
theorem isGoldbach_of_half_prime {n : ℕ} (hn : n ≥ 4) (heven : n % 2 = 0)
    (hp : Nat.Prime (n / 2)) : IsGoldbach n :=
  ⟨n / 2, n / 2, hp, hp, by omega⟩

/-- IsGoldbach 14 の一意性: 14 = p+q, p≤q → p=3∧q=11 ∨ p=7∧q=7 -/
theorem isGoldbach_fourteen_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 14 = p + q) (hle : p ≤ q) : (p = 3 ∧ q = 11) ∨ (p = 7 ∧ q = 7) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 14 - p := by omega
  subst hq_val; have : p ≤ 14 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 16 の分解列挙: 16=3+13 か 16=5+11 -/
theorem isGoldbach_sixteen_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 16 = p + q) (hle : p ≤ q) : (p = 3 ∧ q = 13) ∨ (p = 5 ∧ q = 11) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 16 - p := by omega
  subst hq_val; have : p ≤ 16 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 18 の分解: 18=5+13 か 18=7+11 -/
theorem isGoldbach_eighteen_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 18 = p + q) (hle : p ≤ q) : (p = 5 ∧ q = 13) ∨ (p = 7 ∧ q = 11) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 18 - p := by omega
  subst hq_val; have : p ≤ 18 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 20 の分解: 20=3+17 か 20=7+13 -/
theorem isGoldbach_twenty_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 20 = p + q) (hle : p ≤ q) : (p = 3 ∧ q = 17) ∨ (p = 7 ∧ q = 13) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 20 - p := by omega
  subst hq_val; have : p ≤ 20 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- 22のゴールドバッハ分解: 3+19, 5+17, 11+11 -/
theorem isGoldbach_twentytwo_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 22 = p + q) (hle : p ≤ q) : (p = 3 ∧ q = 19) ∨ (p = 5 ∧ q = 17) ∨ (p = 11 ∧ q = 11) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 22 - p := by omega
  subst hq_val; have : p ≤ 22 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

theorem isGoldbach_twentyfour_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 24 = p + q) (hle : p ≤ q) : (p = 5 ∧ q = 19) ∨ (p = 7 ∧ q = 17) ∨ (p = 11 ∧ q = 13) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 24 - p := by omega
  subst hq_val; have : p ≤ 24 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 26 の分解: 26=3+23 か 26=7+19 か 26=13+13 -/
theorem isGoldbach_twentysix_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 26 = p + q) (hle : p ≤ q) :
    (p = 3 ∧ q = 23) ∨ (p = 7 ∧ q = 19) ∨ (p = 13 ∧ q = 13) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 26 - p := by omega
  subst hq_val; have : p ≤ 26 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- 28のゴールドバッハ分解: 28 = 5 + 23 または 28 = 11 + 17 -/
theorem isGoldbach_twentyeight_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 28 = p + q) (hle : p ≤ q) :
    (p = 5 ∧ q = 23) ∨ (p = 11 ∧ q = 17) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 28 - p := by omega
  subst hq_val; have : p ≤ 28 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- 30 のゴールドバッハ分解: 30 = 7+23 = 11+19 = 13+17 -/
theorem isGoldbach_thirty_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 30 = p + q) (hle : p ≤ q) :
    (p = 7 ∧ q = 23) ∨ (p = 11 ∧ q = 19) ∨ (p = 13 ∧ q = 17) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 30 - p := by omega
  subst hq_val; have : p ≤ 30 := by omega
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact ⟨rfl, rfl⟩ | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 32 の分解 -/
theorem isGoldbach_thirtytwo_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 32 = p + q) (hle : p ≤ q) :
    (p = 3 ∧ q = 29) ∨ (p = 13 ∧ q = 19) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 32 - p := by omega
  subst hq_val; have : p ≤ 32 := by omega
  interval_cases p <;>
    (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr ⟨rfl, rfl⟩
           | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach 34 の分解: 3+31, 5+29, 11+23, 17+17 -/
theorem isGoldbach_thirtyfour_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 34 = p + q) (hle : p ≤ q) :
    (p = 3 ∧ q = 31) ∨ (p = 5 ∧ q = 29) ∨ (p = 11 ∧ q = 23) ∨ (p = 17 ∧ q = 17) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 34 - p := by omega
  subst hq_val; have : p ≤ 34 := by omega
  interval_cases p <;>
    (first | exact Or.inl ⟨rfl, rfl⟩
           | exact Or.inr (Or.inl ⟨rfl, rfl⟩)
           | exact Or.inr (Or.inr (Or.inl ⟨rfl, rfl⟩))
           | exact Or.inr (Or.inr (Or.inr ⟨rfl, rfl⟩))
           | exact absurd hp (by decide)
           | exact absurd hq (by decide)
           | omega)

/-- 36のゴールドバッハ分割の分類 -/
theorem isGoldbach_thirtysix_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 36 = p + q) (hle : p ≤ q) :
    (p = 5 ∧ q = 31) ∨ (p = 7 ∧ q = 29) ∨
    (p = 13 ∧ q = 23) ∨ (p = 17 ∧ q = 19) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 36 - p := by omega
  subst hq_val; have : p ≤ 36 := by omega
  interval_cases p <;>
    (first
      | exact Or.inl ⟨rfl, rfl⟩
      | exact Or.inr (Or.inl ⟨rfl, rfl⟩)
      | exact Or.inr (Or.inr (Or.inl ⟨rfl, rfl⟩))
      | exact Or.inr (Or.inr (Or.inr ⟨rfl, rfl⟩))
      | exact absurd hp (by decide)
      | exact absurd hq (by decide)
      | omega)

/-- 38のゴールドバッハ分割の分類 -/
theorem isGoldbach_thirtyeight_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 38 = p + q) (hle : p ≤ q) :
    (p = 7 ∧ q = 31) ∨ (p = 19 ∧ q = 19) := by
  have := hp.two_le; have := hq.two_le
  have hq_val : q = 38 - p := by omega
  subst hq_val; have : p ≤ 38 := by omega
  interval_cases p <;>
    (first
      | exact Or.inl ⟨rfl, rfl⟩
      | exact Or.inr ⟨rfl, rfl⟩
      | exact absurd hp (by decide)
      | exact absurd hq (by decide)
      | omega)

/-- 40 のゴールドバッハ分解は (3,37), (11,29), (17,23) の3通り -/
theorem isGoldbach_forty_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 40 = p + q) (hle : p ≤ q) :
    (p = 3 ∧ q = 37) ∨ (p = 11 ∧ q = 29) ∨ (p = 17 ∧ q = 23) := by
  have hp2 := hp.two_le; have hq2 := hq.two_le
  have hpub : p ≤ 20 := by omega
  have hq_eq : q = 40 - p := by omega
  subst hq_eq
  interval_cases p <;> (first | exact Or.inl ⟨rfl, rfl⟩ | exact Or.inr (Or.inl ⟨rfl, rfl⟩) | exact Or.inr (Or.inr ⟨rfl, rfl⟩) | exact absurd hp (by decide) | exact absurd hq (by decide) | omega)

/-- IsGoldbach n → n ≠ 2（2は2つの素数の和で表せない: 最小の素数は2であり 2+2=4≠2） -/
theorem isGoldbach_ne_two {n : ℕ} (h : IsGoldbach n) : n ≠ 2 := by
  intro h2; subst h2
  obtain ⟨p, q, hp, hq, heq⟩ := h
  have := hp.two_le; have := hq.two_le; omega

/-- IsGoldbach n → n ≠ 1（1は2つの素数の和で表せない: 最小の素数は2であり 2+2=4>1） -/
theorem isGoldbach_ne_one {n : ℕ} (h : IsGoldbach n) : n ≠ 1 := by
  intro h1; subst h1; obtain ⟨p, q, hp, hq, heq⟩ := h
  have := hp.two_le; have := hq.two_le; omega

/-- IsGoldbach n → n ≠ 0 -/
theorem isGoldbach_ne_zero {n : ℕ} (h : IsGoldbach n) : n ≠ 0 := by
  intro h0; subst h0; obtain ⟨p, q, hp, hq, heq⟩ := h
  have := hp.two_le; omega

/-- IsGoldbach n → n ≠ 3 -/
theorem isGoldbach_ne_three {n : ℕ} (h : IsGoldbach n) : n ≠ 3 := by
  intro h3; subst h3; obtain ⟨p, q, hp, hq, heq⟩ := h
  have := hp.two_le; have := hq.two_le; omega

/-- IsGoldbach n → n ≥ 4（0,1,2,3 はいずれも2つの素数の和で表せない） -/
theorem isGoldbach_ge_four {n : ℕ} (h : IsGoldbach n) : n ≥ 4 := by
  have h0 := isGoldbach_ne_zero h
  have h1 := isGoldbach_ne_one h
  have h2 := isGoldbach_ne_two h
  have h3 := isGoldbach_ne_three h
  omega

/-- IsGoldbach n かつ n 偶数 → n/2 は正整数 -/
theorem isGoldbach_half_pos {n : ℕ} (h : IsGoldbach n) (heven : n % 2 = 0) : n / 2 ≥ 2 := by
  have := isGoldbach_ge_four h; omega

/-- IsGoldbach n ∧ IsGoldbach m → n + m ≥ 8 -/
theorem isGoldbach_sum_ge {n m : ℕ} (hn : IsGoldbach n) (hm : IsGoldbach m) :
    n + m ≥ 8 := by
  have := isGoldbach_ge_four hn; have := isGoldbach_ge_four hm; omega

set_option maxHeartbeats 800000 in
/-- IsGoldbach 42 の分解 -/
theorem isGoldbach_fortytwo_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 42 = p + q) (hle : p ≤ q) :
    (p = 5 ∧ q = 37) ∨ (p = 11 ∧ q = 31) ∨ (p = 13 ∧ q = 29) ∨ (p = 19 ∧ q = 23) := by
  have h1 := hp.two_le; have h2 := hq.two_le
  have h3 : p ≤ 40 := by omega
  have hq_eq : q = 42 - p := by omega
  subst hq_eq
  interval_cases p <;> first | omega | (exfalso; revert hp; decide) |
    (exfalso; revert hq; decide)

set_option maxHeartbeats 800000 in
/-- IsGoldbach 44 の分解 -/
theorem isGoldbach_fortyfour_cases {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q)
    (heq : 44 = p + q) (hle : p ≤ q) :
    (p = 3 ∧ q = 41) ∨ (p = 7 ∧ q = 37) ∨ (p = 13 ∧ q = 31) := by
  have h1 := hp.two_le; have h2 := hq.two_le
  have h3 : p ≤ 42 := by omega
  have hq_eq : q = 44 - p := by omega
  subst hq_eq
  interval_cases p <;> first | omega | (exfalso; revert hp; decide) |
    (exfalso; revert hq; decide)
