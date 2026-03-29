"""
v2(3^m - 1) の LTE公式の数値検証

LTE補題 (p=2の場合):
  v2(x^n - y^n) = v2(x-y) + v2(x+y) + v2(n) - 1  (n偶数, x,y奇数)

ここで x=3, y=1 とすると:
  v2(3^m - 1) の計算

ケース1: m奇数
  3^m - 1 ≡ 3-1 = 2 (mod 4) なので v2(3^m-1) = 1

ケース2: m偶数 (m>=2)
  LTE: v2(3^m - 1^m) = v2(3-1) + v2(3+1) + v2(m) - 1
                      = v2(2) + v2(4) + v2(m) - 1
                      = 1 + 2 + v2(m) - 1
                      = 2 + v2(m)

検証: m=1,...,100 について数値計算で確認
"""

def v2(n):
    """2-adic valuation of n"""
    if n == 0:
        return float('inf')
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count


def v2_3m_minus1_formula(m):
    """LTE公式による予測値"""
    if m == 0:
        return None  # 3^0 - 1 = 0, v2(0) は未定義 (∞)
    if m % 2 == 1:  # m奇数
        return 1
    else:  # m偶数
        return 2 + v2(m)


print("=" * 70)
print("v2(3^m - 1) の LTE公式検証")
print("=" * 70)
print()
print("公式:")
print("  m奇数: v2(3^m - 1) = 1")
print("  m偶数: v2(3^m - 1) = 2 + v2(m)")
print()

# 検証
print(f"{'m':>4} | {'3^m-1':>20} | {'v2(actual)':>10} | {'v2(formula)':>11} | {'match':>5}")
print("-" * 60)

all_match = True
for m in range(1, 51):
    val = 3**m - 1
    actual = v2(val)
    predicted = v2_3m_minus1_formula(m)
    match = actual == predicted
    if not match:
        all_match = False
    # 小さいmだけ 3^m-1 の値を表示
    val_str = str(val) if m <= 10 else "..."
    print(f"{m:>4} | {val_str:>20} | {actual:>10} | {predicted:>11} | {'OK' if match else 'FAIL':>5}")

print()
if all_match:
    print("全て一致! 公式は m=1..50 で正しい。")
else:
    print("不一致あり!")

# 大きな値でも検証
print()
print("大きな m での検証:")
large_ms = [100, 200, 256, 512, 1000, 1024, 2048, 4096, 10000]
for m in large_ms:
    val = 3**m - 1
    actual = v2(val)
    predicted = v2_3m_minus1_formula(m)
    match = actual == predicted
    print(f"  m={m:>5}: v2(actual)={actual:>6}, v2(formula)={predicted:>6}, {'OK' if match else 'FAIL'}")

print()
print("=" * 70)
print("理論的証明のスケッチ")
print("=" * 70)
print()
print("Case 1: m 奇数")
print("  3 ≡ -1 (mod 4) なので 3^m ≡ (-1)^m = -1 ≡ 3 (mod 4)")
print("  よって 3^m - 1 ≡ 2 (mod 4)")
print("  したがって v2(3^m - 1) = 1")
print()
print("Case 2: m 偶数, m >= 2")
print("  LTE補題 (p=2): v2(x^n - y^n) = v2(x-y) + v2(x+y) + v2(n) - 1")
print("  条件: n偶数, x,y奇数 (x=3, y=1 → 共に奇数)")
print("  v2(3^m - 1^m) = v2(3-1) + v2(3+1) + v2(m) - 1")
print("                = v2(2) + v2(4) + v2(m) - 1")
print("                = 1 + 2 + v2(m) - 1")
print("                = 2 + v2(m)")
print()
print("特殊ケース: m = 2^k のとき v2(3^(2^k) - 1) = 2 + k")
for k in range(1, 15):
    m = 2**k
    actual = v2(3**m - 1)
    predicted = 2 + k
    print(f"  k={k:>2}, m=2^k={m:>5}: v2={actual:>3}, predicted={predicted:>3}, {'OK' if actual==predicted else 'FAIL'}")

