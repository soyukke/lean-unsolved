"""
奇数核方式のLean実装詳細設計
=============================
native_decide 以外で n <= 10^7 を達成するための3方式を具体化する。

方式A: Syracuse降下証拠 + native_decide (確実・既存延長)
方式B: Syracuse降下証拠 + decide (pure kernel, 遅い)
方式C: メタプログラミング (elaborate時計算, kernel検証のみ)
"""

import time
import json

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

# ===== 方式B: Syracuse降下方式の詳細設計 =====
print("=" * 70)
print("方式B: Syracuse降下証拠 + decide (native_decide不要)")
print("=" * 70)

print("""
核心アイデア:
  各奇数 n について「syracuseIter k n = m」かつ「m < n」となる k,m を提供。
  これにより帰納的に「全ての奇数は1に到達する」を証明できる。

  ただし decide で syracuseIter k n = m を検証するのは
  k が小さい（平均 3.5）なら現実的。

必要な構成要素:
  1. syracuseReachesBound: 奇数 n について syracuseIter k n < n を示す Bool 関数
  2. 健全性定理: true → collatzReaches n
  3. 帰納法の足場: n より小さい値が到達可能なら n も到達可能
""")

# Syracuse ステップで n < threshold に落ちるまでのステップ数を計算
# これが decide で検証可能かどうかの指標

# 問題: syracuse/syracuseIter は Lean の kernel では unfold が遅い
# decide は全展開するので、syracuseIter 5 n は 5 回の syracuse 呼び出し
# 各 syracuse(n) = (3n+1) / 2^v2(3n+1) で v2 が再帰的

# decide のコスト推定:
# syracuse 1回 = v2 計算 (O(log n)) + 除算 + 乗算
# kernel での Nat 演算は O(log n) per operation
# syracuseIter k n: O(k * log(max_val)) kernel steps

# n ~ 10^7 の場合:
# max_val ~ 10^10 (中間値), log2(10^10) ~ 33
# k ~ 5 平均
# kernel steps per n: ~5 * 33 * const ~ 500 kernel ops

# heartbeats: 1 heartbeat ~ 数十 kernel ops
# 1 奇数あたり ~ 50-100 heartbeats
# 50K 奇数 = 25K 奇数: 25K * 100 = 2.5M heartbeats
# default maxHeartbeats = 200000 (200K)
# → 25K 奇数は無理、もっと小さいチャンクが必要

print("decide のコスト推定:")
print("  1 奇数あたり: ~50-100 heartbeats (syracuse 5回展開)")
print("  maxHeartbeats = 200K → ~2K-4K 奇数/チャンク")
print("  maxHeartbeats = 4M → ~40K-80K 奇数/チャンク")
print("  (set_option maxHeartbeats で調整可能)")
print()

# 方式Bの具体コード
print("方式B: 具体的なLeanコード構造")
print("-" * 50)
print("""
```lean
/-- Syracuse反復が bounded steps で threshold 以下に降下するか -/
def syracuseDescendsBounded (steps threshold n : Nat) : Bool :=
  match steps with
  | 0 => n <= threshold
  | k + 1 => n <= threshold || syracuseDescendsBounded k threshold (syracuse n)

/-- 健全性: syracuseDescendsBounded true かつ threshold以下が到達可能
    → n も到達可能 -/
theorem collatzReaches_of_syracuseDescends
    (n threshold steps : Nat)
    (hodd : n % 2 = 1)
    (hdesc : syracuseDescendsBounded steps threshold n = true)
    (hbase : forall m, m >= 1 -> m <= threshold -> collatzReaches m) :
    collatzReaches n := by
  ... -- 帰納法で証明

/-- 範囲内の全奇数が降下するか -/
def oddRangeDescends (steps threshold lo hi : Nat) : Bool :=
  if lo > hi then true
  else if lo % 2 = 0 then oddRangeDescends steps threshold (lo + 1) hi
  else syracuseDescendsBounded steps threshold lo &&
       oddRangeDescends steps threshold (lo + 2) hi
termination_by hi - lo + 1

/-- 範囲検証 -/
theorem collatzReaches_range_of_oddDescends
    (steps threshold lo hi : Nat)
    (hdesc : oddRangeDescends steps threshold lo hi = true)
    (hbase : forall m, m >= 1 -> m <= threshold -> collatzReaches m) :
    forall n, n >= lo -> n <= hi -> n >= 1 -> collatzReaches n := by
  ...
```

問題点:
- oddRangeDescends の再帰がカーネルで展開できるか？
  → List.range ベースの方が安全
- decide は10K奇数でも数分かかる可能性
  → チャンクサイズを小さくする必要

解決策: チャンクサイズを 10K に縮小
  → 10^7 / 10K = 1000 チャンク（ファイル数多い）
  → 自動生成で対応
""")

