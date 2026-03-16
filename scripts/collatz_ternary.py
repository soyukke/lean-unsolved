#!/usr/bin/env python3
"""
コラッツ予想の3進(base-3)表現による解析

アプローチ:
1. 奇数nの3進表現とSyracuse T(n)の3進表現の関係
2. 3進でのCollatz操作の解釈 (3進左シフト + 2進右シフト)
3. 3進桁和の変化
4. 3-adic的性質
5. (2,3)-adic同時解析
"""

import math
from collections import Counter, defaultdict

# ============================================================
# ユーティリティ
# ============================================================

def to_base3(n):
    """nの3進表現を文字列で返す (最上位桁が先頭)"""
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    return "".join(reversed(digits))

def base3_digits(n):
    """nの3進桁リスト (最下位桁が先頭)"""
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % 3)
        n //= 3
    return digits

def digit_sum_base3(n):
    """3進桁和"""
    s = 0
    while n > 0:
        s += n % 3
        n //= 3
    return s

def v2(n):
    """2-adic valuation (nを割り切る2の最大冪)"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def v3(n):
    """3-adic valuation"""
    if n == 0:
        return float('inf')
    c = 0
    while n % 3 == 0:
        n //= 3
        c += 1
    return c

def syracuse(n):
    """Syracuse写像: T(n) = (3n+1)/2^v2(3n+1), nは奇数"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def collatz_sequence(n):
    """nから1に至るコラッツ列 (奇数のみ, Syracuse)"""
    seq = [n]
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = syracuse(n)
        seq.append(n)
    return seq

# ============================================================
# 解析1: 3進表現でのn → T(n) の桁変化パターン
# ============================================================

def analysis_1_digit_transition():
    print("=" * 70)
    print("解析1: 3進表現での n → T(n) の桁変化パターン")
    print("=" * 70)

    # 小さい例を詳しく表示
    print("\n--- 小さい奇数での例 ---")
    print(f"{'n':>6} {'n(base3)':>12} {'T(n)':>6} {'T(n)(base3)':>12} {'v2(3n+1)':>8} {'桁数変化':>8}")
    for n in range(1, 40, 2):
        tn = syracuse(n)
        v = v2(3*n+1)
        d_n = len(to_base3(n))
        d_tn = len(to_base3(tn))
        print(f"{n:>6} {to_base3(n):>12} {tn:>6} {to_base3(tn):>12} {v:>8} {d_tn - d_n:>+8}")

    # 3進の末尾桁(最下位桁)による分類
    print("\n--- n mod 3 による T(n) mod 3 の分布 (n=1..9999, 奇数) ---")
    # n mod 3 = 0 は n=3k で奇数なのは k が奇数の場合
    # n mod 3 = 1 は n≡1(mod 3)
    # n mod 3 = 2 は n≡2(mod 3)
    transition_count = defaultdict(Counter)
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        transition_count[n % 3][tn % 3] += 1

    for r in [0, 1, 2]:
        total = sum(transition_count[r].values())
        print(f"  n ≡ {r} (mod 3): ", end="")
        for t in [0, 1, 2]:
            c = transition_count[r][t]
            print(f"T(n)≡{t}: {c} ({100*c/total:.1f}%)  ", end="")
        print()

    # 3進の末尾2桁 (mod 9) による分類
    print("\n--- n mod 9 による v2(3n+1) の平均値 ---")
    v2_by_mod9 = defaultdict(list)
    for n in range(1, 10000, 2):
        v2_by_mod9[n % 9].append(v2(3*n+1))
    for r in sorted(v2_by_mod9.keys()):
        vals = v2_by_mod9[r]
        avg = sum(vals) / len(vals)
        print(f"  n ≡ {r} (mod 9): 平均 v2 = {avg:.3f}, 最頻値 = {Counter(vals).most_common(1)[0][0]}")

    # 3進末尾桁の遷移パターン (mod 3^k)
    print("\n--- 3進末尾2桁の遷移 (n mod 9 → T(n) mod 9) ---")
    trans9 = defaultdict(Counter)
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        trans9[n % 9][tn % 9] += 1
    for r in sorted(trans9.keys()):
        print(f"  n≡{r}(mod 9): ", end="")
        for t in sorted(trans9[r].keys()):
            c = trans9[r][t]
            print(f"→{t}:{c} ", end="")
        print()


# ============================================================
# 解析2: 3進左シフト + 2進右シフトの混合操作
# ============================================================

