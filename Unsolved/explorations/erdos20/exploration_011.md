# 探索11: ひまわりの具体例（共通coreが非空）

## 目的
これまでの探索ではcore = ∅ のひまわり（互いに素な集合族）のみを扱ってきた。
本探索では、非空のcoreを持つひまわりの具体例を構成し、Leanで形式検証する。

## 内容

### 定理: sunflower_core1
- 集合族: {1,2,3}, {1,4,5}, {1,6,7}
- core = {1}
- 花びら: {2,3}, {4,5}, {6,7} — 互いに素

### 証明の構造
1. core ⊆ S_i: `simp [Finset.subset_iff]` + `omega` で {1} ⊆ 各集合を確認
2. 花びらの互いに素性: `interval_cases i <;> interval_cases j` で全9ペアを列挙し、
   `simp_all` で getElem を簡約、`decide` で Finset の sdiff/inter を計算

### 技術的ポイント
- `decide` は Finset ℕ の sdiff (\\) と inter (∩) を具体的に計算可能
- 3元集合×3個 = 9ペアの組み合わせを interval_cases で網羅
- core が非空の場合でも同じ証明パターンが適用可能

## 結果
- `sunflower_core1` が sorry なしでビルド成功
- 非空 core のひまわりの形式検証を初めて実施
