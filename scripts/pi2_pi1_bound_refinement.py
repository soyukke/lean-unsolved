"""
Pi_2 -> Pi_1 帰着: 上界関数の精密な分析

Key insight: s(n)/log2(n) は無限大に発散する可能性がある。
Terrasの結果: "ほとんどすべての" n で s(n) < C*log2(n) だが、
例外的な n (record holder) での比率は log(n) とともに増大する。

ここでは:
1. record holder での s(n)/log2(n) の増大速度を分析
2. s(n) vs log2(n)^alpha の最適 alpha を推定
3. CC <-> BCC_f の形式化における微妙な点を分析
"""

import math
import json

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

def stopping_time(n):
    if n <= 0:
        return -1
    steps = 0
    current = n
    while current != 1:
        current = collatz_step(current)
        steps += 1
        if steps > 10**7:
            return -1
    return steps

# ===== 1. record holder の詳細分析 =====

print("=" * 70)
print("1. Record Holder の詳細分析: s(n) vs log2(n)")
print("=" * 70)

record_holders = []
max_ratio = 0

for n in range(2, 2 * 10**6 + 1):
    st = stopping_time(n)
    log2n = math.log2(n)
    ratio = st / log2n
    if ratio > max_ratio:
        max_ratio = ratio
        record_holders.append({
            'n': n,
            'st': st,
            'log2n': log2n,
            'ratio_log': ratio,
            'ratio_log_sq': st / (log2n ** 2),
            'ratio_loglog': ratio / math.log2(log2n) if log2n > 1 else 0
        })

print(f"{'n':>12} | {'s(n)':>6} | {'log2(n)':>8} | {'s/log':>8} | {'s/log^2':>8} | {'(s/log)/loglog':>14}")
print("-" * 70)
for r in record_holders:
    print(f"{r['n']:>12} | {r['st']:>6} | {r['log2n']:>8.2f} | "
          f"{r['ratio_log']:>8.4f} | {r['ratio_log_sq']:>8.4f} | {r['ratio_loglog']:>14.4f}")

# ===== 2. 上界関数 f(n) = C * log2(n)^alpha の最適 alpha =====

print("\n" + "=" * 70)
print("2. f(n) = C * log2(n)^alpha の最適パラメータ")
print("=" * 70)

# 各 alpha について最小の C を求める
alphas = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

for alpha in alphas:
    max_c = 0
    max_c_n = 1
    for n in range(2, 10**6 + 1):
        st = stopping_time(n)
        log2n = math.log2(n)
        c_needed = st / (log2n ** alpha)
        if c_needed > max_c:
            max_c = c_needed
            max_c_n = n
    print(f"alpha = {alpha:.1f}: min C needed = {max_c:.4f} (at n = {max_c_n}), "
          f"f(10^6) = {max_c * (math.log2(10**6)) ** alpha:.1f}")

# ===== 3. CC <-> BCC_f の微妙な論理 =====

print("\n" + "=" * 70)
print("3. CC <-> BCC_f の論理分析")
print("=" * 70)

print("""
【核心的な問題】

CC (Collatz Conjecture):
  forall n >= 1, exists k, T^k(n) = 1     ... Pi_2

CC が真なら stopping time s(n) が well-defined。
  s(n) = min{k : T^k(n) = 1}

BCC_f (Bounded Collatz Conjecture with bound f):
  forall n >= 1, T^{f(n)}(n) = 1           ... Pi_1 (if f computable)

★ CC <-> exists f computable, BCC_f
  証明:
  (→) CC が真なら s(n) が全域関数。だが s は計算可能か？
      CC が真 AND s が計算可能 → BCC_s
      しかし、CC が真でも s が原始帰納的とは限らない。
      実は CC が真なら s は全域計算可能（各 n で有限ステップで停止するから）。
      ∴ f = s でOK。

  (←) BCC_f → CC は自明: T^{f(n)}(n)=1 なら k=f(n) がwitness。

★ だが形式的には注意が必要:
  CC → BCC_f の証明で f = s を使うと、f の定義が CC に依存する。
  形式的には f は CC の証明オブジェクトから構成される。
  これは非構成的（古典論理が必要）。

★ よりクリーンな定式化:
  "exists f : Nat -> Nat, BCC_f" は CC と同値
  だが特定の f を提示することは CC を証明することに等しい。

★ Lean形式化での接続:
  既存の collatzConjectureR_iff_bounded が本質的にこの帰着を含む:
    CollatzConjectureR <-> forall n >= 1, exists k, collatzReachesBounded k n

  これを「特定の f」に制限すると:
    BCC_f -> CollatzConjectureR  (自明)
    CollatzConjectureR -> BCC_s  (s は noncomputable)

★ 重要な発見:
  CC と BCC_f は論理的に同値だが、
  CC は Pi_2、BCC_f は Pi_1 という「異なる複雑性クラス」に属する。
  この差は f の計算可能性に吸収される。

  具体的な f を構成的に与えられない限り、
  Pi_2 → Pi_1 の帰着は「原理的に可能」でしかない。
""")

