"""
SAC/BIC first-principles search for 64-bit vectorial Boolean function.

F = (f_0, ..., f_63), f_j(x) = x_j XOR (XOR over k of (x_{a_{j,k}} & x_{b_{j,k}}))

For quadratic f_j, the derivative D_i f_j is affine linear:
  D_i f_j(x) = c_{ij} XOR (M_{ij} . x)
where M_{ij} is a 64-bit mask (Python int).

SAC(i,j) holds iff M_{ij} != 0 (derivative is non-constant => balanced).
BIC(i,j,k) holds iff M_{ij} != M_{ik} (derivatives are distinct => independent).

We hill-climb on the AND-pair assignments to drive violations to zero.
"""

import random
import sys


def compute_masks(funcs):
    """funcs: list of 64, each a list of (a,b) pairs with a<b.
    Returns M[i][j] = partner-XOR mask (int) for input i in function j."""
    M = [[0] * 64 for _ in range(64)]
    for j, pairs in enumerate(funcs):
        row_a = M  # M[i][j]
        for (a, b) in pairs:
            M[a][j] ^= (1 << b)
            M[b][j] ^= (1 << a)
    return M


def score_masks(M):
    """Returns (sac_violations, bic_violations)."""
    sac = 0
    bic = 0
    for i in range(64):
        seen = set()
        for j in range(64):
            m = M[i][j]
            if m == 0:
                sac += 1
            if m in seen:
                bic += 1
            else:
                seen.add(m)
    return sac, bic


def random_funcs(t, rng):
    """64 functions, each with t random AND pairs (a<b)."""
    funcs = []
    for j in range(64):
        pairs = set()
        while len(pairs) < t:
            a = rng.randrange(64)
            b = rng.randrange(64)
            if a == b:
                continue
            if a > b:
                a, b = b, a
            pairs.add((a, b))
        funcs.append(list(pairs))
    return funcs


def structured_init(t, rng):
    """Initialize with pairings designed for coverage:
    for each j, use a rotation-based perfect matching plus extra random pairs."""
    funcs = []
    for j in range(64):
        pairs = set()
        # Base: perfect matching via rotation by (j+1)
        # pair k with (k + j + 1) mod 64 for k even... need disjoint.
        # Simpler: pair (2k, 2k+1) rotated.
        shift = j
        for k in range(32):
            a = (2 * k + shift) % 64
            b = (2 * k + 1 + shift) % 64
            if a > b:
                a, b = b, a
            pairs.add((a, b))
        # Add extra pairs to reach t
        while len(pairs) < t:
            a = rng.randrange(64)
            b = rng.randrange(64)
            if a == b:
                continue
            if a > b:
                a, b = b, a
            pairs.add((a, b))
        funcs.append(list(pairs))
    return funcs


def evaluate(funcs):
    M = compute_masks(funcs)
    return score_masks(M)


if __name__ == "__main__":
    rng = random.Random(42)
    t = 40
    funcs = structured_init(t, rng)
    sac, bic = evaluate(funcs)
    print(f"t={t} init: SAC violations={sac}, BIC violations={bic}")
    print(f"Total possible SAC: {64*64}, BIC pairs per i: {64*63//2}, total BIC: {64*64*63//2}")
