#!/usr/bin/env python3
"""
collatzResidue Lean 4 設計のリスク分析

潜在的な問題点と代替案を列挙する。
"""

print("=" * 70)
print("潜在的リスクと対策")
print("=" * 70)

risks = [
    {
        "issue": "rfl が大きな値で timeout する",
        "likelihood": "低",
        "detail": "collatzResidue は構造的再帰で termination は自明。"
                  "小さな値(0-8)なら展開回数も少なくrflで通るはず。"
                  "native_decide は代替手段だが、rflで十分なはず。",
        "mitigation": "rfl の代わりに decide または native_decide を使う"
    },
    {
        "issue": "collatzResidue_succ_odd の simp が if を正しく簡約しない",
        "likelihood": "中",
        "detail": "unfold collatzResidue 後、if n % 2 = 0 then ... else ... が現れる。"
                  "n % 2 = 1 という仮定から n % 2 = 0 が偽であることを"
                  "simp が推論できるかは環境依存。",
        "mitigation": "simp の代わりに split + omega を使う: "
                      "split; next h => omega; next h => rfl"
    },
    {
        "issue": "collatzResidue_succ_even の simp [h]",
        "likelihood": "低",
        "detail": "h : n % 2 = 0 から if n % 2 = 0 then A else B を A に簡約。"
                  "simp [h] で ite_true に帰着するはず。",
        "mitigation": "if_pos を直接使う: rw [if_pos h]"
    },
    {
        "issue": "nlinarith が even case で失敗する",
        "likelihood": "低〜中",
        "detail": "Goal: 3 * (4 * c + 1) + 1 = 4^m * 4 with ih: 3*c+1 = 4^m."
                  "nlinarith は ih から 4 * (3c+1) = 4 * 4^m を生成し、"
                  "LHS = 12c+4 = 4(3c+1) とマッチさせる。"
                  "4 * 4^m = 4^m * 4 は Nat.mul_comm で解決。"
                  "nlinarith が自動でこれを行えるかは微妙。",
        "mitigation": "明示的に: have : 4 * 4^((n+1)/2) = 4^((n+1)/2) * 4 := by ring; linarith"
    },
    {
        "issue": "pow_succ の展開方向",
        "likelihood": "低",
        "detail": "Mathlib の pow_succ: a ^ (n+1) = a ^ n * a."
                  "rw [h_exp, pow_succ] で 4^((n+1)/2+1) = 4^((n+1)/2) * 4 となる。"
                  "Goal は ...= 4^((n+1)/2) * 4 の形。"
                  "nlinarith で ih: 3c+1 = 4^((n+1)/2) から直接解ける。",
        "mitigation": "特に問題なし。必要なら mul_comm を挟む。"
    },
    {
        "issue": "collatzResidue_closed で omega が / を含む等式を解けない",
        "likelihood": "中",
        "detail": "omega は Nat の / を扱えるが、a / b = c 型の結論を"
                  "直接導出できない場合がある。"
                  "代替: hsub を rw して Nat.mul_div_cancel_left を使う。",
        "mitigation": "最終設計案ではすでに Nat.mul_div_cancel_left を使用。OK。"
    },
    {
        "issue": "four_pow_mod3 で omega が pow_succ 後の式を処理できない",
        "likelihood": "低〜中",
        "detail": "pow_succ で 4^(n+1) = 4^n * 4 に展開後、"
                  "ih: 4^n % 3 = 1 から 4^n*4 % 3 = 1 を導く。"
                  "omega は % と * の組み合わせを扱えるはず。"
                  "ただし非線形なので失敗する可能性あり。",
        "mitigation": "代替: rw [Nat.pow_mod]; norm_num (既存コードで実績あり)"
    },
]

for i, r in enumerate(risks, 1):
    print(f"\nリスク {i}: {r['issue']}")
    print(f"  可能性: {r['likelihood']}")
    print(f"  詳細: {r['detail']}")
    print(f"  対策: {r['mitigation']}")

