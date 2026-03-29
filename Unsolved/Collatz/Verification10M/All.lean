-- 自動生成ファイル: generate_10m_verification.py
-- n <= 10,000,000 のコラッツ検証統合
-- 生成日時: 2026-03-29 23:18:07
--
-- 構成:
--   基盤: collatzReaches_le_1000000 (既存, n <= 10^6)
--   拡張: 180 チャンク x 50,000 = 1,000,001 ~ 10,000,000
--   steps: 750 (最大 stopping time 685 + 余裕)

import Unsolved.Collatz.Verification10M.Chunk001
import Unsolved.Collatz.Verification10M.Chunk002
import Unsolved.Collatz.Verification10M.Chunk003
import Unsolved.Collatz.Verification10M.Chunk004
import Unsolved.Collatz.Verification10M.Chunk005
import Unsolved.Collatz.Verification10M.Chunk006
import Unsolved.Collatz.Verification10M.Chunk007
import Unsolved.Collatz.Verification10M.Chunk008
import Unsolved.Collatz.Verification10M.Chunk009
import Unsolved.Collatz.Verification10M.Chunk010
import Unsolved.Collatz.Verification10M.Chunk011
import Unsolved.Collatz.Verification10M.Chunk012
import Unsolved.Collatz.Verification10M.Chunk013
import Unsolved.Collatz.Verification10M.Chunk014
import Unsolved.Collatz.Verification10M.Chunk015
import Unsolved.Collatz.Verification10M.Chunk016
import Unsolved.Collatz.Verification10M.Chunk017
import Unsolved.Collatz.Verification10M.Chunk018
import Unsolved.Collatz.Verification10M.Chunk019
import Unsolved.Collatz.Verification10M.Chunk020
import Unsolved.Collatz.Verification10M.Chunk021
import Unsolved.Collatz.Verification10M.Chunk022
import Unsolved.Collatz.Verification10M.Chunk023
import Unsolved.Collatz.Verification10M.Chunk024
import Unsolved.Collatz.Verification10M.Chunk025
import Unsolved.Collatz.Verification10M.Chunk026
import Unsolved.Collatz.Verification10M.Chunk027
import Unsolved.Collatz.Verification10M.Chunk028
import Unsolved.Collatz.Verification10M.Chunk029
import Unsolved.Collatz.Verification10M.Chunk030
import Unsolved.Collatz.Verification10M.Chunk031
import Unsolved.Collatz.Verification10M.Chunk032
import Unsolved.Collatz.Verification10M.Chunk033
import Unsolved.Collatz.Verification10M.Chunk034
import Unsolved.Collatz.Verification10M.Chunk035
import Unsolved.Collatz.Verification10M.Chunk036
import Unsolved.Collatz.Verification10M.Chunk037
import Unsolved.Collatz.Verification10M.Chunk038
import Unsolved.Collatz.Verification10M.Chunk039
import Unsolved.Collatz.Verification10M.Chunk040
import Unsolved.Collatz.Verification10M.Chunk041
import Unsolved.Collatz.Verification10M.Chunk042
import Unsolved.Collatz.Verification10M.Chunk043
import Unsolved.Collatz.Verification10M.Chunk044
import Unsolved.Collatz.Verification10M.Chunk045
import Unsolved.Collatz.Verification10M.Chunk046
import Unsolved.Collatz.Verification10M.Chunk047
import Unsolved.Collatz.Verification10M.Chunk048
import Unsolved.Collatz.Verification10M.Chunk049
import Unsolved.Collatz.Verification10M.Chunk050
import Unsolved.Collatz.Verification10M.Chunk051
import Unsolved.Collatz.Verification10M.Chunk052
import Unsolved.Collatz.Verification10M.Chunk053
import Unsolved.Collatz.Verification10M.Chunk054
import Unsolved.Collatz.Verification10M.Chunk055
import Unsolved.Collatz.Verification10M.Chunk056
import Unsolved.Collatz.Verification10M.Chunk057
import Unsolved.Collatz.Verification10M.Chunk058
import Unsolved.Collatz.Verification10M.Chunk059
import Unsolved.Collatz.Verification10M.Chunk060
import Unsolved.Collatz.Verification10M.Chunk061
import Unsolved.Collatz.Verification10M.Chunk062
import Unsolved.Collatz.Verification10M.Chunk063
import Unsolved.Collatz.Verification10M.Chunk064
import Unsolved.Collatz.Verification10M.Chunk065
import Unsolved.Collatz.Verification10M.Chunk066
import Unsolved.Collatz.Verification10M.Chunk067
import Unsolved.Collatz.Verification10M.Chunk068
import Unsolved.Collatz.Verification10M.Chunk069
import Unsolved.Collatz.Verification10M.Chunk070
import Unsolved.Collatz.Verification10M.Chunk071
import Unsolved.Collatz.Verification10M.Chunk072
import Unsolved.Collatz.Verification10M.Chunk073
import Unsolved.Collatz.Verification10M.Chunk074
import Unsolved.Collatz.Verification10M.Chunk075
import Unsolved.Collatz.Verification10M.Chunk076
import Unsolved.Collatz.Verification10M.Chunk077
import Unsolved.Collatz.Verification10M.Chunk078
import Unsolved.Collatz.Verification10M.Chunk079
import Unsolved.Collatz.Verification10M.Chunk080
import Unsolved.Collatz.Verification10M.Chunk081
import Unsolved.Collatz.Verification10M.Chunk082
import Unsolved.Collatz.Verification10M.Chunk083
import Unsolved.Collatz.Verification10M.Chunk084
import Unsolved.Collatz.Verification10M.Chunk085
import Unsolved.Collatz.Verification10M.Chunk086
import Unsolved.Collatz.Verification10M.Chunk087
import Unsolved.Collatz.Verification10M.Chunk088
import Unsolved.Collatz.Verification10M.Chunk089
import Unsolved.Collatz.Verification10M.Chunk090
import Unsolved.Collatz.Verification10M.Chunk091
import Unsolved.Collatz.Verification10M.Chunk092
import Unsolved.Collatz.Verification10M.Chunk093
import Unsolved.Collatz.Verification10M.Chunk094
import Unsolved.Collatz.Verification10M.Chunk095
import Unsolved.Collatz.Verification10M.Chunk096
import Unsolved.Collatz.Verification10M.Chunk097
import Unsolved.Collatz.Verification10M.Chunk098
import Unsolved.Collatz.Verification10M.Chunk099
import Unsolved.Collatz.Verification10M.Chunk100
import Unsolved.Collatz.Verification10M.Chunk101
import Unsolved.Collatz.Verification10M.Chunk102
import Unsolved.Collatz.Verification10M.Chunk103
import Unsolved.Collatz.Verification10M.Chunk104
import Unsolved.Collatz.Verification10M.Chunk105
import Unsolved.Collatz.Verification10M.Chunk106
import Unsolved.Collatz.Verification10M.Chunk107
import Unsolved.Collatz.Verification10M.Chunk108
import Unsolved.Collatz.Verification10M.Chunk109
import Unsolved.Collatz.Verification10M.Chunk110
import Unsolved.Collatz.Verification10M.Chunk111
import Unsolved.Collatz.Verification10M.Chunk112
import Unsolved.Collatz.Verification10M.Chunk113
import Unsolved.Collatz.Verification10M.Chunk114
import Unsolved.Collatz.Verification10M.Chunk115
import Unsolved.Collatz.Verification10M.Chunk116
import Unsolved.Collatz.Verification10M.Chunk117
import Unsolved.Collatz.Verification10M.Chunk118
import Unsolved.Collatz.Verification10M.Chunk119
import Unsolved.Collatz.Verification10M.Chunk120
import Unsolved.Collatz.Verification10M.Chunk121
import Unsolved.Collatz.Verification10M.Chunk122
import Unsolved.Collatz.Verification10M.Chunk123
import Unsolved.Collatz.Verification10M.Chunk124
import Unsolved.Collatz.Verification10M.Chunk125
import Unsolved.Collatz.Verification10M.Chunk126
import Unsolved.Collatz.Verification10M.Chunk127
import Unsolved.Collatz.Verification10M.Chunk128
import Unsolved.Collatz.Verification10M.Chunk129
import Unsolved.Collatz.Verification10M.Chunk130
import Unsolved.Collatz.Verification10M.Chunk131
import Unsolved.Collatz.Verification10M.Chunk132
import Unsolved.Collatz.Verification10M.Chunk133
import Unsolved.Collatz.Verification10M.Chunk134
import Unsolved.Collatz.Verification10M.Chunk135
import Unsolved.Collatz.Verification10M.Chunk136
import Unsolved.Collatz.Verification10M.Chunk137
import Unsolved.Collatz.Verification10M.Chunk138
import Unsolved.Collatz.Verification10M.Chunk139
import Unsolved.Collatz.Verification10M.Chunk140
import Unsolved.Collatz.Verification10M.Chunk141
import Unsolved.Collatz.Verification10M.Chunk142
import Unsolved.Collatz.Verification10M.Chunk143
import Unsolved.Collatz.Verification10M.Chunk144
import Unsolved.Collatz.Verification10M.Chunk145
import Unsolved.Collatz.Verification10M.Chunk146
import Unsolved.Collatz.Verification10M.Chunk147
import Unsolved.Collatz.Verification10M.Chunk148
import Unsolved.Collatz.Verification10M.Chunk149
import Unsolved.Collatz.Verification10M.Chunk150
import Unsolved.Collatz.Verification10M.Chunk151
import Unsolved.Collatz.Verification10M.Chunk152
import Unsolved.Collatz.Verification10M.Chunk153
import Unsolved.Collatz.Verification10M.Chunk154
import Unsolved.Collatz.Verification10M.Chunk155
import Unsolved.Collatz.Verification10M.Chunk156
import Unsolved.Collatz.Verification10M.Chunk157
import Unsolved.Collatz.Verification10M.Chunk158
import Unsolved.Collatz.Verification10M.Chunk159
import Unsolved.Collatz.Verification10M.Chunk160
import Unsolved.Collatz.Verification10M.Chunk161
import Unsolved.Collatz.Verification10M.Chunk162
import Unsolved.Collatz.Verification10M.Chunk163
import Unsolved.Collatz.Verification10M.Chunk164
import Unsolved.Collatz.Verification10M.Chunk165
import Unsolved.Collatz.Verification10M.Chunk166
import Unsolved.Collatz.Verification10M.Chunk167
import Unsolved.Collatz.Verification10M.Chunk168
import Unsolved.Collatz.Verification10M.Chunk169
import Unsolved.Collatz.Verification10M.Chunk170
import Unsolved.Collatz.Verification10M.Chunk171
import Unsolved.Collatz.Verification10M.Chunk172
import Unsolved.Collatz.Verification10M.Chunk173
import Unsolved.Collatz.Verification10M.Chunk174
import Unsolved.Collatz.Verification10M.Chunk175
import Unsolved.Collatz.Verification10M.Chunk176
import Unsolved.Collatz.Verification10M.Chunk177
import Unsolved.Collatz.Verification10M.Chunk178
import Unsolved.Collatz.Verification10M.Chunk179
import Unsolved.Collatz.Verification10M.Chunk180
import Unsolved.Collatz.StoppingTime.Verification

