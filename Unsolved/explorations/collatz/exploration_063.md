# 探索 63: collatzIter の結合法則と奇数ステップの増加性

## 日付
2026-03-18

## 概要
collatzIter の結合法則的性質（反復の加法性）を証明し、collatzReaches の推移性を導出した。
また、奇数ステップが値を増加させることの形式化を行った。

## 主要結果

### CollatzStoppingTime.lean への追加
1. **`collatzIter_zero'`**: `collatzIter 0 n = n`（明示的な定理）
2. **`collatzIter_add'`**: `collatzIter (a + b) n = collatzIter b (collatzIter a n)`
   - collatzIter の定義 `collatzIter (k+1) n = collatzIter k (collatzStep n)` に基づき、
     `a` に対する帰納法で証明
   - 注意: CollatzMinimal.lean にも同様の `collatzIter_add` が存在するが、
     CollatzStoppingTime は異なる依存チェーンにあるため直接参照できない
3. **`collatzReaches_trans`**: n が k ステップで m に到達し、m が 1 に到達するなら、n も 1 に到達する
   - `collatzIter_add'` から直接導出

### CollatzMod3.lean への追加
4. **`three_mul_add_one_ge_four`**: 奇数 n >= 1 に対して 3n+1 >= 4
5. **`three_mul_add_one_div2_ge_two`**: 奇数 n >= 1 に対して (3n+1)/2 >= 2
6. **`three_mul_add_one_div2_gt`**: 奇数 n >= 1 に対して (3n+1)/2 > n
   - 奇数ステップは必ず値を増加させることの形式化
   - Syracuse 関数の解析において重要な基本性質

## 技術的注意点
- `collatzIter` の再帰方向: `collatzIter (k+1) n = collatzIter k (collatzStep n)`
  - 「先に collatzStep してから残りを反復」という方向
  - したがって `collatzIter_add'` は `collatzIter b (collatzIter a n)` の順序が正しい
    （先に a 回、次に b 回）
- 全ての証明は sorry を使用していない

## 数学的意義
- `collatzIter_add'` は反復回数に関する合成が自然に行えることを保証する基本補題
- `collatzReaches_trans` は軌道解析で中間点を経由する推論パターンの基礎
- `three_mul_add_one_div2_gt` は奇数ステップの増加性を厳密に述べており、
  コラッツ予想の難しさの一因（奇数ステップで値が増加する）を形式的に捉えている
