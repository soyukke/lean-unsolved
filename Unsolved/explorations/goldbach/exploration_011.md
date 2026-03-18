# 探索11: IsGoldbach の偶数性

## 目的
IsGoldbach n の偶数性に関する基本定理を証明する。

## 方法

### isGoldbach_odd_has_two
- IsGoldbach n かつ n が奇数ならば、n = 2 + q (q素数) の分解が存在する
- 証明: p, q がともに奇数素数なら p+q は偶数（even_of_odd_prime_add より）、n が奇数と矛盾
- したがって p=2 または q=2 でなければならない
- `Nat.Even.not_odd` と `Nat.odd_iff` を使って矛盾を導出

### isGoldbach_even_ge_four
- IsGoldbach n かつ n が偶数ならば n >= 4
- 証明: p, q は素数なので各々 >= 2、よって p+q >= 4
- omega で即座に証明

## 結果
- `isGoldbach_odd_has_two`: sorry なしで証明完了
- `isGoldbach_even_ge_four`: sorry なしで証明完了

## 考察
- IsGoldbach n が偶数かつ n >= 4 ∨ 奇数かつ n = 2 + (奇数素数) という完全な分類が得られた
- ゴールドバッハ予想は偶数 n > 2 について述べるが、IsGoldbach 自体は奇数にも適用可能
- 奇数の IsGoldbach は必ず 2 を含むという強い制約がある
