"""Python model wrapper for r7_ufeist16_48 (fast_battery candidate interface).
Exports scalar mix(v, k) and vectorized mix_np(V, K).
TEAM D, round 7. Scalar model: round7/models/r7d.py"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round7/models")
from r7d import r7_ufeist16_48_np as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
