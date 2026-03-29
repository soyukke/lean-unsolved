-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 149: n in [8,400,001 .. 8,450,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_8400001_8450000 :
    collatzAllReachBounded 750 8400001 8450000 = true := by
  native_decide
