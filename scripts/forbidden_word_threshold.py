#!/usr/bin/env python3
"""
探索187: 禁止語閾値 L_0(M) の理論的導出

コラッツ写像の v2 (2-adic valuation) アルファベット {1,...,M} 上の
shift space における「禁止語閾値」L_0(M) を計算・分析する。

既知データ: L_0(3)=9(?), L_0(4)=6, L_0(6)=4 (仮)
目標: L_0(M) ≈ 2M - 2 の理論的根拠を探る

禁止語の定義:
- コラッツ写像 T(n) = n/2 (偶数), 3n+1 (奇数)
- 奇数 n に対し、v2(3n+1) がアルファベット文字を与える
- 長さ L の語 (a_1, ..., a_L) が「禁止」⟺ その v2 列を実現する奇数の初期値が存在しない
- L_0(M) = 全ての禁止語の長さの上限（それ以上長い禁止語は存在しない閾値）
"""

import json
import itertools
import math
from collections import defaultdict

def collatz_v2_sequence(n, length):
    """奇数nからコラッツ写像を適用し、v2列を返す。
    各ステップで奇数に到達するまで進み、v2(3n+1)を記録。
    lengthステップ分。"""
    seq = []
    x = n
    for _ in range(length):
        if x % 2 == 0:
            # 偶数なら奇数になるまで割る（これは前のステップの続き）
            raise ValueError("入力は奇数でなければならない")
        # 3x+1 を計算し、v2 を取る
        y = 3 * x + 1
        v = 0
        while y % 2 == 0:
            v += 1
            y //= 2
        seq.append(v)
        x = y  # 次の奇数
        if x == 1 and len(seq) < length:
            # 1に到達したら、1のサイクルを続ける: 3*1+1=4, v2(4)=2, next=1
            pass  # ループ継続
    return tuple(seq)


def enumerate_realizable_words(M, L, max_start=None):
    """アルファベット {1,...,M} で長さ L の実現可能な語を列挙。
    奇数 1, 3, 5, ... から開始してv2列を収集。"""
    if max_start is None:
        # 十分な初期値を調べる
        max_start = max(10000, 2**(L * M))

    # ただし max_start が大きすぎる場合は制限
    max_start = min(max_start, 10**7)

    realizable = set()
    for n in range(1, max_start + 1, 2):  # 奇数のみ
        try:
            seq = collatz_v2_sequence(n, L)
            # アルファベット {1,...,M} に収まるかチェック
            if all(1 <= v <= M for v in seq):
                realizable.add(seq)
        except:
            pass

    return realizable


def count_all_words(M, L):
    """アルファベット {1,...,M} で長さ L の全ての語の数"""
    return M ** L


def find_forbidden_words(M, L, max_start=10**6):
    """長さ L の禁止語を全て見つける"""
    realizable = enumerate_realizable_words(M, L, max_start)
    all_words = set(itertools.product(range(1, M+1), repeat=L))
    forbidden = all_words - realizable
    return forbidden, realizable


def compute_L0(M, max_L=20, max_start=10**6):
    """L_0(M) を計算: 禁止語が存在する最大の長さ"""
    print(f"\n=== M={M} の禁止語閾値を計算 ===")
    results = []
    last_nonzero_L = 0
    consecutive_zero = 0

    for L in range(1, max_L + 1):
        total = count_all_words(M, L)

        if total > 10**6 and L > 8:
            # 全列挙が非現実的な場合、サンプリング
            realizable = enumerate_realizable_words(M, L, max_start)
            n_real = len(realizable)
            n_forbidden = total - n_real
            exact = False
        else:
            forbidden, realizable = find_forbidden_words(M, L, max_start)
            n_real = len(realizable)
            n_forbidden = len(forbidden)
            exact = (total <= 10**6)

        frac_forbidden = n_forbidden / total if total > 0 else 0

        print(f"  L={L}: total={total}, realizable={n_real}, "
              f"forbidden={n_forbidden} ({frac_forbidden:.4f}), exact={exact}")

        results.append({
            "L": L,
            "total": total,
            "realizable": n_real,
            "forbidden": n_forbidden,
            "frac_forbidden": frac_forbidden,
            "exact": exact
        })

        if n_forbidden > 0:
            last_nonzero_L = L
            consecutive_zero = 0
        else:
            consecutive_zero += 1
            if consecutive_zero >= 3:
                print(f"  -> 3回連続で禁止語なし。L_0(M={M}) = {last_nonzero_L}")
                break

    return last_nonzero_L, results


