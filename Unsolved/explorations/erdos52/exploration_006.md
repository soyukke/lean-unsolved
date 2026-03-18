# 探索6: |A·A| ≥ |A| の証明

## 目的
有限正整数集合 A に対して productset のサイズが元の集合以上であることを形式証明する。

## 主要結果
- `card_le_prodsetFinset_card`: ∀ a ∈ A, a > 0 → |A·A| ≥ |A|

## 証明方針
`card_le_sumsetFinset_card`（|A+A| ≥ |A|）と同様のアプローチ:
1. A の最小元 m を取る（m > 0）
2. A.image (· * m) ⊆ prodsetFinset A を示す
3. (· * m) は A 上で単射（m > 0 なので a₁ * m = a₂ * m → a₁ = a₂）
4. よって |A.image (· * m)| = |A| ≤ |prodsetFinset A|

## 仮定の必要性
0 ∈ A の場合、0 * a = 0 で全ての積が潰れるため |A·A| < |A| となりうる。
例: A = {0, 1, 2} → A·A = {0, 1, 2, 4} で |A·A| = 4 > 3 = |A| は成立するが、
A = {0, 1} → A·A = {0, 1} で |A·A| = 2 = |A| で等号。
一般には ∀ a ∈ A, a > 0 の仮定で十分。

## 所見
Sum-Product予想の max(|A+A|, |A·A|) ≥ C|A|^{2-ε} に対する最も弱い下界。
Plünnecke-Ruzsa不等式の数値検証も併せて実施。
