-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 088: n in [5,350,001 .. 5,400,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_5350001_5400000 :
    collatzAllReachBounded 750 5350001 5400000 = true := by
  native_decide
