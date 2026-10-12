"""Python model wrapper for r25_feist6_linfirst_nw (fast_battery candidate interface)."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round25/models")
from r25c import r25_feist6_linfirst_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
