"""
探索186: Profinite整合性 delta_{K+1} mod 3^K = delta_K の形式化設計

Mealy機械族 M_K の定義:
- 状態集合: Z/3^K Z の奇数 (mod 3^K で奇数の剰余類)
- 入力: j in {1, 2, ...} (v2(3R+1) に依存)
- 遷移: delta_K(R, j) = (3R+1) * 2^{-j} mod 3^K

profinite整合性:
- pi_{K+1,K}: Z/3^{K+1} -> Z/3^K (自然な射影)
- delta_{K+1}(R, j) mod 3^K = delta_K(R mod 3^K, j)

これは射影極限 lim_K M_K が well-defined な Mealy 機械を定義することを保証する。
"""

import json
import math
from collections import Counter, defaultdict

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^v2(3n+1)"""
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def mod_inverse_2(k, mod):
    """2^k の逆元 mod mod (mod が奇数のとき存在)"""
    return pow(2, k, mod) if mod > 1 else 0

def pow2_inv_mod(j, mod):
    """2^{-j} mod mod を計算。mod が奇数なら pow(2, -j, mod) = pow(2, mod-1-j, mod) (Euler) ではなく
    直接 pow(2, j, mod) の逆元を求める"""
    if mod == 1:
        return 0
    p2 = pow(2, j, mod)
    # p2 * x = 1 (mod mod) を求める
    # mod は 3^K なので gcd(2, mod)=1 → 逆元存在
    return pow(p2, -1, mod)

def delta_K(R, j, K):
    """Mealy機械 M_K の遷移関数
    delta_K(R, j) = (3R + 1) * 2^{-j} mod 3^K
    """
    mod = 3 ** K
    val = (3 * R + 1) * pow2_inv_mod(j, mod)
    return val % mod

def syracuse_mod3k(n, K):
    """Syracuse(n) mod 3^K を直接計算"""
    return syracuse(n) % (3 ** K)

# ============================================================
# 検証1: profinite整合性 delta_{K+1} mod 3^K = delta_K
# ============================================================
def verify_profinite_consistency(K_max=6):
    """delta_{K+1}(R, j) mod 3^K == delta_K(R mod 3^K, j) を全ての
    有効な状態・入力で検証"""
    results = {}
    for K in range(1, K_max):
        mod_K = 3 ** K
        mod_K1 = 3 ** (K + 1)

        # K+1 レベルの奇数状態を全列挙
        states_K1 = [r for r in range(mod_K1) if r % 2 == 1]

        total_tests = 0
        failures = 0
        max_j_tested = 0

        for R in states_K1:
            R_proj = R % mod_K  # pi_{K+1,K}(R)

            # j の範囲: v2(3R+1) が自然な入力だが、一般の j も検証
            for j in range(1, 12):
                val_K1 = delta_K(R, j, K + 1)
                val_K1_proj = val_K1 % mod_K
                val_K = delta_K(R_proj, j, K)

                total_tests += 1
                max_j_tested = max(max_j_tested, j)

                if val_K1_proj != val_K:
                    failures += 1
                    if failures <= 3:
                        print(f"  FAILURE at K={K}, R={R}, j={j}: "
                              f"delta_{K+1}={val_K1} mod 3^K={val_K1_proj}, "
                              f"delta_K={val_K}")

        results[K] = {
            "K": K,
            "K_plus_1": K + 1,
            "mod_K": mod_K,
            "mod_K1": mod_K1,
            "num_states_K1": len(states_K1),
            "total_tests": total_tests,
            "failures": failures,
            "consistent": failures == 0,
            "max_j_tested": max_j_tested
        }

    return results

# ============================================================
# 検証2: delta_K と実際のSyracuse関数の整合性
# ============================================================
def verify_delta_vs_syracuse(K_max=5, N=10000):
    """delta_K(n % 3^K, v2(3n+1)) == syracuse(n) % 3^K を検証"""
    results = {}
    for K in range(1, K_max + 1):
        mod = 3 ** K
        total = 0
        failures = 0

        for n in range(1, N + 1, 2):
            j = v2(3 * n + 1)
            R = n % mod

            # Mealy遷移
            delta_val = delta_K(R, j, K)
            # 直接計算
            syr_val = syracuse(n) % mod

            total += 1
            if delta_val != syr_val:
                failures += 1
                if failures <= 3:
                    print(f"  MISMATCH K={K}, n={n}: delta={delta_val}, syr mod={syr_val}")

        results[K] = {
            "K": K,
            "mod": mod,
            "total_tests": total,
            "failures": failures,
            "matches": total - failures,
            "match_rate": round((total - failures) / total, 6) if total > 0 else 0,
            "note": "delta_K depends on j=v2(3n+1) which is NOT determined by n mod 3^K alone"
        }

    return results

# ============================================================
# 検証3: Mealy遷移の決定性の分析
# ============================================================
def analyze_mealy_determinism(K_max=4):
    """各状態 R in (Z/3^K)^* の奇数に対し、
    入力 j が R mod 3^K から一意に決まるか、
    それとも j に依存するかを分析"""
    results = {}

    for K in range(1, K_max + 1):
        mod = 3 ** K

        # 各奇数状態 R に対して、実際に到達する (j, output) ペアを収集
        state_analysis = {}
        N = max(50000, mod * 50)

        for R in range(1, mod, 2):
            j_values = set()
            outputs = {}  # j -> set of outputs

            for mult in range(N // mod + 1):
                n = R + mod * mult
                if n > 0 and n % 2 == 1:
                    j = v2(3 * n + 1)
                    j_values.add(j)
                    if j not in outputs:
                        outputs[j] = set()
                    outputs[j].add(syracuse(n) % mod)

            # 各 j に対して出力は一意か?
            j_deterministic = {j: len(outs) == 1 for j, outs in outputs.items()}
            all_j_det = all(j_deterministic.values())

            state_analysis[R] = {
                "j_values_observed": sorted(j_values),
                "num_j_values": len(j_values),
                "j_deterministic": j_deterministic,
                "all_deterministic_given_j": all_j_det,
                "outputs_by_j": {j: sorted(list(outs)) for j, outs in outputs.items()}
            }

        # 統計
        total_states = len(state_analysis)
        all_det = sum(1 for s in state_analysis.values() if s["all_deterministic_given_j"])
        avg_j = sum(s["num_j_values"] for s in state_analysis.values()) / total_states

        results[K] = {
            "K": K,
            "mod": mod,
            "num_odd_states": total_states,
            "states_fully_deterministic_given_j": all_det,
            "determinism_ratio": round(all_det / total_states, 4),
            "avg_num_j_per_state": round(avg_j, 4),
            "sample_states": {
                R: state_analysis[R]
                for R in sorted(state_analysis.keys())[:5]
            }
        }

    return results

# ============================================================
# 検証4: profinite整合性の代数的構造
# ============================================================
def analyze_algebraic_structure(K_max=5):
    """整合性の代数的本質:
    (3R+1) * 2^{-j} mod 3^{K+1} が
    (3(R mod 3^K)+1) * 2^{-j} mod 3^K に整合する理由を分析"""

    results = {}

    for K in range(1, K_max):
        mod_K = 3 ** K
        mod_K1 = 3 ** (K + 1)

        # 代数的に: R = R_0 + 3^K * t (0 <= t < 3) where R_0 = R mod 3^K
        # 3R + 1 = 3R_0 + 3^{K+1} * t + 1
        # (3R+1) mod 3^{K+1} の 3^K 部分は 3^{K+1} * t なので
        # (3R+1) mod 3^K = (3R_0 + 1) mod 3^K  (3^{K+1}*t は 3^K で割り切れる)

        # 検証: (3R+1) mod 3^K = (3(R mod 3^K)+1) mod 3^K
        consistency_verified = True
        for R in range(mod_K1):
            R0 = R % mod_K
            lhs = (3 * R + 1) % mod_K
            rhs = (3 * R0 + 1) % mod_K
            if lhs != rhs:
                consistency_verified = False
                break

        # 2^{-j} mod 3^K: これは K のみに依存し、R に依存しない
        # よって (3R+1) * 2^{-j} mod 3^K = ((3R+1) mod 3^K) * (2^{-j} mod 3^K) mod 3^K
        #       = (3(R mod 3^K)+1) * (2^{-j} mod 3^K) mod 3^K
        #       = delta_K(R mod 3^K, j)

        # 鍵となる性質: 2^{-j} mod 3^{K+1} の射影
        inv_consistency = True
        for j in range(1, 15):
            inv_K1 = pow2_inv_mod(j, mod_K1)
            inv_K = pow2_inv_mod(j, mod_K)
            if inv_K1 % mod_K != inv_K:
                inv_consistency = False
                print(f"  INV MISMATCH: K={K}, j={j}, inv_K1 mod 3^K = {inv_K1 % mod_K}, inv_K = {inv_K}")

        results[K] = {
            "K": K,
            "linear_part_consistent": consistency_verified,
            "inverse_consistent": inv_consistency,
            "proof_sketch": (
                f"(3R+1) mod 3^{K} = (3(R mod 3^{K})+1) mod 3^{K} "
                f"because 3*(R - R mod 3^{K}) = 3 * 3^{K} * t ≡ 0 (mod 3^{K}). "
                f"Also 2^{{-j}} mod 3^{K} is the projection of 2^{{-j}} mod 3^{K+1}."
            ),
            "formalization_approach": (
                "Split into two lemmas: "
                "(1) (3R+1) % 3^K = (3*(R%3^K)+1) % 3^K  [omega or Nat.add_mul_mod_self] "
                "(2) pow(2,j,3^{K+1})^{-1} % 3^K = pow(2,j,3^K)^{-1}  [ZMod.castHom compatibility]"
            )
        }

    return results

# ============================================================
# 検証5: 射影極限の構造
# ============================================================
def analyze_projective_limit(K_max=5, num_elements=20):
    """射影極限 lim_K M_K の元の具体例を構成"""
    results = {}

    # 小さい奇数から出発して、各 K での軌道を追跡
    test_values = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39]

    for n in test_values[:num_elements]:
        if n % 2 == 0:
            continue
        trajectory = {}
        for K in range(1, K_max + 1):
            mod = 3 ** K
            j = v2(3 * n + 1)
            R = n % mod
            next_state = delta_K(R, j, K)
            actual_syr = syracuse(n) % mod

            trajectory[K] = {
                "state_R": R,
                "input_j": j,
                "next_state": next_state,
                "actual_syracuse_mod": actual_syr,
                "match": next_state == actual_syr
            }

        # 整合性チェック: K+1 の結果 mod 3^K = K の結果
        coherent = True
        for K in range(1, K_max):
            mod_K = 3 ** K
            if trajectory[K + 1]["next_state"] % mod_K != trajectory[K]["next_state"]:
                coherent = False

        results[f"n={n}"] = {
            "n": n,
            "syracuse_n": syracuse(n),
            "v2_3n1": v2(3 * n + 1),
            "trajectory": trajectory,
            "projective_coherent": coherent
        }

    return results

# ============================================================
# 検証6: Lean形式化の設計
# ============================================================
def design_lean_formalization():
    """Lean 4での形式化設計"""

    design = {
        "target_theorem": "profinite_consistency",
        "statement": (
            "forall K : Nat, forall R : ZMod (3^(K+1)), forall j : Nat, "
            "ZMod.castHom (dvd_pow_self 3 (show K <= K+1 by omega)) (delta (K+1) R j) "
            "= delta K (ZMod.castHom ... R) j"
        ),
        "key_definitions": {
            "delta_K": (
                "def delta_K (K : Nat) (R : ZMod (3^K)) (j : Nat) : ZMod (3^K) := "
                "(3 * R + 1) * (2^j)^(-1 : ZMod (3^K))"
            ),
            "mealy_machine": (
                "structure MealyK (K : Nat) where "
                "  states : Finset (ZMod (3^K))  -- odd residues "
                "  transition : ZMod (3^K) -> Nat -> ZMod (3^K)"
            ),
            "projection": (
                "def pi (K : Nat) : ZMod (3^(K+1)) ->+* ZMod (3^K) := "
                "ZMod.castHom (dvd_pow_self 3 (show K <= K+1 by omega))"
            )
        },
        "proof_structure": [
            "Step 1: Show (3*R+1) mod 3^K = (3*(R mod 3^K)+1) mod 3^K",
            "  This is: ZMod.castHom preserves (3*R+1)",
            "  Proof: castHom is a ring hom, so castHom(3*R+1) = 3*castHom(R)+1",
            "",
            "Step 2: Show castHom((2^j)^(-1)) = (2^j)^(-1) in ZMod(3^K)",
            "  This follows from: castHom is a ring hom, ring hom preserves inverses",
            "  Specifically: if f is RingHom and f(x) is invertible, f(x^(-1)) = f(x)^(-1)",
            "",
            "Step 3: Combine: castHom(delta_{K+1}(R,j)) = castHom((3R+1)*(2^j)^(-1))",
            "  = castHom(3R+1) * castHom((2^j)^(-1))",
            "  = (3*castHom(R)+1) * (2^j)^(-1)",
            "  = delta_K(castHom(R), j)",
        ],
        "lean_proof_sketch": """
