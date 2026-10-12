"""Simulated annealing to repair BIC condition (b) in M.
Start from Cauchy M (close: 51-62/64 distinct per block).
Objective: colliding rows + 1000*(singular) + 1000*(SAC-a violations).
Move: single bit flip."""
import numpy as np, math, pickle
from diffusion import gf2_rank

def cost_fast(M):
    """without rank check (call sparingly)"""
    c = 0
    for qb in range(8):
        seen = set()
        for i in range(64):
            v = 0
            for l in range(8):
                v |= int(M[i, qb*8+l]) << l
            if v == 0 or v in seen:
                c += 1
            seen.add(v)
    for i in range(64):
        for qb in range(8):
            if M[i, qb*8:(qb+1)*8].sum() == 0:
                c += 1000
    return c

def cost(M):
    return cost_fast(M) + (0 if gf2_rank(M) == 64 else 100000)

def main():
    rng = np.random.default_rng(31337)
    M = np.load('M64.npy').copy()
    cur = cost(M)
    print("initial cost:", cur, flush=True)
    T = 10.0
    best = cur
    bestM = M.copy()
    it = 0
    # verify initial invertible
    assert gf2_rank(M) == 64
    while cur > 0 and it < 500000:
        i = int(rng.integers(0, 64)); j = int(rng.integers(0, 64))
        M[i, j] ^= 1
        nc = cost_fast(M)
        if nc <= cur or rng.random() < math.exp((cur - nc) / T):
            cur = nc
            if cur < best:
                # lazy rank check on improvement
                if gf2_rank(M) == 64:
                    best = cur
                    bestM = M.copy()
                    print(f"it {it}: new best {best} (T={T:.3f})", flush=True)
                    if best == 0:
                        break
                else:
                    M[i, j] ^= 1  # revert: broke invertibility
                    cur = cost_fast(M)
                    continue
        else:
            M[i, j] ^= 1
        it += 1
        T *= 0.999995
        if it % 50000 == 0:
            print(f"it {it}: cur {cur} best {best} T={T:.4f}", flush=True)
    print("final best:", best)
    if best == 0:
        np.save('M64_bic.npy', bestM)
        rw = bestM.sum(axis=1)
        print("max row weight:", int(rw.max()), "XOR levels:", math.ceil(math.log2(int(rw.max()))))
        print("rank:", gf2_rank(bestM))
        print("saved M64_bic.npy")

if __name__ == '__main__':
    main()
