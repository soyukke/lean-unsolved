# 探索19: IsCousinPrime の定義

## 目標
Cousin prime (差が4の素数ペア) に対する述語 IsCousinPrime を定義し、検証例と基本性質を追加する。

## 成果

### TwinPrime.lean への追加

1. **IsCousinPrime 定義**: `Nat.Prime p ∧ Nat.Prime (p + 4)`
2. **検証例**: IsCousinPrime 3, 7, 13, 37, 67（全て norm_num で自動証明）
3. **IsCousinPrime.mod_six**: p > 3 の cousin prime は p % 6 = 1
   - 既存の cousin_prime_mod_six のラッパー

### 素数確認
- (3,7), (7,11), (13,17), (37,41), (67,71): 全て素数ペア（Python で確認済み）

## 数学的意義
- IsTwinPrime (差2) に対応する IsCousinPrime (差4) の定義
- ドット記法 h.mod_six で既存定理にアクセス可能
- Twin: p%6=5, Cousin: p%6=1 の対比がより明確に

## ステータス
✅ 完了（sorry なし）
