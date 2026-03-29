-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 042: n in [3,050,001 .. 3,100,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_3050001_3100000 :
    collatzAllReachBounded 750 3050001 3100000 = true := by
  native_decide
