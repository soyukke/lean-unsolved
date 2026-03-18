# 探索14: ゴールドバッハ予想の同値な定式化

## 日付
2026-03-18

## 概要
ゴールドバッハ予想の「n > 2 かつ偶数」という条件を「n ≥ 4 かつ偶数」に書き換えた同値定理を証明した。

## 追加した定理

### Goldbach.lean (探索15セクション)
1. `goldbachConjecture_iff_ge4`: GoldbachConjecture ↔ ∀ n ≥ 4, n % 2 = 0 → IsGoldbach n

## 数学的意味
- 「n > 2 かつ偶数」と「n ≥ 4 かつ偶数」は自然数上で同値
  - n > 2 かつ偶数 → n ≥ 4（偶数で n > 2 なら n ≥ 4）
  - n ≥ 4 → n > 2（自明）
- この同値変換により、ゴールドバッハ予想を「4以上の全ての偶数」という形で扱える
- 既存の `goldbachConjecture_iff` は GoldbachConjecture と IsGoldbach の同値性を示すが、
  今回の定理は下限の条件を n ≥ 4 に統一する

## 証明手法
- `constructor` で双方向を分け、各方向は `omega` で条件の同値性を示す
- `hG n (by omega) heven` で条件の変換を自動化
