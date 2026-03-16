#!/usr/bin/env python3
"""
探索24 補足: s3(n) mod 2 = n mod 2 の証明と帰結の整理
"""

def s3(n):
    s = 0
    while n > 0:
        s += n % 3
        n //= 3
    return s

def to_base3(n):
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    return ''.join(reversed(digits))

def syracuse(n):
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def v2(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v

print("=" * 70)
print("s3(n) mod 2 = n mod 2 の証明")
print("=" * 70)

print("""
■ 定理: 全ての正整数 n に対して s3(n) ≡ n (mod 2)

証明:
  n の3進展開を n = Σ d_i * 3^i とする。

  s3(n) = Σ d_i  (d_i ∈ {0, 1, 2})

  一方 n = Σ d_i * 3^i ≡ Σ d_i * 1^i = Σ d_i = s3(n)  (mod 2)

  なぜなら 3 ≡ 1 (mod 2) だから 3^i ≡ 1 (mod 2) for all i.

  よって n ≡ s3(n) (mod 2).  □
""")

# 検証
match = 0
for n in range(1, 100001):
    if n % 2 == s3(n) % 2:
        match += 1
print(f"検証: n=1..100000 で n mod 2 = s3(n) mod 2: {match}/100000")

print("\n" + "=" * 70)
print("帰結: 奇数の s3 は常に奇数")
print("=" * 70)
print("""
n が奇数 → n ≡ 1 (mod 2) → s3(n) ≡ 1 (mod 2)
n が偶数 → n ≡ 0 (mod 2) → s3(n) ≡ 0 (mod 2)

したがって:
- 全ての奇数 n で s3(n) mod 2 = 1
- 全ての偶数 n で s3(n) mod 2 = 0
- s3(n) mod 2 = 0 の奇数は存在しない
""")

# 検証
odd_with_even_s3 = [n for n in range(1, 100001, 2) if s3(n) % 2 == 0]
print(f"s3(n) mod 2 = 0 の奇数 (n=1..100000): {len(odd_with_even_s3)} 個")

print("\n" + "=" * 70)
print("Syracuse写像での保存の証明")
print("=" * 70)
print("""
■ 定理: 奇数 n に対して s3(T(n)) ≡ s3(n) (mod 2)

証明:
  s3(n) ≡ n (mod 2) が全ての正整数で成立する。

  T(n) は奇数（Syracuse写像の像は常に奇数）。

  よって s3(T(n)) ≡ T(n) ≡ 1 (mod 2)  [T(n) は奇数だから]
  かつ   s3(n) ≡ n ≡ 1 (mod 2)        [n は奇数だから]

  したがって s3(T(n)) ≡ 1 ≡ s3(n) (mod 2).  □
""")

print("つまり、s3(n) mod 2 がSyracuse写像の不変量であるのは")
print("「奇数の桁和は奇数」という自明な事実の帰結にすぎない！")

print("\n" + "=" * 70)
print("一般化: s_b(n) mod (b-1) と n mod (b-1)")
print("=" * 70)
print("""
同様の議論: b進桁和 s_b(n) について
  n = Σ d_i * b^i ≡ Σ d_i * 1^i = s_b(n)  (mod b-1)

なぜなら b ≡ 1 (mod b-1).

これは有名な事実: 「9で割った余り = 十進桁和を9で割った余り」の一般化。
- b=10: s_{10}(n) ≡ n (mod 9)  ← 「9の倍数判定法」
- b=3:  s_3(n) ≡ n (mod 2)    ← 今回の事実
""")

# 追加検証: s3(2^k * q) の分析
print("=" * 70)
print("補足: s3(2^k * q) ≡ 2^k * q ≡ 0 * q = 0 (mod 2) when k >= 1")
print("=" * 70)
print("""
セクション12の結果「s3(2^k * q) - s3(q) mod 2 = 1 が常に成立（q奇数）」の説明:

q が奇数 → s3(q) ≡ q ≡ 1 (mod 2)
2^k * q は偶数（k >= 1）→ s3(2^k * q) ≡ 2^k * q ≡ 0 (mod 2)

差: s3(2^k * q) - s3(q) ≡ 0 - 1 = 1 (mod 2)

つまり差が常に奇数なのは単に「偶数 - 奇数 = 奇数」という事実。
""")

print("=" * 70)
print("セクション10の再解釈: フリップ回数が常に奇数な理由")
print("=" * 70)
print("""
m = 3n+1 は偶数 → s3(m) ≡ 0 (mod 2)
T(n) = m/2^k は奇数 → s3(T(n)) ≡ 1 (mod 2)

s3 mod 2 が 0 から 1 に変わる = フリップ回数は奇数

これは v2 の値やフリップの詳細構造とは無関係で、
単に「偶数から奇数になる」という事実から従う。
""")

print("\n" + "=" * 70)
print("最終結論")
print("=" * 70)
print("""
============================================================
定理: 奇数 n に対して s3(T(n)) ≡ s3(n) (mod 2)
============================================================

証明は完全に初等的:

1. s3(n) ≡ n (mod 2) （b進桁和の基本性質: b ≡ 1 mod (b-1) より）
2. T(n) は奇数（Syracuse写像の定義より）
3. n は奇数（前提）
4. よって s3(T(n)) ≡ 1 ≡ s3(n) (mod 2)

この不変量は自明（trivial）: 奇数から奇数への写像で、
「奇数の3進桁和は奇数」という事実を述べているだけ。

コラッツ予想への含意:
- この不変量は新しい情報を一切提供しない
- 奇数全体で s3 mod 2 = 1 が成立するため、
  軌道を制限する力はゼロ
- 探索20で発見された「100%保存」は正しいが、
  自明な理由による

注意: s3(n) mod 2 以外の不変量（例えば s3(n) mod 3 など）
が非自明に保存されるかは別問題として興味深い。
""")

# s3(n) mod 3 は保存されるか？
print("=" * 70)
print("発展: s3(n) mod 3 は Syracuse で保存されるか？")
print("=" * 70)

from collections import Counter
transitions = Counter()
for n in range(1, 200001, 2):
    tn = syracuse(n)
    transitions[(s3(n) % 3, s3(tn) % 3)] += 1

print("\ns3(n) mod 3 の遷移:")
for (a, b) in sorted(transitions.keys()):
    print(f"  s3(n) mod 3 = {a} → s3(T(n)) mod 3 = {b}: {transitions[(a,b)]} 件")

preserve3 = sum(v for (a, b), v in transitions.items() if a == b)
total3 = sum(transitions.values())
print(f"\n保存率: {preserve3}/{total3} ({100*preserve3/total3:.2f}%)")
print("→ s3(n) mod 3 は保存されない（非自明な写像あり）")

# s3(n) mod 4 は？（s3(n) ≡ n mod 2 だが mod 4 では？）
print("\n" + "=" * 70)
print("発展: s3(n) mod 4 は Syracuse で保存されるか？")
print("=" * 70)

transitions4 = Counter()
for n in range(1, 200001, 2):
    tn = syracuse(n)
    transitions4[(s3(n) % 4, s3(tn) % 4)] += 1

print("\ns3(n) mod 4 の遷移:")
for (a, b) in sorted(transitions4.keys()):
    print(f"  s3(n) mod 4 = {a} → s3(T(n)) mod 4 = {b}: {transitions4[(a,b)]} 件")

preserve4 = sum(v for (a, b), v in transitions4.items() if a == b)
total4 = sum(transitions4.values())
print(f"\n保存率: {preserve4}/{total4} ({100*preserve4/total4:.2f}%)")

# n mod 2 自体がSyracuseの不変量であることの確認
print("\n" + "=" * 70)
print("参考: n mod 2 は Syracuse で保存されるか？（当然）")
print("=" * 70)
preserve_mod2 = sum(1 for n in range(1, 200001, 2) if syracuse(n) % 2 == n % 2)
total_mod2 = sum(1 for _ in range(1, 200001, 2))
print(f"n mod 2 保存: {preserve_mod2}/{total_mod2} ({100*preserve_mod2/total_mod2:.2f}%)")
print("→ T(n) は常に奇数を返すので n mod 2 は自明に保存される")