def analysis_2_shift_interpretation():
    print("\n" + "=" * 70)
    print("解析2: 3進左シフト + 2進右シフト の混合操作")
    print("=" * 70)

    print("\n--- 3n+1 の3進表現 = nの3進表現を左シフト+1 ---")
    print(f"{'n':>6} {'n(b3)':>10} {'3n+1(b3)':>12} {'v2':>4} {'T(n)(b3)':>12}")
    for n in range(1, 30, 2):
        m = 3*n + 1
        v = v2(m)
        tn = m >> v
        print(f"{n:>6} {to_base3(n):>10} {to_base3(m):>12} {v:>4} {to_base3(tn):>12}")

    # 3n+1 の2-adic valuation と 3進末尾桁の関係
    print("\n--- v2(3n+1) の分布を n mod 6 で分類 ---")
    # n は奇数なので n mod 6 ∈ {1, 3, 5}
    v2_by_mod = defaultdict(Counter)
    for n in range(1, 10000, 2):
        v2_by_mod[n % 6][v2(3*n+1)] += 1
    for r in sorted(v2_by_mod.keys()):
        print(f"  n ≡ {r} (mod 6):")
        for v_val in sorted(v2_by_mod[r].keys())[:8]:
            c = v2_by_mod[r][v_val]
            print(f"    v2={v_val}: {c}", end="")
        print()

    # 3n+1 の3進表現と元のnの3進表現の差分
    print("\n--- T(n) = (3n+1)/2^k の3進桁と n の3進桁の関係 ---")
    print("  (3進桁ごとの差分パターン)")
    digit_diffs = Counter()
    for n in range(1, 1000, 2):
        tn = syracuse(n)
        dn = base3_digits(n)
        dtn = base3_digits(tn)
        maxlen = max(len(dn), len(dtn))
        dn += [0] * (maxlen - len(dn))
        dtn += [0] * (maxlen - len(dtn))
        diff = tuple((dtn[i] - dn[i]) % 3 for i in range(maxlen))
        digit_diffs[diff] += 1

    print(f"  ユニークな差分パターン数: {len(digit_diffs)}")
    print(f"  上位10パターン:")
    for pat, cnt in digit_diffs.most_common(10):
        print(f"    {pat}: {cnt}回")


# ============================================================
# 解析3: 3進桁和の変化
# ============================================================

def analysis_3_digit_sum():
    print("\n" + "=" * 70)
    print("解析3: 3進桁和 s3(n) と s3(T(n)) の関係")
    print("=" * 70)

    # s3(n) vs s3(T(n)) の散布データ
    ds_counter = Counter()  # s3(T(n)) - s3(n) の分布
    ratio_by_s3 = defaultdict(list)
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        s_n = digit_sum_base3(n)
        s_tn = digit_sum_base3(tn)
        ds_counter[s_tn - s_n] += 1
        ratio_by_s3[s_n].append(s_tn)

    print("\n--- s3(T(n)) - s3(n) の分布 ---")
    for ds in sorted(ds_counter.keys()):
        c = ds_counter[ds]
        if c >= 5:
            print(f"  Δs3 = {ds:>+3}: {c:>5} 回")

    print("\n--- s3(n) ごとの s3(T(n)) の平均 ---")
    for s in sorted(ratio_by_s3.keys()):
        vals = ratio_by_s3[s]
        if len(vals) >= 10:
            avg = sum(vals) / len(vals)
            print(f"  s3={s:>3}: 平均 s3(T(n))={avg:.2f}, 比率={avg/s:.3f}, サンプル数={len(vals)}")

    # 軌道に沿った s3 の変化
    print("\n--- 代表的な軌道での s3 の推移 ---")
    for start in [27, 31, 97, 871, 6171]:
        seq = collatz_sequence(start)
        s3_seq = [digit_sum_base3(x) for x in seq[:20]]
        print(f"  n={start}: s3列 = {s3_seq}")

    # s3 が不変量かどうかチェック: s3(n) mod k が保存されるか？
    print("\n--- s3(n) mod k が保存されるか？ ---")
    for k in [2, 3, 4, 5, 6]:
        preserved = 0
        total = 0
        for n in range(1, 10000, 2):
            tn = syracuse(n)
            if digit_sum_base3(n) % k == digit_sum_base3(tn) % k:
                preserved += 1
            total += 1
        print(f"  mod {k}: 保存率 = {preserved}/{total} = {100*preserved/total:.1f}%")


# ============================================================
# 解析4: 3-adic的性質
# ============================================================

