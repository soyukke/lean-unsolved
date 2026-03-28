"""
最終深掘り:
1. n ≡ 3 (mod 5) → T(n) ≡ 0 (mod 5) の証明的検証
2. mod 5 遷移行列の固有値解析
3. 各素数pについて "5|T(n) ⟺ n≡3 (mod 5)" 型の法則の網羅探索
4. 軌道上のmod 5パターンの周期性
"""
import math
from collections import Counter

def syracuse(n):
    if n <= 0 or n % 2 == 0:
        return None
    x = 3 * n + 1
    while x % 2 == 0:
        x //= 2
    return x

def vp(n, p):
    if n == 0:
        return float('inf')
    c = 0
    while n % p == 0:
        c += 1
        n //= p
    return c

# ============================================================
# 1. n ≡ 3 (mod 5) → 5 | T(n) の代数的証明
# ============================================================
print("=" * 60)
print("[1] n ≡ 3 (mod 5) → 5 | T(n) の代数的検証")
print("=" * 60)

# n ≡ 3 (mod 5) のとき:
# 3n + 1 ≡ 3·3 + 1 = 10 ≡ 0 (mod 5)
# T(n) = (3n+1)/2^v で、5 | (3n+1) かつ gcd(2,5) = 1
# よって 5 | T(n)
print("証明: n ≡ 3 (mod 5) ⟹ 3n+1 ≡ 10 ≡ 0 (mod 5)")
print("  2^v と 5 は互いに素なので、5 | (3n+1)/2^v = T(n)")
print("  これは n ≡ 3 (mod 5) ⟹ 5 | T(n) の厳密な証明。")

# 逆は成り立つか？ 5 | T(n) ⟹ n ≡ 3 (mod 5)?
print("\n逆の検証: 5 | T(n) ⟹ n ≡ 3 (mod 5)?")
counterexamples = []
for n in range(1, 100001, 2):
    t = syracuse(n)
    if t % 5 == 0 and n % 5 != 3:
        counterexamples.append(n)
        if len(counterexamples) <= 5:
            print(f"  反例: n={n} (mod 5 = {n%5}), T(n)={t}")
print(f"  反例の数 (n<100001): {len(counterexamples)}")

if not counterexamples:
    print("  → 反例なし！ 5 | T(n) ⟺ n ≡ 3 (mod 5) が成立する可能性")
    # さらに大きな範囲で確認
    for n in range(100001, 1000001, 2):
        t = syracuse(n)
        if t % 5 == 0 and n % 5 != 3:
            print(f"  大範囲で反例発見: n={n}")
            break
    else:
        print("  n < 1000001 でも反例なし → 定理の可能性大")

# 代数的にも確認: 5 | T(n) ⟹ 5 | (3n+1) ⟹ 3n ≡ -1 ≡ 4 (mod 5) ⟹ n ≡ 4·3^{-1} (mod 5)
# 3^{-1} mod 5 = 2 (because 3·2=6≡1)
# n ≡ 4·2 = 8 ≡ 3 (mod 5)
print("\n代数的証明（逆方向）:")
print("  5 | T(n) ⟹ 5 | (3n+1)  (∵ gcd(2^v, 5) = 1)")
print("  3n+1 ≡ 0 (mod 5) ⟹ 3n ≡ 4 (mod 5)")
print("  3^{-1} ≡ 2 (mod 5)  (∵ 3·2 = 6 ≡ 1)")
print("  n ≡ 4·2 = 8 ≡ 3 (mod 5)")
print("  ∴ 5 | T(n) ⟺ n ≡ 3 (mod 5)  ■")

# ============================================================
# 2. 全素数pについて p | T(n) ⟺ n ≡ ? (mod p) の法則
# ============================================================
print("\n" + "=" * 60)
print("[2] 各素数 p について p | T(n) の条件")
print("=" * 60)

for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    # 3n+1 ≡ 0 (mod p) ⟺ n ≡ (p-1)·(3^{-1} mod p) (mod p)
    # 3^{-1} mod p
    inv3 = pow(3, p - 2, p) if p > 2 else None
    if inv3 is None:
        continue
    target_residue = ((p - 1) * inv3) % p
    # p=3 は特殊: 3n+1 ≡ 1 (mod 3) always → 3 ∤ T(n) always
    if p == 3:
        print(f"  p={p}: 3n+1 ≡ 1 (mod 3) 常に → 3 ∤ T(n) (既知)")
        continue

    # 検証
    violations = 0
    total_checks = 0
    for n in range(1, 50001, 2):
        t = syracuse(n)
        total_checks += 1
        # p | T(n) ⟺ n ≡ target_residue (mod p)?
        if (t % p == 0) != (n % p == target_residue):
            violations += 1

    print(f"  p={p}: p | T(n) ⟺ n ≡ {target_residue} (mod {p}), "
          f"violations={violations}/{total_checks}")

# ============================================================
# 3. 二段階写像: T(T(n)) mod p の法則
# ============================================================
print("\n" + "=" * 60)
print("[3] T(T(n)) mod p の構造")
print("=" * 60)

