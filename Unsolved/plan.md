# コラッツ予想 探索記録

## フェーズ1: 問題の理解と再定式化

### 探索1: 現状の把握

**Mathlibの状況:**
- Mathlib自体にCollatzの形式化は**存在しない**
- 使える道具: `Function.iterate`, `StateTransition`, `WellFounded`, `Dynamics.FixedPoints`

**既存のLean形式化:**
- [syracuse-confinement](https://github.com/johnjanik/syracuse-confinement) — 12,947行、核心部分はまだsorry
- [formal-conjectures (Google DeepMind)](https://github.com/google-deepmind/formal-conjectures) — 問題文のみ

### 探索2: 再定式化の候補
1. Syracuse関数 T(n) = (3n+1)/2^v₂(3n+1) ✅ 採用・形式化済み
2. 2-adic数での解析
3. コラッツグラフの木構造
4. 確率的モデル（各サイクルで平均3/4倍）

## フェーズ2: 小さいケースの網羅的探索

### 探索3: 数値実験 (scripts/collatz_explore.py)
- n=871 が1〜1000で最大stopping time (178ステップ)
- v2(3n+1) の分布は理論予測 P(v2=k) = 1/2^k と完全一致（幾何分布）
- mod 12 で r=7 が最大停止時間

### 探索4: Syracuse関数のLean形式化 (Collatz.lean)
- v2（2-adic付値）、syracuse、syracuseIter を定義
- syracuse 1 = 1（不動点）、syracuse 3 = 5、syracuse 5 = 1 等を検証
- ✅ ビルド成功

## フェーズ3: 構造の発見

### 探索5: 構造解析 (scripts/collatz_structure.py)
- **mod 4 が軌道の上昇/下降を完全に決定する**
  - n ≡ 1 (mod 4) → 即座に下降
  - n ≡ 3 (mod 4) → 必ず上昇、上昇後は50:50でmod 4が分岐
- 逆コラッツ木の成長率は2に漸近
- trailing 1-bits と停止時間に正の相関

### 探索6: CollatzStructure.lean
- collatzStep_odd_gives_even, collatz_cycle_1_4_2 等を証明
- v2_three_mul_add_one_of_mod4_eq3 (n≡3 mod 4 → v2=1)
- collatzStep_even_lt (偶数n≥2なら下降)
- ✅ ビルド成功、sorry なし

## フェーズ4: 形式化と証明

### 探索7: ビットパターン遷移 (scripts/collatz_bit_transition.py)
- **末尾ビットパターンがv2を完全決定**: ...11→v2=1, ...001→v2=2, ...1101→v2=3
- n ≡ 3 (mod 8) → T(n) ≡ 1 (mod 4) 100% → 次で必ず下降
- n ≡ 7 (mod 8) → T(n) ≡ 3 (mod 4) 100% → もう一度上昇
- 連続上昇回数 = 末尾連続1ビット数 → 幾何分布 (1/2)^k
- マルコフ連鎖の定常分布はほぼ一様、混合が速い

### 探索8: 下降補題のLean証明 (CollatzStructure.lean)
- ✅ `v2_ge_two_of_mod4_eq1`: n≡1(mod 4) → v2(3n+1) ≥ 2
- ✅ `syracuse_lt_of_mod4_eq1`: n≡1(mod 4), n>1 → T(n) < n **← 核心的下降補題**
- ✅ `syracuse_mod4_eq3`: n≡3(mod 4) → T(n) = (3n+1)/2
- ✅ `syracuse_gt_of_mod4_eq3`: n≡3(mod 4) → T(n) > n
- ✅ ビルド成功、sorry なし

## 現在の理解

**コラッツの本質**: 各奇数nに対して
- n ≡ 1 (mod 4): 下降確定（T(n) < n）
- n ≡ 3 (mod 4): 上昇確定（T(n) > n）、上昇後は50:50で分岐

連続上昇回数は末尾1ビット数で決まり幾何分布。平均で各サイクルは 3/4 倍に縮小。
**未解決の壁**: 「全ての整数で有限回で1に到達する」ことの証明。確率的には成り立つが決定論的証明がない。

## 次にやること
- [ ] 2ステップ下降の形式化: n≡3(mod 8) → T(T(n)) < T(n) < ... → 2ステップで下降
- [ ] 「上昇+下降」の1サイクルでの縮小率の形式化
- [ ] Tao (2022) のアプローチ調査: 対数密度での「ほぼ全て」の証明手法
