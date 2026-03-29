-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 078: n in [4,850,001 .. 4,900,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_4850001_4900000 :
    collatzAllReachBounded 750 4850001 4900000 = true := by
  native_decide
