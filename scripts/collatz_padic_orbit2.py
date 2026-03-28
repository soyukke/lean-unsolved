"""
追加解析: 注目ポイントの深掘り

1. v3(T(n)) = 0 が常に成立 → T(n)は3と互いに素（既知だが定量的確認）
2. v5/v7比率の安定性（cv ≈ 0.46）の理論的根拠
3. v3密度の異常な低さ（0.0438倍）の構造解析
4. mod p^k の確定性: p=2のみ50%で安定、他は0%に退化
5. p-adic 比率不変量候補の大サンプル検証
"""

import math
from collections import Counter, defaultdict

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

def syracuse_orbit(n, max_steps=500):
    orbit = [n]
    for _ in range(max_steps):
        n = syracuse(n)
        if n is None or n == 1:
            if n == 1:
                orbit.append(1)
            break
        orbit.append(n)
    return orbit

# ============================================================
# 1. v3密度の異常低さの解明: T(n) mod 3 の厳密解析
# ============================================================
print("=" * 60)
print("[1] v3密度の異常低さの解明")
print("=" * 60)

# T(n) = (3n+1)/2^{v2(3n+1)}
# 3n+1 ≡ 1 (mod 3)  (nが任意の奇数)
# よって v3(3n+1) = 0
# T(n) = (3n+1)/2^k で、3n+1 ≡ 1 (mod 3) なので T(n) ≡ 2^{-k} (mod 3)
# 2^{-1} ≡ 2 (mod 3), 2^{-2} ≡ 1 (mod 3), etc.
# よって T(n) mod 3 ∈ {1, 2} — 決して0にならない

# これは軌道上のすべての要素に再帰的に適用される
# つまり、1を除く軌道上のすべての奇数nについて 3∤n が再帰的に保証される...のか？

# 確認: 軌道上で3の倍数が現れるか
count_3div = 0
count_total = 0
for start in range(1, 100001, 2):
    orbit = syracuse_orbit(start, 200)
    for x in orbit:
        count_total += 1
        if x % 3 == 0:
            count_3div += 1

print(f"  軌道上の全要素: {count_total}")
print(f"  3の倍数: {count_3div}")
print(f"  割合: {count_3div/count_total:.8f}")
print()

# 理論的にはT(n)が常に3と互いに素なので、1→1のサイクルを除いて
# 軌道上のすべての要素が3の倍数でない。
# ただし初期値が3の倍数の場合、最初のステップで3の倍数でなくなる
# → v3密度 ≈ 0 は自明な帰結

# n≡0 (mod 3)のとき、T(n)のmod 3を確認
print("n ≡ 0 (mod 3) のとき T(n) mod 3:")
for n in range(3, 100, 6):  # 奇数で3の倍数
    t = syracuse(n)
    print(f"  T({n}) = {t}, mod 3 = {t % 3}")
    if n > 50:
        break

print("\nn ≡ 1 (mod 3) のとき T(n) mod 3:")
for n in range(1, 50, 6):
    t = syracuse(n)
    print(f"  T({n}) = {t}, mod 3 = {t % 3}")

print("\nn ≡ 2 (mod 3) のとき T(n) mod 3:")
for n in range(5, 50, 6):
    t = syracuse(n)
    print(f"  T({n}) = {t}, mod 3 = {t % 3}")

# ============================================================
# 2. v5/v7 比率の理論解析
# ============================================================
print("\n" + "=" * 60)
print("[2] v5/v7 比率不変量の大サンプル検証")
print("=" * 60)

# より長い軌道でΣv_p比率を計算
primes = [5, 7, 11, 13]
ratio_data = defaultdict(list)

for start in range(1, 50001, 2):
    orbit = syracuse_orbit(start, 500)
    if len(orbit) < 50:
        continue

    sums = {}
    for p in primes:
        sums[p] = sum(vp(x, p) for x in orbit)

    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            if sums[q] > 0:
                ratio_data[(p, q)].append(sums[p] / sums[q])

print("\n--- 比率の収束性（大サンプル） ---")
for (p, q), vals in sorted(ratio_data.items()):
    if len(vals) < 100:
        continue
    avg = sum(vals) / len(vals)
    std = (sum((v - avg) ** 2 for v in vals) / len(vals)) ** 0.5
    cv = std / avg if avg > 0 else float('inf')

    # 理論予測: ランダムモデルでは Σv_p/Σv_q → (q-1)/(p-1) × (log p / log q)
    # Heuristic: v_p出現率 ≈ 1/p, 平均 v_p ≈ 1/(p-1) when present
    # → Σv_p / L ≈ 1/(p(p-1)), Σv_q / L ≈ 1/(q(q-1))
    # → ratio ≈ q(q-1) / (p(p-1))
    theory1 = (q * (q - 1)) / (p * (p - 1))
    # Alternative: Σv_p/L ≈ 1/(p-1), ratio ≈ (q-1)/(p-1)
    theory2 = (q - 1) / (p - 1)
    # Simplest: ratio ≈ q/p (Poisson model)
    theory3 = q / p
    # Geometric: Σvp ≈ p/(p-1)^2 * L/p = L/(p-1)^2
    theory4 = ((q-1)**2) / ((p-1)**2)

    print(f"  Σv{p}/Σv{q}: mean={avg:.4f}, cv={cv:.4f}, "
          f"theories: q(q-1)/p(p-1)={theory1:.4f}, (q-1)/(p-1)={theory2:.4f}, "
          f"q/p={theory3:.4f}")

# ============================================================
# 3. mod p^k確定性のp依存性の理論解析
# ============================================================
print("\n" + "=" * 60)
print("[3] mod p^k 確定性がp=2でのみ50%を維持する理由")
print("=" * 60)

