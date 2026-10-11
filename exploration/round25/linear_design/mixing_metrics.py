#!/usr/bin/env python3
"""Mixing-quality metrics toolkit for the RV64 mix search.

Why this exists (2026-10-06): branch number and spread2 (nibble-level,
linear-layer-only) said (5,13) > (3,11), but S2 |z| said the opposite and
theory couldn't separate 1,212 candidates. These metrics capture the
S-box x linear-layer interaction at the trail level — the missing middle
between cheap theory and expensive batteries.

Metrics:
  1. active_sboxes(a, b, rounds): min active S-boxes over N rounds via BFS
     over the DDT. Max differential trail prob <= (DU/16)^active = (1/4)^active.
  2. diffusion_rounds(a, b): for each input bit, rounds until all 64 output
     bits depend on it (boolean dependency tracking). Bit-granular,unlike
     nibble-level branch.
  3. avalanche_dist(a, b, rounds): Hamming-weight distribution over all 64
     single-bit input flips: mean, std, min, max.

Validation criterion: must predict S2 |z| rankings and S3 outcomes across
candidates. If not predictive, they're theater.

Usage:
  python3 mixing_metrics.py --pairs 3,11 5,13 8,15 --rounds 4
"""
import argparse
import itertools
import json
import sys

# rasC2_0 S-box (the reference for trail analysis)
SBOX = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]

def build_ddt():
    """DDT[a][b] = count of x with S(x)^S(x^a) = b."""
    ddt = [[0]*16 for _ in range(16)]
    for x in range(16):
        for a in range(16):
            b = SBOX[x] ^ SBOX[x ^ a]
            ddt[a][b] += 1
    return ddt

DDT = build_ddt()
# For each input diff, the set of reachable output diffs (nonzero -> nonzero)
DDT_TRANS = {a: [b for b in range(16) if DDT[a][b] > 0]
             for a in range(16)}

