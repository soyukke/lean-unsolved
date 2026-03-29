#!/usr/bin/env python3
"""
コラッツ写像の位相的エントロピー - 詳細追加解析

方法8の逆像成長率が log(4/3) ≈ 0.2877 に収束する兆候を詳しく検証
フィボナッチ数列との一致 (方法6) を理論的に深掘り
"""

import math
import random
from collections import Counter

# ============================================================
# 基本関数
# ============================================================

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m >>= 1
    return m

# ============================================================
# 逆像成長率の精密計算 (大きなnまで)
# ============================================================

def precise_preimage_growth():
    """逆像の成長率を大きなnまで精密に計算"""
    print("=" * 70)
    print("逆像成長率の精密計算")
    print("=" * 70)

    def collatz_preimages(x, max_val=10**15):
        """xのコラッツ写像での逆像"""
        pre = []
        pre.append(2 * x)
        if (2 * x - 1) % 3 == 0:
            y = (2 * x - 1) // 3
            if y > 0 and y % 2 == 1:
                pre.append(y)
        return [p for p in pre if p <= max_val]

    # 複数の始点で試す
    for start in [1, 3, 5, 7, 27]:
        print(f"\n--- 始点: {start} ---")
        max_val = 10**15
        current_set = {start}
        prev_size = 1

        growth_rates = []
        for n in range(1, 51):
            next_set = set()
            for x in current_set:
                for p in collatz_preimages(x, max_val):
                    next_set.add(p)
            current_set = next_set

            size = len(current_set)
            if size > 0:
                h_est = math.log(size) / n
                if prev_size > 0 and size > 0:
                    step_growth = math.log(size / prev_size) if size > prev_size else 0
                else:
                    step_growth = 0
                growth_rates.append(step_growth)
            else:
                h_est = 0
                growth_rates.append(0)

            if n % 5 == 0 or n <= 5:
                print(f"  n={n:3d}: |T^{{-n}}| = {size:12d}, "
                      f"(1/n)log = {h_est:.6f}, "
                      f"step growth = {step_growth:.4f}")

            prev_size = size
            if size > 2000000:
                print(f"  (打ち切り: 集合サイズ超過)")
                break

        # 成長率の収束先を推定
        if len(growth_rates) > 10:
            recent = growth_rates[-10:]
            avg_growth = sum(recent) / len(recent)
            print(f"  直近10ステップの平均成長率: {avg_growth:.6f}")
            print(f"  比較: log(4/3) = {math.log(4/3):.6f}")
            print(f"  比較: log(phi) = {math.log((1+math.sqrt(5))/2):.6f}")

    # 理論的分析
    print(f"\n--- 理論的分析 ---")
    print(f"  各整数 x の逆像数:")
    print(f"    x が偶数: 逆像 = {{2x}} (1個)")
    print(f"    x が奇数で x ≡ 0 mod 3: 逆像 = {{2x}} (1個)")
    print(f"    x が奇数で x ≢ 0 mod 3: 逆像 = {{2x, (2x-1)/3}} (2個)")

    # 実際に逆像数の統計
    count_1 = 0
    count_2 = 0
    N = 100000
    for x in range(1, N + 1):
        pre = collatz_preimages(x, 10**20)
        if len(pre) == 1:
            count_1 += 1
        elif len(pre) == 2:
            count_2 += 1

    p2 = count_2 / N
    print(f"\n  [1, {N}] での統計:")
    print(f"    逆像1個: {count_1} ({count_1/N:.4f})")
    print(f"    逆像2個: {count_2} ({count_2/N:.4f})")
    print(f"  平均逆像数: {(count_1 + 2*count_2)/N:.4f}")
    print(f"  予想成長率 log(平均逆像数): {math.log((count_1 + 2*count_2)/N):.6f}")

    # 理論的計算
    # 偶数: N/2, 全て1個
    # 奇数でmod3=0: N/6, 1個
    # 奇数でmod3≠0: N/3, 2個
    # 平均逆像数 = (N/2*1 + N/6*1 + N/3*2) / N = 1/2 + 1/6 + 2/3 = 4/3
    print(f"\n  理論的平均逆像数:")
    print(f"    = (1/2)*1 + (1/6)*1 + (1/3)*2 = 1/2 + 1/6 + 2/3 = 4/3 ≈ {4/3:.6f}")
    print(f"    log(4/3) = {math.log(4/3):.6f}")

# ============================================================
# フィボナッチ数列とパリティブロック数の一致確認
# ============================================================

