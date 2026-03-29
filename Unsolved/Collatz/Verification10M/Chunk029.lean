-- 自動生成ファイル: generate_10m_verification.py
-- チャンク 029: n in [2,400,001 .. 2,450,000]
-- 生成日時: 2026-03-29 23:18:07
import Unsolved.Collatz.StoppingTime.Verification

set_option maxHeartbeats 0 in
set_option maxRecDepth 2000 in
set_option linter.style.nativeDecide false in
theorem collatzAllReach_2400001_2450000 :
    collatzAllReachBounded 750 2400001 2450000 = true := by
  native_decide
