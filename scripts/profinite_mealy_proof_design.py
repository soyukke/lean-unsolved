"""
探索186 (続): profinite整合性の証明構造の詳細設計

核心: delta_{K+1}(R, j) mod 3^K = delta_K(R mod 3^K, j)
     where delta_K(R, j) = (3R+1) * 2^{-j} mod 3^K

証明の本質: 3つの環準同型の性質に帰着:
  1. castHom(3R+1) = 3*castHom(R)+1  (環準同型は加法・乗法を保存)
  2. castHom(2^j) = 2^j              (環準同型は pow を保存)
  3. castHom(u^{-1}) = castHom(u)^{-1} (環準同型は可逆元の逆を保存)

Nat版の証明では:
  1. (3R+1) % 3^K = (3*(R%3^K)+1) % 3^K
  2. (inv(2^j, 3^{K+1})) % 3^K = inv(2^j, 3^K)
  3. (a * b) % m = ((a%m) * (b%m)) % m
"""

import json

def design_nat_proof():
    """Nat版の証明設計（ZModを使わない）"""

    lemmas = []

    # Lemma 1: 線形部分の整合性
    lemmas.append({
        "name": "three_mul_add_one_mod_pow3_consistent",
        "statement": """
theorem three_mul_add_one_mod_pow3_consistent (K R : ℕ) :
    (3 * R + 1) % 3 ^ K = (3 * (R % 3 ^ K) + 1) % 3 ^ K
""",
        "proof_idea": "Nat.add_mul_mod_self or omega on R = (R%3^K) + 3^K*(R/3^K)",
        "proof_sketch": """
  have hR : R = R % 3^K + 3^K * (R / 3^K) := (Nat.mod_add_div R (3^K)).symm
  calc (3 * R + 1) % 3^K
      = (3 * (R % 3^K + 3^K * (R / 3^K)) + 1) % 3^K := by rw [hR]
    _ = (3 * (R % 3^K) + 1 + 3 * 3^K * (R / 3^K)) % 3^K := by ring_nf
    _ = (3 * (R % 3^K) + 1) % 3^K := by rw [Nat.add_mul_mod_self_right]
  -- 注: ring_nf と Nat.add_mul_mod_self が使える形に変形する必要がある
  -- 代替: omega で直接
""",
        "difficulty": "easy",
        "existing_tools": "omega, Nat.mod_add_div, Nat.add_mul_mod_self"
    })

    # Lemma 2: 逆元の整合性
    lemmas.append({
        "name": "pow2_inv_mod_pow3_consistent",
        "statement": """
-- 2^j の逆元が 3^{K+1} と 3^K で整合する
-- i.e., if t * 2^j ≡ 1 (mod 3^{K+1}), then t % 3^K * 2^j ≡ 1 (mod 3^K)
-- equivalently: inv(2^j, 3^{K+1}) % 3^K = inv(2^j, 3^K)
theorem pow2_inv_mod_pow3_consistent (K j : ℕ) (hK : K ≥ 1)
    (t : ℕ) (ht : t * 2^j % 3^(K+1) = 1) :
    t % 3^K * 2^j % 3^K = 1 % 3^K
""",
        "proof_idea": (
            "t * 2^j ≡ 1 (mod 3^{K+1}) implies t * 2^j ≡ 1 (mod 3^K) "
            "because 3^K | 3^{K+1}. Then (t % 3^K) * 2^j ≡ t * 2^j ≡ 1 (mod 3^K)."
        ),
        "proof_sketch": """
  -- Step 1: 3^K | 3^{K+1}
  have hdvd : 3^K ∣ 3^(K+1) := dvd_pow_self 3 (by omega)
  -- Step 2: t * 2^j ≡ 1 (mod 3^K) from t * 2^j ≡ 1 (mod 3^{K+1})
  have h_mod_K : t * 2^j % 3^K = 1 % 3^K := by
    calc t * 2^j % 3^K
        = (t * 2^j % 3^(K+1)) % 3^K := by rw [Nat.mod_mod_of_dvd _ (Or.inr hdvd)]
      _ = 1 % 3^K := by rw [ht]
  -- Step 3: (t % 3^K) * 2^j % 3^K = t * 2^j % 3^K
  rw [Nat.mul_mod, Nat.mod_mod_of_dvd, ← Nat.mul_mod]
  exact h_mod_K
""",
        "difficulty": "medium",
        "existing_tools": "Nat.mod_mod_of_dvd, Nat.mul_mod"
    })

    # Lemma 3: 乗法の整合性 (既存)
    lemmas.append({
        "name": "mul_mod_consistent",
        "statement": """
-- (a * b) % m = ((a % m) * (b % m)) % m
-- This is Nat.mul_mod from Mathlib
""",
        "proof_idea": "This is Nat.mul_mod, already in Mathlib.",
        "difficulty": "trivial (existing)"
    })

    # Main theorem
    main_theorem = {
        "name": "profinite_consistency_nat",
        "statement": """
/-- Mealy機械族の profinite 整合性:
    delta_{K+1}(R, j) mod 3^K = delta_K(R mod 3^K, j)
    ここで delta_K(R, j) = (3R+1) * inv(2^j) mod 3^K -/
theorem profinite_consistency_nat (K R j : ℕ) (hK : K ≥ 1)
    (inv_K : ℕ) (hinv_K : inv_K * 2^j % 3^K = 1)
    (inv_K1 : ℕ) (hinv_K1 : inv_K1 * 2^j % 3^(K+1) = 1) :
    ((3 * R + 1) * inv_K1 % 3^(K+1)) % 3^K
    = (3 * (R % 3^K) + 1) * inv_K % 3^K
""",
        "proof_outline": """
  -- Step 1: Reduce LHS modulo 3^K
  -- ((3R+1) * inv_K1) % 3^{K+1} % 3^K = ((3R+1) * inv_K1) % 3^K
  --   by Nat.mod_mod_of_dvd (since 3^K | 3^{K+1})

  -- Step 2: Factor modular arithmetic
  -- ((3R+1) * inv_K1) % 3^K = ((3R+1) % 3^K) * (inv_K1 % 3^K) % 3^K
  --   by Nat.mul_mod

  -- Step 3: Use three_mul_add_one_mod_pow3_consistent
  -- (3R+1) % 3^K = (3*(R%3^K)+1) % 3^K

  -- Step 4: Use pow2_inv_mod_pow3_consistent
  -- inv_K1 % 3^K behaves like inv_K modulo 3^K
  --   (since inv_K1 * 2^j ≡ 1 mod 3^{K+1} implies inv_K1 * 2^j ≡ 1 mod 3^K)
  --   and the inverse mod 3^K is unique (if it exists)

  -- Step 5: Reassemble
  -- ((3*(R%3^K)+1) % 3^K) * (inv_K1 % 3^K) % 3^K
  -- = (3*(R%3^K)+1) * (inv_K1 % 3^K) % 3^K
  -- Now: inv_K1 % 3^K is also an inverse of 2^j mod 3^K
  -- Since inverse is unique mod 3^K, inv_K1 % 3^K ≡ inv_K (mod 3^K)
  -- Actually we need: inv_K1 % 3^K * 2^j ≡ 1 (mod 3^K)
  -- and inv_K * 2^j ≡ 1 (mod 3^K)
  -- so (3*(R%3^K)+1) * (inv_K1 % 3^K) ≡ (3*(R%3^K)+1) * inv_K (mod 3^K)
  -- This requires uniqueness of inverse, or direct computation.
""",
        "key_insight": (
            "The proof has an inherent difficulty: even though inv_K1 % 3^K and inv_K "
            "are both inverses of 2^j mod 3^K, they might differ by multiples of 3^K. "
            "However, (a * b) % m only depends on (a % m) and (b % m), "
            "so we need to show inv_K1 % 3^K ≡ inv_K (mod 3^K). "
            "This follows from uniqueness of modular inverse."
        )
    }

    # ZMod版 (より簡潔)
    zmod_theorem = {
        "name": "profinite_consistency_zmod",
        "statement": """
/-- ZMod版: castHom は delta を保存する -/
theorem profinite_consistency_zmod (K : ℕ) (hK : K ≥ 1)
    (R : ZMod (3^(K+1))) (j : ℕ) :
    let π : ZMod (3^(K+1)) →+* ZMod (3^K) :=
      ZMod.castHom (dvd_pow_self 3 (show K ≤ K+1 from Nat.le_succ K)) _
    π ((3 * R + 1) * ((2:ZMod (3^(K+1)))^j)⁻¹)
    = (3 * (π R) + 1) * ((2:ZMod (3^K))^j)⁻¹
""",
        "proof": """
  intro π
  -- π is a ring homomorphism
  simp only [map_mul, map_add, map_mul, map_natCast, map_one, map_pow, map_inv₀]
  -- After simplification, both sides are syntactically equal
  -- because π(2) = 2, π(3) = 3, π(1) = 1 (castHom preserves these)
""",
        "advantages": [
            "Much shorter proof via ring homomorphism properties",
            "map_mul, map_add, map_pow, map_inv₀ do all the work",
            "No need to handle modular inverse uniqueness explicitly"
        ],
        "disadvantages": [
            "Requires ZMod infrastructure from Mathlib",
            "Need to ensure 2^j is a unit in ZMod(3^K)",
            "The map_inv₀ might need IsUnit hypothesis"
        ],
        "unit_proof": """
-- 2 is a unit in ZMod(3^K) because gcd(2, 3^K) = 1
theorem two_isUnit_zmod_pow3 (K : ℕ) (hK : K ≥ 1) :
    IsUnit (2 : ZMod (3^K)) := by
  rw [ZMod.isUnit_natCast_iff]
  simp [Nat.Coprime, Nat.gcd_comm]
  -- gcd(2, 3^K) = 1 since 3^K is odd
"""
    }

    # 追加の解析: inv_K1 % 3^K = inv_K の証明
    uniqueness_lemma = {
        "name": "modular_inverse_unique_proj",
        "statement": """
-- If a * b ≡ 1 (mod m*n) and a' * b ≡ 1 (mod m), then a % m ≡ a' (mod m)
-- (Uniqueness of modular inverse under projection)
theorem modular_inverse_unique_proj (a a' b m n : ℕ) (hm : m > 0)
    (h1 : a * b % (m * n) = 1) (h2 : a' * b % m = 1)
    (hmn : m ∣ (m * n)) :
    (a % m) * b % m = 1
""",
        "proof_idea": (
            "From a*b ≡ 1 (mod m*n) and m | m*n, we get a*b ≡ 1 (mod m). "
            "Then (a%m)*b ≡ a*b ≡ 1 (mod m). "
            "Since a' is also an inverse, a ≡ a' (mod m). "
            "This means for the main theorem, we can replace inv_K1 % 3^K with inv_K."
        )
    }

    return {
        "lemmas": lemmas,
        "main_theorem_nat": main_theorem,
        "main_theorem_zmod": zmod_theorem,
        "uniqueness_lemma": uniqueness_lemma,
        "recommended_approach": "ZMod",
        "reason": (
            "The ZMod approach is dramatically simpler because "
            "the entire proof reduces to 'castHom is a ring homomorphism'. "
            "The ring homomorphism properties handle multiplication, addition, "
            "power, and inverse preservation automatically."
        ),
        "estimated_loc": {
            "ZMod_approach": "~30 lines (including definitions and unit proof)",
            "Nat_approach": "~80 lines (handling modular inverse uniqueness)",
        },
        "connection_to_existing": {
            "syracuse_mod3_eq": (
                "The K=1 case of profinite consistency implies: "
                "T(n) mod 3 depends only on n mod 3 and v2(3n+1). "
                "This is a generalization of syracuse_mod3_eq to arbitrary K."
            ),
            "hensel_attrition": (
                "The 2-adic structure (Hensel.lean) controls v2(3n+1), "
                "while the 3-adic structure (this theorem) controls the residue. "
                "Together they give a complete mod 2^a * 3^K description."
            )
        }
    }