def analyze_forbidden_structure(M, L, max_start=10**6):
    """禁止語の構造を分析"""
    forbidden, realizable = find_forbidden_words(M, L, max_start)

    if not forbidden:
        return None

    # 禁止語のパターン分析
    analysis = {
        "total_forbidden": len(forbidden),
        "sum_patterns": defaultdict(int),
        "first_letter_dist": defaultdict(int),
        "last_letter_dist": defaultdict(int),
    }

    for word in forbidden:
        analysis["sum_patterns"][sum(word)] += 1
        analysis["first_letter_dist"][word[0]] += 1
        analysis["last_letter_dist"][word[-1]] += 1

    return analysis


def theoretical_analysis():
    """理論的分析: なぜ L_0(M) ≈ 2M - 2 か"""
    print("\n" + "="*60)
    print("理論的分析: L_0(M) ≈ 2M - 2 の根拠")
    print("="*60)

    # v2列の制約を分析
    # n が奇数のとき、3n+1 = 3n + 1
    # v2(3n+1) = v2(3n+1)
    #
    # n ≡ 1 (mod 4) => 3n+1 ≡ 4 (mod 12) => v2 >= 2
    # n ≡ 3 (mod 4) => 3n+1 ≡ 10 (mod 12) => v2 = 1
    #
    # より一般に、n mod 2^k が v2 列の最初の数ステップを決定

    print("\n[1] mod 2^k による v2 の決定構造")
    for k in range(1, 8):
        mod = 2**k
        v2_map = {}
        for r in range(mod):
            if r % 2 == 0:
                continue  # 偶数はスキップ
            val = 3 * r + 1
            v = 0
            tmp = val
            while tmp % 2 == 0:
                v += 1
                tmp //= 2
            v2_map[r] = v
        print(f"  mod 2^{k}: 奇数残基 -> v2(3r+1): {dict(sorted(v2_map.items()))}")

    # v2 列の遷移行列を構築
    print("\n[2] v2 列の遷移制約")
    print("  v2(3n+1) = a のとき、次の奇数 m = (3n+1)/2^a")
    print("  m mod 2^j が次の v2 を決める")
    print("  => (a_1, a_2, ...) の列には mod 2^k 整合性制約がある")

    # 具体的に: 長さ L の語が実現可能 ⟺
    # 存在する奇数 n s.t. コラッツ軌道の v2 列が一致
    # これは n mod 2^(a_1+a_2+...+a_L) の条件として書ける

    print("\n[3] 実現可能性の条件")
    print("  語 (a_1,...,a_L) が実現可能 ⟺")
    print("  連立合同式 n ≡ r_i (mod 2^{s_i}) が解を持つ")
    print("  ここで s_i は部分和に依存")

    return True


def compute_v2_transition_matrix(M):
    """v2値に基づく遷移行列を計算
    状態: 現在の奇数の mod 2^K での残基
    遷移: v2(3n+1) = a のとき次の奇数の残基"""

    K = 2 * M + 2  # 十分な精度
    mod = 2**K

    # 遷移を計算
    transitions = {}  # (残基, v2値) -> 次の残基
    for r in range(1, mod, 2):  # 奇数残基
        val = 3 * r + 1
        v = 0
        tmp = val
        while tmp % 2 == 0:
            v += 1
            tmp //= 2
        next_r = tmp % mod
        if v <= M:
            transitions[(r % mod, v)] = next_r % mod

    return transitions