def fibonacci_parity_analysis():
    """パリティブロック数がフィボナッチ数列になることの詳細確認"""
    print("\n" + "=" * 70)
    print("パリティブロック数とフィボナッチ数列の関係")
    print("=" * 70)

    # フィボナッチ数列
    fib = [1, 1]
    for i in range(20):
        fib.append(fib[-1] + fib[-2])

    # 実現可能ブロック数
    num_samples = 200000
    orbit_len = 300

    print(f"\n  k | 実現ブロック | F(k+2) | 一致? | (1/k)log(B_k)")
    print(f"  --+-------------+--------+-------+--------------")

    for k in range(1, 21):
        observed_blocks = set()

        for _ in range(num_samples):
            n = random.randint(1, 1000000)
            orbit = []
            x = n
            for _ in range(orbit_len):
                orbit.append(x % 2)
                x = collatz_step(x)

            for i in range(len(orbit) - k):
                block = tuple(orbit[i:i+k])
                observed_blocks.add(block)

        count = len(observed_blocks)
        fib_val = fib[k + 1]  # F(k+2)
        match = "YES" if count == fib_val else "NO"
        h_k = math.log(count) / k if count > 0 else 0

        print(f"  {k:2d} | {count:11d} | {fib_val:6d} | {match:5s} | {h_k:.6f}")

    phi = (1 + math.sqrt(5)) / 2
    print(f"\n  収束先: log(phi) = {math.log(phi):.6f}")
    print(f"  F(k+2)/F(k+1) -> phi = {phi:.6f}")

# ============================================================
# エントロピーの多層構造
# ============================================================

def multilayer_entropy():
    """
    コラッツ写像のエントロピーの多層構造を分析

    層1: パリティ記号力学 (0/1列) => h = log(phi) ≈ 0.4812
    層2: v2列の記号力学 (v2(3x+1)の値) => ?
    層3: 完全な力学系のエントロピー => ?
    """
    print("\n" + "=" * 70)
    print("エントロピーの多層構造")
    print("=" * 70)

    num_samples = 50000
    orbit_len = 200

    # 層2: v2列の統計
    print("\n--- 層2: v2(3x+1) 列のエントロピー ---")

    for k in range(1, 8):
        kgram_counts = Counter()
        total = 0

        for _ in range(num_samples):
            n = random.randint(3, 1000000)
            if n % 2 == 0:
                n += 1

            x = n
            v2_seq = []
            for _ in range(orbit_len):
                if x <= 1:
                    break
                val = 0
                m = 3 * x + 1
                while m % 2 == 0:
                    m >>= 1
                    val += 1
                v2_seq.append(val)
                x = m

            for i in range(len(v2_seq) - k):
                kgram = tuple(v2_seq[i:i+k])
                kgram_counts[kgram] += 1
                total += 1

        if total > 0:
            H_k = -sum(c/total * math.log(c/total) for c in kgram_counts.values() if c > 0)
            h_k = H_k / k
            distinct = len(kgram_counts)
            print(f"  k={k}: 異なる{k}-gram = {distinct:6d}, "
                  f"H_{k} = {H_k:.4f} nats, h_{k} = {h_k:.4f} nats/symbol")

    # 層3: (パリティ, v2) の結合エントロピー
    print("\n--- 層3: (パリティ列, v2列) 結合エントロピー ---")

    # 通常コラッツの拡張記号: 偶数→(0), 奇数→(1, v2(3x+1))
    for k in range(1, 6):
        kgram_counts = Counter()
        total = 0

        for _ in range(num_samples):
            n = random.randint(1, 1000000)

            x = n
            ext_seq = []
            for _ in range(orbit_len):
                if x <= 1:
                    break
                if x % 2 == 0:
                    ext_seq.append('E')
                    x = x // 2
                else:
                    val = 0
                    m = 3 * x + 1
                    while m % 2 == 0:
                        m >>= 1
                        val += 1
                    ext_seq.append(f'O{val}')
                    x = collatz_step(x)  # one step

            for i in range(len(ext_seq) - k):
                kgram = tuple(ext_seq[i:i+k])
                kgram_counts[kgram] += 1
                total += 1

        if total > 0:
            H_k = -sum(c/total * math.log(c/total) for c in kgram_counts.values() if c > 0)
            h_k = H_k / k
            distinct = len(kgram_counts)
            print(f"  k={k}: 異なる{k}-gram = {distinct:6d}, "
                  f"H_{k} = {H_k:.4f} nats, h_{k} = {h_k:.4f} nats/symbol")

# ============================================================
# Syracuse逆像ツリーの成長率とlog(4/3)の精密検証
# ============================================================

