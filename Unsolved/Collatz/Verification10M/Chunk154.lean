-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 154: n in [8,650,001 .. 8,700,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_8650001_8700000 :
    collatzAllReachBounded 750 8650001 8700000 = true := by
  native_decide
