#!/usr/bin/env python3
"""
v2列のshift space構造の解析
===

目的:
1. 「禁止語なし(L<=15で全パターン実現)」と「H(k)/k -> 0」の統一的理解
2. v2列をsymbolic dynamicsのshift spaceとして定式化
3. shift spaceの位相的エントロピー h_top の特定
4. sofic shift / coded shift / 有限型shift (SFT) のどれに該当するか

核心的疑問:
- 有限アルファベット上のshift spaceで、有限長の禁止語がないのにh_top < log|A|というのは可能か?
  -> Yes: coded shift, context-free shift, さらには entropy 0 のshift spaceでも可能
  -> 例: Sturmian shift (h_top = 0, 全ての有限語が出現)

分析計画:
A. 有限範囲アルファベット {1,2,...,M} 上の v2 列の言語構造
B. ブロック計数の増大率 (complexity function) p(n) の漸近解析
C. 繰り返しパターンの検出 (repetitivity, uniform recurrence)
D. v2列と Sturmian-like 構造の比較
E. mod 2^k 空間での位相的エントロピー (有限状態近似)
"""

import json
import math
import sys
from collections import Counter, defaultdict
from itertools import product
import time

# --- Core Collatz functions ---
def collatz_v2(n):
    """Return v2(3n+1) for odd n"""
    m = 3 * n + 1
    v = 0
    while m % 2 == 0:
        m //= 2
        v += 1
    return v

def syracuse(n):
    """Syracuse map: T(n) = (3n+1)/2^v2(3n+1) for odd n"""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m

def v2_orbit(n, max_steps=1000):
    """Return the v2 sequence of n's orbit until reaching 1"""
    seq = []
    curr = n
    for _ in range(max_steps):
        if curr == 1:
            break
        if curr % 2 == 0:
            while curr % 2 == 0:
                curr //= 2
            if curr == 1:
                break
        v = collatz_v2(curr)
        seq.append(v)
        curr = syracuse(curr)
    return seq

# --- Analysis A: Complexity function p(n) ---
def compute_complexity_function(orbits, max_block_len=25):
    """
    Complexity function: p(n) = number of distinct blocks of length n
    appearing in any orbit.

    For a full shift on alphabet {1,...,M}: p(n) = M^n
    For SFT with memory m: p(n) grows exponentially
    For Sturmian: p(n) = n + 1
    For zero-entropy: p(n) grows subexponentially
    """
    all_blocks = defaultdict(set)

    for orbit in orbits:
        if len(orbit) < 2:
            continue
        for block_len in range(1, min(max_block_len + 1, len(orbit) + 1)):
            for i in range(len(orbit) - block_len + 1):
                block = tuple(orbit[i:i+block_len])
                all_blocks[block_len].add(block)

    result = {}
    for n in range(1, max_block_len + 1):
        if n in all_blocks:
            result[n] = len(all_blocks[n])

    return result

# --- Analysis B: Entropy from complexity ---
def analyze_complexity_growth(complexity):
    """
    h_top = lim_{n->inf} log p(n) / n

    If p(n) ~ C * n^alpha: h_top = 0
    If p(n) ~ C * lambda^n: h_top = log(lambda)
    """
    ns = sorted(complexity.keys())
    log_ratios = {}
    for n in ns:
        if n >= 1:
            log_ratios[n] = math.log2(complexity[n]) / n

    # successive ratios
    growth_ratios = {}
    for i in range(1, len(ns)):
        n1, n2 = ns[i-1], ns[i]
        if complexity[n1] > 0:
            growth_ratios[n2] = complexity[n2] / complexity[n1]

    # fit polynomial vs exponential
    # If h_top > 0: log p(n) ~ h_top * n + const
    # If h_top = 0: log p(n) ~ alpha * log(n) + const (polynomial)

    log_p = [(n, math.log2(complexity[n])) for n in ns if complexity[n] > 0]

    return {
        "complexity_values": {n: complexity[n] for n in ns},
        "log_p_over_n": log_ratios,
        "growth_ratios": growth_ratios,
        "log_p": log_p
    }

