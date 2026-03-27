"""
mod 64 での連続上昇ステップ数の分布を調べる。

Syracuse関数: T(n) = (3n+1) / 2^{v2(3n+1)}
連続上昇 = v2(3n+1) = 1 が続く回数（T(n) > n となるステップ）

Hensel attrition の予測:
  k回連続上昇 ⟺ n ≡ 2^{k+1} - 1 (mod 2^{k+1})

  k=0: v2=1でない（上昇しない）→ n ≡ 1 (mod 4) のとき v2≥2
  k=1: 1回だけ上昇 → n ≡ 3 (mod 8) だが n ≢ 7 (mod 8)...

正確には:
  v2(3n+1) = 1 ⟺ (3n+1)/2 が奇数 ⟺ 3n+1 ≡ 2 (mod 4) ⟺ n ≡ 1 (mod 4)?
  いや、3n+1: n=1→4, v2=2; n=3→10, v2=1; n=5→16, v2=4; n=7→22, v2=1

  n ≡ 1 (mod 4): 3*1+1=4, v2=2; 3*5+1=16, v2=4 → v2≥2
  n ≡ 3 (mod 4): 3*3+1=10, v2=1; 3*7+1=22, v2=1 → v2=1

  つまり v2(3n+1)=1 ⟺ n ≡ 3 (mod 4)

連続上昇の定義を明確に:
  奇数nから始めて、T(n) を計算。T(n) > n なら「上昇」。
  v2(3n+1)=1 のとき T(n) = (3n+1)/2 > n（常に上昇）。
  連続上昇回数 = T を繰り返し適用して、v2=1が続く回数。
"""