/-!
# コラッツ予想: n <= 10,000,000 の検証

n <= 1,000,000 の検証 (collatzReaches_le_1000000) を基盤に、
1,000,001 ~ 10,000,000 を 50,000 件ずつのチャンクに分割して
native_decide で検証する。

## チャンク構成
- 180 チャンク (Chunk001 ~ Chunk180)
- 各チャンク: collatzAllReachBounded 750 lo hi = true
- 18 バッチ (10 チャンク/バッチ) のサブ定理で中間統合
-/

/-- 1,000,001 <= n <= 1,500,000 の検証 -/
theorem collatzReaches_1000001_1500000 (n : Nat) (hlo : n >= 1000001) (hhi : n <= 1500000) :
    collatzReaches n := by
  by_cases h0 : n <= 1050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_1000001_1050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 1100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_1050001_1100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 1150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_1100001_1150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 1200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_1150001_1200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 1250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_1200001_1250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 1300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_1250001_1300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 1350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_1300001_1350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 1400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_1350001_1400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 1450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_1400001_1450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_1450001_1500000 n (by omega) hhi

/-- 1,500,001 <= n <= 2,000,000 の検証 -/
theorem collatzReaches_1500001_2000000 (n : Nat) (hlo : n >= 1500001) (hhi : n <= 2000000) :
    collatzReaches n := by
  by_cases h0 : n <= 1550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_1500001_1550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 1600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_1550001_1600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 1650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_1600001_1650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 1700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_1650001_1700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 1750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_1700001_1750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 1800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_1750001_1800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 1850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_1800001_1850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 1900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_1850001_1900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 1950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_1900001_1950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_1950001_2000000 n (by omega) hhi

