# 双子素数予想 探索インデックス

ステータス: ✅完了 🔬進行中 ❌失敗/放棄

## 現状
- TwinPrime.lean に定義、検証例8組+IsTwinPrime検証8組、基本補題（sorry なし）
- 探索17回完了

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

### 探索4: Brunの定理の数値的精密化 ✅
- スクリプト: `scripts/twinprime_brun.py`
- B₂(10⁷) ≈ 1.7383570439（理論値 B₂ ≈ 1.9021605831）
- 残差 B₂ - B₂(10⁷) ≈ 0.164 — 収束は非常に遅い（対数的）
- Mertens型公式 B₂(x) ≈ B₂ - C/ln²(x) の定数 C ≈ 42.6（10⁷時点）
- C は x の増加とともに増大 → 単純な 1/ln²(x) モデルでは不十分、高次補正が必要
- log-log 傾き ≈ -0.07（理論的な -2 より緩やか）→ 対数的補正項の存在を示唆
- 連続区間での増分比は ≈1.5〜1.8 で減少（収束の証拠）

### 探索5: 篩法（Selberg sieve）の数値実装 ✅
- スクリプト: `scripts/twinprime_sieve.py`
- Twin prime constant C₂ ≈ 1.3203236394（10⁷までの素数で計算、理論値との相対誤差 6×10⁻⁹）
- Selberg篩上界: π₂(x) ≤ S·x/ln²(x)、S ≈ 5.28（実測の約3.4倍）
- 実測の π₂(x)/(x/ln²x) ≈ 1.53（10⁷時点）、2C₂ ≈ 2.64 に向けて緩やかに収束
- 4x/ln²x の上界も有効だが、Selberg篩の方が定数が大きい（篩の構造的制約）
- Selberg篩は上界として正しいが最適定数は実測の5〜8倍 → GPY等の改良篩がより tight

### 探索6: Hardy-Littlewood第1予想式の検証 ✅
- スクリプト: `scripts/twinprime_hardy_littlewood.py`
- Li₂(x) = 2C₂ ∫₂ˣ dt/(ln t)² をSimpson則で数値計算
- π₂(10⁷)/Li₂(10⁷) = 0.501 — 10⁷ではまだ1から遠い（収束が非常に遅い）
- 簡易近似 2C₂x/ln²x、積分型 Li₂(x)、補正付き（部分積分展開）の3種を比較
- 補正付き近似が最も精度良好（10⁷で相対誤差 ≈ 2.6%）
- 残差 π₂(x) - Li₂(x) は調査範囲（10⁷まで）で常に負 — 符号変化は未検出
- π₂(x)·ln²(x)/x → 2C₂ の収束も非常に遅い（10⁷で約1.53、理論値2.64）

### 探索7: 双子素数の mod 30 構造 ✅
- `twin_prime_mod30`: p > 5 の双子素数 (p, p+2) は p % 30 ∈ {11, 17, 29}
- p%6=5 から p%30 ∈ {5,11,17,23,29} を導出
- p%30=5 → 5|p → p=5 だが p>5 で矛盾
- p%30=23 → 5|(p+2) → p+2=5 だが p>5 で矛盾
- 30個の剰余類のうち双子素数の p は3個のみ（10%）

### 探索8: Cousin primes と Sexy primes ✅
- `cousin_prime_mod_six`: p > 3 かつ (p, p+4) がともに素数なら p % 6 = 1
  - p%6=5 なら (p+4)%6=3 で 3|(p+4) → 矛盾
- `IsSexyPrime` の定義: p, p+6 がともに素数
- 検証例: (5,11), (7,13), (11,17), (13,19), (23,29)
- Twin: p%6=5, Cousin: p%6=1, Sexy: p%6=1 or 5 の対比

### 探索9: Cousin prime の mod 30 構造 ✅
- `cousin_prime_mod30`: p > 5 の cousin prime (p, p+4) は p % 30 ∈ {1, 7, 13, 19}
- p%6=1 から p%30 ∈ {1, 7, 13, 19, 25} を導出
- p%30=25 → 5|p → p=5 だが p>5 で矛盾 → 25 を排除
- Twin prime の mod 30: {11, 17, 29} (3個) vs Cousin: {1, 7, 13, 19} (4個)

### 探索11: 双子素数の間の数は6の倍数 + 大きい双子素数検証 ✅
- `twin_prime_middle_div6`: (p, p+2) が双子素数で p > 3 のとき 6 | (p+1)
- twin_prime_mod_six (p%6=5) から (p+1)%6=0 を導出
- 双子素数が常に「6の倍数の両隣」に位置することの形式化
- 3桁の双子素数検証: (101,103), (107,109), (137,139), (149,151)
- 累計検証例: 8+4=12組

