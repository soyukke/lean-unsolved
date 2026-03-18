# 探索17: 距離の非退化性

## 日付
2026-03-18

## 目的
軸上の格子点間の距離公式 distSq_axes を形式化する。

## 手法
- `ring` タクティクによる代数的等式の自動証明

## 結果

### distSq_axes
```lean
theorem distSq_axes (a b : ℤ) : distSq (a, 0) (0, b) = a ^ 2 + b ^ 2 := by
  unfold distSq; ring
```

- 格子点 (a, 0) と (0, b) の距離の二乗が a^2 + b^2 であることを示す
- これは distSq_origin の一般化（原点 (0,0) と (a, b) ではなく、軸上の2点間）
- ピタゴラスの定理の座標表示

## 考察
- distSq_same_x, distSq_same_y は同一軸上の2点の距離を扱ったが、distSq_axes は異なる軸上の2点
- この公式はピタゴラス三つ組 a^2 + b^2 = c^2 の幾何的解釈に直結
- 例: distSq_axes 3 4 = 9 + 16 = 25 = 5^2

## 成果物
- `Unsolved/ErdosDistinctDistances.lean` に定理追加
