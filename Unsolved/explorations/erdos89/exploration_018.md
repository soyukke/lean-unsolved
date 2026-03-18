# 探索18: 距離の二乗和恒等式

## 目標
distSq の定義を明示的な座標表現として展開する定理を形式証明する。

## アプローチ
distSq (a,b) (c,d) = (a-c)^2 + (b-d)^2 を unfold + ring で証明。

## 結果

### distSq_explicit
- **定理**: `distSq (a, b) (c, d) = (a - c) ^ 2 + (b - d) ^ 2`
- **証明**: `unfold distSq; ring`
- distSq の定義そのものだが、タプル型の射影 (.1, .2) を具体的な変数名で置き換えた形

### 考察
- distSq の定義は `(p.1 - q.1) ^ 2 + (p.2 - q.2) ^ 2` だが、p, q がタプルリテラルでない場合に .1, .2 の簡約が必要
- distSq_explicit は具体的な座標値を直接代入できるため、後続の計算で便利
- 既存の distSq_origin, distSq_same_x, distSq_same_y は特殊ケースだったが、これは完全な一般形
- 中点公式 |p-q|^2 + |p+q-2r|^2 の展開は複雑なため、今回は基本形の明示に留めた

## 成果物
- `Unsolved/ErdosDistinctDistances.lean` に `distSq_explicit` を追加（sorry なし）
