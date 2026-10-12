"""Statistical SAC/BIC evaluation of F(x) = M . S^8(x), 64x64.
Direct measurement via sampling (2^64 exhaustive impossible).
SAC: for each input bit i, flip rate of each output bit over N samples (want ~0.5).
BIC: for each input bit i, max |correlation| over output pairs (want ~0)."""
import numpy as np

def load_F(sbox_path='S_table.npy', m_path='M64.npy'):
    S = np.load(sbox_path)
    M = np.load(m_path)
    # precompute M rows as (64,8) byte-masks per byte-block for speed
    # F(x): split x (uint64) into 8 bytes, S each, concat to 64-bit vector, multiply by M
    return S, M

def F_batch(XS, S, M):
    """XS: (N,) uint64 -> (N,) uint64. Pure numpy."""
    N = XS.shape[0]
    # bytes: (N,8)
    B = np.zeros((N, 8), dtype=np.uint8)
    for q in range(8):
        B[:, q] = S[(XS >> np.uint64(8*q)) & np.uint64(0xFF)]
    # bit vector (N,64)
    V = np.zeros((N, 64), dtype=np.uint8)
    for q in range(8):
        for l in range(8):
            V[:, q*8+l] = (B[:, q] >> l) & 1
    # Y = V @ M.T  (mod 2)
    Y = (V @ M.T) % 2
    # pack to uint64
    out = np.zeros(N, dtype=np.uint64)
    for j in range(64):
        out |= Y[:, j].astype(np.uint64) << np.uint64(j)
    return out

def avalanche_stats(S, M, N=20000, seed=7):
    rng = np.random.default_rng(seed)
    XS = rng.integers(0, 2**64, size=N, dtype=np.uint64)
    Y0 = F_batch(XS, S, M)
    print(f"sac: testing 64 input bits x {N} samples...", flush=True)
    worst_sac = 0  # max |fliprate - 0.5|
    for i in range(64):
        Y1 = F_batch(XS ^ (np.uint64(1) << np.uint64(i)), S, M)
        D = Y0 ^ Y1  # (N,) uint64, bit j = avalanche of output j
        for j in range(64):
            fr = float(((D >> np.uint64(j)) & np.uint64(1)).mean())
            worst_sac = max(worst_sac, abs(fr - 0.5))
        if i % 16 == 15:
            print(f"  bit {i}: worst |flip-0.5| so far = {worst_sac:.4f}", flush=True)
    print("SAC worst |flip_rate - 0.5| =", round(worst_sac, 4))
    return worst_sac

def bic_stats(S, M, N=20000, seed=11, pairs_per_bit=200):
    rng = np.random.default_rng(seed)
    XS = rng.integers(0, 2**64, size=N, dtype=np.uint64)
    Y0 = F_batch(XS, S, M)
    print(f"bic: testing 64 input bits x {pairs_per_bit} pairs x {N} samples...", flush=True)
    worst_corr = 0.0
    for i in range(64):
        Y1 = F_batch(XS ^ (np.uint64(1) << np.uint64(i)), S, M)
        D = Y0 ^ Y1
        A = np.zeros((N, 64), dtype=np.uint8)
        for j in range(64):
            A[:, j] = ((D >> np.uint64(j)) & np.uint64(1)).astype(np.uint8)
        # sample pairs
        prng = np.random.default_rng(1000 + i)
        for _ in range(pairs_per_bit):
            j, k = prng.choice(64, size=2, replace=False)
            aj, ak = A[:, j].astype(float), A[:, k].astype(float)
            # correlation; guard zero variance
            sj, sk = aj.std(), ak.std()
            if sj < 1e-9 or sk < 1e-9:
                c = 1.0
            else:
                c = abs(np.corrcoef(aj, ak)[0, 1])
            worst_corr = max(worst_corr, c)
        if i % 16 == 15:
            print(f"  bit {i}: worst |corr| so far = {worst_corr:.4f}", flush=True)
    print("BIC worst |corr| =", round(worst_corr, 4))
    return worst_corr

if __name__ == '__main__':
    import sys
    S, M = load_F()
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    avalanche_stats(S, M, N=N)
    bic_stats(S, M, N=N)
