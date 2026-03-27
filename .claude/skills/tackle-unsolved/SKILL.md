---
name: tackle-unsolved
description: 未解決数学問題に取り組むオーケストレータ。brainstorm→並列subagent調査→集約の自動サイクル。
argument-hint: [問題名 例: collatz, goldbach, twinprime, erdos89...]
---

# 未解決数学問題 — 自動探索オーケストレータ

## 対象問題: $ARGUMENTS

このスキルは状態を見て、今やるべきことを自動判定して実行する。
`/loop 15m /tackle-unsolved [問題名]` で常時稼働させることを想定。

## 判定フロー

### 1. 状態の読み込み

以下を読む:
- `Unsolved/explorations/queue.json`
- `Unsolved/explorations/$ARGUMENTS/INDEX.md`（存在すれば）

### 2. 今やるべきことの判定

```
キューに queued アイテムがあるか?
│
├─ YES（5件以上）
│   └─ done件数が aggregate_every の倍数に達しているか?
│       ├─ YES → フェーズ: AGGREGATE
│       └─ NO  → フェーズ: BATCH（並列subagent調査）
│
├─ YES（1-4件）
│   └─ フェーズ: BATCH（残りを消化）+ BRAINSTORM（追加生成）
│
└─ NO（0件）
    └─ done件数 > 0 で未集約?
        ├─ YES → フェーズ: AGGREGATE → BRAINSTORM
        └─ NO  → フェーズ: BRAINSTORM
```

### 3. 各フェーズの実行

#### フェーズ: BRAINSTORM

`/brainstorm` スキルの SKILL.md を読み、その手順に従う:
1. 現状把握（INDEX.md、直近の探索ファイル、Leanファイル、queue.json）
2. 10-20の探索手法候補を生成
3. queue.json に書き込み
4. 最大5件をsubagentに並列ディスパッチして調査
5. 結果を収集・記録

#### フェーズ: BATCH

`/explore-batch` スキルの SKILL.md を読み、その手順に従う:
1. キューから最大5件を選択
2. 全件を並列subagentに同時ディスパッチ
3. 結果を収集・記録
4. queue.json を更新

#### フェーズ: AGGREGATE

`/explore-aggregate` スキルの SKILL.md を読み、その手順に従う:
1. 直近の done アイテムの結果ファイルを横断分析
2. SUMMARY.md を更新
3. カバレッジ分析
4. 次のアクション判定

### 4. 完了報告

実行が終わったら以下を出力:
- 何をしたか（BRAINSTORM / BATCH / AGGREGATE）
- 結果の要約（主要な発見があれば）
- キュー残数と次に実行されるフェーズ

## 重要な原則

- **1回1フェーズ**: BRAINSTORM or BATCH or AGGREGATE のどれか1つ
- **判定を信じる**: 自己判断で別のことをしない
- **subagentは並列**: 逐次実行しない
- **記録を残す**: 全ての結果はファイルに保存
- **途中で諦めない**: 探索が難しくても「失敗した」と記録して完了扱いにする
- **sorry禁止**: Lean形式化でsorryは使わない
- **ファイル編集はメインのみ**: subagentにLeanファイルを編集させない
