"""
f^k(n) = (3^k * n + c_k) / 2^k の c_k の漸化式を求める。

c_k の値: 1, 5, 19, 65, 211, 665, 2059, ...

漸化式を探索する。
"""

# c_k の値を計算
def f(x):
    return (3 * x + 1) // 2

def f_iter(k, x):
    for _ in range(k):
        x = f(x)
    return x

# c_k を求める
ck_values = []
for k in range(1, 12):
    modulus = 2**(k+1)
    n_test = modulus - 1
    fk = f_iter(k, n_test)
    ck = fk * (2**k) - (3**k) * n_test
    ck_values.append(ck)

print("c_k values:", ck_values)

# 漸化式: c_{k+1} = ?
print("\n=== c_{k+1} と c_k の関係 ===")
for i in range(len(ck_values) - 1):
    ratio = ck_values[i+1] / ck_values[i]
    diff = ck_values[i+1] - 3 * ck_values[i]
    print(f"c_{i+2} = {ck_values[i+1]}, c_{i+1} = {ck_values[i]}, "
          f"ratio = {ratio:.4f}, c_{i+2} - 3*c_{i+1} = {diff}")

# c_{k+1} = 3*c_k + 2 ?
print("\n=== 検証: c_{k+1} = 3*c_k + 2 ===")
for i in range(len(ck_values) - 1):
    expected = 3 * ck_values[i] + 2
    print(f"c_{i+2} = {ck_values[i+1]}, 3*c_{i+1} + 2 = {expected}, match = {ck_values[i+1] == expected}")

# 閉じた形: c_k = (3^k - 1)/(3-1) + something?
# c_{k+1} = 3*c_k + 2, c_1 = 1
# 特殊解: c = 2/(1-3) = -1
# 一般解: c_k = A * 3^k - 1
# c_1 = 3A - 1 = 1 → A = 2/3
# c_k = 2/3 * 3^k - 1 = 2 * 3^{k-1} - 1
print("\n=== 閉じた形の検証: c_k = 2 * 3^{k-1} - 1 ===")
for k in range(1, 12):
    closed = 2 * 3**(k-1) - 1
    print(f"k={k}: c_k = {ck_values[k-1]}, 2*3^{k-1}-1 = {closed}, match = {ck_values[k-1] == closed}")

# ではないようだ... もう一度正しくc_1を確認
# c_1 = 1, c_2 = 5
# c_2 = 3*1 + 2 = 5 OK
# c_3 = 3*5 + 2 = 17? でも c_3 = 19

# 再計算
print("\n=== c_{k+1} = a * c_k + b を探索 ===")
for a in range(1, 5):
    for b in range(-10, 10):
        all_match = True
        for i in range(len(ck_values) - 1):
            if ck_values[i+1] != a * ck_values[i] + b:
                all_match = False
                break
        if all_match:
            print(f"  Found: c_{{k+1}} = {a} * c_k + {b}")

# 特殊解の探索
# f(x) = (3x+1)/2 を繰り返す
# f^k(x) = (3^k * x + c_k) / 2^k
# c_k は f^k(0) * 2^k を計算すれば良い
# ただし f(0) = 1/2 なので整数でない...

# 正式に漸化式を導出:
# f^{k+1}(x) = f(f^k(x)) = (3 * (3^k x + c_k)/2^k + 1) / 2
# = (3^{k+1} x + 3 c_k + 2^k) / 2^{k+1}
# よって c_{k+1} = 3 c_k + 2^k

print("\n=== 正しい漸化式: c_{k+1} = 3*c_k + 2^k ===")
ck_computed = [1]  # c_1 = 1
for k in range(1, 11):
    ck_next = 3 * ck_computed[-1] + 2**k
    ck_computed.append(ck_next)

print("Computed c_k:", ck_computed)
print("Actual c_k:  ", ck_values)
print("Match:", ck_computed[:len(ck_values)] == ck_values)

