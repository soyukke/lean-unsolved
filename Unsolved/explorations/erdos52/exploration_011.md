# 探索11: 3元集合の和積（等比的集合）

## 目的
等比数列的な集合 {1,2,4} の sumset と prodset のカードを計算し、
等比的集合が乗法構造を保つ（prodset が小さい）一方で
加法構造は壊れる（sumset が大きい）ことを形式的に検証する。

## 内容

### A = {1, 2, 4}
- sumset A+A = {1+1, 1+2, 1+4, 2+2, 2+4, 4+4} = {2, 3, 4, 5, 6, 8} → card = 6
- prodset A·A = {1·1, 1·2, 1·4, 2·2, 2·4, 4·4} = {1, 2, 4, 8, 16} → card = 5

### 和積予想との関連
- max(|A+A|, |A·A|) = max(6, 5) = 6 = 2|A|
- |A|^{2-ε} に対して: |A|=3 のとき 3^{2-ε} → ε ≈ 0.37 程度で等号
- 等比的集合は |A·A| を最小化するが |A+A| が大きくなる（トレードオフ）

### 証明
- `simp only [sumsetFinset]; decide` / `simp only [prodsetFinset]; decide`
- noncomputable def を simp only で展開後、decide で具体計算

## 結果
- `sumset_124_card`, `prodset_124_card` が sorry なしでビルド成功
- 等比的集合の和積トレードオフを数値的に確認
