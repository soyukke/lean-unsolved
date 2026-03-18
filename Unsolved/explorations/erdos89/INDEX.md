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
| 6 | n ≥ 2 点 → 異なる距離 ≥ 1 | ✅ | ErdosDistinctDistances.lean | distinctDistSqSet_nonempty_of_two_points, numDistinctDist_ge_one |
| 7 | 共線点集合の異なる距離 | ✅ | ErdosDistinctDistances.lean | 3点・4点の共線配置で距離²を具体検証、共線配置は n-1 個の異なる距離 |
| 8 | distSq の座標別分解と基本性質 | ✅ | ErdosDistinctDistances.lean | distSq_same_x, distSq_same_y, distSq_origin（ring で自動証明） |
| 9 | 距離の平行移動不変性 | ✅ | ErdosDistinctDistances.lean | distSq_translate, distSq_rotate90, distSq_reflect_y（等長変換の不変性） |
| 10 | 格子点距離の追加検証 | ✅ | ErdosDistinctDistances.lean | 2x2格子全距離、ピタゴラス数 (3,4,5), (5,12,13) の検証 |
| 11 | 距離のスケーリング | ✅ | ErdosDistinctDistances.lean | distSq_scale（k倍で距離²がk²倍）、distSq_neg（原点対称で距離不変） |
| 12 | 正方格子の追加検証 | ✅ | ErdosDistinctDistances.lean | 3x3格子の距離例、距離²=5の多重出現、三角格子風配置 |
| 13 | 距離の加法性 | ✅ | ErdosDistinctDistances.lean | distSq_origin_add: 原点からの距離²の二次形式展開 |
| 14 | Brahmagupta-Fibonacci恒等式の系 | ✅ | ErdosDistinctDistances.lean | distSq_double_origin: 座標2倍で距離²が4倍 |
| 15 | ピタゴラス三つ組の距離 | ✅ | ErdosDistinctDistances.lean | (3,4,5),(5,12,13),(8,15,17)の距離²をdecideで検証 |
| 16 | 距離と内積の関係 | ✅ | ErdosDistinctDistances.lean | distSq_expand: |p-q|²=|p|²+|q|²-2⟨p,q⟩をringで証明 |
| 17 | 距離の非退化性 | ✅ | ErdosDistinctDistances.lean | distSq_axes: 格子点(a,0)と(0,b)の距離²=a²+b²をringで証明 |
| 18 | 距離の二乗和恒等式 | ✅ | ErdosDistinctDistances.lean | distSq_explicit: distSq(a,b)(c,d)=(a-c)²+(b-d)²の明示的展開 |

## 主要知見

- **格子の最適性**: 焼きなまし法でも整数格子以下の距離数は見つからない（n≤25）
- **Guth-Katz の核心**: Q(P) = Σ t(d)² ≤ Cn³log(n) を Elekes-Sharir + 代数幾何で証明
  - Cauchy-Schwarz から d(P) ≥ cn/log(n) が従う
  - 格子上で Q/(n³logn) ≈ 0.17 と安定（理論と整合）
- **Erdős予想との差**: log(n) vs √log(n) のギャップが残る
- **d(n) のスケーリング**: 小さい n では d(n) ≈ n^0.82 程度（n が小さいため漸近挙動と異なる）
- **共線配置の非効率性**: 等間隔共線 n 点は n-1 個の異なる距離（二次元格子の Θ(n/√log n) より大）
- **座標別分解**: distSq の代数的性質を ring で自動証明、高次元への基盤整備

## 未着手の方向

| 方向 | 概要 | 優先度 |
|------|------|--------|
| Lean での Guth-Katz 下界の形式化 | Q の上界の代数幾何部分は困難 | ★ |
| 非整数座標での最適配置探索 | 実数座標なら格子より少ない距離数が可能か | ★★ |
| 高次元への拡張 | d 次元での異なる距離問題 | ★ |
