"""
コラッツ写像の mod p^k 軌道と多素数 p-adic 構造の解析

Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)} の mod p^k (p=2,3,5,7, k=1..6) での
軌道構造を調べ、新しい不変量の候補を探す。
"""

import json
import sys
from collections import defaultdict, Counter
from math import gcd
from itertools import product

def syracuse(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)}"""
    if n <= 0 or n % 2 == 0:
        return None
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        c += 1
        n //= 2
    return c

def vp(n, p):
    """p-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % p == 0:
        c += 1
        n //= p
    return c

def syracuse_orbit(n, max_steps=200):
    """Syracuse軌道を計算"""
    orbit = [n]
    seen = {n}
    for _ in range(max_steps):
        n = syracuse(n)
        if n is None or n in seen:
            break
        orbit.append(n)
        seen.add(n)
        if n == 1:
            break
    return orbit

# ============================================================
# 1. mod p^k での Syracuse 写像の遷移グラフ解析
# ============================================================
def analyze_mod_pk_transitions(p, k_max=6):
    """mod p^k での奇数剰余類間の遷移を解析"""
    results = {}
    for k in range(1, k_max + 1):
        mod = p ** k
        # 奇数の剰余類のみ（Syracuseは奇数→奇数）
        odd_residues = [r for r in range(mod) if r % 2 == 1]

        # 各奇数剰余類からの遷移先を計算
        transition = {}
        for r in odd_residues:
            # 十分大きい代表元を使って遷移先を確認
            targets = set()
            for mult in range(0, max(50, 2*mod)):
                n = r + mod * (2 * mult + (1 if r % 2 == 0 else 0))
                if n > 0 and n % 2 == 1:
                    t = syracuse(n)
                    targets.add(t % mod)
            transition[r] = sorted(targets)

        # 各剰余類の遷移先の数（確定的 = 1つ、非確定的 = 複数）
        deterministic = sum(1 for r in odd_residues if len(transition[r]) == 1)
        total = len(odd_residues)

        # 到達不可能な剰余類
        reachable = set()
        for targets in transition.values():
            reachable.update(targets)
        unreachable_odd = [r for r in odd_residues if r not in reachable]

        # サイクル検出
        cycles = find_cycles_in_transition(transition, odd_residues)

        results[k] = {
            "mod": mod,
            "odd_residues": len(odd_residues),
            "deterministic": deterministic,
            "det_ratio": round(deterministic / total, 4) if total > 0 else 0,
            "unreachable": unreachable_odd[:10],
            "num_unreachable": len(unreachable_odd),
            "num_cycles": len(cycles),
            "cycle_lengths": [len(c) for c in cycles[:5]],
            "sample_transitions": {r: transition[r] for r in odd_residues[:5]}
        }
    return results

def find_cycles_in_transition(transition, residues):
    """遷移グラフ内のサイクルを検出"""
    # 確定的遷移のみでサイクル検出
    det_trans = {}
    for r in residues:
        if len(transition.get(r, [])) == 1:
            det_trans[r] = transition[r][0]

    visited = set()
    cycles = []
    for start in det_trans:
        if start in visited:
            continue
        path = []
        current = start
        path_set = set()
        while current in det_trans and current not in path_set:
            path_set.add(current)
            path.append(current)
            current = det_trans[current]
        if current in path_set:
            cycle_start = path.index(current)
            cycle = path[cycle_start:]
            cycles.append(cycle)
            visited.update(cycle)
        visited.update(path_set)
    return cycles