/-- 2,000,001 <= n <= 2,500,000 の検証 -/
theorem collatzReaches_2000001_2500000 (n : Nat) (hlo : n >= 2000001) (hhi : n <= 2500000) :
    collatzReaches n := by
  by_cases h0 : n <= 2050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_2000001_2050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 2100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_2050001_2100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 2150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_2100001_2150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 2200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_2150001_2200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 2250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_2200001_2250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 2300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_2250001_2300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 2350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_2300001_2350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 2400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_2350001_2400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 2450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_2400001_2450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_2450001_2500000 n (by omega) hhi

/-- 2,500,001 <= n <= 3,000,000 の検証 -/
theorem collatzReaches_2500001_3000000 (n : Nat) (hlo : n >= 2500001) (hhi : n <= 3000000) :
    collatzReaches n := by
  by_cases h0 : n <= 2550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_2500001_2550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 2600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_2550001_2600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 2650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_2600001_2650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 2700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_2650001_2700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 2750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_2700001_2750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 2800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_2750001_2800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 2850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_2800001_2850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 2900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_2850001_2900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 2950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_2900001_2950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_2950001_3000000 n (by omega) hhi

/-- 3,000,001 <= n <= 3,500,000 の検証 -/
theorem collatzReaches_3000001_3500000 (n : Nat) (hlo : n >= 3000001) (hhi : n <= 3500000) :
    collatzReaches n := by
  by_cases h0 : n <= 3050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_3000001_3050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 3100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_3050001_3100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 3150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_3100001_3150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 3200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_3150001_3200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 3250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_3200001_3250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 3300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_3250001_3300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 3350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_3300001_3350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 3400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_3350001_3400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 3450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_3400001_3450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_3450001_3500000 n (by omega) hhi

