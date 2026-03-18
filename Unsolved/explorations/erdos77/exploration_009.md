# 探索9: 自明な塗り分けの例

## 日付
2026-03-18

## 概要
全ての辺を同色（true）に塗る `allTrueColoring` を定義し、
この塗り分けにおいて任意の頂点部分集合が単色クリークとなることを証明。

## 追加した定義・定理

### `allTrueColoring`
- **定義**: `TwoColoring n` で全ての辺の色が `true`
- **対称性**: `fun _ _ => rfl` で自明

### `allTrue_mono_clique`
- **主張**: `allTrueColoring n` において任意の `S : Finset (Fin n)` が色 `true` の単色クリーク
- **証明**: `rfl` のみ（色関数が定数なので自明）
- **意義**: ラムゼー理論において「自明な塗り分け」の基本例。
  全て同色の場合、K_n 全体が単色クリークとなり、ラムゼー性質は k ≤ n で自明に成立。

## 技術的メモ
- `rfl` のみで証明完了（最もシンプルな証明）
- sorry なし

## ファイル
- `Unsolved/ErdosRamsey.lean`
