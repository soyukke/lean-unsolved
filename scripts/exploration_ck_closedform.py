"""
探索: C_k閉形式 T^k(n) mod 3^k = sum 3^{i-1} * 2^{-S_i} の形式化分析

数学的背景:
- T(n) = (3n+1) / 2^{v2(3n+1)} (Syracuse関数)
- v_i = v2(3 * T^{i-1}(n) + 1) (各ステップの2-adic付値)
- S_i = v_1 + v_2 + ... + v_i (累積付値)
- T^k(n) の閉形式: T^k(n) = (3^k * n + C_k) / 2^{S_k}
  ここで C_k = sum_{i=1}^{k} 3^{k-i} * 2^{S_k - S_i}

質問: T^k(n) mod 3^k は v2列 (v_1,...,v_k) のみに依存するか?

計算: T^k(n) = (3^k * n + C_k) / 2^{S_k}
mod 3^k: T^k(n) mod 3^k = C_k / 2^{S_k} mod 3^k  (3^k * n項が消える)
= C_k * (2^{S_k})^{-1} mod 3^k

C_k = sum_{i=1}^{k} 3^{k-i} * 2^{S_k - S_i}
mod 3^k: C_k mod 3^k = sum_{i=1}^{k} 3^{k-i} * 2^{S_k - S_i} mod 3^k
       = 2^{S_k} * sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k

したがって T^k(n) mod 3^k = sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k
(ここで 2^{-S_i} は mod 3^k での逆元)

これは v2列のみに依存する!
"""

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function"""
    m = 3 * n + 1
    return m >> v2(m)

def syracuse_iter(k, n):
    """Apply syracuse k times"""
    for _ in range(k):
        n = syracuse(n)
    return n

def compute_v2_sequence(n, k):
    """Compute v2 sequence (v_1, ..., v_k)"""
    vs = []
    cur = n
    for _ in range(k):
        v = v2(3 * cur + 1)
        vs.append(v)
        cur = syracuse(cur)
    return vs

def compute_Ck(vs, k):
    """Compute C_k = sum_{i=1}^{k} 3^{k-i} * 2^{S_k - S_i}"""
    # First compute S_i = v_1 + ... + v_i
    Ss = [0] * (k + 1)  # S_0 = 0
    for i in range(1, k + 1):
        Ss[i] = Ss[i-1] + vs[i-1]
    Sk = Ss[k]

    result = 0
    for i in range(1, k + 1):
        result += 3**(k - i) * 2**(Sk - Ss[i])
    return result

def verify_Tk_formula(n, k):
    """Verify T^k(n) = (3^k * n + C_k) / 2^{S_k}"""
    vs = compute_v2_sequence(n, k)
    Ck = compute_Ck(vs, k)
    Sk = sum(vs)

    Tk_actual = syracuse_iter(k, n)
    Tk_formula = (3**k * n + Ck) // 2**Sk

    # Check divisibility
    assert (3**k * n + Ck) % 2**Sk == 0, f"Not divisible for n={n}, k={k}"
    assert Tk_actual == Tk_formula, f"Formula mismatch for n={n}, k={k}: {Tk_actual} vs {Tk_formula}"

    return Tk_actual, vs, Ck, Sk

def verify_mod3k_independence(k, max_n=200):
    """
    Verify: T^k(n) mod 3^k depends only on v2 sequence, not on n.

    For each distinct v2 sequence, all n producing that sequence
    should give the same T^k(n) mod 3^k.
    """
    from collections import defaultdict

    mod3k = 3**k
    v2seq_to_mod = defaultdict(set)
    v2seq_to_ns = defaultdict(list)

    for n in range(1, max_n, 2):  # odd numbers only
        vs = compute_v2_sequence(n, k)
        Tk = syracuse_iter(k, n)
        mod_val = Tk % mod3k
        key = tuple(vs)
        v2seq_to_mod[key].add(mod_val)
        v2seq_to_ns[key].append(n)

    print(f"\n=== k = {k}, mod 3^{k} = {mod3k} ===")
    all_ok = True
    for seq, mods in sorted(v2seq_to_mod.items()):
        ok = len(mods) == 1
        if not ok:
            all_ok = False
        mod_list = sorted(mods)
        ns = v2seq_to_ns[seq][:5]  # show first 5 examples
        status = "OK" if ok else "FAIL"
        print(f"  v2_seq={seq}: mod values={mod_list} [{status}] (examples: {ns})")

    print(f"  Independence verified: {all_ok}")
    return all_ok

def compute_closed_form_mod3k(vs, k):
    """
    Compute T^k(n) mod 3^k from v2 sequence only.

    T^k(n) mod 3^k = C_k * inv(2^{S_k}) mod 3^k
    = sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k
    """
    mod3k = 3**k
    # S_i values
    Ss = [0] * (k + 1)
    for i in range(1, k + 1):
        Ss[i] = Ss[i-1] + vs[i-1]

    result = 0
    for i in range(1, k + 1):
        # 2^{-S_i} mod 3^k
        inv_2_Si = pow(2, -Ss[i], mod3k) if mod3k > 1 else 0
        result += 3**(k - i) * inv_2_Si

    return result % mod3k

def verify_closed_form(k, max_n=200):
    """Verify the closed form T^k(n) mod 3^k = sum 3^{k-i} * 2^{-S_i} mod 3^k"""
    mod3k = 3**k
    if mod3k <= 1:
        return True

    print(f"\n=== Closed form verification: k={k} ===")
    all_ok = True
    for n in range(1, max_n, 2):
        vs = compute_v2_sequence(n, k)
        Tk = syracuse_iter(k, n)
        actual = Tk % mod3k
        predicted = compute_closed_form_mod3k(vs, k)
        if actual != predicted:
            all_ok = False
            print(f"  FAIL n={n}: actual={actual}, predicted={predicted}, vs={vs}")

    if all_ok:
        print(f"  All {max_n//2} odd numbers verified correctly!")
    return all_ok

def analyze_k1_detail():
    """
    k=1 の場合の詳細分析
    T(n) mod 3 = 2^{-v_1} mod 3
    v_1 偶数 -> 2^{-v_1} = (2^{-1})^{v_1} = 2^{v_1} mod 3 = 1 mod 3
    v_1 奇数 -> 2^{v_1} mod 3 = 2 mod 3
    これは syracuse_mod3_eq と一致する!
    """
    print("\n=== k=1 detail analysis ===")
    print("T(n) mod 3 = 2^{-v1} mod 3")
    print("  v1 even -> 1 mod 3")
    print("  v1 odd  -> 2 mod 3")

    for n in range(1, 40, 2):
        v1 = v2(3 * n + 1)
        Tn = syracuse(n)
        mod3 = Tn % 3
        inv_val = pow(2, -v1, 3)
        print(f"  n={n:3d}: v1={v1}, T(n)={Tn:4d}, T(n)%3={mod3}, 2^(-{v1})%3={inv_val}")

def analyze_induction_structure():
    """
    帰納法の構造分析。

    k=1の基底: T(n) mod 3 = 2^{-v_1} mod 3  (syracuse_mod3_eqそのもの)

    帰納ステップ k -> k+1:
    T^{k+1}(n) = T(T^k(n))

    m := T^k(n) とおくと、
    T^{k+1}(n) mod 3^{k+1} = T(m) mod 3^{k+1}

    T(m) = (3m + 1) / 2^{v_{k+1}}
    T(m) mod 3^{k+1} = (3m + 1) * inv(2^{v_{k+1}}) mod 3^{k+1}

    3m + 1 mod 3^{k+1}: m = T^k(n) を帰納仮定から展開
    T^k(n) = 3^k * n * ... + sum 3^{k-i} * 2^{-S_i}  (modular)
    3 * T^k(n) + 1 mod 3^{k+1}:
    = 3 * (sum_{i=1}^{k} 3^{k-i} * 2^{-S_i}) + 1  mod 3^{k+1}  (3^{k+1}*n 項消える)
    = sum_{i=1}^{k} 3^{k+1-i} * 2^{-S_i} + 1  mod 3^{k+1}

    (3*T^k(n)+1) / 2^{v_{k+1}} mod 3^{k+1}:
    = (sum_{i=1}^{k} 3^{k+1-i} * 2^{-S_i} + 1) * 2^{-v_{k+1}} mod 3^{k+1}
    = sum_{i=1}^{k} 3^{k+1-i} * 2^{-S_i-v_{k+1}} + 2^{-v_{k+1}} mod 3^{k+1}
    = sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-S_{k+1} + S_k - S_i} * ...

    wait, S_{k+1} = S_k + v_{k+1}, so S_i + v_{k+1} = S_{i} + (S_{k+1} - S_k)

    = sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-(S_i + v_{k+1})} + 2^{-v_{k+1}} mod 3^{k+1}

    Note: S_i + v_{k+1} is NOT S_{i+1}. We need S_{i} based on the *new* indexing.

    Let me re-index for the (k+1) step:
    v'_j = v_j for j=1..k, v'_{k+1} = v_{k+1}
    S'_j = S_j for j=1..k, S'_{k+1} = S_k + v_{k+1}

    So the formula for T^{k+1}(n) mod 3^{k+1} should be:
    sum_{j=1}^{k+1} 3^{(k+1)-j} * 2^{-S'_j} mod 3^{k+1}

    = sum_{j=1}^{k} 3^{(k+1)-j} * 2^{-S_j} + 3^0 * 2^{-S_{k+1}} mod 3^{k+1}

    From the induction:
    = sum_{j=1}^{k} 3^{(k+1)-j} * 2^{-S_j} * 2^{-v_{k+1}} * 2^{v_{k+1}} + 2^{-S_{k+1}}

    Hmm, let me redo more carefully.

    From the computation:
    T^{k+1}(n) mod 3^{k+1}
    = (3 * T^k(n) + 1) * 2^{-v_{k+1}} mod 3^{k+1}

    By IH: T^k(n) ≡ sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} (mod 3^k)

    So T^k(n) = Q * 3^k + sum_{i=1}^{k} 3^{k-i} * 2^{-S_i}  for some Q
    (where the sum is computed mod 3^k and lifted)

    3 * T^k(n) + 1 = 3Q * 3^k + 3 * sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} + 1
                   = 3^{k+1} * Q + sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-S_i} + 1

    mod 3^{k+1}: 3 * T^k(n) + 1 ≡ sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-S_i} + 1

    T^{k+1}(n) mod 3^{k+1} = (sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-S_i} + 1) * 2^{-v_{k+1}}
                             = sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-(S_i + v_{k+1})} + 2^{-v_{k+1}}

    But S_i + v_{k+1} ≠ S_{i+1} in general (S_{i+1} = S_i + v_{i+1}).

    WAIT: actually S_i = v_1 + ... + v_i, and we want the final formula to be
    sum_{j=1}^{k+1} 3^{(k+1)-j} * 2^{-S_j}

    The j=k+1 term: 3^0 * 2^{-S_{k+1}} = 2^{-S_{k+1}} = 2^{-(S_k + v_{k+1})}

    The j=1..k terms: 3^{(k+1)-j} * 2^{-S_j}

    From induction we get:
    sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-(S_i + v_{k+1})} + 2^{-v_{k+1}}
    = sum_{i=1}^{k} 3^{(k+1)-i} * 2^{-S_i} * 2^{-v_{k+1}} + 2^{-v_{k+1}}

    For this to equal sum_{j=1}^{k+1} 3^{(k+1)-j} * 2^{-S_j}, we need:
    3^{(k+1)-j} * 2^{-S_j} for j=1..k to match 3^{(k+1)-j} * 2^{-S_j} * 2^{-v_{k+1}}

    This does NOT match unless v_{k+1} = 0. So the formula as stated needs correction!

    Let me re-examine...
    """
    print("\n=== Induction structure analysis ===")
    print("Checking if the formula T^k(n) mod 3^k = sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k")
    print("is actually correct...")

def examine_exact_formula(k, max_n=100):
    """Re-examine what the exact formula should be"""
    mod3k = 3**k
    if mod3k <= 1:
        return

    print(f"\n=== Exact formula for k={k}, mod 3^{k}={mod3k} ===")
    for n in range(1, min(max_n, 50), 2):
        vs = compute_v2_sequence(n, k)
        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)
        Sk = Ss[k]

        Tk = syracuse_iter(k, n)
        actual = Tk % mod3k

        # Formula: sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k
        formula_val = 0
        for i in range(1, k + 1):
            inv_2_Si = pow(2, -Ss[i], mod3k)
            formula_val = (formula_val + pow(3, k - i, mod3k) * inv_2_Si) % mod3k

        match = "OK" if actual == formula_val else "FAIL"
        if match == "FAIL" or n <= 19:
            print(f"  n={n:3d}: vs={vs}, Sk={Sk}, T^{k}(n)={Tk}, "
                  f"actual_mod={actual}, formula={formula_val} [{match}]")

# Main execution
print("=" * 70)
print("C_k closed form analysis: T^k(n) mod 3^k")
print("=" * 70)

# Step 1: Verify the closed form T^k(n) = (3^k * n + C_k) / 2^{S_k}
print("\n[Step 1] Verify T^k formula for small cases")
for k in range(1, 5):
    for n in [1, 3, 5, 7, 9, 11, 13, 15]:
        Tk, vs, Ck, Sk = verify_Tk_formula(n, k)
print("  All formula verifications passed!")

# Step 2: Verify mod 3^k independence from n
print("\n[Step 2] Verify T^k(n) mod 3^k depends only on v2 sequence")
for k in range(1, 5):
    verify_mod3k_independence(k, max_n=500)

# Step 3: Verify the explicit closed form
print("\n[Step 3] Verify closed form sum_{i=1}^{k} 3^{k-i} * 2^{-S_i} mod 3^k")
for k in range(1, 6):
    verify_closed_form(k, max_n=500)

# Step 4: k=1 detail
analyze_k1_detail()

# Step 5: Examine exact formula
for k in range(1, 5):
    examine_exact_formula(k)

# Step 6: Understand the induction structure
analyze_induction_structure()

# Step 7: Formalize the key identity for induction
print("\n\n" + "=" * 70)
print("KEY IDENTITY FOR INDUCTION")
print("=" * 70)
print("""
Base case (k=1):
  T(n) mod 3 = 2^{-v_1} mod 3
  This is exactly syracuse_mod3_eq!

