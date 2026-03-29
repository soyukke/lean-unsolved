"""
Exploration Part 3 (fast version): Key structural discoveries
Limited to K <= 4 for semigroup computation
"""

import json
from collections import defaultdict
from math import gcd

def compute_Tk_mod3k(v2_seq):
    k = len(v2_seq)
    if k == 0:
        return None
    mod = 3**k
    S = [0]
    for j in v2_seq:
        S.append(S[-1] + j)
    Ck = 0
    for i in range(k):
        Ck = (Ck + pow(3, k-1-i, mod) * pow(2, S[i], mod)) % mod
    Sk = sum(v2_seq)
    inv_2Sk = pow(2, -Sk, mod)
    return (Ck * inv_2Sk) % mod

# ============================================================
# 1. Semigroup sizes and structure
# ============================================================
print("=" * 70)
print("1. Semigroup analysis (K=1..4)")
print("=" * 70)

semigroup_sizes = {}
for K in range(1, 5):
    mod = 3**K
    ord_val = 2 * 3**(K-1)

    # Generate DISTINCT generators
    distinct_gens = set()
    for j in range(1, ord_val + 1):
        inv2j = pow(2, -j, mod)
        fj = tuple((3 * inv2j * r + inv2j) % mod for r in range(mod))
        distinct_gens.add(fj)

    semigroup = set(distinct_gens)
    frontier = set(distinct_gens)
    for depth in range(1, 30):
        new_elements = set()
        for func in list(frontier):
            for gen in distinct_gens:
                composed = tuple(gen[func[r]] for r in range(mod))
                if composed not in semigroup:
                    new_elements.add(composed)
                    semigroup.add(composed)
        frontier = new_elements
        if not frontier:
            break

    constant_funcs = [f for f in semigroup if all(f[r] == f[0] for r in range(mod))]
    semigroup_sizes[K] = len(semigroup)

    print(f"\nK={K}, mod={mod}:")
    print(f"  |generators| = {len(distinct_gens)}, |semigroup| = {len(semigroup)}")
    print(f"  Constant maps: {len(constant_funcs)}, phi(3^K) = {ord_val}")

    # Level decomposition by v3(slope)
    by_v3 = defaultdict(list)
    for func in semigroup:
        slope = (func[1] - func[0]) % mod
        v3 = 0
        s = slope
        while s > 0 and s % 3 == 0:
            s //= 3
            v3 += 1
        if slope == 0:
            v3 = K
        by_v3[v3].append(func)

    for v3 in sorted(by_v3.keys()):
        print(f"  v3(slope)={v3}: {len(by_v3[v3])} functions")

# Semigroup size pattern
print("\nSemigroup size pattern:")
for K in sorted(semigroup_sizes.keys()):
    print(f"  K={K}: |S| = {semigroup_sizes[K]}")

sizes = [semigroup_sizes[K] for K in sorted(semigroup_sizes.keys())]
print("  Ratios:")
for i in range(len(sizes) - 1):
    print(f"    |S_{i+2}|/|S_{i+1}| = {sizes[i+1]}/{sizes[i]} = {sizes[i+1]/sizes[i]:.4f}")

# Check: |S_K| = sum over levels of phi(3^K) * (number of distinct slopes at that level)
# Or maybe: |S_K| = phi(3^K) * K - something?

for K in sorted(semigroup_sizes.keys()):
    phi = 2 * 3**(K-1)
    print(f"  K={K}: |S|/phi = {semigroup_sizes[K]/phi:.4f}, |S|/K = {semigroup_sizes[K]/K:.4f}")

# ============================================================
# 2. Constant v2 sequences and 3-adic limits
# ============================================================
print("\n" + "=" * 70)
print("2. 3-adic limits for constant and periodic v2 sequences")
print("=" * 70)

# constant j => limit = 1/(2^j - 3) in Z_3
print("\nConstant v2=j => limit = 1/(2^j - 3) in Z_3:")
for j in range(1, 8):
    K = 10
    mod = 3**K
    denom = pow(2, j, mod) - 3
    if gcd(denom % mod, mod) == 1:
        limit_val = pow(denom, -1, mod) % mod
    elif denom == 0:
        print(f"  j={j}: 2^j=3, no limit (singular!)")
        continue
    else:
        print(f"  j={j}: denom={denom}, gcd={gcd(denom % mod, mod)}")
        continue

    # Get 3-adic digits
    digits = []
    v = limit_val
    for _ in range(K):
        digits.append(v % 3)
        v //= 3

    # Verify with transducer
    v2_seq = [j] * K
    val = compute_Tk_mod3k(v2_seq)

    match = "MATCH" if val == limit_val else "MISMATCH"
    print(f"  j={j}: 1/(2^{j}-3) = 1/{2**j - 3} -> {limit_val} mod 3^{K}, "
          f"digits={digits[:6]}..., verify: {match}")

