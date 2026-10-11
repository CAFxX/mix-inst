#!/usr/bin/env python3
"""Linear-mask trail metric for co-designing affine P-boxes.

Round: x -> S -> P -> L -> y,  L(x)=x^R^ra x^R^rb x.
Backward mask propagation: output mask mu -> L^T(mu) = mu ^ R^{-ra} mu ^ R^{-rb} mu
(deterministic; R^T = R^{-1}). Cost of the round = number of active nibbles of
L^T(mu) (each crossed S-box contributes S-box linear bias). Then mu := P^{-1}
permute of the mask, and continue backward.

Metric: for each single-bit start mask, total cost over 4 backward rounds;
cipher score = MIN over starts. Larger = every single-bit-mask linear trail
crosses more S-boxes = weaker linear characteristics = better.

This is a RANKING heuristic only. S1/S2 decide.
"""
import sys
import numpy as np

FULL = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl64(x, r):
    r = int(r) % 64
    if r == 0:
        return x
    return (((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & FULL).astype(np.uint64)

def nibble_count(masks):
    c = np.zeros_like(masks)
    for n in range(16):
        c += (((masks >> np.uint64(4 * n)) & np.uint64(0xF)) != 0).astype(np.uint64)
    return c

def lin_t_scores(ra, rb, rounds=4):
    # masks: (N=2048*64) start masks; Pinv per row
    pairs = [(a, b) for a in range(1, 64, 2) for b in range(64)]
    N = len(pairs)
    Pinv = np.zeros((N, 64), dtype=np.uint64)
    for k, (a, b) in enumerate(pairs):
        for i in range(64):
            Pinv[k, (a * i + b) % 64] = i
    starts = np.repeat(np.array([np.uint64(1 << j) for j in range(64)], dtype=np.uint64)[None, :], N, axis=0).reshape(N * 64)
    Pinv = np.repeat(Pinv, 64, axis=0)
    masks = starts.copy()
    total = np.zeros(N * 64, dtype=np.uint64)
    for _ in range(rounds):
        # L^T: mu ^ R^{-ra} mu ^ R^{-rb} mu = mu ^ rotl(mu,64-ra) ^ rotl(mu,64-rb)
        lt = (masks ^ rotl64(masks, 64 - ra) ^ rotl64(masks, 64 - rb)) & FULL
        total += nibble_count(lt)
        # P^{-1} permute: new bit j = old bit Pinv[j]
        bits = ((lt[:, None] >> Pinv) & np.uint64(1))
        masks = (bits * (np.uint64(1) << np.arange(64, dtype=np.uint64))).sum(axis=1).astype(np.uint64)
    worst = total.reshape(N, 64).min(axis=1)   # attacker picks best start
    avg = total.reshape(N, 64).mean(axis=1)
    return pairs, worst, avg

def main():
    ra = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rb = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    pairs, worst, avg = lin_t_scores(ra, rb)
    order = np.lexsort((avg, -worst))  # max worst first, then max avg
    print(f"# lin({ra},{rb}): min-over-starts 4-round active-Sbox count (bigger=better)")
    for k in order:
        a, b = pairs[k]
        print(f"  ({a:2d},{b:2d})  min={int(worst[k]):2d} avg={avg[k]:.2f}")

if __name__ == "__main__":
    main()
