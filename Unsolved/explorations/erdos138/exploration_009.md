# 探索9: W(k) の自明な下界

## 日付
2026-03-18

## 概要
N=1（1点のみ）の塗り分けでは、任意の k ≥ 2 の等差数列を回避可能であることを
`hasMonoAPList` による rfl 検証で確認。

## 追加した検証

### k=2, N=1
- `hasMonoAPList [false] 2 = false` (rfl)
- `hasMonoAPList [true] 2 = false` (rfl)

### k=4, k=5, N=1
- `hasMonoAPList [false] 4 = false` (rfl)
- `hasMonoAPList [false] 5 = false` (rfl)

## 観察
- N=1 の場合、公差 d ≥ 1 の等差数列 a, a+d, a+2d, ... は2項目以降が範囲外
- したがって k ≥ 2 項の等差数列は存在しない
- これは W(k) ≥ 2 for all k ≥ 2 の具体的な証拠
- 探索7で既にN=1, k=3の検証があったが、今回 k=2,4,5 を追加してパターンを拡充

## 技術的メモ
- 全て `rfl` で証明完了
- sorry なし

## ファイル
- `Unsolved/ErdosVanDerWaerden.lean`
