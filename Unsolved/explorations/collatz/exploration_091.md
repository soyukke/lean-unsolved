# 探索 091: collatzReaches の帰納的構築戦略 (n ≤ 1000)

## メタデータ
- **キューID**: collatz-095
- **カテゴリ**: 変種/特殊ケース
- **成果レベル**: 中発見
- **日付**: 2026-03-27

## アプローチ
CollatzStoppingTime.leanを精読し、native_decideに頼らないn≤1000の証明戦略を設計。collatzReaches_even_iff, collatzReaches_odd_iff, collatzReaches_pow_two_mul_iffの合成可能性とdecide/native_decideの性能限界を比較分析。

## 発見
- 既にcollatzReaches_le_1000はnative_decide方式で証明済み（CollatzStoppingTime.lean L790-794）
- collatzReaches_le_100000まで分割統治+native_decideで証明済み
- 帰納的合成の根本的限界: 奇数nに対しcollatzReaches_odd_iffは3n+1>nに帰着するため値が増大し直接的帰納法は不可能
- 最適な非native_decide戦略は「奇数核分解+個別ステップ数指定」: n=2^k·m(m奇数)と分解しpow_two_mul_iffでmに帰着、各奇数mについて⟨steps, by decide⟩で証明
- collatzReaches_le_25がnon-native_decideの参考上限（interval_cases+個別定理）

## 仮説
- 奇数核テーブル方式（500個の奇数各々に⟨k, by decide⟩）はnative_decideなしで実用的速度で動作
- Lean 4のelaborate/macroで奇数核テーブルを自動生成するメタプログラミングが最適解

## 行き止まり
- 帰納的合成（偶数→n/2、奇数→3n+1）は値が増大するため直接的帰納法として機能しない
- decide単独で∀n≤1000のcollatzReachesBoundedを評価するのは遅すぎて非実用的
- interval_cases+個別定理名の列挙は1000個手書きは非現実的

## 次のステップ
- Lean 4メタプログラミングで奇数核テーブルを自動生成するタクティック実装
- collatzReachesBounded+decideをチャンク分割(25個ずつ)で速度実測
- collatzReaches_le_25方式をn≤100まで非native_decideで拡張できるか試す
