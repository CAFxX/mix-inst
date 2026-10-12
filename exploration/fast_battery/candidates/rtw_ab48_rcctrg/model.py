"""Python model wrapper for rtw_ab48_rcctrg (fast_battery candidate interface)."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round_tweak/models")
from rtweak import feistel_tw_np
SPEC = {'rkmult': 13, 'rounds': [{'nl': ('s1',), 'lin': (4, 8), 'rc': 2654435769}, {'nl': ('chi', 1, 3), 'lin': (4, 8), 'rc': 1013904242}, {'nl': ('s1',), 'lin': (4, 8), 'rc': 3668340011}, {'nl': ('chi', 1, 3), 'lin': (4, 8), 'rc': 2027808484}, {'nl': ('s1',), 'lin': (4, 8), 'rc': 387276957}, {'nl': ('chi', 1, 3), 'lin': None, 'rc': 3041712726}]}

def mix(v, k):
    return int(feistel_tw_np(np.uint64(v), np.uint64(k), SPEC))

def mix_np(V, K):
    return feistel_tw_np(V, K, SPEC)
