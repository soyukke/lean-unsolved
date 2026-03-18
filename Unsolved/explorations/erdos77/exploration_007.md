# 探索7: ラムゼーの基本性質

## 目標
- k=0, k=1 の自明なケースでのラムゼー性質を形式化
- C5着色が三角形フリーであることの具体的検証

## 結果

### R7a: hasRamseyProperty_zero
- **定理**: 任意の n に対し `HasRamseyProperty n 0` が成り立つ
- **証明**: 空集合 ∅ は card = 0 で、空集合上の単色クリーク条件は vacuously true
- **意義**: k=0 は自明だが、基盤的な補題として他の証明で使える

### R7b: hasRamseyProperty_one
- **定理**: n >= 1 なら `HasRamseyProperty n 1` が成り立つ
- **証明**: 1頂点 {0} は card = 1 で、1要素集合の単色条件は vacuously true（i != j が不可能）
- **意義**: k=1 も自明だが、帰納法のベースケースとして有用

### R7c: C5着色の非隣接性の検証
- `c5_not_adjacent_0_2`: C5着色で頂点0と2は隣接しない（距離2）→ `decide` で証明
- `c5_not_adjacent_1_3`: C5着色で頂点1と3は隣接しない（距離2）→ `decide` で証明
- これらは C5 が三角形フリーであることの具体例

## 技術的メモ
- `Finset.not_mem_empty` は現在のMathlibバージョンでは非推奨。代わりに `simp` で処理
- Fin 5 上の `decide` は問題なく動作し、具体的な計算を簡潔に証明できる
- 既存の警告（flexible tactic linter）は以前からのもので、今回の追加部分には影響なし
