"""Python model wrapper for r19_feist6_alt_notr_chioff13_fm03_nw (fast_battery candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round19/models")
from r19 import r19_feist6_alt_notr_chioff13_fm03_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
