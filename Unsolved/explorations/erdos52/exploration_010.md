# 探索10: A={1,...,n} の sumset カード = 2n-1

## 日付
2026-03-18

## 目的
等差数列 {1,2,...,n} の sumset と productset のカード数を具体例で検証する。

## 成果

### Lean定理
- `sumset_1234_card`: `(sumsetFinset {1, 2, 3, 4}).card = 7`
  - A = {1,2,3,4} の sumset = {2,3,4,5,6,7,8}、カード = 2*4-1 = 7
- `prodset_1234_card`: `(prodsetFinset {1, 2, 3, 4}).card = 9`
  - A = {1,2,3,4} の productset = {1,2,3,4,6,8,9,12,16}、カード = 9

### パターン確認
- {1,2,3}: sumset card = 5 = 2*3-1 (既存)
- {1,2,3,4}: sumset card = 7 = 2*4-1 (新規)
- 等差数列 {1,...,n} の sumset カードは常に 2n-1（最小の sumset サイズ）
- productset は sumset より大きい: 6 vs 5 (n=3)、9 vs 7 (n=4)

## 知見
- 等差数列は加法的に構造化されているため |A+A| = 2n-1 と最小
- 一方 |A·A| は n に対して超線形に増大（Erdős-Szemerédi 予想の「敵」にはならない）
- decide タクティクで4元集合の計算も問題なく完了

## sorry
なし
