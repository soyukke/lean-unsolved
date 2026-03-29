"""
Phase 1: native_decide チャンク拡張のコードジェネレータ
Phase 2: Syracuse奇数核方式のLeanコードスケッチ生成

10^7 検証用の .lean ファイルを自動生成する。
"""

import os
import json

BASE_DIR = "/Users/soyukke/study/lean-unsolved"
CHUNK_DIR = os.path.join(BASE_DIR, "Unsolved/Collatz/StoppingTime/Verification10M")

# ===== Phase 1: native_decide チャンク生成 =====

def generate_chunk_file(chunk_id, lo, hi, steps=700):
    """1つのチャンクファイルを生成"""
    content = f"""import Unsolved.Collatz.StoppingTime.Verification

set_option linter.style.nativeDecide false in
theorem collatzAllReach_{lo}_{hi} :
    collatzAllReachBounded {steps} {lo} {hi} = true := by
  native_decide
"""
    return content

def generate_master_file(chunks):
    """マスターファイル (全チャンクを import して統合) を生成"""
    imports = []
    for chunk_id, lo, hi in chunks:
        imports.append(f"import Unsolved.Collatz.StoppingTime.Verification10M.Chunk{chunk_id:03d}")

    # by_cases チェーン生成
    cases = []
    for i, (chunk_id, lo, hi) in enumerate(chunks):
        if i == 0:
            cases.append(f"""    by_cases h{hi} : n <= {hi}
    . exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) h{hi}""")
        elif i == len(chunks) - 1:
            cases.append(f"""    . exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) hn""")
        else:
            cases.append(f"""    . push_neg at h{chunks[i-1][2]}
      by_cases h{hi} : n <= {hi}
      . exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) h{hi}""")

    cases_code = "\n".join(cases)

    content = f"""-- 自動生成ファイル: n <= 10^7 のコラッツ検証
{chr(10).join(imports)}
import Unsolved.Collatz.StoppingTime.Verification

/-!
# コラッツ予想: n <= 10,000,000 の検証

n <= 1,000,000 の検証 (既存) を基盤に、
1,000,001 ~ 10,000,000 を 50,000 件ずつのチャンクに分割して
native_decide で検証する。
-/

theorem collatzReaches_le_10000000 (n : Nat) (hn1 : n >= 1) (hn : n <= 10000000) :
    collatzReaches n := by
  by_cases h1m : n <= 1000000
  . exact collatzReaches_le_1000000 n hn1 h1m
  . push_neg at h1m
{cases_code}
"""
    return content

# 生成するチャンクのリスト
chunks = []
chunk_id = 1
lo = 1_000_001
chunk_size = 50_000

while lo <= 10_000_000:
    hi = min(lo + chunk_size - 1, 10_000_000)
    chunks.append((chunk_id, lo, hi))
    lo = hi + 1
    chunk_id += 1

print(f"Phase 1: {len(chunks)} チャンクを生成")
print(f"  最初: Chunk{chunks[0][0]:03d} ({chunks[0][1]:,} ~ {chunks[0][2]:,})")
print(f"  最後: Chunk{chunks[-1][0]:03d} ({chunks[-1][1]:,} ~ {chunks[-1][2]:,})")

# ディレクトリ作成 (dry run)
print(f"\n出力ディレクトリ: {CHUNK_DIR}")
print(f"生成ファイル数: {len(chunks)} + 1 (master) = {len(chunks) + 1}")

# サンプル出力
print("\n--- Chunk001.lean (サンプル) ---")
print(generate_chunk_file(1, 1_000_001, 1_050_000))

print("--- Verification10M.lean (マスター, 先頭部分) ---")
master = generate_master_file(chunks[:3])
for line in master.split('\n')[:30]:
    print(line)
print("  ...")

# ===== Phase 2: Syracuse奇数核方式のスケッチ =====
print()
print("=" * 70)
print("Phase 2: Syracuse奇数核方式のLeanコードスケッチ")
print("=" * 70)

