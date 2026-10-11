#!/usr/bin/env python3
"""Wave-13 triage: bitsliced 4-bit S-box REPLACEMENT form with P-box diffusion.

Construction: x ^= K (pre-whiten); then per stage: x := S(x); x := rotl(x, p)
where S is a parallel bijective 4-bit S-box (all 16 nibbles) and p is a
per-stage rotation (P-box diffusion, 0-delay wiring). No x^= identity path,
no per-stage key (track-6: per-stage rk costs ~0.74u/stage).

Why: replacement form needs a BIJECTIVE nonlinearity (track-8 Axis B
diagnosis); chi is not bijective at n=64; minimal-MC 4-bit S-boxes are
bijective AND cheap (~2-3 gate levels/nibble bitsliced). Prior sboxL axis
parked on cost (7.55u) but used unoptimized full-width S-boxes.

KEEP bar: proxy z < 25 at 2^18 random 64-bit pairs, then strict reverify at
higher N. Cost is the binding question -> S0 on survivors (bit-exact RTL via gen).

METHODOLOGY (fixed 2026-10-10): input domain is RANDOM 64-bit pairs, NOT
s2proxy_v3's sequential arange(2^logN). The sequential domain freezes the
upper nibbles for per-nibble replacement forms, making out-of-cone output
bits trivially constant (|z|=256) -- a vacuous gate that would kill every
candidate. Random pairs match the real hash-finalization input model.

LAUNCH GATE: run only when `~/workspace/system/bin/load-shed.sh backoff`
exits 0. nice -n 19.
"""
import sys, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat')
import numpy as np
import s2proxy_v3 as P

POOL_PATH = ('/home/hatch/workspace/mix/exploration/round24/sbox_pool/'
             'literature_lowlatency_add2.txt')

def load_pool():
    pool = {}
    for line in open(POOL_PATH):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        pool[parts[0]] = np.array([int(x, 16) for x in parts[1:]],
                                  dtype=np.uint64)
    return pool

def sbox64(x, tab):
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4 * i)) & np.uint64(0xF)
        y |= tab[nib] << np.uint64(4 * i)
    return y & P.M64


# Nibble-transpose diffusion: bit(4a+b) -> bit(16b+a) (a=nibble 0..15,
# b=bit-in-nibble 0..3). 0-delay wiring like rotl, but each nibble's 4 bits
# land in 4 DIFFERENT nibbles -> cone doubles per stage (full nibble coverage
# in 2 S-box layers). Single-rotl diffusion was measured at ~+4 bits/stage
# (thousands of effectively-constant output bits at 6 stages) -- co-designed
# out. Precomputed per-nibble table for vectorized application.
_TRANS = np.zeros((16, 16), dtype=np.uint64)
for _a in range(16):
    for _v in range(16):
        _w = np.uint64(0)
        for _b in range(4):
            if (_v >> _b) & 1:
                _w |= np.uint64(1) << np.uint64(16 * _b + _a)
        _TRANS[_a, _v] = _w


def transpose64(x):
    y = np.zeros_like(x)
    for a in range(16):
        y |= _TRANS[a, (x >> np.uint64(4 * a)) & np.uint64(0xF)]
    return y


def make_mix(tab, nstages):
    def mix_fn(xs, K):
        x = (xs ^ K) & P.M64
        for _ in range(nstages):
            x = transpose64(sbox64(x, tab))
        return x & P.M64
    return mix_fn

# Fixed seed for reproducibility of the random-64-bit input domain.
RNG = np.random.default_rng(0x13A6E13)


def maxz_for_delta_rand64(mix_fn, d0, nPairs):
    # METHODOLOGY FIX 2026-10-10 (track-3): s2proxy_v3.maxz_for_delta uses
    # xs = arange(2^logN) -- a restricted sequential domain. For per-nibble
    # REPLACEMENT forms the S-boxes in nibbles >= logN/4 see CONSTANT inputs,
    # so output bits outside the reachable cone are trivially constant and
    # |z| saturates at 256 -- a vacuous gate (would kill every candidate).
    # Random full-64-bit pairs match the real input model (hash-state
    # finalization) and the S1/S2 null. Seed fixed for reproducibility.
    xs = RNG.integers(0, 2**64, size=nPairs, dtype=np.uint64)
    K = np.full(nPairs, np.uint64(0x123456789ABCDEF0))
    y0 = mix_fn(xs, K)
    y1 = mix_fn(xs ^ np.uint64(d0), K)
    d = (y0 ^ y1).astype(np.uint64)
    bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :]))
              & np.uint64(1)).astype(np.float64)
    mm = bitmat.mean(axis=0)
    z = (mm - 0.5) / np.sqrt(0.25 / nPairs)
    az = np.abs(z)
    nconst = int((az >= 200).sum())  # |z|>=200 <=> effectively constant bit
    return az.max(), int(np.argmax(az)), nconst


def triage_one(name, tab, nstages, nPairs=1 << 18):
    mix_fn = make_mix(tab, nstages)
    worst_z, worst_d, worst_b, tot_const = 0, None, None, 0
    for d0 in P.all_deltas():
        z, b, nc = maxz_for_delta_rand64(mix_fn, d0, nPairs)
        tot_const += nc
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b, tot_const

def main():
    pool = load_pool()
    boxes = ['BOYAR19_GF4INV', 'ULBC_s1', 'JIA25_12GE_R1', 'LU21_SKINNY',
             'ORTHROS_S0', 'PRINCE_S0', 'THF_BLINK_S0']
    # stage counts with nibble-transpose diffusion (co-designed; single-rotl
    # measured ~+4 bits/stage cone growth -- too weak, replaced)
    stage_counts = [4, 5, 6]
    t0 = time.time()
    n_try = n_keep = 0
    for name in boxes:
        tab = pool[name]
        for nst in stage_counts:
            n_try += 1
            z, d, b, nc = triage_one(name, tab, nst)
            mark = 'KEEP' if z < 25 else 'dead'
            if z < 25:
                n_keep += 1
            print(f"[{mark}] {name} {nst}st z={z:.1f} d={d:#x}@{b}"
                  f" constbits={nc}", flush=True)
    print(f"done: {n_try} tries, {n_keep} KEEP, {time.time()-t0:.0f}s")

if __name__ == '__main__':
    main()
