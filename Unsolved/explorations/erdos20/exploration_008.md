# 探索8: 2集合族のひまわり性

## 目的
任意の2つの集合からなる族 [S, T] が必ずひまわりであることを形式証明する。
これはひまわり定義の基本的な性質の検証。

## 主要結果
- `isSunflower_pair`: 任意の S, T : Finset α に対し、IsSunflower [S, T]

## 証明方針
- core = S ∩ T とする
- S ∩ T ⊆ S は `Finset.inter_subset_left`、S ∩ T ⊆ T は `Finset.inter_subset_right`
- 花びらの互いに素条件: `interval_cases` で i, j ∈ {0,1} を場合分け
  - i = j のケースは `simp_all` で矛盾
  - i = 0, j = 1: (S \ (S∩T)) ∩ (T \ (S∩T)) = ∅ を ext + simp で証明
    - x ∈ S かつ x ∉ S∩T かつ x ∈ T は矛盾（x ∈ S ∧ x ∈ T → x ∈ S∩T）
  - i = 1, j = 0: 対称的

## 所見
2集合族が常にひまわりであることは、ひまわり予想の文脈での基本事実。
k-ひまわりの問題は k ≥ 3 で初めて非自明になることを形式的に確認。
既存の isSunflower_nil（0集合）、isSunflower_singleton（1集合）と合わせて、
小さい族のサイズ 0, 1, 2 に対するひまわり性が完全に確立された。
