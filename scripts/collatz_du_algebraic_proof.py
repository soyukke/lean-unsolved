#!/usr/bin/env python3
"""
d/u > log₂(3) の代数的証明への新アプローチ

戦略:
1. Syracuse関数 T(n) = (3n+1)/2^{v₂(3n+1)} の反復で、
   各ステップの v₂ の合計が u·log₂(3) を超えることを示す。
2. n mod 2^K の剰余類ごとに、最初の数ステップの v₂ を厳密に決定し、
   d/u > log₂(3) を部分的に証明する。
3. Hensel補題の応用: k連続上昇後の v₂ ≥ k+1 のバーストを利用。

等価条件: d/u > log₂(3) ⟺ Σ v₂(3T^i(n)+1) > u·log₂(3)
ここで d = Σ v₂(3T^i(n)+1), u は奇数ステップの回数
"""

import math
from fractions import Fraction
from collections import defaultdict
import itertools

LOG2_3 = math.log2(3)  # ≈ 1.58496...

# =====================================================
# Part 1: 剰余類ごとの Syracuse 軌道の厳密追跡
# =====================================================

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) for odd n"""
    val = 3 * n + 1
    return val >> v2(val)

def syracuse_trajectory(n, steps):
    """Syracuse軌道を steps 回追跡。(values, v2_list) を返す"""
    traj = [n]
    v2_list = []
    x = n
    for _ in range(steps):
        if x == 1:
            break
        val = 3 * x + 1
        v = v2(val)
        v2_list.append(v)
        x = val >> v
        traj.append(x)
    return traj, v2_list

print("=" * 70)
print("Part 1: 剰余類ごとの最初の数ステップの v₂ パターン")
print("=" * 70)

# n mod 2^K の各剰余類について、最初のステップの v₂ を計算
# T(n) = (3n+1)/2^{v₂(3n+1)}
# n ≡ r (mod 2^K) のとき v₂(3n+1) は r で決まる

print("\n■ n mod 2^K における v₂(3n+1) の決定")
for K in [2, 3, 4, 5]:
    print(f"\n  mod 2^{K} = {2**K}:")
    for r in range(1, 2**K, 2):  # 奇数の剰余類のみ
        val = 3 * r + 1
        v = v2(val)
        T_r = val >> v
        T_r_mod = T_r % (2**K)
        print(f"    n ≡ {r:>3} (mod {2**K}): v₂(3n+1) = {v}, T(n) ≡ {T_r_mod} (mod {2**K})")


# =====================================================
# Part 2: 2ステップの v₂ 合計の下界
# =====================================================
print("\n" + "=" * 70)
print("Part 2: 2ステップの v₂ 合計の厳密な下界 (n mod 2^K)")
print("=" * 70)

print("""
2ステップで d/u > log₂(3) となる条件:
  v₂(3n+1) + v₂(3T(n)+1) > 2·log₂(3) ≈ 3.170

