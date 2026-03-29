#!/usr/bin/env python3
"""
補足解析: 逆像が成長しない点の構造と、エントロピー階層の関係
"""

import math
import random
from collections import Counter

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def collatz_preimages(x, max_val=10**15):
    pre = []
    pre.append(2 * x)
    if (2 * x - 1) % 3 == 0:
        y = (2 * x - 1) // 3
        if y > 0 and y % 2 == 1:
            pre.append(y)
    return [p for p in pre if p <= max_val]

# ============================================================
# なぜ始点3, 27で逆像が成長しないか?
# ============================================================

def analyze_no_growth_points():
    """逆像が成長しない点の特徴分析"""
    print("=" * 70)
    print("逆像が成長しない点の構造分析")
    print("=" * 70)

    max_val = 10**10

    # 多くの始点で30ステップ後の逆像サイズを計算
    no_growth = []
    growth = []

    for start in range(1, 200):
        current_set = {start}
        for n in range(30):
            next_set = set()
            for x in current_set:
                for p in collatz_preimages(x, max_val):
                    next_set.add(p)
            current_set = next_set
            if len(current_set) == 0:
                break

        size = len(current_set)
        if size <= 1:
            no_growth.append(start)
        else:
            growth.append((start, size))

    print(f"\n  逆像が成長しない点 (30ステップ後 |T^-30| <= 1):")
    print(f"    {no_growth[:50]}")

    print(f"\n  特徴分析:")
    for x in no_growth[:20]:
        # xの逆像の構造
        pre = collatz_preimages(x, max_val)
        print(f"    x={x:4d}: mod3={x%3}, mod6={x%6}, "
              f"逆像={pre}, 逆像数={len(pre)}")

    # 3の倍数の奇数は逆像が1個のみ
    print(f"\n  観察: 逆像が成長しない点は以下のいずれか:")
    print(f"    - 3の倍数 (mod 3 = 0)")
    print(f"    - 逆像がすべて3の倍数に落ちる数")

    # チェーンの追跡
    print(f"\n  始点3の逆像チェーン:")
    x = 3
    for n in range(10):
        pre = collatz_preimages(x, max_val)
        print(f"    T^{{-{n}}}(3): x={x}, 逆像={pre}, mod3={[p%3 for p in pre]}")
        if pre:
            x = pre[0]  # 2x の方を追跡
        else:
            break

# ============================================================
# エントロピー階層の数値的関係
# ============================================================

def entropy_hierarchy():
    """エントロピー値の階層構造"""
    print("\n" + "=" * 70)
    print("エントロピー階層と既知定数の関係")
    print("=" * 70)

    phi = (1 + math.sqrt(5)) / 2

    # 各エントロピー値
    h_metric = 0.0  # メトリックエントロピー (予想が真なら)
    h_preimage = math.log(4/3)  # 逆像成長率
    h_parity = math.log(phi)  # パリティ記号力学
    h_binary = math.log(2)  # 2進シフト
    lyap_collatz = -0.094  # コラッツリアプノフ指数
    lyap_syracuse = -0.283  # Syracuseリアプノフ指数
    drift = -0.415  # ドリフト (既知)
    h_log32 = math.log(3) / math.log(2)  # 候補だった値

    print(f"\n  エントロピー階層 (小さい順):")
    print(f"  {'='*50}")
    print(f"  h_metric        = {h_metric:.6f}  (不変測度のエントロピー)")
    print(f"  h_preimage      = {h_preimage:.6f}  (逆像成長率 = log(4/3))")
    print(f"  h_parity        = {h_parity:.6f}  (パリティ記号力学 = log(phi))")
    print(f"  h_binary_shift  = {h_binary:.6f}  (2進シフト = log(2))")
    print(f"  log(3)          = {math.log(3):.6f}  (3x+1の拡大率)")
    print(f"  log_2(3)        = {h_log32:.6f}  (候補値、非エントロピー)")

    # 関係式
    print(f"\n  注目すべき関係式:")
    print(f"  h_preimage = log(4/3) = 2*log(2) - log(3) = {2*math.log(2) - math.log(3):.6f}")
    print(f"  h_parity   = log(phi) = {math.log(phi):.6f}")
    print(f"  h_preimage / h_binary = log(4/3)/log(2) = {math.log(4/3)/math.log(2):.6f}")
    print(f"  h_parity / h_binary   = log(phi)/log(2) = {math.log(phi)/math.log(2):.6f}")

    # log(4/3) と他の定数の関係
    print(f"\n  log(4/3)の算術的意味:")
    print(f"    log(4/3) = log(4) - log(3)")
    print(f"             = 2*log(2) - log(3)")
    print(f"    これは「2倍操作2回 vs 3倍操作1回」の差")
    print(f"    コラッツの本質: 2^2 = 4 > 3 なので正だが小さい")
    print(f"")
    print(f"  リアプノフ指数との関連:")
    print(f"    lambda_Syracuse = log(3) - <v2>*log(2)")
    print(f"                    = log(3) - 2*log(2) (v2の平均が2の場合)")
    print(f"                    = -log(4/3)")
    print(f"    実測値: {lyap_syracuse:.4f}, -log(4/3) = {-math.log(4/3):.4f}")
    print(f"    注: 概ね一致! (差は v2の平均が厳密に2でないため)")

    # v2の精密平均
    print(f"\n  v2(3x+1)の精密平均:")
    total_v2 = 0
    count = 0
    for _ in range(100000):
        n = random.randint(3, 10000000)
        if n % 2 == 0:
            n += 1
        m = 3 * n + 1
        v = 0
        while m % 2 == 0:
            m >>= 1
            v += 1
        total_v2 += v
        count += 1
    avg_v2 = total_v2 / count
    print(f"    <v2> = {avg_v2:.6f}")
    print(f"    理論値: sum(k/2^k) = 2.000 (幾何級数)")
    print(f"    lambda_exact = log(3) - {avg_v2:.4f}*log(2) = {math.log(3) - avg_v2*math.log(2):.6f}")

    # 対称性: h_preimage + |lambda| ≈ ?
    print(f"\n  発見的関係:")
    print(f"    h_preimage + |lambda_Syracuse| = {h_preimage + abs(lyap_syracuse):.4f}")
    print(f"    h_preimage + |lambda_Collatz|  = {h_preimage + abs(lyap_collatz):.4f}")
    print(f"    log(3/2) = {math.log(3/2):.4f}")
    print(f"    h_preimage ≈ -lambda_Syracuse (符号反転の関係)")

