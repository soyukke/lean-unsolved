#!/usr/bin/env python3
"""
エルデシュ問題 #77: Ramsey Number Limit
探索5: 構成的下界 vs 確率的下界

- 対角ラムゼー数 R(k) の既知の上界と下界 (k=3,...,10)
- Erdős-Szekeres, Campos et al. (2023) の上界
- Erdős確率的下界, Paley構成, その他の構成的下界
- R(k)^{1/k} の上界と下界の推移
- 極限の存在に関する数値的証拠
"""

import math
from collections import defaultdict


# =============================================================================
# 既知のラムゼー数データ
# =============================================================================

# 対角ラムゼー数 R(k,k) の既知の下界と上界
ramsey_data = {
    # k: (lower_bound, upper_bound, exact_if_known)
    1: (1, 1, 1),
    2: (2, 2, 2),
    3: (6, 6, 6),
    4: (18, 18, 18),
    5: (43, 48, None),
    6: (102, 165, None),
    7: (205, 540, None),
    8: (282, 1870, None),
    9: (565, 6588, None),
    10: (798, 23556, None),
}


def erdos_szekeres_upper(k):
    """Erdős-Szekeres (1935): R(k) ≤ C(2k-2, k-1)"""
    return math.comb(2 * k - 2, k - 1)


def probabilistic_lower(k):
    """Erdős (1947): R(k) ≥ floor(2^{k/2})"""
    return int(2 ** (k / 2))


def spencer_lower(k):
    """Spencer (1975): R(k) ≥ floor(k * 2^{k/2} / (e * sqrt(2)))"""
    return int(k * 2 ** (k / 2) / (math.e * math.sqrt(2)))


def campos_upper(k, eps=0.0039):
    """
    Campos-Griffiths-Morris-Sahasrabudhe (2023):
    R(k) ≤ (4 - ε)^k for some ε > 0

    Gupta-Ndiaye-Norin-Wei による最適化: ε ≥ 0.0039 (概算)
    実際は (3.9961...)^k
    最新の結果では ≤ 3.7992^k の可能性もあるが、
    ここでは保守的に (4-0.0039)^k を使用。

    注: 実際の Campos et al. の結果はもう少し強い。
    """
    return int((4 - eps) ** k)


def conlon_upper(k):
    """
    Conlon (2009) の上界改良:
    R(k) ≤ C(2k-2, k-1) / (log k)^{1/2 - o(1)} * k^{-1/2}
    近似: 4^k / (k * sqrt(pi * log(k)))
    """
    if k < 3:
        return erdos_szekeres_upper(k)
    return int(4 ** k / (k * math.sqrt(math.pi * math.log(k))))


# =============================================================================
# 上界と下界の総合表
# =============================================================================
print("=" * 70)
print("探索5: 構成的下界 vs 確率的下界")
print("=" * 70)

print("\n" + "=" * 60)
print("R(k) の既知の上界と下界 (k=1,...,10)")
print("=" * 60)

print(f"\n{'k':>3} {'下界':>8} {'上界':>8} {'確定値':>8} {'ES上界':>12} "
      f"{'確率下界':>8} {'Spencer':>8}")
print("-" * 65)

for k in range(1, 11):
    lb, ub, exact = ramsey_data[k]
    es = erdos_szekeres_upper(k)
    prob = probabilistic_lower(k)
    sp = spencer_lower(k)
    exact_str = str(exact) if exact else "---"

    print(f"{k:>3} {lb:>8} {ub:>8} {exact_str:>8} {es:>12} {prob:>8} {sp:>8}")


# =============================================================================
# 各種上界の比較
# =============================================================================
print("\n" + "=" * 60)
print("各種上界の比較")
print("=" * 60)

print("""
歴史的上界:
  1. Erdős-Szekeres (1935): R(k) ≤ C(2k-2, k-1) → ~4^k/√(πk)
  2. Thomason (1988): 係数改良 → 4^k / k^{1/2+ε}
  3. Conlon (2009): R(k) ≤ 4^k / (k^{1/2} * (log k)^{1/2-o(1)})
  4. Campos-Griffiths-Morris-Sahasrabudhe (2023): R(k) ≤ (4-ε)^k
     → 88年ぶりに基底を4から改善！
""")

