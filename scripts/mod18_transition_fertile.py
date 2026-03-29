#!/usr/bin/env python3
"""
探索194: mod18遷移行列 + 肥沃率2/3 の分析

Syracuse逆像 root(m) のmod6分類:
- syracuse(n) = m のとき、最小の逆像 root(m) = (2m-1)/3 (m ≡ 2 mod 3) として計算
- root(m) が存在するためには m ≡ 2 (mod 3) (つまり 3 ∤ m)
- 肥沃率 = P(3 ∤ m) = 2/3

mod18遷移行列:
- Syracuse は奇数→奇数の写像
- 奇数を mod 18 で分類: 1,3,5,7,9,11,13,15,17 の9クラス
- ただし Syracuse の像は 3 の倍数でない(探索195で証明済み)ので、
  mod 18 の中で 9, 3, 15 は「到達不能」
"""

from collections import defaultdict

# ========================================
# Part 1: Syracuse の mod 6 逆像分類
# ========================================

def v2(n):
    """2-adic valuation"""
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

def syracuse(n):
    """Syracuse function for odd n"""
    m = 3 * n + 1
    return m // (2 ** v2(m))

print("=" * 70)
print("Part 1: Syracuse 逆像の mod 6 分類")
print("=" * 70)

# root(m) = (2m - 1) / 3 が整数になる条件: 2m - 1 ≡ 0 (mod 3) ⟺ 2m ≡ 1 (mod 3) ⟺ m ≡ 2 (mod 3)
# root(m) は最小の逆像

print("\nm mod 6 と root(m) の存在:")
for r in range(6):
    m_example = r if r > 0 else 6
    root_exists = (m_example % 3 != 0)
    fertile = m_example % 3 != 0
    if m_example > 0 and m_example % 2 == 1:
        print(f"  m ≡ {r} (mod 6): 肥沃={fertile}, 奇数={'Yes' if r%2==1 else 'No'}")

# ========================================
# Part 2: mod 6 肥沃率の計算
# ========================================
print("\n" + "=" * 70)
print("Part 2: 肥沃率（3の倍数でない率）")
print("=" * 70)

# 奇数のうち mod 3 で:
# mod 3 = 0: 不肥沃 (3の倍数)
# mod 3 = 1: 肥沃
# mod 3 = 2: 肥沃
# 奇数は mod 6 で 1, 3, 5 のいずれか
# mod 6 = 1: mod 3 = 1 → 肥沃
# mod 6 = 3: mod 3 = 0 → 不肥沃
# mod 6 = 5: mod 3 = 2 → 肥沃
# よって肥沃率 = 2/3

print("\n奇数のmod6分類と肥沃性:")
print("  m ≡ 1 (mod 6): m%3=1, 肥沃 (逆像あり)")
print("  m ≡ 3 (mod 6): m%3=0, 不肥沃 (逆像なし)")
print("  m ≡ 5 (mod 6): m%3=2, 肥沃 (逆像あり)")
print(f"\n肥沃率 = 2/3 (正確)")

# 数値検証
N = 100000
odd_numbers = range(1, 2*N, 2)
fertile_count = sum(1 for n in odd_numbers if n % 3 != 0)
total = sum(1 for _ in odd_numbers)
print(f"\n数値検証 (奇数 1..{2*N-1}):")
print(f"  全奇数数: {total}")
print(f"  肥沃数: {fertile_count}")
print(f"  肥沃率: {fertile_count/total:.6f} (理論値: {2/3:.6f})")

# ========================================
# Part 3: root(m) の mod 6 ケース分け
# ========================================
print("\n" + "=" * 70)
print("Part 3: root(m) = (2m-1)/3 の mod 6 場合分け")
print("=" * 70)

# m は奇数で m%3 ≠ 0 のとき root(m) = (2m-1)/3
# m ≡ 1 (mod 6): root = (2*1-1)/3 = 1/3 → m=1: root=1/3 NG
#   m = 6k+1: root = (12k+2-1)/3 = (12k+1)/3... 
#   12k+1 ≡ 1 (mod 3) ≠ 0 → 整数でない!

# 再考: root の正しい計算
# syracuse(n) = m のとき、n が逆像
# 最小の n: n_0 = (2^{v2(3n_0+1)} * m - 1) / 3
# これは v2(3n_0+1) に依存するので単純ではない
# 
# しかし syracuse_four_mul_add_one より n → 4n+1 で同じ像になるので
# 逆像は n_0, 4n_0+1, 4(4n_0+1)+1, ... の等差的構造

