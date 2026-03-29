"""
v2_mul の Lean 4 形式化: 詳細設計書

== 主要な難所と解決策 ==

1. 奇数*奇数=奇数: omega は非線形なので使えない
   -> Nat.mul_mod を使う: (a*b)%2 = ((a%2)*(b%2))%2
   -> ha : a%2=1, hb_odd : b%2!=0 (つまり b%2=1)
   -> (a*b)%2 = (1*1)%2 = 1%2 = 1

2. a*b = 2*(a/2*b): omega は a*b を直接扱えない
   -> have : a = 2*(a/2) := by omega
   -> calc a*b = (2*(a/2))*b := by rw [...]
   ->         _ = 2*((a/2)*b) := by ring

3. (a*b)/2 のリライト: v2_even の後に出てくる
   -> 方法A: v2_even を使わず、直接 v2_two_mul を使う
   -> v2(2*k) = 1 + v2(k) は v2_two_mul で直接得られる
   -> a*b = 2*((a/2)*b) と書き換えた後、v2_two_mul 適用

4. 偶数*任意 = 偶数: omega で解ける？
   -> a%2=0 => (a*b)%2=0 は Nat.mul_mod で
   -> ただし v2_two_mul なら偶数性の証明不要

== 最終設計: v2_two_mul を活用した簡潔な証明 ==
"""

# v2_odd_mul の完全なLean証明設計
v2_odd_mul_proof = """
/-- 奇数 a に対して v2(a*b) = v2(b) -/
theorem v2_odd_mul (a b : ℕ) (ha : a % 2 = 1) : v2 (a * b) = v2 b := by
  induction b using Nat.strongRecOn with
  | ind b ih =>
    by_cases hb0 : b = 0
    · -- b = 0: v2(a*0) = v2(0) = 0 = v2(0)
      subst hb0; simp
    · by_cases hb_odd : b % 2 ≠ 0
      · -- b is odd: a*b is odd (odd*odd=odd)
        have hab_odd : (a * b) % 2 ≠ 0 := by
          rw [Nat.mul_mod]; simp [ha]; omega
        rw [v2_odd _ hab_odd, v2_odd _ hb_odd]
      · -- b is even
        push_neg at hb_odd
        have hb_even : b % 2 = 0 := by omega
        -- b = 2 * (b/2)
        have hb_eq : b = 2 * (b / 2) := by omega
        -- a*b = a * (2 * (b/2)) = 2 * (a * (b/2))
        have hab_eq : a * b = 2 * (a * (b / 2)) := by
          calc a * b = a * (2 * (b / 2)) := by rw [hb_eq]
            _ = 2 * (a * (b / 2)) := by ring
        -- a * (b/2) > 0 since a > 0 and b/2 > 0 (b > 0 and b even => b >= 2)
        have hab2_pos : a * (b / 2) ≠ 0 := by
          have : a > 0 := by omega
          have : b / 2 > 0 := by omega
          positivity  -- or: exact Nat.ne_of_gt (Nat.mul_pos (by omega) (by omega))
        -- v2(a*b) = v2(2*(a*(b/2))) = 1 + v2(a*(b/2))
        rw [hab_eq, v2_two_mul _ hab2_pos]
        -- IH: v2(a*(b/2)) = v2(b/2)
        have hb2_lt : b / 2 < b := by omega
        rw [ih (b / 2) hb2_lt]
        -- 1 + v2(b/2) = v2(b)
        rw [← v2_even b hb0 hb_even]
"""

# v2_mul の完全なLean証明設計
v2_mul_proof = """
/-- 正の整数 a, b に対して v2(a*b) = v2(a) + v2(b) -/
theorem v2_mul (a b : ℕ) (ha : a > 0) (hb : b > 0) :
    v2 (a * b) = v2 a + v2 b := by
  induction a using Nat.strongRecOn with
  | ind a ih =>
    by_cases ha_odd : a % 2 ≠ 0
    · -- a is odd: v2(a) = 0, v2(a*b) = v2(b)
      rw [v2_odd a ha_odd, v2_odd_mul a b (by omega), Nat.zero_add]
    · -- a is even: a = 2*(a/2)
      push_neg at ha_odd
      have ha_even : a % 2 = 0 := by omega
      have ha_ne : a ≠ 0 := by omega
      -- a = 2 * (a/2)
      have ha_eq : a = 2 * (a / 2) := by omega
      -- a/2 > 0 and a/2 < a
      have ha2_pos : a / 2 > 0 := by omega
      have ha2_lt : a / 2 < a := by omega
      -- a*b = 2 * ((a/2) * b)
      have hab_eq : a * b = 2 * ((a / 2) * b) := by
        calc a * b = (2 * (a / 2)) * b := by rw [ha_eq]
          _ = 2 * ((a / 2) * b) := by ring
      -- (a/2)*b > 0
      have hab2_ne : (a / 2) * b ≠ 0 := by positivity
      -- v2(a*b) = v2(2*((a/2)*b)) = 1 + v2((a/2)*b)
      rw [hab_eq, v2_two_mul _ hab2_ne]
      -- IH: v2((a/2)*b) = v2(a/2) + v2(b)
      rw [ih (a / 2) ha2_lt ha2_pos hb]
      -- v2(a) = 1 + v2(a/2) (by v2_even)
      rw [v2_even a ha_ne ha_even]
      -- 1 + (v2(a/2) + v2(b)) = (1 + v2(a/2)) + v2(b)
      omega
"""

