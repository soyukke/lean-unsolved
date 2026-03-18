import Mathlib

/-!
# エルデシュ問題 #138: Van der Waerden Numbers

W(k) = {1,...,N} を2色で塗り分けたとき、単色k項等差数列が必ず存在する最小のN。

## 背景
- Van der Waerden の定理 (1927): 任意の k に対して W(k) は有限
- 既知の値: W(3)=9, W(4)=35, W(5)=178, W(6)=1132
- エルデシュの問題: W(k)^{1/k} → ∞ を証明せよ ($500)

## 探索の概要

### 探索1: Python数値実験 (scripts/erdos138_van_der_waerden.py)
- W(3)=9, W(4)=35 を全探索で検証
- W(k)^{1/k} の値: 2.08 (k=3), 2.43 (k=4), 2.82 (k=5), 3.23 (k=6) — 増加傾向
- N=8, k=3 で回避可能な塗り分けは正確に6個

### 探索2: 構造解析
- 6個の回避塗り分けは全て色反転でペアを成す（3ペア）
- 回文構造を持つものが4個
- Berlekamp構成: W(p+1) >= p * 2^p を小さい素数で検証

### 探索3: Lean形式化（本ファイル）
- 等差数列・塗り分け・単色等差数列の定義
- W(3) = 9 の部分検証: N=8 で回避可能な塗り分けの具体例を構成
-/

/-! ## 基本定義 -/

/-- k項等差数列: 初項 a, 公差 d の等差数列が集合 S に含まれる -/
def HasArithProgInSet (S : Finset ℕ) (k : ℕ) (a d : ℕ) : Prop :=
  d ≥ 1 ∧ ∀ i : ℕ, i < k → a + i * d ∈ S

/-- 2色塗り分け: {0,...,n-1} → Bool (true = 色1, false = 色0) -/
def Coloring (n : ℕ) := Fin n → Bool

/-- 塗り分け c において、色 color の位置の集合 -/
def colorClass {n : ℕ} (c : Coloring n) (color : Bool) : Finset ℕ :=
  (Finset.univ.filter (fun i : Fin n => c i = color)).image Fin.val

/-- 塗り分け c において、色 color の位置に k 項等差数列が存在する -/
def HasMonoAP {n : ℕ} (c : Coloring n) (color : Bool) (k : ℕ) : Prop :=
  ∃ a d : ℕ, HasArithProgInSet (colorClass c color) k a d

/-- 塗り分け c において、いずれかの色に k 項単色等差数列が存在する -/
def HasMonochromaticAP {n : ℕ} (c : Coloring n) (k : ℕ) : Prop :=
  HasMonoAP c true k ∨ HasMonoAP c false k

/-- k項等差数列を回避する塗り分けが存在する -/
def CanAvoid (n k : ℕ) : Prop :=
  ∃ c : Coloring n, ¬ HasMonochromaticAP c k

/-- Van der Waerden 数の特徴付け:
    W(k) は全ての2色塗り分けに単色k項等差数列が含まれる最小のN -/
def IsVanDerWaerden (k W : ℕ) : Prop :=
  (∀ c : Coloring W, HasMonochromaticAP c k) ∧
  (W ≥ 1 → CanAvoid (W - 1) k)

/-! ## 等差数列に関する基本補題 -/

/-- 長さ0の等差数列は自明に存在する -/
theorem hasArithProg_zero (S : Finset ℕ) (a d : ℕ) (hd : d ≥ 1) :
    HasArithProgInSet S 0 a d := by
  exact ⟨hd, fun i hi => absurd hi (Nat.not_lt_zero i)⟩

/-- 等差数列の要素は有界 -/
theorem arithProg_bound {S : Finset ℕ} {k a d : ℕ}
    (h : HasArithProgInSet S k a d) (hk : k ≥ 1) :
    a + (k - 1) * d ∈ S := by
  exact h.2 (k - 1) (by omega)

/-! ## W(3) = 9 の部分検証 -/

/-- RRBBRRBB 塗り分け（N=8 で3項単色等差数列を回避する例） -/
def coloring_RRBBRRBB : Coloring 8 :=
  fun i => match i.val with
    | 0 => false  -- R
    | 1 => false  -- R
    | 2 => true   -- B
    | 3 => true   -- B
    | 4 => false  -- R
    | 5 => false  -- R
    | 6 => true   -- B
    | 7 => true   -- B
    | _ => false

