#!/usr/bin/env python3
"""
コラッツ予想 探索36: 最小反例の制約解析

背理法アプローチ:
コラッツ予想が偽と仮定 → 1に到達しない最小の正整数 n₀ が存在
n₀ にどんな制約がかかるかを列挙・検証する。
"""

from fractions import Fraction
from itertools import product


def collatz_step(n):
    """コラッツの1ステップ"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1


def T(n):
    """短縮コラッツ関数: 奇数 n → (3n+1) / 2^v2(3n+1)"""
    if n % 2 == 0:
        raise ValueError(f"T is defined for odd n, got {n}")
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m


def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def reaches_one(n, max_steps=10000):
    """n が max_steps 以内に 1 に到達するか"""
    for _ in range(max_steps):
        if n == 1:
            return True
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
    return False


print("=" * 80)
print("コラッツ予想 探索36: 最小反例 n₀ の制約解析")
print("=" * 80)

# ============================================================
# 制約1: n₀ は奇数
# ============================================================
print("\n" + "=" * 80)
print("【制約1】n₀ は奇数")
print("=" * 80)
print("""
証明:
  n₀ が偶数なら collatzStep(n₀) = n₀/2 < n₀。
  n₀/2 も1に到達しない（到達すれば n₀ も到達する）。
  n₀/2 < n₀ は n₀ の最小性に矛盾。
  ∴ n₀ は奇数。
""")
print("→ n₀ ≡ 1 (mod 2) が確定")

# ============================================================
# 制約2: n₀ ≡ 3 (mod 4)
# ============================================================
print("\n" + "=" * 80)
print("【制約2】n₀ ≡ 3 (mod 4)")
print("=" * 80)
print("""
証明:
  n₀ ≡ 1 (mod 4) のとき:
    n₀ = 4k+1 → 3n₀+1 = 12k+4 = 4(3k+1)
    v₂(3n₀+1) ≥ 2 なので T(n₀) = (3n₀+1)/2^v ≤ (3n₀+1)/4
    T(n₀) ≤ (3n₀+1)/4 < n₀  (∵ 3n₀+1 < 4n₀ for n₀ > 1)
  T(n₀) < n₀ かつ T(n₀) は1に到達しない → n₀ の最小性に矛盾。
  ∴ n₀ ≡ 3 (mod 4)。
""")

# 数値検証
print("数値検証: n ≡ 1 (mod 4) のとき T(n) < n を確認")
counterexample_found = False
for n in range(5, 10001, 4):  # n = 5, 9, 13, ...
    t = T(n)
    if t >= n:
        print(f"  反例発見: n={n}, T(n)={t} ≥ n")
        counterexample_found = True
        break
if not counterexample_found:
    print(f"  n ≡ 1 (mod 4), n ∈ [5, 10001) の範囲で T(n) < n が全て成立 ✓")
print("\n→ n₀ ≡ 3 (mod 4) が確定")

# ============================================================
# 制約3: n₀ ≡ 7 (mod 8) の詳細証明
# ============================================================
print("\n" + "=" * 80)
print("【制約3】n₀ ≡ 7 (mod 8)")
print("=" * 80)
print("""
証明:
  n₀ ≡ 3 (mod 8) のとき: n₀ = 8k+3

  ステップ1: T(n₀) の計算
    3n₀+1 = 3(8k+3)+1 = 24k+10 = 2(12k+5)
    12k+5 は奇数 → v₂(3n₀+1) = 1
    T(n₀) = (3n₀+1)/2 = 12k+5

  ステップ2: T(n₀) の mod 4 での値
    T(n₀) = 12k+5 ≡ 5 ≡ 1 (mod 4)
    → T(n₀) ≡ 1 (mod 4) なので、制約2の議論より T(T(n₀)) < T(n₀)

  ステップ3: T(T(n₀)) の上界
    T(n₀) ≡ 1 (mod 4) → v₂(3·T(n₀)+1) ≥ 2
    T(T(n₀)) ≤ (3·T(n₀)+1)/4 = (3(12k+5)+1)/4 = (36k+16)/4 = 9k+4

  ステップ4: 最小性の適用
    T(T(n₀)) も1に到達しない（T(n₀) が到達しないので）。
    最小性より T(T(n₀)) ≥ n₀。
    T(T(n₀)) ≤ 9k+4 かつ n₀ = 8k+3 なので:
      9k+4 ≥ 8k+3 → k ≥ -1 → k ≥ 0 (常に成立)

    !! 待って、これだけでは矛盾が得られない !!
