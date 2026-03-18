# 探索14: IsTwinPrime と twin_prime_mod_six の連携

## 日付
2026-03-18

## 目的
- IsTwinPrime 述語に対するドット記法アクセサを追加
- 既存の twin_prime_mod_six, twin_prime_middle_div6 を IsTwinPrime 経由で呼べるようにする

## 成果

### TwinPrime.lean への追加
1. `IsTwinPrime.mod_six`: IsTwinPrime p かつ p > 3 → p % 6 = 5
   - twin_prime_mod_six h.1 h.2 hp3 で即座に証明
2. `IsTwinPrime.middle_div6`: IsTwinPrime p かつ p > 3 → 6 ∣ (p+1)
   - twin_prime_middle_div6 h.1 h.2 hp3 で即座に証明

## 数学的背景
探索12で導入した IsTwinPrime 述語と、探索3で証明済みの twin_prime_mod_six, 探索11の twin_prime_middle_div6 を連携させた。
ドット記法により `h.mod_six hp3` のような簡潔な呼び出しが可能になる。

双子素数 (p, p+2) で p > 3 のとき:
- p % 6 = 5（twin_prime_mod_six）
- 6 | (p+1)（twin_prime_middle_div6）
- つまり双子素数は常に 6k-1, 6k+1 の形

## ステータス
✅ 完了（sorry なし、lake build 通過）
