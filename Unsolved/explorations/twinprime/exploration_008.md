# 探索8: Cousin primes (差4) と Sexy primes (差6) の構造

## 目的
双子素数 (差2) の mod 6 構造解析を、他の素数ギャップ（差4: cousin primes、差6: sexy primes）に拡張する。

## Cousin primes (差4) の mod 6 構造

### 定理: cousin_prime_mod_six
p > 3 かつ p, p+4 がともに素数なら p % 6 = 1

### 証明の論理
- prime_gt_three_mod_six より p % 6 ∈ {1, 5}
- p % 6 = 5 の場合: (p+4) % 6 = (5+4) % 6 = 9 % 6 = 3
- 3 | (p+4) かつ p+4 > 7 > 3 なので p+4 は素数でない → 矛盾
- よって p % 6 = 1

### 対比
| 素数ペア | ギャップ | p > 3 のとき p % 6 |
|---------|---------|-------------------|
| Twin (p, p+2) | 2 | 5 |
| Cousin (p, p+4) | 4 | 1 |
| Sexy (p, p+6) | 6 | 1 or 5 |

## Sexy primes (差6) の定義と検証

### 定義: IsSexyPrime
`IsSexyPrime p := Nat.Prime p ∧ Nat.Prime (p + 6)`

### 検証例
- (5, 11), (7, 13), (11, 17), (13, 19), (23, 29)

### mod 6 構造
p + 6 ≡ p (mod 6) なので、p % 6 = 1 なら (p+6) % 6 = 1、p % 6 = 5 なら (p+6) % 6 = 5。
つまり sexy primes では p の mod 6 値に制約がない（1 でも 5 でもよい）。
これは twin/cousin と対照的であり、sexy primes がより「豊富」に存在しうる代数的理由を示す。

## 成果
- `cousin_prime_mod_six` を sorry なしで証明完了
- `IsSexyPrime` の定義と5つの検証例を追加

## 今後の課題
- prime k-tuples 予想との関係
- 各ギャップでの素数ペア密度の比較
