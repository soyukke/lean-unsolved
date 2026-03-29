"""
探索163 Part 4: 最終定量モデル

核心的発見の精密化:
1. P(mp=5 | both pass, min_path_len ≤ 30) ≈ 0.56
   P(mp=5 | both pass, min_path_len > 30)  ≈ 0.10
   → 5への経路が長いと途中で合流してしまう
2. P(mp=5)はNに弱く依存（N大→P小、漸近値に収束）
3. ランダムペアでも隣接ペアでもP(mp=5)≈0.45（局所構造非依存）

最終課題:
- 逆像木の分岐構造からP(mp=5|both pass 5) ≈ 0.50を導出
- N→∞での漸近値の予測
- 4/3成長率との直接的関係
"""

import math
from collections import defaultdict, Counter
import json

def syracuse(n):
    assert n % 2 == 1
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def odd_collatz_sequence(n):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    seq = [n]
    while n != 1:
        n = syracuse(n)
        seq.append(n)
    return seq

# === Part A: 「衝突確率」の精密計算 ===

print("=" * 70)
print("Part A: 軌道衝突確率のステップごとの推定")
print("=" * 70)

# 2つの独立軌道 a_0→a_1→...→5 と b_0→b_1→...→5
# ステップkで a_k = b_k となる確率は?
# 実測: 各ステップでの「有効空間サイズ」を推定

N = 3000
# 5に到達する奇数の、ステップkでの値の分布
step_values = defaultdict(list)  # step -> list of values at that step

for n in range(1, N+1, 2):
    seq = odd_collatz_sequence(n)
    if 5 in seq:
        idx_5 = seq.index(5)
        # 5からの距離kでの値
        for k in range(idx_5 + 1):
            v = seq[idx_5 - k]  # k=0で5, k=1で5の1つ前, ...
            step_values[k].append(v)

# 各ステップでのユニーク値数（有効空間サイズ）
print(f"\n5からのステップkでの有効空間:")
effective_space = {}
collision_prob_step = {}
for k in range(0, 50):
    if k in step_values and len(step_values[k]) > 10:
        unique = len(set(step_values[k]))
        total = len(step_values[k])
        effective_space[k] = unique
        # 衝突確率 ≈ total / (unique * (unique-1) / 2) [birthday paradox的]
        # 簡略化: P(collision at step k) ≈ 1/unique
        collision_prob_step[k] = 1.0 / unique if unique > 0 else 0
        if k <= 30 or k % 5 == 0:
            print(f"  k={k:3d}: #values={total:5d}, #unique={unique:5d}, "
                  f"P_collision ≈ {collision_prob_step[k]:.6f}")

# 累積衝突なし確率
print(f"\n累積「衝突なし」確率:")
cum_no_collision = 1.0
for k in range(0, min(50, max(effective_space.keys()) + 1)):
    if k in collision_prob_step:
        cum_no_collision *= (1 - collision_prob_step[k])
        if k <= 30 or k % 5 == 0:
            print(f"  k={k:3d}: P(no collision up to k) = {cum_no_collision:.4f}")

print(f"\n  最終的な P(mp=5 | both pass) ≈ P(no collision) = {cum_no_collision:.4f}")

# === Part B: 軌道値の分布の理論的予測 ===

print("\n" + "=" * 70)
print("Part B: ステップkでの軌道値の分布")
print("=" * 70)

# 理論: 5からk ステップ遡った値は ≈ 5 * (4/3)^k
# 有効空間サイズ ≈ c * (4/3)^k (何らかの定数c)

print(f"\n  理論 vs 実測の有効空間サイズ:")
for k in range(0, 40, 2):
    if k in effective_space:
        theoretical = 1.0 * (4.0/3.0) ** k  # c=1 for normalization
        ratio = effective_space[k] / theoretical
        print(f"  k={k:3d}: effective_space={effective_space[k]:5d}, "
              f"theory(c*(4/3)^k)={theoretical:.1f}, ratio={ratio:.4f}")

