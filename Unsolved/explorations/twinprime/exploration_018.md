# 探索18: 素数三つ子の非存在 (p > 3)

## 目標
p > 3 の双子素数 (p, p+2) に対して p+4 が素数でないことを証明し、
素数三つ子 (p, p+2, p+4) が p > 3 では存在しないことを形式化。

## 数学的背景
- p > 3 の双子素数では twin_prime_mod_six により p % 6 = 5
- したがって (p+4) % 6 = 9 % 6 = 3
- よって 3 | (p+4)
- p+4 > 4 > 3 なので、3 で割り切れる p+4 は素数でない
- 唯一の例外は素数三つ子 (3, 5, 7) のみ

## 成果

### TwinPrime.lean への追加

**no_prime_triplet_gt3**: p > 3 の双子素数 (p, p+2) では p+4 は素数でない

証明の構造:
1. twin_prime_mod_six で p % 6 = 5 を取得
2. omega で 3 | (p+4) を導出
3. Nat.Prime.eq_one_or_self_of_dvd で p+4 = 1 or p+4 = 3 に帰着
4. omega で両方とも矛盾（p > 3 より p+4 > 7）

## 技術的ノート
- `⟨(p + 4) / 3, by omega⟩` で 3 の整除性を構成
- p % 6 = 5 から (p+4) % 6 = 3 への推論は omega が処理
- Nat.Prime.eq_one_or_self_of_dvd と omega の組み合わせで完結
