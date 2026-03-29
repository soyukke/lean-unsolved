-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 006: n in [1,250,001 .. 1,300,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_1250001_1300000 :
    collatzAllReachBounded 750 1250001 1300000 = true := by
  native_decide
