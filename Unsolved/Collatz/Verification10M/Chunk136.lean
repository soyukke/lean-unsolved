-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 136: n in [7,750,001 .. 7,800,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_7750001_7800000 :
    collatzAllReachBounded 750 7750001 7800000 = true := by
  native_decide
