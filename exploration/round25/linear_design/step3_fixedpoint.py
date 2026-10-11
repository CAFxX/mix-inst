#!/usr/bin/env python3
"""Step 3: Fixed-point structure and invariant-subspace risk analysis.
The S-box has 7 fixed points: 0,1,2,3,4,9,12.
We characterize which linear structures would preserve fixed-point-aligned
subspaces, so the routing can avoid them."""
import json
import numpy as np
from itertools import combinations

S = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]
FP = [x for x in range(16) if S[x] == x]
print("fixed points:", FP, f"({len(FP)}/16)")

# 1. Fixed-point set as a union of affine subspaces? Check linear span.
def to_bits(x):
    return [(x >> i) & 1 for i in range(4)]

fps = np.array([to_bits(x) for x in FP])
# rank of the set (as vectors)
rank = np.linalg.matrix_rank(fps)
print(f"rank of fixed-point set (as F2 vectors): {rank}")
# Is 0 in FP? yes. So it's a subset containing 0. Is it a subspace?
# A subspace of dim k has 2^k elements. 7 is not a power of 2, so NOT a subspace.
print("7 is not a power of 2 -> fixed points do NOT form a linear subspace (good)")

# 2. Largest affine subspace contained in FP (invariant-risk primitive)
# A linear layer preserving such a subspace, combined with S-box fixing it
# pointwise-ish, could create a round-invariant.
def is_affine_subspace(pts):
    pts = set(pts)
    # check: for all a,b,c in pts, a^b^c in pts (affine closure)
    for a in pts:
        for b in pts:
            for c in pts:
                if (a ^ b ^ c) not in pts:
                    return False
    return True

# find all maximal affine subspaces of FP via brute force (2^16 subsets is too many;
# instead check all affine subspaces of F2^4 and test containment)
def all_affine_subspaces():
    # represent affine subspace by (offset, basis list)
    subs = []
    # dim 0: singletons
    for o in range(16):
        subs.append((o, []))
    # dim 1: lines {o, o^d}
    for o in range(16):
        for d in range(1, 16):
            pts = tuple(sorted([o, o ^ d]))
            subs.append((pts, 1))
    # dim 2: planes {o, o^a, o^b, o^a^b}
    seen = set()
    for o in range(16):
        for a in range(1, 16):
            for b in range(a+1, 16):
                if a ^ b == 0: continue
                # check a,b independent: a^b != 0 and neither is 0 (true)
                pts = tuple(sorted(set([o, o^a, o^b, o^a^b])))
                if len(pts) == 4 and pts not in seen:
                    seen.add(pts)
                    subs.append((pts, 2))
    return subs

fpset = set(FP)
max_aff = []
for item in all_affine_subspaces():
    if isinstance(item[0], tuple):
        pts, dim = item
        if set(pts) <= fpset and dim == 2:
            max_aff.append((pts, dim))
print(f"\n2-dim affine subspaces fully inside FP set: {len(max_aff)}")
for pts, dim in max_aff[:10]:
    print("  ", [hex(p) for p in pts])

# 3. Key question for routing: the DANGEROUS pattern is a linear layer that maps
#    a nibble-aligned fixed-point-heavy set to itself.
#    Concretely, avoid: y[nibble m] depending ONLY on x[nibble m] (no spread),
#    because then {x : each nibble in FP} (size 7^16) maps into itself under
#    S (pointwise fixed) and under a nibble-diagonal linear layer.
#    Our design forces cross-nibble mixing, which provably breaks this:
#    if every output nibble mixes >=2 input nibbles, no nibble-aligned FP set is preserved.
print("\nDesign rule derived: every linear-layer output bit must XOR bits from")
print(">= 2 distinct input nibbles (ideally >= 3); output nibbles must not be")
print("functions of a single input nibble. This kills the nibble-aligned")
print("fixed-point invariant (7^16-element set).")

# 4. Stronger: check 2-round "fixed-point trail" probability under our constraint.
#    P(nibble hits FP after key xor) -- key xor randomizes, so per nibble P = 7/16.
#    For an invariant we'd need ALL 16 nibbles in FP simultaneously: (7/16)^16 ~ 2^-19
#    per round, AND the linear layer to preserve the pattern. Cross-nibble mixing
#    ensures the linear layer does not preserve nibble-FP patterns.
p_fp = len(FP) / 16
print(f"\nPer-nibble P(FP | random key-xor): {p_fp:.4f} = 7/16")
print(f"P(all 16 nibbles in FP): {(p_fp**16):.2e} ~= 2^{np.log2(p_fp**16):.1f}")

# 5. Linear structures IN the S-box: check for linear/affine approximations
#    with large bias that the routing should not align into trails.
#    Find all (a,b) with |LAT| = 8 (max, i.e. bias 2^-1... in our scaled units |L|=4).
import json as js
D = js.load(open("ddt_lat_full.json"))
L = np.array(D["LAT"])  # scaled by /2; true Walsh = 2*L
W = 2 * L
maxw = np.abs(W[1:, 1:]).max()
print(f"\nMax |Walsh| (nontrivial): {maxw}")
nmax = np.sum(np.abs(W[1:,1:]) == maxw)
print(f"Number of (a,b) achieving it: {nmax} (of 225)")
# list them
idx = np.argwhere(np.abs(W[1:,1:]) == maxw)
print("Top linear approximations (a->b, bias):")
for (i, j) in idx[:12]:
    a, b = i+1, j+1
    print(f"  in_mask={a:04b} -> out_mask={b:04b}, |W|={abs(W[a,b])}")

json.dump({
    "fixed_points": FP,
    "n_fp": len(FP),
    "fp_is_subspace": False,
    "planes_in_fp": [list(p) for p, d in max_aff],
    "design_rule": "every output bit XORs >=2 distinct input nibbles",
    "p_all_fp": float(p_fp**16),
}, open("fixedpoint_analysis.json", "w"), indent=1)
print("\nwrote fixedpoint_analysis.json")
