"""
定理2(c) の反例精査: v2(3n+1) ≡ 2*(n mod 3) (mod 6) で v3(T(n)-1) < 2 のケース
"""

def v2(n):
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def v3(n):
    if n == 0:
        return 0
    if n < 0:
        n = -n
    c = 0
    while n % 3 == 0:
        n //= 3
        c += 1
    return c

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

N_MAX = 500000
exceptions = []

for n in range(1, N_MAX+1, 2):
    nmod3 = n % 3
    val = 3*n+1
    v = v2(val)
    t = val >> v
    target_v2mod6 = (2 * nmod3) % 6

    if v % 6 == target_v2mod6:
        v3_val = v3(t - 1) if t > 1 else -1
        if v3_val < 2:
            exceptions.append((n, nmod3, v, v % 6, t, v3_val, t % 9))

print(f"Total exceptions: {len(exceptions)}")
for (n, nmod3, v, v6, t, v3_val, t9) in exceptions[:20]:
    print(f"  n={n}, n%3={nmod3}, v2={v}, v2%6={v6}, T(n)={t}, v3(T-1)={v3_val}, T%9={t9}")

# Check: are these n=1 (T(1)=1) cases?
print("\nCheck T(n) values:")
for (n, nmod3, v, v6, t, v3_val, t9) in exceptions:
    print(f"  n={n}: T(n)={t}")
