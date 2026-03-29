"""
入次数証明の詳細分析

特にLean 4でのomegaの能力限界と、
collatzStep の unfold/simp パターンの必要性を検証する。
"""

# 核心的な算術の確認

# collatzStep(m) = n のとき:
#   m偶数: m/2 = n → m = 2n
#   m奇数: 3m+1 = n → m = (n-1)/3, n = 3m+1, n%3 = 1, n%6 = 4 (m奇数のため)

# Lean omega での自然数除算の扱い
# omega は Nat の /, % を理解する
# 具体的に確認すべき:
#   (a) m % 2 = 0 ∧ m / 2 = n → m = 2 * n
#   (b) m % 2 = 1 ∧ 3 * m + 1 = n → m = (n - 1) / 3
#   (c) m % 2 = 1 → (3 * m + 1) % 6 = 4

print("核心算術の検証:")
print()

# (a) の検証
print("(a) m偶数, m/2=n → m=2n")
for m in range(0, 100, 2):
    n = m // 2
    assert m == 2 * n
print("   omega で解決可能（自明）")

# (b) の検証
print("(b) m奇数, 3m+1=n → m=(n-1)/3")
for m in range(1, 100, 2):
    n = 3 * m + 1
    assert m == (n - 1) // 3
print("   omega で解決可能")

# (c) の検証
print("(c) m奇数 → (3m+1)%6=4")
for m in range(1, 100, 2):
    assert (3 * m + 1) % 6 == 4
print("   omega で解決可能")

# collatzStep の展開が必要な箇所
print()
print("=" * 70)
print("collatzStep の展開パターン")
print("=" * 70)
print("""
collatzStep の定義:
  def collatzStep (n : ℕ) : ℕ :=
    if n % 2 = 0 then n / 2 else 3 * n + 1

展開には simp [collatzStep] が基本。
ただし、条件 n % 2 = 0 or n % 2 ≠ 0 が必要。

パターン1: collatzStep m = n ∧ m偶数 から m/2 = n を導く
  simp [collatzStep, h_even] で collatzStep m = m/2
  then m/2 = n from hypothesis

パターン2: collatzStep m = n ∧ m奇数 から 3m+1 = n を導く
  simp [collatzStep, h_odd] で collatzStep m = 3*m+1
  then 3*m+1 = n from hypothesis
""")

# 補題の依存関係
print("=" * 70)
print("補題の依存関係")
print("=" * 70)
print("""
collatzStep [Defs.lean 既存]
  ├── collatzStep_even [Defs.lean 既存]
  ├── collatzStep_odd [Defs.lean 既存]
  └── collatzStep_double [Structure.lean 既存]

新規補題:
  ├── collatzStep_odd_predecessor     [新規: n%6=4 → collatzStep((n-1)/3) = n]
  │     依存: collatzStep_odd (既存)
  │     証明: simp [collatzStep] + omega
  │
  ├── collatzStep_even_pred_unique    [新規: m偶数, collatzStep(m)=n → m=2n]
  │     依存: collatzStep_even (既存)
  │     証明: simp [collatzStep, h] + omega
  │
  ├── collatzStep_odd_pred_unique     [新規: m奇数, collatzStep(m)=n → m=(n-1)/3]
  │     依存: collatzStep_odd (既存)
  │     証明: simp [collatzStep, h] + omega
  │
  ├── collatzStep_pred_complete       [新規: 完全分類]
  │     依存: even_pred_unique, odd_pred_unique
  │     証明: m の偶奇で場合分け
  │
  └── collatz_indegree_le_two         [新規: 主定理]
        依存: even_pred_unique, odd_pred_unique
        証明: 鳩の巣原理（3→2パリティ→重複）
""")

# 自然数 vs 整数の注意
print("=" * 70)
print("自然数 (ℕ) での注意点")
print("=" * 70)
print("""
自然数では引き算が切り捨てになる:
  (n - 1) / 3 は n = 0 のとき 0

Lean で m = (n - 1) / 3 かつ 3 * m + 1 = n を扱うとき:
  n ≥ 1 の前提が必要。
  n % 6 = 4 ≥ 4 > 0 なので n ≥ 1 は自動的。

omega が扱える事実:
  n % 6 = 4 → n ≥ 4                     ... ✓ (n ≥ 0 かつ n % 6 = 4 → n ≥ 4)
  n % 6 = 4 → (n - 1) % 3 = 0          ... ✓
  n % 6 = 4 → (n - 1) / 3 % 2 = 1      ... ✓
  n % 6 = 4 → 3 * ((n - 1) / 3) + 1 = n ... ✓
  m % 2 = 1 → (3 * m + 1) % 6 = 4      ... ✓
""")

# Lean 4 の omega で実際に通るかの確認項目
print("=" * 70)
print("Lean 4 テスト項目")
print("=" * 70)
print("""
以下の各 example が omega で通ることを期待:

example (n : ℕ) (h : n % 6 = 4) : n ≥ 4 := by omega
example (n : ℕ) (h : n % 6 = 4) : (n - 1) % 3 = 0 := by omega
example (n : ℕ) (h : n % 6 = 4) : (n - 1) / 3 % 2 = 1 := by omega
example (n : ℕ) (h : n % 6 = 4) : 3 * ((n - 1) / 3) + 1 = n := by omega
example (m : ℕ) (h : m % 2 = 1) : (3 * m + 1) % 6 = 4 := by omega
example (m n : ℕ) (heven : m % 2 = 0) (h : m / 2 = n) : m = 2 * n := by omega
example (m n : ℕ) (hodd : m % 2 = 1) (h : 3 * m + 1 = n) : m = (n - 1) / 3 := by omega
""")

# 形式化の推奨ファイル構造
print("=" * 70)
print("推奨ファイル構造")
print("=" * 70)
print("""
Unsolved/Collatz/Indegree.lean (新規ファイル)
  import Unsolved.Collatz.Defs

  内容:
  1. 偶数前駆の一意性
  2. 奇数前駆の一意性
  3. 奇数前駆の存在条件 (n%6=4)
  4. 前駆ノードの完全分類
  5. 入次数 ≤ 2
  6. 入次数 = 2 ⟺ n ≡ 4 (mod 6)

  依存関係: Defs.lean のみで十分（collatzStep, collatzStep_even, collatzStep_odd）
""")