-- The key insight: everything follows from castHom being a ring homomorphism
-- ZMod.castHom (dvd) : ZMod n →+* ZMod m

theorem profinite_consistency (K : ℕ) (R : ZMod (3^(K+1))) (j : ℕ) :
    let π := ZMod.castHom (Dvd.intro (3^1) rfl) (ZMod (3^K))
    π (delta (K+1) R j) = delta K (π R) j := by
  simp only [delta]
  -- π is a ring homomorphism, so:
  -- π((3*R+1) * (2^j)⁻¹) = π(3*R+1) * π((2^j)⁻¹)
  --                        = (3*π(R)+1) * (π(2^j))⁻¹
  --                        = (3*π(R)+1) * (2^j)⁻¹
  rw [map_mul, map_add, map_mul, map_natCast, map_one, map_inv₀, map_pow, map_natCast]
""",
        "dependencies": [
            "Mathlib.RingTheory.Ideal.Quotient",
            "Mathlib.Data.ZMod.Basic",
            "Mathlib.Data.ZMod.Algebra",
        ],
        "challenges": [
            "ZMod (3^K) requires K to be a natural number, and 3^K > 0",
            "Invertibility of 2^j in ZMod(3^K): gcd(2, 3^K) = 1 always holds",
            "castHom preserves inv requires the element to be a unit in both rings",
            "Need to handle: 2^j is a unit in ZMod(3^K) because gcd(2,3)=1",
        ],
        "alternative_nat_approach": {
            "description": "Instead of ZMod, work purely with Nat and modular arithmetic",
            "statement": (
                "theorem profinite_consistency_nat (K R j : ℕ) (hR : R < 3^(K+1)) "
                "(h2inv : ∃ t, t * 2^j % 3^K = 1) (h2inv' : ∃ t, t * 2^j % 3^(K+1) = 1) : "
                "let inv_K := Classical.choose h2inv; "
                "let inv_K1 := Classical.choose h2inv'; "
                "((3 * R + 1) * inv_K1) % 3^(K+1) % 3^K = ((3 * (R % 3^K) + 1) * inv_K) % 3^K"
            ),
            "proof_idea": (
                "The proof reduces to: "
                "(a * b) % m = ((a % m) * (b % m)) % m [Nat.mul_mod] "
                "and (3 * R + 1) % 3^K = (3 * (R % 3^K) + 1) % 3^K [because 3*(R - R%3^K) ≡ 0 mod 3^K]"
            )
        }
    }

    return design

# ============================================================
# 検証7: 入力 j の分布（v2(3n+1) mod 3^K 依存性）
# ============================================================
def analyze_input_j_distribution(K_max=4, N=50000):
    """各状態 R mod 3^K に対して、v2(3n+1) の分布を調査
    j が R だけで決まるか、それとも上位桁にも依存するか"""
    results = {}

    for K in range(1, K_max + 1):
        mod = 3 ** K
        state_j_dist = {}

        for R in range(1, mod, 2):
            j_counter = Counter()
            count = 0
            for mult in range(min(N // mod + 1, 500)):
                n = R + mod * mult
                if n > 0 and n % 2 == 1:
                    j = v2(3 * n + 1)
                    j_counter[j] += 1
                    count += 1

            state_j_dist[R] = {
                "total_samples": count,
                "j_distribution": dict(sorted(j_counter.items())),
                "num_distinct_j": len(j_counter),
                "is_j_unique": len(j_counter) == 1,
                "dominant_j": j_counter.most_common(1)[0] if j_counter else None
            }

        # j が一意に決まる状態の数
        unique_j_states = sum(1 for s in state_j_dist.values() if s["is_j_unique"])
        total_states = len(state_j_dist)

        results[K] = {
            "K": K,
            "mod": mod,
            "total_odd_states": total_states,
            "states_with_unique_j": unique_j_states,
            "unique_j_ratio": round(unique_j_states / total_states, 4) if total_states > 0 else 0,
            "note": "j (= v2(3n+1)) is generally NOT determined by n mod 3^K alone",
            "implication": "The Mealy machine needs j as explicit input, not derivable from state",
            "sample_states": {
                R: state_j_dist[R]
                for R in sorted(state_j_dist.keys())[:8]
            }
        }

    return results

# ============================================================
# メイン実行
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("探索186: Profinite整合性 delta_{K+1} mod 3^K = delta_K の形式化設計")
    print("=" * 70)

    print("\n検証1: profinite整合性の数値検証...")
    consistency = verify_profinite_consistency(K_max=6)
    for K, r in consistency.items():
        print(f"  K={K}: {r['total_tests']} tests, failures={r['failures']}, consistent={r['consistent']}")

    print("\n検証2: delta_K と Syracuse の整合性...")
    delta_syr = verify_delta_vs_syracuse(K_max=5, N=10000)
    for K, r in delta_syr.items():
        print(f"  K={K}: match_rate={r['match_rate']} ({r['matches']}/{r['total_tests']})")

    print("\n検証3: Mealy遷移の決定性...")
    determinism = analyze_mealy_determinism(K_max=4)
    for K, r in determinism.items():
        print(f"  K={K}: det_ratio={r['determinism_ratio']}, avg_j={r['avg_num_j_per_state']}")

    print("\n検証4: 代数的構造の検証...")
    algebra = analyze_algebraic_structure(K_max=5)
    for K, r in algebra.items():
        print(f"  K={K}: linear_consistent={r['linear_part_consistent']}, inv_consistent={r['inverse_consistent']}")

    print("\n検証5: 射影極限の具体例...")
    proj_limit = analyze_projective_limit(K_max=5, num_elements=10)
    coherent_count = sum(1 for r in proj_limit.values() if r["projective_coherent"])
    total_count = len(proj_limit)
    print(f"  {coherent_count}/{total_count} elements are projective coherent")

    print("\n検証6: Lean形式化設計...")
    design = design_lean_formalization()
    print(f"  Target: {design['target_theorem']}")
    print(f"  Proof steps: {len(design['proof_structure'])}")
    print(f"  Challenges: {len(design['challenges'])}")

    print("\n検証7: 入力 j の分布分析...")
    j_dist = analyze_input_j_distribution(K_max=4, N=30000)
    for K, r in j_dist.items():
        print(f"  K={K}: unique_j_ratio={r['unique_j_ratio']} ({r['states_with_unique_j']}/{r['total_odd_states']})")

    # 統合結果
    final_results = {
        "exploration_id": 186,
        "title": "Profinite整合性 delta_{K+1} mod 3^K = delta_K の形式化設計",
        "verification_1_profinite_consistency": consistency,
        "verification_2_delta_vs_syracuse": delta_syr,
        "verification_3_mealy_determinism": determinism,
        "verification_4_algebraic_structure": algebra,
        "verification_5_projective_limit": proj_limit,
        "verification_6_lean_design": design,
        "verification_7_j_distribution": j_dist,
    }

    output_path = "/Users/soyukke/study/lean-unsolved/results/profinite_mealy_mod3k.json"
    with open(output_path, "w") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n結果を {output_path} に保存しました")
