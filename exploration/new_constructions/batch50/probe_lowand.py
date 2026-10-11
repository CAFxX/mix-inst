#!/usr/bin/env python3
"""Batch-50 CO-DESIGN PROBE: feasibility of bijective QUADRATIC 4-bit
S-boxes with a HARD CAP on AND-monomial count.

This is the gate for the batch-49 deferred lead ("cost-driven
quadratic-S-box mining: minimize AND-monomials s.t. bijective + DU<=8").
Q4 (batch-49) has 5 AND monomials -> 7.0u/stage (S0), vs the <4.83u/stage
budget for 4st viability. A bijective quadratic S-box with AND<=3 and
DU<=8 would project to ~4.2-4.7u/stage -- a real chance. If the family's
floor is 5 (or DU collapses below the cap), the deferred lead is CUT ON
MEASUREMENT and batch-50 pivots to the next-widest axis.

Objective per cap K: energy = 1000*coll + 64*max(0,ANDcount-K) + DU
  + LATbias/8 + 32*(S(0)==0)
i.e. bijectivity and the AND cap are hard (large weights), DU/LAT/S(0)
are optimized within the feasible set.

Usage: probe_lowand.py <K> <nstart> <steps>
Appends per-start checkpoints to probe_lowand.K<N>.starts.jsonl
(unstable-VM rule: checkpoint early and often).
"""
import json
import os
import sys

import numpy as np

N = 16
X = np.arange(N)
XB = ((X[:, None] >> np.arange(4)) & 1)          # (16,4) input bits
QP = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
XQ = np.stack([XB[:, i] * XB[:, j] for i, j in QP], axis=1)  # (16,6)
PAR = np.array([bin(v).count("1") & 1 for v in range(N)])     # parity table


def build(P):
    # P: (4,11) binary; returns S (16,) uint8
    c, L, Q = P[:, 0:1], P[:, 1:5], P[:, 5:11]
    Y = (c.T + XB @ L.T + XQ @ Q.T) & 1          # (16,4)
    return (Y * (1 << np.arange(4))).sum(axis=1).astype(np.uint8)


def profile(S):
    coll = N - len(set(S.tolist()))
    du = 0
    for din in range(1, N):
        cnt = np.bincount(S ^ S[X ^ din], minlength=N)
        m = int(cnt.max())
        if m > du:
            du = m
    SM = S[None, :]
    MOM = np.arange(1, N)[:, None]
    PSM = PAR[SM & MOM]                        # (15,16)
    lb = 0
    for mi in range(1, N):
        px = PAR[X & mi]                       # (16,)
        C = np.sum(px[None, :] ^ PSM ^ 1, axis=1)   # (15,)
        b_ = int(np.max(np.abs(C - 8)))
        if b_ > lb:
            lb = b_
    return coll, du, lb


def andcount(P):
    return int(np.count_nonzero(P[:, 5:11]))


def energy_of(P, K):
    S = build(P)
    coll, du, lb = profile(S)
    ac = andcount(P)
    e = (1000 * coll + 64 * max(0, ac - K) + du + lb / 8.0
         + 32 * (int(S[0]) == 0))
    return e, S, (coll, du, lb, ac)


def anneal(seed, K, steps=10000):
    rng = np.random.default_rng(seed)
    P = rng.integers(0, 2, size=(4, 11)).astype(np.uint8)
    e, S, prof = energy_of(P, K)
    bP, bS, be, bprof = P.copy(), S.copy(), e, prof
    T0, T1 = 8.0, 0.05
    lr = np.log(T1 / T0) / steps
    for t in range(steps):
        T = T0 * np.exp(lr * t)
        o, k = int(rng.integers(0, 4)), int(rng.integers(0, 11))
        P[o, k] ^= 1
        e2, S2, prof2 = energy_of(P, K)
        if e2 < e or rng.random() < np.exp((e - e2) / T):
            e, S, prof = e2, S2, prof2
            if e2 < be:
                be, bP, bS, bprof = e2, P.copy(), S2.copy(), prof2
        else:
            P[o, k] ^= 1
    return be, bprof, bS


def main():
    K = int(sys.argv[1])
    nstart = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    ckpt = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "probe_lowand.K%d.starts.jsonl" % K)
    done = {}
    if os.path.exists(ckpt):
        with open(ckpt) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    done[r["k"]] = r
    if done:
        print("checkpoint: %d/%d starts already done, skipping"
              % (len(done), nstart), flush=True)
    res = []
    for k in range(nstart):
        if k in done:
            r = done[k]
            bS = np.array(r["bS"], dtype=np.uint8)
            be, bprof = r["be"], tuple(r["bprof"])
            print("start %d: SKIP (checkpointed) energy=%.3f coll=%d DU=%d "
                  "LATbias=%d AND=%d S0=%d"
                  % (k, be, bprof[0], bprof[1], bprof[2], bprof[3],
                     int(bS[0])), flush=True)
        else:
            be, bprof, bS = anneal(0xB500 + 100 * K + k, K, steps)
            with open(ckpt, "a") as f:
                f.write(json.dumps({
                    "k": k, "seed": hex(0xB500 + 100 * K + k), "K": K,
                    "be": be, "bprof": [int(v) for v in bprof],
                    "bS": [int(v) for v in bS]}) + "\n")
            print("start %d: energy=%.3f coll=%d DU=%d LATbias=%d AND=%d "
                  "S0=%d" % (k, be, bprof[0], bprof[1], bprof[2], bprof[3],
                             int(bS[0])), flush=True)
        res.append((be, bprof, bS))
    res.sort(key=lambda r: (r[1][0], r[1][1], r[1][3], r[1][2]))
    be, bprof, bS = res[0]
    print("BEST[K=%d] coll=%d DU=%d LATbias=%d AND=%d S0=%d" %
          (K, bprof[0], bprof[1], bprof[2], bprof[3], int(bS[0])))
    print("BEST_LUT[K=%d]=[%s]" % (K, ",".join(str(int(v)) for v in bS)))


if __name__ == "__main__":
    main()