/-- 3,500,001 <= n <= 4,000,000 の検証 -/
theorem collatzReaches_3500001_4000000 (n : Nat) (hlo : n >= 3500001) (hhi : n <= 4000000) :
    collatzReaches n := by
  by_cases h0 : n <= 3550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_3500001_3550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 3600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_3550001_3600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 3650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_3600001_3650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 3700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_3650001_3700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 3750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_3700001_3750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 3800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_3750001_3800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 3850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_3800001_3850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 3900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_3850001_3900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 3950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_3900001_3950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_3950001_4000000 n (by omega) hhi

/-- 4,000,001 <= n <= 4,500,000 の検証 -/
theorem collatzReaches_4000001_4500000 (n : Nat) (hlo : n >= 4000001) (hhi : n <= 4500000) :
    collatzReaches n := by
  by_cases h0 : n <= 4050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_4000001_4050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 4100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_4050001_4100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 4150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_4100001_4150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 4200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_4150001_4200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 4250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_4200001_4250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 4300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_4250001_4300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 4350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_4300001_4350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 4400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_4350001_4400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 4450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_4400001_4450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_4450001_4500000 n (by omega) hhi

/-- 4,500,001 <= n <= 5,000,000 の検証 -/
theorem collatzReaches_4500001_5000000 (n : Nat) (hlo : n >= 4500001) (hhi : n <= 5000000) :
    collatzReaches n := by
  by_cases h0 : n <= 4550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_4500001_4550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 4600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_4550001_4600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 4650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_4600001_4650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 4700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_4650001_4700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 4750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_4700001_4750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 4800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_4750001_4800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 4850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_4800001_4850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 4900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_4850001_4900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 4950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_4900001_4950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_4950001_5000000 n (by omega) hhi

