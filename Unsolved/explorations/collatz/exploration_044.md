# 探索44: stoppingTime の奇数下界

## 目的
奇数 n > 1 に対して stoppingTime(n) >= 2 を証明する。

## 主要結果
- stoppingTime_odd_ge_two: 奇数 n > 1 → s(n) >= 2

## 証明方針
- ステップ0: collatzIter 0 n = n > 1 ≠ 1
- ステップ1: collatzIter 1 n = 3n+1 >= 4 > 1（n が奇数かつ n > 1 なので n >= 3）

stoppingTime は Nat.find で定義されているため、stoppingTime < 2 を仮定して
interval_cases で 0 と 1 の場合に分け、それぞれ矛盾を導く。

## Lean定理
- `collatzIter_one_odd_gt_one`: 奇数 n > 1 に対して collatzIter 1 n ≠ 1
- `stoppingTime_odd_ge_two`: 奇数 n > 1 の stopping time は 2 以上

## 所見
奇数は1ステップで偶数(3n+1)になり、それはまだ1ではない。
この定理は stopping time の下界を与える基本的な結果であり、
より精密な mod 分類（mod 4, mod 8）による下界の改善への出発点となる。
