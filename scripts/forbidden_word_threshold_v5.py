#!/usr/bin/env python3
"""
探索187v5: 禁止語閾値 L_0(M) -- 超高速版
check_word を大幅に高速化: mod 2^S 全探索の代わりに枝刈り付き再帰
"""
import sys
import json
import time
from collections import defaultdict

print("START", flush=True)

def v2(n):
    if n == 0: return 999
    return (n & -n).bit_length() - 1

def check_word_fast(word):
    """高速版: 逐次的に有効な残基集合を追跡

    ステップ i で、「現在の奇数が mod 2^{残りビット} でどの値か」を追跡。
    各ステップで v2=a_i の条件でフィルタ。
    """
    L = len(word)
    if L == 0:
        return True

    # 初期: mod 2^{a_1} で v2(3n+1)=a_1 を満たす n の残基集合
    a1 = word[0]
    mod1 = 1 << a1

    # ステップ1: n mod 2^{a_1} で v2(3n+1) == a_1 となる残基
    current_residues = set()
    for r in range(1, mod1, 2):
        if v2(3*r + 1) == a1:
            current_residues.add(r)

    if not current_residues:
        return False

    # 以降のステップ: 各残基を遷移させて次の mod で条件を確認
    cumulative_bits = a1

    for step in range(1, L):
        a = word[step]
        # 現在の残基は mod 2^{cumulative_bits} での有効残基
        # 次の a ビット分だけ拡張が必要
        new_bits = cumulative_bits + a
        new_mod = 1 << min(new_bits, 24)  # 安全上限
        old_mod = 1 << min(cumulative_bits, 24)

        # 前の残基を拡張: 各残基に対し、mod new_mod の候補を生成
        # ただし old_mod < new_mod の場合のみ拡張
        if new_bits > 24:
            # ビット数が大きすぎる場合、拡張せずに近似判定
            # 現在の残基集合が空でなければ実現可能と見なす
            # (これは近似だが、S > 24 の場合は禁止語がほぼ存在しない)
            new_residues = set()
            for r_prev in current_residues:
                # 遷移: m = (3*r_prev + 1) >> word[step-1] ... ではない
                # 正しくは: current_residues は「ステップ step の開始時の奇数の残基」
                # ではなく、最初の n の残基
                #
                # 実は逐次的にやると、n mod 2^{cumulative_bits} から
                # step 番目の奇数 m_step を計算し、v2(3*m_step+1) を確認する必要がある
                #
                # 直接シミュレーション
                pass
            break

        ext_mod = 1 << new_bits
        new_residues = set()

        for r_old in current_residues:
            # r_old mod old_mod を ext_mod に拡張
            for ext in range(r_old, ext_mod, old_mod):
                if ext % 2 == 0:
                    continue
                # ext は n mod ext_mod の候補
                # step 番目の奇数を計算
                m = ext
                ok = True
                for i in range(step + 1):
                    ai = word[i]
                    val = 3 * m + 1
                    vi = v2(val)
                    if i < step:
                        m = val >> ai
                    else:
                        # ステップ step での判定
                        if vi != ai:
                            ok = False
                        break
                if ok:
                    new_residues.add(ext)

        current_residues = new_residues
        cumulative_bits = new_bits

        if not current_residues:
            return False

    return len(current_residues) > 0


def check_word_direct(word, max_bits=20):
    """直接法: n mod 2^{min(S, max_bits)} の全奇数を試す"""
    S = sum(word)
    bits = min(S, max_bits)
    mod = 1 << bits

    for n in range(1, mod, 2):
        m = n
        ok = True
        for a in word:
            val = 3 * m + 1
            if v2(val) != a:
                ok = False
                break
            m = val >> a
        if ok:
            return True
    return False


def compute_L0_direct(M, max_L=25, max_total=50000, max_bits=18):
    """直接法で L_0 計算"""
    L0 = 0
    results = []
    consec = 0

    for L in range(1, max_L + 1):
        total = M ** L
        if total > max_total:
            print(f"  L={L}: {total} > {max_total}, skip", flush=True)
            break

        t0 = time.time()
        nf = 0
        exs = []

        # 語の生成（再帰）
        def scan(prefix, depth):
            nonlocal nf
            if depth == L:
                if not check_word_direct(prefix, max_bits):
                    nf += 1
                    if nf <= 3:
                        exs.append(list(prefix))
                return
            for a in range(1, M+1):
                scan(prefix + (a,), depth+1)

        scan((), 0)

        el = time.time() - t0
        frac = nf / total if total else 0
        print(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]", flush=True)
        if exs:
            print(f"    ex: {exs}", flush=True)

        results.append({"L": L, "total": total, "forbidden": nf, "frac": frac, "ex": exs})

        if nf > 0:
            L0 = L
            consec = 0
        else:
            consec += 1
            if consec >= 2 and L > max(2*M, 4):
                print(f"  -> stop", flush=True)
                break

    return L0, results


