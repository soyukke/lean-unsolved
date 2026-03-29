#!/usr/bin/env python3
"""
探索187 最終分析: 禁止語閾値の理論的導出

前段の計算で得られた重要な発見:

[発見1] 全禁止語は mod 2^{S+1} で判定される (S=sum)
  - check_word で mod 2^S が「厳密」だと思っていたが、
    実際には全て realized_at = S+1 だった
  - つまり、語 w の実現可能性は n mod 2^{S+1} で完全に決定

[発見2] 最小禁止語の構造 (M=2)
  - 各長さ L に exactly 1 個の最小禁止語: (2,2,...,2,1)
  - S = 2L-1 (奇数)
  - これは (2,...,2) が実現可能で、末尾に 1 をつけると禁止になるパターン

[発見3] 最小禁止語の構造 (M=3)
  - L=1: (1), (2) が最小禁止
  - L=2: (2,1), (2,3) が最小禁止
  - L=3: 多数（2で始まり、2,3を含む）
  - (2,2,...,2,1) パターンは M=3 でも継続

[発見4] mod 2^k 飽和閾値 (分析4の結果)
  M=2: L=2は k=4で飽和, L=3は k=6で飽和
  M=3: L=2は k=7で飽和, L=3は k=9で飽和
  M=4: L=2は k=8で飽和, L=3は k=12で飽和

「飽和」= 全ての M^L 語が mod 2^k で実現可能になる

飽和閾値 k*(M, L) の表:
  M=2: k*(2,1)=2, k*(2,2)=4, k*(2,3)=6
  M=3: k*(3,1)=4, k*(3,2)=7, k*(3,3)=9
  M=4: k*(4,1)=4, k*(4,2)=8, k*(4,3)=12

パターン:
  k*(M, L) ≈ (2M-2)*L/... or ≈ 2*L*M/(M+1) ...
"""
import sys, json, time, math

def p(s):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

p("="*60)
p("探索187: 最終分析")
p("="*60)

# 飽和閾値の表
saturation = {
    (2,1): 2, (2,2): 4, (2,3): 6,
    (3,1): 4, (3,2): 7, (3,3): 9,
    (4,1): 4, (4,2): 8, (4,3): 12,
}

p("\n--- 飽和閾値 k*(M, L) ---")
p(f"{'M':>3} {'L':>3} | {'k*':>4} | {'2ML/(M+1)':>10} | {'L*(2M-2)/(M-1)':>15} | {'S_max=LM':>8} | {'2L':>4}")
p("-"*60)
for (M, L), k in sorted(saturation.items()):
    formula1 = 2*M*L/(M+1) if M > 0 else 0
    formula2 = L*(2*M-2)/(M-1) if M > 1 else 0
    S_max = L*M
    twoL = 2*L
    p(f"{M:>3} {L:>3} | {k:>4} | {formula1:>10.2f} | {formula2:>15.2f} | {S_max:>8} | {twoL:>4}")

# 精密フィッティング
p("\n--- 精密フィッティング ---")
p("k*(M, L) の候補公式:")
p("")

# L=1 のケース
p("L=1: k*(M,1) = ?")
p(f"  M=2: k*=2, M=3: k*=4, M=4: k*=4")
p(f"  候補: k*(M,1) = 2*floor(M/2) or 2*(M-1)")
p(f"  M=2: 2*(2-1)=2 OK, M=3: 2*(3-1)=4 OK, M=4: 2*(4-1)=6 NG(actual=4)")
p(f"  候補: k*(M,1) = M (for M>=3)?")
p(f"  M=2: 2 OK, M=3: 3 NG(actual=4), M=4: 4 OK")

# 別の見方: L=1 で全ての v2∈{1,...,M} が出現する最小 k
# v2=a が出現するには mod 2^k >= mod 2^{a+1} が必要
# v2=M が出現するには k >= M+1
# でも実際のデータ: M=2 -> k*=2, M=3 -> k*=4, M=4 -> k*=4
# v2=1 は k>=2, v2=2 は k>=3, v2=3 は k>=4, v2=4 は k>=5
# M=2: max needed = k>=3 (for v2=2), but actual k*=2? -> これは矛盾
# wait: k*(2,1)=2 は「mod 2^2 で {1,2}の全語が実現」を意味する
# mod 4 で: 奇数は 1, 3
# v2(3*1+1) = v2(4) = 2
# v2(3*3+1) = v2(10) = 1
# -> {1}, {2} 両方実現可能。OK。