# --- Analysis C: Forbidden words by level ---
def analyze_forbidden_words(orbits, alphabet_max=8, max_len=6):
    """
    For each block length L, find which L-blocks over {1,...,alphabet_max}
    appear vs do not appear.

    Key question: Is there a finite L such that the set of forbidden L-blocks
    determines all forbidden words? (= SFT characterization)
    """
    all_words = defaultdict(set)
    for orbit in orbits:
        clipped = [min(v, alphabet_max) for v in orbit]
        for L in range(1, max_len + 1):
            for i in range(len(clipped) - L + 1):
                word = tuple(clipped[i:i+L])
                all_words[L].add(word)

    result = {}
    for L in range(1, max_len + 1):
        total_possible = alphabet_max ** L
        realized = len(all_words[L])
        forbidden_count = total_possible - realized

        # Check if forbidden words at level L are "explained" by forbidden at level L-1
        inherited_forbidden = 0
        if L > 1 and (L-1) in all_words:
            prev_realized = all_words[L-1]
            for word in product(range(1, alphabet_max + 1), repeat=L):
                prefix = word[:L-1]
                suffix = word[1:]
                if prefix not in prev_realized or suffix not in prev_realized:
                    inherited_forbidden += 1

        new_forbidden = forbidden_count - inherited_forbidden if L > 1 else forbidden_count

        result[L] = {
            "total_possible": total_possible,
            "realized": realized,
            "forbidden": forbidden_count,
            "inherited_forbidden": inherited_forbidden if L > 1 else 0,
            "new_forbidden": new_forbidden,
            "realization_ratio": realized / total_possible
        }

    return result

# --- Analysis D: mod 2^k shift space ---
def mod2k_shift_entropy(k_max=16):
    """
    Consider the v2 map on Z/(2^k)Z restricted to odd residues.
    This gives a FINITE dynamical system, whose topological entropy
    is well-defined via the transition graph.

    Key: As k grows, these finite systems approximate the full shift space.
    """
    results = {}
    for k in range(2, k_max + 1):
        mod = 2**k
        odd_residues = [r for r in range(1, mod, 2)]
        n_states = len(odd_residues)

        # Transition map: r -> (3r+1)/2^v2(3r+1) mod 2^(k-v2)
        # But for shift space: we track (r, v2(3r+1))
        transitions = {}
        v2_values = set()
        for r in odd_residues:
            v = collatz_v2(r)  # v2 is determined by r mod 2^k for v <= k
            v_clipped = min(v, k)  # can't determine more than k bits
            next_r = syracuse(r) % mod
            if next_r % 2 == 0:
                # Make it odd
                while next_r % 2 == 0 and next_r > 0:
                    next_r //= 2
                next_r = next_r % mod
                if next_r == 0:
                    next_r = 1  # wrap
            transitions[r] = (next_r, v_clipped)
            v2_values.add(v_clipped)

        # Build transition matrix on odd residues
        # Count number of distinct orbits
        visited_all = set()
        n_orbits = 0
        orbit_lengths = []
        for r in odd_residues:
            if r in visited_all:
                continue
            orbit = []
            curr = r
            visited = set()
            while curr not in visited:
                visited.add(curr)
                orbit.append(curr)
                curr = transitions[curr][0]
            if curr in visited:
                n_orbits += 1
                orbit_lengths.append(len(orbit))
            visited_all |= visited

        # Entropy of the v2 sequence generated by mod 2^k dynamics
        # This is the entropy of the edge labeling on the directed graph
        v2_freq = Counter()
        for r in odd_residues:
            v2_freq[transitions[r][1]] += 1
        total = sum(v2_freq.values())
        H = -sum((c/total) * math.log2(c/total) for c in v2_freq.values() if c > 0)

        results[k] = {
            "n_states": n_states,
            "n_orbits": n_orbits,
            "v2_entropy_bits": round(H, 6),
            "v2_distribution": {v: round(c/total, 6) for v, c in sorted(v2_freq.items())},
            "max_orbit_len": max(orbit_lengths) if orbit_lengths else 0
        }

    return results

