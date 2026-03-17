# 双子素数予想 探索インデックス

ステータス: ✅完了 🔬進行中 ❌失敗/放棄

## 現状
- TwinPrime.lean に定義、検証例8組、基本補題2つ（sorry なし）
- 探索3回完了

## 探索記録

### 探索1: Mathlibの関連定理調査 ✅
- Mathlibに双子素数の直接的な形式化は存在しない
- 関連する形式化: `Nat.primeCounting`, `SelbergSieve`, `SumPrimeReciprocals`, `Chebyshev`
- Brunの定理、Zhang/Maynard-Taoの有界ギャップ定理は未形式化
- Selberg篩の基本設定があるので、上界篩を使った双子素数の密度上界は形式化の方向として有望

### 探索2: 数値実験 ✅
- スクリプト: `scripts/twinprime_explore.py`
- π₂(10⁶) = 8,169 組
- 密度は Hardy-Littlewood 予想と整合的に減少
- Brunの定数 B₂ ≈ 1.711 (10⁶までの部分和、理論値 ≈ 1.902)
- p > 3 の双子素数は全て p ≡ 5 (mod 6)
- mod 30 では 11, 17, 29 の3剰余類にほぼ均等分布（各 ≈33%）
- 素数ギャップ分布: gap=2 と gap=4 がほぼ同数（各 ≈10.4%）、gap=6 が最頻（≈17.3%）

### 探索3: Lean検証例と基本補題 ✅
- 双子素数の検証例: (3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)
- `prime_gt_three_mod_six`: 素数 p > 3 なら p % 6 = 1 or 5
- `twin_prime_mod_six`: 双子素数 (p, p+2) で p > 3 なら p % 6 = 5
- `twin_prime_plus_two_mod_six`: 双子素数 (p, p+2) で p > 3 なら (p+2) % 6 = 1
- 全て sorry なし、lake build 通過

## 次の探索方向
- Hardy-Littlewood の双子素数定数 C₂ の形式化
- Selberg篩を使った双子素数密度の上界証明
- Brunの定理（双子素数の逆数和が収束）の形式化可能性調査
- mod 30 パターンの証明（p > 5 の双子素数は p ≡ 11, 17, 29 (mod 30)）
- Zhang (2013) の有界ギャップ定理 lim inf(pₙ₊₁ - pₙ) < 7×10⁷ の形式化検討