def analysis_4_three_adic():
    print("\n" + "=" * 70)
    print("解析4: 3-adic的性質")
    print("=" * 70)

    # v3(T(n) - n) の分布: T(n) と n が3-adically近いか？
    print("\n--- v3(T(n) - n) の分布 ---")
    v3_diff = Counter()
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        if tn != n:
            v3_diff[v3(abs(tn - n))] += 1
    for v in sorted(v3_diff.keys())[:10]:
        print(f"  v3(|T(n)-n|) = {v}: {v3_diff[v]} 回")

    # n mod 3^k でのSyracuse写像の決定性
    print("\n--- n mod 3^k で T(n) mod 3^k が一意に決まるか？ ---")
    for k in range(1, 6):
        modulus = 3**k
        # 各剰余類でT(n) mod modulus の値を集める
        tn_by_class = defaultdict(set)
        for n in range(1, 20000, 2):
            tn = syracuse(n)
            tn_by_class[n % modulus].add(tn % modulus)
        non_unique = sum(1 for v in tn_by_class.values() if len(v) > 1)
        total_classes = len(tn_by_class)
        print(f"  mod 3^{k}={modulus:>5}: {total_classes} クラス中 {non_unique} が非一意")

    # v3(3n+1) は常に0 (3n+1 ≡ 1 mod 3 なので)
    # 代わりに v3(T(n)) の分布
    print("\n--- v3(T(n)) の分布 ---")
    v3_tn = Counter()
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        v3_tn[v3(tn)] += 1
    for v in sorted(v3_tn.keys())[:6]:
        print(f"  v3(T(n)) = {v}: {v3_tn[v]} 回 ({100*v3_tn[v]/5000:.1f}%)")

    # 3-adic距離 |T(n) - n|_3 の分布
    print("\n--- 3-adic距離でT(n)がnに近い割合 (v3(T(n)-n) >= threshold) ---")
    for threshold in [1, 2, 3, 4]:
        count = 0
        total = 0
        for n in range(3, 10000, 2):
            tn = syracuse(n)
            if tn != n and v3(abs(tn - n)) >= threshold:
                count += 1
            total += 1
        print(f"  v3 >= {threshold}: {count}/{total} = {100*count/total:.1f}%")


# ============================================================
# 解析5: (2,3)-adic 同時解析 (CRT: mod 6^k)
# ============================================================

def analysis_5_two_three_adic():
    print("\n" + "=" * 70)
    print("解析5: (2,3)-adic 同時解析 — mod 6^k")
    print("=" * 70)

    # mod 6^k での Syracuse 写像の構造
    for k in range(1, 5):
        modulus = 6**k
        print(f"\n--- mod 6^{k} = {modulus} での Syracuse写像 ---")

        # 各奇数剰余類での T(n) mod modulus
        tn_map = defaultdict(set)
        for n in range(1, max(50000, modulus * 20), 2):
            tn = syracuse(n)
            tn_map[n % modulus].add(tn % modulus)

        # 一意に決まるクラス
        unique_classes = [(r, list(v)[0]) for r, v in tn_map.items() if len(v) == 1 and r % 2 == 1]
        non_unique = [(r, v) for r, v in tn_map.items() if len(v) > 1 and r % 2 == 1]

        odd_classes = [r for r in tn_map if r % 2 == 1]
        print(f"  奇数剰余類: {len(odd_classes)}, 一意決定: {len(unique_classes)}, 非一意: {len(non_unique)}")

        if k <= 2:
            for r, targets in sorted(tn_map.items()):
                if r % 2 == 1:
                    if len(targets) == 1:
                        print(f"    {r} → {list(targets)[0]}")
                    else:
                        print(f"    {r} → {sorted(targets)}")

    # v2(3n+1) が n mod 2^k で決まる → 合わせて mod lcm(2^k, 3^j) で解析
    print("\n--- n mod 2^k で v2(3n+1) が決定される仕組み ---")
    for k in range(1, 8):
        modulus = 2**k
        v2_by_class = defaultdict(set)
        for n in range(1, 50000, 2):
            v2_by_class[n % modulus].add(v2(3*n+1))
        unique = sum(1 for v in v2_by_class.values() if len(v) == 1)
        total = len(v2_by_class)
        print(f"  mod 2^{k}={modulus:>4}: {unique}/{total} クラスで v2 一意決定")

    # 混合: n mod 2^a * 3^b での決定性
    print("\n--- n mod (2^a × 3^b) でのSyracuse写像の決定性 ---")
    for a in range(1, 6):
        for b in range(1, 4):
            modulus = (2**a) * (3**b)
            tn_map = defaultdict(set)
            for n in range(1, max(50000, modulus * 30), 2):
                tn = syracuse(n)
                tn_map[n % modulus].add(tn % modulus)
            odd_classes = {r: v for r, v in tn_map.items() if r % 2 == 1}
            unique = sum(1 for v in odd_classes.values() if len(v) == 1)
            total = len(odd_classes)
            if total > 0:
                print(f"  2^{a}×3^{b}={modulus:>5}: 一意 {unique}/{total} ({100*unique/total:.0f}%)")


