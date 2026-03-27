---
name: explore-batch
description: キューから複数の探索手法を取り出し、subagentに並列で調査させ、結果を収集・記録する。
argument-hint: [問題名] [件数(デフォルト5)]
---

# 並列探索バッチ

## 対象問題: $ARGUMENTS

## 手順

### 1. キュー読み込みと選択

`Unsolved/explorations/queue.json` を読む。

- `status: "queued"` のアイテムを `priority` 昇順で最大5件選択
- 0件なら「キューが空です。`/brainstorm [問題名]` で補充してください」と報告して終了
- 選択したアイテムの `status` を `"in_progress"` に更新してqueue.jsonに**即座に**書き戻す
  - 書き戻し時は queue.json を**再読み込みしてからマージ**する（他プロセスによる更新との競合を防ぐ）

### 1b. 問題概要の取得

subagentに問題の背景情報を渡すため、以下から問題概要を収集する:

- `.claude/skills/tackle-unsolved/problems.md` → 問題の基本定義とLeanファイル一覧
- `Unsolved/explorations/[problem]/INDEX.md` → 過去の探索履歴と主要発見
- `Unsolved/explorations/[problem]/SUMMARY.md` → 集約済みの知識（存在すれば）

これらから「既知の重要事実」を箇条書き5-10項目にまとめる。

### 2. subagent の並列ディスパッチ

選択した各アイテムについて、Agent ツールで subagent を起動する。
**全subagentを1つのメッセージで同時に起動すること**（並列実行）。

各subagentへのプロンプトは以下の形式:

```
あなたは未解決数学問題の探索エージェントです。以下の探索手法を実行してください。

## 問題: [1bで収集した問題概要]
## 探索手法: [キューアイテムのtitle]
## カテゴリ: [category]
## 説明: [description]
## 期待される成果: [expected_output]

## 既知の重要事実（過去の探索から）
[1bで収集した箇条書き5-10項目]

## 実行ルール
- 使用ツール: [tools 配列の全要素について、該当するルールを全て列挙する]
  - python → Pythonスクリプトを作成・実行して計算実験。スクリプトは `scripts/` に保存
  - lean → Lean 4 コードの調査・分析（ファイルの読み取りのみ、編集しない）
  - websearch → WebSearch で関連研究・既知結果を調査
  - analysis → 数学的分析（代数的操作、場合分け等）を行い結論を記述
  - ※ tools に複数のツールがある場合（例: ["python", "analysis"]）、全ツールを組み合わせて使ってよい
- 15分以内に完了すること
- 行き詰まったら「失敗した理由」を明記して終了してよい（諦めてOK）
- 結果は以下のJSON形式で返すこと:

{
  "title": "探索タイトル",
  "approach": "何をしたか（2-3文）",
  "findings": ["発見1", "発見2", ...],
  "hypotheses": ["仮説1（もしあれば）", ...],
  "dead_ends": ["行き止まり1（もしあれば）", ...],
  "scripts_created": ["スクリプトファイル名（もしあれば）"],
  "outcome": "なし / 小発見 / 中発見 / 大発見 / ブレイクスルー",
  "next_directions": ["次に試すべき方向1", ...],
  "details": "詳細な分析結果（自由記述）"
}

## 現在のプロジェクト状態
- 作業ディレクトリ: (プロジェクトルート)
- Leanソース: Unsolved/ 以下
- 探索ログ: Unsolved/explorations/[problem]/ 以下
- Pythonスクリプト: scripts/ 以下
```

#### subagent の設定

- `subagent_type`: `"general-purpose"` を使用
- 各subagentの `description` は探索手法のタイトルの先頭5語程度
- Lean形式化が含まれる場合は `isolation: "worktree"` を使用

### 3. 結果の収集と記録

全subagentの結果が返ってきたら:

#### 3a. 各探索の結果ファイル作成

`Unsolved/explorations/[problem]/` に各探索の結果を保存:

ファイル名: `exploration_NNN.md`（NNNは連番、既存ファイルから次の番号を算出）

```markdown
# 探索 NNN: [タイトル]

## メタデータ
- **キューID**: [id]
- **カテゴリ**: [category]
- **成果レベル**: [outcome]
- **日付**: [今日の日付]

## アプローチ
[approach]

## 発見
[findings をリスト化]

## 仮説
[hypotheses をリスト化]

## 行き止まり
[dead_ends をリスト化]

## 詳細
[details]

## 次のステップ
[next_directions をリスト化]
```

#### 3b. INDEX.md の更新

各探索について1行追加。

#### 3c. queue.json の更新

各アイテムを `"done"` に更新:
```json
{
  "status": "done",
  "completed": "2026-03-27",
  "result_file": "exploration_NNN.md",
  "outcome": "小発見",
  "summary": "1行要約"
}
```

### 4. バッチサマリー

全subagentの結果を横断的に見て、以下を出力:

```
## バッチ結果サマリー
- 実行: N件
- 成果: 大発見 x件, 中発見 x件, 小発見 x件, なし x件
- 主要な発見:
  - [最も重要な発見1]
  - [最も重要な発見2]
- キュー残数: M件
- 次のアクション: [explore-batch継続 / explore-aggregate推奨 / brainstorm推奨]
```

### 5. 集約チェック

queue.json の `done` 件数が `aggregate_every` の倍数に達していたら:
- 「集約タイミングです。`/explore-aggregate [問題名]` の実行を推奨」と通知

## 重要な制約

- **subagentにはファイル編集させない**: Leanファイルの編集はメインエージェントが集約後に行う
- **全subagentを並列起動**: 逐次実行しない
- **結果を必ず記録**: subagentが失敗しても「失敗」として記録する
- **キューを信じる**: キューにないものは調査しない
