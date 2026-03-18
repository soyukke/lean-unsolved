# 探索13: 素数ペアの一意性 + isGoldbach_sum_comm

## 日付
2026-03-18

## 目的
- ゴールドバッハ分解の非一意性を具体例で示す（10 = 3+7 = 5+5）
- 素数和の可換性 isGoldbach_sum_comm を定理として追加

## 手法

### 非一意性の具体例
10 はすでに IsGoldbach 10 := ⟨3, 7, ...⟩ で検証済み。
別の分解 10 = 5 + 5 も IsGoldbach 10 := ⟨5, 5, ...⟩ で検証。
同一の偶数に対して異なる素数ペアが存在する最小例。

### isGoldbach_sum_comm
素数 p, q に対して p + q が IsGoldbach なら q + p も IsGoldbach。
自然数の加法は可換だが、IsGoldbach の存在証拠としては (q, p, hq, hp, rfl) で構成。

## 結果

### Lean 定理・検証例
```lean
/-- p+q = p'+q' = n で (p,q) ≠ (p',q') の具体例: 10 = 3+7 = 5+5 -/
example : IsGoldbach 10 := ⟨5, 5, by norm_num, by norm_num, by norm_num⟩

/-- 素数 + 素数 = 偶数 の系 -/
theorem isGoldbach_sum_comm {p q : ℕ} (hp : Nat.Prime p) (hq : Nat.Prime q) :
    IsGoldbach (q + p) :=
  ⟨q, p, hq, hp, rfl⟩
```

### ビルド結果
lake build 成功。sorry なし。

## 考察
- g(10) = 2: 最小の g(n) > 1 となる偶数（4, 6, 8, 12 は g(n)=1）
- isGoldbach_sum_comm は自明だが、isGoldbach_of_prime_add と合わせて和の順序を問わないことを明示
- 非一意性は g(n) の研究（素数ペアの数え上げ）への形式的基盤