def backward_propagation_analysis(M, max_L=15):
    """逆方向からの分析: 長さLの語の実現可能性を後ろから組み立てる

    核心的アイデア:
    語 (a_1,...,a_L) に対し、S = a_1 + ... + a_L とする。
    n が奇数で、この v2 列を実現するためには、
    n mod 2^S が特定の値でなければならない。

    M 以下の v2 値のみ使うとき、S <= L*M。
    一方、各 a_i >= 1 なので S >= L。

    禁止語の発生条件: mod 2^S の制約が矛盾するケース
    """
    print("\n" + "="*60)
    print(f"逆伝播分析: M={M}")
    print("="*60)

    results = []

    for L in range(1, max_L + 1):
        # 全ての語を調べる（M^L が小さいとき）
        total = M**L
        if total > 5 * 10**5:
            print(f"  L={L}: 語が多すぎる（{total}個）、スキップ")
            break

        n_realizable = 0
        n_forbidden = 0
        forbidden_sums = defaultdict(int)

        for word in itertools.product(range(1, M+1), repeat=L):
            S = sum(word)
            # この語を実現する奇数nが存在するか？
            # n mod 2^S を決定する
            # 逐次的に構成: n -> (3n+1)/2^{a_1} -> ...

            # 逆に: 最後の奇数から逆算
            # 最後の奇数 m_L は任意の奇数
            # m_{i-1} は (2^{a_i} * m_i - 1) / 3 が奇数整数でなければならない

            # 最後から逆算
            possible = True
            # m_L は任意の奇数とする → mod 2^K で全ての奇数残基を試す
            K_check = S + 4  # 十分な精度
            mod_check = 2**K_check

            # 効率的に: mod mod_check で逆算
            found = False
            # m_L の候補: mod mod_check の全ての奇数
            for m_last in range(1, min(mod_check, 2**14), 2):
                m = m_last
                ok = True
                for i in range(L-1, -1, -1):
                    a = word[i]
                    # m_i から m_{i-1} への逆算
                    # m_i = (3 * m_{i-1} + 1) / 2^{a_i}
                    # => 3 * m_{i-1} + 1 = m_i * 2^{a_i}
                    # => m_{i-1} = (m_i * 2^{a_i} - 1) / 3
                    val = m * (2**a) - 1
                    if val % 3 != 0:
                        ok = False
                        break
                    prev = val // 3
                    if prev <= 0 or prev % 2 == 0:
                        ok = False
                        break
                    m = prev
                if ok:
                    found = True
                    break

            if found:
                n_realizable += 1
            else:
                n_forbidden += 1
                forbidden_sums[S] += 1

        print(f"  L={L}: realizable={n_realizable}/{total}, "
              f"forbidden={n_forbidden}, forbidden_sums={dict(sorted(forbidden_sums.items()))}")
        results.append({
            "L": L,
            "total": total,
            "realizable": n_realizable,
            "forbidden": n_forbidden,
            "forbidden_sum_dist": dict(sorted(forbidden_sums.items()))
        })

    return results


def refined_backward_analysis(M, max_L=15):
    """改良版逆伝播: より多くの末尾候補を試す"""
    print(f"\n=== 改良逆伝播: M={M} ===")
    results = []

    for L in range(1, max_L + 1):
        total = M**L
        if total > 2 * 10**5:
            print(f"  L={L}: {total}語、スキップ")
            break

        n_realizable = 0
        n_forbidden = 0
        forbidden_words = []

        for word in itertools.product(range(1, M+1), repeat=L):
            S = sum(word)

            # 前方向で探索: n = 1, 3, 5, ... から
            found = False

            # mod 2^S で一致するnを直接構成
            # n mod 2^S の各候補について
            mod_S = 2**S
            max_test = min(mod_S, 2**16)

            for n_mod in range(1, max_test, 2):
                m = n_mod
                ok = True
                for i in range(L):
                    a = word[i]
                    val = 3 * m + 1
                    # v2(val) を計算
                    v = 0
                    tmp = val
                    while tmp % 2 == 0:
                        v += 1
                        tmp //= 2
                    if v != a:
                        ok = False
                        break
                    m = tmp  # 次の奇数
                if ok:
                    found = True
                    break

            if found:
                n_realizable += 1
            else:
                n_forbidden += 1
                if n_forbidden <= 20:
                    forbidden_words.append(word)

        frac = n_forbidden / total if total > 0 else 0
        print(f"  L={L}: total={total}, realizable={n_realizable}, "
              f"forbidden={n_forbidden} ({frac:.6f})")
        if forbidden_words and L <= 8:
            print(f"    禁止語の例: {forbidden_words[:10]}")

        results.append({
            "L": L,
            "total": total,
            "realizable": n_realizable,
            "forbidden": n_forbidden,
            "frac_forbidden": frac,
            "forbidden_examples": [list(w) for w in forbidden_words[:10]]
        })

    return results


