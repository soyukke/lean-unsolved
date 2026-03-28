---
name: tackle-unsolved
description: 未解決数学問題（コラッツ予想、ゴールドバッハ予想、双子素数予想、エルデシュ問題、Schur数など）に取り組むオーケストレータ。20個の探索手法をbrainstormし、Opus subagentで並列調査し、結果を集約し、形式化する自動サイクル。ユーザが数学の未解決問題の探索・調査・形式化・証明・計算実験を依頼したとき、または「探索して」「調べて」「コラッツ」「ゴールドバッハ」「エルデシュ」「Lean形式化」「並列探索」「brainstorm」等のキーワードが含まれるときにこのスキルを使用すること。/tackle-unsolved コマンドでも起動する。
argument-hint: [問題名 例: collatz, goldbach, twinprime, erdos89...]
---

# 未解決数学問題 — 自動探索オーケストレータ

## 対象問題: $ARGUMENTS

このスキルは状態を見て、今やるべきことを自動判定して実行する。
`/loop 15m /tackle-unsolved [問題名]` で常時稼働させることを想定。

## 自動サイクルの全体像

```
BRAINSTORM → BATCH(×4) → AGGREGATE → FORMALIZE → 次のBRAINSTORM → ...
   │              │            │            │
   │20手法生成    │5並列調査   │横断分析    │Lean証明作成
   │              │            │形式化候補  │Index.lean更新
   │              │            │の特定      │ビルド検証
   └──────────────┴────────────┴────────────┘
              知識は蓄積され、次のサイクルに活かされる
```

## プロジェクト構造

```
Unsolved/
├── Collatz/                 # コラッツ予想（14モジュール、最も充実）
│   ├── Defs.lean            # コア定義
│   ├── Structure.lean       # 構造的性質
│   ├── Mod.lean, Mod3.lean  # mod 分類
│   ├── Hensel.lean          # Hensel attrition
│   ├── Cycle.lean           # サイクル排除
│   ├── Accel.lean           # 上昇圧縮
│   ├── Formula.lean         # 一般公式
│   ├── Minimal.lean         # 最小反例
│   ├── FiveNPlusOne.lean    # 5n+1変種
│   └── StoppingTime/        # 停止時間（3分割）
│       ├── Defs.lean        # 基本定義・同値形式
│       ├── Verification.lean # 数値検証（≤10^6）
│       └── Orbit.lean       # 周期軌道・減少性
├── Erdos/                   # エルデシュ問題群（5ファイル）
├── Goldbach.lean            # ゴールドバッハ予想
├── TwinPrime.lean           # 双子素数予想
├── Schur.lean               # Schur数
└── Index.lean               # ★副産物定理カタログ（形式化済み成果の一覧）
```

## 判定フロー

### 1. 状態の読み込み

以下を読む:
- `Unsolved/explorations/queue.json`
- `Unsolved/explorations/$ARGUMENTS/INDEX.md`（存在すれば）
- `Unsolved/explorations/$ARGUMENTS/SUMMARY.md`（存在すれば）

### 2. 今やるべきことの判定

```
SUMMARY.md に未形式化の「定理候補」があるか?
│
├─ YES → フェーズ: FORMALIZE
│
└─ NO
    └─ キューに queued アイテムがあるか?
        │
        ├─ YES（5件以上）
        │   └─ done件数が aggregate_every の倍数に達しているか?
        │       ├─ YES → フェーズ: AGGREGATE
        │       └─ NO  → フェーズ: BATCH
        │
        ├─ YES（1-4件）
        │   └─ フェーズ: BATCH
        │
        └─ NO（0件）
            └─ done件数 > 0 で未集約?
                ├─ YES → フェーズ: AGGREGATE
                └─ NO  → フェーズ: BRAINSTORM
```

**FORMALIZE が最優先**: 形式化候補があるなら、探索を増やすより先に成果を定着させる。

### 3. 各フェーズの実行

#### フェーズ: BRAINSTORM

`/brainstorm` スキルの SKILL.md を読み、その手順に従う。
サブエージェントは `math-explorer` タイプで起動。Index.leanの既存定理との重複を回避。

#### フェーズ: BATCH

`/explore-batch` スキルの SKILL.md を読み、その手順に従う。
サブエージェントは `math-explorer` タイプで起動。形式化価値（formalization_value）を追跡。

#### フェーズ: AGGREGATE

`/explore-aggregate` スキルの SKILL.md を読み、その手順に従う。
形式化候補の特定 + Index.lean 更新推奨を含む。

#### フェーズ: FORMALIZE ★新規

`/formalize` スキルの SKILL.md を読み、その手順に従う。
- SUMMARY.md の形式化候補から1-2個を選択
- Lean 4 で sorry なし証明を作成
- `lake build` で検証
- Index.lean を更新
- SUMMARY.md の形式化状況を更新

### 4. 完了報告

実行が終わったら以下を出力:
- 何をしたか（BRAINSTORM / BATCH / AGGREGATE / FORMALIZE）
- 結果の要約
- **形式化した定理**（FORMALIZEフェーズの場合）
- キュー残数と次に実行されるフェーズ

## 重要な原則

- **1回1フェーズ**: BRAINSTORM / BATCH / AGGREGATE / FORMALIZE のどれか1つ
- **FORMALIZEを最優先**: 形式化候補があるなら探索より先に定着させる
- **判定を信じる**: 自己判断で別のことをしない
- **subagentは並列**: 逐次実行しない。math-explorerエージェントを使用
- **記録を残す**: 全ての結果はファイルに保存
- **形式化意識**: 主予想が解けなくても、副産物として価値ある定理を形式化することが成果になる
- **途中で諦めない**: 探索が難しくても「失敗した」と記録して完了扱いにする
- **sorry禁止**: Lean形式化でsorryは使わない
- **ファイル編集はメインのみ**: subagentにLeanファイルを編集させない
