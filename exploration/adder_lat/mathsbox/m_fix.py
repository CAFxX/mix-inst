"""Fix BIC condition (b) via output-side block-diagonal mixer.
M = Dblk . Cexp where Dblk = block_diag(D_0..D_7), D_p random invertible 8x8.
Search D_p's for 64 distinct nonzero restrictions per input byte-block."""
import numpy as np
from diffusion import expand64, gf2_rank
from sbox_math import gmul, ginv, rand_invertible

def cauchy8():
    xs = list(range(1, 9)); ys = list(range(9, 17))
    C = np.zeros((8, 8), dtype=np.uint8)
    for i in range(8):
        for j in range(8):
            C[i, j] = ginv(xs[i] ^ ys[j])
    return C

def cond_ab(M):
    for qb in range(8):
        vecs = [int(sum(int(M[i, qb*8+l]) << l for l in range(8))) for i in range(64)]
        if len(set(vecs)) != 64 or 0 in vecs:
            return False
    for i in range(64):
        for qb in range(8):
            if M[i, qb*8:(qb+1)*8].sum() == 0:
                return False
    return True

def main():
    Cexp = expand64(cauchy8())
    rng = np.random.default_rng(777)
    for t in range(2000):
        Dblk = np.zeros((64, 64), dtype=np.uint8)
        for p in range(8):
            Dblk[p*8:(p+1)*8, p*8:(p+1)*8] = rand_invertible(rng)
        M = (Dblk @ Cexp) % 2
        if gf2_rank(M) != 64:
            continue
        if cond_ab(M):
            print(f"trial {t}: FOUND", flush=True)
            np.save('M64_bic.npy', M)
            rw = M.sum(axis=1)
            import math
            print("max row weight:", int(rw.max()), "XOR levels:", math.ceil(math.log2(int(rw.max()))))
            return
        if t % 200 == 0:
            print(f"trial {t}...", flush=True)
    print("not found")

if __name__ == '__main__':
    main()
