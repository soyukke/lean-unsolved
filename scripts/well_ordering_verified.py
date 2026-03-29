"""
正確な等式検証: T^k(mod*q + r) = a*q + b が q >= 1 で成立するか確認。

前回 MISMATCH の原因: r=7 mod 128 では T^4 の v2 が q 依存。
r=7 mod 256 では T^4 の v2 が q に依存しない（mod が十分大きいため）。
"""

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m >> v2(m)

def verify_trace(mod, residue, steps_spec, verbose=True):
    """
    steps_spec: [(a, b)] -- T^1 = a1*q+b1, T^2 = a2*q+b2, ...
    各 q=0..99 で検証
    """
    all_ok = True
    for q in range(0, 100):
        n = mod * q + residue
        if n < 2:
            continue
        current = n
        for i, (a, b) in enumerate(steps_spec):
            current = syracuse(current)
            expected = a * q + b
            if current != expected:
                if verbose:
                    print(f"  MISMATCH at q={q}, step {i+1}: T^{i+1}({n}) = {current}, expected {expected}")
                all_ok = False
                break
    return all_ok

# r=7 (mod 256) の正確な追跡
print("=" * 70)
print("r=7 (mod 256): 正確な等式追跡の検証")
print("=" * 70)
print("n = 256q + 7")
print()

# 手計算:
# Step 1: 3(256q+7)+1 = 768q+22 = 2(384q+11)
# 384q+11: 384=128*3 偶数, 11 奇数 → 常に奇数. v2 = 1
# T(n) = 384q+11
print("Step 1: 3n+1 = 768q+22, v2(768q+22) = 1 + v2(384q+11)")
print("  384q+11: 偶数*q + 奇数 = 常に奇数 → v2 = 0")
print("  v2(768q+22) = 1, T(n) = 384q+11")
ok1 = verify_trace(256, 7, [(384, 11)], verbose=True)
print(f"  Step 1 検証: {'OK' if ok1 else 'FAIL'}")

# Step 2: 3(384q+11)+1 = 1152q+34 = 2(576q+17)
# 576q+17: 576=64*9 偶数, 17 奇数 → 常に奇数. v2 = 1
# T²(n) = 576q+17
print("\nStep 2: 3*(384q+11)+1 = 1152q+34, v2 = 1")
print("  576q+17: 偶数*q + 奇数 → 常に奇数")
print("  T²(n) = 576q+17")
ok2 = verify_trace(256, 7, [(384, 11), (576, 17)], verbose=True)
print(f"  Step 2 検証: {'OK' if ok2 else 'FAIL'}")

# Step 3: 3(576q+17)+1 = 1728q+52 = 4(432q+13)
# 432q+13: 432=16*27 偶数, 13 奇数 → 常に奇数. v2 = 2
# T³(n) = 432q+13
print("\nStep 3: 3*(576q+17)+1 = 1728q+52 = 4*(432q+13)")
print("  432q+13: 偶数*q + 奇数 → 常に奇数")
print("  v2 = 2, T³(n) = 432q+13")
ok3 = verify_trace(256, 7, [(384, 11), (576, 17), (432, 13)], verbose=True)
print(f"  Step 3 検証: {'OK' if ok3 else 'FAIL'}")

# Step 4: 3(432q+13)+1 = 1296q+40 = 8(162q+5)
# 162q+5: 162=2*81 偶数, 5 奇数 → 常に奇数. v2 = 3
# T⁴(n) = 162q+5
print("\nStep 4: 3*(432q+13)+1 = 1296q+40 = 8*(162q+5)")
print("  162q+5: 偶数*q + 奇数 → 常に奇数")
print("  v2 = 3, T⁴(n) = 162q+5")
ok4 = verify_trace(256, 7, [(384, 11), (576, 17), (432, 13), (162, 5)], verbose=True)
print(f"  Step 4 検証: {'OK' if ok4 else 'FAIL'}")

# 下降の確認
print(f"\nT⁴(n) = 162q+5 < 256q+7?")
print(f"  256-162=94, 7-5=2")
print(f"  94q > -2 → 常に成立 (q >= 0)")
print(f"  → T⁴(n) < n は n ≡ 7 (mod 256) で常に成立!")

# ======================================
# 他の verified ターゲットも検証
# ======================================
print("\n" + "=" * 70)
print("mod 256 での等式排除可能クラス (全て正確に検証)")
print("=" * 70)

targets_256 = []
for r in range(256):
    if r % 4 != 3:
        continue
    if r % 16 == 3 or r % 32 == 11 or r % 32 == 23:
        continue

    a, b = 256, r
    full_trace = []
    success = False
    for step in range(1, 15):
        num_a = 3 * a
        num_b = 3 * b + 1
        v = v2(num_b)
        if num_a % (2 ** v) != 0:
            break  # q 依存
        new_a = num_a // (2 ** v)
        new_b = num_b // (2 ** v)
        full_trace.append((new_a, new_b))
        if new_a < 256:
            success = True
            break
        a, b = new_a, new_b

    if success:
        # 数値検証
        ok = verify_trace(256, r, full_trace, verbose=False)
        if ok:
            last_a, last_b = full_trace[-1]
            k = len(full_trace)
            targets_256.append((r, k, last_a, last_b))
            print(f"  r={r:3d}: T^{k} = {last_a}q+{last_b} < 256q+{r}  [VERIFIED]")
        else:
            print(f"  r={r:3d}: T^{len(full_trace)} MISMATCH (検証失敗)")