# root(m) の正しい定義を再確認
# collatzStep の逆像: m の前像は 2m (偶数) と (m-1)/3 (奇数、m≡4 mod 6のとき)
# Syracuse の逆像は異なる

# Syracuse(n) = (3n+1)/2^{v2(3n+1)} = m
# ⟺ 3n+1 = m * 2^{v2(3n+1)}
# ⟺ n = (m * 2^j - 1) / 3  ここで j = v2(3n+1)

# j=1: n = (2m-1)/3, 条件: 3 | (2m-1) ⟺ m ≡ 2 (mod 3)
# j=2: n = (4m-1)/3, 条件: 3 | (4m-1) ⟺ m ≡ 1 (mod 3)

print("\nSyracuse逆像 n = (2^j * m - 1)/3 の存在条件:")
for j in range(1, 7):
    required_mod3 = pow(2, j, 3)  # 2^j mod 3
    # 2^j * m ≡ 1 (mod 3) ⟺ m ≡ 2^{-j} (mod 3)
    # 2 ≡ -1 (mod 3) なので 2^j ≡ (-1)^j (mod 3)
    # j odd: 2^j ≡ 2 (mod 3), need m ≡ 2 (mod 3) since 2*2=4≡1
    # j even: 2^j ≡ 1 (mod 3), need m ≡ 1 (mod 3) since 1*1=1
    inv_2j = 2 if j % 2 == 1 else 1  # (2^j)^{-1} mod 3
    print(f"  j={j}: 2^j≡{pow(2,j,3)} (mod 3), 整数条件: m ≡ {inv_2j} (mod 3)")

print("\nつまり:")
print("  j奇数 → m ≡ 2 (mod 3) が必要")
print("  j偶数 → m ≡ 1 (mod 3) が必要")
print("  いずれも m ≡ 0 (mod 3) では逆像なし (不肥沃)")

# ========================================
# Part 4: mod 18 遷移行列
# ========================================
print("\n" + "=" * 70)
print("Part 4: mod 18 遷移行列（奇数のSyracuse写像）")
print("=" * 70)

# mod 18 での奇数は: 1, 3, 5, 7, 9, 11, 13, 15, 17
odd_residues_18 = [r for r in range(18) if r % 2 == 1]
print(f"\nmod 18 の奇数剰余: {odd_residues_18}")

# 各 mod 18 クラスから Syracuse でどこに行くか
transition = defaultdict(lambda: defaultdict(int))
tested_count = defaultdict(int)

for n in range(1, 200001, 2):  # 奇数
    r_from = n % 18
    s = syracuse(n)
    r_to = s % 18
    transition[r_from][r_to] += 1
    tested_count[r_from] += 1

print("\nmod 18 遷移行列 (行: 入力mod18, 列: 出力mod18):")
print(f"{'From':>6}", end="")
for r in odd_residues_18:
    print(f" {r:>6}", end="")
print()

for r_from in odd_residues_18:
    print(f"{r_from:>6}", end="")
    total_from = tested_count[r_from]
    for r_to in odd_residues_18:
        count = transition[r_from][r_to]
        if count > 0:
            pct = count / total_from * 100
            print(f" {pct:5.1f}%", end="")
        else:
            print(f"    0%", end="")
    print(f"  (N={total_from})")

# ========================================
# Part 5: 3の倍数の排除確認
# ========================================
print("\n" + "=" * 70)
print("Part 5: 3の倍数クラス（3,9,15）への遷移確認")
print("=" * 70)

for r_from in odd_residues_18:
    hits_to_3mult = sum(transition[r_from][r] for r in [3, 9, 15])
    print(f"  mod18={r_from} → 3の倍数クラスへの遷移: {hits_to_3mult}")

# ========================================
# Part 6: 6ケース split + omega 設計
# ========================================
print("\n" + "=" * 70)
print("Part 6: 形式化設計 - root(m) の mod 6 分類")
print("=" * 70)