# ============================================================
# 2. p-adic valuation の相互作用解析
# ============================================================
def analyze_padic_interactions(N=50000):
    """Syracuse軌道上での各素数のp-adic valuationの分布と相関"""
    primes = [2, 3, 5, 7]

    # v_p(T(n)) の分布
    vp_dist = {p: Counter() for p in primes}
    # v_p(n) と v_q(T(n)) の相関
    vp_cross = {}
    for p, q in product(primes, repeat=2):
        vp_cross[(p, q)] = defaultdict(list)

    # joint distribution v3(n) vs v3(T(n))
    v3_joint = Counter()
    v5_joint = Counter()

    for n in range(1, N + 1, 2):  # 奇数のみ
        t = syracuse(n)
        if t is None:
            continue
        for p in primes:
            val_t = vp(t, p)
            vp_dist[p][val_t] += 1

        # 相関: v_p(n) → v_q(T(n))
        for p in primes:
            val_n = vp(n, p)
            for q in primes:
                val_t = vp(t, q)
                vp_cross[(p, q)][val_n].append(val_t)

        v3n = vp(n, 3)
        v3t = vp(t, 3)
        v3_joint[(v3n, v3t)] += 1

        v5n = vp(n, 5)
        v5t = vp(t, 5)
        v5_joint[(v5n, v5t)] += 1

    # 分布の要約
    dist_summary = {}
    for p in primes:
        total = sum(vp_dist[p].values())
        dist_summary[p] = {
            str(v): round(c / total, 6) for v, c in sorted(vp_dist[p].items()) if v <= 6
        }

    # 相関の要約: E[v_q(T(n)) | v_p(n) = j]
    cross_summary = {}
    for (p, q) in vp_cross:
        key = f"v{p}_to_v{q}"
        cross_summary[key] = {}
        for j in sorted(vp_cross[(p, q)].keys()):
            if j <= 4:
                vals = vp_cross[(p, q)][j]
                if len(vals) >= 10:
                    avg = sum(vals) / len(vals)
                    cross_summary[key][str(j)] = round(avg, 4)

    # v3 joint
    v3_joint_summary = {}
    total_v3 = sum(v3_joint.values())
    for (a, b), c in sorted(v3_joint.items()):
        if a <= 3 and b <= 3:
            v3_joint_summary[f"({a},{b})"] = round(c / total_v3, 6)

    return dist_summary, cross_summary, v3_joint_summary