syracuse_lean_code = """
import Unsolved.Collatz.Defs
import Unsolved.Collatz.StoppingTime.Defs

/-!
# Syracuse 奇数核テーブル方式

各奇数 n に対して、Syracuse反復で n より小さい値に到達するステップ数を
外部計算し、帰納法で collatzReaches を証明する。

## 主要定義
- `syracuseDescends`: Syracuse反復で threshold 以下に降下するか
- `allOddsDescend`: 範囲内の全奇数が降下するか

## 主要定理
- `collatzReaches_of_syracuseDescends`: 降下 → 到達可能
- `collatzReaches_odd_of_allDescend`: 範囲内の全奇数が到達可能
- `collatzReaches_of_odd_core`: 偶数を奇数核に帰着
-/

/-! ## Syracuse 降下判定 -/

/-- Syracuse反復が bounded steps で threshold 以下に降下するか判定 -/
def syracuseDescends (steps threshold n : Nat) : Bool :=
  match steps with
  | 0 => n <= threshold
  | k + 1 => n <= threshold || syracuseDescends k threshold (syracuse n)

/-- 範囲内の全奇数が降下するか判定 -/
def allOddsDescend (steps threshold lo hi : Nat) : Bool :=
  (List.range ((hi - lo + 2) / 2)).all fun i =>
    let n := lo + 2 * i + (if lo % 2 = 0 then 1 else 0)
    syracuseDescends steps threshold n

/-! ## 健全性証明 -/

/-- Syracuse反復でthreshold以下に降下し、threshold以下が全て到達可能なら、
    n も到達可能 -/
theorem collatzReaches_of_syracuseDescends
    (n threshold steps : Nat)
    (hn_odd : n % 2 = 1)
    (hn_pos : n >= 1)
    (hdesc : syracuseDescends steps threshold n = true)
    (hbase : forall m, m >= 1 -> m <= threshold -> collatzReaches m) :
    collatzReaches n := by
  induction steps generalizing n with
  | zero =>
    simp only [syracuseDescends, Nat.ble_eq, decide_eq_true_eq] at hdesc
    exact hbase n hn_pos hdesc
  | succ k ih =>
    simp only [syracuseDescends, Bool.or_eq_true, Nat.ble_eq, decide_eq_true_eq] at hdesc
    rcases hdesc with hdesc | hdesc
    . exact hbase n hn_pos hdesc
    . -- syracuseDescends k threshold (syracuse n) = true
      -- syracuse n は奇数
      -- collatzReaches (syracuse n) を ih で示す
      -- collatzReaches (syracuse n) → collatzReaches n
      sorry -- 要: syracuse n が奇数であること + reachesOne_of_syracuse の逆

/-- 偶数を奇数核に帰着: n = 2^a * m (m 奇数) のとき
    collatzReaches m → collatzReaches n -/
theorem collatzReaches_of_odd_core (n m a : Nat)
    (hm_odd : m % 2 = 1)
    (hm_pos : m >= 1)
    (hn_eq : n = 2^a * m)
    (hm_reaches : collatzReaches m) :
    collatzReaches n := by
  sorry -- 要: reachesOne_double の繰り返し適用

/-- 範囲内の全数が到達可能 -/
theorem collatzReaches_range_of_allOddsDescend
    (steps threshold lo hi : Nat)
    (hdesc : allOddsDescend steps threshold lo hi = true)
    (hbase : forall m, m >= 1 -> m <= threshold -> collatzReaches m) :
    forall n, n >= lo -> n <= hi -> n >= 1 -> collatzReaches n := by
  sorry -- 各 n を奇数核に分解し、allOddsDescend から降下を抽出
"""

print(syracuse_lean_code)

# ===== Phase 3: メタプログラミング方式のスケッチ =====
print()
print("=" * 70)
print("Phase 3: メタプログラミング方式のLeanコードスケッチ")
print("=" * 70)

meta_lean_code = """
import Lean
import Unsolved.Collatz.Defs
import Unsolved.Collatz.StoppingTime.Defs

/-!
# コラッツ検証メタプログラミングタクティク

elaborate 時にコラッツ軌道を計算し、証明項を直接構築する。
kernel は構築済みの proof term のみ型検査する。

## 設計
1. 各奇数 n について、collatzStep を繰り返して 1 または既知値 m に到達
2. 各ステップの等式 collatzStep ai = ai+1 を rfl で証明
3. collatzIter_add で結合して collatzIter k n = m
4. collatzReaches_of_collatzIter で collatzReaches n を得る

## 最適化
- 偶数は 2^a * m (m奇数) に分解して m の証明から構築
- Syracuse ステップ単位でまとめて intermediate proof を削減
-/

open Lean Elab Term Meta

/-- Meta-level collatz step computation -/
private def metaCollatzStep (n : Nat) : Nat :=
  if n % 2 = 0 then n / 2 else 3 * n + 1

/-- Meta-level: n のコラッツ軌道を計算し、1に到達するまでの
    全ステップと中間値のリストを返す -/
private def computeCollatzOrbit (n : Nat) (maxSteps : Nat := 10000) :
    Option (List Nat) := do
  let mut orbit := [n]
  let mut current := n
  for _ in [:maxSteps] do
    if current == 1 then return some orbit
    current := metaCollatzStep current
    orbit := orbit ++ [current]
  none

/-- 証明項の構築: collatzIter 1 n = collatzStep n (by rfl) -/
private def mkCollatzIterOneProof (n : Expr) : MetaM Expr := do
  -- 型: collatzIter 1 n = collatzStep n
  -- 証明: rfl (カーネルが collatzIter (0+1) n を collatzIter 0 (collatzStep n) に簡約)
  mkAppM ``Eq.refl #[← mkAppM ``collatzStep #[n]]

/-- カスタムタクティク: コラッツ検証を elaborate 時に実行 -/
elab "collatz_verify_meta " lo:num " " hi:num : tactic => do
  let loVal := lo.getNat
  let hiVal := hi.getNat

  -- ゴール: forall n, n >= lo -> n <= hi -> n >= 1 -> collatzReaches n
  let goal ← getMainGoal

  -- 各 n について証明を構築
  -- (実際の実装は省略 - ここではアーキテクチャのみ示す)

  logInfo m!"collatz_verify_meta: verifying {loVal} to {hiVal}"
  sorry
"""

print(meta_lean_code)

# ===== 最終サマリー =====
print()
print("=" * 70)
print("全体サマリー")
print("=" * 70)

summary = {
    "phase1": {
        "name": "native_decide chunk extension",
        "files_to_generate": len(chunks) + 1,
        "native_decide": True,
        "kernel_proof": False,
        "difficulty": "easy (1-2 days)",
        "build_time_estimate": "30-60 min",
    },
    "phase2": {
        "name": "Syracuse odd core + native_decide",
        "new_lean_definitions": ["syracuseDescends", "allOddsDescend", "collatzReaches_of_odd_core"],
        "native_decide": True,
        "kernel_proof": False,
        "difficulty": "medium (1 week)",
        "speedup_vs_phase1": "2-10x",
    },
    "phase3": {
        "name": "Metaprogramming (elaborate-time computation)",
        "native_decide": False,
        "kernel_proof": True,
        "difficulty": "hard (2-4 weeks)",
        "memory_concern": "chunk splitting needed (50K per chunk)",
        "key_challenge": "constructing proof terms for collatzIter k n = m without kernel re-computation",
    },
}

print(json.dumps(summary, indent=2, ensure_ascii=False))
