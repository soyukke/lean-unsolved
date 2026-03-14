#!/usr/bin/env python3
"""
コラッツ予想の探索11補助:
mod 2^k でのSyracuse関数の完全な振る舞い表を作成する。
"""

from collections import defaultdict
import math

# ===== ユーティリティ =====

def v2(n):
    """n の2-adic valuation (n を割り切る2の最大冪)"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def syracuse(n):
    """Syracuse関数: 奇数 n に対して (3n+1) / 2^{v2(3n+1)} を返す"""
    assert n % 2 == 1
    val = 3 * n + 1
    return val // (2 ** v2(val))


def collatz_step(n):
    """コラッツの1ステップ: 奇数なら3n+1、偶数ならn/2"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1


# =====================================================================
# 1. mod 8 での完全分類表
# =====================================================================
print("=" * 80)
print("1. mod 8 での完全分類表 (奇数 residue class)")
print("=" * 80)

def analyze_mod(mod_val, data_range=10000):
    """mod mod_val での奇数residue classの振る舞いを解析"""
    odd_residues = [r for r in range(mod_val) if r % 2 == 1]

    # 実データ収集
    data = defaultdict(lambda: {"v2_vals": set(), "T_mod": set(), "ascent": 0, "descent": 0, "count": 0})

    for n in range(1, data_range + 1, 2):  # 奇数のみ
        r = n % mod_val
        val_3n1 = 3 * n + 1
        v = v2(val_3n1)
        T = val_3n1 // (2 ** v)
        T_mod = T % mod_val

        data[r]["v2_vals"].add(v)
        data[r]["T_mod"].add(T_mod)
        data[r]["count"] += 1
        if T > n:
            data[r]["ascent"] += 1
        else:
            data[r]["descent"] += 1

    return odd_residues, data