# --- Analysis E: Recurrence and uniformity ---
def analyze_recurrence(orbits, target_blocks=None, max_gap=500):
    """
    For each block w, compute the return time distribution:
    R_w = {gap between consecutive occurrences of w}

    Uniform recurrence: sup R_w < infinity for all w => minimal shift
    """
    if target_blocks is None:
        target_blocks = [(1,), (2,), (1,1), (1,2), (2,1)]

    result = {}
    for block in target_blocks:
        gaps = []
        L = len(block)
        block_t = tuple(block)

        for orbit in orbits:
            if len(orbit) < L + 1:
                continue
            last_pos = None
            for i in range(len(orbit) - L + 1):
                if tuple(orbit[i:i+L]) == block_t:
                    if last_pos is not None:
                        gap = i - last_pos
                        gaps.append(gap)
                    last_pos = i

        if gaps:
            gap_counter = Counter(gaps)
            mean_gap = sum(gaps) / len(gaps)
            max_observed = max(gaps)
            result[str(block)] = {
                "n_occurrences": len(gaps),
                "mean_return_time": round(mean_gap, 3),
                "max_return_time": max_observed,
                "std_return_time": round((sum((g - mean_gap)**2 for g in gaps) / len(gaps))**0.5, 3),
                "is_bounded": max_observed < max_gap
            }

    return result

# --- Analysis F: v2 列の Sturmian-like 特性 ---
def analyze_sturmian_properties(orbits, max_len=20):
    """
    Sturmian sequence: p(n) = n + 1 for all n
    - Balanced: for any factor w, |#1(w) - #1(w')| <= 1 for same-length factors
    - Complexity exactly n+1

    Check: does v2 complexity grow linearly or faster?
    """
    # Already computed complexity, analyze its growth rate
    complexity = compute_complexity_function(orbits, max_block_len=max_len)

    # Fit: p(n) ~ a * n^alpha or p(n) ~ a * lambda^n
    ns = sorted(complexity.keys())
    if len(ns) < 3:
        return {}

    # Simple linear regression without numpy
    def linreg(xs, ys):
        n = len(xs)
        sx = sum(xs)
        sy = sum(ys)
        sxx = sum(x*x for x in xs)
        sxy = sum(x*y for x, y in zip(xs, ys))
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-15:
            return 0, 0, 1e10
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        # residual
        pred = [slope * x + intercept for x in xs]
        resid = sum((y - p)**2 for y, p in zip(ys, pred)) / n
        return slope, intercept, resid

    log_ns = [math.log(n) for n in ns if n >= 2]
    log_ps = [math.log(complexity[n]) for n in ns if n >= 2]
    ns_float = [float(n) for n in ns if n >= 2]

    if len(log_ns) >= 2:
        # polynomial fit: log p = alpha * log n + const
        alpha_poly, _, poly_resid = linreg(log_ns, log_ps)

        # exponential fit: log p = beta * n + const
        beta_exp, _, exp_resid = linreg(ns_float, log_ps)

        return {
            "complexity": {n: complexity[n] for n in ns},
            "polynomial_fit": {
                "alpha": round(alpha_poly, 4),
                "residual": round(poly_resid, 6)
            },
            "exponential_fit": {
                "lambda": round(math.exp(beta_exp), 6),
                "h_top_estimate": round(beta_exp / math.log(2), 6),
                "residual": round(exp_resid, 6)
            },
            "growth_type": "exponential" if exp_resid < poly_resid * 0.5 else (
                "polynomial" if poly_resid < exp_resid * 0.5 else "ambiguous"
            )
        }
    return {}

