# コラッツ予想 探索インデックス

各探索の詳細は個別ファイルに記録。ステータス: ✅完了 🔬進行中 ❌失敗/放棄

## フェーズ1: 問題の理解と再定式化

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 1 | Mathlib/既存形式化の調査 | ✅ | - | Mathlibにcollatzなし。syracuse-confinement(sorry残)あり |
| 2 | 再定式化の候補 | ✅ | - | Syracuse関数 T(n)=(3n+1)/2^v2 を採用 |

## フェーズ2: 小さいケースの探索

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 3 | 数値実験 | ✅ | scripts/collatz_explore.py | v2分布=幾何分布, n=871が最大stopping time |
| 4 | Syracuse Lean形式化 | ✅ | Collatz.lean | v2, syracuse, syracuseIter定義 |

## フェーズ3: 構造の発見

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 5 | 構造解析 | ✅ | scripts/collatz_structure.py | mod 4が上昇/下降を決定 |
| 6 | 基本補題群 | ✅ | CollatzStructure.lean | even/odd step, 4→2→1 cycle |
| 7 | ビットパターン遷移 | ✅ | scripts/collatz_bit_transition.py | 末尾ビット→v2完全決定 |
| 8 | 下降補題 | ✅ | CollatzStructure.lean | n≡1(mod4)→T(n)<n ★核心 |
| 9 | 2ステップ下降 | ✅ | CollatzStructure.lean | n≡3(mod8)→T²(n)<T(n) |

## フェーズ4: 形式化と証明

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 10 | Taoアプローチ調査 | ✅ | - | 対数密度, 特性関数減衰. Lean形式化は困難 |
| 11 | mod 8完全分類 | ✅ | CollatzMod.lean | v2=2,1,≥3,1 for r=1,3,5,7 |
| 12 | サイクル排除 | ✅ | CollatzCycle.lean | 3^a=2^b→a=b=0, Baker公理 |
| 13 | Hensel attrition | ✅ | CollatzHensel.lean | k回上昇⟺n≡2^{k+1}-1, k=1..4 |
| 14 | 加速Syracuse | ✅ | CollatzAccel.lean | 上界(9n+5)/8等, firstDescent |
| 15 | 大規模解析+一般k調査 | ✅ | scripts/collatz_accel.py | 平均縮小0.985, trailing 1-bits決定的 |
| 16 | ★一般公式 | ✅ | CollatzFormula.lean | 2^k·T^k=3^k·n+(3^k-2^k) ★重要 |
| 17 | 逆コラッツ木 | ✅ | scripts/collatz_inverse_tree.py | 成長率≈4/3, カバー率調査 |
| 18 | 完全サイクル公式 | ✅ | CollatzFormula.lean | 4·2^k·T^{k+1}+2^{k+1}≤3^{k+1}(n+1) |
| 19 | 対数ポテンシャル | ✅ | scripts/collatz_potential.py | Var[delta]=2, 最良ポテンシャル83.5%減少 |

## フェーズ5: 並列力技探索

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 20 | 3進表現 | ✅ | scripts/collatz_ternary.py | ★s3(n)mod2が不変量! T(n)≢0(mod3) |
| 21 | 力学系 | ✅ | scripts/collatz_dynamics.py | ★v2列はマルコフ依存! 全nでλ<0 |
| 22 | 代数的 | ✅ | scripts/collatz_algebraic.py | 葉=3の倍数, σ/log(n)≈3.75 |
| 23 | 制約充足 | ✅ | scripts/collatz_constraint.py | 4^L-3^Lは常に奇数, L≤68でサイクルなし |

## フェーズ6: 深堀り検証

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 24 | s3 mod 2 不変性検証 | ❌自明 | scripts/collatz_s3_invariant.py | s3(n)≡n(mod2)は恒等式。情報量ゼロ |
| 25 | v2マルコフ依存検証 | ❌バイアス | scripts/collatz_v2_markov.py | 一様分布下ではv2列は完全独立。軌道の非一様性が原因 |

