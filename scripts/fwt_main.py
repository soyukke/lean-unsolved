#!/usr/bin/env python3
"""
探索187: 禁止語閾値 L_0(M) 本計算
段階的に M と L を増やす
"""
import sys, time, json
from collections import defaultdict

def v2(n):
    if n == 0: return 999
    return (n & -n).bit_length() - 1

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

def p(s):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def gen_words_iter(M, L):
    """iterative word generation"""
    if L == 0:
        yield ()
        return
    stack = [(a,) for a in range(1, M+1)]
    while stack:
        prefix = stack.pop()
        if len(prefix) == L:
            yield prefix
        else:
            for a in range(1, M+1):
                stack.append(prefix + (a,))

p("="*60)
p("探索187: 禁止語閾値 L_0(M)")
p("="*60)

t_all = time.time()

# まず M=1 の分析
p("\n--- M=1 (alphabet {1}) ---")
p("Only word is (1,...,1). Always forbidden (v2=1 means n≡3 mod 4,")
p("but (3*3+1)/2=5≡1 mod 4, so v2(3*5+1)=v2(16)=4≠1).")
p("Check: n≡3 mod 4 -> 3n+1≡10 mod 12 -> v2=1, next=(3n+1)/2")
p("n=3: 10/2=5, v2(16)=4≠1. n=7: 22/2=11, v2(34)=1. OK for 2 steps.")

# Verify
for L in range(1, 22):
    r = check((1,)*L, 22)
    p(f"  L={L}: {'OK' if r else 'FORBIDDEN'}")

# M=2
p("\n--- M=2 (alphabet {1,2}) ---")
L0_tab = {}
all_res = {}

M = 2
results = []
for L in range(1, 16):
    total = M**L
    if total > 100000:
        p(f"  L={L}: {total} too many, stop")
        break
    t0 = time.time()
    nf = 0
    exs = []
    for w in gen_words_iter(M, L):
        if not check(w):
            nf += 1
            if len(exs) < 3:
                exs.append(list(w))
    el = time.time() - t0
    frac = nf/total
    p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
    if exs:
        p(f"    ex: {exs}")
    results.append({"L": L, "total": total, "forbidden": nf, "frac": frac})
    if nf > 0:
        L0_tab[2] = L
all_res[2] = results

# M=3
p("\n--- M=3 (alphabet {1,2,3}) ---")
M = 3
results = []
for L in range(1, 12):
    total = M**L
    if total > 80000:
        p(f"  L={L}: {total} too many, stop")
        break
    t0 = time.time()
    nf = 0
    exs = []
    for w in gen_words_iter(M, L):
        if not check(w):
            nf += 1
            if len(exs) < 3:
                exs.append(list(w))
    el = time.time() - t0
    frac = nf/total
    p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
    if exs:
        p(f"    ex: {exs}")
    results.append({"L": L, "total": total, "forbidden": nf, "frac": frac})
    if nf > 0:
        L0_tab[3] = L
all_res[3] = results

# M=4
p("\n--- M=4 (alphabet {1,2,3,4}) ---")
M = 4
results = []
for L in range(1, 10):
    total = M**L
    if total > 60000:
        p(f"  L={L}: {total} too many, stop")
        break
    t0 = time.time()
    nf = 0
    exs = []
    for w in gen_words_iter(M, L):
        if not check(w):
            nf += 1
            if len(exs) < 3:
                exs.append(list(w))
    el = time.time() - t0
    frac = nf/total
    p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
    if exs:
        p(f"    ex: {exs}")
    results.append({"L": L, "total": total, "forbidden": nf, "frac": frac})
    if nf > 0:
        L0_tab[4] = L
all_res[4] = results

# M=5
p("\n--- M=5 (alphabet {1,...,5}) ---")
M = 5
results = []
for L in range(1, 8):
    total = M**L
    if total > 50000:
        p(f"  L={L}: {total} too many, stop")
        break
    t0 = time.time()
    nf = 0
    exs = []
    for w in gen_words_iter(M, L):
        if not check(w):
            nf += 1
            if len(exs) < 3:
                exs.append(list(w))
    el = time.time() - t0
    frac = nf/total
    p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
    if exs:
        p(f"    ex: {exs}")
    results.append({"L": L, "total": total, "forbidden": nf, "frac": frac})
    if nf > 0:
        L0_tab[5] = L
all_res[5] = results

# M=6,7
for M in [6, 7]:
    p(f"\n--- M={M} ---")
    results = []
    for L in range(1, 7):
        total = M**L
        if total > 40000:
            p(f"  L={L}: {total} too many, stop")
            break
        t0 = time.time()
        nf = 0
        exs = []
        for w in gen_words_iter(M, L):
            if not check(w):
                nf += 1
                if len(exs) < 3:
                    exs.append(list(w))
        el = time.time() - t0
        frac = nf/total
        p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
        if exs:
            p(f"    ex: {exs}")
        results.append({"L": L, "total": total, "forbidden": nf, "frac": frac})
        if nf > 0:
            L0_tab[M] = L
    all_res[M] = results

# Summary
p("\n" + "="*60)
p("Summary")
p("="*60)
p(f"{'M':>3} | {'L_0(M)':>6} | {'2M-2':>5} | {'diff':>5}")
p("-"*30)
for M in sorted(L0_tab.keys()):
    L0 = L0_tab[M]
    diff = L0 - (2*M - 2)
    p(f"{M:>3} | {L0:>6} | {2*M-2:>5} | {diff:>5}")

# Detailed structure for M=2
p("\n" + "="*60)
p("Forbidden words by sum S (M=2)")
p("="*60)
M = 2
for L in range(1, 12):
    total = M**L
    if total > 50000: break
    by_S = defaultdict(lambda: [0, 0])
    for w in gen_words_iter(M, L):
        S = sum(w)
        by_S[S][1] += 1
        if not check(w):
            by_S[S][0] += 1
    line = f"  L={L}: "
    parts = []
    for S in sorted(by_S.keys()):
        f, t = by_S[S]
        parts.append(f"S={S}:{f}/{t}")
    p(line + ", ".join(parts))

# v2 density
p("\n--- v2=a exact density ---")
for a in range(1, 10):
    mod = 1 << (a+1)
    cnt = sum(1 for r in range(1, mod, 2) if v2(3*r+1) == a)
    to = mod >> 1
    p(f"  v2={a}: {cnt}/{to} = {cnt/to:.6f}")

# 3^{-1} mod 2^k
p("\n--- 3^{-1} mod 2^k ---")
for k in range(1, 10):
    mod = 1 << k
    inv3 = pow(3, -1, mod)
    p(f"  k={k}: 3^(-1) mod {mod} = {inv3}")

p(f"\nTotal time: {time.time()-t_all:.1f}s")

# Save
output = {
    "title": "禁止語閾値L_0(M)の理論的導出",
    "L0_table": {str(k): v for k, v in L0_tab.items()},
    "comparison": {str(M): {"L0": L0_tab.get(M, "?"), "2M-2": 2*M-2}
                   for M in range(2, 8)},
    "detailed": {str(k): v for k, v in all_res.items()},
}
with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v3.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
p("Saved to results/forbidden_word_threshold_v3.json")