def print_table(mod_val, odd_residues, data):
    print(f"\n{'r':>4} | {'v2(3r+1)':>12} | {'v2確定?':>7} | {'T(r) mod {}'.format(mod_val):>14} | {'T確定?':>6} | {'上昇率':>8}")
    print("-" * 70)
    for r in odd_residues:
        d = data[r]
        v2_str = ",".join(map(str, sorted(d["v2_vals"])))
        v2_fixed = "Yes" if len(d["v2_vals"]) == 1 else "No"
        t_str = ",".join(map(str, sorted(d["T_mod"])))
        t_fixed = "Yes" if len(d["T_mod"]) == 1 else "No"
        total = d["ascent"] + d["descent"]
        asc_rate = d["ascent"] / total if total > 0 else 0
        print(f"{r:>4} | {v2_str:>12} | {v2_fixed:>7} | {t_str:>14} | {t_fixed:>6} | {asc_rate:>8.4f}")

    # 理論値も表示
    print(f"\n  理論的計算 (mod {mod_val}):")
    for r in odd_residues:
        val = 3 * r + 1
        v = v2(val)
        T_theory = (val // (2 ** v)) % mod_val
        # ただし v2 が mod_val で確定するかは、3r+1 の下位ビットだけで決まるか
        print(f"  r={r}: 3r+1={val}, v2(3r+1)={v}, T(r)=(3r+1)/2^{v}={val//(2**v)}, T(r) mod {mod_val} = {T_theory}")


# mod 8
odd_8, data_8 = analyze_mod(8, 10000)
print_table(8, odd_8, data_8)

# =====================================================================
# 2. mod 16 での完全分類表
# =====================================================================
print("\n" + "=" * 80)
print("2. mod 16 での完全分類表 (奇数 residue class)")
print("=" * 80)

odd_16, data_16 = analyze_mod(16, 10000)
print_table(16, odd_16, data_16)

# =====================================================================
# 3. mod 32, 64 での完全分類表
# =====================================================================
print("\n" + "=" * 80)
print("3. mod 32 での完全分類表 (奇数 residue class)")
print("=" * 80)

odd_32, data_32 = analyze_mod(32, 10000)
print_table(32, odd_32, data_32)

print("\n" + "=" * 80)
print("3. mod 64 での完全分類表 (奇数 residue class)")
print("=" * 80)

odd_64, data_64 = analyze_mod(64, 10000)
print_table(64, odd_64, data_64)

# =====================================================================
# 4. v2 が確定する最大の residue class の特定
# =====================================================================
print("\n" + "=" * 80)
print("4. v2 が確定する最大の residue class の特定")
print("=" * 80)

print(f"\n{'k':>3} | {'mod 2^k':>8} | {'奇数class数':>10} | {'v2確定数':>8} | {'v2確定率':>8} | {'T確定数':>8} | {'T確定率':>8}")
print("-" * 72)

for k in range(1, 11):
    mod_val = 2 ** k
    odd_residues, data = analyze_mod(mod_val, 10000)

    v2_fixed = sum(1 for r in odd_residues if len(data[r]["v2_vals"]) == 1)
    t_fixed = sum(1 for r in odd_residues if len(data[r]["T_mod"]) == 1)
    total = len(odd_residues)

    print(f"{k:>3} | {mod_val:>8} | {total:>10} | {v2_fixed:>8} | {v2_fixed/total:>8.4f} | {t_fixed:>8} | {t_fixed/total:>8.4f}")

# v2 の値が理論的にどう決まるか解説
print("\n  理論的考察:")
print("  奇数 n に対して、v2(3n+1) は n mod 2^k から決定できるか？")
print("  3n+1 の下位 k ビットは n の下位 k ビットだけで決まる。")
print("  したがって、v2(3n+1) >= k かどうかは n mod 2^k で判定可能。")
print("  v2(3n+1) < k なら、v2(3n+1) は n mod 2^k で完全に決定される。")

# 各 k での v2 確定の詳細
print("\n  v2 が確定しない residue class の例 (mod 2^k):")
for k in range(2, 7):
    mod_val = 2 ** k
    odd_residues, data = analyze_mod(mod_val, 50000)
    not_fixed = [(r, sorted(data[r]["v2_vals"])) for r in odd_residues if len(data[r]["v2_vals"]) > 1]
    if not_fixed:
        examples = not_fixed[:3]
        for r, vals in examples:
            print(f"    mod {mod_val}: r={r}, v2 の値 = {vals}")

# =====================================================================
# 5. 連続上昇回数の完全な特徴づけ
# =====================================================================
print("\n" + "=" * 80)
print("5. 連続上昇回数の完全な特徴づけ（末尾ビットパターンとの対応）")
print("=" * 80)

print("\n  仮説: 奇数 n の末尾の連続1ビット数 = 連続上昇回数")
print("  （Syracuse関数を繰り返し適用して、値が前の値より大きい間を「上昇」とする）")
print()

def count_trailing_ones(n):
    """n の末尾の連続1ビット数"""
    count = 0
    while n & 1:
        count += 1
        n >>= 1
    return count


def count_consecutive_ascents(n):
    """奇数 n から Syracuse 関数を繰り返し適用し、連続して上昇する回数を数える。
    ここでの「上昇」は T(m) > m (Syracuse値が元より大きい)。
    """
    assert n % 2 == 1
    count = 0
    current = n
    while True:
        next_val = syracuse(current)
        if next_val > current:
            count += 1
            current = next_val
        else:
            break
    return count


# 仮説の検証: 末尾連続1ビット ≠ 連続上昇回数の場合もあるので、
# まずは別の定義も試す

# 定義2: 3n+1 操作後、奇数になるまでの2除算回数が1回のとき「上昇」
# (つまり v2(3n+1)=1 のとき上昇、v2>=2のとき下降とみなす)
def count_consecutive_v2_one(n):
    """奇数 n から始めて、v2(3m+1)=1 が連続する回数"""
    assert n % 2 == 1
    count = 0
    current = n
    while current % 2 == 1:
        val = 3 * current + 1
        v = v2(val)
        if v == 1:
            count += 1
            current = val // 2
        else:
            break
    return count


# 検証
N_VERIFY = 100000
trailing_matches_ascent = 0
trailing_matches_v2one = 0
mismatch_examples_ascent = []
mismatch_examples_v2one = []

for n in range(1, N_VERIFY + 1, 2):
    t_ones = count_trailing_ones(n)
    c_asc = count_consecutive_ascents(n)
    c_v2 = count_consecutive_v2_one(n)

    if t_ones == c_asc:
        trailing_matches_ascent += 1
    elif len(mismatch_examples_ascent) < 5:
        mismatch_examples_ascent.append((n, bin(n), t_ones, c_asc))

    if t_ones == c_v2:
        trailing_matches_v2one += 1
    elif len(mismatch_examples_v2one) < 5:
        mismatch_examples_v2one.append((n, bin(n), t_ones, c_v2))

total_odd = N_VERIFY // 2

print(f"  検証範囲: 奇数 n = 1..{N_VERIFY} ({total_odd} 個)")
print()
print(f"  定義A: 連続上昇 (T(m) > m)")
print(f"    末尾1ビット数 == 連続上昇回数: {trailing_matches_ascent}/{total_odd} ({trailing_matches_ascent/total_odd*100:.2f}%)")
if mismatch_examples_ascent:
    print(f"    不一致例:")
    for n, b, t, c in mismatch_examples_ascent:
        print(f"      n={n} ({b}), trailing_ones={t}, consecutive_ascents={c}")

print()
print(f"  定義B: v2(3m+1)=1 が連続する回数")
print(f"    末尾1ビット数 == v2=1連続回数: {trailing_matches_v2one}/{total_odd} ({trailing_matches_v2one/total_odd*100:.2f}%)")
if mismatch_examples_v2one:
    print(f"    不一致例:")
    for n, b, t, c in mismatch_examples_v2one:
        print(f"      n={n} ({b}), trailing_ones={t}, v2_one_consecutive={c}")

# 末尾ビットパターンごとの統計
print("\n  末尾ビットパターンと v2(3n+1) の関係:")
print(f"  {'パターン':>14} | {'v2(3n+1)':>10} | {'理論値':>6} | {'一致率':>8} | {'サンプル数':>10}")
print("  " + "-" * 60)

patterns = [
    ("...0 (偶数)", None, None),  # skip
    ("...01", 1, 1),
    ("...011", 2, 1),  # 3*(4k+3)+1 = 12k+10 = 2(6k+5), v2=1
    ("...0111", 3, 1),
    ("...01111", 4, 1),
]

# 実際に末尾ビットパターンで v2 を調べる
for num_trailing in range(1, 9):
    # 末尾が num_trailing 個の 1 で、その前が 0
    # つまり n mod 2^(num_trailing+1) = 2^num_trailing - 1
    mask = (1 << (num_trailing + 1)) - 1
    target = (1 << num_trailing) - 1  # 0...0111...1

    v2_counts = defaultdict(int)
    total = 0
    for n in range(1, N_VERIFY + 1, 2):
        if (n & mask) == target:
            val = 3 * n + 1
            v = v2(val)
            v2_counts[v] += 1
            total += 1

    if total > 0:
        pattern_str = "...0" + "1" * num_trailing
        v2_str = ", ".join(f"v2={k}:{v}" for k, v in sorted(v2_counts.items()))
        # 理論的に: 3*(2^k - 1) + 1 = 3*2^k - 2 = 2*(3*2^{k-1} - 1), v2=1 for k>=1
        # ただし最小の代表元で計算
        rep = target
        if rep > 0:
            theory_v2 = v2(3 * rep + 1)
        else:
            theory_v2 = "N/A"
        dominant_v2 = max(v2_counts, key=v2_counts.get)
        match_rate = v2_counts[dominant_v2] / total
        print(f"  {pattern_str:>14} | {v2_str:>30} | {theory_v2:>6} | {match_rate:>8.4f} | {total:>10}")


# もっと正確な解析: n ≡ r (mod 2^k) のとき v2(3n+1) はどうなるか
print("\n  n ≡ r (mod 2^(k+1)) で、r の末尾 k 個が 1、k+1 番目が 0 のとき:")
print("  3n+1 = 3r+1 + 3*2^(k+1)*m")
print("  v2(3n+1) = v2(3r+1) （もし v2(3r+1) <= k なら）")
print()

for k in range(1, 9):
    mod = 2 ** (k + 1)
    r = (1 << k) - 1  # 末尾 k 個が 1、k+1 番目が 0
    val = 3 * r + 1
    v = v2(val)
    print(f"  k={k}: r={r} (={bin(r)}), 3r+1={val}, v2(3r+1)={v}, v2 <= k? {v <= k}")

# =====================================================================
# 6. k回連続上昇後の下降率の計算
# =====================================================================
print("\n" + "=" * 80)
print("6. k回連続上昇後の下降率の計算")
print("=" * 80)

print("\n  モデル: k回の上昇で (3/2)^k 倍、その後 1回の下降で 1/2^v2 倍")
print("  全体の縮小率 = (3/2)^k / 2^v2")
print()

# 実データから計算
N_DATA = 100000

# k回連続で v2=1 が続き、次に v2>=2 となるパターンを収集
ascent_data = defaultdict(lambda: {"count": 0, "total_ratio": 0.0, "v2_after": defaultdict(int)})

for n in range(1, N_DATA + 1, 2):
    current = n
    k = 0
    # v2=1 が連続する回数をカウント
    while current % 2 == 1:
        val = 3 * current + 1
        v = v2(val)
        if v == 1:
            k += 1
            current = val // 2
        else:
            # k回上昇後、v2=v で下降
            # 全体の比: 最終値 / 初期値
            final = val // (2 ** v)
            ratio = final / n
            ascent_data[k]["count"] += 1
            ascent_data[k]["total_ratio"] += ratio
            ascent_data[k]["v2_after"][v] += 1
            break

print(f"  {'k (上昇回数)':>12} | {'件数':>8} | {'平均縮小率':>12} | {'(3/2)^k':>10} | {'平均v2':>8} | {'理論縮小率 (3/2)^k*理論':>20}")
print("  " + "-" * 85)

for k in range(0, 15):
    d = ascent_data[k]
    if d["count"] == 0:
        continue
    avg_ratio = d["total_ratio"] / d["count"]
    three_half_k = (3 / 2) ** k

    # 平均 v2 (下降時の)
    total_v2 = sum(v * cnt for v, cnt in d["v2_after"].items())
    avg_v2 = total_v2 / d["count"]

    # 理論縮小率: (3/2)^k / 2^{avg_v2} は正確ではないが参考
    theory_ratio = three_half_k / (2 ** avg_v2)

    print(f"  {k:>12} | {d['count']:>8} | {avg_ratio:>12.6f} | {three_half_k:>10.4f} | {avg_v2:>8.3f} | {theory_ratio:>20.6f}")

# v2 の分布の詳細
print("\n  k回上昇後の v2(下降時) の分布:")
for k in range(0, 10):
    d = ascent_data[k]
    if d["count"] == 0:
        continue
    v2_dist = sorted(d["v2_after"].items())
    dist_str = ", ".join(f"v2={v}:{cnt}({cnt/d['count']*100:.1f}%)" for v, cnt in v2_dist[:6])
    print(f"  k={k}: {dist_str}")

# 理論的な縮小率の計算
print("\n  理論的な平均縮小率の考察:")
print("  k回上昇: 各ステップで v2(3m+1)=1 → 比率 3/2")
print("  最後に v2(3m+1)=v >= 2 → 比率 3/2^v")
print("  全体: (3/2)^k * 3/2^v = 3^(k+1) / 2^(k+v)")
print()
print("  log2(3) ≈ 1.585 なので、1回の上昇で log2(3/2) ≈ 0.585 ビット増加")
print("  1回の下降(v2=v)で v ビット減少")
print("  平均的に下降が上昇を上回れば、全体として減少傾向")

# 全体的な1ステップあたりの平均縮小率
print("\n  全ステップ平均での縮小率:")
total_steps = 0
total_log_ratio = 0.0
for n in range(1, N_DATA + 1, 2):
    val = 3 * n + 1
    v = v2(val)
    result = val // (2 ** v)
    total_steps += 1
    total_log_ratio += math.log2(result / n)

avg_log_ratio = total_log_ratio / total_steps
print(f"  Syracuse 1ステップの平均 log2(T(n)/n): {avg_log_ratio:.6f}")
print(f"  → 平均的に 2^{avg_log_ratio:.4f} ≈ {2**avg_log_ratio:.6f} 倍")
print(f"  → {'縮小傾向' if avg_log_ratio < 0 else '増大傾向'}")

# 各 v2 の出現確率
print("\n  奇数 n に対する v2(3n+1) の出現確率 (n=1..{})".format(N_DATA))
v2_total = defaultdict(int)
for n in range(1, N_DATA + 1, 2):
    v = v2(3 * n + 1)
    v2_total[v] += 1
total_odd_count = N_DATA // 2
print(f"  {'v2':>4} | {'件数':>8} | {'実測確率':>10} | {'理論確率 1/2^v':>14}")
print("  " + "-" * 45)
for v in sorted(v2_total.keys()):
    cnt = v2_total[v]
    print(f"  {v:>4} | {cnt:>8} | {cnt/total_odd_count:>10.6f} | {1/(2**v):>14.6f}")

print("\n  理論的期待値: E[v2] = Σ v/2^v = 2")
print(f"  実測平均 v2: {sum(v*c for v,c in v2_total.items())/total_odd_count:.6f}")
print(f"  E[log2(T(n)/n)] = log2(3) - E[v2] ≈ {math.log2(3) - 2:.6f}")
print(f"  （負なので、平均的に縮小する）")

print("\n" + "=" * 80)
print("解析完了")
print("=" * 80)
