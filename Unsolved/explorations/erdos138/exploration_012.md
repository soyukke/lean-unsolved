# 探索12: W(3)=9 の完全性の再確認

## 目標
N=8 で 3項単色等差数列を回避する塗り分けのバリエーションを追加検証する。

## 背景
- 探索1で N=8 での回避塗り分けは正確に6個（3ペアの色反転）と判明
- RRBBRRBB は既存（探索3）

## 追加検証
- BRRBBRRB: `hasMonoAPList [true, false, false, true, true, false, false, true] 3 = false`
- BBRRBBRR: `hasMonoAPList [true, true, false, false, true, true, false, false] 3 = false`

両方とも `rfl` で検証成功。

## 考察
これらは RRBBRRBB の巡回シフトおよび色反転バリエーション。
6個の回避塗り分けは全て周期2のブロック構造を持ち、
RRBB/BBRR パターンの巡回シフトと色反転で網羅される。
N=9 では `allColoringsHaveAP3 9 = true` が既に検証済みなので、
W(3)=9 の完全な形式的検証が達成されている。
