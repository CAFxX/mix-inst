"""Python model wrapper for r11_feist6_sk4311_nw (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round11/models")
from r11 import r11_feist6_sk4311_nw as _np


def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