## フェーズ7: 第2ラウンド力技探索

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 26 | 周波数領域解析 | ✅ | scripts/collatz_wavelets.py | s(2n)=s(n)+1常成立, パワースペクトル2冪周期, 自己相似 |
| 27 | グラフ理論 | ✅ | scripts/collatz_graph_theory.py | SCC={1}のみ, 葉41.7%, ハブmod3均等 |
| 28 | 連分数 | ✅ | scripts/collatz_continued_fraction.py | ★d/u>log₂(3)が常に成立(調査範囲), 2^a·3^b-1型は長st |
| 29 | 数論的壁 | ✅ | scripts/collatz_number_wall.py | 壁は全てmod4≡3, 2進1密度0.75 |

## フェーズ9: Stopping Time の深堀り

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 42 | StoppingTime追加補題 | ✅ | CollatzStoppingTime.lean | s(4n)=s(n)+2, s(8n)=s(n)+3, 2^k·n到達⟺n到達, s(2^k)=k, collatzIter合成律 |

## フェーズ10: 解析的手法

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 52 | IFS(反復関数系)解析 | ✅ | scripts/collatz_ifs.py | 臨界確率p_c≈0.369, 実軌道λ≈-0.147≈λ(0.5), BC次元≈0.71, 全軌道でλ<0 |
| 53 | 形式的冪級数の有理性テスト | ✅ | scripts/collatz_generating_function.py | 生成関数の過渡部分は非有理、Z変換の極が全て単位円内(|z|≈0.93)、支配的極に普遍性 |

## フェーズ11: 大規模並列探索 (探索42-55)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 42 | 大規模d/u最小値 | ✅ | scripts/collatz_du_large.py | 10^7まで全奇数でd/u>log₂(3), 差分縮小は減速 | B |
| 43 | 行列表現 | ✅ | scripts/collatz_matrix.py | Aff(Q)ランダムウォーク, リアプノフ指数全て負 | B |
| 44 | 2-adic解析 | ✅ | scripts/collatz_padic.py | ★Lipschitz反復不変性, 不動点は1のみ | A |
| 45 | SAT制約探索 | ✅ | scripts/collatz_sat.py | ★k≤9,k≥13で全排除, k=10-12のみ窓 | A |
| 46 | v2独立性 | ✅ | scripts/collatz_v2_independence.py | ★v2依存はビット共有由来, 正の相関は予想に有利 | A |
| 47 | 転送作用素 | ✅ | scripts/collatz_transfer_operator.py | ★★E[v₂]=2.0(k≤9), 全kでE[v₂]>log₂(3) | S |
| 48 | 3n+d変種比較 | ✅ | scripts/collatz_variants.py | ★a=3→4の鋭い相転移, v2分布の普遍性 | A |
| 49 | 逆木密度 | ✅ | scripts/collatz_inverse_density.py | 成長率4/3確認, 定数2.69 | B |
| 50 | ビットエントロピー | ✅ | scripts/collatz_bit_entropy.py | ★ビット長連続増加≤2ステップ | A |
| 51 | delay record | ✅ | scripts/collatz_delay_records.py | 成長定数≈4/3, 末尾1-bits | B |
| 52 | IFS | ✅ | scripts/collatz_ifs.py | 全軌道でリアプノフ指数負 | B |
| 53 | 生成関数 | ✅ | scripts/collatz_generating_function.py | ★Z変換極が全て単位円内 | A |
| 54 | Rauzy fractal | ✅ | scripts/collatz_rauzy.py | U頻度≈log₂(3)-1, 冗長度74% | B |
| 55 | パターンマイニング | ✅ | scripts/collatz_pattern_mining.py | carry chain平均長2.0 | B |
| 65 | 小さい値の到達可能性 | ✅ | CollatzStoppingTime.lean | collatzReaches 5,6,7 を decide で証明 | B |
| 66 | mod 2^k 完全分類まとめ + 到達可能性拡張 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | mod 16 分類追加, collatzReaches 8,9,10 | B |
| 67 | collatzReaches の合成性質 | ✅ | CollatzStoppingTime.lean | collatzReaches_even_iff: 偶数nの到達⟺n/2の到達 | B |
| 68 | collatzReaches の奇数版 | ✅ | CollatzStoppingTime.lean | collatzReaches_odd_iff: 奇数n>1の到達⟺3n+1の到達 | B |
| 69 | 増減まとめ + collatzReaches 合成 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | (3n+1)/2≤2n, collatzReaches 13,15,16 | B |
| 70 | collatzReaches の偶数合成と具体例 | ✅ | CollatzStoppingTime.lean | collatzReaches_of_half, collatzReaches 20 | B |
| 71 | mod 2^k 性質まとめ + stoppingTime 上界 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | (3n+1)≥4∧偶数, mod4排中律, collatzReaches 32,64 | B |
| 72 | 3ステップ合成 + collatzReaches 100 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | 3n+1>n+1, (3n+1)/4 mod4, collatzReaches 100 | B |
| 75 | mod 6 完全分類 + 奇数到達性 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | ★(3n+1)%6=4 (奇数n), collatzReaches 17,19,21 | B |
| 76 | mod 12 分類 + 奇数到達性拡張 | ✅ | CollatzMod3.lean, CollatzStoppingTime.lean | ★(3n+1)%12∈{4,10}, collatzReaches 23,25 | B |

