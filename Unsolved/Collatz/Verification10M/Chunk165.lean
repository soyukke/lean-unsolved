-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 165: n in [9,200,001 .. 9,250,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_9200001_9250000 :
    collatzAllReachBounded 750 9200001 9250000 = true := by
  native_decide
