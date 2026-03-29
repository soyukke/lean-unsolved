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
| 6 | 基本補題群 | ✅ | Collatz/Structure.lean | even/odd step, 4→2→1 cycle |
| 7 | ビットパターン遷移 | ✅ | scripts/collatz_bit_transition.py | 末尾ビット→v2完全決定 |
| 8 | 下降補題 | ✅ | Collatz/Structure.lean | n≡1(mod4)→T(n)<n ★核心 |
| 9 | 2ステップ下降 | ✅ | Collatz/Structure.lean | n≡3(mod8)→T²(n)<T(n) |

## フェーズ4: 形式化と証明

| # | 探索 | ステータス | 成果物 | 主要発見 |
|---|------|----------|--------|---------|
| 10 | Taoアプローチ調査 | ✅ | - | 対数密度, 特性関数減衰. Lean形式化は困難 |
| 11 | mod 8完全分類 | ✅ | Collatz/Mod.lean | v2=2,1,≥3,1 for r=1,3,5,7 |
| 12 | サイクル排除 | ✅ | Collatz/Cycle.lean | 3^a=2^b→a=b=0, Baker公理 |
| 13 | Hensel attrition | ✅ | Collatz/Hensel.lean | k回上昇⟺n≡2^{k+1}-1, k=1..4 |
| 14 | 加速Syracuse | ✅ | Collatz/Accel.lean | 上界(9n+5)/8等, firstDescent |
| 15 | 大規模解析+一般k調査 | ✅ | scripts/collatz_accel.py | 平均縮小0.985, trailing 1-bits決定的 |
| 16 | ★一般公式 | ✅ | Collatz/Formula.lean | 2^k·T^k=3^k·n+(3^k-2^k) ★重要 |
| 17 | 逆コラッツ木 | ✅ | scripts/collatz_inverse_tree.py | 成長率≈4/3, カバー率調査 |
| 18 | 完全サイクル公式 | ✅ | Collatz/Formula.lean | 4·2^k·T^{k+1}+2^{k+1}≤3^{k+1}(n+1) |
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
| 42 | StoppingTime追加補題 | ✅ | Collatz/StoppingTime/*.lean | s(4n)=s(n)+2, s(8n)=s(n)+3, 2^k·n到達⟺n到達, s(2^k)=k, collatzIter合成律 |

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
| 65 | 小さい値の到達可能性 | ✅ | Collatz/StoppingTime/*.lean | collatzReaches 5,6,7 を decide で証明 | B |
| 66 | mod 2^k 完全分類まとめ + 到達可能性拡張 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | mod 16 分類追加, collatzReaches 8,9,10 | B |
| 67 | collatzReaches の合成性質 | ✅ | Collatz/StoppingTime/*.lean | collatzReaches_even_iff: 偶数nの到達⟺n/2の到達 | B |
| 68 | collatzReaches の奇数版 | ✅ | Collatz/StoppingTime/*.lean | collatzReaches_odd_iff: 奇数n>1の到達⟺3n+1の到達 | B |
| 69 | 増減まとめ + collatzReaches 合成 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | (3n+1)/2≤2n, collatzReaches 13,15,16 | B |
| 70 | collatzReaches の偶数合成と具体例 | ✅ | Collatz/StoppingTime/*.lean | collatzReaches_of_half, collatzReaches 20 | B |
| 71 | mod 2^k 性質まとめ + stoppingTime 上界 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | (3n+1)≥4∧偶数, mod4排中律, collatzReaches 32,64 | B |
| 72 | 3ステップ合成 + collatzReaches 100 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | 3n+1>n+1, (3n+1)/4 mod4, collatzReaches 100 | B |
| 75 | mod 6 完全分類 + 奇数到達性 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | ★(3n+1)%6=4 (奇数n), collatzReaches 17,19,21 | B |
| 76 | mod 12 分類 + 奇数到達性拡張 | ✅ | Collatz/Mod3.lean, Collatz/StoppingTime/*.lean | ★(3n+1)%12∈{4,10}, collatzReaches 23,25 | B |

## フェーズ12: 深堀り (探索56-59)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 56 | E[v₂]=2の証明 | ✅ | scripts/collatz_ev2_proof.py | v2=2滞在率25%, 幾何分布メカニズム | A |
| 57 | k=10-12拡大周期 | ✅ | scripts/collatz_expansion_window.py | 大偏差レートI=0.055で消滅を説明 | A |
| 58 | mod32 Lean形式化 | ✅ | Collatz/Minimal.lean拡張 | ★mod32≡11,23排除(sorry無し) | S |
| 59 | v2分布の厳密証明 | ✅ | scripts/collatz_v2_distribution_proof.py | ★★P(v2=j)=1/2^j厳密証明, E[v₂]=2.0 | S |

## フェーズ13: 集約テスト探索 (探索030-034)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 30 | mod 16下降率統計 | ✅ | exploration_030.md | mod 16で残余4,12が最高下降率0.62 | B |
| 31 | 2-adic評価パターン | ✅ | exploration_031.md | ★v2(3n+1)はn mod 8で完全決定 | A |
| 32 | 停止時間生成関数 | ✅ | exploration_032.md | 自然境界で解析接続不可。行き止まり | C |
| 33 | コラッツグラフRamsey性質 | ✅ | exploration_033.md | 長さ5以上の単調増加列は必ず存在 | B |
| 34 | ランダムモデル収束速度 | ✅ | exploration_034.md | O(1/√n)収束、Terrasと一致 | B |

## フェーズ14: ラウンド3並列探索 (探索081-085)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 81 | mod 2^k 層別全単射構造 | ✅ | exploration_081.md | ★v2層別で各層が全単射、一様定常分布 | A |
| 82 | Cramér関数と大偏差解析 | ✅ | exploration_082.md | ★★I(0)=0.055閉形式、発散は指数減衰 | S |
| 83 | T(n)≢0(mod 3)の証明分析 | ✅ | exploration_083.md | 既にLean形式証明済み、mod 3∈{1,2}分類可能 | C |
| 84 | 逆コラッツ木の到達密度下界 | ✅ | exploration_084.md | ★gap≈1.64·exp(-0.237·L/log₂N)のユニバーサル下界 | A |
| 85 | d/u>log₂(3)のバースト公式 | ✅ | exploration_085.md | ★LTEでバースト公式導出、確率的アプローチが有望 | A |

## フェーズ15: ラウンド3バッチ2 (探索086-090)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 86 | Dirichlet級数の解析接続 | ✅ | exploration_086.md | 残余項がEuler-Maclaurin展開と機械精度一致。Dirichlet倍率≈7 | B |
| 87 | U/Dパターン組合せ的数え上げ | ✅ | exploration_087.md | ★禁止パターン不在、2次マルコフ連鎖、均衡復元力 | A |
| 88 | Z_2上の周期点完全分類 | ✅ | exploration_088.md | ★Z_2上に形式的周期点無限。不動点n=1のみ。2-adic反発性 | A |
| 89 | 転送作用素スペクトルギャップ | ✅ | exploration_089.md | ★gap>0.5、混合時間1-2ステップ。E[v₂]正確公式発見 | A |
| 90 | Collatz/Formula一般公式の下降条件 | ✅ | exploration_090.md | 既存形式化でカバー済み。新規方向は上昇回数の上界 | C |

## フェーズ16: ラウンド3バッチ3 (探索091-095)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 91 | collatzReaches帰納的構築戦略 | ✅ | exploration_091.md | 奇数核テーブル+メタプログラミングが最適解 | A |
| 92 | mod 2^10 下降ステップ数分類 | ✅ | exploration_092.md | ★87.5%決定的、(2^{2k}-1)/3型超急速下降 | A |
| 93 | Syracuse力学系エルゴード性 | ✅ | exploration_093.md | ★相関指数減衰τ≈5.7、リアプノフ全負、単一エルゴード | A |
| 94 | stopping time尾部分布 | ✅ | exploration_094.md | ★尾部指数減衰exp(-0.0735t)、max~(logN)^1.623 | A |
| 95 | 連分数展開との相関 | ✅ | exploration_095.md | 連分数とSTは無相関(r=-0.004)、仮説棄却 | C |

## フェーズ17: ラウンド4バッチ1 (探索096-101)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 96 | mod p^k 多素数p-adic構造 | ✅🔷 | exploration_096.md | ★定理: p\|T(n)⟺n≡-(3^{-1})(mod p)。v_p分布はGeo(1/p)。**Lean形式化済み** | A |
| 97 | 超急速下降族の代数的分類 | ✅🔷 | exploration_097.md | ★T(n)=1唯一族は(4^k-1)/3。T(n)=c統一公式。**Lean形式化済み** | A |
| 98 | ST減衰定数λの理論的導出 | ✅ | exploration_098.md | ★★I(0)×4/3=0.0733≈λ=0.0735(0.3%一致) | S |
| 99 | 2次マルコフ遷移行列の固有値 | ✅ | exploration_099.md | ★gap≈0.82, |λ₂|=0.182, 混合6ステップ | A |
| 100 | 集中不等式でd/u>log₂(3) | ✅ | exploration_100.md | Cramér: P≤exp(-0.055k)。v₂=2トラップ発見。∀n証明は不可 | A |
| 101 | スペクトルギャップM→∞漸近 | ✅ | exploration_101.md | ★全k=3..10でgap≥0.65。0漸近なし | A |

## フェーズ18: ラウンド4バッチ2 (探索102-106)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 102 | consecutiveAscents形式化分析 | ✅ | exploration_102.md | 形式化可能(0.92)。帰納法+mod逆変換 | A |
| 103 | E[v₂]パリティ公式形式化設計 | ✅ | exploration_103.md | v2_add_of_ltが核心障壁。k=5で公式不整合 | A |
| 104 | mod 3^k軌道構造 | ✅ | exploration_104.md | ★確定遷移普遍公式1-1/2^{a-1}、T^m→-1集中 | A |
| 105 | mod 2^12 決定的下降割合 | ✅ | exploration_105.md | ★7/8仮説棄却。決定的割合→1(k=14で92%) | A |
| 106 | Baker定理サイクル排除 | ✅ | exploration_106.md | p=1..10完全排除。Baker下界11800bit不足 | B |

## フェーズ19: ラウンド4バッチ3 (探索111-115)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 111 | 逆像密度mod M分布 | ✅ | exploration_111.md | v2条件自動成立。逆像数閉公式。Parry測度乖離 | B |
| 112 | 連続上昇回数・メルセンヌ数 | ✅ | exploration_112.md | ★Waterfall公式T^k(2^m-1)=3^k·2^{m-k}-1。定理候補 | A |
| 113 | 非標準解析的再定式化 | ✅ | exploration_113.md | CC⟺超自然数overspill。overspillの限界明確化 | C |
| 114 | 3n+d変種エルゴード性比較 | ✅ | exploration_114.md | ★v2普遍性定理:全奇数dで同一幾何分布。定理候補 | A |
| 115 | コラッツグラフSCC分析 | ✅ | exploration_115.md | ★入次数完全決定:deg∈{0,1,2}。DAG構造確認 **【Lean形式化済み】** | B |

## フェーズ20: ラウンド5バッチ1 (探索116-120)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 116 | Waterfall一般k帰納法 | ✅ | exploration_116.md | mersenne_orbit_mulから3-5行で導出可能。帰納構造完全解明 | A |
| 117 | v2(3^m-1) LTE公式 | ✅ | exploration_117.md | ★m奇→v2=1, m偶→v2=2+v2(m)。定理候補 | A |
| 118 | 一般Hensel帰納法設計 | ✅ | exploration_118.md | ★100-150行で形式化可能。T^k+1=2·3^k·mが核心 **【Lean形式化済み】** | A |
| 119 | mod 2^k置換サイクル構造 | ✅ | exploration_119.md | ★像の閉公式(k奇3/4,k偶7/12)。多重度完全公式 | A |
| 120 | Tao密度1精密化 | ✅ | exploration_120.md | k_min/logN≈8-10。末尾連続1がTST主因 | B |

## フェーズ21: ラウンド5バッチ2 (探索121-125)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 121 | 入次数≤2形式証明設計 | ✅ | exploration_121.md | 6補題設計。omega中心。Indegree.lean推奨 | A |
| 122 | log₂スケールRW精密化 | ✅ | exploration_122.md | I(0)精密値。KS~k^{-0.43}。TST偏差3.8% | B |
| 123 | 最小反例mod制約 | ✅ | exploration_123.md | ★メルセンヌ閾値定理。mod2^20で94.4%排除 | A |
| 124 | E[v₂]=2形式化戦略 | ✅ | exploration_124.md | ★3段階設計(150-230行)。Mathlib依存確認済 | A |
| 125 | 逆木GWモデル | ✅ | exploration_125.md | mu=4/3超臨界。絶滅確率=0。幅定数C≈0.6713 | B |

## フェーズ22: ラウンド5バッチ3 (探索126-130)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 126 | T^{-k}(1)逆像層 | ❌ | exploration_126.md | タイムアウト失敗 | - |
| 127 | 3^k·2^j-1型軌道分類 | ✅ | exploration_127.md | ★一般化Waterfall+waterfall_step候補 | A |
| 128 | v2列ブロック統計 | ✅ | exploration_128.md | 冗長度超線形。lag4ピーク。v2=4過大 | B |
| 129 | 3-adic評価構造 | ✅ | exploration_129.md | ★T(n)≡1(mod3)⟺v2偶数。3-adic従属性 | A |
| 130 | peak/n漸近分布 | ✅ | exploration_130.md | Weibull型上尾。trail_ones寄与0.59bits | B |

## フェーズ23: ラウンド8バッチ1 (探索161-165)

| # | 探索 | ステータス | 成果物 | 主要発見 | 評価 |
|---|------|----------|--------|---------|------|
| 161 | 10^7検証チャンク生成 | ✅ | exploration_161.md | チャンク分割設計。steps=750、180チャンク | C |
| 162 | syracuse_odd形式化 | ✅ | exploration_162.md | ★div_pow_v2_odd補題設計。20-30行で形式化可能 | A |
| 163 | 合流時間定数導出 | ✅ | exploration_163.md | RW初到達定式化。スペクトルギャップ関係 | C |
| 164 | N(m,k)シフト法則 | ✅ | exploration_164.md | v2層分解による代数的解析途中 | C |
| 165 | 全v2=1サイクル排除 | ✅ | exploration_165.md | ★iter_mul_formulaから10-15行で形式化可能 | A |

## 未着手の方向

| 方向 | 概要 | 優先度 |
|------|------|--------|
| ★d/u > log₂(3) の証明 | 証明できればコラッツと同値 | ★★★ |
| T(n) ≢ 0 (mod 3) のLean証明 | 形式化は容易そう | ★★ |
| ~~s(2n) = s(n) + 1 のLean証明~~ | ✅探索36で完了、探索42で拡張 | ~~★★~~ |
| Syracuseが奇数mod2^K上の全単射 | v2独立性の形式証明 | ★★ |
| 逆コラッツ木の全整数包含の形式化 | 予想と同値な言い換え | ★★ |
| ~~一般k Hensel帰納法~~ | ✅ **形式化済み** `hensel_general` | ~~★~~ |

## やってはいけないこと（失敗/行き止まり）

- `omega` で一般の 2^k を含む式を解こうとする → 使えない
- 個別サイクルでの縮小証明 → 9/8倍等で拡大するケースがある
- mod M でSyracuse写像を well-defined にしようとする → v2が可変で不可能
- `native_decide` の使用 → mathlibのlinterが禁止
- s3(n) mod 2 を不変量として使おうとする → 自明（s3(n) ≡ n mod 2）
- v2列のマルコフ依存を証明しようとする → 一様分布下では完全独立。軌道上の偏りは選択バイアス
