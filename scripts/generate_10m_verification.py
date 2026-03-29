#!/usr/bin/env python3
"""
generate_10m_verification.py
==============================
10^7 検証用 Lean ファイル自動生成スクリプト (Phase 1 完全版)

collatzReaches_le_1000000 (既存) を基盤に、
1,000,001 ~ 10,000,000 を 50,000 件ずつ 180 チャンクに分割して
native_decide で検証する .lean ファイルを自動生成する。

使い方:
  python3 scripts/generate_10m_verification.py [--dry-run] [--chunk-size N] [--steps N]

  --dry-run     : ファイルを生成せず、計画を表示するだけ
  --chunk-size N: チャンクサイズ (デフォルト: 50000)
  --steps N     : collatzAllReachBounded のステップ数 (デフォルト: 750)
  --verify-steps: Python で最大 stopping time を事前計算して steps を自動決定
  --output-dir D: 出力ディレクトリ (デフォルト: Unsolved/Collatz/Verification10M)

生成ファイル:
  Verification10M/
    Chunk001.lean  -- collatzAllReach_1000001_1050000
    Chunk002.lean  -- collatzAllReach_1050001_1100000
    ...
    Chunk180.lean  -- collatzAllReach_9950001_10000000
    All.lean       -- 全チャンク統合 + collatzReaches_le_10000000

lakefile.toml の変更は不要 (Unsolved lean_lib が全サブモジュールを含むため)。
"""

import os
import sys
import argparse
import textwrap
import json
from datetime import datetime


# ============================================================
# 設定
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "Unsolved", "Collatz", "Verification10M")
DEFAULT_CHUNK_SIZE = 50_000
DEFAULT_STEPS = 750  # 10^7 までの最大 stopping time は 685、余裕を持って 750
RANGE_START = 1_000_001
RANGE_END = 10_000_000
EXISTING_UPPER = 1_000_000  # collatzReaches_le_1000000 の上界


# ============================================================
# ユーティリティ
# ============================================================

def collatz_step(n):
    """コラッツ関数の1ステップ"""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def stopping_time(n, max_steps=10000):
    """n の stopping time (1 に到達するまでのステップ数)"""
    current = n
    for i in range(max_steps):
        if current == 1:
            return i
        current = collatz_step(current)
    return -1


def compute_max_stopping_time(lo, hi, verbose=False):
    """[lo, hi] 範囲の最大 stopping time を計算"""
    max_st = 0
    max_n = lo
    for n in range(lo, hi + 1):
        st = stopping_time(n)
        if st > max_st:
            max_st = st
            max_n = n
    if verbose:
        print(f"  [{lo:>10,} - {hi:>10,}]: max stopping time = {max_st} (n = {max_n:,})")
    return max_st, max_n


def make_chunks(start, end, chunk_size):
    """チャンクのリスト [(chunk_id, lo, hi), ...] を生成"""
    chunks = []
    chunk_id = 1
    lo = start
    while lo <= end:
        hi = min(lo + chunk_size - 1, end)
        chunks.append((chunk_id, lo, hi))
        lo = hi + 1
        chunk_id += 1
    return chunks


# ============================================================
# Lean コード生成
# ============================================================

def generate_chunk_lean(chunk_id, lo, hi, steps):
    """1つのチャンクの .lean ファイル内容を生成"""
    return textwrap.dedent(f"""\
        -- 自動生成ファイル: generate_10m_verification.py
        -- チャンク {chunk_id:03d}: n in [{lo:,} .. {hi:,}]
        -- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        import Unsolved.Collatz.StoppingTime.Verification

        set_option maxHeartbeats 0 in
        set_option maxRecDepth 2000 in
        set_option linter.style.nativeDecide false in
        theorem collatzAllReach_{lo}_{hi} :
            collatzAllReachBounded {steps} {lo} {hi} = true := by
          native_decide
    """)


