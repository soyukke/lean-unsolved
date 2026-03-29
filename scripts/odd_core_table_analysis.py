"""
奇数核テーブル方式の設計分析
==========
目的: native_decide以外でn<=10^7のコラッツ検証をLeanで実現する設計を具体化。

奇数核テーブル方式のアイデア:
- 偶数 n = 2^a * m (m奇数) のコラッツ到達可能性は m の到達可能性に帰着
- よって奇数のみテーブルに記録すれば十分
- n <= 10^7 の奇数は 5,000,000 個
- Syracuse関数で各奇数を追跡し、「既知の到達可能値」に落ちたら完了

戦略比較:
1. native_decide チャンク方式 (現在): 50K単位、native_decide
2. 奇数核テーブル + decide: 奇数のみ列挙、decide or native_decide
3. 奇数核テーブル + メタプログラミング: Lean elaboration時にテーブルを構築
4. 外部証明 + Lean検証: 外部で証拠データ生成、Leanで検証のみ
"""

import time
import math
import json

# ===== 基礎分析 =====

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

def syracuse(n):
    """Syracuse function: odd n -> next odd in Collatz sequence"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def collatz_reaches_one(n, max_steps=10000):
    """n -> (reaches_one, steps, max_value)"""
    steps = 0
    current = n
    max_val = n
    while current != 1 and steps < max_steps:
        current = collatz_step(current)
        steps += 1
        max_val = max(max_val, current)
    return current == 1, steps, max_val

def syracuse_reaches_known(n, known_set, max_steps=10000):
    """odd n -> (reaches_known, steps_to_known, target)"""
    steps = 0
    current = n
    while current not in known_set and steps < max_steps:
        current = syracuse(current)
        steps += 1
    if current in known_set:
        return True, steps, current
    return False, steps, current

# ===== 分析1: 奇数の個数 =====
print("=" * 60)
print("分析1: 対象サイズ")
print("=" * 60)

for limit in [10**5, 10**6, 10**7, 10**8]:
    odd_count = limit // 2
    even_count = limit - odd_count
    print(f"n <= {limit:>12,}: 奇数 {odd_count:>12,}, 偶数 {even_count:>12,}")
    print(f"  削減率: {odd_count/limit*100:.1f}% (偶数は奇数核に帰着)")

# ===== 分析2: Syracuse反復で「小さい値」に落ちるまでのステップ数 =====
print()
print("=" * 60)
print("分析2: Syracuse反復ステップ数の分布 (n <= 10^6)")
print("=" * 60)

limit = 10**6
step_counts = []
max_intermediates = []
known = {1}  # initially only 1 is known

t0 = time.time()
for n in range(3, limit + 1, 2):
    steps = 0
    current = n
    max_inter = n
    while current >= n:  # n より小さくなるまで追跡
        current = syracuse(current)
        steps += 1
        max_inter = max(max_inter, current)
    step_counts.append(steps)
    max_intermediates.append(max_inter)
t1 = time.time()

print(f"計算時間: {t1-t0:.2f}秒")
print(f"奇数の個数: {len(step_counts):,}")

# ステップ数の分布
from collections import Counter
step_dist = Counter(step_counts)
print(f"\nステップ数分布 (syracuse反復で自分より小さくなるまで):")
for s in sorted(step_dist.keys()):
    if step_dist[s] >= 10:
        print(f"  {s:>3} steps: {step_dist[s]:>8,} ({step_dist[s]/len(step_counts)*100:.2f}%)")

max_steps = max(step_counts)
avg_steps = sum(step_counts) / len(step_counts)
print(f"\n最大ステップ数: {max_steps}")
print(f"平均ステップ数: {avg_steps:.2f}")
print(f"最大中間値: {max(max_intermediates):,}")

# ===== 分析3: native_decide vs decide のコスト推定 =====
print()
print("=" * 60)
print("分析3: Lean証明方式のコスト推定")
print("=" * 60)

# 現在の native_decide 方式
# 50K チャンク x 20 = 10^6, steps=600
# native_decide は内部的に全件をカーネルで逐一評価
# 推定: 10^7 なら 200チャンク x 50K, native_decide はO(N*S)

# native_decide: 1件あたり O(S) where S = max stopping time
# for n <= 10^7, max stopping time ~= 700 (known: 9780657630 -> 1132 steps)
# n <= 10^7 では max ~= 600-700 steps

limit_test = 10**7
# Known: for n <= 10^7, the maximum total stopping time is for n=8400511, which is 686 steps
# Let's verify max stopping time up to 10^7 with sampling

import random
random.seed(42)
sample_size = 100000
sample = random.sample(range(1, 10**7 + 1), sample_size)

t0 = time.time()
max_stop = 0
for n in sample:
    _, s, _ = collatz_reaches_one(n, 10000)
    max_stop = max(max_stop, s)
t1 = time.time()

print(f"サンプル {sample_size:,} 件 (n<=10^7): 最大ステップ {max_stop}")
print(f"サンプル計算時間: {t1-t0:.2f}秒")

# ===== 分析4: 奇数核テーブル方式の具体設計 =====
print()
print("=" * 60)
print("分析4: 奇数核テーブル方式の設計")
print("=" * 60)

# 方式A: 奇数 -> Syracuse反復 -> 自分より小さい奇数に到達
# 方式B: 奇数 -> Syracuse反復 -> 既知集合に到達 (帰納的に構築)

# 方式Bの具体化:
# Phase 1: 1,3,5,...を順に処理
# 各奇数 n について、syracuse反復で n より小さい値に到達 → 既知
# これは方式Aと同じだが、帰納法のチェーン長が最悪 O(N)

# 方式C: 「外部で証拠(witness)を計算し、Leanで検証のみ」
# 各奇数 n に対して (steps_k, intermediate_bound) を witness として提供
# Lean側: syracuseIter steps_k n < n を検証

print("方式A: 全奇数に対して「自分より小さくなるステップ数」を提供")
print("  - 各 n に対して steps(n) を外部計算")
print("  - Lean検証: syracuseIter steps(n) n < n")
print()

# 方式Aのwitness生成
print("方式Aのwitness (n <= 10^6, 奇数のみ):")
limit = 10**6
witnesses = {}
max_witness_step = 0

t0 = time.time()
for n in range(3, limit + 1, 2):
    current = n
    steps = 0
    while current >= n:
        current = syracuse(current)
        steps += 1
    witnesses[n] = steps
    max_witness_step = max(max_witness_step, steps)
t1 = time.time()

print(f"  奇数件数: {len(witnesses):,}")
print(f"  最大ステップ数: {max_witness_step}")
print(f"  witness生成時間: {t1-t0:.2f}秒")

# witness のサイズ推定 (10^7)
print()
print(f"10^7 の場合の推定:")
odd_count_7 = 5_000_000
# ステップ数は 1-2 bytes per entry (max ~200 for Syracuse)
witness_size_bytes = odd_count_7 * 2  # avg 2 bytes per entry
print(f"  奇数件数: {odd_count_7:,}")
print(f"  witness データサイズ (生データ): ~{witness_size_bytes / 1024 / 1024:.1f} MB")

# ===== 分析5: Lean での具体的実装方式 =====
print()
print("=" * 60)
print("分析5: Lean実装の具体的選択肢")
print("=" * 60)

# 選択肢1: native_decide チャンク拡張 (現在の延長)
# - 50K チャンク x 200 = 10^7
# - 各チャンクで native_decide
# - 生成されるLeanファイルが巨大
chunk_size = 50000
num_chunks = 10**7 // chunk_size
lines_per_chunk = 8  # theorem + native_decide + options
total_lines = num_chunks * lines_per_chunk
print(f"選択肢1: native_decide チャンク拡張")
print(f"  チャンク数: {num_chunks}")
print(f"  推定Leanコード行数: ~{total_lines:,}")
print(f"  問題: native_decide は kernel external, 形式検証の精神に反する")
print()

# 選択肢2: decideマクロ (pure kernel proof)
# - decide はカーネル内でBoolを計算
# - 非常に遅い: 10^3 まで実用的、10^4 で厳しい
print(f"選択肢2: decide")
print(f"  利点: pure kernel proof")
print(f"  問題: 10^4 でも heartbeat limit に達する可能性高い")
print()

# 選択肢3: メタプログラミング (Lean.Elab.Tactic)
# - elaborate time に計算を実行
# - 結果を term として構築
# - kernel は最終的な term のみ検査
print(f"選択肢3: メタプログラミング (elaborator)")
print(f"  アイデア: elaborate時に各奇数を計算し、証明項を構築")
print(f"  利点: カーネルは構築された証明項のみ検証(高速)")
print(f"  問題: 5M個の証明項のメモリ使用量")
print()

# 選択肢4: 外部証拠ファイル + Leanパーサー
print(f"選択肢4: 外部証拠ファイル")
print(f"  フロー: Python → witness.json → Lean elaborator → proof term")
print(f"  利点: 計算は外部(高速), 検証はLean(信頼)")
print()

# 選択肢5: 帰納チェーン方式 (奇数核テーブル)
print(f"選択肢5: 帰納チェーン方式")
print(f"  アイデア:")
print(f"    1. collatzReaches_le_K (K <= 10^6) を既存証明として利用")
print(f"    2. 各奇数 n (10^6 < n <= 10^7) に対して:")
print(f"       syracuseIter s(n) n < 10^6 を示す → 帰納的に完了")
print(f"  利点: 各奇数は独立に検証可能(並列化)")
print()

# ===== 分析6: 帰納チェーン方式の具体分析 =====
print("=" * 60)
print("分析6: 帰納チェーン方式の実現可能性分析")
print("=" * 60)

# n > 10^6 の奇数について、syracuse反復で 10^6 以下に落ちるまでのステップ数
limit = 10**7
threshold = 10**6
sample_odds = list(range(10**6 + 1, 10**6 + 100001, 2))  # 50K sample

t0 = time.time()
chain_steps = []
chain_max_vals = []
for n in sample_odds:
    current = n
    steps = 0
    max_val = n
    while current > threshold:
        current = syracuse(current)
        steps += 1
        max_val = max(max_val, current)
    chain_steps.append(steps)
    chain_max_vals.append(max_val)
t1 = time.time()

print(f"サンプル: 奇数 {len(sample_odds):,} 件 (10^6+1 ~ 10^6+100001)")
print(f"計算時間: {t1-t0:.2f}秒")
print(f"ステップ数: 平均={sum(chain_steps)/len(chain_steps):.1f}, 最大={max(chain_steps)}")
print(f"中間最大値: {max(chain_max_vals):,}")

# 10^7 の最悪ケース推定
print()
print("10^7 近傍のサンプル:")
sample_near_10m = list(range(9_999_901, 10_000_001, 2))
worst_steps = 0
worst_n = 0
for n in sample_near_10m:
    current = n
    steps = 0
    while current > threshold:
        current = syracuse(current)
        steps += 1
    if steps > worst_steps:
        worst_steps = steps
        worst_n = n

print(f"  最悪ケース: n={worst_n}, steps={worst_steps}")

# ===== 分析7: メモリ推定 =====
print()
print("=" * 60)
print("分析7: メモリ・時間推定")
print("=" * 60)

# Lean の証明項サイズ推定
# 方式5 (帰納チェーン): 各チャンクの native_decide term
# 現在: 50K チャンク = 1 native_decide 証明 → ~数十MBのカーネルメモリ
# 10^7: 200チャンク → parallel build 可能

# 方式3 (メタプログラミング):
# 各奇数の証明 = Exists.intro k (by rfl-like term)
# k は ステップ数、rfl part は collatzIter k n = 1 の計算
# 問題: Lean Expression のサイズ
# collatzIter k n を完全に展開すると exponential size
# → 展開しない方式が必要

# 最適方式: 奇数核 + Syracuse 降下証拠 + チャンク
# 各チャンク [lo, hi] について:
# 定理: ∀ n, lo ≤ n → n ≤ hi → collatzReaches n
# 証明:
#   - 偶数 n = 2^a * m を m に帰着
#   - 奇数 m について syracuseIter s(m) m < lo を外部計算
#   - native_decide or decide でチェック

print("最適方式: 奇数核 + Syracuse 降下 + チャンク分割")
print()
print("10^7 の場合:")
print(f"  奇数件数: 5,000,000")
print(f"  チャンク (50K): {10**7 // 50000} 個")
print()

# 各チャンクでの計算量推定
# collatzAllReachBounded steps lo hi
# = hi-lo+1 件 x steps 回の collatzStep
# 50K x 700 = 35M 演算

steps_needed = 700
chunk = 50000
ops_per_chunk = chunk * steps_needed
print(f"  native_decide方式:")
print(f"    演算/チャンク: {ops_per_chunk:,} (~{ops_per_chunk/10**6:.0f}M)")
print(f"    推定ビルド時間/チャンク: 5-30秒 (native code)")
print(f"    総ビルド時間: {200 * 15 / 60:.0f}分 (並列ビルドで短縮可能)")
print()

# 奇数核方式ではどうか
# Syracuse反復のみ: 奇数 25K/チャンク x avg 5 steps = 125K 演算
odd_per_chunk = chunk // 2
avg_syr_steps = 5  # 自分より小さくなるまで
ops_odd = odd_per_chunk * avg_syr_steps
print(f"  奇数核方式:")
print(f"    奇数/チャンク: {odd_per_chunk:,}")
print(f"    平均Syracuseステップ: ~{avg_syr_steps}")
print(f"    演算/チャンク: {ops_odd:,} (~{ops_odd/10**6:.1f}M)")
print(f"    削減率: {ops_odd/ops_per_chunk*100:.1f}% (= {ops_per_chunk/ops_odd:.0f}x 高速化)")

# ===== 分析8: 実際のLeanコード構造提案 =====
print()
print("=" * 60)
print("分析8: 推奨Lean実装構造")
print("=" * 60)

print("""
推奨: native_decideチャンク拡張 + 奇数核最適化の組み合わせ

