"""
探索179: 一般乗法公式の完全Lean 4形式化設計

帰納ステップの各calcステップとLean式の完全な対応を記述。
"""

# まず帰納ステップの代数的検証
def verify_induction_step():
    """
    帰納ステップの代数変形を記号的に検証する

    設定:
      m = T^k(n)  (固定)
      v = v2(3m+1)
      S_k = totalV2 n k
      C_k = generalConst n k

    IH: 2^{S_k} * m = 3^k * n + C_k

    定義:
      S_{k+1} = S_k + v
      C_{k+1} = 3 * C_k + 2^{S_k}

    目標: 2^{S_{k+1}} * T(m) = 3^{k+1} * n + C_{k+1}

    syracuse_mul_pow_v2: T(m) * 2^v = 3m+1
      → 2^v * T(m) = 3m+1  (by mul_comm)

    LHS = 2^{S_k + v} * T(m)
        = 2^{S_k} * 2^v * T(m)        [pow_add]
        = 2^{S_k} * (2^v * T(m))      [mul_assoc]
        = 2^{S_k} * (3m + 1)          [syracuse_mul_pow_v2 rewritten]
        = 2^{S_k} * (3 * m + 1)
        = 3 * (2^{S_k} * m) + 2^{S_k} [ring/nlinarith]
        = 3 * (3^k * n + C_k) + 2^{S_k}  [IH]
        = 3^{k+1} * n + 3 * C_k + 2^{S_k}  [ring]
        = 3^{k+1} * n + C_{k+1}       [generalConst_succ]
    """
    # 記号的な検証（具体値で）
    # n=7, k=2: T^2(7)=17, S_2=2, C_2=5
    # v = v2(3*17+1) = v2(52) = 2
    # S_3 = 2+2 = 4, C_3 = 3*5+4 = 19
    # T(17) = syracuse(17) = 52/4 = 13
    # LHS: 2^4 * 13 = 16 * 13 = 208
    # RHS: 3^3 * 7 + 19 = 189 + 19 = 208 ✓

    # 帰納ステップの各行を検証
    n, k = 7, 2
    m = 17  # T^2(7)
    Sk = 2
    Ck = 5
    v = 2  # v2(52)

    # IH
    assert 2**Sk * m == 3**k * n + Ck, "IH failed"

    # Step by step
    step1 = 2**(Sk+v) * 13  # T(m) = syracuse(17) = 13
    step2 = 2**Sk * 2**v * 13
    assert step1 == step2, "pow_add failed"

    step3 = 2**Sk * (2**v * 13)
    assert step2 == step3, "mul_assoc failed"

    step4 = 2**Sk * (3*m + 1)
    assert step3 == step4, f"syracuse_mul_pow_v2 failed: {step3} vs {step4}"

    step5 = 3 * (2**Sk * m) + 2**Sk
    assert step4 == step5, f"ring failed: {step4} vs {step5}"

    step6 = 3 * (3**k * n + Ck) + 2**Sk
    assert step5 == step6, "IH substitution failed"

    step7 = 3**(k+1) * n + 3*Ck + 2**Sk
    assert step6 == step7, "ring failed"

    Ck1 = 3*Ck + 2**Sk
    step8 = 3**(k+1) * n + Ck1
    assert step7 == step8, "generalConst_succ failed"

    print(f"帰納ステップ検証 (n={n}, k={k}): 全ステップ OK")
    print(f"  m=T^{k}(n)={m}, v=v2(3m+1)={v}, S_k={Sk}, C_k={Ck}")
    print(f"  S_{{k+1}}={Sk+v}, C_{{k+1}}={Ck1}")
    print(f"  LHS=2^{Sk+v}*T(m)={step1}, RHS=3^{k+1}*n+C_{{k+1}}={step8}")

verify_induction_step()

# 追加検証: さまざまな n, k で帰納ステップを検証
print()
print("追加検証:")

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    m = 3*n+1
    return m // (2**v2(m))

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

