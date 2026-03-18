# 探索20: IsTwinPrime p → p ≥ 3

## 日付
2026-03-18

## 概要
IsTwinPrime p ならば p ≥ 3 であることを形式証明。p = 0, 1, 2 の各ケースを排除。

## 追加内容

### TwinPrime.lean
- `IsTwinPrime.three_le`: IsTwinPrime p → p ≥ 3

## 証明の構造
`by_contra` で p ≤ 2 を仮定し、`interval_cases` で p = 0, 1, 2 に場合分け:
- p = 0: `Nat.not_prime_zero` で矛盾（0 は素数でない）
- p = 1: `Nat.not_prime_one` で矛盾（1 は素数でない）
- p = 2: p + 2 = 4 だが `¬ Nat.Prime 4` を `decide` で証明し矛盾

## 数学的意義
IsTwinPrime の最小値が p = 3 であることを確定。
(2, 4) は 4 が素数でないため双子素数でない。

## 証明手法
- by_contra + push_neg: 背理法
- interval_cases: 有限ケースの網羅
- Nat.not_prime_zero, Nat.not_prime_one: Mathlib の基本補題
- decide: 4 が素数でないことの計算的証明

## 評価
A — IsTwinPrime の基本的な下界を確立。interval_cases の活用例。