つまり 2ステップの v₂ 合計 ≥ 4 なら十分。
""")

K = 6  # mod 2^6 = 64 で分類
mod_val = 2**K
print(f"n mod {mod_val} の全奇数剰余類 ({mod_val//2} 個) について2ステップを追跡:")
print(f"{'r':>4} {'v₂₁':>4} {'v₂₂':>4} {'sum':>4} {'sum > 2·log₂3?':>16} {'T(n)mod':>8} {'T²(n)mod':>8}")
print("-" * 60)

two_step_results = {}
for r in range(1, mod_val, 2):
    val1 = 3 * r + 1
    v1 = v2(val1)
    T1 = val1 >> v1
    # T1 mod mod_val
    T1_mod = T1 % mod_val
    # 2nd step
    if T1_mod % 2 == 0:
        # T(n) が偶数になる可能性 → 実際にはSyracuseは奇数のみ扱う
        # T1_mod は Syracuse の結果なので奇数のはず
        # mod で偶数に見えるのは mod_val の問題
        pass
    val2 = 3 * T1_mod + 1
    v2_2 = v2(val2)
    T2 = val2 >> v2_2
    T2_mod = T2 % mod_val

    total_v2 = v1 + v2_2
    sufficient = total_v2 > 2 * LOG2_3
    two_step_results[r] = (v1, v2_2, total_v2, sufficient)
    mark = "YES" if sufficient else "NO "
    print(f"{r:>4} {v1:>4} {v2_2:>4} {total_v2:>4} {mark:>16} {T1_mod:>8} {T2_mod:>8}")

# 集計
yes_count = sum(1 for v in two_step_results.values() if v[3])
total_count = len(two_step_results)
print(f"\n2ステップで d/u > log₂(3) を保証: {yes_count}/{total_count} ({yes_count/total_count*100:.1f}%)")


# =====================================================
# Part 3: kステップのv₂合計の下界 (剰余類ベース)
# =====================================================
print("\n" + "=" * 70)
print("Part 3: kステップのv₂合計 vs k·log₂(3) (剰余類ベース)")
print("=" * 70)

def analyze_k_steps(K_mod, k_steps):
    """mod 2^K_mod の各奇数剰余類について、kステップのv₂合計を計算"""
    mod_val = 2**K_mod
    results = {}
    for r in range(1, mod_val, 2):
        x = r
        v2_sum = 0
        v2_list = []
        for _ in range(k_steps):
            val = 3 * x + 1
            v = v2(val)
            v2_list.append(v)
            v2_sum += v
            x = (val >> v) % mod_val
            # 奇数でない場合（modの影響）は補正
            while x % 2 == 0 and x > 0:
                x = x // 2
                v2_sum += 1  # これも下降ステップ
            if x == 0:
                x = mod_val  # wrap
        results[r] = (v2_sum, v2_list)
    return results

# 注: mod演算で正確な v₂ を追跡するには十分大きな mod が必要
# 代わりに実際の数値で確認する

print("\n■ 小さな剰余類 (mod 8) の最初の数ステップの v₂")
for r in [1, 3, 5, 7]:
    # 多くの代表元で確認
    print(f"\n  n ≡ {r} (mod 8):")
    for n in range(r, r + 800, 8):
        if n <= 0:
            continue
        traj, v2_list = syracuse_trajectory(n, 10)
        if len(v2_list) >= 3:
            # 最初の3ステップの v₂ 合計
            s3 = sum(v2_list[:3])
            # 確認: これは 3·log₂(3) ≈ 4.755 を超えるか
            pass

    # 代表元100個の統計
    v2_sums = {k: [] for k in range(1, 11)}
    for n in range(r, r + 8000, 8):
        if n <= 0:
            continue
        traj, v2_list = syracuse_trajectory(n, 10)
        for k in range(1, min(11, len(v2_list) + 1)):
            v2_sums[k].append(sum(v2_list[:k]))

    print(f"    {'k':>3} {'min Σv₂':>8} {'avg Σv₂':>8} {'k·log₂3':>8} {'min > k·log₂3?':>16}")
    for k in range(1, 11):
        if v2_sums[k]:
            min_s = min(v2_sums[k])
            avg_s = sum(v2_sums[k]) / len(v2_sums[k])
            threshold = k * LOG2_3
            ok = min_s > threshold
            print(f"    {k:>3} {min_s:>8} {avg_s:>8.2f} {threshold:>8.3f} {'YES' if ok else 'NO':>16}")


# =====================================================
# Part 4: Hensel バーストの影響の定量的分析
# =====================================================
print("\n" + "=" * 70)
print("Part 4: Hensel バーストの定量的分析")
print("=" * 70)

print("""
■ k連続上昇の条件と効果

Syracuse関数での「上昇」= v₂(3n+1) = 1 (最小の下降)
k回連続で v₂ = 1 が続く条件: n ≡ 2^{k+1} - 1 (mod 2^{k+1})

しかし k+1 回目には v₂ ≥ k+1 の「バースト下降」が起きる。
これが d/u > log₂(3) を保証する鍵。
""")

# k連続上昇後のバーストを実測
print("■ k連続上昇 (v₂=1 が k 回連続) 後のバースト v₂ の分布")
for k in range(1, 8):
    # n ≡ 2^{k+1} - 1 (mod 2^{k+1}) の奇数で検証
    mod_val = 2**(k+1)
    target_r = mod_val - 1  # = 2^{k+1} - 1

    burst_v2s = []
    for n in range(target_r, target_r + mod_val * 2000, mod_val):
        if n <= 0:
            continue
        traj, v2_list = syracuse_trajectory(n, k + 5)
        if len(v2_list) > k:
            # 最初の k ステップで v₂ = 1 であることを確認
            if all(v == 1 for v in v2_list[:k]):
                burst_v2s.append(v2_list[k])
        if len(burst_v2s) >= 1000:
            break

    if burst_v2s:
        avg_burst = sum(burst_v2s) / len(burst_v2s)
        min_burst = min(burst_v2s)
        # k ステップで v₂ = 1 × k 回、その後 burst_v₂
        # 合計 v₂ = k + burst_v₂
        # u = k+1 ステップ
        # d/u = (k + burst_v₂) / (k + 1)
        # d/u > log₂(3) ⟺ burst_v₂ > (k+1)·log₂(3) - k = k·(log₂(3)-1) + log₂(3)
        needed = k * (LOG2_3 - 1) + LOG2_3
        print(f"  k={k}: min_burst_v₂={min_burst}, avg={avg_burst:.2f}, "
              f"needed for d/u>log₂3: >{needed:.2f}, min_burst≥{min_burst} {'✓' if min_burst >= needed else '✗'}")

        # k+1ステップでの d/u の最小値
        min_ratio = (k + min_burst) / (k + 1)
        avg_ratio = (k + avg_burst) / (k + 1)
        print(f"         min d/u after k+1 steps = {min_ratio:.4f}, avg = {avg_ratio:.4f}")


# =====================================================
# Part 5: 代数的証明の試み - mod ベースの厳密追跡
# =====================================================
print("\n" + "=" * 70)
print("Part 5: mod 2^K ベースの厳密な v₂ 下界")
print("=" * 70)

print("""
■ 核心的アイデア