--- ファイル構造 ---

Unsolved/Collatz/StoppingTime/
  Verification.lean          -- 既存: n <= 10^6
  Verification10M.lean       -- 新規: n <= 10^7 のマスター定理
  Verification10M/
    Chunk001.lean            -- 1,000,001 ~ 1,050,000
    Chunk002.lean            -- 1,050,001 ~ 1,100,000
    ...
    Chunk180.lean            -- 9,950,001 ~ 10,000,000

各 ChunkXXX.lean:
```
import Unsolved.Collatz.StoppingTime.Verification

set_option linter.style.nativeDecide false in
theorem collatzAllReach_{lo}_{hi} :
    collatzAllReachBounded 700 {lo} {hi} = true := by
  native_decide
```

Verification10M.lean:
```
import all Chunk files

theorem collatzReaches_le_10000000 (n : Nat) (hn1 : n >= 1) (hn : n <= 10000000) :
    collatzReaches n := by
  by_cases h : n <= 1000000
  . exact collatzReaches_le_1000000 n hn1 h
  . push_neg at h
    -- case split by chunks
    ...
```

--- 最適化版: 奇数核+Syracuse ---

```lean
/-- Syracuse版: 全奇数を steps ステップで threshold 以下に落とせるか -/
def syracuseAllDescend (steps threshold lo hi : Nat) : Bool :=
  (List.range ((hi - lo) / 2 + 1)).all fun i =>
    let n := lo + 2 * i   -- odd numbers
    syracuseReachesBounded steps threshold n

/-- 健全性: syracuseAllDescend が true なら全奇数は到達可能 -/
theorem collatzReaches_of_syracuseDescend ...
```

