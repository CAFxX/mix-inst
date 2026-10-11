"""S2-proxy v2: replicates diffprof methodology EXACTLY.
- Sequential x in [0, 2^logN), dedupe via x <= x^dl
- Per-bit z-scores, max|z| across bits
- Tests all 64 single-bit + structured + nibble deltas (115 total like diffprof)

Stage types: ('and',a,b,c), ('t3',a,b,c,e), applied via mix_stages.
For full-bundle testing, use model.py directly (see test_model_proxy).
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
    """mix_fn: (xs_array, key_array) -> ys_array. Returns max|z|."""
    N = 1 << logN
    xs = np.arange(N, dtype=np.uint64)
    xs = xs[xs <= (xs ^ np.uint64(d0))]
    npairs = len(xs)
    K = np.full(npairs, np.uint64(0x123456789ABCDEF0))
    y0 = mix_fn(xs, K)
    y1 = mix_fn(xs ^ np.uint64(d0), K)
    d = (y0 ^ y1).astype(np.uint64)
    bitmat = ((d[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(np.float64)
    mm = bitmat.mean(axis=0)
    z = (mm - 0.5) / np.sqrt(0.25 / npairs)
    az = np.abs(z)
    return az.max(), int(np.argmax(az)), npairs

def s2proxy_v2(stages, logN=20, verbose=False):
    def mix_fn(xs, K):
        # stages operate on x^k pre-whitened; emulate key like bundles do
        x = (xs ^ K) & M64
        x = mix_stages(x, stages)
        # post: x ^= rotl(k,13) — linear, doesn't affect |z|
        return x
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if verbose and z > 9:
            print(f"    d0={d0:#018x}: max|z|={z:.1f} @bit{b}")
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def cost_est(stages):
    return sum(3.35 if s[0]=='and' else 4.5 for s in stages)

# reference schedules
AND5XA = [('and',1,4,13),('and',5,16,7),('and',7,22,19),('and',11,37,5),('and',13,43,23)]
AND6A5 = [('and',1,2,13),('and',7,19,5),('and',3,11,29),('and',17,31,7),('and',11,23,37)]
AND6A = AND6A5 + [('and',19,41,23)]
FZ15C = [('t3',1,7,13,29),('t3',3,11,19,37),('t3',5,15,25,41),('t3',9,21,31,49),('t3',13,27,37,55)]

if __name__ == '__main__':
    for name, st in [("and5xa(FAIL)", AND5XA), ("and6a-first5(FAIL)", AND6A5),
                     ("and6a-6st(PASS)", AND6A), ("fz15c(PASS)", FZ15C)]:
        z, d, b = s2proxy_v2(st, logN=20)
        print(f"{name}: v2 proxy max|z|={z:7.1f} (d0={d:#x} bit{b}), est={cost_est(st):.2f}u",
              flush=True)
