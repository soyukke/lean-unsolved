-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 177: n in [9,800,001 .. 9,850,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_9800001_9850000 :
    collatzAllReachBounded 750 9800001 9850000 = true := by
  native_decide