""")

print("再検討: T(T(n₀)) の正確な値を計算")
print()
print("n₀ = 8k+3 のとき:")
print("  T(n₀) = 12k+5")
print("  T(n₀) mod 4 = (12k+5) mod 4 = (0+1) mod 4 = 1  (∵ 12k ≡ 0 mod 4)")
print()

# T(n₀) = 12k+5 のとき、更に mod 8 で場合分け
print("  T(n₀) = 12k+5 の mod 8 での場合分け:")
for k_mod in range(2):  # k mod 2
    val = (12 * k_mod + 5) % 8
    print(f"    k ≡ {k_mod} (mod 2) → T(n₀) = 12k+5 ≡ {val} (mod 8)")

print()
print("  場合A: k ≡ 0 (mod 2), k=2j → n₀ = 16j+3 ≡ 3 (mod 16)")
print("    T(n₀) = 24j+5 ≡ 5 (mod 8)")
print("    3·T(n₀)+1 = 72j+16 = 8(9j+2) → v₂ ≥ 3")
print("    T(T(n₀)) ≤ (3(24j+5)+1)/8 = (72j+16)/8 = 9j+2")
print("    n₀ = 16j+3, T(T(n₀)) ≤ 9j+2")
print("    最小性: 9j+2 ≥ 16j+3 → -7j ≥ 1 → j ≤ -1/7")
print("    j ≥ 0 なので矛盾！ → n₀ ≡ 3 (mod 16) は不可能 ✓")
print()
print("  場合B: k ≡ 1 (mod 2), k=2j+1 → n₀ = 16j+11 ≡ 11 (mod 16)")
print("    T(n₀) = 24j+17 ≡ 1 (mod 8)")
print("    ※ T(n₀) ≡ 1 (mod 4) なので T(T(n₀)) < T(n₀) は確定")
print("    3·T(n₀)+1 = 72j+52 = 4(18j+13) → v₂ = 2 (18j+13 は奇数)")
print("    T(T(n₀)) = (72j+52)/4 = 18j+13")
print("    n₀ = 16j+11, T(T(n₀)) = 18j+13")
print("    最小性: 18j+13 ≥ 16j+11 → 2j ≥ -2 → j ≥ -1")
print("    j ≥ 0 なので常に成立。矛盾なし。")
print()

print("--- 修正結論 ---")
print("n₀ ≡ 3 (mod 8) の全体からは直接矛盾は出ない。")
print("しかし n₀ ≡ 3 (mod 16) は排除できる！")
print("n₀ ≡ 3 (mod 8) なら n₀ ≡ 11 (mod 16) に制限される。")
print()

# ============================================================
# 一般化: mod 2^k での系統的排除
# ============================================================
print("\n" + "=" * 80)
print("【制約の系統的構築】mod 2^k での排除")
print("=" * 80)

def analyze_residue_chain(n0_mod, modulus, max_depth=20):
    """
    n₀ ≡ n0_mod (mod modulus) という仮定のもとで、
    T を繰り返し適用して矛盾（T^k(n₀) < n₀ となる反例なし軌道の存在）を導けるか解析。

    戻り値: (排除可能か, 理由, 深さ)
    """
    # シンボリック解析: n₀ = modulus * j + n0_mod として
    # T の軌道を追跡。各ステップで a*j + b の形を維持。
    # T^k(n₀) = a_k * j + b_k とし、a_k * j + b_k ≥ n₀ = modulus * j + n0_mod
    # が必要（最小性）。
    # (a_k - modulus) * j ≥ n0_mod - b_k
    # a_k < modulus なら j ≤ (n0_mod - b_k) / (modulus - a_k) → j が有限値以下に制限
    # → 有限個の候補しかなく、全部検証できる

    # n₀ = modulus * j + n0_mod, j ≥ 0
    # 現在の値を (a, b) = (modulus, n0_mod) とする → 値 = a*j + b

    a, b = modulus, n0_mod

    for depth in range(1, max_depth + 1):
        # 現在の値 val = a*j + b は奇数であるべき（T を適用するため）
        # val の奇偶は b の奇偶で決まる（a は偶数＝2のべき乗の倍数なので）
        # ただし a が奇数の場合もある

        if b % 2 == 0:
            # 偶数 → 2で割る
            # しかし何回割れるかは j に依存する可能性がある
            # b が偶数で a も偶数なら val は常に偶数
            if a % 2 == 0:
                a //= 2
                b //= 2
                # もう1回チェック
                continue
            else:
                # a が奇数、b が偶数 → val の偶奇は j に依存 → 場合分け必要
                return False, "場合分けが必要(偶奇不定)", depth

        # val = a*j + b は奇数
        # T(val) = (3*val + 1) / 2^v2(3*val+1)
        # 3*val + 1 = 3a*j + 3b + 1
        new_a = 3 * a
        new_b = 3 * b + 1

        # v2 を求める: new_b の v2 が key
        # a が十分 2 で割れるなら v2 は new_b の v2 で確定
        v2_b = v2(new_b)
        v2_a = v2(new_a)

        if v2_a >= v2_b:
            # v2(new_a * j + new_b) = v2_b（j=0以外でも）
            # ただし厳密には new_a / 2^v2_b * j + new_b / 2^v2_b の偶奇による
            divisor = 2 ** v2_b
            a = new_a // divisor
            b = new_b // divisor

            # 最小性チェック: a*j + b ≥ modulus*j + n0_mod
            # (a - modulus)*j ≥ n0_mod - b
            coeff = a - modulus
            rhs = n0_mod - b

            if coeff < 0:
                # j ≤ rhs / coeff = (n0_mod - b) / (a - modulus)
                # coeff < 0 なので j ≤ (n0_mod - b) / (a - modulus)
                # = (b - n0_mod) / (modulus - a)
                if rhs <= 0:
                    # (n0_mod - b) ≤ 0 つまり b ≥ n0_mod
                    # coeff < 0 → coeff * j ≥ rhs は j ≤ rhs/coeff
                    # rhs ≤ 0, coeff < 0 → rhs/coeff ≥ 0
                    j_max = rhs // coeff  # 正の値（負÷負）
                    # j は 0 以上 j_max 以下
                    # これらの有限個を直接検証
                    all_reach = True
                    for jj in range(j_max + 2):  # 余裕をもって
                        candidate = modulus * jj + n0_mod
                        if candidate < 2:
                            continue
                        if not reaches_one(candidate, max_steps=100000):
                            all_reach = False
                            break
                    if all_reach:
                        return True, f"深さ{depth}: T^{depth}(n₀) = {a}j+{b}, 係数{coeff}<0 → j≤{j_max}, 全候補が1到達", depth
                else:
                    # rhs > 0, coeff < 0 → coeff*j ≥ rhs は不可能（j≥0）
                    # つまり T^depth(n₀) < n₀ が全ての j≥0 で成立
                    # → T^depth(n₀) は1に到達しない n₀ 未満の値 → 矛盾
                    return True, f"深さ{depth}: T^{depth}(n₀) = {a}j+{b} < n₀ (∀j≥0)", depth
        else:
            # v2(new_a) < v2(new_b) → j の値によって v2 が変わる → 場合分け
            return False, "v2が不定(場合分け必要)", depth

    return False, "最大深さ到達", max_depth


# mod 8 での解析
print("\n--- mod 8 での解析 ---")
print("n₀ は奇数かつ ≡ 3 (mod 4) なので、mod 8 の候補は: 3, 7")
for r in [3, 7]:
    result, reason, depth = analyze_residue_chain(r, 8)
    status = "排除 ✓" if result else "排除不可 ✗"
    print(f"  n₀ ≡ {r} (mod 8): {status} ({reason})")

# mod 16 での解析
print("\n--- mod 16 での解析 ---")
print("n₀ ≡ 3 or 7 (mod 8) → mod 16 の候補は: 3, 7, 11, 15")
for r in [3, 7, 11, 15]:
    result, reason, depth = analyze_residue_chain(r, 16)
    status = "排除 ✓" if result else "排除不可 ✗"
    print(f"  n₀ ≡ {r:2d} (mod 16): {status} ({reason})")


# 系統的排除: mod 2^k for k = 3..12
print("\n" + "=" * 80)
print("【系統的排除】mod 2^k (k=3..12)")
print("=" * 80)

surviving = {3, 7}  # mod 8 での生存候補（制約1,2 適用後）

for k in range(3, 13):
    modulus = 2 ** k
    new_surviving = set()
    eliminated = []

    for r in sorted(surviving):
        # mod 2*modulus に拡張
        for ext in [r, r + modulus]:
            result, reason, depth = analyze_residue_chain(ext, 2 * modulus)
            if result:
                eliminated.append((ext, reason))
            else:
                new_surviving.add(ext)

    next_modulus = 2 * modulus
    total_odd = next_modulus // 2  # 奇数の個数
    # n₀ ≡ 3 mod 4 に限定した個数
    mod4_candidates = next_modulus // 4

    surviving = new_surviving
    survival_rate = len(surviving) / mod4_candidates if mod4_candidates > 0 else 0

    print(f"\nmod {next_modulus} (2^{k+1}):")
    print(f"  排除: {len(eliminated)} クラス")
    for e_r, e_reason in eliminated[:5]:
        print(f"    n₀ ≡ {e_r} (mod {next_modulus}): {e_reason}")
    if len(eliminated) > 5:
        print(f"    ... (他 {len(eliminated)-5} クラス)")
    print(f"  生存: {len(surviving)} クラス / {mod4_candidates} 候補 (mod 4 ≡ 3 内)")
    print(f"  生存率: {survival_rate:.4f} ({survival_rate*100:.2f}%)")
    if len(surviving) <= 20:
        print(f"  生存クラス: {sorted(surviving)}")


# ============================================================
# 詳細解析: 手動で mod 8 の制約3を検証
# ============================================================
print("\n" + "=" * 80)
print("【詳細検証】制約3 (n₀ ≡ 3 mod 8) の手動証明")
print("=" * 80)

print("""
n₀ = 8k+3 (k ≥ 0) と仮定。

