#!/usr/bin/env python3
"""
探索187v4: 禁止語閾値 L_0(M) 高速計算
flush付き出力
"""

import sys
import json
import time
from collections import defaultdict

def v2(n):
    if n == 0: return 999
    return (n & -n).bit_length() - 1

def check_word(word):
    """word実現可能か"""
    S = sum(word)
    bits = min(S, 22)
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

def gen_words(M, L):
    """M^L語を生成"""
    if L == 0:
        yield ()
        return
    for a in range(1, M+1):
        for rest in gen_words(M, L-1):
            yield (a,) + rest

def p(msg):
    print(msg, flush=True)

def compute_L0(M, max_L=25):
    L0 = 0
    results = []
    consec = 0
    for L in range(1, max_L+1):
        total = M**L
        if total > 150000:
            p(f"  L={L}: {total} > 150000, skip")
            break
        t0 = time.time()
        nf = 0
        exs = []
        for w in gen_words(M, L):
            if not check_word(w):
                nf += 1
                if nf <= 3:
                    exs.append(list(w))
        el = time.time() - t0
        frac = nf/total if total else 0
        p(f"  L={L}: {nf}/{total} forbidden ({frac:.6f}) [{el:.1f}s]")
        if exs:
            p(f"    ex: {exs}")
        results.append({"L":L, "total":total, "forbidden":nf, "frac":frac, "ex":exs})
        if nf > 0:
            L0 = L
            consec = 0
        else:
            consec += 1
            if consec >= 3 and L > 2*M:
                p(f"  -> stop (3 consecutive zeros)")
                break
    return L0, results

p("="*60)
p("探索187: 禁止語閾値 L_0(M)")
p("="*60)

L0_tab = {}
all_res = {}

for M in range(1, 9):
    p(f"\n--- M={M} ---")
    ml = 3*M+3 if M <= 4 else (2*M+4 if M <= 6 else 2*M+2)
    L0, res = compute_L0(M, ml)
    L0_tab[M] = L0
    all_res[M] = res
    p(f"  => L_0({M}) = {L0}")

p("\n" + "="*60)
p("Summary table")
p("="*60)
import math
p(f"{'M':>3} | {'L0':>4} | {'2M-2':>5} | {'2M-1':>5} | {'2M':>4}")
p("-"*35)
for M in sorted(L0_tab.keys()):
    L0 = L0_tab[M]
    p(f"{M:>3} | {L0:>4} | {2*M-2:>5} | {2*M-1:>5} | {2*M:>4}")

# 線形フィット
Ms = [m for m in sorted(L0_tab.keys()) if L0_tab[m] > 0]
L0s = [L0_tab[m] for m in Ms]
if len(Ms) >= 3:
    n = len(Ms)
    sx = sum(Ms); sy = sum(L0s)
    sxy = sum(m*l for m,l in zip(Ms,L0s))
    sx2 = sum(m*m for m in Ms)
    a = (n*sxy - sx*sy)/(n*sx2 - sx*sx)
    b = (sy - a*sx)/n
    p(f"\nLinear fit: L_0(M) = {a:.4f}*M + ({b:.4f})")
    for m,l in zip(Ms,L0s):
        p(f"  M={m}: L0={l}, pred={a*m+b:.2f}")

# Structure analysis for small M
p("\n" + "="*60)
p("Forbidden word structure")
p("="*60)
for M in [2, 3]:
    L0 = L0_tab.get(M, 0)
    if L0 == 0: continue
    for L in [L0-1, L0, L0+1]:
        if L < 1 or M**L > 100000: continue
        p(f"\nM={M}, L={L}:")
        by_sum = defaultdict(lambda: [0,0])
        for w in gen_words(M, L):
            S = sum(w)
            by_sum[S][1] += 1
            if not check_word(w):
                by_sum[S][0] += 1
        for S in sorted(by_sum.keys()):
            f, t = by_sum[S]
            if f > 0:
                p(f"  S={S}: {f}/{t} forbidden ({f/t:.4f})")

# Saturation analysis
p("\n" + "="*60)
p("mod 2^k saturation")
p("="*60)
for M in [2, 3, 4, 5]:
    p(f"\nM={M}:")
    for k in range(1, min(2*M+4, 12)):
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
        p(f"  k={k}: src={len(srcs)}/{to} ({len(srcs)/to:.3f}), "
          f"tgt={len(tgts)}/{to} ({len(tgts)/to:.3f})")

