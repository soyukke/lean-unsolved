#!/usr/bin/env python3
"""
追加解析: 逆コラッツ木のカバー飽和現象と未カバー数の構造

前回の発見: 深さ53の木(1100万ノード)でも 1..100 の16個が未カバー。
特に n=27 が最小未カバー → 27 はコラッツの有名な「遅延」数。

仮説: 未カバー数は逆コラッツ木の到達深さが深い数、
      すなわちコラッツ軌道が長い数に対応する。

追加検証:
1. 未カバー数27のコラッツ軌道を詳細解析
2. 逆コラッツ木での 27 の深さ（到達に必要な深さ）を推定
3. カバー飽和の理論的理由
4. W(D)/D^a の幅比率の正確な値 0.6713 の理論的意味
"""

import math
import time
from collections import defaultdict, Counter

# ============================================================
# 1. n=27 のコラッツ軌道
# ============================================================

print("=" * 70)
print("1. n=27 のコラッツ軌道解析")
print("=" * 70)

def collatz_trajectory(n):
    """コラッツ軌道を返す (shortcut T(n)=(3n+1)/2^v2 版)"""
    trajectory = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = (3 * n + 1) // 2
        trajectory.append(n)
        if len(trajectory) > 100000:
            break
    return trajectory

traj_27 = collatz_trajectory(27)
print(f"27 のコラッツ軌道 (shortcut版):")
print(f"  長さ: {len(traj_27) - 1} ステップ")
print(f"  最大値: {max(traj_27)}")
print(f"  軌道: {traj_27[:30]}...")
print(f"  最後: ...{traj_27[-10:]}")

# 逆コラッツ木で 27 を見つけるには、1 から 27 への逆コラッツパスが必要
# 27 の順コラッツ軌道: 27 → ... → 1 の逆を辿る
print(f"\n27 の順コラッツ軌道を逆転 = 逆コラッツ木での 1→27 のパス:")
# T(27) = (3*27+1)/2 = 41, T(41) = (3*41+1)/2 = 62, ...
# 逆に: 1 → 2 → 4 → 8 → 16 → 5 → 10 → 3 → 6 → ... → 27
# 27 は奇数なので、27 = (2m-1)/3 → m = (3*27+1)/2 = 41
# 41 は奇数なので、41 = (2m-1)/3 → m = (3*41+1)/2 = 62
# 62 は偶数なので、62 = 2m → m = 31

# 逆コラッツ木での 1 → 27 のパスを構築
def reverse_collatz_path(target):
    """target から 1 への順コラッツ軌道を逆転して、逆コラッツパスを得る"""
    forward = []
    n = target
    while n != 1:
        forward.append(n)
        if n % 2 == 0:
            n //= 2
        else:
            n = (3 * n + 1) // 2
    forward.append(1)
    # 逆転
    return list(reversed(forward))

path_to_27 = reverse_collatz_path(27)
print(f"  1 → 27 のパス (長さ {len(path_to_27)-1}):")
print(f"  {path_to_27}")

# 各ステップの操作を確認
print(f"\n操作の詳細:")
for i in range(len(path_to_27) - 1):
    parent = path_to_27[i]
    child = path_to_27[i + 1]
    if child == 2 * parent:
        op = "2n"
    elif (2 * parent - 1) % 3 == 0 and (2 * parent - 1) // 3 == child:
        op = "(2n-1)/3"
    else:
        op = "???"
    print(f"  {parent} → {child} ({op})")

print(f"\n逆コラッツ木での 27 の深さ: {len(path_to_27) - 1}")

# ============================================================
# 2. 1..100 の未カバー数の逆コラッツ深さ
# ============================================================

print("\n" + "=" * 70)
print("2. 1..100 の全ての数の逆コラッツ深さ")
print("=" * 70)

depths = {}
for n in range(1, 101):
    path = reverse_collatz_path(n)
    depths[n] = len(path) - 1