print(f"\n合計: {len(targets_256)} / 32 クラスを等式で排除可能")
print(f"残存: {32 - len(targets_256)} クラス")

# 残存クラスの列挙
remaining = set(r for r in range(256) if r % 4 == 3 and r % 16 != 3 and r % 32 not in [11, 23])
eliminated = set(r for r, _, _, _ in targets_256)
still_remaining = sorted(remaining - eliminated)
print(f"\n残存クラス (mod 256): {still_remaining}")
print(f"残存クラスの mod 32 値: {sorted(set(r % 32 for r in still_remaining))}")

# ======================================
# Lean形式化設計: r=7 (mod 256)
# ======================================
print("\n" + "=" * 70)
print("Lean 形式化設計: minimal_counterexample_not_mod256_eq7")
print("=" * 70)
print("""
証明構造:

theorem minimal_counterexample_not_mod256_eq7 (n : ℕ) (h : isMinimalCounterexample n) :
    n % 256 ≠ 7 := by
  intro h256
  obtain ⟨q, hq⟩ : ∃ q, n = 256 * q + 7 := ⟨n / 256, by omega⟩
  -- 基本性質
  have hge := h.1
  have hnr := h.2.1
  have hmin := h.2.2
  have hodd := minimal_counterexample_odd n h

  -- T(n) の計算 (v2 = 1)
  -- n ≡ 3 (mod 4) なので syracuse_mod4_eq3 適用
  -- T(n) = (3n+1)/2 = (768q+22)/2 = 384q+11
  have hT1 : syracuse n = 384 * q + 11 := by
    rw [syracuse_mod4_eq3 n (by omega)]
    omega

  -- T(n) の性質
  have hT1_odd : syracuse n % 2 = 1 := by rw [hT1]; omega
  have hT1_ge1 : syracuse n ≥ 1 := by rw [hT1]; omega
  have hT1_mod4 : syracuse n % 4 = 3 := by rw [hT1]; omega

  -- T²(n) の計算 (v2 = 1)
  have hT2 : syracuse (syracuse n) = 576 * q + 17 := by
    rw [hT1, syracuse_mod4_eq3 (384 * q + 11) (by omega)]
    omega

  -- T²(n) の性質
  have hT2_odd : syracuse (syracuse n) % 2 = 1 := by rw [hT2]; omega
  have hT2_ge1 : syracuse (syracuse n) ≥ 1 := by rw [hT2]; omega
  have hT2_mod4 : syracuse (syracuse n) % 4 = 1 := by rw [hT2]; omega
  have hT2_gt1 : syracuse (syracuse n) > 1 := by rw [hT2]; omega

  -- T³(n) の計算 (v2 = 2, mod4 = 1 なので syracuse_of_mod8_eq1 を使う)
  -- ここが技術的ポイント: v2(3*(576q+17)+1) = v2(1728q+52) = 2
  -- syracuse_le_of_mod4_eq1 は不等式だけ
  -- 等式を使うには syracuse_of_mod4_eq1 か直接計算が必要

  -- ¬reachesOne の4段伝播
  have hnr1 : ¬reachesOne (syracuse n) := not_reachesOne_syracuse n hge hodd hnr
  have hnr2 : ¬reachesOne (syracuse (syracuse n)) :=
    not_reachesOne_syracuse (syracuse n) hT1_ge1 hT1_odd hnr1
  have hnr3 : ¬reachesOne (syracuse (syracuse (syracuse n))) :=
    not_reachesOne_syracuse (syracuse (syracuse n)) hT2_ge1 hT2_odd hnr2
  have hnr4 : ¬reachesOne (syracuse (syracuse (syracuse (syracuse n)))) :=
    not_reachesOne_syracuse ...  -- T³ の奇数性が必要

  -- T⁴(n) < n の証明
  have hT4_lt : syracuse (syracuse (syracuse (syracuse n))) < n := by
    -- T⁴ = 162q+5 < 256q+7 = n
    ...

  -- 最小性との矛盾
  exact hnr4 (hmin (syracuse (syracuse (syracuse (syracuse n)))) (by ...) hT4_lt)

必要な補助定理:
1. syracuse_mod4_eq3 (既存)
2. syracuse_of_mod4_eq1 等の等式版 (mod8情報が必要な場合)
3. v2 の正確な値に関する補題
""")

# Hensel.lean にどんな補題があるか確認用
print("\n依存するモジュール内の定理を確認する必要あり:")
print("  - Unsolved/Collatz/Hensel.lean: v2 関連の詳細補題")
print("  - Unsolved/Collatz/Structure.lean: syracuse の mod 計算")