print()
print("=" * 70)
print("コラッツ予想との関連")
print("=" * 70)
print()
print("ascentConst(k) = 3^k - 2^k に対して:")
print("v2(ascentConst(k)) = v2(3^k - 2^k)")
print()

# v2(3^k - 2^k) の計算
print(f"{'k':>4} | {'3^k-2^k':>15} | {'v2(3^k-2^k)':>12} | {'v2(k)':>5} | {'k odd/even':>10}")
print("-" * 55)
for k in range(1, 31):
    val = 3**k - 2**k
    v = v2(val)
    vk = v2(k)
    parity = "odd" if k % 2 == 1 else "even"
    val_str = str(val) if k <= 12 else "..."
    print(f"{k:>4} | {val_str:>15} | {v:>12} | {vk:>5} | {parity:>10}")

print()
print("分析: v2(3^k - 2^k) はどうなるか?")
print()
print("3^k - 2^k = 2^k * (3^k/2^k - 1) = 2^k * ((3/2)^k - 1)")
print("これは直接LTEを適用できない（xとyが共に奇数でない）")
print()
print("代替アプローチ: 3^k - 2^k = 2^k * ((3/2)^k - 1)")
print("k奇数: 3^k - 2^k は奇数（3≡1, 2≡0 mod 2 → 3^k - 2^k ≡ 1 mod 2）")
print("k偶数: 因数分解可能")
print()

# k奇数のとき v2(3^k - 2^k) = 0 の検証
print("k奇数のとき v2(3^k - 2^k) の検証:")
for k in range(1, 30, 2):
    val = 3**k - 2**k
    v = v2(val)
    print(f"  k={k}: v2 = {v}")

print()

# k偶数のとき
print("k偶数のとき v2(3^k - 2^k) の検証:")
for k in range(2, 30, 2):
    val = 3**k - 2**k
    v = v2(val)
    vk = v2(k)
    # 仮説: v2(3^k - 2^k) = ?
    print(f"  k={k}: v2(3^k-2^k) = {v}, v2(k) = {vk}")

print()
print("=" * 70)
print("追加分析: v2(3^m - 1) と Syracuse 軌道の関係")
print("=" * 70)
print()
print("Syracuse 固定点 n = (2^m-1)/3 (mが偶数) について:")
print("3n+1 = 2^m であり、v2(3n+1) = m")
print()
print("もし n = (3^m - 1)/2 の形ならば:")
for m in range(1, 16):
    val = 3**m - 1
    if val % 2 == 0:
        n = val // 2
        three_n_plus_1 = 3*n + 1
        v = v2(three_n_plus_1)
        print(f"  m={m:>2}: n=(3^m-1)/2={n:>8}, 3n+1={three_n_plus_1:>10}, v2(3n+1)={v:>3}")
        print(f"         3n+1 = (3*(3^m-1)/2)+1 = (3^{m+1}-3+2)/2 = (3^{m+1}-1)/2")

print()
print("=" * 70)
print("まとめ: Lean形式化に向けた補題の整理")
print("=" * 70)
print()
print("Lemma v2_three_pow_sub_one_odd (m : N) (hm : m % 2 = 1) (hm_pos : m >= 1):")
print("  v2(3^m - 1) = 1")
print()
print("Lemma v2_three_pow_sub_one_even (m : N) (hm : m % 2 = 0) (hm_pos : m >= 2):")
print("  v2(3^m - 1) = 2 + v2(m)")
print()
print("これらは以下の既存補題を拡張する:")
print("  - v2_pow_two: v2(2^m) = m")
print("  - v2_two_mul: v2(2n) = 1 + v2(n)")
print("  - v2_even: v2(n) = 1 + v2(n/2) (n偶数)")
print("  - v2_odd: v2(n) = 0 (n奇数)")
