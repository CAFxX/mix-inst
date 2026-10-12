"""Python model wrapper for ga_g12_111 (GA candidate interface).
Exports scalar `mix(v, k)` and vectorized `mix_np(V, K)`."""
import sys, os, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/ga")
from gamodels import decode_np
_gpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genome.json")
_genome = json.load(open(_gpath))
_np_fn = decode_np(_genome)

def mix(v, k):
    return int(_np_fn(np.uint64(v), np.uint64(k)))

mix_np = _np_fn