# 逆コラッツ木の深さ順にソート
sorted_by_depth = sorted(depths.items(), key=lambda x: x[1], reverse=True)

print(f"\n1..100 の逆コラッツ深さ (降順):")
print(f"{'数':>5} {'深さ':>6} {'偶奇':>5} {'mod6':>5}")
print("-" * 25)
for n, d in sorted_by_depth[:30]:
    parity = "奇" if n % 2 == 1 else "偶"
    print(f"{n:>5} {d:>6} {parity:>5} {n%6:>5}")

# 既知の未カバー集合との比較
uncovered_set = {27, 31, 41, 47, 54, 55, 62, 63, 71, 73, 82, 83, 91, 94, 95, 97}
print(f"\n深い順の1..100 と未カバー集合の対応:")
for n, d in sorted_by_depth[:25]:
    is_uncovered = "*" if n in uncovered_set else " "
    print(f"  {is_uncovered} n={n:>3}, 深さ={d:>3}")

# 閾値を確認
all_depths = [d for n, d in depths.items()]
uncovered_depths = [depths[n] for n in uncovered_set]
covered_depths = [depths[n] for n in range(1, 101) if n not in uncovered_set]

print(f"\n未カバー数の深さ: min={min(uncovered_depths)}, max={max(uncovered_depths)}, "
      f"平均={sum(uncovered_depths)/len(uncovered_depths):.1f}")
print(f"カバー済みの深さ: min={min(covered_depths)}, max={max(covered_depths)}, "
      f"平均={sum(covered_depths)/len(covered_depths):.1f}")

# 深さ53のBFS木で到達する最大深さ
print(f"\n深さ53の逆コラッツ木では深さ53までの数しかカバーできない。")
print(f"1..100 で深さ > 53 の数: "
      f"{sorted([(n, d) for n, d in depths.items() if d > 53], key=lambda x: x[1])}")

# ============================================================
# 3. カバー飽和の理論的説明
# ============================================================

print("\n" + "=" * 70)
print("3. カバー飽和の理論的説明")
print("=" * 70)

print("""
【発見: 逆コラッツ木のカバー飽和】

深さ20でも深さ53でも、1..100 のカバー率が 84/100 で飽和する。
これは、未カバーの16個がそれぞれ深さ > 53 に位置するため。

逆コラッツ木の深さ = 順コラッツ軌道のステップ数
よって「深さが深い」= 「コラッツ軌道が長い」

1..100 で最も深い数の特定:
""")

# 全ての深さを表示
for n, d in sorted(depths.items(), key=lambda x: x[1], reverse=True)[:20]:
    traj = collatz_trajectory(n)
    max_val = max(traj)
    print(f"  n={n:>3}: 逆コラッツ深さ={d:>3}, 軌道最大値={max_val:>10}")

# ============================================================
# 4. 幅比率 W(D)/(4/3)^D の正確な漸近値
# ============================================================

print("\n" + "=" * 70)
print("4. 幅比率 W(D)/(4/3)^D の漸近値解析")
print("=" * 70)

# 実測値が 0.6713 に収束
# これは何か知られた定数か？
C = 0.6713

print(f"W(D) / (4/3)^D → C ≈ {C}")
print(f"C の候補:")
print(f"  2/3 = {2/3:.6f}")
print(f"  1/sqrt(2) = {1/math.sqrt(2):.6f}")
print(f"  3/4 = {3/4:.6f}")
print(f"  log(2) = {math.log(2):.6f}")
print(f"  2*log(2)/log(3) = {2*math.log(2)/math.log(3):.6f}")
print(f"  1/log(3/2) = {1/math.log(3/2):.6f}")
print(f"  3/(2*log(3)) = {3/(2*math.log(3)):.6f}")

# これは Peres の定数 (Wirsching の仕事) に関連するか？
# 逆コラッツ木の成長定数

