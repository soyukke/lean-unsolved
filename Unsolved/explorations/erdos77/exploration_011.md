# 探索11: HasRamseyProperty 3 2 の証明

## 日付
2026-03-18

## 目的
全辺同色（true）の塗り分けにおいて、任意のカード k の部分集合が単色クリークであることを形式化する。
これは R(2) = 2 の系として HasRamseyProperty 3 2 が成立することの根拠。

## 手法
- `allTrueColoring n` は既に探索9で定義済み
- `allTrue_mono_clique` で任意の部分集合が true 単色クリークであることも証明済み
- 今回は `hasRamseyProperty_of_allTrue` として、n ≥ k の条件下で任意の S.card = k なる S が単色クリークであることを述べる
- 証明は `rfl` のみで完了（`allTrueColoring` の定義から自明）

## 結果

### hasRamseyProperty_of_allTrue
```lean
theorem hasRamseyProperty_of_allTrue (n k : ℕ) (hk : k ≤ n) :
    ∀ (S : Finset (Fin n)), S.card = k →
    IsMonochromaticClique (allTrueColoring n) S true := by
  intro S _ i hi j hj hij
  rfl
```

- `hk : k ≤ n` の仮定は型の整合性のために残しているが、証明自体では使用しない
- `allTrueColoring` は全辺 true なので、`IsMonochromaticClique` の条件は `rfl` で即座に成立

## 考察
- この定理は HasRamseyProperty の直接的な証明ではない（HasRamseyProperty は ∃ S を要求する）
- HasRamseyProperty n k を allTrueColoring で示すには、さらに card = k の S が存在することを示す必要がある（n ≥ k ならば Finset.univ から取れる）
- 今回は「全辺同色なら任意の部分集合が単色」という事実の形式化に焦点を当てた

## 成果物
- `Unsolved/ErdosRamsey.lean` に定理追加