# ============================================================
# 解析6: 追加 — 3進表現の長さ (対数的性質)
# ============================================================

def analysis_6_length_dynamics():
    print("\n" + "=" * 70)
    print("解析6: 3進桁数(= ⌊log₃ n⌋+1) のダイナミクス")
    print("=" * 70)

    # T(n) の3進桁数 vs n の3進桁数
    len_change = Counter()
    for n in range(1, 10000, 2):
        tn = syracuse(n)
        dn = len(to_base3(n))
        dtn = len(to_base3(tn))
        len_change[dtn - dn] += 1

    print("\n--- 3進桁数の変化 Δlen = len3(T(n)) - len3(n) ---")
    for dl in sorted(len_change.keys()):
        c = len_change[dl]
        print(f"  Δlen = {dl:>+2}: {c:>5} 回 ({100*c/5000:.1f}%)")

    # log_3(T(n)/n) の分布
    print("\n--- log₃(T(n)/n) の統計 ---")
    log_ratios = []
    for n in range(3, 10000, 2):
        tn = syracuse(n)
        log_ratios.append(math.log(tn / n) / math.log(3))

    avg = sum(log_ratios) / len(log_ratios)
    variance = sum((x - avg)**2 for x in log_ratios) / len(log_ratios)
    print(f"  平均: {avg:.6f}")
    print(f"  理論値 (log₃(3/4) ≈ -0.2618): {math.log(3/4)/math.log(3):.6f}")
    print(f"  分散: {variance:.6f}")
    print(f"  標準偏差: {math.sqrt(variance):.6f}")

    # v2(3n+1) ごとの log₃(T(n)/n)
    print("\n--- v2(3n+1) ごとの log₃(T(n)/n) の平均 ---")
    by_v2 = defaultdict(list)
    for n in range(3, 10000, 2):
        tn = syracuse(n)
        v = v2(3*n+1)
        by_v2[v].append(math.log(tn/n) / math.log(3))
    for v_val in sorted(by_v2.keys())[:8]:
        vals = by_v2[v_val]
        avg = sum(vals)/len(vals)
        theory = 1 - v_val * math.log(2)/math.log(3)
        print(f"  v2={v_val}: 平均={avg:.4f}, 理論値 1-{v_val}·log₃2={theory:.4f}, サンプル数={len(vals)}")


# ============================================================
# 解析7: 3進Carry(繰り上がり)の解析
# ============================================================

def analysis_7_carry():
    print("\n" + "=" * 70)
    print("解析7: 3n+1 の3進表現での繰り上がり(carry)パターン")
    print("=" * 70)

    # 3n+1 = 3n の3進左シフト + 1
    # 3n の3進表現は n の末尾に 0 を追加
    # したがって 3n+1 の末尾桁は 1
    # もし n の末尾桁が 0 なら 3n の末尾2桁は 00 → 3n+1 は 01 (carry なし)
    # n の末尾桁が 1 なら 3n は ...10 → 3n+1 は ...11 (carry なし)
    # n の末尾桁が 2 なら 3n は ...20 → 3n+1 は ...21 (carry なし)
    # 実は 3n の末尾は常に 0 だから carry は起きない！
    # → carry は 3n+1 を 2 で割るときに発生

    print("\n  3n+1 の3進表現 = [n の3進表現] + [1] (左端に桁が追加されることなし)")
    print("  → 3進での操作は単純。複雑さは /2^k にある。")

    # /2 の3進表現での効果を調べる
    print("\n--- 偶数 m の m/2 の3進表現での変化 ---")
    print(f"{'m':>8} {'m(b3)':>12} {'m/2':>8} {'m/2(b3)':>12}")
    for m in [4, 10, 16, 22, 28, 34, 40, 46, 52, 58, 100, 112, 256, 1024]:
        if m % 2 == 0:
            print(f"{m:>8} {to_base3(m):>12} {m//2:>8} {to_base3(m//2):>12}")

    # 3進で /2 を行うときの「桁の変化」のパターン
    # m/2 in base 3: これは 3進での「2の逆数を掛ける」操作
    # Z/3^k Z で 2^{-1} ≡ 2 (mod 3), つまり (3+1)/2 の一般化
    print("\n--- 3進での ÷2 操作 (mod 3^k で 2^{-1} を掛ける操作として) ---")
    print("  2^{-1} mod 3 = 2")
    print("  2^{-1} mod 9 = 5")
    print("  2^{-1} mod 27 = 14")
    print("  2^{-1} mod 81 = 41")
    for k in range(1, 8):
        inv2 = pow(2, -1, 3**k)
        print(f"  2^{{-1}} mod 3^{k} = {inv2} = {to_base3(inv2)}₃")

    # T(n) = (3n+1) × 2^{-v2(3n+1)} の3進表現
    # = n の3進左シフト+1 を 2^{-k} 倍 (3-adic的に)
    print("\n--- 3-adicでの 2^{-k} の3進展開パターン ---")
    for k_pow in range(1, 6):
        val = pow(2, -k_pow, 3**8)
        print(f"  2^{{-{k_pow}}} mod 3^8={3**8}: {val} = {to_base3(val)}₃")


