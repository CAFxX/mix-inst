#!/usr/bin/env python3
"""Analytical co-design screener (vectorized): affine P-boxes P(i)=(a*i+b)%64
for linear layer lin(x)=x^rotl(x,ra)^rotl(x,rb), with 4-bit S-box nibbles.

Bit-level reachability model of one SPN round:
  1. nibble closure (S-box mixes 4 bits of each active nibble)
  2. P-box permutation
  3. linear spread: out[j] depends on in[j], in[j-ra], in[j-rb]

State = batch of uint64 active-masks; one entry per ((a,b), start-nibble).
Single-bit starts in the same nibble are equivalent (nibble closure), so
16 starts per (a,b) suffice.

Usage: python3 affine_diffuse.py [ra] [rb]
"""
import sys
import numpy as np

FULL = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl64(x, r):
    r = int(r) % 64
    if r == 0:
        return x
    return (((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & FULL).astype(np.uint64)

def main():
    ra = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rb = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    pairs = [(a, b) for a in range(1, 64, 2) for b in range(64)]
    N = len(pairs)
    Pinv = np.zeros((N, 64), dtype=np.uint64)
    for k, (a, b) in enumerate(pairs):
        for i in range(64):
            Pinv[k, (a * i + b) % 64] = i
    # one start per nibble: single bit 4n
    masks = np.repeat(np.array([np.uint64(1 << (4 * n)) for n in range(16)], dtype=np.uint64)[None, :], N, axis=0).reshape(N * 16)
    Pinv = np.repeat(Pinv, 16, axis=0)
    N16 = N * 16
    done = np.zeros(N16, dtype=np.int32)          # round when full
    full_rounds = np.zeros(N16, dtype=np.int32)
    for r in range(1, 13):
        # one SPN round
        closed = np.zeros_like(masks)
        for n in range(16):
            bit4 = (masks >> np.uint64(4 * n)) & np.uint64(0xF)
            closed |= np.where(bit4 != 0, np.uint64(0xF << (4 * n)), np.uint64(0)).astype(np.uint64)
        bits = ((closed[:, None] >> Pinv) & np.uint64(1))
        perm = (bits * (np.uint64(1) << np.arange(64, dtype=np.uint64))).sum(axis=1).astype(np.uint64)
        masks = (perm | rotl64(perm, ra) | rotl64(perm, rb)) & FULL
        fin = masks == FULL
        new = fin & (done == 0)
        full_rounds[new] = r
        done |= fin
        if done.all():
            break
    full_rounds[done == 0] = 13  # didn't fully diffuse within 12 rounds
    worst = full_rounds.reshape(N, 16).max(axis=1)
    avg = full_rounds.reshape(N, 16).mean(axis=1)
    order = np.lexsort((avg, worst))
    print(f"# lin({ra},{rb}): worst-rounds, avg-rounds for full bit diffusion (cap 13=never)")
    for k in order:
        a, b = pairs[k]
        print(f"  ({a:2d},{b:2d})  worst={int(worst[k]):2d} avg={avg[k]:.2f}")

if __name__ == "__main__":
    main()
