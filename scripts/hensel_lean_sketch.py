"""
Lean 4 形式化スケッチの最終設計。

核心的な発見をまとめる。
"""

print("=" * 70)
print("一般化Hensel帰納法: Lean 4 形式化スケッチ")
print("=" * 70)
print()
print("=== 定義 ===")
print("""
def ascendingMap (n : Nat) : Nat := (3 * n + 1) / 2

def ascendingMapIter : Nat -> Nat -> Nat
  | 0, n => n
  | k + 1, n => ascendingMapIter k (ascendingMap n)
""")

print("=== 補題 1: syracuse と ascendingMap の関係 ===")
print("""
theorem syracuse_eq_ascendingMap (n : Nat) (h : n % 4 = 3) :
    syracuse n = ascendingMap n
-- 証明: syracuse_mod4_eq3 から直接
""")

print("=== 補題 2: chain formula (除算・引き算なし) ===")
print("""
-- 前提: 全ての中間値が奇数 (stronger version は条件付き)
-- ascendingMap を数学的に適用した場合の公式
-- 帰納法で証明

-- まず奇数性の保存
theorem ascendingMap_odd (n : Nat) (h : n % 4 = 3) :
    ascendingMap n % 2 = 1
-- 3n+1 ≡ 2 (mod 4) => (3n+1)/2 は奇数

-- chain formula の核心
-- 強い帰納法仮説を使って証明:
-- "n % 2^{k+1} = 2^{k+1}-1 のとき、
--   forall i <= k, ascendingMapIter i n % 4 = 3
--   かつ (ascendingMapIter i n + 1) * 2^i = 3^i * (n + 1)"

-- ただし i = k のときは mod 4 = 3 は
-- n % 2^{k+2} = 2^{k+2}-1 のときのみ

-- 正確な形:
theorem chain_formula (n k : Nat) (h : n % 2^(k+1) = 2^(k+1) - 1) :
    (ascendingMapIter k n + 1) * 2^k = 3^k * (n + 1)
-- 証明: k に関する帰納法
-- Base: (n + 1) * 1 = 1 * (n + 1) trivial
-- Step: 帰納仮説 + ascendingMap の定義
--   (asc(a_k) + 1) * 2 = 3 * (a_k + 1)  -- a_k が奇数のとき
--   これと帰納仮説 (a_k + 1) * 2^k = 3^k * (n+1) を組み合わせて
--   (a_{k+1} + 1) * 2^{k+1} = 3^{k+1} * (n+1)
--
-- 鍵: a_k が奇数であることの証明
-- n % 2^{k+1} = 2^{k+1}-1 => n+1 = 2^{k+1}*m => for all i < k+1:
-- (a_i + 1) * 2^i = 3^i * (n+1) = 3^i * 2^{k+1} * m
-- a_i + 1 = 3^i * 2^{k+1-i} * m
-- k+1-i >= 1 (since i < k+1) なので a_i + 1 は偶数 => a_i は奇数
-- さらに k+1-i >= 2 (since i < k) なら a_i + 1 ≡ 0 (mod 4) => a_i ≡ 3 (mod 4)
""")

print("=== 補題 3: syracuseIter = ascendingMapIter ===")
print("""
theorem syracuseIter_eq_ascendingMapIter (n k : Nat)
    (h : n % 2^(k+1) = 2^(k+1) - 1) :
    forall i, i < k -> syracuseIter i n = ascendingMapIter i n
-- 証明: i に関する帰納法
-- 各ステップで ascendingMapIter i n % 4 = 3 を使って
-- syracuse = ascendingMap を適用
""")

print("=== 補題 4: mod 4 条件 ===")
print("""
theorem ascendingMapIter_mod4_of_all_ones (n k : Nat)
    (h : n % 2^(k+1) = 2^(k+1) - 1) :
    ascendingMapIter k n % 4 = if n % 2^(k+2) = 2^(k+2) - 1 then 3 else 1
-- 証明: chain formula から
-- a_k + 1 = 3^k * (n+1) / 2^k
-- n+1 = 2^{k+1} * m
-- a_k + 1 = 3^k * 2 * m
-- a_k = 2 * 3^k * m - 1
-- a_k % 4 = (2m - 1) % 4 (since 3^k is odd)
-- m even: a_k % 4 = 3
-- m odd: a_k % 4 = 1
-- m even <=> 2^{k+2} | (n+1) <=> n % 2^{k+2} = 2^{k+2}-1
""")