# ============================================================
# 3. mod 3^k の特殊構造（T(n) ≢ 0 mod 3 の制約利用）
# ============================================================
def analyze_mod3k_structure(k_max=6):
    """T(n) ≢ 0 (mod 3) の制約がmod 3^k軌道に与える影響"""
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k
        # 奇数かつ 3で割り切れない剰余類（Tの像はここに限定される）
        valid_residues = [r for r in range(mod) if r % 2 == 1 and r % 3 != 0]
        all_odd = [r for r in range(mod) if r % 2 == 1]

        # 実際のT(n) mod 3^k の分布を確認
        image_counts = Counter()
        sample_size = max(10000, 10 * mod)
        for n in range(1, 2 * sample_size + 1, 2):
            t = syracuse(n)
            image_counts[t % mod] += 1

        # 像に現れない剰余類
        zero_image = [r for r in range(mod) if image_counts[r] == 0 and r % 2 == 1]

        # 像がmod 3 != 0 に限定されることの確認
        image_mod3_zero = sum(c for r, c in image_counts.items() if r % 3 == 0)
        image_total = sum(image_counts.values())

        # エントロピー計算
        probs = [c / image_total for c in image_counts.values() if c > 0]
        import math
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        max_entropy = math.log2(len(valid_residues)) if valid_residues else 0

        results[k] = {
            "mod": mod,
            "all_odd": len(all_odd),
            "valid_non3": len(valid_residues),
            "ratio_valid": round(len(valid_residues) / len(all_odd), 4) if all_odd else 0,
            "image_mod3_zero_frac": round(image_mod3_zero / image_total, 6) if image_total > 0 else 0,
            "zero_image_count": len(zero_image),
            "entropy": round(entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "entropy_ratio": round(entropy / max_entropy, 4) if max_entropy > 0 else 0,
        }
    return results


# ============================================================
# 4. 多素数不変量の探索
# ============================================================
def search_invariants(N=20000, orbit_len=50):
    """軌道上の多素数p-adic valuationパターンから不変量を探す"""
    primes = [3, 5, 7]

    # 各軌道について、v_p値の列のパターンを集める
    pattern_stats = {p: defaultdict(list) for p in primes}

    # 軌道上のv_p密度
    density_corr = {p: [] for p in primes}
    orbit_lengths = []

    for start in range(1, N + 1, 2):
        orbit = syracuse_orbit(start, max_steps=orbit_len)
        if len(orbit) < 5:
            continue

        olen = len(orbit)
        orbit_lengths.append(olen)

        for p in primes:
            # v_p(orbit[i]) の列
            vp_seq = [vp(x, p) for x in orbit]

            # 密度: v_p > 0 の割合
            density = sum(1 for v in vp_seq if v > 0) / len(vp_seq)
            density_corr[p].append((start, density, olen))

            # 最初の3ステップのv_pパターン
            pattern = tuple(min(v, 2) for v in vp_seq[:3])
            pattern_stats[p][pattern].append(start)

    # 密度の統計
    density_summary = {}
    for p in primes:
        densities = [d for _, d, _ in density_corr[p]]
        avg_d = sum(densities) / len(densities) if densities else 0
        # 理論値: 1 - (1-1/p)*(1-1/p) ≈ prob(p | orbit[i])
        # 実際にはランダムモデルでは prob(p | n) = 1/p for odd n coprime to 2
        expected = 1 / p  # 大雑把な期待値
        density_summary[p] = {
            "avg_density": round(avg_d, 6),
            "expected_random": round(expected, 6),
            "ratio": round(avg_d / expected, 4) if expected > 0 else 0,
        }

    # パターンの頻度
    pattern_summary = {}
    for p in primes:
        top_patterns = sorted(pattern_stats[p].items(), key=lambda x: -len(x[1]))[:5]
        total = sum(len(v) for v in pattern_stats[p].values())
        pattern_summary[p] = {
            str(pat): round(len(starts) / total, 4)
            for pat, starts in top_patterns
        }

    return density_summary, pattern_summary


# ============================================================
# 5. p=3 での forbidden residues の構造
# ============================================================
def analyze_forbidden_residues_mod3k(k_max=5):
    """T(n) ≡ 0 (mod 3) が起きないことから、mod 3^k でどの剰余類が禁止されるか"""
    results = {}
    for k in range(1, k_max + 1):
        mod = 3 ** k

        # n mod 3^k ごとに T(n) mod 3^k を調べる
        # 奇数nについてのみ
        residue_map = {}
        for r in range(mod):
            if r % 2 == 0:
                continue
            # 複数の代表元で確認
            images = set()
            for mult in range(50):
                n = r + mod * (2 * mult)
                if n > 0 and n % 2 == 1:
                    t = syracuse(n)
                    images.add(t % mod)
            residue_map[r] = sorted(images)

        # T(n) ≡ 0 mod 3 になるn mod 3^k が存在するか？
        maps_to_3div = []
        for r, imgs in residue_map.items():
            for img in imgs:
                if img % 3 == 0:
                    maps_to_3div.append((r, img))

        # 軌道がmod 3^k上で閉じるための条件
        # 長さ2以上のサイクルの検出
        all_images = set()
        for imgs in residue_map.values():
            all_images.update(imgs)
        odd_in_images = [x for x in all_images if x % 2 == 1]

        results[k] = {
            "mod": mod,
            "num_odd_residues": len(residue_map),
            "maps_to_3div_count": len(maps_to_3div),
            "maps_to_3div_examples": maps_to_3div[:5],
            "num_distinct_images": len(all_images),
            "odd_images": len(odd_in_images),
        }
    return results


# ============================================================
# 6. 新しい不変量候補: Σ v_p(orbit) の比率
# ============================================================
def search_ratio_invariants(N=10000):
    """軌道上の Σv_3 / Σv_5 等の比率が収束するかを調査"""
    primes = [3, 5, 7, 11, 13]
    ratios = defaultdict(list)

    for start in range(1, N + 1, 2):
        orbit = syracuse_orbit(start, max_steps=300)
        if len(orbit) < 20:
            continue

        sums = {}
        for p in primes:
            sums[p] = sum(vp(x, p) for x in orbit)

        # 各ペアの比率
        for i, p in enumerate(primes):
            for q in primes[i+1:]:
                if sums[q] > 0:
                    r = sums[p] / sums[q]
                    ratios[(p, q)].append(r)

    # 各比率の統計
    ratio_summary = {}
    for (p, q), vals in ratios.items():
        if len(vals) < 100:
            continue
        avg = sum(vals) / len(vals)
        variance = sum((v - avg) ** 2 for v in vals) / len(vals)
        std = variance ** 0.5
        cv = std / avg if avg > 0 else float('inf')
        ratio_summary[f"v{p}/v{q}"] = {
            "mean": round(avg, 4),
            "std": round(std, 4),
            "cv": round(cv, 4),  # 変動係数
            "n_samples": len(vals),
        }

    return ratio_summary


# ============================================================
# メイン実行
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("コラッツ写像の mod p^k 軌道と多素数 p-adic 構造解析")
    print("=" * 60)

    # 1. mod p^k 遷移解析
    print("\n[1] mod p^k 遷移グラフ解析...")
    pk_results = {}
    for p in [2, 3, 5, 7]:
        k_max = 4 if p >= 5 else 6
        print(f"  p={p}, k=1..{k_max}")
        pk_results[p] = analyze_mod_pk_transitions(p, k_max)

    print("\n--- mod p^k 確定的遷移の割合 ---")
    for p in [2, 3, 5, 7]:
        print(f"p={p}:")
        for k, data in pk_results[p].items():
            print(f"  k={k}: det={data['deterministic']}/{data['odd_residues']} "
                  f"({data['det_ratio']:.1%}), cycles={data['num_cycles']}, "
                  f"cycle_lens={data['cycle_lengths']}")

    # 2. p-adic valuation 相互作用
    print("\n[2] p-adic valuation 相互作用解析...")
    dist_summary, cross_summary, v3_joint = analyze_padic_interactions(50000)

    print("\n--- v_p(T(n)) の分布 ---")
    for p, dist in dist_summary.items():
        print(f"p={p}: {dist}")

    print("\n--- E[v_q(T(n)) | v_p(n)=j] の主要相関 ---")
    for key in ["v3_to_v3", "v3_to_v5", "v5_to_v3", "v5_to_v5"]:
        if key in cross_summary:
            print(f"  {key}: {cross_summary[key]}")

    print("\n--- v3 joint distribution ---")
    for k, v in sorted(v3_joint.items()):
        print(f"  {k}: {v}")

    # 3. mod 3^k 特殊構造
    print("\n[3] mod 3^k 特殊構造解析...")
    mod3k_results = analyze_mod3k_structure(6)
    for k, data in mod3k_results.items():
        print(f"  k={k}: valid_non3={data['valid_non3']}/{data['all_odd']}, "
              f"image_mod3_zero={data['image_mod3_zero_frac']:.6f}, "
              f"entropy_ratio={data['entropy_ratio']:.4f}")

    # 4. 多素数不変量探索
    print("\n[4] 多素数不変量探索...")
    density_summary, pattern_summary = search_invariants(20000)
    print("\n--- v_p 密度 ---")
    for p, data in density_summary.items():
        print(f"  p={p}: avg={data['avg_density']:.6f}, "
              f"expected={data['expected_random']:.6f}, "
              f"ratio={data['ratio']:.4f}")

    print("\n--- 初期パターン頻度 ---")
    for p, patterns in pattern_summary.items():
        print(f"  p={p}: {patterns}")

    # 5. Forbidden residues
    print("\n[5] mod 3^k forbidden residues 解析...")
    forbidden = analyze_forbidden_residues_mod3k(5)
    for k, data in forbidden.items():
        print(f"  k={k}: maps_to_3div={data['maps_to_3div_count']}, "
              f"examples={data['maps_to_3div_examples'][:3]}")

    # 6. 比率不変量
    print("\n[6] Σv_p 比率不変量探索...")
    ratio_results = search_ratio_invariants(10000)
    print("\n--- 比率統計 ---")
    for key, data in sorted(ratio_results.items()):
        print(f"  {key}: mean={data['mean']:.4f}, std={data['std']:.4f}, "
              f"cv={data['cv']:.4f}")

    print("\n" + "=" * 60)
    print("解析完了")
