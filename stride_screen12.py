#!/usr/bin/env python3
"""Power-of-2 stride screen for the 12-round SPN (independent check).

For each (key, stride) with stride = 2^k (k=0..63), plus 3*2^k samples and
j=3: hash I, I+j, ... (N=2^18), then per-bit monobit max|z| plus a reduced
set of reductions (Lemire X=10, X=1000 with exact nulls; mask m=8; mod 7).

Flags: per-bit max|z| > 4.0, or any reduction |z| > 4.5.
"""
import sys, time
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix")
from spn import mix_spn_np, U64
from tests_final import lemire_np, chi2_z, chi2_z_exact, lemire_preimg, mod_preimg, W64

ROUNDS = 12
N = 1 << 18
BIT = np.arange(64, dtype=np.uint64)

KEYS = [0x0000000000000000, 0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA,
        0x5555555555555555, 0xDEADBEEFDEADBEEF, 0x9E3779B97F4A7C15,
        0x0000000000001234, 0x123456789ABCDEF0, 0x0FEDCBA987654321,
        0x8000000000000000, 0x0000000000000001, 0xCAFEBABEDEADBEEF]
STRIDES = ([1 << k for k in range(64)] +
           [3 * (1 << k) for k in (0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 48)] + [3])

def lemire_z(S, X):
    R = lemire_np(S, X)
    if X <= 1024:
        bounds = list(range(X + 1))
    else:
        B = 1024
        bounds = [(k * X) // B for k in range(B + 1)]
    nb = len(bounds) - 1
    E = np.array([lemire_preimg(bounds[k], bounds[k + 1], X) * N / W64
                  for k in range(nb)])
    if X <= 1024:
        cnt = np.bincount(R.astype(np.int64), minlength=X).astype(float)
    else:
        idx = np.digitize(R.astype(object), bounds[1:-1], right=False)
        cnt = np.bincount(np.asarray(idx, dtype=np.int64), minlength=nb).astype(float)
    return chi2_z_exact(cnt, E)

def main():
    t0 = time.time()
    nflag = 0
    worst = (0.0, None)  # (max|z|, description)
    total = len(KEYS) * len(STRIDES)
    done = 0
    for key in KEYS:
        K = np.full(N, U64(key), dtype=np.uint64)
        for j in STRIDES:
            V = (U64(j) * np.arange(N, dtype=np.uint64))  # I = 0
            S = mix_spn_np(V, K, rounds=ROUNDS)
            bitcnt = ((S[:, None] >> BIT) & U64(1)).sum(axis=0).astype(float)
            bz = np.abs((bitcnt - N / 2) / np.sqrt(N / 4))
            pb = float(bz.max()); pb_bit = int(bz.argmax())
            zs = [("lemire-X=10", lemire_z(S, 10)),
                  ("lemire-X=1000", lemire_z(S, 1000)),
                  ("mask-m=8", chi2_z(np.bincount((S & U64(255)).astype(np.int64),
                                                 minlength=256).astype(float), N)),
                  ("mod-7", chi2_z_exact(
                      np.bincount((S % np.uint64(7)).astype(np.int64),
                                  minlength=7).astype(float),
                      np.array(mod_preimg(7), dtype=np.float64) * (N / W64)))]
            w = max(abs(z) for _, z in zs)
            desc = f"key={key:#018x} j={j:#018x} perbit-max|z|={pb:.2f}(bit{pb_bit}) " + \
                   " ".join(f"{n}={z:+.2f}" for n, z in zs)
            if pb > worst[0]:
                worst = (pb, desc)
            flag = pb > 4.0 or w > 4.5
            if flag:
                nflag += 1
                print("FLAG " + desc, flush=True)
            done += 1
            if done % 100 == 0:
                print(f"... {done}/{total} ({time.time()-t0:.0f}s)", flush=True)
    print(f"DONE: {total} (key,stride) combos, {nflag} flags, "
          f"worst per-bit |z| = {worst[0]:.2f}", flush=True)
    print("WORST: " + worst[1], flush=True)
    print(f"elapsed {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
