#!/usr/bin/env python3
"""Batch-49: FAST heuristic search for bijective QUADRATIC 4-bit S-boxes.

Same objective as anneal_q4.py but fully numpy-vectorized
(~1000x faster per energy eval).
State: (4,11) binary quadratic ANF. Energy = 64*collisions + DU + LATbias/8.
"""
import json
import os
import sys

import numpy as np

# 2026-10-11: per-start checkpointing (unstable-VM rule — checkpoint early
# and often). Each completed start is appended to mine_q4_fast.starts.jsonl
# immediately; a resume skips checkpointed starts (same seeds -> deterministic,
# identical aggregate). A silent death can no longer lose completed starts.
CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "mine_q4_fast.starts.jsonl")


def load_ckpt():
    done = {}
    if os.path.exists(CKPT):
        with open(CKPT) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    done[r["k"]] = r
    return done


def save_ckpt(k, be, bprof, bS):
    with open(CKPT, "a") as f:
        f.write(json.dumps({"k": k, "seed": hex(0xB492 + k), "be": be,
                            "bprof": [int(v) for v in bprof],
                            "bS": [int(v) for v in bS]}) + "\n")

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
    # LAT max bias, vectorized over mo: PS[m] = parity(S & (m+1))
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


def energy(S):
    coll, du, lb = profile(S)
    return 64 * coll + du + lb / 8.0, (coll, du, lb)


def comp_degrees(S):
    degs = set()
    Sm = S
    for mask in range(1, N):
        f = PAR[Sm & mask]
        a = f.copy()
        step = 1
        for _ in range(4):
            # Moebius: a[x] ^= a[x^step] for x with step bit set
            idx = X ^ step
            upd = (X & step) != 0
            a2 = a.copy()
            a2[upd] ^= a[idx[upd]]
            a = a2
            step <<= 1
        nz = np.where(a == 1)[0]
        degs.add(max(int(bin(v).count("1")) for v in nz))
    return sorted(degs)


def anneal(seed, steps=25000):
    rng = np.random.default_rng(seed)
    P = rng.integers(0, 2, size=(4, 11)).astype(np.uint8)
    S = build(P)
    e, prof = energy(S)
    bP, bS, be, bprof = P.copy(), S.copy(), e, prof
    T0, T1 = 8.0, 0.05
    lr = np.log(T1 / T0) / steps
    for t in range(steps):
        T = T0 * np.exp(lr * t)
        o, k = int(rng.integers(0, 4)), int(rng.integers(0, 11))
        P[o, k] ^= 1
        S2 = build(P)
        e2, prof2 = energy(S2)
        if e2 < e or rng.random() < np.exp((e - e2) / T):
            e, prof, S = e2, prof2, S2
            if e2 < be:
                be, bP, bS, bprof = e2, P.copy(), S2.copy(), prof2
        else:
            P[o, k] ^= 1
    return be, bprof, bS


def main():
    nstart = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    done = load_ckpt()
    if done:
        print("checkpoint: %d/%d starts already done, skipping" %
              (len(done), nstart), flush=True)
    res = []
    for k in range(nstart):
        if k in done:
            r = done[k]
            bS = np.array(r["bS"], dtype=np.uint8)
            be, bprof = r["be"], tuple(r["bprof"])
            print("start %d: SKIP (checkpointed) energy=%.3f coll=%d DU=%d "
                  "LATbias=%d" % (k, be, bprof[0], bprof[1], bprof[2]),
                  flush=True)
        else:
            be, bprof, bS = anneal(0xB492 + k)
            save_ckpt(k, be, bprof, bS)
            print("start %d: energy=%.3f coll=%d DU=%d LATbias=%d compdeg=%s "
                  "S0=%d" % (k, be, bprof[0], bprof[1], bprof[2],
                             comp_degrees(bS), int(bS[0])), flush=True)
        res.append((be, bprof, bS))
    res.sort(key=lambda r: (r[1][0], r[1][1], r[1][2]))
    be, bprof, bS = res[0]
    print("BEST coll=%d DU=%d LATbias=%d compdeg=%s" %
          (bprof[0], bprof[1], bprof[2], comp_degrees(bS)))
    print("BEST_LUT=[%s]" % ",".join(str(int(v)) for v in bS))


if __name__ == "__main__":
    main()