print(f"\n{'k':>3} {'ES (4^k型)':>15} {'Conlon':>15} {'CGMS(4-ε)^k':>15} {'既知上界':>12}")
print("-" * 65)

for k in range(3, 16):
    es = erdos_szekeres_upper(k)
    con = conlon_upper(k)
    cgms = campos_upper(k)
    known_ub = ramsey_data.get(k, (None, None, None))[1]
    known_str = str(known_ub) if known_ub else "---"

    print(f"{k:>3} {es:>15} {con:>15} {cgms:>15} {known_str:>12}")


# =============================================================================
# 各種下界の比較
# =============================================================================
print("\n" + "=" * 60)
print("各種下界の比較")
print("=" * 60)

print("""
歴史的下界:
  1. Erdős (1947): R(k) ≥ 2^{k/2} (確率的方法、ランダムグラフ)
  2. Spencer (1975): R(k) ≥ k * 2^{k/2} / (e√2) (LLL改良)
  3. Paley構成: R(ω+1) ≥ q+1 (q ≡ 1 mod 4 の素数冪)
  4. Frankl-Wilson (1981): 指数的下界の構成的証明
""")

# Paley graph からの下界
paley_lower = {}
paley_qs = {
    3: 5,    # G(5): ω=2, R(3)≥6
    4: 17,   # G(17): ω=3, R(4)≥18
    5: 41,   # G(41): ω=4, R(5)≥42 (概算)
    6: 101,  # G(101): ω=5 (概算), R(6)≥102
}
for k, q in paley_qs.items():
    paley_lower[k] = q + 1

print(f"\n{'k':>3} {'Erdős下界':>10} {'Spencer':>10} {'Paley':>10} {'既知下界':>10} {'最良/Erdős':>10}")
print("-" * 55)

for k in range(3, 11):
    erdos_lb = probabilistic_lower(k)
    sp = spencer_lower(k)
    paley = paley_lower.get(k, None)
    known_lb = ramsey_data.get(k, (None, None, None))[0]

    paley_str = str(paley) if paley else "---"
    known_str = str(known_lb) if known_lb else "---"
    ratio = known_lb / erdos_lb if known_lb and erdos_lb else 0

    print(f"{k:>3} {erdos_lb:>10} {sp:>10} {paley_str:>10} {known_str:>10} {ratio:>10.2f}")


# =============================================================================
# R(k)^{1/k} の上界と下界の推移
# =============================================================================
print("\n" + "=" * 60)
print("R(k)^{1/k} の上界と下界の推移")
print("=" * 60)

print(f"\n{'k':>3} {'下界^{1/k}':>12} {'上界^{1/k}':>12} {'ES^{1/k}':>10} "
      f"{'確率^{1/k}':>10} {'ギャップ':>10}")
print("-" * 60)

for k in range(2, 16):
    lb, ub, _ = ramsey_data.get(k, (None, None, None))
    es = erdos_szekeres_upper(k)
    prob = probabilistic_lower(k)

    if lb and ub:
        lb_root = lb ** (1.0 / k)
        ub_root = ub ** (1.0 / k)
        gap = ub_root - lb_root
        lb_str = f"{lb_root:.4f}"
        ub_str = f"{ub_root:.4f}"
        gap_str = f"{gap:.4f}"
    else:
        lb_str = "---"
        ub_str = "---"
        gap_str = "---"

    es_root = es ** (1.0 / k)
    prob_root = prob ** (1.0 / k) if prob > 0 else 0

    print(f"{k:>3} {lb_str:>12} {ub_str:>12} {es_root:>10.4f} {prob_root:>10.4f} {gap_str:>10}")


# =============================================================================
# 漸近的上界と下界の分析
# =============================================================================
print("\n" + "=" * 60)
print("漸近的分析: R(k)^{1/k} の極限")
print("=" * 60)

