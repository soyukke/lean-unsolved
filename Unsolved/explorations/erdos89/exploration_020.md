# 探索20: 距離の単調性

## 目的
格子上の距離²が自然数値を取ることの形式的証明と、
5点配置における距離の具体的検証。

## 内容

### distSq_nat_valued
整数座標の点 p, q に対して distSq p q ≥ 0 なので、
`Int.toNat_of_nonneg` を用いて自然数 m が存在して distSq p q = ↑m を示す。

証明の流れ:
1. `distSq_nonneg` で 0 ≤ distSq p q を得る
2. m = (distSq p q).toNat とする
3. `Int.toNat_of_nonneg` で ↑m = distSq p q を得る

### 5点配置の検証
配置: (0,0), (1,0), (2,0), (0,1), (1,1)

- distSq (0,0) (2,0) = 4
- distSq (0,1) (1,0) = 2
- distSq (0,1) (2,0) = 5
- distSq (1,1) (2,0) = 2

全て `decide` で検証。この配置は3種類の異なる距離²（2, 4, 5）を持つ。

## 結果
- `distSq_nat_valued`: sorry なしで証明完了
- 5点配置の距離検証: 4つの example を decide で検証

## 成果物
- `Unsolved/ErdosDistinctDistances.lean` に追加
