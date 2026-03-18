# 探索7: VdW数の追加性質

## 目標
- 小さい N での等差数列回避の自明なケースを追加検証
- colorClass の要素の有界性に関する基本補題の形式化

## 結果

### W7a: 小さい N での回避可能性
リストベースの計算的検証:
- `hasMonoAPList [false] 3 = false`: N=1, 色false のみ → 3-AP回避可能
- `hasMonoAPList [true] 3 = false`: N=1, 色true のみ → 3-AP回避可能
- `hasMonoAPList [true, false] 3 = false`: N=2 → 3-AP回避可能

これらは全て `rfl` で証明可能（計算的に false と評価される）。

### W7b: colorClass_lt
- **定理**: `x ∈ colorClass c color → x < n`
- **証明**: colorClass は `Fin n` の値の像なので、各要素は `i.isLt` で n 未満
- **意義**: 等差数列の有界性を示す際の基本補題。ArithProg の最大項が N 未満であることを導くのに使える

### W7c: colorClass_subset_range
- **定理**: `colorClass c color ⊆ Finset.range n`
- **証明**: `colorClass_lt` を使って `Finset.mem_range` に帰着
- **意義**: colorClass が {0,...,n-1} の部分集合であることの形式的な表現

## 技術的メモ
- `colorClass` は `(Finset.univ.filter (fun i : Fin n => c i = color)).image Fin.val` と定義
- `Finset.mem_image` で分解すると `⟨i : Fin n, _, rfl⟩` が得られ、`i.isLt` で有界性が出る
- これらの補題は将来的に W(k) の上界・下界の議論で活用可能