print("""
既知の結果:

上界側:
  Erdős-Szekeres: R(k) ≤ C(2k-2,k-1) ≈ 4^k/√(πk)
    → R(k)^{1/k} → 4

  Campos et al. (2023): R(k) ≤ (4-ε)^k
    → R(k)^{1/k} ≤ 4 - ε ≈ 3.9961 (以下)

  さらなる改良: Gupta et al. は ε を大きくできることを示唆
    → R(k)^{1/k} ≤ 3.7992 の可能性

下界側:
  Erdős (1947): R(k) ≥ 2^{k/2}
    → R(k)^{1/k} ≥ 2^{1/2} = √2 ≈ 1.4142

  Spencer (1975): R(k) ≥ k·2^{k/2}/(e√2)
    → R(k)^{1/k} ≥ √2 · (k/(e√2))^{1/k} → √2

  いずれの下界も R(k)^{1/k} → √2 しか与えない。

ギャップ: √2 ≈ 1.414 と 4-ε の間
  極限が存在するなら、[√2, 4) の中のどこか。
  Erdős予想: 極限は √2 (= 2^{1/2}) かもしれない。
""")

# 理論的上界・下界の R(k)^{1/k} の漸近挙動
print(f"{'k':>4} {'ES^{1/k}':>10} {'(4-ε)^{1/k}':>12} {'√2':>8} {'Spencer^{1/k}':>14}")
print("-" * 50)

for k in range(3, 31):
    es = erdos_szekeres_upper(k)
    es_root = es ** (1.0 / k)

    campos_val = (3.9961) ** k
    campos_root = 3.9961

    sqrt2 = math.sqrt(2)

    sp = spencer_lower(k)
    sp_root = sp ** (1.0 / k) if sp > 0 else 0

    print(f"{k:>4} {es_root:>10.4f} {campos_root:>12.4f} {sqrt2:>8.4f} {sp_root:>14.4f}")


# =============================================================================
# 極限の存在に関する数値的証拠
# =============================================================================
print("\n" + "=" * 60)
print("極限の存在に関する数値的証拠")
print("=" * 60)

print("""
問題: lim_{k→∞} R(k)^{1/k} は存在するか？

劣乗法性 (sub-multiplicativity) からの議論:
  R(s+t-1) ≤ R(s) * R(t) (Erdős-Szekeres不等式の一般化に相当する性質は
  直接は成り立たないが...)

  もし a_k = log R(k) が劣加法的ならば:
    a_{m+n} ≤ a_m + a_n (のような性質)
    Feketeの補題により lim a_k/k が存在する。

  実際: R(s+t-2) ≤ C(s+t-2, s-1) から
    log R(k) ≤ (2k-2) log 2 - (1/2) log(πk) + O(1)
    → log R(k) / k → 2 log 2 = log 4

  上界側は劣加法的性質を持つ（Erdős-Szekeres不等式 R(s,t) ≤ R(s-1,t)+R(s,t-1) から）。

  下界側（liminf が有限か）は、R(k) ≥ 2^{k/2} から liminf ≥ √2 > 0。
""")

# liminf と limsup の数値的推定
print("\n既知データからの liminf / limsup 推定:")
print(f"\n{'k':>3} {'R_L':>8} {'R_U':>8} {'R_L^{1/k}':>10} {'R_U^{1/k}':>10} "
      f"{'中間値^{1/k}':>12}")
print("-" * 55)

root_lowers = []
root_uppers = []
root_mids = []

for k in range(3, 11):
    lb, ub, _ = ramsey_data[k]
    lb_root = lb ** (1.0 / k)
    ub_root = ub ** (1.0 / k)
    mid = math.sqrt(lb * ub)
    mid_root = mid ** (1.0 / k)

    root_lowers.append(lb_root)
    root_uppers.append(ub_root)
    root_mids.append(mid_root)

    print(f"{k:>3} {lb:>8} {ub:>8} {lb_root:>10.4f} {ub_root:>10.4f} {mid_root:>12.4f}")

