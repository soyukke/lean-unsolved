#!/usr/bin/env python3
"""
探索187v3: 禁止語閾値 L_0(M) の計算と理論的導出
高速化版: ビット演算とキャッシュを活用
"""

import json
import time
from collections import defaultdict
from functools import lru_cache

def v2(n):
    """2-adic valuation (ビット演算で高速化)"""
    if n == 0:
        return 999  # infinity proxy
    return (n & -n).bit_length() - 1

def check_word_mod2S(word):
    """語 word = (a_1,...,a_L) が実現可能か mod 2^S 判定。
    S = sum(word) として mod 2^S の全奇数残基を試す。
    """
    S = sum(word)
    # S が大きすぎる場合は打ち切り（24ビットまで厳密）
    bits = min(S, 22)
    mod = 1 << bits

    for n in range(1, mod, 2):
        m = n
        ok = True
        for a in word:
            val = 3 * m + 1
            actual_v = v2(val)
            if actual_v != a:
                ok = False
                break
            m = val >> a
        if ok:
            return True
    return False


def compute_L0_fast(M, max_L=25, verbose=True):
    """M に対して L_0(M) を高速計算。
    M^L が大きすぎたらストップ。
    """
    L0 = 0
    results = []
    consecutive_zero = 0

    for L in range(1, max_L + 1):
        total = M ** L
        if total > 200000:
            if verbose:
                print(f"    L={L}: {total} words > limit, stopping")
            break

        t0 = time.time()
        n_forbidden = 0
        forbidden_ex = []

        # 語の全列挙
        # itertools.product の代わりに再帰で生成（メモリ節約）
        def enumerate_words(prefix, remaining):
            nonlocal n_forbidden
            if remaining == 0:
                if not check_word_mod2S(prefix):
                    n_forbidden += 1
                    if n_forbidden <= 5:
                        forbidden_ex.append(list(prefix))
                return
            for a in range(1, M + 1):
                enumerate_words(prefix + (a,), remaining - 1)

        enumerate_words((), L)
        elapsed = time.time() - t0

        frac = n_forbidden / total if total > 0 else 0
        if verbose:
            print(f"    L={L}: {n_forbidden}/{total} forbidden ({frac:.6f}), {elapsed:.2f}s")
            if forbidden_ex:
                print(f"      ex: {forbidden_ex}")

        results.append({
            "L": L, "total": total, "forbidden": n_forbidden,
            "frac": frac, "examples": forbidden_ex[:5]
        })

        if n_forbidden > 0:
            L0 = L
            consecutive_zero = 0
        else:
            consecutive_zero += 1
            if consecutive_zero >= 3 and L > 2*M:
                if verbose:
                    print(f"    -> 3 consecutive zeros after L>{2*M}, stopping")
                break

    return L0, results


def fast_scan_M_range():
    """M=1..8 を高速スキャン"""
    print("="*60)
    print("Phase 1: L_0(M) の精密計算")
    print("="*60)

    L0_table = {}
    all_results = {}

    for M in range(1, 9):
        print(f"\n--- M = {M} ---")
        # M=1: alphabet {1}, very small search space
        # M=2: alphabet {1,2}, moderate
        # M=3..8: increasingly large
        if M <= 4:
            max_L = 3*M + 3
        elif M <= 6:
            max_L = 2*M + 4
        else:
            max_L = 2*M + 2

        L0, res = compute_L0_fast(M, max_L=max_L)
        L0_table[M] = L0
        all_results[M] = res
        print(f"  => L_0({M}) = {L0}")

    return L0_table, all_results


def forbidden_word_structure(M, L):
    """禁止語の内部構造を分析"""
    if M**L > 200000:
        return None

    forbidden_info = {
        "by_sum": defaultdict(lambda: {"forbidden": 0, "total": 0}),
        "by_first": defaultdict(lambda: {"forbidden": 0, "total": 0}),
        "by_last": defaultdict(lambda: {"forbidden": 0, "total": 0}),
        "count": 0,
    }

    def enum(prefix, remaining):
        if remaining == 0:
            word = prefix
            S = sum(word)
            is_forb = not check_word_mod2S(word)

            forbidden_info["by_sum"][S]["total"] += 1
            forbidden_info["by_first"][word[0]]["total"] += 1
            forbidden_info["by_last"][word[-1]]["total"] += 1
            if is_forb:
                forbidden_info["by_sum"][S]["forbidden"] += 1
                forbidden_info["by_first"][word[0]]["forbidden"] += 1
                forbidden_info["by_last"][word[-1]]["forbidden"] += 1
                forbidden_info["count"] += 1
            return
        for a in range(1, M+1):
            enum(prefix + (a,), remaining - 1)

    enum((), L)
    return forbidden_info


