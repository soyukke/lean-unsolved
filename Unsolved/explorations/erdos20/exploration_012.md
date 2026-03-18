# 探索12: 2-均一族のひまわり検証

## 目標
2-均一集合族（各集合のサイズが2）の具体例でひまわり性を検証する。

## アプローチ
互いに素な2元集合3つ {1,5}, {2,6}, {3,7} がcore=空のひまわりであることをLeanで形式証明。

## 結果

### sunflower_disjoint_156
- **定理**: `IsSunflower [({1, 5} : Finset ℕ), {2, 6}, {3, 7}]`
- **証明**: core=∅ として、`Finset.empty_subset` で包含条件、`interval_cases` + `decide` で花びらの互いに素性を検証
- 既存の `sunflower_disjoint_three` ({0,1},{2,3},{4,5}) と同様の構造だが、非連続な要素を使用

### 考察
- 2-均一族では、互いに素な集合が3つあれば自明にひまわり（core=∅）
- これはf(2,3)の下界探索の基礎：互いに素でない場合（要素の共有がある場合）にひまわりを回避する構造が問題の本質
- sunflower_disjoint_three との違いは要素の選び方のみで、証明戦略は完全に同一

## 成果物
- `Unsolved/ErdosSunflower.lean` に `sunflower_disjoint_156` を追加（sorry なし）