/-- 5,000,001 <= n <= 5,500,000 の検証 -/
theorem collatzReaches_5000001_5500000 (n : Nat) (hlo : n >= 5000001) (hhi : n <= 5500000) :
    collatzReaches n := by
  by_cases h0 : n <= 5050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_5000001_5050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 5100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_5050001_5100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 5150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_5100001_5150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 5200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_5150001_5200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 5250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_5200001_5250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 5300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_5250001_5300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 5350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_5300001_5350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 5400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_5350001_5400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 5450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_5400001_5450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_5450001_5500000 n (by omega) hhi

/-- 5,500,001 <= n <= 6,000,000 の検証 -/
theorem collatzReaches_5500001_6000000 (n : Nat) (hlo : n >= 5500001) (hhi : n <= 6000000) :
    collatzReaches n := by
  by_cases h0 : n <= 5550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_5500001_5550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 5600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_5550001_5600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 5650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_5600001_5650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 5700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_5650001_5700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 5750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_5700001_5750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 5800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_5750001_5800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 5850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_5800001_5850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 5900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_5850001_5900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 5950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_5900001_5950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_5950001_6000000 n (by omega) hhi

/-- 6,000,001 <= n <= 6,500,000 の検証 -/
theorem collatzReaches_6000001_6500000 (n : Nat) (hlo : n >= 6000001) (hhi : n <= 6500000) :
    collatzReaches n := by
  by_cases h0 : n <= 6050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_6000001_6050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 6100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_6050001_6100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 6150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_6100001_6150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 6200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_6150001_6200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 6250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_6200001_6250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 6300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_6250001_6300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 6350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_6300001_6350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 6400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_6350001_6400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 6450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_6400001_6450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_6450001_6500000 n (by omega) hhi

/-- 6,500,001 <= n <= 7,000,000 の検証 -/
theorem collatzReaches_6500001_7000000 (n : Nat) (hlo : n >= 6500001) (hhi : n <= 7000000) :
    collatzReaches n := by
  by_cases h0 : n <= 6550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_6500001_6550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 6600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_6550001_6600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 6650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_6600001_6650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 6700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_6650001_6700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 6750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_6700001_6750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 6800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_6750001_6800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 6850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_6800001_6850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 6900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_6850001_6900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 6950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_6900001_6950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_6950001_7000000 n (by omega) hhi

/-- 7,000,001 <= n <= 7,500,000 の検証 -/
theorem collatzReaches_7000001_7500000 (n : Nat) (hlo : n >= 7000001) (hhi : n <= 7500000) :
    collatzReaches n := by
  by_cases h0 : n <= 7050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_7000001_7050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 7100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_7050001_7100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 7150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_7100001_7150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 7200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_7150001_7200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 7250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_7200001_7250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 7300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_7250001_7300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 7350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_7300001_7350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 7400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_7350001_7400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 7450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_7400001_7450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_7450001_7500000 n (by omega) hhi

/-- 7,500,001 <= n <= 8,000,000 の検証 -/
theorem collatzReaches_7500001_8000000 (n : Nat) (hlo : n >= 7500001) (hhi : n <= 8000000) :
    collatzReaches n := by
  by_cases h0 : n <= 7550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_7500001_7550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 7600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_7550001_7600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 7650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_7600001_7650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 7700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_7650001_7700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 7750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_7700001_7750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 7800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_7750001_7800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 7850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_7800001_7850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 7900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_7850001_7900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 7950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_7900001_7950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_7950001_8000000 n (by omega) hhi

