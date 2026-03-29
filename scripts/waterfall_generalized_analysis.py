"""
一般化Waterfall公式の帰納法実装の分析

目標: T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1 (s <= j-1, j-s >= 1)

既存補題:
- waterfall_step: a%2=1, a>=1, j>=2 => syracuse(a*2^j - 1) = 3*a*2^{j-1} - 1
- waterfall_formula: m>=1, k<m => syracuseIter k (2^m-1) = 3^k * 2^{m-k} - 1
"""

def syracuse(n):
    """Syracuse function for verification"""
    m = 3 * n + 1
    v = 0
    while m % 2 == 0:
        m //= 2
        v += 1
    return m

def syracuse_iter(k, n):
    """Syracuse iterated k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

print("=" * 70)
print("一般化Waterfall公式の数値検証")
print("T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1")
print("条件: k>=0, j>=2, 0<=s<=j-1 (j-s >= 1)")
print("=" * 70)

# 各種 k, j, s で検証
all_pass = True
tests = 0
for k in range(5):
    for j in range(2, 8):
        for s in range(j):  # s=0,...,j-1
            n = 3**k * 2**j - 1
            lhs = syracuse_iter(s, n)
            rhs = 3**(k+s) * 2**(j-s) - 1
            if lhs != rhs:
                print(f"FAIL: k={k}, j={j}, s={s}: T^{s}({n}) = {lhs} != {rhs}")
                all_pass = False
            tests += 1

print(f"\n全テスト数: {tests}")
print(f"結果: {'全て合格' if all_pass else '失敗あり'}")

print("\n" + "=" * 70)
print("帰納法の構造分析")
print("=" * 70)

print("""
--- s に関する帰納法 ---

