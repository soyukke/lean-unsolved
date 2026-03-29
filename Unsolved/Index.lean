/-!
# 再利用可能な副産物定理カタログ

未解決問題の探索過程で得られた、独立した数学的価値を持つ定理群。
主予想が未証明でも、これらは形式的に検証済みの確定結果である。

## 凡例
- ★★★: 広い応用を持つ基本定理
- ★★: 特定分野で再利用価値が高い
- ★: 問題固有だが教育的・構造的価値がある

---

## 1. p進数論 (2-adic Valuation)
**ファイル**: `Collatz.Defs`, `Collatz.Structure`, `Collatz.Mod`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `v2` | 2-adic付値の再帰的定義 | ★★★ |
| `v2_odd` | 奇数の v2 は 0 | ★★★ |
| `v2_even` | 偶数の v2 は 1 + v2(n/2) | ★★★ |
| `v2_two_mul` | v2(2n) = 1 + v2(n) | ★★★ |

これらは Collatz とは無関係に、2進数論・暗号理論・符号理論で広く使える。

---

## 2. mod 2^k の完全分類手法
**ファイル**: `Collatz.Mod`, `Collatz.Hensel`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `syracuse_behavior_mod8` | Syracuse関数の mod 8 完全分類 | ★★ |
| `v2_of_mod8_eq1/3/5/7` | 各剰余類での v2 の正確な値 | ★★ |
| `single_ascent_mod4` | 1-上昇 ↔ n ≡ 3 (mod 4) | ★★ |
| `double_ascent_mod8` | 2-上昇 ↔ n ≡ 7 (mod 8) | ★★ |
| `triple_ascent_iff_mod16_eq15` | 3-上昇 ↔ n ≡ 15 (mod 16) | ★★ |
| `quadruple_ascent_iff_mod32_eq31` | 4-上昇 ↔ n ≡ 31 (mod 32) | ★★ |

**Hensel Attrition パターン**: k 連続上昇には n ≡ 2^(k+1)-1 (mod 2^(k+1)) が必要。
確率的には 1/2^k の頻度。他の再帰的数論関数の解析にも適用可能。

---

## 3. 乗法的一般公式
**ファイル**: `Collatz.Formula`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `ascentConst_closed` | c_k = 3^k - 2^k (閉形式) | ★★ |
| `syracuse_iter_mul_formula` | 2^k · T^k(n) = 3^k · n + c_k | ★★★ |

除算を回避した乗法的定式化。降下率の理論的解析や他の Collatz 類似問題に転用可能。

---

## 4. Stopping Time 理論
**ファイル**: `Collatz.StoppingTime.Defs`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `stoppingTime_double` | s(2n) = s(n) + 1 | ★★ |
| `stoppingTime_pow_two_mul` | s(2^k·n) = s(n) + k | ★★ |
| `stoppingTime_pow_two'` | s(2^k) = k | ★ |
| `collatzIter_add'` | collatzIter の結合法則 | ★★★ |
| `collatzReaches_trans` | 到達可能性の推移性 | ★★ |

`collatzIter_add'` は軌道論一般で再利用できる基本補題。

---

## 5. サイクル排除
**ファイル**: `Collatz.Cycle`, `Collatz.StoppingTime.Orbit`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `no_collatzStep_fixed_point` | 不動点非存在 (n>0) | ★ |
| `no_collatzStep_two_cycle` | 2-サイクル非存在 | ★ |
| `collatzIter_three_periodic` ~ `seven_periodic` | 3~7-サイクル分類 | ★ |
| `collatzReaches_periodic_trivial` | 周期軌道 = {0,1,2,4} (到達可能性仮定下) | ★★ |
| `no_nontrivial_syracuse_cycle` | 非自明サイクル排除 (Baker公理) | ★★ |

---

## 6. 同値形式の網羅
**ファイル**: `Collatz.StoppingTime.Defs`, `Collatz.StoppingTime.Orbit`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `collatzR_iff_syracuseR` | コラッツ ↔ Syracuse | ★★ |
| `collatzConjectureR_iff_bounded` | コラッツ ↔ 有界ステップ判定 | ★ |
| `collatzConjectureR_iff_eventually_decreases` | コラッツ ↔ 軌道減少性 | ★★ |
| `collatzReaches_iff_enters_cycle` | 到達 ↔ {1,2,4}サイクル進入 | ★ |
| `collatzReaches_of_all_odd` | 奇数で十分 | ★★ |

6つの同値形式を形式証明で結んだ網羅的カタログ。

---