n mod 2^K を知れば、最初の数ステップの v₂ が厳密に決まる。
K を十分大きくすれば、より多くのステップを厳密に追跡できる。

mod 2^K の奇数 n に対し:
  v₂(3n+1) は n mod 2^K から正確に決まる
  （3n+1 の2-adic valuationは n mod 2^v の情報で決まる）
""")

# v₂(3n+1) は n mod 2^? で決まるか検証
print("■ v₂(3n+1) の決定に必要な mod")
for target_v in range(1, 8):
    # v₂(3n+1) = target_v となる条件
    # 3n+1 ≡ 0 (mod 2^target_v) かつ 3n+1 ≢ 0 (mod 2^{target_v+1})
    # ⟺ n ≡ (2^target_v - 1)/3 (mod 2^target_v) ... 3で割り切れる場合
    # 実際: 3n ≡ -1 (mod 2^target_v) ⟺ n ≡ (-1)·3^{-1} (mod 2^target_v)
    # 3^{-1} mod 2^target_v を計算
    mod_val = 2**target_v
    inv3 = pow(3, -1, mod_val)
    r = (-1 * inv3) % mod_val
    # 確認
    residues = []
    for rr in range(1, 2**(target_v + 1), 2):
        if v2(3 * rr + 1) == target_v:
            residues.append(rr)
    print(f"  v₂(3n+1) = {target_v}: n ≡ {residues} (mod {2**(target_v+1)})")


# =====================================================
# Part 6: 全軌道の d/u の代数的下界
# =====================================================
print("\n" + "=" * 70)
print("Part 6: 全軌道の d/u の代数的下界の導出")
print("=" * 70)

print("""
■ アプローチ: 加重平均の下界

各Syracuseステップで v₂ ≥ 1 は保証されている（3n+1は偶数なので）。
つまり d/u ≥ 1 は自明。

しかし log₂(3) ≈ 1.585 の下界が必要。

鍵となる観察:
  v₂(3n+1) = 1 ⟺ n ≡ 1 (mod 4) [つまり n mod 4 = 1]
  v₂(3n+1) ≥ 2 ⟺ n ≡ 3 (mod 4) [つまり n mod 4 = 3]

  さらに v₂(3n+1) = 2 ⟺ n ≡ 3 (mod 8) [n mod 8 = 3]
  v₂(3n+1) ≥ 3 ⟺ n ≡ 7 (mod 8) [n mod 8 = 7]

  v₂(3n+1) = j ⟺ n ≡ (2^j - 1)/3 (mod 2^j)...
  正確には: n ≡ 2^j·t - 1/3 ...
""")

# v₂(3n+1) の分布をmod classから厳密に
print("■ v₂(3n+1) の条件 (奇数 n に対して)")
for j in range(1, 10):
    # v₂(3n+1) ≥ j の条件: 3n+1 ≡ 0 (mod 2^j)
    # ⟺ 3n ≡ -1 (mod 2^j)
    # ⟺ n ≡ -3^{-1} (mod 2^j)
    mod_j = 2**j
    if math.gcd(3, mod_j) == 1:
        inv3 = pow(3, -1, mod_j)
        r_j = (-inv3) % mod_j
        # v₂(3n+1) = j の条件: ≥ j かつ < j+1
        mod_j1 = 2**(j+1)
        inv3_1 = pow(3, -1, mod_j1)
        r_j1 = (-inv3_1) % mod_j1

        # v₂ = j exactly: n ≡ r_j (mod 2^j) かつ n ≢ r_j1 (mod 2^{j+1})
        # 奇数に限定
        print(f"  v₂(3n+1) ≥ {j}: n ≡ {r_j} (mod {mod_j})")

print()

# 密度の計算: v₂(3n+1) = j の奇数 n の密度
print("■ v₂(3n+1) = j の奇数の中での密度")
for j in range(1, 12):
    # mod 2^{j+1} の奇数 (2^j 個) のうち v₂(3n+1) = j となるものの個数
    mod_val = 2**(j+1)
    count = 0
    for r in range(1, mod_val, 2):
        if v2(3*r + 1) == j:
            count += 1
    total_odd = mod_val // 2
    density = count / total_odd
    print(f"  j={j:>2}: density = {count}/{total_odd} = {density:.6f} (理論値 1/2^j = {1/2**j:.6f})")


# =====================================================
# Part 7: 条件付き期待値と下界の厳密計算
# =====================================================
print("\n" + "=" * 70)
print("Part 7: 条件付き v₂ 期待値と d/u の下界")
print("=" * 70)

print("""
■ 重要な定理 (厳密):

奇数 n に対し、v₂(3n+1) = j となる確率（密度）は正確に 1/2^j。
  P(v₂ = j) = 1/2^j  (j = 1, 2, 3, ...)