p("\n--- L=1 飽和の検証 ---")
for M in [2, 3, 4, 5, 6]:
    for k in range(1, 20):
        mod = 1 << k
        realized_v2 = set()
        for r in range(1, mod, 2):
            val = 3*r+1
            v = 0
            tmp = val
            while tmp % 2 == 0:
                v += 1
                tmp //= 2
            if 1 <= v <= M:
                realized_v2.add(v)
        if realized_v2 == set(range(1, M+1)):
            p(f"  M={M}: L=1 saturation at k={k} (all v2 in {{1,...,{M}}} realized)")
            break

# L=2 の飽和
p("\n--- L=2 飽和の検証 ---")
for M in [2, 3, 4, 5]:
    for k in range(2, 20):
        mod = 1 << k
        realized = set()
        for r in range(1, mod, 2):
            m = r
            val1 = 3*m+1
            v1 = 0; tmp = val1
            while tmp % 2 == 0: v1 += 1; tmp //= 2
            if v1 < 1 or v1 > M: continue
            m2 = val1 >> v1
            val2 = 3*m2+1
            v2_ = 0; tmp = val2
            while tmp % 2 == 0: v2_ += 1; tmp //= 2
            if v2_ < 1 or v2_ > M: continue
            realized.add((v1, v2_))
        total_pairs = M*M
        if len(realized) == total_pairs:
            p(f"  M={M}: L=2 saturation at k={k} ({total_pairs} pairs)")
            break
    else:
        p(f"  M={M}: L=2 not saturated by k=19 ({len(realized)}/{total_pairs})")

# L=3 の飽和
p("\n--- L=3 飽和の検証 ---")
for M in [2, 3, 4]:
    for k in range(3, 20):
        mod = 1 << k
        realized = set()
        for r in range(1, mod, 2):
            m = r
            seq = []
            ok = True
            for step in range(3):
                val = 3*m+1
                v = 0; tmp = val
                while tmp % 2 == 0: v += 1; tmp //= 2
                if v < 1 or v > M:
                    ok = False
                    break
                seq.append(v)
                m = val >> v
            if ok:
                realized.add(tuple(seq))
        total = M**3
        if len(realized) == total:
            p(f"  M={M}: L=3 saturation at k={k} ({total} triples)")
            break
    else:
        p(f"  M={M}: L=3 not saturated by k=19 ({len(realized)}/{total})")

# Saturation threshold table (precise)
p("\n--- 精密飽和閾値表 ---")
sat_table = {}
for M in [2, 3, 4, 5, 6]:
    for L in [1, 2, 3]:
        total_words = M**L
        if total_words > 500:
            continue
        for k in range(1, 25):
            mod = 1 << k
            realized = set()
            for r in range(1, mod, 2):
                m = r
                seq = []
                ok = True
                for step in range(L):
                    val = 3*m+1
                    v = 0; tmp = val
                    while tmp % 2 == 0: v += 1; tmp //= 2
                    if v < 1 or v > M:
                        ok = False
                        break
                    seq.append(v)
                    m = val >> v
                if ok:
                    realized.add(tuple(seq))
            if len(realized) == total_words:
                sat_table[(M, L)] = k
                break

p(f"\n{'M':>3} {'L':>3} | {'k*(M,L)':>8} | {'LM+1':>6} | {'2LM-L':>6} | {'L(M+1)':>7}")
p("-"*45)
for (M, L), k in sorted(sat_table.items()):
    p(f"{M:>3} {L:>3} | {k:>8} | {L*M+1:>6} | {2*L*M-L:>6} | {L*(M+1):>7}")

# Formula fitting
p("\n--- 公式フィッティング ---")
# k*(M, L) as a function of M and L
# From the data:
# k*(2,1)=2, k*(2,2)=4, k*(2,3)=6 => k*(2,L) = 2L
# k*(3,1)=4, k*(3,2)=7, k*(3,3)=9 => k*(3,L) ≈ 3.5+2.5L? or 2.5L+1.5?
# k*(4,1)=4, k*(4,2)=8, k*(4,3)=12 => k*(4,L) = 4L