def precise_L0_determination():
    """各 M について L_0(M) を精密に決定"""
    print("\n" + "="*60)
    print("精密な L_0(M) の決定")
    print("="*60)

    L0_values = {}
    all_results = {}

    for M in range(1, 10):
        print(f"\n--- M = {M} ---")
        results = refined_backward_analysis(M, max_L=min(20, max(2*M+4, 8)))

        # L_0 を決定: 禁止語が存在する最大のL
        L0 = 0
        for r in results:
            if r["forbidden"] > 0:
                L0 = r["L"]

        L0_values[M] = L0
        all_results[M] = results
        print(f"  => L_0({M}) = {L0}")

    return L0_values, all_results


def analyze_L0_formula(L0_values):
    """L_0(M) のパターンを分析"""
    print("\n" + "="*60)
    print("L_0(M) のパターン分析")
    print("="*60)

    print(f"\n{'M':>3} | {'L_0(M)':>6} | {'2M-2':>5} | {'2M':>4} | {'差(L0-2M+2)':>11}")
    print("-" * 45)
    for M in sorted(L0_values.keys()):
        L0 = L0_values[M]
        formula_2m2 = 2*M - 2
        formula_2m = 2*M
        diff = L0 - formula_2m2
        print(f"{M:>3} | {L0:>6} | {formula_2m2:>5} | {formula_2m:>4} | {diff:>11}")

    # フィッティング
    Ms = sorted(L0_values.keys())
    L0s = [L0_values[m] for m in Ms]

    # 線形フィット: L0 = a*M + b
    if len(Ms) >= 2:
        # 最小二乗
        n = len(Ms)
        sum_M = sum(Ms)
        sum_L0 = sum(L0s)
        sum_ML0 = sum(m*l for m, l in zip(Ms, L0s))
        sum_M2 = sum(m*m for m in Ms)

        a = (n * sum_ML0 - sum_M * sum_L0) / (n * sum_M2 - sum_M**2)
        b = (sum_L0 - a * sum_M) / n

        print(f"\n線形フィット: L_0(M) ≈ {a:.4f} * M + ({b:.4f})")

        # 残差
        print("\n残差:")
        for m, l in zip(Ms, L0s):
            pred = a * m + b
            print(f"  M={m}: L_0={l}, 予測={pred:.2f}, 残差={l-pred:.2f}")

    return Ms, L0s


def mod2k_saturation_connection(M):
    """mod 2^k 飽和法則との接続を分析

    コラッツ写像の mod 2^k 動力学:
    - k ステップ後、到達可能な残基が飽和する
    - 飽和に必要な最小ステップ数と L_0(M) の関係
    """
    print(f"\n=== mod 2^k 飽和と L_0(M={M}) の接続 ===")

    # mod 2^k で k=1,...,2M+4 まで
    for k in range(1, 2*M + 5):
        mod = 2**k
        # 全ての奇数残基から1ステップのコラッツ写像
        # n -> (3n+1)/2^{v2(3n+1)}
        reachable_from = {}  # v2値ごとの到達可能残基

        for v in range(1, M+1):
            reached = set()
            for r in range(1, mod, 2):
                val = 3 * r + 1
                v2 = 0
                tmp = val
                while tmp % 2 == 0:
                    v2 += 1
                    tmp //= 2
                if v2 == v:
                    reached.add(tmp % mod)
            reachable_from[v] = reached

        # 全 v2 値を通じた到達可能残基の和集合
        all_reached = set()
        for v in range(1, M+1):
            all_reached |= reachable_from[v]

        total_odd = mod // 2
        coverage = len(all_reached) / total_odd if total_odd > 0 else 0

        print(f"  k={k}: mod 2^{k}, 到達可能={len(all_reached)}/{total_odd} "
              f"({coverage:.4f})")

        # 各v2値の寄与
        detail = {v: len(reachable_from[v]) for v in range(1, M+1)}
        if k <= 8:
            print(f"    v2値ごと: {detail}")


