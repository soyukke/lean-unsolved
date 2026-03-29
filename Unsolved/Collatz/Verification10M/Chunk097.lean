-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 097: n in [5,800,001 .. 5,850,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_5800001_5850000 :
    collatzAllReachBounded 750 5800001 5850000 = true := by
  native_decide
