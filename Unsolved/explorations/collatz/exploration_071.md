# 探索71: mod 2^k 性質のまとめ + stoppingTime 上界

## 目標
CollatzMod3.lean に mod 2^k 性質の基本定理を追加し、CollatzStoppingTime.lean に 2^k の到達可能性の具体例を追加する。

## 成果

### CollatzMod3.lean への追加

1. **three_mul_add_one_even_ge4**: 奇数 n >= 1 に対して (3n+1) >= 4 かつ偶数
   - omega で一撃
2. **odd_mod4_cases**: 奇数 n に対して n % 4 = 1 または n % 4 = 3
   - omega で一撃

### CollatzStoppingTime.lean への追加

1. **collatzReaches_thirtytwo**: 32 = 2^5 が1に到達
   - collatzReaches_pow_two 5 の適用
2. **collatzReaches_sixtyfour**: 64 = 2^6 が1に到達
   - collatzReaches_pow_two 6 の適用

## 数学的意義

- mod 4 の排中律は、コラッツ関数の1ステップ解析における基本的な場合分けを提供する
- (3n+1) >= 4 は、奇数ステップ後に少なくとも2回の偶数ステップが可能であることの前提条件
- 2^5, 2^6 の到達可能性は collatzReaches_pow_two の直接適用で、具体例の蓄積

## ステータス
✅ 完了（sorry なし）
