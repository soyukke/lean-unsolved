# 探索13: ひまわりの core サイズの性質

## 目標
同一集合の繰り返しがひまわりであることを形式証明する。

## アプローチ
2つの同一集合 [S, S] が IsSunflower であることを、既存の isSunflower_pair を直接適用して証明。

## 結果

### isSunflower_repeat
- **定理**: `IsSunflower [S, S]` （任意の Finset α に対して）
- **証明**: `isSunflower_pair S S` を exact で適用
- core = S ∩ S = S となり、花びらは S \ S = ∅ で自明に互いに素

### 考察
- 同一集合の繰り返しは IsSunflower の最も退化したケース
- core が集合自体と一致し、花びらが全て空になる
- isSunflower_pair の特殊ケースとして自然に導かれる
- ひまわり予想の文脈では、重複なし（Nodup）の仮定が通常つくため、このケースは直接的には現れないが、定義の整合性確認として有用

## 成果物
- `Unsolved/ErdosSunflower.lean` に `isSunflower_repeat` を追加（sorry なし）