def generate_all_lean(chunks, steps):
    """統合ファイル All.lean の内容を生成

    全チャンクを import し、by_cases チェーンで
    collatzReaches_le_10000000 を証明する。

    既存 Verification.lean のパターン (push_neg + by_cases のネスト) に合わせる。
    ネスト深さを制限するため、10チャンクごとにサブ定理を生成する。
    """

    lines = []

    # ヘッダ
    lines.append(f"-- 自動生成ファイル: generate_10m_verification.py")
    lines.append(f"-- n <= 10,000,000 のコラッツ検証統合")
    lines.append(f"-- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"--")
    lines.append(f"-- 構成:")
    lines.append(f"--   基盤: collatzReaches_le_1000000 (既存, n <= 10^6)")
    lines.append(f"--   拡張: {len(chunks)} チャンク x {DEFAULT_CHUNK_SIZE:,} = {RANGE_START:,} ~ {RANGE_END:,}")
    lines.append(f"--   steps: {steps} (最大 stopping time 685 + 余裕)")
    lines.append("")

    # imports
    for chunk_id, lo, hi in chunks:
        lines.append(f"import Unsolved.Collatz.Verification10M.Chunk{chunk_id:03d}")
    lines.append("import Unsolved.Collatz.StoppingTime.Verification")
    lines.append("")

    # docstring
    batch_size = 10
    n_batches = (len(chunks) + batch_size - 1) // batch_size
    lines.append("/-!")
    lines.append("# コラッツ予想: n <= 10,000,000 の検証")
    lines.append("")
    lines.append("n <= 1,000,000 の検証 (collatzReaches_le_1000000) を基盤に、")
    lines.append(f"1,000,001 ~ 10,000,000 を {DEFAULT_CHUNK_SIZE:,} 件ずつのチャンクに分割して")
    lines.append("native_decide で検証する。")
    lines.append("")
    lines.append("## チャンク構成")
    lines.append(f"- {len(chunks)} チャンク (Chunk001 ~ Chunk{len(chunks):03d})")
    lines.append(f"- 各チャンク: collatzAllReachBounded {steps} lo hi = true")
    lines.append(f"- {n_batches} バッチ ({batch_size} チャンク/バッチ) のサブ定理で中間統合")
    lines.append("-/")
    lines.append("")

    # バッチ分割
    batches = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batches.append(batch)

    # サブ定理の生成 (既存 Verification.lean の push_neg + by_cases パターンに準拠)
    sub_theorem_info = []  # (batch_lo, batch_hi, thm_name)

    for batch_idx, batch in enumerate(batches):
        batch_lo = batch[0][1]
        batch_hi = batch[-1][2]
        thm_name = f"collatzReaches_{batch_lo}_{batch_hi}"
        sub_theorem_info.append((batch_lo, batch_hi, thm_name))

        lines.append(f"/-- {batch_lo:,} <= n <= {batch_hi:,} の検証 -/")
        lines.append(f"theorem {thm_name} (n : Nat) (hlo : n >= {batch_lo}) (hhi : n <= {batch_hi}) :")
        lines.append(f"    collatzReaches n := by")

        if len(batch) == 1:
            chunk_id, lo, hi = batch[0]
            lines.append(f"  exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) (by omega)")
        else:
            # 既存パターン: by_cases + push_neg のネスト
            for i, (chunk_id, lo, hi) in enumerate(batch):
                indent = "  " + "  " * i
                if i == len(batch) - 1:
                    # 最後のチャンク: hhi から直接
                    lines.append(f"{indent}exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) hhi")
                else:
                    boundary = hi
                    lines.append(f"{indent}by_cases h{i} : n <= {boundary}")
                    lines.append(f"{indent}. exact collatzReaches_of_allReachBounded collatzAllReach_{lo}_{hi} n (by omega) h{i}")
                    lines.append(f"{indent}. push_neg at h{i}")
        lines.append("")

    # 最終定理: collatzReaches_le_10000000
    lines.append("/-- n <= 10,000,000 の全自然数がコラッツ操作で 1 に到達する -/")
    lines.append("theorem collatzReaches_le_10000000 (n : Nat) (hn1 : n >= 1) (hn : n <= 10000000) :")
    lines.append("    collatzReaches n := by")

    # 既存の collatzReaches_le_1000000 をベースとした by_cases チェーン
    lines.append("  by_cases h1m : n <= 1000000")
    lines.append("  . exact collatzReaches_le_1000000 n hn1 h1m")
    lines.append("  . push_neg at h1m")

    for i, (batch_lo, batch_hi, thm_name) in enumerate(sub_theorem_info):
        indent = "    " + "  " * i
        if i == len(sub_theorem_info) - 1:
            lines.append(f"{indent}exact {thm_name} n (by omega) hn")
        else:
            lines.append(f"{indent}by_cases h_b{i} : n <= {batch_hi}")
            lines.append(f"{indent}. exact {thm_name} n (by omega) h_b{i}")
            lines.append(f"{indent}. push_neg at h_b{i}")

    lines.append("")
    lines.append("/-- コラッツ予想が n <= 10,000,000 で成り立つ (関数形式) -/")
    lines.append("theorem collatzConjectureR_verified_le_10000000 :")
    lines.append("    forall n : Nat, n >= 1 -> n <= 10000000 -> collatzReaches n :=")
    lines.append("  fun n hn1 hn => collatzReaches_le_10000000 n hn1 hn")
    lines.append("")

    return "\n".join(lines)


def generate_build_script(chunks, output_dir):
    """ビルドスクリプト (bash) を生成"""
    rel_dir = os.path.relpath(output_dir, BASE_DIR)

    content = textwrap.dedent(f"""\
        #!/bin/bash
        # 自動生成: generate_10m_verification.py
        # 10^7 検証のビルドスクリプト
        # 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        #
        # 使い方:
        #   bash scripts/build_10m_verification.sh          # 全チャンク順次ビルド
        #   bash scripts/build_10m_verification.sh 1 10     # Chunk001-010 のみ
        #   bash scripts/build_10m_verification.sh --parallel 4  # 4並列ビルド

        set -euo pipefail

        cd "{BASE_DIR}"

        TOTAL_CHUNKS={len(chunks)}
        START_CHUNK=${{1:-1}}
        END_CHUNK=${{2:-$TOTAL_CHUNKS}}
        PARALLEL=${{3:-1}}

        echo "=== Collatz 10^7 Verification Build ==="
        echo "  Chunks: $START_CHUNK to $END_CHUNK (of $TOTAL_CHUNKS)"
        echo "  Parallel: $PARALLEL"
        echo ""

        # まず依存関係 (Verification.lean) をビルド
        echo "[0/$TOTAL_CHUNKS] Building dependencies..."
        lake env lean Unsolved/Collatz/StoppingTime/Verification.lean 2>&1 | tail -1

        # 各チャンクをビルド
        build_chunk() {{
            local id=$1
            local padded=$(printf "%03d" $id)
            local file="{rel_dir}/Chunk${{padded}}.lean"

            if [ ! -f "$file" ]; then
                echo "  SKIP: $file (not found)"
                return 0
            fi

            local start_time=$(date +%s)
            echo -n "  [$id/$TOTAL_CHUNKS] Building Chunk${{padded}}..."

            if lake env lean "$file" 2>&1 | tail -1; then
                local end_time=$(date +%s)
                local elapsed=$((end_time - start_time))
                echo " OK (${{elapsed}}s)"
            else
                echo " FAILED"
                return 1
            fi
        }}

        FAILED=0
        for i in $(seq $START_CHUNK $END_CHUNK); do
            build_chunk $i || FAILED=$((FAILED + 1))
        done

        echo ""
        if [ $FAILED -eq 0 ]; then
            echo "=== All chunks built successfully ==="
            echo ""
            echo "Now building the master file..."
            lake env lean "{rel_dir}/All.lean" 2>&1 | tail -1
            echo "=== Done! collatzReaches_le_10000000 verified ==="
        else
            echo "=== $FAILED chunk(s) failed ==="
            exit 1
        fi
    """)
    return content


# ============================================================
# メインロジック
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="10^7 コラッツ検証用 Lean ファイル自動生成"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="ファイルを生成せず計画を表示")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE,
                        help=f"チャンクサイズ (デフォルト: {DEFAULT_CHUNK_SIZE:,})")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS,
                        help=f"collatzAllReachBounded のステップ数 (デフォルト: {DEFAULT_STEPS})")
    parser.add_argument("--verify-steps", action="store_true",
                        help="Python で最大 stopping time を事前計算")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="出力ディレクトリ")
    parser.add_argument("--first-n", type=int, default=None,
                        help="最初の N チャンクのみ生成 (テスト用)")
    parser.add_argument("--generate-sample", action="store_true",
                        help="最初の3チャンクのみ生成してサンプル表示")

    args = parser.parse_args()

    chunk_size = args.chunk_size
    steps = args.steps
    output_dir = args.output_dir

    # チャンク一覧を生成
    chunks = make_chunks(RANGE_START, RANGE_END, chunk_size)

    if args.first_n:
        chunks = chunks[:args.first_n]

    if args.generate_sample:
        chunks_for_gen = chunks[:3]
    else:
        chunks_for_gen = chunks

    # ステップ数の事前検証
    if args.verify_steps:
        print("=== ステップ数の事前検証 ===")
        print(f"  範囲: [{RANGE_START:,} - {RANGE_END:,}]")
        overall_max = 0
        overall_max_n = 0
        # 100万ごとにサンプリング
        for block_start in range(RANGE_START, RANGE_END + 1, 1_000_000):
            block_end = min(block_start + 999_999, RANGE_END)
            max_st, max_n = compute_max_stopping_time(block_start, block_end, verbose=True)
            if max_st > overall_max:
                overall_max = max_st
                overall_max_n = max_n
        print(f"\n  全体の最大 stopping time: {overall_max} (n = {overall_max_n:,})")
        recommended = overall_max + 65  # 余裕
        print(f"  推奨 steps: {recommended}")
        if steps < overall_max:
            print(f"  WARNING: 指定された steps={steps} は最大 stopping time {overall_max} より小さい!")
            steps = recommended
            print(f"  steps を {steps} に修正しました。")
        print()

    # 計画の表示
    print("=" * 70)
    print("  Collatz 10^7 Verification - Lean File Generator")
    print("=" * 70)
    print(f"  基盤: collatzReaches_le_1000000 (n <= {EXISTING_UPPER:,})")
    print(f"  拡張範囲: [{RANGE_START:,} - {RANGE_END:,}]")
    print(f"  チャンクサイズ: {chunk_size:,}")
    print(f"  チャンク数: {len(chunks)}")
    print(f"  ステップ数: {steps}")
    print(f"  出力ディレクトリ: {output_dir}")
    print()
    print(f"  生成ファイル:")
    print(f"    Chunk001.lean ~ Chunk{len(chunks):03d}.lean  ({len(chunks)} ファイル)")
    print(f"    All.lean                        (統合ファイル)")
    print(f"    合計: {len(chunks) + 1} ファイル")
    print()

    if args.generate_sample:
        print("--- サンプル: Chunk001.lean ---")
        print(generate_chunk_lean(1, chunks[0][1], chunks[0][2], steps))
        print("--- サンプル: All.lean (先頭 60 行) ---")
        all_content = generate_all_lean(chunks[:3], steps)
        for i, line in enumerate(all_content.split('\n')[:60]):
            print(line)
        print("  ...")
        print()

    if args.dry_run:
        print("[DRY RUN] ファイルは生成されません。")

        # サマリー JSON
        summary = {
            "mode": "dry-run",
            "range": [RANGE_START, RANGE_END],
            "chunk_size": chunk_size,
            "n_chunks": len(chunks),
            "steps": steps,
            "files_to_generate": len(chunks) + 1,
            "estimated_build_time_minutes": f"{len(chunks) * 10 / 60:.0f} - {len(chunks) * 30 / 60:.0f}",
            "chunks": [
                {"id": cid, "lo": lo, "hi": hi}
                for cid, lo, hi in chunks[:5]
            ] + [{"note": f"... ({len(chunks) - 5} more)"}] if len(chunks) > 5 else [
                {"id": cid, "lo": lo, "hi": hi}
                for cid, lo, hi in chunks
            ],
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    # ファイル生成
    os.makedirs(output_dir, exist_ok=True)

    generated = []

    # チャンクファイル
    for chunk_id, lo, hi in chunks_for_gen:
        filename = f"Chunk{chunk_id:03d}.lean"
        filepath = os.path.join(output_dir, filename)
        content = generate_chunk_lean(chunk_id, lo, hi, steps)
        with open(filepath, 'w') as f:
            f.write(content)
        generated.append(filepath)

    # 統合ファイル
    all_filepath = os.path.join(output_dir, "All.lean")
    all_content = generate_all_lean(chunks, steps)
    with open(all_filepath, 'w') as f:
        f.write(all_content)
    generated.append(all_filepath)

    # ビルドスクリプト
    build_script_path = os.path.join(BASE_DIR, "scripts", "build_10m_verification.sh")
    build_content = generate_build_script(chunks, output_dir)
    with open(build_script_path, 'w') as f:
        f.write(build_content)
    os.chmod(build_script_path, 0o755)
    generated.append(build_script_path)

    print(f"  生成完了: {len(generated)} ファイル")
    for f in generated[:5]:
        print(f"    {os.path.relpath(f, BASE_DIR)}")
    if len(generated) > 5:
        print(f"    ... ({len(generated) - 5} more)")
    print(f"    {os.path.relpath(generated[-2], BASE_DIR)}")
    print(f"    {os.path.relpath(generated[-1], BASE_DIR)}")
    print()
    print("  次のステップ:")
    print(f"    1. テストビルド: lake env lean {os.path.relpath(generated[0], BASE_DIR)}")
    print(f"    2. 全体ビルド:  bash scripts/build_10m_verification.sh")
    print(f"    3. 統合ビルド:  lake env lean {os.path.relpath(all_filepath, BASE_DIR)}")


if __name__ == "__main__":
    main()
