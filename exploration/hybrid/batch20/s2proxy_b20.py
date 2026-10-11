"""S2-proxy for batch-20 fused maj+chi body hypotheses.

New construction (not a transplant): each stage fuses maj AND chi into ONE
nonlinear term. Delay play: maj+chi computed in PARALLEL (one nonlinear
depth), so 4 fused stages may beat the 20.1u frontier at ~18-19u.

Stage types:
  ('fm', a,b,c, d,e,f): x ^= maj(x,ra,rb)^rc ^ chi(x,rd,re)^rf   (fused parallel)
  ('dm', a,b,c, d,e,f): x ^= maj(x,ra,rb)^rc ^ maj(x,rd,re)^rf   (dual-maj control)
  ('rf', a,b,c, d,e,f): x  = maj(x,ra,rb) ^ chi(x,rd,re) ^ rl(x,rf)
                        (replacement-form fused; diagnostic vs track-8 rule
                         "replacement needs bijective N" -- maj^chi may not
                         have the deterministic 1-bit trail of pure maj)
"""
import sys
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/hybrid/batch19')
import numpy as np
import s2proxy as S
from s2proxy import rotl, M64


def maj3(x, a, b):
    return (x & rotl(x, a)) | (x & rotl(x, b)) | (rotl(x, a) & rotl(x, b))


def chi1(x, d, e):
    return (~rotl(x, d)) & rotl(x, e)


def apply_stage(x, st):
    if st[0] == 'fm':
        _, a, b, c, d, e, f = st
        return (x ^ maj3(x, a, b) ^ rotl(x, c)
                  ^ chi1(x, d, e) ^ rotl(x, f)) & M64
    if st[0] == 'dm':
        _, a, b, c, d, e, f = st
        return (x ^ maj3(x, a, b) ^ rotl(x, c)
                  ^ maj3(x, d, e) ^ rotl(x, f)) & M64
    if st[0] == 'rf':
        _, a, b, c, d, e, f = st
        return (maj3(x, a, b) ^ chi1(x, d, e) ^ rotl(x, f)) & M64
    raise ValueError(st)


def mix_stages(x, stages):
    for st in stages:
        x = apply_stage(x, st)
    return x


def s2proxy_b20(stages, deltas=None, n=1 << 18):
    if deltas is None:
        deltas = ([1 << i for i in range(64)] + [0xFF, 1 << 0 | 1 << 32,
                   0xAAAAAAAAAAAAAAAA, 0x400, 0x4000000])
    worst_z, worst_d, worst_b = 0, None, None
    orig = S.mix_stages
    S.mix_stages = mix_stages
    try:
        for d0 in deltas:
            z, b = S.max_abs_z_for_delta(stages, d0, n)
            if z > worst_z:
                worst_z, worst_d, worst_b = z, d0, b
    finally:
        S.mix_stages = orig
    return worst_z, worst_d, worst_b


def cost_est(stages):
    # fm/dm: maj(4.1u) and chi(3.26u) in parallel + wider XOR tree ~0.6u
    # rf: replacement form, single nonlinear depth ~4.7u
    return sum(4.7 for s in stages)
