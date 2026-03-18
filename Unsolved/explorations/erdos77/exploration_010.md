# 探索10: allFalseColoring

## 目的
allTrueColoring（探索9）の双対として、全辺を false で塗る塗り分けを定義し、
任意の部分集合が false 単色クリークであることを証明する。

## 手法
- allFalseColoring n: 全ての辺の色を false にする TwoColoring n
- symm 条件は rfl で自明に成立
- IsMonochromaticClique の証明も rfl で完了

## 結果

### allFalseColoring
```
def allFalseColoring (n : ℕ) : TwoColoring n where
  color := fun _ _ => false
  symm := fun _ _ => rfl
```

### allFalse_mono_clique
任意の n と S : Finset (Fin n) に対して、
`IsMonochromaticClique (allFalseColoring n) S false` が成立。
証明は rfl 一発。

## 考察
- allTrueColoring と allFalseColoring は、ラムゼー理論の自明なケースを示す
- n ≥ R(k) のとき、任意の塗り分けに単色 K_k が存在するが、
  自明な塗り分けでは任意のサイズの単色クリークが存在する
- 非自明な塗り分け（例: C5着色）で単色クリークを回避する方が本質的
- 今後の方向: 「最大単色クリークサイズが最小となる塗り分け」の特徴付け

## sorry なし
全証明が sorry なしで完了。
