"""64x64 binary diffusion matrix M from 8x8 Cauchy over GF(2^8).
Verifies: invertibility, SAC condition (a), BIC condition (b), MDS/branch number,
max row weight -> XOR levels. Pure math, no gates."""
import numpy as np
from sbox_math import gmul, ginv

def cauchy8():
    # distinct x_i, y_j with x_i != y_j; use 1..8 and 9..16 (nonzero, distinct)
    xs = list(range(1, 9))
    ys = list(range(9, 17))
    C = np.zeros((8, 8), dtype=np.uint8)
    for i in range(8):
        for j in range(8):
            C[i, j] = ginv(xs[i] ^ ys[j])
    return C

def mul_mat8(c):
    """8x8 binary matrix of 'multiply by c' : (c.v)[t] = sum_l M[t,l] v[l]"""
    M = np.zeros((8, 8), dtype=np.uint8)
    for l in range(8):
        col = gmul(c, 1 << l)
        for t in range(8):
            M[t, l] = (col >> t) & 1
    return M

def expand64(C8):
    M = np.zeros((64, 64), dtype=np.uint8)
    for p in range(8):
        for q in range(8):
            B = mul_mat8(int(C8[p, q]))
            M[p*8:(p+1)*8, q*8:(q+1)*8] = B
    return M

def gf2_rank(M):
    A = M.copy().astype(np.uint8)
    n = A.shape[0]
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(n):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
    return r

def gf8_det(A):
    """determinant of n x n matrix over GF(2^8) via elimination; 0 if singular"""
    n = A.shape[0]
    M = A.astype(int).copy()
    det = 1
    for c in range(n):
        piv = None
        for i in range(c, n):
            if M[i, c] != 0:
                piv = i
                break
        if piv is None:
            return 0
        if piv != c:
            M[[c, piv]] = M[[piv, c]]
        inv = ginv(int(M[c, c]))
        for i in range(c+1, n):
            if M[i, c] != 0:
                f = gmul(int(M[i, c]), inv)
                for j in range(c, n):
                    M[i, j] ^= gmul(f, int(M[c, j]))
    return 1  # nonzero iff we got here

def main():
    C8 = cauchy8()
    print("Cauchy 8x8 over GF(2^8) built")
    # MDS check: all kxk submatrices nonsingular, k=1..8
    from itertools import combinations
    bad = 0
    total = 0
    for k in range(1, 9):
        for rows in combinations(range(8), k):
            for cols in combinations(range(8), k):
                total += 1
                sub = C8[np.ix_(list(rows), list(cols))]
                if gf8_det(sub) == 0:
                    bad += 1
    print(f"MDS submatrix check: {bad} singular / {total} total (expect 0)")
    M = expand64(C8)
    print("64x64 binary rank:", gf2_rank(M), "(expect 64)")
    # condition (a) SAC: each row has >=1 one in each byte-block
    ok_a = True
    for i in range(64):
        for qb in range(8):
            if M[i, qb*8:(qb+1)*8].sum() == 0:
                ok_a = False
    print("SAC condition (a) [row hits every byte-block]:", ok_a)
    # condition (b) BIC: per byte-block, 64 row-restrictions pairwise distinct & nonzero
    ok_b = True
    for qb in range(8):
        vecs = [int(sum(int(M[i, qb*8+l]) << l for l in range(8))) for i in range(64)]
        if len(set(vecs)) != 64 or 0 in vecs:
            ok_b = False
    print("BIC condition (b) [64 distinct nonzero restrictions per block]:", ok_b)
    # row weights
    rw = M.sum(axis=1)
    print("row weight: min", int(rw.min()), "max", int(rw.max()), "mean", float(rw.mean()))
    import math
    print("XOR levels (ceil(log2(maxweight))):", math.ceil(math.log2(int(rw.max()))))
    np.save('M64.npy', M)
    print("saved M64.npy")

if __name__ == '__main__':
    main()
