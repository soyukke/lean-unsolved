# 探索61: mod 8 完全分類と2ステップ合成

## 主要結果
- (3n+1) mod 8 の4パターン完全分類
- collatzStep∘collatzStep(n) = (3n+1)/2 for odd n

## 証明された定理

### mod 8 完全分類 (CollatzMod3.lean セクション8)
- `three_mul_add_one_mod8_1`: n%8=1 → (3n+1)%8=4
- `three_mul_add_one_mod8_3`: n%8=3 → (3n+1)%8=2
- `three_mul_add_one_mod8_5`: n%8=5 → (3n+1)%8=0
- `three_mul_add_one_mod8_7`: n%8=7 → (3n+1)%8=6

### 2ステップ合成 (CollatzMod3.lean セクション9)
- `collatzStep_step_odd`: 奇数 n > 0 に対して collatzStep(collatzStep(n)) = (3n+1)/2

## 意義
mod 8 分類は v₂(3n+1) の正確な値を決定する:
- n%8=5 → v₂≥3, n%8=1 → v₂=2, n%8=3,7 → v₂=1

2ステップ合成は、奇数→(3n+1)→(3n+1)/2 という遷移を1つの定理で表現し、
Syracuse関数の振る舞いの解析に直接利用できる。
