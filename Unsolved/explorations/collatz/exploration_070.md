# 探索70: collatzReaches の偶数合成と具体例

## 目標
collatzReaches_even_iff を使った便利定理と、新しい具体例の追加。

## 成果

### CollatzStoppingTime.lean への追加

1. **collatzReaches_of_half**: n が偶数で collatzReaches (n/2) なら collatzReaches n
   - collatzReaches_even_iff の mpr 方向を直接呼ぶヘルパー
   - 偶数の到達可能性を半分の値から導出する際に便利

2. **collatzReaches_twenty**: collatzReaches 20
   - 20 は 7ステップで 1 に到達: 20→10→5→16→8→4→2→1
   - `decide` で自動証明

### collatzReaches 27 について
- 27 は有名な「111ステップで到達」する値
- `decide` での証明は計算量が大きすぎるためタイムアウトの懸念があり、今回は省略

## 技術的ノート
- collatzReaches_of_half は collatzReaches_even_iff.mpr の薄いラッパーだが、
  iff 全体を展開せずに使えるため可読性が向上する
- collatzReaches 20 は 7ステップなので decide で問題なく通る
