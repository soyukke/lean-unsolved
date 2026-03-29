"""
非標準解析的2-adic反発性の精密分析

n = a (mod 2^k) の層でのSyracuse軌道の分岐パターンを
非標準解析の overspill の視点から分析する。
"""

import math

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count

# === 非標準的な「軌道の一致長」の分析 ===
# n と m が 2-adic に近いとき、T^k(n) と T^k(m) はいつまで一致するか？

print("=" * 70)
print("2-adic 近傍での軌道一致長 (非標準解析の overspill に関連)")
print("=" * 70)
print()

# n mod 2^j が同じ奇数 a のとき、Syracuse 軌道は何ステップまで一致するか
print("--- 軌道一致長: n = a (mod 2^j) の a について T^k の mod 2^{j-2} 一致 ---")

for j in [4, 6, 8, 10, 12]:
    max_agree = 0
    total_agree = 0
    count = 0
    for a in range(1, min(2**j, 200), 2):  # 奇数 a のみ
        # n = a と n = a + 2^j の軌道を比較
        n1 = a
        n2 = a + 2**j
        agree_steps = 0
        for step in range(50):
            # mod 2^{j-2} で一致するか
            mod_val = 2**(max(1, j-2))
            if n1 % mod_val == n2 % mod_val:
                agree_steps += 1
            else:
                break
            n1 = syracuse(n1) if n1 > 0 else 0
            n2 = syracuse(n2) if n2 > 0 else 0
            if n1 == 0 or n2 == 0:
                break
        max_agree = max(max_agree, agree_steps)
        total_agree += agree_steps
        count += 1
    avg_agree = total_agree / count if count > 0 else 0
    print(f"  j={j}: avg agreement steps = {avg_agree:.2f}, max = {max_agree}")

print()
print("非標準解析的解釈:")
print("  2^j-近傍の2数の軌道一致長を L(j) とする。")
print("  L(j) ~ c*j (線形成長) なら、2-adic距離の指数的縮約はない。")
print("  L(j) が有界なら、adic構造は軌道を制御しない。")
print()


# === 非標準的サイクルの代数的制約 ===

print("=" * 70)
print("超有限サイクルの代数的制約")
print("=" * 70)
print()

# Syracuse サイクルの方程式: T^p(n) = n のとき
# 2^s * n = 3^p * n + sum_{i=0}^{p-1} 3^i * 2^{s_i}
# ここで s = sum of v2 values along orbit

# p ステップのサイクルで必要な条件: n = (sum 3^i * 2^{s_i}) / (2^s - 3^p)
# 2^s > 3^p が必要 (n > 0 のため)

print("--- サイクル方程式 n = (分子)/(2^s - 3^p) の制約 ---")
print("p-サイクルでは s > p * log2(3) ≈ p * 1.585 が必要")
print()

for p in range(1, 16):
    min_s = int(math.ceil(p * math.log2(3))) + 1
    denom = 2**min_s - 3**p
    # 最小の分母の大きさ
    print(f"  p={p}: min s={min_s}, 2^{min_s}-3^{p} = {denom}, "
          f"log2(denom) = {math.log2(abs(denom)) if denom != 0 else 'undefined':.2f}")

print()
print("非標準解析的帰結:")
print("  超自然数的周期 p を持つサイクルでは")
print("  s は p*log2(3) より大きい超自然数。")
print("  分母 2^s - 3^p は有限にも無限にもなりうる。")
print()
print("  しかし! 転送原理により:")
print("  「p-サイクルの n は (分子)/(2^s-3^p) の形」は一階の文。")
print("  標準世界で p-サイクルが存在しない => *N でも不存在。")
print("  超有限 p に対する新規サイクルの可能性は転送で排除。")
print()


# === Overspill を使った「ほぼ全てが到達」の強化 ===

print("=" * 70)
print("Tao の density-1 結果の非標準強化")
print("=" * 70)
print()

# d(N) = |{n <= N : n reaches 1}| / N の計算
print("密度 d(N) の精密計算:")
for exp in range(8, 22):
    N = 2**exp
    reached = 0
    for n in range(1, N+1):
        x = n
        for _ in range(10000):
            if x == 1:
                reached += 1
                break
            if x % 2 == 0:
                x //= 2
            else:
                x = 3*x + 1
    d = reached / N
    gap = 1 - d
    print(f"  N=2^{exp}: d(N) = {d:.10f}, 1-d(N) = {gap:.2e}")

print()
print("非標準解析的解釈:")
print("  d(N) = 1 (全 N) なら CC は真。")
print("  数値的には d(N) = 1.0 (計算範囲内)。")
print("  転送: *d(H) = 1 (有限の H に対して当然)。")
print("  Overspill: d が全標準 N で 1 なら、")
print("    ある無限 H で *d(H) = 1 も保証される。")
print("    しかしこれは CC からの帰結であり、CC の証明にはならない。")
print()

# === 非標準的な反例の特徴づけ ===

print("=" * 70)
print("非標準的反例の必要条件")
print("=" * 70)
print("""
CC の否定を仮定し、反例 n0 (標準自然数) の性質を導出:

条件1: n0 は奇数 (偶数なら n0/2 に帰着)
条件2: Syracuse軌道 {T^k(n0)}_{k>=0} は有限値に収束しない
条件3: 軌道は発散するか、非自明サイクルに入る

Baker定理 (公理) 下では条件3のサイクルは排除 => 発散のみ。

発散の非標準的特徴づけ:
  n0 が発散 <=> ある超自然数 K で *T^K(n0) は無限超自然数
  (overspill による)

  さらに: 全標準 k で T^k(n0) > 0 (自明) から
  overspill により ある無限 K0 で *T^{K0}(n0) > 0。

  軌道 {*T^k(n0) : k <= K0} は *N の内的集合で、
  K0 個の超自然数からなる。

  この内的集合に対して:
  - sup は無限超自然数 (発散仮定)
  - inf > 0 (全要素正)
  - 統計的性質は転送により保持

  新しい洞察:
    A(n0, M) = |{k <= M : T^k(n0) > n0}| / M
    「n0 より大きいステップの割合」

    もし発散なら lim_{M->inf} A(n0, M) > 0。
    転送: *A(n0, H) > 0 (ある標準正数以上)。

    しかし探索082のCramer率より:
    P(発散) <= exp(-0.055 k)
    これは「ランダムに見える軌道での」確率。
    特定の n0 に対してはこの確率的議論は適用されない。
""")

print("分析完了")