T(n₀) の計算:
  3n₀ + 1 = 3(8k+3) + 1 = 24k + 10 = 2(12k + 5)
  12k+5 は奇数（12k は偶数、+5 で奇数）
  → v₂(3n₀+1) = 1
  → T(n₀) = (3n₀+1)/2 = 12k + 5
""")

# 数値検証
print("数値検証: n₀ = 8k+3 → T(n₀) = 12k+5")
for k in range(10):
    n0 = 8*k + 3
    t_n0 = T(n0)
    expected = 12*k + 5
    match = "✓" if t_n0 == expected else "✗"
    print(f"  k={k}: n₀={n0}, T(n₀)={t_n0}, 12k+5={expected} {match}")

print("""
T(n₀) = 12k+5 のmod 4:
  12k+5 ≡ 0k+1 ≡ 1 (mod 4)
  → T(n₀) ≡ 1 (mod 4)

制約2より、T(n₀) ≡ 1 (mod 4) なら T(T(n₀)) < T(n₀)。
T(n₀) は1に到達しないので、T(T(n₀)) も1に到達しない。
最小性より T(T(n₀)) ≥ n₀。

T(T(n₀)) の計算:
  T(n₀) = 12k+5
  3·T(n₀)+1 = 3(12k+5)+1 = 36k+16

  v₂(36k+16) は k に依存:
