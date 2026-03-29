"""
探索179: エッジケースの検証

Lean 4形式化で注意すべき点:
1. set で v := v2(3*m+1) と定義したとき、pow_v2_mul_syracuse m を適用できるか
2. generalizing n の有無
3. ring タクティクが自然数で動くか
"""

def v2(n):
    if n == 0: return 0
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def syracuse(n):
    m = 3*n+1
    return m // (2**v2(m))

def syracuse_iter(k, n):
    for _ in range(k):
        n = syracuse(n)
    return n

# エッジケース: n=1 (不動点)
print("=== n=1 (不動点) ===")
for k in range(5):
    Tk = syracuse_iter(k, 1)
    # totalV2
    s = 0
    c = 0
    cur = 1
    for i in range(k):
        vi = v2(3*cur+1)
        c = 3*c + 2**s
        s += vi
        cur = syracuse(cur)
    lhs = 2**s * Tk
    rhs = 3**k * 1 + c
    print(f"  k={k}: T^k(1)={Tk}, S_k={s}, C_k={c}, 2^S*T^k={lhs}, 3^k+C_k={rhs}, eq? {lhs==rhs}")

# Lean 4 の ring vs nlinarith vs omega
print()
print("=== ring タクティクのテスト ===")
# ring は自然数の乗法環で動く: a*(b*c) = (a*b)*c, a*(b+c) = a*b+a*c 等
# 3 * (2^Sk * m) + 2^Sk = ?
# ring で整理: 2^Sk * (3*m+1) = 3*2^Sk*m + 2^Sk  -- これは ring で OK
# 3 * (3^k*n + C_k) + 2^Sk = 3^(k+1)*n + 3*C_k + 2^Sk  -- ring で OK

# 注意: ring は Nat で pow_succ を自動展開する
# 3^(k+1) = 3 * 3^k
# これは ring の範囲内

# pow_add: 2^(a+b) = 2^a * 2^b  -- これは rw [pow_add] で
# ring は pow_add を直接解決しないので rw で先に適用する必要がある

print("ring で解決可能:")
print("  2^Sk * (3*m+1) = 3*(2^Sk*m) + 2^Sk")
print("  3*(3^k*n + C_k) + 2^Sk = 3^(k+1)*n + 3*C_k + 2^Sk")
print()
print("ring で解決不可能（rw で前処理が必要）:")
print("  2^(Sk+v) = 2^Sk * 2^v  → rw [pow_add]")
print("  2^Sk * 2^v * T(m) = 2^Sk * (2^v * T(m))  → rw [mul_assoc]")

# generalizing n が不要であることの確認
print()
print("=== generalizing n 不要の確認 ===")
print("帰納法の構造:")
print("  theorem ... (n k : ℕ) (hn : n ≥ 1) (hodd : n % 2 = 1) :")
print("    2 ^ totalV2 n k * syracuseIter k n = ...")
print("  induction k with  -- n は固定")
print()
print("IH の形: ih : 2^{totalV2 n k} * syracuseIter k n = 3^k * n + generalConst n k")
print("これは n が同じなので generalizing 不要。")
print("もし generalizing n とすると IH が ∀ m になり過剰。")
print()
print("注意: syracuse_iter_mul_formula (既存版) は generalizing n を使っているが、")
print("それは consecutiveAscents の前提を syracuse n に適用するため。")
print("一般版では前提が n ≥ 1 と n odd のみで、")
print("これらは syracuseIter_pos/odd で自動的に伝播するので不要。")
print("ただし、主定理の証明では syracuseIter_pos/odd は直接使わない。")

# pow_v2_mul_syracuse の型の確認
print()
print("=== pow_v2_mul_syracuse の使い方 ===")
print("pow_v2_mul_syracuse (m : ℕ) :")
print("  2 ^ v2 (3 * m + 1) * syracuse m = 3 * m + 1")
print()
print("calc チェーンでの使用:")
print("  _ = 2 ^ Sk * (2 ^ v * syracuse m) := by rw [mul_assoc]")
print("  _ = 2 ^ Sk * (3 * m + 1) := by rw [pow_v2_mul_syracuse]")
print()
print("ここで v = v2(3*m+1) は set で定義済み。")
print("pow_v2_mul_syracuse は m を引数に取るので、")
print("rw [pow_v2_mul_syracuse] で m が自動的にマッチする。")
print()
print("注意: set v := v2(3*m+1) の後、ゴール中の v2(3*m+1) は v に置換される。")
print("pow_v2_mul_syracuse m の結論は 2^{v2(3*m+1)} * syracuse m = 3*m+1 なので、")
print("set 後は 2^v * syracuse m = 3*m+1 に rw できる。")
print("→ rw [hv_def] で v を v2(3*m+1) に戻す必要があるかもしれない。")
print()
print("=== 修正案 ===")
print("set を使わず直接 calc で処理する方が安全:")
lean_code_v2 = """
    calc 2 ^ (totalV2 n k + v2 (3 * syracuseIter k n + 1)) * syracuse (syracuseIter k n)
        = 2 ^ (totalV2 n k) * 2 ^ v2 (3 * syracuseIter k n + 1) * syracuse (syracuseIter k n)
            := by rw [pow_add]
      _ = 2 ^ (totalV2 n k) * (2 ^ v2 (3 * syracuseIter k n + 1) * syracuse (syracuseIter k n))
            := by rw [mul_assoc]
      _ = 2 ^ (totalV2 n k) * (3 * syracuseIter k n + 1)
            := by rw [pow_v2_mul_syracuse]
      _ = 3 * (2 ^ (totalV2 n k) * syracuseIter k n) + 2 ^ (totalV2 n k)
            := by ring
      _ = 3 * (3 ^ k * n + generalConst n k) + 2 ^ (totalV2 n k)
            := by rw [ih]
      _ = 3 ^ (k + 1) * n + (3 * generalConst n k + 2 ^ (totalV2 n k))
            := by ring
"""
print(lean_code_v2)
print("この版は set を使わないので、型のミスマッチリスクがない。")
print("ただし式が長くなるので、abbreviation か have で短縮してもよい。")
