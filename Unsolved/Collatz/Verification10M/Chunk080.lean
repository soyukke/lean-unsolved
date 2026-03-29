-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 080: n in [4,950,001 .. 5,000,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_4950001_5000000 :
    collatzAllReachBounded 750 4950001 5000000 = true := by
  native_decide
