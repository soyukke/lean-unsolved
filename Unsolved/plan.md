# コラッツ予想 探索記録

詳細な探索インデックスは [explorations/collatz/INDEX.md](explorations/collatz/INDEX.md) を参照。
全問題の一覧は [explorations/INDEX.md](explorations/INDEX.md) を参照。

## 現在のステータス
- 探索回数: 29回完了（うち2件は自明/バイアスで棄却）
- Leanファイル: 7個（全て sorry なし、Baker公理のみ axiom）
- Pythonスクリプト: 15個

## 最重要のLean形式証明済み結果
1. mod 4 上昇/下降分類: n≡1→下降, n≡3→上昇
2. 一般公式: 2^k·T^k(n) = 3^k·n + (3^k - 2^k)（連続上昇中、任意k）
3. 完全サイクル上界: 4·2^k·T^{k+1}(n) + 2^{k+1} ≤ 3^{k+1}·(n+1)
4. Hensel attrition: k回連続上昇 ⟺ n≡2^{k+1}-1 (mod 2^{k+1})
5. サイクル排除: 3^a=2^b→a=b=0, Baker公理で非自明サイクル排除

## 最有望な次の方向
1. ★★★ d/u > log₂(3) の証明（コラッツと同値）
2. ★★ 形式化可能な小さい結果: T(n)≢0(mod3), s(2n)=s(n)+1
