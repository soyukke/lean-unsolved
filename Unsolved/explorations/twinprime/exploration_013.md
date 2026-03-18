# 探索13: IsTwinPrime の基本性質

## 日付
2026-03-18

## 概要
探索12で導入した `IsTwinPrime` 述語に対するドット記法アクセサ（射影定理）を追加した。

## 追加した定理

### TwinPrime.lean (探索13セクション)
1. `IsTwinPrime.prime_left`: IsTwinPrime p → Nat.Prime p
2. `IsTwinPrime.prime_right`: IsTwinPrime p → Nat.Prime (p + 2)
3. `IsTwinPrime.two_le`: IsTwinPrime p → p ≥ 2

## 数学的意味
- `IsTwinPrime` は `Nat.Prime p ∧ Nat.Prime (p + 2)` の略記だが、ドット記法アクセサを提供することで使い勝手が向上
- `h.prime_left` で p の素数性、`h.prime_right` で p+2 の素数性を取り出せる
- `h.two_le` は `h.prime_left.two_le` の短縮で、p ≥ 2 を直接得られる
- 今後 IsTwinPrime を前提とする定理で、射影を簡潔に書ける

## 証明手法
- `prime_left` と `prime_right` は `And` の射影（h.1, h.2）
- `two_le` は `Nat.Prime.two_le` への委譲

## sorry
なし
