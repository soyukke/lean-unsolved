#!/usr/bin/env python3
"""
探索187v2: 禁止語閾値 L_0(M) の理論的導出（効率化版）

核心: 奇数 n に対し T(n) = (3n+1)/2^{v2(3n+1)} と定義。
v2列 (a_1,...,a_L) が「実現可能」⟺ ある奇数 n が存在し、
T^0(n)=n, T^1(n) の v2 = a_1, T^2(n) の v2 = a_2, ...

重要な性質: v2列は n mod 2^S (S=sum of a_i) で完全に決定される。
"""

import json
import itertools
from collections import defaultdict
import time

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v

def check_word_realizable(word, max_mod_bits=20):
    """語 word = (a_1,...,a_L) が実現可能か判定。

    n mod 2^S で完全に決まるので、mod 2^S の全奇数残基を試す。
    S = sum(word)。ただし S が大きい場合は上限を設ける。
    """
    S = sum(word)
    L = len(word)

    # mod 2^S で判定可能。ただし S が大きすぎる場合はサンプリング
    check_bits = min(S, max_mod_bits)
    mod_check = 2**check_bits

    for n_mod in range(1, mod_check, 2):
        m = n_mod
        ok = True
        for a in word:
            val = 3 * m + 1
            actual_v = v2(val)
            if actual_v != a:
                ok = False
                break
            m = val >> a  # (3m+1) / 2^a
            # m が偶数になる場合は mod の影響
            # mod_check 内で動くので、奇数でなくなる可能性
            # ただし正しい v2 であれば m は奇数のはず
        if ok:
            return True

    return False

def check_word_realizable_exact(word):
    """語 word の実現可能性を厳密判定。

    n mod 2^S の全奇数残基を試す（S が小さい場合）。
    """
    S = sum(word)
    if S > 24:  # 2^24 = 16M は大きすぎる
        return check_word_realizable(word, max_mod_bits=20)

    mod_S = 2**S
    for n_mod in range(1, mod_S, 2):
        m = n_mod
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


def compute_forbidden_for_M(M, max_L=None):
    """M に対して各長さの禁止語数を計算"""
    if max_L is None:
        max_L = 3 * M + 2

    results = []
    L0 = 0

    for L in range(1, max_L + 1):
        total = M ** L
        if total > 300000:
            print(f"    L={L}: M^L = {total} > 300000, 打ち切り")
            break

        t0 = time.time()
        n_forbidden = 0
        forbidden_examples = []

        for word in itertools.product(range(1, M+1), repeat=L):
            if not check_word_realizable_exact(word):
                n_forbidden += 1
                if n_forbidden <= 5:
                    forbidden_examples.append(list(word))

        n_realizable = total - n_forbidden
        frac = n_forbidden / total
        elapsed = time.time() - t0

        print(f"    L={L}: {n_forbidden}/{total} forbidden ({frac:.6f}), {elapsed:.1f}s")
        if forbidden_examples:
            print(f"      例: {forbidden_examples}")

        if n_forbidden > 0:
            L0 = L

        results.append({
            "L": L, "total": total, "forbidden": n_forbidden,
            "realizable": n_realizable, "frac": frac,
            "examples": forbidden_examples
        })

        # 3回連続で禁止語0なら終了
        if L >= 3 and all(r["forbidden"] == 0 for r in results[-3:]):
            print(f"    -> 3回連続禁止語なし、終了")
            break

    return L0, results


