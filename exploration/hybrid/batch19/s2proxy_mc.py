"""S2-proxy for maj/chi hybrids.

Stage types:
  ('maj', a, b, c): x ^= maj(x, rotl(x,a), rotl(x,b)) ^ rotl(x,c)
      -- fz22_maj5d form (S0 20.5u / 5 stages), proven maj lineage
  ('chi', a, b, c): x ^= ((~rotl(x,a)) & rotl(x,b)) ^ rotl(x,c)
      -- al_chi8 form (S0 26.1u / 8 stages), proven chi lineage
"""
import sys
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
import numpy as np
import s2proxy as S
from s2proxy import rotl, M64


def apply_stage(x, st):
    if st[0] == 'maj':
        _, a, b, c = st
        m = (x & rotl(x, a)) | (x & rotl(x, b)) | (rotl(x, a) & rotl(x, b))
        return (x ^ m ^ rotl(x, c)) & M64
    elif st[0] == 'chi':
        _, a, b, c = st
        return (x ^ ((~rotl(x, a)) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(st)


def mix_stages(x, stages):
    for st in stages:
        x = apply_stage(x, st)
    return x


def s2proxy_mc(stages, deltas=None, n=1 << 18, verbose=False):
    if deltas is None:
        deltas = ([1 << i for i in range(64)] + [0xFF, 1 << 0 | 1 << 32,
                   0xAAAAAAAAAAAAAAAA, 0x400, 0x4000000])
    worst_z, worst_d, worst_b = 0, None, None
    orig = S.mix_stages
    S.mix_stages = mix_stages
    try:
        for d0 in deltas:
            z, b = S.max_abs_z_for_delta(stages, d0, n)
            if verbose:
                print(f"    d0={d0:#018x}: max|z|={z:.1f} @bit{b}")
            if z > worst_z:
                worst_z, worst_d, worst_b = z, d0, b
    finally:
        S.mix_stages = orig
    return worst_z, worst_d, worst_b


def cost_est(stages):
    # empirical per-stage S0: maj=4.1u (fz22_maj5d 20.5/5), chi=3.26u (al_chi8 26.1/8)
    return sum(4.1 if s[0] == 'maj' else 3.26 for s in stages)


if __name__ == '__main__':
    import time
    AND5XA = [('and', 1, 4, 13), ('and', 5, 16, 7), ('and', 7, 22, 19),
              ('and', 11, 37, 5), ('and', 13, 43, 23)]
    # calibration references (and ref uses s2proxy's own apply_stage, emulate inline)
    MAJ5D = [('maj', 1, 7, 13), ('maj', 3, 11, 19), ('maj', 5, 15, 25),
             ('maj', 9, 21, 31), ('maj', 13, 27, 37)]
    CHI5 = [('chi', 1, 2, 13), ('chi', 7, 19, 5), ('chi', 3, 11, 29),
            ('chi', 13, 5, 17), ('chi', 17, 31, 7)]
    for name, st in [("maj5d(fz22 sched)", MAJ5D), ("chi5(al_chi8 sched)", CHI5)]:
        t0 = time.time()
        z, d, b = s2proxy_mc(st)
        print(f"{name}: proxy max|z|={z:.1f} (d0={d:#x} bit{b}), "
              f"est={cost_est(st):.2f}u, {time.time()-t0:.1f}s")