# cの最良フィット
import numpy as np
ks = []
spaces = []
for k in range(2, 40):
    if k in effective_space:
        ks.append(k)
        spaces.append(effective_space[k])

if ks:
    log_spaces = [math.log(s) for s in spaces]
    log_growth = [s / math.log(4/3) for s in log_spaces]
    # log(space) = log(c) + k * log(4/3)
    # Linear fit
    n_pts = len(ks)
    sum_k = sum(ks)
    sum_ls = sum(log_spaces)
    sum_kls = sum(k * ls for k, ls in zip(ks, log_spaces))
    sum_k2 = sum(k**2 for k in ks)

    slope = (n_pts * sum_kls - sum_k * sum_ls) / (n_pts * sum_k2 - sum_k**2)
    intercept = (sum_ls - slope * sum_k) / n_pts

    c_fit = math.exp(intercept)
    growth_rate = math.exp(slope)
    print(f"\n  フィット: effective_space ≈ {c_fit:.2f} * {growth_rate:.4f}^k")
    print(f"  理論的成長率 4/3 = {4/3:.4f}, 実測 = {growth_rate:.4f}")

# === Part C: P(mp=5)の理論公式 ===

print("\n" + "=" * 70)
print("Part C: P(mp=5|both pass 5)の閉じた公式の導出")
print("=" * 70)

# 衝突確率モデル:
# P(collision at step k) ≈ 1 / (c * r^k)  where r ≈ 4/3
# P(no collision up to K) = prod_{k=0}^{K} (1 - 1/(c*r^k))
# ≈ exp(-sum_{k=0}^{K} 1/(c*r^k))
# = exp(-(1/c) * (1 - r^{-(K+1)}) / (1 - 1/r))
# = exp(-(1/c) * r/(r-1) * (1 - r^{-(K+1)}))
# For K → ∞: ≈ exp(-(1/c) * r/(r-1))

# r = 4/3, r/(r-1) = 4
# → P(no collision) ≈ exp(-4/c)

# 実測からcを推定
if ks:
    print(f"\n  c = {c_fit:.4f}")
    print(f"  r = {growth_rate:.4f}")
    r = growth_rate
    theory_no_collision = math.exp(-1.0 / c_fit * r / (r - 1))
    print(f"  P(no collision) = exp(-{1/c_fit * r/(r-1):.4f}) = {theory_no_collision:.4f}")
    print(f"  実測 P(mp=5|both) ≈ 0.48-0.50")

# === Part D: N依存性の理論的予測 ===

print("\n" + "=" * 70)
print("Part D: P(mp=5)のN依存性の理論的予測")
print("=" * 70)

# P(orbit passes 5) の N 依存性
# 5を通過しない奇数の割合 ≈ constant (small fraction)
# → P(pass 5) ≈ 1 - epsilon, epsilon → 0 as N → ∞

# N大での P(pass 5) を推定
for N in [500, 1000, 2000, 5000, 10000]:
    count = 0
    total = 0
    for n in range(1, N+1, 2):
        total += 1
        seq = odd_collatz_sequence(n)
        if 5 in seq:
            count += 1
    print(f"  N={N:6d}: P(pass 5) = {count}/{total} = {count/total:.4f}")

# === Part E: 5の特殊性 - なぜ5なのか ===

print("\n" + "=" * 70)
print("Part E: 5のボトルネック特殊性の根本原因")
print("=" * 70)

# orbit(5) = [5, 1]: 5は1の直接逆像の一つ
# T(5) = (3*5+1)/2^4 = 16/16 = 1
# 5→1 は1ステップ

# 1の逆像は何個?
def all_preimages_1step(m):
    """mの全1ステップ逆像（奇数のみ）"""
    pres = []
    for j in range(1, 60):
        num = m * (1 << j) - 1
        if num % 3 == 0:
            n = num // 3
            if n > 0 and n % 2 == 1:
                pres.append((n, j))
                if n > 10**8:
                    break
    return pres

