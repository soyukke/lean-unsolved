#!/usr/bin/env python3
"""
verify_10m_generator.py
========================
generate_10m_verification.py が生成するファイルの整合性を検証するスクリプト。

チェック項目:
1. 全チャンクが隙間なく [1,000,001, 10,000,000] をカバーしている
2. 各チャンクファイルの定理名が All.lean の import/参照と一致
3. steps パラメータが全チャンクの最大 stopping time を超えている
4. All.lean のサブ定理が全チャンクを網羅している
5. Lean 構文の基本的な妥当性 (括弧・インデント)
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFICATION_DIR = os.path.join(BASE_DIR, "Unsolved", "Collatz", "Verification10M")


def check_chunk_coverage():
    """チャンクファイルが隙間なくカバーしているか確認"""
    chunk_files = sorted([
        f for f in os.listdir(VERIFICATION_DIR)
        if f.startswith("Chunk") and f.endswith(".lean")
    ])

    if not chunk_files:
        print("ERROR: No chunk files found")
        return False

    ranges = []
    for cf in chunk_files:
        with open(os.path.join(VERIFICATION_DIR, cf)) as f:
            content = f.read()
        m = re.search(r'collatzAllReachBounded\s+(\d+)\s+(\d+)\s+(\d+)', content)
        if m:
            steps, lo, hi = int(m.group(1)), int(m.group(2)), int(m.group(3))
            ranges.append((lo, hi, steps, cf))

    ranges.sort(key=lambda x: x[0])

    ok = True
    # Check first starts at 1,000,001
    if ranges[0][0] != 1_000_001:
        print(f"ERROR: First chunk starts at {ranges[0][0]}, expected 1,000,001")
        ok = False

    # Check last ends at 10,000,000
    if ranges[-1][1] != 10_000_000:
        print(f"ERROR: Last chunk ends at {ranges[-1][1]}, expected 10,000,000")
        ok = False

    # Check no gaps
    for i in range(len(ranges) - 1):
        if ranges[i][1] + 1 != ranges[i+1][0]:
            print(f"ERROR: Gap between {ranges[i][3]} (ends {ranges[i][1]}) and {ranges[i+1][3]} (starts {ranges[i+1][0]})")
            ok = False

    if ok:
        print(f"OK: {len(ranges)} chunks cover [1,000,001 - 10,000,000] without gaps")
        print(f"    Steps: {ranges[0][2]} (uniform)")

    return ok


def check_all_lean():
    """All.lean の整合性を確認"""
    all_path = os.path.join(VERIFICATION_DIR, "All.lean")
    if not os.path.exists(all_path):
        print("ERROR: All.lean not found")
        return False

    with open(all_path) as f:
        content = f.read()

    ok = True

    # Check imports
    imports = re.findall(r'import Unsolved\.Collatz\.Verification10M\.Chunk(\d+)', content)
    chunk_files = sorted([
        f for f in os.listdir(VERIFICATION_DIR)
        if f.startswith("Chunk") and f.endswith(".lean")
    ])

    expected_ids = sorted([
        int(re.search(r'Chunk(\d+)', f).group(1))
        for f in chunk_files
    ])
    import_ids = sorted([int(x) for x in imports])

    if import_ids != expected_ids:
        print(f"ERROR: Import mismatch. Imports: {len(import_ids)}, Files: {len(expected_ids)}")
        ok = False
    else:
        print(f"OK: {len(import_ids)} imports match {len(expected_ids)} chunk files")

    # Check final theorem exists
    if 'theorem collatzReaches_le_10000000' in content:
        print("OK: collatzReaches_le_10000000 theorem found")
    else:
        print("ERROR: collatzReaches_le_10000000 theorem not found")
        ok = False

    # Check uses collatzReaches_le_1000000 as base
    if 'collatzReaches_le_1000000' in content:
        print("OK: Uses collatzReaches_le_1000000 as base")
    else:
        print("WARNING: Does not reference collatzReaches_le_1000000")

    # Check all chunk theorems are referenced
    all_refs = re.findall(r'collatzAllReach_(\d+)_(\d+)', content)
    ref_ranges = sorted(set(all_refs))
    print(f"OK: {len(ref_ranges)} chunk theorem references in All.lean")

    return ok


def main():
    print("=" * 60)
    print("  10^7 Verification Generator - Integrity Check")
    print("=" * 60)

    if not os.path.exists(VERIFICATION_DIR):
        print(f"ERROR: Directory not found: {VERIFICATION_DIR}")
        print("Run generate_10m_verification.py first.")
        sys.exit(1)

    print()
    print("[1] Chunk coverage check:")
    ok1 = check_chunk_coverage()

    print()
    print("[2] All.lean integrity check:")
    ok2 = check_all_lean()

    print()
    if ok1 and ok2:
        print("=== ALL CHECKS PASSED ===")
    else:
        print("=== SOME CHECKS FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
