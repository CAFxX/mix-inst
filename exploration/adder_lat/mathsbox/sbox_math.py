"""First-principles 8x8 S-box math: GF(2^8) inversion family + affine search.
Pure math: truth tables, Walsh spectra, ANF. No gates, no netlists."""
import numpy as np
import itertools, math, sys

# ---------------- GF(2^8), poly x^8+x^4+x^3+x+1 (0x11b) ----------------
# NOTE: 0x02 has order 51 here (0x11b is irreducible but NOT primitive),
# so log tables are invalid. Use Russian-peasant multiply + Fermat inverse.
def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & 0x100:
            a ^= 0x11b
    return r

def gpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gmul(r, a)
        e >>= 1
        a = gmul(a, a)
    return r

def ginv(a):
    return gpow(a, 254) if a else 0

INV = np.array([ginv(a) for a in range(256)], dtype=np.uint8)

# ---------------- GF(2) linear helpers ----------------
def mat_vec(M, v):
    """M: (8,8) binary rows, v: uint8 -> uint8. M[t] rows as bitmasks over input bits."""
    out = 0
    for t in range(8):
        if bin(M[t] & v).count('1') & 1:
            out |= (1 << t)
    return out

def mat_vec_arr(M, vs):
    """vectorized over vs (np uint8 array)"""
    out = np.zeros_like(vs)
    for t in range(8):
        row = M[t]
        p = np.zeros_like(vs, dtype=np.uint8)
        for l in range(8):
            if (row >> l) & 1:
                p ^= (vs >> l) & 1
        out |= (p.astype(np.uint8) << t)
    return out

def rand_invertible(rng):
    while True:
        M = rng.integers(0, 256, size=8, dtype=np.uint8)
        # rank check via GF(2) elimination
        rows = [int(r) for r in M]
        rank = 0
        for c in range(8):
            piv = None
            for r in range(rank, 8):
                if (rows[r] >> c) & 1:
                    piv = r
                    break
            if piv is None:
                continue
            rows[rank], rows[piv] = rows[piv], rows[rank]
            for r in range(8):
                if r != rank and ((rows[r] >> c) & 1):
                    rows[r] ^= rows[rank]
            rank += 1
        if rank == 8:
            return M

def apply_affine(S, A, b, C, d):
    """S'(x) = C . S(A.x + b) + d, all as tables. A,C (8,) row-bitmasks, b,d uint8."""
    xs = np.arange(256, dtype=np.uint8)
    t1 = mat_vec_arr(A, xs) ^ np.uint8(b)
    t2 = S[t1]
    t3 = mat_vec_arr(C, t2) ^ np.uint8(d)
    return t3

