-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 034: n in [2,650,001 .. 2,700,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_2650001_2700000 :
    collatzAllReachBounded 750 2650001 2700000 = true := by
  native_decide
