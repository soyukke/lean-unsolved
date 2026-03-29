#!/usr/bin/env python3
"""
collatzResidue 最終Lean実装設計書

閉じた形の証明で omega が Nat 除算を扱えない場合の
代替戦略を含む完全な設計。
"""

print("""
=========================================================
collatzResidue Lean 4 実装 最終設計書
=========================================================

1. 定義
-------
def collatzResidue : N -> N
  | 0 => 0
  | n + 1 => if n % 2 = 0 then 4 * collatzResidue n + 1
             else collatzResidue n

2. 展開補題 (4個)
-----------------
(a) collatzResidue_zero : collatzResidue 0 = 0
    証明: rfl

(b) collatzResidue_even_step (n : N) (h : n % 2 = 0) :
      collatzResidue (n + 1) = 4 * collatzResidue n + 1
    証明: simp [collatzResidue, h]
    代替: unfold collatzResidue; simp [h]

(c) collatzResidue_odd_step (n : N) (h : n % 2 != 0) :
      collatzResidue (n + 1) = collatzResidue n
    証明: simp [collatzResidue, h]
    代替: unfold collatzResidue; simp [h]

(d) collatzResidue_two_mul_succ (m : N) :
      collatzResidue (2 * m + 1) = 4 * collatzResidue (2 * m) + 1
    証明: exact collatzResidue_even_step (2 * m) (by omega)

(e) collatzResidue_two_mul_succ_succ (m : N) :
      collatzResidue (2 * m + 2) = collatzResidue (2 * m + 1)
    証明: exact collatzResidue_odd_step (2 * m + 1) (by omega)

(f) collatzResidue_double_step (m : N) :
      collatzResidue (2 * (m + 1)) = 4 * collatzResidue (2 * m) + 1
    証明: have h1 : 2 * (m + 1) = 2 * m + 2 := by ring
          rw [h1, two_mul_succ_succ, two_mul_succ]

3. 核心等式 (2個) -- 最重要
--------------------------
(A) collatzResidue_even_core (m : N) :
      3 * collatzResidue (2 * m) + 1 = 4 ^ m
    証明: m に関する帰納法
    base (m=0): simp [collatzResidue]  -- 3*0+1 = 1 = 4^0
    step (m -> m+1):
      rw [collatzResidue_double_step]
      -- 目標: 3 * (4 * c(2m) + 1) + 1 = 4^(m+1)
      have key : 3 * (4 * c(2m) + 1) + 1 = 4 * (3 * c(2m) + 1) := by ring
      rw [key, ih]
      ring

(B) collatzResidue_odd_core (m : N) :
      3 * collatzResidue (2 * m + 1) + 1 = 4 ^ (m + 1)
    証明:
      rw [collatzResidue_two_mul_succ]
      -- 目標: 3 * (4 * c(2m) + 1) + 1 = 4^(m+1)
      have key : 3 * (4 * c(2m) + 1) + 1 = 4 * (3 * c(2m) + 1) := by ring
      rw [key, collatzResidue_even_core]
      ring

4. 閉じた形 (2個) -- omega が失敗する可能性あり
----------------------------------------------
(A) collatzResidue_even_closed (m : N) :
      collatzResidue (2 * m) = (4 ^ m - 1) / 3
    証明戦略A (omega が解ける場合):
      have h := collatzResidue_even_core m
      have h4 : 4 ^ m >= 1 := Nat.one_le_pow m 4 (by omega)
      omega

    証明戦略B (omega が失敗する場合):
      have h := collatzResidue_even_core m
      have h4 : 4 ^ m >= 1 := Nat.one_le_pow m 4 (by omega)
      -- 4^m - 1 = 3 * c(2m) を示す
      have h3 : 4 ^ m - 1 = 3 * collatzResidue (2 * m) := by omega
      -- (3 * x) / 3 = x
      rw [h3, Nat.mul_div_cancel_left _ (by omega : (3 : N) > 0)]

    証明戦略C (最も安全):
      have h := collatzResidue_even_core m
      have h4 : 4 ^ m >= 1 := Nat.one_le_pow m 4 (by omega)
      have hmul : 4 ^ m - 1 = 3 * collatzResidue (2 * m) := by omega
      have : (4 ^ m - 1) / 3 = collatzResidue (2 * m) := by
        rw [hmul]
        exact Nat.mul_div_cancel_left _ (by omega)
      omega  -- もしくは linarith もしくは exact this.symm

(B) collatzResidue_odd_closed (m : N) :
      collatzResidue (2 * m + 1) = (4 ^ (m + 1) - 1) / 3
    証明: 上と同様

5. simp の潜在的問題と対策
--------------------------
問題: simp [collatzResidue, h] が if-then-else を正しく簡約しない可能性

対策1: unfold collatzResidue; split を使う
  theorem collatzResidue_even_step (n : N) (h : n % 2 = 0) :
      collatzResidue (n + 1) = 4 * collatzResidue n + 1 := by
    unfold collatzResidue
    split
    · -- n % 2 = 0 の場合
      rfl
    · -- n % 2 != 0 の場合、仮定 h と矛盾
      omega

対策2: if_pos / if_neg を使う
  theorem collatzResidue_even_step (n : N) (h : n % 2 = 0) :
      collatzResidue (n + 1) = 4 * collatzResidue n + 1 := by
    show (if n % 2 = 0 then 4 * collatzResidue n + 1 else collatzResidue n)
       = 4 * collatzResidue n + 1
    rw [if_pos h]

対策3: decide_if パターン
  simp only [collatzResidue, h, ↓reduceIte]

6. ring の注意点
-----------------
Nat 上の ring は引き算を含む式では使えない。
しかし今回の証明では全て加法的な形式なので問題なし。
  3 * (4 * x + 1) + 1 = 4 * (3 * x + 1)  -- ring で解ける (加法のみ)
  4 * 4^m = 4^(m+1)                        -- ring で解ける (乗法)

7. 全体の証明依存グラフ
------------------------
  collatzResidue (定義)
  |
  +-- collatzResidue_zero [rfl]
  +-- collatzResidue_even_step [simp/unfold]
  +-- collatzResidue_odd_step [simp/unfold]
       |
       +-- collatzResidue_two_mul_succ [even_step]
       +-- collatzResidue_two_mul_succ_succ [odd_step]
            |
            +-- collatzResidue_double_step [上2つの組み合わせ]
                 |
                 +-- collatzResidue_even_core [帰納法 + ring]
                      |
                      +-- collatzResidue_odd_core [two_mul_succ + even_core]
                      +-- collatzResidue_even_closed [even_core + Nat.div]
                      +-- collatzResidue_odd_closed [odd_core + Nat.div]

8. 推定実装量
--------------
- 定義: 5行
- 展開補題: 約25行
- 核心等式: 約30行
- 閉じた形: 約20行
- 数値検証: 約10行
合計: 約90行

9. 既存コードとの関係
---------------------
ascentConst との対比:
  ascentConst(k+1) = 3 * ascentConst(k) + 2^k  →  閉じた形: 3^k - 2^k
  collatzResidue(2*(m+1)) = 4 * collatzResidue(2*m) + 1  →  閉じた形: (4^m - 1)/3

両者は連続上昇公式の定数項を異なる観点から捉えている:
- ascentConst: 乗法形式 2^k * T^k(n) = 3^k * n + ascentConst(k)
- collatzResidue: 2進展開の残余パターン

10. 今後の発展可能性
---------------------
- collatzResidue を使った連続上昇の mod 2^k 条件の別証明
- Syracuse 関数の 2-adic 解析における residue の役割
- Hensel attrition の定量的評価の改良
""")
