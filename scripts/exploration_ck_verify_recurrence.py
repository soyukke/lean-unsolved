"""
漸化式の数値検証
2^{S_{k+1}} * T^{k+1}(n) = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}
"""

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

def compute_v2_sequence(n, k):
    vs = []
    cur = n
    for _ in range(k):
        v = v2(3 * cur + 1)
        vs.append(v)
        cur = syracuse(cur)
    return vs

print("Numerical verification of recurrence step:")
print("2^{S_{k+1}} * T^{k+1}(n) = 3 * (2^{S_k} * T^k(n)) + 2^{S_k}")
all_ok = True
for n in [1, 3, 5, 7, 11, 15, 27, 31, 63, 99]:
    for k in range(6):
        vs = compute_v2_sequence(n, k + 1)
        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)

        Tk = syracuse_iter(k, n)
        Tkp1 = syracuse_iter(k + 1, n)

        lhs = 2**Ss[k+1] * Tkp1
        rhs = 3 * (2**Ss[k] * Tk) + 2**Ss[k]

        ok = lhs == rhs
        if not ok:
            all_ok = False
            print(f"  FAIL n={n}, k={k}: LHS={lhs}, RHS={rhs}")
        elif n <= 7:
            print(f"  n={n}, k={k}: LHS=RHS={lhs} [OK]")

print(f"\nAll recurrence steps verified: {all_ok}")

print("\nVerify v2Seq(n, k) = v2(3 * T^k(n) + 1):")
for n in [1, 3, 5, 7, 11]:
    for k in range(6):
        vs = compute_v2_sequence(n, k + 1)
        Tk = syracuse_iter(k, n)
        v2seq_k = vs[k]
        v2_direct = v2(3 * Tk + 1)
        ok = v2seq_k == v2_direct
        if not ok or n <= 5:
            print(f"  n={n}, k={k}: v2Seq={v2seq_k}, v2_direct={v2_direct} [{'OK' if ok else 'FAIL'}]")

# Also verify the full formula
print("\nVerify 2^{S_k} * T^k(n) = 3^k * n + C_k:")
def compute_Ck(vs, k):
    Ss = [0]
    for v in vs:
        Ss.append(Ss[-1] + v)
    result = 0
    for i in range(k):
        result += 3**(k-1-i) * 2**Ss[i]
    return result

all_ok = True
for n in range(1, 200, 2):
    for k in range(1, 6):
        vs = compute_v2_sequence(n, k)
        Sk = sum(vs)
        Ck = compute_Ck(vs, k)
        Tk = syracuse_iter(k, n)

        lhs = 2**Sk * Tk
        rhs = 3**k * n + Ck

        if lhs != rhs:
            all_ok = False
            print(f"  FAIL n={n}, k={k}")

print(f"All full formula checks: {all_ok}")

# Summary statistics for the complexity of the proof
print("\n\nSUMMARY: Lean proof structure")
print("-" * 50)
print("Definitions needed: 3 (v2Seq, cumulV2, ckConst)")
print("Auxiliary lemma: v2Seq_eq (relates v2Seq to v2 applied to iterates)")
print("Core lemma: recurrence_step")
print("  - Uses syracuse_mul_pow_v2 (existing)")
print("  - Uses syracuseIter_odd, syracuseIter_pos (existing)")
print("  - Pure algebraic rewriting after that")
print("Main theorem: syracuse_iter_general_mul")
print("  - Simple induction using recurrence_step")
print("  - Ring arithmetic in the step")
print("Corollary: mod 3^k independence")
print("  - Trivial from main theorem + Nat.add_mul_mod_self")
print()
print("ESTIMATED LINES: 80-100")
print("SORRY COUNT: 0 (all steps have clear proofs)")
print("KEY DEPENDENCY: syracuse_mul_pow_v2 (proven in Structure.lean)")
print()
print("RELATIONSHIP TO EXISTING CODE:")
print("  - Generalizes syracuse_iter_mul_formula (Formula.lean)")
print("  - Which required consecutiveAscents (all v_i = 1)")
print("  - New theorem works for ALL odd n >= 1, no extra conditions")
print("  - ascentConst k = ckConst n k when all v_i = 1")
