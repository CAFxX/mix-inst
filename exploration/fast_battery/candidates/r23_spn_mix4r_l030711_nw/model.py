"""Python model wrapper for r23_spn_mix4r_l030711_nw (fast_battery candidate interface)."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round25/models")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round25")
import r25
_all = json.load(open("/home/hatch/workspace/mix/exploration/round25/specs25.json"))
_spec = next(s for s in _all if s["name"] == "r23_spn_mix4r_l030711_nw")
_spec["rots"] = tuple(_spec["rots"])
r24._install_specs([_spec])
from r24 import r23_spn_mix4r_l030711_nw as _np

def mix(v, k):
    return int(_np(np.uint64(v), np.uint64(k)))

mix_np = _np
