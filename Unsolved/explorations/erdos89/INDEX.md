# Erdős #89 異なる距離問題 探索インデックス

各探索の詳細は個別ファイルに記録。ステータス: ✅完了 🔬進行中 ❌失敗/放棄

## 概要

Erdős #89: n 点の平面配置における異なる距離の最小数 d(n) について、
Erdős は d(n) ≥ cn/√log(n) と予想（整数格子が最適）。
Guth-Katz (2015) が d(n) ≥ cn/log(n) を証明。

## 探索一覧

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 1 | Lean形式化 | ✅ | ErdosDistinctDistances.lean | Point, distSq, distinctDistSqSet, ErdosDistinctDistConjecture (sorry なし) |
| 2 | 格子比較・Landau-Ramanujan検証 | ✅ | scripts/erdos89_distinct_distances.py | 整数格子が最少、d(grid)/(n/√logn) ≈ 1.1-1.3 |
| 3 | (未実施) | - | - | - |
| 4 | 最小距離配置の最適化 | ✅ | scripts/erdos89_optimization.py | 焼きなまし法で格子と同等/微改善、d(n)≈n^0.82、格子が最適候補 |
| 5 | Guth-Katz証明の鍵アイデア数値検証 | ✅ | scripts/erdos89_guth_katz.py | Q=Σt(d)²のスケーリング検証、Q/(n³logn)≈0.17一定、Elekes-Sharir変換の数値的確認 |

## 主要知見

- **格子の最適性**: 焼きなまし法でも整数格子以下の距離数は見つからない（n≤25）
- **Guth-Katz の核心**: Q(P) = Σ t(d)² ≤ Cn³log(n) を Elekes-Sharir + 代数幾何で証明
  - Cauchy-Schwarz から d(P) ≥ cn/log(n) が従う
  - 格子上で Q/(n³logn) ≈ 0.17 と安定（理論と整合）
- **Erdős予想との差**: log(n) vs √log(n) のギャップが残る
- **d(n) のスケーリング**: 小さい n では d(n) ≈ n^0.82 程度（n が小さいため漸近挙動と異なる）

## 未着手の方向

| 方向 | 概要 | 優先度 |
|------|------|--------|
| Lean での Guth-Katz 下界の形式化 | Q の上界の代数幾何部分は困難 | ★ |
| 非整数座標での最適配置探索 | 実数座標なら格子より少ない距離数が可能か | ★★ |
| 高次元への拡張 | d 次元での異なる距離問題 | ★ |
