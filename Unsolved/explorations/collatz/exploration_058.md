# 探索58: 最小反例の mod 32 制約のLean形式化

**日付**: 2026-03-18
**成果物**: `Unsolved/CollatzMinimal.lean`（拡張）
**ステータス**: ✅完了（sorry なし、ビルド成功）

## 目的

最小反例の mod 制約を mod 32 に拡大し、Lean 4 で形式化する。

## 新しい定理（sorry なし）

### n ≡ 11 (mod 32) の排除
```
theorem minimal_counterexample_not_mod32_eq11
```
- T(n) = 48q+17 (mod 8 ≡ 1)
- T²(n) = 36q+13 (mod 4 ≡ 1)
- T³(n) ≤ 27q+10 < 32q+11 = n
- 3段の ¬reachesOne 伝播と最小性の矛盾

### n ≡ 23 (mod 32) の排除
```
theorem minimal_counterexample_not_mod32_eq23
```
- T(n) = 48q+35 (mod 4 ≡ 3, 上昇)
- T²(n) = 72q+53 (mod 8 ≡ 5)
- T³(n) ≤ 27q+20 < 32q+23 = n
- 3段の ¬reachesOne 伝播と最小性の矛盾

## 累積結果

最小反例は以下を全て満たす:
- n > 1
- n は奇数
- n ≡ 3 (mod 4)
- n ≢ 3 (mod 16)
- n ≢ 11 (mod 32) ★NEW
- n ≢ 23 (mod 32) ★NEW

mod 32 で排除できる剰余類: 3, 11, 19, 23 (mod 4 ≡ 3 の8個中4個 = 50%)
残り: 7, 15, 27, 31 (mod 32) — これらは mod 64 以上の解析が必要

## 技術的ノート

- `omega` は `syracuse` 関数を含む式を直接扱えない
- `syracuse_pos` 補題で正値性を確保
- 各ケースで 3回の Syracuse 適用が必要（mod 16 証明の 2回から増加）
