"""S2-proxy v3: extends v2 methodology (sequential x, dedupe, 115 deltas)
with NEW stage types for genuinely-new axes:
  ('and',a,b,c)      x ^= (ra&rb)^rc
  ('t3',a,b,c,e)     x ^= (ra&rb)^rc^re
  ('dual',a,b,c,d,e) x ^= (ra&rb)^(rc&rd)^re
  ('maj',a,b,c,d)    x ^= maj(ra,rb,rc)^rd, maj=(a&b)|(b&c)|(a&c)
  ('sbox',)          x = sbox64(x)            (rasC2_0 per nibble)
  ('sboxL',a,b)      x = sbox64(x); x ^= ra^rb
"""
import numpy as np
import sys

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
SBOXES = {
 'rasC2_0': [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],
 'SKINNY':  [0xC,0x6,0x9,0x0,0x1,0xA,0x7,0xB,0x3,0xE,0xF,0x8,0x4,0xD,0x5,0x2],
 'TWINE':   [0xE,0x1,0xB,0x6,0xF,0xD,0x0,0xA,0x7,0x3,0xC,0x9,0x2,0x8,0x4,0x5],
 'KLEIN':   [0x7,0x4,0xA,0x9,0x1,0xF,0xB,0x0,0xC,0x3,0x2,0x6,0x8,0xE,0xD,0x5],
 'PRINCE':  [0xB,0xF,0x3,0x2,0xA,0xC,0x9,0x1,0x6,0x7,0x8,0x0,0xE,0x5,0xD,0x4],
 'QARMA_s2':[0x2,0xC,0xE,0x8,0x6,0xF,0xB,0x0,0x1,0x4,0xD,0x7,0x9,0x3,0xA,0x5],
}
SBOX = np.array(SBOXES['rasC2_0'], dtype=np.uint64)  # default; set via set_sbox

def set_sbox(name):
    global SBOX
    SBOX = np.array(SBOXES[name], dtype=np.uint64)

def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def sbox64(x):
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4 * i)) & np.uint64(0xF)
        y |= SBOX[nib] << np.uint64(4 * i)
    return y & M64


def psbox64(x, hi):
    """Partial S-box: 8 nibbles on hi32 (hi=1) or lo32 (hi=0), passthrough."""
    y = np.zeros_like(x)
    base = 8 if hi else 0
    for i in range(8):
        nib = (x >> np.uint64(4 * (base + i))) & np.uint64(0xF)
        y |= SBOX[nib] << np.uint64(4 * (base + i))
    # passthrough the other half
    mask = np.uint64(0xFFFFFFFF00000000) if hi else np.uint64(0x00000000FFFFFFFF)
    keep = (x & ~mask) & M64
    return (y | keep) & M64

def maj3(a, b, c):
    return ((a & b) | (b & c) | (a & c)) & M64

def apply_stage(x, st):
    t = st[0]
    if t == 'and':
        _, a, b, c = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    if t == 't3':
        _, a, b, c, e = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, e)) & M64
    if t == 'dual':
        _, a, b, c, d, e = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, c) & rotl(x, d))
                ^ rotl(x, e)) & M64
    if t == 'maj':
        _, a, b, c, d = st
        return (x ^ maj3(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, d)) & M64
    if t == 'sbox':
        return sbox64(x)
    if t == 'sboxL':
        _, a, b = st
        x = sbox64(x)
        return (x ^ rotl(x, a) ^ rotl(x, b)) & M64
    if t == 'psboxL':
        # partial sbox layer: ('psboxL',a,b,hi)
        _, a, b, hi = st
        x = psbox64(x, hi)
        return (x ^ rotl(x, a) ^ rotl(x, b)) & M64
    if t == 't4':
        _, a, b, c, d, e = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)
                ^ rotl(x, e)) & M64
    if t == 't5':
        _, a, b, c, d, e, f = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)
                ^ rotl(x, e) ^ rotl(x, f)) & M64
    if t == 'sdual':
        # shared-rb dual: x ^= (ra&rb)^(rb&rc)^rd ; triple-miss quiet
        _, a, b, c, d = st
        rb = rotl(x, b)
        return (x ^ (rotl(x, a) & rb) ^ (rb & rotl(x, c))
                ^ rotl(x, d)) & M64
    raise ValueError(st)

def mix_stages(x, stages):
    for st in stages:
        x = apply_stage(x, st)
    return x

