"""Search Cauchy params for M satisfying BIC condition (b):
per input byte-block, all 64 row-restrictions pairwise distinct & nonzero.
Keeps MDS (Cauchy always MDS) and invertibility."""
import numpy as np
from sbox_math import gmul, ginv
from diffusion import mul_mat8, expand64, gf2_rank

def cauchy8_xs_ys(xs, ys):
    C = np.zeros((8, 8), dtype=np.uint8)
    for i in range(8):
        for j in range(8):
            C[i, j] = ginv(xs[i] ^ ys[j])
    return C

def cond_b(M):
    for qb in range(8):
        vecs = [int(sum(int(M[i, qb*8+l]) << l for l in range(8))) for i in range(64)]
        if len(set(vecs)) != 64 or 0 in vecs:
            return False
    return True

def cond_a(M):
    for i in range(64):
        for qb in range(8):
            if M[i, qb*8:(qb+1)*8].sum() == 0:
                return False
    return True

def main():
    rng = np.random.default_rng(2026)
    for t in range(500):
        # 16 distinct nonzero elements, split 8/8 with xs^ys != 0
        elems = rng.choice(255, size=16, replace=False) + 1
        xs = [int(e) for e in elems[:8]]
        ys = [int(e) for e in elems[8:]]
        if any(x == y for x in xs for y in ys):
            continue
        C8 = cauchy8_xs_ys(xs, ys)
        M = expand64(C8)
        if gf2_rank(M) != 64:
            continue
        if not cond_a(M):
            continue
        if cond_b(M):
            print(f"trial {t}: FOUND (b) with xs={xs} ys={ys}", flush=True)
            np.save('M64_bic.npy', M)
            rw = M.sum(axis=1)
            import math
            print("row weight max:", int(rw.max()), "XOR levels:", math.ceil(math.log2(int(rw.max()))))
            return
        if t % 50 == 0:
            print(f"trial {t}...", flush=True)
    print("not found in 500 trials")

if __name__ == '__main__':
    main()
