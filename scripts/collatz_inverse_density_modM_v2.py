#!/usr/bin/env python3
"""
逆像密度のmod M分布 - Part 2: 深掘り解析

Part 1で発見された主要パターン:
1. 逆像ゼロクラス: m ≡ 0 (mod 3) の奇数は逆像を持たない → T(n) ≢ 0 (mod 3) の証明と整合
2. 逆像の残基分布に強い偏り: mod 8 で n≡5 が約2/3を占める
3. 遷移行列の不変測度が完全に一様（≠ Parry測度）

この Part 2 では:
- 逆像ゼロ条件の精密解析（3の倍数以外のゼロクラスの存在確認）
- 逆像分岐の v2 依存構造
- 理論的な逆像密度定数 C(m) の mod M 依存性
- beta=3/2 のParry測度と比較した非一様性の定量化
"""

import math
from collections import defaultdict, Counter

def v2(n):
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

def inverse_syracuse_all(m, max_val=None):
    preimages = []
    max_k = 60
    if max_val and m > 0:
        max_k = min(int(math.log2(3 * max_val / m)) + 2, 60)
    for k in range(1, max_k + 1):
        val = m * (1 << k) - 1
        if val % 3 == 0:
            n = val // 3
            if n > 0 and n % 2 == 1:
                if v2(3 * n + 1) == k:
                    if max_val is None or n <= max_val:
                        preimages.append(n)
    return preimages

