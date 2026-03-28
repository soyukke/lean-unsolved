# 探索 090: CollatzFormula.lean 一般公式の下降条件分析

## メタデータ
- **キューID**: collatz-087
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 小発見
- **日付**: 2026-03-27

## アプローチ
既存のCollatzFormula.lean（探索16の成果）を精読し、2^k·T^k(n) = 3^k·n + (3^k - 2^k)の公式から下降条件T^k(n) < nの成立条件を数学的に分析した。CollatzAccel.leanのmod 8/16分類による具体的上界との関連も調査。

## 発見
- 連続上昇条件(v2=1が連続)のもとではT^k(n) < nは成立しない: (3/2)^k > 1なので常に増加。syracuseIter_ge_of_ascentsとして既に形式化済み
- 下降が起こるのは上昇終了後の次のステップ（v2≥2）でのみ。full_cycle_bound定理が既に形式化済み
- k回上昇+1回下降のサイクル比率は3^{k+1}/2^{k+2}で、k=0で3/4<1（収縮）、k≥1で膨張
- メルセンヌ数2^m-1の軌道公式mersenne_orbit_mulとm-1回上昇後のmersenne_descentは完全に形式化済み
- descent_value_formula: 2^k·(3·T^k(n)+1) + 2^{k+1} = 3^{k+1}·(n+1) が下降値の核心等式

## 仮説
- consecutiveAscents n k ならば n ≥ 2^k - 1 という下界定理は形式化可能
- 一般のv2列に対する反復公式はv2値の列(j_1,...,j_k)をパラメータ化した形で形式化可能
- full_cycle_boundの系として T^{k+1}(n) ≤ 3^{k+1}·(n+1)/2^{k+2} の形式化は直接的に可能

## 行き止まり
- T^k(n) < n ⟺ n > (3^k - 2^k)/(2^k - 3^k) の形式化は意味をなさない: k≥1で分母が負になりℕでは表現不可
- k→∞の漸近挙動のLean形式化: Mathlibのtopologyライブラリとのブリッジが重い

## 詳細
CollatzFormula.leanには主要定理が既に完全に形式化されている:
1. ascentConst_add_two_pow: ascentConst k + 2^k = 3^k
2. syracuse_iter_mul_formula: 2^k·T^k(n) = 3^k·n + ascentConst k
3. full_cycle_bound: 4·2^k·T^{k+1}(n) + 2^{k+1} ≤ 3^{k+1}·(n+1)

新規形式化の方向として最も有望なのは:
1. 連続上昇回数の上界: consecutiveAscents n k → n ≥ 2^k - 1
2. full_cycle_boundの除算形式
3. 一般化反復公式（v2列パラメータ版）

## 次のステップ
- consecutiveAscents n kの下界定理の形式化
- full_cycle_boundの除算形式への変換
- 一般v2列に対する反復公式の形式化
- 連続上昇回数の上界: k ≤ log2(n+1) の形の定理