""")

print("v₂(36k+16) の k に対する依存:")
for k in range(16):
    val = 36*k + 16
    v = v2(val)
    print(f"  k={k:2d}: 36k+16={val:4d}, v₂={v}, T(T(n₀))={val // (2**v)}")

print("""
パターン:
  k偶 (k=2j): 36(2j)+16 = 72j+16 = 8(9j+2), v₂ ≥ 3
    9j+2 の偶奇: 奇数(j偶)or偶数(j奇)
    - j偶: v₂ = 3, T(T(n₀)) = 9j+2
    - j奇: v₂ ≥ 4
  k奇 (k=2j+1): 36(2j+1)+16 = 72j+52 = 4(18j+13), v₂ = 2
    (18j+13 は奇数)
    T(T(n₀)) = 18j+13
""")

# n₀ ≡ 3 (mod 16) の排除
print("=" * 60)
print("n₀ ≡ 3 (mod 16) の排除 (k偶, k=2j):")
print("=" * 60)
print("""
  n₀ = 16j+3, T(T(n₀)) ≤ 9j+2

  最小性: T(T(n₀)) ≥ n₀
  → 9j+2 ≥ 16j+3
  → -7j ≥ 1
  → j ≤ -1/7

  j ≥ 0 なので矛盾！
  → n₀ ≡ 3 (mod 16) は不可能。 ✓