def all_deltas():
    deltas = [0x400, 0x4000000]
    for k in range(64):
        deltas.append(1 << k)
    for d in [3, 5, 9, 0x11, 0x8000000000000001, 0x100000001,
              0xF0F0F0F0F0F0F0F0, 0xFFFFFFFFFFFFFFFF]:
        if d not in deltas:
            deltas.append(d)
    for v in range(1, 16):
        for nib in [0, 7, 8, 15]:
            d = v << (4 * nib)
            if d not in deltas:
                deltas.append(d)
    return deltas

def maxz_for_delta(mix_fn, d0, logN=20):
    N = 1 << logN
    xs = np.arange(N, dtype=np.uint64)
    xs = xs[xs <= (xs ^ np.uint64(d0))]
    npairs = len(xs)
    K = np.full(npairs, np.uint64(0x123456789ABCDEF0))
    y0 = mix_fn(xs, K)
    y1 = mix_fn(xs ^ np.uint64(d0), K)
    d = (y0 ^ y1).astype(np.uint64)
    bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :]))
              & np.uint64(1)).astype(np.float64)
    mm = bitmat.mean(axis=0)
    z = (mm - 0.5) / np.sqrt(0.25 / npairs)
    az = np.abs(z)
    return az.max(), int(np.argmax(az)), npairs

def s2proxy_v3(stages, logN=20, verbose=False):
    def mix_fn(xs, K):
        x = (xs ^ K) & M64
        return mix_stages(x, stages)
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if verbose and z > 9:
            print(f"    d0={d0:#018x}: max|z|={z:.1f} @bit{b}", flush=True)
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

COST = {'and': 3.35, 't3': 4.5, 'dual': 5.0, 'maj': 4.3, 'sbox': 4.0,
        'sboxL': 5.5, 't4': 5.6, 't5': 5.6, 'sdual': 4.2, 'psboxL': 4.5}

def cost_est(stages):
    return sum(COST[s[0]] for s in stages)

# ---- Wave P1: 4-stage genuinely-new axes ----
T3A = ('t3', 1, 7, 13, 29)
T3B = ('t3', 3, 11, 19, 37)
T3C = ('t3', 5, 15, 25, 41)
ANDA = ('and', 1, 2, 13)
ANDB = ('and', 7, 19, 5)
ANDC = ('and', 3, 11, 29)
DUALA = ('dual', 10, 5, 55, 41, 3)

P1 = {
    # t3 front-end + S-box last (NEW: 3^3=27 >= 16 nibbles by fan-out counting)
    "P1a_t3x3_sboxL": [T3A, T3B, T3C, ('sboxL', 5, 13)],
    "P1a2_t3x3_sbox": [T3A, T3B, T3C, ('sbox',)],          # is L load-bearing?
    "P1b_t3t3and_sboxL": [T3A, T3B, ANDC, ('sboxL', 5, 13)],
    "P1c_t3andand_sboxL": [T3A, ANDB, ANDC, ('sboxL', 5, 13)],
    "P1d_andx3_sboxL": [ANDA, ANDB, ANDC, ('sboxL', 5, 13)],  # control: expect FAIL
    # dual last stage, 4-stage variants (track-5 batch-18 is 5-stage)
    "P1e_t3x3_dual": [T3A, T3B, T3C, DUALA],
    "P1f_t3t3and_dual": [T3A, T3B, ANDC, DUALA],
    # controls
    "P1g_t3x4": [T3A, T3B, T3C, ('t3', 9, 21, 31, 49)],       # expect FAIL (4-stage wall)
    "P1h_majx4": [('maj', 1, 7, 13, 29), ('maj', 3, 11, 19, 37),
                  ('maj', 5, 15, 25, 41), ('maj', 9, 21, 31, 49)],
}

# ---- Wave P2: high-fan-out linear front-end + strict-quiet last stage ----
# Rationale: P1 failed because d_3 (3 t3 stages, 3^3=27) can't cover 16 S-box
# nibbles against stuck bits. t4/t5 stages give 4^2=16 / 5^2=25 certain
# coverage in just 2 stages.
T4A = ('t4', 1, 7, 13, 29, 41)
T4B = ('t4', 3, 11, 19, 37, 53)
T5A = ('t5', 1, 7, 13, 29, 41, 55)
T5B = ('t5', 3, 11, 19, 37, 53, 5)

