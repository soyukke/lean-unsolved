-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 024: n in [2,150,001 .. 2,200,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_2150001_2200000 :
    collatzAllReachBounded 750 2150001 2200000 = true := by
  native_decide