# v2=a density
p("\n" + "="*60)
p("v2=a density per a")
p("="*60)
for a in range(1, 10):
    mod = 1 << (a+1)
    cnt = sum(1 for r in range(1, mod, 2) if v2(3*r+1) == a)
    to = mod >> 1
    p(f"  a={a}: {cnt}/{to} = {cnt/to:.6f}, expected 1/2^a = {1/(1<<a):.6f}")

# 3^{-1} mod 2^k
p("\n" + "="*60)
p("3^{-1} mod 2^k and v2 conditions")
p("="*60)
for a in range(1, 9):
    mod_a = 1 << a
    inv3 = pow(3, -1, mod_a)
    # 3n+1 ≡ 0 (mod 2^a) => n ≡ -inv3 ≡ mod_a - inv3
    n_cond = (mod_a - inv3) % mod_a
    p(f"  a={a}: inv(3) mod 2^{a} = {inv3}, v2(3n+1)>=a iff n ≡ {n_cond} (mod {mod_a})")

# Theoretical analysis
p("\n" + "="*60)
p("Theoretical analysis: why L_0(M) ~ 2M-2?")
p("="*60)

p("""
Key insight: For word w = (a_1,...,a_L) with S = sum(a_i):
- Realizability is determined by n mod 2^S
- There are 2^{S-1} odd residues mod 2^S
- Each v2=a_i constraint restricts to a specific residue class mod 2^{a_i}
- The constraints are NOT independent: they form a chain

The chain structure:
  n mod 2^{a_1} -> determines v2 step 1
  m_1 = (3n+1)/2^{a_1} mod 2^{a_2} -> determines v2 step 2
  ...

This is equivalent to n mod 2^S satisfying L simultaneous conditions.
The number of solutions = 2^{S-1} * prod(P_i) where P_i ~ 1/2^{a_i}
= 2^{S-1} / 2^S = 1/2

So on average each word has ~1/2 solution mod 2^S.
Forbidden words are those with 0 solutions.

For fixed S, the number of words is C(S-1, L-1) (compositions).
The fraction of forbidden words depends on the arithmetic structure.

When M is small (a_i <= M), the maximum S for length L is L*M.
The minimum S is L.

Critical observation: forbidden words tend to have S close to L (i.e., a_i mostly 1).
For S = L (all a_i = 1): the constraint is n mod 2^L.
The v2=1 condition requires n ≡ 1 (mod 4) [since 3n+1 ≡ 4 (mod 8) iff n ≡ 1 (mod 4)].
But the transition n -> (3n+1)/2 mod 2^{L-1} may or may not be consistent.

The "period" of the v2=1 chain:
  n ≡ 1 (mod 4): v2(3n+1) = 2, not 1!
  n ≡ 3 (mod 4): v2(3n+1) = 1.

So v2=1 requires n ≡ 3 (mod 4).
Then m = (3n+1)/2 = (3*3+1)/2 = 5 if n=3, or (3*7+1)/2 = 11 if n=7.
For m ≡ 3 (mod 4) to get v2=1 again: need to check mod 8.

The chain (1,1,1,...) of length L requires n mod 2^L to be in a specific class.
The number of valid n depends on L.

For the word (1,1,...,1) of length L:
  Need n ≡ 3 (mod 4), then (3n+1)/2 ≡ 3 (mod 4), etc.
  This is a system of L congruences mod 2^L.

Let's check: does (1,1,...,1) eventually become forbidden?
""")

# Check (1,1,...,1) for various L
p("Checking all-ones word (1,1,...,1):")
for L in range(1, 25):
    w = tuple([1]*L)
    result = check_word(w)
    p(f"  L={L}: {'realizable' if result else 'FORBIDDEN'}")

# Check high-value words
p("\nChecking all-M words (M,M,...,M) for M=2:")
for L in range(1, 15):
    w = tuple([2]*L)
    result = check_word(w)
    p(f"  L={L}: {'realizable' if result else 'FORBIDDEN'}")

# Save results
output = {
    "title": "禁止語閾値 L_0(M) の理論的導出",
    "L0_table": {str(k): v for k, v in L0_tab.items()},
    "formula_comparison": {
        str(M): {"L0": L0_tab[M], "2M-2": 2*M-2, "2M-1": 2*M-1, "2M": 2*M}
        for M in sorted(L0_tab.keys())
    },
    "detailed_results": {str(k): v for k, v in all_res.items()},
}

with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v3.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
p("\nSaved to results/forbidden_word_threshold_v3.json")
