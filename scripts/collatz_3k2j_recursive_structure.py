"""
3^k*2^j-1 型の着地後の再帰的構造の分析

着地値 2*3^m - 1 が T を適用すると再び 3^k'*2^j'-1 型になるか?
もしそうなら、軌道全体が 3^k*2^j-1 型の列で記述できる。
"""

def v2(n):
    if n == 0: return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    if n == 0: return 0
    m = 3 * n + 1
    return m >> v2(m)

def factor_3k2j_m1(n):
    """n = 3^k * 2^j - 1 の形に分解。不可能なら None"""
    val = n + 1  # = 3^k * 2^j
    if val <= 0:
        return None
    # 2^j を取り出す
    j = v2(val)
    if j == 0:
        return None  # 奇数部が2の冪でない
    odd_part = val >> j  # = 3^k
    # 3^k かチェック
    k = 0
    temp = odd_part
    while temp > 1 and temp % 3 == 0:
        temp //= 3
        k += 1
    if temp != 1:
        return None  # 3の冪でない
    return (k, j)

# ============================================================
# Part 1: 着地値 2*3^m - 1 は 3^k'*2^j'-1 型か?
# ============================================================
print("=" * 80)
print("Part 1: 着地値 2*3^m - 1 の分解")
print("=" * 80)

print("\n2*3^m - 1 + 1 = 2*3^m = 3^m * 2^1")
print("つまり 2*3^m - 1 = 3^m * 2^1 - 1  (k=m, j=1)")
print("これは常に 3^k*2^j-1 型! ただし j=1.")

for m in range(1, 15):
    n = 2 * 3**m - 1
    decomp = factor_3k2j_m1(n)
    print(f"  m={m:2d}: 2*3^{m}-1 = {n:12d}, decomp = 3^{decomp[0]}*2^{decomp[1]}-1 = {decomp}")

# ============================================================
# Part 2: j=1 ケースの T の効果
# ============================================================
print("\n" + "=" * 80)
print("Part 2: T(3^k * 2^1 - 1) = T(2*3^k - 1) の分解")
print("=" * 80)

print("\nn = 2*3^k - 1 に T を適用:")
print("3n+1 = 6*3^k - 2 = 2*(3^{k+1} - 1)")
print("T(n) = (3^{k+1} - 1) / 2^{v2(3^{k+1}-1)}")

for k in range(1, 20):
    n = 2 * 3**k - 1
    t = syracuse(n)
    decomp = factor_3k2j_m1(t)
    p = k + 1
    v2_val = v2(3**p - 1)
    t_formula = (3**p - 1) // (2**v2_val)

    # (3^p - 1) / 2^{v2(3^p-1)} は 3^k'*2^j'-1 型か?
    decomp_str = f"3^{decomp[0]}*2^{decomp[1]}-1" if decomp else "NOT 3^k*2^j-1"

    print(f"  k={k:2d}: T(2*3^{k}-1) = (3^{p}-1)/2^{v2_val} = {t:12d}, "
          f"decomp = {decomp_str}")

# ============================================================
# Part 3: (3^p - 1) / 2^{v2(3^p-1)} の分解
# ============================================================
print("\n" + "=" * 80)
print("Part 3: (3^p - 1) / 2^{v2(3^p-1)} の 3^k*2^j-1 型への分解")
print("=" * 80)

print("\nv2(3^p - 1):")
print("  p odd:  v2(3^p-1) = 1")
print("  p even: v2(3^p-1) = v2(3^2-1) + v2(p) = 3 + v2(p)  (Lifting the exponent)")
print("  ...いや正確には p=2q のとき v2(3^{2q}-1) = v2((3^2)^q - 1) = v2(9^q-1)")
print("  v2(9^q - 1) = v2(8) + v2(q) = 3 + v2(q)  (LTE for p=2)")

for p in range(1, 25):
    val = 3**p - 1
    v = v2(val)
    quot = val // (2**v)  # 奇数部

    # 奇数部を 3^a * r の形に分解
    a = 0
    temp = quot
    while temp % 3 == 0:
        temp //= 3
        a += 1

    if p % 2 == 1:
        expected_v = 1
    else:
        expected_v = 3 + v2(p)

    # (3^p-1)/2^v が 何*何 の形か
    # 3^p - 1 = 2^v * odd_part
    # odd_part = (3^p - 1) / 2^v

    print(f"  p={p:2d}: 3^p-1 = {val:15d}, v2={v:2d}(expected={expected_v:2d}), "
          f"odd_part={quot:12d} = 3^{a} * {temp}")