""")

# n₀ ≡ 11 (mod 16) の解析
print("=" * 60)
print("n₀ ≡ 11 (mod 16) の解析 (k奇, k=2j+1):")
print("=" * 60)
print("""
  n₀ = 16j+11, T(T(n₀)) = 18j+13

  最小性: T(T(n₀)) ≥ n₀
  → 18j+13 ≥ 16j+11
  → 2j ≥ -2
  → j ≥ -1

  j ≥ 0 で常に成立。矛盾なし。
  しかも T(T(n₀)) = 18j+13 > 16j+11 = n₀ なので、
  T(T(n₀)) は n₀ より大きい。更なる追跡が必要。
""")


# ============================================================
# 3の倍数の制約
# ============================================================
print("\n" + "=" * 80)
print("【制約: 3の倍数】n₀ は3の倍数でない")
print("=" * 80)
print("""
証明:
  n₀ ≡ 0 (mod 3) とする。n₀ は奇数なので n₀ = 3m (m は奇数)。
  T(n₀) = (3·3m + 1) / 2^v₂(9m+1)

  探索31の結果: T(n) ≡ 0 (mod 3) にならない（n が奇数のとき）。
    証明: 3n+1 ≡ 1 (mod 3) なので T(n) = (3n+1)/2^k ≡ 2^(-k) (mod 3) ≢ 0 (mod 3)。

  直接的制約: n₀ が3の倍数であること自体の排除は？

  n₀ = 3m の場合:
    T(n₀) は3の倍数でない。T(n₀) も1に到達しない。
    T(n₀) < n₀ になるか？ → n₀ ≡ 1 (mod 4) なら Yes（制約2）。
    n₀ ≡ 3 (mod 4) かつ 3|n₀ のとき:
      n₀ = 3(4l+1) = 12l+3 → mod 8:
        l=0: 3, l=1: 15 ≡ 7, l=2: 27 ≡ 3, ...
      直接排除はできないが、mod 条件と組み合わせると制約が強まる。
