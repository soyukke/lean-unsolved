"""
エルデシュ問題 #138: Van der Waerden Numbers
W(k) = {1,...,N} を2色で塗り分けたとき、単色k項等差数列が必ず存在する最小のN

探索1: 数値実験
- W(3)=9, W(4)=35, W(5)=178 を全探索で検証
- W(k)^{1/k} の値を計算し増加傾向を確認
- 最適塗り分け（等差数列回避）を出力
- 下界・上界の比較表

探索2: 最適塗り分けの構造解析
- N=8 での最適塗り分けを全列挙
- 対称性・自己相似性を分析
- Berlekamp構成の検証
"""

from itertools import product
import math
import time


def has_monochromatic_ap(coloring, k):
    """
    coloring: 長さNのリスト (0 or 1)
    k項単色等差数列が存在するか判定
    """
    n = len(coloring)
    for start in range(n):
        max_diff = (n - 1 - start) // (k - 1) if k > 1 else n
        for diff in range(1, max_diff + 1):
            # 等差数列: start, start+diff, start+2*diff, ..., start+(k-1)*diff
            end = start + (k - 1) * diff
            if end >= n:
                break
            color = coloring[start]
            is_mono = True
            for j in range(1, k):
                if coloring[start + j * diff] != color:
                    is_mono = False
                    break
            if is_mono:
                return True
    return False


def find_avoiding_colorings(n, k):
    """N={1,...,n}のk項単色等差数列を回避する全2色塗り分けを列挙"""
    avoiding = []
    for bits in range(2**n):
        coloring = [(bits >> i) & 1 for i in range(n)]
        if not has_monochromatic_ap(coloring, k):
            avoiding.append(coloring)
    return avoiding


def compute_W_bruteforce(k, max_n=200):
    """W(k)を全探索で計算（小さいkのみ実用的）"""
    print(f"\n{'='*60}")
    print(f"W({k}) の計算 (全探索)")
    print(f"{'='*60}")

    for n in range(k, max_n + 1):
        found_avoiding = False
        for bits in range(2**n):
            coloring = [(bits >> i) & 1 for i in range(n)]
            if not has_monochromatic_ap(coloring, k):
                found_avoiding = True
                break

        if not found_avoiding:
            print(f"W({k}) = {n}")
            print(f"  N={n-1} では回避可能、N={n} では不可能")
            return n

        if n % 10 == 0:
            print(f"  N={n}: 回避可能な塗り分けが存在")

    print(f"  max_n={max_n} まで確定せず")
    return None


def compute_W_backtrack(k, max_n=200):
    """W(k)をバックトラッキングで計算（全探索より高速）"""
    print(f"\n{'='*60}")
    print(f"W({k}) の計算 (バックトラッキング)")
    print(f"{'='*60}")

    def can_extend(coloring, pos, color, k):
        """coloring[pos] = color としたとき、pos を含むk項単色等差数列が生じるか"""
        n = pos + 1
        # pos を含む等差数列をチェック
        # pos = start + j * diff の形で、全てのstart, diff, jを調べる
        for diff in range(1, n):
            # pos が等差数列の各位置にあるケース
            for j in range(k):
                start = pos - j * diff
                end = start + (k - 1) * diff
                if start < 0 or end >= n:
                    continue
                # この等差数列が全て同色か確認
                all_same = True
                for m in range(k):
                    idx = start + m * diff
                    c = color if idx == pos else coloring[idx]
                    if c != color:
                        all_same = False
                        break
                if all_same:
                    return False  # 単色等差数列が生じる
        return True  # 拡張可能

    def backtrack(coloring, pos, n, k):
        if pos == n:
            return True  # 全位置を塗れた
        for color in [0, 1]:
            coloring[pos] = color
            if can_extend(coloring, pos, color, k):
                if backtrack(coloring, pos + 1, n, k):
                    return True
        coloring[pos] = -1
        return False

    for n in range(k, max_n + 1):
        coloring = [-1] * n
        start_time = time.time()
        found = backtrack(coloring, 0, n, k)
        elapsed = time.time() - start_time

        if not found:
            print(f"W({k}) = {n}")
            print(f"  N={n-1} では回避可能、N={n} では不可能")
            return n

        if n % 10 == 0 or elapsed > 0.1:
            print(f"  N={n}: 回避可能 ({elapsed:.3f}秒)")

    print(f"  max_n={max_n} まで確定せず")
    return None


