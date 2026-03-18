# 探索6: f(1,k) = k — 1-均一族のひまわり定理

## 目的
1-均一集合族（シングルトンの族）で重複なし・k個あるなら、それ自体がk-ひまわりであることを形式証明する。

## 主要結果
- `disjoint_of_card_one_ne`: サイズ1の異なるFinsetは互いに素
- `sunflower_uniform1_singletons`: 1-均一族の重複なしリストはひまわり

## 証明方針
- core = ∅ とする
- ∅ ⊆ S は自明
- 花びらの互いに素性: S_i \ ∅ = S_i で、|S_i| = 1 かつ S_i ≠ S_j からdisjointを導出
- `Finset.card_eq_one` でシングルトンに分解し、`Finset.singleton_inter_of_not_mem` で交差が空であることを示す

## 所見
f(1,k) = k は自明なケースだが、ひまわり予想の形式化における基盤定理。
Erdős-Rado上界 f(n,k) ≤ (k-1)^n · n! + 1 の n=1 ケースとも整合する。
