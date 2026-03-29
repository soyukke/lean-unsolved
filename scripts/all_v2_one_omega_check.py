"""
omega の処理能力の確認

omega は線形整数算術 (Presburger arithmetic) を解決する。
2^p, 3^p は変数 p の関数だが、仮説中では具体的な自然数値として扱われる。
つまり omega にとっては a = 2^p, b = 3^p, c = ascentConst p は
ただの自然数の定数/変数であり、以下の問題になる:

仮説:
  hmul: a * n = b * n + c
  hac:  c + a = b
  h32:  b > a
  hn:   n >= 1

omega は a*n, b*n を非線形項として扱えるか?

Lean 4 の omega は:
- 線形算術 (加減算、定数倍) を解く
- a * n (2つの変数の積) は非線形なので、直接は扱えない
- ただし、hmul から 得られる等式を使って omega が解ける場合がある

実際の問題:
  hmul: a * n = b * n + c  ... (1)
  hac:  c + a = b          ... (2)

  (2) より b = c + a, これを (1) に代入:
  a * n = (c + a) * n + c
  a * n = c * n + a * n + c
  0 = c * n + c
  0 = c * (n + 1)

  c >= 1 (h32とhacから), n >= 1 → c*(n+1) >= 2 > 0
  矛盾

omega が a*n を処理できるか?
→ hmul: a*n = b*n + c で、b = c + a (hac から) を代入すると
   a*n = (c+a)*n + c
  これは a*n - a*n = c*n + c つまり 0 = c*(n+1)
  omega は c*n を処理できない可能性がある。

代替戦略:
  hmul: 2^p * n = 3^p * n + ascentConst p
  これは「左辺 < 右辺」を示せばいい。

  hn >= 1, 3^p > 2^p より
  3^p * n >= 3^p >= 2^p + 1 > 2^p * 1 = 2^p (n=1のとき)
  ... いや、もっと単純に:

  hmul を使って:
  2^p * n = 3^p * n + ascentConst p >= 3^p * n + 1
  しかし 2^p * n < 3^p * n (∵ 2^p < 3^p, n >= 1)

  具体的に:
  3^p * n > 2^p * n (∵ 3^p > 2^p, n >= 1)
  3^p * n + ascentConst p > 2^p * n (右辺はさらに大きい)
  しかし hmul は 2^p * n = 3^p * n + ascentConst p

  omega で解けるか?
  仮説を全部 omega に渡すと:
  - hmul: 2^p * n = 3^p * n + ascentConst p
  - h32: 3^p > 2^p  (つまり 3^p >= 2^p + 1)
  - hac: ascentConst p + 2^p = 3^p
  - hn: n >= 1

  変数: n, 2^p, 3^p, ascentConst p (それぞれ独立な自然数変数として)
  ただし2^p * n は非線形... omegaは掛け算を処理できない。

  つまり nlinarith か linarith が必要かもしれない。
"""