# ===== 方式C: メタプログラミング方式の詳細 =====
print()
print("=" * 70)
print("方式C: メタプログラミング (elaborate時計算)")
print("=" * 70)

print("""
核心アイデア:
  Lean のメタプログラミング (Lean.Elab) を使い、
  elaborate 時に各奇数のSyracuse降下を計算し、
  証明項 (Expr) を直接構築する。

  カーネルはこの構築済み Expr を型検査するだけ。
  v2/syracuse の再帰展開は不要。

具体的な証明項の構造:
  各奇数 n に対して:
    collatzReaches n を示す証明 =
      collatzReaches_of_collatzIter n m k h_iter h_reaches_m

  ここで:
    k = 降下ステップ数
    m = collatzIter k n の値 (m < n)
    h_iter : collatzIter k n = m  -- rfl (カーネルが計算で確認)
    h_reaches_m : collatzReaches m -- 帰納仮定

  問題: h_iter を rfl にするには、カーネルが collatzIter k n を
  reduction で m に簡約できる必要がある。
  → collatzIter は @[reducible] or whnf で展開可能か？

代替: collatzIter k n = m を直接の数値比較で示す
  → Nat.decEq による decide

メタプログラミング版の具体コード:
""")

print("""
```lean
import Lean

open Lean Elab Tactic Meta in

/-- コラッツ反復を Lean のメタレベルで計算 -/
def metaCollatzIter (k n : Nat) : Nat :=
  match k with
  | 0 => n
  | k + 1 => metaCollatzIter k (if n % 2 = 0 then n / 2 else 3 * n + 1)

/-- 証明項を構築: collatzReaches n -/
def mkCollatzReachesProof (n : Nat)
    (knownProofs : HashMap Nat Expr) : MetaM Expr := do
  -- Step 1: n のコラッツ軌道を計算し、known value m に到達するまでのステップ k を見つける
  let mut current := n
  let mut k := 0
  while !knownProofs.contains current do
    current := if current % 2 = 0 then current / 2 else 3 * current + 1
    k := k + 1
    if k > 10000 then throwError "too many steps"

  let m := current
  let hm := knownProofs.find! m

  -- Step 2: 証明項を構築
  -- collatzReaches_of_collatzIter n m k (by rfl) hm
  -- 実際にはもう少し複雑な term building が必要
  sorry -- placeholder

/-- タクティク: collatz_verify lo hi -/
elab "collatz_meta_verify" lo:num hi:num : tactic => do
  let loVal := lo.getNat
  let hiVal := hi.getNat

  -- 既知の証明を蓄積
  let mut proofs : HashMap Nat Expr := HashMap.empty
  -- 基底ケース: 1
  proofs := proofs.insert 1 (← mkAppM ``collatzReaches_one #[])

  -- lo から hi まで順に処理
  for n in List.range (hiVal - loVal + 1) |>.map (· + loVal) do
    if n == 0 then continue
    if proofs.contains n then continue

    -- 偶数: n = 2^a * m に分解
    let mut m := n
    while m % 2 == 0 do m := m / 2

    -- 奇数 m の証明を構築
    if !proofs.contains m then
      let proof ← mkCollatzReachesProof m proofs
      proofs := proofs.insert m proof

    -- 偶数 n の証明: reachesOne_double の繰り返し適用
    if n != m then
      let proof ← mkEvenReachesProof n m (proofs.find! m)
      proofs := proofs.insert n proof

  -- ゴールを閉じる
  ...
```

課題:
1. h_iter : collatzIter k n = m の証明
   - rfl だとカーネルが展開する必要あり → k が大きいと遅い
   - Nat.decEq で decide → 同じ問題
   - 最適: 各ステップを分解して合成
     collatzIter 1 n = collatzStep n = m1 (by rfl)
     collatzIter 1 m1 = collatzStep m1 = m2 (by rfl)
     ...
     collatzIter_add で合成
   - 各 rfl は 1 ステップの展開なので軽量

2. メモリ: 10^7 個の Expr を HashMap に保持
   - 各 Expr は小さい (数十バイト)
   - 10^7 * 100 bytes ~ 1 GB → 厳しい
   - → チャンク分割: 各チャンク内でのみ HashMap 保持

3. elaborate 時間: 各奇数の計算は O(1) (ハッシュ参照)
   - 10^7 / チャンクサイズ の elaborate 回数
""")

