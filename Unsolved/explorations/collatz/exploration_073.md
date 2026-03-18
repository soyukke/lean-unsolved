# 探索73: collatzReaches の基数による分類

## 日付
2026-03-18

## 概要
2のべき乗 128, 256, 1024 に対して collatzReaches を証明。
collatzReaches_pow_two を利用した機械的な証明パターン。

## 成果
- `collatzReaches_128`: 2^7 = 128 が1に到達
- `collatzReaches_256`: 2^8 = 256 が1に到達
- `collatzReaches_1024`: 2^10 = 1024 が1に到達

### CollatzMod3.lean への追加
- `syracuse_eq_n_plus`: 奇数 n >= 1 に対して (3n+1)/2 = n + (n+1)/2 の恒等式

## 数学的背景
2のべき乗は k 回の半減で1に到達する。これは collatzReaches_pow_two k で直接証明可能。
Syracuse 値 (3n+1)/2 の分解式 n + (n+1)/2 は、奇数 n に対するステップの増分を直接示す。

## ファイル
- `Unsolved/CollatzStoppingTime.lean` (セクション20)
- `Unsolved/CollatzMod3.lean` (セクション18)
