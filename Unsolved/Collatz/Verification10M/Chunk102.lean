-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 102: n in [6,050,001 .. 6,100,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_6050001_6100000 :
    collatzAllReachBounded 750 6050001 6100000 = true := by
  native_decide
