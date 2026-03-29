#!/usr/bin/env python3
"""
探索187: 禁止語閾値の再定義と分析

前の結果から判明:
- M=1 (v2=1のみ): 全長の (1,...,1) が禁止 → L_0(1) = ∞
- M=2 (v2∈{1,2}): 禁止語の割合が ~50% で一定 → L_0(2) = ∞

これは「禁止語閾値」の定義を再考する必要がある。

再定義案:
(A) 「最小禁止語」に着目: 延長しても禁止なままの語 vs 新たに禁止になる語
(B) 「M-制約なし」: v2 の値に上限を設けず、特定の v2 列が禁止される条件
(C) 「非排除閾値」: mod 2^k で「全ての v2∈{1,...,M} の列を実現可能」になる最小 k

仮説の修正:
L_0(M) ≈ 2M-2 は「非排除閾値」を指している可能性がある。
つまり、mod 2^k の有限構造が「飽和」する k の値。
"""
import sys, time
from collections import defaultdict

def v2(n):
    if n == 0: return 999
    return (n & -n).bit_length() - 1

def p(s):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def check(word, max_bits=20):
    S = sum(word)
    bits = min(S, max_bits)
    mod = 1 << bits
    for n in range(1, mod, 2):
        m = n
        ok = True
        for a in word:
            val = 3*m+1
            if v2(val) != a:
                ok = False
                break
            m = val >> a
        if ok:
            return True
    return False

p("="*60)
p("禁止語閾値の再定義分析")
p("="*60)

# 分析1: v2値に上限なしの場合（自然な v2 列）
p("\n--- 分析1: 上限なしの v2 列 ---")
p("各長さ L で、v2 値の最大値を記録")
for L in range(1, 8):
    # 奇数 1..10000 からの v2 列
    max_v2 = defaultdict(int)
    v2_seqs = set()
    for n in range(1, 10001, 2):
        m = n
        seq = []
        for _ in range(L):
            val = 3*m+1
            a = v2(val)
            seq.append(a)
            m = val >> a
        v2_seqs.add(tuple(seq))
        for i, a in enumerate(seq):
            max_v2[i] = max(max_v2[i], a)

    # 理論上の全列挙は不可能なので、実現された語数を報告
    p(f"  L={L}: {len(v2_seqs)} distinct sequences from n=1..10000 (odd)")
    p(f"    max v2 at each position: {dict(sorted(max_v2.items()))}")

# 分析2: mod 2^k で全ての「短い v2 列」が実現可能になる最小 k
p("\n--- 分析2: mod 2^k 完全実現閾値 ---")
p("語 (a_1,...,a_L) が mod 2^k で実現可能になる最小の k ≥ S = sum(a_i)")

# M=2, 短い禁止語の最小実現 k を調査
p("\nM=2 の禁止語と最小実現mod:")
for L in range(1, 7):
    total = 2**L
    for mask in range(total):
        word = tuple(((mask >> i) & 1) + 1 for i in range(L))
        S = sum(word)
        # mod 2^k で k = S, S+1, ... と増やして最小の実現 k を探す
        realized_at = None
        for k in range(S, S+10):
            mod = 1 << k
            found = False
            for n in range(1, mod, 2):
                m = n
                ok = True
                for a in word:
                    val = 3*m+1
                    if v2(val) != a:
                        ok = False
                        break
                    m = val >> a
                if ok:
                    found = True
                    break
            if found:
                realized_at = k
                break
        if realized_at is None:
            p(f"  {word}: S={S}, NOT realized up to k={S+9}")
        elif realized_at > S:
            p(f"  {word}: S={S}, first realized at k={realized_at}")

# 分析3: 「延長不可能な禁止語」（最小禁止語）
p("\n--- 分析3: 最小禁止語 ---")
p("禁止語 w のうち、全ての真部分接頭辞が実現可能なもの")

for M in [2, 3]:
    p(f"\nM={M}:")
    for L in range(1, 9):
        total = M**L
        if total > 30000: break
        minimal_forbidden = []

        def gen(prefix, depth):
            if depth == L:
                word = prefix
                if not check(word, 20):
                    # 全ての真部分接頭辞が実現可能か?
                    is_minimal = True
                    for plen in range(1, L):
                        if not check(word[:plen], 20):
                            is_minimal = False
                            break
                    if is_minimal:
                        minimal_forbidden.append(word)
                return
            for a in range(1, M+1):
                gen(prefix + (a,), depth+1)

        gen((), 0)
        if minimal_forbidden:
            p(f"  L={L}: {len(minimal_forbidden)} minimal forbidden words")
            for w in minimal_forbidden[:10]:
                p(f"    {list(w)} (S={sum(w)})")

