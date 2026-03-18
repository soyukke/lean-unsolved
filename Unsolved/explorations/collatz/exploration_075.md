# 探索75: mod 6 完全分類 + 奇数到達性の系統的検証

## 日付
2026-03-18

## 概要
CollatzMod3.lean に `three_mul_add_one_mod6` を追加し、奇数 n に対して (3n+1) % 6 = 4 が常に成立することを証明。
CollatzStoppingTime.lean に collatzReaches 17, 19, 21 を追加。

## 成果

### CollatzMod3.lean
- `three_mul_add_one_mod6`: 奇数 n に対して (3n+1) % 6 = 4（omega で一発）
  - n%6=1: (3+1)%6=4
  - n%6=3: (9+1)%6=4
  - n%6=5: (15+1)%6=4
  - 全ての奇数で一致するのは mod 6 の構造的性質

### CollatzStoppingTime.lean
- `collatzReaches_17`: 17 は 12 ステップで 1 に到達
- `collatzReaches_19`: 19 は 20 ステップで 1 に到達
- `collatzReaches_21`: 21 は 7 ステップで 1 に到達

## Python検証
- 17→52→26→13→40→20→10→5→16→8→4→2→1 (12ステップ) OK
- 21→64→32→16→8→4→2→1 (7ステップ) OK

## sorry
なし
