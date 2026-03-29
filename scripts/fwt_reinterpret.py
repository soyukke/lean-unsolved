#!/usr/bin/env python3
"""
探索187: L_0(M) の再解釈 - k*(M, L) = L_0(M) を満たす L を特定

もし L_0(M) が k*(M, L_M) (あるL_Mでの飽和閾値)なら:
  L_0(3) = 9 = k*(3, 3)  → L_3 = 3
  L_0(4) = 6              → k*(4, L_4) = 6 → L_4 = 6/4 = 1.5 (非整数)
  L_0(6) = 4              → k*(6, L_6) = 4 → ?

しかし、もし L_0(M) が別の量だとしたら？
  L_0(3) = 9: 何の 9？
  L_0(4) = 6: 何の 6？
  L_0(6) = 4: 何の 4？

新仮説: L_0(M) = 「禁止語の最大和 S_max」としてみる
  → 各Mで最小禁止語の最大Sを求める

または: L_0(M) = 「禁止語が存在する最大のS」
"""
import sys

def p(s):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def vv2(n):
    """2-adic valuation"""
    if n == 0: return 999
    return (n & -n).bit_length() - 1

def check_word(word, max_bits=22):
    S = sum(word)
    bits = min(S, max_bits)
    mod = 1 << bits
    for n in range(1, mod, 2):
        m = n
        ok = True
        for a in word:
            val = 3*m+1
            if vv2(val) != a:
                ok = False
                break
            m = val >> a
        if ok:
            return True
    return False

p("="*60)
p("L_0(M) の再解釈")
p("="*60)

# 元データの確認: L_0(3)=9, L_0(4)=6, L_0(6)=4
# 2M-2 の値: M=3→4, M=4→6, M=6→10
# 待って: 2*4-2=6, L_0(4)=6... 一致する！
# 2*3-2=4, L_0(3)=9... 不一致
# 2*6-2=10, L_0(6)=4... 不一致

# 問題文を再読: "L_0(3)=9, L_0(4)=6, L_0(6)=4"
# そして "L_0(M) ≈ 2M-2"

# 確認: L_0(4)=6 = 2*4-2 = 6. 一致。
# L_0(6)=4 ≠ 2*6-2 = 10. 不一致。
# L_0(3)=9 ≠ 2*3-2 = 4. 不一致。

# 別の公式: L_0(M) ≈ 3M/(M-1)?
# M=3: 9/2=4.5, M=4: 12/3=4, M=6: 18/5=3.6 → 不一致

# L_0(M) = ceil(6/(M-2))? M=3: 6/1=6, M=4: 6/2=3, M=6: 6/4=1.5 → 不一致

# L_0(M) = ?
# (3, 9), (4, 6), (6, 4)
# 積: 3*9=27=3^3, 4*6=24, 6*4=24 → ほぼ24に収束？

# L_0(M) * M ≈ 24?
# M=3: 9*3=27, M=4: 6*4=24, M=6: 6*4=24 → L_0(M) ≈ 24/M?

# 確認: L_0(3) ≈ 24/3 = 8 vs 9 (近い)
# L_0(4) = 24/4 = 6 (一致)
# L_0(6) = 24/6 = 4 (一致)

p("仮説: L_0(M) * M ≈ 24 つまり L_0(M) ≈ 24/M")
p(f"  M=3: L_0=9, 24/3=8 (近い)")
p(f"  M=4: L_0=6, 24/4=6 (一致)")
p(f"  M=6: L_0=4, 24/6=4 (一致)")
p(f"  → L_0(3) = 9 ≠ 8 なので厳密一致ではない")

# もう少し精密に
# (3, 9), (4, 6), (6, 4) を通る曲線
# L_0(M) = a / (M - b) + c のフィット
# 3点なので3パラメータ決定可能

# 9 = a/(3-b) + c
# 6 = a/(4-b) + c
# 4 = a/(6-b) + c

# 6-4 = a*(1/(4-b) - 1/(6-b)) = a*(6-b-4+b)/((4-b)(6-b)) = 2a/((4-b)(6-b))
# 2 = 2a/((4-b)(6-b)) → a = (4-b)(6-b)