# ============================================================
# Syracuse写像のより正確な逆像成長率
# ============================================================

def syracuse_precise_growth():
    """Syracuse写像の逆像成長率がどの値に収束するか"""
    print("\n" + "=" * 70)
    print("Syracuse写像の逆像成長率の精密推定")
    print("=" * 70)

    def syracuse(n):
        m = 3 * n + 1
        while m % 2 == 0:
            m >>= 1
        return m

    def syracuse_preimages(x, max_val=10**12):
        pre = []
        for k in range(1, 50):
            val = x * (2 ** k) - 1
            if val % 3 == 0:
                y = val // 3
                if y > 0 and y % 2 == 1 and y <= max_val:
                    pre.append(y)
            if x * (2 ** k) > max_val * 3:
                break
        return pre

    # 始点1の逆像ツリー
    max_val = 10**10
    current_set = {1}
    step_growths = []

    print(f"\n  始点: 1")
    for n in range(1, 25):
        next_set = set()
        for x in current_set:
            for p in syracuse_preimages(x, max_val):
                next_set.add(p)
        prev_size = len(current_set)
        current_set = next_set
        size = len(current_set)

        if prev_size > 0 and size > 0:
            growth = math.log(size / prev_size)
            step_growths.append(growth)
        h_est = math.log(size) / n if size > 0 else 0

        print(f"  n={n:3d}: |T_S^{{-n}}| = {size:10d}, "
              f"(1/n)log = {h_est:.6f}, "
              f"step_growth = {growth:.4f}")

        if size > 2000000:
            print(f"  (打ち切り)")
            break

    if len(step_growths) > 3:
        recent = step_growths[-3:]
        avg = sum(recent) / len(recent)
        print(f"\n  直近3ステップの平均成長率: {avg:.6f}")
        print(f"  比較: log(2) = {math.log(2):.6f}")
        print(f"  (Syracuse逆像は1ステップで複数のkが可能)")

    # 平均逆像数の計算
    print(f"\n  Syracuse写像の平均逆像数:")
    total_pre = 0
    count = 0
    for x in range(1, 100000, 2):  # 奇数のみ
        pre = syracuse_preimages(x, 10**15)
        total_pre += len(pre)
        count += 1
    avg_pre = total_pre / count
    print(f"    平均逆像数 = {avg_pre:.4f}")
    print(f"    log(平均逆像数) = {math.log(avg_pre):.4f}")

    # 各kについての寄与
    print(f"\n  k別の逆像存在確率:")
    for k in range(1, 20):
        has_pre = 0
        for x in range(1, 50000, 2):
            val = x * (2 ** k) - 1
            if val % 3 == 0:
                y = val // 3
                if y > 0 and y % 2 == 1:
                    has_pre += 1
        total = 25000
        prob = has_pre / total
        print(f"    k={k:2d}: P(逆像存在) = {prob:.4f} (理論: 1/3 * 1/2 for k>=2)")

# ============================================================
# メイン
# ============================================================

if __name__ == "__main__":
    random.seed(42)

    analyze_no_growth_points()
    entropy_hierarchy()
    syracuse_precise_growth()