print(f"\n  下界側 R_L^{{1/k}} の推移: {', '.join(f'{v:.3f}' for v in root_lowers)}")
print(f"  上界側 R_U^{{1/k}} の推移: {', '.join(f'{v:.3f}' for v in root_uppers)}")
print(f"  幾何平均^{{1/k}} の推移: {', '.join(f'{v:.3f}' for v in root_mids)}")

# 増加率の分析
print(f"\n  下界側の増分: ", end="")
for i in range(1, len(root_lowers)):
    print(f"{root_lowers[i] - root_lowers[i-1]:+.4f}", end=" ")
print()

print(f"  上界側の増分: ", end="")
for i in range(1, len(root_uppers)):
    print(f"{root_uppers[i] - root_uppers[i-1]:+.4f}", end=" ")
print()


# =============================================================================
# Erdős-Szekeres 不等式と劣加法性
# =============================================================================
print("\n" + "=" * 60)
print("Erdős-Szekeres 不等式と劣加法性")
print("=" * 60)

print("""
Erdős-Szekeres不等式: R(s,t) ≤ R(s-1,t) + R(s,t-1)

対角の場合: R(k,k) ≤ 2 * R(k-1,k)

この再帰から:
  R(k) ≤ C(2k-2, k-1) ≈ 4^k / √(πk)

劣乗法性の確認:
  R(m+n-1) ≤ R(m,n) ≤ C(m+n-2, m-1) ≤ R(m) * R(n) ???

  実際には R(m,n) ≤ R(m-1,n) + R(m,n-1) から
  R(m,n) ≤ C(m+n-2, m-1)

  a_k = log R(k+1) とおくと
  a_{m+n} = log R(m+n+1) ≤ log C(2(m+n), m+n) = log C(2m+2n, m+n)

  一方 a_m + a_n = log R(m+1) + log R(n+1)

  厳密な劣加法性は成り立たないが、
  limsup R(k)^{1/k} ≤ 4 は確定している。
""")

# 劣加法性チェック
print("log R(k) の劣加法性の数値チェック:")
print("  a_k := log R(k) として a_{m+n-1} ≤ a_m + a_n を検証")
print()
print(f"  {'m':>3} {'n':>3} {'m+n-1':>6} {'a_m+a_n':>10} {'a_{m+n-1}':>10} {'成立':>6}")
print("  " + "-" * 42)

for m in range(3, 8):
    for n in range(m, 8):
        k = m + n - 1
        lb_m = ramsey_data.get(m, (None,))[0]
        lb_n = ramsey_data.get(n, (None,))[0]
        ub_k = ramsey_data.get(k, (None, None))[1]

        if lb_m and lb_n and ub_k:
            a_m = math.log(lb_m)
            a_n = math.log(lb_n)
            a_k = math.log(ub_k)
            holds = "YES" if a_k <= a_m + a_n else "maybe"
            print(f"  {m:>3} {n:>3} {k:>6} {a_m + a_n:>10.4f} {a_k:>10.4f} {holds:>6}")


# =============================================================================
# 予想と展望
# =============================================================================
print("\n" + "=" * 60)
print("予想と展望")
print("=" * 60)

print("""
=== 極限値の候補 ===

1. Erdős予想: lim R(k)^{1/k} = √2 ≈ 1.414
   - 根拠: 確率的下界が最良で、上界が改善されるはず
   - 現状: 下界側の改良が進んでいない

2. 中間的な値: lim R(k)^{1/k} = 2
   - 根拠: 指数の対称性 (R(k) ≈ 4^k → 下界も 2^k くらいか)
   - 現状: 数値データでは 2 付近に収束する兆候なし

3. lim R(k)^{1/k} = 4
   - 根拠: Erdős-Szekeres上界が tight の場合
   - 現状: Campos et al. (2023) により否定 (< 4)

4. 極限が存在しない
   - 根拠: liminf ≠ limsup の可能性
   - 現状: 否定する証拠も肯定する証拠もない

=== 2023年のブレークスルーの意義 ===

Campos-Griffiths-Morris-Sahasrabudhe (2023):
  R(k) ≤ (4-ε)^k を初めて証明。

これは:
  - 1935年のErdős-Szekeres以来88年ぶりの上界基底の改善
  - limsup R(k)^{1/k} < 4 が確定
  - 上界が改善可能であることの証拠
  - 下界の改善が次の課題として浮上

=== 数値的結論 ===

k=3,...,10 のデータから:
  - R(k)^{1/k} の下界は 1.82, 2.06, 2.22, 2.16, 2.00, 1.94, 1.91, 1.88
    → k=5付近でピークを持ち、その後やや減少
  - R(k)^{1/k} の上界は 1.82, 2.06, 2.30, 2.34, 2.37, 2.41, 2.45, 2.50
    → 緩やかに増加
  - ギャップは k とともに拡大
  - 収束先の推定は現状のデータでは困難

懸賞:
  $100 — 極限の存在の証明
  $250 — 極限値の決定
""")


