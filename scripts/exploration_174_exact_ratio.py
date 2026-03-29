"""
探索174 追加分析: Geom(3/4) が *厳密に* 成り立つかどうかの検証

入次数分布が厳密に P(d) = (3/4)(1/4)^{d-1} に等しいのか、
それとも漸近的な近似なのかを精密に調べる。
"""

from collections import defaultdict

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
    return m >> v2(m)

# === 1. 像サイズの厳密分析 ===
print("=" * 60)
print("1. 像サイズの厳密分析")
print("=" * 60)

for N in [100, 1000, 10000, 100000]:
    preimage_count = defaultdict(int)
    for n in range(1, N+1, 2):
        m = syracuse(n)
        preimage_count[m] += 1

    num_odd = N // 2 + (1 if N % 2 == 1 else 0)
    image_size = len(preimage_count)

    # 理論値: 像サイズ = 3N/8 (N/2 個の奇数を入力、各像 4/3 個平均)
    # 但し正確には: 像の数 = (入力数) / (平均入次数)
    #   = (N/2) / (4/3) = 3N/8

    expected_image = 3 * N / 8
    print(f"N={N:7d}: 奇数={num_odd:7d}, 像={image_size:7d}, "
          f"3N/8={expected_image:.1f}, 比={image_size/expected_image:.6f}")

# === 2. 入次数の分布が完全に (3/4)(1/4)^{d-1} なのかの精密検証 ===
print("\n" + "=" * 60)
print("2. 入次数分布の有理数的精密検証")
print("=" * 60)

# N = 4^K の倍数で検証すると、丁度の値が出るかもしれない
for K in range(2, 7):
    N = 4**K
    preimage_count = defaultdict(int)
    for n in range(1, N+1, 2):
        m = syracuse(n)
        preimage_count[m] += 1

    indeg_dist = defaultdict(int)
    for m, count in preimage_count.items():
        indeg_dist[count] += 1

    total_images = sum(indeg_dist.values())
    print(f"\nN = 4^{K} = {N}")
    print(f"  奇数入力: {N//2}, 像の数: {total_images}")

    sum_check = 0
    for d in sorted(indeg_dist.keys()):
        count = indeg_dist[d]
        frac_num = count
        frac_den = total_images
        # 分数表現
        from math import gcd
        g = gcd(frac_num, frac_den)
        print(f"  d={d}: count={count}/{total_images} = {count//g}/{total_images//g}, "
              f"  理論: 3/4 * (1/4)^{d-1} = {3 * 4**(K-d) if d <= K else '< 1/N'}")
        sum_check += d * count

    print(f"  sum(d * count_d) = {sum_check}, 入力奇数 = {N//2}, 比 = {sum_check}/{N//2}")

# === 3. 入次数分布の厳密な構造: mod 条件との関係 ===
print("\n" + "=" * 60)
print("3. 入次数と root の mod 条件")
print("=" * 60)

N = 10000
preimage_count = defaultdict(list)
for n in range(1, N+1, 2):
    m = syracuse(n)
    preimage_count[m].append(n)

# 入次数 d の像 m の mod 条件を分析
for d in range(1, 6):
    targets_d = [m for m, preim in preimage_count.items() if len(preim) == d]
    if not targets_d:
        continue

    roots = []
    for m in sorted(targets_d)[:20]:
        root = preimage_count[m][0]
        roots.append(root)

    print(f"\n入次数 d={d}: {len(targets_d)} 個の像")
    print(f"  代表的な root (最小逆像): {roots[:15]}")

    # root の mod 条件を分析
    mod_counts = defaultdict(int)
    for m in targets_d:
        root = preimage_count[m][0]
        mod_counts[root % 4] += 1

    print(f"  root mod 4 分布: {dict(mod_counts)}")

    # root の範囲分析
    # 入次数 d ⟺ 4^{d-1} * root ≤ N < 4^d * root
    # ⟺ N/4^d < root ≤ N/4^{d-1}
    lower = N / 4**d
    upper = N / 4**(d-1)
    actual_roots = [preimage_count[m][0] for m in targets_d]
    min_root = min(actual_roots) if actual_roots else 0
    max_root = max(actual_roots) if actual_roots else 0
    print(f"  root の範囲: [{min_root}, {max_root}]")
    print(f"  理論的範囲: ({lower:.1f}, {upper:.1f}]")

# === 4. 入次数 ≥ d の像の「厳密な数」 ===
print("\n" + "=" * 60)
print("4. 入次数 ≥ d の像の数（厳密）")
print("=" * 60)

N = 10000
preimage_count_dict = defaultdict(int)
for n in range(1, N+1, 2):
    m = syracuse(n)
    preimage_count_dict[m] += 1

total_images = len(preimage_count_dict)

for d in range(1, 8):
    ge_d = sum(1 for m, c in preimage_count_dict.items() if c >= d)
    ratio = ge_d / total_images if total_images > 0 else 0
    # Geom(3/4) では P(indeg >= d) = (1/4)^{d-1}
    theory = (1/4)**(d-1)
    print(f"  P(indeg ≥ {d}) = {ge_d}/{total_images} = {ratio:.6f}, "
          f"理論(1/4)^{d-1} = {theory:.6f}, 比 = {ratio/theory:.6f}")

# === 5. 鎖構造の「完全性」 ===
print("\n" + "=" * 60)
print("5. 逆像鎖の完全性の検証")
print("=" * 60)

print("全ての逆像が n' = 4n + 1 の鎖上にあるかを検証")

N = 5000
violations = 0
total_checked = 0

for m_val in range(1, N+1, 2):
    if m_val % 3 == 0:
        continue
    preims = []
    for n in range(1, N+1, 2):
        if syracuse(n) == m_val:
            preims.append(n)

    if len(preims) < 2:
        continue

    total_checked += 1
    root = preims[0]
    # 全ての preimage が 4^k * root + (4^k-1)/3 の形であるか確認
    for p in preims:
        found = False
        current = root
        for k in range(20):
            if current == p:
                found = True
                break
            current = 4 * current + 1
        if not found:
            violations += 1
            print(f"  VIOLATION: m={m_val}, preimage={p} is not on chain from root={root}")
            break

if violations == 0:
    print(f"  検証OK: {total_checked} 個の像（各2逆像以上）で全逆像が鎖上にある")
else:
    print(f"  {violations} 件の違反を発見")

# === 6. 厳密な分布: 入次数 d の像の数の閉公式候補 ===
print("\n" + "=" * 60)
print("6. 入次数 d の像の数の閉公式")
print("=" * 60)

print("""
入次数 d の像 m の数（[1,N] の奇数を入力としたとき）:

root(m) ∈ (N/4^d, N/4^{d-1}] の奇数 m (mod 3 != 0) に対応。

root は m の関数:
  root(m) = (4m-1)/3  (m mod 3 = 1)
  root(m) = (2m-1)/3  (m mod 3 = 2)

よって入次数 d の m の数:
  ≈ |{m odd, m mod 3 != 0 : root(m) ∈ (N/4^d, N/4^{d-1}]}|

root(m) ≈ (4/3)m (mod 3=1) or (2/3)m (mod 3=2) なので:
  m ∈ (3N/(4^{d+1}), 3N/4^d] (mod 3=1) or (3N/(2*4^d), 3N/(2*4^{d-1})]  (mod 3=2)

これにより入次数 d の像の数:
  ≈ (3/4) * (1/4)^{d-1} * (像の総数)

結論: Geom(3/4) は *漸近的* に成立し、有限 N では端数効果による誤差がある。
      N → ∞ で P(d) → (3/4)(1/4)^{d-1} に収束。
""")

print("完了。")
