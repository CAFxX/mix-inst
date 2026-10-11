"""Fast numpy S2-proxy: differential z-score screen for 5-stage candidates.

For each input delta, simulate N random x, compute output differences,
z-score per output bit, report max|z|. Mirrors s2_diffprof.c (N=2^22, |z|>9 kill).

Stage types:
  ('and', a, b, c): x ^= (ra&rb) ^ rc
  ('t3', a, b, c, e): x ^= (ra&rb) ^ rc ^ re
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def apply_stage(x, st):
    if st[0] == 'and':
        _, a, b, c = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64
    elif st[0] == 't3':
        _, a, b, c, e = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,e)) & M64
    raise ValueError(st)

def mix_stages(x, stages):
    for st in stages:
        x = apply_stage(x, st)
    return x

def max_abs_z_for_delta(stages, d0, n=1<<18, seed=0):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    y0 = mix_stages(xs, stages)
    y1 = mix_stages(xs ^ np.uint64(d0), stages)
    d = (y0 ^ y1).astype(np.uint64)
    bitmat = ((d[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(np.float64)
    m = bitmat.mean(axis=0)
    z = (m - 0.5) / np.sqrt(0.25 / n)
    az = np.abs(z)
    return az.max(), int(np.argmax(az))

def s2proxy(stages, deltas=None, n=1<<18, verbose=False):
    if deltas is None:
        # MUST include all 64 single-bit deltas (real S2 does); sampling misses killers
        deltas = [1<<i for i in range(64)] + [0xFF, 1<<0 | 1<<32, 0xAAAAAAAAAAAAAAAA,
                  0x400, 0x4000000]
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in deltas:
        z, b = max_abs_z_for_delta(stages, d0, n)
        if verbose:
            print(f"    d0={d0:#018x}: max|z|={z:.1f} @bit{b}")
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def cost_est(stages):
    # empirical per-stage S0: and=3.35u, t3=4.5u
    return sum(3.35 if s[0]=='and' else 4.5 for s in stages)

# known schedules
AND5XA = [('and',1,4,13),('and',5,16,7),('and',7,22,19),('and',11,37,5),('and',13,43,23)]
AND6A5 = [('and',1,2,13),('and',7,19,5),('and',3,11,29),('and',17,31,7),('and',11,23,37)]
AND6A = AND6A5 + [('and',19,41,23)]
FZ15C = [('t3',1,7,13,29),('t3',3,11,19,37),('t3',5,15,25,41),('t3',9,21,31,49),('t3',13,27,37,55)]
# fz23_b approx: [t3,AND,t3,AND,AND] with fz15c rotations / danger-free AND rots
FZ23B = [('t3',1,7,13,29),('and',7,19,5),('t3',5,15,25,41),('and',17,31,7),('and',11,23,37)]

if __name__ == '__main__':
    for name, st in [("and5xa(FAIL)", AND5XA), ("and6a-first5(FAIL)", AND6A5),
                     ("and6a-6st(PASS)", AND6A), ("fz15c(PASS)", FZ15C),
                     ("fz23b(FAIL)", FZ23B)]:
        z, d, b = s2proxy(st, verbose=False)
        print(f"{name}: proxy max|z|={z:7.1f} (d0={d:#x} bit{b}), est_cost={cost_est(st):.2f}u",
              flush=True)
