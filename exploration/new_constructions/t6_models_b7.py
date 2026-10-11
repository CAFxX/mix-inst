"""Track 6, batch 7: AND-OR fused constructions (genuinely new axis).

Batch 5 used majority (maj3): nonlinear in x but slow (5.94u/stage).
Batch 7 uses AND-OR: (x&a)|(b&c) — nonlinear in x (via x&a), but only
2 logic levels (AND then OR) vs maj3's 3-AND+OR.

Structure per stage:
  x = ((x & ra) | (rb & rc)) ^ ((rd & re) | (rf & rg)) ^ (rh & ri)

- (x & ra): nonlinear in x, breaks the fz_xor_trail linear trail
- (rb & rc), (rd & re), etc.: provide diffusion from other rotations
- XOR combines the three terms

Estimated: ~3u/stage (AND=1u, OR=1u, XOR-tree=1u) → 5 stages ≈ 15u.
This beats the 19.8u floor if statistical quality holds.

Candidates:
  t6_aor5a: 5-stage, rotation set A
  t6_aor5b: 5-stage, rotation set B (different schedule)
  t6_aor4a: 4-stage (test if 4 stages suffice with stronger per-stage mixing)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D)]

def rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def make_aor(nstages, rotations):
    """Create AND-OR fused candidate function.
    
    Args:
        nstages: number of stages
        rotations: list of tuples, each with 9 rotation amounts
                   (ra, rb, rc, rd, re, rf, rg, rh, ri)
    """
    def fn(val, key):
        x = np.uint64(val) ^ np.uint64(key)
        k = np.uint64(key)
        for i in range(nstages):
            rots = rotations[i]
            ra, rb, rc, rd, re, rf, rg, rh, ri = rots
            # Rotated copies
            vra = rotl64(x, ra)
            vrb = rotl64(x, rb)
            vrc = rotl64(x, rc)
            vrd = rotl64(x, rd)
            vre = rotl64(x, re)
            vrf = rotl64(x, rf)
            vrg = rotl64(x, rg)
            vrh = rotl64(x, rh)
            vri = rotl64(x, ri)
            # AND-OR fused: x = ((x&ra)|(rb&rc)) ^ ((rd&re)|(rf&rg)) ^ (rh&ri)
            # Note: vra is rotl(x, ra), but we need (x & ra) where ra is the rotated x
            # Actually: (x & ra) means x AND (rotated x by ra)
            t1 = (x & vra) | (vrb & vrc)
            t2 = (vrd & vre) | (vrf & vrg)
            t3 = (vrh & vri)
            x = t1 ^ t2 ^ t3 ^ rotl64(k, 13*(i+1)) ^ RC64[i % len(RC64)]
        return x ^ (k >> np.uint64(32))
    return fn

# Rotation sets: 9 rotations per stage (ra through ri)
ROTS_A_5 = [
    (3, 11, 23, 31, 43, 53, 7, 17, 29),
    (7, 17, 29, 37, 47, 59, 5, 13, 27),
    (5, 13, 27, 41, 49, 61, 9, 19, 33),
    (9, 19, 33, 39, 51, 57, 11, 23, 35),
    (11, 23, 35, 45, 55, 63, 3, 11, 23),
]

ROTS_B_5 = [
    (5, 13, 27, 41, 49, 61, 9, 19, 33),
    (11, 23, 35, 45, 55, 63, 3, 11, 23),
    (3, 11, 23, 31, 43, 53, 7, 17, 29),
    (9, 19, 33, 39, 51, 57, 11, 23, 35),
    (7, 17, 29, 37, 47, 59, 5, 13, 27),
]

ROTS_A_4 = ROTS_A_5[:4]

CANDIDATES_B7 = {
    "t6_aor5a": (make_aor(5, ROTS_A_5), "5-stage AND-OR fused, rotation set A"),
    "t6_aor5b": (make_aor(5, ROTS_B_5), "5-stage AND-OR fused, rotation set B"),
    "t6_aor4a": (make_aor(4, ROTS_A_4), "4-stage AND-OR fused, rotation set A"),
}

# Vectorized versions for triage
def _vec(fn):
    def vfn(vals, keys):
        return np.array([fn(int(v), int(k)) for v, k in zip(vals, keys)], dtype=np.uint64)
    return vfn

MIX_NP_B7 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B7.items()}
