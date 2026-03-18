# 探索69: コラッツ写像の増減まとめ + collatzReaches 合成

## 日付
2026-03-18

## 目的
- コラッツ写像の増減に関する上界定理を追加
- collatzReaches の具体的な到達可能性を拡張

## 成果

### CollatzMod3.lean への追加
- `three_mul_add_one_div2_le_two_mul`: 奇数 n >= 1 に対して (3n+1)/2 <= 2n（omega で証明）

### CollatzStoppingTime.lean への追加
- `collatzReaches_thirteen`: 13 が 9 ステップで 1 に到達（decide で証明）
- `collatzReaches_fifteen`: 15 が 17 ステップで 1 に到達（decide で証明）
- `collatzReaches_sixteen`: 16 = 2^4 が 1 に到達（collatzReaches_pow_two 4 で証明）

## 数学的背景

### (3n+1)/2 <= 2n の証明
奇数 n >= 1 に対して:
- 3n+1 <= 4n（n >= 1 のとき）
- よって (3n+1)/2 <= 2n

これは奇数ステップでの増加が高々2倍であることを示す。
three_mul_add_one_div2_gt（既存: (3n+1)/2 > n）と合わせて、
奇数ステップの出力は (n, 2n] の範囲に収まることがわかる。

### 到達可能性の経路
- 13 -> 40 -> 20 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 (9ステップ)
- 15 -> 46 -> 23 -> 70 -> 35 -> 106 -> 53 -> 160 -> 80 -> 40 -> 20 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 (17ステップ)
- 16 = 2^4 -> 8 -> 4 -> 2 -> 1 (4ステップ)

## sorry の有無
なし

## 評価
B — 基本的な定理と具体例の追加
