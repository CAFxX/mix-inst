"""Python model wrapper for r7_feist8_spn_nw (fast_battery candidate interface).
8-round Feistel, F = 2-round SPN (S1 S-box, rotl7/rotl13 xor-linear), NO whitening
(L = val>>32, R = val&0xffffffff directly).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round6/models")
from r6 import _feist_F_spn_np, _rk_np

def _np(x, k):
    x = np.uint64(x); k = np.uint64(k)
    L = (x >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R = x & np.uint64(0xFFFFFFFF)
    # NO whitening with key
    for i in range(8):
        rk = _rk_np(k, i+1)
        F = _feist_F_spn_np(R, rk, "s1")
        L, R = R, L ^ F
    return ((R << np.uint64(32)) | L)

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