def sum_constraint_analysis(M, max_L=15):
    """和の制約による禁止語の理論的分析

    語 (a_1,...,a_L) の和 S = a_1+...+a_L に対し:
    - 実現可能 => n mod 2^S の解が存在
    - 各ステップの v2 値は n mod 2^(a_1+...+a_i) で決定
    - 制約の「自由度」: n mod 2^S は S ビットの情報
    - 一方、語は L 個の制約を課す
    - L > S の場合、制約が冗長 => 全て実現可能
    - L ≤ S の場合、非自明な制約が残る可能性

    S の最小値 = L (全て1), 最大値 = L*M
    S ≤ L*M かつ S ≥ L

    禁止語が生じる条件: mod 2^S で整合的な残基が存在しない
    """
    print(f"\n=== 和制約分析: M={M} ===")

    for L in range(1, max_L + 1):
        total = M**L
        if total > 5*10**4:
            break

        forbidden_by_S = defaultdict(int)
        realizable_by_S = defaultdict(int)

        for word in itertools.product(range(1, M+1), repeat=L):
            S = sum(word)
            mod_S = 2**S
            max_test = min(mod_S, 2**16)

            found = False
            for n_mod in range(1, max_test, 2):
                m = n_mod
                ok = True
                for i in range(L):
                    a = word[i]
                    val = 3 * m + 1
                    v = 0
                    tmp = val
                    while tmp % 2 == 0:
                        v += 1
                        tmp //= 2
                    if v != a:
                        ok = False
                        break
                    m = tmp
                if ok:
                    found = True
                    break

            if found:
                realizable_by_S[S] += 1
            else:
                forbidden_by_S[S] += 1

        if forbidden_by_S:
            print(f"  L={L}: 禁止語のS分布: {dict(sorted(forbidden_by_S.items()))}")
            # Sの値と禁止率
            for S in sorted(set(list(forbidden_by_S.keys()) + list(realizable_by_S.keys()))):
                f = forbidden_by_S.get(S, 0)
                r = realizable_by_S.get(S, 0)
                total_S = f + r
                if total_S > 0:
                    # S >= 2L ならば禁止語なし？
                    pass
        else:
            print(f"  L={L}: 禁止語なし")


if __name__ == "__main__":
    print("="*60)
    print("探索187: 禁止語閾値 L_0(M) の理論的導出")
    print("="*60)

    # Phase 1: 各Mについて L_0 を精密計算
    L0_values, all_results = precise_L0_determination()

    # Phase 2: パターン分析
    Ms, L0s = analyze_L0_formula(L0_values)

    # Phase 3: 和制約分析（小さいMのみ）
    for M in [2, 3, 4]:
        sum_constraint_analysis(M, max_L=12)

    # Phase 4: mod 2^k 飽和接続
    for M in [2, 3, 4, 5]:
        mod2k_saturation_connection(M)

    # 結果保存
    output = {
        "L0_values": {str(k): v for k, v in L0_values.items()},
        "pattern_analysis": {
            "Ms": Ms,
            "L0s": L0s,
        },
        "detailed_results": {
            str(k): v for k, v in all_results.items()
        }
    }

    with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print("\n結果を results/forbidden_word_threshold.json に保存しました")
