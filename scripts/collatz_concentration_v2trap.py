#!/usr/bin/env python3
"""
追加分析: v₂=2 トラップ現象の解明と集中不等式への影響

前回発見: P(v₂_{i+1}=2 | v₂_i=2) = 0.982 という異常に強い自己相関。
これはd/u > log₂3 を強化する方向に働くのか？

分析項目:
1. v₂=2 トラップの代数的メカニズム
2. トラップ脱出後のv₂分布
3. d/u への影響（トラップがd/uを押し上げるか）
4. mod構造を使った厳密解析
"""

import math

def v2(n):
    if n == 0:
        return 999
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def v2_of_3n1(n):
    return v2(3 * n + 1)

LOG2_3 = math.log2(3)

# =========================================================
# 1. v₂=2 トラップの代数的メカニズム
# =========================================================

def analyze_v2_trap():
    print("=" * 60)
    print("1. v₂=2 トラップの代数的メカニズム")
    print("=" * 60)

    # v₂(3n+1) = 2 ⟺ 4 | (3n+1) だが 8 ∤ (3n+1)
    # ⟺ 3n+1 ≡ 4 (mod 8) ⟺ 3n ≡ 3 (mod 8) ⟺ n ≡ 1 (mod 8)
    # ただし n は奇数なので n ≡ 1 (mod 8) ∨ n ≡ 5 (mod 8) が奇数条件
    # n ≡ 1 (mod 8): 3n+1 ≡ 4 (mod 8) → v₂=2 ✓
    # n ≡ 5 (mod 8): 3n+1 ≡ 16 (mod 24) → v₂≥4

    print("  v₂(3n+1) = 2 の条件:")
    print("    3n+1 ≡ 4 (mod 8), すなわち n ≡ 1 (mod 8)")
    print()

    # T(n) = (3n+1)/4 when v₂=2
    # n ≡ 1 (mod 8) → T(n) = (3n+1)/4
    # T(n) mod 8 = (3·1+1)/4 mod 8 = 1 mod 8 ← ★ ここがトラップ
    print("  n ≡ 1 (mod 8) のとき:")
    for r in range(1, 64, 8):
        if r % 2 == 0:
            continue
        T_r = (3 * r + 1) // 4
        v2_val = v2(3 * r + 1)
        T_mod8 = T_r % 8
        next_v2 = v2(3 * T_r + 1) if T_r % 2 == 1 else "偶数"
        print(f"    r={r:3d} (mod 64): T(r)={T_r}, T(r) mod 8 = {T_mod8}, "
              f"v₂(3T(r)+1) = {next_v2}")

    # mod 16 での精密化
    print("\n  mod 16 での分析:")
    for r in range(1, 16, 2):
        v2_val = v2(3 * r + 1)
        if v2_val >= 2:
            T_r = (3 * r + 1) // (2**v2_val)
            T_mod = T_r % 16
            print(f"    r≡{r:2d} (mod 16): v₂={v2_val}, T(r)≡{T_mod} (mod 16)")

    # v₂=2 の連続長の分布
    print("\n  v₂=2 連続ラン長の分布:")
    run_lengths = []
    for n in range(1, 10001, 2):
        seq = []
        current = n
        for _ in range(500):
            if current <= 0:
                break
            seq.append(v2_of_3n1(current))
            current = syracuse(current)
            if current == 1:
                break

        # v₂=2 の連続ラン長を計測
        i = 0
        while i < len(seq):
            if seq[i] == 2:
                run_start = i
                while i < len(seq) and seq[i] == 2:
                    i += 1
                run_lengths.append(i - run_start)
            else:
                i += 1

    if run_lengths:
        from collections import Counter
        counts = Counter(run_lengths)
        total_runs = len(run_lengths)
        print(f"    総ラン数: {total_runs}")
        for length in sorted(counts.keys())[:15]:
            print(f"    長さ {length:3d}: {counts[length]:6d} ({counts[length]/total_runs:.4f})")
        avg_run = sum(run_lengths) / len(run_lengths)
        max_run = max(run_lengths)
        print(f"    平均ラン長: {avg_run:.2f}")
        print(f"    最大ラン長: {max_run}")


# =========================================================
# 2. トラップがd/uに与える影響
# =========================================================