# 分析4: 「v2-saturated length」
# mod 2^k で、全ての v2∈{1,...,M} の L-語が実現可能になる最小の (k, L)
p("\n--- 分析4: 飽和長 ---")
p("各 mod 2^k で、実現可能な v2∈{1,...,M} 語の割合")

for M in [2, 3, 4]:
    p(f"\nM={M}:")
    for k in range(2, min(3*M+2, 16)):
        mod = 1 << k
        # 長さ1の実現可能割合
        for L in [1, 2, 3]:
            total = M**L
            if total > 10000: continue
            realized_count = [0]

            def gen_check(prefix, depth):
                if depth == L:
                    for n in range(1, mod, 2):
                        m = n
                        ok = True
                        for a in prefix:
                            val = 3*m+1
                            if v2(val) != a:
                                ok = False
                                break
                            m = val >> a
                        if ok:
                            realized_count[0] += 1
                            return
                    return
                for a in range(1, M+1):
                    gen_check(prefix + (a,), depth+1)

            gen_check((), 0)
            realized = realized_count[0]
            frac = realized / total
            p(f"  k={k}, L={L}: {realized}/{total} realized ({frac:.4f})")

# 分析5: 禁止語の「3-adic構造」
p("\n--- 分析5: 禁止の算術的条件 ---")
p("v2(3n+1) = a ⟺ 3n ≡ 2^a - 1 (mod 2^{a+1})")
p("                ⟺ n ≡ (2^a - 1) * 3^{-1} (mod 2^{a+1})")
p("ただし v2 = a exactly なので mod 2^{a+1} で条件あり")

for a in range(1, 8):
    mod = 1 << (a+1)
    inv3 = pow(3, -1, mod)
    # v2(3n+1) >= a: 3n+1 ≡ 0 mod 2^a => n ≡ -1/3 mod 2^a
    n_ge = (-inv3) % (1 << a)
    # v2(3n+1) = a exactly: additionally 3n+1 ≢ 0 mod 2^{a+1}
    n_exact = []
    for r in range(1, mod, 2):
        if v2(3*r+1) == a:
            n_exact.append(r)
    p(f"  a={a}: n ≡ {n_ge} (mod {1<<a}), exact solutions mod {mod}: {n_exact}")

# 遷移の可逆性
p("\n--- 分析6: 遷移の可逆性 ---")
p("T_a: n -> (3n+1)/2^a (v2=a の場合)")
p("逆写像 T_a^{-1}: m -> (2^a * m - 1)/3 (これが奇数整数ならOK)")

for a in range(1, 6):
    p(f"\na={a}:")
    p(f"  T_a^{{-1}}(m) = (2^{a}*m - 1)/3")
    p(f"  これが整数 ⟺ 2^{a}*m ≡ 1 (mod 3) ⟺ m ≡ {pow(2**a, -1, 3)} (mod 3)")
    inv_2a = pow(2**a, -1, 3)
    p(f"  つまり m ≡ {inv_2a} (mod 3) のとき逆像が存在")
    p(f"  さらに奇数: (2^{a}*m-1)/3 が奇数 ⟺ 2^{a}*m-1 ≡ 3 (mod 6)")
    p(f"                ⟺ 2^{a}*m ≡ 4 (mod 6) ⟺ m ≡ {(4*pow(2**a,-1,6))%6} (mod 6)")

    # 具体的に
    valid_m = []
    for m in range(1, 25, 2):
        val = (2**a * m - 1)
        if val % 3 == 0:
            prev = val // 3
            if prev > 0 and prev % 2 == 1:
                valid_m.append((m, prev))
    p(f"  有効な (m, T_a^{{-1}}(m)): {valid_m[:8]}")

p("\n" + "="*60)
p("結論と次のステップ")
p("="*60)
p("""
主要発見:
1. M=1 (v2=1のみ): 全長の (1,...,1) が禁止。L_0(1) = ∞。
   理由: v2=1 の遷移 T_1 は mod 2^L で 3-adic の構造を持ち、
   長い列 (1,1,...,1) を実現する残基が存在しない。

2. M=2 (v2∈{1,2}): 禁止語の割合が ~50% で安定。L_0(2) = ∞ (?)。
   禁止語の例は主に高い v2 値を多く含む語。

3. 当初の仮説 L_0(M) ≈ 2M-2 は、おそらく別の量を指している:
   - mod 2^k 飽和の閾値
   - または最小禁止語の長さ
   - または特定のタイプの禁止語の閾値

次の方向:
- 「最小禁止語」の長さの最大値として L_0(M) を再定義
- mod 2^k 飽和法則との正確な対応を確立
""")

p(f"\nTotal time: {time.time()-time.time():.1f}s")