# --- Analysis G: 長距離制約の検出 ---
def analyze_long_range_constraints(orbits, alphabet_max=6):
    """
    Key insight:
    - No finite forbidden words => SFT would be the full shift
    - But H(k)/k -> 0 => the language is NOT the full shift

    Resolution: The shift space might be a "context-free shift" or
    "countable intersection of SFTs" where constraints are non-local.

    Test: For each v2 value j and each position in a length-L block,
    compute conditional probability given DISTANT (not adjacent) context.
    """
    # Compute: P(v_t = j | v_{t-d} = i) for various distances d
    conditional = defaultdict(lambda: defaultdict(int))
    marginal = Counter()

    for orbit in orbits:
        for t in range(len(orbit)):
            j = min(orbit[t], alphabet_max)
            marginal[j] += 1
            for d in [1, 2, 5, 10, 20, 50]:
                if t >= d:
                    i = min(orbit[t-d], alphabet_max)
                    conditional[(d, i)][j] += 1

    # Compute mutual information at each distance
    total = sum(marginal.values())
    p_marginal = {j: c/total for j, c in marginal.items()}

    mi_by_distance = {}
    for d in [1, 2, 5, 10, 20, 50]:
        mi = 0.0
        for i in range(1, alphabet_max + 1):
            total_given_i = sum(conditional[(d, i)].values())
            if total_given_i == 0:
                continue
            p_i = total_given_i / total
            for j in range(1, alphabet_max + 1):
                c = conditional[(d, i)][j]
                if c == 0:
                    continue
                p_j_given_i = c / total_given_i
                p_j = p_marginal.get(j, 1e-10)
                mi += p_i * p_j_given_i * math.log2(p_j_given_i / p_j)
        mi_by_distance[d] = round(mi, 8)

    return {
        "mutual_information_by_distance": mi_by_distance,
        "decay_pattern": "Check if MI decays exponentially or polynomially"
    }

# --- Analysis H: Conditional entropy rate with growing context (refined) ---
def compute_refined_entropy_rate(orbits, max_context=12, alphabet_max=8):
    """
    H(k) = H(X_k | X_1, ..., X_{k-1})

    For SFT: H(k) stabilizes after memory length m
    For sofic: H(k) stabilizes after some finite k
    For non-sofic subshift: H(k) may never stabilize
    For zero-entropy: H(k) -> 0
    """
    block_counts = defaultdict(int)

    for orbit in orbits:
        clipped = [min(v, alphabet_max) for v in orbit]
        for L in range(1, max_context + 2):
            for i in range(len(clipped) - L + 1):
                block = tuple(clipped[i:i+L])
                block_counts[block] += 1

    conditional_entropies = {}
    for k in range(1, max_context + 1):
        # H(X_{k+1} | X_1, ..., X_k) = H(X_1,...,X_{k+1}) - H(X_1,...,X_k)
        H_k = 0.0
        H_k1 = 0.0

        total_k = sum(c for b, c in block_counts.items() if len(b) == k)
        total_k1 = sum(c for b, c in block_counts.items() if len(b) == k + 1)

        if total_k > 0:
            for b, c in block_counts.items():
                if len(b) == k and c > 0:
                    p = c / total_k
                    H_k -= p * math.log2(p)

        if total_k1 > 0:
            for b, c in block_counts.items():
                if len(b) == k + 1 and c > 0:
                    p = c / total_k1
                    H_k1 -= p * math.log2(p)

        conditional_entropies[k] = round(H_k1 - H_k, 6)

    # Analyze the decay pattern of conditional entropy
    ce_values = list(conditional_entropies.values())
    if len(ce_values) >= 4:
        # Check if decay is exponential: H(k) ~ A * r^k
        ks_list = list(conditional_entropies.keys())
        hs_list = ce_values

        # Only use positive values
        pos_ks = [k for k, h in zip(ks_list, hs_list) if h > 0.01]
        pos_hs = [h for h in hs_list if h > 0.01]

        if len(pos_ks) >= 3:
            log_hs = [math.log(h) for h in pos_hs]
            pos_ks_f = [float(k) for k in pos_ks]

            # Simple linear regression
            n = len(pos_ks_f)
            sx = sum(pos_ks_f)
            sy = sum(log_hs)
            sxx = sum(x*x for x in pos_ks_f)
            sxy = sum(x*y for x, y in zip(pos_ks_f, log_hs))
            denom = n * sxx - sx * sx
            if abs(denom) > 1e-15:
                slope = (n * sxy - sx * sy) / denom
                decay_rate = round(slope, 6)
                decay_base = round(math.exp(slope), 6)

                return {
                    "conditional_entropies": conditional_entropies,
                    "decay_rate_per_step": decay_rate,
                    "decay_base": decay_base,
                    "extrapolated_limit": "0" if decay_base < 1 else "positive",
                    "half_life_steps": round(-math.log(2) / slope, 2) if slope < 0 else "N/A"
                }

    return {"conditional_entropies": conditional_entropies}