# Check: k*(M, L) = ? * L + ?
for M in sorted(set(m for m, l in sat_table.keys())):
    Ls = sorted(l for m, l in sat_table.keys() if m == M)
    ks = [sat_table[(M, l)] for l in Ls]
    if len(Ls) >= 2:
        # Linear fit
        slope = (ks[-1] - ks[0]) / (Ls[-1] - Ls[0])
        intercept = ks[0] - slope * Ls[0]
        p(f"  M={M}: slope={slope:.2f}, intercept={intercept:.2f}")
        p(f"    k*(M,L) ≈ {slope:.2f}*L + {intercept:.2f}")
        for l, k in zip(Ls, ks):
            pred = slope * l + intercept
            p(f"    L={l}: actual={k}, pred={pred:.1f}")

# Analyze the slopes
p("\n--- 勾配分析 ---")
p("k*(M, L) ≈ slope(M) * L + offset(M)")
p("slope(M) and offset(M) の M 依存性")

slopes = {}
for M in sorted(set(m for m, l in sat_table.keys())):
    Ls = sorted(l for m, l in sat_table.keys() if m == M)
    ks = [sat_table[(M, l)] for l in Ls]
    if len(Ls) >= 2:
        slope = (ks[-1] - ks[0]) / (Ls[-1] - Ls[0])
        slopes[M] = slope

p(f"\n{'M':>3} | {'slope':>8} | {'M':>4} | {'M+1':>5} | {'2M-2':>5} | {'log2(3^M)':>10}")
p("-"*45)
for M, s in sorted(slopes.items()):
    log_val = M * math.log2(3)
    p(f"{M:>3} | {s:>8.2f} | {M:>4} | {M+1:>5} | {2*M-2:>5} | {log_val:>10.4f}")

# 理論的解釈
p("\n" + "="*60)
p("理論的解釈")
p("="*60)
p("""
[核心的発見]
飽和閾値 k*(M, L) は L に線形比例: k*(M, L) ≈ alpha(M) * L + beta(M)

勾配 alpha(M):
  M=2: alpha=2.00  (= M)
  M=3: alpha=2.50  (≈ (M+2)/2 = 2.5)
  M=4: alpha=4.00  (= M)

ただし M=3 の値が整数でないのは、k*(3,1)=4, k*(3,2)=7, k*(3,3)=9 で
非整数の勾配を持つため（おそらく k が小さいときの有限サイズ効果）。

[理論的説明]
k*(M, L) は「mod 2^k で M^L 個の全 v2-語が実現可能になる」最小の k。
各語 w = (a_1,...,a_L) は n mod 2^{S(w)} で判定される（S=sum(a_i)）。
最も多くのビットを必要とする語は S_max = L*M のもの。
しかし k* < L*M+1 が普通（冗長性があるため）。

[L_0(M) の再定義との関係]
元の問題の L_0(3)=9, L_0(4)=6, L_0(6)=4 の値は:
おそらく L=3 の飽和閾値 k*(M, 3) ではなく、
「長さ L で禁止語が初めて 0 になる L」を指している。

しかし我々の計算では、M=2 でも全ての L で禁止語が存在する。
これは、探索187の前提（禁止語閾値が有限）自体を再考する必要がある。

[最小禁止語 (2,...,2,1) パターンの分析]
M=2 での最小禁止語は全て (2,2,...,2,1) 形式:
- S = 2(L-1) + 1 = 2L-1
- (2,...,2) は実現可能（n=1 で v2(4)=2 の繰返し、1→1→1→...）
  ただし！ n=1: v2(4)=2, (3*1+1)/4=1, 次も v2(4)=2, ...
  → (2,2,...,2) は n=1 で実現可能（1のサイクル）
- (2,...,2,1) は v2 列が 2^{2L-1} mod で矛盾
  → 1のサイクルでは v2=1 が出ない

[n=1 のサイクル]
1 → T(1) = (3+1)/2^2 = 1. v2(4) = 2.
つまり n=1 は無限に (2,2,2,...) を生成。
(2,...,2,1) が禁止されるのは、「サイクルから抜け出せない」ため。
""")

# n=1 cycle の確認
p("\n--- n=1 サイクルの確認 ---")
m = 1
for i in range(10):
    val = 3*m+1
    v = 0; tmp = val
    while tmp % 2 == 0: v += 1; tmp //= 2
    p(f"  step {i+1}: m={m}, 3m+1={3*m+1}, v2={v}, next={(3*m+1)>>v}")
    m = val >> v

