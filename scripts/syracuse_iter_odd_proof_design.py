"""
syracuseIter_odd: syracuseIter k n が常に奇数であることの証明設計

目標:
  theorem syracuseIter_odd (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
      syracuseIter k n % 2 = 1

既存の道具:
  - syracuse_odd : n >= 1, n % 2 = 1 -> syracuse n % 2 = 1
  - syracuse_pos : n >= 1, n % 2 = 1 -> syracuse n >= 1
  - syracuseIter_odd_of_ascents : consecutiveAscents仮定あり(不要にしたい)

証明戦略: kに関する帰納法
  base: k = 0 -> syracuseIter 0 n = n, n % 2 = 1 で即座
  step: k+1 -> syracuseIter (k+1) n = syracuseIter k (syracuse n)
    - syracuse_odd: n >= 1, n奇数 -> syracuse n 奇数
    - syracuse_pos: n >= 1, n奇数 -> syracuse n >= 1
    - 帰納法仮説を syracuse n に適用

ポイント: consecutiveAscents は一切不要。syracuse_odd と syracuse_pos だけで十分。
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function"""
    m = 3 * n + 1
    return m // (2 ** v2(m))

def syracuse_iter(k, n):
    """Syracuse iteration"""
    for _ in range(k):
        n = syracuse(n)
    return n

# 検証: syracuseIter k n が常に奇数かつ正であること
print("=== syracuseIter k n の奇数性・正値性の検証 ===\n")

test_values = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 99, 101, 999, 1001]

all_odd = True
all_pos = True
for n in test_values:
    for k in range(20):
        val = syracuse_iter(k, n)
        if val % 2 != 1:
            print(f"FAIL: syracuseIter({k}, {n}) = {val} is even!")
            all_odd = False
        if val < 1:
            print(f"FAIL: syracuseIter({k}, {n}) = {val} < 1!")
            all_pos = False

if all_odd:
    print("OK: All tested values are odd")
if all_pos:
    print("OK: All tested values are >= 1")

# 帰納法の構造を具体的に追う
print("\n=== 帰納法のステップ追跡 (n=7) ===\n")
n_start = 7
for k in range(8):
    val = syracuse_iter(k, n_start)
    next_val = syracuse(val)
    print(f"  k={k}: syracuseIter({k}, {n_start}) = {val}, "
          f"odd={val%2==1}, pos={val>=1}, "
          f"syracuse({val}) = {next_val}, "
          f"next_odd={next_val%2==1}, next_pos={next_val>=1}")

# 証明設計の正しさを論理的に確認
print("\n=== 証明設計の論理的構造 ===\n")
print("""
定理: syracuseIter_odd (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
        syracuseIter k n % 2 = 1

証明: k に関する帰納法

[base case] k = 0:
  syracuseIter 0 n = n   (定義)
  n % 2 = 1              (仮定 hodd)
  完了 ✓

[inductive step] k -> k+1:
  目標: syracuseIter (k+1) n % 2 = 1

  展開: syracuseIter (k+1) n = syracuseIter k (syracuse n)  (定義)

  let m := syracuse n とおく

  必要な前提:
  (A) m % 2 = 1   ... syracuse_odd n hn hodd より
  (B) m >= 1       ... syracuse_pos n hn hodd より

  帰納法仮説を m に適用:
  IH(m, k) : m >= 1 -> m % 2 = 1 -> syracuseIter k m % 2 = 1

  (A) と (B) より:
  syracuseIter k (syracuse n) % 2 = 1

  完了 ✓
""")

# 並行して syracuseIter_pos も証明できることを確認
print("=== 同時に証明可能: syracuseIter_pos ===\n")
print("""
定理: syracuseIter_pos (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
        syracuseIter k n >= 1

証明: k に関する帰納法 (syracuseIter_odd と全く同じ構造)

[base] k=0: syracuseIter 0 n = n >= 1  ✓
[step] k+1: syracuseIter (k+1) n = syracuseIter k (syracuse n)
  syracuse n >= 1     by syracuse_pos
  syracuse n % 2 = 1  by syracuse_odd
  IH 適用 ✓
""")

# Lean4コードのスケッチ
print("=== Lean 4 証明スケッチ ===\n")
lean_code = """
/-- syracuseIter k n は常に奇数（n >= 1 かつ n 奇数のとき）。
    consecutiveAscents 仮定は不要。syracuse_odd と syracuse_pos のみで証明。-/
theorem syracuseIter_odd (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuseIter k n % 2 = 1 := by
  induction k generalizing n with
  | zero => simp only [syracuseIter_zero]; exact hodd
  | succ k ih =>
    simp only [syracuseIter_succ]
    exact ih (syracuse n)
      (syracuse_pos n hn hodd)
      (syracuse_odd n hn hodd)

/-- syracuseIter k n は常に正（n >= 1 かつ n 奇数のとき）-/
theorem syracuseIter_pos (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    syracuseIter k n ≥ 1 := by
  induction k generalizing n with
  | zero => simp only [syracuseIter_zero]; exact hn
  | succ k ih =>
    simp only [syracuseIter_succ]
    exact ih (syracuse n)
      (syracuse_pos n hn hodd)
      (syracuse_odd n hn hodd)
"""
print(lean_code)

# 既存の syracuseIter_odd_of_ascents との比較
print("=== 既存定理との比較 ===\n")
print("""
既存 (Formula.lean):
  syracuseIter_odd_of_ascents (n k : N) (hn : n >= 1) (hodd : n % 2 = 1)
      (hasc : consecutiveAscents n k) :
      syracuseIter k n % 2 = 1

新規 (提案):
  syracuseIter_odd (n k : N) (hn : n >= 1) (hodd : n % 2 = 1) :
      syracuseIter k n % 2 = 1

違い:
  - consecutiveAscents 仮定が完全に不要
  - syracuse_odd (Structure.lean) と syracuse_pos (Structure.lean) のみに依存
  - 証明は 7 行程度
  - syracuseIter_odd_of_ascents は syracuseIter_odd の特殊ケース

既存定理の使用箇所への影響:
  syracuseIter_odd_of_ascents を使用している箇所は全て
  syracuseIter_odd で置き換え可能（仮定が弱くなるため）

  ただし、連続上昇版が必要な他の定理（mod4, 上界等）では
  consecutiveAscents 仮定は引き続き必要。
""")

# 依存関係のまとめ
print("=== 依存関係 ===\n")
print("""
syracuseIter_odd
  ├── syracuseIter_zero  (Defs.lean, @[simp])
  ├── syracuseIter_succ  (Defs.lean, @[simp])
  ├── syracuse_odd       (Structure.lean)
  │   └── odd_of_div_two_pow_v2  (Structure.lean)
  │       ├── two_pow_v2_dvd
  │       ├── v2_ge_of_dvd
  │       └── Nat.mul_dvd_of_dvd_div
  └── syracuse_pos       (Structure.lean)
      └── pow_v2_le
          └── pow_v2_dvd

全て既に形式化済み。新たな sorry 不要。
""")

# 配置場所の提案
print("=== 配置場所の提案 ===\n")
print("""
Structure.lean の syracuse_odd の直後（行 578 付近）に配置するのが最適。

理由:
  1. syracuse_odd と syracuse_pos に直接依存
  2. Structure.lean は Defs.lean のみインポート（Formula.lean の Hensel.lean 非依存）
  3. 論理的に syracuse_odd の帰結として自然

代替: Defs.lean に配置も可能だが、syracuse_odd 自体が Structure.lean にある。
""")
