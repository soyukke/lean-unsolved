"""
Well-ordering deeper analysis:
1. mod 32 で残存するのはどの剰余類か
2. mod 64 以上でさらに細分して排除可能なクラスを特定
3. Lean 形式化として最も証明しやすい次のターゲットを決定
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

# mod 32 で残存するクラスの特定
print("=== mod 32 の残存クラス ===")
for r in range(32):
    if r % 4 != 3:
        continue
    # 大きいqで試して、20ステップ以内に下降するか
    all_descend = True
    non_descend_examples = []
    for q in range(1, 200):
        n = 32 * q + r
        current = n
        descended = False
        for step in range(20):
            current = syracuse(current)
            if current < n:
                descended = True
                break
        if not descended:
            all_descend = False
            non_descend_examples.append((q, n))

    if non_descend_examples:
        print(f"  r={r}: {len(non_descend_examples)} 個が20ステップで非下降")
        for q, n in non_descend_examples[:3]:
            print(f"    n={n} (q={q})")
    else:
        print(f"  r={r}: 全て20ステップ以内に下降")

# mod 64 の詳細分析
print("\n=== mod 64 の残存クラス（厳密判定）===")
# 各クラスについて、q=1..1000 で 50ステップ以内に下降するか確認
remaining_64 = []
for r in range(64):
    if r % 4 != 3:
        continue
    non_descend_count = 0
    for q in range(1, 500):
        n = 64 * q + r
        current = n
        descended = False
        for step in range(50):
            current = syracuse(current)
            if current < n:
                descended = True
                break
        if not descended:
            non_descend_count += 1
    if non_descend_count > 0:
        remaining_64.append(r)
        print(f"  r={r}: {non_descend_count}/499 が非下降 (50ステップ)")
    # else: 全て下降
print(f"\n  mod 64 残存: {remaining_64 if remaining_64 else '(なし)'}")

# mod 128, 256 で新規排除可能なクラス特定
print("\n=== Lean形式化のための次ターゲット候補 ===")
print("方針: mod 64 の各 r ≡ 3 (mod 4) について symbolic analysis")
print("v2 が q に依存しないステップ数を調べ、下降が証明可能なクラスを列挙\n")

def find_symbolic_descent(mod, residue, max_steps=30):
    """
    n = mod*q + residue のとき、T^k(n) = a*q + b を追跡。
    v2 が q に依存する場合、mod を2倍にして分岐する。
    返値: (descent_step, formula) or None
    """
    a, b = mod, residue

    for step in range(1, max_steps + 1):
        num_a = 3 * a
        num_b = 3 * b + 1

        v = v2(num_b)
        if num_a % (2 ** v) != 0:
            return None, step  # q 依存

        new_a = num_a // (2 ** v)
        new_b = num_b // (2 ** v)

        if new_a < mod:
            # T^step(n) = new_a*q + new_b < mod*q + residue
            # (mod - new_a)*q > new_b - residue
            if new_b <= residue:
                return step, f"T^{step} = {new_a}q+{new_b}, always < n"
            else:
                threshold = (new_b - residue) / (mod - new_a)
                return step, f"T^{step} = {new_a}q+{new_b}, < n when q >= {int(threshold)+1}"

        a, b = new_a, new_b
    return None, max_steps

# mod 64 の未排除クラスに対して分析
for r in range(64):
    if r % 4 != 3:
        continue
    result, step = find_symbolic_descent(64, r)
    if result is not None:
        pass  # 排除可能
    else:
        print(f"  r={r} (mod 64): step {step} で q 依存発生")
        # このクラスを mod 128 に分岐
        for sub_r in [r, r + 64]:
            result2, step2 = find_symbolic_descent(128, sub_r)
            if result2 is not None:
                print(f"    r={sub_r} (mod 128): 排除可能! {result2}")
            else:
                print(f"    r={sub_r} (mod 128): step {step2} で q 依存")
                # さらに mod 256 に
                for sub_r2 in [sub_r, sub_r + 128]:
                    result3, step3 = find_symbolic_descent(256, sub_r2)
                    if result3 is not None:
                        print(f"      r={sub_r2} (mod 256): 排除可能! {result3}")
                    else:
                        print(f"      r={sub_r2} (mod 256): step {step3} で q 依存")

# Lean 形式化に最適なターゲットの決定
print("\n=== mod 64 で symbolic に排除可能なクラス一覧 ===")
easy_targets = []
for r in range(64):
    if r % 4 != 3:
        continue
    result, step = find_symbolic_descent(64, r)
    if result is not None:
        easy_targets.append((r, result, step))

# ステップ数でソート
easy_targets.sort(key=lambda x: x[1])
for r, step, desc in easy_targets:
    already_done = False
    if r % 16 == 3:
        already_done = True
    if r % 32 == 11 or r % 32 == 23:
        already_done = True
    status = " (既証明)" if already_done else " (新規!)"
    print(f"  r={r:2d} (mod 64): step={step}, {desc}{status}")

# 新規で最も簡単なターゲット
print("\n=== 推奨: 次に形式化すべき定理 ===")
for r, step, desc in easy_targets:
    already_done = (r % 16 == 3) or (r % 32 in [11, 23])
    if not already_done:
        print(f"  r={r} (mod 64): T^{step} で下降, {desc}")
        # 具体例
        n = 64 * 10 + r
        current = n
        path = [n]
        for _ in range(step):
            current = syracuse(current)
            path.append(current)
        print(f"    例: n={n}: " + " -> ".join(str(x) for x in path))
