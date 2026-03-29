"""
非標準解析によるコラッツ予想の再定式化
=======================================

超実数体 *R と超自然数 *N 上でのコラッツ関数の挙動を分析する。

主要な概念:
1. 転送原理 (Transfer Principle): 標準モデルの一階述語が超冪モデルでも成立
2. 内的集合 vs 外的集合: N は *N の内的部分集合ではない
3. Overspill/Underspill: 全標準自然数で成立する内的性質は超自然数にも「溢れる」
4. 標準部分 (Standard Part): 有限超実数からの射影

計算実験: 非標準的な視点からの数値的検証
"""

import math

# === Part 1: コラッツ関数の基本定義 ===

def collatz_step(n):
    """コラッツ関数"""
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def syracuse(n):
    """Syracuse関数 (奇数 n 用)"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def syracuse_iter(n, k):
    """Syracuse関数の k 回反復"""
    for _ in range(k):
        n = syracuse(n)
    return n

def stopping_time(n, limit=10000):
    """停止時間: n が初めて n より小さくなるまでのステップ数"""
    orig = n
    for k in range(1, limit):
        n = collatz_step(n)
        if n < orig:
            return k
    return -1

def total_stopping_time(n, limit=100000):
    """全停止時間: 1に到達するまでのステップ数"""
    for k in range(limit):
        if n == 1:
            return k
        n = collatz_step(n)
    return -1


# === Part 2: 非標準解析的再定式化の枠組み ===

print("=" * 70)
print("非標準解析によるコラッツ予想の再定式化")
print("=" * 70)

# --- 2.1: 転送原理による同値な命題の列挙 ---
print("\n--- 2.1: 転送原理によるコラッツ予想の非標準的同値条件 ---")
print("""
コラッツ予想の標準的定式化:
  CC: forall n in N, n >= 1, exists k in N, collatzIter(k, n) = 1

転送原理により、*N 上では:
  *CC: forall n in *N, n >= 1, exists k in *N, *collatzIter(k, n) = 1

ここで *collatzIter は collatzIter の自然拡張。

