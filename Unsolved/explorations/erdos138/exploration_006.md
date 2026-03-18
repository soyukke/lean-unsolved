# 探索6: N=3 での 3-AP 回避可能性の形式化

## 日付
2026-03-18

## 目的
N=3 で 3項等差数列を回避する塗り分けが存在することを Lean で形式的に検証する。

## 手法

### 分析
- N=3 の位置は {0, 1, 2}
- 3-AP は a, a+d, a+2d (d >= 1) で a+2d < 3 を満たすもの
- 唯一の候補: a=0, d=1 → (0, 1, 2)
- 塗り分け RBR (false, true, false) では色が F, T, F で単色でない
- 塗り分け BRB (true, false, true) も同様に単色でない

### リストベース検証
- `hasMonoAPList` を使って決定的に検証
- `hasMonoAPList [false, true, false] 3 = false` が `rfl` で証明可能

## 結果

### 追加した検証
1. `hasMonoAPList [false, true, false] 3 = false` -- RBR 塗り分け
2. `hasMonoAPList [true, false, true] 3 = false` -- BRB 塗り分け（色反転）
3. `hasMonoAPList [false, true] 3 = false` -- N=2 でも回避可能

### CanAvoid 3 3 について
- `CanAvoid` は存在命題（Prop）なので `rfl` では直接示せない
- リストベースの `hasMonoAPList` による検証は Bool の等式なので `rfl` で済む
- Prop 版は塗り分けの構成 + 単色 AP の不存在の証明が必要で、
  `HasMonochromaticAP` の定義が存在量化を含むため直接的な `decide` が難しい
- リストベース検証で実質的に同等の結果を得ている

## 成果物
- `Unsolved/ErdosVanDerWaerden.lean`: N=3 での 3-AP 回避検証を追加

## 既存の結果との関係
- 探索3 で N=8 での回避（W(3)=9 の下界）を検証済み
- 今回は最小ケース N=3 での回避を追加

## 次のステップ
- W(4)=35 の部分検証（N=34 での回避塗り分け構成）
- CanAvoid の Prop 版での直接証明（Decidable インスタンス経由）
- W(k) の単調性の Lean 形式化