### 探索13: IsTwinPrime の基本性質 ✅
- `IsTwinPrime.prime_left`: IsTwinPrime p → Nat.Prime p
- `IsTwinPrime.prime_right`: IsTwinPrime p → Nat.Prime (p+2)
- `IsTwinPrime.two_le`: IsTwinPrime p → p ≥ 2
- IsTwinPrime 述語に対するドット記法アクセサの提供

### 探索14: IsTwinPrime と twin_prime_mod_six の連携 ✅
- `IsTwinPrime.mod_six`: IsTwinPrime p かつ p > 3 → p % 6 = 5（twin_prime_mod_six のラッパー）
- `IsTwinPrime.middle_div6`: IsTwinPrime p かつ p > 3 → 6 ∣ (p+1)（twin_prime_middle_div6 のラッパー）
- IsTwinPrime 述語に対するドット記法で既存定理を呼べるようにした

### 探索15: 大きい双子素数の検証 ✅
- IsTwinPrime 59, IsTwinPrime 71 の検証例追加
- norm_num で自動証明
- 累計 IsTwinPrime 検証: 3, 5, 11, 17, 29, 41, 59, 71 の8個

### 探索17: 大きい双子素数 ✅
- IsTwinPrime 179, 191, 197 の検証例追加
- (179,181), (191,193), (197,199) はすべて双子素数
- norm_num で自動証明
- 累計 IsTwinPrime 検証: 3, 5, 11, 17, 29, 41, 59, 71, 179, 191, 197 の11個

### 探索18: 素数三つ子の非存在 (p > 3) ✅
- `no_prime_triplet_gt3`: p > 3 の双子素数 (p, p+2) では p+4 は素数でない
- twin_prime_mod_six で p%6=5 → (p+4)%6=3 → 3|(p+4) → 素数でない
- 素数三つ子 (p, p+2, p+4) は (3, 5, 7) のみ

### 探索19: IsCousinPrime の定義 ✅
- `IsCousinPrime` 述語の定義: `Nat.Prime p ∧ Nat.Prime (p + 4)`
- 検証例: IsCousinPrime 3, 7, 13, 37, 67（全て norm_num で自動証明）
- `IsCousinPrime.mod_six`: p > 3 → p % 6 = 1（cousin_prime_mod_six のラッパー）
- IsTwinPrime (差2) との対比: Twin→p%6=5, Cousin→p%6=1

### 探索20: IsTwinPrime p → p ≥ 3 ✅
- `IsTwinPrime.three_le`: IsTwinPrime p → p ≥ 3
- by_contra + interval_cases で p=0,1,2 を排除
- p=0: Nat.not_prime_zero、p=1: Nat.not_prime_one、p=2: 4は素数でない
- IsTwinPrime の最小値が 3 であることを確定

### 探索16: TwinPrimeConjecture の同値な定式化 ✅
- `twinPrimeConjecture_iff`: TwinPrimeConjecture ↔ ∀ N, ∃ p > N, IsTwinPrime p
- TwinPrimeConjecture の定義を IsTwinPrime 述語で書き直せることを形式証明
- unfold して構造が同一であることを示すだけの簡潔な証明

### 探索12: 双子素数ペアの対称性 ✅
- `IsTwinPrime` 定義述語の導入: `Nat.Prime p ∧ Nat.Prime (p + 2)`
- `twin_prime_second`: 自明だが明示的な p+2 の素数性
- 検証例: IsTwinPrime 3, 5, 11, 17, 29, 41（全て norm_num で自動証明）
- 双子素数予想を `∃ p > N, IsTwinPrime p` と簡潔に記述可能に

## 次の探索方向
- Brunの定理の形式化: 双子素数の逆数和 B₂ が収束することの証明（Selberg篩を使う）
- Twin prime constant C₂ の形式化: Euler積表示の証明
- Hardy-Littlewood予想の精密化: 10⁸〜10⁹ での数値検証（高速篩が必要）
- mod 30 パターンの証明（p > 5 の双子素数は p ≡ 11, 17, 29 (mod 30)）
- Selberg篩の上界改良: Bombieri-Davenport型の定数改善
- Zhang (2013) の有界ギャップ定理 lim inf(pₙ₊₁ - pₙ) < 7×10⁷ の形式化検討