for n in [3, 5, 7, 9, 11, 13, 15, 27, 31]:
    cur = n
    Sk = 0
    Ck = 0
    for k in range(6):
        # Verify IH at this k
        m = syracuse_iter(k, n)
        assert 2**Sk * m == 3**k * n + Ck, f"n={n},k={k}: IH failed"

        # Compute next step quantities
        v = v2(3*m+1)
        Tm = syracuse(m)
        Sk1 = Sk + v
        Ck1 = 3*Ck + 2**Sk

        # Verify induction step
        lhs = 2**Sk1 * Tm
        rhs = 3**(k+1) * n + Ck1
        assert lhs == rhs, f"n={n},k={k}: induction step failed"

        # Verify intermediate steps
        assert 2**Sk * (2**v * Tm) == 2**Sk * (3*m+1), \
            f"n={n},k={k}: syracuse_mul_pow_v2 step failed"
        assert 2**Sk * (3*m+1) == 3*(2**Sk * m) + 2**Sk, \
            f"n={n},k={k}: ring step failed"

        Sk = Sk1
        Ck = Ck1
        cur = Tm

    print(f"  n={n:3d}: k=0..5 全ステップ OK")

print()
print("=" * 70)
print("完全な Lean 4 証明コード設計:")
print("=" * 70)

lean_code = r"""
-- ====================================================================
-- 探索179: Syracuse反復の一般乗法公式
-- ====================================================================
-- import Unsolved.Collatz.Structure

/-!
# Syracuse反復の一般乗法公式（consecutiveAscents不要）

## 主結果
  2^{totalV2 n k} * syracuseIter k n = 3^k * n + generalConst n k

  ここで:
  - totalV2 n k := sum of v2(3 * T^i(n) + 1) for i = 0..k-1
  - generalConst n 0 := 0
  - generalConst n (k+1) := 3 * generalConst n k + 2^{totalV2 n k}

## 既存公式との関係
  consecutiveAscents n k のとき v2(3*T^i(n)+1)=1 (i<k) なので:
  - totalV2 n k = k
  - generalConst n k = ascentConst k = 3^k - 2^k
  本定理はその制限を完全に除去した一般版。
-/

/-! ## 1. 定義 -/

/-- 累積2-adic付値: Σ_{i=0}^{k-1} v2(3 * T^i(n) + 1) -/
def totalV2 (n : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => totalV2 n k + v2 (3 * syracuseIter k n + 1)

/-- 一般化定数項: C_0 = 0, C_{k+1} = 3 * C_k + 2^{S_k(n)} -/
def generalConst (n : ℕ) : ℕ → ℕ
  | 0 => 0
  | k + 1 => 3 * generalConst n k + 2 ^ totalV2 n k

/-! ## 2. 展開補題 -/

@[simp] theorem totalV2_zero (n : ℕ) : totalV2 n 0 = 0 := rfl

@[simp] theorem totalV2_succ (n k : ℕ) :
    totalV2 n (k + 1) = totalV2 n k + v2 (3 * syracuseIter k n + 1) := rfl

@[simp] theorem generalConst_zero (n : ℕ) : generalConst n 0 = 0 := rfl

@[simp] theorem generalConst_succ (n k : ℕ) :
    generalConst n (k + 1) = 3 * generalConst n k + 2 ^ totalV2 n k := rfl

/-! ## 3. 補助定理: syracuse_mul_pow_v2 の左掛け版 -/

/-- 2^{v2(3n+1)} * syracuse(n) = 3n+1 (syracuse_mul_pow_v2のmul_comm) -/
theorem pow_v2_mul_syracuse (n : ℕ) :
    2 ^ v2 (3 * n + 1) * syracuse n = 3 * n + 1 := by
  rw [mul_comm]
  exact syracuse_mul_pow_v2 n

/-! ## 4. 主定理 -/

/-- ★ Syracuse反復の一般乗法公式（consecutiveAscents不要）:
    2^{totalV2 n k} * syracuseIter k n = 3^k * n + generalConst n k

    依存定理: syracuse_mul_pow_v2, syracuseIter_odd, syracuseIter_pos -/
theorem syracuse_iter_general_mul (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :
    2 ^ totalV2 n k * syracuseIter k n = 3 ^ k * n + generalConst n k := by
  induction k with
  | zero =>
    simp [totalV2, generalConst, syracuseIter]
  | succ k ih =>
    -- 展開: T^{k+1}(n) = T(T^k(n)), S_{k+1} = S_k + v_k, C_{k+1} = 3*C_k + 2^{S_k}
    simp only [syracuseIter_succ, totalV2_succ, generalConst_succ]
    -- set m := syracuseIter k n (= T^k(n))
    set m := syracuseIter k n with hm_def
    set v := v2 (3 * m + 1) with hv_def
    set Sk := totalV2 n k with hSk_def
    -- ih: 2^{S_k} * m = 3^k * n + generalConst n k
    -- 目標: 2^{S_k + v} * syracuse m = 3^{k+1} * n + (3 * generalConst n k + 2^{S_k})
    calc 2 ^ (Sk + v) * syracuse m
        = 2 ^ Sk * 2 ^ v * syracuse m := by rw [pow_add]
      _ = 2 ^ Sk * (2 ^ v * syracuse m) := by rw [mul_assoc]
      _ = 2 ^ Sk * (3 * m + 1) := by rw [pow_v2_mul_syracuse]
      _ = 3 * (2 ^ Sk * m) + 2 ^ Sk := by ring
      _ = 3 * (3 ^ k * n + generalConst n k) + 2 ^ Sk := by rw [ih]
      _ = 3 ^ (k + 1) * n + (3 * generalConst n k + 2 ^ Sk) := by ring

/-! ## 5. 系: 加法的代替公式 -/

/-- 一般公式の加法形式: generalConst n k + 2^{totalV2 n k} = ?
    注意: consecutiveAscents 版では C_k + 2^k = 3^k だが、
    一般の場合 C_k(n) + 2^{S_k(n)} = 3^k * (n+1) ではない。 -/

/-! ## 6. 系: 既存公式の特殊ケースとしての再導出 -/

-- consecutiveAscents n k のとき totalV2 n k = k を示す定理は
-- v2_three_mul_add_one_of_mod4_eq3 を使って
-- 各ステップで v2 = 1 を示す必要がある。これは将来の探索課題。

/-! ## 7. 数値検証 -/

-- k=1, n=9: 2^2 * 7 = 28, 3*9 + 1 = 28
-- totalV2 9 1 = v2(28) = 2, generalConst 9 1 = 2^0 = 1
-- 2^2 * 7 = 28 = 3*9 + 1 ✓

-- k=2, n=27: totalV2 27 2 = 1 + 2 = 3, generalConst 27 2 = 3*1 + 2^1 = 5
-- 2^3 * 31 = 248 = 9*27 + 5 ✓
"""

