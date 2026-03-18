"""
エルデシュ問題 #20: Sunflower Conjecture（ひまわり予想）の数値実験

探索1: 小さい n, k での f(n,k) の計算と構造解析
探索2: ひまわりフリー集合族の構造分析

f(n,k) = n-均一集合族がk-ひまわりを含むための最小サイズ
k-ひまわり: k個の集合で、任意の2つの共通部分が全て同じ（core）

Erdős-Rado (1960): f(n,k) ≤ (k-1)^n · n! + 1
最良結果: f(n,k) ≤ (C·k·log(n))^n [Alweiss-Lovett-Wu-Zhang 2020]
"""

import itertools
import math
import random
from collections import defaultdict

# ============================================================
# ひまわりの判定
# ============================================================

def is_sunflower(sets):
    """集合のリストがひまわりかどうか判定する。
    k個の集合で、任意の2つの共通部分が全て同じ（core）であれば真。
    """
    if len(sets) < 2:
        return True
    # 全ペアの共通部分が同じか確認
    core = sets[0] & sets[1]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            if sets[i] & sets[j] != core:
                return False
    # 花びら部分が互いに素か確認（coreを除いた部分が互いに素）
    petals = [s - core for s in sets]
    for i in range(len(petals)):
        for j in range(i + 1, len(petals)):
            if petals[i] & petals[j]:
                return False
    return True


def contains_k_sunflower(family, k):
    """集合族がk-ひまわりを含むか判定する。"""
    family_list = list(family)
    if len(family_list) < k:
        return False, []
    for combo in itertools.combinations(family_list, k):
        sets = [frozenset(s) for s in combo]
        if is_sunflower(sets):
            return True, sets
    return False, []


def find_sunflower_free_families(n, k, universe_size):
    """n-均一集合族でk-ひまわりを含まない最大サイズの族を全探索する。
    universe_size: 台集合のサイズ
    """
    # 台集合 {0, 1, ..., universe_size-1} の n-元部分集合を列挙
    all_sets = [frozenset(s) for s in itertools.combinations(range(universe_size), n)]

    best_family = []
    best_size = 0

    # 小さいケースは全探索、大きい場合は貪欲法
    if len(all_sets) <= 20:
        # 全部分集合を調べる（2^|all_sets|通り）
        for r in range(len(all_sets), 0, -1):
            found = False
            for combo in itertools.combinations(all_sets, r):
                family = list(combo)
                has_sf, _ = contains_k_sunflower(family, k)
                if not has_sf:
                    if r > best_size:
                        best_size = r
                        best_family = family
                    found = True
                    break
            if found:
                break
    else:
        # 貪欲法: ランダムに追加して最大族を探す
        for trial in range(100):
            random.shuffle(all_sets)
            family = []
            for s in all_sets:
                test_family = family + [s]
                has_sf, _ = contains_k_sunflower(test_family, k)
                if not has_sf:
                    family.append(s)
            if len(family) > best_size:
                best_size = len(family)
                best_family = family[:]

    return best_family, best_size


# ============================================================
# 探索1: f(n,k) の正確な計算
# ============================================================

def compute_f_exact(n, k, universe_size=None):
    """f(n,k) を全探索で計算する。
    台集合のサイズを指定できる（Noneの場合は自動設定）。
    """
    if universe_size is None:
        # 台集合は十分大きくする（少なくとも n*k 程度）
        universe_size = max(n * k, 2 * n + 1)

    all_sets = [frozenset(s) for s in itertools.combinations(range(universe_size), n)]
    total = len(all_sets)

    # サイズ m の n-均一集合族が必ず k-ひまわりを含む最小の m を求める
    # つまり f(n,k) = (ひまわりフリーの最大サイズ) + 1

    sf_free, max_sf_free_size = find_sunflower_free_families(n, k, universe_size)

    return max_sf_free_size + 1, sf_free


def erdos_rado_bound(n, k):
    """Erdős-Rado の上界: (k-1)^n · n! + 1"""
    return (k - 1) ** n * math.factorial(n) + 1


def alwz_bound(n, k, C=10.0):
    """ALWZ 2020 の上界: (C·k·log(n+1))^n （近似値）"""
    return (C * k * math.log(n + 1)) ** n


print("=" * 70)
print("エルデシュ問題 #20: Sunflower Conjecture 数値実験")
print("=" * 70)

# --- 探索1: 小さい n, k での f(n,k) ---

print("\n" + "=" * 70)
print("探索1: f(n, k=3) の正確な値と上界の比較")
print("=" * 70)

print(f"\n{'n':>3} | {'台集合':>6} | {'f(n,3)':>8} | {'ER上界':>12} | {'比率':>8} | {'f/2^n':>8}")
print("-" * 65)

f_values = {}
for n in range(1, 6):
    # 台集合サイズを段階的に増やして f(n,3) を計算
    if n <= 3:
        univ = max(n * 4, 2 * n + 2)
        f_val, sf_free = compute_f_exact(n, 3, univ)
    elif n == 4:
        univ = 10
        f_val, sf_free = compute_f_exact(n, 3, univ)
    else:
        # n=5 は全探索が困難なので貪欲法で下界を推定
        univ = 12
        f_val, sf_free = compute_f_exact(n, 3, univ)

    er = erdos_rado_bound(n, 3)
    ratio = f_val / er if er > 0 else 0
    ratio_exp = f_val / (2 ** n) if 2 ** n > 0 else 0
    f_values[n] = f_val

    print(f"{n:>3} | {univ:>6} | {f_val:>8} | {er:>12} | {ratio:>8.4f} | {ratio_exp:>8.4f}")

