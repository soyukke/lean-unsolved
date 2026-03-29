#!/usr/bin/env python3
"""超軽量: M=1,2 だけまず計算"""
import sys, time

def v2(n):
    if n == 0: return 999
    return (n & -n).bit_length() - 1

def check(word, max_bits=18):
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

sys.stdout.write("test: v2(12)=" + str(v2(12)) + "\n")
sys.stdout.flush()

# M=1: alphabet {1}
sys.stdout.write("\nM=1:\n")
sys.stdout.flush()
for L in range(1, 15):
    w = (1,)*L
    r = check(w, 20)
    sys.stdout.write(f"  L={L}: (1,...,1) -> {'OK' if r else 'FORBIDDEN'}\n")
    sys.stdout.flush()

# M=2: small words
sys.stdout.write("\nM=2, checking small L:\n")
sys.stdout.flush()
for L in range(1, 8):
    total = 2**L
    nf = 0
    t0 = time.time()
    # Generate all words over {1,2} of length L
    for mask in range(total):
        word = tuple(((mask >> i) & 1) + 1 for i in range(L))
        if not check(word, 18):
            nf += 1
    el = time.time() - t0
    sys.stdout.write(f"  L={L}: {nf}/{total} forbidden [{el:.2f}s]\n")
    sys.stdout.flush()

sys.stdout.write("\nDone\n")
sys.stdout.flush()
