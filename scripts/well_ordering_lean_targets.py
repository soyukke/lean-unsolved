"""
Lean形式化のターゲット分析:
mod 128, 256 で新規に排除可能なクラスの詳細
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

def trace_symbolic(mod, residue, max_steps=30):
    """
    T^k を symbolic に追跡し、各ステップの情報を返す。
    """
    a, b = mod, residue
    steps = []
    for step in range(1, max_steps + 1):
        num_a = 3 * a
        num_b = 3 * b + 1
        v = v2(num_b)
        if num_a % (2 ** v) != 0:
            steps.append({
                'step': step, 'a': a, 'b': b,
                'num_a': num_a, 'num_b': num_b, 'v': v,
                'q_dependent': True
            })
            break

        new_a = num_a // (2 ** v)
        new_b = num_b // (2 ** v)

        descent = new_a < mod
        steps.append({
            'step': step, 'a': new_a, 'b': new_b, 'v': v,
            'descent': descent, 'q_dependent': False
        })

        if descent:
            break
        a, b = new_a, new_b

    return steps

# ======================================
# r=7 (mod 128) の形式化設計
# ======================================
print("=" * 70)
print("TARGET 1: r=7 (mod 128)")
print("=" * 70)
steps = trace_symbolic(128, 7)
for s in steps:
    if s.get('q_dependent'):
        print(f"  Step {s['step']}: q-dependent (num_a={s['num_a']}, num_b={s['num_b']}, v2={s['v']})")
    else:
        desc = " <-- DESCENT!" if s.get('descent') else ""
        print(f"  Step {s['step']}: T^{s['step']}(n) = {s['a']}q + {s['b']}  (v2={s['v']}){desc}")

# 具体値検証
print("\n  数値検証:")
for q in range(1, 10):
    n = 128 * q + 7
    current = n
    path = [n]
    for _ in range(5):
        current = syracuse(current)
        path.append(current)
    descend = path[-1] < n
    print(f"    n={n}: " + " -> ".join(str(x) for x in path) + f"  {'< n' if descend else '>= n'}")

# Lean形式化の骨格
print("""
  Lean形式化骨格:
  -- n = 128*q + 7 のとき
  -- T(n) = (3*(128q+7)+1)/2 = (384q+22)/2 = 192q+11  (v2=1)
  -- T²(n) = (3*(192q+11)+1)/2 = (576q+34)/2 = 288q+17  (v2=1)
  -- T³(n) = (3*(288q+17)+1)/4 = (864q+52)/4 = 216q+13  (v2=2)
  -- T⁴(n) = (3*(216q+13)+1)/8 = (648q+40)/8 = 81q+5  (v2=3)
  -- 81q+5 < 128q+7 iff 47q > -2 → 常に成立!

  theorem minimal_counterexample_not_mod128_eq7 (n : ℕ) (h : isMinimalCounterexample n) :
      n % 128 ≠ 7
""")

# ======================================
# 他のターゲットも同様に分析
# ======================================
targets = [
    (128, 7, "新規"),
    (128, 23, "新規（mod 32 = 23 の再確認）"),
    (128, 87, "新規"),
    (256, 15, "新規"),
    (256, 143, "新規"),
    (256, 59, "新規"),
    (256, 187, "新規"),
    (256, 95, "新規"),
    (256, 175, "新規"),
    (256, 219, "新規"),
]

print("\n" + "=" * 70)
print("全ターゲットの概要")
print("=" * 70)
for mod, r, note in targets:
    steps = trace_symbolic(mod, r)
    last = steps[-1]
    if last.get('descent'):
        k = last['step']
        final_a = last['a']
        final_b = last['b']

        # q の閾値
        if final_b <= r:
            threshold = "q >= 0"
            difficulty = "easy"
        else:
            threshold = f"q >= {(final_b - r) // (mod - final_a) + 1}"
            difficulty = "medium"

        print(f"  r={r:3d} (mod {mod:3d}): T^{k} = {final_a}q+{final_b} < {mod}q+{r}  [{threshold}] [{difficulty}] [{note}]")

        # 具体例
        n = mod * 5 + r
        current = n
        for _ in range(k):
            current = syracuse(current)
        print(f"    例: n={n}, T^{k}={current}, n-T^{k}={n-current}")
    else:
        print(f"  r={r:3d} (mod {mod:3d}): 非シンボリック ({note})")

# ======================================
# 最も形式化しやすいターゲットの決定
# ======================================
print("\n" + "=" * 70)
print("推奨形式化順序（ステップ数・難易度で評価）")
print("=" * 70)
print("""
1. r=7 (mod 128): T^4 で下降, 4ステップ, 常に成立 → 最も簡単
   依存定理: syracuse_mod4_eq3, v2 関連

2. r=87 (mod 128): T^3 で下降, 3ステップ

3. r=15 (mod 256), r=143 (mod 256): T^4 で下降

