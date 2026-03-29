-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 086: n in [5,250,001 .. 5,300,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_5250001_5300000 :
    collatzAllReachBounded 750 5250001 5300000 = true := by
  native_decide