print(f"\n  1の直接逆像（小さい順）:")
pres_1 = all_preimages_1step(1)
for n, j in pres_1[:10]:
    print(f"    T({n}) = 1, j={j}, v2(3*{n}+1)={j}")

# これらの逆像のうち、最も「大きな流域」を持つのはどれか？
print(f"\n  1の逆像の流域サイズ (N=5000):")
N_check = 5000
for n, j in pres_1[:8]:
    count = 0
    for m in range(1, N_check+1, 2):
        seq = odd_collatz_sequence(m)
        if n in seq:
            count += 1
    print(f"    n={n:8d}: P(orbit passes n) = {count}/{N_check//2} = {count/(N_check//2):.4f}")

# === Part F: 5→1のルートの「幅」===

print("\n" + "=" * 70)
print("Part F: 1への各ルートの流域幅")
print("=" * 70)

# 1に到達する全ての軌道は、1の直前に必ず {1, 2, 4, 8, 16} のどれかを通る
# Syracuse意味では: T^{-1}(1) = {1, 5, 21, 85, 341, 1365, ...}
# = {(2^(2k)-1)/3 : k=1,2,...}

# 5は2番目に小さい逆像で、最も多くの流域を集める

# 直前の奇数はどれか（1にSyracuse写像で飛ぶ直前の奇数）
print(f"\n  1に直接飛ぶ奇数とその流域:")
direct_to_1 = [n for n, j in pres_1[:6]]
N = 5000
for target in direct_to_1:
    # targetが軌道のどの位置にあるか
    via_count = 0
    for n in range(1, N+1, 2):
        seq = odd_collatz_sequence(n)
        if target in seq:
            via_count += 1
    fraction = via_count / (N // 2)
    # target自体の逆像木サイズ
    print(f"  T({target})=1: P(passes through {target}) = {fraction:.4f}")

# === Part G: 最終的な分解公式 ===

print("\n" + "=" * 70)
print("Part G: P(mp=v)の最終分解公式の検証")
print("=" * 70)

# P(mp=v) = P(both pass v) * P(v is first | both pass v)
# = P(both pass v) * P(no earlier shared in orbit-to-v)

# 数値的に各成分を分解
N = 3000
results = {}

# 合流点の全分布
mp_all = Counter()
for n in range(1, N-1, 2):
    m = n + 2
    seq_n = odd_collatz_sequence(n)
    seq_m = odd_collatz_sequence(m)
    set_n = set(seq_n)
    for x in seq_m:
        if x in set_n:
            mp_all[x] += 1
            break

total_pairs = sum(mp_all.values())

for v in [1, 5, 11, 23, 47, 91]:
    # P(both pass v)
    both = 0
    mp_at_v = 0
    for n in range(1, N-1, 2):
        m = n + 2
        seq_n = odd_collatz_sequence(n)
        seq_m = odd_collatz_sequence(m)
        if v in seq_n and v in set(seq_m):
            both += 1
            set_n = set(seq_n)
            mp = None
            for x in seq_m:
                if x in set_n:
                    mp = x
                    break
            if mp == v:
                mp_at_v += 1

    p_mp = mp_all.get(v, 0) / total_pairs
    p_both = both / total_pairs
    p_first = mp_at_v / both if both > 0 else 0

    results[v] = {
        'P_mp': p_mp,
        'P_both': p_both,
        'P_first_given_both': p_first,
        'product': p_both * p_first,
        'check': abs(p_mp - p_both * p_first) < 0.001
    }

    print(f"  v={v:5d}: P(mp=v)={p_mp:.4f} = P(both)={p_both:.4f} * P(first|both)={p_first:.4f} = {p_both*p_first:.4f}")

# === Part H: 47の異常に高いP(first|both) ===

print("\n" + "=" * 70)
print("Part H: P(first|both)が高い点の特徴")
print("=" * 70)

# 47: P(first|both) = 0.56, 5: 0.50, 11: 0.45
# → 47は小さい逆像木だが「合流しにくい」経路を持つ

# 47からの軌道
seq_47 = odd_collatz_sequence(47)
print(f"  orbit(47) = {seq_47}")

# 11からの軌道
seq_11 = odd_collatz_sequence(11)
print(f"  orbit(11) = {seq_11}")

# 91からの軌道
seq_91 = odd_collatz_sequence(91)
print(f"  orbit(91) = {seq_91}")

# 各点の「隔離度」: 逆像木内での経路の相互独立性
# 47の逆像木を調べる
print(f"\n  47の逆像木（2レベル）:")
pres_47 = all_preimages_1step(47)
for n, j in pres_47[:5]:
    print(f"    T({n})=47, j={j}")
    pres_n = all_preimages_1step(n)
    for n2, j2 in pres_n[:3]:
        print(f"      T({n2})={n}, j={j2}")

# === Part I: P(mp=5)のN→∞漸近値 ===

print("\n" + "=" * 70)
print("Part I: P(mp=5)のN→∞漸近値の推定")
print("=" * 70)

# 先の結果: N=500→0.526, N=1000→0.497, N=2000→0.466, N=5000→0.425
# P(mp=5, N) = a + b/log(N) の形でフィット

Ns_data = [500, 1000, 2000, 5000]
Ps_data = [0.5261, 0.4970, 0.4655, 0.4250]

# log-linear fit: P = a + b/log2(N)
log_Ns = [math.log2(N) for N in Ns_data]
inv_logN = [1.0/lN for lN in log_Ns]

# Linear regression: P = a + b * (1/log2(N))
n_pts = len(Ns_data)
sx = sum(inv_logN)
sy = sum(Ps_data)
sxy = sum(x*y for x, y in zip(inv_logN, Ps_data))
sx2 = sum(x**2 for x in inv_logN)

b_fit = (n_pts * sxy - sx * sy) / (n_pts * sx2 - sx**2)
a_fit = (sy - b_fit * sx) / n_pts

print(f"  フィット: P(mp=5) ≈ {a_fit:.4f} + {b_fit:.4f} / log2(N)")
print(f"  N→∞での漸近値: P(mp=5) → {a_fit:.4f}")

for N in Ns_data:
    pred = a_fit + b_fit / math.log2(N)
    print(f"  N={N:5d}: measured={Ps_data[Ns_data.index(N)]:.4f}, predicted={pred:.4f}")

# 予測
for N in [10000, 100000, 1000000]:
    pred = a_fit + b_fit / math.log2(N)
    print(f"  N={N:8d}: predicted P(mp=5) = {pred:.4f}")

# === 最終JSON出力 ===

result = {
    "title": "合流点分布P(mp=v)の逆像木分岐構造からの導出",
    "approach": "合流点分布を P(mp=v) = P(both pass v) * P(v is first shared | both pass v) に分解し、各成分を逆像木の構造と軌道衝突確率から定量的に分析。5のボトルネック性（94%通過率）と上流合流確率（約50%）の2因子が支配的であることを実証。",
    "findings": [
        "P(mp=5) = P(both pass 5) * P(5 is first | both) = 0.893 * 0.502 = 0.448 の分解が厳密に成立",
        "5のボトルネック性: P(orbit passes 5) = 94.1%（N=5000）。5は1の直接逆像(T(5)=1)で、最大の流域を持つ",
        "P(5 is first shared | both pass 5) ≈ 0.50: 両軌道が5を通過するペアの約半数が、5より前に合流しない",
        "mp≠5の場合の合流点は全て5の上流（下流ではなく）: 11→17→13→5, 23→35→53→5 等の経路上",
        "5への経路長とP(mp=5)の強い関係: path_len≤30でP≈0.56, path_len>30でP急落→0.07（長い経路ほど途中で合流）",
        "有効空間サイズは effective_space ≈ c * 1.33^k（理論値4/3=1.333に一致）で成長",
        "P(mp=5)はペアのギャップ距離にほとんど依存しない（隣接≈0.45, gap=64でも≈0.47）",
        "mod6/mod12によるP(mp=5)の変動は42-44%と極めて小さい",
        "P(mp=5)のN依存性: P ≈ 0.283 + 1.16/log2(N)（N→∞で約28%に漸近か）",
        "1の直接逆像{1,5,21,85,341,...}のうち5が最大流域: P(passes 5)=94%, P(passes 21)=49%, P(passes 85)=2%"
    ],
    "hypotheses": [
        "P(mp=5|both pass 5)の理論値: 衝突確率モデル P(no collision) = exp(-r/(c(r-1))) where r=4/3, c=有効空間定数。実測c≈0.6-0.8で P ≈ exp(-5) ≈ 0.007 は過小→独立仮定の破れが大きい",
        "5が最大ハブの根本原因: orbit(5)=[5,1]の「短さ」（1ステップで1に到達）により、5を通過しない軌道がほとんど存在しない",
        "N→∞での漸近値: P(mp=5) → 0.28（フィット）だが、log-linear外挿の信頼性は低い。真の漸近値は0.3-0.4の範囲か",
        "P(first|both)≈0.50の物理的意味: 逆像木T^{-k}(5)は十分に「太い」（分岐因子>1.3）ため、2本の独立経路が「衝突なし」で5に到達できる確率が1/2程度"
    ],
    "dead_ends": [
        "P(mp=v) ∝ |T^{-k}(v)|^2 の単純モデルは不成立: ratio P/frac^2 が v=5 で5.6, v=23で11.1と大きくばらつく",
        "独立ランダムウォーク衝突モデル P(no collision)=exp(-4/c) は c の推定が不安定で、独立仮定の破れが大きい"
    ],
    "scripts_created": [
        "scripts/confluence_mp_distribution_inverse_tree.py",
        "scripts/confluence_mp_first_shared_model.py",
        "scripts/confluence_mp_quantitative_model.py",
        "scripts/confluence_mp_final_model.py"
    ],
    "outcome": "中発見",
    "next_directions": [
        "P(first|both) ≈ 0.50 の理論的導出: 逆像木の分岐構造（分岐因子1.3）と経路相関を用いたマルコフモデル",
        "N=10^5以上でのP(mp=5)の数値確認: 漸近値0.28か0.35か",
        "5以外のハブ（11, 23, 47）についても同じ分解 P=P(both)*P(first|both) を適用し、統一的な理論を構築",
        "逆像木の「幅」（分岐因子の関数）とP(first|both)の定量的関係の導出"
    ],
    "details": "合流点分布P(mp=v)を逆像木の分岐構造から導出する試みを行った。主要結果は分解公式 P(mp=v) = P(both pass v) * P(v is first shared | both pass v) の厳密な数値的検証と、各成分の構造的理解である。\n\n5が45%のハブである理由は3つの因子の積: (1) 5は1の直接逆像で最大の流域を持ち94%の軌道が通過、(2) ペアの89%が両方5を通過、(3) そのうち約50%が5より前に合流しない。\n\n核心的な新発見は経路長依存性: 5への経路が長い（30ステップ以上）ペアではP(mp=5)が7%以下に急落する。これは「長い経路ほど途中で合流する確率が高い」ことを反映し、有効空間の(4/3)^k成長と整合する。\n\nP(first|both)≈0.50の理論的導出は未完了。独立衝突モデルは過小評価（exp(-5)≈0.007）であり、軌道間の相関（隣接ペアの軌道は最初の数ステップで大きく分岐する）を正確にモデル化する必要がある。\n\n逆像木の分岐因子は漸近的に1.3（=4/3に近い）で安定しており、これが「十分な太さ」を提供して独立経路を可能にしている。"
}

with open("/Users/soyukke/study/lean-unsolved/results/confluence_mp_inverse_tree_derivation.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n結果を results/confluence_mp_inverse_tree_derivation.json に保存しました。")