4. r=59 (mod 256), r=187 (mod 256): T^4 で下降
""")

# 形式化に必要な中間定理の数を分析
print("\n=== r=7 (mod 128) に必要な中間定理 ===")
print("1. n ≡ 7 (mod 128) → n ≡ 3 (mod 4)")
print("2. syracuse_mod4_eq3: n ≡ 3 mod 4 → T(n) = (3n+1)/2")
print("3. n = 128q+7 → T(n) = 192q+11")
print("4. 192q+11 ≡ 3 (mod 4) → T²(n) = (3*(192q+11)+1)/2 = 288q+17")
print("5. 288q+17 ≡ 1 (mod 4) → T³(n) ≤ (3*(288q+17)+1)/4 = 216q+13")
print("   注意: ここは不等式！ v2 ≥ 2 を使う")
print("6. 216q+13 ≡ 1 (mod 4) → T⁴(n) ≤ (3*(216q+13)+1)/4 = 162q+10")
print("   注意: ここも不等式！")
print()
print("修正: 正確な v2 を使う場合:")

for q in range(1, 10):
    n = 128 * q + 7
    t1 = syracuse(n)
    t2 = syracuse(t1)
    t3 = syracuse(t2)
    t4 = syracuse(t3)
    m1 = 3 * n + 1
    m2 = 3 * t1 + 1
    m3 = 3 * t2 + 1
    m4 = 3 * t3 + 1
    print(f"  q={q}: n={n}, T1={t1}(v2={v2(m1)}), T2={t2}(v2={v2(m2)}), T3={t3}(v2={v2(m3)}), T4={t4}(v2={v2(m4)})")

# 正確な symbolic 計算（v2 が正確に決まるバージョン）
print("\n=== 正確な symbolic T^k: r=7 (mod 128) ===")
print("n = 128q + 7")
print("3n+1 = 384q + 22 = 2(192q + 11)")
print("v2(384q+22) = v2(2) + v2(192q+11)")
print("192q + 11: 192 = 64*3, 11 は奇数 → v2(192q+11) depends on q")
print("  q=0: 11 (v2=0)")
print("  q odd: 192q+11 ≡ 192+11 = 203 (mod 2) → odd, v2=0")
print("  q even: 192q+11 ≡ 11 (mod 2) → odd, v2=0")
print("192q + 11 は常に奇数! (192は偶数, 11は奇数 → 偶数+奇数=奇数)")
print("よって v2(384q+22) = 1")
print("T(n) = (384q+22)/2 = 192q + 11 ✓")
print()
print("T(n) = 192q + 11")
print("3*T(n)+1 = 576q + 34 = 2(288q + 17)")
print("288q + 17: 288 = 32*9, 17は奇数 → 288q+17 は常に奇数")
print("v2(576q+34) = 1")
print("T²(n) = 288q + 17 ✓")
print()
print("T²(n) = 288q + 17")
print("3*T²(n)+1 = 864q + 52 = 4(216q + 13)")
print("216q + 13: 216 = 8*27, 13は奇数 → 216q+13 は常に奇数")
print("v2(864q+52) = 2")
print("T³(n) = 216q + 13 ✓")
print()
print("T³(n) = 216q + 13")
print("3*T³(n)+1 = 648q + 40 = 8(81q + 5)")
print("81q + 5: 81は奇数, 5は奇数 → 81q+5 の偶奇は q に依存!")
print("  q odd: 81q+5 ≡ 81+5 = 86 ≡ 0 (mod 2) → 偶数!")
print("  q even: 81q+5 ≡ 0+5 = 5 ≡ 1 (mod 2) → 奇数!")
print()
print("→ T³(n) = 216q+13 の段階で v2 が q に依存する!")
print("しかし、T³(n) = 216q+13 < 128q+7 iff 88q > -6 → 常に成立!")
print("→ T³ の段階で既に下降している! (4ステップではなく3ステップ)")
print()

# 再確認
print("=== 再確認: T³ で下降する? ===")
for q in range(0, 10):
    n = 128 * q + 7
    if n < 2:
        continue
    t1 = syracuse(n)
    t2 = syracuse(t1)
    t3 = syracuse(t2)
    expected_t3 = 216 * q + 13
    print(f"  q={q}: n={n}, T³(n)={t3}, 216q+13={expected_t3}, T³<n: {t3<n}")

# あれ? T³ で正確に 216q+13 になるなら、これは mod 128 で排除可能
print("\n→ T³(n) = 216q + 13 > 128q + 7 for q >= 1")
print("  216*1+13 = 229 > 128*1+7 = 135? YES, 229 > 135")
print("  T³ の時点ではまだ下降していない!")
print()
print("  T⁴ の v2 は q に依存するため、mod 128 では T⁴ < n を示せない")
print("  → mod 256 に分岐が必要:")
print("    n ≡ 7 (mod 256): n = 256q+7")
print("    n ≡ 135 (mod 256): n = 256q+135")

for sub_r in [7, 135]:
    steps = trace_symbolic(256, sub_r)
    print(f"\n  r={sub_r} (mod 256):")
    for s in steps:
        if s.get('q_dependent'):
            print(f"    Step {s['step']}: q-dependent")
        else:
            desc = " <-- DESCENT!" if s.get('descent') else ""
            print(f"    Step {s['step']}: T^{s['step']} = {s['a']}q + {s['b']}  (v2={s['v']}){desc}")