""")

# 3の倍数チェック
print("生存クラスの中で3の倍数のもの:")
final_modulus = 2**13  # 最後のmodulus
surviving_and_div3 = []
surviving_and_not_div3 = []
for r in sorted(surviving):
    if r % 3 == 0:
        surviving_and_div3.append(r)
    else:
        surviving_and_not_div3.append(r)

print(f"  3の倍数: {len(surviving_and_div3)} / {len(surviving)}")
if surviving_and_div3 and len(surviving_and_div3) <= 30:
    print(f"  具体値: {surviving_and_div3}")
print(f"  3の倍数でない: {len(surviving_and_not_div3)} / {len(surviving)}")


# ============================================================
# 高次の排除: 再帰的解析
# ============================================================
print("\n" + "=" * 80)
print("【拡張解析】深い軌道追跡による排除")
print("=" * 80)

def deep_analyze(n0_mod, modulus, max_iter=50):
    """
    より深い軌道追跡。
    n₀ = modulus * j + n0_mod として T を繰り返し適用。
    a*j + b の形で追跡し、排除できるか判定。

    偶数になったら2で割り、奇数なら T を適用。
    """
    a, b = modulus, n0_mod
    history = [(a, b, "init")]

    for step in range(1, max_iter + 1):
        if b % 2 == 0 and a % 2 == 0:
            a //= 2
            b //= 2
            history.append((a, b, "div2"))
            continue
        elif b % 2 == 0 and a % 2 == 1:
            return False, "偶奇不定", step, history

        # 奇数: 3x+1
        a_new = 3 * a
        b_new = 3 * b + 1

        # 2で割れるだけ割る
        v2_a = v2(a_new)
        v2_b = v2(b_new)

        if v2_a >= v2_b:
            divisor = 2 ** v2_b
            a = a_new // divisor
            b = b_new // divisor
            history.append((a, b, f"T (v2={v2_b})"))

            # 最小性チェック
            coeff = a - modulus
            rhs = n0_mod - b

            if coeff < 0 and rhs > 0:
                # T^step(n₀) < n₀ が全 j≥0 で成立 → 矛盾
                return True, f"step {step}: {a}j+{b} < {modulus}j+{n0_mod} (∀j≥0)", step, history
            elif coeff < 0 and rhs <= 0:
                j_max = (-rhs) // (-coeff)
                # 有限個の候補
                all_reach = True
                for jj in range(j_max + 1):
                    candidate = modulus * jj + n0_mod
                    if candidate < 2:
                        continue
                    if not reaches_one(candidate, max_steps=1000000):
                        all_reach = False
                        break
                if all_reach:
                    return True, f"step {step}: j≤{j_max}, 全候補1到達", step, history
        else:
            return False, "v2不定", step, history

    return False, "最大ステップ到達", max_iter, history


# mod 32 の詳細解析
print("\n--- mod 32 の生存候補の深い解析 ---")
surviving_32 = set()
for r in [3, 7, 11, 15, 19, 23, 27, 31]:
    result, reason, depth = analyze_residue_chain(r, 32)
    if not result:
        surviving_32.add(r)
    status = "排除✓" if result else "生存✗"
    print(f"  n₀ ≡ {r:2d} (mod 32): {status} ({reason})")

print(f"\n  mod 32 生存: {sorted(surviving_32)}")

# 深い解析
print("\n--- 深い軌道追跡 ---")
for r in sorted(surviving_32):
    result, reason, step, history = deep_analyze(r, 32, max_iter=100)
    status = "排除✓" if result else "生存✗"
    print(f"  n₀ ≡ {r:2d} (mod 32): {status} (step={step}, {reason})")


# ============================================================
# mod 2^k の排除率の要約
# ============================================================
print("\n" + "=" * 80)
print("【要約】mod 2^k での排除率")
print("=" * 80)

surviving_set = {1}  # 奇数のみ → mod 2 で {1}
print(f"{'k':>3} {'mod':>8} {'候補':>6} {'生存':>6} {'排除':>6} {'排除率':>10} {'密度':>10}")
print("-" * 60)

# k=1: 奇数
print(f"{'1':>3} {'2':>8} {'1':>6} {'1':>6} {'0':>6} {'0.00%':>10} {'50.00%':>10}")

# k=2: mod 4, 制約2で ≡1(mod4) 排除
surviving_set = {3}
print(f"{'2':>3} {'4':>8} {'2':>6} {'1':>6} {'1':>6} {'50.00%':>10} {'25.00%':>10}")

# k=3以降: 系統的計算
all_surviving = {3, 7}  # mod 8

for k in range(3, 16):
    modulus = 2 ** k
    new_surviving = set()

    for r in sorted(all_surviving):
        for ext in [r, r + modulus]:
            result, reason, step, history = deep_analyze(ext, 2 * modulus, max_iter=100)
            if not result:
                new_surviving.add(ext)

    next_mod = 2 * modulus
    total_odd_mod4_3 = next_mod // 4  # ≡3 mod 4 の個数
    all_surviving = new_surviving

    eliminated_count = total_odd_mod4_3 - len(all_surviving)
    elim_rate = eliminated_count / total_odd_mod4_3 * 100 if total_odd_mod4_3 > 0 else 0
    density = len(all_surviving) / next_mod * 100

    print(f"{k+1:>3} {next_mod:>8} {total_odd_mod4_3:>6} {len(all_surviving):>6} {eliminated_count:>6} {elim_rate:>9.2f}% {density:>9.4f}%")

print(f"\n最終生存クラス (mod {2**16}):")
print(f"  個数: {len(all_surviving)}")
if len(all_surviving) <= 50:
    for r in sorted(all_surviving):
        print(f"    {r} (= {bin(r)})")


# ============================================================
# n₀ の下界との組み合わせ
# ============================================================
print("\n" + "=" * 80)
print("【下界との組み合わせ】")
print("=" * 80)
print("""
既知の数値検証結果:
  n ≤ 2.36 × 10²¹ では全て1に到達（Barina, 2021）
  → n₀ > 2.36 × 10²¹