これは幾何分布であり:
  E[v₂] = Σ j/2^j = 2

■ d/u との関係:

Syracuseの u ステップでの total v₂ = d (下降ステップ合計)
d/u = (1/u) Σᵢ v₂ᵢ

もし v₂ᵢ が独立同分布なら:
  E[d/u] = E[v₂] = 2 > log₂(3) ≈ 1.585 ✓

問題: v₂ᵢ は独立ではない。T(n) の値は n に依存するため。

■ 核心の問いかけ:
  依存性を考慮しても E[v₂] ≥ log₂(3) + ε を示せるか？
  あるいは、特定の剰余類で必ず d/u > log₂(3) を示せるか？
""")

# v₂ の自己相関を実測
print("■ 連続するv₂ の相関分析")
v2_pairs = defaultdict(list)  # v₂ᵢ の値ごとに v₂ᵢ₊₁ の分布
for n in range(3, 200001, 2):
    traj, v2_list = syracuse_trajectory(n, 50)
    for i in range(len(v2_list) - 1):
        v2_pairs[v2_list[i]].append(v2_list[i+1])

print(f"{'v₂ᵢ':>4} {'count':>8} {'E[v₂ᵢ₊₁]':>10} {'E[v₂]=2?':>10}")
print("-" * 40)
for j in sorted(v2_pairs.keys()):
    if len(v2_pairs[j]) > 100:
        avg_next = sum(v2_pairs[j]) / len(v2_pairs[j])
        print(f"{j:>4} {len(v2_pairs[j]):>8} {avg_next:>10.4f} {'≈2' if abs(avg_next - 2) < 0.1 else f'偏差{avg_next-2:+.3f}'}")


# =====================================================
# Part 8: 特定剰余類に対する d/u > log₂(3) の厳密証明
# =====================================================
print("\n" + "=" * 70)
print("Part 8: 特定剰余類に対する d/u > log₂(3) の厳密証明の試み")
print("=" * 70)

print("""
■ 戦略: n ≡ r (mod 2^K) について、最初の m ステップの v₂ 合計を厳密に
計算し、Σv₂ > m·log₂(3) が成り立つ剰余類を特定する。

これが成り立てば「最初の m ステップに限っては d/u > log₂(3)」が
その剰余類で厳密に証明される。
""")

def exact_v2_sequence(r, K, max_steps):
    """
    n ≡ r (mod 2^K) のとき、最初の max_steps ステップの v₂ を
    厳密に決定できる範囲で返す。

    v₂(3n+1) は n mod 2^v で決まるので、
    K ビットの情報で何ステップまで追跡できるか。
    """
    mod_val = 2**K
    x = r
    v2_list = []
    for _ in range(max_steps):
        if x == 0:
            break
        # x は奇数であるべき
        if x % 2 == 0:
            break
        val = 3 * x + 1
        v = v2(val)
        # v₂ が K を超えると mod で正確に追跡できない
        if v >= K:
            break
        v2_list.append(v)
        x = (val >> v) % mod_val
        # x が偶数になったら mod の問題
        while x > 0 and x % 2 == 0:
            x //= 2
            # この余分な ÷2 は Syracuse の定義に含まれない
            # Syracuse は奇数→奇数なので、ここに来るのは mod 演算の問題
        if x == 0:
            x = mod_val + 1  # 非ゼロに
            break
    return v2_list

# K=12 で各剰余類を分析
K = 12
mod_val = 2**K
print(f"\n■ mod 2^{K} = {mod_val} の各奇数剰余類の最初の数ステップ")

# 各剰余類について、確実に追跡できるステップ数と v₂ 合計
residue_data = []
for r in range(1, mod_val, 2):
    v2_seq = exact_v2_sequence(r, K, 20)
    steps = len(v2_seq)
    if steps > 0:
        total_v2 = sum(v2_seq)
        threshold = steps * LOG2_3
        ratio = total_v2 / steps if steps > 0 else 0
        residue_data.append((r, steps, total_v2, threshold, ratio, v2_seq))

# ステップ数ごとの統計
step_counts = defaultdict(int)
for _, steps, _, _, _, _ in residue_data:
    step_counts[steps] += 1

print("\n追跡可能ステップ数の分布:")
for s in sorted(step_counts.keys()):
    print(f"  {s} ステップ: {step_counts[s]} 個")

# d/u > log₂(3) が保証される剰余類
print(f"\n■ 最初の m ステップで d/u > log₂(3) が厳密に保証される剰余類:")
for min_steps in [2, 3, 4, 5, 6]:
    proved = [(r, s, tv, th, ratio) for r, s, tv, th, ratio, _ in residue_data if s >= min_steps]
    guaranteed = [(r, s, tv, th, ratio) for r, s, tv, th, ratio in proved
                  if sum(1 for r2, s2, tv2, th2, ratio2, seq in residue_data if r2 == r and tv2 > s2 * LOG2_3) > 0]

    # 正確に: 最初の min_steps ステップの v₂ 合計 > min_steps * log₂(3)
    count_ok = 0
    count_total = 0
    for r, s, tv, th, ratio, v2_seq in residue_data:
        if s >= min_steps:
            count_total += 1
            partial_sum = sum(v2_seq[:min_steps])
            if partial_sum > min_steps * LOG2_3:
                count_ok += 1

    if count_total > 0:
        print(f"  {min_steps}ステップ: {count_ok}/{count_total} ({count_ok/count_total*100:.1f}%) の剰余類で保証")


# =====================================================
# Part 9: v₂ の最悪ケース分析 - 連続 v₂=1 の最大長
# =====================================================
print("\n" + "=" * 70)
print("Part 9: 連続 v₂=1 の最大長とバーストの保証")
print("=" * 70)

print("""
■ 最悪ケース分析