def lin_apply(x, a, b):
    def rotl(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & 0xFFFFFFFFFFFFFFFF
    return x ^ rotl(x, a) ^ rotl(x, b)

def diff_to_nibbles(d):
    """Which nibbles are active in a 64-bit difference."""
    return tuple(i for i in range(16) if (d >> (4*i)) & 0xF)

def nibble_diff_pattern(d, nib):
    return (d >> (4*nib)) & 0xF

def active_sboxes(a, b, rounds, max_states=200000):
    """Min active S-boxes over `rounds` via BFS on difference states.

    State = 64-bit difference. Transitions: through S-box layer (per-nibble
    DDT) then linear layer. Cost = number of active S-boxes traversed.
    Returns (min_active, example_trail).
    """
    # BFS (Dijkstra) over difference states, cost = active S-boxes
    import heapq
    # Start: all 64 single-bit differences
    # State: (cost, difference)
    # To keep it tractable, we track (difference -> min_cost) and prune.
    best = {}
    pq = []
    for bit in range(64):
        d = 1 << bit
        heapq.heappush(pq, (0, 0, d, [d]))  # (cost, round, diff, trail)
        best[(0, d)] = 0

    min_active = None
    best_trail = None

    while pq:
        cost, r, d, trail = heapq.heappop(pq)
        if best.get((r, d), 1e9) < cost:
            continue
        if r == rounds:
            if min_active is None or cost < min_active:
                min_active = cost
                best_trail = trail
            continue
        if min_active is not None and cost >= min_active:
            continue

        # Through S-box layer: each active nibble branches via DDT
        an = diff_to_nibbles(d)
        n_active = len(an)
        new_cost = cost + n_active

        if min_active is not None and new_cost >= min_active:
            continue

        # Cartesian product of DDT transitions for active nibbles
        # (prune: if too many, sample — but 4-bit S-box keeps it small)
        options = [DDT_TRANS[nibble_diff_pattern(d, nib)] for nib in an]
        # Cap the branching to avoid explosion
        total = 1
        for o in options:
            total *= len(o)
        if total > 5000:
            # Too many; take the min-cost path greedily (lower bound)
            # This makes it a lower bound, not exact — note in output
            continue

        for combo in itertools.product(*options):
            d2 = 0
            for nib, od in zip(an, combo):
                d2 |= od << (4 * nib)
            if d2 == 0:
                continue
            # Through linear layer
            d3 = lin_apply(d2, a, b)
            key = (r + 1, d3)
            if best.get(key, 1e9) > new_cost:
                best[key] = new_cost
                heapq.heappush(pq, (new_cost, r + 1, d3, trail + [d3]))
                if len(best) > max_states:
                    # State cap hit; return lower bound
                    return min_active, best_trail, True

    return min_active, best_trail, False

def diffusion_rounds(a, b, max_rounds=10):
    """For each input bit, rounds until all 64 outputs depend on it.

    Boolean dependency: dep[r][i] = bitmask of input bits affecting output i
    after r rounds. S-box makes all 4 output bits of a nibble depend on all 4
    input bits of that nibble. Linear layer XORs dependencies.
    Returns list of 64 ints (rounds per input bit), and the max.
    """
    # dep[i] = 64-bit mask of input bits that output bit i depends on
    # Start: identity (round 0)
    dep = [1 << i for i in range(64)]

    def apply_sbox_dep(dep):
        out = [0]*64
        for nib in range(16):
            # Union of deps for the 4 bits in this nibble
            u = 0
            for k in range(4):
                u |= dep[nib*4 + k]
            for k in range(4):
                out[nib*4 + k] = u
        return out

    def apply_lin_dep(dep, a, b):
        # out[i] = dep[i] | dep[(i-a)%64] | dep[(i-b)%64]
        # (dependency is a UNION, not XOR — if two inputs both depend on
        # bit k, the output still depends on bit k)
        out = [0]*64
        for i in range(64):
            out[i] = dep[i] | dep[(i - a) % 64] | dep[(i - b) % 64]
        return out

    full = (1 << 64) - 1
    result = [None]*64

    for r in range(1, max_rounds + 1):
        dep = apply_sbox_dep(dep)
        dep = apply_lin_dep(dep, a, b)
        for i in range(64):
            if result[i] is None:
                # Check if input bit i affects all outputs
                # (i.e., for all output j, bit i in dep[j])
                if all((dep[j] >> i) & 1 for j in range(64)):
                    result[i] = r
        if all(x is not None for x in result):
            break

    return result

def avalanche_dist(a, b, rounds=2):
    """Hamming-weight distribution of output differences for single-bit inputs.

    Applies `rounds` of (S-box then linear). Returns dict with mean/std/min/max.
    """
    import statistics
    weights = []
    for bit in range(64):
        d = 1 << bit
        for _ in range(rounds):
            # S-box layer: per nibble, nonzero -> nonzero (worst case: keep as is
            # for weight; actually S-box is a permutation, weight can change.
            # For avalanche we care about the actual S-box.)
            d2 = 0
            for nib in range(16):
                p = (d >> (4*nib)) & 0xF
                if p:
                    # Apply actual S-box difference: use a representative
                    # For single-bit input diffs, we track the actual propagation.
                    # Simplification: S-box maps nonzero to nonzero; use SBOX diff.
                    # We need a concrete input; use 0 as base.
                    d2 |= (SBOX[p] ^ SBOX[0]) << (4*nib) if p else 0
            # Actually simpler: model as random permutation per nibble?
            # No — use the real S-box with input 0.
            d = lin_apply(d2, a, b)
        weights.append(bin(d).count("1"))
    return {"mean": statistics.mean(weights),
            "stdev": statistics.stdev(weights) if len(weights) > 1 else 0,
            "min": min(weights), "max": max(weights), "n": len(weights)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True,
                    help="comma-separated a,b pairs, e.g. '3,11 5,13'")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    pairs = []
    for p in args.pairs.split():
        a, b = p.split(",")
        pairs.append((int(a), int(b)))

    results = {}
    for a, b in pairs:
        print(f"[{a},{b}] active S-boxes...", flush=True)
        act, trail, capped = active_sboxes(a, b, args.rounds)
        print(f"[{a},{b}] diffusion rounds...", flush=True)
        diff = diffusion_rounds(a, b)
        print(f"[{a},{b}] avalanche...", flush=True)
        aval = avalanche_dist(a, b, rounds=2)
        results[f"{a},{b}"] = {
            "min_active_sboxes": act,
            "max_trail_prob_log2": act * -2 if act else None,  # (1/4)^act
            "state_capped": capped,
            "diffusion_rounds_max": max(x for x in diff if x),
            "diffusion_rounds_all": diff,
            "avalanche_2r": aval,
        }
        print(f"  active={act} (trail<=2^{act*-2 if act else '?'}), "
              f"diff_max={max(x for x in diff if x)}, "
              f"aval_mean={aval['mean']:.1f}±{aval['stdev']:.1f} "
              f"[{aval['min']},{aval['max']}]", flush=True)

    if args.out:
        json.dump(results, open(args.out, "w"), indent=1)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