def main():
    print("="*60)
    print("探索187: 禁止語閾値 L_0(M) の効率化版")
    print("="*60)

    L0_table = {}
    all_details = {}

    for M in range(1, 9):
        print(f"\n--- M = {M} ---")
        L0, details = compute_forbidden_for_M(M)
        L0_table[M] = L0
        all_details[M] = details
        print(f"  => L_0({M}) = {L0}")

    # パターン分析
    print("\n" + "="*60)
    print("パターン分析")
    print("="*60)

    print(f"\n{'M':>3} | {'L_0(M)':>6} | {'2M-2':>5} | {'2M-1':>5} | {'2M':>4} | {'floor(log2(3^M-1))':>18}")
    print("-" * 65)
    for M in sorted(L0_table.keys()):
        L0 = L0_table[M]
        import math
        log_val = math.floor(math.log2(3**M - 1)) if M > 0 else 0
        print(f"{M:>3} | {L0:>6} | {2*M-2:>5} | {2*M-1:>5} | {2*M:>4} | {log_val:>18}")

    # 理論的分析
    print("\n" + "="*60)
    print("理論的分析")
    print("="*60)

    print("""
禁止語閾値の理論的構造:

[核心] 語 w = (a_1,...,a_L)、S = sum(a_i) とする。
- w が実現可能 ⟺ ある奇数 n (mod 2^S) が存在し、
  コラッツ軌道の v2 列が w に一致。
- n は S ビットの情報を持つ（ただし奇数制約で1ビット消費 → S-1 ビット自由）
- L 個の制約 v2 = a_i は、合計で約 S ビットの制約を課す
  （各 a_i は a_i ビットの情報に対応）

[禁止語発生の条件]
- a_i の値が全て 1 のとき: S = L、制約は厳しい
- a_i の値が大きいとき: S >> L、自由度が多く実現可能性が高い

[閾値のメカニズム]
M が小さい → 各 a_i が小さい → S が小さい → mod 2^S の空間が狭い
→ 制約が「衝突」しやすい → 禁止語が生まれやすい

Lが大きくなると:
- 可能な語の数 M^L は指数増大
- しかし各語の和 S ≥ L は線形増大
- mod 2^S の残基数 2^{S-1} も指数増大
- → 禁止語の割合は急速に減少
""")

    # v2列の mod 構造の詳細分析
    print("\n" + "="*60)
    print("v2列と mod 2^k の精密関係")
    print("="*60)

    # M=2 の場合の詳細
    M_detail = 2
    print(f"\nM={M_detail} の詳細: アルファベット {{1, 2}}")
    print("長さ1の語:")
    for a in range(1, M_detail+1):
        # v2(3n+1) = a となる n mod 2^a の条件
        mod_a = 2**a
        valid_n = []
        for r in range(1, mod_a, 2):
            if v2(3*r+1) == a:
                valid_n.append(r)
        print(f"  v2(3n+1)={a}: n ≡ {valid_n} (mod {mod_a})")

    print("\nM=2 の長さ2の語:")
    for word in itertools.product(range(1, M_detail+1), repeat=2):
        S = sum(word)
        mod_S = 2**S
        valid_starts = []
        for r in range(1, mod_S, 2):
            m = r
            ok = True
            for a in word:
                val = 3*m+1
                if v2(val) != a:
                    ok = False
                    break
                m = val >> a
            if ok:
                valid_starts.append(r)
        status = "実現可能" if valid_starts else "禁止"
        print(f"  {word}: S={S}, n ≡ {valid_starts} (mod {mod_S}) [{status}]")

    # 1/3 の mod 2^k 構造
    print("\n" + "="*60)
    print("3の逆元と禁止語の関係")
    print("="*60)

    print("""
鍵となる観察:
v2(3n+1) = a ⟺ 3n+1 ≡ 0 (mod 2^a) かつ 3n+1 ≢ 0 (mod 2^{a+1})
⟺ n ≡ (2^a - 1)/3 (mod 2^a) かつ n ≢ (2^{a+1}-1)/3 (mod 2^{a+1})

(2^a - 1)/3 が整数であるためには 2^a ≡ 1 (mod 3)、つまり a が偶数。
a が奇数の場合: 2^a ≡ 2 (mod 3) なので (2^a-1)/3 は整数でない...

これは正しくない。3n ≡ -1 (mod 2^a) つまり n ≡ -1/3 ≡ -3^{-1} (mod 2^a)。
mod 2^a における 3 の逆元は:
""")

    for a in range(1, 9):
        mod_a = 2**a
        # 3^{-1} mod 2^a
        inv3 = pow(3, -1, mod_a)
        # n ≡ (2^a * t - 1) * inv3 (mod 2^a) for some t
        # 実際には 3n + 1 ≡ 0 (mod 2^a) => n ≡ (-1)*inv3 = mod_a - inv3
        n_cond = (mod_a - inv3) % mod_a
        # さらに v2 = a exactly なので mod 2^{a+1} ではない
        if a < 8:
            mod_a1 = 2**(a+1)
            inv3_1 = pow(3, -1, mod_a1)
            n_cond_1 = (mod_a1 - inv3_1) % mod_a1
            print(f"  a={a}: 3^{{-1}} mod 2^{a} = {inv3}, "
                  f"n ≡ {n_cond} (mod {mod_a}), "
                  f"かつ n ≢ {n_cond_1} (mod {mod_a1})")
        else:
            print(f"  a={a}: 3^{{-1}} mod 2^{a} = {inv3}, n ≡ {n_cond} (mod {mod_a})")

    # 遷移行列の分析
    print("\n" + "="*60)
    print("遷移行列分析: v2値 a で遷移した後の残基構造")
    print("="*60)

    for M in [2, 3, 4]:
        print(f"\nM={M}:")
        for a in range(1, M+1):
            # v2=a の遷移: n -> (3n+1)/2^a
            # n mod 2^a が特定の値でなければならない
            # 遷移後の値 mod 2^k
            for k in range(1, 6):
                mod_k = 2**k
                mod_ak = 2**(a+k)
                transitions = {}
                for r in range(1, mod_ak, 2):
                    if v2(3*r+1) == a:
                        next_val = (3*r+1) >> a
                        key = r % mod_k
                        val = next_val % mod_k
                        if key not in transitions:
                            transitions[key] = set()
                        transitions[key].add(val)
                if k <= 3:
                    trans_str = {k_: sorted(v_) for k_, v_ in sorted(transitions.items())}
                    print(f"  a={a}, mod 2^{k}: {trans_str}")

    # 禁止語の和の分析
    print("\n" + "="*60)
    print("禁止語と和 S の関係")
    print("="*60)

    for M in range(2, 6):
        print(f"\nM={M}:")
        for L in range(1, min(2*M+3, 10)):
            total = M**L
            if total > 100000:
                break

            forbidden_by_S = defaultdict(int)
            total_by_S = defaultdict(int)

            for word in itertools.product(range(1, M+1), repeat=L):
                S = sum(word)
                total_by_S[S] += 1
                if not check_word_realizable_exact(word):
                    forbidden_by_S[S] += 1

            if forbidden_by_S:
                print(f"  L={L}:")
                for S in sorted(total_by_S.keys()):
                    f = forbidden_by_S.get(S, 0)
                    t = total_by_S[S]
                    if t > 0:
                        rate = f/t
                        if f > 0:
                            print(f"    S={S}: {f}/{t} forbidden ({rate:.4f})")

    # 理論的導出の試み
    print("\n" + "="*60)
    print("L_0(M) ≈ 2M-2 の導出試案")
    print("="*60)

    print("""
仮説: L_0(M) は以下の条件で決まる最大の L:
  「長さ L、アルファベット {1,...,M} の語で、
   mod 2^S (S=sum) の制約が矛盾するものが存在する」

[議論]
1. 最も制約が厳しい語は S が最小のもの: 全て a_i = 1、S = L
2. S = L のとき、n mod 2^L の空間は 2^{L-1} 個の奇数残基
3. 各 v2=1 の制約は残基を 1/2 に絞る（概算）
4. L ステップで残基数 ≈ 2^{L-1} / 2^L → 0（厳しすぎ）

実際にはもっと緩い: v2=1 は n ≡ 3 (mod 4) を要求し、
遷移後の n' = (3n+1)/2 の分布は一様ではない。

[精密版]
v2=a の遷移は mod 2^a で 1 つの残基クラスを選ぶ。
語 (a_1,...,a_L) の制約は合計 S = sum(a_i) ビット。
n の自由度は S-1 ビット（奇数制約）。
制約のビット数 ≈ S（各 a_i が a_i ビットの制約）。

自由度 ≈ S - 1、制約 ≈ S → ギリギリ。
禁止語が存在するのは、制約が「偶然」矛盾するケース。

L_0(M) は、M^L 個の語の中に禁止語が1つでも存在する最大の L。
禁止語の割合 ≈ C / 2^{f(L,M)} (指数減少)
禁止語の数 ≈ M^L * C / 2^{f(L,M)}

これが 1 を下回る L が L_0(M) + 1:
M^L * C / 2^{f(L,M)} ≈ 1
""")

    # 結果の保存
    result = {
        "title": "禁止語閾値 L_0(M) の理論的導出",
        "L0_table": {str(k): v for k, v in L0_table.items()},
        "detailed_results": {str(k): v for k, v in all_details.items()}
    }

    with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v2.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print("\n結果を保存しました")


if __name__ == "__main__":
    main()
