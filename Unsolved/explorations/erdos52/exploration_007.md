# 探索7: sumset/productset の追加性質

## 目的
sumset と productset の単調性および上界を形式証明する。

## 主要結果

### 単調性
- `sumsetFinset_mono`: A ⊆ B → sumset(A) ⊆ sumset(B)
- `prodsetFinset_mono`: A ⊆ B → prodset(A) ⊆ prodset(B)

### 上界
- `sumsetFinset_card_le_sq`: |A+A| <= |A|^2
- `prodsetFinset_card_le_sq`: |A*A| <= |A|^2

## 証明方針

### 単調性
mem_sumsetFinset / mem_prodsetFinset で展開し、A の元が B の元でもあることから直接導出。

### 上界
sumset(A) = image(+, A x A) なので:
1. |image(f, S)| <= |S| (Finset.card_image_le)
2. |A x A| = |A| * |A| (Finset.card_product)
を組み合わせて omega で完了。

## 所見
|A+A| <= |A|^2 は自明だが、Sum-Product 予想の文脈では重要な上界。
等差数列では |A+A| = 2|A|-1 と線形であり、この |A|^2 上界は非常に緩い。
単調性は部分集合に対する議論で有用な基本ツール。
既存の下界 |A+A| >= |A|, |A*A| >= |A| と合わせて、sumset/productset のサイズが
|A| と |A|^2 の間にあることが形式的に確立された。