P2 = {
    "P2a_t4x2_sboxL": [T4A, T4B, ('sboxL', 5, 13)],
    "P2b_t5x2_sboxL": [T5A, T5B, ('sboxL', 5, 13)],
    "P2c_t4x2_dual": [T4A, T4B, DUALA],
    "P2d_t5x2_dual": [T5A, T5B, DUALA],
    "P2e_t3t3_sboxLx2": [T3A, T3B, ('sboxL', 5, 13), ('sboxL', 11, 29)],
    "P2f_t4_t3_sboxL": [T4A, T3B, ('sboxL', 5, 13)],
}

# ---- Wave P3: cascaded S-box layers with dev-4 S-box (SKINNY-class) ----
# P2e [t3,t3,sboxL,sboxL] hit z=14.5 (gray zone). S-box layers bootstrap
# difference weight: each layer spreads wt-1 -> wt-1..3 (avg ~2).
P3 = {
    "P3a_t3and_sboxLx2": [T3A, ANDC, ('sboxL', 5, 13), ('sboxL', 5, 13)],
    "P3b_t3t3_sbox_sboxL": [T3A, T3B, ('sbox',), ('sboxL', 5, 13)],
    "P3c_t3_sboxLx2": [T3A, ('sboxL', 5, 13), ('sboxL', 5, 13)],
    "P3d_and_sboxLx3": [ANDA, ('sboxL', 5, 13), ('sboxL', 5, 13), ('sboxL', 5, 13)],
    "P3e_t3t3_sboxLx2": [T3A, T3B, ('sboxL', 5, 13), ('sboxL', 5, 13)],
    "P3f_t3x3_sboxL": [T3A, T3B, T3C, ('sboxL', 5, 13)],
    "P3g_t3t3_sboxL": [T3A, T3B, ('sboxL', 5, 13)],
}

# ---- Wave P4: sdual (shared-rb dual) + sbox-middle variants ----
P4 = {
    "P4a_t3t3_sboxLx2_skn": [T3A, T3B, ('sboxL', 5, 13), ('sboxL', 11, 29)],
    "P4b_t3_sbox_and_sboxL": [T3A, ('sbox',), ANDC, ('sboxL', 5, 13)],
    "P4c_and_sbox_and_sboxL": [ANDA, ('sbox',), ANDC, ('sboxL', 5, 13)],
    "P4d_sdualx5": [('sdual', 1, 7, 13, 29), ('sdual', 3, 11, 19, 37),
                    ('sdual', 5, 15, 25, 41), ('sdual', 9, 21, 31, 49),
                    ('sdual', 13, 27, 37, 55)],
    "P4e_sdualx4": [('sdual', 1, 7, 13, 29), ('sdual', 3, 11, 19, 37),
                    ('sdual', 5, 15, 25, 41), ('sdual', 9, 21, 31, 49)],
    "P4f_t3t3_sdual_sdual": [T3A, T3B, ('sdual', 5, 15, 25, 41),
                             ('sdual', 9, 21, 31, 49)],
    "P4g_t3t3_sboxLx2_r": [T3A, T3B, ('sboxL', 5, 13), ('sboxL', 3, 17)],
}

# ---- Wave P5: partial-S-box (8 nibbles/layer, alternating halves) ----
P5 = {
    "P5a_t3t3_psboxLx2": [T3A, T3B, ('psboxL', 2, 8, 1), ('psboxL', 41, 13, 1)],
    "P5b_t3t3_psboxLx2_alt": [T3A, T3B, ('psboxL', 2, 8, 1), ('psboxL', 41, 13, 0)],
    "P5c_t3t3_psboxLx2_b": [T3A, T3B, ('psboxL', 5, 13, 1), ('psboxL', 11, 29, 0)],
}

WAVES = {'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4, 'P5': P5}

if __name__ == '__main__':
    logN = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    only = sys.argv[2] if len(sys.argv) > 2 else None
    if only == '-':
        only = None
    wavearg = sys.argv[3] if len(sys.argv) > 3 else 'P1'
    wave = WAVES[wavearg]
    sb = sys.argv[4] if len(sys.argv) > 4 else 'rasC2_0'
    set_sbox(sb)
    print(f"# wave={wavearg} sbox={sb} logN={logN}", flush=True)
    for name, st in wave.items():
        if only and only not in name:
            continue
        z, d, b = s2proxy_v3(st, logN=logN)
        print(f"{name}: v3 proxy max|z|={z:7.1f} (d0={d:#x} bit{b}), "
              f"est={cost_est(st):.2f}u", flush=True)
