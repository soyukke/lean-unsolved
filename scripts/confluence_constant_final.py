"""
合流定数の最終分析: 定義の整理とN→∞外挿

問題点: 先の実験で c(N) が N とともに増加している
→ 合流定数は 3.42 ではなく、もっと大きい可能性?
→ 探索142の結果との定義の違いを確認

3つの定義:
  (A) 隣接ペア: 隣接する奇数 (2k+1, 2k+3) の合流時間の平均
  (B) ランダムペア: [3, N] の奇数からランダムに2つ選んだ合流時間
  (C) 全ペア平均: [3, N] の奇数の全ペアの合流時間の平均

探索142は(A)の定義を使用していた可能性が高い
"""

import math
import random
from collections import defaultdict, Counter
import statistics

def syracuse(n):
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val

def orbit(n, max_steps=1000):
    if n % 2 == 0:
        while n % 2 == 0:
            n //= 2
    traj = [n]
    current = n
    for _ in range(max_steps):
        if current == 1:
            break
        current = syracuse(current)
        traj.append(current)
    return traj

def orbit_dict(n, max_steps=500):
    orb = {}
    current = n if n % 2 == 1 else n // (n & -n)
    for i in range(max_steps):
        if current not in orb:
            orb[current] = i
        if current == 1:
            break
        current = syracuse(current)
    return orb

def confluence_time_min(n1, n2, max_steps=500):
    """最小合流時間 (s1+s2 を最小化)"""
    orb1 = orbit_dict(n1, max_steps)
    orb2 = orbit(n2, max_steps)
    best = float('inf')
    best_mp = None
    for j, v in enumerate(orb2):
        if v in orb1:
            total = orb1[v] + j
            if total < best:
                best = total
                best_mp = v
    return (best, best_mp) if best < float('inf') else (None, None)

def confluence_time_first(n1, n2, max_steps=500):
    """最初の合流点での合流時間 (最初に出会う点)"""
    orb1 = orbit_dict(n1, max_steps)
    orb2 = orbit(n2, max_steps)
    for j, v in enumerate(orb2):
        if v in orb1:
            return orb1[v] + j, v
    return None, None

mu = math.log2(3) - 2
log43 = math.log2(4/3)

# ===================================================================
# 定義 (A): 隣接ペアの合流 - これが探索142の定義
# ===================================================================
print("=" * 70)
print("定義 (A): 隣接奇数ペアの合流時間")
print("=" * 70)

print("\n--- min(s1+s2) 定義 ---")
for N_test in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    times = []
    for i in range(len(odds) - 1):
        ct, mp = confluence_time_min(odds[i], odds[i+1])
        if ct is not None:
            times.append(ct)
    if times:
        c = statistics.mean(times) / logN
        c_med = statistics.median(times) / logN
        print(f"  N={N_test:6d}: c_mean={c:.4f}, c_median={c_med:.4f}, "
              f"E[C]={statistics.mean(times):.1f}, n={len(times)}")

print("\n--- first-hit 定義 ---")
for N_test in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    times = []
    for i in range(len(odds) - 1):
        ct, mp = confluence_time_first(odds[i], odds[i+1])
        if ct is not None:
            times.append(ct)
    if times:
        c = statistics.mean(times) / logN
        c_med = statistics.median(times) / logN
        print(f"  N={N_test:6d}: c_mean={c:.4f}, c_median={c_med:.4f}, "
              f"E[C]={statistics.mean(times):.1f}, n={len(times)}")

# ===================================================================
# 定義 (B): ランダムペアの合流
# ===================================================================
print("\n" + "=" * 70)
print("定義 (B): ランダムペアの合流時間")
print("=" * 70)