print(lean_code)

print()
print("=" * 70)
print("要点まとめ:")
print("=" * 70)
print()
print("1. 新定義2つ: totalV2, generalConst")
print("   - n を引数に持つが、k に関して再帰的に定義")
print("   - syracuseIter k n を内部で使用")
print()
print("2. 補助定理1つ: pow_v2_mul_syracuse")
print("   - syracuse_mul_pow_v2 の mul_comm 版")
print("   - calc チェーンの中核")
print()
print("3. 主定理: syracuse_iter_general_mul")
print("   - k に関する帰納法（n は固定、generalizing n 不要）")
print("   - 帰納ステップは6行のcalcチェーン")
print("   - 各行で使うタクティク: pow_add, mul_assoc, pow_v2_mul_syracuse, ih, ring")
print()
print("4. 証明の困難度: 低")
print("   - 全体で約40行")
print("   - 使うタクティク: simp, rw, ring, calc")
print("   - sorry なし")
print("   - 既存定理への依存は最小限 (syracuse_mul_pow_v2 のみ)")
print()
print("5. 数学的意義: 中")
print("   - consecutiveAscents 制限の完全除去")
print("   - 任意の奇数 n, 任意のステップ数 k に適用可能")
print("   - 将来の自動化・大域的分析の基盤")
