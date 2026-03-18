# 探索12: 双子素数ペアの対称性

## 日付
2026-03-18

## 目的
双子素数の定義述語 `IsTwinPrime` を導入し、具体例で検証する。

## 成果

### Lean定理
- `twin_prime_second`: (p, p+2) が双子素数なら p+2 も素数（自明だが明示的に記述）
- `IsTwinPrime`: 双子素数の定義述語 `Nat.Prime p ∧ Nat.Prime (p + 2)`

### 検証例
- `IsTwinPrime 3`, `IsTwinPrime 5`, `IsTwinPrime 11`, `IsTwinPrime 17`, `IsTwinPrime 29`, `IsTwinPrime 41`
- 全て `norm_num` で自動証明

## 知見
- `IsTwinPrime` を導入することで、双子素数に関する定理の記述がより簡潔になる
- 既存の `TwinPrimeConjecture` は `∃ p > N, Nat.Prime p ∧ Nat.Prime (p + 2)` の形だが、`IsTwinPrime` を使えば `∃ p > N, IsTwinPrime p` と書ける

## sorry
なし