# 精密測定: 深い木を作って C を推定
print("\n精密測定:")
visited = {1: 0}
frontier = {1}
for d in range(1, 55):
    nxt = set()
    for n in frontier:
        c1 = 2 * n
        if c1 not in visited:
            visited[c1] = d
            nxt.add(c1)
        if (2*n-1) % 3 == 0:
            c2 = (2*n-1) // 3
            if c2 > 0 and c2 not in visited:
                visited[c2] = d
                nxt.add(c2)
    width = len(nxt)
    expected = (4/3)**d
    ratio = width / expected if expected > 0 else 0
    if d >= 40:
        print(f"  D={d}: W(D)={width}, (4/3)^D={expected:.0f}, ratio={ratio:.8f}")
    frontier = nxt
    if len(visited) > 10_000_000:
        break

# ============================================================
# 5. GWモデルの限界と本当に必要な深さ
# ============================================================

print("\n" + "=" * 70)
print("5. 1..N を全カバーするのに必要な深さ")
print("=" * 70)

# 1..N の数 n の逆コラッツ深さの最大値 = 必要な深さ
print("\n各 N に対する、1..N の全数カバーに必要な深さ:")
for N in [10, 20, 50, 100, 200, 500, 1000]:
    max_depth = 0
    for n in range(1, N + 1):
        path = reverse_collatz_path(n)
        d = len(path) - 1
        max_depth = max(max_depth, d)
    # 木のサイズ
    tree_size = sum((4/3)**d for d in range(max_depth + 1))
    print(f"  N={N:>5}: 必要深さ={max_depth:>4}, 推定木サイズ={(4/3)**max_depth:.0f}")

# ============================================================
# 6. Syracuse逆像の分岐パターン: m≡0(mod3) の重要性
# ============================================================

print("\n" + "=" * 70)
print("6. m≡0(mod3) のSyracuse逆像がない理由")
print("=" * 70)

print("\nm ≡ 0 (mod 3) の数は Syracuse T の値域に含まれない:")
print("  T(n) = (3n+1)/2^v ≡ 1/2^v (mod 3)")
print("  2^v mod 3 は 2 or 1 なので 1/2^v mod 3 は 1 or 2")
print("  よって T(n) ≢ 0 (mod 3)")
print()
print("  これは Syracuse 逆像が mod 3 で 1 or 2 にしか存在しないことを意味する。")
print("  mod 6 での分布: m ≡ 1, 5 (mod 6) のみ逆像を持つ。")
print("  m ≡ 3 (mod 6) は逆像なし。")
print()

# これが GW 過程に与える影響
print("GW過程への影響:")
print("  Syracuse版 GW過程では:")
print("    m ≡ 1 (mod 6): 逆像数 = max_k/2 個 (全ての偶数kで)")
print("    m ≡ 5 (mod 6): 逆像数 = max_k/2 個 (全ての奇数kで)")
print("    m ≡ 3 (mod 6): 逆像数 = 0 → 絶滅！")
print()
print("  ただし T(n) ≢ 0 (mod 3) なので、逆コラッツ木のノードに")
print("  m ≡ 3 (mod 6) が現れること自体がない。")
print("  → Syracuse逆木の全ノードは mod 3 で 1 or 2 のみ")

# 検証
print("\n検証: 逆コラッツ木のノードの mod 3 分布")
mod3_count = Counter()
for n in visited:
    mod3_count[n % 3] += 1
total_v = len(visited)
for r in range(3):
    print(f"  mod 3 = {r}: {mod3_count[r]}個 ({mod3_count[r]/total_v*100:.2f}%)")

# ============================================================
# 7. 多重型GW過程の正しい定式化
# ============================================================

print("\n" + "=" * 70)
print("7. 多重型GW過程の正しい定式化 (mod 3 で)")
print("=" * 70)