# 閉じた形を求める
# c_{k+1} = 3 c_k + 2^k, c_1 = 1
# 一般解: c_k = A * 3^k + B * 2^k (同次解 + 特殊解)
# 同次: c_k = A * 3^k
# 特殊: c_k = B * 2^k を代入: B * 2^{k+1} = 3 * B * 2^k + 2^k
# 2B = 3B + 1 → B = -1
# 一般: c_k = A * 3^k - 2^k
# c_1 = 3A - 2 = 1 → A = 1
# c_k = 3^k - 2^k

print("\n=== 閉じた形の検証: c_k = 3^k - 2^k ===")
for k in range(1, 12):
    closed = 3**k - 2**k
    print(f"k={k}: c_k = {ck_values[k-1]}, 3^k - 2^k = {closed}, match = {ck_values[k-1] == closed}")

# まとめ
print("\n" + "=" * 60)
print("=== 重要な結論 ===")
print("f^k(n) = (3^k * n + 3^k - 2^k) / 2^k")
print("       = (3^k * (n + 1) - 2^k) / 2^k")
print("       = 3^k * (n + 1) / 2^k - 1")
print()

# 検証
for k in range(1, 8):
    modulus = 2**(k+1)
    for n in [modulus - 1, 3*modulus - 1, 5*modulus - 1]:
        fk = f_iter(k, n)
        formula = (3**k * (n + 1) - 2**k) // 2**k
        formula2 = (3**k * n + 3**k - 2**k) // 2**k
        print(f"  k={k}, n={n}: f^k(n) = {fk}, formula = {formula}, formula2 = {formula2}, "
              f"match = {fk == formula == formula2}")

# === 帰納ステップの mod 分析 ===
print("\n=== 帰納ステップの核心 ===")
print("n ≡ 2^{k+1}-1 (mod 2^{k+1}) のとき:")
print("f^k(n) = (3^k * (n+1) - 2^k) / 2^k")
print()
print("f^k(n) mod 4 を n mod 2^{k+2} で分析する:")
print("n = 2^{k+1}*q + (2^{k+1}-1) = 2^{k+1}*(q+1) - 1")
print("n + 1 = 2^{k+1}*(q+1)")
print("f^k(n) = (3^k * 2^{k+1} * (q+1) - 2^k) / 2^k")
print("       = 3^k * 2 * (q+1) - 1")
print("       = 2 * 3^k * (q+1) - 1")
print()
print("f^k(n) mod 4:")
print("= (2 * 3^k * (q+1) - 1) mod 4")
print("3^k mod 2 = 1 always (3^k is odd)")
print("so 2 * 3^k * (q+1) mod 4 = 2 * (q+1) mod 4 (since 3^k is odd)")
print()
print("If q is even (q+1 odd): 2*(q+1) mod 4 = 2, so f^k(n) mod 4 = 1")
print("If q is odd (q+1 even): 2*(q+1) mod 4 = 0, so f^k(n) mod 4 = -1 mod 4 = 3")
print()
print("q odd <=> n = 2^{k+1}*q + 2^{k+1}-1 with q odd")
print("       <=> n mod 2^{k+2} = 2^{k+2}-1")
print()

# 検証
print("=== 最終検証 ===")
for k in range(1, 8):
    modulus = 2**(k+1)
    modulus2 = 2**(k+2)
    target = modulus - 1  # 2^{k+1}-1
    target2 = modulus2 - 1  # 2^{k+2}-1

    for q in range(8):
        n = modulus * q + target
        fk = f_iter(k, n)
        q_parity = "odd" if q % 2 == 1 else "even"
        n_mod = n % modulus2
        expected_mod4 = 3 if q % 2 == 1 else 1
        print(f"  k={k}, q={q}({q_parity}), n={n}, n%{modulus2}={n_mod}, "
              f"f^{k}(n)={fk}, f^{k}(n)%4={fk%4}, expected={expected_mod4}, "
              f"match={fk%4 == expected_mod4}")
    print()