# ============================================================
# Part 4: 着地後の軌道を 3^k*2^j-1 型の列として追跡
# ============================================================
print("\n" + "=" * 80)
print("Part 4: 軌道の 3^k*2^j-1 型追跡")
print("=" * 80)

print("\n初期値 n = 3^k*2^j-1 から、各ステップで分解を試みる")

def trace_orbit_decomposed(n_init, max_steps=50):
    """軌道を追跡し、各値を 3^k*2^j-1 型に分解"""
    trace = []
    current = n_init
    for step in range(max_steps):
        if current <= 1:
            break
        decomp = factor_3k2j_m1(current)
        if decomp:
            k, j = decomp
            trace.append((step, current, k, j, 'match'))
        else:
            trace.append((step, current, None, None, 'no_match'))
        current = syracuse(current)
    return trace

# いくつかの例で追跡
test_cases = [
    (0, 10),  # 2^10 - 1 = 1023
    (1, 5),   # 3*2^5 - 1 = 95
    (2, 4),   # 9*2^4 - 1 = 143
    (0, 6),   # 2^6 - 1 = 63
    (1, 8),   # 3*2^8 - 1 = 767
]

for k0, j0 in test_cases:
    n = 3**k0 * 2**j0 - 1
    print(f"\n--- 初期値: 3^{k0}*2^{j0}-1 = {n} ---")
    trace = trace_orbit_decomposed(n, 30)
    match_count = sum(1 for t in trace if t[4] == 'match')
    total = len(trace)
    print(f"  3^k*2^j-1型に合致: {match_count}/{total} ({100*match_count/total:.1f}%)")
    for step, val, kk, jj, status in trace[:20]:
        if status == 'match':
            print(f"  step {step:2d}: {val:10d} = 3^{kk}*2^{jj}-1")
        else:
            print(f"  step {step:2d}: {val:10d}  (not 3^k*2^j-1 type)")

# ============================================================
# Part 5: Waterfall + Landing の繰り返し構造
# ============================================================
print("\n" + "=" * 80)
print("Part 5: Waterfall-Landing 繰り返し構造")
print("=" * 80)

print("""
観察: 3^k*2^j-1 型の軌道は以下のサイクルで進む:

Phase 1 (Waterfall): j-1 回の上昇
  3^k*2^j-1 -> 3^{k+1}*2^{j-1}-1 -> ... -> 3^{k+j-1}*2^1-1

Phase 2 (Landing): T(2*3^m-1) = (3^{m+1}-1)/2^{v2(3^{m+1}-1)}
  ここで m = k+j-1

問題: Phase 2 の結果は再び 3^k'*2^j'-1 型か?
""")

def analyze_waterfall_landing_chain(k0, j0, max_iterations=10):
    """Waterfall-Landing の繰り返しを追跡"""
    chain = []
    k, j = k0, j0
    current = 3**k * 2**j - 1

    for iteration in range(max_iterations):
        if current <= 1:
            chain.append({'iter': iteration, 'k': k, 'j': j, 'n': current, 'status': 'reached_1'})
            break

        # Waterfall phase: j-1 回上昇
        if j >= 2:
            landing = 2 * 3**(k+j-1) - 1
            chain.append({
                'iter': iteration,
                'k': k, 'j': j,
                'n': current,
                'waterfall_steps': j-1,
                'landing': landing,
                'status': 'waterfall'
            })

            # Landing: T(landing) を計算
            t_landing = syracuse(landing)
            if t_landing <= 1:
                chain.append({'iter': iteration+1, 'n': t_landing, 'status': 'reached_1'})
                break

            # 次の分解
            decomp = factor_3k2j_m1(t_landing)
            if decomp:
                k, j = decomp
                current = t_landing
            else:
                chain.append({
                    'iter': iteration+1,
                    'n': t_landing,
                    'status': 'left_family',
                    'note': f'T(2*3^{k+j-1}-1) = {t_landing} is not 3^k*2^j-1 type'
                })
                break
        elif j == 1:
            # j=1: 2*3^k - 1, mod4=1, 直接 landing
            chain.append({
                'iter': iteration,
                'k': k, 'j': 1,
                'n': current,
                'waterfall_steps': 0,
                'landing': current,
                'status': 'direct_landing'
            })
            t = syracuse(current)
            if t <= 1:
                chain.append({'iter': iteration+1, 'n': t, 'status': 'reached_1'})
                break
            decomp = factor_3k2j_m1(t)
            if decomp:
                k, j = decomp
                current = t
            else:
                chain.append({
                    'iter': iteration+1,
                    'n': t,
                    'status': 'left_family',
                    'note': f'{t} is not 3^k*2^j-1 type'
                })
                break

    return chain

