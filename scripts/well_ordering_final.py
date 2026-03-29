"""
最終分析: Lean形式化可能な最小反例制約の新定理

key insight: symbolic trace で v2 が q に依存しない限り、
T^k(n) = a*q + b は正確な等式として成立する。

v2 が q に依存する場合は、T^k(n) <= (上界) として不等式のみ使える。
ただし上界でも T^k(n) < n が示せれば最小反例排除に十分。
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

def trace_exact(mod, residue, max_steps=10):
    """各ステップの v2 が正確に決まるか追跡。
    結果: (step, a, b, v, exact) のリスト
    exact=True なら T^k = a*q + b (等式)
    exact=False なら T^k <= a*q + b (不等式、v2 >= v_min)
    """
    a, b = mod, residue
    results = []

    for step in range(1, max_steps + 1):
        num_a = 3 * a
        num_b = 3 * b + 1
        v = v2(num_b)

        # a*q + b where a = num_a, b = num_b
        # v2(num_a * q + num_b) の q 依存性チェック
        # num_a * q + num_b で、v2 は num_b の v2 が最小保証
        # ただし num_a が 2^v で割り切れるなら exact

        if num_a % (2 ** v) == 0:
            # exact
            new_a = num_a // (2 ** v)
            new_b = num_b // (2 ** v)
            results.append({
                'step': step, 'a': new_a, 'b': new_b,
                'v': v, 'exact': True,
                'descent': new_a < mod
            })
            if new_a < mod:
                break
            a, b = new_a, new_b
        else:
            # v2 >= v (minimum from constant term)
            # but not exact
            # use inequality: T^k <= (num_a * q + num_b) / 2^v
            new_a = num_a // (2 ** v)  # 切り捨て
            new_b = num_b // (2 ** v)
            results.append({
                'step': step, 'a': new_a, 'b': new_b,
                'v': v, 'exact': False,
                'descent': new_a < mod,
                'note': f'v2 >= {v}, 不等式: T^{step} <= {new_a}q + {new_b}'
            })
            if new_a < mod:
                break
            # 不正確なので先に進めない
            results[-1]['stop'] = True
            break

    return results

# ======================================
# r=87 (mod 128) の詳細分析
# ======================================
print("=" * 70)
print("TARGET: r=87 (mod 128) - 最も形式化しやすいターゲット")
print("=" * 70)
print("n = 128q + 87")
results = trace_exact(128, 87)
for r in results:
    exact_str = "=" if r['exact'] else "<="
    desc = " <-- DESCENT!" if r.get('descent') else ""
    print(f"  Step {r['step']}: T^{r['step']}(n) {exact_str} {r['a']}q + {r['b']}  (v2={r['v']}){desc}")
    if r.get('note'):
        print(f"    {r['note']}")

print("\n証明の詳細:")
print("n = 128q + 87")
print("n % 4 = 3 (87 % 4 = 3)")
print()
print("Step 1: 3n+1 = 384q + 262 = 2(192q + 131)")
print("  192q + 131: 192 偶数, 131 奇数 → 常に奇数")
print("  v2 = 1 (正確)")
print("  T(n) = 192q + 131")
print("  T(n) % 4 = (192q + 131) % 4 = 131 % 4 = 3")
print()
print("Step 2: 3*T(n)+1 = 576q + 394 = 2(288q + 197)")
print("  288q + 197: 288 偶数, 197 奇数 → 常に奇数")
print("  v2 = 1 (正確)")
print("  T²(n) = 288q + 197")
print("  T²(n) % 8 = (288q + 197) % 8 = 197 % 8 = 5")
print()
print("Step 3: 3*T²(n)+1 = 864q + 592 = ?")
v = v2(592)
print(f"  v2(864q + 592): v2(592) = {v}")
print(f"  864 % {2**v} = {864 % (2**v)}")
if 864 % (2**v) == 0:
    print(f"  864 / {2**v} = {864 // (2**v)}, 592 / {2**v} = {592 // (2**v)}")
    print(f"  T³(n) = {864 // (2**v)}q + {592 // (2**v)} (正確)")
    a3 = 864 // (2**v)
    b3 = 592 // (2**v)
    print(f"  T³(n) = {a3}q + {b3}")
    print(f"  {a3}q + {b3} < 128q + 87?")
    print(f"  {a3 - 128}q < {87 - b3}")
    if a3 < 128:
        print(f"  {a3} < 128 なので常に成立!")
    else:
        print(f"  {a3} >= 128 なのでまだ下降していない")
else:
    print(f"  q依存!")

# 数値検証
print("\n数値検証:")
for q in range(1, 10):
    n = 128 * q + 87
    t1 = syracuse(n)
    t2 = syracuse(t1)
    t3 = syracuse(t2)
    print(f"  q={q}: n={n}, T={t1}, T²={t2}, T³={t3}, T³<n: {t3<n}")

# ======================================
# r=23 (mod 128) の再確認 (既にmod32で証明済みだが mod 128 版)
# ======================================
print("\n" + "=" * 70)
print("TARGET: r=23 (mod 128) - 既に mod 32 = 23 で証明済みの一般化")
print("=" * 70)
# mod 32 = 23 はもう証明済みなので、r=23 (mod 128) は自明に排除される
# ただし r=87 (mod 128) は mod 32 = 87%32 = 23 → これも既に排除済み!
print(f"87 % 32 = {87 % 32}")  # = 23
print("→ r=87 (mod 128) は mod 32 ≡ 23 → 既に証明済み!")
print()

# 本当に新規なターゲットを探す
print("=" * 70)
print("新規ターゲットの再確認")
print("=" * 70)

# 既証明:
# - n % 4 = 1 → 排除
# - n % 16 = 3 → 排除
# - n % 32 = 11 → 排除
# - n % 32 = 23 → 排除
# したがって mod 32 で可能な残基は: {7, 15, 27, 31} (mod 32 で mod 4 = 3)

for mod in [64, 128, 256]:
    print(f"\nmod {mod} で新規排除可能なクラス:")
    new_targets = []
    for r in range(mod):
        if r % 4 != 3:
            continue
        # 既に排除済みかチェック
        already = (r % 4 == 1) or (r % 16 == 3) or (r % 32 == 11) or (r % 32 == 23)
        if already:
            continue
        # symbolic descent 可能か
        results = trace_exact(mod, r)
        if results and results[-1].get('descent'):
            last = results[-1]
            exact_str = "=" if last['exact'] else "<="
            new_targets.append((r, last['step'], last['a'], last['b'], last['exact']))
            print(f"  r={r:3d}: T^{last['step']} {exact_str} {last['a']}q+{last['b']} < {mod}q+{r}  [新規!]")
    if not new_targets:
        print(f"  (なし)")

# mod 32 で未排除の剰余類 {7, 15, 27, 31} に対する mod 64 サブクラス分析
print("\n" + "=" * 70)
print("mod 32 残存 {7, 15, 27, 31} の mod 64 サブクラス")
print("=" * 70)
for base in [7, 15, 27, 31]:
    for sub_r in [base, base + 32]:
        results = trace_exact(64, sub_r)
        status = "OK" if (results and results[-1].get('descent')) else "NG"
        if results and results[-1].get('descent'):
            last = results[-1]
            print(f"  r={sub_r:2d} (mod 64): T^{last['step']} で下降 [{status}]")
        elif results and results[-1].get('stop'):
            print(f"  r={sub_r:2d} (mod 64): step {results[-1]['step']} で q依存 [{status}]")
        else:
            print(f"  r={sub_r:2d} (mod 64): 未下降 [{status}]")

# 結論: 全てNGになるはず（mod 64 では新規排除不可）
# mod 128 で分岐
print("\n" + "=" * 70)
print("mod 128 サブクラスの分析")
print("=" * 70)
for base in [7, 15, 27, 31]:
    for sub_r in [base, base + 32, base + 64, base + 96]:
        results = trace_exact(128, sub_r)
        already = (sub_r % 16 == 3) or (sub_r % 32 == 11) or (sub_r % 32 == 23)
        if already:
            continue
        if results and results[-1].get('descent'):
            last = results[-1]
            exact_str = "=" if last['exact'] else "<="
            print(f"  r={sub_r:3d} (mod 128): T^{last['step']} {exact_str} {last['a']}q+{last['b']} [新規排除可能!]")
            # 数値検証
            for q in [1, 2, 3]:
                n = 128 * q + sub_r
                current = n
                for _ in range(last['step']):
                    current = syracuse(current)
                expected = last['a'] * q + last['b']
                eq_str = "=" if current == expected else "!="
                print(f"    q={q}: n={n}, T^{last['step']}={current} {eq_str} {expected}, T^k<n: {current<n}")
        else:
            print(f"  r={sub_r:3d} (mod 128): 未排除")
