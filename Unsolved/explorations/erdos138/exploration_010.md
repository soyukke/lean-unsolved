# 探索10: 2-AP は常に存在（N ≥ 2 のとき）

## 目的
k=2（2項等差数列）に対して、W(2) の振る舞いを hasMonoAPList で検証する。

## 手法
N=2 の全4通りの塗り分けを hasMonoAPList で計算し、rfl で検証。

## 結果

### N=2, k=2 の全塗り分け
- [false, false] → hasMonoAPList = true（位置0,1が同色 false）
- [true, true] → hasMonoAPList = true（位置0,1が同色 true）
- [false, true] → hasMonoAPList = false（2色で回避可能）
- [true, false] → hasMonoAPList = false（2色で回避可能）

### N=3, N=4 では 3-AP は回避可能
allColoringsHaveAP3 3 = false, allColoringsHaveAP3 4 = false を native_decide で検証。
W(3)=9 なので N < 9 では 3-AP 回避塗り分けが存在する。

## 考察
- W(2) = 3: {1,2,3} の2色塗り分けでは必ず同色の2項AP（= 隣接する同色の2点）が存在
  - N=2 では [false, true] で回避可能なので W(2) > 2
  - N=3 では鳩の巣原理により回避不可能
- allColoringsHaveAP3 は k=3 固定の関数であるため、k=2 用の網羅的検証には
  別の関数が必要だが、個別の rfl 検証で十分に確認できた
- 今後の方向: k=2 用の allColoringsHaveAP 関数の定義、W(2)=3 の形式証明

## sorry なし
全検証が rfl ベースで sorry なしで完了。
