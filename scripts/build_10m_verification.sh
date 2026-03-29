#!/bin/bash
# 自動生成: generate_10m_verification.py
# 10^7 検証のビルドスクリプト
# 生成日時: 2026-03-29 23:18:07
#
# 使い方:
#   bash scripts/build_10m_verification.sh          # 全チャンク順次ビルド
#   bash scripts/build_10m_verification.sh 1 10     # Chunk001-010 のみ
#   bash scripts/build_10m_verification.sh --parallel 4  # 4並列ビルド

set -euo pipefail

cd "/Users/soyukke/study/lean-unsolved"

TOTAL_CHUNKS=180
START_CHUNK=${1:-1}
END_CHUNK=${2:-$TOTAL_CHUNKS}
PARALLEL=${3:-1}

echo "=== Collatz 10^7 Verification Build ==="
echo "  Chunks: $START_CHUNK to $END_CHUNK (of $TOTAL_CHUNKS)"
echo "  Parallel: $PARALLEL"
echo ""

# まず依存関係 (Verification.lean) をビルド
echo "[0/$TOTAL_CHUNKS] Building dependencies..."
lake env lean Unsolved/Collatz/StoppingTime/Verification.lean 2>&1 | tail -1

# 各チャンクをビルド
build_chunk() {
    local id=$1
    local padded=$(printf "%03d" $id)
    local file="Unsolved/Collatz/Verification10M/Chunk${padded}.lean"

    if [ ! -f "$file" ]; then
        echo "  SKIP: $file (not found)"
        return 0
    fi

    local start_time=$(date +%s)
    echo -n "  [$id/$TOTAL_CHUNKS] Building Chunk${padded}..."

    if lake env lean "$file" 2>&1 | tail -1; then
        local end_time=$(date +%s)
        local elapsed=$((end_time - start_time))
        echo " OK (${elapsed}s)"
    else
        echo " FAILED"
        return 1
    fi
}

FAILED=0
for i in $(seq $START_CHUNK $END_CHUNK); do
    build_chunk $i || FAILED=$((FAILED + 1))
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo "=== All chunks built successfully ==="
    echo ""
    echo "Now building the master file..."
    lake env lean "Unsolved/Collatz/Verification10M/All.lean" 2>&1 | tail -1
    echo "=== Done! collatzReaches_le_10000000 verified ==="
else
    echo "=== $FAILED chunk(s) failed ==="
    exit 1
fi
