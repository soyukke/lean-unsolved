# 探索68: collatzReaches の奇数版

## 日付
2026-03-18

## 目的
collatzReaches_even_iff（探索67）の奇数版を証明する。
奇数 n > 1 に対して collatzReaches n ↔ collatzReaches (3*n+1) を形式化。

## 手法
- collatzStep_odd_eq を使い、奇数 n の collatzStep が 3*n+1 であることを活用
- collatzIter_succ による1ステップ展開で双方向の同値を証明

## 結果

### collatzReaches_odd_iff
```
theorem collatzReaches_odd_iff (n : ℕ) (hn : n > 1) (hodd : n % 2 = 1) :
    collatzReaches n ↔ collatzReaches (3 * n + 1)
```

- (→) 方向: k=0 なら n=1 で hn と矛盾。k=succ k' なら collatzIter_succ と collatzStep_odd_eq で展開
- (←) 方向: k+1 ステップに持ち上げて同様に展開

## 数学的意義
- 探索67の collatzReaches_even_iff と合わせて、collatzReaches が collatzStep の1ステップで保存されることを完全にカバー
- 偶数版: collatzReaches n ↔ collatzReaches (n/2)
- 奇数版: collatzReaches n ↔ collatzReaches (3n+1)
- この2つを組み合わせると、任意の n > 1 に対して collatzReaches が1ステップ先と同値であることが示せる

## ステータス
✅ sorry なし、lake build 通過

## 成果物
- CollatzStoppingTime.lean に追加
