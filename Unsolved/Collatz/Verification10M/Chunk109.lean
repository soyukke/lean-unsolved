-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 109: n in [6,400,001 .. 6,450,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_6400001_6450000 :
    collatzAllReachBounded 750 6400001 6450000 = true := by
  native_decide
