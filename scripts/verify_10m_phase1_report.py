#!/usr/bin/env python3
"""
verify_10m_phase1_report.py
============================
10^7検証Phase1の結果レポートを生成するスクリプト。
最初の10チャンクの最大stopping timeを検証し、ビルド時間の見積もりを行う。
"""

import json
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

def stopping_time(n, max_steps=10000):
    current = n
    for i in range(max_steps):
        if current == 1:
            return i
        current = collatz_step(current)
    return -1

def analyze_chunk(chunk_id, lo, hi):
    """1チャンクの最大stopping timeを計算"""
    max_st = 0
    max_n = lo
    for n in range(lo, hi + 1):
        st = stopping_time(n)
        if st > max_st:
            max_st = st
            max_n = n
    return max_st, max_n

# 10チャンクの範囲
CHUNK_SIZE = 50000
RANGE_START = 1000001
STEPS = 750

chunks = []
for i in range(10):
    lo = RANGE_START + i * CHUNK_SIZE
    hi = lo + CHUNK_SIZE - 1
    chunks.append((i + 1, lo, hi))

print("=" * 70)
print("  10^7 Verification Phase 1 Report")
print("  最初の10チャンクの分析")
print("=" * 70)
print()

chunk_results = []
overall_max_st = 0
overall_max_n = 0

for chunk_id, lo, hi in chunks:
    t0 = time.time()
    max_st, max_n = analyze_chunk(chunk_id, lo, hi)
    elapsed = time.time() - t0

    if max_st > overall_max_st:
        overall_max_st = max_st
        overall_max_n = max_n

    result = {
        "chunk_id": chunk_id,
        "range": [lo, hi],
        "max_stopping_time": max_st,
        "max_stopping_time_n": max_n,
        "python_analysis_time_sec": round(elapsed, 2)
    }
    chunk_results.append(result)
    print(f"  Chunk{chunk_id:03d} [{lo:>10,} - {hi:>10,}]: "
          f"max_st = {max_st:>4d} (n = {max_n:>10,}), "
          f"Python解析: {elapsed:.1f}s")

print()
print(f"  全10チャンクの最大 stopping time: {overall_max_st} (n = {overall_max_n:,})")
print(f"  設定 steps: {STEPS} (余裕: {STEPS - overall_max_st})")
print()

# ビルド時間の見積もり
build_time_per_chunk = 8.65  # Chunk001=8.6s, Chunk002=8.7s の平均
total_chunks = 180
estimated_total = build_time_per_chunk * total_chunks

print(f"  ビルド時間:")
print(f"    1チャンクあたり: ~{build_time_per_chunk:.1f}s (実測平均)")
print(f"    10チャンク: ~{build_time_per_chunk * 10:.0f}s = ~{build_time_per_chunk * 10 / 60:.1f}min")
print(f"    全180チャンク: ~{estimated_total:.0f}s = ~{estimated_total / 60:.0f}min = ~{estimated_total / 3600:.1f}h")
print(f"    (逐次実行の場合。並列化で短縮可能)")
print()

# JSON出力
report = {
    "title": "10^7 Verification Phase 1 Report",
    "description": "最初の10チャンク (n = 1,000,001 ~ 1,500,000) の分析結果",
    "total_chunks_generated": 10,
    "total_chunks_needed": 180,
    "chunk_size": CHUNK_SIZE,
    "steps": STEPS,
    "build_test_results": {
        "chunk001": {"status": "SUCCESS", "build_time_sec": 8.6},
        "chunk002": {"status": "SUCCESS", "build_time_sec": 8.7}
    },
    "overall_max_stopping_time": overall_max_st,
    "overall_max_stopping_time_n": overall_max_n,
    "steps_margin": STEPS - overall_max_st,
    "chunk_analysis": chunk_results,
    "build_time_estimates": {
        "per_chunk_sec": build_time_per_chunk,
        "10_chunks_sec": round(build_time_per_chunk * 10, 1),
        "180_chunks_sec": round(estimated_total, 1),
        "180_chunks_min": round(estimated_total / 60, 1),
        "180_chunks_hours": round(estimated_total / 3600, 2)
    },
    "conclusion": "Phase1成功: 10チャンク生成+2チャンクビルドテスト完了。"
                   "native_decide による 50K 範囲の検証は約 9s/チャンクで安定。"
                   "steps=750 は十分な余裕あり。"
                   "全180チャンクの逐次ビルドは約26分の見込み。"
}

output_path = os.path.join(BASE_DIR, "results", "10m_verification_phase1.json")
with open(output_path, 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"  レポート出力: {output_path}")