print("=== 主定理 ===")
print("""
theorem hensel_attrition_general (n k : Nat)
    (hn : n >= 1) (hodd : n % 2 = 1) :
    consecutiveAscents n k <-> n % 2^(k+1) = 2^(k+1) - 1

-- 証明: k に関する強帰納法

-- Base case (k = 0):
-- consecutiveAscents n 0 は空真 (forall i < 0, ...)
-- n % 2 = 1 は hodd から直接
-- よって both directions trivial

-- Inductive step (k -> k+1):
-- IH: forall j <= k, consecutiveAscents n j <-> n % 2^(j+1) = 2^(j+1) - 1

-- (=>): consecutiveAscents n (k+1)
-- => consecutiveAscents n k  (by monotonicity)
-- => n % 2^(k+1) = 2^(k+1) - 1  (by IH)
-- + syracuse(syracuseIter k n) > syracuseIter k n  (from def of k+1 ascents)
-- syracuseIter k n = ascendingMapIter k n  (by Lemma 3)
-- syracuse(ascendingMapIter k n) > ascendingMapIter k n
-- => ascendingMapIter k n % 4 = 3  (by syracuse_ascent_iff_mod4_eq3)
-- => n % 2^(k+2) = 2^(k+2) - 1  (by Lemma 4)

-- (<=): n % 2^(k+2) = 2^(k+2) - 1
-- => n % 2^(k+1) = 2^(k+1) - 1  (by mod divisibility)
-- => consecutiveAscents n k  (by IH)
-- + n % 2^(k+2) = 2^(k+2) - 1
-- => ascendingMapIter k n % 4 = 3  (by Lemma 4)
-- syracuseIter k n = ascendingMapIter k n  (by Lemma 3)
-- => syracuseIter k n % 4 = 3
-- => syracuse(syracuseIter k n) > syracuseIter k n  (by syracuse_gt_of_mod4_eq3)
-- + consecutiveAscents n k
-- => consecutiveAscents n (k+1)
""")

print("=== 実装上の技術的課題と解決策 ===")
print("""
課題1: 2^k が一般kの場合 omega タクティックが使えない
解決: ring, norm_num, Nat.pow_le_pow_right 等を活用

課題2: mod の除算整合性 (2^{k+2} | (n+1) => 2^{k+1} | (n+1))
解決: Nat.dvd_of_dvd_of_dvd, dvd_trans

課題3: chain formula での自然数除算
解決: 乗法的等式 (a+1)*2^k = 3^k*(n+1) を使い除算を完全に回避

課題4: ascendingMapIter の奇数性の帰納的証明
解決: chain formula から a_i + 1 = 3^i * 2^{k+1-i} * m を導出
      k+1-i >= 1 なので a_i + 1 は偶数 => a_i は奇数

課題5: 強帰納法の帰納仮説の型
解決: Nat.strongRecOn を使用

課題6: k=0 と k>=1 の場合分け
解決: k=0 は trivial, k>=1 で帰納法
""")

print("=== 新規補題の依存関係グラフ ===")
print("""
ascendingMap_def
    |
ascendingMap_odd  <-- v2_three_mul_add_one_of_mod4_eq3
    |
chain_formula  (帰納法: k)
    |
    +-- ascendingMapIter_odd_of_mod  (chain_formula から導出)
    |
    +-- ascendingMapIter_mod4  (chain_formula から導出)
    |
syracuseIter_eq_ascendingMapIter  (帰納法: i)
    |     uses: syracuse_eq_ascendingMap + ascendingMapIter_mod4
    |
    +-- hensel_attrition_general  (帰納法: k)
              uses: all above + syracuse_ascent_iff_mod4_eq3
                                + consecutiveAscents_mono
""")