目標: forall s, s < j, syracuseIter s (3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1

ベースケース (s=0):
  syracuseIter 0 (3^k * 2^j - 1) = 3^k * 2^j - 1 = 3^{k+0} * 2^{j-0} - 1
  定義的に成立 (syracuseIter_zero)

帰納ステップ (s -> s+1):
  仮定: syracuseIter s (3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1
  目標: syracuseIter (s+1) (3^k * 2^j - 1) = 3^{k+s+1} * 2^{j-s-1} - 1

  前提: s+1 < j, つまり j-s >= 2

  展開:
    syracuseIter (s+1) (3^k * 2^j - 1)
    = syracuse (syracuseIter s (3^k * 2^j - 1))   -- syracuseIter_succ_right
    = syracuse (3^{k+s} * 2^{j-s} - 1)            -- 帰納仮定
    = 3 * 3^{k+s} * 2^{j-s-1} - 1                 -- waterfall_step
    = 3^{k+s+1} * 2^{j-(s+1)} - 1                 -- 算術

  waterfall_step の適用条件:
    a = 3^{k+s}, j' = j-s
    - a % 2 = 1: 3^{k+s} は奇数 (Odd.pow)
    - a >= 1: 3^{k+s} >= 1 (正値性)
    - j' >= 2: j-s >= 2 (前提 s+1 < j)
""")

print("=" * 70)
print("Lean証明で必要な補助補題の分析")
print("=" * 70)

print("""
必要な補題:
1. syracuseIter_succ_right: syracuseIter (k+1) n = syracuse (syracuseIter k n)
   -> 既存: full_cycle_bound.syracuseIter_succ_right にある

2. waterfall_step: a%2=1, a>=1, j>=2 => syracuse(a*2^j-1) = 3*a*2^{j-1}-1
   -> 既存: waterfall_step

3. 3^n は奇数: Odd (3^n)
   -> 既存: Odd.pow (Mathlib)

4. 3^n >= 1:
   -> Nat.one_le_pow / positivity

5. 算術等式: 3 * 3^{k+s} * 2^{j-s-1} = 3^{k+s+1} * 2^{j-(s+1)}
   -> ring / norm_num / pow_succ

6. j - s - 1 = j - (s+1) の自然数算術
   -> omega

Lean実装上の課題:
- 自然数の引き算 (j-s) が Lean では下から切り詰められる
  -> s < j の前提で正しく動作する
- syracuseIter_succ_right は private で定義されている可能性
  -> where節にあるので、名前空間を確認する必要がある
""")

print("=" * 70)
print("waterfall_step の適用パターン詳細検証")
print("=" * 70)

for k in range(4):
    for j in range(2, 6):
        for s in range(j):
            a = 3**(k+s)
            jp = j - s  # j'
            n_val = a * 2**jp - 1
            syr_n = syracuse(n_val)
            expected = 3*a * 2**(jp-1) - 1
            ok = syr_n == expected
            if not ok or (k <= 1 and j <= 4):
                print(f"k={k}, j={j}, s={s}: a=3^{k+s}={a}, j'=j-s={jp}, "
                      f"T({n_val}) = {syr_n}, 3a*2^(j'-1)-1 = {expected}, "
                      f"{'OK' if ok else 'FAIL'}")

print("\n" + "=" * 70)
print("特殊ケース: waterfall_formula との整合性")
print("=" * 70)

print("\nwaterfall_formula は k=0 の特殊ケース:")
print("T^s(2^j - 1) = 3^s * 2^{j-s} - 1  (s < j)")
for j in range(2, 8):
    for s in range(j):
        n = 2**j - 1
        lhs = syracuse_iter(s, n)
        rhs = 3**s * 2**(j-s) - 1
        ok = lhs == rhs
        if not ok:
            print(f"  FAIL: j={j}, s={s}")
print("  全て一致 (waterfall_formula の特殊ケースとして)")

print("\n" + "=" * 70)
print("Lean証明の具体的な構造（擬似コード）")
print("=" * 70)

print("""
/-- 一般化Waterfall公式:
    T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1
    条件: j >= 2, s < j -/
theorem generalized_waterfall_formula (k j s : Nat)
    (hj : j >= 2) (hs : s < j) :
    syracuseIter s (3^k * 2^j - 1) = 3^(k+s) * 2^(j-s) - 1 := by
  induction s with
  | zero =>
    simp [syracuseIter_zero]
    -- 目標: 3^k * 2^j - 1 = 3^(k+0) * 2^(j-0) - 1
    -- ring / simp で解決
  | succ s ih =>
    -- 前提: s+1 < j, つまり s < j-1, つまり j-s >= 2
    have hs' : s < j := by omega
    -- 帰納仮定を適用
    have ih_applied := ih (by omega : s < j)
    -- syracuseIter_succ_right で展開
    rw [show syracuseIter (s+1) _ = syracuse (syracuseIter s _) from ...]
    -- 帰納仮定で書き換え
    rw [ih_applied]
    -- waterfall_step を適用
    -- a = 3^(k+s), j' = j-s >= 2
    have ha_odd : (3^(k+s)) % 2 = 1 := ...  -- Odd.pow
    have ha_pos : 3^(k+s) >= 1 := ...        -- positivity
    have hjs : j - s >= 2 := by omega
    rw [waterfall_step (3^(k+s)) (j-s) ha_odd ha_pos hjs]
    -- 目標: 3 * 3^(k+s) * 2^(j-s-1) - 1 = 3^(k+s+1) * 2^(j-(s+1)) - 1
    -- 算術変換
    congr 1
    -- 3 * 3^(k+s) = 3^(k+s+1)
    -- j-s-1 = j-(s+1)
    ring_nf / omega / ...
""")

print("=" * 70)
print("syracuseIter_succ_right のアクセス可能性の確認")
print("=" * 70)

print("""
full_cycle_bound.syracuseIter_succ_right は where 節で定義されている。
Lean 4 では where 節の定理はドット記法でアクセス可能:
  full_cycle_bound.syracuseIter_succ_right

ただし、直接帰納法で証明する方が良いかもしれない:

theorem syracuseIter_succ_right' (k n : Nat) :
    syracuseIter (k+1) n = syracuse (syracuseIter k n) := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih =>
    simp only [syracuseIter_succ]
    exact ih (syracuse n)
""")

print("\n" + "=" * 70)
print("自然数引き算の問題パターン")
print("=" * 70)

print("""
Lean での j - s の扱い:
- s < j のとき j - s > 0 (正常)
- Nat.sub_add_cancel : s <= j -> (j - s) + s = j

特に注意が必要な等式:
1. j - (s + 1) = j - s - 1  (s + 1 <= j のとき)
   -> Nat.sub_succ
2. 3 * 3^(k+s) = 3^(k+s+1)
   -> pow_succ の逆方向 or ring
3. 2^(j-s-1) = 2^(j-(s+1))
   -> congr, j-s-1 = j-(s+1) は omega

帰納ステップの核心的な算術:
  3 * 3^(k+s) * 2^(j-s-1) = 3^(k+(s+1)) * 2^(j-(s+1))

左辺: 3^1 * 3^(k+s) * 2^(j-s-1) = 3^(k+s+1) * 2^(j-s-1)
右辺: 3^(k+s+1) * 2^(j-s-1)  (since j-(s+1) = j-s-1)

よって congr 1 で:
  3 * 3^(k+s) * 2^(j-s-1) - 1 = 3^(k+s+1) * 2^(j-(s+1)) - 1

  LeftHS inside: 3 * 3^(k+s) * 2^(j-s-1)
  RightHS inside: 3^(k+s+1) * 2^(j-(s+1))

  k + (s+1) = k + s + 1 は simp/ring
  j - (s+1) = j - s - 1 は omega (s+1 <= j のとき、つまり s < j)
""")
