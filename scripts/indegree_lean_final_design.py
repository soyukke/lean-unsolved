"""
Indegree.lean 最終設計 (探索122)

collatzStep の逆像を完全分類し、入次数 <= 2 を Lean 4 で証明するための
詳細設計書。全ての算術的事実は omega で解決可能であることを検証済み。

6 + 2 = 8 補題の依存関係と証明戦略を文書化。
"""

LEAN_SKETCH = r"""
import Unsolved.Collatz.Defs

/-!
# コラッツグラフの入次数分析 (Indegree)

collatzStep の逆像（前駆ノード）を完全に分類し、
入次数が最大2であることを証明する。

## 前駆ノードの数学的分類
collatzStep(m) = n を満たす正整数 m:
- **偶数前駆**: m = 2n (常に存在、m は偶数で m/2 = n)
- **奇数前駆**: m = (n-1)/3 (n % 6 = 4 のときのみ存在、m は奇数で 3m+1 = n)

## 補題構成 (8補題)
1. `collatzStep_double` - 偶数前駆の構成
2. `collatzStep_odd_predecessor` - 奇数前駆の構成
3. `collatzStep_even_pred_unique` - 偶数前駆の一意性
4. `collatzStep_odd_pred_unique` - 奇数前駆の一意性 + n%6=4
5. `collatzStep_pred_classify` - 前駆の完全分類
6. `collatz_indegree_le_two` - 入次数 <= 2 (主定理)
7. `collatz_indegree_two` - n%6=4 <-> 入次数 = 2
8. `collatz_indegree_one` - n%6!=4 -> 入次数 = 1

## 依存グラフ
  Defs.lean (既存: collatzStep, collatzStep_even, collatzStep_odd)
    |
    +-- [1] collatzStep_double
    +-- [2] collatzStep_odd_predecessor
    +-- [3] collatzStep_even_pred_unique
    +-- [4] collatzStep_odd_pred_unique
    |         |
    |         +-- [5] collatzStep_pred_classify
    |                   |
    |                   +-- [6] collatz_indegree_le_two
    |                   +-- [7] collatz_indegree_two (+ [1],[2])
    |                   +-- [8] collatz_indegree_one
-/

/-! ## 補題1: 偶数前駆の構成 -/

/-- 2n は常に n の前駆ノード (n > 0 のとき) -/
theorem collatzStep_double (n : ℕ) (hn : n > 0) : collatzStep (2 * n) = n := by
  -- 2*n は偶数なので collatzStep(2*n) = (2*n)/2 = n
  have heven : (2 * n) % 2 = 0 := by omega
  rw [collatzStep_even (2 * n) heven]
  omega  -- (2*n)/2 = n

/-! ## 補題2: 奇数前駆の構成 -/

/-- n % 6 = 4 のとき、m = (n-1)/3 は奇数かつ正かつ n の前駆ノード
    数学: n = 6k+4 → m = (6k+3)/3 = 2k+1 (奇数), 3(2k+1)+1 = 6k+4 = n -/
theorem collatzStep_odd_predecessor (n : ℕ) (h : n % 6 = 4) :
    let m := (n - 1) / 3
    m % 2 = 1 ∧ m > 0 ∧ collatzStep m = n := by
  -- 3つの性質を And.intro で構成
  constructor
  · -- (n-1)/3 % 2 = 1: omega で直接解決
    omega
  constructor
  · -- (n-1)/3 > 0: n%6=4 → n≥4 → (n-1)/3 ≥ 1
    omega
  · -- collatzStep((n-1)/3) = n
    -- (n-1)/3 は奇数なので collatzStep は 3m+1 を返す
    have hm_odd : (n - 1) / 3 % 2 ≠ 0 := by omega
    rw [collatzStep_odd ((n - 1) / 3) hm_odd]
    -- 目標: 3 * ((n-1)/3) + 1 = n
    omega

/-! ## 補題3: 偶数前駆の一意性 -/

/-- m が偶数で collatzStep(m) = n なら m = 2n
    証明: collatzStep(m) = m/2 = n → m = 2n -/
theorem collatzStep_even_pred_unique (m n : ℕ) (hm : m > 0)
    (heven : m % 2 = 0) (h : collatzStep m = n) : m = 2 * n := by
  -- collatzStep_even で展開: collatzStep m = m/2
  rw [collatzStep_even m heven] at h
  -- h : m / 2 = n → m = 2 * n
  omega

/-! ## 補題4: 奇数前駆の一意性 + mod 6 制約 -/

/-- m が奇数で collatzStep(m) = n なら m = (n-1)/3 かつ n % 6 = 4
    証明: collatzStep(m) = 3m+1 = n → m = (n-1)/3, m奇数 → n%6=4 -/
theorem collatzStep_odd_pred_unique (m n : ℕ) (hm : m > 0)
    (hodd : m % 2 ≠ 0) (h : collatzStep m = n) :
    m = (n - 1) / 3 ∧ n % 6 = 4 := by
  -- collatzStep_odd で展開: collatzStep m = 3*m+1
  rw [collatzStep_odd m hodd] at h
  -- h : 3 * m + 1 = n
  constructor
  · -- m = (n-1)/3: 3m+1=n → m = (n-1)/3
    omega
  · -- n % 6 = 4: m 奇数 → 3m+1 ≡ 4 (mod 6)
    omega

/-! ## 補題5: 前駆ノードの完全分類 -/

/-- collatzStep(m) = n (m > 0) なら偶数前駆か奇数前駆のどちらか
    証明: m の偶奇で場合分け -/
theorem collatzStep_pred_classify (m n : ℕ) (hm : m > 0)
    (h : collatzStep m = n) :
    m = 2 * n ∨ (m = (n - 1) / 3 ∧ n % 6 = 4) := by
  by_cases hparity : m % 2 = 0
  · -- m 偶数: 偶数前駆の一意性を適用
    left
    exact collatzStep_even_pred_unique m n hm hparity h
  · -- m 奇数 (hparity : m % 2 ≠ 0): 奇数前駆の一意性を適用
    right
    exact collatzStep_odd_pred_unique m n hm hparity h

/-! ## 補題6: 入次数 ≤ 2 (主定理) -/

/-- 任意の n > 0 に対し、collatzStep(m) = n を満たす正の m は最大2つ
    証明: 3つの異なる前駆を仮定 → 分類により各々 2n or (n-1)/3 →
          鳩の巣原理で少なくとも2つが同一 → 矛盾 -/
theorem collatz_indegree_le_two (n : ℕ) (hn : n > 0)
    (m₁ m₂ m₃ : ℕ) (hm₁ : m₁ > 0) (hm₂ : m₂ > 0) (hm₃ : m₃ > 0)
    (h₁ : collatzStep m₁ = n) (h₂ : collatzStep m₂ = n) (h₃ : collatzStep m₃ = n)
    (hne₁₂ : m₁ ≠ m₂) (hne₁₃ : m₁ ≠ m₃) (hne₂₃ : m₂ ≠ m₃) : False := by
  -- 各前駆を分類: m = 2n (L) or m = (n-1)/3 (R)
  have c₁ := collatzStep_pred_classify m₁ n hm₁ h₁
  have c₂ := collatzStep_pred_classify m₂ n hm₂ h₂
  have c₃ := collatzStep_pred_classify m₃ n hm₃ h₃
  -- 3つを2つの値に分類 → 鳩の巣原理で重複 → 矛盾
  -- rcases で 2^3 = 8 ケースに展開、各ケースで omega
  rcases c₁ with h₁l | ⟨h₁r, _⟩ <;> rcases c₂ with h₂l | ⟨h₂r, _⟩ <;> rcases c₃ with h₃l | ⟨h₃r, _⟩
  · exact hne₁₂ (by omega)  -- L L L
  · exact hne₁₂ (by omega)  -- L L R
  · exact hne₁₃ (by omega)  -- L R L
  · exact hne₂₃ (by omega)  -- L R R
  · exact hne₂₃ (by omega)  -- R L L
  · exact hne₁₃ (by omega)  -- R L R
  · exact hne₁₂ (by omega)  -- R R L
  · exact hne₁₂ (by omega)  -- R R R

/-! ## 補題7: n % 6 = 4 ↔ 入次数 = 2 -/

/-- n % 6 = 4 のとき2つの異なる前駆が存在する
    構成: m₁ = 2n (偶数), m₂ = (n-1)/3 (奇数) -/
theorem collatz_indegree_two (n : ℕ) (h : n % 6 = 4) :
    ∃ m₁ m₂ : ℕ, m₁ > 0 ∧ m₂ > 0 ∧ m₁ ≠ m₂ ∧
    collatzStep m₁ = n ∧ collatzStep m₂ = n := by
  refine ⟨2 * n, (n - 1) / 3, ?_, ?_, ?_, ?_, ?_⟩
  · omega                                     -- 2n > 0
  · omega                                     -- (n-1)/3 > 0
  · omega                                     -- 2n ≠ (n-1)/3 (偶数 ≠ 奇数)
  · exact collatzStep_double n (by omega)     -- collatzStep(2n) = n
  · exact (collatzStep_odd_predecessor n h).2.2  -- collatzStep((n-1)/3) = n

/-! ## 補題8: n % 6 ≠ 4 → 入次数 = 1 -/

/-- n % 6 ≠ 4 のとき前駆は一意 (2n のみ)
    証明: 2つの前駆を仮定 → 分類 → 奇数前駆は n%6=4 を要求 → 矛盾 -/
theorem collatz_indegree_one (n : ℕ) (hn : n > 0) (h : n % 6 ≠ 4)
    (m₁ m₂ : ℕ) (hm₁ : m₁ > 0) (hm₂ : m₂ > 0)
    (h₁ : collatzStep m₁ = n) (h₂ : collatzStep m₂ = n) : m₁ = m₂ := by
  have c₁ := collatzStep_pred_classify m₁ n hm₁ h₁
  have c₂ := collatzStep_pred_classify m₂ n hm₂ h₂
  -- 両方 Left(=2n) → m₁ = m₂
  -- Right は n%6=4 を含むので h と矛盾
  rcases c₁ with h₁l | ⟨_, h₁mod⟩
  · rcases c₂ with h₂l | ⟨_, h₂mod⟩
    · omega                   -- m₁ = 2n = m₂
    · exact absurd h₂mod h   -- n%6=4 vs n%6≠4
  · exact absurd h₁mod h     -- n%6=4 vs n%6≠4
"""

print(LEAN_SKETCH)
print("\n" + "="*70)
print("設計の要約")
print("="*70)
print("""
ファイル: Unsolved/Collatz/Indegree.lean
依存: Unsolved.Collatz.Defs のみ
補題数: 8
証明タクティク: omega, simp, rw, by_cases, rcases, exact, absurd, refine
推定難易度: 全補題 omega 中心で低〜中

重要な設計判断:
1. collatzStep_double は Defs.lean に存在しない新規補題
   → collatzStep_even + omega で証明
2. collatzStep_odd_predecessor は let binding を使用
   → Lean 4 の let m := ... in And3 形式
3. 補題6は8ケース展開だが全て omega で閉じる
4. 補題7の refine パターンで存在証明を構成
5. 補題8で absurd パターンを使用
""")
