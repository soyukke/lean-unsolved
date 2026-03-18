# 探索76: (3n+1) % 12 完全分類 + collatzReaches 23, 25

## 日付: 2026-03-18

## 目的
- コラッツ写像の mod 12 における性質を解明
- 奇数の到達可能性検証を拡張

## 結果

### (3n+1) % 12 の完全分類
奇数 n に対して (3n+1) % 12 は必ず 4 か 10:
- n%12=1: (3+1)%12=4
- n%12=3: (9+1)%12=10
- n%12=5: (15+1)%12=4
- n%12=7: (21+1)%12=10
- n%12=9: (27+1)%12=4
- n%12=11: (33+1)%12=10

パターン: n%4=1 なら 4、n%4=3 なら 10。

### collatzReaches の拡張
- collatzReaches 23: 15ステップで1に到達（Python確認済み）
- collatzReaches 25: 23ステップで1に到達（Python確認済み）

## Lean 成果物
- `three_mul_add_one_mod12_cases`: omega で自動証明
- `collatzReaches_23`: decide で検証
- `collatzReaches_25`: decide で検証

## 評価: B
mod 12 分類は mod 6 の自然な拡張。(3n+1) % 12 ∈ {4, 10} は mod 4 構造に帰着。