# --- 定数 c の推定 ---
print("\n" + "=" * 70)
print("f(n,3) / c^n の比率から最適定数 c を推定")
print("=" * 70)

print(f"\n{'n':>3} | {'f(n,3)':>8} | {'f^(1/n)':>10} | {'log_2(f)/n':>12}")
print("-" * 50)
for n, f_val in f_values.items():
    if n > 0 and f_val > 0:
        c_est = f_val ** (1.0 / n)
        log_ratio = math.log2(f_val) / n
        print(f"{n:>3} | {f_val:>8} | {c_est:>10.4f} | {log_ratio:>12.4f}")


# --- ランダム集合族でのひまわり出現確率 ---
print("\n" + "=" * 70)
print("ランダム n-均一集合族でのひまわり出現確率")
print("=" * 70)

random.seed(42)

for n in [2, 3, 4]:
    for m in [3, 5, 10, 15, 20]:
        universe = list(range(max(2 * n + 2, 8)))
        trials = 500
        sunflower_count = 0
        for _ in range(trials):
            # ランダムに m 個の n-元集合を選ぶ
            family = set()
            attempts = 0
            while len(family) < m and attempts < 1000:
                s = frozenset(random.sample(universe, n))
                family.add(s)
                attempts += 1
            if len(family) == m:
                has_sf, _ = contains_k_sunflower(list(family), 3)
                if has_sf:
                    sunflower_count += 1
        prob = sunflower_count / trials
        print(f"n={n}, m={m:>3}, 台集合={len(universe)}: "
              f"3-ひまわり出現確率 = {prob:.3f} ({sunflower_count}/{trials})")
    print()


# ============================================================
# 探索2: ひまわりフリー集合族の構造解析
# ============================================================

print("\n" + "=" * 70)
print("探索2: ひまわりフリー（k=3）集合族の構造解析")
print("=" * 70)

for n in [2, 3, 4]:
    if n == 4:
        univ = 9
    else:
        univ = max(2 * n + 2, n * 3)

    sf_free, size = find_sunflower_free_families(n, 3, univ)

    print(f"\n--- n={n}, 台集合={{0,...,{univ-1}}}, 最大ひまわりフリー族: サイズ {size} ---")

    # 集合族を表示
    sorted_family = sorted([sorted(list(s)) for s in sf_free])
    for i, s in enumerate(sorted_family):
        print(f"  {i+1}: {set(s)}")

    # 構造分析
    if sf_free:
        # 1. 各要素の出現頻度
        freq = defaultdict(int)
        for s in sf_free:
            for x in s:
                freq[x] += 1
        print(f"  要素頻度: {dict(sorted(freq.items()))}")

        # 2. ペアワイズ共通部分のサイズ分布
        intersection_sizes = defaultdict(int)
        for i in range(len(sf_free)):
            for j in range(i + 1, len(sf_free)):
                inter_size = len(sf_free[i] & sf_free[j])
                intersection_sizes[inter_size] += 1
        print(f"  共通部分サイズ分布: {dict(sorted(intersection_sizes.items()))}")

        # 3. 包含関係の確認
        contains_count = 0
        for i in range(len(sf_free)):
            for j in range(len(sf_free)):
                if i != j and sf_free[i] <= sf_free[j]:
                    contains_count += 1
        print(f"  包含関係ペア数: {contains_count}")

        # 4. 最大共通部分
        max_inter = 0
        for i in range(len(sf_free)):
            for j in range(i + 1, len(sf_free)):
                max_inter = max(max_inter, len(sf_free[i] & sf_free[j]))
        print(f"  最大共通部分サイズ: {max_inter}")


# ============================================================
# 理論的まとめ
# ============================================================

print("\n" + "=" * 70)
print("まとめ: 各上界の比較")
print("=" * 70)

print(f"\n{'n':>3} | {'f(n,3)実測':>12} | {'ER上界':>12} | {'ALWZ推定':>14} | {'予想c^n':>12}")
print("-" * 70)
for n in range(1, 6):
    f_val = f_values.get(n, "?")
    er = erdos_rado_bound(n, 3)
    alwz = alwz_bound(n, 3, C=10.0)
    conj = 3.0 ** n  # 予想: c_3 ≈ 3 程度

    f_str = str(f_val) if isinstance(f_val, int) else "?"
    print(f"{n:>3} | {f_str:>12} | {er:>12} | {alwz:>14.1f} | {conj:>12.1f}")

print(f"""
理論的背景:
- Erdős-Rado 定理 (1960): f(n,k) ≤ (k-1)^n · n! + 1
  → 指数 × 階乗の増大
- Sunflower 予想: f(n,k) ≤ c_k^n （純指数的上界が存在）
  → k=3 では c_3 < ∞ が予想
- ALWZ 2020: f(n,k) ≤ (C·k·log(n))^n
  → log(n) の因子が残る（予想ではこれを除去したい）
- 予想が正しいなら、f(n,3)^(1/n) は有界であるはず
""")