# テスト
for k0 in range(4):
    for j0 in [3, 5, 8]:
        n = 3**k0 * 2**j0 - 1
        chain = analyze_waterfall_landing_chain(k0, j0, 20)
        print(f"\n--- 3^{k0}*2^{j0}-1 = {n} ---")
        for entry in chain:
            if entry['status'] == 'waterfall':
                print(f"  [{entry['iter']}] 3^{entry['k']}*2^{entry['j']}-1 = {entry['n']}, "
                      f"waterfall {entry['waterfall_steps']} steps -> landing {entry['landing']}")
            elif entry['status'] == 'direct_landing':
                print(f"  [{entry['iter']}] 3^{entry['k']}*2^1-1 = {entry['n']} (j=1, direct landing)")
            elif entry['status'] == 'reached_1':
                print(f"  [{entry['iter']}] Reached {entry['n']}")
            elif entry['status'] == 'left_family':
                print(f"  [{entry['iter']}] LEFT FAMILY: {entry['n']} ({entry.get('note','')})")

# ============================================================
# Part 6: (3^p-1)/2^{v2(3^p-1)} が 3^k*2^j-1型かの系統調査
# ============================================================
print("\n" + "=" * 80)
print("Part 6: (3^p - 1) / 2^{v2(3^p-1)} の分解結果")
print("=" * 80)

print("\nこの値は T(2*3^{p-1}-1) に等しい")
print("p = k+j (waterfall の k+j-1+1)")

for p in range(2, 30):
    val = 3**p - 1
    v = v2(val)
    result = val // (2**v)
    decomp = factor_3k2j_m1(result)
    if decomp:
        kk, jj = decomp
        decomp_str = f"3^{kk}*2^{jj}-1"
    else:
        # 一般的な因数分解
        decomp_str = f"NOT in family (odd={result})"

    print(f"  p={p:2d}: (3^{p}-1)/2^{v} = {result:15d}, {decomp_str}")

# ============================================================
# Part 7: 非3^k*2^j-1型の値の構造
# ============================================================
print("\n" + "=" * 80)
print("Part 7: 族を離れる場合の分析")
print("=" * 80)

left_family = []
for p in range(2, 30):
    val = 3**p - 1
    v = v2(val)
    result = val // (2**v)
    decomp = factor_3k2j_m1(result)
    if decomp is None:
        left_family.append((p, result))
        # result + 1 の素因数分解
        n1 = result + 1
        factors = {}
        temp = n1
        for prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
            while temp % prime == 0:
                factors[prime] = factors.get(prime, 0) + 1
                temp //= prime
        if temp > 1:
            factors[temp] = 1

        print(f"  p={p:2d}: result={result:15d}, result+1={n1:15d} = {factors}")

# ============================================================
# Part 8: 着地後の連続下降と再上昇のパターン
# ============================================================
print("\n" + "=" * 80)
print("Part 8: 着地後の軌道パターン - 下降フェーズの長さと次のwaterfall")
print("=" * 80)

for k0 in [0, 1, 2]:
    for j0 in range(3, 12):
        n_init = 3**k0 * 2**j0 - 1
        # waterfall phase
        landing = 2 * 3**(k0+j0-1) - 1
        # 着地後の軌道を追跡
        current = landing
        orbit_after_landing = [current]
        for _ in range(100):
            if current <= 1:
                break
            current = syracuse(current)
            orbit_after_landing.append(current)

        # 最初の下降の長さ
        desc_len = 0
        for i in range(len(orbit_after_landing)-1):
            if orbit_after_landing[i+1] < orbit_after_landing[i]:
                desc_len += 1
            else:
                break

        # 次の上昇開始点の分解
        if desc_len > 0 and desc_len < len(orbit_after_landing):
            next_asc_start = orbit_after_landing[desc_len]
            decomp_next = factor_3k2j_m1(next_asc_start)
        else:
            next_asc_start = None
            decomp_next = None

        m = k0 + j0 - 1
        v2_3m1 = v2(3**(m+1) - 1)

        if j0 <= 8:
            print(f"  k={k0}, j={j0}: m={m}, v2(3^{m+1}-1)={v2_3m1}, "
                  f"desc_len={desc_len}, "
                  f"next_asc={next_asc_start}, decomp={decomp_next}")

