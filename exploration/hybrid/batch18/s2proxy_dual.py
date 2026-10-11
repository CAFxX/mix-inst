"""Extended S2-proxy with 'dual' stage: x ^= (ra&rb)^(rc&rd)^re.
Tests the hypothesis: dual-AND last stage (stricter quiet condition:
BOTH pairs missed) breaks the 5-stage wall even with U=0.50 AND prefix.
"""
import numpy as np, sys
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy import rotl, max_abs_z_for_delta, M64

def apply_stage(x, st):
    if st[0] == 'and':
        _, a, b, c = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64
    elif st[0] == 't3':
        _, a, b, c, e = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,e)) & M64
    elif st[0] == 'dual':
        _, a, b, c, d, e = st
        return (x ^ (rotl(x,a) & rotl(x,b)) ^ (rotl(x,c) & rotl(x,d)) ^ rotl(x,e)) & M64
    raise ValueError(st)

def mix_stages(x, stages):
    for st in stages:
        x = apply_stage(x, st)
    return x

def s2proxy_dual(stages, deltas=None, n=1<<18, verbose=False):
    # monkey-patch mix_stages used by max_abs_z_for_delta via local copy
    if deltas is None:
        deltas = [1<<i for i in (0, 7, 13, 29, 46, 63)] + [0xFF, 1<<0 | 1<<32]
    worst_z, worst_d, worst_b = 0, None, None
    import s2proxy as S
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
    # and=3.35u, t3=4.5u, dual~5.0u (t6_dual4a 19.9/4)
    return sum({'and':3.35,'t3':4.5,'dual':5.0}[s[0]] for s in stages)

if __name__ == '__main__':
    # sanity: and5xa should still FAIL
    AND5XA = [('and',1,4,13),('and',5,16,7),('and',7,22,19),('and',11,37,5),('and',13,43,23)]
    z,d,b = s2proxy_dual(AND5XA)
    print(f"and5xa(FAIL ref): proxy max|z|={z:.1f}, est={cost_est(AND5XA):.2f}u")
    # test: [and,and,and,and,dual]
    T = [('and',1,2,13),('and',7,19,5),('and',3,11,29),('and',17,31,7),
         ('dual',11,23,37,47,5)]
    z,d,b = s2proxy_dual(T, verbose=True)
    print(f"[andx4,dual]: proxy max|z|={z:.1f} (d0={d:#x} bit{b}), est={cost_est(T):.2f}u")
