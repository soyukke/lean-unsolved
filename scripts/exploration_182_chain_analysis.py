"""
探索182: chainOffset + chainElem + syracuse_chainElem の数学的分析

chainOffset: c(0) = 0, c(k+1) = 4*c(k) + 1
chainElem: chainElem(n, k) = 4^k * n + c(k)
主定理: syracuse(chainElem(n, k)) = syracuse(n) (n>=1, n奇数)

Step 1: chainOffset の閉形式を導出
Step 2: chainElem の性質を確認
Step 3: 主定理を帰納法で検証
"""

# chainOffset の閉形式
# c(0) = 0
# c(k+1) = 4*c(k) + 1
# これは漸化式 c(k+1) = 4*c(k) + 1 で、特解は c = -1/3
# 一般解: c(k) = A * 4^k - 1/3
# c(0) = 0 => A = 1/3
# c(k) = (4^k - 1) / 3

print("=== chainOffset の閉形式 ===")
def chainOffset_rec(k):
    if k == 0:
        return 0
    return 4 * chainOffset_rec(k-1) + 1

def chainOffset_closed(k):
    return (4**k - 1) // 3

for k in range(10):
    rec = chainOffset_rec(k)
    closed = chainOffset_closed(k)
    print(f"c({k}) = {rec} (rec) = {closed} (closed), match={rec==closed}")

print()
print("=== chainElem の値 ===")
def chainElem(n, k):
    return 4**k * n + chainOffset_closed(k)

# n=1 (奇数, >=1) の場合
print("n=1:")
for k in range(8):
    elem = chainElem(1, k)
    print(f"  chainElem(1, {k}) = {elem}, mod 2 = {elem % 2}")

print()
print("n=3:")
for k in range(6):
    elem = chainElem(3, k)
    print(f"  chainElem(3, {k}) = {elem}, mod 2 = {elem % 2}")

print()
print("=== chainElem の奇偶性 ===")
# chainElem(n, k) = 4^k * n + (4^k - 1)/3
# n が奇数のとき:
# k=0: 1*n + 0 = n (奇数)
# k=1: 4*n + 1 = 4n+1 (奇数、nが奇数なので 4*odd+1 = even+1 = odd)
# k>=1: 4^k * n + (4^k-1)/3
# 4^k は常に偶数(k>=1)なので 4^k * n は偶数
# (4^k - 1)/3: 4^1-1=3, /3=1(奇数); 4^2-1=15, /3=5(奇数); 4^3-1=63, /3=21(奇数)
# 一般に (4^k-1)/3 は k>=1 のとき奇数? 確認

print("(4^k - 1) / 3 mod 2:")
for k in range(10):
    val = (4**k - 1) // 3
    print(f"  k={k}: (4^{k}-1)/3 = {val}, mod 2 = {val % 2}")

# chainElem(n,k) mod 2 = (4^k * n + (4^k-1)/3) mod 2
# k=0: n mod 2 = 1 (n奇数)
# k>=1: (0 + 1) mod 2 = 1 (偶数 + 奇数 = 奇数)
# つまり chainElem(n,k) は常に奇数！
print()
print("=== chainElem は常に奇数（n奇数時）===")
for n in [1, 3, 5, 7, 9, 11]:
    for k in range(6):
        elem = chainElem(n, k)
        assert elem % 2 == 1, f"FAIL: chainElem({n},{k}) = {elem} is even!"
    print(f"  n={n}: all chainElem(n,0..5) are odd ✓")

print()
print("=== 主定理の検証: syracuse(chainElem(n,k)) = syracuse(n) ===")

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

# 帰納法の基底ケース (k=0): chainElem(n,0) = n なので syracuse(n) = syracuse(n) ✓
# 帰納ステップ (k -> k+1):
# chainElem(n, k+1) = 4^(k+1) * n + c(k+1)
#                    = 4 * (4^k * n) + 4*c(k) + 1
#                    = 4 * (4^k * n + c(k)) + 1
#                    = 4 * chainElem(n, k) + 1
# つまり chainElem(n, k+1) = 4 * chainElem(n, k) + 1
# 帰納法仮定: syracuse(chainElem(n, k)) = syracuse(n)
# syracuse_four_mul_add_one から:
#   syracuse(4 * chainElem(n,k) + 1) = syracuse(chainElem(n,k))
# したがって:
#   syracuse(chainElem(n, k+1)) = syracuse(chainElem(n, k)) = syracuse(n) ✓

print("帰納法による証明構造:")
print("  base: chainElem(n, 0) = n => syracuse(chainElem(n, 0)) = syracuse(n) ✓")
print("  step: chainElem(n, k+1) = 4 * chainElem(n, k) + 1")
print("        => syracuse(chainElem(n, k+1)) = syracuse(chainElem(n, k))  [by syracuse_four_mul_add_one]")
print("        => ... = syracuse(n)  [by IH]")
print()

# 数値検証
print("数値検証:")
for n in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]:
    target = syracuse(n)
    for k in range(8):
        elem = chainElem(n, k)
        result = syracuse(elem)
        ok = "✓" if result == target else "✗"
        if k <= 2 or not (result == target):
            print(f"  syracuse(chainElem({n},{k})) = syracuse({elem}) = {result}, expected {target} {ok}")
    print(f"  n={n}: all k=0..7 verified ✓")

print()
print("=== chainElem >= 1 の確認 ===")
# chainElem(n, k) = 4^k * n + (4^k - 1)/3
# n >= 1 のとき、4^k * n >= 4^k >= 1 なので chainElem >= 1
for n in [1, 3, 5]:
    for k in range(6):
        elem = chainElem(n, k)
        assert elem >= 1, f"FAIL: chainElem({n},{k}) = {elem} < 1"
    print(f"  n={n}: all chainElem >= 1 ✓")

print()
print("=== chainOffset の再帰関係の検証 (Lean形式化用) ===")
# c(k+1) = 4*c(k) + 1 を直接的に確認
# (4^(k+1) - 1)/3 = 4*(4^k - 1)/3 + 1 ?
# LHS = (4*4^k - 1)/3
# RHS = (4*4^k - 4)/3 + 1 = (4*4^k - 4 + 3)/3 = (4*4^k - 1)/3 ✓
print("c(k+1) = 4*c(k) + 1 verified algebraically ✓")

print()
print("=== chainElem の再帰関係の検証 ===")
# chainElem(n, k+1) = 4 * chainElem(n, k) + 1
# LHS = 4^(k+1) * n + c(k+1) = 4 * 4^k * n + 4*c(k) + 1
# RHS = 4 * (4^k * n + c(k)) + 1 = 4 * 4^k * n + 4*c(k) + 1 ✓
print("chainElem(n, k+1) = 4 * chainElem(n, k) + 1 verified algebraically ✓")

print()
print("=== Lean形式化で証明が必要な補題リスト ===")
print("1. chainOffset_zero: chainOffset 0 = 0")
print("2. chainOffset_succ: chainOffset (k+1) = 4 * chainOffset k + 1")
print("3. chainElem_zero: chainElem n 0 = n")
print("4. chainElem_succ: chainElem n (k+1) = 4 * chainElem n k + 1")
print("5. chainElem_odd: n % 2 = 1 → chainElem n k % 2 = 1")
print("6. chainElem_pos: n ≥ 1 → chainElem n k ≥ 1")
print("7. syracuse_chainElem: n ≥ 1 → n % 2 = 1 → syracuse (chainElem n k) = syracuse n")