def verify_inv_uniqueness_numerically():
    """逆元の一意性を数値的に検証"""
    results = []

    for K in range(1, 6):
        mod_K = 3 ** K
        mod_K1 = 3 ** (K + 1)

        for j in range(1, 10):
            p2 = pow(2, j)

            # inv mod 3^{K+1}
            inv_K1 = pow(p2, -1, mod_K1)
            # inv mod 3^K
            inv_K = pow(p2, -1, mod_K)

            # 検証: inv_K1 % 3^K == inv_K
            projected = inv_K1 % mod_K
            match = projected == inv_K

            if not match:
                results.append({
                    "K": K, "j": j,
                    "inv_K1": inv_K1, "inv_K": inv_K,
                    "inv_K1_mod_3K": projected,
                    "match": False
                })

    if not results:
        return {"all_match": True, "note": "inv(2^j, 3^{K+1}) % 3^K = inv(2^j, 3^K) for all tested K, j"}
    else:
        return {"all_match": False, "failures": results}


def analyze_connection_to_syracuse_mod3():
    """syracuse_mod3_eq との関連を明示的に検証"""

    print("\n--- syracuse_mod3_eq との関連 ---")
    print("K=1 の場合:")
    print("  delta_1(R, j) = (3R+1) * 2^{-j} mod 3")
    print("  3R+1 mod 3 = 1 (always)")
    print("  So delta_1(R, j) = 2^{-j} mod 3")
    print("  2^{-1} mod 3 = 2, 2^{-2} mod 3 = 1, 2^{-3} mod 3 = 2, ...")
    print("  = 2 if j odd, 1 if j even")
    print("  This is exactly syracuse_mod3_eq!")
    print()

    # 数値検証
    for j in range(1, 10):
        inv = pow(pow(2, j), -1, 3)
        expected = 2 if j % 2 == 1 else 1
        assert inv == expected, f"j={j}: inv={inv}, expected={expected}"
    print("  Verified: 2^{-j} mod 3 = (2 if j odd, 1 if j even) for j=1..9")

    # K=2 の場合
    print("\nK=2 の場合:")
    print("  delta_2(R, j) = (3R+1) * 2^{-j} mod 9")
    print("  3R+1 mod 9 depends on R mod 9")
    for R in [1, 3, 5, 7]:
        val = (3 * R + 1) % 9
        print(f"    R={R}: (3R+1) mod 9 = {val}")

    print("\n  2^{-j} mod 9:")
    for j in range(1, 8):
        inv = pow(pow(2, j), -1, 9)
        print(f"    j={j}: 2^{{-{j}}} mod 9 = {inv}")

    # K=2 での完全な遷移テーブル
    print("\n  Complete transition table for K=2 (mod 9):")
    mod = 9
    for R in range(1, mod, 2):
        for j in range(1, 7):
            val = (3 * R + 1) * pow(pow(2, j), -1, mod) % mod
            print(f"    delta_2({R}, {j}) = {val}", end="  ")
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("探索186 (続): 証明構造の詳細設計")
    print("=" * 70)

    # 逆元の一意性検証
    print("\n逆元の一意性 (inv(2^j, 3^{K+1}) % 3^K = inv(2^j, 3^K)):")
    inv_result = verify_inv_uniqueness_numerically()
    print(f"  {inv_result}")

    # syracuse_mod3_eq との関連
    analyze_connection_to_syracuse_mod3()

    # 証明設計
    design = design_nat_proof()

    print("\n" + "=" * 70)
    print("推奨アプローチ:", design["recommended_approach"])
    print("理由:", design["reason"])
    print()
    print("推定コード量:")
    for k, v in design["estimated_loc"].items():
        print(f"  {k}: {v}")

    print("\n既存形式化との接続:")
    for k, v in design["connection_to_existing"].items():
        print(f"  {k}: {v}")

    # 結果保存
    output_path = "/Users/soyukke/study/lean-unsolved/results/profinite_mealy_proof_design.json"
    with open(output_path, "w") as f:
        json.dump(design, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n結果を {output_path} に保存")
