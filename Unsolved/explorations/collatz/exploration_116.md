# 探索 116: Waterfall公式の一般k帰納法証明とconsecutiveAscentsの接続

## メタデータ
- **キューID**: collatz-116
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 中発見
- **形式化価値**: 定理候補
- **関連Leanモジュール**: Collatz.Formula, Collatz.Hensel, Collatz.Structure
- **日付**: 2026-03-29

## アプローチ
既存のmersenne_orbit_mul、syracuse_iter_mul_formula、consecutiveAscentsの3つの形式証明済み結果を起点に、Waterfall公式の直接導出パスと一般hensel_attritionの帰納ステップの代数的構造を解明。

## 発見
- **waterfall_formula**: mersenne_orbit_mulから直接導出可能。2^k*(T^k+1)=3^k*2^m → T^k=3^k*2^{m-k}-1。Nat.eq_of_mul_eq_mul_leftとpow_addで3-5行
- **核心**: consecutiveAscents n k かつ n%2^{k+1}=2^{k+1}-1 のとき、T^k(n)=2*3^k*(q+1)-1
- **一般hensel帰納ステップ**: T^k(n) mod 4 = 3 ⟺ q奇数 ⟺ n%2^{k+2}=2^{k+2}-1
- **waterfall_step**: T(a*2^j-1)=3a*2^{j-1}-1 (a奇数, j≥2)。syracuse_two_pow_sub_oneの真の一般化

## 次のステップ
- waterfall_formulaのLean形式化（mersenne_orbit_mulから3-5行）
- mersenne_consecutive_ascentsの証明
- 一般hensel_attrition_forwardの帰納法実装