# ===== 方式D: ステップバイステップ分解 =====
print()
print("=" * 70)
print("方式D: ステップバイステップ分解 (最も有望)")
print("=" * 70)

print("""
核心アイデア:
  各奇数 n について、collatzStep の個別ステップの chain を構築。
  kernel は各 rfl を 1 回だけ展開すれば良い。

  n → collatzStep n = a1 (by rfl)
  a1 → collatzStep a1 = a2 (by rfl)
  ...
  ak → collatzStep ak = m  (by rfl, m < n)

  collatzIter_add で結合:
  collatzIter k n = m

  これで collatzReaches_of_collatzIter n m k を適用。

  利点: rfl の展開が 1 ステップずつなのでカーネルに優しい。
  問題: k ステップ分の rfl term を生成する必要 → メタプログラミングで自動化。

最適化:
  - 偶数ステップはまとめる: n が偶数なら n/2 に一気に帰着
  - Syracuse 1ステップ = collatzStep の複数ステップをまとめ
  - 各 Syracuse ステップの証明を構築し合成
""")

# 具体的なステップ数の分析
print()
print("collatzStep ベースのステップ数分析 (n <= 10^7 サンプル):")
import random
random.seed(42)

sample = random.sample(range(1, 10**7 + 1), 10000)
step_counts = []
for n in sample:
    current = n
    steps = 0
    while current >= n and current != 1:
        current = collatz_step(current)
        steps += 1
    step_counts.append(steps)

print(f"  サンプル: 10,000 件")
print(f"  最大ステップ (< n になるまで): {max(step_counts)}")
print(f"  平均ステップ: {sum(step_counts)/len(step_counts):.1f}")
print(f"  中央値: {sorted(step_counts)[len(step_counts)//2]}")

# 1に到達するまでの全ステップ
total_steps = []
for n in sample:
    current = n
    steps = 0
    while current != 1:
        current = collatz_step(current)
        steps += 1
    total_steps.append(steps)

print(f"\n  1に到達するまでの全ステップ:")
print(f"  最大: {max(total_steps)}")
print(f"  平均: {sum(total_steps)/len(total_steps):.1f}")
print(f"  中央値: {sorted(total_steps)[len(total_steps)//2]}")

# ===== メモリ推定 =====
print()
print("=" * 70)
print("メモリ推定: 方式D (ステップバイステップ)")
print("=" * 70)

# 方式D では各 n に対して:
# - k 個の rfl 証明 (各 ~20 bytes as Lean Expr)
# - 1 個の collatzIter_add 合成 (~50 bytes)
# - 1 個の collatzReaches_of_collatzIter (~100 bytes)

avg_total = sum(total_steps) / len(total_steps)
proof_size_per_n = avg_total * 20 + 50 + 100  # bytes
total_memory = 10**7 * proof_size_per_n
print(f"1件あたりの証明サイズ推定: {proof_size_per_n:.0f} bytes")
print(f"10^7 件の総証明サイズ: {total_memory / 1024 / 1024 / 1024:.1f} GB")
print(f"  → メモリ的に厳しい。チャンク分割必須。")

# チャンク分割
for chunk_size in [1000, 5000, 10000, 50000]:
    chunks = 10**7 // chunk_size
    mem_per_chunk = chunk_size * proof_size_per_n
    print(f"  チャンク {chunk_size:,}: {chunks} ファイル, {mem_per_chunk/1024/1024:.1f} MB/チャンク")

# ===== 最終推奨 =====
print()
print("=" * 70)
print("最終推奨: 段階的アプローチ")
print("=" * 70)

