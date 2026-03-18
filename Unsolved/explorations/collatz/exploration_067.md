# 探索67: collatzReaches の合成性質

## 日付: 2026-03-18

## 目的
偶数 n に対して `collatzReaches n ↔ collatzReaches (n/2)` を証明する。
コラッツ到達可能性が偶数の半減で保存されることの形式化。

## 手法
`collatzIter_succ` の展開方向 (`collatzIter (k+1) n = collatzIter k (collatzStep n)`) を利用。
偶数 n に対して `collatzStep n = n/2` なので、1ステップ追加/除去で同値性が得られる。

### 順方向 (collatzReaches n → collatzReaches (n/2))
- k=0 の場合: n=1 だが n%2=0 と矛盾 (omega)
- k=succ の場合: `collatzIter_succ` と `collatzStep_even_eq_div2` で rewrite

### 逆方向 (collatzReaches (n/2) → collatzReaches n)
- k+1 ステップで到達: 最初のステップで n → n/2、残りの k ステップで 1 に到達

## 成果物
- `collatzReaches_even_iff`: CollatzStoppingTime.lean に追加
- sorry なし、lake build 通過

## 評価: B
基本的だが有用な同値定理。既存の `collatzReaches_double_of` / `collatzReaches_of_double` の一般化。
