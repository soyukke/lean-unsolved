-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 060: n in [3,950,001 .. 4,000,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_3950001_4000000 :
    collatzAllReachBounded 750 3950001 4000000 = true := by
  native_decide