# ===== 4. Lean形式化コードのスケッチ =====

print("=" * 70)
print("4. Lean 4 形式化コード設計")
print("=" * 70)

lean_sketch = """
-- BoundedCollatzConjecture: 計算可能上界 f による CC の Pi_1 版
def BoundedCollatzConjecture (f : Nat -> Nat) : Prop :=
  forall n : Nat, n >= 1 -> collatzIter (f n) n = 1

-- CC <-> exists f, BCC_f
theorem cc_iff_exists_bound :
    CollatzConjectureR <-> Exists (fun f => BoundedCollatzConjecture f) := by
  constructor
  . intro hcc
    -- CC が真なら stoppingTime が全域で定義される
    -- f(n) = stoppingTime n (noncomputable)
    use fun n => if h : n >= 1 then
      stoppingTime n (hcc n h) else 0
    intro n hn
    simp [hn]
    exact collatzIter_stoppingTime n (hcc n hn)
  . intro ⟨f, hbcc⟩
    intro n hn
    exact ⟨f n, hbcc n hn⟩

-- BCC_f -> CC は自明 (Pi_1 -> Pi_2 は自然な方向)
theorem cc_of_bounded (f : Nat -> Nat) (h : BoundedCollatzConjecture f) :
    CollatzConjectureR := by
  intro n hn
  exact ⟨f n, h n hn⟩

-- CC -> BCC_f は stoppingTime を使う (noncomputable)
noncomputable def stoppingTimeFn (hcc : CollatzConjectureR) : Nat -> Nat :=
  fun n => if h : n >= 1 then stoppingTime n (hcc n h) else 0

-- 有限版は decidable
def BoundedCollatzBelow (f : Nat -> Nat) (N : Nat) : Prop :=
  forall n : Nat, 1 <= n -> n <= N -> collatzIter (f n) n = 1

-- 任意の計算可能 f と有限 N に対して、BoundedCollatzBelow は decidable
-- (native_decide で検証可能)

-- 既存コードとの接続
theorem bounded_collatz_of_allReach (f : Nat -> Nat) (N : Nat)
    (h : forall n, 1 <= n -> n <= N -> collatzReachesBounded (f n) n = true) :
    BoundedCollatzBelow f N := by
  intro n hn1 hnN
  exact (collatzReaches_of_bounded (f n) n (h n hn1 hnN)).choose_spec.2
  -- ※ 実際には collatzReaches_of_bounded は exists を返すので
  -- collatzIter (f n) n = 1 を直接得るにはもう少し工夫が必要

-- ★ collatzReachesBounded と BoundedCollatzConjecture の橋渡し
-- collatzReachesBounded steps n = true → collatzIter steps n = 1 OR
--   exists k < steps, collatzIter k n = 1
-- 厳密には collatzIter (f n) n = 1 の証明には
-- 「f(n) が正確に stopping time 以上」が必要
"""

print(lean_sketch)

# ===== 5. 微妙な点: f(n) = s(n) でない場合 =====

print("\n" + "=" * 70)
print("5. f(n) > s(n) のとき T^{f(n)}(n) = 1 が成り立たない問題")
print("=" * 70)

# T^k(1) は 1,4,2,1,4,2,... のサイクル
# したがって T^k(n)=1 が成り立つ k は s(n), s(n)+3, s(n)+6, ...
# f(n) >= s(n) でも f(n) - s(n) が 3 の倍数でなければ T^{f(n)}(n) != 1

print("T^k(1) のサイクル:")
n = 1
for k in range(10):
    print(f"  T^{k}(1) = {n}")
    n = collatz_step(n)

print("\n例: n = 3, s(3) = 7")
n = 3
for k in range(15):
    val = stopping_time(3) if k == 0 else None
    # 実際に計算
    current = 3
    for _ in range(k):
        current = collatz_step(current)
    print(f"  T^{k}(3) = {current}", "  <-- reaches 1" if current == 1 else "")

print("""
★ 重大な発見: BoundedCollatzConjecture の定義に修正が必要

BCC_f: forall n >= 1, T^{f(n)}(n) = 1 は
f(n) が s(n) + 3k の形でない限り成り立たない。

修正版1 (existential):
  forall n >= 1, exists k <= f(n), T^k(n) = 1
  → これは元の CC とほぼ同じ (Pi_2 のまま!)

修正版2 (collatzReachesBounded を使用):
  forall n >= 1, collatzReachesBounded (f(n)) n = true
  → これは Pi_1 (decidable predicate)
  → 既存コードと完全に整合

修正版3 (正確な stopping time):
  forall n >= 1, T^{f(n)}(n) = 1  where f(n) = s(n)
  → これは CC そのものの再記述 (非構成的)

★ 結論: collatzReachesBounded を使った版が最適
""")