def saturation_analysis(M):
    """mod 2^k 飽和分析: v2値 ≤ M の遷移で到達可能な残基の飽和"""
    print(f"\n  mod 2^k 飽和 (M={M}):")

    for k in range(1, min(2*M+4, 14)):
        mod = 1 << k
        # v2 ≤ M の遷移で、各奇数残基から到達可能な次の残基を収集
        all_sources = set()  # v2 ≤ M を持つ始点
        all_targets = set()  # 到達先

        for r in range(1, mod, 2):
            val = 3 * r + 1
            a = v2(val)
            if 1 <= a <= M:
                all_sources.add(r)
                target = (val >> a) % mod
                all_targets.add(target)

        total_odd = mod >> 1
        src_cov = len(all_sources) / total_odd
        tgt_cov = len(all_targets) / total_odd

        print(f"    k={k}: sources={len(all_sources)}/{total_odd} ({src_cov:.4f}), "
              f"targets={len(all_targets)}/{total_odd} ({tgt_cov:.4f})")


def inverse_map_density(M):
    """逆写像密度: 各 v2 値について、mod 2^k で条件を満たす残基の割合"""
    print(f"\n  逆写像密度 (M={M}):")

    for a in range(1, M+1):
        # v2(3n+1) = a を満たす n の密度
        # n ≡ ? (mod 2^a) で exactly v2=a
        # mod 2^a で 3n+1 ≡ 0 (mod 2^a) の解: n ≡ (2^a-1)*inv(3) (mod 2^a)
        # ただし exactly a なので、mod 2^{a+1} で ≢ 0
        mod_a = 1 << a
        mod_a1 = 1 << (a+1)

        count_exact = 0
        for r in range(1, mod_a1, 2):
            if v2(3*r+1) == a:
                count_exact += 1

        total_odd = mod_a1 >> 1
        density = count_exact / total_odd
        print(f"    a={a}: density = {count_exact}/{total_odd} = {density:.6f} "
              f"(expected: 1/2^a = {1/mod_a:.6f})")


