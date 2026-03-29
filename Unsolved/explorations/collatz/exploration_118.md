# 探索 118: 一般化Hensel帰納法の設計

## メタデータ
- **キューID**: collatz-126
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 中発見
- **形式化価値**: 定理候補
- **関連Leanモジュール**: Collatz.Formula, Collatz.Hensel, Collatz.Structure
- **日付**: 2026-03-29

## アプローチ
k=1..4の個別証明とSyracuse反復の乗法公式を基盤に、一般kに対する帰納法証明を完全設計。k=0..8で512奇数の全数検証。

## 発見
- **帰納ステップ核心**: n%2^{k+1}=2^{k+1}-1のとき n+1=2^{k+1}*m、T^k(n)+1=2*3^k*m
- **T^k(n) mod 4の判定**: 2*3^k*m mod 4 = 2*m mod 4（3^kの奇数性）。m偶数→mod4=3(上昇継続)、m奇数→mod4=1(停止)
- **m偶奇⟺n mod 2^{k+2}**: m偶数⟺2^{k+2}|(n+1)⟺n%2^{k+2}=2^{k+2}-1
- Lean実装: Lemma A(mod_pow_weaken 5-10行) + Lemma B(iter_mod4 50-80行) + 主定理(30-50行) = 合計100-150行

## 次のステップ
- Lemma B(iter_mod4_from_alt_formula)をLean実装
- 主定理hensel_general をNat.strongRecOnで実装
