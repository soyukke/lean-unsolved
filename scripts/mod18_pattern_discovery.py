#!/usr/bin/env python3
"""
探索194 Part 3: mod 18 遷移行列の構造的パターンの発見
"""

def v2(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    m = 3 * n + 1
    return m // (2 ** v2(m))

# ========================================
# 核心発見: 遷移確率のパターン
# ========================================
print("=" * 70)
print("核心発見: mod 18 遷移確率の共通パターン")
print("=" * 70)

# 各 mod 6 クラスで同一の遷移確率分布:
# 50.8%, 25.4%, 12.7%, 6.4%, 3.2%, 1.6%
# これは幾何的! 50.8 ≈ 1/2 * 100, 25.4 ≈ 1/4 * 100, 12.7 ≈ 1/8 * 100
# 正確には: 1/2, 1/4, 1/8, 1/16, 1/32, 1/64... → 級数和 = 1 - 1/64 ≈ 0.984
# でも 6 ターゲットなので...

# v2(3n+1) の分布を見る
from collections import Counter
v2_dist = Counter()
for n in range(1, 1000001, 2):
    v2_dist[v2(3*n+1)] += 1

total = sum(v2_dist.values())
print("\nv2(3n+1) の分布 (奇数 n のみ):")
for k in sorted(v2_dist.keys()):
    pct = v2_dist[k] / total * 100
    theory = 100 / (2**k) if k >= 1 else 0
    print(f"  v2={k}: {pct:.2f}% (理論値 1/2^{k} = {theory:.2f}%)")

# ========================================
# v2(3n+1) = j の確率が 1/2^j であることの分析
# ========================================
print("\n" + "=" * 70)
print("v2(3n+1) の確率分析")
print("=" * 70)

# 奇数 n に対して:
# v2(3n+1) = 1 ⟺ n ≡ 3 (mod 4) → 確率 1/2
# v2(3n+1) = 2 ⟺ n ≡ 1 (mod 8) → 確率 1/4
# v2(3n+1) = 3 ⟺ n ≡ 5 (mod 16) ∨ n ≡ 13 (mod 16) → 確率 1/8 (mod 8 = 5の半分)
# v2(3n+1) ≥ 3 ⟺ n ≡ 5 (mod 8) → 確率 1/4
# 各 j での条件: n ≡ (2^j - 1)/3 (mod 2^j) (3で割った逆元)

print("\nv2(3n+1) = j の条件:")
for j in range(1, 8):
    # v2(3n+1) = j ⟺ 2^j | (3n+1) but 2^{j+1} ∤ (3n+1)
    # 3n ≡ -1 (mod 2^j) ⟺ 3n ≡ 2^j - 1 (mod 2^j)
    # n ≡ (2^j - 1) * 3^{-1} (mod 2^j)
    # 3^{-1} mod 2^j: 3 * x ≡ 1 (mod 2^j)
    mod = 2 ** j
    inv3 = pow(3, -1, mod)
    n_cond = ((mod - 1) * inv3) % mod
    
    # さらに 2^{j+1} ∤ (3n+1) の条件
    mod2 = 2 ** (j + 1)
    inv3_2 = pow(3, -1, mod2)
    n_cond2 = ((mod2 - 1) * inv3_2) % mod2
    
    # v2 = j exactly: n ≡ n_cond (mod 2^j) かつ n ≢ n_cond2 (mod 2^{j+1})
    # 確率: 1/2^j - 1/2^{j+1} = 1/2^{j+1}  ... いや違う
    # 2^j | (3n+1) の確率は 1/2^j (mod 2^j で 1 つのクラス)
    # 2^{j+1} | (3n+1) の確率は 1/2^{j+1}
    # v2 = j の確率 = 1/2^j - 1/2^{j+1} = 1/2^{j+1}
    
    # いや、奇数 n に限定しているので:
    # 奇数 mod 2^j で条件を満たすクラス数 / 全奇数クラス数
    # 奇数は mod 2^j で 2^{j-1} クラス
    
    count_exact = 0
    for n_test in range(1, mod2, 2):
        if v2(3*n_test + 1) == j:
            count_exact += 1
    total_odd = mod2 // 2  # 奇数の数 in [1, 2^{j+1})
    
    print(f"  v2={j}: n≡{n_cond} (mod {mod}), "
          f"正確な確率={count_exact}/{total_odd}=1/{total_odd//count_exact if count_exact else '?'}")

# ========================================
# mod 6 * v2 による完全な遷移の解析
# ========================================
print("\n" + "=" * 70)
print("mod 6 と v2 による遷移先の決定")
print("=" * 70)

# Syracuse(n) mod 6 は n mod 6 と v2(3n+1) で決まるか?
from collections import defaultdict

for r6 in [1, 3, 5]:
    print(f"\nn ≡ {r6} (mod 6):")
    for vj in range(1, 7):
        targets = set()
        count = 0
        for n in range(r6, 100000, 6):
            if n > 0 and v2(3*n+1) == vj:
                s = syracuse(n) % 6
                targets.add(s)
                count += 1
        if count > 0:
            print(f"  v2(3n+1)={vj}: syracuse(n) mod 6 = {sorted(targets)} (count={count})")

# ========================================
# 核心: v2(3n+1) = j のとき syracuse(n) = (3n+1)/2^j
# n ≡ r (mod 6) → 3n+1 ≡ 3r+1 (mod 6) → (3r+1)/2^j mod 6 は?
# ========================================
print("\n" + "=" * 70)
print("代数的解析: syracuse(n) mod 3 の決定")
print("=" * 70)

# syracuse(n) = (3n+1)/2^v2(3n+1) 
# (3n+1) mod 3 = 1 (常に)
# 2^j mod 3: j奇数→2, j偶数→1
# (3n+1)/2^j mod 3 = 1 * (2^j)^{-1} mod 3
# j奇数: (2)^{-1} = 2 mod 3, so mod3 = 2
# j偶数: (1)^{-1} = 1 mod 3, so mod3 = 1

print("\nsyracuse(n) mod 3 は v2(3n+1) の偶奇のみで決まる:")
print("  v2(3n+1) 奇数 → syracuse(n) ≡ 2 (mod 3)")
print("  v2(3n+1) 偶数 → syracuse(n) ≡ 1 (mod 3)")

# 数値検証
for vj in range(1, 7):
    mods = set()
    for n in range(1, 10000, 2):
        if v2(3*n+1) == vj:
            mods.add(syracuse(n) % 3)
    print(f"  v2={vj}: syracuse(n) mod 3 = {sorted(mods)}")

# ========================================
# mod 6 での遷移: n mod 6 と v2 parity で決まる!
# ========================================
print("\n" + "=" * 70)
print("核心発見: syracuse(n) mod 6 は v2 の偶奇で2択に分かれる")
print("=" * 70)

# n ≡ r (mod 6), v2(3n+1) = j のとき
# syracuse(n) mod 2 = 1 (常に奇数)  
# syracuse(n) mod 3: j奇→2, j偶→1
# これとmod2を合わせると:
# j奇: mod6 ∈ {5} (奇数でmod3=2)
# j偶: mod6 ∈ {1} (奇数でmod3=1)

print("\nv2 奇数 → syracuse(n) ≡ 5 (mod 6)")
print("v2 偶数 → syracuse(n) ≡ 1 (mod 6)")

# 検証
for vj in range(1, 8):
    mod6_vals = set()
    for n in range(1, 50000, 2):
        if v2(3*n+1) == vj:
            mod6_vals.add(syracuse(n) % 6)
    if mod6_vals:
        print(f"  v2={vj} ({'奇' if vj%2==1 else '偶'}): syracuse(n) mod 6 = {sorted(mod6_vals)}")

# ========================================
# まとめ
# ========================================
print("\n" + "=" * 70)
print("最終まとめ: 形式化可能な新定理")
print("=" * 70)

summary = """
【新発見1】syracuse(n) mod 3 は v2(3n+1) の偶奇で決まる
  - v2(3n+1) 奇数 → syracuse(n) ≡ 2 (mod 3)
  - v2(3n+1) 偶数 → syracuse(n) ≡ 1 (mod 3)
  証明: (3n+1) mod 3 = 1, 2^j mod 3 = (-1)^j, (3n+1)/2^j mod 3 = (-1)^{-j} = (-1)^j

【新発見2】syracuse(n) mod 6 は v2(3n+1) の偶奇で決まる  
  - v2(3n+1) 奇数 → syracuse(n) ≡ 5 (mod 6) (∈ mod3=2 クラス)
  - v2(3n+1) 偶数 → syracuse(n) ≡ 1 (mod 6) (∈ mod3=1 クラス)

【新発見3】肥沃率 2/3 の精密化
  - Syracuse の像は mod 6 で {1, 5} のみ（{3} には決して行かない）
  - 確率的に: P(mod6=5 の像) = P(v2 奇数) = 1/2 + 1/8 + 1/32 + ... = 2/3
  - 確率的に: P(mod6=1 の像) = P(v2 偶数) = 1/4 + 1/16 + 1/64 + ... = 1/3

【新発見4】mod 18 遷移行列が mod 6 で退化する
  - n mod 18 の9クラスは mod 6 の3クラスに退化
  - 各mod 6 クラス内では同一の遷移確率分布
  - 遷移確率は幾何分布 P(target t | source s) = (1/2)^j で v2 = j に対応

【形式化設計】
定理群:
1. syracuse_mod3_of_v2_odd: v2奇 → mod3=2 
2. syracuse_mod3_of_v2_even: v2偶 → mod3=1
3. syracuse_mod6_of_v2_odd: v2奇 → mod6=5
4. syracuse_mod6_of_v2_even: v2偶 → mod6=1
5. syracuse_preimage_mod6_eq5: mod6=5 → 逆像 (2m-1)/3 存在
6. syracuse_preimage_mod6_eq1: mod6=1 → 逆像 (4m-1)/3 存在
7. fertile_iff: m%3≠0 ⟺ 逆像存在
"""
print(summary)

