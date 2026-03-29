# 探索 117: v2(3^m-1)のLTE公式

## メタデータ
- **キューID**: collatz-117
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 中発見
- **形式化価値**: 定理候補
- **関連Leanモジュール**: Collatz.Defs, Collatz.Structure, Mathlib.Data.Nat.PadicVal
- **日付**: 2026-03-29

## アプローチ
LTE補題を3^m-1に適用しv2の閉形式を導出。m=1-10000で数値検証。MathlibのpadicValNat.pow_two_sub_oneとの接続も確認。

## 発見
- **定理1**: m奇数(m≥1)→v2(3^m-1)=1。証明: 3≡-1(mod4)→3^m≡3(mod4)→3^m-1≡2(mod4)
- **定理2**: m偶数(m≥2)→v2(3^m-1)=2+v2(m)。証明: LTE(p=2)でv2(3-1)+v2(3+1)+v2(m)-1=1+2+v2(m)-1
- **副産物**: v2(3^k+1)=2(k奇数), 1(k偶数)
- **副産物**: ascentConst(k)=3^k-2^kは全k≥1で奇数(v2=0)
- Mathlibにpadicvalnat.pow_two_sub_oneが存在。v2=padicValNat 2の橋渡しのみ必要

## 次のステップ
- v2=padicValNat 2の等価性補題をLean形式化
- v2(3^m-1)公式のLean形式化（因数分解ルートまたはLTEルート）