# Main
print("="*60, flush=True)
print("探索187: 禁止語閾値 L_0(M)", flush=True)
print("="*60, flush=True)

t_total = time.time()
L0_tab = {}
all_res = {}

for M in range(1, 8):
    print(f"\n--- M={M} ---", flush=True)
    if M <= 3:
        ml, mt, mb = 3*M+4, 80000, 20
    elif M <= 5:
        ml, mt, mb = 2*M+4, 40000, 18
    else:
        ml, mt, mb = 2*M+2, 20000, 16

    L0, res = compute_L0_direct(M, ml, mt, mb)
    L0_tab[M] = L0
    all_res[M] = res
    print(f"  => L_0({M}) = {L0}", flush=True)

# Summary
print(f"\n{'M':>3} | {'L0':>4} | {'2M-2':>5} | {'2M-1':>5}", flush=True)
print("-"*30, flush=True)
for M in sorted(L0_tab.keys()):
    print(f"{M:>3} | {L0_tab[M]:>4} | {2*M-2:>5} | {2*M-1:>5}", flush=True)

# Check specific word patterns
print("\n--- Specific word patterns ---", flush=True)
print("All-ones (1,1,...,1):", flush=True)
for L in range(1, 22):
    w = tuple([1]*L)
    r = check_word_direct(w, 22)
    print(f"  L={L}: {'OK' if r else 'FORBIDDEN'}", flush=True)

print("\nWord (2,2,...,2):", flush=True)
for L in range(1, 12):
    w = tuple([2]*L)
    r = check_word_direct(w, 22)
    print(f"  L={L}: {'OK' if r else 'FORBIDDEN'}", flush=True)

print("\nWord (1,2,1,2,...):", flush=True)
for L in range(2, 14, 2):
    w = tuple([1,2]*(L//2))
    r = check_word_direct(w, 22)
    print(f"  L={L}: {'OK' if r else 'FORBIDDEN'}", flush=True)

# Forbidden word sum analysis
print("\n--- Forbidden word sum analysis ---", flush=True)
for M in [2, 3]:
    print(f"\nM={M}:", flush=True)
    L0 = L0_tab.get(M, 0)
    for L in range(1, min(L0+3, 10)):
        if M**L > 50000: break
        by_S = defaultdict(lambda: [0, 0])
        def scan_sum(prefix, depth):
            if depth == L:
                S = sum(prefix)
                by_S[S][1] += 1
                if not check_word_direct(prefix, 20):
                    by_S[S][0] += 1
                return
            for a in range(1, M+1):
                scan_sum(prefix + (a,), depth+1)
        scan_sum((), 0)
        has_forb = False
        for S in sorted(by_S.keys()):
            f, t = by_S[S]
            if f > 0:
                has_forb = True
                print(f"  L={L}, S={S}: {f}/{t} forbidden ({f/t:.4f})", flush=True)
        if not has_forb:
            print(f"  L={L}: no forbidden words", flush=True)

# v2 density
print("\n--- v2=a density ---", flush=True)
for a in range(1, 8):
    mod = 1 << (a+1)
    cnt = sum(1 for r in range(1, mod, 2) if v2(3*r+1) == a)
    to = mod >> 1
    print(f"  v2={a}: {cnt}/{to} = {cnt/to:.6f} (theory: {1/(1<<a):.6f})", flush=True)

# Saturation
print("\n--- mod 2^k saturation ---", flush=True)
for M in [2, 3, 4]:
    print(f"M={M}:", flush=True)
    for k in range(1, 2*M+3):
        mod = 1 << k
        srcs = set()
        tgts = set()
        for r in range(1, mod, 2):
            val = 3*r+1
            a = v2(val)
            if 1 <= a <= M:
                srcs.add(r)
                tgts.add((val >> a) % mod)
        to = mod >> 1
        print(f"  k={k}: src={len(srcs)}/{to} tgt={len(tgts)}/{to}", flush=True)

print(f"\nTotal time: {time.time()-t_total:.1f}s", flush=True)

# Save
output = {
    "title": "禁止語閾値L_0(M)の理論的導出",
    "L0_table": {str(k): v for k, v in L0_tab.items()},
    "comparison": {str(M): {"L0": L0_tab[M], "2M-2": 2*M-2} for M in sorted(L0_tab.keys())},
    "detailed": {str(k): v for k, v in all_res.items()},
}
with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v3.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
print("Saved.", flush=True)