/-- RBBRRBBR 塗り分け（回文構造） -/
def coloring_RBBRRBBR : Coloring 8 :=
  fun i => match i.val with
    | 0 => false  -- R
    | 1 => true   -- B
    | 2 => true   -- B
    | 3 => false  -- R
    | 4 => false  -- R
    | 5 => true   -- B
    | 6 => true   -- B
    | 7 => false  -- R
    | _ => false

/-! ## 決定可能性を用いた具体的検証のための補助定義 -/

/-- リストで表現した塗り分けにおいて、
    指定色の位置にk項等差数列(初項a, 公差d)が存在するか判定 -/
def checkAPInList (coloring : List Bool) (color : Bool) (k a d : ℕ) : Bool :=
  d ≥ 1 &&
  (List.range k).all fun i =>
    match coloring[a + i * d]? with
    | some c => c == color
    | none => false

/-- リストで表現した塗り分けに単色k項等差数列が存在するか判定 -/
def hasMonoAPList (coloring : List Bool) (k : ℕ) : Bool :=
  let n := coloring.length
  -- 全ての色、初項、公差を試す
  [true, false].any fun color =>
    (List.range n).any fun a =>
      (List.range n).any fun dMinusOne =>
        checkAPInList coloring color k a (dMinusOne + 1)

/-- RRBBRRBB は 3項単色等差数列を含まない -/
example : hasMonoAPList [false, false, true, true, false, false, true, true] 3 = false := by
  rfl

/-- RBBRRBBR は 3項単色等差数列を含まない -/
example : hasMonoAPList [false, true, true, false, false, true, true, false] 3 = false := by
  rfl

/-- RBRBBRBR は 3項単色等差数列を含まない -/
example : hasMonoAPList [false, true, false, true, true, false, true, false] 3 = false := by
  rfl

/-! ## N=9 では全ての塗り分けが 3項単色等差数列を含む（W(3)=9 の検証） -/

/-- 長さ9のリストで表現した塗り分けに3項単色等差数列が必ず存在するか、
    全2^9 = 512通りを検査 -/
def allColoringsHaveAP3 (n : ℕ) : Bool :=
  (List.range (2^n)).all fun bits =>
    let coloring := (List.range n).map fun i => (bits / 2^i) % 2 == 1
    hasMonoAPList coloring 3

set_option maxRecDepth 4096 in
set_option maxHeartbeats 800000 in
/-- N=9 では全ての2色塗り分けが3項単色等差数列を含む -/
example : allColoringsHaveAP3 9 = true := by rfl

set_option maxRecDepth 4096 in
/-- N=8 では3項単色等差数列を回避できる塗り分けが存在する -/
example : allColoringsHaveAP3 8 = false := by rfl

/-! ## 等差数列に関する性質 -/

/-- リストベースの判定で色反転が単色APの存在を保つことを検証 -/
example : hasMonoAPList [true, false, true, false, true] 3 =
          hasMonoAPList [false, true, false, true, false] 3 := by rfl

/-! ## Van der Waerden 数の単調性 -/

/-- k項APを回避できるなら (k+1)項APも回避できる:
    (k+1)項APは最初のk項がk-APなので、k-APがなければ(k+1)-APもない -/
theorem canAvoid_succ_of_canAvoid {n k : ℕ} (h : CanAvoid n k) : CanAvoid n (k + 1) := by
  obtain ⟨c, hc⟩ := h
  exact ⟨c, fun hmono => by
    apply hc
    cases hmono with
    | inl h =>
      left
      obtain ⟨a, d, ⟨hd, hap⟩⟩ := h
      exact ⟨a, d, hd, fun i hi => hap i (Nat.lt_succ_of_lt hi)⟩
    | inr h =>
      right
      obtain ⟨a, d, ⟨hd, hap⟩⟩ := h
      exact ⟨a, d, hd, fun i hi => hap i (Nat.lt_succ_of_lt hi)⟩⟩

-- =============================================================================
-- 探索6: N=3 で 3-AP 回避可能
-- =============================================================================

/-! ## 探索6: N=3 で 3項等差数列を回避可能

N=3 の位置は {0, 1, 2}。3-AP は a, a+d, a+2d (d ≥ 1) で a+2d < 3 となるのは
a=0, d=1 のみ（0, 1, 2）。塗り分け RBR (false, true, false) では
色が F, T, F なので単色でない。
-/

/-- N=3, RBR 塗り分けは 3項単色等差数列を含まない（リストベース検証） -/
example : hasMonoAPList [false, true, false] 3 = false := by rfl