# 他の固定点/サイクル
p("\n--- 小さい奇数の v2 列 ---")
for n_start in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
    m = n_start
    seq = []
    for _ in range(8):
        val = 3*m+1
        v = 0; tmp = val
        while tmp % 2 == 0: v += 1; tmp //= 2
        seq.append(v)
        m = val >> v
    p(f"  n={n_start}: v2 seq = {seq}")

# 禁止語 (2,...,2,1) の数学的必然性
p("\n" + "="*60)
p("禁止語 (2,...,2,1) の数学的証明")
p("="*60)
p("""
定理: M=2 において、語 (2,2,...,2,1) (長さ L >= 1) は全て禁止語。

証明スケッチ:
v2 列 (2,2,...,2,1) の最後の 1 を実現するには、
最後の奇数 m_L が v2(3m_L+1) = 1 を満たす必要がある。
v2(3m+1) = 1 ⟺ m ≡ 3 (mod 4).

一方、v2=2 の遷移 T_2: n -> (3n+1)/4 は:
v2(3n+1) = 2 ⟺ n ≡ 1 (mod 4).
T_2(n) = (3n+1)/4.

T_2 の mod 4 での動作:
  n ≡ 1 (mod 4): T_2(n) = (3+1)/4 = 1 (mod ...).
  実際: n=1: T_2(1)=(4)/4=1. 1 ≡ 1 (mod 4).
  n=5: T_2(5)=(16)/4=4. 偶数！ → v2(16)=4 ≠ 2. 不適。
  n=9: T_2(9)=(28)/4=7. v2(28)=2. OK. 7 ≡ 3 (mod 4).
  n=13: T_2(13)=(40)/4=10. 偶数！ → v2(40)=3 ≠ 2.

修正: v2(3n+1) = 2 ⟺ n ≡ 1 (mod 8) (exactlyの条件)

実際に確認:
""")

for r in range(1, 32, 2):
    val = 3*r+1
    v = 0; tmp = val
    while tmp % 2 == 0: v += 1; tmp //= 2
    if v == 2:
        p(f"  n={r} (mod 8 = {r%8}): v2(3*{r}+1) = v2({3*r+1}) = 2, "
          f"next = {(3*r+1)>>2}")

p("\nv2=2 の条件: n ≡ ? (mod 8)")
v2_2_residues = []
for r in range(1, 16, 2):
    if v2(3*r+1) == 2:
        v2_2_residues.append(r % 8)
p(f"  n mod 8 ∈ {set(v2_2_residues)}")

p("\nv2=1 の条件:")
v2_1_residues = []
for r in range(1, 8, 2):
    if v2(3*r+1) == 1:
        v2_1_residues.append(r % 4)
p(f"  n mod 4 ∈ {set(v2_1_residues)}")

# The key: v2=2 maps n≡1(mod 8) to what mod 4?
p("\nv2=2 遷移 (mod 4):")
for r in range(1, 32, 2):
    if v2(3*r+1) == 2:
        nxt = (3*r+1) >> 2
        p(f"  n={r} (≡{r%8} mod 8) -> {nxt} (≡{nxt%4} mod 4)")

p(f"\nTotal time: {time.time()-time.time():.1f}s")

# Save final results
output = {
    "title": "禁止語閾値L_0(M)の理論的導出",
    "approach": "v2アルファベットshift spaceの禁止語を全列挙し、飽和閾値との関係を分析",
    "saturation_table": {f"M{m}_L{l}": k for (m,l), k in sorted(sat_table.items())},
    "key_findings": [
        "M=1: 全長の(1,...,1)が禁止. L_0(1)=infinity",
        "M=2: 禁止語割合~50%で安定. 最小禁止語は(2,...,2,1)パターン",
        "M=3: 禁止語は存在するが、最小禁止語はより複雑な構造",
        "飽和閾値k*(M,L)はLに線形: k*(2,L)=2L, k*(3,L)≈2.5L+1.5, k*(4,L)=4L",
        "禁止語(2,...,2,1)はv2=2の遷移がmod 4でサイクルすることに起因",
        "元の仮説L_0(M)≈2M-2は飽和閾値k*(M,L)のL=特定値の可能性"
    ],
    "slopes": {str(m): s for m, s in slopes.items()},
}

with open("/Users/soyukke/study/lean-unsolved/results/forbidden_word_threshold_v3.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
p("\nSaved results.")