## 7. 5n+1 変種の比較研究
**ファイル**: `Collatz.FiveNPlusOne`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| 非自明サイクル {13,33,83}, {17,27,43} の完全証明 | ★★ |
| 3-サイクル代数的条件 (2^s = 5^k 型) | ★ |
| mod 8 での成長率比較 | ★ |

「なぜ 3n+1 だけ収束するか」の構造的理解。Collatz 変種研究のベンチマーク。

---

## 8. 数値検証
**ファイル**: `Collatz.StoppingTime.Verification`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `collatzReaches_le_1000000` | n ≤ 10^6 の完全検証 | ★ |
| `collatzReachesBounded` | 決定可能な有界判定関数 | ★★ |
| `collatzReaches_of_bounded` / `_complete` | 健全性と完全性 | ★★ |

`collatzReachesBounded` のパターンは他の再帰的問題の有界検証にも転用可能。

---

## 9. Ramsey理論
**ファイル**: `Erdos.Ramsey`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `IsRamseyNumber 3 6` | R(3,3) = 6 | ★★ |

古典的 Ramsey 数の形式証明。

---

## 10. Schur数
**ファイル**: `Schur`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `isSchurNumber_one` | S(1) = 2 | ★ |
| `isSchurNumber_two` | S(2) = 5 | ★★ |

加法的組合せ論の基本定数の完全な形式証明。

---

## 11. Goldbach / Twin Prime
**ファイル**: `Goldbach`, `TwinPrime`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `isGoldbach_double_prime` | 2p は常に Goldbach | ★ |
| `goldbach_implies_weak_goldbach` | 強Goldbach → 弱Goldbach | ★★ |
| `twin_prime_mod_six` | p > 3 の twin prime ⇒ p ≡ 5 (mod 6) | ★ |

---

## 12. Syracuse像の素因子構造
**ファイル**: `Collatz.Structure`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `two_pow_v2_dvd` | 2^v2(m) ∣ m | ★★★ |
| `syracuse_mul_pow_v2` | syracuse(n) * 2^v2(3n+1) = 3n+1 (乗法的分解) | ★★ |
| `syracuse_dvd_odd_prime_iff` | 素数 p ≠ 2 について: p ∣ syracuse(n) ⟺ p ∣ (3n+1) | ★★ |
| `v2_pow_two` | v2(2^m) = m | ★★★ |
| `syracuse_eq_one_iff_pow_two` | syracuse(n) = 1 ⟺ ∃ m, 3n+1 = 2^m | ★★ |
| `three_pow_odd` | 3^m は全て奇数 | ★★ |
| `v2_three_pow_sub_one_odd` | m奇数のとき v2(3^m-1) = 1 (LTE公式) | ★★ |
| `v2_three_pow_add_one_odd` | k奇数のとき v2(3^k+1) = 2 | ★★ |
| `v2_three_pow_add_one_even` | k偶数のとき v2(3^k+1) = 1 | ★★ |
| `syracuse_mod3_eq` | T(n) mod 3 = (v2偶→1, v2奇→2): 3-adic従属性 | ★★ |

Syracuse像の奇素因子は (3n+1) の奇素因子と完全に一致する。
T(n)=1 となる n は (4^k-1)/3 族に限る。

---

## 13. メルセンヌ数のSyracuse反復（Waterfall公式）
**ファイル**: `Collatz.Formula`

| 定理 | 内容 | 再利用性 |
|------|------|----------|
| `syracuse_two_pow_sub_one` | m≥2 で syracuse(2^m-1) = 3·2^{m-1}-1 | ★★ |
| `waterfall_landing_mod4` | 2·3^{m-1}-1 ≡ 1 (mod 4): 帰着後即時下降 | ★ |
| `waterfall_formula` | T^k(2^m-1) = 3^k·2^{m-k}-1 (完全版Waterfall) | ★★★ |
| `waterfall_step` | T(a·2^j-1) = 3a·2^{j-1}-1 (a奇数, j≥2) | ★★★ |

メルセンヌ数の完全閉公式と一般化Waterfall単一ステップ。

---

## 今後形式化の価値が高い方向

1. **d/u > log₂(3) の証明** — コラッツ予想と同値。降下/上昇比の厳密な下界。
2. **v2普遍性定理** — 全奇数dでv2(3n+d)は同一幾何分布（探索114）。
3. **Waterfall公式（一般化）** — T^k(2^m-1)=3^k·2^{m-k}-1 の完全帰納証明。
4. **Baker's theorem の Lean形式化** — 現在公理として導入。Mathlib への貢献可能性。
-/
