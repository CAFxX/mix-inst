"""Python model wrapper for r22c_spn_mix6r_lp_nw (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round22/models")
from r22 import r22c_spn_mix6r_lp_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
