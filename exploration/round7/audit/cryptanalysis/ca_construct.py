"""Constructive differential trail for r7_feist8_s1_1sbox.

Feistel difference relation: x_{i+1} = x_{i-1} ^ lin(e_i), e_i in DDT_S(x_i),
x_i = F-input difference at round i (x_1 = dR_0).

Skeleton (input diff (a,0), a single nibble at p1):
  x = (0, a, f2, 0, f2, f5, 0, f5),  wt = (0,1,3,0,3,1,0,1) = 9 active
Constraints:
  e2: single nibble at p1, DDT[a][e2]>0 ; f2 = lin(e2), wt(f2)==3
  e3 = lin^{-1}(a); DDT[f2_j][e3_j] > 0 for all j  => x4 = 0
  e5: supp(e5) subset supp(f2), DDT[f2_j][e5_j]>0, lin(e5) single nibble at p2 (=:f5)
  DDT[f5_{p2}][e2] > 0  => with e6 = e2: x7 = f2 ^ lin(e2) = 0
  e8: DDT[f5_{p2}][e8] > 0 ; f8 = lin(e8); output diff = (f5, f8)
"""
import math
S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
DDT = [[0]*16 for _ in range(16)]
for x in range(16):
    for a in range(16):
        DDT[a][S1[x] ^ S1[x ^ a]] += 1

def lin32(x):
    x &= 0xFFFFFFFF
    return (x ^ (((x << 7) | (x >> 25)) & 0xFFFFFFFF) ^ (((x << 13) | (x >> 19)) & 0xFFFFFFFF)) & 0xFFFFFFFF

# inverse of lin32 via 32x32 bit matrix
M = [[0]*32 for _ in range(32)]
for i in range(32):
    y = lin32(1 << i)
    for j in range(32):
        M[j][i] = (y >> j) & 1
def mat_vec_inv(y):
    # solve M z = y over GF(2)
    A = [row[:] + [(y >> i) & 1] for i, row in enumerate(M)]
    n = 32
    piv = [-1]*n
    r = 0
    for c in range(n):
        p = next((i for i in range(r, n) if A[i][c]), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]; piv[c] = r
        for i in range(n):
            if i != r and A[i][c]:
                A[i] = [(a ^ b) for a, b in zip(A[i], A[r])]
        r += 1
    z = 0
    for c in range(n):
        if piv[c] != -1 and A[piv[c]][n]:
            z |= (1 << c)
    assert lin32(z) == y
    return z

def nibs(x):
    return [(x >> (4*i)) & 0xF for i in range(8)]
def supp(x):
    return {i for i in range(8) if (x >> (4*i)) & 0xF}
def wt(x):
    return len(supp(x))
def ddt_ok(b, e):
    nb, ne = nibs(b), nibs(e)
    return all(DDT[nb[j]][ne[j]] > 0 for j in range(8))
def ddt_logprob(b, e):
    nb, ne = nibs(b), nibs(e)
    lp = 0.0
    for j in range(8):
        if nb[j] or ne[j]:
            lp += math.log(DDT[nb[j]][ne[j]] / 16)
    return lp

found = []
for p1 in range(8):
    for aval in range(1, 16):
        a = aval << (4*p1)
        e3 = mat_vec_inv(a)  # lin(e3) = a
        if wt(e3) > 4:  # need supp(e3) subset supp(f2), wt(f2)=3 -> wt(e3)<=3
            continue
        for e2val in range(1, 16):
            if DDT[aval][e2val] == 0: continue
            e2 = e2val << (4*p1)
            f2 = lin32(e2)
            if wt(f2) != 3: continue
            if not (supp(e3) <= supp(f2)): continue
            if not ddt_ok(f2, e3): continue
            lp3 = ddt_logprob(f2, e3)
            # find e5: lin(e5) single nibble at some p2, supp(e5)<=supp(f2), ddt_ok(f2,e5)
            for p2 in range(8):
                for cval in range(1, 16):
                    f5 = cval << (4*p2)
                    e5 = mat_vec_inv(f5)
                    if not (supp(e5) <= supp(f2)): continue
                    if not ddt_ok(f2, e5): continue
                    if DDT[cval][e2val] == 0: continue  # DDT[f5_{p2}][e2]
                    lp5 = ddt_logprob(f2, e5)
                    lp2 = math.log(DDT[aval][e2val]/16)
                    lp6 = math.log(DDT[cval][e2val]/16)
                    # round 8: best e8
                    best_e8, best_lp8 = None, -1e9
                    for e8val in range(16):
                        if DDT[cval][e8val] == 0: continue
                        l = math.log(DDT[cval][e8val]/16)
                        if l > best_lp8: best_lp8, best_e8 = l, e8val
                    f8 = lin32(best_e8 << (4*p2))
                    total_lp = lp2 + lp3 + lp5 + lp6 + best_lp8
                    active = 0+1+3+0+3+1+0+1
                    found.append((total_lp, active, {
                        'a': a, 'p1': p1, 'e2': e2, 'f2': f2, 'e3': e3,
                        'e5': e5, 'f5': f5, 'p2': p2, 'e8': best_e8 << (4*p2), 'f8': f8,
                        'lp': (lp2, lp3, lp5, lp6, best_lp8)}))
found.sort(key=lambda z: -z[0])
print(f"feasible 9-active skeletons: {len(found)}")
for (lp, act, d) in found[:5]:
    print(f"  P = 2^{lp/math.log(2):.2f}, active={act}, in_diff=(0x{d['a']:08x},0x00000000), out_diff=(0x{d['f5']:08x},0x{d['f8']:08x})")
    print(f"    per-round log2: r2:{d['lp'][0]/math.log(2):.2f} r3:{d['lp'][1]/math.log(2):.2f} r5:{d['lp'][2]/math.log(2):.2f} r6:{d['lp'][3]/math.log(2):.2f} r8:{d['lp'][4]/math.log(2):.2f}")
import pickle
with open("constructive_trails.pkl", "wb") as fh:
    pickle.dump(found, fh)