# Special cases
print("\nSpecial 3-adic values:")
print(f"  j=1: 1/(2-3) = -1 in Z_3 = ...222 (all digits 2)")
print(f"  j=2: 1/(4-3) = 1 in Z_3 = ...001 (d_1=1, rest 0)")
print(f"  j=3: 1/(8-3) = 1/5 in Z_3")
print(f"  j=4: 1/(16-3) = 1/13 in Z_3")

# ============================================================
# 3. Period-2 v2 sequences
# ============================================================
print("\n" + "=" * 70)
print("3. Period-2 v2 sequences: (a,b,a,b,...)")
print("=" * 70)

print("\nLimit = (3 + 2^a) / (2^{a+b} - 9) in Z_3:")
for a in range(1, 5):
    for b in range(1, 5):
        denom = 2**(a+b) - 9
        numer = 3 + 2**a
        if denom == 0:
            print(f"  (a,b)=({a},{b}): SINGULAR (2^(a+b)=9)")
            continue
        K = 8
        mod = 3**K
        if gcd(abs(denom) % mod, mod) != 1:
            continue
        limit_val = (numer * pow(denom, -1, mod)) % mod

        # Verify
        v2_seq = [a, b] * (K // 2) + ([a] if K % 2 else [])
        v2_seq = v2_seq[:K]
        val = compute_Tk_mod3k(v2_seq)

        digits = []
        v = limit_val
        for _ in range(6):
            digits.append(v % 3)
            v //= 3

        match = "OK" if val == limit_val else "DIFF"
        print(f"  ({a},{b}): {numer}/{denom} -> digits={digits}, verify={match}")

# ============================================================
# 4. Key quotient structure theorem
# ============================================================
print("\n" + "=" * 70)
print("4. Quotient structure: mod 9 transitions factor through mod 3")
print("=" * 70)

# The crucial observation: in the mod 9 transducer,
# states {1,4,7} (d_1=1) have IDENTICAL transitions
# states {2,5,8} (d_1=2) have IDENTICAL transitions
# This means the automaton has a quotient of size 2!

# More generally: in M_K, the transition depends only on R mod 3^{K-1}.
# So M_K has a quotient isomorphic to M_{K-1}!

# But there's more: the OUTPUT depends on the FULL state R mod 3^K.
# So the quotient loses information about the last digit.

# The transducer is a TOWER:
# M_1 --quotient--> M_0 (trivial)
# M_2 --quotient--> M_1 (2 real states)
# M_3 --quotient--> M_2 (6 real states)
# ...
# Each level adds one "layer" of output resolution.

print("\nTower structure:")
print("  M_K has phi(3^K) = 2*3^{K-1} operational states")
print("  M_K --quotient--> M_{K-1} by reducing state mod 3^{K-1}")
print("  Each level adds 2*3^{K-2} new states (for K >= 2)")
print("  The quotient preserves the transition structure exactly")

# Verify: at each level K, the extension adds a LIFT of each transition
# in M_{K-1}, and each state in M_{K-1} lifts to 3 states in M_K
for K in range(2, 5):
    mod_K = 3**K
    mod_Km1 = 3**(K-1)

    # For each state r in M_{K-1} and input j,
    # the three lifts r, r+mod_{K-1}, r+2*mod_{K-1} in M_K
    # all transition to the SAME value mod 3^{K-1}
    violations = 0
    tests = 0
    for r in range(mod_Km1):
        if gcd(r, 3) == 0 and r != 0:
            continue  # skip non-coprime (unreachable)
        for j in range(1, 7):
            inv_j_K = pow(2, -j, mod_K)
            targets_mod_Km1 = set()
            for lift in range(3):
                R = r + lift * mod_Km1
                new_R = ((3 * R + 1) * inv_j_K) % mod_K
                targets_mod_Km1.add(new_R % mod_Km1)
            tests += 1
            if len(targets_mod_Km1) > 1:
                violations += 1

    print(f"  K={K}: {tests} tests, {violations} violations (should be 0)")

# ============================================================
# 5. The full picture: explicit description for small K
# ============================================================
print("\n" + "=" * 70)
print("5. Complete transducer specification")
print("=" * 70)

# M_1: states {1,2}, transition delta(R,j) = 2^{-j} mod 3
# M_2: states {1,2,4,5,7,8}, transition delta(R,j) = (3R+1)*2^{-j} mod 9
# etc.

# The effective quotient at K=2 has 2 states (d_1 values 1,2)
# and at K=3 has 6 states (d_1, d_2 combinations)

# Print the mod 9 transducer in quotient form
print("\n--- M_2 quotient form (2 effective states) ---")
print("Effective state = d_1 = R mod 3 in {1, 2}")
print("Input effective mod 6")
print()
print("  state | j%6=1 | j%6=2 | j%6=3 | j%6=4 | j%6=5 | j%6=0")
print("  ------|-------|-------|-------|-------|-------|------")

for d1 in [1, 2]:
    row = f"  d1={d1} |"
    for j in range(1, 7):
        inv2j = pow(2, -j, 9)
        new_R = ((3 * d1 + 1) * inv2j) % 9
        new_d1 = new_R % 3
        d2_out = new_R // 3
        row += f" {new_d1}(d2={d2_out})|"
    print(row)

print()
print("Interpretation: from state d_1, reading j, go to new d_1 and output d_2")
print("The pair (new d_1, d_2) encodes new_R = new_d1 + 3*d_2")

# ============================================================
# 6. Summary and key theorem
# ============================================================
print("\n" + "=" * 70)
print("6. KEY THEOREM: The Collatz 2-adic to 3-adic transducer")
print("=" * 70)

print("""
THEOREM (Collatz Transducer Family):
For each K >= 1, there exists a deterministic finite automaton (Mealy machine)

  M_K = (Q_K, Sigma_K, delta_K, q_0, lambda_K)

with:
  - Q_K = (Z/3^K Z)* ∪ {0}  (state space, |Q_K| = phi(3^K) + 1 = 2*3^{K-1} + 1)
  - Sigma_K = Z/ord_{3^K}(2)Z = Z/2*3^{K-1}Z  (effective input alphabet)
  - q_0 = 0  (initial state)
  - delta_K(R, j) = (3R + 1) * 2^{-j} mod 3^K  (transition function)
  - lambda_K(R) = (R mod 3, (R//3) mod 3, ..., (R//3^{K-1}) mod 3)  (output)

such that:

1. CORRECTNESS: For any odd n >= 1, after feeding the v2 sequence
   (j_1, ..., j_k) where j_i = v_2(3*T^{i-1}(n)+1) into M_K,
   the final state equals T^k(n) mod 3^K (for any k >= K).

2. PROFINITE CONSISTENCY: The natural projection
   pi: Q_{K+1} -> Q_K given by R ↦ R mod 3^K
   commutes with the transition: pi(delta_{K+1}(R,j)) = delta_K(pi(R), j mod 2*3^{K-1}).

3. AFFINE STRUCTURE: delta_K is the affine map f_j(R) = 3*2^{-j}*R + 2^{-j}.
   The slope 3*2^{-j} is always divisible by 3.

4. k-STEP INDEPENDENCE: After k >= K transitions from q_0, the final state
   R_k mod 3^K depends ONLY on the v2 sequence, not on n.
   (Because the k-fold composition slope = 3^k * 2^{-S_k} ≡ 0 mod 3^K for k >= K.)

5. QUOTIENT TOWER: M_K quotients to M_{K-1} via state reduction mod 3^{K-1}.
   The transition depends only on R mod 3^{K-1}, so the quotient is exact.

6. DIGIT 0 AVOIDANCE: All reachable states R satisfy R mod 3 ≠ 0.
   (Equivalently, the first 3-adic digit of T^k(n) is always in {1,2}.)

7. CONSTANT SEQUENCE LIMITS: For v2 = (j,j,...,j),
   the 3-adic limit is 1/(2^j - 3) ∈ Z_3.
   Special cases: j=1 → -1, j=2 → 1.

8. SEMIGROUP: The transition semigroup generated by {f_j : j=1,...,2*3^{K-1}}
   has size 2, 12, 60, 276 for K=1,2,3,4 respectively.
   It decomposes by v3(slope) into K+1 levels, with constant maps at the bottom.
""")

# Save final results
results = {
    "title": "2-adic -> 3-adic transducer: 有限状態オートマトン表現の完全構成",
    "approach": "v2列からT^k(n) mod 3^Kを計算するMealy machine族 {M_K} を構成。遷移関数 delta(R,j)=(3R+1)*2^{-j} mod 3^K のアフィン写像構造を解明。profinite limit, quotient tower, 遷移半群のlevel分解を検証。",
    "findings": [
        "遷移関数の完全な代数的記述: delta_K(R, j) = (3R+1)*2^{-j} mod 3^K はアフィン写像 f_j(R) = 3*2^{-j}*R + 2^{-j}",
        "k回合成の傾き 3^k*2^{-S_k} が mod 3^k で消滅するため、合成は定数写像。k-step独立性の代数的証明",
        "Profinite consistency完全検証: delta_{K+1}(R,j) mod 3^K = delta_K(R mod 3^K, j) (K=1..4)",
        "Quotient tower構造: M_Kの遷移はR mod 3^{K-1}のみに依存。商自動機械はM_{K-1}と完全一致",
        "到達可能状態 = {0} ∪ (Z/3^KZ)* = phi(3^K)+1。3の倍数は初期状態0のみ到達可能",
        "遷移半群サイズ: K=1:2, K=2:12, K=3:60, K=4:276。Level分解（v3(slope)による層別化）を発見",
        "定常v2列の3-adic極限: j=const => 1/(2^j-3) ∈ Z_3。j=1で-1, j=2で1",
        "周期v2列の3-adic極限の閉形式: (a,b)周期 => (3+2^a)/(2^{a+b}-9) ∈ Z_3",
        "K>=5でcoverage gap: v2列の実現可能性制約により全coprime残基が出現しない"
    ],
    "hypotheses": [
        "遷移半群サイズの成長率 |S_{K+1}|/|S_K| は K -> inf で 3 に収束するか",
        "coverage gapはv2列のMarkov的制約から厳密に特徴づけられる",
        "profinite limit M_inf は Z_2 上の連続力学系 → Z_3 への連続写像を定義する"
    ],
    "dead_ends": [
        "streaming transducer（入力ごとに1桁出力）は有限状態では不可能。必要状態数が桁とともに増大",
        "3-adic桁のcoherence不成立: T^k(n) mod 3^{k-1} ≠ T^{k-1}(n) mod 3^{k-1}",
        "K=5の半群計算は状態空間爆発のため直接計算不可（243^243規模の関数空間）"
    ],
    "scripts_created": [
        "scripts/exploration_2adic_3adic_transducer.py",
        "scripts/exploration_2adic_3adic_transducer_v2.py",
        "scripts/exploration_2adic_3adic_transducer_v3_fast.py"
    ],
    "outcome": "中発見",
    "next_directions": [
        "遷移半群サイズ列 2, 12, 60, 276 のOEIS検索と閉形式の探索",
        "Lean形式化: profinite consistency定理",
        "Lean形式化: affine composition slope vanishing定理",
        "v2列の実現可能性制約（Markov連鎖モデル）と coverage gap の関係解析",
        "3-adic極限の連続写像としての性質（Z_2 -> Z_3の連続性、像の測度）"
    ],
    "transducer_specification": {
        "family": "M_K for K = 1, 2, 3, ...",
        "state_space": "Q_K = (Z/3^K Z)* ∪ {0}, |Q_K| = 2*3^{K-1} + 1",
        "input_alphabet": "Z_{>0}, effective mod 2*3^{K-1} (= ord_{3^K}(2))",
        "initial_state": 0,
        "transition": "delta_K(R, j) = (3R + 1) * 2^{-j} mod 3^K",
        "output": "lambda_K(R) = base-3 digits of R (K digits)",
        "properties": [
            "Affine: f_j(R) = 3*2^{-j}*R + 2^{-j}",
            "Profinite consistent: compatible under reduction mod 3^{K-1}",
            "k >= K compositions are constant (independent of initial state)",
            "All reachable states coprime to 3 (except initial 0)",
            "Quotient M_K -> M_{K-1} is exact (transition factors through)"
        ]
    },
    "semigroup_analysis": {
        "sizes": {"1": 2, "2": 12, "3": 60, "4": 276},
        "ratios": {"2/1": 6.0, "3/2": 5.0, "4/3": 4.6},
        "level_decomposition": "Functions classified by v3(slope). Level K contains constant maps.",
        "constant_maps": {"1": 2, "2": 6, "3": 18, "4": 54}
    },
    "3adic_limits": {
        "constant_j": "1/(2^j - 3) in Z_3",
        "j=1": "-1 = ...222 in Z_3",
        "j=2": "1 = ...001 in Z_3",
        "period_2": "(3+2^a)/(2^{a+b}-9) in Z_3"
    },
    "explicit_tables": {
        "M1_mod3": {
            "description": "State-independent: delta(R,j) = 2^{-j} mod 3",
            "rule": "j odd -> 2, j even -> 1"
        },
        "M2_mod9": {
            "description": "2 effective states (d_1 in {1,2}), input mod 6",
            "transitions": {
                "(1,1)": "(2,d2=0)", "(1,2)": "(1,d2=0)", "(1,3)": "(2,d2=1)",
                "(1,4)": "(1,d2=2)", "(1,5)": "(2,d2=2)", "(1,6)": "(1,d2=1)",
                "(2,1)": "(2,d2=2)", "(2,2)": "(1,d2=1)", "(2,3)": "(2,d2=0)",
                "(2,4)": "(1,d2=0)", "(2,5)": "(2,d2=1)", "(2,6)": "(1,d2=2)"
            }
        }
    },
    "details": "See transducer_specification and semigroup_analysis for full details."
}

with open("/Users/soyukke/study/lean-unsolved/results/2adic_3adic_transducer.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nResults saved to results/2adic_3adic_transducer.json")