# ---------------- metrics (vectorized) ----------------
def fwht_rows(H):
    H = H.copy()
    n = H.shape[1]
    step = 1
    while step < n:
        H = H.reshape(-1, 2*step, H.shape[1]//(2*step) if False else 1) if False else H
        # manual: operate on pairs of blocks
        H2 = H.reshape(H.shape[0], -1, 2*step)
        u = H2[:, :, :step].copy()
        v = H2[:, :, step:]
        H2[:, :, :step] = u + v
        H2[:, :, step:] = u - v
        H = H2.reshape(H.shape[0], n)
        step *= 2
    return H

def comp_nonlinearity(S):
    """min NL over 255 nonzero components"""
    masks = np.arange(1, 256, dtype=np.uint8)[:, None]
    # parity(m & S[x]) for all m,x : use bitwise
    # v[m,x] = (-1)^{popcount(m & S[x]) mod 2}
    Sx = S[None, :]  # (1,256)
    mm = masks  # (255,1)
    # compute parity via lookup: precompute parity of 0..255
    PAR = np.array([bin(i).count('1') & 1 for i in range(256)], dtype=np.uint8)
    P = PAR[(mm & Sx).astype(np.uint8)]  # (255,256)
    H = fwht_rows(np.where(P == 0, 1, -1).astype(np.int32))
    maxw = np.abs(H).max(axis=1)
    nl = 128 - maxw // 2
    return int(nl.min()), nl

def mobius_rows(A):
    A = A.copy()
    n = A.shape[1]
    step = 1
    while step < n:
        A2 = A.reshape(A.shape[0], -1, 2*step)
        A2[:, :, step:] ^= A2[:, :, :step]
        A = A2.reshape(A.shape[0], n)
        step *= 2
    return A

def comp_degree(S):
    """max algebraic degree over 8 components, via Mobius"""
    bits = ((S[None, :] >> np.arange(8)[:, None]) & 1).astype(np.uint8)
    ANF = mobius_rows(bits)
    deg = 0
    for j in range(8):
        idx = np.flatnonzero(ANF[j])
        if len(idx):
            d = max(bin(i).count('1') for i in idx)
            deg = max(deg, d)
    return deg

def sac_report(S):
    """returns (#violations, max |bias|) over 8x8 (input bit, output bit)"""
    viol = 0
    maxbias = 0
    for i in range(8):
        d = S ^ S[np.arange(256) ^ (1 << i)]
        for j in range(8):
            c = int((((d >> j) & 1).sum()))
            b = abs(c - 128)
            maxbias = max(maxbias, b)
            if c != 128:
                viol += 1
    return viol, maxbias

def bic_report(S):
    """max |bias| of D_i s_j + D_i s_k over i, j<k. 0 = perfect BIC."""
    maxbias = 0
    for i in range(8):
        A = ((S[None, :] ^ S[None, :][:, np.arange(256) ^ (1 << i)]) >> np.arange(8)[:, None]) & 1
        # A: (8,256)
        for j in range(8):
            for k in range(j+1, 8):
                c = int(((A[j] ^ A[k]) == 0).sum())
                maxbias = max(maxbias, abs(c - 128))
    return maxbias

def diff_uniformity(S):
    du = 0
    for a in range(1, 256):
        dd = S ^ S[np.arange(256) ^ a]
        bc = np.bincount(dd, minlength=256)
        du = max(du, int(bc.max()))
    return du

def alldir_sac_bic(S):
    """check SAC/BIC for ALL 255 nonzero directions (stronger than unit vectors)"""
    sac_viol = 0
    bic_max = 0
    for a in range(1, 256):
        D = S ^ S[np.arange(256) ^ np.uint8(a)]
        bits = ((D[None, :] >> np.arange(8)[:, None]) & 1)
        for j in range(8):
            if int(bits[j].sum()) != 128:
                sac_viol += 1
        for j in range(8):
            for k in range(j+1, 8):
                c = int(((bits[j] ^ bits[k]) == 0).sum())
                bic_max = max(bic_max, abs(c - 128))
    return sac_viol, bic_max

def influence(S):
    """for each output bit, set of input bits it depends on"""
    inf = []
    for j in range(8):
        s = set()
        col = ((S >> j) & 1)
        for i in range(8):
            if np.any(col != col[np.arange(256) ^ (1 << i)]):
                s.add(i)
        inf.append(s)
    return inf

if __name__ == '__main__':
    print("base = GF(2^8) inversion (0->0)")
    S0 = INV
    nl, _ = comp_nonlinearity(S0)
    print("NL(min) =", nl, "(expect 112)")
    print("degree =", comp_degree(S0), "(expect 7)")
    print("diff uniformity =", diff_uniformity(S0), "(expect 4)")
    sv, sb = sac_report(S0)
    print("SAC violations (unit vec) =", sv, "maxbias =", sb)
    print("BIC maxbias (unit vec) =", bic_report(S0))
    asv, abm = alldir_sac_bic(S0)
    print("all-direction SAC violations =", asv, "(out of", 255*8, ")")
    print("all-direction BIC maxbias =", abm)
    print("influence per output bit:", influence(S0))