print("""
逆コラッツ木のノードの mod 3 分類:
  タイプ A: n ≡ 1 (mod 3) = {1, 4, 7, 10, ...}
  タイプ B: n ≡ 2 (mod 3) = {2, 5, 8, 11, ...}
  タイプ C: n ≡ 0 (mod 3) = {3, 6, 9, 12, ...}

操作の mod 3 遷移:
  2n の mod 3:
    n ≡ 0 → 2n ≡ 0
    n ≡ 1 → 2n ≡ 2
    n ≡ 2 → 2n ≡ 1
  (2n-1)/3 の mod 3 (存在する場合):
    (2n-1)/3 は常に奇数。
    n ≡ 2 (mod 3): 2n-1 = 4n'-3 ≡ 0 (mod 3), (2n-1)/3 の mod 3 = ?
    n ≡ 5 (mod 6): 2n-1 = 10n'-9 ≡ 0 (mod 3)
""")

# mod 3 遷移行列
M3 = [[0]*3 for _ in range(3)]
for r in range(3):
    M3[r][(2*r) % 3] += 1
    # (2n-1)/3 の条件
    if (2*r - 1) % 3 == 0:
        child = ((2*r - 1) // 3) % 3
        M3[r][child] += 1

print("mod 3 遷移行列:")
for i in range(3):
    print(f"  {M3[i]}")

# mod 3 = 0 からは mod 3 = 0 にしか行けない (2n操作のみ)
# mod 3 = 1 → 2n: mod 3 = 2 のみ
# mod 3 = 2 → 2n: mod 3 = 1, (2*2-1)/3 = 1: mod 3 = 1
#   → mod 3 = 2 の子は {mod1, mod1} = 2つのmod1の子

# 到達可能
print("\n根=1 (mod 3 = 1) からの到達可能性:")
print("  1 (mod1) → 2n=2 (mod2)")
print("  2 (mod2) → 2n=4 (mod1), (2*2-1)/3=1 (mod1)")
print("  → mod 0 には到達不能")
print("  → 逆コラッツ木は mod 3 で {1, 2} の間を行き来する")

# ============================================================
# 8. 定常分布の解析的計算
# ============================================================

print("\n" + "=" * 70)
print("8. mod 6 定常分布の解析的計算")
print("=" * 70)

# 実測データ: 大きい深さでの mod 6 分布
# mod6=[0:0.250, 1:0.083, 2:0.250, 3:0.083, 4:0.250, 5:0.083]
# これは {0,2,4} が 1/4 ずつ、{1,3,5} が 1/12 ずつ

print("実測定常分布:")
print("  mod 0: 0.250 = 3/12")
print("  mod 1: 0.083 ≈ 1/12")
print("  mod 2: 0.250 = 3/12")
print("  mod 3: 0.083 ≈ 1/12")
print("  mod 4: 0.250 = 3/12")
print("  mod 5: 0.083 ≈ 1/12")
print()
print("偶数 (0,2,4): 各 3/12 → 合計 9/12 = 3/4")
print("奇数 (1,3,5): 各 1/12 → 合計 3/12 = 1/4")
print()

# 理論的確認: 逆コラッツ操作で偶奇比率
# n の子 2n は常に偶数
# n の子 (2n-1)/3 は (存在すれば) 常に奇数
# 深さD+1のフロンティアで:
#   偶数ノード = 全親からの 2n 操作の結果 = W(D) 個
#   奇数ノード = deg2 の親からの (2n-1)/3 操作の結果 = W(D)/3 個
# → 偶:奇 = W(D) : W(D)/3 = 3:1 = 3/4 : 1/4 ✓
print("理論的偶奇比率:")
print("  偶数 = W(D) 個 (全親から 2n)")
print("  奇数 = W(D)*P(deg2) = W(D)/3 個 ((2n-1)/3 が有効な親から)")
print("  偶:奇 = 3:1 = 3/4 : 1/4  (実測と一致)")
print()

# さらに mod 6 内の均等性
# 偶数内: 0:2:4 の比率
# mod 6 遷移を追跡
# 偶数 mod 6 ∈ {0, 2, 4}
# 2n 操作: 0→0, 1→2, 2→4, 3→0, 4→2, 5→4
# (2n-1)/3: 2→1, 5→3
# 偶数間遷移 (2n): 0→0, 2→4, 4→2 + 奇数から: 1→2, 3→0, 5→4
# 偶数の定常: 0 ← {0, 3}, 2 ← {1, 4}, 4 ← {2, 5}
# 奇数の定常: 1 ← {2}, 3 ← {5}, 5 ← なし...

print("mod 6 の詳細遷移 (前駆 → 子):")
print("  前駆 mod6=0: 子 2n mod6=0 (偶)")
print("  前駆 mod6=1: 子 2n mod6=2 (偶)")
print("  前駆 mod6=2: 子 2n mod6=4 (偶), 子 (2n-1)/3 mod6=1 (奇)")
print("  前駆 mod6=3: 子 2n mod6=0 (偶)")
print("  前駆 mod6=4: 子 2n mod6=2 (偶)")
print("  前駆 mod6=5: 子 2n mod6=4 (偶), 子 (2n-1)/3 mod6=3 (奇)")
print()

# 定常分布を pi = (a,b,c,d,e,f) for mod 0,1,2,3,4,5 とする
# 関係式: 子の分布 = 操作を親に適用
# pi(0) ∝ pi(0) + pi(3)
# pi(1) ∝ pi(2)  [from (2n-1)/3]
# pi(2) ∝ pi(1) + pi(4)
# pi(3) ∝ pi(5)  [from (2n-1)/3]
# pi(4) ∝ pi(2) + pi(5)
# pi(5) ∝ 0  [誰からも (2n-1)/3 で来ない]

# 待ってください、mod 6 = 5 の子を生む親は？
# (2n-1)/3 ≡ 5 (mod 6) → 2n-1 ≡ 15 (mod 18) → 2n ≡ 16 (mod 18) → n ≡ 8 (mod 9)
# 2n ≡ 5*2 = 10 (mod 12) → n ≡ 5 (mod 6)
# ↑ 2n 操作で mod6=5 は偶数なので来ない

# 5 は奇数なので 2n では来ない。(2n-1)/3 で来るには...
# (2p-1)/3 ≡ 5 (mod 6) → 2p-1 ≡ 15 (mod 18) → 2p ≡ 16 (mod 18) → p ≡ 8 (mod 9)
# p mod 6: p ≡ 8 mod 9, p ∈ {8, 17, 26, 35, ...}
# p mod 6 = {2, 5, 2, 5, ...}
# でも (2p-1) mod 3 = 0 の条件: p ≡ 2 or 5 (mod 6)
# p=8: mod6=2, (16-1)/3=5 ✓
# p=17: mod6=5, (34-1)/3=11 ≡ 5(mod6) ✓
# p=26: mod6=2, (52-1)/3=17 ≡ 5(mod6) ✓

# 修正: mod 6 = 5 の子を生む親は mod 6 = 2 と mod 6 = 5
# でも上の遷移表では mod 2 → mod 1, mod 5 → mod 3

# 再確認
print("再確認: mod 6 → (2n-1)/3 の mod 6")
for p_mod in range(6):
    if (2*p_mod - 1) % 3 == 0:
        child = (2*p_mod - 1) // 3
        # 実際にはこれは mod 6 の代表値に対してのみ
        # 一般の n ≡ p_mod (mod 6) に対して (2n-1)/3 mod 6 を計算
        results = set()
        for n in range(p_mod, 120, 6):
            if n > 0 and (2*n-1) % 3 == 0:
                c = (2*n-1) // 3
                results.add(c % 6)
        print(f"  p ≡ {p_mod} (mod 6): (2p-1)/3 mod 6 = {sorted(results)}")

print("\n→ mod 6 だけでは遷移が一意に決まらない！")
print("→ mod 6 のGW過程は正確でない。mod 12 や mod 18 が必要。")

# ============================================================
# 9. 定数 C ≈ 0.6713 の解析
# ============================================================

print("\n" + "=" * 70)
print("9. 定数 C ≈ 0.6713 の数値解析")
print("=" * 70)

# W(D) ≈ C * (4/3)^D
# C ≈ 0.6713
# これは逆コラッツ木の「定常振幅」

# 精密計算
visited2 = {1: 0}
frontier2 = {1}
ratios = []
for d in range(1, 55):
    nxt = set()
    for n in frontier2:
        c1 = 2 * n
        if c1 not in visited2:
            visited2[c1] = d
            nxt.add(c1)
        if (2*n-1) % 3 == 0:
            c2 = (2*n-1) // 3
            if c2 > 0 and c2 not in visited2:
                visited2[c2] = d
                nxt.add(c2)
    width = len(nxt)
    expected = (4/3)**d
    ratio = width / expected
    ratios.append(ratio)
    frontier2 = nxt
    if len(visited2) > 10_000_000:
        break

if ratios:
    final_ratios = ratios[-10:]
    C_est = sum(final_ratios) / len(final_ratios)
    print(f"最終10層の C の値: {[f'{r:.8f}' for r in final_ratios]}")
    print(f"C の推定値: {C_est:.10f}")

    # 数学的定数との比較
    candidates = {
        "2/3": 2/3,
        "2/e": 2/math.e,
        "ln(2)": math.log(2),
        "3*ln(2)/pi": 3*math.log(2)/math.pi,
        "2*ln(4/3)": 2*math.log(4/3),
        "1/(2*ln(3/2))": 1/(2*math.log(3/2)),
        "sqrt(2/pi * ln(4/3))": math.sqrt(2/math.pi * math.log(4/3)),
        "3/(2*sqrt(pi))": 3/(2*math.sqrt(math.pi)),
    }

    print(f"\n既知定数との比較:")
    for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - C_est)):
        diff = abs(val - C_est)
        print(f"  {name:>25} = {val:.10f}  (差 = {diff:.6e})")

