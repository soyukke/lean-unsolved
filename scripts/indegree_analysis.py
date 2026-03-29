"""
コラッツグラフの入次数分析
各ノード n の前駆ノード（collatzStep(m) = n となる m）を調査する。

前駆ノードの候補:
(a) 偶数前駆: m = 2n (常に collatzStep(2n) = n)
(b) 奇数前駆: m = (n-1)/3 (n ≡ 1 mod 3 かつ (n-1)/3 が奇数のとき)

n ≡ 4 (mod 6) のとき入次数 = 2（偶数前駆 + 奇数前駆）
それ以外のとき入次数 = 1（偶数前駆のみ）
"""

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def find_predecessors(n, max_search=10*n if False else None):
    """n の前駆ノード（collatzStep(m) = n となる全ての m > 0）を探す"""
    preds = []
    # (a) 偶数前駆: m = 2n
    m_even = 2 * n
    assert collatz_step(m_even) == n, f"Even predecessor failed: collatz_step({m_even}) = {collatz_step(m_even)}, expected {n}"
    preds.append(('even', m_even))

    # (b) 奇数前駆: collatzStep(m) = 3m+1 = n → m = (n-1)/3
    #     条件: n ≡ 1 (mod 3) かつ (n-1)/3 が奇数かつ (n-1)/3 > 0
    if n >= 1 and (n - 1) % 3 == 0:
        m_odd_candidate = (n - 1) // 3
        if m_odd_candidate > 0 and m_odd_candidate % 2 == 1:
            assert collatz_step(m_odd_candidate) == n, f"Odd predecessor failed: collatz_step({m_odd_candidate}) = {collatz_step(m_odd_candidate)}, expected {n}"
            preds.append(('odd', m_odd_candidate))

    return preds

def brute_force_predecessors(n, search_range=1000):
    """ブルートフォースで前駆ノードを探す（検証用）"""
    preds = []
    for m in range(1, search_range + 1):
        if collatz_step(m) == n:
            preds.append(m)
    return preds

# 1. mod 6 による入次数の分類検証
print("=" * 70)
print("1. mod 6 による入次数の完全分類")
print("=" * 70)

for r in range(6):
    print(f"\n--- n ≡ {r} (mod 6) ---")
    for n in [r + 6*k for k in range(5) if r + 6*k >= 1]:
        preds_smart = find_predecessors(n)
        preds_brute = brute_force_predecessors(n, search_range=max(6*n+10, 100))
        degree = len(preds_brute)
        smart_ms = sorted([m for _, m in preds_smart])
        if degree != len(preds_smart):
            print(f"  n={n}: MISMATCH! Smart={smart_ms}, Brute={preds_brute}")
        elif n <= 30:
            print(f"  n={n}: indegree={degree}, preds={preds_brute}")

# 2. n ≡ 4 (mod 6) のときのみ入次数2であることの大規模検証
print("\n" + "=" * 70)
print("2. 大規模検証: N=10^5 までの全ての n で入次数を確認")
print("=" * 70)

N = 100_000
mismatches = 0
count_deg1 = 0
count_deg2 = 0

for n in range(1, N + 1):
    preds = find_predecessors(n)
    expected_deg = 2 if n % 6 == 4 else 1
    actual_deg = len(preds)

    if actual_deg != expected_deg:
        mismatches += 1
        if mismatches <= 10:
            print(f"  MISMATCH: n={n}, expected indegree={expected_deg}, got={actual_deg}, preds={preds}")

    if actual_deg == 1:
        count_deg1 += 1
    elif actual_deg == 2:
        count_deg2 += 1

print(f"  Total n checked: {N}")
print(f"  Indegree 1: {count_deg1}")
print(f"  Indegree 2: {count_deg2}")
print(f"  Mismatches: {mismatches}")

# 3. 奇数前駆が存在する条件の詳細分析
print("\n" + "=" * 70)
print("3. 奇数前駆が存在する条件の詳細分析")
print("=" * 70)

print("\n奇数前駆 m = (n-1)/3 が存在する条件:")
print("  (i)   n ≡ 1 (mod 3)   ... (n-1) が 3 で割り切れる")
print("  (ii)  (n-1)/3 が奇数  ... m が奇数")
print("  (iii) (n-1)/3 > 0     ... m > 0")
print()

# n ≡ 1 (mod 3) の中で (n-1)/3 が奇数になる条件
print("n ≡ 1 (mod 3) の場合を mod 6 で分類:")
for n_mod6 in range(6):
    if n_mod6 % 3 != 1:
        continue
    # n ≡ 1 (mod 6) と n ≡ 4 (mod 6)
    sample_n = n_mod6 if n_mod6 > 0 else 6
    m_val = (sample_n - 1) // 3
    print(f"  n ≡ {n_mod6} (mod 6): (n-1)/3 のパリティ = {'奇数' if m_val % 2 == 1 else '偶数'}")