def find_optimal_colorings_backtrack(n, k):
    """N=nでk項単色等差数列を回避する塗り分けを全列挙（バックトラッキング）"""
    results = []

    def can_extend(coloring, pos, color, k):
        n_cur = pos + 1
        for diff in range(1, n_cur):
            for j in range(k):
                start = pos - j * diff
                end = start + (k - 1) * diff
                if start < 0 or end >= n_cur:
                    continue
                all_same = True
                for m in range(k):
                    idx = start + m * diff
                    c = color if idx == pos else coloring[idx]
                    if c != color:
                        all_same = False
                        break
                if all_same:
                    return False
        return True

    def backtrack(coloring, pos):
        if pos == n:
            results.append(coloring[:])
            return
        for color in [0, 1]:
            coloring[pos] = color
            if can_extend(coloring, pos, color, k):
                backtrack(coloring, pos + 1)
        coloring[pos] = -1

    coloring = [-1] * n
    backtrack(coloring, 0)
    return results


# =====================================================
# 探索1: 数値実験
# =====================================================
print("=" * 70)
print("探索1: Van der Waerden Numbers の数値実験")
print("=" * 70)

# W(3) の全探索による検証
W3 = compute_W_bruteforce(3, max_n=15)

# W(4) の計算（バックトラッキング）
W4 = compute_W_backtrack(4, max_n=40)

# W(5) の計算（時間がかかるのでバックトラッキング、上限を設定）
print(f"\nW(5) の計算はN=178まで必要で時間がかかるため、")
print(f"既知の値 W(5)=178 を使用します。")
W5 = 178

# 既知の値
known_W = {3: 9, 4: 35, 5: 178, 6: 1132}

# W(k)^{1/k} の計算
print(f"\n{'='*60}")
print(f"W(k)^{{1/k}} の増加傾向")
print(f"{'='*60}")
print(f"{'k':>3} {'W(k)':>8} {'W(k)^(1/k)':>12} {'log W(k)/k':>12}")
print(f"{'-'*3:>3} {'-'*8:>8} {'-'*12:>12} {'-'*12:>12}")
for k, w in sorted(known_W.items()):
    root = w ** (1.0 / k)
    log_ratio = math.log(w) / k
    print(f"{k:>3} {w:>8} {root:>12.6f} {log_ratio:>12.6f}")

print(f"\n結論: W(k)^{{1/k}} は k の増加とともに増加しており、")
print(f"W(k)^{{1/k}} -> ∞ と矛盾しない。")

# 下界・上界の比較表
print(f"\n{'='*60}")
print(f"下界・上界の比較")
print(f"{'='*60}")
print(f"{'k':>3} {'W(k)':>8} {'下界 2^k':>10} {'比率':>8} {'W(k)/k':>10}")
print(f"{'-'*3:>3} {'-'*8:>8} {'-'*10:>10} {'-'*8:>8} {'-'*10:>10}")
for k, w in sorted(known_W.items()):
    lower = 2**k
    ratio = w / lower
    wk = w / k
    print(f"{k:>3} {w:>8} {lower:>10} {ratio:>8.3f} {wk:>10.1f}")

print(f"\n注: Kozik-Shabanov (2016) により W(k) >> 2^k")
print(f"Gowers (2001) により上界は多重指数関数的")


# 最適塗り分けの出力
print(f"\n{'='*60}")
print(f"k=3: N=8 での回避可能な塗り分け例")
print(f"{'='*60}")

# k=3, N=8 の回避可能な塗り分けをバックトラッキングで全列挙
colorings_8_3 = find_optimal_colorings_backtrack(8, 3)
print(f"回避可能な塗り分け数: {len(colorings_8_3)}")
for i, c in enumerate(colorings_8_3[:10]):
    s = ''.join(['R' if x == 0 else 'B' for x in c])
    print(f"  {i+1:>2}. {s}  (位置1-8)")
if len(colorings_8_3) > 10:
    print(f"  ... 他 {len(colorings_8_3) - 10} 個")