Inductive step: Suppose T^k(n) ≡ Σ_{i=1}^{k} 3^{k-i} · 2^{-S_i} (mod 3^k)

  Let m = T^k(n). Then T^{k+1}(n) = T(m).

  m = 3^k · Q + R  where R = Σ_{i=1}^{k} 3^{k-i} · 2^{-S_i} mod 3^k
  (Q depends on n, R depends only on v2 sequence)

  3m + 1 = 3^{k+1} · Q + 3R + 1

  mod 3^{k+1}:
  3m + 1 ≡ 3R + 1 (mod 3^{k+1})
         = 3 · Σ_{i=1}^{k} 3^{k-i} · 2^{-S_i} + 1
         = Σ_{i=1}^{k} 3^{k+1-i} · 2^{-S_i} + 1

  T^{k+1}(n) = (3m + 1) / 2^{v_{k+1}}

  mod 3^{k+1}: (gcd(2, 3) = 1 so division by 2^{v_{k+1}} is multiplication by inverse)

  T^{k+1}(n) ≡ (Σ_{i=1}^{k} 3^{k+1-i} · 2^{-S_i} + 1) · 2^{-v_{k+1}} (mod 3^{k+1})
              = Σ_{i=1}^{k} 3^{(k+1)-i} · 2^{-(S_i + v_{k+1})} + 2^{-v_{k+1}}

  Now S_i + v_{k+1} is NOT the same as S_{i+1} in general!
  But: we can rewrite this by noting S_{k+1} = S_k + v_{k+1}:

  For i=1..k: S_i + v_{k+1} = S_i + S_{k+1} - S_k

  Hmm, this doesn't simplify to the target formula directly.

  Let me re-check if the formula is:
  T^k(n) mod 3^k = Σ_{i=1}^{k} 3^{k-i} · 2^{-(S_i)} mod 3^k  ???

  Or perhaps: T^k(n) mod 3^k = Σ_{i=0}^{k-1} 3^i · 2^{-S_{k-i}} mod 3^k ???