# ===== 6. 最終設計 =====

print("=" * 70)
print("6. 最終形式化設計")
print("=" * 70)

print("""
【最終設計: collatzReachesBounded ベースの Pi_1 帰着】

定義:
  def CollatzBoundedPi1 (f : Nat -> Nat) : Prop :=
    forall n : Nat, n >= 1 -> collatzReachesBounded (f n) n = true

これは Pi_1 文:
  - forall n (全称)
  - collatzReachesBounded (f n) n = true は計算可能述語
  - 反例があれば有限ステップで見つかる

同値性:
  theorem cc_iff_bounded_pi1 :
    CollatzConjectureR <-> Exists (fun f => CollatzBoundedPi1 f) := by
    constructor
    . intro hcc
      use fun n => (collatzReachesBounded_complete (hcc n (by omega))).choose
      -- ※ 正確にはChoose を使って witness を取り出す
    . intro ⟨f, hpi1⟩ n hn
      exact collatzReaches_of_bounded (f n) n (hpi1 n hn)

有限検証版:
  def CollatzBoundedPi1Below (f : Nat -> Nat) (N : Nat) : Prop :=
    forall n : Nat, 1 <= n -> n <= N -> collatzReachesBounded (f n) n = true

  instance : DecidableEq Bool := inferInstance
  -- native_decide で検証可能

既存検証との接続:
  collatzReaches_le_1000000 は事実上:
    CollatzBoundedPi1Below (fun _ => 600) 1000000

  より精密に:
    CollatzBoundedPi1Below (fun n => 9 * Nat.log2 n + 10) N -- NG
    CollatzBoundedPi1Below (fun n => 20 * (Nat.log2 n)^2) N -- OK for small N
""")

# ===== 結果保存 =====

result = {
    "title": "Pi_2 -> Pi_1 帰着: 計算可能上界による同値変換",
    "approach": "stopping timeの上界関数を詳細分析。9*log2(n)は不十分でO(log^2(n))が必要。collatzReachesBoundedベースの定式化が最適と判明。",
    "findings": [
        "s(n)/log2(n) の record holder は n=27 で 23.34, n=837799 で 26.63 と増大し続ける",
        "9*log2(n) 上界は既に N=32 (n=27) で破綻する",
        "20*log2(n)^2 は n<=10^6 で十分だが理論的保証なし",
        "BCC_f を T^{f(n)}(n)=1 で定義すると {1,4,2} サイクルのせいで f(n)=s(n)+3k でないと成立しない",
        "collatzReachesBounded ベースの Pi_1 定式化が最も自然で既存コードと整合する",
        "CC <-> exists f, CollatzBoundedPi1 f の形式化は既存の collatzConjectureR_iff_bounded から直接得られる"
    ],
    "hypotheses": [
        "s(n)/log2(n) は O(log(log(n))) で増大する可能性がある (Terrasの予想と関連)",
        "f(n) = C * log2(n) * log2(log2(n)) が最適な上界の形かもしれない"
    ],
    "dead_ends": [
        "T^{f(n)}(n)=1 での BCC 定義は {1,4,2} サイクルにより不適切",
        "9*log2(n) は上界として不十分"
    ],
    "record_holders": [
        {"n": 27, "st": 111, "ratio": 23.34},
        {"n": 230631, "st": 442, "ratio": 24.81},
        {"n": 626331, "st": 508, "ratio": 26.38},
        {"n": 837799, "st": 524, "ratio": 26.63}
    ],
    "scripts_created": ["scripts/pi2_to_pi1_analysis.py", "scripts/pi2_pi1_bound_refinement.py"],
    "outcome": "中発見",
    "next_directions": [
        "collatzReachesBounded ベースの CollatzBoundedPi1 と CC の同値性を Lean で形式化",
        "s(n) の record holder の増大速度を理論的に解析（Terras予想との関連）",
        "CollatzBoundedPi1Below の native_decide 検証を既存 Verification と統合"
    ],
    "lean_formalization_plan": {
        "new_definitions": [
            "CollatzBoundedPi1 (f : Nat -> Nat) : Prop",
            "CollatzBoundedPi1Below (f : Nat -> Nat) (N : Nat) : Prop"
        ],
        "new_theorems": [
            "cc_iff_bounded_pi1 : CollatzConjectureR <-> Exists CollatzBoundedPi1",
            "cc_of_bounded_pi1 : CollatzBoundedPi1 f -> CollatzConjectureR",
            "bounded_pi1_decidable_below : Decidable (CollatzBoundedPi1Below f N)"
        ],
        "connection_to_existing": "collatzConjectureR_iff_bounded から直接導出可能"
    }
}

with open("/Users/soyukke/study/lean-unsolved/results/pi2_pi1_reduction_analysis.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n結果を更新しました。")
