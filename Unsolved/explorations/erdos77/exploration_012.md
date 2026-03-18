# 探索12: HasRamseyProperty の合成

## 目的
HasRamseyProperty n k かつ k ≥ 1 のとき n ≥ 1 を証明する。
すなわち、サイズ1以上の単色クリークの存在を保証するラムゼー性質が成り立つなら、
グラフの頂点数は少なくとも1であることを示す。

## 方針
背理法: n = 0 と仮定すると K_0 上の塗り分けを構成でき、
任意の S ⊆ Fin 0 は |S| = 0 なので |S| ≥ 1 (= k ≥ 1) と矛盾。

## 技術的ポイント
- K_0 上の `TwoColoring 0` は `Fin.elim0` で構成。
  `color : Fin 0 → Fin 0 → Bool` と `symm : ∀ i j : Fin 0, ...` の両方が
  `fun i => Fin.elim0 i` で空虚に満たされる。
- `Finset.card_le_univ S` で |S| ≤ |Fin 0| = 0 を得る。
- `hcard` で |S| = k、`hk` で k ≥ 1 なので |S| ≥ 1 だが |S| ≤ 0 と omega で矛盾。

## 結果
- `hasRamseyProperty_pos`: sorry なしで証明完了。
- ラムゼー性質の基本的な帰結として、グラフサイズの下界を形式的に確立。

## 成果物
- `Unsolved/ErdosRamsey.lean` に定理追加