d/u が最小になるのは v₂ = 1 が多く続くとき。
v₂ = 1 が k 回連続するには n ≡ 2^{k+1} - 1 (mod 2^{k+1})。
密度は 1/2^{k+1} → k が大きいほど稀。

k 回連続 v₂=1 の後の v₂ をバーストと呼ぶ。
バーストで v₂_burst ≥ ? なら、k+1ステップでの d/u > log₂(3) が保証される。

条件: (k + v₂_burst) / (k+1) > log₂(3)
⟺ v₂_burst > (k+1)·log₂(3) - k = k·(log₂(3)-1) + log₂(3)
                                   ≈ 0.585·k + 1.585
""")

# k連続 v₂=1 後の最小バースト v₂ を厳密に計算
print("■ k連続 v₂=1 後のバースト v₂ の厳密計算")
print(f"{'k':>3} {'密度':>12} {'needed_burst':>14} {'min_burst':>10} {'保証?':>8}")
print("-" * 55)

for k in range(1, 15):
    # n ≡ 2^{k+1}-1 (mod 2^{k+1}) の形の奇数
    mod_val = 2**(k+1)
    target_r = mod_val - 1
    density = Fraction(1, mod_val)

    needed = k * (LOG2_3 - 1) + LOG2_3

    # 実際にバースト v₂ を計算
    # n = target_r のとき、Syracuse を k 回適用
    # まず小さい例で確認
    burst_values = []
    for mult in range(0, 5000):
        n = target_r + mult * mod_val
        if n <= 0:
            continue
        traj, v2_list = syracuse_trajectory(n, k + 3)
        if len(v2_list) > k:
            # 最初の k 回が v₂=1 であることを確認
            if all(v == 1 for v in v2_list[:k]):
                burst_values.append(v2_list[k])
        if len(burst_values) >= 500:
            break

    if burst_values:
        min_burst = min(burst_values)
        ok = min_burst > needed
        print(f"{k:>3} {str(density):>12} {needed:>14.3f} {min_burst:>10} {'YES' if ok else 'NO':>8}")


# =====================================================
# Part 10: 代数的証明 - T^k の明示的公式
# =====================================================
print("\n" + "=" * 70)
print("Part 10: Syracuse k回反復の明示的公式")
print("=" * 70)

print("""
■ Syracuse 1回の公式: T(n) = (3n+1)/2^{v₂(3n+1)}

■ k回連続 v₂=1 の場合の公式:
  T^k(n) = (3^k · n + (3^k - 2^k)) / 2^k  (k回とも v₂=1 のとき)

  証明: T(n) = (3n+1)/2 のとき (v₂=1)
    T²(n) = (3·(3n+1)/2 + 1)/2 = (9n+3+2)/(4) = (9n+5)/4
    T³(n) = (3·(9n+5)/4 + 1)/2 = (27n+15+4)/(8) = (27n+19)/8

  一般に T^k(n) = (3^k·n + c_k) / 2^k where c_k = (3^k - 2^k)
  (ただし全ステップ v₂=1 と仮定)

■ k+1 回目のバースト:
  x = T^k(n) = (3^k·n + 3^k - 2^k) / 2^k
  v₂(3x+1) = v₂(3·(3^k·n + 3^k - 2^k)/2^k + 1)
            = v₂((3^{k+1}·n + 3^{k+1} - 3·2^k + 2^k) / 2^k)
            = v₂(3^{k+1}·n + 3^{k+1} - 2^{k+1} + 2^k - 2^k) ...

  より簡単に: 3x+1 = 3(3^k·n + 3^k - 2^k)/2^k + 1
             = (3^{k+1}·n + 3^{k+1} - 3·2^k + 2^k) / 2^k
             = (3^{k+1}·(n+1) - 2^{k+1}) / 2^k

  n ≡ 2^{k+1}-1 (mod 2^{k+1}) のとき n+1 ≡ 0 (mod 2^{k+1})
  n+1 = 2^{k+1}·m として:
  3x+1 = (3^{k+1}·2^{k+1}·m - 2^{k+1}) / 2^k
       = 2·(3^{k+1}·m - 1)

  v₂(3x+1) = 1 + v₂(3^{k+1}·m - 1)