# ============================================================
# 解析8: 核心 — 3進表現でのT(n)の明示公式
# ============================================================

def analysis_8_explicit_formula():
    print("\n" + "=" * 70)
    print("解析8: T(n)の3進表現での明示的構造")
    print("=" * 70)

    # T(n) = (3n+1)/2^k where k = v2(3n+1)
    # 3進で見ると: T(n) ≡ (3n+1) × 2^{-k} (mod 3^m)
    # 3n+1 の3進表現 = n₃ × 10₃ + 1₃ = (d_{L}...d₁d₀)₃ || 0₃ + 1₃
    # = d_{L}...d₁d₀ 1₃

    # 実際に T(n) mod 3^m を n mod 3^m から計算
    print("\n--- n mod 3^m → T(n) mod 3^m の写像 (v2 ごとに) ---")
    m = 4
    modulus = 3**m
    by_v2_class = defaultdict(lambda: defaultdict(set))
    for n in range(1, 200000, 2):
        tn = syracuse(n)
        k = v2(3*n+1)
        by_v2_class[k][(n % modulus)].add(tn % modulus)

    for k_val in sorted(by_v2_class.keys())[:5]:
        classes = by_v2_class[k_val]
        unique = sum(1 for v in classes.values() if len(v) == 1)
        total = len(classes)
        print(f"\n  v2={k_val}: {unique}/{total} クラスで T(n) mod {modulus} が一意")
        if k_val <= 3 and total <= 30:
            for r in sorted(classes.keys()):
                targets = classes[r]
                if len(targets) == 1:
                    t = list(targets)[0]
                    # 検証: t ≡ (3r+1) × 2^{-k} (mod 3^m)
                    expected = ((3*r + 1) * pow(2, -k_val, modulus)) % modulus
                    check = "✓" if expected == t else "✗"
                    print(f"    {r:>4} ({to_base3(r):>6}₃) → {t:>4} ({to_base3(t):>6}₃) [公式: {expected:>4}] {check}")

    # 公式の確認: T(n) ≡ (3n+1) · 2^{-v2(3n+1)} (mod 3^m)
    # これは自明だが、v2(3n+1) が n mod 2^k で決まることと合わせると
    # n mod lcm(2^k, 3^m) で T(n) mod 3^m が完全に決定される
    print("\n--- 核心: T(n) mod 3^m は n mod (2^k × 3^m) で完全に決定される ---")
    print("  T(n) ≡ (3n+1) × 2^{-v2(3n+1)} (mod 3^m)")
    print("  v2(3n+1) は n mod 2^k で決定 (k十分大)")
    print("  → n mod (2^K × 3^m) で T(n) mod 3^m が決定")

    for m_val in range(1, 5):
        for K in range(1, 8):
            modulus_3 = 3**m_val
            modulus_full = (2**K) * modulus_3
            tn_map = defaultdict(set)
            for n in range(1, max(100000, modulus_full * 30), 2):
                tn = syracuse(n)
                tn_map[n % modulus_full].add(tn % modulus_3)
            odd_classes = {r: v for r, v in tn_map.items() if r % 2 == 1}
            unique = sum(1 for v in odd_classes.values() if len(v) == 1)
            total = len(odd_classes)
            if total > 0 and unique == total:
                print(f"  3^{m_val}={modulus_3}, 2^{K}={2**K}: 完全決定! (mod {modulus_full}, {total}クラス)")
                break


# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":
    analysis_1_digit_transition()
    analysis_2_shift_interpretation()
    analysis_3_digit_sum()
    analysis_4_three_adic()
    analysis_5_two_three_adic()
    analysis_6_length_dynamics()
    analysis_7_carry()
    analysis_8_explicit_formula()

    print("\n" + "=" * 70)
    print("全解析完了")
    print("=" * 70)
