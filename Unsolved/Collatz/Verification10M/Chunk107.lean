-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 107: n in [6,300,001 .. 6,350,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_6300001_6350000 :
    collatzAllReachBounded 750 6300001 6350000 = true := by
  native_decide
