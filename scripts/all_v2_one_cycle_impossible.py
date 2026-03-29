"""
全v2=1サイクル不可能性の数学的検証とLean形式化設計

問題: もしSyracuse軌道が周期pのサイクルで、全ステップでv2=1なら
      T^p(n) = n を満たす正の奇数nは存在しない

証明の核心:
  全v2=1 ⟺ consecutiveAscents n p (hensel_general により n ≡ 2^{p+1}-1 mod 2^{p+1})
  既存定理 syracuse_iter_mul_formula:
    2^p * T^p(n) = 3^p * n + ascentConst p
  T^p(n) = n を代入:
    2^p * n = 3^p * n + ascentConst p
  移項: n * (2^p - 3^p) = ascentConst p = 3^p - 2^p
  つまり: n * (2^p - 3^p) = -(2^p - 3^p)  [整数として]

  p >= 1 のとき 3^p > 2^p なので 2^p - 3^p < 0
  自然数では: 3^p - 2^p = n * (3^p - 2^p) が必要
  したがって n = 1

  しかし n=1 が周期pの全v2=1サイクルに属するか確認:
  consecutiveAscents 1 p ⟺ 1 % 2^{p+1} = 2^{p+1} - 1
  p >= 1 のとき 2^{p+1} >= 4 なので 1 ≠ 2^{p+1} - 1 (p >= 1)
  よって矛盾。
"""

def verify_math():
    """数学的な検証"""
    print("=== 全v2=1サイクル不可能性の検証 ===\n")

    # 1. ascentConst k = 3^k - 2^k の確認
    print("1. ascentConst の値確認:")
    for k in range(1, 10):
        ac = 3**k - 2**k
        print(f"   ascentConst({k}) = 3^{k} - 2^{k} = {3**k} - {2**k} = {ac}")

    # 2. サイクル方程式の検証
    print("\n2. サイクル方程式 2^p * n = 3^p * n + (3^p - 2^p) の解:")
    for p in range(1, 10):
        # 2^p * n = 3^p * n + (3^p - 2^p)
        # n * (2^p - 3^p) = 3^p - 2^p
        # n = (3^p - 2^p) / (2^p - 3^p) = -1
        lhs_coeff = 2**p - 3**p   # 自然数では負
        rhs = 3**p - 2**p         # 正
        print(f"   p={p}: n * ({lhs_coeff}) = {rhs}")
        print(f"         n = {rhs}/{lhs_coeff} = {rhs/lhs_coeff}")
        # 整数としては n = -1

    # 3. 自然数での議論
    print("\n3. 自然数の議論:")
    print("   2^p * n = 3^p * n + (3^p - 2^p)")
    print("   p >= 1 のとき 3^p > 2^p なので右辺 > 3^p * n")
    print("   つまり 2^p * n > 3^p * n は不可能 (n > 0 のとき 2^p < 3^p)")
    print("   実際、左辺 < 右辺の第一項のみ なので等式は成り立たない")

    # 4. Lean形式化の方向性確認
    print("\n4. Lean形式化での議論:")
    print("   syracuse_iter_mul_formula: 2^p * T^p(n) = 3^p * n + ascentConst p")
    print("   T^p(n) = n を代入: 2^p * n = 3^p * n + ascentConst p")
    print("   ascentConst p = 3^p - 2^p >= 1 (p >= 1)")
    print("   したがって 2^p * n >= 3^p * n + 1")
    print("   しかし p >= 1 なら 2^p < 3^p なので 2^p * n < 3^p * n (n >= 1)")
    print("   矛盾！")

    # 5. ascentConst >= 1 の確認
    print("\n5. ascentConst p >= 1 (p >= 1) の確認:")
    for p in range(1, 15):
        ac = 3**p - 2**p
        print(f"   ascentConst({p}) = {ac} >= 1: {ac >= 1}")

    # 6. n=1 の場合の直接検証
    print("\n6. n=1 がconsecutiveAscentsを満たすか:")
    print("   consecutiveAscents 1 p ⟺ 1 % 2^{p+1} = 2^{p+1} - 1")
    for p in range(1, 8):
        mod_val = 2**(p+1)
        expected = mod_val - 1
        actual = 1 % mod_val
        print(f"   p={p}: 1 % {mod_val} = {actual}, 必要値 = {expected}, 一致: {actual == expected}")