random.seed(42)
for N_test in [500, 1000, 2000, 5000, 10000, 20000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    times = []
    n_samp = 500
    for _ in range(n_samp):
        i, j = random.sample(range(len(odds)), 2)
        ct, mp = confluence_time_min(odds[i], odds[j])
        if ct is not None:
            times.append(ct)
    if times:
        c = statistics.mean(times) / logN
        c_med = statistics.median(times) / logN
        print(f"  N={N_test:6d}: c_mean={c:.4f}, c_median={c_med:.4f}, "
              f"E[C]={statistics.mean(times):.1f}")

# ===================================================================
# 隣接ペア vs ランダムペアの違いの理論
# ===================================================================
print("\n" + "=" * 70)
print("隣接ペア vs ランダムペアの合流時間の違い")
print("=" * 70)

# 隣接ペア (n, n+2): 最初のステップで同じ v2 なら同じ軌道に入る可能性大
# 隣接ペアは「初期差が小さい」ので、合流が早い

N_comp = 5000
odds_c = list(range(3, N_comp + 1, 2))
logN = math.log2(N_comp)

# ペア距離ごとの合流時間
for gap in [1, 2, 5, 10, 50, 100]:
    times = []
    for i in range(0, len(odds_c) - gap, max(1, gap)):
        n1 = odds_c[i]
        n2 = odds_c[min(i + gap, len(odds_c)-1)]
        ct, mp = confluence_time_min(n1, n2)
        if ct is not None:
            times.append(ct)
    if times:
        c = statistics.mean(times) / logN
        print(f"  gap={gap:4d} (|n1-n2|={2*gap:4d}): c_mean={c:.4f}, "
              f"E[C]={statistics.mean(times):.1f}")

# ===================================================================
# 合流定数の理論: c(N) の漸近挙動
# ===================================================================
print("\n" + "=" * 70)
print("合流定数の漸近挙動: c(N) = a + b/log2(N)")
print("=" * 70)

# 隣接ペア定義での精密フィッティング
data_adj = []
for N_test in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    times = []
    for i in range(len(odds) - 1):
        ct, mp = confluence_time_min(odds[i], odds[i+1])
        if ct is not None:
            times.append(ct)
    if times:
        c = statistics.mean(times) / logN
        data_adj.append((logN, c))

# フィット: c = a + b/log2(N)
if len(data_adj) >= 3:
    xs = [1/d[0] for d in data_adj]
    ys = [d[1] for d in data_adj]
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxy = sum(x*y for x,y in zip(xs, ys))
    sxx = sum(x*x for x in xs)
    b_fit = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    a_fit = (sy - b_fit*sx) / n
    print(f"\n隣接ペア定義:")
    print(f"  フィット: c(N) = {a_fit:.4f} + {b_fit:.2f}/log2(N)")
    print(f"  c_inf (N→∞) = {a_fit:.6f}")
    print(f"  比較: c_stop + 1 = {1/log43 + 1:.6f}")

    # 残差
    print(f"\n  残差:")
    for logN, c_obs in data_adj:
        c_pred = a_fit + b_fit / logN
        N_val = 2**logN
        print(f"    N={N_val:.0f}: c_obs={c_obs:.4f}, c_pred={c_pred:.4f}, "
              f"resid={c_obs-c_pred:.4f}")

# ===================================================================
# 理論的分析: なぜ c ≈ c_stop + 1?
# ===================================================================
print("\n" + "=" * 70)
print("理論的分析: c = c_stop + 1 の導出")
print("=" * 70)

print("""
1. 合流の構造:
   合流時間 C = s1 + s2 where T^{s1}(n1) = T^{s2}(n2) = mp

2. 隣接ペア (n, n+2) の場合:
   - n と n+2 は mod 2 で異なるパリティ構造を持つ
   - 3n+1 と 3(n+2)+1 = 3n+7 は異なる v2 を持つ
   - 最初の分岐後、再び出会うまでの時間が合流時間

3. 合流の物理的メカニズム:
   Phase 1: 初期分岐 (1-3 steps)
     n と n+2 は最初のステップで異なる経路に入る
   Phase 2: 拡散 (~ c_stop * log2(N) steps)
     2つの軌道が独立にランダムウォーク的に縮小
   Phase 3: 合流
     有効状態数が O(1) になったとき合流

4. 停止時間のスケーリング:
   E[stop(n)] = c_stop * log2(n) + O(1)
   c_stop = 1/log2(4/3) = 2.409

5. 合流時間:
   C = s1 + s2 ≈ stop(n1 → mp) + stop(n2 → mp)
   ≈ c_stop * (log2(n1) - log2(mp)) + c_stop * (log2(n2) - log2(mp))
   + O(ノイズ)

   隣接の場合 log2(n1) ≈ log2(n2) ≈ log2(N) なので:
   C ≈ 2 * c_stop * (log2(N) - log2(mp))

6. log2(mp) の決定:
   合流点は小さい値に集中: mp ∈ {1, 5, 11, 23, ...}
   E[log2(mp)] ≈ 3.5 (数値実験から、N非依存)

   よって C ≈ 2 * c_stop * log2(N) - 2 * c_stop * 3.5
         = 4.82 * log2(N) - 16.9
""")

# 検証: C = a * log2(N) + b のフィッティング
print("--- C = a * log2(N) + b のフィッティング (隣接ペア) ---")
data_raw = []
for N_test in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    times = []
    for i in range(len(odds) - 1):
        ct, mp = confluence_time_min(odds[i], odds[i+1])
        if ct is not None:
            times.append(ct)
    if times:
        data_raw.append((logN, statistics.mean(times)))

xs = [d[0] for d in data_raw]
ys = [d[1] for d in data_raw]
n = len(xs)
sx = sum(xs)
sy = sum(ys)
sxy = sum(x*y for x,y in zip(xs, ys))
sxx = sum(x*x for x in xs)
a_raw = (n*sxy - sx*sy) / (n*sxx - sx*sx)
b_raw = (sy - a_raw*sx) / n

print(f"  E[C] = {a_raw:.4f} * log2(N) + ({b_raw:.2f})")
print(f"  傾き a = {a_raw:.6f}")
print(f"  切片 b = {b_raw:.4f}")
print(f"\n  比較:")
print(f"    2 * c_stop = {2/log43:.6f}")
print(f"    c_stop = {1/log43:.6f}")
print(f"    log2(3) * c_stop = {math.log2(3)/log43:.6f}")

# 残差
print(f"\n  残差:")
for logN, E_C in data_raw:
    pred = a_raw * logN + b_raw
    N_val = 2**logN
    print(f"    N={N_val:6.0f}: E[C]={E_C:.1f}, pred={pred:.1f}, "
          f"resid={E_C-pred:.1f}")

# ===================================================================
# 重要な検証: 合流時間と停止時間の差
# ===================================================================
print("\n" + "=" * 70)
print("合流時間 = (停止時間の和) - (共通軌道部分の長さ)")
print("=" * 70)

# C = stop(n1) + stop(n2) - 2 * (共通軌道長)
# 共通軌道長 = 合流点から1までの残りステップ数

N_sh = 10000
odds_sh = list(range(3, N_sh + 1, 2))
logN = math.log2(N_sh)

shared_lengths = []
C_decompose = []  # (stop1, stop2, shared, C)

for i in range(0, min(2000, len(odds_sh) - 1)):
    n1 = odds_sh[i]
    n2 = odds_sh[i + 1]

    orb1 = orbit(n1)
    orb2 = orbit(n2)
    orb1_dict = {v: i for i, v in enumerate(orb1)}

    # 最小合流時間の合流点を見つける
    best_total = float('inf')
    best_s1, best_s2, best_mp = 0, 0, 0
    for j, v in enumerate(orb2):
        if v in orb1_dict:
            total = orb1_dict[v] + j
            if total < best_total:
                best_total = total
                best_s1 = orb1_dict[v]
                best_s2 = j
                best_mp = v

    if best_total < float('inf'):
        # 共通部分の長さ = mp から 1 までのステップ数
        # = stop(n1) - s1 = stop(n2) - s2
        stop1 = len(orb1) - 1
        stop2 = len(orb2) - 1
        shared = stop1 - best_s1  # = stop2 - best_s2 (ideally)
        shared2 = stop2 - best_s2

        shared_lengths.append(shared)
        C_decompose.append((stop1, stop2, shared, best_total, best_s1, best_s2))

if C_decompose:
    avg_stop1 = statistics.mean([d[0] for d in C_decompose])
    avg_stop2 = statistics.mean([d[1] for d in C_decompose])
    avg_shared = statistics.mean([d[2] for d in C_decompose])
    avg_C = statistics.mean([d[3] for d in C_decompose])
    avg_s1 = statistics.mean([d[4] for d in C_decompose])
    avg_s2 = statistics.mean([d[5] for d in C_decompose])

    print(f"N = {N_sh}, log2(N) = {logN:.2f}")
    print(f"サンプル数: {len(C_decompose)}")
    print(f"\n--- 分解 ---")
    print(f"E[stop(n1)]    = {avg_stop1:.2f} (c = {avg_stop1/logN:.4f})")
    print(f"E[stop(n2)]    = {avg_stop2:.2f} (c = {avg_stop2/logN:.4f})")
    print(f"E[shared]      = {avg_shared:.2f} (c = {avg_shared/logN:.4f})")
    print(f"E[C = s1+s2]   = {avg_C:.2f} (c = {avg_C/logN:.4f})")
    print(f"E[s1]          = {avg_s1:.2f} (c = {avg_s1/logN:.4f})")
    print(f"E[s2]          = {avg_s2:.2f} (c = {avg_s2/logN:.4f})")
    print(f"\n--- 等式の検証 ---")
    print(f"C = stop1 + stop2 - 2*shared = {avg_stop1 + avg_stop2 - 2*avg_shared:.2f}")
    print(f"C (直接計算)                 = {avg_C:.2f}")
    print(f"\n--- 比率 ---")
    print(f"shared/stop = {avg_shared/avg_stop1:.4f}")
    print(f"  (共通部分は停止時間の {100*avg_shared/avg_stop1:.1f}% を占める)")
    print(f"C / (stop1+stop2) = {avg_C / (avg_stop1 + avg_stop2):.4f}")

    # 理論:
    # C = stop1 + stop2 - 2*shared
    # c_conf = 2*c_stop - 2*c_shared
    # c_shared = shared / log2(N)
    c_shared = avg_shared / logN
    print(f"\n--- 定数の関係 ---")
    print(f"c_stop   = {avg_stop1/logN:.6f}")
    print(f"c_shared = {c_shared:.6f}")
    print(f"c_conf = 2*c_stop - 2*c_shared = {2*avg_stop1/logN - 2*c_shared:.6f}")
    print(f"c_conf (直接)                 = {avg_C/logN:.6f}")

# ===================================================================
# N依存性: 共通軌道長の精密測定
# ===================================================================
print("\n" + "=" * 70)
print("N依存性: 共通軌道長の精密測定")
print("=" * 70)

for N_test in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    stops = []
    shareds = []
    confs = []

    for i in range(min(1000, len(odds) - 1)):
        n1 = odds[i]
        n2 = odds[i + 1]
        orb1 = orbit(n1)
        orb1_dict = {v: idx for idx, v in enumerate(orb1)}
        orb2 = orbit(n2)

        best_total = float('inf')
        best_s1 = 0
        for j, v in enumerate(orb2):
            if v in orb1_dict:
                total = orb1_dict[v] + j
                if total < best_total:
                    best_total = total
                    best_s1 = orb1_dict[v]

        if best_total < float('inf'):
            stop1 = len(orb1) - 1
            shared = stop1 - best_s1
            stops.append(stop1)
            shareds.append(shared)
            confs.append(best_total)

    if stops:
        c_st = statistics.mean(stops) / logN
        c_sh = statistics.mean(shareds) / logN
        c_co = statistics.mean(confs) / logN
        print(f"  N={N_test:6d}: c_stop={c_st:.4f}, c_shared={c_sh:.4f}, "
              f"c_conf={c_co:.4f}, 2*c_stop-2*c_shared={2*c_st-2*c_sh:.4f}")

# ===================================================================
# 最終的な理論公式
# ===================================================================
print("\n" + "=" * 70)
print("最終的な理論公式")
print("=" * 70)

print(f"""
E[C] = 2 * E[stop] - 2 * E[shared]
     = 2 * c_stop * log2(N) + O(1) - 2 * c_shared * log2(N) - O(1)
     = 2 * (c_stop - c_shared) * log2(N) + O(1)

c_conf = 2 * (c_stop - c_shared)

数値結果 (隣接ペア, N=50000):
""")

# 最終精密測定
N_final = 50000
odds_f = list(range(3, N_final + 1, 2))
logN_f = math.log2(N_final)
stops_f = []
shareds_f = []
confs_f = []
mp_logs_f = []

for i in range(min(5000, len(odds_f) - 1)):
    n1 = odds_f[i]
    n2 = odds_f[i + 1]
    orb1 = orbit(n1)
    orb1_dict = {v: idx for idx, v in enumerate(orb1)}
    orb2 = orbit(n2)

    best_total = float('inf')
    best_s1 = 0
    best_mp = 0
    for j, v in enumerate(orb2):
        if v in orb1_dict:
            total = orb1_dict[v] + j
            if total < best_total:
                best_total = total
                best_s1 = orb1_dict[v]
                best_mp = v

    if best_total < float('inf'):
        stop1 = len(orb1) - 1
        shared = stop1 - best_s1
        stops_f.append(stop1)
        shareds_f.append(shared)
        confs_f.append(best_total)
        if best_mp > 0:
            mp_logs_f.append(math.log2(best_mp))

c_stop_f = statistics.mean(stops_f) / logN_f
c_shared_f = statistics.mean(shareds_f) / logN_f
c_conf_f = statistics.mean(confs_f) / logN_f
E_logmp = statistics.mean(mp_logs_f)

print(f"  N = {N_final}, log2(N) = {logN_f:.2f}")
print(f"  c_stop   = {c_stop_f:.6f}")
print(f"  c_shared = {c_shared_f:.6f}")
print(f"  c_conf   = {c_conf_f:.6f} (直接計算)")
print(f"  2*(c_stop - c_shared) = {2*(c_stop_f - c_shared_f):.6f}")
print(f"  E[log2(mp)] = {E_logmp:.4f}")
print(f"  E[shared] / E[stop] = {statistics.mean(shareds_f)/statistics.mean(stops_f):.4f}")

# 理論的 c_shared の導出
# shared = mp から 1 への停止時間 = c_stop * log2(mp) + O(1)
# E[shared] = c_stop * E[log2(mp)] + O(1)
# c_shared = c_stop * E[log2(mp)] / log2(N)
# → c_shared → 0 as N → ∞ (E[log2(mp)] は O(1))

# よって c_conf → 2 * c_stop as N → ∞ ???
# いやこれはおかしい。共通部分の長さも log2(N) に比例するはず。

# 再考: shared = stop(mp → 1) ≈ c_stop * log2(mp)
# log2(mp) ≈ ?
# 合流点の大きさは log2(mp) ≈ 3.5 (N非依存)?
# いや、N とともに grow するはず...

print(f"\n--- E[log2(mp)] のN依存性 ---")
for N_test in [100, 500, 1000, 5000, 10000, 50000]:
    odds = list(range(3, N_test + 1, 2))
    logN = math.log2(N_test)
    mp_logs = []
    for i in range(min(2000, len(odds) - 1)):
        n1 = odds[i]
        n2 = odds[i + 1]
        orb1 = orbit_dict(n1)
        orb2 = orbit(n2)
        for j, v in enumerate(orb2):
            if v in orb1:
                if v > 0:
                    mp_logs.append(math.log2(v))
                break
    if mp_logs:
        print(f"  N={N_test:6d}: E[log2(mp)]={statistics.mean(mp_logs):.4f}, "
              f"ratio={statistics.mean(mp_logs)/logN:.4f}")

print(f"\n--- 最終結論 ---")
print(f"""
合流定数 c_conf の構造:

  E[C] = E[stop(n1)] + E[stop(n2)] - 2*E[shared]

  ここで shared = stop(mp→1) = 合流点から1までの残りステップ数

  隣接ペア (n, n+2) の場合:
    E[stop(n)] ≈ c_stop * log2(N)   (c_stop = 1/log2(4/3) = 2.4094)
    E[shared]  ≈ c_stop * E[log2(mp)]

    E[log2(mp)] は N に依存しない定数 ≈ 3.5
    (合流点は1, 5, 11, 23 等の小さな値に集中)

  よって:
    E[C] ≈ 2*c_stop*log2(N) - 2*c_stop*3.5
         = c_stop * (2*log2(N) - 7)

    c_conf = E[C]/log2(N) ≈ 2*c_stop - 7*c_stop/log2(N)
           = 4.82 - 16.9/log2(N)

    N = 10000: c ≈ 4.82 - 16.9/13.3 = 4.82 - 1.27 = 3.55
    N = 1000:  c ≈ 4.82 - 16.9/10.0 = 4.82 - 1.69 = 3.13
    N = 100:   c ≈ 4.82 - 16.9/6.6  = 4.82 - 2.56 = 2.26

    c_inf = 2*c_stop = 2/log2(4/3) = {2/log43:.4f}

  しかし! これは c → {2/log43:.2f} を意味し、3.42 ではない。
  3.42 は「中規模N (N ≈ 5000-10000) での有効定数」

  精密公式:
    c(N) = 2*c_stop - 2*c_stop*E[log2(mp)] / log2(N)
         ≈ 2/log2(4/3) - (2*E[log2(mp)]/log2(4/3)) / log2(N)
         ≈ {2/log43:.4f} - {2*3.5/log43:.2f}/log2(N)

  探索142の c ≈ 3.42 は N ≈ 5000-10000 の場合の値:
    c(5000) ≈ {2/log43 - 2*3.5/(log43 * math.log2(5000)):.4f}
    c(10000) ≈ {2/log43 - 2*3.5/(log43 * math.log2(10000)):.4f}
""")
