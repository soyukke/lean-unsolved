# 探索 102: consecutiveAscents の一般Hensel attrition定理の形式化分析

## メタデータ
- **キューID**: collatz-110
- **カテゴリ**: 既存補題の拡張
- **成果レベル**: 中発見
- **日付**: 2026-03-28

## アプローチ
CollatzHensel.lean, CollatzFormula.leanを精読し、k=1..4の具体的hensel_attrition定理を一般kに拡張する方針を設計。

## 発見
- 形式化可能（信頼度0.92）。推奨アプローチはk帰納法+mod算術逆変換
- 実際にはn≥2^k-1より強いn≥2^{k+1}-1が成立（n%2^{k+1}=2^{k+1}-1から）
- 核心はconsecutiveAscents_shift+mod逆変換: (3n+1)/2≡2^{k+1}-1(mod 2^{k+1})をn≡2^{k+2}-1(mod 2^{k+2})に変換
- 3がmod 2^mで可逆（奇数）であることが鍵

## 推奨定理文
```
theorem hensel_attrition_general (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1)
    (hk : k ≥ 1) (hasc : consecutiveAscents n k) : n % (2^(k+1)) = 2^(k+1) - 1

theorem consecutiveAscents_lower_bound (n k : ℕ) ... : n ≥ 2^(k+1) - 1
```

## 次のステップ
- v2_add_of_lt補題の先行実装（最優先）
- 3のmod 2^m逆元の存在補題
