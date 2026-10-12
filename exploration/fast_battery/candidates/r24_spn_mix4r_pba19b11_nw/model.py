"""Python model wrapper for r24_spn_mix4r_pba19b11_nw (fast_battery candidate interface)."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round24/models")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round24")
import r24
_all = json.load(open("/home/hatch/workspace/mix/exploration/round24/specs24.json"))
_spec = next(s for s in _all if s["name"] == "r24_spn_mix4r_pba19b11_nw")
_spec["rots"] = tuple(_spec["rots"])
r24._install_specs([_spec])
from r24 import r24_spn_mix4r_pba19b11_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