def check_nlinarith():
    print("=== nlinarith/linarith 分析 ===\n")

    print("仮説 (omega/linarith が見る形):")
    print("  hmul : 2^p * n = 3^p * n + ascentConst p")
    print("  hac  : ascentConst p + 2^p = 3^p")
    print("  h32  : 3^p > 2^p")
    print("  hn   : n >= 1")
    print()

    print("omega の場合:")
    print("  2^p, 3^p, n の積を含むため、直接は無理")
    print("  しかし omega は Nat 上の等式をパターンで処理する場合がある")
    print()

    print("linarith の場合:")
    print("  hmul: 2^p * n = 3^p * n + ascentConst p")
    print("  これは (3^p - 2^p) * n + ascentConst p = 0 と同値（整数上）")
    print("  自然数上では、右辺 > 左辺 を示す必要がある")
    print("  linarith は積の項を扱えない")
    print()

    print("nlinarith の場合:")
    print("  非線形算術を扱える")
    print("  h32 * hn: 3^p * 1 > 2^p * 1 → 3^p > 2^p")
    print("  h32 を n 倍: (3^p - 2^p) * n >= (3^p - 2^p) * 1 >= 1")
    print("  つまり 3^p * n >= 2^p * n + 1")
    print("  よって 3^p * n + ascentConst p >= 2^p * n + 1 + ascentConst p > 2^p * n")
    print("  hmul と矛盾 → nlinarith で閉じる")
    print()

    print("=== 推奨される証明コード (改訂版) ===\n")
    print("""
-- 方法A: omega のみ (動くかは検証が必要)
theorem no_all_v2_one_cycle_v1 (n p : Nat) (hn : n >= 1) (hodd : n % 2 = 1)
    (hp : p >= 1) (hasc : consecutiveAscents n p)
    (hcycle : syracuseIter p n = n) : False := by
  have hmul := syracuse_iter_mul_formula n p hn hodd hasc
  rw [hcycle] at hmul
  have hac := ascentConst_add_two_pow p
  have h32 : 3 ^ p > 2 ^ p := by
    have := ascentConst_add_two_pow p
    suffices ascentConst p >= 1 by omega
    induction p with
    | zero => omega
    | succ k _ => simp only [ascentConst]; have := Nat.one_le_pow k 2 (by omega); omega
  -- ここが問題: omega は a*n を処理できるか?
  omega  -- これが失敗する可能性あり

-- 方法B: 手動で不等式を構成 (確実)
theorem no_all_v2_one_cycle_v2 (n p : Nat) (hn : n >= 1) (hodd : n % 2 = 1)
    (hp : p >= 1) (hasc : consecutiveAscents n p)
    (hcycle : syracuseIter p n = n) : False := by
  have hmul := syracuse_iter_mul_formula n p hn hodd hasc
  rw [hcycle] at hmul
  -- hmul : 2^p * n = 3^p * n + ascentConst p
  have hac := ascentConst_add_two_pow p
  -- hac : ascentConst p + 2^p = 3^p
  -- hac より: 3^p * n = (ascentConst p + 2^p) * n = ascentConst p * n + 2^p * n
  have hexpand : 3 ^ p * n = ascentConst p * n + 2 ^ p * n := by
    have : 3 ^ p = ascentConst p + 2 ^ p := by linarith
    linarith [Nat.mul_comm (ascentConst p + 2 ^ p) n,
              show (ascentConst p + 2 ^ p) * n = ascentConst p * n + 2 ^ p * n from by ring]
  -- hmul に代入: 2^p * n = ascentConst p * n + 2^p * n + ascentConst p
  rw [hexpand] at hmul
  -- hmul : 2^p * n = ascentConst p * n + 2^p * n + ascentConst p
  -- 0 = ascentConst p * n + ascentConst p = ascentConst p * (n + 1)
  -- ascentConst p >= 1, n >= 1 なので矛盾
  have hac_pos : ascentConst p >= 1 := by
    induction p with
    | zero => omega
    | succ k _ => simp only [ascentConst]; have := Nat.one_le_pow k 2 (by omega); omega
  omega

-- 方法C: linarith のみ (最もエレガント、動く可能性が高い)
theorem no_all_v2_one_cycle_v3 (n p : Nat) (hn : n >= 1) (hodd : n % 2 = 1)
    (hp : p >= 1) (hasc : consecutiveAscents n p)
    (hcycle : syracuseIter p n = n) : False := by
  have hmul := syracuse_iter_mul_formula n p hn hodd hasc
  rw [hcycle] at hmul
  -- hmul : 2 ^ p * n = 3 ^ p * n + ascentConst p
  -- 右辺 > 左辺 を示す
  have hac := ascentConst_add_two_pow p
  -- hac : ascentConst p + 2 ^ p = 3 ^ p
  -- つまり 3 ^ p * n = (ascentConst p + 2 ^ p) * n
  --                    = ascentConst p * n + 2 ^ p * n
  -- 従って 右辺 = ascentConst p * n + 2^p * n + ascentConst p
  --             > 2^p * n = 左辺
  have hac_pos : ascentConst p >= 1 := by
    induction p with
    | zero => omega
    | succ k _ => simp only [ascentConst]; have := Nat.one_le_pow k 2 (by omega); omega
  -- 3^p * n + ascentConst p
  -- = (ascentConst p + 2^p) * n + ascentConst p   [hac]
  -- = ascentConst p * n + 2^p * n + ascentConst p
  -- >= 1 * 1 + 2^p * n + 1                         [hac_pos, hn]
  -- = 2^p * n + 2
  -- > 2^p * n
  -- しかし hmul は 2^p * n = ... なので矛盾
  nlinarith [Nat.mul_le_mul_right n hac.symm.le]
""")

    print("\n=== 最終推奨 ===")
    print()
    print("方法B が最も安全。omega は Nat 上の a*n の等式を")
    print("処理できる可能性が高い（Lean 4 の omega は Nat.mul を")
    print("展開できる場合がある）が、明示的に展開しておく方が確実。")
    print()
    print("方法C (nlinarith) も有力。非線形算術を直接扱える。")
    print()
    print("実際にはどちらも試して動く方を採用する設計にすべき。")


if __name__ == "__main__":
    check_nlinarith()
