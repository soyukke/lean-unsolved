# 探索60: v₂(3n+1) の mod 4/8 依存性

## 目的
3n+1 の2進付値 v₂ が n mod 4 および n mod 8 に依存することを形式証明する。

## 主要結果
- n ≡ 3 (mod 4) → v₂(3n+1) = 1（常に）
- n ≡ 1 (mod 4) → v₂(3n+1) ≥ 2
- n ≡ 1 (mod 8) → v₂(3n+1) = 2
- n ≡ 5 (mod 8) → v₂(3n+1) ≥ 3

## Lean定理
- two_dvd_three_mul_add_one
- three_mul_add_one_mod4_of_mod4_eq1/eq3
- three_mul_add_one_div2_odd_of_mod4_eq3
- collatzStep_lt_of_even