/-- 8,000,001 <= n <= 8,500,000 の検証 -/
theorem collatzReaches_8000001_8500000 (n : Nat) (hlo : n >= 8000001) (hhi : n <= 8500000) :
    collatzReaches n := by
  by_cases h0 : n <= 8050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_8000001_8050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 8100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_8050001_8100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 8150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_8100001_8150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 8200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_8150001_8200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 8250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_8200001_8250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 8300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_8250001_8300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 8350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_8300001_8350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 8400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_8350001_8400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 8450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_8400001_8450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_8450001_8500000 n (by omega) hhi

/-- 8,500,001 <= n <= 9,000,000 の検証 -/
theorem collatzReaches_8500001_9000000 (n : Nat) (hlo : n >= 8500001) (hhi : n <= 9000000) :
    collatzReaches n := by
  by_cases h0 : n <= 8550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_8500001_8550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 8600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_8550001_8600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 8650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_8600001_8650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 8700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_8650001_8700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 8750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_8700001_8750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 8800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_8750001_8800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 8850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_8800001_8850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 8900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_8850001_8900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 8950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_8900001_8950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_8950001_9000000 n (by omega) hhi

/-- 9,000,001 <= n <= 9,500,000 の検証 -/
theorem collatzReaches_9000001_9500000 (n : Nat) (hlo : n >= 9000001) (hhi : n <= 9500000) :
    collatzReaches n := by
  by_cases h0 : n <= 9050000
  . exact collatzReaches_of_allReachBounded collatzAllReach_9000001_9050000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 9100000
    . exact collatzReaches_of_allReachBounded collatzAllReach_9050001_9100000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 9150000
      . exact collatzReaches_of_allReachBounded collatzAllReach_9100001_9150000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 9200000
        . exact collatzReaches_of_allReachBounded collatzAllReach_9150001_9200000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 9250000
          . exact collatzReaches_of_allReachBounded collatzAllReach_9200001_9250000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 9300000
            . exact collatzReaches_of_allReachBounded collatzAllReach_9250001_9300000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 9350000
              . exact collatzReaches_of_allReachBounded collatzAllReach_9300001_9350000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 9400000
                . exact collatzReaches_of_allReachBounded collatzAllReach_9350001_9400000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 9450000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_9400001_9450000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_9450001_9500000 n (by omega) hhi

/-- 9,500,001 <= n <= 10,000,000 の検証 -/
theorem collatzReaches_9500001_10000000 (n : Nat) (hlo : n >= 9500001) (hhi : n <= 10000000) :
    collatzReaches n := by
  by_cases h0 : n <= 9550000
  . exact collatzReaches_of_allReachBounded collatzAllReach_9500001_9550000 n (by omega) h0
  . push_neg at h0
    by_cases h1 : n <= 9600000
    . exact collatzReaches_of_allReachBounded collatzAllReach_9550001_9600000 n (by omega) h1
    . push_neg at h1
      by_cases h2 : n <= 9650000
      . exact collatzReaches_of_allReachBounded collatzAllReach_9600001_9650000 n (by omega) h2
      . push_neg at h2
        by_cases h3 : n <= 9700000
        . exact collatzReaches_of_allReachBounded collatzAllReach_9650001_9700000 n (by omega) h3
        . push_neg at h3
          by_cases h4 : n <= 9750000
          . exact collatzReaches_of_allReachBounded collatzAllReach_9700001_9750000 n (by omega) h4
          . push_neg at h4
            by_cases h5 : n <= 9800000
            . exact collatzReaches_of_allReachBounded collatzAllReach_9750001_9800000 n (by omega) h5
            . push_neg at h5
              by_cases h6 : n <= 9850000
              . exact collatzReaches_of_allReachBounded collatzAllReach_9800001_9850000 n (by omega) h6
              . push_neg at h6
                by_cases h7 : n <= 9900000
                . exact collatzReaches_of_allReachBounded collatzAllReach_9850001_9900000 n (by omega) h7
                . push_neg at h7
                  by_cases h8 : n <= 9950000
                  . exact collatzReaches_of_allReachBounded collatzAllReach_9900001_9950000 n (by omega) h8
                  . push_neg at h8
                    exact collatzReaches_of_allReachBounded collatzAllReach_9950001_10000000 n (by omega) hhi

