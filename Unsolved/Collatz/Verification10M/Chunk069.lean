-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 069: n in [4,400,001 .. 4,450,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_4400001_4450000 :
    collatzAllReachBounded 750 4400001 4450000 = true := by
  native_decide