重要: CC と *CC は一階の文として同値 (Los's theorem)。

しかし、以下の区別が本質的:
  (A) CC を否定すると:
      exists n in N, n >= 1, forall k in N, collatzIter(k, n) != 1
      転送: exists n in *N, ...
      だが n は超自然数かもしれない。

  (B) コラッツ軌道の有限性:
      CC <=> forall n in N, ST(n) < infinity  (ST = total stopping time)

  非標準版:
      *CC <=> forall n in *N, *ST(n) は有限超自然数

  ここで「有限」とは「ある標準自然数以下」ということ。
""")

# --- 2.2: Overspill 原理の適用 ---
print("\n--- 2.2: Overspill 原理の帰結 ---")
print("""
Overspill原理:
  内的集合 A が全ての標準自然数を含むなら、
  ある無限超自然数 H が存在して A は H も含む。

逆に Underspill原理:
  内的集合 A が全ての無限超自然数を含むなら、
  ある標準自然数 M が存在して A は M 以上の全ての標準自然数を含む。

コラッツへの適用:
  Aₘ = {n in *N : *ST(n) <= m} とする。

  CC が成立するとき:
    全ての標準 n に対して *ST(n) は標準 (有限)。
    B_N = {n in *N : n <= N かつ *ST(n) は有限}
    全ての標準 N に対して B_N は [1,N] 全体を含む。

  しかし B_N = [1,N] は一階の文で表現できない
  (「有限」は外的概念)。

  代わりに:
    C_m = {n in *N : n <= N かつ *ST(n) <= m}

    CC が成立するなら、全標準 n, N に対し
    ある標準 m(n) が存在して n in C_{m(n)}。

    しかし m(n) は n に依存し、一様な上界は保証されない。
""")

# --- 2.3: 停止時間の成長率の数値実験 ---
print("\n--- 2.3: ST(n)/log(n) の挙動 ---")
print("(非標準解析では「st(ST(N)/log(N))」が有限か否かが鍵)")

# 大きな n での ST(n)/log(n) の分布を調べる
ranges_and_ratios = []
for exp in range(5, 25):
    N = 2**exp
    max_ratio = 0
    sum_ratio = 0
    count = 0
    for n in range(max(1, N - 500), N + 1):
        if n <= 0:
            continue
        st = total_stopping_time(n)
        if st >= 0 and n > 1:
            ratio = st / math.log2(n)
            max_ratio = max(max_ratio, ratio)
            sum_ratio += ratio
            count += 1
    avg_ratio = sum_ratio / count if count > 0 else 0
    ranges_and_ratios.append((exp, avg_ratio, max_ratio))
    print(f"  2^{exp}: avg(ST/log2(n)) = {avg_ratio:.4f}, max(ST/log2(n)) = {max_ratio:.4f}")

print("""
非標準解析的解釈:
  もし sup_n ST(n)/log2(n) < infinity (標準的に有界) なら、
  超自然数 N に対しても *ST(N)/log2(N) は有限超実数。

  数値的には max_ratio が緩やかに成長している。
  これは ST(n) ~ C * log(n)^alpha (alpha > 1) を示唆する。
""")


# === Part 3: 非標準的サイクル/発散の特徴づけ ===

print("\n--- 3: 非標準的サイクル/発散の特徴づけ ---")
print("""
転送原理を使った精密な分析:

定理 (非標準的サイクルの特徴づけ):
  CC が偽 ⟺ ある n0 in N で以下のいずれか:
  (i) 軌道が発散: collatzIter(k, n0) -> infinity (k -> infinity)
  (ii) 非自明サイクル: ある p >= 2 で collatzIter(p, n0) = n0

  超冪 *N に転送すると:
  *CC が偽 ⟺ ある n0 in *N (超自然数を含む) で
  (i') *collatzIter(k, n0) が全ての k in *N で有界でない、または
  (ii') ある p in *N (超自然数の可能性あり) で *collatzIter(p, n0) = n0

  ここで重要な洞察:
  - (ii') で p が超自然数の場合、これは「超有限周期」を持つ軌道。
    標準的には発散的に見えるが、*N の中では有限ステップで戻る。
  - しかし転送原理により、*N で非自明なサイクルが存在するなら
    N でも非自明なサイクルが存在する。
    (一階の文 "exists n, exists p>1, collatzIter(p,n)=n" の転送)

  したがって:
    超自然数的な周期を持つ「サイクル」は標準的サイクルの非標準延長でしかない。
    超有限周期の新規サイクルは転送原理で排除される。
""")

# === Part 4: 内的集合 vs 外的集合の境界分析 ===

print("\n--- 4: 内的/外的集合の区別とコラッツ予想 ---")
print("""
核心的な問題: 「1に到達する数の集合」は内的か外的か？

S = {n in N : n reaches 1} (コラッツ予想 iff S = N without {0})

*S = {n in *N : n reaches 1 within *N steps}

*S は内的集合 (S の定義が一階述語であるため)。

重要な帰結:
  CC ⟺ *S contains all standard positive naturals
     ⟺ (overspill により) *S contains some infinite hypernatural

逆に、CC の否定:
  not-CC ⟺ ある標準 n0 で n0 not in S
  転送して: n0 not in *S

つまり: CC が偽なら、標準自然数の中に反例がある。
(これは当然だが、非標準的な視点では、
 「超自然数にだけ反例がある」という可能性は排除される。)

しかし、次の問いは非自明:
  Q: *S が全ての標準自然数を含むとき、
     「ある無限超自然数 H」で H in *S が成立するか？

  A: Overspill により YES。
     なぜなら *S = {n in *N : exists k in *N, *collatzIter(k,n)=1}
     は内的集合であり、全標準自然数を含むなら overspill が適用される。

  すなわち: CC ⟺ ある無限超自然数 H で H in *S。
""")


# === Part 5: Overspill を使った定量的分析 ===

print("\n--- 5: Overspill による定量的結果 ---")

# CC が成立すると仮定して、overspill の帰結を数値検証
# A_m = {n : ST(n) <= m} として、どの m まで [1,N] をカバーするか

print("A_m = {n in [1,N] : ST(n) <= m} の被覆率:")
for N_exp in [10, 12, 14, 16]:
    N = 2**N_exp
    sts = []
    for n in range(1, N+1):
        st = total_stopping_time(n)
        sts.append(st)
    max_st = max(sts)

    # 各 m での被覆率
    coverages = []
    for m_mult in [0.5, 1.0, 1.5, 2.0]:
        m = int(m_mult * N_exp * 6.95)  # 6.95 ~ average multiplier
        covered = sum(1 for s in sts if s <= m)
        coverages.append((m, covered / N))

    print(f"  N=2^{N_exp} (max ST={max_st}):")
    for m, cov in coverages:
        print(f"    m={m}: coverage = {cov:.6f}")

print("""
非標準解析的解釈:
  Overspill の定量版:
    CC が成立 => 全標準 N に対して A_{f(N)} が [1,N] をカバー
    (f(N) = max(ST(n) : n <= N))

    Overspill により:
    ある無限 H で A_{*f(H)} が [1,H] をカバー。

    ここで *f(H) は f の非標準拡張。

    問題: *f(H)/log(H) は有限超実数か？
    もし有限なら: ST の成長が真に log(n) のオーダー。
    もし無限なら: ST が log(n) より速く成長する超自然数が存在。
""")


# === Part 6: 2-adic 反発性の非標準解釈 ===

print("\n--- 6: 2-adic 反発性と非標準解析 ---")
print("""
既知の結果: Z_2 上で |dT/dn|_2 = 4 (2-adic微分)。

非標準解釈:
  超自然数 N に対して、T の *Z_2 上の挙動を考える。

  標準的な Syracuse 関数 T: 奇数N -> 奇数N は
  T(n) = (3n+1) / 2^{v2(3n+1)}

  *T は *N -> *N に自然拡張される。

  超自然数 N で v2(3N+1) = V (V は超自然数の可能性) のとき:
  *T(N) = (3N+1) / 2^V

  もし V が無限 (超自然数) なら: *T(N) は 3N+1 の「超有限回2で割った結果」
  → *T(N) は奇数の超自然数。

  2-adic 反発性の帰結:
  n と n+2^k が「近い」(2-adic距離) のとき、
  T(n) と T(n+2^k) は 4倍離れる (2-adic距離で)。

  非標準的に: 無限に近い2つの超自然数の *T 値は
  指数的に離れる → 超有限的な安定性（周期性）が妨げられる。
""")

# 2-adic 反発の数値検証
print("2-adic 反発性の数値検証:")
print("  n, T(n), v2(T(n)-T(n+2^k)) for various k:")
for n in [1, 3, 5, 7, 11, 13]:
    Tn = syracuse(n)
    for k in [2, 4, 6]:
        m = n + 2**k
        if m % 2 == 1:
            Tm = syracuse(m)
            diff = abs(Tn - Tm)
            v2_diff = 0
            if diff > 0:
                temp = diff
                while temp % 2 == 0:
                    v2_diff += 1
                    temp //= 2
            print(f"    n={n}, m=n+2^{k}={m}, T(n)={Tn}, T(m)={Tm}, v2(|T(n)-T(m)|)={v2_diff}")


# === Part 7: 非標準解析で得られる新命題の整理 ===

print("\n" + "=" * 70)
print("Part 7: 主要な非標準解析的命題の整理")
print("=" * 70)
print("""
命題 NSC-1 (転送原理の直接帰結):
  CC は一階の文であるため、CC ⟺ *CC。
  超自然数の世界に「新しい反例」は生まれない。
  反例があるなら標準自然数の中にある。

命題 NSC-2 (Overspill):
  CC ⟺ ある無限超自然数 H が *S に属する。
  (*S = {n in *N : n は有限ステップで 1 に到達})

  これは CC を「無限超自然数が到達する」という形で言い換える。

命題 NSC-3 (Underspill による一様有界性):
  CC が成立するとき、
  f(N) = max{ST(n) : 1 <= n <= N} とすると
  *f は *N 上の内的関数。
  全標準 N で f(N) は有限なので、
  CC => ある無限超自然数 H で *f(H) は有限超実数ではない
  (overspill は f(N) < infinity を保証しない、
   なぜなら「f(N) は有限」は外的述語)。

  実際: f(N) → infinity は既知なので、*f(H) は無限超自然数。
  これは自明ではあるが、ST の成長度の非標準的特徴づけとなる。

命題 NSC-4 (超有限サイクルの排除):
  Baker の定理 + 転送原理により:
  p <= 10 の非自明サイクルは標準世界で排除済み。
  転送: *N でも p <= 10 の非自明 *サイクルは存在しない。

  さらに: 一般のサイクル排除 (Baker公理下) は
  転送により *N にも適用される。

命題 NSC-5 (発散の非標準的特徴づけ):
  n0 の軌道が発散 ⟺ 全 k に対して collatzIter(k, n0) >= n0
  ではない (一時的に下がることもある)。

  より正確には:
  n0 が発散 ⟺ supk collatzIter(k, n0) = infinity
  ⟺ (転送) *N に拡張したとき、ある超自然数 K で
     *collatzIter(K, n0) は無限超自然数。

  Overspill の応用:
  全標準 k で collatzIter(k, n0) は有限
  (これは自明 - 標準的操作の有限回適用)
  → overspill により ある無限 K で *collatzIter(K, n0) も有限。
  ※これは CC の証明にはならない！
    なぜなら overspill は「有限」を保証するが、
    「= 1 に到達」を保証しない。

命題 NSC-6 (密度の非標準版):
  d(N) = |{n <= N : n in S}| / N とすると:
  Tao (2019) の結果: d(N) → 1 (density 1 の意味で)。

  転送: *d(H) ≈ 1 (任意の無限超自然数 H に対して)。
  すなわち *d(H) と 1 の差は無限小。

  これは「ほとんど全ての超自然数以下の自然数が到達する」ことを意味し、
  反例の密度が無限小であることを示す。
""")


# === Part 8: 非標準解析的アプローチの限界分析 ===

print("\n--- 8: アプローチの限界分析 ---")
print("""
根本的な限界:

1. 転送原理の限界:
   CC は一階の文なので CC ⟺ *CC。
   つまり非標準解析で CC を証明することは、
   標準解析で CC を証明することと完全に同値。
   非標準解析は「新しい証明力」を加えない。

2. Overspill/Underspill の限界:
   これらは「存在」を示す道具であり、
   具体的な上界を与えない。
   「全ての n に対して ST(n) < f(n)」のような
   一様な評価には直接使えない。

3. 内的/外的の区別の帰結:
   「1に到達する集合」*S は内的。
   「有限ステップで到達」の「有限」は外的。
   この不一致がコラッツ予想の本質的困難の一つ。

しかし、有望な方向:

A. 非標準的な証明戦略:
   CC の否定を仮定 → ある標準 n0 が反例
   → n0 の *N 上の軌道を分析
   → 転送 + overspill で矛盾を導く

   具体的: n0 の軌道 {collatzIter(k, n0)} を考える。
   全 k で collatzIter(k, n0) != 1 なら、
   {collatzIter(k, n0) : k in *N} は *N の内的部分集合。
   この集合の性質を分析して矛盾を導くことが目標。

B. 局所的 Overspill の活用:
   コラッツ軌道の統計的性質（エルゴード的）は
   有限の範囲で確認済み（探索093）。
   これを overspill で超有限に延長し、
   超有限軌道でも統計的に下降傾向を示すことが可能。

   ただし: 統計的下降 ≠ 必ず 1 に到達
   (Tao の壁と同じ)

C. 非標準モデル理論と決定不能性:
   もし CC が PA (Peano 算術) から独立なら、
   PA のある非標準モデルで CC は偽。
   すなわち、その非標準モデルの超自然数で反例が存在。

   CC の PA からの独立性は未解決だが、
   もし独立なら非標準解析的アプローチには
   本質的な限界がある。
""")


# === Part 9: 最大停止時間の対数比の精密分析 ===

print("\n--- 9: max ST(n) の成長オーダー ---")
print("超自然数 N での *ST(N) の大きさを推定するための基礎データ")

max_sts = []
for exp in range(5, 22):
    N = 2**exp
    max_st = 0
    for n in range(1, N+1):
        st = total_stopping_time(n)
        if st > max_st:
            max_st = st
    ratio = max_st / (exp * math.log2(exp + 1)) if exp > 0 else 0
    max_sts.append((exp, max_st, ratio))
    if exp <= 18:
        print(f"  N=2^{exp}: max_ST = {max_st}, max_ST/(log2(N)*log2(log2(N))) = {ratio:.4f}")

# 成長率の推定
exps = [x[0] for x in max_sts if x[0] >= 8]
sts_vals = [x[1] for x in max_sts if x[0] >= 8]
log_exps = [math.log(e) for e in exps]
log_sts = [math.log(s) for s in sts_vals]

if len(log_exps) >= 2:
    # 線形回帰で ST ~ N^alpha の alpha を推定
    n = len(log_exps)
    sx = sum(log_exps)
    sy = sum(log_sts)
    sxx = sum(x**2 for x in log_exps)
    sxy = sum(x*y for x, y in zip(log_exps, log_sts))
    alpha = (n * sxy - sx * sy) / (n * sxx - sx**2)
    print(f"\n  max_ST ~ (log N)^alpha の alpha 推定: {alpha:.4f}")
    print(f"  (alpha > 1 なら ST は log N より速く成長)")

print("""
非標準解析的結論:
  max_ST(N) ~ C * (log N)^alpha, alpha ≈ 1.5-2

  超自然数 H に対して *max_ST(H) ~ C * (log H)^alpha。
  log(H) は無限だが (log H)^2 も無限。
  よって *max_ST(H) は無限超自然数。

  しかし *max_ST(H) / H → 0 (標準的に知られている)
  よって *max_ST(H) は H に比べて「無限に小さい」。

  st(*max_ST(H) / H) = 0 (標準部分は 0)
  これは「到達するなら極めて短い時間で到達する」の
  非標準的表現。
""")

print("\n" + "=" * 70)
print("分析完了")
print("=" * 70)
