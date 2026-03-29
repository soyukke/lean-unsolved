-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 079: n in [4,900,001 .. 4,950,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_4900001_4950000 :
    collatzAllReachBounded 750 4900001 4950000 = true := by
  native_decide