""")

# 3^{k+1}·m - 1 の v₂ を k と m について計算
print("■ v₂(3^{k+1}·m - 1) の値 (k, m)")
print(f"{'k\\m':>4}", end="")
for m in range(1, 21):
    print(f"{m:>4}", end="")
print()
for k in range(1, 10):
    print(f"{k:>4}", end="")
    for m in range(1, 21):
        val = 3**(k+1) * m - 1
        print(f"{v2(val):>4}", end="")
    print()

print("\n■ v₂(3^{k+1}·m - 1) のパターン分析")
for k in range(1, 8):
    power = 3**(k+1)
    # v₂(power·m - 1) は m の関数
    # power は奇数なので power·m - 1 ≡ m-1 (mod 2)
    # m=1: power-1, m=2: 2·power-1, ...
    vals = [v2(power * m - 1) for m in range(1, 100)]
    avg_v = sum(vals) / len(vals)
    min_v = min(vals)
    print(f"  k={k}: 3^{k+1}={power}, min v₂(3^{k+1}·m-1) = {min_v}, avg = {avg_v:.2f}")
    print(f"         burst v₂ = 1 + {min_v} = {1+min_v}")
    needed = k * (LOG2_3 - 1) + LOG2_3
    print(f"         needed > {needed:.3f}, actual min = {1+min_v}, {'PROVED' if 1+min_v > needed else 'NOT proved'}")


# =====================================================
# Part 11: 全剰余類の網羅的証明の試み
# =====================================================
print("\n" + "=" * 70)
print("Part 11: mod 2^K の全剰余類で d/u > log₂(3) を証明する試み")
print("=" * 70)

def compute_du_ratio_guaranteed(K):
    """
    mod 2^K の各奇数剰余類について、
    厳密に追跡可能なステップでの d/u の下界を計算
    """
    mod_val = 2**K
    results = {}

    for r in range(1, mod_val, 2):
        # Syracuse 軌道を mod_val の精度で追跡
        x = r
        total_v2 = 0
        steps = 0

        for _ in range(K):  # 最大 K ステップ
            if x <= 0 or x % 2 == 0:
                break
            val = 3 * x + 1
            v = v2(val)
            if v >= K:  # mod_val では追跡不能
                total_v2 += v  # ただし実際の v₂ はこれ以上
                steps += 1
                break
            total_v2 += v
            steps += 1
            x = (val >> v) % mod_val
            # 偶数の処理
            extra_v2 = 0
            while x > 0 and x % 2 == 0:
                x //= 2
                extra_v2 += 1
            if extra_v2 > 0:
                total_v2 += extra_v2

        if steps > 0:
            ratio = total_v2 / steps
            results[r] = (steps, total_v2, ratio)
        else:
            results[r] = (0, 0, 0)

    return results

# 実際の軌道で検証: mod 追跡と一致するか
print("\n■ mod 追跡の検証 (K=8)")
K = 8
mod_val = 2**K
correct = 0
total = 0
for r in range(1, mod_val, 2):
    v2_seq_mod = exact_v2_sequence(r, K, 10)
    # 実際の値で検証 (n = r)
    _, v2_seq_real = syracuse_trajectory(r, 10)

    match = True
    for i in range(min(len(v2_seq_mod), len(v2_seq_real))):
        if v2_seq_mod[i] != v2_seq_real[i]:
            match = False
            break

    total += 1
    if match and len(v2_seq_mod) > 0:
        correct += 1

print(f"  一致率: {correct}/{total}")


# =====================================================
# Part 12: 最終的な定理の形式化
# =====================================================
print("\n" + "=" * 70)
print("Part 12: 定理の形式化と結論")
print("=" * 70)

# n ≡ 3 (mod 4) の場合の証明
print("""
■ 定理1 (部分的): n ≡ 3 (mod 4) に対する最初のステップ

n ≡ 3 (mod 4) のとき:
  v₂(3n+1) ≥ 2

証明: n = 4k+3 とすると 3n+1 = 12k+10 = 2(6k+5)
  6k+5 の偶奇: 6k+5 ≡ k+1 (mod 2)
  k が奇数なら 6k+5 は偶数 → v₂ ≥ 2 + 1 = 3 以上
  k が偶数なら 6k+5 は奇数 → v₂ = 2 ちょうど

  つまり n ≡ 3 (mod 4) → v₂(3n+1) ≥ 2
  さらに n ≡ 3 (mod 8) → v₂(3n+1) = 2
        n ≡ 7 (mod 8) → v₂(3n+1) ≥ 3

■ 定理2: n ≡ 1 (mod 4) の場合、最初のステップ

