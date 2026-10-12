"""Python model wrapper for r7_feist4_spn (fast_battery candidate interface).
4-round Feistel, F = 2-round SPN (S1 S-box, rotl7/rotl13 xor-linear), val^key whitening.
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round6/models")
from r6 import _feistel_np

def _np(x, k):
    return _feistel_np(np.uint64(x), np.uint64(k), 4, "s1")

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