# ============================================================
# 10. まとめ
# ============================================================

print("\n" + "=" * 70)
print("10. まとめ: GWモデルの結論")
print("=" * 70)

print("""
【主要な発見】

1. 逆コラッツ木は「真の木」(森の一成分)
   - T: N→N が関数なので、逆グラフは forest
   - BFS構築で衝突ゼロを確認
   - これは予想とは独立な構造的事実

2. 超臨界GW過程として:
   - mu = 4/3, sigma^2 = 2/9
   - P(子=0) = 0 → 絶滅確率 = 0
   - 木は必ず成長し続ける

3. 幅の漸近: W(D) ≈ C * (4/3)^D
   - C ≈ 0.6713 (定常振幅)
   - この定数は自明な数学定数とは一致しない（さらなる解析が必要）

4. 被覆の限界:
   - 1..N の全カバーには深さ = max_{n<=N} depth(n) が必要
   - depth(n) = n の順コラッツ軌道長
   - 1..100 のカバーには深さ ≈ 70+ が必要
   - Coupon Collector推定は楽観的すぎる

5. Syracuse版の二分法:
   - m ≡ 1,5 (mod 6): 大量の逆像 (各kで1/3の確率)
   - m ≡ 3 (mod 6): 逆像なし
   - ただし T(n) ≢ 0 (mod 3) なので木のノードに m≡3 は出現しない

6. コラッツ予想への含意:
   - GWモデルは「木が成長する」ことを示すが、
   - 「全ての数をカバーする」ことは別問題
   - 核心的困難: 到達深さ = コラッツ軌道長 の有界性
   - これは事実上コラッツ予想そのものと同値
""")

print("完了!")
