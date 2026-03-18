# 探索9: ひまわりの長さに関する単調性

## 日付
2026-03-18

## 概要
4つの空集合がひまわりであることの証明を追加。
既存の `sunflower_empty_sets`（3つの空集合）の拡張として、
リスト長4のケースでも `interval_cases` による網羅的検証が有効であることを確認。

## 追加した定理

### `sunflower_four_empty`
- **主張**: `[(∅ : Finset ℕ), ∅, ∅, ∅]` はひまわり
- **証明方法**: core = ∅、花びらの互いに素性を `interval_cases i <;> interval_cases j <;> simp_all` で処理
- **意義**: 4×4 = 16 通りの組み合わせ（対角除外で12通り）を interval_cases で自動処理

## 技術的メモ
- `interval_cases i <;> interval_cases j <;> simp_all` は 4×4 のケースでも問題なく動作
- sorry なし
- 既存の `sunflower_empty_sets`（3つ）と同じパターンで拡張可能

## ファイル
- `Unsolved/ErdosSunflower.lean`
