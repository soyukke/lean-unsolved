# 探索64: (3n+1)/2 の mod 性質と collatzReaches 3

## 日付
2026-03-18

## 概要
Syracuse 関数 f(n) = (3n+1)/2 の剰余性質を追加し、具体的な軌道検証（n=3）を行った。

## 追加した定理

### CollatzMod3.lean (セクション13)
1. `syracuse_even_of_mod4_eq1`: n ≡ 1 (mod 4) → (3n+1)/2 は偶数
2. `syracuse_mod4_of_mod8_eq3`: n ≡ 3 (mod 8) → (3n+1)/2 ≡ 1 (mod 4)
3. `syracuse_mod4_of_mod8_eq7`: n ≡ 7 (mod 8) → (3n+1)/2 ≡ 3 (mod 4)

### CollatzStoppingTime.lean (セクション11)
4. `collatzReaches_three`: 3 はコラッツ操作で1に到達する（7ステップ）
5. 軌道の検証例: collatzStep 3 = 10, collatzStep 10 = 5, collatzStep 5 = 16

## 数学的意味
- Syracuse 関数の mod 4 性質により、奇数入力後の次のステップが偶数か奇数かを事前に判定できる
- n ≡ 1 (mod 4) のとき Syracuse 値は偶数 → 次も割り算ステップ（連続的な値の減少）
- n ≡ 3 (mod 4) のとき Syracuse 値は奇数 → 次は 3x+1 ステップ（値の増加）
- 3 の軌道: 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1（7ステップで到達）

## 証明手法
- 全て `omega` または `decide` で完結
- `collatzReaches_three` は `⟨7, by decide⟩` で具体的に構成
