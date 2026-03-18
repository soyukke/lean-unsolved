# 探索12: 大きい検証例 + isGoldbach_double_prime

## 日付
2026-03-18

## 目的
- 2000, 5000, 10000 での IsGoldbach 検証例を追加し、norm_num の4桁素数への適用を確認
- 素数 p に対する 2p の IsGoldbach 性を定理として証明

## 手法

### 大きい検証例
Python で素数判定を行い、適切な分解を選定:
- 2000 = 3 + 1997 (1997 は素数)
- 5000 = 7 + 4993 (4993 は素数。4997 は合成数のため不可)
- 10000 = 59 + 9941 (9941 は素数)

全て norm_num で素数判定が完了（各数秒以内）。

### isGoldbach_double_prime
p が素数なら p + p = 2 * p なので IsGoldbach (2 * p) が自明に成立。
証明は存在証拠 (p, p, hp, hp, by ring) で完結。

## 結果

### Lean 定理・検証例
```lean
-- 2000 = 3 + 1997
example : IsGoldbach 2000 := ⟨3, 1997, by norm_num, by norm_num, by norm_num⟩

-- 5000 = 7 + 4993
example : IsGoldbach 5000 := ⟨7, 4993, by norm_num, by norm_num, by norm_num⟩

-- 10000 = 59 + 9941
example : IsGoldbach 10000 := ⟨59, 9941, by norm_num, by norm_num, by norm_num⟩

/-- p が素数なら 2p は IsGoldbach -/
theorem isGoldbach_double_prime {p : ℕ} (hp : Nat.Prime p) : IsGoldbach (2 * p) :=
  ⟨p, p, hp, hp, by ring⟩
```

### ビルド結果
lake build 成功。sorry なし。

## 考察
- norm_num は4桁の素数 (1997, 4993, 9941) でも問題なく判定可能
- isGoldbach_double_prime は自明だが、偶数の無限族 {4, 6, 10, 14, 22, ...} が IsGoldbach であることを保証する
- この定理は「素数が無限に存在する」ことと組み合わせると、IsGoldbach な偶数が無限に存在することを示す
