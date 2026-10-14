"""Adversarial follow-up: worst keys for the 8-round weakness, N=2^18.
SPN-8 included as positive control (must flag); SPN-10 must be clean."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tests_final import seq_battery, splitmix_np, murmur_np
from spn import mix_spn_np

CANDS = [
    ("splitmix64", splitmix_np),
    ("murmur3-fmix", murmur_np),
    ("SPN-8", lambda V, K: mix_spn_np(V, K, rounds=8)),
    ("SPN-10", lambda V, K: mix_spn_np(V, K, rounds=10)),
]

# keys that maximized the 8-round lemire-X=10 deviation, plus extra strides
CONFIGS = [
    ("seq-key0",     0x0000000000000000, 0, 1, 1 << 18),
    ("seq-key9e37",  0x9E3779B97F4A7C15, 0, 1, 1 << 18),
    ("seq-keyAAAA",  0xAAAAAAAAAAAAAAAA, 0, 1, 1 << 18),
    ("seq-keyFFFF",  0xFFFFFFFFFFFFFFFF, 0, 1, 1 << 18),
    ("seq-key5555",  0x5555555555555555, 0, 1, 1 << 18),
    ("stride-3",     0x0000000000001234, 0, 3, 1 << 18),
    ("stride-big2",  0x0FEDCBA987654321, 999, 0xFFFFFFFFFFFFFFC5, 1 << 18),
]

t0 = time.time()
nflag = 0
for name, fn in CANDS:
    print(f"--- {name} ---", flush=True)
    for cname, key, I, j, N in CONFIGS:
        res = seq_battery(fn, key, I, j, N, cname)
        flags = [(t, z) for t, z in res if abs(z) > 4]
        nflag += len(flags)
        worst = max(res, key=lambda tz: abs(tz[1]))
        print(f"    {cname:14s} {len(res)} tests, worst: {worst[0]} z={worst[1]:+.2f}" +
              (f"  FLAGS: {[(t, round(z,2)) for t,z in flags]}" if flags else ""), flush=True)
print(f"total flags: {nflag}  ({time.time()-t0:.0f}s)")