def trap_impact_on_du():
    print("\n" + "=" * 60)
    print("2. v₂=2 トラップが d/u に与える影響")
    print("=" * 60)

    # v₂=2のトラップ中は d/u = 2.0 > log₂3
    # トラップ外ではv₂=1が多い傾向 → d/u 低下
    print(f"  トラップ中: v₂=2 → d/u=2.0 > log₂3={LOG2_3:.4f} ✓")
    print(f"  トラップ外: v₂の混合分布")

    # トラップ内外でのv₂平均を分離測定
    v2_in_trap = []
    v2_out_trap = []

    for n in range(1, 10001, 2):
        current = n
        prev_v2 = None
        in_trap = False
        for _ in range(300):
            if current <= 0:
                break
            v = v2_of_3n1(current)
            if v == 2 and (prev_v2 == 2 or prev_v2 is None):
                in_trap = True
            else:
                in_trap = False

            if in_trap:
                v2_in_trap.append(v)
            else:
                v2_out_trap.append(v)

            prev_v2 = v
            current = syracuse(current)
            if current == 1:
                break

    if v2_in_trap:
        mean_in = sum(v2_in_trap) / len(v2_in_trap)
        print(f"\n  トラップ内 v₂平均: {mean_in:.4f} (n={len(v2_in_trap)})")
    if v2_out_trap:
        mean_out = sum(v2_out_trap) / len(v2_out_trap)
        print(f"  トラップ外 v₂平均: {mean_out:.4f} (n={len(v2_out_trap)})")

    # トラップ外でのv₂分布
    print(f"\n  トラップ外のv₂分布:")
    from collections import Counter
    counts = Counter(v2_out_trap)
    total_out = len(v2_out_trap)
    for v in sorted(counts.keys())[:10]:
        observed = counts[v] / total_out
        expected = 1 / (2**v)
        print(f"    v₂={v}: 観測 {observed:.4f}, 理論(幾何) {expected:.4f}, "
              f"比 {observed/expected:.3f}")


# =========================================================
# 3. 修正集中不等式: トラップ考慮版
# =========================================================

def modified_concentration():
    print("\n" + "=" * 60)
    print("3. トラップ考慮版の集中不等式")
    print("=" * 60)

    # v₂=2のトラップの平均持続時間をτとすると、
    # k ステップ中、約 k·p_trap 時間がトラップ内で v₂=2
    # 残りの k·(1-p_trap) 時間がトラップ外

    # 定常状態でのトラップ占有率
    trap_steps = 0
    total_steps = 0
    for n in range(1, 5001, 2):
        current = n
        prev_v2 = None
        for _ in range(500):
            if current <= 0:
                break
            v = v2_of_3n1(current)
            total_steps += 1
            if v == 2:
                trap_steps += 1
            prev_v2 = v
            current = syracuse(current)
            if current == 1:
                break

    p_trap = trap_steps / total_steps if total_steps > 0 else 0
    print(f"  v₂=2 の定常占有率: {p_trap:.4f}")
    print(f"  理論値 P(v₂=2) = 1/4 = 0.2500")

    # 修正平均: p_trap * 2 + (1-p_trap) * E_out
    # E_out を推定
    v2_out_vals = []
    for n in range(1, 5001, 2):
        current = n
        for _ in range(500):
            if current <= 0:
                break
            v = v2_of_3n1(current)
            if v != 2:
                v2_out_vals.append(v)
            current = syracuse(current)
            if current == 1:
                break

    E_out = sum(v2_out_vals) / len(v2_out_vals) if v2_out_vals else 0
    E_total = p_trap * 2 + (1 - p_trap) * E_out
    print(f"  E[v₂ | v₂≠2] = {E_out:.4f}")
    print(f"  総合 E[v₂] = {p_trap:.4f}·2 + {1-p_trap:.4f}·{E_out:.4f} = {E_total:.4f}")

    # トラップを一つのブロックとして扱う
    # ブロック内: 確定的にv₂=2 → d/u=2.0
    # ブロック間: ほぼ独立 → Cramérを適用
    print(f"\n  ブロック化した集中不等式:")
    print(f"    トラップブロック: d/u = 2.0 (確定)")
    print(f"    非トラップ部分: E[v₂] = {E_out:.4f}")
    print(f"    非トラップ部分の I(log₂3) を計算...")

    # 非トラップv₂の分布からCramér関数を数値的に計算
    from collections import Counter
    counts = Counter(v2_out_vals)
    total = len(v2_out_vals)
    print(f"\n    非トラップv₂分布:")
    probs = {}
    for v in sorted(counts.keys())[:12]:
        p = counts[v] / total
        probs[v] = p
        print(f"      v₂={v}: {p:.4f}")

    # 数値的にCramér関数 I(x) = sup_t(tx - log M(t)) を計算
    # M(t) = Σ p_v · exp(t·v)
    target = LOG2_3
    best_I = -float('inf')
    best_t = 0
    for t_int in range(-10000, 1000):
        t = t_int / 1000.0
        log_M = 0
        M_val = sum(p * math.exp(t * v) for v, p in probs.items())
        if M_val <= 0:
            continue
        log_M = math.log(M_val)
        I_val = t * target - log_M
        if I_val > best_I:
            best_I = I_val
            best_t = t

    print(f"\n    非トラップ分布の I(log₂3) = {best_I:.5f} (t*={best_t:.4f})")
    print(f"    幾何分布の I(log₂3) = 0.05498 との比較")

    # 最悪ケース: 全てが非トラップの場合
    print(f"\n    最悪ケース推定:")
    print(f"      P(S_k/k < log₂3) ≤ exp(-{best_I:.5f}·k)")
    for k in [100, 500, 1000]:
        val = math.exp(-best_I * k) if best_I * k < 700 else 0.0
        print(f"      k={k}: {val:.6e}")


