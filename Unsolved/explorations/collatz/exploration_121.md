# 探索 121: 入次数≤2の形式証明設計

## メタデータ
- **キューID**: collatz-118
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 中発見
- **形式化価値**: 補題候補
- **関連Leanモジュール**: Collatz.Defs
- **日付**: 2026-03-29

## 発見
- 前駆ノードの完全分類: (a)偶数前駆m=2n（常に1つ）、(b)奇数前駆m=(n-1)/3（n%6=4のとき正確に1つ）
- 6補題で構成: even_pred_unique, odd_pred_unique, odd_predecessor, pred_complete, indegree_le_two, indegree_eq_two_iff
- 全核心算術はomegaで解決可能。N=10^5で不一致0件
- 推奨: Collatz/Indegree.lean新規作成、依存はDefs.leanのみ

## 次のステップ
- Indegree.leanの実装（6補題、各15-30行）
