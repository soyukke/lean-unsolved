#!/usr/bin/env python3
"""
コラッツ予想 探索38: 最小反例の mod 2^k 排除を系統的に拡張

residue class r (mod 2^k) に対して、最小反例 n₀ ≡ r (mod 2^k) を
Syracuse列の追跡により排除できるかを系統的に調べる。
"""

from fractions import Fraction
from collections import defaultdict


def v2(n):
    """2-adic付値: nを割り切る2の最大冪"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def syracuse_step_exact(n):
    """Syracuse関数 T(n) = (3n+1)/2^{v2(3n+1)}"""
    x = 3 * n + 1
    return x >> v2(x)


def try_exclude_residue(r, k, max_steps=50):
    """
    residue class r (mod 2^k) の最小反例を排除できるか試みる。

    n₀ ≡ r (mod 2^k), n₀ = 2^k * j + r として、
    Syracuse列を追跡し、ある T^s(n₀) < n₀ を示せるか調べる。

    Returns: (excluded, steps, reason)
    """
    mod = 2 ** k

    # 偶数は自明に排除
    if r % 2 == 0:
        return (True, 0, "even")

    # r ≡ 1 (mod 4) → T(n₀) = (3n₀+1)/2^v ≤ (3n₀+1)/4 < n₀ (n₀≥5)
    if r % 4 == 1:
        return (True, 1, "r≡1(mod4): T(n)≤(3n+1)/4<n")

    # r ≡ 3 (mod 4) の場合: Syracuse列を正確に追跡
    # n₀ = mod*j + r として、T^s(n₀) を j の1次式で表現
    # T^s(n₀) = a*j + b (正確には有理数係数)
    # T^s(n₀) < n₀ ⟺ a*j + b < mod*j + r ⟺ (a - mod)*j < r - b
    # a < mod なら十分大きい j で排除不可だが、j≥0 の全てで成り立つなら排除
    # a < mod かつ r - b > 0 なら全ての j≥0 で成り立つ → 排除

    # 有理数で正確に追跡
    # n₀ = mod*j + r, j は非負整数パラメータ
    # 各ステップで n = a*j + b (a, b は Fraction)

    a = Fraction(mod)  # n₀ の j の係数
    b = Fraction(r)    # n₀ の定数項

    for step in range(1, max_steps + 1):
        # 現在: n = a*j + b (奇数であるはず)
        # 3n+1 = 3a*j + 3b+1
        three_n_plus_1_a = 3 * a
        three_n_plus_1_b = 3 * b + 1

        # v2 を決定: 3n+1 の 2-adic 付値が j に依らず一定かチェック
        # 3*r+1 の v2 から始めて、mod 2^k の範囲で確定するか
        # 実際には 3b+1 の v2 が確定的なら OK
        # (a が十分大きい 2 の冪で割れるなら)

        # 具体的な値で v2 を計算
        val_at_0 = int(three_n_plus_1_b)  # j=0 での値
        val_at_1 = int(three_n_plus_1_a + three_n_plus_1_b)  # j=1 での値

        v2_0 = v2(val_at_0)
        v2_1 = v2(val_at_1)

        # v2 が j に依存する場合、この手法では追跡不可
        if v2_0 != v2_1:
            return (False, step, f"v2 ambiguous at step {step}")

        # さらに j=2,3 でも確認
        confirmed = True
        for jj in range(2, min(8, k+2)):
            val_jj = int(three_n_plus_1_a * jj + three_n_plus_1_b)
            if v2(val_jj) != v2_0:
                confirmed = False
                break

        if not confirmed:
            return (False, step, f"v2 varies at step {step}")

        v = v2_0
        divisor = Fraction(2 ** v)
        a = three_n_plus_1_a / divisor
        b = three_n_plus_1_b / divisor

        # チェック: a*j + b < mod*j + r が全ての j≥0 で成立するか
        # ⟺ (a - mod)*j + (b - r) < 0 for all j≥0
        # ⟺ a ≤ mod かつ (a < mod または b < r)
        # より正確: a < mod なら、j が十分大きければ成立するが j=0 では b < r が必要
        # a = mod なら b < r が必要
        # a > mod なら排除不可

        diff_a = a - mod
        diff_b = b - r

        if diff_a < 0 and diff_b < 0:
            # 全ての j≥0 で T^step(n₀) < n₀
            return (True, step, f"T^{step}(n₀) = ({a})*j + ({b}) < {mod}*j + {r}")
        elif diff_a < 0 and diff_b >= 0:
            # j ≥ ceil(diff_b / (-diff_a)) で成立
            # j=0 では成立しないが、j が大きければ成立
            # 最小反例は任意の j なので、j=0 の場合(n₀=r)を別途チェック
            # n₀=r の場合は直接軌道を調べる
            # ここでは「部分排除」として扱う
            pass

        # 現在の値が偶数になったら除算（これは Syracuse なので常に奇数のはず）
        # ただし b が整数でない場合がある→打ち切り
        if b.denominator != 1:
            return (False, step, f"non-integer at step {step}")

        # 次のステップ用: 現在の値が奇数かチェック
        b_int = int(b)
        if b_int % 2 == 0:
            # j=0 で偶数→ Syracuse の前提が崩れる
            # a の偶奇も確認
            a_int_mod2 = int(a) % 2
            if a_int_mod2 == 0:
                # 常に偶数→さらに2で割る（Syracuseではなく通常Collatz追跡に切替）
                return (False, step, f"even value at step {step}, need different approach")
            else:
                # j の偶奇で変わる
                return (False, step, f"parity depends on j at step {step}")

    return (False, max_steps, "max steps reached")


# ============================================================
# 1. k=3..16 での完全な排除表
# ============================================================
print("=" * 80)
print("1. mod 2^k での residue class 排除表")
print("=" * 80)

exclusion_data = {}  # k -> list of (r, excluded, steps, reason)
exclusion_rates = {}

for k in range(3, 17):
    mod = 2 ** k
    results = []
    excluded_count = 0
    odd_count = 0

    for r in range(1, mod, 2):  # 奇数のみ
        odd_count += 1
        exc, steps, reason = try_exclude_residue(r, k)
        results.append((r, exc, steps, reason))
        if exc:
            excluded_count += 1

    exclusion_data[k] = results
    rate = excluded_count / odd_count
    exclusion_rates[k] = (excluded_count, odd_count, rate)

    print(f"\nmod 2^{k} = {mod}:")
    print(f"  奇数 residue class: {odd_count}")
    print(f"  排除可能: {excluded_count}")
    print(f"  排除率: {rate:.6f} ({rate*100:.2f}%)")

    # 排除できない class を列挙（k≤8 の場合のみ詳細表示）
    if k <= 8:
        non_excluded = [(r, steps, reason) for r, exc, steps, reason in results if not exc]
        if non_excluded:
            print(f"  排除不可の class ({len(non_excluded)}個):")
            for r, steps, reason in non_excluded:
                binary = bin(r)[2:].zfill(k)
                print(f"    r={r:>{len(str(mod))}} (bin: {binary}), 理由: {reason}")

# ============================================================
# 2. 排除率の漸近挙動
# ============================================================
print("\n" + "=" * 80)
print("2. 排除率の漸近挙動")
print("=" * 80)

print(f"\n{'k':>4} {'mod':>8} {'奇数':>8} {'排除':>8} {'排除率':>10} {'1-排除率':>12}")
print("-" * 56)
for k in sorted(exclusion_rates.keys()):
    exc, total, rate = exclusion_rates[k]
    print(f"{k:>4} {2**k:>8} {total:>8} {exc:>8} {rate:>10.6f} {1-rate:>12.8f}")

# 1-排除率 の減少率を分析
print("\n漸近解析:")
prev_rem = None
for k in sorted(exclusion_rates.keys()):
    exc, total, rate = exclusion_rates[k]
    rem = 1 - rate
    if prev_rem is not None and rem > 0:
        ratio = rem / prev_rem
        print(f"  k={k}: 残存率 = {rem:.8f}, 前のkからの比 = {ratio:.4f}")
    else:
        print(f"  k={k}: 残存率 = {rem:.8f}")
    prev_rem = rem

# ============================================================
# 3. 排除できない class の共通パターン
# ============================================================
print("\n" + "=" * 80)
print("3. 排除できない class の共通パターン")
print("=" * 80)

# k=10 での排除できない class を詳しく分析
k_analyze = 10
mod_analyze = 2 ** k_analyze
non_exc_classes = []
for r, exc, steps, reason in exclusion_data[k_analyze]:
    if not exc:
        non_exc_classes.append(r)

print(f"\nmod 2^{k_analyze} = {mod_analyze} での排除不可 class ({len(non_exc_classes)}個):")

# 末尾ビットパターンの分析
print("\n末尾ビットパターン分析:")
tail_patterns = defaultdict(int)
for r in non_exc_classes:
    for bits in range(3, min(k_analyze+1, 9)):
        pattern = r % (2**bits)
        tail_patterns[(bits, pattern)] += 1

# 各ビット長での最頻パターン
for bits in range(3, min(k_analyze+1, 9)):
    total_non_exc = len(non_exc_classes)
    patterns_at_bits = {p: c for (b, p), c in tail_patterns.items() if b == bits}
    print(f"\n  末尾 {bits} ビット:")
    sorted_patterns = sorted(patterns_at_bits.items(), key=lambda x: -x[1])
    for p, c in sorted_patterns[:10]:
        binary = bin(p)[2:].zfill(bits)
        frac = c / total_non_exc * 100
        print(f"    {binary} (={p:>4}): {c:>4}個 ({frac:.1f}%)")

# mod 4, mod 8, mod 16 での分布
print("\n排除不可 class の小さい mod での分布:")
for small_k in [2, 3, 4, 5]:
    small_mod = 2 ** small_k
    dist = defaultdict(int)
    for r in non_exc_classes:
        dist[r % small_mod] += 1
    print(f"  mod {small_mod}: ", end="")
    for res in sorted(dist.keys()):
        print(f"{res}:{dist[res]} ", end="")
    print()

# ============================================================
# 4. 排除ステップ数の分布
# ============================================================
print("\n" + "=" * 80)
print("4. 排除ステップ数の分布")
print("=" * 80)

for k in [6, 8, 10, 12, 14, 16]:
    if k not in exclusion_data:
        continue
    step_dist = defaultdict(int)
    for r, exc, steps, reason in exclusion_data[k]:
        if exc:
            step_dist[steps] += 1

    total_exc = sum(step_dist.values())
    print(f"\nmod 2^{k}: 排除可能 {total_exc}個")
    for s in sorted(step_dist.keys()):
        print(f"  {s}ステップ: {step_dist[s]:>6}個 ({step_dist[s]/total_exc*100:>6.2f}%)")

# ============================================================
# 5.「最強の排除」の探索
# ============================================================
print("\n" + "=" * 80)
print("5. 最強の排除")
print("=" * 80)

# 各ステップ数での最初の排除例
print("\n各ステップ数での排除例 (mod 2^16):")
k = 16
mod = 2 ** k
step_examples = {}
for r, exc, steps, reason in exclusion_data[k]:
    if exc and steps not in step_examples:
        step_examples[steps] = (r, reason)

for s in sorted(step_examples.keys()):
    r, reason = step_examples[s]
    print(f"  {s}ステップ: r={r} (mod {mod})")
    # 実際の軌道を表示
    n = r
    traj = [n]
    for _ in range(s):
        n = syracuse_step_exact(n)
        traj.append(n)
    print(f"    軌道: {' → '.join(str(x) for x in traj)}")

# 最も多くのステップを要する排除
max_step_excluded = {}
for k in range(3, 17):
    max_s = 0
    max_r = 0
    for r, exc, steps, reason in exclusion_data[k]:
        if exc and steps > max_s:
            max_s = steps
            max_r = r
    max_step_excluded[k] = (max_s, max_r)

print("\n各 mod 2^k での最大排除ステップ数:")
for k in sorted(max_step_excluded.keys()):
    s, r = max_step_excluded[k]
    print(f"  mod 2^{k:>2}: 最大 {s} ステップ (r={r})")

# ============================================================
# 6. 排除の連鎖構造
# ============================================================
print("\n" + "=" * 80)
print("6. 排除の連鎖構造")
print("=" * 80)

k = 10
mod = 2 ** k
print(f"\nmod 2^{k} = {mod} での連鎖分析:")

# 排除可能な class のマップ
exc_map = {}
for r, exc, steps, reason in exclusion_data[k]:
    exc_map[r] = (exc, steps)

# 各排除可能な class について、T(r) mod 2^k も排除可能か調べる
chain_count = 0
chain_break_count = 0
chains = []

for r, exc, steps, reason in exclusion_data[k]:
    if not exc or steps == 0:
        continue

    # Syracuse 列を mod 2^k で追跡
    current = r
    chain = [current]
    for _ in range(10):
        next_val = syracuse_step_exact(current) % mod
        if next_val % 2 == 0:
            break
        chain.append(next_val)
        if next_val not in exc_map:
            break
        if not exc_map[next_val][0]:
            break
        current = next_val

    if len(chain) >= 3:
        chains.append(chain)

chains.sort(key=len, reverse=True)
print(f"\n長い排除連鎖 (上位20):")
for i, chain in enumerate(chains[:20]):
    exc_info = []
    for c in chain:
        if c in exc_map and exc_map[c][0]:
            exc_info.append(f"{c}(✓{exc_map[c][1]}st)")
        else:
            exc_info.append(f"{c}(?)")
    print(f"  {i+1}. 長さ {len(chain)}: {' → '.join(exc_info)}")

# ============================================================
# 7. 排除不可 class の軌道特性
# ============================================================
print("\n" + "=" * 80)
print("7. 排除不可 class の軌道特性")
print("=" * 80)

k = 10
mod = 2 ** k
non_exc = [r for r, exc, steps, reason in exclusion_data[k] if not exc]

print(f"\nmod 2^{k} = {mod} での排除不可 class の具体的軌道:")
for r in non_exc[:20]:
    n = r
    traj = [n]
    for _ in range(15):
        n = syracuse_step_exact(n)
        traj.append(n)
        if n == 1:
            break

    # 最初に r 未満になるステップ
    first_below = None
    for i, t in enumerate(traj[1:], 1):
        if t < r:
            first_below = i
            break

    print(f"  r={r:>5}: 初回下降ステップ={first_below}, 軌道前半: {' → '.join(str(x) for x in traj[:8])}...")

# ============================================================
# 8. v2 分岐の構造
# ============================================================
print("\n" + "=" * 80)
print("8. v2 分岐が起きる理由の分析")
print("=" * 80)

k = 8
mod = 2 ** k
print(f"\nmod 2^{k} = {mod} での排除不可 class の v2 分岐パターン:")

for r, exc, steps, reason in exclusion_data[k]:
    if exc:
        continue
    # 手動で追跡
    a = Fraction(mod)
    b = Fraction(r)
    print(f"\n  r = {r} (bin: {bin(r)[2:].zfill(k)}):")

    for step in range(1, 8):
        three_a = 3 * a
        three_b = 3 * b + 1

        # v2 を j=0..7 で調べる
        v2s = []
        for jj in range(8):
            val = int(three_a * jj + three_b)
            v2s.append(v2(val))

        v2_set = set(v2s)
        if len(v2_set) > 1:
            print(f"    step {step}: v2 分岐! v2 values for j=0..7: {v2s}")
            print(f"    3*a = {three_a}, 3*b+1 = {three_b}")
            # v2(3*a) を表示
            if three_a != 0:
                print(f"    v2(3*a) = {v2(int(three_a))}, v2(3*b+1) = {v2(int(three_b))}")
            break
        else:
            v = v2s[0]
            a = three_a / Fraction(2**v)
            b = three_b / Fraction(2**v)
            print(f"    step {step}: v2={v}, a={a}, b={b} (a*j+b < mod*j+r? a<mod:{a<mod}, b<r:{b<Fraction(r)})")

# ============================================================
# 9. 理論的まとめ
# ============================================================
print("\n" + "=" * 80)
print("9. 理論的まとめ")
print("=" * 80)

print("\n排除率の推移:")
print(f"{'k':>4} {'排除率':>10} {'排除不可数':>10} {'理論的期待':>12}")
for k in sorted(exclusion_rates.keys()):
    exc, total, rate = exclusion_rates[k]
    non_exc = total - exc
    # Terras (1976) の結果: ほぼ全ての n で stopping time は有限
    # 排除不可の割合は指数的に減少するか？
    print(f"{k:>4} {rate:>10.6f} {non_exc:>10}")

print("\n結論:")
print("- mod 2^k の奇数 residue class のうち、最小反例を排除できる割合")
print("- k が増えるにつれて排除率がどう変化するか")
print("- 排除不可の class は v2 の分岐（j 依存性）により追跡が困難になるもの")
print("- これは Collatz 問題の本質的困難を反映している")

# 追加: 排除不可 class の「密度」
print("\n排除不可 class の密度推定:")
for k in sorted(exclusion_rates.keys()):
    exc, total, rate = exclusion_rates[k]
    non_exc = total - exc
    density = non_exc / (2**k)  # 全整数中での密度
    print(f"  k={k:>2}: 密度 = {density:.8f} (= {non_exc}/{2**k})")
