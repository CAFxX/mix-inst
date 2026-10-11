#!/usr/bin/env python3
"""Batch-50 CO-DESIGN PROBE (hard constraint): feasibility of bijective
QUADRATIC 4-bit S-boxes with <= k AND monomials.

Cleaner than probe_lowand.py's penalty form: the AND pattern is FIXED
to a specific set of k pairs (out of the 6 possible), so the cap holds
by construction, and the anneal optimizes ONLY the linear part
(4 components x (1 const + 4 linear + k AND-coeffs) bits) with
energy = 1000*coll + DU + LATbias/8 + 32*(S(0)==0).

For each k in {2,3} and each pair-pattern, an independent anneal runs;
the best (coll, DU, LAT, S0) per pattern is reported. If ANY pattern
reaches coll=0 + DU<=8 + S(0)!=0, the batch-50 minimal-AND axis is
viable with that S-box. If no pattern does, the deferred lead is CUT
ON MEASUREMENT (family floor established by exhaustive-pattern
search, not by penalty-landscape luck).

Usage: probe_lowand_hard.py <k> <steps> [nstart]
Checkpoint: probe_lowand_hard.k<k>.starts.jsonl (per pattern+start).
"""
import itertools
import json
import os
import sys

import numpy as np

N = 16
X = np.arange(N)
XB = ((X[:, None] >> np.arange(4)) & 1)          # (16,4) input bits
PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
XQ = np.stack([XB[:, i] * XB[:, j] for i, j in PAIRS], axis=1)  # (16,6)
PAR = np.array([bin(v).count("1") & 1 for v in range(N)])


def build_from(P, pat):
    # P: (4, 5+k) binary: [const, lin0..3, andcoeff_0..k-1]
    # pat: tuple of k pair-indices into PAIRS
    c, L, M = P[:, 0:1], P[:, 1:5], P[:, 5:5 + len(pat)]
    XQp = XQ[:, list(pat)]                        # (16,k)
    Y = (c.T + XB @ L.T + XQp @ M.T) & 1          # (16,4)
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
    PSM = PAR[SM & MOM]
    lb = 0
    for mi in range(1, N):
        px = PAR[X & mi]
        C = np.sum(px[None, :] ^ PSM ^ 1, axis=1)
        b_ = int(np.max(np.abs(C - 8)))
        if b_ > lb:
            lb = b_
    return coll, du, lb


def energy_of(P, pat):
    S = build_from(P, pat)
    coll, du, lb = profile(S)
    e = 1000 * coll + du + lb / 8.0 + 32 * (int(S[0]) == 0)
    return e, S, (coll, du, lb)


def anneal(seed, pat, steps):
    k = len(pat)
    rng = np.random.default_rng(seed)
    P = rng.integers(0, 2, size=(4, 5 + k)).astype(np.uint8)
    e, S, prof = energy_of(P, pat)
    bP, bS, be, bprof = P.copy(), S.copy(), e, prof
    T0, T1 = 8.0, 0.05
    lr = np.log(T1 / T0) / steps
    npar = 4 * (5 + k)
    for t in range(steps):
        T = T0 * np.exp(lr * t)
        o = int(rng.integers(0, npar))
        oo, kk = divmod(o, 5 + k)
        P[oo, kk] ^= 1
        e2, S2, prof2 = energy_of(P, pat)
        if e2 < e or rng.random() < np.exp((e - e2) / T):
            e, S, prof = e2, S2, prof2
            if e2 < be:
                be, bP, bS, bprof = e2, P.copy(), S2.copy(), prof2
        else:
            P[oo, kk] ^= 1
    return be, bprof, bS


def main():
    k = int(sys.argv[1])
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    nstart = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    patterns = list(itertools.combinations(range(6), k))
    ckpt = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "probe_lowand_hard.k%d.starts.jsonl" % k)
    done = {}
    if os.path.exists(ckpt):
        with open(ckpt) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    done[(r["pi"], r["s"])] = r
    print("k=%d: %d patterns x %d starts x %d steps" %
          (k, len(patterns), nstart, steps), flush=True)
    best = None
    for pi, pat in enumerate(patterns):
        patname = "+".join("x%dx%d" % PAIRS[i] for i in pat)
        for s in range(nstart):
            key = (pi, s)
            if key in done:
                r = done[key]
                be, bprof = r["be"], tuple(r["bprof"])
                bS = np.array(r["bS"], dtype=np.uint8)
                print("pat %2d [%s] start %d: SKIP E=%.1f coll=%d DU=%d "
                      "LAT=%d S0=%d" % (pi, patname, s, be, bprof[0],
                                       bprof[1], bprof[2], int(bS[0])),
                      flush=True)
            else:
                be, bprof, bS = anneal(0xB510 + 1000 * k + 37 * pi + s,
                                      pat, steps)
                with open(ckpt, "a") as f:
                    f.write(json.dumps({
                        "pi": pi, "s": s, "pat": list(pat),
                        "patname": patname, "k": k,
                        "seed": hex(0xB510 + 1000 * k + 37 * pi + s),
                        "be": be, "bprof": [int(v) for v in bprof],
                        "bS": [int(v) for v in bS]}) + "\n")
                print("pat %2d [%s] start %d: E=%.1f coll=%d DU=%d LAT=%d "
                      "S0=%d" % (pi, patname, s, be, bprof[0], bprof[1],
                                 bprof[2], int(bS[0])), flush=True)
            cand = (bprof[0], bprof[1], bprof[2], int(bS[0]) == 0, pi, s,
                    patname, bS)
            if best is None or cand[:4] < best[:4]:
                best = cand
    print("HARD-PROBE BEST[k=%d]: coll=%d DU=%d LAT=%d S0zero=%s pat=%s" %
          (k, best[0], best[1], best[2], best[3], best[6]))
    print("HARD-PROBE BEST_LUT[k=%d]=[%s]" %
          (k, ",".join(str(int(v)) for v in best[7])))
    # Viability gate for the batch-50 axis.
    viable = best[0] == 0 and best[1] <= 8 and not best[3]
    print("VIABILITY[k=%d]: %s" %
          (k, "VIABLE" if viable else "NOT VIABLE (cut on measurement)"))


if __name__ == "__main__":
    main()