## フェーズ12: 深堀り (探索56-59)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 56 | E[v₂]=2の証明 | ✅ | scripts/collatz_ev2_proof.py | v2=2滞在率25%, 幾何分布メカニズム | A |
| 57 | k=10-12拡大周期 | ✅ | scripts/collatz_expansion_window.py | 大偏差レートI=0.055で消滅を説明 | A |
| 58 | mod32 Lean形式化 | ✅ | CollatzMinimal.lean拡張 | ★mod32≡11,23排除(sorry無し) | S |
| 59 | v2分布の厳密証明 | ✅ | scripts/collatz_v2_distribution_proof.py | ★★P(v2=j)=1/2^j厳密証明, E[v₂]=2.0 | S |

## フェーズ13: 集約テスト探索 (探索030-034)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 30 | mod 16下降率統計 | ✅ | exploration_030.md | mod 16で残余4,12が最高下降率0.62 | B |
| 31 | 2-adic評価パターン | ✅ | exploration_031.md | ★v2(3n+1)はn mod 8で完全決定 | A |
| 32 | 停止時間生成関数 | ✅ | exploration_032.md | 自然境界で解析接続不可。行き止まり | C |
| 33 | コラッツグラフRamsey性質 | ✅ | exploration_033.md | 長さ5以上の単調増加列は必ず存在 | B |
| 34 | ランダムモデル収束速度 | ✅ | exploration_034.md | O(1/√n)収束、Terrasと一致 | B |

## 未着手の方向

| 方向 | 概要 | 優先度 |
|------|------|--------|
| ★d/u > log₂(3) の証明 | 証明できればコラッツと同値 | ★★★ |
| T(n) ≢ 0 (mod 3) のLean証明 | 形式化は容易そう | ★★ |
| ~~s(2n) = s(n) + 1 のLean証明~~ | ✅探索36で完了、探索42で拡張 | ~~★★~~ |
| Syracuseが奇数mod2^K上の全単射 | v2独立性の形式証明 | ★★ |
| 逆コラッツ木の全整数包含の形式化 | 予想と同値な言い換え | ★★ |
| 一般k Hensel帰納法 | 技術的に可能だが大労力 | ★ |

## やってはいけないこと（失敗/行き止まり）

- `omega` で一般の 2^k を含む式を解こうとする → 使えない
- 個別サイクルでの縮小証明 → 9/8倍等で拡大するケースがある
- mod M でSyracuse写像を well-defined にしようとする → v2が可変で不可能
- `native_decide` の使用 → mathlibのlinterが禁止
- s3(n) mod 2 を不変量として使おうとする → 自明（s3(n) ≡ n mod 2）
- v2列のマルコフ依存を証明しようとする → 一様分布下では完全独立。軌道上の偏りは選択バイアス