import json
from collections import defaultdict

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function T(n) = (3n+1)/2^{v2(3n+1)}"""
    val = 3 * n + 1
    return val // (2 ** v2(val))

def consecutive_ascents(n):
    """
    連続上昇ステップ数を計算。
    v2(3n+1) = 1 が続く回数を数える。
    v2=1 なら T(n) = (3n+1)/2 > n（上昇）。
    """
    count = 0
    current = n
    while True:
        val = 3 * current + 1
        v = v2(val)
        if v == 1:
            count += 1
            current = val // 2  # 次の奇数
        else:
            break
    return count

def hensel_prediction(r, mod):
    """
    Hensel attrition による予測:
    k回連続上昇 ⟺ n ≡ 2^{k+1} - 1 (mod 2^{k+1})

    r mod mod での予測連続上昇回数を返す。
    """
    # n ≡ r (mod mod) のとき、最大何回連続上昇するか
    # k回連続上昇の条件: n ≡ -1 (mod 4), n ≡ -1 (mod 8), ..., n ≡ -1 (mod 2^{k+1})
    # つまり n ≡ 2^{k+1}-1 (mod 2^{k+1})

    # r mod 4 ≠ 3 なら k=0
    # r mod 4 = 3 かつ r mod 8 ≠ 7 なら k=1
    # r mod 8 = 7 かつ r mod 16 ≠ 15 なら k=2
    # etc.

    k = 0
    power = 4  # 2^{k+1} starts at 2^1=2, but condition is mod 2^{k+1}
    while power <= mod:
        if r % power == power - 1:
            k += 1
            power *= 2
        else:
            break
    return k

# --- メイン計算 ---
MOD = 64
odd_residues = [r for r in range(MOD) if r % 2 == 1]  # 32個の奇数剰余類

print(f"=== mod {MOD} での連続上昇ステップ数の分布 ===\n")

# 各剰余類での連続上昇ステップ数を計算（代表元で）
results = {}
for r in odd_residues:
    # 複数の代表元で確認（rが0の場合は避ける）
    ascents_list = []
    for k in range(100):
        n = r + MOD * k
        if n == 0:
            continue
        if n % 2 == 0:
            continue
        a = consecutive_ascents(n)
        ascents_list.append(a)

    # 全て同じ値か確認
    unique_vals = set(ascents_list)
    if len(unique_vals) == 1:
        ascent_val = ascents_list[0]
        consistent = True
    else:
        ascent_val = ascents_list[0]  # 最初の値
        consistent = False

    hensel_pred = hensel_prediction(r, MOD)

    results[r] = {
        'ascent': ascent_val,
        'consistent': consistent,
        'unique_vals': sorted(unique_vals),
        'hensel_pred': hensel_pred,
        'match': ascent_val == hensel_pred if consistent else None
    }

# 結果表示
print(f"{'残余':>4} {'連続上昇':>8} {'一致?':>5} {'Hensel予測':>10} {'整合':>5} {'備考'}")
print("-" * 70)

all_match = True
mismatch_details = []

for r in odd_residues:
    res = results[r]
    if res['consistent']:
        consistency = "Yes"
        match_str = "○" if res['match'] else "×"
        if not res['match']:
            all_match = False
            mismatch_details.append(f"r={r}: 実測={res['ascent']}, Hensel={res['hensel_pred']}")
        note = ""
    else:
        consistency = "No"
        match_str = "?"
        all_match = False
        note = f"値が変動: {res['unique_vals']}"
        mismatch_details.append(f"r={r}: 値が変動 {res['unique_vals']}, Hensel={res['hensel_pred']}")

    print(f"{r:>4} {res['ascent']:>8} {consistency:>5} {res['hensel_pred']:>10} {match_str:>5}  {note}")

print()

# 連続上昇ステップ数別の剰余類数
ascent_count = defaultdict(list)
for r in odd_residues:
    res = results[r]
    if res['consistent']:
        ascent_count[res['ascent']].append(r)

print("=== 連続上昇ステップ数別の剰余類分布 ===")
for k in sorted(ascent_count.keys()):
    residues = ascent_count[k]
    # Hensel予測: k回連続上昇する割合は 1/2^{k+1} - 1/2^{k+2} = 1/2^{k+2}
    # mod 64 での予測個数: 32 * (1/2^{k+1} - 1/2^{k+2}) ... ただし最大kは制限
    print(f"  k={k}: {len(residues)}個 → {residues}")

# Hensel理論との比較
print("\n=== Hensel attrition 理論との比較 ===")
print("理論: k回連続上昇 ⟺ n ≡ 2^{k+1}-1 (mod 2^{k+1})")
print("  k=0: n ≡ 1 (mod 4) → mod64で16個 (1/2の奇数)")
print("  k=1: n ≡ 3 (mod 8) → mod64で8個 (1/4の奇数)")
print("  k=2: n ≡ 7 (mod 16) → mod64で4個 (1/8の奇数)")
print("  k=3: n ≡ 15 (mod 32) → mod64で2個 (1/16の奇数)")
print("  k=4: n ≡ 31 (mod 64) → mod64で1個 (1/32の奇数)")
print("  k≥5: n ≡ 63 (mod 64) → mod64では判定不能（k=5は mod128が必要）")

# 実際のk=5以上の検証（mod 128）
print("\n=== mod 128 でのk≥5検証 ===")
for r in [63, 63+64]:  # mod 128 で 63 と 127
    ascents_list = []
    for k_rep in range(100):
        n = r + 128 * k_rep
        if n == 0:
            continue
        a = consecutive_ascents(n)
        ascents_list.append(a)
    unique = set(ascents_list)
    hensel = hensel_prediction(r, 128)
    print(f"  r={r} (mod 128): 連続上昇 = {unique}, Hensel予測 = {hensel}")

# E[v2] の検証
print("\n=== 平均 v2 値の検証 ===")
total_v2 = 0
count = 0
for n in range(1, 100000, 2):  # 奇数のみ
    val = 3 * n + 1
    total_v2 += v2(val)
    count += 1
avg_v2 = total_v2 / count
print(f"  E[v2(3n+1)] for n=1,3,...,99999: {avg_v2:.6f} (理論値: 2.0)")

# 連続上昇の平均回数
total_ascent = 0
count = 0
for n in range(1, 100000, 2):
    total_ascent += consecutive_ascents(n)
    count += 1
avg_ascent = total_ascent / count
print(f"  E[連続上昇回数] for n=1,3,...,99999: {avg_ascent:.6f}")
print(f"  理論値（幾何分布 p=1/2）: Σ k*(1/2)^{'{k+1}'} = 1.0")

# v2の分布とHensel
print("\n=== 初回 v2 値の mod 64 分布 ===")
print(f"{'残余':>4} {'v2(3r+1)':>10} {'2進表現':>20}")
print("-" * 40)
for r in odd_residues:
    val = 3 * r + 1
    v = v2(val)
    # 2^v で実際の構造を見る
    print(f"{r:>4} {v:>10}   {bin(r):>20}")

# 最終まとめ
print("\n" + "=" * 70)
if all_match:
    print("結論: 全剰余類でHensel attrition予測と完全に整合！")
else:
    print("不整合が見つかった剰余類:")
    for d in mismatch_details:
        print(f"  {d}")

# --- JSON出力 ---
print("\n\n=== JSON OUTPUT ===")

findings = [
    f"mod 64 の全32奇数剰余類で連続上昇ステップ数を計算完了",
    f"E[v2(3n+1)] = {avg_v2:.6f}（理論値2.0と整合）",
    f"E[連続上昇回数] = {avg_ascent:.6f}（幾何分布の理論値1.0と近い）",
]

if all_match:
    findings.append("全剰余類でHensel attrition予測と完全整合")
else:
    findings.append(f"不整合あり: {len(mismatch_details)}件")

# 分布情報
for k in sorted(ascent_count.keys()):
    findings.append(f"k={k}（{k}回連続上昇）: {len(ascent_count[k])}個の剰余類")

output = {
    "title": "mod 64 での連続上昇ステップ数の分布",
    "approach": f"奇数nをmod {MOD}で分類し、各剰余類でSyracuse列の連続上昇（v2=1が続く回数）を計算。100個の代表元で一致性を確認し、Hensel attrition予測と比較した。",
    "findings": findings,
    "hypotheses": [
        "連続上昇回数はn mod 2^{k+1}で完全に決定される（Hensel attrition）",
        "mod 64では最大k=5まで判定可能、k≥6にはmod 128以上が必要"
    ],
    "dead_ends": [],
    "scripts_created": ["collatz_mod64_ascent.py"],
    "outcome": "",  # 実行後に判定
    "next_directions": [
        "mod 256やmod 1024での拡張分析",
        "連続上昇後の下降幅（v2≥2の値）のmod依存性",
        "連続上昇回数と到達最大値・停止時間の相関"
    ],
    "details": ""
}
