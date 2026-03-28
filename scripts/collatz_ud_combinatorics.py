"""
探索086: 軌道の上昇/下降パターンの組合せ的数え上げ

Syracuse軌道をU(v2=1)/D(v2>=2)の2文字列として符号化し、
長さLの全可能文字列のうち実現可能なものを数え上げる。
禁止パターンの同定と漸化式の導出を目指す。
"""

import itertools
from collections import defaultdict, Counter
import math

# === Part 1: Syracuse関数とU/D符号化 ===

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^v2(3n+1) for odd n"""
    assert n % 2 == 1 and n > 0
    val = 3 * n + 1
    return val >> v2(val)

def get_ud_sequence(n, max_steps=200):
    """Get U/D sequence from Syracuse orbit of odd n.
    U = v2(3n+1) == 1 (上昇: bit length increases)
    D = v2(3n+1) >= 2 (下降: bit length decreases)
    Returns list of 'U' or 'D' and list of v2 values.
    """
    seq = []
    v2_seq = []
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        val = 3 * current + 1
        v = v2(val)
        v2_seq.append(v)
        seq.append('U' if v == 1 else 'D')
        current = val >> v
    return ''.join(seq), v2_seq

# === Part 2: 全奇数から実現されるU/D列を収集 ===

def collect_realized_patterns(max_n, pattern_length):
    """Collect all realized U/D patterns of given length from odd numbers up to max_n."""
    realized = set()
    for n in range(3, max_n + 1, 2):
        ud, _ = get_ud_sequence(n)
        for i in range(len(ud) - pattern_length + 1):
            realized.add(ud[i:i+pattern_length])
    return realized

print("=" * 70)
print("Part 1: U/D列の基本統計")
print("=" * 70)

# 小さい奇数のU/D列を表示
print("\n--- 小さい奇数のU/D列 ---")
for n in [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27, 31, 63, 127, 255]:
    ud, v2s = get_ud_sequence(n)
    print(f"n={n:5d}: {ud[:40]}  (len={len(ud)}, U率={ud.count('U')/len(ud) if ud else 0:.3f})")

# === Part 3: 長さLの実現可能パターン数え上げ ===

print("\n" + "=" * 70)
print("Part 2: 長さLの実現可能U/Dパターンの数え上げ")
print("=" * 70)

max_n = 100000  # 探索する奇数の上限

for L in range(1, 13):
    total_possible = 2**L  # 全可能な{U,D}^L列
    realized = collect_realized_patterns(max_n, L)
    forbidden_count = total_possible - len(realized)

    # 禁止パターンの一覧（短いLのみ）
    if L <= 6:
        all_patterns = set()
        for bits in range(total_possible):
            pat = ''.join('U' if (bits >> (L-1-i)) & 1 else 'D' for i in range(L))
            all_patterns.add(pat)
        forbidden = all_patterns - realized
        forbidden_list = sorted(forbidden)[:20]
        print(f"\nL={L:2d}: 実現={len(realized):5d}/{total_possible:5d} "
              f"(禁止={forbidden_count}, 実現率={len(realized)/total_possible:.4f})")
        if forbidden_list:
            print(f"  禁止パターン: {forbidden_list}")
    else:
        print(f"L={L:2d}: 実現={len(realized):5d}/{total_possible:5d} "
              f"(禁止={forbidden_count}, 実現率={len(realized)/total_possible:.4f})")

# === Part 4: U連続の最大長を調査 ===

print("\n" + "=" * 70)
print("Part 3: U連続（v2=1連続）の最大長")
print("=" * 70)

max_u_run = defaultdict(int)  # max_u_run[k] = そのk連続が出現したnの数

for n in range(3, max_n + 1, 2):
    ud, _ = get_ud_sequence(n)
    # 最大U連続を計算
    max_run = 0
    current_run = 0
    for c in ud:
        if c == 'U':
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    max_u_run[max_run] += 1

print(f"max_n = {max_n}")
for k in sorted(max_u_run.keys()):
    print(f"  最大U連続 = {k}: {max_u_run[k]} 個 ({max_u_run[k]/50000*100:.2f}%)")

# 具体的にU連続が長いnを探す
print("\n--- U連続が特に長い例 ---")
long_u_examples = []
for n in range(3, max_n + 1, 2):
    ud, v2s = get_ud_sequence(n)
    max_run = 0
    current_run = 0
    for c in ud:
        if c == 'U':
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    if max_run >= 6:
        long_u_examples.append((n, max_run, ud[:60]))

long_u_examples.sort(key=lambda x: -x[1])
for n, run, ud in long_u_examples[:10]:
    print(f"  n={n}: 最大U連続={run}, UD={ud}")

# === Part 5: D連続の最大長を調査 ===

print("\n" + "=" * 70)
print("Part 4: D連続（v2>=2連続）の最大長")
print("=" * 70)

max_d_run = defaultdict(int)

for n in range(3, max_n + 1, 2):
    ud, _ = get_ud_sequence(n)
    max_run = 0
    current_run = 0
    for c in ud:
        if c == 'D':
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    max_d_run[max_run] += 1

for k in sorted(max_d_run.keys()):
    print(f"  最大D連続 = {k}: {max_d_run[k]} 個 ({max_d_run[k]/50000*100:.2f}%)")

# === Part 6: 禁止パターンの構造分析 ===

print("\n" + "=" * 70)
print("Part 5: 禁止パターンの構造分析")
print("=" * 70)

# U連続の上限を厳密に調べる
# n mod 8 で v2(3n+1) が決まることを使う
# n ≡ 1 (mod 8) → v2(3n+1) = v2(3+1) = 2 → D
# n ≡ 3 (mod 8) → v2(3*3+1) = v2(10) = 1 → U
# n ≡ 5 (mod 8) → v2(3*5+1) = v2(16) = 4 → D
# n ≡ 7 (mod 8) → v2(3*7+1) = v2(22) = 1 → U

print("\n--- n mod 8 とU/D対応 ---")
for r in [1, 3, 5, 7]:
    v = v2(3*r + 1)
    ud = 'U' if v == 1 else 'D'
    print(f"  n ≡ {r} (mod 8) → v2(3n+1) = {v} → {ud}")

# より詳細: n mod 2^k で v2 を決定
print("\n--- n mod 2^k とv2(3n+1)の完全表 ---")
for k in [3, 4, 5]:
    mod = 2**k
    print(f"\n  mod 2^{k} = {mod}:")
    for r in range(1, mod, 2):
        v = v2(3*r + 1)
        ud = 'U' if v == 1 else 'D'
        print(f"    n ≡ {r:3d} (mod {mod}) → v2 = {v} → {ud}")

# === Part 7: U連続時の遷移を代数的に追跡 ===

print("\n" + "=" * 70)
print("Part 6: U連続（v2=1連続）の代数的追跡")
print("=" * 70)

# T(n) = (3n+1)/2 when v2(3n+1)=1
# For U to continue, we need v2(3*T(n)+1) = 1 too
# T(n) = (3n+1)/2, so 3*T(n)+1 = 3(3n+1)/2 + 1 = (9n+3+2)/2 = (9n+5)/2
# For this to be odd after dividing by 2 once, we need v2((9n+5)/2) = v2(9n+5) - 1 = 1
# So v2(9n+5) = 2, meaning 9n+5 ≡ 4 (mod 8), i.e., 9n ≡ -1 (mod 8), i.e., n ≡ 7 (mod 8)

print("U連続に必要な条件:")
print("  1回目のU: v2(3n+1) = 1 → n ≡ 3 or 7 (mod 8)")
print()

# 1 step U: n → (3n+1)/2 = T1
# Need v2(3n+1) = 1
# 2 steps U: T1 → (3*T1+1)/2 = T2
# Need v2(3*T1+1) = 1

# Let's trace algebraically
# U^k means k consecutive U steps
# After k U steps: n → (3^k * n + c_k) / 2^k where c_k satisfies some recurrence

print("U^k 後の値の公式:")
for k in range(1, 8):
    # Compute symbolically: after k U-steps, value = (3^k * n + c_k) / 2^k
    # c_1 = 1, c_{k+1} = 3*c_k + 2^k (from T_{k+1} = (3*T_k + 1)/2 = (3*(3^k*n+c_k)/2^k + 1)/2)
    # Actually let's just compute: T^k(n) when all v2=1
    # T(n) = (3n+1)/2
    # T^2(n) = (3*(3n+1)/2 + 1)/2 = (9n+3+2)/4 = (9n+5)/4
    # T^3(n) = (3*(9n+5)/4 + 1)/2 = (27n+15+4)/8 = (27n+19)/8
    # General: T^k(n) = (3^k * n + (3^k - 2^k) * 2 / (3-2) ???

    # Correct recurrence: a_k = 3^k, c_{k+1} = 3*c_k + 2^k, c_0 = 0
    # c_k = sum_{i=0}^{k-1} 3^{k-1-i} * 2^i = (3^k - 2^k) / (3-2) = 3^k - 2^k
    # Wait, let me compute directly
    c = 0
    for i in range(k):
        c = 3 * c + (1 << i)  # c_{i+1} = 3*c_i + 2^i
    # Actually the formula is T^k(n) = (3^k * n + c) / 2^k when all v2=1
    print(f"  U^{k}: T^{k}(n) = (3^{k}·n + {c}) / 2^{k}  = ({3**k}n + {c}) / {2**k}")

    # For T^k(n) to be a positive odd integer: 3^k * n + c ≡ 0 (mod 2^k) and result is odd
    # Also need 3^k * n + c > 0 (always true for n>=1)

    # Condition for v2(3*T^k(n)+1) = 1 (next step is also U):
    # This requires T^k(n) ≡ 3 or 7 (mod 8)

print()

# === Part 8: U連続可能性の mod 条件 ===

print("U^k 連続が可能なnの mod 条件:")
for k in range(1, 10):
    # Find all odd n in [1, 2^15] that have at least k consecutive U's at the start
    valid_n = []
    for n in range(1, 2**15, 2):
        ud, v2s = get_ud_sequence(n, max_steps=k+2)
        if len(ud) >= k and all(c == 'U' for c in ud[:k]):
            valid_n.append(n)

    if valid_n:
        # Find the mod pattern
        # Check mod 2^(k+2)
        mod = 2**(k+2)
        residues = sorted(set(n % mod for n in valid_n))
        density = len(valid_n) / (2**14)  # fraction of odd numbers

        if len(residues) <= 16:
            print(f"  U^{k}: 密度={density:.6f}, mod {mod} で {len(residues)} 剰余類: {residues[:16]}")
        else:
            # Try larger mod
            print(f"  U^{k}: 密度={density:.6f}, mod {mod} で {len(residues)} 剰余類")
    else:
        print(f"  U^{k}: 実現なし!")

# === Part 9: 禁止パターンの漸化式 ===

print("\n" + "=" * 70)
print("Part 7: 禁止パターン数の漸化式")
print("=" * 70)

# Count realized patterns more carefully with larger sample
max_n_large = 500000
realized_by_length = {}

for L in range(1, 16):
    realized = set()
    for n in range(3, max_n_large + 1, 2):
        ud, _ = get_ud_sequence(n, max_steps=L+5)
        for i in range(len(ud) - L + 1):
            realized.add(ud[i:i+L])
    realized_by_length[L] = realized

    total = 2**L
    r = len(realized)
    f = total - r
    print(f"  L={L:2d}: 実現={r:6d}/{total:6d}, 禁止={f:6d}, 実現率={r/total:.6f}")

# Check if forbidden patterns follow a pattern
print("\n--- 禁止パターン数の増加パターン ---")
forbidden_counts = []
for L in range(1, 16):
    total = 2**L
    r = len(realized_by_length[L])
    f = total - r
    forbidden_counts.append(f)

print("L:       ", [i for i in range(1, 16)])
print("禁止数:  ", forbidden_counts)
print("2^L:     ", [2**L for L in range(1, 16)])

# 禁止/実現の比率
print("\n禁止数の比率 f(L+1)/f(L):")
for i in range(1, len(forbidden_counts)):
    if forbidden_counts[i-1] > 0:
        ratio = forbidden_counts[i] / forbidden_counts[i-1]
        print(f"  f({i+2})/f({i+1}) = {forbidden_counts[i]}/{forbidden_counts[i-1]} = {ratio:.4f}")

# === Part 10: U連続上限の理論的分析 ===

print("\n" + "=" * 70)
print("Part 8: U連続上限の理論的分析")
print("=" * 70)

# For n starting with k consecutive U's:
# After k U-steps, value = (3^k * n + c_k) / 2^k
# Need all intermediate values to be odd and have v2(3*val+1)=1
# This is equivalent to a system of congruences mod 2^(k+1)

# Let's check: is there a maximum k?
# Since any k consecutive U's require n in a specific residue class mod 2^(k+2),
# and such residue classes always exist (they just get sparser),
# there is no absolute maximum k.

# But: does U^k appear as a SUBSTRING (not just prefix)?
# Answer should be yes for any k, just extremely rare.

# Search for long U runs in a targeted way
# n ≡ 3 (mod 4) gives v2=1 for first step
# Then the image (3n+1)/2 needs to also ≡ 3 or 7 (mod 8)

print("大きいnでの最大U連続探索:")
max_u_seen = 0
best_n = 0
for n in range(3, 2000001, 2):
    ud, _ = get_ud_sequence(n, max_steps=300)
    current_run = 0
    max_run = 0
    for c in ud:
        if c == 'U':
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    if max_run > max_u_seen:
        max_u_seen = max_run
        best_n = n
        print(f"  n={n}: 最大U連続={max_run}")

print(f"\n最大U連続記録: {max_u_seen} (n={best_n})")

# === Part 11: 遷移確率の解析 ===

print("\n" + "=" * 70)
print("Part 9: U/D遷移確率の解析")
print("=" * 70)

# Count transitions
trans = Counter()  # (prev, next) → count
for n in range(3, max_n + 1, 2):
    ud, _ = get_ud_sequence(n)
    for i in range(len(ud) - 1):
        trans[(ud[i], ud[i+1])] += 1

total_trans = sum(trans.values())
print("2文字遷移確率:")
for (a, b) in sorted(trans.keys()):
    p = trans[(a,b)] / total_trans
    # conditional
    cond_total = sum(trans[(a, x)] for x in ['U', 'D'])
    p_cond = trans[(a,b)] / cond_total if cond_total > 0 else 0
    print(f"  P({b}|{a}) = {p_cond:.6f}  (count={trans[(a,b)]})")

# 3-gram transitions
print("\n3文字遷移確率:")
trans3 = Counter()
for n in range(3, max_n + 1, 2):
    ud, _ = get_ud_sequence(n)
    for i in range(len(ud) - 2):
        trans3[ud[i:i+3]] += 1

total3 = sum(trans3.values())
for pat in sorted(trans3.keys()):
    p = trans3[pat] / total3
    prefix = pat[:2]
    cond_total = sum(trans3[prefix + x] for x in ['U', 'D'])
    p_cond = trans3[pat] / cond_total if cond_total > 0 else 0
    print(f"  P({pat[2]}|{pat[:2]}) = {p_cond:.6f}  ({pat}: count={trans3[pat]})")

# === Part 12: 禁止パターンの最小生成集合 ===

print("\n" + "=" * 70)
print("Part 10: 禁止パターンの最小生成集合（禁止パターンの核）")
print("=" * 70)

# A forbidden pattern p of length L is "minimal" if no proper substring of p is forbidden
# (i.e., it cannot be derived from shorter forbidden patterns)
print("最小禁止パターンの探索:")

all_forbidden = {}
for L in range(1, 13):
    total = 2**L
    all_pats = set()
    for bits in range(total):
        pat = ''.join('U' if (bits >> (L-1-i)) & 1 else 'D' for i in range(L))
        all_pats.add(pat)
    forbidden = all_pats - realized_by_length.get(L, set())
    all_forbidden[L] = forbidden

# Find minimal forbidden patterns
minimal_forbidden = []
for L in range(1, 13):
    for pat in sorted(all_forbidden.get(L, set())):
        # Check if any proper substring is already forbidden
        is_derived = False
        for L2 in range(1, L):
            for i in range(L - L2 + 1):
                if pat[i:i+L2] in all_forbidden.get(L2, set()):
                    is_derived = True
                    break
            if is_derived:
                break
        if not is_derived:
            minimal_forbidden.append(pat)
            print(f"  最小禁止: {pat} (長さ={L})")

if not minimal_forbidden:
    print("  長さ12以下に最小禁止パターンは見つからず!")
    print("  → 全ての{U,D}^L列がSyracuse軌道で実現可能（L≤12の範囲で）")

# Summary
print("\n" + "=" * 70)
print("=== まとめ ===")
print("=" * 70)
print(f"1. 長さL≤12の全U/D列 {sum(2**L for L in range(1,13))} パターン中、")
print(f"   禁止パターン数: {sum(len(all_forbidden.get(L, set())) for L in range(1,13))}")
print(f"2. 最大U連続(n≤{2000000}): {max_u_seen}")
print(f"3. U連続に上限はなく、任意のkでU^kは実現可能（密度は指数的に減少）")
print(f"4. P(U|U) ≈ {trans[('U','U')]/(trans[('U','U')]+trans[('U','D')]):.4f}, P(U|D) ≈ {trans[('D','U')]/(trans[('D','U')]+trans[('D','D')]):.4f}")