def lean_proof_design():
    """Lean形式化の設計"""
    print("\n\n=== Lean形式化設計 ===\n")

    print("--- 定理文 ---")
    print("""
/-- 全v2=1サイクルの不存在:
    周期 p >= 1 の Syracuse サイクルで全ステップが v2=1 (連続上昇) なら矛盾 -/
theorem no_all_v2_one_cycle (n p : Nat) (hn : n >= 1) (hodd : n % 2 = 1)
    (hp : p >= 1) (hasc : consecutiveAscents n p)
    (hcycle : syracuseIter p n = n) : False
""")

    print("--- 証明戦略 ---")
    print("""
証明戦略: 2つの不等式の矛盾

ステップ1: syracuse_iter_mul_formula を適用
  have hmul := syracuse_iter_mul_formula n p hn hodd hasc
  -- hmul : 2^p * syracuseIter p n = 3^p * n + ascentConst p

ステップ2: hcycle (T^p(n) = n) で書き換え
  rw [hcycle] at hmul
  -- hmul : 2^p * n = 3^p * n + ascentConst p

ステップ3: ascentConst p >= 1 を示す
  have hac_pos : ascentConst p >= 1
  -- ascentConst_closed と hp から

ステップ4: 3^p > 2^p を示す (p >= 1)
  have h32 : 3^p > 2^p
  -- three_pow_ge_two_pow の強化版、または ascentConst_add_two_pow から

ステップ5: 矛盾を導く
  -- hmul: 2^p * n = 3^p * n + ascentConst p
  -- 左辺 = 2^p * n
  -- 右辺 >= 3^p * n + 1 > 2^p * n (n >= 1, p >= 1)
  -- omega で閉じる
""")

    print("--- 必要な補助補題 ---")
    print("""
補題1: ascentConst_pos (p >= 1 なら ascentConst p >= 1)
  -- ascentConst_closed: ascentConst p = 3^p - 2^p
  -- p >= 1 なら 3^p >= 3 > 2 = 2^1 <= 2^p ... いや3^1 > 2^1だが
  -- 実は 3^p > 2^p は帰納法で示すか、ascentConst_add_two_pow から
  -- ascentConst p + 2^p = 3^p かつ 3^p > 2^p (p >= 1) から
  -- ascentConst p = 3^p - 2^p >= 1

補題2: three_pow_gt_two_pow (p >= 1 なら 3^p > 2^p)
  -- 既存の three_pow_ge_two_pow は >=
  -- p >= 1 での strict版が必要
  -- 帰納法: p=1 で 3 > 2, p+1 で 3*3^p > 3*2^p > 2*2^p (3^p > 2^p)
  -- あるいは ascentConst_add_two_pow から直接:
  --   ascentConst p + 2^p = 3^p
  --   ascentConst p >= 1 (帰納法 or 直接計算)
""")

    print("--- 完全なLean証明コード案 ---")
    print("""
/-- p >= 1 なら 3^p > 2^p -/
theorem three_pow_gt_two_pow (p : Nat) (hp : p >= 1) : 3 ^ p > 2 ^ p := by
  have h := ascentConst_add_two_pow p
  -- h : ascentConst p + 2^p = 3^p
  -- ascentConst p >= 1 を示せば done
  suffices ascentConst p >= 1 by omega
  induction p with
  | zero => omega
  | succ k _ =>
    simp only [ascentConst]
    -- 3 * ascentConst k + 2^k >= 1
    -- 2^k >= 1 なので自明
    have : 2 ^ k >= 1 := Nat.one_le_pow k 2 (by omega)
    omega

/-- 全v2=1サイクルの不存在 (公理なし、直接証明) -/
theorem no_all_v2_one_cycle (n p : Nat) (hn : n >= 1) (hodd : n % 2 = 1)
    (hp : p >= 1) (hasc : consecutiveAscents n p)
    (hcycle : syracuseIter p n = n) : False := by
  -- ステップ1: 一般公式の適用
  have hmul := syracuse_iter_mul_formula n p hn hodd hasc
  -- hmul : 2^p * syracuseIter p n = 3^p * n + ascentConst p
  -- ステップ2: サイクル条件で書き換え
  rw [hcycle] at hmul
  -- hmul : 2^p * n = 3^p * n + ascentConst p
  -- ステップ3: 矛盾を導く
  have h32 : 3 ^ p > 2 ^ p := three_pow_gt_two_pow p hp
  have hac : ascentConst p + 2 ^ p = 3 ^ p := ascentConst_add_two_pow p
  -- hmul: 2^p * n = 3^p * n + ascentConst p
  -- 右辺 = 3^p * n + (3^p - 2^p) >= 3^p * n + 1 > 2^p * n
  -- omega で閉じるはず
  omega
""")

    print("--- 証明の行数見積もり ---")
    print("""
  three_pow_gt_two_pow: 約8行
  no_all_v2_one_cycle: 約12行
  合計: 約20行 (+ コメント10行 = 30行程度)
""")

    print("--- 代替アプローチ: IsSyracuseCycleとの統合 ---")
    print("""
既存のIsSyracuseCycle定義:
  def IsSyracuseCycle (k n : Nat) : Prop :=
    k > 0 /\\ n > 0 /\\ n % 2 = 1 /\\ syracuseIter k n = n

統合版定理:
/-- 全v2=1の Syracuse サイクルは存在しない (公理不要) -/
theorem no_all_v2_one_syracuse_cycle (k n : Nat)
    (hcycle : IsSyracuseCycle k n)
    (hasc : consecutiveAscents n k) : False := by
  obtain ⟨hk, hn, hodd, hiter⟩ := hcycle
  exact no_all_v2_one_cycle n k hn hodd hk hasc hiter
""")

    print("--- 既存定理との関係整理 ---")
    print("""
  依存する既存定理:
  1. syracuse_iter_mul_formula (Formula.lean)
     前提: n >= 1, n % 2 = 1, consecutiveAscents n k
     結論: 2^k * syracuseIter k n = 3^k * n + ascentConst k

  2. ascentConst_add_two_pow (Formula.lean)
     結論: ascentConst k + 2^k = 3^k

  3. ascentConst (Formula.lean)
     定義: ascentConst 0 = 0, ascentConst (k+1) = 3 * ascentConst k + 2^k

  使わない（不要な）もの:
  - baker_cycle_bound (Bakerの定理の公理)
  - hensel_general (直接は不要、hasc が前提に入っているため)
  - ascentConst_closed (omegaで十分)
""")

    print("--- 数学的意義 ---")
    print("""
  この定理の価値:
  1. 公理を一切使わない純粋な証明（baker_cycle_bound不要）
  2. Syracuse cycle問題の最も単純なケースの完全排除
  3. 「全ステップ上昇のサイクルは不可能」という直観的に自明な事実の形式化
  4. 既存のsyracuse_iter_mul_formulaとascentConst_add_two_powの
     自然な応用で、わずか20行で証明可能
  5. 将来の「上昇率r/pのサイクル排除」への足がかり
     (r=pの場合 = 全v2=1 が今回の定理)

  制約:
  - 全ステップv2=1のサイクルのみ排除
  - 一般的なサイクル排除にはBakerの定理が依然必要
  - しかし、証明のパターンは一般ケースへの示唆を含む
""")