/-- n <= 10,000,000 の全自然数がコラッツ操作で 1 に到達する -/
theorem collatzReaches_le_10000000 (n : Nat) (hn1 : n >= 1) (hn : n <= 10000000) :
    collatzReaches n := by
  by_cases h1m : n <= 1000000
  . exact collatzReaches_le_1000000 n hn1 h1m
  . push_neg at h1m
    by_cases h_b0 : n <= 1500000
    . exact collatzReaches_1000001_1500000 n (by omega) h_b0
    . push_neg at h_b0
      by_cases h_b1 : n <= 2000000
      . exact collatzReaches_1500001_2000000 n (by omega) h_b1
      . push_neg at h_b1
        by_cases h_b2 : n <= 2500000
        . exact collatzReaches_2000001_2500000 n (by omega) h_b2
        . push_neg at h_b2
          by_cases h_b3 : n <= 3000000
          . exact collatzReaches_2500001_3000000 n (by omega) h_b3
          . push_neg at h_b3
            by_cases h_b4 : n <= 3500000
            . exact collatzReaches_3000001_3500000 n (by omega) h_b4
            . push_neg at h_b4
              by_cases h_b5 : n <= 4000000
              . exact collatzReaches_3500001_4000000 n (by omega) h_b5
              . push_neg at h_b5
                by_cases h_b6 : n <= 4500000
                . exact collatzReaches_4000001_4500000 n (by omega) h_b6
                . push_neg at h_b6
                  by_cases h_b7 : n <= 5000000
                  . exact collatzReaches_4500001_5000000 n (by omega) h_b7
                  . push_neg at h_b7
                    by_cases h_b8 : n <= 5500000
                    . exact collatzReaches_5000001_5500000 n (by omega) h_b8
                    . push_neg at h_b8
                      by_cases h_b9 : n <= 6000000
                      . exact collatzReaches_5500001_6000000 n (by omega) h_b9
                      . push_neg at h_b9
                        by_cases h_b10 : n <= 6500000
                        . exact collatzReaches_6000001_6500000 n (by omega) h_b10
                        . push_neg at h_b10
                          by_cases h_b11 : n <= 7000000
                          . exact collatzReaches_6500001_7000000 n (by omega) h_b11
                          . push_neg at h_b11
                            by_cases h_b12 : n <= 7500000
                            . exact collatzReaches_7000001_7500000 n (by omega) h_b12
                            . push_neg at h_b12
                              by_cases h_b13 : n <= 8000000
                              . exact collatzReaches_7500001_8000000 n (by omega) h_b13
                              . push_neg at h_b13
                                by_cases h_b14 : n <= 8500000
                                . exact collatzReaches_8000001_8500000 n (by omega) h_b14
                                . push_neg at h_b14
                                  by_cases h_b15 : n <= 9000000
                                  . exact collatzReaches_8500001_9000000 n (by omega) h_b15
                                  . push_neg at h_b15
                                    by_cases h_b16 : n <= 9500000
                                    . exact collatzReaches_9000001_9500000 n (by omega) h_b16
                                    . push_neg at h_b16
                                      exact collatzReaches_9500001_10000000 n (by omega) hn

/-- コラッツ予想が n <= 10,000,000 で成り立つ (関数形式) -/
theorem collatzConjectureR_verified_le_10000000 :
    forall n : Nat, n >= 1 -> n <= 10000000 -> collatzReaches n :=
  fun n hn1 hn => collatzReaches_le_10000000 n hn1 hn
