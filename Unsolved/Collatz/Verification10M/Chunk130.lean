-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 130: n in [7,450,001 .. 7,500,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_7450001_7500000 :
    collatzAllReachBounded 750 7450001 7500000 = true := by
  native_decide
