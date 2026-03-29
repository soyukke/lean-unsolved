-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 100: n in [5,950,001 .. 6,000,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_5950001_6000000 :
    collatzAllReachBounded 750 5950001 6000000 = true := by
  native_decide
