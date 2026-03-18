# 探索9: Cousin prime の mod 30 構造

## 目的
Cousin prime (p, p+4) で p > 5 のとき、p % 30 の取りうる値を特定する。

## 方法
1. cousin_prime_mod_six より p % 6 = 1
2. p % 6 = 1 かつ p % 30 < 30 より、p % 30 ∈ {1, 7, 13, 19, 25}
3. p % 30 = 25 を排除: 25 ≡ 0 (mod 5) なので 5 | p、p > 5 かつ p が素数なので矛盾

## 結果
- `cousin_prime_mod30`: p > 5 の cousin prime (p, p+4) は p % 30 ∈ {1, 7, 13, 19}
- sorry なしで証明完了

## 考察
- Twin prime の mod 30 構造と対比:
  - Twin (p, p+2): p % 30 ∈ {11, 17, 29} (3個)
  - Cousin (p, p+4): p % 30 ∈ {1, 7, 13, 19} (4個)
- Cousin prime の方が剰余類が1つ多い
- Twin prime では p%30=5 と p%30=23 の2つを排除、Cousin では p%30=25 の1つのみ排除
- 30個の剰余類のうち cousin prime の p は4個（13.3%）