for p in [5, 7, 11]:
    print(f"\np={p}: T(T(n)) mod {p} の分布 (n mod {p} 別):")
    for r in range(p):
        dist = Counter()
        count = 0
        for n in range(1, 100001, 2):
            if n % p == r:
                t1 = syracuse(n)
                if t1 and t1 % 2 == 1:
                    t2 = syracuse(t1)
                    if t2:
                        dist[t2 % p] += 1
                        count += 1
        if count > 0:
            top3 = sorted(dist.items(), key=lambda x: -x[1])[:3]
            dominant = top3[0][1] / count if top3 else 0
            desc = ", ".join(f"{res}:{c/count:.3f}" for res, c in top3)
            marker = " ★" if dominant > 0.5 else ""
            print(f"  n≡{r}: {desc}{marker}")

# ============================================================
# 4. mod 5 軌道の遷移行列
# ============================================================
print("\n" + "=" * 60)
print("[4] mod 5 遷移行列（奇数剰余類のみ）")
print("=" * 60)

# 奇数の mod 5 剰余類: 1, 3 (0,2,4は偶数を含む)
# 実際は mod 10 で見る方が自然（奇数 = 1,3,5,7,9 mod 10）
# mod 10 = mod 2 × mod 5 で、奇数のmod5は 0,1,2,3,4 全部あり得る

trans_mat = {}
for r in range(5):
    dist = Counter()
    count = 0
    for n in range(1, 200001, 2):
        if n % 5 == r:
            t = syracuse(n)
            dist[t % 5] += 1
            count += 1
    if count > 0:
        trans_mat[r] = {s: dist.get(s, 0) / count for s in range(5)}
        row = " ".join(f"{trans_mat[r].get(s, 0):.4f}" for s in range(5))
        print(f"  [{r}] → {row}")

# 定常分布の計算
print("\n定常分布（数値的推定 — 長軌道のmod5分布）:")
mod5_dist = Counter()
total = 0
for start in range(1, 50001, 2):
    n = start
    for _ in range(500):
        n = syracuse(n)
        if n is None or n <= 1:
            break
        mod5_dist[n % 5] += 1
        total += 1

for r in range(5):
    print(f"  mod 5 = {r}: {mod5_dist.get(r, 0)/total:.4f}")

# ============================================================
# 5. 多素数結合不変量: (n mod 5, n mod 7) → (T(n) mod 5, T(n) mod 7)
# ============================================================
print("\n" + "=" * 60)
print("[5] (mod 5, mod 7) 結合遷移の確定的ペア")
print("=" * 60)

deterministic_pairs = []
for r5 in range(5):
    for r7 in range(7):
        targets = set()
        count = 0
        for n in range(1, 100001, 2):
            if n % 5 == r5 and n % 7 == r7:
                t = syracuse(n)
                targets.add((t % 5, t % 7))
                count += 1
        if count > 0:
            if len(targets) == 1:
                deterministic_pairs.append((r5, r7, list(targets)[0]))

print(f"確定的遷移ペアの数: {len(deterministic_pairs)}/35")
for r5, r7, target in deterministic_pairs[:10]:
    print(f"  ({r5},{r7}) → {target}")

# ============================================================
# 6. v5の軌道上累積の漸近挙動
# ============================================================
print("\n" + "=" * 60)
print("[6] Σv5(orbit[0..L])/L の収束")
print("=" * 60)

# T(n)のmod5分布が一様(各20%)なら、v5の期待値は 1/4
# (P(v5=0)=4/5, P(v5=k)=(1/5)^k * 4/5, E[v5] = 1/4)
# ただし n≡3 (mod 5) → 5|T(n) の偏りがある

for start in [27, 97, 871, 6171, 77031]:
    n = start
    cumsum = 0
    steps = 0
    for i in range(1000):
        n = syracuse(n)
        if n is None or n <= 1:
            break
        cumsum += vp(n, 5)
        steps += 1
    if steps > 0:
        avg = cumsum / steps
        print(f"  start={start}: Σv5/L = {avg:.4f} (L={steps}), "
              f"theory=0.2500")

print("\n理論値の導出:")
print("  P(5|T(n)) = 1/5 (∵ n≡3 mod 5 の割合が1/5)")
print("  v5がGeo(1/5)に従う → E[v5] = (1/5)/(1-1/5) = 1/4 = 0.25")
print("  → Σv5/L → 1/4 に収束するはず")

# 一般化: p≠3 の素数について
print("\n一般化: 各素数pについて Σvp/L の理論値 vs 実測:")
for p in [5, 7, 11, 13, 17, 19]:
    theory = 1 / (p - 1)  # E[vp] = (1/p)/(1-1/p) = 1/(p-1)
    # 実測
    total_vp = 0
    total_steps = 0
    for start in range(1, 20001, 2):
        n = start
        for _ in range(200):
            n = syracuse(n)
            if n is None or n <= 1:
                break
            total_vp += vp(n, p)
            total_steps += 1
    measured = total_vp / total_steps if total_steps > 0 else 0
    print(f"  p={p}: theory=1/{p-1}={theory:.6f}, measured={measured:.6f}, "
          f"ratio={measured/theory:.4f}")

print("\n" + "=" * 60)
print("最終解析完了")