""")

# Step 8: Check alternative formula forms
print("\n[Step 8] Check alternative formula representations")
for k in range(1, 5):
    mod3k = 3**k
    print(f"\nk={k}, mod 3^k={mod3k}")
    for n in [1, 3, 7, 15, 31]:
        if n % 2 == 0:
            continue
        vs = compute_v2_sequence(n, k)
        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)

        Tk = syracuse_iter(k, n)
        actual = Tk % mod3k

        # Original formula: sum_{i=1}^{k} 3^{k-i} * 2^{-S_i}
        f1 = sum(pow(3, k-i, mod3k) * pow(2, -Ss[i], mod3k) for i in range(1, k+1)) % mod3k

        # Alternative: sum_{j=0}^{k-1} 3^j * 2^{-S_{k-j}}
        f2 = sum(pow(3, j, mod3k) * pow(2, -Ss[k-j], mod3k) for j in range(k)) % mod3k

        print(f"  n={n:3d}: vs={vs}, actual={actual}, f1={f1}, f2={f2}, f1==f2={f1==f2}")

print("\n\n" + "=" * 70)
print("INDUCTION STEP VERIFICATION")
print("=" * 70)
# Verify the induction step numerically
for k in range(1, 4):
    mod_next = 3**(k+1)
    print(f"\nVerifying k -> k+1: k={k}, mod 3^{k+1}={mod_next}")
    for n in range(1, 60, 2):
        vs = compute_v2_sequence(n, k+1)
        vs_k = vs[:k]
        v_kp1 = vs[k]

        Ss = [0]
        for v in vs:
            Ss.append(Ss[-1] + v)

        Tkp1 = syracuse_iter(k+1, n)
        actual = Tkp1 % mod_next

        # Target formula: sum_{i=1}^{k+1} 3^{(k+1)-i} * 2^{-S_i}
        target = sum(pow(3, (k+1)-i, mod_next) * pow(2, -Ss[i], mod_next)
                    for i in range(1, k+2)) % mod_next

        # From induction hypothesis:
        # IH gives T^k(n) mod 3^k, then
        # T^{k+1}(n) mod 3^{k+1} = (3 * (IH_residue mod 3^k) + 1) * 2^{-v_{k+1}} mod 3^{k+1}

        # IH residue (using the FULL T^k(n), not just mod 3^k)
        Tk = syracuse_iter(k, n)
        ih_residue = sum(pow(3, k-i, 3**k) * pow(2, -Ss[i], 3**k)
                        for i in range(1, k+1)) % (3**k)

        # Step: (3 * ih_residue + 1) * 2^{-v_{k+1}} mod 3^{k+1}
        step_val = (3 * ih_residue + 1) * pow(2, -v_kp1, mod_next) % mod_next

        match_target = "OK" if actual == target else "FAIL"
        match_step = "OK" if actual == step_val else "FAIL"

        if n <= 11 or match_target != "OK" or match_step != "OK":
            print(f"  n={n:3d}: actual={actual:4d}, target={target:4d} [{match_target}], "
                  f"step={step_val:4d} [{match_step}], v_{k+1}={v_kp1}")