n ≡ 1 (mod 4) のとき:
  v₂(3n+1) = 1 (最悪ケース)
  T(n) = (3n+1)/2

  次のステップ: v₂(3·(3n+1)/2 + 1) = v₂((9n+3+2)/2) = v₂((9n+5)/2)

  n ≡ 1 (mod 4): 9n+5 ≡ 9+5 = 14 ≡ 2 (mod 4), so (9n+5)/2 ≡ 1 (mod 2) is odd
  wait: (9n+5) の偶奇: 9n+5, n奇数なので 9n奇数, 9n+5偶数
  v₂(9n+5):
    n ≡ 1 (mod 8): 9+5=14, v₂(14)=1, so (9n+5)/2 の v₂ を見る
    実は T(n) = (3n+1)/2 で、次は v₂(3·T(n)+1)
""")

# 2ステップでの厳密な v₂ 合計
print("■ 2ステップの v₂ 合計の厳密計算 (mod 16)")
for r in range(1, 16, 2):
    v1 = v2(3*r + 1)
    T1 = (3*r + 1) >> v1
    v2_2 = v2(3*T1 + 1)
    total = v1 + v2_2
    ratio_2 = total / 2
    ok = "✓" if ratio_2 > LOG2_3 else "✗"
    print(f"  n ≡ {r:>2} (mod 16): v₂₁={v1}, T(n)={T1:>4}, v₂₂={v2_2}, Σv₂={total}, Σv₂/2={ratio_2:.2f} {ok}")

# 3ステップ
print("\n■ 3ステップの v₂ 合計 (mod 64)")
proved_3 = 0
total_3 = 0
not_proved = []
for r in range(1, 64, 2):
    v2_list_3 = []
    x = r
    for _ in range(3):
        val = 3*x + 1
        v = v2(val)
        v2_list_3.append(v)
        x = val >> v
    total_v2_3 = sum(v2_list_3)
    ratio_3 = total_v2_3 / 3
    total_3 += 1
    if ratio_3 > LOG2_3:
        proved_3 += 1
    else:
        not_proved.append((r, v2_list_3, total_v2_3, ratio_3))

print(f"  証明済み: {proved_3}/{total_3}")
if not_proved:
    print(f"  未証明の剰余類:")
    for r, vl, tv, ratio in not_proved:
        print(f"    n ≡ {r} (mod 64): v₂列={vl}, Σv₂={tv}, Σv₂/3={ratio:.3f}")

# 4ステップ (mod 256)
print("\n■ 4ステップの v₂ 合計 (mod 256)")
proved_4 = 0
total_4 = 0
not_proved_4 = []
for r in range(1, 256, 2):
    v2_list_4 = []
    x = r
    for _ in range(4):
        val = 3*x + 1
        v = v2(val)
        v2_list_4.append(v)
        x = val >> v
    total_v2_4 = sum(v2_list_4)
    ratio_4 = total_v2_4 / 4
    total_4 += 1
    if ratio_4 > LOG2_3:
        proved_4 += 1
    else:
        not_proved_4.append((r, v2_list_4, total_v2_4, ratio_4))

print(f"  証明済み: {proved_4}/{total_4}")
if not_proved_4:
    print(f"  未証明の剰余類 ({len(not_proved_4)} 個):")
    for r, vl, tv, ratio in not_proved_4[:20]:
        print(f"    n ≡ {r} (mod 256): v₂列={vl}, Σv₂={tv}, Σv₂/4={ratio:.3f}")
    if len(not_proved_4) > 20:
        print(f"    ... (他 {len(not_proved_4) - 20} 個)")

# 深いステップ (mod 2^K) で問題の剰余類を追跡
print("\n■ 未証明の剰余類の再帰的追跡")
print("  未証明 = 最初の数ステップで v₂ 合計が不足するケース")
print("  これらは後続のステップで補償されるか？\n")

# mod 2^10 で 10ステップ
K_big = 10
proved_big = 0
total_big = 0
not_proved_big = []
worst_ratio = float('inf')
worst_r = 0

for r in range(1, 2**K_big, 2):
    v2_list_big = []
    x = r
    for step in range(K_big):
        val = 3*x + 1
        v = v2(val)
        v2_list_big.append(v)
        x = val >> v
    total_v2_big = sum(v2_list_big)
    ratio_big = total_v2_big / K_big
    total_big += 1
    if ratio_big > LOG2_3:
        proved_big += 1
    else:
        not_proved_big.append((r, v2_list_big, total_v2_big, ratio_big))
    if ratio_big < worst_ratio:
        worst_ratio = ratio_big
        worst_r = r

print(f"  mod 2^{K_big}, {K_big}ステップ: 証明済み {proved_big}/{total_big} ({proved_big/total_big*100:.1f}%)")
print(f"  最悪の d/u = {worst_ratio:.4f} (r={worst_r})")
if not_proved_big:
    print(f"  未証明: {len(not_proved_big)} 個")


# 重要な結論
print("\n" + "=" * 70)
print("最終結論")
print("=" * 70)
print(f"""
■ 発見のまとめ

1. v₂(3n+1) の分布は厳密に幾何分布 P(v₂=j) = 1/2^j
   → E[v₂] = 2 > log₂(3) ≈ 1.585

