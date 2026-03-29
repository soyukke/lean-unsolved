-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 005: n in [1,200,001 .. 1,250,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_1200001_1250000 :
    collatzAllReachBounded 750 1200001 1250000 = true := by
  native_decide
