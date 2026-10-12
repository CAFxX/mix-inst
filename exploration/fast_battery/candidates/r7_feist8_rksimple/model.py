"""Python model wrapper for r7_feist8_rksimple (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round7/models")
from r7c import r7_feist8_rksimple as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