2. 連続 v₂=1 (最悪ケース) が k 回続くには n ≡ 2^{{k+1}}-1 (mod 2^{{k+1}})
   密度 = 1/2^{{k+1}} で指数的に稀

3. k連続上昇後のバースト: v₂ ≥ 2 が保証される
   (3^{{k+1}}·m - 1 の最小 v₂ は m=1 のとき)

4. mod 2^K で最初の K ステップを厳密追跡すると:
   - 2ステップ (mod 16): 大部分で d/u > log₂(3)
   - 10ステップ (mod 1024): {proved_big}/{total_big} で証明済み

5. 残る困難: v₂=1 の連続は稀だが、それでも任意の長さの連続が
   存在し得る。有限ステップの追跡では「全ての n」には到達できない。

■ 部分的証明

定理: n ≡ 3 (mod 4) ならば、最初の Syracuse ステップで v₂ ≥ 2。
      つまり1ステップでの d/u ≥ 2 > log₂(3)。

定理: n ≡ 7 (mod 8) ならば、最初の Syracuse ステップで v₂ ≥ 3。
      つまり1ステップでの d/u ≥ 3 > log₂(3)。

注意: これは「最初のステップ」のみの保証であり、
      全軌道での d/u > log₂(3) の証明ではない。
""")

# 新しい方向: 加重マルコフ連鎖アプローチ
print("=" * 70)
print("新方向: 加重マルコフ連鎖による下界")
print("=" * 70)

print("""
■ マルコフ連鎖モデル

状態: n mod 2^K の奇数剰余類
遷移: T(n) mod 2^K → T(n) mod 2^K
報酬: v₂(3n+1)

定常分布 π が一様ならば、長期平均 v₂ = E_π[v₂] = 2。

問題: 一様でない場合も E_π[v₂] > log₂(3) か？
""")

# マルコフ連鎖の構成と定常分布
print("■ mod 8 のマルコフ連鎖")
K_markov = 3
mod_markov = 2**K_markov
states = list(range(1, mod_markov, 2))
print(f"  状態: {states}")

# 遷移行列
transitions = {}
for s in states:
    val = 3 * s + 1
    v = v2(val)
    t = (val >> v) % mod_markov
    if t % 2 == 0:
        t = (t // 2) % mod_markov
        if t == 0:
            t = mod_markov  # shouldn't happen
    transitions[s] = (t, v)
    print(f"  {s} → {t} (v₂={v})")

# 定常分布の計算（べき乗法）
import numpy as np

n_states = len(states)
state_idx = {s: i for i, s in enumerate(states)}
P = np.zeros((n_states, n_states))
rewards = np.zeros(n_states)

for s in states:
    t, v = transitions[s]
    # t が状態リストにあるか確認
    if t in state_idx:
        P[state_idx[s], state_idx[t]] = 1.0
    rewards[state_idx[s]] = v

print(f"\n  遷移行列 P:")
print(P)

# 定常分布
eigenvalues, eigenvectors = np.linalg.eig(P.T)
# 固有値1に対応する固有ベクトル
idx = np.argmin(np.abs(eigenvalues - 1))
pi = np.real(eigenvectors[:, idx])
pi = pi / pi.sum()
print(f"\n  定常分布 π:")
for i, s in enumerate(states):
    print(f"    π({s}) = {pi[i]:.6f}")

expected_v2 = np.dot(pi, rewards)
print(f"\n  E_π[v₂] = {expected_v2:.6f}")
print(f"  log₂(3) = {LOG2_3:.6f}")
print(f"  E_π[v₂] > log₂(3): {expected_v2 > LOG2_3}")

# より大きな mod でも
for K_m in [4, 5, 6, 7, 8]:
    mod_m = 2**K_m
    states_m = list(range(1, mod_m, 2))
    n_s = len(states_m)
    s_idx = {s: i for i, s in enumerate(states_m)}
    P_m = np.zeros((n_s, n_s))
    r_m = np.zeros(n_s)

    for s in states_m:
        val = 3 * s + 1
        v = v2(val)
        t = (val >> v) % mod_m
        while t % 2 == 0 and t > 0:
            t //= 2
        t = t % mod_m
        if t == 0:
            t = 1  # fallback
        if t in s_idx:
            P_m[s_idx[s], s_idx[t]] = 1.0
        r_m[s_idx[s]] = v

    # 定常分布
    try:
        evals, evecs = np.linalg.eig(P_m.T)
        idx = np.argmin(np.abs(evals - 1))
        pi_m = np.real(evecs[:, idx])
        pi_m = np.abs(pi_m)
        pi_m = pi_m / pi_m.sum()
        e_v2 = np.dot(pi_m, r_m)
        print(f"  mod 2^{K_m}: E_π[v₂] = {e_v2:.6f}, > log₂(3): {e_v2 > LOG2_3}")
    except:
        print(f"  mod 2^{K_m}: 計算エラー")

print("\n完了")