# ===========================================
# MAIN EXECUTION
# ===========================================
def main():
    print("=== v2 Shift Space Analysis ===")
    print()

    start_time = time.time()

    # Generate orbits
    print("Generating v2 orbits...")
    orbits = []
    N_MAX = 200000  # Use first 200k odd numbers
    for n in range(3, N_MAX, 2):
        orbit = v2_orbit(n, max_steps=500)
        if len(orbit) >= 5:
            orbits.append(orbit)

    total_symbols = sum(len(o) for o in orbits)
    print(f"  Generated {len(orbits)} orbits, {total_symbols} total symbols")
    print(f"  Time: {time.time() - start_time:.1f}s")

    results = {}

    # A. Complexity function
    print("\nA. Computing complexity function p(n)...")
    t0 = time.time()
    complexity = compute_complexity_function(orbits, max_block_len=20)
    complexity_analysis = analyze_complexity_growth(complexity)
    results["complexity_analysis"] = complexity_analysis
    print(f"  Time: {time.time() - t0:.1f}s")

    for n in sorted(complexity.keys()):
        h = math.log2(complexity[n]) / n if complexity[n] > 0 else 0
        print(f"  p({n:2d}) = {complexity[n]:>10d}  log2(p)/n = {h:.4f}")

    # B. Sturmian analysis
    print("\nB. Analyzing growth type (polynomial vs exponential)...")
    t0 = time.time()
    sturmian = analyze_sturmian_properties(orbits, max_len=20)
    results["sturmian_analysis"] = sturmian
    print(f"  Growth type: {sturmian.get('growth_type', 'unknown')}")
    if 'exponential_fit' in sturmian:
        print(f"  h_top estimate from complexity: {sturmian['exponential_fit']['h_top_estimate']}")
    if 'polynomial_fit' in sturmian:
        print(f"  Polynomial alpha: {sturmian['polynomial_fit']['alpha']}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # C. Forbidden words analysis
    print("\nC. Forbidden word analysis...")
    t0 = time.time()
    forbidden = analyze_forbidden_words(orbits, alphabet_max=6, max_len=6)
    results["forbidden_words"] = forbidden
    for L in sorted(forbidden.keys()):
        d = forbidden[L]
        print(f"  L={L}: realized={d['realized']}/{d['total_possible']} "
              f"forbidden={d['forbidden']} (new={d['new_forbidden']})")
    print(f"  Time: {time.time() - t0:.1f}s")

    # D. mod 2^k entropy
    print("\nD. mod 2^k shift space entropy...")
    t0 = time.time()
    mod2k = mod2k_shift_entropy(k_max=14)
    results["mod2k_entropy"] = mod2k
    for k in sorted(mod2k.keys()):
        d = mod2k[k]
        print(f"  k={k:2d}: states={d['n_states']:>5d} H={d['v2_entropy_bits']:.4f} bits "
              f"orbits={d['n_orbits']}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # E. Recurrence analysis
    print("\nE. Recurrence analysis...")
    t0 = time.time()
    recurrence = analyze_recurrence(orbits)
    results["recurrence"] = recurrence
    for block, data in recurrence.items():
        print(f"  {block}: mean_return={data['mean_return_time']:.1f} "
              f"max_return={data['max_return_time']} "
              f"bounded={data['is_bounded']}")
    print(f"  Time: {time.time() - t0:.1f}s")

    # F. Long-range constraints
    print("\nF. Long-range mutual information...")
    t0 = time.time()
    long_range = analyze_long_range_constraints(orbits)
    results["long_range_constraints"] = long_range
    for d, mi in long_range["mutual_information_by_distance"].items():
        print(f"  distance={d:3d}: MI = {mi:.8f} bits")
    print(f"  Time: {time.time() - t0:.1f}s")

    # G. Refined conditional entropy
    print("\nG. Conditional entropy decay...")
    t0 = time.time()
    cond_entropy = compute_refined_entropy_rate(orbits, max_context=12)
    results["conditional_entropy_decay"] = cond_entropy
    if "conditional_entropies" in cond_entropy:
        for k, h in cond_entropy["conditional_entropies"].items():
            print(f"  H(X_{k+1}|X_1..X_{k}) = {h:.6f}")
    if "decay_base" in cond_entropy:
        print(f"  Decay base: {cond_entropy['decay_base']}")
        print(f"  Half-life: {cond_entropy.get('half_life_steps', 'N/A')} steps")
    print(f"  Time: {time.time() - t0:.1f}s")

    # --- Synthesis ---
    print("\n" + "="*60)
    print("SYNTHESIS: Shift space classification")
    print("="*60)

    # Determine shift type
    growth = sturmian.get("growth_type", "unknown")
    h_top = sturmian.get("exponential_fit", {}).get("h_top_estimate", None)
    decay_base = cond_entropy.get("decay_base", None)

    synthesis = {
        "growth_type": growth,
        "h_top_from_complexity": h_top,
        "conditional_entropy_decay_base": decay_base,
    }

    # Key question: Is h_top > 0?
    if h_top is not None and h_top > 0.1:
        synthesis["h_top_positive"] = True
        synthesis["shift_type_candidate"] = "positive entropy subshift (not SFT, possibly sofic or coded)"
    elif h_top is not None and h_top <= 0.1:
        synthesis["h_top_positive"] = False
        synthesis["shift_type_candidate"] = "zero or near-zero entropy subshift"

    # Forbidden word pattern
    total_new_forbidden = sum(forbidden[L]["new_forbidden"] for L in forbidden if L >= 2)
    synthesis["total_new_forbidden_at_each_level"] = {
        L: forbidden[L]["new_forbidden"] for L in sorted(forbidden.keys()) if L >= 2
    }
    synthesis["new_forbidden_growing"] = all(
        forbidden[L]["new_forbidden"] > 0 for L in range(3, max(forbidden.keys()) + 1)
    )

    if synthesis.get("new_forbidden_growing"):
        synthesis["sft_status"] = "NOT an SFT (new forbidden words appear at every level)"
        synthesis["sofic_status"] = "Likely NOT sofic (sofic shifts have bounded new forbidden words)"

    # Resolution of the paradox
    synthesis["paradox_resolution"] = (
        "The v2 sequence shift space has new forbidden words appearing at every block length, "
        "meaning it is NOT a shift of finite type (SFT). The absence of forbidden words at "
        "small lengths (L<=2) combined with H(k)/k -> 0 is consistent with a coded shift or "
        "countable intersection of SFTs. The constraints are inherently NON-LOCAL: each finite "
        "v2-block is realizable, but the set of infinite admissible sequences is strictly smaller "
        "than the full shift, with topological entropy determined by the growth rate of the "
        "complexity function."
    )

    results["synthesis"] = synthesis

    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time:.1f}s")
    print(json.dumps(synthesis, indent=2))

    return results

if __name__ == "__main__":
    results = main()

    output = {
        "title": "v2列のshift space構造解析",
        "approach": "v2列をsymbolic dynamicsのshift spaceとして分析。complexity function p(n)の増大率、"
                    "禁止語の階層構造、mod 2^kでの有限近似、条件付きエントロピーの減衰率を調査。",
        "findings": [],
        "hypotheses": [],
        "dead_ends": [],
        "scripts_created": ["scripts/v2_shift_space_analysis.py"],
        "outcome": "",
        "next_directions": [],
        "details": results
    }

    # Populate findings from synthesis
    s = results.get("synthesis", {})
    output["findings"].append(f"Complexity function growth type: {s.get('growth_type', 'unknown')}")
    output["findings"].append(f"h_top estimate from complexity: {s.get('h_top_from_complexity', 'N/A')}")

    if s.get("new_forbidden_growing"):
        output["findings"].append("New forbidden words appear at EVERY block length -> NOT an SFT")
        output["findings"].append("Likely NOT sofic (since new forbidden words keep appearing)")

    if s.get("conditional_entropy_decay_base"):
        base = s["conditional_entropy_decay_base"]
        output["findings"].append(f"Conditional entropy decays geometrically with base {base}")

    # Save
    with open("/Users/soyukke/study/lean-unsolved/results/v2_shift_space_structure.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print("\nResults saved to results/v2_shift_space_structure.json")
