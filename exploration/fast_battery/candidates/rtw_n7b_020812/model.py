"""Python model wrapper for rtw_n7b_020812 (fast_battery candidate interface)."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round_tweak/models")
from rtweak import feistel_tw_np
SPEC = {'rkmult': 13, 'rounds': [{'nl': ('s1',), 'lin': (2, 8, 12)}, {'nl': ('chi', 1, 3), 'lin': (2, 8, 12)}, {'nl': ('s1',), 'lin': (2, 8, 12)}, {'nl': ('chi', 1, 3), 'lin': (2, 8, 12)}, {'nl': ('s1',), 'lin': (2, 8, 12)}, {'nl': ('chi', 1, 3), 'lin': (2, 8, 12)}]}

def mix(v, k):
    return int(feistel_tw_np(np.uint64(v), np.uint64(k), SPEC))

def mix_np(V, K):
    return feistel_tw_np(V, K, SPEC)
