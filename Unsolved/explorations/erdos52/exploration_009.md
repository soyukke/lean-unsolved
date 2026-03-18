# 探索9: 2元集合の和積比較

## 日付
2026-03-18

## 概要
2元集合 {1,3} と {2,3} の sumset/prodset のカード数を decide で検証。
いずれも |A+A| = |A·A| = 3 となり、2元集合では和と積が同サイズとなることを確認。

## 追加した定理

### `sumset_13_card` / `prodset_13_card`
- {1, 3}: sumset = {2, 4, 6}, card = 3
- {1, 3}: prodset = {1, 3, 9}, card = 3

### `sumset_23_card` / `prodset_23_card`
- {2, 3}: sumset = {4, 5, 6}, card = 3
- {2, 3}: prodset = {4, 6, 9}, card = 3

## 観察
- 2元集合 {a, b} (a < b) では:
  - sumset = {2a, a+b, 2b} で常にカード3（a < a+b < 2b なので3つ全て異なる）
  - prodset = {a², ab, b²} でカード3（a² < ab < b² なので3つ全て異なる、a,b > 0 のとき）
- max(|A+A|, |A·A|) = 3 > 2 = |A| なので和積予想と整合的

## 技術的メモ
- `simp only [sumsetFinset]; decide` / `simp only [prodsetFinset]; decide` で全て証明
- sorry なし

## ファイル
- `Unsolved/ErdosSumProduct.lean`
