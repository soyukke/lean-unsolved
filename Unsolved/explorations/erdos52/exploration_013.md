# 探索13: sumset の自明な等式

## 目標
空集合の sumset と productset が空であることを形式証明する。

## アプローチ
sumsetFinset と prodsetFinset の定義を展開し、simp で自動証明。

## 結果

### sumsetFinset_empty
- **定理**: `sumsetFinset (∅ : Finset ℕ) = ∅`
- **証明**: `simp [sumsetFinset]`
- 空集合の直積 ∅ ×ˢ ∅ = ∅ なので、image も ∅

### prodsetFinset_empty
- **定理**: `prodsetFinset (∅ : Finset ℕ) = ∅`
- **証明**: `simp [prodsetFinset]`
- 同様に空集合の直積から従う

### 考察
- これらは sumsetFinset/prodsetFinset の基本的な境界条件
- 既存の sumsetFinset_nonempty/prodsetFinset_nonempty（非空集合の場合）と対になる性質
- card_le_sumsetFinset_card の hA = ∅ 分岐で暗黙に使われている性質を明示化

## 成果物
- `Unsolved/ErdosSumProduct.lean` に `sumsetFinset_empty`, `prodsetFinset_empty` を追加（sorry なし）