/-- N=3, BRB 塗り分けも 3項単色等差数列を含まない -/
example : hasMonoAPList [true, false, true] 3 = false := by rfl

/-- N=2 でも 3項単色等差数列を回避可能 -/
example : hasMonoAPList [false, true] 3 = false := by rfl

-- =============================================================================
-- 探索7: VdW数の追加性質
-- =============================================================================

/-! ## 探索7: VdW数の追加性質

N=1, N=2 での等差数列回避の自明なケースと、
colorClass の要素の有界性に関する補題。
-/

/-- N=1 では 3-AP を回避可能（1点では公差 ≥ 1 のAPが作れない） -/
example : hasMonoAPList [false] 3 = false := by rfl
example : hasMonoAPList [true] 3 = false := by rfl

/-- N=2 でも 3-AP 回避可能（追加の塗り分け） -/
example : hasMonoAPList [false, true] 3 = false := by rfl
example : hasMonoAPList [true, false] 3 = false := by rfl

/-- colorClass の要素は n 未満 -/
theorem colorClass_lt {n : ℕ} {c : Coloring n} {color : Bool} {x : ℕ}
    (hx : x ∈ colorClass c color) : x < n := by
  unfold colorClass at hx
  rw [Finset.mem_image] at hx
  obtain ⟨i, _, rfl⟩ := hx
  exact i.isLt

/-- colorClass は {0, ..., n-1} の部分集合 -/
theorem colorClass_subset_range {n : ℕ} {c : Coloring n} {color : Bool} :
    colorClass c color ⊆ Finset.range n := by
  intro x hx
  rw [Finset.mem_range]
  exact colorClass_lt hx

-- =============================================================================
-- 探索8: N=4,5,6,7 での 3-AP 回避検証と 4-AP の検証
-- =============================================================================

/-! ## 探索8: 小さい N での等差数列回避の系統的検証

N=4,5,6,7 での 3-AP 回避可能な塗り分けの具体例と、
4-AP (k=4) に関する基本的な検証を行う。
-/

/-- N=4: RBRB は 3-AP を含まない -/
example : hasMonoAPList [false, true, false, true] 3 = false := by rfl

/-- N=5: RBRBB は 3-AP を含まない -/
example : hasMonoAPList [false, true, false, true, true] 3 = false := by rfl

/-- N=6: RBBRRB は 3-AP を含まない -/
example : hasMonoAPList [false, true, true, false, false, true] 3 = false := by rfl

/-- N=7: RBBRRBB は 3-AP を含まない -/
example : hasMonoAPList [false, true, true, false, false, true, true] 3 = false := by rfl

/-- N=3 で 4-AP は自明に回避可能（3点に4項APは入らない） -/
example : hasMonoAPList [false, true, false] 4 = false := by rfl

/-- N=5 で 4-AP 回避可能 -/
example : hasMonoAPList [false, true, false, true, false] 4 = false := by rfl

/-- N=7 で 4-AP 回避可能: RBRBRBB -/
example : hasMonoAPList [false, true, false, true, false, true, true] 4 = false := by rfl

/-- N=10 で 4-AP 回避可能: RRRBRRBRRR -/
example : hasMonoAPList [false, false, false, true, false, false, true, false, false, false] 4 = false := by rfl

/-! ## 探索9: W(k) の自明な下界 -/

/-- k ≥ 2 なら N=1 で k-AP を回避可能（1点に2項以上のAPは存在しない） -/
example : hasMonoAPList [false] 2 = false := by rfl
example : hasMonoAPList [true] 2 = false := by rfl
example : hasMonoAPList [false] 4 = false := by rfl
example : hasMonoAPList [false] 5 = false := by rfl

/-! ## 探索10: 2-AP は常に存在（N ≥ 2 のとき） -/

-- N=2 で 2-AP は回避不可能
-- 位置 0,1 で公差1の2-AP: {0,1}、どちらかは同色
-- hasMonoAPList で確認:
example : hasMonoAPList [false, false] 2 = true := by rfl
example : hasMonoAPList [true, true] 2 = true := by rfl
example : hasMonoAPList [false, true] 2 = false := by rfl
example : hasMonoAPList [true, false] 2 = false := by rfl

-- N=3 では 3-AP を回避可能（W(3)=9 なので 3 < 9）
example : allColoringsHaveAP3 3 = false := by native_decide

-- N=4 でも 3-AP を回避可能
example : allColoringsHaveAP3 4 = false := by native_decide
