# 探索16: 距離と内積の関係

## 目標
距離の二乗を内積を用いて展開する公式を形式証明する。

## アプローチ
|p-q|² = |p|² + |q|² - 2⟨p,q⟩ という標準的な恒等式を ring タクティクで証明。

## 結果

### distSq_expand
- **定理**: `distSq p q = distSq p (0,0) + distSq q (0,0) - 2 * (p.1 * q.1 + p.2 * q.2)`
- 証明: `unfold distSq; ring`
- 左辺は (p₁-q₁)²+(p₂-q₂)²、右辺は (p₁²+p₂²)+(q₁²+q₂²)-2(p₁q₁+p₂q₂)

### 意義
- この公式は距離問題を内積（双線形形式）の言語で扱うための基礎
- Guth-Katz の証明で使われる Elekes-Sharir 変換では、距離の等式を代数的条件に翻訳する際にこの種の展開が本質的
- distSq_origin_add（探索13）と合わせて、距離の代数的性質の体系的な整備が進んだ

### 関連する既存結果
- `distSq_origin`: distSq(0,0)(x,y) = x²+y²
- `distSq_origin_add`: 二次形式としての加法分解
- `sum_sq_mul_sum_sq`: Brahmagupta-Fibonacci 恒等式

## 成果物
- `Unsolved/ErdosDistinctDistances.lean` に `distSq_expand` を追加（sorry なし）