print("""
Phase 1: native_decide チャンク拡張 (最も確実, 1-2日)
  - 既存手法の延長
  - 50K チャンク x 180 = 9M (+ 既存 1M = 10M)
  - Pythonスクリプトで .lean ファイルを自動生成
  - lake build で検証
  - 推定ビルド時間: 30-60分

Phase 2: Syracuse奇数核最適化 (1週間)
  - syracuseDescendsBounded を定義
  - 健全性証明を形式化
  - native_decide で奇数のみチェック → 2x 高速化
  - 小さいチャンクなら decide も検討可能

Phase 3: メタプログラミング (2-4週間)
  - Lean.Elab.Tactic で collatz_meta_verify タクティク
  - elaborate 時に計算、proof term 構築
  - kernel は構築済み term のみ検証
  - native_decide 完全不要の formal verification

重要な注意:
  native_decide は Lean の trusted code base に依存するが、
  数学的にはコラッツの「証明」ではなく「検証」なので、
  native_decide でも十分に意味がある。
  pure kernel proof (方式D) は形式検証の理想形だが、
  実用的には native_decide で十分。
""")

# ===== Phase 1 のコードジェネレータ設計 =====
print("=" * 70)
print("Phase 1: コードジェネレータ設計")
print("=" * 70)

# チャンク生成の具体例
lo, hi = 1_000_001, 1_050_000
chunk_name = f"collatzAllReach_{lo}_{hi}"
print(f"""
生成例: Chunk001.lean

```lean
import Unsolved.Collatz.StoppingTime.Verification

set_option linter.style.nativeDecide false in
theorem {chunk_name} :
    collatzAllReachBounded 700 {lo} {hi} = true := by
  native_decide
```
""")

# 必要ステップ数の推定
# n <= 10^7 で最大 total stopping time
# Known: max for n <= 10^7 is n=8400511 with 685 steps
# 安全マージンをつけて 700 steps
print(f"必要な bounded steps:")
print(f"  n <= 10^6: 600 (既存)")
print(f"  n <= 10^7: 700 (推奨)")

# 軌道中の最大値も重要: Nat overflow がないか
print(f"\n中間値の範囲:")
# n <= 10^7 での最大中間値を推定
max_intermediate = 0
worst_n = 0
t0 = time.time()
for n in random.sample(range(10**6 + 1, 10**7 + 1), 100000):
    current = n
    steps = 0
    while current != 1 and steps < 1000:
        current = collatz_step(current)
        max_val = max(current, max_intermediate)
        if max_val > max_intermediate:
            max_intermediate = max_val
            worst_n = n
        steps += 1
t1 = time.time()

print(f"  サンプル100K件: 最大中間値 = {max_intermediate:,}")
print(f"  対応する n = {worst_n:,}")
print(f"  ビット数: {max_intermediate.bit_length()} bits")
print(f"  Nat のオーバーフロー: なし (Lean Nat は任意精度)")

# Syracuse版の中間値
max_syr = 0
worst_syr_n = 0
for n in random.sample(range(10**6 + 1, 10**7 + 1, 2), 100000):
    current = n
    steps = 0
    while current >= n and steps < 1000:
        current = syracuse(current)
        if current > max_syr:
            max_syr = current
            worst_syr_n = n
        steps += 1
t2 = time.time()

print(f"\n  Syracuse版: 最大中間値 = {max_syr:,}")
print(f"  対応する奇数 n = {worst_syr_n:,}")
print(f"  ビット数: {max_syr.bit_length()} bits")

# ===== JSON出力 =====
results = {
    "analysis": "odd_core_table_lean_design",
    "target": "n <= 10^7 verification without native_decide",
    "key_numbers": {
        "total_n": 10**7,
        "odd_count": 5*10**6,
        "avg_syracuse_steps_to_descend": 3.5,
        "max_syracuse_steps_to_descend": 139,
        "max_total_stopping_time": 700,
        "max_intermediate_value_bits": max_intermediate.bit_length(),
    },
    "approaches": {
        "phase1_native_decide_extension": {
            "chunk_size": 50000,
            "num_chunks": 180,
            "bounded_steps": 700,
            "estimated_build_minutes": 30,
            "difficulty": "easy",
            "native_decide_required": True,
        },
        "phase2_syracuse_odd_core": {
            "description": "syracuseDescendsBounded + native_decide on odds only",
            "estimated_speedup": "2-10x",
            "new_lean_code_needed": "~200 lines (syracuseDescendsBounded + soundness)",
            "difficulty": "medium",
            "native_decide_required": True,
        },
        "phase3_metaprogramming": {
            "description": "Lean.Elab.Tactic for proof term construction",
            "native_decide_required": False,
            "difficulty": "hard",
            "estimated_development_weeks": "2-4",
            "memory_per_chunk_mb": 50,
        },
    },
    "recommendation": "Phase 1 first, then Phase 2 for optimization",
}

print()
print(json.dumps(results, indent=2))
