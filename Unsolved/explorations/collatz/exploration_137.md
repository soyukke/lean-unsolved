# 探索 137: v2_mul乗法性の形式化設計

## メタデータ
- **キューID**: collatz-140
- **成果レベル**: 小発見
- **形式化価値**: 定理候補
- **日付**: 2026-03-29

## 発見
- v2_odd_mul: a%2=1 → v2(a*b)=v2(b)。bのstrongRecOn
- v2_mul: a>0→b>0→v2(a*b)=v2(a)+v2(b)。aのstrongRecOn
- 核心技法: calc+ringでa*b=2*((a/2)*b)変換
- pow_v2_dvdと同一パターン（実証済み）