print("="*60)
print("v2_odd_mul の Lean 4 証明設計")
print("="*60)
print(v2_odd_mul_proof)

print("="*60)
print("v2_mul の Lean 4 証明設計")
print("="*60)
print(v2_mul_proof)

# 技術的難所の詳細分析
print("="*60)
print("技術的難所と解決策")
print("="*60)

difficulties = [
    {
        "issue": "奇数*奇数=奇数の証明",
        "detail": "omega は (a*b)%2 を直接扱えない（非線形）",
        "solution": "Nat.mul_mod を使って (a*b)%2 = ((a%2)*(b%2))%2 に変換後 omega",
        "lean_code": "have hab_odd : (a * b) % 2 ≠ 0 := by rw [Nat.mul_mod]; simp [ha]; omega",
        "risk": "低: Nat.mul_mod は Mathlib の基本補題",
    },
    {
        "issue": "a*b = 2*((a/2)*b) の変換",
        "detail": "omega は a*b と (a/2)*b を直接結べない",
        "solution": "have a = 2*(a/2) を omega で得て、calc で ring で整理",
        "lean_code": """have ha_eq : a = 2 * (a / 2) := by omega
calc a * b = (2 * (a / 2)) * b := by rw [ha_eq]
  _ = 2 * ((a / 2) * b) := by ring""",
        "risk": "低: omega + ring の標準パターン",
    },
    {
        "issue": "positivity での (a/2)*b ≠ 0",
        "detail": "a > 0, a%2=0 => a/2 > 0, b > 0 => (a/2)*b > 0",
        "solution": "positivity タクティクか、Nat.mul_pos + omega",
        "lean_code": "have hab2_ne : (a / 2) * b ≠ 0 := by positivity",
        "risk": "低: positivity は標準タクティク",
    },
    {
        "issue": "v2_even の向きの問題",
        "detail": "v2_even は v2 n = 1 + v2(n/2) の形。最後の式変形で向きを合わせる必要",
        "solution": "← v2_even でゴールの v2(b) を 1 + v2(b/2) に変換",
        "lean_code": "rw [← v2_even b hb0 hb_even]",
        "risk": "低: 標準的なリライト",
    },
    {
        "issue": "Nat.strongRecOn のAPI",
        "detail": "Lean 4 / Mathlib のバージョンにより induction using の構文が異なる可能性",
        "solution": "既存コード (pow_v2_dvd) と同じパターンを使用",
        "lean_code": "induction b using Nat.strongRecOn with | ind b ih => ...",
        "risk": "低: 既存コードで動作実績あり",
    },
    {
        "issue": "simp [ha] の挙動",
        "detail": "ha : a % 2 = 1 を simp に渡したとき、Nat.mul_mod の簡約後に期待通り動くか",
        "solution": "simp でダメなら norm_num や omega で手動簡約",
        "lean_code": """-- 代替案
have : (a * b) % 2 = ((a % 2) * (b % 2)) % 2 := Nat.mul_mod a b 2
rw [ha] at this
-- this : (a * b) % 2 = (1 * (b % 2)) % 2
simp at this
-- this : (a * b) % 2 = b % 2
omega -- or exact""",
        "risk": "中: simp の挙動は予測困難、代替案あり",
    },
]

for i, d in enumerate(difficulties):
    print(f"\n{i+1}. {d['issue']}")
    print(f"   問題: {d['detail']}")
    print(f"   解決: {d['solution']}")
    print(f"   リスク: {d['risk']}")

# ファイル配置の提案
print("\n" + "="*60)
print("ファイル配置の提案")
print("="*60)
print("""
v2_odd_mul と v2_mul は Defs.lean の v2_two_mul の直後に配置するのが自然。
ただし Defs.lean が大きくなりすぎる場合は、新ファイル
  Unsolved/Collatz/V2Mul.lean
を作成し、import Unsolved.Collatz.Defs とする。

既存の依存関係:
  Defs.lean <- Structure.lean <- Mod.lean <- Hensel.lean <- Accel.lean

v2_odd_mul, v2_mul は Defs.lean の補題(v2_odd, v2_even, v2_two_mul)のみに
依存するため、Defs.lean に追加するか、V2Mul.lean を Defs.lean の
直接の依存先として配置するのが最適。
""")

# 影響範囲の分析
print("="*60)
print("v2_mul が有効化する下流の定理候補")
print("="*60)
print("""
1. v2(3*n+1) の分析の強化
   - 現在: mod 8 での場合分けで v2 の値を個別に計算
   - v2_mul があれば: v2(3*n+1) の分析で3の因子と(n+1/3)の因子を分離可能

2. Syracuse 関数の合成の分析
   - syracuse(n) * 2^v2(3n+1) = 3n+1 (既存)
   - v2_mul により syracuse の反復の v2 構造を帰納的に分析可能

3. 2-adic valuation の一般理論
   - v2(n!) = sum_{k>=1} floor(n/2^k) (Legendre)
   - v2(binomial(n,k)) = (carries in binary addition)

4. Hensel attrition の一般化
   - k回連続上昇の v2 分析で、乗法性が直接使える
""")