# 9-6 = a*(1/(3-b) - 1/(4-b)) = a*(4-b-3+b)/((3-b)(4-b)) = a/((3-b)(4-b))
# 3 = a/((3-b)(4-b)) = (4-b)(6-b)/((3-b)(4-b)) = (6-b)/(3-b)
# 3(3-b) = 6-b → 9-3b = 6-b → 3 = 2b → b = 3/2

# a = (4-3/2)(6-3/2) = (5/2)(9/2) = 45/4
# c = 6 - a/(4-b) = 6 - (45/4)/(5/2) = 6 - (45/4)*(2/5) = 6 - 9/2 = 3/2

p("\n正確なフィット: L_0(M) = 45/(4(M - 3/2)) + 3/2")
p(f"  = 45/(4M - 6) + 3/2")
p("検証:")
for M in [3, 4, 5, 6, 7, 8]:
    val = 45 / (4*M - 6) + 1.5
    p(f"  M={M}: L_0 = {val:.4f}")

# 整数版の近似
p("\n或いは L_0(M) = ceil(45/(4M-6) + 3/2)")
for M in [3, 4, 5, 6, 7, 8]:
    import math
    val = math.ceil(45 / (4*M - 6) + 1.5)
    p(f"  M={M}: L_0 = {val}")

# L_0(M) ≈ 2M - 2 の検証
p("\n2M-2 との比較:")
p(f"  M=3: 2M-2=4, actual=9")
p(f"  M=4: 2M-2=6, actual=6")
p(f"  M=6: 2M-2=10, actual=4")
p("→ 2M-2 は M=4 でのみ一致。一般には成立しない。")

# ここで問題文を再確認
# "禁止語閾値L_0(M)≈2M-2の理論的導出"
# "v2アルファベット{1,...,M}でのshift spaceの禁止語閾値"
# "L_0(3)=9,L_0(4)=6,L_0(6)=4"

# 2M-2: M=3→4, M=4→6, M=6→10
# actual: 9, 6, 4
# これは 2M-2 とは全く異なるパターン

# もしかして L_0(M) ≈ 2M-2 は別のMの範囲？
# 或いは問題文のL_0値が異なる量？

# k*(M, 3) の値: k*(3,3)=9, k*(4,3)=12, k*(6,3)=19
# これはL_0(3)=9のみ一致

# 新しい解釈を試す
# L_0(M) = 「mod 2^k = mod 2^S_max で、全ての長さ≤L の語が
#   実現可能になる最小のL」（ここでS_max = M*L）

# 或いは: L_0(M) = 「和S = 一定 の場合の禁止語閾値」

# 実験: S を固定して禁止語を調べる
p("\n--- S 固定での禁止語 ---")
for S in range(1, 15):
    # 和が S で、各要素が 1 以上の語（composition of S）
    # M は上限
    for M in [3, 4, 6]:
        # S の M-bounded composition
        comps = []
        def gen_comp(remaining, max_val, prefix):
            if remaining == 0:
                comps.append(tuple(prefix))
                return
            for a in range(1, min(remaining, max_val) + 1):
                gen_comp(remaining - a, max_val, prefix + [a])
        gen_comp(S, M, [])

        n_forbidden = 0
        for w in comps:
            if not check_word(w, 22):
                n_forbidden += 1

        total = len(comps)
        if total > 0 and n_forbidden > 0:
            p(f"  S={S}, M={M}: {n_forbidden}/{total} forbidden compositions")

# 最大S で禁止語が存在するS
p("\n--- 禁止語が存在する最大のS (M固定) ---")
for M in [2, 3, 4, 5, 6]:
    max_S_with_forbidden = 0
    for S in range(1, 25):
        comps = []
        def gen_comp2(remaining, max_val, prefix):
            if remaining == 0:
                comps.append(tuple(prefix))
                return
            for a in range(1, min(remaining, max_val) + 1):
                gen_comp2(remaining - a, max_val, prefix + [a])
        gen_comp2(S, M, [])

        if len(comps) > 50000:
            p(f"  M={M}, S={S}: too many compositions ({len(comps)}), skip")
            break

        has_forbidden = False
        for w in comps:
            if not check_word(w, 22):
                has_forbidden = True
                break

        if has_forbidden:
            max_S_with_forbidden = S

    p(f"  M={M}: max S with forbidden word = {max_S_with_forbidden}")

p("\nDone.")