# n ≡ 1 (mod 6): (n-1)/3 = (6k)/3 = 2k（偶数）→ 奇数前駆なし
# n ≡ 4 (mod 6): (n-1)/3 = (6k+3)/3 = 2k+1（奇数）→ 奇数前駆あり！
print()
print("結論:")
print("  n ≡ 1 (mod 6): m = (n-1)/3 は偶数 → 奇数前駆なし")
print("  n ≡ 4 (mod 6): m = (n-1)/3 は奇数 → 奇数前駆あり!")
print("  n ≡ 0,2,3,5 (mod 6): n ≢ 1 (mod 3) → 奇数前駆の候補なし")

# 4. 前駆ノードの数学的完全性の確認
print("\n" + "=" * 70)
print("4. 前駆ノードの網羅性確認 (ブルートフォース vs 解析)")
print("=" * 70)

all_ok = True
for n in range(1, 1001):
    preds_smart = sorted([m for _, m in find_predecessors(n)])
    preds_brute = brute_force_predecessors(n, search_range=3*n+10)
    if preds_smart != preds_brute:
        print(f"  MISMATCH at n={n}: smart={preds_smart}, brute={preds_brute}")
        all_ok = False

if all_ok:
    print(f"  全て一致 (n=1..1000, 探索範囲 3n+10)")

# 5. 数学的証明の骨子
print("\n" + "=" * 70)
print("5. 入次数 ≤ 2 の数学的証明の骨子")
print("=" * 70)

print("""
定理: 任意の正整数 n に対して、collatzStep(m) = n となる正整数 m の数は最大2。

証明:
  collatzStep(m) = n となる m を分類する。

  Case 1: m が偶数のとき
    collatzStep(m) = m/2 = n ⟹ m = 2n
    これは一意に定まる。

  Case 2: m が奇数のとき
    collatzStep(m) = 3m+1 = n ⟹ m = (n-1)/3
    条件: n ≡ 1 (mod 3) かつ (n-1)/3 が奇数。

    n ≡ 1 (mod 3) ⟺ n = 3k+1 (k ≥ 0)
    (n-1)/3 = k
    k が奇数 ⟺ k ≡ 1 (mod 2) ⟺ n = 3(2j+1)+1 = 6j+4 ⟺ n ≡ 4 (mod 6)

    よって、奇数前駆は n ≡ 4 (mod 6) のとき正確に1つ存在し、
    それ以外のときは存在しない。

  まとめ:
    - n ≡ 4 (mod 6): 偶数前駆 2n + 奇数前駆 (n-1)/3 の計2つ
    - それ以外: 偶数前駆 2n のみ（計1つ）

    いずれの場合も入次数 ≤ 2。 □

Lean形式化に必要な補題:
  1. collatzStep_double: collatzStep(2n) = n （既存）
  2. collatzStep_odd_pred: n ≡ 4 (mod 6) → collatzStep((n-1)/3) = n
  3. collatzStep_pred_complete: collatzStep(m) = n → m = 2n ∨ (m = (n-1)/3 ∧ n % 6 = 4)
  4. collatz_indegree_le_two: 入次数 ≤ 2 の定理 (上記3の帰結)
""")

# 6. n ≡ 4 (mod 6) の同値条件の確認
print("=" * 70)
print("6. n ≡ 4 (mod 6) の同値条件")
print("=" * 70)

count = 0
for n in range(1, 10001):
    has_odd_pred = (n >= 1 and (n - 1) % 3 == 0 and (n - 1) // 3 > 0 and ((n - 1) // 3) % 2 == 1)
    is_4mod6 = (n % 6 == 4)
    if has_odd_pred != is_4mod6:
        count += 1
        if count <= 5:
            print(f"  n={n}: has_odd_pred={has_odd_pred}, n%6==4: {is_4mod6}")

if count == 0:
    print(f"  完全一致: n=1..10000 で「奇数前駆存在 ⟺ n ≡ 4 (mod 6)」が確認")
else:
    print(f"  不一致 {count} 件")

# 7. Lean証明で使う具体的な mod 計算
print("\n" + "=" * 70)
print("7. Lean証明に必要な mod 計算")
print("=" * 70)

print("\ncollatzStep(m) = n かつ m が奇数のとき:")
print("  3m + 1 = n")
print("  m = (n-1)/3")
print("  m が奇数 ⟺ (n-1)/3 が奇数")
print()
print("n % 6 別の (n-1)/3 のパリティ:")
for r in range(6):
    if (r - 1) % 3 == 0 and r >= 1:
        m = (r - 1) // 3
        print(f"  n ≡ {r} (mod 6): n-1 ≡ {r-1} (mod 6), (n-1)/3 ≡ {m} (mod 2) [{'奇数' if m % 2 == 1 else '偶数'}]")
    else:
        if r >= 1:
            print(f"  n ≡ {r} (mod 6): (n-1) % 3 = {(r-1) % 3} ≠ 0 → 奇数前駆なし")
        else:
            print(f"  n ≡ {r} (mod 6): n=0 は考慮外（n≥1）")

print("\n完了!")