--- 代替: メタプログラミング方式 ---

```lean
/-- elaborate時にコラッツ検証を実行するタクティク -/
syntax "collatz_verify" num num : tactic

macro_rules
| `(tactic| collatz_verify $lo $hi) => do
  -- elaborate 時に各 n について計算
  -- 証明項を直接構築
  ...
```
""")

# ===== 分析9: ビルド時間の実測推定 =====
print()
print("=" * 60)
print("分析9: 実測ベースの推定")
print("=" * 60)

# 現在の 50K native_decide のビルド時間を推定
# collatzAllReachBounded 600 950001 1000000 = true by native_decide
# 50,000 x 600 steps = 30M operations

# Python で同等の計算にかかる時間を計測
t0 = time.time()
count = 0
for n in range(950001, 1000001):
    current = n
    for _ in range(600):
        if current == 1:
            break
        current = collatz_step(current)
    count += 1
t1 = time.time()

python_time_50k = t1 - t0
print(f"Python 50K件 (950001-1000000, 600steps): {python_time_50k:.3f}秒")
# Lean native_decide は C compiled, おおよそ Python の 10-50x 速い
lean_native_est = python_time_50k / 20  # conservative
print(f"Lean native_decide 推定: ~{lean_native_est:.3f}秒/チャンク")

# 奇数核方式
t0 = time.time()
for n in range(950001, 1000001, 2):
    current = n
    while current >= n:
        current = syracuse(current)
t1 = time.time()

python_time_odd = t1 - t0
lean_odd_est = python_time_odd / 20
print(f"\n奇数核 Python 25K件 (950001-1000001, odd): {python_time_odd:.3f}秒")
print(f"奇数核 Lean推定: ~{lean_odd_est:.3f}秒/チャンク")
print(f"高速化比: {python_time_50k/python_time_odd:.1f}x")

# 10^7 全体の推定
total_chunks = 10**7 // 50000
total_native = total_chunks * lean_native_est
total_odd = total_chunks * lean_odd_est
print(f"\n10^7 全体推定:")
print(f"  native_decide方式: {total_chunks}チャンク x {lean_native_est:.3f}秒 = {total_native:.0f}秒 ({total_native/60:.1f}分)")
print(f"  奇数核方式: {total_chunks}チャンク x {lean_odd_est:.3f}秒 = {total_odd:.0f}秒 ({total_odd/60:.1f}分)")
print(f"  (並列ビルドで更に短縮可能)")

# ===== 最終まとめ =====
print()
print("=" * 60)
print("最終まとめ: 推奨設計")
print("=" * 60)

print("""
1. 推奨方式: native_decideチャンク拡張 (最も確実)
   - 既存 collatzReaches_le_1000000 を基盤に
   - 10^6 ~ 10^7 を 50K チャンクで 180 個に分割
   - 各チャンク: collatzAllReachBounded 700 lo hi = true by native_decide
   - Python コードジェネレータで .lean ファイルを自動生成
   - 並列ビルド (lake build -j N) で時間短縮

2. 奇数核最適化版 (次のステップ):
   - syracuseAllDescend を定義し奇数のみチェック
   - 計算量を約 1/10 に削減
   - ただし新しい健全性証明が必要

3. メタプログラミング方式 (発展):
   - Lean.Elab.Tactic でカスタムタクティク
   - elaborate時に計算、proof term を直接構築
   - kernel は構築済み term のみ検証 → native_decide 不要
   - 技術的難易度が高い

結論: まず方式1を実装し、確実に10^7を達成した後、
方式2・3で最適化するのが現実的。
""")