def main():
    print("=" * 80)
    print("逆像密度 Part 2: 深掘り解析")
    print("=" * 80)

    # -------------------------------------------------------
    # 解析A: 逆像ゼロクラスの完全分類
    # -------------------------------------------------------
    print("\n解析A: 逆像ゼロの m の分類")
    print("-" * 60)
    print("T(n) ≢ 0 (mod 3) が形式証明済み。")
    print("逆像ゼロ ⟺ m ≡ 0 (mod 3) を確認。")

    N = 100000
    zero_preimage_ms = []
    nonzero_but_sparse = []

    for m in range(1, 1000, 2):
        preimages = inverse_syracuse_all(m, max_val=N)
        if len(preimages) == 0:
            zero_preimage_ms.append(m)
        elif len(preimages) <= 2:
            nonzero_but_sparse.append((m, len(preimages)))

    mod3_of_zeros = Counter(m % 3 for m in zero_preimage_ms)
    print(f"\n逆像ゼロの m の個数: {len(zero_preimage_ms)}")
    print(f"mod 3 分布: {dict(mod3_of_zeros)}")

    non_3mult = [m for m in zero_preimage_ms if m % 3 != 0]
    print(f"3の倍数でない逆像ゼロ: {non_3mult[:20]}{'...' if len(non_3mult)>20 else ''}")
    print(f"  → {len(non_3mult)} 個（これは v2 条件による制限）")

    # 3の倍数でないのに逆像がゼロの場合の原因分析
    if non_3mult:
        print("\n非3倍数の逆像ゼロ m の詳細:")
        for m in non_3mult[:10]:
            print(f"  m={m} (mod3={m%3}, mod8={m%8}):")
            for k in range(1, 20):
                val = m * (1 << k) - 1
                if val % 3 == 0:
                    n = val // 3
                    is_odd = n % 2 == 1
                    actual_v2 = v2(3*n+1) if n > 0 else -1
                    match = "MATCH" if actual_v2 == k else f"v2={actual_v2}!=k={k}"
                    if is_odd and n > 0:
                        print(f"    k={k}: n={n}, odd={is_odd}, {match}")

    # -------------------------------------------------------
    # 解析B: 逆像分岐のv2依存構造（決定論的パターン）
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析B: 逆像分岐のk値（v2値）パターン")
    print("-" * 60)

    print("\nT(n)=m の逆像 n=(m*2^k-1)/3 において有効な k の系列:")
    print("条件: (1) 3|(m*2^k-1), (2) n奇数, (3) v2(3n+1)=k")

    # m mod 6 別の有効k系列パターン
    for m_mod6 in [1, 5]:  # 奇数で3の倍数でないもの
        print(f"\nm ≡ {m_mod6} (mod 6):")
        # 代表元で確認
        m = m_mod6
        valid_ks = []
        invalid_ks = []
        for k in range(1, 40):
            val = m * (1 << k) - 1
            if val % 3 == 0:
                n = val // 3
                if n > 0 and n % 2 == 1:
                    actual_v2 = v2(3*n+1)
                    if actual_v2 == k:
                        valid_ks.append(k)
                    else:
                        invalid_ks.append((k, actual_v2))

        print(f"  有効な k: {valid_ks[:15]}")
        print(f"  無効な k (v2不一致): {invalid_ks[:10]}")

        # k の差分パターン
        if len(valid_ks) >= 2:
            diffs = [valid_ks[i+1]-valid_ks[i] for i in range(len(valid_ks)-1)]
            print(f"  連続kの差分: {diffs[:15]}")

    # 全ての m mod 6 = 1, 5 について有効k系列の統計
    print("\n有効k系列の統計（m ≤ 200）:")
    k_diff_patterns = defaultdict(list)

    for m in range(1, 200, 2):
        if m % 3 == 0:
            continue
        valid_ks = []
        for k in range(1, 50):
            val = m * (1 << k) - 1
            if val % 3 == 0:
                n = val // 3
                if n > 0 and n % 2 == 1 and v2(3*n+1) == k:
                    valid_ks.append(k)

        if len(valid_ks) >= 3:
            diffs = tuple(valid_ks[i+1]-valid_ks[i] for i in range(min(5, len(valid_ks)-1)))
            k_diff_patterns[diffs].append(m)

    print("最頻出の差分パターン:")
    for pattern, ms in sorted(k_diff_patterns.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  差分{pattern}: {len(ms)}個, 例: {ms[:5]}")

    # -------------------------------------------------------
    # 解析C: mod 8 での逆像の偏り（n≡5 が2/3）の理論的説明
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析C: 逆像 n mod 8 の偏り分析")
    print("-" * 60)

    print("\n前像の mod 8 分布を v2(3n+1) 値ごとに分解:")

    N = 100000
    # 逆像のmod8分布をv2ごとに
    v2_mod8_dist = defaultdict(lambda: Counter())

    for n in range(1, N+1, 2):
        k = v2(3*n+1)
        v2_mod8_dist[k][n % 8] += 1

    for k in sorted(v2_mod8_dist.keys())[:8]:
        dist = v2_mod8_dist[k]
        total = sum(dist.values())
        print(f"  v2={k}: ", end="")
        for r in [1, 3, 5, 7]:
            frac = dist.get(r, 0) / total if total > 0 else 0
            print(f"n≡{r}:{frac:.4f} ", end="")
        print(f"  (total={total})")

    print("\nmod 8 の逆像偏りの理由:")
    print("  n≡1(mod8): v2=2 → T(n)=(3n+1)/4 ~ 0.75n (下降)")
    print("  n≡3(mod8): v2=1 → T(n)=(3n+1)/2 ~ 1.5n (上昇)")
    print("  n≡5(mod8): v2≥3 → T(n)=(3n+1)/2^k ~ 0.375n以下 (強い下降)")
    print("  n≡7(mod8): v2=1 → T(n)=(3n+1)/2 ~ 1.5n (上昇)")
    print()
    print("  逆像 T(n)=m の n は:")
    print("  - k=1: n≡3 or 7 (mod 8) → T(n)=1.5n → n ~ m/1.5")
    print("  - k=2: n≡1 (mod 8) → T(n)=0.75n → n ~ m/0.75")
    print("  - k≥3: n≡5 (mod 8) → T(n)≤0.375n → n ≥ m/0.375")
    print("  高い v2 → n が大きい → [1,N]に入る前像が多い！")

    # 実際にどの k の前像が最も多いか
    print("\n各 k 値の前像数（m=1..100の平均）:")
    k_counts = defaultdict(list)
    for m in range(1, 100, 2):
        if m % 3 == 0:
            continue
        for k in range(1, 30):
            val = m * (1 << k) - 1
            if val % 3 == 0:
                n = val // 3
                if n > 0 and n % 2 == 1 and v2(3*n+1) == k:
                    if n <= N:
                        k_counts[k].append(m)

    for k in sorted(k_counts.keys())[:15]:
        count = len(k_counts[k])
        print(f"  k={k:2d}: {count} 個の前像（m≤100, n≤{N}）")

    # -------------------------------------------------------
    # 解析D: 遷移行列の構造（理論的な導出）
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析D: mod 8 遷移行列の理論的構造")
    print("-" * 60)

    print("\nSyracuse T(n) mod 8 の決定論的な対応:")
    for n_mod8 in [1, 3, 5, 7]:
        print(f"\n  n ≡ {n_mod8} (mod 8):")
        # mod 16 に細分化して T(n) mod 8 を計算
        for n_mod16 in [n_mod8, n_mod8 + 8]:
            # さらに mod 32 で
            for n_mod32 in [n_mod16, n_mod16 + 16]:
                if n_mod32 < 32:
                    n_test = n_mod32 if n_mod32 > 0 else n_mod32 + 32
                    while n_test <= 0 or n_test % 2 == 0:
                        n_test += 32
                    tn = syracuse(n_test)
                    tn_mod8 = tn % 8
                    k = v2(3*n_test + 1)
                    print(f"    n≡{n_mod32:2d}(mod 32): v2={k}, T(n)≡{tn_mod8}(mod 8)")

    # 厳密な遷移確率（mod 8）
    print("\n\n厳密な遷移確率 P(T(n)≡j | n≡i) (mod 8):")
    print("理論導出: n ≡ r (mod 8) のとき T(n) mod 8 は n mod 16 以上で決定")

    for i_mod8 in [1, 3, 5, 7]:
        t_vals = Counter()
        # mod 2^12 まで展開して安定確率を求める
        modulus = 2**12
        for r in range(i_mod8, modulus, 8):
            if r > 0 and r % 2 == 1:
                tn = syracuse(r)
                t_vals[tn % 8] += 1

        total = sum(t_vals.values())
        print(f"  n≡{i_mod8}(mod 8): ", end="")
        for j in [1, 3, 5, 7]:
            prob = t_vals.get(j, 0) / total if total > 0 else 0
            print(f"→{j}:{prob:.4f} ", end="")
        print()

    # -------------------------------------------------------
    # 解析E: 逆像密度定数 C(m) の理論予測
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析E: 逆像密度定数の理論予測")
    print("-" * 60)

    print("\n|T^{-1}(m) ∩ [1,N]| の漸近形:")
    print("n = (m*2^k - 1)/3 ≤ N ⟹ k ≤ log_2(3N/m + 1/m)")
    print("有効な k は全体の約1/2 (mod 2 による)")
    print("v2条件: 有効 k のうちさらに制限あり")

    # 精密な C(m) を大きな N で測定
    N_large = 1000000
    print(f"\nC(m) = |T^-1(m) ∩ [1,{N_large}]| / log_2({N_large}) (log_2={math.log2(N_large):.2f})")

    c_by_mod = defaultdict(list)
    for m in range(1, 500, 2):
        if m % 3 == 0:
            c_by_mod[(m % 8, 'div3')].append(0)
            continue
        preimages = inverse_syracuse_all(m, max_val=N_large)
        c = len(preimages) / math.log2(N_large)
        c_by_mod[m % 8].append(c)
        c_by_mod[(m % 8, m % 16)].append(c)

    print("\nmod 8 別の C(m) 統計:")
    for r in [1, 3, 5, 7]:
        vals = c_by_mod[r]
        if vals:
            avg = sum(vals)/len(vals)
            std = (sum((v-avg)**2 for v in vals)/len(vals))**0.5
            mn = min(vals)
            mx = max(vals)
            print(f"  r={r}: avg={avg:.4f}, std={std:.4f}, min={mn:.4f}, max={mx:.4f}, n={len(vals)}")

    print("\nmod 16 別の C(m) 統計:")
    for r8 in [1, 3, 5, 7]:
        for r16 in [r8, r8+8]:
            key = (r8, r16)
            vals = c_by_mod.get(key, [])
            if vals:
                avg = sum(vals)/len(vals)
                std = (sum((v-avg)**2 for v in vals)/len(vals))**0.5
                print(f"  r≡{r16:2d}(mod 16): avg_C={avg:.4f}, std={std:.4f}")

    # -------------------------------------------------------
    # 解析F: beta=3/2 接続 - Lyapunov指数と逆像密度
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析F: beta=3/2 のLyapunov指数と逆像密度の接続")
    print("-" * 60)

    print("\nSyracuse関数の対数微分:")
    print("  log T(n) = log(3n+1) - v2(3n+1)*log 2")
    print("  E[log T(n)/n] = log 3 - E[v2]*log 2")
    print()

    # E[v2(3n+1)] を mod 8 別に計算
    for mod in [8, 16, 32]:
        print(f"mod {mod} 別の E[v2(3n+1)]:")
        for r in range(1, mod, 2):
            total_v2 = 0
            count = 0
            for n in range(r, 100000, mod):
                if n > 0:
                    total_v2 += v2(3*n+1)
                    count += 1
            avg = total_v2 / count if count > 0 else 0
            if mod <= 16 or r in [1,3,5,7,13,21,29]:
                print(f"  r={r:2d}: E[v2]={avg:.4f}")

        # 全体平均
        total_v2_all = sum(v2(3*n+1) for n in range(1, 100000, 2))
        count_all = len(range(1, 100000, 2))
        print(f"  全体: E[v2]={total_v2_all/count_all:.4f}")

        # Lyapunov指数
        lyap = math.log(3) - (total_v2_all/count_all) * math.log(2)
        print(f"  Lyapunov指数 = log3 - E[v2]*log2 = {lyap:.6f}")
        print(f"  (理論値: log(3/4) = {math.log(3/4):.6f})")
        print()

    # -------------------------------------------------------
    # 解析G: 逆像密度の精密な理論予測
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析G: 逆像密度の精密な理論予測")
    print("-" * 60)

    print("\n逆像 n = (m*2^k - 1)/3 の有効 k の密度:")
    print("  m ≡ 1 (mod 6): k ≡ 0 (mod 2) かつ v2 条件")
    print("  m ≡ 5 (mod 6): k ≡ 1 (mod 2) かつ v2 条件")
    print()

    # v2条件の通過率を精密に測定
    for m_mod6 in [1, 5]:
        valid_total = 0
        candidate_total = 0

        for m in range(m_mod6, 600, 6):
            if m == 0:
                continue
            for k in range(1, 40):
                val = m * (1 << k) - 1
                if val % 3 == 0:
                    n = val // 3
                    if n > 0 and n % 2 == 1:
                        candidate_total += 1
                        if v2(3*n+1) == k:
                            valid_total += 1

        pass_rate = valid_total / candidate_total if candidate_total > 0 else 0
        print(f"  m ≡ {m_mod6} (mod 6): v2条件通過率 = {valid_total}/{candidate_total} = {pass_rate:.6f}")

    # 理論予測: 通過率 = ?
    # n = (m*2^k - 1)/3 のとき、v2(3n+1) = v2(m*2^k) = k + v2(m) (mが奇数なら v2(m)=0)
    # → v2(3n+1) = v2(3*(m*2^k-1)/3 + 1) = v2(m*2^k) = k (mが奇数のとき)
    # つまり v2条件は自動的に満たされる！
    print("\n*** 重要な発見 ***")
    print("n = (m*2^k - 1)/3 (mが奇数) のとき:")
    print("  3n + 1 = m * 2^k")
    print("  v2(3n+1) = v2(m * 2^k) = k + v2(m)")
    print("  mが奇数 → v2(m) = 0 → v2(3n+1) = k")
    print("  → v2 条件は自動的に成立！")
    print()

    # 検証
    print("検証:")
    mismatches = 0
    total_checks = 0
    for m in range(1, 200, 2):
        for k in range(1, 30):
            val = m * (1 << k) - 1
            if val % 3 == 0:
                n = val // 3
                if n > 0 and n % 2 == 1:
                    total_checks += 1
                    actual = v2(3*n+1)
                    if actual != k:
                        mismatches += 1
                        print(f"  不一致! m={m}, k={k}, n={n}, v2(3n+1)={actual}")
    print(f"  チェック数: {total_checks}, 不一致: {mismatches}")

    # -------------------------------------------------------
    # 解析H: 逆像数の閉じた公式
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析H: 逆像数の閉じた公式")
    print("-" * 60)

    print("\nT^{-1}(m) ∩ [1,N] の逆像数:")
    print("n = (m*2^k - 1)/3 ≤ N")
    print("⟺ k ≤ log_2((3N+1)/m)")
    print()
    print("有効な k の条件:")
    print("  (a) m*2^k ≡ 1 (mod 3)  ← k の偶奇で決定")
    print("  (b) (m*2^k - 1)/3 が奇数 ← mod 6 条件")
    print("  (c) v2(3n+1) = k  ← 自動成立（上で証明）")
    print()

    # 有効k: m≡1(mod3)ならk偶数、m≡2(mod3)ならk奇数
    # n = (m*2^k-1)/3 の奇数条件:
    # m*2^k ≡ 1 (mod 3) のもとで (m*2^k-1)/3 mod 2 を計算
    print("n の奇数条件の詳細:")
    for m_mod3 in [1, 2]:
        for k_parity in ['even', 'odd']:
            if (m_mod3 == 1 and k_parity == 'even') or (m_mod3 == 2 and k_parity == 'odd'):
                # m*2^k ≡ 1 (mod 3)
                # n = (m*2^k - 1)/3
                # n mod 2: (m*2^k - 1) mod 6 を調べる
                count_odd = 0
                count_even = 0
                for k in range(1, 100):
                    if (k % 2 == 0 and m_mod3 == 1) or (k % 2 == 1 and m_mod3 == 2):
                        val = m_mod3 * (1 << k) - 1
                        n_cand = val // 3
                        if n_cand % 2 == 1:
                            count_odd += 1
                        else:
                            count_even += 1

                print(f"  m≡{m_mod3}(mod3), k {k_parity}: "
                      f"n奇数={count_odd}, n偶数={count_even}, "
                      f"奇数率={count_odd/(count_odd+count_even):.4f}")

    # 最終的な逆像数の公式
    print("\n逆像数の閉じた公式:")
    print("|T^{-1}(m) ∩ [1,N]| = floor(K/2)")
    print("ここで K = floor(log_2((3N+1)/m))")
    print("（有効kは全体の半分: 偶数 or 奇数のみ、")
    print("  さらにそのうちnが奇数のものは約半分）")
    print()

    # 精密版
    print("精密な公式の検証:")
    for m in [1, 5, 7, 11, 13, 17, 19, 23]:
        for N in [1000, 10000, 100000]:
            actual = len(inverse_syracuse_all(m, max_val=N))
            K = int(math.log2((3*N+1)/m))
            # 有効kはm mod 3に依存して偶数or奇数
            if m % 3 == 1:
                # k偶数: 2, 4, ..., K以下
                predicted = K // 2
                # さらに奇数条件で約半分
                # 実際には k mod 4 で決まる
                # k≡0(mod4): n偶数, k≡2(mod4): n奇数（m≡1 mod 6の場合）
                # 要するに4個に1個が有効
                valid_k_count = 0
                for k in range(2, K+1, 2):
                    val = m * (1 << k) - 1
                    if val % 3 == 0:
                        n = val // 3
                        if n > 0 and n % 2 == 1:
                            valid_k_count += 1
                predicted_refined = valid_k_count
            elif m % 3 == 2:
                predicted = (K + 1) // 2
                valid_k_count = 0
                for k in range(1, K+1, 2):
                    val = m * (1 << k) - 1
                    if val % 3 == 0:
                        n = val // 3
                        if n > 0 and n % 2 == 1:
                            valid_k_count += 1
                predicted_refined = valid_k_count
            else:
                predicted = 0
                predicted_refined = 0

            print(f"  m={m:3d}, N={N:6d}: actual={actual:2d}, K={K:2d}, "
                  f"K/2={K//2:2d}, refined={predicted_refined:2d}")

    # -------------------------------------------------------
    # 解析I: beta=3/2 展開の直接計算
    # -------------------------------------------------------
    print("\n" + "=" * 80)
    print("解析I: Syracuse逆写像のbeta=3/2 展開表現")
    print("-" * 60)

    print("\n逆像の列 n_k = (m*2^k - 1)/3 は指数的に成長:")
    print("  n_k ~ m * 2^k / 3")
    print("  log_2(n_k) ~ k + log_2(m/3)")
    print()
    print("これを beta=3/2 展開で表現すると:")
    print("  n を基数 beta=3/2 で展開: n = sum d_i * (3/2)^i")
    print("  Syracuse逆写像: T^{-1}(m) の各要素は")
    print("  m の beta 展開の桁を1つ追加したもの")
    print()

    # beta=3/2 展開を計算
    print("m=1 の beta=3/2 展開と逆像の対応:")
    m = 1
    for k in [2, 4, 6, 8, 10]:
        n = (m * (1<<k) - 1) // 3
        if n > 0 and n % 2 == 1:
            # beta展開
            x = n
            digits = []
            beta = 3/2
            for _ in range(20):
                d = int(x * beta)
                digits.append(d)
                x = x * beta - d
                if abs(x) < 1e-10:
                    break
            print(f"  k={k:2d}: n={n:8d}, beta展開={digits[:10]}")

    print("\n" + "=" * 80)
    print("完了")
    print("=" * 80)

if __name__ == "__main__":
    main()
