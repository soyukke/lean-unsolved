# Erdős #52 和積問題 探索インデックス

## 概要
- **予想**: 任意の有限集合 A ⊂ ℤ に対し max(|A+A|, |A·A|) ≥ c|A|^{2-ε}
- **Leanファイル**: `Unsolved/ErdosSumProduct.lean`（sorry なし）

## 探索記録

| # | テーマ | スクリプト | 主要発見 |
|---|--------|-----------|---------|
| 1-3 | 基本計算、特殊集合分析 | `scripts/erdos52_sum_product.py`, `erdos52_special_sets.py` | smooth numbers が比率を最も抑える |
| 4 | 有限体 F_p 上の和積現象 | `scripts/erdos52_finite_field.py` | 部分群で|A*A|=|A|だが|A+A|大、ε≈0.37-0.47 |
| 5 | 加法/乗法エネルギー分析 | `scripts/erdos52_energy.py` | BSG型関係 E·E*≥|A|^4 全例で成立、トレードオフ確認 |
| 6 | |A·A|≥|A| の形式証明 | `scripts/erdos52_plunnecke.py` | productset下界とPlunnecke-Ruzsa数値検証 |
| 7 | sumset/prodset の単調性・上界 | — | mono補題と|A+A|,|A*A|≤|A|^2をLeanで証明 |
| 8 | シングルトンのsumset/prodset | — | sumset({a})={2a}, prodset({a})={a²}, {1,2}の計算例 |
| 9 | 2元集合の和積比較 | — | {1,3},{2,3}でsumset/prodsetともにcard=3を検証 |
| 10 | A={1,...,n}のsumsetカード=2n-1 | — | {1,2,3,4}でsumset card=7, prodset card=9を検証 |
| 11 | 3元集合の和積（等比的集合） | — | {1,2,4}: sumset card=6, prodset card=5（等比的集合は積集合が小さい） |

## 主要発見

### 探索4: 有限体上の和積
- F_p 上の乗法的部分群 H: |H*H|=|H| だが |H+H| ≈ min(p, 2|H|+) と大きい
- BKT型下界 max(|A+A|,|A*A|) ≥ |A|^{1+ε}: 全例で成立
- ε の最小値: |A|=3で ε≈0.465、|A|=5で ε≈0.365-0.43
- 最小化する集合: {1,x,p-x}型（部分群的構造）が多い
- |A| ≈ p^{0.7} 付近で ε が最小（≈0.39）

### 探索5: エネルギー分析
- 区間{1,...,n}: E(A)/n³≈0.67（加法構造化）、E*(A)/n³≈0.28（乗法は弱い）
- 等比数列: 逆パターン（E*/n³≈0.67、E/n³≈0.19）
- smooth numbers: 両エネルギーがやや高い → 和積の「敵」
- BSG型関係 E(A)·E*(A) ≥ |A|^4: 全15ケースで成立（比率6.1〜19.6）
- Cauchy-Schwarz下界は実際値の67-76%とかなりタイト
- 結論: 加法と乗法が同時に退化できない → 和積予想の本質