# 正確なroot: syracuse の「最小逆像」
# n_j(m) = (2^j * m - 1) / 3 (存在するjのうち最小のもの)
# 
# m ≡ 1 (mod 6): m%3=1 → 最小 j は偶数(j=2): n = (4m-1)/3
#   n = (4(6k+1)-1)/3 = (24k+3)/3 = 8k+1, n ≡ 1 (mod 8)
# m ≡ 5 (mod 6): m%3=2 → 最小 j は奇数(j=1): n = (2m-1)/3  
#   n = (2(6k+5)-1)/3 = (12k+9)/3 = 4k+3, n ≡ 3 (mod 4)

print("\n最小逆像 root(m) の存在と mod 分類:")
print()

# 数値検証
for m_mod6 in [1, 3, 5]:
    print(f"m ≡ {m_mod6} (mod 6):")
    examples = [m_mod6 + 6*k for k in range(5) if m_mod6 + 6*k > 0 and (m_mod6 + 6*k) % 2 == 1]
    for m in examples[:5]:
        # 最小の正の奇数 n で syracuse(n) = m
        found = None
        for n in range(1, 1000, 2):
            if syracuse(n) == m:
                found = n
                break
        if found:
            print(f"  m={m}: root={found}, root%6={found%6}, root%4={found%4}, root%8={found%8}")
        else:
            print(f"  m={m}: 逆像なし")
    print()

# ========================================
# Part 7: 完全な mod 18 → mod 18 理論分析
# ========================================
print("\n" + "=" * 70)
print("Part 7: Syracuse の mod 18 理論分析")
print("=" * 70)

# 奇数 n の mod 18 クラスから syracuse(n) の mod 18 を代数的に求める
print("\n代数的 mod 18 遷移 (n=18q+r の場合):")
for r in odd_residues_18:
    # 3n+1 = 3(18q+r)+1 = 54q + 3r + 1
    val_3r_1 = 3 * r + 1
    v2_val = v2(val_3r_1)
    syr_r = val_3r_1 // (2 ** v2_val)
    
    # Syracuse(18q+r) = (54q + 3r+1) / 2^v2(54q + 3r+1)
    # ここで v2 は q にも依存するが、最小の v2 は v2(3r+1) で決まる部分がある
    # 正確には: 54q + 3r+1 = 2^v2(3r+1) * ((54q)/(2^v2(3r+1)) + (3r+1)/(2^v2(3r+1)))
    
    # r=1: 3r+1=4, v2=2, syr = (54q+4)/4 = (27q+2)/2... qの偶奇に依存
    # これは mod 18 では確定しない場合がある
    
    # 厳密には mod 18 で v2(3n+1) が確定するか?
    # n ≡ r (mod 18) → 3n+1 ≡ 3r+1 (mod 54)
    # v2(3n+1) は 3n+1 の2冪因子なので、3r+1 の2冪因子が最低保証
    
    # 例: r=1: 3r+1=4=2^2, 54qは2の倍数なので v2(54q+4) ≥ 2
    #   q偶: 54q ≡ 0 mod 4, 54q+4 ≡ 0 mod 4, v2 ≥ 2
    #   q奇: 54q ≡ 54 ≡ 2 mod 4, 54q+4 ≡ 6 ≡ 2 mod 4 → v2 = 1? NO
    #   54*1+4 = 58, v2(58) = 1. Wait: n=18+1=19, 3*19+1=58, v2(58)=1
    
    # mod 18 だけでは v2 が確定しない!
    # mod 36 が必要か?
    
    # 実際の遷移を見る
    examples_n = [r + 18*q for q in range(20) if r + 18*q > 0]
    syrs = [syracuse(n) % 18 for n in examples_n]
    unique_targets = sorted(set(syrs))
    
    print(f"  n≡{r:2d} (mod 18): 3r+1={val_3r_1:3d}, v2(3r+1)={v2_val}, "
          f"遷移先mod18={unique_targets}")

# ========================================
# Part 8: mod 36 分析
# ========================================
print("\n" + "=" * 70)
print("Part 8: mod 36 での確定性分析")
print("=" * 70)

odd_residues_36 = [r for r in range(36) if r % 2 == 1]

deterministic_count = 0
total_classes = 0

for r in odd_residues_36:
    examples_n = [r + 36*q for q in range(50) if r + 36*q > 0]
    if not examples_n:
        continue
    syrs = [syracuse(n) % 18 for n in examples_n]
    unique_targets = sorted(set(syrs))
    is_deterministic = len(unique_targets) == 1
    total_classes += 1
    if is_deterministic:
        deterministic_count += 1
    if not is_deterministic:
        print(f"  n≡{r:2d} (mod 36): 遷移先mod18={unique_targets} (非確定的)")

