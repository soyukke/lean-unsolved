"""
E[v2] = 2 の HasSum 形式化設計: 数学的分析

目標: HasSum (fun n => (n+1) / 2^{n+1}) 2

数学的背景:
- Syracuse関数で v2(3n+1) の期待値を計算する
- 奇数 n が一様ランダムなとき、v2(3n+1) の値は確率 1/2^j で j に等しい
  (正確には Pr[v2(3n+1) = j] = 1/2^j for j >= 1)
- E[v2] = sum_{j=1}^{infty} j / 2^j = 2

証明戦略:
A. 有限部分和: S_K = sum_{j=1}^K j/2^j = 2 - (K+2)/2^K  (帰納法)
B. 極限: HasSum (fun n => (n+1)/2^{n+1}) 2  (hasSum_iff_tendsto_nat_of_nonneg 使用)
"""

from fractions import Fraction

def partial_sum(K):
    """S_K = sum_{j=1}^K j/2^j"""
    s = Fraction(0)
    for j in range(1, K+1):
        s += Fraction(j, 2**j)
    return s

def formula(K):
    """2 - (K+2)/2^K"""
    return Fraction(2) - Fraction(K+2, 2**K)

print("=== 部分和公式 S_K = 2 - (K+2)/2^K の検証 ===")
for K in range(1, 20):
    s = partial_sum(K)
    f = formula(K)
    match = "OK" if s == f else "FAIL"
    print(f"K={K:2d}: S_K = {float(s):.10f}, formula = {float(f):.10f}, {match}")

print()
print("=== 帰納法のステップ検証 ===")
print("Base: K=1: S_1 = 1/2, formula = 2 - 3/2 = 1/2 OK")

for K in range(1, 10):
    # S_{K+1} = S_K + (K+1)/2^{K+1}
    sk = formula(K)
    step = Fraction(K+1, 2**(K+1))
    sk_plus_1_from_rec = sk + step
    sk_plus_1_from_formula = formula(K+1)
    match = "OK" if sk_plus_1_from_rec == sk_plus_1_from_formula else "FAIL"
    print(f"K={K:2d} -> K+1={K+1:2d}: S_K + (K+1)/2^(K+1) = {sk_plus_1_from_rec} = {sk_plus_1_from_formula} {match}")

print()
print("=== 帰納法ステップの代数的検証 ===")
print("S_{K+1} = S_K + (K+1)/2^{K+1}")
print("       = [2 - (K+2)/2^K] + (K+1)/2^{K+1}")
print("       = 2 - 2(K+2)/2^{K+1} + (K+1)/2^{K+1}")
print("       = 2 - [2(K+2) - (K+1)] / 2^{K+1}")
print("       = 2 - [2K+4 - K - 1] / 2^{K+1}")
print("       = 2 - (K+3) / 2^{K+1}")
print("       = 2 - ((K+1)+2) / 2^{K+1}  [K+3 = (K+1)+2]")
print("=> 公式が K+1 でも成立")

print()
print("=== 極限 K -> inf: (K+2)/2^K -> 0 の確認 ===")
for K in [10, 20, 50, 100]:
    val = Fraction(K+2, 2**K)
    print(f"K={K:3d}: (K+2)/2^K = {float(val):.20e}")

print()
print("=== HasSum 証明に必要な Mathlib 定理 ===")
print("1. hasSum_iff_tendsto_nat_of_nonneg: f >= 0 なら HasSum f r <=> Tendsto (partialSum) atTop (nhds r)")
print("2. tendsto_pow_atTop_nhds_zero_of_lt_one: 0 <= r < 1 => r^n -> 0")
print("3. hasSum_geometric_of_lt_one: HasSum (fun n => r^n) (1-r)^{-1} (0 <= r < 1)")
print("4. Finset.sum_range_succ: sum over range (n+1) = sum over range n + f n")

print()
print("=== 証明戦略の詳細 ===")
print("Thm B (有限部分和): 自然数上の等式")
print("  sum_{j in range K} (j+1) / 2^{j+1} = 2 - (K+2) / 2^K")
print("  ただし Lean では ℝ 上で証明")
print()
print("Thm C (HasSum): hasSum_iff_tendsto_nat_of_nonneg を使う")
print("  部分和 = sum_{j in range K} (j+1)/2^{j+1} = 2 - (K+2)/2^K")
print("  (K+2)/2^K -> 0 なので部分和 -> 2")
print()

print("=== インデックスの注意 ===")
print("数学的には sum_{j=1}^{infty} j/2^j = 2")
print("HasSum (fun n => (n+1)/2^{n+1}) 2 はインデックス 0 始まりへ変換")
print("  n=0: (0+1)/2^1 = 1/2")
print("  n=1: (1+1)/2^2 = 2/4 = 1/2")
print("  n=2: (2+1)/2^3 = 3/8")
print("  n=3: (3+1)/2^4 = 4/16 = 1/4")
print("  ...")
for n in range(10):
    val = Fraction(n+1, 2**(n+1))
    print(f"  f({n}) = {n+1}/{2**(n+1)} = {float(val):.6f}")
s = sum(Fraction(n+1, 2**(n+1)) for n in range(100))
print(f"  S_100 = {float(s):.15f} (limit = 2)")

