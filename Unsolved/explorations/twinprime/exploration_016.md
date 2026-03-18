# 探索16: TwinPrimeConjecture の同値な定式化

## 日付
2026-03-18

## 目的
TwinPrimeConjecture を IsTwinPrime 述語を使って書き直せることを形式証明する。

## 結果

### twinPrimeConjecture_iff
```
theorem twinPrimeConjecture_iff :
    TwinPrimeConjecture ↔ ∀ N : ℕ, ∃ p : ℕ, p > N ∧ IsTwinPrime p
```

- TwinPrimeConjecture は `∀ N, ∃ p > N, Nat.Prime p ∧ Nat.Prime (p+2)` と定義
- IsTwinPrime は `Nat.Prime p ∧ Nat.Prime (p+2)` と定義
- unfold すると両辺が構造的に同一なので、obtain + exact で証明

## 数学的意義
- IsTwinPrime 述語を使った表記 `∀ N, ∃ p > N, IsTwinPrime p` がより簡潔
- 今後 IsTwinPrime の性質（mod 6, mod 30 等）を直接適用しやすくなる
- 探索13-14で定義した IsTwinPrime.prime_left, .prime_right, .mod_six 等との連携が容易に

## ステータス
✅ sorry なし、lake build 通過

## 成果物
- TwinPrime.lean に追加