print(f"\n確定的クラス: {deterministic_count}/{total_classes}")

# ========================================
# Part 9: Lean形式化設計
# ========================================
print("\n" + "=" * 70)
print("Part 9: Lean 4 形式化設計")
print("=" * 70)

design = """
=== Lean 4 形式化設計: mod18遷移行列 + 肥沃率2/3 ===

【定理1: fertile_rate_two_thirds】
-- 奇数 m のうち 3 で割れないもの(肥沃)の割合は 2/3
-- 奇数を mod 6 で分類: {1,3,5}、このうち 3 が不肥沃
-- Finset版: Finset.filter (fun m => m%3 ≠ 0) (Finset.filter Odd (Finset.range N))

theorem fertile_iff_not_div_three (m : Nat) (hm : m % 2 = 1) :
    (∃ n : Nat, n ≥ 1 ∧ n % 2 = 1 ∧ syracuse n = m) ↔ m % 3 ≠ 0 := sorry
-- 注: ← 方向は syracuse_four_mul_add_one を使った構成が必要
-- → 方向は three_mul_add_one_mod3 から従う (3n+1 は常に mod3≡1)

【定理2: syracuse_image_not_div_three (既に証明済み)】
-- syracuse(n) % 3 ≠ 0 (n ≥ 1, n奇数)
-- Structure.lean の syracuse_not_div_three として存在

【定理3: odd_mod6_trichotomy】
-- 奇数 m は mod 6 で 1, 3, 5 のいずれか
theorem odd_mod6_trichotomy (m : Nat) (hm : m % 2 = 1) :
    m % 6 = 1 ∨ m % 6 = 3 ∨ m % 6 = 5 := by omega

【定理4: fertile_count_exact】
-- {1..6N} の奇数のうち肥沃なものは正確に 2N 個
-- 全奇数は 3N 個なので肥沃率 = 2N/3N = 2/3
theorem fertile_count_in_range (N : Nat) (hN : N ≥ 1) :
    (Finset.filter (fun m => m % 3 ≠ 0 ∧ m % 2 = 1) (Finset.range (6*N+1))).card
    = 2 * N := by sorry

【定理5: syracuse_preimage_j1】
-- j=1 逆像: m ≡ 2 (mod 3) のとき n = (2m-1)/3 は正の奇数で syracuse(n) = m
theorem syracuse_preimage_j1 (m : Nat) (hm : m ≥ 2) (hmod : m % 3 = 2) :
    let n := (2 * m - 1) / 3
    n % 2 = 1 ∧ n ≥ 1 ∧ syracuse n = m := by
  -- n = (2m-1)/3, m = 3k+2 → n = (6k+3)/3 = 2k+1 (奇数)
  -- v2(3n+1) = v2(3(2k+1)+1) = v2(6k+4) = v2(2(3k+2)) = 1 + v2(3k+2)
  -- syracuse(n) = (3n+1)/2^v2(3n+1)
  -- 3n+1 = 2m なので syracuse(n) = 2m/2 = m iff v2(3n+1) = 1
  -- しかし v2(3n+1) = 1 は n ≡ 3 mod 4 のとき
  sorry

【定理6: syracuse_preimage_j2】  
-- j=2 逆像: m ≡ 1 (mod 3) のとき n = (4m-1)/3 は正の奇数で syracuse(n) = m
theorem syracuse_preimage_j2 (m : Nat) (hm : m ≥ 1) (hmod : m % 3 = 1) :
    let n := (4 * m - 1) / 3
    n % 2 = 1 ∧ n ≥ 1 ∧ syracuse n = m := by
  sorry

【定理7: root_mod6_classification】
-- root(m) の mod 分類
-- m ≡ 1 (mod 6): root = (4m-1)/3, root ≡ 1 (mod 8)
-- m ≡ 5 (mod 6): root = (2m-1)/3, root ≡ 3 (mod 4)
-- m ≡ 3 (mod 6): 逆像なし (不肥沃)

=== 証明戦略 ===
各定理は omega タクティクと既存の v2/syracuse 補題を活用。
6ケースの split は `omega` で自動化可能な範囲が大きい。
"""
print(design)
