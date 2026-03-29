-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 053: n in [3,600,001 .. 3,650,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_3600001_3650000 :
    collatzAllReachBounded 750 3600001 3650000 = true := by
  native_decide
