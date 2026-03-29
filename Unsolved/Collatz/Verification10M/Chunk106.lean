-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 106: n in [6,250,001 .. 6,300,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_6250001_6300000 :
    collatzAllReachBounded 750 6250001 6300000 = true := by
  native_decide