# =========================================================
# 4. 大きな初期値での検証
# =========================================================

def large_n_verification():
    print("\n" + "=" * 60)
    print("4. 大きな初期値での d/u 検証")
    print("=" * 60)

    import random
    random.seed(42)

    k_steps = 500
    worst_ratio = float('inf')
    worst_n = 0
    ratios = []

    test_ranges = [
        ("10^4付近", [random.randrange(10001, 20000, 2) for _ in range(1000)]),
        ("10^6付近", [random.randrange(1000001, 2000000, 2) for _ in range(1000)]),
        ("10^9付近", [random.randrange(1000000001, 2000000000, 2) for _ in range(500)]),
        ("10^12付近", [random.randrange(10**12+1, 2*10**12, 2) for _ in range(200)]),
    ]

    for label, seeds in test_ranges:
        range_ratios = []
        range_worst = float('inf')
        range_worst_n = 0

        for n in seeds:
            if n % 2 == 0:
                n += 1
            seq = []
            current = n
            for _ in range(k_steps):
                if current <= 0:
                    break
                v = v2_of_3n1(current)
                seq.append(v)
                current = syracuse(current)
                if current == 1:
                    current = 1

            if len(seq) >= k_steps:
                ratio = sum(seq) / len(seq)
                range_ratios.append(ratio)
                if ratio < range_worst:
                    range_worst = ratio
                    range_worst_n = n

        if range_ratios:
            avg = sum(range_ratios) / len(range_ratios)
            print(f"\n  {label} ({len(range_ratios)}軌道, k={k_steps}):")
            print(f"    平均 d/u = {avg:.5f}")
            print(f"    最小 d/u = {range_worst:.5f} (n={range_worst_n})")
            print(f"    d/u < log₂3: {sum(1 for r in range_ratios if r < LOG2_3)}/{len(range_ratios)}")
            print(f"    最小の余裕 = {range_worst - LOG2_3:.5f}")


# =========================================================
# 5. 結論: Borel-Cantelli による「ほぼ全て」の定式化
# =========================================================

def borel_cantelli_formulation():
    print("\n" + "=" * 60)
    print("5. Borel-Cantelli 型の定式化")
    print("=" * 60)

    I_x = 0.05498

    print(f"""
  定理（条件付き）:
    v₂ 列が十分な mixing 条件を満たすなら:

    A_k(n) = {{S_k(n)/k < log₂3}} に対し
    P(A_k(n)) ≤ C · exp(-I·k) where I ≈ {I_x:.5f}

  Borel-Cantelli の適用:
    Σ_{{k=1}}^∞ P(A_k(n)) ≤ C · Σ exp(-I·k) = C/(exp(I)-1) ≈ C·{1/(math.exp(I_x)-1):.1f}

    → 有限 → ほとんどすべての n に対し、
       十分大きな k から S_k(n)/k ≥ log₂3

  数値的意味:
    k ≥ 100 では P(d/u < log₂3) < 0.005
    k ≥ 200 では P(d/u < log₂3) < 0.00002
    k ≥ 500 では P(d/u < log₂3) < 10^{{-12}}

  重要な注意:
    1. 「ほとんどすべてのn」＝ 例外集合は密度0
       → しかし無限個の例外が存在する可能性は排除できない
    2. mixing 条件の厳密な証明がこのアプローチの核心的課題
    3. Tao(2019)はこの困難を mod 2^k の精密な解析で回避
""")


# =========================================================
# メイン
# =========================================================

def main():
    analyze_v2_trap()
    trap_impact_on_du()
    modified_concentration()
    large_n_verification()
    borel_cantelli_formulation()

if __name__ == "__main__":
    main()
