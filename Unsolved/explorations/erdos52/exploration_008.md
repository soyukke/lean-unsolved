# 探索8: 特殊集合の sumset/productset

## 目的
シングルトン集合の sumset/productset を計算し、和積問題の自明な等号ケースを確認する。
また {1,2} での具体的な計算例を追加する。

## 主要結果

### シングルトンの sumset/productset
- `sumsetFinset_singleton`: sumset({a}) = {a+a}
- `prodsetFinset_singleton`: prodset({a}) = {a*a}

### 具体例
- `sumset_12_card`: |{1,2}+{1,2}| = 3（{2,3,4}）
- `prodset_12_card`: |{1,2}·{1,2}| = 3（{1,2,4}）

## 証明方針

### シングルトン定理
- `mem_sumsetFinset` / `mem_prodsetFinset` で展開
- singleton の membership を simp で簡約
- 順方向: b = a, c = a から b+c = a+a
- 逆方向: a, a を具体的な証人として提供

### 具体例
- `simp only [sumsetFinset]` / `simp only [prodsetFinset]` で定義展開
- `decide` で有限計算を自動処理（既存の sumset_123_card と同じパターン）

## 所見
シングルトン {a} は max(|A+A|, |A·A|) = 1 = |A| となる自明な等号ケース。
Sum-Product 予想は |A| ≥ 2 を前提とするが、これは |A| = 1 では成立しないため。
{1,2} の例では |A+A| = |A·A| = 3 > 2 = |A| で、既に |A|^{2-ε} ≈ 2^{1.5} ≈ 2.83
程度の下界は達成されている。
既存の下界 |A| ≤ |A+A|, |A| ≤ |A·A| と上界 |A+A|, |A·A| ≤ |A|^2 の間の
より精密な評価に向けた基礎事例。
