-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 163: n in [9,100,001 .. 9,150,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_9100001_9150000 :
    collatzAllReachBounded 750 9100001 9150000 = true := by
  native_decide