def syracuse_preimage_growth():
    """Syracuse写像の逆像成長率"""
    print("\n" + "=" * 70)
    print("Syracuse写像の逆像成長率")
    print("=" * 70)

    def syracuse_preimages(x, max_val=10**15):
        """奇数xのSyracuse写像での逆像 (全て奇数)"""
        pre = []
        # T(y) = (3y+1)/2^v2(3y+1) = x
        # => 3y+1 = x * 2^k for some k >= 1
        # => y = (x * 2^k - 1) / 3
        # y は正の奇数である必要がある
        for k in range(1, 60):
            val = x * (2 ** k) - 1
            if val % 3 == 0:
                y = val // 3
                if y > 0 and y % 2 == 1 and y <= max_val:
                    pre.append(y)
            if x * (2 ** k) > max_val * 3:
                break
        return pre

    for start in [1, 3, 5]:
        print(f"\n--- 始点: {start} ---")
        max_val = 10**12
        current_set = {start}

        for n in range(1, 41):
            next_set = set()
            for x in current_set:
                for p in syracuse_preimages(x, max_val):
                    next_set.add(p)
            current_set = next_set

            size = len(current_set)
            if size > 0:
                h_est = math.log(size) / n
            else:
                h_est = 0

            if n % 5 == 0 or n <= 5:
                print(f"  n={n:3d}: |T_S^{{-n}}| = {size:10d}, "
                      f"(1/n)log = {h_est:.6f}")

            if size > 500000:
                print(f"  (打ち切り)")
                break

# ============================================================
# 理論的まとめ
# ============================================================

def theoretical_summary():
    """理論的結果のまとめ"""
    print("\n" + "=" * 70)
    print("理論的まとめ: コラッツ写像の位相的エントロピー")
    print("=" * 70)

    phi = (1 + math.sqrt(5)) / 2

    print(f"""
  ■ 定義の問題
    コラッツ写像 T: N -> N は非コンパクト空間上の写像。
    Bowen-Dinaburgの位相的エントロピーは通常コンパクト空間で定義。
    非コンパクト空間への拡張には Bowen (1973) の定義が使える。

  ■ パリティ記号力学
    コラッツ軌道のパリティ列は {0,1} 上の記号力学を定義。
    禁止語: "11" (奇数の次は必ず偶数)
    => 黄金比シフト (Golden mean shift) と同型
    => エントロピー = log(phi) = {math.log(phi):.6f} nats = {math.log(phi)/math.log(2):.6f} bits

  ■ 逆像の成長率 (コラッツ写像 T: N -> N)
    |T^{{-n}}(x)| の成長率 ≈ (4/3)^n
    理由: 平均逆像数 = 4/3 (偶数:1個, 奇数mod3≠0:2個, 奇数mod3=0:1個)
    => log(4/3) = {math.log(4/3):.6f}

  ■ リアプノフ指数とRuelle不等式
    Syracuse写像のリアプノフ指数 ≈ -0.283 (負)
    通常コラッツのリアプノフ指数 ≈ -0.094 (負)
    Ruelle不等式: h_mu(T) <= max(0, lambda) = 0
    => 不変測度のメトリックエントロピーは 0

  ■ 候補 log_2(3) ≈ 1.585 の検討
    log_2(3) = log(3)/log(2) は2進シフトとの比較で自然に現れる。
    しかしこれは「コラッツの各奇数ステップでの拡大率 log(3)」を
    2進シフトのエントロピー log(2) で正規化したもの。
    位相的エントロピー h(T) そのものとは別の量。

  ■ 結論
    コラッツ写像のエントロピー的性質は多層的:

    1. 位相的エントロピー (厳密): 定義域がNのため技術的に困難
       - 有限切断 [1,N] では N→∞ で定義可能
       - 逆像成長率から h_top ≈ log(4/3) = {math.log(4/3):.6f}

    2. 記号力学的エントロピー:
       - パリティ列: log(phi) = {math.log(phi):.6f} (黄金比シフト)
       - v2列: より高い (無限アルファベット)

    3. メトリックエントロピー: 0 (コラッツ予想が真なら)

    4. log(3)/log(2) ≈ 1.585:
       - 位相的エントロピーではない
       - 「1奇数ステップあたりの情報生成率」として解釈可能
       - 3x+1操作が持つ本質的な「複雑さの種」

  ■ 新発見: log(4/3)の意味
    逆像成長率 log(4/3) ≈ 0.2877 は、
    コラッツ写像の「分岐の複雑さ」を直接測る量。

    log(4/3) = log(4) - log(3) = 2*log(2) - log(3)

    これは log(2) と log(3) の差に関連し、
    コラッツ予想の本質的な困難さ (2と3の算術的独立性) と
    力学系的複雑さが結びつくことを示唆する。
""")

# ============================================================
# メイン
# ============================================================

if __name__ == "__main__":
    random.seed(42)

    precise_preimage_growth()
    fibonacci_parity_analysis()
    multilayer_entropy()
    syracuse_preimage_growth()
    theoretical_summary()
