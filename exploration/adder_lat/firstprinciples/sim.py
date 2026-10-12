"""First-principles 3-stage 64-bit Boolean mapping simulator.

Stage function (3 levels, 8 inputs, NL=112, degree 2, balanced):
    out = (a0^a5) ^ (a1&a4) ^ (a2&a7) ^ (a3&a6)
This is the optimal 7-input form x0^(x1&x4)^(x2&x7)^(x3&x6) with x0 -> (x0^x5),
an affine input transform, so NL=112 and balance are preserved, now 8-input.

Wiring:
  Stage 1: out[i] takes primary inputs {(i+j) mod 64 : j=0..7}   (local)
  Stage 2: out[i] takes Stage-1 outs {(i+8j) mod 64 : j=0..7}     (stride-8)
  Stage 3: out[i] takes Stage-2 outs {(i+j) mod 64 : j=0..7}     (local)

Dependency: D1=8, D2=64 (8 disjoint 8-blocks), D3=64. Degree: 2->4->8.
Levels: 3+3+3=9 (~16.2u).
"""
import numpy as np
import itertools

# Precompute wiring index arrays: W[s][i][j] = source index for stage s, output i, input j
W1 = np.array([[(i + j) % 64 for j in range(8)] for i in range(64)], dtype=np.int64)
W2 = np.array([[(i + 8 * j) % 64 for j in range(8)] for i in range(64)], dtype=np.int64)
W3 = np.array([[(i + j) % 64 for j in range(8)] for i in range(64)], dtype=np.int64)


def stage_func(A):
    """A: (N,64,8) uint8 -> (N,64) uint8. out=(a0^a5)^(a1&a4)^(a2&a7)^(a3&a6)."""
    a0 = A[:, :, 0]; a1 = A[:, :, 1]; a2 = A[:, :, 2]; a3 = A[:, :, 3]
    a4 = A[:, :, 4]; a5 = A[:, :, 5]; a6 = A[:, :, 6]; a7 = A[:, :, 7]
    return ((a0 ^ a5) ^ (a1 & a4) ^ (a2 & a7) ^ (a3 & a6)).astype(np.uint8)


def forward(X):
    """X: (N,64) uint8 -> (N,64) uint8 through all 3 stages."""
    A1 = X[:, W1]          # (N,64,8)
    S1 = stage_func(A1)    # (N,64)
    A2 = S1[:, W2]
    S2 = stage_func(A2)
    A3 = S2[:, W3]
    S3 = stage_func(A3)
    return S3


def check_stage_func():
    """Verify NL=112, balanced, degree 2 for the 8-input stage function."""
    # truth table over 8 inputs
    tt = np.zeros(256, dtype=np.uint8)
    for bits in itertools.product([0, 1], repeat=8):
        b = np.array(bits, dtype=np.uint8)
        idx = sum(v << k for k, v in enumerate(bits))
        tt[idx] = (b[0] ^ b[5]) ^ (b[1] & b[4]) ^ (b[2] & b[7]) ^ (b[3] & b[6])
    assert tt.sum() == 128, f"not balanced: {tt.sum()}"
    # Walsh-Hadamard for NL
    w = np.where(tt == 0, 1.0, -1.0)
    h = w.copy()
    n = 8
    N = 256
    for i in range(n):
        step = 1 << (i + 1)
        for j in range(0, N, step):
            for k in range(1 << i):
                u, v = h[j + k], h[j + k + (1 << i)]
                h[j + k] = u + v
                h[j + k + (1 << i)] = u - v
    maxw = np.max(np.abs(h))
    nl = (N - maxw) // 2
    print(f"Stage function: balanced={tt.sum()==128}, NL={int(nl)}, max|W|={int(maxw)}")
    # degree: check ANF has degree-2 terms but no higher
    # (by construction: only AND2 of distinct vars, XORed)
    print("Stage function: degree=2 (by construction: 3 AND2 + XORs)")


def check_dependence():
    """Verify each Stage-3 output transitively depends on all 64 primary inputs."""
    # D1(i) = set(W1[i]), D2(i) = union of D1[W2[i][j]], D3 similarly
    D1 = [set(W1[i].tolist()) for i in range(64)]
    D2 = [set().union(*[D1[k] for k in W2[i].tolist()]) for i in range(64)]
    D3 = [set().union(*[D2[k] for k in W3[i].tolist()]) for i in range(64)]
    s1 = sorted(set(len(d) for d in D1))
    s2 = sorted(set(len(d) for d in D2))
    s3 = sorted(set(len(d) for d in D3))
    print(f"D1 sizes: {s1}, D2 sizes: {s2}, D3 sizes: {s3}")
    assert all(len(d) == 64 for d in D3), "not all Stage-3 outputs cover 64 inputs!"
    print("All 64 Stage-3 outputs depend on all 64 primary inputs. OK")


def bits_to_u64(X):
    """(N,64) uint8 -> (N,) uint64."""
    powers = (1 << np.arange(64, dtype=np.uint64))
    return (X.astype(np.uint64) * powers).sum(axis=1)


def test_bijectivity(n_pairs=200_000, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2, size=(n_pairs, 64), dtype=np.uint8)
    Y = forward(X)
    y64 = bits_to_u64(Y)
    # collisions: duplicate outputs among distinct inputs
    # (inputs distinct w.h.p.)
    uniq, counts = np.unique(y64, return_counts=True)
    ncoll = int(np.sum(counts > 1))
    print(f"Bijectivity: {n_pairs} samples, {ncoll} output collisions")
    return ncoll == 0


if __name__ == "__main__":
    import sys
    check_stage_func()
    check_dependence()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    ok = test_bijectivity(n)
    print("BIJECTIVE (sampled)" if ok else "NOT bijective (collisions found)")