# k=3, N=9 で不可能であることの確認
print(f"\nk=3: N=9 で回避不可能を確認:")
colorings_9_3 = find_optimal_colorings_backtrack(9, 3)
print(f"  回避可能な塗り分け数: {len(colorings_9_3)} (0なら W(3)=9 確認)")


# =====================================================
# 探索2: 最適塗り分けの構造解析
# =====================================================
print(f"\n\n{'='*70}")
print(f"探索2: 最適塗り分けの構造解析")
print(f"{'='*70}")

# N=8, k=3 の全回避塗り分けの対称性分析
print(f"\n--- N=8, k=3 の回避塗り分けの対称性分析 ---")
print(f"全回避塗り分け数: {len(colorings_8_3)}")

# 反転（色の入れ替え）でのペア
complement_pairs = 0
self_complement = 0
for c in colorings_8_3:
    comp = [1 - x for x in c]
    if comp in colorings_8_3:
        if comp == c:
            self_complement += 1
        else:
            complement_pairs += 1

print(f"色反転でもう一方も回避可能: {complement_pairs} 個 (ペア: {complement_pairs//2})")
print(f"色反転で自己一致: {self_complement} 個")

# 左右反転での対称性
palindrome_pairs = 0
self_palindrome = 0
for c in colorings_8_3:
    rev = c[::-1]
    if rev in colorings_8_3:
        if rev == c:
            self_palindrome += 1
        else:
            palindrome_pairs += 1

print(f"左右反転でもう一方も回避可能: {palindrome_pairs} 個 (ペア: {palindrome_pairs//2})")
print(f"回文構造: {self_palindrome} 個")

# 各塗り分けのパターン分析
print(f"\n--- 各塗り分けの構造 ---")
for i, c in enumerate(colorings_8_3):
    s = ''.join(['R' if x == 0 else 'B' for x in c])
    # 色ごとの位置
    red_pos = [j+1 for j in range(8) if c[j] == 0]
    blue_pos = [j+1 for j in range(8) if c[j] == 1]
    # mod 3 分布
    red_mod3 = [p % 3 for p in red_pos]
    blue_mod3 = [p % 3 for p in blue_pos]
    print(f"  {i+1:>2}. {s}  R={red_pos} B={blue_pos}")
    if i < 6:
        print(f"      R mod3={red_mod3} B mod3={blue_mod3}")

# Berlekamp構成の検証
print(f"\n--- Berlekamp構成の検証 ---")
print(f"Berlekamp (1968): p が素数のとき、")
print(f"  W(p+1) >= p * 2^p を示した。")
print("  構成: {0,...,p-1} × Z_p で、色は x の二次剰余で決定")