def verify_omega_feasibility():
    """omegaで閉じるかの確認"""
    print("\n\n=== omega可能性の検証 ===\n")

    # omega が処理する形: 線形算術
    # hmul: 2^p * n = 3^p * n + ascentConst p
    # hac: ascentConst p + 2^p = 3^p
    # h32: 3^p > 2^p
    # hn: n >= 1

    # 変数を具体的に置く: a = 2^p, b = 3^p, c = ascentConst p
    # hmul: a * n = b * n + c
    # hac: c + a = b
    # h32: b > a
    # hn: n >= 1

    # omegaで: a*n = b*n + c, c + a = b, b > a, n >= 1
    # c = b - a, b > a より c >= 1
    # a*n = b*n + c = b*n + b - a
    # a*n + a = b*n + b = b*(n+1)
    # a*(n+1) = b*(n+1) [... いやこれは違う]
    # a*n = b*n + c
    # a*n - b*n = c (自然数の引き算は注意)
    # しかし a < b なので a*n < b*n (n >= 1)
    # よって a*n = b*n + c は不可能 (c >= 0 では右辺 >= 左辺の厳密不等式)

    # もっと正確に:
    # b*n >= a*n + 1 (b > a, n >= 1 なので b*n >= a*n + n >= a*n + 1)
    # b*n + c >= a*n + 1 + c >= a*n + 1
    # しかし hmul は a*n = b*n + c
    # 左辺 = a*n, 右辺 >= a*n + 1
    # 矛盾

    print("omega が閉じる条件:")
    print("  仮説: a * n = b * n + c, c + a = b, b > a, n >= 1")
    print("  c = b - a >= 1")
    print("  右辺 = b * n + c >= (a+1) * n + 1 = a*n + n + 1 >= a*n + 2")
    print("  左辺 = a * n < a*n + 2")
    print("  矛盾！ omega は線形算術なのでこれを解決可能")

    # omegaの限界: 2^p, 3^p は非線形
    # しかし、仮説にすでに具体的な値として入っているので問題なし
    # hmul, hac, h32 の3つの仮説から omega で閉じるはず

    print("\n  注意: 2^p, 3^p は仮説中の具体値として扱われるため")
    print("  omega は線形算術として処理可能")
    print("  → omega で閉じると期待される")

    # 検証: 具体的な p でチェック
    print("\n  具体的検証:")
    for p in range(1, 8):
        a = 2**p
        b = 3**p
        c = b - a  # ascentConst
        print(f"  p={p}: 2^p={a}, 3^p={b}, ascentConst={c}")
        print(f"    等式 {a}*n = {b}*n + {c} が n>=1 で成り立つか?")
        # a*n = b*n + c → (a-b)*n = c → n = c/(a-b) = c/(-(b-a)) = -c/(b-a) = -1
        print(f"    n = {c}/({a}-{b}) = {c}/{a-b} = {c/(a-b)} → 自然数に解なし")


if __name__ == "__main__":
    verify_math()
    lean_proof_design()
    verify_omega_feasibility()