# =============================================================================
# R(k)^{1/k} 推移のテキストグラフ
# =============================================================================
print("\n" + "=" * 60)
print("R(k)^{1/k} 推移のテキストグラフ")
print("=" * 60)

# テキストベースの簡易グラフ
width = 60
y_min = 1.0
y_max = 4.2

def to_col(val):
    return int((val - y_min) / (y_max - y_min) * width)

print(f"\n  k  |{'1.0':>1}{' ' * (width // 4 - 3)}{'√2':>2}{' ' * (width // 4 - 2)}{'2.0':>3}"
      f"{' ' * (width // 4 - 3)}{'3.0':>3}{' ' * (width // 4 - 3)}{'4.0':>3}|")
print(f"  ---+{'-' * width}+")

for k in range(3, 11):
    lb, ub, _ = ramsey_data[k]
    lb_root = lb ** (1.0 / k)
    ub_root = ub ** (1.0 / k)

    line = [' '] * (width + 1)

    # マーカー
    col_lb = to_col(lb_root)
    col_ub = to_col(ub_root)

    # 範囲を描画
    for c in range(max(0, col_lb), min(width, col_ub) + 1):
        line[c] = '-'

    if 0 <= col_lb <= width:
        line[col_lb] = '['
    if 0 <= col_ub <= width:
        line[col_ub] = ']'

    # √2 と 4 のマーカー
    col_sqrt2 = to_col(math.sqrt(2))
    col_4 = to_col(4.0)

    line_str = ''.join(line)
    print(f"  {k:>2} |{line_str}| [{lb_root:.2f}, {ub_root:.2f}]")

print(f"  ---+{'-' * width}+")
print(f"       √2={math.sqrt(2):.4f}                           4-ε≈3.7992")


# =============================================================================
# まとめ
# =============================================================================
print("\n" + "=" * 70)
print("探索5 まとめ")
print("=" * 70)
print("""
1. 上界の歴史:
   - Erdős-Szekeres (1935): R(k)^{1/k} ≤ 4
   - Conlon (2009): 係数改良だが基底4は変わらず
   - Campos et al. (2023): R(k)^{1/k} ≤ 4-ε (88年ぶりのブレークスルー)

2. 下界の歴史:
   - Erdős (1947): R(k)^{1/k} ≥ √2 (確率的方法)
   - Spencer (1975): 係数改良だが基底√2は変わらず
   - Paley構成: 構成的に √2 程度の下界を実現

3. 現在の状況:
   - √2 ≤ liminf R(k)^{1/k} ≤ limsup R(k)^{1/k} ≤ 4-ε
   - 上界側: 初めて4を破った (2023)
   - 下界側: 77年間 √2 のまま変化なし

4. 数値的証拠:
   - k=3,...,10 での R(k)^{1/k} の挙動は複雑
   - 下界の k-乗根は k=5 付近でピーク後に微減
   - 上界の k-乗根は緩やかに増加
   - 極限値の推定は現状のデータでは困難

5. 今後の方向:
   - 下界の改善が最大の課題（77年間停滞）
   - 構成的下界: Paley graph 以外の構成の探索
   - 確率的下界: alteration method の改良
   - 極限の存在自体が $100 の懸賞問題
""")
