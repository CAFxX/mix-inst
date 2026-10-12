"""Python model wrapper for r23_spn_mix4r_hs_aff_nw (fast_battery candidate interface)."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round23/models")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round23")
import r23
_all = json.load(open("/home/hatch/workspace/mix/exploration/round23/specs23.json"))
_spec = next(s for s in _all if s["name"] == "r23_spn_mix4r_hs_aff_nw")
_spec["rots"] = tuple(_spec["rots"])
r23._install_specs([_spec])
from r23 import r23_spn_mix4r_hs_aff_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
