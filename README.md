# lean-unsolved

Formal exploration of unsolved problems in mathematics using **Lean 4** and **Mathlib**.

All proofs are `sorry`-free.

## Problems

| Problem | Explorations | Lean files | Status |
|---------|-------------|------------|--------|
| Collatz conjecture | 85+ | 11 | Active |
| Goldbach's conjecture | 27 | 1 | Active |
| Twin prime conjecture | 24 | 1 | Active |
| Erdos #89 (Distinct distances) | 21 | 1 | Active |
| Erdos #52 (Sum-product) | 16 | 1 | Active |
| Erdos #20 (Sunflower) | 15 | 1 | Active |
| Erdos #77 (Ramsey limits) | 14 | 1 | Active |
| Erdos #138 (Van der Waerden) | 13 | 1 | Active |
| Schur numbers | - | 1 | Active |

## Key results (Collatz)

- General formula: `2^k * T^k(n) = 3^k * n + (3^k - 2^k)`
- Cycle exclusion via Baker's theorem
- Hensel attrition for k=1..4
- mod 32 residue class elimination
- v2 distribution: `P(v2=j) = 1/2^j` (rigorous proof)
- Cramer rate function: `I(0) = 0.055` (divergence probability decays exponentially)

## Build

```bash
lake build
```

Requires Lean 4 v4.29.0-rc4 and Mathlib v4.29.0-rc4.

## Structure

```
Unsolved/           # Lean source files
  Collatz.lean      # Core definitions (Syracuse function, etc.)
  Collatz*.lean     # Collatz-related proofs
  Goldbach.lean     # Goldbach conjecture
  TwinPrime.lean    # Twin prime conjecture
  Erdos*.lean       # Erdos problems
  Schur.lean        # Schur numbers
  explorations/     # Exploration logs and queue
scripts/            # Python computational experiments
```

## License

Apache-2.0
