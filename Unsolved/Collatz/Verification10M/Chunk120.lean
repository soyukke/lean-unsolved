-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 120: n in [6,950,001 .. 7,000,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_6950001_7000000 :
    collatzAllReachBounded 750 6950001 7000000 = true := by
  native_decide