# ============================================================
# Part 9: v2(3^p-1) のパターンと着地後の挙動の関係
# ============================================================
print("\n" + "=" * 80)
print("Part 9: v2(3^p-1) と着地後の縮小率の関係")
print("=" * 80)

print("\nT(2*3^{m}-1) / (2*3^m-1) = ((3^{m+1}-1)/2^{v2(3^{m+1}-1)}) / (2*3^m-1)")
print("大きな m で: ~ 3^{m+1} / (2^v * 2*3^m) = 3/(2^{v+1})")
print("v = v2(3^{m+1}-1)")

for m in range(1, 25):
    n = 2 * 3**m - 1
    t = syracuse(n)
    ratio = t / n
    p = m + 1
    v = v2(3**p - 1)
    theoretical_ratio = 3 / (2**(v+1))
    print(f"  m={m:2d}: v2(3^{p}-1)={v:2d}, ratio={ratio:.6f}, "
          f"3/2^{v+1}={theoretical_ratio:.6f}, "
          f"{'LARGE DROP' if v >= 4 else ''}")

# ============================================================
# Summary Statistics
# ============================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print("""
====================
核心的発見
====================

[発見1] 一般化Waterfall公式 (k-independent):
  T^s(3^k * 2^j - 1) = 3^{k+s} * 2^{j-s} - 1   (0 <= s <= j-2)

  これは既知の Waterfall 公式 T^s(2^m-1) = 3^s*2^{m-s}-1 の
  k=0 ケースの自然な一般化。kはsにシフトされるだけ。
  証明は waterfall_step の s 回適用。

[発見2] 普遍的着地定理:
  T^{j-1}(3^k * 2^j - 1) = 2*3^{k+j-1} - 1 = 3^{k+j-1}*2^1 - 1
  mod 4 = 1, 必ず下降。連続上昇回数は正確に j-1。

[発見3] 着地後の行先:
  T(2*3^m - 1) = (3^{m+1}-1) / 2^{v2(3^{m+1}-1)}
  縮小率 ~ 3/2^{v+1} where v = v2(3^{m+1}-1)
  v >= 4 のとき大きなジャンプダウン (ratio < 0.1)

[発見4] 3^k*2^j-1 族の閉鎖性:
  Waterfall フェーズは族内で閉じる（定理1）。
  Landing 後は一般には族を離れる。(3^p-1)/2^{v2(3^p-1)}
  が 3^k'*2^j'-1 型になるのは特殊ケースのみ。

[発見5] 着地後の比率は (3/2)^{j-1} に漸近:
  T^{j-1}(3^k*2^j-1) / (3^k*2^j-1) ~ (2/3)*(3/2)^{j-1} * correction(k)
  j が大きいほど着地値は初期値の指数的倍数。
  しかし着地後の1ステップで v2(3^{m+1}-1) に応じて大幅に縮小。

====================
形式化への接続
====================

定理1 (generalized_waterfall) の形式化:
  既存の waterfall_step: T(a*2^j-1) = 3a*2^{j-1}-1 (a odd, j>=2) を
  s 回帰納法で適用するだけ。
  基礎: s=0 は自明。
  帰納: a = 3^{k+s} は奇数、指数 = j-s >= 2 を保証。

定理2 (universal_landing) の形式化:
  定理1で s=j-1 を代入。j-1 <= j-2 ではないが、
  実は s=j-1 のとき公式自体は成立: 3^{k+j-1}*2^1-1 = 2*3^{k+j-1}-1
  ただしこのステップは waterfall_step ではなく直接計算。
  3n+1 = 3*(3^{k+j-2}*4-1)+1 = 3^{k+j-1}*4-2 = 2*(2*3^{k+j-1}-1)
  v2(3n+1) = 1, T(n) = (3n+1)/2 = 2*3^{k+j-1}-1

定理3 (consecutive_ascents_3k2j):
  定理1 + mod4=3 条件から各ステップが上昇であることを示す。
  定理2 + mod4=1 から j-1回目の着地で下降を示す。
""")
