-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 025: n in [2,200,001 .. 2,250,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_2200001_2250000 :
    collatzAllReachBounded 750 2200001 2250000 = true := by
  native_decide
