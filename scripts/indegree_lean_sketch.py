"""
Lean 4 形式化スケッチの作成

コラッツグラフの入次数 ≤ 2 の形式証明に必要な定理群を分析する。
"""

lean_sketch = """
/-!
# コラッツグラフの入次数分析

## 主定理
各正整数 n に対して、collatzStep(m) = n を満たす正整数 m は最大2個。
具体的には:
- 偶数前駆: m = 2n (常に存在)
- 奇数前駆: m = (n-1)/3 (n ≡ 4 mod 6 のときのみ存在)

## 既存定理（利用可能）
- collatzStep_even: n % 2 = 0 → collatzStep n = n / 2
- collatzStep_odd: n % 2 ≠ 0 → collatzStep n = 3 * n + 1
- collatzStep_double: n > 0 → collatzStep (2 * n) = n

## 新規に必要な補題

### 補題1: 奇数前駆の存在
collatzStep_odd_predecessor:
  n % 6 = 4 → n ≥ 4 →
  let m := (n - 1) / 3
  m % 2 = 1 ∧ collatzStep m = n

証明戦略:
  n = 6k + 4 とおく。
  m = (6k+4-1)/3 = (6k+3)/3 = 2k+1（奇数）
  collatzStep(2k+1) = 3(2k+1)+1 = 6k+4 = n  ✓

### 補題2: 前駆ノードの完全分類
collatzStep_predecessors_complete:
  m > 0 → collatzStep m = n →
  m = 2 * n ∨ (n % 6 = 4 ∧ m = (n - 1) / 3)

証明戦略:
  m の偶奇で場合分け。
  Case m 偶数: collatzStep m = m/2 = n → m = 2n
  Case m 奇数: collatzStep m = 3m+1 = n → m = (n-1)/3
    n = 3m+1 より n % 3 = 1
    m 奇数より m = 2j+1, n = 6j+4 → n % 6 = 4

### 補題3: 奇数前駆の一意性
collatzStep_odd_pred_unique:
  m > 0 → m % 2 = 1 → collatzStep m = n →
  m = (n - 1) / 3

証明: collatzStep m = 3m+1 = n より m = (n-1)/3。

### 補題4: 偶数前駆の一意性
collatzStep_even_pred_unique:
  m > 0 → m % 2 = 0 → collatzStep m = n →
  m = 2 * n

証明: collatzStep m = m/2 = n より m = 2n。

### 主定理: 入次数 ≤ 2
collatz_indegree_le_two:
  n > 0 →
  ∀ m₁ m₂ m₃ : ℕ,
    m₁ > 0 → m₂ > 0 → m₃ > 0 →
    collatzStep m₁ = n → collatzStep m₂ = n → collatzStep m₃ = n →
    m₁ ≠ m₂ → m₁ ≠ m₃ → m₂ ≠ m₃ →
    False

証明:
  3つの異なる前駆 m₁, m₂, m₃ が存在すると仮定。
  各 mᵢ は偶数か奇数。
  - 偶数前駆は m = 2n で一意（補題4）→ 偶数前駆は最大1つ
  - 奇数前駆は m = (n-1)/3 で一意（補題3）→ 奇数前駆は最大1つ
  したがって前駆は最大2つ → 3つの異なる前駆は矛盾。□

### 精密化: n ≡ 4 (mod 6) ⟺ 入次数 = 2
collatz_indegree_eq_two_iff:
  n > 0 →
  (∃ m₁ m₂ : ℕ, m₁ > 0 ∧ m₂ > 0 ∧ m₁ ≠ m₂ ∧
    collatzStep m₁ = n ∧ collatzStep m₂ = n)
  ↔ n % 6 = 4

### 対偶: n ≢ 4 (mod 6) → 入次数 = 1
collatz_indegree_eq_one:
  n > 0 → n % 6 ≠ 4 →
  ∀ m₁ m₂ : ℕ,
    m₁ > 0 → m₂ > 0 →
    collatzStep m₁ = n → collatzStep m₂ = n →
    m₁ = m₂
"""

print(lean_sketch)

# Lean で omega が解ける算術的事実の確認
print("=" * 70)
print("omega で解けるべき算術的事実:")
print("=" * 70)

# (1) n % 6 = 4 → (n-1) % 3 = 0
for n in range(4, 100, 6):
    assert (n - 1) % 3 == 0, f"Failed at n={n}"
print("(1) n % 6 = 4 → (n-1) % 3 = 0  ... OK")

# (2) n % 6 = 4 → (n-1)/3 % 2 = 1
for n in range(4, 100, 6):
    assert ((n - 1) // 3) % 2 == 1, f"Failed at n={n}"
print("(2) n % 6 = 4 → (n-1)/3 % 2 = 1  ... OK")

# (3) n % 6 = 4 → 3 * ((n-1)/3) + 1 = n
for n in range(4, 1000, 6):
    m = (n - 1) // 3
    assert 3 * m + 1 == n, f"Failed at n={n}"
print("(3) n % 6 = 4 → 3 * ((n-1)/3) + 1 = n  ... OK")

# (4) m 奇数, 3m+1 = n → n % 6 = 4
for m in range(1, 1000, 2):
    n = 3 * m + 1
    assert n % 6 == 4, f"Failed at m={m}, n={n}"
print("(4) m 奇数 → (3m+1) % 6 = 4  ... OK")

# (5) m 偶数, m > 0, m/2 = n → m = 2n
for m in range(2, 1000, 2):
    n = m // 2
    assert m == 2 * n, f"Failed at m={m}"
print("(5) m 偶数, m/2 = n → m = 2n  ... OK (自明)")

# (6) n ≥ 4 かつ n % 6 = 4 → (n-1)/3 > 0
for n in range(4, 1000, 6):
    assert (n - 1) // 3 > 0, f"Failed at n={n}"
print("(6) n ≥ 4 かつ n % 6 = 4 → (n-1)/3 > 0  ... OK")

print()
print("全ての算術的事実は omega タクティクで解決可能と推定。")
print("Lean 4 の omega は線形算術を完全に解くので、")
print("mod, div に関する事実は omega で直接証明可能。")

# 証明難易度の推定
print("\n" + "=" * 70)
print("証明難易度の推定")
print("=" * 70)
print("""
1. collatzStep_odd_predecessor: ★☆☆ (omega で直接可能)
   - n % 6 = 4 のとき m = (n-1)/3 とすれば m 奇数かつ 3m+1=n
   - omega で全て解ける算術

2. collatzStep_predecessors_complete: ★★☆ (場合分け + omega)
   - m の偶奇で場合分け
   - 偶数: m/2 = n → m = 2n (omega)
   - 奇数: 3m+1 = n → m = (n-1)/3, n%6=4 (omega)

3. collatz_indegree_le_two: ★★☆ (鳩の巣原理的)
   - 3つの前駆を仮定 → 偶奇分類 → 少なくとも2つが同じパリティ
   - 同パリティの2つは一意性から等しい → 矛盾

4. collatz_indegree_eq_two_iff: ★★☆ (↔ の両方向)
   - →方向: 異なる2前駆の存在から n%6=4
   - ←方向: n%6=4 から 2n と (n-1)/3 の構成

5. 全体的な難易度: 中程度
   - 主に omega で解ける算術
   - 場合分けの構造が明快
   - Lean 4 の既存ライブラリ（Nat.div_mul_cancel 等）で補完
""")
