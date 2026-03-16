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

## 未着手の方向

| 方向 | 概要 | 優先度 |
|------|------|--------|
| s3(n) mod 2 不変性の証明 | 3進桁和の偶奇がSyracuseで保存 | ★★★ |
| v2マルコフ依存の形式化 | 遷移確率の正確な値をLeanで | ★★★ |
| T(n) ≢ 0 (mod 3) の証明 | 形式化は容易そう | ★★ |
| 一般k Hensel帰納法 | 技術的に可能だが大労力 | ★ |
| Tao証明の部分形式化 | Mathlib未整備で困難 | ★ |

## やってはいけないこと（失敗/行き止まり）

- `omega` で一般の 2^k を含む式を解こうとする → 使えない
- 個別サイクルでの縮小証明 → 9/8倍等で拡大するケースがある
- mod M でSyracuse写像を well-defined にしようとする → v2が可変で不可能
- `native_decide` の使用 → mathlibのlinterが禁止
