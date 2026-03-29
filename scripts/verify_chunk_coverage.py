#!/usr/bin/env python3
"""
verify_chunk_coverage.py
========================
180チャンクのカバレッジ整合性を検証するスクリプト。
各チャンクが [1,000,001 .. 10,000,000] を隙間なくカバーしていることを確認する。
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK_DIR = os.path.join(BASE_DIR, "Unsolved", "Collatz", "Verification10M")

def main():
    # チャンクファイルを読み込み
    chunks = []
    for fname in sorted(os.listdir(CHUNK_DIR)):
        if not fname.startswith("Chunk") or not fname.endswith(".lean"):
            continue
        fpath = os.path.join(CHUNK_DIR, fname)
        with open(fpath, 'r') as f:
            content = f.read()

        # 定理名から lo, hi を抽出
        m = re.search(r'collatzAllReach_(\d+)_(\d+)', content)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            chunks.append((fname, lo, hi))

    print(f"チャンクファイル数: {len(chunks)}")

    # ソート
    chunks.sort(key=lambda x: x[1])

    # カバレッジ検証
    expected_lo = 1_000_001
    errors = []
    for fname, lo, hi in chunks:
        if lo != expected_lo:
            errors.append(f"  GAP: expected lo={expected_lo:,} but {fname} starts at {lo:,}")
        if hi < lo:
            errors.append(f"  ERROR: {fname} has hi={hi:,} < lo={lo:,}")
        expected_lo = hi + 1

    if expected_lo - 1 != 10_000_000:
        errors.append(f"  END: expected last hi=10,000,000 but got {expected_lo - 1:,}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
    else:
        print("OK: 全180チャンクが [1,000,001 .. 10,000,000] を隙間なくカバー")

    # サマリー
    print(f"\n最初のチャンク: {chunks[0][0]} [{chunks[0][1]:,} .. {chunks[0][2]:,}]")
    print(f"最後のチャンク: {chunks[-1][0]} [{chunks[-1][1]:,} .. {chunks[-1][2]:,}]")
    print(f"カバー範囲: [{chunks[0][1]:,} .. {chunks[-1][2]:,}]")
    print(f"総数: {sum(hi - lo + 1 for _, lo, hi in chunks):,}")

    # All.lean のインポート数確認
    all_path = os.path.join(CHUNK_DIR, "All.lean")
    if os.path.exists(all_path):
        with open(all_path, 'r') as f:
            all_content = f.read()
        n_imports = all_content.count("import Unsolved.Collatz.Verification10M.Chunk")
        print(f"\nAll.lean のチャンク import 数: {n_imports}")
        if n_imports == len(chunks):
            print("OK: import 数とチャンク数が一致")
        else:
            print(f"MISMATCH: import={n_imports}, chunks={len(chunks)}")

if __name__ == "__main__":
    main()
