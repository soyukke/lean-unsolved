# 探索7: Erdos-Rado 上界 (n=1) の形式化

## 目的
空族・単一集合族がひまわりであることの自明な事実を形式証明する。
Erdos-Rado 定理 f(n,k) <= (k-1)^n * n! + 1 の n=1 ケース（f(1,k) <= k）の基礎補題。

## 主要結果
- `isSunflower_nil`: 空族はひまわり（core = 空集合で自明に成立）
- `isSunflower_singleton`: 単一集合はひまわり（core = その集合自身、花びらの互いに素条件は自明）

## 証明方針

### isSunflower_nil
- core = 空集合
- 「全ての S in [] について core ⊆ S」は前提が空なので自明
- 花びらの互いに素条件は i < 0 が不可能なので自明

### isSunflower_singleton
- core = S（唯一の集合そのもの）
- S ⊆ S は自明
- 花びら条件: i < 1 かつ j < 1 かつ i != j は不可能（omega で解決）

## 所見
これらは f(1,k) = k の既存証明（探索6の sunflower_uniform1_singletons）を補完する基礎事実。
帰納法の基底ケースとして、将来的に Erdos-Rado 上界の一般的な形式化に利用可能。
空族・単一族がひまわりであることは、ContainsSunflower の帰納的構成でも有用。
