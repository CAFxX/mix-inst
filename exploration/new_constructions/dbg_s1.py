import sys
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, N_DIFF_PAIRS
from t6_diffwall_verify2 import load_model
from screen_lib import KEYS, N

print("N_DIFF_PAIRS =", N_DIFF_PAIRS, " N =", N)
mod = load_model("as6_200_106")
key = int(KEYS[0])
print("key =", hex(key))

V = np.arange(N, dtype=np.uint64)
S = np.asarray(mod.mix_np(V, np.full(N, np.uint64(key), dtype=np.uint64)), dtype=np.uint64)
print("S[:4] =", [hex(int(x)) for x in S[:4]])
logps, wz, flp, blp = diff_cell_logps(S, key)
print("worst|z| =", wz, "fisher =", flp, "bonf =", blp)
print("per-delta logps:", ["%.1f" % lp for lp in logps])