我々の制約:
  1. n₀ は奇数
  2. n₀ ≡ 3 (mod 4)
  3. n₀ ≡ 3 (mod 16) は不可能 → n₀ ≡ 7 or 11 or 15 (mod 16) のいずれか
     （ただし mod 8 では 3 or 7、mod 16 では 3 が排除されるので 7, 11, 15 のうち生存するもの）
  4. n₀ は3の倍数でない（T(n) が3の倍数にならないことからの間接的制約ではなく、
     直接排除はできない場合もある）
  5. n₀ > 2.36 × 10²¹
""")

lower_bound = 2.36e21
final_mod = 2**16
surviving_count = len(all_surviving)
density_in_mod = surviving_count / final_mod

print(f"密度解析:")
print(f"  mod {final_mod} での生存率: {surviving_count}/{final_mod} = {density_in_mod:.6f}")
print(f"  つまり自然数のうち約 {density_in_mod*100:.4f}% のみが n₀ の候補")
print(f"  [1, 10^25] の範囲での候補数: 約 {density_in_mod * 1e25:.2e}")
print(f"  [2.36×10²¹, 10^25] の範囲での候補数: 約 {density_in_mod * (1e25 - lower_bound):.2e}")


# ============================================================
# 追加の代数的制約
# ============================================================
print("\n" + "=" * 80)
print("【追加制約】代数的性質")
print("=" * 80)

print("""
定理 (Terras, 1976):
  ほぼ全ての正整数 n に対して、コラッツ軌道はいつか n 未満の値に到達する。
  （密度1で stopping time が有限）

定理 (Krasikov-Lagarias, 2003):
  x 以下で1に到達する整数の個数は x^0.84 以上。

n₀ への含意:
  - n₀ は統計的に極めて稀な例外でなければならない
  - n₀ の軌道は永遠に n₀ 以上の値にとどまるか、サイクルに入る
  - サイクルの場合: Eliahou (1993) により 1以外のサイクルの最小元 > 10^17
    Simons & de Weger (2005) により 1以外のサイクルは長さ > 10^7
""")

# ============================================================
# 軌道の上昇・下降パターン制約
# ============================================================
print("\n" + "=" * 80)
print("【軌道パターン制約】")
print("=" * 80)

print("生存クラスの T による初期軌道パターン:")
final_survivors = sorted(all_surviving)[:20]  # 最初の20個

for r in final_survivors:
    # 具体的な小さい値で軌道を追跡
    n = r  # mod 2^16 の代表元
    if n < 2:
        continue
    traj = [n]
    current = n
    for _ in range(10):
        if current % 2 == 0:
            current = current // 2
        else:
            current = T(current)
        traj.append(current)
        if current == 1:
            break

    ascents = sum(1 for i in range(len(traj)-1) if traj[i+1] > traj[i])
    descents = sum(1 for i in range(len(traj)-1) if traj[i+1] < traj[i])
    print(f"  n₀ ≡ {r:5d} (mod {2**16}): 最初の10ステップ 上昇{ascents}/下降{descents}")
    print(f"    軌道(代表元): {traj[:8]}...")


# ============================================================
# 結論
# ============================================================
print("\n" + "=" * 80)
print("【結論】探索36のまとめ")
print("=" * 80)
print(f"""
背理法による最小反例 n₀ の制約:

1. n₀ は奇数                          [確定]
2. n₀ ≡ 3 (mod 4)                    [確定] (≡1 mod 4 → T(n₀)<n₀ で矛盾)
3. n₀ ≡ 3 (mod 16) は不可能           [確定] (T(T(n₀))<n₀ で矛盾)
4. mod {2**16} での生存クラス: {surviving_count} / {2**16}
   密度: {density_in_mod*100:.4f}%
5. n₀ > 2.36 × 10²¹                  [数値検証による]
6. T(n₀) は3の倍数でない               [確定]
7. n₀ のサイクルがあれば長さ > 10^7     [Simons & de Weger]

核心的洞察:
  mod 2^k で k を大きくするごとに、排除できる residue class が増加する。
  しかし排除率は 100% には到達しない（Collatz予想の困難さの反映）。
  各段階で約半分の候補が生き残り、密度は指数的に減少するが零にはならない。

  この「排除しきれない」性質こそが、Collatz予想が未解決である理由の一端を示している。
  背理法で完全に矛盾を導くには、mod 2^k の解析だけでは不十分であり、
  異なる手法（解析的、力学系的、etc.）との組み合わせが必要。
""")
