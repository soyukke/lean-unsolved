-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 126: n in [7,250,001 .. 7,300,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_7250001_7300000 :
    collatzAllReachBounded 750 7250001 7300000 = true := by
  native_decide