# p=2の場合: T(n) = (3n+1)/2^{v2(3n+1)}
# n mod 2^k が決まれば v2(3n+1) が（ある程度）決まる
# → T(n) mod 2^k がある程度決まる

# p=3の場合: 3n+1 ≡ 1 (mod 3) は常に成立
# しかし v2(3n+1) はn mod 2^? に依存するので、
# n mod 3^k だけでは v2が決まらない
# → T(n) mod 3^k は n mod 3^k だけでは決まらない

# 検証: n ≡ 1 (mod 9) のとき T(n) mod 9 の分布
print("\nn ≡ 1 (mod 9) のとき T(n) mod 9 の分布:")
dist = Counter()
for n in range(1, 100000, 2):
    if n % 9 == 1:
        t = syracuse(n)
        dist[t % 9] += 1
total = sum(dist.values())
for r in sorted(dist.keys()):
    print(f"  T(n) ≡ {r} (mod 9): {dist[r]/total:.4f}")

print("\nn ≡ 1 (mod 4) のとき T(n) mod 4 の分布:")
dist2 = Counter()
for n in range(1, 100000, 2):
    if n % 4 == 1:
        t = syracuse(n)
        dist2[t % 4] += 1
total2 = sum(dist2.values())
for r in sorted(dist2.keys()):
    print(f"  T(n) ≡ {r} (mod 4): {dist2[r]/total2:.4f}")

# p=2のkey insight: n mod 2^k → v2(3n+1)が決まるケースが半分ある
print("\nn mod 8 → v2(3n+1) の対応:")
for r in [1, 3, 5, 7]:
    vals = set()
    for mult in range(200):
        n = r + 8 * mult
        if n > 0:
            v = vp(3 * n + 1, 2)
            vals.add(v)
    print(f"  n ≡ {r} (mod 8): v2 ∈ {sorted(vals)[:5]}{'...' if len(vals)>5 else ''}")

# ============================================================
# 4. 新しい不変量候補: mod combined構造
# ============================================================
print("\n" + "=" * 60)
print("[4] CRT(mod 2^k, mod 3^j)結合構造")
print("=" * 60)

# mod 2^k × mod 3^j の結合で確定性が上がるか
for k2 in [3, 4, 5]:
    for k3 in [1, 2, 3]:
        mod2 = 2 ** k2
        mod3 = 3 ** k3
        mod_combined = mod2 * mod3

        deterministic = 0
        total = 0
        for r in range(mod_combined):
            if r % 2 == 0:
                continue
            total += 1
            targets = set()
            for mult in range(100):
                n = r + mod_combined * mult
                if n > 0 and n % 2 == 1:
                    t = syracuse(n)
                    targets.add(t % mod_combined)
            if len(targets) == 1:
                deterministic += 1

        print(f"  mod 2^{k2}×3^{k3} = mod {mod_combined}: "
              f"det={deterministic}/{total} ({deterministic/total:.1%})")

# ============================================================
# 5. v5分布の精密解析 — ランダムモデルとの比較
# ============================================================
print("\n" + "=" * 60)
print("[5] v5(T(n))分布 vs 幾何分布")
print("=" * 60)

# T(n) mod 5 の分布: T(n) = (3n+1)/2^v
# 3n+1 mod 5 は n mod 5 に依存
# 2^v mod 5 は v mod 4 に依存（2^4 ≡ 1 mod 5）
v5_dist = Counter()
for n in range(1, 200001, 2):
    t = syracuse(n)
    v5_dist[vp(t, 5)] += 1

total = sum(v5_dist.values())
print("v5(T(n)) 分布:")
for v in range(7):
    obs = v5_dist.get(v, 0) / total
    # 幾何分布 Geo(1/5): P(v=k) = (1/5)^k × (4/5)
    geo = (1/5)**v * (4/5)
    # 一様分布: P(5|T(n)) = 1/5
    print(f"  v5={v}: observed={obs:.6f}, geometric(1/5)={geo:.6f}, "
          f"ratio={obs/geo:.4f}")

# v7の同様の検証
print("\nv7(T(n)) 分布:")
v7_dist = Counter()
for n in range(1, 200001, 2):
    t = syracuse(n)
    v7_dist[vp(t, 7)] += 1
total = sum(v7_dist.values())
for v in range(6):
    obs = v7_dist.get(v, 0) / total
    geo = (1/7)**v * (6/7)
    print(f"  v7={v}: observed={obs:.6f}, geometric(1/7)={geo:.6f}, "
          f"ratio={obs/geo:.4f}")

# ============================================================
# 6. T(n) mod 5 の条件付き分布（n mod 5 別）
# ============================================================
print("\n" + "=" * 60)
print("[6] T(n) mod 5 の条件付き分布（n mod 5 別）")
print("=" * 60)

for r5 in [1, 2, 3, 4]:  # 5の倍数を除く奇数
    dist = Counter()
    count = 0
    for n in range(1, 200001, 2):
        if n % 5 == r5:
            t = syracuse(n)
            dist[t % 5] += 1
            count += 1
    if count > 0:
        print(f"n ≡ {r5} (mod 5):")
        for res in range(5):
            print(f"  T(n) ≡ {res} (mod 5): {dist.get(res, 0)/count:.4f}")

# n ≡ 0 (mod 5) の特別ケース
dist = Counter()
count = 0
for n in range(5, 200001, 10):  # 奇数の5の倍数
    t = syracuse(n)
    dist[t % 5] += 1
    count += 1
print(f"n ≡ 0 (mod 5) (奇数):")
for res in range(5):
    print(f"  T(n) ≡ {res} (mod 5): {dist.get(res, 0)/count:.4f}")

print("\n" + "=" * 60)
print("追加解析完了")
