# 探索43: T(n) mod 3 不変量

## 目的
コラッツステップにおける mod 3 の振る舞いを形式化する。

## 主要結果
- 奇数 n に対して (3n+1) % 3 = 1 が常に成立
- 偶数ステップの mod 3 解析（mod 6 による分類）

## Lean定理
- `three_mul_add_one_mod3`: 任意の n に対して (3n+1) % 3 = 1
- `three_mul_add_one_not_mul3`: (3n+1) は 3 の倍数でない
- `collatzStep_odd_result_mod3`: 奇数 n の collatzStep の mod 3 = 1
- `collatzStep_even_mod6_eq0/eq2/eq4`: 偶数ステップの mod 6 分類
- `collatz_odd_step_mod3_invariant`: 3 の倍数でない奇数 n → collatzStep(n) % 3 = 1

## 数学的背景
3n+1 操作は mod 3 で常に 1 を生成する:
- n % 3 = 0: 3n+1 ≡ 1 (mod 3)
- n % 3 = 1: 3n+1 ≡ 4 ≡ 1 (mod 3)
- n % 3 = 2: 3n+1 ≡ 7 ≡ 1 (mod 3)

## 所見
3n+1 操作は mod 3 で常に 1 を生成する。これにより、コラッツ軌道の mod 3 値は
{1, 2} 内にとどまる（0 にはならない、ただし 3 の倍数から始めない限り）。
偶数ステップ（n/2）は mod 3 を変化させうるが、mod 6 で完全に分類できる。

既存の `syracuse_not_div_three` (CollatzStructure.lean) と合わせて、
Syracuse 関数の値が 3 の倍数にならないことの完全な理解が得られた。