def theoretical_derivation(L0_table):
    """理論的導出"""
    print("\n" + "="*60)
    print("Phase 3: 理論的導出")
    print("="*60)

    # 表
    print(f"\n{'M':>3} | {'L0':>4} | {'2M-2':>5} | {'2M-1':>5} | {'2M':>4} | {'M+ceil(M*log2(3))-1':>20}")
    print("-" * 60)
    import math
    for M in sorted(L0_table.keys()):
        L0 = L0_table[M]
        log2_3M = M * math.log2(3)
        formula = M + math.ceil(log2_3M) - 1
        print(f"{M:>3} | {L0:>4} | {2*M-2:>5} | {2*M-1:>5} | {2*M:>4} | {formula:>20}")

    # 各種フィッティングを試す
    Ms = [m for m in sorted(L0_table.keys()) if L0_table[m] > 0]
    L0s = [L0_table[m] for m in Ms]

    if len(Ms) >= 3:
        # 線形回帰 L0 = aM + b
        n = len(Ms)
        sx = sum(Ms)
        sy = sum(L0s)
        sxy = sum(m*l for m, l in zip(Ms, L0s))
        sx2 = sum(m*m for m in Ms)

        a = (n*sxy - sx*sy) / (n*sx2 - sx*sx)
        b = (sy - a*sx) / n

        print(f"\n線形フィット: L_0(M) = {a:.4f}*M + ({b:.4f})")
        print("残差:")
        for m, l in zip(Ms, L0s):
            pred = a*m + b
            print(f"  M={m}: L_0={l}, pred={pred:.2f}, residual={l-pred:.2f}")

        # log フィット
        import math
        log_Ms = [math.log(m) for m in Ms]
        sx_l = sum(log_Ms)
        sxy_l = sum(lm*l for lm, l in zip(log_Ms, L0s))
        sx2_l = sum(lm*lm for lm in log_Ms)

        a_l = (n*sxy_l - sx_l*sy) / (n*sx2_l - sx_l*sx_l)
        b_l = (sy - a_l*sx_l) / n

        print(f"\nlog フィット: L_0(M) = {a_l:.4f}*log(M) + ({b_l:.4f})")

    # 理論的議論
    print("""
====== 理論的議論 ======

[定義の確認]
コラッツ shift space の v2 アルファベット Σ_M = {1,...,M}。
語 w = (a_1,...,a_L) ∈ Σ_M^L が「禁止」⟺ この v2 列を実現する奇数が存在しない。
L_0(M) = max{L : 長さ L の禁止語が存在する}。

[mod 2^S 判定定理]
語 w = (a_1,...,a_L), S = sum(a_i) について:
w が実現可能 ⟺ ある奇数 n ∈ {1,3,...,2^S-1} が w を実現。
（証明: n mod 2^S が v2 列を完全に決定するため）

[密度の計算]
v2(3n+1) = a の確率: P(a) = 1/2^a （n が一様ランダム奇数のとき）
長さ L の特定の語 w = (a_1,...,a_L) を実現する n の「密度」≈ 1/2^S。
mod 2^S 空間に 2^{S-1} 個の奇数残基があり、期待される実現数 ≈ 2^{S-1}/2^S = 1/2。

⟹ 各語の実現確率 ≈ 1 - e^{-1/2} ≈ 0.39（Poisson近似）

これは語の長さ L に依存しない！
しかし実際には、制約の構造（v2 = a_i の条件が非独立）により
短い語の方が禁止されやすい。

[禁止語数の漸近]
禁止語の割合 ≈ f(M, S_min) ここで S_min = L（全て1の場合）。
M^L 個の語のうち禁止語数 ≈ M^L * g(L, M)。
g(L, M) は L の増加とともに急速に減少。

L_0(M) は M^L * g(L, M) ≈ 1 となる点。

[2M-2 の意味]
仮説: L_0(M) = 2M-2 は以下から導かれる:
- v2=a の制約は mod 2^a で 1 つの残基クラスを指定
- 連続する v2 制約の「独立性」は約 1/(M-1) ずつ失われる
- 累積制約が mod 空間を完全にカバーするのに 2M-2 ステップ必要
""")

    return True


def main():
    t_start = time.time()

    # Phase 1: L_0 計算
    L0_table, all_results = fast_scan_M_range()

    # Phase 2: 構造分析
    print("\n" + "="*60)
    print("Phase 2: 構造分析")
    print("="*60)

    structure_data = {}
    for M in [2, 3, 4]:
        if M in L0_table and L0_table[M] > 0:
            L0 = L0_table[M]
            for L in [L0-1, L0, L0+1]:
                if L >= 1 and M**L <= 100000:
                    print(f"\nM={M}, L={L}:")
                    info = forbidden_word_structure(M, L)
                    if info:
                        key = f"M{M}_L{L}"
                        structure_data[key] = {
                            "forbidden_count": info["count"],
                            "by_sum": {str(k): dict(v) for k, v in sorted(info["by_sum"].items())},
                        }
                        for S, data in sorted(info["by_sum"].items()):
                            if data["forbidden"] > 0:
                                print(f"  S={S}: {data['forbidden']}/{data['total']} forbidden")

    # Phase 2b: 飽和分析
    for M in [2, 3, 4, 5]:
        saturation_analysis(M)
        inverse_map_density(M)

    # Phase 3: 理論
    theoretical_derivation(L0_table)

    elapsed = time.time() - t_start
    print(f"\n総計算時間: {elapsed:.1f}s")

    # 保存
    output = {
        "title": "禁止語閾値 L_0(M) の理論的導出",
        "L0_table": {str(k): v for k, v in L0_table.items()},
        "formula_candidates": {
            "2M-2": {str(k): 2*k-2 for k in range(1, 9)},
            "2M-1": {str(k): 2*k-1 for k in range(1, 9)},
        },
        "detailed_results": {str(k): v for k, v in all_results.items()},
        "structure_analysis": structure_data,
        "elapsed_seconds": elapsed
    }

    with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v3.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print("結果を results/forbidden_word_threshold_v3.json に保存しました")


if __name__ == "__main__":
    main()