print()
print("=" * 70)
print("代替タクティク集 (フォールバック)")
print("=" * 70)

fallbacks = """
-- collatzResidue_succ_even の代替
theorem collatzResidue_succ_even' (n : Nat) (h : n % 2 = 0) :
    collatzResidue (n + 1) = 4 * collatzResidue n + 1 := by
  show (if n % 2 = 0 then 4 * collatzResidue n + 1
        else collatzResidue n) = 4 * collatzResidue n + 1
  rw [if_pos h]

-- collatzResidue_succ_odd の代替
theorem collatzResidue_succ_odd' (n : Nat) (h : n % 2 = 1) :
    collatzResidue (n + 1) = collatzResidue n := by
  show (if n % 2 = 0 then 4 * collatzResidue n + 1
        else collatzResidue n) = collatzResidue n
  rw [if_neg (by omega)]

-- collatzResidue_core_eq の even case 代替 (nlinarith 失敗時)
-- rw [h_exp, pow_succ] 後の Goal:
-- 3 * (4 * collatzResidue n + 1) + 1 = 4 ^ ((n + 1) / 2) * 4
-- を明示的に変形:
-- have step1 : 3 * (4 * collatzResidue n + 1) + 1
--            = 4 * (3 * collatzResidue n + 1) := by ring
-- rw [step1, ih]
-- 残り: 4 * 4 ^ ((n + 1) / 2) = 4 ^ ((n + 1) / 2) * 4
-- exact Nat.mul_comm 4 (4 ^ ((n + 1) / 2))

-- four_pow_mod3 の代替
theorem four_pow_mod3' (m : Nat) : 4 ^ m % 3 = 1 := by
  rw [show (4 : Nat) = 3 + 1 from rfl]
  rw [Nat.add_pow_mod_right]  -- これは使えないかも
  -- 代替: induction + norm_num
  induction m with
  | zero => norm_num
  | succ n ih =>
    rw [pow_succ, Nat.mul_mod, ih]
    norm_num
"""
print(fallbacks)

print("=" * 70)
print("最も安全な証明戦略 (保守的)")
print("=" * 70)

safe_code = r"""
-- 最も安全な版: 明示的な変形を使い nlinarith を避ける
theorem collatzResidue_core_eq_safe (k : Nat) :
    3 * collatzResidue k + 1 = 4 ^ ((k + 1) / 2) := by
  induction k with
  | zero => simp [collatzResidue]
  | succ n ih =>
    by_cases hn : n % 2 = 0
    · -- n even
      rw [collatzResidue_succ_even n hn]
      have h_exp : (n + 2) / 2 = (n + 1) / 2 + 1 := by omega
      rw [h_exp, pow_succ]
      -- Goal: 3 * (4 * c + 1) + 1 = 4^m * 4  where ih: 3*c+1 = 4^m
      -- 12c + 4 = 4^m * 4
      -- 4 * (3c + 1) = 4 * 4^m = 4^m * 4
      have step : 3 * (4 * collatzResidue n + 1) + 1
                = 4 * (3 * collatzResidue n + 1) := by ring
      rw [step, ih, mul_comm]
    · -- n odd
      have hn_odd : n % 2 = 1 := by omega
      rw [collatzResidue_succ_odd n hn_odd]
      have h_exp : (n + 2) / 2 = (n + 1) / 2 := by omega
      rw [h_exp]
      exact ih
"""
print(safe_code)

print()
print("=" * 70)
print("推奨: safe版を第一候補とし、nlinarith版をフォールバックに")
print("=" * 70)
print()
print("safe版の利点:")
print("  - ring と mul_comm のみ使用（確実に通る）")
print("  - nlinarith の不確実性を回避")
print("  - 証明構造が明確で読みやすい")
print()
print("3つの定理合計: 約80行の Lean コード")
print("  - collatzResidue: 定義 (5行)")
print("  - rfl 検証: 9行")
print("  - 展開補題: 15行")
print("  - 核心等式: 25行")
print("  - 系(closed form): 15行")
print("  - pair補題: 5行")