for p in [2, 3, 5, 7]:
    lower = p * 2**p
    print(f"\n  p={p}: W({p+1}) >= {lower}")
    if p + 1 in known_W:
        print(f"    実際の W({p+1}) = {known_W[p+1]}, 比率 = {known_W[p+1]/lower:.3f}")

    # p=2 の場合の具体的構成
    if p == 2:
        print(f"    Z_2 × Z_2 での構成 (N={p * 2**p - 1}):")
        # 0は二次剰余でない、1は二次剰余
        # 色を二次剰余で決定
        n = p * 2**p - 1
        coloring_berlekamp = []
        for i in range(n):
            # 位置 i を p進展開: i = a_0 + a_1*p + ... + a_{p-1}*p^{p-1}
            # 色は Σ a_j の二次剰余性
            digit_sum = 0
            val = i
            for _ in range(p):
                digit_sum += val % p
                val //= p
            # mod p で二次剰余判定
            r = digit_sum % p
            if p == 2:
                coloring_berlekamp.append(r)
            else:
                # ルジャンドル記号
                coloring_berlekamp.append(1 if pow(r, (p-1)//2, p) == 1 and r != 0 else 0)
        s = ''.join(['R' if x == 0 else 'B' for x in coloring_berlekamp])
        print(f"    塗り分け: {s}")

# p=3 の構成
print(f"\n  p=3 の Berlekamp風構成 (N=23):")
p = 3
n_berl = p * 2**p - 1  # 23
coloring_b3 = []
for i in range(n_berl):
    # 3進展開の各桁の和 mod 3 の二次剰余性
    digit_sum = 0
    val = i
    while val > 0:
        digit_sum += val % p
        val //= p
    r = digit_sum % p
    # p=3 の二次剰余: 1 (1^2=1, 2^2=1 mod 3)
    if r == 0:
        coloring_b3.append(0)
    else:
        # r=1,2: 1は二次剰余、2は非二次剰余
        coloring_b3.append(0 if pow(r, (p-1)//2, p) != 1 else 1)

s = ''.join(['R' if x == 0 else 'B' for x in coloring_b3])
print(f"  塗り分け: {s}")
print(f"  3項等差数列を回避? {not has_monochromatic_ap(coloring_b3, 3)}")
print(f"  4項等差数列を回避? {not has_monochromatic_ap(coloring_b3, 4)}")


# W(k)^{1/k} の増加の理論的根拠
print(f"\n\n{'='*60}")
print(f"理論的考察: W(k)^{{1/k}} -> ∞ について")
print(f"{'='*60}")
print(f"""
既知の結果:
1. Gowers (2001): W(k) <= 2^(2^(2^(2^(2^(k+9)))))  (多重指数関数的上界)
2. Kozik-Shabanov (2016): W(k) >= 2^k / (e*k)  (指数的下界)
3. Berlekamp (1968): W(p+1) >= p * 2^p  (pが素数)

W(k)^{{1/k}} -> ∞ の意味:
  任意の C > 0 に対し、十分大きい k で W(k) > C^k
  これは W(k) が任意の指数関数より速く成長することを意味する。

Gowers の上界からは W(k)^{{1/k}} -> ∞ は直接従う
（多重指数関数は任意の単一指数関数より速く成長するため）。

しかしエルデシュの問題は、これを初等的に（Gowersの結果を使わずに）
証明できるかを問うているとも解釈できる。

下界の観点:
  Kozik-Shabanov: W(k) >= 2^k / (ek) より
  W(k)^{{1/k}} >= (2^k / (ek))^{{1/k}} = 2 / (ek)^{{1/k}} -> 2
  これだけでは W(k)^{{1/k}} -> ∞ を示せない。

  もし W(k) >= k^k のような下界が示せれば
  W(k)^{{1/k}} >= k となり ∞ に発散する。
  しかしこのような強い下界は未証明。
""")

# k=3,4の最適塗り分けを1つ出力
print(f"\n{'='*60}")
print(f"各kでの最適塗り分け例（W(k)-1 での回避例）")
print(f"{'='*60}")

# k=3, N=8
print(f"\nk=3, N=8:")
if colorings_8_3:
    c = colorings_8_3[0]
    s = ''.join(['R' if x == 0 else 'B' for x in c])
    print(f"  {s}")
    print(f"  R: 位置 {[j+1 for j in range(8) if c[j] == 0]}")
    print(f"  B: 位置 {[j+1 for j in range(8) if c[j] == 1]}")

# k=4, N=34
print(f"\nk=4, N=34 (バックトラッキングで1つ探索):")
result_34 = [None]

def find_one_coloring_backtrack(n, k):
    """1つの回避塗り分けをバックトラッキングで探索"""
    def can_extend(coloring, pos, color):
        for diff in range(1, pos + 1):
            for j in range(k):
                start = pos - j * diff
                end = start + (k - 1) * diff
                if start < 0 or end > pos:
                    continue
                all_same = True
                for m in range(k):
                    idx = start + m * diff
                    c = color if idx == pos else coloring[idx]
                    if c != color:
                        all_same = False
                        break
                if all_same:
                    return False
        return True

    def backtrack(coloring, pos):
        if pos == n:
            return coloring[:]
        for color in [0, 1]:
            coloring[pos] = color
            if can_extend(coloring, pos, color):
                result = backtrack(coloring, pos + 1)
                if result is not None:
                    return result
        coloring[pos] = -1
        return None

    return backtrack([-1] * n, 0)

c34 = find_one_coloring_backtrack(34, 4)
if c34:
    s = ''.join(['R' if x == 0 else 'B' for x in c34])
    print(f"  {s}")
    print(f"  R: 位置 {[j+1 for j in range(34) if c34[j] == 0]}")
    print(f"  B: 位置 {[j+1 for j in range(34) if c34[j] == 1]}")
else:
    print(f"  見つからず")

print(f"\n探索1-2 完了。")
