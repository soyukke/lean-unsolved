# 問題一覧と概要

subagentに問題の背景を渡す際に参照する。

## collatz
**コラッツ予想 (Collatz conjecture)**
任意の正整数 n に対し、n が偶数なら n/2、奇数なら 3n+1 を繰り返すと必ず 1 に到達するという予想。
Syracuse関数 T(n) = (3n+1)/2^v2(3n+1) を用いた定式化を採用。
Leanファイル: Collatz.lean, CollatzStructure.lean, CollatzMod.lean, CollatzHensel.lean, CollatzCycle.lean, CollatzAccel.lean, CollatzFormula.lean, CollatzMinimal.lean, CollatzMod3.lean, CollatzStoppingTime.lean, Collatz5n1.lean

## goldbach
**ゴールドバッハ予想 (Goldbach's conjecture)**
2より大きい全ての偶数は2つの素数の和で表せるという予想。
Leanファイル: Goldbach.lean

## twinprime
**双子素数予想 (Twin prime conjecture)**
差が2の素数の組（双子素数）が無限に存在するという予想。
Leanファイル: TwinPrime.lean

## erdos89
**エルデシュ #89: 異なる距離問題 (Erdős distinct distances)**
平面上のn点集合が定める異なる距離の最小数に関する問題。
Leanファイル: ErdosDistinctDistances.lean

## erdos77
**エルデシュ #77: ラムゼー数の極限 (Erdős-Ramsey)**
R(k,k)^{1/k} の極限値に関する問題。
Leanファイル: ErdosRamsey.lean

## erdos20
**エルデシュ #20: ひまわり予想 (Erdős sunflower conjecture)**
k-集合族にひまわりが含まれるための十分条件に関する予想。
Leanファイル: ErdosSunflower.lean

## erdos52
**エルデシュ #52: 和積問題 (Erdős sum-product)**
有限集合 A に対し |A+A| + |A·A| ≥ c|A|^{1+ε} となるεの最大値に関する問題。
Leanファイル: ErdosSumProduct.lean

## erdos138
**エルデシュ #138: Van der Waerden数 (Van der Waerden numbers)**
W(k) の増大度に関する問題。
Leanファイル: ErdosVanDerWaerden.lean
