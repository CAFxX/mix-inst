"""Bit-exact Python model for t6_het6c (batch 6 heterogeneous)."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
import numpy as np
from t6_models_b6 import CANDIDATES_B6, MIX_NP_B6

_scalar_fn = CANDIDATES_B6["t6_het6c"][0]
_desc = CANDIDATES_B6["t6_het6c"][1]

def mix(v, k):
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _scalar_fn(int(v), int(k))
    return MIX_NP_B6["t6_het6c"](v, k)

def mix_np(V, K):
    return MIX_NP_B6["t6_het6c"](V, K)

meta = {"desc": _desc}
