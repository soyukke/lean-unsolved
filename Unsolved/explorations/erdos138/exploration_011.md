# 探索11: 5-AP の検証

## 日付
2026-03-18

## 目的
5項等差数列（5-AP）の回避可能性を小さい N で検証する。

## 手法
- `hasMonoAPList` を用いた `rfl` ベースの具体的計算

## 結果

### N=5 で 5-AP 回避
```lean
example : hasMonoAPList [false, true, false, true, false] 5 = false := by rfl
```
- N=5 で 5-AP は自明に回避可能
- 5-AP には d ≥ 1 が必要で、a + 4d < 5 を満たすのは a=0, d=1 のみ（位置 0,1,2,3,4）
- 交互塗り分け RBRBB では位置 0,1,2,3,4 の色が F,T,F,T,F で単色でない

### N=9 で 5-AP 回避
```lean
example : hasMonoAPList [false, false, true, false, false, true, false, true, true] 5 = false := by rfl
```
- RRBRRBRBB 塗り分けは 5-AP を含まない
- 注: 交互塗り分け（d=2 の偶数位置 AP）は偶数公差の 5-AP を含むため不適

## 考察
- 交互塗り分けは公差が奇数の AP を回避するが、偶数公差（例: d=2）では同色位置が連続するため回避できない
- W(5) = 178 なので、N=9 では 5-AP 回避は容易

## 成果物
- `Unsolved/ErdosVanDerWaerden.lean` に example 追加
