"""Python model wrapper for rtw_ab0612_pb2io (fast_battery candidate interface)."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round_tweak/models")
from rtweak import feistel_tw_np
SPEC = {'rkmult': 13, 'rounds': [{'nl': ('s1',), 'lin': (6, 12), 'pin': ('rev', None), 'pout': ('rev', None)}, {'nl': ('chi', 1, 3), 'lin': (6, 12), 'pin': ('rev', None), 'pout': ('rev', None)}, {'nl': ('s1',), 'lin': (6, 12), 'pin': ('rev', None), 'pout': ('rev', None)}, {'nl': ('chi', 1, 3), 'lin': (6, 12), 'pin': ('rev', None), 'pout': ('rev', None)}, {'nl': ('s1',), 'lin': (6, 12), 'pin': ('rev', None), 'pout': ('rev', None)}, {'nl': ('chi', 1, 3), 'lin': None, 'pin': ('rev', None), 'pout': ('rev', None)}]}

def mix(v, k):
    return int(feistel_tw_np(np.uint64(v), np.uint64(k), SPEC))

def mix_np(V, K):
    return feistel_tw_np(V, K, SPEC)
